#!/usr/bin/env python3
"""Authority convergence and certification tests."""
from __future__ import annotations

import inspect
import os
import tempfile
import json

from form.mandell.seed import CELLS, define_cell, expand_cell, BULLET
from form.mandell import meta_runtime, language, canonical
from form.mandell.language import (
    dump_language, save_program_language, load_program_language,
    parse_directive, harvest_evidence, plan_from_evidence, LANGUAGE_VERSION,
)
from form.mandell.canonical import parse_directive_v2, compress_graph, expand_graph, cheat_project, freeze_program
from form.mandell.activation import GREEK, explain_dell
from form.mandell.latinmandell import explain, customize, export_customs
from form.mandell.meta_runtime import tokenless
from form.open import open_program
from form.mandell.executor import execute_seed
from form.mandell.floor import FLOOR

LARGE = "\n".join(
    ["02[Persona:Architect]", "53[Scope:M4]", "23[Lock:Floor]", "23[Lock:00_99]"]
    + [f"91[Assert:N{i}]" for i in range(40)]
    + [f"12[Test:T{i}]" for i in range(20)]
    + ["92[Guard:NO_UI]", "92[Guard:NO_NURSERY]", "20[Alpha]"]
)


def smoke() -> bool:
    print("=== MANDELL AUTHORITY CONVERGENCE ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" | {detail}" if detail and not ok else ""))
        r.append(bool(ok))

    src = inspect.getsource(meta_runtime.parse_directive)
    rec("single_directive_parser_authority", "parse_directive_v2" in inspect.getsource(language.parse_directive))
    rec("compat_wrapper_zero_semantic_logic", "parse_seed" not in src and "_ATOM" not in src)
    rec("large_directive_fixture", parse_directive_v2(LARGE)["ok"] is True and len(parse_directive_v2(LARGE)["nodes"]) >= 60)
    multi = parse_directive_v2("97[Define:Obj]\n:: first\n:: second")
    rec("multiline_define_fixture", "first" in (multi["nodes"][0].get("payload") or "") and "second" in (multi["nodes"][0].get("payload") or ""))
    rec("multiline_query_fixture", "q" in parse_directive_v2("54[Query:X]\n:: q")["nodes"][0]["payload"])
    rec("flow_only_lines", parse_directive_v2("08[Create]\n>\n12[Test]")["ok"] is True)
    rec("unknown_semantic_text_fails", parse_directive_v2("08[Create]\nthis line is semantic junk")["ok"] is False)
    g = parse_directive_v2(LARGE)
    rec("large_directive_roundtrip", [n["dell"] for n in expand_graph(compress_graph(g))["nodes"]] == [n["dell"] for n in g["nodes"]])
    rec("architect_status_roundtrip", expand_graph(compress_graph(parse_directive_v2("02[Persona:Architect]\n90[Trace:SHA]\n20[Alpha]")))["ok"])
    rec("m3_style_roundtrip", expand_graph(compress_graph(parse_directive_v2("97[Define:Objective]\n23[Lock:Floor]\n92[Guard:NO_UI]\n20[Alpha]")))["ok"])
    p = open_program("M4")
    fr = freeze_program(p)
    rec("freeze_schema", "plane" in fr and "core_ii" in fr and "mandell_language" in fr)
    origin = freeze_program(p)
    cheat_project(p, ["08[Create] :: z"], "cold")
    rec("cheat_exact_original_state_preserved", freeze_program(p) == origin)
    cheat_project(p, ["not_a_seed"], "cold")
    rec("cheat_failure_exact_original_state_preserved", freeze_program(p) == origin)
    CELLS.clear()
    define_cell("Inner", "12[Test]")
    define_cell("Wrap", "08[Create] > {{Inner}}")
    customize("m4lux", dell=9, sense="light")
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    save_program_language(p, path)
    CELLS.clear()
    q = load_program_language("M4", path)
    rec("program_save_load_cells", "Wrap" in CELLS)
    rec("program_save_load_nested_cells", [a.dell for a in expand_cell("Wrap").atoms] == [8, 12])
    rec("program_save_load_latin_custom", "m4lux" in export_customs())
    rec("program_save_load_language_version", dump_language()["version"] == LANGUAGE_VERSION)
    data = json.load(open(path))
    rec("transient_meta_state_not_persisted", "cheat_projections" not in data and "omni_report" not in data)
    save_program_language(q, path)
    rec("save_load_save_language_stable", json.load(open(path))["mandell_language"]["version"] == LANGUAGE_VERSION)
    os.remove(path)
    ev = harvest_evidence()
    rec("omni_harvest_evidence", all("contracts" in row and "authority" in row for row in ev))
    miss = dict(ev[0], contracts=[{"id": "x", "tested": False, "ready": False}])
    rec("evidence_missing_test", canonical.measured_route(miss)["factors"]["verification_confidence"] < canonical.measured_route(ev[0])["factors"]["verification_confidence"])
    more = dict(ev[0], edges=list(ev[0]["edges"]) + ["extra"])
    rec("evidence_dependency_change", canonical.measured_route(more)["factors"]["resonance"] > canonical.measured_route(ev[0])["factors"]["resonance"])
    rec("evidence_locked_domain", canonical.measured_route(dict(ev[0], locked_domains_touched=3))["factors"]["scope_interference"] == 4)
    rec("rename_locality_score_invariant", canonical.measured_route(ev[0])["value"] == canonical.measured_route(dict(ev[0], locality="zzzz"))["value"])
    rec("same_evidence_same_score", canonical.measured_route(ev[0])["value"] == canonical.measured_route(dict(ev[0]))["value"])
    rec("different_evidence_different_score", canonical.measured_route(ev[0])["value"] != canonical.measured_route(ev[-1])["value"])
    rec("resolution_recalculates_evidence", plan_from_evidence(ev, resolved=ev[0]["locality"])["chosen"] != ev[0]["locality"])
    families = ["08[Create] :: fam", "51[Select]", "60[true] > 08[Create] > 61[Join]", "80[Context:x]", "93[Try] > 95[Commit]"]
    rec("cheat_each_family", all(cheat_project(p, [s], "cold")["ok"] for s in families))
    rec("cell_authority_single", dump_language()["language_configuration"]["cell_authority"] == "seed.expand_cell")
    rec("latin_100", all(explain_dell(n)["ok"] for n in range(100)))
    rec("latin_unknown_no_invent", not explain("zzzxxyy").get("suggested_seeds"))
    rec("greek_floor", list(FLOOR) == ["Alpha", "Delta", "Omega", "Omni"])
    rec("greek_non_floor", GREEK["Lambda"]["floor_status"] == "not_floor")
    rec("moji_canonical_equivalence", tokenless("08[Create] > 08[Map] > 08[Keep]")["equivalent"] is True)
    rec("tokenless_corpus", tokenless("08[Create" + BULLET + "Map]")["equivalent"] is True)
    rec("metric_harness_deterministic", parse_directive_v2(LARGE)["semantic_hash"] == parse_directive_v2(LARGE)["semantic_hash"])
    rec("self_host_real_directive", parse_directive(LARGE)["ok"] is True and execute_seed(p, "12[Test]").get("ok") is not False)
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
