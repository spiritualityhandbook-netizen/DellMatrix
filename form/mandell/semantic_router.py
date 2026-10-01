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
    """Honest execution receipt for a routing attempt."""

    input: str                    # raw user input
    mandell: str                  # Mandell composition from the Intent
    action: str                   # Intent action
    dell: Optional[int]           # primary Dell address parsed from composition
    routed: bool                  # whether a Dell was actually executed
    route: str                    # correspondence key or "no-route"
    seed: str                     # canonical seed executed ("" if none)
    ok: bool                      # execution ok (False if not routed or failed)
    messages: List[str] = field(default_factory=list)
    state_note: str = ""
    error: str = ""


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
}


def route_intent(program: Any, intent: Any, raw_line: str = "") -> RouteReceipt:
    """Route a Mandell Intent through the Dell execution authority.

    Returns a RouteReceipt that honestly reports what happened. If the
    Intent's Mandell composition does not parse, or the (action, dell)
    pair has no verified correspondence, NOTHING executes.
    """
    from .seed import parse_seed
    from .executor import execute_seed

    mandell = (getattr(intent, "mandel", "") or "").strip()
    action = (getattr(intent, "action", "") or "").strip()

    def _no_route(dell: Optional[int], error: str) -> RouteReceipt:
        return RouteReceipt(
            input=raw_line or "",
            mandell=mandell,
            action=action,
            dell=dell,
            routed=False,
            route="no-route",
            seed="",
            ok=False,
            messages=[],
            state_note="no state change (not routed)",
            error=error,
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
        return _no_route(
            dell,
            f"no verified correspondence for ({action!r}, Dell {dell}) — refusing to guess",
        )

    seed = corr.build_seed(intent, parsed)
    try:
        result = execute_seed(program, seed)
    except Exception as exc:  # fail safe: report, do not propagate
        return RouteReceipt(
            input=raw_line or "",
            mandell=mandell,
            action=action,
            dell=dell,
            routed=False,
            route=f"{action}/{dell}",
            seed=seed,
            ok=False,
            messages=[],
            state_note="no state change (execution raised)",
            error=f"Dell execution raised: {exc}",
        )

    messages = list(result.get("messages") or [])
    ok = bool(result.get("ok", False))
    # State note derived from the Dell's own messages (actual evidence).
    state_note = "; ".join(
        m for m in messages
        if any(k in m for k in ("ideas=", "nursery=", "file=", "Nursery pending", "Ringed growth"))
    ) or ("executed" if ok else "failed")

    return RouteReceipt(
        input=raw_line or "",
        mandell=mandell,
        action=action,
        dell=dell,
        routed=True,
        route=f"{action}/{dell} [{corr.dell_name}]",
        seed=seed,
        ok=ok,
        messages=messages,
        state_note=state_note,
        error="" if ok else (result.get("error") or "Dell execution failed"),
    )
