#!/usr/bin/env python3
"""
Free Matrix — Track B primary.

ONE PROCESS: live UI server + awake growth loop together.

Perspectives (who sees what):
  first  — cone in front only
  third  — around the body
  parts  — filtered slice of the plane
  whole  — full plane (omniscient)

Roles:
  user / architect — may switch to ANY mode at any time
  ai_first / ai_third / ai_parts / ai_whole — defaults; user can override

  python -m form.dell_matrix.free_matrix
  python -m form.dell_matrix.free_matrix --awake-every 30
  python -m form.dell_matrix.free_matrix --smoke

Trading (Track C) skipped.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
import argparse
import time

# module-level registry attached to program when opened
_REGISTRY = None


def open_world(owner: str = "FreeMatrix"):
    global _REGISTRY
    from form.open import open_program
    from form.dell_matrix.perspective_views import bootstrap_default_viewers
    program = open_program(owner)
    _REGISTRY = bootstrap_default_viewers(program)
    program.perspectives = _REGISTRY
    return program


def perspectives(program=None):
    global _REGISTRY
    if program is not None and getattr(program, "perspectives", None) is not None:
        return program.perspectives
    return _REGISTRY


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


def see(program, viewer_id: str = "user", mode: Optional[str] = None) -> Dict[str, Any]:
    """See through a viewer's perspective. User/architect may pass any mode."""
    from form.dell_matrix.perspective_views import see_as, sync_viewer_pose
    reg = perspectives(program)
    if reg is None:
        # fallback classic cone
        from form.dell_matrix.vision import compute_vision, format_look_report
        from form.dell_matrix.perspective_views import _nodes_from_program, _pose_from_program
        pos, facing = _pose_from_program(program)
        nodes = _nodes_from_program(program)
        vis = compute_vision(list(pos), facing, nodes)
        return {"mode": "first", "vision": vis, "report": format_look_report(vis)}
    v = reg.viewers.get(viewer_id)
    if v is None:
        return {"ok": False, "error": f"unknown viewer {viewer_id}", "viewers": reg.list_viewers()}
    sync_viewer_pose(program, v)
    return see_as(program, v, mode=mode)


def set_view(program, viewer_id: str, mode: str, *, as_role: str = "user") -> Dict[str, Any]:
    """User/architect: set any viewer's mode (first|third|parts|whole)."""
    reg = perspectives(program)
    if reg is None:
        return {"ok": False, "error": "no registry — open_world first"}
    return reg.set_mode(viewer_id, mode, as_role=as_role)


def list_views(program) -> List[Dict[str, Any]]:
    reg = perspectives(program)
    if reg is None:
        return []
    return reg.list_viewers()


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


def draw_frame(program, viewer_id: str = "user", mode: Optional[str] = None) -> Dict[str, Any]:
    fp = {}
    try:
        fp = view(program)
    except Exception:
        pass
    vision = see(program, viewer_id=viewer_id, mode=mode)
    center = fp.get("center") or fp.get("pos") or []
    facing = fp.get("facing") or fp.get("yaw") or "?"
    mode_s = vision.get("mode") or mode or "?"
    lines = [
        "╔══════════════════════════════════════╗",
        "║         FREE MATRIX · DRAW FRAME     ║",
        "╠══════════════════════════════════════╣",
        f"║ viewer: {viewer_id[:28]:28} ║",
        f"║ mode:   {str(mode_s)[:28]:28} ║",
        f"║ center: {str(center)[:28]:28} ║",
        f"║ facing: {str(facing)[:28]:28} ║",
        "╠══════════════════════════════════════╣",
    ]
    for row in (vision.get("report") or [])[:8]:
        lines.append(f"║ {str(row)[:36]:36} ║")
    lines.append("╚══════════════════════════════════════╝")
    glyph = None
    try:
        from form.dell_matrix.inspire_pack import procedural_glyph
        glyph = procedural_glyph(str(center))
    except Exception:
        pass
    return {"ok": True, "frame": "\n".join(lines), "glyph": glyph, "vision": vision}


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


