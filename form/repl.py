#!/usr/bin/env python3
"""REPL — Mandell Origin. English, seeds, lattice, polyglot, Lupe-ready."""

from __future__ import annotations

import sys

try:
    from form.open import Program, open_program
    from form.dell_matrix.plane import Skin
    from form.mandell.translate import translate
    from form.mandell.seed import looks_like_seed
    from form.mandell.bridge import to_english, to_mandell, bridge
    from form.mandell.executor import execute_seed
    from form.mandell.patterns import teach, list_patterns
    from form.mandell.polyglot import bridge_lang, list_langs
    from form.mandell.phrases import list_phrases, match_phrase
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
    from form.mandell.patterns import teach, list_patterns
    from form.mandell.polyglot import bridge_lang, list_langs
    from form.mandell.phrases import list_phrases, match_phrase
    from form.avatar import Facing, Posture, Locomotion, Expression
    from form.persist import load as persist_load

HELP = """
Mandell Origin — English or seeds.

Ideas / Growth
  create an idea called business
  grow ideas 2
  proposals | confirm <id> | confirm all | reject all
  rank | lineage <id>
  distill <words> | macro [n] | replay [n]

Lattice / Perception
  cube | sphere | core | flower | toggle
  lattice | chord 0 0 | shell 0

Avatar
  walk | turn left/right | sit | stand | smile | how do I look

System
  save | load | visual | status | enhance on/off | pulse
  acceptance | lang list

Bridge
  mandell <english> | english <seed> | es ... | fr ...
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


def _echo_seed(english: str = "", mandel: str = "") -> None:
    if mandel:
        _say(f"Mandell: {mandel}")
        return
    if english:
        hit = match_phrase(english)
        if hit and hit.get("mandel"):
            _say(f"Mandell: {hit['mandel']}")


def _show_proposals(p: Program) -> None:
    pending = p.list_proposals()
    if not pending:
        _say("Nursery is empty.")
        return
    _say(f"Nursery has {len(pending)} proposal(s):")
    for i, prop in enumerate(pending[:20], 1):
        aff = float(prop.get("affinity", 0))
        _say(f"  {i}. aff={aff:.3f} [{prop.get('kind')}] {prop['id']}")
        _say(f"      {prop['label']}")
    _say("Type: confirm <id> | confirm all | reject all | rank | lineage <id>")


def _handle_lattice(p: Program, lower: str, raw: str) -> bool:
    if lower in ("cube", "to cube", "form cube"):
        p.lattice.to_cube()
        _say(f"Form → cube  (skin={p.lattice.perception.skin_name()})")
        _echo_seed(mandel="15[Map] :: cube")
        return True
    if lower in ("sphere", "to sphere", "form sphere"):
        p.lattice.to_sphere()
        _say(f"Form → sphere  (skin={p.lattice.perception.skin_name()})")
        _echo_seed(mandel="15[Map] :: sphere")
        return True
    if lower in ("core", "to core", "form core"):
        p.lattice.to_core()
        _say(f"Form → core  (skin={p.lattice.perception.skin_name()})")
        _echo_seed(mandel="15[Map] :: core")
        return True
    if lower in ("flower", "to flower", "form flower"):
        n = p.lattice.plant_flower(1)
        _say(f"Form → flower  planted {n} centers")
        _echo_seed(mandel="15[Map] :: flower")
        return True
    if lower in ("toggle", "toggle form", "dual"):
        new = p.lattice.toggle_form()
        _say(f"Form toggled → {new.value}")
        _echo_seed(mandel="04[Transform] :: toggle_form")
        return True
    if lower in ("lattice", "show lattice", "lattice status"):
        st = p.lattice.status()
        _say(f"size={st['size']} form={st['form']} dual={st['dual']} skin={st['skin']}")
        _say(f"cells={st['cells']} modules={st['modules']}")
        print()
        print(p.lattice.render_ascii())
        print()
        _echo_seed(mandel="09[Show] :: lattice")
        return True
    if lower.startswith("chord ") or lower == "chord":
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
        _echo_seed(mandel="35[Discover] :: chord")
        return True
    if lower.startswith("shell") or lower == "shell":
        parts = raw.split()
        try:
            n = int(parts[1]) if len(parts) > 1 else 0
        except ValueError:
            n = 0
        cells = p.lattice.cells_by_shell(n)
        _say(f"Shell {n}: {len(cells)} cell(s)")
        for c in cells[:24]:
            _say(f"  ({c.h},{c.v},{c.f})  {c.label or '—'}")
        return True
    return False


def _handle_macro_rank(p: Program, lower: str, raw: str) -> bool:
    """Early English handlers — not seed-only."""
    if lower in ("rank", "rank proposals"):
        ranked = p.ranked_proposals() if hasattr(p, "ranked_proposals") else p.list_proposals()
        if not ranked:
            _say("Nursery is empty.")
            return True
        _say(f"Ranked {len(ranked)} proposals:")
        for i, prop in enumerate(ranked[:12], 1):
            _say(
                f"  {i}. aff={float(prop.get('affinity', 0)):.3f} "
                f"[{prop.get('kind')}] {prop.get('id')} — {prop.get('label')}"
            )
        _echo_seed(mandel="46[Rank]")
        return True

    if lower == "macro" or lower.startswith("macro "):
        parts = raw.split()
        n = 5
        if len(parts) > 1 and parts[1].isdigit():
            n = int(parts[1])
        seed = p.macro_seed(n)
        _say(seed)
        _say(f"history={len(p.history)}")
        _echo_seed(mandel=f"48[Macro] :: {n}")
        return True

    if lower == "replay" or lower.startswith("replay "):
        parts = raw.split()
        n = 3
        if len(parts) > 1 and parts[1].isdigit():
            n = int(parts[1])
        if hasattr(p, "replay_exec"):
            out = p.replay_exec(n)
            _say(f"Replay n={n} ran={len(out.get('ran', []))} skipped={len(out.get('skipped', []))}")
            for item in out.get("ran", [])[:8]:
                _say(f"  · {item}")
            for item in out.get("skipped", [])[:4]:
                _say(f"  skip {item}")
        else:
            for item in p.replay(n):
                _say(f"  · {item}")
        _echo_seed(mandel="48[Macro] >> 13[Loop] :: replay")
        return True

    if lower.startswith("distill") or lower.startswith("summarize"):
        text = raw.split(maxsplit=1)[1] if " " in raw else ""
        if not text and p.cube.session.plane.units:
            last = list(p.cube.session.plane.units.values())[-1]
            text = f"{last.label} {last.words}"
        short = p.distill_label(text)
        p.place(short, short.replace("_", " "), words=text or short, skin=Skin.SEED)
        _say(f"Distilled → {short}")
        _echo_seed(mandel=f"38[Distill] :: {short}")
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

    if _handle_lattice(p, lower, raw_line):
        return p
    if _handle_macro_rank(p, lower, raw_line):
        return p

    if lower in ("proposals", "nursery", "void", "pending"):
        _show_proposals(p)
        return p

    if lower in ("lang list", "langs", "languages"):
        _say("Supported: " + ", ".join(list_langs()))
        _echo_seed(mandel="35[Discover] :: lang_list")
        return p

    if lower.startswith("lineage "):
        pid = raw_line.split(maxsplit=1)[1].strip()
        prop = p.nursery.proposals.get(pid)
        if prop:
            _say(f"Proposal {prop.id} [{prop.kind}] {prop.label}")
            _say(f"  parents: {prop.parents or '—'}")
            _say(f"  affinity: {prop.affinity:.3f}")
            _say(f"  status: {prop.status}")
            return p
        unit = p.cube.session.plane.units.get(pid)
        if unit:
            _say(f"Live idea {pid}: {unit.label}")
            kids = [pr for pr in p.nursery.proposals.values() if pid in (pr.parents or [])]
            _say(f"  nursery children: {len(kids)}")
            return p
        _say(f"No proposal or idea for id: {pid}")
        return p

    if lower in ("confirm all", "confirm-all"):
        pending = p.list_proposals()
        if not pending:
            _say("Nursery is empty.")
            return p
        n = 0
        for prop in list(pending):
            res = p.confirm_proposal(prop["id"])
            if res.get("ok"):
                n += 1
                _say(f'Confirmed: "{res["label"]}"')
        _say(f"Confirmed {n} proposal(s).")
        return p

    if lower in ("reject all", "reject-all"):
        pending = p.list_proposals()
        n = 0
        for prop in list(pending):
            if p.reject_proposal(prop["id"]).get("ok"):
                n += 1
        _say(f"Rejected {n} proposal(s).")
        return p

    if lower.startswith("confirm "):
        pid = raw_line.split(maxsplit=1)[1].strip()
        res = p.confirm_proposal(pid)
        _say(f'Confirmed. "{res["label"]}" is live.' if res.get("ok") else f"Could not confirm: {res.get('reason')}")
        return p

    if lower.startswith("reject "):
        pid = raw_line.split(maxsplit=1)[1].strip()
        res = p.reject_proposal(pid)
        _say("Rejected." if res.get("ok") else f"Could not reject: {res.get('reason')}")
        return p

    if lower in ("acceptance", "accept", "cold start", "coldstart"):
        _say("Acceptance: create → grow → confirm → sphere → save → load → visual")
        return p

    if lower.startswith("teach "):
        print()
        print(teach(raw_line.split(maxsplit=1)[1].strip()))
        print()
        return p

    if lower in ("patterns", "pattern list"):
        for pat in list_patterns():
            _say(f"{pat['name']}: {pat['mandel']} — {pat['english']}")
        return p

    if lower in ("phrases", "phrase list"):
        for ph in list_phrases()[:30]:
            _say(f"{ph['hint']}: {ph['mandel']}")
        return p

    if lower.startswith("mandell ") or lower.startswith("to mandell "):
        _say(to_mandell(raw_line.split(maxsplit=1)[1]))
        return p

    if lower.startswith("english ") or lower.startswith("to english "):
        _say(to_english(raw_line.split(maxsplit=1)[1]))
        return p

    if lower.startswith("bridge "):
        rep = bridge(raw_line.split(maxsplit=1)[1])
        _say(f"mandel:  {rep.get('mandel')}")
        _say(f"english: {rep.get('english')}")
        return p

    if lower.startswith("es ") or lower.startswith("spanish "):
        text = raw_line.split(maxsplit=1)[1]
        rep = bridge_lang("es", text)
        _say(f"english: {rep.get('english')}")
        _say(f"mandel:  {rep.get('mandel')}")
        if rep.get("ok") == "true" and rep.get("english"):
            return _execute_intent(p, translate(rep["english"]), raw_line=rep["english"])
        return p

    if lower.startswith("fr ") or lower.startswith("french "):
        text = raw_line.split(maxsplit=1)[1]
        rep = bridge_lang("fr", text)
        _say(f"english: {rep.get('english')}")
        _say(f"mandel:  {rep.get('mandel')}")
        if rep.get("ok") == "true" and rep.get("english"):
            return _execute_intent(p, translate(rep["english"]), raw_line=rep["english"])
        return p

    if action == "place":
        uid = args.get("id", "idea")
        label = args.get("label", uid)
        p.place(uid, label, words=args.get("words", ""), skin=Skin.CUBE)
        _say(f'Created idea: "{label}"')
        _echo_seed(raw_line, intent.mandel or "")

    elif action == "grow":
        n = int(args.get("cycles", 1))
        out = p.grow_ideas(n)
        _say("Ringed growth complete.")
        _say(f"Proposed {out.get('proposed_new', 0)} new + {out.get('proposed_evolved', 0)} evolved.")
        _say(f"Nursery pending: {out.get('nursery', {}).get('pending', 0)}")
        _echo_seed(mandel="13[Loop] > 04[Transform] :: grow")

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
        if hasattr(p, "note_seed"):
            p.note_seed(19, "Drive", "walk")
        _say(f"You walked forward {steps}. Now at {pos}.")

    elif action == "run":
        p.avatar.set_locomotion(Locomotion.RUN)
        pos = p.avatar.step(2)
        if hasattr(p, "note_seed"):
            p.note_seed(19, "Drive", "run")
        _say(f"You ran to {pos}.")

    elif action == "stop":
        p.avatar.set_locomotion(Locomotion.IDLE)
        if hasattr(p, "note_seed"):
            p.note_seed(32, "Pause", "stop")
        _say("You stopped.")

    elif action == "turn":
        direction = args.get("direction", "right")
        facing = p.avatar.turn_left() if direction == "left" else p.avatar.turn_right()
        if hasattr(p, "note_seed"):
            p.note_seed(4, "Transform", f"turn_{direction}")
        _say(f"You turned {direction}. Facing {facing}.")

    elif action == "face":
        d = str(args.get("direction", "n")).lower()
        facing = _FACING.get(d, Facing.N)
        p.avatar.face(facing)
        _say(f"Facing {facing.name}.")

    elif action == "sit":
        p.avatar.set_posture(Posture.SIT)
        if hasattr(p, "note_seed"):
            p.note_seed(4, "Transform", "sit")
        _say("You sat down.")

    elif action == "stand":
        p.avatar.set_posture(Posture.STAND)
        if hasattr(p, "note_seed"):
            p.note_seed(4, "Transform", "stand")
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
        if hasattr(p, "note_seed"):
            p.note_seed(5, "Tone", name)
        _say(f"{face}  You look {name}.")

    elif action == "avatar_status":
        st = p.avatar_status()
        _say(f"{st['look']}  {st['describe']}")

    elif action == "enhance_on":
        p.enhance_on()
        if hasattr(p, "note_seed"):
            p.note_seed(25, "Pulse", "enhance_on")
        _say("Enhance ON.")

    elif action == "enhance_off":
        p.enhance_off()
        if hasattr(p, "note_seed"):
            p.note_seed(32, "Pause", "enhance_off")
        _say("Enhance OFF.")

    elif action == "pulse":
        p.pulse()
        if hasattr(p, "note_seed"):
            p.note_seed(25, "Pulse")
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
        _say(f"lattice form={lat['form']} cells={lat['cells']} history={len(p.history)}")

    elif action == "help":
        print()
        print(HELP)
        print()

    else:
        uid = args.get("id", "idea")
        label = args.get("label", intent.english[:48])
        p.place(uid, label, words=intent.english, skin=Skin.CUBE)
        _say(f'Created idea: "{label}"')
        _echo_seed(raw_line, intent.mandel or "")

    return p


def run(owner: str = "Operator", do_load: bool = False) -> None:
    print()
    print("  DellMatrix — Mandell Origin")
    print("  English · Seeds · Lattice · Perception · Polyglot · Lupe-ready")
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
