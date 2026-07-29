#!/usr/bin/env python3
"""
Visual surface L3 — SVG + HTML from Dell Matrix plane.

09[Show] > 15[Map] >> 47[Embed] :: Visual

Not a game engine. Real openable visual:
- SVG graph of units / edges / sandboxes
- HTML wrapper you can open in a browser

Run:
  python -m form.dell_matrix.visual --smoke
  python -m form.dell_matrix.visual --demo
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import html
import os
import sys

try:
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.dell_matrix.plane import Plane, Perspective, Skin
    from form.dell_matrix.graph_view import build_view, GraphView
    from form.dell_matrix.blank_cube import give
    from form.open import open_program
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.dell_matrix.plane import Plane, Perspective, Skin
    from form.dell_matrix.graph_view import build_view, GraphView
    from form.dell_matrix.blank_cube import give
    from form.open import open_program

_OUT = os.path.join(os.path.dirname(__file__), "..", "state", "visual")
os.makedirs(_OUT, exist_ok=True)

LEVEL = 3

_SKIN_COLOR = {
    "cube": "#5b8def",
    "sphere": "#7c5cbf",
    "seed": "#3cb371",
    "flower": "#e6a817",
    "building": "#c47c48",
    "words": "#888888",
    "circle": "#2aa7a0",
}


def _map_pos(x: float, y: float, scale: float = 80.0, cx: float = 400.0, cy: float = 300.0) -> Tuple[float, float]:
    return cx + x * scale, cy - y * scale


def plane_to_svg(
    plane: Plane,
    *,
    scores: Optional[Dict[str, float]] = None,
    width: int = 800,
    height: int = 600,
    title: str = "Dell Matrix",
) -> str:
    assert_floor_intact()
    scores = scores or {}
    view = build_view(plane)
    cx, cy = width / 2, height / 2

    parts: List[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="100%" height="100%" fill="#0f1115"/>',
        f'<text x="16" y="28" fill="#9aa3b2" font-family="system-ui,sans-serif" font-size="14">{html.escape(title)} · {plane.perspective.value} · L{LEVEL}</text>',
        f'<text x="16" y="48" fill="#5c6575" font-family="system-ui,sans-serif" font-size="11">Floor: {" · ".join(FLOOR)}</text>',
    ]

    # edges first
    pos: Dict[str, Tuple[float, float]] = {}
    for n in view.nodes:
        pos[n.id] = _map_pos(n.x, n.y, cx=cx, cy=cy)

    for e in view.edges:
        if e.source not in pos or e.target not in pos:
            # sandbox id edges skip
            continue
        x1, y1 = pos[e.source]
        x2, y2 = pos[e.target]
        color = {"enhance": "#3d5a80", "vesica": "#6b4f9a", "sandbox": "#664422"}.get(e.kind, "#333")
        dash = ' stroke-dasharray="4 4"' if e.kind == "sandbox" else ""
        parts.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="1.5"{dash} opacity="0.7"/>'
        )

    # sandbox rings
    for sid, members in view.sandboxes.items():
        if not members:
            continue
        xs = [pos[m][0] for m in members if m in pos]
        ys = [pos[m][1] for m in members if m in pos]
        if not xs:
            continue
        minx, maxx = min(xs) - 36, max(xs) + 36
        miny, maxy = min(ys) - 36, max(ys) + 36
        parts.append(
            f'<rect x="{minx:.1f}" y="{miny:.1f}" width="{maxx-minx:.1f}" height="{maxy-miny:.1f}" '
            f'fill="none" stroke="#a67c52" stroke-width="1.5" stroke-dasharray="6 4" rx="12" opacity="0.8"/>'
        )
        parts.append(
            f'<text x="{minx:.1f}" y="{miny-6:.1f}" fill="#a67c52" font-size="10" font-family="system-ui,sans-serif">box:{html.escape(sid)}</text>'
        )

    # nodes
    for n in view.nodes:
        x, y = pos[n.id]
        color = _SKIN_COLOR.get(n.skin, "#5b8def")
        r = 18 if n.skin != "building" else 16
        if n.skin in ("sphere", "circle", "seed", "flower"):
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{color}" opacity="0.9"/>')
        else:
            parts.append(
                f'<rect x="{x-r:.1f}" y="{y-r:.1f}" width="{2*r}" height="{2*r}" fill="{color}" rx="4" opacity="0.9"/>'
            )
        label = html.escape(n.label[:18])
        parts.append(
            f'<text x="{x:.1f}" y="{y+r+14:.1f}" text-anchor="middle" fill="#e8eaed" '
            f'font-family="system-ui,sans-serif" font-size="12">{label}</text>'
        )
        sc = scores.get(n.id)
        if sc is not None and sc > 0:
            parts.append(
                f'<text x="{x:.1f}" y="{y+4:.1f}" text-anchor="middle" fill="#0f1115" '
                f'font-family="system-ui,sans-serif" font-size="10" font-weight="600">{sc:.1f}</text>'
            )

    parts.append("</svg>")
    return "\n".join(parts)


def plane_to_html(
    plane: Plane,
    *,
    scores: Optional[Dict[str, float]] = None,
    title: str = "Dell Matrix",
) -> str:
    svg = plane_to_svg(plane, scores=scores, title=title)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{html.escape(title)}</title>
<style>
  body {{ margin:0; background:#0a0b0e; color:#e8eaed; font-family:system-ui,sans-serif; }}
  header {{ padding:12px 16px; border-bottom:1px solid #222; }}
  main {{ display:flex; justify-content:center; padding:16px; }}
  .meta {{ color:#9aa3b2; font-size:13px; }}
</style>
</head>
<body>
<header>
  <strong>{html.escape(title)}</strong>
  <div class="meta">perspective={html.escape(plane.perspective.value)} · units={len(plane.units)} · Floor locked</div>
</header>
<main>
{svg}
</main>
</body>
</html>
"""


