"""R7.7 — Grand Integration: Phase 7 as one synchronized system.

Terminal Phase 7 circuit (draft R7.5-block: "one synchronized
system, no-theater audit"). No new production machinery: this suite
proves the five Phase 7 surfaces compose on ONE owner in ONE
continuous real-user-path session, and that the accumulated
persisted state passes every circuit's own strict validator.

Scenario (single REPL process, fresh owner):
  onboard (all four moves verified -> graduation to beginner)
  -> perspective studio (compose -> leave)
  -> workshop bimo (in-scope command -> leave)
  -> forge (dock -> save a named configuration -> leave)
  -> connect (gate on -> allow local host -> real fetch against a
     test-local server -> ask the fake provider -> leave)

Cross-surface invariants proven in the same run: no scoped
environment can be entered from inside another (studio rejects
'forge', forge rejects 'connect', connect rejects 'onboard',
workshop rejects 'connect'); every surface's evidence lands in its
own strict section of the SAME state file; the live BIMO body equals
the forged configuration; the connect proposal is pending (not
confirmed) after reload; onboarding stays complete after reload.

The no-theater audit then re-validates the accumulated sections with
each circuit's own validate function: all must accept their records
with zero malformed — five independent stage-then-save cycles must
not corrupt one another's evidence.

All fixtures use disposable-copy isolation (unique owner). The only
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


def _repl(commands: list, owner: str, do_load: bool = False, timeout: int = 300):
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


def _cleanup(owner: str) -> None:
    from form.persist import _path, _cp_path
    for path in (_path(owner), _cp_path(owner)):
        try:
            os.remove(path)
        except OSError:
            pass
    demo = f"DEMO_TUTORIAL_{owner}"
    for path_owner in (demo,):
        from form.persist import _path as _p2, _cp_path as _c2
        for path in (_p2(path_owner), _c2(path_owner)):
            try:
                os.remove(path)
            except OSError:
                pass


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = b"grand integration evidence page"
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
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, port


def part_grand_scenario():
    server, port = _serve()
    owner = unique_owner("r77grand")
    try:
        rc, out, _ = _repl([
            # R7.4 onboarding: full rhythm, completion, graduation.
            "onboard",
            "create an idea called Seedling detail: first goals: learn",
            "grow ideas 1",
            "look",
            "save",
            # R7.2 studio: compose; 'forge' inside must be rejected.
            "perspective studio",
            'compose [{"id":"v1","pos":[0,0],"facing":"E"}]',
            "forge",
            "leave",
            # R7.3 workshop: in-scope command; 'connect' rejected.
            "workshop bimo",
            "bimo",
            "connect",
            "leave",
            # R7.5 forge: stage + commit a named configuration;
            # 'connect' inside must be rejected.
            "forge",
            "dock logic manny",
            "dock voice mansplainer",
            "connect",
            "save integration-crew",
            "leave",
            # R7.6 connect: gated fetch + docked ask; 'onboard'
            # inside must be rejected.
            "connect",
            "internet on",
            "allow 127.0.0.1",
            f"fetch http://127.0.0.1:{port}/",
            "ask propose an idea about grand integration",
            "onboard",
            "leave",
            "quit",
        ], owner)
        check("grand: repl exits clean", rc == 0)
        check("grand: onboarding completed + graduated in-run",
              "Onboarding complete" in out
              and "first-run → beginner" in out)
        for mv in ("Create an idea", "Grow, then confirm", "Look around",
                   "Save and load"):
            check(f"grand: move verified: {mv}", f"Verified: {mv}" in out)
        check("grand: forge rejected inside studio",
              "Studio: command out of scope" in out)
        check("grand: forge entered exactly once (legitimately)",
              out.count("BIMO Forge — build") == 1)
        check("grand: connect rejected inside workshop",
              "Out of scope for the bimo workshop" in out)
        check("grand: connect rejected inside forge",
              "that is not a forge command here" in out)
        check("grand: onboard rejected inside connect",
              "that is not a connect command here" in out)
        check("grand: forged configuration committed",
              "Committed 'integration-crew'" in out)
        check("grand: fetch through the gate succeeded",
              "Fetched http://127.0.0.1" in out)
        check("grand: docked ask pending",
              "PENDING in the Nursery" in out)

        st = _state(owner)
        check("grand: persisted level is beginner",
              (st.get("ux") or {}).get("mode") == "beginner")
        ob = st["onboarding_sessions"]["sessions"]
        check("grand: onboarding evidence present + completed",
              len(ob) == 1
              and next(iter(ob.values()))["completed"] is True)
        check("grand: studio evidence present",
              len(st["studio_sessions"]["sessions"]) == 1)
        check("grand: workshop evidence present",
              len(st["workshop_sessions"]["sessions"]) == 1)
        check("grand: forge evidence present",
              len(st["forge_sessions"]["sessions"]) == 1)
        cfg = st["bimo_configurations"]["configurations"].get(
            "integration-crew")
        check("grand: named configuration stored exactly",
              cfg is not None and cfg["slots"]["logic"] == "manny"
              and cfg["slots"]["voice"] == "mansplainer")
        check("grand: live BIMO body equals the forged configuration",
              st["bimo"]["slots"]["logic"] == "manny"
              and st["bimo"]["slots"]["voice"] == "mansplainer")
        cs = st["connection_sessions"]["sessions"]
        check("grand: connection evidence present", len(cs) == 1)
        if cs:
            steps = [(s["kind"], s["result"]) for s in
                     next(iter(cs.values()))["steps"]]
            check("grand: fetch provenance in connection evidence",
                  any(k == "fetch" and r.startswith(
                      "host=127.0.0.1 status=200") for k, r in steps),
                  f"{steps}")
            check("grand: ask outcome in connection evidence",
                  ("ask", "proposal pending") in steps)
        return owner, st
    finally:
        server.shutdown()


def part_reload_coherence(owner):
    try:
        rc, out, _ = _repl([
            "onboard",
            "proposals",
            "forge",
            "load integration-crew",
            "status",
            "leave",
            "quit",
        ], owner, do_load=True)
        check("reload: onboarding reports already complete",
              "Onboarding already complete" in out)
        check("reload: level stays beginner", "mode=beginner" in out)
        check("reload: connect proposal still pending after reload",
              "docked_idea" in out and "[new]" in out)
        check("reload: forged configuration loadable in a new forge",
              "Staged configuration 'integration-crew'" in out)
    finally:
        _cleanup(owner)


def part_no_theater_audit(owner, st):
    """Every accumulated section passes its OWN strict validator."""
    from form.dell_matrix.perspective_studio import (
        validate_section as v_studio)
    from form.dell_matrix.workshop_session import (
        validate_section as v_workshop)
    from form.dell_matrix.onboarding_session import (
        validate_section as v_onboarding)
    from form.dell_matrix.bimo_forge import (
        validate_sessions_section as v_forge,
        validate_configurations_section as v_configs)
    from form.dell_matrix.connection_session import (
        validate_section as v_connection)
    cases = [
        ("studio", v_studio, st["studio_sessions"], 1),
        ("workshop", v_workshop, st["workshop_sessions"], 1),
        ("forge sessions", v_forge, st["forge_sessions"], 1),
        ("configurations", v_configs, st["bimo_configurations"], 1),
        ("connection", v_connection, st["connection_sessions"], 1),
    ]
    for label, fn, raw, expected in cases:
        valid, malformed = fn(raw, owner)
        check(f"audit: {label} section revalidates clean",
              len(valid) == expected and malformed is None,
              f"valid={len(valid)} malformed={malformed}")
    valid, malformed, meta = v_onboarding(st["onboarding_sessions"], owner)
    check("audit: onboarding section revalidates clean",
          len(valid) == 1 and malformed is None
          and meta.get("begun") is True)


def smoke() -> bool:
    owner, st = part_grand_scenario()
    part_no_theater_audit(owner, st)
    part_reload_coherence(owner)
    passed = sum(1 for _, ok in CHECKS if ok)
    print(f"=== R7.7 Grand Integration: {passed}/{len(CHECKS)} ===")
    return passed == len(CHECKS)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
