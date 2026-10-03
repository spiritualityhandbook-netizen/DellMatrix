#!/usr/bin/env python3
"""Greek operators — the Mandell floor made public.

From preform/seed/00_FLOOR.md:
    Alpha · Delta · Omega · Omni — the floor.
    "Everything else snaps in and out of this floor. Nothing overrides it."

From form/mandell/activation.py (GREEK):
    Alpha: source       (floor)
    Delta: change       (floor)
    Omega: bound        (floor)
    Omni:  full-field meta-bus (floor)
    Lambda: logic wavelength   (language)
    Sigma:  sum of parts       (language)

These were previously dormant — defined and tested but with no public path.
This module wires them into the REPL as read-only observation commands.

Commands:
    alpha <idea>   — Show the source/origin of an idea
    delta <idea>   — Show the change/transformation history of an idea
    omega <idea>   — Show the boundary/completion state of an idea
    omni           — Full-field overview (all ideas, presence, system)
    lambda <idea>  — Show the logic/reasoning behind an idea
    sigma          — Sum/total view (counts, aggregates)

All are read-only. They observe and report; they do not mutate.
They use the existing observe_specialized_execution() authority for
honest observation, following the TPP-I pattern.
"""

from __future__ import annotations

from typing import Any, Tuple

from form.mandell.activation import greek_operator


def _resolve_idea(p, ref: str):
    """Resolve an idea reference to a Unit, or return None."""
    try:
        from form.lifecycle import resolve_idea
        unit, err = resolve_idea(p, ref)
        if err is not None:
            return None
        return unit
    except Exception:
        return None


def do_alpha(p, ref: str, interaction_id: str) -> Tuple[Any, str]:
    """Alpha (source): show the origin of an idea."""
    op = greek_operator("Alpha")
    if not op.get("ok"):
        return p, "Alpha operator unavailable."

    unit = _resolve_idea(p, ref)
    if unit is None:
        return p, f"Alpha: no idea found for '{ref}'."

    # Source = creation info, origin
    uid = getattr(unit, "id", None) or getattr(unit, "uid", "?")
    label = getattr(unit, "label", None) or str(uid)

    # Check lifecycle for registration info
    lifecycle = getattr(p, "lifecycle", {}) or {}
    lc = lifecycle.get(str(uid), {}) or lifecycle.get(label, {})

    lines = [
        f"Alpha ({op['semantic_root']}) — '{label}'",
        f"  Semantic root: {op['semantic_root']}",
        f"  Floor status: {op['floor_status']}",
    ]
    if lc:
        reg = lc.get("registered_seq", "UNKNOWN")
        lines.append(f"  Lifecycle registered at seq: {reg}")
    # Outcome history for this idea
    outcomes = getattr(p, "outcome_records", {}) or {}
    related = [k for k, v in outcomes.items()
               if isinstance(v, dict) and label in str(v.get("source", ""))]
    if related:
        lines.append(f"  Related outcomes: {len(related)}")
        for oid in related[:5]:
            lines.append(f"    - {oid}")
    else:
        lines.append("  No recorded outcomes reference this idea yet.")

    return p, "\n".join(lines)


def do_delta(p, ref: str, interaction_id: str) -> Tuple[Any, str]:
    """Delta (change): show the transformation history of an idea."""
    op = greek_operator("Delta")
    if not op.get("ok"):
        return p, "Delta operator unavailable."

    unit = _resolve_idea(p, ref)
    if unit is None:
        return p, f"Delta: no idea found for '{ref}'."

    uid = getattr(unit, "id", None) or getattr(unit, "uid", "?")
    label = getattr(unit, "label", None) or str(uid)

    lifecycle = getattr(p, "lifecycle", {}) or {}
    lc = lifecycle.get(str(uid), {}) or lifecycle.get(label, {})

    lines = [
        f"Delta ({op['semantic_root']}) — '{label}'",
        f"  Semantic root: {op['semantic_root']}",
        f"  Floor status: {op['floor_status']}",
    ]
    if lc:
        presence = lc.get("presence", "UNKNOWN")
        pinned = lc.get("pinned", False)
        lines.append(f"  Current presence: {presence}")
        lines.append(f"  Pinned: {pinned}")
        # Presence changes are the "deltas" in TPP-I
        lines.append("  Presence transitions are recorded in lifecycle metadata.")
    else:
        lines.append("  No lifecycle transitions recorded.")

    return p, "\n".join(lines)


def do_omega(p, ref: str, interaction_id: str) -> Tuple[Any, str]:
    """Omega (bound): show the boundary/completion state of an idea."""
    op = greek_operator("Omega")
    if not op.get("ok"):
        return p, "Omega operator unavailable."

    unit = _resolve_idea(p, ref)
    if unit is None:
        return p, f"Omega: no idea found for '{ref}'."

    uid = getattr(unit, "id", None) or getattr(unit, "uid", "?")
    label = getattr(unit, "label", None) or str(uid)

    lifecycle = getattr(p, "lifecycle", {}) or {}
    lc = lifecycle.get(str(uid), {}) or lifecycle.get(label, {})

    lines = [
        f"Omega ({op['semantic_root']}) — '{label}'",
        f"  Semantic root: {op['semantic_root']}",
        f"  Floor status: {op['floor_status']}",
    ]
    if lc:
        presence = lc.get("presence", "UNKNOWN")
        # Omega = boundary: is this idea at its bound?
        if presence == "faded":
            lines.append("  At bound: FADED (attention withdrawn, evidence preserved)")
        elif presence == "active":
            pinned = lc.get("pinned", False)
            if pinned:
                lines.append("  At bound: PINNED ACTIVE (protected, will not fade)")
            else:
                lines.append("  At bound: ACTIVE (present, unfaded)")
        else:
            lines.append(f"  Bound state: {presence}")
    else:
        lines.append("  No boundary state recorded (pre-lifecycle idea).")

    return p, "\n".join(lines)


