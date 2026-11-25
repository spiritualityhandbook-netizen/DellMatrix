#!/usr/bin/env python3
"""
Blank Dell Matrix runner
Offline · stdlib only
Confirms Floor + core registry; lists personal slots.
"""
from __future__ import annotations
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

def load_registry():
    path = os.path.join(ROOT, "CORE_REGISTRY.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def list_personal():
    pages = os.path.join(ROOT, "personal")
    code = os.path.join(ROOT, "personal_code")
    def ls(d):
        if not os.path.isdir(d):
            return []
        return sorted(x for x in os.listdir(d) if not x.startswith("."))
    return {"personal": ls(pages), "personal_code": ls(code)}

def main():
    print("=== Blank Dell Matrix ===")
    try:
        reg = load_registry()
    except Exception as e:
        print(f"FAIL registry: {type(e).__name__}: {e}")
        sys.exit(1)

    floor = reg.get("floor", [])
    print(f"Floor: {' · '.join(floor)}")
    print(f"Matrix: {reg.get('matrix')} | status={reg.get('status')}")
    print(f"Dells: {len(reg.get('dells', []))} | Flows: {len(reg.get('flows', []))}")

    # Floor check
    required = {"Alpha", "Delta", "Omega", "Omni"}
    ok_floor = required.issubset(set(floor))
    print(f"Floor lock: {'PASS' if ok_floor else 'FAIL'}")

    slots = list_personal()
    print(f"Personal pages: {slots['personal'] or '(empty — enhance here)'}")
    print(f"Personal code:  {slots['personal_code'] or '(empty — enhance here)'}")
    print("Dual-output: Mandel structure inside · English display only")
    print("Snap-back: see ../DISTRIBUTION.md when ready to contribute to Main")
    print("=== READY ===" if ok_floor else "=== BROKEN FLOOR ===")
    sys.exit(0 if ok_floor else 1)

if __name__ == "__main__":
    main()
