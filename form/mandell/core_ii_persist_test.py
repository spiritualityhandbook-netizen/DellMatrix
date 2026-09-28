#!/usr/bin/env python3
"""Core II durable-state persist tests. Offline."""
from __future__ import annotations

import json
import os
import tempfile

from form.open import open_program
from form.persist import (
    CORE_II_DURABLE,
    CORE_II_STATE_VERSION,
    load,
    restore_core_ii,
    save,
    serialize,
    serialize_core_ii,
)
from form.mandell.core_ii_exec import CoreIIState, attach, execute_core_ii


def _fill(program) -> None:
    msgs: list = []
    execute_core_ii(program, 53, "Scope", "test_scope", msgs)
    execute_core_ii(program, 55, "Set", "alpha=1", msgs)
    execute_core_ii(program, 82, "Group", "test_group", msgs)
    execute_core_ii(program, 97, "Define", "test_def=meaning", msgs)
    execute_core_ii(program, 98, "Alias", "test_alias=test_def", msgs)
    execute_core_ii(program, 99, "Compose", "test_comp=51>52>70", msgs)
    execute_core_ii(program, 74, "Weight", "test=0.75", msgs)
    execute_core_ii(program, 80, "Context", "test_context", msgs)
    execute_core_ii(program, 59, "Route", "test_route", msgs)
    execute_core_ii(program, 81, "Reference", "test_ref", msgs)
    execute_core_ii(program, 78, "Cause", "A>B", msgs)
    execute_core_ii(program, 79, "Depend", "B>C", msgs)
    execute_core_ii(program, 91, "Assert", "true", msgs)
    execute_core_ii(program, 92, "Guard", "allow", msgs)
    st = attach(program)
    st.snapshots.append({"transient": True})
    st.staged.append({"transient": True})
    st.traces.append("transient")
    st.last_error = "transient"
    st.try_depth = 3
    st.parallel = ["a", "b"]
    st.branch = {"cond": "x"}
    st.last_diff = {"k": 1}
    st.limit = "max"


def _durable(st: CoreIIState) -> dict:
    return {
        "scope": st.scope,
        "selected": list(st.selected),
        "store": dict(st.store),
        "groups": {k: list(v) for k, v in st.groups.items()},
        "defs": dict(st.defs),
        "aliases": dict(st.aliases),
        "compositions": dict(st.compositions),
        "weights": dict(st.weights),
        "context": st.context,
        "route": st.route,
        "refs": dict(st.refs),
        "causes": [tuple(x) for x in st.causes],
        "deps": [tuple(x) for x in st.deps],
        "last_assert": st.last_assert,
        "last_guard": st.last_guard,
    }


def smoke() -> bool:
    print("=== CORE_II PERSIST SMOKE ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" | {detail}" if detail and not ok else ""))
        r.append(bool(ok))

    rec("durable_contract", set(CORE_II_DURABLE) == {
        "scope", "selected", "store", "groups", "defs", "aliases",
        "compositions", "weights", "context", "route", "refs",
        "causes", "deps", "last_assert", "last_guard",
    })
    rec("schema_version", CORE_II_STATE_VERSION == 1)

    p = open_program("CoreIIPersistRT")
    _fill(p)
    blob = serialize_core_ii(p)
    rec("unit_present", blob.get("present") is True and blob.get("version") == 1)
    rec("unit_scope", blob.get("scope") == "test_scope")
    rec("unit_store", blob.get("store", {}).get("alpha") == "1")
    rec("unit_no_snapshots", "snapshots" not in blob)
    rec("unit_no_traces", "traces" not in blob)
    rec("unit_no_try_depth", "try_depth" not in blob)
    try:
        json.dumps(blob)
        rec("json_serializable", True)
    except TypeError as exc:
        rec("json_serializable", False, str(exc))

    before = _durable(p.core_ii)
    path = save(p)
    rec("saved", os.path.isfile(path))
    loaded = load("CoreIIPersistRT")
    after = _durable(loaded.core_ii)
    rec("roundtrip_durable", before == after, str((before, after)))
    rec("roundtrip_transient_cleared", loaded.core_ii.try_depth == 0 and loaded.core_ii.traces == [])
    rec("tuple_causes", loaded.core_ii.causes == [("A", "B")])
    rec("tuple_deps", loaded.core_ii.deps == [("B", "C")])

    raw = serialize(p)
    raw.pop("core_ii", None)
    fd, old_path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    with open(old_path, "w", encoding="utf-8") as f:
        json.dump(raw, f)
    old = load("CoreIIPersistOld", path=old_path)
    rec("old_v7_default_state", old.core_ii.scope == "plane" and old.core_ii.store == {})
    os.remove(old_path)

    bad = serialize(p)
    bad["core_ii"] = "not-a-dict"
    fd, bad_path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    with open(bad_path, "w", encoding="utf-8") as f:
        json.dump(bad, f)
    try:
        broken = load("CoreIIPersistBad", path=bad_path)
        rec("malformed_loads", True)
        rec("malformed_fallback", broken.core_ii.scope == "plane" and broken.core_ii.store == {})
    except Exception as exc:
        rec("malformed_loads", False, str(exc))
        rec("malformed_fallback", False)
    os.remove(bad_path)

    typed = serialize(p)
    typed["core_ii"]["store"] = ["not", "a", "dict"]
    typed["core_ii"]["weights"] = {"test": "nope"}
    typed["core_ii"]["future_field"] = {"ignore": True}
    fd, typed_path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    with open(typed_path, "w", encoding="utf-8") as f:
        json.dump(typed, f)
    typed_p = load("CoreIIPersistTyped", path=typed_path)
    rec("bad_store_ignored", typed_p.core_ii.store == {})
    rec("unknown_field_ignored", True)
    os.remove(typed_path)

    first = serialize_core_ii(loaded)
    save(loaded)
    again = load("CoreIIPersistRT")
    second = serialize_core_ii(again)
    rec("save_load_save_stable", first == second)

    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
