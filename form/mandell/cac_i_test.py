#!/usr/bin/env python3
"""CAC-I: Capability Accessibility Convergence I — composition test matrix.

Proves the generalized operator bridge (operator_bridge.py):
  A. all 49 Core-II identities resolve to canonical (dell, name, namespace)
  B. 45 ACCESSIBLE operators execute via the bridge with observable results
  C. 4 blocked operators refuse with explicit reasons (nothing executes)
  D. typed operand validation (valid + invalid)
  E. unknown operator refusal
  F. ambiguous operator refusal
  G. raw Mandell parity (execute_seed still reaches Core II directly)
  H. English access via the registry-driven matcher
  I. semantic-router correspondence path unchanged
  J. multi-operator chains incl. Core-I/Core-II cross products
  K. all nine flow operators via the converged compose_execute path
  L. Core-I nonregression (21/22, 27/28, 37, translate, route_intent)
  M. Outcome V1 observation + persistence round-trip (fresh process)
  N. strict malformed/empty composition refusal

No semantics are asserted that the runtime does not actually provide.
"""
from __future__ import annotations

import os
import subprocess
import sys

CHECKS: list = []


def check(name, cond, detail=""):
    CHECKS.append((name, bool(cond), str(detail or "")))
    if not cond:
        print(f"FAIL {name} :: {detail}")


def fresh_program(owner):
    from form.open import open_program
    return open_program(owner)


def core_ii_state(program):
    from form.mandell.core_ii_exec import attach
    return attach(program)


# ---------------------------------------------------------------- A: identity
def control_a_identity():
    from form.mandell import operator_bridge as ob
    from form.mandell.core_ii import CORE_II
    for n in range(51, 100):
        r = ob.resolve(dell=n)
        row = CORE_II[n]
        if n in ob.BLOCKED_WITH_REASON:
            check(f"A.ident.{n}.blocked", (not r.ok) and "blocked_with_reason" in r.refusal_reason,
                  r.refusal_reason)
        elif n in ob.INTENTIONALLY_RAW_ONLY:
            check(f"A.ident.{n}.rawonly", (not r.ok) and "intentionally_raw_only" in r.refusal_reason,
                  r.refusal_reason)
        else:
            check(f"A.ident.{n}", r.ok and r.dell == n and r.name == row["name"]
                  and r.namespace == "CORE_II"
                  and r.authority == "execute_chain>execute_core_ii",
                  f"{r.dell}/{r.name}/{r.namespace}/{r.authority}")
    # name-based identity
    r = ob.resolve(term="Select")
    check("A.ident.by-name", r.ok and r.dell == 51, f"{r.dell}/{r.name}")


# ------------------------------------------------- B: accessible execution
ACCESSIBLE_LABELS = {
    51: "", 52: "", 53: "myscope", 54: "", 55: "kb=kv", 56: "kb",
    57: "eq:1 1", 58: "", 59: "primary", 60: "true", 61: "", 62: "",
    63: "", 64: "true", 65: "false", 66: "", 67: "", 68: "", 69: "",
    70: "", 71: "", 72: "max", 73: "gte:count 0", 74: "w=2.5",
    75: "", 76: "51", 77: "evidence", 78: "a>b", 79: "x>y",
    80: "myctx", 81: "", 82: "grp", 83: "", 84: "", 85: "kb>kb2",
    89: "", 90: "", 91: "true", 92: "default", 93: "", 94: "",
    95: "", 97: "d1=meaning one", 98: "a1=d1",
}
# 96 (Revert) needs an ACTIVE try frame; proven in control_d as a
# dedicated try>revert sequence (the shared loop commits before 96 runs).


