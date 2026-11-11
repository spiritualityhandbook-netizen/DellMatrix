"""SD-1 (master plan P4) — dock session evidence section.

Every docked inference session (form/dell_matrix/inference_dock.py)
leaves a persisted evidence record in the program-state section
``dock_sessions``, following the ConnectionSession section pattern
(P3/TD-2 session_section kit): closed-shape records, owner-bound,
malformed preserved as evidence, absent = legacy.

One deliberate difference from the interaction sections: a dock
record may persist OPEN (``closed`` is null). A dock session is a
capability session, not an interaction: proposals it creates are
durable in the Nursery the moment they land, so their session link
must be durable at the same moment — not only after a polite
undock. The record is upserted into program state at dock time and
updated in place on every successful propose().

What the record holds (evidence, never authority):
- who/what docked: subject (host-established), provider, model
  label, task kind, snap registration name;
- when: started / closed timestamps;
- per proposal: the Nursery pid, the origin string exactly as
  stamped, the reason exactly as stored, the ACTUAL model the
  transport reported, a SHA-256 of the exact prompt text sent,
  a bounded prompt summary, and a snapshot id = SHA-256 of the
  canonical JSON of the validated context actually sent (null when
  no context was sent).

Prompts are never stored in full; fetched/credential material never
enters this section (propose() screens before evidence is written).

DD-37 (plan SS12.36c/d, C8.Roster): the section is TWO TIERS.
The old 10-record rotation (charter B2 counted retention) is
retired for dock sessions — a still-docked session that started
before 10 newer ones was silently evicted, which Ace's ruling
forbids. Section version 2 persists:

- LIVE tier (``sessions``): every OPEN record, uncapped, full
  detail — the roster of currently docked Psalms;
- HISTORY tier (``history``): every CLOSED record, compacted to
  identity fields plus per-proposal provenance digests
  (pid/ts/task/model/origin — the fields the review joins read),
  complete coverage, nothing dropped.

Compaction supersedes B2 rotation for dock history: the section's
``dropped_total`` (carried by persist.py) is the frozen historical
count of evictions by the retired rotation — it never grows under
this contract, is never reset, and never counts a compaction.
In memory both tiers live in ``program.dock_sessions`` as full
records (history records hold digest proposal entries); the tier
split exists only at the persistence boundary. Version 1 sections
load whole, all records at full detail.
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional, Tuple

from form.dell_matrix.session_section import (
    MISSING,
    add_malformed,
    carry_preserved,
    collect_valid,
    section_shell,
)

_MAX_PROPOSALS = 50

DOCK_SECTION_VERSION = 2
_LEGACY_SECTION_VERSION = 1

# History-tier provenance digest: the per-proposal fields the
# review joins (repl._show_proposals, design_loop.chain) read.
# Compaction drops the rest of the entry (reason, prompt hash /
# summary / char count, snapshot id) — never the pid->session link.
_DIGEST_FIELDS = ("pid", "ts", "task", "model", "origin")

_HEX = frozenset("0123456789abcdef")


def _is_hex64(v: Any) -> bool:
    return isinstance(v, str) and len(v) == 64 and all(c in _HEX for c in v)


def _bounded_str(v: Any, limit: int) -> bool:
    return isinstance(v, str) and len(v) <= limit


def new_record(owner: str, subject: str, provider: str, model: str,
               task: str, snap_name: str) -> Dict[str, Any]:
    """Build a fresh open evidence record for a docked session."""
    return {
        "session_id": str(uuid.uuid4()),
        "owner": owner,
        "subject": subject,
        "provider": provider,
        "model": model,
        "task": task,
        "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "closed": None,
        "snap_name": snap_name,
        "proposals": [],
        # PP2b (charter ruling B2): entries evicted by the
        # proposals bound are counted, so the loss is measurable
        # instead of silent.
        "dropped": 0,
    }


def append_proposal(record: Dict[str, Any], entry: Dict[str, Any]) -> None:
    """Append one proposal-evidence entry, enforcing the bound.

    Beyond _MAX_PROPOSALS the oldest entries are dropped: the record
    is bounded evidence of the session's most recent work, and the
    Nursery itself remains the complete proposal ledger.
    """
    props = record.setdefault("proposals", [])
    props.append(entry)
    if len(props) > _MAX_PROPOSALS:
        excess = len(props) - _MAX_PROPOSALS
        del props[:excess]
        # PP2b (B2): count the eviction on the record itself.
        cur = record.get("dropped")
        record["dropped"] = (cur if isinstance(cur, int)
                              and not isinstance(cur, bool)
                              and cur >= 0 else 0) + excess


def close_record(record: Dict[str, Any]) -> None:
    record["closed"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _is_valid_entry(e: Any) -> bool:
    if not isinstance(e, dict):
        return False
    if not _bounded_str(e.get("pid"), 80) or not e.get("pid"):
        return False
    if not _bounded_str(e.get("ts"), 128) or not e.get("ts"):
        return False
    if not _bounded_str(e.get("task"), 40):
        return False
    if not _bounded_str(e.get("reason"), 160):
        return False
    if not _bounded_str(e.get("origin"), 120):
        return False
    if not _is_hex64(e.get("prompt_hash")):
        return False
    if not _bounded_str(e.get("prompt_summary"), 80):
        return False
    pc = e.get("prompt_chars")
    if not isinstance(pc, int) or isinstance(pc, bool) or pc < 0:
        return False
    snap = e.get("snapshot_id")
    if snap is not None and not _is_hex64(snap):
        return False
    if not _bounded_str(e.get("model"), 120):
        return False
    return True


def validate(raw: Any, owner: str) -> Tuple[bool, str]:
    """Strict shape check for a persisted dock session record."""
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
    for key, limit in (("subject", 200), ("provider", 80),
                       ("model", 120), ("task", 40), ("snap_name", 120)):
        if not _bounded_str(raw.get(key), limit):
            return False, f"session.{key} must be a string (max {limit})"
    closed = raw.get("closed")
    if closed is not None:
        if not isinstance(closed, str) or not closed or len(closed) > 128:
            return False, "session.closed must be null or a timestamp"
    props = raw.get("proposals")
    if not isinstance(props, list):
        return False, "session.proposals must be an array"
    if len(props) > _MAX_PROPOSALS:
        return False, f"session.proposals exceeds {_MAX_PROPOSALS}"
    for e in props:
        if not _is_valid_entry(e):
            return False, "session.proposals has an invalid entry"
    # PP2b (B2): the eviction counter, when present, must be a
    # non-negative int. Absent is legacy (pre-PP2b records).
    dropped = raw.get("dropped")
    if dropped is not None:
        if not isinstance(dropped, int) or isinstance(dropped, bool) \
                or dropped < 0:
            return False, "session.dropped must be a non-negative int"
    return True, ""


def _is_valid_digest_entry(e: Any) -> bool:
    """A history-tier provenance digest: exactly the join fields,
    at the same bounds as the full entry's."""
    if not isinstance(e, dict):
        return False
    if not _bounded_str(e.get("pid"), 80) or not e.get("pid"):
        return False
    if not _bounded_str(e.get("ts"), 128) or not e.get("ts"):
        return False
    if not _bounded_str(e.get("task"), 40):
        return False
    if not _bounded_str(e.get("model"), 120):
        return False
    if not _bounded_str(e.get("origin"), 120):
        return False
    return True


