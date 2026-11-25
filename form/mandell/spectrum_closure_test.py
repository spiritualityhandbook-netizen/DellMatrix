#!/usr/bin/env python3
"""Exact 80-99 + predicate parity + persistence classification."""
from __future__ import annotations

from form.open import open_program
from form.mandell.executor import execute_seed
from form.persist import serialize
from form.persist_core_ii import CORE_II_DURABLE


def smoke() -> bool:
    print("=== SPECTRUM CLOSURE ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" | {detail}" if detail and not ok else ""))
        r.append(bool(ok))

    p = open_program("Ref")
    execute_seed(p, "55[Set] :: k=1")
    execute_seed(p, "81[Reference] :: k")
    rec("reference_does_not_copy", p.core_ii.refs.get("k") == "k" and p.core_ii.store.get("copy_k") is None)

    p = open_program("Grp")
    execute_seed(p, "51[Select]")
    execute_seed(p, "82[Group] :: g1")
    members = list(p.core_ii.groups.get("g1") or [])
    execute_seed(p, "83[Ungroup] :: g1")
    rec("group_ungroup_roundtrip", "g1" not in p.core_ii.groups and members)

    p = open_program("Cpy")
    execute_seed(p, "55[Set] :: k=1")
    execute_seed(p, "84[Copy] :: k")
    p.core_ii.store["k"] = "2"
    rec("copy_independent_from_source", p.core_ii.store.get("copy_k") == "1" and p.core_ii.store.get("k") == "2")

    p = open_program("Mv")
    execute_seed(p, "55[Set] :: k=1")
    execute_seed(p, "85[Move] :: k>y")
    rec("move_no_duplicate_ownership", "k" not in p.core_ii.store and p.core_ii.store.get("y") == "1")

    p = open_program("Del")
    out = execute_seed(p, "86[Delete] :: missing")
    rec("delete_explicit_not_silent", out.get("ok") is False and "delete_missing" in (out.get("error") or ""))

    p = open_program("Rep")
    execute_seed(p, "55[Set] :: k=old")
    execute_seed(p, "87[Replace] :: k>z")
    rec("replace_atomic", "k" not in p.core_ii.store and p.core_ii.store.get("z") == "old")
    execute_seed(p, "96[Revert]")
    rec("replace_rollback_capable", p.core_ii.store.get("k") == "old")

    p = open_program("Pat")
    execute_seed(p, "55[Set] :: k=old")
    execute_seed(p, "88[Patch] :: k=new")
    rec("patch_targeted", p.core_ii.store.get("k") == "new")
    execute_seed(p, "96[Revert]")
    rec("patch_rollback_capable", p.core_ii.store.get("k") == "old")

    p = open_program("Df")
    execute_seed(p, "55[Set] :: k=1")
    execute_seed(p, "88[Patch] :: k=2")
    execute_seed(p, "89[Diff]")
    rec("diff_machine_readable", isinstance(p.core_ii.last_diff.get("changed"), list) and "before" in p.core_ii.last_diff and "after" in p.core_ii.last_diff)

    p = open_program("Tr")
    execute_seed(p, "80[Context] :: frame")
    execute_seed(p, "90[Trace]")
    rec("trace_ordered", len(p.core_ii.traces) >= 2)

    p = open_program("Tx")
    execute_seed(p, "55[Set] :: k=1")
    execute_seed(p, "93[Try]")
    rec("try_creates_real_checkpoint", any(f.get("status") == "open" and f.get("checkpoint") for f in p.core_ii.tx))
    execute_seed(p, "88[Patch] :: k=bad")
    execute_seed(p, "91[false]")
    execute_seed(p, "94[Catch]")
    rec("failure_reaches_catch", any(f.get("status") == "caught" for f in p.core_ii.tx))
    rec("catch_keeps_error_history", bool(p.core_ii.traces))

    p = open_program("Cm")
    execute_seed(p, "55[Set] :: k=1")
    execute_seed(p, "93[Try]")
    execute_seed(p, "88[Patch] :: k=2")
    execute_seed(p, "95[Commit]")
    rec("commit_accepts_staged_change", p.core_ii.store.get("k") == "2" and any(f.get("status") == "committed" for f in p.core_ii.tx))
    out = execute_seed(p, "96[Revert]")
    rec("committed_not_reverted_by_unrelated_revert", p.core_ii.store.get("k") == "2" and out.get("error") == "unrelated_revert")

    p = open_program("Rb")
    execute_seed(p, "55[Set] :: k=1")
    execute_seed(p, "93[Try]")
    execute_seed(p, "87[Replace] :: k>z")
    execute_seed(p, "96[Revert]")
    rec("revert_restores_exact_transaction_state", p.core_ii.store.get("k") == "1" and "z" not in p.core_ii.store)

    p = open_program("Nest")
    execute_seed(p, "55[Set] :: k=1")
    execute_seed(p, "93[Try]")
    execute_seed(p, "93[Try]")
    execute_seed(p, "88[Patch] :: k=inner")
    execute_seed(p, "96[Revert]")
    rec("nested_transaction_ownership", p.core_ii.store.get("k") == "1" and sum(1 for f in p.core_ii.tx if f.get("status") == "open") == 1)

    p = open_program("Def")
    execute_seed(p, "97[Define] :: Wave=80>90")
    rec("define_retrievable", p.core_ii.defs.get("Wave") == "80>90")
    out = execute_seed(p, "98[Alias] :: W=Wave")
    rec("alias_resolves_existing", p.core_ii.aliases.get("W") == "Wave" and out.get("ok") is not False)
    out = execute_seed(p, "98[Alias] :: A=B")
    rec("alias_missing_target_fails", out.get("error") == "alias_missing")
    execute_seed(p, "98[Alias] :: A=Wave")
    out = execute_seed(p, "98[Alias] :: Wave=A")
    rec("alias_cycle_fails", out.get("error") == "alias_cycle")

    p = open_program("Cmp")
    out = execute_seed(p, "99[Compose] :: Path=80>90")
    rec("compose_parse_validated", "Path" in p.core_ii.compositions)
    rec("compose_executable", out.get("ok") is not False)
    rec("compose_preserves_dell_order", [x.split("[")[0] for x in p.core_ii.traces if x[:2] in ("80", "90")] == ["80", "90"])
    out = execute_seed(p, "99[Compose] :: Bad=not_a_dell")
    rec("malformed_composition", out.get("error") == "malformed_composition")

    p = open_program("Prd")
    execute_seed(p, "51[Select]")
    execute_seed(p, "52[Filter] :: welcome")
    execute_seed(p, "58[Match] :: welcome")
    execute_seed(p, "67[Any] :: welcome")
    execute_seed(p, "73[Threshold] :: gte:count 1")
    execute_seed(p, "60[last_result] > 80[TrueArm] > 91[true]")
    rec("predicate_circuit_end_to_end", p.core_ii.last_assert == "PASS")

    p = open_program("Obj")
    execute_seed(p, "55[Set] :: k=1")
    execute_seed(p, "81[Reference] :: k")
    execute_seed(p, "84[Copy] :: k")
    execute_seed(p, "88[Patch] :: k=2")
    execute_seed(p, "89[Diff]")
    execute_seed(p, "90[Trace]")
    rec("object_circuit_end_to_end", p.core_ii.store.get("k") == "2" and p.core_ii.refs.get("k") == "k")

    p = open_program("NoLeak")
    execute_seed(p, "54[Query]")
    blob = serialize(p).get("core_ii") or {}
    rec("no_derived_result_leak", "_last_result" not in (blob.get("store") or {}) and "last_result" not in blob)
    rec("no_control_frame_leak", "frames" not in blob and "last_control" not in blob and "tx" not in blob)
    rec("limit_not_durable", "limit" not in blob)
    rec("snapshots_not_durable", "snapshots" not in blob and "staged" not in blob)
    rec("durable_set_stable", set(CORE_II_DURABLE) == {
        "scope", "selected", "store", "groups", "defs", "aliases",
        "compositions", "weights", "context", "route", "refs",
        "causes", "deps", "last_assert", "last_guard",
    })
    p = open_program("LR")
    execute_seed(p, "54[Query]")
    rec("last_result_present_runtime", bool(p.core_ii.last_result))
    rec("store_user_durable_not_auto_derived", "_last_result" not in p.core_ii.store)

    from form.mandell.control_runtime import eval_condition
    from form.mandell.predicate import eval_predicate
    p = open_program("PredAuth")
    execute_seed(p, "51[Select]")
    rec("single_predicate_authority", eval_condition(p.core_ii, p, "any:welcome") == bool(eval_predicate(p.core_ii, p, "any:welcome").get("matched")))

    p = open_program("NoLeak2")
    execute_seed(p, "73[Threshold] :: gte:count 0")
    rec("no_derived_store_leak", "_threshold" not in p.core_ii.store and "_last_result" not in p.core_ii.store)

    p = open_program("CopyMut")
    execute_seed(p, "80[Context] :: copy")
    p.core_ii.store["k"] = ["a"]
    execute_seed(p, "84[Copy] :: k")
    p.core_ii.store["copy_k"].append("b")
    rec("copy_mutable_independence", p.core_ii.store["k"] == ["a"] and p.core_ii.store["copy_k"] == ["a", "b"])

    p = open_program("FailCk")
    execute_seed(p, "55[Set] :: k=1")
    snaps = len(p.core_ii.snapshots)
    execute_seed(p, "86[Delete] :: missing")
    rec("failed_mutation_no_checkpoint", len(p.core_ii.snapshots) == snaps)

    p = open_program("DiffImm")
    execute_seed(p, "55[Set] :: a=1")
    execute_seed(p, "55[Set] :: b=1")
    execute_seed(p, "88[Patch] :: b=2")
    execute_seed(p, "89[Diff]")
    rec("diff_immediate_baseline", p.core_ii.last_diff.get("changed") == ["b"] and p.core_ii.last_diff.get("baseline") == "immediate")

    p = open_program("DiffTx")
    execute_seed(p, "55[Set] :: a=1")
    execute_seed(p, "93[Try]")
    execute_seed(p, "88[Patch] :: a=2")
    execute_seed(p, "89[Diff]")
    rec("diff_transaction_baseline", p.core_ii.last_diff.get("baseline") == "transaction" and "a" in p.core_ii.last_diff.get("changed"))

    p = open_program("DiffClean")
    execute_seed(p, "55[Set] :: a=1")
    execute_seed(p, "88[Patch] :: a=2")
    execute_seed(p, "55[Set] :: b=1")
    execute_seed(p, "88[Patch] :: b=2")
    execute_seed(p, "89[Diff]")
    rec("diff_no_snapshot_contamination", p.core_ii.last_diff.get("changed") == ["b"])

    p = open_program("TxOC")
    execute_seed(p, "55[Set] :: k=1")
    execute_seed(p, "93[Try]")
    execute_seed(p, "88[Patch] :: k=2")
    execute_seed(p, "95[Commit]")
    rec("tx_open_commit", p.core_ii.store.get("k") == "2" and p.core_ii.tx[-1]["status"] == "committed")

    p = open_program("TxOR")
    execute_seed(p, "55[Set] :: k=1")
    execute_seed(p, "93[Try]")
    execute_seed(p, "88[Patch] :: k=2")
    execute_seed(p, "96[Revert]")
    rec("tx_open_revert", p.core_ii.store.get("k") == "1" and p.core_ii.tx[-1]["status"] == "reverted")

    p = open_program("TxFC")
    execute_seed(p, "55[Set] :: k=1")
    execute_seed(p, "93[Try]")
    execute_seed(p, "91[false]")
    rec("tx_failure_sets_failed", p.core_ii.tx[-1]["status"] == "failed")
    execute_seed(p, "94[Catch]")
    rec("tx_failure_catch", p.core_ii.tx[-1]["status"] == "caught")

    p = open_program("TxNext")
    execute_seed(p, "55[Set] :: k=1")
    execute_seed(p, "93[Try]")
    execute_seed(p, "88[Patch] :: k=bad")
    execute_seed(p, "91[false]")
    execute_seed(p, "94[Catch]")
    execute_seed(p, "96[Revert]")
    rec("tx_catch_next_transition", p.core_ii.store.get("k") == "1" and p.core_ii.tx[-1]["status"] == "reverted")

    p = open_program("TxNestR")
    execute_seed(p, "55[Set] :: k=1")
    execute_seed(p, "93[Try]")
    execute_seed(p, "88[Patch] :: k=outer")
    execute_seed(p, "93[Try]")
    execute_seed(p, "88[Patch] :: k=inner")
    execute_seed(p, "96[Revert]")
    rec("tx_nested_inner_revert", p.core_ii.store.get("k") == "outer" and sum(1 for f in p.core_ii.tx if f.get("status") == "open") == 1)

    p = open_program("TxNestC")
    execute_seed(p, "55[Set] :: k=1")
    execute_seed(p, "93[Try]")
    execute_seed(p, "88[Patch] :: k=outer")
    execute_seed(p, "93[Try]")
    execute_seed(p, "88[Patch] :: k=inner")
    execute_seed(p, "95[Commit]")
    rec("tx_nested_inner_commit", p.core_ii.store.get("k") == "inner" and p.core_ii.tx[-1]["status"] == "committed" and p.core_ii.tx[0]["status"] == "open")

    p = open_program("TxRef")
    execute_seed(p, "55[Set] :: k=1")
    execute_seed(p, "93[Try]")
    execute_seed(p, "95[Commit]")
    out = execute_seed(p, "96[Revert]")
    rec("tx_committed_revert_refused", out.get("error") == "unrelated_revert")

    p = open_program("TxHist")
    execute_seed(p, "93[Try]")
    execute_seed(p, "95[Commit]")
    rec("tx_history_lifecycle", len(p.core_ii.tx) == 1 and p.core_ii.tx[0]["status"] == "committed" and p.core_ii.try_depth == 0)

    p = open_program("CycD")
    out = execute_seed(p, "99[Compose] :: Loop=Loop")
    rec("compose_direct_cycle", out.get("error") == "compose_cycle")

    p = open_program("CycI")
    execute_seed(p, "80[Context] :: cyc")
    p.core_ii.compositions["A"] = "B"
    p.core_ii.compositions["B"] = "A"
    out = execute_seed(p, "99[Compose] :: A")
    rec("compose_indirect_cycle", out.get("error") == "compose_cycle")

    p = open_program("CycA")
    execute_seed(p, "99[Compose] :: Path=80")
    execute_seed(p, "98[Alias] :: X=Path")
    out = execute_seed(p, "99[Compose] :: Path=X")
    rec("compose_alias_cycle", out.get("error") == "compose_cycle")

    p = open_program("CycN")
    execute_seed(p, "99[Compose] :: Leaf=80")
    execute_seed(p, "99[Compose] :: Wrap=Leaf")
    rec("compose_valid_nested", "Wrap" in p.core_ii.compositions and any(tr.startswith("80") for tr in p.core_ii.traces))

    p = open_program("CycB")
    execute_seed(p, "72[Limit] :: 1")
    p.core_ii.compositions["C"] = "80"
    p.core_ii.compositions["B"] = "C"
    p.core_ii.compositions["A"] = "B"
    out = execute_seed(p, "99[Compose] :: A")
    rec("compose_depth_bound", out.get("error") == "compose_depth" and not any(x.startswith("80") for x in p.core_ii.traces))

    p = open_program("LR2")
    execute_seed(p, "54[Query]")
    rec("last_result_transient_runtime", "last_result" not in (serialize(p).get("core_ii") or {}))

    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