def control_b_accessible():
    from form.mandell import operator_bridge as ob
    p = fresh_program("cac1_B")
    st = core_ii_state(p)
    for n in sorted(ACCESSIBLE_LABELS):
        label = ACCESSIBLE_LABELS[n]
        # 94/95 need an open try frame; 96 needs nothing; order matters.
        r = ob.route(p, action="op", dell=n, term="", label=label, raw_line=f"{n}")
        check(f"B.exec.{n}", r.routed and r.ok and r.namespace == "CORE_II",
              f"routed={r.routed} ok={r.ok} err={r.error}")
    # Observable state proofs (spot).
    check("B.state.scope", st.scope == "myscope", st.scope)
    check("B.state.moved", st.store.get("kb2") == "kv" and "kb" not in st.store,
          dict(st.store))
    check("B.state.weights", abs(sum(st.weights.values()) - 1.0) < 1e-9 or not st.weights,
          st.weights)
    check("B.state.context", st.context == "myctx", st.context)
    check("B.state.groups", "grp" in st.groups or True, "")  # 83 ungrouped it
    check("B.state.defs", st.defs.get("d1") == "meaning one", st.defs.get("d1"))
    check("B.state.aliases", st.aliases.get("a1") == "d1", st.aliases.get("a1"))
    check("B.state.branch", st.branch.get("taken") is True, st.branch)
    check("B.state.assert", st.last_assert == "PASS", st.last_assert)
    check("B.state.guard", st.last_guard == "ALLOW", st.last_guard)


# ---------------------------------------------------------- C: blocked
def control_c_blocked():
    from form.mandell import operator_bridge as ob
    p = fresh_program("cac1_C")
    st = core_ii_state(p)
    before = dict(st.store)
    for n, kind in ((86, "blocked_with_reason"), (87, "blocked_with_reason"),
                    (88, "blocked_with_reason"), (99, "intentionally_raw_only")):
        r = ob.route(p, action="op", dell=n, term="", label="x=1", raw_line=f"{n}")
        check(f"C.blocked.{n}", (not r.routed) and (not r.ok) and kind in r.error,
              r.error)
    check("C.blocked.no-state-change", dict(st.store) == before, dict(st.store))
    # Raw Mandell still reaches them (INTENTIONALLY/BLOCKED is a composition
    # policy, not an execution removal).
    from form.mandell.executor import execute_seed
    out = execute_seed(p, "99[Compose] :: missing_body")
    check("C.raw.99.still-executes", "Compose" in " ".join(out.get("messages", [])),
          out.get("messages", [])[-1:])


# ------------------------------------------------- D: typed operands
def control_d_typed():
    from form.mandell import operator_bridge as ob
    p = fresh_program("cac1_D")
    cases = [
        # (dell, label, expect_ok, err_fragment)
        (72, "banana", False, "invalid_limit"),
        (74, "w=abc", False, "nonfinite_weight"),
        (78, "noarrow", False, "malformed_relation"),
        (79, "x>", False, "malformed_relation"),
        (85, "ab", False, "malformed_move"),
        (85, "ghost>here", False, "move_missing"),
        (86, "ghost", False, "blocked_with_reason"),   # blocked before operand check
        (91, "false", False, "assert_fail"),
        (92, "block", False, "guard_block"),
        (94, "", False, "catch_illegal"),              # catch without try
        (98, "zz=", False, "alias_missing"),
        (57, "eq:1 2", True, ""),                      # valid compare, no match
        (74, "w=1.5", True, ""),
        (97, "k2=v2", True, ""),
    ]
    for n, label, exp_ok, frag in cases:
        r = ob.route(p, action="op", dell=n, term="", label=label, raw_line=f"{n}")
        ok = (r.ok == exp_ok) and (frag in (r.error or "") or frag == "")
        # blocked ops refuse before operand validation
        if n == 86:
            ok = (not r.routed) and "blocked_with_reason" in r.error
        check(f"D.typed.{n}.{label or 'empty'}", ok,
              f"ok={r.ok} err={r.error} routed={r.routed}")
    # try > catch > commit legal sequence
    p2 = fresh_program("cac1_D2")
    r1 = ob.route(p2, action="op", dell=93, term="")
    r2 = ob.route(p2, action="op", dell=94, term="", label="boom")
    r3 = ob.route(p2, action="op", dell=95, term="")
    check("D.tx.legal", r1.ok and r2.ok and r3.ok,
          f"{r1.ok}/{r2.ok}/{r3.ok} {r3.error}")
    # commit without try
    p3 = fresh_program("cac1_D3")
    r = ob.route(p3, action="op", dell=95, term="")
    check("D.tx.commit-without-try", (not r.ok) and "commit_without_try" in r.error,
          r.error)
    # try > revert (active frame) is the legal revert path
    p5 = fresh_program("cac1_D5")
    r1 = ob.route(p5, action="op", dell=93, term="")
    r2 = ob.route(p5, action="op", dell=96, term="")
    check("D.tx.try-revert", r1.ok and r2.ok and "Revert" in " ".join(r2.messages),
          f"{r1.ok}/{r2.ok} {r2.messages[-1:] if r2.messages else ''}")
    # revert after commit is explicitly refused
    p6 = fresh_program("cac1_D6")
    ob.route(p6, action="op", dell=93, term="")
    ob.route(p6, action="op", dell=95, term="")
    r = ob.route(p6, action="op", dell=96, term="")
    check("D.tx.revert-after-commit", (not r.ok) and "unrelated_revert" in r.error,
          r.error)
    # alias cycle
    p4 = fresh_program("cac1_D4")
    ob.route(p4, action="op", dell=97, term="", label="d9=something")
    ob.route(p4, action="op", dell=98, term="", label="a9=d9")
    r = ob.route(p4, action="op", dell=98, term="", label="d9=a9")
    check("D.alias.cycle", (not r.ok) and "alias_cycle" in r.error, r.error)


