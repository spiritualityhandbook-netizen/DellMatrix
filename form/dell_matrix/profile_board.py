#!/usr/bin/env python3
"""C7.Profile board — Dell 49's speedometer (DD-39).

Ace's contract (§12.38a): Profile must SENSE LAG AND PROCESSING
STRAIN and locate the CAUSE — the named operation broken into
its pieces, each piece timed, so the dragging stage is visible.
§14 C7 acceptance: named stages with monotonic timing,
environment/workload identity, overhead disclosed; real
observations vs deliberate benchmarks distinct; repeat
benchmarks use disposable state; probes never silently contact
a provider.

FORM (v1, grounded defaults — Q-C7P.1/.2/.5/.7 as decided for
this slice, each routed in the circuit report):

- BENCHMARK-ONLY (Q-C7P.1 default): every run is a DELIBERATE
  benchmark, kind=BENCHMARK on the receipt. OBSERVED mode —
  instrumenting live pulse/grow/save — is a separate later
  circuit and no number here pretends to be one.
- DISPOSABLE SUBJECT: the benchmark constructs a throwaway
  program (unique temp owner, the p2_perf_baseline isolation
  pattern), builds the declared workload on it, times the
  stages there, and disposes of its state files. The LIVE
  program is never the measured system and is never read —
  status() is not called on this path at all, which removes
  both the old status-echo duplication (Schema owns status,
  DD-29) and the transitive persona_matrix write-on-read from
  Dell 49's path. The persona write itself is NOT repaired
  here; it remains the C7.Schema audit's separate hygiene item.
- STAGES (Q-C7P.4 default): place -> pulse -> growth -> save
  -> load, timed with time.perf_counter() (monotonic). Each
  stage runs in its own try/except and VERIFIES its effect
  (units placed, pulse ok, growth ok, save file present, load
  returns the saved unit count): a stage that raises or fails
  its check reports FAILED with the error class named; the
  board completes; a failed stage is never a timed pass.
- NURSERY UPDATE is a growth SUB-STAGE, named as such in the
  growth stage's note (proposals pending before -> after). No
  standalone nursery operation exists, so none is invented.
- EMBEDDING is ABSENT / OFF-by-design standalone: embedding
  exists only behind a docked Psalm (Dell 47 binding), and the
  benchmark NEVER contacts a provider to fill the row. The row
  carries seconds=None — distinguishable from a measured 0.
- OVERHEAD DISCLOSED (Q-C7P.7 default): harness overhead is
  measured by an empty-workload calibration (construct +
  dispose a disposable program, no stages) run before the
  timed run, and printed as its own line. Stages + overhead +
  unaccounted reconcile to the total BY CONSTRUCTION:
  unaccounted is the remainder, printed, never rounded away.
- LARGEST STAGE NAMED (Q-C7P.5 default): the receipt names the
  largest-share timed stage as an OBSERVATION ("largest:
  <stage> <pct>%"). V1 carries NO normative threshold verdict;
  the needle's threshold is Q-ACE-C7P.1, routed, not invented.
- RECEIPT-ONLY TIMINGS (Q-C7P.2 default (b)): no timings store
  is built in v1; the receipt itself carries the full per-stage
  timings. Kept timings (change over time) are a named
  follow-up circuit. Timings are evidence, never influence:
  nothing here gates, ranks, authorizes, or feeds learning.

The board never raises: a construction-level failure returns a
report with verdict FAILED and the error named.
"""
from __future__ import annotations

import glob
import os
import platform as _platform
import time
from itertools import count as _count
from typing import Any, Callable, Dict, List, Optional

STANDARD_IDEAS = 12
STAGE_ORDER: List[str] = ["place", "pulse", "growth", "save", "load"]

_STATE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "state")
_RUN_COUNTER = _count(1)


# ------------------------------------------------------------------
# Stage operations — each acts on the DISPOSABLE program, returns
# an optional note, and raises on failure (including a failed
# effect check). Timing wraps the call; nothing here reads a
# clock.
# ------------------------------------------------------------------

def _stage_place(prog: Any, ctx: Dict[str, Any]) -> str:
    # A fresh program's plane already carries its seed unit, so
    # the honest effect check is the DELTA: exactly n new units.
    n = ctx["ideas"]
    before = len(prog.cube.session.plane.units)
    for i in range(n):
        prog.place(f"profile_bench_{i}", f"Profile Bench Idea {i}",
                   words=f"benchmark workload seed {i}")
    got = len(prog.cube.session.plane.units) - before
    if got != n:
        raise RuntimeError(f"place built {got} units, expected {n}")
    return f"{n} ideas placed"


def _stage_pulse(prog: Any, ctx: Dict[str, Any]) -> str:
    out = prog.pulse() or {}
    if out.get("ok") is not True:
        raise RuntimeError(
            f"pulse refused: {out.get('reason') or 'no reason given'}")
    return f"resonance ok, session_pulses={out.get('session_pulses')}"


