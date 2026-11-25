#!/usr/bin/env python3
"""G31-CONTRACT-02 regression suite: two execution profiles, one vocabulary.

Implements the acceptance baseline of G31-CONTRACT-01 (Director CONFIRMED
design, 2026-11-14): T-1..T-6 including T-5a/b/c, the D-6 refusal-
visibility contract, and the FLOW_PROFILES annotation on the single
FLOW_CONTRACT vocabulary authority.

Profiles:
  A canonical_chain            — all nine operators (chain_exec /
                                 compose_execute / REPL raw-seed dispatch)
  B correspondence_composition — ">" and ">>" only; the other seven are
                                 refused at parse, observably (D-6).

Run: python3 -m form.mandell.g31_contract_test
"""

from __future__ import annotations

import glob
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from form import persist_rest  # noqa: E402
from form.mandell.core_ii_exec import attach  # noqa: E402

RESULTS = []

NINE = [">", ">>", ">>>", ":", "::", ":>", "<:", "<:>", "<<[Delta]"]
SEVEN_REFUSED = [">>>", ":", "::", ":>", "<:", "<:>", "<<[Delta]"]
ORIGINAL_CONTRACT = {
    ">": "FlowTo", ">>": "FlowThru", ">>>": "FlowOver", ":": "FlowBy",
    "::": "DeepFlowBy", ":>": "FlowTowards", "<:": "FlowFrom",
    "<:>": "DynamicFlow", "<<[Delta]": "DeltaFlow",
}


def _rec(name, cond, detail=""):
    RESULTS.append((name, bool(cond), str(detail)[:220]))


def _cleanup(owner):
    base = os.path.join(os.path.dirname(__file__), "..", "state")
    for pat in (f"program_{owner}.json", f"nursery_{owner}.json",
                f"checkpoint_{owner}_*", f"confirm_{owner}.journal.json",
                f"checkpoint_{owner}.journal.json"):
        for f in glob.glob(os.path.join(base, pat)):
            os.remove(f)
    for d in glob.glob(os.path.join(base, f"ideas_{owner}*")):
        if os.path.isdir(d):
            shutil.rmtree(d)


def _repl(owner, lines, load=False):
    root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", ".."))
    args = [sys.executable, "-m", "form.repl", "--owner", owner]
    if load:
        args.append("--load")
    return subprocess.run(args, input="\n".join(lines) + "\n",
                          capture_output=True, text=True, cwd=root,
                          timeout=300)


def _state(owner):
    p = persist_rest.load(owner, activate=False)
    return attach(p)


