"""Supersession actual failure path test (Director 2026-10-05, 2026-10-06).

Tests the REAL compensation path, not denial-before-placement.

Scenario A -- restart proof (fresh OS process):
1. Valid authorization, confirmed predecessor
2. Begin supersession (successor placed via the production confirm path)
3. Inject link_write failure; production _rollback_full runs with an
   injected plane.remove failure -> incomplete rollback
4. Assert from production evidence only:
   - successor ID captured from the successful tracking_place call
   - exception details carry rollback == "incomplete" with named failures
     (no injected_failure escape hatch)
   - supersession journal retained
   - predecessor restored to active
5. Restart child (fresh OS process): production recover_supersede_intent
   plus inspection of the exact successor in Nursery, Plane, velocities,
   placements and lattice (via production all_members). Assert the
   documented coherent recovery outcome ("already_complete") -- or
   explicit fail-closed behavior (RollbackRecoveryError + journal retained).

Scenario B -- unsafe-save closure (Director 2026-10-06):
Detecting an unsafe save does not prevent it. An instance with incomplete
rollback must REJECT normal saves until verified restoration or
reconstruction:
6. Rejected saves: persist_rest.save and nursery.save raise
   RollbackRecoveryError on the unresolved instance.
7. Durable member bytes unchanged by the rejected saves.
8. Recovery evidence (journal) preserved across the rejected saves.
9. Another instance reloading the owner (which runs disk recovery and
   clears the disk journal) does NOT clear this instance's in-memory
   recovery-required condition: its saves stay rejected.
10. Verified restoration via production _rollback_full, then save/reload
    produces coherent state (successor absent everywhere, predecessor
    active). Restoration precedes the clean save.

"A denial before placement cannot prove compensation."

Evidence class: INTEGRATION (real Program, real files) + CROSS_PROCESS
(fresh-process restart child via subprocess).
"""

import glob
import json
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(REPO))

from form.open import open_program

OWNER = "SUP_FAIL_PATH"
CHECKS = []


def check(name, cond, detail=""):
    CHECKS.append(bool(cond))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f" | {detail}" if detail and not cond else ""))


def clean():
    for pat in [f'form/state/nursery_{OWNER}.json', f'form/state/program_{OWNER}.json']:
        pp = os.path.join(REPO, pat)
        if os.path.isfile(pp):
            os.remove(pp)
    for pp in glob.glob(os.path.join(REPO, 'form', 'state', f'checkpoint_{OWNER}_*')):
        os.remove(pp)
    # Remove any stale supersession journal from a previous run.
    from form.mandell.core_i_recovery import _supersede_journal_path
    jp = _supersede_journal_path(OWNER)
    if not os.path.isabs(jp):
        jp = os.path.join(REPO, jp)
    if os.path.isfile(jp):
        os.remove(jp)


