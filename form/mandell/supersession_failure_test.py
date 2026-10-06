"""Supersession actual failure path test (Director 2026-10-05, 2026-10-06).

Tests the REAL compensation path, not denial-before-placement:
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
6. Save assertions: save the unresolved original instance and assert the
   ACTUAL artifact state (detectably unclean, not "did not throw"); then
   complete restoration via production _rollback_full, save, and assert
   the actual artifacts are clean. Restoration must precede a clean save.

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


def run_restart_child(owner, pred_id, succ_id):
    """Fresh-process restart: production recovery + artifact inspection."""
    repo_root = os.path.dirname(REPO)
    child_path = os.path.join("/tmp", f"restart_child_{owner}.py")
    with open(child_path, "w", encoding="utf-8") as f:
        f.write(RESTART_CHILD_SRC)
    proc = subprocess.run(
        [sys.executable, child_path, repo_root, owner, pred_id, succ_id],
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


def run_save_assertions(p, pred, pred_id, succ_id, old_snap):
    """Save the unresolved original instance; assert actual artifacts.

    Restoration must precede a clean save: saving the unresolved instance
    must NOT silently yield clean state. Then complete restoration via
    production _rollback_full and assert the artifacts are actually clean.
    """
    from form import persist_rest
    from form.mandell import supersession as sup
    from form.mandell.supersession import inspect_revision

    # 4a. Exercise saving the UNRESOLVED original instance.
    # In-memory rollback was incomplete: proposal popped, plane.remove
    # threw (unit still present), spatial entries popped.
    # Save exactly as production would (nursery + program).
    try:
        p.nursery.save()
        persist_rest.save(p)
        saved = True
        save_err = None
    except Exception as e:
        saved = False
        save_err = e
    if not saved:
        # The save was rejected: acceptable disjunct ("that save must be
        # rejected"), and it is observable, not silent.
        check("save:unresolved_rejected", True,
              f"save rejected: {type(save_err).__name__}: {save_err}")
    else:
        p3 = persist_rest.load(OWNER, activate=False)
        n3 = succ_id in p3.nursery.proposals
        u3 = succ_id in p3.cube.session.plane.units
        v3 = succ_id in p3.spatial.velocities
        pl3 = succ_id in p3.spatial.placements
        # Actual artifact assertions: the unresolved save is detectably
        # UNCLEAN -- it must not be counted as clean merely for not throwing.
        # The four representations must all agree for a coherent state;
        # here they disagree (partial in-memory rollback was persisted).
        states = [n3, u3, v3, pl3]
        is_clean = not any(states)
        check("save:unresolved_not_clean", is_clean is False,
              f"nursery={n3} units={u3} vel={v3} place={pl3}")
        check("save:unresolved_inconsistent",
              not (all(states) or not any(states)),
              f"nursery={n3} units={u3} vel={v3} place={pl3}: "
              f"representations disagree")

    # 4b. Complete the restoration via production _rollback_full
    # (plane.remove is restored now), then the save must be clean.
    rb = sup._rollback_full(p, pred, old_snap, succ_id)
    check("save:restoration_ok", rb.get("ok") is True,
          f"failures={rb.get('failures')}")
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


def test_actual_failure_path():
    """The real test: authorize, confirm predecessor, start supersession,
    fail at link_write with injected cleanup failure."""
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

    if succ_id is None:
        check("fail:aborted", False,
              "no successor ID captured; artifact assertions impossible")
        return

    # Req 2 (continued): journal retained (production journal path).
    jp = _supersede_journal_path(OWNER)
    if not os.path.isabs(jp):
        jp = os.path.join(REPO, jp)
    check("fail:journal_retained", os.path.isfile(jp),
          f"journal at {jp} exists={os.path.isfile(jp)}")

    # Predecessor integrity: production inspect_revision, exactly active.
    rev = inspect_revision(p, pred_id)
    lifecycle = rev.get("lifecycle_state") if isinstance(rev, dict) else str(rev)
    check("fail:pred_restored_active", lifecycle == "active",
          f"lifecycle={lifecycle}")

    # Req 3: fresh-process restart with production recovery.
    run_restart_child(OWNER, pred_id, succ_id)

    # Req 4: save assertions on the unresolved original instance.
    run_save_assertions(p, pred, pred_id, succ_id, old_snap)


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


def smoke():
    print("=== SUPERSESSION FAILURE PATH ===")
    try:
        test_actual_failure_path()
    except Exception as e:
        import traceback
        check("test_actual_failure_path", False,
              f"EXC {type(e).__name__}: {e}\n{traceback.format_exc()[:600]}")
    try:
        test_spatial_verification_sensitivity()
    except Exception as e:
        import traceback
        check("test_spatial_verification_sensitivity", False,
              f"EXC {type(e).__name__}: {e}\n{traceback.format_exc()[:600]}")
    n = sum(CHECKS)
    print(f"=== {n}/{len(CHECKS)} ===")
    return n == len(CHECKS)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
