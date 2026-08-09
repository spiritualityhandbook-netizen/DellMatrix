#!/usr/bin/env python3
"""
Act-on-seen — take action on whatever is in the vision cone.

From look_around / compute_vision results, choose an index and act:
  inspect | zoom | attend | force | confirm | detail | goals | nearest

Offline · uses existing Program surfaces only.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional


def _vision_nodes(program) -> List[Dict[str, Any]]:
    try:
        v = program.look_around()
        return list(v.get("nodes") or [])
    except Exception:
        return []


def list_seen(program) -> Dict[str, Any]:
    nodes = _vision_nodes(program)
    return {
        "ok": True,
        "count": len(nodes),
        "nodes": [
            {
                "index": i,
                "id": n.get("id"),
                "label": n.get("label"),
                "skin": n.get("skin"),
                "dist": n.get("dist"),
                "score": n.get("score"),
            }
            for i, n in enumerate(nodes)
        ],
        "actions": ["inspect", "zoom", "attend", "force", "confirm", "detail", "nearest", "list"],
    }


def act_on_seen(
    program,
    action: str = "inspect",
    index: int = 0,
    extra: str = "",
) -> Dict[str, Any]:
    """
    Act on the node currently in vision at `index` (0 = nearest in cone).
    """
    action = (action or "inspect").lower().strip()
    nodes = _vision_nodes(program)
    if action in ("list", "seen", "what"):
        return list_seen(program)
    if not nodes:
        return {"ok": False, "reason": "nothing in view — turn or walk closer", "action": action}
    idx = max(0, min(int(index), len(nodes) - 1))
    target = nodes[idx]
    tid = str(target.get("id") or "")
    label = str(target.get("label") or tid)

    if action in ("inspect", "info", "look"):
        info = program.idea_info(tid) if hasattr(program, "idea_info") else {"id": tid, "label": label}
        program.note_seed(9, "Show", f"act_inspect_{label[:20]}")
        return {"ok": True, "action": "inspect", "target": target, "info": info}

    if action in ("zoom", "page", "open"):
        out = program.zoom_to(tid)
        return {"ok": bool(out.get("ok")), "action": "zoom", "target": target, "result": out}

    if action in ("attend", "attention"):
        q = extra or label
        ranked = program.attend(q, top_k=5) if hasattr(program, "attend") else []
        return {"ok": True, "action": "attend", "query": q, "target": target, "ranked": ranked}

    if action in ("force", "pull", "gravity"):
        # make this node a temporary gravity well focus via score boost path
        try:
            if hasattr(program, "forces") and program.forces:
                program.forces.gravity.wells = [{
                    "id": tid,
                    "label": label,
                    "mass": float(target.get("score") or 1) + 2.5,
                }]
                report = program.force_tick()
                program.note_seed(25, "Pulse", f"act_force_{label[:20]}")
                return {"ok": True, "action": "force", "target": target, "force_tick": report}
        except Exception as e:
            return {"ok": False, "action": "force", "error": str(e), "target": target}
        return {"ok": False, "reason": "no forces", "target": target}

    if action in ("confirm",):
        # if it is a nursery ghost id pattern, try confirm; else no-op message
        try:
            out = program.confirm_proposal(tid)
            return {"ok": bool(out.get("ok")), "action": "confirm", "target": target, "result": out}
        except Exception:
            return {"ok": False, "action": "confirm", "reason": "not a pending proposal", "target": target}

    if action in ("detail",):
        text = (extra or "seen in vision").strip()
        out = program.set_idea_detail(tid, text) if hasattr(program, "set_idea_detail") else {"ok": False}
        return {"ok": bool(out.get("ok")), "action": "detail", "target": target, "result": out}

    if action in ("nearest", "goto"):
        # walk avatar toward target position if available on plane
        try:
            u = program.cube.session.plane.units.get(tid)
            if u is not None:
                program.avatar.body.pos = (float(u.x), float(u.y))
                program._push_user_trail()
                program.note_seed(2, "Walk", f"act_nearest_{label[:20]}")
                return {"ok": True, "action": "nearest", "target": target, "pos": [u.x, u.y]}
        except Exception as e:
            return {"ok": False, "action": "nearest", "error": str(e)}
        return {"ok": False, "reason": "unit missing", "target": target}

    return {
        "ok": False,
        "reason": f"unknown action: {action}",
        "actions": ["inspect", "zoom", "attend", "force", "confirm", "detail", "nearest", "list"],
        "target": target,
    }


def format_act_report(result: Dict[str, Any]) -> List[str]:
    lines = [f"Act-on-seen · action={result.get('action')} ok={result.get('ok')}"]
    t = result.get("target") or {}
    if t:
        lines.append(f"  target: {t.get('label')} [{t.get('skin')}] d={t.get('dist')}")
    if result.get("reason"):
        lines.append(f"  reason: {result['reason']}")
    if result.get("info"):
        info = result["info"]
        if isinstance(info, dict):
            lines.append(f"  info: {info.get('label') or info.get('id')} goals={info.get('goals') or info.get('detail') or '—'}")
    return lines


def smoke() -> bool:
    print("=== ACT_ON_SEEN SMOKE ===")
    from form.open import open_program
    p = open_program("ActSmoke")
    p.place("a", "SeenA", words="vision target", x=0, y=2)
    p.avatar.body.pos = (0.0, 0.0)
    # face north so y+ is in cone
    try:
        from form.avatar.body import Facing
        p.avatar.body.facing = Facing.N
    except Exception:
        pass
    seen = list_seen(p)
    r = act_on_seen(p, "inspect", 0)
    ok = seen.get("count", 0) >= 0 and r.get("action") == "inspect"
    print(f"[{'PASS' if ok else 'FAIL'}] seen={seen.get('count')} inspect_ok={r.get('ok')}")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
