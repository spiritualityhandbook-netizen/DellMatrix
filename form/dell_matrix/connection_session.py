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
the shared strict schema (sixth instance): closed records only,
bounded (50 steps / 10 sessions), owner-bound, malformed preserved,
absent = legacy. Only step kinds and fixed result summaries are
stored — never prompts, never fetched content, never URLs beyond the
recorded fetch host.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

_MAX_STEPS = 50
_MAX_SESSIONS = 10

CONNECTION_SECTION_VERSION = 1

FAIL_PROTECTED = "PROTECTED_MATERIAL"
FAIL_OUT_OF_SCOPE = "OUT_OF_SCOPE"
FAIL_SAVE = "SAVE_FAILED"
FAIL_DOCK = "DOCK_FAILED"


def _is_valid_step(rec: Any) -> bool:
    """Strict step record check. No coercion."""
    if not isinstance(rec, dict):
        return False
    for k in ("kind", "time", "result"):
        v = rec.get(k)
        if not isinstance(v, str) or len(v) > 256:
            return False
    if len(rec.get("kind", "")) == 0 or len(rec.get("kind", "")) > 32:
        return False
    return True


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
        self.steps.append({
            "kind": str(kind)[:32],
            "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "result": str(result)[:240],
        })
        if len(self.steps) > _MAX_STEPS:
            self.steps = self.steps[-_MAX_STEPS:]

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
        record = self.to_dict()
        record["closed"] = time.strftime(
            "%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        steps = list(record.get("steps", []))
        steps.append({
            "kind": "leave",
            "time": record["closed"],
            "result": "leave recorded",
        })
        record["steps"] = steps[-_MAX_STEPS:]
        return record

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
_MISSING = object()


def _add_malformed(malformed: Dict[str, Any], key: str, raw: Any, error: str) -> None:
    """Add malformed evidence without overwriting earlier evidence."""
    entry = {"raw": raw, "error": error}
    if key in malformed:
        existing = malformed[key]
        if isinstance(existing, list):
            existing.append(entry)
        else:
            malformed[key] = [existing, entry]
    else:
        malformed[key] = [entry]


def _carry_preserved(raw: Any, malformed: Dict[str, Any]) -> None:
    """Carry previously-preserved malformed evidence through, by key."""
    preserved = raw.get("malformed") if isinstance(raw, dict) else None
    if isinstance(preserved, dict):
        for k, v in preserved.items():
            if not isinstance(k, str):
                continue
            if isinstance(v, list):
                for entry in v:
                    if isinstance(entry, dict):
                        _add_malformed(malformed, k, entry.get("raw"),
                                       entry.get("error", "preserved"))
                    else:
                        _add_malformed(malformed, k, entry, "preserved")
            elif isinstance(v, dict) and "raw" in v:
                _add_malformed(malformed, k, v.get("raw"),
                               v.get("error", "preserved"))
            else:
                _add_malformed(malformed, k, v, "preserved")


def validate_section(raw: Any, owner: str
                     ) -> Tuple[Dict[str, Dict[str, Any]],
                                Optional[Dict[str, Any]]]:
    """Validate a persisted connection_sessions section. Never raises."""
    if raw is _MISSING:
        return {}, None
    if raw is None:
        malformed: Dict[str, Any] = {}
        _add_malformed(malformed, "_section", None,
                       "explicit null is malformed, not legacy absence")
        return {}, malformed
    if not isinstance(raw, dict):
        malformed = {}
        _add_malformed(malformed, "_section", raw, "section not an object")
        return {}, malformed
    version = raw.get("version")
    if isinstance(version, bool) or not isinstance(version, int):
        malformed = {}
        _add_malformed(malformed, "_section", raw,
                       "section version must be int 1")
        return {}, malformed
    if version != CONNECTION_SECTION_VERSION:
        malformed = {}
        _add_malformed(malformed, "_section", raw,
                       f"unsupported section version {version}")
        return {}, malformed
    if not isinstance(raw.get("sessions"), dict):
        malformed = {}
        _add_malformed(malformed, "_section", raw, "sessions not an object")
        return {}, malformed
    valid: Dict[str, Dict[str, Any]] = {}
    malformed = {}
    for sid, rec in raw["sessions"].items():
        if not isinstance(sid, str):
            _add_malformed(malformed, "_non_string_key", rec,
                           "session key not a string")
            continue
        ok, err = ConnectionSession.validate(rec, owner)
        if not ok:
            _add_malformed(malformed, sid, rec, err)
            continue
        if not isinstance(rec, dict) or rec.get("session_id") != sid:
            _add_malformed(malformed, sid, rec, "session key/ID mismatch")
            continue
        valid[sid] = dict(rec)
    _carry_preserved(raw, malformed)
    ordered = sorted(valid.items(),
                     key=lambda kv: str(kv[1].get("started", "")),
                     reverse=True)[:_MAX_SESSIONS]
    return dict(ordered), (malformed if malformed else None)


def serialize_section(sessions: Any, malformed: Any,
                      owner: str) -> Dict[str, Any]:
    """Serialize connection sessions with the strict schema. Never raises."""
    valid: Dict[str, Dict[str, Any]] = {}
    mal: Dict[str, Any] = {}
    if isinstance(sessions, dict):
        for sid, rec in sessions.items():
            if not isinstance(sid, str):
                _add_malformed(mal, "_non_string_key", rec,
                               "session key not a string")
                continue
            ok, err = ConnectionSession.validate(rec, owner)
            if not ok:
                _add_malformed(mal, sid, rec,
                               f"not serialized as valid: {err}")
                continue
            if not isinstance(rec, dict) or rec.get("session_id") != sid:
                _add_malformed(mal, sid, rec,
                               "not serialized as valid: key/ID mismatch")
                continue
            valid[sid] = dict(rec)
    _carry_preserved({"malformed": malformed} if isinstance(malformed, dict) else {}, mal)
    ordered = sorted(valid.items(),
                     key=lambda kv: str(kv[1].get("started", "")),
                     reverse=True)[:_MAX_SESSIONS]
    section: Dict[str, Any] = {
        "version": CONNECTION_SECTION_VERSION,
        "sessions": dict(ordered),
    }
    if mal:
        section["malformed"] = mal
    return section