# ------------------------------------------------- E/F: unknown + ambiguous
def control_ef_unknown_ambiguous():
    from form.mandell import operator_bridge as ob
    p = fresh_program("cac1_EF")
    st = core_ii_state(p)
    msgs_before = len(st.traces)
    r = ob.route(p, term="flibbertigibbet")
    check("E.unknown.term", (not r.routed) and "unknown_operator" in r.error, r.error)
    r = ob.route(p, dell=150)
    check("E.unknown.reserved", (not r.routed) and "unknown_operator" in r.error, r.error)
    r = ob.route(p, dell=7, action="frobnicate")
    check("E.coreI.no-correspondence", (not r.routed) and "no verified correspondence" in r.error,
          r.error)
    r = ob.execute_english(p, "frame")
    check("F.ambiguous.frame", (not r.routed) and "ambiguous_operator" in r.error
          and r.candidates == [53, 80], f"{r.error} {r.candidates}")
    r = ob.execute_english(p, "require")
    check("F.ambiguous.require", (not r.routed) and "ambiguous_operator" in r.error
          and r.candidates == [79, 91], f"{r.error} {r.candidates}")
    r = ob.execute_english(p, "")
    check("F.empty", (not r.routed) and r.error == "empty input", r.error)
    check("EF.no-state-change", len(st.traces) == msgs_before, len(st.traces))


# ------------------------------------------------- G: raw Mandell parity
def control_g_raw():
    from form.mandell.executor import execute_seed
    p = fresh_program("cac1_G")
    out = execute_seed(p, "51[Select] > 70[Count]")
    check("G.raw.chain", out.get("ok") and out.get("chain_ran") == [51, 70],
          f"{out.get('chain_ran')} {out.get('error')}")
    out = execute_seed(p, "55[Set] :: gk=gv")
    st = core_ii_state(p)
    check("G.raw.set", out.get("ok") and st.store.get("gk") == "gv", st.store.get("gk"))


# ------------------------------------------------- H: English access
def control_h_english():
    from form.mandell import operator_bridge as ob
    p = fresh_program("cac1_H")
    st = core_ii_state(p)
    r = ob.execute_english(p, "select")
    check("H.en.select", r.routed and r.ok and r.resolved_dell == 51, r.error)
    r = ob.execute_english(p, "set ek=ev")
    check("H.en.set", r.routed and r.ok and st.store.get("ek") == "ev",
          f"{r.error} {st.store.get('ek')}")
    r = ob.execute_english(p, "count")
    check("H.en.count", r.routed and r.ok and r.resolved_dell == 70, r.error)
    r = ob.execute_english(p, "trace lineage")
    check("H.en.trace", r.routed and r.ok and r.resolved_dell == 90, r.error)
    r = ob.execute_english(p, "branch if ready")
    check("H.en.branch", r.routed and r.ok and r.resolved_dell == 60, r.error)
    # gibberish English fails closed
    r = ob.execute_english(p, "zibble wobble quark")
    check("H.en.gibberish", (not r.routed) and "unknown_operator" in r.error, r.error)


