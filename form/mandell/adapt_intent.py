#!/usr/bin/env python3
"""Deterministic intent determination — the Adapt layer inside Dell 45.

DD-36 / SS12.34a-b (ACE_FUTURE_DEVELOPMENT_PLAN): Translate is
dual-mode. The deterministic layer comes FIRST: vocabulary + entity
tagging -> intent + confidence + tagged entities, for the
command-shaped English that can honestly be parsed without a model.
The existing pattern router's families are this layer's vocabulary;
the canonical cascade still constructs the Intent (see translate.py:
translate_dual) — this module DETERMINES, it never constructs
Mandell, never executes, and never imports translate (no
Translate<->dock loop by construction).

CREDIT (Ace, SS12.34b item 2 — credit where it belongs): this layer
implements the architecture of the Adapt Intent Parser, by the
Mycroft AI team (team led by Sean Fitzgerald), Apache-2.0
(github.com/MycroftAI/adapt). Ace ruled ADOPT-with-credit; the
library itself is not vendored because the DellMatrix runtime is
stdlib-only (requirements.txt) and offline-first — the approach is
adapted in-tree, the credit stands in full. Classification per the
external-idea law: ADAPT (approach), with the adoption decision and
its grounds recorded on PR #505.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Tuple

ADAPT_CREDIT = (
    "Adapt Intent Parser — Mycroft AI (team led by Sean Fitzgerald), "
    "Apache-2.0; architecture adapted in-tree for DellMatrix "
    "(DD-36 / SS12.34b, PR #505)."
)


@dataclass
class Determination:
    """One determined intent: type, canonical action, tagged entities."""
    intent_type: str
    action: str
    entities: Dict[str, List[str]] = field(default_factory=dict)
    confidence: float = 0.0
    utterance: str = ""


@dataclass
class _IntentSpec:
    intent_type: str
    action: str
    required: Tuple[str, ...]
    optional: Tuple[str, ...]
    order: int


_TOKEN_RE = re.compile(r"[a-z0-9']+")


def _tokens(text: str) -> List[str]:
    return _TOKEN_RE.findall((text or "").lower())


class AdaptEngine:
    """Vocabulary/entity intent determination, Adapt-style.

    Entities are named keyword sets (vocabulary phrases, matched as
    token n-grams, longest first) and/or regexes over the utterance.
    An intent is a candidate only when ALL its required entities are
    present. Confidence is deterministic:

        0.55 * required_ratio + 0.25 * optional_ratio
        + 0.20 * tagged_token_coverage

    (optional_ratio is 1.0 when the intent declares no optionals).
    Ranking: confidence desc, then more required entities, then
    registration order — fully deterministic for identical input.
    """

    def __init__(self) -> None:
        self._vocab: Dict[str, List[Tuple[str, ...]]] = {}
        self._regex: Dict[str, List[re.Pattern]] = {}
        self._intents: List[_IntentSpec] = []

    # -- registration ---------------------------------------------------
    def register_vocab(self, entity: str, phrases: Iterable[str]) -> None:
        bucket = self._vocab.setdefault(entity, [])
        for phrase in phrases:
            toks = tuple(_tokens(phrase))
            if toks and toks not in bucket:
                bucket.append(toks)
        bucket.sort(key=len, reverse=True)

    def register_regex(self, entity: str, pattern: str) -> None:
        self._regex.setdefault(entity, []).append(re.compile(pattern))

    def register_intent(self, intent_type: str, action: str,
                         required: Iterable[str],
                         optional: Iterable[str] = ()) -> None:
        self._intents.append(_IntentSpec(
            intent_type=intent_type, action=action,
            required=tuple(required), optional=tuple(optional),
            order=len(self._intents)))

    # -- entity tagging ---------------------------------------------------
    def tag(self, utterance: str) -> Tuple[Dict[str, List[str]], int, int]:
        """Return (entities, tagged_token_count, total_token_count)."""
        text = (utterance or "").lower()
        toks = _tokens(text)
        entities: Dict[str, List[str]] = {}
        covered = [False] * len(toks)
        # Vocabulary: longest phrases first, non-overlapping.
        phrases: List[Tuple[Tuple[str, ...], str]] = []
        for entity, plist in self._vocab.items():
            for p in plist:
                phrases.append((p, entity))
        phrases.sort(key=lambda pe: -len(pe[0]))
        for phrase, entity in phrases:
            n = len(phrase)
            for i in range(0, len(toks) - n + 1):
                if tuple(toks[i:i + n]) == phrase and not any(covered[i:i + n]):
                    for j in range(i, i + n):
                        covered[j] = True
                    entities.setdefault(entity, []).append(" ".join(phrase))
        # Regex entities over the raw utterance.
        for entity, patterns in self._regex.items():
            for pat in patterns:
                for m in pat.finditer(text):
                    value = m.group(1) if m.groups() else m.group(0)
                    entities.setdefault(entity, []).append(value)
                    for tok in _tokens(m.group(0)):
                        for i, t in enumerate(toks):
                            if t == tok and not covered[i]:
                                covered[i] = True
                                break
        return entities, sum(1 for c in covered if c), len(toks)

    # -- determination ----------------------------------------------------
    def rank(self, utterance: str) -> List[Determination]:
        entities, tagged, total = self.tag(utterance)
        if total == 0:
            return []
        coverage = tagged / total
        out: List[Tuple[float, int, int, Determination]] = []
        for spec in self._intents:
            matched_req = [e for e in spec.required if entities.get(e)]
            if len(matched_req) != len(spec.required):
                continue  # required gate: all required entities present
            req_ratio = 1.0
            if spec.optional:
                matched_opt = [e for e in spec.optional if entities.get(e)]
                opt_ratio = len(matched_opt) / len(spec.optional)
            else:
                opt_ratio = 1.0
            confidence = round(
                0.55 * req_ratio + 0.25 * opt_ratio + 0.20 * coverage, 6)
            det = Determination(
                intent_type=spec.intent_type, action=spec.action,
                entities={k: list(v) for k, v in entities.items()},
                confidence=confidence, utterance=utterance or "")
            out.append((-confidence, -len(spec.required), spec.order, det))
        out.sort(key=lambda t: (t[0], t[1], t[2]))
        return [t[3] for t in out]

    def determine(self, utterance: str) -> Optional[Determination]:
        ranked = self.rank(utterance)
        return ranked[0] if ranked else None


# ---------------------------------------------------------------------------
# DellMatrix vocabulary — the pattern router's families, declared as the
# deterministic subset. ONLY families the canonical cascade verifiably
# constructs are registered (probed at build head, PR #505): e.g.
# PlaceVerb is {place, plant} — "put"/"set" are NOT claimed, because the
# cascade honestly returns unknown for them. Destructive verbs are
# deliberately absent: this layer never determines a destructive intent.
# ---------------------------------------------------------------------------
def build_default_engine() -> AdaptEngine:
    e = AdaptEngine()
    e.register_vocab("GrowVerb", ["grow", "evolve"])
    e.register_vocab("PlaceVerb", ["place", "plant"])
    e.register_vocab("ShowVerb", ["show", "display"])
    e.register_vocab("SaveVerb", ["save"])
    e.register_vocab("LoadVerb", ["load", "restore"])
    e.register_vocab("WalkVerb", ["walk", "step"])
    e.register_vocab("TurnVerb", ["turn", "rotate"])
    e.register_vocab("CycleVerb", ["cycle"])
    e.register_vocab("ConfirmVerb", ["confirm"])
    e.register_vocab("RejectVerb", ["reject"])
    e.register_vocab("StatusVerb", ["status"])
    e.register_vocab("HelpVerb", ["help"])
    e.register_vocab("StampVerb", ["stamp", "mark"])
    e.register_vocab("MeasureVerb", ["measure"])
    e.register_vocab("SimulateVerb", ["simulate", "dry run"])
    e.register_vocab("CheckpointVerb", ["checkpoint"])
    e.register_vocab("Direction", [
        "left", "right", "forward", "forwards", "back", "backwards",
        "up", "down",
    ])
    e.register_vocab("Count", [
        "one", "two", "three", "four", "five", "six", "seven", "eight",
        "nine", "ten",
    ])
    e.register_regex("Count", r"\b(\d+)\b")

    e.register_intent("GrowIntent", "grow", ["GrowVerb"], ["Count"])
    e.register_intent("PlaceIntent", "place", ["PlaceVerb"], ["Count"])
    e.register_intent("ShowIntent", "show", ["ShowVerb"])
    e.register_intent("SaveIntent", "save", ["SaveVerb"])
    e.register_intent("LoadIntent", "load", ["LoadVerb"])
    e.register_intent("WalkIntent", "walk", ["WalkVerb"],
                      ["Direction", "Count"])
    e.register_intent("TurnIntent", "turn", ["TurnVerb", "Direction"])
    e.register_intent("CycleIntent", "cycle", ["CycleVerb"], ["Count"])
    e.register_intent("ConfirmIntent", "nurture", ["ConfirmVerb"])
    e.register_intent("RejectIntent", "nurture", ["RejectVerb"])
    e.register_intent("StatusIntent", "status", ["StatusVerb"])
    e.register_intent("HelpIntent", "help", ["HelpVerb"])
    e.register_intent("StampIntent", "stamp", ["StampVerb"])
    e.register_intent("MeasureIntent", "measure", ["MeasureVerb"])
    e.register_intent("SimulateIntent", "simulate", ["SimulateVerb"])
    e.register_intent("CheckpointIntent", "checkpoint", ["CheckpointVerb"])
    return e


def smoke() -> bool:
    engine = build_default_engine()
    d = engine.determine("grow 3")
    ok = (d is not None and d.intent_type == "GrowIntent"
          and engine.determine("flibberty gibbet") is None
          and engine.determine("turn") is None)
    print(f"adapt_intent smoke: {'PASS' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
