"""R7.6 — Connected World proofs.

The `connect` scoped session is the public path to two existing
authorities: the InternetGate (default OFF, host allowlist, bounded
fetches) and the inference dock (explicit provider by name, host-held
credentials, screened I/O, PENDING proposals only). It adds no new
network or inference machinery.

Covers: the full connect flow on the real REPL public path; the gate
staying OFF by default and rejecting fetches; allowlist enforcement;
a REAL fetch through the gate against a local HTTP server (offline,
deterministic) with provenance evidence (host/status/bytes recorded,
content and URL never stored); docked `ask` creating a PENDING
proposal with the fake provider; provider selection discipline
(unknown provider -> DOCK_FAILED, key-shaped input rejected, invalid
name rejected — credentials are never entered); the protected screen
(grant-handle canary, zero disclosure); honest EOF (nothing from the
session persisted); gate state persisting through the leave save;
mutual exclusion with the workshop gate; the strict section schema;
stage-then-save failure recovery; and the bounds.

All fixtures use disposable-copy isolation (unique owners). The only
network touched is 127.0.0.1 (a test-local HTTP server).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer

CHECKS: list = []


def check(name: str, cond: bool, detail: str = "") -> None:
    CHECKS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f" — {detail}" if detail and not cond else ""))


def unique_owner(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def _repl(commands: list, owner: str, do_load: bool = False, timeout: int = 120):
    """Run the real REPL with piped commands. Returns (rc, stdout, stderr)."""
    cwd = os.path.abspath(".")
    args = [sys.executable, "-m", "form.repl", "--owner", owner]
    if do_load:
        args.append("--load")
    inp = "\n".join(commands) + "\n"
    result = subprocess.run(
        args, cwd=cwd, env={**os.environ, "PYTHONPATH": cwd},
        input=inp, capture_output=True, text=True, timeout=timeout)
    return result.returncode, result.stdout, result.stderr


def _state(owner: str) -> dict:
    from form.persist import _path
    with open(_path(owner)) as f:
        return json.load(f)


def _state_exists(owner: str) -> bool:
    from form.persist import _path
    return os.path.isfile(_path(owner))


def _cleanup(owner: str) -> None:
    from form.persist import _path, _cp_path
    for path in (_path(owner), _cp_path(owner)):
        try:
            os.remove(path)
        except OSError:
            pass


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = b"tidal resonance evidence page 42"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
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


def part_happy_path_and_provenance():
    server, port = _serve()
    owner = unique_owner("r76happy")
    try:
        rc, out, _ = _repl([
            "connect",
            "status",
            "fetch https://example.com",
            "internet on",
            "allow 127.0.0.1",
            f"fetch http://127.0.0.1:{port}/evidence?secret=1",
            "ask propose an idea about tidal resonance",
            "status",
            "leave",
            "proposals",
            "quit",
        ], owner)
        check("happy: repl exits clean", rc == 0)
        check("happy: gate OFF by default", "Internet gate: OFF" in out)
        check("happy: fetch rejected while gate off",
              "Internet gate OFF" in out)
        check("happy: real fetch through the gate succeeded",
              "Fetched http://127.0.0.1" in out
              and "tidal resonance evidence page 42" in out)
        check("happy: provenance note shown", "Provenance recorded" in out)
        check("happy: ask created a PENDING proposal",
              "PENDING in the Nursery" in out
              and "provider=fake" in out)
        check("happy: session saved on leave",
              "Connection session saved" in out)
        st = _state(owner)
        sessions = st["connection_sessions"]["sessions"]
        check("happy: one closed session record", len(sessions) == 1)
        if sessions:
            rec = next(iter(sessions.values()))
            steps = [(s["kind"], s["result"]) for s in rec["steps"]]
            check("happy: fetch provenance step recorded",
                  any(k == "fetch" and r.startswith(
                      "host=127.0.0.1 status=200 bytes=") 
                      for k, r in steps), f"{steps}")
            check("happy: gate-off rejection recorded",
                  ("fetch", "rejected: gate off") in steps)
            check("happy: ask step recorded",
                  ("ask", "proposal pending") in steps)
            blob = json.dumps(rec)
            check("happy: prompt text NOT in evidence",
                  "tidal resonance" not in blob.replace(
                      "host=127.0.0.1 status=200", ""))
            check("happy: URL path/query NOT in evidence",
                  "secret=1" not in blob and "/evidence" not in blob)
            check("happy: fetched content NOT in evidence",
                  "evidence page 42" not in blob)
        check("happy: gate ON persisted through the leave save",
              st["internet"].get("on") is True)
    finally:
        server.shutdown()
        _cleanup(owner)


def part_allowlist_enforced():
    owner = unique_owner("r76allow")
    try:
        rc, out, _ = _repl([
            "connect", "internet on",
            "fetch https://not-allowed-host.invalid/x",
            "leave", "quit",
        ], owner)
        check("allowlist: unlisted host rejected by the gate",
              "host not allowed" in out)
        st = _state(owner)
        rec = next(iter(st["connection_sessions"]["sessions"].values()))
        steps = [(s["kind"], s["result"]) for s in rec["steps"]]
        check("allowlist: rejection recorded with fixed code",
              ("fetch", "rejected: host not allowed") in steps,
              f"{steps}")
    finally:
        _cleanup(owner)


def part_provider_discipline():
    owner = unique_owner("r76prov")
    try:
        rc, out, _ = _repl([
            "connect",
            "provider bogus_provider_xyz",
            "ask propose something",
            "provider fake",
            "ask propose something real",
            "leave", "quit",
        ], owner)
        check("provider: unknown provider fails as DOCK_FAILED",
              "DOCK_FAILED" in out)
        check("provider: fake provider recovers and proposes",
              "PENDING in the Nursery" in out)
        st = _state(owner)
        rec = next(iter(st["connection_sessions"]["sessions"].values()))
        steps = [(s["kind"], s["result"]) for s in rec["steps"]]
        check("provider: dock failure recorded with fixed code",
              ("ask", "rejected: DOCK_FAILED") in steps, f"{steps}")
    finally:
        _cleanup(owner)

    owner = unique_owner("r76prov2")
    try:
        rc, out, _ = _repl([
            "connect",
            "provider openai key=sk-1234567890",
            "provider bad!name",
            "leave", "quit",
        ], owner)
        check("provider: key-shaped input never accepted",
              "that is not a connect command here" in out)
        check("provider: invalid name token rejected",
              "selected by a single name token only" in out)
        st = _state(owner)
        blob = json.dumps(st["connection_sessions"])
        check("provider: key material absent from evidence",
              "sk-1234567890" not in blob)
    finally:
        _cleanup(owner)


def part_protection():
    from form.open import open_program
    from form.dell_matrix import agent_coordinator as ac
    from form.dell_matrix import agent_authority as aa
    owner = unique_owner("r76prot")
    try:
        p = open_program(owner)
        pr = p.nursery.add("S1", words="r76 protection fixture idea")
        pid = pr.id
        coord = ac.new_coordinator(p)
        coord.register_agent("ta", persona_slots={"pilot": "manny"})
        grant = aa.issue_root_grant(p, issuer="t", subject="ta",
                                    target=pid, content_pid=pid)
        handle = grant["grant_id"]
        p.save()
        rc, out, _ = _repl(
            ["connect", f"ask use this token {handle}", "leave"], owner)
        check("protected line rejected", "Rejected: PROTECTED_MATERIAL" in out)
        check("handle absent from REPL output", handle not in out)
        from form.persist import _path
        with open(_path(owner), "rb") as f:
            blob = f.read().decode("utf-8", "replace")
        check("handle absent from persisted evidence", handle not in blob)
        recs = _state(owner)["connection_sessions"]["sessions"]
        if recs:
            kinds = [(s["kind"], s["result"]) for s in
                     next(iter(recs.values()))["steps"]]
            check("protected attempt recorded with safe code only",
                  ("protected", "rejected: PROTECTED_MATERIAL") in kinds,
                  f"{kinds}")
    finally:
        _cleanup(owner)


def part_eof_honesty():
    owner = unique_owner("r76eof")
    try:
        rc, out, _ = _repl(
            ["connect", "internet on", "ask propose an idea about x"],
            owner)  # EOF inside connect (no leave/quit)
        check("eof: session-not-saved stated plainly",
              "Connection session NOT saved (EOF)" in out)
        check("eof: nothing persisted from the session",
              not _state_exists(owner)
              or _state(owner)["connection_sessions"]["sessions"] == {})
        if _state_exists(owner):
            check("eof: gate change not persisted either",
                  _state(owner)["internet"].get("on") is not True)
    finally:
        _cleanup(owner)


def part_mutual_exclusion():
    owner = unique_owner("r76mux")
    try:
        rc, out, _ = _repl(["workshop bimo", "connect", "leave", "quit"],
                           owner)
        check("mux: connect inside workshop rejected by workshop gate",
              "Out of scope for the bimo workshop" in out)
        st = _state(owner)
        check("mux: no connection session recorded",
              st["connection_sessions"]["sessions"] == {})
        rc, out, _ = _repl(["connect", "forge", "leave", "quit"], owner,
                           do_load=True)
        check("mux: forge inside connect rejected as out of scope",
              "that is not a connect command here" in out)
    finally:
        _cleanup(owner)


def part_schema_strictness():
    from form.dell_matrix.connection_session import (
        ConnectionSession, validate_section, _MISSING)
    owner = "schemaowner"
    valid, mal = validate_section(_MISSING, owner)
    check("schema: absent = legacy", valid == {} and mal is None)
    valid, mal = validate_section(None, owner)
    check("schema: explicit null fails closed, preserved",
          valid == {} and mal is not None)
    valid, mal = validate_section({"version": True, "sessions": {}}, owner)
    check("schema: bool version fails closed",
          valid == {} and mal is not None)
    good = ConnectionSession.open(owner)
    good.record("enter", "connection entered")
    rec = good.closed_copy()
    section = {"version": 1, "sessions": {rec["session_id"]: rec}}
    valid, mal = validate_section(section, owner)
    check("schema: valid closed record accepted",
          rec["session_id"] in valid and mal is None)
    bad = dict(rec, owner="someoneelse")
    section = {"version": 1, "sessions": {rec["session_id"]: bad}}
    valid, mal = validate_section(section, owner)
    check("schema: foreign owner rejected + preserved",
          valid == {} and mal is not None)
    open_rec = good.to_dict()  # closed is None -> invalid as evidence
    section = {"version": 1, "sessions": {open_rec["session_id"]: open_rec}}
    valid, mal = validate_section(section, owner)
    check("schema: unclosed record rejected + preserved",
          valid == {} and mal is not None)
    section = {"version": 1, "sessions": {"other-id": rec}}
    valid, mal = validate_section(section, owner)
    check("schema: key/ID mismatch rejected + preserved",
          valid == {} and mal is not None)


def part_finish_failure_recovery():
    import form.repl as repl_mod
    from form.open import open_program
    from form.dell_matrix.connection_session import ConnectionSession
    owner = unique_owner("r76fail")
    try:
        p = open_program(owner)
        session = ConnectionSession.open(owner)
        session.record("enter", "connection entered")
        from form import persist_rest
        orig_save = persist_rest.save

        def _boom(prog, *a, **k):
            raise RuntimeError("simulated save failure")
        persist_rest.save = _boom
        said = []
        orig_say = repl_mod._say
        repl_mod._say = lambda m: said.append(str(m))
        try:
            p2, s2 = repl_mod._finish_connection(p, session)
        finally:
            persist_rest.save = orig_save
            repl_mod._say = orig_say
        out = "\n".join(said)
        check("finish: save failure reported as SAVE_FAILED",
              "SAVE_FAILED" in out)
        check("finish: session retained for retry", s2 is session)
        check("finish: no evidence staged on failure",
              not getattr(p, "connection_sessions", None))
    finally:
        _cleanup(owner)


def part_bounds():
    from form.dell_matrix.connection_session import (
        ConnectionSession, serialize_section)
    s = ConnectionSession.open("o")
    for i in range(60):
        s.record("status", "shown")
    check("bounds: steps capped at 50", len(s.steps) == 50)
    sessions = {}
    for i in range(12):
        one = ConnectionSession.open("o")
        one.session_id = f"s{i:02d}"
        one.started = f"2026-10-22T00:{i:02d}:00Z"
        rec = one.closed_copy()
        sessions[rec["session_id"]] = rec
    section = serialize_section(sessions, None, "o")
    check("bounds: sessions capped at 10",
          len(section["sessions"]) == 10)


def smoke() -> bool:
    part_happy_path_and_provenance()
    part_allowlist_enforced()
    part_provider_discipline()
    part_protection()
    part_eof_honesty()
    part_mutual_exclusion()
    part_schema_strictness()
    part_finish_failure_recovery()
    part_bounds()
    passed = sum(1 for _, ok in CHECKS if ok)
    print(f"=== R7.6 Connected World: {passed}/{len(CHECKS)} ===")
    return passed == len(CHECKS)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
