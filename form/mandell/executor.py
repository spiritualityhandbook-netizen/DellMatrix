#!/usr/bin/env python3
"""
Mandell seed executor — dense Dell coverage.

Maps parsed seeds onto Program actions.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Tuple

from .seed import Seed, parse_seed
from .registry import get_dell


def execute_seed(program: Any, seed_text: str) -> Dict[str, Any]:
    """
    Run a Mandell seed against a Program-like object.
    Returns a result dict with ok, messages, and optional new_program.
    """
    from form.dell_matrix.plane import Skin
    from form.avatar import Locomotion, Posture, Expression, Facing

    s = parse_seed(seed_text)
    if not s.ok:
        return {"ok": False, "error": s.error, "messages": [f"Seed error: {s.error}"]}

    messages = [f"Mandell: {s.as_mandel()}", f"English: {s.as_english()}"]
    primary = s.primary_dell()
    terms = {a.term.lower() for a in s.atoms}
    label = s.label or ""
    new_program = None

    def place_idea(name: str) -> None:
        uid = name.replace(" ", "_")[:24] or "idea"
        program.place(uid, name.replace("_", " "), words=name, skin=Skin.CUBE)
        messages.append(f'Created idea: "{name}"')

    # --- Dell coverage ---
    if primary == 0:  # Nova — fresh note only
        messages.append("Nova is cheat/edge only — floor stays locked.")

    elif primary == 1:  # Initiate
        messages.append(f"Initiated. owner={program.owner}")

    elif primary == 2:  # Persona / avatar focus
        st = program.avatar_status()
        messages.append(f"{st['look']}  {st['describe']}")

    elif primary == 4:  # Transform — posture / turn from label
        lab = label.lower()
        if "left" in lab:
            facing = program.avatar.turn_left()
            messages.append(f"Turned left. Facing {facing}.")
        elif "right" in lab:
            facing = program.avatar.turn_right()
            messages.append(f"Turned right. Facing {facing}.")
        elif "sit" in lab:
            program.avatar.set_posture(Posture.SIT)
            messages.append("Sat down.")
        elif "stand" in lab:
            program.avatar.set_posture(Posture.STAND)
            messages.append("Stood up.")
        elif "jump" in lab:
            program.avatar.set_posture(Posture.JUMP)
            program.avatar.set_posture(Posture.STAND)
            messages.append("Jumped.")
        elif "bend" in lab:
            program.avatar.set_posture(Posture.BEND)
            messages.append("Bent over.")
        else:
            messages.append("Transform ready — use label sit/stand/jump/turn_left/turn_right.")

    elif primary == 5:  # Tone
        expr_map = {
            "joy": Expression.JOY, "smile": Expression.JOY,
            "calm": Expression.CALM, "focus": Expression.FOCUS,
            "soft": Expression.SOFT, "intense": Expression.INTENSE,
            "curious": Expression.CURIOUS, "neutral": Expression.NEUTRAL,
        }
        key = label.lower() if label else "neutral"
        expr = expr_map.get(key, Expression.NEUTRAL)
        face = program.face.set(expr)
        messages.append(f"{face}  tone={expr.value}")

    elif primary == 7:  # Link — record as idea bridge label
        name = label or "link"
        place_idea(f"link_{name}")

    elif primary == 8:  # Create
        place_idea(label or "idea")

    elif primary == 9:  # Show
        if "embed" in terms or "visual" in (label or "").lower() or 47 in [a.dell for a in s.atoms]:
            paths = program.visual()
            messages.append("Visual ready.")
            messages.append(paths.get("easy") or paths.get("html", ""))
        elif "avatar" in (label or "").lower():
            st = program.avatar_status()
            messages.append(f"{st['look']}  {st['describe']}")
        elif "help" in (label or "").lower():
            messages.append("Help: English or seeds. Type help in REPL for full list.")
        else:
            messages.append("(render)")
            messages.append("__RENDER__")

    elif primary == 10:  # Keep
        path = program.save()
        ns = program.nursery.summary()
        messages.append("Session saved.")
        messages.append(f"ideas={len(program.cube.session.plane.units)} nursery={ns['pending']}")
        messages.append(f"file={path}")

    elif primary == 13:  # Loop / grow
        cycles = 1
        if label.isdigit():
            cycles = max(1, int(label))
        out = program.grow_ideas(cycles)
        messages.append(
            f"Ringed growth: +{out.get('proposed_new', 0)} new "
            f"+{out.get('proposed_evolved', 0)} evolved · FOG cut {out.get('fog_cut', 0)}"
        )
        messages.append(f"Nursery pending: {out.get('nursery', {}).get('pending', 0)}")

    elif primary == 14:  # Bind
        place_idea(label or "bind")

    elif primary == 15:  # Map — often chained after Create
        if label:
            place_idea(label)
        else:
            messages.append(f"Mapped units={len(program.cube.session.plane.units)}")

    elif primary == 16:  # Decay
        if hasattr(program.enhance, "decay"):
            program.enhance.decay(0.9)
            messages.append("Scores decayed ×0.9.")
        else:
            messages.append("Decay noted (enhance decay).")

    elif primary == 18:  # Mirror
        messages.append(f"Mirror: ideas={list(program.cube.session.plane.units.keys())[:12]}")

    elif primary == 19:  # Drive
        lab = (label or "walk").lower()
        if "run" in lab:
            program.avatar.set_locomotion(Locomotion.RUN)
            pos = program.avatar.step(2)
            messages.append(f"Ran to {pos}.")
        elif "stop" in lab:
            program.avatar.set_locomotion(Locomotion.IDLE)
            messages.append("Stopped.")
        else:
            program.avatar.set_locomotion(Locomotion.WALK)
            pos = program.avatar.step(1)
            messages.append(f"Walked to {pos}, facing {program.avatar.body.facing.name}.")

    elif primary == 21:  # Merge
        place_idea(label or "merge")
        messages.append("Merge recorded as idea (full pair-merge UI later).")

    elif primary == 22:  # Split
        place_idea(label or "split")

    elif primary == 23:  # Lock
        program.sandbox_on()
        messages.append("Sandbox ON (locked region).")

    elif primary == 24:  # Unlock
        program.sandbox_off()
        messages.append("Sandbox OFF.")

    elif primary == 25:  # Pulse
        lab = (label or "").lower()
        if "enhance_on" in lab or "on" == lab:
            program.enhance_on()
            messages.append("Enhance ON.")
        else:
            program.pulse()
            messages.append("Pulse sent.")

    elif primary == 27:  # Checkpoint
        if hasattr(program, "checkpoint"):
            cp = program.checkpoint()
            messages.append(f"Checkpoint: {cp}")
        else:
            path = program.save()
            messages.append(f"Saved as checkpoint stand-in: {path}")

    elif primary == 28:  # Rollback / load
        from form.persist import load as persist_load
        new_program = persist_load(program.owner)
        messages.append("Session loaded.")

    elif primary == 29:  # Compress
        place_idea(f"compress_{label or 'x'}")
        messages.append("Compress marker placed (payload shrink is future work).")

    elif primary == 32:  # Pause
        lab = (label or "").lower()
        if "enhance" in lab:
            program.enhance_off()
            messages.append("Enhance OFF.")
        else:
            program.avatar.set_locomotion(Locomotion.IDLE)
            messages.append("Paused / idle.")

    elif primary == 33:  # Resume
        program.avatar.set_locomotion(Locomotion.WALK)
        messages.append("Resumed walk posture.")

    elif primary == 35:  # Discover
        lab = (label or "").lower()
        if "nursery" in lab:
            pending = program.list_proposals()
            messages.append(f"Nursery pending: {len(pending)}")
            for prop in pending[:8]:
                messages.append(f"  [{prop.get('kind')}] {prop.get('id')} — {prop.get('label')}")
        else:
            st = program.avatar_status()
            ns = program.nursery.summary()
            messages.append(f"{st['look']}  {st['describe']}")
            messages.append(
                f"ideas={len(program.cube.session.plane.units)} "
                f"nursery={ns['pending']} gen={program.duo.generation}"
            )

    elif primary == 38:  # Distill
        place_idea(f"distill_{label or 'x'}")
        messages.append("Distill marker placed.")

    elif primary == 45:  # Translate
        from form.mandell.bridge import bridge
        rep = bridge(label or "")
        messages.append(f"mandel: {rep.get('mandel')}")
        messages.append(f"english: {rep.get('english')}")

    elif primary == 47:  # Embed → visual
        paths = program.visual()
        messages.append(paths.get("easy") or paths.get("html", ""))

    elif primary == 50:  # Manifest
        if label:
            place_idea(label)
            messages.append("Manifested into the matrix.")
        else:
            messages.append("Manifest needs a :: label.")

    else:
        d = get_dell(primary) if primary is not None else None
        name = d["name"] if d else str(primary)
        messages.append(f"Dell {primary:02d}[{name}] recognized — runtime binding still thin.")
        if label:
            place_idea(label)

    return {
        "ok": True,
        "seed": s.as_mandel(),
        "english": s.as_english(),
        "primary": primary,
        "messages": messages,
        "new_program": new_program,
    }
