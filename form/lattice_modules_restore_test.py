#!/usr/bin/env python3
"""P0-R: lattice SnapModule registry persistence (Director 7085151190 item 2).

The lattice module registry (HarmonicLattice.modules) was lost at WRITE
time: _serialize_lattice emitted module IDs only and restore never read
the field, so after any save/load every SnapModule's kind/axis/index/
cell membership/meta were gone and snap_out returned False for every
pre-save module, while the module's cells survived as orphans.

Contract under test (Option B + lattice-local format marker):
  * writer emits versioned, lossless module records (modules_format=2):
    {id, kind, axis, index, meta, cells=[[h,v,f],...]} referencing the
    serialized lattice cells by verified coordinate;
  * restore validates the field STAGED, before any swap, and refuses
    typed (ProgramLoadError) on inconsistent IDs/keys/coords/overlaps
    and foreign-owner payloads; source bytes never change on refusal;
  * legacy rule: a NONEMPTY IDs-only modules field (no format marker)
    is IRRECOVERABLE -- fail closed, never fabricate modules from IDs;
    legacy absent/empty remains supported;
  * writer honesty: a module whose identity fields or meta cannot be
    represented in JSON fails the SAVE loudly before any bytes move.

Registration paths exercised are the only ones that exist
(latch_plane / snap_in; latch_plane has no production callers today --
this suite pins the persistence contract, it does not wire latch_plane).

Correction addendum (Director CORRECTION_REQUIRED 7088548924 + CORRECTION
CHOICE 7088582500 + clarification 7088600824): the writer must prove,
per module coordinate, before any bytes move -- (1) the coordinate
exists in lat.cells, (2) coordinate membership is valid with the
canonical lat.cells[coord] as the persisted cell (Option B shadow
binding stays legal; no object/content identity with mod.cells is
required), (3) no coordinate is claimed by two modules, (4) coordinate/
meta fields carry reader-compatible types and finite JSON values. Any
failure raises LatticeModuleSaveError pre-byte. snap_in and
rebuild_from_plane are NOT changed: their live overlap/orphan behavior
is a documented limitation the save refusal makes explicit. Sections
13-15 pin A/B/D/E of the choice.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import types

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from form.open import open_program
from form.persist import serialize, save, load, LatticeModuleSaveError
from form.persist_rest import ProgramLoadError
from form.dell_matrix.harmonic_lattice import Cell, SnapModule

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _tmp():
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    return path


def _sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _build(owner):
    """Program with two modules (one latch, one rich snap_in) + a loose cell."""
    p = open_program(owner)
    p.lattice.latch_plane("alpha-latch", axis="H", index=2, width=2, depth=2,
                          label_prefix="alpha")
    rich = Cell(h=9, v=9, f=1, content="payload-idea", label="rich",
                tags=["probe", "p0r"], members=["payload-idea"])
    p.lattice.snap_in(SnapModule(
        id="beta-rich", kind="lattice2d", axis="V", index=5,
        cells={(9, 9, 1): rich},
        meta={"source": "p0r-suite", "purpose": "registry-roundtrip"}))
    p.lattice.put(3, 3, 0, content="loose-cell", label="loose")
    return p


def _child(code, *args):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    out = subprocess.run([sys.executable, "-c", code, *args],
                         capture_output=True, text=True, cwd=ROOT, env=env,
                         timeout=120)
    if out.returncode != 0:
        raise RuntimeError(f"child failed rc={out.returncode}: {out.stderr.strip()[-400:]}")
    return json.loads(out.stdout.strip().splitlines()[-1])


_CHILD_INSPECT = r"""
import json, sys
from form.persist import load
p = load(sys.argv[1], path=sys.argv[2])
mods = {}
for mid, m in sorted(p.lattice.modules.items()):
    mods[mid] = {"kind": m.kind, "axis": m.axis, "index": m.index,
                 "meta": m.meta, "coords": sorted(list(c) for c in m.cells.keys())}
print(json.dumps({"modules": mods,
                  "cells": sorted(list(c) for c in p.lattice.cells.keys()),
                  "status_modules": sorted(p.lattice.status()["modules"])}))
