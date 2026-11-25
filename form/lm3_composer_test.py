"""LM-3 THE COMPOSER -- contracts for morpheme.compose_word
(LatinMandell plan SS15, circuit LM-3; grounding
hidden_files/lm3/GROUNDING.md).

Contracts proven here:

- STACK: compose_word consumes split_word's receipt (pieces in
  parse order, STACK roles already the kind values) and stacks
  each piece's GOVERNING sense -- rows[0] under the ONE existing
  precedence authority (lm_table.PRECEDENCE). No second selector,
  no ranking, no filtering is introduced. The gloss joins
  verbatim table senses with " - "-style role punctuation only
  (the existing " . " join convention, written below as the
  middle-dot join); UNRESOLVED pieces render as their raw text
  in brackets, named, never dropped, never smoothed over.
- GLOSS_STATE (deterministic, not a score): COMPOSED = every
  piece resolved; PARTIAL = at least one resolved and at least
  one UNRESOLVED; UNRESOLVED = no resolved pieces -> NO gloss
  is emitted at all (multiplicative zero). A word the splitter
  returns with an UNRESOLVED middle composes at most PARTIAL
  even when lookup() can see senses for its substrings
  ('incredible'/'cred': substring visibility is NOT composition
  material).
- CURATED GOVERNS (Q-LM3.1, proposed rule, pending Director
  confirmation): where a genuine curated whole-word entry
  exists (latinmandell ROOTS or customs), it is reported as the
  word's governed sense/Dell and the piece stack is shown
  beside it; disagreements print, never hide. root_of()'s
  DERIVED paths (suffix hints, hyphen morphology) are NOT
  curated entries and never govern.
- MAP (PROJECTION discipline): Dell candidates derive ONLY
  from pieces whose governing row carries a dell_ref (today
  exactly the 53 ace_seed bindings) -- ranked by the row's
  precedence, root/whole pieces before affixes at equal
  precedence. One distinct Dell -> THE candidate; more ->
  ranked list with ambiguity named; none -> dell None,
  ambiguity "no_candidate". Quarantined (position_unresolved)
  pieces never contribute a candidate. A candidate is a
  reading, never a lookup claim.
- LINEAGE (Q-B2 law): lineage = the governing rows only;
  lineage_class is DERIVED_ADAPTATION when at least one
  governing row is external_wikipedia (carrying source_revid +
  provenance source_file + license on the entry), INDEPENDENT
  otherwise. UNCHANGED_QUOTE never applies to a stack.
  Vocabulary follows the Q-B2 boundary record; the build-time
  row-set classifier lm1_import.classify_export is a separate
  bulk-export contract and is NOT reused (its own docstring:
  "LM-2/LM-3 composition lineage is a separate circuit").
- FAIL-CLOSED: PairInconsistentError from the loader propagates
  out of compose_word (scratch tree, corrupted real pair) --
  never a silent v1 gloss, never a swallowed error.
- SCORES UNCHANGED: the split receipt's accounted +
  morpheme_resolved ride the composed receipt byte-identical;
  no blended confidence number is minted.
- LEGACY PARITY: explain_morphemes / latinmandell.explain /
  format_explain / root_of behavior is byte-identical to the
  pre-LM-3 baseline (pinned literals below); latinmandell does
  NOT adopt the composer in this circuit (Q-LM3.4 proposed).
- Evidence level: INTEGRATION (direct module path). The gold
  expectations are INTERNAL (derived from the shipped table's
  own rows at the merged LM-2 head) and labeled INTERNAL; no
  external gold is claimed.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from form.mandell import lm_table, morpheme  # noqa: E402
from form.mandell import latinmandell  # noqa: E402

JOIN = " · "

# Scratch driver: runs in a tree carrying the REAL morpheme /
# lm_table / latinmandell modules and the REAL v2 pair with a
# corrupted collisions member. compose_word must surface
# PairInconsistentError, never a gloss.
_PAIR_DRIVER = '''
import json, sys
sys.path.insert(0, sys.argv[1])
from form.mandell import morpheme
try:
    r = morpheme.compose_word("biology")
    print(json.dumps({"gloss": r["gloss"],
                      "gloss_state": r["gloss_state"]}))
except Exception as e:
    print(json.dumps({"error": type(e).__name__}))
'''


def _gov(receipt, piece):
    for p in receipt["pieces"]:
        if p["piece"] == piece:
            return p.get("governing")
    return None


def smoke() -> bool:
    print("=== LM-3 COMPOSER SMOKE ===")
    r = []

    def rec(name, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}")
        r.append(bool(ok))

    compose = morpheme.compose_word

    # ---- T1 transportation: PARTIAL, unresolved middle named
    t1 = compose("transportation")
    rec("T1 transportation gloss_state PARTIAL",
        t1["gloss_state"] == "PARTIAL")
    rec("T1 gloss stacks governing senses, [porta] named",
        t1["gloss"] == JOIN.join(
            ["across · transformative", "[porta]", "act or state"]))
    rec("T1 porta governing is None",
        _gov(t1, "porta") is None)
    sp = morpheme.split_word("transportation")
    rec("T1 scores ride unchanged from the split receipt",
        t1["accounted"] == sp["accounted"]
        and t1["morpheme_resolved"] == sp["morpheme_resolved"])
    rec("T1 root_of suffix hint is NOT curated (derived path)",
        t1["curated"] is None)
    rec("T1 lineage INDEPENDENT (inrepo governing rows)",
        t1["lineage_class"] == "INDEPENDENT")

    # ---- T2 biology: COMPOSED + DERIVED_ADAPTATION lineage
    t2 = compose("biology")
    rec("T2 biology gloss_state COMPOSED",
        t2["gloss_state"] == "COMPOSED")
    rec("T2 gloss is the verbatim external senses stacked",
        t2["gloss"] == JOIN.join(
            ["life", "word, reason, speech, thought"]))
    rec("T2 lineage_class DERIVED_ADAPTATION",
        t2["lineage_class"] == "DERIVED_ADAPTATION")
    lin = {e["piece"]: e for e in t2["lineage"]}
    rec("T2 lineage names both source_revids (pinned)",
        lin.get("bio", {}).get("source_revid") == 1275596589
        and lin.get("logy", {}).get("source_revid") == 1320808977)
    rec("T2 lineage entries carry CC BY-SA license + source_file",
        all(lin[p].get("license") == "CC BY-SA 4.0"
            and lin[p].get("source_file")
            for p in ("bio", "logy")))
    rec("T2 no curated entry, no Dell candidate",
        t2["curated"] is None and t2["dell_candidates"] == []
        and t2["dell"] is None
        and t2["ambiguity"] == "no_candidate")
    rec("T2 scores are the split scores (1.0 / 1.0)",
        t2["accounted"] == 1.0 and t2["morpheme_resolved"] == 1.0)

    # ---- T3 structure: quarantined 'struct' claim nowhere
    t3 = compose("structure")
    rec("T3 structure PARTIAL via [stru, ct, ure]",
        t3["gloss_state"] == "PARTIAL"
        and [p["piece"] for p in t3["pieces"]] == ["stru", "ct", "ure"])
    rec("T3 gloss names [ct] unresolved, governing senses verbatim",
        t3["gloss"] == JOIN.join(
            ["to make up, build", "[ct]",
             "object / result · formalized"]))
    rec("T3 no piece is the quarantined 'struct'",
        all(p["piece"] != "struct" for p in t3["pieces"]))

    # ---- T4 incredible: substring 'cred' sense never composes
    t4 = compose("incredible")
    rec("T4 incredible splits [in resolved, credible UNRESOLVED] "
        "on the integrated head",
        [(p["piece"], p["resolved"]) for p in t4["pieces"]]
        == [("in", True), ("credible", False)])
    rec("T4 at most PARTIAL, unresolved middle named",
        t4["gloss_state"] == "PARTIAL"
        and t4["gloss"] == JOIN.join(["in, on", "[credible]"]))
    rec("T4 'cred' sense (believe, trust) nowhere in the receipt",
        "believe" not in json.dumps(t4, ensure_ascii=False))
    rec("T4 no candidates from substring visibility",
        t4["dell_candidates"] == [] and t4["dell"] is None)

    # ---- T5 transform: curated governs, stack beside it
    t5 = compose("transform")
    rec("T5 curated entry governs (Ace's pure meaning)",
        t5["curated"] is not None
        and t5["curated"]["sense"] == "change form across a boundary"
        and t5["curated"]["dell"] == 4)
    rec("T5 stack still computed and shown (both print)",
        t5["gloss"] == JOIN.join(
            ["across · transformative", "Bring shape"])
        and t5["gloss_state"] == "COMPOSED")
    rec("T5 governed Dell is the curated 4",
        t5["dell"] == 4)
    rec("T5 lineage INDEPENDENT (inrepo + candidate governing)",
        t5["lineage_class"] == "INDEPENDENT")
    rec("T5 governing row for 'form' is rows[0] (candidate, "
        "rank 5) -- precedence decides, no second selector",
        _gov(t5, "form") == {"sense": "Bring shape",
                             "stratum": "candidate",
                             "precedence_rank": 5})

    # ---- T6 MAP candidates
    t6a = compose("unlock")
    rec("T6 unlock: exactly one piece candidate, Dell 23 via 'lock'",
        t6a["dell_candidates"] == [
            {"dell": 23, "via_piece": "lock",
             "via_stratum": "ace_seed", "rank": 1}]
        and t6a["ambiguity"] is False)
    rec("T6 unlock: curated whole-word entry (Dell 24) governs "
        "over the piece candidate -- both print (Q-LM3.1 rule)",
        t6a["curated"] is not None
        and t6a["curated"]["dell"] == 24
        and t6a["dell"] == 24)
    t6b = compose("lock-load")
    rec("T6 lock-load: two distinct Dells, ranked, ambiguity named",
        [c["dell"] for c in t6b["dell_candidates"]] == [23, 28]
        and t6b["ambiguity"] is True and t6b["dell"] is None)
    t6c = compose("lock")
    rec("T6 lock (whole piece): candidate 23 stands",
        [c["dell"] for c in t6c["dell_candidates"]] == [23]
        and t6c["dell"] == 23)

    # ---- T7 zero resolved pieces: NO gloss emitted
    t7 = compose("zzzzqqq")
    rec("T7 unknown word: gloss_state UNRESOLVED, gloss None",
        t7["gloss_state"] == "UNRESOLVED" and t7["gloss"] is None)
    rec("T7 unknown word: no lineage, no candidates",
        t7["lineage"] == [] and t7["dell_candidates"] == [])
    t7b = compose("")
    rec("T7 empty word: UNRESOLVED, gloss None",
        t7b["gloss_state"] == "UNRESOLVED" and t7b["gloss"] is None)

    # ---- T8 census word: category classifies, meaning stacks
    t8 = compose("the")
    rec("T8 census word: census True, classify carries POINT",
        t8["census"] is True and t8["classify"] == ["POINT"])
    rec("T8 census gloss is the predisposed meaning, COMPOSED",
        t8["gloss"] == "point-known — the identifiable one"
        and t8["gloss_state"] == "COMPOSED")
    rec("T8 census lineage INDEPENDENT",
        t8["lineage_class"] == "INDEPENDENT")

    # ---- T9 quarantined pieces: senses may stack, annotation
    # carried, no MAP candidate (commandell = com/man/dell)
    t9 = compose("commandell")
    qp = [p for p in t9["pieces"] if p["piece"] in ("man", "dell")]
    rec("T9 quarantined pieces keep position_unresolved annotation",
        len(qp) == 2
        and all(p.get("position_unresolved") is True for p in qp))
    rec("T9 quarantined governing senses still stack (visibility, "
        "not position)",
        all(p.get("governing") for p in qp)
        and t9["gloss_state"] == "COMPOSED")
    rec("T9 quarantined pieces contribute no Dell candidate",
        t9["dell_candidates"] == []
        and t9["ambiguity"] == "no_candidate")

    # ---- T10 determinism: same process, same receipt
    rec("T10 compose is deterministic within a process",
        compose("biology") == compose("biology"))

    # ---- T11 PairInconsistentError propagates (scratch, real pair)
    scratch = tempfile.mkdtemp(prefix="lm3_pair_")
    try:
        md_dir = os.path.join(scratch, "form", "mandell")
        os.makedirs(md_dir)
        open(os.path.join(scratch, "form", "__init__.py"), "w").close()
        open(os.path.join(md_dir, "__init__.py"), "w").close()
        src_md = os.path.join(_HERE, "mandell")
        for f in ("morpheme.py", "lm_table.py", "latinmandell.py",
                  "lm_table_v2.json", "lm_table_v2.collisions.json",
                  "lm0_census_v1.json"):
            shutil.copy(os.path.join(src_md, f), os.path.join(md_dir, f))
        cpath = os.path.join(md_dir, "lm_table_v2.collisions.json")
        with open(cpath, encoding="utf-8") as f:
            ctext = f.read()
        i = ctext.find("dell")
        with open(cpath, "w", encoding="utf-8") as f:
            f.write(ctext[:i] + "z" + ctext[i + 1:])
        driver = os.path.join(scratch, "driver.py")
        with open(driver, "w", encoding="utf-8") as f:
            f.write(_PAIR_DRIVER)
        proc = subprocess.run(
            [sys.executable, driver, scratch],
            capture_output=True, text=True, cwd=scratch,
            env={**os.environ, "PYTHONPATH": scratch})
        out = (json.loads(proc.stdout.strip().splitlines()[-1])
               if proc.returncode == 0 else
               {"driver_error": proc.stderr[-400:]})
        rec("T11 corrupted pair: PairInconsistentError propagates "
            "out of compose_word (fail-closed, no silent gloss)",
            out.get("error") == "PairInconsistentError")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    # ---- T12 legacy parity (pre-LM-3 baseline literals)
    rec("T12 explain_morphemes('Com-man-dell') unchanged",
        morpheme.explain_morphemes("Com-man-dell")["parts"] == [
            {"morpheme": "Com", "sense": "together · synthesis · unified",
             "known": True, "kind": "prefix"},
            {"morpheme": "man", "sense": "control · hand · execution",
             "known": True, "kind": "prefix"},
            {"morpheme": "dell", "sense": "nested unit · operator cell · protected pocket",
             "known": True, "kind": "root"}])
    rec("T12 format_explain worked example unchanged",
        latinmandell.format_explain("transform the idea")
        == "LatinMandell · transform the idea\n"
           "  transform\n"
           "    la: transformare\n"
           "    sense: change form across a boundary  dell=04\n"
           "  idea\n"
           "    la: idea / forma\n"
           "    sense: form held in mind · pattern  dell=08\n"
           "  seeds: 04[Transform] · 08[Create]")
    rec("T12 root_of('transportation') still returns its legacy "
        "suffix hint (composer did not rewrite latinmandell)",
        (latinmandell.root_of("transportation") or {}).get("sense")
        == "act or state of (← Latin -tio)")

    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
