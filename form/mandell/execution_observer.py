#!/usr/bin/env python3
"""EOC-I: Execution observation adapter (NBD-Ω-005).

ONE observation boundary. This adapter WRAPS raw Mandell execution:

  raw Mandell > existing parser > existing execution >
  existing state changes/results > Outcome V1 observation

It is not an executor, router, ledger, or truth authority. It decides
nothing, modifies no operands, changes no routing, promotes no knowledge.

Capture ownership law (double-capture prevention):
- This adapter owns capture ONLY for the top-level raw executions it runs.
- Nested executions (chain Core-I leafs, Dell 99 inner compose, control
  bodies) call execute_seed/execute_chain directly — never this adapter —
  so they can never double-capture.
- route_intent (wrapper) and operator_bridge (self-capture) keep their own
  capture and never use this adapter.
- Projections (cheat_project), benchmarks (language.metrics), and replay
  never use this adapter, so they are never observed.
Double-capture is therefore impossible by construction, not by flag.

One record per top-level execution. Per-node fates ride in the existing
messages (no invented events). Provenance follows the existing DCC-XX-C1
identity rule; never fabricated.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class _RawReceipt:
    """Receipt-shaped evidence for capture_outcome (existing ledger)."""
    action: str = ""
    mandell: str = ""
    dell: Optional[int] = None
    semantic: str = ""
    input: str = ""
    routed: bool = False
    ok: bool = False
    error: str = ""
    messages: List[str] = field(default_factory=list)
    state_note: str = ""
    # ARGUS 3.3b: the raw path must not assert "no partial completion" for
    # executions that were partial. These mirror RouteReceipt's contract.
    atom_results: List[Dict[str, Any]] = field(default_factory=list)
    partial: bool = False


def _identity(seed_text: str):
    """Derive (action, dell, name) for the receipt without executing."""
    from .seed import parse_seed
    from . import registry

    parsed = parse_seed(seed_text or "")
    if not parsed.ok:
        return parsed, "parse", None, "parse"
    atoms = parsed.atoms or []
    primary = parsed.primary_dell()
    if len(atoms) == 1 and primary is not None:
        rec = registry.get_dell(int(primary)) or {}
        name = str(rec.get("name", "") or f"Dell{primary}")
        return parsed, name.lower(), int(primary), name
    return parsed, "chain", (int(primary) if primary is not None else None), "chain"


def _capture(program: Any, receipt: _RawReceipt, nurture_before: Any,
             interaction_id: Optional[str] = None) -> None:
    """Single Outcome V1 observation via the existing ledger. Never raises."""
    nurture_after = getattr(program, "last_nurture", None)
    nurture_fresh = (nurture_after is not nurture_before
                     and isinstance(nurture_after, dict))
    try:
        from .outcome_ledger import capture_outcome
        capture_outcome(program, receipt, nurture_fresh=nurture_fresh,
                        interaction_id=interaction_id)
    except Exception:
        pass


def observe_specialized_execution(
    program: Any,
    *,
    action: str,
    input_text: str,
    ok: bool,
    error: str = "",
    messages: Optional[List[str]] = None,
    semantic: str = "",
    interaction_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """SAOC-I: Observe a specialized execution authority (not via Dell).

    Wraps EXISTING specialized execution (e.g., English Create via
    parse_and_place/p.place) with Outcome V1 observation, without altering
    execution semantics. The caller has already executed; this function
    only captures the observation.

    Does NOT claim Dell execution. If the specialized authority did not
    use a Dell, dell=None and mandell="". Semantic similarity to a Dell
    is not execution identity.

    Returns the captured Outcome record, or None if capture failed.
    Never raises.
    """
    try:
        from .outcome_ledger import capture_outcome
        receipt = _RawReceipt(
            action=action or "",
            mandell="",  # Not fabricated: specialized authority did not use Mandell
            dell=None,   # Not fabricated: no Dell executed
            semantic=semantic or f"{action}[specialized]",
            input=input_text or "",
            routed=True,  # It did execute via specialized authority
            ok=bool(ok),
            error=error or "",
            messages=list(messages or []),
            state_note="specialized execution (not via Dell)",
        )
        return capture_outcome(program, receipt, interaction_id=interaction_id)
    except Exception:
        return None


def observe_seed_execution(program: Any, seed_text: str,
                          interaction_id: Optional[str] = None) -> Dict[str, Any]:
    """Execute raw Mandell with Outcome V1 observation (EOC-I adapter).

    Runs the EXISTING execute_seed front door (all paths: apply_core_i,
    21/22 live, leaf, chain). Captures exactly one Outcome V1 record via
    the existing ledger. Returns the execution result dict unchanged
    (observation never alters execution semantics).

    Parse failures are observed as non-execution records (routed=False),
    consistent with the routed contract. Raised exceptions are captured
    as failed and then re-raised (execution semantics preserved).

    ``interaction_id`` (EIC-I): optional explicit correlation to the
    interaction that caused this execution. None = UNKNOWN. This function
    ACCEPTS identity; it does not mint it.
    """
    from .seed import parse_seed

    raw = seed_text or ""
    parsed, action, dell, name = _identity(raw)
    nurture_before = getattr(program, "last_nurture", None)

    if not parsed.ok:
        out = {"ok": False, "error": parsed.error,
               "messages": [f"Seed error: {parsed.error}"]}
        _capture(program, _RawReceipt(
            action="parse", mandell=raw, dell=None, semantic="parse[?]",
            input=raw, routed=False, ok=False, error=parsed.error or "",
            messages=list(out["messages"]), state_note="not executed (parse failed)",
        ), nurture_before, interaction_id=interaction_id)
        return out

    from .executor import execute_seed
    try:
        out = execute_seed(program, raw)
    except Exception as exc:
        _capture(program, _RawReceipt(
            action=action, mandell=raw, dell=dell,
            semantic=f"{action}[{name}]", input=raw,
            routed=True, ok=False, error=f"execution raised: {exc}",
            messages=[f"execution raised: {exc}"],
            state_note="no state change (execution raised)",
        ), nurture_before, interaction_id=interaction_id)
        raise

    if not isinstance(out, dict):
        out = {"ok": False, "error": "non-dict result", "messages": []}
    messages = list(out.get("messages") or [])
    ok = bool(out.get("ok", False))
    error = str(out.get("error") or "")
    state_note = "; ".join(messages[-3:]) if messages else ("executed" if ok else "failed")
    # ARGUS 3.3b: carry the chain's atom results so the Outcome ledger does
    # not falsely record atom_results=[] / partial_completion=False.
    _atom_results = [dict(r) for r in (out.get("atom_results") or []) if isinstance(r, dict)]
    _oks = [bool(r.get("ok", True)) for r in _atom_results]
    _partial = bool(out.get("partial", False)) or (bool(_atom_results) and any(_oks) and not all(_oks))
    _capture(program, _RawReceipt(
        action=action, mandell=raw, dell=dell,
        semantic=f"{action}[{name}]", input=raw,
        routed=True, ok=ok, error=error if not ok else "",
        messages=messages, state_note=state_note,
        atom_results=_atom_results, partial=_partial,
    ), nurture_before, interaction_id=interaction_id)
    return out
