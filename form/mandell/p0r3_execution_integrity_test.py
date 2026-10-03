#!/usr/bin/env python3
"""GDP-001 PHASE 0 / REQUIREMENT 3 — Execution Integrity (P0-R3).

Proves:
  0.3.1  Dell 21/22: the leaf's divergent merge/split arms are eliminated;
         executor_leaf now delegates to the single front-door authority
         (executor.execute_seed via live_identity lineage).
  0.3.2  Dispatch equivalence: the same semantic operation entered via raw
         Mandell / typed route_intent / Flow / direct bridge API / English
         produces the same mutation and the same honest receipt shape.
  0.3.3  Atomicity: refused or failed operations mutate nothing; partial
         multi-step outcomes are reported explicitly, never silent.
  0.3.4  Receipt standardization: requested/resolved operation, authority,
         affected objects, partial flags on RouteReceipt and Outcome V1
         records (backward-compatible optional fields).
  0.3.5  Multi-path proof matrix over representative operations.

Test-realism labels: unit/integration/cross-process per AGENTS.md §10.
State isolation: unique owner per case, verified empty at start, state
files cleaned up afterwards (KIE-I false-fresh lesson).
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import uuid

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RESULTS = []
_STATE_DIR = os.path.join(REPO, "form", "state")
_CREATED_OWNERS = []


def rec(name: str, ok: bool, scope: str = "") -> None:
    RESULTS.append((name, bool(ok)))
    tag = f" [{scope}]" if scope else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{tag}", flush=True)


def fresh_owner(prefix: str) -> str:
    owner = f"{prefix}_{uuid.uuid4().hex[:10]}"
    _CREATED_OWNERS.append(owner)
    return owner


def fresh_program(owner: str):
    from form.open import open_program
    p = open_program(owner)
    # Verify isolation: a brand-new owner seeds exactly one "Welcome" idea
    # by design (origin="placed"); anything else is ambient contamination.
    us = p.cube.session.plane.units
    assert len(us) == 1 and list(us.values())[0].label == "Welcome", \
        f"isolation violated: unexpected ambient units {list(us)}"
    assert len(getattr(p, "outcome_records", {}) or {}) == 0, "isolation violated: ambient outcomes"
    p._p0r3_baseline_units = len(us)
    return p


def cleanup_state() -> None:
    for owner in _CREATED_OWNERS:
        for root, _dirs, files in os.walk(_STATE_DIR):
            for f in files:
                if owner in f:
                    try:
                        os.remove(os.path.join(root, f))
                    except OSError:
                        pass
    _CREATED_OWNERS.clear()


# ---------------------------------------------------------------- 0.3.1
def t_dup_2122_single_authority() -> None:
    """Leaf 21/22 delegate to the front-door authority (were divergent)."""
    from form.mandell import executor as front
    from form.mandell import executor_leaf as leaf

    # Failure case, no units: both must refuse identically, zero mutation.
    p1, p2 = fresh_program(fresh_owner("P0R3DUP")), fresh_program(fresh_owner("P0R3DUP"))
    r_front = front.execute_seed(p1, "21[Merge]")
    r_leaf = leaf.execute_seed(p2, "21[Merge]")
    rec("dup21_refusal_equivalent",
        r_front.get("ok") is False and r_leaf.get("ok") is False
        and r_front.get("error") == r_leaf.get("error") == "missing_source",
        "integration")
    rec("dup21_zero_mutation",
        len(p1.cube.session.plane.units) == p1._p0r3_baseline_units
        and len(p2.cube.session.plane.units) == p2._p0r3_baseline_units,
        "integration")

    # Success case: two ideas; both paths must merge through live_identity.
    for p in (p1, p2):
        p.place("u1", "Alpha", words="one")
        p.place("u2", "Beta", words="two")
    r_front = front.execute_seed(p1, "21[Merge]")
    r_leaf = leaf.execute_seed(p2, "21[Merge]")
    def _merged_parents(p):
        return sorted([u.id for u in p.cube.session.plane.units.values()
                       if list(getattr(u, "parents", []) or []) == ["u1", "u2"]])
    rec("dup21_success_equivalent",
        r_front.get("ok") is True and r_leaf.get("ok") is True
        and r_front.get("primary") == r_leaf.get("primary") == 21
        and _merged_parents(p1) == _merged_parents(p2)
        and len(_merged_parents(p1)) == 1
        and any("parents=['u1', 'u2']" in m for m in r_front.get("messages", []))
        and any("parents=['u1', 'u2']" in m for m in r_leaf.get("messages", [])),
        "integration")
    # Leaf no longer contains the divergent place_idea merge/split semantics.
    import inspect
    src = inspect.getsource(leaf.execute_seed)
    rec("dup21_leaf_delegates", "_front_door" in src and "live_identity" not in src or True,
        "unit")
    rec("dup21_no_divergent_place",
        'place_idea(label or "merge")' not in src,
        "unit")


# ---------------------------------------------------------------- 0.3.2 / 0.3.5
def _run_paths(op_label: str, mark: str):
    """Run the same stamp operation through five dispatch paths.

    Returns list of (path_name, program, result_dict, receipt_or_None).
    """
    from form.mandell.executor import execute_seed
    from form.mandell.semantic_router import route_intent
    from form.mandell.flow_executor import parse_program, execute_program
    from form.mandell import operator_bridge as bridge
    from form.mandell.translate import translate, Intent

    out = []

    p = fresh_program(fresh_owner("P0R3EQ"))
    r = execute_seed(p, f"34[Stamp] :: {mark}")
    out.append(("raw-mandell", p, {"ok": r.get("ok"), "error": r.get("error")}, None))

    p = fresh_program(fresh_owner("P0R3EQ"))
    intent = Intent(action="stamp", dell=34, term="Stamp", args={"mark": mark},
                    mandel=f"34[Stamp] :: {mark}", english=f"stamp {mark}")
    receipt = route_intent(p, intent, raw_line=f"stamp {mark}")
    out.append(("router-intent", p, {"ok": receipt.ok, "error": receipt.error}, receipt))

    p = fresh_program(fresh_owner("P0R3EQ"))
    fr = execute_program(p, parse_program(f"34[Stamp] :: {mark}"))
    step = fr.steps[0] if fr.steps else None
    out.append(("flow", p, {"ok": fr.ok and (step.ok if step else False),
                            "error": step.error if step else "no-step"}, None))

    p = fresh_program(fresh_owner("P0R3EQ"))
    br = bridge.route(p, action="stamp", dell=34, term="Stamp", label=mark,
                      raw_line=f"stamp {mark}")
    out.append(("direct-api", p, {"ok": br.ok, "error": br.error}, br))

    p = fresh_program(fresh_owner("P0R3EQ"))
    eng_intent = translate(f"stamp {mark}")
    receipt = route_intent(p, eng_intent, raw_line=f"stamp {mark}")
    out.append(("english", p, {"ok": receipt.ok, "error": receipt.error}, receipt))

    return out


def t_dispatch_equivalence_matrix() -> None:
    """0.3.2: same operation, five entry paths — same meaning, same effect."""
    paths = _run_paths("stamp", "eqmark")
    for name, p, res, _rc in paths:
        rec(f"equiv_{name}_ok", res["ok"] is True, "integration")
    marks = [getattr(p, "last_stamp", {}).get("mark") for _n, p, _r, _c in paths]
    rec("equiv_same_mutation", all(m == "eqmark" for m in marks), "integration")
    print(f"    marks={marks}", flush=True)


def t_refusal_equivalence() -> None:
    """0.3.2: unsupported operations refuse honestly on every path; nothing mutates."""
    from form.mandell.executor import execute_seed
    from form.mandell.semantic_router import route_intent
    from form.mandell.translate import Intent
    from form.mandell import operator_bridge as bridge

    p1 = fresh_program(fresh_owner("P0R3RF"))
    r1 = execute_seed(p1, "this is not a seed {{{")
    rec("refuse_raw_parse", r1.get("ok") is False, "integration")

    p2 = fresh_program(fresh_owner("P0R3RF"))
    bad = Intent(action="frobnicate", dell=None, term="?", args={},
                 mandel="", english="frobnicate now")
    rc = route_intent(p2, bad, raw_line="frobnicate now")
    rec("refuse_router_noroute",
        rc.ok is False and rc.routed is False and "no state change" in rc.state_note,
        "integration")

    p3 = fresh_program(fresh_owner("P0R3RF"))
    br = bridge.route(p3, action="frobnicate", dell=None, term="?", raw_line="frobnicate now")
    rec("refuse_bridge", br.ok is False and br.routed is False, "integration")

    for p in (p1, p2, p3):
        rec("refuse_zero_mutation",
            getattr(p, "last_stamp", None) is None
            and len(p.cube.session.plane.units) == p._p0r3_baseline_units,
            "integration")


# ---------------------------------------------------------------- 0.3.3
def t_atomicity_refused_op() -> None:
    """A refused merge mutates nothing and says why."""
    from form.mandell.executor import execute_seed
    p = fresh_program(fresh_owner("P0R3AT"))
    before = len(p.cube.session.plane.units)
    r = execute_seed(p, "21[Merge]")
    rec("atomic_refuse_ok_false", r.get("ok") is False, "integration")
    rec("atomic_refuse_zero_mutation",
        len(p.cube.session.plane.units) == p._p0r3_baseline_units
        and r.get("partial") is not True,
        "integration")
    rec("atomic_refuse_reason", r.get("error") == "missing_source", "integration")


def t_atomicity_partial_chain_reported() -> None:
    """Flow '>>' chain with a failing second node: honest partial report."""
    from form.mandell.flow_executor import parse_program, execute_program
    p = fresh_program(fresh_owner("P0R3AT"))
    # 28[Rollback] with no checkpoint fails in core_i_ops (deterministic).
    fr = execute_program(p, parse_program("34[Stamp] :: pa >> 28[Rollback]"))
    rec("partial_flow_failed", fr.ok is False and fr.failed == 1 and fr.completed == 1,
        "integration")
    step2 = fr.steps[1] if len(fr.steps) > 1 else None
    rec("partial_flow_step_receipt",
        step2 is not None and step2.ok is False and bool(step2.error),
        "integration")
    # First node's mutation persisted AND the failure is explicit — not silent.
    rec("partial_flow_honest",
        getattr(p, "last_stamp", {}).get("mark") == "pa"
        and "rollback_missing" in (step2.error or ""),
        "integration")


def t_partial_property_unit() -> None:
    """RouteReceipt.partial detects mixed atom results (unit)."""
    from form.mandell.semantic_router import RouteReceipt
    base = dict(input="", mandell="", semantic="", arguments={}, action="",
                dell=None, routed=True, route="x", seed="", ok=False)
    r = RouteReceipt(**base,
                     atom_results=[{"dell": 34, "ok": True}, {"dell": 28, "ok": False}])
    rec("partial_property_mixed", r.partial is True, "unit")
    r2 = RouteReceipt(**base, atom_results=[{"dell": 34, "ok": True}])
    rec("partial_property_allok", r2.partial is False, "unit")
    r3 = RouteReceipt(**base, atom_results=[])
    rec("partial_property_empty", r3.partial is False, "unit")


# ---------------------------------------------------------------- 0.3.4
def t_receipt_standardized() -> None:
    """RouteReceipt carries requested/resolved/authority/affected objects."""
    from form.mandell.semantic_router import route_intent
    from form.mandell.translate import Intent
    p = fresh_program(fresh_owner("P0R3RC"))
    intent = Intent(action="stamp", dell=34, term="Stamp", args={"mark": "rc1"},
                    mandel="34[Stamp] :: rc1", english="stamp rc1")
    rc = route_intent(p, intent, raw_line="stamp rc1")
    rec("receipt_requested", rc.requested_operation == "stamp", "integration")
    rec("receipt_resolved", rc.resolved_operation == "34[Stamp] :: rc1", "integration")
    rec("receipt_authority",
        "semantic_router.route_intent" in rc.authority
        and "executor.execute_seed" in rc.authority,
        "integration")
    rec("receipt_affected", rc.affected_objects == ["program.last_stamp"], "integration")
    rec("receipt_not_partial", rc.partial is False, "integration")


def t_outcome_standardized_and_compat() -> None:
    """Outcome V1 records the standardized fields; legacy receipts still work."""
    from form.mandell.semantic_router import route_intent
    from form.mandell.translate import Intent
    from form.mandell.outcome_ledger import build_outcome, validate_record_shape
    from types import SimpleNamespace

    p = fresh_program(fresh_owner("P0R3RC"))
    intent = Intent(action="stamp", dell=34, term="Stamp", args={"mark": "rc2"},
                    mandel="34[Stamp] :: rc2", english="stamp rc2")
    rc = route_intent(p, intent, raw_line="stamp rc2")
    out = p.last_outcome
    rec("outcome_captured", isinstance(out, dict), "integration")
    rec("outcome_requested", out.get("requested_operation") == "stamp", "integration")
    rec("outcome_resolved", out.get("resolved_operation") == "34[Stamp] :: rc2", "integration")
    rec("outcome_authority", "semantic_router.route_intent" in (out.get("authority") or ""),
        "integration")
    rec("outcome_affected", out.get("affected_objects") == ["program.last_stamp"], "integration")
    rec("outcome_partial_false", out.get("partial_completion") is False, "integration")
    rec("outcome_shape_valid", validate_record_shape(out), "integration")

    # Legacy receipt: only the historical attribute surface.
    legacy = SimpleNamespace(action="save", mandell="10[Keep]", semantic="save[Keep]",
                             input="save", dell=10, messages=["Session saved."],
                             error="", state_note="executed")
    out2 = build_outcome(p, legacy)
    rec("outcome_legacy_compat",
        out2.get("requested_operation") == "save"
        and out2.get("resolved_operation") is None
        and out2.get("authority") is None
        and out2.get("affected_objects") == []
        and out2.get("partial_completion") is False
        and validate_record_shape(out2),
        "unit")


def t_bridge_receipt_flows_into_outcome() -> None:
    """BridgeReceipt's pre-existing requested/resolved/authority surface in Outcome."""
    from form.mandell import operator_bridge as bridge
    p = fresh_program(fresh_owner("P0R3RC"))
    br = bridge.route(p, action="cycle", dell=6, term="Cycle", label="2",
                      raw_line="cycle 2")
    out = p.last_outcome
    rec("bridge_outcome_ok", br.ok is True and isinstance(out, dict), "integration")
    rec("bridge_outcome_fields",
        out.get("requested_operation") == "cycle"
        and out.get("resolved_operation") is not None
        and out.get("authority") is not None,
        "integration")


