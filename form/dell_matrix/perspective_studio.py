"""R7.2 Perspective Studio — presentation adapter over R7.1 compose_views.

The studio is a scoped REPL mode for composing perspective views and
inspecting their meaning. It is a presentation adapter only:

- Delegates composition to R7.1 compose_views (no replacement compositor).
- Uses the existing "perspective" workshop identity for attribution.
- Derives owner from the Program; rejects any supplied owner mismatch.
- Persists only presentation specifications and bounded session evidence
  (session ID, owner, command kind, time, result summary).
- Never persists grants, authority, or raw credentials.
- Layout and legend are descriptive: position means canonical coordinates,
  skin is presentation metadata, epistemic status means verification —
  not accepted truth or permission.

All mutations route through the standard dispatcher or are rejected;
the studio itself performs no mutations.

Persistence contract (shared strict schema):
- Section version 1. Bool-as-version and unsupported coercions rejected.
- Session dict key must equal the record's session_id.
- Record owner must equal the Program owner.
- Only closed records persist; active sessions never serialize.
- Malformed sections are preserved as evidence through save/reload.
- Retention: 10 most recent sessions, 50 most recent commands per session.
  Bounds are enforced during recording, not only at serialization.
  History beyond the retained window is not available; this is documented,
  not claimed as complete.
"""

from __future__ import annotations

import json
import math
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

# Bounds for caller-supplied composition specs.
_MAX_SPECS = 8
_MAX_ID_LEN = 64
_MAX_ROLE_LEN = 32
_MAX_FACING_LEN = 8
_MAX_MODE_LEN = 16
_MAX_JSON_BYTES = 8192

# Bounds for session evidence. Enforced during recording.
_MAX_COMMANDS = 50
_MAX_SESSIONS = 10

# Strict persistence schema version. Must be int 1; bool is rejected.
STUDIO_SECTION_VERSION = 1

_VALID_FACINGS = frozenset({"N", "S", "E", "W", "NE", "NW", "SE", "SW"})
_VALID_MODES = frozenset({"first", "third", "parts", "whole"})

# Inspectable layout legend. Descriptive only: these define what the
# presentation fields mean, not what they authorize or prove.
# Keys correspond to fields displayed by the studio's compose output.
LEGEND: Dict[str, str] = {
    "viewer": "Attribution: which viewer specification produced this component.",
    "requested_mode": "The observation mode requested (first/third/parts/whole).",
    "epistemic_status": "Verification standing of the view (e.g., REAL, PARTIAL); "
                        "not accepted truth and not permission.",
    "source": "Provenance of the observation data.",
    "observations": "The attributed observation report from the compositor.",
}

STUDIO_COMMANDS = ("compose", "legend", "help", "leave")

# Fixed bounded failure codes. Never reflect raw input, unknown keys,
# or exception text.
FAIL_PROTECTED = "PROTECTED_MATERIAL"
FAIL_MALFORMED_JSON = "MALFORMED_JSON"
FAIL_INVALID_SPEC = "INVALID_SPEC"
FAIL_OWNER_MISMATCH = "OWNER_MISMATCH"
FAIL_OUT_OF_SCOPE = "OUT_OF_SCOPE"
FAIL_SAVE = "SAVE_FAILED"


