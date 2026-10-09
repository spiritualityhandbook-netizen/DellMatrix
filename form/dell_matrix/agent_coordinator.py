"""R6.4 trusted host coordinator for multi-agent shared state.

GDP_PHASE_6_R64_MULTI_INTELLIGENCE_SHARED_STATE_CIRCUIT (MODE=C).

One trusted host coordinator serializes protected mutations for multiple
logical agents cooperating over one knowledge system. Identity, permission,
memory, and outcomes stay separate per agent.

Architecture (per directive §2):
- ONE HostCoordinator per program/owner. All accepted-state writes are
  serialized through it. No distributed consensus, no concurrent-writer
  safety, no malicious in-process Python protection is claimed.
- Agent identity is HOST-BOUND (registered by trusted code), never taken
  from an agent payload.
- Agents receive bounded DETACHED snapshots (read-only dicts) and narrow
  request interfaces. They never receive mutable Program/Nursery objects,
  policy controllers, or credentials belonging to another agent.
- BIMO slots / personas are DESCRIPTIVE behavior metadata. They never
  mint, inherit, or combine authority.
- Permission decisions are owned by AcceptancePolicy; the coordinator
  delegates. R6.1 agent_confirm is the canonical writer path.
- R6.3 rollback mediation (check_save_allowed, rollback epochs) is reused
  for recovery-required and stale-writer invalidation.

Request lifecycle:
    register_agent (trusted) -> AgentIdentity
    snapshot_for(subject)     -> detached read-only dict
    enqueue(subject, envelope) -> queued_id   (shape/bounds validated)
    dispatch(queued_id, grant_handle) -> receipt  (authority, freshness,
        recovery-required, and epoch revalidated AT EXECUTION)

A queued request is NOT prior authorization to commit. Revocation,
changed content, recovery-required state, and rollback invalidation
still take effect at dispatch.

Repeated-request behavior (directive §3):
- exact retry (same request_id + same content evidence) -> same receipt,
  no duplicate transition.
- reused request_id with different content -> REJECT.
- interrupted/unknown outcome -> status "unknown", never "completed".

Audit (directive §5): every enqueue/dispatch/deny is recorded in the
program-payload agent_audit section (see capture_agent_action). Records
carry bound subject, request correlation, operation, affected objects,
result, and provenance. Grant handles and credentials are NEVER logged.
Statuses: attempted, denied, committed, failed, incomplete_recovery.
"""

from __future__ import annotations

import copy
import hashlib
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Constants and bounds
# ---------------------------------------------------------------------------

AGENT_AUDIT_VERSION = 1
AUDIT_ID_PREFIX = "aa1:"

_MAX_SUBJECT = 200
_MAX_REQUEST_ID = 128
_MAX_OPERATION = 64
_MAX_TARGET = 256
_MAX_CORRELATION = 512
_MAX_PERSONA_SLOTS = 16
_MAX_QUEUE = 64
_MAX_SNAPSHOT_IDEAS = 200
_MAX_SNAPSHOT_UNITS = 200
_MAX_AUDIT_RECORDS = 500

OPERATIONS = ("confirm",)

# Audit result vocabulary. Observable result only.
AUDIT_ATTEMPTED = "attempted"
AUDIT_DENIED = "denied"
AUDIT_COMMITTED = "committed"
AUDIT_FAILED = "failed"
AUDIT_INCOMPLETE = "incomplete_recovery"
AUDIT_RESULTS = (AUDIT_ATTEMPTED, AUDIT_DENIED, AUDIT_COMMITTED,
                 AUDIT_FAILED, AUDIT_INCOMPLETE)


def _bound(text: Any, limit: int) -> str:
    s = str(text or "")
    return s[:limit]


def _utcnow() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


# ---------------------------------------------------------------------------
# Agent identity (host-bound)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AgentIdentity:
    """Host-bound agent identity record.

    Created ONLY by HostCoordinator.register_agent (trusted host path).
    persona_slots and bimo_binding are DESCRIPTIVE behavior metadata;
    they are never consulted for permission decisions.
    """
    subject: str
    owner: str
    persona_slots: Dict[str, str] = field(default_factory=dict)
    bimo_binding: Dict[str, str] = field(default_factory=dict)
    registered_at: str = ""


