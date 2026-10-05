#!/usr/bin/env python3
"""DBEL-I: DuoBeta Evidence Learning (NBD-Ω-007).

Connects verified execution evidence (Outcome V1) to DuoBeta's
learning/growth mechanisms WITHOUT autonomous code mutation, truth
promotion, or authority bypass.

Law:
  OBSERVED EXPERIENCE > EVIDENCE EXTRACTION > PROPOSAL > GATE >
  ACCEPT/REJECT > DURABLE LEARNING STATE > FUTURE SELECTION INFLUENCE

NOT: outcome > rewrite code. NOT: outcome > declare truth.
NOT: outcome > silently mutate canonical knowledge.

AUTONOMY=NO: this module observes, proposes, gates, records, and
applies explicitly authorized metadata updates. It never rewrites
runtime code, invents execution semantics, merges PRs, changes
authority laws, promotes knowledge to truth, or executes directives.

Learned state lives in the EXISTING DuoBeta ledger (program.duo.ledger)
as GrowthEntries with structured `meta` (kind=learn). No parallel ledger.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

MIN_EVIDENCE = 3
ALLOWED_KINDS = ("preference", "avoidance", "blocked_association")
KIND_RESULT = {"preference": "completed", "avoidance": "failed",
               "blocked_association": "blocked"}

# ASI-I (NBD-Ω-008): bound on the learned score's production influence.
# The score is a LINEAR count (success − failure − blocked); the bound
# limits its contribution to selection ordering. Minimum safeguard
# against reinforcement runaway; no decay math, no stochasticity.
#
# AEC-I (NBD-Ω-018): replaced destructive hard clamp (ASI_LEARNED_CAP=5)
# with bounded monotonic saturation. Raw evidence ordering is preserved:
# 6 < 10 raw MUST remain 6-equiv < 10-equiv after bounding.
#
# Transform: f(raw) = (raw * SATURATION_SCALE) / (SATURATION_SCALE + |raw|)
#   - Bounded: |f(raw)| < SATURATION_SCALE (never reached, asymptotically approached)
#   - Strictly monotonic: raw A < raw B ⟹ f(A) < f(B) (no false ties)
#   - Sign-preserving: f(0)=0, sign(f(x))=sign(x)
#   - Deterministic: pure float ops (IEEE 754), no randomness
#
# SATURATION_SCALE justification:
#   MIN_EVIDENCE = 3 (minimum meaningful learning signal).
#   SATURATION_SCALE = 100 = 33× MIN_EVIDENCE.
#   - Realistic strong preference (10-30) experiences <10% compression.
#   - At raw=100, f=50 (50% compression, still distinct and ordered).
#   - Beyond 100, asymptotic compression prevents runaway domination.
#   - Bound (100) is never reached, only approached; no hard threshold collapse.
#
# This is NOT a bigger clamp. It is a different representation: continuous
# saturation vs destructive clipping. The scale is justified by evidence
# semantics, not chosen arbitrarily.
SATURATION_SCALE = 100.0

# DEPRECATED: ASI_LEARNED_CAP removed by AEC-I. Retained as alias for
# backward compatibility with tests/diagnostics that reference it.
# New code should use SATURATION_SCALE and saturate_learned_score().
ASI_LEARNED_CAP = 5


def saturate_learned_score(raw: int) -> float:
    """AEC-I (NBD-Ω-018): bounded monotonic saturation of learned evidence.

    Transforms raw evidence count (success − failure − blocked) into a
    bounded advisory score.

    Contract:
      - BOUNDED: |result| < SATURATION_SCALE (100.0)
      - MONOTONIC (supported domain): for |raw| < 6255496814851557,
        raw A < raw B ⟹ result A < result B (strict)
      - SIGN-PRESERVING: sign(result) == sign(raw); f(0) == 0.0
      - DETERMINISTIC: pure function, no state, no randomness
      - PURE/READ-ONLY: does not modify inputs or global state

    WO-5.4 / D20-P #15 ADMISSION: Strict ordering is NOT guaranteed for
    |raw| >= 6255496814851557 (~6.25e15) due to IEEE 754 double-precision
    limits. At 10^18, f(x) and f(x+1) both equal 99.99999999999999.
    This is a bounded finding, not a defect in the formula:
    - The raw evidence (ledger counts) is preserved exactly as integers.
    - The score is ADVISORY influence, never truth.
    - Selectors MUST define deterministic tie-breaking for score collisions
      (see suggest_preferred: ties broken by raw count, then ID).
    - Supported domain for strict ordering: |raw| < 6255496814851557.

    Float determinism: uses only multiplication, division, abs — all
    IEEE 754 deterministic. Codebase already uses floats deterministically
    for Jaccard similarity in Relevance V2 ranking.

    This bounds INFLUENCE, not raw evidence. The underlying ledger
    (success/failure/blocked counts) is untouched.
    """
    if raw == 0:
        return 0.0
    # f(x) = (x * S) / (S + |x|)
    # Strictly increasing, bounded by S, sign-preserving.
    return (raw * SATURATION_SCALE) / (SATURATION_SCALE + abs(raw))


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _learn_entries(program: Any) -> List[Any]:
    duo = getattr(program, "duo", None)
    ledger = getattr(duo, "ledger", None) or []
    return [e for e in ledger
            if isinstance(getattr(e, "meta", None), dict)
            and (e.meta or {}).get("kind") == "learn"]


def _append_learn_entry(program: Any, detail: str, meta: Dict[str, Any]) -> Any:
    """Append a learning entry to the DuoBeta ledger (durable via duo_ledger).

    WO-5.4: If program.learning_record is False, returns None without
    recording. The ledger is unchanged.
    """
    # WO-5.4: Recording OFF → do not record.
    if not getattr(program, "learning_record", True):
        return None
    from form.duobeta.growth import GrowthEntry
    duo = program.duo
    duo.generation += 1
    entry = GrowthEntry(gen=duo.generation, detail=str(detail)[:120],
                        ts=_ts(), meta=dict(meta))
    duo.ledger.append(entry)
    return entry


# ── E: evidence extraction ────────────────────────────────────────────
def extract_evidence(program: Any, outcome_id: str) -> Dict[str, Any]:
    """Extract consumable evidence from an Outcome V1 record.

    Every field carries source/meaning/scope. Knowledge provenance is
    included ONLY when actually present (never invented).
    """
    from .outcome_ledger import get_outcome
    rec = get_outcome(program, str(outcome_id or ""))
    if not rec:
        return {"ok": False, "status": "not_recorded",
                "detail": f"no outcome {outcome_id}"}
    knowledge = [k.get("id") for k in (rec.get("knowledge") or [])
                 if isinstance(k, dict) and k.get("id")]
    return {
        "ok": True,
        "outcome_id": rec.get("outcome_id"),
        "fields": {
            "result": {"value": rec.get("result"), "source": "Outcome V1",
                       "meaning": "execution outcome (not truth)",
                       "scope": "single execution"},
            "dell": {"value": rec.get("dell"), "source": "Outcome V1",
                     "meaning": "operator identity", "scope": "single execution"},
            "operation": {"value": rec.get("operation"), "source": "Outcome V1",
                          "meaning": "semantic operation", "scope": "single execution"},
            "knowledge_ids": {"value": knowledge, "source": "Outcome V1.knowledge",
                              "meaning": "involved knowledge (only when provenanced)",
                              "scope": "only when present; empty stays empty"},
            "generation_id": {"value": rec.get("generation_id"), "source": "Outcome V1",
                              "meaning": "temporal scope", "scope": "single execution"},
        },
    }


# ── F: proposal stage ─────────────────────────────────────────────────
def propose(program: Any, kind: str, dell: Any,
            knowledge_id: Optional[str] = None,
            evidence_outcome_ids: Optional[List[str]] = None) -> Dict[str, Any]:
    """Stage a learning proposal (inspectable before application).

    Returns the proposal dict. The proposal is recorded in the DuoBeta
    ledger as PROPOSED. Forbidden targets (code, truth, conflicts) cannot
    be expressed: the schema has no such fields.
    """
    try:
        dell_n = int(dell)
    except (TypeError, ValueError):
        dell_n = None
    oids = list(evidence_outcome_ids or [])
    kid = str(knowledge_id) if knowledge_id else None
    entry = _append_learn_entry(
        program,
        f"LEARN PROPOSED {kind} dell={dell_n} knowledge={kid}",
        {"kind": "learn", "proposal_kind": str(kind), "dell": dell_n,
         "knowledge_id": kid, "status": "PROPOSED",
         "evidence": {"outcome_ids": oids}, "gate": None,
         "reason": "", "proposed_ts": _ts()})
    # WO-5.4: If recording is OFF, _append_learn_entry returns None.
    if entry is None:
        return {"ok": False, "reason": "learning_record_disabled",
                "detail": "Recording is OFF; proposal not staged."}
    return {"ok": True, "proposal_id": entry.gen, "kind": kind,
            "dell": dell_n, "knowledge_id": kid,
            "evidence_outcome_ids": oids, "status": "PROPOSED"}


def get_proposal(program: Any, proposal_id: Any) -> Optional[Dict[str, Any]]:
    """Inspect a staged proposal (read-only)."""
    try:
        pid = int(proposal_id)
    except (TypeError, ValueError):
        return None
    for e in _learn_entries(program):
        if e.gen == pid:
            m = e.meta or {}
            return {"proposal_id": e.gen, "kind": m.get("proposal_kind"),
                    "dell": m.get("dell"), "knowledge_id": m.get("knowledge_id"),
                    "status": m.get("status"),
                    "evidence_outcome_ids": (m.get("evidence") or {}).get("outcome_ids", []),
                    "gate": m.get("gate"), "reason": m.get("reason", ""),
                    "detail": e.detail, "ts": e.ts}
    return None


# ── G: gate ───────────────────────────────────────────────────────────
def gate_proposal(program: Any, proposal_id: Any) -> Dict[str, Any]:
    """Deterministic gate. Ordered rules; REJECTED persists with reason.

    Rules:
      1. kind allowed else REJECTED(forbidden_kind)
      2. 1<=dell<=99 else REJECTED(out_of_scope)
      3. >=MIN_EVIDENCE supporting outcomes else REJECTED(insufficient_evidence)
      4. supporting results match kind else REJECTED(evidence_mismatch)
      5. knowledge_id in evidence knowledge (when claimed) else REJECTED(evidence_mismatch)
      6. not already APPLIED for (kind,dell,knowledge_id) else REJECTED(duplicate)
    """
    from .outcome_ledger import get_outcome
    pid = int(proposal_id)
    target = None
    for e in _learn_entries(program):
        if e.gen == pid:
            target = e
            break
    if target is None:
        return {"ok": False, "accepted": False, "reason": "unknown_proposal"}
    m = target.meta or {}
    if m.get("status") != "PROPOSED":
        return {"ok": False, "accepted": False,
                "reason": f"not_proposed (status={m.get('status')})"}

    def reject(reason: str) -> Dict[str, Any]:
        m["status"] = "REJECTED"
        m["gate"] = {"accepted": False, "reason": reason, "ts": _ts()}
        m["reason"] = reason
        return {"ok": True, "accepted": False, "reason": reason,
                "proposal_id": pid}

    kind = m.get("proposal_kind")
    if kind not in ALLOWED_KINDS:
        return reject("forbidden_kind")
    dell = m.get("dell")
    if not isinstance(dell, int) or not (1 <= dell <= 99):
        return reject("out_of_scope")

    want_result = KIND_RESULT[kind]
    oids = (m.get("evidence") or {}).get("outcome_ids") or []
    dell_matched = []
    supporting = []
    knowledge_seen = set()
    for oid in oids:
        rec = get_outcome(program, oid)
        if not rec:
            continue
        if rec.get("dell") != dell:
            continue
        dell_matched.append(oid)
        if str(rec.get("result")) != want_result:
            continue
        supporting.append(oid)
        for k in (rec.get("knowledge") or []):
            if isinstance(k, dict) and k.get("id"):
                knowledge_seen.add(k["id"])
    if len(dell_matched) < MIN_EVIDENCE:
        return reject("insufficient_evidence")
    if len(supporting) < MIN_EVIDENCE:
        return reject("evidence_mismatch")
    kid = m.get("knowledge_id")
    if kid and kid not in knowledge_seen:
        return reject("evidence_mismatch")

    for e in _learn_entries(program):
        em = e.meta or {}
        if (em.get("status") == "APPLIED"
                and em.get("proposal_kind") == kind
                and em.get("dell") == dell
                and em.get("knowledge_id") == kid):
            return reject("duplicate")

    m["status"] = "ACCEPTED"
    m["gate"] = {"accepted": True, "reason": "all_rules_pass",
                 "supporting": supporting, "ts": _ts()}
    m["evidence"] = {"outcome_ids": oids, "supporting": supporting}
    m["reason"] = ""
    return {"ok": True, "accepted": True, "reason": "all_rules_pass",
            "proposal_id": pid, "supporting": supporting}


# ── Apply (I: application boundary) ───────────────────────────────────
def apply_proposal(program: Any, proposal_id: Any) -> Dict[str, Any]:
    """Apply an ACCEPTED proposal. Modifies ONLY the DuoBeta ledger entry
    (status → APPLIED). The preference index is derived, never separately
    persisted. Never touches code/registry/semantics/outcomes/truth/
    conflicts/persistence/generation architecture."""
    pid = int(proposal_id)
    for e in _learn_entries(program):
        if e.gen == pid:
            m = e.meta or {}
            if m.get("status") != "ACCEPTED":
                return {"ok": False, "applied": False,
                        "reason": f"not_accepted (status={m.get('status')})"}
            m["status"] = "APPLIED"
            m["applied_ts"] = _ts()
            return {"ok": True, "applied": True, "proposal_id": pid}
    return {"ok": False, "applied": False, "reason": "unknown_proposal"}


# ── Preference index (M: heat honesty — separable, never collapsed) ───
def preference_index(program: Any) -> Dict[Tuple[Any, Any], Dict[str, Any]]:
    """Derived from APPLIED ledger entries. Separable counters:
    success / failure / blocked / last_seen. No collapsed score, no truth."""
    idx: Dict[Tuple[Any, Any], Dict[str, Any]] = {}
    for e in _learn_entries(program):
        m = e.meta or {}
        if m.get("kind") != "learn" or m.get("status") != "APPLIED":
            continue
        key = (m.get("dell"), m.get("knowledge_id"))
        cell = idx.setdefault(key, {"success": 0, "failure": 0,
                                    "blocked": 0, "last_seen": ""})
        n = len((m.get("evidence") or {}).get("supporting", [])
                or (m.get("evidence") or {}).get("outcome_ids", []))
        pk = m.get("proposal_kind")
        if pk == "preference":
            cell["success"] += n
        elif pk == "avoidance":
            cell["failure"] += n
        elif pk == "blocked_association":
            cell["blocked"] += n
        if m.get("applied_ts"):
            cell["last_seen"] = m["applied_ts"]
    return idx


def suggest_preferred(program: Any, dell: Any,
                      knowledge_ids: List[str]) -> List[str]:
    """Rank knowledge candidates by learned preference (transparent).

    Score = success − failure − blocked (documented, separable).
    No learning → original order. Ties → original order (stable).
    This is the bounded 'future selection' DBEL-I influences.
    The certified 37 selector is untouched.

    WO-5.4: If program.learning_influence is False, returns baseline
    order (identical inputs → identical outputs, no learning effect).
    """
    try:
        dell_n = int(dell)
    except (TypeError, ValueError):
        return list(knowledge_ids)
    # WO-5.4: Learning influence OFF → baseline order.
    if not getattr(program, "learning_influence", True):
        return list(knowledge_ids)
    idx = preference_index(program)

    def score(kid: str) -> int:
        c = idx.get((dell_n, kid), {})
        return int(c.get("success", 0)) - int(c.get("failure", 0)) - int(c.get("blocked", 0))

    order = {kid: i for i, kid in enumerate(knowledge_ids)}
    return sorted(knowledge_ids, key=lambda k: (-score(k), order.get(k, 0)))


def bounded_learned_score(program: Any, dell: Any,
                          knowledge_id: str) -> float:
    """ASI-I (NBD-Ω-008) / AEC-I (NBD-Ω-018): bounded learned preference score.

    Score = saturate(success − failure − blocked), derived from APPLIED
    DuoBeta learning entries only. Bounded, monotonic, sign-preserving;
    no collapsed "heat", no truth claim.

    AEC-I: replaced destructive hard clamp with monotonic saturation.
    Raw evidence ordering is preserved within the supported domain:
    6 < 10 raw ⟹ f(6) < f(10).

    WO-5.4 ADMISSION: Strict ordering holds for |raw| < 6255496814851557.
    Beyond that, IEEE 754 collisions occur (see saturate_learned_score).
    The suggest_preferred selector uses raw integers (not saturated floats)
    and is therefore unaffected. Ties are broken deterministically by
    original order.

    This is an ADVISORY preference. It is NOT truth, eligibility,
    revision, dependency satisfaction, conflict resolution, disposition,
    permission, or execution authority. It may only reorder candidates
    that have already passed the hard eligibility laws; it can never
    add, remove, or resurrect a candidate.

    No learning → 0.0 (cold start: selection order exactly baseline).

    WO-5.4: If program.learning_influence is False, returns 0.0.
    """
    try:
        dell_n = int(dell)
    except (TypeError, ValueError):
        return 0.0
    # WO-5.4: Learning influence OFF → 0.0 (baseline).
    if not getattr(program, "learning_influence", True):
        return 0.0
    idx = preference_index(program)
    # Key must match preference_index exactly: (dell, knowledge_id as stored).
    # Do NOT stringify None (DBEL-I stores None for unassociated learning).
    key = (dell_n, knowledge_id)
    c = idx.get(key, {})
    raw = (int(c.get("success", 0)) - int(c.get("failure", 0))
           - int(c.get("blocked", 0)))
    return saturate_learned_score(raw)


def learning_ledger(program: Any) -> List[Dict[str, Any]]:
    """Read-only view of learning entries (for ROS-I inspection)."""
    out = []
    for e in _learn_entries(program):
        m = e.meta or {}
        out.append({"proposal_id": e.gen, "kind": m.get("proposal_kind"),
                    "dell": m.get("dell"), "knowledge_id": m.get("knowledge_id"),
                    "status": m.get("status"), "reason": m.get("reason", ""),
                    "detail": e.detail, "ts": e.ts})
    return out
