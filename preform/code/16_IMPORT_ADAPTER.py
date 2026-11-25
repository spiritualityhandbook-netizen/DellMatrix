#!/usr/bin/env python3
"""
16_IMPORT_ADAPTER.py
Code Phase 4 · Artifact 16 (cell 4.1)
Status: TRUE
Offline · Zero dependencies · Stdlib only

Thin import layer for preform/code modules.
Used by Integrator (4.2) to prefer real 05–14 when available.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import importlib.util
import os
import sys

_CODE_DIR = os.path.dirname(os.path.abspath(__file__))

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
    "01_REGISTRY_DATA.json": [],
    "02_TINY_LEXER.py": ["tokenize"],
}

@dataclass
class ModuleLoad:
    file: str
    loaded: bool
    source: str  # real | missing | error
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
            extra = f" attrs={len(m.attrs)}" if m.attrs else ""
            err = f" | {m.error}" if m.error else ""
            lines.append(f"  [{flag}] {name}{extra}{err}")
        lines.append(f"--- real={real} missing={missing} errors={errors} ---")
        return "\n".join(lines)

    def get(self, file: str, attr: str, default: Any = None) -> Any:
        m = self.modules.get(file)
        if not m or not m.loaded:
            return default
        return m.attrs.get(attr, default)

    def source_of(self, file: str) -> str:
        m = self.modules.get(file)
        return m.source if m else "missing"

    def real_count(self) -> int:
        return sum(1 for m in self.modules.values() if m.source == "real")


def _load_py(path: str) -> Any:
    name = os.path.splitext(os.path.basename(path))[0]
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
        return ModuleLoad(file=filename, loaded=True, source="real", attrs={"path": path})

    try:
        mod = _load_py(path)
        attrs = {a: getattr(mod, a) for a in expected_attrs if hasattr(mod, a)}
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


def resolve_components(report: Optional[LoadReport] = None) -> Dict[str, Any]:
    """
    Build a component map for Integrator.
    Values are either real classes/callables or None (caller uses stand-in).
    Never raises.
    """
    if report is None:
        try:
            report = load_all()
        except Exception:
            report = LoadReport()

    def take(file: str, attr: str):
        if report.source_of(file) != "real":
            return None
        return report.get(file, attr, None)

    return {
        "report": report,
        "Grid": take("05_GRID.py", "Grid"),
        "Avatar": take("06_AVATAR_FSM.py", "Avatar"),
        "Reach": take("06_AVATAR_FSM.py", "Reach"),
        "Facing": take("06_AVATAR_FSM.py", "Facing"),
        "ExpressionField": take("07_EXPRESSION_FIELD.py", "ExpressionField"),
        "FaceStateController": take("08_FACE_STATE_CYCLES.py", "FaceStateController"),
        "KaomojiRegistry": take("09_KAOMOJI_PACKS.py", "KaomojiRegistry"),
        "AsciiPlayer": take("10_ASCII_ANIMATION.py", "AsciiPlayer"),
        "Anim": take("10_ASCII_ANIMATION.py", "Anim"),
        "ReachInventory": take("11_REACH_INVENTORY.py", "ReachInventory"),
        "GodWorkSpace": take("12_GODWORKSPACE.py", "GodWorkSpace"),
        "Thinks": take("13_THINKS.py", "Thinks"),
        "Intent": take("13_THINKS.py", "Intent"),
        "TokenWorkMem": take("14_TOKEN_WORKMEM.py", "TokenWorkMem"),
        "tokenize": take("02_TINY_LEXER.py", "tokenize"),
    }


def smoke_adapter() -> bool:
    print("=== IMPORT ADAPTER SMOKE ===")
    results = []

    def record(name: str, passed: bool, detail: str = "") -> None:
        print(f"[{len(results)+1}] {name}: {'PASS' if passed else 'FAIL'}" + (f" | {detail}" if detail else ""))
        results.append(passed)

    try:
        report = load_all()
        record("load_all", True, f"modules={len(report.modules)} real={report.real_count()}")
    except Exception as e:
        record("load_all", False, f"EXCEPTION {type(e).__name__}: {e}")
        return False

    try:
        print(report.summary())
        record("summary", True)
    except Exception as e:
        record("summary", False, f"EXCEPTION {type(e).__name__}: {e}")

    try:
        comps = resolve_components(report)
        record("resolve_components", isinstance(comps, dict), f"keys={len(comps)}")
    except Exception as e:
        record("resolve_components", False, f"EXCEPTION {type(e).__name__}: {e}")

    try:
        val = report.get("99_NOT_REAL.py", "Grid", default="FALLBACK")
        record("get_missing_safe", val == "FALLBACK", f"val={val}")
    except Exception as e:
        record("get_missing_safe", False, f"EXCEPTION {type(e).__name__}: {e}")

    passed = sum(1 for p in results if p)
    print(f"=== RESULT: {passed}/{len(results)} PASS ===")
    return passed == len(results)


if __name__ == "__main__":
    ok = smoke_adapter()
    sys.exit(0 if ok else 1)
