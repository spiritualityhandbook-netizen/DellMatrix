"""Acceptance policy for human-controlled confirmation.

Phase 5 (WO-5.1): Automated exploration can propose; acceptance requires
explicit human review or scoped session opt-in.

Director GDP_PHASE_5_WHOLE_CIRCUIT_CONVERGENCE (2026-10-05):
- The policy is the SINGLE owner of acceptance authorization.
- Session IDs are collision-resistant (uuid4), not millisecond timestamps.
- Acceptance-relevant data uses canonical JSON serialization + SHA-256;
  no delimiter concatenation.
- Approval ISSUANCE is recorded in the session policy. A matching
  dictionary alone is not evidence of issuance: check() verifies the
  approval_id against the issuance record.
- Approvals bind operation, target, reviewed data hash, and session.
  Revocation is supported. Retry means re-issuance after re-review.
- Revalidation happens at the mutation/commit boundary, not merely
  before delegation.
- Default denial, explicit manual review, scoped opt-in preserved.
- Scope: local acceptance mechanism. This does not claim protection
  against arbitrary malicious Python running in the same process.

One policy check at the canonical acceptance boundary
(Program.confirm_proposal). Producers must carry explicit review/producer
context; permission is never inferred from owner prefixes, caller names,
prompts, or default flags.

Session-scoped opt-in: identifies scope/producer, expires at session end,
is visible, revocable, and audited. Recheck happens immediately before
commit; revocation invalidates approval.
"""

from __future__ import annotations
from typing import Dict, Any, Optional, List, Mapping
import hashlib
import json
import time
import uuid


