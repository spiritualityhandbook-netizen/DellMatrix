#!/usr/bin/env python3
"""DCC-XIX: Operator-governed conflict disposition + routing policy (Disposition V1).

Conflict V1 (DCC-XIII) DETECTS bounded polarity conflicts and quarantines
every participating unit. DCC-XIX adds the missing control layer: an
explicit human/operator decision about what DellMatrix should DO WITH a
detected conflict FOR ROUTING PURPOSES.

CONFLICT DETECTION != CONFLICT DISPOSITION != TRUTH.

Conflict V1 answers:      "Does this bounded detector identify a conflict?"
Disposition V1 answers:   "What explicit routing policy did the operator
                           assign to that conflict?"
Neither answers:          "Which proposition is objectively true?"

Stable conflict identity
------------------------
A durable disposition requires stable identity. The identity is derived
only from the conflict protocol version and the canonical sorted
participant IDs:

    conflict_id = "cv1:" + sha256(f"{version}|{id_a}|{id_b}")[:32]

with id_a < id_b. No discovery order, no timestamps, no relevance rank,
no mutable scores. The same conflict reconstructed after restart produces
the same identity. A superseded participant changes the identity: the
old disposition never silently transfers to the new conflict.

Disposition V1 states
---------------------
    unresolved  -- default; no record stored. DCC-XIII behavior preserved:
                   every active conflict participant is quarantined.
    prefer      -- the operator prefers one participant FOR ROUTING. The
                   preferred unit may route iff it independently passes
                   revision, dependency, eligibility, and relevance gates.
                   The other participant stays conflict-excluded. No
                   autonomous promotion of the non-preferred side.
    coexist     -- conflict quarantine is waived for this identified
                   conflict only. The statements are NOT declared true,
                   agreeing, or resolved; the conflict remains detected
                   and visible in receipts/traces.

Clearing a disposition deletes the record and returns the conflict to the
default unresolved state.

Routing order (conceptual; preserved in receipts)
------------------------------------------------
lifecycle/revision -> dependency -> eligibility -> Relevance V2 -> top-5
-> Conflict V1 detection -> disposition policy -> routable -> scope
-> consumer. Disposition never alters relevance scores, never widens the
candidate set, and never bypasses revision/dependency gates.

Composition rule: a unit is routable only if EVERY detected conflict
involving it permits it. One unresolved applicable conflict still
quarantines the unit even if another conflict prefers it.

Failure posture: a malformed or inapplicable disposition record never
makes knowledge more routable (fail closed at the governance layer).
Records are persisted on the owner's nursery via Persistence V2 atomic
writes and ride Checkpoint Generation V1 members, so a fresh process
observes either the OLD complete policy or the NEW complete policy --
never a half-policy.
"""
from __future__ import annotations

import hashlib
import re
from typing import Any, Dict, List, Optional, Set, Tuple

from form.mandell.conflict_router import CONFLICT_VERSION, detect_conflicts

CONFLICT_DISPOSITION_VERSION = 1

# Dispositions that may be stored. "unresolved" is the default and is never
# stored as a record: absence of a record means unresolved.
DISPOSITION_PREFER = "prefer"
DISPOSITION_COEXIST = "coexist"
STORED_DISPOSITIONS = (DISPOSITION_PREFER, DISPOSITION_COEXIST)

_CONFLICT_ID_RE = re.compile(r"^cv(\d+):([0-9a-f]{32})$")


def conflict_id_for(id_a: str, id_b: str, conflict_version: int = CONFLICT_VERSION) -> str:
    """Deterministic stable identity for a Conflict V1 pair.

    Derived only from the protocol version and the canonical (sorted)
    participant IDs. Order-independent: conflict_id_for(A, B) ==
    conflict_id_for(B, A).
    """
    a, b = sorted((str(id_a), str(id_b)))
    digest = hashlib.sha256(f"{conflict_version}|{a}|{b}".encode("utf-8")).hexdigest()[:32]
    return f"cv{conflict_version}:{digest}"


