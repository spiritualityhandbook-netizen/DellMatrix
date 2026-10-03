#!/usr/bin/env python3
"""Typed Mandell -> Dell semantic routing boundary (DCC-II).

Routes a Mandell Intent to the EXISTING Dell execution authority, but ONLY
where semantic equivalence has been demonstrated and recorded in
CORRESPONDENCE.

Semantic Safety Law:
  - No name-matching. A correspondence is allowed only where the Intent's
    semantics (inputs, outputs, side effects, state authority, failure
    behavior) match the Dell execution arm's actual behavior.
  - Address identity comes from parsing the Intent's Mandell composition
    with the real Mandell parser (parse_seed). The (action, dell) pair must
    BOTH match a registered correspondence.
  - If the Mandell Core operation numbers and Dell addresses were different
    namespaces, they would be kept different. Here the Intent's mandel
    strings use Dell addresses (10, 13, 35) from the Dell registry, and the
    correspondence is verified against the arms in executor_leaf.py /
    core_i_ops.py — the same authority the seed path uses.
  - The router NEVER reimplements a Dell arm. Execution always goes through
    form.mandell.executor.execute_seed, the existing authority.
  - If no correspondence matches, nothing executes. The receipt says so.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple


@dataclass
class RouteReceipt:
    """Honest execution receipt for a routing attempt (v2)."""

    input: str                    # raw user input
    mandell: str                  # Mandell composition from the Intent
    semantic: str                 # semantic operation (action term)
    arguments: Dict[str, Any]     # typed arguments through Mandell
    action: str                   # Intent action
    dell: Optional[int]           # primary Dell address parsed from composition
    routed: bool                  # whether a Dell was actually executed
    route: str                    # correspondence key or "no-route"
    seed: str                     # canonical seed executed ("" if none)
    ok: bool                      # execution ok (False if not routed or failed)
    messages: List[str] = field(default_factory=list)
    state_note: str = ""
    error: str = ""
    new_program: Any = None       # restored program (Dell 28 rollback only)
    # GDP-001 0.3.4: standardized receipt fields. Optional/backward
    # compatible; "" / [] / None means "unknown", never fabricated.
    requested_operation: str = ""  # what was asked (intent action / raw input)
    resolved_operation: str = ""   # what actually executed (canonical seed)
    authority: str = ""            # which authority executed it
    affected_objects: List[str] = field(default_factory=list)  # known mutations
    atom_results: List[Dict[str, Any]] = field(default_factory=list)  # chain

    @property
    def partial(self) -> bool:
        """True when a multi-atom execution partially completed.

        Some atoms succeeded and mutated state while others failed —
        reported explicitly, never silent.
        """
        rs = [r for r in self.atom_results if isinstance(r, dict)]
        oks = [bool(r.get("ok", True)) for r in rs]
        return bool(rs) and any(oks) and not all(oks)


# Canonical execution authority chain, recorded on every receipt.
_AUTHORITY_ROUTER = "form.mandell.semantic_router.route_intent"
_AUTHORITY_EXECUTOR = "form.mandell.executor.execute_seed"
_AUTHORITY_CHAIN = "form.mandell.chain_exec.execute_chain"


def _affected_for(action: str, dell: Optional[int]) -> List[str]:
    """Honestly known mutation targets for correspondence-routed ops.

    Only entries the router can verify from its own evidence. Everything
    else is [] (unknown), never invented.
    """
    key = ((action or "").strip().lower(), dell)
    return list({
        ("stamp", 34): ["program.last_stamp"],
        ("checkpoint", 27): ["program.last_core_i", "generation"],
        ("rollback", 28): ["program (restored generation)"],
        ("save", 10): ["program state file"],
        ("nurture", 37): ["program.last_nurture"],
        ("grow", 13): ["nursery proposals"],
        ("discover", 35): ["program.last_discover"],
        ("cycle", 6): ["duobeta cycles"],
        ("form", 15): ["lattice form"],
    }.get(key, []))


@dataclass
class _Correspondence:
    action: str
    dell: int
    dell_name: str
    evidence: str
    build_seed: Callable[[Any, Any], str]  # (intent, parsed_seed) -> canonical seed


def _seed_save(intent: Any, parsed: Any) -> str:
    return "10[Keep]"


def _seed_grow(intent: Any, parsed: Any) -> str:
    try:
        cycles = int((intent.args or {}).get("cycles", 1))
    except (TypeError, ValueError):
        cycles = 1
    return f"13[Loop] :: {max(1, cycles)}"


def _seed_discover(intent: Any, parsed: Any) -> str:
    label = (parsed.label or "inventory").strip() or "inventory"
    return f"35[Discover] :: {label}"


# DCC-III seed builders (arguments flow through Mandell, not around it).
def _seed_measure(intent: Any, parsed: Any) -> str:
    return "40[TokenCount]"


def _seed_test(intent: Any, parsed: Any) -> str:
    return "12[Test]"


def _seed_architect(intent: Any, parsed: Any) -> str:
    return "11[Architect]"


def _seed_simulate(intent: Any, parsed: Any) -> str:
    return "31[Simulate]"


def _seed_checkpoint(intent: Any, parsed: Any) -> str:
    return "27[Checkpoint]"


def _seed_stamp(intent: Any, parsed: Any) -> str:
    mark = str((intent.args or {}).get("mark", "")).strip()[:48] or "mark"
    # Sanitize: Mandell label must be safe.
    mark = "".join(c for c in mark if c.isalnum() or c in "-_ ").strip() or "mark"
    return f"34[Stamp] :: {mark}"


def _seed_cycle(intent: Any, parsed: Any) -> str:
    try:
        n = int((intent.args or {}).get("count", 1))
    except (TypeError, ValueError):
        n = 1
    n = max(1, min(n, 5))  # Dell 6 caps at 5
    return f"06[Cycle] :: {n}"


def _seed_form(intent: Any, parsed: Any) -> str:
    form_name = str((intent.args or {}).get("form", "")).strip().lower()
    if form_name not in ("cube", "sphere", "core", "flower"):
        form_name = "cube"  # safe default; Dell 15 ignores invalid
    return f"15[Map] :: {form_name}"


def _seed_rollback(intent: Any, parsed: Any) -> str:
    return "28[Rollback]"


def _seed_retry(intent: Any, parsed: Any) -> str:
    return "42[Retry]"


# DCC-VI seed builder: arguments flow through Mandell, not around it.
def _seed_nurture(intent: Any, parsed: Any) -> str:
    label = (parsed.label or "").strip()
    return f"37[Nurture] :: {label}" if label else "37[Nurture]"


# Verified semantic correspondences.
# Each entry documents WHY the routing is safe (not just name similarity).
CORRESPONDENCE: Dict[Tuple[str, int], _Correspondence] = {
    ("save", 10): _Correspondence(
        action="save",
        dell=10,
        dell_name="Keep",
        evidence=(
            "Intent('save') = persist the session. Dell 10 arm "
            "(executor_leaf.py) calls program.save() — the identical state "
            "authority, inputs, outputs, and side effects as the direct "
            "handler. Verified live: same file written, same messages."
        ),
        build_seed=_seed_save,
    ),
    ("grow", 13): _Correspondence(
        action="grow",
        dell=13,
        dell_name="Loop",
        evidence=(
            "Intent('grow') = grow ideas via nursery. Dell 13 arm calls "
            "program.grow_ideas(cycles) — the identical state authority as "
            "the direct handler. Cycles carried from intent.args (default 1). "
            "Verified live: identical state authority and side effects. "
            "Note: correspondence is to the arm's BEHAVIOR (grow_ideas), not "
            "the Dell's display name."
        ),
        build_seed=_seed_grow,
    ),
    ("discover", 35): _Correspondence(
        action="discover",
        dell=35,
        dell_name="Discover",
        evidence=(
            "Intent('discover') = inspect/inventory state. Dell 35 arm "
            "(core_i_ops.py) lists program ideas and nursery summary — "
            "read-only, no state mutation. The label selects nursery vs "
            "full inventory (genuine selection behavior inside the Dell). "
            "Verified live: state unchanged, label-driven selection."
        ),
        build_seed=_seed_discover,
    ),
    # DCC-III: expanded semantic vocabulary (all EXACT, verified live).
    ("measure", 40): _Correspondence(
        action="measure",
        dell=40,
        dell_name="TokenCount",
        evidence=(
            "Intent('measure') = compute session weight. Dell 40 arm "
            "(core_i_ops.py) computes approx units from ideas/history/cells/"
            "pending — read-only, no mutation. Verified live: returns "
            "TokenCount with breakdown."
        ),
        build_seed=_seed_measure,
    ),
    ("test", 12): _Correspondence(
        action="test",
        dell=12,
        dell_name="Test",
        evidence=(
            "Intent('test') = self-check systems. Dell 12 arm "
            "(executor_leaf.py) runs 5 checks (floor, lattice, growth, "
            "nursery, ideas) — read-only except note_seed logging. "
            "Verified live: 5/5 PASS."
        ),
        build_seed=_seed_test,
    ),
    ("architect", 11): _Correspondence(
        action="architect",
        dell=11,
        dell_name="Architect",
        evidence=(
            "Intent('architect') = show schema. Dell 11 arm "
            "(executor_leaf.py) displays owner, ideas, lattice size/form, "
            "cells — read-only. Verified live: schema displayed."
        ),
        build_seed=_seed_architect,
    ),
    ("simulate", 31): _Correspondence(
        action="simulate",
        dell=31,
        dell_name="Simulate",
        evidence=(
            "Intent('simulate') = dry-run preview. Dell 31 arm "
            "(executor_leaf.py) shows status explicitly as 'no mutation' — "
            "read-only. Verified live: dry-run output, no state change."
        ),
        build_seed=_seed_simulate,
    ),
    ("checkpoint", 27): _Correspondence(
        action="checkpoint",
        dell=27,
        dell_name="Checkpoint",
        evidence=(
            "Intent('checkpoint') = save restore point. Dell 27 arm "
            "(core_i_ops.py) delegates to core_i_recovery.checkpoint, which "
            "commits a Checkpoint Generation V1 generation (Persistence V2 "
            "atomic members + atomic CURRENT pointer) — STATE-CHANGING "
            "(durable generation). Verified live: generation committed."
        ),
        build_seed=_seed_checkpoint,
    ),
    ("stamp", 34): _Correspondence(
        action="stamp",
        dell=34,
        dell_name="Stamp",
        evidence=(
            "Intent('stamp') = mark moment with label. Dell 34 arm "
            "(core_i_ops.py) sets program.last_stamp — STATE-CHANGING. "
            "Mark carried through Mandell label. Verified live: stamp set."
        ),
        build_seed=_seed_stamp,
    ),
    ("cycle", 6): _Correspondence(
        action="cycle",
        dell=6,
        dell_name="Cycle",
        evidence=(
            "Intent('cycle') = run N growth cycles. Dell 6 arm "
            "(executor_leaf.py) calls program.grow_ideas(n) with n from "
            "label (1-5) and displays DuoBeta rings — STATE-CHANGING with "
            "DuoBeta interaction. Count through Mandell. Verified live: "
            "Cycle x2 with rings."
        ),
        build_seed=_seed_cycle,
    ),
    ("form", 15): _Correspondence(
        action="form",
        dell=15,
        dell_name="Map",
        evidence=(
            "Intent('form') = change lattice form. Dell 15 arm "
            "(executor_leaf.py) calls to_cube/to_sphere/to_core/to_flower — "
            "STATE-CHANGING. Form name through Mandell label. Verified "
            "live: Form → sphere."
        ),
        build_seed=_seed_form,
    ),
    ("load", 28): _Correspondence(
        action="load",
        dell=28,
        dell_name="Rollback",
        evidence=(
            "Intent('load') = restore checkpoint. Dell 28 arm "
            "(core_i_ops.py) restores via core_i_recovery.rollback, which "
            "loads the committed Generation V1 generation (fingerprint-"
            "validated, never hybrid; legacy timestamp files still readable) "
            "— CONTROL (revert). Fails safe with "
            "'rollback_missing' if no checkpoint. Verified live: restored."
        ),
        build_seed=_seed_rollback,
    ),
    ("retry", 42): _Correspondence(
        action="retry",
        dell=42,
        dell_name="Retry",
        evidence=(
            "Intent('retry') = replay last operation. Dell 42 arm "
            "(executor_leaf.py) replays from history — CONTROL. "
            "Verified live: Retry ran."
        ),
        build_seed=_seed_retry,
    ),
    # DCC-VI: nurture = nursery mutations via Dell 37 (SAFE_ADAPTER).
    # Dell 37 arm (core_i_ops.py) calls existing Nursery.add/confirm/reject
    # methods — real, tested runtime authority. Not a new state system.
    ("nurture", 37): _Correspondence(
        action="nurture",
        dell=37,
        dell_name="Nurture",
        evidence=(
            "Intent('nurture') = nursery proposal operations. Dell 37 arm "
            "(core_i_ops.py) adapts existing Nursery.add/confirm/reject — "
            "real methods with save/rollback safety. Label carries the "
            "operation (add <label> / confirm <pid> / reject <pid>). "
            "Verified live: proposals added/confirmed/rejected."
        ),
        build_seed=_seed_nurture,
    ),
}


def route_intent(program: Any, intent: Any, raw_line: str = "",
                 composition: Optional[Dict[str, Any]] = None,
                 interaction_id: Optional[str] = None) -> RouteReceipt:
    """Route a Mandell Intent through the Dell execution authority.

    Returns a RouteReceipt that honestly reports what happened. If the
    Intent's Mandell composition does not parse, or the (action, dell)
    pair has no verified correspondence, NOTHING executes.

    DCC-XX: after the receipt is built, an Outcome Record V1 is captured
    into the program's durable outcome ledger (post-hoc observation;
    routing behavior untouched). ``composition`` optionally carries flow
    context (``{"flow_program": ..., "node_index": ...}``) for node-level
    outcomes inside composed programs.

    DCC-XX-C1 freshness gate: ``program.last_nurture`` is a single-slot
    attribute shared across calls. The slot's identity is snapshotted
    before execution; provenance is attributed to the outcome only when
    the executed call replaced the slot (handlers always assign a fresh
    dict). Stale evidence from a previous call can never contaminate a
    later outcome.

    ``interaction_id`` (EIC-I): optional explicit correlation to the
    interaction that caused this execution. None = UNKNOWN. This function
    ACCEPTS identity; it does not mint it.
    """
    nurture_before = getattr(program, "last_nurture", None)
    receipt = _route_intent_impl(program, intent, raw_line)
    # DCC-XX-C1: attribute the arm's receipt only to the call that
    # produced it. Identity comparison: every arm handler assigns a
    # fresh dict to program.last_nurture when it runs.
    nurture_after = getattr(program, "last_nurture", None)
    nurture_fresh = (nurture_after is not nurture_before
                     and isinstance(nurture_after, dict))
    # DCC-XX capture: post-hoc, never raises, never alters routing.
    try:
        from .outcome_ledger import capture_outcome
        capture_outcome(program, receipt, composition,
                        nurture_fresh=nurture_fresh,
                        interaction_id=interaction_id)
    except Exception:
        pass
    return receipt


def _route_intent_impl(program: Any, intent: Any, raw_line: str = "") -> RouteReceipt:
    from .seed import parse_seed
    from .executor import execute_seed

    mandell = (getattr(intent, "mandel", "") or "").strip()
    action = (getattr(intent, "action", "") or "").strip()
    # DCC-III: semantic operation and typed arguments (through Mandell).
    semantic = f"{action}[{getattr(intent, 'term', '') or '?'}]"
    arguments = dict(getattr(intent, "args", None) or {})

    def _no_route(dell: Optional[int], error: str) -> RouteReceipt:
        return RouteReceipt(
            input=raw_line or "",
            mandell=mandell,
            semantic=semantic,
            arguments=arguments,
            action=action,
            dell=dell,
            routed=False,
            route="no-route",
            seed="",
            ok=False,
            messages=[],
            state_note="no state change (not routed)",
            error=error,
            new_program=None,
            requested_operation=action or "",
            resolved_operation="",
            authority=_AUTHORITY_ROUTER,
            affected_objects=[],
        )

    if not mandell:
        return _no_route(None, "empty Mandell composition — nothing to route")
    if not action or action == "unknown":
        return _no_route(None, f"unsupported action {action!r} — nothing to route")

    parsed = parse_seed(mandell)
    if not parsed.ok:
        return _no_route(None, f"Mandell parse failed: {parsed.error}")

    dell = parsed.primary_dell()
    corr = CORRESPONDENCE.get((action, dell))
    if corr is None:
        # SSI-I: generalized Core-II domain. Canonical identity via the
        # bridge resolver (operator_bridge.resolve); execution via the
        # existing chain_exec authority; Outcome V1 capture stays in the
        # route_intent wrapper (single capture — this path never nests
        # inside bridge.route(), which self-captures for direct API use).
        return _route_generalized(program, intent, parsed, action, dell,
                                  mandell, semantic, arguments, raw_line)

    seed = corr.build_seed(intent, parsed)
    try:
        result = execute_seed(program, seed)
    except Exception as exc:  # fail safe: report, do not propagate
        return RouteReceipt(
            input=raw_line or "",
            mandell=mandell,
            semantic=semantic,
            arguments=arguments,
            action=action,
            dell=dell,
            routed=False,
            route=f"{action}/{dell}",
            seed=seed,
            ok=False,
            messages=[],
            state_note="no state change (execution raised)",
            error=f"Dell execution raised: {exc}",
            new_program=None,
            requested_operation=action or "",
            resolved_operation=seed,
            authority=f"{_AUTHORITY_ROUTER} -> {_AUTHORITY_EXECUTOR}",
            affected_objects=[],
        )

    messages = list(result.get("messages") or [])
    ok = bool(result.get("ok", False))
    # State note derived from the Dell's own messages (actual evidence).
    state_note = "; ".join(
        m for m in messages
        if any(k in m for k in ("ideas=", "nursery=", "file=", "Nursery pending", "Ringed growth",
                                "Checkpoint", "Stamp:", "Form →", "Cycle x", "TokenCount", "PASS", "restored"))
    ) or ("executed" if ok else "failed")

    return RouteReceipt(
        input=raw_line or "",
        mandell=mandell,
        semantic=semantic,
        arguments=arguments,
        action=action,
        dell=dell,
        routed=True,
        route=f"{action}/{dell} [{corr.dell_name}]",
        seed=seed,
        ok=ok,
        messages=messages,
        state_note=state_note,
        error="" if ok else (result.get("error") or "Dell execution failed"),
        new_program=result.get("new_program"),
        requested_operation=action or "",
        resolved_operation=seed,
        authority=f"{_AUTHORITY_ROUTER} -> correspondence[{action}/{dell} {corr.dell_name}] -> {_AUTHORITY_EXECUTOR}",
        affected_objects=_affected_for(action, dell) if ok else [],
    )


def _route_generalized(program: Any, intent: Any, parsed: Any, action: str,
                       dell: Optional[int], mandell: str, semantic: str,
                       arguments: Dict[str, Any], raw_line: str = "") -> RouteReceipt:
    """SSI-I: generalized-domain fallback inside the canonical router.

    Consulted ONLY after the CORRESPONDENCE miss. Identity comes from the
    bridge resolver (operator_bridge.resolve); execution from the existing
    chain_exec authority. Fail-closed: unknown / ambiguous / blocked /
    Core-I-without-correspondence all refuse here with explicit reasons.
    Outcome V1 capture stays in the route_intent wrapper.
    """
    from .operator_bridge import resolve as bridge_resolve
    from .seed import parse_seed
    from .chain_exec import execute_chain

    term = (getattr(intent, "term", "") or "").strip() or None
    bres = bridge_resolve(action=action or None, dell=dell, term=term)
    if not bres.ok:
        # Preserve the historical refusal shape for the pure no-route case;
        # the bridge gives a more specific reason when it has one.
        reason = bres.refusal_reason or (
            f"no verified correspondence for ({action!r}, Dell {dell})"
            " — refusing to guess"
        )
        return RouteReceipt(
            input=raw_line or "", mandell=mandell, semantic=semantic,
            arguments=arguments, action=action, dell=dell,
            routed=False, route="no-route", seed="", ok=False,
            messages=[], state_note="no state change (not routed)",
            error=reason, new_program=None,
            requested_operation=action or "",
            resolved_operation="",
            authority=f"{_AUTHORITY_ROUTER} -> operator_bridge.resolve",
            affected_objects=[],
        )

    # bres.ok implies CORE_II accessible (resolve never returns ok for
    # Core-I without correspondence, blocked, or raw-only operators).
    label = (parsed.label or "").strip()
    seed_text = f"{bres.dell:02d}[{bres.name}]"
    if label:
        seed_text += f" :: {label}"
    seed = parse_seed(seed_text)
    if not seed.ok:
        return RouteReceipt(
            input=raw_line or "", mandell=mandell, semantic=semantic,
            arguments=arguments, action=action, dell=bres.dell,
            routed=False, route="no-route", seed="", ok=False,
            messages=[], state_note="no state change (not routed)",
            error=f"Mandell parse failed: {seed.error}", new_program=None,
        )
    try:
        out = execute_chain(program, seed, seed_text)
    except Exception as exc:  # fail safe: report, do not propagate
        return RouteReceipt(
            input=raw_line or "", mandell=seed_text,
            semantic=f"{action}[{bres.name}]", arguments=arguments,
            action=action, dell=bres.dell, routed=False,
            route=f"{action}/{bres.dell} [{bres.name}]", seed=seed_text,
            ok=False, messages=[],
            state_note="no state change (execution raised)",
            error=f"Dell execution raised: {exc}", new_program=None,
            requested_operation=action or "",
            resolved_operation=seed_text,
            authority=f"{_AUTHORITY_ROUTER} -> {_AUTHORITY_CHAIN}",
            affected_objects=[],
        )

    messages = list(out.get("messages") or [])
    ok = bool(out.get("ok", False))
    atom_results = [dict(r) for r in (out.get("atom_results") or []) if isinstance(r, dict)]
    # GDP-001 0.3.3: a ">" chain continues past a failed atom, so earlier
    # atoms may have mutated state. Report that explicitly — never silent
    # partial success.
    _oks = [bool(r.get("ok", True)) for r in atom_results]
    _partial = bool(atom_results) and any(_oks) and not all(_oks)
    state_note = "; ".join(messages[-3:]) if messages else ("executed" if ok else "failed")
    if _partial:
        state_note = (f"PARTIAL CHAIN: {sum(_oks)}/{len(_oks)} atoms completed; "
                      f"mutations from completed atoms persist; {state_note}")
    return RouteReceipt(
        input=raw_line or "", mandell=seed_text,
        semantic=f"{action}[{bres.name}]", arguments=arguments,
        action=action, dell=bres.dell, routed=True,
        route=f"{action}/{bres.dell} [{bres.name}]",
        seed=seed_text, ok=ok, messages=messages,
        state_note=state_note,
        error="" if ok else (out.get("error") or "Dell execution failed"),
        new_program=out.get("new_program"),
        requested_operation=action or "",
        resolved_operation=seed_text,
        authority=f"{_AUTHORITY_ROUTER} -> generalized[{action}/{bres.dell} {bres.name}] -> {_AUTHORITY_CHAIN}",
        affected_objects=[],
        atom_results=atom_results,
    )
