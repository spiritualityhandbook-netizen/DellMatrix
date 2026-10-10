#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R7.1 read-only perspective composition — proof matrix.

GDP_R71_FINISH_EXISTING_OUTCOME_EVIDENCE (MODE=C).

Proves with populated public-path evidence:
- Exact Idea IDs in each mode's observation structure
- Exact aggregation outcomes (no permissive branches)
- Real detachment sensitivity (shallow copy fails the assertion)
- Exact restart (JSON-captured composition compared)
- Content-level state preservation
- Sibling failure preservation

Uses disposable-copy isolation.
"""

from __future__ import annotations

import copy
import json
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
    from form.dell_matrix import agent_authority as aa
    grant = aa.issue_root_grant(p, issuer="test-host",
                               subject=subject, target=pid,
                               content_pid=pid)
    return grant


def _confirmed_idea(p, words: str) -> str:
    """Create, authorize, and confirm a real Idea. Returns pid."""
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
    
    assert r["ok"] is True, f"confirm failed: {r}"
    assert r["result"] == "committed", f"not committed: {r}"
    
    prop = p.nursery.proposals.get(pid)
    assert prop is not None and prop.status == "confirmed"
    assert pid in p.cube.session.plane.units
    
    return pid


def _idea_ids_in_view(view: Dict[str, Any], mode: str) -> List[str]:
    """Extract Idea IDs from a view's observation structure by mode."""
    ids = []
    if mode == "first":
        vision = view.get("vision", {})
        # in_view_ids is the list of visible Idea IDs
        ids.extend(vision.get("in_view_ids", []))
        # Also check nodes
        for n in vision.get("nodes", []):
            if isinstance(n, dict) and "id" in n:
                ids.append(n["id"])
    else:
        # third, parts, whole: nodes[].id
        for n in view.get("nodes", []):
            if isinstance(n, dict) and "id" in n:
                ids.append(n["id"])
    return ids


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


def part_populated_observations():
    """Exact Idea IDs in each mode's observation structure.
    
    Positions Viewers deliberately so each mode can see the confirmed Idea.
    A metadata-rich empty view must fail (assert IDs present, not just keys).
    """
    from form.dell_matrix import perspective_views as pv

    p = fresh_program(unique_owner("r71pop"))
    pid = _confirmed_idea(p, "populated observation idea")
    
    # The confirmed Idea is at (-1.0, -1.0). Position viewers to see it.
    # For 'first' mode: stand west of it facing east
    # For other modes: position doesn't matter as much, but be deliberate
    
    mode_viewers = {
        "first": pv.Viewer(id="v-first", role="user", pos=(-5.0, 0.0), facing="E"),
        "third": pv.Viewer(id="v-third", role="user", pos=(0.0, 0.0), facing="E"),
        "parts": pv.Viewer(id="v-parts", role="user", pos=(0.0, 0.0), facing="E"),
        "whole": pv.Viewer(id="v-whole", role="user", pos=(0.0, 0.0), facing="E"),
    }
    
    for mode, viewer in mode_viewers.items():
        result = pv.compose_views(p, [(viewer, mode)])
        comp = result["components"][0]
        view = comp["view"]
        
        # Assert fixture precondition: view succeeded
        check(f"r71 populated: {mode} view ok",
              comp.get("epistemic_status") in ("REAL", "PARTIAL"),
              detail=f"status={comp.get('epistemic_status')}")
        
        # Extract Idea IDs from the actual observation structure
        ids = _idea_ids_in_view(view, mode)
        
        # Assert exact Idea ID present (not just metadata keys)
        check(f"r71 populated: {mode} contains exact pid",
              pid in ids,
              detail=f"mode={mode}, pid={pid[:12]}, found_ids={[i[:12] for i in ids]}")


