#!/usr/bin/env python3
"""Canonical semantic engine tests."""
from __future__ import annotations

from form.mandell.seed import CELLS, BULLET, define_cell, expand_cell, link_cell, parse_seed
from form.mandell.canonical import (
    seed_graph, parse_directive_v2, compress_graph, expand_graph,
    cheat_project, freeze_program, measured_route, rank_evidence,
)
from form.mandell.activation import GREEK
from form.mandell.meta_runtime import tokenless, cell_expand
from form.open import open_program

M1 = "02[Persona:Architect]\n53[Scope:MANDELL]\n23[Lock:Floor]\n91[Assert:Alpha]\n92[Guard:NO_NURSERY]\n12[Test:Floor]\n20[Alpha]"
M2 = "02[Persona:Architect]\n53[Scope:Meta]\n97[Define:Objective]\n23[Lock:00_99]\n92[Guard:NO_UI]\n12[Test:CellDirectCycle]\n20[Alpha]"
STATUS = "02[Persona:Architect]\n80[Context:HEAD]\n90[Trace:SHA]\n12[Test:mandell_meta_runtime]\n20[Alpha]"


def smoke() -> bool:
    print("=== MANDELL CANONICAL ENGINE ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" | {detail}" if detail and not ok else ""))
        r.append(bool(ok))

    a = seed_graph("08[Create] > 12[Test]")
    b = parse_directive_v2("08[Create] > 12[Test]")
    rec("seed_and_directive_share_node_model", a["nodes"][0]["dell"] == b["nodes"][0]["dell"] == 8)
    CELLS.clear()
    define_cell("Inner", "12[Test]")
    define_cell("Seq", "08[Create] > {{Inner}}")
    rec("nested_cell_sequence", [x.dell for x in expand_cell("Seq").atoms] == [8, 12])
    define_cell("SetC", "08[Create" + BULLET + "Map" + BULLET + "Keep]")
    rec("nested_cell_set", [x.term for x in expand_cell("SetC").atoms] == ["Create", "Map", "Keep"])
    rec("nested_cell_chainlink", parse_seed("08[Create" + BULLET + "Map] > 12[Test" + BULLET + "Keep]").ok)
    link_cell("Loop", "Loop")
    rec("cell_cycle_canonical", expand_cell("Loop").error == "cell_cycle")
    rec("canonical_cell_parity", cell_expand("Seq").get("atoms") == [(8, "Create"), (12, "Test")])
    rec("real_m1_directive_fixture", parse_directive_v2(M1)["ok"] is True)
    rec("real_m2_directive_fixture", parse_directive_v2(M2)["ok"] is True)
    rec("real_architect_status_fixture", parse_directive_v2(STATUS)["ok"] is True)
    rec("multiline_payload", parse_directive_v2("97[Define:Obj] :: LINE")["nodes"][0]["payload"] == "LINE")
    g = parse_directive_v2(M1)
    rec("source_span_roundtrip", g["nodes"][0]["source_span"][1] > g["nodes"][0]["source_span"][0])
    rec("unparseable_not_silent", parse_directive_v2("this is not mandell").get("ok") is False)
    rec("m1_roundtrip", [n["dell"] for n in expand_graph(compress_graph(g))["nodes"]] == [n["dell"] for n in g["nodes"]])
    rec("m2_roundtrip", expand_graph(compress_graph(parse_directive_v2(M2)))["ok"] is True)
    rec("status_roundtrip", expand_graph(compress_graph(parse_directive_v2(STATUS)))["ok"] is True)
    red = parse_directive_v2("80[Context:X]\n80[Context:X]\n23[Lock:Floor]")
    rec("compression_reduces_when_redundancy_exists", compress_graph(red)["compressed_nodes"] < compress_graph(red)["source_nodes"])
    p = open_program("CANON")
    origin = freeze_program(p)
    core_i = cheat_project(p, ["08[Create] :: c1"], "cold")
    rec("cheat_core_i", core_i["origin_unchanged"] is True and "c1" in core_i["steps"][0]["candidate_next_state"]["units"])
    rec("cheat_original_unchanged", freeze_program(p) == origin)
    rec("cheat_core_ii", cheat_project(p, ["55[Set] :: k=9"], "cold")["steps"][0]["candidate_next_state"]["store"].get("k") == "9")
    rec("cheat_control", cheat_project(p, ["60[true] > 08[Create] > 61[Join]"], "cold")["ok"] is True)
    define_cell("Make", "08[Create] :: cellu")
    rec("cheat_cell", expand_cell("Make").ok)
    rec("cheat_cross_core", cheat_project(p, ["08[Create] :: z", "51[Select]"], "warm")["ok"] is True)
    rec("cheat_failure", cheat_project(p, ["not_a_seed"], "cold")["steps"][0]["projected_failure"] is True)
    rec("projection_delta_exact", bool(core_i["steps"][0]["predicted_delta"]["units_added"]))
    ev_a = {"locality": "cells", "contracts": [{"tested": True, "ready": True}, {"tested": True, "ready": True}], "edges": [1, 2], "shared": ["seed"], "downstream": ["codec"], "code_localities": ["seed"], "dependents": 1, "locked_domains_touched": 0}
    ev_b = {"locality": "docs", "contracts": [{"tested": False, "ready": False}], "edges": [], "shared": [], "downstream": [], "code_localities": ["docs"], "dependents": 1, "locked_domains_touched": 2}
    rec("measured_route_factors", measured_route(ev_a)["factors"]["closures"] == 2)
    rec("route_evidence_trace", "resonance" in measured_route(ev_a)["trace"])
    rec("dependency_changes_rank", rank_evidence([ev_b, ev_a])[0]["locality"] == "cells")
    rec("resolved_circuit_removed_from_rank", rank_evidence([ev_a])[0]["locality"] == "cells")
    rec("broad_cycle_before_after", rank_evidence([ev_a])[0]["route_value"] != rank_evidence([ev_b])[0]["route_value"])
    rec("broad_cycle_three_projection_maximum", len(cheat_project(p, ["08[Create] :: a", "08[Create] :: b", "08[Create] :: c", "08[Create] :: d"], "hot")["steps"]) == 3)
    rec("self_host_m3_fixture", parse_directive_v2(M1 + "\n12[Test:SelfHostM3Fixture]")["ok"] is True)
    rec("latin_canonical_graph", seed_graph("08[Create]")["ok"] is True)
    rec("greek_canonical_representation", GREEK["Alpha"]["floor_status"] == "floor")
    rec("moji_canonical_roundtrip", tokenless("08[Create] > 08[Map] > 08[Keep]")["equivalent"] is True)
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
