"""R6.4 trusted host coordinator for multi-agent shared state.

GDP_PHASE_6_R64_MULTI_INTELLIGENCE_SHARED_STATE_CIRCUIT (MODE=C).
AMEND: GDP_PHASE_6_R64_CLOSE_IDENTITY_EVIDENCE_AND_PERSISTENCE.

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

Retry identity (AMEND §1): receipts are namespaced by canonical
(owner, host-bound subject, request_id). A canonical detached request
descriptor (operation, target, expected evidence, correlation semantics)
is compared for idempotency. B can never receive A's cached receipt.
Returned receipts are detached deep copies; caller mutation cannot
alter cached evidence. Cached-retry and conflict paths remove their
queued entries. Historical receipts are labeled historical: not new
authorization, execution, or proof of unchanged live state. Receipt
retention is bounded (no durable exactly-once claim).

Secret protection (AMEND §3): recognized handles/credentials are
screened by VALUE using the existing protected-value infrastructure
(form.dell_matrix.inference_dock.protected_values / contains_protected),
not by key name alone. Envelopes carrying protected values are rejected
at the boundary; audit capture defensively redacts. Coverage: canonical
grant-handle format + session-issued values + configured credentials.
No unknown-secret guarantee is claimed.

Outcome contract (AMEND §4): audit capture failure is observable in the
returned outcome (audit_ok flag); incomplete compensation from the
canonical writer is preserved as incomplete_recovery, never ordinary
denial; operation exceptions yield honest failed/unknown, never inferred
noncommit.
"""

from __future__ import annotations

import copy
import hashlib
import math
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Constants and bounds
# ---------------------------------------------------------------------------

AGENT_AUDIT_VERSION = 1
AUDIT_ID_PREFIX = "aa1:"

_MAX_SUBJECT = 200
_MAX_REQUEST_ID = 128
_MAX_OPERATION = 64
_MAX_TARGET = 256
_MAX_PERSONA_SLOTS = 16
_MAX_QUEUE = 64
_MAX_RECEIPTS = 500
_MAX_SNAPSHOT_IDEAS = 200
_MAX_SNAPSHOT_UNITS = 200
_MAX_AUDIT_RECORDS = 500

# Envelope content bounds (AMEND §2): strict, explicit.
_MAX_DEPTH = 4
_MAX_NODES = 64
_MAX_BYTES = 4096
_MAX_STR_LEN = 512

OPERATIONS = ("confirm",)

# Audit result vocabulary. Observable result only.
AUDIT_ATTEMPTED = "attempted"
AUDIT_DENIED = "denied"
AUDIT_COMMITTED = "committed"
AUDIT_FAILED = "failed"
AUDIT_INCOMPLETE = "incomplete_recovery"
AUDIT_RESULTS = (AUDIT_ATTEMPTED, AUDIT_DENIED, AUDIT_COMMITTED,
                 AUDIT_FAILED, AUDIT_INCOMPLETE)

_REDACTED = "[REDACTED]"


def _bound(text: Any, limit: int) -> str:
    s = str(text or "")
    return s[:limit]


def _utcnow() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


# ---------------------------------------------------------------------------
# Strict value validation (AMEND §2)
# ---------------------------------------------------------------------------

class EnvelopeValidationError(ValueError):
    """Malformed request envelope. Fail closed."""


def _is_finite_number(v: Any) -> bool:
    if isinstance(v, bool):
        return False
    if isinstance(v, (int, float)):
        return math.isfinite(v)
    return False


