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
