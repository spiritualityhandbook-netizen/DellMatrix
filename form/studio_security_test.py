#!/usr/bin/env python3
"""DellMatrix Studio security regression (Studio security circuit).

Drives the REAL Studio server (gui.server) over HTTP on an ephemeral
port with raw header control (http.client), against throwaway owners
whose state files are removed exactly afterwards. Every adversarial
check asserts BOTH the refusal AND zero business-state mutation
(store snapshot equality), so a refusal that still executes fails.

Contract under test (gui/server.py hardening):
  * Host allowlist — loopback hostnames only, port must match the
    bound port; missing Host rejected (DNS-rebinding defense).
  * Origin discipline on POST — a present Origin must be this
    server's own loopback origin (foreign origin / foreign port /
    "null" rejected).
  * Content-Type discipline — POST /api/* requires application/json.
  * Per-launch session token — minted per server module load, served
    only inside the index page (no-store), required as the
    X-Studio-Token header on every POST /api/*.
  * Request-size cap — Content-Length over the cap is refused 413
    BEFORE the body is read (proven by declaring 200 KB, sending
    1 KB, and still receiving the refusal); malformed / negative
    Content-Length is a 400, never a 500.
  * Connection timeout — a slow-drip connection is closed by the
    server (module constant patched down for the check).
  * Static confinement — traversal-shaped paths stay 404 (this held
    on the pre-hardening base too; recorded as an already-safe
    surface, kept here as a regression guard).

GET endpoints intentionally require no token: they never mutate, the
Host check defeats rebound reads, and same-origin policy defeats
cross-origin reads. That posture is part of the submitted design and
is asserted here so it cannot drift silently.

Regress entry: smoke() -> True, final line prints n/m.
"""
from __future__ import annotations

import http.client
import json
import os
import re
import shutil
import socket
import sys
import threading
from http.server import ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gui.server as studio  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OWNERS = ("StudioSecA", "StudioSecB")
CHECKS = []

TOKEN_RE = re.compile(r'name="studio-token"\s+content="([^"]+)"')


def check(name, cond):
    CHECKS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")
    if not cond:
        raise AssertionError(name)


def _cleanup(owner):
    state = os.path.join(ROOT, "form", "state")
    names = [f"{p}_{owner}.json" for p in
             ("program", "nursery", "checkpoint", "confirm")]
    names += [f"{base}_{owner}.json" for base in
              ("current", "gen", "graph")]
    names.append(f"nursery_{owner}.json")
    for name in set(names):
        path = os.path.join(state, name)
        if os.path.exists(path):
            os.remove(path)
    ideas = os.path.join(state, f"ideas_{owner}")
    if os.path.isdir(ideas):
        shutil.rmtree(ideas)


def _raw(port, method, path, headers=None, body=b"", host="default",
         send_length=True):
    """One HTTP request with full header control. host: "default"
    sends this server's own Host; None omits Host; any string is
    sent verbatim."""
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    conn.putrequest(method, path, skip_host=True,
                    skip_accept_encoding=True)
    hdrs = dict(headers or {})
    if host == "default":
        hdrs.setdefault("Host", "127.0.0.1:%d" % port)
    elif host is not None:
        hdrs["Host"] = host
    for key, value in hdrs.items():
        conn.putheader(key, value)
    if send_length and "Content-Length" not in hdrs:
        conn.putheader("Content-Length", str(len(body)))
    conn.endheaders(body if body else None)
    res = conn.getresponse()
    text = res.read().decode("utf-8", "replace")
    out_headers = {k.lower(): v for k, v in res.getheaders()}
    status = res.status
    conn.close()
    return status, text, out_headers


def _json_req(port, method, path, payload=None, **kw):
    body = b""
    headers = dict(kw.pop("headers", None) or {})
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers.setdefault("Content-Type", "application/json")
    status, text, out_headers = _raw(port, method, path, headers=headers,
                                     body=body, **kw)
    try:
        return status, json.loads(text), out_headers
    except ValueError:
        return status, text, out_headers


def _store(port, owner):
    _, payload, _ = _json_req(port, "GET", f"/api/state?owner={owner}")
    return (payload.get("state") or {}).get("store") or {}