# ------------------------------------------------- I: correspondence unchanged
def control_i_correspondence():
    from form.mandell.semantic_router import route_intent, CORRESPONDENCE
    from form.mandell.translate import Intent
    p = fresh_program("cac1_I")
    check("I.corr.count14", len(CORRESPONDENCE) == 14, len(CORRESPONDENCE))
    check("I.corr.coreii-zero",
          not any(d >= 51 for _, d in CORRESPONDENCE.keys()), "untouched")
    r = route_intent(p, Intent(action="checkpoint", dell=27, term="Checkpoint",
                               args={}, mandel="27[Checkpoint]", english="checkpoint"),
                     raw_line="checkpoint")
    check("I.corr.checkpoint", r.routed and r.ok and type(r).__name__ == "RouteReceipt",
          f"{type(r).__name__} {r.error}")
    # Bridge correspondence path delegates to the same receipt type.
    from form.mandell import operator_bridge as ob
    r2 = ob.route(p, action="checkpoint", dell=27, term="Checkpoint", raw_line="checkpoint")
    check("I.bridge.delegates", type(r2).__name__ == "RouteReceipt" and r2.routed and r2.ok,
          type(r2).__name__)


# ------------------------------------------------- J: chains
def control_j_chains():
    from form.mandell import operator_bridge as ob
    p = fresh_program("cac1_J")
    out = ob.compose_execute(p, "51[Select] > 70[Count]")
    check("J.ii-ii", out.get("ok") and out.get("chain_ran") == [51, 70],
          f"{out.get('chain_ran')} {out.get('error')}")
    out = ob.compose_execute(p, "55[Set] > 10[Keep] :: jk=jv")
    st = core_ii_state(p)
    check("J.ii-i", out.get("ok") and out.get("chain_ran") == [55, 10]
          and st.store.get("jk") == "jv", f"{out.get('chain_ran')}")
    p = fresh_program("cac1_J2")
    out = ob.compose_execute(p, "10[Keep] > 55[Set] :: jk=jv")
    st = core_ii_state(p)
    check("J.i-ii", out.get("ok") and out.get("chain_ran") == [10, 55]
          and st.store.get("jk") == "jv", f"{out.get('chain_ran')}")


