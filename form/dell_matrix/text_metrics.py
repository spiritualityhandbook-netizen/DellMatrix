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


# ------------------------------------------------------------------
# Stopwords (post-plan PP1 / Ace D6, 2026-10-28)
#
# Ace's rule: words may FIND candidate pairs, but connector words
# — "and", "the", "if" — and other function words that hold no
# meaning beyond connecting content words must not count IN the
# pair comparisons. This set is the single authority for that
# exclusion. It applies ONLY at pair-comparison call sites
# (growth affinity, goal boost, knowledge-selection scoring),
# via content_tokens()/content_tokens_of(). Raw tokenization
# (tokens(), token_seq()) is unchanged: signal consumers —
# negation/conflict detection, phrase and order matching — read
# raw text or raw sequences and never this filter (the TD-6
# blast-radius lesson: a similarity parameter must never starve
# a signal detector).
#
# Curation rules:
# - English function words only: articles, conjunctions,
#   prepositions, pronouns, auxiliary/modal verbs, and common
#   adverbs of manner/time that carry no topic content.
# - Negation and contrast words are NEVER stopwords here —
#   "no", "not", "nor", "never", "but", "yet" change meaning;
#   excluding them from any comparison would hide opposition.
# - Only words of length >= 3 are listed; shorter words never
#   tokenize under TOKEN_RE anyway ("if", "of", "to", "in").
STOPWORDS = frozenset({
    "the", "and", "for", "with", "from", "into", "upon", "about",
    "above", "after", "again", "against", "all", "any", "are",
    "been", "before", "below", "between", "both", "can", "could",
    "did", "does", "doing", "down", "during", "each", "few",
    "further", "had", "has", "have", "having", "her", "here",
    "hers", "herself", "him", "himself", "his", "how", "its",
    "itself", "just", "may", "might", "more", "most", "must",
    "off", "once", "only", "other", "our", "ours", "out", "over",
    "own", "same", "she", "should", "some", "such", "than",
    "that", "their", "theirs", "them", "themselves", "then",
    "there", "these", "this", "those", "through", "too", "under",
    "until", "very", "was", "were", "what", "when", "where",
    "which", "while", "who", "whom", "why", "will", "would",
    "you", "your", "yours", "yourself", "also", "because",
    "become", "becomes", "became", "per", "via", "one", "two",
    "get", "got", "make", "made", "like", "way", "thing",
    "things", "much", "many", "well", "back", "even", "still",
})


def content_tokens(text: str) -> Set[str]:
    """Canonical token set with stopwords removed — the set a
    PAIR COMPARISON should see. A text of only stopwords yields
    the empty set (no content = no basis for comparison)."""
    return tokens(text) - STOPWORDS


def content_tokens_of(label: str, words: str) -> Set[str]:
    """content_tokens() over a unit's label + words."""
    return content_tokens(f"{label} {words}")
