"""PP3 (post-plan, D5) — the unknowns register.

An unknown is a first-class state: something the matrix met and
could not resolve — a seed it could not parse, an atom that did
not execute, a field entry a docked judge flagged as
unverifiable. Before PP3 those moments evaporated (a result
message, a skipped flag) and the matrix could not discover what
it does not know because the not-knowing itself was never
recorded.

This module is the persisted section ``unknowns`` following the
session_section kit pattern (P3/TD-2): closed-shape records,
owner-bound, malformed preserved as evidence, absent = legacy.

The discipline mirrors the knowledge lifecycle: an unknown is
OBSERVED, never silently answered. It leaves OPEN only through
an explicit act carrying evidence — resolve (with the answer)
or mark unknowable (with the reason) — and the record keeps its
history either way. Recording is deduped by (subject, question):
a repeated encounter increments ``seen`` instead of piling up
rows, so recurrence itself becomes evidence.

The curated limitation knowledge base (form/mandell/
limitation_knowledge.py) is a different authority — hand-verified
system limitations. This register holds ENCOUNTERED unknowns;
neither duplicates the other.
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

_MAX_ENTRIES = 200

UNKNOWN_SECTION_VERSION = 1

STATUSES = ("OPEN", "RESOLVED", "UNKNOWABLE")

_ENTRY_KEYS = frozenset({
    "entry_id", "owner", "opened", "subject", "question", "source",
    "status", "seen", "resolution", "resolver", "closed"})


def _bounded_str(v: Any, limit: int) -> bool:
    return isinstance(v, str) and len(v) <= limit


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def new_entry(owner: str, subject: str, question: str,
              source: str) -> Dict[str, Any]:
    """Build one OPEN entry. Raises ValueError on bad shape —
    callers on capture paths go through register_encounter, which
    never raises."""
    entry = {
        "entry_id": uuid.uuid4().hex,
        "owner": owner,
        "opened": _now(),
        "subject": subject,
        "question": question,
        "source": source,
        "status": "OPEN",
        "seen": 1,
        "resolution": "",
        "resolver": "",
        "closed": "",
    }
    ok, why = validate(entry, owner)
    if not ok:
        raise ValueError(f"unknown entry invalid: {why}")
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
    if not _bounded_str(entry["opened"], 32) or not entry["opened"]:
        return False, "opened invalid"
    if not _bounded_str(entry["subject"], 200) or not entry["subject"]:
        return False, "subject invalid"
    if not _bounded_str(entry["question"], 1000) \
            or not entry["question"]:
        return False, "question invalid"
    if not _bounded_str(entry["source"], 120) or not entry["source"]:
        return False, "source invalid"
    if entry["status"] not in STATUSES:
        return False, "status invalid"
    if type(entry["seen"]) is not int or entry["seen"] < 1:
        return False, "seen invalid"
    if not _bounded_str(entry["resolution"], 1000):
        return False, "resolution invalid"
    if not _bounded_str(entry["resolver"], 200):
        return False, "resolver invalid"
    if not _bounded_str(entry["closed"], 32):
        return False, "closed invalid"
    if entry["status"] == "OPEN":
        if entry["resolution"] or entry["resolver"] or entry["closed"]:
            return False, "open entry carries a resolution"
    else:
        if not entry["resolution"]:
            return False, "closed entry lacks a resolution"
        if not entry["resolver"]:
            return False, "closed entry lacks a resolver"
        if not entry["closed"]:
            return False, "closed entry lacks a closed stamp"
    return True, ""


# Sentinel for absent section key (legacy). Distinct from explicit
# null, which is malformed — the kit's one sentinel.
_MISSING = MISSING


def validate_section(raw: Any, owner: str
                     ) -> Tuple[Dict[str, Dict[str, Any]],
                                Optional[Dict[str, Any]]]:
    """Validate a persisted unknowns section. Never raises."""
    return validate_records_section(
        raw, version=UNKNOWN_SECTION_VERSION, kind="entries",
        validate_rec=lambda rec: validate(rec, owner),
        id_field="entry_id", max_keep=_MAX_ENTRIES,
        sort_field="opened", key_not_string="entry key not a string",
        mismatch="entry key/ID mismatch")


def serialize_section(entries: Any, malformed: Any,
                      owner: str) -> Dict[str, Any]:
    """Serialize unknowns with the strict schema. Never raises."""
    return serialize_records_section(
        entries, malformed, version=UNKNOWN_SECTION_VERSION,
        kind="entries",
        validate_rec=lambda rec: validate(rec, owner),
        id_field="entry_id", max_keep=_MAX_ENTRIES,
        sort_field="opened", key_not_string="entry key not a string",
        mismatch="not serialized as valid: key/ID mismatch")


# ---------------------------------------------------------------------------
# Register operations on a Program (lazy attach — the pattern the
# SD sections use: absent attributes mean an empty register).
# ---------------------------------------------------------------------------

def attach(program: Any) -> Dict[str, Dict[str, Any]]:
    """Return the program's register dict, attaching an empty one
    (plus its malformed sidecar) when absent."""
    entries = getattr(program, "unknowns", None)
    if not isinstance(entries, dict):
        entries = {}
        program.unknowns = entries
        if getattr(program, "unknowns_malformed", None) is None:
            program.unknowns_malformed = None
    return entries


def register_encounter(program: Any, subject: str, question: str,
                       source: str) -> Tuple[Optional[Dict[str, Any]],
                                              bool]:
    """Record one encountered unknown, in memory only (persistence
    rides the program's normal saves, like outcome recording).

    Dedup: an OPEN entry with the same (subject, question) absorbs
    the encounter — ``seen`` increments and the existing entry is
    returned with created=False. A RESOLVED/UNKNOWABLE match does
    NOT absorb: re-encountering a settled question is a new fact
    and opens a fresh entry. Never raises; a malformed encounter
    returns (None, False)."""
    try:
        subject = str(subject)[:200]
        question = str(question)[:1000]
        source = str(source)[:120]
        if not subject or not question or not source:
            return None, False
        entries = attach(program)
        for entry in entries.values():
            if entry.get("status") == "OPEN" \
                    and entry.get("subject") == subject \
                    and entry.get("question") == question:
                entry["seen"] = int(entry.get("seen") or 1) + 1
                return entry, False
        entry = new_entry(program.owner, subject, question, source)
        entries[entry["entry_id"]] = entry
        return entry, True
    except Exception:
        return None, False


def list_entries(program: Any, status: Optional[str] = None
                 ) -> List[Dict[str, Any]]:
    """Copies of register entries, OPEN first then by opened."""
    entries = attach(program)
    out = [dict(e) for e in entries.values()
           if status is None or e.get("status") == status]
    out.sort(key=lambda e: (e.get("status") != "OPEN",
                            e.get("opened") or ""))
    return out


def close_entry(program: Any, entry_id: str, status: str,
                resolution: str, resolver: str) -> Dict[str, Any]:
    """The discovery path's gate: an unknown leaves OPEN only with
    evidence — a non-empty resolution (the answer, or why it is
    unknowable) and a named resolver. Returns a result dict; on
    refusal the entry is untouched."""
    if status not in ("RESOLVED", "UNKNOWABLE"):
        return {"ok": False, "reason": "bad_status"}
    if not isinstance(resolution, str) or not resolution.strip():
        return {"ok": False, "reason": "resolution_required",
                "detail": "An unknown closes only with evidence: "
                          "the answer, or why it cannot be known."}
    if not isinstance(resolver, str) or not resolver.strip():
        return {"ok": False, "reason": "resolver_required"}
    entries = attach(program)
    entry = entries.get(entry_id)
    if entry is None:
        return {"ok": False, "reason": "unknown_entry"}
    if entry.get("status") != "OPEN":
        return {"ok": False, "reason": "already_closed",
                "status": entry.get("status")}
    entry["status"] = status
    entry["resolution"] = resolution.strip()[:1000]
    entry["resolver"] = resolver.strip()[:200]
    entry["closed"] = _now()
    ok, why = validate(entry, program.owner)
    if not ok:  # defensive: restore OPEN rather than persist rot
        entry["status"] = "OPEN"
        entry["resolution"] = ""
        entry["resolver"] = ""
        entry["closed"] = ""
        return {"ok": False, "reason": f"invalid_close: {why}"}
    return {"ok": True, "entry": dict(entry)}
