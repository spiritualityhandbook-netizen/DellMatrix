"""LM-2 THE SPLITTER — contracts for morpheme.split_word (LatinMandell
plan SS15, circuit LM-2; grounding hidden_files/lm2/GROUNDING.md).

Contracts proven here:

- BEFORE -> AFTER: explain_morphemes() returned ONE opaque part for
  ordinary English (transportation / incredible / preview /
  unbelievable: sense '(open)', known False) and split_word did not
  exist. split_word now returns a structured parse wherever the LM-1
  harvested table supports one -- and an honest UNRESOLVED parse
  where it does not (incredible / unbelievable contain no harvested
  piece: in-/un-/cred/believ were never harvested, so the splitter
  fabricates nothing).
- CENSUS WHOLE: a confirmed LM-0 census word classifies WHOLE with
  ALL its categories (multi-category is law, R8) and is never split.
  The shipped census artifact pins the confirmed edition by sha256.
- NO SILENT FIRST-MATCH: a piece's senses are the FULL lm_table
  row set with stratum + precedence annotation; quarantined pieces
  (dell / man / re / alpha / delta / omega) annotate
  position_unresolved instead of picking a winner.
- HONEST SCORES: every parse exposes ACCOUNTED (resolved chars /
  total chars) and MORPHEME-RESOLVED (resolved pieces / pieces).
- HYPHEN REGRESSION: split_delimited / force_mandell_morphemes /
  explain_morphemes behavior is byte-for-byte the pre-LM-2 baseline.
- INTERNAL GOLD BATTERY: hand-built expected segmentations drawn
  from the LM-1 table pieces and the confirmed census, labeled
  INTERNAL. The score is printed whatever it is. External gold
  (MorphoLex / SIGMORPHON) is a named follow-up pending a license
  check -- it is NOT this circuit.
- PROOF CIRCUIT (Director mail 1a1ce1ed1a8c42c5, S8-S14):
  recorded-split governance vs the greedy path (S8); greedy
  prefix/suffix guards and suffix-stack order (S9); punctuation,
  delimiters and case (S10); explicit UNRESOLVED accounting
  arithmetic (S11); census recount from the artifact's ENTRIES,
  independent of its header claims (S12); v2 presence + the
  per-process table cache against a synthesized bound pair and a
  fixture loader implementing the PR #393 pair contract -- this
  branch's shipped loader predates v2, so S13 exercises
  split_word's side of the contract in subprocess scratch trees;
  the authoritative composition with the REAL #393 loader and
  artifacts is proof (d) in hidden_files/lm2/proof_d_real.py (S13);
  quarantine annotation for 'man' / 'alpha' (S14; 'dell' / 're'
  are S5).
"""

from __future__ import annotations

import hashlib
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

CENSUS_SHA256 = "c37adb098db942209b18e05ae9d9736fbee3b563532873f016a3474293da85c0"
CENSUS_PER_CATEGORY = {"LINK": 233, "POINT": 117, "CONDITION": 34,
                       "NEGATE": 37, "ASK": 34, "OPERATOR": 27,
                       "FOCUS": 6, "FLUFF": 0}

