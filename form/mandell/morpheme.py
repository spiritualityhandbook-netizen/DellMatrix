#!/usr/bin/env python3
"""
Morpheme delimiter protocol + lexicon (Codex + Visual Control forms).

Force structured subword splits. Expand prefix/root/suffix senses.
Does not reprogram host BPE.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import json
import os
import re

PREFIXES: Dict[str, str] = {
    "com": "together · synthesis · unified",
    "con": "with · joint",
    "re": "again · iterative · back",
    "pre": "before · predictive",
    "post": "after",
    "trans": "across · transformative",
    "de": "down · analytical · reverse · intensive",
    "omni": "all · universal · whole",
    "im": "in · isolated",
    "sub": "under · nested",
    "over": "above · across",
    "nova": "new · edge (not Floor)",
    "alpha": "beginning",
    "omega": "end · completion",
    "delta": "change",
    "man": "control · hand · execution",
    "nur": "nurse · feed · adaptive growth",
    "syn": "synchronized",
    "iso": "quarantined · equal",
    "aequi": "balanced",
    "ob": "against · opposed",
    "ad": "toward · directed",
    "fu": "forward vector",
    "nud": "raw · naked",
}

ROOTS: Dict[str, str] = {
    "fac": "construct · make",
    "log": "trace · reason",
    "mit": "send · transmit",
    "spec": "evaluate · look",
    "men": "mind",
    "mend": "validate · repair · honor",
    "tu": "protect",
    "birth": "genesis",
    "dell": "nested unit · operator cell · protected pocket",
    "mand": "command · order · execute",
    "cor": "heart · core",
    "ordo": "order · rank",
    "lux": "light",
    "lumen": "light made visible",
    "pulse": "stroke · beat",
    "voc": "voice",
    "gen": "origin · generate",
    "struct": "structure",
    "plete": "terminate · complete",
}

SUFFIXES: Dict[str, str] = {
    "ce": "attribute / act",
    "er": "actor",
    "re": "loop / again · return frame",
    "ure": "object / result · formalized",
    "dell": "fragment · nested cell · protected pocket",
    "tion": "act or state",
    "ment": "result or means · mind",
    "ing": "active pipeline",
    "ex": "execute immediately",
    "term": "terminate · wipe",
    "mut": "mutate variable",
}

# Flat lookup for quick sense
MORPHEMES: Dict[str, str] = {}
MORPHEMES.update(PREFIXES)
MORPHEMES.update(ROOTS)
MORPHEMES.update(SUFFIXES)
MORPHEMES.update({
    "mandel": "control-nest · Mandell root surface",
    "mandell": "control-nest · Mandell root surface",
    "nurture": "feed growth",
    "commandell": "unified execution protected pocket",
    "omnifacure": "universal object construction",
})


def split_delimited(text: str) -> List[str]:
    t = (text or "").strip()
    if not t:
        return []
    t = re.sub(r"^[\[\{⟨]+", "", t)
    t = re.sub(r"[\]\}⟩]+", "", t)
    parts = re.split(r"[-_/]+", t)
    return [p for p in (x.strip() for x in parts) if p]


def force_mandell_morphemes(word: str) -> str:
    w = (word or "").strip()
    low = w.lower().replace(" ", "")
    table = {
        "commandell": "Com-man-dell",
        "mandell": "Man-dell",
        "mandel": "Man-del",
        "mandellang": "Man-dell-Lang",
        "mandellanguage": "Man-dell-Lang-uage",
        "commence": "Com-men-ce",
        "commend": "Com-mend",
        "command": "Com-mand",
        "complete": "Com-plete",
        "nurture": "Nur-tu-re",
        "future": "Fu-tu-re",
        "omnifacure": "Omni-fac-ure",
        "omni-fac-ure": "Omni-fac-ure",
        "transfacure": "Trans-fac-ure",
        "rebirth": "Re-birth",
        "defacure": "De-fac-ure",
        "refacure": "Re-fac-ure",
        "conlogure": "Con-log-ure",
        "premiture": "Pre-mit-ure",
        "omnispecure": "Omni-spec-ure",
        "translogdell": "Trans-log-dell",
    }
    if low in table:
        return table[low]
    if "-" in w or "_" in w:
        return w
    return w


def sense_of(part: str) -> str:
    p = (part or "").lower()
    if p in PREFIXES:
        return PREFIXES[p]
    if p in ROOTS:
        return ROOTS[p]
    if p in SUFFIXES:
        return SUFFIXES[p]
    return MORPHEMES.get(p, "")


def explain_morphemes(text: str) -> Dict:
    forced = force_mandell_morphemes(text)
    parts = split_delimited(forced if "-" in forced else text)
    if not parts:
        parts = split_delimited(text)
    out = []
    for p in parts:
        s = sense_of(p)
        out.append({
            "morpheme": p,
            "sense": s or "(open)",
            "known": bool(s),
            "kind": (
                "prefix" if p.lower() in PREFIXES else
                "root" if p.lower() in ROOTS else
                "suffix" if p.lower() in SUFFIXES else
                "open"
            ),
        })
    return {
        "input": text,
        "forced": forced,
        "parts": out,
        "note": "Delimiter + lexicon · client-side Mandell surface",
    }


# ------------------------------------------------------------------
# LM-2 THE SPLITTER (LatinMandell plan section 15, circuit LM-2)
#
# split_word() decomposes one word against the LM-1 harvested table
# (form.mandell.lm_table -- the ONLY table path) plus the confirmed
# LM-0 census (lm0_census_v1.json, generated by form/lm2_census_build
# from the Ace-confirmed census edition). It extends this module; it
# does not replace split_delimited / force_mandell_morphemes /
# explain_morphemes, whose behavior is unchanged.
#
# Contract:
# - A confirmed-census word classifies WHOLE with ALL its census
#   categories (multi-category is law, R8) and is never split.
# - A word carrying a table-recorded split (inrepo_force stratum --
#   the same record force_mandell_morphemes uses) decomposes by
#   that record when every row agrees on exactly one split.
# - Otherwise greedy longest-match: at most one prefix (consumed
#   only when >= 3 chars remain, or the remainder is a known
#   root/whole piece, so 'pre' is not torn out of 'press'), an
#   iterated suffix stack under the analogous guard, and the middle
#   is a root/whole piece when the table knows it, else UNRESOLVED.
# - A piece's senses are the FULL lm_table.lookup() row set with
#   stratum + precedence annotation -- never a silent first-match.
#   (sense_of() above keeps its legacy first-match behavior for its
#   existing callers; split_word does not inherit it.) Quarantined
#   pieces (dell / man / re / alpha / delta / omega) annotate
#   position_unresolved instead of picking a positional winner.
# - QUARANTINE ELIGIBILITY (Director mail 1a1ce8ae4b5c8fe3):
#   position-dependent consumption (the prefix/suffix inventories,
#   known-middle, slot kind) is driven ONLY by rows whose own
#   position_class is resolved -- see _lm2_position_eligible. A
#   position_unresolved row's authored_position_class never
#   licenses a positional use; the row remains fully visible
#   through lookup() and piece senses -- excluded from position,
#   never erased.
# - Material with no table rows becomes an UNRESOLVED piece
#   carrying the raw text -- never guessed, never dropped.
# - Receipts: accounted = resolved chars / total chars;
#   morpheme_resolved = resolved pieces / total pieces.
# 'kind' is the piece's role in THIS parse; the table's own
# position claims live in the senses rows.
# ------------------------------------------------------------------

_LM2_HERE = os.path.dirname(os.path.abspath(__file__))
LM2_CENSUS_PATH = os.path.join(_LM2_HERE, "lm0_census_v1.json")
_LM2_QUARANTINED = ("dell", "man", "re", "alpha", "delta", "omega")
_lm2_state: Dict = {}


def _lm2_position_eligible(row: Dict) -> bool:
    """The ONE positional eligibility predicate (Director mail
    1a1ce8ae4b5c8fe3). A table row may drive position-dependent
    consumption -- prefix/suffix inventory membership,
    known-middle, slot kind -- only when its OWN position_class
    is resolved. A position_unresolved row's
    authored_position_class is a claim under dispute, never a
    positional license. Eligibility gates POSITION only: the
    row still serves in full through lm_table.lookup() and
    piece senses."""
    return row.get("position_class") != "position_unresolved"


def _lm2_loads() -> Dict:
    if "table" not in _lm2_state:
        try:
            from form.mandell import lm_table
        except ImportError:  # direct-script fallback
            import lm_table
        table = lm_table.load_table()
        census: Dict[str, Dict] = {}
        if os.path.exists(LM2_CENSUS_PATH):
            with open(LM2_CENSUS_PATH, encoding="utf-8") as f:
                doc = json.load(f)
            census = {e["word"]: e for e in doc.get("entries", [])}
        prefixes, suffixes = set(), set()
        for row in table.get("rows", []):
            if not _lm2_position_eligible(row):
                continue
            if row.get("position_class") == "prefix":
                prefixes.add(row["piece"])
            if row.get("position_class") == "suffix":
                suffixes.add(row["piece"])
        _lm2_state.update(
            lm_table=lm_table, table=table, census=census,
            prefixes=sorted(prefixes, key=len, reverse=True),
            suffixes=sorted(suffixes, key=len, reverse=True))
    return _lm2_state


def _lm2_piece(piece: str, kind: str, st: Dict) -> Dict:
    rows = st["lm_table"].lookup(piece, st["table"])
    out = {"piece": piece,
           "kind": kind if rows else "UNRESOLVED",
           "senses": rows,
           "resolved": bool(rows)}
    if rows and piece in _LM2_QUARANTINED:
        out["position_unresolved"] = True
    return out


def _lm2_census_piece(entry: Dict) -> Dict:
    return {
        "piece": entry["word"],
        "kind": "whole",
        "senses": [{"stratum": "lm0_census",
                    "category": row["category"],
                    "sense": row["meaning"],
                    "section": row["section"],
                    "precedence_rank": 0} for row in entry["rows"]],
        "resolved": True,
        "categories": list(entry["categories"]),
    }


def _lm2_known_middle(text: str, st: Dict) -> bool:
    for row in st["lm_table"].lookup(text, st["table"]):
        if (_lm2_position_eligible(row)
                and row.get("position_class")
                in ("root", "whole_form")):
            return True
    return False


def _lm2_slot_kind(part: str, slot: str, st: Dict) -> str:
    classes = set()
    for row in st["lm_table"].lookup(part, st["table"]):
        if _lm2_position_eligible(row):
            classes.add(row.get("position_class"))
    if slot == "first" and "prefix" in classes:
        return "prefix"
    if slot == "last" and "suffix" in classes:
        return "suffix"
    if "root" in classes or "whole_form" in classes:
        return "root"
    return {"first": "prefix", "middle": "root", "last": "suffix"}[slot]


def _lm2_recorded_split(word: str, st: Dict) -> Optional[List[Dict]]:
    rows = st["lm_table"].lookup(word, st["table"])
    splits = {row.get("split") for row in rows if row.get("split")}
    if len(splits) != 1:
        return None
    parts = [p.lower() for p in split_delimited(splits.pop())]
    if len(parts) < 2 or "".join(parts) != word:
        return None
    pieces = []
    for i, part in enumerate(parts):
        slot = ("first" if i == 0 else
                "last" if i == len(parts) - 1 else "middle")
        pieces.append(_lm2_piece(part, _lm2_slot_kind(part, slot, st), st))
    return pieces


def _lm2_generic(word: str, st: Dict) -> List[Dict]:
    rest = word
    pieces: List[Dict] = []
    for cand in st["prefixes"]:
        if rest.startswith(cand) and len(rest) > len(cand):
            rem = rest[len(cand):]
            if len(rem) >= 3 or _lm2_known_middle(rem, st):
                pieces.append(_lm2_piece(cand, "prefix", st))
                rest = rem
            break
    tail: List[Dict] = []
    while True:
        hit = None
        for cand in st["suffixes"]:
            if rest.endswith(cand) and len(rest) > len(cand):
                rem = rest[:-len(cand)]
                if len(rem) >= 2 or _lm2_known_middle(rem, st):
                    hit = (cand, rem)
                break
        if hit is None:
            break
        tail.insert(0, _lm2_piece(hit[0], "suffix", st))
        rest = hit[1]
    if rest:
        single = not pieces and not tail
        pieces.append(_lm2_piece(rest, "whole" if single else "root", st))
    return pieces + tail


def _lm2_parse_token(tok: str, st: Dict) -> List[Dict]:
    entry = st["census"].get(tok)
    if entry is not None:
        return [_lm2_census_piece(entry)]
    recorded = _lm2_recorded_split(tok, st)
    if recorded is not None:
        return recorded
    return _lm2_generic(tok, st)


def _lm2_receipt(word, norm: str, pieces: List[Dict],
                 census: bool) -> Dict:
    total = sum(len(p["piece"]) for p in pieces)
    resolved_chars = sum(len(p["piece"]) for p in pieces if p["resolved"])
    return {
        "word": word,
        "normalized": norm,
        "pieces": pieces,
        "accounted": (resolved_chars / total) if total else 0.0,
        "morpheme_resolved": (
            sum(1 for p in pieces if p["resolved"]) / len(pieces)
            if pieces else 0.0),
        "census": census,
    }


def split_word(word: str) -> Dict:
    """LM-2 decomposition of one word. See the LM-2 contract above.

    Returns {word, normalized, pieces, accounted, morpheme_resolved,
    census}; each piece is {piece, kind, senses, resolved} with kind
    in prefix / root / suffix / whole / UNRESOLVED. Delimited forms
    (Com-man-dell class) are segmented part by part via
    split_delimited; scores then cover the part letters only.
    """
    st = _lm2_loads()
    raw = (word or "").strip()
    norm = raw.lower()
    if not norm:
        return _lm2_receipt(word, "", [], False)
    if any(d in raw for d in "-_/"):
        pieces: List[Dict] = []
        for part in split_delimited(raw):
            pieces.extend(_lm2_parse_token(part.lower(), st))
        return _lm2_receipt(word, norm, pieces, False)
    return _lm2_receipt(word, norm, _lm2_parse_token(norm, st),
                        norm in st["census"])


# ------------------------------------------------------------------
# LM-3 THE COMPOSER (LatinMandell plan section 15, circuit LM-3)
#
# compose_word() is the STACK + CLASSIFY + MAP steps of the plan
# formula PARSE = SPLIT x STACK x CLASSIFY x MAP, built directly
# on split_word's receipt: pieces arrive IN PARSE ORDER with
# their STACK roles (kind: prefix aims, root carries, suffix
# lands), the FULL precedence-ranked sense rows, the quarantine
# annotations, and the per-row lineage fields. The composer adds
# NO table access, NO new ranking, and NO new authority:
#
# - GOVERNING SENSE: a piece's governing row is rows[0] of its
#   split-receipt senses -- the ONE existing selector
#   (lm_table.PRECEDENCE) already ordered them. The composer
#   never re-derives position from the governing row (position
#   was settled at split time under _lm2_position_eligible) and
#   never consults substring rows: only pieces the splitter
#   actually produced are composition material ('incredible':
#   lookup('cred') can see a sense, but 'cred' is not a piece of
#   the parse, so its sense composes nothing).
# - STACK: the gloss joins governing senses VERBATIM with the
#   existing " · " convention; UNRESOLVED pieces render as
#   their raw text in brackets, named in place, never dropped.
#   The template contributes only role punctuation -- no
#   connective prose is generated. gloss_state is derived, not
#   scored: COMPOSED (every piece resolved), PARTIAL (>=1
#   resolved and >=1 UNRESOLVED), UNRESOLVED (none resolved ->
#   gloss is None: SPLIT found nothing to stack, and the
#   multiplicative law forbids a fabricated product).
# - CURATED (Q-LM3.1 proposed rule, pending Director ruling):
#   where latinmandell.root_of returns a genuine whole-word
#   entry (customs or the 53 ROOTS -- Ace's pure meanings by
#   design, R14), it is reported as `curated` and governs the
#   word's Dell; the stack is still computed and shown beside
#   it, disagreements printed, never hidden. root_of's DERIVED
#   paths (the -tion/-ible suffix hints and hyphen morphology,
#   recognizable by their "morphology" key) are readings, not
#   curated entries, and never govern -- the -tion hint is
#   exactly the pseudo-gloss LM-3 exists to replace.
# - MAP (PROJECTION discipline): Dell candidates derive ONLY
#   from pieces whose governing row carries a dell_ref (today
#   exactly the 53 ace_seed bindings; external rows carry
#   none). A candidate is a reading, not a lookup claim.
#   Ranking is a presentation order over already-governed rows:
#   the contributing row's precedence_rank, then root/whole
#   pieces before affixes, then parse order. Distinct Dells:
#   exactly one -> THE candidate (ambiguity False); more ->
#   ambiguity True, dell None; none -> ambiguity
#   "no_candidate", dell None. A quarantined
#   (position_unresolved) piece never contributes a candidate,
#   though its governing SENSE may still stack -- quarantine
#   excludes position, never visibility (LM-2 law).
# - CLASSIFY (word level): a census word classifies by its LM-0
#   categories; a word with >=1 contributing content piece is
#   FUNCTION; otherwise UNRESOLVED. Sentence-level spine
#   assembly is LM-4 scope (Q-LM3.3).
# - LINEAGE (Q-B2 law): lineage entries are the GOVERNING rows
#   only, one per contributing piece; external entries carry
#   source_revid + provenance source_file + license.
#   lineage_class: DERIVED_ADAPTATION when >=1 governing row is
#   external_wikipedia (a stack composed in whole or in part
#   from external glosses, distributed under CC BY-SA 4.0 with
#   attribution), INDEPENDENT otherwise. UNCHANGED_QUOTE never
#   applies to a stack. The vocabulary follows the Q-B2 boundary
#   record; lm1_import.classify_export is a build-time bulk
#   export classifier for row sets and is deliberately NOT
#   reused here (its own docstring reserves LM-2/LM-3
#   composition lineage as a separate circuit).
# - HONESTY SCORES: accounted + morpheme_resolved ride the
#   split receipt UNCHANGED. No blended confidence is minted.
# - FAIL-CLOSED: compose_word calls split_word, so a
#   PairInconsistentError from the loader propagates out of the
#   composer exactly as out of the splitter.
# - latinmandell.explain / format_explain do NOT adopt the
#   composer in this circuit (Q-LM3.4 proposed); their behavior
#   is unchanged.
# ------------------------------------------------------------------

_LM3_STRATUM_EXTERNAL = "external_wikipedia"
_LM3_KIND_TIER = {"root": 0, "whole": 0, "prefix": 1, "suffix": 2}


def _lm3_curated(word: str) -> Optional[Dict]:
    """The genuine curated whole-word entry for `word`, or None.

    root_of() also returns DERIVED readings (suffix hints and
    hyphen morphology); those carry a "morphology" key and are
    not curated entries, so they never govern. Customs and the
    53 ROOTS hits carry no such key.
    """
    try:
        try:
            from form.mandell import latinmandell
        except ImportError:  # direct-script fallback
            import latinmandell
        hit = latinmandell.root_of(word)
    except Exception:
        return None
    if not hit or "morphology" in hit:
        return None
    return {"sense": hit.get("sense"), "dell": hit.get("dell"),
            "la": hit.get("la"), "custom": bool(hit.get("custom"))}


def compose_word(word: str) -> Dict:
    """LM-3 composition of one word. See the LM-3 contract above.

    Returns {word, normalized, pieces (the split receipt's
    pieces, each extended with `governing`: {sense, stratum,
    precedence_rank} or None), gloss, gloss_state, accounted,
    morpheme_resolved, curated, dell_candidates, dell,
    ambiguity, lineage, lineage_class, classify, census}.
    """
    split = split_word(word)
    pieces: List[Dict] = []
    lineage: List[Dict] = []
    raw_candidates: List[Dict] = []
    gloss_parts: List[str] = []
    contributing = 0
    for idx, piece in enumerate(split["pieces"]):
        out = dict(piece)
        governing = None
        if piece.get("resolved") and piece.get("senses"):
            row = piece["senses"][0]
            if row.get("sense"):
                governing = {
                    "sense": row["sense"],
                    "stratum": row.get("stratum"),
                    "precedence_rank": row.get("precedence_rank"),
                }
                entry = {"piece": piece["piece"],
                         "stratum": row.get("stratum"),
                         "precedence_rank": row.get("precedence_rank")}
                if row.get("stratum") == _LM3_STRATUM_EXTERNAL:
                    entry["source_revid"] = row.get("source_revid")
                    entry["source_file"] = (
                        row.get("provenance") or {}).get("source_file")
                    entry["license"] = row.get("license")
                lineage.append(entry)
                if (row.get("dell_ref") is not None
                        and not piece.get("position_unresolved")):
                    raw_candidates.append({
                        "dell": row["dell_ref"],
                        "via_piece": piece["piece"],
                        "via_stratum": row.get("stratum"),
                        "rank": row.get("precedence_rank"),
                        "_tier": _LM3_KIND_TIER.get(piece["kind"], 3),
                        "_idx": idx,
                    })
        out["governing"] = governing
        pieces.append(out)
        if governing is not None:
            contributing += 1
            gloss_parts.append(governing["sense"])
        else:
            gloss_parts.append("[%s]" % piece["piece"])

    total = len(split["pieces"])
    if contributing == 0:
        gloss, gloss_state = None, "UNRESOLVED"
    elif contributing == total:
        gloss, gloss_state = " · ".join(gloss_parts), "COMPOSED"
    else:
        gloss, gloss_state = " · ".join(gloss_parts), "PARTIAL"

    # MAP candidates: dedupe per Dell keeping the best-ranked
    # contribution, then present in (rank, kind tier, parse
    # order) -- a presentation order over governed rows only.
    by_dell: Dict[Any, Dict] = {}
    for cand in raw_candidates:
        key = (cand["rank"], cand["_tier"], cand["_idx"])
        cur = by_dell.get(cand["dell"])
        if cur is None or key < (cur["rank"], cur["_tier"], cur["_idx"]):
            by_dell[cand["dell"]] = cand
    candidates = sorted(
        by_dell.values(),
        key=lambda c: (c["rank"], c["_tier"], c["_idx"]))
    dell_candidates = [
        {"dell": c["dell"], "via_piece": c["via_piece"],
         "via_stratum": c["via_stratum"], "rank": c["rank"]}
        for c in candidates]
    if not dell_candidates:
        ambiguity: Any = "no_candidate"
    elif len(dell_candidates) == 1:
        ambiguity = False
    else:
        ambiguity = True

    curated = _lm3_curated(word)
    if curated is not None and curated.get("dell") is not None:
        dell = curated["dell"]
    elif len(dell_candidates) == 1:
        dell = dell_candidates[0]["dell"]
    else:
        dell = None

    if split["census"] and split["pieces"]:
        classify: Any = list(split["pieces"][0].get("categories") or [])
    elif contributing:
        classify = "FUNCTION"
    else:
        classify = "UNRESOLVED"

    lineage_class = (
        "DERIVED_ADAPTATION"
        if any(e["stratum"] == _LM3_STRATUM_EXTERNAL for e in lineage)
        else "INDEPENDENT")

    return {
        "word": split["word"],
        "normalized": split["normalized"],
        "pieces": pieces,
        "gloss": gloss,
        "gloss_state": gloss_state,
        "accounted": split["accounted"],
        "morpheme_resolved": split["morpheme_resolved"],
        "curated": curated,
        "dell_candidates": dell_candidates,
        "dell": dell,
        "ambiguity": ambiguity,
        "lineage": lineage,
        "lineage_class": lineage_class,
        "classify": classify,
        "census": split["census"],
    }


def smoke() -> bool:
    print("=== MORPHEME PROTOCOL SMOKE ===")
    r = []
    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}")
        r.append(bool(ok))
    rec("force Commandell", force_mandell_morphemes("Commandell") == "Com-man-dell")
    rec("force Omni-fac-ure", "fac" in force_mandell_morphemes("omnifacure").lower())
    rec("split", split_delimited("Com-man-dell") == ["Com", "man", "dell"])
    rec("prefix sense", "unified" in sense_of("com").lower() or "together" in sense_of("com").lower())
    rec("explain", len(explain_morphemes("Omni-fac-ure")["parts"]) >= 2)
    rec("new prefix syn", "syn" in PREFIXES)
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