def _is_finite_number(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def validate_spec(raw: Any) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """Validate one caller-supplied viewer spec.

    Returns (ok, error, normalized). No eval, no attribute access,
    no permissive string coercion. Finite numbers only. Bounded input.
    This is the shared contract: the REPL and direct API callers use
    the same validation. Direct callers must not assume normalized data.
    """
    if not isinstance(raw, dict):
        return False, "spec must be a JSON object", None
    # id: required non-empty string, bounded
    vid = raw.get("id")
    if not isinstance(vid, str) or not vid or len(vid) > _MAX_ID_LEN:
        return False, "spec.id must be a non-empty string (max 64)", None
    # role: optional string, bounded; default matches Viewer
    role = raw.get("role", "ai_first")
    if not isinstance(role, str) or len(role) > _MAX_ROLE_LEN:
        return False, "spec.role must be a string (max 32)", None
    # pos: required [x, y] of finite numbers
    pos = raw.get("pos")
    if (not isinstance(pos, (list, tuple)) or len(pos) != 2
            or not all(_is_finite_number(v) for v in pos)):
        return False, "spec.pos must be [x, y] of finite numbers", None
    # facing: optional, bounded, must be a known facing
    facing = raw.get("facing", "N")
    if not isinstance(facing, str) or len(facing) > _MAX_FACING_LEN:
        return False, "spec.facing must be a string (max 8)", None
    if facing not in _VALID_FACINGS:
        return False, f"spec.facing must be one of {sorted(_VALID_FACINGS)}", None
    # mode: optional; if present must be a known mode
    mode = raw.get("mode")
    if mode is not None:
        if not isinstance(mode, str) or len(mode) > _MAX_MODE_LEN:
            return False, "spec.mode must be a string (max 16)", None
        if mode not in _VALID_MODES:
            return False, f"spec.mode must be one of {sorted(_VALID_MODES)}", None
    # owner: if supplied, must be a bounded string; the caller checks it
    # against the Program owner. Reject unexpected keys to keep the schema
    # explicit.
    allowed = {"id", "role", "pos", "facing", "mode", "owner"}
    extra = set(raw.keys()) - allowed
    if extra:
        return False, "spec has unexpected keys", None
    owner = raw.get("owner")
    if owner is not None and (not isinstance(owner, str) or len(owner) > 128):
        return False, "spec.owner must be a string (max 128)", None
    normalized = {
        "id": vid,
        "role": role,
        "pos": [float(pos[0]), float(pos[1])],
        "facing": facing,
        "mode": mode,
    }
    if owner is not None:
        normalized["owner"] = owner
    return True, "", normalized


def parse_specs_json(text: str) -> Tuple[bool, str, Optional[List[Dict[str, Any]]]]:
    """Parse and validate a JSON array of viewer specs.

    Bounded input: rejects payloads over _MAX_JSON_BYTES and arrays
    over _MAX_SPECS. Every spec goes through validate_spec.
    Error messages are bounded and do not reflect input content.
    """
    if len(text.encode("utf-8")) > _MAX_JSON_BYTES:
        return False, FAIL_MALFORMED_JSON, None
    try:
        raw = json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return False, FAIL_MALFORMED_JSON, None
    if not isinstance(raw, list):
        return False, FAIL_MALFORMED_JSON, None
    if not raw:
        return False, FAIL_INVALID_SPEC, None
    if len(raw) > _MAX_SPECS:
        return False, FAIL_INVALID_SPEC, None
    out: List[Dict[str, Any]] = []
    for item in raw:
        ok, _, norm = validate_spec(item)
        if not ok:
            return False, FAIL_INVALID_SPEC, None
        out.append(norm)  # type: ignore[arg-type]
    return True, "", out


def _is_valid_command(rec: Any) -> bool:
    """Strict command record check. No coercion."""
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
class StudioSession:
    """One closed or active studio session record.

    Only presentation specifications and bounded evidence are stored.
    Never grants, authority, or raw credentials.
    Bounds are enforced during recording: at most _MAX_COMMANDS commands
    are retained; older commands are discarded. This is a retained window,
    not complete history.
    """
    session_id: str
    owner: str
    started: str
    closed: Optional[str] = None
    commands: List[Dict[str, str]] = field(default_factory=list)

    def record(self, kind: str, result: str) -> None:
        """Record one command. Enforces the in-memory bound."""
        self.commands.append({
            "kind": str(kind)[:32],
            "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "result": str(result)[:240],
        })
        # Enforce bound during recording, not only at serialization.
        if len(self.commands) > _MAX_COMMANDS:
            self.commands = self.commands[-_MAX_COMMANDS:]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "owner": self.owner,
            "started": self.started,
            "closed": self.closed,
            "commands": [dict(c) for c in self.commands[-_MAX_COMMANDS:]],
        }

    @staticmethod
    def validate(raw: Any, owner: str) -> Tuple[bool, str]:
        """Strict shape check for a persisted session record.

        Requires: session_id/owner/started are non-empty bounded strings;
        owner matches the Program owner; closed is set (only closed records
        persist); commands is a list of valid command records.
        No coercion. Bool is not a valid string.
        """
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
# use data.get("studio_sessions", _MISSING) to distinguish.
_MISSING = object()


