#!/usr/bin/env python3
"""Real-browser acceptance for DellMatrix Studio (security circuit).

Drives the hardened Studio server with a real Chromium engine
(headless) over the DevTools protocol, using a minimal stdlib
WebSocket client (no third-party packages on this VM). The drive
is genuine UI interaction: the page loads from the server, the
seed is typed into the real editor, the real RUN button is
clicked, and verdicts are read back from the live DOM (rack size,
canvas outcome classes, store panel, receipts, status line).
Console errors and page exceptions are collected via CDP events.

Realism label: INTEGRATION-plus. A real browser engine ran the
real frontend against the real server, but no human session,
display, or manual interaction is claimed — NOT REAL_USER_PATH.
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
PAGE_URL = os.environ.get("PAGE_URL", "http://127.0.0.1:8877/")
OUT_DIR = os.path.dirname(os.path.abspath(__file__))


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


def main():
    checks = []

    def expect(name, cond, detail=""):
        checks.append((name, bool(cond)))
        print("[%s] %s %s" % ("PASS" if cond else "FAIL", name, detail))

    # find the page target
    targets = None
    for _ in range(50):
        try:
            with urllib.request.urlopen(
                    "http://127.0.0.1:%d/json/list" % CDP_PORT,
                    timeout=2) as res:
                targets = json.loads(res.read().decode())
            break
        except Exception:
            time.sleep(0.2)
    if not targets:
        print("FAIL: no CDP targets")
        return 1
    page = next((t for t in targets if t.get("type") == "page"), None)
    if not page:
        print("FAIL: no page target")
        return 1

    cdp = CDP(WS(page["webSocketDebuggerUrl"]))
    cdp.call("Page.enable")
    cdp.call("Runtime.enable")
    cdp.call("Log.enable")
    cdp.call("Page.navigate", {"url": PAGE_URL})
    cdp.pump(4)

    expect("page title is the Studio",
           cdp.eval("document.title") == "DellMatrix Studio",
           repr(cdp.eval("document.title")))
    rack = cdp.eval("document.querySelectorAll('#rack .dell').length")
    expect("Dell Rack renders exactly 100 Dells", rack == 100,
           "count=%r" % rack)
    status0 = cdp.eval(
        "document.querySelector('#status-text').textContent")
    print("status after load:", status0)

    seed = "55[Set] :: tempo=120 >> 56[Get] :: tempo"
    cdp.eval(
        "(() => { const el = document.querySelector('#seed-editor');"
        " el.value = %s;"
        " el.dispatchEvent(new Event('input', {bubbles: true}));"
        " return el.value; })()" % json.dumps(seed))
    cdp.pump(2)
    atoms = cdp.eval("document.querySelectorAll('#chain .atom').length")
    expect("canvas renders the parsed chain (2 atoms)", atoms == 2,
           "count=%r" % atoms)
    painted = cdp.eval(
        "document.querySelectorAll('#chain .atom-ok').length")
    expect("no outcome painted before the run", painted == 0,
           "ok=%r" % painted)

    cdp.eval("document.querySelector('#execute-btn').click()")
    cdp.pump(4)
    ok_cards = cdp.eval(
        "document.querySelectorAll('#chain .atom-ok').length")
    expect("both atoms painted atom-ok from real receipts",
           ok_cards == 2, "ok=%r" % ok_cards)
    verdicts = cdp.eval(
        "[...document.querySelectorAll('#chain .atom-verdict')]"
        ".map(v => v.textContent).join(' | ')")
    print("verdicts:", verdicts)
    store_text = cdp.eval(
        "document.querySelector('#store').textContent")
    expect("store panel shows the executed value",
           "tempo" in (store_text or ""), repr(store_text)[:120])
    receipts = cdp.eval(
        "document.querySelector('#receipts').textContent")
    expect("receipts panel records the run",
           "No runs yet" not in (receipts or ""), repr(receipts)[:120])
    status1 = cdp.eval(
        "document.querySelector('#status-text').textContent")
    print("status after run:", status1)

    errors = []
    for ev in cdp.events:
        method = ev.get("method")
        params = ev.get("params") or {}
        if method == "Runtime.exceptionThrown":
            errors.append("exception: %s" % json.dumps(params)[:200])
        elif method == "Runtime.consoleAPICalled" \
                and params.get("type") == "error":
            errors.append("console.error: %s" % json.dumps(params)[:200])
        elif method == "Log.entryAdded" \
                and (params.get("entry") or {}).get("level") == "error":
            errors.append("log: %s" % json.dumps(params)[:200])
    expect("zero console errors / page exceptions", not errors,
           "; ".join(errors)[:300])

    shot = cdp.call("Page.captureScreenshot", {"format": "png"})
    if shot.get("data"):
        with open(os.path.join(OUT_DIR, "studio_browser.png"),
                  "wb") as fh:
            fh.write(base64.b64decode(shot["data"]))
        print("screenshot saved: studio_browser.png")

    passed = sum(1 for _, c in checks if c)
    print("BROWSER-ACCEPT: %d/%d" % (passed, len(checks)))
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
