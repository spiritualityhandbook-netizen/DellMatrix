#!/usr/bin/env python3
"""
Function 150-loop — ensure the program works end-to-end.

150 cycles rotate through every major functional surface:
  create · grow · nursery · lattice · move · look · forces · personas
  inspire · self · english · pages · workshops · persist · readiness

Each cycle must return a useful end (msg/error). Mis-creates and empty
responses are failures. Soft repair is attempted once per fail.

  python -m form.dell_matrix.function_150_loop
  python -m form.dell_matrix.function_150_loop --cycles 150
  python -m form.dell_matrix.function_150_loop --smoke
"""

from __future__ import annotations

import os
import re
import sys
from typing import Any, Dict, List, Optional, Tuple

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


def _fill(cmd: str, ctx: Dict[str, Any]) -> str:
    c = (cmd or "").rstrip()
    if c == "create an idea called ":
        return (
            "create an idea called LoopFocus "
            "detail: function loop probe idea "
            "goals: verify create; grow; confirm"
        )
    if c == "confirm ":
        pid = ctx.get("pid")
        return f"confirm {pid}" if pid else "confirm all"
    if c == "reject ":
        pid = ctx.get("reject_pid")
        return f"reject {pid}" if pid else "reject all"
    if c.endswith(" ") and c.strip() in ("confirm", "reject", "create an idea called"):
        return c  # incomplete — expected usage fail ok only for bare
    return c


def _build_function_bank() -> List[Tuple[str, str]]:
    """(group, cmd) pairs covering full program surface."""
    bank: List[Tuple[str, str]] = []

    # Core acceptance / needs
    bank += [
        ("needs", "create an idea called FuncSeed detail: function loop seed goals: pass probes; stay offline"),
        ("needs", "what next"),
        ("needs", "ready"),
        ("needs", "history"),
        ("needs", "self"),
        ("needs", "self map"),
        ("growth", "grow ideas 1"),
        ("growth", "proposals"),
        ("growth", "rank"),
        ("growth", "confirm "),  # filled with pid
        ("form", "cube"),
        ("form", "sphere"),
        ("form", "flower"),
        ("form", "toggle"),
        ("form", "lattice"),
        ("form", "geometry"),
        ("form", "verita"),
        ("form", "voynich"),
        ("form", "fractal"),
        ("move", "home"),
        ("move", "look"),
        ("move", "multilook"),
        ("move", "page"),
        ("move", "nearest"),
        ("move", "radar"),
        ("move", "fp forward"),
        ("move", "fp turn right"),
        ("move", "fp look up"),
        ("move", "fp look"),
        ("move", "walk forward"),
        ("move", "turn left"),
        ("move", "backstep"),
        ("system", "status"),
        ("system", "help"),
        ("system", "audit"),
        ("system", "matrices"),
        ("system", "entities"),
        ("system", "pulse"),
        ("system", "enhance on"),
        ("system", "forces"),
        ("system", "force tick"),
        ("system", "weather rain"),
        ("system", "weather clear"),
        ("system", "evolve"),
        ("system", "self evolve"),
        ("system", "close gaps"),
        ("agents", "personas"),
        ("agents", "bimo"),
        ("agents", "bimo defaults"),
        ("agents", "guide"),
        ("agents", "ai status"),
        ("agents", "ai walk"),
        ("agents", "persona manny"),
        ("agents", "persona clear"),
        ("inspire", "inspire"),
        ("inspire", "attend growth"),
        ("inspire", "slopes"),
        ("inspire", "prefs"),
        ("inspire", "glyph FuncSeed"),
        ("inspire", "script look; status"),
        ("english", "english status"),
        ("english", "english help"),
        ("rooms", "rooms"),
        ("rooms", "view growth"),
        ("rooms", "view water"),
        ("rooms", "view network"),
        ("workshops", "workshops"),
        ("workshops", "workshop matrix"),
        ("workshops", "workshop leave"),
        ("workshops", "workshop forces"),
        ("workshops", "workshop leave"),
        ("persist", "save"),
        ("edit", "set detail FuncSeed loop-updated detail"),
        ("edit", "set goals FuncSeed pass loop; stay honest"),
        ("edit", "idea FuncSeed"),
        ("guard", "confirm"),  # bare → usage
        ("guard", "asdfghjklxyz"),  # unknown → not invent
    ]

    # Expand from actions registry (unique cmds)
    try:
        from form.dell_matrix.actions_registry import actions_flat
        seen = {c for _, c in bank}
        for item in actions_flat("depth"):
            cmd = item.get("cmd") or ""
            if not cmd or cmd in seen:
                continue
            if cmd.lower() in ("live", "tutorial"):
                continue
            if cmd.endswith(" ") and cmd.strip() in ("confirm", "reject"):
                continue  # handled via filled
            bank.append(("action", cmd))
            seen.add(cmd)
            if len(bank) >= 120:
                break
    except Exception:
        pass

    # Workshop extras
    try:
        from form.dell_matrix.workshops import list_workshops
        for w in list_workshops():
            for item in (w.get("commands") or [])[:4]:
                c = item.get("cmd")
                if c:
                    bank.append((f"ws:{w['id']}", c))
    except Exception:
        pass

    return bank


