#!/usr/bin/env python3
"""R17 — Compose's recursion bound must be HONEST (no phantom 8).

Wave-4 verdict (LIMITS_VERIFICATION_WAVE4_2026-11-15, matrix row
R17): DEFECT-CONFIRMED on the phantom-8 half — _compose_bound
silently yields 8 where bound_detail says "unspecified", the exact
silent default DD-44 abolished and SS12.63a.2 extended family-wide.
Caller census + probe: hidden_files/R17_CENSUS_PROBE_2026-11-18.md
(Uni exec cycle 2026-11-18 05:43 CST) — spectrum_ops._compose_bound
is the SOLE production consumer reaching validate_bound's phantom
branches; the shared validator is NOT touched by this repair.

Three silent-8 faces on the Compose path (probe-verified at base):
  1. unspecified limit -> phantom cap 8: a 12-deep composition
     chain is refused compose_depth by a number nobody stated.
  2. stated "max" -> DOWNGRADED to 8 (bound_detail: specified 64).
  3. invalid stated limit ("100" / "abc") -> silently replaced
     by 8: a shallow chain runs under a fabricated cap, a deep
     chain is refused for a reason that hides the corruption.

Repair contract (DD-44's own pattern, applied to the Compose
domain DD-44 named for a later circuit): the bound is consulted
exactly where it can bite — a nested (depth > 0) expansion of a
non-raw body — and there it resolves through bound_detail:
  - specified -> that exact cap (max = MAX_BOUND = 64);
  - unspecified -> NO cap is applied and no number is invented
    (termination is still guaranteed: the compose_cycle stack
    guard bounds expansion by the finite name set);
  - invalid -> refuse "invalid_limit", never a silent fallback.
A raw seed body ("[" in raw) is terminal — it cannot recurse, so
it is returned before any bound consultation, at any depth.
A flat body never consults the bound. Stated caps stay exact:
depth == cap succeeds, depth == cap + 1 refuses compose_depth.

OPEN QUESTION for the authorities, named in the PR package: the
05:43 census sketch proposed refusal (bound_unspecified) on ANY
nested expansion without a stated Limit. That reading breaks
authority-pinned B18 behavior (step10_consistency: good=good
nested Compose with no Limit stated). This suite pins the
DD-44-faithful reading above; flipping to the strict reading is
a one-line change in _compose_seed plus step10/DD-44 updates
that only an authority ruling should authorize.

Labels: INTEGRATION (direct _compose_seed calls on a real
CoreIIState) + PUBLIC_ENTRY_PATH (execute_seed Compose chains).
No persistent state is touched: CoreIIState is constructed in
memory; Program checks use uuid owners like DD-44's suite.

Run: python3 -m form.r17_compose_bound_test
"""
from __future__ import annotations

import sys
import uuid
from pathlib import Path

REPO = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, REPO)

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}"
          + (f" — {detail}" if detail and not cond else ""))


def _cleanup_state(owner):
    """Remove exactly the canonical state files for this test's
    owner (step10 pattern). Returns a list of errors; a swallowed
    cleanup failure is a defect, so callers surface it as a check."""
    import glob
    import os
    import shutil
    base = os.path.join(REPO, "form", "state")
    errors = []
    if not os.path.isdir(base):
        return errors
    for pat in (f"program_{owner}.json", f"nursery_{owner}.json",
                f"checkpoint_{owner}.json",
                f"confirm_journal_{owner}.json",
                f"confirm_gen_{owner}.json",
                f"confirm_current_{owner}.json",
                f"exchange_journal_{owner}.json"):
        for f in glob.glob(os.path.join(base, pat)):
            try:
                os.remove(f)
            except OSError as e:
                errors.append(f"{f}: {e}")
    d = os.path.join(base, f"ideas_{owner}")
    if os.path.isdir(d):
        try:
            shutil.rmtree(d)
        except OSError as e:
            errors.append(f"{d}: {e}")
    return errors


def _state(limit="", chain=0):
    """A real CoreIIState holding a c1->c2->...->cN->digits chain."""
    from form.mandell.core_ii_exec import CoreIIState
    st = CoreIIState()
    st.limit = limit
    for i in range(1, chain):
        st.compositions[f"c{i}"] = f"c{i + 1}"
    if chain:
        st.compositions[f"c{chain}"] = "70"
    return st


