#!/usr/bin/env python3
"""DCC-XVIII: Coherent checkpoint generations + cross-file recovery.

Success definition under test: every file participating in one committed
logical checkpoint belongs to the same certified generation. A crash before
generation commit leaves the previous committed generation authoritative; a
crash after commit exposes the new complete generation. Loading never
constructs a hybrid from independently valid but generation-mismatched files.

Controls:
  A  normal G1/G2 commit; fresh process loads exactly coherent G2; member
     generation/fingerprint evidence agrees
  B  crash before first member -> no committed generation (legacy signal)
  C  crash after one member -> G1 authoritative; partial member inert
  D  crash after all members, before commit -> G1 authoritative
  E  crash after commit -> coherent G2
  F  committed member missing -> recover certified previous (or explicit fail)
  G  committed member corrupt -> fingerprint catches; recover previous
  H  member swap across generations -> fingerprint/identity rejects
  I  manifest corrupt -> recover via pointer's previous link; corrupt pointer
     -> explicit failure; absent pointer -> legacy signal
  J  stale uncommitted generation cannot win over committed G1
  K  multiple stale generations -> G1 deterministically (no timestamp guess)
  L  load atomicity: failed load leaves live state semantically unchanged
  M  supersession integration: one coherent revision generation
  N  lineage + dependency integration: coherent chain across load
  O  contextual routing reproduces across checkpoint load
  P  owner isolation: A's failure never affects B's committed generation
  Q  cross-owner member swap never satisfies another owner's manifest
  R  repeated checkpoints G1->G4; latest committed always loads
  S  retention: current + previous kept; cleanup cannot delete current
  T  recovery policy: both generations invalid -> explicit failure
  U  failure atomicity at every pre-commit stage -> prior generation wins
  V  literal OS-process matrix (distinct PIDs, no inherited-memory canary)
  W  DCC-XVII preservation: V2 writes only; temp-crash leaves no confusion

AUTONOMY = NO.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from form.open import open_program
from form import persist_rest
from form.persist import _STATE_DIR, _safe_owner


def _safe_owner_collides(ox: str, oy: str) -> bool:
    """True when two distinct raw owners normalize to the same safe name."""
    return ox != oy and _safe_owner(ox) == _safe_owner(oy)
from form.dell_matrix import atomic_write as AW
from form.dell_matrix.atomic_write import AtomicWriteError, atomic_write_bytes
from form.dell_matrix.nursery import Nursery, owner_nursery_path
from form.mandell import checkpoint_generation as CG
from form.mandell.checkpoint_generation import (
    CHECKPOINT_PROTOCOL_VERSION,
    CheckpointCommitError,
    CheckpointError,
    CheckpointLoadError,
    CheckpointNotEstablished,
)
from form.mandell import supersession as S
from form.mandell.knowledge_selector import select_for_context
from form.mandell.conflict_router import detect_conflicts, route_conflicts
from form.mandell.dependency_validity import inspect_dependency

STATE = Path(_STATE_DIR)
OWNERS: list[str] = []
CHECKS: list[tuple[str, bool]] = []


def check(name: str, cond: bool) -> None:
    CHECKS.append((name, bool(cond)))


def wipe_owner(owner: str) -> None:
    patterns = {f"*{owner}*"}
    safe = _safe_owner(owner)
    if safe != owner:
        patterns.add(f"*{safe}*")
    for pat in patterns:
        try:
            matches = list(STATE.glob(pat))
        except (OSError, ValueError):
            continue
        for f in matches:
            try:
                if f.is_file():
                    f.unlink()
            except OSError:
                pass


def fresh_owner(owner: str):
    wipe_owner(owner)
    if owner not in OWNERS:
        OWNERS.append(owner)
    return open_program(owner)


def sha_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def add_confirmed(p, label: str, words: str) -> str:
    pr = p.nursery.add(label, words=words)
    p.confirm_proposal(pr.id)
    return pr.id


def state_digest(p) -> dict:
    return {
        "nursery_ids": sorted(p.nursery.proposals.keys()),
        "plane_ids": sorted(p.cube.session.plane.units.keys()),
    }


# ---------------------------------------------------------------- CONTROL A
def control_a_normal_g1_g2() -> None:
    o = "DCCXVIII_A"
    p = fresh_owner(o)
    a = add_confirmed(p, "alpha base", "alpha beta gamma delta")
    r1 = CG.commit_checkpoint(p, generation_id="ga00000000000001")
    b = add_confirmed(p, "beta growth", "alpha beta gamma epsilon")
    r2 = CG.commit_checkpoint(p, generation_id="ga00000000000002")
    check("A.receipt_protocol", r1["checkpoint_protocol_version"] == 1 == r2["checkpoint_protocol_version"])
    check("A.receipt_committed", r1["committed"] is True and r2["committed"] is True)
    check("A.ids_distinct", r1["generation_id"] != r2["generation_id"])
    check("A.prev_link", r2["previous_generation_id"] == r1["generation_id"] and r1["previous_generation_id"] is None)
    q, lr = CG.load_checkpoint(o, activate=False)
    check("A.fresh_loads_g2", lr["generation_id"] == "ga00000000000002" and lr["recovered_from"] is None)
    check("A.legacy_false", lr["legacy"] is False)
    # Member generation/fingerprint evidence agrees: receipt == manifest == bytes.
    manifest = json.loads((Path(CG._manifest_path(o, "ga00000000000002"))).read_text())
    agree = True
    for kind in ("nursery", "program"):
        spec = manifest["members"][kind]
        agree = agree and spec == lr["members"][kind] == r2["members"][kind]
        agree = agree and sha_of(STATE / spec["file"]) == spec["sha256"]
    check("A.member_evidence_agrees", agree)
    d_before, d_after = state_digest(p), state_digest(q)
    check("A.state_coherent", d_before == d_after and a in d_after["nursery_ids"] and b in d_after["plane_ids"])


# ---------------------------------------------------------------- CONTROL B
def control_b_no_checkpoint() -> None:
    o = "DCCXVIII_B"
    fresh_owner(o)
    try:
        CG.load_checkpoint(o, activate=False)
        check("B.legacy_signal", False)
    except CheckpointNotEstablished:
        check("B.legacy_signal", True)
    except CheckpointError:
        check("B.legacy_signal", False)


# ---------------------------------------------------------------- CONTROL F
def control_f_member_missing() -> None:
    o = "DCCXVIII_F"
    p = fresh_owner(o)
    a = add_confirmed(p, "f base", "foxtrot base words")
    CG.commit_checkpoint(p, generation_id="gf00000000000001")
    b = add_confirmed(p, "f next", "foxtrot next words")
    CG.commit_checkpoint(p, generation_id="gf00000000000002")
    # Delete the committed G2 program member: loader must not mix G2 nursery with G1 program.
    (Path(CG._member_path(o, "program", "gf00000000000002"))).unlink()
    q, lr = CG.load_checkpoint(o, activate=False)
    check("F.recovers_previous", lr["recovered_from"] == "gf00000000000002"
          and lr["generation_id"] == "gf00000000000001")
    d = state_digest(q)
    check("F.recovered_state_is_g1", a in d["nursery_ids"] and b not in d["nursery_ids"])
    # No previous generation at all -> explicit honest failure, never a hybrid.
    o2 = "DCCXVIII_F2"
    p2 = fresh_owner(o2)
    add_confirmed(p2, "f2 base", "foxtrot two base")
    CG.commit_checkpoint(p2, generation_id="gf2000000000001")
    (Path(CG._member_path(o2, "program", "gf2000000000001"))).unlink()
    try:
        CG.load_checkpoint(o2, activate=False)
        check("F.explicit_when_no_previous", False)
    except CheckpointLoadError:
        check("F.explicit_when_no_previous", True)


# ---------------------------------------------------------------- CONTROL G
def control_g_member_corrupt() -> None:
    o = "DCCXVIII_G"
    p = fresh_owner(o)
    a = add_confirmed(p, "g base", "golf base words here")
    CG.commit_checkpoint(p, generation_id="gg00000000000001")
    b = add_confirmed(p, "g next", "golf next words here")
    CG.commit_checkpoint(p, generation_id="gg00000000000002")
    mp = Path(CG._member_path(o, "nursery", "gg00000000000002"))
    blob = mp.read_bytes()
    mp.write_bytes(blob[: len(blob) // 3])  # truncated member
    q, lr = CG.load_checkpoint(o, activate=False)
    check("G.fingerprint_catches", lr["recovered_from"] == "gg00000000000002"
          and lr["generation_id"] == "gg00000000000001")
    check("G.no_mixed_state", b not in state_digest(q)["nursery_ids"]
          and a in state_digest(q)["nursery_ids"])


# ---------------------------------------------------------------- CONTROL H
def control_h_member_swap() -> None:
    o = "DCCXVIII_H"
    p = fresh_owner(o)
    a = add_confirmed(p, "h base", "hotel base words here")
    CG.commit_checkpoint(p, generation_id="gh00000000000001")
    b = add_confirmed(p, "h next", "hotel next words here")
    CG.commit_checkpoint(p, generation_id="gh00000000000002")
    # Place the valid G1 nursery member where the G2 member is expected.
    g1 = (Path(CG._member_path(o, "nursery", "gh00000000000001"))).read_bytes()
    (Path(CG._member_path(o, "nursery", "gh00000000000002"))).write_bytes(g1)
    q, lr = CG.load_checkpoint(o, activate=False)
    check("H.swap_rejected", lr["generation_id"] == "gh00000000000001"
          and lr["recovered_from"] == "gh00000000000002")
    check("H.no_g2_leak", b not in state_digest(q)["nursery_ids"])


# ---------------------------------------------------------------- CONTROL I
def control_i_manifest_and_pointer() -> None:
    o = "DCCXVIII_I"
    p = fresh_owner(o)
    add_confirmed(p, "i base", "india base words here")
    CG.commit_checkpoint(p, generation_id="gi00000000000001")
    add_confirmed(p, "i next", "india next words here")
    CG.commit_checkpoint(p, generation_id="gi00000000000002")
    # Corrupt the committed G2 manifest: recovery follows the pointer's
    # previous_generation_id link deterministically.
    (Path(CG._manifest_path(o, "gi00000000000002"))).write_bytes(b"{corrupt!!")
    q, lr = CG.load_checkpoint(o, activate=False)
    check("I.recovers_previous", lr["generation_id"] == "gi00000000000001"
          and lr["recovered_from"] == "gi00000000000002")
    # Corrupt the pointer itself: nothing is knowable -> explicit failure, never guess.
    (Path(CG._pointer_path(o))).write_bytes(b"nope")
    try:
        CG.load_checkpoint(o, activate=False)
        check("I.pointer_corrupt_explicit", False)
    except CheckpointLoadError:
        check("I.pointer_corrupt_explicit", True)
    # Absent pointer -> legacy signal, not an error.
    (Path(CG._pointer_path(o))).unlink()
    try:
        CG.load_checkpoint(o, activate=False)
        check("I.absent_pointer_legacy", False)
    except CheckpointNotEstablished:
        check("I.absent_pointer_legacy", True)

# ---------------------------------------------------------------- CONTROL J
def control_j_stale_uncommitted() -> None:
    o = "DCCXVIII_J"
    p = fresh_owner(o)
    a = add_confirmed(p, "j base", "juliett base words")
    CG.commit_checkpoint(p, generation_id="gj00000000000001")
    b = add_confirmed(p, "j next", "juliett next words")
    # Seal G2 members + manifest but never commit the pointer.
    CG._seal_members(p, "gj00000000000002")
    q, lr = CG.load_checkpoint(o, activate=False)
    check("J.stale_cannot_win", lr["generation_id"] == "gj00000000000001"
          and lr["recovered_from"] is None)
    check("J.g1_state", a in state_digest(q)["nursery_ids"] and b not in state_digest(q)["nursery_ids"])


# ---------------------------------------------------------------- CONTROL K
def control_k_multiple_stale() -> None:
    o = "DCCXVIII_K"
    p = fresh_owner(o)
    a = add_confirmed(p, "k base", "kilo base words")
    CG.commit_checkpoint(p, generation_id="gk00000000000001")
    for i, gid in enumerate(("gk00000000000002", "gk00000000000003", "gk00000000000004")):
        add_confirmed(p, f"k s{i}", f"kilo stale {i} words")
        CG._seal_members(p, gid)
    q, lr = CG.load_checkpoint(o, activate=False)
    check("K.deterministic_g1", lr["generation_id"] == "gk00000000000001")
    check("K.no_timestamp_guess", a in state_digest(q)["nursery_ids"])


# ---------------------------------------------------------------- CONTROL L
def control_l_load_atomicity() -> None:
    o = "DCCXVIII_L"
    p = fresh_owner(o)
    a = add_confirmed(p, "l base", "lima base words")
    CG.commit_checkpoint(p, generation_id="gl00000000000001")
    # Bind live state L, then break the committed generation.
    live = persist_rest.load(o, activate=True)
    before = state_digest(live)
    (Path(CG._member_path(o, "program", "gl00000000000001"))).unlink()
    (Path(CG._member_path(o, "nursery", "gl00000000000001"))).unlink()
    try:
        CG.load_checkpoint(o, activate=False)
        check("L.failed_load_raises", False)
    except CheckpointLoadError:
        check("L.failed_load_raises", True)
    from form.mandell.language import bound_program
    bound = bound_program()
    after = state_digest(bound) if bound is not None else None
    check("L.live_unchanged", after == before and a in (after or {}).get("nursery_ids", []))


# ---------------------------------------------------------------- CONTROL M
def control_m_supersession() -> None:
    o = "DCCXVIII_M"
    p = fresh_owner(o)
    a = add_confirmed(p, "m base", "mike base words here")
    res = S.supersede_proposal(p, a, "mike revision two words")
    assert res["ok"]
    b = res["new_id"]
    CG.commit_checkpoint(p, generation_id="gm00000000000001")
    q, lr = CG.load_checkpoint(o, activate=False)
    old, new = S.inspect_revision(q, a), S.inspect_revision(q, b)
    check("M.coherent_revision",
          old["lifecycle_state"] == "superseded" and new["lifecycle_state"] == "active"
          and old["superseded_by_id"] == b and new["supersedes_id"] == a
          and b in q.cube.session.plane.units)
    check("M.no_old_active_new_links", not (old["lifecycle_state"] == "active" and new["supersedes_id"] == a))
    check("M.no_old_superseded_missing_succ", not (old["lifecycle_state"] == "superseded" and b not in q.nursery.proposals))


# ---------------------------------------------------------------- CONTROL N
def control_n_lineage_dependency() -> None:
    o = "DCCXVIII_N"
    p = fresh_owner(o)
    from form.mandell.knowledge_lineage import lineage_record
    a = add_confirmed(p, "n root", "november root words")
    bp = p.nursery.add("n child", words="november child words", parents=[a])
    p.confirm_proposal(bp.id)
    b = bp.id
    cp = p.nursery.add("n grandchild", words="november grandchild words", parents=[b])
    p.confirm_proposal(cp.id)
    c = cp.id
    CG.commit_checkpoint(p, generation_id="gn00000000000001")
    q, lr = CG.load_checkpoint(o, activate=False)
    lb, lc = lineage_record(q, b), lineage_record(q, c)
    db, dc = inspect_dependency(q, b), inspect_dependency(q, c)
    check("N.parents_coherent", lb["parent_ids"] == [a] and lc["parent_ids"] == [b])
    check("N.roots_coherent", lb["root_ids"] == [a] and lc["root_ids"] == [a])
    check("N.depth_coherent", lb["depth"] == 2 and lc["depth"] == 3)
    check("N.dependency_valid", db["dependency_status"] == "valid" and dc["dependency_status"] == "valid")
    rev_b = S.inspect_revision(q, b)
    check("N.revision_active", rev_b["lifecycle_state"] == "active")


# ---------------------------------------------------------------- CONTROL O
def control_o_contextual_routing() -> None:
    o = "DCCXVIII_O"
    p = fresh_owner(o)
    # Fixture: active revision pair, dep chain, invalid dep, candidates, conflict pair.
    old = add_confirmed(p, "o base", "orchard harvest moon cider")
    res = S.supersede_proposal(p, old, "orchard harvest moon cider reserve")
    assert res["ok"]
    new = res["new_id"]
    va = add_confirmed(p, "o valid a", "orchard valid ancestor cider")
    vbp = p.nursery.add("o valid b", words="orchard valid descendant cider", parents=[va])
    p.confirm_proposal(vbp.id)
    vb = vbp.id
    # Invalid dependency via superseded ancestor (DCC-XVI contract):
    # descendants of a superseded ancestor are honestly dependency-invalid.
    vp = add_confirmed(p, "o parent", "orchard parent cider")
    vcp = p.nursery.add("o child", words="orchard child cider", parents=[vp])
    p.confirm_proposal(vcp.id)
    bad = vcp.id
    sres = S.supersede_proposal(p, vp, "orchard parent cider reserve")
    assert sres["ok"]
    c1 = add_confirmed(p, "o c1", "rain dances nourish crops")
    c2 = add_confirmed(p, "o c2", "rain dances do not nourish crops")
    persist_rest.save(p)
    before_sel = select_for_context(p, "orchard harvest moon cider")
    before_ids = [e.get("id") for e in before_sel.get("selected", [])]
    conflicts = detect_conflicts([
        {"id": c1, "text": "rain dances nourish crops"},
        {"id": c2, "text": "rain dances do not nourish crops"},
    ])
    before_routable, before_quarantined = route_conflicts(before_ids, conflicts)
    CG.commit_checkpoint(p, generation_id="go00000000000001")
    q, lr = CG.load_checkpoint(o, activate=False)
    after_sel = select_for_context(q, "orchard harvest moon cider")
    after_ids = [e.get("id") for e in after_sel.get("selected", [])]
    after_routable, after_quarantined = route_conflicts(after_ids, conflicts)
    check("O.routing_reproduced", after_ids == before_ids and after_routable == before_routable
          and after_quarantined == before_quarantined)
    check("O.revision_filtered", old not in after_ids and new in after_ids)
    check("O.dep_filtered", bad not in after_ids)
    check("O.top5_bounded", len(after_ids) <= 5)
    check("O.provenance", all("id" in e for e in after_sel.get("selected", [])))


# ---------------------------------------------------------------- CONTROL P
def control_p_owner_isolation() -> None:
    oa, ob = "DCCXVIII_PA", "DCCXVIII_PB"
    pa = fresh_owner(oa)
    add_confirmed(pa, "pa base", "papa alpha words")
    CG.commit_checkpoint(pa, generation_id="gpA0000000000001")
    pb = fresh_owner(ob)
    b = add_confirmed(pb, "pb base", "papa beta words")
    CG.commit_checkpoint(pb, generation_id="gpB0000000000001")
    # Break A's committed generation; B must be unaffected.
    (Path(CG._member_path(oa, "program", "gpA0000000000001"))).unlink()
    try:
        CG.load_checkpoint(oa, activate=False)
        a_failed = False
    except CheckpointLoadError:
        a_failed = True
    qb, lrb = CG.load_checkpoint(ob, activate=False)
    check("P.a_fails_honestly", a_failed)
    check("P.b_unaffected", lrb["generation_id"] == "gpB0000000000001"
          and b in state_digest(qb)["nursery_ids"])
    # Collision namespace: raw owners that normalize to the same safe name
    # must never share generation artifacts. (Their live canonical files do
    # collide -- pre-existing Persistence V2 behavior, out of scope here --
    # so the collision fixture is managed explicitly, not via wipe_owner.)
    ox, oy = "DCCXVIII/PX", "DCCXVIII_PX"
    assert _safe_owner_collides(ox, oy)
    for f in STATE.glob("*DCCXVIII_PX*"):
        try:
            if f.is_file():
                f.unlink()
        except OSError:
            pass
    OWNERS.extend([ox, oy])
    px = open_program(ox)
    x = add_confirmed(px, "px base", "xray one words")
    CG.commit_checkpoint(px, generation_id="gpx0000000000001")
    ox_files = {
        "pointer": Path(CG._pointer_path(ox)),
        "manifest": Path(CG._manifest_path(ox, "gpx0000000000001")),
        "nursery": Path(CG._member_path(ox, "nursery", "gpx0000000000001")),
        "program": Path(CG._member_path(ox, "program", "gpx0000000000001")),
    }
    ox_shas = {k: sha_of(p) for k, p in ox_files.items()}
    py = open_program(oy)
    y = add_confirmed(py, "py base", "yankee two words")
    CG.commit_checkpoint(py, generation_id="gpy0000000000001")
    nsx, nsy = CG._owner_ns(ox), CG._owner_ns(oy)
    oy_member = Path(CG._member_path(oy, "nursery", "gpy0000000000001"))
    qx, lrx = CG.load_checkpoint(ox, activate=False)
    qy, lry = CG.load_checkpoint(oy, activate=False)
    check("P.collision_namespaces_disjoint",
          nsx != nsy
          and ox_files["nursery"] != oy_member
          and oy_member.is_file())
    check("P.collision_no_overwrite",
          all(p.is_file() and sha_of(p) == ox_shas[k] for k, p in ox_files.items()))
    check("P.collision_each_loads_own",
          x in state_digest(qx)["nursery_ids"] and y not in state_digest(qx)["nursery_ids"]
          and y in state_digest(qy)["nursery_ids"]
          and lrx["generation_id"] == "gpx0000000000001"
          and lry["generation_id"] == "gpy0000000000001")


# ---------------------------------------------------------------- CONTROL Q
def control_q_cross_owner_swap() -> None:
    oa, ob = "DCCXVIII_QA", "DCCXVIII_QB"
    pa = fresh_owner(oa)
    a = add_confirmed(pa, "qa base", "quebec alpha words")
    CG.commit_checkpoint(pa, generation_id="gqA0000000000001")
    pb = fresh_owner(ob)
    b = add_confirmed(pb, "qb base", "quebec beta words")
    CG.commit_checkpoint(pb, generation_id="gqB0000000000001")
    CG.commit_checkpoint(pb, generation_id="gqB0000000000002")
    # Plant A's valid nursery member where B's current member is expected.
    a_bytes = (Path(CG._member_path(oa, "nursery", "gqA0000000000001"))).read_bytes()
    (Path(CG._member_path(ob, "nursery", "gqB0000000000002"))).write_bytes(a_bytes)
    qb, lrb = CG.load_checkpoint(ob, activate=False)
    check("Q.never_satisfies", a not in state_digest(qb)["nursery_ids"])
    check("Q.b_recovers_or_fails_honestly",
          lrb["generation_id"] in ("gqB0000000000001", "gqB0000000000002")
          and b in state_digest(qb)["nursery_ids"])


# ---------------------------------------------------------------- CONTROL R
def control_r_repeated() -> None:
    o = "DCCXVIII_R"
    p = fresh_owner(o)
    ids = []
    for i in range(1, 5):
        ids.append(add_confirmed(p, f"r{i}", f"romeo generation {i} words"))
        CG.commit_checkpoint(p, generation_id=f"gr0000000000000{i}")
        q, lr = CG.load_checkpoint(o, activate=False)
        if lr["generation_id"] != f"gr0000000000000{i}":
            check("R.latest_loads", False)
            return
    check("R.latest_loads", True)
    q, lr = CG.load_checkpoint(o, activate=False)
    d = state_digest(q)
    check("R.no_stale_resurrection", all(i in d["nursery_ids"] for i in ids)
          and lr["recovered_from"] is None)


# ---------------------------------------------------------------- CONTROL S
def control_s_retention() -> None:
    o = "DCCXVIII_S"
    p = fresh_owner(o)
    gids = []
    for i in range(1, 5):
        add_confirmed(p, f"s{i}", f"sierra generation {i} words")
        gid = f"gs0000000000000{i}"
        CG.commit_checkpoint(p, generation_id=gid)
        gids.append(gid)
    remaining = {f.name for f in STATE.glob(f"*{o}*")}
    g1_files = [n for n in remaining if "gs00000000000001" in n or "gs00000000000002" in n]
    g34_files = [n for n in remaining if "gs00000000000003" in n or "gs00000000000004" in n]
    check("S.old_generations_swept", g1_files == [] and len(g34_files) == 6)
    check("S.current_pointer", json.loads((Path(CG._pointer_path(o))).read_text())["generation_id"]
          == "gs00000000000004")
    # Cleanup provably cannot delete the current generation.
    rep = CG._retain_current_and_previous(o)
    check("S.cannot_delete_current",
          "gs00000000000004" in rep["kept"]
          and (Path(CG._manifest_path(o, "gs00000000000004"))).is_file()
          and (Path(CG._member_path(o, "nursery", "gs00000000000004"))).is_file())
    q, lr = CG.load_checkpoint(o, activate=False)
    check("S.current_loads", lr["generation_id"] == "gs00000000000004")


# ---------------------------------------------------------------- CONTROL T
def control_t_both_invalid() -> None:
    o = "DCCXVIII_T"
    p = fresh_owner(o)
    add_confirmed(p, "t base", "tango base words")
    CG.commit_checkpoint(p, generation_id="gt00000000000001")
    add_confirmed(p, "t next", "tango next words")
    CG.commit_checkpoint(p, generation_id="gt00000000000002")
    # Break BOTH generations: explicit failure naming both, never a guess.
    (Path(CG._member_path(o, "program", "gt00000000000002"))).unlink()
    (Path(CG._member_path(o, "program", "gt00000000000001"))).unlink()
    try:
        CG.load_checkpoint(o, activate=False)
        check("T.explicit_when_both_invalid", False)
    except CheckpointLoadError as exc:
        check("T.explicit_when_both_invalid", "gt00000000000002" in str(exc)
              and "gt00000000000001" in str(exc))


# ---------------------------------------------------------------- CONTROL U
def control_u_failure_atomicity() -> None:
    stages = ["save_nursery", "save_program", "before_members", "member_nursery",
              "member_program", "manifest", "after_members", "pointer", "after_commit"]
    for stage in stages:
        o = f"DCCXVIII_U_{stage}"
        p = fresh_owner(o)
        add_confirmed(p, "u base", "uniform base words")
        CG.commit_checkpoint(p, generation_id="gu10000000000001")
        add_confirmed(p, "u next", "uniform next words")
        try:
            CG.commit_checkpoint(p, generation_id="gu20000000000001", _fail_at=stage)
            check(f"U.{stage}_raises", False)
            continue
        except CheckpointCommitError:
            check(f"U.{stage}_raises", True)
        q, lr = CG.load_checkpoint(o, activate=False)
        # after_commit fails AFTER the pointer swap: the new generation is
        # the honest winner; every other stage leaves the prior generation.
        if stage == "after_commit":
            check(f"U.{stage}_new_wins", lr["generation_id"] == "gu20000000000001"
                  and lr["recovered_from"] is None)
        else:
            check(f"U.{stage}_prior_wins", lr["generation_id"] == "gu10000000000001"
                  and lr["recovered_from"] is None)

# ---------------------------------------------------------------- CONTROL V
_CHILD_COMMIT = r'''
import sys, os, json
sys.path.insert(0, __REPO__)
owner, mode, crash_at, sidecar = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
from form.open import open_program
from form.mandell import checkpoint_generation as CG

def _add2(p, label, words):
    pr = p.nursery.add(label, words=words)
    p.confirm_proposal(pr.id)
    return pr.id

p = open_program(owner)
_add2(p, "v base one", "victor base one words")
CG.commit_checkpoint(p, generation_id="gv00000000000001")
CG._V_CANARY = "canary-%d" % os.getpid()  # inherited-memory canary: must not cross processes
with open(sidecar, "w") as f:
    json.dump({"pid": os.getpid()}, f)
    f.flush()
    os.fsync(f.fileno())
if mode == "commit2":
    _add2(p, "v base two", "victor base two words")
    fail = None if crash_at == "none" else "crash_" + crash_at
    CG.commit_checkpoint(p, generation_id="gv00000000000002", _fail_at=fail)
elif mode == "commit4":
    for i in (2, 3, 4):
        _add2(p, f"v base {i}", f"victor base {i} words")
        CG.commit_checkpoint(p, generation_id="gv0000000000000%d" % i)
elif mode == "seal_only":
    _add2(p, "v base two", "victor base two words")
    CG._seal_members(p, "gv00000000000002")
'''

_CHILD_LOAD = r'''
import sys, os, json
sys.path.insert(0, __REPO__)
owner, sidecar = sys.argv[1], sys.argv[2]
from form.mandell import checkpoint_generation as CG
from form.mandell.checkpoint_generation import CheckpointNotEstablished, CheckpointLoadError
out = {"pid": os.getpid(), "canary_absent": not hasattr(CG, "_V_CANARY")}
try:
    q, lr = CG.load_checkpoint(owner, activate=False)
    out.update({
        "generation_id": lr["generation_id"],
        "recovered_from": lr["recovered_from"],
        "nursery_ids": sorted(q.nursery.proposals.keys()),
        "plane_ids": sorted(q.cube.session.plane.units.keys()),
    })
except CheckpointNotEstablished:
    out["not_established"] = True
except CheckpointLoadError as exc:
    out["load_error"] = str(exc)[:160]
with open(sidecar, "w") as f:
    json.dump(out, f)
'''


def _write_child(name: str, template: str) -> Path:
    p = Path(f"/tmp/dccxviii_{name}_{os.getpid()}.py")
    p.write_text(template.replace("__REPO__", repr(str(REPO))))
    return p


def _run_child(script: Path, *args: str) -> tuple[int, str, str]:
    proc = subprocess.run([sys.executable, str(script), *args],
                          capture_output=True, text=True, timeout=180)
    return proc.returncode, proc.stdout, proc.stderr


def _read_sidecar(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def control_v_process_matrix() -> None:
    commit_py = _write_child("commit", _CHILD_COMMIT)
    load_py = _write_child("load", _CHILD_LOAD)
    scenarios = [
        # (name, committer mode, crash_at, parent file manipulation, expected generation, expected recovered_from)
        ("normal", "commit2", "none", None, "gv00000000000002", None),
        ("crash_before_members", "commit2", "before_members", None, "gv00000000000001", None),
        ("crash_after_member1", "commit2", "member_nursery", None, "gv00000000000001", None),
        ("crash_after_all_members", "commit2", "after_members", None, "gv00000000000001", None),
        ("crash_after_commit", "commit2", "after_commit", None, "gv00000000000002", None),
        ("missing_member", "commit2", "none", "del_program_member", "gv00000000000001", "gv00000000000002"),
        ("corrupt_member", "commit2", "none", "trunc_nursery_member", "gv00000000000001", "gv00000000000002"),
        ("swapped_member", "commit2", "none", "swap_nursery_member", "gv00000000000001", "gv00000000000002"),
        ("corrupt_manifest", "commit2", "none", "corrupt_manifest", "gv00000000000001", "gv00000000000002"),
        ("stale_g2", "seal_only", "none", None, "gv00000000000001", None),
        ("repeated", "commit4", "none", None, "gv00000000000004", None),
    ]
    all_ok = True
    for idx, (name, mode, crash_at, manip, exp_gen, exp_rec) in enumerate(scenarios):
        o = f"DCCXVIII_V{idx}"
        wipe_owner(o)
        OWNERS.append(o)
        sidecar_c, sidecar_l = Path(f"/tmp/dccxviii_c_{idx}.json"), Path(f"/tmp/dccxviii_l_{idx}.json")
        rc, _, err = _run_child(commit_py, o, mode, crash_at, str(sidecar_c))
        died_at_boundary = crash_at not in ("none",)
        if died_at_boundary and rc != 42:
            check(f"V.{name}_child_died", False)
            all_ok = False
            print(f"    V.{name}: RED (child rc={rc} err={err[-200:]})")
            continue
        if not died_at_boundary and rc != 0:
            check(f"V.{name}_child_ok", False)
            all_ok = False
            print(f"    V.{name}: RED (child rc={rc} err={err[-200:]})")
            continue
        if manip == "del_program_member":
            (Path(CG._member_path(o, "program", "gv00000000000002"))).unlink()
        elif manip == "trunc_nursery_member":
            mp = Path(CG._member_path(o, "nursery", "gv00000000000002"))
            mp.write_bytes(mp.read_bytes()[:17])
        elif manip == "swap_nursery_member":
            g1 = (Path(CG._member_path(o, "nursery", "gv00000000000001"))).read_bytes()
            (Path(CG._member_path(o, "nursery", "gv00000000000002"))).write_bytes(g1)
        elif manip == "corrupt_manifest":
            (Path(CG._manifest_path(o, "gv00000000000002"))).write_bytes(b"[[[bad")
        rc2, _, err2 = _run_child(load_py, o, str(sidecar_l))
        if rc2 != 0:
            check(f"V.{name}_load", False)
            all_ok = False
            print(f"    V.{name}: RED (loader rc={rc2} err={err2[-200:]})")
            continue
        out = _read_sidecar(sidecar_l)
        cpid = _read_sidecar(sidecar_c)["pid"] if sidecar_c.is_file() else -1
        ok = (
            out.get("generation_id") == exp_gen
            and out.get("recovered_from") == exp_rec
            and out.get("pid") != cpid
            and out.get("canary_absent") is True
            and len(out.get("nursery_ids", [])) > 0
        )
        check(f"V.{name}", ok)
        all_ok = all_ok and ok
        print(f"    V.{name}: {'GREEN' if ok else 'RED'}")
    # multi-stale: parent seals G2/G3/G4 without pointer; loader must pick G1.
    o = "DCCXVIII_VM"
    wipe_owner(o)
    OWNERS.append(o)
    p = open_program(o)
    _ = p.nursery.add("vm base", words="victor multi base")
    p.confirm_proposal(_.id)
    CG.commit_checkpoint(p, generation_id="gvm0000000000001")
    for i, gid in enumerate(("gvm0000000000002", "gvm0000000000003", "gvm0000000000004")):
        pr = p.nursery.add(f"vm s{i}", words=f"victor multi stale {i}")
        p.confirm_proposal(pr.id)
        CG._seal_members(p, gid)
    sidecar_l = Path("/tmp/dccxviii_l_m.json")
    rc2, _, _ = _run_child(load_py, o, str(sidecar_l))
    out = _read_sidecar(sidecar_l)
    ok = rc2 == 0 and out.get("generation_id") == "gvm0000000000001" and out.get("canary_absent") is True
    check("V.multi_stale", ok)
    all_ok = all_ok and ok
    print(f"    V.multi_stale: {'GREEN' if ok else 'RED'}")
    print(f"  V literal process matrix: {'GREEN' if all_ok else 'RED'}")


# ---------------------------------------------------------------- CONTROL W
def control_w_preservation() -> None:
    import re
    import form.dell_matrix.atomic_write as _aw
    src = Path(REPO, "form", "mandell", "checkpoint_generation.py").read_text()
    check("W.no_direct_writes", re.search(r'open\([^)]*,\s*["\']w', src) is None)
    check("W.uses_v2_json", "atomic_write_json" in src)
    check("W.uses_v2_bytes", "atomic_write_bytes" in src)
    check("W.protocol_version", CHECKPOINT_PROTOCOL_VERSION == 1 and _aw.PERSISTENCE_PROTOCOL_VERSION == 2)
    # A temp-write crash on a member path leaves the canonical absent and no confusion.
    o = "DCCXVIII_W"
    wipe_owner(o)
    if o not in OWNERS:
        OWNERS.append(o)
    target = str(Path(CG._member_path(o, "nursery", "gw00000000000001")))
    try:
        atomic_write_bytes(target, b'{"x": 1}', _fail_at="temp_write")
        check("W.temp_crash_raises", False)
    except AtomicWriteError:
        check("W.temp_crash_raises", True)
    tmps = [f.name for f in STATE.glob("*.dmtmp.*")]
    check("W.temp_left_not_canonical", (not os.path.isfile(target)) and len(tmps) == 1)
    for t in tmps:
        try:
            (STATE / t).unlink()
        except OSError:
            pass
    check("W.no_pointer_without_commit", not CG.has_checkpoint(o))


# ---------------------------------------------------------------- RUN
def run() -> bool:
    for owner in list(OWNERS):
        wipe_owner(owner)
    OWNERS.clear()
    try:
        assert CHECKPOINT_PROTOCOL_VERSION == 1
        assert AW.PERSISTENCE_PROTOCOL_VERSION == 2
        control_a_normal_g1_g2()
        control_b_no_checkpoint()
        control_f_member_missing()
        control_g_member_corrupt()
        control_h_member_swap()
        control_i_manifest_and_pointer()
        control_j_stale_uncommitted()
        control_k_multiple_stale()
        control_l_load_atomicity()
        control_m_supersession()
        control_n_lineage_dependency()
        control_o_contextual_routing()
        control_p_owner_isolation()
        control_q_cross_owner_swap()
        control_r_repeated()
        control_s_retention()
        control_t_both_invalid()
        control_u_failure_atomicity()
        control_v_process_matrix()
        control_w_preservation()
    finally:
        for owner in list(OWNERS):
            wipe_owner(owner)
        OWNERS.clear()
        for t in STATE.glob("*.dmtmp.*"):
            try:
                t.unlink()
            except OSError:
                pass
        for f in Path("/tmp").glob("dccxviii_*"):
            try:
                f.unlink()
            except OSError:
                pass
    failed = [n for n, ok in CHECKS if not ok]
    total = len(CHECKS)
    passed = total - len(failed)
    print(f"DCC-XVIII: {passed}/{total}")
    if failed:
        print("FAILED:", failed)
    return not failed and total > 0


def smoke() -> bool:
    """Regress entry point: the full dedicated DCC-XVIII control suite."""
    return run()


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