def _validate_subject(subject: Any) -> str:
    if not isinstance(subject, str) or not subject:
        raise ValueError("subject must be non-empty str")
    if len(subject) > _MAX_SUBJECT:
        raise ValueError("subject exceeds bound")
    return subject


# ---------------------------------------------------------------------------
# Typed request envelope
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RequestEnvelope:
    """Typed agent request. Identity is NOT in the envelope.

    The subject is supplied separately by the host binding at enqueue
    time; a caller-supplied subject field is rejected.
    """
    request_id: str
    operation: str
    target: str
    expected: Dict[str, Any]      # content/state evidence at request time
    correlation: Dict[str, Any]   # parent_request, session, note


def make_envelope(*, request_id: str, operation: str, target: str,
                  expected: Optional[Dict[str, Any]] = None,
                  correlation: Optional[Dict[str, Any]] = None) -> RequestEnvelope:
    """Build a validated envelope. Raises ValueError on shape violations."""
    if not isinstance(request_id, str) or not request_id:
        raise ValueError("request_id must be non-empty str")
    if len(request_id) > _MAX_REQUEST_ID:
        raise ValueError("request_id exceeds bound")
    if operation not in OPERATIONS:
        raise ValueError(f"unsupported operation: {operation!r}")
    if not isinstance(target, str) or not target:
        raise ValueError("target must be non-empty str")
    if len(target) > _MAX_TARGET:
        raise ValueError("target exceeds bound")
    expected = dict(expected or {})
    correlation = dict(correlation or {})
    if len(str(correlation)) > _MAX_CORRELATION:
        raise ValueError("correlation exceeds bound")
    # Identity fields are forbidden in the envelope: the host binding is
    # the only identity source.
    for forbidden in ("subject", "agent", "producer", "_subject",
                      "grant_id", "grant_handle", "credential", "password"):
        if forbidden in expected or forbidden in correlation:
            raise ValueError(f"envelope must not carry identity/credential field: {forbidden}")
    return RequestEnvelope(request_id=request_id, operation=operation,
                           target=target, expected=expected,
                           correlation=correlation)


# ---------------------------------------------------------------------------
# Agent audit (structured outcome capture, program-payload backed)
# ---------------------------------------------------------------------------

def _audit_id_for(owner: str, seq: int, request_id: str,
                  operation: str, result: str) -> str:
    canonical = "|".join([str(AGENT_AUDIT_VERSION), owner, str(seq),
                          request_id, operation, result])
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:32]
    return AUDIT_ID_PREFIX + digest


def capture_agent_action(program: Any, *, subject: str, request_id: str,
                         operation: str, target: str, result: str,
                         correlation: Optional[Dict[str, Any]] = None,
                         affected: Optional[List[str]] = None,
                         provenance: Optional[Dict[str, Any]] = None,
                         detail: str = "") -> Optional[Dict[str, Any]]:
    """Record one agent-action audit record into the program payload.

    Post-hoc observation: never raises, never alters dispatch behavior.
    Grant handles and credentials are NEVER logged (callers must not pass
    them; this function drops any such keys defensively).
    """
    try:
        records = getattr(program, "agent_audit_records", None)
        if records is None or not isinstance(records, dict):
            return None
        if result not in AUDIT_RESULTS:
            result = AUDIT_FAILED
        seq = int(getattr(program, "agent_audit_seq", 0) or 0) + 1
        owner = str(getattr(program, "owner", "") or "")

        def _scrub(obj: Any) -> Any:
            if isinstance(obj, dict):
                return {k: _scrub(v) for k, v in obj.items()
                        if "grant" not in str(k).lower()
                        and "credential" not in str(k).lower()
                        and "password" not in str(k).lower()
                        and "secret" not in str(k).lower()}
            if isinstance(obj, list):
                return [_scrub(v) for v in obj[:32]]
            return obj

        record = {
            "audit_id": _audit_id_for(owner, seq, request_id, operation, result),
            "audit_version": AGENT_AUDIT_VERSION,
            "audit_seq": seq,
            "owner": owner,
            "subject": _bound(subject, _MAX_SUBJECT),
            "request_id": _bound(request_id, _MAX_REQUEST_ID),
            "operation": _bound(operation, _MAX_OPERATION),
            "target": _bound(target, _MAX_TARGET),
            "result": result,
            "correlation": _scrub(dict(correlation or {})),
            "affected": [_bound(a, _MAX_TARGET) for a in (affected or [])[:16]],
            "provenance": _scrub(dict(provenance or {})),
            "detail": _bound(detail, 300),
            "ts": _utcnow(),
        }
        program.agent_audit_seq = seq
        records[record["audit_id"]] = record
        # Bound the in-memory map; persistence bounds separately.
        while len(records) > _MAX_AUDIT_RECORDS:
            oldest = min(records.values(), key=lambda r: r["audit_seq"])
            del records[oldest["audit_id"]]
        program.last_agent_audit = record
        return record
    except Exception:
        return None


