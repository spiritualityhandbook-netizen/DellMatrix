#!/usr/bin/env python3
"""CORE-I-UNSUPPORTED-ARG-GATE — fail-closed gate for typed args on
unregistered Core I Dells (Director MODE C repair, Core I contract
ruling on PR #256, 2026-11-03).

Defect (investigation PR #256, census re-verified from scratch):
50 of 51 Core I Dells parse typed arguments and silently ignore
them on every surface (single-atom leaf, core_i_ops intercept,
live_identity, chain re-entry). Dell 8 is the sole registered
exception. Crispest exhibit: 06[Cycle](cycles="3") runs x1 while
06[Cycle] :: 3 runs x3 — same shape, different count, no signal.

Repair (this circuit): a per-EXECUTING-atom gate at the canonical
funnel, executor.execute_seed. When the parsed seed is a single
Core I atom (Dell 0-50) with nonempty args and NO registered
signature, execution refuses BEFORE any dispatch (intercept,
live_identity, or leaf) with error
'UNSUPPORTED_ARGS: <sorted role names>'. Multi-atom seeds are
never judged at the funnel: chain_exec re-enters execute_seed
(_leaf=True) per Core I atom with that atom's own args, so each
atom is judged on its own args at its own execution — the
Director's per-atom correction. A mixed chain such as
03[Logic] > 55[Set](key="tempo", value="120") executes fully;
the Set is never refused for another atom's sake.

Diagnostics name sorted role NAMES only; raw values are never
echoed by the refusal (Q-C2: the preexisting universal seed echo
still reproduces the caller's own input; the canary scope is the
refusal's own diagnostics — error, receipts, appended messages).

Labels: seed execution PUBLIC_ENTRY_PATH (execute_seed on a real
Program); the REPL section is a literal subprocess session
(REAL_USER_PATH). Setup places units directly.
"""
from __future__ import annotations

import glob
import json
import os
import shutil
import subprocess
import sys

RESULTS = []

STATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "state")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Census pin (PR #256). The sweep ITERATES the set derived live
# from the registry + signature source and asserts it equals
# this pin — a future registration fails the count loud.
EXPECTED_UNTYPED_50 = [n for n in range(51) if n != 8]
EXPECTED_TYPED_17 = [8, 51, 52, 53, 54, 55, 56, 57, 58, 67,
                     68, 69, 84, 85, 86, 87, 88]
EXPECTED_HANDLED = {27, 28, 34, 35, 37, 40, 44, 47}

CANARY = "CANARYZZ_9f3e_UNIQ"


def _rec(name, cond, detail=""):
    RESULTS.append((name, bool(cond), str(detail)))


def _cleanup(owner):
    # Loud cleanup (standing law): exact owner scope only.
    for f in glob.glob(os.path.join(STATE_DIR, f"*{owner}*")):
        try:
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.remove(f)
        except FileNotFoundError:
            pass


def _fresh(owner):
    _cleanup(owner)
    from form.open import Program
    p = Program(owner)
    units = set(p.cube.session.plane.units)
    assert units == {"welcome"}, \
        f"owner {owner} unexpected start state: {sorted(units)}"
    return p


def _st(p):
    from form.mandell.core_ii_exec import attach
    return attach(p)


def _snap(p):
    s = _st(p)
    return {
        "store": dict(s.store or {}),
        "groups": {k: list(v) for k, v in (s.groups or {}).items()},
        "selected": list(s.selected or []),
        "scope": s.scope,
        "defs": dict(s.defs or {}),
        "aliases": dict(s.aliases or {}),
        "compositions": dict(s.compositions or {}),
        "last_result": dict(s.last_result or {}),
        "units": sorted(p.cube.session.plane.units),
        "control_steps": s.control_steps,
    }


def _receipts(r):
    return r.get("atom_results") or []


def _by_dell(r, n):
    return [a for a in _receipts(r) if a.get("dell") == n]


def _term(n):
    from form.mandell.registry import DELLS
    return DELLS[n]["name"]


def _scope():
    from form.mandell.registry import DELLS
    from form.mandell.signatures import has_signature
    untyped = sorted(n for n in DELLS
                     if 0 <= n <= 50 and not has_signature(n))
    typed = sorted(n for n in DELLS if has_signature(n))
    _rec("scope: untyped Core I set derived live == census pin (50)",
         untyped == EXPECTED_UNTYPED_50, f"derived={untyped}")
    _rec("scope: typed-signature count stays 17 (no new signatures)",
         typed == EXPECTED_TYPED_17, f"typed={typed}")
    from form.mandell.core_i_ops import HANDLED
    _rec("scope: intercept HANDLED set re-verified from code",
         set(HANDLED) == EXPECTED_HANDLED, f"HANDLED={sorted(HANDLED)}")


def _sweep_untyped():
    from form.mandell.executor import execute_seed
    owner = "CoreIGateSweep"
    for n in EXPECTED_UNTYPED_50:
        p = _fresh(owner)
        before = _snap(p)
        r = execute_seed(p, f'{n:02d}[{_term(n)}](probe="v")')
        _rec(f"sweep {n:02d}[{_term(n)}]: single-atom typed args "
             f"refuse UNSUPPORTED_ARGS, zero mutation",
             r.get("ok") is False
             and str(r.get("error")) == "UNSUPPORTED_ARGS: probe"
             and _snap(p) == before,
             f"ok={r.get('ok')} err={r.get('error')} "
             f"mutated={_snap(p) != before}")
    _cleanup(owner)


def _chain_parity():
    from form.mandell.executor import execute_seed
    owner = "CoreIGateParity"
    # One leaf-arm Dell (43), one intercept Dell (37), one
    # live-identity Dell (21), one plain Dell (5): the chained
    # receipt's error must equal the single-atom refusal exactly,
    # and the FlowTo partner still executes (per-atom refusal,
    # chain continues).
    for n in (43, 37, 21, 5):
        p = _fresh(owner)
        r1 = execute_seed(p, f'{n:02d}[{_term(n)}](probe="v")')
        p = _fresh(owner)
        r2 = execute_seed(p, f'{n:02d}[{_term(n)}](probe="v") > 70[Count]')
        mine = _by_dell(r2, n)
        partner = _by_dell(r2, 70)
        _rec(f"parity {n:02d}[{_term(n)}]: chain receipt refusal == "
             f"single refusal; FlowTo partner executes",
             r1.get("ok") is False
             and str(r1.get("error")) == "UNSUPPORTED_ARGS: probe"
             and len(mine) == 1
             and mine[0].get("ok") is False
             and mine[0].get("error") == "UNSUPPORTED_ARGS: probe"
             and len(partner) == 1 and partner[0].get("ok") is True,
             f"single_err={r1.get('error')} mine={mine} "
             f"partner={partner}")
    _cleanup(owner)


def _mixed_chains():
    from form.mandell.executor import execute_seed
    owner = "CoreIGateMixed"
    # The Director's adversarial example, verbatim: a Core I atom
    # followed by a valid typed Core II atom executes FULLY.
    p = _fresh(owner)
    r = execute_seed(p, '03[Logic] > 55[Set](key="tempo", value="120")')
    _rec("mixed (Director's example): 03[Logic] > 55[Set](typed) "
         "executes fully, Set NOT refused, effect stands",
         r.get("ok") is True
         and _st(p).store.get("tempo") == "120"
         and "UNSUPPORTED_ARGS" not in json.dumps(r, default=str),
         f"ok={r.get('ok')} err={r.get('error')} "
         f"store={_st(p).store}")
    # Typed Core II first, Core I with args second: the Core II
    # atom's effect stands; the Core I atom refuses on its OWN args.
    p = _fresh(owner)
    r = execute_seed(p, '55[Set](key="a", value="1") > '
                        '05[Tone](expression="calm")')
    tone = _by_dell(r, 5)
    _rec("mixed reversed: Set effect stands, Tone refuses per-atom",
         _st(p).store.get("a") == "1"
         and len(tone) == 1 and tone[0].get("ok") is False
         and tone[0].get("error") == "UNSUPPORTED_ARGS: expression",
         f"store={_st(p).store} tone={tone}")
    # Core I with args BETWEEN two valid Core II atoms: first
    # stands, middle refuses, last still executes (FlowTo).
    p = _fresh(owner)
    r = execute_seed(p, '55[Set](key="a", value="1") > '
                        '43[Fallback](note="hi") > '
                        '55[Set](key="b", value="2")')
    mid = _by_dell(r, 43)
    _rec("mixed sandwich: Core I refusal is per-atom; both Core II "
         "effects stand",
         _st(p).store.get("a") == "1" and _st(p).store.get("b") == "2"
         and len(mid) == 1 and mid[0].get("ok") is False
         and mid[0].get("error") == "UNSUPPORTED_ARGS: note",
         f"store={_st(p).store} mid={mid}")
    _cleanup(owner)


def _intercept():
    from form.mandell.executor import execute_seed
    owner = "CoreIGateIce"
    for n in sorted(EXPECTED_HANDLED):
        p = _fresh(owner)
        before = _snap(p)
        r = execute_seed(p, f'{n:02d}[{_term(n)}](probe="v")')
        _rec(f"intercept {n:02d}[{_term(n)}]: typed args refuse at "
             f"the funnel, before apply_core_i, zero mutation",
             r.get("ok") is False
             and str(r.get("error")) == "UNSUPPORTED_ARGS: probe"
             and _snap(p) == before,
             f"ok={r.get('ok')} err={r.get('error')}")
    _cleanup(owner)


def _live_identity():
    from form.mandell.executor import execute_seed
    owner = "CoreIGateLive"
    for n in (21, 22):
        p = _fresh(owner)
        before = _snap(p)
        r = execute_seed(p, f'{n:02d}[{_term(n)}](probe="v")')
        _rec(f"live {n:02d}[{_term(n)}]: typed args refuse before "
             f"merge/split runs, zero mutation",
             r.get("ok") is False
             and str(r.get("error")) == "UNSUPPORTED_ARGS: probe"
             and _snap(p) == before,
             f"ok={r.get('ok')} err={r.get('error')}")
    # Label-only behavior preserved exactly as on base:
    # Split on a placed unit creates its two parts.
    p = _fresh(owner)
    p.place("alpha_one", "Alpha One")
    r = execute_seed(p, "22[Split] :: alpha_one")
    units = set(p.cube.session.plane.units)
    _rec("live label-only preserved: 22[Split] :: alpha_one splits",
         r.get("ok") is True
         and {"alpha_one_a", "alpha_one_b"} <= units,
         f"ok={r.get('ok')} units={sorted(units)}")
    # Merge label-only outcome identical to base (missing_source
    # on an unselected label) — the gate does not touch it.
    p = _fresh(owner)
    p.place("alpha_one", "Alpha One")
    r = execute_seed(p, "21[Merge] :: alpha_one")
    _rec("live label-only preserved: 21[Merge] :: alpha_one outcome "
         "unchanged (missing_source, as on base)",
         r.get("ok") is False and r.get("error") == "missing_source",
         f"ok={r.get('ok')} err={r.get('error')}")
    _cleanup(owner)


def _dell8():
    from form.mandell.executor import execute_seed
    owner = "CoreIGateD8"

    def _units(p):
        return set(p.cube.session.plane.units)

    p = _fresh(owner)
    r = execute_seed(p, '08[Create](name="Solo Wish", skin="SPHERE")')
    _rec("dell8 valid single: registered contract preserved",
         r.get("ok") is True and "solo_wish" in _units(p),
         f"ok={r.get('ok')} err={r.get('error')}")
    p = _fresh(owner)
    r = execute_seed(p, '08[Create](name="Chain Wish", skin="SEED") '
                        '> 70[Count]')
    _rec("dell8 valid chain: registered contract preserved",
         r.get("ok") is True and "chain_wish" in _units(p),
         f"ok={r.get('ok')} err={r.get('error')}")
    p = _fresh(owner)
    r = execute_seed(p, '08[Create](name="Bad Wish", skin="TRIANGLE")')
    _rec("dell8 invalid value: INVALID_VALUE (not UNSUPPORTED_ARGS)",
         r.get("ok") is False
         and "INVALID_VALUE" in str(r.get("error"))
         and "UNSUPPORTED_ARGS" not in str(r.get("error"))
         and "bad_wish" not in _units(p),
         f"err={r.get('error')}")
    p = _fresh(owner)
    r = execute_seed(p, '08[Create](name="X", bogus="1")')
    _rec("dell8 unknown role: UNKNOWN_ROLE (not UNSUPPORTED_ARGS)",
         r.get("ok") is False
         and "UNKNOWN_ROLE" in str(r.get("error")),
         f"err={r.get('error')}")
    p = _fresh(owner)
    r = execute_seed(p, '08[Create](name="Named Wish") :: other_label')
    _rec("dell8 conflict: ARGUMENT_CONFLICT preserved",
         r.get("ok") is False
         and str(r.get("error")) == "ARGUMENT_CONFLICT",
         f"err={r.get('error')}")
    _cleanup(owner)


def _legacy():
    from form.mandell.executor import execute_seed
    owner = "CoreIGateLegacy"
    p = _fresh(owner)
    r = execute_seed(p, "06[Cycle] :: 3")
    _rec("legacy: 06[Cycle] :: 3 still runs x3 (label count path)",
         r.get("ok") is True
         and any("Cycle x3" in str(m) for m in r.get("messages", [])),
         f"msgs={r.get('messages')}")
    p = _fresh(owner)
    r = execute_seed(p, "06[Cycle]")
    _rec("legacy: bare 06[Cycle] still runs x1",
         r.get("ok") is True
         and any("Cycle x1" in str(m) for m in r.get("messages", [])),
         f"msgs={r.get('messages')}")
    p = _fresh(owner)
    r = execute_seed(p, "05[Tone] :: joy")
    _rec("legacy: 05[Tone] :: joy executes (label is not args)",
         r.get("ok") is True
         and any("tone=joy" in str(m) for m in r.get("messages", [])),
         f"ok={r.get('ok')} msgs={r.get('messages')}")
    p = _fresh(owner)
    r = execute_seed(p, '05[Tone] :: (expression="calm")')
    _rec("legacy: arg-shaped text inside a LABEL stays a label "
         "(args=={} — the gate is inert)",
         r.get("ok") is True
         and "UNSUPPORTED_ARGS" not in json.dumps(r, default=str),
         f"ok={r.get('ok')} err={r.get('error')}")
    _cleanup(owner)


def _flow_and_skips():
    from form.mandell.executor import execute_seed
    owner = "CoreIGateFlow"
    # Q4 fence: a Core I atom with args behind a FlowThru block
    # never executes — its receipt stays the flow skip; the args
    # are never inspected.
    p = _fresh(owner)
    r = execute_seed(p, '82[Group](bogus="x") >> '
                        '05[Tone](expression="calm")')
    tone = _by_dell(r, 5)
    _rec("flowthru fence: blocked Core I atom keeps flow_thru_block "
         "skip, NOT an UNSUPPORTED_ARGS refusal",
         len(tone) == 1 and tone[0].get("skipped") is True
         and tone[0].get("error") == "flow_thru_block",
         f"tone={tone}")
    # Reserved atoms: args never inspected, behavior unchanged.
    p = _fresh(owner)
    r = execute_seed(p, '151[Harmonic](bogus="x")')
    _rec("reserved: 151 single-seed behavior unchanged",
         r.get("ok") is False
         and str(r.get("error")) ==
         "Dell 151 not executable via single-seed leaf",
         f"ok={r.get('ok')} err={r.get('error')}")
    p = _fresh(owner)
    r = execute_seed(p, '55[Set](key="a", value="1") > '
                        '151[Harmonic](bogus="x")')
    harm = _by_dell(r, 151)
    _rec("reserved: 151 in chain stays a Decision-1 skip receipt",
         len(harm) == 1 and harm[0].get("skipped") is True
         and harm[0].get("error") == "reserved/not-active",
         f"harm={harm}")
    _cleanup(owner)


def _manifest_set():
    from form.mandell.executor import execute_seed
    owner = "CoreIGateMani"
    # ManifestSet (seed expansion, separator •): the prototype's
    # args ride EVERY member atom (chainlink origin). Each member
    # is judged on its own at its own re-entry.
    p = _fresh(owner)
    before = _snap(p)
    r = execute_seed(p, '43[A • B](note="hi")')
    recs = _by_dell(r, 43)
    _rec("manifestset: EVERY member refuses per-atom "
         "(UNSUPPORTED_ARGS), zero mutation",
         len(recs) == 2
         and all(a.get("ok") is False
                 and a.get("error") == "UNSUPPORTED_ARGS: note"
                 for a in recs)
         and _snap(p) == before,
         f"recs={recs}")
    p = _fresh(owner)
    r = execute_seed(p, "43[A • B]")
    recs = _by_dell(r, 43)
    _rec("manifestset legacy: arg-free members execute as on base",
         len(recs) == 2 and all(a.get("ok") is True for a in recs),
         f"recs={recs}")
    _cleanup(owner)


def _diagnostics_blob(r):
    """Every diagnostic surface the REFUSAL generates: the
    top-level error, all atom receipts, and all appended messages
    EXCEPT the universal seed-echo header lines (the caller's own
    input text — Q-C2 boundary, as certified for Core II)."""
    msgs = [str(m) for m in (r.get("messages") or [])
            if not str(m).startswith(("Mandell:", "English:"))]
    return json.dumps({"error": r.get("error"),
                       "atom_results": _receipts(r),
                       "messages": msgs}, default=str)


def _canary():
    from form.mandell.executor import execute_seed
    owner = "CoreIGateCan"
    cases = [
        ("leaf 05[Tone]", '05[Tone](expression="%s")' % CANARY,
         "UNSUPPORTED_ARGS: expression"),
        ("intercept 37[Nurture]", '37[Nurture](label="%s")' % CANARY,
         "UNSUPPORTED_ARGS: label"),
        ("sanitize 41[Sanitize]", '41[Sanitize](secret="%s")' % CANARY,
         "UNSUPPORTED_ARGS: secret"),
    ]
    for name, seed, want_err in cases:
        p = _fresh(owner)
        r = execute_seed(p, seed)
        blob = _diagnostics_blob(r)
        gate_lines = [str(m) for m in (r.get("messages") or [])
                      if "no registered typed signature" in str(m)]
        _rec(f"canary {name}: refusal names the role, NEVER the "
             f"raw value",
             str(r.get("error")) == want_err
             and CANARY not in blob
             and len(gate_lines) == 1 and CANARY not in gate_lines[0],
             f"err={r.get('error')} blob_has_canary={CANARY in blob} "
             f"gate_lines={gate_lines}")
    _cleanup(owner)


def _repl():
    owner = "CoreIGateRepl"
    _cleanup(owner)
    lines = [
        '05[Tone](expression="calm") :: joy',
        '06[Cycle](cycles="3")',
        "06[Cycle] :: 3",
        '08[Create](name="Repl Wish", skin="SPHERE")',
        '03[Logic] > 55[Set](key="tempo", value="120")',
    ]
    proc = subprocess.run(
        [sys.executable, "-m", "form.repl", "--owner", owner],
        input="\n".join(lines) + "\n", capture_output=True, text=True,
        cwd=ROOT, timeout=300)
    out = proc.stdout + proc.stderr
    _rec("repl: Core I typed args refuse visibly (REAL_USER_PATH) "
         "— the printed TOAM refusal lines for 05 and 06",
         "Dell 05[Tone] has no registered typed signature; typed "
         "arguments refused before execution (roles: expression)"
         in out
         and "Dell 06[Cycle] has no registered typed signature; "
         "typed arguments refused before execution (roles: cycles)"
         in out,
         out[-800:])
    _rec("repl: 06[Cycle] :: 3 still runs x3 in the same session",
         "Cycle x3" in out, out[-800:])
    _rec("repl: Dell 8 typed Create still works in the same session",
         'Created idea: "Repl Wish"' in out, out[-800:])
    _cleanup(owner)


def main():
    _scope()
    _sweep_untyped()
    _chain_parity()
    _mixed_chains()
    _intercept()
    _live_identity()
    _dell8()
    _legacy()
    _flow_and_skips()
    _manifest_set()
    _canary()
    _repl()
    total = len(RESULTS)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        if not ok:
            print(f"FAIL {name} :: {detail}")
    print(f"CORE_I_ARG_GATE: {passed}/{total}")
    return passed == total


def smoke():
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