# INTERNAL gold battery -- hand-built from the LM-1 table (recorded
# splits, prefix/root/suffix inventories) and the confirmed census.
# Each entry: word -> [(piece, kind, resolved), ...]; census entries
# add a 4th element on the single piece: the full category set.
# "UNRES" pieces are the honest expectation where the harvested
# table holds no piece (never a fabricated split).
GOLD = {
    # census whole-classification (never split)
    "and": [("and", "whole", True, {"LINK"})],
    "the": [("the", "whole", True, {"POINT"})],
    "who": [("who", "whole", True, {"POINT", "ASK"})],
    "without": [("without", "whole", True,
                 {"LINK", "CONDITION", "NEGATE"})],
    "when": [("when", "whole", True, {"POINT", "CONDITION", "ASK"})],
    "not": [("not", "whole", True, {"NEGATE"})],
    "only": [("only", "whole", True, {"FOCUS"})],
    "will": [("will", "whole", True, {"OPERATOR"})],
    "but": [("but", "whole", True, {"LINK"})],
    "if": [("if", "whole", True, {"CONDITION"})],
    # table-recorded splits (inrepo_force stratum)
    "command": [("com", "prefix", True), ("mand", "root", True)],
    "complete": [("com", "prefix", True), ("plete", "root", True)],
    "commence": [("com", "prefix", True), ("men", "root", True),
                 ("ce", "suffix", True)],
    "commend": [("com", "prefix", True), ("mend", "root", True)],
    "nurture": [("nur", "prefix", True), ("tu", "root", True),
                ("re", "suffix", True)],
    "future": [("fu", "prefix", True), ("tu", "root", True),
               ("re", "suffix", True)],
    "rebirth": [("re", "prefix", True), ("birth", "root", True)],
    "omnifacure": [("omni", "prefix", True), ("fac", "root", True),
                   ("ure", "suffix", True)],
    "translogdell": [("trans", "prefix", True), ("log", "root", True),
                     ("dell", "suffix", True)],
    "commandell": [("com", "prefix", True), ("man", "root", True),
                   ("dell", "suffix", True)],
    "defacure": [("de", "prefix", True), ("fac", "root", True),
                 ("ure", "suffix", True)],
    "conlogure": [("con", "prefix", True), ("log", "root", True),
                  ("ure", "suffix", True)],
    "premiture": [("pre", "prefix", True), ("mit", "root", True),
                  ("ure", "suffix", True)],
    "omnispecure": [("omni", "prefix", True), ("spec", "root", True),
                    ("ure", "suffix", True)],
    "refacure": [("re", "prefix", True), ("fac", "root", True),
                 ("ure", "suffix", True)],
    "mandell": [("man", "prefix", True), ("dell", "suffix", True)],
    "mandel": [("man", "prefix", True), ("del", "UNRESOLVED", False)],
    # The recorded force splits for mandellang / mandellanguage
    # ('Man-dell-Lang', 'Man-dell-Lang-uage') do NOT tile the word --
    # the parts join to 'mandelllang' / 'mandelllanguage' (the 'l'
    # is shared between dell and Lang). They are overlapping display
    # forms, so the recorded-split path honestly declines them and
    # the generic path runs. Gold records that behavior.
    "mandellang": [("mandel", "prefix", True),
                   ("lang", "UNRESOLVED", False)],
    "mandellanguage": [("mandel", "prefix", True),
                       ("language", "UNRESOLVED", False)],
    # generic greedy segmentation over the harvested inventory
    "transportation": [("trans", "prefix", True),
                       ("porta", "UNRESOLVED", False),
                       ("tion", "suffix", True)],
    "preview": [("pre", "prefix", True),
                ("view", "UNRESOLVED", False)],
    "incredible": [("incredible", "UNRESOLVED", False)],
    "unbelievable": [("unbelievable", "UNRESOLVED", False)],
    "structure": [("struct", "root", True), ("ure", "suffix", True)],
    "transform": [("trans", "prefix", True), ("form", "root", True)],
    "compress": [("com", "prefix", True),
                 ("press", "UNRESOLVED", False)],
    "confirm": [("con", "prefix", True),
                ("firm", "UNRESOLVED", False)],
    "movement": [("move", "UNRESOLVED", False),
                 ("ment", "suffix", True)],
    "singing": [("sing", "UNRESOLVED", False),
                ("ing", "suffix", True)],
    "transmit": [("trans", "prefix", True), ("mit", "root", True)],
    "submit": [("sub", "prefix", True), ("mit", "root", True)],
    "inspect": [("inspect", "UNRESOLVED", False)],
    "logic": [("logic", "whole", True)],
    "evolve": [("evolve", "whole", True)],
    "dell": [("dell", "whole", True)],
    "re": [("re", "whole", True)],
    "translation": [("trans", "prefix", True),
                    ("la", "UNRESOLVED", False),
                    ("tion", "suffix", True)],
    "omni": [("omni", "whole", True)],
    "zzqx": [("zzqx", "UNRESOLVED", False)],
}


