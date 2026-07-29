#!/usr/bin/env python3
"""
Visual surface L3 + interactive HTML.

09[Show] > 15[Map] >> 47[Embed] :: Visual

SVG graph + offline HTML with:
- click unit → detail panel (label, skin, words, score, sandbox)
- hover highlight
- perspective / unit count meta

Run:
  python -m form.dell_matrix.visual --smoke
  python -m form.dell_matrix.visual --demo
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import html
import json
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
        f'<svg id="matrix-svg" xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="100%" height="100%" fill="#0f1115"/>',
        f'<text x="16" y="28" fill="#9aa3b2" font-family="system-ui,sans-serif" font-size="14">{html.escape(title)} · {plane.perspective.value} · L{LEVEL}</text>',
        f'<text x="16" y="48" fill="#5c6575" font-family="system-ui,sans-serif" font-size="11">Floor: {" · ".join(FLOOR)} · click a node</text>',
    ]

    pos: Dict[str, Tuple[float, float]] = {}
    for n in view.nodes:
        pos[n.id] = _map_pos(n.x, n.y, cx=cx, cy=cy)

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

    for n in view.nodes:
        x, y = pos[n.id]
        color = _SKIN_COLOR.get(n.skin, "#5b8def")
        r = 18 if n.skin != "building" else 16
        sc = scores.get(n.id, 0.0)
        # clickable group
        parts.append(f'<g class="node" data-id="{html.escape(n.id)}" style="cursor:pointer">')
        if n.skin in ("sphere", "circle", "seed", "flower"):
            parts.append(
                f'<circle class="node-shape" cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{color}" opacity="0.9"/>'
            )
        else:
            parts.append(
                f'<rect class="node-shape" x="{x-r:.1f}" y="{y-r:.1f}" width="{2*r}" height="{2*r}" fill="{color}" rx="4" opacity="0.9"/>'
            )
        label = html.escape(n.label[:18])
        parts.append(
            f'<text x="{x:.1f}" y="{y+r+14:.1f}" text-anchor="middle" fill="#e8eaed" '
            f'font-family="system-ui,sans-serif" font-size="12">{label}</text>'
        )
        if sc and sc > 0:
            parts.append(
                f'<text x="{x:.1f}" y="{y+4:.1f}" text-anchor="middle" fill="#0f1115" '
                f'font-family="system-ui,sans-serif" font-size="10" font-weight="600">{sc:.1f}</text>'
            )
        parts.append("</g>")

    parts.append("</svg>")
    return "\n".join(parts)


def _nodes_payload(plane: Plane, scores: Optional[Dict[str, float]] = None) -> List[Dict[str, Any]]:
    scores = scores or {}
    out = []
    for uid, u in plane.units.items():
        out.append(
            {
                "id": uid,
                "label": u.label,
                "words": u.words,
                "skin": u.skin.value,
                "x": u.x,
                "y": u.y,
                "sandboxed": u.sandboxed,
                "sandbox_id": u.sandbox_id,
                "score": float(scores.get(uid, 0.0)),
                "connected": not u.sandboxed,
            }
        )
    return out


def plane_to_html(
    plane: Plane,
    *,
    scores: Optional[Dict[str, float]] = None,
    title: str = "Dell Matrix",
) -> str:
    svg = plane_to_svg(plane, scores=scores, title=title)
    payload = json.dumps(_nodes_payload(plane, scores))
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{html.escape(title)}</title>
<style>
  :root {{ color-scheme: dark; }}
  body {{ margin:0; background:#0a0b0e; color:#e8eaed; font-family:system-ui,sans-serif; }}
  header {{ padding:12px 16px; border-bottom:1px solid #222; display:flex; justify-content:space-between; gap:12px; flex-wrap:wrap; }}
  .meta {{ color:#9aa3b2; font-size:13px; }}
  main {{ display:flex; flex-wrap:wrap; gap:16px; padding:16px; justify-content:center; }}
  #panel {{
    min-width:240px; max-width:320px; background:#151820; border:1px solid #2a2f3a;
    border-radius:12px; padding:14px 16px; height:fit-content;
  }}
  #panel h2 {{ margin:0 0 8px; font-size:16px; }}
  #panel .k {{ color:#9aa3b2; font-size:12px; margin-top:10px; }}
  #panel .v {{ font-size:14px; white-space:pre-wrap; word-break:break-word; }}
  .node-shape:hover {{ filter: brightness(1.15); stroke:#fff; stroke-width:2; }}
  .node.active .node-shape {{ stroke:#fff; stroke-width:2.5; }}
  .hint {{ color:#5c6575; font-size:12px; }}
</style>
</head>
<body>
<header>
  <div>
    <strong>{html.escape(title)}</strong>
    <div class="meta">perspective={html.escape(plane.perspective.value)} · units={len(plane.units)} · Floor locked · interactive L{LEVEL}</div>
  </div>
  <div class="hint">Click a node for details</div>
</header>
<main>
{svg}
<aside id="panel">
  <h2 id="p-title">Select a unit</h2>
  <div class="k">id</div><div class="v" id="p-id">—</div>
  <div class="k">skin</div><div class="v" id="p-skin">—</div>
  <div class="k">score</div><div class="v" id="p-score">—</div>
  <div class="k">state</div><div class="v" id="p-state">—</div>
  <div class="k">words</div><div class="v" id="p-words">—</div>
</aside>
</main>
<script>
const NODES = {payload};
const byId = Object.fromEntries(NODES.map(n => [n.id, n]));
function show(id) {{
  const n = byId[id];
  if (!n) return;
  document.querySelectorAll('.node').forEach(g => g.classList.remove('active'));
  const g = document.querySelector('.node[data-id="'+id+'"]');
  if (g) g.classList.add('active');
  document.getElementById('p-title').textContent = n.label;
  document.getElementById('p-id').textContent = n.id;
  document.getElementById('p-skin').textContent = n.skin;
  document.getElementById('p-score').textContent = (n.score || 0).toFixed(2);
  document.getElementById('p-state').textContent = n.sandboxed ? ('SANDBOX '+(n.sandbox_id||'')) : 'CONNECTED';
  document.getElementById('p-words').textContent = n.words || '(empty)';
}}
document.querySelectorAll('.node').forEach(g => {{
  g.addEventListener('click', () => show(g.getAttribute('data-id')));
}});
</script>
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
    return {"svg": svg_path, "html": html_path, "level": str(LEVEL), "interactive": "true"}


def smoke() -> bool:
    print("=== VISUAL INTERACTIVE SMOKE ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{len(r)+1}] {name}: {'PASS' if ok else 'FAIL'}" + (f" | {detail}" if detail else ""))
        r.append(bool(ok))

    p = open_program("VisInt")
    p.place("biz", "Business", words="CRM routes", skin=Skin.BUILDING, x=1)
    p.place("music", "Music", words="Ep4", skin=Skin.SEED, x=-1)
    p.enhance_on()
    p.pulse()
    paths = write_visual(p.cube.session.plane, owner="VisInt", scores=p.scores())
    rec("files", os.path.isfile(paths["svg"]) and os.path.isfile(paths["html"]))
    html_txt = open(paths["html"], encoding="utf-8").read()
    rec("has script", "NODES" in html_txt and "addEventListener" in html_txt)
    rec("has panel", "p-words" in html_txt)
    rec("has node data", "Business" in html_txt)
    rec("interactive flag", paths.get("interactive") == "true")
    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


def demo() -> None:
    print("09[Show] > 15[Map] >> 47[Embed] :: Visual interactive")
    p = open_program("Demo")
    p.place("biz", "Business", skin=Skin.BUILDING, x=1)
    p.place("music", "Music", skin=Skin.SEED, x=-1)
    print(write_visual(p.cube.session.plane, owner="Demo"))


def main() -> None:
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    demo()


if __name__ == "__main__":
    main()
