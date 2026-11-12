#!/usr/bin/env python3
"""LM-2 census build — export the confirmed LM-0 census to JSON.

The confirmed census (director-reports/LM0_CENSUS_CONFIRMED_2026-11-11.md,
sha256 c37adb098db942209b18e05ae9d9736fbee3b563532873f016a3474293da85c0)
is the small-word authority for LM-2: its words classify WHOLE and are
never morpheme-split. This generator parses the census markdown tables
under the eight confirmed category headings (# 1. LINK .. # 8. FOCUS)
and writes form/mandell/lm0_census_v1.json deterministically.

Unconfirmed material is excluded by construction: the SS1F reservoir is
prose (not a table) and is named UNCONFIRMED in the census itself; SS9
(MORPHEME SIDE) is not a small-word category. Multi-category membership
is law (R8): a word filed under several categories keeps every row.

    python -m form.lm2_census_build            # regenerate the artifact
    python -m form.lm2_census_build --check    # verify artifact == census
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
CENSUS_PATH = os.path.join(
    _ROOT, "director-reports", "LM0_CENSUS_CONFIRMED_2026-11-11.md")
OUT_PATH = os.path.join(_HERE, "mandell", "lm0_census_v1.json")

CATEGORIES = ["LINK", "POINT", "CONDITION", "NEGATE", "ASK",
              "OPERATOR", "FOCUS", "FLUFF"]
# Census heading order: # 6 is FLUFF, # 7 OPERATOR, # 8 FOCUS.
_HEADING = {"1": "LINK", "2": "POINT", "3": "CONDITION", "4": "NEGATE",
            "5": "ASK", "6": "FLUFF", "7": "OPERATOR", "8": "FOCUS"}


def parse_census(text: str):
    """Return (rows, per_category) where rows are dicts with
    word / category / meaning / section, in census order."""
    rows = []
    per_category = {c: 0 for c in CATEGORIES}
    current = None
    section = ""
    in_table = False
    for line in text.splitlines():
        m = re.match(r"^# (\d+)\.\s+([A-Z][A-Z-]*)", line)
        if m:
            name = _HEADING.get(m.group(1))
            current = name if name and m.group(2).startswith(name) else None
            in_table = False
            continue
        if line.startswith("# "):
            current = None
            in_table = False
            continue
        if line.startswith("## "):
            section = line[3:].strip()
            in_table = False
            continue
        if current is None:
            continue
        if re.match(r"^\|\s*candidate\s*\|", line):
            in_table = True
            continue
        if in_table:
            if re.match(r"^\|[\s:\-|]+\|$", line):
                continue
            if line.startswith("|"):
                cells = [c.strip() for c in line.split("|")]
                # cells: ['', candidate, meaning, source, notes, '']
                if len(cells) >= 4 and cells[1]:
                    rows.append({
                        "word": cells[1].lower(),
                        "category": current,
                        "meaning": cells[2],
                        "section": section,
                    })
                    per_category[current] += 1
            else:
                in_table = False
    return rows, per_category


def build_doc() -> dict:
    with open(CENSUS_PATH, "rb") as f:
        raw = f.read()
    sha = hashlib.sha256(raw).hexdigest()
    rows, per_category = parse_census(raw.decode("utf-8"))
    by_word = {}
    for row in rows:
        by_word.setdefault(row["word"], []).append(row)
    entries = []
    for word in sorted(by_word):
        wrows = sorted(by_word[word],
                       key=lambda r: CATEGORIES.index(r["category"]))
        entries.append({
            "word": word,
            "categories": sorted({r["category"] for r in wrows},
                                 key=CATEGORIES.index),
            "rows": [{"category": r["category"],
                      "meaning": r["meaning"],
                      "section": r["section"]} for r in wrows],
        })
    return {
        "header": {
            "artifact": "lm0_census_v1",
            "source": "director-reports/LM0_CENSUS_CONFIRMED_2026-11-11.md",
            "source_sha256": sha,
            "generated_by": "form/lm2_census_build.py",
            "rows": len(rows),
            "unique_words": len(entries),
            "per_category": per_category,
            "note": "Confirmed LM-0 census (Ace-confirmed 2026-11-11). "
                    "Multi-category membership is law (R8); the SS1F "
                    "reservoir is UNCONFIRMED and excluded.",
        },
        "entries": entries,
    }


def main() -> int:
    doc = build_doc()
    text = json.dumps(doc, indent=1, sort_keys=True,
                      ensure_ascii=False) + "\n"
    if "--check" in sys.argv:
        if not os.path.exists(OUT_PATH):
            print("MISSING artifact")
            return 1
        with open(OUT_PATH, encoding="utf-8") as f:
            current = f.read()
        ok = current == text
        print("CENSUS ARTIFACT", "MATCHES" if ok else "STALE")
        return 0 if ok else 1
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(text)
    h = doc["header"]
    print(f"wrote {OUT_PATH}: {h['rows']} rows, "
          f"{h['unique_words']} unique words, {h['per_category']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
