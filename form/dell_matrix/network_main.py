#!/usr/bin/env python3
"""
NetworkMain — out of preform.

21[Merge] : 25[Pulse] >> 14[Bind] :: NetworkMain

Two modes:
1) serve  — stdlib HTTP POST/GET shared Main JSON on localhost
2) client — push/pull to a NetworkMain URL

Still never clobbers personal planes — only Main tags/contributions.

Run:
  python -m form.dell_matrix.network_main --serve --port 8765
  python -m form.dell_matrix.network_main --smoke
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.request import Request, urlopen
from urllib.error import URLError
import json
import os
import sys
import threading

try:
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.dell_matrix.shared_main import (
        load_shared,
        save_shared,
        push_to_shared,
        pull_from_shared,
        DEFAULT_SHARED,
        shared_summary,
    )
    from form.dell_matrix.main_field import MainField
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.dell_matrix.shared_main import (
        load_shared,
        save_shared,
        push_to_shared,
        pull_from_shared,
        DEFAULT_SHARED,
        shared_summary,
    )
    from form.dell_matrix.main_field import MainField

LEVEL = 1


class _Handler(BaseHTTPRequestHandler):
    shared_path = DEFAULT_SHARED

    def log_message(self, fmt, *args):
        pass  # quiet

    def _json(self, code: int, payload: dict):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.startswith("/main"):
            try:
                data = load_shared(self.shared_path)
                self._json(200, {"ok": True, "main": data, "floor": list(FLOOR)})
            except Exception as e:
                self._json(500, {"ok": False, "error": str(e)})
        elif self.path.startswith("/health"):
            self._json(200, {"ok": True, "floor": list(FLOOR), "level": LEVEL})
        else:
            self._json(404, {"ok": False, "error": "use /main or /health"})

    def do_POST(self):
        if not self.path.startswith("/main/push"):
            self._json(404, {"ok": False})
            return
        n = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(n)
        try:
            body = json.loads(raw.decode("utf-8"))
        except Exception:
            self._json(400, {"ok": False, "error": "bad json"})
            return
        tags = body.get("tags") or {}
        owner = body.get("owner") or "remote"
        local = MainField()
        local.tags = {k: float(v) for k, v in tags.items()}
        out = push_to_shared(local, owner, self.shared_path)
        self._json(200, out)


def serve(host: str = "127.0.0.1", port: int = 8765, path: str = DEFAULT_SHARED) -> HTTPServer:
    assert_floor_intact()
    _Handler.shared_path = path
    httpd = HTTPServer((host, port), _Handler)
    return httpd


def serve_background(host: str = "127.0.0.1", port: int = 8765) -> Tuple[HTTPServer, threading.Thread]:
    httpd = serve(host, port)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd, t


def client_pull(base_url: str) -> Dict[str, Any]:
    assert_floor_intact()
    url = base_url.rstrip("/") + "/main"
    try:
        with urlopen(url, timeout=5) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except URLError as e:
        return {"ok": False, "error": str(e)}


def client_push(base_url: str, tags: Dict[str, float], owner: str) -> Dict[str, Any]:
    assert_floor_intact()
    url = base_url.rstrip("/") + "/main/push"
    data = json.dumps({"tags": tags, "owner": owner}).encode("utf-8")
    req = Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urlopen(req, timeout=5) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except URLError as e:
        return {"ok": False, "error": str(e)}


def pull_into_local(local: MainField, base_url: str, mode: str = "merge") -> Dict[str, Any]:
    remote = client_pull(base_url)
    if not remote.get("ok"):
        return remote
    main = remote.get("main") or {}
    tags = {k: float(v) for k, v in (main.get("tags") or {}).items()}
    if mode == "replace_tags":
        local.tags = dict(tags)
    else:
        for k, v in tags.items():
            local.tags[k] = local.tags.get(k, 0.0) + v
    return {"ok": True, "mode": mode, "tags": len(local.tags), "personal_clobber": False}


def smoke() -> bool:
    print("=== NETWORK MAIN SMOKE ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{len(r)+1}] {name}: {'PASS' if ok else 'FAIL'}" + (f" | {detail}" if detail else ""))
        r.append(bool(ok))

    httpd, _t = serve_background("127.0.0.1", 8769)
    try:
        health = client_pull("http://127.0.0.1:8769")  # wrong path shape — use health via urlopen
        from urllib.request import urlopen as uo

        h = json.loads(uo("http://127.0.0.1:8769/health", timeout=3).read().decode())
        rec("health", h.get("ok") is True)
        push = client_push("http://127.0.0.1:8769", {"net": 1.5}, "SmokeNet")
        rec("push", push.get("ok") is True, str(push))
        got = client_pull("http://127.0.0.1:8769")
        rec("pull", got.get("ok") is True and "net" in (got.get("main") or {}).get("tags", {}))
        local = MainField()
        into = pull_into_local(local, "http://127.0.0.1:8769")
        rec("into local", into.get("ok") and local.tags.get("net", 0) > 0)
        rec("floor", list(FLOOR) == ["Alpha", "Delta", "Omega", "Omni"])
    finally:
        httpd.shutdown()
    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


def main() -> None:
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    if "--serve" in sys.argv:
        port = 8765
        for i, a in enumerate(sys.argv):
            if a == "--port" and i + 1 < len(sys.argv):
                port = int(sys.argv[i + 1])
        print(f"NetworkMain serve 127.0.0.1:{port}  GET /main  POST /main/push  GET /health")
        serve("127.0.0.1", port).serve_forever()
    print(shared_summary())


if __name__ == "__main__":
    main()
