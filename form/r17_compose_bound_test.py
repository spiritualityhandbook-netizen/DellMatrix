#!/usr/bin/env python3
"""R17 — Compose's recursion bound must be HONEST (no phantom 8).

Wave-4 verdict (LIMITS_VERIFICATION_WAVE4_2026-11-15, matrix row
R17): DEFECT-CONFIRMED on the phantom-8 half — _compose_bound
silently yields 8 where bound_detail says "unspecified", the exact
silent default DD-44 abolished and SS12.63a.2 extended family-wide.
Caller census + probe: hidden_files/R17_CENSUS_PROBE_2026-11-18.md
— spectrum_ops._compose_bound is the SOLE production consumer
reaching validate_bound's phantom branches; the shared validator
is NOT touched by this repair.

Bound contract as ruled by the Director (PR #486 GP-E03A + G2
ruling 6978656808 on PR #485, sustaining Uni CH-11):

  - specified bound (incl. the word "max" = MAX_BOUND 64) is
    enforced EXACTLY at every nested expansion: depth == cap
    succeeds, depth == cap + 1 refuses compose_depth;
  - invalid stated bound refuses invalid_limit;
  - UNSPECIFIED bound + a nested NONTERMINAL expansion (a name
    whose body itself references names) REFUSES bound_unspecified
    BEFORE expanding — never a fabricated 8, never the first #485
    head's uncapped recursion (the permissive reading this suite
    originally pinned; superseded by the G2 ruling);
  - flat digit bodies and raw "[...]" terminal seeds never consult
    the bound, at any depth — they cannot recurse; a name resolving
    to a flat-digit body is terminal for the same reason;
  - cycle detection (compose_cycle) precedes expansion, so the
    authority-pinned step10 B18 define-path fixtures (good=good
    with the name pre-seeded on the stack) keep exact behavior;
    the direct self-reference control below is re-pinned under a
    stated bound per the G2 instruction, so the cycle guard itself
    is what is on trial there.

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
    print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if not cond else ""))


def _cleanup_state(owner: str):
    errs = []
    state = Path(__file__).resolve().parent / "state"
    for pat in (f"program_{owner}.json", f"nursery_{owner}.json"):
        try:
            (state / pat).unlink(missing_ok=True)
        except Exception as exc:  # surfaced, never swallowed
            errs.append(f"{pat}: {exc}")
    return errs


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

    out, err = _seed(_state("3", chain=3), "c1")
    check("control stated 3 admits depth 3", err == "" and "70" in out,
          f"out={out!r} err={err!r}")

    out, err = _seed(_state("2", chain=3), "c1")
    check("control stated 2 refuses depth 3 as compose_depth",
          err == "compose_depth", f"out={out!r} err={err!r}")

    # Cycle detection under a STATED bound (re-pinned per G2: the
    # cycle guard, not the bound machinery, is on trial here).
    st = _state("5")
    st.compositions["x"] = "x"
    out, err = _seed(st, "x")
    check("control self-reference under stated bound -> compose_cycle",
          err == "compose_cycle", f"out={out!r} err={err!r}")

    # ---- defect face 1: unspecified must not cap at phantom 8 ---
    out, err = _seed(_state("", chain=12), "c1")
    check("unspecified: 12-deep chain refuses bound_unspecified (not phantom 8, not uncapped)",
          err == "bound_unspecified" and out == "", f"out={out!r} err={err!r}")

    # ---- G2 failing-first: absent limit, nested 3 ----------------
    out, err = _seed(_state("", chain=3), "c1")
    check("unspecified: 3-deep nested chain refuses bound_unspecified",
          err == "bound_unspecified" and out == "", f"out={out!r} err={err!r}")

    # ---- G2: many unique names, absent limit ---------------------
    st = _state("")
    for i in range(1, 40):
        st.compositions[f"u{i}"] = f"u{i + 1}"
    st.compositions["u40"] = "70"
    out, err = _seed(st, "u1")
    check("unspecified: 40 unique-name chain refuses bound_unspecified",
          err == "bound_unspecified" and out == "", f"out={out!r} err={err!r}")

    # ---- cycle precedence: a cycle cannot succeed under ANY ----
    # bound, so compose_cycle is reported before the bound is
    # consulted (preserves spectrum_closure compose_indirect_cycle).
    st = _state("")
    st.compositions["A"] = "B"
    st.compositions["B"] = "A"
    out, err = _seed(st, "A")
    check("indirect cycle, no limit stated -> compose_cycle (not bound_unspecified)",
          err == "compose_cycle", f"out={out!r} err={err!r}")

    st = _state("5")
    st.compositions["A"] = "B"
    st.compositions["B"] = "A"
    out, err = _seed(st, "A")
    check("indirect cycle under stated bound -> compose_cycle",
          err == "compose_cycle", f"out={out!r} err={err!r}")

    # ---- G2 round 2 (6978856860): the cycle pre-scan itself must --
    # be bounded and fail-closed. Long ACYCLIC chains must reach the
    # bound verdicts (compose_depth / bound_unspecified) as TYPED
    # refusals — never a RecursionError out of the pre-scan, never
    # an exponential fan-out walk.
    def _chain_state(limit, n):
        st = _state(limit)
        for i in range(1, n):
            st.compositions[f"a{i}"] = f"a{i + 1}"
        st.compositions[f"a{n}"] = "70"
        return st

    def _guarded(st, body):
        try:
            return _seed(st, body)
        except RecursionError:
            return "", "RECURSION_ERROR"
        except Exception as exc:  # surfaced as a failing verdict
            return "", f"UNCAUGHT:{type(exc).__name__}"

    out, err = _guarded(_chain_state("", 1100), "a1")
    check("1100 unique names, no bound -> bound_unspecified (no RecursionError)",
          err == "bound_unspecified" and out == "", f"err={err!r}")

    out, err = _guarded(_chain_state("3", 1100), "a1")
    check("1100 unique names, cap 3 -> compose_depth (scan prunes at budget)",
          err == "compose_depth" and out == "", f"err={err!r}")

    out, err = _guarded(_chain_state("max", 1100), "a1")
    check("1100 unique names, max -> compose_depth (no RecursionError)",
          err == "compose_depth" and out == "", f"err={err!r}")

    out, err = _guarded(_chain_state("", 66), "a1")
    check("66 unique names, no bound -> bound_unspecified",
          err == "bound_unspecified" and out == "", f"err={err!r}")

    out, err = _guarded(_chain_state("max", 66), "a1")
    check("66 unique names, max -> compose_depth",
          err == "compose_depth" and out == "", f"err={err!r}")

    # Large fan-out: one name naming 60 terminal names under a
    # stated cap succeeds (the fan expansion itself is nested
    # nonterminal, so it lawfully needs the bound); a 12-level
    # binary diamond (4096 naive paths, ~36 distinct names)
    # under max completes — proof the scan is memoized, not
    # path-exponential.
    st = _state("3")
    st.compositions["fan"] = ">".join(f"t{i}" for i in range(60))
    for i in range(60):
        st.compositions[f"t{i}"] = "70"
    out, err = _guarded(st, "fan")
    check("fan-out 60 terminal names, cap 3 -> success",
          err == "" and "70" in out, f"err={err!r}")

    st = _state("max")
    st.compositions["d0"] = "d1a>d1b"
    for lvl in range(1, 12):
        for side in ("a", "b"):
            st.compositions[f"d{lvl}{side}"] = f"d{lvl + 1}a>d{lvl + 1}b"
    st.compositions["d12a"] = "70"
    st.compositions["d12b"] = "89"
    out, err = _guarded(st, "d0")
    check("binary diamond depth 12 under max -> success (memoized scan)",
          err == "" and "70" in out, f"err={err!r}")

    # ---- defect face 2: stated max must mean 64, not 8 ----------
    out, err = _seed(_state("max", chain=12), "c1")
    check("stated max: 12-deep chain admitted (cap 64, not phantom 8)",
          err == "" and "70" in out, f"out={out!r} err={err!r}")

    # ---- G2: 64/65 boundary under max ----------------------------
    out, err = _seed(_state("max", chain=64), "c1")
    check("stated max: 64-deep chain admitted at the cap",
          err == "" and "70" in out, f"out={out!r} err={err!r}")

    out, err = _seed(_state("max", chain=65), "c1")
    check("stated max: 65-deep chain refuses compose_depth past the cap",
          err == "compose_depth" and out == "", f"out={out!r} err={err!r}")

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

    # ---- name resolving to flat digits: terminal, no consult ----
    st = _state("")
    st.compositions["leaf"] = "70>89"
    out, err = _seed(st, "leaf")
    check("name -> flat digits expands without a stated bound",
          err == "" and "70" in out, f"out={out!r} err={err!r}")

    # ---- PUBLIC_ENTRY_PATH: Compose through execute_seed --------
    from form.open import Program
    from form.mandell.core_ii_exec import attach
    from form.mandell.executor import execute_seed

    run = uuid.uuid4().hex[:8]
    owner = f"R17{run}"
    _cleanup_state(owner)
    p = Program(owner=owner)
    attach(p)

    # Absent limit: a TERMINAL define (body = digits) and a one-hop
    # define onto it (body = a name whose body is terminal) are flat
    # operations and succeed; the first define whose expansion must
    # traverse a NONTERMINAL body refuses and stores NOTHING.
    r = execute_seed(p, "99[Compose] :: c12=70")
    base_ok = bool(r.get("ok"))
    r = execute_seed(p, "99[Compose] :: c11=c12")
    hop_ok = bool(r.get("ok")) and p.core_ii.compositions.get("c11") == "c12"
    r = execute_seed(p, "99[Compose] :: c10=c11")
    check("public path: nested define with no Limit refuses bound_unspecified, nothing stored",
          base_ok and hop_ok and (not r.get("ok"))
          and "bound_unspecified" in str(r)
          and "c10" not in p.core_ii.compositions,
          f"r={r} comps={list(p.core_ii.compositions)}")

    # With a Limit stated, the same 12-deep chain defines clean.
    p.core_ii.limit = "max"
    r = execute_seed(p, "99[Compose] :: c12=70")
    ok_deep = bool(r.get("ok"))
    for i in range(11, 0, -1):
        r = execute_seed(p, f"99[Compose] :: c{i}=c{i + 1}")
        ok_deep = ok_deep and bool(r.get("ok"))
    check("public path: 12-deep Compose chain under stated max defines clean",
          ok_deep, f"last={r}")

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
