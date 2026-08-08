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
    from form.idea_create import parse_create_line, slug_id, format_report
    from form.dell_matrix.plane import Skin

    parsed = parse_create_line(raw)
    label = parsed["label"]
    uid = slug_id(label)
    # avoid collision
    base = uid
    n = 1
    while uid in program.cube.session.plane.units:
        uid = f"{base}_{n}"
        n += 1
        if n > 50:
            break

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
        "unit": u,
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
    plane = program.cube.session.plane
    ref = (ref or "").strip()
    if not ref:
        return None, None
    if ref in plane.units:
        return ref, plane.units[ref]
    for uid, u in plane.units.items():
        if (u.label or "").lower() == ref.lower():
            return uid, u
    # partial
    rl = ref.lower()
    for uid, u in plane.units.items():
        if rl in (u.label or "").lower() or rl in uid.lower():
            return uid, u
    return None, None


def set_detail(program, ref: str, detail: str) -> Dict[str, Any]:
    uid, u = _resolve_unit(program, ref)
    if not u:
        return {"ok": False, "reason": f"idea not found: {ref}"}
    old = getattr(u, "detail", "") or ""
    u.detail = (detail or "").strip()[:2000]
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

def _stack(program) -> List[Dict[str, Any]]:
    if not hasattr(program, "action_stack") or program.action_stack is None:
        program.action_stack = []
    return program.action_stack


def push_action(program, entry: Dict[str, Any]) -> None:
    st = _stack(program)
    st.append(entry)
    while len(st) > 32:
        st.pop(0)


def undo_last(program) -> Dict[str, Any]:
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
            # remove unit
            del plane.units[uid]
            try:
                # drop lattice content if any
                for key, cell in list(program.lattice.cells.items()):
                    if cell.content == uid:
                        cell.content = None
                        cell.label = ""
            except Exception:
                pass
            program.note_seed(24, "Unlock", f"undo_place_{uid}")
            return {
                "ok": True,
                "undid": "place",
                "id": uid,
                "label": act.get("label"),
                "msg": f'Undid place · removed "{act.get("label")}" ({uid})',
            }
        return {"ok": False, "reason": f"idea {uid} already gone", "undid": None}
    if kind == "edit_detail":
        uid = act.get("id")
        u = program.cube.session.plane.units.get(uid)
        if u is not None:
            u.detail = act.get("old") or ""
            return {"ok": True, "undid": "edit_detail", "id": uid, "msg": f"Restored detail on {uid}"}
        return {"ok": False, "reason": "unit missing"}
    if kind == "edit_goals":
        uid = act.get("id")
        u = program.cube.session.plane.units.get(uid)
        if u is not None:
            u.goals = list(act.get("old") or [])
            return {"ok": True, "undid": "edit_goals", "id": uid, "msg": f"Restored goals on {uid}"}
        return {"ok": False, "reason": "unit missing"}
    return {"ok": False, "reason": f"cannot undo kind={kind}"}


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
    lines.append("  doors: undo | replay 3 | macro 5 | self")
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