"""

_CHILD_SNAPOUT = r"""
import json, sys
from form.persist import load
p = load(sys.argv[1], path=sys.argv[2])
before = sorted(list(c) for c in p.lattice.cells.keys())
ok = p.lattice.snap_out(sys.argv[3])
print(json.dumps({"snap_out": ok, "before": before,
                  "after": sorted(list(c) for c in p.lattice.cells.keys()),
                  "registry_after": sorted(p.lattice.modules.keys())}))
"""

_CHILD_LOAD = r"""
import json, sys
from form.persist import load
from form.persist_rest import ProgramLoadError
try:
    p = load(sys.argv[1], path=sys.argv[2])
    print(json.dumps({"refused": None, "modules": sorted(p.lattice.modules.keys())}))
except ProgramLoadError as e:
    print(json.dumps({"refused": "ProgramLoadError", "message": str(e)}))
"""


def _mutate(path, fn):
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    fn(data)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh)
    return _sha(path)


def _expect_refusal(rec, name, path, owner, sha_before):
    try:
        load(owner, path=path)
        rec(name, False, "load succeeded; expected ProgramLoadError")
        return
    except ProgramLoadError:
        pass
    except Exception as e:  # wrong refusal type is a contract failure
        rec(name, False, f"raised {type(e).__name__}, not ProgramLoadError")
        return
    rec(name, _sha(path) == sha_before, "refused typed but source bytes changed")


def smoke() -> bool:
    print("=== LATTICE MODULES RESTORE (P0-R) ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" | {detail}" if detail and not ok else ""))
        r.append(bool(ok))

    # ---- 1. clean round trip, cold (separate process) -------------------
    path = _tmp()
    p = _build("P0ROne")
    save(p, path)
    got = _child(_CHILD_INSPECT, "P0ROne", path)
    alpha = got["modules"].get("alpha-latch") or {}
    beta = got["modules"].get("beta-rich") or {}
    rec("roundtrip_registry_ids", sorted(got["modules"]) == ["alpha-latch", "beta-rich"],
        f"got {sorted(got['modules'])}")
    rec("roundtrip_alpha_fields", alpha.get("kind") == "lattice2d" and alpha.get("axis") == "H"
        and alpha.get("index") == 2 and alpha.get("meta") == {"width": 2, "depth": 2},
        f"alpha={alpha}")
    rec("roundtrip_alpha_coords", alpha.get("coords") == [[2, 0, 0], [2, 0, 1], [2, 1, 0], [2, 1, 1]],
        f"coords={alpha.get('coords')}")
    rec("roundtrip_beta_fields", beta.get("kind") == "lattice2d" and beta.get("axis") == "V"
        and beta.get("index") == 5
        and beta.get("meta") == {"source": "p0r-suite", "purpose": "registry-roundtrip"}
        and beta.get("coords") == [[9, 9, 1]], f"beta={beta}")
    rec("roundtrip_status_lists_modules", got["status_modules"] == ["alpha-latch", "beta-rich"],
        f"status={got['status_modules']}")

    out = _child(_CHILD_SNAPOUT, "P0ROne", path, "alpha-latch")
    rec("roundtrip_snapout_true", out["snap_out"] is True, f"snap_out={out['snap_out']}")
    rec("roundtrip_snapout_removes_exactly_module_cells",
        out["after"] == [[3, 3, 0], [9, 9, 1]] and out["registry_after"] == ["beta-rich"],
        f"after={out['after']} registry={out['registry_after']}")

    # ---- 2/3. rich payload equality + resave stability / permanence ----
    path2 = _tmp()
    save(_build("P0RTwo"), path2)
    q = load("P0RTwo", path=path2)
    rich = q.lattice.modules["beta-rich"].cells[(9, 9, 1)] if "beta-rich" in q.lattice.modules else None
    rec("roundtrip_rich_cell_payload", rich is not None and rich.content == "payload-idea"
        and rich.label == "rich" and list(rich.tags) == ["probe", "p0r"]
        and list(rich.members) == ["payload-idea"],
        "rich cell payload mismatch after reload")
    lat_before = serialize(q)["lattice"]
    path2b = _tmp()
    save(q, path2b)
    with open(path2b, "r", encoding="utf-8") as fh:
        lat_after = json.load(fh)["lattice"]
    rec("resave_lattice_section_stable", lat_after == lat_before,
        "save->load->save changed the lattice section")
    rec("resave_not_empty_registry", isinstance(lat_after.get("modules"), list)
        and len(lat_after["modules"]) == 2
        and all(isinstance(m, dict) for m in lat_after["modules"]),
        f"resaved modules field: {lat_after.get('modules')!r}")
    q2 = load("P0RTwo", path=path2b)
    rec("resave_registry_survives_second_load",
        sorted(q2.lattice.modules) == ["alpha-latch", "beta-rich"],
        f"second-load registry: {sorted(q2.lattice.modules)}")

    # ---- 4. legacy IDs-only: IRRECOVERABLE, fail closed ------------------
    path4 = _tmp()
    save(_build("P0RFour"), path4)
    sha4 = _mutate(path4, lambda d: (d["lattice"].__setitem__("modules", ["alpha-latch", "beta-rich"]),
                                     d["lattice"].pop("modules_format", None)))
    verdict = _child(_CHILD_LOAD, "P0RFour", path4)
    rec("legacy_ids_only_refuses_typed", verdict["refused"] == "ProgramLoadError",
        f"verdict={verdict}")
    rec("legacy_ids_only_bytes_preserved", _sha(path4) == sha4, "source bytes changed")

    # ---- 5. legacy absent/empty controls --------------------------------
    for name, fn in (
        ("legacy_modules_key_absent_loads", lambda d: (d["lattice"].pop("modules", None),
                                                       d["lattice"].pop("modules_format", None))),
        ("legacy_modules_empty_loads", lambda d: (d["lattice"].__setitem__("modules", []),
                                                  d["lattice"].pop("modules_format", None))),
        ("legacy_lattice_section_absent_loads", lambda d: d.pop("lattice", None)),
    ):
        pth = _tmp()
        save(_build("P0RFive"), pth)
        _mutate(pth, fn)
        try:
            qq = load("P0RFive", path=pth)
            rec(name, qq.lattice.modules == {}, f"registry={qq.lattice.modules}")
        except Exception as e:
            rec(name, False, f"raised {type(e).__name__}: {e}")

    # new-writer empty registry is NOT a legacy refusal
    pth = _tmp()
    save(open_program("P0REmpty"), pth)
    try:
        qq = load("P0REmpty", path=pth)
        rec("writer_empty_registry_loads", qq.lattice.modules == {}, f"registry={qq.lattice.modules}")
    except Exception as e:
        rec("writer_empty_registry_loads", False, f"raised {type(e).__name__}: {e}")

    # ---- 6. malformed-present controls (marker format) -------------------
    # Mutations install the intended format-2 state directly (valid record
    # templates with one defect each), so every case is meaningful against
    # any writer shape.
    def alpha_rec(**over):
        base = {"id": "alpha-latch", "kind": "lattice2d", "axis": "H", "index": 2,
                "meta": {"width": 2, "depth": 2},
                "cells": [[2, 0, 0], [2, 0, 1], [2, 1, 0], [2, 1, 1]]}
        base.update(over)
        return base

    def beta_rec(**over):
        base = {"id": "beta-rich", "kind": "lattice2d", "axis": "V", "index": 5,
                "meta": {"source": "p0r-suite", "purpose": "registry-roundtrip"},
                "cells": [[9, 9, 1]]}
        base.update(over)
        return base

    def with_records(records, fmt=2):
        def fn(d):
            if fmt is not None:
                d["lattice"]["modules_format"] = fmt
            else:
                d["lattice"].pop("modules_format", None)
            d["lattice"]["modules"] = records
        return fn

    def rec_mut(name, fn):
        pth = _tmp()
        save(_build("P0RSix"), pth)
        sha = _mutate(pth, fn)
        _expect_refusal(rec, name, pth, "P0RSix", sha)

    rec_mut("malformed_record_missing_id",
            with_records([{k: v for k, v in alpha_rec().items() if k != "id"}, beta_rec()]))
    rec_mut("malformed_id_wrong_type",
            with_records([alpha_rec(id=7), beta_rec()]))
    rec_mut("malformed_id_empty",
            with_records([alpha_rec(id=""), beta_rec()]))
    rec_mut("malformed_kind_wrong_type",
            with_records([alpha_rec(kind=7), beta_rec()]))
    rec_mut("malformed_index_bool",
            with_records([alpha_rec(index=True), beta_rec()]))
    rec_mut("malformed_meta_non_dict",
            with_records([alpha_rec(meta=["x"]), beta_rec()]))
    rec_mut("malformed_cells_bad_shape",
            with_records([alpha_rec(cells=[[2, 0]]), beta_rec()]))
    rec_mut("malformed_cells_bool_coord",
            with_records([alpha_rec(cells=[[True, 0, 0]]), beta_rec()]))
    rec_mut("malformed_modules_dict_under_marker",
            with_records({"alpha-latch": alpha_rec()}))
    rec_mut("malformed_modules_strings_under_marker",
            with_records(["alpha-latch", "beta-rich"]))
    rec_mut("malformed_record_extra_key",
            with_records([alpha_rec(surprise=1), beta_rec()]))
    rec_mut("malformed_duplicate_module_id",
            with_records([alpha_rec(), alpha_rec()]))
    rec_mut("malformed_dangling_coord",
            with_records([alpha_rec(cells=[[7, 7, 7]]), beta_rec()]))
    rec_mut("malformed_overlap_two_modules",
            with_records([alpha_rec(), beta_rec(cells=[[2, 0, 0]])]))
    rec_mut("malformed_unknown_format_marker",
            with_records([alpha_rec(), beta_rec()], fmt=3))
    rec_mut("malformed_records_without_marker",
            with_records([alpha_rec(), beta_rec()], fmt=None))
    rec_mut("malformed_foreign_owner_payload",
            with_records([alpha_rec(owner="Mallory"), beta_rec()]))

    # ---- 8. shadowed coordinate: Option B binding pinned -----------------
    p8 = open_program("P0REight")
    p8.lattice.put(5, 5, 0, content="pre-existing", label="native")
    shadow = Cell(h=5, v=5, f=0, content="shadow-payload", label="shadow")
    p8.lattice.snap_in(SnapModule(id="gamma-shadow", kind="lattice2d", axis="H",
                                  index=0, cells={(5, 5, 0): shadow}, meta={}))
    path8 = _tmp()
    save(p8, path8)
    q8 = load("P0REight", path=path8)
    mod8 = q8.lattice.modules.get("gamma-shadow")
    rec("shadowed_module_survives", mod8 is not None and sorted(mod8.cells) == [(5, 5, 0)],
        f"module={mod8}")
    rec("shadowed_binds_lattice_cell_optionB",
        mod8 is not None and mod8.cells[(5, 5, 0)].content == "pre-existing",
        "restored module must bind the lattice cell at the recorded coordinate")
    rec("shadowed_snapout_pinned", q8.lattice.snap_out("gamma-shadow") is True
        and (5, 5, 0) not in q8.lattice.cells,
        "snap_out of a restored shadow module removes its recorded coordinate")

    # ---- 9. cross-owner isolation control --------------------------------
    pathb = _tmp()
    save(_build("P0RBee"), pathb)
    try:
        qb = load("P0RBee", path=pathb)
        rec("cross_owner_other_file_unaffected",
            sorted(qb.lattice.modules) == ["alpha-latch", "beta-rich"],
            f"registry={sorted(qb.lattice.modules)}")
    except Exception as e:
        rec("cross_owner_other_file_unaffected", False, f"raised {type(e).__name__}: {e}")

    # ---- 12. writer honesty ----------------------------------------------
    bad = open_program("P0RBad")
    bad.lattice.snap_in(SnapModule(id="bad-meta", kind="lattice2d", axis="H", index=0,
                                   cells={}, meta={"oops": object()}))
    target = _tmp()
    save(_build("P0RGood"), target)
    sha_good = _sha(target)
    try:
        save(bad, target)
        rec("writer_unserializable_meta_refuses", False, "save succeeded with object() in meta")
    except Exception:
        rec("writer_unserializable_meta_refuses", _sha(target) == sha_good,
            "save refused but target bytes changed")
    bad2 = open_program("P0RBad2")
    bad2.lattice.snap_in(SnapModule(id="bad-meta2", kind="lattice2d", axis="H", index=0,
                                    cells={}, meta=["not-a-dict"]))
    try:
        save(bad2, _tmp())
        rec("writer_non_dict_meta_refuses", False, "save succeeded with list meta")
    except Exception:
        rec("writer_non_dict_meta_refuses", True)

    # ---- 13. closure A: rebuild-orphaned module refuses at save ----------
    # (Director 7088582500 item A: latch_plane then rebuild_from_plane
    # removing the module's cells; save must refuse typed, target SHA
    # identical, second owner unaffected. snap_in/rebuild unchanged.)
    path13o = _tmp()
    save(_build("P0ROther13"), path13o)
    p13 = open_program("P0RThirteen")
    p13.lattice.latch_plane("mod-orphan", axis="H", index=2, width=2, depth=2,
                            label_prefix="orphan")
    p13.lattice.rebuild_from_plane(types.SimpleNamespace(units={}))
    target13 = _tmp()
    save(_build("P0RGood13"), target13)
    sha13 = _sha(target13)
    try:
        save(p13, target13)
        rec("closure_rebuild_orphan_save_refuses_typed", False,
            "save succeeded with a module whose cells were rebuilt away")
    except LatticeModuleSaveError:
        rec("closure_rebuild_orphan_save_refuses_typed", True)
    except Exception as e:
        rec("closure_rebuild_orphan_save_refuses_typed", False,
            f"raised {type(e).__name__}, not LatticeModuleSaveError")
    rec("closure_rebuild_orphan_bytes_identical", _sha(target13) == sha13,
        "refused save changed the previous canonical file")
    try:
        qo13 = load("P0ROther13", path=path13o)
        rec("closure_second_owner_unaffected",
            sorted(qo13.lattice.modules) == ["alpha-latch", "beta-rich"],
            f"registry={sorted(qo13.lattice.modules)}")
    except Exception as e:
        rec("closure_second_owner_unaffected", False,
            f"raised {type(e).__name__}: {e}")
    # control: a module whose coordinate survives the rebuild round-trips
    p13b = open_program("P0RThirteenB")
    p13b.lattice.snap_in(SnapModule(
        id="mod-keep", kind="lattice2d", axis="H", index=0,
        cells={(6, 6, 0): Cell(h=6, v=6, f=0, content="keep", label="keep")},
        meta={}))
    unit13 = types.SimpleNamespace(x=6.0, y=6.0, label="keep")
    p13b.lattice.rebuild_from_plane(types.SimpleNamespace(units={"u1": unit13}))
    path13b = _tmp()
    try:
        save(p13b, path13b)
        q13b = load("P0RThirteenB", path=path13b)
        mod13b = q13b.lattice.modules.get("mod-keep")
        rec("closure_surviving_module_roundtrips",
            mod13b is not None and sorted(mod13b.cells) == [(6, 6, 0)],
            f"module={mod13b}")
    except Exception as e:
        rec("closure_surviving_module_roundtrips", False,
            f"raised {type(e).__name__}: {e}")

    # ---- 14. closure B + D: live overlap and poisoned meta refuse at save -
    # (Director 7088582500 items B/D: two live overlapping modules still
    # register in memory -- no mutation-time change is authorized -- but
    # the save refuses typed with identical bytes; non-finite meta is a
    # writer refusal too, original preserved.)
    p14 = open_program("P0RFourteen")
    p14.lattice.snap_in(SnapModule(
        id="mod-first", kind="lattice2d", axis="H", index=0,
        cells={(4, 4, 0): Cell(h=4, v=4, f=0, content="one", label="one")},
        meta={}))
    p14.lattice.snap_in(SnapModule(
        id="mod-second", kind="lattice2d", axis="H", index=0,
        cells={(4, 4, 0): Cell(h=4, v=4, f=0, content="two", label="two")},
        meta={}))
    rec("overlap_live_registers_both",
        sorted(p14.lattice.modules) == ["mod-first", "mod-second"],
        f"registry={sorted(p14.lattice.modules)}")
    target14 = _tmp()
    save(_build("P0RGood14"), target14)
    sha14 = _sha(target14)
    try:
        save(p14, target14)
        rec("overlap_save_refuses_typed", False,
            "save succeeded with two modules claiming one coordinate")
    except LatticeModuleSaveError:
        rec("overlap_save_refuses_typed", True)
    except Exception as e:
        rec("overlap_save_refuses_typed", False,
            f"raised {type(e).__name__}, not LatticeModuleSaveError")
    rec("overlap_save_bytes_identical", _sha(target14) == sha14,
        "refused save changed the previous canonical file")
    p14d = open_program("P0RFourteenD")
    p14d.lattice.snap_in(SnapModule(id="mod-nan", kind="lattice2d", axis="H",
                                    index=0, cells={},
                                    meta={"bad": float("nan")}))
    target14d = _tmp()
    save(_build("P0RGood14D"), target14d)
    sha14d = _sha(target14d)
    try:
        save(p14d, target14d)
        rec("poisoned_nan_meta_save_refuses_typed", False,
            "save succeeded with NaN in module meta (not finite JSON)")
    except LatticeModuleSaveError:
        rec("poisoned_nan_meta_save_refuses_typed", True)
    except Exception as e:
        rec("poisoned_nan_meta_save_refuses_typed", False,
            f"raised {type(e).__name__}, not LatticeModuleSaveError")
    rec("poisoned_nan_meta_bytes_unchanged", _sha(target14d) == sha14d,
        "refused save changed the previous canonical file")

    # ---- 15. closure E: every writer-accepted output loads ---------------
    # (Director 7088582500 item E: for each registry shape, save either
    # refuses typed (LatticeModuleSaveError) or the written file loads;
    # never save-succeeds + load-refuses.)
    def _closure(name, prog, owner):
        pth = _tmp()
        try:
            save(prog, pth)
        except LatticeModuleSaveError:
            rec(name, True)
            return
        except Exception as e:
            rec(name, False,
                f"save raised {type(e).__name__}, not LatticeModuleSaveError")
            return
        try:
            load(owner, path=pth)
            rec(name, True)
        except Exception as e:
            rec(name, False,
                f"writer accepted but loader refused: {type(e).__name__}: {e}")

    _closure("closure_property_clean", _build("P0REClean"), "P0REClean")
    p15s = open_program("P0REShadow")
    p15s.lattice.put(5, 5, 0, content="pre-existing", label="native")
    p15s.lattice.snap_in(SnapModule(
        id="gamma-shadow", kind="lattice2d", axis="H", index=0,
        cells={(5, 5, 0): Cell(h=5, v=5, f=0, content="shadow-payload",
                               label="shadow")}, meta={}))
    _closure("closure_property_shadowed", p15s, "P0REShadow")
    _closure("closure_property_empty", open_program("P0REEmpty"), "P0REEmpty")
    p15d = open_program("P0REDangle")
    p15d.lattice.latch_plane("mod-dangle", axis="H", index=2, width=2,
                             depth=2, label_prefix="dangle")
    p15d.lattice.rebuild_from_plane(types.SimpleNamespace(units={}))
    _closure("closure_property_dangling", p15d, "P0REDangle")
    p15o = open_program("P0REOverlap")
    p15o.lattice.snap_in(SnapModule(
        id="mod-o1", kind="lattice2d", axis="H", index=0,
        cells={(4, 4, 0): Cell(h=4, v=4, f=0, content="one", label="one")},
        meta={}))
    p15o.lattice.snap_in(SnapModule(
        id="mod-o2", kind="lattice2d", axis="H", index=0,
        cells={(4, 4, 0): Cell(h=4, v=4, f=0, content="two", label="two")},
        meta={}))
    _closure("closure_property_overlap", p15o, "P0REOverlap")

    print(f"LATTICE MODULES RESTORE: {sum(r)}/{len(r)}")
    return all(r)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
