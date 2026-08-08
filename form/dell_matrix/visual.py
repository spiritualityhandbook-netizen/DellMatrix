#!/usr/bin/env python3
"""Visual control panel — offline HTML UI. Shared actions · entities · pages · vision."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import html
import json
import math
import os
import sys

try:
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.dell_matrix.plane import Plane, Skin
    from form.dell_matrix.graph_view import build_view
    from form.dell_matrix.actions_registry import actions_for_mode
    from form.open import open_program
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.dell_matrix.plane import Plane, Skin
    from form.dell_matrix.graph_view import build_view
    from form.dell_matrix.actions_registry import actions_for_mode
    from form.open import open_program

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_OUT = os.path.join(os.path.dirname(__file__), "..", "state", "visual")
os.makedirs(_OUT, exist_ok=True)
EASY_UI = os.path.join(_ROOT, "DellMatrix_UI.html")
LEVEL = 8

_SKIN_COLOR = {
    "cube": "#5b8def", "sphere": "#7c5cbf", "seed": "#3cb371",
    "flower": "#e6a817", "building": "#c47c48", "words": "#888888", "circle": "#2aa7a0",
    "core": "#d97706",
}
_FORM_SKIN = {
    "cube": "cube", "sphere": "sphere", "core": "seed",
    "flower": "flower", "square": "cube", "circle": "circle",
}
_FACE_ANG = {
    "E": 0, "NE": 45, "N": 90, "NW": 135,
    "W": 180, "SW": 225, "S": 270, "SE": 315,
}


def _map_pos(x: float, y: float, scale: float = 70.0, cx: float = 360.0, cy: float = 260.0) -> Tuple[float, float]:
    return cx + x * scale, cy - y * scale


def _resolve_skin(unit_skin: str, form: str) -> str:
    if unit_skin and unit_skin not in ("cube", ""):
        return unit_skin
    return _FORM_SKIN.get(form, "cube")


def _agent_mark(
    parts: List[str], pos, facing: str, label: str, color: str, scale: float, cx: float, cy: float,
    *, posture: str = "stand", locomotion: str = "idle", holding: Any = None, sub: str = "",
) -> None:
    if not pos or len(pos) < 2:
        return
    x, y = _map_pos(float(pos[0]), float(pos[1]), scale=scale, cx=cx, cy=cy)
    r = 9.0
    if posture == "sit":
        r = 6.0
    elif posture == "jump":
        r = 10.0
    elif locomotion == "run":
        r = 11.0
    elif locomotion == "jog":
        r = 10.0
    parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{color}" stroke="#fff" stroke-width="2"/>')
    if locomotion == "run":
        parts.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r+4}" fill="none" stroke="{color}" opacity="0.35"/>'
        )
    parts.append(
        f'<text x="{x:.1f}" y="{y-r-6:.1f}" text-anchor="middle" fill="{color}" '
        f'font-family="system-ui,sans-serif" font-size="11" font-weight="600">{html.escape(label)}</text>'
    )
    if sub:
        parts.append(
            f'<text x="{x:.1f}" y="{y+r+12:.1f}" text-anchor="middle" fill="#9aa3b2" '
            f'font-family="system-ui,sans-serif" font-size="9">{html.escape(sub)}</text>'
        )
    if holding:
        parts.append(
            f'<circle cx="{x+r*0.7:.1f}" cy="{y-r*0.7:.1f}" r="3.5" fill="#fbbf24" stroke="#fff" stroke-width="1"/>'
        )
    # facing uses screen Y-up via cy - y*scale mapping
    ang = math.radians(-(_FACE_ANG.get(str(facing).upper(), 90)))
    x2, y2 = x + math.cos(ang) * 16, y + math.sin(ang) * 16
    parts.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="2.5"/>')


def _cone_svg(parts: List[str], cone: List, scale: float, cx: float, cy: float, color: str) -> None:
    if not cone or len(cone) < 3:
        return
    pts = []
    for p in cone:
        sx, sy = _map_pos(float(p[0]), float(p[1]), scale=scale, cx=cx, cy=cy)
        pts.append(f"{sx:.1f},{sy:.1f}")
    parts.append(
        f'<polygon points="{" ".join(pts)}" fill="{color}" opacity="0.12" stroke="{color}" '
        f'stroke-width="1" stroke-opacity="0.45"/>'
    )


def plane_to_svg(
    plane: Plane, *,
    scores: Optional[Dict[str, float]] = None,
    width: int = 720, height: int = 520,
    title: str = "Dell Matrix", form: str = "cube",
    avatar: Optional[Dict[str, Any]] = None,
    companion: Optional[Dict[str, Any]] = None,
    vision: Optional[Dict[str, Any]] = None,
    nursery: Optional[List[Dict[str, Any]]] = None,
    show_ghosts: bool = True,
    flower_pts: Optional[List[Dict[str, Any]]] = None,
    shell_rings: Optional[List[Dict[str, Any]]] = None,
) -> str:
    assert_floor_intact()
    scores = scores or {}
    view = build_view(plane, scores=scores)
    cx, cy = width / 2, height / 2
    scale = 70.0
    form_bg = {
        "flower": ("#12100a", "#e6a817"),
        "sphere": ("#0c0a14", "#7c5cbf"),
        "core": ("#14100a", "#d97706"),
        "circle": ("#0a1412", "#2aa7a0"),
    }.get(form, ("#0a1018", "#5b8def"))
    parts: List[str] = [
        f'<svg id="matrix-svg" xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<defs>",
        f'<radialGradient id="bgGlow" cx="50%" cy="45%" r="65%">'
        f'<stop offset="0%" stop-color="{form_bg[0]}"/><stop offset="100%" stop-color="#04060a"/></radialGradient>',
        '<filter id="softGlow" x="-40%" y="-40%" width="180%" height="180%">'
        '<feGaussianBlur stdDeviation="2.2" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
        '<linearGradient id="edgeVesica" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0%" stop-color="#6b4f9a"/><stop offset="100%" stop-color="#a78bfa"/></linearGradient>',
        "</defs>",
        f'<rect width="100%" height="100%" fill="url(#bgGlow)" rx="12"/>',
        # subtle grid
        f'<g opacity="0.35" stroke="{form_bg[1]}" stroke-width="0.6">',
    ]
    for gx in range(0, width + 1, 40):
        parts.append(f'<line x1="{gx}" y1="0" x2="{gx}" y2="{height}" opacity="0.15"/>')
    for gy in range(0, height + 1, 40):
        parts.append(f'<line x1="0" y1="{gy}" x2="{width}" y2="{gy}" opacity="0.15"/>')
    parts.append("</g>")
    # center axes
    parts.append(
        f'<line x1="0" y1="{cy}" x2="{width}" y2="{cy}" stroke="{form_bg[1]}" stroke-width="1" opacity="0.2"/>'
    )
    parts.append(
        f'<line x1="{cx}" y1="0" x2="{cx}" y2="{height}" stroke="{form_bg[1]}" stroke-width="1" opacity="0.2"/>'
    )
    parts.append(
        f'<text x="16" y="26" fill="#9aa3b2" font-family="system-ui,sans-serif" font-size="13">{html.escape(title)}</text>'
    )
    parts.append(
        f'<text x="16" y="44" fill="#5c6575" font-family="system-ui,sans-serif" font-size="11">'
        f'form={html.escape(form)} · Floor: {" · ".join(FLOOR)} · snapshot</text>'
    )
    # skin legend
    lx = 16
    ly = height - 16
    parts.append(f'<g font-family="system-ui,sans-serif" font-size="9" fill="#8b97ab">')
    for i, (sk, col) in enumerate(_SKIN_COLOR.items()):
        x = lx + (i % 8) * 88
        y = ly - (0 if i < 8 else 14)
        parts.append(f'<circle cx="{x}" cy="{y - 3}" r="4" fill="{col}"/>')
        parts.append(f'<text x="{x + 8}" y="{y}">{sk}</text>')
    parts.append("</g>")

    # form grammar: shell rings / flower centers
    if shell_rings:
        for ring in shell_rings:
            r = float(ring.get("radius", 1)) * scale
            stroke = "#3d5a80" if form in ("core", "sphere") else "#2a4a3a"
            parts.append(
                f'<circle cx="{cx}" cy="{cy}" r="{r:.1f}" fill="none" stroke="{stroke}" '
                f'stroke-width="1" opacity="0.45" stroke-dasharray="4 3"/>'
            )
    if flower_pts:
        # equal-radius FoL circles (radius ~ scale units)
        fr = 0.95 * scale
        for pt in flower_pts:
            fx, fy = _map_pos(float(pt["x"]), float(pt["y"]), scale=scale, cx=cx, cy=cy)
            parts.append(
                f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="{fr:.1f}" fill="none" '
                f'stroke="#e6a817" opacity="0.28" stroke-width="1.2"/>'
            )
            parts.append(f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="3" fill="#e6a817" opacity="0.45"/>')

    if vision and vision.get("cone"):
        _cone_svg(parts, vision["cone"], scale, cx, cy, "#38bdf8")

    pos: Dict[str, Tuple[float, float]] = {}
    for n in view.nodes:
        pos[n.id] = _map_pos(n.x, n.y, scale=scale, cx=cx, cy=cy)

    for e in view.edges:
        if e.source not in pos or e.target not in pos:
            continue
        x1, y1 = pos[e.source]
        x2, y2 = pos[e.target]
        color = {"enhance": "#3d5a80", "vesica": "#6b4f9a", "sandbox": "#664422"}.get(e.kind, "#333")
        dash = ' stroke-dasharray="4 4"' if e.kind == "sandbox" else ""
        parts.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="1.5"{dash} opacity="0.7"/>'
        )

    in_view = set(str(i) for i in ((vision or {}).get("in_view_ids") or []))
    prefer = set()
    persona = (vision or {}).get("persona") or {}
    for sk in persona.get("prefer_skins") or []:
        prefer.add(str(sk))
    zoom_id = str((vision or {}).get("zoom_id") or "")  # optional
    # also accept plane zoom via nodes metadata later
    for n in view.nodes:
        x, y = pos[n.id]
        skin = _resolve_skin(n.skin, form)
        color = _SKIN_COLOR.get(skin, "#5b8def")
        sc = float(scores.get(n.id, 0.0) or 0.0)
        # size-by-score: louder ideas read larger
        r = max(12.0, min(28.0, 16.0 + sc * 3.5))
        is_in = str(n.id) in in_view
        is_pref = is_in and bool(prefer) and skin in prefer
        if is_pref:
            glow = ' stroke="#e6a817" stroke-width="2.5" stroke-dasharray="3 2" filter="url(#softGlow)"'
        elif is_in:
            glow = ' stroke="#fff" stroke-width="2.5" filter="url(#softGlow)"'
        else:
            glow = ""
        # per-node gradient for spherical skins
        gid = f"ng{html.escape(n.id).replace(' ', '_')}"
        parts.append(
            f'<radialGradient id="{gid}" cx="35%" cy="30%" r="70%">'
            f'<stop offset="0%" stop-color="#ffffff" stop-opacity="0.45"/>'
            f'<stop offset="45%" stop-color="{color}"/>'
            f'<stop offset="100%" stop-color="#000000" stop-opacity="0.35"/></radialGradient>'
        )
        fill = f"url(#{gid})" if skin in ("sphere", "circle", "seed", "flower", "core") else color
        parts.append(f'<g class="node" data-id="{html.escape(n.id)}" style="cursor:pointer">')
        if skin == "flower":
            for k in range(6):
                ang = math.radians(60 * k)
                px = x + math.cos(ang) * r * 0.55
                py = y + math.sin(ang) * r * 0.55
                parts.append(
                    f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r * 0.42:.1f}" fill="{color}" opacity="0.5"/>'
                )
            parts.append(
                f'<circle class="node-shape" cx="{x:.1f}" cy="{y:.1f}" r="{r * 0.55:.1f}" '
                f'fill="{fill}" opacity="0.95"{glow}/>'
            )
        elif skin in ("sphere", "circle", "seed", "core"):
            parts.append(
                f'<circle class="node-shape" cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" opacity="0.95"{glow}/>'
            )
        elif skin == "building":
            parts.append(
                f'<rect class="node-shape" x="{x-r:.1f}" y="{y-r*1.2:.1f}" width="{2*r}" height="{2.4*r}" '
                f'fill="{color}" rx="2" opacity="0.92"{glow}/>'
            )
            # windows
            for wi in range(2):
                for wj in range(3):
                    wx = x - r * 0.45 + wi * r * 0.55
                    wy = y - r * 0.7 + wj * r * 0.55
                    parts.append(
                        f'<rect x="{wx:.1f}" y="{wy:.1f}" width="{r*0.25:.1f}" height="{r*0.28:.1f}" '
                        f'fill="#0f1115" opacity="0.35"/>'
                    )
        elif skin == "words":
            parts.append(
                f'<rect class="node-shape" x="{x-r*0.75:.1f}" y="{y-r:.1f}" width="{1.5*r}" height="{2*r}" '
                f'fill="{color}" rx="2" opacity="0.92"{glow}/>'
            )
            for li, dy in enumerate((-0.45, -0.1, 0.25)):
                parts.append(
                    f'<line x1="{x-r*0.45:.1f}" y1="{y+r*dy:.1f}" x2="{x+r*0.45:.1f}" y2="{y+r*dy:.1f}" '
                    f'stroke="#0f1115" stroke-width="1.2" opacity="0.45"/>'
                )
        else:
            parts.append(
                f'<rect class="node-shape" x="{x-r:.1f}" y="{y-r:.1f}" width="{2*r}" height="{2*r}" '
                f'fill="{color}" rx="4" opacity="0.92"{glow}/>'
            )
        parts.append(
            f'<text x="{x:.1f}" y="{y+r+14:.1f}" text-anchor="middle" fill="#e8eaed" '
            f'font-family="system-ui,sans-serif" font-size="12">{html.escape(n.label[:16])}</text>'
        )
        if sc and sc > 0:
            parts.append(
                f'<text x="{x:.1f}" y="{y+4:.1f}" text-anchor="middle" fill="#0f1115" '
                f'font-family="system-ui,sans-serif" font-size="10" font-weight="600">{sc:.1f}</text>'
            )
        parts.append("</g>")

    # nursery ghosts
    if show_ghosts and nursery:
        for i, prop in enumerate(nursery[:8]):
            gx = cx + (i - 3.5) * 40
            gy = height - 48
            parts.append(
                f'<circle cx="{gx:.1f}" cy="{gy:.1f}" r="10" fill="none" stroke="#3cb371" '
                f'stroke-dasharray="3 3" opacity="0.55"/>'
            )
            parts.append(
                f'<text x="{gx:.1f}" y="{gy+22:.1f}" text-anchor="middle" fill="#5c6575" '
                f'font-size="9" font-family="system-ui,sans-serif">{html.escape((prop.get("label") or "?")[:8])}</text>'
            )

    if not view.nodes and not (nursery or []):
        parts.append(
            f'<text x="{cx}" y="{cy - 10}" text-anchor="middle" fill="#9aa3b2" '
            f'font-family="system-ui,sans-serif" font-size="15">No ideas yet</text>'
        )
        parts.append(
            f'<text x="{cx}" y="{cy + 14}" text-anchor="middle" fill="#5c6575" '
            f'font-family="system-ui,sans-serif" font-size="13">Try: create an idea called test · or type live</text>'
        )

    # YOU + AI on map (posture / loco / holding)
    if avatar:
        body = avatar.get("body") or avatar
        pos_a = avatar.get("pos") or body.get("pos") or [0, 0]
        facing = avatar.get("facing") or body.get("facing") or "N"
        face = avatar.get("look") or ""
        posture = avatar.get("posture") or body.get("posture") or "stand"
        loco = avatar.get("locomotion") or body.get("locomotion") or "idle"
        holding = avatar.get("holding") or body.get("holding")
        sub = f"{posture} · {loco}"
        _agent_mark(
            parts, pos_a, facing, f"YOU {face}".strip(), "#38bdf8", scale, cx, cy,
            posture=str(posture), locomotion=str(loco), holding=holding, sub=sub,
        )
    if companion:
        doing = companion.get("doing") or companion.get("mode") or ""
        _agent_mark(
            parts, companion.get("pos"), companion.get("facing") or "N",
            companion.get("label") or "AI", "#e879f9", scale, cx, cy,
            sub=str(doing),
        )

    parts.append("</svg>")
    return "\n".join(parts)


def _nodes_payload(plane: Plane, scores: Optional[Dict[str, float]] = None) -> List[Dict[str, Any]]:
    scores = scores or {}
    out = []
    for uid, u in plane.units.items():
        out.append({
            "id": uid, "label": u.label, "words": u.words,
            "detail": getattr(u, "detail", "") or "",
            "goals": list(getattr(u, "goals", []) or []),
            "skin": u.skin.value,
            "x": u.x, "y": u.y, "sandboxed": u.sandboxed,
            "score": float(scores.get(uid, 0.0)),
        })
    return out


def plane_to_html(
    plane: Plane, *,
    scores: Optional[Dict[str, float]] = None,
    title: str = "Dell Matrix", owner: str = "Operator",
    avatar: Optional[Dict[str, Any]] = None,
    nursery: Optional[List[Dict[str, Any]]] = None,
    rings: Optional[List[str]] = None,
    form: str = "cube", skin: str = "cube",
    companion: Optional[Dict[str, Any]] = None,
    ux_mode: str = "builder",
    page: Optional[Dict[str, Any]] = None,
    vision: Optional[Dict[str, Any]] = None,
    flower_pts: Optional[List] = None,
    shell_rings: Optional[List] = None,
    show_ghosts: bool = True,
) -> str:
    svg = plane_to_svg(
        plane, scores=scores, title=title, form=form,
        avatar=avatar, companion=companion, vision=vision,
        nursery=nursery, show_ghosts=show_ghosts,
        flower_pts=flower_pts, shell_rings=shell_rings,
    )
    nodes = json.dumps(_nodes_payload(plane, scores))
    actions = json.dumps(actions_for_mode(ux_mode))
    nursery = nursery or []
    avatar = avatar or {}
    companion = companion or {}
    rings = rings or ["Seed", "Token", "Body", "Lens", "Evolve"]
    nursery_json = json.dumps(nursery)
    avatar_json = json.dumps(avatar)
    companion_json = json.dumps(companion)
    page_json = json.dumps(page or {})
    vision_json = json.dumps(vision or {})
    rings_s = " → ".join(rings)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{html.escape(title)}</title>
<style>
  :root {{ color-scheme: dark; --bg:#0a0b0e; --card:#151820; --line:#2a2f3a; --text:#e8eaed; --muted:#9aa3b2; --accent:#5b8def; --ok:#3cb371; --ai:#e879f9; --user:#38bdf8; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--text); font-family:system-ui,-apple-system,sans-serif; line-height:1.45; }}
  header {{ padding:16px 18px; border-bottom:1px solid var(--line); display:flex; flex-wrap:wrap; gap:12px; align-items:center; justify-content:space-between; }}
  header h1 {{ margin:0; font-size:18px; font-weight:600; }}
  header .meta {{ color:var(--muted); font-size:12px; }}
  .layout {{ display:grid; grid-template-columns: 280px 1fr 280px; gap:16px; padding:16px; max-width:1400px; margin:0 auto; }}
  @media (max-width: 1000px) {{ .layout {{ grid-template-columns: 1fr; padding:12px; gap:12px; }} }}
  .card {{ background:var(--card); border:1px solid var(--line); border-radius:14px; padding:16px; }}
  .card h2 {{ margin:0 0 12px; font-size:13px; color:var(--muted); font-weight:600; text-transform:uppercase; letter-spacing:.04em; }}
  .group {{ margin-bottom:16px; }}
  .group-title {{ font-size:12px; color:var(--muted); margin-bottom:8px; }}
  .btn-row {{ display:flex; flex-wrap:wrap; gap:8px; }}
  button.action {{ background:#1c2230; color:var(--text); border:1px solid var(--line); border-radius:10px; padding:10px 12px; font-size:13px; cursor:pointer; min-height:40px; }}
  button.action:hover {{ border-color:var(--accent); background:#222a3a; }}
  button.live {{ background:#1a3a2a; border-color:var(--ok); }}
  #cmd-box {{ margin-top:14px; padding:14px; background:#0f1115; border-radius:10px; border:1px dashed var(--line); min-height:72px; }}
  #cmd-box .label {{ font-size:11px; color:var(--muted); margin-bottom:6px; }}
  #cmd-text {{ font-size:15px; font-family:ui-monospace,monospace; color:#7dd3a0; word-break:break-word; }}
  #cmd-hint {{ font-size:12px; color:var(--muted); margin-top:8px; }}
  .copy-btn {{ margin-top:10px; background:var(--accent); color:#fff; border:none; border-radius:8px; padding:8px 14px; font-size:13px; cursor:pointer; min-height:36px; }}
  .node-shape:hover {{ filter:brightness(1.15); stroke:#fff; stroke-width:2; }}
  .node.active .node-shape {{ stroke:#fff; stroke-width:2.5; }}
  #detail .k {{ color:var(--muted); font-size:11px; margin-top:8px; }}
  #detail .v {{ font-size:13px; word-break:break-word; }}
  .proposal {{ border:1px solid var(--line); border-radius:10px; padding:10px 12px; margin-bottom:10px; font-size:13px; }}
  .proposal .kind {{ color:var(--ok); font-size:11px; }}
  .proposal .aff {{ color:var(--accent); font-size:11px; font-weight:600; }}
  .avatar-line {{ font-size:14px; margin-bottom:6px; }}
  .empty {{ color:var(--muted); font-size:13px; }}
  .credit {{ font-size:11px; color:#5c6575; margin-top:12px; line-height:1.5; }}
  .page-card {{ border:1px solid var(--accent); border-radius:10px; padding:10px; margin-top:10px; font-size:12px; }}
  .seen {{ font-size:12px; border:1px solid var(--line); border-radius:8px; padding:6px; margin-bottom:4px; }}
</style>
</head>
<body>
<header>
  <div>
    <h1>{html.escape(title)}</h1>
    <div class="meta">owner={html.escape(owner)} · ideas={len(plane.units)} · form={html.escape(form)} · skin={html.escape(skin)} · mode={html.escape(ux_mode)} · rings: {html.escape(rings_s)}</div>
  </div>
  <div class="meta">Offline snapshot · copy a command · paste at you&gt; · for live: type <b>live</b></div>
</header>
<div class="layout">
  <section class="card" id="controls">
    <h2>Actions</h2>
    <div id="btn-root"></div>
    <div id="cmd-box">
      <div class="label">Copy, then paste into the program window (you&gt;)</div>
      <div id="cmd-text">(tap a button)</div>
      <div id="cmd-hint"></div>
      <button class="copy-btn" id="copy-btn" type="button">Copy command</button>
    </div>
    <div class="credit">
      This panel is a <b>snapshot</b> (not live). Commands run in the program window.
      Type <b>live</b> for two-way localhost visual. Growth stays in Nursery until confirm.
    </div>
  </section>
  <section class="card" style="overflow:auto">
    <h2>Matrix snapshot</h2>
    {svg}
    <div id="detail" style="margin-top:14px">
      <h2 style="margin-top:0">Selected idea (inspect)</h2>
      <div class="k">label</div><div class="v" id="p-title">—</div>
      <div class="k">id</div><div class="v" id="p-id">—</div>
      <div class="k">score · skin</div><div class="v" id="p-score">—</div>
      <div class="k">detail</div><div class="v" id="p-detail">—</div>
      <div class="k">goals</div><div class="v" id="p-goals">—</div>
      <div class="k">words</div><div class="v" id="p-words">—</div>
      <div class="k">page cmd</div><div class="v" id="p-page">zoom &lt;id&gt;</div>
    </div>
    <div id="page-box"></div>
  </section>
  <section class="card">
    <h2>Avatar · YOU</h2>
    <div id="avatar-box" class="avatar-line empty">—</div>
    <h2 style="margin-top:14px">AI companion</h2>
    <div id="ai-box" class="avatar-line empty">—</div>
    <h2 style="margin-top:14px">Vision (last look)</h2>
    <div id="vision-box" class="empty">Type look in the program</div>
    <h2 style="margin-top:18px">Nursery (ranked)</h2>
    <div id="nursery-box" class="empty">No pending proposals</div>
  </section>
</div>
<script>
const NODES = {nodes};
const ACTIONS = {actions};
const NURSERY = {nursery_json};
const AVATAR = {avatar_json};
const COMPANION = {companion_json};
const PAGE = {page_json};
const VISION = {vision_json};
const byId = Object.fromEntries(NODES.map(n => [n.id, n]));
const root = document.getElementById('btn-root');
ACTIONS.forEach(g => {{
  const wrap = document.createElement('div');
  wrap.className = 'group';
  wrap.innerHTML = '<div class="group-title">' + g.group + '</div>';
  const row = document.createElement('div');
  row.className = 'btn-row';
  g.items.forEach(item => {{
    const b = document.createElement('button');
    b.type = 'button'; b.className = 'action' + (item.cmd === 'live' ? ' live' : '');
    b.textContent = item.label;
    b.addEventListener('click', () => {{
      document.getElementById('cmd-text').textContent = item.cmd;
      document.getElementById('cmd-hint').textContent = item.hint || 'Paste into the program window';
      window._lastCmd = item.cmd;
    }});
    row.appendChild(b);
  }});
  wrap.appendChild(row); root.appendChild(wrap);
}});
document.getElementById('copy-btn').addEventListener('click', async () => {{
  const t = window._lastCmd || '';
  if (!t) {{
    document.getElementById('cmd-hint').textContent = 'Tap a button first';
    return;
  }}
  try {{
    await navigator.clipboard.writeText(t);
    document.getElementById('cmd-hint').textContent = 'Copied — paste into the program window (you>)';
  }} catch (e) {{
    document.getElementById('cmd-hint').textContent = 'Select the green text above and copy it';
  }}
}});
function showNode(id) {{
  const n = byId[id]; if (!n) return;
  document.querySelectorAll('.node').forEach(g => g.classList.remove('active'));
  const g = document.querySelector('.node[data-id="'+id+'"]');
  if (g) g.classList.add('active');
  document.getElementById('p-title').textContent = n.label;
  document.getElementById('p-id').textContent = n.id;
  document.getElementById('p-score').textContent = (n.score || 0).toFixed(2) + ' · ' + (n.skin || '');
  document.getElementById('p-detail').textContent = n.detail || '(none)';
  document.getElementById('p-goals').textContent = (n.goals && n.goals.length) ? n.goals.join(' · ') : '(none)';
  document.getElementById('p-words').textContent = n.words || '(empty)';
  document.getElementById('p-page').textContent = 'zoom ' + n.id;
  window._lastCmd = 'zoom ' + n.id;
  document.getElementById('cmd-text').textContent = 'zoom ' + n.id;
  document.getElementById('cmd-hint').textContent = 'Inspect page — paste to zoom in program';
}}
document.querySelectorAll('.node').forEach(g => g.addEventListener('click', () => showNode(g.getAttribute('data-id'))));
(function(){{
  const box = document.getElementById('avatar-box');
  if (AVATAR && (AVATAR.look || AVATAR.describe)) {{
    box.className = 'avatar-line';
    const pos = AVATAR.pos || (AVATAR.body && AVATAR.body.pos) || '?';
    const face = AVATAR.facing || (AVATAR.body && AVATAR.body.facing) || '?';
    box.textContent = (AVATAR.look || '') + '  ' + (AVATAR.describe || '') + ' · map @ ' + JSON.stringify(pos) + ' face ' + face;
  }}
}})();
(function(){{
  const box = document.getElementById('ai-box');
  if (COMPANION && COMPANION.pos) {{
    box.className = 'avatar-line';
    box.textContent = (COMPANION.name || 'AI') + ' @ ' + JSON.stringify(COMPANION.pos) + ' face ' + (COMPANION.facing||'?') + ' mode=' + (COMPANION.mode||'manual') + ' · ' + (COMPANION.doing||'');
  }} else {{
    box.textContent = 'AI companion not placed (loads with session)';
  }}
}})();
(function(){{
  const box = document.getElementById('vision-box');
  if (VISION && VISION.pattern) {{
    box.className = '';
    const p = VISION.pattern;
    let html = '<div class="seen">face ' + (VISION.facing||'?') + ' · see ' + (p.count||0) + ' · near ' + (p.nearest||'—') + '</div>';
    (VISION.nodes||[]).forEach(n => {{
      html += '<div class="seen"><b>' + (n.label||'') + '</b> ' + (n.skin||'') + ' d=' + n.dist + '</div>';
    }});
    if (!(VISION.nodes||[]).length) html += '<div class="empty">Nothing in view</div>';
    box.innerHTML = html;
  }}
}})();
(function(){{
  const box = document.getElementById('page-box');
  if (PAGE && PAGE.ok) {{
    box.innerHTML = '<div class="page-card"><b>Open page:</b> ' + (PAGE.label||'') +
      '<br>skin ' + (PAGE.skin||'') + ' shell ' + (PAGE.shell??'—') +
      '<br>' + (PAGE.detail||PAGE.words||'') +
      '<br>neighbors: ' + ((PAGE.neighbors||[]).join(', ')||'—') +
      '<br><span style="color:var(--muted)">unzoom to leave</span></div>';
  }}
}})();
(function(){{
  const box = document.getElementById('nursery-box');
  if (!NURSERY || !NURSERY.length) return;
  box.className = ''; box.innerHTML = '';
  NURSERY.slice(0, 12).forEach(p => {{
    const d = document.createElement('div');
    d.className = 'proposal';
    const aff = (typeof p.affinity === 'number') ? p.affinity.toFixed(3) : '—';
    d.innerHTML = '<div class="kind">' + (p.kind || '') + ' · ' + (p.id || '') + '</div>'
      + '<div class="aff">aff ' + aff + '</div>'
      + '<div>' + (p.label || '') + '</div>'
      + '<div style="color:var(--muted);font-size:11px;margin-top:4px">confirm ' + (p.id || '') + '</div>';
    box.appendChild(d);
  }});
}})();
</script>
</body>
</html>
"""


