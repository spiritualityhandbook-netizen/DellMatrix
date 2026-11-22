#!/usr/bin/env python3
"""R5-D S7 admission — the registered proof suite for the bounded
build authorized by Director ruling 7079092723 (PR #508).

Scope proven here (and ONLY this scope): the seven existing Program
methods radial_drift, internet_on/off, sandbox_on/off,
enhance_on/off enforce the adopted R5-C budget (10,000 entries AND
2,097,152 canonical bytes of the prospective SANITIZED logical
history, json.dumps(..., indent=2, ensure_ascii=True) UTF-8) as a
typed pre-mutation refusal, under ONE shared per-Program reentrant
admission RLock that Program.note also funnels through, plus the
locked history-snapshot reader the save serializer uses. Leg 15
additionally pins deepcopy safety: the RLock is excluded from
Program copy state (__getstate__) so simulate_board's deepcopy
isolation works and every copy carries its own fresh lock.

Companion receipts (kept outside form/ so the canonical regression
never has to carry their by-design deferred REDs):
hidden_files/r5d_s7_2026-11-22/ — RED_R5RD/RED_R5SS at base
f60d19f (36/94, 15/40) and GREEN runs on this build (R5RD 94/94;
R5SS 30/40 with the deferred set enumerated in the source-to-test
map beside them).

DEFERRED, labeled, NOT asserted here (separate save/load phase;
Director 7079092723): T1 note() [:120], T2 note() history_max cut,
T3 serializer [-24:], T4 restore cuts — so no end-to-end lossless
retention, no durability across save/reload, no note-door (funnel)
admission, and no cross-process admission are claimed. Legacy
controls below prove the deferred cuts are UNCHANGED.

Labels: thread legs are INTEGRATION (in-process). The lock-order
leg uses the real owner_state_lock + admission RLock pair.
Hygiene: uuid owners, exact-pattern cleanup; cleanup errors fail.
"""
from __future__ import annotations

import hashlib
import json
import sys
import threading
import time
import uuid
from pathlib import Path

REPO = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, REPO)

RESULTS = []
_CLEANUP_ERRORS = []
RUN = uuid.uuid4().hex[:8]
OWNER = f"R5S7{RUN}"
CAP = 10_000
CAP_BYTES = 2_097_152
S7 = ["radial_drift", "internet_on", "internet_off",
      "sandbox_on", "sandbox_off", "enhance_on", "enhance_off"]
ENTRY = {"radial_drift": "16[Decay] :: drift_6",
         "internet_on": "25[Pulse] :: internet_on",
         "internet_off": "32[Pause] :: internet_off",
         "sandbox_on": "23[Lock] :: sandbox_on",
         "sandbox_off": "24[Unlock] :: sandbox_off",
         "enhance_on": "25[Pulse] :: enhance_on",
         "enhance_off": "32[Pause] :: enhance_off"}
SECRET = f"CANARY{RUN}SECRET"


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def deferred(name, scope):
    # Printed, never counted: a deferred expectation is neither a
    # pass nor a fail — it names the phase that owns it.
    print(f"DEFERRED  {name}  {scope}")


def _canonical(entries):
    return len(json.dumps(list(entries), indent=2,
                          ensure_ascii=True).encode("utf-8"))


