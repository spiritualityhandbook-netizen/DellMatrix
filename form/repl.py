#!/usr/bin/env python3
"""REPL — talk normally. Full session save/load."""

from __future__ import annotations

import sys

try:
    from form.open import Program, open_program
    from form.dell_matrix.plane import Skin
    from form.mandell.translate import translate
    from form.avatar import Facing, Posture, Locomotion, Expression
    from form.persist import load as persist_load
except ImportError:
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from form.open import Program, open_program
    from form.dell_matrix.plane import Skin
    from form.mandell.translate import translate
    from form.avatar import Facing, Posture, Locomotion, Expression
    from form.persist import load as persist_load

HELP = """
Talk normally.

  create an idea called grocery list
  grow ideas 2
  proposals / confirm <id> / reject <id>
  walk forward / smile / how do I look
  visual
  save          ← saves matrix + avatar + nursery
  load          ← restores last session
  help / quit
""".strip()

_FACING = {
    "n": Facing.N, "north": Facing.N, "s": Facing.S, "south": Facing.S,
    "e": Facing.E, "east": Facing.E, "w": Facing.W, "west": Facing.W,
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
        _say("Nursery is empty. Nothing waiting.")
        return
    _say(f"Nursery has {len(pending)} proposal(s):")
    for i, prop in enumerate(pending[:20], 1):
        _say(f"  {i}. [{prop.get('kind')}] {prop['id']}")
        _say(f"      {prop['label']}  (affinity {prop.get('affinity', 0):.2f})")
    _say("Type: confirm <id>   or   reject <id>")


def _execute_intent(p: Program, intent, raw_line: str = "") -> Program:
    """Returns program (may be replaced on load)."""
    action = intent.action
    args = intent.args or {}
    lower = raw_line.lower().strip()

    if lower in ("proposals", "nursery", "void", "pending"):
        _show_proposals(p)
        return p

    if lower.startswith("confirm "):
        pid = raw_line.split(maxsplit=1)[1].strip()
        res = p.confirm_proposal(pid)
        if res.get("ok"):
            _say(f'Confirmed. "{res["label"]}" is now live in the matrix.')
        else:
            _say(f"Could not confirm: {res.get('reason')}")
        return p

    if lower.startswith("reject "):
        pid = raw_line.split(maxsplit=1)[1].strip()
        res = p.reject_proposal(pid)
        if res.get("ok"):
            _say(f'Rejected. "{res["label"]}" stays out.')
        else:
            _say(f"Could not reject: {res.get('reason')}")
        return p

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
        fog = out.get("fog_cut", 0)
        pending = out.get("nursery", {}).get("pending", 0)
        _say(f"Ringed growth complete ({' → '.join(out.get('rings', []))}).")
        _say(f"Proposed {new_n} new + {evo_n} evolved. FOG cut {fog}.")
        _say(f"Nursery pending: {pending}. Nothing is live until you confirm.")
        _say("Type: proposals")

    elif action == "show":
        print()
        print(p.render())

    elif action == "visual":
        paths = p.visual()
        easy = paths.get("easy") or paths.get("html", "")
        _say("Visual control panel ready (offline).")
        _say("Open this file in any browser:")
        _say(easy)

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
        ns = p.nursery.summary()
        _say("Session saved.")
        _say(f"  ideas: {len(p.cube.session.plane.units)}")
        _say(f"  avatar: {p.avatar.describe()}")
        _say(f"  nursery pending: {ns['pending']}")
        _say(f"  file: {path}")

    elif action == "load":
        p2 = persist_load(p.owner)
        ns = p2.nursery.summary()
        _say("Session loaded.")
        _say(f"  ideas: {len(p2.cube.session.plane.units)}")
        _say(f"  avatar: {p2.avatar.describe()}")
        _say(f"  nursery pending: {ns['pending']}")
        print()
        print(p2.render())
        return p2

    elif action == "status":
        st = p.avatar_status()
        ns = p.nursery.summary()
        _say(f"{st['look']}  {st['describe']}")
        _say(f"Live ideas: {len(p.cube.session.plane.units)}")
        _say(f"Nursery pending: {ns['pending']}")
        _say(f"Rings: {' → '.join(p.duo.rings)} (Voynich-inspired)")

    elif action == "help":
        print()
        print(HELP)
        print()

    else:
        uid = args.get("id", "idea")
        label = args.get("label", intent.english[:48])
        p.place(uid, label, words=intent.english, skin=Skin.CUBE)
        _say(f'Created idea: "{label}"')

    return p


def run(owner: str = "Operator", do_load: bool = False) -> None:
    print()
    print("  DellMatrix — full session save/load")
    print("  Growth quarantined · Voynich-inspired rings")
    print()
    p = persist_load(owner) if do_load else open_program(owner)
    if do_load:
        _say(f"Loaded session for {owner}.")
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
        p = _execute_intent(p, intent, raw_line=line)

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