def _validate_record_fields(raw: Any, owner: str) -> Tuple[bool, str]:
    """The record-level shape shared by both tiers (everything
    except the proposal entries, which differ per tier)."""
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
    for key, limit in (("subject", 200), ("provider", 80),
                       ("model", 120), ("task", 40), ("snap_name", 120)):
        if not _bounded_str(raw.get(key), limit):
            return False, f"session.{key} must be a string (max {limit})"
    closed = raw.get("closed")
    if closed is not None:
        if not isinstance(closed, str) or not closed or len(closed) > 128:
            return False, "session.closed must be null or a timestamp"
    dropped = raw.get("dropped")
    if dropped is not None:
        if not isinstance(dropped, int) or isinstance(dropped, bool) \
                or dropped < 0:
            return False, "session.dropped must be a non-negative int"
    return True, ""


def validate_archive(raw: Any, owner: str) -> Tuple[bool, str]:
    """Strict shape check for a history-tier (compacted) record:
    the full record shape, with provenance digests in place of
    full proposal entries."""
    ok, err = _validate_record_fields(raw, owner)
    if not ok:
        return False, err
    if raw.get("closed") is None:
        return False, "history session must be closed"
    props = raw.get("proposals")
    if not isinstance(props, list):
        return False, "session.proposals must be an array"
    if len(props) > _MAX_PROPOSALS:
        return False, f"session.proposals exceeds {_MAX_PROPOSALS}"
    for e in props:
        if not _is_valid_digest_entry(e):
            return False, "session.proposals has an invalid digest entry"
    return True, ""


