"""R6.3 trusted authority-bound rollback (GDP_PHASE_6_R63_AUTHORITY_BOUND_ROLLBACK).

This module is the TRUSTED side of the rollback authority circuit. It
generalizes the R6.1 capability pattern (bound confirmation endpoint)
to checkpoint rollback — a destructive operation reachable today with
zero authority via REPL "revert"/"restore" and direct calls.

Threat boundary (declared mediated-interface boundary):
- Untrusted rollback requests arrive with (generation_id, grant_handle).
  Owner, subject, issuer, review context, and internal authorization
  cannot be substituted through the request: the endpoint binds them
  from trusted host state at creation.
- The restore target is FROZEN before any safety checkpoint: CURRENT
  is resolved once to an exact generation id; the manifest fingerprint
  and member hashes are bound. A moving pointer or pathname is never
  the authorization target.
- This does not defend against malicious Python with unrestricted
  host/process access, nor against concurrent races (explicitly out
  of scope).

All authorization decisions remain owned by AcceptancePolicy; this
module only delegates to it. No second permission store.
"""

from __future__ import annotations
from typing import Any, Dict, Optional


ROLLBACK_OPERATION = "checkpoint.rollback"


class RollbackTargetError(Exception):
    """The restore target cannot be frozen (missing/corrupt generation)."""