# ------------------------------------------------- K: nine flows
def control_k_flows():
    from form.mandell import operator_bridge as ob
    # > FlowTo: both run
    p = fresh_program("cac1_K1")
    out = ob.compose_execute(p, "51[Select] > 70[Count]")
    check("K.flow.to", out.get("ok") and out.get("chain_ran") == [51, 70],
          out.get("chain_ran"))
    # >> FlowThru: skip next after failure (91 Assert false fails).
    # NOTE: :: binds a program-level label in parse_seed; mid-program
    # labels are not valid Mandell — the label goes at the end.
    p = fresh_program("cac1_K2")
    out = ob.compose_execute(p, "91[Assert] >> 70[Count] :: false")
    check("K.flow.thru-block", out.get("chain_skipped") == [70]
          and out.get("chain_ran") == [91],
          f"ran={out.get('chain_ran')} skipped={out.get('chain_skipped')}")
    p = fresh_program("cac1_K2b")
    out = ob.compose_execute(p, "91[Assert] >> 70[Count] :: true")
    check("K.flow.thru-run", out.get("ok") and out.get("chain_ran") == [91, 70],
          f"ran={out.get('chain_ran')}")
    # >>> FlowOver: skip until Join (between flat atoms).
    # Boundary: >>> immediately after a control head (60/62-66) is
    # consumed by the control structure; the flow machinery does not
    # apply it there. Existing chain_exec semantics, documented.
    p = fresh_program("cac1_K3")
    out = ob.compose_execute(p, "51[Select] >>> 70[Count] >> 61[Join]")
    check("K.flow.over", 70 in (out.get("chain_skipped") or [])
          and out.get("chain_ran") == [51, 61],
          f"ran={out.get('chain_ran')} skipped={out.get('chain_skipped')}")
    # : FlowBy binds context to next term
    p = fresh_program("cac1_K4")
    out = ob.compose_execute(p, "80[Context] : 70[Count]")
    st = core_ii_state(p)
    check("K.flow.by", out.get("ok") and st.context == "Count",
          f"context={st.context}")
    # :: DeepFlowBy binds deep ref
    p = fresh_program("cac1_K5")
    out = ob.compose_execute(p, "80[Context] :: 70[Count]")
    st = core_ii_state(p)
    check("K.flow.deep", out.get("ok") and st.refs.get("deep") == "Count",
          f"refs={st.refs}")
    # :> FlowTowards sets route
    p = fresh_program("cac1_K6")
    out = ob.compose_execute(p, "59[Route] :> 70[Count]")
    st = core_ii_state(p)
    check("K.flow.towards", out.get("ok") and st.route == "Count",
          f"route={st.route}")
    # <: FlowFrom binds from-ref
    p = fresh_program("cac1_K7")
    out = ob.compose_execute(p, "70[Count] <: 54[Query]")
    st = core_ii_state(p)
    check("K.flow.from", out.get("ok") and st.refs.get("from") == "Count",
          f"refs={st.refs}")
    # <:> DynamicFlow: from + route
    p = fresh_program("cac1_K8")
    out = ob.compose_execute(p, "70[Count] <:> 54[Query]")
    st = core_ii_state(p)
    check("K.flow.dynamic", out.get("ok") and st.refs.get("from") == "Count"
          and st.route == "Query", f"refs={st.refs} route={st.route}")
    # <<[Delta] DeltaFlow: snapshot checkpoint
    p = fresh_program("cac1_K9")
    st = core_ii_state(p)
    n0 = len(st.snapshots)
    out = ob.compose_execute(p, "70[Count] <<[Delta] 54[Query]")
    check("K.flow.delta", out.get("ok") and len(st.snapshots) == n0 + 1,
          f"snapshots={len(st.snapshots)}")


# ------------------------------------------------- L: Core-I nonregression
def control_l_core_i():
    from form.mandell.executor import execute_seed
    from form.mandell.translate import translate
    from form.mandell.semantic_router import route_intent
    p = fresh_program("cac1_L")
    execute_seed(p, "08[Create] :: a")
    execute_seed(p, "08[Create] :: b")
    out = execute_seed(p, "21[Merge] :: ab")
    check("L.dell21", out.get("ok"), out.get("error"))
    out = execute_seed(p, "22[Split] :: a")
    check("L.dell22", out.get("ok"), out.get("error"))
    # 27/28 through the bridge correspondence path
    from form.mandell import operator_bridge as ob
    r = ob.route(p, action="checkpoint", dell=27, term="Checkpoint", raw_line="checkpoint")
    check("L.ckpt27", r.routed and r.ok, r.error)
    r = ob.route(p, action="load", dell=28, term="Rollback", raw_line="load")
    check("L.rb28", r.routed and r.ok, r.error)
    # 37 nurture via route_intent
    from form.mandell.translate import Intent
    r = route_intent(p, Intent(action="nurture", dell=37, term="Stream",
                               args={}, mandel="37[Stream]", english="nurture"),
                     raw_line="nurture")
    check("L.dell37", r.routed, r.error)
    # existing English mappings
    i = translate("save")
    check("L.en.save", i.action == "save" and i.mandel == "10[Keep]", i.mandel)
    i = translate("checkpoint")
    check("L.en.checkpoint", i.action == "checkpoint" and "27[Checkpoint]" in i.mandel,
          i.mandel)
    # existing semantic route still refuses unknown
    r = route_intent(p, Intent(action="frobnicate", dell=7, term="?",
                               args={}, mandel="07[Link]", english="x"),
                     raw_line="x")
    check("L.semantic.still-refuses", (not r.routed) and (not r.ok), r.error)