def write_visual(
    plane: Plane,
    owner: str = "Operator",
    scores: Optional[Dict[str, float]] = None,
) -> Dict[str, str]:
    base = os.path.join(_OUT, f"matrix_{owner}")
    svg_path = base + ".svg"
    html_path = base + ".html"
    svg = plane_to_svg(plane, scores=scores, title=f"Dell Matrix · {owner}")
    doc = plane_to_html(plane, scores=scores, title=f"Dell Matrix · {owner}")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(doc)
    return {"svg": svg_path, "html": html_path, "level": str(LEVEL)}


def smoke() -> bool:
    print("=== VISUAL L3 SMOKE ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{len(r)+1}] {name}: {'PASS' if ok else 'FAIL'}" + (f" | {detail}" if detail else ""))
        r.append(bool(ok))

    p = open_program("VisualL3")
    p.place("biz", "Business", words="CRM", skin=Skin.BUILDING, x=1)
    p.place("music", "Music", words="Ep4", skin=Skin.SEED, x=-1)
    p.place("cube1", "HarmonicCube", skin=Skin.CUBE, y=1)
    p.box(["cube1"], "sandbox_A")
    p.enhance_on()
    p.pulse()
    paths = write_visual(p.cube.session.plane, owner="VisualL3", scores=p.scores())
    rec("svg file", os.path.isfile(paths["svg"]), paths["svg"])
    rec("html file", os.path.isfile(paths["html"]), paths["html"])
    with open(paths["svg"], encoding="utf-8") as f:
        svg = f.read()
    rec("svg has nodes", "Business" in svg and "Music" in svg)
    rec("svg has box", "sandbox_A" in svg or "box:" in svg)
    rec("html wraps svg", "<svg" in open(paths["html"], encoding="utf-8").read())
    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


def demo() -> None:
    print("09[Show] > 15[Map] >> 47[Embed] :: Visual L3")
    p = open_program("Demo")
    p.place("biz", "Business", skin=Skin.BUILDING, x=1)
    p.place("music", "Music", skin=Skin.SEED, x=-1)
    paths = write_visual(p.cube.session.plane, owner="Demo")
    print(paths)


def main() -> None:
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    demo()


if __name__ == "__main__":
    main()
