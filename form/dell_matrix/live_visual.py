#!/usr/bin/env python3
"""
Live two-way visual bridge — localhost only.

Full movement inside the matrix for User (Avatar) and AI companion.
Both positions are drawn on the SVG, both can be moved by commands.

Constraints kept:
- Offline core (127.0.0.1 only)
- Growth still only via Nursery + confirm
- Floor lock untouched
- Snapshot path remains default

Pure stdlib.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple
import json
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

_HOST = "127.0.0.1"
_DEFAULT_PORT = 8765

# Simple AI companion state (per live session)
_AI: Dict[str, Any] = {
    "name": "AI",
    "pos": [2, 1],
    "facing": "N",
    "label": "AI",
}

_FACING_DELTA = {
    "N": (0, 1), "NE": (1, 1), "E": (1, 0), "SE": (1, -1),
    "S": (0, -1), "SW": (-1, -1), "W": (-1, 0), "NW": (-1, 1),
}
_FACING_ORDER = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]


def _ai_step(steps: int = 1) -> Tuple[int, int]:
    dx, dy = _FACING_DELTA.get(_AI["facing"], (0, 1))
    _AI["pos"][0] += dx * steps
    _AI["pos"][1] += dy * steps
    return tuple(_AI["pos"])


def _ai_turn(steps: int = 1) -> str:
    idx = _FACING_ORDER.index(_AI["facing"]) if _AI["facing"] in _FACING_ORDER else 0
    _AI["facing"] = _FACING_ORDER[(idx + steps) % 8]
    return _AI["facing"]


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
    # Ensure body pos is exposed
    body = {}
    if hasattr(program, "avatar") and hasattr(program.avatar, "body"):
        b = program.avatar.body
        body = {
            "pos": list(b.pos) if hasattr(b, "pos") else [0, 0],
            "facing": b.facing.name if hasattr(b.facing, "name") else str(b.facing),
            "posture": b.posture.name.lower() if hasattr(b.posture, "name") else "stand",
            "locomotion": b.locomotion.name.lower() if hasattr(b.locomotion, "name") else "idle",
        }
    lat = program.lattice.status() if hasattr(program, "lattice") else {}
    return {
        "ok": True,
        "owner": program.owner,
        "ideas": len(plane.units),
        "nodes": nodes,
        "nursery": nursery[:20],
        "avatar": avatar,
        "user": body,
        "ai": {
            "name": _AI["name"],
            "pos": list(_AI["pos"]),
            "facing": _AI["facing"],
            "label": _AI["label"],
        },
        "form": lat.get("form", "cube"),
        "skin": lat.get("skin", "cube"),
        "rings": list(getattr(program.duo, "rings", [])),
        "history_len": len(getattr(program, "history", [])),
        "floor": ["Alpha", "Delta", "Omega", "Omni"],
    }


def _handle_ai_command(cmd: str) -> Optional[Dict[str, Any]]:
    """Handle ai-specific movement commands. Returns None if not an AI cmd."""
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
            return {"ok": True, "msg": f"AI facing {d}"}
        return {"ok": False, "error": f"unknown facing {d}"}
    if rest in ("status", "where", "pos"):
        return {"ok": True, "msg": f"AI at {_AI['pos']} facing {_AI['facing']}"}
    if rest.startswith("goto ") or rest.startswith("move "):
        parts = rest.split()
        try:
            x, y = int(parts[1]), int(parts[2])
            _AI["pos"] = [x, y]
            return {"ok": True, "msg": f"AI moved to {[x, y]}"}
        except Exception:
            return {"ok": False, "error": "usage: ai goto X Y"}
    return {"ok": False, "error": f"unknown ai command: {rest}"}


def _run_command(program, cmd: str) -> Dict[str, Any]:
    cmd = (cmd or "").strip()
    if not cmd:
        return {"ok": False, "error": "empty command"}

    # AI movement first
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
.layout{display:grid;grid-template-columns:280px 1fr 260px;gap:12px;padding:12px;max-width:1400px;margin:0 auto}
@media(max-width:1000px){.layout{grid-template-columns:1fr}}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px}
h2{margin:0 0 8px;font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}
.btn-row{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px}
button{background:#1c2230;color:var(--text);border:1px solid var(--line);border-radius:8px;padding:8px 10px;font-size:12px;cursor:pointer;min-height:34px}
button:hover{border-color:var(--accent)}button.primary{background:var(--accent);color:#fff;border-color:var(--accent)}
button.ok{border-color:var(--ok)}button.warn{border-color:var(--warn)}
button.user{border-color:var(--user)}button.ai{border-color:var(--ai)}
#cmd{width:100%;background:#0f1115;border:1px solid var(--line);border-radius:8px;color:#7dd3a0;padding:9px;font-family:ui-monospace,monospace;font-size:13px}
#log{font-size:11px;color:var(--muted);min-height:28px;margin-top:6px;white-space:pre-wrap}
#svg-wrap{width:100%;overflow:auto;background:#0f1115;border-radius:10px;border:1px solid var(--line)}
svg{display:block;width:100%;height:auto}
.node-label{font-size:11px;fill:#e8eaed}
.detail .k{color:var(--muted);font-size:10px;margin-top:6px}.detail .v{font-size:12px;word-break:break-word}
.proposal{border:1px solid var(--line);border-radius:8px;padding:8px;margin-bottom:6px;font-size:12px}
.aff{color:var(--accent);font-size:10px}
</style>
</head>
<body>
<header>
  <div><h1>DellMatrix Live</h1><div class="meta" id="meta">connecting…</div></div>
  <div class="meta">localhost · User + AI movement · Floor locked · <label><input type="checkbox" id="auto" checked> auto 2s</label></div>
</header>
<div class="layout">
  <section class="card">
    <h2>Actions</h2>
    <div class="btn-row">
      <button data-cmd="create an idea called live_seed">Create</button>
      <button data-cmd="grow ideas 1">Grow</button>
      <button data-cmd="confirm all" class="ok">Confirm all</button>
      <button data-cmd="reject all" class="warn">Reject all</button>
    </div>
    <div class="btn-row">
      <button data-cmd="cube">Cube</button>
      <button data-cmd="sphere">Sphere</button>
      <button data-cmd="core">Core</button>
      <button data-cmd="flower">Flower</button>
      <button data-cmd="lattice">Lattice</button>
    </div>
    <h2>User movement</h2>
    <div class="btn-row">
      <button class="user" data-cmd="walk forward">Walk</button>
      <button class="user" data-cmd="turn left">← Turn</button>
      <button class="user" data-cmd="turn right">Turn →</button>
      <button class="user" data-cmd="face north">Face N</button>
      <button class="user" data-cmd="sit down">Sit</button>
      <button class="user" data-cmd="stand up">Stand</button>
    </div>
    <h2>AI movement</h2>
    <div class="btn-row">
      <button class="ai" data-cmd="ai walk">AI Walk</button>
      <button class="ai" data-cmd="ai turn left">AI ←</button>
      <button class="ai" data-cmd="ai turn right">AI →</button>
      <button class="ai" data-cmd="ai face N">AI Face N</button>
      <button class="ai" data-cmd="ai status">AI Pos</button>
    </div>
    <div class="btn-row">
      <button data-cmd="enhance on">Enhance</button>
      <button data-cmd="pulse">Pulse</button>
      <button data-cmd="smile">Smile</button>
      <button data-cmd="save">Save</button>
      <button data-cmd="status">Status</button>
    </div>
    <input id="cmd" placeholder="any command… (ai walk 2 · ai goto 3 4)"/>
    <div class="btn-row" style="margin-top:6px">
      <button class="primary" id="send">Send</button>
      <button id="refresh">Refresh</button>
    </div>
    <div id="log"></div>
  </section>
  <section class="card">
    <h2>Matrix</h2>
    <div id="svg-wrap"><svg id="matrix" viewBox="0 0 640 420"></svg></div>
    <div class="detail" id="detail" style="margin-top:10px">
      <h2 style="margin:0">Selected</h2>
      <div class="k">label</div><div class="v" id="d-label">—</div>
      <div class="k">id</div><div class="v" id="d-id">—</div>
      <div class="k">skin / score</div><div class="v" id="d-skin">—</div>
      <div class="k">words</div><div class="v" id="d-words">—</div>
    </div>
  </section>
  <section class="card">
    <h2>Nursery</h2>
    <div id="nursery"></div>
    <h2 style="margin-top:12px">User</h2>
    <div id="user-pos" class="meta">—</div>
    <h2 style="margin-top:12px">AI</h2>
    <div id="ai-pos" class="meta">—</div>
    <h2 style="margin-top:12px">Avatar look</h2>
    <div id="avatar" class="meta">—</div>
    <h2 style="margin-top:12px">Rings</h2>
    <div id="rings" class="meta">—</div>
  </section>
</div>
<script>
const SKIN={cube:'#5b8def',sphere:'#7c5cbf',seed:'#3cb371',flower:'#e6a817',building:'#c47c48',words:'#888',circle:'#2aa7a0',core:'#d97706'};
const log=t=>document.getElementById('log').textContent=t;
let lastState=null;
async function getState(){const r=await fetch('/state');return r.json()}
async function sendCmd(cmd){
  log('→ '+cmd);
  const r=await fetch('/cmd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({cmd})});
  const data=await r.json();
  if(data.ok){log('✓ '+(data.msg||cmd));render(data.state||await getState())}
  else{log('✗ '+(data.error||'failed'));if(data.state)render(data.state)}
}
function render(s){
  if(!s)return; lastState=s;
  document.getElementById('meta').textContent=`owner=${s.owner||'?'} · ideas=${s.ideas??0} · form=${s.form||'?'} · hist=${s.history_len??0}`;
  const svg=document.getElementById('matrix');
  const W=640,H=420,cx=W/2,cy=H/2,scale=48;
  let maxR=2;
  (s.nodes||[]).forEach(n=>{const r=Math.hypot(n.x,n.y);if(r>maxR)maxR=r});
  const user=s.user||{}; const ai=s.ai||{};
  if(user.pos){const r=Math.hypot(user.pos[0]||0,user.pos[1]||0);if(r>maxR)maxR=r}
  if(ai.pos){const r=Math.hypot(ai.pos[0]||0,ai.pos[1]||0);if(r>maxR)maxR=r}
  if(maxR<2)maxR=2;
  const map=(x,y)=>[cx+(x/maxR)*scale*3.2, cy-(y/maxR)*scale*3.2];
  let els=`<rect width="100%" height="100%" fill="#0f1115" rx="8"/>`;
  els+=`<text x="12" y="18" fill="#5c6575" font-size="11">form=${s.form||'?'} · User+AI movement</text>`;
  // nodes
  (s.nodes||[]).forEach(n=>{
    const [x,y]=map(n.x,n.y);
    const col=SKIN[n.skin]||'#5b8def';
    const r=n.sandboxed?11:15;
    if(['sphere','circle','seed','flower','core'].includes(n.skin))
      els+=`<circle cx="${x}" cy="${y}" r="${r}" fill="${col}" opacity="0.9" data-id="${n.id}" style="cursor:pointer"/>`;
    else
      els+=`<rect x="${x-r}" y="${y-r}" width="${r*2}" height="${r*2}" rx="3" fill="${col}" opacity="0.9" data-id="${n.id}" style="cursor:pointer"/>`;
    els+=`<text x="${x}" y="${y+r+11}" text-anchor="middle" class="node-label">${(n.label||'').slice(0,12)}</text>`;
  });
  // User marker
  if(user.pos){
    const [ux,uy]=map(user.pos[0]||0,user.pos[1]||0);
    els+=`<circle cx="${ux}" cy="${uy}" r="10" fill="#38bdf8" stroke="#fff" stroke-width="2"/>`;
    els+=`<text x="${ux}" y="${uy-14}" text-anchor="middle" fill="#38bdf8" font-size="11" font-weight="600">YOU</text>`;
    els+=`<text x="${ux}" y="${uy+4}" text-anchor="middle" fill="#0f1115" font-size="9">${(user.facing||'N').slice(0,2)}</text>`;
  }
  // AI marker
  if(ai.pos){
    const [ax,ay]=map(ai.pos[0]||0,ai.pos[1]||0);
    els+=`<circle cx="${ax}" cy="${ay}" r="10" fill="#e879f9" stroke="#fff" stroke-width="2"/>`;
    els+=`<text x="${ax}" y="${ay-14}" text-anchor="middle" fill="#e879f9" font-size="11" font-weight="600">AI</text>`;
    els+=`<text x="${ax}" y="${ay+4}" text-anchor="middle" fill="#0f1115" font-size="9">${(ai.facing||'N').slice(0,2)}</text>`;
  }
  if(!(s.nodes||[]).length && !user.pos)els+=`<text x="${cx}" y="${cy}" text-anchor="middle" fill="#9aa3b2" font-size="14">No ideas yet</text>`;
  svg.innerHTML=els;
  svg.querySelectorAll('[data-id]').forEach(el=>{
    el.addEventListener('click',()=>{
      const id=el.getAttribute('data-id');
      const n=(s.nodes||[]).find(x=>x.id===id);
      if(!n)return;
      document.getElementById('d-label').textContent=n.label;
      document.getElementById('d-id').textContent=n.id;
      document.getElementById('d-skin').textContent=`${n.skin} · score ${n.score||0}`;
      document.getElementById('d-words').textContent=n.words||'(empty)';
      document.getElementById('cmd').value='confirm '+n.id;
    });
  });
  // Nursery
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
  // positions
  const u=s.user||{}; const a=s.ai||{};
  document.getElementById('user-pos').textContent=`pos ${JSON.stringify(u.pos||[0,0])} · face ${u.facing||'?'} · ${u.posture||''} ${u.locomotion||''}`;
  document.getElementById('ai-pos').textContent=`pos ${JSON.stringify(a.pos||[0,0])} · face ${a.facing||'?'} · ${a.label||'AI'}`;
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

    url = f"http://{_HOST}:{port}/"
    return {
        "ok": True,
        "url": url,
        "host": _HOST,
        "port": port,
        "note": "Open the URL. User (Avatar) + AI both move on the matrix. Offline localhost only.",
        "stop": "Process exit stops the server.",
    }


def smoke() -> bool:
    print("=== LIVE VISUAL SMOKE ===")
    try:
        from form.open import open_program
        p = open_program("LiveSmoke")
        p.place("a", "Alpha", words="test")
        st = _state_payload(p)
        assert st["ideas"] >= 1
        assert "user" in st and "ai" in st
        print("[PASS] state + user/ai")
        out = _run_command(p, "ai walk")
        assert out.get("ok") is True
        print("[PASS] ai walk")
        print("=== RESULT: PASS ===")
        return True
    except Exception as e:
        print("[FAIL]", e)
        return False


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