def conflict_id_parts(conflict_id: str) -> Optional[Tuple[int, str]]:
    """Parse a conflict ID; None when malformed."""
    m = _CONFLICT_ID_RE.match(str(conflict_id or ""))
    if not m:
        return None
    return int(m.group(1)), m.group(2)


def _participant_ids(entry: Dict[str, Any]) -> List[str]:
    return sorted((str(entry["id_a"]), str(entry["id_b"])))


def validate_record(record: Any) -> Tuple[bool, List[str]]:
    """Structural + semantic shape check of a disposition record.

    Returns (ok, errors). This checks the record's own coherence, not
    whether it applies to a currently detected conflict (that is decided
    at routing/trace time so stale records stay inspectable).
    """
    errors: List[str] = []
    if not isinstance(record, dict):
        return False, ["record is not an object"]
    if record.get("conflict_disposition_version") != CONFLICT_DISPOSITION_VERSION:
        errors.append(
            f"conflict_disposition_version must be {CONFLICT_DISPOSITION_VERSION}"
        )
    cid = record.get("conflict_id")
    if conflict_id_parts(cid) is None:
        errors.append("conflict_id is malformed")
    parts = record.get("participant_ids")
    if not isinstance(parts, list) or len(parts) != 2 or any(
        not isinstance(p, str) or not p for p in parts
    ):
        errors.append("participant_ids must be a list of exactly two non-empty unit IDs")
    elif sorted(parts) != list(parts):
        errors.append("participant_ids must be canonically sorted")
    elif parts[0] == parts[1]:
        errors.append("participant_ids must be two distinct units")
    disp = record.get("disposition")
    if disp not in STORED_DISPOSITIONS:
        errors.append(f"disposition must be one of {list(STORED_DISPOSITIONS)}")
    pref = record.get("preferred_ids")
    if not isinstance(pref, list) or any(not isinstance(p, str) or not p for p in pref):
        errors.append("preferred_ids must be a list of unit IDs")
    elif len(set(pref)) != len(pref):
        errors.append("preferred_ids must not contain duplicates")
    elif isinstance(parts, list) and len(parts) == 2 and sorted(parts) == list(parts):
        if disp == DISPOSITION_PREFER:
            if len(pref) != 1:
                errors.append("prefer disposition requires exactly one preferred ID")
            elif pref[0] not in parts:
                errors.append("preferred ID is not a conflict participant")
        elif disp == DISPOSITION_COEXIST and pref:
            errors.append("coexist disposition must not name preferred IDs")
    reason = record.get("operator_reason", "")
    if not isinstance(reason, str):
        errors.append("operator_reason must be a string")
    seq = record.get("update_seq")
    if not isinstance(seq, int) or isinstance(seq, bool) or seq < 1:
        errors.append("update_seq must be a positive integer")
    return (not errors), errors


def record_applies_to(record: Dict[str, Any], entry: Dict[str, Any]) -> bool:
    """True iff the record governs this exact detected conflict.

    Identity is exact: the record's conflict_id must equal the detected
    pair's stable identity AND its participant_ids must match the pair.
    A superseded participant changes the identity, so governance never
    silently transfers to changed knowledge.
    """
    ok, _ = validate_record(record)
    if not ok:
        return False
    pair = _participant_ids(entry)
    if list(record.get("participant_ids") or []) != pair:
        return False
    return record.get("conflict_id") == conflict_id_for(
        pair[0], pair[1], CONFLICT_VERSION
    )


