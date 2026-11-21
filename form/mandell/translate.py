#!/usr/bin/env python3
"""45[Translate] — English → Mandell (phrases first, then patterns)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import re

from .phrases import match_phrase
from .morpheme import compose_sentence, sentence_gloss_lines, token_key


@dataclass
class Intent:
    action: str
    dell: Optional[int] = None
    term: str = ""
    args: Dict[str, Any] = field(default_factory=dict)
    mandel: str = ""
    english: str = ""
    # LM-4 THE TOLL BOOTH: the LatinMandell decomposition receipt
    # for the English this Intent was translated from (the forced
    # first READ). Computed ONCE by the translate() wrapper and
    # attached at its single exit point; None exactly when no
    # decomposition exists (empty input -- never fabricated).
    lm: Optional[Dict[str, Any]] = None
    # C9 DUAL MODE (DD-36): the engine receipt, attached ONLY by the
    # translate_dual() door — which layer translated (adapt / router
    # / dock / guard / none), the mode, and the deterministic layer's
    # confidence where meaningful. Canonical translate() never sets
    # it (None), so existing consumers see no change.
    engine: Optional[Dict[str, Any]] = None


# hint → action used by REPL
_HINT_ACTION = {
    "place": "place",
    "grow": "grow",
    "show": "show",
    "visual": "visual",
    "save": "save",
    "load": "load",
    "walk": "walk",
    "run": "run",
    "stop": "stop",
    "turn_left": "turn",
    "turn_right": "turn",
    "sit": "sit",
    "stand": "stand",
    "jump": "jump",
    "express_joy": "express",
    "express_calm": "express",
    "express_focus": "express",
    "avatar_status": "avatar_status",
    "enhance_on": "enhance_on",
    "enhance_off": "enhance_off",
    "pulse": "pulse",
    "sandbox_on": "sandbox_on",
    "sandbox_off": "sandbox_off",
    "status": "status",
    "help": "help",
    "proposals": "proposals",
    "merge": "place",
    "link": "place",
    "distill": "place",
    "compress": "place",
    "look": "look",
    "live": "live",
    "evolve": "evolve",
    "growth": "growth",
    "ledger": "ledger",
    "discover": "discover",
    # DCC-III: expanded semantic vocabulary
    "measure": "measure",
    "test": "test",
    "architect": "architect",
    "simulate": "simulate",
    "checkpoint": "checkpoint",
    "stamp": "stamp",
    "cycle": "cycle",
    "form": "form",
    "retry": "retry",
    "audit": "audit",
    "matrices": "matrices",
    "forces": "forces",
    "force_tick": "force_tick",
    "entities": "entities",
    "personas": "personas",
    "guide": "guide",
    "rooms": "rooms",
    "backstep": "backstep",
    "strafe": "strafe",
    "jog": "jog",
    "unzoom": "unzoom",
    "zoom": "zoom",
    "weather": "weather",
    "english_status": "english_status",
    "english_expand": "english_expand",
    "english_help": "english_help",
    "form_cube": "form",
    "form_sphere": "form",
    "form_core": "form",
    "form_flower": "form",
    "toggle_form": "toggle_form",
    "lattice": "lattice",
    "fp_forward": "fp_forward",
    "fp_back": "fp_back",
    "fp_up": "fp_up",
    "fp_down": "fp_down",
    "fp_turn_left": "fp_turn_left",
    "fp_turn_right": "fp_turn_right",
    # Nursery confirm/reject (must not fall to place)
    "confirm_all": "confirm_all",
    "reject_all": "reject_all",
    "rank": "rank",
    # Inspire + pages + workshops + geometry
    "page": "page",
    "home": "home",
    "nearest": "nearest",
    "multilook": "multilook",
    "attend": "attend",
    "slopes": "slopes",
    "prefs": "prefs",
    "glyph": "glyph",
    "inspire": "inspire",
    "workshops": "workshops",
    "workshop": "workshop",
    "workshop_leave": "workshop_leave",
    "bimo": "bimo",
    "bimo_fuse": "bimo_fuse",
    "bimo_defaults": "bimo_defaults",
    "geometry": "geometry",
    "verita": "verita",
    "voynich": "voynich",
    "fractal": "fractal",
    "mode": "mode",
    "view_first": "view_first",
    "view_map": "view_map",
    "ai_follow": "ai_follow",
    "ai_walk": "ai_walk",
    "ai_wander": "ai_wander",
    "ai_status": "ai_status",
    "force": "force",
    "recenter": "recenter",
    "lang_list": "lang_list",
}


# 72-06 Class E repair (Ace FIX-FIRST, 2026-11-05): spelled-out
# counts must be honored exactly like digits. The word table
# mirrors english_composer._WORD_NUM so bare translate() and the
# composite path accept the same words; conversion happens ONLY
# at count positions, never as a global text substitution, so
# user labels containing number words are never rewritten.
_COUNT_WORDS = {
    "once": 1, "twice": 2, "thrice": 3,
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
}


def _count_value(raw: Any, default: int = 1) -> int:
    """Parse a captured count token: digits or a number word."""
    s = str(raw or "").strip().lower()
    if s.isdigit():
        return int(s)
    return _COUNT_WORDS.get(s, default)


def _count_operand(raw: Any, default: int):
    """R19-SIB (Director ruling 6987078989, Q-A/Q-C): judge a
    captured count operand by the shared count grammar
    (executor_leaf._parse_count + the established count words).

    Returns the int value for a valid count, `default` for an
    absent/empty operand, or the RAW string for an explicitly
    malformed operand — the executing authority refuses raw
    counts typed. Nothing is silently defaulted (the _count_value
    behavior this replaces at the count doors), no Unicode digit
    is converted, and int() never sees an unbounded string.
    """
    s = str(raw or "").strip()
    if not s:
        return default
    low = s.lower()
    if low in _COUNT_WORDS:
        return _COUNT_WORDS[low]
    from form.mandell.executor_leaf import _parse_count
    n = _parse_count(s)
    return n if n is not None else s


# ------------------------------------------------------------------
# LM-4 THE TOLL BOOTH: the forced pass. translate() is a thin
# wrapper over _translate_body() (the pre-LM-4 translator, every
# arm unchanged). The wrapper computes the LatinMandell
# decomposition ONCE, at entry, on the text the body will
# actually translate, and attaches it to the returned Intent at
# this SINGLE exit point -- the body has ~77 return sites, and
# per-site attachment is how one gets missed (the suite's T3 pins
# every branch). The body's segmentation recursion calls the
# BODY, so segments never mint their own receipts; the outer
# call's receipt covers the whole input. english_composer calls
# the public translate() per clause, so each clause Intent
# carries its own clause-level receipt.
#
# The decomposition is a READ, not a routing input (grounding
# conflict C2): it never changes which Intent the body returns
# (T15 pins the pre-LM-4 baseline). FAIL-CLOSED: compose_sentence
# runs BEFORE the body; a PairInconsistentError from the LM
# table loader propagates out of translate() -- the line fails,
# nothing executes without a receipt (Q-LM4.4; never the silent
# no-decomposition execution).
# ------------------------------------------------------------------

# Argument keys whose VALUES echo the whole input rather than
# capturing an operand (the create arm's `raw`, the unknown arm's
# `query`). Every token would "match" an echo; echoes are not
# captures and never mark operands.
_LM4_ECHO_ARG_KEYS = ("raw", "query")


def _lm4_operand_keys(intent: Intent) -> set:
    """Normalized token keys captured as USER DATA by the body's
    arms: every string value in Intent.args (recursively),
    excluding the echo keys. Case is folded by token_key; the
    arms' own captures already preserve the user's case in args
    (D1 ARGUMENT_LOSS law) -- matching here is by lookup key."""
    keys = set()

    def _walk(v):
        if isinstance(v, str):
            for w in v.split():
                k = token_key(w)
                if k:
                    keys.add(k)
        elif isinstance(v, dict):
            for x in v.values():
                _walk(x)
        elif isinstance(v, (list, tuple)):
            for x in v:
                _walk(x)

    for k, v in (intent.args or {}).items():
        if k in _LM4_ECHO_ARG_KEYS:
            continue
        _walk(v)
    return keys


def _lm4_spine_mandell(sentence: Dict[str, Any]) -> str:
    """The spine as an NN[Dell] chain text -- a labeled READING
    (projection), distinct from the executed mandel string, which
    remains the authority for what ran. Dell names come from the
    existing registry (the SSI-I precedent); an unnamed Dell
    renders as its bare number."""
    parts = []
    for e in sentence.get("spine") or []:
        dell = e.get("dell")
        if dell is None:
            continue
        name = ""
        try:
            from .registry import get_dell
            rec = get_dell(dell)
            name = str((rec or {}).get("name") or "")
        except Exception:
            name = ""
        parts.append(f"{dell:02d}[{name}]" if name else f"{dell:02d}")
    return " > ".join(parts)


def _lm4_receipt(intent: Intent, sentence: Dict[str, Any]) -> Dict[str, Any]:
    """Assemble Intent.lm from the finished Intent + the entry
    decomposition. OPERAND post-pass: a token the arms captured
    as user data is reclassified OPERAND -- still traced (its
    decomposition is shown; it was still read), but removed from
    the spine and from Dell agreement, and the sentence figures
    that depend on spine/class are recomputed. A user naming an
    idea 'biology' must not make the sentence 'about' Dell
    selection for that token."""
    operands = _lm4_operand_keys(intent)
    if operands:
        for tok in sentence.get("tokens") or []:
            if tok.get("normalized") in operands \
                    and tok.get("role") != "operand":
                tok["class"] = "OPERAND"
                tok["role"] = "operand"
        sentence["spine"] = [
            {"token": t["token"], "dell": t["governing_dell"],
             "via": t["via"]}
            for t in sentence.get("tokens") or []
            if t.get("role") == "function"]
        dells = {e["dell"] for e in sentence["spine"]
                 if e["dell"] is not None}
        sentence["dell"] = dells.pop() if len(dells) == 1 else None
        n = len(sentence.get("tokens") or [])
        sentence["semantic_accounted"] = (
            sum(1 for t in sentence.get("tokens") or []
                if t.get("class") != "UNRESOLVED") / n if n else 0.0)
    structs = {t["structural_dell"]
               for t in sentence.get("tokens") or []
               if t.get("structural_dell") is not None}
    s_dell = structs.pop() if len(structs) == 1 else None
    g_dell = sentence.get("dell")
    agree = None if (s_dell is None or g_dell is None) \
        else (s_dell == g_dell)
    return {
        "sentence": sentence,
        "intent_dell": intent.dell,
        "spine_dell": sentence.get("dell"),
        "dell_diagnostic": {
            "structural_dell": s_dell,
            "governing_dell": g_dell,
            "agree": agree,
        },
        "presentation": {
            "gloss": sentence_gloss_lines(sentence),
            "spine_mandell": _lm4_spine_mandell(sentence),
        },
    }


# MPC-001 Track C2 / MPC-002: SEMANTIC LOSS GUARD markers (safety
# critical). If English contains conditional/qualifying clauses that
# would be silently dropped by translation, the result must be
# UNKNOWN rather than a weakened (especially destructive)
# instruction. A destructive operation may not execute after its
# limiting condition has been lost in translation. Extracted to
# module level (2026-11-21, C9) so _translate_body and the dual-mode
# door share ONE guard — no second copy to drift.
_CONDITIONAL_MARKERS = [
    r"\bif\b", r"\bunless\b", r"\bwhen\b", r"\bwhile\b", r"\buntil\b",
    r"\bprovided\b", r"\bassuming\b",
]
_NEGATION_MARKERS = [
    r"\bdon't\b", r"\bdo not\b", r"\bnever\b", r"\bnot\b",
]
_DESTRUCTIVE_VERBS = [
    r"\bdelete\b", r"\bremove\b", r"\bdestroy\b", r"\bclear\b",
    r"\bmove\b", r"\breplace\b", r"\boverwrite\b",
]


def _safety_blocked(raw_lower: str) -> bool:
    has_conditional = any(re.search(p, raw_lower) for p in _CONDITIONAL_MARKERS)
    has_negation = any(re.search(p, raw_lower) for p in _NEGATION_MARKERS)
    is_destructive = any(re.search(p, raw_lower) for p in _DESTRUCTIVE_VERBS)
    return (has_conditional or has_negation) and is_destructive


def translate(english: str) -> Intent:
    """English -> Intent, with the LM-4 decomposition attached.

    Empty input returns the body's nothing_to_translate Intent
    with NO receipt (no fabricated decomposition of nothing --
    the wrapper's guard order preserves the body's entry guard).
    Every other input is decomposed ONCE at entry; see the LM-4
    block above."""
    text = (english or "").strip()
    if not text:
        return _translate_body(english)
    sentence = compose_sentence(text)
    intent = _translate_body(english)
    intent.lm = _lm4_receipt(intent, sentence)
    return intent


def _translate_body(english: str) -> Intent:
    text = english.strip()
    # B6 (Director FIX, step 6): empty input reports
    # nothing_to_translate — no fabricated Show intent, no side
    # effects. This guard sits at the entry so bridge(), the leaf
    # Dell-45 arm and the English paths all inherit it.
    if not text:
        return Intent("nothing_to_translate", None, "", {}, "", "")
    # DCC-VI: operational capabilities on RAW text (before english_brain
    # rewrites "add idea X" -> "create an idea called X").
    raw_lower = text.lower().strip()
    # D1 circuit 3 (ARGUMENT_LOSS fix): routing matches run on the
    # lowercased text, but arguments that NAME user data (ids, keys,
    # labels, words) must keep the user's case — a store that has
    # 'A' is not found by source='a'. Sites below therefore
    # re-match their pattern against orig_text (the entry text,
    # pre-normalization) or the current text with re.IGNORECASE
    # and take captures from that match — the add-idea site's
    # m_orig precedent, generalized. Routing keywords, direction
    # words and closed vocabularies are deliberately left
    # lowercased. (R5: store keys joined the preserved class —
    # the get/find sites below capture them verbatim, because
    # Dell 55 stores lab keys raw; see the R5 note there.)
    orig_text = text
    # MPC-001 Track C2: SEMANTIC LOSS GUARD (safety critical) — the
    # marker logic lives in _safety_blocked() (module level) so the
    # C9 dual-mode door applies the identical guard; behavior here
    # is unchanged.
    if _safety_blocked(raw_lower):
        return Intent("unknown", None, "", {}, "09[Show] :: unknown", text)
    # MPC-001 Track C1: MULTI-INTENT SEGMENTATION.
    # If English contains explicit sequencing ("then", "and then"), try to
    # translate each segment and chain via existing Flow (>).
    # Reference words ("the copy", "it", "the result") become "last_result"
    # via existing Ω-056 authority. If any segment fails, return UNKNOWN
    # rather than a misrouted single operation.
    _SEQUENCE_MARKERS = [r"\bthen\b", r"\band then\b", r",\s*then\b"]
    has_sequence = any(re.search(p, raw_lower) for p in _SEQUENCE_MARKERS)
    if has_sequence:
        # Split on sequence markers
        parts = re.split(r"\bthen\b|\band then\b", raw_lower)
        parts = [p.strip(" ,") for p in parts if p.strip(" ,")]
        if len(parts) >= 2:
            # Translate each part (recursive, but guard against infinite recursion)
            # Replace reference words with last_result
            _REF_WORDS = [r"\bthe copy\b", r"\bit\b", r"\bthe result\b", r"\bthat\b"]
            translated = []
            for part in parts:
                # Substitute reference words
                for rw in _REF_WORDS:
                    part = re.sub(rw, "last_result", part)
                # Recursive translate (will not re-enter segmentation due to no "then")
                # LM-4: segments call the BODY -- the wrapper's
                # outer receipt covers the whole input; a segment
                # never mints its own sentence receipt.
                sub = _translate_body(part)
                if "unknown" in sub.mandel:
                    # Segment failed → whole thing is UNKNOWN (safe)
                    return Intent("unknown", None, "", {}, "09[Show] :: unknown", text)
                # Extract just the operation (strip Flow suffixes like "> 15[Map]")
                op = sub.mandel.split(" > ")[0]
                translated.append(op)
            # Chain via Flow
            chained = " > ".join(translated)
            return Intent("sequence", None, "Sequence", {}, chained, text)
    if re.search(r"\brevert\b", raw_lower):
        return Intent("load", 28, "Rollback", {}, "28[Rollback] :: load", text)
    if re.search(r"\bcount\s+nursery\b", raw_lower):
        return Intent("discover", 35, "Discover", {}, "35[Discover] :: count_nursery", text)
    if re.search(r"\blist\s+pending\b", raw_lower):
        return Intent("discover", 35, "Discover", {}, "35[Discover] :: list_pending", text)
    if re.search(r"\bcompare\s+nursery\b", raw_lower):
        return Intent("discover", 35, "Discover", {}, "35[Discover] :: compare_nursery", text)
    # DCC-XIV: lineage trace for one knowledge unit (before bare \btrace\b,
    # which would also match "trace lineage <id>" / "trace dependency <id>").
    m = re.search(r"\btrace\s+lineage\s+(\S+)", raw_lower)
    if m:
        m = re.search(r"\btrace\s+lineage\s+(\S+)", orig_text, re.IGNORECASE) or m
        return Intent("discover", 35, "Discover", {},
                      f"35[Discover] :: trace_lineage {m.group(1)}", text)
    # DCC-XV: dependency trace — historical lineage + current dependency status.
    m = re.search(r"\btrace\s+dependency\s+(\S+)", raw_lower)
    if m:
        m = re.search(r"\btrace\s+dependency\s+(\S+)", orig_text, re.IGNORECASE) or m
        return Intent("discover", 35, "Discover", {},
                      f"35[Discover] :: trace_dependency {m.group(1)}", text)
    # DCC-XVI: revision trace — which accepted version replaces which
    # (revision ancestry, not derivation ancestry).
    m = re.search(r"\btrace\s+revision\s+(\S+)", raw_lower)
    if m:
        m = re.search(r"\btrace\s+revision\s+(\S+)", orig_text, re.IGNORECASE) or m
        return Intent("discover", 35, "Discover", {},
                      f"35[Discover] :: trace_revision {m.group(1)}", text)
    # DCC-XIX: conflict trace — detection evidence + operator disposition
    # for one stable conflict ID (before bare \btrace\b).
    m = re.search(r"\btrace\s+conflict\s+(\S+)", raw_lower)
    if m:
        m = re.search(r"\btrace\s+conflict\s+(\S+)", orig_text, re.IGNORECASE) or m
        return Intent("discover", 35, "Discover", {},
                      f"35[Discover] :: trace_conflict {m.group(1)}", text)
    # DCC-XX: outcome trace — one exact outcome by stable ID; list recent
    # outcomes; outcomes involving a specific knowledge ID.
    m = re.search(r"\btrace\s+outcome\s+(\S+)", raw_lower)
    if m:
        m = re.search(r"\btrace\s+outcome\s+(\S+)", orig_text, re.IGNORECASE) or m
        return Intent("discover", 35, "Discover", {},
                      f"35[Discover] :: trace_outcome {m.group(1)}", text)
    if re.search(r"\blist\s+outcomes\b", raw_lower):
        return Intent("discover", 35, "Discover", {},
                      "35[Discover] :: list_outcomes", text)
    if re.search(r"\bshow\s+last\s+outcome\b", raw_lower):
        return Intent("discover", 35, "Discover", {},
                      "35[Discover] :: list_outcomes", text)
    m = re.search(r"\boutcomes\s+for\s+idea\s+(\S+)", raw_lower)
    if m:
        m = re.search(r"\boutcomes\s+for\s+idea\s+(\S+)", orig_text, re.IGNORECASE) or m
        return Intent("discover", 35, "Discover", {},
                      f"35[Discover] :: outcomes_for_idea {m.group(1)}", text)
    if re.search(r"\btrace\b", raw_lower):
        return Intent("discover", 35, "Discover", {}, "35[Discover] :: trace", text)
    # DCC-VII: query accepted/promoted knowledge.
    if re.search(r"\blist\s+confirmed\b", raw_lower):
        return Intent("discover", 35, "Discover", {}, "35[Discover] :: list_confirmed", text)
    if re.search(r"\bcount\s+confirmed\b", raw_lower):
        return Intent("discover", 35, "Discover", {}, "35[Discover] :: count_confirmed", text)
    m = re.search(r"\bfind\s+idea\s+(.+)$", raw_lower)
    if m:
        m = re.search(r"\bfind\s+idea\s+(.+)$", orig_text, re.IGNORECASE) or m
        query = m.group(1).strip()[:60]
        if query:
            return Intent("discover", 35, "Discover", {},
                         f"35[Discover] :: find_idea {query}", text)
    # DCC-XVI: versioned supersession — one explicit operation:
    # "supersede idea <old_id> with <new words>". Must precede the
    # "use idea" pattern (both start with an idea verb + id).
    m = re.search(r"\bsupersede\s+idea\s+(\S+)\s+with\s+(.+)$", raw_lower)
    if m:
        m = re.search(r"\bsupersede\s+idea\s+(\S+)\s+with\s+(.+)$", orig_text, re.IGNORECASE) or m
        old_id = m.group(1).strip()
        words = m.group(2).strip()[:240]
        if old_id and words:
            return Intent("nurture", 37, "Nurture", {},
                         f"37[Nurture] :: supersede {old_id} with {words}", text)
    # DCC-XIX: operator-governed conflict disposition — explicit routing
    # policy for one stable conflict, never a truth claim. Malformed IDs
    # are accepted here and refused honestly by the handler.
    m = re.search(r"\bresolve\s+conflict\s+(\S+)\s+prefer\s+(\S+)", raw_lower)
    if m:
        m = re.search(r"\bresolve\s+conflict\s+(\S+)\s+prefer\s+(\S+)", orig_text, re.IGNORECASE) or m
        cid, fav = m.group(1).strip(), m.group(2).strip()
        if cid and fav:
            return Intent("nurture", 37, "Nurture", {},
                         f"37[Nurture] :: resolve_conflict {cid} prefer {fav}", text)
    m = re.search(r"\bresolve\s+conflict\s+(\S+)\s+coexist\b", raw_lower)
    if m:
        m = re.search(r"\bresolve\s+conflict\s+(\S+)\s+coexist\b", orig_text, re.IGNORECASE) or m
        cid = m.group(1).strip()
        if cid:
            return Intent("nurture", 37, "Nurture", {},
                         f"37[Nurture] :: resolve_conflict {cid} coexist", text)
    m = re.search(r"\bclear\s+conflict\s+resolution\s+(\S+)", raw_lower)
    if m:
        m = re.search(r"\bclear\s+conflict\s+resolution\s+(\S+)", orig_text, re.IGNORECASE) or m
        cid = m.group(1).strip()
        if cid:
            return Intent("nurture", 37, "Nurture", {},
                         f"37[Nurture] :: clear_conflict_resolution {cid}", text)
    # DCC-VIII: explicit knowledge consumption.
    m = re.search(r"\buse\s+idea\s+(\S+)(?:\s+to\s+(\w+))?", raw_lower)
    if m:
        m = re.search(r"\buse\s+idea\s+(\S+)(?:\s+to\s+(\w+))?", orig_text, re.IGNORECASE) or m
        pid = m.group(1).strip()
        target = (m.group(2) or "grow").lower()
        if pid:
            return Intent("nurture", 37, "Nurture", {},
                         f"37[Nurture] :: use_idea {pid} to {target}", text)
    # DCC-IX: contextual knowledge selection.
    m = re.search(r"\bgrow\s+using\s+knowledge\s+about\s+(.+)$", raw_lower)
    if m:
        m = re.search(r"\bgrow\s+using\s+knowledge\s+about\s+(.+)$", orig_text, re.IGNORECASE) or m
        context = m.group(1).strip()[:80]
        if context:
            return Intent("nurture", 37, "Nurture", {},
                         f"37[Nurture] :: grow_using_knowledge_about {context}", text)
    m = re.search(r"\badd\s+idea\s+(.+)$", raw_lower)
    if m:
        label = m.group(1).strip()[:80]
        if not label:
            return Intent("unknown", None, "", {}, "09[Show] :: unknown", text)
        m_orig = re.search(r"\badd\s+idea\s+(.+)$", text, re.IGNORECASE)
        label_orig = m_orig.group(1).strip()[:80] if m_orig else label
        return Intent("nurture", 37, "Nurture", {"label": label_orig},
                      f"37[Nurture] :: {label_orig}", text)
    m = re.search(r"\bconfirm\s+(\S+)$", raw_lower)
    if m:
        m = re.search(r"\bconfirm\s+(\S+)$", orig_text, re.IGNORECASE) or m
        pid = m.group(1).strip()
        return Intent("nurture", 37, "Nurture", {"pid": pid, "op": "confirm"},
                      f"37[Nurture] :: confirm {pid}", text)
    m = re.search(r"\breject\s+(\S+)$", raw_lower)
    if m:
        m = re.search(r"\breject\s+(\S+)$", orig_text, re.IGNORECASE) or m
        pid = m.group(1).strip()
        return Intent("nurture", 37, "Nurture", {"pid": pid, "op": "reject"},
                      f"37[Nurture] :: reject {pid}", text)
    # English brain: politeness strip + paraphrase + synonym rewrite
    try:
        from form.mandell.english_brain import normalize_english
        normalized, _path = normalize_english(text)
        if normalized:
            text = normalized
    except Exception:
        pass
    lower = text.lower().strip()

    # 1) Stable phrase dictionary (preferred)
    hit = match_phrase(text)
    if hit:
        hint = hit["hint"]
        action = _HINT_ACTION.get(hint, "place")
        args: Dict[str, Any] = {}
        if action == "place":
            label = hit.get("label") or "idea"
            from form.idea_create import slug_id
            uid = slug_id(label)
            args = {"id": uid, "label": label.replace("_", " "), "words": label}
        elif action == "grow":
            # SM-11: the phrase pattern captures an explicit count
            # ("grow 3", "grow ideas 2", "evolve ideas 4") into the
            # hit label. That count must reach Intent.args — the
            # router's _seed_grow carries it into the Mandell label,
            # and Dell 13 clamps/reports it (1..5). Previously this
            # branch hard-coded 1 and the digit-aware branch below
            # was unreachable, so the user's count was silently
            # dropped while execution reported success.
            _lbl = str(hit.get("label") or "")
            # R19-SIB: "item" is match_phrase's no-capture sentinel
            # (an omitted count), not an operand. A captured count
            # is judged whole by _count_operand; the old
            # max(1, _count_value(...)) silently defaulted garbage
            # to 1, converted fullwidth digits, and floored 0.
            args = {"cycles": _count_operand(
                "" if _lbl == "item" else _lbl, 1)}
        elif action == "turn":
            args = {"direction": "left" if "left" in hint else "right"}
        elif action == "express":
            expr = "joy"
            if "calm" in hint:
                expr = "calm"
            elif "focus" in hint:
                expr = "focus"
            args = {"expression": expr}
        elif action == "walk":
            # SM-11: same dropped-count class — the walk phrase
            # pattern captures an explicit step count ("walk 2",
            # "walk forward 3") into the hit label; the REPL walk
            # handler reads steps from Intent.args. Hard-coding 1
            # silently dropped the user's count.
            _lbl = str(hit.get("label") or "")
            # R19-SIB: same judgment as the grow arm — "item" is
            # the omitted sentinel; malformed counts travel RAW
            # and the consuming door refuses them typed.
            args = {"steps": _count_operand(
                "" if _lbl == "item" else _lbl, 1)}
        elif action == "strafe":
            args = {"direction": "left" if "left" in lower else "right"}
        elif action == "zoom":
            # 72-06 Class D: the mandel now carries the operand
            # ("15[Map] :: zoom {label}"); the old {"ref": ...} arg
            # had no consumer anywhere in form/ or gui/ — retired.
            args = {}
        elif action == "weather":
            # 72-06 Class D: same — operand rides the mandel
            # ("25[Pulse] :: weather {label}"); {"condition": ...}
            # was dead (no consumer) — retired.
            args = {}
        elif action == "english_expand":
            # R19-SIB: default 50 only for a genuinely omitted
            # count (no label, or the "item" sentinel); a captured
            # count is judged whole — garbage no longer becomes a
            # silent 50 and oversized input no longer crashes.
            _lbl = str(hit.get("label") or "")
            n = 50 if _lbl in ("", "item") else _count_operand(_lbl, 50)
            args = {"cycles": n}
        elif action == "form":
            # DCC-III: extract form name from hint (form_sphere) or mandel.
            form_name = "cube"
            if "_" in hint:
                form_name = hint.split("_", 1)[1]
            elif hit.get("mandel"):
                m = re.search(r"15\[Map\] :: (\w+)", hit["mandel"])
                if m:
                    form_name = m.group(1)
            args = {"form": form_name}
        # DCC-III: derive Dell term from mandel for honest semantic reporting.
        # The hint is for action routing; the term is the Dell's canonical name.
        dell_term = hint
        m_term = re.search(r"\[\s*([A-Za-z]+)\s*\]", hit.get("mandel", ""))
        if m_term:
            dell_term = m_term.group(1)
        return Intent(
            action=action,
            mandel=hit["mandel"],
            english=text,
            args=args,
            term=dell_term,
        )

    # 2) Fallbacks (same spirit as before)
    if re.search(r"\b(save|keep|persist)(?:\s+session)?\b", lower):
        return Intent("save", 10, "Keep", {}, "10[Keep]", text)
    if re.search(r"\b(load|reload|restore)(?:\s+session)?\b", lower):
        return Intent("load", 28, "Rollback", {}, "28[Rollback] :: load", text)

    # Ω-057-C1: English reachability for signed operational semantics (84-88).
    # Uses raw_lower; must precede Dell19 locomotion fallbacks to distinguish
    # object relocation ("move A to B") from avatar movement ("move forward").
    # Dell19 preserved: directional movement still routes to Drive.
    # Articles stripped; multi-word phrases preserved.
    # Ω-057-C3: "set" removed from Dell88 pattern. Dell54 owns Set semantics.
    # Dell88 reachable only via explicit "patch" language.
    def _strip_article(s: str) -> str:
        s = s.strip()
        for art in ("the ", "a ", "an "):
            if s[:len(art)].lower() == art:
                return s[len(art):].strip()
        return s
    m = re.search(r"\bmove\s+(.+?)\s+to\s+(\S+)\s*$", raw_lower)
    if m:
        m = re.search(r"\bmove\s+(.+?)\s+to\s+(\S+)\s*$", orig_text, re.IGNORECASE) or m
        src = _strip_article(m.group(1))
        dst = m.group(2).strip()
        if src and dst and src.lower() not in ("forward", "ahead", "left", "right", "up", "down"):
            return Intent("move", 85, "Move",
                         {"source": src, "destination": dst},
                         f'85[Move](source="{src}", destination="{dst}")', text)
    m = re.search(r"\bcopy\s+(.+?)\s*$", raw_lower)
    if m:
        m = re.search(r"\bcopy\s+(.+?)\s*$", orig_text, re.IGNORECASE) or m
        src = _strip_article(m.group(1))
        # Don't capture trailing clauses ("and rename...")
        src = re.split(r"\s+and\s+", src, flags=re.IGNORECASE)[0].strip()
        if src:
            return Intent("copy", 84, "Copy",
                         {"source": src},
                         f'84[Copy](source="{src}")', text)
    m = re.search(r"\bdelete\s+(.+?)\s*$", raw_lower)
    if m:
        m = re.search(r"\bdelete\s+(.+?)\s*$", orig_text, re.IGNORECASE) or m
        key = _strip_article(m.group(1))
        # Don't capture conditionals ("if it's empty")
        key = re.split(r"\s+if\s+", key, flags=re.IGNORECASE)[0].strip()
        if key:
            return Intent("delete", 86, "Delete",
                         {"key": key},
                         f'86[Delete](key="{key}")', text)
    m = re.search(r"\breplace\s+(\S+)\s+with\s+(.+)$", raw_lower)
    if m:
        m = re.search(r"\breplace\s+(\S+)\s+with\s+(.+)$", orig_text, re.IGNORECASE) or m
        old = _strip_article(m.group(1))
        new = _strip_article(m.group(2).strip()[:60])
        if old and new:
            return Intent("replace", 87, "Replace",
                         {"old": old, "new": new},
                         f'87[Replace](old="{old}", new="{new}")', text)
    m = re.search(r"\bpatch\s+(\S+)\s+to\s+(.+)$", raw_lower)
    if m:
        m = re.search(r"\bpatch\s+(\S+)\s+to\s+(.+)$", orig_text, re.IGNORECASE) or m
        key = _strip_article(m.group(1))
        val = m.group(2).strip()[:60]
        if key and val:
            return Intent("patch", 88, "Patch",
                         {"key": key, "value": val},
                         f'88[Patch](key="{key}", value="{val}")', text)

    # Ω-058-C1: English reachability for Dell56 (Get) object retrieval.
    # Dell56 has no typed signature; uses legacy lab mechanism: 56[Get] :: key
    # AMBIGUITY GUARDS: Only specific-object retrieval. Do NOT capture:
    # - "find ideas about X" (idea search)
    # - "find previous/interaction/history" (history retrieval)
    # - "find knowledge about X" (knowledge retrieval)
    # - "find everything/all matching X" (pattern search → Dell58)
    # - "find X about Y" (topic search)
    def _is_ambiguous_find(phrase: str) -> bool:
        ambiguous_markers = [
            "ideas", "idea", "previous", "interaction", "history",
            "knowledge", "everything", "all ", "about", "matching",
        ]
        pl = phrase.lower()
        return any(marker in pl for marker in ambiguous_markers)
    # get <key> → Dell56 (specific object retrieval)
    # MPC-002: Updated to typed format (validates via new signature)
    # D1 reconciliation R5 (ARGUMENT_LOSS end-to-end): the key is
    # a USER OPERAND. Detection runs on raw_lower, but the capture
    # is re-matched against orig_text (the circuit-3 precedent)
    # and preserved exactly — case AND spaces. Store keys are
    # raw: Dell 55 writes the lab key verbatim, so the old
    # slug normalization (lowercase + underscores) made 'A'
    # unreadable as 'a' and spaced keys unreachable entirely.
    m = re.search(r"\bget\s+(.+?)\s*$", raw_lower)
    if m:
        mo = re.search(r"\bget\s+(.+?)\s*$", orig_text, re.IGNORECASE)
        key = _strip_article((mo or m).group(1))
        # Don't capture "get up", "get going" (phrasal verbs)
        if key and key.lower() not in ("up", "going", "down", "out") and not _is_ambiguous_find(key):
            return Intent("get", 56, "Get",
                         {"key": key},
                         f'56[Get](key="{key}")', text)
    # find <key> → Dell56 ONLY for specific object (definite, no ambiguity markers)
    # MPC-002: Updated to typed format; R5: operand preserved as for get.
    m = re.search(r"\bfind\s+(.+?)\s*$", raw_lower)
    if m:
        mo = re.search(r"\bfind\s+(.+?)\s*$", orig_text, re.IGNORECASE)
        phrase = (mo or m).group(1).strip()
        # Must have definite article or be a simple noun phrase
        # Must NOT have ambiguity markers
        if phrase and not _is_ambiguous_find(phrase):
            key = _strip_article(phrase)
            # Only if it's a simple object reference (no "about", no complex clauses)
            if key and len(key.split()) <= 3:
                return Intent("find", 56, "Get",
                             {"key": key},
                             f'56[Get](key="{key}")', text)

    # MPC-002: Bounded English for retrieval family (51, 58).
    # Dell51 Select: "select X" → typed predicate
    # Dell58 Match: "search for X" / "find X matching Y" → typed pattern
    # Preserves distinctions: select vs query vs match vs get.
    m = re.search(r"\bselect\s+(.+?)\s*$", raw_lower)
    if m:
        m = re.search(r"\bselect\s+(.+?)\s*$", orig_text, re.IGNORECASE) or m
        pred = _strip_article(m.group(1))
        if pred and not _is_ambiguous_find(pred):
            # Use typed format (validates via new signature)
            safe_pred = pred.replace('"', '')[:60]
            return Intent("select", 51, "Select",
                         {"predicate": safe_pred},
                         f'51[Select](predicate="{safe_pred}")', text)
    m = re.search(r"\bsearch\s+for\s+(.+?)\s*$", raw_lower)
    if m:
        m = re.search(r"\bsearch\s+for\s+(.+?)\s*$", orig_text, re.IGNORECASE) or m
        pat = _strip_article(m.group(1))
        if pat:
            safe_pat = pat.replace('"', '')[:60]
            return Intent("match", 58, "Match",
                         {"pattern": safe_pat},
                         f'58[Match](pattern="{safe_pat}")', text)

    if re.search(r"\b(walk|go|move)\s+(forward|ahead)\b", lower) or lower in ("walk", "go forward"):
        # R19-SIB: this fallback fires when the strict walk phrase
        # did not claim the text — e.g. "walk forward banana". A
        # token after the direction word is a count operand and is
        # judged whole (RAW travel when malformed; the REPL walk
        # handler refuses it typed). No token: the default 1.
        _mtail = re.search(r"\b(?:forward|ahead)\b\s+(\S+)", lower)
        _steps = _count_operand(_mtail.group(1), 1) if _mtail else 1
        return Intent("walk", 19, "Drive", {"steps": _steps}, "19[Drive] :: walk", text)
    if re.search(r"\b(backstep|back\s*step|step\s+back)\b", lower) or lower in ("s", "back"):
        return Intent("backstep", 19, "Drive", {"steps": 1}, "19[Drive] :: backstep", text)
    if re.search(r"\bstrafe\s+(left|right|l|r)\b", lower):
        d = "left" if re.search(r"\bleft\b|\bl\b", lower.split("strafe", 1)[-1]) else "right"
        return Intent("strafe", 19, "Drive", {"direction": d, "steps": 1}, f"19[Drive] :: strafe_{d}", text)
    if re.search(r"\bjog\b", lower):
        return Intent("jog", 19, "Drive", {}, "19[Drive] :: jog", text)
    if re.search(r"\brun\b", lower):
        return Intent("run", 19, "Drive", {}, "19[Drive] :: run", text)
    if re.search(r"\b(stop|halt|idle)\b", lower):
        return Intent("stop", 32, "Pause", {}, "32[Pause] :: stop", text)
    if re.search(r"\bturn\s+(left|right)\b", lower):
        d = "left" if "left" in lower else "right"
        return Intent("turn", 4, "Transform", {"direction": d}, f"04[Transform] :: turn_{d}", text)
    if re.search(r"\b(sit|sit\s+down)\b", lower):
        return Intent("sit", 4, "Transform", {}, "04[Transform] :: sit", text)
    if re.search(r"\b(stand|stand\s+up)\b", lower):
        return Intent("stand", 4, "Transform", {}, "04[Transform] :: stand", text)
    if re.search(r"\b(jump)\b", lower):
        return Intent("jump", 4, "Transform", {}, "04[Transform] :: jump", text)

    if re.search(r"\b(smile|happy|joy)\b", lower):
        return Intent("express", 5, "Tone", {"expression": "joy"}, "05[Tone] :: joy", text)
    if re.search(r"\b(calm|relax)\b", lower):
        return Intent("express", 5, "Tone", {"expression": "calm"}, "05[Tone] :: calm", text)
    if re.search(r"\b(focus)\b", lower):
        return Intent("express", 5, "Tone", {"expression": "focus"}, "05[Tone] :: focus", text)
    if re.search(r"\b(how\s+do\s+i\s+look)\b", lower):
        return Intent("avatar_status", 9, "Show", {}, "09[Show] :: avatar", text)

    m = re.search(r"(?:create|add|make|new|place|plant)\s+(?:an?\s+)?(?:idea\s+)?(?:called\s+)?(.+)$", text, re.IGNORECASE)
    if m:
        # Keep original casing from text for label body; strong parse happens in handlers
        body = m.group(1).strip().strip("'")
        # strip detail/goals from id slug only
        label_only = re.split(r"\bdetail\s*:|\bgoals\s*:", body, maxsplit=1, flags=re.I)[0].strip()
        from form.idea_create import slug_id
        uid = slug_id(label_only)
        # TOAM-I: preserve name argument in Seed (Dell 8 signature requires 'name')
        safe_name = (label_only or body[:48]).replace('"', '')
        return Intent(
            "place",
            8,
            "Create",
            {"id": uid, "label": label_only or body[:48], "words": body[:120], "raw": text},
            f'08[Create](name="{safe_name}") > 15[Map] :: {uid}',
            text,
        )

    if re.search(r"\b(evolve\s+program|grow\s+program|level\s+up)\b", lower) or lower == "evolve":
        return Intent("evolve", 13, "Loop", {}, "13[Loop] :: evolve", text)
    if re.search(r"\bgrow\b", lower) or re.search(r"\bevolve\s+ideas?\b", lower):
        # R19-SIB (Q-C): this fallback catches every grow phrase
        # the strict patterns did not claim — including ones with
        # an explicit malformed count ("grow banana", "grow -3",
        # "grow 20x"). The trailing operand is judged whole: a
        # valid count travels, an absent/filler tail keeps the
        # default 1, and anything else travels RAW so Dell 13
        # refuses it typed. Malformed counts reach refusal, never
        # fallback growth.
        _toks = lower.split()
        while _toks and _toks[-1] in ("idea", "ideas"):
            _toks.pop()
        _operand = ""
        if _toks and _toks[-1] not in ("grow", "evolve"):
            _operand = _toks[-1]
        return Intent("grow", 13, "Loop",
                      {"cycles": _count_operand(_operand, 1)},
                      "13[Loop] > 04[Transform] :: grow", text)
    # DCC-III: expanded semantic vocabulary (all route through Dell authority).
    # Note: stamp/cycle/form (with args) checked before bare nouns to avoid
    # substring matches (e.g. "test" in "test-mark").
    m = re.search(r"\b(stamp|mark)\s+(.+)$", text, re.IGNORECASE)
    if m:
        mark = m.group(2).strip()[:48] or "mark"
        return Intent("stamp", 34, "Stamp", {"mark": mark}, f"34[Stamp] :: {mark}", text)
    if re.search(r"\b(measure|session\s+weight|how\s+heavy)\b", lower):
        return Intent("measure", 40, "TokenCount", {}, "40[TokenCount]", text)
    if re.search(r"\b(self[\s-]?test|check\s+systems|\btest\b)", lower):
        return Intent("test", 12, "Test", {}, "12[Test]", text)
    if re.search(r"\b(architect|show\s+schema)\b", lower):
        return Intent("architect", 11, "Architect", {}, "11[Architect]", text)
    if re.search(r"\b(simulate|dry[\s-]?run|what\s+would\s+happen)\b", lower):
        return Intent("simulate", 31, "Simulate", {}, "31[Simulate]", text)
    if re.search(r"\b(checkpoint|save\s+a\s+checkpoint|make\s+a\s+checkpoint)\b", lower):
        return Intent("checkpoint", 27, "Checkpoint", {}, "27[Checkpoint]", text)
    m = re.search(r"\b(cycle|run\s+cycles?)\b", lower)
    if m:
        # R19 (Director correction 6986258354): distinguish an
        # OMITTED count (default 1) from an EXPLICIT operand, and
        # consume the operand as a whole token. The previous
        # optional-capture regex silently executed 1 for
        # "cycle banana" / "cycle -3" / "cycle ²", stole the
        # prefix of "cycle 20x" (executed 20), converted the
        # fullwidth "cycle ２０" to 20, and crashed outright on
        # an oversized digit string (int() digit limit). Now: a
        # valid count (ASCII digits within the leaf grammar's
        # length bound, or an established number word) travels as
        # an int with NO clamp and NO floor — the Dell 6 leaf
        # clamps + reports (0 included). Any other explicit token
        # travels RAW in the args/seed so the leaf refuses it
        # typed (invalid_cycle_count, no growth), exactly as the
        # router path carries raw labels. Length is checked
        # before any int conversion.
        tok_m = re.match(r"\s*(\S+)", lower[m.end():])
        tok = tok_m.group(1) if tok_m else None
        if tok is None or tok == "times":
            n: Any = 1
        elif tok in _COUNT_WORDS:
            n = _COUNT_WORDS[tok]
        elif tok.isascii() and tok.isdigit() and len(tok) <= 9:
            n = int(tok)
        else:
            n = tok
        return Intent("cycle", 6, "Cycle", {"count": n}, f"06[Cycle] :: {n}", text)
    m = re.search(r"\bform\s+(cube|sphere|core|flower)\b", lower)
    if m:
        form_name = m.group(1)
        return Intent("form", 15, "Map", {"form": form_name}, f"15[Map] :: {form_name}", text)
    if re.search(r"\b(retry|repeat\s+last)\b", lower):
        return Intent("retry", 42, "Retry", {}, "42[Retry]", text)
    if re.search(r"\b(show|display)\b", lower):
        return Intent("show", 9, "Show", {}, "09[Show]", text)
    if re.search(r"\b(visual|workspace)\b", lower):
        return Intent("visual", 9, "Show", {}, "09[Show] >> 47[Embed] :: visual", text)
    if re.search(r"\benhance\s+on\b", lower):
        return Intent("enhance_on", 25, "Pulse", {}, "25[Pulse] :: enhance_on", text)
    if re.search(r"\benhance\s+off\b", lower):
        return Intent("enhance_off", 32, "Pause", {}, "32[Pause] :: enhance_off", text)
    if re.search(r"\bpulse\b", lower):
        return Intent("pulse", 25, "Pulse", {}, "25[Pulse]", text)
    if re.search(r"\bstatus\b", lower):
        return Intent("status", 35, "Discover", {}, "35[Discover]", text)
    if re.search(r"\bhelp\b", lower):
        return Intent("help", 9, "Show", {}, "09[Show] :: help", text)

    # SSI-I: explicit canonical Core-II operator references.
    # `dell 74`, `74[Weight]`, optionally with `:: label`.
    # No loose prose aliases — canonical wording only. Identity and
    # policy (blocked/raw-only) are decided downstream by the bridge
    # resolver inside route_intent; translate only recognizes the reference.
    m = re.search(r"\bdell\s+([5-9]\d)\b", lower)
    if not m:
        m = re.search(r"\b([5-9]\d)\[([A-Za-z]+)\]", text)
    if m:
        n = int(m.group(1))
        from .registry import get_dell as _get_dell
        rec = _get_dell(n)
        if rec is not None and str(rec.get("namespace", "")) == "CORE_II":
            name = str(rec.get("name", ""))
            label = ""
            if "::" in text:
                label = text.split("::", 1)[1].strip()[:120]
            mandel = f"{n:02d}[{name}]"
            if label:
                mandel += f" :: {label}"
            return Intent(name.lower(), n, name, {"label": label}, mandel, text)
        # Not a Core-II address: fall through to unknown (never guess).

    # Explicit plant/note without create verb (short noun phrases only when intentional)
    # e.g. "plant Garden Gate" already handled as create synonym via english_brain.
    # Never free-hash unknown text into ideas — that destroys usability.
    return Intent(
        "unknown",
        9,
        "Show",
        {"query": text[:80]},
        "09[Show] :: unknown",
        text,
    )




# ---------------------------------------------------------------------------
# C9 DUAL MODE (DD-36 as amended by SS12.34b; Ace "not yet" lifted by
# his 2026-11-20 ruling, item 10 — row #157 Adapt: NOW).
#
# Layering inside Dell 45: (1) the deterministic Adapt-architecture
# layer (adapt_intent.py) determines intent + entities + confidence
# FIRST; (2) the canonical cascade above still CONSTRUCTS the Intent —
# operands and canonical meaning have exactly one authority; (3) in
# docked mode the canonical cascade stands in for the docked AI's
# understanding, and residue is marked proposal-only: the dock may
# PROPOSE a translation as pending work, this door never invents one.
# DD-35 binds both modes: beyond the honest deterministic subset, the
# undocked door returns an explicit no_intent — dell None, mandel ""
# — never an invented Show seed. Canonical translate() is unchanged.
# ---------------------------------------------------------------------------
from .adapt_intent import build_default_engine  # noqa: E402

_DUAL_ENGINE = None
_DUAL_CONFIDENCE_FLOOR = 0.5


def _dual_engine():
    global _DUAL_ENGINE
    if _DUAL_ENGINE is None:
        _DUAL_ENGINE = build_default_engine()
    return _DUAL_ENGINE


def adapt_determine(english: str):
    """Translate as a TOOL (SS12.34b item 3): the deterministic layer,
    callable on its own — by the docked AI or any caller — so the
    model does not have to do the grind of command-shaped English.
    Returns a Determination or None. Never calls translate(): the
    layer is determination-only, so no Translate<->dock loop exists.
    """
    return _dual_engine().determine((english or "").strip())


def translate_dual(english: str, *, docked: bool = False) -> Intent:
    """The dual-mode door (DD-36). Every result carries an engine
    receipt on Intent.engine naming the layer that translated.

    Undocked: safety guard first (layer "guard"); then the Adapt
    layer — when its determination agrees with the canonical
    construction, the receipt names layer "adapt" with its
    confidence; when the canonical router carries a text the Adapt
    layer did not determine (compounds, richer families), the
    receipt names layer "router" and records any disagreement as
    adapt_mismatch; when neither layer honestly parses the text,
    DD-35: an explicit no_intent (layer "none").

    Docked: the canonical result stands (layer "dock"); an unknown
    result is residue — receipt residue/proposal_only True — the
    docked AI may propose a translation as pending work under the
    dock's proposal discipline; nothing is invented here.
    """
    text = (english or "").strip()
    mode = "docked" if docked else "undocked"
    if not text:
        base = _translate_body(english)
        base.engine = {"mode": mode, "layer": "none", "confidence": None,
                       "intent_type": None, "reason": "empty_input"}
        return base
    if docked:
        intent = translate(english)
        residue = intent.action == "unknown"
        intent.engine = {"mode": mode, "layer": "dock", "confidence": None,
                         "intent_type": None, "residue": residue,
                         "proposal_only": residue}
        return intent
    if _safety_blocked(text.lower()):
        intent = translate(english)
        intent.engine = {"mode": mode, "layer": "guard", "confidence": None,
                         "intent_type": None,
                         "reason": "conditional_or_negated_destructive"}
        return intent
    det = adapt_determine(text)
    intent = translate(english)
    if (det is not None and det.confidence >= _DUAL_CONFIDENCE_FLOOR
            and intent.action == det.action):
        intent.engine = {"mode": mode, "layer": "adapt",
                         "confidence": det.confidence,
                         "intent_type": det.intent_type,
                         "entities": det.entities}
        return intent
    if intent.action != "unknown":
        receipt = {"mode": mode, "layer": "router",
                   "confidence": det.confidence if det else None,
                   "intent_type": det.intent_type if det else None}
        if det is not None and det.action != intent.action:
            receipt["adapt_mismatch"] = det.intent_type
        intent.engine = receipt
        return intent
    # DD-35: honest no-intent. The canonical unknown's LM-4 receipt is
    # carried over (the decomposition exists and is real); the
    # invented Show seed form is NOT carried — mandel stays "".
    ni = Intent("no_intent", None, "", {}, "", text)
    ni.lm = intent.lm
    ni.engine = {"mode": mode, "layer": "none",
                 "confidence": det.confidence if det else None,
                 "intent_type": det.intent_type if det else None,
                 "reason": "no_deterministic_intent"}
    return ni
