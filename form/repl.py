#!/usr/bin/env python3
"""REPL — Mandell Origin. English, seeds, patterns, polyglot bridge, lattice."""

from __future__ import annotations

import sys

try:
    from form.open import Program, open_program
    from form.dell_matrix.plane import Skin
    from form.mandell.translate import translate
    from form.mandell.seed import looks_like_seed
    from form.mandell.bridge import to_english, to_mandell, bridge
    from form.mandell.executor import execute_seed
    from form.mandell.patterns import teach, list_patterns, get_pattern
    from form.mandell.polyglot import bridge_lang
    from form.mandell.phrases import list_phrases
    from form.avatar import Facing, Posture, Locomotion, Expression
    from form.persist import load as persist_load
except ImportError:
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from form.open import Program, open_program
    from form.dell_matrix.plane import Skin
    from form.mandell.translate import translate
    from form.mandell.seed import looks_like_seed
    from form.mandell.bridge import to_english, to_mandell, bridge
    from form.mandell.executor import execute_seed
    from form.mandell.patterns import teach, list_patterns, get_pattern
    from form.mandell.polyglot import bridge_lang
    from form.mandell.phrases import list_phrases
    from form.avatar import Facing, Posture, Locomotion, Expression
    from form.persist import load as persist_load

HELP = """
Mandell Origin — English or seeds.

  create an idea called business
  08[Create] > 15[Map] :: business
  grow ideas 2
  save / load / visual / proposals / confirm <id>

Lattice / Perception:
  cube | sphere | core | flower | toggle
  lattice
  chord 0 0

Teach:
  teach loop | patterns | phrases

Bridge:
  mandell <english>
  english <seed>
  es ... | fr ...
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
        _say("Nursery is empty.")
        return
    _say(f"Nursery has {len(pending)} proposal(s):")
    for i, prop in enumerate(pending[:20], 1):
        _say(f"  {i}. [{prop.get('kind')}] {prop['id']}")
        _say(f"      {prop['label']}")
    _say("Type: confirm <id>  or  reject <id>")


def _handle_lattice(p: Program, lower: str, raw: str) -> bool:
    """Return True if command was a lattice/perception command."""
    if lower in ("cube", "to cube", "form cube"):
        p.lattice.to_cube()
        _say(f"Form → cube  (skin={p.lattice.perception.skin_name()})")
        return True
    if lower in ("sphere", "to sphere", "form sphere"):
        p.lattice.to_sphere()
        _say(f"Form → sphere  (skin={p.lattice.perception.skin_name()})")
        return True
    if lower in ("core", "to core", "form core"):
        p.lattice.to_core()
        _say(f"Form → core  (skin={p.lattice.perception.skin_name()})")
        return True
    if lower in ("flower", "to flower", "form flower"):
        n = p.lattice.plant_flower(1)
        _say(f"Form → flower  planted {n} centers  (skin={p.lattice.perception.skin_name()})")
        return True
    if lower in ("toggle", "toggle form", "dual"):
        new = p.lattice.toggle_form()
        _say(f"Form toggled → {new.value}  (skin={p.lattice.perception.skin_name()})")
        return True
    if lower in ("lattice", "show lattice", "lattice status"):
        st = p.lattice.status()
        _say(f"size={st['size']} form={st['form']} dual={st['dual']} skin={st['skin']}")
        _say(f"cells={st['cells']} modules={st['modules']} origin={st['example_origin']}")
        print()
        print(p.lattice.render_ascii())
        print()
        return True
    if lower.startswith("chord "):
        parts = raw.split()
        try:
            h = int(parts[1]) if len(parts) > 1 else 0
            v = int(parts[2]) if len(parts) > 2 else 0
            f = int(parts[3]) if len(parts) > 3 else 0
        except ValueError:
            h = v = f = 0
        chord = p.lattice.pull_chord(h, v, f)
        _say(f"Chord at ({h},{v},{f}):")
        for c in chord:
            mark = "●" if c["has_content"] else "·"
            _say(f"  {mark} {c['coords']}  {c['note']}  shell={c['shell']}  {c['label'] or '—'}")
        return True
    if lower == "chord":
        chord = p.lattice.pull_chord(0, 0, 0)
        _say("Chord at origin (0,0,0):")
        for c in chord:
            mark = "●" if c["has_content"] else "·"
            _say(f"  {mark} {c['coords']}  {c['note']}  shell={c['shell']}  {c['label'] or '—'}")
        return True
    return False


def _apply_seed_result(p: Program, result: dict) -> Program:
    for msg in result.get("messages") or []:
        if msg == "__RENDER__":
            print()
            print(p.render())
        else:
            _say(msg)
    if result.get("new_program") is not None:
        p2 = result["new_program"]
        print()
        print(p2.render())
        return p2
    return p


def _execute_intent(p: Program, intent, raw_line: str = "") -> Program:
    action = intent.action
    args = intent.args or {}
    lower = raw_line.lower().strip()

    # --- Lattice / Perception (NBD) ---
    if _handle_lattice(p, lower, raw_line):
        return p

    if lower in ("proposals", "nursery", "void", "pending"):
        _show_proposals(p)
        return p

    if lower.startswith("confirm "):
        pid = raw_line.split(maxsplit=1)[1].strip()
        res = p.confirm_proposal(pid)
        _say(f'Confirmed. "{res["label"]}" is live.' if res.get("ok") else f"Could not confirm: {res.get('reason')}")
        return p

    if lower.startswith("reject "):
        pid = raw_line.split(maxsplit=1)[1].strip()
        res = p.reject_proposal(pid)
        _say(f'Rejected.' if res.get("ok") else f"Could not reject: {res.get('reason')}")
        return p

    if lower.startswith("teach "):
        name = raw_line.split(maxsplit=1)[1].strip()
        print()
        print(teach(name))
        print()
        return p

    if lower in ("patterns", "pattern list"):
        for pat in list_patterns():
            _say(f"{pat['name']}: {pat['mandel']} — {pat['english']}")
        return p

    if lower in ("phrases", "phrase list"):
        for ph in list_phrases()[:25]:
            _say(f"{ph['hint']}: {ph['mandel']}")
        return p

    if lower.startswith("mandell ") or lower.startswith("to mandell "):
        text = raw_line.split(maxsplit=1)[1]
        _say(to_mandell(text))
        return p

    if lower.startswith("english ") or lower.startswith("to english "):
        text = raw_line.split(maxsplit=1)[1]
        _say(to_english(text))
        return p

    if lower.startswith("bridge "):
        text = raw_line.split(maxsplit=1)[1]
        rep = bridge(text)
        _say(f"mandel:  {rep.get('mandel')}")
        _say(f"english: {rep.get('english')}")
        return p

    if lower.startswith("es ") or lower.startswith("spanish "):
        text = raw_line.split(maxsplit=1)[1]
        rep = bridge_lang("es", text)
        _say(f"english: {rep.get('english')}")
        _say(f"mandel:  {rep.get('mandel')}")
        if rep.get("ok") == "true" and rep.get("english"):
            intent2 = translate(rep["english"])
            return _execute_intent(p, intent2, raw_line=rep["english"])
        return p

    if lower.startswith("fr ") or lower.startswith("french "):
        text = raw_line.split(maxsplit=1)[1]
        rep = bridge_lang("fr", text)
        _say(f"english: {rep.get('english')}")
        _say(f"mandel:  {rep.get('mandel')}")
        if rep.get("ok") == "true" and rep.get("english"):
            intent2 = translate(rep["english"])
            return _execute_intent(p, intent2, raw_line=rep["english"])
        return p

    if action == "place":
        uid = args.get("id", "idea")
        label = args.get("label", uid)
        p.place(uid, label, words=args.get("words", ""), skin=Skin.CUBE)
        _say(f'Created idea: "{label}"')
        if intent.mandel:
            _say(f"Mandell: {intent.mandel}")

    elif action == "grow":
        n = int(args.get("cycles", 1))
        out = p.grow_ideas(n)
        _say(f"Ringed growth complete.")
        _say(f"Proposed {out.get('proposed_new', 0)} new + {out.get('proposed_evolved', 0)} evolved.")
        _say(f"Nursery pending: {out.get('nursery', {}).get('pending', 0)}")

    elif action == "show":
        print()
        print(p.render())

    elif action == "visual":
        paths = p.visual()
        _say("Visual ready:")
        _say(paths.get("easy") or paths.get("html", ""))

    elif action == "walk":
        steps = int(args.get("steps", 1))
        p.avatar.set_locomotion(Locomotion.WALK)
        pos = p.avatar.step(steps)
        _say(f"You walked forward {steps}. Now at {pos}, facing {p.avatar.body.facing.name}.")

    elif action == "run":
        p.avatar.set_locomotion(Locomotion.RUN)
        pos = p.avatar.step(2)
        _say(f"You ran to {pos}.")

    elif action == "stop":
        p.avatar.set_locomotion(Locomotion.IDLE)
        _say("You stopped.")

    elif action == "turn":
        direction = args.get("direction", "right")
        facing = p.avatar.turn_left() if direction == "left" else p.avatar.turn_right()
        _say(f"You turned {direction}. Facing {facing}.")

    elif action == "face":
        d = str(args.get("direction", "n")).lower()
        facing = _FACING.get(d, Facing.N)
        p.avatar.face(facing)
        _say(f"Facing {facing.name}.")

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

    elif action == "express":
        name = args.get("expression", "neutral")
        face = p.face.set(_EXPR.get(name, Expression.NEUTRAL))
        _say(f"{face}  You look {name}.")

    elif action == "avatar_status":
        st = p.avatar_status()
        _say(f"{st['look']}  {st['describe']}")

    elif action == "enhance_on":
        p.enhance_on()
        _say("Enhance ON.")

    elif action == "enhance_off":
        p.enhance_off()
        _say("Enhance OFF.")

    elif action == "pulse":
        p.pulse()
        _say("Pulse sent.")

    elif action == "sandbox_on":
        p.sandbox_on()
        _say("Sandbox ON.")

    elif action == "sandbox_off":
        p.sandbox_off()
        _say("Sandbox OFF.")

    elif action == "save":
        path = p.save()
        ns = p.nursery.summary()
        _say("Session saved.")
        _say(f"ideas={len(p.cube.session.plane.units)} nursery={ns['pending']} lattice_cells={len(p.lattice.cells)}")
        _say(f"file={path}")

    elif action == "load":
        p2 = persist_load(p.owner)
        _say("Session loaded.")
        print()
        print(p2.render())
        return p2

    elif action == "status":
        st = p.avatar_status()
        ns = p.nursery.summary()
        lat = p.lattice.status()
        _say(f"{st['look']}  {st['describe']}")
        _say(f"ideas={len(p.cube.session.plane.units)} nursery={ns['pending']}")
        _say(f"lattice form={lat['form']} cells={lat['cells']}")

    elif action == "help":
        print()
        print(HELP)
        print()

    else:
        uid = args.get("id", "idea")
        label = args.get("label", intent.english[:48])
        p.place(uid, label, words=intent.english, skin=Skin.CUBE)
        _say(f'Created idea: "{label}"')
        if intent.mandel:
            _say(f"Mandell: {intent.mandel}")

    return p


def run(owner: str = "Operator", do_load: bool = False) -> None:
    print()
    print("  DellMatrix — Mandell Origin")
    print("  English · Seeds · Lattice · Perception")
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

        if looks_like_seed(line):
            result = execute_seed(p, line)
            p = _apply_seed_result(p, result)
            continue

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