def _stage_growth(prog: Any, ctx: Dict[str, Any]) -> str:
    before = prog.nursery.summary().get("pending")
    out = prog.grow_ideas(1) or {}
    if out.get("ok") is not True:
        raise RuntimeError(
            f"growth refused: {out.get('reason') or 'no reason given'}")
    after = prog.nursery.summary().get("pending")
    ctx["units_at_save"] = len(prog.cube.session.plane.units)
    return (f"nursery update included in growth (sub-stage; "
            f"proposals pending {before} -> {after})")


def _stage_save(prog: Any, ctx: Dict[str, Any]) -> str:
    ctx["units_at_save"] = len(prog.cube.session.plane.units)
    path = prog.save()
    if not path or not os.path.isfile(path):
        raise RuntimeError(f"save produced no file at {path!r}")
    return f"saved {os.path.basename(path)}"


def _stage_load(prog: Any, ctx: Dict[str, Any]) -> str:
    from form.open import Program
    loaded = Program.load(ctx["owner"])
    got = len(loaded.cube.session.plane.units)
    want = ctx.get("units_at_save", ctx["ideas"])
    if got != want:
        raise RuntimeError(f"load returned {got} units, expected {want}")
    return f"loaded {got} units"


# Patchable stage table (tests substitute failures/delays here).
STAGE_FUNCS: Dict[str, Callable[[Any, Dict[str, Any]], str]] = {
    "place": _stage_place,
    "pulse": _stage_pulse,
    "growth": _stage_growth,
    "save": _stage_save,
    "load": _stage_load,
}

EMBEDDING_NOTE = (
    "OFF-by-design — embedding needs a docked Psalm (Dell 47 "
    "binding); the standalone benchmark never contacts a provider")


# ------------------------------------------------------------------
# Disposable lifecycle
# ------------------------------------------------------------------

def _disposable_owner(tag: str = "") -> str:
    return f"ProfileBench{os.getpid()}_{next(_RUN_COUNTER)}{tag}"


def _dispose(owner: str) -> Optional[str]:
    """Remove every state artifact of a disposable owner.
    Returns an error string on failure, None on success; never
    raises (the board must complete) — the failure is disclosed
    on the report instead of being swallowed."""
    import shutil
    try:
        for f in glob.glob(os.path.join(_STATE_DIR, f"*{owner}*")):
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.remove(f)
        return None
    except OSError as e:
        return f"cleanup failed for {owner}: {type(e).__name__}: {e}"


def _calibrate_overhead() -> float:
    """Empty-workload calibration: construct + dispose a
    disposable program, run no stages. This measures the fixed
    harness cost the timed run also pays; it is disclosed on the
    receipt as the overhead line (an estimate — the reconciling
    remainder is reported separately as unaccounted)."""
    from form.open import open_program
    owner = _disposable_owner("CAL")
    t0 = time.perf_counter()
    open_program(owner)
    _dispose(owner)
    return time.perf_counter() - t0


# ------------------------------------------------------------------
# The benchmark
# ------------------------------------------------------------------

