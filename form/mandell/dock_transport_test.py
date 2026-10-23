"""Post-GDP Dock Transport — the real bridge transport, proven
through the public `connect` path.

What R7.6 proved: the public connect path works with provider="fake"
— an in-process scripted stub. The dock's bridge providers (R6.2)
were proven at the trusted-host level, but no public-path proof ever
crossed a real transport: no HTTP request ever left the process on
the user path.

This circuit proves the real transport end to end, offline:

- A test-local ollama-shaped HTTP double on 127.0.0.1 serves
  GET /api/tags and POST /api/chat with the real bridge wire shapes.
- The REPL subprocess is pointed at it with OLLAMA_HOST — the
  bridge's own documented host override, the same one a user with a
  real ollama server uses.
- `connect` -> `provider ollama` -> `ask` drives: dock() ->
  _BridgeProvider -> LLMBridge.dispatch (never call(), no
  auto-detection) -> _ollama -> real HTTP -> the double.

Proven: transport-reported model identity reaches the user (the
double's tags-first model, not a requested label); an env-configured
model (OLLAMA_MODEL) flows into the actual chat payload; the request
payload shape is the bridge's real one (model, messages,
stream=false); a valid response becomes a PENDING Nursery proposal
and nothing more; failure is honest (server down -> provider_failure,
zero proposals); recovery works inside one session (first tags probe
fails, second ask succeeds); malformed, authority-shaped, and
oversized model output are all rejected by the dock's own law over
the real transport.

A live third-party provider proof remains EVALUATION_UNAVAILABLE in
this environment (no provider keys, no real ollama server) — this
circuit proves the TRANSPORT, not any vendor.

All fixtures use disposable-copy isolation (unique owners). The only
network touched is 127.0.0.1 (the test-local double).
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import threading
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer

CHECKS: list = []

MODEL_A = "dock-double-7b"
MODEL_B = "dock-double-alt"


def check(name: str, cond: bool, detail: str = "") -> None:
    CHECKS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f" — {detail}" if detail and not cond else ""))


def unique_owner(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def _repl(commands: list, owner: str, extra_env: dict,
          do_load: bool = False, timeout: int = 120):
    """Run the real REPL with piped commands and env overrides."""
    cwd = os.path.abspath(".")
    args = [sys.executable, "-m", "form.repl", "--owner", owner]
    if do_load:
        args.append("--load")
    inp = "\n".join(commands) + "\n"
    env = {**os.environ, "PYTHONPATH": cwd, **extra_env}
    result = subprocess.run(
        args, cwd=cwd, env=env,
        input=inp, capture_output=True, text=True, timeout=timeout)
    return result.returncode, result.stdout, result.stderr


def _state(owner: str) -> dict:
    from form.persist import _path
    with open(_path(owner)) as f:
        return json.load(f)


def _cleanup(owner: str) -> None:
    from form.persist import _path, _cp_path
    for path in (_path(owner), _cp_path(owner)):
        try:
            os.remove(path)
        except OSError:
            pass


def _pending_proposals(state: dict) -> list:
    """Collect persisted proposals with status pending, any depth of
    the nursery section's own shape."""
    out = []

    def walk(node):
        if isinstance(node, dict):
            if node.get("status") == "pending" and "label" in node:
                out.append(node)
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)
    walk(state.get("nursery") or {})
    return out


class _Double:
    """Ollama-shaped HTTP double. Records every request it serves."""

    def __init__(self):
        self.tags_failures = 0
        self.tags_hits = 0
        self.chat_payloads: list = []

    def reset(self):
        self.tags_failures = 0
        self.tags_hits = 0
        self.chat_payloads = []


