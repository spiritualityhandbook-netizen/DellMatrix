"""R6.1 trusted agent-authority dispatch (GDP_PHASE_6_CAPABILITY_AUTHORITY_CIRCUIT).

This module is the TRUSTED side of the agent authority circuit. It does
not grant agents any new power to authorize themselves; it gives the
human/controller layer a small, explicit surface to:

- issue root capability grants (issue_root_grant),
- narrow them for a specific agent task (attenuate_for),
- dispatch an agent's confirm request with the caller identity bound by
  trusted code, not by the agent's payload (agent_confirm).

Threat boundary: untrusted agent requests arrive through agent_confirm
with (pid, grant_handle). The subject is established by the trusted
dispatcher and checked against the grant's issuance record. Agents
cannot mint grants, list credentials, or widen scope. This does not
defend against malicious Python with unrestricted host/process access.

All authorization decisions remain owned by AcceptancePolicy; this
module only delegates to it.
"""

from __future__ import annotations
from typing import Any, Dict, Optional, Mapping


def issue_root_grant(program: Any, *, issuer: str, subject: str,
                     target: Optional[str] = None,
                     content_pid: Optional[str] = None,
                     max_depth: int = 1,
                     note: str = "") -> Dict[str, Any]:
    """Issue a root capability grant. TRUSTED HUMAN/CONTROLLER PATH ONLY.

    Never expose this to agent-reachable interfaces. The returned
    grant_id is the secret handle: deliver it to the authorized subject
    through a trusted out-of-band path; it is never logged.

    If content_pid is given, the grant binds the canonical acceptance
    data hash of that live proposal (content mismatch at execution
    denies).
    """
    policy = getattr(program, "acceptance_policy", None)
    if policy is None:
        raise RuntimeError("acceptance policy missing")
    content = None
    if content_pid is not None:
        content = program._acceptance_data_for(content_pid, "confirm")
    return policy.issue_grant(
        issuer=issuer, subject=subject, owner=getattr(program, "owner", ""),
        operation="nursery.confirm", target=target, content=content,
        max_depth=max_depth, note=note)


def attenuate_for(program: Any, parent_grant_id: str, *,
                  target: Optional[str] = None,
                  content_pid: Optional[str] = None,
                  max_depth: Optional[int] = None,
                  note: str = "") -> Dict[str, Any]:
    """Narrow a grant for a specific task. Trusted path; attenuation only.

    Subject/owner/operation are inherited (never reassigned). Raises
    ApprovalError on any expansion attempt.
    """
    policy = getattr(program, "acceptance_policy", None)
    if policy is None:
        raise RuntimeError("acceptance policy missing")
    content = None
    if content_pid is not None:
        content = program._acceptance_data_for(content_pid, "confirm")
    return policy.attenuate_grant(
        parent_id=parent_grant_id, target=target, content=content,
        max_depth=max_depth, note=note)


def revoke_grant(program: Any, grant_id: str) -> Dict[str, Any]:
    """Revoke a grant (trusted path). Unfinished descendants deny."""
    policy = getattr(program, "acceptance_policy", None)
    if policy is None:
        raise RuntimeError("acceptance policy missing")
    return policy.revoke_grant(grant_id)


def agent_confirm(program: Any, pid: str, grant_id: str,
                  subject: str) -> Dict[str, Any]:
    """Mediated agent confirm entry. The trust boundary.

    `subject` is the agent identity established by the TRUSTED
    dispatcher -- it is not taken from the agent's request payload.
    The grant presented must have been issued for exactly this subject,
    owner, operation, and target/content scope; otherwise the canonical
    writer denies with no mutation.

    Returns the canonical confirm receipt (ok True/False). Denial
    performs no protected mutation or durable write.
    """
    return program.confirm_proposal(
        pid,
        _producer=f"agent:{subject}",
        _review_context={"grant_id": grant_id},
        _operation="confirm",
        _subject=subject,
    )


class AgentEndpoint:
    """Host-created subject-bound agent endpoint (Director 2026-10-07).

    Created ONLY by the trusted host via bind_agent(). The subject,
    owner, and operation are bound at creation from trusted host state;
    the agent request surface exposes exactly one method:

        confirm(pid, grant_handle)

    The surface accepts NO subject, issuer, producer, review context,
    _auth, or arbitrary forwarded kwargs. Identity substitution through
    the payload is impossible by construction: there is no parameter
    to substitute through.

    Mint/revoke/controller functions (issue_root_grant, attenuate_for,
    revoke_grant, describe_grants) are NOT on this surface.

    This is local mediated-request enforcement. It does not authenticate
    strings by itself and does not protect against arbitrary malicious
    Python inside the trusted host.
    """

    __slots__ = ("_program", "_subject", "_owner")

    def __init__(self, program: Any, trusted_subject: str):
        if not isinstance(trusted_subject, str) or not trusted_subject:
            raise ValueError("trusted_subject must be non-empty str")
        if len(trusted_subject) > 200:
            raise ValueError("trusted_subject exceeds 200 chars")
        object.__setattr__(self, "_program", program)
        object.__setattr__(self, "_subject", trusted_subject)
        object.__setattr__(self, "_owner",
                           getattr(program, "owner", None))

    @property
    def bound_subject(self) -> str:
        """The host-bound subject (read-only; for audit display)."""
        return self._subject

    def confirm(self, pid: str,
                grant_handle: str) -> Dict[str, Any]:
        """Agent request: confirm pid presenting a grant handle.

        Only pid and the handle cross the boundary. The subject is the
        host binding, never a request parameter.
        """
        if not isinstance(pid, str) or not pid:
            return {"ok": False, "reason": "acceptance_policy_denied",
                    "detail": "Endpoint: pid must be non-empty str.",
                    "pid": pid}
        if not isinstance(grant_handle, str) or not grant_handle:
            return {"ok": False, "reason": "acceptance_policy_denied",
                    "detail": "Endpoint: grant handle must be non-empty str.",
                    "pid": pid}
        return self._program.confirm_proposal(
            pid,
            _producer=f"agent:{self._subject}",
            _review_context={"grant_id": grant_handle},
            _operation="confirm",
            _subject=self._subject,
        )


def bind_agent(program: Any, trusted_subject: str) -> AgentEndpoint:
    """Create a subject-bound agent endpoint. TRUSTED HOST ONLY.

    `trusted_subject` is established by the host (e.g. the agent
    framework's authenticated identity), never by agent payload text.
    The returned endpoint is the ONLY agent-facing request surface;
    it cannot mint, attenuate, revoke, or list grants.
    """
    return AgentEndpoint(program, trusted_subject)