def run_failure_scenario():
    """Clean slate, authorized supersession, link_write failure with
    injected throwing plane.remove during production _rollback_full.

    Returns (p, pred, pred_id, succ_id, old_snap, journal_path), or
    (None, ...) with a failed check if the scenario is invalid.
    """
    clean()
    from form.mandell import supersession as sup
    from form.mandell.supersession import ACTIVE, inspect_revision
    from form.mandell.core_i_recovery import _supersede_journal_path

    p = open_program(OWNER)
    try:
        p.acceptance_policy.grant_opt_in(OWNER, scope="test")
    except AttributeError:
        pass

    # Create and confirm predecessor with valid auth.
    pred = p.nursery.add("Pred", words="predecessor content")
    ctx = p.make_review_context(pred.id, OWNER)
    r = p.confirm_proposal(pred.id, _producer=OWNER, _review_context=ctx)
    check("setup:pred_confirmed", r.get("ok") and pred.status == "confirmed",
          f"ok={r.get('ok')} status={pred.status}")
    pred_id = pred.id

    # Snapshot exactly as production _rollback_full expects (for the
    # later restoration-retry step).
    old_snap = {
        "lifecycle_state": getattr(pred, "lifecycle_state", ACTIVE),
        "supersedes_id": getattr(pred, "supersedes_id", None),
        "superseded_by_id": getattr(pred, "superseded_by_id", None),
        "revision_root_id": getattr(pred, "revision_root_id", None),
        "revision_number": getattr(pred, "revision_number", None),
    }

    # Capture the successor ID from the successful tracking_place call.
    # (p.place is invoked by the production confirm path for the successor.)
    placed_ids = []
    orig_place = p.place

    def tracking_place(*a, **kw):
        placed_ids.append(a[0])
        return orig_place(*a, **kw)

    p.place = tracking_place

    # Inject cleanup failure: plane.remove throws during rollback.
    orig_remove = p.cube.session.plane.remove

    def failing_remove(sid):
        raise RuntimeError("injected_rollback_failure")

    p.cube.session.plane.remove = failing_remove

    succ_id = None
    try:
        sup.supersede_proposal(
            p, pred_id, words="successor content",
            _producer=OWNER,
            _fail_at="link_write",  # fail at link commit, after successor placed
        )
        check("fail:raised", False, "expected SupersedeError, none raised")
    except sup.SupersedeError as e:
        check("fail:raised", True, f"reason={e.reason}")
        # Req 1: successor ID from the successful tracking_place call.
        placed_new = [i for i in placed_ids if i != pred_id]
        check("fail:succ_id_captured", len(placed_new) == 1,
              f"placed_ids={placed_ids}")
        succ_id = placed_new[0] if placed_new else None
        # Req 2: actual rollback == "incomplete" details with named
        # failures. No injected_failure escape hatch.
        details = getattr(e, "details", {}) or {}
        check("fail:rollback_incomplete",
              details.get("rollback") == "incomplete",
              f"details={details}")
        check("fail:rollback_failures_named",
              isinstance(details.get("rollback_failures"), list)
              and len(details["rollback_failures"]) > 0,
              f"details={details}")
    except Exception as e:
        check("fail:raised_supersede", False,
              f"wrong exception: {type(e).__name__}: {e}")
    finally:
        p.place = orig_place
        p.cube.session.plane.remove = orig_remove

    jp = _supersede_journal_path(OWNER)
    if not os.path.isabs(jp):
        jp = os.path.join(REPO, jp)

    if succ_id is None:
        check("fail:aborted", False,
              "no successor ID captured; artifact assertions impossible")
        return None, None, None, None, None, jp

    # Journal retained (production journal path).
    check("fail:journal_retained", os.path.isfile(jp),
          f"journal at {jp} exists={os.path.isfile(jp)}")

    # Predecessor integrity: production inspect_revision, exactly active.
    rev = inspect_revision(p, pred_id)
    lifecycle = rev.get("lifecycle_state") if isinstance(rev, dict) else str(rev)
    check("fail:pred_restored_active", lifecycle == "active",
          f"lifecycle={lifecycle}")

    # The instance must be marked recovery-required (incomplete rollback).
    check("fail:marked_recovery_required",
          getattr(p, "_recovery_required", None) is not None,
          "instance must require recovery after incomplete rollback")

    return p, pred, pred_id, succ_id, old_snap, jp