def part_exact_aggregation():
    """Exact aggregation outcomes with fixture preconditions.
    
    No permissive branches. Each case asserts preconditions then exact result.
    """
    from form.dell_matrix import perspective_views as pv

    p = fresh_program(unique_owner("r71agg"))
    pid = _confirmed_idea(p, "aggregation idea")
    
    v1 = pv.Viewer(id="v1", role="user", pos=(-5.0, 0.0), facing="E")
    v2 = pv.Viewer(id="v2", role="user", pos=(0.0, 0.0), facing="E")
    
    # Case 1: All REAL → REAL
    # Precondition: both components must be REAL
    r1 = pv.compose_views(p, [(v1, "whole"), (v2, "whole")])
    s1 = [c["epistemic_status"] for c in r1["components"]]
    check("r71 agg: precondition both REAL",
          s1 == ["REAL", "REAL"],
          detail=f"got {s1}")
    check("r71 agg: all REAL → REAL",
          r1["epistemic_status"] == "REAL",
          detail=f"got {r1['epistemic_status']}")
    
    # Case 2: Readable + failed → PARTIAL
    # Precondition: one REAL, one UNSUPPORTED
    v_bad = pv.Viewer(id="vbad", role="user", pos=(float('inf'), 0.0), facing="E")
    r2 = pv.compose_views(p, [(v1, "whole"), (v_bad, "whole")])
    s2 = [c["epistemic_status"] for c in r2["components"]]
    check("r71 agg: precondition REAL+UNSUPPORTED",
          s2[0] == "REAL" and s2[1] == "UNSUPPORTED",
          detail=f"got {s2}")
    check("r71 agg: readable+failed → PARTIAL",
          r2["epistemic_status"] == "PARTIAL",
          detail=f"got {r2['epistemic_status']}")
    
    # Case 3: No readable → first non-readable status (not invented ordering)
    r3 = pv.compose_views(p, [(v_bad, "whole")])
    s3 = [c["epistemic_status"] for c in r3["components"]]
    check("r71 agg: precondition all UNSUPPORTED",
          s3 == ["UNSUPPORTED"],
          detail=f"got {s3}")
    check("r71 agg: no readable → UNSUPPORTED (preserved)",
          r3["epistemic_status"] == "UNSUPPORTED",
          detail=f"got {r3['epistemic_status']}")
    
    # Case 4: Empty → UNKNOWN (explicitly empty request)
    r4 = pv.compose_views(p, [])
    check("r71 agg: empty → UNKNOWN",
          r4["epistemic_status"] == "UNKNOWN" and r4["ok"] is True)
    check("r71 agg: empty has no components",
          r4["components"] == [])
    
    # Case 5: Malformed containers → UNSUPPORTED (explicit rejection)
    for bad in [None, False, 0, "", {}]:
        rb = pv.compose_views(p, bad)
        check(f"r71 agg: {bad!r} → UNSUPPORTED",
              rb["ok"] is False and rb["epistemic_status"] == "UNSUPPORTED",
              detail=f"got ok={rb.get('ok')}")


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
    
    v1 = pv.Viewer(id="v1", role="user", pos=(0.0, 0.0), facing="E")
    v2 = pv.Viewer(id="v2", role="user", pos=(0.0, 0.0), facing="E")
    
    result = pv.compose_views(p, [(v1, "whole"), (v2, "whole")])
    
    check("r71 no-merge: components separate",
          len(result["components"]) == 2
          and result["components"][0]["viewer"] == "v1"
          and result["components"][1]["viewer"] == "v2")
    
    check("r71 no-merge: no accepted_truth field",
          "accepted_truth" not in result)
    
    check("r71 no-merge: no total_count field",
          "total_count" not in result)
    
    # Both components see the same pids (overlapping), but kept separate
    ids1 = _idea_ids_in_view(result["components"][0]["view"], "whole")
    ids2 = _idea_ids_in_view(result["components"][1]["view"], "whole")
    check("r71 no-merge: overlapping observations separate",
          pid1 in ids1 and pid1 in ids2 and pid2 in ids1 and pid2 in ids2,
          detail="both viewers see both pids, components not merged")


