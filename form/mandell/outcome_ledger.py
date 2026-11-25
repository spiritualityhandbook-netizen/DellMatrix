#!/usr/bin/env python3
"""DCC-XX: Execution Outcome Ledger — Outcome Record V1.

Durable, queryable evidence connecting:

    KNOWLEDGE > SELECTION > CONFLICT DISPOSITION > EXECUTION > OBSERVED OUTCOME

LAW: OUTCOME != TRUTH.

An operation succeeding does NOT prove its input knowledge true.
An operation failing does NOT prove its input knowledge false.
Repeated success does NOT increase truth authority.
Repeated failure does NOT reject knowledge.

Outcome evidence is OBSERVATION. It may inform future explicit
mechanisms. DCC-XX MUST NOT autonomously mutate knowledge truth,
verification status, conflict disposition, revision authority, or
dependency authority based on outcome. AUTONOMY = NO.

Relationship to Program.history: history is the lossy operational UX
event stream (last 24 unstructured lines). The outcome ledger is the
durable structured evidence store. No authority is duplicated — the
ledger carries fields history never had (stable identity, revision
snapshots, conflict/disposition snapshots, result status).

Capture point: the ``route_intent`` result boundary in
form/mandell/semantic_router.py. Every intent-driven execution passes
through it (single commands and every flow node). Capture is post-hoc
observation; routing behavior is untouched. No second executor.

Freshness gate (DCC-XX-C1): the arm's structured receipt
(``program.last_nurture``) is a single-slot attribute shared across
calls. The ``route_intent`` wrapper snapshots its identity before
execution and only attributes knowledge/conflict provenance to the
outcome when the executed call replaced it. A previous successful
call's evidence can never contaminate a later blocked, failed,
no-route, or non-knowledge outcome.

Blocked semantics (DCC-XX-C1): a Dell 37 contextual grow whose
conflict routing quarantined every selected unit (conflicts detected,
``routable_selected_ids`` empty, ``quarantined_ids`` non-empty) records
``blocked`` — the routing succeeded but the intended execution did not
occur. Partial quarantine (some routable) and empty selection remain
``completed``/``failed`` per the arm's honest receipt.

Identity: ``out1:`` + sha256(version|owner|seq|operation|knowledge
part|conflict part|result)[:32]. The per-owner durable sequence counter
guarantees distinguishability of repeated identical executions.
Wall-clock is never an identity input.

Granularity: one outcome per ``route_intent`` call (= per node for
flow programs, per intent for single executions). Program-level
aggregation is derivable by grouping on the composition reference.
There is no separate program-level outcome record.

Persistence: the ledger lives in the program payload (execution
evidence -> program authority), serialized by form/persist.serialize,
riding Persistence V2 atomic writes and Checkpoint Generation V1
coherence. Failed save/commit -> previous generation authoritative.
No ``outcomes.json`` sidecar.

Retention: unbounded growth is tolerated (duo_ledger precedent);
a pruning policy is documented as DEFERRED. No destructive pruning
is invented here.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

OUTCOME_VERSION = 1
OUTCOME_ID_PREFIX = "out1:"

# Result vocabulary (unifies flow completed/failed/skipped, arm ok/error,
# router routed/unrouted). Observable result only — never a truth judgment.
RESULT_COMPLETED = "completed"
RESULT_FAILED = "failed"
RESULT_BLOCKED = "blocked"
RESULT_SKIPPED = "skipped"
RESULTS = (RESULT_COMPLETED, RESULT_FAILED, RESULT_BLOCKED, RESULT_SKIPPED)

# Evidence storage budget (GP-E02 / FI-012): records carry evidence
# whole. The budget is a disclosed STORAGE bound, not a content limit:
# a field past the budget refuses the WHOLE capture explicitly —
# build_outcome raises EvidenceOverBudget before any append and
# capture_outcome returns None with nothing stored — instead of the
# old behavior, which silently truncated fields to a prefix and
# silently dropped messages past the count cap.
#
# The budget binds at three levels (Director 7066282827): per field,
# per message count, and per TOTAL record — the sum of every evidence
# field in one record. Per-field/count caps alone would still admit
# 10,000 messages x 100,000 chars (~10^9 chars retained); the total
# cap bounds one record's evidence at _MAX_TOTAL_EVIDENCE chars
# regardless of distribution. The total is audited from field lengths
# BEFORE the record (and its bounded copies) is materialized, so the
# refusal itself allocates nothing proportional to the evidence.
#
# A refused capture is never a silent bare None: capture_outcome
# records a typed CaptureDiagnostic on the program for EVERY attempt
# (see last_capture_diagnostic) distinguishing evidence_over_budget
# from ledger_absent / ledger_invalid / capture_error.
_MAX_INPUT = 100_000
_MAX_ERROR = 100_000
_MAX_MESSAGE = 100_000
_MAX_MESSAGES = 10_000
_MAX_STATE_NOTE = 100_000
_MAX_FLOW_PROGRAM = 100_000
_MAX_TOTAL_EVIDENCE = 1_000_000


class EvidenceOverBudget(ValueError):
    """Evidence exceeds the disclosed storage budget.

    Carries structured provenance (field / length / budget) so the
    refusal is auditable without parsing the message.
    """

    def __init__(self, message: str, *, field: Optional[str] = None,
                 length: Optional[int] = None,
                 budget: Optional[int] = None) -> None:
        super().__init__(message)
        self.field = field
        self.length = length
        self.budget = budget


def _bound(text: Any, limit: int, field: str = "field") -> str:
    s = str(text or "")
    if len(s) > limit:
        raise EvidenceOverBudget(
            f"outcome evidence field {field!r} length {len(s)} exceeds "
            f"storage budget {limit}; capture refused, nothing stored",
            field=field, length=len(s), budget=limit)
    return s


def _content_fingerprint(proposal: Any) -> str:
    """Derivable per-proposal content fingerprint, snapshotted at capture.

    sha256 over the canonical (label|words|revision_number) triple.
    Frozen at capture time; later revision never rewrites the record.
    """
    label = str(getattr(proposal, "label", "") or "")
    words = str(getattr(proposal, "words", "") or "")
    rev = getattr(proposal, "revision_number", 1)
    try:
        rev_n = int(rev)
    except (TypeError, ValueError):
        rev_n = 1
    return hashlib.sha256(f"{label}|{words}|{rev_n}".encode("utf-8")).hexdigest()[:32]


def outcome_id_for(version: int, owner: str, seq: int, operation: str,
                   knowledge_part: str, conflict_part: str,
                   result: str) -> str:
    """Stable outcome identity. Not wall-clock based.

    ``seq`` (the per-owner durable outcome sequence) guarantees that
    repeated identical executions remain distinguishable.
    """
    canonical = (
        f"{version}|{owner}|{seq}|{operation}|"
        f"{knowledge_part}|{conflict_part}|{result}"
    )
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:32]
    return f"{OUTCOME_ID_PREFIX}{digest}"


def _knowledge_snapshot(nurture: Any) -> List[Dict[str, Any]]:
    """Frozen knowledge provenance from the arm's structured receipt.

    ``nurture`` is the ``program.last_nurture`` dict attributed to THIS
    call by the freshness gate (the ``route_intent`` wrapper passes it
    only when the executed call replaced the slot). Callers must pass
    None when the evidence is not fresh; returns [] when knowledge did
    not participate. Each entry snapshots (id, revision_number,
    revision_root_id, lifecycle_state, content_fingerprint) at capture
    time — later revision of the knowledge MUST NOT rewrite this.
    """
    if not isinstance(nurture, dict):
        return []
    details = nurture.get("selected_details") or []
    if not isinstance(details, list):
        return []
    # NOTE: content fingerprints need the nursery; the program is not
    # passed here. Fingerprints are resolved by the caller via
    # _resolve_fingerprints below.
    out: List[Dict[str, Any]] = []
    for d in details:
        if not isinstance(d, dict):
            continue
        uid = str(d.get("id", ""))
        if not uid:
            continue
        try:
            rev_n = int(d.get("revision_number", 1))
        except (TypeError, ValueError):
            rev_n = 1
        out.append({
            "id": uid,
            "revision_number": rev_n,
            "revision_root_id": str(d.get("revision_root_id", uid)),
            "lifecycle_state": str(d.get("lifecycle_state", "active")),
            "content_fingerprint": "",
        })
    return out


def _resolve_fingerprints(program: Any,
                          knowledge: List[Dict[str, Any]]) -> None:
    """Fill content fingerprints in place from the live nursery.

    Fingerprints snapshot proposal content at capture time; later
    revision never rewrites the record (the record keeps its copy).
    """
    proposals = getattr(getattr(program, "nursery", None), "proposals", None) or {}
    for k in knowledge:
        k["content_fingerprint"] = _content_fingerprint(proposals.get(k["id"]))


def _conflict_snapshot(nurture: Any) -> Dict[str, Any]:
    """Frozen conflict/disposition provenance from the arm's receipt.

    ``nurture`` is the ``program.last_nurture`` dict attributed to THIS
    call by the freshness gate. Callers must pass None when the
    evidence is not fresh. Records the routing state that ACTUALLY
    APPLIED at execution time: conflict identity, whether
    unresolved/resolved, disposition applied, policy exclusions. Never
    reinterpreted later.
    """
    empty = {"conflicts": [], "policy_exclusions": [],
             "quarantined_ids": [], "routable_ids": []}
    if not isinstance(nurture, dict):
        return empty
    conflicts: List[Dict[str, Any]] = []
    disps = nurture.get("conflict_dispositions") or []
    if isinstance(disps, list):
        for d in disps:
            if not isinstance(d, dict):
                continue
            conflicts.append({
                "conflict_id": str(d.get("conflict_id", "")),
                "disposition": str(d.get("disposition", "unresolved")),
                "preferred_ids": [str(x) for x in (d.get("preferred_ids") or [])],
                "permitted_ids": [str(x) for x in (d.get("permitted_ids") or [])],
                "participant_ids": [str(x) for x in (d.get("participant_ids") or [])],
                "detected": bool(d.get("detected", False)),
                "disposition_applicable": bool(d.get("disposition_applicable", False)),
            })
    exclusions = nurture.get("conflict_policy_exclusions") or []
    quarantined = nurture.get("quarantined_ids") or []
    routable = nurture.get("routable_selected_ids") or []
    return {
        "conflicts": conflicts,
        "policy_exclusions": [str(x) for x in exclusions] if isinstance(exclusions, list) else [],
        "quarantined_ids": [str(x) for x in quarantined] if isinstance(quarantined, list) else [],
        "routable_ids": [str(x) for x in routable] if isinstance(routable, list) else [],
    }


def _blocked_by_quarantine(nurture: Any, receipt: Any) -> bool:
    """DCC-XX-C1: detect the all-quarantined Dell 37 grow.

    The arm returns ok=True when routing correctly quarantined every
    selected unit — routing succeeded, but the intended execution
    (knowledge-driven growth) did not occur. Recording ``completed``
    would be false evidence. Returns True only for a fresh Dell 37
    ``grow_contextual`` receipt with conflicts detected, zero routable
    IDs, and a non-empty quarantine set. Partial quarantine, empty
    selection, failed arms, and non-grow operations are unaffected.
    """
    if not isinstance(nurture, dict):
        return False
    try:
        if int(getattr(receipt, "dell", -1)) != 37:
            return False
    except (TypeError, ValueError):
        return False
    if nurture.get("action") != "grow_contextual":
        return False
    if not bool(nurture.get("ok")):
        return False
    routable = nurture.get("routable_selected_ids") or []
    quarantined = nurture.get("quarantined_ids") or []
    conflicts = nurture.get("conflicts") or []
    return (len(routable) == 0 and len(quarantined) > 0
            and len(conflicts) > 0)


def _generation_epoch(program: Any) -> Optional[str]:
    """Committed checkpoint generation at capture time (epoch context).

    Best-effort: identifies the state epoch the execution ran against.
    Not an identity input. None when no checkpoint is established.
    """
    try:
        from form.mandell.checkpoint_generation import current_generation_id
        return current_generation_id(program.owner)
    except Exception:
        return None


def _result_of(receipt: Any) -> str:
    """Map a RouteReceipt to the unified observable result vocabulary."""
    routed = bool(getattr(receipt, "routed", False))
    ok = bool(getattr(receipt, "ok", False))
    error = str(getattr(receipt, "error", "") or "").lower()
    if not routed:
        # Nothing executed. Distinguish refused routing (blocked) from
        # explicitly skipped steps.
        if "skip" in error:
            return RESULT_SKIPPED
        return RESULT_BLOCKED
    return RESULT_COMPLETED if ok else RESULT_FAILED


def build_outcome(program: Any, receipt: Any,
                  composition: Optional[Dict[str, Any]] = None,
                  nurture_fresh: bool = False,
                  interaction_id: Optional[str] = None) -> Dict[str, Any]:
    """Construct an Outcome Record V1 from a RouteReceipt (pure).

    Does not mutate the program. All provenance is snapshotted from
    the arm's structured receipt available at the route_intent boundary.
    Contains zero truth/verification/confidence fields by construction.

    ``nurture_fresh`` is set by the ``route_intent`` wrapper: True only
    when the executed call replaced ``program.last_nurture``. When
    False, knowledge/conflict provenance is recorded empty — stale
    evidence from a previous call can never contaminate this outcome.

    ``interaction_id`` (EIC-I): optional explicit correlation to the
    interaction that caused this execution. None = UNKNOWN (legacy or
    non-interactive execution). Never fabricated. Does not imply truth,
    success, causation beyond propagated ancestry, persistence, or ordering.
    """
    owner = str(getattr(program, "owner", "Operator"))
    seq = int(getattr(program, "outcome_seq", 0) or 0) + 1

    operation = str(getattr(receipt, "action", "") or "")
    mandell = str(getattr(receipt, "mandell", "") or "")
    try:
        dell = getattr(receipt, "dell", None)
        dell_n: Optional[int] = int(dell) if dell is not None else None
    except (TypeError, ValueError):
        dell_n = None
    semantic = str(getattr(receipt, "semantic", "") or "")
    result = _result_of(receipt)

    # DAF-02/B5: the ledger is the persistence boundary. A receipt
    # for Dell 41[Sanitize] is stored ONLY in sanitized form —
    # mandell, input, messages, state_note, and error pass through
    # the shared redactor regardless of which capture path built
    # the receipt, so a Sanitize execution can never persist the
    # secret-shaped values it exists to redact.
    _sanitize_receipt = dell_n == 41
    if _sanitize_receipt:
        from .redaction import sanitize_text
        mandell = sanitize_text(mandell)

    # DCC-XX-C1: attribute provenance only to the call that produced
    # it. A stale last_nurture from a previous call is ignored.
    nurture = getattr(program, "last_nurture", None) if nurture_fresh else None
    knowledge = _knowledge_snapshot(nurture)
    _resolve_fingerprints(program, knowledge)
    conflict = _conflict_snapshot(nurture)

    # DCC-XX-C1: an all-quarantined Dell 37 grow did not execute its
    # intended effect; recording completed would be false evidence.
    if result == RESULT_COMPLETED and _blocked_by_quarantine(nurture, receipt):
        result = RESULT_BLOCKED

    knowledge_part = "|".join(
        f"{k['id']}#{k['revision_number']}#{k['content_fingerprint']}"
        for k in knowledge
    )
    conflict_part = "|".join(
        f"{c['conflict_id']}:{c['disposition']}:{','.join(c['permitted_ids'])}"
        for c in conflict["conflicts"]
    )

    outcome_id = outcome_id_for(
        OUTCOME_VERSION, owner, seq, operation,
        knowledge_part, conflict_part, result,
    )

    messages = getattr(receipt, "messages", None) or []
    if not isinstance(messages, list):
        messages = [messages]
    if _sanitize_receipt:
        from .redaction import sanitize_text as _st
        messages = [_st(str(m)) for m in messages]
    if len(messages) > _MAX_MESSAGES:
        raise EvidenceOverBudget(
            f"outcome evidence field 'messages' count {len(messages)} "
            f"exceeds storage budget {_MAX_MESSAGES}; capture refused, "
            f"nothing stored",
            field="messages", length=len(messages), budget=_MAX_MESSAGES)

    # Evidence text fields, hoisted so the total-record budget can be
    # audited from lengths BEFORE the record is materialized. The
    # sanitize/bound treatment below is unchanged: Dell 41 receipts
    # are sanitized first, then every field passes _bound.
    raw_input = getattr(receipt, "input", "")
    raw_error = getattr(receipt, "error", "")
    raw_note = getattr(receipt, "state_note", "")
    if _sanitize_receipt:
        from .redaction import sanitize_text as _stf
        input_text: Any = _stf(str(raw_input or ""))
        error_text: Any = _stf(str(raw_error or ""))
        note_text: Any = _stf(str(raw_note or ""))
    else:
        input_text, error_text, note_text = raw_input, raw_error, raw_note
    flow_text: Any = ""
    if isinstance(composition, dict):
        flow_text = composition.get("flow_program", "")

    def _evidence_len(value: Any) -> int:
        return len(value) if isinstance(value, str) else len(str(value or ""))

    total_evidence = (
        _evidence_len(input_text) + _evidence_len(error_text)
        + _evidence_len(note_text)
        + sum(_evidence_len(m) for m in messages)
        + _evidence_len(flow_text)
    )
    if total_evidence > _MAX_TOTAL_EVIDENCE:
        raise EvidenceOverBudget(
            f"outcome evidence total length {total_evidence} exceeds "
            f"total storage budget {_MAX_TOTAL_EVIDENCE}; capture "
            f"refused, nothing stored",
            field="total", length=total_evidence,
            budget=_MAX_TOTAL_EVIDENCE)

    record: Dict[str, Any] = {
        "outcome_version": OUTCOME_VERSION,
        "outcome_id": outcome_id,
        "outcome_seq": seq,
        "owner": owner,
        "operation": operation,
        "mandell": mandell,
        "dell": dell_n,
        "semantic": semantic,
        "input": _bound(input_text, _MAX_INPUT, "input"),
        "result": result,
        "error": _bound(error_text, _MAX_ERROR, "error"),
        "messages": [_bound(m, _MAX_MESSAGE, "message") for m in messages],
        "state_note": _bound(note_text, _MAX_STATE_NOTE, "state_note"),
        "knowledge": knowledge,
        "conflicts": conflict["conflicts"],
        "policy_exclusions": conflict["policy_exclusions"],
        "quarantined_ids": conflict["quarantined_ids"],
        "routable_ids": conflict["routable_ids"],
        "composition": None,
        "generation_id": _generation_epoch(program),
        # Explicit boundary marker: this record is observation, not truth.
        "outcome_is_observation": True,
        # EIC-I: explicit interaction correlation. None = UNKNOWN.
        # Does not imply truth, success, persistence, or ordering.
        "interaction_id": interaction_id,
        # GDP-001 0.3.4: standardized receipt fields. Optional and
        # backward-compatible: None/[] means the executing path did not
        # supply them. Never fabricated. Read from both RouteReceipt
        # (requested_operation/resolved_operation) and BridgeReceipt
        # (requested_action/resolved_name) naming.
        "requested_operation": (
            getattr(receipt, "requested_operation", None)
            or getattr(receipt, "requested_action", None)
            or getattr(receipt, "action", None)
            or None
        ),
        "resolved_operation": (
            getattr(receipt, "resolved_operation", None)
            or getattr(receipt, "seed", None)
            or getattr(receipt, "resolved_name", None)
            or None
        ),
        "authority": getattr(receipt, "authority", None) or None,
        "affected_objects": list(getattr(receipt, "affected_objects", None) or []),
        "atom_results": [dict(r) for r in (getattr(receipt, "atom_results", None) or [])
                         if isinstance(r, dict)],
        "partial_completion": bool(getattr(receipt, "partial", False)),
    }
    if composition is not None and isinstance(composition, dict):
        record["composition"] = {
            "flow_program": _bound(composition.get("flow_program", ""), _MAX_FLOW_PROGRAM, "flow_program"),
            "node_index": int(composition.get("node_index", 0) or 0),
        }
    return record


# Capture diagnostic vocabulary (GP-E02 correction, Director
# 7066282827). A capture attempt ends exactly one of two ways:
# captured, or capture_unavailable with one of these typed reasons.
# The reasons are mutually distinguishable — an over-budget refusal
# can never be mistaken for a missing ledger, and vice versa.
CAPTURED = "captured"
CAPTURE_UNAVAILABLE = "capture_unavailable"
REASON_EVIDENCE_OVER_BUDGET = "evidence_over_budget"
REASON_LEDGER_ABSENT = "ledger_absent"
REASON_LEDGER_INVALID = "ledger_invalid"
REASON_CAPTURE_ERROR = "capture_error"


@dataclass(frozen=True)
class CaptureDiagnostic:
    """Typed outcome of one capture_outcome attempt.

    ``status`` is CAPTURED (``reason`` None, ``outcome_id`` set) or
    CAPTURE_UNAVAILABLE (``reason`` one of the REASON_* constants;
    for evidence_over_budget, ``field``/``length``/``budget`` carry
    the refusal provenance). Observation only — never a truth claim.
    """

    status: str
    reason: Optional[str] = None
    detail: str = ""
    field: Optional[str] = None
    length: Optional[int] = None
    budget: Optional[int] = None
    outcome_id: Optional[str] = None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "reason": self.reason,
            "detail": self.detail,
            "field": self.field,
            "length": self.length,
            "budget": self.budget,
            "outcome_id": self.outcome_id,
        }


def last_capture_diagnostic(program: Any) -> Optional[Dict[str, Any]]:
    """The typed diagnostic of the most recent capture attempt.

    This is the disclosed surface a consumer reads to distinguish
    "the latest execution was captured" (status captured, outcome_id
    set) from "its outcome is unavailable, and why" (status
    capture_unavailable + reason). Returns None only when no capture
    has been attempted on this program through capture_outcome.
    """
    diag = getattr(program, "last_capture_diagnostic", None)
    if isinstance(diag, CaptureDiagnostic):
        return diag.as_dict()
    if isinstance(diag, dict):
        return dict(diag)
    return None


def _store_capture_diagnostic(program: Any,
                              diagnostic: CaptureDiagnostic) -> None:
    try:
        program.last_capture_diagnostic = diagnostic
    except Exception:
        pass


def capture_outcome(program: Any, receipt: Any,
                    composition: Optional[Dict[str, Any]] = None,
                    nurture_fresh: bool = False,
                    interaction_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Capture an Outcome Record V1 into the program's ledger.

    Called once per route_intent call, after the RouteReceipt is built.
    Post-hoc observation only: never raises, never alters routing, never
    mutates knowledge truth, verification, disposition, revision, or
    dependency authority. Returns the record, or None if the program
    cannot host a ledger.

    A None return is never silent: EVERY attempt records a typed
    CaptureDiagnostic on the program (read it via
    last_capture_diagnostic) distinguishing evidence_over_budget from
    ledger_absent / ledger_invalid / capture_error. The observed
    routing action is never vetoed by a refusal — the refusal is
    reported, not raised.

    ``nurture_fresh`` (from the route_intent wrapper) gates provenance
    attribution: only a receipt slot replaced by THIS call is read.

    ``interaction_id`` (EIC-I): optional explicit correlation.
    None = UNKNOWN.
    """
    record: Optional[Dict[str, Any]] = None
    diagnostic: Optional[CaptureDiagnostic] = None
    try:
        records = getattr(program, "outcome_records", None)
        if records is None:
            diagnostic = CaptureDiagnostic(
                status=CAPTURE_UNAVAILABLE, reason=REASON_LEDGER_ABSENT,
                detail="program has no outcome_records ledger")
        elif not isinstance(records, dict):
            diagnostic = CaptureDiagnostic(
                status=CAPTURE_UNAVAILABLE, reason=REASON_LEDGER_INVALID,
                detail="program outcome_records is not a dict")
        else:
            try:
                record = build_outcome(program, receipt, composition,
                                       nurture_fresh=nurture_fresh,
                                       interaction_id=interaction_id)
            except EvidenceOverBudget as exc:
                diagnostic = CaptureDiagnostic(
                    status=CAPTURE_UNAVAILABLE,
                    reason=REASON_EVIDENCE_OVER_BUDGET,
                    detail=str(exc), field=exc.field,
                    length=exc.length, budget=exc.budget)
            except Exception as exc:  # observer contract: never raise
                diagnostic = CaptureDiagnostic(
                    status=CAPTURE_UNAVAILABLE,
                    reason=REASON_CAPTURE_ERROR,
                    detail=f"{type(exc).__name__}: {exc}"[:300])
            if record is not None:
                # Deterministic: the sequence counter advances exactly
                # once per captured outcome, in the same step as the
                # append.
                program.outcome_seq = int(record["outcome_seq"])
                records[record["outcome_id"]] = record
                program.last_outcome = record
                diagnostic = CaptureDiagnostic(
                    status=CAPTURED, outcome_id=record["outcome_id"])
    except Exception as exc:  # observer contract: never raise
        record = None
        diagnostic = CaptureDiagnostic(
            status=CAPTURE_UNAVAILABLE, reason=REASON_CAPTURE_ERROR,
            detail=f"{type(exc).__name__}: {exc}"[:300])
    if diagnostic is not None:
        _store_capture_diagnostic(program, diagnostic)
    return record


