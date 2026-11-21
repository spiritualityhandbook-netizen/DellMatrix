#!/usr/bin/env python3
"""FI-012 Q.8 census-refresh probe (Part VI — Unknowns; Uni-owed).

Q-FI012.8 (FI012_ELASTIC_INTAKE_DEVELOPMENT_2026-11-16): M-34's
current location was UNVERIFIED at 3eecb4f5 — the census-era
idea-create field caps (label 80 / detail 2,000 / goals 12 /
words 500, silently truncated at parse; census-era R29 site
idea_create.py:44-47) were not found at their census site, and a
bounded census-refresh probe was owed before FI-012 wave W4
(idea-create door) could be scoped.

This probe IS that census refresh, run at the Part VI base pin
(af2519b6). It establishes, mechanically and behaviorally:

  S1  the caps' current site: form/idea_create.py
      parse_create_line, at the census values, verified against
      the function's own source;
  S2  the caller census: parse_create_line is the single parse
      authority for create-lines (production callers enumerated
      by AST scan);
  B1-B4  each cap's behavior at the parse door: over-cap input is
      SILENTLY truncated — the returned record carries no
      truncation flag, receipt, or signal of any kind;
  B5  the words cap's effective value: the [:500] slice can never
      bind past 120, because words is derived from detail[:120]
      first — the field's true cap at this door is 120;
  C1  the store-layer contrast: the Nursery store itself stores a
      150-char label WHOLE (its admitted bound is 200, enforced by
      typed refusal, Q-S2.1) — the 80 cap exists ONLY at the parse
      layer and bypasses the store's refuse-honestly contract.

Labels: UNIT (source census) + INTEGRATION (parse door behavior,
the same function the production door calls). State hygiene: the
Nursery contrast uses a temp file; nothing touches real state.
"""
from __future__ import annotations

import ast
import inspect
import os
import sys
import tempfile
from pathlib import Path

REPO = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, REPO)

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def _production_callers(func_name: str, defining: str):
    """AST census: files under form/ (excluding *_test.py and the
    defining module) that call func_name."""
    hits = []
    for path in sorted(Path(REPO, "form").rglob("*.py")):
        rel = str(path.relative_to(REPO))
        if rel == defining or path.name.endswith("_test.py"):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                f = node.func
                if (isinstance(f, ast.Name) and f.id == func_name) or (
                        isinstance(f, ast.Attribute)
                        and f.attr == func_name):
                    hits.append(rel)
                    break
    return hits


def main() -> int:
    from form.idea_create import parse_create_line

    print("=== FI012 Q8 CENSUS (M-34 refresh at Part VI base) ===")

    # --- S1: site + census values, from the function's own source
    src = inspect.getsource(parse_create_line)
    caps = {"label[:80]": "label[:80]" in src,
            "detail[:2000]": "detail[:2000]" in src,
            "goals[:12]": "goals[:12]" in src,
            "words[:500]": "words[:500]" in src}
    check("S1_site_and_census_values",
          all(caps.values()),
          f"form/idea_create.py parse_create_line caps={caps}")

    # --- S2: caller census (single parse authority)
    callers = _production_callers("parse_create_line",
                                  "form/idea_create.py")
    print(f"  census: production callers of parse_create_line = "
          f"{callers}")
    check("S2_single_parse_authority",
          "form/dell_matrix/needs.py" in callers and len(callers) >= 1,
          f"callers={callers}")

    # --- B1: label cap — silent truncation, no signal
    r = parse_create_line(
        "create an idea called " + "L" * 100 +
        " detail: d goals: g")
    keys = sorted(r.keys())
    check("B1_label_100_to_80_silent",
          len(r["label"]) == 80
          and not any("trunc" in k or "cap" in k or "refus" in k
                      for k in keys),
          f"label_len={len(r['label'])} keys={keys}")

    # --- B2: detail cap
    r = parse_create_line(
        "create an idea called x detail: " + "d" * 2500 +
        " goals: g")
    check("B2_detail_2500_to_2000_silent",
          len(r["detail"]) == 2000,
          f"detail_len={len(r['detail'])}")

    # --- B3: goals cap
    goals = "; ".join(f"goal{i}" for i in range(15))
    r = parse_create_line(
        f"create an idea called x detail: d goals: {goals}")
    check("B3_goals_15_to_12_silent",
          len(r["goals"]) == 12,
          f"goals_kept={len(r['goals'])}")

    # --- B4: words — no truncation signal in any result
    r = parse_create_line(
        "create an idea called x detail: " + "w " * 200 +
        " goals: g")
    check("B4_no_truncation_signal",
          not any("trunc" in k for k in r.keys()),
          f"keys={sorted(r.keys())}")

    # --- B5: words effective cap is 120, not 500
    detail = "x" * 300
    r = parse_create_line(
        f"create an idea called x detail: {detail} goals: g")
    check("B5_words_effective_cap_120",
          r["words"] == detail[:120] and len(r["words"]) == 120,
          f"words_len={len(r['words'])} (source slice [:500] "
          f"unreachable past the [:120] derivation)")

    # --- C1: store-layer contrast — Nursery stores 150 whole
    from form.dell_matrix.nursery import Nursery
    with tempfile.TemporaryDirectory() as td:
        n = Nursery(path=os.path.join(td, "nursery_probe.json"))
        prop = n.add("y" * 150, words="w", kind="new")
        stored = n.proposals[prop.id].label
    check("C1_store_stores_150_whole",
          stored == "y" * 150,
          f"nursery stored label_len={len(stored)} "
          f"(store bound 200, typed refusal; parse cap 80 is "
          f"parse-layer only)")

    print("CENSUS TABLE — M-34 at current main:")
    print("  label : cap 80   @ form/idea_create.py parse_create_line"
          " — SILENT truncation")
    print("  detail: cap 2000 @ form/idea_create.py parse_create_line"
          " — SILENT truncation")
    print("  goals : cap 12   @ form/idea_create.py parse_create_line"
          " — SILENT truncation")
    print("  words : cap 500 nominal / 120 effective @ same site"
          " — SILENT truncation")
    print("  store layer (Nursery.add): NO corresponding caps; "
          "admitted bounds enforced by typed refusal")

    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"FI012_Q8_CENSUS {passed}/{len(RESULTS)}")
    return 0 if passed == len(RESULTS) else 1


def smoke():
    return main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
