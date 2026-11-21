#!/usr/bin/env python3
"""Q1 C-B PREP — journaled Exchange import/recovery transaction,
failing-first on current main (Part I, MWL #118 / DD-07 / PR #294).

AUTHORITY AND GATE STATUS (read first):
- PR #294 Q1 GATE HOLD CONTINUES (Director 7040542941, 2026-11-20).
  This file is PREPARATION ONLY, produced under that ruling's explicit
  "UNBLOCK NOW (PREPARATION/TESTS ONLY)" paragraph. It contains NO
  product code, changes NO product behavior, and does not merge,
  close, or alter PR #294.
- Design disposition (Director 7040542941): C-B is the smallest
  independent journaled T4 Exchange/recovery lock+idempotent-disposal
  circuit (W1/W2/W3). C-A (72-28 ordinary-save pair atomicity) is a
  SEPARATE circuit and is NOT covered here except where a check names
  it as out of scope.
- Companion design package: director-reports/
  Q1_CB_TRANSACTION_DESIGN_2026-11-20.md (lock-order table, per-case
  expected outcomes, P3/P5 contracts).

WHAT THIS SUITE DOES: it re-runs the Q1 audit windows W1/W2/W3 as
genuine child OS processes against CURRENT MAIN product code (the
audit's two-week-old receipts are not trusted as current), plus the
P3 idempotent-disposal and P5 clean-read / fail-closed invariants the
Director named mandatory. Every check asserts the REPAIRED contract
from DIRECTOR_Q1_REPAIR_PLAN.md (Amendment D/F bifurcation):

  W1  recovery and the canonical save serialize on the one owner
      lock; recovery re-reads under the lock after the save commits;
      a locked save's marker unit SURVIVES a concurrent recovery.
  W2  a duplicate recovery over proven-clean state produces NO
      spurious ExchangeError; the journal is disposed exactly once
      in effect (P3 idempotent disposal); final state clean.
  W2F fault injection: with a journal PRESENT, a disposal unlink
      failure must still raise (fail-closed) — P3 idempotence may
      accept proven absence, never swallow a real failure.
  W3  import holds coherence end-to-end: if the importer reports
      ok=True, the final durable files AGREE (proposal present iff
      seed+receipts present). ok=True over disagreeing files is the
      false-success defect.
  P3  sequential idempotence: a second recovery after a completed
      one is an honest no-op ("none"), never an error.
  P5  clean reads stay clean: with no journal present, recovery is
      the fast path ("none") and writes nothing.
  P5D adverse: a corrupt journal fails CLOSED — recovery raises or
      reports an error outcome AND retains the journal bytes as
      evidence; it never silently disposes of an unreadable journal.

Coordination seams (same doctrine as the original audit probe): a
seam only pauses a child at a real code boundary
(exchange._raw_state_files after its real read returns;
exchange.record_receipt on its first call) and changes no logic; the
window it exposes is the code's own. Children are genuine separate
OS processes (CROSS_PROCESS tier). Bounded waits only (AGENTS 31.1).

STATUS: FAILING-FIRST. On current main the W1/W2/W3 checks are
EXPECTED TO FAIL (the defects reproduce); the guard checks (W2F, P3,
P5) are expected to pass and protect against overcorrection when the
C-B repair is later authorized. The C-B product repair itself is NOT
authorized by this file: it requires Keeper review of this package
and a separate Director authorization under the save-path GATE
exception (Director 7040542941).
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

ROOT = None  # repo root, set in parent/smoke mode

PID = "q1cbpid"
SEED = {"label": "q1cb-label", "chain": "chain-q1cb", "keep": "Q1CB-KEEP"}
MAN = {"author_origin": "q1cb:origin", "created": "2026-11-20T00:00:00Z",
       "registry": "core1:00-50,core2:51-99", "requirements": ["req-q1cb"]}


def wait_for(path, timeout=60.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if os.path.isfile(path):
            return True
        time.sleep(0.01)
    return False


def write_result(path, obj):
    with open(path, "w") as f:
        json.dump(obj, f)


def read_json(path):
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ---------------- children (genuine separate OS processes) ----------------

def child_saver(a):
    from form import persist_rest
    prog = persist_rest.load(a.owner, activate=False)
    prog.place("q1cb-marker", "Q1CB Marker Unit", x=3.0, y=3.0)
    write_result(a.ready, {"loaded": True})
    if not wait_for(a.barrier):
        write_result(a.result, {"outcome": "barrier_timeout"})
        return 1
    try:
        persist_rest.save(prog)
        write_result(a.result, {"outcome": "saved"})
    except Exception as e:
        write_result(a.result, {"outcome": "error",
                                "error": f"{type(e).__name__}: {e}"})
    return 0


def child_recover(a):
    from form.dell_matrix import exchange
    orig = exchange._raw_state_files

    def seamed(owner):
        r = orig(owner)
        write_result(a.ready, {"read_done": True})
        if a.barrier and not wait_for(a.barrier):
            raise RuntimeError("barrier timeout in seam")
        return r

    exchange._raw_state_files = seamed
    try:
        outcome = exchange.recover_exchange_import(a.owner)
        write_result(a.result, {"outcome": outcome})
    except Exception as e:
        write_result(a.result, {"outcome": "error",
                                "error": f"{type(e).__name__}: {e}"})
    return 0


def child_recover_unlinkfail(a):
    """P5-D/W2F fault injection: disposal unlink of the journal file
    raises OSError; recovery must fail closed, never swallow it."""
    from form.dell_matrix import exchange
    real_remove = os.remove

    def failing_remove(path, *args, **kwargs):
        if "exchange_import_" in str(path) and str(path).endswith(
                ".journal.json"):
            raise OSError("injected disposal failure (Q1CB W2F)")
        return real_remove(path, *args, **kwargs)

    # _clear_import_journal deletes via os.remove (exchange.py:431);
    # patch the exact primitive the disposal path calls, plus unlink
    # for any sibling path. The seam injects a fault only; it changes
    # no product logic.
    os.remove = failing_remove
    os.unlink = failing_remove
    try:
        outcome = exchange.recover_exchange_import(a.owner)
        write_result(a.result, {"outcome": outcome})
    except Exception as e:
        write_result(a.result, {"outcome": "error",
                                "error": f"{type(e).__name__}: {e}"})
    return 0


def child_load(a):
    from form import persist_rest
    try:
        prog = persist_rest.load(a.owner, activate=False)
        write_result(a.result, {"outcome": "loaded", "owner": prog.owner})
    except Exception as e:
        write_result(a.result, {"outcome": "error",
                                "error": f"{type(e).__name__}: {e}"})
    return 0


def child_import(a):
    from form.open import Program
    from form.dell_matrix import exchange
    orig = exchange.record_receipt
    state = {"signalled": False}

    def seamed(program, pid, receipt, **kw):
        if not state["signalled"]:
            state["signalled"] = True
            write_result(a.ready, {"landed_pid": pid})
            if not wait_for(a.barrier):
                raise RuntimeError("barrier timeout in seam")
        return orig(program, pid, receipt, **kw)

    exchange.record_receipt = seamed
    packet = {
        "version": 1,
        "seed": {"label": "q1cb-w3-label", "chain": "chain-w3cb",
                 "keep": "Q1CB-W3-KEEP"},
        "manifest": {"author_origin": "q1cb:origin",
                     "created": "2026-11-20T00:00:00Z",
                     "registry": "core1:00-50,core2:51-99",
                     "requirements": ["req-w3cb"]},
        "receipts": [
            {"origin": "q1cb:org", "guess": f"g{j}", "test_method": "m",
             "result": "r", "mirror": "mi", "outcome": "o"}
            for j in range(2)],
    }
    prog = Program(owner=a.owner)
    try:
        res = exchange.import_packet(prog, packet)
        write_result(a.result, {"outcome": "returned", "res": res})
    except Exception as e:
        write_result(a.result, {"outcome": "error",
                                "error": f"{type(e).__name__}: {e}"})
    return 0


# ---------------- parent helpers ----------------

def state_dir():
    return os.path.join(ROOT, "form", "state")


def cleanup(owner):
    sd = state_dir()
    errors = []
    pats = [f"program_{owner}.json", f"nursery_{owner}.json",
            f"exchange_import_{owner}.journal.json",
            f"graph_{owner}.json", f"graph_{owner}.journal.json",
            f"confirm_{owner}.journal.json",
            f"checkpoint_{owner}.journal.json",
            f"current_{owner}.json", f"ideas_{owner}"]
    for pat in pats:
        for p in glob.glob(os.path.join(sd, pat)) + \
                glob.glob(os.path.join(sd, f"program_{owner}_cp_*")) + \
                glob.glob(os.path.join(sd, f"gen_{owner}_*")) + \
                glob.glob(os.path.join(sd, f"checkpoint_{owner}_*")):
            try:
                if os.path.isdir(p):
                    shutil.rmtree(p)
                else:
                    os.remove(p)
            except OSError as e:
                errors.append(f"{p}: {e}")
    if errors:
        raise RuntimeError(f"cleanup failed for {owner}: {errors}")


def spawn(mode, owner, coord, tag, barrier=True):
    args = [sys.executable, os.path.abspath(__file__), mode,
            "--owner", owner,
            "--ready", os.path.join(coord, f"{tag}.ready"),
            "--result", os.path.join(coord, f"{tag}.result")]
    if barrier:
        args += ["--barrier", os.path.join(coord, f"{tag}.go")]
    env = dict(os.environ)
    env["PYTHONPATH"] = ROOT + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.Popen(args, cwd=ROOT, env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True)


def finish(proc, coord, tag, timeout=90.0):
    rp = os.path.join(coord, f"{tag}.result")
    ok = wait_for(rp, timeout)
    try:
        out, err = proc.communicate(timeout=15)
    except subprocess.TimeoutExpired:
        proc.kill()
        out, err = proc.communicate()
    if not ok:
        return {"outcome": "no_result", "stderr_tail": (err or "")[-400:]}
    with open(rp) as f:
        r = json.load(f)
    if err and r.get("outcome") in ("error",):
        r["stderr_tail"] = err[-300:]
    return r


def touch(path):
    with open(path, "w") as f:
        f.write("go")


def setup_base(owner):
    from form.open import open_program
    from form import persist_rest
    prog = open_program(owner)
    prog.place("q1cb-base", "Q1CB Base Unit", x=1.0, y=1.0)
    persist_rest.save(prog)


def setup_partial_import(owner):
    """Fabricate a partial import on disk: nursery proposal + program
    seed entry (receipts missing => not complete), journal landed.
    Identical fabrication to the Q1 audit probe, rebased by owner."""
    sd = state_dir()
    ppath = os.path.join(sd, f"program_{owner}.json")
    npath = os.path.join(sd, f"nursery_{owner}.json")
    prog = read_json(ppath) or {}
    seed_entry = dict(SEED)
    seed_entry.update(dict(MAN))
    seed_entry.update({"pid": PID, "receipts_expected": 2,
                       "receipts_hash": "0" * 64})
    prog["exchange_seeds"] = {"version": 1, "kind": "entries",
                              "entries": {"seedq1cb": seed_entry}}
    prog["exchange_receipts"] = {"version": 1, "kind": "entries",
                                 "entries": {}}
    with open(ppath, "w") as f:
        json.dump(prog, f)
    nurs = read_json(npath) or {}
    nurs[PID] = {"label": SEED["label"], "origin": "exchange:q1cb:origin",
                 "detail": "KEEP: Q1CB-KEEP", "status": "pending"}
    with open(npath, "w") as f:
        json.dump(nurs, f)
    journal = {"version": 1, "kind": "exchange_import", "owner": owner,
               "import_id": "q1cbprobe", "phase": "landed",
               "status": "in_progress", "pid": PID,
               "label": SEED["label"], "origin": "exchange:q1cb:origin",
               "detail_sha256": hashlib.sha256(b"KEEP: Q1CB-KEEP").hexdigest(),
               "seed": SEED, "manifest": MAN,
               "receipts_expected": 2, "receipts_hash": "0" * 64}
    with open(os.path.join(sd, f"exchange_import_{owner}.journal.json"),
              "w") as f:
        json.dump(journal, f)


# ---------------- cases (each returns (name, ok, detail)) ----------------

def case_w1(coord):
    owner = "Q1CBW1"
    cleanup(owner)
    setup_base(owner)
    saver = spawn("child-saver", owner, coord, "w1saver")
    assert wait_for(os.path.join(coord, "w1saver.ready")), "saver no ready"
    setup_partial_import(owner)
    rec = spawn("child-recover", owner, coord, "w1rec")
    assert wait_for(os.path.join(coord, "w1rec.ready")), "recover no ready"
    touch(os.path.join(coord, "w1saver.go"))
    saver_res = finish(saver, coord, "w1saver")
    mid = read_json(os.path.join(state_dir(), f"program_{owner}.json"))
    marker_mid = "q1cb-marker" in json.dumps(mid)
    touch(os.path.join(coord, "w1rec.go"))
    rec_res = finish(rec, coord, "w1rec")
    final = read_json(os.path.join(state_dir(), f"program_{owner}.json"))
    marker_final = "q1cb-marker" in json.dumps(final)
    cleanup(owner)
    ok = marker_mid and marker_final
    return ("CB-W1 locked save's marker survives concurrent recovery "
            "(no silent loss)", ok,
            f"saver={saver_res.get('outcome')} recover={rec_res.get('outcome')} "
            f"marker_after_save={marker_mid} marker_after_recovery={marker_final}")


def case_w2(coord):
    owner = "Q1CBW2"
    cleanup(owner)
    setup_base(owner)
    setup_partial_import(owner)
    r1 = spawn("child-recover", owner, coord, "w2r1")
    r2 = spawn("child-recover", owner, coord, "w2r2")
    assert wait_for(os.path.join(coord, "w2r1.ready")), "r1 no ready"
    assert wait_for(os.path.join(coord, "w2r2.ready")), "r2 no ready"
    touch(os.path.join(coord, "w2r1.go"))
    touch(os.path.join(coord, "w2r2.go"))
    res1 = finish(r1, coord, "w2r1")
    res2 = finish(r2, coord, "w2r2")
    sd = state_dir()
    final_p = read_json(os.path.join(sd, f"program_{owner}.json")) or {}
    final_n = read_json(os.path.join(sd, f"nursery_{owner}.json")) or {}
    journal_gone = not os.path.isfile(
        os.path.join(sd, f"exchange_import_{owner}.journal.json"))
    clean = PID not in final_n and PID not in json.dumps(
        final_p.get("exchange_seeds"))
    errors = [r for r in (res1, res2) if r.get("outcome") == "error"]
    cleanup(owner)
    ok = clean and journal_gone and not errors
    return ("CB-W2 duplicate recovery over clean state: no spurious "
            "error, journal disposed, state clean (P3)", ok,
            f"r1={res1.get('outcome')} r2={res2.get('outcome')} "
            f"errors={[e.get('error', '')[:80] for e in errors]} "
            f"clean={clean} journal_disposed={journal_gone}")


def case_w2f(coord):
    owner = "Q1CBW2F"
    cleanup(owner)
    setup_base(owner)
    setup_partial_import(owner)
    proc = spawn("child-recover-unlinkfail", owner, coord, "w2f",
                 barrier=False)
    res = finish(proc, coord, "w2f")
    journal_retained = os.path.isfile(os.path.join(
        state_dir(), f"exchange_import_{owner}.journal.json"))
    cleanup(owner)
    ok = res.get("outcome") == "error" and journal_retained
    return ("CB-W2F disposal unlink failure with journal present "
            "fails closed (error raised, journal retained)", ok,
            f"outcome={res.get('outcome')} "
            f"error={res.get('error', '')[:100]} "
            f"journal_retained={journal_retained}")


def case_w3(coord):
    owner = "Q1CBW3"
    cleanup(owner)
    imp = spawn("child-import", owner, coord, "w3imp")
    ready_p = os.path.join(coord, "w3imp.ready")
    assert wait_for(ready_p), "importer never landed"
    with open(ready_p) as f:
        pid = json.load(f)["landed_pid"]
    loader = spawn("child-load", owner, coord, "w3load", barrier=False)
    load_res = finish(loader, coord, "w3load")
    touch(os.path.join(coord, "w3imp.go"))
    imp_res = finish(imp, coord, "w3imp")
    sd = state_dir()
    final_p = read_json(os.path.join(sd, f"program_{owner}.json")) or {}
    final_n = read_json(os.path.join(sd, f"nursery_{owner}.json")) or {}
    prop_final = pid in final_n
    seed_final = pid in json.dumps(final_p.get("exchange_seeds"))
    rcpt_final = pid in json.dumps(final_p.get("exchange_receipts"))
    reported_ok = (imp_res.get("res") or {}).get("ok") is True
    coherent = prop_final == (seed_final and rcpt_final)
    cleanup(owner)
    ok = coherent or not reported_ok
    return ("CB-W3 import ok=True implies final files agree "
            "(proposal iff seed+receipts); else honest failure", ok,
            f"loader={load_res.get('outcome')} importer_ok={reported_ok} "
            f"proposal={prop_final} seed={seed_final} receipts={rcpt_final} "
            f"coherent={coherent}")


def case_p3(coord):
    owner = "Q1CBP3"
    cleanup(owner)
    setup_base(owner)
    setup_partial_import(owner)
    from form.dell_matrix import exchange
    first = exchange.recover_exchange_import(owner)
    try:
        second = exchange.recover_exchange_import(owner)
        err = ""
    except Exception as e:
        second, err = "error", f"{type(e).__name__}: {e}"
    cleanup(owner)
    ok = first == "removed" and second == "none"
    return ("CB-P3 sequential idempotence: second recovery is an "
            "honest no-op ('none')", ok,
            f"first={first} second={second} {err[:80]}")


def case_p5(coord):
    owner = "Q1CBP5"
    cleanup(owner)
    setup_base(owner)
    sd = state_dir()
    before = {}
    for p in sorted(glob.glob(os.path.join(sd, f"*{owner}*"))):
        with open(p, "rb") as f:
            before[p] = hashlib.sha256(f.read()).hexdigest()
    from form.dell_matrix import exchange
    outcome = exchange.recover_exchange_import(owner)
    after = {}
    for p in sorted(glob.glob(os.path.join(sd, f"*{owner}*"))):
        with open(p, "rb") as f:
            after[p] = hashlib.sha256(f.read()).hexdigest()
    cleanup(owner)
    ok = outcome == "none" and before == after
    return ("CB-P5 clean read stays clean: no journal -> 'none', "
            "zero writes", ok,
            f"outcome={outcome} files_unchanged={before == after}")


def case_p5d(coord):
    owner = "Q1CBP5D"
    cleanup(owner)
    setup_base(owner)
    jpath = os.path.join(state_dir(),
                         f"exchange_import_{owner}.journal.json")
    with open(jpath, "w") as f:
        f.write("{ this is not a journal !!!")
    from form.dell_matrix import exchange
    try:
        outcome = exchange.recover_exchange_import(owner)
        err = ""
    except Exception as e:
        outcome, err = "error", f"{type(e).__name__}: {e}"
    retained = os.path.isfile(jpath)
    cleanup(owner)
    ok = outcome == "error" and retained
    return ("CB-P5D corrupt journal fails closed: error outcome and "
            "journal bytes retained as evidence", ok,
            f"outcome={outcome} {err[:80]} journal_retained={retained}")


CASES = [case_w1, case_w2, case_w2f, case_w3, case_p3, case_p5, case_p5d]


def smoke() -> bool:
    global ROOT
    ROOT = os.path.abspath(os.path.join(os.path.dirname(
        os.path.abspath(__file__)), ".."))
    print("=== Q1 C-B PREP — EXCHANGE RECOVERY TRANSACTION (FAILING-FIRST) ===")
    coord = tempfile.mkdtemp(prefix="q1cb_coord_")
    results = []
    for fn in CASES:
        try:
            name, ok, detail = fn(coord)
        except Exception as e:
            name, ok, detail = fn.__name__, False, \
                f"case error: {type(e).__name__}: {e}"
        results.append(ok)
        print(f"[{'PASS' if ok else 'FAIL'}] {name} :: {detail}")
    total = len(results)
    passed = sum(results)
    print(f"Q1 CB PREP: {passed}/{total} checks passed")
    return all(results)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="mode")
    for m in ("child-saver", "child-recover", "child-recover-unlinkfail",
              "child-load", "child-import"):
        p = sub.add_parser(m)
        p.add_argument("--owner", required=True)
        p.add_argument("--ready", required=True)
        p.add_argument("--result", required=True)
        p.add_argument("--barrier", default="")
    a = ap.parse_args()
    if a.mode is None:
        return 0 if smoke() else 1
    fn = {"child-saver": child_saver, "child-recover": child_recover,
          "child-recover-unlinkfail": child_recover_unlinkfail,
          "child-load": child_load, "child-import": child_import}[a.mode]
    return fn(a)


if __name__ == "__main__":
    sys.exit(main())
