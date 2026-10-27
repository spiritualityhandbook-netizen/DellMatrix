"""R7.3 General Workshop Contract — scoped workshop session evidence.

The workshops registry (form/dell_matrix/workshops.py) defines seven
workshops as data: names, descriptions, and button-menu command lists.
Program.enter_workshop/leave_workshop track which workshop is active.
Before R7.3, entering a workshop changed nothing about dispatch: any
command could run inside any workshop, and no session evidence existed.

This module supplies the session-evidence half of the general workshop
contract (the REPL supplies the scoped gate):

    enter -> scoped command set + scoped prompt -> leave

- The scoped command set is DERIVED from the workshop's own registry
  entry (command stems), never a second hand-maintained list.
- In-scope commands route through the SAME public dispatcher as outside
  (mutations via the same path; the workshop grants nothing new).
- Session evidence is bounded (50 commands, 10 sessions), records only
  command stems and fixed result codes, and persists only on leave via
  the canonical save with stage-then-save semantics (handled by the
  REPL handler, mirroring the R7.2 studio).
- The Perspective Studio (R7.2) remains the specialized environment for
  perspective work; this contract governs the menu workshops. Only one
  scoped environment may be active at a time.

Persistence contract (shared strict schema, same pattern as R7.2):
- Section version 1. Bool-as-version and unsupported coercions rejected.
- Session dict key must equal the record's session_id.
- Record owner must equal the Program owner; workshop must be a known
  workshop id from the registry.
- Only closed records persist; active sessions never serialize.
- Malformed sections are preserved as evidence through save/reload;
  same-key failures accumulate, never overwrite.
- Retention: 10 most recent sessions, 50 most recent commands per
  session, enforced during recording. History beyond the retained
  window is not available; this is documented, not claimed as complete.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from form.dell_matrix.session_section import (
    MISSING,
    add_malformed,
    append_step,
    closed_record,
    is_valid_step,
    serialize_records_section,
    validate_records_section,
)

_MAX_COMMANDS = 50
_MAX_SESSIONS = 10

WORKSHOP_SECTION_VERSION = 1

FAIL_PROTECTED = "PROTECTED_MATERIAL"
FAIL_OUT_OF_SCOPE = "OUT_OF_SCOPE"
FAIL_SAVE = "SAVE_FAILED"

# The kit's record check, under this module's historical name.
_is_valid_command = is_valid_step


def known_workshop_ids() -> Set[str]:
    from form.dell_matrix.workshops import WORKSHOPS
    return set(WORKSHOPS.keys())


def scope_stems(workshop_id: str) -> Set[str]:
    """Derive the scoped command stems from the workshop's registry entry.

    A line is in scope when its first token is one of these stems (the
    first token of any command in the workshop's menu). Deriving from
    the registry keeps exactly one authority for what a workshop offers.
    """
    from form.dell_matrix.workshops import get_workshop
    w = get_workshop(workshop_id)
    if not w:
        return set()
    stems: Set[str] = set()
    for c in w.get("commands") or []:
        cmd = str(c.get("cmd", "")).strip()
        if cmd:
            stems.add(cmd.split()[0].lower())
    return stems


@dataclass
class WorkshopSession:
    """One closed or active workshop session record.

    Only command stems and fixed result summaries are stored. Never raw
    input lines, grants, authority, or credentials.
    """
    session_id: str
    owner: str
    workshop: str
    started: str
    closed: Optional[str] = None
    commands: List[Dict[str, str]] = field(default_factory=list)

    @classmethod
    def open(cls, owner: str, workshop: str) -> "WorkshopSession":
        return cls(
            session_id=str(uuid.uuid4()),
            owner=owner,
            workshop=workshop,
            started=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )

    def record(self, kind: str, result: str) -> None:
        """Record one command. Enforces the in-memory bound."""
        self.commands = append_step(self.commands, kind, result,
                                    _MAX_COMMANDS)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "owner": self.owner,
            "workshop": self.workshop,
            "started": self.started,
            "closed": self.closed,
            "commands": [dict(c) for c in self.commands[-_MAX_COMMANDS:]],
        }

    def closed_copy(self) -> Dict[str, Any]:
        """Build the closed record WITHOUT mutating the session.

        The caller stages this record, saves, and only discards the
        session after successful persistence. On save failure the
        session remains active and usable; closed_copy() is idempotent.
        """
        return closed_record(self.to_dict(), "commands", _MAX_COMMANDS)

    @staticmethod
    def validate(raw: Any, owner: str) -> Tuple[bool, str]:
        """Strict shape check for a persisted workshop session record."""
        if not isinstance(raw, dict):
            return False, "session must be an object"
        for key in ("session_id", "owner", "workshop", "started"):
            v = raw.get(key)
            if not isinstance(v, str) or isinstance(v, bool):
                return False, f"session.{key} must be a string"
            if not v or len(v) > 128:
                return False, f"session.{key} must be non-empty (max 128)"
        if raw["owner"] != owner:
            return False, "session.owner does not match Program owner"
        if raw["workshop"] not in known_workshop_ids():
            return False, "session.workshop is not a known workshop"
        closed = raw.get("closed")
        if not isinstance(closed, str) or not closed or len(closed) > 128:
            return False, "session.closed must be set (only closed records persist)"
        cmds = raw.get("commands")
        if not isinstance(cmds, list):
            return False, "session.commands must be an array"
        if len(cmds) > _MAX_COMMANDS:
            return False, f"session.commands exceeds {_MAX_COMMANDS}"
        for c in cmds:
            if not _is_valid_command(c):
                return False, "session.commands has an invalid record"
        return True, ""


# Sentinel for absent section key (legacy). Distinct from explicit null,
# which is malformed. Python maps JSON null to None, so the loader must
# use data.get("workshop_sessions", _MISSING) to distinguish.
# _MISSING is the session_section kit's one sentinel (P3/TD-2), and
# _add_malformed its one implementation.
_MISSING = MISSING
_add_malformed = add_malformed


def validate_section(raw: Any, owner: str) -> Tuple[Dict[str, Dict[str, Any]], Optional[Dict[str, Any]]]:
    """Validate a persisted workshop_sessions section (strict schema).

    Returns (sessions, malformed). Mirrors the R7.2 studio contract:
    absent (_MISSING) is legacy; explicit null / non-dict / wrong
    version are malformed under "_section"; per-record failures are
    preserved by key; previously-preserved malformed evidence is carried
    through with same-key append. Never raises.
    """
    return validate_records_section(
        raw, version=WORKSHOP_SECTION_VERSION, kind="sessions",
        validate_rec=lambda rec: WorkshopSession.validate(rec, owner),
        id_field="session_id", max_keep=_MAX_SESSIONS,
        sort_field="started", key_not_string="session key not a string",
        mismatch="session key/ID mismatch")


def serialize_section(sessions: Any, malformed: Any, owner: str) -> Dict[str, Any]:
    """Serialize workshop sessions with the shared strict schema.

    Valid closed records go to "sessions". Invalid records (active,
    foreign-owner, unknown-workshop, key/ID-mismatched) are preserved in
    "malformed", never silently saved as valid or discarded. Never raises.
    """
    return serialize_records_section(
        sessions, malformed, version=WORKSHOP_SECTION_VERSION,
        kind="sessions",
        validate_rec=lambda rec: WorkshopSession.validate(rec, owner),
        id_field="session_id", max_keep=_MAX_SESSIONS,
        sort_field="started", key_not_string="session key not a string",
        mismatch="not serialized as valid: key/ID mismatch")
