#!/usr/bin/env python3
"""
pack_seed.py
One-command Blank Dell Matrix packer for handoff.

1. Runs integrity checks (same contract as check_seed.py)
2. Builds a zip of the seed folder (excludes junk)
3. Writes next to seed/ or to --out path

Offline · stdlib only

Usage:
  python pack_seed.py
  python pack_seed.py --out /path/to/BlankDellMatrix.zip
  python pack_seed.py --skip-check   # not recommended
"""

from __future__ import annotations
import argparse
import json
import os
import sys
import zipfile
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
FLOOR = {"Alpha", "Delta", "Omega", "Omni"}

REQUIRED_FILES = [
    "00_FLOOR.md",
    "01_DUAL_OUTPUT.md",
    "CORE_REGISTRY.json",
    "blank_runner.py",
    "README.md",
    "GIVE_PACK.md",
    "check_seed.py",
    "pack_seed.py",
]
REQUIRED_DIRS = ["personal", "personal_code", "SNAP_TEMPLATE"]

SKIP_NAMES = {
    ".DS_Store",
    "__pycache__",
    ".git",
    ".gitignore",
    "Thumbs.db",
}
SKIP_SUFFIXES = {".pyc", ".pyo", ".zip"}


def integrity() -> tuple[bool, list[str]]:
    """Return (ok, failure messages)."""
    fails: list[str] = []

    for f in REQUIRED_FILES:
        if not os.path.isfile(os.path.join(ROOT, f)):
            fails.append(f"missing file: {f}")

    for d in REQUIRED_DIRS:
        if not os.path.isdir(os.path.join(ROOT, d)):
            fails.append(f"missing dir: {d}")

    reg_path = os.path.join(ROOT, "CORE_REGISTRY.json")
    try:
        with open(reg_path, "r", encoding="utf-8") as fh:
            reg = json.load(fh)
        floor = set(reg.get("floor", []))
        if not FLOOR.issubset(floor):
            fails.append(f"floor incomplete: {sorted(floor)}")
        if reg.get("status") != "TRUE":
            fails.append(f"registry status={reg.get('status')}")
        if not reg.get("dells"):
            fails.append("registry has no dells")
    except Exception as e:
        fails.append(f"registry error: {type(e).__name__}: {e}")

    man = os.path.join(ROOT, "SNAP_TEMPLATE", "MANIFEST.md")
    if not os.path.isfile(man):
        fails.append("missing SNAP_TEMPLATE/MANIFEST.md")

    return len(fails) == 0, fails


def should_skip(name: str) -> bool:
    if name in SKIP_NAMES:
        return True
    if name.startswith(".") and name not in {".gitkeep"}:
        # keep .gitkeep so empty dirs survive zip
        if name == ".gitkeep":
            return False
        return True
    _, ext = os.path.splitext(name)
    if ext in SKIP_SUFFIXES:
        return True
    return False


def build_zip(out_path: str) -> int:
    count = 0
    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for dirpath, dirnames, filenames in os.walk(ROOT):
            # prune skip dirs in-place
            dirnames[:] = [d for d in dirnames if not should_skip(d)]
            for fn in filenames:
                if should_skip(fn):
                    continue
                full = os.path.join(dirpath, fn)
                # archive name relative to parent of seed so zip root is seed/
                rel = os.path.relpath(full, os.path.dirname(ROOT))
                zf.write(full, arcname=rel.replace("\\", "/"))
                count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description="Pack Blank Dell Matrix for handoff")
    parser.add_argument(
        "--out",
        default="",
        help="Output zip path (default: sibling BlankDellMatrix-YYYY-MM-DD.zip)",
    )
    parser.add_argument(
        "--skip-check",
        action="store_true",
        help="Skip integrity check (not recommended)",
    )
    args = parser.parse_args()

    print("=== PACK BLANK DELL MATRIX ===")

    if not args.skip_check:
        ok, fails = integrity()
        if not ok:
            print("Integrity: FAIL")
            for f in fails:
                print(f"  - {f}")
            print("=== FIX BEFORE PACK ===")
            return 1
        print("Integrity: PASS")
    else:
        print("Integrity: SKIPPED")

    if args.out:
        out_path = os.path.abspath(args.out)
    else:
        parent = os.path.dirname(ROOT)
        out_path = os.path.join(parent, f"BlankDellMatrix-{date.today().isoformat()}.zip")

    try:
        n = build_zip(out_path)
    except Exception as e:
        print(f"Zip error: {type(e).__name__}: {e}")
        return 1

    size = os.path.getsize(out_path)
    print(f"Files packed: {n}")
    print(f"Output: {out_path}")
    print(f"Size: {size} bytes")
    print("=== READY TO SEND ===")
    print("Tell them: unzip → cd seed → python blank_runner.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
