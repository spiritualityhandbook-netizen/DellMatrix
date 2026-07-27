#!/usr/bin/env python3
"""
16_IMPORT_ADAPTER.py
Code Phase 4 · Artifact 16 (cell 4.1)
Status: TRUE
Offline · Zero dependencies · Stdlib only

Thin import layer:
- Tries to load real preform/code modules 05–14 by file path
- Falls back to None markers when missing or incompatible
- Reports load map for smoke / diagnostics
- Does not change Integrator public API — Integrator may consume this map later

Usage:
    from import_adapter import load_all, LoadReport
    report = load_all()
    print(report.summary())
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import importlib.util
import os
import sys

_CODE_DIR = os.path.dirname(os.path.abspath(__file__))

# Module file → expected attribute names (best-effort)
MODULE_SPEC: Dict[str, List[str]] = {
    "05_GRID.py": ["Grid", "Cell", "place_dell", "place_text"],
    "06_AVATAR_FSM.py": ["Avatar", "BodyState", "Facing", "Posture", "Locomotion", "Reach"],
    "07_EXPRESSION_FIELD.py": ["ExpressionField", "Expression", "EXPRESSION_MAP"],
    "08_FACE_STATE_CYCLES.py": ["FaceStateController", "FaceCycle", "CycleMode", "build_default_controller"],
    "09_KAOMOJI_PACKS.py": ["KaomojiRegistry", "KaomojiPack", "build_default_registry", "KAOMOJI_PACKS"],
    "10_ASCII_ANIMATION.py": ["AsciiPlayer", "Anim", "build_default_player"],
    "11_REACH_INVENTORY.py": ["ReachInventory", "Inventory", "InventorySlot"],
    "12_GODWORKSPACE.py": ["GodWorkSpace", "WorkspaceState"],
    "13_THINKS.py": ["Thinks", "Thought", "Intent", "BodySnapshot", "try_execute"],
    "14_TOKEN_WORKMEM.py": ["TokenWorkMem", "TokenBudget", "WorkMemory", "WorkGraph"],
    "01_REGISTRY_DATA.json": [],  # data file, not a module
    "02_TINY_LEXER.py": ["tokenize"],
}

@dataclass
class ModuleLoad:
    file: str
    loaded: bool
    source: str  # "real" | "missing" | "error"
    attrs: Dict[str, Any] = field(default_factory=dict)
    error: str = ""

@dataclass
class LoadReport:
    modules: Dict[str, ModuleLoad] = field(default_factory=dict)

    def summary(self) -> str:
        lines = ["=== IMPORT ADAPTER REPORT ==="]
        real = missing = errors = 0
        for name, m in sorted(self.modules.items()):
            if m.source == "real":
                real += 1
                flag = "REAL"
            elif m.source == "missing":
                missing += 1
                flag = "MISS"
            else:
                errors += 1
                flag = "ERR "
            attr_n = len(m.attrs)
            extra = f" attrs={attr_n}" if attr_n else ""
            err = f" | {m.error}" if m.error else ""
            lines.append(f"  [{flag}] {name}{extra}{err}")
        lines.append(f"--- real={real} missing={missing} errors={errors} ---")
        return "\n".join(lines)

    def get(self, file: str, attr: str, default: Any = None) -> Any:
        m = self.modules.get(file)
        if not m or not m.loaded:
            return default
        return m.attrs.get(attr, default)

    def all_real(self, files: Optional[List[str]] = None) -> bool:
        targets = files or list(MODULE_SPEC.keys())
        return all(
            self.modules.get(f, ModuleLoad(f, False, "missing")).source == "real"
            for f in targets
            if f.endswith(".py")
        )


def _load_py(path: str) -> Any:
    name = os.path.splitext(os.path.basename(path))[0]
    # unique module name to avoid collisions
    mod_name = f"preform_code_{name}"
    spec = importlib.util.spec_from_file_location(mod_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"no spec for {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


def load_module(filename: str, expected_attrs: Optional[List[str]] = None) -> ModuleLoad:
    path = os.path.join(_CODE_DIR, filename)
    expected_attrs = expected_attrs if expected_attrs is not None else MODULE_SPEC.get(filename, [])

    if not os.path.isfile(path):
        return ModuleLoad(file=filename, loaded=False, source="missing", error="file not found")

    if filename.endswith(".json"):
        # presence-only check for data files
        return ModuleLoad(file=filename, loaded=True, source="real", attrs={"path": path})

    try:
        mod = _load_py(path)
        attrs = {}
        for a in expected_attrs:
            if hasattr(mod, a):
                attrs[a] = getattr(mod, a)
        return ModuleLoad(file=filename, loaded=True, source="real", attrs=attrs)
    except Exception as e:
        return ModuleLoad(
            file=filename,
            loaded=False,
            source="error",
            error=f"{type(e).__name__}: {e}",
        )


def load_all(code_dir: Optional[str] = None) -> LoadReport:
    global _CODE_DIR
    if code_dir:
        _CODE_DIR = code_dir
    report = LoadReport()
    for filename, attrs in MODULE_SPEC.items():
        report.modules[filename] = load_module(filename, attrs)
    return report


def smoke_adapter() -> bool:
    """Adapter self-test with error handling."""
    print("=== IMPORT ADAPTER SMOKE ===")
    results = []

    def record(name: str, passed: bool, detail: str = "") -> None:
        status = "PASS" if passed else "FAIL"
        suffix = f" | {detail}" if detail else ""
        print(f"[{len(results)+1}] {name}: {status}{suffix}")
        results.append((name, passed, detail))

    try:
        report = load_all()
        record("load_all", True, f"modules={len(report.modules)}")
    except Exception as e:
        record("load_all", False, f"EXCEPTION {type(e).__name__}: {e}")
        print("=== RESULT: FAIL ===")
        return False

    try:
        print(report.summary())
        record("summary", True)
    except Exception as e:
        record("summary", False, f"EXCEPTION {type(e).__name__}: {e}")

    # Core files that should exist in a full checkout
    for core in ["02_TINY_LEXER.py", "05_GRID.py", "06_AVATAR_FSM.py"]:
        m = report.modules.get(core)
        if m is None:
            record(f"present:{core}", False, "not in report")
        else:
            # PASS if real OR missing (missing is valid offline partial checkout)
            # FAIL only on error source
            ok = m.source in ("real", "missing")
            record(f"load:{core}", ok, f"source={m.source} err={m.error or '-'}")

    # get() must not raise on missing
    try:
        val = report.get("99_NOT_REAL.py", "Grid", default="FALLBACK")
        record("get_missing_safe", val == "FALLBACK", f"val={val}")
    except Exception as e:
        record("get_missing_safe", False, f"EXCEPTION {type(e).__name__}: {e}")

    passed = sum(1 for _, p, _ in results if p)
    total = len(results)
    print(f"=== RESULT: {passed}/{total} PASS ===")
    return passed == total


if __name__ == "__main__":
    ok = smoke_adapter()
    sys.exit(0 if ok else 1)
