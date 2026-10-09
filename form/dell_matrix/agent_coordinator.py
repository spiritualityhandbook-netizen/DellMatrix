"""R6.4 trusted host coordinator for multi-agent shared state.

GDP_PHASE_6_R64_MULTI_INTELLIGENCE_SHARED_STATE_CIRCUIT (MODE=C).
AMEND: GDP_PHASE_6_R64_CLOSE_IDENTITY_EVIDENCE_AND_PERSISTENCE.
AMEND-2: GDP_PHASE_6_R64_FINISH_EXISTING_BOUNDARIES.
AMEND-3: GDP_PHASE_6_R64_CLOSE_ALL_OUTWARD_SECRET_PATHS.

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
    snapshot_for(subject)     -> detached sanitized snapshot
    enqueue(subject, envelope) -> queued_id   (shape/bounds validated;
        the VALIDATED snapshot is retained, not the caller's envelope)
    dispatch(queued_id, grant_handle) -> receipt  (authority, freshness,
        recovery-required, and epoch revalidated AT EXECUTION)

A queued request is NOT prior authorization to commit. Revocation,
changed content, recovery-required state, and rollback invalidation
still take effect at dispatch.

Retry identity: receipts are namespaced by canonical
(owner, host-bound subject, request_id). A canonical detached request
descriptor (operation, target, expected evidence, correlation semantics)
is compared for idempotency. B can never receive A's cached receipt.
Returned receipts are detached deep copies; caller mutation cannot
alter cached evidence. Cached-retry and conflict paths remove their
queued entries; a conflicting reuse never overwrites established
history. Historical receipts are labeled historical: not new
authorization, execution, or proof of unchanged live state. Receipt
retention is bounded (no durable exactly-once claim).

Secret protection: the COMPLETE external envelope (identifiers, target,
operation, all keys and values) is screened by VALUE using the existing
protected-value infrastructure
(form.dell_matrix.inference_dock.protected_values /
contains_protected_decoded), not by key name alone. Protection failure
rejects explicitly.

ONE COMPLETE OUTWARD BOUNDARY (AMEND-3): every agent-facing return is
sanitized through a single boundary — snapshots, receipts, audit
records, nested dictionary keys AND values, identifiers, provenance,
error details. Protected dictionary keys receive deterministic
collision-free safe representations ([REDACTED_KEY:n]); they are never
passed through and never silently overwrite evidence. If sanitization
is unavailable, the original payload is NEVER released: receipts become
minimal fixed-schema (classification preserved, no uncontrolled text,
no identifiers, no nested payloads, no reflected exceptions),
snapshots fail closed. A warning flag does not close the boundary.
Coverage: canonical grant-handle format + session-issued values +
configured credentials. No unknown-secret guarantee is claimed.

Outcome contract: audit capture failures are aggregated across the
request lifecycle (enqueue, dispatch, retry, conflict, failure,
incomplete) and observable in the returned outcome (audit_ok flag +
audit block); captured-in-memory evidence is distinguished from
persisted evidence. Incomplete compensation from the canonical writer
is classified by the writer's canonical fields
(reason="acceptance_policy_denied", compensation="incomplete",
compensation_failures, compensation_removed, evidence_retained) and
preserved as incomplete_recovery with sanitized structured details —
never ordinary denial. Operation exceptions yield honest
failed/unknown, never inferred noncommit.
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


def _protection_utils():
    """Import the existing protection utilities.

    Directive §2: protection import failure must REJECT explicitly, never
    silently disable screening. Reuses the existing protection
    infrastructure; no new secret interpreter is introduced.

    Directive §2 (FINISH_OUTPUT_COLLISION_AND_ERROR_CONTRACT): the
    failure message is FIXED — the original exception text is never
    reflected, as it may contain protected material.
    """
    try:
        from form.dell_matrix.inference_dock import (
            protected_values, contains_protected_decoded)
    except Exception:
        raise EnvelopeValidationError(
            "secret protection unavailable (import failed)")
    return protected_values, contains_protected_decoded


def _screen_envelope(program: Any, *, request_id: str, operation: str,
                     target: str, expected: Dict[str, Any],
                     correlation: Dict[str, Any]) -> None:
    """Screen the COMPLETE external envelope (directive §2).

    Covers identifiers (request_id), target, operation, and all keys and
    string values in expected/correlation — not only expected/correlation
    values. Uses the decoded-form check so \\uXXXX-encoded handles are
    caught. Raises EnvelopeValidationError on detection or on protection
    failure. Never reflects protected values in the error message.
    """
    protected_values, contains_protected = _protection_utils()
    try:
        protected = protected_values(program)
    except Exception:
        raise EnvelopeValidationError(
            "secret protection unavailable (values failed)")

    def _hit(where: str) -> EnvelopeValidationError:
        # The error names the location, never the protected value.
        return EnvelopeValidationError(
            f"envelope: protected material detected at {where}")

    for label, text in (("request_id", request_id),
                        ("operation", operation),
                        ("target", target)):
        try:
            if contains_protected(str(text), protected):
                raise _hit(label)
        except EnvelopeValidationError:
            raise
        except Exception:
            raise EnvelopeValidationError(
                "secret protection unavailable (screen failed)")

    def _scan(obj: Any, path: str) -> None:
        try:
            if isinstance(obj, str):
                if contains_protected(obj, protected):
                    raise _hit(path)
            elif isinstance(obj, dict):
                for k, v in obj.items():
                    if isinstance(k, str) and contains_protected(k, protected):
                        raise _hit(f"{path}.<key>")
                    _scan(v, f"{path}.{k}")
            elif isinstance(obj, (list, tuple)):
                for i, v in enumerate(obj):
                    _scan(v, f"{path}[{i}]")
        except EnvelopeValidationError:
            raise
        except Exception:
            raise EnvelopeValidationError(
                "secret protection unavailable (screen failed)")

    _scan(expected, "expected")
    _scan(correlation, "correlation")


def _sanitize_outward(program: Any, obj: Any) -> Any:
    """Redact recognized protected values from outward-bound data.

    Directive §1 (CLOSE_ALL_OUTWARD_SECRET_PATHS): sanitizes nested
    dictionary KEYS as well as values, identifiers, provenance, and error
    details. Protected keys are replaced with deterministic
    collision-free safe representations ([REDACTED_KEY:n]) — never
    silently overwritten, never passed through.

    Raises EnvelopeValidationError if protection is unavailable — the
    caller must treat this as observable failure and MUST NOT return the
    unsanitized original (directive §2).
    """
    protected_values, contains_protected = _protection_utils()
    try:
        protected = protected_values(program)
    except Exception:
        # Fixed message: the original exception text may contain
        # protected material and is never reflected (directive §2).
        raise EnvelopeValidationError(
            "secret protection unavailable (values failed)")

    def _check(text: str) -> bool:
        try:
            return bool(contains_protected(text, protected))
        except Exception:
            raise EnvelopeValidationError(
                "secret protection unavailable (screen failed)")

    def _redact(o: Any, key_counter: List[int]) -> Any:
        if isinstance(o, str):
            return _REDACTED if _check(o) else o
        if isinstance(o, dict):
            # Directive §1 (FINISH_OUTPUT_COLLISION_AND_ERROR_CONTRACT):
            # Reserve ALL surviving clean keys BEFORE allocating
            # replacements. A protected key followed by a literal
            # "[REDACTED_KEY:1]" (or vice versa) must not collide —
            # the allocator checks reserved clean keys, not only keys
            # already emitted.
            reserved: set = set()
            for k in o.keys():
                if isinstance(k, str) and not _check(k):
                    reserved.add(k)
            out: Dict[str, Any] = {}
            allocated: set = set()
            for k, v in o.items():
                nk = k
                if isinstance(k, str) and _check(k):
                    # Deterministic replacement that skips reserved clean
                    # keys AND previously allocated replacements.
                    while True:
                        key_counter[0] += 1
                        candidate = f"[REDACTED_KEY:{key_counter[0]}]"
                        if (candidate not in reserved
                                and candidate not in allocated
                                and candidate not in out):
                            break
                    nk = candidate
                    allocated.add(nk)
                out[nk] = _redact(v, key_counter)
            return out
        if isinstance(o, (list, tuple)):
            return [_redact(v, key_counter) for v in o]
        return o

    try:
        return _redact(obj, [0])
    except EnvelopeValidationError:
        raise
    except Exception:
        raise EnvelopeValidationError(
            "secret protection unavailable (redact failed)")


def _safe_detail(program: Any, text: Any) -> str:
    """Sanitize an outward-bound detail string.

    Returns the sanitized text, or a fixed safe message if sanitization
    is unavailable. Never returns unsanitized text.
    """
    try:
        sanitized = _sanitize_outward(program, str(text))
        return str(sanitized)[:300]
    except EnvelopeValidationError:
        return "Detail withheld: output sanitization unavailable."


def _minimal_receipt(*, ok: bool, result: str,
                     audit_failures: List[str]) -> Dict[str, Any]:
    """Minimal fixed-schema receipt for protection-unavailable exits.

    Directive §2: preserves the actual classification (ok/result) but
    contains NO uncontrolled text, identifiers, nested payloads, or
    reflected exceptions. Reports the protection failure explicitly.
    Never falsely reverses an already-committed operation.
    """
    return {
        "ok": bool(ok),
        "result": result,
        "historical": False,
        "request_id": "",
        "subject": "",
        "operation": "",
        "target": "",
        "reason": "protection_unavailable",
        "detail": ("Output sanitization failed after execution. "
                   "Classification preserved; no request content returned. "
                   "Evidence/protection failure reported explicitly."),
        "audit_ok": False,
        "audit": {
            "captured_in_memory": False,
            "persisted": False,
            "evidence": "missing",
            "failures": list(audit_failures) + ["protection_unavailable"],
            "ok": False,
        },
        "protection_failure": True,
        "ts": _utcnow(),
    }


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
    # Value-based secret screening of the COMPLETE envelope (directive §2):
    # identifiers, target, operation, and all keys/values in expected and
    # correlation. Protection failure rejects explicitly.
    if program is not None:
        _screen_envelope(program, request_id=request_id, operation=operation,
                         target=target, expected=exp, correlation=corr)
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
    The COMPLETE record is sanitized — subject, request_id, operation,
    target, correlation, affected, provenance, and detail (directive §2).
    If sanitization protection is unavailable, capture FAILS (returns
    None) rather than storing unsanitized material.
    """
    try:
        records = getattr(program, "agent_audit_records", None)
        if records is None or not isinstance(records, dict):
            return None
        if result not in AUDIT_RESULTS:
            result = AUDIT_FAILED
        seq = int(getattr(program, "agent_audit_seq", 0) or 0) + 1
        owner = str(getattr(program, "owner", "") or "")

        # Sanitize the complete outward record BEFORE construction.
        # Protection failure -> observable capture failure (None).
        try:
            san_subject = _sanitize_outward(program, subject)
            san_request_id = _sanitize_outward(program, request_id)
            san_operation = _sanitize_outward(program, operation)
            san_target = _sanitize_outward(program, target)
            san_correlation = _sanitize_outward(program, dict(correlation or {}))
            san_affected = _sanitize_outward(
                program, [a for a in (affected or [])[:16]])
            san_provenance = _sanitize_outward(program, dict(provenance or {}))
            san_detail = _sanitize_outward(program, detail)
        except EnvelopeValidationError:
            return None

        record = {
            "audit_id": _audit_id_for(owner, seq, str(san_request_id),
                                      str(san_operation), result),
            "audit_version": AGENT_AUDIT_VERSION,
            "audit_seq": seq,
            "owner": owner,
            "subject": _bound(san_subject, _MAX_SUBJECT),
            "request_id": _bound(san_request_id, _MAX_REQUEST_ID),
            "operation": _bound(san_operation, _MAX_OPERATION),
            "target": _bound(san_target, _MAX_TARGET),
            "result": result,
            "correlation": san_correlation if isinstance(san_correlation, dict) else {},
            "affected": [_bound(a, _MAX_TARGET) for a in san_affected]
                        if isinstance(san_affected, list) else [],
            "provenance": san_provenance if isinstance(san_provenance, dict) else {},
            "detail": _bound(san_detail, 300),
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

    R6.5 (GDP_PHASE_6_R65_SEPARATION_ENFORCEMENT): enforces separation
    boundaries — persona metadata never confers authority; BIMO fusion
    is descriptive, not authoritative.

    HUMAN SOVEREIGNTY: Every protected operation requires a grant issued
    through the trusted host path (AcceptancePolicy via agent_authority).
    Agents cannot mint, widen, or restore authority. There is no bulk
    threshold — sovereignty applies to every protected operation equally.
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
        """Return a bounded DETACHED sanitized snapshot for an agent.

        Directive §1 (CLOSE_ALL_OUTWARD_SECRET_PATHS): proposal and Plane
        words/labels are sanitized. The snapshot is built from detached
        string copies; sanitization never modifies canonical Idea content.
        If sanitization is unavailable, fail closed (raise) rather than
        return unscreened content.
        """
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
        snap = {
            "subject": subject,
            "owner": self._owner,
            "ideas": ideas,
            "units": units,
            "detached": True,
        }
        try:
            return _sanitize_outward(self._program, snap)
        except EnvelopeValidationError:
            # Directive §2 (FINISH_OUTPUT_COLLISION_AND_ERROR_CONTRACT):
            # Fixed non-reflecting outward error. The original exception
            # text is NOT included — it may contain protected material.
            # Diagnostic evidence is retained through the audit failure
            # mechanism, not the exception message. Suppress chaining.
            raise CoordinatorError(
                "snapshot unavailable: output sanitization failed"
            ) from None

    # -- enqueue -----------------------------------------------------------

    def enqueue(self, subject: str, envelope: RequestEnvelope) -> str:
        """Validate and queue a request. Returns queued_id.

        Directive §1: the validator's DETACHED values are RETAINED. A new
        envelope is constructed from the validated values and stored;
        the caller's original envelope (whose nested mappings remain
        mutable) is never stored. The descriptor is derived from the
        retained snapshot. Post-enqueue mutation of the caller's envelope
        cannot reach execution, attribution, screening, or evidence.
        """
        _validate_subject(subject)
        if subject not in self._agents:
            raise CoordinatorError(f"unknown agent subject: {subject}")
        if not isinstance(envelope, RequestEnvelope):
            raise CoordinatorError("envelope must be a RequestEnvelope")
        # Re-validate AND RETAIN: construct a new envelope from the
        # validator's detached copies. Construction may have been bypassed
        # via direct RequestEnvelope(...) instantiation, and the original's
        # nested mappings are mutable regardless.
        rid, op, tgt, exp, corr = _validate_envelope_fields(
            request_id=envelope.request_id, operation=envelope.operation,
            target=envelope.target, expected=envelope.expected,
            correlation=envelope.correlation, program=self._program)
        retained = RequestEnvelope(request_id=rid, operation=op, target=tgt,
                                   expected=exp, correlation=corr)
        if len(self._queue) >= self._queue_bound:
            raise CoordinatorError("coordinator queue full")
        # Fingerprint/epoch computation failures fail closed (AMEND §2).
        try:
            content_now = self._program.acceptance_data_hash(
                retained.target, retained.operation)
            if not isinstance(content_now, str):
                raise TypeError("content fingerprint not a str")
        except Exception:
            raise CoordinatorError(
                "fingerprint computation failed closed")
        try:
            epoch_now = self._rollback_epoch()
        except Exception:
            raise CoordinatorError(
                "epoch computation failed closed")
        queued_id = "q:" + uuid.uuid4().hex[:16]
        self._queue[queued_id] = {
            "queued_id": queued_id,
            "subject": subject,
            "envelope": retained,
            "descriptor": retained.descriptor(),
            "content_at_enqueue": content_now,
            "epoch_at_enqueue": epoch_now,
            "enqueued_at": _utcnow(),
            # Directive §3: aggregate audit-capture failures across the
            # request lifecycle; a failed attempted-event must not
            # disappear because a later final-event capture succeeds.
            "audit_failures": [],
        }
        audit_rec = capture_agent_action(
            self._program, subject=subject, request_id=retained.request_id,
            operation=retained.operation, target=retained.target,
            result=AUDIT_ATTEMPTED, correlation=retained.correlation,
            detail="enqueued")
        if audit_rec is None:
            self._queue[queued_id]["audit_failures"].append("enqueue_attempted")
        return queued_id

    # -- dispatch ----------------------------------------------------------

    def dispatch(self, queued_id: str, grant_handle: str) -> Dict[str, Any]:
        """Execute or deny a queued request. Serialized; non-reentrant.

        Directive §2: all exits return sanitized outward data, or a
        minimal fixed-schema receipt if sanitization is unavailable.
        """
        if self._in_dispatch:
            return self._outward(self._deny_receipt(
                None, None, "reentrant_dispatch",
                "Concurrent/reentrant dispatch is rejected explicitly; "
                "protected writes are serialized.", audit_ok=True))
        queued = self._queue.get(queued_id)
        if queued is None:
            # The queued_id is user-supplied; sanitize the reflected detail.
            return self._outward(self._deny_receipt(
                None, None, "unknown_queued_id",
                _safe_detail(self._program,
                             f"No such queued request: {queued_id!r}."),
                audit_ok=True))
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
                audit_rec = capture_agent_action(
                    self._program, subject=subject,
                    request_id=envelope.request_id,
                    operation=envelope.operation, target=envelope.target,
                    result=hist.get("result", AUDIT_DENIED),
                    correlation=envelope.correlation,
                    detail="idempotent retry: historical receipt returned, "
                           "no duplicate transition")
                block = self._audit_block(
                    queued, "retry", audit_rec is not None)
                hist = self._finalize_audit_ok(hist, block)
                # Directive §2: sanitized outward, or minimal on failure.
                return self._outward(hist)
            # Directive §1: conflicting reuse is denied WITHOUT overwriting
            # the established historical receipt. The prior record stands.
            receipt = self._deny_receipt(
                subject, envelope, "request_id_reuse",
                "request_id reused with different request descriptor; rejected.")
            audit_rec = capture_agent_action(
                self._program, subject=subject,
                request_id=envelope.request_id,
                operation=envelope.operation, target=envelope.target,
                result=AUDIT_DENIED, correlation=envelope.correlation,
                detail="request_id_reuse: conflicting descriptor rejected; "
                       "established receipt preserved")
            block = self._audit_block(
                queued, "conflict", audit_rec is not None)
            receipt = self._finalize_audit_ok(receipt, block)
            return copy.deepcopy(self._outward(receipt))

        self._in_dispatch = True
        try:
            # Recovery-required: stale-save protection (R6.3).
            try:
                from form.mandell.core_i_recovery import check_save_allowed
                check_save_allowed(program, "agent dispatch")
            except Exception as e:
                return self._finalize_denial(
                    subject, envelope, queued_id, rkey, "recovery_required",
                    f"Recovery-required state blocks dispatch: {e}",
                    queued=queued)

            # Rollback epoch.
            if self._rollback_epoch() != queued["epoch_at_enqueue"]:
                return self._finalize_denial(
                    subject, envelope, queued_id, rkey, "stale_after_rollback",
                    "Rollback epoch advanced after enqueue; queued request invalidated.",
                    queued=queued)

            # Freshness.
            try:
                content_now = program.acceptance_data_hash(
                    envelope.target, envelope.operation)
                if not isinstance(content_now, str):
                    raise TypeError("content fingerprint not a str")
            except Exception as e:
                return self._finalize_denial(
                    subject, envelope, queued_id, rkey, "fingerprint_failed",
                    f"Content fingerprint failed closed: {e}",
                    queued=queued)
            expected = envelope.expected.get("content_hash")
            if expected and expected != content_now:
                return self._finalize_denial(
                    subject, envelope, queued_id, rkey, "content_changed",
                    "Target content changed since the request was prepared; denied.",
                    queued=queued)
            if content_now != queued["content_at_enqueue"]:
                return self._finalize_denial(
                    subject, envelope, queued_id, rkey, "content_changed",
                    "Target content changed between enqueue and dispatch; denied.",
                    queued=queued)

            # Authority: canonical R6.1 writer path.
            from form.dell_matrix import agent_authority as aa
            try:
                writer_receipt = aa.agent_confirm(
                    program, envelope.target, grant_handle, subject)
            except Exception as e:
                # Honest failed/unknown; never infer noncommit from exception.
                return self._finalize_failure(
                    subject, envelope, queued_id, rkey,
                    f"Writer raised {type(e).__name__}: {e}",
                    queued=queued)

            if not isinstance(writer_receipt, dict):
                return self._finalize_failure(
                    subject, envelope, queued_id, rkey,
                    "Writer returned non-dict receipt; outcome unknown.",
                    queued=queued)
            if not writer_receipt.get("ok"):
                # Directive §3: classify by the canonical writer contract,
                # not invented reason names.
                if self._is_canonical_incomplete(writer_receipt):
                    return self._finalize_incomplete(
                        subject, envelope, queued_id, rkey, writer_receipt,
                        queued=queued)
                reason = writer_receipt.get("reason", "writer_denied")
                try:
                    san_wdetail = _sanitize_outward(
                        self._program, writer_receipt.get("detail", ""))
                except EnvelopeValidationError:
                    san_wdetail = "[sanitize failed]"
                detail = str(san_wdetail)
                return self._finalize_denial(
                    subject, envelope, queued_id, rkey, f"writer_{reason}",
                    f"Canonical writer denied: {detail}" if detail else
                    "Canonical writer denied.",
                    queued=queued)

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
                "ts": _utcnow(),
            }
            audit_rec = capture_agent_action(
                program, subject=subject, request_id=envelope.request_id,
                operation=envelope.operation, target=envelope.target,
                result=AUDIT_COMMITTED, correlation=envelope.correlation,
                affected=[envelope.target],
                provenance={"writer_ok": True},
                detail="committed via canonical writer")
            block = self._audit_block(queued, "committed",
                                      audit_rec is not None)
            receipt = self._finalize_audit_ok(receipt, block)
            if audit_rec is None:
                # Committed but audit failed: observable, NOT reversed.
                receipt["audit_failure"] = (
                    "Committed; audit capture failed. The operation is "
                    "complete; evidence is missing, not reversed.")
            # Directive §2: sanitized outward, or minimal on failure.
            # The minimal receipt (classification preserved) is what is
            # stored and returned; the unsanitized original is never released.
            receipt = self._outward(receipt)
            self._store_receipt(rkey, queued["descriptor"], receipt)
            self._queue.pop(queued_id, None)
            return copy.deepcopy(receipt)
        finally:
            self._in_dispatch = False

    def _outward(self, receipt: Dict[str, Any]) -> Dict[str, Any]:
        """Return the outward-bound receipt: sanitized, or minimal.

        Directive §2 (CLOSE_ALL_OUTWARD_SECRET_PATHS): if sanitization
        fails, NEVER return the unsanitized original. Return a minimal
        fixed-schema receipt preserving the classification (ok/result).
        """
        try:
            return _sanitize_outward(self._program, receipt)
        except EnvelopeValidationError:
            return _minimal_receipt(
                ok=receipt.get("ok", False),
                result=receipt.get("result", AUDIT_FAILED),
                audit_failures=receipt.get("audit", {}).get("failures", []))

    # -- internals ----------------------------------------------------------

    def _audit_block(self, queued: Optional[Dict[str, Any]],
                     event: str, captured: bool) -> Dict[str, Any]:
        """Build the receipt's audit-evidence block (directive §3).

        Aggregates capture failures across the request lifecycle
        (enqueue, dispatch, retry, conflict, failure, incomplete). A
        failed attempted-event is listed even when the final event
        captured successfully. Distinguishes captured-in-memory evidence
        from persisted evidence (persistence requires save+reload; it is
        never claimed at dispatch time).
        """
        failures: List[str] = []
        if queued is not None:
            failures.extend(queued.get("audit_failures") or [])
        if not captured:
            failures.append(event)
        ok = not failures
        return {
            "captured_in_memory": captured,
            "persisted": False,
            "evidence": "in_memory" if captured else "missing",
            "failures": failures,
            "ok": ok,
        }

    def _finalize_audit_ok(self, receipt: Dict[str, Any],
                           audit_block: Dict[str, Any]) -> Dict[str, Any]:
        """Attach the audit block; keep top-level audit_ok for compat."""
        receipt["audit"] = audit_block
        receipt["audit_ok"] = audit_block["ok"]
        if not audit_block["ok"]:
            receipt["audit_failure"] = (
                "One or more audit captures failed during this request's "
                f"lifecycle: {', '.join(audit_block['failures'])}. "
                "The outcome stands; evidence is incomplete, not reversed.")
        return receipt

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
                         reason: str, detail: str,
                         queued: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        receipt = self._deny_receipt(subject, envelope, reason, detail)
        audit_rec = capture_agent_action(
            self._program, subject=subject, request_id=envelope.request_id,
            operation=envelope.operation, target=envelope.target,
            result=AUDIT_DENIED, correlation=envelope.correlation,
            detail=f"{reason}: {detail}"[:300])
        block = self._audit_block(queued, "denied", audit_rec is not None)
        receipt = self._finalize_audit_ok(receipt, block)
        # Directive §2: sanitized outward, or minimal on failure.
        # The minimal receipt (classification preserved) is what is
        # stored and returned; the unsanitized original is never released.
        receipt = self._outward(receipt)
        self._store_receipt(rkey, envelope.descriptor(), receipt)
        self._queue.pop(queued_id, None)
        return copy.deepcopy(receipt)

    def _finalize_failure(self, subject: str, envelope: RequestEnvelope,
                          queued_id: str, rkey: Tuple[str, str, str],
                          detail: str,
                          queued: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
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
            "ts": _utcnow(),
        }
        audit_rec = capture_agent_action(
            self._program, subject=subject, request_id=envelope.request_id,
            operation=envelope.operation, target=envelope.target,
            result=AUDIT_FAILED, correlation=envelope.correlation,
            detail=f"unknown_outcome: {detail}"[:300])
        block = self._audit_block(queued, "failed", audit_rec is not None)
        receipt = self._finalize_audit_ok(receipt, block)
        # Directive §2: sanitized outward, or minimal on failure.
        # The minimal receipt (classification preserved) is what is
        # stored and returned; the unsanitized original is never released.
        receipt = self._outward(receipt)
        self._store_receipt(rkey, envelope.descriptor(), receipt)
        self._queue.pop(queued_id, None)
        return copy.deepcopy(receipt)

    def _is_canonical_incomplete(self, writer_receipt: Dict[str, Any]) -> bool:
        """Classify by the canonical writer contract (directive §3).

        confirm_lineage reports incomplete compensation as:
            reason="acceptance_policy_denied",
            compensation="incomplete",
            compensation_failures, compensation_removed, evidence_retained.
        No invented reason names are consulted.
        """
        return (writer_receipt.get("reason") == "acceptance_policy_denied"
                and writer_receipt.get("compensation") == "incomplete")

    def _finalize_incomplete(self, subject: str, envelope: RequestEnvelope,
                             queued_id: str, rkey: Tuple[str, str, str],
                             writer_receipt: Dict[str, Any],
                             queued: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Preserve incomplete-compensation details (directive §3).

        Returns incomplete_recovery with the canonical structured fields
        retained and sanitized — never an ordinary denial, and failure
        details never disappear.
        """
        try:
            san_failures = _sanitize_outward(
                self._program, writer_receipt.get("compensation_failures", []))
            san_removed = _sanitize_outward(
                self._program, writer_receipt.get("compensation_removed", []))
            san_detail = _sanitize_outward(
                self._program, writer_receipt.get("detail", ""))
        except EnvelopeValidationError:
            san_failures, san_removed, san_detail = [], [], "[sanitize failed]"
        receipt = {
            "ok": False,
            "result": AUDIT_INCOMPLETE,
            "historical": False,
            "request_id": envelope.request_id,
            "subject": subject,
            "operation": envelope.operation,
            "target": envelope.target,
            "reason": "incomplete_recovery",
            "writer_reason": writer_receipt.get("reason"),
            "compensation": writer_receipt.get("compensation"),
            "compensation_failures": san_failures,
            "compensation_removed": san_removed,
            "evidence_retained": bool(writer_receipt.get("evidence_retained")),
            "detail": _bound(
                "Incomplete recovery: the canonical writer reported "
                "incomplete compensation. This is not an ordinary denial; "
                "recovery must complete before the outcome is known.", 300),
            "writer_detail": _bound(str(san_detail), 200),
            "ts": _utcnow(),
        }
        audit_rec = capture_agent_action(
            self._program, subject=subject, request_id=envelope.request_id,
            operation=envelope.operation, target=envelope.target,
            result=AUDIT_INCOMPLETE, correlation=envelope.correlation,
            provenance={
                "compensation": "incomplete",
                "compensation_failures": san_failures,
                "evidence_retained": bool(writer_receipt.get("evidence_retained")),
            },
            detail=f"incomplete_recovery: {san_detail}"[:300])
        block = self._audit_block(queued, "incomplete", audit_rec is not None)
        receipt = self._finalize_audit_ok(receipt, block)
        # Directive §2: sanitized outward, or minimal on failure.
        # The minimal receipt (classification preserved) is what is
        # stored and returned; the unsanitized original is never released.
        receipt = self._outward(receipt)
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
        """Request a confirm through the coordinator.

        Directive §2: validation-error exits return sanitized details;
        if sanitization is unavailable, a fixed safe message is used.
        The grant handle itself never enters the returned receipt.
        """
        _program = self._coordinator._program
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
                _program=_program)
        except (EnvelopeValidationError, ValueError) as e:
            return {"ok": False, "result": AUDIT_DENIED,
                    "reason": "bad_envelope",
                    "detail": _safe_detail(_program, e)}
        try:
            queued_id = self._coordinator.enqueue(self._subject, envelope)
        except (CoordinatorError, EnvelopeValidationError, ValueError) as e:
            return {"ok": False, "result": AUDIT_DENIED,
                    "reason": "enqueue_rejected",
                    "detail": _safe_detail(_program, e)}
        return self._coordinator.dispatch(queued_id, grant_handle)


def new_coordinator(program: Any) -> HostCoordinator:
    """Create the trusted host coordinator for a program. TRUSTED HOST ONLY."""
    return HostCoordinator(program)