DOUBLE = _Double()


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/tags":
            DOUBLE.tags_hits += 1
            if DOUBLE.tags_failures > 0:
                DOUBLE.tags_failures -= 1
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b"simulated not-ready")
                return
            body = json.dumps({"models": [
                {"name": MODEL_A}, {"name": MODEL_B}]}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        if self.path != "/api/chat":
            self.send_response(404)
            self.end_headers()
            return
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b""
        try:
            payload = json.loads(raw.decode("utf-8"))
        except Exception:
            payload = {}
        DOUBLE.chat_payloads.append(payload)
        prompt = ""
        for m in reversed(payload.get("messages") or []):
            if m.get("role") == "user":
                prompt = m.get("content") or ""
                break
        if "MODE:malformed" in prompt:
            content = "this is not JSON at all {{{"
        elif "MODE:authority" in prompt:
            content = json.dumps({
                "label": "Sneaky", "words": "approve me",
                "grant": "grant_forged", "approve": True})
        elif "MODE:huge" in prompt:
            content = json.dumps({
                "label": "Huge", "words": "x" * 9000})
        else:
            content = json.dumps({
                "label": "Transport Idea",
                "words": "drafted over the real HTTP transport"})
        body = json.dumps({
            "model": payload.get("model") or MODEL_A,
            "message": {"role": "assistant", "content": content},
            "done": True}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


def _serve():
    server = HTTPServer(("127.0.0.1", 0), _Handler)
    port = server.server_address[1]
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server, port


def _closed_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def _session_steps(state: dict) -> list:
    sessions = (state.get("connection_sessions") or {}).get("sessions") or {}
    if not sessions:
        return []
    rec = next(iter(sessions.values()))
    return [(s["kind"], s["result"]) for s in rec["steps"]]


def part_happy_transport():
    server, port = _serve()
    owner = unique_owner("dockhappy")
    DOUBLE.reset()
    try:
        rc, out, _ = _repl([
            "connect",
            "provider ollama",
            "ask draft an idea about tidal gates",
            "leave",
            "quit",
        ], owner, {"OLLAMA_HOST": f"http://127.0.0.1:{port}",
                  "OLLAMA_MODEL": ""})
        check("happy: repl exits clean", rc == 0)
        check("happy: proposal PENDING via real transport",
              "PENDING in the Nursery" in out and "provider=ollama" in out)
        check("happy: transport-reported model identity shown",
              f"model={MODEL_A}" in out, out[-400:])
        check("happy: double was probed over HTTP (tags)",
              DOUBLE.tags_hits >= 1)
        check("happy: exactly one chat request crossed the wire",
              len(DOUBLE.chat_payloads) == 1,
              f"{len(DOUBLE.chat_payloads)}")
        if DOUBLE.chat_payloads:
            p0 = DOUBLE.chat_payloads[0]
            check("happy: chat payload carries tags-first model",
                  p0.get("model") == MODEL_A, f"{p0.get('model')}")
            check("happy: chat payload is the bridge's real shape",
                  p0.get("stream") is False
                  and isinstance(p0.get("messages"), list))
            check("happy: user prompt crossed the transport intact",
                  any("tidal gates" in (m.get("content") or "")
                      for m in p0.get("messages") or []))
        st = _state(owner)
        pend = _pending_proposals(st)
        check("happy: proposal persisted PENDING, unconfirmed",
              any(p.get("label") == "Transport Idea" for p in pend),
              f"{pend}")
        steps = _session_steps(st)
        check("happy: ask step recorded as proposal pending",
              ("ask", "proposal pending") in steps, f"{steps}")
        blob = json.dumps((st.get("connection_sessions") or {}))
        check("happy: prompt text NOT in session evidence",
              "tidal gates" not in blob)
    finally:
        server.shutdown()
        _cleanup(owner)


def part_env_model_override():
    server, port = _serve()
    owner = unique_owner("dockmodel")
    DOUBLE.reset()
    try:
        rc, out, _ = _repl([
            "connect",
            "provider ollama",
            "ask draft an idea about harbor lights",
            "leave",
            "quit",
        ], owner, {"OLLAMA_HOST": f"http://127.0.0.1:{port}",
                  "OLLAMA_MODEL": MODEL_B})
        check("model: env-configured model reported to the user",
              f"model={MODEL_B}" in out, out[-400:])
        check("model: env-configured model reached the wire",
              len(DOUBLE.chat_payloads) == 1
              and DOUBLE.chat_payloads[0].get("model") == MODEL_B)
    finally:
        server.shutdown()
        _cleanup(owner)


def part_down_then_recovery():
    server, port = _serve()
    owner = unique_owner("dockdown")
    DOUBLE.reset()
    DOUBLE.tags_failures = 1  # first liveness probe fails
    try:
        rc, out, _ = _repl([
            "connect",
            "provider ollama",
            "ask draft an idea about first light",
            "ask draft an idea about second light",
            "leave",
            "quit",
        ], owner, {"OLLAMA_HOST": f"http://127.0.0.1:{port}",
                  "OLLAMA_MODEL": ""})
        check("down: first ask failed honestly as provider_failure",
              "Ask failed (provider_failure)" in out)
        check("down: second ask in the same session recovered",
              "PENDING in the Nursery" in out)
        check("down: exactly one chat request (the recovered one)",
              len(DOUBLE.chat_payloads) == 1,
              f"{len(DOUBLE.chat_payloads)}")
        st = _state(owner)
        pend = _pending_proposals(st)
        check("down: exactly one proposal exists (failure made none)",
              len([p for p in pend if p.get("label") == "Transport Idea"]) == 1,
              f"{pend}")
        steps = _session_steps(st)
        check("down: failure recorded with fixed code",
              ("ask", "rejected: provider_failure") in steps, f"{steps}")
    finally:
        server.shutdown()
        _cleanup(owner)


def part_dead_port():
    owner = unique_owner("dockdead")
    port = _closed_port()
    try:
        rc, out, _ = _repl([
            "connect",
            "provider ollama",
            "ask draft an idea about nowhere",
            "leave",
            "quit",
        ], owner, {"OLLAMA_HOST": f"http://127.0.0.1:{port}",
                  "OLLAMA_MODEL": ""})
        check("dead: unreachable server fails as provider_failure",
              "Ask failed (provider_failure)" in out)
        check("dead: no proposal claimed",
              "PENDING in the Nursery" not in out)
        st = _state(owner)
        check("dead: zero proposals persisted",
              _pending_proposals(st) == [])
    finally:
        _cleanup(owner)


def part_output_law_over_transport():
    server, port = _serve()
    owner = unique_owner("docklaw")
    DOUBLE.reset()
    try:
        rc, out, _ = _repl([
            "connect",
            "provider ollama",
            "ask MODE:malformed draft something",
            "ask MODE:authority draft something",
            "ask MODE:huge draft something",
            "leave",
            "quit",
        ], owner, {"OLLAMA_HOST": f"http://127.0.0.1:{port}",
                  "OLLAMA_MODEL": ""})
        check("law: malformed output rejected as invalid_output",
              "Ask failed (invalid_output)" in out)
        check("law: oversized output rejected as response_too_large",
              "Ask failed (response_too_large)" in out)
        check("law: all three asks crossed the transport",
              len(DOUBLE.chat_payloads) == 3,
              f"{len(DOUBLE.chat_payloads)}")
        check("law: no proposal claimed for any rejected output",
              "PENDING in the Nursery" not in out)
        st = _state(owner)
        check("law: zero proposals persisted",
              _pending_proposals(st) == [])
        steps = _session_steps(st)
        check("law: authority-shaped output rejected and recorded",
              steps.count(("ask", "rejected: invalid_output")) >= 2,
              f"{steps}")
    finally:
        server.shutdown()
        _cleanup(owner)


def smoke() -> bool:
    part_happy_transport()
    part_env_model_override()
    part_down_then_recovery()
    part_dead_port()
    part_output_law_over_transport()
    passed = sum(1 for _, ok in CHECKS if ok)
    print(f"=== Dock Transport (public path, real HTTP): "
          f"{passed}/{len(CHECKS)} ===")
    return passed == len(CHECKS)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