RESTART_CHILD_SRC = '''
import sys, json, os
REPO_ROOT, OWNER, PRED_ID, SUCC_ID = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
sys.path.insert(0, REPO_ROOT)
os.chdir(REPO_ROOT)
out = {}
from form.mandell.core_i_recovery import (
    _supersede_journal_path, recover_supersede_intent, RollbackRecoveryError)
jp = _supersede_journal_path(OWNER)
# 1. Journal evidence linkage (production journal path + schema).
try:
    with open(jp, encoding="utf-8") as f:
        journal = json.load(f)
    out["journal_old_id"] = journal.get("old_id")
    out["journal_new_id"] = journal.get("new_id")
    out["journal_link_ok"] = (journal.get("old_id") == PRED_ID
                              and journal.get("new_id") == SUCC_ID)
except Exception as e:
    out["journal_link_ok"] = False
    out["journal_error"] = f"{type(e).__name__}: {e}"
# 2. Production recovery: documented outcome or explicit fail-closed.
try:
    outcome = recover_supersede_intent(OWNER)
    out["recovery"] = {"outcome": outcome, "fail_closed": False,
                       "journal_retained": os.path.isfile(jp)}
except RollbackRecoveryError as e:
    out["recovery"] = {"outcome": None, "fail_closed": True,
                       "journal_retained": os.path.isfile(jp),
                       "error": str(e)[:300]}
except Exception as e:
    out["recovery"] = {"outcome": None, "fail_closed": "unexpected",
                       "journal_retained": os.path.isfile(jp),
                       "error": f"{type(e).__name__}: {e}"}
# 3. Inspect the exact successor in every representation (production load).
from form import persist_rest
p2 = persist_rest.load(OWNER, activate=False)
out["succ_in_nursery"] = SUCC_ID in p2.nursery.proposals
out["succ_nursery_status"] = getattr(p2.nursery.proposals.get(SUCC_ID), "status", None)
out["succ_in_units"] = SUCC_ID in p2.cube.session.plane.units
out["succ_in_velocities"] = SUCC_ID in p2.spatial.velocities
out["succ_in_placements"] = SUCC_ID in p2.spatial.placements
try:
    p2.lattice.rebuild_from_plane(p2.cube.session.plane)
    out["succ_in_lattice"] = SUCC_ID in p2.lattice.all_members()
except Exception as e:
    out["succ_in_lattice"] = f"ERROR {type(e).__name__}: {e}"
from form.mandell.supersession import inspect_revision
rev = inspect_revision(p2, PRED_ID)
out["pred_lifecycle"] = rev.get("lifecycle_state") if isinstance(rev, dict) else str(rev)
print(json.dumps(out))
'''


def test_restart_proof():
    """Scenario A: fresh-process restart with production recovery."""
    p, pred, pred_id, succ_id, old_snap, jp = run_failure_scenario()
    if succ_id is None:
        return
    repo_root = os.path.dirname(REPO)
    child_path = os.path.join("/tmp", f"restart_child_{OWNER}.py")
    with open(child_path, "w", encoding="utf-8") as f:
        f.write(RESTART_CHILD_SRC)
    proc = subprocess.run(
        [sys.executable, child_path, repo_root, OWNER, pred_id, succ_id],
        capture_output=True, text=True, timeout=120, cwd=repo_root)
    if proc.returncode != 0:
        check("restart:child_ok", False, f"child failed: {proc.stderr[:300]}")
        return
    try:
        out = json.loads(proc.stdout.strip().split("\n")[-1])
    except Exception as e:
        check("restart:child_parse", False, f"parse: {e}; stdout={proc.stdout[:300]}")
        return

    # Journal evidence linkage: the journal names this exact pair.
    check("restart:journal_link", out.get("journal_link_ok") is True,
          f"old={out.get('journal_old_id')} new={out.get('journal_new_id')}")

    rec = out.get("recovery", {})
    if rec.get("fail_closed") is True:
        # Explicit fail-closed: recovery refused and retained evidence.
        check("restart:fail_closed_journal_retained",
              rec.get("journal_retained") is True,
              f"error={rec.get('error')}")
    elif rec.get("fail_closed") == "unexpected":
        check("restart:recovery_no_unexpected", False, f"error={rec.get('error')}")
    else:
        # Documented coherent recovery outcome for the valid pre-commit
        # state (predecessor active, successor confirmed, no links):
        # "already_complete" -- accepted as-is, journal cleared.
        check("restart:recovery_outcome",
              rec.get("outcome") == "already_complete",
              f"outcome={rec.get('outcome')}")
        check("restart:journal_cleared_after_coherent",
              rec.get("journal_retained") is False,
              "journal must be cleared once recovery proves coherence")

    # The exact successor inspected in every representation.
    check("restart:succ_nursery",
          out.get("succ_in_nursery") is True
          and out.get("succ_nursery_status") == "confirmed",
          f"in_nursery={out.get('succ_in_nursery')} status={out.get('succ_nursery_status')}")
    check("restart:succ_plane", out.get("succ_in_units") is True,
          f"in_units={out.get('succ_in_units')}")
    check("restart:succ_velocities", out.get("succ_in_velocities") is True,
          f"in_velocities={out.get('succ_in_velocities')}")
    check("restart:succ_placements", out.get("succ_in_placements") is True,
          f"in_placements={out.get('succ_in_placements')}")
    check("restart:succ_lattice", out.get("succ_in_lattice") is True,
          f"in_lattice={out.get('succ_in_lattice')}")
    check("restart:pred_active", out.get("pred_lifecycle") == "active",
          f"lifecycle={out.get('pred_lifecycle')}")