def write_visual(
    plane: Plane,
    owner: str = "Operator",
    scores: Optional[Dict[str, float]] = None,
    avatar: Optional[Dict[str, Any]] = None,
    nursery: Optional[List[Dict[str, Any]]] = None,
    rings: Optional[List[str]] = None,
    form: str = "cube",
    skin: str = "cube",
    companion: Optional[Dict[str, Any]] = None,
    ux_mode: str = "builder",
    page: Optional[Dict[str, Any]] = None,
    vision: Optional[Dict[str, Any]] = None,
    program: Any = None,
) -> Dict[str, str]:
    base = os.path.join(_OUT, f"matrix_{owner}")
    svg_path = base + ".svg"
    html_path = base + ".html"
    title = f"Dell Matrix · {owner}"
    flower_pts = program.flower_draw_data() if program and hasattr(program, "flower_draw_data") else None
    shell_rings = program.shell_rings_data() if program and hasattr(program, "shell_rings_data") else None
    show_ghosts = True
    if program and hasattr(program, "show_nursery_ghosts"):
        show_ghosts = bool(program.show_nursery_ghosts)
    svg = plane_to_svg(
        plane, scores=scores, title=title, form=form,
        avatar=avatar, companion=companion, vision=vision,
        nursery=nursery, show_ghosts=show_ghosts,
        flower_pts=flower_pts, shell_rings=shell_rings,
    )
    doc = plane_to_html(
        plane, scores=scores, title=title, owner=owner,
        avatar=avatar, nursery=nursery, rings=rings,
        form=form, skin=skin, companion=companion, ux_mode=ux_mode,
        page=page, vision=vision, flower_pts=flower_pts,
        shell_rings=shell_rings, show_ghosts=show_ghosts,
    )
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(doc)
    with open(EASY_UI, "w", encoding="utf-8") as f:
        f.write(doc)
    return {
        "svg": svg_path, "html": html_path, "easy": EASY_UI,
        "level": str(LEVEL), "form": form, "skin": skin, "interactive": "true",
        "mode": ux_mode,
    }


