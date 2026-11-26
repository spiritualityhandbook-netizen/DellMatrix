#!/usr/bin/env python3
"""GP-E08 — Typed English/LM/Seed admission (Part II, anchor row #24).

One lossless AST over the three existing doors:

    raw user text -> explicit typed roles -> operator -> operand
    -> execution mode, with source-span provenance and an
    ambiguity verdict.

This layer creates NO second parser. It classifies the door the
REPL itself would take — LatinMandell (`la `/`latin ` prefix,
via polyglot.bridge_lang, the REPL's own LM handler path), seed
(seed.looks_like_seed / seed.parse_seed), English
(translate.translate) — and renders that door's own result as a
typed Admission. Legacy door semantics are preserved untouched:
translate(), parse_seed() and bridge_lang() are not modified,
and an unambiguous case admits exactly what the door produces.

What the layer ADDS over the bare doors:

- LOSSLESS RAW: the Admission carries the user's text verbatim.
- TYPED ROLES: every role declares a type. English-door args in
  ARG_TYPES must arrive with the declared type; a mis-typed role
  is rejected BEFORE any caller can route it (mistyped_role:<k>).
- SPAN PROVENANCE: a role whose surface token is literally in the
  raw text carries its (start, end) span and provenance
  "literal"; a door-supplied default (Class E: the count the
  door fills in when the user wrote none) is disclosed with
  provenance "default" and NO span — the default is never silent
  in the AST; anything computed carries "derived".
- AMBIGUITY VERDICT: text that CLAIMS seed form (an atom-shaped
  fragment `NN[`) but fails seed parsing is rejected at this
  door (seed_parse_refusal, with the parser's positioned error
  as detail) instead of falling through to an English guess.
  Unresolvable English (the translator's `unknown`, including
  the semantic-loss guard) is rejected as no_intent; empty input
  as nothing_to_translate; an unmapped LatinMandell phrase as
  unresolved_latinmandell.

Admission is pure: it takes no Program and mutates nothing. The
caller contract — route only admitted admissions — is what makes
every rejection a rejection BEFORE mutation; GP-E08's suite
proves it end-to-end against route_intent on isolated owners.

Verification instrument: the modernized #308 oracle
(director-reports/evidence/72-06-intent-args/, merged f9a275ca),
adopted by reference per PART_II_PLAN §6 — not duplicated here.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple

from .polyglot import bridge_lang
from .seed import Seed, looks_like_seed, parse_seed
from .translate import Intent, _COUNT_WORDS, translate

# Declared types for English-door Intent.args keys. An admitted
# Intent whose listed arg arrives with any other type is a
# mis-typed role and is refused here, before routing.
ARG_TYPES: Dict[str, type] = {"count": int, "cycles": int, "steps": int}

# A seed-atom-shaped fragment anywhere in the text is a seed
# CLAIM: the text is held to seed grammar, never reinterpreted
# as English prose about brackets.
_SEED_FRAGMENT = re.compile(r"\d{1,3}\s*\[")


@dataclass(frozen=True)
class Role:
    name: str            # "operator" | "operand" | "atom" | "flow"
                         # | "label" | "lm_source" | "arg:<key>"
    value: Any
    type: str            # "action" | "mandell" | "dell_atom" |
                         # "flow_op" | "label" | "str" | "int" | ...
    span: Optional[Tuple[int, int]] = None
    provenance: str = "derived"   # "literal" | "derived" | "default"


@dataclass(frozen=True)
class Admission:
    raw: str
    kind: str            # "empty" | "seed" | "latinmandell" | "english"
    verdict: str         # "admitted" | "rejected"
    reason: str = ""     # refusal code when rejected
    detail: str = ""     # positioned/typed detail for a refusal
    mode: str = "none"   # "single" | "chain" | "sequence" | "none"
    roles: Tuple[Role, ...] = ()
    intent: Optional[Intent] = None
    seed: Optional[Seed] = None

    def role(self, name: str) -> Optional[Role]:
        for r in self.roles:
            if r.name == name:
                return r
        return None


def _find(pattern: str, text: str, start: int = 0,
          flags: int = 0) -> Optional[Tuple[int, int]]:
    m = re.search(pattern, text[start:], flags)
    if not m:
        return None
    return (start + m.start(), start + m.end())


def _int_span(value: int, raw: str) -> Optional[Tuple[int, int]]:
    """Locate an int arg's surface token: the digit form first,
    then any count word naming the same value (the door's own
    _COUNT_WORDS table — reused, not duplicated)."""
    surfaces = [str(value)] + [w for w, v in _COUNT_WORDS.items()
                               if v == value]
    for surf in surfaces:
        span = _find(rf"\b{re.escape(surf)}\b", raw, flags=re.IGNORECASE)
        if span is not None:
            return span
    return None


def _arg_role(key: str, value: Any, raw: str) -> Role:
    type_name = ARG_TYPES[key].__name__ if key in ARG_TYPES \
        else type(value).__name__
    span: Optional[Tuple[int, int]] = None
    provenance = "derived"
    if isinstance(value, bool):
        pass
    elif isinstance(value, int):
        span = _int_span(value, raw)
        if span is not None:
            provenance = "literal"
        elif key in ARG_TYPES:
            # A declared-type arg with no surface token in the raw
            # text is the door's own default, disclosed as such.
            provenance = "default"
    elif isinstance(value, str) and value:
        span = _find(re.escape(value), raw) or _find(
            re.escape(value), raw, flags=re.IGNORECASE)
        if span is not None:
            provenance = "literal"
    return Role(name=f"arg:{key}", value=value, type=type_name,
                span=span, provenance=provenance)


def _from_intent(intent: Intent, raw: str, kind: str) -> Admission:
    """Render one door-produced Intent as a typed Admission."""
    if intent.action == "nothing_to_translate":
        return Admission(raw=raw, kind=kind, verdict="rejected",
                         reason="nothing_to_translate", intent=intent)
    if intent.action == "unknown":
        # Covers plain no-correspondence AND the translator's
        # semantic-loss guard (conditional/negated destructive
        # text): both surface at this door as an explicit refusal,
        # never as a weakened executable intent.
        return Admission(raw=raw, kind=kind, verdict="rejected",
                         reason="no_intent", intent=intent)
    for key, want in ARG_TYPES.items():
        if key in intent.args:
            got = intent.args[key]
            if isinstance(got, bool) or not isinstance(got, want):
                return Admission(
                    raw=raw, kind=kind, verdict="rejected",
                    reason=f"mistyped_role:{key}",
                    detail=f"arg {key}: expected {want.__name__}, "
                           f"got {type(got).__name__}",
                    intent=intent)
    roles = [
        Role(name="operator",
             value={"action": intent.action, "dell": intent.dell},
             type="action"),
        Role(name="operand", value=intent.mandel, type="mandell"),
    ]
    for key in sorted(intent.args):
        roles.append(_arg_role(key, intent.args[key], raw))
    return Admission(
        raw=raw, kind=kind, verdict="admitted",
        mode="sequence" if intent.action == "sequence" else "single",
        roles=tuple(roles), intent=intent)


def _from_seed(seed: Seed, raw: str, body: str, offset: int) -> Admission:
    """Render a parsed Seed as a typed Admission. Spans are
    located in the parsed body and rebased onto the raw text."""
    def rebase(span: Optional[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
        if span is None:
            return None
        return (span[0] + offset, span[1] + offset)

    roles = []
    cursor = 0
    atom_spans = []
    for i, atom in enumerate(seed.atoms):
        span = _find(rf"0*{atom.dell}\[\s*{re.escape(atom.term)}\s*\]",
                     body, cursor)
        atom_spans.append(span)
        if span is not None:
            cursor = span[1]
        roles.append(Role(
            name="atom",
            value={"dell": atom.dell, "term": atom.term,
                   "resolved_term": atom.resolved_term},
            type="dell_atom", span=rebase(span), provenance="literal"))
        for key in sorted(atom.args):
            surf = f'{key}="{atom.args[key]}"'
            aspan = _find(re.escape(surf), body, cursor)
            if aspan is not None:
                cursor = aspan[1]
            roles.append(Role(name=f"arg:{key}", value=atom.args[key],
                              type="str", span=rebase(aspan),
                              provenance="literal"))
        if i < len(seed.flows):
            fspan = _find(re.escape(seed.flows[i]), body, cursor)
            if fspan is not None:
                cursor = fspan[1]
            roles.append(Role(name="flow", value=seed.flows[i],
                              type="flow_op", span=rebase(fspan),
                              provenance="literal"))
    if seed.label:
        lspan = _find(re.escape(seed.label), body,
                      atom_spans[-1][1] if atom_spans and atom_spans[-1]
                      else cursor)
        roles.append(Role(name="label", value=seed.label, type="label",
                          span=rebase(lspan), provenance="literal"))
    if seed.atoms:
        first = seed.atoms[0]
        roles.insert(0, Role(
            name="operator",
            value={"dell": first.dell, "term": first.term},
            type="dell_atom", span=rebase(atom_spans[0]),
            provenance="literal"))
    roles.append(Role(name="operand", value=seed.as_mandel(),
                      type="mandell"))
    return Admission(
        raw=raw, kind="seed", verdict="admitted",
        mode="chain" if len(seed.atoms) > 1 else "single",
        roles=tuple(roles), seed=seed)


def admit(text: Any) -> Admission:
    """Admit one raw line through the typed admission layer."""
    raw = "" if text is None else str(text)
    body = raw.strip()
    if not body:
        return Admission(raw=raw, kind="empty", verdict="rejected",
                         reason="nothing_to_translate")
    lower = body.lower()

    # LatinMandell door — the REPL's own claim: `la `/`latin `
    # prefix, resolved through bridge_lang exactly as the REPL's
    # handler resolves it, then executed as the bridged English.
    if lower.startswith("la ") or lower.startswith("latin "):
        rest = body.split(maxsplit=1)[1]
        rep = bridge_lang("la", rest)
        lm_role = Role(name="lm_source", value=rest, type="str",
                       span=_find(re.escape(rest), raw),
                       provenance="literal")
        if rep.get("ok") != "true":
            return Admission(raw=raw, kind="latinmandell",
                             verdict="rejected",
                             reason="unresolved_latinmandell",
                             detail=rep.get("note", ""),
                             roles=(lm_role,))
        adm = _from_intent(translate(rep.get("english", "")), raw,
                           "latinmandell")
        return Admission(raw=adm.raw, kind=adm.kind, verdict=adm.verdict,
                         reason=adm.reason, detail=adm.detail,
                         mode=adm.mode, roles=(lm_role,) + adm.roles,
                         intent=adm.intent, seed=adm.seed)

    # Seed door — a seed-shaped line, or any line carrying an
    # atom-shaped fragment, is held to seed grammar.
    if looks_like_seed(body) or _SEED_FRAGMENT.search(body):
        seed = parse_seed(body)
        if not seed.ok:
            return Admission(raw=raw, kind="seed", verdict="rejected",
                             reason="seed_parse_refusal",
                             detail=seed.error, seed=seed)
        offset = raw.find(body)
        return _from_seed(seed, raw, body, offset if offset >= 0 else 0)

    # English door.
    return _from_intent(translate(raw), raw, "english")
