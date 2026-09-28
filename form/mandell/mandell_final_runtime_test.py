#!/usr/bin/env python3
"""M5 final runtime closure tests."""
from __future__ import annotations

import inspect
import os
import tempfile
import json

from form.persist import serialize, save, load
from form.open import open_program
from form.mandell.seed import CELLS, define_cell
from form.mandell.language import (
    dump_language, harvest_evidence, discover_tests,
    save_program_language, large_directive_fixture, metrics,
)
from form.mandell.canonical import parse_directive_v2, compress_graph, expand_graph, freeze_program, cheat_project
from form.mandell import meta_runtime, canonical
from form.mandell.executor import execute_seed


def smoke() -> bool:
    print("=== MANDELL FINAL RUNTIME ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" | {detail}" if detail and not ok else ""))
        r.append(bool(ok))

    p = open_program("M5")
    define_cell("K", "08[Create] :: k")
    blob = serialize(p)
    rec("native_serialize_language", isinstance(blob.get("mandell_language"), dict))
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    save(p, path)
    rec("native_save_language", "mandell_language" in json.load(open(path)))
    CELLS.clear()
    q = load("M5", path)
    rec("native_load_language", "K" in CELLS)
    rec("no_post_save_json_patch_required", "attach_language" not in inspect.getsource(save_program_language))
    rec("directive_codec_authority", "compress_graph" in inspect.getsource(meta_runtime.compress_directive))
    big = large_directive_fixture()
    rec("large_directive_gt_10000_chars", len(big) > 10000)
    rec("real_directive_corpus", parse_directive_v2(big)["ok"] and expand_graph(compress_graph(parse_directive_v2(big)))["ok"])
    rec("no_silent_drop", parse_directive_v2("08[Create]\njunk text")["ok"] is False)
    found = discover_tests()
    rec("test_registry_discovery", any(x["file"] == "mandell_final_runtime_test.py" and x["exists"] for x in found))
    rec("missing_test_detection", any(x["file"] == "missing_mandell_cert_test.py" and x["exists"] is False for x in found))
    rec("new_test_discovery", any("final_runtime" in x["file"] for x in found))
    ev = harvest_evidence()
    rec("omni_derived_evidence", len(ev) >= 5)
    rec("broad_mode_evidence_only", meta_runtime.plan_cycle(["cells"]).get("error") == "string_list_scoring_forbidden")
    rec("rename_invariant", canonical.measured_route(ev[0])["value"] == canonical.measured_route(dict(ev[0], locality="zz"))["value"])
    rec("evidence_mutation_changes_rank", canonical.measured_route(dict(ev[0], edges=list(ev[0]["edges"])+["n"]))["value"] != canonical.measured_route(ev[0])["value"])
    m = metrics(p)
    rec("metric_ambiguity", m["ambiguity"]["sample_count"] >= 3)
    rec("metric_execution_accuracy", m["execution"]["sample_count"] >= 2)
    rec("metric_context_retention", m["context"]["sample_count"] >= 1)
    rec("metric_recursive_efficiency", m["recursive"]["sample_count"] >= 3)
    rec("metric_long_session_compression", m["compression"]["baseline"] > 10000)
    rec("metric_instruction_persistence", m["persistence"]["result"] == 1)
    rec("metric_not_hash_only", "execute_seed" in m["execution"]["method"])
    rec("freeze_native_parity", "mandell_language" in freeze_program(p) and "attach_language" not in inspect.getsource(freeze_program))
    rec("cheat_native_persistence_parity", cheat_project(p, ["08[Create] :: n5"], "cold")["origin_unchanged"] is True)
    rec("self_host_large_directive", parse_directive_v2(big)["ok"] and execute_seed(p, "12[Test]").get("ok") is not False)
    os.remove(path)
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
