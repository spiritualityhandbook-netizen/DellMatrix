#!/usr/bin/env python3
"""Live /cmd hardening regression (MPC-011 close, §0).

Bounded hardening: default-deny unauthorized cross-origin command
execution, preserve localhost operation, no wildcard ACAO, no oversized
auth system. No browser exploit is claimed.

- missing Origin (curl/local scripts) -> allowed (200)
- server's own origin -> allowed (200)
- foreign origin -> 403 denied
- other localhost port -> 403 denied
- no Access-Control-Allow-Origin: * on responses
"""
from __future__ import annotations

import sys
import os
import json
import urllib.request
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from form.open import open_program
from form.dell_matrix import live_visual

CHECKS = []


def check(name, cond):
    CHECKS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")
    if not cond:
        raise AssertionError(name)


def _post(port, origin):
    data = json.dumps({"cmd": "create an idea called hz_probe"}).encode()
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/cmd", data=data,
        headers={"Content-Type": "application/json"},
    )
    if origin:
        req.add_header("Origin", origin)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, r.headers.get("Access-Control-Allow-Origin")
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Access-Control-Allow-Origin")


def run_all():
    p = open_program("HZReg")
    info = live_visual.start_live(p, port=18773, background=True)
    port = info["port"]
    try:
        s, _ = _post(port, None)
        check("missing Origin allowed (localhost operation)", s == 200)
        s, _ = _post(port, f"http://127.0.0.1:{port}")
        check("own origin allowed", s == 200)
        s, _ = _post(port, f"http://localhost:{port}")
        check("localhost origin allowed", s == 200)
        s, _ = _post(port, "http://evil.example")
        check("foreign origin denied 403", s == 403)
        s, _ = _post(port, "http://127.0.0.1:19999")
        check("other-port origin denied 403", s == 403)
        _, acao = _post(port, None)
        check("no wildcard ACAO", acao != "*")
    finally:
        try:
            live_visual._LIVE_SERVER.shutdown()
        except Exception:
            pass

    print(f"CMD-HARDENING: {sum(1 for _, c in CHECKS if c)}/{len(CHECKS)} GREEN")


def smoke() -> bool:
    """Regress entry point: run all checks, return True on success."""
    try:
        run_all()
        return True
    except Exception as e:
        print(f"CMD-HARDENING SMOKE FAILED: {e}")
        return False


if __name__ == "__main__":
    run_all()
