#!/usr/bin/env python3
"""Mandell meta-runtime machinery tests."""
from __future__ import annotations

from form.mandell.seed import CELLS, BULLET
from form.mandell.meta_runtime import (
    cell_define, cell_expand, persist_cell_graph, load_cell_graph,
    parse_directive, compress_directive, expand_directive, directive_delta,
    moji_expand, moji_render, MOJI_REGISTRY, tokenless,
    cheat_from_state, route_value, rank_routes, omni_scan, plan_cycle,
)
from form.mandell.latinmandell import explain, customize, export_customs
from form.mandell.activation import explain_dell
from form.open import open_program
from form.mandell.executor import execute_seed


def smoke() -> bool:
    print("=== MANDELL META RUNTIME ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" | {detail}" if detail and not ok else ""))
        r.append(bool(ok))

    CELLS.clear()
    cell_define("Loop", "cell:Loop")
    rec("cell_direct_cycle", cell_expand("Loop").get("error") == "cell_cycle")
    CELLS.clear()
    cell_define("A", "cell:B")
    cell_define("B", "cell:A")
    rec("cell_indirect_cycle", cell_expand("A").get("error") == "cell_cycle")
    CELLS.clear()
    cell_define("D", "90[Trace]")
    cell_define("C", "cell:D")
    cell_define("B2", "cell:C")
    cell_define("A2", "cell:B2")
    rec("cell_deep_nested", cell_expand("A2").get("atoms") == [(90, "Trace")])
    rec("cell_missing_reference", cell_expand("Nope").get("error") == "unknown cell Nope")
    cell_define("Flow", "08[Create] >> 12[Test]")
    rec("cell_flow_preservation", cell_expand("Flow").get("flows") == [">>"])
    cell_define("Set", "08[Create" + BULLET + "Map" + BULLET + "Keep]")
    rec("cell_manifestset_preservation", cell_expand("Set").get("atoms") == [(8, "Create"), (8, "Map"), (8, "Keep")])
    path = persist_cell_graph("/tmp/dm/cell_graph.json")
    CELLS.clear()
    load_cell_graph(path)
    rec("cell_persistence_graph", cell_expand("Flow").get("flows") == [">>"])

    rec("directive_single_line", parse_directive("35[Discover] > 12[Test]").get("ok") is True)
    multi = parse_directive("02[Persona:Architect]\n53[Scope:Meta]\n91[Assert:X]\n92[Guard:NO_UI]\n12[Test:T]\n20[Alpha]")
    rec("directive_multiline", multi["ok"] and len(multi["nodes"]) >= 5)
    rec("directive_preserves_guards", len(multi["guards"]) == 1)
    rec("directive_preserves_tests", len(multi["tests"]) == 1)
    rec("directive_malformed", parse_directive("not a directive").get("ok") is False)
    rec("directive_architect_status", parse_directive("02[Persona:Architect]\n90[Trace:SHA]\n20[Alpha]")["ok"] is True)
    rec("directive_master_block", parse_directive("97[Define:Objective]\n23[Lock:Floor]\n92[Guard:NO_NURSERY]\n20[Alpha]")["ok"] is True)
    ast = parse_directive("23[Lock:Floor]\n92[Guard:NO_UI]\n12[Test:A]\n20[Alpha]\n80[Context:X]\n80[Context:X]")
    comp = compress_directive(ast)
    rec("directive_critical_node_preservation", bool(comp["locks"] and comp["guards"] and comp["tests"] and comp["exit"]))
    rec("directive_roundtrip", expand_directive(comp).get("ok") is True)
    rec("directive_delta_against_head", any(n["manifest"].startswith("Test") for n in directive_delta(ast, parse_directive("23[Lock:Floor]\n12[Test:NEW]"))["added"]))
    rec("directive_compression_proof", comp["compressed_nodes"] <= comp["source_nodes"])

    rec("moji_registry", all("canonical" in v for v in MOJI_REGISTRY.values()))
    rec("moji_expand", moji_expand("08[Create] > 12[Test]") == "08[Create] > 12[Test]")
    rec("moji_render", isinstance(moji_render("08[Create] > 08[Map]"), str))
    rec("moji_semantic_roundtrip", tokenless("08[Create] > 08[Map] > 08[Keep]").get("equivalent") is True)
    ts = tokenless("08[Create] > 08[Map] > 08[Keep]")
    rec("tokenless_seed", ts["equivalent"] is True and ts["compressed_chars"] < ts["source_chars"])
    rec("tokenless_directive", tokenless("35[Discover] > 12[Test]")["ok"] is True)
    rec("tokenless_cell", tokenless("08[Create" + BULLET + "Keep]")["ok"] is True)
    rec("tokenless_cross_core", tokenless("08[Create] > 51[Select]")["equivalent"] is True)
    rec("tokenless_roundtrip", ts["semantic_hash_before"] == ts["semantic_hash_after"])

    st = {"units": {}, "store": {}}
    cold = cheat_from_state(st, ["08[Create] :: p1"], "cold")
    rec("cheat_real_state_cold", cold["ok"] and len(cold["steps"]) == 1 and "p1" in cold["steps"][0]["candidate_next_state"]["units"])
    warm = cheat_from_state(st, ["08[Create] :: p1", "55[Set] :: k=1"], "warm")
    rec("cheat_real_state_warm", warm["ok"] and warm["steps"][1]["candidate_next_state"]["store"].get("k") == "1")
    hot = cheat_from_state(st, ["08[Create] :: p1", "55[Set] :: k=1", "51[Select]"], "hot")
    rec("cheat_real_state_hot", hot["ok"] and len(hot["steps"]) == 3)
    rec("cheat_prior_state_dependency", hot["steps"][2]["assumptions"] == ["from_iter:2"])
    rec("cheat_no_mutation", hot["origin"] == st and st["units"] == {})
    rec("cheat_failure", cheat_from_state(st, ["not_a_seed"], "cold").get("ok") is False)

    a = {"locality": "cells", "closures": 4, "resonance": 3, "reuse": 2, "future_work_avoided": 2, "verification_confidence": 3, "movement": 1, "rework_risk": 1, "scope_interference": 1}
    b = dict(a, locality="docs", closures=1, resonance=1)
    rec("route_formula_exact", route_value(a).get("value") == (4*3*2*2*3)/(1*1*1))
    ranked = rank_routes([b, a])
    rec("route_different_inputs_different_scores", ranked[0]["locality"] == "cells" and ranked[0]["route_value"] != ranked[1]["route_value"])
    rec("route_tie_policy", rank_routes([a, dict(a, locality="aaa")])[0]["locality"] == "aaa")
    rec("route_invalid_factor", route_value({"closures": 1}).get("error") == "invalid_factor")
    rec("route_zero_denominator", route_value(dict(a, movement=0)).get("error") == "zero_denominator")

    CELLS.clear()
    cell_define("Z", "cell:Z")
    scan = omni_scan(["injected"])
    rec("omni_detects_injected_open_circuit", "injected" in scan["open_circuits"] and any(x.startswith("cell_cycle") for x in scan["open_circuits"]))
    CELLS.clear()
    rec("omni_clears_resolved_circuit", "cell_cycle:Z" not in omni_scan().get("open_circuits"))
    rec("omni_read_only", scan.get("owned_nodes") == [])
    plan = plan_cycle(["cell_cycle:Z", "docs"], resolved="docs")
    rec("planning_recalculate", plan["chosen"] != "docs")
    rec("planning_resolution_changes_route", plan["chosen"] != "docs")
    rec("planning_dependency_changes_route", plan_cycle(["cell_graph"], resolved=None)["chosen"] == "cell_graph")

    rec("latin_coverage_00_99", all(explain_dell(n)["ok"] for n in range(100)))
    rec("latin_compound", bool(explain("create grow").get("roots")))
    rec("latin_unknown", explain("zzzxxyy").get("ok") is True and not explain("zzzxxyy").get("suggested_seeds"))
    customize("lumen2", dell=9, sense="light")
    rec("latin_custom_persistence", "lumen2" in export_customs())

    p = open_program("SH")
    out = execute_seed(p, "35[Discover] > 18[Mirror] > 12[Test]")
    rec("self_host_simple", out.get("ok") is not False)
    cell_define("Plan", "08[Create] :: sh")
    rec("self_host_cell", cell_expand("Plan").get("ok") is True)
    rec("self_host_control", execute_seed(p, "60[true] > 08[Create] > 61[Join]").get("ok") is not False)
    execute_seed(p, "08[Create] :: x")
    out = execute_seed(p, "51[Select]")
    rec("self_host_cross_core", out.get("ok") is not False and "x" in p.core_ii.selected)
    rec("self_host_compressed_directive", parse_directive(tokenless("35[Discover] > 12[Test]")["compressed"]).get("ok") is True)

    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
