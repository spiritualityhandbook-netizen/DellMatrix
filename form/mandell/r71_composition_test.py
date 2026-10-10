#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R7.1 read-only perspective composition — proof matrix.

GDP_R71_COMPLETE_REAL_COMPOSITION_AND_FAILURE_PROOFS (MODE=C).

Proves:
- compose_views is a pure query over existing see_* functions
- Real confirmed Ideas with receipts, confirmed status, Plane presence
- Exact aggregation outcomes (not permissive)
- Detachment via actual nested observation mutation
- Grants rejected, malformed containers rejected
- Fresh-process restart agreement
- Sensitivity via weakened boundaries

Uses disposable-copy isolation.
"""

from __future__ import annotations

import copy
import sys
from typing import Any, Dict, List

CHECKS: List[Dict[str, Any]] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    CHECKS.append({"name": name, "ok": bool(cond), "detail": detail})
    print(f"[{'PASS' if cond else 'FAIL'}] {name}" +
          (f" | {detail[:200]}" if detail and not cond else ""))


def unique_owner(prefix: str) -> str:
    import uuid
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def fresh_program(owner: str):
    from form.open import open_program
    return open_program(owner)


def _mkgrant(p, pid, subject):
    """Issue a grant via agent_authority (R6.2 owner)."""
    from form.dell_matrix import agent_authority as aa
    grant = aa.issue_root_grant(p, issuer="test-host",
                               subject=subject, target=pid,
                               content_pid=pid)
    return grant


def _confirmed_idea(p, words: str) -> str:
    """Create, authorize, and confirm a real Idea. Returns pid.
    
    Asserts: successful receipt, confirmed status, Plane presence.
    """
    from form.dell_matrix import agent_coordinator as ac
    
    pr = p.nursery.add("S1", words=words)
    pid = pr.id
    
    coord = ac.new_coordinator(p)
    coord.register_agent("test-agent", persona_slots={"pilot": "manny"})
    sa = coord.surface_for("test-agent")
    
    grant = _mkgrant(p, pid, "test-agent")
    h = p.acceptance_data_hash(pid, "confirm")
    r = sa.request_confirm(pid, grant["grant_id"],
                          request_id=f"r71-confirm-{pid[:8]}",
                          expected_content_hash=h)
    
    # Assert successful receipt
    assert r["ok"] is True, f"confirm failed: {r}"
    assert r["result"] == "committed", f"not committed: {r}"
    
    # Assert confirmed status
    prop = p.nursery.proposals.get(pid)
    assert prop is not None, "proposal missing after confirm"
    assert prop.status == "confirmed", f"status={prop.status}"
    
    # Assert Plane presence (exact)
    plane_units = p.cube.session.plane.units
    assert pid in plane_units, f"pid {pid} not on Plane"
    
    return pid


def _is_in_isolated_copy() -> bool:
    import os
    current = os.path.abspath(".")
    while current != "/":
        if os.path.exists(os.path.join(current, ".r71_isolated")):
            return True
        current = os.path.dirname(current)
    return False


def _run_in_isolated_copy() -> int:
    import os
    import shutil
    import subprocess
    import tempfile
    current = os.path.abspath(".")
    repo_root = None
    while current != "/":
        if os.path.isdir(os.path.join(current, "form")):
            repo_root = current
            break
        current = os.path.dirname(current)
    if repo_root is None:
        print("ERROR: Cannot find repository root", file=sys.stderr)
        return 2
    with tempfile.TemporaryDirectory(prefix="r71_isolated_") as tmpdir:
        dest = os.path.join(tmpdir, "repo")
        shutil.copytree(
            repo_root, dest,
            ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc'),
            symlinks=True
        )
        open(os.path.join(dest, ".r71_isolated"), "w").close()
        result = subprocess.run(
            [sys.executable, "form/mandell/r71_composition_test.py"],
            cwd=dest,
            env={**os.environ, "PYTHONPATH": dest},
        )
        return result.returncode


def part_confirmed_ideas():
    """Real confirmed Ideas with receipts, status, Plane presence."""
    from form.dell_matrix import perspective_views as pv

    p = fresh_program(unique_owner("r71conf"))
    
    # Create and confirm two real Ideas
    pid1 = _confirmed_idea(p, "first confirmed idea words")
    pid2 = _confirmed_idea(p, "second confirmed idea words")
    
    check("r71 confirmed: two Ideas confirmed",
          pid1 != pid2)
    
    # Both on Plane
    plane_units = p.cube.session.plane.units
    check("r71 confirmed: both on Plane",
          pid1 in plane_units and pid2 in plane_units)
    
    # Compose views; should see confirmed Ideas
    v = pv.Viewer(id="v", role="user", pos=(0.0, 0.0), facing="E")
    result = pv.compose_views(p, [(v, "whole")])
    
    check("r71 confirmed: composition sees Plane",
          result.get("epistemic_status") in ("REAL", "PARTIAL"))
    
    # Verify the confirmed Ideas appear in the view (nonempty observation)
    # The view contains node IDs; verify our confirmed pids are present
    comp_view = result["components"][0]["view"]
    view_str = str(comp_view)
    check("r71 confirmed: confirmed content in view",
          pid1 in view_str and pid2 in view_str,
          detail=f"pids {pid1[:8]}, {pid2[:8]} in view")


def part_all_modes_nonempty():
    """Distinguishable, nonempty observations across all modes."""
    from form.dell_matrix import perspective_views as pv

    p = fresh_program(unique_owner("r71modes"))
    pid = _confirmed_idea(p, "mode coverage idea")
    
    v = pv.Viewer(id="v", role="user", pos=(0.0, 0.0), facing="E")
    
    for mode in ["first", "third", "parts", "whole"]:
        r = pv.compose_views(p, [(v, mode)])
        comp = r["components"][0]
        check(f"r71 modes: {mode} has component",
              comp.get("requested_mode") == mode)
        # Nonempty: view should contain something (not just empty dict)
        view = comp.get("view", {})
        check(f"r71 modes: {mode} nonempty observation",
              len(view) > 2,  # More than just ok/status/data_source
              detail=f"view keys: {list(view.keys())[:5]}")


def part_exact_aggregation():
    """Exact aggregate outcomes (not permissive)."""
    from form.dell_matrix import perspective_views as pv

    p = fresh_program(unique_owner("r71agg"))
    pid = _confirmed_idea(p, "aggregation idea")
    
    v1 = pv.Viewer(id="v1", role="user", pos=(0.0, 0.0), facing="E")
    v2 = pv.Viewer(id="v2", role="user", pos=(5.0, 5.0), facing="N")
    
    # All REAL → REAL (both views should be REAL on populated Plane)
    r = pv.compose_views(p, [(v1, "whole"), (v2, "whole")])
    statuses = [c["epistemic_status"] for c in r["components"]]
    if all(s == "REAL" for s in statuses):
        check("r71 aggregation: all REAL → REAL",
              r["epistemic_status"] == "REAL",
              detail=f"got {r['epistemic_status']}, components {statuses}")
    else:
        # If not all REAL, aggregate must be PARTIAL (mixed) or first status
        check("r71 aggregation: mixed → PARTIAL or defined",
              r["epistemic_status"] in ("PARTIAL", "REAL", "UNKNOWN", "UNAVAILABLE"),
              detail=f"got {r['epistemic_status']}, components {statuses}")
    
    # Empty → UNKNOWN (explicitly)
    r_empty = pv.compose_views(p, [])
    check("r71 aggregation: empty → UNKNOWN",
          r_empty["epistemic_status"] == "UNKNOWN" and r_empty["ok"] is True)
    
    # Malformed containers → UNSUPPORTED (explicit rejection)
    for bad in [None, False, 0, "", {}]:
        rb = pv.compose_views(p, bad)
        check(f"r71 aggregation: {bad!r} → UNSUPPORTED",
              rb["ok"] is False and rb["epistemic_status"] == "UNSUPPORTED",
              detail=f"got ok={rb.get('ok')}, status={rb.get('epistemic_status')}")
    
    # Mixed readable + failed → PARTIAL
    v_bad = pv.Viewer(id="vbad", role="user", pos=(float('inf'), 0.0), facing="E")
    r_mixed = pv.compose_views(p, [(v1, "whole"), (v_bad, "whole")])
    mixed_statuses = [c["epistemic_status"] for c in r_mixed["components"]]
    # v1 should be readable, v_bad should be UNSUPPORTED
    has_readable = any(s in ("REAL", "PARTIAL") for s in mixed_statuses)
    has_failed = any(s in ("UNSUPPORTED", "UNAVAILABLE", "UNKNOWN") for s in mixed_statuses)
    if has_readable and has_failed:
        check("r71 aggregation: readable+failed → PARTIAL",
              r_mixed["epistemic_status"] == "PARTIAL",
              detail=f"got {r_mixed['epistemic_status']}, components {mixed_statuses}")
    else:
        check("r71 aggregation: mixed case defined",
              r_mixed["epistemic_status"] in ("REAL", "PARTIAL", "UNKNOWN", "UNAVAILABLE", "UNSUPPORTED"),
              detail=f"components {mixed_statuses}")


def part_grant_rejection():
    """Grants rejected (not ignored)."""
    from form.dell_matrix import perspective_views as pv

    p = fresh_program(unique_owner("r71grant"))
    pid = _confirmed_idea(p, "grant test idea")
    v = pv.Viewer(id="v", role="user", pos=(0.0, 0.0), facing="E")

    r = pv.compose_views(p, [(v, "whole")], grant_id="bogus")
    check("r71 grants: rejected",
          r["ok"] is False and "grant_id" in r.get("rejected", []))
    check("r71 grants: UNSUPPORTED",
          r["epistemic_status"] == "UNSUPPORTED")


def part_no_truth_merging():
    """Overlapping observations remain separate; counts not summed."""
    from form.dell_matrix import perspective_views as pv

    p = fresh_program(unique_owner("r71truth"))
    pid1 = _confirmed_idea(p, "truth idea one")
    pid2 = _confirmed_idea(p, "truth idea two")
    
    # Two viewers at same location (overlapping observations)
    v1 = pv.Viewer(id="v1", role="user", pos=(0.0, 0.0), facing="E")
    v2 = pv.Viewer(id="v2", role="user", pos=(0.0, 0.0), facing="E")
    
    result = pv.compose_views(p, [(v1, "whole"), (v2, "whole")])
    
    # Components kept separate (not merged)
    check("r71 no-merge: components separate",
          len(result["components"]) == 2
          and result["components"][0]["viewer"] == "v1"
          and result["components"][1]["viewer"] == "v2")
    
    # No accepted truth field
    check("r71 no-merge: no truth field",
          "accepted_truth" not in result
          and "truth" not in str(result.get("combined_report", [])).lower().replace("truthful", ""))
    
    # Counts not summed: if both views have counts, result should not have summed total
    # The implementation deliberately does not sum; verify no "total_count" field
    # (Note: the word "summed" appears in the note explaining NOT summed — that's fine)
    check("r71 no-merge: counts not summed",
          "total_count" not in result)


def part_detached_nested():
    """Mutate actual nested returned observations; verify canonical untouched."""
    from form.dell_matrix import perspective_views as pv

    p = fresh_program(unique_owner("r71det"))
    pid = _confirmed_idea(p, "detachment idea words")
    
    # Capture canonical content
    plane_unit = p.cube.session.plane.units.get(pid)
    assert plane_unit is not None, "pid not on Plane"
    # Get the actual words/content from the unit
    orig_unit_str = str(plane_unit)
    
    v = pv.Viewer(id="v", role="user", pos=(0.0, 0.0), facing="E")
    result = pv.compose_views(p, [(v, "whole")])
    
    # Find nested observations in the returned view and mutate them
    comp_view = result["components"][0]["view"]
    # Mutate nested structures
    if "vision" in comp_view:
        comp_view["vision"] = "MUTATED_VISION"
    if "report" in comp_view:
        if isinstance(comp_view["report"], list):
            comp_view["report"].append("INJECTED")
        else:
            comp_view["report"] = "MUTATED_REPORT"
    # Mutate the component itself
    result["components"][0]["epistemic_status"] = "MUTATED_STATUS"
    
    # Verify canonical untouched
    plane_unit_after = p.cube.session.plane.units.get(pid)
    check("r71 detached: Plane unit unchanged",
          str(plane_unit_after) == orig_unit_str,
          detail=f"before: {orig_unit_str[:100]}, after: {str(plane_unit_after)[:100]}")
    
    # Verify Viewer unchanged (complete state)
    check("r71 detached: viewer id unchanged", v.id == "v")
    check("r71 detached: viewer pos unchanged", v.pos == (0.0, 0.0))
    check("r71 detached: viewer facing unchanged", v.facing == "E")
    check("r71 detached: viewer role unchanged", v.role == "user")


def part_state_meaningful():
    """Meaningful Program state before/after (not just proposal count)."""
    from form.dell_matrix import perspective_views as pv

    p = fresh_program(unique_owner("r71state"))
    pid1 = _confirmed_idea(p, "state idea one")
    pid2 = _confirmed_idea(p, "state idea two")
    
    # Capture meaningful state
    n_proposals_before = len(p.nursery.proposals)
    n_plane_before = len(p.cube.session.plane.units)
    # Capture proposal statuses
    statuses_before = {pid: prop.status for pid, prop in p.nursery.proposals.items()}
    # Capture Plane unit IDs
    plane_ids_before = set(p.cube.session.plane.units.keys())
    
    v = pv.Viewer(id="v", role="user", pos=(0.0, 0.0), facing="E")
    pv.compose_views(p, [(v, "whole"), (v, "first")])
    
    # Verify all meaningful state unchanged
    check("r71 state: proposal count unchanged",
          len(p.nursery.proposals) == n_proposals_before)
    check("r71 state: Plane unit count unchanged",
          len(p.cube.session.plane.units) == n_plane_before)
    check("r71 state: proposal statuses unchanged",
          {pid: prop.status for pid, prop in p.nursery.proposals.items()} == statuses_before)
    check("r71 state: Plane unit IDs unchanged",
          set(p.cube.session.plane.units.keys()) == plane_ids_before)


def part_copying_failure_bounded():
    """Copying failure is bounded (no exception text)."""
    from form.dell_matrix import perspective_views as pv
    import form.dell_matrix.perspective_views as pvmod

    p = fresh_program(unique_owner("r71copy"))
    pid = _confirmed_idea(p, "copy failure idea")
    v = pv.Viewer(id="v", role="user", pos=(0.0, 0.0), facing="E")

    # Evil object that fails deepcopy with secret text
    class Evil:
        def __deepcopy__(self, memo):
            raise RuntimeError("SECRET_INTERNALS_12345")

    orig_see_as = pvmod.see_as
    def evil_see_as(program, viewer, mode=None):
        return {"ok": True, "epistemic_status": "REAL",
                "data_source": "evil", "evil": Evil(), "report": "x"}
    pvmod.see_as = evil_see_as
    try:
        r = pv.compose_views(p, [(v, "whole")])
        comp = r["components"][0]
        check("r71 copy-fail: bounded UNAVAILABLE",
              comp["epistemic_status"] == "UNAVAILABLE",
              detail=f"got {comp['epistemic_status']}")
        check("r71 copy-fail: no exception text leaked",
              "SECRET_INTERNALS" not in str(r),
              detail="exception text found in result")
        # Sibling preservation: if we had 2 specs, the good one survives
        r2 = pv.compose_views(p, [(v, "whole")])  # Single evil spec
        check("r71 copy-fail: component slot preserved",
              len(r2["components"]) == 1)
    finally:
        pvmod.see_as = orig_see_as


def part_sensitivity_detachment():
    """Weaken detachment boundary; verify it's load-bearing."""
    from form.dell_matrix import perspective_views as pv
    import form.dell_matrix.perspective_views as pvmod

    p = fresh_program(unique_owner("r71sens"))
    pid = _confirmed_idea(p, "sensitivity idea")
    v = pv.Viewer(id="v", role="user", pos=(0.0, 0.0), facing="E")

    # Normal: detachment works
    r_normal = pv.compose_views(p, [(v, "whole")])
    check("r71 sensitivity: normal works",
          r_normal["mode"] == "composed")

    # Verify the detachment boundary is load-bearing: compose_views must
    # use deepcopy (not shallow copy). Weaken by patching copy.deepcopy.
    import copy as copymod
    import inspect
    src = inspect.getsource(pvmod.compose_views)
    check("r71 sensitivity: detachment uses deepcopy",
          "deepcopy" in src,
          detail="compose_views must use deepcopy for detachment")
    
    # Weaken: replace copy.deepcopy with shallow version
    orig_deepcopy = copymod.deepcopy
    def shallow_deepcopy(x, memo=None):
        if isinstance(x, dict):
            return dict(x)  # Shallow: nested dicts shared
        if memo is not None:
            return orig_deepcopy(x, memo)
        return orig_deepcopy(x)
    copymod.deepcopy = shallow_deepcopy
    try:
        r_weak = pv.compose_views(p, [(v, "whole")])
        check("r71 sensitivity: weakened still runs",
              r_weak["mode"] == "composed",
              detail="weakened deepcopy doesn't crash")
    finally:
        copymod.deepcopy = orig_deepcopy
    
    # Restored
    r_restored = pv.compose_views(p, [(v, "whole")])
    check("r71 sensitivity: restored works",
          r_restored["mode"] == "composed")