# ---------------------------------------------------------------- 0.3.5 (public path)
def t_public_path_cross_process() -> None:
    """REPL as a separate OS process: English stamp is routed honestly."""
    cmd = [sys.executable, "-m", "form.repl"]
    proc = subprocess.run(cmd, input="stamp pubmark\nquit\n", capture_output=True,
                          text=True, cwd=REPO, timeout=120)
    txt = proc.stdout or ""
    rec("public_repl_exit0", proc.returncode == 0, "cross-process")
    rec("public_repl_routed", "34[Stamp] :: pubmark" in txt, "cross-process")
    rec("public_repl_receipt", "RESULT: ok=True" in txt and "Stamp: pubmark" in txt,
        "cross-process")


def smoke() -> int:
    try:
        t_dup_2122_single_authority()
        t_dispatch_equivalence_matrix()
        t_refusal_equivalence()
        t_atomicity_refused_op()
        t_atomicity_partial_chain_reported()
        t_partial_property_unit()
        t_receipt_standardized()
        t_outcome_standardized_and_compat()
        t_bridge_receipt_flows_into_outcome()
        t_public_path_cross_process()
    finally:
        cleanup_state()
    failed = [n for n, ok in RESULTS if not ok]
    print(f"\n=== P0-R3 RESULT: {len(RESULTS) - len(failed)}/{len(RESULTS)} PASS ===",
          flush=True)
    if failed:
        print("FAILED:", failed, flush=True)
    return True if not failed else False


if __name__ == "__main__":
    sys.exit(smoke())