def _add_malformed(malformed: Dict[str, Any], key: str, raw: Any, error: str) -> None:
    """Add malformed evidence without overwriting earlier evidence.

    Multiple failures under the same key are preserved as a list, in
    observation order. Earlier evidence is never discarded.
    """
    entry = {"raw": raw, "error": error}
    if key in malformed:
        existing = malformed[key]
        if isinstance(existing, list):
            existing.append(entry)
        else:
            malformed[key] = [existing, entry]
    else:
        malformed[key] = [entry]


def validate_section(raw: Any, owner: str) -> Tuple[Dict[str, Dict[str, Any]], Optional[Dict[str, Any]]]:
    """Validate a persisted studio_sessions section with the strict schema.

    Returns (sessions, malformed). Sessions maps session_id -> record for
    valid closed records. Malformed is None when the section is absent
    (legacy, via _MISSING) or fully valid; otherwise it preserves the
    malformed records with per-record errors.

    Distinguishes (via the _MISSING sentinel):
    - absent (_MISSING): legacy, no sessions. Not malformed.
    - explicit null (None): malformed, preserved under "_section".
    - non-dict: malformed, preserved under "_section".
    - wrong version (including bool): malformed, preserved under "_section".
    - per-record failures: valid records kept, failures preserved by key.
    - previously-preserved "malformed" key: carried through; same-key
      failures are appended, not overwritten.

    Never raises for any input. No broad suppression needed by callers.
    """
    if raw is _MISSING:
        return {}, None
    if raw is None:
        malformed: Dict[str, Any] = {}
        _add_malformed(malformed, "_section", None, "explicit null is malformed, not legacy absence")
        return {}, malformed
    if not isinstance(raw, dict):
        malformed = {}
        _add_malformed(malformed, "_section", raw, "section not an object")
        return {}, malformed
    version = raw.get("version")
    # Strict: must be int 1. Bool is rejected (isinstance(True, int) is True,
    # so check explicitly). No coercion.
    if isinstance(version, bool) or not isinstance(version, int):
        malformed = {}
        _add_malformed(malformed, "_section", raw, "section version must be int 1")
        return {}, malformed
    if version != STUDIO_SECTION_VERSION:
        malformed = {}
        _add_malformed(malformed, "_section", raw, f"unsupported section version {version}")
        return {}, malformed
    raw_sessions = raw.get("sessions")
    if not isinstance(raw_sessions, dict):
        malformed = {}
        _add_malformed(malformed, "_section", raw, "sessions not an object")
        return {}, malformed
    valid: Dict[str, Dict[str, Any]] = {}
    malformed = {}
    for sid, rec in raw_sessions.items():
        if not isinstance(sid, str):
            _add_malformed(malformed, "_non_string_key", rec, "session key not a string")
            continue
        ok, err = StudioSession.validate(rec, owner)
        if not ok:
            _add_malformed(malformed, sid, rec, err)
            continue
        # Key/ID agreement: dict key must equal the record's session_id.
        if not isinstance(rec, dict) or rec.get("session_id") != sid:
            _add_malformed(malformed, sid, rec, "session key/ID mismatch")
            continue
        valid[sid] = dict(rec)
    # Carry through previously-preserved malformed evidence. Same-key
    # failures are appended, not overwritten.
    preserved = raw.get("malformed")
    if isinstance(preserved, dict):
        for k, v in preserved.items():
            if not isinstance(k, str):
                continue
            if isinstance(v, list):
                for entry in v:
                    if isinstance(entry, dict):
                        _add_malformed(malformed, k, entry.get("raw"), entry.get("error", "preserved"))
                    else:
                        _add_malformed(malformed, k, entry, "preserved")
            elif isinstance(v, dict) and "raw" in v:
                _add_malformed(malformed, k, v.get("raw"), v.get("error", "preserved"))
            else:
                _add_malformed(malformed, k, v, "preserved")
    # Retention: 10 most recent by started timestamp.
    ordered = sorted(valid.items(),
                     key=lambda kv: str(kv[1].get("started", "")),
                     reverse=True)[:_MAX_SESSIONS]
    return dict(ordered), (malformed if malformed else None)