def _eligible_units(program: Any) -> List[Tuple[str, Any]]:
    """Units eligible for conflict analysis without any context.

    Mirrors the selector's eligibility prefix (DCC-XII/XV/XVI): confirmed
    AND on-plane AND revision-active AND dependency-valid. Relevance and
    top-5 are context-bound and intentionally excluded: command-time
    validation asks whether the conflict is real right now, while routing
    application is still confined to the detected (selected) set.
    """
    from form.mandell.dependency_validity import is_dependency_valid
    from form.mandell.supersession import is_revision_active

    out = []
    proposals = getattr(getattr(program, "nursery", None), "proposals", None) or {}
    plane_units = (
        getattr(getattr(getattr(program, "cube", None), "session", None), "plane", None)
        and getattr(program.cube.session.plane, "units", None)
    ) or {}
    for pid, prop in proposals.items():
        if getattr(prop, "status", "") != "confirmed":
            continue
        if pid not in plane_units:
            continue
        if not is_revision_active(program, pid):
            continue
        if not is_dependency_valid(program, pid):
            continue
        out.append((pid, prop))
    return out


def detectable_conflicts(program: Any) -> List[Dict[str, Any]]:
    """Conflicts currently detectable among eligible units (deterministic)."""
    from form.mandell.knowledge_selector import unit_text

    items = [{"id": pid, "text": unit_text(program, pid)} for pid, _ in _eligible_units(program)]
    entries = detect_conflicts(items)
    for e in entries:
        e["conflict_id"] = conflict_id_for(e["id_a"], e["id_b"], CONFLICT_VERSION)
    return entries


def _dispositions(program: Any) -> Dict[str, Dict[str, Any]]:
    store = getattr(getattr(program, "nursery", None), "conflict_dispositions", None)
    return store if isinstance(store, dict) else {}


def _participant_qualifies(program: Any, uid: str) -> Tuple[bool, str]:
    """Defense-in-depth recheck at the disposition gate.

    Mirrors accepted-knowledge qualification: confirmed, on-plane,
    revision-active, dependency-valid. The selector already guarantees
    this for selected units; the disposition layer re-verifies so a
    preferred participant that lost qualification can never route on
    the strength of the disposition alone, and the non-preferred side
    is never auto-promoted as a "winner".
    """
    from form.mandell.dependency_validity import is_dependency_valid
    from form.mandell.supersession import is_revision_active

    proposals = getattr(getattr(program, "nursery", None), "proposals", None) or {}
    prop = proposals.get(uid)
    if prop is None or getattr(prop, "status", "") != "confirmed":
        return False, "not confirmed"
    plane_units = (
        getattr(getattr(getattr(program, "cube", None), "session", None), "plane", None)
        and getattr(program.cube.session.plane, "units", None)
    ) or {}
    if uid not in plane_units:
        return False, "not on plane"
    if not is_revision_active(program, uid):
        return False, "revision not active"
    if not is_dependency_valid(program, uid):
        return False, "dependency invalid"
    return True, "qualifies"


def _new_record(
    conflict_id: str,
    participant_ids: List[str],
    disposition: str,
    preferred_ids: List[str],
    operator_reason: str,
    update_seq: int,
) -> Dict[str, Any]:
    return {
        "conflict_disposition_version": CONFLICT_DISPOSITION_VERSION,
        "conflict_id": conflict_id,
        "participant_ids": list(participant_ids),
        "disposition": disposition,
        "preferred_ids": list(preferred_ids),
        "operator_reason": operator_reason,
        "update_seq": update_seq,
    }


