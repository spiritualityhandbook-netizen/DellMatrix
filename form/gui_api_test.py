#!/usr/bin/env python3
"""DellMatrix Studio GUI API regression (P5).

Drives the REAL Studio server (gui.server) over HTTP on an
ephemeral port, against throwaway owners whose state files are
removed exactly afterwards (program_/nursery_/ideas_). The
server is a front-end, so every check goes through the public
paths it wraps: open_program, execute_seed, parse_seed, the
canonical DELLS registry and the view_rooms growth lens.

Contract coverage:
  * static assets 200 + content markers; unknown path 404
  * /api/dells == the canonical registry (100, fidelity per Dell)
  * /api/parse: real atoms for a valid seed; honest refusal
  * /api/execute: Set/Get store round-trip visible in /api/state
  * skipped honesty: a reserved Dell (151[Harmonic]) is reported
    skipped with its reason, never as executed
  * every example seed shipped in index.html executes ok=True
  * /api/growth: lens stages equal the fixture plants' own
    stages, attributed by the growth force (canonical authority)
  * /api/owner: owner isolation (B empty, A intact on return)
  * error states: empty seed / non-string seed / non-JSON body
    are 400s with an error message, never a crash

Regress entry: smoke() -> True, final line prints n/m.
"""
from __future__ import annotations

import html as html_mod
import json
import os
import re
import shutil
import sys
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gui.server as studio  # noqa: E402
from form.mandell.registry import DELLS  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OWNERS = ("GuiApiTestA", "GuiApiTestB", "GuiApiTestEx")
CHECKS = []


def check(name, cond):
    CHECKS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")
    if not cond:
        raise AssertionError(name)


def _cleanup(owner):
    state = os.path.join(ROOT, "form", "state")
    for name in (f"program_{owner}.json", f"nursery_{owner}.json"):
        path = os.path.join(state, name)
        if os.path.exists(path):
            os.remove(path)
    ideas = os.path.join(state, f"ideas_{owner}")
    if os.path.isdir(ideas):
        shutil.rmtree(ideas)


_TOKEN = None