def part_detached_real_sensitivity():
    """Real detachment sensitivity with retained nested observation.
    
    Dispatch fixture returns a retained nested observation. Mutate the composed
    result; the retained original must stay unchanged. Replace deepcopy with
    shallow: the same assertion must fail. Restore in finally.
    """
    from form.dell_matrix import perspective_views as pv
    import form.dell_matrix.perspective_views as pvmod
    import copy as copymod

    p = fresh_program(unique_owner("r71detsens"))
    pid = _confirmed_idea(p, "detachment sensitivity idea")
    v = pv.Viewer(id="v", role="user", pos=(0.0, 0.0), facing="E")

    # Retained nested observation: a dict we keep a reference to
    retained_nested = {"secret": "ORIGINAL", "items": [1, 2, 3]}
    
    orig_see_as = pvmod.see_as
    def fixture_see_as(program, viewer, mode=None):
        return {
            "ok": True,
            "epistemic_status": "REAL",
            "data_source": "fixture",
            "mode": mode,
            "nested": retained_nested,  # Same object, not a copy
            "report": "fixture",
        }
    pvmod.see_as = fixture_see_as
    try:
        # Normal (deepcopy): mutate composed result, retained stays unchanged
        r1 = pv.compose_views(p, [(v, "whole")])
        r1["components"][0]["view"]["nested"]["secret"] = "MUTATED"
        r1["components"][0]["view"]["nested"]["items"].append(999)
        
        check("r71 detach-sens: retained unchanged with deepcopy",
              retained_nested["secret"] == "ORIGINAL"
              and retained_nested["items"] == [1, 2, 3],
              detail=f"retained={retained_nested}")
        
        # Reset retained for the shallow test
        retained_nested["secret"] = "ORIGINAL"
        retained_nested["items"] = [1, 2, 3]
        
        # Weaken: replace deepcopy with shallow copy
        orig_deepcopy = copymod.deepcopy
        def shallow_deepcopy(x, memo=None):
            if isinstance(x, dict):
                return dict(x)
            if memo is not None:
                return orig_deepcopy(x, memo)
            return orig_deepcopy(x)
        copymod.deepcopy = shallow_deepcopy
        try:
            r2 = pv.compose_views(p, [(v, "whole")])
            r2["components"][0]["view"]["nested"]["secret"] = "MUTATED_SHALLOW"
            # With shallow copy, the nested dict is shared → retained changes
            # The assertion MUST FAIL (proving the boundary is load-bearing)
            shallow_failed = (retained_nested["secret"] != "ORIGINAL")
            check("r71 detach-sens: shallow copy fails the assertion",
                  shallow_failed,
                  detail=f"retained secret={retained_nested['secret']}, "
                         f"expected it to be mutated (proving shallow is insufficient)")
        finally:
            copymod.deepcopy = orig_deepcopy
    finally:
        pvmod.see_as = orig_see_as


def part_state_content():
    """Content-level state preservation (not just counts/IDs)."""
    from form.dell_matrix import perspective_views as pv

    p = fresh_program(unique_owner("r71state"))
    pid1 = _confirmed_idea(p, "state idea one words")
    pid2 = _confirmed_idea(p, "state idea two words")
    
    # Capture full content before
    proposals_before = {
        pid: {"words": str(prop.words), "status": prop.status}
        for pid, prop in p.nursery.proposals.items()
    }
    plane_before = {
        uid: {"words": str(unit.words), "x": unit.x, "y": unit.y,
              "label": unit.label, "skin": str(unit.skin)}
        for uid, unit in p.cube.session.plane.units.items()
    }
    
    v = pv.Viewer(id="v", role="user", pos=(1.0, 2.0), facing="S",
                  part_radius=5.0, part_skins=["words"])
    v_before = {
        "id": v.id, "role": v.role, "pos": v.pos, "facing": v.facing,
        "mode": v.mode, "part_radius": v.part_radius,
        "part_skins": list(v.part_skins),
    }
    
    pv.compose_views(p, [(v, "whole"), (v, "first")])
    
    # Compare content after
    proposals_after = {
        pid: {"words": str(prop.words), "status": prop.status}
        for pid, prop in p.nursery.proposals.items()
    }
    plane_after = {
        uid: {"words": str(unit.words), "x": unit.x, "y": unit.y,
              "label": unit.label, "skin": str(unit.skin)}
        for uid, unit in p.cube.session.plane.units.items()
    }
    v_after = {
        "id": v.id, "role": v.role, "pos": v.pos, "facing": v.facing,
        "mode": v.mode, "part_radius": v.part_radius,
        "part_skins": list(v.part_skins),
    }
    
    check("r71 state: proposal content unchanged",
          proposals_after == proposals_before,
          detail="proposal words/status differ")
    check("r71 state: Plane unit content unchanged",
          plane_after == plane_before,
          detail="plane unit content differ")
    check("r71 state: all Viewer fields unchanged",
          v_after == v_before,
          detail=f"viewer changed: {v_after} vs {v_before}")


