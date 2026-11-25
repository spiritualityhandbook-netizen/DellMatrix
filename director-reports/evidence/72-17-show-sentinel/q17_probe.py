#!/usr/bin/env python3
"""72-17 probe: where does the bare-Show literal '__RENDER__' reach a user?

Surfaces:
  S1 front door (in-process API): execute_seed bare 09[Show] + labeled
     controls (lattice / avatar).
  S2 REPL (cross-process, real user path): piped session; the user must
     see the render board, never the sentinel.
  S3 Studio server (cross-process): POST /api/execute bare 09[Show];
     the JSON payload the frontend dumps verbatim into its console
     (gui/static/app.js execute(): logConsole(JSON.stringify(result))).
  S4 chain (in-process): sentinel passthrough inside a chain result.

Exit 0 = all surface verdicts as classified; 1 = a verdict differs;
2 = setup failure (inconclusive, never a pass).
"""
import json
import os
import subprocess
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

fails = []


def check(name, cond, detail):
    print(('PASS ' if cond else 'FAIL ') + name + ' :: ' + detail)
    if not cond:
        fails.append(name)


# ---------- S1: front door ----------
try:
    from form.open import Program
    from form.mandell.executor import execute_seed
    p = Program(owner='Q17PROBE')
    r = execute_seed(p, '09[Show]')
    msgs = r.get('messages') or []
    check('S1.bare_show_sentinel', '__RENDER__' in msgs,
          f'messages={msgs!r} ok={r.get("ok")}')
    r2 = execute_seed(p, '09[Show]:: lattice')
    check('S1.lattice_control', '__RENDER__' not in ' '.join(r2.get('messages') or []),
          f'lattice messages head={(r2.get("messages") or [""])[0][:40]!r}')
    r3 = execute_seed(p, '09[Show]:: avatar')
    check('S1.avatar_control', '__RENDER__' not in ' '.join(r3.get('messages') or []),
          f'avatar messages={(r3.get("messages") or [])!r}')
except Exception as exc:
    print(f'SETUP_FAILED S1: {type(exc).__name__}: {exc}')
    sys.exit(2)

# ---------- S2: REPL cross-process ----------
try:
    session = '08[Create]:: probeidea\n09[Show]\n'
    cp = subprocess.run([sys.executable, '-m', 'form.repl', '--owner', 'Q17REPL'],
                        input=session, capture_output=True, text=True, timeout=120)
    out = cp.stdout + cp.stderr
    check('S2.repl_no_sentinel', '__RENDER__' not in out,
          'sentinel absent from REPL stdout' if '__RENDER__' not in out
          else 'SENTINEL LEAKED INTO REPL OUTPUT')
    check('S2.repl_render_shown', 'DellMatrix · owner=Q17REPL' in out,
          'render board header present' if 'DellMatrix · owner=Q17REPL' in out
          else 'render board NOT found in REPL output')
except Exception as exc:
    print(f'SETUP_FAILED S2: {type(exc).__name__}: {exc}')
    sys.exit(2)

# ---------- S3: Studio server cross-process ----------
port = 8971
srv = None
try:
    srv = subprocess.Popen([sys.executable, 'gui/server.py', '--port', str(port),
                            '--owner', 'Q17STUDIO'],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    deadline = time.time() + 30
    up = False
    while time.time() < deadline:
        try:
            urllib.request.urlopen(f'http://127.0.0.1:{port}/', timeout=2)
            up = True
            break
        except Exception:
            if srv.poll() is not None:
                break
            time.sleep(0.5)
    if not up:
        print('SETUP_FAILED S3: studio server did not come up')
        sys.exit(2)
    # Browser-faithful session bootstrap: the token is served only
    # inside the index page (meta tag); the frontend sends it back
    # as X-Studio-Token on POSTs. Do exactly that.
    with urllib.request.urlopen(f'http://127.0.0.1:{port}/', timeout=5) as resp:
        html = resp.read().decode()
    import re as _re
    m = _re.search(r'name="studio-token"\s+content="([^"]+)"', html)
    if not m:
        print('SETUP_FAILED S3: studio-token meta not found in served page')
        sys.exit(2)
    req = urllib.request.Request(
        f'http://127.0.0.1:{port}/api/execute',
        data=json.dumps({'seed': '09[Show]', 'owner': 'Q17STUDIO'}).encode(),
        headers={'Content-Type': 'application/json',
                 'X-Studio-Token': m.group(1)}, method='POST')
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())
    msgs = (data.get('result') or {}).get('messages') or []
    check('S3.studio_payload_carries_sentinel', '__RENDER__' in msgs,
          f'/api/execute result.messages={msgs!r} (frontend dumps this JSON verbatim: app.js execute())')
finally:
    if srv is not None:
        srv.terminate()
        try:
            srv.wait(timeout=10)
        except Exception:
            srv.kill()

# ---------- S4: chain passthrough ----------
try:
    p4 = Program(owner='Q17CHAIN')
    r4 = execute_seed(p4, '08[Create]:: chainidea > 09[Show]')
    msgs4 = r4.get('messages') or []
    check('S4.chain_carries_sentinel', '__RENDER__' in msgs4,
          f'chain messages={msgs4!r}')
except Exception as exc:
    print(f'SETUP_FAILED S4: {type(exc).__name__}: {exc}')
    sys.exit(2)

print()
if fails:
    print('PROBE RESULT: verdicts differ on: ' + ', '.join(fails))
    sys.exit(1)
print('PROBE RESULT: classification holds on every surface probed.')