def _validate_strict_value(value: Any, *, depth: int, nodes: List[int],
                            path: str) -> None:
    """Recursively validate a value: strict types, finite numbers,
    depth/node/byte bounds. Raises EnvelopeValidationError.

    Allowed: str (bounded), int/float (finite, not bool), None,
    list/tuple, dict with str keys. No other types.
    """
    nodes[0] += 1
    if nodes[0] > _MAX_NODES:
        raise EnvelopeValidationError(f"{path}: node count exceeds bound")
    if depth > _MAX_DEPTH:
        raise EnvelopeValidationError(f"{path}: depth exceeds bound")
    if value is None:
        return
    if isinstance(value, bool):
        raise EnvelopeValidationError(f"{path}: bool not allowed")
    if isinstance(value, str):
        if len(value) > _MAX_STR_LEN:
            raise EnvelopeValidationError(f"{path}: string exceeds bound")
        return
    if isinstance(value, (int, float)):
        if not math.isfinite(value):
            raise EnvelopeValidationError(f"{path}: non-finite number")
        return
    if isinstance(value, (list, tuple)):
        for i, item in enumerate(value):
            _validate_strict_value(item, depth=depth + 1, nodes=nodes,
                                   path=f"{path}[{i}]")
        return
    if isinstance(value, dict):
        for k, v in value.items():
            if not isinstance(k, str):
                raise EnvelopeValidationError(f"{path}: non-str dict key")
            if len(k) > _MAX_STR_LEN:
                raise EnvelopeValidationError(f"{path}: key exceeds bound")
            _validate_strict_value(v, depth=depth + 1, nodes=nodes,
                                   path=f"{path}.{k}")
        return
    raise EnvelopeValidationError(
        f"{path}: unsupported type {type(value).__name__}")


def _validate_mapping_strict(mapping: Any, name: str) -> Dict[str, Any]:
    """Validate a top-level mapping strictly; return a detached deep copy.

    Explicit None is malformed (not absence) — callers pass {} for empty.
    """
    if mapping is None:
        raise EnvelopeValidationError(f"{name}: explicit null is malformed")
    if not isinstance(mapping, dict):
        raise EnvelopeValidationError(
            f"{name}: expected dict, got {type(mapping).__name__}")
    nodes = [0]
    _validate_strict_value(mapping, depth=0, nodes=nodes, path=name)
    import json as _json
    try:
        size = len(_json.dumps(mapping, default=str))
    except Exception:
        size = _MAX_BYTES + 1
    if size > _MAX_BYTES:
        raise EnvelopeValidationError(f"{name}: byte size exceeds bound")
    return copy.deepcopy(mapping)


def _check_no_protected_values(program: Any, mapping: Dict[str, Any],
                               where: str) -> None:
    """Reject mappings carrying recognized protected values (AMEND §3).

    Scans VALUES (not just keys) using the existing protected-value
    infrastructure. Raises EnvelopeValidationError on detection.
    """
    try:
        from form.dell_matrix.inference_dock import (
            protected_values, contains_protected)
    except Exception:
        return  # infrastructure unavailable; key-name scrub remains below
    protected = protected_values(program)

    def _scan(obj: Any, path: str) -> None:
        if isinstance(obj, str):
            if contains_protected(obj, protected):
                raise EnvelopeValidationError(
                    f"{where}: protected value detected at {path}")
        elif isinstance(obj, dict):
            for k, v in obj.items():
                if contains_protected(str(k), protected):
                    raise EnvelopeValidationError(
                        f"{where}: protected key at {path}.{k}")
                _scan(v, f"{path}.{k}")
        elif isinstance(obj, (list, tuple)):
            for i, v in enumerate(obj):
                _scan(v, f"{path}[{i}]")

    _scan(mapping, where)


def _redact_protected(program: Any, obj: Any) -> Any:
    """Defensively redact recognized protected values (defense in depth)."""
    try:
        from form.dell_matrix.inference_dock import (
            protected_values, contains_protected)
        protected = protected_values(program)
    except Exception:
        protected = frozenset()

    def _redact(o: Any) -> Any:
        if isinstance(o, str):
            try:
                from form.dell_matrix.inference_dock import contains_protected as cp
                if cp(o, protected):
                    return _REDACTED
            except Exception:
                pass
            return o
        if isinstance(o, dict):
            return {k: _redact(v) for k, v in o.items()}
        if isinstance(o, list):
            return [_redact(v) for v in o]
        return o

    return _redact(obj)


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
# Typed request envelope (AMEND §2: one validator, construction + enqueue)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RequestEnvelope:
    """Typed agent request. Identity is NOT in the envelope.

    The subject is supplied separately by the host binding at enqueue
    time; a caller-supplied subject field is rejected. Nested mappings
    are detached (deep-copied) at construction; frozen=True alone does
    not freeze their contents.
    """
    request_id: str
    operation: str
    target: str
    expected: Dict[str, Any]
    correlation: Dict[str, Any]

    def descriptor(self) -> Dict[str, Any]:
        """Canonical detached request descriptor for idempotency comparison.

        Covers operation, target, expected evidence, and correlation with
        defined semantics. Two envelopes are the "same request" iff their
        descriptors are equal.
        """
        return {
            "operation": self.operation,
            "target": self.target,
            "expected": copy.deepcopy(self.expected),
            "correlation": copy.deepcopy(self.correlation),
        }


