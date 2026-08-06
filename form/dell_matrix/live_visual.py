#!/usr/bin/env python3
"""
Live two-way visual bridge — localhost only.

Enhanced panel: SVG matrix from node positions, skin colors, more actions,
node detail, nursery reject, auto-refresh, clearer feedback.

Constraints kept:
- Offline core (127.0.0.1 only)
- Growth still only via Nursery + confirm
- Floor lock untouched
- Snapshot path remains the default; this is opt-in via `live` / `visual live`

Pure stdlib (http.server). No extra dependencies.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
import json
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

_HOST = "127.0.0.1"
_DEFAULT_PORT = 8765


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
    lat = program.lattice.status() if hasattr(program, "lattice") else {}
    return {
        "ok": True,
        "owner": program.owner,
        "ideas": len(plane.units),
        "nodes": nodes,
        "nursery": nursery[:20],
        "avatar": avatar,
        "form": lat.get("form", "cube"),
        "skin": lat.get("skin", "cube"),
        "rings": list(getattr(program.duo, "rings", [])),
        "history_len": len(getattr(program, "history", [])),
        "floor": ["Alpha", "Delta", "Omega", "Omni"],
    }


def _run_command(program, cmd: str) -> Dict[str, Any]:
    cmd = (cmd or "").strip()
    if not cmd:
        return {"ok": False, "error": "empty command"}
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
:root{color-scheme:dark;--bg:#0a0b0e;--card:#151820;--line:#2a2f3a;--text:#e8eaed;--muted:#9aa3b2;--accent:#5b8def;--ok:#3cb371;--warn:#e6a817}
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
#cmd{width:100%;background:#0f1115;border:1px solid var(--line);border-radius:8px;color:#7dd3a0;padding:9px;font-family:ui-monospace,monospace;font-size:13px}
#log{font-size:11px;color:var(--muted);min-height:28px;margin-top:6px;white-space:pre-wrap}
#svg-wrap{width:100%;overflow:auto;background:#0f1115;border-radius:10px;border:1px solid var(--line)}
svg{display:block;width:100%;height:auto}
.node-label{font-size:11px;fill:#e8eaed}
.detail .k{color:var(--muted);font-size:10px;margin-top:6px}.detail .v{font-size:12px;word-break:break-word}
.proposal{border:1px solid var(--line);border-radius:8px;padding:8px;margin-bottom:6px;font-size:12px}
.aff{color:var(--accent);font-size:10px}
.chip{display:inline-block;padding:2px 6px;border-radius:6px;font-size:10px;margin-right:4px}
</style>
</head>
<body>
<header>
  <div><h1>DellMatrix Live</h1><div class="meta" id="meta">connecting…</div></div>
  <div class="meta">localhost · two-way · Floor locked · <label><input type="checkbox" id="auto" checked> auto 2s</label></div>
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
    <div class="btn-row">
      <button data-cmd="enhance on">Enhance ON</button>
      <button data-cmd="pulse">Pulse</button>
      <button data-cmd="walk forward">Walk</button>
      <button data-cmd="smile">Smile</button>
      <button data-cmd="save">Save</button>
      <button data-cmd="status">Status</button>
    </div>
    <input id="cmd" placeholder="any command…"/>
    <div class="btn-row" style="margin-top:6px">
      <button class="primary" id="send">Send</button>
      <button id="refresh">Refresh</button>
    </div>
    <div id="log"></div>
  </section>
  <section class="card">
    <h2>Matrix</h2>
    <div id="svg-wrap"><svg id="matrix" viewBox="0 0 640 400"></svg></div>
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
    <h2 style="margin-top:12px">Avatar</h2>
    <div id="avatar" class="meta">—</div>
    <h2 style="margin-top:12px">Rings</h2>
    <div id="rings" class="meta">—</div>
  </section>
</div>
<script>
const SKIN = {cube:'#5b8def',sphere:'#7c5cbf',seed:'#3cb371',flower:'#e6a817',building:'#c47c48',words:'#888',circle:'#2aa7a0',core:'#d97706'};
const log = t => document.getElementById('log').textContent = t;
let lastState = null;
async function getState(){const r=await fetch('/state');return r.json()}
async function sendCmd(cmd){
  log('→ '+cmd);
  const r=await fetch('/cmd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({cmd})});
  const data=await r.json();
  if(data.ok){log('✓ '+cmd);render(data.state||await getState())}
  else{log('✗ '+(data.error||'failed'));if(data.state)render(data.state)}
}
function render(s){
  if(!s)return; lastState=s;
  document.getElementById('meta').textContent=`owner=${s.owner||'?'} · ideas=${s.ideas??0} · form=${s.form||'?'} · skin=${s.skin||'?'} · hist=${s.history_len??0}`;
  // SVG matrix
  const svg=document.getElementById('matrix');
  const W=640,H=400,cx=W/2,cy=H/2,scale=55;
  let maxR=1;
  (s.nodes||[]).forEach(n=>{const r=Math.hypot(n.x,n.y);if(r>maxR)maxR=r});
  if(maxR<1)maxR=1;
  let els=`<rect width="100%" height="100%" fill="#0f1115" rx="8"/>`;
  els+=`<text x="12" y="20" fill="#5c6575" font-size="11">form=${s.form||'?'} · Floor locked</text>`;
  (s.nodes||[]).forEach(n=>{
    const x=cx+(n.x/maxR)*scale*3, y=cy-(n.y/maxR)*scale*3;
    const col=SKIN[n.skin]||'#5b8def';
    const r=n.sandboxed?12:16;
    if(['sphere','circle','seed','flower','core'].includes(n.skin))
      els+=`<circle cx="${x}" cy="${y}" r="${r}" fill="${col}" opacity="0.9" data-id="${n.id}" style="cursor:pointer"/>`;
    else
      els+=`<rect x="${x-r}" y="${y-r}" width="${r*2}" height="${r*2}" rx="4" fill="${col}" opacity="0.9" data-id="${n.id}" style="cursor:pointer"/>`;
    els+=`<text x="${x}" y="${y+r+12}" text-anchor="middle" class="node-label">${(n.label||'').slice(0,14)}</text>`;
    if(n.score>0)els+=`<text x="${x}" y="${y+4}" text-anchor="middle" fill="#0f1115" font-size="10" font-weight="600">${n.score.toFixed(1)}</text>`;
  });
  if(!(s.nodes||[]).length)els+=`<text x="${cx}" y="${cy}" text-anchor="middle" fill="#9aa3b2" font-size="14">No ideas yet</text>`;
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
  const nur=document.getElementById('nursery');
  nur.innerHTML='';
  (s.nursery||[]).forEach(p=>{
    const d=document.createElement('div');d.className='proposal';
    d.innerHTML=`<div class="aff">aff ${(p.affinity||0).toFixed(3)} · ${p.kind||''}</div>
      <div>${p.label||''}</div>
      <div style="margin-top:4px">
        <button data-c="${p.id||''}">Confirm</button>
        <button data-r="${p.id||''}" class="warn">Reject</button>
      </div>`;
    nur.appendChild(d);
  });
  if(!(s.nursery||[]).length)nur.innerHTML='<span class="meta">Nursery empty</span>';
  nur.querySelectorAll('[data-c]').forEach(b=>b.onclick=()=>sendCmd('confirm '+b.getAttribute('data-c')));
  nur.querySelectorAll('[data-r]').forEach(b=>b.onclick=()=>sendCmd('reject '+b.getAttribute('data-r')));
  const av=s.avatar||{};
  document.getElementById('avatar').textContent=(av.look||'')+'  '+(av.describe||'—');
  document.getElementById('rings').textContent=(s.rings||[]).join(' → ')||'—';
}
document.getElementById('send').onclick=()=>{const c=document.getElementById('cmd').value.trim();if(c)sendCmd(c)};
document.getElementById('cmd').addEventListener('keydown',e=>{if(e.key==='Enter')document.getElementById('send').click()});
document.getElementById('refresh').onclick=async()=>{render(await getState());log('refreshed')};
document.querySelectorAll('[data-cmd]').forEach(b=>b.onclick=()=>sendCmd(b.getAttribute('data-cmd')));
getState().then(render).catch(e=>log('connect failed: '+e));
setInterval(async()=>{
  if(document.getElementById('auto').checked){
    try{render(await getState())}catch(e){}
  }
},2000);
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
        "note": "Open the URL in a browser. Commands execute on this live Program. Offline localhost only.",
        "stop": "Process exit stops the server (daemon thread).",
    }


def smoke() -> bool:
    print("=== LIVE VISUAL SMOKE ===")
    try:
        from form.open import open_program
        p = open_program("LiveSmoke")
        p.place("a", "Alpha", words="test")
        st = _state_payload(p)
        assert st["ideas"] >= 1
        print("[PASS] state payload")
        out = _run_command(p, "status")
        assert out.get("ok") is True
        print("[PASS] run command")
        print("=== RESULT: PASS ===")
        return True
    except Exception as e:
        print("[FAIL]", e)
        return False


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