def set_disposition(
    program: Any,
    conflict_id: str,
    disposition: str,
    preferred_ids: Optional[List[str]] = None,
    operator_reason: str = "",
) -> Dict[str, Any]:
    """Assign an explicit operator routing disposition to a detected conflict.

    The conflict must be currently detectable among eligible units; the
    preferred ID (for prefer) must be a participant. The record is
    persisted via the nursery's Persistence V2 atomic write: on save
    failure the in-memory record is rolled back and the failure is
    reported honestly -- the fresh process sees the old complete policy.

    Repeated identical commands are a deterministic no-op (same-state
    acknowledgement, no duplicate effect, no nursery rewrite).
    """
    preferred_ids = list(preferred_ids or [])
    operator_reason = str(operator_reason or "")
    base: Dict[str, Any] = {
        "ok": False,
        "action": "resolve_conflict",
        "conflict_disposition_version": CONFLICT_DISPOSITION_VERSION,
        "conflict_id": conflict_id,
        "disposition": disposition,
        "preferred_ids": preferred_ids,
    }
    if conflict_id_parts(conflict_id) is None:
        return {**base, "error": "malformed conflict_id"}
    if disposition not in STORED_DISPOSITIONS:
        return {**base, "error": f"disposition must be one of {list(STORED_DISPOSITIONS)}"}
    if disposition == DISPOSITION_PREFER and len(preferred_ids) != 1:
        return {**base, "error": "prefer requires exactly one preferred unit ID"}
    if disposition == DISPOSITION_COEXIST and preferred_ids:
        return {**base, "error": "coexist must not name preferred unit IDs"}
    if len(set(preferred_ids)) != len(preferred_ids):
        return {**base, "error": "preferred_ids must not contain duplicates"}

    detected = {e["conflict_id"]: e for e in detectable_conflicts(program)}
    entry = detected.get(conflict_id)
    if entry is None:
        return {**base, "error": "unknown conflict: not currently detectable among eligible units"}
    pair = _participant_ids(entry)
    if any(p not in pair for p in preferred_ids):
        return {**base, "error": "preferred ID is not a conflict participant"}

    store = _dispositions(program)
    previous = store.get(conflict_id)
    prev_seq = int(previous.get("update_seq", 0)) if isinstance(previous, dict) else 0
    candidate = _new_record(
        conflict_id, pair, disposition, preferred_ids, operator_reason, prev_seq + 1
    )
    ok_shape, shape_errors = validate_record(candidate)
    if not ok_shape:  # defensive; construction above is already constrained
        return {**base, "error": f"record failed validation: {shape_errors}"}

    if isinstance(previous, dict):
        prev_norm = {k: previous.get(k) for k in (
            "disposition", "preferred_ids", "operator_reason", "participant_ids")}
        cand_norm = {k: candidate.get(k) for k in prev_norm}
        if prev_norm == cand_norm:
            return {
                **base,
                "ok": True,
                "noop": True,
                "participant_ids": pair,
                "update_seq": previous.get("update_seq"),
                "note": "identical disposition already in effect; no change",
            }

    before = dict(store)
    store[conflict_id] = candidate
    try:
        program.nursery.save()
    except Exception as exc:
        # Failure atomicity: restore the in-memory store so memory and
        # disk agree on the old complete policy.
        try:
            program.nursery.conflict_dispositions.clear()
            program.nursery.conflict_dispositions.update(before)
        except Exception:
            pass
        return {
            **base,
            "ok": False,
            "participant_ids": pair,
            "error": f"persistence failed; prior disposition preserved: {type(exc).__name__}: {exc}",
        }
    return {
        **base,
        "ok": True,
        "noop": False,
        "participant_ids": pair,
        "update_seq": candidate["update_seq"],
        "previous_disposition": (previous or {}).get("disposition"),
        "note": "explicit operator routing disposition; not a truth claim",
    }


def clear_disposition(program: Any, conflict_id: str) -> Dict[str, Any]:
    """Remove an explicit disposition; the conflict returns to unresolved.

    Clearing twice is deterministic: the second clear is a no-op
    acknowledgement that the conflict is already unresolved.
    """
    base: Dict[str, Any] = {
        "ok": False,
        "action": "clear_conflict_resolution",
        "conflict_disposition_version": CONFLICT_DISPOSITION_VERSION,
        "conflict_id": conflict_id,
    }
    if conflict_id_parts(conflict_id) is None:
        return {**base, "error": "malformed conflict_id"}
    store = _dispositions(program)
    previous = store.get(conflict_id)
    if previous is None:
        return {**base, "ok": True, "noop": True,
                "note": "no explicit disposition; already unresolved"}
    before = dict(store)
    del store[conflict_id]
    try:
        program.nursery.save()
    except Exception as exc:
        try:
            program.nursery.conflict_dispositions.clear()
            program.nursery.conflict_dispositions.update(before)
        except Exception:
            pass
        return {**base, "ok": False,
                "error": f"persistence failed; prior disposition preserved: {type(exc).__name__}: {exc}"}
    return {
        **base,
        "ok": True,
        "noop": False,
        "cleared_disposition": (previous or {}).get("disposition"),
        "note": "returned to default unresolved quarantine",
    }


