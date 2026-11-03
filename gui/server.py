#!/usr/bin/env python3
"""DellMatrix Studio — local GUI server (Python standard library only).

Serves the Studio frontend and a small JSON API over the REAL
DellMatrix program, reached only through its public paths:

  * form.open.open_program(owner)          — canonical constructor
  * form.mandell.executor.execute_seed     — the front door
  * form.mandell.registry.DELLS            — the canonical registry
  * form.mandell.core_ii.CORE_II           — Core II metadata
  * form.dell_matrix.view_rooms            — the growth lens

The GUI adds no execution authority of its own: every seed the
user runs goes through execute_seed exactly as the REPL's do,
and sovereign steps (Commit, Lock, the learning gate) remain
the user's explicit actions.

Launch:
    python3 -m gui.server [--owner NAME] [--port 8765] [--host 127.0.0.1]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
_STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

from form.dell_matrix.view_rooms import filter_nodes_for_room  # noqa: E402
from form.mandell.core_ii import CORE_II  # noqa: E402
from form.mandell.executor import execute_seed  # noqa: E402
from form.mandell.registry import DELLS  # noqa: E402
from form.open import open_program  # noqa: E402

_LOCK = threading.RLock()
_PROGRAMS: dict = {}
_ACTIVE_OWNER = "Operator"

_STATIC_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/style.css": ("style.css", "text/css; charset=utf-8"),
}


def _safe(value, depth=0):
    """Convert a program value into JSON-safe data with hard caps,
    so a state snapshot can never explode or hang the API."""
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        return value if len(value) <= 2000 else value[:2000] + "…"
    if depth >= 4:
        return repr(value)[:200]
    if isinstance(value, dict):
        return {str(k): _safe(v, depth + 1)
                for k, v in list(value.items())[:100]}
    if isinstance(value, (list, tuple)):
        return [_safe(v, depth + 1) for v in list(value)[:100]]
    return repr(value)[:200]


def _get_program(owner: str):
    with _LOCK:
        prog = _PROGRAMS.get(owner)
        if prog is None:
            prog = open_program(owner)
            _PROGRAMS[owner] = prog
        return prog


def _plants(program):
    # ForceField is a dataclass of forces; the plants live on its
    # GrowthForce: program.forces.growth.plants. (A flat
    # forces.plants does not exist — reading it silently yielded
    # an empty field in the first P1 smoke.)
    forces = getattr(program, "forces", None)
    if forces is None:
        return []
    growth = getattr(forces, "growth", None)
    plants = getattr(growth, "plants", None)
    if plants is None:
        plants = getattr(forces, "plants", [])
    return [p for p in (plants or []) if isinstance(p, dict)]


def _state_snapshot(program):
    core_ii = getattr(program, "core_ii", None)
    store = {}
    selected = None
    last_result = None
    if core_ii is not None:
        raw_store = getattr(core_ii, "store", {}) or {}
        store = {str(k): _safe(v) for k, v in list(raw_store.items())[:200]}
        selected = _safe(getattr(core_ii, "selected", None))
        last_result = _safe(getattr(core_ii, "last_result", None))
    plants = _plants(program)
    return {
        "owner": getattr(program, "owner", _ACTIVE_OWNER),
        "store": store,
        "store_count": len(store),
        "selected": selected,
        "last_result": last_result,
        "plants": [{"idea": p.get("idea"),
                    "idea_full": p.get("idea_full"),
                    "stage": p.get("stage")} for p in plants[:200]],
        "plant_count": len(plants),
        "history_count": len(getattr(program, "history", []) or []),
    }


def _dells_payload():
    out = []
    for n in range(100):
        entry = DELLS.get(n) or {}
        row = {
            "num": n,
            "name": entry.get("name", ""),
            "manor": entry.get("manor", ""),
            "core": "I" if n <= 50 else "II",
        }
        c2 = CORE_II.get(n)
        if c2:
            row["family"] = c2.get("family")
            row["effect"] = c2.get("effect")
            row["root"] = c2.get("root")
        out.append(row)
    return out


def _growth_payload(program):
    plants = _plants(program)
    nodes = []
    for i, p in enumerate(plants):
        label = p.get("idea_full") or p.get("idea") or ""
        nodes.append({"id": "plant-%d" % i, "label": label, "score": 0.0})
    if not nodes:
        return {"nodes": [], "plant_count": 0}
    viewed = filter_nodes_for_room("growth", nodes, plants=plants)
    return {"nodes": _safe(viewed), "plant_count": len(plants)}


class _Handler(BaseHTTPRequestHandler):
    server_version = "DellMatrixStudio/1.0"

    def log_message(self, fmt, *args):  # keep the console quiet
        pass

    def _send_json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_static(self, path):
        name, ctype = _STATIC_FILES[path]
        full = os.path.join(_STATIC_DIR, name)
        try:
            with open(full, "rb") as fh:
                body = fh.read()
        except OSError:
            self._send_json({"ok": False, "error": "static file missing: %s" % name},
                            status=404)
            return
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _owner_from(self, query, body=None):
        if body and isinstance(body.get("owner"), str) and body["owner"].strip():
            return body["owner"].strip()
        values = query.get("owner")
        if values and values[0].strip():
            return values[0].strip()
        return _ACTIVE_OWNER

    def do_GET(self):
        try:
            parsed = urlparse(self.path)
            path = parsed.path
            query = parse_qs(parsed.query)
            if path in _STATIC_FILES:
                self._send_static(path)
                return
            if path == "/api/dells":
                self._send_json({"ok": True, "dells": _dells_payload()})
                return
            if path == "/api/state":
                owner = self._owner_from(query)
                with _LOCK:
                    program = _get_program(owner)
                    self._send_json({"ok": True,
                                     "state": _state_snapshot(program)})
                return
            if path == "/api/growth":
                owner = self._owner_from(query)
                with _LOCK:
                    program = _get_program(owner)
                    self._send_json({"ok": True,
                                     "growth": _growth_payload(program)})
                return
            self._send_json({"ok": False, "error": "unknown path: %s" % path},
                            status=404)
        except Exception as exc:  # the API reports, never crashes
            self._send_json({"ok": False, "error": "%s: %s"
                             % (type(exc).__name__, exc)}, status=500)

    def do_POST(self):
        try:
            parsed = urlparse(self.path)
            path = parsed.path
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(length) if length > 0 else b"{}"
            try:
                body = json.loads(raw.decode("utf-8")) if raw else {}
            except (ValueError, UnicodeDecodeError):
                self._send_json({"ok": False, "error": "request body is not JSON"},
                                status=400)
                return
            if path == "/api/execute":
                seed = body.get("seed")
                if not isinstance(seed, str) or not seed.strip():
                    self._send_json({"ok": False,
                                     "error": "seed must be a non-empty string"},
                                    status=400)
                    return
                owner = self._owner_from({}, body)
                with _LOCK:
                    program = _get_program(owner)
                    result = execute_seed(program, seed)
                    self._send_json({
                        "ok": True,
                        "result": _safe(result),
                        "state": _state_snapshot(program),
                    })
                return
            if path == "/api/owner":
                global _ACTIVE_OWNER
                owner = self._owner_from({}, body)
                with _LOCK:
                    _ACTIVE_OWNER = owner
                    program = _get_program(owner)
                    self._send_json({"ok": True,
                                     "state": _state_snapshot(program)})
                return
            self._send_json({"ok": False, "error": "unknown path: %s" % path},
                            status=404)
        except Exception as exc:
            self._send_json({"ok": False, "error": "%s: %s"
                             % (type(exc).__name__, exc)}, status=500)


def main(argv=None):
    global _ACTIVE_OWNER
    ap = argparse.ArgumentParser(
        description="DellMatrix Studio — local GUI server")
    ap.add_argument("--owner", default="Operator",
                    help="program owner to open first (default: Operator)")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args(argv)
    _ACTIVE_OWNER = args.owner
    _get_program(args.owner)  # fail fast if the program cannot open
    server = ThreadingHTTPServer((args.host, args.port), _Handler)
    print("DellMatrix Studio: http://%s:%d  (owner: %s)"
          % (args.host, args.port, args.owner), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
