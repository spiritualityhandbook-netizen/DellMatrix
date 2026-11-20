#!/usr/bin/env python3
"""R5-D refusal depth — per-method assertions, actual-save-format
byte parity, thread/process concurrency isolation.

Answers Director 7032773180 (01:00 disposition on PR #498):
(1) explicit per-method before/after state + filesystem +
    external-effect assertions at refusal, incl. preservation of
    legitimate no-note early returns;
(2) byte-equivalence shown against the ACTUAL persistence
    serializer, not the assumed canonical formula;
(3) concurrency guarantees isolated by thread vs process.

ACTUAL SAVE FORMAT (source-verified this run):
save path = persist_rest.save -> _write_program_file ->
atomic_write.atomic_write_json, whose serializer is
json.dumps(payload, indent=2) — ensure_ascii defaults to True,
NO sort_keys — over persist.serialize(program), whose "history"
value is list(history)[-24:] (persist.py:378). Section C proves
each of those facts empirically and measures where the R5-C
admission formula (canonical bytes of the FULL logical history)
diverges from the bytes the save format actually writes.

PER-METHOD PRE-NOTE MUTATIONS (source-verified, open.py):
radial_drift  apply_radial_soft_forget(lattice, keys) BEFORE note
internet_on   creates InternetGate + turn_on() BEFORE note
internet_off  turn_off() BEFORE note; NO-GATE EARLY RETURN
              {"ok": True, "on": False} with no note — the only
              legitimate no-note early return among S7
sandbox_on    note BEFORE apply_on (note-first caller)
sandbox_off   note BEFORE apply_off (note-first caller)
enhance_on    enhance.turn_on() BEFORE note
enhance_off   enhance.turn_off() BEFORE note
A lawful preflight sits at each caller entry point, before the
first mutation OR the note, whichever comes first; on refusal
NOTHING may change: full history digest, serialized state,
per-method subsystem digest, state-dir file set/sha256, and
thread count all identical before/after.

STATUS: FAILING-FIRST on current main (7027419): no typed
refusal exists, so the refusal battery fails; the preservation
check (internet_off no-gate early return), the serializer-fact
checks, and the atomic-write integrity check PASS today and
must keep passing. Labels: thread leg = INTEGRATION
(in-process); multi-process leg = CROSS_PROCESS (separate OS
processes via subprocess). NO product code changed.
Hygiene: uuid owner, exact-pattern cleanup; cleanup errors fail.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import uuid
from pathlib import Path

REPO = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, REPO)

RESULTS = []
_CLEANUP_ERRORS = []
RUN = uuid.uuid4().hex[:8]
OWNER = f"R5RD{RUN}"
CAP = 10_000
CAP_BYTES = 2_097_152
S7 = ["radial_drift", "internet_on", "internet_off",
      "sandbox_on", "sandbox_off", "enhance_on", "enhance_off"]
HIST_CANARY = f"histcanary-{RUN}"


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def _canonical(entries):
    return len(json.dumps(list(entries), indent=2,
                          ensure_ascii=True).encode("utf-8"))


def _digest(obj):
    blob = json.dumps(obj, sort_keys=True, default=repr,
                      ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _refusal_seen(fn):
    try:
        ret = fn()
    except Exception as exc:  # noqa: BLE001
        name, msg = type(exc).__name__, str(exc)
        if any(k in name for k in ("Refus", "History", "Cap",
                                   "Budget")) or "refus" in msg.lower() \
                or "LEGACY_OVER_BUDGET" in msg:
            return True, exc
        return False, exc
    if isinstance(ret, dict) and ret.get("ok") is False:
        return True, ret
    return False, ret


def _dir_snapshot():
    from form.persist import _STATE_DIR
    snap = {}
    for pth in sorted(Path(_STATE_DIR).rglob("*")):
        if pth.is_file():
            try:
                snap[str(pth)] = hashlib.sha256(
                    pth.read_bytes()).hexdigest()
            except OSError:
                snap[str(pth)] = "UNREADABLE"
    return snap


def _ser_bytes(p):
    from form.persist import serialize
    return json.dumps(serialize(p), indent=2, ensure_ascii=True,
                      sort_keys=True).encode("utf-8")


def _hist_digest(p):
    return _digest(list(p.history))


def _subsystem_digest(p, fn_name):
    """Digest of exactly the subsystem fn mutates BEFORE its note
    (or, for note-first callers, the subsystem it mutates after)."""
    if fn_name == "radial_drift":
        cells = sorted(
            (str(k), getattr(c, "label", ""), repr(getattr(c, "content", None)),
             tuple(getattr(c, "members", []) or []))
            for k, c in p.lattice.cells.items())
        ledger = {k: (v.get("hits"), v.get("has_payload"),
                      repr(v.get("payload")), v.get("meta"))
                  for k, v in p.keys.keys.items()}
        return _digest({"cells": cells, "ledger": ledger})
    if fn_name in ("internet_on", "internet_off"):
        gate = p.internet
        return _digest({"gate_is_none": gate is None,
                        "status": gate.status() if gate else None})
    if fn_name in ("sandbox_on", "sandbox_off"):
        plane = p.cube.session.plane
        boxed = sorted(uid for uid, u in plane.units.items()
                       if getattr(u, "sandboxed", False))
        return _digest({"on": p.sandbox.on, "level": p.sandbox.level,
                        "box": p.sandbox.auto_box_id, "boxed": boxed,
                        "units": len(plane.units)})
    if fn_name in ("enhance_on", "enhance_off"):
        return _digest(p.enhance.status())
    raise AssertionError(fn_name)


def _gate_on(p):
    from form.dell_matrix.internet_gate import InternetGate
    if p.internet is None:
        p.internet = InternetGate()
    try:
        p.internet.turn_on()
    except Exception:  # noqa: BLE001
        pass


def _prep(p, fn_name):
    """Per-method pre-state for a refusal leg."""
    if fn_name == "radial_drift":
        # Non-vacuous subsystem probe: a far-shell cell (shell 30
        # >= outer_shell 6) with payload — soft-forget MUST touch
        # the cell content and the KeyLedger if the call runs.
        p.lattice.put(30, 30, 1, label="seedcell",
                      content="seedpayload")
    elif fn_name == "internet_on":
        p.internet = None  # gate creation is itself an effect
    elif fn_name == "internet_off":
        _gate_on(p)


def _battery(p, fn_name, scenario):
    fn = getattr(p, fn_name)
    _prep(p, fn_name)
    before = (_hist_digest(p), _ser_bytes(p),
              _subsystem_digest(p, fn_name), _dir_snapshot(),
              threading.active_count())
    refused, how = _refusal_seen(fn)
    after = (_hist_digest(p), _ser_bytes(p),
             _subsystem_digest(p, fn_name), _dir_snapshot(),
             threading.active_count())
    tag = f"pm_{fn_name}_{scenario}"
    check(f"{tag}_typed_refusal", refused, f"refused={refused}")
    check(f"{tag}_history_unchanged", after[0] == before[0])
    check(f"{tag}_state_unchanged", after[1] == before[1])
    check(f"{tag}_subsystem_unchanged", after[2] == before[2])
    check(f"{tag}_files_unchanged", after[3] == before[3])
    check(f"{tag}_threads_unchanged", after[4] == before[4],
          f"threads {before[4]}->{after[4]}")


def _filler_for_bytes(entry, target):
    base = _canonical(["", entry])
    n = target - base
    assert n >= 0, (target, base)
    filler = "f" * n
    assert _canonical([filler, entry]) == target
    return filler


ENTRY = {"radial_drift": "16[Decay] :: drift_6",
         "internet_on": "25[Pulse] :: internet_on",
         "internet_off": "32[Pause] :: internet_off",
         "sandbox_on": "23[Lock] :: sandbox_on",
         "sandbox_off": "24[Unlock] :: sandbox_off",
         "enhance_on": "25[Pulse] :: enhance_on",
         "enhance_off": "32[Pause] :: enhance_off"}


def _mp_child(owner, shared_path, result_path):
    """CROSS_PROCESS child: separate OS process, same owner."""
    from form.open import open_program
    p = open_program(owner)
    p.history = [f"mp-{i:05d}" for i in range(CAP)]
    out = {}
    for name in ("radial_drift", "sandbox_on"):
        refused, _ = _refusal_seen(getattr(p, name))
        out[name] = {"refused": refused, "hist_len": len(p.history)}
    p.save(path=shared_path)
    Path(result_path).write_text(json.dumps(out), encoding="utf-8")
    return 0


def main():
    from form.open import open_program

    p = open_program(OWNER)
    cap_hist = [HIST_CANARY] + [f"cap-{i:05d}" for i in range(CAP - 1)]

    # ── A. PER-METHOD REFUSAL BATTERY (entry cap + byte cap+1) ──
    for fn_name in S7:
        p.history = list(cap_hist)
        _battery(p, fn_name, "entrycap")
    for fn_name in S7:
        p.history = [_filler_for_bytes(ENTRY[fn_name], CAP_BYTES + 1)]
        _battery(p, fn_name, "bytecap_plus1")

    # ── B. LEGITIMATE NO-NOTE EARLY RETURN PRESERVED ──
    # internet_off with NO gate: lawful early return, no note, no
    # gate creation, even at entry cap. PASS today; the R5-D build
    # must NOT convert this into a refusal or an error.
    p.internet = None
    p.history = list(cap_hist)
    before = (_hist_digest(p), _subsystem_digest(p, "internet_off"))
    try:
        ret = p.internet_off()
        err = ""
    except Exception as exc:  # noqa: BLE001
        ret, err = None, repr(exc)
    check("early_return_internet_off_no_gate_preserved",
          ret == {"ok": True, "on": False} and not err
          and _hist_digest(p) == before[0]
          and _subsystem_digest(p, "internet_off") == before[1]
          and p.internet is None,
          f"ret={ret!r:.60} err={err}")

    # ── C. ACTUAL SAVE FORMAT vs ADMISSION FORMULA ──
    from form.persist import serialize
    # C1: atomic_write_json's dumps(payload, indent=2) — the
    # ensure_ascii default makes it byte-identical to the
    # canonical parameterization on this axis.
    payload = {"history": ["café ☕ entry", "plain"], "n": 1}
    check("ser_ensure_ascii_axis_parity",
          json.dumps(payload, indent=2).encode("utf-8")
          == json.dumps(payload, indent=2,
                        ensure_ascii=True).encode("utf-8"),
          "atomic_write_json omits ensure_ascii; default True")
    # C2: a real save file IS json.dumps(serialize(p), indent=2).
    p.history = ["alpha", "café ☕", "beta", "gamma"]
    tmpdir = Path(tempfile.mkdtemp(prefix=f"r5rd_{RUN}_"))
    target = str(tmpdir / "saveprobe.json")
    p.save(path=target)
    file_bytes = Path(target).read_bytes()
    expect = json.dumps(serialize(p), indent=2).encode("utf-8")
    check("ser_actual_file_is_dumps_serialize_indent2",
          file_bytes == expect,
          f"file={len(file_bytes)}B expect={len(expect)}B "
          "(no sort_keys; insertion order)")
    # C3: the history SEGMENT inside the file is NOT the canonical
    # top-level dumps of the history list: nesting adds exactly
    # 2 bytes per interior line (n elements + closing bracket).
    hist = list(serialize(p)["history"])
    seg_start = file_bytes.index(b'"history": ') + len(b'"history": ')
    # The value's closing bracket sits on its own line at depth-1
    # indent (2 spaces). A naive search for "]" stops inside the
    # "10[Keep] :: ..." entry string — instrument fix, run 2.
    seg_end = file_bytes.index(b"\n  ]", seg_start) + len(b"\n  ]")
    segment = file_bytes[seg_start:seg_end]
    canon = json.dumps(hist, indent=2,
                       ensure_ascii=True).encode("utf-8")
    delta = len(segment) - len(canon)
    check("ser_file_segment_differs_by_nesting_indent",
          segment != canon and delta == 2 * (len(hist) + 1),
          f"segment={len(segment)}B canonical={len(canon)}B "
          f"delta={delta}B predicted={2 * (len(hist) + 1)}B")
    # C4: serialize() persists only history[-24:] — the admission
    # formula (full logical history) and the persisted bytes
    # DIVERGE in both directions.
    big = [f"e{i:02d}-" + "x" * 79_995 for i in range(30)]
    p.history = list(big)
    ser_hist = serialize(p)["history"]
    full_bytes = _canonical(big)
    slice_bytes = _canonical(ser_hist)
    check("ser_persisted_slice_diverges_from_admission_formula",
          ser_hist == big[-24:] and full_bytes > CAP_BYTES
          and slice_bytes <= CAP_BYTES,
          f"full={full_bytes}B (formula: REFUSE) vs persisted "
          f"slice={slice_bytes}B (file: under cap) — the cap binds "
          "the logical history, never the written bytes")
    shutil.rmtree(tmpdir, ignore_errors=True)

    # ── D1. TOCTOU — THREADS (INTEGRATION, in-process) ──
    _gate_on(p)
    p.history = list(cap_hist)
    before = (_hist_digest(p), _ser_bytes(p))
    results_t = []

    def worker():
        for name in S7:
            r, _ = _refusal_seen(getattr(p, name))
            results_t.append(r)
    threads = [threading.Thread(target=worker) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=120)
    check("toctou_threads_all_refused_state_stable",
          len(results_t) == 28 and all(results_t)
          and (_hist_digest(p), _ser_bytes(p)) == before,
          f"calls={len(results_t)} refused={sum(results_t)}")

    # ── D2. CONCURRENCY — PROCESSES (CROSS_PROCESS) ──
    mpdir = Path(tempfile.mkdtemp(prefix=f"r5rdmp_{RUN}_"))
    shared = str(mpdir / "shared.json")
    procs, result_files = [], []
    for i in range(3):
        rf = str(mpdir / f"child{i}.json")
        result_files.append(rf)
        procs.append(subprocess.Popen(
            [sys.executable, str(Path(__file__).resolve()),
             "--mp-child", OWNER, shared, rf],
            cwd=REPO, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL))
    rcs = [pr.wait(timeout=600) for pr in procs]
    reports = []
    for rf in result_files:
        try:
            reports.append(json.loads(Path(rf).read_text("utf-8")))
        except Exception:  # noqa: BLE001
            reports.append(None)
    check("mp_children_executed_cross_process",
          rcs == [0, 0, 0] and all(reports),
          f"rcs={rcs} reports_ok={sum(1 for r in reports if r)}")
    check("mp_all_refused_at_cap",
          all(r and all(v["refused"] for v in r.values())
              for r in reports),
          f"reports={reports}")
    try:
        shared_data = json.loads(Path(shared).read_text("utf-8"))
        shared_ok = isinstance(shared_data, dict) \
            and isinstance(shared_data.get("history"), list)
        shared_len = len(shared_data.get("history", []))
    except Exception:  # noqa: BLE001
        shared_ok, shared_len = False, -1
    check("mp_shared_file_valid_after_concurrent_saves",
          shared_ok, f"history_len_in_file={shared_len} "
          "(atomic_write whole-generation guarantee)")
    print("OBSERVED  cross-process admission: each process holds "
          "independent in-memory state; no admission coordination "
          "exists across processes — the only cross-process fence "
          "is owner_state_lock around canonical save, which does "
          "not re-check admission. Per-child outcomes above.")
    shutil.rmtree(mpdir, ignore_errors=True)

    _cleanup()
    check("cleanup_clean", not _CLEANUP_ERRORS,
          "; ".join(_CLEANUP_ERRORS))
    ok_n = sum(1 for _, ok in RESULTS if ok)
    print(f"R5RD {ok_n}/{len(RESULTS)} PASS")
    return 0 if ok_n == len(RESULTS) else 1


def _cleanup():
    from form.persist import _STATE_DIR, _safe_owner
    from form.dell_matrix.nursery import owner_nursery_path
    state = Path(_STATE_DIR)
    safe = _safe_owner(OWNER)
    cands = [state / f"program_{safe}.json",
             Path(owner_nursery_path(OWNER))]
    cands += list(state.glob(f"*{safe}*"))
    for c in dict.fromkeys(cands):
        try:
            if c.is_file():
                c.unlink()
        except OSError as exc:
            _CLEANUP_ERRORS.append(f"{c}: {exc}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--mp-child":
        sys.exit(_mp_child(sys.argv[2], sys.argv[3], sys.argv[4]))
    sys.exit(main())
