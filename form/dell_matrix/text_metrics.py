"""Canonical tokenization + Jaccard substrate (P3 / TD-6).

One token contract for the growth/selection family:

    tokens are lowercase runs of [a-z0-9_] of length >= 3.

This is RingedGrowth's contract (the GDP-001 Phase 3 mathematical
admission substrate). Before P3 the regex and the Jaccard formula
were copy-pasted into six modules in two divergent variants, and
knowledge_selector claimed to tokenize "the same way RingedGrowth
does" while using a different regex ([a-z0-9]+ — 1-2 char tokens
counted, no underscores), so growth token sets and KIE selection
token sets were quietly different sets for short-token text.

Now: this module is the single implementation. ringed_growth,
verita, and knowledge_selector delegate here, and harmony's
pairwise coherence uses this module's jaccard. (idea_grow and
floor_spirit also delegated here until their SD-5 retirement.)

Deliberate exceptions, documented at their sites:
- harmony._idea_tokens keeps the [a-z0-9]+ tokenizer: its domain is
  idea-object properties, where short values are content; its
  *formula* (mean pairwise Jaccard x redundancy term) is a distinct
  measure (see the duplicates sweep, FA-4). Only its Jaccard is
  shared.
- resonance._tokens is a hand-rolled list tokenizer for the
  state-diffusion family (bracket stripping, "pulled:" filtering) —
  a different mechanism, not this substrate.
"""

from __future__ import annotations

import re
from typing import List, Set

TOKEN_RE = re.compile(r"[a-z0-9_]{3,}", re.I)


def tokens(text: str) -> Set[str]:
    """The canonical token set of a text."""
    return {m.group(0).lower() for m in TOKEN_RE.finditer((text or "").lower())}


def token_seq(text: str) -> List[str]:
    """Ordered canonical tokens (same normalization as tokens())."""
    return [m.group(0).lower() for m in TOKEN_RE.finditer((text or "").lower())]


def tokens_of(label: str, words: str) -> Set[str]:
    """Canonical token set of a unit's label + words."""
    return tokens(f"{label} {words}")


def jaccard(a: Set[str], b: Set[str]) -> float:
    """Jaccard similarity between token sets. Empty on either side
    is 0.0 (no shared vocabulary is no similarity, never NaN)."""
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0
