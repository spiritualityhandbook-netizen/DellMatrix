"""Master plan P10 — flow-grammar conformance.

The grammar has nine flow operators. This suite pins the
conformance property — the parsed set, the runtime contract
set, and the publicly executable set are THE SAME SET — at the
public path: every operator is executed through a fresh REPL
process (REAL_USER_PATH) and its observable effect is asserted
(flow messages in the session output; state bindings verified
after save + reload in a separate process).

Pinned semantics (from chain_exec._apply_flow + cac_i K):
  >    FlowTo       both atoms run
  >>   FlowThru     next atom skipped iff the previous failed
  >>>  FlowOver     skip atoms until Join (Dell 61)
  :    FlowBy       bind execution context to the next term
  ::   DeepFlowBy   bind deep ref to the next term (mid-chain);
                    at seed end, :: is the label position — the
                    dual role is pinned by its own check
  :>   FlowTowards  set route to the next term
  <:   FlowFrom     bind from-ref to the previous term
  <:>  DynamicFlow  from-ref + route together (SD disposition:
                    KEEP — both bindings are state consumed by
                    the query/spectrum paths; no authority
                    effect; semantics pinned here)
  <<[Delta] DeltaFlow  append a state checkpoint snapshot
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
from form.mandell.control_runtime import FLOW_CONTRACT  # noqa: E402
from form.mandell.seed import parse_seed  # noqa: E402
from form.mandell.chain_exec import _flow_at  # noqa: E402

RESULTS = []

OPERATORS = [">", ">>", ">>>", ":", "::", ":>", "<:", "<:>",
             "<<[Delta]"]

SEEDS = {
    ">": "51[Select] > 70[Count]",
    ">>": "91[Assert] >> 70[Count] :: true",
    ">>>": "51[Select] >>> 70[Count] >> 61[Join]",
    ":": "80[Context] : 70[Count]",
    "::": "80[Context] :: 70[Count]",
    ":>": "59[Route] :> 70[Count]",
    "<:": "70[Count] <: 54[Query]",
    "<:>": "70[Count] <:> 54[Query]",
    "<<[Delta]": "70[Count] <<[Delta] 54[Query]",
}


def _rec(name, cond, detail=""):
    RESULTS.append((name, bool(cond), str(detail)[:200]))


def _cleanup(owner):
    base = os.path.join(
        os.path.dirname(__file__), "..", "state")
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
    owners = [f"P10FG{i}" for i in range(12)]
    for o in owners:
        _cleanup(o)
    try:
        # --- conformance of the three sets ---
        parsed = set()
        for op, seed_text in SEEDS.items():
            s = parse_seed(seed_text)
            parsed.add(_flow_at(s, 0))
        _rec("parse_set_is_the_nine", parsed == set(OPERATORS),
             str(sorted(parsed)))
        _rec("contract_set_is_the_nine",
             set(FLOW_CONTRACT.keys()) == set(OPERATORS),
             str(sorted(FLOW_CONTRACT.keys())))

        # --- per-operator public-path effects ---
        r = _repl(owners[0], [SEEDS[">"], "quit"])
        # Non-vacuous: the chain path ran — the router's per-atom
        # receipt ("MANDELL: 51[Select]" as a standalone routed
        # atom) must NOT appear; the seed executed as one chain.
        _rec("flowto_runs_both_as_one_chain",
             r.returncode == 0 and "FlowThru blocked" not in r.stdout
             and "skipped by FlowOver" not in r.stdout
             and "MANDELL: 51[Select]\n" not in r.stdout
             and "51[Select] > 70[Count]" in r.stdout)

        r = _repl(owners[1], ["91[Assert] >> 70[Count] :: false",
                              SEEDS[">>"], "quit"])
        _rec("flowthru_blocks_after_failure",
             "FlowThru blocked after fail" in r.stdout)

        r = _repl(owners[2], [SEEDS[">>>"], "quit"])
        _rec("flowover_skips_until_join",
             "FlowOver boundary — skip until Join" in r.stdout
             and "skipped by FlowOver 70" in r.stdout)

        r = _repl(owners[3], [SEEDS[":"], "save", "quit"])
        st = _state(owners[3])
        _rec("flowby_binds_context",
             "FlowBy bind context=Count" in r.stdout
             and st.context == "Count", f"context={st.context}")

        r = _repl(owners[4], [SEEDS["::"], "save", "quit"])
        st = _state(owners[4])
        _rec("deepflowby_binds_deep_ref",
             "DeepFlowBy Count" in r.stdout
             and st.refs.get("deep") == "Count", f"refs={st.refs}")

        r = _repl(owners[5], ["51[Select] > 70[Count] :: probe",
                              "quit"])
        _rec("label_position_is_not_deepflow",
             "DeepFlowBy" not in r.stdout)

        r = _repl(owners[6], [SEEDS[":>"], "save", "quit"])
        st = _state(owners[6])
        _rec("flowtowards_sets_route",
             "FlowTowards Count" in r.stdout
             and st.route == "Count", f"route={st.route}")

        r = _repl(owners[7], [SEEDS["<:"], "save", "quit"])
        st = _state(owners[7])
        _rec("flowfrom_binds_from_ref",
             "FlowFrom Count" in r.stdout
             and st.refs.get("from") == "Count", f"refs={st.refs}")

        r = _repl(owners[8], [SEEDS["<:>"], "save", "quit"])
        st = _state(owners[8])
        _rec("dynamicflow_binds_from_and_route",
             "DynamicFlow Count->Query" in r.stdout
             and st.refs.get("from") == "Count"
             and st.route == "Query",
             f"refs={st.refs} route={st.route}")

        r = _repl(owners[9], [SEEDS["<<[Delta]"],
                              SEEDS["<<[Delta]"], "quit"])
        _rec("deltaflow_appends_checkpoints",
             "DeltaFlow checkpoint snapshots=1" in r.stdout
             and "DeltaFlow checkpoint snapshots=2" in r.stdout)
    finally:
        for o in owners:
            _cleanup(o)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        print(f"[{'PASS' if ok else 'FAIL'}] {name} | {detail}")
    print(f"\n=== RESULT: {passed}/{len(RESULTS)} PASS ===")
    return passed == len(RESULTS)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
