#!/usr/bin/env python3
"""CA01-LIVE-RESPONSE-INTEGRITY regression (MPC-011 I).

POST /cmd used to mutate successfully and then kill the connection: the
`create` result embedded the raw Unit object, json.dumps raised TypeError,
and the client got an empty reply (HTTP 000) — a false failure inviting
retry duplication. parse_and_place now returns a JSON-safe unit summary.

Proven against a real HTTP server + real HTTP client on 127.0.0.1.
"""
from __future__ import annotations

import sys
import os
import json
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from form.open import open_program
from form.dell_matrix import live_visual

CHECKS = []


def check(name, cond):
    CHECKS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")
    if not cond:
        raise AssertionError(name)


def _post(port, cmd):
    data = json.dumps({"cmd": cmd}).encode()
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/cmd", data=data,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.status, r.read().decode()


def run_all():
    p = open_program("LRIReg")
    info = live_visual.start_live(p, port=18771, background=True)
    port = info["port"]
    try:
        # 1. mutating POST returns HTTP 200 (not a dropped connection)
        status, body = _post(port, "create an idea called lri_probe")
        check("POST /cmd returns HTTP 200", status == 200)

        # 2. body is valid JSON with ok=True
        d = json.loads(body)
        check("response is valid JSON, ok=True", d.get("ok") is True)

        # 3. receipt carries a string id
        cid = d.get("create", {}).get("id")
        check("receipt carries string idea id", isinstance(cid, str) and cid)

        # 4. receipt <-> observable state consistency
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/state", timeout=10) as r:
            state = json.loads(r.read().decode())
        node_ids = [n.get("id") for n in state.get("nodes", [])]
        check("receipt id present in /state", cid in node_ids or cid in p.cube.session.plane.units)

        # 5. retry is an honest duplicate (dedup), not a silent drop or overwrite
        status2, body2 = _post(port, "create an idea called lri_probe")
        d2 = json.loads(body2)
        check("retry returns HTTP 200 JSON ok", status2 == 200 and d2.get("ok") is True)
        check("retry mints distinct dedup id", d2.get("create", {}).get("id") == f"{cid}_1")
    finally:
        try:
            live_visual._LIVE_SERVER.shutdown()
        except Exception:
            pass

    print(f"LIVE-RESPONSE-INTEGRITY: {sum(1 for _, c in CHECKS if c)}/{len(CHECKS)} GREEN")


def smoke() -> bool:
    """Regress entry point: run all checks, return True on success."""
    try:
        run_all()
        return True
    except Exception as e:
        print(f"LIVE-RESPONSE-INTEGRITY SMOKE FAILED: {e}")
        return False


if __name__ == "__main__":
    run_all()