def test_save_proof():
    """Scenario B: the unsafe save is closed (Director 2026-10-06).

    The unresolved instance must REJECT normal saves; durable bytes and
    recovery evidence must be unchanged; another instance's disk recovery
    must not clear this instance's condition; verified restoration then
    permits a clean save.
    """
    p, pred, pred_id, succ_id, old_snap, jp = run_failure_scenario()
    if succ_id is None:
        return
    from form import persist_rest
    from form.mandell import supersession as sup
    from form.mandell.supersession import inspect_revision
    from form.mandell.core_i_recovery import RollbackRecoveryError
    from form.persist import _path as _program_path
    from form.dell_matrix.nursery import owner_nursery_path

    prog_path = _program_path(OWNER)
    nurs_path = owner_nursery_path(OWNER)
    with open(prog_path, "rb") as f:
        prog_before = f.read()
    with open(nurs_path, "rb") as f:
        nurs_before = f.read()

    # 1. The unresolved save is REJECTED (both member files).
    rej_nursery = rej_prog = False
    try:
        p.nursery.save()
    except RollbackRecoveryError:
        rej_nursery = True
    try:
        persist_rest.save(p)
    except RollbackRecoveryError:
        rej_prog = True
    check("save:unresolved_rejected", rej_nursery and rej_prog,
          f"nursery_rejected={rej_nursery} program_rejected={rej_prog}")

    # 2. Durable member bytes unchanged by the rejected saves.
    with open(prog_path, "rb") as f:
        prog_after = f.read()
    with open(nurs_path, "rb") as f:
        nurs_after = f.read()
    check("save:bytes_unchanged",
          prog_before == prog_after and nurs_before == nurs_after,
          "durable bytes must be unchanged by rejected saves")

    # 3. Recovery evidence preserved across the rejected saves.
    check("save:evidence_preserved", os.path.isfile(jp),
          f"journal at {jp} must survive rejected saves")
    check("save:flag_preserved",
          getattr(p, "_recovery_required", None) is not None,
          "in-memory recovery-required must survive rejected saves")

    # 4. Another instance reloading the owner runs disk recovery (clearing
    # the disk journal) -- this instance's in-memory condition survives.
    # (persist_rest.load runs the existing recovery mechanism.)
    p2 = persist_rest.load(OWNER, activate=False)
    check("save:disk_journal_cleared_by_other",
          not os.path.isfile(jp),
          "other instance's load runs disk recovery")
    still_rejected = False
    try:
        persist_rest.save(p)
    except RollbackRecoveryError:
        still_rejected = True
    check("save:flag_survives_disk_recovery",
          still_rejected and getattr(p, "_recovery_required", None) is not None,
          "disk recovery must not repair this instance's memory")

    # 5. Verified restoration, then save/reload produces coherent state.
    rb = sup._rollback_full(p, pred, old_snap, succ_id)
    check("save:restoration_ok", rb.get("ok") is True,
          f"failures={rb.get('failures')}")
    check("save:flag_cleared_by_verified_restoration",
          getattr(p, "_recovery_required", None) is None,
          "verified restoration clears the condition")
    # _rollback_full saves nursery + program itself on success.
    p4 = persist_rest.load(OWNER, activate=False)
    n4 = succ_id in p4.nursery.proposals
    u4 = succ_id in p4.cube.session.plane.units
    v4 = succ_id in p4.spatial.velocities
    pl4 = succ_id in p4.spatial.placements
    check("save:clean_after_restoration", not (n4 or u4 or v4 or pl4),
          f"nursery={n4} units={u4} vel={v4} place={pl4}")
    rev4 = inspect_revision(p4, pred_id)
    lc4 = rev4.get("lifecycle_state") if isinstance(rev4, dict) else str(rev4)
    check("save:pred_active_after_restoration", lc4 == "active",
          f"lifecycle={lc4}")