def apply_dispositions(
    selected_ids: List[str],
    conflicts: List[Dict[str, Any]],
    program: Any,
) -> Tuple[List[str], List[str], Dict[str, Any]]:
    """Apply Conflict Disposition V1 to the conflict-routing gate.

    selected_ids: selector rank order (unchanged by disposition).
    conflicts:    Conflict V1 entries over the selected set.

    A unit is routable only if EVERY detected conflict involving it
    permits it:
      unresolved -> no participant permitted (DCC-XIII quarantine)
      prefer X   -> X permitted iff X currently qualifies; the other
                    participant is never auto-promoted
      coexist    -> quarantine waived for this conflict only

    Malformed or inapplicable records fail closed: the conflict is
    treated as unresolved. Records for conflicts not detected here have
    no routing effect (stale, still inspectable).

    Returns (routable_ids, quarantined_ids, evidence).
    """
    store = _dispositions(program)
    selected_set = set(selected_ids)
    ordered = sorted(conflicts, key=lambda e: conflict_id_for(
        str(e.get("id_a")), str(e.get("id_b")), CONFLICT_VERSION))

    permitted: Dict[str, bool] = {sid: True for sid in selected_ids}
    per_conflict: List[Dict[str, Any]] = []
    invalid_ids: List[str] = []
    policy_exclusions: List[Dict[str, Any]] = []

    for entry in ordered:
        cid = conflict_id_for(str(entry.get("id_a")), str(entry.get("id_b")),
                              CONFLICT_VERSION)
        pair = _participant_ids(entry)
        record = store.get(cid)
        disposition = "unresolved"
        preferred: List[str] = []
        applicable = False
        note = "no explicit disposition; default unresolved quarantine"
        if record is not None and record_applies_to(record, entry):
            disposition = str(record["disposition"])
            preferred = list(record["preferred_ids"])
            applicable = True
            note = f"operator disposition: {disposition}"
        elif record is not None:
            invalid_ids.append(cid)
            note = "disposition record invalid or inapplicable; fail closed to unresolved"

        permitted_here: Set[str] = set()
        excluded_here: List[Dict[str, Any]] = []
        if disposition == DISPOSITION_COEXIST:
            permitted_here = set(pair)
            note = "operator disposition: coexist; quarantine waived for this conflict only"
        elif disposition == DISPOSITION_PREFER and len(preferred) == 1:
            fav = preferred[0]
            qualifies, why = _participant_qualifies(program, fav)
            if qualifies:
                permitted_here = {fav}
                note = f"operator disposition: prefer {fav}; {fav} independently qualified"
            else:
                # The preferred participant lost qualification: it cannot
                # route, and the other side is NOT auto-promoted.
                note = (f"operator disposition: prefer {fav}; {fav} currently "
                        f"ineligible ({why}); no autonomous fallback winner")
            for uid in pair:
                if uid not in permitted_here and uid in selected_set:
                    excluded_here.append({
                        "unit_id": uid,
                        "conflict_id": cid,
                        "reason": ("preferred participant ineligible"
                                   if uid == fav else "not preferred; no auto-promotion"),
                        "detail": note,
                    })
        else:
            for uid in pair:
                if uid in selected_set:
                    excluded_here.append({
                        "unit_id": uid,
                        "conflict_id": cid,
                        "reason": "unresolved conflict quarantine",
                        "detail": note,
                    })

        for uid in pair:
            if uid in selected_set and uid not in permitted_here:
                if permitted.get(uid, True):
                    policy_exclusions.append({
                        "unit_id": uid,
                        "conflict_id": cid,
                        "disposition": disposition,
                        "reason": next(
                            (x["reason"] for x in excluded_here if x["unit_id"] == uid),
                            "conflict policy",
                        ),
                    })
                permitted[uid] = False

        per_conflict.append({
            "conflict_id": cid,
            "participant_ids": pair,
            "detected": True,
            "conflict_version": CONFLICT_VERSION,
            "disposition": disposition,
            "preferred_ids": preferred if applicable else [],
            "disposition_applicable": applicable,
            "permitted_ids": sorted(permitted_here),
            "note": note,
        })

    routable_ids = [sid for sid in selected_ids if permitted.get(sid, True)]
    quarantined_ids = sorted(sid for sid in selected_ids if not permitted.get(sid, True))

    detected_ids = {c["conflict_id"] for c in per_conflict}
    stale_ids = sorted(cid for cid in store if cid not in detected_ids)

    evidence = {
        "conflict_disposition_version": CONFLICT_DISPOSITION_VERSION,
        "conflict_dispositions": per_conflict,
        "conflict_policy_exclusions": sorted(
            policy_exclusions, key=lambda x: (x["unit_id"], x["conflict_id"])),
        "invalid_disposition_ids": sorted(invalid_ids),
        "stale_disposition_ids": stale_ids,
    }
    return routable_ids, quarantined_ids, evidence


