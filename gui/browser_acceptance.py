#!/usr/bin/env python3
"""Real-browser acceptance for DellMatrix Studio — AUTOMATED BROWSER (CDP).

Drives the Studio server with a real Chromium engine (headless) over
the DevTools protocol, using a minimal stdlib WebSocket client (no
third-party packages). The drive is genuine UI interaction:

- the page loads from the real server, token meta and all;
- the seed arrives through the page's own example <select> and its
  real change handler (the app's code path for that control);
- RUN is pressed with Input.dispatchMouseEvent at the button's real
  coordinates — the browser input pipeline, not el.click();
- every app request is issued by the page's own app.js, which is
  also what carries the per-launch session token. The driver itself
  sends ZERO HTTP requests to the app API (its only HTTP is the CDP
  /json/list control plane), so a broken token flow fails here
  exactly as it would for a user;
- verdicts are read back from the live DOM: rack size, canvas
  outcome classes painted from the run's real receipts, the chain
  verdict, the store panel, the receipts panel;
- console errors and page exceptions are collected via CDP events;
- a full-page screenshot is captured in the same session, after
  the interaction assertions pass.

Provenance: adapted from the security circuit's preserved driver
(director-reports/evidence/studio-security/browser_acceptance.py,
kept untouched as the historical original). Changes: repo-owned
home, bounded-wait polling instead of fixed sleeps, real mouse
input, token-meta assertion, structured assertion output
(assertions.json), raw console capture (console_events.json),
screenshot byte verification.

Realism label: AUTOMATED BROWSER (CDP) on the CI runner — genuine
Chromium, real DOM, real input events. It is NOT a human session
and does NOT claim REAL_USER_PATH. API replay is not used anywhere
in this driver and would not be browser acceptance.

Environment:
  PAGE_URL       Studio base URL (default http://127.0.0.1:8765/)
  CDP_PORT       Chromium remote-debugging port (default 9333)
  BROWSER_ACC_OUT  output dir (default ./browser-evidence)
Exit code: 0 iff every assertion passes.
"""
from __future__ import annotations

import base64
import json
import os
import socket
import struct
import sys
import time
import urllib.request

CDP_PORT = int(os.environ.get("CDP_PORT", "9333"))
PAGE_URL = os.environ.get("PAGE_URL", "http://127.0.0.1:8765/")
OUT_DIR = os.environ.get(
    "BROWSER_ACC_OUT",
    os.path.join(os.getcwd(), "browser-evidence"))
EXAMPLE_SEED = "55[Set] :: tempo=120 >> 56[Get] :: tempo"


# ---------------- minimal WebSocket client -----------------------
class WS:
    def __init__(self, url):
        assert url.startswith("ws://")
        rest = url[5:]
        authority, _, path = rest.partition("/")
        host, _, port = authority.partition(":")
        self.sock = socket.create_connection(
            (host, int(port or 80)), timeout=15)
        key = base64.b64encode(os.urandom(16)).decode()
        req = ("GET /%s HTTP/1.1\r\nHost: %s\r\n"
               "Upgrade: websocket\r\nConnection: Upgrade\r\n"
               "Sec-WebSocket-Key: %s\r\nSec-WebSocket-Version: 13\r\n"
               "\r\n" % (path, authority, key))
        self.sock.sendall(req.encode())
        buf = b""
        while b"\r\n\r\n" not in buf:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise RuntimeError("WS handshake closed early")
            buf += chunk
        head, _, self._pending = buf.partition(b"\r\n\r\n")
        if b"101" not in head.split(b"\r\n")[0]:
            raise RuntimeError("WS handshake failed: %r" % head[:120])
        self._buf = self._pending

    def _read_exact(self, n):
        while len(self._buf) < n:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise RuntimeError("WS closed")
            self._buf += chunk
        out, self._buf = self._buf[:n], self._buf[n:]
        return out

    def send_text(self, text):
        data = text.encode("utf-8")
        mask = os.urandom(4)
        header = bytearray([0x81])
        if len(data) < 126:
            header.append(0x80 | len(data))
        elif len(data) < 65536:
            header.append(0x80 | 126)
            header += struct.pack(">H", len(data))
        else:
            header.append(0x80 | 127)
            header += struct.pack(">Q", len(data))
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(data))
        self.sock.sendall(bytes(header) + mask + masked)

    def recv_msg(self, timeout=10):
        self.sock.settimeout(timeout)
        payload = b""
        while True:
            b1, b2 = self._read_exact(2)
            fin = bool(b1 & 0x80)
            opcode = b1 & 0x0F
            masked = bool(b2 & 0x80)
            length = b2 & 0x7F
            if length == 126:
                length = struct.unpack(">H", self._read_exact(2))[0]
            elif length == 127:
                length = struct.unpack(">Q", self._read_exact(8))[0]
            mask = self._read_exact(4) if masked else None
            data = self._read_exact(length)
            if mask:
                data = bytes(b ^ mask[i % 4] for i, b in enumerate(data))
            if opcode == 9:  # ping -> pong
                pong = bytearray([0x8A])
                m = os.urandom(4)
                pong.append(0x80 | len(data))
                self.sock.sendall(bytes(pong) + m + bytes(
                    b ^ m[i % 4] for i, b in enumerate(data)))
                continue
            if opcode == 8:
                raise RuntimeError("WS close frame")
            payload += data
            if fin:
                return payload.decode("utf-8", "replace")