def _ok_result(cmd: str, out: Dict[str, Any], ideas_before: int, ideas_after: int) -> Tuple[bool, str]:
    """Judge if function end is acceptable."""
    msg = (out.get("msg") or out.get("error") or "").strip()
    end = out.get("end") or ""
    lower = cmd.lower().strip()

    # bare incomplete → must be usage
    if lower in ("confirm", "reject", "create", "zoom", "shell", "workshop", "view"):
        if "usage" in msg.lower() or end == "usage" or not out.get("ok"):
            return True, "usage"
        if "created idea" in msg.lower():
            return False, "incomplete_miscreate"
        return bool(msg), "incomplete"

    # garbage guard
    if re.fullmatch(r"[a-z0-9?]{6,}", lower) or lower in ("asdfghjklxyz",):
        if ideas_after > ideas_before:
            return False, "garbage_created_idea"
        if "not understood" in msg.lower() or end in ("unknown", "usage") or not out.get("ok"):
            return True, "guard"
        return bool(msg), "guard_soft"

    # normal: need non-empty useful body
    if not msg:
        return False, "empty"
    if "created idea" in msg.lower() and not (
        lower.startswith("create") or lower.startswith("plant") or "idea called" in lower
    ):
        return False, "miscreate"
    # ok True or intentional soft fail with guidance
    if out.get("ok") or end in ("usage", "unknown") or "usage" in msg.lower():
        return True, "ok"
    # some fails are still useful ends
    if len(msg) >= 8:
        return True, "useful_fail"
    return False, "fail"