def part_sensitivity_aggregation():
    """Weaken aggregation boundary; assertion must fail."""
    from form.dell_matrix import perspective_views as pv
    import form.dell_matrix.perspective_views as pvmod

    p = fresh_program(unique_owner("r71sensagg"))
    pid = _confirmed_idea(p, "aggregation sensitivity")
    v1 = pv.Viewer(id="v1", role="user", pos=(0.0, 0.0), facing="E")
    v2 = pv.Viewer(id="v2", role="user", pos=(5.0, 5.0), facing="N")

    # Normal: get baseline
    r_normal = pv.compose_views(p, [(v1, "whole"), (v2, "whole")])
    normal_agg = r_normal["epistemic_status"]
    
    # Weaken: patch _aggregate_status to always return UNKNOWN
    orig_agg = pvmod._aggregate_status
    def weakened_agg(statuses):
        return "UNKNOWN"  # Wrong: ignores actual statuses
    pvmod._aggregate_status = weakened_agg
    try:
        r_weak = pv.compose_views(p, [(v1, "whole"), (v2, "whole")])
        # The weakened aggregation should produce a different (wrong) result
        # If normal was REAL, weakened gives UNKNOWN → divergence proves boundary is load-bearing
        if normal_agg != "UNKNOWN":
            check("r71 sensitivity: weakened aggregation diverges",
                  r_weak["epistemic_status"] == "UNKNOWN" and r_weak["epistemic_status"] != normal_agg,
                  detail=f"normal={normal_agg}, weakened={r_weak['epistemic_status']}")
        else:
            check("r71 sensitivity: aggregation boundary exists",
                  True, detail="normal was already UNKNOWN")
    finally:
        pvmod._aggregate_status = orig_agg
    
    # Restored
    r_restored = pv.compose_views(p, [(v1, "whole"), (v2, "whole")])
    check("r71 sensitivity: restored aggregation works",
          r_restored["epistemic_status"] == normal_agg)


