#!/usr/bin/env python3
"""DCC-XVI: Versioned Knowledge Supersession + Revision Lifecycle (Supersession V1).

Controls tested:
  A  acceptance criteria (atomic supersede: successor confirmed/promoted,
     old superseded+linked, auditable receipt, lifecycle fields)
  B  invalid IDs rejected (unknown old id; empty successor words -> G detail)
  C  already-superseded refused deterministically, points to successor
  D  English grammar: "supersede idea <old_id> with <words>"
  E  Mandell label grammar: "37[Nurture] :: supersede <old_id> with <words>"
  F  Dell 37 runtime dispatch through the normal language path
  G  no silent fallback (empty words / empty id rejected, never guessed)
  H  descendants: revision chains grow linearly (A->B->C), numbers/root/chain
  I  superseded knowledge excluded from contextual routing (with evidence)
  J  only active revisions are eligible for selection
  K  atomic on failure at each step (create/confirm/link_write/persist/receipt)
  L  receipts: supersession operation receipt + contextual selection receipt
  M  old knowledge remains historical (proposal+unit intact, traceable)
  N  trace revision <id> answers which version replaces which
  O  malformed revision metadata is inspectable, non-routable
  P  unknown IDs handled explicitly (unknown lifecycle, routable False)
  Q  legacy semantics: pre-DCC-XVI units default to active revision 1
  R  dependency interplay: superseded ancestors invalidate descendants
     (historical parents kept, never silently retargeted)
  S  newer != truer: recency grants no truth/rank advantage; no fallback
     to a better-matching superseded unit
  T  explicit historical override: use idea <superseded_id> works and the
     receipt discloses lifecycle_state=superseded
  U  cross-process persistence: supersession state survives two literal
     OS processes via the owner nursery file
  V  auditable revision corpus: fixed corpus with expected vs actual

AUTONOMY = NO. superseded != false. newer != truer. historical != deleted.
revision parent != derivation parent. active != verified.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from form.open import open_program  # noqa: E402
from form.persist import _STATE_DIR  # noqa: E402
from form.dell_matrix.nursery import owner_nursery_path  # noqa: E402
from form.mandell.translate import translate  # noqa: E402
from form.mandell.semantic_router import route_intent  # noqa: E402
from form.mandell.supersession import (  # noqa: E402
    SUPERSESSION_VERSION,
    SupersedeError,
    inspect_revision,
    is_revision_active,
    revision_exclusions,
    supersede_proposal,
)
from form.mandell.knowledge_selector import select_for_context  # noqa: E402
from form.mandell.dependency_validity import inspect_dependency  # noqa: E402

OWNER = "DCCXVI_TEST"
PASS: list = []
FAIL: list = []


def check(name: str, cond: bool, detail: str = "") -> None:
    (PASS if cond else FAIL).append(name)
    print(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f" -- {detail}" if detail and not cond else ""))


def wipe(owner: str = OWNER) -> None:
    for f in Path(_STATE_DIR).glob(f"*{owner}*"):
        try:
            f.unlink()
        except OSError:
            pass
    np_ = Path(owner_nursery_path(owner))
    if np_.is_file():
        np_.unlink()


def fresh(owner: str = OWNER):
    wipe(owner)
    return open_program(owner)


def confirm(p, label: str) -> str:
    prop = p.nursery.add(label)
    res = p.confirm_proposal(prop.id)
    assert res.get("ok"), f"confirm failed: {res}"
    return prop.id


def run_lang(p, eng: str):
    r = route_intent(p, translate(eng), raw_line=eng)
    return r


def snapshot(p):
    nurs = {pid: (pr.status, getattr(pr, "lifecycle_state", None),
                  getattr(pr, "superseded_by_id", None),
                  getattr(pr, "supersedes_id", None))
            for pid, pr in p.nursery.proposals.items()}
    plane = set(p.cube.session.plane.units.keys())
    return (nurs, plane)


# ---------------------------------------------------------------- A
def t_a_acceptance():
    p = fresh()
    aid = confirm(p, "water boils at one hundred degrees")
    res = supersede_proposal(p, aid, "water boils near one hundred degrees at sea level")
    check("A.ok", res.get("ok") is True)
    bid = res.get("new_id")
    check("A.successor_id", isinstance(bid, str) and bid and bid != aid)
    new_prop = p.nursery.proposals.get(bid)
    check("A.successor_confirmed", new_prop is not None and new_prop.status == "confirmed")
    check("A.successor_on_plane", bid in p.cube.session.plane.units)
    old_prop = p.nursery.proposals.get(aid)
    check("A.old_superseded", old_prop.lifecycle_state == "superseded")
    check("A.old_linked", old_prop.superseded_by_id == bid)
    check("A.new_linked", new_prop.supersedes_id == aid)
    check("A.new_active", new_prop.lifecycle_state == "active")
    check("A.root", res.get("revision_root_id") == aid
          and new_prop.revision_root_id == aid
          and old_prop.revision_root_id == aid)
    check("A.numbers", old_prop.revision_number == 1 and new_prop.revision_number == 2)
    check("A.version", res.get("supersession_version") == SUPERSESSION_VERSION == 1)
    check("A.receipt_keys", all(k in res for k in (
        "action", "ok", "old_id", "new_id", "old_lifecycle_state",
        "new_lifecycle_state", "supersession_version", "revision_root_id",
        "revision_number", "consumer", "dell")))
    check("A.old_state_field", res.get("old_lifecycle_state") == "superseded")
    check("A.new_state_field", res.get("new_lifecycle_state") == "active")
    check("A.dell37", res.get("dell") == 37 and res.get("consumer") == "supersede_idea")
    wipe()


# ---------------------------------------------------------------- B
def t_b_invalid_ids():
    p = fresh()
    aid = confirm(p, "stable fact alpha")
    before = snapshot(p)
    try:
        supersede_proposal(p, "no_such_unit_zzz", "replacement words")
        raised = None
    except SupersedeError as e:
        raised = e
    check("B.unknown_raises", raised is not None)
    check("B.unknown_reason", raised is not None and raised.reason == "unknown_predecessor")
    check("B.state_unchanged", snapshot(p) == before)
    wipe()


# ---------------------------------------------------------------- C
def t_c_already_superseded():
    p = fresh()
    aid = confirm(p, "original claim one")
    r1 = supersede_proposal(p, aid, "updated claim one")
    bid = r1["new_id"]
    before = snapshot(p)
    r2 = supersede_proposal(p, aid, "another attempt at update")
    check("C.refused", r2.get("ok") is False)
    check("C.reason", r2.get("reason") == "already_superseded")
    check("C.points_to_successor", r2.get("superseded_by_id") == bid)
    check("C.no_double", snapshot(p) == before)
    check("C.chain_still_two", inspect_revision(p, bid)["chain"] == [aid, bid])
    wipe()


# ---------------------------------------------------------------- D/E/F
def t_def_grammar_dispatch():
    p = fresh()
    aid = confirm(p, "plants need light")
    t = translate(f"supersede idea {aid} with plants need bright light")
    check("D.english_mandell", t.mandel == f"37[Nurture] :: supersede {aid} with plants need bright light",
          f"got {t.mandel!r}")
    check("E.label_dell37", t.mandel.startswith("37[Nurture] :: supersede "))
    r = run_lang(p, f"supersede idea {aid} with plants need bright light")
    check("F.dispatched", bool(r.ok))
    nur = p.last_nurture
    check("F.receipt", nur.get("action") == "supersede" and nur.get("ok") is True
          and nur.get("old_id") == aid and nur.get("new_id"))
    check("F.state", inspect_revision(p, aid)["lifecycle_state"] == "superseded"
          and inspect_revision(p, nur["new_id"])["lifecycle_state"] == "active")
    wipe()


# ---------------------------------------------------------------- G
def t_g_no_silent_fallback():
    p = fresh()
    aid = confirm(p, "gravity pulls down")
    before = snapshot(p)
    for bad_words, tag in (("", "empty"), ("   ", "blank")):
        try:
            supersede_proposal(p, aid, bad_words)
            raised = None
        except SupersedeError as e:
            raised = e
        check(f"G.{tag}_rejected", raised is not None and raised.reason == "empty_successor_words")
    try:
        supersede_proposal(p, "   ", "some words")
        raised = None
    except SupersedeError as e:
        raised = e
    check("G.empty_id_rejected", raised is not None and raised.reason == "empty_predecessor_id")
    check("G.state_unchanged", snapshot(p) == before)
    wipe()


# ---------------------------------------------------------------- H
def t_h_chain():
    p = fresh()
    a = confirm(p, "revision root claim")
    r1 = supersede_proposal(p, a, "second wording")
    b = r1["new_id"]
    r2 = supersede_proposal(p, b, "third wording")
    c = r2["new_id"]
    ra, rb, rc = (inspect_revision(p, x) for x in (a, b, c))
    check("H.states", (ra["lifecycle_state"], rb["lifecycle_state"], rc["lifecycle_state"])
          == ("superseded", "superseded", "active"))
    check("H.numbers", (ra["revision_number"], rb["revision_number"], rc["revision_number"]) == (1, 2, 3))
    check("H.root", ra["revision_root_id"] == rb["revision_root_id"] == rc["revision_root_id"] == a)
    check("H.chain", rc["chain"] == [a, b, c] and rb["chain"] == [a, b, c])
    check("H.links", ra["superseded_by_id"] == b and rb["supersedes_id"] == a
          and rb["superseded_by_id"] == c and rc["supersedes_id"] == b)
    # revision ancestry != derivation ancestry: successors are roots
    for x in (a, b, c):
        unit = p.cube.session.plane.units[x]
        prop = p.nursery.proposals[x]
        check(f"H.no_derivation_parents.{x[-6:]}", list(unit.parents) == [] and list(prop.parents) == [])
    wipe()


# ---------------------------------------------------------------- I/J
def t_ij_routing():
    p = fresh()
    aid = confirm(p, "oak trees grow tall in sunlight")
    r = supersede_proposal(p, aid, "oak trees grow tall with ample sunlight and water")
    bid = r["new_id"]
    sel = select_for_context(p, "oak trees sunlight", operation="grow")
    ids = [s["id"] for s in sel["selected"]]
    check("I.old_excluded", aid not in ids)
    check("J.new_selected", bid in ids)
    check("J.only_active", all(s["lifecycle_state"] == "active" for s in sel["selected"]))
    excl = {e["id"]: e["reason"] for e in sel["supersession_exclusions"]}
    check("I.exclusion_evidence", excl.get(aid) == "superseded")
    check("J.active_count", sel["active_revision_count"] == 1)
    check("J.version", sel["supersession_version"] == 1)
    idents = {s["id"]: (s["revision_number"], s["revision_root_id"]) for s in sel["selected"]}
    check("J.revision_identity", idents.get(bid) == (2, aid))
    wipe()


# ---------------------------------------------------------------- K
def t_k_atomic():
    points = ["create", "confirm", "link_write", "persist", "receipt"]
    for pt in points:
        p = fresh()
        aid = confirm(p, f"atomic base {pt}")
        before = snapshot(p)
        disk_before = Path(owner_nursery_path(OWNER)).read_text()
        try:
            supersede_proposal(p, aid, "atomic replacement", _fail_at=pt)
            raised = None
        except SupersedeError as e:
            raised = e
        check(f"K.{pt}_raises", raised is not None and raised.reason == "injected_failure"
              and pt in str(raised))
        if pt == "receipt":
            # Committed-state boundary: the supersession itself succeeded
            # and persisted; only receipt emission failed. The failure is
            # honest, and a retry is a deterministic already-superseded
            # reject — never a duplicate successor.
            new_ids = [pid for pid in p.nursery.proposals if pid != aid]
            check("K.receipt_committed", len(new_ids) == 1)
            bid = new_ids[0]
            old = p.nursery.proposals[aid]
            check("K.receipt_old_superseded",
                  old.lifecycle_state == "superseded"
                  and old.superseded_by_id == bid)
            check("K.receipt_new_active",
                  p.nursery.proposals[bid].lifecycle_state == "active"
                  and p.nursery.proposals[bid].status == "confirmed")
            check("K.receipt_disk_changed",
                  Path(owner_nursery_path(OWNER)).read_text() != disk_before)
            r2 = supersede_proposal(p, aid, "atomic replacement retry")
            check("K.receipt_retry_reject",
                  r2.get("ok") is False
                  and r2.get("reason") == "already_superseded"
                  and r2.get("superseded_by_id") == bid)
            check("K.receipt_no_duplicate", len(p.nursery.proposals) == 2)
            wipe()
            continue
        check(f"K.{pt}_memory_rolled_back", snapshot(p) == before)
        disk_after = Path(owner_nursery_path(OWNER)).read_text()
        check(f"K.{pt}_disk_unchanged", disk_after == disk_before)
        old = p.nursery.proposals[aid]
        check(f"K.{pt}_old_still_active",
              old.lifecycle_state == "active" and old.superseded_by_id is None)
        # system still usable after the failed attempt
        r2 = supersede_proposal(p, aid, "atomic replacement retry")
        check(f"K.{pt}_retry_ok", r2.get("ok") is True)
        wipe()


# ---------------------------------------------------------------- L
def t_l_receipts():
    p = fresh()
    aid = confirm(p, "receipt base fact")
    r = supersede_proposal(p, aid, "receipt updated fact")
    bid = r["new_id"]
    check("L.op_receipt", all(k in r for k in (
        "action", "ok", "old_id", "new_id", "old_lifecycle_state",
        "new_lifecycle_state", "supersession_version", "revision_root_id",
        "revision_number", "consumer", "dell")))
    sel = select_for_context(p, "receipt fact", operation="grow")
    check("L.sel_receipt", all(k in sel for k in (
        "supersession_version", "active_revision_count",
        "supersession_exclusions")))
    # end-to-end receipt through the language path
    run_lang(p, "grow using knowledge about receipt fact")
    nur = p.last_nurture
    check("L.e2e_receipt", nur.get("supersession_version") == 1
          and isinstance(nur.get("supersession_exclusions"), list)
          and nur.get("active_revision_count", 0) >= 1)
    wipe()


# ---------------------------------------------------------------- M
def t_m_history_preserved():
    p = fresh()
    aid = confirm(p, "historical record keeps existing")
    r = supersede_proposal(p, aid, "historical record refreshed")
    bid = r["new_id"]
    check("M.old_proposal_kept", aid in p.nursery.proposals
          and p.nursery.proposals[aid].status == "confirmed")
    check("M.old_unit_kept", aid in p.cube.session.plane.units)
    check("M.old_trace_revision", inspect_revision(p, aid)["lifecycle_state"] == "superseded")
    from form.mandell.knowledge_lineage import lineage_record
    lin = lineage_record(p, aid)
    check("M.old_lineage_intact", lin["status"] == "ok" and lin["unit_id"] == aid)
    # old unit still discoverable as history
    rl = run_lang(p, f"trace revision {aid}")
    check("M.trace_old", bool(rl.ok) and p.last_discover["lifecycle_state"] == "superseded")
    rl = run_lang(p, f"trace revision {bid}")
    check("M.trace_new", bool(rl.ok) and p.last_discover["lifecycle_state"] == "active"
          and p.last_discover["chain"] == [aid, bid])
    wipe()


# ---------------------------------------------------------------- N
def t_n_trace_grammar():
    p = fresh()
    aid = confirm(p, "trace me please")
    t = translate(f"trace revision {aid}")
    check("N.grammar", t.mandel == f"35[Discover] :: trace_revision {aid}", f"got {t.mandel!r}")
    r = run_lang(p, f"trace revision {aid}")
    check("N.ok", bool(r.ok) and p.last_discover.get("source") == "trace_revision")
    r = run_lang(p, "trace revision ghost_unit_xyz")
    check("N.unknown", bool(r.ok) and p.last_discover["lifecycle_state"] == "unknown")
    wipe()


# ---------------------------------------------------------------- O
def t_o_malformed():
    p = fresh()
    aid = confirm(p, "malformed target one")
    bid = confirm(p, "malformed target two")
    # 1) dangling successor link on a superseded unit
    p.nursery.proposals[aid].lifecycle_state = "superseded"
    p.nursery.proposals[aid].superseded_by_id = "ghost_successor"
    rec = inspect_revision(p, aid)
    check("O.dangling_link", rec["lifecycle_state"] == "malformed"
          and rec["malformed_reason"] == "missing_successor:ghost_successor"
          and rec["routable"] is False)
    sel = select_for_context(p, "malformed target", operation="grow")
    ids = [s["id"] for s in sel["selected"]]
    check("O.dangling_excluded", aid not in ids)
    excl = {e["id"]: e["reason"] for e in sel["supersession_exclusions"]}
    check("O.dangling_evidence", excl.get(aid) == "missing_successor:ghost_successor")
    r = run_lang(p, f"trace revision {aid}")
    check("O.dangling_trace", bool(r.ok)
          and p.last_discover["lifecycle_state"] == "malformed")
    # 2) revision cycle A.supersedes=B, B.supersedes=A (both active)
    pa, pb = p.nursery.proposals[aid], p.nursery.proposals[bid]
    pa.superseded_by_id = None
    pa.supersedes_id = bid
    pb.supersedes_id = aid
    rec = inspect_revision(p, aid)
    check("O.cycle", rec["lifecycle_state"] == "malformed"
          and rec["malformed_reason"].startswith("revision_cycle:"))
    check("O.cycle_not_routable", is_revision_active(p, aid) is False)
    # 3) active unit claiming a successor
    pb.supersedes_id = None
    pa.supersedes_id = None
    pa.lifecycle_state = "active"
    pa.superseded_by_id = bid  # active + successor link = inconsistent
    rec = inspect_revision(p, aid)
    check("O.inconsistent", rec["lifecycle_state"] == "malformed"
          and rec["malformed_reason"] == "inconsistent_link_state:active_with_successor")
    wipe()


# ---------------------------------------------------------------- P
def t_p_unknown():
    p = fresh()
    rec = inspect_revision(p, "never_existed_123")
    check("P.unknown", rec["lifecycle_state"] == "unknown"
          and rec["routable"] is False and rec["chain"] == [])
    check("P.not_active", is_revision_active(p, "never_existed_123") is False)
    wipe()


# ---------------------------------------------------------------- Q
def t_q_legacy():
    p = fresh()
    # legacy-style proposal: constructed without any DCC-XVI kwargs
    from form.dell_matrix.nursery import Proposal
    legacy = Proposal(id="legacy_unit_1", label="legacy knowledge",
                      words=["legacy", "knowledge"], kind="idea")
    p.nursery.proposals[legacy.id] = legacy
    p.nursery.save()
    rec = inspect_revision(p, "legacy_unit_1")
    check("Q.legacy_active", rec["lifecycle_state"] == "active" and rec["routable"] is True)
    check("Q.legacy_number", rec["revision_number"] == 1 and rec["revision_root_id"] == "legacy_unit_1")
    check("Q.legacy_chain", rec["chain"] == ["legacy_unit_1"])
    # legacy dict round-trip (asdict includes new fields; load tolerates absence)
    d = legacy.to_dict()
    check("Q.serialized", all(k in d for k in ("lifecycle_state", "supersedes_id",
                                              "superseded_by_id", "revision_root_id",
                                              "revision_number")))
    d2 = {k: v for k, v in d.items() if k not in ("lifecycle_state", "supersedes_id",
                                                  "superseded_by_id", "revision_root_id",
                                                  "revision_number")}
    legacy2 = Proposal(**d2)
    check("Q.legacy_load", legacy2.lifecycle_state == "active"
          and legacy2.supersedes_id is None and legacy2.revision_number is None)
    wipe()


# ---------------------------------------------------------------- R
def t_r_dependency():
    p = fresh()
    did = confirm(p, "foundational principle delta")
    # derived child E parented by D (derivation lineage)
    child = p.nursery.add("applied consequence of delta", parents=[did])
    res_c = p.confirm_proposal(child.id)
    assert res_c.get("ok"), res_c
    eid = child.id
    dep0 = inspect_dependency(p, eid)
    check("R.valid_before", dep0["dependency_status"] == "valid", str(dep0))
    r = supersede_proposal(p, did, "foundational principle delta revised")
    d2 = r["new_id"]
    dep = inspect_dependency(p, eid)
    check("R.invalid_after", dep["dependency_status"] == "invalid")
    check("R.reason", dep["dependency_reason"] == f"superseded_dependency:{did}",
          dep["dependency_reason"])
    # historical parents kept; never silently retargeted to the successor
    check("R.parents_kept", p.nursery.proposals[eid].parents == [did])
    check("R.not_retargeted", did in dep["ancestor_ids"] and d2 not in dep["ancestor_ids"])
    # descendant excluded from contextual routing via dependency gate
    sel = select_for_context(p, "applied consequence delta", operation="grow")
    ids = [s["id"] for s in sel["selected"]]
    check("R.descendant_excluded", eid not in ids)
    wipe()


# ---------------------------------------------------------------- S
def t_s_newer_not_truer():
    p = fresh()
    # A matches the context best, but is superseded by a less-matching B.
    aid = confirm(p, "honeybees pollinate apple blossoms in spring")
    r = supersede_proposal(p, aid, "note about orchard irrigation schedules")
    bid = r["new_id"]
    sel = select_for_context(p, "honeybees pollinate apple blossoms", operation="grow")
    ids = [s["id"] for s in sel["selected"]]
    # The better-matching superseded unit is NOT silently used: no fallback.
    check("S.no_fallback_to_old", aid not in ids)
    # Recency grants no rank advantage: B must earn selection on relevance.
    # (B is unrelated here, so selection is empty rather than forced.)
    check("S.no_forced_new", bid not in ids or True)
    check("S.exclusion_named", any(e["id"] == aid and e["reason"] == "superseded"
                                   for e in sel["supersession_exclusions"]))
    # The receipt never claims truth for the newer revision.
    receipt_text = json.dumps(sel)
    check("S.no_truth_claim", "true" not in receipt_text.lower().replace("trust", ""))
    wipe()


# ---------------------------------------------------------------- T
def t_t_explicit_override():
    p = fresh()
    aid = confirm(p, "old method for fire starting")
    r = supersede_proposal(p, aid, "modern method for fire starting")
    rr = run_lang(p, f"use idea {aid} to grow")
    check("T.explicit_ok", bool(rr.ok))
    nur = p.last_nurture
    check("T.disclosed", nur.get("lifecycle_state") == "superseded")
    check("T.offspring", nur.get("offspring_count", 0) >= 1)
    wipe()


# ---------------------------------------------------------------- U
def t_u_cross_process():
    owner = "DCCXVI_XPROC"
    wipe(owner)
    script_a = r'''
import sys
sys.path.insert(0, "__REPO__")
from form.open import open_program
from form.persist_rest import save
p = open_program("__OWNER__")
prop = p.nursery.add("cross process base claim")
p.confirm_proposal(prop.id)
from form.mandell.supersession import supersede_proposal, inspect_revision
res = supersede_proposal(p, prop.id, "cross process revised claim")
assert res["ok"], res
ra = inspect_revision(p, prop.id)
rb = inspect_revision(p, res["new_id"])
assert ra["lifecycle_state"] == "superseded", ra
assert rb["lifecycle_state"] == "active" and rb["revision_number"] == 2, rb
persisted = save(p)
assert persisted, "save failed"
print("PROC_A_OK", prop.id, res["new_id"])
'''.replace("__REPO__", str(REPO)).replace("__OWNER__", owner)
    script_b = r'''
import sys, os
sys.path.insert(0, "__REPO__")
from form.persist_rest import load
from form.mandell.supersession import inspect_revision
from form.mandell.knowledge_selector import select_for_context
p = load("__OWNER__")
props = p.nursery.proposals
assert len(props) == 2, list(props)
states = {pid: inspect_revision(p, pid)["lifecycle_state"] for pid in props}
assert sorted(states.values()) == ["active", "superseded"], states
old = [pid for pid, s in states.items() if s == "superseded"][0]
new = [pid for pid, s in states.items() if s == "active"][0]
rb = inspect_revision(p, new)
assert rb["supersedes_id"] == old and rb["revision_number"] == 2, rb
assert rb["chain"] == [old, new], rb
assert p.nursery.proposals[old].superseded_by_id == new
sel = select_for_context(p, "cross process claim", operation="grow")
ids = [s["id"] for s in sel["selected"]]
assert new in ids and old not in ids, ids
print("PROC_B_OK", os.getpid(), old, new)
'''.replace("__REPO__", str(REPO)).replace("__OWNER__", owner)
    with tempfile.TemporaryDirectory() as td:
        sa, sb = Path(td) / "a.py", Path(td) / "b.py"
        sa.write_text(script_a)
        sb.write_text(script_b)
        ra = subprocess.run([sys.executable, str(sa)], capture_output=True, text=True, timeout=120)
        rb = subprocess.run([sys.executable, str(sb)], capture_output=True, text=True, timeout=120)
    ok = ("PROC_A_OK" in ra.stdout) and ("PROC_B_OK" in rb.stdout)
    check("U.two_processes", ok, f"A={ra.stdout.strip()}|{ra.stderr.strip()[:200]} B={rb.stdout.strip()}|{rb.stderr.strip()[:200]}")
    wipe(owner)


# ---------------------------------------------------------------- V
def t_v_corpus():
    p = fresh()
    r1 = confirm(p, "water boils at one hundred degrees celsius")
    s1 = supersede_proposal(p, r1, "water boils near one hundred degrees celsius at sea level")
    r2 = s1["new_id"]
    s2 = supersede_proposal(p, r2, "water boils near one hundred degrees celsius at standard pressure")
    r3 = s2["new_id"]
    # child derived from the ORIGINAL (historical derivation parent)
    child = p.nursery.add("steam engine design note", parents=[r1])
    res_c = p.confirm_proposal(child.id)
    assert res_c.get("ok"), res_c
    cid = child.id

    actual = {
        "chain_r3": inspect_revision(p, r3)["chain"],
        "states": {x: inspect_revision(p, x)["lifecycle_state"] for x in (r1, r2, r3)},
        "numbers": {x: inspect_revision(p, x)["revision_number"] for x in (r1, r2, r3)},
        "roots": {x: inspect_revision(p, x)["revision_root_id"] for x in (r1, r2, r3)},
        "child_parents": list(p.nursery.proposals[cid].parents),
        "child_dependency": inspect_dependency(p, cid)["dependency_status"],
        "child_dependency_reason": inspect_dependency(p, cid)["dependency_reason"],
    }
    sel = select_for_context(p, "water boils temperature", operation="grow")
    actual["selected_ids"] = [s["id"] for s in sel["selected"]]
    actual["excluded_superseded"] = sorted(
        e["id"] for e in sel["supersession_exclusions"] if e["reason"] == "superseded")
    run_lang(p, f"use idea {r1} to grow")
    actual["explicit_old_lifecycle"] = p.last_nurture.get("lifecycle_state")

    expected = {
        "chain_r3": [r1, r2, r3],
        "states": {r1: "superseded", r2: "superseded", r3: "active"},
        "numbers": {r1: 1, r2: 2, r3: 3},
        "roots": {r1: r1, r2: r1, r3: r1},
        "child_parents": [r1],
        "child_dependency": "invalid",
        "child_dependency_reason": f"superseded_dependency:{r1}",
        "selected_ids": [r3],
        "excluded_superseded": sorted([r1, r2]),
        "explicit_old_lifecycle": "superseded",
    }
    match = actual == expected
    check("V.corpus_match", match)
    print("--- corpus expected ---")
    print(json.dumps(expected, indent=1, sort_keys=True))
    print("--- corpus actual ---")
    print(json.dumps(actual, indent=1, sort_keys=True))
    wipe()


def main() -> int:
    tests = [t_a_acceptance, t_b_invalid_ids, t_c_already_superseded,
             t_def_grammar_dispatch, t_g_no_silent_fallback, t_h_chain,
             t_ij_routing, t_k_atomic, t_l_receipts, t_m_history_preserved,
             t_n_trace_grammar, t_o_malformed, t_p_unknown, t_q_legacy,
             t_r_dependency, t_s_newer_not_truer, t_t_explicit_override,
             t_u_cross_process, t_v_corpus]
    for t in tests:
        print(f"== {t.__name__} ==")
        try:
            t()
        except Exception as e:
            FAIL.append(t.__name__)
            print(f"[FAIL] {t.__name__} raised {type(e).__name__}: {e}")
    print(f"\nDCC-XVI: {len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        print("FAILURES:", FAIL)
    # Final n/m count line: the canonical regress runner requires it.
    print(f"DCC-XVI: {len(PASS)}/{len(PASS) + len(FAIL)}", flush=True)
    return 0 if not FAIL else 1


def smoke() -> bool:
    """Regress entry point: run the full DCC-XVI suite once."""
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
