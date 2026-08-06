#!/usr/bin/env python3
"""
Live two-way visual bridge — localhost only.

Lupe20 enhance: vision cone on SVG, WASD keys, facing arrows, movement trails,
proximity, AI follow/wander, in-view node highlight, command history.

Law: offline 127.0.0.1 · Nursery+confirm · Floor locked · pure stdlib.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import json
import math
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

_HOST = "127.0.0.1"
_DEFAULT_PORT = 8765

_AI: Dict[str, Any] = {
    "name": "AI",
    "pos": [2, 1],
    "facing": "N",
    "label": "AI",
    "doing": "idle",
    "last_action": "spawned",
    "mode": "manual",  # manual | wander | follow
    "trail": [],
}

_USER_TRAIL: List[List[float]] = []
_CMD_HISTORY: List[str] = []
_MAX_TRAIL = 12
_MAX_HIST = 16

_FACING_DELTA = {
    "N": (0, 1), "NE": (1, 1), "E": (1, 0), "SE": (1, -1),
    "S": (0, -1), "SW": (-1, -1), "W": (-1, 0), "NW": (-1, 1),
}
_FACING_ORDER = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
_VISION_RANGE = 5.5
_VISION_HALF_ANGLE = 55.0


def _push_trail(trail: List, pos) -> None:
    trail.append([float(pos[0]), float(pos[1])])
    while len(trail) > _MAX_TRAIL:
        trail.pop(0)


def _ai_step(steps: int = 1) -> Tuple[int, int]:
    dx, dy = _FACING_DELTA.get(_AI["facing"], (0, 1))
    _AI["pos"][0] += dx * steps
    _AI["pos"][1] += dy * steps
    _AI["doing"] = "walking"
    _AI["last_action"] = f"walked to {tuple(_AI['pos'])}"
    _push_trail(_AI["trail"], _AI["pos"])
    return tuple(_AI["pos"])


def _ai_turn(steps: int = 1) -> str:
    idx = _FACING_ORDER.index(_AI["facing"]) if _AI["facing"] in _FACING_ORDER else 0
    _AI["facing"] = _FACING_ORDER[(idx + steps) % 8]
    _AI["doing"] = "turning"
    _AI["last_action"] = f"turned to {_AI['facing']}"
    return _AI["facing"]


def _ai_tick_modes(user_pos: List[float]) -> None:
    mode = _AI.get("mode", "manual")
    if mode == "wander":
        # simple: step, occasionally turn
        import random
        if random.random() < 0.35:
            _ai_turn(1 if random.random() < 0.5 else -1)
        _ai_step(1)
        _AI["doing"] = "wandering"
    elif mode == "follow":
        ux, uy = float(user_pos[0]), float(user_pos[1])
        ax, ay = float(_AI["pos"][0]), float(_AI["pos"][1])
        dx, dy = ux - ax, uy - ay
        dist = math.hypot(dx, dy)
        if dist > 1.2:
            # face toward user then step
            ang = math.degrees(math.atan2(dy, dx)) % 360
            best, best_d = "E", 999
            for name, (fx, fy) in _FACING_DELTA.items():
                fa = math.degrees(math.atan2(fy, fx)) % 360
                d = abs(fa - ang) % 360
                d = min(d, 360 - d)
                if d < best_d:
                    best_d, best = d, name
            _AI["facing"] = best
            _ai_step(1)
            _AI["doing"] = "following"
            _AI["last_action"] = f"follow → {tuple(_AI['pos'])}"
        else:
            _AI["doing"] = "near user"
            _AI["last_action"] = "holding near"


def _angle_diff(a: float, b: float) -> float:
    d = abs(a - b) % 360
    return min(d, 360 - d)


def _facing_angle(facing: str) -> float:
    table = {"E": 0, "NE": 45, "N": 90, "NW": 135, "W": 180, "SW": 225, "S": 270, "SE": 315}
    return float(table.get(facing, 90))


def _vision(
    pos: List[float],
    facing: str,
    nodes: List[Dict[str, Any]],
    other: Optional[Dict[str, Any]] = None,
    range_: float = _VISION_RANGE,
) -> Dict[str, Any]:
    px, py = float(pos[0]), float(pos[1])
    face_ang = _facing_angle(facing)
    seen_nodes: List[Dict[str, Any]] = []
    in_view_ids: List[str] = []
    for n in nodes:
        dx = float(n.get("x", 0)) - px
        dy = float(n.get("y", 0)) - py
        dist = math.hypot(dx, dy)
        if dist < 0.01 or dist > range_:
            continue
        ang = math.degrees(math.atan2(dy, dx)) % 360
        if _angle_diff(ang, face_ang) <= _VISION_HALF_ANGLE:
            seen_nodes.append({
                "id": n.get("id"),
                "label": n.get("label"),
                "skin": n.get("skin"),
                "score": n.get("score", 0),
                "words": (n.get("words") or "")[:60],
                "dist": round(dist, 2),
            })
            in_view_ids.append(str(n.get("id")))
    seen_nodes.sort(key=lambda x: x["dist"])

    skins: Dict[str, int] = {}
    for sn in seen_nodes:
        skins[sn["skin"]] = skins.get(sn["skin"], 0) + 1
    pattern = {
        "count": len(seen_nodes),
        "skins": skins,
        "avg_score": round(sum(s["score"] for s in seen_nodes) / len(seen_nodes), 2) if seen_nodes else 0,
        "nearest": seen_nodes[0]["label"] if seen_nodes else None,
    }

    other_seen = None
    proximity = None
    if other and other.get("pos"):
        ox, oy = float(other["pos"][0]), float(other["pos"][1])
        dx, dy = ox - px, oy - py
        dist = math.hypot(dx, dy)
        proximity = {"name": other.get("name") or other.get("label"), "dist": round(dist, 2)}
        if 0.01 < dist <= range_:
            ang = math.degrees(math.atan2(dy, dx)) % 360
            if _angle_diff(ang, face_ang) <= _VISION_HALF_ANGLE:
                other_seen = {
                    "name": other.get("name") or other.get("label") or "other",
                    "pos": list(other["pos"]),
                    "facing": other.get("facing"),
                    "dist": round(dist, 2),
                    "doing": other.get("doing"),
                    "last_action": other.get("last_action"),
                }

    return {
        "facing": facing,
        "range": range_,
        "half_angle": _VISION_HALF_ANGLE,
        "nodes": seen_nodes[:12],
        "in_view_ids": in_view_ids,
        "pattern": pattern,
        "sees_other": other_seen,
        "proximity": proximity,
    }


def _user_body(program) -> Dict[str, Any]:
    body = {"pos": [0, 0], "facing": "N", "posture": "stand", "locomotion": "idle"}
    if hasattr(program, "avatar") and hasattr(program.avatar, "body"):
        b = program.avatar.body
        body = {
            "pos": list(b.pos) if hasattr(b, "pos") else [0, 0],
            "facing": b.facing.name if hasattr(b.facing, "name") else str(b.facing),
            "posture": b.posture.name.lower() if hasattr(b.posture, "name") else "stand",
            "locomotion": b.locomotion.name.lower() if hasattr(b.locomotion, "name") else "idle",
        }
        _push_trail(_USER_TRAIL, body["pos"])
    return body


def _state_payload(program) -> Dict[str, Any]:
    plane = program.cube.session.plane
    scores = program.scores() if hasattr(program, "scores") else {}
    nodes = []
    for uid, u in plane.units.items():
        nodes.append({
            "id": uid,
            "label": u.label,
            "words": getattr(u, "words", "") or "",
            "skin": u.skin.value if hasattr(u.skin, "value") else str(u.skin),
            "x": float(getattr(u, "x", 0) or 0),
            "y": float(getattr(u, "y", 0) or 0),
            "sandboxed": bool(getattr(u, "sandboxed", False)),
            "score": float(scores.get(uid, 0.0)),
        })
    nursery = program.ranked_proposals() if hasattr(program, "ranked_proposals") else []
    avatar = program.avatar_status() if hasattr(program, "avatar_status") else {}
    body = _user_body(program)
    lat = program.lattice.status() if hasattr(program, "lattice") else {}

    # AI modes tick lightly on state read when active
    if _AI.get("mode") in ("wander", "follow"):
        _ai_tick_modes(body["pos"])

    ai_info = {
        "name": _AI["name"],
        "pos": list(_AI["pos"]),
        "facing": _AI["facing"],
        "label": _AI["label"],
        "doing": _AI.get("doing", "idle"),
        "last_action": _AI.get("last_action", ""),
        "mode": _AI.get("mode", "manual"),
        "trail": list(_AI.get("trail") or []),
    }

    user_vision = _vision(body["pos"], body["facing"], nodes, other=ai_info)
    ai_vision = _vision(ai_info["pos"], ai_info["facing"], nodes, other={
        "name": "YOU", "pos": body["pos"], "facing": body["facing"],
        "doing": body.get("locomotion"), "last_action": body.get("posture"),
    })

    return {
        "ok": True,
        "owner": program.owner,
        "ideas": len(plane.units),
        "nodes": nodes,
        "nursery": nursery[:20],
        "avatar": avatar,
        "user": body,
        "user_trail": list(_USER_TRAIL),
        "ai": ai_info,
        "user_vision": user_vision,
        "ai_vision": ai_vision,
        "cmd_history": list(_CMD_HISTORY[-_MAX_HIST:]),
        "form": lat.get("form", "cube"),
        "skin": lat.get("skin", "cube"),
        "rings": list(getattr(program.duo, "rings", [])),
        "history_len": len(getattr(program, "history", [])),
        "floor": ["Alpha", "Delta", "Omega", "Omni"],
        "vision_range": _VISION_RANGE,
        "vision_half_angle": _VISION_HALF_ANGLE,
    }


def _handle_ai_command(cmd: str) -> Optional[Dict[str, Any]]:
    lower = cmd.lower().strip()
    if not lower.startswith("ai "):
        return None
    rest = lower[3:].strip()
    if rest in ("walk", "step", "forward"):
        pos = _ai_step(1)
        return {"ok": True, "msg": f"AI walked to {pos}"}
    if rest.startswith("walk ") or rest.startswith("step "):
        try:
            n = int(rest.split()[1])
        except Exception:
            n = 1
        pos = _ai_step(n)
        return {"ok": True, "msg": f"AI walked {n} to {pos}"}
    if rest in ("turn left", "left"):
        f = _ai_turn(-1)
        return {"ok": True, "msg": f"AI turned left → {f}"}
    if rest in ("turn right", "right"):
        f = _ai_turn(1)
        return {"ok": True, "msg": f"AI turned right → {f}"}
    if rest.startswith("face "):
        d = rest.split(maxsplit=1)[1].upper()
        if d in _FACING_DELTA:
            _AI["facing"] = d
            _AI["doing"] = "looking"
            _AI["last_action"] = f"faced {d}"
            return {"ok": True, "msg": f"AI facing {d}"}
        return {"ok": False, "error": f"unknown facing {d}"}
    if rest in ("status", "where", "pos"):
        return {"ok": True, "msg": f"AI at {_AI['pos']} face {_AI['facing']} mode={_AI.get('mode')} doing={_AI.get('doing')}"}
    if rest in ("look", "see", "vision"):
        _AI["doing"] = "looking"
        _AI["last_action"] = "looked"
        return {"ok": True, "msg": "AI looked"}
    if rest in ("wander", "mode wander"):
        _AI["mode"] = "wander"
        _AI["doing"] = "wandering"
        _AI["last_action"] = "mode=wander"
        return {"ok": True, "msg": "AI mode → wander"}
    if rest in ("follow", "mode follow"):
        _AI["mode"] = "follow"
        _AI["doing"] = "following"
        _AI["last_action"] = "mode=follow"
        return {"ok": True, "msg": "AI mode → follow"}
    if rest in ("manual", "mode manual", "stop"):
        _AI["mode"] = "manual"
        _AI["doing"] = "idle"
        _AI["last_action"] = "mode=manual"
        return {"ok": True, "msg": "AI mode → manual"}
    if rest.startswith("goto ") or rest.startswith("move "):
        parts = rest.split()
        try:
            x, y = int(parts[1]), int(parts[2])
            _AI["pos"] = [x, y]
            _push_trail(_AI["trail"], _AI["pos"])
            _AI["doing"] = "moved"
            _AI["last_action"] = f"goto {[x, y]}"
            return {"ok": True, "msg": f"AI moved to {[x, y]}"}
        except Exception:
            return {"ok": False, "error": "usage: ai goto X Y"}
    return {"ok": False, "error": f"unknown ai command: {rest}"}


def _run_command(program, cmd: str) -> Dict[str, Any]:
    cmd = (cmd or "").strip()
    if not cmd:
        return {"ok": False, "error": "empty command"}

    _CMD_HISTORY.append(cmd)
    while len(_CMD_HISTORY) > _MAX_HIST:
        _CMD_HISTORY.pop(0)

    lower = cmd.lower().strip()
    if lower in ("look", "see", "vision", "look around"):
        return {"ok": True, "msg": "Looking…", "command": cmd, "state": _state_payload(program)}

    # quick WASD-style aliases for user
    if lower in ("w", "forward"):
        cmd = "walk forward"
        lower = cmd
    elif lower == "a":
        cmd = "turn left"
        lower = cmd
    elif lower == "d":
        cmd = "turn right"
        lower = cmd
    elif lower == "s":
        cmd = "turn right"
        # double turn ≈ about face then optional; keep simple: turn right twice via two cmds not here
        lower = cmd

    ai_res = _handle_ai_command(cmd)
    if ai_res is not None:
        ai_res["command"] = cmd
        ai_res["state"] = _state_payload(program)
        return ai_res

    try:
        from form.mandell.seed import looks_like_seed
        from form.mandell.executor import execute_seed
        from form.mandell.translate import translate
        from form.repl import _execute_intent, _apply_seed_result
    except Exception as e:
        return {"ok": False, "error": f"import: {e}"}

    try:
        if looks_like_seed(cmd):
            result = execute_seed(program, cmd)
            _apply_seed_result(program, result)
        else:
            intent = translate(cmd)
            _execute_intent(program, intent, raw_line=cmd)
        return {"ok": True, "command": cmd, "state": _state_payload(program)}
    except Exception as e:
        return {"ok": False, "error": str(e), "command": cmd, "state": _state_payload(program)}


def _make_handler(program):
    class LiveHandler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

        def _cors(self):
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")

        def _json(self, code: int, payload: Dict[str, Any]):
            body = json.dumps(payload).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self._cors()
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_OPTIONS(self):
            self.send_response(204)
            self._cors()
            self.end_headers()

        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path in ("/", "/index.html", "/ui"):
                self._serve_ui()
                return
            if parsed.path == "/state":
                self._json(200, _state_payload(program))
                return
            if parsed.path == "/health":
                self._json(200, {"ok": True, "live": True})
                return
            self._json(404, {"ok": False, "error": "not found"})

        def do_POST(self):
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path != "/cmd":
                self._json(404, {"ok": False, "error": "not found"})
                return
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length).decode("utf-8") if length else ""
            cmd = ""
            try:
                data = json.loads(raw) if raw else {}
                cmd = data.get("cmd") or data.get("command") or ""
            except Exception:
                cmd = raw.strip()
            result = _run_command(program, cmd)
            self._json(200 if result.get("ok") else 400, result)

        def _serve_ui(self):
            body = _LIVE_HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return LiveHandler


_LIVE_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>DellMatrix Live</title>
<style>
:root{color-scheme:dark;--bg:#0a0b0e;--card:#151820;--line:#2a2f3a;--text:#e8eaed;--muted:#9aa3b2;--accent:#5b8def;--ok:#3cb371;--warn:#e6a817;--ai:#e879f9;--user:#38bdf8}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font-family:system-ui,sans-serif}
header{padding:10px 14px;border-bottom:1px solid var(--line);display:flex;gap:10px;align-items:center;justify-content:space-between;flex-wrap:wrap}
h1{margin:0;font-size:15px}.meta{color:var(--muted);font-size:11px}
.layout{display:grid;grid-template-columns:260px 1fr 270px;gap:10px;padding:10px;max-width:1500px;margin:0 auto}
@media(max-width:1100px){.layout{grid-template-columns:1fr}}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:10px}
h2{margin:0 0 6px;font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}
.btn-row{display:flex;flex-wrap:wrap;gap:5px;margin-bottom:6px}
button{background:#1c2230;color:var(--text);border:1px solid var(--line);border-radius:7px;padding:6px 8px;font-size:11px;cursor:pointer;min-height:30px}
button:hover{border-color:var(--accent)}button.primary{background:var(--accent);color:#fff;border-color:var(--accent)}
button.ok{border-color:var(--ok)}button.warn{border-color:var(--warn)}
button.user{border-color:var(--user)}button.ai{border-color:var(--ai)}
#cmd{width:100%;background:#0f1115;border:1px solid var(--line);border-radius:8px;color:#7dd3a0;padding:8px;font-family:ui-monospace,monospace;font-size:12px}
#log{font-size:11px;color:var(--muted);min-height:22px;margin-top:4px;white-space:pre-wrap}
#svg-wrap{width:100%;overflow:auto;background:#0f1115;border-radius:10px;border:1px solid var(--line)}
svg{display:block;width:100%;height:auto}.node-label{font-size:10px;fill:#e8eaed}
.seen{border:1px solid var(--line);border-radius:7px;padding:5px 7px;margin-bottom:4px;font-size:11px}
.seen .d{color:var(--muted);font-size:10px}.pattern{font-size:10px;color:var(--muted);margin-bottom:6px}
.proposal{border:1px solid var(--line);border-radius:7px;padding:6px;margin-bottom:5px;font-size:11px}.aff{color:var(--accent);font-size:10px}
.hist{font-size:10px;color:var(--muted);max-height:70px;overflow:auto}
kbd{background:#1c2230;border:1px solid var(--line);border-radius:4px;padding:1px 4px;font-size:10px}
</style>
</head>
<body>
<header>
  <div><h1>DellMatrix Live · Lupe20</h1><div class="meta" id="meta">connecting…</div></div>
  <div class="meta">WASD · vision cone · trails · AI modes · <label><input type="checkbox" id="auto" checked> auto</label></div>
</header>
<div class="layout">
  <section class="card">
    <h2>Actions</h2>
    <div class="btn-row">
      <button data-cmd="create an idea called live_seed">Create</button>
      <button data-cmd="grow ideas 1">Grow</button>
      <button data-cmd="confirm all" class="ok">Confirm all</button>
      <button data-cmd="look" class="user">Look</button>
    </div>
    <div class="btn-row">
      <button data-cmd="cube">Cube</button>
      <button data-cmd="sphere">Sphere</button>
      <button data-cmd="core">Core</button>
      <button data-cmd="flower">Flower</button>
    </div>
    <h2>User <kbd>W</kbd><kbd>A</kbd><kbd>D</kbd> + look</h2>
    <div class="btn-row">
      <button class="user" data-cmd="walk forward">W Walk</button>
      <button class="user" data-cmd="turn left">A ←</button>
      <button class="user" data-cmd="turn right">D →</button>
      <button class="user" data-cmd="look">Look</button>
      <button class="user" data-cmd="face north">Face N</button>
    </div>
    <h2>AI</h2>
    <div class="btn-row">
      <button class="ai" data-cmd="ai walk">Walk</button>
      <button class="ai" data-cmd="ai turn left">←</button>
      <button class="ai" data-cmd="ai turn right">→</button>
      <button class="ai" data-cmd="ai look">Look</button>
    </div>
    <div class="btn-row">
      <button class="ai" data-cmd="ai follow">Follow me</button>
      <button class="ai" data-cmd="ai wander">Wander</button>
      <button class="ai" data-cmd="ai manual">Manual</button>
      <button class="ai" data-cmd="ai status">Status</button>
    </div>
    <div class="btn-row">
      <button data-cmd="enhance on">Enhance</button>
      <button data-cmd="pulse">Pulse</button>
      <button data-cmd="save">Save</button>
      <button data-cmd="status">Status</button>
    </div>
    <input id="cmd" placeholder="W/A/D · look · ai follow · ai goto 3 4"/>
    <div class="btn-row" style="margin-top:5px">
      <button class="primary" id="send">Send</button>
      <button id="refresh">Refresh</button>
    </div>
    <div id="log"></div>
    <h2 style="margin-top:8px">Cmd history</h2>
    <div class="hist" id="hist">—</div>
  </section>
  <section class="card">
    <h2>Matrix</h2>
    <div id="svg-wrap"><svg id="matrix" viewBox="0 0 640 440"></svg></div>
    <h2 style="margin-top:8px">Your vision</h2>
    <div class="pattern" id="user-pattern">—</div>
    <div id="user-seen"></div>
    <h2 style="margin-top:8px">AI vision + doing</h2>
    <div class="pattern" id="ai-pattern">—</div>
    <div id="ai-seen"></div>
  </section>
  <section class="card">
    <h2>Nursery</h2>
    <div id="nursery"></div>
    <h2 style="margin-top:10px">User</h2>
    <div id="user-pos" class="meta">—</div>
    <h2 style="margin-top:10px">AI</h2>
    <div id="ai-pos" class="meta">—</div>
    <h2 style="margin-top:10px">Proximity</h2>
    <div id="prox" class="meta">—</div>
    <h2 style="margin-top:10px">Avatar</h2>
    <div id="avatar" class="meta">—</div>
    <h2 style="margin-top:10px">Rings</h2>
    <div id="rings" class="meta">—</div>
  </section>
</div>
<script>
const SKIN={cube:'#5b8def',sphere:'#7c5cbf',seed:'#3cb371',flower:'#e6a817',building:'#c47c48',words:'#888',circle:'#2aa7a0',core:'#d97706'};
const FACE_ANG={E:0,NE:45,N:90,NW:135,W:180,SW:225,S:270,SE:315};
const log=t=>document.getElementById('log').textContent=t;
async function getState(){const r=await fetch('/state');return r.json()}
async function sendCmd(cmd){
  log('→ '+cmd);
  const r=await fetch('/cmd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({cmd})});
  const data=await r.json();
  if(data.ok){log('✓ '+(data.msg||cmd));render(data.state||await getState())}
  else{log('✗ '+(data.error||'failed'));if(data.state)render(data.state)}
}
function conePath(cx,cy,facing,rangePx,halfAng){
  const base=(FACE_ANG[facing]||90)*Math.PI/180;
  // SVG y is down; our map already flips y, so invert angle for screen
  const a0= -base + (halfAng*Math.PI/180);
  const a1= -base - (halfAng*Math.PI/180);
  const x1=cx+Math.cos(a0)*rangePx, y1=cy+Math.sin(a0)*rangePx;
  const x2=cx+Math.cos(a1)*rangePx, y2=cy+Math.sin(a1)*rangePx;
  return `M ${cx} ${cy} L ${x1} ${y1} A ${rangePx} ${rangePx} 0 0 1 ${x2} ${y2} Z`;
}
function renderVision(elId,patId,vision){
  const box=document.getElementById(elId); const pat=document.getElementById(patId);
  if(!vision){box.innerHTML='';pat.textContent='—';return}
  const p=vision.pattern||{};
  pat.textContent=`face ${vision.facing} · see ${p.count||0} · skins ${JSON.stringify(p.skins||{})} · avg ${p.avg_score||0} · near ${p.nearest||'—'}`;
  box.innerHTML='';
  (vision.nodes||[]).forEach(n=>{
    const d=document.createElement('div');d.className='seen';
    d.innerHTML=`<div><b>${n.label}</b> <span class="d">${n.skin} · d=${n.dist} · sc=${n.score||0}</span></div>
      <div class="d">${n.words||''}</div>
      <button data-act="confirm ${n.id}">Confirm</button>
      <button data-act="create an idea called seen_${(n.label||'x').slice(0,10)}">Note</button>`;
    box.appendChild(d);
  });
  if(vision.sees_other){
    const o=vision.sees_other;
    const d=document.createElement('div');d.className='seen';
    d.innerHTML=`<div><b>sees ${o.name}</b> <span class="d">d=${o.dist} face ${o.facing} · ${o.doing||''}</span></div><div class="d">${o.last_action||''}</div>`;
    box.appendChild(d);
  }
  if(!(vision.nodes||[]).length && !vision.sees_other)box.innerHTML='<span class="meta">Nothing in view</span>';
  box.querySelectorAll('[data-act]').forEach(b=>b.onclick=()=>sendCmd(b.getAttribute('data-act')));
}
function render(s){
  if(!s)return;
  document.getElementById('meta').textContent=`owner=${s.owner||'?'} · ideas=${s.ideas??0} · form=${s.form||'?'} · AI mode=${(s.ai&&s.ai.mode)||'manual'}`;
  const svg=document.getElementById('matrix');
  const W=640,H=440,cx=W/2,cy=H/2,scale=46;
  let maxR=2.5;
  (s.nodes||[]).forEach(n=>{const r=Math.hypot(n.x,n.y);if(r>maxR)maxR=r});
  const user=s.user||{}, ai=s.ai||{};
  if(user.pos){const r=Math.hypot(user.pos[0]||0,user.pos[1]||0);if(r>maxR)maxR=r}
  if(ai.pos){const r=Math.hypot(ai.pos[0]||0,ai.pos[1]||0);if(r>maxR)maxR=r}
  if(maxR<2.5)maxR=2.5;
  const map=(x,y)=>[cx+(x/maxR)*scale*3.2, cy-(y/maxR)*scale*3.2];
  const rangePx=(s.vision_range||5.5)/maxR*scale*3.2;
  const half=s.vision_half_angle||55;
  const inView=new Set((s.user_vision&&s.user_vision.in_view_ids)||[]);
  let els=`<rect width="100%" height="100%" fill="#0f1115" rx="8"/>`;
  els+=`<text x="12" y="16" fill="#5c6575" font-size="10">form=${s.form||'?'} · cones · trails · lupe20</text>`;
  // trails
  const drawTrail=(trail,col)=>{
    if(!trail||trail.length<2)return;
    let d='';
    trail.forEach((p,i)=>{const [x,y]=map(p[0],p[1]);d+=(i?`L ${x} ${y}`:`M ${x} ${y}`)});
    els+=`<path d="${d}" fill="none" stroke="${col}" stroke-width="2" opacity="0.35"/>`;
  };
  drawTrail(s.user_trail,'#38bdf8');
  drawTrail(ai.trail,'#e879f9');
  // vision cones
  if(user.pos){const [ux,uy]=map(user.pos[0]||0,user.pos[1]||0);
    els+=`<path d="${conePath(ux,uy,user.facing||'N',rangePx,half)}" fill="#38bdf8" opacity="0.12" stroke="#38bdf8" stroke-width="1" opacity="0.2"/>`;}
  if(ai.pos){const [ax,ay]=map(ai.pos[0]||0,ai.pos[1]||0);
    els+=`<path d="${conePath(ax,ay,ai.facing||'N',rangePx,half)}" fill="#e879f9" opacity="0.10" stroke="#e879f9" stroke-width="1"/>`;}
  // nodes
  (s.nodes||[]).forEach(n=>{
    const [x,y]=map(n.x,n.y); const col=SKIN[n.skin]||'#5b8def'; const r=n.sandboxed?10:14;
    const glow=inView.has(String(n.id))?` stroke="#fff" stroke-width="2.5"`:'';
    if(['sphere','circle','seed','flower','core'].includes(n.skin))
      els+=`<circle cx="${x}" cy="${y}" r="${r}" fill="${col}" opacity="0.92" data-id="${n.id}" style="cursor:pointer"${glow}/>`;
    else els+=`<rect x="${x-r}" y="${y-r}" width="${r*2}" height="${r*2}" rx="3" fill="${col}" opacity="0.92" data-id="${n.id}" style="cursor:pointer"${glow}/>`;
    els+=`<text x="${x}" y="${y+r+10}" text-anchor="middle" class="node-label">${(n.label||'').slice(0,11)}</text>`;
  });
  // markers + facing arrows
  const arrow=(x,y,facing,col)=>{
    const ang=(-(FACE_ANG[facing]||90))*Math.PI/180;
    const len=16; const x2=x+Math.cos(ang)*len, y2=y+Math.sin(ang)*len;
    els+=`<line x1="${x}" y1="${y}" x2="${x2}" y2="${y2}" stroke="${col}" stroke-width="2.5" marker-end="url(#arrow)"/>`;
  };
  els+=`<defs><marker id="arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#fff"/></marker></defs>`;
  if(user.pos){const [ux,uy]=map(user.pos[0]||0,user.pos[1]||0);
    els+=`<circle cx="${ux}" cy="${uy}" r="9" fill="#38bdf8" stroke="#fff" stroke-width="2"/>`;
    els+=`<text x="${ux}" y="${uy-13}" text-anchor="middle" fill="#38bdf8" font-size="10" font-weight="600">YOU</text>`;
    arrow(ux,uy,user.facing||'N','#38bdf8');
  }
  if(ai.pos){const [ax,ay]=map(ai.pos[0]||0,ai.pos[1]||0);
    els+=`<circle cx="${ax}" cy="${ay}" r="9" fill="#e879f9" stroke="#fff" stroke-width="2"/>`;
    els+=`<text x="${ax}" y="${ay-13}" text-anchor="middle" fill="#e879f9" font-size="10" font-weight="600">AI</text>`;
    arrow(ax,ay,ai.facing||'N','#e879f9');
  }
  svg.innerHTML=els;
  svg.querySelectorAll('[data-id]').forEach(el=>{
    el.addEventListener('click',()=>{
      const id=el.getAttribute('data-id');
      document.getElementById('cmd').value='confirm '+id;
    });
  });
  renderVision('user-seen','user-pattern',s.user_vision);
  renderVision('ai-seen','ai-pattern',s.ai_vision);
  if(s.ai){const ap=document.getElementById('ai-pattern');
    ap.textContent+=(ap.textContent?' · ':'')+`mode ${s.ai.mode||'manual'} · ${s.ai.doing||''} · ${s.ai.last_action||''}`;
  }
  const nur=document.getElementById('nursery');nur.innerHTML='';
  (s.nursery||[]).forEach(p=>{
    const d=document.createElement('div');d.className='proposal';
    d.innerHTML=`<div class="aff">aff ${(p.affinity||0).toFixed(3)} · ${p.kind||''}</div><div>${p.label||''}</div>
      <div style="margin-top:3px"><button data-c="${p.id||''}">Confirm</button> <button data-r="${p.id||''}" class="warn">Reject</button></div>`;
    nur.appendChild(d);
  });
  if(!(s.nursery||[]).length)nur.innerHTML='<span class="meta">Nursery empty</span>';
  nur.querySelectorAll('[data-c]').forEach(b=>b.onclick=()=>sendCmd('confirm '+b.getAttribute('data-c')));
  nur.querySelectorAll('[data-r]').forEach(b=>b.onclick=()=>sendCmd('reject '+b.getAttribute('data-r')));
  document.getElementById('user-pos').textContent=`pos ${JSON.stringify(user.pos||[0,0])} · face ${user.facing||'?'} · ${user.posture||''} ${user.locomotion||''}`;
  document.getElementById('ai-pos').textContent=`pos ${JSON.stringify(ai.pos||[0,0])} · face ${ai.facing||'?'} · mode ${ai.mode||'manual'} · ${ai.doing||''}`;
  const prox=(s.user_vision&&s.user_vision.proximity)||null;
  document.getElementById('prox').textContent=prox?`${prox.name} dist ${prox.dist}`:'—';
  const av=s.avatar||{};
  document.getElementById('avatar').textContent=(av.look||'')+'  '+(av.describe||'—');
  document.getElementById('rings').textContent=(s.rings||[]).join(' → ')||'—';
  document.getElementById('hist').textContent=(s.cmd_history||[]).slice().reverse().join(' · ')||'—';
}
document.getElementById('send').onclick=()=>{const c=document.getElementById('cmd').value.trim();if(c)sendCmd(c)};
document.getElementById('cmd').addEventListener('keydown',e=>{if(e.key==='Enter')document.getElementById('send').click()});
document.getElementById('refresh').onclick=async()=>{render(await getState());log('refreshed')};
document.querySelectorAll('[data-cmd]').forEach(b=>b.onclick=()=>sendCmd(b.getAttribute('data-cmd')));
// WASD when not typing in input
window.addEventListener('keydown',e=>{
  if(document.activeElement===document.getElementById('cmd'))return;
  const k=e.key.toLowerCase();
  if(k==='w'){e.preventDefault();sendCmd('walk forward')}
  else if(k==='a'){e.preventDefault();sendCmd('turn left')}
  else if(k==='d'){e.preventDefault();sendCmd('turn right')}
  else if(k==='q'){e.preventDefault();sendCmd('look')}
  else if(k==='e'){e.preventDefault();sendCmd('ai look')}
  else if(k==='f'){e.preventDefault();sendCmd('ai follow')}
});
getState().then(render).catch(e=>log('connect failed: '+e));
setInterval(async()=>{if(document.getElementById('auto').checked){try{render(await getState())}catch(e){}}},1800);
</script>
</body>
</html>
"""


