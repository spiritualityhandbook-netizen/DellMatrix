#!/usr/bin/env python3
"""
Live two-way visual bridge — localhost only.

DellMatrix enhances itself: the panel both shows state and sends commands
that execute on the live Program, then returns fresh state.

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

# Late imports to avoid circulars at module load

_HOST = "127.0.0.1"
_DEFAULT_PORT = 8765


def _state_payload(program) -> Dict[str, Any]:
    """Full live state for the panel."""
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
        "floor": list(getattr(program, "FLOOR", ["Alpha", "Delta", "Omega", "Omni"])),
    }


def _run_command(program, cmd: str) -> Dict[str, Any]:
    """Execute one command through the same path the REPL uses."""
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
            # side-effect messages ignored in live mode; state is truth
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
            # quiet
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
                # plain text body
                cmd = raw.strip()
            result = _run_command(program, cmd)
            self._json(200 if result.get("ok") else 400, result)

        def _serve_ui(self):
            # Minimal live panel that talks to /cmd and /state
            html = _LIVE_HTML
            body = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return LiveHandler


_LIVE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>DellMatrix Live</title>
<style>
  :root { color-scheme: dark; --bg:#0a0b0e; --card:#151820; --line:#2a2f3a; --text:#e8eaed; --muted:#9aa3b2; --accent:#5b8def; --ok:#3cb371; }
  * { box-sizing: border-box; }
  body { margin:0; background:var(--bg); color:var(--text); font-family:system-ui,sans-serif; }
  header { padding:14px 18px; border-bottom:1px solid var(--line); display:flex; gap:12px; align-items:center; justify-content:space-between; flex-wrap:wrap; }
  h1 { margin:0; font-size:17px; }
  .meta { color:var(--muted); font-size:12px; }
  .layout { display:grid; grid-template-columns: 300px 1fr; gap:14px; padding:14px; max-width:1200px; margin:0 auto; }
  @media (max-width:900px){ .layout { grid-template-columns:1fr; } }
  .card { background:var(--card); border:1px solid var(--line); border-radius:12px; padding:14px; }
  h2 { margin:0 0 10px; font-size:12px; color:var(--muted); text-transform:uppercase; letter-spacing:.04em; }
  .btn-row { display:flex; flex-wrap:wrap; gap:8px; margin-bottom:10px; }
  button { background:#1c2230; color:var(--text); border:1px solid var(--line); border-radius:9px; padding:9px 11px; font-size:13px; cursor:pointer; min-height:38px; }
  button:hover { border-color:var(--accent); }
  button.primary { background:var(--accent); color:#fff; border-color:var(--accent); }
  #cmd { width:100%; background:#0f1115; border:1px solid var(--line); border-radius:8px; color:#7dd3a0; padding:10px; font-family:ui-monospace,monospace; font-size:14px; }
  #log { font-size:12px; color:var(--muted); min-height:40px; margin-top:8px; white-space:pre-wrap; }
  .node { display:inline-block; margin:4px; padding:8px 10px; border-radius:8px; background:#1c2230; border:1px solid var(--line); font-size:13px; cursor:pointer; }
  .node:hover { border-color:var(--accent); }
  .proposal { border:1px solid var(--line); border-radius:8px; padding:8px 10px; margin-bottom:8px; font-size:13px; }
  .aff { color:var(--accent); font-size:11px; }
  .ok { color:var(--ok); }
</style>
</head>
<body>
<header>
  <div>
    <h1>DellMatrix Live</h1>
    <div class="meta" id="meta">connecting…</div>
  </div>
  <div class="meta">localhost only · two-way · Floor locked</div>
</header>
<div class="layout">
  <section class="card">
    <h2>Command</h2>
    <div class="btn-row">
      <button type="button" data-cmd="create an idea called live_seed">Create</button>
      <button type="button" data-cmd="grow ideas 1">Grow</button>
      <button type="button" data-cmd="proposals">Proposals</button>
      <button type="button" data-cmd="confirm all">Confirm all</button>
      <button type="button" data-cmd="sphere">Sphere</button>
      <button type="button" data-cmd="status">Status</button>
      <button type="button" data-cmd="save">Save</button>
    </div>
    <input id="cmd" placeholder="type any command…" />
    <div class="btn-row" style="margin-top:8px">
      <button class="primary" type="button" id="send">Send</button>
      <button type="button" id="refresh">Refresh state</button>
    </div>
    <div id="log"></div>
  </section>
  <section class="card">
    <h2>Live matrix</h2>
    <div id="nodes"></div>
    <h2 style="margin-top:16px">Nursery</h2>
    <div id="nursery"></div>
    <h2 style="margin-top:16px">Avatar</h2>
    <div id="avatar" class="meta">—</div>
  </section>
</div>
<script>
const log = (t) => { document.getElementById('log').textContent = t; };
async function getState() {
  const r = await fetch('/state');
  return r.json();
}
async function sendCmd(cmd) {
  log('→ ' + cmd);
  const r = await fetch('/cmd', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({cmd})
  });
  const data = await r.json();
  if (data.ok) {
    log('✓ ' + cmd);
    render(data.state || await getState());
  } else {
    log('✗ ' + (data.error || 'failed') + (data.state ? '' : ''));
    if (data.state) render(data.state);
  }
}
function render(s) {
  if (!s) return;
  document.getElementById('meta').textContent =
    `owner=${s.owner || '?'} · ideas=${s.ideas ?? 0} · form=${s.form || '?'} · skin=${s.skin || '?'}`;
  const nodes = document.getElementById('nodes');
  nodes.innerHTML = '';
  (s.nodes || []).forEach(n => {
    const d = document.createElement('div');
    d.className = 'node';
    d.textContent = `${n.label} (${n.skin}) ${n.score ? n.score.toFixed(1) : ''}`;
    d.title = n.id + ' · ' + (n.words || '');
    d.onclick = () => { document.getElementById('cmd').value = 'confirm ' + n.id; };
    nodes.appendChild(d);
  });
  if (!(s.nodes || []).length) nodes.innerHTML = '<span class="meta">No ideas yet — try Create</span>';
  const nur = document.getElementById('nursery');
  nur.innerHTML = '';
  (s.nursery || []).forEach(p => {
    const d = document.createElement('div');
    d.className = 'proposal';
    d.innerHTML = `<div class="aff">aff ${(p.affinity||0).toFixed(3)} · ${p.kind||''} · ${p.id||''}</div>
      <div>${p.label||''}</div>
      <button type="button" style="margin-top:6px" data-confirm="${p.id||''}">Confirm</button>`;
    nur.appendChild(d);
  });
  if (!(s.nursery || []).length) nur.innerHTML = '<span class="meta">Nursery empty</span>';
  nur.querySelectorAll('[data-confirm]').forEach(b => {
    b.onclick = () => sendCmd('confirm ' + b.getAttribute('data-confirm'));
  });
  const av = s.avatar || {};
  document.getElementById('avatar').textContent = (av.look || '') + '  ' + (av.describe || '—');
}
document.getElementById('send').onclick = () => {
  const c = document.getElementById('cmd').value.trim();
  if (c) sendCmd(c);
};
document.getElementById('cmd').addEventListener('keydown', e => {
  if (e.key === 'Enter') document.getElementById('send').click();
});
document.getElementById('refresh').onclick = async () => {
  render(await getState());
  log('state refreshed');
};
document.querySelectorAll('[data-cmd]').forEach(b => {
  b.onclick = () => sendCmd(b.getAttribute('data-cmd'));
});
getState().then(render).catch(e => log('connect failed: ' + e));
</script>
</body>
</html>
"""


def start_live(program, port: int = _DEFAULT_PORT, background: bool = True) -> Dict[str, Any]:
    """Start the live visual server bound to the given Program."""
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
