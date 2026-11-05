#!/usr/bin/env python3
"""Q1 audit cross-process probes (G-03) — AUDIT ONLY, no product change.

Run from the DellMatrix repo root (a disposable clone):
    python3 <this file> parent --workdir <tmpcoorddir>

Modes (children are genuine separate OS processes):
  child-saver    load owner, place marker unit, signal, wait, locked save
  child-recover  recover_exchange_import with a coordination seam on
                 exchange._raw_state_files: after the real read returns,
                 signal + wait for a barrier, then return the (now
                 potentially stale) snapshot. The seam only pauses at a
                 real code boundary; it changes no logic and holds no
                 lock — the window it exposes is the code's own.
  child-import   import_packet with a coordination seam on
                 exchange.record_receipt (first call signals + waits):
                 journal is written and the proposal has landed in the
                 nursery file at that point; the final save is pending.
  child-load     plain persist_rest.load (runs all load recoveries)

Parent orchestrates W1/W2/W3 with unique owners in the clone's own
form/state (per-owner files), cleans up only its owners' canonical
files, and prints a JSON verdict per window. Bounded waits only
(AGENTS 31.1)."""
import argparse, glob, hashlib, json, os, shutil, subprocess, sys, time

ROOT = None  # set in parent main (repo root = cwd)


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


# ---------------- children ----------------

def child_saver(a):
    from form import persist_rest
    prog = persist_rest.load(a.owner, activate=False)
    prog.place("q1-marker", "Q1 Marker Unit", x=3.0, y=3.0)
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
        if not wait_for(a.barrier):
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


