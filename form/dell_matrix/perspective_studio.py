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

_VALID_FACINGS = frozenset({"N", "S", "E", "W", "NE", "NW", "SE", "SW"})
_VALID_MODES = frozenset({"first", "third", "parts", "whole"})

# Inspectable layout legend. Descriptive only: these define what the
# presentation fields mean, not what they authorize or prove.
LEGEND: Dict[str, str] = {
    "position": "Canonical plane coordinates (x, y) of the observed unit.",
    "label": "Display label of the observed unit.",
    "skin": "Presentation metadata only; carries no authority or truth claim.",
    "epistemic_status": "Verification standing of the view (e.g., REAL, PARTIAL); "
                        "not accepted truth and not permission.",
    "viewer": "Attribution: which viewer specification produced this component.",
    "requested_mode": "The observation mode requested (first/third/parts/whole).",
    "source": "Provenance of the observation data.",
}

STUDIO_COMMANDS = ("compose", "legend", "help", "leave")


def _is_finite_number(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def validate_spec(raw: Any) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """Validate one caller-supplied viewer spec.

    Returns (ok, error, normalized). No eval, no attribute access,
    no permissive string coercion. Finite numbers only. Bounded input.
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
    # owner: if supplied, must match the Program owner (checked by caller);
    # reject unexpected keys to keep the schema explicit.
    allowed = {"id", "role", "pos", "facing", "mode", "owner"}
    extra = set(raw.keys()) - allowed
    if extra:
        return False, f"spec has unexpected keys: {sorted(extra)}", None
    normalized = {
        "id": vid,
        "role": role,
        "pos": [float(pos[0]), float(pos[1])],
        "facing": facing,
        "mode": mode,
    }
    if "owner" in raw:
        normalized["owner"] = raw["owner"]
    return True, "", normalized


def parse_specs_json(text: str) -> Tuple[bool, str, Optional[List[Dict[str, Any]]]]:
    """Parse and validate a JSON array of viewer specs.

    Bounded input: rejects payloads over _MAX_JSON_BYTES and arrays
    over _MAX_SPECS. Every spec goes through validate_spec.
    """
    if len(text.encode("utf-8")) > _MAX_JSON_BYTES:
        return False, f"specs JSON exceeds {_MAX_JSON_BYTES} bytes", None
    try:
        raw = json.loads(text)
    except (json.JSONDecodeError, ValueError) as exc:
        return False, f"malformed JSON: {exc}", None
    if not isinstance(raw, list):
        return False, "specs must be a JSON array", None
    if not raw:
        return False, "specs array must not be empty", None
    if len(raw) > _MAX_SPECS:
        return False, f"specs array exceeds {_MAX_SPECS} entries", None
    out: List[Dict[str, Any]] = []
    for i, item in enumerate(raw):
        ok, err, norm = validate_spec(item)
        if not ok:
            return False, f"spec[{i}]: {err}", None
        out.append(norm)  # type: ignore[arg-type]
    return True, "", out


@dataclass
class StudioSession:
    """One closed or active studio session record.

    Only presentation specifications and bounded evidence are stored.
    Never grants, authority, or raw credentials.
    """
    session_id: str
    owner: str
    started: str
    closed: Optional[str] = None
    commands: List[Dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "owner": self.owner,
            "started": self.started,
            "closed": self.closed,
            "commands": [
                {
                    "kind": str(c.get("kind", ""))[:32],
                    "time": str(c.get("time", ""))[:32],
                    "result": str(c.get("result", ""))[:240],
                }
                for c in self.commands
            ][-50:],
        }

    @staticmethod
    def validate(raw: Any) -> Tuple[bool, str]:
        """Shape check for a persisted session record."""
        if not isinstance(raw, dict):
            return False, "session must be an object"
        for key in ("session_id", "owner", "started"):
            v = raw.get(key)
            if not isinstance(v, str) or not v or len(v) > 128:
                return False, f"session.{key} must be a non-empty string (max 128)"
        closed = raw.get("closed")
        if closed is not None and (not isinstance(closed, str) or len(closed) > 128):
            return False, "session.closed must be a string or null"
        cmds = raw.get("commands")
        if cmds is not None:
            if not isinstance(cmds, list):
                return False, "session.commands must be an array"
            for c in cmds:
                if not isinstance(c, dict):
                    return False, "session command must be an object"
                for k in ("kind", "time", "result"):
                    v = c.get(k)
                    if v is not None and not isinstance(v, str):
                        return False, f"session command.{k} must be a string"
        return True, ""


class PerspectiveStudio:
    """Presentation adapter over R7.1 compose_views.

    The studio holds no authority. It delegates composition, derives the
    owner from the Program, and records bounded session evidence.
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
        self._session.commands.append({
            "kind": kind,
            "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "result": result,
        })

    def compose(self, specs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compose views via R7.1 compose_views. No hardcoded composition."""
        from form.dell_matrix.perspective_views import Viewer, compose_views

        # Owner mismatch: reject any spec carrying a different owner.
        for s in specs:
            if "owner" in s and s["owner"] != self._owner:
                self._record("compose", "rejected: owner mismatch")
                return {"ok": False, "status": "OWNER_MISMATCH",
                        "detail": "spec owner does not match Program owner"}
        viewers = []
        for s in specs:
            viewers.append(Viewer(
                id=s["id"],
                role=s["role"],
                pos=(s["pos"][0], s["pos"][1]),
                facing=s["facing"],
                mode=s.get("mode"),
            ))
        # Caller supplies the mode per spec; default to whole-view.
        pairs = [(v, v.effective_mode()) for v in viewers]
        result = compose_views(self._program, pairs)
        # Detachment: the studio never hands out its live session or the
        # program's mutable state; the result is already a detached report.
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
            "Out-of-scope commands are rejected while the studio is active."
        )

    def close(self) -> StudioSession:
        """Close the session record. Does not persist; caller saves."""
        self._session.closed = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self._record("leave", "session closed")
        return self._session