def run_one_process(
    program,
    *,
    port: int = 8765,
    awake_every: float = 30.0,
    net_query: str = "matrix free agent coherence embodiment",
    ui: bool = True,
) -> None:
    """
    ONE PROCESS law:
      · live UI server in background thread (if ui)
      · awake growth loop in the main thread until Ctrl+C
    """
    if ui:
        info = start_ui(program, port=port, background=True)
        if info.get("ok"):
            print(f"UI: {info.get('url')}")
            print("Pages: walk lattice nursery program personas forces geometry …")
        else:
            print("UI issue:", info)
            print("Continue with awake loop only.")

    print(f"Awake loop every {awake_every}s · Ctrl+C to stop")
    print("Perspectives:", [v["id"] + ":" + v["mode"] for v in list_views(program)])
    tick = 0
    try:
        while True:
            tick += 1
            ar = pulse_awake(net_query)
            ag = ar.get("auto_growth") or ar
            conf = ag.get("confirmed_labels") or []
            print(
                f"[awake {tick}] confirmed={ag.get('confirmed', 0)} "
                f"net={ag.get('net_count', '?')} labels={conf[:3]}"
            )
            # soft companion drift each cycle
            try:
                companion_step(program, 1)
            except Exception:
                pass
            time.sleep(max(5.0, float(awake_every)))
    except KeyboardInterrupt:
        print("\nFree matrix one-process stopped.")


def status(program) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "track": "B",
        "primary": "free_matrix_ui",
        "one_process": "ui_thread + awake_main",
        "perspectives": list_views(program),
        "skipped": ["Track C trading"],
    }
    try:
        out["view"] = view(program)
    except Exception as e:
        out["view_error"] = str(e)
    try:
        out["see_user_first"] = see(program, "user", "first")
        out["see_architect_whole"] = see(program, "architect", "whole")
    except Exception as e:
        out["see_error"] = str(e)
    return out


def smoke() -> bool:
    print("=== FREE MATRIX SMOKE ===")
    r = []
    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}"); r.append(bool(ok))
    # perspective unit smoke always
    try:
        from form.dell_matrix.perspective_views import smoke as ps
        rec("perspective_smoke", ps())
    except Exception as e:
        print("perspective", e); rec("perspective_smoke", False)
    try:
        p = open_world("SmokeFree")
        rec("open", p is not None)
        rec("registry", len(list_views(p)) >= 4)
        rec("set_whole", set_view(p, "companion", "whole").get("ok") is True)
        rec("see_third", see(p, "user", "third").get("ok") is True)
        rec("see_whole", see(p, "architect", "whole").get("ok") is True)
    except Exception as e:
        print("open/see", e)
        rec("open", False)
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="DellMatrix Free Matrix — one process")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--owner", default="FreeMatrix")
    ap.add_argument("--awake-every", type=float, default=30.0,
                    help="Seconds between awake pulses in the one-process loop")
    ap.add_argument("--no-awake", action="store_true", help="UI only, no growth loop")
    ap.add_argument("--no-ui", action="store_true", help="Awake loop only, no HTTP UI")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args(argv)

    if args.smoke:
        return 0 if smoke() else 1

    print("=" * 56)
    print("  FREE MATRIX · one process · Track B")
    print("  UI thread + awake loop · multi-perspective")
    print("=" * 56)

    program = open_world(args.owner)
    print("Viewers:")
    for v in list_views(program):
        print(f"  · {v['id']:12} role={v['role']:12} mode={v['mode']}")

    print("\nUser can switch any view:")
    print("  set_view(p, 'companion', 'whole')")
    print("  see(p, 'user', 'third')  see(p, 'architect', 'whole')")

    fr = draw_frame(program, "user", "first")
    print(fr.get("frame", ""))

    if args.no_awake and args.no_ui:
        print("Nothing to run (--no-awake and --no-ui).")
        return 0

    if args.no_awake:
        # UI only, keep process alive
        info = start_ui(program, port=args.port, background=True)
        print(info.get("url"))
        try:
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            print("\nStopped.")
        return 0

    run_one_process(
        program,
        port=args.port,
        awake_every=args.awake_every,
        ui=not args.no_ui,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
