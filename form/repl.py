#!/usr/bin/env python3
"""REPL — Form 1.00 with tutorial."""

from __future__ import annotations

import shlex
import sys

try:
    from form.open import Program, open_program
    from form.dell_matrix.plane import Skin
    from form.dell_matrix.blank_cube import BlankCube
    from form.persist import list_checkpoints
except ImportError:
    import os

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from form.open import Program, open_program
    from form.dell_matrix.plane import Skin
    from form.dell_matrix.blank_cube import BlankCube
    from form.persist import list_checkpoints

HELP = """
Form 1.00 — type tutorial once, then operate.

  place <id> <label> [words…]   put an idea on the plane
  enhance on → pulse → show     feel resonance
  visual                        write HTML map
  save / load                   keep your cube
  push_main / pull_main         shared third field
  box <id…>                     sandbox (no outside enhance)
  help | quit
""".strip()

TUTORIAL = """
TUTORIAL (Form 1.00)
--------------------
1) place biz Business my company idea
2) place music Music a song idea
3) enhance on
4) pulse
5) show          ← scores rise between connected ideas
6) visual        ← open the HTML path printed
7) save

Rules:
- enhance stays OFF until you turn it on
- box isolates an idea from the others
- push_main shares tags to Main without changing your plane
- ambient has no capture engines in Form 1.00 (skeleton only)
""".strip()


def _skin(name: str) -> Skin:
    try:
        return Skin(name.lower())
    except Exception:
        return Skin.CUBE


def run(owner: str = "Operator", do_load: bool = False) -> None:
    print("Dell Matrix Form 1.00 — type tutorial or help")
    print(f"owner={owner}\n")
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
        elif cmd in ("help", "?"):
            print(HELP)
        elif cmd == "tutorial":
            print(TUTORIAL)
        elif cmd == "show":
            print(p.render())
        elif cmd == "status":
            st = p.status()
            print({"owner": st["owner"], "enhance": st["enhance"]["on"], "ambient": st["ambient"]["master_on"], "main": st["main"], "units": list(p.cube.session.plane.units.keys())})
        elif cmd == "scores":
            print(p.scores())
        elif cmd == "main":
            print(p.main.summary())
        elif cmd == "shared":
            print(p.shared_main_summary())
        elif cmd == "ambient":
            print(p.ambient.status())
        elif cmd == "verify":
            print(p.matrix.verify())
        elif cmd == "health":
            print({"enhance": p.enhance.on, "ambient": p.ambient.master_on, "units": len(p.cube.session.plane.units), "gen": p.duo.generation, "verify_ok": p.matrix.verify().get("ok"), "form": "1.00"})
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
        elif cmd == "decay":
            print(p.enhance.decay(float(parts[1]) if len(parts) > 1 else 0.9))
        elif cmd == "clear":
            print(p.enhance.clear())
        elif cmd == "pull" and len(parts) >= 3:
            print(p.pull(parts[1], parts[2]))
        elif cmd == "push_main":
            print(p.push_main())
        elif cmd == "pull_main":
            print(p.pull_main())
        elif cmd == "snapshot_main":
            print(p.snapshot_main())
        elif cmd == "visual":
            print(p.visual())
        elif cmd == "checkpoint":
            print(p.checkpoint())
        elif cmd == "checkpoints":
            print(list_checkpoints(owner))
        elif cmd == "pack":
            pack_cube = BlankCube(owner=p.owner, clean=True)
            pack_cube.session = p.cube.session
            print("pack", pack_cube.write_pack())
        elif cmd == "save":
            print("saved", p.save())
        elif cmd == "load":
            p = Program.load(owner)
            print(p.render())
        elif cmd == "grow":
            p.grow(1)
            print("gen", p.duo.generation)
        else:
            print("unknown — type help or tutorial")

    print("session end")


def main() -> None:
    owner = "Operator"
    do_load = "--load" in sys.argv
    for i, a in enumerate(sys.argv):
        if a == "--owner" and i + 1 < len(sys.argv):
            owner = sys.argv[i + 1]
    run(owner, do_load)


if __name__ == "__main__":
    main()
