#!/usr/bin/env python3
"""PAC-I: Persistence Authority Convergence tests.

Proves ONE AUTHORITATIVE DURABLE STATE PATH:

    Dell 27 > canonical checkpoint op > Persistence V2 >
    Checkpoint Generation V1 > atomic durable generation

Controls:
  A  Dell 27 commits a real Generation V1 generation (live operation proof);
     generation identity observable via result + CURRENT pointer
  B  generation roundtrip: G1 -> mutate -> G2 -> load G2 exact; load G1 exact
  C  cross-process restore: fresh OS process loads the committed generation
  D  corrupt current member -> deterministic recovery of previous generation
  E  current + previous invalid -> explicit CheckpointLoadError (no fabrication)
  F  failure injection at every pre-commit stage -> prior generation wins;
     after_commit -> new generation wins
  G  literal crash boundaries (os._exit in subprocess): before CURRENT commit
     -> G1 authoritative; after commit -> G2 authoritative
  H  no-hybrid: crash around G2 never mixes K1/D1/O1 with K2/D2/O2
  I  Outcome V1 coherence: outcomes sealed per-generation with knowledge
  J  disposition coherence: conflict_dispositions sealed per-generation
  K  revision coherence: supersession chains survive generation load
  L  save/load symmetry: _last_result/action_stack/last_nurture ephemeral;
     canonical fields round-trip
  M  undo authority: place-undo delegates to plane.remove; revision-owned
     units refused; edit-undo restores + evidences
  N  sidecar authority: selfgrow files noncanonical, unread by canonical paths

AUTONOMY = NO.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from form.open import open_program
from form.persist import _STATE_DIR, _safe_owner
from form.mandell import checkpoint_generation as gen
from form.mandell import core_i_recovery as cir
from form.mandell.executor import execute_seed
from form.mandell.checkpoint_generation import (
    CheckpointCommitError,
    CheckpointLoadError,
    _load_generation,
)

PASS = 0
FAIL = 0
FAILURES = []


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        FAILURES.append(f"{name}: {detail}")


def _owner(tag):
    return f"pac1_{tag}"


def _cleanup(owner):
    safe = _safe_owner(owner)
    try:
        for name in os.listdir(_STATE_DIR):
            if safe not in name:
                continue
            # Never delete collision-safe temp files (Persistence V2): a
            # concurrent process may be mid-replace on its own temp.
            if ".dmtmp." in name:
                continue
            p = os.path.join(_STATE_DIR, name)
            try:
                if os.path.isfile(p):
                    os.remove(p)
            except OSError:
                pass
    except OSError:
        pass
    # generation namespace dirs/files for this owner
    try:
        ns = gen._owner_ns(owner)
        for name in os.listdir(_STATE_DIR):
            if ns in name and ".dmtmp." not in name:
                p = os.path.join(_STATE_DIR, name)
                try:
                    if os.path.isfile(p):
                        os.remove(p)
                except OSError:
                    pass
    except OSError:
        pass


def _fresh(owner):
    _cleanup(owner)
    return open_program(owner)


_SEEDED = {"welcome"}  # open_program seeds a default welcome unit; not under test


def _units(prog):
    return set(prog.cube.session.plane.units.keys()) - _SEEDED


# ── A: Dell 27 commits a real generation ──────────────────────────────────
def test_a():
    owner = _owner("a")
    p = _fresh(owner)
    out = execute_seed(p, "27[Checkpoint]")
    check("A.ok", out.get("ok") is True, f"dell27 failed: {out.get('error')}")
    gid = out.get("generation_id")
    check("A.gen_id", isinstance(gid, str) and len(gid) >= 4, f"no generation id: {gid}")
    check("A.pointer", gen.current_generation_id(owner) == gid,
          "CURRENT pointer does not name the Dell 27 generation")
    check("A.manifest", os.path.isfile(gen._manifest_path(owner, gid)), "manifest missing")
    check("A.last_checkpoint", getattr(p, "last_checkpoint", None) == gid,
          "program.last_checkpoint not set to generation id")
    check("A.msg", "generation" in " ".join(out.get("messages", [])).lower(),
          "Dell 27 message does not name the generation")
    _cleanup(owner)


# ── B: generation roundtrip ───────────────────────────────────────────────
def test_b():
    owner = _owner("b")
    p = _fresh(owner)
    p.place("u1", "Unit One", words="first knowledge")
    g1 = cir.checkpoint(p)
    p.place("u2", "Unit Two", words="second knowledge")
    g2 = cir.checkpoint(p)
    check("B.g1!=g2", g1 != g2, "generation ids must differ")
    prog2, _r2 = _load_generation(owner, g2, False, None)
    units2 = _units(prog2)
    check("B.g2_units", units2 == {"u1", "u2"}, f"G2 units wrong: {units2}")
    prog1, _r1 = _load_generation(owner, g1, False, None)
    units1 = _units(prog1)
    check("B.g1_units", units1 == {"u1"}, f"G1 units wrong: {units1}")
    _cleanup(owner)


# ── C: cross-process restore ──────────────────────────────────────────────
def test_c():
    owner = _owner("c")
    p = _fresh(owner)
    p.place("uc", "Cross Unit", words="cross process knowledge")
    gid = cir.checkpoint(p)
    code = (
        "import sys; sys.path.insert(0, %r); "
        "from form.mandell.checkpoint_generation import load_checkpoint; "
        "prog, rec = load_checkpoint(%r, activate=False); "
        "print('PID_OK'); "
        "print('GEN:' + rec['generation_id']); "
        "print('UNITS:' + ','.join(sorted(prog.cube.session.plane.units.keys()))); "
        "print('OUTCOME_LEDGER:' + str('outcome_ledger' in 'x'))"
        % (str(REPO), owner)
    )
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=120)
    out = r.stdout
    check("C.proc", r.returncode == 0, f"subprocess failed: {r.stderr[:300]}")
    check("C.gen", f"GEN:{gid}" in out, f"generation mismatch: {out[:200]}")
    check("C.units", "UNITS:" in out and "uc" in out.split("UNITS:")[1].split("\n")[0],
          f"units mismatch: {out[:200]}")
    _cleanup(owner)


# ── D: corrupt current -> recover previous ────────────────────────────────
def test_d():
    owner = _owner("d")
    p = _fresh(owner)
    p.place("ud1", "D One", words="d1")
    g1 = cir.checkpoint(p)
    p.place("ud2", "D Two", words="d2")
    g2 = cir.checkpoint(p)
    # Corrupt the CURRENT generation's program member on disk.
    mpath = os.path.join(_STATE_DIR, gen._read_manifest(owner, g2)["members"]["program"]["file"])
    with open(mpath, "wb") as f:
        f.write(b"{corrupt!!")
    prog, rec = gen.load_checkpoint(owner, activate=False)
    units = _units(prog)
    check("D.recovered", units == {"ud1"}, f"expected G1 units, got {units}")
    check("D.recovered_from", rec.get("recovered_from") == g2,
          f"recovered_from wrong: {rec.get('recovered_from')}")
    check("D.g1_intact", rec.get("generation_id") == g1, "did not load G1")
    _cleanup(owner)


# ── E: both invalid -> explicit failure ───────────────────────────────────
def test_e():
    owner = _owner("e")
    p = _fresh(owner)
    p.place("ue1", "E One", words="e1")
    g1 = cir.checkpoint(p)
    p.place("ue2", "E Two", words="e2")
    g2 = cir.checkpoint(p)
    for gid in (g1, g2):
        mpath = os.path.join(_STATE_DIR, gen._read_manifest(owner, gid)["members"]["program"]["file"])
        with open(mpath, "wb") as f:
            f.write(b"{corrupt!!")
    try:
        gen.load_checkpoint(owner, activate=False)
        check("E.explicit", False, "expected CheckpointLoadError, got success")
    except CheckpointLoadError:
        check("E.explicit", True)
    except Exception as exc:
        check("E.explicit", False, f"wrong exception: {type(exc).__name__}: {exc}")
    _cleanup(owner)


# ── F: failure-injection matrix ───────────────────────────────────────────
def test_f():
    stages = ["save_nursery", "save_program", "before_members", "member_nursery",
              "member_program", "manifest", "after_members", "pointer"]
    for stage in stages:
        owner = _owner(f"f_{stage}")
        p = _fresh(owner)
        p.place("uf", "F Unit", words="f")
        g1 = cir.checkpoint(p)
        p.place("uf2", "F Unit 2", words="f2")
        try:
            gen.commit_checkpoint(p, _fail_at=stage)
            check(f"F.{stage}.raises", False, "expected CheckpointCommitError")
        except CheckpointCommitError:
            check(f"F.{stage}.raises", True)
        except Exception as exc:
            check(f"F.{stage}.raises", False, f"wrong exc: {type(exc).__name__}")
        # Prior generation must remain authoritative.
        try:
            prog, rec = gen.load_checkpoint(owner, activate=False)
            units = _units(prog)
            check(f"F.{stage}.prior", units == {"uf"} and rec.get("generation_id") == g1,
                  f"prior generation not authoritative: {units}")
        except Exception as exc:
            check(f"F.{stage}.prior", False, f"load failed: {exc}")
        _cleanup(owner)
    # after_commit: the pointer WAS swapped before the injected failure, so the
    # new generation is authoritative (DCC-XVIII law: crash after commit -> G2).
    owner = _owner("f_after")
    p = _fresh(owner)
    p.place("ufa", "FA Unit", words="fa")
    cir.checkpoint(p)
    p.place("ufa2", "FA Unit 2", words="fa2")
    try:
        rec = gen.commit_checkpoint(p, _fail_at="after_commit")
        check("F.after_commit.raises", False, "after_commit must raise post-commit")
        rec_id = rec["generation_id"]
    except CheckpointCommitError:
        check("F.after_commit.raises", True)
        rec_id = gen.current_generation_id(owner)
    prog, lrec = gen.load_checkpoint(owner, activate=False)
    units = _units(prog)
    check("F.after_commit.wins", units == {"ufa", "ufa2"} and lrec.get("generation_id") == rec_id,
          f"post-commit generation not authoritative: {units}")
    _cleanup(owner)

# ── G: literal crash boundaries (os._exit in subprocess) ──────────────────
_CRASH_CHILD = (
    "import sys, os; sys.path.insert(0, %r); "
    "from form import persist_rest; "
    "from form.mandell import checkpoint_generation as gen; "
    "p = persist_rest.load(%r); "
    "p.place('ugx', 'Crash Unit', words='crash'); "
    "sealed = gen._seal_members(p, %r); "
    "os._exit(%d)"
)


def _run_crash_child(owner, gen_id, exit_after_commit):
    """Child loads live state, seals members for a new generation, then dies
    before/after the CURRENT commit boundary."""
    if exit_after_commit:
        code = (
            "import sys, os; sys.path.insert(0, %r); "
            "from form import persist_rest; "
            "from form.mandell import checkpoint_generation as gen; "
            "p = persist_rest.load(%r); "
            "p.place('ugx', 'Crash Unit', words='crash'); "
            "rec = gen.commit_checkpoint(p, generation_id=%r); "
            "os._exit(0)"
        ) % (str(REPO), owner, gen_id)
    else:
        code = _CRASH_CHILD % (str(REPO), owner, gen_id, 0)
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=120)
    return r


def test_g():
    # Before CURRENT commit: previous generation authoritative.
    owner = _owner("g_before")
    p = _fresh(owner)
    p.place("ug1", "G One", words="g1")
    g1 = cir.checkpoint(p)
    _run_crash_child(owner, "gcrashbefore", exit_after_commit=False)
    prog, rec = gen.load_checkpoint(owner, activate=False)
    units = _units(prog)
    check("G.before.g1", units == {"ug1"} and rec.get("generation_id") == g1,
          f"pre-commit crash must leave G1 authoritative: {units}")
    _cleanup(owner)
    # After CURRENT commit: new generation authoritative.
    owner = _owner("g_after")
    p = _fresh(owner)
    p.place("ug1", "G One", words="g1")
    cir.checkpoint(p)
    _run_crash_child(owner, "gcrashafter", exit_after_commit=True)
    prog, rec = gen.load_checkpoint(owner, activate=False)
    units = _units(prog)
    check("G.after.g2", units == {"ug1", "ugx"} and rec.get("generation_id") == "gcrashafter",
          f"post-commit crash must leave G2 authoritative: {units}")
    _cleanup(owner)


def _snap_state(prog):
    """Canonical (K, D, O) triple from a loaded program."""
    k = sorted(_units(prog))
    d = dict(getattr(prog.nursery, "conflict_dispositions", {}) or {})
    o = sorted((getattr(prog, "outcome_records", {}) or {}).keys())
    return k, d, o


def test_h():
    # H: no-hybrid — crash around G2 yields exactly G1 or exactly G2.
    owner = _owner("h")
    p = _fresh(owner)
    p.place("uk1", "K One", words="k1")
    p.nursery.conflict_dispositions["q1"] = {"disposition": "prefer", "unit_id": "uk1"}
    p.outcome_records["out1:o1"] = {"outcome_version": 1, "outcome_id": "out1:o1", "result": "completed", "op": "grow", "outcome_is_observation": True}
    p.outcome_seq = 1
    g1 = cir.checkpoint(p)
    k1, d1, o1 = _snap_state(p)
    p.place("uk2", "K Two", words="k2")
    p.nursery.conflict_dispositions["q2"] = {"disposition": "coexist", "unit_id": "uk2"}
    p.outcome_records["out1:o2"] = {"outcome_version": 1, "outcome_id": "out1:o2", "result": "blocked", "op": "grow", "outcome_is_observation": True}
    p.outcome_seq = 2
    k2, d2, o2 = _snap_state(p)
    try:
        gen.commit_checkpoint(p, generation_id="ghybrid", _fail_at="pointer")
        check("H.raises", False, "expected CheckpointCommitError at pointer stage")
    except CheckpointCommitError:
        check("H.raises", True)
    prog, rec = gen.load_checkpoint(owner, activate=False)
    k, d, o = _snap_state(prog)
    is_g1 = (k == k1 and d == d1 and o == o1)
    is_g2 = (k == k2 and d == d2 and o == o2)
    check("H.no_hybrid", is_g1 or is_g2,
          f"hybrid state observed: k={k} d={sorted(d)} o={o}")
    check("H.is_g1", is_g1, "pre-commit crash must yield exactly G1 triple")
    _cleanup(owner)


# ── I: Outcome V1 coherence ───────────────────────────────────────────────
def test_i():
    owner = _owner("i")
    p = _fresh(owner)
    p.place("ui1", "I One", words="i1")
    p.outcome_records["out1:oi1"] = {"outcome_version": 1, "outcome_id": "out1:oi1",
                                "result": "completed", "op": "grow",
                                "outcome_is_observation": True}
    p.outcome_seq = 1
    g1 = cir.checkpoint(p)
    p.outcome_records["out1:oi2"] = {"outcome_version": 1, "outcome_id": "out1:oi2",
                                "result": "blocked", "op": "grow",
                                "outcome_is_observation": True}
    p.outcome_seq = 2
    g2 = cir.checkpoint(p)
    prog2, _r = _load_generation(owner, g2, False, None)
    o2 = sorted((getattr(prog2, "outcome_records", {}) or {}).keys())
    check("I.g2_outcomes", o2 == ["out1:oi1", "out1:oi2"], f"G2 outcomes wrong: {o2}")
    check("I.g2_seq", getattr(prog2, "outcome_seq", 0) == 2, "outcome_seq not durable")
    prog1, _r = _load_generation(owner, g1, False, None)
    o1 = sorted((getattr(prog1, "outcome_records", {}) or {}).keys())
    check("I.g1_outcomes", o1 == ["out1:oi1"], f"G1 outcomes wrong: {o1}")
    rec = prog2.outcome_records["out1:oi1"]
    check("I.observation", rec.get("outcome_is_observation") is True and "truth" not in str(rec).lower(),
          "outcome record must stay observation-only")
    _cleanup(owner)


# ── J: disposition coherence ──────────────────────────────────────────────
def test_j():
    owner = _owner("j")
    p = _fresh(owner)
    p.place("uj1", "J One", words="j1")
    p.nursery.conflict_dispositions["jq1"] = {"disposition": "prefer", "unit_id": "uj1",
                                              "disposition_version": 1}
    g1 = cir.checkpoint(p)
    p.nursery.conflict_dispositions["jq1"] = {"disposition": "clear", "unit_id": "uj1",
                                              "disposition_version": 1}
    g2 = cir.checkpoint(p)
    prog2, _r = _load_generation(owner, g2, False, None)
    d2 = dict(prog2.nursery.conflict_dispositions or {})
    check("J.g2_disposition", d2.get("jq1", {}).get("disposition") == "clear",
          f"G2 disposition wrong: {d2}")
    prog1, _r = _load_generation(owner, g1, False, None)
    d1 = dict(prog1.nursery.conflict_dispositions or {})
    check("J.g1_disposition", d1.get("jq1", {}).get("disposition") == "prefer",
          f"G1 disposition wrong: {d1}")
    _cleanup(owner)


# ── K: revision coherence ─────────────────────────────────────────────────
def test_k():
    from form.mandell.supersession import supersede_proposal, inspect_revision
    owner = _owner("k")
    p = _fresh(owner)
    # Seed a nursery proposal + plane unit pair.
    prop = p.nursery.add("Rev One")
    p.confirm_proposal(prop.id, _producer="test", _review_context=p.make_review_context(prop.id, "test"))
    pid = prop.id
    p.place(pid, "Rev One", words="rev seed words")
    g1 = cir.checkpoint(p)
    p.acceptance_policy.grant_opt_in("test", scope="test")
    res = supersede_proposal(p, pid, "rev successor words", label="Rev Two", _producer="test")
    check("K.supersede_ok", res.get("ok") is True, f"supersede failed: {res}")
    new_id = res.get("new_id")
    check("K.successor_id", isinstance(new_id, str) and new_id and new_id != pid,
          f"bad successor id: {new_id}")
    g2 = cir.checkpoint(p)
    prog2, _r = _load_generation(owner, g2, False, None)
    rev2 = inspect_revision(prog2, pid)
    check("K.g2_superseded", rev2.get("lifecycle_state") == "superseded",
          f"G2 revision state wrong: {rev2.get('lifecycle_state')}")
    prog1, _r = _load_generation(owner, g1, False, None)
    rev1 = inspect_revision(prog1, pid)
    check("K.g1_active", rev1.get("lifecycle_state") == "active",
          f"G1 revision state wrong: {rev1.get('lifecycle_state')}")
    _cleanup(owner)

# ── L: save/load symmetry classifications ─────────────────────────────────
def test_l():
    from form import persist_rest
    owner = _owner("l")
    p = _fresh(owner)
    p.place("ul1", "L One", words="l1")
    # In-memory-only state that must NOT persist.
    p.action_stack = [{"kind": "place", "id": "ul1", "label": "L One"}]
    p.last_nurture = {"fake": "stale"}
    p.last_checkpoint = "stale-pointer"
    try:
        p.core_ii.store["_last_result"] = {"matched": True}
        has_core_ii = True
    except Exception:
        has_core_ii = False
    persist_rest.save(p)
    p2 = persist_rest.load(owner)
    # EPHEMERAL_BY_DESIGN: none of these survive.
    check("L.action_stack", not getattr(p2, "action_stack", None),
          "action_stack must not persist")
    check("L.last_nurture", getattr(p2, "last_nurture", None) is None,
          "last_nurture must not persist (C1 freshness)")
    check("L.last_checkpoint", getattr(p2, "last_checkpoint", None) is None,
          "last_checkpoint must not persist")
    if has_core_ii:
        check("L._last_result", "_last_result" not in (p2.core_ii.store or {}),
              "_last_result must stay filtered from persistence")
    # DURABLE_REQUIRED: canonical state round-trips.
    check("L.units", "ul1" in p2.cube.session.plane.units, "unit missing after load")
    check("L.history", isinstance(getattr(p2, "history", None), list), "history missing")
    # Invariant: durable correctness never depends on _last_result restoration.
    try:
        p2.core_ii.store["_last_result"] = {"matched": False}
    except Exception:
        pass
    check("L.invariant", "ul1" in p2.cube.session.plane.units,
          "durable state must not depend on _last_result")
    _cleanup(owner)


# ── M: undo authority control ─────────────────────────────────────────────
def test_m():
    from form.dell_matrix.needs import push_action, undo_last
    from form.mandell.supersession import supersede_proposal
    owner = _owner("m")
    p = _fresh(owner)
    # M1: place-undo delegates to plane.remove and evidences via history.
    p.place("um1", "M One", words="m1")
    push_action(p, {"kind": "place", "id": "um1", "label": "M One"})
    r = undo_last(p)
    check("M1.ok", r.get("ok") is True, f"undo failed: {r}")
    check("M1.via", r.get("via") == "plane.remove", f"undo must delegate: {r}")
    check("M1.gone", "um1" not in p.cube.session.plane.units, "unit not removed")
    hist = " ".join(str(h) for h in (getattr(p, "history", []) or []))
    check("M1.evidence", "undo_place_um1" in hist, "undo left no history evidence")
    # M2: revision-owned unit is refused, never bypassed.
    prop = p.nursery.add("M Rev")
    p.confirm_proposal(prop.id, _producer="test", _review_context=p.make_review_context(prop.id, "test"))
    pid = prop.id
    p.place(pid, "M Rev", words="m rev words")
    p.acceptance_policy.grant_opt_in("test", scope="test")
    sres = supersede_proposal(p, pid, "m rev successor", label="M Rev 2", _producer="test")
    check("M2.supersede", sres.get("ok") is True, f"setup supersede failed: {sres}")
    push_action(p, {"kind": "place", "id": pid, "label": "M Rev"})
    r2 = undo_last(p)
    check("M2.refused", r2.get("ok") is False and r2.get("reason") == "revision_authority",
          f"revision-owned undo must refuse: {r2}")
    check("M2.intact", pid in p.cube.session.plane.units, "revision unit was deleted!")
    # M3: edit-undo restores and evidences.
    p.place("um3", "M Three", words="m3")
    u = p.cube.session.plane.units["um3"]
    push_action(p, {"kind": "edit_detail", "id": "um3", "old": "orig detail"})
    u.detail = "changed detail"
    r3 = undo_last(p)
    check("M3.restored", r3.get("ok") is True and u.detail == "orig detail",
          f"edit undo failed: {r3}")
    hist3 = " ".join(str(h) for h in (getattr(p, "history", []) or []))
    check("M3.evidence", "undo_edit_detail_um3" in hist3, "edit undo left no evidence")
    _cleanup(owner)


# ── N: sidecar authority control ──────────────────────────────────────────
def test_n():
    import form.duobeta.selfgrow as sg
    # N1: selfgrow sidecars are labeled noncanonical.
    src = Path(sg.__file__).read_text(encoding="utf-8")
    check("N.labeled", "NONCANONICAL" in src and "EXPERIMENTAL" in src,
          "selfgrow sidecars must be labeled noncanonical/experimental")
    # N2: no canonical load/restore path reads the selfgrow sidecars.
    canonical_readers = []
    for mod_path in ["form/persist.py", "form/persist_rest.py", "form/open.py",
                     "form/dell_matrix/nursery.py",
                     "form/mandell/checkpoint_generation.py",
                     "form/mandell/core_i_recovery.py"]:
        text = (REPO / mod_path).read_text(encoding="utf-8")
        if "selfgrow_ledger" in text or "selfgrow_state" in text or "LEDGER_PATH" in text:
            canonical_readers.append(mod_path)
    check("N.isolated", not canonical_readers,
          f"canonical paths must not read selfgrow sidecars: {canonical_readers}")
    # N3: only selfgrow itself references its sidecar paths.
    refs = []
    for py in REPO.rglob("form/**/*.py"):
        if "test" in py.name or py.name == "selfgrow.py" or py.name == "grow.py":
            continue
        try:
            t = py.read_text(encoding="utf-8")
        except OSError:
            continue
        if "selfgrow_ledger.json" in t or "selfgrow_state.json" in t:
            refs.append(str(py.relative_to(REPO)))
    check("N.only_selfgrow", not refs, f"unexpected sidecar readers: {refs}")


# ── O: Dell 28 rollback end-to-end ─────────────────────────────────────────
def test_o():
    owner = _owner("o")
    p = _fresh(owner)
    p.place("uo1", "O One", words="o1")
    out27 = execute_seed(p, "27[Checkpoint]")
    check("O.dell27_ok", out27.get("ok") is True, f"dell27 failed: {out27.get('error')}")
    p.place("uo2", "O Two", words="o2")
    # R6.3: Dell 28 without explicit bound approval denies (zero mutation).
    # The positive mediated path is proven in the R6.3 circuit suite.
    out28 = execute_seed(p, "28[Rollback]")
    check("O.dell28_denied", out28.get("ok") is False and
          out28.get("error") == "acceptance_policy_denied",
          f"dell28 should deny without authority: {out28}")
    check("O.restored", out28.get("new_program") is None,
          "denied Dell 28 must not return a program")
    # Live state untouched by the denial.
    check("O.untouched", _units(p) == {"uo1", "uo2"},
          f"denied rollback mutated live state: {_units(p)}")
    # Explicit generation id rollback.
    gid = out27.get("generation_id")
    p2 = _fresh(owner + "b")
    p2.place("uo3", "O Three", words="o3")
    g = cir.checkpoint(p2)
    from form.mandell.core_i_recovery import rollback
    # R6.3: canonical rollback requires mediation (assertions preserved).
    _med = {"operation": "checkpoint.rollback", "owner": p2.owner,
            "generation_id": g}
    rp = rollback(p2.owner, g, _mediation=_med)
    check("O.explicit_gen", _units(rp) == {"uo3"}, f"explicit generation rollback wrong: {_units(rp)}")
    # Missing checkpoint -> honest rollback_missing.
    p3 = _fresh(owner + "c")
    _med3 = {"operation": "checkpoint.rollback", "owner": p3.owner,
             "generation_id": "no_such_generation"}
    try:
        rollback(p3.owner, "no_such_generation", _mediation=_med3)
        check("O.missing", False, "expected FileNotFoundError")
    except FileNotFoundError as exc:
        check("O.missing", "rollback_missing" in str(exc), f"wrong error: {exc}")
    _cleanup(owner)
    _cleanup(owner + "b")
    _cleanup(owner + "c")


def main():
    tests = [test_a, test_b, test_c, test_d, test_e, test_f, test_g,
             test_h, test_i, test_j, test_k, test_l, test_m, test_n, test_o]
    for t in tests:
        try:
            t()
        except Exception as exc:
            check(t.__name__, False, f"EXCEPTION {type(exc).__name__}: {exc}")
    print(f"PAC-I: {PASS} passed, {FAIL} failed")
    print(f"PAC-I: {PASS}/{PASS + FAIL}")
    for f in FAILURES:
        print("FAIL:", f)
    return 1 if FAIL else 0


def smoke() -> bool:
    """Regress entry point: the full PAC-I authority-convergence suite."""
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
