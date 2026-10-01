#!/usr/bin/env python3
"""DCC-XIII: Bounded deterministic conflict detection + routing (Conflict V1).

Conflict V1 detects ONE bounded pattern: textual polarity conflict.

A conflict is declared for a pair of selected knowledge units iff ALL hold:
  1. Polarity: exactly one unit contains a supported explicit negation
     signal (NEGATION_WORDS or an n't-contraction).
  2. Shared frame: the de-negated token sets share a content frame:
     |shared| >= FRAME_SHARED_MIN (2) AND
     Jaccard(de-negated A, de-negated B) >= FRAME_JACCARD_MIN (0.5).
  3. Both units were already eligible and selected (conflict analysis never
     widens the candidate set; status filtering happens before routing).

Every decision is reconstructible from the conflict entry:
  pair IDs, polarity evidence, shared frame, frame Jaccard, reason.

Conflict V1 is NOT:
  - general contradiction detection
  - semantic entailment / paraphrase understanding
  - truth verification or fact checking
  - learned reasoning or autonomous judgment

Known boundaries (documented, not hidden):
  - Morphological variants ("requires" vs "require") are different tokens;
    they reduce frame similarity but do not break the canonical pattern.
  - Double negation ("does not lack") is read as negation; V1 does not
    resolve it.
  - Paraphrases with disjoint vocabularies are invisible to V1.
  - "no" is a supported signal ("needs no light"); rare non-negation uses
    of these words are accepted false-positive risk, bounded by the frame
    rule.

Routing (route_conflicts): every unit participating in >=1 conflict pair
is quarantined; the routable set preserves the selector's rank order minus
quarantined IDs. No member is chosen as "true" — ID, time, and score are
never used as truth proxies.
"""
from __future__ import annotations

from typing import Dict, List, Set, Tuple

from form.mandell.knowledge_selector import _token_seq

CONFLICT_VERSION = 1

# Explicit, bounded negation signals. Words are matched as whole tokens
# (same normalization as the selector); n't-contractions are detected on
# the raw lowercased text because the tokenizer splits "doesn't" into
# "doesn"+"t".
NEGATION_WORDS = frozenset({"not", "no", "never", "none", "neither", "nor", "cannot"})

# Both must hold for a shared content frame.
FRAME_JACCARD_MIN = 0.5
FRAME_SHARED_MIN = 2


def _negation_evidence(text: str) -> List[str]:
    """Supported negation signals present in text (sorted, deterministic)."""
    low = (text or "").lower()
    toks = set(_token_seq(low))
    found = sorted(toks & NEGATION_WORDS)
    if "n't" in low:
        found.append("n't")
    return sorted(set(found))


def _has_negation(text: str) -> bool:
    return bool(_negation_evidence(text))


def _frame_tokens(text: str) -> Set[str]:
    """De-negated token set: the comparable content frame."""
    low = (text or "").lower()
    frame = set(_token_seq(low)) - NEGATION_WORDS
    if "n't" in low:
        # Tokenizer splits "doesn't" -> "doesn"+"t"; drop the residue so it
        # cannot pollute frame similarity.
        frame.discard("t")
    return frame


def detect_conflicts(items: List[Dict[str, str]]) -> List[Dict]:
    """Detect polarity conflicts among selected units.

    items: [{"id": str, "text": str}, ...] — already eligible+selected.
    Returns conflict entries ordered by (id_a, id_b); each entry carries
    enough evidence to reconstruct the decision.
    """
    ordered = sorted(items, key=lambda d: d["id"])
    ids = [d["id"] for d in ordered]
    neg = {d["id"]: _negation_evidence(d["text"]) for d in ordered}
    frames = {d["id"]: _frame_tokens(d["text"]) for d in ordered}

    conflicts = []
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            a, b = ids[i], ids[j]
            # Polarity: exactly one side negated.
            if bool(neg[a]) == bool(neg[b]):
                continue
            fa, fb = frames[a], frames[b]
            shared = sorted(fa & fb)
            if len(shared) < FRAME_SHARED_MIN:
                continue
            union = fa | fb
            jacc = len(shared) / len(union) if union else 0.0
            if jacc < FRAME_JACCARD_MIN:
                continue
            neg_id, pos_id = (a, b) if neg[a] else (b, a)
            conflicts.append({
                "id_a": a,
                "id_b": b,
                "negative_id": neg_id,
                "positive_id": pos_id,
                "negation_evidence": neg[neg_id],
                "shared_frame": shared,
                "frame_jaccard": round(jacc, 4),
                "reason": (
                    f"polarity conflict: '{neg_id}' carries negation "
                    f"{neg[neg_id]} over the shared frame with '{pos_id}'"
                ),
            })
    return conflicts


def route_conflicts(
    selected_ids: List[str],
    conflicts: List[Dict],
) -> Tuple[List[str], List[str]]:
    """Split selected IDs into (routable, quarantined).

    Every unit in >=1 conflict pair is quarantined. Routable preserves the
    selector's rank order. Deterministic.
    """
    quarantined = set()
    for c in conflicts:
        quarantined.add(c["id_a"])
        quarantined.add(c["id_b"])
    quarantined_ids = sorted(quarantined)
    routable = [sid for sid in selected_ids if sid not in quarantined]
    return routable, quarantined_ids
