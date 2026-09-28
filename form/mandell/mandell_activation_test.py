#!/usr/bin/env python3
"""Mandell language activation gate. No product track."""
from __future__ import annotations

from form.mandell.floor import FLOOR, NOVA_MODE, assert_floor_intact
from form.mandell.registry import DELLS
from form.mandell.seed import BULLET, FLOW_OPS, MANDELLMOJI, parse_seed, define_cell, expand_cell, CELLS
from form.mandell.activation import (
    GREEK, cheat_project, temp_horizon, omni_report, semantic_hash, tokenless_report,
    emoji_expand, persist_cells, load_cells, explain_dell, parse_directive, broad_route, DIRECTIONS,
)
from form.mandell.latinmandell import customize, explain, export_customs


def smoke() -> bool:
    print("=== MANDELL ACTIVATION ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" | {detail}" if detail and not ok else ""))
        r.append(bool(ok))

    rec("floor_locked", list(FLOOR) == ["Alpha", "Delta", "Omega", "Omni"] and assert_floor_intact())
    rec("nova_not_floor", "Nova" not in FLOOR and "Cheat" in NOVA_MODE)
    rec("greek_floor_roles", all(GREEK[n]["floor_status"] == "floor" for n in ("Alpha", "Delta", "Omega", "Omni")))
    rec("lambda_sigma_not_floor", GREEK["Lambda"]["floor_status"] == "not_floor" and GREEK["Sigma"]["floor_status"] == "not_floor")
    cold = cheat_project("HEAD", "forward", "cold")
    warm = cheat_project("HEAD", "forward", "warm")
    hot = cheat_project("HEAD", "forward", "hot")
    rec("nova_cheat_cold_1", len(cold) == 1 and cold[0]["label"] == "PROJECTED_NOT_FACT")
    rec("nova_cheat_warm_2", len(warm) == 2)
    rec("nova_cheat_hot_3", len(hot) == 3 and hot[2]["iteration"] == 3)
    rec("hot_derived_from_prior", hot[1]["assumptions"] == [f"from:{hot[0]['candidate_state']}"])
    rec("cold1", temp_horizon("cold") == 1)
    rec("warm2", temp_horizon("warm") == 2)
    rec("hot3", temp_horizon("hot") == 3)
    report = omni_report()
    rec("omni_whole_language_inspection", report["floor"] == list(FLOOR) and report["dells"]["count"] == 100 and report["owned_nodes"] == [])
    rec("latin_known_root", (explain("create").get("roots") or [{}])[0].get("la") == "creare")
    customize("lumen", dell=9, sense="light made visible")
    rec("latin_customization", (explain("lumen").get("roots") or [{}])[0].get("dell") == 9)
    rec("latin_persistence_roundtrip", "lumen" in export_customs())
    rec("00_99_explainable", all(explain_dell(n)["ok"] for n in range(100)))
    rec("chain_emoji_roundtrip", parse_seed(emoji_expand("08[Create] " + MANDELLMOJI["Chain"] + " 12[Test]")).flows == [">"])
    rec("emoji_not_required", parse_seed("08[Create] > 12[Test]").ok)
    rec("flow_to", parse_seed("08[Create] > 12[Test]").flows == [">"])
    rec("flow_thru", parse_seed("08[Create] >> 12[Test]").flows == [">>"])
    rec("flow_over", parse_seed("08[Create] >>> 12[Test]").flows == [">>>"])
    rec("flow_by", parse_seed("08[Create] : 12[Test]").flows == [":"])
    rec("flow_towards", parse_seed("08[Create] :> 12[Test]").flows == [":>"])
    rec("flow_from", parse_seed("08[Create] <: 12[Test]").flows == ["<:"])
    rec("dynamic_flow", parse_seed("08[Create] <:> 12[Test]").flows == ["<:>"])
    rec("delta_flow", parse_seed("08[Create] <<[Delta] 12[Test]").flows == ["<<[Delta]"])
    rec("parser_flowset_eq_declared", set(FLOW_OPS) >= {">", ">>", ">>>", ":", ":>", "<:", "<:>", "<<[Delta]"})
    rec("manifest_set", parse_seed("08[Create" + BULLET + "Map]").ok)
    rec("chainlink", [a.dell for a in parse_seed("08[Create" + BULLET + "Map] > 12[Test" + BULLET + "Keep]").atoms] == [8, 12, 8, 12])
    rec("chainlink_cardinality_failure", "cardinality" in parse_seed("08[Create" + BULLET + "Map] > 12[Test" + BULLET + "Keep" + BULLET + "Loop]").error)
    define_cell("Complete", "35[Discover] > 18[Mirror] > 12[Test]")
    rec("cell_define", "Complete" in CELLS)
    rec("cell_expand", [a.dell for a in expand_cell("Complete").atoms] == [35, 18, 12])
    path = persist_cells("/tmp/dm/cells.json")
    CELLS.clear()
    rec("cell_persistence", load_cells(path) >= 1 and "Complete" in CELLS)
    verbose = "08[Create] > 08[Map] > 08[Keep]"
    compressed = "08[Create" + BULLET + "Map" + BULLET + "Keep]"
    tr = tokenless_report(verbose, compressed)
    rec("verbose_to_tokenless", tr["positive"] is True)
    rec("tokenless_to_canonical", tr["equivalent"] is True)
    rec("semantic_hash_equality", tr["semantic_hash_equal"] is True)
    rec("direction_each", DIRECTIONS == ("forward", "back", "side", "up", "down", "in", "out"))
    rec("hot_forward_three", len(cheat_project("HEAD", "forward", "hot")) == 3)
    rec("100_registered", len(DELLS) == 100)
    rec("100_parseable", all(parse_seed(f"{n:02d}[{DELLS[n]['name']}]") .ok for n in range(100)))
    plan = parse_directive("35[Discover] > 18[Mirror] > 12[Test] :: language_gate")
    rec("parse_real_architect_directive", plan["ok"] is True)
    rec("broad_mode_chooses_coherent_locality", broad_route(["cells", "cheat"])["chosen"] in ("cells", "cheat"))
    rec("broad_mode_does_not_chase_empty", broad_route([]).get("chosen") == "none")
    rec("self_host_plan_parseable", parse_seed("35[Discover] > 18[Mirror] > 12[Test] > 90[Trace]").ok)
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
