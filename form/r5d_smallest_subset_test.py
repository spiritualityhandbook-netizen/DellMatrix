#!/usr/bin/env python3
"""R5-D smallest genuinely side-effect-free subset — proofs.

Answers Director 7032352360: propose the smallest genuinely
side-effect-free initial implementation subset; prove exact
canonical UTF-8 sanitized byte admission and no state/filesystem
changes on refusal; separate process-thread TOCTOU from
unproven multi-process behavior.

PROPOSED SUBSET S7 (see R5D_SMALLEST_SUBSET_PROPOSAL_2026-11-20):
radial_drift, internet_on, internet_off, sandbox_on,
sandbox_off, enhance_on, enhance_off — the 7 of the 10 named at
8170967 with files_same=True at cap AND over in both runs, one
fixed-literal note_seed each, no file/socket/thread effects.
EXCLUDED: save (writes program file), visual (writes snapshot
files), live_visual (starts a localhost HTTP listener — an
effect the state-dir snapshot cannot see; probed directly).

ADMISSION CONTRACT (R5-C policy 7026062701): admit iff entries
<= 10,000 AND canonical bytes <= 2,097,152, canonical bytes =
len(json.dumps(history, indent=2, ensure_ascii=True)
.encode("utf-8")) on the post-sanitize history incl. the exact
eventual entry; sanitize-before-measure; exact fit admitted;
first-reached binds; typed pre-mutation refusal; on refusal the
full serialized state AND the state-dir file set/sha256 are
unchanged and no history canary leaks.

STATUS: FAILING-FIRST on current main (7027419): note() evicts
at history_max=24, no typed refusal exists, sanitize applies
only under the chain flag. Exclusion probes PASS today (they
prove the excluded effects exist). Labels: INTEGRATION,
in-process THREADS only for TOCTOU; multi-process writers are
NOT TESTED and remain UNKNOWN. NO product code changed.
Hygiene: uuid owner, exact-pattern cleanup; cleanup errors fail.
"""
from __future__ import annotations

import hashlib
import json
import socket
import sys
import threading
import uuid
from pathlib import Path

REPO = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, REPO)

RESULTS = []
_CLEANUP_ERRORS = []
RUN = uuid.uuid4().hex[:8]
OWNER = f"R5SS{RUN}"
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
CANARY = f"CANARY{RUN}SECRET"
HIST_CANARY = f"histcanary-{RUN}"


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def _canonical(entries):
    return len(json.dumps(list(entries), indent=2,
                          ensure_ascii=True).encode("utf-8"))


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


def _gate_on(p):
    from form.dell_matrix.internet_gate import InternetGate
    if p.internet is None:
        p.internet = InternetGate()
    try:
        p.internet.turn_on()
    except Exception:  # noqa: BLE001
        pass


def _filler_for_bytes(entry, target):
    """One filler entry so canonical([filler, entry]) == target."""
    base = _canonical(["", entry])
    n = target - base
    assert n >= 0, (target, base)
    filler = "f" * n
    assert _canonical([filler, entry]) == target
    return filler