def test_spatial_verification_sensitivity():
    """Sensitivity: _verify_successor_absent must check spatial entries.

    Director 2026-10-05: _rollback_full returned ok=True when spatial
    removal silently did nothing. This test calls the production check;
    if spatial checks are removed from _verify_successor_absent,
    sens:velocities_detected and sens:placements_detected MUST fail.
    """
    from form.mandell.supersession import _verify_successor_absent
    p = open_program("SENS_SPATIAL")
    succ_id = "sens_succ_001"
    # Place spatial entries (simulating a successor that was placed).
    p.spatial.velocities[succ_id] = [1.0, 2.0]
    p.spatial.placements[succ_id] = {"pos": [0, 0]}
    # Do NOT remove them (simulating silent noop).
    failures = _verify_successor_absent(p, succ_id)
    has_vel = any("velocities_still_present" in f for f in failures)
    has_place = any("placements_still_present" in f for f in failures)
    check("sens:velocities_detected", has_vel, f"failures={failures}")
    check("sens:placements_detected", has_place, f"failures={failures}")
    # Cleanup.
    p.spatial.velocities.pop(succ_id, None)
    p.spatial.placements.pop(succ_id, None)
    failures2 = _verify_successor_absent(p, succ_id)
    check("sens:clean_passes", len(failures2) == 0, f"failures={failures2}")


def test_save_guard_sensitivity():
    """Sensitivity: removing the save guard must fail the save proof.

    Calls the production check_save_allowed directly: with the guard
    present, a flagged instance is rejected; this documents the exact
    production check the save proof depends on.
    """
    from form.mandell.core_i_recovery import (
        check_save_allowed, mark_recovery_required, clear_recovery_required,
        RollbackRecoveryError)
    p = open_program("SENS_GUARD")
    # Unflagged: allowed (no exception).
    try:
        check_save_allowed(p, "probe")
        unflagged_ok = True
    except RollbackRecoveryError:
        unflagged_ok = False
    check("sens:unflagged_allowed", unflagged_ok, "unflagged save must pass guard")
    # Flagged: rejected.
    mark_recovery_required(p, "probe_id", "probe_reason", {"x": 1})
    try:
        check_save_allowed(p, "probe")
        flagged_rejected = False
    except RollbackRecoveryError:
        flagged_rejected = True
    check("sens:flagged_rejected", flagged_rejected, "flagged save must be rejected")
    # Cleared: allowed again.
    clear_recovery_required(p, "probe_id")
    try:
        check_save_allowed(p, "probe")
        cleared_ok = True
    except RollbackRecoveryError:
        cleared_ok = False
    check("sens:cleared_allowed", cleared_ok, "cleared save must pass guard")


def smoke():
    print("=== SUPERSESSION FAILURE PATH ===")
    for fn in [test_restart_proof, test_save_proof,
               test_spatial_verification_sensitivity,
               test_save_guard_sensitivity]:
        try:
            fn()
        except Exception as e:
            import traceback
            check(fn.__name__, False,
                  f"EXC {type(e).__name__}: {e}\n{traceback.format_exc()[:600]}")
    n = sum(CHECKS)
    print(f"=== {n}/{len(CHECKS)} ===")
    return n == len(CHECKS)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