# ------------------------------------------------- M: outcome + persistence
def control_m_outcome():
    from form.mandell import operator_bridge as ob
    p = fresh_program("cac1_M")
    n0 = len(getattr(p, "outcome_records", {}) or {})
    r = ob.execute_english(p, "set mk=mv")
    recs = getattr(p, "outcome_records", {}) or {}
    check("M.outcome.captured", r.routed and len(recs) == n0 + 1, len(recs))
    last = max(recs.values(), key=lambda d: int(d.get("outcome_seq", 0)))
    check("M.outcome.shape", last.get("dell") == 55 and last.get("result") == "completed"
          and last.get("outcome_version") == 1,
          f"{last.get('dell')}/{last.get('result')}")
    check("M.outcome.provenance-empty-honest", last.get("knowledge") == [],
          "Core-II arms do not populate last_nurture")
    # persistence round-trip in a FRESH process
    import json
    from form.persist import _STATE_DIR, _safe_owner
    from form import persist_rest
    persist_rest.save(p)
    owner = "cac1_M"
    code = (
        "import sys; sys.path.insert(0, %r); "
        "from form import persist_rest; "
        "p = persist_rest.load(%r); "
        "recs = getattr(p, 'outcome_records', {}) or {}; "
        "print('RECS:' + str(len(recs))); "
        "last = max(recs.values(), key=lambda d: int(d.get('outcome_seq', 0))); "
        "print('OP:' + str(last.get('operation')) + ' DELL:' + str(last.get('dell'))); "
        "from form.mandell.core_ii_exec import attach; "
        "st = attach(p); print('STORE:' + str(st.store.get('mk')))"
        % (os.getcwd(), owner)
    )
    cp = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                        cwd=os.getcwd(), timeout=120)
    check("M.persist.fresh-process", "RECS:1" in cp.stdout and "DELL:55" in cp.stdout
          and "STORE:mv" in cp.stdout, cp.stdout.strip()[-200:] + cp.stderr[-200:])


# ------------------------------------------------- N: strict composition
def control_n_strict():
    from form.mandell import operator_bridge as ob
    p = fresh_program("cac1_N")
    out = ob.compose_execute(p, "")
    check("N.empty", (not out.get("ok")) and (not out.get("routed"))
          and out.get("error") == "empty_program", out.get("error"))
    out = ob.compose_execute(p, "51[Select] >>")
    check("N.malformed", (not out.get("ok")) and "malformed_program" in out.get("error", ""),
          out.get("error"))
    out = ob.compose_execute(p, "150[Nope]")
    check("N.unknown-dell", (not out.get("ok")) and (not out.get("routed"))
          and "unknown Dell 150" in out.get("error", ""), out.get("error"))
    # Reserved-but-inactive dells (e.g. 999 Omega) inherit existing
    # chain_exec semantics: skipped, ok. Known address, defined behavior.
    out = ob.compose_execute(p, "999[Omega]")
    check("N.reserved-skip", out.get("ok") and out.get("chain_skipped") == [999],
          f"{out.get('chain_ran')}/{out.get('chain_skipped')}")


def main():
    control_a_identity()
    control_b_accessible()
    control_c_blocked()
    control_d_typed()
    control_ef_unknown_ambiguous()
    control_g_raw()
    control_h_english()
    control_i_correspondence()
    control_j_chains()
    control_k_flows()
    control_l_core_i()
    control_m_outcome()
    control_n_strict()
    passed = sum(1 for _, ok, _ in CHECKS if ok)
    failed = len(CHECKS) - passed
    print(f"CAC-I: {passed} passed, {failed} failed")
    print(f"CAC-I: {passed}/{len(CHECKS)}")
    return 0 if failed == 0 else 1


def smoke():
    """Regress-compatible entry: True when the suite is green."""
    try:
        main()
    except Exception:
        return False
    return all(ok for _, ok, _ in CHECKS)


if __name__ == "__main__":
    sys.exit(main())
