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

Phase 6 R6.1 (GDP_PHASE_6_CAPABILITY_AUTHORITY_CIRCUIT, Director
2026-10-07): capability grants for agent authority. The policy remains
the SINGLE owner of acceptance authorization; grants extend (not
duplicate) the existing issuance, session, source-chain and revocation
machinery.

Grant model:
- A grant is an opaque, high-entropy, session-scoped issued handle
  ("grant_<uuid4hex>") backed by a canonical issuance record. No custom
  cryptographic token format. Copied/edited dictionaries and
  caller-supplied identities confer nothing: check() verifies the handle
  against the issuance record.
- Root grants are issued ONLY through the trusted human/controller path
  (issue_grant). Agent-facing interfaces expose specifically authorized
  operations and attenuation -- never root minting, policy internals, or
  credential listings.
- Grants bind: issuer, session, trusted subject, owner, operation,
  target/content, parent grant, and permitted delegation depth.
- Attenuation (attenuate_grant) may only NARROW authority. Expansion,
  foreign sessions/owners, invalid parents, malformed constraints,
  cycles, and excessive chain depth are rejected.
- Revoking any ancestor denies unfinished descendants at execution
  time. Already committed history is not retroactively erased.
- The trusted subject is bound at issuance and re-validated at every
  check against the dispatch-bound subject. Caller-supplied identity
  strings (e.g. _producer) never satisfy the subject binding.
- Audit entries reference grants by issuance sequence number, never by
  handle value. Handles are secrets; they are not logged.

