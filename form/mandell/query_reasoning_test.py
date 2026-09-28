#!/usr/bin/env python3
"""Exact contracts for 51-59 and 67-79. One assertion per named contract."""
from __future__ import annotations

from form.open import open_program
from form.mandell.executor import execute_seed
from form.persist import serialize


def smoke() -> bool:
    print("=== QUERY REASONING ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" | {detail}" if (detail and not ok) else ""))
        r.append(bool(ok))

    def lr(p):
        return getattr(p.core_ii, "last_result", None) or {}

    p = open_program("Sel")
    execute_seed(p, "51[Select] :: zzznomatch")
    rec("select_does_not_fabricate_ids", p.core_ii.selected == [])

    p = open_program("Fil")
    execute_seed(p, "51[Select] :: zzznomatch")
    before = list(p.core_ii.selected)
    execute_seed(p, "52[Filter] :: welcome")
    rec("filter_never_adds_unselected_member", p.core_ii.selected == [] and before == [])

    p = open_program("Qry")
    execute_seed(p, "51[Select]")
    execute_seed(p, "54[Query] :: welcome")
    cell = lr(p)
    rec("query_returns_machine_readable_result", all(k in cell for k in ("value", "matched", "count", "source", "predicate", "confidence", "trace")))

    p = open_program("GetM")
    execute_seed(p, "56[Get] :: missing_key")
    rec("get_missing", lr(p).get("error") == "missing" and lr(p).get("value") is None)
    p = open_program("GetE")
    execute_seed(p, "55[Set] :: blank=")
    execute_seed(p, "56[Get] :: blank")
    rec("get_empty_distinct", lr(p).get("error") == "empty" and lr(p).get("value") == "")

    p = open_program("CmpN")
    execute_seed(p, "55[Set] :: a=2")
    execute_seed(p, "55[Set] :: b=10")
    execute_seed(p, "57[Compare] :: lt:a b")
    rec("compare_typed_numeric", lr(p).get("mode") == "number" and lr(p).get("matched") is True)
    p = open_program("CmpT")
    execute_seed(p, "55[Set] :: a=2")
    out = execute_seed(p, "57[Compare] :: lt:a hello")
    rec("compare_type_mismatch_explicit", out.get("error") == "type_mismatch" or lr(p).get("error") == "type_mismatch")

    p = open_program("Mch")
    execute_seed(p, "51[Select]")
    first = list(p.core_ii.selected)
    execute_seed(p, "58[Match] :: welcome")
    rec("match_deterministic", p.core_ii.selected == [i for i in first if "welcome" in str(i).lower()])

    p = open_program("Rt")
    execute_seed(p, "59[Route] :: alt")
    rec("route_standalone_functional", p.core_ii.route == "alt")

    p = open_program("Qe")
    execute_seed(p, "67[Any] :: welcome")
    rec("any_empty_false", lr(p).get("matched") is False)
    execute_seed(p, "68[All] :: welcome")
    rec("all_empty_true", lr(p).get("matched") is True)
    execute_seed(p, "69[None] :: welcome")
    rec("none_empty_true", lr(p).get("matched") is True)

    p = open_program("Cnt")
    execute_seed(p, "51[Select] :: zzznomatch")
    execute_seed(p, "70[Count]")
    rec("count_exact", lr(p).get("value") == 0 and lr(p).get("count") == 0)

    p = open_program("Mea")
    execute_seed(p, "51[Select]")
    execute_seed(p, "71[Measure] :: count:selected")
    rec("measure_has_unit_or_kind", lr(p).get("unit") == "count" and lr(p).get("measure_kind") == "selected")

    p = open_program("Lim")
    out = execute_seed(p, "72[Limit] :: -1")
    rec("limit_rejects_invalid", out.get("error") == "invalid_limit")
    execute_seed(p, "72[Limit] :: 64")
    rec("limit_accepts_64", p.core_ii.limit == "64")
    execute_seed(p, "72[Limit] :: 0")
    rec("limit_accepts_0", p.core_ii.limit == "0")

    p = open_program("Thr")
    execute_seed(p, "55[Set] :: score=10")
    execute_seed(p, "73[Threshold] :: gte:score 5")
    rec("threshold_actually_evaluates", lr(p).get("matched") is True)

    p = open_program("Wnf")
    out = execute_seed(p, "74[Weight] :: bad=inf")
    rec("weight_rejects_nonfinite", out.get("error") == "nonfinite_weight")

    p = open_program("Nrm")
    execute_seed(p, "74[Weight] :: A=2")
    execute_seed(p, "74[Weight] :: B=1")
    execute_seed(p, "75[Normalize]")
    wa, wb = p.core_ii.weights.get("A"), p.core_ii.weights.get("B")
    rec("normalize_keys_preserved", set(p.core_ii.weights) >= {"A", "B"})
    rec("normalize_sum_approx_1", abs((wa or 0) + (wb or 0) - 1.0) < 1e-6)
    rec("normalize_ratio", abs((wa or 0) - 2.0 / 3.0) < 1e-4 and abs((wb or 0) - 1.0 / 3.0) < 1e-4)
    p = open_program("Nz")
    execute_seed(p, "75[Normalize]")
    rec("normalize_zero_set_defined", lr(p).get("error") == "zero_set")

    p = open_program("Res")
    execute_seed(p, "76[Resolve] :: 8")
    rec("resolve_confidence_bounded", 0.0 <= float(lr(p).get("confidence") or 0) <= 1.0)

    p = open_program("Inf")
    execute_seed(p, "77[Infer] :: maybe")
    rec("infer_never_fact_without_evidence", lr(p).get("fact") is False and lr(p).get("projected") is True)

    p = open_program("Cau")
    execute_seed(p, "78[Cause] :: A>B")
    rec("cause_direction_preserved", p.core_ii.causes == [("A", "B")])
    execute_seed(p, "78[Cause] :: A>B")
    rec("cause_duplicate_explicit", lr(p).get("error") == "duplicate_relation" and p.core_ii.causes == [("A", "B")])
    out = execute_seed(p, "78[Cause] :: Z>Z")
    rec("cause_self_explicit", out.get("error") == "self_relation")
    out = execute_seed(p, "78[Cause] :: nopath")
    rec("cause_malformed_explicit", out.get("error") == "malformed_relation")

    p = open_program("Dep")
    execute_seed(p, "79[Depend] :: B>C")
    rec("depend_direction_preserved", p.core_ii.deps == [("B", "C")])
    execute_seed(p, "79[Depend] :: B>C")
    rec("depend_duplicate_explicit", lr(p).get("error") == "duplicate_relation")
    out = execute_seed(p, "79[Depend] :: X>X")
    rec("depend_self_explicit", out.get("error") == "self_relation")
    out = execute_seed(p, "79[Depend] :: nopath")
    rec("depend_malformed_explicit", out.get("error") == "malformed_relation")

    p = open_program("Pipe")
    execute_seed(p, "51[Select]")
    execute_seed(p, "52[Filter] :: welcome")
    execute_seed(p, "58[Match] :: welcome")
    execute_seed(p, "67[Any] :: welcome")
    execute_seed(p, "73[Threshold] :: gte:count 1")
    out = execute_seed(p, "60[last_result] > 80[TrueArm] > 61[Join]")
    rec("predicate_pipeline", p.core_ii.context == "TrueArm")
    rec("control_consumes_same_predicate_engine", 80 in out.get("chain_ran", []))

    p = open_program("Rpipe")
    execute_seed(p, "51[Select]")
    execute_seed(p, "54[Query]")
    execute_seed(p, "70[Count]")
    execute_seed(p, "71[Measure] :: count:selected")
    execute_seed(p, "57[Compare] :: gte:count 0")
    execute_seed(p, "73[Threshold] :: gte:count 0")
    execute_seed(p, "77[Infer] :: enough")
    rec("reasoning_pipeline_machine_readable", all(k in lr(p) for k in ("value", "source", "confidence", "trace")))
    rec("infer_after_pipeline_not_fact", lr(p).get("fact") is False)

    p = open_program("PersR")
    execute_seed(p, "78[Cause] :: A>B")
    execute_seed(p, "79[Depend] :: B>C")
    execute_seed(p, "74[Weight] :: A=2")
    blob = serialize(p).get("core_ii") or {}
    rec("persistence_durable_reasoning_state", blob.get("causes") == [["A", "B"]] or blob.get("causes") == [("A", "B")])
    rec("persistence_deps", blob.get("deps") == [["B", "C"]] or blob.get("deps") == [("B", "C")])
    rec("persistence_weights", blob.get("weights", {}).get("A") == 2)

    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