def child_load(a):
    from form import persist_rest
    try:
        prog = persist_rest.load(a.owner, activate=False)
        write_result(a.result, {"outcome": "loaded",
                                "owner": prog.owner})
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
        "seed": {"label": "q1-w3-label", "chain": "chain-w3",
                 "keep": "Q1-W3-KEEP"},
        "manifest": {"author_origin": "q1:origin",
                     "created": "2026-11-05T00:00:00Z",
                     "registry": "core1:00-50,core2:51-99",
                     "requirements": ["req-w3"]},
        "receipts": [
            {"origin": "q1:org", "guess": f"g{j}", "test_method": "m",
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
    lock = os.path.join(sd, ".locks", f"program_{owner}.json.lock")
    # lock file is never removed by the lock module; leave it (its
    # documented residue class) — only report.
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


def read_json(path):
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


PID = "q1partialpid"
SEED = {"label": "q1-label", "chain": "chain-q1", "keep": "Q1-KEEP"}
MAN = {"author_origin": "q1:origin", "created": "2026-11-05T00:00:00Z",
       "registry": "core1:00-50,core2:51-99", "requirements": ["req-q1"]}


def setup_base(owner):
    from form.open import open_program
    from form import persist_rest
    prog = open_program(owner)
    prog.place("q1-base", "Q1 Base Unit", x=1.0, y=1.0)
    persist_rest.save(prog)


def setup_partial_import(owner):
    """Fabricate a partial import on disk: nursery proposal + program
    seed entry (receipts missing => not complete), journal landed."""
    sd = state_dir()
    ppath = os.path.join(sd, f"program_{owner}.json")
    npath = os.path.join(sd, f"nursery_{owner}.json")
    prog = read_json(ppath) or {}
    seed_entry = dict(SEED)
    seed_entry.update(dict(MAN))
    seed_entry.update({"pid": PID, "receipts_expected": 2,
                       "receipts_hash": "0" * 64})
    prog["exchange_seeds"] = {"version": 1, "kind": "entries",
                              "entries": {"seedq1": seed_entry}}
    prog["exchange_receipts"] = {"version": 1, "kind": "entries",
                                 "entries": {}}
    with open(ppath, "w") as f:
        json.dump(prog, f)
    nurs = read_json(npath) or {}
    nurs[PID] = {"label": SEED["label"], "origin": "exchange:q1:origin",
                 "detail": "KEEP: Q1-KEEP", "status": "pending"}
    with open(npath, "w") as f:
        json.dump(nurs, f)
    journal = {"version": 1, "kind": "exchange_import", "owner": owner,
               "import_id": "q1probe", "phase": "landed",
               "status": "in_progress", "pid": PID,
               "label": SEED["label"], "origin": "exchange:q1:origin",
               "detail_sha256": hashlib.sha256(b"KEEP: Q1-KEEP").hexdigest(),
               "seed": SEED, "manifest": MAN,
               "receipts_expected": 2, "receipts_hash": "0" * 64}
    with open(os.path.join(sd, f"exchange_import_{owner}.journal.json"),
              "w") as f:
        json.dump(journal, f)


def probe_w1(coord):
    owner = "Q1W1Probe"
    cleanup(owner)
    setup_base(owner)
    saver = spawn("child-saver", owner, coord, "w1saver")
    assert wait_for(os.path.join(coord, "w1saver.ready")), "saver no ready"
    setup_partial_import(owner)
    rec = spawn("child-recover", owner, coord, "w1rec")
    assert wait_for(os.path.join(coord, "w1rec.ready")), "recover no ready"
    # Recovery has read its snapshot (no marker, partial import present)
    # and is paused before any write. Now the locked saver commits.
    touch(os.path.join(coord, "w1saver.go"))
    saver_res = finish(saver, coord, "w1saver")
    mid = read_json(os.path.join(state_dir(), f"program_{owner}.json"))
    marker_mid = "q1-marker" in json.dumps(mid)
    # Release recovery: it writes its stale snapshot back.
    touch(os.path.join(coord, "w1rec.go"))
    rec_res = finish(rec, coord, "w1rec")
    final = read_json(os.path.join(state_dir(), f"program_{owner}.json"))
    marker_final = "q1-marker" in json.dumps(final)
    seeds_final = "exchange_seeds" in json.dumps(final) and PID in json.dumps(final.get("exchange_seeds"))
    verdict = {
        "window": "W1 load-recovery vs canonical save",
        "saver": saver_res, "recover": rec_res,
        "marker_present_after_locked_save": marker_mid,
        "marker_present_after_recovery_writeback": marker_final,
        "partial_import_removed": not seeds_final,
        "finding": ("CONFIRMED: recovery writeback erased the locked "
                    "save's marker unit" if marker_mid and not marker_final
                    else "NOT REPRODUCED in this interleaving"),
    }
    cleanup(owner)
    return verdict


def probe_w2(coord):
    owner = "Q1W2Probe"
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
    verdict = {
        "window": "W2 load vs load (concurrent recovery)",
        "recover1": res1, "recover2": res2,
        "final_state_clean": clean, "journal_disposed": journal_gone,
        "finding": ("Both recoveries reported: see outcomes — an error "
                    "outcome from a duplicate recovery over cleanly "
                    "removed state CONFIRMS a spurious-failure window; "
                    "two 'removed' outcomes with clean state REFUTE it "
                    "for this case"),
    }
    cleanup(owner)
    return verdict


def probe_w3(coord):
    owner = "Q1W3Probe"
    cleanup(owner)
    imp = spawn("child-import", owner, coord, "w3imp")
    ready_p = os.path.join(coord, "w3imp.ready")
    assert wait_for(ready_p), "importer never landed"
    with open(ready_p) as f:
        pid = json.load(f)["landed_pid"]
    # Import is mid-flight: journal landed, nursery proposal durable,
    # final program save pending. A second process loads now.
    loader = spawn("child-load", owner, coord, "w3load", barrier=False)
    load_res = finish(loader, coord, "w3load")
    sd = state_dir()
    mid_n = read_json(os.path.join(sd, f"nursery_{owner}.json")) or {}
    mid_journal = os.path.isfile(
        os.path.join(sd, f"exchange_import_{owner}.journal.json"))
    # Release the importer to finish.
    touch(os.path.join(coord, "w3imp.go"))
    imp_res = finish(imp, coord, "w3imp")
    final_p = read_json(os.path.join(sd, f"program_{owner}.json")) or {}
    final_n = read_json(os.path.join(sd, f"nursery_{owner}.json")) or {}
    pj = json.dumps(final_p)
    verdict = {
        "window": "W3 import vs load-recovery (resurrection)",
        "pid": pid, "loader": load_res, "importer": imp_res,
        "after_load_proposal_in_nursery_file": pid in mid_n,
        "after_load_journal_present": mid_journal,
        "final_proposal_in_nursery_file": pid in final_n,
        "final_seed_in_program_file": pid in json.dumps(
            final_p.get("exchange_seeds")),
        "final_receipts_in_program_file": pid in json.dumps(
            final_p.get("exchange_receipts")),
        "finding": ("Resurrection/incoherence is present iff the "
                    "importer reported success while the final files "
                    "disagree (seed/receipts without proposal, or "
                    "proposal restored after recovery removal)"),
    }
    cleanup(owner)
    return verdict


def parent(a):
    global ROOT
    ROOT = os.getcwd()
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    coord = a.workdir
    os.makedirs(coord, exist_ok=True)
    verdicts = []
    for name, fn in (("W1", probe_w1), ("W2", probe_w2), ("W3", probe_w3)):
        try:
            v = fn(coord)
        except Exception as e:
            v = {"window": name, "probe_error": f"{type(e).__name__}: {e}"}
        verdicts.append(v)
        print(json.dumps(v, indent=1), flush=True)
    write_result(os.path.join(coord, "q1_probe_verdicts.json"), verdicts)
    return 0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="mode", required=True)
    for m in ("child-saver", "child-recover", "child-load", "child-import"):
        p = sub.add_parser(m)
        p.add_argument("--owner", required=True)
        p.add_argument("--ready", required=True)
        p.add_argument("--result", required=True)
        p.add_argument("--barrier", default="")
    p = sub.add_parser("parent")
    p.add_argument("--workdir", required=True)
    a = ap.parse_args()
    fn = {"child-saver": child_saver, "child-recover": child_recover,
          "child-load": child_load, "child-import": child_import,
          "parent": parent}[a.mode]
    return fn(a)


if __name__ == "__main__":
    sys.exit(main())
