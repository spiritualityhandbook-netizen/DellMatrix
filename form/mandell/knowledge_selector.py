#!/usr/bin/env python3
"""DCC-IX/XII: Deterministic contextual knowledge selector (Relevance V2).

Selects relevant confirmed knowledge for an operation based on context,
using the same token semantics as RingedGrowth affinity plus deterministic
phrase/order/coverage evidence.

Contract:
  Input: program, context (str), operation (str)
  Output: {
    "context": str,
    "normalized_context": str,
    "selector_version": 2,
    "eligible_count": int,
    "selected": [{
        "id": str, "label": str,
        "score": float,            # Jaccard (historical meaning, unchanged)
        "shared": [str],
        "coverage": float,         # |shared| / |context tokens|
        "exact_phrase": 0|1,       # normalized context substring of unit text
        "ordered": 0|1,            # context tokens as ordered subsequence
        "rank": int,               # 1-based
    }],
    "reason": str
  }

Eligibility: confirmed status AND promoted to cube.
Ranking: exact_phrase DESC, ordered DESC, coverage DESC, jaccard DESC,
         proposal ID ASC (total deterministic order).
No match: empty selected list (consumer runs scoped-empty, never fallback).
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Set

_TOKEN = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> Set[str]:
    """Tokenize text the same way RingedGrowth does."""
    return {m.group(0).lower() for m in _TOKEN.finditer(text.lower())}


def _token_seq(text: str) -> List[str]:
    """Ordered token sequence (same normalization as _tokens)."""
    return [m.group(0).lower() for m in _TOKEN.finditer(text.lower())]


def _norm_text(text: str) -> str:
    """Normalized text for phrase matching: tokens joined by single spaces."""
    return " ".join(_token_seq(text or ""))


def _ordered_subseq(ctx_seq: List[str], unit_seq: List[str]) -> bool:
    """True if every context token appears in unit_seq in order (gaps allowed)."""
    if not ctx_seq:
        return False
    it = iter(unit_seq)
    return all(any(tok == want for tok in it) for want in ctx_seq)


def _jaccard(a: Set[str], b: Set[str]) -> float:
    """Jaccard similarity between token sets."""
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def _unit_tokens(program: Any, uid: str) -> Set[str]:
    """Get tokens for a cube unit (label + detail)."""
    return _tokens(unit_text(program, uid))


def unit_text(program: Any, uid: str) -> str:
    """Combined text of a cube unit (label + detail + words)."""
    unit = program.cube.session.plane.units.get(uid)
    if not unit:
        return ""
    label = getattr(unit, "label", "") or ""
    detail = getattr(unit, "detail", "") or ""
    words = getattr(unit, "words", "") or ""
    return f"{label} {detail} {words}"


class ScopedPlaneView:
    """Read-only view restricting a plane to a subset of unit IDs.

    DCC-XI: lets RingedGrowth consume exactly the selector-approved
    subset without modifying the consumer or mutating the plane.

    Safety:
    - .units exposes ONLY the scoped subset (snapshot dict at construction).
    - All other attribute access delegates to the real plane
      (enhance_scope, spatial methods). Delegated methods only affect
      affinity weighting between scoped pairs; they cannot introduce
      new units into the pair enumeration (the sole enumeration point
      is list(plane.units.keys()) inside RingedGrowth.run).
    - The view is constructed per-call and never persisted; no way to
      widen or leak scope across calls.
    """

    def __init__(self, plane: Any, unit_ids: List[str]):
        self._plane = plane
        # Snapshot: only IDs present on the real plane, in given order.
        self._scoped = {uid: plane.units[uid] for uid in unit_ids if uid in plane.units}
        self._scope_ids = list(self._scoped.keys())

    @property
    def units(self) -> Dict[str, Any]:
        return self._scoped

    @property
    def scope_ids(self) -> List[str]:
        """The exact unit IDs this view exposes."""
        return list(self._scope_ids)

    def __getattr__(self, name: str) -> Any:
        # Delegate enhance_scope and any other plane API to the real plane.
        # Only called when normal lookup fails, so _plane/_scoped are safe.
        return getattr(self.__dict__["_plane"], name)


def select_for_context(
    program: Any,
    context: str,
    operation: str = "grow",
    min_score: float = 0.0,
    max_selected: int = 5,
) -> Dict[str, Any]:
    """Select confirmed knowledge relevant to context (Relevance V2).
    
    Deterministic: same state + context → same selection and ordering.
    
    Relevance V2 scoring contract (all components exposed per selection):
      jaccard      = |ctx ∩ unit| / |ctx ∪ unit|   (kept as "score", unchanged meaning)
      coverage     = |ctx ∩ unit| / |ctx|          (fraction of context covered)
      exact_phrase = 1 if normalized context is a substring of normalized
                     unit text, else 0
      ordered      = 1 if context tokens appear as an ordered subsequence
                     of the unit token sequence, else 0
    
    Ranking tuple (total, deterministic):
      (-exact_phrase, -ordered, -coverage, -jaccard, id) ascending
    i.e. exact_phrase DESC, ordered DESC, coverage DESC, jaccard DESC,
    proposal ID ASC (stable final tie-break).
    
    Eligibility: confirmed AND on-plane AND revision-active (DCC-XVI) AND
    dependency-valid (DCC-XV). Revision filtering runs before dependency
    filtering and before Relevance V2 scoring; scoring never weakens
    eligibility; no-match still yields an empty selection.
    """
    context = (context or "").strip()
    ctx_tokens = _tokens(context)
    ctx_seq = _token_seq(context)
    ctx_norm = _norm_text(context)
    
    # Eligible: confirmed AND in cube
    eligible = []
    for pid, prop in program.nursery.proposals.items():
        if prop.status != "confirmed":
            continue
        if pid not in program.cube.session.plane.units:
            continue
        eligible.append((pid, prop))

    # DCC-XVI: revision/supersession gates eligibility BEFORE lineage,
    # dependency, and Relevance V2. Only active revisions may route;
    # superseded and malformed-revision units are excluded with evidence.
    # Revision ancestry is not derivation ancestry: this filter never
    # touches lineage parents.
    from form.mandell.supersession import (
        SUPERSESSION_VERSION, inspect_revision, is_revision_active,
        revision_exclusions,
    )
    rev_excluded_ids = [
        pid for pid, _ in eligible if not is_revision_active(program, pid)
    ]
    rev_exclusions = revision_exclusions(program, rev_excluded_ids)
    eligible = [(pid, prop) for pid, prop in eligible
                if is_revision_active(program, pid)]
    active_revision_count = len(eligible)

    # DCC-XV: dependency validity gates eligibility. A derived unit is
    # dependency-valid only when every required transitive ancestor exists
    # on the plane, is confirmed, is revision-active, and has valid
    # lineage. Historical lineage is untouched; this filters
    # current-state qualification before Relevance V2 ever sees the
    # candidate.
    from form.mandell.dependency_validity import (
        DEPENDENCY_VERSION, dependency_exclusions, is_dependency_valid,
    )
    dep_excluded_ids = [
        pid for pid, _ in eligible if not is_dependency_valid(program, pid)
    ]
    dep_exclusions = dependency_exclusions(program, dep_excluded_ids)
    eligible = [(pid, prop) for pid, prop in eligible
                if is_dependency_valid(program, pid)]

    eligible_count = len(eligible)
    dependency_valid_count = eligible_count
    
    if not ctx_tokens or not eligible:
        return {
            "context": context,
            "normalized_context": ctx_norm,
            "operation": operation,
            "selector_version": 2,
            "supersession_version": SUPERSESSION_VERSION,
            "dependency_version": DEPENDENCY_VERSION,
            "eligible_count": eligible_count,
            "active_revision_count": active_revision_count,
            "dependency_valid_count": dependency_valid_count,
            "supersession_exclusions": rev_exclusions,
            "dependency_exclusions": dep_exclusions,
            "selected": [],
            "reason": "no context tokens" if not ctx_tokens else "no eligible knowledge",
        }
    
    # Score each eligible unit (Relevance V2)
    scored = []
    for pid, prop in eligible:
        unit_tokens = _unit_tokens(program, pid)
        jaccard = _jaccard(ctx_tokens, unit_tokens)
        if jaccard <= min_score:
            continue
        shared = sorted(ctx_tokens & unit_tokens)
        unit = program.cube.session.plane.units.get(pid)
        unit_text = ""
        if unit:
            unit_text = f"{getattr(unit, 'label', '') or ''} " \
                        f"{getattr(unit, 'detail', '') or ''} " \
                        f"{getattr(unit, 'words', '') or ''}"
        unit_norm = _norm_text(unit_text)
        unit_seq = _token_seq(unit_text)
        exact_phrase = 1 if (ctx_norm and ctx_norm in unit_norm) else 0
        ordered = 1 if _ordered_subseq(ctx_seq, unit_seq) else 0
        coverage = round(len(shared) / len(ctx_tokens), 4) if ctx_tokens else 0.0
        # DCC-XVI: revision identity on each selection (eligibility
        # already guarantees active; identity is audit evidence).
        rev = inspect_revision(program, pid)
        scored.append({
            "id": pid,
            "label": prop.label,
            "score": round(jaccard, 4),   # historical meaning: Jaccard
            "shared": shared,
            "coverage": coverage,
            "exact_phrase": exact_phrase,
            "ordered": ordered,
            "lifecycle_state": rev["lifecycle_state"],
            "revision_number": rev["revision_number"],
            "revision_root_id": rev["revision_root_id"],
            "rank_key": (-exact_phrase, -ordered, -coverage, -round(jaccard, 4), pid),
        })
    
    # Deterministic V2 ordering: exact_phrase DESC, ordered DESC,
    # coverage DESC, jaccard DESC, ID ASC
    scored.sort(key=lambda x: x["rank_key"])

    # ASI-I (NBD-Ω-008): bounded learned preference (advisory).
    # Stable re-sort of the already-selected top-N by the bounded DuoBeta
    # learned score (Dell 37 = this contextual selector's Dell).
    # Position: AFTER revision/dependency/relevance hard laws and AFTER
    # the max_selected limit; BEFORE conflict/disposition, which filter
    # the reordered list downstream in core_i_ops (hard-law dominance by
    # construction). Relevance V2 order is preserved for equal learned
    # scores (stable sort). Never adds, removes, or resurrects a candidate.
    # Cold start (no learning): all scores 0 → order exactly baseline.
    from form.mandell.duobeta_learn import bounded_learned_score
    top = scored[:max_selected]
    baseline_selected_ids = [s["id"] for s in top]
    learned_scores = {
        s["id"]: bounded_learned_score(program, 37, s["id"]) for s in top
    }
    top.sort(key=lambda s: -learned_scores[s["id"]])  # stable
    learned_selected_ids = [s["id"] for s in top]
    learned_preference_applied = any(v != 0 for v in learned_scores.values())

    # Limit to max_selected; assign 1-based rank
    selected = []
    for i, s in enumerate(top, start=1):
        entry = {k: v for k, v in s.items() if k != "rank_key"}
        entry["rank"] = i
        selected.append(entry)
    
    if selected:
        reason = (f"relevance v2: {len(selected)} of {eligible_count} eligible "
                  f"(exact_phrase, ordered, coverage, jaccard; ID tie-break)")
    else:
        reason = f"no token overlap with {eligible_count} eligible"
    
    return {
        "context": context,
        "normalized_context": ctx_norm,
        "operation": operation,
        "selector_version": 2,
        "supersession_version": SUPERSESSION_VERSION,
        "dependency_version": DEPENDENCY_VERSION,
        "eligible_count": eligible_count,
        "active_revision_count": active_revision_count,
        "dependency_valid_count": dependency_valid_count,
        "supersession_exclusions": rev_exclusions,
        "dependency_exclusions": dep_exclusions,
        "selected": selected,
        "reason": reason,
        # ASI-I observability (read-only evidence; flows into the
        # grow_contextual receipt / last_nurture for ROS-I inspection).
        "baseline_selected_ids": baseline_selected_ids,
        "learned_selected_ids": learned_selected_ids,
        "learned_scores": learned_scores,
        "learned_preference_applied": learned_preference_applied,
    }