def canonical_hash(data: Mapping[str, Any]) -> str:
    """Canonical SHA-256 over JSON with sorted keys.

    Deterministic across processes. `default=str` handles non-JSON-native
    values conservatively (they stringify identically given identical input).
    """
    raw = json.dumps(data, sort_keys=True, separators=(",", ":"),
                     default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def acceptance_data(identity: str, owner: str, content: Mapping[str, Any],
                    parents: List[str],
                    goals: Optional[List[str]] = None,
                    revision: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    """Canonical acceptance-relevant data for hashing.

    Fields: identity, owner, content, parents, goals, revision metadata.
    Callers must pass the same logical data to get the same hash; field
    ORDER does not matter (canonical JSON sorts keys).
    """
    return {
        "identity": identity,
        "owner": owner or "",
        "content": dict(content),
        "parents": sorted(parents or []),
        "goals": sorted(goals or []),
        "revision": dict(revision or {}),
    }


class ApprovalError(ValueError):
    """Raised for malformed approval issuance requests."""


class AcceptancePolicy:
    """Session-scoped acceptance policy.

    Default: DENY. Producers must either:
    1. Present a review context referencing an approval ISSUED by this
       policy session (issuance recorded; revocation honored), or
    2. Hold an active scoped opt-in for their producer ID.

    All decisions are audited. Opt-ins and issued approvals expire at
    session end. Restart clears both.
    """

    def __init__(self):
        # producer_id -> grant record
        self._opt_ins: Dict[str, Dict[str, Any]] = {}
        # approval_id -> issuance record
        self._issued_approvals: Dict[str, Dict[str, Any]] = {}
        self._revoked_approvals: set = set()
        self._audit: List[Dict[str, Any]] = []
        # Collision-resistant session identifier (Director 2026-10-05).
        self._session_id = f"session_{uuid.uuid4().hex}"

    @property
    def session_id(self) -> str:
        return self._session_id

    # -- opt-in ---------------------------------------------------------

    def grant_opt_in(self, producer: str, scope: str,
                     note: str = "") -> Dict[str, Any]:
        """Grant scoped opt-in. Visible, revocable, audited."""
        if not isinstance(producer, str) or not producer:
            raise ValueError("producer must be non-empty str")
        if not isinstance(scope, str) or not scope:
            raise ValueError("scope must be non-empty str")
        grant = {
            "producer": producer,
            "scope": scope,
            "granted_at": time.time(),
            "note": note[:200],
            "session_id": self._session_id,
        }
        self._opt_ins[producer] = grant
        self._audit.append({
            "action": "grant",
            "producer": producer,
            "scope": scope,
            "at": grant["granted_at"],
        })
        return {"ok": True, "grant": grant}

    def revoke_opt_in(self, producer: str) -> Dict[str, Any]:
        """Revoke opt-in. Audited."""
        existed = producer in self._opt_ins
        if existed:
            del self._opt_ins[producer]
        self._audit.append({
            "action": "revoke",
            "producer": producer,
            "at": time.time(),
            "existed": existed,
        })
        return {"ok": True, "revoked": existed}

    def list_opt_ins(self) -> List[Dict[str, Any]]:
        """Visible list of active opt-ins."""
        return [
            {"producer": p, "scope": g["scope"], "note": g["note"]}
            for p, g in self._opt_ins.items()
        ]

    def is_opted_in(self, producer: str) -> bool:
        """Session-bound opt-in check. Replaces direct _opt_ins inspection."""
        grant = self._opt_ins.get(producer)
        return bool(grant and grant.get("session_id") == self._session_id)

    # -- approval issuance ----------------------------------------------

    def issue_approval(self, *, operation: str, target: str, reviewer: str,
                       data: Mapping[str, Any],
                       producer: Optional[str] = None,
                       note: str = "") -> Dict[str, Any]:
        """Record approval issuance. Returns approval_id + review context.

        The returned context is the ONLY form check() accepts: it must
        reference an issuance recorded here, in this session, not revoked,
        with matching operation/target/data hash.

        Retry semantics: a denied or stale approval is never auto-retried.
        The caller re-reviews and calls issue_approval again, producing a
        NEW approval_id. Each issuance is independently audited.
        """
        if not isinstance(operation, str) or not operation:
            raise ApprovalError("operation must be non-empty str")
        if not isinstance(target, str) or not target:
            raise ApprovalError("target must be non-empty str")
        if not isinstance(reviewer, str) or not reviewer:
            raise ApprovalError("reviewer must be non-empty str")
        data_hash = canonical_hash(data)
        approval_id = f"appr_{uuid.uuid4().hex[:16]}"
        record = {
            "approval_id": approval_id,
            "operation": operation,
            "target": target,
            "reviewer": reviewer,
            "data_hash": data_hash,
            "session_id": self._session_id,
            "producer": producer,
            "issued_at": time.time(),
            "note": note[:200],
        }
        self._issued_approvals[approval_id] = record
        self._audit.append({
            "action": "issue",
            "approval_id": approval_id,
            "operation": operation,
            "target": target,
            "reviewer": reviewer,
            "at": record["issued_at"],
        })
        context = {
            "approval_id": approval_id,
            "reviewer": reviewer,
            "approved_pid": target,
            "operation": operation,
            "session_id": self._session_id,
            "proposal_version": data_hash,
        }
        return {"ok": True, "approval_id": approval_id, "context": context,
                "record": dict(record)}

    def derive_approval(self, *, source_approval_id: Optional[str],
                        source_opt_in: Optional[str],
                        operation: str, target: str, reviewer: str,
                        data: Mapping[str, Any],
                        note: str = "") -> Dict[str, Any]:
        """Derive a scoped approval from an approved enclosing operation.

        Used by composite operations (e.g. supersession): the enclosing
        operation was authorized (via approval or opt-in); the inner step
        (e.g. successor confirm) gets its own recorded, audited approval
        bound to the inner target+data. This is NOT a general bypass: the
        derived approval is recorded, bound, revocable, and session-scoped
        like any other.
        """
        if source_approval_id:
            src = self._issued_approvals.get(source_approval_id)
            if (not src or source_approval_id in self._revoked_approvals
                    or src["session_id"] != self._session_id):
                raise ApprovalError("source approval invalid/revoked/foreign")
            from_note = f"derived from {source_approval_id}"
        elif source_opt_in:
            if not self.is_opted_in(source_opt_in):
                raise ApprovalError("source opt-in not active")
            from_note = f"derived from opt_in:{source_opt_in}"
        else:
            raise ApprovalError("derive_approval requires a source")
        note = (note + " " + from_note).strip()[:200]
        result = self.issue_approval(operation=operation, target=target,
                                     reviewer=reviewer, data=data,
                                     producer=source_opt_in, note=note)
        result["record"]["derived_from"] = (
            source_approval_id or f"opt_in:{source_opt_in}")
        self._issued_approvals[result["approval_id"]] = result["record"]
        return result

    def revoke_approval(self, approval_id: str) -> Dict[str, Any]:
        """Revoke a previously issued approval. Audited."""
        existed = approval_id in self._issued_approvals
        if existed:
            self._revoked_approvals.add(approval_id)
        self._audit.append({
            "action": "revoke_approval",
            "approval_id": approval_id,
            "at": time.time(),
            "existed": existed,
        })
        return {"ok": True, "revoked": existed}

    def list_approvals(self) -> List[Dict[str, Any]]:
        """Visible list of issued (non-revoked) approvals."""
        return [
            {k: r[k] for k in ("approval_id", "operation", "target",
                               "reviewer", "issued_at", "note")}
            for aid, r in self._issued_approvals.items()
            if aid not in self._revoked_approvals
        ]

    # -- check ----------------------------------------------------------

    def check(self, producer: str, pid: str,
              review_context: Optional[Dict[str, Any]] = None,
              proposal_version: Optional[str] = None,
              operation: str = "confirm") -> Dict[str, Any]:
        """Check if acceptance is allowed. Called at the commit boundary.

        The review context must reference an approval ISSUED by this policy
        session (verified against the issuance record — a matching dict
        alone is insufficient), not revoked, with matching operation,
        target, session, and data hash.
        """
        # 1. Issued-approval review context.
        if isinstance(review_context, dict):
            approval_id = review_context.get("approval_id")
            rec = self._issued_approvals.get(approval_id) if approval_id else None
            if (rec is not None
                    and approval_id not in self._revoked_approvals
                    and rec["session_id"] == self._session_id
                    and rec["operation"] == operation
                    and rec["target"] == pid
                    and rec["data_hash"] == proposal_version):
                self._audit.append({
                    "action": "allow",
                    "via": "issued_approval",
                    "approval_id": approval_id,
                    "producer": producer,
                    "pid": pid,
                    "reviewer": rec["reviewer"],
                    "at": time.time(),
                })
                return {"allowed": True, "via": "issued_approval",
                        "approval_id": approval_id}
            # A dict that fails issuance verification is not silently
            # treated as "no context": record the forgery attempt signal.
            if approval_id is not None:
                self._audit.append({
                    "action": "deny",
                    "via": "unissued_approval",
                    "producer": producer,
                    "pid": pid,
                    "approval_id": approval_id,
                    "at": time.time(),
                })
                return {
                    "allowed": False,
                    "reason": "acceptance_policy_denied",
                    "detail": "Review context references no valid issued "
                              "approval in this session.",
                }

        # 2. Active scoped opt-in for this producer.
        if self.is_opted_in(producer):
            grant = self._opt_ins[producer]
            self._audit.append({
                "action": "allow",
                "via": "opt_in",
                "producer": producer,
                "pid": pid,
                "scope": grant["scope"],
                "at": time.time(),
            })
            return {"allowed": True, "via": "opt_in", "scope": grant["scope"]}

        # 3. Default: DENY.
        self._audit.append({
            "action": "deny",
            "producer": producer,
            "pid": pid,
            "at": time.time(),
        })
        return {
            "allowed": False,
            "reason": "acceptance_policy_denied",
            "detail": (
                f"Producer '{producer}' has no issued approval or active "
                f"opt-in for proposal '{pid}'. Acceptance requires explicit "
                f"human review or scoped session opt-in."
            ),
        }

    def audit_log(self) -> List[Dict[str, Any]]:
        """Return audit log (read-only copy)."""
        return [dict(entry) for entry in self._audit]

    def reset_session(self) -> None:
        """Clear opt-ins and issued approvals (e.g., on restart)."""
        self._opt_ins.clear()
        self._issued_approvals.clear()
        self._revoked_approvals.clear()
        self._session_id = f"session_{uuid.uuid4().hex}"
        self._audit.append({
            "action": "session_reset",
            "at": time.time(),
        })