def serialize_section(sessions: Any, malformed: Any, owner: str) -> Dict[str, Any]:
    """Serialize studio sessions with the shared strict schema.

    Valid closed records go to "sessions". Invalid records (active,
    malformed, foreign-owner, key/ID-mismatched) are preserved in
    "malformed", not silently saved as valid or discarded. This is the
    same schema the loader validates; serialization and restoration share
    the contract.

    Returns the section dict. Never raises for any input.
    """
    valid: Dict[str, Dict[str, Any]] = {}
    mal: Dict[str, Any] = {}
    if isinstance(sessions, dict):
        for sid, rec in sessions.items():
            if not isinstance(sid, str):
                _add_malformed(mal, "_non_string_key", rec, "session key not a string")
                continue
            ok, err = StudioSession.validate(rec, owner)
            if not ok:
                _add_malformed(mal, sid, rec, f"not serialized as valid: {err}")
                continue
            if not isinstance(rec, dict) or rec.get("session_id") != sid:
                _add_malformed(mal, sid, rec, "not serialized as valid: key/ID mismatch")
                continue
            valid[sid] = dict(rec)
    # Carry through existing malformed evidence.
    if isinstance(malformed, dict):
        for k, v in malformed.items():
            if not isinstance(k, str):
                continue
            if isinstance(v, list):
                for entry in v:
                    if isinstance(entry, dict):
                        _add_malformed(mal, k, entry.get("raw"), entry.get("error", "preserved"))
                    else:
                        _add_malformed(mal, k, entry, "preserved")
            elif isinstance(v, dict) and "raw" in v:
                _add_malformed(mal, k, v.get("raw"), v.get("error", "preserved"))
            else:
                _add_malformed(mal, k, v, "preserved")
    # Retention: 10 most recent.
    ordered = sorted(valid.items(),
                     key=lambda kv: str(kv[1].get("started", "")),
                     reverse=True)[:_MAX_SESSIONS]
    section: Dict[str, Any] = {
        "version": STUDIO_SECTION_VERSION,
        "sessions": dict(ordered),
    }
    if mal:
        section["malformed"] = mal
    return section


def _screen_protected(program: Any, obj: Any) -> bool:
    """Screen structured data for protected material. Fail-closed.

    Returns True if clean. Returns False if protected material is found
    OR if screening cannot be performed. Never raises. Shared by the
    public compose() API and the REPL handler.
    """
    try:
        from form.dell_matrix.inference_dock import (
            protected_values, contains_protected_decoded)
        protected = protected_values(program)

        def _check(o: Any) -> bool:
            if isinstance(o, dict):
                for k, v in o.items():
                    if isinstance(k, str) and contains_protected_decoded(k, protected):
                        return False
                    if not _check(v):
                        return False
                return True
            if isinstance(o, (list, tuple)):
                return all(_check(v) for v in o)
            if isinstance(o, str):
                return not contains_protected_decoded(o, protected)
            return True

        return _check(obj)
    except Exception:
        return False