def _validate_envelope_fields(*, request_id: Any, operation: Any,
                              target: Any, expected: Any,
                              correlation: Any,
                              program: Any = None) -> Tuple[str, str, str, Dict, Dict]:
    """One validator used at construction AND enqueue (AMEND §2)."""
    if not isinstance(request_id, str) or not request_id:
        raise EnvelopeValidationError("request_id must be non-empty str")
    if len(request_id) > _MAX_REQUEST_ID:
        raise EnvelopeValidationError("request_id exceeds bound")
    if not isinstance(operation, str) or operation not in OPERATIONS:
        raise EnvelopeValidationError(f"unsupported operation: {operation!r}")
    if not isinstance(target, str) or not target:
        raise EnvelopeValidationError("target must be non-empty str")
    if len(target) > _MAX_TARGET:
        raise EnvelopeValidationError("target exceeds bound")
    # Strict validation; explicit null is malformed (callers pass {}).
    exp = _validate_mapping_strict(expected, "expected")
    corr = _validate_mapping_strict(correlation, "correlation")
    # Identity/credential fields are forbidden: the host binding is the
    # only identity source.
    for mapping, name in ((exp, "expected"), (corr, "correlation")):
        for forbidden in ("subject", "agent", "producer", "_subject",
                          "grant_id", "grant_handle", "credential",
                          "password", "secret", "token"):
            if forbidden in mapping:
                raise EnvelopeValidationError(
                    f"{name} must not carry identity/credential field: {forbidden}")
    # Value-based secret screening (AMEND §3).
    if program is not None:
        _check_no_protected_values(program, exp, "expected")
        _check_no_protected_values(program, corr, "correlation")
    return request_id, operation, target, exp, corr


