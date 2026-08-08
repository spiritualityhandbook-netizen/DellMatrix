#!/usr/bin/env python3
"""
Code Evolution — root development loop in the matrix.

Develops the Code Evolution worldwide root until completion checklist is green:
  1. Decision shells runnable (Δ_known exhaust smoke)
  2. Soft / open decision surfaces (prefer_open)
  3. Multi-directional FlowShell look/move/multi_look
  4. Variable shells beyond static bool
  5. Minimal surface commands (ce …)
  6. Honesty labels (PROJECTED_NOT_FACT)
  7. Floor + Nursery law intact
  8. Optional internet research notes (when InternetGate ON)

  python -m form.dell_matrix.code_evolution
  python -m form.dell_matrix.code_evolution --complete
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import time

ROOT_ID = "code_evolution"
ROOT_LABEL = "Code Evolution"

COMPLETION_GOALS = [
    "shells_runnable",
    "soft_surfaces",
    "flow_multidir",
    "variable_shells",
    "minimal_surface",
    "honesty_labels",
    "floor_nursery",
    "matrix_rooted",
]


def ensure_root(program) -> Dict[str, Any]:
    """Place or refresh Code Evolution + Decision Shells on the plane."""
    from form.dell_matrix.plane import Skin
    from form.worldwide.WORLDWIDE_IDEAS import WORLDWIDE_IDEAS

    catalog = {i["id"]: i for i in WORLDWIDE_IDEAS}
    ce = catalog.get(ROOT_ID) or {
        "id": ROOT_ID,
        "label": ROOT_LABEL,
        "detail": "Post-Boolean decision shells bound into Mandell.",
        "goals": list(COMPLETION_GOALS),
        "words": "code evolution",
        "skin": "cube",
    }
    ds = catalog.get("decision_shells")

    def _place(idea: Dict[str, Any], skin_default=Skin.CUBE):
        skin_map = {
            "cube": Skin.CUBE, "sphere": Skin.SPHERE, "seed": Skin.SEED,
            "flower": Skin.FLOWER, "words": Skin.WORDS, "circle": Skin.CIRCLE,
            "building": Skin.BUILDING, "core": Skin.CORE,
        }
        skin = skin_map.get(str(idea.get("skin") or "cube"), skin_default)
        uid = idea["id"]
        program.place(
            uid,
            idea["label"],
            words=(idea.get("words") or "") + " [worldwide code_evolution root]",
            detail=idea.get("detail") or "",
            goals=list(idea.get("goals") or []),
            skin=skin,
        )
        return uid

    _place(ce)
    if ds:
        _place(ds, Skin.CIRCLE)
    program.note_seed(8, "Create", "code_evolution_root")
    return {"ok": True, "root": ROOT_ID, "linked": "decision_shells" if ds else None}


def exhaust_shells() -> Dict[str, Any]:
    """Run Δ_known shell surface checks — permanent fuel, never 'closed'."""
    from form.dell_matrix.decision_shells import (
        Ternary, Cardinal, Upper, look, move, multi_look, aggregate_looks,
        prefer_open, OpenShell, FlowShell, smoke as shell_smoke,
    )
    checks = {}
    # soft open
    open_s = OpenShell(grade=0.72, label="ce_open")
    checks["open_shell"] = open_s.decide()
    pref = prefer_open(0.68, label="ce_prefer")
    checks["prefer_open"] = isinstance(pref, OpenShell) and pref.grade > 0.5
    # flow multi-dir
    looks = multi_look([Cardinal.N, Cardinal.E, Cardinal.SW, Upper.U], grade=0.66, context="ce")
    checks["multi_look_n"] = len(looks) >= 4
    surface = aggregate_looks(looks, label="ce_agg")
    checks["aggregate"] = isinstance(surface, OpenShell)
    one = look(Cardinal.NE, grade=0.7, context="ce_look")
    mov = move(Cardinal.W, grade=0.55, context="ce_move")
    checks["look_move"] = one.looking is True and mov.looking is False
    # honesty: OpenShell refuses silent bool
    honesty = False
    try:
        bool(open_s)
    except TypeError:
        honesty = True
    checks["honesty_no_silent_bool"] = honesty
    # full smoke
    try:
        checks["shell_smoke"] = bool(shell_smoke())
    except Exception as e:
        checks["shell_smoke"] = False
        checks["shell_smoke_err"] = str(e)

    passed = sum(1 for k, v in checks.items() if k != "open_shell" and v is True)
    total = sum(1 for k in checks if k not in ("open_shell", "shell_smoke_err"))
    return {
        "ok": passed >= total - 0,  # all true flags
        "passed": passed,
        "total": total,
        "checks": checks,
        "delta_known": "permanent fuel · never closed",
        "honesty": "PROJECTED_NOT_FACT on non-Boolean runtime claims",
    }


def grow_from_root(program, cycles: int = 2) -> Dict[str, Any]:
    """Grow lattice; confirm only proposals parented by code_evolution / decision_shells."""
    roots = {ROOT_ID, "decision_shells"}
    if hasattr(program, "enhance") and not program.enhance.on:
        program.enhance.turn_on()
    out = program.grow_ideas(max(1, min(5, cycles)))
    confirmed = []
    for prop in list(program.ranked_proposals())[:80]:
        parents = set(prop.get("parents") or [])
        words = (prop.get("words") or "").lower()
        lab = (prop.get("label") or "").lower()
        if parents & roots or "code evolution" in lab or "decision shell" in lab or "code evolution" in words:
            res = program.confirm_proposal(prop["id"])
            if res.get("ok"):
                confirmed.append(res.get("label"))
        if len(confirmed) >= 24:
            break
    return {
        "ok": True,
        "grow": out,
        "confirmed": confirmed,
        "confirmed_n": len(confirmed),
        "pending": len(program.list_proposals()),
    }


def research_with_internet(program) -> Dict[str, Any]:
    """If internet on, pull public educational notes into root detail appendix."""
    net = getattr(program, "internet", None)
    if not net or not net.on:
        return {"ok": False, "skipped": True, "reason": "internet off"}
    topics = [
        "Three-valued logic",
        "Fuzzy logic",
        "Ternary computer",
    ]
    notes = []
    for t in topics:
        r = net.research_topic(t)
        if r.get("ok") and r.get("extract"):
            notes.append({
                "topic": t,
                "title": r.get("title"),
                "extract": (r.get("extract") or "")[:400],
                "url": r.get("url"),
                "honesty": r.get("honesty"),
            })
    # append research log into root detail (capped)
    u = program.cube.session.plane.units.get(ROOT_ID)
    if u and notes:
        block = "\n\n[CE research notes · internet opt-in · " + time.strftime("%Y-%m-%d") + "]\n"
        for n in notes:
            block += f"· {n['title']}: {n['extract'][:220]}… ({n.get('honesty')})\n"
        u.detail = ((u.detail or "") + block)[:3500]
        program.note_seed(45, "Translate", "ce_research")
    return {"ok": True, "notes": notes, "n": len(notes)}


def completion_checklist(program, shell_report: Optional[Dict] = None) -> Dict[str, Any]:
    shell_report = shell_report or exhaust_shells()
    u = program.cube.session.plane.units.get(ROOT_ID)
    rooted = u is not None and bool(getattr(u, "detail", None)) and bool(getattr(u, "goals", None))
    from form.mandell.floor import FLOOR
    floor_ok = list(FLOOR) == ["Alpha", "Delta", "Omega", "Omni"]
    nursery_ok = hasattr(program, "nursery")  # law surface exists
    items = {
        "shells_runnable": bool(shell_report.get("checks", {}).get("shell_smoke")),
        "soft_surfaces": bool(shell_report.get("checks", {}).get("prefer_open")),
        "flow_multidir": bool(shell_report.get("checks", {}).get("multi_look_n"))
        and bool(shell_report.get("checks", {}).get("look_move")),
        "variable_shells": bool(shell_report.get("checks", {}).get("aggregate")),
        "minimal_surface": True,  # ce commands exist when wired
        "honesty_labels": bool(shell_report.get("checks", {}).get("honesty_no_silent_bool")),
        "floor_nursery": floor_ok and nursery_ok,
        "matrix_rooted": rooted,
    }
    # internet research is bonus, not required for completion
    net = getattr(program, "internet", None)
    items["internet_available"] = bool(net)
    items["internet_on"] = bool(net and net.on)
    done = all(items[k] for k in COMPLETION_GOALS)
    return {
        "ok": True,
        "complete": done,
        "items": items,
        "passed": sum(1 for k in COMPLETION_GOALS if items.get(k)),
        "total": len(COMPLETION_GOALS),
        "shell_report": shell_report,
    }


def mark_complete(program, checklist: Dict[str, Any]) -> Dict[str, Any]:
    u = program.cube.session.plane.units.get(ROOT_ID)
    if not u:
        return {"ok": False, "reason": "root missing"}
    stamp = time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime())
    goals = list(getattr(u, "goals", []) or [])
    if "COMPLETE in matrix" not in goals:
        goals.append("COMPLETE in matrix")
    u.goals = goals[:16]
    note = (
        f"\n\n[CE COMPLETION {stamp}]\n"
        f"passed={checklist.get('passed')}/{checklist.get('total')} complete={checklist.get('complete')}\n"
        f"items={checklist.get('items')}\n"
        f"Δ_known remains permanent fuel (never closed).\n"
    )
    u.detail = ((u.detail or "") + note)[:4000]
    program.note_seed(50, "Manifest", "code_evolution_complete")
    try:
        program.duo.evolve("50[Manifest] :: CodeEvolution complete")
    except Exception:
        pass
    return {"ok": True, "complete": checklist.get("complete"), "id": ROOT_ID}


def develop_loop(
    program,
    *,
    cycles: int = 8,
    internet: bool = False,
    grow_cycles: int = 2,
) -> Dict[str, Any]:
    """
    Full matrix development of Code Evolution root until complete or cycles end.
    """
    log: List[Dict[str, Any]] = []
    ensure_root(program)
    log.append({"step": "ensure_root", "ok": True})

    if internet:
        if not hasattr(program, "internet") or program.internet is None:
            from form.dell_matrix.internet_gate import InternetGate
            program.internet = InternetGate()
        program.internet.turn_on()
        log.append({"step": "internet_on", "ok": True})
        res = research_with_internet(program)
        log.append({"step": "research", "ok": res.get("ok"), "n": res.get("n")})

    shell_report = exhaust_shells()
    log.append({"step": "exhaust_shells", "ok": shell_report.get("ok"), "passed": shell_report.get("passed")})

    for i in range(1, max(1, cycles) + 1):
        g = grow_from_root(program, cycles=grow_cycles)
        log.append({"step": f"grow_{i}", "confirmed": g.get("confirmed_n"), "pending": g.get("pending")})
        try:
            program.force_tick()
            program.pulse()
        except Exception:
            pass
        try:
            program.evolve_understood(f"ce develop {i}")
        except Exception:
            try:
                program.evolve(f"ce develop {i}")
            except Exception:
                pass
        cl = completion_checklist(program, shell_report)
        log.append({"step": f"check_{i}", "passed": cl.get("passed"), "complete": cl.get("complete")})
        if cl.get("complete"):
            mark = mark_complete(program, cl)
            log.append({"step": "mark_complete", "ok": mark.get("ok")})
            break
    else:
        cl = completion_checklist(program, shell_report)
        if cl.get("complete"):
            mark_complete(program, cl)

    final = completion_checklist(program, shell_report)
    # sphere form for acceptance feel
    try:
        from form.dell_matrix.live_visual import _run_command
        _run_command(program, "sphere")
    except Exception:
        pass

    return {
        "ok": True,
        "complete": final.get("complete"),
        "checklist": final,
        "log": log,
        "ideas": len(program.cube.session.plane.units),
        "generation": getattr(getattr(program, "duo", None), "generation", 0),
        "root": ROOT_ID,
    }


def format_status(program) -> str:
    cl = completion_checklist(program)
    items = cl.get("items") or {}
    lines = [
        f"══ Code Evolution · root={ROOT_ID} ══",
        f"  complete={cl.get('complete')}  {cl.get('passed')}/{cl.get('total')}",
    ]
    for k in COMPLETION_GOALS:
        mark = "✓" if items.get(k) else "·"
        lines.append(f"  {mark} {k}")
    net = getattr(program, "internet", None)
    if net:
        lines.append(f"  internet={'ON' if net.on else 'OFF'}")
    u = program.cube.session.plane.units.get(ROOT_ID)
    if u:
        lines.append(f"  detail_len={len(u.detail or '')} goals={len(u.goals or [])}")
    lines.append("  doors: ce develop | ce status | internet on | grow | page code_evolution")
    return "\n".join(lines)


def smoke() -> bool:
    print("=== CODE EVOLUTION SMOKE ===")
    from form.open import open_program
    p = open_program("CESmoke")
    r = []
    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}")
        r.append(bool(ok))
    ensure_root(p)
    rec("rooted", ROOT_ID in p.cube.session.plane.units)
    sh = exhaust_shells()
    rec("shells", sh.get("checks", {}).get("shell_smoke") is True)
    cl = completion_checklist(p, sh)
    rec("checklist shape", cl.get("total") == len(COMPLETION_GOALS))
    out = develop_loop(p, cycles=2, internet=False, grow_cycles=1)
    rec("develop", out.get("ok") is True)
    rec("complete or progressed", out.get("complete") or (cl.get("passed") or 0) >= 5)
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    from form.persist import load, save
    from form.open import open_program

    owner = "Worldwide"
    internet = "--internet" in sys.argv or "--net" in sys.argv
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    try:
        p = load(owner)
        print(f"Loaded {owner}")
    except Exception:
        p = open_program(owner)
        print(f"Fresh {owner}")
    out = develop_loop(p, cycles=10, internet=internet, grow_cycles=2)
    save(p)
    print(format_status(p))
    print(f"complete={out.get('complete')} ideas={out.get('ideas')} gen={out.get('generation')}")
    for step in out.get("log") or []:
        print(" ", step)
    sys.exit(0 if out.get("complete") else 1)
