#!/usr/bin/env python3
"""
Seed integrity checker — run before giving the Blank pack away.
Offline · stdlib only
"""
from __future__ import annotations
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
REQUIRED_FILES = [
    "00_FLOOR.md",
    "01_DUAL_OUTPUT.md",
    "CORE_REGISTRY.json",
    "blank_runner.py",
    "README.md",
    "GIVE_PACK.md",
]
REQUIRED_DIRS = ["personal", "personal_code", "SNAP_TEMPLATE"]
FLOOR = {"Alpha", "Delta", "Omega", "Omni"}

def main() -> int:
    print("=== SEED INTEGRITY CHECK ===")
    results = []

    def record(name: str, ok: bool, detail: str = "") -> None:
        status = "PASS" if ok else "FAIL"
        suffix = f" | {detail}" if detail else ""
        print(f"[{len(results)+1}] {name}: {status}{suffix}")
        results.append(ok)

    def run(name, fn):
        try:
            ok, detail = fn()
            record(name, bool(ok), detail)
        except Exception as e:
            record(name, False, f"EXCEPTION {type(e).__name__}: {e}")

    for f in REQUIRED_FILES:
        path = os.path.join(ROOT, f)
        run(f"file:{f}", lambda p=path, n=f: (os.path.isfile(p), n))

    for d in REQUIRED_DIRS:
        path = os.path.join(ROOT, d)
        run(f"dir:{d}", lambda p=path, n=d: (os.path.isdir(p), n))

    def check_registry():
        path = os.path.join(ROOT, "CORE_REGISTRY.json")
        with open(path, "r", encoding="utf-8") as fh:
            reg = json.load(fh)
        floor = set(reg.get("floor", []))
        if not FLOOR.issubset(floor):
            return False, f"floor={sorted(floor)}"
        if reg.get("status") != "TRUE":
            return False, f"status={reg.get('status')}"
        if not reg.get("dells"):
            return False, "no dells"
        return True, f"dells={len(reg['dells'])} flows={len(reg.get('flows', []))}"

    run("registry", check_registry)

    def check_personal_clean():
        """Warn-only if personal has extra files; still PASS (author may ship examples)."""
        extras = []
        for d in ("personal", "personal_code"):
            p = os.path.join(ROOT, d)
            if not os.path.isdir(p):
                continue
            for x in os.listdir(p):
                if x.startswith("."):
                    continue
                if x == ".gitkeep":
                    continue
                extras.append(f"{d}/{x}")
        if extras:
            return True, f"note: non-empty personal slots {extras[:5]}"
        return True, "personal slots empty"

    run("personal_slots", check_personal_clean)

    def check_snap_template():
        man = os.path.join(ROOT, "SNAP_TEMPLATE", "MANIFEST.md")
        return os.path.isfile(man), "MANIFEST.md"

    run("snap_template", check_snap_template)

    passed = sum(1 for x in results if x)
    total = len(results)
    ready = passed == total
    print(f"=== RESULT: {passed}/{total} PASS ===")
    print("=== READY TO GIVE ===" if ready else "=== FIX FAILURES BEFORE GIVE ===")
    return 0 if ready else 1

if __name__ == "__main__":
    sys.exit(main())
