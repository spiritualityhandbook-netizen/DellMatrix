#!/usr/bin/env python3
"""REPL — Form front door. Talk normally. Avatar included."""

from __future__ import annotations

import shlex
import sys

try:
    from form.open import Program, open_program
    from form.dell_matrix.plane import Skin
    from form.dell_matrix.blank_cube import BlankCube
    from form.persist import list_checkpoints
    from form.mandell.translate import translate
    from form.avatar import Facing, Posture, Locomotion, Expression
except ImportError:
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from form.open import Program, open_program
    from form.dell_matrix.plane import Skin
    from form.dell_matrix.blank_cube import BlankCube
    from form.persist import list_checkpoints
    from form.mandell.translate import translate
    from form.avatar import Facing, Posture, Locomotion, Expression

HELP = """
Just talk normally. Examples:

  create an idea called grocery list
  grow ideas 3
  show me the matrix
  visual

  walk forward
  turn left
  turn right
  sit down
  stand up
  jump
  smile
  how do I look

  enhance on
  pulse
  save
  help
""".strip()

_FACING = {
    "n": Facing.N, "north": Facing.N,
    "s": Facing.S, "south": Facing.S,
    "e": Facing.E, "east": Facing.E,
    "w": Facing.W, "west": Facing.W,
}

_EXPR = {
    "neutral": Expression.NEUTRAL,
    "focus": Expression.FOCUS,
    "joy": Expression.JOY,
    "calm": Expression.CALM,
    "intense": Expression.INTENSE,
    "curious": Expression.CURIOUS,
    "resolute": Expression.RESOLUTE,
    "soft": Expression.SOFT,
}


def _execute_intent(p: Program, intent) -> None:
    action = intent.action
    args = intent.args or {}

    print(f"  → {intent.mandel}")

    if action == "place":
        uid = args.get("id", "idea")
        label = args.get("label", uid)
        words = args.get("words", "")
        p.place(uid, label, words=words, skin=Skin.CUBE)
        print(f"  placed: {label}")

    elif action == "grow":
        n = int(args.get("cycles", 1))
        out = p.grow_ideas(n)
        print(f"  grew {len(out)} cycle(s)")
        print(p.render())

    elif action == "show":
        print(p.render())

    elif action == "visual":
        paths = p.visual()
        print("  Visual workspace ready (offline):")
        print("  →", paths.get("html"))
        print("  Open that file in any browser.")

    elif action == "walk":
        steps = int(args.get("steps", 1))
        p.avatar.set_locomotion(Locomotion.WALK)
        pos = p.avatar.step(steps)
        print(f"  walked to {pos}")

    elif action == "run":
        p.avatar.set_locomotion(Locomotion.RUN)
        pos = p.avatar.step(2)
        print(f"  ran to {pos}")

    elif action == "stop":
        p.avatar.set_locomotion(Locomotion.IDLE)
        print("  stopped")

    elif action == "turn":
        direction = args.get("direction", "right")
        if direction == "left":
            facing = p.avatar.turn_left()
        else:
            facing = p.avatar.turn_right()
        print(f"  now facing {facing}")

    elif action == "face":
        d = str(args.get("direction", "n")).lower()
        facing = _FACING.get(d, Facing.N)
        p.avatar.face(facing)
        print(f"  facing {facing.name}")

    elif action == "sit":
        p.avatar.set_posture(Posture.SIT)
        print("  sat down")

    elif action == "stand":
        p.avatar.set_posture(Posture.STAND)
        print("  standing")

    elif action == "jump":
        p.avatar.set_posture(Posture.JUMP)
        print("  jumped")
        p.avatar.set_posture(Posture.STAND)

    elif action == "bend":
        p.avatar.set_posture(Posture.BEND)
        print("  bent over")

    elif action == "pick_up":
        item = args.get("item", "item")
        ok = p.avatar.pick_up(item)
        print(f"  picked up {item}" if ok else "  hands full")

    elif action == "place_down":
        item = p.avatar.place_down()
        print(f"  put down {item}" if item else "  nothing in hands")

    elif action == "express":
        name = args.get("expression", "neutral")
        expr = _EXPR.get(name, Expression.NEUTRAL)
        face = p.face.set(expr)
        print(f"  {face}  ({name})")

    elif action == "avatar_status":
        st = p.avatar_status()
        print(f"  {st['look']}  {st['describe']}")

    elif action == "enhance_on":
        p.enhance_on()
        print("  enhance ON")

    elif action == "enhance_off":
        p.enhance_off()
        print("  enhance OFF")

    elif action == "pulse":
        print(p.pulse())

    elif action == "sandbox_on":
        print(p.sandbox_on())

    elif action == "sandbox_off":
        print(p.sandbox_off())

    elif action == "save":
        print("  saved", p.save())

    elif action == "status":
        print(p.status())

    elif action == "help":
        print(HELP)

    else:
        print("  (understood as idea)")
        uid = args.get("id", "idea")
        label = args.get("label", intent.english[:40])
        p.place(uid, label, words=intent.english, skin=Skin.CUBE)
        print(f"  placed: {label}")


def run(owner: str = "Operator", do_load: bool = False) -> None:
    print("DellMatrix — just talk to it")
    print(f"owner={owner}\n")
    p = Program.load(owner) if do_load else open_program(owner)
    print(p.render())
    print("\nType normal English. Examples: create an idea called test · walk forward · smile · help\n")

    while True:
        try:
            line = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue

        if line.lower() in ("quit", "exit", "q"):
            break

        if line.lower().startswith("say "):
            line = line[4:].strip()

        # Always go through the translator for average-user experience
        intent = translate(line)
        _execute_intent(p, intent)

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
