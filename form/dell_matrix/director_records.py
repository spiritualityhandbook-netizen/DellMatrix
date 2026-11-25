"""SD-4 (master plan P7) — Director record section.

The scoped Director's acts are RECORDS, never decisions: a
recommendation to accept or reject, an evidence request, a
directive proposal link, and — just as important — a record of
every refusal (an out-of-scope or malformed attempt is evidence,
not silence). This module is the persisted section
``director_records`` holding those entries, following the
session_section kit pattern (P3/TD-2): closed-shape records,
owner-bound, malformed preserved as evidence, absent = legacy.

An entry NEVER changes a proposal's status. AcceptancePolicy is
untouched by this section; the human gate reads recommendations
as advice with provenance (who recommended, why, when), nothing
more.
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Dict, Optional, Tuple

from form.dell_matrix.session_section import (
    MISSING,
    serialize_records_section,
    validate_records_section,
)

_MAX_ENTRIES = 200

DIRECTOR_SECTION_VERSION = 1

KINDS = ("recommendation", "evidence_request", "directive", "refusal")
DECISIONS = ("accept", "reject")

_ENTRY_KEYS = frozenset({
    "entry_id", "owner", "ts", "session_id", "subject", "kind",
    "pid", "decision", "reason", "note"})


def _bounded_str(v: Any, limit: int) -> bool:
    return isinstance(v, str) and len(v) <= limit


def new_entry(owner: str, session_id: str, subject: str, kind: str,
              *, pid: str = "", decision: str = "", reason: str = "",
              note: str = "") -> Dict[str, Any]:
    """Build one entry. Callers (director_session) validate the
    semantics; this constructor enforces the persisted shape."""
    entry = {
        "entry_id": uuid.uuid4().hex,
        "owner": owner,
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "session_id": session_id,
        "subject": subject,
        "kind": kind,
        "pid": pid,
        "decision": decision,
        "reason": reason,
        "note": note,
    }
    ok, why = validate(entry, owner)
    if not ok:
        raise ValueError(f"director entry invalid: {why}")
    return entry


def validate(entry: Any, owner: str) -> Tuple[bool, str]:
    if not isinstance(entry, dict):
        return False, "entry not an object"
    if set(entry.keys()) != _ENTRY_KEYS:
        return False, "entry keys mismatch"
    if entry["owner"] != owner:
        return False, "entry owner mismatch"
    if not _bounded_str(entry["entry_id"], 64) or not entry["entry_id"]:
        return False, "entry_id invalid"
    if not _bounded_str(entry["ts"], 32) or not entry["ts"]:
        return False, "ts invalid"
    if not _bounded_str(entry["session_id"], 64):
        return False, "session_id invalid"
    if not _bounded_str(entry["subject"], 200) or not entry["subject"]:
        return False, "subject invalid"
    if entry["kind"] not in KINDS:
        return False, "kind invalid"
    if not _bounded_str(entry["pid"], 120):
        return False, "pid invalid"
    if entry["decision"] not in DECISIONS + ("",):
        return False, "decision invalid"
    if entry["kind"] == "recommendation" \
            and entry["decision"] not in DECISIONS:
        return False, "recommendation needs a decision"
    if not _bounded_str(entry["reason"], 1000):
        return False, "reason invalid"
    if not _bounded_str(entry["note"], 1000):
        return False, "note invalid"
    return True, ""


# Sentinel for absent section key (legacy). Distinct from explicit
# null, which is malformed — the kit's one sentinel.
_MISSING = MISSING


def validate_section(raw: Any, owner: str
                     ) -> Tuple[Dict[str, Dict[str, Any]],
                                Optional[Dict[str, Any]]]:
    """Validate a persisted director_records section. Never raises."""
    return validate_records_section(
        raw, version=DIRECTOR_SECTION_VERSION, kind="entries",
        validate_rec=lambda rec: validate(rec, owner),
        id_field="entry_id", max_keep=_MAX_ENTRIES,
        sort_field="ts", key_not_string="entry key not a string",
        mismatch="entry key/ID mismatch")


def serialize_section(entries: Any, malformed: Any,
                      owner: str, extra: Any = None) -> Dict[str, Any]:
    """Serialize director entries with the strict schema. Never
    raises."""
    return serialize_records_section(
        entries, malformed, version=DIRECTOR_SECTION_VERSION,
        kind="entries",
        validate_rec=lambda rec: validate(rec, owner),
        id_field="entry_id", max_keep=_MAX_ENTRIES,
        sort_field="ts", key_not_string="entry key not a string",
        mismatch="not serialized as valid: key/ID mismatch",
        extra=extra)
