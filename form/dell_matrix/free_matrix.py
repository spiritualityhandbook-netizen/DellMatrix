#!/usr/bin/env python3
"""
Free Matrix — Track B primary entry.

Chat is a *window* into the matrix, not the prison.
You (and the AI companion) walk, look, and act inside the live UI.

  python -m form.dell_matrix.free_matrix
  python -m form.dell_matrix.free_matrix --port 8765
  python -m form.dell_matrix.free_matrix --awake    # also run growth heartbeat
  python -m form.dell_matrix.free_matrix --smoke

Stack used:
  form/open.Program
  live_visual.start_live  → browser UI (walk lattice nursery …)
  first_person            → move / turn / look
  vision + act_on_seen    → see and act on what is in view
  companion               → AI body in the same world
  matrix_awake (optional) → continuous growth while UI stays up
  draw_frame              → text/SVG-ish frame of current view (Track D seed)

Not included: trading (Track C skipped by operator).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
import argparse
import json
import time


def open_world(owner: str = "FreeMatrix"):
    from form.open import open_program
    return open_program(owner)


def walk(program, direction: str = "forward") -> Dict[str, Any]:
    from form.dell_matrix.first_person import move_fp
    return move_fp(program, direction)


def turn(program, direction: str = "right") -> Dict[str, Any]:
    from form.dell_matrix.first_person import turn_fp
    return turn_fp(program, direction)


def look(program, pitch: str = "level") -> Dict[str, Any]:
    from form.dell_matrix.first_person import look_fp
    return look_fp(program, pitch)


def view(program) -> Dict[str, Any]:
    from form.dell_matrix.first_person import first_person_view
    return first_person_view(program)


def see(program) -> Dict[str, Any]:
    from form.dell_matrix.vision import compute_vision, format_look_report
    vis = compute_vision(program)
    return {"vision": vis, "report": format_look_report(vis)}


def act(program, action: str = "inspect", target: str = "") -> Dict[str, Any]:
    from form.dell_matrix.act_on_seen import act_on_seen, format_act_report
    result = act_on_seen(program, action=action, target=target)
    return {"result": result, "report": format_act_report(result)}


def companion_step(program, steps: int = 1) -> Dict[str, Any]:
    comp = getattr(program, "companion", None)
    if comp is None:
        try:
            from form.dell_matrix.companion import AICompanion
            comp = AICompanion()
            program.companion = comp
        except Exception as e:
            return {"ok": False, "error": str(e)}
    if hasattr(comp, "step"):
        pos = comp.step(steps)
        return {"ok": True, "pos": pos, "doing": getattr(comp, "doing", ""), "last": getattr(comp, "last_action", "")}
    return {"ok": False, "error": "companion has no step"}


def draw_frame(program) -> Dict[str, Any]:
    """Track D seed: render a portable frame of where you are and what you see."""
    fp = view(program)
    vision = see(program)
    center = fp.get("center") or fp.get("pos") or []
    facing = fp.get("facing") or fp.get("yaw") or "?"
    lines = [
        "╔══════════════════════════════════════╗",
        "║         FREE MATRIX · DRAW FRAME     ║",
        "╠══════════════════════════════════════╣",
        f"║ center: {str(center)[:28]:28} ║",
        f"║ facing: {str(facing)[:28]:28} ║",
        "╠══════════════════════════════════════╣",
    ]
    report = vision.get("report") or []
    for row in report[:8]:
        lines.append(f"║ {str(row)[:36]:36} ║")
    lines.append("╚══════════════════════════════════════╝")
    frame = "\n".join(lines)
    # optional glyph from inspire if present
    glyph = None
    try:
        from form.dell_matrix.inspire_pack import procedural_glyph
        glyph = procedural_glyph(str(center))
    except Exception:
        glyph = None
    return {"ok": True, "frame": frame, "glyph": glyph, "center": center, "facing": facing}


def start_ui(program, port: int = 8765, background: bool = True) -> Dict[str, Any]:
    from form.dell_matrix.live_visual import start_live
    return start_live(program, port=port, background=background)


def pulse_awake(net_query: str = "") -> Dict[str, Any]:
    try:
        from form.dell_matrix.matrix_awake import AWAKE
        AWAKE.auto_on()
        AWAKE.turn_on()
        return AWAKE.step(net_query=net_query)
    except Exception as e:
        return {"ok": False, "error": str(e)}


def status(program) -> Dict[str, Any]:
    out: Dict[str, Any] = {"track": "B", "primary": "free_matrix_ui"}
    try:
        out["view"] = view(program)
    except Exception as e:
        out["view_error"] = str(e)
    try:
        out["see"] = see(program)
    except Exception as e:
        out["see_error"] = str(e)
    try:
        from form.dell_matrix.matrix_body import body_pulse
        out["body"] = body_pulse()
    except Exception as e:
        out["body_error"] = str(e)
    out["skipped"] = ["Track C trading"]
    out["also"] = ["Track A awake optional", "Track D draw_frame seed"]
    return out


def smoke() -> bool:
    print("=== FREE MATRIX SMOKE (Track B) ===")
    r = []
    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}"); r.append(bool(ok))
    try:
        p = open_world("SmokeFree")
        rec("open", p is not None)
    except Exception as e:
        print("open failed", e)
        rec("open", False)
        print(f"=== {sum(r)}/{len(r)} ===")
        return False
    try:
        w = walk(p, "forward")
        rec("walk", w.get("ok") is True or "view" in w)
    except Exception as e:
        print("walk", e); rec("walk", False)
    try:
        t = turn(p, "right")
        rec("turn", t.get("ok") is True or "view" in t)
    except Exception as e:
        print("turn", e); rec("turn", False)
    try:
        v = view(p)
        rec("view", isinstance(v, dict))
    except Exception as e:
        print("view", e); rec("view", False)
    try:
        d = draw_frame(p)
        rec("draw_frame", d.get("ok") is True)
        print(d.get("frame", "")[:400])
    except Exception as e:
        print("draw", e); rec("draw_frame", False)
    try:
        s = status(p)
        rec("status", s.get("track") == "B")
    except Exception as e:
        print("status", e); rec("status", False)
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="DellMatrix Free Matrix — Track B")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--owner", default="FreeMatrix")
    ap.add_argument("--awake", action="store_true", help="Run one awake growth pulse after UI start")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--no-ui", action="store_true", help="API only — no HTTP server")
    args = ap.parse_args(argv)

    if args.smoke:
        return 0 if smoke() else 1

    print("=" * 56)
    print("  FREE MATRIX · Track B primary")
    print("  Chat is a window. The world is the matrix.")
    print("=" * 56)

    program = open_world(args.owner)
    st = status(program)
    print("status track:", st.get("track"))
    if "view" in st:
        print("view keys:", list((st.get("view") or {}).keys())[:12])

    fr = draw_frame(program)
    print(fr.get("frame", ""))

    if not args.no_ui:
        info = start_ui(program, port=args.port, background=True)
        if info.get("ok"):
            print(f"\nOpen in browser: {info.get('url')}")
            print("Pages: walk lattice nursery program personas forces geometry …")
            print("Keep this process alive or the UI dies.")
        else:
            print("UI start issue:", info)
            print("Fallback offline: use Program command `visual` for HTML snapshot")

    if args.awake:
        print("\nAwake pulse (Track A support)…")
        ar = pulse_awake("matrix coherence free agent embodiment")
        ag = ar.get("auto_growth") or ar
        print("awake confirmed:", ag.get("confirmed_labels") or ag.get("confirmed"))

    print("\nAPI in Python:")
    print("  from form.dell_matrix import free_matrix as fm")
    print("  p = fm.open_world()")
    print("  fm.walk(p,'forward'); fm.turn(p,'left'); fm.look(p,'up')")
    print("  fm.see(p); fm.act(p,'inspect'); fm.draw_frame(p)")
    print("  fm.start_ui(p)")
    print("\nSkipped: Track C trading")
    print("Also densified: Track A (--awake), Track D (draw_frame seed)")

    if not args.no_ui:
        print("\nCtrl+C to stop")
        try:
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            print("\nFree matrix stopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
