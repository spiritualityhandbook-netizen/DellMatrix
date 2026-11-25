#!/usr/bin/env python3
"""72-60 — Four-way equivalence: Python API / GUI-API / REPL / Python.

Register row 72-60: identical executable semantics across all four
surfaces for a representative program set. Prior evidence proved
GUI/API through public paths (gui_api_test); the register's named
remaining gap was the REPL leg. Grounding + probe:
hidden_files/72-60_ground.md, 72-60_probe.py (main 16c50bf).

Contract under test (like-for-like law from the grounding):
- Receipts are compared Python vs GUI/API directly (normalized:
  ok, error, any_skipped, per-atom dell/ok/skipped).
- The REPL leg (literal `python3 -m form.repl` subprocess,
  REAL_USER_PATH) is compared on (a) stdout-visible per-seed
  effects and (b) the final snapshot AFTER save+reload against
  the Python/GUI legs ALSO put through save+reload — never
  in-memory vs reloaded. last_result is excluded from the
  reloaded comparison: probe2 proved it is non-persistent through
  save/load on ALL surfaces (a common save/load property, not a
  surface divergence).

Representative seeds (same set as the probe): Create, Set, Get,
labelled Nurture, bare Nurture (failure honesty), a Create >>
reserved-151 chain (skipped honesty), and a Set >> Set chain
(state accumulation).

Run: python3 -m form.four_way_equivalence_test
"""

import glob
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import urllib.error
import urllib.request
import uuid
from http.server import ThreadingHTTPServer

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import gui.server as studio
from form.mandell.executor import execute_seed
from form.open import open_program
from form.persist import _STATE_DIR, _safe_owner, load as persist_load

RESULTS = []
_CLEANUP_ERRORS = []
RUN = uuid.uuid4().hex[:8]
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

SEEDS = [
    "08[Create] :: EqAlpha",
    "55[Set] :: tempo=120",
    "56[Get] :: tempo",
    "37[Nurture] :: EqIdeaOne",
    "37[Nurture]",
    "08[Create] :: EqBeta >> 151[Harmonic] :: x",
    "55[Set] :: mode=probe >> 55[Set] :: tempo=99",
]


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))
    print(f"{'PASS' if ok else 'FAIL'} {name} {detail}")


def cleanup(owner):
    safe = _safe_owner(owner)
    state = _STATE_DIR
    if not os.path.isdir(state):
        return
    for name in os.listdir(state):
        if safe in name:
            p = os.path.join(state, name)
            try:
                shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
            except OSError as e:
                _CLEANUP_ERRORS.append(f"{p}: {e}")


def snap_core(program):
    s = studio._state_snapshot(program)
    return {
        "store": s.get("store"),
        "nursery_pending": program.nursery.summary().get("pending"),
        "plane_labels": sorted(n.get("label") for n in program.nodes_payload()),
    }


def norm(result):
    atoms = [(r.get("dell"), r.get("ok"), r.get("skipped"))
             for r in (result.get("atom_results") or [])]
    return {"ok": result.get("ok"), "error": result.get("error"),
            "any_skipped": result.get("any_skipped"), "atoms": atoms}


_TOKEN = None


def req(base, method, path, body=None):
    global _TOKEN
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Content-Type": "application/json"} if data else {}
    if method == "POST":
        if _TOKEN is None:
            page = urllib.request.urlopen(base + "/", timeout=30).read().decode()
            _TOKEN = re.search(r'name="studio-token"\s+content="([^"]+)"', page).group(1)
        headers["X-Studio-Token"] = _TOKEN
    r = urllib.request.Request(base + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=30) as res:
            return res.status, json.loads(res.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())


