#!/usr/bin/env python3
"""
What the program needs — and how to satisfy it.

Implements first-class surfaces the Origin path was missing:
  · strong create (detail + goals parsed, not stuffed into the label)
  · edit idea detail / goals after place
  · history (what the program just did)
  · undo (safe reverse of last place)
  · what next / nbd (live next-best directives from state)
  · ready (acceptance + health checklist)

Law: Floor locked · Nursery confirm · offline · no junk free-create.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import re
import time


# ─── Strong create ─────────────────────────────────────────────────────────

def parse_and_place(program, raw: str) -> Dict[str, Any]:
    """Parse create line with detail:/goals: and place a strong idea."""
    from form.idea_create import parse_create_line, unique_unit_id, format_report
    from form.dell_matrix.plane import Skin

    parsed = parse_create_line(raw)
    label = parsed["label"]
    # Canonical slug + collision dedup (idea_create.unique_unit_id).
    uid = unique_unit_id(program.cube.session.plane.units, label)

    u = program.place(
        uid,
        label,
        words=parsed.get("words") or label,
        detail=parsed.get("detail") or "",
        goals=list(parsed.get("goals") or []),
        skin=Skin.CUBE,
    )
    # stack for undo
    push_action(program, {
        "kind": "place",
        "id": uid,
        "label": label,
        "ts": time.time(),
    })
    return {
        "ok": True,
        "id": uid,
        "label": label,
        "detail": parsed.get("detail") or "",
        "goals": list(parsed.get("goals") or []),
        "complete": parsed.get("complete"),
        "strength": parsed.get("strength"),
        "grade": parsed.get("grade"),
        "missing": parsed.get("missing") or [],
        "hint": parsed.get("hint") or "",
        "unit": {
            "id": uid,
            "label": label,
            "skin": u.skin.value if hasattr(u.skin, "value") else str(u.skin),
            "x": u.x,
            "y": u.y,
        },
        "report": format_report(parsed),
    }


def format_create_end(res: Dict[str, Any]) -> str:
    lines = [
        f'Created idea: "{res.get("label")}" id={res.get("id")}',
        f"  strength={res.get('strength')} ({res.get('grade')}) complete={res.get('complete')}",
        f"  detail: {(res.get('detail') or '—')[:120]}",
        f"  goals: {', '.join(res.get('goals') or []) or '—'}",
    ]
    if res.get("missing"):
        lines.append(f"  missing for Strong: {', '.join(res['missing'])}")
        lines.append("  tip: add with  set detail <id|label> …  ·  set goals <id|label> a; b; c")
    lines.append("  doors: page | grow ideas 1 | proposals | look")
    return "\n".join(lines)


# ─── Edit detail / goals ───────────────────────────────────────────────────

def _resolve_unit(program, ref: str):
    """Resolve an edit target. Canonical tiers first (P1/TD-3): exact
    ID, exact-case label, case-insensitive label — a tier matches
    only when it names exactly ONE unit, so an edit can never land
    on the wrong unit when labels collide. The partial-substring
    tier remains as this surface's deliberate fuzzy fallback, and it
    too must be unique to resolve."""
    plane = program.cube.session.plane
    ref = (ref or "").strip()
    if not ref:
        return None, None
    if ref in plane.units:
        return ref, plane.units[ref]
    exact = [(uid, u) for uid, u in plane.units.items()
             if (u.label or "") == ref]
    if len(exact) == 1:
        return exact[0]
    if len(exact) > 1:
        return None, None
    low = ref.lower()
    ci = [(uid, u) for uid, u in plane.units.items()
          if (u.label or "").lower() == low]
    if len(ci) == 1:
        return ci[0]
    if len(ci) > 1:
        return None, None
    # partial (unique only)
    rl = ref.lower()
    part = [(uid, u) for uid, u in plane.units.items()
            if rl in (u.label or "").lower() or rl in uid.lower()]
    if len(part) == 1:
        return part[0]
    return None, None


def set_detail(program, ref: str, detail: str) -> Dict[str, Any]:
    uid, u = _resolve_unit(program, ref)
    if not u:
        return {"ok": False, "reason": f"idea not found: {ref}"}
    old = getattr(u, "detail", "") or ""
    # J-04/J-17 (GP-E27): the edited detail is stored WHOLE. The
    # former [:2000] cut silently truncated admitted edits at this
    # door (a >2,000-char edit lost its tail with no provenance or
    # refusal) — the SYS-C29 family defect, sibling of the create
    # door's cut removed in idea_create.parse_create_line.
    u.detail = (detail or "").strip()
    if not (u.words or "").strip() and u.detail:
        u.words = u.detail[:120]
    push_action(program, {"kind": "edit_detail", "id": uid, "old": old, "new": u.detail, "ts": time.time()})
    program.note_seed(4, "Transform", f"detail_{uid}")
    return {"ok": True, "id": uid, "label": u.label, "detail": u.detail}


def set_goals(program, ref: str, goals_raw: str) -> Dict[str, Any]:
    uid, u = _resolve_unit(program, ref)
    if not u:
        return {"ok": False, "reason": f"idea not found: {ref}"}
    old = list(getattr(u, "goals", []) or [])
    parts = [g.strip() for g in re.split(r"[;,]|\band\b", goals_raw or "") if g.strip()]
    u.goals = parts[:12]
    push_action(program, {"kind": "edit_goals", "id": uid, "old": old, "new": list(u.goals), "ts": time.time()})
    program.note_seed(4, "Transform", f"goals_{uid}")
    return {"ok": True, "id": uid, "label": u.label, "goals": list(u.goals)}


def idea_info(program, ref: str) -> Dict[str, Any]:
    uid, u = _resolve_unit(program, ref)
    if not u:
        return {"ok": False, "reason": f"idea not found: {ref}"}
    from form.idea_create import strength_score, grade_for
    detail = getattr(u, "detail", "") or ""
    goals = list(getattr(u, "goals", []) or [])
    sc = strength_score(detail, goals)
    return {
        "ok": True,
        "id": uid,
        "label": u.label,
        "words": u.words or "",
        "detail": detail,
        "goals": goals,
        "skin": u.skin.value if hasattr(u.skin, "value") else str(u.skin),
        "x": u.x, "y": u.y,
        "strength": sc,
        "grade": grade_for(sc),
        "complete": bool(detail and goals),
    }


def format_idea_end(info: Dict[str, Any]) -> str:
    if not info.get("ok"):
        return info.get("reason") or "not found"
    lines = [
        f"══ Idea · {info.get('label')} ══",
        f"  id={info.get('id')} skin={info.get('skin')} pos=({info.get('x')},{info.get('y')})",
        f"  strength={info.get('strength')} ({info.get('grade')}) complete={info.get('complete')}",
        f"  words: {info.get('words') or '—'}",
        f"  detail: {info.get('detail') or '—'}",
        f"  goals: {', '.join(info.get('goals') or []) or '—'}",
        "  doors: set detail <id> … · set goals <id> a; b · page · zoom " + str(info.get("id")),
    ]
    return "\n".join(lines)


# ─── Action stack / undo ───────────────────────────────────────────────────

# Q-LC.1 (DD-54 bounded slice; Director EXE 6965138959 on PR #434):
# the session ACTION stack's depth is Ace's ruled 30 by default and
# adjustable per owner (Program.undo_depth) under a named safety
# ceiling. This governs ONLY the session action history — the Core II
# snapshot stack (SNAPSHOTS_CAP) is a separate authority, untouched.
UNDO_DEPTH = 30
UNDO_DEPTH_MAX = 200


def _stack(program) -> List[Dict[str, Any]]:
    if not hasattr(program, "action_stack") or program.action_stack is None:
        program.action_stack = []
    return program.action_stack


def _redo_stack(program) -> List[Dict[str, Any]]:
    if not hasattr(program, "redo_stack") or program.redo_stack is None:
        program.redo_stack = []
    return program.redo_stack


def effective_undo_depth(program) -> int:
    """The owner's effective action-history depth. A stored value
    outside [1, UNDO_DEPTH_MAX] is not honored silently: the ruled
    default applies (the set door refuses out-of-range values, so an
    out-of-range stored value can only be legacy/corrupt state)."""
    try:
        d = int(getattr(program, "undo_depth", UNDO_DEPTH))
    except (TypeError, ValueError):
        return UNDO_DEPTH
    if d < 1 or d > UNDO_DEPTH_MAX:
        return UNDO_DEPTH
    return d


def _count_drops(program, n: int) -> None:
    if n > 0:
        try:
            program.action_dropped_total = int(getattr(program, "action_dropped_total", 0) or 0) + n
        except Exception:
            pass


def _trim_to_depth(program, stack: List[Dict[str, Any]]) -> int:
    """Trim oldest-first to the effective depth; count every drop so
    no loss at the bound is ever silent. Returns the drop count."""
    depth = effective_undo_depth(program)
    dropped = 0
    while len(stack) > depth:
        stack.pop(0)
        dropped += 1
    _count_drops(program, dropped)
    return dropped


def push_action(program, entry: Dict[str, Any]) -> None:
    st = _stack(program)
    st.append(entry)
    # DD-54 §3 (linear history): any new action discards the redo tail.
    redo = _redo_stack(program)
    if redo:
        redo.clear()
    _trim_to_depth(program, st)


def _push_back_from_redo(program, entry: Dict[str, Any]) -> None:
    """Re-stack an entry redo just re-applied, so it is undoable again
    (redo advances the SAME action stream). Unlike push_action this
    must not clear the redo tail it is consuming."""
    st = _stack(program)
    st.append(entry)
    _trim_to_depth(program, st)


def _feed_redo(program, entry: Dict[str, Any]) -> None:
    redo = _redo_stack(program)
    redo.append(entry)
    # The tail can only hold what undo popped; bound it by the same
    # depth, dropping from the far (oldest-pushed) end first.
    _trim_to_depth(program, redo)


def set_undo_depth(program, n) -> Dict[str, Any]:
    """Ace's adjustability door for the session action history.

    Refuses honestly (changing nothing) below 1 or above the named
    ceiling. A shrink trims BOTH stacks oldest-first and reports how
    many inverses were dropped; a grow never resurrects drops."""
    try:
        value = int(n)
    except (TypeError, ValueError):
        return {"ok": False, "reason": f"undo depth must be an integer, got {n!r}"}
    if str(n).strip() not in (str(value), f"+{value}") and not isinstance(n, int):
        return {"ok": False, "reason": f"undo depth must be an integer, got {n!r}"}
    if value < 1:
        return {"ok": False, "reason": f"undo depth {value} refused: minimum is 1 (a 0-depth undo is a contradiction)"}
    if value > UNDO_DEPTH_MAX:
        return {"ok": False, "reason": f"undo depth {value} refused: ceiling is UNDO_DEPTH_MAX={UNDO_DEPTH_MAX}"}
    program.undo_depth = value
    dropped = _trim_to_depth(program, _stack(program))
    dropped += _trim_to_depth(program, _redo_stack(program))
    return {
        "ok": True,
        "depth": value,
        "dropped": dropped,
        "msg": f"Undo depth set to {value}" + (f" · dropped {dropped} oldest inverse(s)" if dropped else ""),
    }


def _revision_owned(program, uid: str) -> bool:
    """True when DCC-XVI revision/supersession authority owns this unit's history.

    A unit that is superseded, has a successor, or sits in a multi-node
    revision chain may only change through supersession — never through undo.
    A lone active rev-1 unit (the normal freshly-placed case) is not owned.
    """
    try:
        from form.mandell.supersession import inspect_revision
        rev = inspect_revision(program, uid)
    except Exception:
        return False
    if rev.get("lifecycle_state") == "superseded":
        return True
    if rev.get("superseded_by_id"):
        return True
    chain = rev.get("chain") or []
    return len(chain) > 1


def _clear_lattice_refs(program, uid: str) -> None:
    """View hygiene: drop lattice cells still pointing at a removed unit.

    P4-DIR-01: removes uid from multi-content `members`; updates the
    legacy `content` primary if it was the removed uid.
    """
    try:
        for _key, cell in list(program.lattice.cells.items()):
            if uid in cell.members:
                cell.members = [m for m in cell.members if m != uid]
                if cell.content == uid:
                    cell.content = cell.members[0] if cell.members else None
                    cell.label = ""
            elif cell.content == uid:
                cell.content = None
                cell.label = ""
    except Exception:
        pass


def undo_last(program) -> Dict[str, Any]:
    # PAC-I authority law: undo is a SESSION/UI reversal convenience
    # (callers: REPL, live_visual). It is explicitly NONCANONICAL as a
    # history authority: every canonical effect delegates to the designated
    # authority — plane.remove for removal; revision-owned units are refused,
    # never bypassed. Evidence of each undo lands in program.history via
    # note_seed (persisted).
    st = _stack(program)
    if not st:
        return {
            "ok": False,
            "reason": "nothing to undo",
            "hint": "Undo reverses last place or edit. Try create first.",
        }
    act = st.pop()
    kind = act.get("kind")
    if kind == "place":
        uid = act.get("id")
        plane = program.cube.session.plane
        if uid and uid in plane.units:
            if _revision_owned(program, uid):
                # A refused undo must not consume the entry: restore it
                # to the top of the stack it was popped from, so the
                # refusal loses no history (redo-side sibling law).
                st.append(act)
                return {
                    "ok": False,
                    "reason": "revision_authority",
                    "undid": None,
                    "hint": "Unit participates in a revision chain; undo cannot bypass supersession.",
                }
            # Q-LC.1 §3.2: capture the unit's FULL restorable record
            # BEFORE removal — after plane.remove nothing remains for
            # redo to re-place. Only a successful undo feeds the tail.
            u = plane.units[uid]
            record = {
                "id": uid,
                "label": u.label,
                "words": u.words or "",
                "detail": getattr(u, "detail", "") or "",
                "goals": list(getattr(u, "goals", []) or []),
                "skin": u.skin.value if hasattr(u.skin, "value") else str(u.skin),
                "x": u.x,
                "y": u.y,
                "parents": list(getattr(u, "parents", []) or []),
                "origin": getattr(u, "origin", "placed") or "placed",
                "sandboxed": bool(getattr(u, "sandboxed", False)),
                "sandbox_id": getattr(u, "sandbox_id", None),
                # The canonical Idea pointer is part of the restorable
                # record: dropping it here re-places the unit unbound
                # (idea_id=None) and binding census then persists an
                # unbound unit whose Idea is unreferenced.
                "idea_id": getattr(u, "idea_id", None),
            }
            # Delegate to the canonical one-way removal authority.
            removed = plane.remove(uid)
            _clear_lattice_refs(program, uid)
            if not removed:
                return {"ok": False, "reason": f"idea {uid} already gone", "undid": None}
            program.note_seed(24, "Unlock", f"undo_place_{uid}")
            _feed_redo(program, {**act, "record": record})
            return {
                "ok": True,
                "undid": "place",
                "id": uid,
                "label": act.get("label"),
                "via": "plane.remove",
                "msg": f'Undid place · removed "{act.get("label")}" ({uid})',
            }
        return {"ok": False, "reason": f"idea {uid} already gone", "undid": None}
    if kind == "edit_detail":
        uid = act.get("id")
        u = program.cube.session.plane.units.get(uid)
        if u is not None:
            u.detail = act.get("old") or ""
            program.note_seed(24, "Unlock", f"undo_edit_detail_{uid}")
            _feed_redo(program, act)
            return {"ok": True, "undid": "edit_detail", "id": uid, "msg": f"Restored detail on {uid}"}
        return {"ok": False, "reason": "unit missing"}
    if kind == "edit_goals":
        uid = act.get("id")
        u = program.cube.session.plane.units.get(uid)
        if u is not None:
            u.goals = list(act.get("old") or [])
            program.note_seed(24, "Unlock", f"undo_edit_goals_{uid}")
            _feed_redo(program, act)
            return {"ok": True, "undid": "edit_goals", "id": uid, "msg": f"Restored goals on {uid}"}
        return {"ok": False, "reason": "unit missing"}
    return {"ok": False, "reason": f"cannot undo kind={kind}"}


def redo_last(program) -> Dict[str, Any]:
    """Re-apply the most recently undone action (DD-54 §2).

    Redo walks the SAME action stream undo consumed: a successful redo
    pushes the entry back onto the action stack, so it is undoable
    again. Re-application goes through canonical doors only —
    Program.place for places (never a backdoor insert), direct field
    restoration for edits (the same inverse shape undo uses). Refusals
    mutate nothing: a re-taken id, a revision-owned target, a missing
    unit, or a failed sandbox-membership restore (the re-place is
    rolled back) all refuse visibly. Session-only, like undo: redo
    walks state, never records (DD-54 §6)."""
    redo = _redo_stack(program)
    if not redo:
        return {
            "ok": False,
            "reason": "nothing to redo",
            "hint": "Redo re-applies an undone place or edit. Undo first.",
        }
    # Peek, do not pop: the tail entry is consumed ONLY by a successful
    # re-application. A refusal (re-taken id, revision authority,
    # missing unit, failed place) leaves the entry in place, so the
    # owner can remove the conflict and retry — popping first would
    # permanently lose recoverable history on a refused operation.
    act = redo[-1]
    kind = act.get("kind")
    if kind == "place":
        uid = act.get("id")
        record = act.get("record") or {}
        plane = program.cube.session.plane
        if not uid or not record:
            return {"ok": False, "reason": "redo place record missing", "redid": None}
        if uid in plane.units:
            return {"ok": False, "reason": f"idea {uid} already exists", "redid": None}
        if _revision_owned(program, uid):
            return {
                "ok": False,
                "reason": "revision_authority",
                "redid": None,
                "hint": "Unit participates in a revision chain; redo cannot bypass supersession.",
            }
        from form.dell_matrix.plane import Skin
        try:
            skin = Skin(str(record.get("skin") or "cube"))
        except ValueError:
            skin = Skin.CUBE
        try:
            u = program.place(
                uid,
                record.get("label") or act.get("label") or uid,
                words=record.get("words") or "",
                detail=record.get("detail") or "",
                goals=list(record.get("goals") or []),
                skin=skin,
                x=float(record.get("x") or 0.0),
                y=float(record.get("y") or 0.0),
                parents=list(record.get("parents") or []),
                origin=str(record.get("origin") or "placed"),
                idea_id=record.get("idea_id"),
            )
        except Exception as e:
            return {"ok": False, "reason": f"redo place refused: {e}", "redid": None}
        # Restore EXACTLY the captured sandbox membership. Program.place
        # may already have auto-boxed the unit (global sandbox gate on):
        # that membership is not in the record, so remove it through
        # the canonical unbox door BEFORE boxing into the saved box —
        # otherwise the unit sits in both member lists while sandbox_id
        # names only one, and a later undo leaves a dangling entry.
        saved_box = str(record["sandbox_id"]) if (
            record.get("sandboxed") and record.get("sandbox_id")) else None
        try:
            if getattr(u, "sandboxed", False) and getattr(u, "sandbox_id", None) != saved_box:
                plane.unbox(uid)
            if saved_box:
                plane.box([uid], saved_box)
                u.sandboxed = True
                u.sandbox_id = saved_box
        except Exception as e:
            # Refusal honesty (Director §42 DELTA 6968119456): a failed
            # membership restore is a REFUSED redo, never a swallowed
            # success — reporting ok=True here would claim the C3
            # exact-membership guarantee while the unit sits unboxed or
            # in the wrong box. Roll the re-place back so the refusal
            # mutates nothing and the tail entry stays for a retry (the
            # canonical removal door undo uses). The rollback cannot
            # depend on the door that just failed — plane.remove routes
            # through unbox — so a blocked door falls back to stripping
            # the membership directly rather than leaving a
            # half-restored unit behind.
            try:
                plane.remove(uid)
            except Exception:
                for sb in plane.sandboxes.values():
                    if uid in sb.member_ids:
                        sb.member_ids = [m for m in sb.member_ids if m != uid]
                plane.units.pop(uid, None)
            _clear_lattice_refs(program, uid)
            return {
                "ok": False,
                "reason": f"redo sandbox restore refused: {e}",
                "redid": None,
                "hint": "Sandbox membership could not be restored; the redo entry was kept — fix the cause and retry.",
            }
        if redo and redo[-1] is act:
            redo.pop()
        program.note_seed(24, "Unlock", f"redo_place_{uid}")
        _push_back_from_redo(program, {k: v for k, v in act.items() if k != "record"})
        return {
            "ok": True,
            "redid": "place",
            "id": uid,
            "label": record.get("label") or act.get("label"),
            "via": "program.place",
            "msg": f'Redid place · restored "{record.get("label") or act.get("label")}" ({uid})',
        }
    if kind == "edit_detail":
        uid = act.get("id")
        u = program.cube.session.plane.units.get(uid)
        if u is not None:
            if _revision_owned(program, uid):
                return {"ok": False, "reason": "revision_authority", "redid": None}
            u.detail = act.get("new") or ""
            if redo and redo[-1] is act:
                redo.pop()
            program.note_seed(24, "Unlock", f"redo_edit_detail_{uid}")
            _push_back_from_redo(program, act)
            return {"ok": True, "redid": "edit_detail", "id": uid, "msg": f"Re-applied detail on {uid}"}
        return {"ok": False, "reason": "unit missing"}
    if kind == "edit_goals":
        uid = act.get("id")
        u = program.cube.session.plane.units.get(uid)
        if u is not None:
            if _revision_owned(program, uid):
                return {"ok": False, "reason": "revision_authority", "redid": None}
            u.goals = list(act.get("new") or [])
            if redo and redo[-1] is act:
                redo.pop()
            program.note_seed(24, "Unlock", f"redo_edit_goals_{uid}")
            _push_back_from_redo(program, act)
            return {"ok": True, "redid": "edit_goals", "id": uid, "msg": f"Re-applied goals on {uid}"}
        return {"ok": False, "reason": "unit missing"}
    return {"ok": False, "reason": f"cannot redo kind={kind}"}


# ─── History ───────────────────────────────────────────────────────────────

def history_report(program, n: int = 16) -> List[str]:
    hist = list(getattr(program, "history", []) or [])[-max(1, n):]
    stack = list(_stack(program))[-8:]
    lines = [f"History · {len(hist)} notes (last {len(hist)} shown):"]
    if not hist:
        lines.append("  (empty — act, then history fills)")
    else:
        for i, h in enumerate(hist, 1):
            lines.append(f"  {i:2}. {h}")
    if stack:
        lines.append("Undo stack (latest last):")
        for s in stack:
            lines.append(f"  · {s.get('kind')} {s.get('id') or s.get('label') or ''}")
    depth = effective_undo_depth(program)
    dropped = int(getattr(program, "action_dropped_total", 0) or 0)
    redo_n = len(_redo_stack(program))
    lines.append(
        f"Undo depth: {len(_stack(program))}/{depth} (session action history; "
        f"dropped {dropped} at the bound) · redo tail: {redo_n} · "
        f"snapshot stack is separate")
    lines.append("  doors: undo | redo | undo depth [n] | replay 3 | macro 5 | self")
    return lines


# ─── Next best directive (live) ────────────────────────────────────────────

def next_directives(program) -> List[Dict[str, Any]]:
    """
    Live NBD from actual Program state — what to do next to strengthen Origin path.
    """
    tips: List[Dict[str, Any]] = []
    ideas = len(program.cube.session.plane.units)
    nursery = 0
    try:
        nursery = int(program.nursery.summary().get("pending", 0))
    except Exception:
        pass
    audit = program.audit() if hasattr(program, "audit") else {}
    avg = float(audit.get("average") or 0)
    form = program.lattice.perception.form.value if hasattr(program, "lattice") else "?"
    zoom = program.cube.session.plane.zoom_target
    enhance_on = bool(getattr(getattr(program, "enhance", None), "on", False))
    auto_confirm = bool(getattr(program, "auto_confirm_grow", False))
    sk = getattr(program, "self_knowledge", None)
    mastery = 0.0
    if sk and hasattr(sk, "to_dict"):
        mastery = float(sk.to_dict().get("avg_mastery") or 0)

    # count strong ideas
    strong = 0
    weak_ids = []
    for uid, u in program.cube.session.plane.units.items():
        d = getattr(u, "detail", "") or ""
        g = getattr(u, "goals", []) or []
        if d and g:
            strong += 1
        elif uid != "welcome":
            weak_ids.append(uid)

    if ideas <= 1:
        tips.append({
            "priority": 100,
            "cmd": "create an idea called My Focus detail: what this matrix is for goals: ship one loop; stay offline honest",
            "why": "Need a real idea with detail + goals (Strong idea law)",
        })
    elif weak_ids and strong < 1:
        wid = weak_ids[0]
        tips.append({
            "priority": 95,
            "cmd": f"set detail {wid} what this idea means in one sentence",
            "why": "Ideas exist but lack detail — strengthen before grow",
        })
        tips.append({
            "priority": 94,
            "cmd": f"set goals {wid} clarify purpose; confirm when ready; evolve honestly",
            "why": "Goals steer ringed growth affinity",
        })
    if nursery == 0 and ideas >= 1:
        grow_cmd = "grow ideas 2"
        grow_why = "Nursery empty — grow proposes quarantined candidates"
        if auto_confirm:
            grow_why += " · auto confirm all ON (will accept onto lattice)"
        tips.append({
            "priority": 80,
            "cmd": grow_cmd,
            "why": grow_why,
        })
    if nursery > 0:
        if auto_confirm:
            tips.append({
                "priority": 90,
                "cmd": "grow ideas 1",
                "why": f"{nursery} pending · auto confirm grow ON — grow will also confirm all",
            })
        tips.append({
            "priority": 85,
            "cmd": "proposals",
            "why": f"{nursery} pending — review then confirm all or confirm <id>",
        })
        tips.append({
            "priority": 84,
            "cmd": "confirm all",
            "why": "Accept nursery proposals onto the live lattice (Nursery law)",
        })
    if not auto_confirm and ideas >= 1:
        tips.append({
            "priority": 35,
            "cmd": "auto confirm all grow mode",
            "why": "Optional: grow then auto-confirm all pending (fast lattice fill)",
        })
    if form == "cube" and ideas >= 2:
        tips.append({
            "priority": 60,
            "cmd": "sphere",
            "why": "Acceptance path: perceive as sphere after confirm",
        })
    if not enhance_on:
        tips.append({
            "priority": 50,
            "cmd": "enhance on",
            "why": "Enhance gate off — pulse/scores stay cold",
        })
    if avg < 0.70:
        tips.append({
            "priority": 70,
            "cmd": "self evolve",
            "why": f"Pillars avg={avg:.2f} GROWING — evolve with understanding",
        })
    if mastery < 0.5:
        tips.append({
            "priority": 55,
            "cmd": "self",
            "why": "Self-knowledge cold — run self then close gaps",
        })
    if not zoom and ideas >= 1:
        tips.append({
            "priority": 40,
            "cmd": "page",
            "why": "Open nearest idea end-page (full doors)",
        })
    tips.append({
        "priority": 20,
        "cmd": "save",
        "why": "Persist v7 session when ready",
    })
    tips.append({
        "priority": 15,
        "cmd": "visual",
        "why": "Offline snapshot panel for the acceptance close",
    })
    tips.sort(key=lambda t: -t["priority"])
    return tips[:8]


def format_next(program) -> str:
    tips = next_directives(program)
    lines = ["══ What next (live NBD) ══"]
    if not tips:
        lines.append("  You're clear — try evolve or inspire.")
    for i, t in enumerate(tips, 1):
        lines.append(f"  {i}. {t['cmd']}")
        lines.append(f"     why: {t['why']}")
    lines.append("  doors: ready | self | grow ideas 2 | proposals | help")
    return "\n".join(lines)


# ─── Ready checklist ───────────────────────────────────────────────────────

def ready_checklist(program) -> Dict[str, Any]:
    """Acceptance + health readiness."""
    ideas = len(program.cube.session.plane.units)
    nursery = 0
    try:
        nursery = int(program.nursery.summary().get("pending", 0))
    except Exception:
        pass
    audit = program.audit() if hasattr(program, "audit") else {}
    form = program.lattice.perception.form.value if hasattr(program, "lattice") else "?"
    strong = 0
    for u in program.cube.session.plane.units.values():
        if (getattr(u, "detail", None) or "") and (getattr(u, "goals", None) or []):
            strong += 1
    checks = [
        {"id": "ideas", "ok": ideas >= 1, "label": f"Has ideas ({ideas})"},
        {"id": "strong", "ok": strong >= 1, "label": f"Strong idea with detail+goals ({strong})"},
        {"id": "grown", "ok": nursery > 0 or ideas >= 2, "label": f"Grown or multi-idea (nursery={nursery})"},
        {"id": "form", "ok": form in ("sphere", "circle", "flower", "core"), "label": f"Non-cube form ({form}) — or run sphere"},
        {"id": "pillars", "ok": float(audit.get("average") or 0) >= 0.70, "label": f"Pillars healthy ({audit.get('label')} {audit.get('average')})"},
        {"id": "floor", "ok": True, "label": "Floor locked"},
    ]
    # soft: save exists as capability
    checks.append({"id": "save_path", "ok": True, "label": "Save/load available (persist v7)"})
    passed = sum(1 for c in checks if c["ok"])
    # Full ready = all checks green (acceptance close)
    ready = all(c["ok"] for c in checks)
    return {
        "ok": True,
        "ready": ready,
        "passed": passed,
        "total": len(checks),
        "checks": checks,
        "next": next_directives(program)[:3],
    }


def format_ready(program) -> str:
    r = ready_checklist(program)
    lines = [
        f"══ Ready · {'YES' if r['ready'] else 'NOT YET'} · {r['passed']}/{r['total']} ══",
    ]
    for c in r["checks"]:
        mark = "✓" if c["ok"] else "·"
        lines.append(f"  {mark} {c['label']}")
    if not r["ready"]:
        lines.append("Next:")
        for t in r.get("next") or []:
            lines.append(f"  → {t['cmd']}")
            lines.append(f"    {t['why']}")
    else:
        lines.append("  Path clear: save · visual · or keep evolving (self evolve)")
    lines.append("  doors: what next | self | tutorial | help")
    return "\n".join(lines)


def smoke() -> bool:
    print("=== NEEDS MODULE SMOKE ===")
    from form.open import open_program
    p = open_program("NeedsSmoke")
    r = []
    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}")
        r.append(bool(ok))

    res = parse_and_place(
        p,
        "create an idea called Code Evolution detail: post-Boolean shells goals: exhaust; honesty",
    )
    rec("strong create", res.get("ok") and res.get("complete") and res.get("label") == "Code Evolution")
    u = p.cube.session.plane.units.get(res["id"])
    rec("detail stored", bool(u and (u.detail or "").startswith("post-Boolean")))
    rec("goals stored", bool(u and len(u.goals) >= 2))

    info = idea_info(p, "Code Evolution")
    rec("idea info", info.get("ok") and info.get("complete"))

    sd = set_detail(p, "Code Evolution", "updated detail about shells")
    rec("set detail", sd.get("ok") and "updated" in (sd.get("detail") or ""))

    und = undo_last(p)
    rec("undo edit", und.get("ok"))

    # undo place
    parse_and_place(p, "create an idea called TempUndo detail: x goals: y")
    n_before = len(p.cube.session.plane.units)
    und2 = undo_last(p)
    n_after = len(p.cube.session.plane.units)
    rec("undo place", und2.get("ok") and n_after == n_before - 1)

    nxt = next_directives(p)
    rec("nbd", len(nxt) >= 1)
    ready = ready_checklist(p)
    rec("ready shape", "checks" in ready and ready.get("total", 0) >= 5)
    hist = history_report(p)
    rec("history", len(hist) >= 2)

    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
