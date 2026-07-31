#!/usr/bin/env python3
"""REPL — talk normally. Growth goes to Nursery until you confirm."""

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
Talk normally. Growth is powerful but safe.

  create an idea called grocery list
  grow ideas 2          → proposes into Nursery (not live yet)
  proposals             → list quarantined ideas
  confirm <id>          → move proposal into live matrix
  reject <id>           → discard proposal
  walk forward / smile / how do I look
  show me / visual / save
  help / quit
""".strip()

_FACING = {
    "n": Facing.N, "north": Facing.N,
    "s": Facing.S, "south": Facing.S,
    "e": Facing.E, "east": Facing.E,
    "w": Facing.W, "west": Facing.W,
}
_EXPR = {
    "neutral": Expression.NEUTRAL, "focus": Expression.FOCUS,
    "joy": Expression.JOY, "calm": Expression.CALM,
    "intense": Expression.INTENSE, "curious": Expression.CURIOUS,
    "resolute": Expression.RESOLUTE, "soft": Expression.SOFT,
}


def _say(msg: str) -> None:
    print(f"  {msg}")


def _show_proposals(p: Program) -> None:
    pending = p.list_proposals()
    if not pending:
        _say("Nursery is empty. Nothing waiting for confirmation.")
        return
    _say(f"Nursery has {len(pending)} proposal(s) waiting:")
    for i, prop in enumerate(pending[:20], 1):
        kind = prop.get("kind", "?")
        aff = prop.get("affinity", 0)
        _say(f"  {i}. [{kind}] {prop['id']}")
        _say(f"      {prop['label']}  (affinity {aff:.2f})")
    if len(pending) > 20:
        _say(f"  ... and {len(pending) - 20} more")
    _say("Type: confirm <id>   or   reject <id>")


def _execute_intent(p: Program, intent, raw_line: str = "") -> None:
    action = intent.action
    args = intent.args or {}
    lower = raw_line.lower().strip()

    # Direct nursery commands (before translator fallback)
    if lower in ("proposals", "nursery", "void", "pending"):
        _show_proposals(p)
        return

    if lower.startswith("confirm "):
        pid = raw_line.split(maxsplit=1)[1].strip()
        res = p.confirm_proposal(pid)
        if res.get("ok"):
            _say(f'Confirmed. "{res["label"]}" is now live in the matrix.')
        else:
            _say(f"Could not confirm: {res.get('reason')}")
        return

    if lower.startswith("reject "):
        pid = raw_line.split(maxsplit=1)[1].strip()
        res = p.reject_proposal(pid)
        if res.get("ok"):
            _say(f'Rejected. "{res["label"]}" stays out of the matrix.')
        else:
            _say(f"Could not reject: {res.get('reason')}")
        return

    if action == "place":
        uid = args.get("id", "idea")
        label = args.get("label", uid)
        p.place(uid, label, words=args.get("words", ""), skin=Skin.CUBE)
        _say(f'Created idea: "{label}"')

    elif action == "grow":
        n = int(args.get("cycles", 1))
        out = p.grow_ideas(n)
        new_n = out.get("proposed_new", 0)
        evo_n = out.get("proposed_evolved", 0)
        pending = out.get("nursery", {}).get("pending", 0)
        _say(f"Growth complete. Proposed {new_n} new + {evo_n} evolved ideas.")
        _say(f"They are quarantined in the Nursery ({pending} pending).")
        _say("They cannot grow further or affect the matrix until you confirm.")
        _say("Type: proposals")

    elif action == "show":
        print()
        print(p.render())

    elif action == "visual":
        paths = p.visual()
        _say("Visual workspace ready (offline).")
        _say(paths.get("html", ""))

    elif action == "walk":
        steps = int(args.get("steps", 1))
        p.avatar.set_locomotion(Locomotion.WALK)
        pos = p.avatar.step(steps)
        _say(f"You walked forward {steps} step(s). Now at {pos}, facing {p.avatar.body.facing.name}.")

    elif action == "run":
        p.avatar.set_locomotion(Locomotion.RUN)
        pos = p.avatar.step(2)
        _say(f"You ran. Now at {pos}, facing {p.avatar.body.facing.name}.")

    elif action == "stop":
        p.avatar.set_locomotion(Locomotion.IDLE)
        _say("You stopped.")

    elif action == "turn":
        direction = args.get("direction", "right")
        facing = p.avatar.turn_left() if direction == "left" else p.avatar.turn_right()
        _say(f"You turned {direction}. Now facing {facing}.")

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
        _say(f'You picked up "{item}".' if ok else "Your hands are already full.")

    elif action == "place_down":
        item = p.avatar.place_down()
        _say(f'You put down "{item}".' if item else "You weren't holding anything.")

    elif action == "express":
        name = args.get("expression", "neutral")
        face = p.face.set(_EXPR.get(name, Expression.NEUTRAL))
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
        p.pulse()
        _say("Pulse sent.")

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
        ns = p.nursery.summary()
        _say(f"{st['look']}  {st['describe']}")
        _say(f"Live ideas: {len(p.cube.session.plane.units)}")
        _say(f"Nursery pending: {ns['pending']}")

    elif action == "help":
        print()
        print(HELP)
        print()

    else:
        uid = args.get("id", "idea")
        label = args.get("label", intent.english[:48])
        p.place(uid, label, words=intent.english, skin=Skin.CUBE)
        _say(f'Created idea: "{label}"')


def run(owner: str = "Operator", do_load: bool = False) -> None:
    print()
    print("  DellMatrix")
    print("  Talk normally. Growth stays in Nursery until you confirm.")
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
        _execute_intent(p, intent, raw_line=line)

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