def start_live(program, port: int = _DEFAULT_PORT, background: bool = True) -> Dict[str, Any]:
    handler = _make_handler(program)
    server = HTTPServer((_HOST, port), handler)

    def _serve():
        try:
            server.serve_forever()
        except Exception:
            pass

    if background:
        t = threading.Thread(target=_serve, daemon=True)
        t.start()
    else:
        server.serve_forever()

    return {
        "ok": True,
        "url": f"http://{_HOST}:{port}/",
        "host": _HOST,
        "port": port,
        "note": "Lupe20: WASD, vision cones, trails, AI follow/wander, proximity, act on seen.",
        "stop": "Process exit stops the server.",
    }


def smoke() -> bool:
    print("=== LIVE VISUAL LUPE20 SMOKE ===")
    try:
        from form.open import open_program
        p = open_program("LiveSmoke")
        p.place("a", "Alpha", words="test", x=1, y=2)
        st = _state_payload(p)
        assert "user_vision" in st and "ai_vision" in st
        assert "user_trail" in st
        out = _run_command(p, "ai follow")
        assert out.get("ok") is True
        out = _run_command(p, "look")
        assert out.get("ok") is True
        print("[PASS] lupe20 core")
        print("=== RESULT: PASS ===")
        return True
    except Exception as e:
        print("[FAIL]", e)
        return False


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
