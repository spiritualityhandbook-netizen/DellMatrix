#!/usr/bin/env python3
"""72-17 browser probe: is '__RENDER__' visible in the REAL Studio UI?

Drives headless Chromium over CDP against the real Studio server —
the same machinery and realism class as gui/browser_acceptance.py
(AUTOMATED BROWSER (CDP): genuine Chromium, real DOM, real input
events; NOT a human session). The driver sends ZERO HTTP requests
to the app API; every app request is issued by the page's own
app.js carrying the per-launch session token, exactly as a user's
browser does.

Flow: load page -> type a CONTROL seed (55[Set]>>56[Get]) into
#seed-editor with real input -> click RUN with real mouse events
-> bounded-poll the user-visible #console-log -> then the same
with the bare Show seed 09[Show].

Assertions:
  B1 the control run's console dump does NOT contain __RENDER__
  B2 the bare-Show run's console dump DOES contain __RENDER__
     (browser presentation, not API transport)
  B3 the token meta is a real per-launch token (the authenticated
     path a user takes; a broken token flow fails here)

The Chromium instance is started EXTERNALLY (this probe only
connects to its CDP port), mirroring gui/browser_acceptance.py
and the studio-browser-acceptance workflow. The Studio server
is started by this probe on loopback.

Outputs (this directory): browser_console_log.txt,
browser_screenshot.png, browser_assertions.json.
Exit 0 = all assertions pass; 1 = an assertion differs;
2 = setup failure (inconclusive, never a pass).
Env: Q17_CDP_PORT (default 9444), Q17_PINNED_SHA (recorded
into the assertions file).
"""
import importlib.util
import json
import os
import subprocess
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

_spec = importlib.util.spec_from_file_location(
    'browser_acceptance', os.path.join(ROOT, 'gui', 'browser_acceptance.py'))
_ba = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ba)
WS, CDP = _ba.WS, _ba.CDP

CDP_PORT = int(os.environ.get('Q17_CDP_PORT', '9444'))
PAGE_PORT = 8973
PAGE_URL = f'http://127.0.0.1:{PAGE_PORT}/'
PINNED = os.environ.get('Q17_PINNED_SHA', 'unset')

checks = []


def expect(name, cond, detail=''):
    checks.append({'name': name, 'pass': bool(cond), 'detail': str(detail)[:500]})
    print(('PASS ' if cond else 'FAIL ') + name + ' :: ' + str(detail)[:200], flush=True)


def main():
    srv = subprocess.Popen(
        [sys.executable, 'gui/server.py', '--port', str(PAGE_PORT),
         '--owner', 'Q17BROWSER'],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        # --- browser target (bounded wait) ---
        targets, deadline = None, time.time() + 30
        while time.time() < deadline:
            try:
                with urllib.request.urlopen(
                        f'http://127.0.0.1:{CDP_PORT}/json/list', timeout=2) as r:
                    targets = json.loads(r.read().decode())
                break
            except Exception:
                time.sleep(0.25)
        if not targets:
            print('SETUP_FAILED: no CDP targets')
            return 2
        page = next((t for t in targets if t.get('type') == 'page'), None)
        if not page:
            print('SETUP_FAILED: no page target')
            return 2
        cdp = CDP(WS(page['webSocketDebuggerUrl']))
        version = cdp.call('Browser.getVersion').get('product')
        cdp.call('Page.enable')
        cdp.call('Runtime.enable')
        cdp.call('Page.navigate', {'url': PAGE_URL})

        def wait_eval(expr, timeout=25.0):
            dl = time.time() + timeout
            val = None
            while True:
                try:
                    val = cdp.eval(expr)
                except Exception:
                    val = None
                if val:
                    return val
                if time.time() >= dl:
                    return val
                cdp.pump(0.25)

        title = wait_eval("document.title === 'DellMatrix Studio' && document.title")
        if title != 'DellMatrix Studio':
            print('SETUP_FAILED: page did not load the Studio')
            return 2
        token = cdp.eval("(document.querySelector('meta[name=\"studio-token\"]') || {}).content || ''")
        expect('B3.session_token_real', len(token or '') >= 16 and token != '__STUDIO_TOKEN__',
               f'token length={len(token or "")}')
        wait_eval("document.querySelectorAll('#rack > *').length > 0")

        def run_seed(seed):
            before = cdp.eval("document.querySelector('#console-log').textContent.length")
            cdp.eval("document.querySelector('#seed-editor').focus()")
            cdp.eval("document.querySelector('#seed-editor').select()")
            cdp.call('Input.insertText', {'text': seed})
            rect = cdp.eval("JSON.stringify(document.querySelector('#execute-btn').getBoundingClientRect())")
            r = json.loads(rect)
            x, y = r['x'] + r['width'] / 2, r['y'] + r['height'] / 2
            cdp.call('Input.dispatchMouseEvent',
                     {'type': 'mousePressed', 'x': x, 'y': y, 'button': 'left', 'clickCount': 1})
            cdp.call('Input.dispatchMouseEvent',
                     {'type': 'mouseReleased', 'x': x, 'y': y, 'button': 'left', 'clickCount': 1})
            # bounded wait: console grows past `before` and status settles
            dl = time.time() + 30
            while time.time() < dl:
                txt = cdp.eval("document.querySelector('#console-log').textContent") or ''
                status = cdp.eval("document.querySelector('#status-text').textContent") or ''
                if len(txt) > (before or 0) and 'done' in status:
                    return txt
                cdp.pump(0.25)
            return cdp.eval("document.querySelector('#console-log').textContent") or ''

        control_txt = run_seed('55[Set] :: tempo=120 >> 56[Get] :: tempo')
        expect('B1.control_no_sentinel', '__RENDER__' not in control_txt,
               'control dump clean' if '__RENDER__' not in control_txt else 'sentinel in CONTROL run')
        show_txt = run_seed('09[Show]')
        new_part = show_txt[len(control_txt):] if show_txt.startswith(control_txt[:200]) else show_txt
        expect('B2.show_sentinel_visible_in_console', '__RENDER__' in show_txt,
               'sentinel present in user-visible console text after bare 09[Show]'
               if '__RENDER__' in show_txt else 'sentinel NOT in console text')

        with open(os.path.join(HERE, 'browser_console_log.txt'), 'w') as f:
            f.write(show_txt)
        shot = cdp.call('Page.captureScreenshot', {'format': 'png'})
        import base64 as _b64
        with open(os.path.join(HERE, 'browser_screenshot.png'), 'wb') as f:
            f.write(_b64.b64decode(shot['data']))
        meta = {'browser': version, 'python': sys.version.split()[0],
                'pinned_sha': PINNED, 'page_url': PAGE_URL,
                'checks': checks}
        with open(os.path.join(HERE, 'browser_assertions.json'), 'w') as f:
            json.dump(meta, f, indent=2)
        bad = [c['name'] for c in checks if not c['pass']]
        print('BROWSER PROBE RESULT: ' + ('all assertions pass' if not bad else 'differ: ' + ', '.join(bad)))
        return 0 if not bad else 1
    finally:
        try:
            srv.terminate()
            srv.wait(timeout=10)
        except Exception:
            try:
                srv.kill()
            except Exception:
                pass


if __name__ == '__main__':
    sys.exit(main())