def list_agent_audit(program: Any, limit: int = 50) -> List[Dict[str, Any]]:
    records = getattr(program, "agent_audit_records", None) or {}
    ordered = sorted(records.values(), key=lambda r: r.get("audit_seq", 0))
    return ordered[-limit:]


# ---------------------------------------------------------------------------
# Host coordinator
# ---------------------------------------------------------------------------

class CoordinatorError(Exception):
    """Explicit coordinator rejection (not a crash)."""


class HostCoordinator:
    """One trusted host coordinator per program/owner.

    Serializes protected multi-agent mutations. Constructed by the
    trusted host with the live Program; agents never construct one.
    """

    def __init__(self, program: Any, *, queue_bound: int = _MAX_QUEUE):
        self._program = program
        self._owner = str(getattr(program, "owner", "") or "")
        self._agents: Dict[str, AgentIdentity] = {}
        self._queue: Dict[str, Dict[str, Any]] = {}
        self._receipts: Dict[str, Dict[str, Any]] = {}
        self._in_dispatch = False
        self._queue_bound = int(queue_bound) if queue_bound else _MAX_QUEUE

    # -- registration (trusted host only) --------------------------------

    def register_agent(self, trusted_subject: str, *,
                       persona_slots: Optional[Dict[str, str]] = None,
                       bimo_binding: Optional[Dict[str, str]] = None) -> AgentIdentity:
        """Register an agent identity. TRUSTED HOST ONLY.

        `trusted_subject` is established by the host (e.g. the agent
        framework's authenticated identity), never by agent payload text.
        persona_slots/bimo_binding are descriptive behavior metadata.
        """
        subject = _validate_subject(trusted_subject)
        slots = dict(persona_slots or {})
        if len(slots) > _MAX_PERSONA_SLOTS:
            raise ValueError("persona_slots exceeds bound")
        binding = dict(bimo_binding or {})
        ident = AgentIdentity(subject=subject, owner=self._owner,
                              persona_slots={str(k): str(v) for k, v in slots.items()},
                              bimo_binding={str(k): str(v) for k, v in binding.items()},
                              registered_at=_utcnow())
        self._agents[subject] = ident
        return ident

    def agent_identity(self, subject: str) -> Optional[AgentIdentity]:
        return self._agents.get(subject)

    # -- snapshots (bounded, detached) ------------------------------------

    def snapshot_for(self, subject: str) -> Dict[str, Any]:
        """Return a bounded DETACHED snapshot for an agent.

        Read-only plain dicts/lists. Mutating the snapshot never affects
        live state or another agent's snapshot. Does NOT include mutable
        Program/Nursery objects, policy controllers, or credentials.
        """
        _validate_subject(subject)
        if subject not in self._agents:
            raise CoordinatorError(f"unknown agent subject: {subject}")
        program = self._program
        ideas: List[Dict[str, Any]] = []
        nursery = getattr(program, "nursery", None)
        proposals = getattr(nursery, "proposals", None) or {}
        for pid, prop in list(proposals.items())[:_MAX_SNAPSHOT_IDEAS]:
            ideas.append({
                "pid": str(pid),
                "label": str(getattr(prop, "label", "") or ""),
                "words": str(getattr(prop, "words", "") or ""),
                "status": str(getattr(prop, "status", "") or ""),
                "revision_number": int(getattr(prop, "revision_number", 1) or 1),
            })
        units: List[Dict[str, Any]] = []
        plane = getattr(getattr(program, "cube", None), "session", None)
        plane = getattr(plane, "plane", None) if plane is not None else None
        if plane is not None:
            for uid, u in list(getattr(plane, "units", {}).items())[:_MAX_SNAPSHOT_UNITS]:
                units.append({
                    "uid": str(uid),
                    "label": str(getattr(u, "label", "") or ""),
                    "words": str(getattr(u, "words", "") or ""),
                    "x": getattr(u, "x", 0),
                    "y": getattr(u, "y", 0),
                })
        return {
            "subject": subject,
            "owner": self._owner,
            "ideas": copy.deepcopy(ideas),
            "units": copy.deepcopy(units),
            "detached": True,
        }

    # -- enqueue -----------------------------------------------------------

    def enqueue(self, subject: str, envelope: RequestEnvelope) -> str:
        """Validate and queue a request. Returns queued_id.

        Identity comes from the host binding (the `subject` argument),
        not from the envelope. Shape and bounds are validated here;
        authority, freshness, recovery-required, and epoch are validated
        AT DISPATCH (a queued request is not prior authorization).
        """
        _validate_subject(subject)
        if subject not in self._agents:
            raise CoordinatorError(f"unknown agent subject: {subject}")
        if not isinstance(envelope, RequestEnvelope):
            raise CoordinatorError("envelope must be a RequestEnvelope")
        if len(self._queue) >= self._queue_bound:
            raise CoordinatorError("coordinator queue full")
        # Capture execution-time evidence baseline: content hash and
        # rollback epoch at enqueue; dispatch revalidates both.
        program = self._program
        try:
            content_now = program.acceptance_data_hash(envelope.target, envelope.operation)
        except Exception:
            content_now = ""
        epoch_now = self._rollback_epoch()
        queued_id = "q:" + uuid.uuid4().hex[:16]
        self._queue[queued_id] = {
            "queued_id": queued_id,
            "subject": subject,
            "envelope": envelope,
            "content_at_enqueue": content_now,
            "epoch_at_enqueue": epoch_now,
            "enqueued_at": _utcnow(),
        }
        capture_agent_action(program, subject=subject,
                             request_id=envelope.request_id,
                             operation=envelope.operation,
                             target=envelope.target, result=AUDIT_ATTEMPTED,
                             correlation=envelope.correlation,
                             detail="enqueued")
        return queued_id

    # -- dispatch ----------------------------------------------------------

    def dispatch(self, queued_id: str, grant_handle: str) -> Dict[str, Any]:
        """Execute or deny a queued request. Serialized; non-reentrant.

        Revalidates at execution: idempotency, authority (grant via
        AcceptancePolicy through the canonical writer), freshness
        (content hash), rollback epoch, and recovery-required state.
        Returns a receipt dict (never raises for denials).
        """
        if self._in_dispatch:
            return self._deny_receipt(
                None, None, "reentrant_dispatch",
                "Concurrent/reentrant dispatch is rejected explicitly; "
                "protected writes are serialized.")
        queued = self._queue.get(queued_id)
        if queued is None:
            return self._deny_receipt(None, None, "unknown_queued_id",
                                      f"No such queued request: {queued_id!r}.")
        subject = queued["subject"]
        envelope: RequestEnvelope = queued["envelope"]
        program = self._program

        # Idempotency: exact retry returns the cached receipt; reused
        # request_id with different content rejects.
        prior = self._receipts.get(envelope.request_id)
        if prior is not None:
            if prior.get("content_evidence") == self._content_evidence_of(envelope):
                capture_agent_action(
                    program, subject=subject, request_id=envelope.request_id,
                    operation=envelope.operation, target=envelope.target,
                    result=prior["result"], correlation=envelope.correlation,
                    affected=prior.get("affected", []),
                    detail="idempotent retry: cached receipt returned, no duplicate transition")
                return dict(prior, idempotent_retry=True)
            receipt = self._deny_receipt(
                subject, envelope, "request_id_reuse",
                "request_id reused with different content evidence; rejected.")
            self._receipts[envelope.request_id + ":conflict"] = receipt
            return receipt

        self._in_dispatch = True
        try:
            # Recovery-required: stale-save protection (R6.3).
            try:
                from form.mandell.core_i_recovery import check_save_allowed
                check_save_allowed(program, "agent dispatch")
            except Exception as e:
                return self._finalize_denial(
                    subject, envelope, "recovery_required",
                    f"Recovery-required state blocks dispatch: {e}")

            # Rollback epoch: a rollback between enqueue and dispatch
            # invalidates the queued request.
            if self._rollback_epoch() != queued["epoch_at_enqueue"]:
                return self._finalize_denial(
                    subject, envelope, "stale_after_rollback",
                    "Rollback epoch advanced after enqueue; queued request invalidated.")

            # Freshness: content must match the enqueue-time evidence and
            # any caller-supplied expected evidence.
            try:
                content_now = program.acceptance_data_hash(
                    envelope.target, envelope.operation)
            except Exception:
                content_now = ""
            expected = envelope.expected.get("content_hash")
            if expected and expected != content_now:
                return self._finalize_denial(
                    subject, envelope, "content_changed",
                    "Target content changed since the request was prepared; denied.")
            if content_now != queued["content_at_enqueue"]:
                return self._finalize_denial(
                    subject, envelope, "content_changed",
                    "Target content changed between enqueue and dispatch; denied.")

            # Authority: delegate to the canonical R6.1 writer path.
            # The grant is checked by AcceptancePolicy inside
            # confirm_proposal; the coordinator never mints authority.
            from form.dell_matrix import agent_authority as aa
            writer_receipt = aa.agent_confirm(
                program, envelope.target, grant_handle, subject)

            if not isinstance(writer_receipt, dict) or not writer_receipt.get("ok"):
                reason = (writer_receipt or {}).get("reason", "writer_denied")
                detail = (writer_receipt or {}).get("detail", "")
                return self._finalize_denial(
                    subject, envelope, f"writer_{reason}",
                    f"Canonical writer denied: {detail}" if detail else
                    "Canonical writer denied.")

            # Committed.
            receipt = {
                "ok": True,
                "result": AUDIT_COMMITTED,
                "request_id": envelope.request_id,
                "queued_id": queued_id,
                "subject": subject,
                "operation": envelope.operation,
                "target": envelope.target,
                "correlation": dict(envelope.correlation),
                "content_evidence": self._content_evidence_of(envelope, content_now),
                "affected": [envelope.target],
                "writer_receipt": {
                    k: v for k, v in writer_receipt.items()
                    if "grant" not in str(k).lower()
                },
                "ts": _utcnow(),
            }
            self._receipts[envelope.request_id] = receipt
            self._queue.pop(queued_id, None)
            capture_agent_action(
                program, subject=subject, request_id=envelope.request_id,
                operation=envelope.operation, target=envelope.target,
                result=AUDIT_COMMITTED, correlation=envelope.correlation,
                affected=[envelope.target],
                provenance={"writer_ok": True},
                detail="committed via canonical writer")
            return dict(receipt)
        finally:
            self._in_dispatch = False

    # -- internals ----------------------------------------------------------

    def _rollback_epoch(self) -> int:
        try:
            from form.mandell import core_i_recovery as rec
            key = rec._epoch_key(self._owner)
            return int(rec._rollback_epochs.get(key, 0))
        except Exception:
            return 0

    def _content_evidence_of(self, envelope: RequestEnvelope,
                             content_now: str = "") -> Dict[str, Any]:
        return {
            "target": envelope.target,
            "operation": envelope.operation,
            "content_hash": content_now or envelope.expected.get("content_hash", ""),
        }

    def _deny_receipt(self, subject: Optional[str],
                      envelope: Optional[RequestEnvelope],
                      reason: str, detail: str) -> Dict[str, Any]:
        return {
            "ok": False,
            "result": AUDIT_DENIED,
            "request_id": envelope.request_id if envelope else "",
            "subject": subject or "",
            "operation": envelope.operation if envelope else "",
            "target": envelope.target if envelope else "",
            "reason": reason,
            "detail": _bound(detail, 300),
            "ts": _utcnow(),
        }

    def _finalize_denial(self, subject: str, envelope: RequestEnvelope,
                         reason: str, detail: str) -> Dict[str, Any]:
        receipt = self._deny_receipt(subject, envelope, reason, detail)
        self._receipts[envelope.request_id] = receipt
        self._queue.pop(self._queued_id_of(envelope), None)
        capture_agent_action(
            self._program, subject=subject, request_id=envelope.request_id,
            operation=envelope.operation, target=envelope.target,
            result=AUDIT_DENIED, correlation=envelope.correlation,
            detail=f"{reason}: {detail}"[:300])
        return receipt

    def _queued_id_of(self, envelope: RequestEnvelope) -> Optional[str]:
        for qid, q in self._queue.items():
            if q["envelope"] is envelope:
                return qid
        return None

    # -- agent-facing narrow surface ---------------------------------------

    def surface_for(self, subject: str) -> "AgentRequestSurface":
        """Return the narrow agent-facing interface for a registered agent."""
        _validate_subject(subject)
        if subject not in self._agents:
            raise CoordinatorError(f"unknown agent subject: {subject}")
        return AgentRequestSurface(self, subject)