def trace_conflict(program: Any, conflict_id: str) -> Dict[str, Any]:
    """Inspect one conflict: current detection evidence, disposition,
    participant revision/dependency state, and current applicability.
    Never claims truth.
    """
    from form.mandell.dependency_validity import inspect_dependency
    from form.mandell.supersession import inspect_revision

    base: Dict[str, Any] = {
        "action": "trace_conflict",
        "conflict_disposition_version": CONFLICT_DISPOSITION_VERSION,
        "conflict_id": conflict_id,
        "ok": False,
    }
    if conflict_id_parts(conflict_id) is None:
        return {**base, "error": "malformed conflict_id"}
    record = _dispositions(program).get(conflict_id)
    detected = {e["conflict_id"]: e for e in detectable_conflicts(program)}
    entry = detected.get(conflict_id)
    rec_ok, rec_errors = validate_record(record) if record is not None else (True, [])

    participant_ids: List[str] = []
    if entry is not None:
        participant_ids = _participant_ids(entry)
    elif isinstance(record, dict) and isinstance(record.get("participant_ids"), list):
        participant_ids = [str(p) for p in record["participant_ids"]]

    participants = []
    for uid in participant_ids:
        qualifies, why = _participant_qualifies(program, uid)
        rev = inspect_revision(program, uid)
        dep = inspect_dependency(program, uid)
        participants.append({
            "unit_id": uid,
            "currently_qualifies": qualifies,
            "qualification_note": why,
            "lifecycle_state": rev.get("lifecycle_state"),
            "revision_number": rev.get("revision_number"),
            "revision_root_id": rev.get("revision_root_id"),
            "dependency_status": dep.get("dependency_status"),
            "dependency_reason": dep.get("dependency_reason"),
        })

    return {
        **base,
        "ok": True,
        "currently_detected": entry is not None,
        "detection_evidence": (
            {k: entry[k] for k in (
                "id_a", "id_b", "negative_id", "positive_id",
                "negation_evidence", "shared_frame", "frame_jaccard",
                "reason", "conflict_version") if k in entry}
            if entry is not None else None
        ),
        "participant_ids": participant_ids,
        "participants": participants,
        "disposition_record": record,
        "disposition_record_valid": rec_ok,
        "disposition_record_errors": rec_errors,
        "disposition": (record or {}).get("disposition", "unresolved") if record else "unresolved",
        "applicability": (
            "detected now; disposition governs routing" if entry is not None
            else ("stale: not currently detectable; no routing effect" if record
                  else "no conflict and no disposition on record")
        ),
    }
