#!/usr/bin/env python3
"""72-17 R-B — machine sentinel '__RENDER__' inside human messages.

Defect (confirmed by the 72-17 investigation, PRs #304-#306;
DIRECTOR_REPORT_72_17_SHOW_SENTINEL): a bare 09[Show] makes
executor_leaf append the literal token '__RENDER__' to the
result's human-readable `messages` list. The REPL — the token's
only intended consumer — intercepts it (repl.py _apply_seed_result)
and prints Program.render(); every other display surface must
know the same trick, and the Studio frontend does not: it dumps
the raw result JSON into the user console (gui/static/app.js
execute()), so the placeholder is USER-VISIBLE in Studio.

Repair shape R-B (SLEEP v2 queue item 3, Ace FIX-FIRST; the
Director's preferred candidate in his 2026-11-05 reviews):
the executor stops placing the token in `messages` and instead
sets a structured render directive on the result; the REPL keys
off the field. Pinned contract:

  - bare 09[Show] via the front door: ok=True, NO '__RENDER__'
    anywhere in messages, and result["directive"] == "render".
  - labeled Show variants (avatar / lattice / visual) keep their
    exact current output and carry NO directive.
  - other Dells carry NO directive.
  - a chain containing bare Show: chain messages carry NO token
    and the chain result propagates directive == "render".
  - the Studio /api/execute payload for bare Show carries the
    directive and NO token anywhere in the serialized result.
  - REPL parity (REAL_USER_PATH controls): a piped session still
    shows the real render board and never the token — true before
    the repair (interceptor) and must stay true after it (field).

Labels: front-door / chain checks are INTEGRATION; the Studio
check is cross-process against the real server; the REPL checks
are REAL_USER_PATH (cross-process) controls.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
import urllib.request
import uuid

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def _owner(tag):
    return tag + uuid.uuid4().hex[:10]


def smoke() -> bool:
    from form.open import Program
    from form.mandell.executor import execute_seed

    p = Program(owner=_owner("RB"))

    # -- bare Show: the defect surface -------------------------------
    r = execute_seed(p, "09[Show]")
    msgs = r.get("messages") or []
    check("bare.ok", r.get("ok") is True, f"ok={r.get('ok')}")
    check("bare.no_sentinel_in_messages", "__RENDER__" not in msgs,
          f"messages={msgs!r}")
    check("bare.no_sentinel_joined",
          "__RENDER__" not in " ".join(str(m) for m in msgs), "")
    check("bare.directive_render", r.get("directive") == "render",
          f"directive={r.get('directive')!r}")

    # -- labeled variants: controls (exact output, no directive) -----
    st = p.avatar_status()
    r = execute_seed(p, "09[Show] :: avatar")
    check("avatar.unchanged_no_directive",
          (r.get("messages") or [])[-1:]
          == [f"{st['look']}  {st['describe']}"]
          and not r.get("directive"),
          f"messages={r.get('messages')!r} directive={r.get('directive')!r}")
    r = execute_seed(p, "09[Show] :: lattice")
    m = r.get("messages") or []
    check("lattice.unchanged_no_directive",
          bool(m) and str(m[-1]).startswith("HarmonicLattice size=")
          and not r.get("directive"),
          f"directive={r.get('directive')!r}")
    r = execute_seed(p, "09[Show] :: visual")
    m = r.get("messages") or []
    check("visual.unchanged_no_directive",
          "Visual ready." in m and not r.get("directive"),
          f"messages={m!r} directive={r.get('directive')!r}")

    # -- a non-Show Dell carries no directive -------------------------
    r = execute_seed(p, "08[Create] :: directiveprobe")
    check("create.no_directive", not r.get("directive"),
          f"directive={r.get('directive')!r}")

    # -- chain: token must not pass through; directive propagates ----
    p2 = Program(owner=_owner("RBC"))
    r = execute_seed(p2, "08[Create]:: chainprobe > 09[Show]")
    msgs = r.get("messages") or []
    check("chain.no_sentinel_in_messages", "__RENDER__" not in msgs,
          f"messages={msgs!r}")
    check("chain.directive_render", r.get("directive") == "render",
          f"directive={r.get('directive')!r}")

    # -- REPL parity controls (REAL_USER_PATH, cross-process) --------
    owner = _owner("RBREPL")
    cp = subprocess.run(
        [sys.executable, "-m", "form.repl", "--owner", owner],
        input="08[Create]:: probeidea\n09[Show]\n",
        capture_output=True, text=True, timeout=120)
    out = cp.stdout + cp.stderr
    check("repl.no_sentinel", "__RENDER__" not in out, "")
    check("repl.render_shown", f"DellMatrix · owner={owner}" in out, "")

    # -- Studio API (cross-process, real server) ----------------------
    port = 8977
    sowner = _owner("RBSTUDIO")
    srv = subprocess.Popen(
        [sys.executable, "gui/server.py", "--port", str(port),
         "--owner", sowner],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        deadline = time.time() + 30
        up = False
        while time.time() < deadline:
            try:
                urllib.request.urlopen(
                    f"http://127.0.0.1:{port}/", timeout=2)
                up = True
                break
            except Exception:
                if srv.poll() is not None:
                    break
                time.sleep(0.5)
        if not up:
            check("studio.server_up", False, "server did not come up")
        else:
            with urllib.request.urlopen(
                    f"http://127.0.0.1:{port}/", timeout=5) as resp:
                html = resp.read().decode()
            mtok = re.search(
                r'name="studio-token"\s+content="([^"]+)"', html)
            if not mtok:
                check("studio.token_bootstrap", False,
                      "studio-token meta not found")
            else:
                req = urllib.request.Request(
                    f"http://127.0.0.1:{port}/api/execute",
                    data=json.dumps(
                        {"seed": "09[Show]", "owner": sowner}).encode(),
                    headers={"Content-Type": "application/json",
                             "X-Studio-Token": mtok.group(1)},
                    method="POST")
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read().decode())
                result = data.get("result") or {}
                smsgs = result.get("messages") or []
                check("studio.no_sentinel_in_messages",
                      "__RENDER__" not in smsgs,
                      f"messages={smsgs!r}")
                check("studio.no_sentinel_serialized",
                      "__RENDER__" not in json.dumps(result), "")
                check("studio.directive_render",
                      result.get("directive") == "render",
                      f"directive={result.get('directive')!r}")
    finally:
        srv.terminate()
        try:
            srv.wait(timeout=10)
        except Exception:
            srv.kill()

    failed = [n for n, ok in RESULTS if not ok]
    print(f"show_render_directive: "
          f"{len(RESULTS) - len(failed)}/{len(RESULTS)}")
    return not failed


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
