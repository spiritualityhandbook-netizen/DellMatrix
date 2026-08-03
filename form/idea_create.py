#!/usr/bin/env python3
"""Parse and validate idea create lines: label + detail + goals. Strong-idea law."""

from __future__ import annotations

from typing import Any, Dict, List
import re
import sys


def parse_create_line(raw: str) -> Dict[str, Any]:
    text = (raw or "").strip()
    m = re.search(
        r"(?:create(?:\s+an)?\s+idea(?:\s+called)?)\s+(.+)$",
        text,
        re.I,
    )
    body = m.group(1).strip() if m else text

    detail_m = re.search(r"\bdetail\s*:\s*(.+?)(?=\bgoals\s*:|$)", body, re.I | re.S)
    goals_m = re.search(r"\bgoals\s*:\s*(.+)$", body, re.I | re.S)

    detail = detail_m.group(1).strip(" |\n\t") if detail_m else ""
    goals: List[str] = []
    if goals_m:
        graw = goals_m.group(1).strip()
        goals = [g.strip() for g in re.split(r"[;,]|\band\b", graw) if g.strip()]

    label_part = re.split(r"\bdetail\s*:|\bgoals\s*:|\|", body, maxsplit=1, flags=re.I)[0].strip()
    label_part = re.sub(r"^(?:called\s+)", "", label_part, flags=re.I).strip()
    label = label_part.strip(" \"'") or "idea"

    words = detail[:120] if detail else ""

    missing = []
    if not detail:
        missing.append("detail")
    if not goals:
        missing.append("goals")

    strength = strength_score(detail, goals)

    return {
        "label": label[:80],
        "detail": detail[:2000],
        "goals": goals[:12],
        "words": words[:500],
        "complete": len(missing) == 0,
        "missing": missing,
        "strength": strength,
        "grade": grade_for(strength),
        "hint": (
            "Strong idea needs detail + goals, e.g.\n"
            "  create an idea called Code Evolution detail: post-Boolean decision shells "
            "goals: exhaust known shells; intuitive surface; honesty labels"
        ),
    }


def strength_score(detail: str, goals: List[str]) -> float:
    """0..1 — strong when detail is substantive and goals exist."""
    d = (detail or "").strip()
    g = [x for x in (goals or []) if str(x).strip()]
    if not d and not g:
        return 0.0
    ds = min(1.0, len(d) / 80.0) * 0.45
    gs = min(1.0, len(g) / 3.0) * 0.40
    words = len(re.findall(r"[a-zA-Z]{3,}", d))
    ws = min(1.0, words / 12.0) * 0.15
    return round(min(1.0, ds + gs + ws), 3)


def grade_for(score: float) -> str:
    if score >= 0.75:
        return "Strong"
    if score >= 0.45:
        return "Partial"
    if score > 0:
        return "Weak"
    return "Empty"


def slug_id(label: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", (label or "idea").lower()).strip("_")
    return (s[:40] or "idea")


def format_report(parsed: Dict[str, Any]) -> str:
    lines = [
        f"label:    {parsed.get('label')}",
        f"complete: {parsed.get('complete')}",
        f"strength: {parsed.get('strength')} ({parsed.get('grade')})",
        f"detail:   {(parsed.get('detail') or '—')[:120]}",
        f"goals:    {parsed.get('goals') or '—'}",
    ]
    if parsed.get("missing"):
        lines.append(f"missing:  {', '.join(parsed['missing'])}")
        lines.append(parsed.get("hint") or "")
    return "\n".join(lines)


def smoke() -> bool:
    print("=== IDEA CREATE SMOKE ===")
    r = []
    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}")
        r.append(bool(ok))
    p = parse_create_line(
        "create an idea called Code Evolution detail: post-Boolean shells "
        "goals: exhaust known; intuitive surface; honesty"
    )
    rec("complete", p["complete"] is True)
    rec("strongish", p["strength"] >= 0.45)
    rec("label", "Code Evolution" in p["label"] or p["label"].startswith("Code"))
    weak = parse_create_line("create an idea called OnlyName")
    rec("weak incomplete", weak["complete"] is False)
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


def main() -> None:
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    if "--check" in sys.argv:
        i = sys.argv.index("--check")
        raw = sys.argv[i + 1] if i + 1 < len(sys.argv) else ""
        print(format_report(parse_create_line(raw)))
        return
    print("Usage: python -m form.idea_create --check \"create an idea called X detail: … goals: …\"")


if __name__ == "__main__":
    main()
