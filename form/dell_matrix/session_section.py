"""Shared strict session-section kit (P3 / TD-2).

The Program session sections (connection, workshop, studio,
onboarding, forge sessions + BIMO configurations) implement one
strict persistence contract:

- an absent section key (the MISSING sentinel) is legacy, not
  malformed;
- explicit null / non-object / wrong version fail closed and are
  preserved as malformed evidence under "_section";
- per-record failures are preserved by key, never discarded;
- previously-preserved malformed evidence is carried through with
  same-key append, never overwritten;
- retention keeps the most recent records by a sort field.

Before P3 each session module carried its own copy of this
machinery (_add_malformed x5, _carry_preserved x2 plus three inline
copies, the section shell x5, the per-record loop x6) and the
copies had begun to drift (only two of five modules had
_carry_preserved at all). This module is the single implementation.
The session modules keep only their record schema (the session
dataclass and its validate()), their section key, and their
version/bound constants, and delegate the section mechanics here.
"""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, Optional, Tuple

# Sentinel for an absent section key (legacy). Distinct from explicit
# null, which is malformed. Loaders use data.get(<section>, MISSING).
# Every session module's _MISSING is this same object.
MISSING = object()

RecordValidator = Callable[[Any], Tuple[bool, str]]


def add_malformed(malformed: Dict[str, Any], key: str, raw: Any,
                  error: str) -> None:
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


def carry_preserved(preserved: Any, malformed: Dict[str, Any]) -> None:
    """Carry previously-preserved malformed evidence through, by key.

    ``preserved`` is the raw section's "malformed" value (on load) or
    the malformed mapping handed to a serializer. Non-dict input is
    a no-op.
    """
    if isinstance(preserved, dict):
        for k, v in preserved.items():
            if not isinstance(k, str):
                continue
            if isinstance(v, list):
                for entry in v:
                    if isinstance(entry, dict):
                        add_malformed(malformed, k, entry.get("raw"),
                                      entry.get("error", "preserved"))
                    else:
                        add_malformed(malformed, k, entry, "preserved")
            elif isinstance(v, dict) and "raw" in v:
                add_malformed(malformed, k, v.get("raw"),
                              v.get("error", "preserved"))
            else:
                add_malformed(malformed, k, v, "preserved")


def is_valid_step(rec: Any) -> bool:
    """Strict step/command record check. No coercion."""
    if not isinstance(rec, dict):
        return False
    for k in ("kind", "time", "result"):
        v = rec.get(k)
        if not isinstance(v, str) or len(v) > 256:
            return False
    if len(rec.get("kind", "")) == 0 or len(rec.get("kind", "")) > 32:
        return False
    return True


def section_precheck(raw: Any, version: int):
    """Shell checks before the records key: null / shape / version.

    Returns (error, malformed) — error None means the shell so far is
    readable and validation can proceed.
    """
    if raw is None:
        malformed: Dict[str, Any] = {}
        add_malformed(malformed, "_section", None,
                      "explicit null is malformed, not legacy absence")
        return "null", malformed
    if not isinstance(raw, dict):
        malformed = {}
        add_malformed(malformed, "_section", raw, "section not an object")
        return "shape", malformed
    v = raw.get("version")
    if isinstance(v, bool) or not isinstance(v, int):
        malformed = {}
        add_malformed(malformed, "_section", raw,
                      "section version must be int 1")
        return "version", malformed
    if v != version:
        malformed = {}
        add_malformed(malformed, "_section", raw,
                      f"unsupported section version {v}")
        return "version", malformed
    return None, None


def section_kind_check(raw: Any, kind: str) -> Optional[Dict[str, Any]]:
    """Malformed dict if raw[kind] is not an object, else None."""
    if not isinstance(raw.get(kind), dict):
        malformed: Dict[str, Any] = {}
        add_malformed(malformed, "_section", raw, f"{kind} not an object")
        return malformed
    return None


def section_shell(raw: Any, kind: str, version: int):
    """Full shared section pre-checks (precheck + records-key shape).

    Returns (error, malformed) — error None means the section shell
    is readable and per-record validation can proceed against
    raw[kind].
    """
    error, malformed = section_precheck(raw, version)
    if error is not None:
        return error, malformed
    bad = section_kind_check(raw, kind)
    if bad is not None:
        return "shape", bad
    return None, None