def _req(base, method, path, body=None, raw=None):
    # Harness transport speaks the legitimate client's protocol
    # (Studio security circuit): POSTs carry the per-launch session
    # token served inside the index page, exactly as the browser
    # does. All checks and assertions below are unchanged.
    global _TOKEN
    data = raw
    headers = {}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if raw is not None:
        headers["Content-Type"] = "application/json"
    if method == "POST":
        if _TOKEN is None:
            _, page0 = _req(base, "GET", "/")
            found = re.search(
                r'name="studio-token"\s+content="([^"]+)"', page0)
            _TOKEN = found.group(1) if found else ""
        headers["X-Studio-Token"] = _TOKEN
    req = urllib.request.Request(base + path, data=data, headers=headers,
                                 method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            return res.status, res.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")


def _json(base, method, path, body=None, raw=None):
    status, text = _req(base, method, path, body=body, raw=raw)
    try:
        return status, json.loads(text)
    except ValueError:
        return status, text


def run_all():
    for owner in OWNERS:
        _cleanup(owner)
    saved_owner = studio._ACTIVE_OWNER
    server = ThreadingHTTPServer(("127.0.0.1", 0), studio._Handler)
    base = "http://127.0.0.1:%d" % server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        a, b, ex = OWNERS

        # --- static assets -------------------------------------
        status, page = _req(base, "GET", "/")
        check("GET / 200", status == 200)
        check("index carries the Studio wordmark",
              "DELLMATRIX" in page and "STUDIO" in page
              and 'class="brand"' in page)
        status, js = _req(base, "GET", "/app.js")
        check("GET /app.js 200 + outcome-painting code shipped",
              status == 200 and "buildOutcome" in js
              and "groupByStage" in js)
        status, css = _req(base, "GET", "/style.css")
        check("GET /style.css 200 + studio theme shipped",
              status == 200 and ".canvas-empty" in css)
        status, payload = _json(base, "GET", "/no-such-path")
        check("unknown path is an honest 404",
              status == 404 and payload.get("ok") is False)

        # --- /api/dells registry fidelity ----------------------
        status, payload = _json(base, "GET", "/api/dells")
        dells = payload.get("dells") or []
        check("/api/dells 200 with exactly 100 Dells",
              status == 200 and len(dells) == 100)
        check("dell numbers are 0..99 in order",
              [d["num"] for d in dells] == list(range(100)))
        check("every dell name matches the canonical registry",
              all(d["name"] == (DELLS.get(d["num"]) or {}).get("name", "")
                  for d in dells))
        check("core split is I for 00-50, II for 51-99",
              all(d["core"] == ("I" if d["num"] <= 50 else "II")
                  for d in dells))

        # --- /api/parse ----------------------------------------
        status, payload = _json(base, "POST", "/api/parse",
                                {"seed": "55[Set] :: k=1"})
        parse = payload.get("parse") or {}
        atoms = parse.get("atoms") or []
        check("parse of a valid seed is ok with the real atom",
              parse.get("ok") is True and len(atoms) == 1
              and atoms[0]["num"] == 55 and atoms[0]["name"] == "Set")
        status, payload = _json(base, "POST", "/api/parse",
                                {"seed": "garbage text"})
        parse = payload.get("parse") or {}
        check("unparseable seed is an honest refusal, not a guess",
              parse.get("ok") is False and bool(parse.get("error"))
              and parse.get("atoms") == [])
        status, payload = _json(base, "POST", "/api/parse", {"seed": 42})
        check("non-string seed is a 400 with an error",
              status == 400 and payload.get("ok") is False)

        # --- /api/execute + /api/state round-trip --------------
        status, payload = _json(base, "POST", "/api/execute",
                                {"seed": "55[Set] :: tempo=120",
                                 "owner": a})
        check("execute Set ok", payload.get("result", {}).get("ok") is True)
        check("execute response state shows the stored value",
              (payload.get("state") or {}).get("store", {}).get("tempo")
              == "120")
        status, payload = _json(base, "GET", f"/api/state?owner={a}")
        state = payload.get("state") or {}
        check("/api/state round-trips the store for the owner",
              state.get("owner") == a
              and state.get("store", {}).get("tempo") == "120"
              and state.get("store_count") == 1)

        # --- skipped honesty ------------------------------------
        status, payload = _json(
            base, "POST", "/api/execute",
            {"seed": "08[Create] :: Alpha >> 151[Harmonic] :: x",
             "owner": a})
        result = payload.get("result") or {}
        receipts = {r["dell"]: r for r in result.get("atom_results") or []}
        check("reserved Dell is reported skipped with its reason",
              result.get("any_skipped") is True
              and receipts.get(151, {}).get("skipped") is True
              and receipts.get(151, {}).get("ok") is False
              and "reserved/not-active" in
              (receipts.get(151, {}).get("reason") or ""))
        check("the executed atom in the same chain is honestly ok",
              receipts.get(8, {}).get("ok") is True
              and receipts.get(8, {}).get("skipped") is False)

        # --- shipped examples all execute -----------------------
        examples = [html_mod.unescape(v) for v in
                    re.findall(r'<option value="([^"]*)"', page)
                    if "[" in v]
        check("index ships at least 14 example seeds", len(examples) >= 14)
        bad = []
        for seed in examples:
            _, payload = _json(base, "POST", "/api/execute",
                               {"seed": seed, "owner": ex})
            if (payload.get("result") or {}).get("ok") is not True:
                bad.append(seed)
        check("every shipped example executes ok=True", not bad)

        # --- /api/growth lens fidelity --------------------------
        prog = studio._get_program(a)
        growth = prog.forces.growth
        growth.plant("GuiApiFixture")
        for _ in range(4):
            growth.grow_all(2.0)
        plant_stage = growth.plants[-1]["stage"]
        check("fixture plant actually grew past seed",
              plant_stage != "seed")
        status, payload = _json(base, "GET", f"/api/growth?owner={a}")
        nodes = (payload.get("growth") or {}).get("nodes") or []
        mine = [n for n in nodes if n.get("label") == "GuiApiFixture"]
        check("/api/growth node stage equals the plant's own stage",
              len(mine) == 1 and mine[0].get("stage") == plant_stage
              and mine[0].get("stage_source") == "growth_force")
        status, payload = _json(base, "GET", f"/api/growth?owner={b}")
        check("/api/growth is honestly empty for a plantless owner",
              (payload.get("growth") or {}).get("nodes") == []
              and (payload.get("growth") or {}).get("plant_count") == 0)

        # --- /api/owner isolation -------------------------------
        status, payload = _json(base, "POST", "/api/owner", {"owner": b})
        state = payload.get("state") or {}
        check("switching to owner B shows B's own empty store",
              state.get("owner") == b and state.get("store_count") == 0)
        status, payload = _json(base, "POST", "/api/owner", {"owner": a})
        state = payload.get("state") or {}
        check("switching back to A keeps A's store intact",
              state.get("owner") == a
              and state.get("store", {}).get("tempo") == "120")

        # --- error states ---------------------------------------
        status, payload = _json(base, "POST", "/api/execute",
                                {"seed": "   ", "owner": a})
        check("empty seed is a 400 with an error, not a crash",
              status == 400 and payload.get("ok") is False
              and bool(payload.get("error")))
        status, payload = _json(base, "POST", "/api/execute",
                                raw=b"this is not json")
        check("non-JSON body is a 400 with an error, not a crash",
              status == 400 and payload.get("ok") is False)
    finally:
        server.shutdown()
        server.server_close()
        studio._ACTIVE_OWNER = saved_owner
        for owner in OWNERS:
            studio._PROGRAMS.pop(owner, None)
            _cleanup(owner)

    print(f"GUI-API: {sum(1 for _, c in CHECKS if c)}/{len(CHECKS)} GREEN")


def smoke() -> bool:
    """Regress entry point: run all checks, return True on success."""
    try:
        run_all()
        return True
    except Exception as e:
        print(f"GUI-API SMOKE FAILED: {e}")
        return False


if __name__ == "__main__":
    run_all()