def freeze_rollback_target(owner: str,
                           generation_id: Optional[str] = None) -> Dict[str, Any]:
    """Resolve and freeze the restore target.

    CURRENT is resolved ONCE here, before any safety checkpoint is
    created. The returned record binds: owner, exact generation id,
    manifest fingerprint, and verified member identities/hashes.

    Validation/staging is private with activation disabled: nothing
    live is touched. Raises RollbackTargetError when no committed
    generation exists or the target fails validation.
    """
    import os
    from form.mandell import checkpoint_generation as gen

    if not isinstance(owner, str) or not owner:
        raise RollbackTargetError("owner must be non-empty str")
    # Resolve CURRENT once. An explicit generation id is used as-is
    # (validated below); None means the committed CURRENT generation.
    if generation_id is None:
        try:
            gid = gen._read_pointer(owner).get("generation_id")
        except Exception as exc:
            raise RollbackTargetError(
                f"no committed generation for owner {owner!r}: {exc}"
            ) from exc
        if not gid:
            raise RollbackTargetError(
                f"CURRENT pointer names no generation for {owner!r}")
    else:
        if not isinstance(generation_id, str) or not generation_id:
            raise RollbackTargetError(
                "generation_id must be non-empty str or None")
        gid = generation_id
    # Read and validate the manifest; verify every member file exists
    # and matches its sealed sha256 fingerprint.
    try:
        manifest = gen._read_manifest(owner, gid)
    except Exception as exc:
        raise RollbackTargetError(
            f"generation {gid!r} unreadable: {exc}") from exc
    members = manifest.get("members") or {}
    if not isinstance(members, dict) or not members:
        raise RollbackTargetError(
            f"generation {gid!r} has no members")
    from form.persist import _STATE_DIR
    frozen_members: Dict[str, str] = {}
    for kind, spec in members.items():
        if not isinstance(spec, dict):
            raise RollbackTargetError(
                f"generation {gid!r} member {kind!r} malformed")
        sha = spec.get("sha256")
        fname = spec.get("file")
        if not sha or not fname:
            raise RollbackTargetError(
                f"generation {gid!r} member {kind!r} missing fingerprint")
        mpath = os.path.join(_STATE_DIR, fname)
        if not os.path.isfile(mpath):
            raise RollbackTargetError(
                f"generation {gid!r} member {kind!r} file absent")
        # Re-hash: the sealed fingerprint must match the bytes now.
        import hashlib
        h = hashlib.sha256()
        with open(mpath, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        if h.hexdigest() != sha:
            raise RollbackTargetError(
                f"generation {gid!r} member {kind!r} fingerprint mismatch")
        frozen_members[kind] = sha
    # Private staging with activation disabled: proves the generation
    # loads without touching live state.
    try:
        gen._load_generation(owner, gid, False, None)
    except Exception as exc:
        raise RollbackTargetError(
            f"generation {gid!r} failed private staging: {exc}") from exc
    return {
        "owner": owner,
        "generation_id": gid,
        "members": frozen_members,
    }


def _live_fingerprints(owner: str) -> Dict[str, str]:
    """Non-secret live-state fingerprints for content binding."""
    from form.persist import _path, _STATE_DIR, _safe_owner
    from form.dell_matrix.nursery import owner_nursery_path
    import hashlib
    import os
    out: Dict[str, str] = {}
    for name, path in (("program", _path(owner)),
                       ("nursery", owner_nursery_path(owner))):
        try:
            h = hashlib.sha256()
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    h.update(chunk)
            out[name] = h.hexdigest()
        except OSError:
            out[name] = "absent"
    return out


def rollback_content(frozen_target: Dict[str, Any],
                     live_fingerprints: Dict[str, str]) -> Dict[str, Any]:
    """Canonical content bound into a rollback grant.

    Binds BOTH the frozen target generation AND the live state at
    issuance. Drift in either denies at execution (fail closed).
    """
    return {
        "target_generation": {
            "generation_id": frozen_target["generation_id"],
            "members": dict(frozen_target["members"]),
        },
        "live_at_issuance": dict(live_fingerprints),
    }


def issue_rollback_grant(program: Any, *, issuer: str, subject: str,
                         frozen_target: Dict[str, Any],
                         max_depth: int = 1,
                         note: str = "") -> Dict[str, Any]:
    """Issue a rollback capability grant. TRUSTED HUMAN/CONTROLLER ONLY.

    Never expose to agent-reachable interfaces. The grant_id is the
    secret handle: deliver out-of-band; never log it.

    `frozen_target` must come from freeze_rollback_target(). The grant
    binds operation="checkpoint.rollback", the exact generation id as
    target, and the canonical content hash (target + live fingerprints).
    checkpoint.rollback is never interchangeable with nursery.confirm:
    _check_grant denies on operation mismatch.
    """
    from form.dell_matrix.acceptance_policy import canonical_hash
    policy = getattr(program, "acceptance_policy", None)
    if policy is None:
        raise RuntimeError("acceptance policy missing")
    if not isinstance(frozen_target, dict):
        raise ValueError("frozen_target must come from freeze_rollback_target()")
    if frozen_target.get("owner") != getattr(program, "owner", None):
        raise ValueError("frozen_target owner mismatch")
    content = rollback_content(frozen_target,
                               _live_fingerprints(program.owner))
    return policy.issue_grant(
        issuer=issuer, subject=subject, owner=getattr(program, "owner", ""),
        operation=ROLLBACK_OPERATION,
        target=frozen_target["generation_id"],
        content=content, max_depth=max_depth, note=note)


def agent_rollback(program: Any, generation_id: str, grant_id: str,
                   subject: str) -> Dict[str, Any]:
    """Mediated rollback entry. The trust boundary.

    `subject` is established by the TRUSTED dispatcher — never from the
    agent's payload. Delegates to the program's mediated rollback,
    which performs entry check → safety checkpoint → intent journal →
    live revalidation → canonical rollback.
    """
    return program.confirm_rollback(
        generation_id,
        _review_context={"grant_id": grant_id},
        _subject=subject,
    )


class RollbackEndpoint:
    """Host-created subject-bound rollback endpoint.

    Created ONLY by the trusted host via bind_rollback_agent(). The
    subject and owner are bound at creation from trusted host state;
    the agent request surface exposes exactly one method:

        rollback(generation_id, grant_handle)

    The surface accepts NO subject, issuer, owner, review context, or
    internal authorization parameters. Identity substitution through
    the payload is impossible by construction.

    Mint/attenuate/revoke functions are NOT on this surface.
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

    def rollback(self, generation_id: Optional[str],
                 grant_handle: str) -> Dict[str, Any]:
        """Agent request: roll back to generation_id presenting a grant.

        Only the generation id and the handle cross the boundary.
        generation_id=None means the committed CURRENT generation as
        frozen at execution (resolved once inside mediation).
        """
        if generation_id is not None and (
                not isinstance(generation_id, str) or not generation_id):
            return {"ok": False, "reason": "acceptance_policy_denied",
                    "detail": "Endpoint: generation_id must be non-empty "
                             "str or None."}
        if not isinstance(grant_handle, str) or not grant_handle:
            return {"ok": False, "reason": "acceptance_policy_denied",
                    "detail": "Endpoint: grant handle must be non-empty str."}
        return self._program.confirm_rollback(
            generation_id,
            _review_context={"grant_id": grant_handle},
            _subject=self._subject,
        )


def bind_rollback_agent(program: Any, trusted_subject: str) -> RollbackEndpoint:
    """Create a subject-bound rollback endpoint. TRUSTED HOST ONLY.

    `trusted_subject` is established by the host (e.g. the agent
    framework's authenticated identity), never by agent payload text.
    """
    return RollbackEndpoint(program, trusted_subject)