Threat boundary: this protects untrusted agent requests arriving through
mediated interfaces. It does not claim protection against malicious
Python with unrestricted access to the host process, policy memory, or
filesystem.
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

    # R6.1: the only grantable capability in this circuit.
    GRANT_OPERATION = "nursery.confirm"
    # R6.3: frozen allowlist of grantable operations. checkpoint.rollback
    # is never interchangeable with nursery.confirm: issuance, checking,
    # attenuation, audit, and revocation all carry the operation string,
    # and _check_grant denies on operation mismatch.
    GRANTABLE_OPERATIONS = frozenset({"nursery.confirm", "checkpoint.rollback"})
    # R6.1: bound on delegation chain length (excessive depth rejected).
    MAX_GRANT_DEPTH = 8

    def __init__(self):
        # producer_id -> grant record
        self._opt_ins: Dict[str, Dict[str, Any]] = {}
        # approval_id -> issuance record
        self._issued_approvals: Dict[str, Dict[str, Any]] = {}
        self._revoked_approvals: set = set()
        # R6.1: grant_id -> grant issuance record (opaque handles).
        self._issued_grants: Dict[str, Dict[str, Any]] = {}
        self._revoked_grants: set = set()
        # R6.1: issuance sequence; audit references grants by seq, never
        # by handle value.
        self._grant_seq: int = 0
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
            # Full data retained for derivation relationship verification.
            # (Director 2026-10-05 final: derived approvals must prove
            # their relationship to the source's approved payload.)
            "data": dict(data),
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
                        relationship: Mapping[str, Any],
                        note: str = "") -> Dict[str, Any]:
        """Derive a scoped approval from an approved enclosing operation.

        Director 2026-10-05 (final): derivation is CONSTRAINED to explicit
        permitted relationships. An ordinary approval cannot authorize
        arbitrary derivation.

        Currently permitted:
        - {"type": "supersede_successor", "predecessor_id": old_id}:
          source must be a "supersede" approval for predecessor_id (or an
          active opt-in with the same relationship declared); the derived
          operation must be "confirm"; the derived target's content must
          match the source's approved successor payload.

        The derived approval records its source chain. At execution time,
        check() re-validates the chain: a revoked parent approval or a
        revoked source opt-in invalidates an unfinished child.
        """
        rel_type = relationship.get("type") if isinstance(relationship, Mapping) else None
        if rel_type != "supersede_successor":
            raise ApprovalError(
                f"derive_approval: relationship type {rel_type!r} not permitted")
        predecessor_id = relationship.get("predecessor_id")
        if not predecessor_id:
            raise ApprovalError("derive_approval: predecessor_id required")
        if operation != "confirm":
            raise ApprovalError(
                "derive_approval: supersede_successor permits only confirm")

        if source_approval_id:
            src = self._issued_approvals.get(source_approval_id)
            if (not src or source_approval_id in self._revoked_approvals
                    or src["session_id"] != self._session_id):
                raise ApprovalError("source approval invalid/revoked/foreign")
            if src["operation"] != "supersede" or src["target"] != predecessor_id:
                raise ApprovalError(
                    "derive_approval: source is not a supersede approval "
                    f"for {predecessor_id!r}")
            # Bind to the approved successor payload: the derived target's
            # content must match what the enclosing operation approved.
            approved_succ = (src.get("data") or {}).get("successor")
            content = (data.get("content") or {}) if isinstance(data, Mapping) else {}
            derived_succ = canonical_hash({
                "label": content.get("label", ""),
                "words": content.get("words", ""),
            })
            if not approved_succ or derived_succ != approved_succ:
                raise ApprovalError(
                    "derive_approval: derived content does not match the "
                    "approved successor payload")
            from_note = f"derived from {source_approval_id}"
            derived_from = source_approval_id
        elif source_opt_in:
            if not self.is_opted_in(source_opt_in):
                raise ApprovalError("source opt-in not active")
            from_note = f"derived from opt_in:{source_opt_in}"
            derived_from = f"opt_in:{source_opt_in}"
        else:
            raise ApprovalError("derive_approval requires a source")
        note = (note + " " + from_note).strip()[:200]
        result = self.issue_approval(operation=operation, target=target,
                                     reviewer=reviewer, data=data,
                                     producer=source_opt_in, note=note)
        result["record"]["derived_from"] = derived_from
        result["record"]["relationship"] = dict(relationship)
        self._issued_approvals[result["approval_id"]] = result["record"]
        self._audit.append({
            "action": "derive",
            "approval_id": result["approval_id"],
            "derived_from": derived_from,
            "relationship": rel_type,
            "at": time.time(),
        })
        return result

    # -- R6.1 capability grants ---------------------------------------

    def _next_grant_seq(self) -> int:
        self._grant_seq += 1
        return self._grant_seq

    def _validate_grant_fields(self, *, issuer: str, subject: str, owner: str,
                               operation: str, target: Optional[str],
                               content: Optional[Mapping[str, Any]],
                               max_depth: int) -> Optional[str]:
        """Return an error string for malformed grant fields, else None."""
        for name, val in (("issuer", issuer), ("subject", subject),
                          ("owner", owner)):
            if not isinstance(val, str) or not val:
                return f"{name} must be non-empty str"
            if len(val) > 200:
                return f"{name} exceeds 200 chars"
        if operation not in self.GRANTABLE_OPERATIONS:
            return (f"operation {operation!r} not grantable in this circuit "
                    f"(grantable: {sorted(self.GRANTABLE_OPERATIONS)!r})")
        if target is not None and (not isinstance(target, str) or not target):
            return "target must be None or non-empty str"
        if content is not None and not isinstance(content, Mapping):
            return "content must be None or a mapping"
        if (not isinstance(max_depth, int) or isinstance(max_depth, bool)
                or not (0 <= max_depth <= self.MAX_GRANT_DEPTH)):
            return (f"max_depth must be int in [0, {self.MAX_GRANT_DEPTH}]")
        return None

    def issue_grant(self, *, issuer: str, subject: str, owner: str,
                    operation: str = GRANT_OPERATION,
                    target: Optional[str] = None,
                    content: Optional[Mapping[str, Any]] = None,
                    max_depth: int = 1,
                    note: str = "") -> Dict[str, Any]:
        """Issue a root capability grant. TRUSTED PATH ONLY.

        Called exclusively by the human/controller path to authorize an
        agent subject. Returns the opaque handle (grant_id) plus a
        non-secret descriptor. The handle is the credential: it is
        returned to the caller and never logged.

        Binds: issuer, session, trusted subject, owner, operation,
        target/content, and permitted delegation depth. Roots have no
        parent. Use attenuate_grant for narrowed children.

        Content semantics (Director 2026-10-07 AMEND: absence vs empty):
        content=None means UNCONSTRAINED (documented positive — the grant
        authorizes the operation on the target regardless of content).
        Every valid supplied Mapping — including {} — is hashed and
        bound; execution then requires an exact hash match.
        """
        err = self._validate_grant_fields(
            issuer=issuer, subject=subject, owner=owner, operation=operation,
            target=target, content=content, max_depth=max_depth)
        if err:
            raise ApprovalError(f"issue_grant: {err}")
        grant_id = f"grant_{uuid.uuid4().hex}"
        seq = self._next_grant_seq()
        record = {
            "grant_id": grant_id,
            "kind": "grant",
            "seq": seq,
            "issuer": issuer,
            "session_id": self._session_id,
            "subject": subject,
            "owner": owner,
            "operation": operation,
            "target": target,
            # Director 2026-10-07 AMEND: explicit absence handling. None
            # = unconstrained; {} (and every valid Mapping) is hashed.
            "content_hash": (canonical_hash(content)
                             if content is not None else None),
            "parent_id": None,
            "max_depth": max_depth,
            "issued_at": time.time(),
            "note": note[:200] if isinstance(note, str) else "",
        }
        self._issued_grants[grant_id] = record
        self._audit.append({
            "action": "grant_issue",
            "grant_seq": seq,
            "issuer": issuer,
            "subject": subject,
            "owner": owner,
            "operation": operation,
            "at": record["issued_at"],
        })
        return {"ok": True, "grant_id": grant_id,
                "descriptor": {"seq": seq, "operation": operation,
                               "subject": subject, "owner": owner,
                               "target": target}}

    def _grant_ancestors(self, record: Mapping[str, Any]) -> List[str]:
        """Ancestor grant_ids from parent upward. Cycle-safe."""
        out: List[str] = []
        seen = {record.get("grant_id")}
        cur = record.get("parent_id")
        while cur:
            if cur in seen:
                break
            seen.add(cur)
            out.append(cur)
            parent = self._issued_grants.get(cur)
            cur = parent.get("parent_id") if parent else None
        return out

    def attenuate_grant(self, *, parent_id: str,
                        subject: Optional[str] = None,
                        owner: Optional[str] = None,
                        target: Optional[str] = None,
                        content: Optional[Mapping[str, Any]] = None,
                        max_depth: Optional[int] = None,
                        note: str = "") -> Dict[str, Any]:
        """Derive a NARROWED child grant. Attenuation only.

        The child may only narrow the parent's authority:
        - subject/owner/operation: must equal the parent's (identity and
          scope are not reassignable by the holder).
        - target: parent None -> child may bind a specific target;
          parent specific -> child must match it exactly.
        - content: parent unbound -> child may bind; parent bound ->
          child must match.
        - max_depth: must be strictly less than the parent's remaining
          depth (each attenuation consumes delegation budget); the
          parent must permit delegation (max_depth >= 1).

        Rejects: unknown/revoked/foreign-session parents, invalid
        ancestor chains, expansion, cycles, excessive depth, malformed
        constraints. Raises ApprovalError on any violation.
        """
        if not isinstance(parent_id, str) or not parent_id:
            raise ApprovalError("attenuate_grant: parent_id required")
        parent = self._issued_grants.get(parent_id)
        if parent is None:
            raise ApprovalError("attenuate_grant: unknown parent grant")
        if parent_id in self._revoked_grants:
            raise ApprovalError("attenuate_grant: parent grant revoked")
        if parent.get("session_id") != self._session_id:
            raise ApprovalError("attenuate_grant: foreign session parent")
        if not self._grant_chain_valid(parent):
            raise ApprovalError("attenuate_grant: parent chain invalid")
        if parent.get("max_depth", 0) < 1:
            raise ApprovalError(
                "attenuate_grant: parent permits no delegation")
        ancestors = self._grant_ancestors(parent)
        if len(ancestors) + 1 >= self.MAX_GRANT_DEPTH:
            raise ApprovalError("attenuate_grant: excessive chain depth")

        eff_subject = parent["subject"] if subject is None else subject
        eff_owner = parent["owner"] if owner is None else owner
        if eff_subject != parent["subject"]:
            raise ApprovalError(
                "attenuate_grant: subject reassignment is expansion")
        if eff_owner != parent["owner"]:
            raise ApprovalError(
                "attenuate_grant: owner reassignment is expansion")
        if parent["target"] is not None:
            if target is not None and target != parent["target"]:
                raise ApprovalError(
                    "attenuate_grant: target widening is expansion")
            eff_target = parent["target"]
        else:
            if target is not None and (
                    not isinstance(target, str) or not target):
                raise ApprovalError(
                    "attenuate_grant: malformed target constraint")
            eff_target = target
        parent_hash = parent.get("content_hash")
        if parent_hash is not None:
            if content is not None and canonical_hash(content) != parent_hash:
                raise ApprovalError(
                    "attenuate_grant: content rebinding is expansion")
            eff_content_hash = parent_hash
        else:
            if content is not None and not isinstance(content, Mapping):
                raise ApprovalError(
                    "attenuate_grant: malformed content constraint")
            eff_content_hash = (canonical_hash(content)
                                if content is not None else None)
        if max_depth is None:
            eff_depth = parent["max_depth"] - 1
        else:
            if (not isinstance(max_depth, int) or isinstance(max_depth, bool)
                    or not (0 <= max_depth < parent["max_depth"])):
                raise ApprovalError(
                    "attenuate_grant: max_depth must be strictly less "
                    "than the parent's remaining depth")
            eff_depth = max_depth

        grant_id = f"grant_{uuid.uuid4().hex}"
        seq = self._next_grant_seq()
        record = {
            "grant_id": grant_id,
            "kind": "grant",
            "seq": seq,
            "issuer": parent["issuer"],
            "session_id": self._session_id,
            "subject": eff_subject,
            "owner": eff_owner,
            "operation": parent["operation"],
            "target": eff_target,
            "content_hash": eff_content_hash,
            "parent_id": parent_id,
            "max_depth": eff_depth,
            "issued_at": time.time(),
            "note": note[:200] if isinstance(note, str) else "",
        }
        self._issued_grants[grant_id] = record
        self._audit.append({
            "action": "grant_attenuate",
            "grant_seq": seq,
            "parent_seq": parent.get("seq"),
            "subject": eff_subject,
            "owner": eff_owner,
            "operation": record["operation"],
            "at": record["issued_at"],
        })
        return {"ok": True, "grant_id": grant_id,
                "descriptor": {"seq": seq, "operation": record["operation"],
                               "subject": eff_subject, "owner": eff_owner,
                               "target": eff_target,
                               "parent_seq": parent.get("seq")}}

    def revoke_grant(self, grant_id: str) -> Dict[str, Any]:
        """Revoke a grant. Unfinished descendants deny via chain check.

        Already committed history is not retroactively erased; revocation
        gates future checks only. Audited by sequence number, never by
        handle value.
        """
        existed = grant_id in self._issued_grants
        seq = (self._issued_grants[grant_id].get("seq")
               if existed else None)
        if existed:
            self._revoked_grants.add(grant_id)
        self._audit.append({
            "action": "grant_revoke",
            "grant_seq": seq,
            "at": time.time(),
            "existed": existed,
        })
        return {"ok": True, "revoked": existed}

    def describe_grants(self) -> List[Dict[str, Any]]:
        """Trusted-operator visibility: active grants WITHOUT handles."""
        return [
            {"seq": r.get("seq"), "issuer": r.get("issuer"),
             "subject": r.get("subject"), "owner": r.get("owner"),
             "operation": r.get("operation"), "target": r.get("target"),
             "parent_seq": (self._issued_grants.get(r.get("parent_id"), {})
                            .get("seq") if r.get("parent_id") else None),
             "max_depth": r.get("max_depth"),
             "issued_at": r.get("issued_at")}
            for gid, r in self._issued_grants.items()
            if gid not in self._revoked_grants
        ]

    def _grant_chain_valid(self, record: Mapping[str, Any],
                           _seen: Optional[set] = None) -> bool:
        """Recursively validate the full ancestor chain at execution time.

        Every ancestor must be issued, unrevoked, and in this session.
        Cycles and missing parents invalidate. Already committed outcomes
        are not retroactively undone -- this gates future checks.
        """
        seen = _seen if _seen is not None else set()
        gid = record.get("grant_id")
        if not gid or gid in seen:
            return False
        seen.add(gid)
        if gid in self._revoked_grants:
            return False
        if record.get("session_id") != self._session_id:
            return False
        parent_id = record.get("parent_id")
        if not parent_id:
            return True
        parent = self._issued_grants.get(parent_id)
        if parent is None:
            return False
        return self._grant_chain_valid(parent, seen)

    def _check_grant(self, producer: str, pid: str, grant_id: Any,
                     proposal_version: Optional[str], operation: str,
                     subject: Optional[str],
                     owner: Optional[str]) -> Dict[str, Any]:
        """Execution-time grant validation. Never raises."""
        def deny(detail: str, via: str) -> Dict[str, Any]:
            self._audit.append({
                "action": "deny",
                "via": via,
                "producer": producer,
                "pid": pid,
                "at": time.time(),
            })
            return {"allowed": False, "reason": "acceptance_policy_denied",
                    "detail": detail}

        rec = (self._issued_grants.get(grant_id)
               if isinstance(grant_id, str) and grant_id else None)
        if rec is None:
            return deny("Grant references no issued grant in this session.",
                        "unissued_grant")
        if grant_id in self._revoked_grants:
            return deny("Grant has been revoked.", "revoked_grant")
        if rec.get("session_id") != self._session_id:
            return deny("Grant belongs to a foreign session.",
                        "foreign_session_grant")
        if not self._grant_chain_valid(rec):
            return deny("Grant's ancestor chain is invalid "
                        "(ancestor revoked or missing).",
                        "revoked_grant_chain")
        # Trusted subject binding: the dispatcher must bind the actual
        # caller identity. A missing binding or a mismatch denies; a
        # caller-supplied identity string never satisfies this.
        if not isinstance(subject, str) or not subject:
            return deny("Grant requires a trusted subject binding.",
                        "unbound_subject_grant")
        if subject != rec.get("subject"):
            return deny("Grant subject mismatch.", "subject_mismatch_grant")
        if not isinstance(owner, str) or not owner:
            return deny("Grant requires an owner scope.", "unbound_owner")
        if owner != rec.get("owner"):
            return deny("Grant owner mismatch.", "owner_mismatch_grant")
        want_op = ("nursery.confirm" if operation == "confirm"
                   else operation)
        if want_op != rec.get("operation"):
            return deny("Grant operation mismatch.", "operation_mismatch")
        if rec.get("target") is not None and rec["target"] != pid:
            return deny("Grant target mismatch.", "target_mismatch_grant")
        if (rec.get("content_hash") is not None
                and rec["content_hash"] != proposal_version):
            return deny("Reviewed content changed after grant issuance.",
                        "content_mismatch_grant")
        self._audit.append({
            "action": "allow",
            "via": "grant",
            "grant_seq": rec.get("seq"),
            "producer": producer,
            "pid": pid,
            "subject": subject,
            "at": time.time(),
        })
        return {"allowed": True, "via": "grant",
                "grant_seq": rec.get("seq")}

    def _source_chain_valid(self, record: Mapping[str, Any]) -> bool:
        """Validate a derived approval's source chain at execution time.

        Director 2026-10-05 (final): a revoked parent approval or a
        revoked source opt-in invalidates an unfinished child. Already
        committed outcomes are not retroactively undone (revocation only
        gates future checks).
        """
        derived_from = record.get("derived_from")
        if not derived_from:
            return True  # not derived; nothing to re-validate
        if derived_from.startswith("opt_in:"):
            producer = derived_from[len("opt_in:"):]
            return self.is_opted_in(producer)
        src = self._issued_approvals.get(derived_from)
        return bool(src
                    and derived_from not in self._revoked_approvals
                    and src["session_id"] == self._session_id)

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
              operation: str = "confirm",
              subject: Optional[str] = None,
              owner: Optional[str] = None) -> Dict[str, Any]:
        """Check if acceptance is allowed. Called at the commit boundary.

        The review context must reference an approval ISSUED by this policy
        session (verified against the issuance record — a matching dict
        alone is insufficient), not revoked, with matching operation,
        target, session, and data hash.

        R6.1: a review context carrying "grant_id" routes to grant
        validation. Grants additionally require the dispatch-bound
        trusted subject and the owner scope; both are established by
        trusted code, never by caller-supplied strings.
        """
        # 0. R6.1 capability-grant context. One decision owner: the grant
        #    branch lives inside check(), sharing session/audit machinery.
        if (isinstance(review_context, dict)
                and review_context.get("grant_id")):
            return self._check_grant(producer, pid,
                                     review_context.get("grant_id"),
                                     proposal_version, operation,
                                     subject=subject, owner=owner)
        # 1. Issued-approval review context.
        if isinstance(review_context, dict):
            approval_id = review_context.get("approval_id")
            rec = self._issued_approvals.get(approval_id) if approval_id else None
            if (rec is not None
                    and approval_id not in self._revoked_approvals
                    and rec["session_id"] == self._session_id
                    and rec["operation"] == operation
                    and rec["target"] == pid
                    and rec["data_hash"] == proposal_version
                    and self._source_chain_valid(rec)):
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
            # Derived approval whose source chain is now invalid (parent
            # revoked or opt-in revoked): deny explicitly.
            if (rec is not None
                    and approval_id not in self._revoked_approvals
                    and rec.get("derived_from")
                    and not self._source_chain_valid(rec)):
                self._audit.append({
                    "action": "deny",
                    "via": "revoked_source_chain",
                    "producer": producer,
                    "pid": pid,
                    "approval_id": approval_id,
                    "at": time.time(),
                })
                return {
                    "allowed": False,
                    "reason": "acceptance_policy_denied",
                    "detail": "Derived approval's source was revoked.",
                }
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
        """Clear opt-ins, issued approvals, and issued grants.

        R6.1: session reset invalidates session grants (they are not
        re-issued); durable Ideas are untouched.
        """
        self._opt_ins.clear()
        self._issued_approvals.clear()
        self._revoked_approvals.clear()
        self._issued_grants.clear()
        self._revoked_grants.clear()
        self._session_id = f"session_{uuid.uuid4().hex}"
        self._audit.append({
            "action": "session_reset",
            "at": time.time(),
        })