class PerspectiveStudio:
    """Presentation adapter over R7.1 compose_views.

    The studio holds no authority. It delegates composition, derives the
    owner from the Program, and records bounded session evidence.
    The public compose() validates specs with the shared contract;
    callers must not assume normalized data.
    """

    WORKSHOP_ID = "perspective"

    def __init__(self, program: Any):
        self._program = program
        self._owner = program.owner
        self._session = StudioSession(
            session_id=str(uuid.uuid4()),
            owner=self._owner,
            started=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )

    @property
    def owner(self) -> str:
        return self._owner

    @property
    def session(self) -> StudioSession:
        return self._session

    def _record(self, kind: str, result: str) -> None:
        self._session.record(kind, result)

    def compose(self, specs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compose views via R7.1 compose_views.

        Enforces the complete collection contract: supported container,
        non-empty, eight-spec limit, per-spec validation, finite
        representable coordinates, and owner binding. Screens structured
        input for protected material before composition, and screens the
        detached output before release. Protection failure rejects with
        fixed codes; no reflected input or exception text.
        """
        from form.dell_matrix.perspective_views import Viewer, compose_views

        # Collection contract: supported container, non-empty, bounded.
        if not isinstance(specs, list):
            self._record("compose", FAIL_INVALID_SPEC)
            return {"ok": False, "status": FAIL_INVALID_SPEC,
                    "detail": "specs must be a list"}
        if not specs:
            self._record("compose", FAIL_INVALID_SPEC)
            return {"ok": False, "status": FAIL_INVALID_SPEC,
                    "detail": "specs must not be empty"}
        if len(specs) > _MAX_SPECS:
            self._record("compose", FAIL_INVALID_SPEC)
            return {"ok": False, "status": FAIL_INVALID_SPEC,
                    "detail": f"specs exceeds {_MAX_SPECS}"}

        # Protection: screen structured input before composition.
        # Direct API callers receive the same enforcement as the REPL.
        if not _screen_protected(self._program, specs):
            self._record("compose", FAIL_PROTECTED)
            return {"ok": False, "status": FAIL_PROTECTED,
                    "detail": "protected material rejected"}

        # Shared validation: do not assume normalized data.
        # Catch numeric conversion failures (e.g., OverflowError from
        # huge integers) and return fixed bounded rejection.
        normalized: List[Dict[str, Any]] = []
        try:
            for s in specs:
                ok, _, norm = validate_spec(s)
                if not ok:
                    self._record("compose", FAIL_INVALID_SPEC)
                    return {"ok": False, "status": FAIL_INVALID_SPEC,
                            "detail": "spec failed validation"}
                normalized.append(norm)  # type: ignore[arg-type]
        except (OverflowError, ValueError, TypeError, ArithmeticError):
            self._record("compose", FAIL_INVALID_SPEC)
            return {"ok": False, "status": FAIL_INVALID_SPEC,
                    "detail": "spec numeric conversion failed"}
        # Owner mismatch: reject any spec carrying a different owner.
        for s in normalized:
            if "owner" in s and s["owner"] != self._owner:
                self._record("compose", FAIL_OWNER_MISMATCH)
                return {"ok": False, "status": FAIL_OWNER_MISMATCH,
                        "detail": "spec owner does not match Program owner"}
        viewers = []
        try:
            for s in normalized:
                viewers.append(Viewer(
                    id=s["id"],
                    role=s["role"],
                    pos=(s["pos"][0], s["pos"][1]),
                    facing=s["facing"],
                    mode=s.get("mode"),
                ))
        except (OverflowError, ValueError, TypeError, ArithmeticError):
            self._record("compose", FAIL_INVALID_SPEC)
            return {"ok": False, "status": FAIL_INVALID_SPEC,
                    "detail": "viewer construction failed"}
        pairs = [(v, v.effective_mode()) for v in viewers]
        result = compose_views(self._program, pairs)

        # Protection: screen detached output before release. The compositor
        # may reflect canonical labels containing protected-format material.
        # If screening fails or finds protected material, reject without
        # releasing the output. Do not modify canonical Idea content.
        if not _screen_protected(self._program, result):
            self._record("compose", FAIL_PROTECTED)
            return {"ok": False, "status": FAIL_PROTECTED,
                    "detail": "protected material in output"}

        # Detachment: the compositor returns deep-copied views; the studio
        # never hands out its live session or the program's mutable state.
        self._record("compose",
                     f"ok={result.get('ok')} status={result.get('epistemic_status')} "
                     f"components={len(result.get('components', []))}")
        return result

    def legend(self) -> Dict[str, str]:
        self._record("legend", f"keys={len(LEGEND)}")
        return dict(LEGEND)

    def help_text(self) -> str:
        self._record("help", "shown")
        return (
            "Perspective Studio — scoped composition workshop.\n"
            "Commands while in studio:\n"
            "  compose <JSON specs>  Compose views. Specs: JSON array of objects\n"
            '    with keys id (string), role (string), pos ([x, y] finite numbers),\n'
            "    facing (N/S/E/W/NE/NW/SE/SW), mode (first/third/parts/whole, optional).\n"
            '    Example: compose [{"id":"v1","role":"user","pos":[0,0],"facing":"E"}]\n'
            "  legend                Show the inspectable layout legend.\n"
            "  help                  Show this text.\n"
            "  leave                 Save session evidence and exit the studio.\n"
            "Out-of-scope commands are rejected while the studio is active.\n"
            "Evidence: the 50 most recent commands per session are retained;\n"
            "earlier commands are not preserved. At most 10 sessions are kept."
        )

    def prepare_leave(self) -> Dict[str, Any]:
        """Build the closed session record WITHOUT mutating the studio.

        The caller stages this record, saves, and only discards the studio
        after successful persistence. On save failure the studio remains
        active and usable; prepare_leave() is idempotent.
        """
        closed_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        record = self._session.to_dict()
        record["closed"] = closed_at
        # The leave command itself is part of the closed record.
        cmds = list(record.get("commands", []))
        cmds.append({
            "kind": "leave",
            "time": closed_at,
            "result": "session closed",
        })
        record["commands"] = cmds[-_MAX_COMMANDS:]
        return record
