#!/usr/bin/env python3
"""R5-D named minimal caller subset — executable caller-level proofs.

Answers Director 7031879676: "narrow to a named minimal caller
subset; publish executable at-cap/+1 caller-level tests asserting
no prior state/external side effects, canonical UTF-8
sanitize-before-measure parity, stable preflight under
concurrency/TOCTOU, restart/fault/legacy and privacy behavior;
document the 10 SKIPs explicitly; do not silently promote all 25
from a function-level heuristic."

NAMED MINIMAL SUBSET (10 callers) — the intersection of:
  (a) the 25 INVENTORY-CLEAN sites of R5D_SIDE_EFFECT_INVENTORY
      (evidence 1d14ebe), and
  (b) form/open.py Program methods invocable with NO required
      arguments (the only callers executable end-to-end without
      invented fixtures):
  open.py:1116 radial_drift, 1221 internet_on, 1228 internet_off,
  2056 sandbox_on, 2063 sandbox_off, 2068 enhance_on,
  2072 enhance_off, 2166 save, 2171 visual, 2191 live_visual.

ACCOUNTING OF THE 25 CLEAN (nothing silently promoted):
  10 in the subset above;
  4 CLEAN but arg-required, reported SKIP below with exact args
     (806 set_view[room_id], 1011 enter_workshop[workshop_id],
      1110 set_lattice_size[size], 2157 run_script[script]);
  11 CLEAN but non-Program callers needing module fixtures, NOT in
     this subset and NOT claimed proven here: allwhere 382/417/475,
     code_evolution 76/254, first_person 537, fourier 199,
     linear_algebra 192, core_ii_exec 134, repl 419/483.
The other 6 SKIPs of the earlier 34-caller layer are non-CLEAN
sites (594/599 zoom_to[ref], 778 bimo_dock[slot,persona],
952 set_weather[condition], 1165 place[id,label],
2052 reject_proposal[pid]) — all 10 SKIPs are printed explicitly
in section S and never counted as PASS.

Per subset caller, at history == cap (10,000) AND cap+1 (10,001):
  A. typed refusal (exception named Refus*/History*/Cap*/Budget*,
     refusal message, LEGACY_OVER_BUDGET, or ok=False receipt);
  B. serialize(program) byte-identical after the call — i.e. NONE
     of the caller's own mutations ran before the refusal;
  C. external side effects: the state dir's file set + per-file
     sha256 is unchanged across the call (catches save()/visual()
     writes and live_visual artifacts).
Cross-cutting:
  U. UTF-8 parity: note_seed at cap with ASCII vs multibyte
     (accented/CJK/emoji/combining) labels of equal char length
     must refuse identically; sanitize-before-measure: with the
     chain sanitize flag on, a canary secret label is refused and
     the canary never appears in serialized state.
  T. TOCTOU/concurrency: 4 threads x subset callers at cap — every
     call refused, serialized state identical afterwards.
  R. restart/legacy/privacy: an at-cap state survives a
     serialize -> save-file -> Program.load round trip whole;
     a legacy cap+50 file loads whole (no silent truncation);
     refusal output never contains a history canary string.

STATUS: FAILING-FIRST on current main (7027419): note() truncates
to history_max=24, no typed refusal exists, save()/visual() write
files unconditionally. Expected FAIL today; the R5-D build for
these 10 callers turns this suite green. NO product code changed.
Labels: INTEGRATION (in-process; threads share one Program —
multi-process writers remain UNKNOWN per the path-proof record).
Hygiene: uuid owner, exact-pattern cleanup; cleanup errors fail.
"""
from __future__ import annotations

import hashlib
import json
import sys
import threading
import uuid
from pathlib import Path

REPO = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, REPO)

RESULTS = []
_CLEANUP_ERRORS = []
RUN = uuid.uuid4().hex[:8]
OWNER = f"R5CS{RUN}"
CAP = 10_000
SUBSET = ["radial_drift", "internet_on", "internet_off",
          "sandbox_on", "sandbox_off", "enhance_on", "enhance_off",
          "save", "visual", "live_visual"]
SKIPS = [("open.py:594", "zoom_to", ["ref"], "BLOCKED"),
         ("open.py:599", "zoom_to", ["ref"], "BLOCKED"),
         ("open.py:778", "bimo_dock", ["slot", "persona"], "BLOCKED"),
         ("open.py:806", "set_view", ["room_id"], "CLEAN"),
         ("open.py:952", "set_weather", ["condition"], "BLOCKED"),
         ("open.py:1011", "enter_workshop", ["workshop_id"], "CLEAN"),
         ("open.py:1110", "set_lattice_size", ["size"], "CLEAN"),
         ("open.py:1165", "place", ["id", "label"], "BLOCKED"),
         ("open.py:2052", "reject_proposal", ["pid"], "BLOCKED"),
         ("open.py:2157", "run_script", ["script"], "CLEAN")]
CANARY = f"CANARY{RUN}SECRET"
HIST_CANARY = f"histcanary-{RUN}"


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


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


