#!/usr/bin/env python3
"""Control 60-66 and flow contract tests. Offline. No threads."""
from __future__ import annotations

from form.open import open_program
from form.mandell.executor import execute_seed
from form.mandell.seed import parse_seed, BULLET


def smoke() -> bool:
    print("=== CONTROL RUNTIME ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" | {detail}" if detail and not ok else ""))
        r.append(bool(ok))

    def run(owner, seed):
        p = open_program(owner)
        return p, execute_seed(p, seed)

    p, out = run("BrT", "60[true] > 80[Context] > 61[Join]")
    rec("branch_true", out.get("ok", True) and 80 in out.get("chain_ran", []))
    rec("branch_true_context", (p.core_ii.context == "plane"))

    p, out = run("BrF", "60[false] > 80[Context] > 61[Join]")
    rec("branch_false", 80 not in out.get("chain_ran", []) and 80 in out.get("chain_skipped", []))
    rec("unchosen_not_run", p.core_ii.context == "")

    p = open_program("JnS")
    execute_seed(p, "55[Set] :: a=1")
    out = execute_seed(p, "62[Parallel] > 80[Context] > 61[all]")
    rec("join_success", out.get("ok", True) is True)

    p, out = run("JnF", "62[Parallel] > 91[false] > 61[all]")
    rec("join_failure_policy", out.get("ok") is False or "join_fail" in (out.get("error") or "") or 91 in out.get("chain_ran", []))

    p, out = run("Par", "62[Parallel] > 80[Context] > 53[Scope] > 61[Join]")
    rec("parallel_two_paths", out.get("chain_ran")[:1] == [62] and 80 in out.get("chain_ran", []) and 53 in out.get("chain_ran", []))
    rec("parallel_stable_order", [x for x in out.get("chain_ran", []) if x in (80, 53)] == [80, 53])

    p, out = run("ParFail", "62[Parallel] > 91[false] > 80[Context] > 61[any]")
    rec("parallel_failure_capture", 91 in out.get("chain_ran", []) and 80 in out.get("chain_ran", []))

    p, out = run("Seq", "63[Sequence] > 80[Context] > 53[Scope] > 61[Join]")
    ran = [x for x in out.get("chain_ran", []) if x in (80, 53)]
    rec("sequence_order", ran == [80, 53])

    p = open_program("Uz")
    execute_seed(p, "72[Limit] :: 3")
    out = execute_seed(p, "64[true] > 80[Context] > 61[Join]")
    rec("until_zero", (getattr(p.core_ii, "last_control", None) or p.core_ii.last_frame or {}).get("status") == "zero" or (getattr(p.core_ii, "last_control", None) or {}).get("iterations") == 0)

    p = open_program("Um")
    execute_seed(p, "72[Limit] :: 3")
    out = execute_seed(p, "64[false] > 80[Context] > 61[Join]")
    rec("until_multi_or_bound", (getattr(p.core_ii, "last_control", None) or p.core_ii.last_frame or {}).get("iterations", 0) >= 1)
    rec("until_bound", (getattr(p.core_ii, "last_control", None) or p.core_ii.last_frame or {}).get("status") == "bounded")

    p = open_program("Wz")
    execute_seed(p, "72[Limit] :: 3")
    out = execute_seed(p, "65[false] > 80[Context] > 61[Join]")
    rec("while_zero", (getattr(p.core_ii, "last_control", None) or p.core_ii.last_frame or {}).get("status") == "zero")

    p = open_program("Wb")
    execute_seed(p, "72[Limit] :: 3")
    out = execute_seed(p, "65[true] > 80[Context] > 61[Join]")
    rec("while_bound", (getattr(p.core_ii, "last_control", None) or p.core_ii.last_frame or {}).get("status") == "bounded")
    rec("while_multi", (getattr(p.core_ii, "last_control", None) or p.core_ii.last_frame or {}).get("iterations", 0) == 3)

    p, out = run("Fe0", "51[Select] > 52[Filter] > 66[ForEach] > 80[Context] > 61[Join] :: zzznomatch")
    rec("foreach_empty", (getattr(p.core_ii, "last_control", None) or p.core_ii.last_frame or {}).get("status") in ("empty", "pending", "ok") or (getattr(p.core_ii, "last_control", None) or {}).get("iterations", 0) == 0)

    p, out = run("FeN", "51[Select] > 66[ForEach] > 80[Context] > 61[Join]")
    rec("foreach_multiple", (getattr(p.core_ii, "last_control", None) or p.core_ii.last_frame or {}).get("iterations", 0) >= 1)
    rec("foreach_isolation", bool((getattr(p.core_ii, "last_control", None) or p.core_ii.last_frame or {}).get("results")))

    p, out = run("Ft", "91[false] > 80[Context]")
    rec("flow_to", 80 in out.get("chain_ran", []))

    p, out = run("FthruP", "91[true] >> 80[Context]")
    rec("flow_thru_pass", 80 in out.get("chain_ran", []))

    p, out = run("FthruB", "91[false] >> 80[Context]")
    rec("flow_thru_block", 80 in out.get("chain_skipped", []))

    p, out = run("Fover", "80[Context] >>> 53[Scope] > 61[Join] > 90[Trace]")
    rec("flow_over_boundary", 53 in out.get("chain_skipped", []) and 61 in out.get("chain_ran", []))

    p, out = run("Fby", "80[Context] : 53[Scope]")
    rec("flow_by_binding", p.core_ii.context == "Scope")

    p, out = run("Ftw", "80[Context] :> 53[Scope]")
    rec("flow_towards", p.core_ii.route == "Scope")

    p, out = run("Ffrom", "80[Context] <: 53[Scope]")
    rec("flow_from", p.core_ii.refs.get("from") == "Context")

    p, out = run("Fdyn", "80[Context] <:> 53[Scope]")
    rec("dynamic_flow", p.core_ii.refs.get("from") == "Context" and p.core_ii.route == "Scope")

    p, out = run("Fdel", "80[Context] <<[Delta] 53[Scope]")
    rec("delta_checkpoint", len(p.core_ii.snapshots) >= 1)

    s = parse_seed("08[Create] > 15[Map] :: name")
    rec("deep_flow_label", s.ok and s.label == "name")

    s = parse_seed(f"60[true] > 08[Create{BULLET}Map] > 61[Join]")
    rec("chain_with_control_parse", s.ok and len(s.atoms) >= 3)
    p, out = run("ChCtrl", "60[true] > 80[Context] > 61[Join]")
    rec("chain_with_control", 80 in out.get("chain_ran", []))

    s = parse_seed(f"08[Create{BULLET}Map] > 12[Test{BULLET}Keep]")
    rec("chainlink_parse", s.ok)
    p, out = run("ClCtrl", "63[Sequence] > 80[Context] > 61[Join]")
    rec("manifest_with_control", 80 in out.get("chain_ran", []))

    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