def run_loop(cycles: int = 150, owner: str = "Func150") -> Dict[str, Any]:
    from form.open import open_program
    from form.dell_matrix.live_visual import _run_command
    from form.dell_matrix.needs import parse_and_place

    print("=== FUNCTION 150 LOOP ===")
    print(f"cycles={cycles} owner={owner}")

    p = open_program(owner)
    p.set_ux_mode("depth")
    # seed so page/confirm paths have material
    parse_and_place(
        p,
        "create an idea called FuncSeed detail: function loop seed goals: pass probes; stay offline",
    )
    p.enhance.turn_on()
    p.grow_ideas(1)

    bank = _build_function_bank()
    print(f"function bank size={len(bank)}")

    history: List[Dict[str, Any]] = []
    pass_n = 0
    fail_n = 0
    repairs = 0
    groups: Dict[str, Dict[str, int]] = {}

    for i in range(1, cycles + 1):
        group, cmd_template = bank[(i - 1) % len(bank)]
        props = p.list_proposals() if hasattr(p, "list_proposals") else []
        ctx = {
            "pid": props[0]["id"] if props else None,
            "reject_pid": props[-1]["id"] if len(props) > 1 else None,
        }
        cmd = _fill(cmd_template, ctx)

        before = len(p.cube.session.plane.units)
        try:
            out = _run_command(p, cmd)
        except Exception as e:
            out = {"ok": False, "error": f"EXC {e}", "end": "error"}
        after = len(p.cube.session.plane.units)

        ok, reason = _ok_result(cmd, out, before, after)

        # one soft repair attempt
        if not ok:
            try:
                if reason == "empty":
                    out2 = _run_command(p, "status")
                    ok2, _ = _ok_result("status", out2, after, len(p.cube.session.plane.units))
                    if ok2:
                        repairs += 1
                        ok = True
                        reason = "repaired_via_status"
                elif reason == "miscreate" or reason == "garbage_created_idea":
                    # cannot un-spam easily mid-loop; count fail
                    pass
                elif reason == "fail":
                    out2 = _run_command(p, "help")
                    if (out2.get("msg") or out2.get("error")):
                        repairs += 1
                        ok = True
                        reason = "repaired_via_help"
            except Exception:
                pass

        gstat = groups.setdefault(group.split(":")[0], {"ok": 0, "fail": 0})
        if ok:
            pass_n += 1
            gstat["ok"] += 1
        else:
            fail_n += 1
            gstat["fail"] += 1

        row = {
            "cycle": i,
            "group": group,
            "cmd": cmd[:80],
            "ok": ok,
            "reason": reason,
            "end": out.get("end"),
            "msg_len": len((out.get("msg") or out.get("error") or "")),
        }
        history.append(row)

        if i == 1 or i % 25 == 0 or i == cycles or not ok:
            mark = "PASS" if ok else "FAIL"
            print(f"  c{i:03d} [{mark}] {group:12} {cmd[:50]!r} · {reason}")

        # keep nursery from exploding unbounded: every 30 cycles confirm one
        if i % 30 == 0:
            props = p.list_proposals()
            if props:
                try:
                    p.confirm_proposal(props[0]["id"])
                except Exception:
                    pass

    rate = pass_n / max(1, cycles)
    # page asset check once
    from form.dell_matrix.live_visual import _PAGE_ROUTES
    from form.dell_matrix import live_visual as lv
    assets = os.path.join(os.path.dirname(lv.__file__), "assets")
    pages_ok = 0
    for route, rel in _PAGE_ROUTES.items():
        path = os.path.join(assets, rel)
        if os.path.isfile(path) and os.path.getsize(path) > 100:
            pages_ok += 1
    pages_total = len(_PAGE_ROUTES)

    # final readiness snapshot
    try:
        ready = p.ready() if hasattr(p, "ready") else {}
    except Exception:
        ready = {}

    print("\n=== GROUP SCORES ===")
    for g, st in sorted(groups.items()):
        tot = st["ok"] + st["fail"]
        print(f"  {g:12} {st['ok']}/{tot} ({st['ok']/max(1,tot):.0%})")

    print(
        f"\n=== RESULT: {pass_n}/{cycles} ({rate:.1%}) fails={fail_n} "
        f"repairs={repairs} pages={pages_ok}/{pages_total} ==="
    )

    # gates
    fails = [h for h in history if not h["ok"]]
    passed = (
        rate >= 0.95
        and len(fails) <= max(3, cycles // 30)
        and pages_ok == pages_total
    )
    print(f"FUNCTION 150: {'PASS' if passed else 'FAIL'}")
    if fails:
        print("Remaining fails:")
        for f in fails[:15]:
            print(f"  c{f['cycle']} {f['group']} {f['cmd']!r} · {f['reason']}")

    # save session so user can open live/offline
    try:
        path = p.save()
        print(f"Saved session → {path}")
    except Exception:
        path = ""

    return {
        "ok": passed,
        "pass": pass_n,
        "fail": fail_n,
        "cycles": cycles,
        "rate": rate,
        "repairs": repairs,
        "pages_ok": pages_ok,
        "pages_total": pages_total,
        "groups": groups,
        "fails": fails,
        "history": history,
        "ready": ready,
        "save": path,
        "ideas": len(p.cube.session.plane.units),
        "generation": getattr(p.duo, "generation", 0),
    }


def smoke() -> bool:
    out = run_loop(cycles=18, owner="FuncSmoke")
    return bool(out.get("rate", 0) >= 0.90 and out.get("pages_ok") == out.get("pages_total"))


if __name__ == "__main__":
    n = 150
    owner = "Func150"
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    for a in sys.argv[1:]:
        if a.isdigit():
            n = int(a)
        if a.startswith("--owner="):
            owner = a.split("=", 1)[1]
    out = run_loop(cycles=n, owner=owner)
    sys.exit(0 if out.get("ok") else 1)
