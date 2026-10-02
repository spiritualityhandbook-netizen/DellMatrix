#!/usr/bin/env python3
"""DCC-V: Natural English multi-step instruction -> Mandell program -> DCC-IV execution.

Architecture (no bypass):
  RAW ENGLISH
  > COMPOSITION INTERPRETATION (clause split + normalize)
  > ORDERED INTENTS (via existing translate())
  > MANDELL PROGRAM (compiled from Intent.mandel)
  > DCC-IV PARSER (parse_program validates BEFORE any execution)
  > DCC-IV EXECUTOR (execute_program)
  > SEMANTIC ROUTER (route_intent per node)
  > DELL AUTHORITY (execute_seed)

English constructs the Mandell program. It never bypasses it.
Compilation failure = zero Dells executed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .translate import translate, Intent
from .flow_executor import parse_program, execute_program, FlowReceipt

# Clause separators (word-boundary aware; not a naive split).
# Ordered longest-first to match "and then" before "then".
_CLAUSE_SEP = re.compile(r"\s*\b(?:and then|after that|then)\b\s*", re.IGNORECASE)

# Word numbers for cycle counts.
_WORD_NUM = {
    "once": 1, "twice": 2, "thrice": 3,
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
}


def _normalize_clause(clause: str) -> str:
    """Normalize a natural-English clause to a form translate() understands.

    This extends existing translate authority; it does not replace it.
    Only provable normalizations; ambiguous input is left for translate
    to reject honestly.
    """
    text = (clause or "").strip()
    if not text:
        return text
    lower = text.lower()

    # "cycle twice" / "cycle two times" -> "cycle 2"
    m = re.search(r"\bcycle\b(.*)", lower)
    if m:
        rest = m.group(1)
        for word, num in _WORD_NUM.items():
            if re.search(rf"\b{word}\b", rest):
                return f"cycle {num}"
        m2 = re.search(r"\b(\d+)\s*times?\b", rest)
        if m2:
            return f"cycle {m2.group(1)}"

    # "form a sphere" / "form the cube" -> "form sphere" / "form cube"
    m = re.search(r"\bform\s+(?:a\s+|an\s+|the\s+)?(cube|sphere|core|flower)\b", lower)
    if m:
        return f"form {m.group(1)}"

    # "stamp it created" / "stamp them xyz" -> "stamp created" / "stamp xyz"
    # "it"/"them" are placeholders; the Dell only needs the mark value.
    m = re.search(r"\b(stamp|mark)\s+(?:it\s+|them\s+)(.+)$", lower)
    if m:
        mark = m.group(2).strip()
        # Get original-case mark from text
        m_orig = re.search(r"\b(stamp|mark)\s+(?:it\s+|them\s+)(.+)$", text, re.IGNORECASE)
        mark_orig = m_orig.group(2).strip() if m_orig else mark
        return f"stamp {mark_orig}"

    # "discover my ideas" / "discover ideas" / "discover them" -> "discover"
    if re.search(r"\bdiscover\b", lower):
        # If it's just "discover" with trailing nouns, strip to "discover"
        if re.match(r"^\s*discover\s+(my\s+|the\s+)?(ideas?|them|it)\s*$", lower):
            return "discover"

    # "measure them" / "measure it" -> "measure"
    if re.match(r"^\s*measure\s+(them|it)\s*$", lower):
        return "measure"

    return text


def _split_clauses(english: str) -> List[str]:
    """Split English into clauses on sequencing connectors.

    Uses word-boundary regex (not str.split). A 'then' inside a word
    (e.g., 'thenable') does not split. Empty clauses are dropped.
    """
    parts = _CLAUSE_SEP.split(english)
    clauses = [p.strip() for p in parts if p.strip()]
    return clauses


@dataclass
class CompositeIntent:
    """Ordered intents compiled into one Mandell program."""
    english: str
    clauses: List[str]
    intents: List[Intent]
    flows: List[str]
    mandell: str  # The compiled Mandell program


@dataclass
class ComposeResult:
    ok: bool
    composite: CompositeIntent | None
    error: str = ""
    dells_executed: int = 0  # Always 0 on compile failure.


def compose_english(english: str) -> ComposeResult:
    """Compile English into a Mandell program. Zero Dells executed.

    Fails safely if any clause is unsupported, malformed, or ambiguous.
    """
    english = (english or "").strip()
    if not english:
        return ComposeResult(ok=False, composite=None, error="empty input")

    clauses = _split_clauses(english)
    if len(clauses) < 2:
        return ComposeResult(
            ok=False, composite=None,
            error="not a composition (need at least 2 clauses)",
        )

    intents: List[Intent] = []
    for idx, clause in enumerate(clauses):
        normalized = _normalize_clause(clause)
        intent = translate(normalized)
        if intent.action == "unknown":
            return ComposeResult(
                ok=False, composite=None,
                error=f"clause {idx+1} unsupported: {clause!r}",
            )
        # The Intent must have a valid Mandell composition.
        if not intent.mandel or "unknown" in intent.mandel.lower():
            return ComposeResult(
                ok=False, composite=None,
                error=f"clause {idx+1} malformed: {clause!r}",
            )
        intents.append(intent)

    # Compile to Mandell program.
    mandell_parts = [i.mandel for i in intents]
    flows = [">"] * (len(intents) - 1)
    mandell = " > ".join(mandell_parts)

    # Validate via DCC-IV parser BEFORE any execution (compile before execute).
    try:
        fp = parse_program(mandell)
    except ValueError as e:
        return ComposeResult(
            ok=False, composite=None,
            error=f"mandell compile failed: {e}",
        )

    # Verify the parsed structure matches our intents.
    if len(fp.nodes) != len(intents):
        return ComposeResult(
            ok=False, composite=None,
            error="node count mismatch after parse",
        )

    composite = CompositeIntent(
        english=english,
        clauses=clauses,
        intents=intents,
        flows=flows,
        mandell=mandell,
    )
    return ComposeResult(ok=True, composite=composite)


def execute_composite(program: Any, composite: CompositeIntent,
                      interaction_id: Optional[str] = None) -> FlowReceipt:
    """Execute a compiled CompositeIntent via DCC-IV.

    The Mandell program was already validated at compose time.

    ``interaction_id`` (EIC-I): forwarded to execute_program for per-node
    Outcome correlation.
    """
    fp = parse_program(composite.mandell)
    return execute_program(program, fp, interaction_id=interaction_id)


def format_composite_receipt(composite: CompositeIntent, receipt: FlowReceipt) -> str:
    """Format INPUT / MANDELL / FLOW / STEPs / FINAL."""
    from .flow_executor import format_receipt
    lines = []
    lines.append("INPUT:")
    lines.append(f"  {composite.english}")
    lines.append("MANDELL:")
    lines.append(f"  {composite.mandell}")
    lines.append("FLOW:")
    flow_names = []
    for f in composite.flows:
        flow_names.append("FlowTo" if f == ">" else "FlowThru")
    lines.append(f"  {' > '.join(flow_names) if flow_names else '(single)'}")
    lines.append("")
    # format_receipt repeats PROGRAM/FLOW; strip its header to avoid duplication.
    body = format_receipt(receipt)
    body_lines = body.split("\n")
    # Skip leading PROGRAM: and FLOW: sections (first 4 lines: PROGRAM, mandell, FLOW, flows, blank).
    if body_lines and body_lines[0].startswith("PROGRAM:"):
        # Find the blank line after FLOW section.
        idx = 0
        while idx < len(body_lines) and body_lines[idx].strip() != "":
            idx += 1
        body_lines = body_lines[idx + 1:]
    lines.append("\n".join(body_lines))
    return "\n".join(lines)
