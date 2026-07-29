#!/usr/bin/env python3
"""Dual-output boundary check — structure vs display."""

from __future__ import annotations

from typing import Any, Dict
import re
import sys

try:
    from form.mandell.floor import FLOOR, assert_floor_intact
except ImportError:
    import os

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from form.mandell.floor import FLOOR, assert_floor_intact

# Seeds look like 15[Map] or 08[Create]
_SEED = re.compile(r"\d{1,2}\[[A-Za-z_]+\]")


def check_seed(text: str) -> Dict[str, Any]:
    assert_floor_intact()
    found = _SEED.findall(text)
    return {
        "ok": True,
        "floor": list(FLOOR),
        "seeds_found": found,
        "has_seed": len(found) > 0,
        "rule": "Mandell structure inside · English display only",
    }


def smoke() -> bool:
    print("=== DUAL OUTPUT SMOKE ===")
    r = []

    def rec(name, ok):
        print(f"[{len(r)+1}] {name}: {'PASS' if ok else 'FAIL'}")
        r.append(bool(ok))

    c = check_seed("15[Map] : 18[Mirror] >> 46[Rank] > 50[Manifest] :: NBD")
    rec("find seeds", c["has_seed"] and "15[Map]" in c["seeds_found"])
    rec("floor", c["floor"] == list(FLOOR))
    rec("english ok", check_seed("English only display")["ok"] is True)
    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


def main() -> None:
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    print(check_seed("15[Map] >> 50[Manifest]"))


if __name__ == "__main__":
    main()