def run_all():
    for owner in OWNERS:
        _cleanup(owner)
    saved_owner = studio._ACTIVE_OWNER
    saved_timeout = getattr(studio, "_REQUEST_TIMEOUT_S", None)
    server = ThreadingHTTPServer(("127.0.0.1", 0), studio._Handler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        a, b = OWNERS
        origin = "http://127.0.0.1:%d" % port

        # --- the legitimate page + its token ---------------------
        status, page, page_headers = _raw(port, "GET", "/")
        check("GET / 200 serves the Studio page",
              status == 200 and "DELLMATRIX" in page)
        match = TOKEN_RE.search(page)
        token = match.group(1) if match else None
        check("index page carries a per-launch session token",
              token is not None and len(token) >= 32)
        check("token-bearing index is served Cache-Control: no-store",
              "no-store" in (page_headers.get("cache-control") or ""))
        auth = {"X-Studio-Token": token or "missing-token"}

        # --- legitimate flow (browser shape + tooling shape) -----
        status, payload, _ = _json_req(
            port, "POST", "/api/execute",
            {"seed": "55[Set] :: tempo=120", "owner": a},
            headers={**auth, "Origin": origin})
        check("browser-shaped execute (own Origin + token) succeeds",
              status == 200
              and (payload.get("result") or {}).get("ok") is True)
        check("the stored value is visible afterwards",
              _store(port, a).get("tempo") == "120")
        status, payload, _ = _json_req(
            port, "POST", "/api/execute",
            {"seed": "56[Get] :: tempo", "owner": a}, headers=auth)
        check("no-Origin tooling execute with token succeeds",
              status == 200
              and (payload.get("result") or {}).get("ok") is True)
        status, payload, _ = _json_req(port, "GET", "/api/dells")
        check("GET /api/dells needs no token and lists 100 Dells",
              status == 200 and len(payload.get("dells") or []) == 100)

        # --- Host allowlist (DNS-rebinding defense) --------------
        status, _, _ = _raw(port, "GET", "/api/dells",
                            host="evil.example:%d" % port)
        check("foreign Host is rejected 403", status == 403)
        status, _, _ = _raw(port, "GET", "/api/dells",
                            host="localhost.evil.com:%d" % port)
        check("suffix-trick Host is rejected 403", status == 403)
        status, _, _ = _raw(port, "GET", "/api/dells",
                            host="127.0.0.1:%d" % (port + 9))
        check("loopback Host with the wrong port is rejected 403",
              status == 403)
        status, _, _ = _raw(port, "GET", "/api/dells", host=None)
        check("missing Host is rejected 403", status == 403)
        status, _, _ = _raw(port, "GET", "/api/dells",
                            host="localhost:%d" % port)
        check("localhost Host is accepted", status == 200)
        status, _, _ = _raw(port, "GET", "/api/dells",
                            host="[::1]:%d" % port)
        check("[::1] Host is accepted", status == 200)

        # --- Origin + Content-Type discipline --------------------
        before = _store(port, a)
        status, _, _ = _json_req(
            port, "POST", "/api/execute",
            {"seed": "55[Set] :: pwned=1", "owner": a},
            headers={**auth, "Origin": "http://evil.example"})
        check("cross-origin execute is rejected 403", status == 403)
        check("cross-origin execute mutated nothing",
              _store(port, a) == before and "pwned" not in _store(port, a))
        raw_seed = json.dumps(
            {"seed": "55[Set] :: pwned=1", "owner": a}).encode("utf-8")
        status, _, _ = _raw(
            port, "POST", "/api/execute",
            headers={**auth, "Origin": "http://evil.example",
                     "Content-Type": "text/plain"},
            body=raw_seed)
        check("simple-request (text/plain) execute is rejected",
              status in (403, 415))
        check("simple-request execute mutated nothing",
              "pwned" not in _store(port, a))
        status, _, _ = _raw(
            port, "POST", "/api/execute",
            headers={**auth, "Content-Type": "text/plain"},
            body=raw_seed)
        check("token-carrying text/plain execute is rejected 415",
              status == 415)
        check("the text/plain rejection mutated nothing",
              "pwned" not in _store(port, a))
        status, _, _ = _json_req(
            port, "POST", "/api/execute",
            {"seed": "55[Set] :: pwned=1", "owner": a},
            headers={**auth,
                     "Origin": "http://127.0.0.1:%d" % (port + 9)})
        check("Origin from a foreign port is rejected 403",
              status == 403)
        status, _, _ = _json_req(
            port, "POST", "/api/execute",
            {"seed": "55[Set] :: pwned=1", "owner": a},
            headers={**auth, "Origin": "null"})
        check("Origin 'null' is rejected 403", status == 403)
        check("no rejected execute ever mutated the store",
              _store(port, a) == before)

        # --- session token enforcement ---------------------------
        status, _, _ = _json_req(
            port, "POST", "/api/execute",
            {"seed": "55[Set] :: pwned=1", "owner": a})
        check("tokenless execute is rejected 401", status == 401)
        status, _, _ = _json_req(
            port, "POST", "/api/execute",
            {"seed": "55[Set] :: pwned=1", "owner": a},
            headers={"X-Studio-Token": "definitely-wrong"})
        check("wrong-token execute is rejected 401", status == 401)
        check("token rejections mutated nothing",
              _store(port, a) == before)
        status, _, _ = _json_req(port, "POST", "/api/owner",
                                 {"owner": b})
        check("tokenless owner switch is rejected 401", status == 401)
        check("active owner unchanged after tokenless switch attempt",
              studio._ACTIVE_OWNER == saved_owner)
        status, js, _ = _raw(port, "GET", "/app.js")
        check("session token never appears in /app.js",
              status == 200 and bool(token) and token not in js)
        status, err_text, _ = _raw(port, "GET", "/no-such-path")
        check("session token never appears in error bodies",
              status == 404 and bool(token) and token not in err_text)

        # --- size cap + Content-Length honesty -------------------
        sock = socket.create_connection(("127.0.0.1", port), timeout=10)
        try:
            sock.settimeout(5)
            sock.sendall(
                b"POST /api/execute HTTP/1.1\r\n"
                b"Host: 127.0.0.1\r\n"
                b"Content-Type: application/json\r\n"
                b"Content-Length: 200000\r\n\r\n"
                + b'{"seed": "' + b"x" * 1000)
            chunks = b""
            try:
                while b"\r\n\r\n" not in chunks:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    chunks += chunk
            except socket.timeout:
                chunks = b""
        finally:
            sock.close()
        check("oversized body is refused 413 BEFORE being read",
              chunks.startswith(b"HTTP/1.1 413")
              or chunks.startswith(b"HTTP/1.0 413"))
        status, _, _ = _raw(port, "POST", "/api/execute",
                            headers={**auth,
                                     "Content-Type": "application/json",
                                     "Content-Length": "abc"},
                            body=b"{}", send_length=False)
        check("malformed Content-Length is a 400, never a 500",
              status == 400)
        status, _, _ = _raw(port, "POST", "/api/parse",
                            headers={**auth,
                                     "Content-Type": "application/json",
                                     "Content-Length": "-5"},
                            body=b"", send_length=False)
        check("negative Content-Length is a 400", status == 400)

        # --- slow-drip timeout -----------------------------------
        if hasattr(studio, "_REQUEST_TIMEOUT_S"):
            studio._REQUEST_TIMEOUT_S = 1
        drip = socket.create_connection(("127.0.0.1", port), timeout=10)
        closed = False
        try:
            drip.settimeout(8)
            drip.sendall(b"GET / HTTP/1.1\r\nHost: 127.0.0.1\r\n")
            try:
                closed = drip.recv(1024) == b""
            except (ConnectionResetError, socket.timeout):
                closed = False
        finally:
            drip.close()
            if saved_timeout is not None:
                studio._REQUEST_TIMEOUT_S = saved_timeout
        check("slow-drip connection is closed by the server timeout",
              closed)

        # --- static confinement (already safe on base; guard) ----
        status, _, _ = _raw(port, "GET", "/../gui/server.py")
        check("dot-dot path stays 404", status == 404)
        status, _, _ = _raw(port, "GET", "/%2e%2e%2fform%2fstate")
        check("encoded traversal path stays 404", status == 404)
    finally:
        server.shutdown()
        server.server_close()
        studio._ACTIVE_OWNER = saved_owner
        if saved_timeout is not None:
            studio._REQUEST_TIMEOUT_S = saved_timeout
        for owner in OWNERS:
            studio._PROGRAMS.pop(owner, None)
            _cleanup(owner)

    print(f"STUDIO-SEC: {sum(1 for _, c in CHECKS if c)}/{len(CHECKS)} GREEN")


def smoke() -> bool:
    """Regress entry point: run all checks, return True on success."""
    try:
        run_all()
        return True
    except Exception as e:
        print(f"STUDIO-SEC SMOKE FAILED: {e}")
        return False


if __name__ == "__main__":
    run_all()