def main():
    from form.open import Program, open_program
    from form.persist import serialize

    check("control_subset_named_10", len(SUBSET) == 10,
          ",".join(SUBSET))
    p = open_program(OWNER)
    cap_hist = [HIST_CANARY] + [f"cap-{i:05d}" for i in range(CAP - 1)]
    over_hist = cap_hist + ["cap-over"]

    # ── A/B/C per caller at cap and cap+1 ──
    for fn_name in SUBSET:
        fn = getattr(p, fn_name, None)
        if fn is None or not callable(fn):
            print(f"SKIP  subset_{fn_name}  no method")
            continue
        for label, hist in (("atcap", cap_hist), ("over", over_hist)):
            p.history = list(hist)
            before = serialize(p)
            snap0 = _dir_snapshot()
            refused, how = _refusal_seen(fn)
            unchanged = serialize(p) == before
            snap_same = _dir_snapshot() == snap0
            leak = HIST_CANARY in repr(how)
            check(f"{label}_{fn_name}",
                  refused and unchanged and snap_same and not leak,
                  f"refused={refused} unchanged={unchanged} "
                  f"files_same={snap_same} canary_leak={leak}")

    # ── U: UTF-8 parity + sanitize-before-measure ──
    labels = {"ascii": "a" * 40, "accent": "é" * 40,
              "cjk": "漢" * 40, "emoji": "🙂" * 40,
              "combining": "é" * 40}
    outcomes = {}
    for kind, lab in labels.items():
        p.history = list(cap_hist)
        before = serialize(p)
        refused, _ = _refusal_seen(lambda: p.note_seed(9, "Show", lab))
        outcomes[kind] = (refused, serialize(p) == before)
    check("utf8_parity_all_labels_refuse_identically",
          len(set(outcomes.values())) == 1 and outcomes["ascii"][0],
          f"outcomes={outcomes}")
    p.history = list(cap_hist)
    p._chain_sanitize_redact = True
    refused, _ = _refusal_seen(
        lambda: p.note_seed(9, "Show", f"token {CANARY}"))
    leaked = CANARY in json.dumps(serialize(p))
    check("sanitize_before_measure_canary",
          refused and not leaked,
          f"refused={refused} canary_in_state={leaked}")
    p._chain_sanitize_redact = False

    # ── T: concurrency / TOCTOU stability at cap ──
    p.history = list(cap_hist)
    before = serialize(p)
    results_t = []

    def worker():
        for name in SUBSET:
            r, _ = _refusal_seen(getattr(p, name))
            results_t.append(r)
    threads = [threading.Thread(target=worker) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=60)
    check("toctou_concurrent_all_refused_state_stable",
          len(results_t) == 40 and all(results_t)
          and serialize(p) == before,
          f"calls={len(results_t)} refused={sum(results_t)}")

    # ── R: restart round trip + legacy loads whole + privacy ──
    p.history = list(cap_hist)
    saved_path = p.save()
    try:
        q = Program.load(OWNER)
        rt_ok = list(q.history) == cap_hist
        rt_err = ""
    except Exception as exc:  # noqa: BLE001
        rt_ok, rt_err = False, repr(exc)
    check("restart_atcap_roundtrip_whole", rt_ok, f"err={rt_err}")
    from form.persist import _STATE_DIR, _safe_owner
    state_file = Path(_STATE_DIR) / f"program_{_safe_owner(OWNER)}.json"
    data = json.loads(state_file.read_text())
    legacy = [f"leg-{i:05d}" for i in range(CAP + 50)]
    data["history"] = legacy
    state_file.write_text(json.dumps(data))
    try:
        q2 = Program.load(OWNER)
        leg_ok = list(q2.history) == legacy
        leg_err = ""
    except Exception as exc:  # noqa: BLE001
        leg_ok, leg_err = False, repr(exc)
    check("legacy_over_cap_loads_whole", leg_ok,
          f"err={leg_err} (silent truncation = FAIL)")

    # ── S: the 10 SKIPs, explicit, never PASS ──
    for tag, fn_name, args, inv in SKIPS:
        print(f"SKIP  caller_{tag}_{fn_name}  needs args {args}  "
              f"inventory={inv}  (excluded from subset; not a pass)")

    _cleanup()
    check("cleanup_clean", not _CLEANUP_ERRORS,
          "; ".join(_CLEANUP_ERRORS))
    ok_n = sum(1 for _, ok in RESULTS if ok)
    print(f"R5CS {ok_n}/{len(RESULTS)} PASS "
          f"(+10 documented SKIP, never PASS)")
    return 0 if ok_n == len(RESULTS) else 1


def _cleanup():
    from form.persist import _STATE_DIR, _safe_owner
    from form.dell_matrix.nursery import owner_nursery_path
    state = Path(_STATE_DIR)
    safe = _safe_owner(OWNER)
    cands = [state / f"program_{safe}.json",
             Path(owner_nursery_path(OWNER))]
    cands += list(state.glob(f"*{safe}*"))
    cands += list((state / "visual").glob(f"*{safe}*")) \
        if (state / "visual").exists() else []
    for pth in set(cands):
        try:
            if pth.is_dir():
                import shutil
                shutil.rmtree(pth)
            elif pth.exists():
                pth.unlink()
        except OSError as exc:
            _CLEANUP_ERRORS.append(f"{pth}: {exc}")


def smoke():
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
