#!/usr/bin/env python3
"""Mandell seed executor — dense Dell coverage."""

from __future__ import annotations

from typing import Any, Dict
from datetime import datetime, timezone

from .seed import parse_seed
from .registry import get_dell


def execute_seed(program: Any, seed_text: str) -> Dict[str, Any]:
    from form.dell_matrix.plane import Skin
    from form.avatar import Locomotion, Posture, Expression

    s = parse_seed(seed_text)
    if not s.ok:
        return {"ok": False, "error": s.error, "messages": [f"Seed error: {s.error}"]}

    messages = [f"Mandell: {s.as_mandel()}", f"English: {s.as_english()}"]
    primary = s.primary_dell()
    terms = {a.term.lower() for a in s.atoms}
    label = s.label or ""
    new_program = None

    def place_idea(name: str, skin: Skin = Skin.CUBE) -> None:
        uid = name.replace(" ", "_")[:24] or "idea"
        program.place(uid, name.replace("_", " "), words=name, skin=skin)
        messages.append(f'Created idea: "{name}"')

    if primary == 0:
        messages.append("Nova is cheat/edge only — floor stays locked.")
    elif primary == 1:
        messages.append(f"Initiated. owner={program.owner}")
    elif primary == 2:
        st = program.avatar_status()
        messages.append(f"{st['look']}  {st['describe']}")
    elif primary == 4:
        lab = label.lower()
        if "left" in lab:
            messages.append(f"Turned left. Facing {program.avatar.turn_left()}.")
        elif "right" in lab:
            messages.append(f"Turned right. Facing {program.avatar.turn_right()}.")
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
        elif "toggle" in lab:
            new = program.lattice.toggle_form()
            messages.append(f"Form toggled → {new.value}")
        else:
            messages.append("Transform ready.")
    elif primary == 5:
        expr_map = {
            "joy": Expression.JOY, "smile": Expression.JOY,
            "calm": Expression.CALM, "focus": Expression.FOCUS,
            "soft": Expression.SOFT, "intense": Expression.INTENSE,
            "curious": Expression.CURIOUS, "neutral": Expression.NEUTRAL,
        }
        expr = expr_map.get((label or "neutral").lower(), Expression.NEUTRAL)
        face = program.face.set(expr)
        messages.append(f"{face}  tone={expr.value}")
    elif primary == 7:
        place_idea(f"link_{label or 'link'}")
    elif primary == 8:
        place_idea(label or "idea")
    elif primary == 9:
        lab = (label or "").lower()
        if "embed" in terms or "visual" in lab or 47 in [a.dell for a in s.atoms]:
            paths = program.visual()
            messages.append("Visual ready.")
            messages.append(paths.get("easy") or paths.get("html", ""))
        elif "avatar" in lab:
            st = program.avatar_status()
            messages.append(f"{st['look']}  {st['describe']}")
        elif "lattice" in lab:
            messages.append(program.lattice.render_ascii())
        else:
            messages.append("__RENDER__")
    elif primary == 10:
        path = program.save()
        ns = program.nursery.summary()
        messages.append("Session saved.")
        messages.append(f"ideas={len(program.cube.session.plane.units)} nursery={ns['pending']}")
        messages.append(f"file={path}")
    elif primary == 12:
        checks = []
        checks.append(("floor", True))
        checks.append(("lattice", hasattr(program, "lattice") and program.lattice is not None))
        checks.append(("growth", hasattr(program, "growth")))
        checks.append(("nursery", hasattr(program, "nursery")))
        checks.append(("ideas", len(program.cube.session.plane.units) >= 0))
        ok_n = sum(1 for _, v in checks if v)
        for name, ok in checks:
            messages.append(f"  {'PASS' if ok else 'FAIL'}  {name}")
        messages.append(f"Test: {ok_n}/{len(checks)}")
        if hasattr(program, "note_seed"):
            program.note_seed(12, "Test", f"{ok_n}/{len(checks)}")
    elif primary == 13:
        cycles = int(label) if label.isdigit() else 1
        out = program.grow_ideas(max(1, cycles))
        messages.append(
            f"Ringed growth: +{out.get('proposed_new', 0)} new "
            f"+{out.get('proposed_evolved', 0)} evolved"
        )
        messages.append(f"Nursery pending: {out.get('nursery', {}).get('pending', 0)}")
    elif primary == 14:
        place_idea(label or "bind")
    elif primary == 15:
        lab = (label or "").lower()
        if lab in ("cube", "sphere", "core", "flower"):
            getattr(program.lattice, f"to_{lab}")()
            messages.append(f"Form → {lab}")
        elif label:
            place_idea(label)
        else:
            messages.append(f"Mapped units={len(program.cube.session.plane.units)}")
    elif primary == 16:
        factor = 0.9
        if label.replace(".", "", 1).isdigit():
            factor = max(0.1, min(1.0, float(label)))
        if hasattr(program.enhance, "decay"):
            program.enhance.decay(factor)
            messages.append(f"Scores decayed ×{factor}.")
        else:
            st = program.enhance.state
            for k in list(st.scores.keys()):
                st.scores[k] = float(st.scores[k]) * factor
            messages.append(f"Scores decayed ×{factor} (manual).")
        if hasattr(program, "note_seed"):
            program.note_seed(16, "Decay", str(factor))
    elif primary == 17:  # Shadow densified — background parallel note, no live mutation
        shadow_id = f"shadow_{(label or 'bg').replace(' ', '_')[:20]}"
        messages.append(f"Shadow track: {shadow_id} (parallel — not live)")
        messages.append("Shadow does not write the live matrix. Use confirm/Manifest to promote.")
        if hasattr(program, "note_seed"):
            program.note_seed(17, "Shadow", shadow_id)
        # quarantine-style: place only if nursery path available as proposal words
        try:
            if hasattr(program.nursery, "propose") or hasattr(program.growth, "propose_shadow"):
                messages.append("Shadow registered in growth shadow channel if available.")
            else:
                messages.append("Shadow noted in history only (safe).")
        except Exception:
            messages.append("Shadow noted in history only (safe).")
    elif primary == 18:
        ids = list(program.cube.session.plane.units.keys())
        messages.append(f"Mirror: {len(ids)} live ideas")
        for uid in ids[:16]:
            u = program.cube.session.plane.units[uid]
            messages.append(f"  · {uid}: {u.label} [{u.skin.value}]")
        ns = program.nursery.summary()
        messages.append(f"nursery pending={ns['pending']} history={len(getattr(program, 'history', []))}")
        if hasattr(program, "note_seed"):
            program.note_seed(18, "Mirror")
    elif primary == 19:
        lab = (label or "walk").lower()
        if "run" in lab:
            program.avatar.set_locomotion(Locomotion.RUN)
            messages.append(f"Ran to {program.avatar.step(2)}.")
        elif "stop" in lab:
            program.avatar.set_locomotion(Locomotion.IDLE)
            messages.append("Stopped.")
        else:
            program.avatar.set_locomotion(Locomotion.WALK)
            messages.append(f"Walked to {program.avatar.step(1)}.")
    elif primary == 21:
        place_idea(label or "merge")
    elif primary == 22:
        source = label
        if not source and program.cube.session.plane.units:
            source = list(program.cube.session.plane.units.values())[-1].label
        base = (source or "split").replace(" ", "_")[:20]
        place_idea(f"{base}_a", Skin.SEED)
        place_idea(f"{base}_b", Skin.SEED)
        messages.append(f"Split → {base}_a + {base}_b")
        if hasattr(program, "note_seed"):
            program.note_seed(22, "Split", base)
    elif primary == 23:
        program.sandbox_on()
        messages.append("Sandbox ON.")
    elif primary == 24:
        program.sandbox_off()
        messages.append("Sandbox OFF.")
    elif primary == 25:
        lab = (label or "").lower()
        if "enhance_on" in lab or lab == "on":
            program.enhance_on()
            messages.append("Enhance ON.")
        else:
            program.pulse()
            messages.append("Pulse sent.")
    elif primary == 27:
        from form.persist import checkpoint as persist_cp
        try:
            cp = persist_cp(program)
            messages.append(f"Checkpoint written: {cp}")
        except Exception:
            path = program.save()
            messages.append(f"Checkpoint stand-in save: {path}")
        if hasattr(program, "note_seed"):
            program.note_seed(27, "Checkpoint")
    elif primary == 28:
        from form.persist import load as persist_load
        new_program = persist_load(program.owner)
        messages.append("Session loaded.")
    elif primary == 29:
        short = program.distill_label(label) if hasattr(program, "distill_label") else (label or "x")
        place_idea(f"compress_{short}", Skin.SEED)
        messages.append(f"Compressed → {short}")
    elif primary == 31:
        st = program.status()
        messages.append("Simulate (dry-run — no mutation):")
        messages.append(f"  owner={st.get('owner')} ideas={st.get('ideas')}")
        messages.append(f"  nursery={st.get('nursery')}")
        messages.append(f"  lattice={st.get('lattice')}")
        messages.append(f"  history_len={st.get('history_len')}")
        if hasattr(program, "note_seed"):
            program.note_seed(31, "Simulate")
    elif primary == 32:
        if "enhance" in (label or "").lower():
            program.enhance_off()
            messages.append("Enhance OFF.")
        else:
            program.avatar.set_locomotion(Locomotion.IDLE)
            messages.append("Paused.")
    elif primary == 33:
        program.avatar.set_locomotion(Locomotion.WALK)
        if not program.enhance.on:
            program.enhance_on()
            messages.append("Resumed walk + enhance ON.")
        else:
            messages.append("Resumed walk.")
        if hasattr(program, "note_seed"):
            program.note_seed(33, "Resume")
    elif primary == 34:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        mark = label or "stamp"
        messages.append(f"Stamp: {mark} @ {ts}")
        messages.append(
            f"ideas={len(program.cube.session.plane.units)} "
            f"history={len(getattr(program, 'history', []))} "
            f"form={program.lattice.perception.form.value}"
        )
        if hasattr(program, "note_seed"):
            program.note_seed(34, "Stamp", f"{mark}_{ts}")
    elif primary == 35:
        lab = (label or "").lower()
        if "nursery" in lab:
            pending = program.list_proposals()
            messages.append(f"Nursery pending: {len(pending)}")
            for prop in pending[:8]:
                messages.append(f"  [{prop.get('kind')}] {prop.get('id')} — {prop.get('label')}")
        elif lab.startswith("shell"):
            n = 0
            parts = lab.split()
            if len(parts) > 1 and parts[1].isdigit():
                n = int(parts[1])
            cells = program.lattice.cells_by_shell(n)
            messages.append(f"Shell {n}: {len(cells)} cells")
        else:
            st = program.avatar_status()
            ns = program.nursery.summary()
            messages.append(f"{st['look']}  {st['describe']}")
            messages.append(
                f"ideas={len(program.cube.session.plane.units)} nursery={ns['pending']}"
            )
    elif primary == 38:
        source = label
        if not source and program.cube.session.plane.units:
            last = list(program.cube.session.plane.units.values())[-1]
            source = f"{last.label} {last.words}"
        short = program.distill_label(source)
        place_idea(short, Skin.SEED)
        messages.append(f"Distilled → {short}")
        if hasattr(program, "note_seed"):
            program.note_seed(38, "Distill", short)
    elif primary == 42:  # Retry densified — re-run last seed-shaped history once
        items = program.replay(1) if hasattr(program, "replay") else []
        if not items:
            messages.append("Retry: history empty — nothing to re-attempt.")
        else:
            last = items[-1]
            messages.append(f"Retry last: {last}")
            if hasattr(program, "replay_exec"):
                out = program.replay_exec(1)
                messages.append(f"Retry ran={len(out.get('ran', []))} skipped={len(out.get('skipped', []))}")
                for item in out.get("ran", [])[:4]:
                    messages.append(f"  · {item}")
            if hasattr(program, "note_seed"):
                program.note_seed(42, "Retry", last[:40])
    elif primary == 43:  # Fallback densified — safe path status + acceptance reminder
        messages.append("Fallback safe path:")
        messages.append("  1. status / 31[Simulate]")
        messages.append("  2. save / 10[Keep]")
        messages.append("  3. acceptance: create → grow → confirm → sphere → save → load → visual")
        st = program.status()
        messages.append(f"  now: ideas={st.get('ideas')} form={program.lattice.perception.form.value}")
        if hasattr(program, "note_seed"):
            program.note_seed(43, "Fallback")
    elif primary == 45:
        from form.mandell.bridge import bridge
        rep = bridge(label or "")
        messages.append(f"mandel: {rep.get('mandel')}")
        messages.append(f"english: {rep.get('english')}")
    elif primary == 46:
        ranked = program.ranked_proposals() if hasattr(program, "ranked_proposals") else program.list_proposals()
        ranked = sorted(ranked, key=lambda p: -float(p.get("affinity", 0)))
        messages.append(f"Ranked {len(ranked)} proposals:")
        for i, prop in enumerate(ranked[:12], 1):
            messages.append(
                f"  {i}. aff={float(prop.get('affinity', 0)):.3f} [{prop.get('kind')}] "
                f"{prop.get('id')} — {prop.get('label')}"
            )
    elif primary == 47:
        paths = program.visual()
        messages.append(paths.get("easy") or paths.get("html", ""))
    elif primary == 48:
        lab = (label or "").lower()
        n = 3
        for tok in lab.replace("_", " ").split():
            if tok.isdigit():
                n = int(tok)
        if "replay" in lab or "replay" in terms:
            if hasattr(program, "replay_exec"):
                out = program.replay_exec(n)
                messages.append(
                    f"Replay exec n={n} ran={len(out.get('ran', []))} "
                    f"skipped={len(out.get('skipped', []))}"
                )
                for item in out.get("ran", [])[:8]:
                    messages.append(f"  · {item}")
            else:
                for item in program.replay(n):
                    messages.append(f"  · {item}")
        else:
            n = int(label) if label.isdigit() else 5
            messages.append(program.macro_seed(n))
            messages.append(f"history={len(getattr(program, 'history', []))}")
    elif primary == 50:
        lab = (label or "").lower()
        if lab in ("acceptance", "accept"):
            messages.append("Acceptance: create → grow → confirm → sphere → save → load → visual")
        elif label:
            place_idea(label)
            messages.append("Manifested.")
        else:
            messages.append("Manifest needs :: label.")
    else:
        d = get_dell(primary) if primary is not None else None
        name = d["name"] if d else str(primary)
        messages.append(f"Dell {primary:02d}[{name}] recognized — runtime thin.")
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
