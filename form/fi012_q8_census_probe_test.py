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

UPDATE (2026-11-25, Director ruling 7166339462; PR #507 repair):
the census above is the dated historical record at the Part VI
base pin and stands. Two expectations were superseded by the
#522 / R24-L landing on main (labels carried losslessly; the
canonical 200-char budget enforced as a typed refusal BEFORE
placement at needs.parse_and_place, never by slicing):

  S1  the label leg of the source census no longer counts the
      literal text "label[:80]" — the landed source carries that
      string in a comment, which satisfied the old census while
      the behavior had already changed. The census now reads the
      function's AST: the returned record's label entry must be
      the unsliced name and no [:80] slice bound may exist in the
      function's code. The detail/goals/words caps are censused
      the same way (AST slice bounds, not text).
  B1  now tests the observable #522 contract at the normal entry
      point (needs.parse_and_place): a 100-char label is
      preserved whole through placement, and a 201-char label is
      refused (label_over_budget) before any placement.

All other census items (S2, B2-B5, C1) are unchanged: the
detail[:2000] / goals[:12] / words[:500] parse slices remain on
main by design. State hygiene extended: the entry-point legs use
a dedicated probe owner via form.open.open_program and never
save, so no state file is created.
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

    # --- S1: site + census values, from the function's own AST.
    # Post-#522 census (Director 7166339462): the old text census
    # counted the literal "label[:80]", which the landed source
    # carries in a comment — a comment satisfied it while the
    # behavior had already changed. The census now reads CODE:
    # slice bounds actually present in the function, plus the
    # shape of the returned record's label entry (must be the
    # unsliced name; the [:80] bound must not exist as code).
    fn_tree = ast.parse(inspect.getsource(parse_create_line))
    slice_uppers = set()
    label_is_unsliced_name = False
    for node in ast.walk(fn_tree):
        if (isinstance(node, ast.Subscript)
                and isinstance(node.slice, ast.Slice)
                and isinstance(node.slice.upper, ast.Constant)):
            slice_uppers.add(node.slice.upper.value)
        if isinstance(node, ast.Dict):
            for k, v in zip(node.keys, node.values):
                if (isinstance(k, ast.Constant)
                        and k.value == "label"):
                    label_is_unsliced_name = isinstance(v, ast.Name)
    caps = {"detail[:2000]": 2000 in slice_uppers,
            "goals[:12]": 12 in slice_uppers,
            "words[:500]": 500 in slice_uppers,
            "label_unsliced": label_is_unsliced_name
            and 80 not in slice_uppers}
    check("S1_site_and_census_values",
          all(caps.values()),
          f"form/idea_create.py parse_create_line caps={caps} "
          f"slice_uppers={sorted(slice_uppers)}")

    # --- S2: caller census (single parse authority)
    callers = _production_callers("parse_create_line",
                                  "form/idea_create.py")
    print(f"  census: production callers of parse_create_line = "
          f"{callers}")
    check("S2_single_parse_authority",
          "form/dell_matrix/needs.py" in callers and len(callers) >= 1,
          f"callers={callers}")

    # --- B1: label contract at the normal entry point (#522 /
    # R24-L, Director 7166339462). Historical pin (superseded):
    # B1_label_100_to_80_silent — parse_create_line sliced a
    # 100-char label to 80 with no signal. The landed contract:
    # the label is carried losslessly and the canonical budget
    # (200) is enforced by typed refusal BEFORE placement at
    # needs.parse_and_place. Both legs are tested here at that
    # entry point.
    from form.open import open_program
    from form.dell_matrix.needs import parse_and_place
    prog = open_program("FI012Q8PROBE")

    def _unit_labels():
        return [u.label for u in
                prog.cube.session.plane.units.values()]

    r = parse_create_line(
        "create an idea called " + "L" * 100 +
        " detail: d goals: g")
    res = parse_and_place(
        prog, "create an idea called " + "L" * 100 +
        " detail: d goals: g")
    check("B1_label_100_preserved_whole_at_entry",
          len(r["label"]) == 100
          and res.get("ok") is True
          and res.get("label") == "L" * 100
          and "L" * 100 in _unit_labels(),
          f"parse_len={len(r['label'])} ok={res.get('ok')} "
          f"placed_whole={'L' * 100 in _unit_labels()}")

    before = len(_unit_labels())
    res = parse_and_place(
        prog, "create an idea called " + "M" * 201 +
        " detail: d goals: g")
    check("B1b_label_201_refused_before_placement",
          res.get("ok") is False
          and res.get("error") == "label_over_budget"
          and len(_unit_labels()) == before,
          f"ok={res.get('ok')} error={res.get('error')} "
          f"units {before} -> {len(_unit_labels())}")

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
          f"(store bound 200, typed refusal; since #522 the parse "
          f"layer no longer slices the label either — see B1)")

    print("CENSUS TABLE — M-34 at current main:")
    print("  label : NO parse cap @ form/idea_create.py"
          " parse_create_line — carried losslessly; budget 200"
          " enforced by typed refusal at needs.parse_and_place"
          " (#522/R24-L; historical cap 80 silent slice superseded)")
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
