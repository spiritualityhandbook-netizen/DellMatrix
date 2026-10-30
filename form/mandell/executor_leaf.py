#!/usr/bin/env python3
"""Mandell seed executor — dense Dell coverage."""

from __future__ import annotations

from typing import Any, Dict
from datetime import datetime, timezone
import re

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
    # TOAM-I C3: For Dell 8 with typed args, use the 'name' arg as the label.
    # This wires the typed representation to the existing Create authority.
    create_skin = Skin.CUBE
    if primary == 8 and s.atoms:
        atom_args = getattr(s.atoms[0], "args", None) or {}
        if atom_args:
            from form.mandell.signatures import get_signature, has_signature
            if has_signature(8):
                sig = get_signature(8)
                errors = sig.validate(atom_args)
                if errors:
                    err_msg = f"TOAM validation failed for 08[Create]: {'; '.join(errors)}"
                    messages.append(err_msg)
                    return {"ok": False, "error": errors[0], "messages": messages}
                # Use typed name; conflict law: if legacy label differs, fail safely
                typed_name = atom_args.get("name", "")
                from form.idea_create import slug_id
                if label and label != typed_name and label != slug_id(typed_name):
                    # Legacy label is the uid (underscored); typed name is human-readable.
                    # They refer to the same thing if uid matches. Only fail on true conflict.
                    err_msg = f"ARGUMENT_CONFLICT for 08[Create]: typed name='{typed_name}' vs legacy label='{label}'"
                    messages.append(err_msg)
                    return {"ok": False, "error": "ARGUMENT_CONFLICT", "messages": messages}
                if typed_name:
                    label = typed_name
                    messages.append(f"TOAM: typed name='{typed_name}' wired to Create")
                # R4: skin was enum-validated above (validate()
                # refuses non-members before any mutation), so
                # this resolution cannot fail; wire it through.
                if "skin" in atom_args:
                    create_skin = Skin[atom_args["skin"]]
                    messages.append(f"TOAM: typed skin='{atom_args['skin']}' wired to Create")
    new_program = None

    def place_idea(name: str, skin: Skin = Skin.CUBE) -> None:
        # Canonical slug + collision dedup (form/idea_create.py, P3/TD-5):
        # raw-Mandell creation produces the same id parse_and_place would
        # for the same label, and dedups instead of silently overwriting.
        from form.idea_create import slug_id, unique_unit_id
        raw_uid = slug_id(name)
        uid = unique_unit_id(program.cube.session.plane.units, name)
        program.place(uid, name.replace("_", " "), words=name, skin=skin)
        if uid == raw_uid:
            messages.append(f'Created idea: "{name}"')
        else:
            messages.append(f'Created idea: "{name}" (id: {uid})')

    if primary == 0:
        messages.append("Nova is cheat/edge only — floor stays locked.")
    elif primary == 1:
        messages.append(f"Initiated. owner={program.owner}")
    elif primary == 2:
        st = program.avatar_status()
        messages.append(f"{st['look']}  {st['describe']}")
    elif primary == 3:
        messages.append("Logic constraints (live):")
        messages.append("  · Floor locked (Alpha · Delta · Omega · Omni)")
        messages.append("  · Growth never auto-writes live matrix (Nursery only)")
        messages.append("  · RingedGrowth is sole public growth entrypoint")
        messages.append("  · Origin offline — no network required for acceptance")
        if label:
            messages.append(f"  · noted rule: {label}")
        if hasattr(program, "note_seed"):
            program.note_seed(3, "Logic", label or "constraints")
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
    elif primary == 6:
        n = int(label) if label.isdigit() else 1
        n = max(1, min(n, 5))
        out = program.grow_ideas(n)
        messages.append(f"Cycle x{n}: +{out.get('proposed_new', 0)} new +{out.get('proposed_evolved', 0)} evolved")
        messages.append(f"rings: {' → '.join(program.duo.rings)}")
        if hasattr(program, "note_seed"):
            program.note_seed(6, "Cycle", str(n))
    elif primary == 7:
        place_idea(f"link_{label or 'link'}")
    elif primary == 8:
        place_idea(label or "idea", skin=create_skin)
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
    elif primary == 11:
        messages.append("Architect schema:")
        messages.append(f"  owner={program.owner}")
        messages.append(f"  ideas={len(program.cube.session.plane.units)}")
        messages.append(f"  lattice size={program.lattice.size} form={program.lattice.perception.form.value}")
        messages.append(f"  cells={len(program.lattice.cells)}")
        if hasattr(program, "note_seed"):
            program.note_seed(11, "Architect")
    elif primary == 12:
        checks = [
            ("floor", True),
            ("lattice", hasattr(program, "lattice") and program.lattice is not None),
            ("growth", hasattr(program, "growth")),
            ("nursery", hasattr(program, "nursery")),
            ("ideas", len(program.cube.session.plane.units) >= 0),
        ]
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
    elif primary == 17:
        shadow_id = f"shadow_{(label or 'bg').replace(' ', '_')[:20]}"
        messages.append(f"Shadow track: {shadow_id} (parallel — not live)")
        if hasattr(program, "note_seed"):
            program.note_seed(17, "Shadow", shadow_id)
    elif primary == 18:
        ids = list(program.cube.session.plane.units.keys())
        messages.append(f"Mirror: {len(ids)} live ideas")
        for uid in ids[:16]:
            u = program.cube.session.plane.units[uid]
            messages.append(f"  · {uid}: {u.label} [{u.skin.value}]")
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
    elif primary == 20:
        messages.append("Alpha close:")
        messages.append(f"  ideas={len(program.cube.session.plane.units)}")
        messages.append(f"  form={program.lattice.perception.form.value}")
        messages.append("  Tip: save before exit — 10[Keep]")
        if hasattr(program, "note_seed"):
            program.note_seed(20, "Alpha", label or "close")
    elif primary == 21:
        # GDP-001 0.3.1: Dell 21/22 have ONE semantic authority — the front
        # door (executor.execute_seed) via live_identity lineage. The leaf's
        # previous arms reimplemented merge/split with divergent semantics
        # (plain place_idea) and were unreachable through the canonical front
        # door (executor.py intercepts 21/22 before delegating here). They now
        # delegate so every entry path executes the same authority.
        from .executor import execute_seed as _front_door
        _fd = _front_door(program, seed_text)
        _fd_msgs = [m for m in (_fd.get("messages") or [])
                    if not (m.startswith("Mandell:") or m.startswith("English:"))]
        return {**_fd, "messages": messages + _fd_msgs}
    elif primary == 22:
        # GDP-001 0.3.1: same single-authority delegation as Dell 21 above.
        from .executor import execute_seed as _front_door
        _fd = _front_door(program, seed_text)
        _fd_msgs = [m for m in (_fd.get("messages") or [])
                    if not (m.startswith("Mandell:") or m.startswith("English:"))]
        return {**_fd, "messages": messages + _fd_msgs}
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
    elif primary == 26:
        lab = (label or "warm").lower()
        if lab in ("cold", "cool"):
            if program.enhance.on:
                program.enhance_off()
            messages.append("Temp → cold (enhance OFF)")
        elif lab in ("hot", "heat"):
            program.enhance_on()
            program.pulse()
            messages.append("Temp → hot (enhance ON + pulse)")
        else:
            program.enhance_on()
            messages.append("Temp → warm (enhance ON)")
        if hasattr(program, "note_seed"):
            program.note_seed(26, "Temp", lab)
    elif primary == 29:
        short = program.distill_label(label) if hasattr(program, "distill_label") else (label or "x")
        place_idea(f"compress_{short}", Skin.SEED)
        messages.append(f"Compressed → {short}")
    elif primary == 30:
        source = label
        if not source and program.cube.session.plane.units:
            last = list(program.cube.session.plane.units.values())[-1]
            source = f"{last.label} {last.words}".strip()
        parts = [t for t in (source or "expand").replace("_", " ").split() if t]
        expanded = " ".join(parts) if parts else "expand"
        place_idea(f"expand_{expanded.replace(' ', '_')[:24]}", Skin.CUBE)
        messages.append(f"Expanded → {expanded}")
        if hasattr(program, "note_seed"):
            program.note_seed(30, "Expand", expanded[:40])
    elif primary == 31:
        st = program.status()
        messages.append("Simulate (dry-run — no mutation):")
        messages.append(f"  owner={st.get('owner')} ideas={st.get('ideas')}")
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
    elif primary == 36:
        name = label or "inject"
        place_idea(name, Skin.SEED)
        messages.append(f"Injected into scope: {name}")
        if hasattr(program, "note_seed"):
            program.note_seed(36, "Inject", name)
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
    elif primary == 39:
        ok = True
        reasons = []
        if not hasattr(program, "lattice") or program.lattice is None:
            ok = False
            reasons.append("missing lattice")
        if not hasattr(program, "nursery"):
            ok = False
            reasons.append("missing nursery")
        if not hasattr(program, "growth"):
            ok = False
            reasons.append("missing growth")
        messages.append(f"Schema: {'VALID' if ok else 'INVALID'}")
        for r in reasons:
            messages.append(f"  · {r}")
        if hasattr(program, "note_seed"):
            program.note_seed(39, "Schema", "valid" if ok else "invalid")
    elif primary == 41:
        raw = label or ""
        cleaned = re.sub(
            r"(?i)(password|secret|token|api[_-]?key|bearer)\s*[:=]?\s*\S+",
            r"\1=[REDACTED]",
            raw,
        )
        cleaned = re.sub(r"\b\d{12,}\b", "[REDACTED_NUM]", cleaned)
        messages.append(f"Sanitize in:  {raw or '(empty)'}")
        messages.append(f"Sanitize out: {cleaned or '(empty)'}")
        if hasattr(program, "note_seed"):
            program.note_seed(41, "Sanitize")
    elif primary == 42:
        items = program.replay(1) if hasattr(program, "replay") else []
        if not items:
            messages.append("Retry: history empty.")
        else:
            last = items[-1]
            messages.append(f"Retry last: {last}")
            if hasattr(program, "replay_exec"):
                out = program.replay_exec(1)
                messages.append(f"Retry ran={len(out.get('ran', []))} skipped={len(out.get('skipped', []))}")
            if hasattr(program, "note_seed"):
                program.note_seed(42, "Retry", last[:40])
    elif primary == 43:
        messages.append("Fallback safe path:")
        messages.append("  1. status / 31[Simulate]")
        messages.append("  2. save / 10[Keep]")
        messages.append("  3. acceptance: create → grow → confirm → sphere → save → load → visual")
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
            else:
                for item in program.replay(n):
                    messages.append(f"  · {item}")
        else:
            n = int(label) if label.isdigit() else 5
            messages.append(program.macro_seed(n))
    elif primary == 49:
        st = program.status()
        messages.append("Profile:")
        messages.append(f"  owner={st.get('owner')}")
        messages.append(f"  ideas={st.get('ideas')} history={st.get('history_len')}")
        messages.append(f"  nursery={st.get('nursery')}")
        messages.append(f"  lattice={st.get('lattice')}")
        messages.append(f"  enhance={st.get('enhance')}")
        if hasattr(program, "note_seed"):
            program.note_seed(49, "Profile")
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
        # P0-R2 MUST_FIX + ARGUS 2a: dells this leaf cannot execute must
        # honestly refuse. Previously this branch answered ok=True
        # "runtime thin" for ANY unmapped primary AND placed an idea as a
        # side effect, reachable via the public raw-seed path.
        # - >99 / None: reserved/not-active (no authority anywhere).
        # - 51-99: Core-II authority lives in chain_exec/core_ii_exec;
        #   the leaf has no Core-II executor. Production routes these via
        #   the front door before the leaf; direct leaf calls refuse.
        # - HANDLED set {27, 28, 34, 35, 37, 40, 44, 47}: production
        #   authority is core_i_ops (the front door intercepts these
        #   before the leaf on every production path). The leaf has NO
        #   arms for them: MPC-011 removed 37's dead Stream branch, and
        #   P1/TD-1 removed the seven divergent shadow arms (legacy
        #   timestamp checkpoints + silent save fallback for 27, a
        #   save-reload mislabeled as rollback for 28, success claims
        #   for the honestly-refused 44/47, and divergent 34/35/40
        #   copies). Direct leaf calls refuse rather than shadow the
        #   real authority.
        # 0-50 with explicit arms execute below (message-only "runtime thin"
        # for registered-but-armless dells: pre-existing, documented).
        if primary is None or primary > 50 or primary in (27, 28, 34, 35, 37, 40, 44, 47):
            name = {27: "Checkpoint", 28: "Rollback", 34: "Stamp",
                    35: "Discover", 37: "Nurture", 40: "TokenCount",
                    44: "Bridge", 47: "Embed"}.get(
                        primary, "reserved/not-active")
            return {
                "ok": False,
                "seed": s.as_mandel(),
                "english": s.as_english(),
                "primary": primary,
                "messages": [f"Dell {primary}[{name}] refused: no executor on this path."],
                "new_program": new_program,
                "error": f"Dell {primary} not executable via single-seed leaf",
            }
        d = get_dell(primary)
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