def main():
    owners = {"py": f"Eq60Py{RUN}", "gui": f"Eq60Gui{RUN}", "repl": f"Eq60Repl{RUN}"}
    for o in owners.values():
        cleanup(o)
    try:
        # --- Python leg ---
        prog_py = open_program(owners["py"])
        receipts_py = [norm(execute_seed(prog_py, s)) for s in SEEDS]
        snap_py_mem = snap_core(prog_py)

        # --- GUI/API leg (real Studio HTTP) ---
        server = ThreadingHTTPServer(("127.0.0.1", 0), studio._Handler)
        base = "http://127.0.0.1:%d" % server.server_address[1]
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            receipts_gui = []
            for s in SEEDS:
                _, payload = req(base, "POST", "/api/execute",
                                 {"seed": s, "owner": owners["gui"]})
                receipts_gui.append(norm(payload.get("result") or {}))
            prog_gui = studio._get_program(owners["gui"])
            snap_gui_mem = snap_core(prog_gui)
        finally:
            server.shutdown(); server.server_close()
            studio._PROGRAMS.pop(owners["gui"], None)

        check("A1.receipts_py_gui_identical_all_seeds",
              receipts_py == receipts_gui,
              f"py={receipts_py} gui={receipts_gui}" if receipts_py != receipts_gui else "7/7")
        check("A2.snapshot_py_gui_identical_in_memory",
              snap_py_mem == snap_gui_mem,
              f"{snap_py_mem} vs {snap_gui_mem}" if snap_py_mem != snap_gui_mem else "")
        check("A3.bare_nurture_failure_honest_both",
              receipts_py[4]["ok"] is False and receipts_gui[4]["ok"] is False,
              f"py_ok={receipts_py[4]['ok']} gui_ok={receipts_gui[4]['ok']}")
        check("A4.reserved_chain_skipped_honest_both",
              receipts_py[5]["any_skipped"] is True and receipts_gui[5]["any_skipped"] is True
              and any(a[2] for a in receipts_py[5]["atoms"]),
              f"py_skipped={receipts_py[5]['any_skipped']}")
        check("A5.final_store_expected",
              snap_py_mem["store"] == {"tempo": 99, "mode": "probe"}
              or snap_py_mem["store"] == {"tempo": "99", "mode": "probe"},
              f"store={snap_py_mem['store']}")

        # --- Save+reload both in-process legs (like-for-like basis) ---
        prog_py.save()
        snap_py_rel = snap_core(persist_load(owners["py"]))
        prog_gui.save()
        snap_gui_rel = snap_core(persist_load(owners["gui"]))
        check("B1.reloaded_snapshots_py_gui_identical",
              snap_py_rel == snap_gui_rel,
              f"{snap_py_rel} vs {snap_gui_rel}" if snap_py_rel != snap_gui_rel else "")
        check("B2.reloaded_store_survives",
              snap_py_rel["store"] == snap_py_mem["store"],
              f"reloaded={snap_py_rel['store']} mem={snap_py_mem['store']}")

        # --- REPL leg (REAL_USER_PATH subprocess) ---
        inp = "\n".join(SEEDS + ["save", "quit"]) + "\n"
        proc = subprocess.run(
            [sys.executable, "-m", "form.repl", "--owner", owners["repl"]],
            input=inp, capture_output=True, text=True, cwd=ROOT, timeout=300)
        out = proc.stdout or ""
        check("C1.repl_exit_clean", proc.returncode == 0,
              f"rc={proc.returncode} err={(proc.stderr or '')[-200:]}")
        check("C2.repl_stdout_shows_created_labels",
              "EqAlpha" in out and "EqBeta" in out,
              "")
        check("C3.repl_stdout_shows_nurtured_idea", "EqIdeaOne" in out, "")
        check("C4.repl_stdout_bare_nurture_failure_visible",
              "add idea requires a label" in out,
              f"tail={out[-300:]!r}" if "add idea requires a label" not in out else "")
        check("C5.repl_stdout_reserved_honesty_visible",
              "151" in out and ("reserved" in out.lower() or "skipped" in out.lower()),
              f"tail={out[-300:]!r}" if "151" not in out else "")
        snap_repl_rel = snap_core(persist_load(owners["repl"]))
        check("C6.repl_reloaded_snapshot_equals_py_gui",
              snap_repl_rel == snap_py_rel == snap_gui_rel,
              f"repl={snap_repl_rel} py={snap_py_rel}" if snap_repl_rel != snap_py_rel else "")
    finally:
        for o in owners.values():
            cleanup(o)

    check("Z.cleanup", not _CLEANUP_ERRORS, "; ".join(_CLEANUP_ERRORS))
    failed = [n for n, ok, _ in RESULTS if not ok]
    print(f"four_way_equivalence: {len(RESULTS) - len(failed)}/{len(RESULTS)} PASS")
    if failed:
        print("FAILURES:", ", ".join(failed))
    return 1 if failed else 0


def smoke():
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
