#!/usr/bin/env python3
"""Parse and validate idea create lines: label + detail + goals. Strong-idea law."""

from __future__ import annotations

from typing import Any, Dict, List
import re
import sys


# FI-012 parse-door bounds (PR #507 remediation matrix rows 5-8;
# Director design choices 7066291209). These are the door's declared
# admission bounds: boundary-exact input passes with unaltered bytes,
# and every over-bound case refuses typed BEFORE anything is built —
# the historical label[:80] / detail[:2000] / goals[:12] slices
# silently destroyed authored content under a success report.
MAX_LABEL_CHARS = 80
MAX_DETAIL_CHARS = 2000
MAX_GOALS = 12
# The advertised words contract (7066291209 choice 1): words is the
# derivation of detail, lossless up to this declared bound. Beyond
# it, words carries the declared excerpt and the authored detail is
# preserved whole beside it in the same record, with the cap
# disclosed in the result (words_capped) — never a silent loss. The
# historical detail[:120] prefix made the effective cap 120 while
# the source advertised 500.
WORDS_DERIVATION_CHARS = 500


class IdeaCreateError(ValueError):
    """Typed refusal at the idea-create parse door (FI-012).

    Carries the refused field, the authored size and the supported
    bound so the composed public path can surface the refusal in its
    result (field / authored / bound / error) instead of reporting
    ok=True over partial content. A non-string input is refused with
    field="input" (authored/bound are None): malformed input is
    never silently reinterpreted as an empty idea and never crashes
    the door untyped.
    """

    def __init__(self, field: str, authored, bound, message: str):
        super().__init__(message)
        self.field = field
        self.authored = authored
        self.bound = bound


def _bound_refusal(field: str, authored: int, bound: int, unit: str) -> IdeaCreateError:
    return IdeaCreateError(
        field, authored, bound,
        f"{field} length {authored} exceeds the admitted bound of "
        f"{bound} {unit}; refused, nothing parsed")


def _split_goals(graw: str) -> List[str]:
    return [g.strip() for g in re.split(r"[;,]|\band\b", graw) if g.strip()]


def parse_create_line(raw: str) -> Dict[str, Any]:
    """Parse a create line into label / detail / goals.

    Marker law (FI-012 row 5): markers are recognized only in their
    ruled syntactic position. ``detail:`` opens the detail section.
    ``goals:`` is structural ONLY when it introduces the grammar's
    ruled goals form — a separator-delimited list (';' / ',' /
    'and'). A bare ``goals:`` token inside detail prose that
    introduces no delimited list is detail text, never structure:
    it manufactures no goals and no completeness verdict. (The
    disclosed other face: a single undelimited goal is likewise
    detail text, and the record honestly reports the idea
    incomplete, with the hint showing the delimited form.) Control
    characters in the label (the forged-line class) refuse typed.

    Raises IdeaCreateError on malformed input and on any field
    beyond its declared bound; returns the parsed record otherwise.
    """
    if not isinstance(raw, str):
        raise IdeaCreateError(
            "input", None, None,
            f"create line must be a string, not "
            f"{type(raw).__name__}; refused, nothing parsed")
    text = raw.strip()
    m = re.search(
        r"(?:create(?:\s+an)?\s+idea(?:\s+called)?)\s+(.+)$",
        text,
        re.I,
    )
    body = m.group(1).strip() if m else text

    detail_m = re.search(r"\bdetail\s*:\s*", body, re.I)
    goals_ms = list(re.finditer(r"\bgoals\s*:\s*", body, re.I))

    # The structural goals marker is the first candidate whose own
    # segment (up to the next marker or end of line) splits into a
    # delimited list of at least two goals.
    markers = sorted(
        [(mm.start(), mm.end(), "detail") for mm in [detail_m] if mm]
        + [(mm.start(), mm.end(), "goals") for mm in goals_ms])
    goals_span = None
    for i, (start, end, kind) in enumerate(markers):
        if kind != "goals":
            continue
        seg_end = markers[i + 1][0] if i + 1 < len(markers) else len(body)
        if len(_split_goals(body[end:seg_end])) >= 2:
            goals_span = (start, end)
            break

    if detail_m and goals_span and goals_span[0] > detail_m.start():
        detail = body[detail_m.end():goals_span[0]].strip(" |\n\t")
    elif detail_m:
        detail = body[detail_m.end():].strip(" |\n\t")
    else:
        detail = ""

    goals: List[str] = []
    if goals_span:
        g_end = detail_m.start() if (detail_m and detail_m.start() > goals_span[0]) \
            else len(body)
        goals = _split_goals(body[goals_span[1]:g_end])

    cuts = [len(body)]
    if detail_m:
        cuts.append(detail_m.start())
    if goals_span:
        cuts.append(goals_span[0])
    pipe = body.find("|")
    if pipe != -1:
        cuts.append(pipe)
    label_part = body[:min(cuts)].strip()
    label_part = re.sub(r"^(?:called\s+)", "", label_part, flags=re.I).strip()
    label = label_part.strip(" \"'") or "idea"

    # Typed refusals, before the record is built (row 7 / row 5).
    if any(ord(c) < 32 or ord(c) == 127 for c in label):
        raise IdeaCreateError(
            "label", len(label), None,
            "label contains control characters (forged-line class); "
            "refused, nothing parsed")
    if len(label) > MAX_LABEL_CHARS:
        raise _bound_refusal("label", len(label), MAX_LABEL_CHARS, "chars")
    if len(detail) > MAX_DETAIL_CHARS:
        raise _bound_refusal("detail", len(detail), MAX_DETAIL_CHARS, "chars")
    if len(goals) > MAX_GOALS:
        raise _bound_refusal("goals", len(goals), MAX_GOALS, "entries")

    words = detail[:WORDS_DERIVATION_CHARS] if detail else ""

    missing = []
    if not detail:
        missing.append("detail")
    if not goals:
        missing.append("goals")

    strength = strength_score(detail, goals)

    parsed = {
        "label": label,
        "detail": detail,
        "goals": goals,
        "words": words,
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
    if len(detail) > WORDS_DERIVATION_CHARS:
        # Preservation contract, disclosed: detail above is whole;
        # words is the declared-bound excerpt of it.
        parsed["words_capped"] = {
            "bound": WORDS_DERIVATION_CHARS,
            "authored": len(detail),
        }
    return parsed


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


def unique_unit_id(units: Any, label: str, *, prefix: str = "",
                   suffix_start: int = 1) -> str:
    """Canonical unique unit id for a label (P3/TD-5).

    The one slug + collision-dedup implementation: slug_id(label),
    with ``prefix`` prepended, collision-suffixed ``_n`` (n from
    ``suffix_start``) until the id is free in ``units``. Entry paths
    keep their prefixes and numbering conventions as parameters
    instead of re-implementing slug rules — before P3 the same label
    produced different ids depending on the door used (translate,
    executor_leaf, live_visual, live_identity each had a variant).
    No attempt cap: n strictly increases over a finite unit set, so
    the loop always terminates.
    """
    base = prefix + slug_id(label)
    uid = base
    n = suffix_start
    while uid in units:
        uid = f"{base}_{n}"
        n += 1
    return uid


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
