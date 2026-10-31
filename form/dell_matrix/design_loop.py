"""SD-5 (master plan P8) — the inside-out loop ledger.

The loop's receipt chain, in one place. A design proposal's life
spans systems: filed by a docked session in the dev-scope matrix
(SD-1 evidence), recommended on by the scoped Director (SD-4
records), decided by the human gate (the canonical confirm), and
implemented by the trusted host in the repository (a merged PR).
This module is the persisted section ``design_loop`` that ties
the chain together per proposal, plus `chain()` — the single
assembly a reviewer reads after the fact:

    filed        who filed it, in which dock session
    gate         the Director's recommendations + the human
                 gate's decision (from the proposal's status)
    implemented  the PR number / merge SHA the host recorded

Events are append-only records (session_section kit pattern:
closed shape, owner-bound, malformed preserved, absent =
legacy). Recording an event never changes a proposal; the
human gate remains the sole decision owner, and the host's
implementation record is a claim the PR itself verifies.
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional, Tuple

from form.dell_matrix.session_section import (
    MISSING,
    oldest_key,
    serialize_records_section,
    validate_records_section,
)

# The dedicated dev-scope owner for inside-out development.
DEV_OWNER = "DellMatrixDev"

_MAX_EVENTS = 200

DESIGN_LOOP_SECTION_VERSION = 1

EVENTS = ("filed", "gate", "implemented")

_ENTRY_KEYS = frozenset({
    "entry_id", "owner", "ts", "pid", "event", "actor", "note",
    "pr", "merge_sha"})


def _bounded_str(v: Any, limit: int) -> bool:
    return isinstance(v, str) and len(v) <= limit


def new_event(owner: str, pid: str, event: str, *, actor: str = "",
              note: str = "", pr: int = 0,
              merge_sha: str = "") -> Dict[str, Any]:
    entry = {
        "entry_id": uuid.uuid4().hex,
        "owner": owner,
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "pid": pid,
        "event": event,
        "actor": actor,
        "note": note,
        "pr": pr,
        "merge_sha": merge_sha,
    }
    ok, why = validate(entry, owner)
    if not ok:
        raise ValueError(f"design loop event invalid: {why}")
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
    if not _bounded_str(entry["pid"], 120) or not entry["pid"]:
        return False, "pid invalid"
    if entry["event"] not in EVENTS:
        return False, "event invalid"
    if not _bounded_str(entry["actor"], 200):
        return False, "actor invalid"
    if not _bounded_str(entry["note"], 1000):
        return False, "note invalid"
    if not isinstance(entry["pr"], int) or entry["pr"] < 0:
        return False, "pr invalid"
    if not _bounded_str(entry["merge_sha"], 64):
        return False, "merge_sha invalid"
    if entry["event"] == "implemented" and entry["pr"] <= 0:
        return False, "implemented event needs a PR number"
    return True, ""


_MISSING = MISSING


def validate_section(raw: Any, owner: str
                     ) -> Tuple[Dict[str, Dict[str, Any]],
                                Optional[Dict[str, Any]]]:
    """Validate a persisted design_loop section. Never raises."""
    return validate_records_section(
        raw, version=DESIGN_LOOP_SECTION_VERSION, kind="entries",
        validate_rec=lambda rec: validate(rec, owner),
        id_field="entry_id", max_keep=_MAX_EVENTS,
        sort_field="ts", key_not_string="entry key not a string",
        mismatch="entry key/ID mismatch")


def serialize_section(entries: Any, malformed: Any,
                      owner: str, extra: Any = None) -> Dict[str, Any]:
    """Serialize design-loop events with the strict schema. Never
    raises."""
    return serialize_records_section(
        entries, malformed, version=DESIGN_LOOP_SECTION_VERSION,
        kind="entries",
        validate_rec=lambda rec: validate(rec, owner),
        id_field="entry_id", max_keep=_MAX_EVENTS,
        sort_field="ts", key_not_string="entry key not a string",
        mismatch="not serialized as valid: key/ID mismatch",
        extra=extra)


def record_event(program: Any, pid: str, event: str, **kw) -> Dict[str, Any]:
    """Append one loop event to the program's section and save
    (best-effort, mirroring dock evidence discipline)."""
    entry = new_event(getattr(program, "owner", ""), pid, event, **kw)
    entries = getattr(program, "design_loop", None)
    if entries is None:
        entries = {}
        program.design_loop = entries
    entries[entry["entry_id"]] = entry
    while len(entries) > _MAX_EVENTS:
        # DAF-05: evict under the shared explicit oldest-first
        # policy; dict order after a reload is newest-first and
        # must never choose the victim.
        entries.pop(oldest_key(entries))
        # AF-4: count the eviction at the moment/place of loss
        # (PP2b B2); the serialize backstop never sees a
        # population this writer already trimmed to the cap.
        total = getattr(program, "design_loop_dropped_total", 0)
        if not isinstance(total, int) or isinstance(total, bool) \
                or total < 0:
            total = 0
        program.design_loop_dropped_total = total + 1
    try:
        program.save()
    except Exception:
        pass
    return entry


def chain(program: Any, pid: str) -> Dict[str, Any]:
    """Assemble one proposal's full loop receipt chain.

    Sources: the Nursery proposal itself, the SD-1 dock session
    evidence (filing provenance), the SD-4 Director records
    (recommendations), this section's events (filed / gate /
    implemented), and the proposal's live status (the gate's
    outcome)."""
    prop = program.nursery.proposals.get(pid)
    out: Dict[str, Any] = {
        "pid": pid,
        "found": prop is not None,
        "proposal": None,
        "filed": None,
        "recommendations": [],
        "gate": None,
        "implemented": None,
        "events": [],
    }
    if prop is not None:
        out["proposal"] = {
            "label": prop.label, "kind": prop.kind,
            "status": prop.status, "origin": prop.origin,
            "reason": prop.reason, "detail": prop.detail,
            "goals": list(prop.goals),
        }
    for rec in (getattr(program, "dock_sessions", None) or
                {}).values():
        for e in rec.get("proposals") or []:
            if e.get("pid") == pid:
                out["filed"] = {
                    "subject": rec.get("subject"),
                    "provider": rec.get("provider"),
                    "model": e.get("model"),
                    "task": e.get("task"),
                    "session_id": rec.get("session_id"),
                    "origin": e.get("origin"),
                    "ts": e.get("ts"),
                }
    for e in (getattr(program, "director_records", None) or
              {}).values():
        if e.get("pid") == pid and e.get("kind") == "recommendation":
            out["recommendations"].append({
                "decision": e.get("decision"),
                "reason": e.get("reason"),
                "subject": e.get("subject"),
                "ts": e.get("ts"),
                "entry_id": e.get("entry_id"),
            })
    events: List[Dict[str, Any]] = [
        e for e in (getattr(program, "design_loop", None) or
                    {}).values() if e.get("pid") == pid]
    events.sort(key=lambda e: e.get("ts", ""))
    out["events"] = events
    for e in events:
        if e["event"] == "gate":
            out["gate"] = {"actor": e.get("actor"),
                           "note": e.get("note"), "ts": e.get("ts")}
        elif e["event"] == "implemented":
            out["implemented"] = {"pr": e.get("pr"),
                                  "merge_sha": e.get("merge_sha"),
                                  "actor": e.get("actor"),
                                  "ts": e.get("ts")}
    return out