def smoke() -> bool:
    print("=== VISUAL UI SMOKE ===")
    r = []
    def rec(name, ok, detail=""):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" | {detail}" if detail else ""))
        r.append(bool(ok))
    p = open_program("VisUI")
    p.place("biz", "Business", words="crm", skin=Skin.BUILDING, x=1)
    p.lattice.to_sphere()
    paths = write_visual(
        p.cube.session.plane, owner="VisUI",
        avatar=p.avatar_status(), rings=list(p.duo.rings),
        form=p.lattice.perception.form.value,
        skin=p.lattice.perception.skin_name(),
        nursery=p.ranked_proposals(),
        companion=p.companion.to_dict(),
        ux_mode=p.ux_mode,
        vision=p.look_around(),
        program=p,
    )
    rec("html", os.path.isfile(paths["html"]))
    rec("easy path", os.path.isfile(paths.get("easy", "")))
    txt = open(paths["html"], encoding="utf-8").read()
    rec("live CTA", "live" in txt.lower() and "Live panel" in txt)
    rec("snapshot wording", "Matrix snapshot" in txt or "snapshot" in txt.lower())
    rec("YOU on map", "YOU" in txt)
    rec("AI companion", "AI" in txt or "companion" in txt.lower())
    rec("copy hint", "paste into the program" in txt.lower())
    p2 = open_program("VisEmpty")
    p2.cube.session.plane.units.clear()
    paths2 = write_visual(p2.cube.session.plane, owner="VisEmpty", program=p2)
    empty_txt = open(paths2["html"], encoding="utf-8").read()
    rec("empty state", "No ideas yet" in empty_txt)
    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


def main() -> None:
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    p = open_program("Demo")
    print(write_visual(
        p.cube.session.plane, owner="Demo",
        avatar=p.avatar_status(), rings=list(p.duo.rings),
        form=p.lattice.perception.form.value,
        skin=p.lattice.perception.skin_name(),
        companion=p.companion.to_dict(), program=p,
    ))


if __name__ == "__main__":
    main()
