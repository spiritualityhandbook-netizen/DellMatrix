#!/usr/bin/env python3
"""NBDE-I: Next Best Directive Engine I (NBD-Ω-009).

The first canonical NBD-Ω decision-support engine.

READ-ONLY DECISION SUPPORT. Input: verified current system evidence.
Output: ranked proposed directives with explanations.

NBD-Ω may: DISCOVER, CLASSIFY, SCORE, COMPARE, RANK, EXPLAIN, PROPOSE.
NBD-Ω may NOT: EXECUTE, MUTATE, MERGE, APPLY LEARNING, CHANGE AUTHORITY,
DECLARE TRUTH, AUTONOMOUSLY ISSUE WORK.

Law:
  SYSTEM EVIDENCE > NBD ANALYSIS > PROPOSED DIRECTIVES
  > DIRECTOR DECISION > separate authorized implementation cycle

AUTONOMY=NO. DIRECTOR_DECISION_REQUIRED=YES. EXECUTION_AUTHORITY=NONE.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

ENGINE_VERSION = 1

# ── F: fact vs projection ────────────────────────────────────────────
FACT = "FACT"
DERIVED_FACT = "DERIVED_FACT"
PROJECTION = "PROJECTION"
UNKNOWN = "UNKNOWN"

# ── H: candidate states ──────────────────────────────────────────────
OPEN = "OPEN"
BLOCKED = "BLOCKED"
READY = "READY"
CLOSED = "CLOSED"

_EPS = 1e-9


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ── E: evidence ──────────────────────────────────────────────────────
@dataclass
class Evidence:
    """A single verified/read-only evidence item."""
    source: str            # which module/ledger/view produced it
    scope: str             # what it covers (and does not)
    detail: str            # the observation itself
    kind: str = FACT       # FACT | DERIVED_FACT | PROJECTION | UNKNOWN
    freshness: str = ""    # state fingerprint where available
    verification: str = ""  # how it was verified

    def as_dict(self) -> Dict[str, Any]:
        return {"source": self.source, "scope": self.scope,
                "detail": self.detail, "kind": self.kind,
                "freshness": self.freshness,
                "verification": self.verification}


# ── G: candidate model ───────────────────────────────────────────────
@dataclass
class Candidate:
    candidate_id: str
    title: str
    target_circuit: str
    evidence: List[Evidence] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    expected_closures: int = 0              # PROJECTION
    expected_reuse: float = 0.0             # PROJECTION 0..1
    expected_future_work_avoided: int = 0   # PROJECTION
    verification_plan: str = ""             # FACT-derivable
    risk: float = 0.5                       # PROJECTION 0..1
    scope_interference: float = 0.5         # 0..1
    movement_cost: float = 0.5              # 0..1
    projection_flags: List[str] = field(default_factory=list)
    blocked_reason: Optional[str] = None
    state: str = OPEN
    locality: str = "general"
    # RCCR-I: True if mapped circuit is OPEN (needs classification).
    # Such candidates cannot become READY until the circuit is classified.
    circuit_needs_classification: bool = False
    # J: resonance / urgency / historical recovery (PROJECTION unless noted)
    resonance: float = 0.5                   # PROJECTION 0..1
    urgency: float = 0.0                     # PROJECTION 0..1
    historical_recovery: float = 0.0         # DERIVED_FACT 0..1
    verification_confidence: float = 0.5     # DERIVED_FACT 0..1

    def as_dict(self) -> Dict[str, Any]:
        d = {k: v for k, v in self.__dict__.items() if k != "evidence"}
        d["evidence"] = [e.as_dict() for e in self.evidence]
        return d


# ── L: state fingerprint ─────────────────────────────────────────────
def state_fingerprint(program: Any, main_commit: str = "unknown") -> Dict[str, Any]:
    """Bind an NBD result to the system state it was computed from.

    main_commit is injected by the caller (NBD may not invoke git).
    """
    fp: Dict[str, Any] = {
        "nbd_engine_version": ENGINE_VERSION,
        "computed_at": _ts(),
        "main_commit": main_commit,
    }
    # outcome ledger
    try:
        from .outcome_ledger import list_outcomes
        fp["outcome_ledger_count"] = len(list_outcomes(program))
    except Exception:
        fp["outcome_ledger_count"] = "unknown"
    # duobeta ledger
    try:
        duo = getattr(program, "duo", None)
        fp["duobeta_ledger_count"] = len(getattr(duo, "ledger", []) or [])
    except Exception:
        fp["duobeta_ledger_count"] = "unknown"
    # generation
    try:
        from .checkpoint_generation import current_generation_id
        fp["generation_id"] = current_generation_id(
            getattr(program, "owner", "Operator"))
    except Exception:
        fp["generation_id"] = "unknown"
    return fp


def fingerprint_hash(fp: Dict[str, Any]) -> str:
    canon = "|".join(f"{k}={fp.get(k)}" for k in sorted(fp))
    return hashlib.sha256(canon.encode()).hexdigest()[:16]


# ── H: eligibility ───────────────────────────────────────────────────
def classify_candidates(candidates: List[Candidate]) -> List[Candidate]:
    """DISCOVER > VERIFY > CLASSIFY. Resolve BLOCKED from dependencies.

    A candidate with unmet dependencies (depends on a non-CLOSED
    candidate) becomes BLOCKED with a reason. CLOSED stays CLOSED.
    Otherwise OPEN becomes READY (verified by construction here —
    callers must only pass verified candidates).
    """
    by_id = {c.candidate_id: c for c in candidates}
    for c in candidates:
        if c.state == CLOSED:
            continue
        unmet = [d for d in c.dependencies
                 if d in by_id and by_id[d].state != CLOSED]
        # Unknown dependency IDs are treated as unmet (honest).
        unknown = [d for d in c.dependencies if d not in by_id]
        blockers = unmet + unknown
        if blockers:
            c.state = BLOCKED
            c.blocked_reason = f"unmet dependencies: {sorted(blockers)}"
        elif c.state in (OPEN, BLOCKED):
            # RCCR-I: If the mapped circuit is OPEN (needs classification),
            # the candidate cannot become READY. It stays OPEN.
            if c.circuit_needs_classification:
                c.state = OPEN
                c.blocked_reason = "circuit OPEN: needs classification"
            else:
                # Verified and unblocked → READY (BLOCKED can recover).
                c.state = READY
                c.blocked_reason = None
    return candidates


def ready_set(candidates: List[Candidate]) -> List[Candidate]:
    """Only READY candidates may compete for immediate ranking."""
    return [c for c in candidates if c.state == READY]


# ── K: anti-gaming ───────────────────────────────────────────────────
def anti_gaming_checks(c: Candidate) -> List[str]:
    """Explicit anti-gaming checks. Returns list of triggered adjustments."""
    triggered: List[str] = []
    # 1. closure inflation: closures must reference ledger IDs
    refs = 0
    for e in c.evidence:
        txt = (e.detail + " " + e.scope).upper()
        # crude: count LE-## / DCC-## / PR-# references
        import re
        refs += len(re.findall(r"\b(LE|DCC)-\d+", txt))
        refs += len(re.findall(r"\bPR\s*#\d+", txt))
    if c.expected_closures > refs:
        triggered.append(
            f"closure_inflation: claimed {c.expected_closures} closures "
            f"but only {refs} ledger references; discounting")
        c.expected_closures = refs
    # 2. reuse without evidence
    if c.expected_reuse > 0.5:
        has_fact = any(e.kind in (FACT, DERIVED_FACT)
                       and "reuse" in (e.detail + e.scope).lower()
                       for e in c.evidence)
        if not has_fact:
            triggered.append(
                "reuse_unbacked: expected_reuse > 0.5 without FACT "
                "evidence; capping at 0.5")
            c.expected_reuse = 0.5
    # 3. future-work inflation cap
    if c.expected_future_work_avoided > 3:
        backed = any(e.kind == DERIVED_FACT and "blocks" in e.detail.lower()
                     for e in c.evidence)
        if not backed:
            triggered.append(
                "future_work_inflation: capping at 3 without DERIVED_FACT")
            c.expected_future_work_avoided = 3
    # 5. movement understatement floor (locality distance)
    # (handled at batch time; floor here for cross-locality singles)
    # 7. metric-serving work: closures==0 and no evidence → disqualify
    if c.expected_closures == 0 and not c.evidence:
        triggered.append("metric_serving: no closures, no evidence; "
                         "closures stay 0 (ranks last)")
    return triggered


# ── J: scoring ───────────────────────────────────────────────────────
@dataclass
class Score:
    dw: float
    next_weight: float
    route_value: float
    components: Dict[str, Any]
    projection_flags: List[str]


def _clamp01(x: float) -> float:
    try:
        f = float(x)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, f))


def score_candidate(c: Candidate, locality_peers: int = 0) -> Score:
    """Score with full component exposure. No hidden magic numbers.

    DW = (C × D × R × I × V) / (K × S)
    NextWeight = DW × (1 + H + U − F)
    RouteValue = (Closures × Resonance × Reuse × FutureWorkAvoided ×
                  VerificationConfidence)
                 / (Movement × ReworkRisk × ScopeInterference)
    """
    # FACT-backed / DERIVED_FACT inputs
    D = 1.0 if c.state == READY else 0.0          # dependency readiness
    I = _clamp01(0.5 + 0.5 * min(1.0, len(c.verification_plan) / 200.0))
    V = _clamp01(c.verification_confidence)        # DERIVED_FACT
    H = _clamp01(c.historical_recovery)            # DERIVED_FACT
    # PROJECTION inputs (labeled)
    C = max(0, int(c.expected_closures))
    C_n = min(1.0, C / 5.0)                        # normalize: 5 closures = 1.0
    R = _clamp01(c.resonance)
    # locality resonance boost from peers (DERIVED_FACT count, capped)
    R = _clamp01(R + 0.1 * min(3, locality_peers))
    U = _clamp01(c.urgency)
    K = max(_clamp01(c.risk), _EPS)                # rework risk
    S = max(_clamp01(c.scope_interference), _EPS)
    reuse = _clamp01(c.expected_reuse)
    fwa = max(0, int(c.expected_future_work_avoided))
    fwa_n = min(1.0, fwa / 5.0)
    movement = max(_clamp01(c.movement_cost), _EPS)
    # F: future-work duplication (DERIVED_FACT; set by caller if duplicate)
    F_dup = _clamp01(getattr(c, "_duplication", 0.0))

    dw = (C_n * D * R * I * V) / (K * S)
    next_weight = dw * (1 + H + U - F_dup)
    route_value = ((C_n * R * reuse * fwa_n * V)
                   / (movement * K * S))

    flags = list(c.projection_flags)
    for name in ("expected_closures", "expected_reuse",
                 "expected_future_work_avoided", "risk", "resonance",
                 "urgency"):
        if name not in flags:
            flags.append(name)

    return Score(
        dw=round(dw, 4),
        next_weight=round(next_weight, 4),
        route_value=round(route_value, 4),
        components={
            "C_closures": C, "C_norm": round(C_n, 4),
            "D_readiness": D, "R_resonance": round(R, 4),
            "I_clarity": round(I, 4), "V_confidence": round(V, 4),
            "K_risk": round(K, 4), "S_interference": round(S, 4),
            "H_recovery": round(H, 4), "U_urgency": round(U, 4),
            "F_duplication": round(F_dup, 4),
            "reuse": round(reuse, 4), "future_work_avoided": fwa,
            "movement": round(movement, 4),
        },
        projection_flags=sorted(set(flags)),
    )


# ── ranking ──────────────────────────────────────────────────────────
@dataclass
class RankedProposal:
    candidate: Candidate
    score: Score
    rank: int
    anti_gaming: List[str]


def rank_candidates(candidates: List[Candidate]) -> List[RankedProposal]:
    """Rank READY candidates deterministically.

    Sort: NextWeight DESC, RouteValue DESC, candidate_id ASC (stable tie).
    Deterministic: identical input → identical ranking.
    """
    ready = ready_set(candidates)
    # locality peer counts (for resonance)
    loc_count: Dict[str, int] = {}
    for c in ready:
        loc_count[c.locality] = loc_count.get(c.locality, 0) + 1
    ranked: List[RankedProposal] = []
    for c in ready:
        ag = anti_gaming_checks(c)
        peers = max(0, loc_count.get(c.locality, 1) - 1)
        sc = score_candidate(c, locality_peers=peers)
        ranked.append(RankedProposal(candidate=c, score=sc, rank=0,
                                     anti_gaming=ag))
    # Deterministic: NextWeight DESC, RouteValue DESC, id ASC
    ranked.sort(key=lambda r: (-r.score.next_weight,
                               -r.score.route_value,
                               r.candidate.candidate_id))
    for i, r in enumerate(ranked, start=1):
        r.rank = i
    return ranked


# ── I: locality batching ─────────────────────────────────────────────
@dataclass
class BatchProposal:
    batch_id: str
    locality: str
    members: List[str]
    rationale: str
    combined_closures: int


def propose_batches(ranked: List[RankedProposal]) -> List[BatchProposal]:
    """Identify coherent batches (same locality, resonant, low-interference).

    Batching is itself a proposal — it cannot mutate scope.
    A batch is proposed when ≥2 READY candidates share a locality,
    each has scope_interference ≤ 0.5, and they are dependency-compatible
    (no member depends on another member's non-closure).
    """
    by_loc: Dict[str, List[RankedProposal]] = {}
    for r in ranked:
        by_loc.setdefault(r.candidate.locality, []).append(r)
    batches: List[BatchProposal] = []
    for loc, members in sorted(by_loc.items()):
        if len(members) < 2 or loc == "general":
            continue
        if any(m.candidate.scope_interference > 0.5 for m in members):
            continue
        ids = [m.candidate.candidate_id for m in members]
        # dependency-compatible: no member blocked on another member
        # (all are READY, so dependencies are met; check no inter-dependency
        # that would force ordering — we allow ordering, just note it)
        inter = [m.candidate.candidate_id for m in members
                 if any(d in ids for d in m.candidate.dependencies)]
        batches.append(BatchProposal(
            batch_id=f"batch-{loc}",
            locality=loc,
            members=ids,
            rationale=(f"{len(ids)} READY candidates in locality '{loc}' "
                       f"with low interference; inter-dependencies: {inter or 'none'}"),
            combined_closures=sum(m.candidate.expected_closures
                                  for m in members),
        ))
    return batches


# ── Q: sensitivity ───────────────────────────────────────────────────
def sensitivity(c: Candidate, peers: int = 0) -> Dict[str, Any]:
    """Show how the ranking responds to counterfactual changes.

    Not probabilistic forecasting — deterministic recomputation under
    stated alternate assumptions.
    """
    base = score_candidate(c, locality_peers=peers)
    out: Dict[str, Any] = {"base_next_weight": base.next_weight,
                           "scenarios": {}}

    def _clone(**kw):
        import copy
        cc = copy.copy(c)
        for k, v in kw.items():
            setattr(cc, k, v)
        return cc

    scenarios = {
        "dependency_blocked": _clone(state=BLOCKED),
        "verification_confidence_halved": _clone(
            verification_confidence=c.verification_confidence / 2.0),
        "scope_interference_doubled": _clone(
            scope_interference=min(1.0, c.scope_interference * 2.0)),
        "reuse_was_projection": _clone(expected_reuse=0.2),
    }
    for name, cc in scenarios.items():
        s = score_candidate(cc, locality_peers=peers)
        out["scenarios"][name] = {
            "next_weight": s.next_weight,
            "delta": round(s.next_weight - base.next_weight, 4),
        }
    return out


# ── O: first-run packet ──────────────────────────────────────────────
def nbd_packet(program: Any, candidates: List[Candidate],
             main_commit: str = "unknown") -> Dict[str, Any]:
    """Run NBD-Ω and return the recommendation packet (read-only)."""
    fp = state_fingerprint(program, main_commit=main_commit)
    classify_candidates(candidates)
    ranked = rank_candidates(candidates)
    batches = propose_batches(ranked)
    top = ranked[0] if ranked else None
    return {
        "nbd_engine_version": ENGINE_VERSION,
        "AUTONOMY": "NO",
        "DIRECTOR_DECISION_REQUIRED": "YES",
        "EXECUTION_AUTHORITY": "NONE",
        "state_fingerprint": fp,
        "fingerprint_hash": fingerprint_hash(fp),
        "candidates": [c.as_dict() for c in candidates],
        "ready_set": [r.candidate.candidate_id for r in ranked],
        "ranked": [{
            "rank": r.rank,
            "candidate_id": r.candidate.candidate_id,
            "title": r.candidate.title,
            "next_weight": r.score.next_weight,
            "route_value": r.score.route_value,
            "dw": r.score.dw,
            "components": r.score.components,
            "projection_flags": r.score.projection_flags,
            "anti_gaming": r.anti_gaming,
            "state": r.candidate.state,
        } for r in ranked],
        "batches": [b.__dict__ for b in batches],
        "top_proposal": ({
            "candidate_id": top.candidate.candidate_id,
            "title": top.candidate.title,
            "next_weight": top.score.next_weight,
            "explanation": _explain(top),
        } if top else None),
        "stale": False,
    }


def _explain(r: RankedProposal) -> str:
    c = r.candidate
    s = r.score
    parts = [
        f"{c.title} ranks #{r.rank} with NextWeight {s.next_weight} "
        f"(DW {s.dw}, RouteValue {s.route_value}).",
    ]
    comps = s.components
    parts.append(
        f"Closures {comps['C_closures']}, readiness {comps['D_readiness']}, "
        f"resonance {comps['R_resonance']}, verification confidence "
        f"{comps['V_confidence']}, risk {comps['K_risk']}, interference "
        f"{comps['S_interference']}.")
    if r.anti_gaming:
        parts.append("Anti-gaming adjustments: " + "; ".join(r.anti_gaming))
    proj = [f for f in s.projection_flags]
    parts.append(f"Projected inputs (not fact): {', '.join(proj)}.")
    ev_kinds = {}
    for e in c.evidence:
        ev_kinds[e.kind] = ev_kinds.get(e.kind, 0) + 1
    parts.append(f"Evidence: {ev_kinds}.")
    return " ".join(parts)


# ── L: staleness check ───────────────────────────────────────────────
def is_stale(packet: Dict[str, Any], program: Any) -> bool:
    """A packet is stale if the state fingerprint no longer matches."""
    old = packet.get("state_fingerprint", {})
    new = state_fingerprint(program)
    for k in ("main_commit", "outcome_ledger_count",
              "duobeta_ledger_count", "generation_id"):
        if old.get(k) != new.get(k):
            return True
    return False


# ── LEAS-I: canonical ledger integration ─────────────────────────────
def sync_from_ledger(candidates: List[Candidate]) -> List[str]:
    """Sync candidate states from the canonical circuit ledger.

    Returns list of candidate_ids whose state was updated.
    Enforces no-resurrection: CLOSED candidates cannot become OPEN/READY
    via sync (they're already CLOSED; sync only confirms).

    This is the ONE place where ledger state flows into NBD.
    Do not duplicate circuit state manually elsewhere.
    """
    try:
        from .circuit_ledger import build_ledger, is_resurrection
    except ImportError:
        return []  # Ledger not available; no sync
    ledger = {c.circuit_id: c for c in build_ledger()}
    updated = []
    # Map candidate -> circuit IDs via evidence or candidate_id conventions
    # For now: candidates carry circuit refs in their evidence; we match
    # by known mappings. A full mapping table lives in nbd_candidates.py.
    try:
        from .nbd_candidates import CANDIDATE_CIRCUIT_MAP
    except ImportError:
        CANDIDATE_CIRCUIT_MAP = {}
    for cand in candidates:
        circuit_ids = CANDIDATE_CIRCUIT_MAP.get(cand.candidate_id, [])
        for cid in circuit_ids:
            circ = ledger.get(cid)
            if circ is None:
                continue
            # Enforce no-resurrection
            if is_resurrection(cid, circ.state):
                # Ledger says CLOSED but candidate would reopen — this is
                # a bug in the map or ledger, not a valid transition.
                continue
            # Sync CLOSED state from ledger
            if circ.state == "CLOSED" and cand.state != "CLOSED":
                cand.state = CLOSED
                updated.append(cand.candidate_id)
            elif circ.state == "BLOCKED" and cand.state == "OPEN":
                cand.state = BLOCKED
                cand.blocked_reason = f"Ledger: {cid} BLOCKED"
                updated.append(cand.candidate_id)
            elif circ.state in ("SUPERSEDED", "HISTORICAL_ONLY") and cand.state != "CLOSED":
                # Superseded/historical circuits cannot rank; mark CLOSED
                # to exclude from READY competition (they're resolved, not open).
                cand.state = CLOSED
                updated.append(cand.candidate_id)
            elif circ.state == "OPEN":
                # RCCR-I: Circuit is OPEN (not yet classified). The candidate
                # cannot become READY until the circuit is classified.
                # Mark the flag; classify_candidates() will respect it.
                cand.circuit_needs_classification = True
                updated.append(cand.candidate_id)
    return updated
