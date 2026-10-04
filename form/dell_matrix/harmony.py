"""Harmony: the degree to which a set of ideas forms a coherent, non-redundant whole.

GDP-001 Phase 3, R3.2 (3.2.1 / 3.2.3). DellMatrix semantic, not a musical metaphor.

Operational definition (acceptance matrix 3.2.1): harmony measures set-level
coherence penalized by redundancy. It is deliberately distinct from:

- resonance ``pulse`` (form.dell_matrix.resonance.pulse): state diffusion over
  plane units over time — a dynamic process, not a set metric;
- ``harmonize_pair`` (form.dell_matrix.resonance.harmonize_pair): a
  state-mutating resonance write for one pair of plane units;
- ``_affinity`` (form.dell_matrix.ringed_growth._affinity): a PAIR score
  blending token overlap with spatial distance, enhance-scope and goal boosts;
- Verita pair coherence (verita_between_nodes): a different pair authority.

The separation is proven, not asserted, in
form/mandell/p3_r32_harmony_proof.py (3.2.4).

Canonical owner: this module, ``form/dell_matrix/harmony.py::harmony_score``.
Real caller: initially the R3.2 proof; integration in R3.5.
"""

from __future__ import annotations

import re
from typing import Any, Iterable, List, Set

from form.dell_matrix.faded_policy import exclude_faded

_TOKEN = re.compile(r"[a-z0-9]+")

# Weight applied to near-duplicate pairs when computing the redundancy term.
# harmony = C * (1 - R) with R = mean pairwise jaccard ** _DUP_EXPONENT.
# The cubic exponent concentrates the penalty on near-identical pairs while
# leaving moderate overlap nearly unpenalized. Module-level so the R3.2
# mutation test can perturb it and the proof must detect the change.
_DUP_EXPONENT = 3.0


def _idea_tokens(idea: Any) -> Set[str]:
    """Honest token source: what an idea object actually exposes.

    Reads only real, verified attributes:
      - ``idea.title`` (str)
      - ``idea.get_active_properties()`` (dict of property name -> value),
        keys and string values tokenized; non-string scalars contribute their
        repr so numeric/bool properties still participate.
    Anything else (None, non-idea objects, ideas with no readable content)
    yields the empty set. Never raises.
    """
    if idea is None or isinstance(idea, (str, bytes)):
        return set()
    parts: List[str] = []
    title = getattr(idea, "title", None)
    if isinstance(title, str):
        parts.append(title)
    get_props = getattr(idea, "get_active_properties", None)
    if callable(get_props):
        try:
            props = get_props()
        except Exception:
            props = None
        if isinstance(props, dict):
            for k, v in props.items():
                if isinstance(k, str):
                    parts.append(k)
                if isinstance(v, str):
                    parts.append(v)
                elif isinstance(v, (int, float, bool)):
                    parts.append(repr(v))
    blob = " ".join(parts).lower()
    return {m.group(0) for m in _TOKEN.finditer(blob)}


def _pair_coherence(ta: Set[str], tb: Set[str]) -> float:
    """Pairwise coherence: Jaccard similarity of token sets."""
    if not ta and not tb:
        return 0.0
    union = ta | tb
    if not union:
        return 0.0
    return len(ta & tb) / len(union)


def _redundancy_weight(jac: float) -> float:
    """Near-duplicate concentration weight for one pair, in [0, 1]."""
    j = min(max(jac, 0.0), 1.0)
    return j ** _DUP_EXPONENT


