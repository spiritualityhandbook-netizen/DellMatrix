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

    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