def collect_valid(records: Dict[Any, Any], validate_rec: RecordValidator,
                  id_field: str, malformed: Dict[str, Any], *,
                  key_not_string: str, mismatch: str,
                  serialize: bool = False) -> Dict[str, Dict[str, Any]]:
    """The shared per-record validation loop.

    Valid records are copied into the returned dict under their key;
    failures are preserved in ``malformed`` under the record's key
    (or "_non_string_key"). In serialize mode, validation failures
    are reported as "not serialized as valid: <err>"; the mismatch
    message is passed verbatim by the caller for each mode.
    """
    valid: Dict[str, Dict[str, Any]] = {}
    for key, rec in records.items():
        if not isinstance(key, str):
            add_malformed(malformed, "_non_string_key", rec,
                          key_not_string)
            continue
        ok, err = validate_rec(rec)
        if not ok:
            add_malformed(malformed, key, rec,
                          f"not serialized as valid: {err}"
                          if serialize else err)
            continue
        if not isinstance(rec, dict) or rec.get(id_field) != key:
            add_malformed(malformed, key, rec, mismatch)
            continue
        valid[key] = dict(rec)
    return valid


def retention_order(valid: Dict[str, Dict[str, Any]], sort_field: str,
                    max_keep: int) -> Dict[str, Dict[str, Any]]:
    """Keep the most recent ``max_keep`` records by ``sort_field``."""
    ordered = sorted(valid.items(),
                     key=lambda kv: str(kv[1].get(sort_field, "")),
                     reverse=True)[:max_keep]
    return dict(ordered)


def validate_records_section(raw: Any, *, version: int, kind: str,
                             validate_rec: RecordValidator,
                             id_field: str, max_keep: int,
                             sort_field: str, key_not_string: str,
                             mismatch: str
                             ) -> Tuple[Dict[str, Dict[str, Any]],
                                        Optional[Dict[str, Any]]]:
    """Validate one persisted records section. Never raises.

    Absent (MISSING) is legacy: ({}, None). Shell failures and
    per-record failures are preserved as malformed evidence.
    """
    if raw is MISSING:
        return {}, None
    error, malformed = section_shell(raw, kind, version)
    if error is not None:
        return {}, malformed
    malformed = {}
    valid = collect_valid(raw[kind], validate_rec, id_field, malformed,
                          key_not_string=key_not_string,
                          mismatch=mismatch)
    carry_preserved(raw.get("malformed"), malformed)
    return (retention_order(valid, sort_field, max_keep),
            (malformed if malformed else None))


def serialize_records_section(records: Any, malformed_in: Any, *,
                              version: int, kind: str,
                              validate_rec: RecordValidator,
                              id_field: str, max_keep: int,
                              sort_field: str, key_not_string: str,
                              mismatch: str,
                              extra: Optional[Dict[str, Any]] = None
                              ) -> Dict[str, Any]:
    """Serialize one records section with the strict schema.

    Valid records go under ``kind``; invalid records are preserved
    in "malformed", never silently saved as valid or discarded.
    ``extra`` fields (e.g. onboarding's "begun") are written after
    "version" and before the records key. Never raises.
    """
    mal: Dict[str, Any] = {}
    valid: Dict[str, Dict[str, Any]] = {}
    if isinstance(records, dict):
        valid = collect_valid(records, validate_rec, id_field, mal,
                              key_not_string=key_not_string,
                              mismatch=mismatch, serialize=True)
    carry_preserved(malformed_in, mal)
    section: Dict[str, Any] = {"version": version}
    if extra:
        section.update(extra)
    section[kind] = retention_order(valid, sort_field, max_keep)
    if mal:
        section["malformed"] = mal
    return section


def append_step(steps: list, kind: str, result: str, max_keep: int) -> list:
    """record() core: append one bounded step record and trim to the
    retained window. Returns the list; callers rebind, as before."""
    steps.append({
        "kind": str(kind)[:32],
        "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "result": str(result)[:240],
    })
    if len(steps) > max_keep:
        steps = steps[-max_keep:]
    return steps


def closed_record(record: Dict[str, Any], list_key: str, max_keep: int,
                  *, kind: str = "leave",
                  result: str = "leave recorded") -> Dict[str, Any]:
    """closed_copy() core over a to_dict() record: stamp ``closed``,
    append the closing step, trim to the retained window. Builds the
    closed record without mutating the session."""
    record["closed"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    items = list(record.get(list_key, []))
    items.append({
        "kind": kind,
        "time": record["closed"],
        "result": result,
    })
    record[list_key] = items[-max_keep:]
    return record