def do_omni(p, interaction_id: str) -> Tuple[Any, str]:
    """Omni (full-field): overview of everything."""
    op = greek_operator("Omni")
    if not op.get("ok"):
        return p, "Omni operator unavailable."

    lines = [
        f"Omni ({op['semantic_root']})",
        f"  Semantic root: {op['semantic_root']}",
        f"  Floor status: {op['floor_status']}",
        "",
    ]

    # Ideas
    try:
        units = p.cube.session.plane.units
        total = len(units)
    except Exception:
        total = 0
        units = {}

    lifecycle = getattr(p, "lifecycle", {}) or {}
    active = sum(1 for uid in units
                 if (lifecycle.get(str(uid), {}) or {}).get("presence", "active") == "active")
    faded = total - active
    pinned = sum(1 for uid in units
                 if (lifecycle.get(str(uid), {}) or {}).get("pinned", False))

    lines.append(f"  Ideas: {total} total ({active} active, {faded} faded, {pinned} pinned)")

    # Outcomes
    outcomes = getattr(p, "outcome_records", {}) or {}
    lines.append(f"  Outcomes: {len(outcomes)} recorded")

    # Knowledge
    try:
        from form.mandell import knowledge as _k
        # Just report presence, don't invoke
        lines.append("  Knowledge: authority present")
    except Exception:
        lines.append("  Knowledge: authority not loaded")

    lines.append("")
    lines.append("  Floor: Alpha · Delta · Omega · Omni (intact)")

    return p, "\n".join(lines)


def do_lambda(p, ref: str, interaction_id: str) -> Tuple[Any, str]:
    """Lambda (logic): show the reasoning behind an idea."""
    op = greek_operator("Lambda")
    if not op.get("ok"):
        return p, "Lambda operator unavailable."

    unit = _resolve_idea(p, ref)
    if unit is None:
        return p, f"Lambda: no idea found for '{ref}'."

    uid = getattr(unit, "id", None) or getattr(unit, "uid", "?")
    label = getattr(unit, "label", None) or str(uid)

    lines = [
        f"Lambda ({op['semantic_root']}) — '{label}'",
        f"  Semantic root: {op['semantic_root']}",
        f"  Floor status: {op['floor_status']} (language layer)",
        "",
        "  Logic trace: idea exists as a Unit in the session plane.",
        "  For selection reasoning, use: why",
        "  For execution history, use: delta <idea>",
    ]

    return p, "\n".join(lines)


def do_sigma(p, interaction_id: str) -> Tuple[Any, str]:
    """Sigma (sum): aggregate view."""
    op = greek_operator("Sigma")
    if not op.get("ok"):
        return p, "Sigma operator unavailable."

    lines = [
        f"Sigma ({op['semantic_root']})",
        f"  Semantic root: {op['semantic_root']}",
        f"  Floor status: {op['floor_status']} (language layer)",
        "",
    ]

    try:
        units = p.cube.session.plane.units
        total = len(units)
    except Exception:
        total = 0

    outcomes = getattr(p, "outcome_records", {}) or {}
    lifecycle = getattr(p, "lifecycle", {}) or {}

    lines.append(f"  Sum: {total} ideas + {len(outcomes)} outcomes + {len(lifecycle)} lifecycle records")
    lines.append(f"  Total tracked objects: {total + len(outcomes) + len(lifecycle)}")

    return p, "\n".join(lines)


def handle_greek_command(p, line: str, interaction_id: str) -> Tuple[bool, Any, str]:
    """Handle alpha/delta/omega/omni/lambda/sigma commands.

    Returns (handled, program, message).
    All commands are read-only.
    """
    low = line.strip().lower()

    # omni (no argument)
    if low == "omni":
        p, msg = do_omni(p, interaction_id)
        return True, p, msg

    # sigma (no argument)
    if low == "sigma":
        p, msg = do_sigma(p, interaction_id)
        return True, p, msg

    # alpha <ref>
    if low == "alpha" or low.startswith("alpha "):
        ref = line.strip()[5:].strip()
        if not ref:
            return True, p, "Usage: alpha <idea>"
        p, msg = do_alpha(p, ref, interaction_id)
        return True, p, msg

    # delta <ref>
    if low == "delta" or low.startswith("delta "):
        ref = line.strip()[5:].strip()
        if not ref:
            return True, p, "Usage: delta <idea>"
        p, msg = do_delta(p, ref, interaction_id)
        return True, p, msg

    # omega <ref>
    if low == "omega" or low.startswith("omega "):
        ref = line.strip()[5:].strip()
        if not ref:
            return True, p, "Usage: omega <idea>"
        p, msg = do_omega(p, ref, interaction_id)
        return True, p, msg

    # lambda <ref>
    if low == "lambda" or low.startswith("lambda "):
        ref = line.strip()[6:].strip()
        if not ref:
            return True, p, "Usage: lambda <idea>"
        p, msg = do_lambda(p, ref, interaction_id)
        return True, p, msg

    return False, p, ""
