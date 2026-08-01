#!/usr/bin/env python3
"""
Visual control panel — intuitive offline HTML UI.

Writes:
  1) form/state/visual/matrix_<owner>.html  (history)
  2) DellMatrix_UI.html at project root     (easy to find)

Node shapes follow live lattice form when unit skin is generic.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import html
import json
import os
import sys

try:
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.dell_matrix.plane import Plane, Skin
    from form.dell_matrix.graph_view import build_view
    from form.open import open_program
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.dell_matrix.plane import Plane, Skin
    from form.dell_matrix.graph_view import build_view
    from form.open import open_program

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_OUT = os.path.join(os.path.dirname(__file__), "..", "state", "visual")
os.makedirs(_OUT, exist_ok=True)
EASY_UI = os.path.join(_ROOT, "DellMatrix_UI.html")

LEVEL = 5

_SKIN_COLOR = {
    "cube": "#5b8def", "sphere": "#7c5cbf", "seed": "#3cb371",
    "flower": "#e6a817", "building": "#c47c48", "words": "#888888", "circle": "#2aa7a0",
    "core": "#d97706",
}

# form → default geometric skin for generic units
_FORM_SKIN = {
    "cube": "cube",
    "sphere": "sphere",
    "core": "seed",
    "flower": "flower",
    "square": "cube",
    "circle": "circle",
}

ACTIONS = [
    {"group": "Ideas", "items": [
        {"label": "Create idea", "cmd": "create an idea called ", "hint": "Type a name after this"},
        {"label": "Grow ideas", "cmd": "grow ideas 2", "hint": "Ringed growth → Nursery"},
        {"label": "Show proposals", "cmd": "proposals", "hint": "View Nursery quarantine"},
        {"label": "Show matrix", "cmd": "show me", "hint": "Print live state"},
    ]},
    {"group": "Nursery", "items": [
        {"label": "Confirm idea", "cmd": "confirm ", "hint": "Paste proposal id after"},
        {"label": "Reject idea", "cmd": "reject ", "hint": "Paste proposal id after"},
        {"label": "Confirm all", "cmd": "confirm all", "hint": ""},
        {"label": "Reject all", "cmd": "reject all", "hint": ""},
    ]},
    {"group": "Lattice", "items": [
        {"label": "Cube", "cmd": "cube", "hint": ""},
        {"label": "Sphere", "cmd": "sphere", "hint": ""},
        {"label": "Core", "cmd": "core", "hint": ""},
        {"label": "Flower", "cmd": "flower", "hint": ""},
        {"label": "Lattice", "cmd": "lattice", "hint": ""},
    ]},
    {"group": "Avatar", "items": [
        {"label": "Walk forward", "cmd": "walk forward", "hint": ""},
        {"label": "Turn left", "cmd": "turn left", "hint": ""},
        {"label": "Turn right", "cmd": "turn right", "hint": ""},
        {"label": "Sit down", "cmd": "sit down", "hint": ""},
        {"label": "Stand up", "cmd": "stand up", "hint": ""},
        {"label": "Smile", "cmd": "smile", "hint": ""},
        {"label": "How do I look?", "cmd": "how do I look", "hint": ""},
    ]},
    {"group": "System", "items": [
        {"label": "Enhance ON", "cmd": "enhance on", "hint": ""},
        {"label": "Enhance OFF", "cmd": "enhance off", "hint": ""},
        {"label": "Pulse", "cmd": "pulse", "hint": ""},
        {"label": "Save", "cmd": "save", "hint": ""},
        {"label": "Status", "cmd": "status", "hint": ""},
        {"label": "Help", "cmd": "help", "hint": ""},
    ]},
]


def _map_pos(x: float, y: float, scale: float = 70.0, cx: float = 360.0, cy: float = 260.0) -> Tuple[float, float]:
    return cx + x * scale, cy - y * scale


def _resolve_skin(unit_skin: str, form: str) -> str:
    """Prefer explicit unit skin; otherwise follow live lattice form."""
    if unit_skin and unit_skin not in ("cube", ""):
        return unit_skin
    return _FORM_SKIN.get(form, "cube")


def plane_to_svg(
    plane: Plane,
    *,
    scores: Optional[Dict[str, float]] = None,
    width: int = 720,
    height: int = 520,
    title: str = "Dell Matrix",
    form: str = "cube",
) -> str:
    assert_floor_intact()
    scores = scores or {}
    view = build_view(plane)
    cx, cy = width / 2, height / 2
    parts: List[str] = [
        f'<svg id="matrix-svg" xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="100%" height="100%" fill="#0f1115" rx="12"/>',
        f'<text x="16" y="26" fill="#9aa3b2" font-family="system-ui,sans-serif" font-size="13">{html.escape(title)}</text>',
        f'<text x="16" y="44" fill="#5c6575" font-family="system-ui,sans-serif" font-size="11">form={html.escape(form)} · Floor: {" · ".join(FLOOR)}</text>',
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
    for n in view.nodes:
        x, y = pos[n.id]
        skin = _resolve_skin(n.skin, form)
        color = _SKIN_COLOR.get(skin, "#5b8def")
        r = 18
        sc = scores.get(n.id, 0.0)
        parts.append(f'<g class="node" data-id="{html.escape(n.id)}" style="cursor:pointer">')
        if skin in ("sphere", "circle", "seed", "flower", "core"):
            parts.append(f'<circle class="node-shape" cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{color}" opacity="0.9"/>')
        else:
            parts.append(
                f'<rect class="node-shape" x="{x-r:.1f}" y="{y-r:.1f}" width="{2*r}" height="{2*r}" fill="{color}" rx="4" opacity="0.9"/>'
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
    if not view.nodes:
        parts.append(
            f'<text x="{cx}" y="{cy}" text-anchor="middle" fill="#5c6575" '
            f'font-family="system-ui,sans-serif" font-size="14">No ideas yet — create one</text>'
        )
    parts.append("</svg>")
    return "\n".join(parts)


def _nodes_payload(plane: Plane, scores: Optional[Dict[str, float]] = None) -> List[Dict[str, Any]]:
    scores = scores or {}
    out = []
    for uid, u in plane.units.items():
        out.append({
            "id": uid, "label": u.label, "words": u.words, "skin": u.skin.value,
            "x": u.x, "y": u.y, "sandboxed": u.sandboxed,
            "score": float(scores.get(uid, 0.0)),
        })
    return out


def plane_to_html(
    plane: Plane,
    *,
    scores: Optional[Dict[str, float]] = None,
    title: str = "Dell Matrix",
    owner: str = "Operator",
    avatar: Optional[Dict[str, Any]] = None,
    nursery: Optional[List[Dict[str, Any]]] = None,
    rings: Optional[List[str]] = None,
    form: str = "cube",
    skin: str = "cube",
) -> str:
    svg = plane_to_svg(plane, scores=scores, title=title, form=form)
    nodes = json.dumps(_nodes_payload(plane, scores))
    actions = json.dumps(ACTIONS)
    nursery = nursery or []
    avatar = avatar or {}
    rings = rings or ["Seed", "Token", "Body", "Lens", "Evolve"]
    nursery_json = json.dumps(nursery)
    avatar_json = json.dumps(avatar)
    rings_s = " → ".join(rings)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{html.escape(title)}</title>
<style>
  :root {{ color-scheme: dark; --bg:#0a0b0e; --card:#151820; --line:#2a2f3a; --text:#e8eaed; --muted:#9aa3b2; --accent:#5b8def; --ok:#3cb371; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--text); font-family:system-ui,-apple-system,sans-serif; }}
  header {{ padding:14px 18px; border-bottom:1px solid var(--line); display:flex; flex-wrap:wrap; gap:12px; align-items:center; justify-content:space-between; }}
  header h1 {{ margin:0; font-size:18px; font-weight:600; }}
  header .meta {{ color:var(--muted); font-size:12px; }}
  .layout {{ display:grid; grid-template-columns: 280px 1fr 280px; gap:14px; padding:14px; max-width:1400px; margin:0 auto; }}
  @media (max-width: 1000px) {{ .layout {{ grid-template-columns: 1fr; }} }}
  .card {{ background:var(--card); border:1px solid var(--line); border-radius:14px; padding:14px; }}
  .card h2 {{ margin:0 0 10px; font-size:14px; color:var(--muted); font-weight:600; text-transform:uppercase; letter-spacing:.04em; }}
  .group {{ margin-bottom:14px; }}
  .group-title {{ font-size:12px; color:var(--muted); margin-bottom:6px; }}
  .btn-row {{ display:flex; flex-wrap:wrap; gap:6px; }}
  button.action {{ background:#1c2230; color:var(--text); border:1px solid var(--line); border-radius:10px; padding:8px 12px; font-size:13px; cursor:pointer; }}
  button.action:hover {{ border-color:var(--accent); background:#222a3a; }}
  #cmd-box {{ margin-top:12px; padding:12px; background:#0f1115; border-radius:10px; border:1px dashed var(--line); min-height:64px; }}
  #cmd-box .label {{ font-size:11px; color:var(--muted); margin-bottom:4px; }}
  #cmd-text {{ font-size:15px; font-family:ui-monospace,monospace; color:#7dd3a0; word-break:break-word; }}
  #cmd-hint {{ font-size:12px; color:var(--muted); margin-top:6px; }}
  .copy-btn {{ margin-top:8px; background:var(--accent); color:#fff; border:none; border-radius:8px; padding:6px 12px; font-size:12px; cursor:pointer; }}
  .node-shape:hover {{ filter:brightness(1.15); stroke:#fff; stroke-width:2; }}
  .node.active .node-shape {{ stroke:#fff; stroke-width:2.5; }}
  #detail .k {{ color:var(--muted); font-size:11px; margin-top:8px; }}
  #detail .v {{ font-size:13px; word-break:break-word; }}
  .proposal {{ border:1px solid var(--line); border-radius:10px; padding:8px 10px; margin-bottom:8px; font-size:13px; }}
  .proposal .kind {{ color:var(--ok); font-size:11px; }}
  .avatar-line {{ font-size:14px; margin-bottom:6px; }}
  .empty {{ color:var(--muted); font-size:13px; }}
  .credit {{ font-size:11px; color:#5c6575; margin-top:10px; line-height:1.4; }}
</style>
</head>
<body>
<header>
  <div>
    <h1>{html.escape(title)}</h1>
    <div class="meta">owner={html.escape(owner)} · ideas={len(plane.units)} · form={html.escape(form)} · skin={html.escape(skin)} · rings: {html.escape(rings_s)}</div>
  </div>
  <div class="meta">Offline control panel · type commands in the program window</div>
</header>
<div class="layout">
  <section class="card" id="controls">
    <h2>Actions</h2>
    <div id="btn-root"></div>
    <div id="cmd-box">
      <div class="label">Type this in the program:</div>
      <div id="cmd-text">(tap a button)</div>
      <div id="cmd-hint"></div>
      <button class="copy-btn" id="copy-btn" type="button">Copy command</button>
    </div>
    <div class="credit">
      Growth uses Voynich-inspired rings (Seed→Token→Body→Lens→Evolve).
      Proposals stay in Nursery until you confirm. Live matrix is never auto-changed.
      Node shapes follow live lattice form when unit skin is generic.
    </div>
  </section>
  <section class="card" style="overflow:auto">
    <h2>Live matrix</h2>
    {svg}
    <div id="detail" style="margin-top:12px">
      <h2 style="margin-top:0">Selected idea</h2>
      <div class="k">label</div><div class="v" id="p-title">—</div>
      <div class="k">id</div><div class="v" id="p-id">—</div>
      <div class="k">score</div><div class="v" id="p-score">—</div>
      <div class="k">words</div><div class="v" id="p-words">—</div>
    </div>
  </section>
  <section class="card">
    <h2>Avatar</h2>
    <div id="avatar-box" class="avatar-line empty">—</div>
    <h2 style="margin-top:18px">Nursery (quarantine)</h2>
    <div id="nursery-box" class="empty">No pending proposals</div>
  </section>
</div>
<script>
const NODES = {nodes};
const ACTIONS = {actions};
const NURSERY = {nursery_json};
const AVATAR = {avatar_json};
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
    b.type = 'button'; b.className = 'action'; b.textContent = item.label;
    b.addEventListener('click', () => {{
      document.getElementById('cmd-text').textContent = item.cmd;
      document.getElementById('cmd-hint').textContent = item.hint || '';
      window._lastCmd = item.cmd;
    }});
    row.appendChild(b);
  }});
  wrap.appendChild(row); root.appendChild(wrap);
}});
document.getElementById('copy-btn').addEventListener('click', async () => {{
  const t = window._lastCmd || '';
  if (!t) return;
  try {{ await navigator.clipboard.writeText(t); document.getElementById('cmd-hint').textContent = 'Copied — paste into the program window'; }}
  catch (e) {{ document.getElementById('cmd-hint').textContent = 'Select and copy the command above'; }}
}});
function showNode(id) {{
  const n = byId[id]; if (!n) return;
  document.querySelectorAll('.node').forEach(g => g.classList.remove('active'));
  const g = document.querySelector('.node[data-id="'+id+'"]');
  if (g) g.classList.add('active');
  document.getElementById('p-title').textContent = n.label;
  document.getElementById('p-id').textContent = n.id;
  document.getElementById('p-score').textContent = (n.score || 0).toFixed(2);
  document.getElementById('p-words').textContent = n.words || '(empty)';
}}
document.querySelectorAll('.node').forEach(g => g.addEventListener('click', () => showNode(g.getAttribute('data-id'))));
(function(){{
  const box = document.getElementById('avatar-box');
  if (AVATAR && (AVATAR.look || AVATAR.describe)) {{
    box.className = 'avatar-line';
    box.textContent = (AVATAR.look || '') + '  ' + (AVATAR.describe || '');
  }}
}})();
(function(){{
  const box = document.getElementById('nursery-box');
  if (!NURSERY || !NURSERY.length) return;
  box.className = ''; box.innerHTML = '';
  NURSERY.slice(0, 12).forEach(p => {{
    const d = document.createElement('div');
    d.className = 'proposal';
    d.innerHTML = '<div class="kind">' + (p.kind || '') + ' · ' + (p.id || '') + '</div>'
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
) -> Dict[str, str]:
    base = os.path.join(_OUT, f"matrix_{owner}")
    svg_path = base + ".svg"
    html_path = base + ".html"
    title = f"Dell Matrix · {owner}"
    svg = plane_to_svg(plane, scores=scores, title=title, form=form)
    doc = plane_to_html(
        plane, scores=scores, title=title, owner=owner,
        avatar=avatar, nursery=nursery, rings=rings,
        form=form, skin=skin,
    )
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(doc)
    with open(EASY_UI, "w", encoding="utf-8") as f:
        f.write(doc)
    return {
        "svg": svg_path,
        "html": html_path,
        "easy": EASY_UI,
        "level": str(LEVEL),
        "form": form,
        "skin": skin,
        "interactive": "true",
    }


def smoke() -> bool:
    print("=== VISUAL UI SMOKE ===")
    r = []
    def rec(name, ok, detail=""):
        print(f"[{len(r)+1}] {name}: {'PASS' if ok else 'FAIL'}" + (f" | {detail}" if detail else ""))
        r.append(bool(ok))
    p = open_program("VisUI")
    p.place("biz", "Business", words="crm", skin=Skin.BUILDING, x=1)
    p.lattice.to_sphere()
    paths = write_visual(
        p.cube.session.plane, owner="VisUI",
        avatar=p.avatar_status(), rings=list(p.duo.rings),
        form=p.lattice.perception.form.value,
        skin=p.lattice.perception.skin_name(),
    )
    rec("html", os.path.isfile(paths["html"]))
    rec("easy path", os.path.isfile(paths.get("easy", "")))
    txt = open(paths["html"], encoding="utf-8").read()
    rec("buttons", "Grow ideas" in txt)
    rec("form meta", "form=sphere" in txt or "form=cube" in txt)
    rec("lattice buttons", "Sphere" in txt)
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
    ))


if __name__ == "__main__":
    main()
