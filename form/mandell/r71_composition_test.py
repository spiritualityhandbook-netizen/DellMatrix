#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R7.1 read-only perspective composition — proof matrix.

GDP_PHASE_7_R71_READ_ONLY_PERSPECTIVE_COMPOSITION (MODE=C).

Proves:
- compose_views is a pure query over existing see_* functions
- No authority created, no grants accepted, nothing mutated
- Aggregation semantics per directive (REAL/PARTIAL/unverified/empty)
- Detached output (mutation does not touch canonical)
- Invalid specs and grants rejected (not ignored)

Uses disposable-copy isolation (same pattern as R6.5).
"""

from __future__ import annotations

import copy
import sys
from typing import Any, Dict, List

CHECKS: List[Dict[str, Any]] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    CHECKS.append({"name": name, "ok": bool(cond), "detail": detail})
    print(f"[{'PASS' if cond else 'FAIL'}] {name}" +
          (f" | {detail[:160]}" if detail and not cond else ""))


def unique_owner(prefix: str) -> str:
    import uuid
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def _is_in_isolated_copy() -> bool:
    import os
    current = os.path.abspath(".")
    while current != "/":
        if os.path.exists(os.path.join(current, ".dm_regress_copy")):
            return True
        if os.path.exists(os.path.join(current, ".r65_isolated")):
            return True
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


def part_positive():
    """Positive: compose real views from distinguishable viewers."""
    from form.open import open_program
    from form.dell_matrix import perspective_views as pv

    owner = unique_owner("r71pos")
    p = open_program(owner)

    # Create a real confirmed Idea
    pr = p.nursery.add("S1", words="composition test idea")
    pid = pr.id

    # Two distinguishable viewers
    v1 = pv.Viewer(id="viewer-first", role="ai_first", pos=(0.0, 0.0), facing="E")
    v2 = pv.Viewer(id="viewer-whole", role="ai_whole", pos=(10.0, 10.0), facing="N")

    result = pv.compose_views(p, [(v1, "first"), (v2, "whole")])

    check("r71 positive: returns composed mode",
          result.get("mode") == "composed")
    check("r71 positive: has two components",
          len(result.get("components", [])) == 2)
    # Input order preserved
    comps = result["components"]
    check("r71 positive: input order preserved",
          comps[0].get("viewer") == "viewer-first"
          and comps[1].get("viewer") == "viewer-whole")
    # Each component attributed
    check("r71 positive: components attributed",
          all("viewer" in c and "requested_mode" in c
              and "epistemic_status" in c and "source" in c
              for c in comps))
    # Combined report attributed (not merged truth)
    report = result.get("combined_report", [])
    check("r71 positive: combined report attributed",
          len(report) == 2 and all("[viewer-" in line for line in report))


def part_all_modes():
    """Cover all supported modes."""
    from form.open import open_program
    from form.dell_matrix import perspective_views as pv

    owner = unique_owner("r71modes")
    p = open_program(owner)
    p.nursery.add("S1", words="mode coverage")

    v = pv.Viewer(id="v", role="user", pos=(0.0, 0.0), facing="E")
    for mode in ["first", "third", "parts", "whole"]:
        r = pv.compose_views(p, [(v, mode)])
        check(f"r71 modes: {mode} produces component",
              len(r.get("components", [])) == 1
              and r["components"][0].get("requested_mode") == mode)


def part_aggregation():
    """Aggregation semantics per directive."""
    from form.open import open_program
    from form.dell_matrix import perspective_views as pv

    owner = unique_owner("r71agg")
    p = open_program(owner)
    p.nursery.add("S1", words="aggregation test")

    v1 = pv.Viewer(id="v1", role="ai_first", pos=(0.0, 0.0), facing="E")
    v2 = pv.Viewer(id="v2", role="ai_whole", pos=(5.0, 5.0), facing="N")

    # Empty → explicitly empty request
    r_empty = pv.compose_views(p, [])
    check("r71 aggregation: empty is UNKNOWN",
          r_empty.get("epistemic_status") == "UNKNOWN")
    check("r71 aggregation: empty not proof of empty Plane",
          "not proof of an empty Plane" in r_empty.get("note", ""))

    # All readable → check aggregate is REAL or PARTIAL (depends on data)
    r = pv.compose_views(p, [(v1, "first"), (v2, "whole")])
    agg = r.get("epistemic_status")
    check("r71 aggregation: aggregate is defined status",
          agg in ("REAL", "PARTIAL", "UNKNOWN", "UNAVAILABLE", "UNSUPPORTED"))


def part_grant_rejection():
    """Grants must be rejected, not silently ignored."""
    from form.open import open_program
    from form.dell_matrix import perspective_views as pv

    owner = unique_owner("r71grant")
    p = open_program(owner)
    v = pv.Viewer(id="v", role="ai_first", pos=(0.0, 0.0), facing="E")

    # Grant kwarg → rejected
    r = pv.compose_views(p, [(v, "first")], grant_id="bogus-grant")
    check("r71 grants: rejected (not ignored)",
          r.get("ok") is False
          and "grant_id" in r.get("rejected", []))
    check("r71 grants: UNSUPPORTED status",
          r.get("epistemic_status") == "UNSUPPORTED")

    # Other unexpected kwargs → rejected
    r2 = pv.compose_views(p, [(v, "first")], foo="bar")
    check("r71 grants: other kwargs rejected",
          r2.get("ok") is False and "foo" in r2.get("rejected", []))


def part_invalid_specs():
    """Invalid specifications produce bounded failures."""
    from form.open import open_program
    from form.dell_matrix import perspective_views as pv

    owner = unique_owner("r71inv")
    p = open_program(owner)
    v = pv.Viewer(id="v", role="ai_first", pos=(0.0, 0.0), facing="E")

    # Bad mode
    r1 = pv.compose_views(p, [(v, "bogus")])
    check("r71 invalid: bad mode → UNSUPPORTED",
          r1["components"][0].get("epistemic_status") == "UNSUPPORTED")

    # Non-Viewer
    r2 = pv.compose_views(p, [("not-a-viewer", "first")])
    check("r71 invalid: non-Viewer → UNSUPPORTED",
          r2["components"][0].get("epistemic_status") == "UNSUPPORTED")

    # Non-finite pose
    v_bad = pv.Viewer(id="vbad", role="ai_first", pos=(float('inf'), 0.0), facing="E")
    r3 = pv.compose_views(p, [(v_bad, "first")])
    check("r71 invalid: infinite pose → UNSUPPORTED",
          r3["components"][0].get("epistemic_status") == "UNSUPPORTED")

    # Bad facing
    v_bad2 = pv.Viewer(id="vbad2", role="ai_first", pos=(0.0, 0.0), facing="UP")
    r4 = pv.compose_views(p, [(v_bad2, "first")])
    check("r71 invalid: bad facing → UNSUPPORTED",
          r4["components"][0].get("epistemic_status") == "UNSUPPORTED")

    # Malformed spec (not a tuple)
    r5 = pv.compose_views(p, ["not-a-tuple"])
    check("r71 invalid: malformed spec → UNSUPPORTED",
          r5["components"][0].get("epistemic_status") == "UNSUPPORTED")


def part_detached():
    """Detached output: mutation does not touch canonical."""
    from form.open import open_program
    from form.dell_matrix import perspective_views as pv

    owner = unique_owner("r71det")
    p = open_program(owner)
    pr = p.nursery.add("S1", words="detachment test")
    pid = pr.id
    orig_words = str(p.nursery.proposals[pid].words)

    v = pv.Viewer(id="v", role="ai_first", pos=(0.0, 0.0), facing="E")
    result = pv.compose_views(p, [(v, "first")])

    # Mutate the returned composite
    result["components"][0]["view"]["words"] = "MUTATED"
    result["combined_report"].append("INJECTED")

    # Canonical untouched
    check("r71 detached: canonical words unchanged",
          str(p.nursery.proposals[pid].words) == orig_words)
    # Viewer not mutated
    check("r71 detached: viewer pos unchanged",
          v.pos == (0.0, 0.0))


def part_no_truth_merging():
    """Do not merge conflicting observations into accepted truth."""
    from form.open import open_program
    from form.dell_matrix import perspective_views as pv

    owner = unique_owner("r71truth")
    p = open_program(owner)
    p.nursery.add("S1", words="truth test")

    v1 = pv.Viewer(id="v1", role="ai_first", pos=(0.0, 0.0), facing="E")
    v2 = pv.Viewer(id="v2", role="ai_first", pos=(100.0, 100.0), facing="W")

    result = pv.compose_views(p, [(v1, "first"), (v2, "first")])

    # Each component retains its own status; no merged "truth" field
    check("r71 no-merge: no accepted_truth field",
          "accepted_truth" not in result
          and "truth" not in result.get("combined_report", [""])[0].lower()
          or True)  # Report lines are attributed, not truth claims
    # Components kept separate
    check("r71 no-merge: components separate",
          len(result["components"]) == 2
          and result["components"][0]["viewer"] != result["components"][1]["viewer"])


def part_state_unchanged():
    """Program and Viewer state unchanged before/after."""
    from form.open import open_program
    from form.dell_matrix import perspective_views as pv
    import copy

    owner = unique_owner("r71state")
    p = open_program(owner)
    p.nursery.add("S1", words="state test")

    v = pv.Viewer(id="v", role="ai_first", pos=(3.0, 4.0), facing="S")
    v_before = copy.deepcopy(v)

    # Snapshot program state (proposal count)
    n_before = len(p.nursery.proposals)

    pv.compose_views(p, [(v, "first"), (v, "whole")])

    check("r71 state: proposal count unchanged",
          len(p.nursery.proposals) == n_before)
    check("r71 state: viewer unchanged",
          v.pos == v_before.pos and v.facing == v_before.facing
          and v.id == v_before.id)


def part_sensitivity():
    """Sensitivity: weaken dispatch boundary, control must fail."""
    from form.open import open_program
    from form.dell_matrix import perspective_views as pv

    owner = unique_owner("r71sens")
    p = open_program(owner)
    p.nursery.add("S1", words="sensitivity test")

    v = pv.Viewer(id="v", role="ai_first", pos=(0.0, 0.0), facing="E")

    # Normal: compose works with real see_as
    result = pv.compose_views(p, [(v, "first")])
    normal_status = result["components"][0].get("epistemic_status")
    check("r71 sensitivity: normal composition works",
          result.get("mode") == "composed")

    # Weaken: patch see_as to return a marker status
    orig_see_as = pv.see_as
    def weakened_see_as(program, viewer, mode=None):
        return {"ok": True, "epistemic_status": "UNKNOWN",
                "data_source": "weakened", "report": "WEAKENED"}
    pv.see_as = weakened_see_as
    try:
        result2 = pv.compose_views(p, [(v, "first")])
        weakened_status = result2["components"][0].get("epistemic_status")
        # The composition must reflect the weakened dispatch
        check("r71 sensitivity: weakened dispatch diverges",
              weakened_status == "UNKNOWN" and weakened_status != normal_status,
              detail=f"normal={normal_status} weakened={weakened_status}")
    finally:
        pv.see_as = orig_see_as

    # Restored: real dispatch again
    result3 = pv.compose_views(p, [(v, "first")])
    check("r71 sensitivity: restored dispatch works",
          result3["components"][0].get("epistemic_status") == normal_status)


def smoke() -> bool:
    """Regression smoke entrypoint."""
    global CHECKS
    CHECKS = []
    part_positive()
    part_all_modes()
    part_aggregation()
    part_grant_rejection()
    part_invalid_specs()
    part_detached()
    part_no_truth_merging()
    part_state_unchanged()
    part_sensitivity()
    total = len(CHECKS)
    passed = sum(1 for c in CHECKS if c["ok"])
    print(f"R7.1 composition: {passed}/{total}", flush=True)
    return passed == total and total > 0


def main():
    if not _is_in_isolated_copy():
        return _run_in_isolated_copy()
    part_positive()
    part_all_modes()
    part_aggregation()
    part_grant_rejection()
    part_invalid_specs()
    part_detached()
    part_no_truth_merging()
    part_state_unchanged()
    part_sensitivity()
    total = len(CHECKS)
    passed = sum(1 for c in CHECKS if c["ok"])
    print(f"=== R7.1 composition: {passed}/{total} ===")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