# ---- S13 fixtures -------------------------------------------------
# A minimal loader implementing the PR #393 pair contract
# (v2-preferred default path; the pair binding in the v2 header --
# generation = sha256(collisions_sha256 || rows_sha256) over the
# canonical rows bytes -- is verified on load and any mismatch
# raises PairInconsistentError; lookup returns the FULL row set
# with precedence annotation, external_wikipedia lowest). It is a
# test fixture, NOT shipped code: this branch's real loader
# predates v2 support. split_word is the unit under test.
_S13_LOADER = '''
import hashlib, json, os
_HERE = os.path.dirname(os.path.abspath(__file__))
V1 = os.path.join(_HERE, "lm_table_v1.json")
V1C = os.path.join(_HERE, "lm_table_v1.collisions.json")
V2 = os.path.join(_HERE, "lm_table_v2.json")
V2C = os.path.join(_HERE, "lm_table_v2.collisions.json")
PRECEDENCE = ["customs", "ace_seed", "inrepo", "inrepo_force",
              "inrepo_legacy", "candidate", "external_wikipedia"]
_RANK = {n: i for i, n in enumerate(PRECEDENCE)}

class PairInconsistentError(RuntimeError):
    pass

def _sha(b):
    return hashlib.sha256(b).hexdigest()

def _canon(rows):
    return json.dumps(rows, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")

def load_table(path=None):
    if path is not None:
        if not os.path.exists(path):
            return {"header": None, "rows": []}
        doc = json.load(open(path, encoding="utf-8"))
        return {"header": doc.get("header"),
                "rows": doc.get("rows", [])}
    if os.path.exists(V2):
        doc = json.loads(open(V2, "rb").read().decode("utf-8"))
        pair = (doc.get("header") or {}).get("pair")
        if pair:
            if not os.path.exists(V2C):
                raise PairInconsistentError("collisions missing")
            cbytes = open(V2C, "rb").read()
            rows_sha = _sha(_canon(doc.get("rows", [])))
            gen = _sha(bytes.fromhex(_sha(cbytes))
                       + bytes.fromhex(rows_sha))
            if (_sha(cbytes) != pair["collisions_sha256"]
                    or rows_sha != pair["rows_sha256"]
                    or gen != pair["generation"]):
                raise PairInconsistentError("pair binding mismatch")
        return {"header": doc.get("header"),
                "rows": doc.get("rows", [])}
    if not os.path.exists(V1):
        return {"header": None, "rows": []}
    doc = json.load(open(V1, encoding="utf-8"))
    return {"header": doc.get("header"), "rows": doc.get("rows", [])}

def load_collisions(path=None):
    p = path or (V2C if os.path.exists(V2) else V1C)
    if not os.path.exists(p):
        return []
    if path is None and os.path.exists(V2):
        load_table()
    return json.load(open(p, encoding="utf-8"))

def lookup(piece, table=None):
    t = table if table is not None else load_table()
    key = (piece or "").strip().strip("-").lower()
    if not key:
        return []
    out = []
    for row in t.get("rows", []):
        if row.get("piece") == key:
            a = dict(row)
            a["precedence_rank"] = _RANK.get(row.get("stratum"),
                                             len(PRECEDENCE))
            out.append(a)
    out.sort(key=lambda r: (r["precedence_rank"],
                            r.get("authored_position_class", "")))
    return out
'''