def make_envelope(*, request_id: str, operation: str, target: str,
                  expected: Optional[Dict[str, Any]] = None,
                  correlation: Optional[Dict[str, Any]] = None,
                  _program: Any = None) -> RequestEnvelope:
    """Build a validated envelope. Raises EnvelopeValidationError."""
    rid, op, tgt, exp, corr = _validate_envelope_fields(
        request_id=request_id, operation=operation, target=target,
        expected={} if expected is None else expected,
        correlation={} if correlation is None else correlation,
        program=_program)
    return RequestEnvelope(request_id=rid, operation=op, target=tgt,
                           expected=exp, correlation=corr)


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

    Post-hoc observation. Returns the record, or None if capture failed
    (callers must treat None as observable failure, not silent success).
    Recognized protected values are redacted (defense in depth); the
    boundary rejection in _validate_envelope_fields is the primary guard.
    """
    try:
        records = getattr(program, "agent_audit_records", None)
        if records is None or not isinstance(records, dict):
            return None
        if result not in AUDIT_RESULTS:
            result = AUDIT_FAILED
        seq = int(getattr(program, "agent_audit_seq", 0) or 0) + 1
        owner = str(getattr(program, "owner", "") or "")

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
            "correlation": _redact_protected(program, dict(correlation or {})),
            "affected": [_bound(a, _MAX_TARGET) for a in (affected or [])[:16]],
            "provenance": _redact_protected(program, dict(provenance or {})),
            "detail": _bound(_redact_protected(program, detail), 300),
            "ts": _utcnow(),
        }
        program.agent_audit_seq = seq
        records[record["audit_id"]] = record
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
    return [copy.deepcopy(r) for r in ordered[-limit:]]


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

    def __init__(self, program: Any, *, queue_bound: int = _MAX_QUEUE,
                 receipt_bound: int = _MAX_RECEIPTS):
        self._program = program
        self._owner = str(getattr(program, "owner", "") or "")
        self._agents: Dict[str, AgentIdentity] = {}
        self._queue: Dict[str, Dict[str, Any]] = {}
        # Receipt namespace: (owner, subject, request_id) -> receipt.
        # B can never receive A's cached receipt (AMEND §1).
        self._receipts: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
        self._receipt_order: List[Tuple[str, str, str]] = []
        self._in_dispatch = False
        self._queue_bound = int(queue_bound) if queue_bound else _MAX_QUEUE
        self._receipt_bound = int(receipt_bound) if receipt_bound else _MAX_RECEIPTS

    # -- registration (trusted host only) --------------------------------

    def register_agent(self, trusted_subject: str, *,
                       persona_slots: Optional[Dict[str, str]] = None,
                       bimo_binding: Optional[Dict[str, str]] = None) -> AgentIdentity:
        """Register an agent identity. TRUSTED HOST ONLY."""
        subject = _validate_subject(trusted_subject)
        slots = _validate_mapping_strict(
            {} if persona_slots is None else persona_slots, "persona_slots")
        if len(slots) > _MAX_PERSONA_SLOTS:
            raise ValueError("persona_slots exceeds bound")
        binding = _validate_mapping_strict(
            {} if bimo_binding is None else bimo_binding, "bimo_binding")
        ident = AgentIdentity(
            subject=subject, owner=self._owner,
            persona_slots={str(k): str(v) for k, v in slots.items()},
            bimo_binding={str(k): str(v) for k, v in binding.items()},
            registered_at=_utcnow())
        self._agents[subject] = ident
        return ident

    def agent_identity(self, subject: str) -> Optional[AgentIdentity]:
        return self._agents.get(subject)

    def _receipt_key(self, subject: str, request_id: str) -> Tuple[str, str, str]:
        return (self._owner, subject, request_id)

    # -- snapshots (bounded, detached) ------------------------------------

    def snapshot_for(self, subject: str) -> Dict[str, Any]:
        """Return a bounded DETACHED snapshot for an agent."""
        _validate_subject(subject)
        if subject not in self._agents:
            raise CoordinatorError(f"unknown agent subject: {subject}")
        program = self._program
        ideas: List[Dict[str, Any]] = []
        nursery = getattr(program, "nursery", None)
        proposals = getattr(nursery, "proposals", None) or {}
        for pid, prop in list(proposals.items())[:_MAX_SNAPSHOT_IDEAS]:
            label = str(getattr(prop, "label", "") or "")[:_MAX_STR_LEN]
            words = str(getattr(prop, "words", "") or "")[:_MAX_STR_LEN]
            ideas.append({
                "pid": str(pid)[:_MAX_TARGET],
                "label": label,
                "words": words,
                "status": str(getattr(prop, "status", "") or "")[:64],
                "revision_number": int(getattr(prop, "revision_number", 1) or 1),
            })
        units: List[Dict[str, Any]] = []
        plane = getattr(getattr(program, "cube", None), "session", None)
        plane = getattr(plane, "plane", None) if plane is not None else None
        if plane is not None:
            for uid, u in list(getattr(plane, "units", {}).items())[:_MAX_SNAPSHOT_UNITS]:
                units.append({
                    "uid": str(uid)[:_MAX_TARGET],
                    "label": str(getattr(u, "label", "") or "")[:_MAX_STR_LEN],
                    "words": str(getattr(u, "words", "") or "")[:_MAX_STR_LEN],
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

        The SAME validator runs here as at construction (AMEND §2):
        directly constructed malformed envelopes are rejected even if
        make_envelope was bypassed.
        """
        _validate_subject(subject)
        if subject not in self._agents:
            raise CoordinatorError(f"unknown agent subject: {subject}")
        if not isinstance(envelope, RequestEnvelope):
            raise CoordinatorError("envelope must be a RequestEnvelope")
        # Re-validate the envelope's fields (construction may have been
        # bypassed via direct RequestEnvelope(...) instantiation).
        _validate_envelope_fields(
            request_id=envelope.request_id, operation=envelope.operation,
            target=envelope.target, expected=envelope.expected,
            correlation=envelope.correlation, program=self._program)
        if len(self._queue) >= self._queue_bound:
            raise CoordinatorError("coordinator queue full")
        # Fingerprint/epoch computation failures fail closed (AMEND §2).
        try:
            content_now = self._program.acceptance_data_hash(
                envelope.target, envelope.operation)
            if not isinstance(content_now, str):
                raise TypeError("content fingerprint not a str")
        except Exception as e:
            raise CoordinatorError(
                f"fingerprint computation failed closed: {e}")
        try:
            epoch_now = self._rollback_epoch()
        except Exception as e:
            raise CoordinatorError(
                f"epoch computation failed closed: {e}")
        queued_id = "q:" + uuid.uuid4().hex[:16]
        self._queue[queued_id] = {
            "queued_id": queued_id,
            "subject": subject,
            "envelope": envelope,
            "descriptor": envelope.descriptor(),
            "content_at_enqueue": content_now,
            "epoch_at_enqueue": epoch_now,
            "enqueued_at": _utcnow(),
        }
        audit_rec = capture_agent_action(
            self._program, subject=subject, request_id=envelope.request_id,
            operation=envelope.operation, target=envelope.target,
            result=AUDIT_ATTEMPTED, correlation=envelope.correlation,
            detail="enqueued")
        if audit_rec is None:
            # Audit capture failure is observable; the request is still
            # queued but flagged.
            self._queue[queued_id]["audit_ok"] = False
        else:
            self._queue[queued_id]["audit_ok"] = True
        return queued_id

    # -- dispatch ----------------------------------------------------------

    def dispatch(self, queued_id: str, grant_handle: str) -> Dict[str, Any]:
        """Execute or deny a queued request. Serialized; non-reentrant."""
        if self._in_dispatch:
            return self._deny_receipt(
                None, None, "reentrant_dispatch",
                "Concurrent/reentrant dispatch is rejected explicitly; "
                "protected writes are serialized.", audit_ok=True)
        queued = self._queue.get(queued_id)
        if queued is None:
            return self._deny_receipt(None, None, "unknown_queued_id",
                                      f"No such queued request: {queued_id!r}.",
                                      audit_ok=True)
        subject = queued["subject"]
        envelope: RequestEnvelope = queued["envelope"]
        program = self._program
        rkey = self._receipt_key(subject, envelope.request_id)

        # Idempotency (AMEND §1): namespaced by (owner, subject,
        # request_id); canonical descriptor compared. Cached receipts are
        # labeled historical. The queued entry is removed (no leakage).
        prior = self._receipts.get(rkey)
        if prior is not None:
            self._queue.pop(queued_id, None)
            if prior.get("descriptor") == queued["descriptor"]:
                hist = copy.deepcopy(prior["receipt"])
                hist["historical"] = True
                hist["idempotent_retry"] = True
                hist["detail"] = ("Historical receipt: not new authorization, "
                                  "execution, or proof of unchanged live state.")
                self._audit_retry(subject, envelope, hist)
                return hist
            receipt = self._deny_receipt(
                subject, envelope, "request_id_reuse",
                "request_id reused with different request descriptor; rejected.",
                audit_ok=True)
            self._store_receipt(rkey, queued["descriptor"], receipt)
            return copy.deepcopy(receipt)

        self._in_dispatch = True
        try:
            # Recovery-required: stale-save protection (R6.3).
            try:
                from form.mandell.core_i_recovery import check_save_allowed
                check_save_allowed(program, "agent dispatch")
            except Exception as e:
                return self._finalize_denial(
                    subject, envelope, queued_id, rkey, "recovery_required",
                    f"Recovery-required state blocks dispatch: {e}")

            # Rollback epoch.
            if self._rollback_epoch() != queued["epoch_at_enqueue"]:
                return self._finalize_denial(
                    subject, envelope, queued_id, rkey, "stale_after_rollback",
                    "Rollback epoch advanced after enqueue; queued request invalidated.")

            # Freshness.
            try:
                content_now = program.acceptance_data_hash(
                    envelope.target, envelope.operation)
                if not isinstance(content_now, str):
                    raise TypeError("content fingerprint not a str")
            except Exception as e:
                return self._finalize_denial(
                    subject, envelope, queued_id, rkey, "fingerprint_failed",
                    f"Content fingerprint failed closed: {e}")
            expected = envelope.expected.get("content_hash")
            if expected and expected != content_now:
                return self._finalize_denial(
                    subject, envelope, queued_id, rkey, "content_changed",
                    "Target content changed since the request was prepared; denied.")
            if content_now != queued["content_at_enqueue"]:
                return self._finalize_denial(
                    subject, envelope, queued_id, rkey, "content_changed",
                    "Target content changed between enqueue and dispatch; denied.")

            # Authority: canonical R6.1 writer path.
            from form.dell_matrix import agent_authority as aa
            try:
                writer_receipt = aa.agent_confirm(
                    program, envelope.target, grant_handle, subject)
            except Exception as e:
                # Honest failed/unknown; never infer noncommit from exception.
                return self._finalize_failure(
                    subject, envelope, queued_id, rkey,
                    f"Writer raised {type(e).__name__}: {e}")

            if not isinstance(writer_receipt, dict):
                return self._finalize_failure(
                    subject, envelope, queued_id, rkey,
                    "Writer returned non-dict receipt; outcome unknown.")
            if not writer_receipt.get("ok"):
                reason = writer_receipt.get("reason", "writer_denied")
                # Preserve incomplete-compensation details (AMEND §4).
                if reason in ("incomplete_compensation", "incomplete_recovery",
                              "recovery_required"):
                    return self._finalize_incomplete(
                        subject, envelope, queued_id, rkey, reason,
                        writer_receipt)
                detail = writer_receipt.get("detail", "")
                return self._finalize_denial(
                    subject, envelope, queued_id, rkey, f"writer_{reason}",
                    f"Canonical writer denied: {detail}" if detail else
                    "Canonical writer denied.")

            # Committed.
            receipt = {
                "ok": True,
                "result": AUDIT_COMMITTED,
                "historical": False,
                "request_id": envelope.request_id,
                "queued_id": queued_id,
                "subject": subject,
                "operation": envelope.operation,
                "target": envelope.target,
                "correlation": copy.deepcopy(envelope.correlation),
                "content_evidence": {
                    "target": envelope.target,
                    "operation": envelope.operation,
                    "content_hash": content_now,
                },
                "affected": [envelope.target],
                "audit_ok": True,
                "ts": _utcnow(),
            }
            audit_rec = capture_agent_action(
                program, subject=subject, request_id=envelope.request_id,
                operation=envelope.operation, target=envelope.target,
                result=AUDIT_COMMITTED, correlation=envelope.correlation,
                affected=[envelope.target],
                provenance={"writer_ok": True},
                detail="committed via canonical writer")
            if audit_rec is None:
                # Committed but audit failed: observable, NOT reversed.
                receipt["audit_ok"] = False
                receipt["audit_failure"] = (
                    "Committed; audit capture failed. The operation is "
                    "complete; evidence is missing, not reversed.")
            self._store_receipt(rkey, queued["descriptor"], receipt)
            self._queue.pop(queued_id, None)
            return copy.deepcopy(receipt)
        finally:
            self._in_dispatch = False

    # -- internals ----------------------------------------------------------

    def _rollback_epoch(self) -> int:
        from form.mandell import core_i_recovery as rec
        key = rec._epoch_key(self._owner)
        val = rec._rollback_epochs.get(key, 0)
        if isinstance(val, bool) or not isinstance(val, int):
            raise TypeError("rollback epoch is not an int")
        return val

    def _store_receipt(self, rkey: Tuple[str, str, str],
                       descriptor: Dict[str, Any],
                       receipt: Dict[str, Any]) -> None:
        """Store a receipt with explicit retention bound (AMEND §1)."""
        self._receipts[rkey] = {
            "receipt": copy.deepcopy(receipt),
            "descriptor": copy.deepcopy(descriptor),
        }
        if rkey in self._receipt_order:
            self._receipt_order.remove(rkey)
        self._receipt_order.append(rkey)
        while len(self._receipt_order) > self._receipt_bound:
            oldest = self._receipt_order.pop(0)
            self._receipts.pop(oldest, None)

    def _audit_retry(self, subject: str, envelope: RequestEnvelope,
                     hist: Dict[str, Any]) -> None:
        capture_agent_action(
            self._program, subject=subject, request_id=envelope.request_id,
            operation=envelope.operation, target=envelope.target,
            result=hist.get("result", AUDIT_DENIED),
            correlation=envelope.correlation,
            detail="idempotent retry: historical receipt returned, no duplicate transition")

    def _deny_receipt(self, subject: Optional[str],
                      envelope: Optional[RequestEnvelope],
                      reason: str, detail: str,
                      audit_ok: bool = True) -> Dict[str, Any]:
        return {
            "ok": False,
            "result": AUDIT_DENIED,
            "historical": False,
            "request_id": envelope.request_id if envelope else "",
            "subject": subject or "",
            "operation": envelope.operation if envelope else "",
            "target": envelope.target if envelope else "",
            "reason": reason,
            "detail": _bound(detail, 300),
            "audit_ok": audit_ok,
            "ts": _utcnow(),
        }

    def _finalize_denial(self, subject: str, envelope: RequestEnvelope,
                         queued_id: str, rkey: Tuple[str, str, str],
                         reason: str, detail: str) -> Dict[str, Any]:
        receipt = self._deny_receipt(subject, envelope, reason, detail)
        audit_rec = capture_agent_action(
            self._program, subject=subject, request_id=envelope.request_id,
            operation=envelope.operation, target=envelope.target,
            result=AUDIT_DENIED, correlation=envelope.correlation,
            detail=f"{reason}: {detail}"[:300])
        if audit_rec is None:
            receipt["audit_ok"] = False
        self._store_receipt(rkey, envelope.descriptor(), receipt)
        self._queue.pop(queued_id, None)
        return copy.deepcopy(receipt)

    def _finalize_failure(self, subject: str, envelope: RequestEnvelope,
                          queued_id: str, rkey: Tuple[str, str, str],
                          detail: str) -> Dict[str, Any]:
        """Honest failed/unknown outcome (AMEND §4)."""
        receipt = {
            "ok": False,
            "result": AUDIT_FAILED,
            "historical": False,
            "request_id": envelope.request_id,
            "subject": subject,
            "operation": envelope.operation,
            "target": envelope.target,
            "reason": "unknown_outcome",
            "detail": _bound(detail, 300),
            "audit_ok": True,
            "ts": _utcnow(),
        }
        audit_rec = capture_agent_action(
            self._program, subject=subject, request_id=envelope.request_id,
            operation=envelope.operation, target=envelope.target,
            result=AUDIT_FAILED, correlation=envelope.correlation,
            detail=f"unknown_outcome: {detail}"[:300])
        if audit_rec is None:
            receipt["audit_ok"] = False
        self._store_receipt(rkey, envelope.descriptor(), receipt)
        self._queue.pop(queued_id, None)
        return copy.deepcopy(receipt)

    def _finalize_incomplete(self, subject: str, envelope: RequestEnvelope,
                             queued_id: str, rkey: Tuple[str, str, str],
                             reason: str,
                             writer_receipt: Dict[str, Any]) -> Dict[str, Any]:
        """Preserve incomplete-compensation details (AMEND §4)."""
        receipt = {
            "ok": False,
            "result": AUDIT_INCOMPLETE,
            "historical": False,
            "request_id": envelope.request_id,
            "subject": subject,
            "operation": envelope.operation,
            "target": envelope.target,
            "reason": reason,
            "detail": _bound(
                "Incomplete recovery: the writer reported incomplete "
                f"compensation ({writer_receipt.get('detail', '')}). This is "
                "not an ordinary denial; recovery must complete before "
                "the outcome is known.", 300),
            "writer_detail": _bound(str(writer_receipt.get("detail", "")), 200),
            "audit_ok": True,
            "ts": _utcnow(),
        }
        audit_rec = capture_agent_action(
            self._program, subject=subject, request_id=envelope.request_id,
            operation=envelope.operation, target=envelope.target,
            result=AUDIT_INCOMPLETE, correlation=envelope.correlation,
            detail=f"{reason}: {writer_receipt.get('detail', '')}"[:300])
        if audit_rec is None:
            receipt["audit_ok"] = False
        self._store_receipt(rkey, envelope.descriptor(), receipt)
        self._queue.pop(queued_id, None)
        return copy.deepcopy(receipt)

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
        """Request a confirm through the coordinator."""
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
        if expected_content_hash is not None:
            if not isinstance(expected_content_hash, str):
                return {"ok": False, "result": AUDIT_DENIED,
                        "reason": "bad_envelope",
                        "detail": "expected_content_hash must be str."}
            expected["content_hash"] = expected_content_hash
        try:
            envelope = make_envelope(
                request_id=rid, operation="confirm", target=pid,
                expected=expected, correlation=correlation,
                _program=self._coordinator._program)
        except (EnvelopeValidationError, ValueError) as e:
            return {"ok": False, "result": AUDIT_DENIED,
                    "reason": "bad_envelope", "detail": str(e)}
        try:
            queued_id = self._coordinator.enqueue(self._subject, envelope)
        except (CoordinatorError, EnvelopeValidationError, ValueError) as e:
            return {"ok": False, "result": AUDIT_DENIED,
                    "reason": "enqueue_rejected", "detail": str(e)}
        return self._coordinator.dispatch(queued_id, grant_handle)


def new_coordinator(program: Any) -> HostCoordinator:
    """Create the trusted host coordinator for a program. TRUSTED HOST ONLY."""
    return HostCoordinator(program)
