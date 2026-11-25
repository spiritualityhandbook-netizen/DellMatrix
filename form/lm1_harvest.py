#!/usr/bin/env python3
"""LM-1 HARVEST-ONLY table builder (build-time tooling only).

Authorized by Director mail 1a1cc55119b5979f (2026-11-11): ONE bounded
IN-REPO HARVEST-ONLY LM-1 build. NO external import -- the Wikipedia/
Wiktionary roots table is under a Q-LM1.1 HOLD and appears nowhere in
this tool's inputs or outputs.

Harvests ONLY in-repo sources:

  ace_seed      form/mandell/latinmandell.py ROOTS (53 surface roots)
  inrepo        form/mandell/morpheme.py typed PREFIXES/ROOTS/SUFFIXES
  inrepo_force  form/mandell/morpheme.py force_mandell_morphemes table
  inrepo_legacy src/core/mandel_ontology.js MORPHEMES (legacy layer,
                NOT the production runtime; labeled as such)
  candidate     preform/pages/21_AFFIX_LEXICON_STARTER.md (15 authored
                entries -> 16 piece rows; the combined cell
                "Man- / Mandel-" yields two pieces). CANDIDATES ONLY
                (Q-LM1.9): unconfirmed, gated by Leight/Loure.

Emits (deterministic: same sources -> same bytes):

  form/mandell/lm_table_v1.json            the versioned table (Q-LM1.8)
  form/mandell/lm_table_v1.collisions.json the collision log

Design law carried from the proposal (LM1_PROPOSAL_2026-11-11 SS3.4/4):
- Every row carries provenance {source_file, source_symbol}.
- Position conflicts stay QUARANTINED: pieces under an unruled
  conflict (dell / man / re; the alpha/delta/omega operator-vs-prefix
  family) ship with position_class == "position_unresolved" and
  conflict_status == "position_unresolved"; the AUTHORED position is
  preserved in authored_position_class. No existing first-match
  behavior in any module is changed by this tool or the table.
- Collisions (same normalized piece, differing position or sense)
  are ALL written to the collision log. Non-silent by construction:
  form/lm1_harvest_test.py recounts collisions independently and
  fails if the log and the recount disagree.
- NO bulk English examples (Q-LM1.10): senses are the in-repo
  authored glosses only; nothing is copied from any external work.
- Customs are runtime state, not source: they are NOT harvested.
  The loader documents that customs outrank every shipped stratum
  (precedence: customs > ace_seed > inrepo > inrepo_force >
  inrepo_legacy > candidate).

The source manifest lives INSIDE the table header (one artifact, one
hash): a sibling manifest file could drift from the table it
describes; an embedded manifest cannot be separated from it.

Run from the repository root:  python3 -m form.lm1_harvest
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

TOOL_VERSION = "lm1_harvest/1.0"
HARVEST_DATE = "2026-11-11"
TABLE_PATH = os.path.join(_HERE, "mandell", "lm_table_v1.json")
COLLISIONS_PATH = os.path.join(_HERE, "mandell",
                               "lm_table_v1.collisions.json")

PRECEDENCE = ["customs", "ace_seed", "inrepo", "inrepo_force",
              "inrepo_legacy", "candidate"]

# Pieces whose position is under an unruled conflict (proposal SS2.6;
# Q-LM1.3-Q-LM1.6). Quarantined, never guessed.
QUARANTINED = {"dell", "man", "re", "alpha", "delta", "omega"}

CENSUS_PATH = "director-reports/LM0_CENSUS_CONFIRMED_2026-11-11.md"
CENSUS_SHA256 = \
    "c37adb098db942209b18e05ae9d9736fbee3b563532873f016a3474293da85c0"

SOURCES = [
    ("form/mandell/latinmandell.py", "ROOTS"),
    ("form/mandell/morpheme.py", "PREFIXES/ROOTS/SUFFIXES + "
     "force_mandell_morphemes"),
    ("src/core/mandel_ontology.js", "MORPHEMES"),
    ("preform/pages/21_AFFIX_LEXICON_STARTER.md",
     "Starter prefixes / Starter suffixes"),
]


def _norm(piece: str) -> str:
    return (piece or "").strip().strip("-").lower()


def _sha256(path: str) -> str:
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def _row(piece, authored_form, position, language, sense, stratum,
         source_file, source_symbol, dell_ref=None, la=None,
         split=None, notes=""):
    return {
        "piece": piece,
        "authored_form": authored_form,
        "position_class": position,
        "authored_position_class": position,
        "language": language,
        "sense": sense,
        "dell_ref": dell_ref,
        "la": la,
        "split": split,
        "stratum": stratum,
        "provenance": {"source_file": source_file,
                       "source_symbol": source_symbol},
        "conflict_status": "clean",
        "notes": notes,
    }


def harvest_latinmandell() -> list:
    from form.mandell import latinmandell
    rows = []
    for word, entry in latinmandell.ROOTS.items():
        rows.append(_row(
            piece=_norm(word), authored_form=word,
            position="whole_form", language="Latin",
            sense=entry["sense"], stratum="ace_seed",
            source_file="form/mandell/latinmandell.py",
            source_symbol="ROOTS",
            dell_ref=entry.get("dell"), la=entry.get("la"),
            notes="Ace seed surface root; customs outrank at runtime."))
    return rows


def harvest_morpheme_typed() -> list:
    from form.mandell import morpheme
    rows = []
    for table, pos in ((morpheme.PREFIXES, "prefix"),
                       (morpheme.ROOTS, "root"),
                       (morpheme.SUFFIXES, "suffix")):
        for piece, sense in table.items():
            rows.append(_row(
                piece=_norm(piece), authored_form=piece,
                position=pos, language="project", sense=sense,
                stratum="inrepo",
                source_file="form/mandell/morpheme.py",
                source_symbol=pos.upper() + "ES" if pos == "prefix"
                else pos.upper() + "S"))
    return rows


def harvest_morpheme_force() -> list:
    src = open(os.path.join(_HERE, "mandell", "morpheme.py"),
               encoding="utf-8").read()
    tree = ast.parse(src)
    table = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and \
                node.name == "force_mandell_morphemes":
            for sub in ast.walk(node):
                if isinstance(sub, ast.Dict) and len(sub.keys) >= 10:
                    table = {k.value: v.value for k, v
                             in zip(sub.keys, sub.values)}
    if table is None:
        raise AssertionError("force table not found in morpheme.py")
    rows = []
    for word, split in table.items():
        rows.append(_row(
            piece=_norm(word), authored_form=word,
            position="whole_form", language="project", sense="",
            stratum="inrepo_force",
            source_file="form/mandell/morpheme.py",
            source_symbol="force_mandell_morphemes",
            split=split,
            notes="Whole-form forced split; carries a split, not a "
                  "sense (the split's pieces carry the senses)."))
    return rows


def harvest_ontology() -> list:
    path = os.path.join(_ROOT, "src", "core", "mandel_ontology.js")
    text = open(path, encoding="utf-8").read()
    block = text[text.index("MORPHEMES"):]
    block = block[:block.index("};")]
    groups = [
        ("latinPrefix", "prefix", "Latin"),
        ("latinRoot", "root", "Latin"),
        ("greek", "operator", "Greek"),
    ]
    rows = []
    for group, pos, lang in groups:
        seg = block[block.index(group):]
        seg = seg[:seg.index("}")]
        for form, sense in re.findall(r"'?([A-Za-z-]+)'?\s*:\s*'([^']+)'",
                                      seg):
            rows.append(_row(
                piece=_norm(form), authored_form=form,
                position=pos, language=lang, sense=sense,
                stratum="inrepo_legacy",
                source_file="src/core/mandel_ontology.js",
                source_symbol=f"MORPHEMES.{group}",
                notes="Legacy layer (src/ is not the production "
                      "runtime); evidence only."))
    return rows


def harvest_preform() -> list:
    path = os.path.join(_ROOT, "preform", "pages",
                        "21_AFFIX_LEXICON_STARTER.md")
    text = open(path, encoding="utf-8").read()
    rows = []
    section = None
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("## Starter prefixes"):
            section = ("prefix", "Starter prefixes")
            continue
        if s.startswith("## Starter suffixes"):
            section = ("suffix", "Starter suffixes")
            continue
        if section is None or not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 2 or cells[0] == "Affix" or \
                set(cells[0]) <= set("- "):
            continue
        pos, symbol = section
        path_note = cells[2] if len(cells) > 2 and cells[2] else ""
        for form in cells[0].split("/"):
            rows.append(_row(
                piece=_norm(form), authored_form=form.strip(),
                position=pos, language="project", sense=cells[1],
                stratum="candidate",
                source_file="preform/pages/21_AFFIX_LEXICON_STARTER.md",
                source_symbol=symbol,
                notes="CANDIDATE ONLY (Q-LM1.9): NOT IN USE preform "
                      "material; admission gated by Leight/Loure + "
                      "Architect confirm."
                      + (f" Admission path: {path_note}."
                         if path_note else "")))
    return rows


def apply_quarantine(rows: list) -> None:
    for row in rows:
        if row["piece"] in QUARANTINED:
            row["position_class"] = "position_unresolved"
            row["conflict_status"] = "position_unresolved"


def compute_collisions(rows: list) -> list:
    groups = {}
    for row in rows:
        groups.setdefault(row["piece"], []).append(row)
    out = []
    for piece in sorted(groups):
        grows = groups[piece]
        if len(grows) < 2:
            continue
        keys = {(g["position_class"], g["sense"]) for g in grows}
        if len(keys) <= 1:
            continue
        best = min(grows, key=lambda g: PRECEDENCE.index(g["stratum"]))
        out.append({
            "piece": piece,
            "rows": [
                {"stratum": g["stratum"],
                 "authored_position_class": g["authored_position_class"],
                 "position_class": g["position_class"],
                 "sense": g["sense"],
                 "source_file": g["provenance"]["source_file"]}
                for g in sorted(
                    grows,
                    key=lambda g: PRECEDENCE.index(g["stratum"]))],
            "precedence_outcome":
                "No runtime change: existing module behavior is "
                "untouched by the table. Table annotation only: "
                f"highest-precedence shipped stratum = "
                f"{best['stratum']} (a runtime custom, if bound, "
                "outranks every shipped stratum). "
                "position_unresolved pieces are excluded from "
                "position-dependent consumption until an authority "
                "rules (Q-LM1.3-Q-LM1.6).",
        })
    return out


def build() -> dict:
    rows = []
    rows += harvest_latinmandell()
    rows += harvest_morpheme_typed()
    rows += harvest_morpheme_force()
    rows += harvest_ontology()
    rows += harvest_preform()
    apply_quarantine(rows)
    rank = {s: i for i, s in enumerate(PRECEDENCE)}
    rows.sort(key=lambda r: (r["piece"], rank[r["stratum"]],
                             r["authored_position_class"]))
    collisions = compute_collisions(rows)
    collided = {c["piece"] for c in collisions}
    for row in rows:
        if row["piece"] in collided and \
                row["conflict_status"] == "clean":
            row["conflict_status"] = "collision_logged"

    per_stratum = {}
    for row in rows:
        per_stratum[row["stratum"]] = per_stratum.get(row["stratum"], 0) + 1

    manifest_sources = []
    for rel, symbol in SOURCES:
        manifest_sources.append({
            "path": rel, "symbol": symbol,
            "sha256": _sha256(os.path.join(_ROOT, rel))})
    census_abs = os.path.join(_ROOT, CENSUS_PATH)
    census_sha = _sha256(census_abs) if os.path.exists(census_abs) \
        else None
    if census_sha != CENSUS_SHA256:
        raise AssertionError(
            f"census anchor mismatch: {census_sha} != {CENSUS_SHA256} "
            "-- the LM-1 build is contingent on the byte-verified "
            "Ace-confirmed census being published first")

    header = {
        "table": "lm_table",
        "version": 1,
        "generated_by": TOOL_VERSION,
        "harvest_date": HARVEST_DATE,
        "authorization": "Director mail 1a1cc55119b5979f (2026-11-11): "
                         "ONE bounded in-repo HARVEST-ONLY LM-1 build; "
                         "external import HELD (Q-LM1.1)",
        "precedence": PRECEDENCE,
        "precedence_note": "Customs are runtime state (persist v7), "
                           "never harvested; a bound custom outranks "
                           "every shipped stratum. lookup() returns "
                           "the full row set -- never a silent "
                           "first-match.",
        "coverage": {
            "harvested_rows": len(rows),
            "per_stratum": per_stratum,
            "external_rows_not_imported": 1693,
            "external_note": "The 1,693-row Wikipedia roots table "
                             "was NOT imported (Q-LM1.1 HOLD; no "
                             "license decision). This table covers "
                             "in-repo material only.",
            "collision_pieces": len(collisions),
            "quarantined_pieces": sorted(QUARANTINED),
        },
        "manifest": {
            "sources": manifest_sources,
            "census_anchor": {"path": CENSUS_PATH,
                              "sha256": census_sha},
        },
    }
    return {"header": header, "rows": rows,
            "collisions": collisions}


def main() -> int:
    built = build()
    table_doc = {"header": built["header"], "rows": built["rows"]}
    with open(TABLE_PATH, "w", encoding="utf-8") as f:
        json.dump(table_doc, f, ensure_ascii=False, indent=1,
                  sort_keys=True)
        f.write("\n")
    with open(COLLISIONS_PATH, "w", encoding="utf-8") as f:
        json.dump(built["collisions"], f, ensure_ascii=False,
                  indent=1, sort_keys=True)
        f.write("\n")
    print(f"lm1_harvest: {len(built['rows'])} rows, "
          f"{len(built['collisions'])} collision pieces -> "
          f"{TABLE_PATH}, {COLLISIONS_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