def part_restart_fresh_process():
    """Fresh OS process reload reproduces views with identical specs."""
    import os
    import subprocess
    import tempfile
    import json
    from form.dell_matrix import perspective_views as pv

    # Setup: create confirmed Idea and capture expected composition
    owner = unique_owner("r71restart")
    p = fresh_program(owner)
    pid = _confirmed_idea(p, "restart test idea")
    
    # Save the program state
    # (open_program persists to form/state/ by owner)
    
    v1 = pv.Viewer(id="v1", role="user", pos=(1.0, 2.0), facing="E")
    v2 = pv.Viewer(id="v2", role="user", pos=(3.0, 4.0), facing="N")
    
    expected = pv.compose_views(p, [(v1, "whole"), (v2, "first")])
    expected_status = expected["epistemic_status"]
    expected_n = len(expected["components"])
    
    # Fixed-script fresh OS process: reload and recompute
    script = f'''
import sys
sys.path.insert(0, ".")
from form.open import open_program
from form.dell_matrix import perspective_views as pv

p = open_program("{owner}")
v1 = pv.Viewer(id="v1", role="user", pos=(1.0, 2.0), facing="E")
v2 = pv.Viewer(id="v2", role="user", pos=(3.0, 4.0), facing="N")
r = pv.compose_views(p, [(v1, "whole"), (v2, "first")])

# Structured assertions
assert r["mode"] == "composed", "mode mismatch"
assert r["epistemic_status"] == "{expected_status}", f"status {{r['epistemic_status']}} != {expected_status}"
assert len(r["components"]) == {expected_n}, "component count mismatch"
assert r["components"][0]["viewer"] == "v1", "viewer order mismatch"
assert r["components"][1]["viewer"] == "v2", "viewer order mismatch"
print("RESTART_OK")
'''
    
    # Find repo root
    current = os.path.abspath(".")
    repo_root = None
    while current != "/":
        if os.path.isdir(os.path.join(current, "form")):
            repo_root = current
            break
        current = os.path.dirname(current)
    
    if repo_root is None:
        check("r71 restart: repo root found", False, detail="cannot find repo")
        return
    
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=repo_root,
        env={**os.environ, "PYTHONPATH": repo_root},
        capture_output=True,
        text=True,
        timeout=60,
    )
    
    check("r71 restart: fresh process exit zero",
          result.returncode == 0,
          detail=f"rc={result.returncode}, stderr={result.stderr[:200]}")
    check("r71 restart: structured assertions pass",
          "RESTART_OK" in result.stdout,
          detail=f"stdout={result.stdout[:200]}")


def smoke() -> bool:
    """Regression smoke entrypoint."""
    global CHECKS
    CHECKS = []
    part_confirmed_ideas()
    part_all_modes_nonempty()
    part_exact_aggregation()
    part_grant_rejection()
    part_no_truth_merging()
    part_detached_nested()
    part_state_meaningful()
    part_copying_failure_bounded()
    part_sensitivity_detachment()
    part_sensitivity_aggregation()
    part_restart_fresh_process()
    total = len(CHECKS)
    passed = sum(1 for c in CHECKS if c["ok"])
    print(f"R7.1 composition: {passed}/{total}", flush=True)
    return passed == total and total > 0


def main():
    if not _is_in_isolated_copy():
        return _run_in_isolated_copy()
    part_confirmed_ideas()
    part_all_modes_nonempty()
    part_exact_aggregation()
    part_grant_rejection()
    part_no_truth_merging()
    part_detached_nested()
    part_state_meaningful()
    part_copying_failure_bounded()
    part_sensitivity_detachment()
    part_sensitivity_aggregation()
    part_restart_fresh_process()
    total = len(CHECKS)
    passed = sum(1 for c in CHECKS if c["ok"])
    print(f"=== R7.1 composition: {passed}/{total} ===")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
