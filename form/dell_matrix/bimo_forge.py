"""R7.5 BIMO Forge — staged, named BIMO configurations.

Repository reality before R7.5: BIMOBody (form/dell_matrix/personas.py)
is the single authority for persona docking — slots, pilot, fuse() —
and the REPL reaches it ad hoc (`bimo dock <slot> <persona>`, ...).
Every dock mutates the ONE live configuration immediately; there are
no named configurations, no way to assemble a candidate arrangement
without disturbing the live body, and no configuration evidence.

The Forge adds exactly that, extending existing authorities only:

- A scoped REPL session (`forge`) stages a DETACHED copy of the live
  slots/pilot. Dock/undock/pilot/defaults/clear operate on the staged
  copy through BIMOBody's own methods; `preview` fuses the staged
  copy. The live body is untouched until an explicit commit.
- `save <name>` commits: the staged arrangement becomes the live body
  AND is stored as a named configuration, in one canonical save with
  stage-then-save semantics (full restore on failure).
- Named configurations persist in the `bimo_configurations` section
  and session evidence in `forge_sessions`, both under the shared
  strict schema (fourth/fifth instances of the pattern): bounded,
  owner-bound, malformed evidence preserved, absent = legacy.

Authority law (R6.4/R6.5, unchanged): personas and slots describe
behavior only. A configuration stores slot->persona mappings and a
pilot — nothing else. The schema has no grants, capabilities, or
authority fields, and validation rejects unknown slots and unknown
persona ids, so a hand-edited configuration cannot mint anything.
"""

from __future__ import annotations

import re
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
_MAX_CONFIGURATIONS = 10

FORGE_SECTION_VERSION = 1

# The kit's step check, under this module's historical name.
_is_valid_step = is_valid_step

FAIL_PROTECTED = "PROTECTED_MATERIAL"
FAIL_OUT_OF_SCOPE = "OUT_OF_SCOPE"
FAIL_SAVE = "SAVE_FAILED"

_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,47}$")


def normalize_config_name(name: Any) -> Optional[str]:
    """Canonical configuration name, or None if not a valid name."""
    if not isinstance(name, str):
        return None
    n = name.strip().lower()
    return n if _NAME_RE.match(n) else None


# ---------------------------------------------------------------------------
# Named configurations
# ---------------------------------------------------------------------------

def validate_configuration(raw: Any, owner: str) -> Tuple[bool, str]:
    """Strict shape check for one named BIMO configuration record."""
    from form.dell_matrix.personas import BIMO_SLOTS, normalize_persona_id
    if not isinstance(raw, dict):
        return False, "configuration must be an object"
    extra = set(raw) - {"name", "owner", "slots", "pilot", "saved"}
    if extra:
        return False, ("configuration has fields outside the schema "
                       "(slots/pilot only — no grants or authority fields)")
    name = raw.get("name")
    if normalize_config_name(name) is None or name != normalize_config_name(name):
        return False, "configuration.name must be a canonical name"
    o = raw.get("owner")
    if not isinstance(o, str) or o != owner:
        return False, "configuration.owner does not match Program owner"
    saved = raw.get("saved")
    if not isinstance(saved, str) or not saved or len(saved) > 128:
        return False, "configuration.saved must be a non-empty string"
    pilot = raw.get("pilot")
    if not isinstance(pilot, str) or normalize_persona_id(pilot) != pilot:
        return False, "configuration.pilot must be a known persona id"
    slots = raw.get("slots")
    if not isinstance(slots, dict):
        return False, "configuration.slots must be an object"
    for slot, pid in slots.items():
        if slot not in BIMO_SLOTS:
            return False, f"configuration.slots has unknown slot {slot!r}"
        if pid is not None and (
                not isinstance(pid, str)
                or normalize_persona_id(pid) != pid):
            return False, "configuration.slots values must be null or known persona ids"
    return True, ""