_S13_DRIVER = '''
import json, sys
sys.path.insert(0, sys.argv[1])
from form.mandell import morpheme
def sig(w):
    p = morpheme.split_word(w)
    return {"pieces": [[x["piece"], x["kind"], x["resolved"]]
                       for x in p["pieces"]],
            "accounted": p["accounted"]}
try:
    print(json.dumps({"telescope": sig("telescope")}))
except Exception as e:
    print(json.dumps({"error": type(e).__name__}))
'''

_S13_CACHE_DRIVER = '''
import json, os, shutil, sys
root = sys.argv[1]
sys.path.insert(0, root)
from form.mandell import morpheme
def sig(w):
    p = morpheme.split_word(w)
    return [[x["piece"], x["kind"], x["resolved"]]
            for x in p["pieces"]]
first = sig("telescope")
md = os.path.join(root, "form", "mandell")
for f in ("lm_table_v2.json", "lm_table_v2.collisions.json"):
    shutil.copy(os.path.join(root, "stash", f), os.path.join(md, f))
second = sig("telescope")
print(json.dumps({"first": first, "second": second}))
'''


def _sig(parse):
    """(piece, kind, resolved) signature of a parse for gold compare."""
    return [(p["piece"], p["kind"], p["resolved"])
            for p in parse["pieces"]]


def _gold_sig(expected):
    return [(e[0], e[1], e[2]) for e in expected]