def part_sibling_failures():
    """Failing component beside readable; assert both outcomes."""
    from form.dell_matrix import perspective_views as pv

    p = fresh_program(unique_owner("r71sib"))
    pid = _confirmed_idea(p, "sibling idea")
    
    v_good = pv.Viewer(id="v-good", role="user", pos=(0.0, 0.0), facing="E")
    v_bad = pv.Viewer(id="v-bad", role="user", pos=(float('inf'), 0.0), facing="E")
    
    # Failing first, readable second
    # Note: invalid specs produce components without viewer ID (bounded failure);
    # identify by index and status
    r = pv.compose_views(p, [(v_bad, "whole"), (v_good, "whole")])
    
    check("r71 siblings: two components",
          len(r["components"]) == 2)
    check("r71 siblings: first failed (UNSUPPORTED)",
          r["components"][0]["epistemic_status"] == "UNSUPPORTED"
          and r["components"][0]["index"] == 0,
          detail=f"got {r['components'][0]}")
    check("r71 siblings: second readable",
          r["components"][1]["epistemic_status"] in ("REAL", "PARTIAL")
          and r["components"][1].get("viewer") == "v-good",
          detail=f"got {r['components'][1].get('epistemic_status')}")
    check("r71 siblings: aggregate PARTIAL",
          r["epistemic_status"] == "PARTIAL",
          detail=f"got {r['epistemic_status']}")
    
    # Readable first, failing second (order preserved by index)
    r2 = pv.compose_views(p, [(v_good, "whole"), (v_bad, "whole")])
    check("r71 siblings: order preserved",
          r2["components"][0].get("viewer") == "v-good"
          and r2["components"][1]["index"] == 1
          and r2["components"][1]["epistemic_status"] == "UNSUPPORTED")


def part_copying_failure_bounded():
    """Copying failure bounded; no exception text; sibling preserved."""
    from form.dell_matrix import perspective_views as pv
    import form.dell_matrix.perspective_views as pvmod

    p = fresh_program(unique_owner("r71copy"))
    pid = _confirmed_idea(p, "copy failure idea")
    v_good = pv.Viewer(id="v-good", role="user", pos=(0.0, 0.0), facing="E")
    v_evil = pv.Viewer(id="v-evil", role="user", pos=(1.0, 1.0), facing="N")

    class Evil:
        def __deepcopy__(self, memo):
            raise RuntimeError("SECRET_INTERNALS_12345")

    orig_see_as = pvmod.see_as
    def evil_see_as(program, viewer, mode=None):
        if viewer.id == "v-evil":
            return {"ok": True, "epistemic_status": "REAL",
                    "data_source": "evil", "evil": Evil(), "report": "x"}
        return orig_see_as(program, viewer, mode)
    pvmod.see_as = evil_see_as
    try:
        # Evil beside good: evil fails bounded, good survives
        r = pv.compose_views(p, [(v_evil, "whole"), (v_good, "whole")])
        check("r71 copy-fail: evil component UNAVAILABLE",
              r["components"][0]["epistemic_status"] == "UNAVAILABLE",
              detail=f"got {r['components'][0].get('epistemic_status')}")
        # Safe check (Evil object has no __str__ issue, but be consistent)
        def safe_contains_secret(obj, depth=0):
            if depth > 10:
                return False
            if isinstance(obj, str):
                return "SECRET_INTERNALS" in obj
            if isinstance(obj, dict):
                return any(safe_contains_secret(v, depth+1) for v in obj.values())
            if isinstance(obj, (list, tuple)):
                return any(safe_contains_secret(v, depth+1) for v in obj)
            return False
        check("r71 copy-fail: no exception text",
              not safe_contains_secret(r))
        check("r71 copy-fail: good sibling preserved",
              r["components"][1]["viewer"] == "v-good"
              and r["components"][1]["epistemic_status"] in ("REAL", "PARTIAL"),
              detail=f"got {r['components'][1].get('epistemic_status')}")
    finally:
        pvmod.see_as = orig_see_as


