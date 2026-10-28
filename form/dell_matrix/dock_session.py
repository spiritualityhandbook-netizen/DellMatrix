"""SD-1 (master plan P4) — dock session evidence section.

Every docked inference session (form/dell_matrix/inference_dock.py)
leaves a persisted evidence record in the program-state section
``dock_sessions``, following the ConnectionSession section pattern
(P3/TD-2 session_section kit): closed-shape records, owner-bound,
malformed preserved as evidence, absent = legacy.

One deliberate difference from the interaction sections: a dock
record may persist OPEN (``closed`` is null). A dock session is a
capability session, not an interaction: proposals it creates are
durable in the Nursery the moment they land, so their session link
must be durable at the same moment — not only after a polite
undock. The record is upserted into program state at dock time and
updated in place on every successful propose().

What the record holds (evidence, never authority):
- who/what docked: subject (host-established), provider, model
  label, task kind, snap registration name;
- when: started / closed timestamps;
- per proposal: the Nursery pid, the origin string exactly as
  stamped, the reason exactly as stored, the ACTUAL model the
  transport reported, a SHA-256 of the exact prompt text sent,
  a bounded prompt summary, and a snapshot id = SHA-256 of the
  canonical JSON of the validated context actually sent (null when
  no context was sent).

Prompts are never stored in full; fetched/credential material never
enters this section (propose() screens before evidence is written).
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional, Tuple

from form.dell_matrix.session_section import (
    MISSING,
    serialize_records_section,
    validate_records_section,
)

_MAX_SESSIONS = 10
_MAX_PROPOSALS = 50

DOCK_SECTION_VERSION = 1

_HEX = frozenset("0123456789abcdef")


def _is_hex64(v: Any) -> bool:
    return isinstance(v, str) and len(v) == 64 and all(c in _HEX for c in v)


def _bounded_str(v: Any, limit: int) -> bool:
    return isinstance(v, str) and len(v) <= limit


def new_record(owner: str, subject: str, provider: str, model: str,
               task: str, snap_name: str) -> Dict[str, Any]:
    """Build a fresh open evidence record for a docked session."""
    return {
        "session_id": str(uuid.uuid4()),
        "owner": owner,
        "subject": subject,
        "provider": provider,
        "model": model,
        "task": task,
        "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "closed": None,
        "snap_name": snap_name,
        "proposals": [],
        # PP2b (charter ruling B2): entries evicted by the
        # proposals bound are counted, so the loss is measurable
        # instead of silent.
        "dropped": 0,
    }


def append_proposal(record: Dict[str, Any], entry: Dict[str, Any]) -> None:
    """Append one proposal-evidence entry, enforcing the bound.

    Beyond _MAX_PROPOSALS the oldest entries are dropped: the record
    is bounded evidence of the session's most recent work, and the
    Nursery itself remains the complete proposal ledger.
    """
    props = record.setdefault("proposals", [])
    props.append(entry)
    if len(props) > _MAX_PROPOSALS:
        excess = len(props) - _MAX_PROPOSALS
        del props[:excess]
        # PP2b (B2): count the eviction on the record itself.
        cur = record.get("dropped")
        record["dropped"] = (cur if isinstance(cur, int)
                              and not isinstance(cur, bool)
                              and cur >= 0 else 0) + excess


def close_record(record: Dict[str, Any]) -> None:
    record["closed"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _is_valid_entry(e: Any) -> bool:
    if not isinstance(e, dict):
        return False
    if not _bounded_str(e.get("pid"), 80) or not e.get("pid"):
        return False
    if not _bounded_str(e.get("ts"), 128) or not e.get("ts"):
        return False
    if not _bounded_str(e.get("task"), 40):
        return False
    if not _bounded_str(e.get("reason"), 160):
        return False
    if not _bounded_str(e.get("origin"), 120):
        return False
    if not _is_hex64(e.get("prompt_hash")):
        return False
    if not _bounded_str(e.get("prompt_summary"), 80):
        return False
    pc = e.get("prompt_chars")
    if not isinstance(pc, int) or isinstance(pc, bool) or pc < 0:
        return False
    snap = e.get("snapshot_id")
    if snap is not None and not _is_hex64(snap):
        return False
    if not _bounded_str(e.get("model"), 120):
        return False
    return True


def validate(raw: Any, owner: str) -> Tuple[bool, str]:
    """Strict shape check for a persisted dock session record."""
    if not isinstance(raw, dict):
        return False, "session must be an object"
    for key in ("session_id", "owner", "started"):
        v = raw.get(key)
        if not isinstance(v, str) or isinstance(v, bool):
            return False, f"session.{key} must be a string"
        if not v or len(v) > 128:
            return False, f"session.{key} must be non-empty (max 128)"
    if raw["owner"] != owner:
        return False, "session.owner does not match Program owner"
    for key, limit in (("subject", 200), ("provider", 80),
                       ("model", 120), ("task", 40), ("snap_name", 120)):
        if not _bounded_str(raw.get(key), limit):
            return False, f"session.{key} must be a string (max {limit})"
    closed = raw.get("closed")
    if closed is not None:
        if not isinstance(closed, str) or not closed or len(closed) > 128:
            return False, "session.closed must be null or a timestamp"
    props = raw.get("proposals")
    if not isinstance(props, list):
        return False, "session.proposals must be an array"
    if len(props) > _MAX_PROPOSALS:
        return False, f"session.proposals exceeds {_MAX_PROPOSALS}"
    for e in props:
        if not _is_valid_entry(e):
            return False, "session.proposals has an invalid entry"
    # PP2b (B2): the eviction counter, when present, must be a
    # non-negative int. Absent is legacy (pre-PP2b records).
    dropped = raw.get("dropped")
    if dropped is not None:
        if not isinstance(dropped, int) or isinstance(dropped, bool) \
                or dropped < 0:
            return False, "session.dropped must be a non-negative int"
    return True, ""


# Sentinel for absent section key (legacy). Distinct from explicit
# null, which is malformed. Loaders use data.get("dock_sessions",
# _MISSING) — the kit's one sentinel.
_MISSING = MISSING


def validate_section(raw: Any, owner: str
                     ) -> Tuple[Dict[str, Dict[str, Any]],
                                Optional[Dict[str, Any]]]:
    """Validate a persisted dock_sessions section. Never raises."""
    return validate_records_section(
        raw, version=DOCK_SECTION_VERSION, kind="sessions",
        validate_rec=lambda rec: validate(rec, owner),
        id_field="session_id", max_keep=_MAX_SESSIONS,
        sort_field="started", key_not_string="session key not a string",
        mismatch="session key/ID mismatch")


def serialize_section(sessions: Any, malformed: Any,
                      owner: str, extra: Any = None) -> Dict[str, Any]:
    """Serialize dock sessions with the strict schema. Never raises."""
    return serialize_records_section(
        sessions, malformed, version=DOCK_SECTION_VERSION,
        kind="sessions",
        validate_rec=lambda rec: validate(rec, owner),
        id_field="session_id", max_keep=_MAX_SESSIONS,
        sort_field="started", key_not_string="session key not a string",
        mismatch="not serialized as valid: key/ID mismatch",
        extra=extra)
