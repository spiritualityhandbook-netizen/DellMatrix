#!/usr/bin/env python3
"""Control closure tests. One contract per test. No weak ORs."""
from __future__ import annotations

from form.open import open_program
from form.mandell.executor import execute_seed
from form.mandell.seed import FLOW_OPS
from form.mandell.control_runtime import FLOW_CONTRACT
from form.persist import serialize
from form.persist_core_ii import CORE_II_DURABLE


def smoke() -> bool:
    print("=== CONTROL CLOSURE ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" | {detail}" if (detail and not ok) else ""))
        r.append(bool(ok))

    def ctrl(p):
        return getattr(p.core_ii, "last_control", None) or {}

    p = open_program("BTA")
    out = execute_seed(p, "60[true] > 80[TrueArm] > 59[Else] > 53[FalseArm] > 61[Join]")
    rec("branch_true_arm_exact", 80 in out.get("chain_ran", []) and 53 in out.get("chain_skipped", []))
    rec("branch_true_context", p.core_ii.context == "TrueArm")
    rec("branch_true_scope_untouched", p.core_ii.scope == "plane")

    p = open_program("BFA")
    out = execute_seed(p, "60[false] > 80[TrueArm] > 59[Else] > 53[FalseArm] > 61[Join]")
    rec("branch_false_arm_exact", 53 in out.get("chain_ran", []) and 80 in out.get("chain_skipped", []))
    rec("unchosen_arm_no_mutation", p.core_ii.context == "" and p.core_ii.scope == "FalseArm")

    p = open_program("BNE")
    out = execute_seed(p, "60[false] > 80[TrueArm] > 61[Join]")
    rec("branch_no_else", 80 in out.get("chain_skipped", []) and p.core_ii.context == "")

    p = open_program("BME")
    out = execute_seed(p, "60[true] > 80[TrueArm] > 59[Else] > 53[FalseArm] > 59[Else] > 90[Trace] > 61[Join]")
    rec("branch_multiple_else_failure", out.get("error") == "multiple_else")
    rec("multiple_else_no_true_arm", p.core_ii.context != "TrueArm")

    p = open_program("NBS")
    out = execute_seed(p, "63[Sequence] > 60[true] > 80[TrueArm] > 61[Join] > 61[Join]")
    rec("nested_branch_in_sequence", p.core_ii.context == "TrueArm" and 63 in out.get("chain_ran", []))

    p = open_program("NSB")
    out = execute_seed(p, "60[true] > 63[Sequence] > 80[TrueArm] > 61[Join] > 61[Join]")
    rec("nested_sequence_in_branch", p.core_ii.context == "TrueArm")

    p = open_program("NFB")
    out = execute_seed(p, "51[Select] > 66[ForEach] > 60[true] > 80[TrueArm] > 61[Join] > 61[Join]")
    rec("nested_branch_in_foreach", 80 in out.get("chain_ran", []) and 66 in out.get("chain_ran", []) and 60 in out.get("chain_ran", []))

    p = open_program("NBF")
    out = execute_seed(p, "60[true] > 51[Select] > 66[ForEach] > 80[TrueArm] > 61[Join] > 61[Join]")
    rec("nested_foreach_in_branch", 80 in out.get("chain_ran", []) and 66 in out.get("chain_ran", []) and 60 in out.get("chain_ran", []))

    p = open_program("NL")
    execute_seed(p, "72[Limit] :: 2")
    out = execute_seed(p, "64[false] > 63[Sequence] > 80[TrueArm] > 61[Join] > 61[Join]")
    rec("nested_loop", ctrl(p).get("kind") == "until" and int(ctrl(p).get("iterations") or 0) >= 1)

    p = open_program("NJO")
    out = execute_seed(p, "63[Sequence] > 60[true] > 80[TrueArm] > 61[Join] > 61[Join]")
    rec("nested_join_ownership", 61 in out.get("chain_ran", []))

    p = open_program("DB")
    out = execute_seed(
        p,
        "63[Sequence] > 63[Sequence] > 63[Sequence] > 63[Sequence] > 63[Sequence] > 80[TrueArm] > 61[Join] > 61[Join] > 61[Join] > 61[Join] > 61[Join]",
    )
    rec("depth_bound", out.get("error") == "depth_bound")

    p = open_program("Umut")
    execute_seed(p, "72[Limit] :: 8")
    out = execute_seed(p, "64[store_done] > 55[done] > 61[Join]")
    rec("until_condition_mutation", p.core_ii.store.get("done") == "1")
    rec("until_early_exit", ctrl(p).get("status") != "bounded" and ctrl(p).get("iterations") == 1)

    p = open_program("Wmut")
    execute_seed(p, "55[Set] :: go=1")
    execute_seed(p, "72[Limit] :: 8")
    out = execute_seed(p, "65[store_go] > 86[go] > 61[Join]")
    rec("while_condition_mutation", "go" not in p.core_ii.store)
    rec("while_early_exit", ctrl(p).get("status") != "bounded" and ctrl(p).get("iterations") == 1)

    p = open_program("Ubd")
    execute_seed(p, "72[Limit] :: 3")
    out = execute_seed(p, "64[false] > 80[TrueArm] > 61[Join]")
    rec("loop_bound_failure", ctrl(p).get("status") == "bounded" and out.get("error") == "bound_reached")

    p = open_program("ParD")
    out = execute_seed(p, "62[Parallel] > 80[TrueArm] > 53[FalseArm] > 61[Join]")
    rec("parallel_distinct_results", p.core_ii.context == "TrueArm" and p.core_ii.scope == "FalseArm")

    p = open_program("ParS")
    out = execute_seed(p, "62[Parallel] > 91[false] > 80[TrueArm] > 61[Join]")
    rec("parallel_sibling_failure", 91 in out.get("chain_ran", []) and p.core_ii.context == "TrueArm")

    p = open_program("FeI")
    out = execute_seed(p, "51[Select] > 66[ForEach] > 80[TrueArm] > 61[Join]")
    rec("foreach_member_identity", any(isinstance(item, dict) and item.get("member") for item in (ctrl(p).get("results") or [])))
    rec("foreach_context_restore", p.core_ii.context == "")

    p = open_program("FeF")
    out = execute_seed(p, "51[Select] > 66[ForEach] > 91[false] > 61[Join]")
    rec("foreach_failure_trace", any(isinstance(item, dict) and item.get("error") == "assert_fail" and item.get("member") for item in (ctrl(p).get("results") or [])))

    p = open_program("Ft")
    out = execute_seed(p, "91[false] > 80[TrueArm]")
    rec("flow_to", p.core_ii.context == "TrueArm")

    p = open_program("FthP")
    out = execute_seed(p, "91[true] >> 80[TrueArm]")
    rec("flow_thru_pass", p.core_ii.context == "TrueArm")

    p = open_program("FthB")
    out = execute_seed(p, "91[false] >> 80[TrueArm]")
    rec("flow_thru_block", 80 in out.get("chain_skipped", []) and p.core_ii.context == "")

    p = open_program("Fov")
    out = execute_seed(p, "80[TrueArm] >>> 53[FalseArm] > 61[Join]")
    rec("flow_over", 53 in out.get("chain_skipped", []) and 61 in out.get("chain_ran", []))

    p = open_program("Fby")
    out = execute_seed(p, "80[Context] : 53[Scope]")
    rec("flow_by", p.core_ii.context == "Scope")

    p = open_program("Ftw")
    out = execute_seed(p, "80[Context] :> 53[Scope]")
    rec("flow_towards", p.core_ii.route == "Scope")

    p = open_program("Ffr")
    out = execute_seed(p, "80[Context] <: 53[Scope]")
    rec("flow_from", p.core_ii.refs.get("from") == "Context")

    p = open_program("Fdy")
    out = execute_seed(p, "80[Context] <:> 53[Scope]")
    rec("dynamic_flow", p.core_ii.refs.get("from") == "Context" and p.core_ii.route == "Scope")

    p = open_program("Fdl")
    out = execute_seed(p, "80[Context] <<[Delta] 53[Scope]")
    rec("delta_flow", len(p.core_ii.snapshots) >= 1)

    p = open_program("Fdp")
    out = execute_seed(p, "80[Context] :: 53[Scope]")
    rec("deep_flow_by", p.core_ii.refs.get("deep") == "Scope")

    rec("flow_parser_runtime_parity", set(FLOW_OPS) == set(FLOW_CONTRACT))

    p = open_program("Pers")
    execute_seed(p, "60[true] > 80[TrueArm] > 61[Join]")
    blob = serialize(p).get("core_ii") or {}
    rec("transient_frames_not_persisted", "frames" not in blob and "last_control" not in blob and "flow_taken" not in blob)
    rec("durable_set_unchanged", set(CORE_II_DURABLE) == {
        "scope", "selected", "store", "groups", "defs", "aliases",
        "compositions", "weights", "context", "route", "refs",
        "causes", "deps", "last_assert", "last_guard",
    })

    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
