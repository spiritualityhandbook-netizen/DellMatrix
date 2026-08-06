#!/usr/bin/env python3
"""
Live two-way visual bridge — localhost only.

Full movement + directional vision for User and AI.
When you look, you see ideas, patterns, and what the AI sees/does.
You can act on that information.

Constraints: offline (127.0.0.1), Nursery+confirm, Floor locked.
Pure stdlib.
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
}

_FACING_DELTA = {
    "N": (0, 1), "NE": (1, 1), "E": (1, 0), "SE": (1, -1),
    "S": (0, -1), "SW": (-1, -1), "W": (-1, 0), "NW": (-1, 1),
}
_FACING_ORDER = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
_VISION_RANGE = 5.0
_VISION_HALF_ANGLE = 55.0  # degrees either side of facing


def _ai_step(steps: int = 1) -> Tuple[int, int]:
    dx, dy = _FACING_DELTA.get(_AI["facing"], (0, 1))
    _AI["pos"][0] += dx * steps
    _AI["pos"][1] += dy * steps
    _AI["doing"] = "walking"
    _AI["last_action"] = f"walked to {tuple(_AI['pos'])}"
    return tuple(_AI["pos"])


def _ai_turn(steps: int = 1) -> str:
    idx = _FACING_ORDER.index(_AI["facing"]) if _AI["facing"] in _FACING_ORDER else 0
    _AI["facing"] = _FACING_ORDER[(idx + steps) % 8]
    _AI["doing"] = "turning"
    _AI["last_action"] = f"turned to {_AI['facing']}"
    return _AI["facing"]


def _angle_diff(a: float, b: float) -> float:
    d = abs(a - b) % 360
    return min(d, 360 - d)


def _facing_angle(facing: str) -> float:
    # 0 = East, 90 = North (math angles)
    table = {"E": 0, "NE": 45, "N": 90, "NW": 135, "W": 180, "SW": 225, "S": 270, "SE": 315}
    return float(table.get(facing, 90))


def _vision(
    pos: List[float],
    facing: str,
    nodes: List[Dict[str, Any]],
    other: Optional[Dict[str, Any]] = None,
    range_: float = _VISION_RANGE,
) -> Dict[str, Any]:
    """Return what is visible in the facing cone."""
    px, py = float(pos[0]), float(pos[1])
    face_ang = _facing_angle(facing)
    seen_nodes: List[Dict[str, Any]] = []
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
    seen_nodes.sort(key=lambda x: x["dist"])

    # patterns
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
    if other and other.get("pos"):
        ox, oy = float(other["pos"][0]), float(other["pos"][1])
        dx, dy = ox - px, oy - py
        dist = math.hypot(dx, dy)
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
        "nodes": seen_nodes[:12],
        "pattern": pattern,
        "sees_other": other_seen,
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

    ai_info = {
        "name": _AI["name"],
        "pos": list(_AI["pos"]),
        "facing": _AI["facing"],
        "label": _AI["label"],
        "doing": _AI.get("doing", "idle"),
        "last_action": _AI.get("last_action", ""),
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
        "ai": ai_info,
        "user_vision": user_vision,
        "ai_vision": ai_vision,
        "form": lat.get("form", "cube"),
        "skin": lat.get("skin", "cube"),
        "rings": list(getattr(program.duo, "rings", [])),
        "history_len": len(getattr(program, "history", [])),
        "floor": ["Alpha", "Delta", "Omega", "Omni"],
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
        return {"ok": True, "msg": f"AI at {_AI['pos']} facing {_AI['facing']} doing={_AI.get('doing')}"}
    if rest in ("look", "see", "vision"):
        _AI["doing"] = "looking"
        _AI["last_action"] = "looked"
        return {"ok": True, "msg": "AI looked"}
    if rest.startswith("goto ") or rest.startswith("move "):
        parts = rest.split()
        try:
            x, y = int(parts[1]), int(parts[2])
            _AI["pos"] = [x, y]
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

    lower = cmd.lower().strip()
    if lower in ("look", "see", "vision", "look around"):
        # just refresh vision in state
        return {"ok": True, "msg": "Looking…", "command": cmd, "state": _state_payload(program)}

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
header{padding:12px 16px;border-bottom:1px solid var(--line);display:flex;gap:10px;align-items:center;justify-content:space-between;flex-wrap:wrap}
h1{margin:0;font-size:16px}.meta{color:var(--muted);font-size:12px}
.layout{display:grid;grid-template-columns:270px 1fr 280px;gap:12px;padding:12px;max-width:1480px;margin:0 auto}
@media(max-width:1100px){.layout{grid-template-columns:1fr}}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px}
h2{margin:0 0 8px;font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}
.btn-row{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px}
button{background:#1c2230;color:var(--text);border:1px solid var(--line);border-radius:8px;padding:7px 9px;font-size:12px;cursor:pointer;min-height:32px}
button:hover{border-color:var(--accent)}button.primary{background:var(--accent);color:#fff;border-color:var(--accent)}
button.ok{border-color:var(--ok)}button.warn{border-color:var(--warn)}
button.user{border-color:var(--user)}button.ai{border-color:var(--ai)}
#cmd{width:100%;background:#0f1115;border:1px solid var(--line);border-radius:8px;color:#7dd3a0;padding:9px;font-family:ui-monospace,monospace;font-size:13px}
#log{font-size:11px;color:var(--muted);min-height:24px;margin-top:6px;white-space:pre-wrap}
#svg-wrap{width:100%;overflow:auto;background:#0f1115;border-radius:10px;border:1px solid var(--line)}
svg{display:block;width:100%;height:auto}.node-label{font-size:11px;fill:#e8eaed}
.seen{border:1px solid var(--line);border-radius:8px;padding:6px 8px;margin-bottom:5px;font-size:12px}
.seen .d{color:var(--muted);font-size:10px}.pattern{font-size:11px;color:var(--muted);margin-bottom:8px}
.proposal{border:1px solid var(--line);border-radius:8px;padding:8px;margin-bottom:6px;font-size:12px}.aff{color:var(--accent);font-size:10px}
</style>
</head>
<body>
<header>
  <div><h1>DellMatrix Live</h1><div class="meta" id="meta">connecting…</div></div>
  <div class="meta">look · patterns · AI vision · act · <label><input type="checkbox" id="auto" checked> auto 2s</label></div>
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
    <h2>User move / look</h2>
    <div class="btn-row">
      <button class="user" data-cmd="walk forward">Walk</button>
      <button class="user" data-cmd="turn left">←</button>
      <button class="user" data-cmd="turn right">→</button>
      <button class="user" data-cmd="face north">Face N</button>
      <button class="user" data-cmd="look">Look</button>
    </div>
    <h2>AI move / look</h2>
    <div class="btn-row">
      <button class="ai" data-cmd="ai walk">Walk</button>
      <button class="ai" data-cmd="ai turn left">←</button>
      <button class="ai" data-cmd="ai turn right">→</button>
      <button class="ai" data-cmd="ai look">Look</button>
      <button class="ai" data-cmd="ai status">Status</button>
    </div>
    <div class="btn-row">
      <button data-cmd="enhance on">Enhance</button>
      <button data-cmd="pulse">Pulse</button>
      <button data-cmd="save">Save</button>
      <button data-cmd="status">Status</button>
    </div>
    <input id="cmd" placeholder="look · ai look · ai goto 3 4 · confirm id"/>
    <div class="btn-row" style="margin-top:6px">
      <button class="primary" id="send">Send</button>
      <button id="refresh">Refresh</button>
    </div>
    <div id="log"></div>
  </section>
  <section class="card">
    <h2>Matrix</h2>
    <div id="svg-wrap"><svg id="matrix" viewBox="0 0 640 420"></svg></div>
    <h2 style="margin-top:10px">Your vision</h2>
    <div class="pattern" id="user-pattern">—</div>
    <div id="user-seen"></div>
    <h2 style="margin-top:10px">AI vision + doing</h2>
    <div class="pattern" id="ai-pattern">—</div>
    <div id="ai-seen"></div>
  </section>
  <section class="card">
    <h2>Nursery</h2>
    <div id="nursery"></div>
    <h2 style="margin-top:12px">User</h2>
    <div id="user-pos" class="meta">—</div>
    <h2 style="margin-top:12px">AI</h2>
    <div id="ai-pos" class="meta">—</div>
    <h2 style="margin-top:12px">Avatar</h2>
    <div id="avatar" class="meta">—</div>
    <h2 style="margin-top:12px">Rings</h2>
    <div id="rings" class="meta">—</div>
  </section>
</div>
<script>
const SKIN={cube:'#5b8def',sphere:'#7c5cbf',seed:'#3cb371',flower:'#e6a817',building:'#c47c48',words:'#888',circle:'#2aa7a0',core:'#d97706'};
const log=t=>document.getElementById('log').textContent=t;
async function getState(){const r=await fetch('/state');return r.json()}
async function sendCmd(cmd){
  log('→ '+cmd);
  const r=await fetch('/cmd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({cmd})});
  const data=await r.json();
  if(data.ok){log('✓ '+(data.msg||cmd));render(data.state||await getState())}
  else{log('✗ '+(data.error||'failed'));if(data.state)render(data.state)}
}
function renderVision(elId,patId,vision,prefix){
  const box=document.getElementById(elId); const pat=document.getElementById(patId);
  if(!vision){box.innerHTML='';pat.textContent='—';return}
  const p=vision.pattern||{};
  pat.textContent=`facing ${vision.facing} · see ${p.count||0} · skins ${JSON.stringify(p.skins||{})} · avg score ${p.avg_score||0} · nearest ${p.nearest||'—'}`;
  box.innerHTML='';
  (vision.nodes||[]).forEach(n=>{
    const d=document.createElement('div');d.className='seen';
    d.innerHTML=`<div><b>${n.label}</b> <span class="d">${n.skin} · d=${n.dist} · sc=${n.score||0}</span></div>
      <div class="d">${n.words||''}</div>
      <button data-act="confirm ${n.id}" style="margin-top:3px">Confirm</button>
      <button data-act="create an idea called seen_${(n.label||'x').slice(0,12)}">Note</button>`;
    box.appendChild(d);
  });
  if(vision.sees_other){
    const o=vision.sees_other;
    const d=document.createElement('div');d.className='seen';
    d.innerHTML=`<div><b>sees ${o.name}</b> <span class="d">d=${o.dist} face ${o.facing} doing ${o.doing||'?'}</span></div>
      <div class="d">${o.last_action||''}</div>`;
    box.appendChild(d);
  }
  if(!(vision.nodes||[]).length && !vision.sees_other)box.innerHTML='<span class="meta">Nothing in view</span>';
  box.querySelectorAll('[data-act]').forEach(b=>b.onclick=()=>sendCmd(b.getAttribute('data-act')));
}
function render(s){
  if(!s)return;
  document.getElementById('meta').textContent=`owner=${s.owner||'?'} · ideas=${s.ideas??0} · form=${s.form||'?'}`;
  const svg=document.getElementById('matrix');
  const W=640,H=420,cx=W/2,cy=H/2,scale=48;
  let maxR=2;
  (s.nodes||[]).forEach(n=>{const r=Math.hypot(n.x,n.y);if(r>maxR)maxR=r});
  const user=s.user||{}, ai=s.ai||{};
  if(user.pos){const r=Math.hypot(user.pos[0]||0,user.pos[1]||0);if(r>maxR)maxR=r}
  if(ai.pos){const r=Math.hypot(ai.pos[0]||0,ai.pos[1]||0);if(r>maxR)maxR=r}
  if(maxR<2)maxR=2;
  const map=(x,y)=>[cx+(x/maxR)*scale*3.2, cy-(y/maxR)*scale*3.2];
  let els=`<rect width="100%" height="100%" fill="#0f1115" rx="8"/>`;
  els+=`<text x="12" y="18" fill="#5c6575" font-size="11">form=${s.form||'?'} · vision cones active</text>`;
  (s.nodes||[]).forEach(n=>{
    const [x,y]=map(n.x,n.y); const col=SKIN[n.skin]||'#5b8def'; const r=n.sandboxed?11:15;
    if(['sphere','circle','seed','flower','core'].includes(n.skin))
      els+=`<circle cx="${x}" cy="${y}" r="${r}" fill="${col}" opacity="0.9" data-id="${n.id}" style="cursor:pointer"/>`;
    else els+=`<rect x="${x-r}" y="${y-r}" width="${r*2}" height="${r*2}" rx="3" fill="${col}" opacity="0.9" data-id="${n.id}" style="cursor:pointer"/>`;
    els+=`<text x="${x}" y="${y+r+11}" text-anchor="middle" class="node-label">${(n.label||'').slice(0,12)}</text>`;
  });
  if(user.pos){const [ux,uy]=map(user.pos[0]||0,user.pos[1]||0);
    els+=`<circle cx="${ux}" cy="${uy}" r="10" fill="#38bdf8" stroke="#fff" stroke-width="2"/>`;
    els+=`<text x="${ux}" y="${uy-14}" text-anchor="middle" fill="#38bdf8" font-size="11" font-weight="600">YOU</text>`;
    els+=`<text x="${ux}" y="${uy+4}" text-anchor="middle" fill="#0f1115" font-size="9">${(user.facing||'N').slice(0,2)}</text>`;}
  if(ai.pos){const [ax,ay]=map(ai.pos[0]||0,ai.pos[1]||0);
    els+=`<circle cx="${ax}" cy="${ay}" r="10" fill="#e879f9" stroke="#fff" stroke-width="2"/>`;
    els+=`<text x="${ax}" y="${ay-14}" text-anchor="middle" fill="#e879f9" font-size="11" font-weight="600">AI</text>`;
    els+=`<text x="${ax}" y="${ay+4}" text-anchor="middle" fill="#0f1115" font-size="9">${(ai.facing||'N').slice(0,2)}</text>`;}
  svg.innerHTML=els;
  svg.querySelectorAll('[data-id]').forEach(el=>{
    el.addEventListener('click',()=>{
      const id=el.getAttribute('data-id'); const n=(s.nodes||[]).find(x=>x.id===id);
      if(!n)return; document.getElementById('cmd').value='confirm '+n.id;
    });
  });
  renderVision('user-seen','user-pattern',s.user_vision,'user');
  renderVision('ai-seen','ai-pattern',s.ai_vision,'ai');
  // also show AI doing in pattern line
  if(s.ai){const ap=document.getElementById('ai-pattern');
    ap.textContent=(ap.textContent||'')+` · AI doing: ${s.ai.doing||'idle'} · ${s.ai.last_action||''}`;
  }
  const nur=document.getElementById('nursery');nur.innerHTML='';
  (s.nursery||[]).forEach(p=>{
    const d=document.createElement('div');d.className='proposal';
    d.innerHTML=`<div class="aff">aff ${(p.affinity||0).toFixed(3)} · ${p.kind||''}</div><div>${p.label||''}</div>
      <div style="margin-top:4px"><button data-c="${p.id||''}">Confirm</button> <button data-r="${p.id||''}" class="warn">Reject</button></div>`;
    nur.appendChild(d);
  });
  if(!(s.nursery||[]).length)nur.innerHTML='<span class="meta">Nursery empty</span>';
  nur.querySelectorAll('[data-c]').forEach(b=>b.onclick=()=>sendCmd('confirm '+b.getAttribute('data-c')));
  nur.querySelectorAll('[data-r]').forEach(b=>b.onclick=()=>sendCmd('reject '+b.getAttribute('data-r')));
  document.getElementById('user-pos').textContent=`pos ${JSON.stringify(user.pos||[0,0])} · face ${user.facing||'?'} · ${user.posture||''} ${user.locomotion||''}`;
  document.getElementById('ai-pos').textContent=`pos ${JSON.stringify(ai.pos||[0,0])} · face ${ai.facing||'?'} · ${ai.doing||''} · ${ai.last_action||''}`;
  const av=s.avatar||{};
  document.getElementById('avatar').textContent=(av.look||'')+'  '+(av.describe||'—');
  document.getElementById('rings').textContent=(s.rings||[]).join(' → ')||'—';
}
document.getElementById('send').onclick=()=>{const c=document.getElementById('cmd').value.trim();if(c)sendCmd(c)};
document.getElementById('cmd').addEventListener('keydown',e=>{if(e.key==='Enter')document.getElementById('send').click()});
document.getElementById('refresh').onclick=async()=>{render(await getState());log('refreshed')};
document.querySelectorAll('[data-cmd]').forEach(b=>b.onclick=()=>sendCmd(b.getAttribute('data-cmd')));
getState().then(render).catch(e=>log('connect failed: '+e));
setInterval(async()=>{if(document.getElementById('auto').checked){try{render(await getState())}catch(e){}}},2000);
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
        "note": "Look around. See patterns. See what AI sees and does. Act on it.",
        "stop": "Process exit stops the server.",
    }


def smoke() -> bool:
    print("=== LIVE VISUAL SMOKE ===")
    try:
        from form.open import open_program
        p = open_program("LiveSmoke")
        p.place("a", "Alpha", words="test", x=1, y=2)
        st = _state_payload(p)
        assert "user_vision" in st and "ai_vision" in st
        print("[PASS] vision in state")
        out = _run_command(p, "look")
        assert out.get("ok") is True
        print("[PASS] look")
        out = _run_command(p, "ai look")
        assert out.get("ok") is True
        print("[PASS] ai look")
        print("=== RESULT: PASS ===")
        return True
    except Exception as e:
        print("[FAIL]", e)
        return False


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