def compact_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce one proposal-evidence entry to its provenance
    digest. Idempotent: a digest compacts to itself."""
    return {k: entry.get(k) for k in _DIGEST_FIELDS}


def compact_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """The history-tier form of a closed record: identity fields
    verbatim, proposal entries as provenance digests."""
    out = dict(record)
    out["proposals"] = [compact_entry(e)
                        for e in record.get("proposals") or []]
    return out


# Sentinel for absent section key (legacy). Distinct from explicit
# null, which is malformed. Loaders use data.get("dock_sessions",
# _MISSING) — the kit's one sentinel.
_MISSING = MISSING


def validate_section(raw: Any, owner: str
                     ) -> Tuple[Dict[str, Dict[str, Any]],
                                Optional[Dict[str, Any]]]:
    """Validate a persisted dock_sessions section. Never raises.

    Version 2: live tier under "sessions" (full records) plus
    history tier under "history" (compact records) — both
    uncapped; the returned mapping holds every valid record,
    history records in their compact in-memory form. Version 1
    (legacy): all records at full detail under "sessions".
    """
    if raw is MISSING:
        return {}, None
    version = raw.get("version") if isinstance(raw, dict) else None
    if version == _LEGACY_SECTION_VERSION:
        error, malformed = section_shell(raw, "sessions",
                                         _LEGACY_SECTION_VERSION)
        if error is not None:
            return {}, malformed
        malformed = {}
        valid = collect_valid(
            raw["sessions"], lambda rec: validate(rec, owner),
            "session_id", malformed,
            key_not_string="session key not a string",
            mismatch="session key/ID mismatch")
        carry_preserved(raw.get("malformed"), malformed)
        return valid, (malformed if malformed else None)
    error, malformed = section_shell(raw, "sessions",
                                     DOCK_SECTION_VERSION)
    if error is not None:
        return {}, malformed
    if "history" in raw and not isinstance(raw.get("history"), dict):
        malformed = {}
        add_malformed(malformed, "_section", raw,
                      "history not an object")
        return {}, malformed
    malformed = {}
    live = collect_valid(
        raw["sessions"], lambda rec: validate(rec, owner),
        "session_id", malformed,
        key_not_string="session key not a string",
        mismatch="session key/ID mismatch")
    history = collect_valid(
        raw.get("history") or {}, lambda rec: validate_archive(rec, owner),
        "session_id", malformed,
        key_not_string="session key not a string",
        mismatch="session key/ID mismatch")
    for key in sorted(set(live) & set(history)):
        add_malformed(malformed, key, history.pop(key),
                      "session present in both live and history tiers")
    merged = dict(history)
    merged.update(live)
    carry_preserved(raw.get("malformed"), malformed)
    return merged, (malformed if malformed else None)


def serialize_section(sessions: Any, malformed: Any,
                      owner: str, extra: Any = None) -> Dict[str, Any]:
    """Serialize dock sessions as a version 2 two-tier section.

    Open records persist at full detail under "sessions"; closed
    records persist compacted under "history" (omitted when
    empty). Invalid records are preserved in "malformed", never
    silently saved as valid or discarded. Never raises.
    """
    mal: Dict[str, Any] = {}
    live: Dict[str, Dict[str, Any]] = {}
    history: Dict[str, Dict[str, Any]] = {}
    if isinstance(sessions, dict):
        for key, rec in sessions.items():
            if not isinstance(key, str):
                add_malformed(mal, "_non_string_key", rec,
                              "session key not a string")
                continue
            closed = isinstance(rec, dict) \
                and rec.get("closed") is not None
            if closed:
                ok, err = validate_archive_in_memory(rec, owner)
                if not ok:
                    add_malformed(
                        mal, key, rec,
                        f"not serialized as valid: {err}")
                    continue
                if rec.get("session_id") != key:
                    add_malformed(
                        mal, key, rec,
                        "not serialized as valid: key/ID mismatch")
                    continue
                history[key] = compact_record(rec)
            else:
                ok, err = validate(rec, owner)
                if not ok:
                    add_malformed(
                        mal, key, rec,
                        f"not serialized as valid: {err}")
                    continue
                if not isinstance(rec, dict) \
                        or rec.get("session_id") != key:
                    add_malformed(
                        mal, key, rec,
                        "not serialized as valid: key/ID mismatch")
                    continue
                live[key] = dict(rec)
    carry_preserved(malformed, mal)
    section: Dict[str, Any] = {"version": DOCK_SECTION_VERSION}
    if extra:
        section.update(extra)
    section["sessions"] = live
    if history:
        section["history"] = history
    if mal:
        section["malformed"] = mal
    return section


def validate_archive_in_memory(raw: Any, owner: str
                               ) -> Tuple[bool, str]:
    """Validate a closed record about to be compacted for save.

    In memory a closed record may hold full proposal entries
    (written this session, or loaded from a v1 file) or digests
    (loaded from a v2 history tier); both forms are valid here —
    compaction normalizes them. Anything else is malformed.
    """
    ok, err = _validate_record_fields(raw, owner)
    if not ok:
        return False, err
    if raw.get("closed") is None:
        return False, "history session must be closed"
    props = raw.get("proposals")
    if not isinstance(props, list):
        return False, "session.proposals must be an array"
    if len(props) > _MAX_PROPOSALS:
        return False, f"session.proposals exceeds {_MAX_PROPOSALS}"
    for e in props:
        if not (_is_valid_entry(e) or _is_valid_digest_entry(e)):
            return False, "session.proposals has an invalid entry"
    return True, ""