def _seed(st, body, depth=0):
    from form.mandell.spectrum_ops import _compose_seed
    return _compose_seed(st, body, depth=depth)


def main() -> int:
    # ---- controls: behavior that must NOT change ----------------
    out, err = _seed(_state(""), "70>89")
    check("control flat digits, no limit stated", err == "" and "70" in out,
          f"out={out!r} err={err!r}")

    out, err = _seed(_state(""), "70[Count]")
    check("control raw seed, no limit stated", err == "" and out == "70[Count]",
          f"out={out!r} err={err!r}")

    out, err = _seed(_state("", chain=3), "c1")
    check("control shallow nested chain, no limit stated",
          err == "" and "70" in out, f"out={out!r} err={err!r}")

    out, err = _seed(_state("3", chain=3), "c1")
    check("control stated 3 admits depth 3", err == "" and "70" in out,
          f"out={out!r} err={err!r}")

    out, err = _seed(_state("2", chain=3), "c1")
    check("control stated 2 refuses depth 3 as compose_depth",
          err == "compose_depth", f"out={out!r} err={err!r}")

    st = _state("")
    st.compositions["x"] = "x"
    out, err = _seed(st, "x")
    check("control self-reference still compose_cycle",
          err == "compose_cycle", f"out={out!r} err={err!r}")

    # ---- defect face 1: unspecified must not cap at phantom 8 ---
    out, err = _seed(_state("", chain=12), "c1")
    check("unspecified: 12-deep chain is NOT refused by an unstated 8",
          err == "" and "70" in out, f"out={out!r} err={err!r}")

    # ---- defect face 2: stated max must mean 64, not 8 ----------
    out, err = _seed(_state("max", chain=12), "c1")
    check("stated max: 12-deep chain admitted (cap 64, not phantom 8)",
          err == "" and "70" in out, f"out={out!r} err={err!r}")

    out, err = _seed(_state("max", chain=12), "c1", depth=0)
    check("stated max: exactness — depth 12 under cap 64 succeeds",
          err == "", f"err={err!r}")

    # ---- defect face 3: invalid stated limit must refuse --------
    for bad in ("abc", "100"):
        out, err = _seed(_state(bad, chain=3), "c1")
        check(f"invalid limit {bad!r}: nested expansion refuses invalid_limit",
              err == "invalid_limit", f"out={out!r} err={err!r}")

    # ---- raw seed is terminal: no bound consultation ------------
    st = _state("abc")
    st.compositions["deep"] = "70[Count]"
    out, err = _seed(st, "deep", depth=0)
    check("raw inner body returned without consulting an invalid limit",
          err == "" and out == "70[Count]", f"out={out!r} err={err!r}")

    # ---- PUBLIC_ENTRY_PATH: Compose through execute_seed --------
    from form.open import Program
    from form.mandell.core_ii_exec import attach
    from form.mandell.executor import execute_seed

    run = uuid.uuid4().hex[:8]
    owner = f"R17{run}"
    _cleanup_state(owner)
    p = Program(owner=owner)
    attach(p)

    # Deep chain defined in reverse (each define-run expands the
    # chain below it). No Limit is ever stated. The chain base is
    # Dell 70 (Count) alone: it runs clean on empty state, so a
    # define-run failure can only come from the bound machinery.
    r = execute_seed(p, "99[Compose] :: c12=70")
    ok_deep = bool(r.get("ok"))
    for i in range(11, 0, -1):
        r = execute_seed(p, f"99[Compose] :: c{i}=c{i + 1}")
        ok_deep = ok_deep and bool(r.get("ok"))
    check("public path: 12-deep Compose chain, no Limit stated, "
          "defines clean (no phantom 8)", ok_deep, f"last={r}")

    # Invalid stored limit surfaces honestly on a nested Compose.
    p.core_ii.limit = "abc"
    r = execute_seed(p, "99[Compose] :: outer=c12")
    check("public path: invalid stored limit -> Compose invalid_limit",
          (not r.get("ok")) and "invalid_limit" in str(r),
          f"r={r}")

    errs = _cleanup_state(owner)
    check("cleanup of the test owner's state files", not errs,
          f"errors={errs}")

    failed = [n for n, ok in RESULTS if not ok]
    print(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} PASS"
          + (f" — FAILING: {failed}" if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
