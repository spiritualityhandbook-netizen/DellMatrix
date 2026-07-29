#!/usr/bin/env python3
"""
REPL L3 — full interactive session on the one program.

01[Initiate] > 13[Loop] >> 09[Show] :: REPL

Run:
  python -m form.repl
  python -m form.repl --owner Ace --load
"""

from __future__ import annotations

import json
import shlex
import sys

try:
    from form.open import Program, open_program
    from form.dell_matrix.plane import Skin
    from form.dell_matrix.blank_cube import BlankCube
except ImportError:
    import os

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from form.open import Program, open_program
    from form.dell_matrix.plane import Skin
    from form.dell_matrix.blank_cube import BlankCube

HELP = """
Commands (L3):
  help                         this list
  show                         render plane + scores
  status                       compact status
  scores                       resonance scores
  main                         Main summary / top tags
  verify                       snap host health (required ports)
  health                       floor + enhance + unit count
  place <id> <label> [words…]  put unit on plane
  words <id> <text…>           set unit words
  skin <id> <skin>             cube|sphere|seed|building|words|circle|flower
  move <id> <x> <y>
  remove <id>                  take unit off plane
  box <id> [id…] | unbox <id>
  neighbors <id>               spatial neighbors
  perspective <mode>           table|page|cube|circle|flower|sphere
  zoom <id> | zoom out
  enhance on | enhance off
  pulse                        resonance pulse
  pull <unit_id> <tag>         voluntary pull from Main
  pack                         write BlankCube pack for owner
  save | load | grow
  quit
""".strip()


def _skin(name: str) -> Skin:
    try:
        return Skin(name.lower())
    except Exception:
        return Skin.CUBE


def run(owner: str = "Operator", do_load: bool = False) -> None:
    print("01[Initiate] > 13[Loop] >> 09[Show] :: REPL L3")
    print(f"English: Interactive Dell Matrix — owner={owner}")
    print("Type 'help'.\n")

    p = Program.load(owner) if do_load else open_program(owner)
    print(p.render())

    while True:
        try:
            line = input("matrix> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        try:
            parts = shlex.split(line)
        except ValueError as e:
            print("parse error:", e)
            continue
        cmd = parts[0].lower()

        if cmd in ("quit", "exit", "q"):
            break
        elif cmd == "help":
            print(HELP)
        elif cmd == "show":
            print(p.render())
        elif cmd == "status":
            st = p.status()
            print(
                {
                    "owner": st["owner"],
                    "enhance": st["enhance"]["on"],
                    "main": st["main"],
                    "units": list(p.cube.session.plane.units.keys()),
                }
            )
        elif cmd == "scores":
            print(p.scores())
        elif cmd == "main":
            print(p.main.summary())
        elif cmd == "verify":
            print(p.matrix.verify())
        elif cmd == "health":
            print(
                {
                    "floor": list(p.status()["floor"]["floor"]),
                    "enhance": p.enhance.on,
                    "units": len(p.cube.session.plane.units),
                    "gen": p.duo.generation,
                    "main_contributions": len(p.main.contributions),
                    "verify_ok": p.matrix.verify().get("ok"),
                }
            )
        elif cmd == "place" and len(parts) >= 3:
            p.place(parts[1], parts[2], words=" ".join(parts[3:]), skin=Skin.CUBE)
            print("placed", parts[1])
        elif cmd == "words" and len(parts) >= 3:
            u = p.cube.session.plane.units.get(parts[1])
            if not u:
                print("missing")
            else:
                u.words = " ".join(parts[2:])
                print("ok")
        elif cmd == "skin" and len(parts) >= 3:
            print("ok" if p.cube.session.plane.set_skin(parts[1], _skin(parts[2])) else "missing")
        elif cmd == "move" and len(parts) >= 4:
            print("ok" if p.cube.session.plane.move(parts[1], float(parts[2]), float(parts[3])) else "missing")
        elif cmd == "remove" and len(parts) >= 2:
            print("ok" if p.cube.session.plane.remove(parts[1]) else "missing")
        elif cmd == "box" and len(parts) >= 2:
            p.box(parts[1:])
            print("boxed", parts[1:])
        elif cmd == "unbox" and len(parts) >= 2:
            print("ok" if p.cube.session.plane.unbox(parts[1]) else "missing")
        elif cmd == "neighbors" and len(parts) >= 2:
            print(p.cube.session.plane.neighbors(parts[1]))
        elif cmd == "perspective" and len(parts) >= 2:
            print("ok" if p.set_perspective(parts[1]) else "bad")
        elif cmd == "zoom" and len(parts) >= 2:
            if parts[1] == "out":
                p.cube.session.plane.zoom_out()
                print("overview")
            else:
                print("ok" if p.cube.session.plane.zoom_in(parts[1]) else "missing")
        elif cmd == "enhance" and len(parts) >= 2:
            if parts[1] == "on":
                p.enhance_on()
                print("enhance ON")
            else:
                p.enhance_off()
                print("enhance OFF")
        elif cmd == "pulse":
            print(p.pulse())
        elif cmd == "pull" and len(parts) >= 3:
            print(p.pull(parts[1], parts[2]))
        elif cmd == "pack":
            # export current personal plane as blank pack under owner name
            pack_cube = BlankCube(owner=p.owner, clean=True)
            pack_cube.session = p.cube.session
            path = pack_cube.write_pack()
            print("pack", path)
        elif cmd == "save":
            print("saved", p.save())
        elif cmd == "load":
            p = Program.load(owner)
            print(p.render())
        elif cmd == "grow":
            p.grow(1)
            print("gen", p.duo.generation)
        else:
            print("unknown — type help")

    print("20[Alpha] :: REPL end")


def main() -> None:
    owner = "Operator"
    do_load = "--load" in sys.argv
    for i, a in enumerate(sys.argv):
        if a == "--owner" and i + 1 < len(sys.argv):
            owner = sys.argv[i + 1]
    run(owner, do_load)


if __name__ == "__main__":
    main()