class AgentRequestSurface:
    """Narrow agent-facing request interface.

    Created ONLY by HostCoordinator.surface_for for a registered agent.
    Exposes exactly: snapshot() and request_confirm(). No subject,
    producer, grant-minting, or program access. The subject is the
    host binding, never a request parameter.
    """

    __slots__ = ("_coordinator", "_subject")

    def __init__(self, coordinator: HostCoordinator, subject: str):
        object.__setattr__(self, "_coordinator", coordinator)
        object.__setattr__(self, "_subject", subject)

    @property
    def bound_subject(self) -> str:
        return self._subject

    def snapshot(self) -> Dict[str, Any]:
        """Bounded detached snapshot (read-only)."""
        return self._coordinator.snapshot_for(self._subject)

    def request_confirm(self, pid: str, grant_handle: str, *,
                        request_id: Optional[str] = None,
                        expected_content_hash: Optional[str] = None,
                        correlation: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Request a confirm through the coordinator.

        Only pid and the grant handle cross the boundary (plus
        request-scoped metadata). The coordinator validates, queues,
        and dispatches; the receipt reports the outcome.
        """
        if not isinstance(pid, str) or not pid:
            return {"ok": False, "result": AUDIT_DENIED,
                    "reason": "bad_target",
                    "detail": "pid must be non-empty str."}
        if not isinstance(grant_handle, str) or not grant_handle:
            return {"ok": False, "result": AUDIT_DENIED,
                    "reason": "bad_grant_handle",
                    "detail": "grant handle must be non-empty str."}
        rid = request_id or ("r:" + uuid.uuid4().hex[:16])
        expected: Dict[str, Any] = {}
        if expected_content_hash:
            expected["content_hash"] = expected_content_hash
        try:
            envelope = make_envelope(
                request_id=rid, operation="confirm", target=pid,
                expected=expected, correlation=correlation)
        except ValueError as e:
            return {"ok": False, "result": AUDIT_DENIED,
                    "reason": "bad_envelope", "detail": str(e)}
        try:
            queued_id = self._coordinator.enqueue(self._subject, envelope)
        except CoordinatorError as e:
            return {"ok": False, "result": AUDIT_DENIED,
                    "reason": "enqueue_rejected", "detail": str(e)}
        return self._coordinator.dispatch(queued_id, grant_handle)


def new_coordinator(program: Any) -> HostCoordinator:
    """Create the trusted host coordinator for a program. TRUSTED HOST ONLY."""
    return HostCoordinator(program)