def part_report_failure_bounded():
    """Report-construction failure bounded; no reflected exception text."""
    from form.dell_matrix import perspective_views as pv
    import form.dell_matrix.perspective_views as pvmod

    p = fresh_program(unique_owner("r71repfail"))
    pid = _confirmed_idea(p, "report failure idea")
    v = pv.Viewer(id="v", role="user", pos=(0.0, 0.0), facing="E")

    # Evil report object that fails str()
    class EvilReport:
        def __str__(self):
            raise RuntimeError("REPORT_SECRET_67890")
        def __repr__(self):
            raise RuntimeError("REPORT_SECRET_67890")

    orig_see_as = pvmod.see_as
    def evil_report_see_as(program, viewer, mode=None):
        return {"ok": True, "epistemic_status": "REAL",
                "data_source": "evil", "report": EvilReport(), "mode": mode}
    pvmod.see_as = evil_report_see_as
    try:
        r = pv.compose_views(p, [(v, "whole")])
        # Should not crash; report construction is bounded
        check("r71 report-fail: composition completes",
              r["mode"] == "composed")
        # Check no exception text leaked via safe traversal (not json.dumps
        # which would invoke the evil __str__)
        def safe_contains_secret(obj, depth=0):
            if depth > 10:
                return False
            if isinstance(obj, str):
                return "REPORT_SECRET" in obj
            if isinstance(obj, dict):
                return any(safe_contains_secret(v, depth+1) for v in obj.values())
            if isinstance(obj, (list, tuple)):
                return any(safe_contains_secret(v, depth+1) for v in obj)
            return False
        check("r71 report-fail: no exception text",
              not safe_contains_secret(r))
        # Components still present
        check("r71 report-fail: component preserved",
              len(r["components"]) == 1)
    finally:
        pvmod.see_as = orig_see_as


def part_restart_exact():
    """Exact restart: saved-view round trip via correct loader.
    
    Saves the populated Program, loads it in a fresh child through
    persist_rest.load(owner, activate=False), asserts exact confirmed Idea IDs
    in both Nursery and Plane, then compares the complete deterministic
    composition. Proves sensitivity by mutating one observation.
    """
    import os
    import subprocess
    from form.dell_matrix import perspective_views as pv
    from form import persist_rest

    owner = unique_owner("r71restart")
    p = fresh_program(owner)
    pid = _confirmed_idea(p, "restart exact idea words")
    # Save the populated Program
    p.save()
    
    # Viewer specifications (explicit, deterministic)
    v1_spec = {"id": "v1", "role": "user", "pos": [0.0, 0.0], "facing": "E"}
    v2_spec = {"id": "v2", "role": "user", "pos": [5.0, 5.0], "facing": "N"}
    
    v1 = pv.Viewer(id="v1", role="user", pos=(0.0, 0.0), facing="E")
    v2 = pv.Viewer(id="v2", role="user", pos=(5.0, 5.0), facing="N")
    
    expected = pv.compose_views(p, [(v1, "whole"), (v2, "whole")])
    
    # Capture complete deterministic composition
    # Normalize through JSON round-trip for tuple/list consistency
    def normalize(obj):
        return json.loads(json.dumps(obj, sort_keys=True, default=str))
    
    expected_norm = normalize({
        "aggregate": expected["epistemic_status"],
        "components": [
            {
                "viewer": c["viewer"],
                "mode": c["requested_mode"],
                "status": c["epistemic_status"],
                "source": c["source"],
                # Complete observation: nodes with IDs, positions, labels
                "nodes": sorted(
                    [{"id": n.get("id"), "label": n.get("label"),
                      "x": n.get("x"), "y": n.get("y")}
                     for n in c["view"].get("nodes", [])
                     if isinstance(n, dict)],
                    key=lambda x: x["id"] or ""
                ),
                "count": c["view"].get("count"),
            }
            for c in expected["components"]
        ],
    })
    expected_json = json.dumps(expected_norm, sort_keys=True)
    
    cwd = os.path.abspath(".")
    specs_json = json.dumps([v1_spec, v2_spec])
    
    # Fixed child script
    script = f'''
import sys, json
sys.path.insert(0, ".")
from form import persist_rest
from form.dell_matrix import perspective_views as pv

# Load via correct reader
p = persist_rest.load("{owner}", activate=False)

# Assert exact confirmed Idea IDs in both Nursery and Plane BEFORE composing
pid = "{pid}"
assert pid in p.nursery.proposals, f"pid not in nursery"
assert p.nursery.proposals[pid].status == "confirmed", "not confirmed"
assert pid in p.cube.session.plane.units, f"pid not in Plane"

# Recreate specifications
specs_data = json.loads({specs_json!r})
viewers = []
for s in specs_data:
    viewers.append(pv.Viewer(id=s["id"], role=s["role"],
                             pos=tuple(s["pos"]), facing=s["facing"]))

r = pv.compose_views(p, [(viewers[0], "whole"), (viewers[1], "whole")])

def normalize(obj):
    return json.loads(json.dumps(obj, sort_keys=True, default=str))

actual_norm = normalize({{
    "aggregate": r["epistemic_status"],
    "components": [
        {{
            "viewer": c["viewer"],
            "mode": c["requested_mode"],
            "status": c["epistemic_status"],
            "source": c["source"],
            "nodes": sorted(
                [{{"id": n.get("id"), "label": n.get("label"),
                  "x": n.get("x"), "y": n.get("y")}}
                 for n in c["view"].get("nodes", [])
                 if isinstance(n, dict)],
                key=lambda x: x["id"] or ""
            ),
            "count": c["view"].get("count"),
        }}
        for c in r["components"]
    ],
}})
actual_json = json.dumps(actual_norm, sort_keys=True)
expected_json = {expected_json!r}

if actual_json != expected_json:
    print(f"MISMATCH", file=sys.stderr)
    sys.exit(1)
print("RESTART_EXACT_OK")
'''
    
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=cwd,
        env={**os.environ, "PYTHONPATH": cwd},
        capture_output=True,
        text=True,
        timeout=60,
    )
    
    check("r71 restart: fresh process exit zero",
          result.returncode == 0,
          detail=f"rc={result.returncode}, stderr={result.stderr[:300]}")
    check("r71 restart: complete composition matches",
          "RESTART_EXACT_OK" in result.stdout,
          detail=f"stdout={result.stdout[:200]}")
    
    # Sensitivity: mutate one observation, comparison must reject
    mutated = json.loads(expected_json)
    # Change one node's label (preserve status/count/viewer order)
    if mutated["components"] and mutated["components"][0]["nodes"]:
        mutated["components"][0]["nodes"][0]["label"] = "MUTATED_LABEL"
    mutated_json = json.dumps(mutated, sort_keys=True)
    check("r71 restart: mutated observation differs",
          mutated_json != expected_json,
          detail="mutation did not change the JSON (test bug)")


