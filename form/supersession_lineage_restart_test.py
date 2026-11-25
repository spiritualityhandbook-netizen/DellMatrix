#!/usr/bin/env python3
"""72-33 — Supersession acceptance lineage across
restart (evidence circuit).

Register: "Verify supersession crash + acceptance
lineage across restart (P1/E) (= SM-30)." Remaining
action: "Present suite evidence for ruling, or extend
lineage assertions."

form/mandell/supersession_failure_test.py already
proves the hard failure paths: an interrupted
supersession with an INCOMPLETE rollback, fresh-process
recovery, unsafe-save closure, and checkpoint-path
closure (Scenarios A/B/C). What it does not prove is
the LINEAGE contract this row names:

- A multi-link acceptance chain (A confirmed, B
  supersedes A, C supersedes B) carries exact lineage
  in-process: per-link supersedes / superseded_by,
  one shared revision root, increasing revision
  numbers, and the full ordered chain readable from
  every link.
- The ENTIRE lineage — links, lifecycle states,
  revision numbers, chain, and each link's ACCEPTED
  (confirmed) status — survives a restart byte-for-
  byte: a fresh OS process loading the owner through
  the production path reports identical inspections,
  with exactly the tip active and no recovery pending.
- A crash on the SECOND link of a chain (injected at
  the documented "confirm" window) rolls back
  completely: no successor proposal exists, the
  predecessor stays active with its lineage untouched,
  and a fresh-process restart confirms the identical
  coherent state.

All operations run through the production public path
(supersede_proposal / confirm_proposal /
inspect_revision / recover_supersede_intent).

Labels: INTEGRATION in-process; CROSS_PROCESS for the
restart legs (fresh OS process via subprocess).
Hygiene: uuid-unique owners; exact-pattern cleanup;
cleanup failures reported, never swallowed.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import uuid
from pathlib import Path

REPO = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, REPO)

RESULTS = []
_CLEANUP_ERRORS = []
RUN = uuid.uuid4().hex[:8]

CHILD_SRC = r'''
import json, sys
sys.path.insert(0, sys.argv[1])
owner = sys.argv[2]
ids = sys.argv[3].split(",")
from form.open import open_program
from form.mandell.supersession import inspect_revision, is_revision_active
from form.mandell.core_i_recovery import recover_supersede_intent
rec = recover_supersede_intent(owner)
p = open_program(owner)
out = {"recovery": rec, "proposals": sorted(p.nursery.proposals.keys()),
       "units": {}}
for uid in ids:
    ins = inspect_revision(p, uid)
    prop = p.nursery.proposals.get(uid)
    out["units"][uid] = {
        "lifecycle": ins.get("lifecycle_state"),
        "supersedes": ins.get("supersedes_id"),
        "superseded_by": ins.get("superseded_by_id"),
        "root": ins.get("revision_root_id"),
        "number": ins.get("revision_number"),
        "chain": ins.get("chain"),
        "active": is_revision_active(p, uid),
        "status": getattr(prop, "status", None),
    }
print(json.dumps(out))
'''


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def _setup(owner):
    from form.open import open_program
    p = open_program(owner)
    try:
        p.acceptance_policy.grant_opt_in(owner, scope="test")
    except AttributeError:
        pass
    return p


def _add_confirm(p, owner, name, words):
    prop = p.nursery.add(name, words=words)
    ctx = p.make_review_context(prop.id, owner)
    r = p.confirm_proposal(prop.id, _producer=owner,
                           _review_context=ctx)
    assert r.get("ok"), r
    return prop.id


def _child(owner, ids):
    path = f"/tmp/7233_child_{RUN}_{owner[-4:]}.py"
    with open(path, "w", encoding="utf-8") as f:
        f.write(CHILD_SRC)
    proc = subprocess.run(
        [sys.executable, path, REPO, owner, ",".join(ids)],
        capture_output=True, text=True, timeout=120, cwd=REPO)
    if proc.returncode != 0:
        return None, proc.stderr[-300:]
    try:
        return json.loads(proc.stdout.strip().split("\n")[-1]), ""
    except Exception as exc:
        return None, f"parse: {exc}"


def _lineage(p, ids):
    from form.mandell.supersession import inspect_revision
    out = {}
    for uid in ids:
        ins = inspect_revision(p, uid)
        out[uid] = {"lifecycle": ins["lifecycle_state"],
                    "supersedes": ins["supersedes_id"],
                    "superseded_by": ins["superseded_by_id"],
                    "root": ins["revision_root_id"],
                    "number": ins["revision_number"],
                    "chain": ins["chain"]}
    return out


def _cleanup(owner):
    from form.persist import _STATE_DIR, _safe_owner
    from form.dell_matrix.nursery import owner_nursery_path
    state = Path(_STATE_DIR)
    safe = _safe_owner(owner)
    cands = [state / f"program_{safe}.json",
             Path(owner_nursery_path(owner))]
    cands += list(state.glob(f"*{safe}*"))
    for pth in set(cands):
        try:
            if pth.is_dir():
                import shutil
                shutil.rmtree(pth)
            elif pth.exists():
                pth.unlink()
        except OSError as exc:
            _CLEANUP_ERRORS.append(f"{pth}: {exc}")


OWNERS = []


def main():
    from form.mandell import supersession as sup

    # -- A/B: happy 3-link chain + restart --------------------------------
    owner = f"T7233A{RUN}"; OWNERS.append(owner)
    p = _setup(owner)
    a = _add_confirm(p, owner, "Alpha", "first")
    r1 = sup.supersede_proposal(p, a, words="second", _producer=owner)
    b = r1.get("new_id")
    r2 = sup.supersede_proposal(p, b, words="third", _producer=owner)
    c = r2.get("new_id")
    check("A1.chain_builds_two_supersessions",
          r1.get("ok") is True and r2.get("ok") is True and b and c,
          f"r1={r1.get('ok')} r2={r2.get('ok')} b={b} c={c}")
    ids = [a, b, c]
    lin = _lineage(p, ids)
    check("A2.inprocess_lineage_exact",
          lin[a] == {"lifecycle": "superseded", "supersedes": None,
                     "superseded_by": b, "root": a, "number": 1,
                     "chain": ids}
          and lin[b] == {"lifecycle": "superseded", "supersedes": a,
                         "superseded_by": c, "root": a, "number": 2,
                         "chain": ids}
          and lin[c] == {"lifecycle": "active", "supersedes": b,
                         "superseded_by": None, "root": a, "number": 3,
                         "chain": ids},
          f"{lin}")
    out, err = _child(owner, ids)
    check("B1.restart_child_runs", out is not None, err)
    if out is not None:
        same = all(
            {k: out["units"][u][k] for k in
             ("lifecycle", "supersedes", "superseded_by", "root",
              "number", "chain")} == lin[u]
            for u in ids)
        check("B2.lineage_identical_across_restart", same,
              f"child={out['units']}")
        check("B3.acceptance_survives_tip_only_active",
              all(out["units"][u]["status"] == "confirmed" for u in ids)
              and out["units"][c]["active"] is True
              and out["units"][a]["active"] is False
              and out["units"][b]["active"] is False,
              f"{[(u, out['units'][u]['status'], out['units'][u]['active']) for u in ids]}")
        check("B4.no_recovery_pending_on_clean_chain",
              out["recovery"] == "none", f"recovery={out['recovery']!r}")

    # -- C: crash on the second link ---------------------------------------
    owner = f"T7233B{RUN}"; OWNERS.append(owner)
    p = _setup(owner)
    d = _add_confirm(p, owner, "Delta", "d1")
    r = sup.supersede_proposal(p, d, words="d2", _producer=owner)
    e = r.get("new_id")
    before = sorted(p.nursery.proposals.keys())
    raised = None
    try:
        sup.supersede_proposal(p, e, words="d3", _producer=owner,
                               _fail_at="confirm")
    except sup.SupersedeError as exc:
        raised = exc
    check("C1.crash_at_confirm_raises",
          raised is not None
          and getattr(raised, "reason", "") == "injected_failure",
          f"raised={raised!r}")
    lin = _lineage(p, [d, e])
    check("C2.rollback_complete_lineage_untouched",
          sorted(p.nursery.proposals.keys()) == before
          and lin[e]["lifecycle"] == "active"
          and lin[e]["superseded_by"] is None
          and lin[e]["chain"] == [d, e]
          and lin[d]["superseded_by"] == e,
          f"lin={lin} props={sorted(p.nursery.proposals.keys())}")
    out, err = _child(owner, [d, e])
    check("C3.restart_after_crash_child_runs", out is not None, err)
    if out is not None:
        check("C4.restart_confirms_coherent_lineage",
              out["proposals"] == before
              and out["units"][e]["lifecycle"] == "active"
              and out["units"][e]["active"] is True
              and out["units"][e]["chain"] == [d, e]
              and out["units"][d]["lifecycle"] == "superseded",
              f"child={out}")

    for o in OWNERS:
        _cleanup(o)
    check("cleanup.no_errors", not _CLEANUP_ERRORS, str(_CLEANUP_ERRORS))

    total = len(RESULTS)
    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"supersession_lineage_restart_test: {passed}/{total} PASS")
    return 0 if passed == total else 1


def smoke():
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
