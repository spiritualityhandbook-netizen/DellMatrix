#!/usr/bin/env python3
"""
Give a blank Dell Matrix to someone.

08[Create] >> 50[Manifest] : 10[Keep] :: BlankGive

Creates a clean owner plane (welcome only or truly empty),
saves program_<owner>.json, writes a tiny START.txt next to state.

Usage:
  python -m form.give_blank --owner SisterName
  python -m form.give_blank --owner SisterName --empty
"""

from __future__ import annotations

import os
import sys

try:
    from form.open import open_program
    from form.dell_matrix.blank_cube import give, BlankCube
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from form.open import open_program
    from form.dell_matrix.blank_cube import give, BlankCube


def give_blank(owner: str, empty: bool = False) -> dict:
    p = open_program(owner)
    if empty:
        p.cube.session.plane.units.clear()
        p.cube.session.plane.sandboxes.clear()
    # gates stay default OFF
    assert p.enhance.on is False
    assert p.sandbox.on is False
    assert p.ambient.master_on is False

    path = p.save()
    pack_cube = BlankCube(owner=owner, clean=True)
    pack_cube.session = p.cube.session
    pack_path = pack_cube.write_pack()

    state_dir = os.path.join(os.path.dirname(__file__), "state")
    start = os.path.join(state_dir, f"START_{owner}.txt")
    with open(start, "w", encoding="utf-8") as f:
        f.write(
            f"""Dell Matrix — blank for {owner}

1) Open Terminal in the DellMatrix folder (the one that contains form/)

2) Run:
   python -m form.repl --owner {owner} --load

3) Type:
   tutorial
   place my1 MyFirstIdea words about what matters to me
   show
   save

Defaults (safe):
  enhance OFF · sandbox OFF · ambient OFF

Your cube is yours. Floor is shared and locked.
"""
        )
    return {
        "owner": owner,
        "save": path,
        "pack": pack_path,
        "start": start,
        "units": list(p.cube.session.plane.units.keys()),
        "enhance": p.enhance.on,
        "sandbox": p.sandbox.on,
    }


def main() -> None:
    owner = "Sister"
    empty = "--empty" in sys.argv
    for i, a in enumerate(sys.argv):
        if a == "--owner" and i + 1 < len(sys.argv):
            owner = sys.argv[i + 1]
    out = give_blank(owner, empty=empty)
    print("08[Create] >> 50[Manifest] :: BlankGive")
    print("English: Blank matrix ready.\n")
    for k, v in out.items():
        print(f"  {k}: {v}")
    print(f"\nOn her computer:\n  python -m form.repl --owner {owner} --load\n")


if __name__ == "__main__":
    main()