def make_configuration(name: str, owner: str, slots: Dict[str, Any],
                       pilot: str) -> Dict[str, Any]:
    """Build a configuration record from staged state (normalized)."""
    from form.dell_matrix.personas import BIMO_SLOTS
    return {
        "name": name,
        "owner": owner,
        "slots": {s: slots.get(s) for s in BIMO_SLOTS},
        "pilot": pilot,
        "saved": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


# ---------------------------------------------------------------------------
# Session evidence (mirrors the workshop/studio strict schema)
# ---------------------------------------------------------------------------

@dataclass
class ForgeSession:
    """One closed or active forge session record + runtime staging.

    The persisted shape is only the evidence fields (to_dict). The
    staged slots/pilot are runtime-only: they hold the candidate
    arrangement being built and are never serialized as evidence.
    Only step kinds and fixed result summaries are stored. Never raw
    input lines, grants, authority, or credentials.
    """
    session_id: str
    owner: str
    started: str
    closed: Optional[str] = None
    steps: List[Dict[str, str]] = field(default_factory=list)
    # Runtime-only staging (excluded from to_dict).
    staged_slots: Dict[str, Optional[str]] = field(
        default_factory=dict, repr=False)
    staged_pilot: str = field(default="mathelody", repr=False)

    @classmethod
    def open(cls, owner: str, live_slots: Dict[str, Any],
             live_pilot: str) -> "ForgeSession":
        from form.dell_matrix.personas import BIMO_SLOTS
        return cls(
            session_id=str(uuid.uuid4()),
            owner=owner,
            started=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            staged_slots={s: live_slots.get(s) for s in BIMO_SLOTS},
            staged_pilot=live_pilot,
        )

    def staged_body(self):
        """A detached BIMOBody holding the staged arrangement.

        All staging operations go through BIMOBody's own methods, so
        slot/persona validation has exactly one authority.
        """
        from form.dell_matrix.personas import BIMOBody
        body = BIMOBody(slots=dict(self.staged_slots),
                        pilot=self.staged_pilot)
        return body

    def adopt(self, body) -> None:
        """Adopt a staged body's arrangement after an operation."""
        self.staged_slots = dict(body.slots)
        self.staged_pilot = body.pilot

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
        """Strict shape check for a persisted forge session record."""
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
# which is malformed. Loaders use data.get(<section>, _MISSING).
# _MISSING is the session_section kit's one sentinel (P3/TD-2), and
# _add_malformed its one implementation. Both forge sections (sessions
# and configurations) delegate their mechanics to the kit; this module
# keeps the two record schemas and the section constants.
_MISSING = MISSING
_add_malformed = add_malformed


def validate_sessions_section(raw: Any, owner: str
                              ) -> Tuple[Dict[str, Dict[str, Any]],
                                         Optional[Dict[str, Any]]]:
    """Validate a persisted forge_sessions section. Never raises."""
    return validate_records_section(
        raw, version=FORGE_SECTION_VERSION, kind="sessions",
        validate_rec=lambda rec: ForgeSession.validate(rec, owner),
        id_field="session_id", max_keep=_MAX_SESSIONS,
        sort_field="started", key_not_string="session key not a string",
        mismatch="session key/ID mismatch")


def serialize_sessions_section(sessions: Any, malformed: Any,
                               owner: str) -> Dict[str, Any]:
    """Serialize forge sessions with the strict schema. Never raises."""
    return serialize_records_section(
        sessions, malformed, version=FORGE_SECTION_VERSION,
        kind="sessions",
        validate_rec=lambda rec: ForgeSession.validate(rec, owner),
        id_field="session_id", max_keep=_MAX_SESSIONS,
        sort_field="started", key_not_string="session key not a string",
        mismatch="not serialized as valid: key/ID mismatch")


def validate_configurations_section(raw: Any, owner: str
                                    ) -> Tuple[Dict[str, Dict[str, Any]],
                                               Optional[Dict[str, Any]]]:
    """Validate a persisted bimo_configurations section. Never raises."""
    return validate_records_section(
        raw, version=FORGE_SECTION_VERSION, kind="configurations",
        validate_rec=lambda rec: validate_configuration(rec, owner),
        id_field="name", max_keep=_MAX_CONFIGURATIONS,
        sort_field="saved",
        key_not_string="configuration key not a string",
        mismatch="configuration key/name mismatch")


def serialize_configurations_section(configs: Any, malformed: Any,
                                     owner: str) -> Dict[str, Any]:
    """Serialize named configurations with the strict schema."""
    return serialize_records_section(
        configs, malformed, version=FORGE_SECTION_VERSION,
        kind="configurations",
        validate_rec=lambda rec: validate_configuration(rec, owner),
        id_field="name", max_keep=_MAX_CONFIGURATIONS,
        sort_field="saved",
        key_not_string="configuration key not a string",
        mismatch="not serialized as valid: key/name mismatch")
