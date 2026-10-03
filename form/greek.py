#!/usr/bin/env python3
"""Greek operators — the Mandell floor made public (C1 corrected).

NBD-Ω-050-C1: Semantic authority correction.

The rejected implementation invented operational meanings not established
by canonical authority (transformation history, bound/completion equivalence,
logic traces, aggregate formulas). This correction removes all unsupported
semantic claims.

What remains is truthful and minimal:

Each operator exposes, at runtime, from canonical authority:
    NAME, SCOPE, SEMANTIC_ROOT, FLOOR_STATUS

Canonical authority: form/mandell/activation.py (GREEK dict, greek_operator()).
Historical authority: preform/seed/00_FLOOR.md (floor membership).

Omni additionally reuses the existing canonical omni_report() — the system's
own defined Omni representation. No invented Omni semantics.

No operator takes an operand. No canonical or historical evidence establishes
an operand contract for any Greek operator. Bare operator commands only.

All commands are read-only. They do not modify Program, create Outcomes,
touch lifecycle, knowledge, Dells, persistence, or execution authority.
"""

from __future__ import annotations

from typing import Any, Tuple

from form.mandell.activation import greek_operator, omni_report

# The six public operators. Order: floor first, then language.
OPERATORS = ("alpha", "delta", "omega", "omni", "lambda", "sigma")


def _canonical_name(cmd: str) -> str:
    """Map lowercase command to canonical operator name."""
    return {"alpha": "Alpha", "delta": "Delta", "omega": "Omega",
            "omni": "Omni", "lambda": "Lambda", "sigma": "Sigma"}[cmd]


def describe_operator(cmd: str) -> Tuple[bool, str]:
    """Return (ok, message) describing the operator from canonical authority.

    For omni, appends the existing canonical omni_report() contents.
    No invented semantics. No operands.
    """
    name = _canonical_name(cmd)
    op = greek_operator(name)
    if not op.get("ok"):
        return False, f"{name} operator unavailable."

    lines = [
        f"{op['name']}",
        f"  Scope: {op['scope']}",
        f"  Semantic root: {op['semantic_root']}",
        f"  Floor status: {op['floor_status']}",
    ]

    if cmd == "omni":
        # Reuse existing canonical Omni representation. Display truthfully.
        try:
            rep = omni_report()
            lines.append("")
            lines.append("  Canonical omni report:")
            lines.append(f"    Floor: {', '.join(rep.get('floor', []))}")
            dells = rep.get("dells", {})
            lines.append(f"    Dells: {dells.get('count', '?')} "
                         f"(range {dells.get('min', '?')}-{dells.get('max', '?')})")
            lines.append(f"    Cells defined: {len(rep.get('cells', []))}")
            lines.append(f"    Nova mode: {rep.get('nova', '?')}")
            oc = rep.get("open_circuits", [])
            if oc:
                lines.append(f"    Open circuits: {', '.join(oc)}")
        except Exception as e:
            lines.append(f"  (omni_report unavailable: {e})")

    return True, "\n".join(lines)


def handle_greek_command(p, line: str, interaction_id: str) -> Tuple[bool, Any, str]:
    """Handle bare Greek operator commands.

    Returns (handled, program, message).
    All commands are read-only. No operands supported.
    """
    stripped = line.strip()
    low = stripped.lower()

    # Bare operator only. No operand contract exists.
    if low in OPERATORS:
        ok, msg = describe_operator(low)
        return True, p, msg

    # Operator with arguments: not supported, say so truthfully.
    first = low.split()[0] if low.split() else ""
    if first in OPERATORS:
        name = _canonical_name(first)
        return True, p, (
            f"Usage: {first}\n"
            f"{name} takes no operand. "
            f"No operand contract is established for Greek operators."
        )

    return False, p, ""
