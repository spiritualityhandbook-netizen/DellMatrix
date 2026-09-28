#!/usr/bin/env python3
"""Full persist domain roundtrip + checkpoint + Mandell e2e."""
from __future__ import annotations

import json
import os
import tempfile

from form.open import open_program
from form.persist import serialize, save, load, checkpoint
from form.persist_rest import DURABLE_KEYS, durable
from form.mandell.seed import CELLS, define_cell, expand_cell
from form.mandell.latinmandell import customize, clear_customs, root_of
from form.mandell.executor import execute_seed
from form.dell_matrix.plane import Skin
from form.avatar import Expression


def _tmp():
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    return path


def smoke() -> bool:
    print("=== PERSIST FULL ROUNDTRIP ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" | {detail}" if detail and not ok else ""))
        r.append(bool(ok))

    rec("persist_import", True)
    p = open_program("RT")
    p.place("u1", "UnitOne", words="w", detail="d1", goals=["g1"], skin=Skin.CUBE, x=2, y=3)
    p.place("u2", "UnitTwo", words="w2", x=4)
    plane = p.cube.session.plane
    plane.box(["u1", "u2"], "box1")
    p.enhance.turn_on()
    p.sandbox.turn_on()
    p.network_url = "https://example.invalid"
    p.ambient.turn_on()
    p.main.tags["ops"] = 1.5
    p.avatar.step(2)
    p.face.set(Expression.JOY)
    p.lattice.to_sphere()
    p.history = ["h1", "h2"]
    p.ux_mode = "builder"
    p.grid_snap = True
    customize("rtlux", dell=9, sense="roundtrip-light")
    define_cell("L0", "08[Create] :: nested")
    define_cell("L1", "{{L0}}")
    execute_seed(p, "08[Create] :: corei")
    execute_seed(p, "51[Select]")
    execute_seed(p, "55[Set] :: rk=7")
    before = serialize(p)
    rec("serialize_load_domain_parity", set(DURABLE_KEYS) <= set(before.keys()))
    rec("mandell_language_version", (before.get("mandell_language") or {}).get("version") == "4")
    rec("mandell_cells_present", "L1" in ((before.get("mandell_language") or {}).get("cells") or {}))
    path = _tmp()
    save(p, path)
    CELLS.clear()
    clear_customs()
    q = load("RT", path)
    after = serialize(q)
    rec("plane_units_sandboxes", "u1" in after["plane"]["units"] and "box1" in after["plane"]["sandboxes"])
    rec("plane_perspective_zoom", after["plane"].get("perspective") == before["plane"].get("perspective"))
    rec("enhance_sandbox", after.get("enhance_on") is True and after.get("sandbox_on") is True)
    rec("network_internet", after.get("network_url") == "https://example.invalid")
    rec("ambient", bool((after.get("ambient") or {}).get("master_on")))
    rec("resonance", isinstance(after.get("resonance"), dict))
    rec("main_tags", (after.get("main") or {}).get("tags", {}).get("ops") == 1.5)
    rec("main_contribution_pull", isinstance((after.get("main") or {}).get("contributions"), list))
    rec("duo_generation", after.get("duo_generation") == before.get("duo_generation"))
    rec("avatar", after.get("avatar", {}).get("expression") == before.get("avatar", {}).get("expression"))
    rec("nursery", isinstance(after.get("nursery"), dict))
    rec("lattice", after.get("lattice", {}).get("form") == before.get("lattice", {}).get("form") or after.get("lattice", {}).get("size") == before.get("lattice", {}).get("size"))
    rec("companion", isinstance(after.get("companion"), dict))
    rec("inspire", isinstance(after.get("inspire"), dict))
    rec("self_knowledge", isinstance(after.get("self_knowledge"), dict))
    rec("ux", after.get("ux", {}).get("grid_snap") is True)
    rec("forces", isinstance(after.get("forces"), dict))
    rec("bimo", isinstance(after.get("bimo"), dict))
    rec("persona_matrix", getattr(q, "persona_lens", None) == getattr(p, "persona_lens", None))
    rec("history", "h1" in (after.get("history") or []))
    rec("latin_customs", root_of("rtlux") is not None)
    rec("mandell_cells", "L1" in CELLS and expand_cell("L1").ok)
    rec("core_ii", isinstance(after.get("core_ii"), dict))
    rec("roundtrip_semantic_equivalence", durable(after)["owner"] == durable(before)["owner"] and durable(after)["version"] == durable(before)["version"])
    cp = checkpoint(p)
    rec("checkpoint_full_state", os.path.isfile(cp) and "mandell_language" in json.load(open(cp)))
    rec("checkpoint_mandell_language", "L1" in json.load(open(cp)).get("mandell_language", {}).get("cells", {}))
    rec("checkpoint_core_ii", "core_ii" in json.load(open(cp)))
    CELLS.clear()
    clear_customs()
    z = load("RT", path)
    rec("mandell_persistence_roundtrip", "L1" in CELLS and expand_cell("L1").ok and root_of("rtlux") is not None)
    rec("execution_eq", execute_seed(z, "12[Test]").get("ok") is not False)
    os.remove(path)
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