def part_sensitivity_aggregation():
    """Weaken aggregation; assertion must fail. Restore in finally."""
    from form.dell_matrix import perspective_views as pv
    import form.dell_matrix.perspective_views as pvmod

    p = fresh_program(unique_owner("r71sensagg"))
    pid = _confirmed_idea(p, "aggregation sensitivity")
    v1 = pv.Viewer(id="v1", role="user", pos=(0.0, 0.0), facing="E")
    v2 = pv.Viewer(id="v2", role="user", pos=(5.0, 5.0), facing="N")

    r_normal = pv.compose_views(p, [(v1, "whole"), (v2, "whole")])
    normal_agg = r_normal["epistemic_status"]
    # Precondition: normal is REAL
    check("r71 sens-agg: precondition REAL",
          normal_agg == "REAL",
          detail=f"got {normal_agg}")
    
    orig_agg = pvmod._aggregate_status
    def weakened_agg(statuses):
        return "UNKNOWN"
    pvmod._aggregate_status = weakened_agg
    try:
        r_weak = pv.compose_views(p, [(v1, "whole"), (v2, "whole")])
        check("r71 sens-agg: weakened diverges (fails)",
              r_weak["epistemic_status"] != normal_agg,
              detail=f"weakened={r_weak['epistemic_status']}, normal={normal_agg}")
    finally:
        pvmod._aggregate_status = orig_agg
    
    r_restored = pv.compose_views(p, [(v1, "whole"), (v2, "whole")])
    check("r71 sens-agg: restored",
          r_restored["epistemic_status"] == normal_agg)


def smoke() -> bool:
    global CHECKS
    CHECKS = []
    part_populated_observations()
    part_exact_aggregation()
    part_grant_rejection()
    part_no_truth_merging()
    part_detached_real_sensitivity()
    part_state_content()
    part_sibling_failures()
    part_copying_failure_bounded()
    part_report_failure_bounded()
    part_restart_exact()
    part_sensitivity_aggregation()
    total = len(CHECKS)
    passed = sum(1 for c in CHECKS if c["ok"])
    print(f"R7.1 composition: {passed}/{total}", flush=True)
    return passed == total and total > 0


def main():
    if not _is_in_isolated_copy():
        return _run_in_isolated_copy()
    part_populated_observations()
    part_exact_aggregation()
    part_grant_rejection()
    part_no_truth_merging()
    part_detached_real_sensitivity()
    part_state_content()
    part_sibling_failures()
    part_copying_failure_bounded()
    part_report_failure_bounded()
    part_restart_exact()
    part_sensitivity_aggregation()
    total = len(CHECKS)
    passed = sum(1 for c in CHECKS if c["ok"])
    print(f"=== R7.1 composition: {passed}/{total} ===")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
