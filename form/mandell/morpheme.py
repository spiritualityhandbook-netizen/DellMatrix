#!/usr/bin/env python3
"""
Morpheme delimiter protocol + lexicon (Codex + Visual Control forms).

Force structured subword splits. Expand prefix/root/suffix senses.
Does not reprogram host BPE.
"""

from __future__ import annotations

from typing import Dict, List, Optional
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
