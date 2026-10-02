#!/usr/bin/env python3
"""ROS-I: Runtime Observability Surface (NBD-Ω-006).

Canonical READ-ONLY observation functions over existing live evidence.

LAW: OBSERVATION MUST NOT EXECUTE, MUTATE, OR PERSIST.
Every function below is a pure read: it never executes a Dell, never
modifies Program/Nursery/conflicts/DuoBeta, never commits a checkpoint,
never changes generation, and never creates an Outcome record.

Honest-unknown vocabulary (Phase L):
  known            evidence present
  not_recorded     the ledger/query has no entry
  not_applicable   concept does not apply to this item
  ephemeral        EPHEMERAL_BY_DESIGN (never presented as durable)
  blocked          policy boundary (reason given, never invented)
  unsupported      capability boundary

Empty knowledge provenance remains empty. Outcome != truth is explicit
in every trace/query result.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional


# ── Phase E: Dell explain ─────────────────────────────────────────────
def explain_dell(n: Any) -> Dict[str, Any]:
    """Factual read-only metadata for a Dell address.

    All fields come from the registry and existing policy tables.
    Nothing is invented. Unknown addresses return ok=False honestly.
    """
    try:
        addr = int(n)
    except (TypeError, ValueError):
        return {"ok": False, "status": "unknown_dell",
                "detail": f"{n!r} is not a Dell address"}
    from . import registry
    rec = registry.get_dell(addr)
    if not rec:
        return {"ok": False, "status": "unknown_dell",
                "detail": f"Dell {addr} is not registered"}
    from .operator_bridge import BLOCKED_WITH_REASON, _BLOCK_REASONS, _RAW_ONLY_REASONS

    namespace = str(rec.get("namespace", ""))
    is_core_i = namespace == "CORE_I" or (0 <= addr <= 50)
    is_core_ii = namespace == "CORE_II" or (51 <= addr <= 99)

    if addr in BLOCKED_WITH_REASON:
        semantic_access = "BLOCKED"
        policy = {"restriction": "blocked_with_reason",
                  "reason": _BLOCK_REASONS.get(addr, "")}
    elif addr == 99:
        semantic_access = "MANDELL_ONLY"
        policy = {"restriction": "intentionally_raw_only",
                  "reason": _RAW_ONLY_REASONS.get(addr, "")}
    else:
        semantic_access = "CANONICAL_ENGLISH"
        policy = {"restriction": "none", "reason": ""}

    # Execution authority (existing, factual).
    if addr in (21, 22):
        authority = "live_identity (merge_live/split_live) via execute_seed"
    elif addr in (27, 28):
        authority = "core_i_recovery via execute_seed (Dell 27 commits Generation V1)"
    elif addr == 99:
        authority = "spectrum_ops compose via execute_chain (raw only)"
    elif is_core_i:
        authority = "apply_core_i / executor_leaf via execute_seed; chain leaf via execute_chain"
    else:
        authority = "execute_chain > execute_core_ii"

    return {
        "ok": True,
        "status": "known",
        "address": addr,
        "canonical_name": rec.get("name"),
        "manor": rec.get("manor"),
        "classification": "Core-I" if is_core_i else ("Core-II" if is_core_ii else "unknown"),
        "execution_authority": authority,
        "semantic_accessibility": semantic_access,
        "raw_accessibility": "RAW_MANDELL (all nine flows; 86/87/88 attempt execution, may fail on operands)",
        "policy": policy,
        "flow_compatibility": "all nine flows (>, >>, >>>, ::, :, :>, <:, <:>, <<[Delta]) via raw chain_exec",
        "outcome_is_observation": True,
    }


# ── Phase F: execution trace ──────────────────────────────────────────
def execution_trace(program: Any, outcome_id: Optional[str] = None) -> Dict[str, Any]:
    """Coherent read-only trace of an execution, as a view over existing evidence.

    Uses the Outcome V1 record + re-parsing the RECORDED input (parse_seed
    is pure analysis, not execution). Never invents per-node events.
    outcome_id=None traces the latest recorded outcome.
    """
    from .outcome_ledger import get_outcome, list_outcomes
    rec = None
    if outcome_id:
        rec = get_outcome(program, outcome_id)
        if not rec:
            return {"ok": False, "status": "not_recorded",
                    "detail": f"no outcome {outcome_id} in this program's ledger"}
    else:
        latest = list_outcomes(program, limit=1)
        if not latest:
            return {"ok": False, "status": "not_recorded",
                    "detail": "no outcomes recorded for this program"}
        rec = latest[0]

    mandell = str(rec.get("mandell") or rec.get("input") or "")
    atoms: List[Dict[str, Any]] = []
    flows: List[str] = []
    parse_status = "known"
    try:
        from .seed import parse_seed
        parsed = parse_seed(mandell)
        if parsed.ok:
            atoms = [{"dell": a.dell, "term": a.term,
                      "mandell": a.as_mandel()} for a in (parsed.atoms or [])]
            flows = list(parsed.flows or [])
        else:
            parse_status = "not_applicable (input was not a parseable seed)"
    except Exception:
        parse_status = "not_applicable (input could not be re-parsed)"

    knowledge = rec.get("knowledge") or []
    return {
        "ok": True,
        "status": "known",
        "outcome_id": rec.get("outcome_id"),
        "input_understood": mandell,
        "resolved_to": {"dell": rec.get("dell"),
                        "operation": rec.get("operation"),
                        "semantic": rec.get("semantic")},
        "ordered_atoms": atoms,
        "parse_status": parse_status,
        "flow_used": flows,
        "what_happened": {"result": rec.get("result"),
                          "ok": rec.get("result") == "completed",
                          "error": rec.get("error") or ""},
        "messages": list(rec.get("messages") or [])[:12],
        "knowledge_involved": knowledge if knowledge else "not_recorded (empty provenance remains empty)",
        "generation": rec.get("generation_id") or "not_recorded",
        "outcome_is_observation": True,
        "outcome_is_not_truth": True,
    }


# ── Phase G: outcome inspection ───────────────────────────────────────
def latest_outcomes(program: Any, limit: int = 10) -> List[Dict[str, Any]]:
    """Latest Outcome V1 records (existing query authority). Read-only."""
    from .outcome_ledger import list_outcomes
    try:
        n = max(1, min(int(limit), 100))
    except (TypeError, ValueError):
        n = 10
    return list_outcomes(program, limit=n)


def outcomes_for_dell(program: Any, n: Any) -> Dict[str, Any]:
    """Outcome V1 records for a Dell address. Honest when none exist."""
    try:
        addr = int(n)
    except (TypeError, ValueError):
        return {"ok": False, "status": "unknown_dell", "outcomes": []}
    from .outcome_ledger import list_outcomes
    recs = [r for r in list_outcomes(program, limit=1000)
            if r.get("dell") == addr]
    return {"ok": True,
            "status": "known" if recs else "not_recorded",
            "dell": addr, "count": len(recs), "outcomes": recs}


def outcomes_by_status(program: Any, status: str) -> Dict[str, Any]:
    """Outcome V1 records filtered by result status."""
    valid = {"completed", "failed", "blocked", "skipped"}
    s = str(status or "").lower()
    if s not in valid:
        return {"ok": False, "status": "unsupported",
                "detail": f"status must be one of {sorted(valid)}",
                "outcomes": []}
    from .outcome_ledger import list_outcomes
    recs = [r for r in list_outcomes(program, limit=1000)
            if str(r.get("result")) == s]
    return {"ok": True, "status": "known" if recs else "not_recorded",
            "result": s, "count": len(recs), "outcomes": recs}


def outcome_by_id(program: Any, outcome_id: str) -> Dict[str, Any]:
    """Specific Outcome V1 lookup. Honest when absent."""
    from .outcome_ledger import get_outcome
    rec = get_outcome(program, str(outcome_id or ""))
    if not rec:
        return {"ok": False, "status": "not_recorded",
                "detail": f"no outcome {outcome_id} in this program's ledger"}
    return {"ok": True, "status": "known", "outcome": rec}


def outcomes_for_knowledge_item(program: Any, knowledge_id: str) -> Dict[str, Any]:
    """Outcome V1 records carrying provenance for a knowledge item."""
    from .outcome_ledger import outcomes_for_knowledge
    recs = outcomes_for_knowledge(program, str(knowledge_id or ""))
    return {"ok": True,
            "status": "known" if recs else "not_recorded",
            "knowledge_id": knowledge_id, "count": len(recs),
            "outcomes": recs}


# ── Phase H: runtime health ───────────────────────────────────────────
def runtime_health(owner: str = "Operator") -> Dict[str, Any]:
    """Component/invariant availability. Read-only.

    Health means AVAILABLE, not intelligent, not truth-verified,
    not correct-answer-guaranteed. Each check is an import/attribute
    probe; failures report honestly.
    """
    checks: Dict[str, Dict[str, Any]] = {}

    def probe(name: str, fn) -> None:
        try:
            detail = fn()
            checks[name] = {"available": True, "detail": detail}
        except Exception as exc:
            checks[name] = {"available": False,
                            "detail": f"{type(exc).__name__}: {exc}"}

    def _registry():
        from . import registry
        r = registry.get_dell(70)
        return f"name={r['name']}" if r else "empty"
    probe("registry", _registry)

    def _core_i():
        from .core_i_ops import HANDLED
        return f"{len(HANDLED)} handled atoms"
    probe("core_i_authority", _core_i)

    def _core_ii():
        from .core_ii_exec import execute_core_ii
        return "execute_core_ii importable"
    probe("core_ii_authority", _core_ii)

    def _router():
        from .semantic_router import route_intent
        return "route_intent importable"
    probe("semantic_router", _router)

    def _outcome():
        from .outcome_ledger import capture_outcome
        return "capture_outcome importable"
    probe("outcome_v1", _outcome)

    def _persist():
        from form.dell_matrix.atomic_write import PERSISTENCE_PROTOCOL_VERSION
        return f"protocol v{PERSISTENCE_PROTOCOL_VERSION}"
    probe("persistence_v2", _persist)

    def _generation():
        from .checkpoint_generation import current_generation_id
        gid = current_generation_id(owner)
        return f"current={gid}" if gid else "no generation committed yet"
    probe("generation_v1", _generation)

    def _nursery():
        from form.dell_matrix.nursery import Nursery
        return "Nursery importable"
    probe("knowledge_plane", _nursery)

    def _duobeta():
        from form.duobeta.growth import DuoBeta
        return "DuoBeta importable"
    probe("duobeta", _duobeta)

    all_ok = all(c["available"] for c in checks.values())
    return {"ok": all_ok, "owner": owner, "components": checks,
            "health_means": "component/invariant availability only",
            "health_does_not_mean": ["system intelligent", "truth verified",
                                     "correct answer guaranteed"]}


# ── Phase I: current state ────────────────────────────────────────────
def runtime_state(program: Any) -> Dict[str, Any]:
    """Read-only runtime state summary. Computed on the fly; nothing persisted.

    EPHEMERAL_BY_DESIGN fields (action_stack, last_nurture, last_checkpoint,
    _last_result) are never presented as durable. Last-execution evidence
    comes from the durable Outcome V1 ledger (legitimately available).
    """
    from .checkpoint_generation import current_generation_id
    from .outcome_ledger import list_outcomes

    owner = getattr(program, "owner", "Operator")
    try:
        generation = current_generation_id(owner)
    except Exception:
        generation = None

    # Knowledge plane (read-only summary).
    knowledge: Dict[str, Any] = {"status": "not_recorded"}
    nursery = getattr(program, "nursery", None)
    if nursery is not None and hasattr(nursery, "summary"):
        try:
            knowledge = {"status": "known", **dict(nursery.summary())}
        except Exception:
            pass

    # Conflict/disposition counts (read-only; never modified).
    conflicts: Dict[str, Any] = {"status": "not_recorded"}
    try:
        cq = getattr(program, "conflict_quarantine", None)
        if isinstance(cq, dict):
            conflicts = {"status": "known",
                         "quarantined_sets": len(cq)}
    except Exception:
        pass

    # Outcome counts by status (durable ledger).
    outcomes: Dict[str, Any] = {"status": "known", "counts": {},
                                "total": 0}
    try:
        recs = list_outcomes(program, limit=1000)
        counts: Dict[str, int] = {}
        for r in recs:
            s = str(r.get("result") or "unknown")
            counts[s] = counts.get(s, 0) + 1
        outcomes = {"status": "known", "counts": counts, "total": len(recs)}
    except Exception:
        outcomes = {"status": "not_recorded", "counts": {}, "total": 0}

    # DuoBeta summary (read-only attributes).
    duobeta: Dict[str, Any] = {"status": "not_recorded"}
    duo = getattr(program, "duo", None)
    if duo is not None:
        try:
            duobeta = {"status": "known",
                       "generation": getattr(duo, "generation", None),
                       "rings": list(getattr(duo, "rings", []) or []),
                       "ledger_len": len(getattr(duo, "ledger", []) or [])}
        except Exception:
            pass

    # Last execution evidence (durable ledger only — legitimate).
    last_execution: Dict[str, Any] = {"status": "not_recorded"}
    try:
        latest = list_outcomes(program, limit=1)
        if latest:
            r = latest[0]
            last_execution = {"status": "known",
                              "outcome_id": r.get("outcome_id"),
                              "operation": r.get("operation"),
                              "dell": r.get("dell"),
                              "result": r.get("result")}
    except Exception:
        pass

    return {
        "ok": True,
        "owner": owner,
        "current_generation": generation if generation else "not_recorded (no generation committed yet)",
        "knowledge": knowledge,
        "conflicts": conflicts,
        "outcomes": outcomes,
        "duobeta": duobeta,
        "last_execution": last_execution,
        "ephemeral_note": "action_stack/last_nurture/last_checkpoint/_last_result are EPHEMERAL_BY_DESIGN and not shown",
    }


# ── DBEL-I: learning inspection (read-only) ───────────────────────────
def learning_ledger_view(program: Any) -> Dict[str, Any]:
    """Read-only view of DuoBeta learning entries. Delegates to canonical
    DuoBeta state; gains no mutation authority."""
    from .duobeta_learn import learning_ledger
    try:
        entries = learning_ledger(program)
    except Exception:
        entries = []
    return {"ok": True,
            "status": "known" if entries else "not_recorded",
            "count": len(entries), "entries": entries}


def learned_preferences_view(program: Any) -> Dict[str, Any]:
    """Read-only view of the derived preference index (separable counters)."""
    from .duobeta_learn import preference_index
    try:
        idx = preference_index(program)
    except Exception:
        idx = {}
    prefs = [{"dell": k[0], "knowledge_id": k[1], **v}
             for k, v in idx.items()]
    return {"ok": True,
            "status": "known" if prefs else "not_recorded",
            "count": len(prefs), "preferences": prefs}


def selection_learning_view(program: Any, context: str) -> Dict[str, Any]:
    """ASI-I (NBD-Ω-008): read-only inspection of learned preference
    influence on knowledge selection.

    Returns whether learning affected the selection, which preference
    evidence applied (bounded scores), which hard filters ran before
    learning (revision/dependency exclusions), and the final selected
    candidate(s) — alongside the Relevance V2 baseline order.

    Pure read: delegates to select_for_context (no mutation authority).
    """
    from .knowledge_selector import select_for_context
    try:
        sel = select_for_context(program, context, operation="grow")
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}
    return {"ok": True,
            "learned_preference_applied":
                sel.get("learned_preference_applied", False),
            "learned_scores": sel.get("learned_scores", {}),
            "baseline_selected_ids": sel.get("baseline_selected_ids", []),
            "learned_selected_ids": sel.get("learned_selected_ids", []),
            "selected_ids": [s["id"] for s in sel.get("selected", [])],
            "supersession_exclusions":
                sel.get("supersession_exclusions", []),
            "dependency_exclusions": sel.get("dependency_exclusions", []),
            "eligible_count": sel.get("eligible_count", 0)}


def nbd_view(program: Any, candidate_id: str = "") -> Dict[str, Any]:
    """NBDE-I (NBD-Ω-009): read-only inspection of NBD-Ω recommendations.

    Runs the NBD engine (read-only) and returns the ranked proposals,
    or details for a specific candidate. Creates no outcomes, mutates
    no state.
    """
    from .nbd_engine import nbd_packet, is_stale
    from .nbd_candidates import build_frontier
    try:
        cands = build_frontier(program)
        pkt = nbd_packet(program, cands)
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}
    if candidate_id:
        cid = candidate_id.strip().lower()
        for c in pkt["candidates"]:
            if c["candidate_id"].lower() == cid:
                return {"ok": True, "candidate": c,
                        "stale": is_stale(pkt, program)}
        return {"ok": False, "error": f"unknown candidate {candidate_id!r}"}
    return {"ok": True,
            "ranked": pkt["ranked"],
            "batches": pkt["batches"],
            "top_proposal": pkt["top_proposal"],
            "ready_set": pkt["ready_set"],
            "fingerprint_hash": pkt["fingerprint_hash"],
            "stale": is_stale(pkt, program),
            "AUTONOMY": pkt["AUTONOMY"],
            "DIRECTOR_DECISION_REQUIRED":
                pkt["DIRECTOR_DECISION_REQUIRED"],
            "EXECUTION_AUTHORITY": pkt["EXECUTION_AUTHORITY"]}