def get_outcome(program: Any, outcome_id: str) -> Optional[Dict[str, Any]]:
    """Exact lookup of one outcome by its stable ID."""
    records = getattr(program, "outcome_records", None) or {}
    rec = records.get(str(outcome_id))
    return dict(rec) if isinstance(rec, dict) else None


def get_outcome_by_seq(program: Any, seq: int) -> Optional[Dict[str, Any]]:
    """Lookup one outcome by its sequence number (COO-I).

    Seq is stable within persisted owner state. Suitable for user-facing
    selection (friendlier than UUID). Returns None if not found.
    """
    records = getattr(program, "outcome_records", None) or {}
    try:
        target = int(seq)
    except (TypeError, ValueError):
        return None
    for rec in records.values():
        if isinstance(rec, dict) and int(rec.get("outcome_seq", -1) or -1) == target:
            return dict(rec)
    return None


def find_outcomes(program: Any, query: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Deterministic literal substring search over Outcome input/Mandell (COO-I).

    Case-insensitive. Searches input, mandell, operation, semantic.
    No fuzzy/semantic matching. Returns newest first by outcome_seq.
    """
    records = getattr(program, "outcome_records", None) or {}
    ql = str(query or "").lower().strip()
    if not ql:
        return []
    out = []
    for rec in records.values():
        if not isinstance(rec, dict):
            continue
        haystack = " ".join([
            str(rec.get("input") or ""),
            str(rec.get("mandell") or ""),
            str(rec.get("operation") or ""),
            str(rec.get("semantic") or ""),
        ]).lower()
        if ql in haystack:
            out.append(dict(rec))
    out.sort(key=lambda r: int(r.get("outcome_seq", 0) or 0), reverse=True)
    try:
        # GP-E02: the caller's limit is honored exactly — the old
        # silent clamp to 100 hid matches the caller asked for.
        n = max(1, int(limit))
    except (TypeError, ValueError):
        n = 20
    return out[:n]


def list_outcomes(program: Any, limit: int = 10) -> List[Dict[str, Any]]:
    """Most recent outcomes, newest first (by outcome_seq)."""
    records = getattr(program, "outcome_records", None) or {}
    recs = [r for r in records.values() if isinstance(r, dict)]
    recs.sort(key=lambda r: int(r.get("outcome_seq", 0) or 0), reverse=True)
    try:
        n = max(1, int(limit))
    except (TypeError, ValueError):
        n = 10
    return [dict(r) for r in recs[:n]]


def outcomes_for_knowledge(program: Any, knowledge_id: str) -> List[Dict[str, Any]]:
    """All outcomes whose knowledge provenance includes a knowledge ID.

    Matches the exact unit ID and any revision root sharing that ID:
    historical records keep the revision that participated at capture.
    """
    records = getattr(program, "outcome_records", None) or {}
    kid = str(knowledge_id)
    out = []
    for rec in records.values():
        if not isinstance(rec, dict):
            continue
        for k in rec.get("knowledge") or []:
            if not isinstance(k, dict):
                continue
            if k.get("id") == kid or k.get("revision_root_id") == kid:
                out.append(dict(rec))
                break
    out.sort(key=lambda r: int(r.get("outcome_seq", 0) or 0))
    return out


def outcomes_for_interaction(program: Any, interaction_id: str) -> List[Dict[str, Any]]:
    """All outcomes explicitly correlated to an interaction ID (EIC-I/DIVG-I).

    Read-only. Returns outcomes where interaction_id matches exactly.
    Empty list if none (including legacy UNKNOWN outcomes).
    Sorted by outcome_seq ascending (chronological).
    """
    records = getattr(program, "outcome_records", None) or {}
    iid = str(interaction_id or "")
    if not iid:
        return []
    out = [dict(r) for r in records.values()
           if isinstance(r, dict) and r.get("interaction_id") == iid]
    out.sort(key=lambda r: int(r.get("outcome_seq", 0) or 0))
    return out


def validate_record_shape(rec: Dict[str, Any]) -> bool:
    """Shape check for a persisted outcome record (load-time guard)."""
    if not isinstance(rec, dict):
        return False
    if rec.get("outcome_version") != OUTCOME_VERSION:
        return False
    oid = rec.get("outcome_id")
    if not isinstance(oid, str) or not oid.startswith(OUTCOME_ID_PREFIX):
        return False
    if rec.get("result") not in RESULTS:
        return False
    # OUTCOME != TRUTH: a persisted record must never carry truth claims.
    for forbidden in ("truth", "verified", "verification", "confidence",
                      "truth_score", "auto_confirm", "auto_reject"):
        if forbidden in rec:
            return False
    return True
