#!/usr/bin/env python3
"""Director Mode C correction probe — Origin implicit-port case.

Launches the REAL Studio server (gui.server) bound to port 8765
exactly, fetches the per-launch session token from the index page,
then POSTs /api/execute carrying a VALID token and
Origin: http://127.0.0.1 (NO explicit port). Per the Director's
same-port rule, the omitted port resolves to 80, which is not the
bound port 8765, so the request must be refused 403 with ZERO
business-state mutation.

Pre-fix expectation (the defect): the request is ACCEPTED (200) and
the store mutates. Post-fix expectation: 403 and the store snapshot
is unchanged. Exit 0 iff the post-fix expectation holds.
"""
from __future__ import annotations

import http.client
import json
import os
import re
import shutil
import sys
import threading
from http.server import ThreadingHTTPServer

REPO = os.path.expanduser("~/workspace/nbd-omega-studiosec")
sys.path.insert(0, REPO)

import gui.server as studio  # noqa: E402

OWNER = "StudioCorrProbe"
PORT = 8765
TOKEN_RE = re.compile(r'name="studio-token"\s+content="([^"]+)"')


def cleanup(owner):
    state = os.path.join(REPO, "form", "state")
    names = [f"{p}_{owner}.json" for p in
             ("program", "nursery", "checkpoint", "confirm")]
    names += [f"{base}_{owner}.json" for base in ("current", "gen", "graph")]
    names.append(f"nursery_{owner}.json")
    for name in set(names):
        path = os.path.join(state, name)
        if os.path.exists(path):
            os.remove(path)
    ideas = os.path.join(state, f"ideas_{owner}")
    if os.path.isdir(ideas):
        shutil.rmtree(ideas)


def req(method, path, headers=None, body=b""):
    conn = http.client.HTTPConnection("127.0.0.1", PORT, timeout=10)
    conn.putrequest(method, path, skip_host=True,
                    skip_accept_encoding=True)
    hdrs = {"Host": "127.0.0.1:%d" % PORT}
    hdrs.update(headers or {})
    for k, v in hdrs.items():
        conn.putheader(k, v)
    if method == "POST" and "Content-Length" not in hdrs:
        conn.putheader("Content-Length", str(len(body)))
    conn.endheaders(body if body else None)
    res = conn.getresponse()
    text = res.read().decode("utf-8", "replace")
    status = res.status
    conn.close()
    return status, text


def store():
    _, text = req("GET", f"/api/state?owner={OWNER}")
    payload = json.loads(text)
    return (payload.get("state") or {}).get("store") or {}


def main():
    cleanup(OWNER)
    saved_owner = studio._ACTIVE_OWNER
    server = ThreadingHTTPServer(("127.0.0.1", PORT), studio._Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        status, page = req("GET", "/")
        assert status == 200, f"index status {status}"
        token = TOKEN_RE.search(page).group(1)
        print(f"server bound to {PORT}; token acquired ({len(token)} chars)")

        before = store()
        body = json.dumps({"seed": "55[Set] :: corrprobe=1",
                           "owner": OWNER}).encode("utf-8")
        status, text = req("POST", "/api/execute", headers={
            "X-Studio-Token": token,
            "Content-Type": "application/json",
            "Origin": "http://127.0.0.1",  # NO explicit port
        }, body=body)
        after = store()
        print(f"POST /api/execute valid-token + Origin http://127.0.0.1 "
              f"(no port) -> HTTP {status}")
        print(f"store before: {before}")
        print(f"store after:  {after}")
        refused = status == 403
        unmutated = after == before and "corrprobe" not in after
        print(f"refused 403: {refused}; zero mutation: {unmutated}")
        if refused and unmutated:
            print("PROBE RESULT: PASS — implicit-port Origin refused, "
                  "no mutation")
            return 0
        print("PROBE RESULT: FAIL — implicit-port Origin was ACCEPTED "
              "(defect present)" if status == 200 else
              "PROBE RESULT: FAIL — unexpected outcome")
        return 1
    finally:
        server.shutdown()
        server.server_close()
        studio._ACTIVE_OWNER = saved_owner
        studio._PROGRAMS.pop(OWNER, None)
        cleanup(OWNER)


if __name__ == "__main__":
    sys.exit(main())