def main():
    from form.open import open_program
    from form.mandell.redaction import sanitize_text

    # ── CONTROLS ──
    check("control_sanitize_authority_redacts",
          CANARY not in sanitize_text(f"password: {CANARY}"),
          sanitize_text(f"password: {CANARY}"))
    check("control_canonical_ensure_ascii_escapes",
          _canonical(["é"]) - _canonical(["a"]) == 5,
          f"é-entry={_canonical(['é'])} a-entry={_canonical(['a'])} "
          "(BMP char = 6 canonical bytes vs 1)")

    p = open_program(OWNER)
    cap_hist = [HIST_CANARY] + [f"cap-{i:05d}" for i in range(CAP - 1)]

    # ── EXCLUSION PROBES (PASS today: the effects exist) ──
    p.history = list(cap_hist)
    snap0 = _dir_snapshot()
    p.save()
    check("excl_save_writes_file_at_cap", _dir_snapshot() != snap0,
          "save() purpose is a disk write; files change at cap")
    p.history = list(cap_hist)
    snap0 = _dir_snapshot()
    p.visual()
    check("excl_visual_writes_file_at_cap", _dir_snapshot() != snap0,
          "write_visual writes snapshot files at cap")
    res = p.live_visual(port=18777)
    listening = False
    try:
        with socket.create_connection(("127.0.0.1", 18777), timeout=2):
            listening = True
    except OSError:
        listening = False
    try:
        from form.dell_matrix import live_visual as _lv
        if getattr(_lv, "_LIVE_SERVER", None) is not None:
            _lv._LIVE_SERVER.shutdown()
            _lv._LIVE_SERVER = None
    except Exception:  # noqa: BLE001
        pass
    check("excl_live_visual_starts_listener", listening,
          f"start_live effect invisible to state-dir snapshot; "
          f"ret={res!r:.80}")

    # ── S7 PER-CALLER: entry-cap refusal / fit admission / bytes ──
    for fn_name in S7:
        fn = getattr(p, fn_name)
        entry = ENTRY[fn_name]
        # entry-cap refusal: no state, no files, no leak
        if fn_name == "internet_off":
            _gate_on(p)
        p.history = list(cap_hist)
        before = _ser_bytes(p)
        snap0 = _dir_snapshot()
        refused, how = _refusal_seen(fn)
        check(f"s7_{fn_name}_entrycap_refusal_clean",
              refused and _ser_bytes(p) == before
              and _dir_snapshot() == snap0
              and HIST_CANARY not in repr(how),
              f"refused={refused}")
        # entry-cap-1 admitted, exact entry appended
        if fn_name == "internet_off":
            _gate_on(p)
        p.history = list(cap_hist[:-1])
        refused, _ = _refusal_seen(fn)
        check(f"s7_{fn_name}_entrycap_minus1_admitted",
              not refused and len(p.history) == CAP
              and p.history[-1] == entry,
              f"refused={refused} len={len(p.history)} "
              f"last={p.history[-1] if p.history else ''!r:.40}")
        # byte-cap exact fit admitted
        filler = _filler_for_bytes(entry, CAP_BYTES)
        if fn_name == "internet_off":
            _gate_on(p)
        p.history = [filler]
        refused, _ = _refusal_seen(fn)
        check(f"s7_{fn_name}_bytecap_exact_fit_admitted",
              not refused and list(p.history) == [filler, entry]
              and _canonical(p.history) == CAP_BYTES,
              f"refused={refused} bytes={_canonical(p.history)}")
        # byte-cap+1 refusal: no state, no files
        filler1 = _filler_for_bytes(entry, CAP_BYTES + 1)
        if fn_name == "internet_off":
            _gate_on(p)
        p.history = [filler1]
        before = _ser_bytes(p)
        snap0 = _dir_snapshot()
        refused, _ = _refusal_seen(fn)
        check(f"s7_{fn_name}_bytecap_plus1_refusal_clean",
              refused and _ser_bytes(p) == before
              and _dir_snapshot() == snap0,
              f"refused={refused}")

    # ── BYTE EXACTNESS at the shared capture door (note_seed) ──
    # bytes-not-chars: equal char length, different canonical bytes
    lab_a, lab_b = "a" * 40, "é" * 40
    ent_a = f"09[Show] :: {lab_a}"
    ent_b = f"09[Show] :: {lab_b}"
    outcomes = {}
    for tag, lab, ent in (("ascii", lab_a, ent_a),
                          ("accent", lab_b, ent_b)):
        filler = _filler_for_bytes(ent, CAP_BYTES)
        p.history = [filler]
        refused, _ = _refusal_seen(lambda: p.note_seed(9, "Show", lab))
        outcomes[tag] = (refused, list(p.history) == [filler, ent])
    check("bytes_measured_not_chars",
          outcomes["ascii"] == (False, True)
          and outcomes["accent"][0] is False
          and _canonical([_filler_for_bytes(ent_b, CAP_BYTES),
                          ent_b]) == CAP_BYTES,
          f"outcomes={outcomes} (accent entry costs "
          f"{_canonical([ent_b]) - _canonical([ent_a])} more bytes "
          "at equal chars; filler rebalanced to the same byte cap)")
    # sharper straddle: SAME filler, ascii fits / accent refuses
    shared = _filler_for_bytes(ent_a, CAP_BYTES)
    p.history = [shared]
    ref_a, _ = _refusal_seen(lambda: p.note_seed(9, "Show", lab_a))
    p.history = [shared]
    ref_b, _ = _refusal_seen(lambda: p.note_seed(9, "Show", lab_b))
    check("bytes_straddle_same_filler",
          (not ref_a) and ref_b,
          f"ascii_refused={ref_a} accent_refused={ref_b} "
          "(char-count admission would treat them identically)")
    # sanitize-before-measure: raw over cap, sanitized exact fit
    raw_label = "token " + "x" * 200
    san_label = sanitize_text(raw_label)
    ent_raw = f"09[Show] :: {raw_label[:40]}"
    ent_san = f"09[Show] :: {san_label[:40]}"
    filler = _filler_for_bytes(ent_san, CAP_BYTES)
    assert _canonical([filler, ent_raw]) > CAP_BYTES
    p.history = [filler]
    p._chain_sanitize_redact = True
    refused, _ = _refusal_seen(
        lambda: p.note_seed(9, "Show", raw_label))
    stored_ok = list(p.history) == [filler, ent_san]
    p._chain_sanitize_redact = False
    check("sanitize_before_measure_straddle",
          not refused and stored_ok,
          f"refused={refused} stored_sanitized={stored_ok} "
          f"raw_bytes={_canonical([filler, ent_raw])} "
          f"san_bytes={_canonical([filler, ent_san])}")
    # sanitize canary at entry cap: refused, canary never in state
    p.history = list(cap_hist)
    p._chain_sanitize_redact = True
    before = _ser_bytes(p)
    refused, _ = _refusal_seen(
        lambda: p.note_seed(9, "Show", f"password: {CANARY}"))
    leaked = CANARY.encode() in _ser_bytes(p)
    p._chain_sanitize_redact = False
    check("sanitize_canary_at_cap_refused_no_leak",
          refused and not leaked and _ser_bytes(p) == before,
          f"refused={refused} canary_in_state={leaked}")

    # ── TOCTOU: THREAD evidence only ──
    _gate_on(p)
    p.history = list(cap_hist)
    before = _ser_bytes(p)
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
          and _ser_bytes(p) == before,
          f"calls={len(results_t)} refused={sum(results_t)}")
    print("NOT_TESTED  multiprocess_writers  UNKNOWN — no "
          "cross-process claim is made by this suite")

    # ── SAVELOAD separation (NOT an S7 verdict) ──
    p.history = [f"hist-{i:02d}" for i in range(30)]
    path = p.save()
    from form.open import Program
    try:
        q = Program.load(OWNER, path)
        whole = list(q.history) == [f"hist-{i:02d}" for i in range(30)]
        err = ""
    except Exception as exc:  # noqa: BLE001
        whole, err = False, repr(exc)
    check("saveload_restart_30_whole_SEPARATE_CONTRACT", whole,
          f"err={err} (save/load contract; excluded from S7)")

    _cleanup()
    check("cleanup_clean", not _CLEANUP_ERRORS,
          "; ".join(_CLEANUP_ERRORS))
    ok_n = sum(1 for _, ok in RESULTS if ok)
    s7_n = sum(1 for n, ok in RESULTS if ok and n.startswith("s7_"))
    print(f"R5SS {ok_n}/{len(RESULTS)} PASS (S7 {s7_n}/28; "
          "exclusion probes and saveload counted separately)")
    return 0 if ok_n == len(RESULTS) else 1


def _cleanup():
    from form.persist import _STATE_DIR, _safe_owner
    from form.dell_matrix.nursery import owner_nursery_path
    state = Path(_STATE_DIR)
    safe = _safe_owner(OWNER)
    cands = [state / f"program_{safe}.json",
             Path(owner_nursery_path(OWNER))]
    cands += list(state.glob(f"*{safe}*"))
    visual_dir = state.parent / "visual"
    if visual_dir.is_dir():
        cands += [x for x in visual_dir.rglob("*")
                  if x.is_file() and safe.lower() in x.name.lower()]
    for c in dict.fromkeys(cands):
        try:
            if c.is_file():
                c.unlink()
        except OSError as exc:
            _CLEANUP_ERRORS.append(f"{c}: {exc}")


if __name__ == "__main__":
    sys.exit(main())
