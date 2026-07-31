#!/usr/bin/env python3
"""REPL — Form front door. Talk normally. Clear English feedback."""

from __future__ import annotations

import sys

try:
    from form.open import Program, open_program
    from form.dell_matrix.plane import Skin
    from form.mandell.translate import translate
    from form.avatar import Facing, Posture, Locomotion, Expression
except ImportError:
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from form.open import Program, open_program
    from form.dell_matrix.plane import Skin
    from form.mandell.translate import translate
    from form.avatar import Facing, Posture, Locomotion, Expression

HELP = """
Just type normal English. Examples:

  create an idea called grocery list
  grow ideas 2
  walk forward
  turn left
  sit down
  smile
  how do I look
  show me
  visual
  save
  help
  quit
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


def _say(msg: str) -> None:
    """Plain English reply to the user."""
    print(f"  {msg}")


def _execute_intent(p: Program, intent) -> None:
    action = intent.action
    args = intent.args or {}

    if action == "place":
        uid = args.get("id", "idea")
        label = args.get("label", uid)
        words = args.get("words", "")
        p.place(uid, label, words=words, skin=Skin.CUBE)
        _say(f'Created idea: "{label}"')

    elif action == "grow":
        n = int(args.get("cycles", 1))
        out = p.grow_ideas(n)
        _say(f"Grew the matrix {len(out)} time(s).")
        print()
        print(p.render())

    elif action == "show":
        print()
        print(p.render())

    elif action == "visual":
        paths = p.visual()
        html = paths.get("html", "")
        _say("Visual workspace ready (works offline).")
        _say(f"Open this file in any browser:")
        _say(html)

    elif action == "walk":
        steps = int(args.get("steps", 1))
        p.avatar.set_locomotion(Locomotion.WALK)
        pos = p.avatar.step(steps)
        facing = p.avatar.body.facing.name
        _say(f"You walked forward {steps} step(s). Now at {pos}, facing {facing}.")

    elif action == "run":
        p.avatar.set_locomotion(Locomotion.RUN)
        pos = p.avatar.step(2)
        facing = p.avatar.body.facing.name
        _say(f"You ran. Now at {pos}, facing {facing}.")

    elif action == "stop":
        p.avatar.set_locomotion(Locomotion.IDLE)
        _say("You stopped.")

    elif action == "turn":
        direction = args.get("direction", "right")
        if direction == "left":
            facing = p.avatar.turn_left()
            _say(f"You turned left. Now facing {facing}.")
        else:
            facing = p.avatar.turn_right()
            _say(f"You turned right. Now facing {facing}.")

    elif action == "face":
        d = str(args.get("direction", "n")).lower()
        facing = _FACING.get(d, Facing.N)
        p.avatar.face(facing)
        _say(f"You are now facing {facing.name}.")

    elif action == "sit":
        p.avatar.set_posture(Posture.SIT)
        _say("You sat down.")

    elif action == "stand":
        p.avatar.set_posture(Posture.STAND)
        _say("You stood up.")

    elif action == "jump":
        p.avatar.set_posture(Posture.JUMP)
        p.avatar.set_posture(Posture.STAND)
        _say("You jumped.")

    elif action == "bend":
        p.avatar.set_posture(Posture.BEND)
        _say("You bent over.")

    elif action == "pick_up":
        item = args.get("item", "item")
        ok = p.avatar.pick_up(item)
        if ok:
            _say(f'You picked up "{item}".')
        else:
            _say("Your hands are already full.")

    elif action == "place_down":
        item = p.avatar.place_down()
        if item:
            _say(f'You put down "{item}".')
        else:
            _say("You weren't holding anything.")

    elif action == "express":
        name = args.get("expression", "neutral")
        expr = _EXPR.get(name, Expression.NEUTRAL)
        face = p.face.set(expr)
        _say(f"{face}  You look {name}.")

    elif action == "avatar_status":
        st = p.avatar_status()
        _say(f"{st['look']}  {st['describe']}")

    elif action == "enhance_on":
        p.enhance_on()
        _say("Enhance is now ON.")

    elif action == "enhance_off":
        p.enhance_off()
        _say("Enhance is now OFF.")

    elif action == "pulse":
        result = p.pulse()
        _say("Pulse sent.")
        if result:
            _say(str(result))

    elif action == "sandbox_on":
        p.sandbox_on()
        _say("Sandbox is now ON.")

    elif action == "sandbox_off":
        p.sandbox_off()
        _say("Sandbox is now OFF.")

    elif action == "save":
        path = p.save()
        _say("Saved.")
        _say(f"Location: {path}")

    elif action == "status":
        st = p.avatar_status()
        _say(f"{st['look']}  {st['describe']}")
        _say(f"Ideas in matrix: {len(p.cube.session.plane.units)}")
        _say(f"Enhance: {'ON' if p.enhance.on else 'OFF'}")

    elif action == "help":
        print()
        print(HELP)
        print()

    else:
        # Fallback treated as new idea
        uid = args.get("id", "idea")
        label = args.get("label", intent.english[:48])
        p.place(uid, label, words=intent.english, skin=Skin.CUBE)
        _say(f'Created idea: "{label}"')


def run(owner: str = "Operator", do_load: bool = False) -> None:
    print()
    print("  DellMatrix")
    print("  Talk normally. Type help for examples. Type quit to leave.")
    print()
    p = Program.load(owner) if do_load else open_program(owner)
    print(p.render())
    print()

    while True:
        try:
            line = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue

        if line.lower() in ("quit", "exit", "q"):
            _say("Goodbye.")
            break

        if line.lower().startswith("say "):
            line = line[4:].strip()

        intent = translate(line)
        _execute_intent(p, intent)

    print()


def main() -> None:
    owner = "Ace"
    do_load = "--load" in sys.argv
    for i, a in enumerate(sys.argv):
        if a == "--owner" and i + 1 < len(sys.argv):
            owner = sys.argv[i + 1]
    run(owner, do_load)


if __name__ == "__main__":
    main()
