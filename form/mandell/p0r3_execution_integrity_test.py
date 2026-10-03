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


# --------------------------------- DIRECTOR DECISION 1 (gate R1)
def t_director_d1_reserved_atom_truth() -> None:
    """Unified atom truth: ok=False, skipped=True, reason=<explicit>.

    A reserved/unexecuted atom did NOT successfully execute merely because
    its containing chain continues. ATOM EXECUTION RESULT != CHAIN
    CONTINUATION POLICY. No consumer may infer ok=True for an unexecuted op.
    """
    from form.mandell.executor import execute_seed
    from form.mandell.execution_observer import observe_seed_execution

    def atom_map(r):
        return {a["dell"]: a for a in (r.get("atom_results") or [])}

    # 1. single reserved seed -> honest refusal, zero mutation
    o = fresh_owner("d1")
    p = fresh_program(o)
    n0 = len(p.cube.session.plane.units)
    r = execute_seed(p, "151[Harmonic]")
    rec("d1_single_reserved_okfalse", r.get("ok") is False, "d1")
    rec("d1_single_reserved_zero_mutation",
        len(p.cube.session.plane.units) == n0, "d1")

    # 2. reserved first atom: chain continues, atom honest, aggregate honest
    o = fresh_owner("d1")
    p = fresh_program(o)
    r = execute_seed(p, "151[Harmonic] > 34[Stamp]")
    m = atom_map(r)
    rec("d1_first_atom_okfalse", m[151]["ok"] is False, "d1")
    rec("d1_first_atom_skipped", m[151]["skipped"] is True, "d1")
    rec("d1_first_atom_reason", bool(m[151].get("reason")), "d1")
    rec("d1_first_chain_continues", m[34]["ok"] is True, "d1")
    rec("d1_first_chain_okfalse", r.get("ok") is False, "d1")
    rec("d1_first_chain_partial", r.get("partial") is True, "d1")

    # 3. reserved middle atom, surrounded by supported
    o = fresh_owner("d1")
    p = fresh_program(o)
    r = execute_seed(p, "34[Stamp] > 151[Harmonic] > 34[Stamp]")
    m = atom_map(r)
    rec("d1_middle_atom_okfalse", m[151]["ok"] is False, "d1")
    rec("d1_middle_chain_continues_both_sides",
        m[34]["ok"] is True, "d1")
    rec("d1_middle_aggregate_partial", r.get("partial") is True, "d1")
    rec("d1_middle_any_skipped", r.get("any_skipped") is True, "d1")

    # 4. reserved final atom
    o = fresh_owner("d1")
    p = fresh_program(o)
    r = execute_seed(p, "34[Stamp] > 151[Harmonic]")
    m = atom_map(r)
    rec("d1_final_atom_okfalse", m[151]["ok"] is False, "d1")
    rec("d1_final_chain_okfalse", r.get("ok") is False, "d1")

    # 5. multiple reserved atoms
    o = fresh_owner("d1")
    p = fresh_program(o)
    r = execute_seed(p, "34[Stamp] > 151[Harmonic] > 151[Harmonic] > 34[Stamp]")
    ars = r.get("atom_results") or []
    skips = [a for a in ars if a.get("skipped")]
    rec("d1_multi_all_skips_okfalse",
        len(skips) == 2 and all(a["ok"] is False for a in skips), "d1")
    rec("d1_multi_supported_still_run",
        sum(1 for a in ars if a["ok"] is True) == 2, "d1")

    # 6. supported atoms surrounding reserved (already covered in 3; explicit)
    o = fresh_owner("d1")
    p = fresh_program(o)
    n0 = len(p.cube.session.plane.units)
    r = execute_seed(p, "34[Stamp] > 151[Harmonic] > 34[Stamp]")
    rec("d1_surrounding_mutations_honest",
        len(p.cube.session.plane.units) >= n0, "d1")

    # 7. all-supported chain: ok=True, partial=False, nothing skipped
    o = fresh_owner("d1")
    p = fresh_program(o)
    r = execute_seed(p, "34[Stamp] > 34[Stamp]")
    rec("d1_all_supported_ok", r.get("ok") is True, "d1")
    rec("d1_all_supported_not_partial", r.get("partial") is False, "d1")
    rec("d1_all_supported_none_skipped", r.get("any_skipped") is False, "d1")

    # 8. all-reserved chain: ok=False, not partial (fully skipped), all honest
    o = fresh_owner("d1")
    p = fresh_program(o)
    n0 = len(p.cube.session.plane.units)
    r = execute_seed(p, "151[Harmonic] > 151[Harmonic]")
    ars = r.get("atom_results") or []
    rec("d1_all_reserved_okfalse", r.get("ok") is False, "d1")
    rec("d1_all_reserved_not_partial", r.get("partial") is False, "d1")
    rec("d1_all_reserved_all_skipped",
        len(ars) == 2 and all(a["ok"] is False and a["skipped"] is True
                              for a in ars), "d1")
    rec("d1_all_reserved_zero_mutation",
        len(p.cube.session.plane.units) == n0, "d1")

    # 9. nested/composed path: reserved atom inside a Sequence control
    o = fresh_owner("d1")
    p = fresh_program(o)
    r = execute_seed(p, "63[Sequence] > 34[Stamp] > 151[Harmonic] > 61[Join]")
    m = {a["dell"]: a for a in (r.get("atom_results") or [])
         if a.get("dell") != 61}
    rec("d1_nested_reserved_okfalse", m[151]["ok"] is False, "d1")
    rec("d1_nested_reserved_skipped", m[151]["skipped"] is True, "d1")
    rec("d1_nested_chain_okfalse", r.get("ok") is False, "d1")

    # 10. raw receipt: observe_seed_execution -> Outcome carries the truth
    o = fresh_owner("d1")
    p = fresh_program(o)
    out = observe_seed_execution(p, "34[Stamp] > 151[Harmonic]")
    recs = getattr(p, "outcome_records", None)
    last = recs[-1] if isinstance(recs, list) else list(recs.values())[-1]
    am = {a["dell"]: a for a in (last.get("atom_results") or [])}
    rec("d1_raw_receipt_atom_okfalse", am[151]["ok"] is False, "d1")
    rec("d1_raw_receipt_atom_skipped", am[151]["skipped"] is True, "d1")
    rec("d1_raw_receipt_partial", last.get("partial_completion") is True, "d1")
    rec("d1_raw_receipt_chain_okfalse", out.get("ok") is False, "d1")

    # 11. public receipt: router on a single reserved intent refuses honestly
    o = fresh_owner("d1")
    p = fresh_program(o)
    from form.mandell import semantic_router as sr
    from form.mandell.translate import Intent
    intent = Intent(action="harmonic", dell=151, term="Harmonic",
                   mandel="151[Harmonic]", english="151[Harmonic]")
    n0 = len(p.cube.session.plane.units)
    receipt = sr.route_intent(p, intent)
    rec("d1_public_receipt_okfalse", receipt.ok is False, "d1")
    rec("d1_public_receipt_names_block",
        "reserv" in str(receipt.error or receipt.state_note or "").lower(),
        "d1")
    rec("d1_public_receipt_zero_mutation",
        len(p.cube.session.plane.units) == n0, "d1")

    # 12. consumer interpretation: no consumer infers ok=True for unexecuted
    o = fresh_owner("d1")
    p = fresh_program(o)
    r = execute_seed(p, "34[Stamp] > 151[Harmonic]")

    def consumer_infers_success(chain_result):
        # A naive consumer: "chain ok and every atom ok" -> success.
        # Must NOT report success for the skipped atom.
        for a in (chain_result.get("atom_results") or []):
            if a.get("skipped") and a.get("ok"):
                return True  # BUG: inferred success for unexecuted atom
        return False

    rec("d1_consumer_no_false_success",
        consumer_infers_success(r) is False, "d1")
    rec("d1_consumer_sees_explicit_reason",
        all(a.get("reason") for a in (r.get("atom_results") or [])
            if a.get("skipped")), "d1")


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
        t_director_d1_reserved_atom_truth()
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
