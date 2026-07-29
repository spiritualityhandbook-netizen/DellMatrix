#!/usr/bin/env python3
"""REPL — interactive session with main/scores surface commands."""

from __future__ import annotations

import shlex
import sys

try:
    from form.open import Program, open_program
    from form.dell_matrix.plane import Skin
except ImportError:
    import os

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from form.open import Program, open_program
    from form.dell_matrix.plane import Skin

HELP = """
Commands:
  help | show | status | scores | main
  place <id> <label> [words…]
  skin <id> <cube|sphere|seed|building|words|circle|flower>
  move <id> <x> <y>
  box <id> [id…] | unbox <id>
  perspective <table|page|cube|circle|flower|sphere>
  zoom <id> | zoom out
  enhance on | enhance off | pulse
  pull <unit_id> <tag>
  save | load | grow
  quit
""".strip()


def _skin(name: str) -> Skin:
    try:
        return Skin(name.lower())
    except Exception:
        return Skin.CUBE


def run(owner: str = "Operator", do_load: bool = False) -> None:
    print("01[Initiate] > 13[Loop] >> 09[Show] :: REPL")
    print(f"English: Interactive Dell Matrix — owner={owner}\n")
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
            print({"owner": st["owner"], "enhance": st["enhance"]["on"], "main": st["main"], "units": list(p.cube.session.plane.units.keys())})
        elif cmd == "scores":
            print(p.scores())
        elif cmd == "main":
            print(p.main.summary())
        elif cmd == "place" and len(parts) >= 3:
            p.place(parts[1], parts[2], words=" ".join(parts[3:]), skin=Skin.CUBE)
            print("placed", parts[1])
        elif cmd == "skin" and len(parts) >= 3:
            print("ok" if p.cube.session.plane.set_skin(parts[1], _skin(parts[2])) else "missing")
        elif cmd == "move" and len(parts) >= 4:
            print("ok" if p.cube.session.plane.move(parts[1], float(parts[2]), float(parts[3])) else "missing")
        elif cmd == "box" and len(parts) >= 2:
            p.box(parts[1:])
            print("boxed", parts[1:])
        elif cmd == "unbox" and len(parts) >= 2:
            print("ok" if p.cube.session.plane.unbox(parts[1]) else "missing")
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