def run_profile_benchmark(only_stage: Optional[str] = None) -> Dict[str, Any]:
    """Run the Dell 49 benchmark. ``only_stage`` is None for the
    standard benchmark or one of STAGE_ORDER / 'embedding' for a
    single-stage run. Never raises; never touches the live
    program (it receives no program at all)."""
    from form.open import open_program

    run_no = next(_RUN_COUNTER)
    run_id = f"{os.getpid()}-{run_no}"
    mode = "single" if only_stage else "standard"
    run_stages = [only_stage] if only_stage else list(STAGE_ORDER)
    invalid_stage = bool(only_stage) and only_stage not in STAGE_ORDER \
        and only_stage != "embedding"
    overhead = _calibrate_overhead()

    stages: List[Dict[str, Any]] = []
    setup: List[str] = []
    error: Optional[str] = (
        f"ValueError: unknown stage {only_stage!r}" if invalid_stage
        else None)
    cleanup_error: Optional[str] = None
    owner = _disposable_owner()
    ctx: Dict[str, Any] = {"owner": owner, "ideas": STANDARD_IDEAS}

    t_start = time.perf_counter()
    if invalid_stage:
        pass  # stages stay empty; the error above names the refusal
    elif only_stage == "embedding":
        stages.append({"name": "embedding", "status": "ABSENT",
                       "seconds": None, "share": None,
                       "note": EMBEDDING_NOTE})
    else:
        try:
            prog = open_program(owner)
            placed = False
            saved = False

            def _setup_place():
                nonlocal placed
                STAGE_FUNCS["place"](prog, ctx)
                placed = True
                setup.append("place workload (untimed setup)")

            def _setup_save():
                nonlocal saved
                ctx["units_at_save"] = len(prog.cube.session.plane.units)
                prog.save()
                saved = True
                setup.append("save workload (untimed setup)")

            for name in STAGE_ORDER:
                if name not in run_stages:
                    continue
                if name == "place":
                    pass  # the timed stage IS the construction
                elif not placed:
                    _setup_place()
                if name == "pulse" and not prog.enhance.on:
                    prog.enhance_on()
                    setup.append("enhance gate on (untimed setup)")
                if name == "load" and not saved:
                    _setup_save()
                t0 = time.perf_counter()
                try:
                    note = STAGE_FUNCS[name](prog, ctx)
                    entry = {"name": name, "status": "TIMED",
                             "seconds": time.perf_counter() - t0,
                             "share": None, "note": note or ""}
                except Exception as e:
                    entry = {"name": name, "status": "FAILED",
                             "seconds": time.perf_counter() - t0,
                             "share": None,
                             "note": f"{type(e).__name__}: {e}"[:160]}
                stages.append(entry)
                if name == "place":
                    placed = True
                if name == "save" and entry["status"] == "TIMED":
                    saved = True
            if mode == "standard":
                stages.append({"name": "embedding", "status": "ABSENT",
                               "seconds": None, "share": None,
                               "note": EMBEDDING_NOTE})
        except Exception as e:
            error = f"{type(e).__name__}: {e}"[:200]
        finally:
            cleanup_error = _dispose(owner)
    total = time.perf_counter() - t_start

    timed = [s for s in stages if s["status"] == "TIMED"]
    failed = [s for s in stages if s["status"] == "FAILED"]
    for s in stages:
        if s["status"] in ("TIMED", "FAILED") and total > 0:
            s["share"] = s["seconds"] / total
    stage_seconds = sum(s["seconds"] for s in stages
                        if s["seconds"] is not None)
    unaccounted = total - stage_seconds - overhead
    largest = None
    if timed:
        top = max(timed, key=lambda s: s["seconds"])
        largest = {"name": top["name"], "share": top["share"]}
    if error:
        verdict = "FAILED"
    elif failed:
        verdict = "PARTIAL"
    else:
        verdict = "COMPLETE"

    lines = [f"Profile: {verdict}"]
    if mode == "standard":
        lines.append(
            f"  kind: BENCHMARK · workload: {STANDARD_IDEAS} ideas · "
            f"stages: {', '.join(STAGE_ORDER)}")
    else:
        lines.append(
            f"  kind: BENCHMARK · single stage: {only_stage} · "
            f"workload: {STANDARD_IDEAS} ideas")
    lines.append(
        f"  env: python {_platform.python_version()} · "
        f"{_platform.platform()}")
    for s in stages:
        if s["status"] == "ABSENT":
            lines.append(f"  · {s['name']}: ABSENT — {s['note']}")
        elif s["status"] == "FAILED":
            lines.append(f"  · {s['name']}: FAILED — {s['note']}")
        else:
            line = (f"  · {s['name']}: {s['seconds']:.4f}s "
                    f"({(s['share'] or 0) * 100:.1f}%)")
            if s["note"]:
                line += f" — {s['note']}"
            lines.append(line)
    if error:
        lines.append(f"  error: {error}")
    lines.append(
        f"  overhead: {overhead:.4f}s (harness, empty-workload "
        f"calibration)")
    lines.append(f"  unaccounted: {unaccounted:.4f}s")
    lines.append(f"  total: {total:.4f}s")
    if largest:
        lines.append(
            f"  largest: {largest['name']} "
            f"{(largest['share'] or 0) * 100:.1f}%")
    else:
        lines.append("  largest: none (no stage timed)")
    if cleanup_error:
        lines.append(f"  warning: {cleanup_error}")

    return {
        "dell": 49,
        "kind": "BENCHMARK",
        "verdict": verdict,
        "workload": {
            "mode": mode,
            "ideas": STANDARD_IDEAS,
            "stages": run_stages,
            "setup": setup,
            "run": run_id,
            "owner": owner,
        },
        "environment": {
            "python": _platform.python_version(),
            "platform": _platform.platform(),
        },
        "stages": stages,
        "overhead_seconds": overhead,
        "unaccounted_seconds": unaccounted,
        "total_seconds": total,
        "largest_stage": largest,
        "error": error,
        "cleanup_error": cleanup_error,
        "lines": lines,
    }


def smoke() -> bool:
    print("=== PROFILE BOARD SMOKE ===")
    rep = run_profile_benchmark()
    timed = [s for s in rep["stages"] if s["status"] == "TIMED"]
    ok = (rep["verdict"] == "COMPLETE" and len(timed) == 5
          and rep["kind"] == "BENCHMARK")
    print(f"verdict={rep['verdict']} timed={len(timed)} "
          f"total={rep['total_seconds']:.4f}s")
    print(f"=== {'1/1' if ok else '0/1'} ===")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