# ---------------- CDP session ------------------------------------
class CDP:
    def __init__(self, ws):
        self.ws = ws
        self._id = 0
        self.events = []

    def call(self, method, params=None, timeout=20):
        self._id += 1
        mid = self._id
        self.ws.send_text(json.dumps(
            {"id": mid, "method": method, "params": params or {}}))
        deadline = time.time() + timeout
        while time.time() < deadline:
            msg = json.loads(self.ws.recv_msg(
                timeout=max(1, int(deadline - time.time()))))
            if msg.get("id") == mid:
                if "error" in msg:
                    raise RuntimeError("CDP %s: %s" % (method, msg["error"]))
                return msg.get("result") or {}
            if "method" in msg:
                self.events.append(msg)
        raise TimeoutError("CDP call timed out: %s" % method)

    def pump(self, seconds):
        deadline = time.time() + seconds
        while time.time() < deadline:
            try:
                msg = json.loads(self.ws.recv_msg(
                    timeout=max(1, int(deadline - time.time()))))
                if "method" in msg:
                    self.events.append(msg)
            except (socket.timeout, TimeoutError):
                break

    def eval(self, expression):
        result = self.call("Runtime.evaluate", {
            "expression": expression, "returnByValue": True})
        inner = result.get("result") or {}
        if inner.get("subtype") == "error":
            raise RuntimeError("eval error: %s" % inner)
        return inner.get("value")