def harmony_score(idea_set: Iterable[Any]) -> float:
    """Harmony: the degree to which a set of ideas forms a coherent, non-redundant whole.

    (1) NAME
        harmony_score

    (2) INPUTS (types/domains)
        idea_set: any iterable of idea-like objects (form.mandell.idea.Idea or
        duck-typed equivalents). "Well-typed" = an iterable (not str/bytes)
        whose elements are objects or None. Tokens are read honestly via
        _idea_tokens (title + active property names/values); elements that
        expose nothing contribute the empty token set.

    (3) OUTPUTS (types/ranges)
        float in [0, 1].
        - empty set -> 0.0
        - single idea -> 1.0 if it has any tokens, else 0.0 (solo coherence)
        - n >= 2 -> C * (1 - R) as defined in (4)

    (4) FORMULA / DEFINITION (documented variables)
        Let S = {i_1, ..., i_n} be the idea set, T_k = tokens(i_k) from
        _idea_tokens, and for each pair (a, b), a < b:

            jac(a,b) = |T_a ∩ T_b| / |T_a ∪ T_b|        (0 if T_a = T_b = ∅)
                     pairwise Jaccard coherence, in [0, 1]

            C = (2 / (n (n-1))) * Σ_{a<b} jac(a,b)     mean pairwise coherence
            R = (2 / (n (n-1))) * Σ_{a<b} jac(a,b)^3   near-duplicate
                                                      concentration, in [0, 1]

            harmony(S) = C * (1 - R)

        Reading: harmony is high when ideas are pairwise coherent (high C)
        but not identical (low R). Identical ideas give jac = 1 for every
        pair, so C = R = 1 and harmony = 0. Disjoint ideas give C = 0 and
        harmony = 0. The cubic exponent concentrates the redundancy penalty
        on near-duplicate pairs: moderate overlap (jac ≈ 0.5) contributes
        0.125 to R, near-identity (jac ≈ 0.95) contributes ≈ 0.857.

    (5) INVARIANTS
        - 0.0 <= harmony_score(S) <= 1.0 for all inputs.
        - Symmetric: permuting the input order never changes the result
          (all terms are symmetric pair sums).
        - harmony({x}) = 1.0 iff x has non-empty tokens.
        - harmony(S) = 0.0 if every pair is disjoint (C = 0).
        - harmony(S) = 0.0 if every pair is identical (C = R = 1).

    (6) FAILURE / DEGENERATE BEHAVIOR
        - empty set -> 0.0 (defined, no exception)
        - single idea -> solo coherence (1.0 with content, 0.0 without)
        - None / non-iterable / str / bytes input -> 0.0 (fail-closed)
        - elements that are None or expose no content -> empty token set,
          pair coherence 0.0 against any partner
        - both token sets empty -> pair coherence 0.0 (no content, no
          coherence claimed)
        - FADED ideas (R3.5.2) are excluded before scoring; all-faded
          input -> 0.0 (defined, no exception)
        Never raises for well-typed input. Ill-typed input is fail-closed
        to 0.0, never an exception.

    (7) DETERMINISM CLAIM
        Pure function of the input content. No randomness, no wall-clock,
        no ambient state, no iteration-order dependence: token sets are
        Python sets combined only through symmetric sums, and the result
        is a closed-form float. Identical inputs -> identical outputs,
        in this process and across processes.

    (8) CANONICAL OWNER + REAL CALLER
        Canonical owner: form/dell_matrix/harmony.py::harmony_score (this
        module). Real caller: initially the R3.2 proof
        (form/mandell/p3_r32_harmony_proof.py); integration callers in
        R3.5. Public path: Program.harmony_of (form/open.py), a thin
        documented wrapper.
    """
    if idea_set is None or isinstance(idea_set, (str, bytes)):
        return 0.0
    try:
        items = list(idea_set)
    except TypeError:
        return 0.0
    # P3 R3.5.2: faded-state exclusion — ideas whose lifecycle state is FADED
    # do not participate in harmony computation. All-faded -> empty -> 0.0.
    items = exclude_faded(items)
    n = len(items)
    if n == 0:
        return 0.0
    token_sets = [_idea_tokens(it) for it in items]
    if n == 1:
        return 1.0 if token_sets[0] else 0.0
    pairs = n * (n - 1) // 2
    c_total = 0.0
    r_total = 0.0
    for a in range(n):
        ta = token_sets[a]
        for b in range(a + 1, n):
            jac = _pair_coherence(ta, token_sets[b])
            c_total += jac
            r_total += _redundancy_weight(jac)
    coherence = c_total / pairs
    redundancy = r_total / pairs
    score = coherence * (1.0 - redundancy)
    # Clamp defensively against float drift; contract range is [0, 1].
    return min(max(score, 0.0), 1.0)
