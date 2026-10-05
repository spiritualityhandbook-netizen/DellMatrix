"""Acceptance policy for human-controlled confirmation.

Phase 5 (WO-5.1): Automated exploration can propose; acceptance requires
explicit human review or scoped session opt-in.

One policy check at the canonical acceptance boundary
(Program.confirm_proposal). Producers must carry explicit review/producer
context; permission is never inferred from owner prefixes, caller names,
prompts, or default flags.

Session-scoped opt-in: identifies scope/producer, expires at session end,
is visible, revocable, and audited. Recheck happens immediately before
commit; revocation invalidates approval.
"""

from __future__ import annotations
from typing import Dict, Any, Optional, List
import time


class AcceptancePolicy:
    """Session-scoped acceptance policy.

    Default: DENY. Producers must either:
    1. Provide explicit review context from a trusted public command, or
    2. Hold an active scoped opt-in for their producer ID.

    All decisions are audited. Opt-ins expire at session end and are
    revocable. Restart clears all opt-ins.
    """

    def __init__(self):
        # producer_id -> {"scope": str, "granted_at": float, "note": str}
        self._opt_ins: Dict[str, Dict[str, Any]] = {}
        self._audit: List[Dict[str, Any]] = []
        self._session_id = f"session_{int(time.time() * 1000)}"

    @property
    def session_id(self) -> str:
        return self._session_id

    def grant_opt_in(self, producer: str, scope: str,
                     note: str = "") -> Dict[str, Any]:
        """Grant scoped opt-in. Visible, revocable, audited.

        Args:
            producer: Producer ID (e.g., "auto_growth", "grow_auto").
            scope: Scope description (e.g., "session", "owner:Operator").
            note: Human-readable reason.

        Returns:
            Receipt dict with grant details.
        """
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

    def check(self, producer: str, pid: str,
              review_context: Optional[Dict[str, Any]] = None,
              proposal_version: Optional[str] = None) -> Dict[str, Any]:
        """Check if acceptance is allowed. Called immediately before commit.

        Args:
            producer: Producer ID attempting acceptance.
            pid: Proposal ID.
            review_context: Explicit review proof from trusted command.
                Must contain "reviewer" (nonempty str), "approved_pid" == pid,
                "session_id" == this policy's session_id, and
                "proposal_version" == proposal_version.
            proposal_version: Current version/content hash of the proposal.
                The review is only valid if it matches what was reviewed.

        Returns:
            {"allowed": bool, "reason": str, ...}
        """
        # 1. Explicit review context from trusted public command.
        # Director 2026-10-05: Bind to session and proposal version.
        if isinstance(review_context, dict):
            reviewer = review_context.get("reviewer")
            approved_pid = review_context.get("approved_pid")
            ctx_session = review_context.get("session_id")
            ctx_version = review_context.get("proposal_version")
            if (isinstance(reviewer, str) and reviewer and
                    approved_pid == pid and
                    ctx_session == self._session_id and
                    ctx_version is not None and
                    ctx_version == proposal_version):
                self._audit.append({
                    "action": "allow",
                    "via": "review_context",
                    "producer": producer,
                    "pid": pid,
                    "reviewer": reviewer,
                    "at": time.time(),
                })
                return {"allowed": True, "via": "review_context"}

        # 2. Active scoped opt-in for this producer.
        grant = self._opt_ins.get(producer)
        if grant is not None:
            # Recheck: grant must be for this session.
            if grant.get("session_id") == self._session_id:
                self._audit.append({
                    "action": "allow",
                    "via": "opt_in",
                    "producer": producer,
                    "pid": pid,
                    "scope": grant["scope"],
                    "at": time.time(),
                })
                return {"allowed": True, "via": "opt_in",
                        "scope": grant["scope"]}

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
                f"Producer '{producer}' has no review context or active "
                f"opt-in for proposal '{pid}'. Acceptance requires explicit "
                f"human review or scoped session opt-in."
            ),
        }

    def audit_log(self) -> List[Dict[str, Any]]:
        """Return audit log (read-only copy)."""
        return [dict(entry) for entry in self._audit]

    def reset_session(self) -> None:
        """Clear all opt-ins (e.g., on restart). Audit preserved."""
        self._opt_ins.clear()
        self._session_id = f"session_{int(time.time() * 1000)}"
        self._audit.append({
            "action": "session_reset",
            "at": time.time(),
        })
