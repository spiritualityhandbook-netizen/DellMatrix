#!/usr/bin/env python3
"""
First-person matrix walk — inside centerpoints (Minecraft-like).

You stand at the center of a lattice cell (block/sphere dual).
Move centerpoint → centerpoint. Look around for pages of data.
What you see depends on perspective, forces, harmony, and resonance.

Not a top-down vision cone. First-person interior of the matrix.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import math

# Horizontal facing (yaw) — walk on HV plane
_YAW_ORDER = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
_YAW_DELTA = {
    "N": (0, 1), "NE": (1, 1), "E": (1, 0), "SE": (1, -1),
    "S": (0, -1), "SW": (-1, -1), "W": (-1, 0), "NW": (-1, 1),
}
# Pitch: look / move on F axis
_PITCHES = ("down", "level", "up")


def snap_center(x: float, y: float, f: float = 0.0) -> Tuple[int, int, int]:
    return int(round(x)), int(round(y)), int(round(f))


def neighbors_cube(h: int, v: int, f: int) -> Dict[str, Tuple[int, int, int]]:
    """6-connected orthogonal neighbors (block faces)."""
    return {
        "N": (h, v + 1, f),
        "S": (h, v - 1, f),
        "E": (h + 1, v, f),
        "W": (h - 1, v, f),
        "up": (h, v, f + 1),
        "down": (h, v, f - 1),
    }


def neighbors_sphere(h: int, v: int, f: int) -> Dict[str, Tuple[int, int, int]]:
    """
    Sphere dual: same centers, but primary links are radial shells
    (in/out) plus tangential ring steps on current shell.
    """
    r = max(abs(h), abs(v), abs(f))
    # outward / inward along max-norm ray
    out_h = h + (1 if h > 0 else (-1 if h < 0 else 0))
    out_v = v + (1 if v > 0 else (-1 if v < 0 else 0))
    out_f = f + (1 if f > 0 else (-1 if f < 0 else 0))
    if h == 0 and v == 0 and f == 0:
        # at origin: six directions outward
        return neighbors_cube(h, v, f)
    # normalize step to grow shell by 1
    mh = abs(h) or 1
    # simpler: use cube neighbors + radial label
    base = neighbors_cube(h, v, f)
    # re-key radial
    base["out"] = (out_h if abs(out_h) >= abs(h) or h == 0 else h,
                   out_v if abs(out_v) >= abs(v) or v == 0 else v,
                   out_f if abs(out_f) >= abs(f) or f == 0 else f)
    # fix origin shell expansion properly
    if r == 0:
        return neighbors_cube(h, v, f)
    # inward toward origin
    scale = (r - 1) / r if r > 0 else 0
    base["in"] = (
        int(round(h * scale)),
        int(round(v * scale)),
        int(round(f * scale)),
    )
    return base


def neighbors_for_form(form: str, h: int, v: int, f: int) -> Dict[str, Tuple[int, int, int]]:
    form = (form or "cube").lower()
    if form in ("sphere", "circle", "core", "flower"):
        return neighbors_sphere(h, v, f)
    return neighbors_cube(h, v, f)


def face_toward(yaw: str, pitch: str = "level") -> Tuple[int, int, int]:
    """Unit step in look direction."""
    if pitch == "up":
        return (0, 0, 1)
    if pitch == "down":
        return (0, 0, -1)
    dx, dy = _YAW_DELTA.get(yaw.upper(), (0, 1))
    # cardinal only for clean block steps when walking
    if abs(dx) and abs(dy):
        # diagonal: prefer longer component as primary for "forward block"
        pass
    return (dx, dy, 0)


def turn_yaw(yaw: str, steps: int = 1) -> str:
    # turn by 90° (2 steps of 8-way) for clean Minecraft feel
    order = _YAW_ORDER
    idx = order.index(yaw) if yaw in order else 0
    # 2 steps = 90°
    return order[(idx + 2 * steps) % 8]


def units_at_center(
    nodes: List[Dict[str, Any]],
    h: int, v: int, f: int,
    *,
    tol: float = 0.51,
) -> List[Dict[str, Any]]:
    """Ideas whose plane (x,y) snaps to this HV center; f used for shell ranking."""
    here = []
    for n in nodes:
        nx = float(n.get("x", 0) or 0)
        ny = float(n.get("y", 0) or 0)
        if abs(nx - h) <= tol and abs(ny - v) <= tol:
            here.append(n)
    return here


def resonance_rank(
    nodes: List[Dict[str, Any]],
    *,
    center: Tuple[int, int, int],
    scores: Optional[Dict[str, float]] = None,
    forces: Optional[Dict[str, Any]] = None,
    form: str = "cube",
) -> List[Dict[str, Any]]:
    """
    Place information where it belongs *now* at this centerpoint.
    Higher score, closer shell, force alignment → higher rank.
    """
    scores = scores or {}
    forces = forces or {}
    ch, cv, cf = center
    ranked = []
    active_forces = set(forces.get("active") or [])
    weather = (forces.get("weather") or "clear")
    for n in nodes:
        nx, ny = float(n.get("x", 0) or 0), float(n.get("y", 0) or 0)
        # distance under form metric
        if form in ("sphere", "core", "circle", "flower"):
            dist = math.sqrt((nx - ch) ** 2 + (ny - cv) ** 2 + (0 - cf) ** 2)
        else:
            dist = max(abs(nx - ch), abs(ny - cv), abs(0 - cf))
        sc = float(scores.get(n.get("id"), n.get("score") or 0) or 0)
        # force reach: growth boosts seed/flower; water boosts words/circle; etc.
        force_boost = 0.0
        skin = str(n.get("skin") or "")
        if "growth" in active_forces and skin in ("seed", "flower"):
            force_boost += 0.35
        if "water" in active_forces and skin in ("words", "circle", "sphere"):
            force_boost += 0.25
        if "gravity" in active_forces and sc > 1:
            force_boost += 0.2
        if weather == "fog":
            force_boost -= 0.15 * min(1.0, dist)
        if weather == "rain" and skin == "seed":
            force_boost += 0.15
        # harmonic: nearer + higher score
        harm = sc * 0.5 + force_boost + max(0.0, 3.0 - dist) * 0.4
        entry = dict(n)
        entry["_dist"] = round(dist, 3)
        entry["_resonance"] = round(harm, 3)
        entry["_at_center"] = dist < 0.51
        ranked.append(entry)
    ranked.sort(key=lambda x: (-x["_resonance"], x["_dist"]))
    return ranked


def cell_mandell(h: int, v: int, f: int, form: str = "cube") -> str:
    """Pure Mandell address for a centerpoint — bridge language for place."""
    kind = "SphereCell" if form in ("sphere", "circle", "core", "flower") else "CubeCell"
    return f"15[Map] :: {kind}@({h},{v},{f})"


def build_page(
    unit: Optional[Dict[str, Any]],
    *,
    perspective: str = "page",
    form: str = "cube",
    shell: int = 0,
    coord: Optional[Tuple[int, int, int]] = None,
) -> Dict[str, Any]:
    """Page card for one idea as seen from a centerpoint."""
    ch, cv, cf = coord or (0, 0, 0)
    mandel = cell_mandell(ch, cv, cf, form)
    if not unit:
        return {
            "ok": False,
            "empty": True,
            "title": f"Void cell ({ch},{cv},{cf})",
            "body": (
                "Empty centerpoint in the infinite matrix. "
                "Still a full cube/sphere you can enter. "
                "Resonance may bind ideas here when growth + forces align."
            ),
            "perspective": perspective,
            "form": form,
            "shell": shell,
            "coord": [ch, cv, cf],
            "mandel": mandel,
            "cell_kind": "sphere" if form in ("sphere", "circle", "core", "flower") else "cube",
        }
    return {
        "ok": True,
        "empty": False,
        "id": unit.get("id"),
        "title": unit.get("label"),
        "skin": unit.get("skin"),
        "score": unit.get("score") or unit.get("_resonance"),
        "detail": unit.get("detail") or "",
        "goals": unit.get("goals") or [],
        "words": unit.get("words") or "",
        "resonance": unit.get("_resonance"),
        "dist": unit.get("_dist"),
        "perspective": perspective,
        "form": form,
        "shell": shell,
        "at_center": unit.get("_at_center", False),
        "coord": [ch, cv, cf],
        "mandel": mandel,
        "cell_kind": "sphere" if form in ("sphere", "circle", "core", "flower") else "cube",
    }


def first_person_view(program) -> Dict[str, Any]:
    """
    Full first-person state for live visual.
    You are always at the center of the current block/sphere cell.
    """
    # center from avatar + Program center_f
    ax, ay = program.avatar.body.pos
    cf = int(getattr(program, "center_f", 0) or 0)
    h, v, f = snap_center(float(ax), float(ay), float(cf))
    # keep avatar snapped
    program.avatar.body.pos = (h, v)
    program.center_f = f

    yaw = program.avatar.body.facing.name if hasattr(program.avatar.body.facing, "name") else "N"
    pitch = str(getattr(program, "look_pitch", "level") or "level")
    if pitch not in _PITCHES:
        pitch = "level"

    form = program.lattice.perception.form.value if hasattr(program, "lattice") else "cube"
    perspective = program.cube.session.plane.perspective.value if hasattr(program, "cube") else "table"
    scores = program.scores() if hasattr(program, "scores") else {}
    nodes = program.nodes_payload() if hasattr(program, "nodes_payload") else []
    forces = program.forces.status() if hasattr(program, "forces") else {}

    nbrs = neighbors_for_form(form, h, v, f)
    # cardinal walk targets for Minecraft feel
    walk = {
        "forward": _step_block(h, v, f, yaw, 0),
        "back": _step_block(h, v, f, yaw, 4),  # 180°
        "left": _step_block(h, v, f, yaw, -2),
        "right": _step_block(h, v, f, yaw, 2),
        "up": (h, v, f + 1),
        "down": (h, v, f - 1),
    }

    ranked = resonance_rank(nodes, center=(h, v, f), scores=scores, forces=forces, form=form)
    here = [n for n in ranked if n.get("_at_center")]
    # visible in look direction: filter by forward half-space / pitch
    looking = _filter_looking(ranked, h, v, f, yaw, pitch)

    # face walls: what's on each adjacent center
    faces: Dict[str, Any] = {}
    for name, coord in {
        "front": walk["forward"],
        "back": walk["back"],
        "left": walk["left"],
        "right": walk["right"],
        "up": walk["up"],
        "down": walk["down"],
    }.items():
        ch, cv, cf_ = coord
        at = units_at_center(nodes, ch, cv, cf_)
        # rank those with resonance from here
        face_rank = resonance_rank(at or [], center=(h, v, f), scores=scores, forces=forces, form=form)
        if not face_rank and at:
            face_rank = at
        top = face_rank[0] if face_rank else None
        page = build_page(
            top, perspective=perspective, form=form,
            shell=int(max(abs(ch), abs(cv), abs(cf_))),
            coord=coord,
        )
        faces[name] = {
            "coord": list(coord),
            "empty": top is None,
            "page": page,
            "count": len(at),
            "skin": (top or {}).get("skin") if top else None,
            "mandel": cell_mandell(ch, cv, cf_, form),
            "color": {
                "cube": "#5b8def", "sphere": "#7c5cbf", "seed": "#3cb371",
                "flower": "#e6a817", "building": "#c47c48", "words": "#9aa3b2",
                "circle": "#2aa7a0", "core": "#d97706",
            }.get((top or {}).get("skin") or "", "#3d5a80"),
            "enterable": True,  # infinite matrix: every adjacent cell is a real cube/sphere
        }

    # pages at current center (primary + stack)
    shell_here = int(max(abs(h), abs(v), abs(f)))
    pages_here = [
        build_page(u, perspective=perspective, form=form, shell=shell_here, coord=(h, v, f))
        for u in here[:8]
    ]
    if not pages_here:
        pages_here = [build_page(None, perspective=perspective, form=form,
                                 shell=shell_here, coord=(h, v, f))]

    # forces reaching this centerpoint
    force_reach = _forces_at_center(forces, form, h, v, f)

    dual = "sphere" if form in ("cube", "square") else "cube"
    try:
        dual = program.lattice.perception.dual().value
    except Exception:
        pass

    cell_kind = "sphere" if form in ("sphere", "circle", "core", "flower") else "cube"
    here_mandel = cell_mandell(h, v, f, form)

    return {
        "mode": "first_person",
        "center": [h, v, f],
        "yaw": yaw,
        "pitch": pitch,
        "form": form,
        "dual": dual,
        "perspective": perspective,
        "cell_kind": cell_kind,
        "mandel": here_mandel,
        "mandel_bridge": {
            "here": here_mandel,
            "move_forward": f"19[Drive] :: step → {cell_mandell(*walk['forward'], form)}",
            "look": f"09[Show] :: look@{yaw}/{pitch}",
            "form_seed": f"15[Map] :: {form}",
            "law": "Floor Alpha·Delta·Omega·Omni · Mandell is the communication bridge",
        },
        "infinite": True,
        "neighbors": {k: list(v) for k, v in nbrs.items()},
        "walk": {k: list(v) for k, v in walk.items()},
        "faces": faces,
        "here": {
            "coord": [h, v, f],
            "pages": pages_here,
            "count": len(here),
            "mandel": here_mandel,
            "occupied": len(here) > 0,
        },
        "looking": {
            "yaw": yaw,
            "pitch": pitch,
            "pages": [
                build_page(
                    u, perspective=perspective, form=form,
                    shell=int(u.get("_dist") or 0),
                    coord=(int(round(float(u.get("x") or 0))), int(round(float(u.get("y") or 0))), 0),
                )
                for u in looking[:12]
            ],
            "count": len(looking),
        },
        "resonance_top": [
            {"id": u.get("id"), "label": u.get("label"), "resonance": u.get("_resonance"),
             "dist": u.get("_dist"), "skin": u.get("skin"),
             "x": u.get("x"), "y": u.get("y")}
            for u in ranked[:10]
        ],
        "forces_reach": force_reach,
        # Local occupancy radar (shell ±2 on H/V, same F) for minimap + HUD
        "radar": _local_radar(nodes, h, v, f, radius=2),
        # Nearest occupied cells for "jump to nearest" UX
        "nearest": [
            {
                "id": u.get("id"),
                "label": u.get("label"),
                "skin": u.get("skin"),
                "x": int(round(float(u.get("x") or 0))),
                "y": int(round(float(u.get("y") or 0))),
                "dist": u.get("_dist"),
                "resonance": u.get("_resonance"),
                "score": u.get("score"),
            }
            for u in ranked if not u.get("_at_center")
        ][:12],
        "occupied_faces": sum(1 for fce in faces.values() if not fce.get("empty")),
        "hint": (
            "Infinite matrix of cubes/spheres. Each wall is the next cell. "
            "W/S step · A/D turn · R/F up/down · click a face to enter that cell. "
            "L lattice · H home · J nearest · Mandell addresses every centerpoint."
        ),
    }


def _local_radar(
    nodes: List[Dict[str, Any]], h: int, v: int, f: int, radius: int = 2
) -> List[Dict[str, Any]]:
    """Compact grid of nearby cells with occupancy counts for HUD radar."""
    by: Dict[Tuple[int, int], List[Dict[str, Any]]] = {}
    for n in nodes or []:
        try:
            nx = int(round(float(n.get("x") or 0)))
            ny = int(round(float(n.get("y") or 0)))
        except Exception:
            continue
        if abs(nx - h) > radius or abs(ny - v) > radius:
            continue
        by.setdefault((nx, ny), []).append(n)
    cells: List[Dict[str, Any]] = []
    for dy in range(radius, -radius - 1, -1):
        for dx in range(-radius, radius + 1):
            x, y = h + dx, v + dy
            at = by.get((x, y), [])
            top = at[0] if at else None
            cells.append({
                "x": x, "y": y, "dx": dx, "dy": dy,
                "here": dx == 0 and dy == 0,
                "count": len(at),
                "skin": (top or {}).get("skin"),
                "label": (top or {}).get("label"),
                "id": (top or {}).get("id"),
            })
    return cells


def _step_block(h: int, v: int, f: int, yaw: str, turn_steps_45: int) -> Tuple[int, int, int]:
    """Step one block in yaw rotated by turn_steps_45 (units of 45°). Cardinalized."""
    order = _YAW_ORDER
    idx = order.index(yaw) if yaw in order else 0
    face = order[(idx + turn_steps_45) % 8]
    dx, dy = _YAW_DELTA[face]
    # for movement into blocks, use orthogonal step only (Minecraft)
    if abs(dx) and abs(dy):
        # pick dominant for diagonal faces when walking "forward" on NE etc.
        if abs(dx) >= abs(dy):
            dy = 0
            dx = 1 if dx > 0 else -1
        else:
            dx = 0
            dy = 1 if dy > 0 else -1
    return (h + dx, v + dy, f)


def _filter_looking(
    ranked: List[Dict[str, Any]],
    h: int, v: int, f: int,
    yaw: str, pitch: str,
) -> List[Dict[str, Any]]:
    if pitch == "up":
        # prefer higher shell / labels above — use score as stand-in for "above"
        return [n for n in ranked if not n.get("_at_center")][:12]
    if pitch == "down":
        return list(reversed([n for n in ranked if not n.get("_at_center")][:12]))
    dx, dy = _YAW_DELTA.get(yaw, (0, 1))
    # normalize
    mag = math.hypot(dx, dy) or 1
    fx, fy = dx / mag, dy / mag
    out = []
    for n in ranked:
        if n.get("_at_center"):
            continue
        vx = float(n.get("x", 0) or 0) - h
        vy = float(n.get("y", 0) or 0) - v
        if math.hypot(vx, vy) < 0.01:
            continue
        # forward half
        dot = (vx * fx + vy * fy) / (math.hypot(vx, vy) or 1)
        if dot > 0.15:
            out.append(n)
    return out


def _forces_at_center(forces: Dict[str, Any], form: str, h: int, v: int, f: int) -> List[Dict[str, Any]]:
    active = forces.get("active") or []
    reach = []
    shell = max(abs(h), abs(v), abs(f))
    for name in active:
        intensity = 0.5
        for fr in forces.get("forces") or []:
            if fr.get("type") == name or fr.get("name", "").lower() == name:
                intensity = float(fr.get("intensity") or 0.5)
        # simple falloff by shell
        present = intensity * max(0.15, 1.0 - shell * 0.08)
        reach.append({
            "force": name,
            "intensity": round(present, 3),
            "reaches": present > 0.2,
            "note": f"{name} field at shell {shell}",
        })
    weather = forces.get("weather")
    if weather:
        reach.append({"force": "weather", "intensity": 1.0, "reaches": True, "note": f"weather={weather}"})
    breath = forces.get("breath") or {}
    if breath:
        reach.append({
            "force": "breath",
            "intensity": 0.6,
            "reaches": True,
            "note": f"phase={breath.get('phase')} cycle={breath.get('cycle')}",
        })
    return reach


def move_fp(program, direction: str) -> Dict[str, Any]:
    """Move one centerpoint: forward|back|left|right|up|down."""
    view = first_person_view(program)
    walk = view["walk"]
    d = (direction or "forward").lower()
    if d not in walk:
        return {"ok": False, "reason": f"unknown direction {d}", "view": view}
    h, v, f = walk[d]
    program.avatar.body.pos = (h, v)
    program.center_f = f
    program.grid_snap = True
    if hasattr(program, "apply_grid_snap"):
        program.apply_grid_snap()
    if hasattr(program, "_push_user_trail"):
        program._push_user_trail()
    if hasattr(program, "note_seed"):
        program.note_seed(19, "Drive", f"fp_{d}")
    return {"ok": True, "center": [h, v, f], "direction": d, "view": first_person_view(program)}


def turn_fp(program, direction: str = "right") -> Dict[str, Any]:
    from form.avatar import Facing
    yaw = program.avatar.body.facing.name
    steps = 1 if direction in ("right", "r") else -1
    new_yaw = turn_yaw(yaw, steps)
    # map to Facing enum (only 8-way names)
    program.avatar.face(Facing[new_yaw])
    if hasattr(program, "note_seed"):
        program.note_seed(4, "Transform", f"fp_turn_{direction}")
    return {"ok": True, "yaw": new_yaw, "view": first_person_view(program)}


def look_fp(program, pitch: str = "level") -> Dict[str, Any]:
    p = (pitch or "level").lower()
    if p in ("u", "up", "sky"):
        p = "up"
    elif p in ("d", "down", "floor"):
        p = "down"
    else:
        p = "level"
    program.look_pitch = p
    if hasattr(program, "note_seed"):
        program.note_seed(9, "Show", f"fp_look_{p}")
    return {"ok": True, "pitch": p, "view": first_person_view(program)}


def goto_center(program, h: int, v: int, f: int = 0) -> Dict[str, Any]:
    program.avatar.body.pos = (int(h), int(v))
    program.center_f = int(f)
    if hasattr(program, "_push_user_trail"):
        program._push_user_trail()
    return {"ok": True, "center": [int(h), int(v), int(f)], "view": first_person_view(program)}


def smoke() -> bool:
    print("=== FIRST-PERSON MATRIX SMOKE ===")
    try:
        from form.open import open_program
        p = open_program("FPSmoke")
        p.place("a", "Alpha", words="here", detail="center data", goals=["see"], x=0, y=0)
        p.place("b", "Beta", words="north", x=0, y=1)
        p.center_f = 0
        p.look_pitch = "level"
        v = first_person_view(p)
        ok = v["mode"] == "first_person" and v["center"] == [0, 0, 0]
        print(f"[{'PASS' if ok else 'FAIL'}] at origin center")
        r = move_fp(p, "forward")
        ok2 = r["ok"] and r["center"][1] == 1
        print(f"[{'PASS' if ok2 else 'FAIL'}] move forward {r.get('center')}")
        turn_fp(p, "right")
        look_fp(p, "up")
        v2 = first_person_view(p)
        ok3 = v2["pitch"] == "up" and "faces" in v2
        print(f"[{'PASS' if ok3 else 'FAIL'}] look up + faces")
        return ok and ok2 and ok3
    except Exception as e:
        print("[FAIL]", e)
        return False


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