def _digest(obj):
    blob = json.dumps(obj, sort_keys=True, default=repr,
                      ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _ser_state(p):
    """Serialized state with the volatile wall-clock 'saved' field
    removed. serialize() stamps 'saved' at second resolution; the
    R5RD battery's raw byte comparison straddled a second boundary
    once on this build (run 1: 93/94, the sole diff was /saved) —
    an instrument artifact, proven by field diff, not a mutation.
    This suite compares state, not clocks."""
    from form.persist import serialize
    payload = serialize(p)
    payload.pop("saved", None)
    return json.dumps(payload, indent=2, ensure_ascii=True,
                      sort_keys=True).encode("utf-8")


def _refused(fn):
    from form.open import HistoryAdmissionRefusal
    try:
        fn()
    except HistoryAdmissionRefusal as exc:
        return True, exc
    except Exception as exc:  # noqa: BLE001
        return False, exc
    return False, None


def _subsystem_digest(p, fn_name):
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
    if fn_name == "radial_drift":
        p.lattice.put(30, 30, 1, label="seedcell",
                      content="seedpayload")
    elif fn_name == "internet_on":
        p.internet = None
    elif fn_name == "internet_off":
        _gate_on(p)


def _filler_for_bytes(entry, target):
    base = _canonical(["", entry])
    filler = "f" * (target - base)
    assert _canonical([filler, entry]) == target
    return filler


def main():
    from form.open import open_program

    p = open_program(OWNER)
    cap_hist = [f"s7canary-{RUN}"] + [f"cap-{i:05d}" for i in range(CAP - 1)]

    # ── 1. PER-METHOD AT-CAP + BYTES+1: typed refusal, ZERO effects ──
    for scenario in ("entrycap", "bytecap_plus1"):
        for fn_name in S7:
            _prep(p, fn_name)
            if scenario == "entrycap":
                p.history = list(cap_hist)
            else:
                p.history = [_filler_for_bytes(ENTRY[fn_name],
                                                CAP_BYTES + 1)]
            before = (_digest(list(p.history)), _ser_state(p),
                      _subsystem_digest(p, fn_name))
            refused, exc = _refused(getattr(p, fn_name))
            after = (_digest(list(p.history)), _ser_state(p),
                     _subsystem_digest(p, fn_name))
            check(f"refusal_clean_{fn_name}_{scenario}",
                  refused and after == before
                  and f"s7canary-{RUN}" not in str(exc),
                  f"refused={refused} exc={type(exc).__name__}")

    # ── 2. EXACT FITS ADMITTED (entry cap-1 and byte cap) ──
    # Admission half asserted exactly; the len==CAP retention half
    # is DEFERRED (T2 note() cut) and printed as such below.
    for fn_name in S7:
        _prep(p, fn_name)
        p.history = list(cap_hist[:-1])
        refused, _ = _refused(getattr(p, fn_name))
        check(f"exact_fit_entry_admitted_{fn_name}",
              not refused and p.history[-1] == ENTRY[fn_name],
              f"refused={refused} last={p.history[-1]!r:.40}")
        filler = _filler_for_bytes(ENTRY[fn_name], CAP_BYTES)
        _prep(p, fn_name)
        p.history = [filler]
        refused, _ = _refused(getattr(p, fn_name))
        check(f"exact_fit_bytes_admitted_{fn_name}",
              not refused and list(p.history) == [filler, ENTRY[fn_name]]
              and _canonical(p.history) == CAP_BYTES,
              f"refused={refused} bytes={_canonical(p.history)}")
    deferred("retention_len_eq_cap_after_admission",
             "DEFERRED T2: note() history_max cut (separate "
             "save/load phase, Director 7079092723)")

    # ── 3. UNICODE: bytes measured, not chars ──
    p.history = ["é" * 400_000]  # 400k chars, ~2.4M canonical bytes
    refused, _ = _refused(p.enhance_on)
    check("unicode_bytes_not_chars_refused", refused,
          f"bytes={_canonical(p.history) + 30}")
    p.history = ["a" * 400_000]  # same char count, ~0.4M bytes
    refused, _ = _refused(p.enhance_on)
    check("unicode_ascii_control_admitted",
          not refused and p.history[-1] == ENTRY["enhance_on"],
          f"refused={refused}")

    # ── 4. SANITIZE-BEFORE-MEASURE (mechanism level, _s7_admit) ──
    # The S7 labels are fixed literals (sanitize is identity on
    # them — verified for all seven); the straddle is therefore
    # proven on the shared admission mechanism every S7 method
    # calls, with a caller-shaped label.
    raw_label = "token " + "x" * 200  # sanitize shrinks to 16 chars
    san_entry = p._s7_entry(9, "Show", raw_label)
    raw_entry = f"09[Show] :: {raw_label[:40]}"
    filler = _filler_for_bytes(san_entry, CAP_BYTES)
    assert _canonical([filler, raw_entry]) > CAP_BYTES
    p.history = [filler]
    with p._admission_lock():
        try:
            got = p._s7_admit(9, "Show", raw_label)
            admit_err = ""
        except Exception as exc:  # noqa: BLE001
            got, admit_err = None, repr(exc)
    canary_entry = p._s7_entry(9, "Show", f"password: {SECRET}")
    check("sanitize_before_measure_straddle",
          got == san_entry and SECRET not in canary_entry
          and "[REDACTED]" in canary_entry,
          f"admitted={got is not None} err={admit_err} "
          f"raw_bytes={_canonical([filler, raw_entry])} "
          f"san_bytes={_canonical([filler, san_entry])}")

    # ── 5. FIRST-EFFECT ORDERING on the admitted path ──
    # Wrap note(): the subsystem digest AT append time proves
    # whether the method's effect ran before or after its note.
    orig_note = p.note

    def ordering_leg(fn_name, note_first):
        _prep(p, fn_name)
        p.history = [f"ord-{fn_name}"]
        seen = {}

        def recorder(action):
            seen["digest"] = _subsystem_digest(p, fn_name)
            return orig_note(action)
        p.note = recorder
        try:
            getattr(p, fn_name)()
        finally:
            p.note = orig_note
        after = _subsystem_digest(p, fn_name)
        if note_first:
            ok = seen.get("digest") != after
        else:
            ok = seen.get("digest") == after
        check(f"first_effect_ordering_{fn_name}", ok,
              f"note_first={note_first}")

    for name in ("radial_drift", "internet_on", "internet_off",
                 "enhance_on", "enhance_off"):
        ordering_leg(name, note_first=False)
    for name in ("sandbox_on", "sandbox_off"):
        ordering_leg(name, note_first=True)

    # ── 6. internet_off NO-GATE return unchanged, even over cap ──
    p.internet = None
    for tag, hist in (("entrycap", list(cap_hist)),
                      ("bytecap", [_filler_for_bytes(
                          ENTRY["internet_off"], CAP_BYTES + 1)])):
        p.history = list(hist)
        before = _digest(list(p.history))
        ret = p.internet_off()
        check(f"internet_off_no_gate_return_unchanged_{tag}",
              ret == {"ok": True, "on": False} and p.internet is None
              and _digest(list(p.history)) == before,
              f"ret={ret!r:.40}")

    # ── 7. MIXED-WRITER RACE: check-and-append is atomic ──
    # Non-S7 note_seed writers race S7 callers at the entry cap.
    # Invariant: no S7 entry is EVER appended when the history
    # length at its (locked) append moment would exceed the cap —
    # i.e. no writer interleaves between an S7 preflight and its
    # append, even though note() truncations keep changing the
    # length the next preflight sees.
    p.history = list(cap_hist)
    _gate_on(p)
    s7_entries = set(ENTRY.values())
    appends = []
    errors = []

    def shim(action):
        if action in s7_entries:
            appends.append((action, len(p.history)))
        return orig_note(action)
    p.note = shim

    def s7_caller():
        for _ in range(120):
            for name in S7:
                try:
                    getattr(p, name)()
                except Exception as exc:  # noqa: BLE001
                    if type(exc).__name__ != "HistoryAdmissionRefusal":
                        errors.append(repr(exc))

    def plain_writer():
        for i in range(240):
            p.note_seed(9, "Show", f"race-{i}")

    threads = ([threading.Thread(target=s7_caller) for _ in range(2)]
               + [threading.Thread(target=plain_writer)
                  for _ in range(2)])
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=180)
    p.note = orig_note
    check("mixed_writer_race_atomic_check_append",
          not errors and all(n + 1 <= CAP for _, n in appends)
          and len(appends) > 0,
          f"s7_appends={len(appends)} errors={errors[:2]}")

    # ── 8. S7-ONLY RACE at the byte boundary: exactly one wins ──
    filler = _filler_for_bytes(ENTRY["enhance_on"], CAP_BYTES)
    p.history = [filler]
    outcomes = []

    def racer():
        r, _ = _refused(p.enhance_on)
        outcomes.append(r)
    racers = [threading.Thread(target=racer) for _ in range(4)]
    for t in racers:
        t.start()
    for t in racers:
        t.join(timeout=60)
    check("s7_race_exactly_one_admission",
          outcomes.count(False) == 1 and outcomes.count(True) == 3
          and _canonical(p.history) == CAP_BYTES,
          f"outcomes={outcomes}")

    # ── 9. LOCK ORDER: owner_state_lock OUTER, admission INNER ──
    from form.owner_state_lock import owner_state_lock, OwnerLockBusy
    owner2 = f"{OWNER}L"
    p2 = open_program(owner2)
    # Positive: the production nesting (save's snapshot inside the
    # owner transaction) completes promptly.
    done = []

    def positive():
        with owner_state_lock(owner2):
            done.append(p2.history_snapshot())
    t = threading.Thread(target=positive)
    t.start()
    t.join(timeout=15)
    check("lock_order_positive_nesting_completes",
          not t.is_alive() and len(done) == 1)
    # Negative mutant: deliberately INVERT the order in two threads.
    # The inversion must be DETECTED (both sides blocked at the
    # watchdog instant) — proving the hazard is real and the
    # hierarchy in the product code is what prevents it.
    ev_owner_held = threading.Event()
    ev_adm_held = threading.Event()
    inv = {"busy": False, "completed": False}

    def holder():
        with owner_state_lock(owner2):
            ev_owner_held.set()
            # Wait until the inverter holds the admission lock,
            # then reach for it: the inversion is now real.
            ev_adm_held.wait(timeout=15)
            lock = p2._admission_lock()
            lock.acquire()
            try:
                inv["completed"] = True
            finally:
                lock.release()

    def inverter():
        lock = p2._admission_lock()
        lock.acquire()
        ev_adm_held.set()
        try:
            with owner_state_lock(owner2):
                pass
        except OwnerLockBusy:
            inv["busy"] = True
        finally:
            lock.release()

    th = threading.Thread(target=holder, daemon=True)
    ti = threading.Thread(target=inverter, daemon=True)
    th.start()
    ev_owner_held.wait(timeout=15)
    ti.start()
    ev_adm_held.wait(timeout=15)
    time.sleep(3)
    detected = th.is_alive() and ti.is_alive() \
        and not inv["completed"]
    th.join(timeout=30)
    ti.join(timeout=30)
    check("lock_order_inversion_detected_negative_mutant",
          detected and inv["busy"] and inv["completed"],
          f"detected={detected} busy={inv['busy']} "
          f"holder_completed={inv['completed']}")

    # ── 10. SAVE-READER atomic snapshot under concurrent appends ──
    p3 = open_program(f"{OWNER}S")
    stop = []

    def appender():
        for i in range(3000):
            p3.note(f"m{i:05d}")
            if i % 25 == 0:
                time.sleep(0.001)

    def contiguous(snap):
        idx = []
        for s in snap:
            if not (isinstance(s, str) and s.startswith("m")
                    and s[1:].isdigit()):
                return False
            idx.append(int(s[1:]))
        return all(b == a + 1 for a, b in zip(idx, idx[1:]))

    t = threading.Thread(target=appender)
    t.start()
    snaps_ok = True
    n_snaps = 0
    while t.is_alive():
        snap = p3.history_snapshot()
        n_snaps += 1
        if not contiguous(snap):
            snaps_ok = False
            break
    t.join(timeout=60)
    from form.persist import serialize
    ser_hist = serialize(p3)["history"]
    snap = p3.history_snapshot()
    check("save_reader_atomic_snapshot",
          snaps_ok and n_snaps >= 10 and contiguous(ser_hist)
          and ser_hist == snap[-24:],
          f"snapshots={n_snaps}")
    probe = p3.history_snapshot()
    probe.append("tamper")
    check("snapshot_is_a_copy", "tamper" not in p3.history)

    # ── 11. OWNER ISOLATION ──
    pa = open_program(f"{OWNER}A")
    pb = open_program(f"{OWNER}B")
    pa.history = list(cap_hist)
    refused_a, _ = _refused(pa.enhance_on)
    refused_b, _ = _refused(pb.enhance_on)
    check("owner_isolation",
          refused_a and not refused_b
          and pa._admission_lock() is not pb._admission_lock()
          and pb.history[-1] == ENTRY["enhance_on"],
          f"a={refused_a} b={refused_b}")

    # ── 12. REENTRANT NESTED NOTE under the held lock ──
    p.history = ["seed-entry"]
    nested = []

    def nest():
        with p._admission_lock():
            p.note_seed(10, "Keep", "nested-writer")
            nested.append(p.enhance_on())
    t = threading.Thread(target=nest)
    t.start()
    t.join(timeout=30)
    check("reentrant_nested_note_no_deadlock",
          not t.is_alive() and len(nested) == 1
          and p.history[-1] == ENTRY["enhance_on"],
          f"alive={t.is_alive()}")

    # ── 13. NEGATIVE PRIVACY CANARIES ──
    # A secret-shaped value sitting in history must never appear
    # in a refusal (message carries counts/bytes only) — and the
    # S7 entry computation redacts secret-shaped labels before
    # measure and storage (leg 4). Here: refusal-side canary.
    p.history = [f"password: {SECRET}"] + \
        [f"cap-{i:05d}" for i in range(CAP - 1)]
    refused, exc = _refused(p.sandbox_on)
    check("privacy_canary_refusal_carries_no_content",
          refused and SECRET not in str(exc)
          and "password" not in str(exc),
          f"exc={str(exc)[:60]!r}")

    # ── 14. LEGACY CONTROLS: deferred cuts visibly unchanged ──
    q = open_program(f"{OWNER}G")
    for i in range(30):
        q.note(f"legacy-{i}")
    t1 = None
    q.note("y" * 200)
    t1 = q.history[-1]
    check("legacy_controls_t1_t2_t3_unchanged",
          len(q.history) == 24 and len(t1) == 120
          and serialize(q)["history"] == list(q.history)[-24:],
          f"len={len(q.history)} entry_chars={len(t1)} "
          "(T1/T2/T3 DEFERRED, behavior preserved verbatim)")
    deferred("saveload_whole_history_retention",
             "DEFERRED T3/T4: serializer [-24:] + restore cuts "
             "(separate save/load phase)")
    deferred("note_door_admission",
             "OUT OF S7 SCOPE: the note funnel carries the lock, "
             "not the cap (Director 7079092723 authorizes S7 "
             "method entries only)")

    # ── 15. DEEPCOPY SAFETY (regression pin, #513 c13 defect) ──
    # simulate_board (Dell 31 [Simulate]) isolates a rehearsal by
    # deepcopying the live Program; the per-Program RLock can be
    # neither deepcopied nor shared with the copy. Program
    # __getstate__ excludes the lock from copied state and the
    # copy recreates its OWN fresh lock via _admission_lock().
    # At the pre-repair head this leg's deepcopy raised TypeError
    # and every simulation returned ok=False (c13 9/20).
    import copy as _copy
    from form.dell_matrix.simulate_board import run_simulation
    d = open_program(f"{OWNER}D")
    d.note("deepcopy pin entry")
    clone = None
    dc_error = ""
    try:
        clone = _copy.deepcopy(d)
    except Exception as exc:  # recorded as the check's detail
        dc_error = f"{type(exc).__name__}: {exc}"
    sim = run_simulation(d, "08[Create] :: s7_deepcopy_pin")
    check("deepcopy_safe_own_lock_simulation_executes",
          clone is not None
          and clone._admission_lock() is not d._admission_lock()
          and clone.history_snapshot() == list(d.history)
          and sim.get("ok") is True
          and sim.get("outcome") == "executed",
          f"deepcopy_error={dc_error} sim_ok={sim.get('ok')} "
          f"sim_error={sim.get('error', '')}")

    _cleanup()
    check("cleanup_clean", not _CLEANUP_ERRORS,
          "; ".join(_CLEANUP_ERRORS))
    ok_n = sum(1 for _, ok in RESULTS if ok)
    print(f"r5d_s7_admission_test: {ok_n}/{len(RESULTS)} PASS")
    return 0 if ok_n == len(RESULTS) else 1


def _cleanup():
    from form.persist import _STATE_DIR, _safe_owner
    from form.dell_matrix.nursery import owner_nursery_path
    state = Path(_STATE_DIR)
    for owner in (OWNER, f"{OWNER}L", f"{OWNER}S", f"{OWNER}A",
                  f"{OWNER}B", f"{OWNER}G", f"{OWNER}D"):
        safe = _safe_owner(owner)
        cands = [state / f"program_{safe}.json",
                 Path(owner_nursery_path(owner))]
        cands += list(state.glob(f"*{safe}*"))
        for c in dict.fromkeys(cands):
            try:
                if c.is_file():
                    c.unlink()
            except OSError as exc:
                _CLEANUP_ERRORS.append(f"{c}: {exc}")


def smoke() -> bool:
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
