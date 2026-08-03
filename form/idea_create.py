#!/usr/bin/env python3
"""Parse and validate idea create lines: label + detail + goals."""

from __future__ import annotations

from typing import Any, Dict, List
import re


def parse_create_line(raw: str) -> Dict[str, Any]:
    """
    Patterns:
      create an idea called NAME detail: ... goals: a; b
      create idea NAME | detail: ... | goals: a, b
      create an idea called NAME
    """
    text = (raw or "").strip()
    lower = text.lower()
    label = ""
    detail = ""
    goals: List[str] = []
    words = ""

    # strip leading create boilerplate
    m = re.search(
        r"(?:create(?:\s+an)?\s+idea(?:\s+called)?)\s+(.+)$",
        text,
        re.I,
    )
    body = m.group(1).strip() if m else text

    # split on detail: / goals:
    detail_m = re.search(r"\bdetail\s*:\s*(.+?)(?=\bgoals\s*:|$)", body, re.I | re.S)
    goals_m = re.search(r"\bgoals\s*:\s*(.+)$", body, re.I | re.S)

    if detail_m:
        detail = detail_m.group(1).strip(" |\n\t")
    if goals_m:
        graw = goals_m.group(1).strip()
        goals = [g.strip() for g in re.split(r"[;,]|\band\b", graw) if g.strip()]

    # label = body before detail/goals markers
    label_part = body
    for sep in (" detail:", " Detail:", " DETAIL:", " | detail", " goals:", " Goals:"):
        idx = label_part.lower().find(sep.lower() if sep.strip() else sep)
        # simpler cut
    label_part = re.split(r"\bdetail\s*:|\bgoals\s*:|\|", body, maxsplit=1, flags=re.I)[0].strip()
    label_part = re.sub(r"^(?:called\s+)", "", label_part, flags=re.I).strip()
    label = label_part.strip(" \"'") or "idea"

    if detail and not words:
        words = detail[:120]

    missing = []
    if not detail:
        missing.append("detail")
    if not goals:
        missing.append("goals")

    return {
        "label": label[:80],
        "detail": detail[:2000],
        "goals": goals[:12],
        "words": words[:500],
        "complete": len(missing) == 0,
        "missing": missing,
        "hint": (
            "Add detail and goals, e.g.\n"
            "  create an idea called True Lore detail: deeper meanings of names and lore "
            "goals: teach patterns; honest research; loved name tool"
        ),
    }


def slug_id(label: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", (label or "idea").lower()).strip("_")
    return (s[:40] or "idea")