def smoke() -> bool:
    owners = [f"G31C{i}" for i in range(8)]
    for o in owners:
        _cleanup(o)
    try:
        # --- Vocabulary authority + profile annotation ---------------
        from form.mandell import control_runtime
        from form.mandell.control_runtime import FLOW_CONTRACT
        from form.mandell import flow_executor
        # Tolerant pre-implementation reads: a missing annotation must
        # FAIL its cases, not abort the suite (failing-first evidence).
        FLOW_PROFILES = getattr(control_runtime, "FLOW_PROFILES", {})

        _rec("vocabulary_unchanged", FLOW_CONTRACT == ORIGINAL_CONTRACT,
             str(FLOW_CONTRACT))
        _pB = FLOW_PROFILES.get("correspondence_composition", {})
        _rec("profiles_two", set(FLOW_PROFILES) ==
             {"canonical_chain", "correspondence_composition"},
             str(sorted(FLOW_PROFILES)))
        _rec("profile_a_is_the_nine",
             set(FLOW_PROFILES.get("canonical_chain", {})
                 .get("operators", [])) == set(NINE))
        _rec("profile_b_is_two",
             set(_pB.get("operators", [])) == {">", ">>"})
        _rec("profile_b_refused_is_seven",
             set(_pB.get("refused", {})) == set(SEVEN_REFUSED))
        _rec("profile_b_refusals_mirror_s3",
             all(_pB.get("refused", {}).get(op) ==
                 flow_executor.FLOW_CLASSIFICATION[op]
                 for op in SEVEN_REFUSED))
        _rec("s3_classification_unchanged",
             flow_executor.EXECUTABLE_FLOWS == {">", ">>"} and
             all(flow_executor.FLOW_CLASSIFICATION[op] ==
                 _pB.get("refused", {}).get(op)
                 for op in SEVEN_REFUSED))

        # --- D-6 unit leg: refusal is a distinguishable type ---------
        FlowRefusal = getattr(flow_executor, "FlowRefusal", None)
        try:
            flow_executor.parse_program("70[Count] >>> 51[Select]")
            _rec("refusal_type_distinguishable", False, "no raise")
        except ValueError as e:
            _rec("refusal_type_distinguishable",
                 FlowRefusal is not None
                 and isinstance(e, FlowRefusal)
                 and ">>>" in str(e)
                 and "REQUIRES_RUNTIME_SUPPORT" in str(e), str(e))
        try:
            flow_executor.parse_program("word 70[Count] >>> 51[Select]")
            _rec("parse_miss_is_not_refusal", False, "no raise")
        except ValueError as e:
            _rec("parse_miss_is_not_refusal",
                 FlowRefusal is None or not isinstance(e, FlowRefusal),
                 str(e))

        # --- T-1: seed line dispatches to Profile A ------------------
        r = _repl(owners[0], ["51[Select] >>> 70[Count] >> 61[Join]",
                              "quit"])
        _rec("t1_seed_goes_canonical",
             r.returncode == 0 and "skipped by FlowOver" in r.stdout
             and "Flow refused" not in r.stdout)

        # --- T-2: Profile B refusal is observable, executes nowhere --
        # 150[Future] is not a registered Dell, so the raw-seed branch
        # declines the line; the DCC-IV branch reaches the refused
        # operator. D-6: the refusal must surface, and nothing may run.
        r = _repl(owners[1], ["150[Future] >>> 70[Count]", "quit"])
        st = _state(owners[1])
        _rec("t2_refusal_observable",
             "Flow refused" in r.stdout and ">>>" in r.stdout
             and "REQUIRES_RUNTIME_SUPPORT" in r.stdout,
             r.stdout[-200:])
        _rec("t2_refusal_executes_nowhere",
             "FlowOver boundary" not in r.stdout
             and "skipped by FlowOver" not in r.stdout
             and not st.context, f"context={st.context!r}")
        # A parse miss may still fall through quietly (D-6).
        r = _repl(owners[2], ["word 70[Count] >>> 51[Select]", "quit"])
        _rec("t2_parse_miss_stays_quiet", "Flow refused" not in r.stdout)

        # --- T-3: composer discipline --------------------------------
        from form.open import open_program
        from form.mandell.english_composer import (
            CompositeIntent, execute_composite)
        p3 = open_program(owners[3])
        good = CompositeIntent(english="x", clauses=[], intents=[],
                               flows=[">"],
                               mandell="40[TokenCount] > 12[Test]")
        rc = execute_composite(p3, good)
        _rec("t3_composer_executes_in_profile_b",
             rc.completed == 2 and rc.failed == 0 and rc.ok)
        bad = CompositeIntent(english="x", clauses=[], intents=[],
                              flows=[":"],
                              mandell="40[TokenCount] : 12[Test]")
        try:
            execute_composite(p3, bad)
            _rec("t3_altered_composite_refused", False, "no raise")
        except ValueError as e:
            _rec("t3_altered_composite_refused",
                 "DESCRIPTIVE_ONLY" in str(e), str(e))

        # --- T-4: Assert-label divergence is receipt-visible ---------
        from form.mandell.seed import parse_seed
        from form.mandell.chain_exec import execute_chain
        text = "91[Assert] >> 70[Count] :: false"
        pa = open_program(owners[4])
        oa = execute_chain(pa, parse_seed(text), text)
        a_blocked = any(a.get("skipped") for a in oa["atom_results"])
        pb = open_program(owners[5])
        rb = flow_executor.execute_program(
            pb, flow_executor.parse_program(text))
        _rec("t4_assert_label_pair_visible",
             oa["ok"] is False and a_blocked
             and "Assert FAIL false" in oa["messages"]
             and rb.completed == 2 and rb.ok,
             f"A ok={oa['ok']} blocked={a_blocked} | "
             f"B completed={rb.completed} ok={rb.ok}")

        # --- T-5a: bind-after-failure persists as working state ------
        r = _repl(owners[6], ["91[Assert] : 70[Count] :: false",
                              "save", "quit"])
        st = _state(owners[6])
        _rec("t5a_binding_persists",
             "Assert FAIL false" in r.stdout and st.context == "Count",
             f"context={st.context!r}")

        # --- T-5b/c + T-6: generations and rollback separation -------
        from form.mandell.checkpoint_generation import (
            committed_generation_state)
        p7 = open_program(owners[7])
        g0 = committed_generation_state(owners[7])
        ob = execute_chain(p7, parse_seed(
            "91[Assert] : 70[Count] :: false"),
            "91[Assert] : 70[Count] :: false")
        g1 = committed_generation_state(owners[7])
        od = execute_chain(p7, parse_seed(
            "70[Count] <<[Delta] 54[Query]"),
            "70[Count] <<[Delta] 54[Query]")
        g2 = committed_generation_state(owners[7])
        orb = execute_chain(p7, parse_seed("28[Rollback]"),
                            "28[Rollback]")
        _rec("t5b_generation_census_unchanged",
             ob["ok"] is False and g0 == g1 == g2,
             f"g0={g0} g1={g1} g2={g2}")
        _rec("t5c_rollback_posture_unchanged",
             orb["ok"] is False
             and any("Rollback denied" in m for m in orb["messages"]),
             str(orb["messages"][-1:]))
        _rec("t6_deltaflow_snapshot_not_a_generation",
             od["ok"] is True
             and any("DeltaFlow checkpoint snapshots=1" in m
                     for m in od["messages"])
             and g2 == g0)
    finally:
        for o in owners:
            _cleanup(o)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        print(f"[{'PASS' if ok else 'FAIL'}] {name} | {detail}")
    print(f"\n=== RESULT: {passed}/{len(RESULTS)} PASS ===")
    return passed == len(RESULTS)


if __name__ == "__main__":
    raise SystemExit(0 if smoke() else 1)
