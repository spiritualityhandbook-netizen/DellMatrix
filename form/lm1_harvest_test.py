"""LM-1 HARVEST-ONLY build — probes P1/P3-P8 (Director authorization
mail 1a1cc55119b5979f, 2026-11-11; proposal director-reports/
LM1_PROPOSAL_2026-11-11.md SS4c adapted to the harvest-only subset).

Contracts proven here:

- P1 HARVEST RECONCILE: the shipped table's per-stratum row counts
  equal INDEPENDENT recounts of each in-repo source, executed in
  this test from the sources themselves (never read off the table).
- P3 PROVENANCE COMPLETE: every row carries provenance
  {source_file, source_symbol}; the table header's source manifest
  pins each source file by sha256 matching the file on disk; NO
  wikimedia/wikipedia/wiktionary source appears anywhere (the
  Q-LM1.1 external-import HOLD is structural, not a comment).
- P4 COLLISION LOG COMPLETE: the set of pieces in the shipped
  collision log equals the set an independent recount computes
  from the table rows (same normalized piece, differing position
  or sense). Non-silent by construction.
- P5 NO SILENT FIRST-MATCH: lm_table.lookup() returns the FULL
  row set for a piece, annotated with precedence ranks; the
  precedence order is documented with customs first (customs are
  runtime state and outrank every shipped stratum).
- P6 POSITION QUARANTINE: every row for a quarantined piece
  (dell / man / re, plus the alpha/delta/omega role-conflict
  family) carries position_class == position_unresolved and
  conflict_status == position_unresolved. No guessed positions.
- P7 ABSENT TABLE = TODAY'S BEHAVIOR: with the table path pointed
  at a missing file, the loader returns an empty table without
  raising; latinmandell / morpheme behavior spot checks match the
  pre-build baseline exactly (deepen drops unresolved silently
  TODAY -- that is the pinned current behavior, not an LM-1 fix;
  morpheme first-match sense for "re" unchanged).
- P8 HONEST COVERAGE: the table header states the harvested totals
  per stratum AND that the 1,693-row external table was NOT
  imported (Q-LM1.1 HOLD). Coverage is printed, never implied.
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

QUARANTINED = ("dell", "man", "re", "alpha", "delta", "omega")
EXTERNAL_TOKENS = ("wikimedia", "wikipedia", "wiktionary")


def _norm(piece: str) -> str:
    return (piece or "").strip().strip("-").lower()


# ------------------------------------------------------------------
# Independent recounts (from the sources, not the table)
# ------------------------------------------------------------------

def recount_latinmandell() -> int:
    from form.mandell import latinmandell
    return len(latinmandell.ROOTS)


def recount_morpheme_typed() -> dict:
    from form.mandell import morpheme
    return {
        "prefix": len(morpheme.PREFIXES),
        "root": len(morpheme.ROOTS),
        "suffix": len(morpheme.SUFFIXES),
    }


def recount_morpheme_force() -> int:
    src = open(os.path.join(_HERE, "mandell", "morpheme.py"),
               encoding="utf-8").read()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and \
                node.name == "force_mandell_morphemes":
            for sub in ast.walk(node):
                if isinstance(sub, ast.Dict) and len(sub.keys) >= 10:
                    return len(sub.keys)
    raise AssertionError("force table not found")


def recount_ontology() -> int:
    path = os.path.join(_ROOT, "src", "core", "mandel_ontology.js")
    text = open(path, encoding="utf-8").read()
    block = text[text.index("MORPHEMES"):]
    block = block[:block.index("};")]
    return len(re.findall(r"'[^']+'\s*:", block)) + \
        len(re.findall(r"\b(Alpha|Delta|Lambda|Sigma|Omega)\s*:", block))


def recount_preform_pieces() -> int:
    """Count authored ROWS (15 table entries; the combined cell
    'Man- / Mandel-' expands to 2 piece rows -> 16). A piece that
    appears in both tables (dell, man) is two authored rows, so
    this counts rows, not unique spellings."""
    path = os.path.join(_ROOT, "preform", "pages",
                        "21_AFFIX_LEXICON_STARTER.md")
    text = open(path, encoding="utf-8").read()
    n = 0
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2 or cells[0] in ("Affix",) or \
                set(cells[0]) <= set("- "):
            continue
        for form in cells[0].split("/"):
            if _norm(form):
                n += 1
    return n


# ------------------------------------------------------------------
# smoke
# ------------------------------------------------------------------

def smoke() -> bool:
    print("=== LM-1 HARVEST SMOKE ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}"
              + (f" -- {detail}" if detail and not ok else ""))
        r.append(bool(ok))

    from form.mandell import lm_table

    table = lm_table.load_table()
    rows = table["rows"]
    header = table["header"]

    # ---- P1: counts reconcile against independent recounts
    lm_n = recount_latinmandell()
    typed = recount_morpheme_typed()
    force_n = recount_morpheme_force()
    onto_n = recount_ontology()
    pre_n = recount_preform_pieces()
    by_stratum = {}
    for row in rows:
        by_stratum[row["stratum"]] = by_stratum.get(row["stratum"], 0) + 1
    rec("P1 ace_seed count == latinmandell ROOTS recount",
        by_stratum.get("ace_seed") == lm_n,
        f"{by_stratum.get('ace_seed')} != {lm_n}")
    rec("P1 inrepo count == morpheme typed recount",
        by_stratum.get("inrepo") == sum(typed.values()),
        f"{by_stratum.get('inrepo')} != {sum(typed.values())}")
    typed_by_pos = {}
    for row in rows:
        if row["stratum"] == "inrepo":
            authored = row.get("authored_position_class") \
                or row["position_class"]
            typed_by_pos[authored] = typed_by_pos.get(authored, 0) + 1
    rec("P1 inrepo authored position split == typed recount (24/19/11)",
        typed_by_pos == typed, f"{typed_by_pos} != {typed}")
    rec("P1 inrepo_force count == force table recount",
        by_stratum.get("inrepo_force") == force_n,
        f"{by_stratum.get('inrepo_force')} != {force_n}")
    rec("P1 inrepo_legacy count == ontology recount",
        by_stratum.get("inrepo_legacy") == onto_n,
        f"{by_stratum.get('inrepo_legacy')} != {onto_n}")
    rec("P1 candidate count == preform piece recount",
        by_stratum.get("candidate") == pre_n,
        f"{by_stratum.get('candidate')} != {pre_n}")
    expected_total = lm_n + sum(typed.values()) + force_n + onto_n + pre_n
    rec("P1 total rows == sum of recounts",
        len(rows) == expected_total, f"{len(rows)} != {expected_total}")

    # ---- P3: provenance + manifest + no external source
    prov_ok = all(
        row.get("provenance", {}).get("source_file")
        and row.get("provenance", {}).get("source_symbol")
        for row in rows)
    rec("P3 every row carries provenance {source_file, source_symbol}",
        prov_ok)
    manifest = header.get("manifest", {})
    sources = manifest.get("sources", [])
    hash_ok = bool(sources)
    for entry in sources:
        p = os.path.join(_ROOT, entry["path"])
        if not os.path.exists(p):
            hash_ok = False
            break
        digest = hashlib.sha256(open(p, "rb").read()).hexdigest()
        if digest != entry["sha256"]:
            hash_ok = False
            break
    rec("P3 manifest source sha256 pins match files on disk", hash_ok)
    # The HOLD is structural: no row's provenance, no manifest
    # source, and no stratum may reference an external source.
    # (Header prose NAMING the held table to record the HOLD is
    # honest documentation, not a source.)
    source_refs = []
    for row in rows:
        source_refs.append(row["provenance"]["source_file"].lower())
        source_refs.append(row["stratum"].lower())
    for entry in sources:
        source_refs.append(entry["path"].lower())
    rec("P3 no external (wikimedia/wikipedia/wiktionary) source anywhere",
        not any(tok in ref for ref in source_refs
                for tok in EXTERNAL_TOKENS))

    # ---- P4: collision log completeness vs independent recount
    groups = {}
    for row in rows:
        groups.setdefault(_norm(row["piece"]), []).append(row)
    expected_collisions = set()
    for piece, grows in groups.items():
        if len(grows) < 2:
            continue
        keys = {(g["position_class"], g["sense"]) for g in grows}
        if len(keys) > 1:
            expected_collisions.add(piece)
    logged = {_norm(e["piece"]) for e in lm_table.load_collisions()}
    rec("P4 collision log == independent collision recount",
        logged == expected_collisions,
        f"logged-only={sorted(logged - expected_collisions)} "
        f"recount-only={sorted(expected_collisions - logged)}")

    # ---- P5: lookup returns the full set, customs documented first
    rec("P5 precedence documented with customs first",
        lm_table.PRECEDENCE[0] == "customs"
        and "customs" in json.dumps(header).lower())
    dell_rows = lm_table.lookup("dell")
    rec("P5 lookup('dell') returns the full row set (>=3 strata rows)",
        len(dell_rows) >= 3
        and len(dell_rows) == len(groups.get("dell", [])),
        f"got {len(dell_rows)}")
    ranks = [d["precedence_rank"] for d in dell_rows]
    rec("P5 lookup rows carry precedence ranks, best first",
        ranks == sorted(ranks) and len(set(ranks)) >= 2)

    # ---- P6: position quarantine
    quar_ok = True
    for piece in QUARANTINED:
        for row in groups.get(piece, []):
            if row["position_class"] != "position_unresolved" or \
                    row["conflict_status"] != "position_unresolved":
                quar_ok = False
    rec("P6 quarantined pieces carry position_unresolved everywhere",
        quar_ok)
    rec("P6 quarantine set is non-empty in the table (dell/man/re present)",
        all(p in groups for p in ("dell", "man", "re")))

    # ---- P7: absent table = today's behavior; baseline spot checks
    missing = lm_table.load_table(
        path=os.path.join(_HERE, "mandell", "lm_table_v1.MISSING.json"))
    rec("P7 absent table loads empty without raising",
        missing["rows"] == [] and missing["header"] is None)
    from form.mandell import latinmandell, morpheme
    latinmandell.clear_customs()
    deep = latinmandell.deepen("anchor the law and keep the trace")
    rec("P7 baseline: deepen resolves only 'keep' (pre-build behavior)",
        [d["word"] for d in deep] == ["keep"])
    keep = latinmandell.root_of("keep")
    rec("P7 baseline: root_of('keep') == servare / dell 10",
        keep is not None and keep["la"] == "servare"
        and keep["dell"] == 10)
    rec("P7 baseline: morpheme first-match sense for 're' unchanged",
        morpheme.sense_of("re") == morpheme.PREFIXES["re"])
    rec("P7 baseline: morpheme.smoke() and latinmandell.smoke() pass",
        morpheme.smoke() and latinmandell.smoke())

    # ---- P8: honest coverage stated in the header
    cov = header.get("coverage", {})
    rec("P8 header states external table NOT imported (1693 rows held)",
        cov.get("external_rows_not_imported") == 1693
        and cov.get("harvested_rows") == len(rows))
    print(f"    P8 coverage: harvested {len(rows)} rows in "
          f"{len(by_stratum)} strata {by_stratum}; external 1693-row "
          f"table NOT imported (Q-LM1.1 HOLD)")

    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
