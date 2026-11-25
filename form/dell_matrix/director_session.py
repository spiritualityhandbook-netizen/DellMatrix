"""SD-4 (master plan P7) — the scoped Director role session.

A second, simultaneous dock with a least-privilege role: the
Director. It follows the agent_authority binding discipline
(host establishes the subject; the surface accepts no identity
parameters) but deliberately does NOT use the confirm-grant
machinery: the Director's "accept" is a RECOMMENDATION RECORD,
never a confirmation. AcceptancePolicy is untouched; the human
gate remains the sole decision owner.

Surface (the whole allowlist):

    snapshot()            the scope program's field snapshot
    review(pid)           one in-scope proposal, read-only
    recommend(pid, decision, reason)
                          decision in {"accept", "reject"}; writes
                          a director_records entry; changes NOTHING
    request_evidence(pid, what)
                          writes an evidence-request entry
    directive(text, reason="")
                          files a PENDING proposal through the
                          wrapped docked session (propose), and
                          records the link
    undock()              closes the wrapped session

Everything else — relate, synthesize, flag, raw propose, confirm,
grants — is absent from the surface by construction.

Scope is a checked invariant, not a convention: construction
requires a DockedSession whose program owner equals the declared
scope owner and whose bound subject carries the "director:"
prefix. Attempts against pids outside the scoped snapshot are
refused AND recorded (kind="refusal"): an expansion attempt
leaves evidence, never an effect.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from form.dell_matrix import director_records as _records

MAX_REASON_CHARS = 1000


class DirectorError(Exception):
    """Director binding or scope violation."""


class DirectorSession:
    """Host-bound scoped Director endpoint. Created ONLY by the
    trusted host via bind_director()."""

    __slots__ = ("_session", "_program", "_subject", "_scope_owner",
                 "_closed")

    def __init__(self, docked_session: Any, *, scope_owner: str):
        from form.dell_matrix.inference_dock import DockedSession
        if not isinstance(docked_session, DockedSession):
            raise DirectorError("Director requires a DockedSession")
        if not docked_session.is_docked:
            raise DirectorError("Director session is not docked")
        subject = docked_session.bound_subject
        if not subject.startswith("director:"):
            raise DirectorError(
                "Director subject must carry the 'director:' prefix")
        program = docked_session._program
        owner = getattr(program, "owner", None)
        if owner != scope_owner:
            raise DirectorError(
                f"scope owner mismatch: program owner {owner!r} "
                f"!= declared scope {scope_owner!r}")
        object.__setattr__(self, "_session", docked_session)
        object.__setattr__(self, "_program", program)
        object.__setattr__(self, "_subject", subject)
        object.__setattr__(self, "_scope_owner", scope_owner)
        object.__setattr__(self, "_closed", False)

    # -- read-only identity -------------------------------------------
    @property
    def bound_subject(self) -> str:
        return self._subject

    @property
    def scope_owner(self) -> str:
        return self._scope_owner

    @property
    def session_id(self) -> str:
        return self._session.session_id

    # -- internal helpers ----------------------------------------------
    def _is_closed(self) -> bool:
        """Director review repair (2026-10-28): the endpoint dies
        with its dock. Closed when this session undocked OR the
        wrapped docked session was undocked by any other path."""
        return bool(self._closed) or not self._session.is_docked

    def _closed_refusal(self, pid: Any = "") -> Dict[str, Any]:
        """Refusal for a closed session. Deliberately NOT recorded:
        after undock the endpoint performs no reads and no writes,
        not even refusal records."""
        return {"ok": False, "reason": "session_closed",
                "pid": pid if isinstance(pid, str) else ""}

    def _record(self, kind: str, *, pid: str = "", decision: str = "",
                reason: str = "", note: str = "") -> Dict[str, Any]:
        entry = _records.new_entry(
            self._scope_owner, self.session_id, self._subject, kind,
            pid=pid, decision=decision, reason=reason, note=note)
        entries = getattr(self._program, "director_records", None)
        if entries is None:
            entries = {}
            self._program.director_records = entries
        entries[entry["entry_id"]] = entry
        # Bounded: keep the newest _MAX. DAF-05: the victim is
        # chosen by the shared explicit oldest-first policy —
        # dict order after a reload is newest-first, not insert
        # order, and must never choose the victim.
        from form.dell_matrix.session_section import oldest_key
        while len(entries) > _records._MAX_ENTRIES:
            entries.pop(oldest_key(entries))
            # AF-4: count the eviction at the moment/place of
            # loss (PP2b B2), as the other bounded writers do.
            total = getattr(self._program,
                            "director_records_dropped_total", 0)
            if not isinstance(total, int) \
                    or isinstance(total, bool) or total < 0:
                total = 0
            self._program.director_records_dropped_total = total + 1
        try:
            self._program.save()
        except Exception:
            pass  # in-memory record stands; persistence is retried
            # on the next program save, like dock evidence.
        return entry

    def _refuse(self, pid: str, why: str) -> Dict[str, Any]:
        self._record("refusal", pid=pid if isinstance(pid, str)
                     else "", note=why)
        return {"ok": False, "reason": why, "pid": pid}

    def _find_proposal(self, pid: Any) -> Optional[Dict[str, Any]]:
        if not isinstance(pid, str) or not pid:
            return None
        snap = self._session.field_snapshot() or {}
        # The coordinator snapshot carries Nursery proposals under
        # "ideas" (units under "units") — the SD-2 key contract.
        for entry in snap.get("ideas") or []:
            if entry.get("pid") == pid:
                return entry
        return None

    # -- the allowlist ---------------------------------------------------
    def snapshot(self) -> Dict[str, Any]:
        """The scoped field snapshot (the wrapped session's
        coordinator snapshot over the SCOPE program only).
        Proposals are under "ideas", plane units under "units"
        (the coordinator's key contract). A closed session reads
        nothing and returns the empty snapshot."""
        if self._is_closed():
            return {}
        return self._session.field_snapshot() or {}

    def review(self, pid: str) -> Dict[str, Any]:
        """Read one in-scope proposal. Out-of-scope is refused and
        recorded."""
        if self._is_closed():
            return self._closed_refusal(pid)
        found = self._find_proposal(pid)
        if found is None:
            return self._refuse(pid, "out_of_scope")
        return {"ok": True, "proposal": found}

    def recommend(self, pid: str, decision: str,
                  reason: str) -> Dict[str, Any]:
        """Record an accept/reject RECOMMENDATION. This never
        confirms, rejects, or otherwise changes the proposal: the
        human gate decides, reading this as advice with
        provenance."""
        if self._is_closed():
            return self._closed_refusal(pid)
        if decision not in _records.DECISIONS:
            return self._refuse(pid, "invalid_decision")
        if not isinstance(reason, str) or not reason.strip():
            return self._refuse(pid, "reason_required")
        if len(reason) > MAX_REASON_CHARS:
            return self._refuse(pid, "reason_too_long")
        found = self._find_proposal(pid)
        if found is None:
            return self._refuse(pid, "out_of_scope")
        if found.get("status") != "pending":
            return self._refuse(pid, "not_pending")
        entry = self._record("recommendation", pid=pid,
                             decision=decision, reason=reason)
        return {"ok": True, "effect": "recommendation_only",
                "entry_id": entry["entry_id"], "pid": pid,
                "decision": decision}

    def request_evidence(self, pid: str, what: str) -> Dict[str, Any]:
        """Record a request for more evidence about an in-scope
        proposal."""
        if self._is_closed():
            return self._closed_refusal(pid)
        if not isinstance(what, str) or not what.strip():
            return self._refuse(pid, "note_required")
        if len(what) > MAX_REASON_CHARS:
            return self._refuse(pid, "note_too_long")
        if self._find_proposal(pid) is None:
            return self._refuse(pid, "out_of_scope")
        entry = self._record("evidence_request", pid=pid, note=what)
        return {"ok": True, "entry_id": entry["entry_id"],
                "pid": pid}

    def directive(self, text: str, reason: str = "") -> Dict[str, Any]:
        """File a directive as a PENDING proposal through the
        wrapped docked session, and record the link. The proposal
        carries the dock's provenance; it has no authority."""
        if self._is_closed():
            return self._closed_refusal("")
        out = self._session.propose(text, reason=reason or None)
        if not out.get("ok"):
            return out
        entry = self._record("directive", pid=out["pid"],
                             reason=reason or "")
        return {"ok": True, "pid": out["pid"],
                "entry_id": entry["entry_id"],
                "provider": out.get("provider"),
                "model": out.get("model")}

    def undock(self) -> Dict[str, Any]:
        """Close the endpoint and the wrapped dock. Idempotent;
        after this every allowlist method refuses (session_closed)
        and nothing is read or written."""
        if not self._closed:
            object.__setattr__(self, "_closed", True)
            self._session.undock()
        return {"ok": True, "effect": "undocked"}


def bind_director(program: Any, *, provider: str = "fake",
                  subject: str = "director:dev",
                  scope_owner: Optional[str] = None,
                  task: str = "review") -> DirectorSession:
    """Create a scoped Director session. TRUSTED HOST ONLY.

    Docks `subject` (must carry the "director:" prefix) into
    `program` through the standard SD-1 dock, then wraps it in
    the restricted Director surface. `scope_owner` defaults to the
    program's own owner; the wrap verifies they match, so a
    Director bound to one owner's matrix can never be re-scoped
    to another by argument.
    """
    if not isinstance(subject, str) \
            or not subject.startswith("director:"):
        raise DirectorError(
            "Director subject must carry the 'director:' prefix")
    owner = scope_owner if scope_owner is not None \
        else getattr(program, "owner", None)
    from form.dell_matrix.inference_dock import dock
    session = dock(program, trusted_subject=subject,
                   provider=provider, task=task)
    return DirectorSession(session, scope_owner=owner)