def smoke() -> bool:
    print("=== LM-2 SPLITTER SMOKE ===")
    r = []

    def rec(name, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}")
        r.append(bool(ok))

    from form.mandell import lm_table, morpheme

    # ---- S1 census artifact integrity
    cpath = os.path.join(_HERE, "mandell", "lm0_census_v1.json")
    with open(cpath, encoding="utf-8") as f:
        census_doc = json.load(f)
    header = census_doc["header"]
    rec("S1 census artifact pins the confirmed edition sha256",
        header["source_sha256"] == CENSUS_SHA256)
    census_file = os.path.join(
        _ROOT, "director-reports", "LM0_CENSUS_CONFIRMED_2026-11-11.md")
    with open(census_file, "rb") as f:
        on_disk = hashlib.sha256(f.read()).hexdigest()
    rec("S1 census source on disk hashes to the pinned edition",
        on_disk == CENSUS_SHA256)
    rec("S1 census totals: 488 rows / 441 unique / per-category exact",
        header["rows"] == 488 and header["unique_words"] == 441
        and header["per_category"] == CENSUS_PER_CATEGORY
        and len(census_doc["entries"]) == 441)
    from form import lm2_census_build
    rec("S1 generator rebuild == shipped artifact (deterministic)",
        lm2_census_build.build_doc() == census_doc)

    # ---- S2 BEFORE -> AFTER
    rec("S2 split_word exists (BEFORE: absent)",
        hasattr(morpheme, "split_word"))
    if not hasattr(morpheme, "split_word"):
        print(f"=== {sum(r)}/{len(r)} ===")
        return False
    before = morpheme.explain_morphemes("transportation")["parts"]
    rec("S2 baseline explain_morphemes still one opaque part",
        len(before) == 1 and before[0]["known"] is False
        and before[0]["sense"] == "(open)")
    t = morpheme.split_word("transportation")
    rec("S2 transportation decomposes: trans + UNRES(porta) + tion",
        _sig(t) == _gold_sig(GOLD["transportation"]))
    pv = morpheme.split_word("preview")
    rec("S2 preview decomposes: pre resolved + UNRES(view)",
        _sig(pv) == _gold_sig(GOLD["preview"]))
    for w in ("incredible", "unbelievable"):
        p = morpheme.split_word(w)
        rec(f"S2 {w}: honest UNRESOLVED, nothing fabricated",
            _sig(p) == _gold_sig(GOLD[w]) and p["accounted"] == 0.0)

    # ---- S3 census whole-classification
    who = morpheme.split_word("who")
    rec("S3 census word classifies whole with ALL categories",
        len(who["pieces"]) == 1 and who["pieces"][0]["kind"] == "whole"
        and set(who["pieces"][0]["categories"]) == {"POINT", "ASK"})
    without = morpheme.split_word("without")
    rec("S3 multi-category law: without = LINK + CONDITION + NEGATE",
        set(without["pieces"][0]["categories"])
        == {"LINK", "CONDITION", "NEGATE"})
    but = morpheme.split_word("but")
    rec("S3 census rows kept: 'but' carries 2 rows, 1 category",
        but["pieces"][0]["categories"] == ["LINK"]
        and len(but["pieces"][0]["senses"]) == 2)

    # ---- S4 honest scores
    zz = morpheme.split_word("zzqx")
    rec("S4 nonsense word: UNRESOLVED, ACCOUNTED 0, RESOLVED 0",
        _sig(zz) == [("zzqx", "UNRESOLVED", False)]
        and zz["accounted"] == 0.0 and zz["morpheme_resolved"] == 0.0)
    rec("S4 transportation scores: ACCOUNTED 9/14, RESOLVED 2/3",
        abs(t["accounted"] - 9 / 14) < 1e-9
        and abs(t["morpheme_resolved"] - 2 / 3) < 1e-9)
    cmd = morpheme.split_word("command")
    rec("S4 full parse: ACCOUNTED 1 and RESOLVED 1",
        cmd["accounted"] == 1.0 and cmd["morpheme_resolved"] == 1.0)

    # ---- S5 no silent first-match
    dell_rows = lm_table.lookup("dell")
    cd = morpheme.split_word("commandell")
    dell_piece = [p for p in cd["pieces"] if p["piece"] == "dell"][0]
    rec("S5 'dell' senses == FULL lookup row set (>=4, >=2 strata)",
        len(dell_piece["senses"]) == len(dell_rows) >= 4
        and len({row["stratum"] for row in dell_piece["senses"]}) >= 2
        and all("precedence_rank" in row
                for row in dell_piece["senses"]))
    rec("S5 quarantined piece annotates position_unresolved",
        dell_piece.get("position_unresolved") is True)
    re_piece = morpheme.split_word("future")["pieces"][-1]
    rec("S5 're' annotates position_unresolved, senses complete",
        re_piece["piece"] == "re"
        and re_piece.get("position_unresolved") is True
        and len(re_piece["senses"]) == len(lm_table.lookup("re")))

    # ---- S6 hyphen / legacy regression (byte-for-byte baseline)
    rec("S6 split_delimited unchanged",
        morpheme.split_delimited("Com-man-dell") == ["Com", "man", "dell"])
    rec("S6 force_mandell_morphemes unchanged",
        morpheme.force_mandell_morphemes("Commandell") == "Com-man-dell"
        and morpheme.force_mandell_morphemes("mandell") == "Man-dell"
        and morpheme.force_mandell_morphemes("nurture") == "Nur-tu-re")
    hy = morpheme.split_word("Com-man-dell")
    rec("S6 split_word on hyphen form: com/man/dell all resolved",
        [p["piece"] for p in hy["pieces"]] == ["com", "man", "dell"]
        and all(p["resolved"] for p in hy["pieces"]))
    rec("S6 morpheme.smoke() baseline passes", morpheme.smoke())

    # ---- S7 INTERNAL gold battery (score printed whatever it is)
    misses = []
    for word, expected in GOLD.items():
        parse = morpheme.split_word(word)
        ok = _sig(parse) == _gold_sig(expected)
        if ok and len(expected) == 1 and len(expected[0]) == 4:
            ok = (set(parse["pieces"][0].get("categories", []))
                  == expected[0][3])
        if not ok:
            misses.append((word, expected, _sig(parse)))
    score = (len(GOLD) - len(misses)) / len(GOLD)
    print(f"    INTERNAL GOLD BATTERY: {len(GOLD) - len(misses)}/"
          f"{len(GOLD)} = {score:.3f}")
    for word, expected, got in misses:
        print(f"    GOLD MISS {word}: expected {_gold_sig(expected)} "
              f"got {got}")
    rec("S7 INTERNAL gold battery: every case matches", not misses)

    # ---- S8 recorded-split governance (proof item (c))
    nur_splits = {row.get("split") for row in lm_table.lookup("nurture")
                  if row.get("split")}
    nur = morpheme.split_word("nurture")
    rec("S8 recorded split governs: nurture == Nur-tu-re, suffix is "
        "'re' although 'ure' is a table suffix piece",
        nur_splits == {"Nur-tu-re"}
        and _sig(nur) == [("nur", "prefix", True),
                          ("tu", "root", True),
                          ("re", "suffix", True)]
        and len(lm_table.lookup("ure")) >= 1)
    lang_splits = {row.get("split")
                   for row in lm_table.lookup("mandellang")
                   if row.get("split")}
    lang = morpheme.split_word("mandellang")
    rec("S8 non-tiling recorded split honestly declined: "
        "mandellang (record: Man-dell-Lang) takes the generic path",
        lang_splits == {"Man-dell-Lang"}
        and _sig(lang) == _gold_sig(GOLD["mandellang"]))
    cd2 = morpheme.split_word("commandell")
    rec("S8 recorded path: every piece's senses == FULL lookup set",
        all(p["senses"] == lm_table.lookup(p["piece"])
            for p in cd2["pieces"]))

    # ---- S9 greedy guards + suffix stacking (proof item (c))
    rec("S9 prefix guard: 'press' -- 'pre' NOT torn out (remainder "
        "'ss' too short and not a known root)",
        _sig(morpheme.split_word("press"))
        == [("press", "UNRESOLVED", False)])
    rec("S9 prefix guard: 'prezz' -- 'pre' blocked the same way",
        _sig(morpheme.split_word("prezz"))
        == [("prezz", "UNRESOLVED", False)])
    rec("S9 prefix guard passes when the remainder is a known "
        "root: pretu == pre + tu",
        _sig(morpheme.split_word("pretu"))
        == [("pre", "prefix", True), ("tu", "root", True)])
    rec("S9 suffix stack preserves word order: movementing == "
        "move + ment + ing",
        _sig(morpheme.split_word("movementing"))
        == [("move", "UNRESOLVED", False), ("ment", "suffix", True),
            ("ing", "suffix", True)])

    # ---- S10 punctuation / delimiters / case (proof item (c))
    up = morpheme.split_word("TRANSPORTATION")
    rec("S10 uppercase input: parse == lowercase parse, raw input "
        "preserved in the receipt",
        _sig(up) == _sig(t) and up["normalized"] == "transportation"
        and up["word"] == "TRANSPORTATION")
    rec("S10 trailing punctuation stays glued to an UNRESOLVED "
        "residue and blocks the suffix match (honest, pinned)",
        _sig(morpheme.split_word("transportation."))
        == [("trans", "prefix", True),
            ("portation.", "UNRESOLVED", False)])
    hd = morpheme.split_word("trans-portation")
    rec("S10 hyphenated input: parts parsed separately",
        _sig(hd) == [("trans", "whole", True),
                     ("porta", "UNRESOLVED", False),
                     ("tion", "suffix", True)])
    rec("S10 trailing comma glues to the residue the same way",
        _sig(morpheme.split_word("commandell,"))
        == [("com", "prefix", True),
            ("mandell,", "UNRESOLVED", False)])

    # ---- S11 explicit UNRESOLVED accounting (proof item (c))
    rec("S11 preview accounting: ACCOUNTED 3/7, RESOLVED 1/2",
        abs(pv["accounted"] - 3 / 7) < 1e-9
        and abs(pv["morpheme_resolved"] - 1 / 2) < 1e-9)
    rec("S11 mandellang accounting: ACCOUNTED 6/10, RESOLVED 1/2",
        abs(lang["accounted"] - 6 / 10) < 1e-9
        and abs(lang["morpheme_resolved"] - 1 / 2) < 1e-9)
    mv = morpheme.split_word("movementing")
    rec("S11 movementing accounting: ACCOUNTED 7/11, RESOLVED 2/3",
        abs(mv["accounted"] - 7 / 11) < 1e-9
        and abs(mv["morpheme_resolved"] - 2 / 3) < 1e-9)
    rec("S11 delimited accounting covers part letters only: "
        "trans-portation ACCOUNTED 9/14, RESOLVED 2/3",
        abs(hd["accounted"] - 9 / 14) < 1e-9
        and abs(hd["morpheme_resolved"] - 2 / 3) < 1e-9)

    # ---- S12 census recount from the artifact's ENTRIES
    # (proof item (a): independent of the header's own claims)
    entries = census_doc["entries"]
    per_entries = {}
    total_entries_rows = 0
    for e in entries:
        total_entries_rows += len(e["rows"])
        for row in e["rows"]:
            per_entries[row["category"]] = \
                per_entries.get(row["category"], 0) + 1
    rec("S12 census entries recount: 488 rows in the entries alone",
        total_entries_rows == 488)
    rec("S12 census entries recount: per-category == confirmed "
        "counts",
        {c: per_entries.get(c, 0) for c in CENSUS_PER_CATEGORY}
        == CENSUS_PER_CATEGORY)
    rec("S12 census entries: 441 unique words; each entry's "
        "category set == its rows' categories",
        len({e["word"] for e in entries}) == 441
        and all(set(row["category"] for row in e["rows"])
                == set(e["categories"]) for e in entries))

    # ---- S13 v2 presence + cache (proof item (d), fixture form)
    import shutil
    import subprocess
    import tempfile
    scratch = tempfile.mkdtemp(prefix="lm2_s13_")
    try:
        md_dir = os.path.join(scratch, "form", "mandell")
        os.makedirs(md_dir)
        open(os.path.join(scratch, "form", "__init__.py"),
             "w").close()
        open(os.path.join(md_dir, "__init__.py"), "w").close()
        shipped_md = os.path.join(_HERE, "mandell")
        for f in ("morpheme.py", "lm0_census_v1.json",
                  "lm_table_v1.json", "lm_table_v1.collisions.json"):
            shutil.copy(os.path.join(shipped_md, f),
                        os.path.join(md_dir, f))
        with open(os.path.join(md_dir, "lm_table.py"), "w",
                  encoding="utf-8") as f:
            f.write(_S13_LOADER)

        def _ext_row(piece, pos, sense):
            return {"piece": piece, "authored_form": piece,
                    "position_class": pos,
                    "authored_position_class": pos,
                    "language": "Greek", "sense": sense,
                    "dell_ref": None, "la": None, "split": None,
                    "stratum": "external_wikipedia",
                    "provenance": {"source_file": "S13 fixture",
                                   "source_symbol": "synthesized"},
                    "conflict_status": "clean",
                    "notes": "S13 fixture row (synthesized v2 pair)"}

        with open(os.path.join(shipped_md, "lm_table_v1.json"),
                  encoding="utf-8") as f:
            v1_doc = json.load(f)
        rows2 = v1_doc["rows"] + [
            _ext_row("tele", "prefix", "far"),
            _ext_row("scope", "root", "instrument for seeing")]
        with open(os.path.join(shipped_md,
                               "lm_table_v1.collisions.json"),
                  "rb") as f:
            coll_bytes = f.read()
        rows_sha = hashlib.sha256(json.dumps(
            rows2, ensure_ascii=False, sort_keys=True,
            separators=(",", ":")).encode("utf-8")).hexdigest()
        coll_sha = hashlib.sha256(coll_bytes).hexdigest()
        gen = hashlib.sha256(bytes.fromhex(coll_sha)
                             + bytes.fromhex(rows_sha)).hexdigest()
        v2_doc = {"header": {"table": "lm_table", "version": 2,
                             "pair": {"generation": gen,
                                      "collisions_sha256": coll_sha,
                                      "rows_sha256": rows_sha}},
                  "rows": rows2}
        stash = os.path.join(scratch, "stash")
        os.makedirs(stash)
        with open(os.path.join(stash, "lm_table_v2.json"), "w",
                  encoding="utf-8") as f:
            json.dump(v2_doc, f, ensure_ascii=False, indent=1,
                      sort_keys=True)
            f.write("\n")
        with open(os.path.join(stash,
                               "lm_table_v2.collisions.json"),
                  "wb") as f:
            f.write(coll_bytes)
        driver = os.path.join(scratch, "driver.py")
        with open(driver, "w", encoding="utf-8") as f:
            f.write(_S13_DRIVER)
        cache_driver = os.path.join(scratch, "cache_driver.py")
        with open(cache_driver, "w", encoding="utf-8") as f:
            f.write(_S13_CACHE_DRIVER)

        def _run(path):
            proc = subprocess.run(
                [sys.executable, path, scratch],
                capture_output=True, text=True, cwd=scratch,
                env={**os.environ, "PYTHONPATH": scratch})
            if proc.returncode != 0:
                return {"driver_error": proc.stderr[-400:]}
            return json.loads(proc.stdout.strip().splitlines()[-1])

        out1 = _run(driver)
        rec("S13 v2 absent: split_word works on the v1 table",
            out1.get("telescope", {}).get("pieces")
            == [["telescope", "UNRESOLVED", False]]
            and out1.get("telescope", {}).get("accounted") == 0.0)
        for f in ("lm_table_v2.json", "lm_table_v2.collisions.json"):
            shutil.copy(os.path.join(stash, f),
                        os.path.join(md_dir, f))
        out2 = _run(driver)
        rec("S13 v2 present (consistent synthesized pair): wider "
            "external coverage is served",
            out2.get("telescope", {}).get("pieces")
            == [["tele", "prefix", True], ["scope", "root", True]]
            and out2.get("telescope", {}).get("accounted") == 1.0)
        cpath13 = os.path.join(md_dir, "lm_table_v2.collisions.json")
        with open(cpath13, encoding="utf-8") as f:
            ctext = f.read()
        i13 = ctext.find("dell")
        with open(cpath13, "w", encoding="utf-8") as f:
            f.write(ctext[:i13] + "z" + ctext[i13 + 1:])
        out3 = _run(driver)
        rec("S13 corrupt pair: PairInconsistentError propagates "
            "out of split_word (fail-closed, no v1 fallback)",
            out3.get("error") == "PairInconsistentError")
        for f in ("lm_table_v2.json", "lm_table_v2.collisions.json"):
            os.remove(os.path.join(md_dir, f))
        out4 = _run(cache_driver)
        rec("S13 cache is PER-PROCESS: a pair arriving mid-process "
            "is not picked up; fresh processes (above) see the "
            "disk state",
            out4.get("first") == [["telescope", "UNRESOLVED", False]]
            and out4.get("second") == out4.get("first"))
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    # ---- S14 quarantine annotation (proof item (e); dell/re: S5)
    man_piece = [p for p in cd["pieces"] if p["piece"] == "man"][0]
    rec("S14 quarantined 'man' annotates position_unresolved, "
        "senses complete",
        man_piece.get("position_unresolved") is True
        and len(man_piece["senses"]) == len(lm_table.lookup("man")))
    al = morpheme.split_word("alpha")
    rec("S14 quarantined 'alpha' (whole) annotates "
        "position_unresolved, senses complete",
        al["pieces"][0].get("position_unresolved") is True
        and len(al["pieces"][0]["senses"])
        == len(lm_table.lookup("alpha")))

    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
