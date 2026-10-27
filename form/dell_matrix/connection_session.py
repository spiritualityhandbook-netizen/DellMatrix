"""R7.6 Connected World — a public, evidence-recorded path to the
existing connection authorities.

Repository reality before R7.6: the connection machinery was complete
but fragmented and partly unreachable.

- InternetGate (form/dell_matrix/internet_gate.py) is the fetch
  authority: default OFF, host allowlist, bounded fetches. The REPL
  reaches it ad hoc (`internet on`, `fetch <url>`, `net research`),
  but fetches leave no durable evidence — the gate's fetch log is
  in-memory only and its persisted form keeps just a count.
- inference_dock (form/dell_matrix/inference_dock.py) is the LLM
  docking authority: explicit provider configuration, host-held
  credentials, screened input/output, bounded sizes/timeouts, and
  proposals that land PENDING in the Nursery (never confirmed, never
  authority). It was TRUSTED HOST ONLY — no public user path existed.

The `connect` scoped REPL session unifies the public path without
touching either authority's laws:

- Gate control (`internet on|off`, `allow <host>`) goes through the
  Program's existing gate methods; the gate stays default-OFF and
  the allowlist stays enforced by the gate itself.
- `fetch <url>` goes through the gate and records PROVENANCE evidence
  in the session record: the host the program actually fetched from,
  the HTTP status, and the byte count — assigned by the host at fetch
  time, never by content. Fetched content is displayed bounded (as
  the ad-hoc path does) and is NEVER stored in evidence and NEVER
  enters knowledge or proposals by itself (STORED != ELIGIBLE).
- `ask <prompt>` is the public docking path: a DockedSession is
  created by the host with a host-established subject, the provider
  is selected BY NAME only (default "fake": deterministic, offline),
  and propose() runs the dock's own enforcement order. The result is
  a PENDING Nursery proposal or a fixed reason code.
- Credential gateway by construction: no command accepts a
  credential, a key, or a URL with embedded secrets; providers read
  credentials from the host environment themselves (the dock's
  existing law). Provider selection is one token — a name.

Session evidence persists in the `connection_sessions` section under
the shared strict schema (implemented once in the session_section
kit, P3/TD-2): closed records only, bounded (50 steps / 10
sessions), owner-bound, malformed preserved, absent = legacy. Only
step kinds and fixed result summaries are stored — never prompts,
never fetched content, never URLs beyond the recorded fetch host.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from form.dell_matrix.session_section import (
    MISSING,
    add_malformed,
    append_step,
    closed_record,
    is_valid_step,
    serialize_records_section,
    validate_records_section,
)

_MAX_STEPS = 50
_MAX_SESSIONS = 10

CONNECTION_SECTION_VERSION = 1

FAIL_PROTECTED = "PROTECTED_MATERIAL"
FAIL_OUT_OF_SCOPE = "OUT_OF_SCOPE"
FAIL_SAVE = "SAVE_FAILED"
FAIL_DOCK = "DOCK_FAILED"

# The kit's step check, under this module's historical name.
_is_valid_step = is_valid_step


@dataclass
class ConnectionSession:
    """One closed or active connect session record + runtime state.

    The persisted shape is only the evidence fields (to_dict). The
    selected provider name and the live DockedSession handle are
    runtime-only: provider configuration is explicit per session and
    is never persisted as a standing enablement.
    """
    session_id: str
    owner: str
    started: str
    closed: Optional[str] = None
    steps: List[Dict[str, str]] = field(default_factory=list)
    # Runtime-only (excluded from to_dict).
    provider: str = field(default="fake", repr=False)
    docked: Any = field(default=None, repr=False)

    @classmethod
    def open(cls, owner: str) -> "ConnectionSession":
        return cls(
            session_id=str(uuid.uuid4()),
            owner=owner,
            started=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )

    def record(self, kind: str, result: str) -> None:
        """Record one step. Enforces the in-memory bound."""
        self.steps = append_step(self.steps, kind, result, _MAX_STEPS)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "owner": self.owner,
            "started": self.started,
            "closed": self.closed,
            "steps": [dict(s) for s in self.steps[-_MAX_STEPS:]],
        }

    def closed_copy(self) -> Dict[str, Any]:
        """Build the closed record WITHOUT mutating the session."""
        return closed_record(self.to_dict(), "steps", _MAX_STEPS)

    @staticmethod
    def validate(raw: Any, owner: str) -> Tuple[bool, str]:
        """Strict shape check for a persisted connection session."""
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
        closed = raw.get("closed")
        if not isinstance(closed, str) or not closed or len(closed) > 128:
            return False, "session.closed must be set (only closed records persist)"
        steps = raw.get("steps")
        if not isinstance(steps, list):
            return False, "session.steps must be an array"
        if len(steps) > _MAX_STEPS:
            return False, f"session.steps exceeds {_MAX_STEPS}"
        for s in steps:
            if not _is_valid_step(s):
                return False, "session.steps has an invalid record"
        return True, ""


# Sentinel for absent section key (legacy). Distinct from explicit null,
# which is malformed. Loaders use data.get("connection_sessions", _MISSING).
# _MISSING is the session_section kit's one sentinel (P3/TD-2), and
# _add_malformed its one implementation.
_MISSING = MISSING
_add_malformed = add_malformed


def validate_section(raw: Any, owner: str
                     ) -> Tuple[Dict[str, Dict[str, Any]],
                                Optional[Dict[str, Any]]]:
    """Validate a persisted connection_sessions section. Never raises."""
    return validate_records_section(
        raw, version=CONNECTION_SECTION_VERSION, kind="sessions",
        validate_rec=lambda rec: ConnectionSession.validate(rec, owner),
        id_field="session_id", max_keep=_MAX_SESSIONS,
        sort_field="started", key_not_string="session key not a string",
        mismatch="session key/ID mismatch")


def serialize_section(sessions: Any, malformed: Any,
                      owner: str) -> Dict[str, Any]:
    """Serialize connection sessions with the strict schema. Never raises."""
    return serialize_records_section(
        sessions, malformed, version=CONNECTION_SECTION_VERSION,
        kind="sessions",
        validate_rec=lambda rec: ConnectionSession.validate(rec, owner),
        id_field="session_id", max_keep=_MAX_SESSIONS,
        sort_field="started", key_not_string="session key not a string",
        mismatch="not serialized as valid: key/ID mismatch")
