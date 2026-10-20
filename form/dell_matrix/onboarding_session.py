"""R7.4 (GDP draft 7.1.4) — disclosure onboarding / teach rhythm evidence.

Adopted decisions (Ace, 2026-10-20, "Adopt D1/D2 as recommended"):

- D1: a fourth disclosure level ``first-run`` below ``beginner`` — a
  guided surface that exists to be graduated from. Disclosure stays
  presentational at every level; it never gates dispatch.
- D2: the teach rhythm Show -> Explain -> Try -> Verify, applied to a
  short path (create, grow/confirm, look, save/load). The program
  demonstrates each move in the isolated demo owner (Show), says why
  in one line (Explain), the user performs the move in their own
  state inside a scoped session (Try), and the program checks the
  observable result and says plainly whether it happened (Verify).
  Completion is recorded only when Verify passes for the user's own
  Try steps.

This module supplies the session-evidence half (the REPL supplies the
scoped flow, mirroring the R7.2 studio / R7.3 workshop pattern):

- Session evidence is bounded (50 steps, 10 sessions), records only
  step kinds and fixed result codes, and persists only on leave via
  the canonical save with stage-then-save semantics.
- Persistence uses the shared strict schema pattern (third instance):
  absent section is legacy; explicit null / malformed is preserved
  evidence, never silently treated as completed or as legacy.

Onboarding state machine (section-level ``begun`` fact):

- Section absent (pre-feature persisted state): LEGACY. The owner is
  not demoted to first-run; their restored mode is untouched.
- Section present, ``begun`` False, no completed record: the owner
  has state under the new serializer but never began onboarding —
  legacy-equivalent; mode untouched.
- ``begun`` True, no completed record: onboarding is in progress for
  this owner; the starting level on load is ``first-run`` (leaving
  early keeps the level; it remains first-run on reload).
- A valid closed record with ``completed`` True: GRADUATED. A
  persisted ``first-run`` mode upgrades to ``beginner`` on load; any
  other persisted mode is kept (disclosure is presentational, the
  user may have moved up manually).
- Section-level malformation (unreadable version/begun/sessions):
  FAIL CLOSED — not completed, not legacy; starting level first-run,
  evidence preserved. A malformed record never proves completion.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

_MAX_STEPS = 50
_MAX_SESSIONS = 10

ONBOARDING_SECTION_VERSION = 1

FAIL_PROTECTED = "PROTECTED_MATERIAL"
FAIL_OUT_OF_SCOPE = "OUT_OF_SCOPE"
FAIL_SAVE = "SAVE_FAILED"

FIRST_RUN_MODE = "first-run"
GRADUATED_MODE = "beginner"

# The teach-rhythm path (D2). One authority for the flow: the REPL
# presents these moves in order and verifies each Try against the
# observable program state. ``try_stems`` are the accepted first
# tokens for the user's Try line at that move.
MOVES: List[Dict[str, Any]] = [
    {
        "id": "create",
        "title": "Create an idea",
        "explain": "Everything here starts as an idea placed on the "
                   "matrix; creating one is how work begins.",
        "try_stems": ("create",),
        "try_hint": "create an idea called <name> detail: <what it is> "
                    "goals: <what it is for>",
    },
    {
        "id": "grow_confirm",
        "title": "Grow, then confirm",
        "explain": "Grow proposes variations into the Nursery "
                   "quarantine; nothing enters your matrix until you "
                   "confirm it.",
        "try_stems": ("grow", "confirm"),
        "try_hint": "grow ideas 1  (then: proposals, confirm all)",
    },
    {
        "id": "look",
        "title": "Look around",
        "explain": "Look shows what your avatar sees from where it "
                   "stands; it is how you read the current state "
                   "before acting.",
        "try_stems": ("look", "show", "entities"),
        "try_hint": "look",
    },
    {
        "id": "save_load",
        "title": "Save and load",
        "explain": "Save writes your state to disk and load restores "
                   "it exactly; work survives restarts because it is "
                   "written down.",
        "try_stems": ("save",),
        "try_hint": "save",
    },
]

MOVE_IDS = tuple(m["id"] for m in MOVES)


def _is_valid_step(rec: Any) -> bool:
    """Strict step record check. No coercion. Mirrors workshop schema."""
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
class OnboardingSession:
    """One closed or active onboarding session record.

    Only step kinds and fixed result summaries are stored. Never raw
    input lines, grants, authority, or credentials.
    """
    session_id: str
    owner: str
    started: str
    closed: Optional[str] = None
    completed: bool = False
    steps: List[Dict[str, str]] = field(default_factory=list)
    # Runtime-only: index into MOVES for the move awaiting its Try.
    # Never serialized (to_dict controls the persisted shape).
    move_index: int = field(default=0, repr=False)

    @classmethod
    def open(cls, owner: str) -> "OnboardingSession":
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
            "completed": bool(self.completed),
            "steps": [dict(s) for s in self.steps[-_MAX_STEPS:]],
        }

    def closed_copy(self, completed: bool) -> Dict[str, Any]:
        """Build the closed record WITHOUT mutating the session.

        The caller stages this record, saves, and only discards the
        session after successful persistence. On save failure the
        session remains active and usable; closed_copy() is idempotent.
        """
        record = self.to_dict()
        record["closed"] = time.strftime(
            "%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        record["completed"] = bool(completed)
        steps = list(record.get("steps", []))
        steps.append({
            "kind": "complete" if completed else "leave",
            "time": record["closed"],
            "result": "completed recorded" if completed
                      else "leave recorded",
        })
        record["steps"] = steps[-_MAX_STEPS:]
        return record

    @staticmethod
    def validate(raw: Any, owner: str) -> Tuple[bool, str]:
        """Strict shape check for a persisted onboarding session record."""
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
        completed = raw.get("completed")
        if not isinstance(completed, bool):
            return False, "session.completed must be a bool"
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
# which is malformed. Python maps JSON null to None, so the loader must
# use data.get("onboarding_sessions", _MISSING) to distinguish.
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


def validate_section(raw: Any, owner: str
                     ) -> Tuple[Dict[str, Dict[str, Any]],
                                Optional[Dict[str, Any]], Dict[str, Any]]:
    """Validate a persisted onboarding_sessions section (strict schema).

    Returns (sessions, malformed, meta). meta keys:
      present           — the section key existed in the persisted data
      begun             — the section's begun fact (False when unreadable)
      section_malformed — the section itself could not be read (version,
                          begun, or sessions shape); fail closed
    Absent (_MISSING) is legacy; explicit null is malformed. Per-record
    failures are preserved by key; previously-preserved malformed
    evidence is carried through with same-key append. Never raises.
    """
    meta: Dict[str, Any] = {
        "present": raw is not _MISSING,
        "begun": False,
        "section_malformed": False,
    }
    if raw is _MISSING:
        return {}, None, meta
    if raw is None:
        malformed: Dict[str, Any] = {}
        _add_malformed(malformed, "_section", None,
                       "explicit null is malformed, not legacy absence")
        meta["section_malformed"] = True
        return {}, malformed, meta
    if not isinstance(raw, dict):
        malformed = {}
        _add_malformed(malformed, "_section", raw, "section not an object")
        meta["section_malformed"] = True
        return {}, malformed, meta
    version = raw.get("version")
    if isinstance(version, bool) or not isinstance(version, int):
        malformed = {}
        _add_malformed(malformed, "_section", raw,
                       "section version must be int 1")
        meta["section_malformed"] = True
        return {}, malformed, meta
    if version != ONBOARDING_SECTION_VERSION:
        malformed = {}
        _add_malformed(malformed, "_section", raw,
                       f"unsupported section version {version}")
        meta["section_malformed"] = True
        return {}, malformed, meta
    begun = raw.get("begun")
    if not isinstance(begun, bool):
        malformed = {}
        _add_malformed(malformed, "_section", raw,
                       "section begun must be a bool")
        meta["section_malformed"] = True
        return {}, malformed, meta
    meta["begun"] = begun
    raw_sessions = raw.get("sessions")
    if not isinstance(raw_sessions, dict):
        malformed = {}
        _add_malformed(malformed, "_section", raw, "sessions not an object")
        meta["section_malformed"] = True
        return {}, malformed, meta
    valid: Dict[str, Dict[str, Any]] = {}
    malformed = {}
    for sid, rec in raw_sessions.items():
        if not isinstance(sid, str):
            _add_malformed(malformed, "_non_string_key", rec,
                           "session key not a string")
            continue
        ok, err = OnboardingSession.validate(rec, owner)
        if not ok:
            _add_malformed(malformed, sid, rec, err)
            continue
        if not isinstance(rec, dict) or rec.get("session_id") != sid:
            _add_malformed(malformed, sid, rec, "session key/ID mismatch")
            continue
        valid[sid] = dict(rec)
    preserved = raw.get("malformed")
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
    ordered = sorted(valid.items(),
                     key=lambda kv: str(kv[1].get("started", "")),
                     reverse=True)[:_MAX_SESSIONS]
    return dict(ordered), (malformed if malformed else None), meta


def serialize_section(sessions: Any, malformed: Any, owner: str,
                      begun: Any = False) -> Dict[str, Any]:
    """Serialize onboarding sessions with the shared strict schema.

    Valid closed records go to "sessions". Invalid records (active,
    foreign-owner, key/ID-mismatched, non-bool completed) are preserved
    in "malformed", never silently saved as valid or discarded.
    ``begun`` is written as a strict bool (only True begins onboarding;
    any other value serializes as False). Never raises.
    """
    valid: Dict[str, Dict[str, Any]] = {}
    mal: Dict[str, Any] = {}
    if isinstance(sessions, dict):
        for sid, rec in sessions.items():
            if not isinstance(sid, str):
                _add_malformed(mal, "_non_string_key", rec,
                               "session key not a string")
                continue
            ok, err = OnboardingSession.validate(rec, owner)
            if not ok:
                _add_malformed(mal, sid, rec,
                               f"not serialized as valid: {err}")
                continue
            if not isinstance(rec, dict) or rec.get("session_id") != sid:
                _add_malformed(mal, sid, rec,
                               "not serialized as valid: key/ID mismatch")
                continue
            valid[sid] = dict(rec)
    if isinstance(malformed, dict):
        for k, v in malformed.items():
            if not isinstance(k, str):
                continue
            if isinstance(v, list):
                for entry in v:
                    if isinstance(entry, dict):
                        _add_malformed(mal, k, entry.get("raw"),
                                       entry.get("error", "preserved"))
                    else:
                        _add_malformed(mal, k, entry, "preserved")
            elif isinstance(v, dict) and "raw" in v:
                _add_malformed(mal, k, v.get("raw"),
                               v.get("error", "preserved"))
            else:
                _add_malformed(mal, k, v, "preserved")
    ordered = sorted(valid.items(),
                     key=lambda kv: str(kv[1].get("started", "")),
                     reverse=True)[:_MAX_SESSIONS]
    section: Dict[str, Any] = {
        "version": ONBOARDING_SECTION_VERSION,
        "begun": begun is True,
        "sessions": dict(ordered),
    }
    if mal:
        section["malformed"] = mal
    return section


def has_completed(sessions: Any) -> bool:
    """True iff a valid closed record proves onboarding completion."""
    if not isinstance(sessions, dict):
        return False
    return any(isinstance(rec, dict) and rec.get("completed") is True
               for rec in sessions.values())


def apply_restored_level(p: Any, sessions: Any, meta: Dict[str, Any]) -> None:
    """Apply the D1 starting-level rule after a restore.

    Mutates only ``p.ux_mode``. See the module docstring for the state
    machine. Legacy (absent section, or begun False without completion)
    leaves the restored mode untouched.
    """
    if not meta.get("present"):
        return  # legacy: pre-feature state, never demoted
    if meta.get("section_malformed"):
        # Fail closed: unreadable evidence proves neither completion
        # nor legacy. The not-graduated surface is first-run.
        p.ux_mode = FIRST_RUN_MODE
        return
    if has_completed(sessions):
        if getattr(p, "ux_mode", None) == FIRST_RUN_MODE:
            p.ux_mode = GRADUATED_MODE
        return
    if meta.get("begun"):
        p.ux_mode = FIRST_RUN_MODE


def mark_new_owner(p: Any) -> None:
    """Mark a brand-new owner (no persisted state) as first-run.

    Called only at canonical fresh-owner boundaries (persist load with
    no state file; REPL start with no state file). Sets the level and
    the begun fact in memory; both persist on the owner's next save.
    """
    p.ux_mode = FIRST_RUN_MODE
    p.onboarding_begun = True
    p.onboarding_sessions = {}
    p.onboarding_sessions_malformed = None
    p.onboarding_completed = False
