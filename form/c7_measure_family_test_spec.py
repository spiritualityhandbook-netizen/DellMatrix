#!/usr/bin/env python3
"""Part II / C7 family — Measure family + Profile (rows #149-#151).

Contracts:
- GP-E12 (quantification): Measure returns a typed value —
  quantity, unit, scope, source, timestamp, uncertainty,
  eligibility set and provenance; token counts label the
  tokenizer/model basis; Profile measures elapsed monotonic time
  with environment/workload identity.
- Row #151 (DD-46/47/48): every quantity carries unit, source,
  timestamp, method.
- Row #149 (DD-39): Profile is the speedometer — named stages,
  monotonic timing, environment/workload identity, overhead
  disclosed, real observations vs deliberate benchmarks distinct.
  PR #401 shipped the benchmark speedometer (credit settlement in
  this Part's package); this suite pins what it does and fails
  what the family contract still lacks.
- Row #150 (DD-30): token accounting labels its basis.

Measured at main af2519b6 before this suite was written
(PUBLIC_ENTRY_PATH probes): 71[Measure] last_result =
{value, matched, count, source='measure', predicate, confidence,
trace, unit='count', measure_kind='count'} — unit and source are
carried, but NO timestamp, NO provenance, NO method/scope/
uncertainty/eligibility. 40[TokenCount] reports approx_units with
no tokenizer/model basis label. 49[Profile] prints kind BENCHMARK,
workload, named stages and environment identity (pins).

Labels: PUBLIC_ENTRY_PATH (execute_seed). Hygiene: uuid owners,
exact-pattern cleanup, cleanup errors fail the suite.
"""
from __future__ import annotations

import sys
import uuid
from pathlib import Path

REPO = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, REPO)

RESULTS = []
_CLEANUP_ERRORS = []
RUN = uuid.uuid4().hex[:8]
TAGS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def execute_seed(p, seed):
    from form.mandell.executor import execute_seed as _es
    return _es(p, seed)


def main():
    from form.open import Program
    from form.mandell.core_ii_exec import attach
    TAGS.append("M")
    p = Program(owner=f"C7M{RUN}")
    attach(p)
    execute_seed(p, "55[Set] :: N=5")
    execute_seed(p, "51[Select]")
    r = execute_seed(p, "71[Measure]")
    lr = p.core_ii.last_result or {}
    check("pin.measure_executes", bool(r.get("ok")), f"lr={lr}")
    check("pin.measure_labels_cardinality",
          lr.get("measure_kind") == "count" and lr.get("unit") == "count"
          and lr.get("value") == lr.get("count"),
          f"lr={lr}")
    check("measure.carries_timestamp",
          bool(lr.get("timestamp") or lr.get("measured_at")
               or lr.get("time")),
          f"keys={sorted(lr.keys())}")
    check("measure.carries_provenance_and_method",
          bool(lr.get("provenance") or lr.get("method")
               or lr.get("scope")),
          f"keys={sorted(lr.keys())}")

    r = execute_seed(p, "40[TokenCount] :: hello world token probe")
    blob = " ".join(str(m) for m in (r.get("messages") or [])).lower()
    check("pin.tokencount_executes", bool(r.get("ok")), f"{r.get('messages')}")
    check("tokencount.labels_basis",
          ("tokenizer" in blob or "basis" in blob or "model" in blob
           or "approx" in blob and "basis" in blob),
          f"messages={r.get('messages')}")

    r = execute_seed(p, "49[Profile]")
    blob = " ".join(str(m) for m in (r.get("messages") or []))
    check("pin.profile_benchmark_labeled",
          "BENCHMARK" in blob and "stages:" in blob and "env:" in blob,
          "kind/workload/stages/env disclosed by the #401 speedometer")

    for tag in TAGS:
        _cleanup(tag)
    check("cleanup.clean", not _CLEANUP_ERRORS,
          f"errors={_CLEANUP_ERRORS}")
    ok_n = sum(1 for _, ok in RESULTS if ok)
    print(f"C7_MEASURE_FAMILY {ok_n}/{len(RESULTS)}")
    return 0 if ok_n == len(RESULTS) else 1


def _cleanup(tag):
    from form.persist import _STATE_DIR, _safe_owner
    from form.dell_matrix.nursery import owner_nursery_path
    owner = f"C7{tag}{RUN}"
    state = Path(_STATE_DIR)
    safe = _safe_owner(owner)
    cands = [state / f"program_{safe}.json",
             Path(owner_nursery_path(owner))]
    cands += list(state.glob(f"*{safe}*"))
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