# ---------------- the drive --------------------------------------
def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    checks = []

    def expect(name, cond, detail=""):
        checks.append({"name": name, "pass": bool(cond),
                       "detail": str(detail)[:400]})
        print("[%s] %s %s" % ("PASS" if cond else "FAIL", name, detail),
              flush=True)

    def wait_eval(expression, timeout=20.0, interval=0.25):
        """Poll an expression until it returns a truthy value;
        return that value, or the last (falsy) value at deadline.
        Bounded wait: the deadline is part of the contract."""
        deadline = time.time() + timeout
        value = None
        while True:
            try:
                value = cdp.eval(expression)
            except Exception:
                value = None
            if value:
                return value
            if time.time() >= deadline:
                return value
            cdp.pump(interval)

    # ---- connect to the browser --------------------------------
    targets = None
    deadline = time.time() + 20
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(
                    "http://127.0.0.1:%d/json/list" % CDP_PORT,
                    timeout=2) as res:
                targets = json.loads(res.read().decode())
            break
        except Exception:
            time.sleep(0.25)
    if not targets:
        expect("CDP target list reachable", False,
               "no targets on port %d" % CDP_PORT)
        return finish(checks, None)
    page = next((t for t in targets if t.get("type") == "page"), None)
    if not page:
        expect("CDP page target present", False, repr(targets)[:200])
        return finish(checks, None)

    cdp = CDP(WS(page["webSocketDebuggerUrl"]))
    version = cdp.call("Browser.getVersion")
    print("browser:", version.get("product"), flush=True)
    cdp.call("Page.enable")
    cdp.call("Runtime.enable")
    cdp.call("Log.enable")
    cdp.call("Page.navigate", {"url": PAGE_URL})

    # ---- load + structure --------------------------------------
    title = wait_eval(
        "document.title === 'DellMatrix Studio' && document.title", 20)
    expect("page title is the Studio", title == "DellMatrix Studio",
           repr(cdp.eval("document.title")))
    structure = cdp.eval(
        "['#transport','#rack-panel','#seed-editor','#chain',"
        "'#receipts','#execute-btn','#examples']"
        ".filter(s => !document.querySelector(s))")
    expect("transport, rack, editor, canvas, receipts, RUN, examples"
           " all in the DOM", structure == [],
           "missing=%r" % structure)
    token = cdp.eval(
        "(document.querySelector('meta[name=\"studio-token\"]')"
        " || {}).content || ''")
    expect("served page carries the per-launch session token"
           " (not the placeholder)",
           len(token) >= 16 and token != "__STUDIO_TOKEN__",
           "len=%d" % len(token))
    status = wait_eval(
        "(document.querySelector('#status-text').textContent || '')"
        ".startsWith('engine ready') && "
        "document.querySelector('#status-text').textContent", 20)
    expect("frontend init completed (engine ready status)", bool(status),
           repr(cdp.eval(
               "document.querySelector('#status-text').textContent")))
    print("status after load:", status, flush=True)

    # ---- rack ---------------------------------------------------
    rack = wait_eval(
        "document.querySelectorAll('#rack .dell').length === 100 && 100",
        20)
    count = cdp.eval("document.querySelectorAll('#rack .dell').length")
    expect("Dell Rack renders exactly 100 Dells", count == 100,
           "count=%r" % count)
    heads = cdp.eval(
        "[...document.querySelectorAll('#rack .rack-group-head')]"
        ".map(h => h.textContent).join(' | ')")
    expect("both Core I and Core II rack groups render",
           "CORE I" in (heads or "") and "CORE II" in (heads or ""),
           repr(heads))

    # ---- load the example through the UI ------------------------
    cdp.eval(
        "(() => { const s = document.querySelector('#examples');"
        " s.value = %s;"
        " s.dispatchEvent(new Event('change', {bubbles: true}));"
        " return s.value; })()" % json.dumps(EXAMPLE_SEED))
    editor = wait_eval(
        "document.querySelector('#seed-editor').value === %s && true"
        % json.dumps(EXAMPLE_SEED), 10)
    expect("example select loads its seed into the editor",
           bool(editor),
           repr(cdp.eval("document.querySelector('#seed-editor').value")))
    atoms = wait_eval(
        "document.querySelectorAll('#chain .atom').length === 2 && 2",
        10)
    atom_count = cdp.eval("document.querySelectorAll('#chain .atom').length")
    expect("canvas renders the canonical parse (2 atoms)",
           atom_count == 2, "count=%r" % atom_count)
    painted = cdp.eval(
        "document.querySelectorAll('#chain .atom-ok, #chain .atom-fail,"
        " #chain .atom-skipped').length")
    expect("no outcome painted before the run", painted == 0,
           "painted=%r" % painted)

    # ---- press RUN through the real input pipeline --------------
    rect = cdp.eval(
        "(() => { const b = document.querySelector('#execute-btn');"
        " b.scrollIntoView({block: 'center'});"
        " const r = b.getBoundingClientRect();"
        " return {x: r.x + r.width / 2, y: r.y + r.height / 2}; })()")
    for ev_type, buttons in (("mouseMoved", 0), ("mousePressed", 1),
                             ("mouseReleased", 0)):
        params = {"type": ev_type, "x": rect["x"], "y": rect["y"],
                  "button": "left", "buttons": buttons}
        if ev_type != "mouseMoved":
            params["clickCount"] = 1
        cdp.call("Input.dispatchMouseEvent", params)
    print("RUN clicked at", rect, flush=True)

    verdict = wait_eval(
        "(() => { const v = document.querySelector('#canvas-verdict');"
        " return v && v.className.includes('verdict-ok')"
        " && v.textContent.includes('CHAIN OK')"
        " && v.textContent; })()", 20)
    expect("chain verdict shows CHAIN OK from the run's receipts",
           bool(verdict),
           repr(cdp.eval(
               "document.querySelector('#canvas-verdict').textContent")))
    ok_cards = cdp.eval("document.querySelectorAll('#chain .atom-ok').length")
    expect("both atoms painted atom-ok from real receipts",
           ok_cards == 2, "ok=%r" % ok_cards)
    atom_verdicts = cdp.eval(
        "[...document.querySelectorAll('#chain .atom-verdict')]"
        ".map(v => v.textContent)")
    expect("per-atom verdicts read 'ran'",
           len(atom_verdicts or []) == 2
           and all("ran" in v for v in atom_verdicts),
           repr(atom_verdicts))
    store_text = cdp.eval("document.querySelector('#store').textContent")
    expect("store panel shows the executed value (tempo = 120)",
           "tempo" in (store_text or "") and "120" in (store_text or ""),
           repr(store_text)[:160])
    receipt_rows = cdp.eval(
        "document.querySelectorAll('#receipts .receipt').length")
    receipt_text = cdp.eval(
        "document.querySelector('#receipts').textContent")
    expect("receipts panel records the run as OK",
           (receipt_rows or 0) >= 1 and "OK" in (receipt_text or ""),
           "rows=%r" % receipt_rows)
    status1 = cdp.eval("document.querySelector('#status-text').textContent")
    print("status after run:", status1, flush=True)

    # ---- SM-49 extended coverage --------------------------------
    # Growth, Console, failed chains, skipped atoms, PARTIAL — all
    # through the same real UI path as the happy path above: set the
    # editor through its own input event, wait for the canonical
    # parse, press RUN with the real mouse pipeline. Scenario seeds
    # were established at the executor level first (Cycle 22/23
    # probes); the assertions below are the browser-level proof.
    # Labels carry a per-run suffix so a Create can never collide
    # with a previous run's persisted owner state.
    uniq = "%d" % (int(time.time()) % 1000000)
    FAIL_SEED = '61[Join](bogus="1")'
    LEAF_FAIL_SEED = "37[Nurture]"
    PARTIAL_SEED = ("08[Create] :: Sm49Partial%s >> 37[Nurture]"
                    " >> 09[Show]" % uniq)
    GROWTH_LABEL = "Sm49Growth%s" % uniq
    GROWTH_SEED = "08[Create] :: %s >> 13[Loop] :: 1" % GROWTH_LABEL

    def click_element(selector):
        rect = cdp.eval(
            "(() => { const b = document.querySelector(%s);"
            " if (!b) return null;"
            " b.scrollIntoView({block: 'center'});"
            " const r = b.getBoundingClientRect();"
            " return {x: r.x + r.width / 2, y: r.y + r.height / 2};"
            " })()" % json.dumps(selector))
        if not rect:
            return False
        for ev_type, buttons in (("mouseMoved", 0), ("mousePressed", 1),
                                 ("mouseReleased", 0)):
            params = {"type": ev_type, "x": rect["x"], "y": rect["y"],
                      "button": "left", "buttons": buttons}
            if ev_type != "mouseMoved":
                params["clickCount"] = 1
            cdp.call("Input.dispatchMouseEvent", params)
        return True

    def run_seed(seed, first_num, atom_count):
        cdp.eval(
            "(() => { const e = document.querySelector('#seed-editor');"
            " e.value = %s;"
            " e.dispatchEvent(new Event('input', {bubbles: true}));"
            " return e.value; })()" % json.dumps(seed))
        parsed = wait_eval(
            "(() => { const a = document.querySelectorAll('#chain .atom');"
            " return a.length === %d && a[0] && a[0].querySelector('.atom-num')"
            " && a[0].querySelector('.atom-num').textContent === %s; })()"
            % (atom_count, json.dumps("%02d" % first_num)), 10)
        if not parsed:
            return False
        return click_element("#execute-btn")

    # Failed chain: an unsupported-args Core II Dell carries
    # per-atom receipts, so the canvas paints a real FAILED verdict.
    run_seed(FAIL_SEED, 61, 1)
    fail_verdict = wait_eval(
        "(() => { const v = document.querySelector('#canvas-verdict');"
        " return v && v.className.includes('verdict-fail')"
        " && v.textContent.includes('FAILED') && v.textContent; })()", 20)
    expect("failed chain verdict shows FAILED from real receipts",
           bool(fail_verdict),
           repr(cdp.eval(
               "document.querySelector('#canvas-verdict').textContent")))
    fail_cards = cdp.eval(
        "document.querySelectorAll('#chain .atom-fail').length")
    expect("failed atom painted atom-fail from its receipt",
           fail_cards == 1, "fail=%r" % fail_cards)

    # Failed Core I leaf: a bare 37[Nurture] failure carries no
    # per-atom receipts by design, so no canvas verdict may be
    # inferred — the failure is proven at the receipts surface,
    # with its honest error text.
    run_seed(LEAF_FAIL_SEED, 37, 1)
    leaf_receipt = wait_eval(
        "(() => { const rows = document.querySelectorAll("
        "'#receipts .receipt-fail');"
        " return [...rows].some(r => r.textContent.includes("
        "'add idea requires a label')); })()", 20)
    expect("bare Dell 37 failure is recorded as a FAILED receipt"
           " with its error text", bool(leaf_receipt),
           repr(cdp.eval(
               "document.querySelector('#receipts').textContent"))[:200])
    leaf_hidden = cdp.eval(
        "document.querySelector('#canvas-verdict').className")
    expect("leaf failure paints no inferred canvas verdict"
           " (verdict stays hidden, no per-atom receipts)",
           "verdict-hidden" in (leaf_hidden or ""), repr(leaf_hidden))

    # PARTIAL + skipped: Create succeeds, bare Nurture fails, and
    # FlowThru skips Show — one ok, one fail, one skipped card.
    run_seed(PARTIAL_SEED, 8, 3)
    partial_verdict = wait_eval(
        "(() => { const v = document.querySelector('#canvas-verdict');"
        " return v && v.className.includes('verdict-partial')"
        " && v.textContent.includes('1 skipped of 3')"
        " && v.textContent; })()", 20)
    expect("PARTIAL verdict shows '1 skipped of 3 atoms'",
           bool(partial_verdict),
           repr(cdp.eval(
               "document.querySelector('#canvas-verdict').textContent")))
    card_counts = cdp.eval(
        "({ok: document.querySelectorAll('#chain .atom-ok').length,"
        " fail: document.querySelectorAll('#chain .atom-fail').length,"
        " skipped: document.querySelectorAll('#chain .atom-skipped')"
        ".length})")
    expect("PARTIAL chain paints one ok, one fail, one skipped card",
           card_counts == {"ok": 1, "fail": 1, "skipped": 1},
           repr(card_counts))
    skipped_text = cdp.eval(
        "[...document.querySelectorAll('#chain .atom-verdict')]"
        ".map(v => v.textContent).join(' | ')")
    expect("skipped atom's verdict reads 'skipped' with its reason",
           "skipped" in (skipped_text or ""), repr(skipped_text)[:200])

    # Growth: Create + Loop plants the new unit through the real
    # growth path; the Growth view must card it under its exact
    # label (exact identity, not a stage inference).
    run_seed(GROWTH_SEED, 8, 2)
    growth_verdict = wait_eval(
        "(() => { const v = document.querySelector('#canvas-verdict');"
        " return v && v.className.includes('verdict-ok')"
        " && v.textContent; })()", 20)
    expect("growth chain verdict shows CHAIN OK", bool(growth_verdict),
           repr(cdp.eval(
               "document.querySelector('#canvas-verdict').textContent")))
    click_element('[data-view="growth"]')
    growth_card = wait_eval(
        "(() => { const labels = [...document.querySelectorAll("
        "'#growth .plant-label')].map(e => e.textContent);"
        " return labels.includes(%s); })()" % json.dumps(GROWTH_LABEL),
        20)
    expect("Growth view cards the grown unit under its exact label",
           bool(growth_card),
           repr(cdp.eval(
               "document.querySelector('#growth').textContent"))[:200])
    click_element('[data-view="studio"]')

    # SM-54: an UNPLANTED plane unit must also be carded by the
    # Growth view — the payload serves canonical plane nodes through
    # the lens, not a plant-fabricated inventory. Its card must claim
    # no stage ("stage: —"), the honest unplanted verdict.
    UNPLANTED_LABEL = "Sm54Unplanted%s" % uniq
    run_seed("08[Create] :: %s" % UNPLANTED_LABEL, 8, 1)
    click_element('[data-view="growth"]')
    unplanted_card = wait_eval(
        "(() => { const labels = [...document.querySelectorAll("
        "'#growth .plant-label')].map(e => e.textContent);"
        " return labels.includes(%s); })()" % json.dumps(UNPLANTED_LABEL),
        20)
    expect("Growth view cards an unplanted plane unit "
           "(canonical nodes, not plant fabrication)",
           bool(unplanted_card),
           repr(cdp.eval(
               "document.querySelector('#growth').textContent"))[:200])
    unplanted_stage = cdp.eval(
        "(() => { const cards = [...document.querySelectorAll("
        "'#growth .plant')]; const c = cards.find(x => x.querySelector("
        "'.plant-label').textContent === %s); return c ? c.querySelector("
        "'.plant-stage').textContent : null; })()"
        % json.dumps(UNPLANTED_LABEL))
    expect("unplanted unit's card claims no stage",
           unplanted_stage == "stage: —", repr(unplanted_stage))
    click_element('[data-view="studio"]')

    # Console: one summary line per run, derived from receipts —
    # OK, FAILED and the PARTIAL line with its skipped count must
    # all be present; Clear empties the log (view-only).
    click_element('[data-view="console"]')
    console_text = wait_eval(
        "document.querySelector('#console-log').textContent"
        " && document.querySelector('#console-log').textContent", 10)
    expect("console records an OK run summary",
           "— OK" in (console_text or ""), repr(console_text)[:200])
    expect("console records a FAILED run summary",
           "— FAILED" in (console_text or ""), repr(console_text)[:200])
    expect("console records the PARTIAL summary with '1 skipped'",
           "— PARTIAL" in (console_text or "")
           and "1 skipped" in (console_text or ""),
           repr(console_text)[:300])
    click_element("#console-clear")
    cleared = cdp.eval(
        "(document.querySelector('#console-log').textContent || '')"
        ".trim()")
    expect("console Clear empties the log", cleared == "",
           "len=%d" % len(cleared or ""))
    click_element('[data-view="studio"]')

    # ---- console errors (raw capture kept for audit) ------------
    raw_errors = []
    for ev in cdp.events:
        method = ev.get("method")
        params = ev.get("params") or {}
        if method == "Runtime.exceptionThrown":
            raw_errors.append({"kind": "exception",
                               "text": json.dumps(params)[:500]})
        elif method == "Runtime.consoleAPICalled" \
                and params.get("type") == "error":
            raw_errors.append({"kind": "console.error",
                               "text": json.dumps(params)[:500]})
        elif method == "Log.entryAdded" \
                and (params.get("entry") or {}).get("level") == "error":
            raw_errors.append({"kind": "log",
                               "text": json.dumps(params)[:500]})
    app_errors = [e for e in raw_errors if "favicon" not in e["text"]]
    with open(os.path.join(OUT_DIR, "console_events.json"), "w") as fh:
        json.dump({"raw_error_candidates": raw_errors,
                   "excluded_as_favicon_only":
                       len(raw_errors) - len(app_errors),
                   "app_errors": app_errors}, fh, indent=2)
    expect("zero console errors / page exceptions (favicon excluded)",
           not app_errors, "; ".join(
               e["text"] for e in app_errors)[:300])

    # ---- screenshot (same session, after the drive) -------------
    metrics = cdp.call("Page.getLayoutMetrics")
    size = (metrics.get("cssContentSize")
            or metrics.get("contentSize") or {})
    width = int(size.get("width") or 1440)
    height = min(int(size.get("height") or 1000), 4000)
    shot = cdp.call("Page.captureScreenshot", {
        "format": "png", "captureBeyondViewport": True,
        "clip": {"x": 0, "y": 0, "width": width, "height": height,
                 "scale": 1}})
    png = base64.b64decode(shot["data"]) if shot.get("data") else b""
    shot_path = os.path.join(OUT_DIR, "studio_browser.png")
    with open(shot_path, "wb") as fh:
        fh.write(png)
    dims = None
    if len(png) >= 24 and png[:8] == b"\x89PNG\r\n\x1a\n":
        dims = struct.unpack(">II", png[16:24])
    expect("screenshot is a real PNG of the page",
           dims is not None and len(png) > 10000,
           "bytes=%d dims=%r" % (len(png), dims))
    print("screenshot saved: %s (%d bytes, dims %r)"
          % (shot_path, len(png), dims), flush=True)

    return finish(checks, version)


def finish(checks, version):
    passed = sum(1 for c in checks if c["pass"])
    summary = {
        "label": "AUTOMATED BROWSER (CDP) — genuine Chromium run; "
                 "not a human session; not REAL_USER_PATH",
        "page_url": PAGE_URL,
        "browser": (version or {}).get("product"),
        "user_agent": (version or {}).get("userAgent"),
        "checks": checks,
        "passed": passed,
        "total": len(checks),
    }
    with open(os.path.join(OUT_DIR, "assertions.json"), "w") as fh:
        json.dump(summary, fh, indent=2)
    print("BROWSER-ACCEPT: %d/%d" % (passed, len(checks)), flush=True)
    return 0 if passed == len(checks) and checks else 1


if __name__ == "__main__":
    sys.exit(main())
