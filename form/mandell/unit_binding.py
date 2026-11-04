"""Track D TD-1 — Plane Unit -> canonical Idea binding foundation.

Director ruling 2026-11-04 (PR #261): strategy S1 (recorded mapping)
approved. A Plane Unit gains an optional `idea_id` pointer to a
canonical Idea; SemanticGraph remains the ONLY containment
authority — this module performs NO graph writes and grants the
pointer no graph semantics. TD-1 is binding only: no containment
operations live here (TD-2, not yet authorized).

Binding protocol (per unit, idempotent, ordered for failure):

1. Pointer set + target VALIDATES (a real load_idea: the file must
   exist, parse, and carry the same id — file existence alone is
   not validity, per the Director's amendment) -> already bound,
   no-op.
2. Pointer set + target missing -> BindingRefused(target_missing);
   corrupt or id-mismatched -> BindingRefused(target_invalid).
   This is half-bound state H1: refused and reported, NEVER
   silently rebound — a missing canonical record is a persistence
   integrity event.
3. Pointer unset: before minting, the persisted program state is
   re-read; if it already carries a pointer for this unit, another
   instance bound it first -> BindingRefused(conflict) naming the
   persisted id. A stale instance never silently overwrites.
4. Otherwise a shell Idea is minted (fresh UUID; title = the unit's
   label; provenance = the real invoking subject on the shell's
   single bridge_bind change event; NO other content — no Plane
   words/detail/goals are copied) and saved FIRST. The pointer is
   written second, then the normal Program save. If that save
   fails, the in-memory pointer is rolled back and BindingFailed
   reports the orphaned shell id: the shell remains as
   census-visible canonical history (never auto-deleted), and the
   unit is NOT reported bound. Cross-file atomicity is not claimed:
   the ordering guarantees the pointer never precedes the Idea.

Provenance source is HUMAN: TD-1's authorized surface is the
sovereign user's Program operation, and `subject` names the actual
invoker in the shell's provenance.

TD-1-R1 (Director directive 2026-11-04) — conflict and corruption
guard, closing two source-review findings on the protocol above:

  F1 (corrupt state): bind reads the canonical state file once at
  entry. A file that exists but cannot be read or parsed refuses
  the bind with state_unreadable BEFORE any mint — the bind never
  proceeds toward a save that would silently overwrite corrupt
  state, and the corrupt bytes are left exactly as found.

  F2 (concurrent writers): the entry read's SHA-256 fingerprint
  is a compare-and-swap token. Because a bind's save rewrites
  the WHOLE program state, any intervening save invalidates
  this instance. Immediately before the pointer is committed,
  the file is re-read; a changed fingerprint (including
  absent->present and present->absent transitions) fails the
  bind — the minted shell is reported as a census-visible
  orphan and the winning writer's persisted state is untouched.
  Disclosed residual: between the gate re-read and the atomic
  rename inside the save itself, a racing save can still land;
  the guard detects every interleaving that completes before
  the gate, and narrows the undetectable window to that rename.

  Reconciliation: when the in-memory pointer and the canonical
  persisted pointer for a unit disagree, the persisted record
  is canonical — bind refuses with a conflict naming both,
  rather than trusting memory into an already_bound answer.
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict


class BindingRefused(Exception):
    """A binding was refused before any mutation. `kind` is the
    machine-readable reason; `detail` carries the evidence."""

    def __init__(self, kind: str, message: str, **detail: Any):
        super().__init__(message)
        self.kind = kind
        self.detail = detail


class BindingFailed(Exception):
    """The mint succeeded but the commit did not complete (Program
    save failure, or the TD-1-R1 concurrency gate refused the
    commit). The pointer was rolled back or never set;
    `orphan_idea_id` names the shell left as census-visible
    history; `detail` carries the machine-readable evidence."""

    def __init__(self, message: str, orphan_idea_id: str = None,
                 **detail: Any):
        super().__init__(message)
        self.orphan_idea_id = orphan_idea_id
        self.detail = detail


def _plane(program):
    return program.cube.session.plane


def _validate_pointer(owner: str, idea_id: str) -> str:
    """'ok' | 'missing' | 'invalid' — by validated load, never by
    file existence (Director amendment 1)."""
    from form.mandell.idea_persist import load_idea
    try:
        idea = load_idea(idea_id, owner)
    except FileNotFoundError:
        return "missing"
    except ValueError:
        return "invalid"
    return "ok" if idea.id == idea_id else "invalid"


def _read_persisted_state(owner: str):
    """One read of the canonical state file (TD-1-R1).

    Returns (status, fingerprint, data):
      status "absent"    — no state file; fingerprint None.
      status "unreadable" — the file exists but cannot be read or
        parsed; fingerprint is the hash of the bytes as found (or
        None when even the read failed); data None. Bind refuses
        this state before minting (finding F1): a bind must never
        proceed toward a save that would silently overwrite it.
      status "ok"        — parsed JSON; fingerprint = SHA-256 of
        the exact bytes read; data = the parsed record.
    The fingerprint is the compare-and-swap token for the commit
    gate (finding F2)."""
    import hashlib
    from form.persist import _path
    path = _path(owner)
    if not os.path.isfile(path):
        return "absent", None, None
    try:
        with open(path, "rb") as f:
            blob = f.read()
    except OSError:
        return "unreadable", None, None
    fingerprint = hashlib.sha256(blob).hexdigest()
    try:
        data = json.loads(blob.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        return "unreadable", fingerprint, None
    if not isinstance(data, dict):
        return "unreadable", fingerprint, None
    return "ok", fingerprint, data


def _pointer_in(data, unit_id: str):
    """The pointer a parsed state record carries for this unit."""
    units = (data.get("plane") or {}).get("units") or {}
    rec = units.get(unit_id) or {}
    ptr = rec.get("idea_id")
    return ptr if isinstance(ptr, str) and ptr else None


def bind_unit_to_idea(program, unit_id: str, *, subject: str) -> Dict[str, Any]:
    """Bind one Plane unit to a canonical Idea shell (S1, lazy).

    Returns a receipt dict on success (status 'bound' or
    'already_bound'). Raises BindingRefused / BindingFailed per the
    module contract; on any raise the unit's pointer is unchanged
    (rollback) and no graph write has occurred.
    """
    if not isinstance(subject, str) or not subject.strip():
        raise BindingRefused(
            "subject_required",
            "bind requires the real invoking subject for provenance")
    plane = _plane(program)
    unit = plane.units.get(unit_id)
    if unit is None:
        raise BindingRefused(
            "unit_not_found", f"no Plane unit {unit_id!r}",
            unit_id=unit_id)
    owner = program.owner
    existing = getattr(unit, "idea_id", None)

    # TD-1-R1: one canonical read at entry. Unreadable state
    # refuses before anything else (F1) — never proceed toward a
    # save that would silently overwrite it.
    state_status, entry_fingerprint, state_data = \
        _read_persisted_state(owner)
    if state_status == "unreadable":
        raise BindingRefused(
            "state_unreadable",
            f"persisted program state for owner {owner!r} exists "
            f"but cannot be read or parsed; refusing to bind "
            f"before any mint — the bytes are left as found",
            unit_id=unit_id)
    persisted = _pointer_in(state_data, unit_id) \
        if state_status == "ok" else None

    # TD-1-R1 baseline (F2): an instance stamped at load/save time
    # (persist_rest) with the state version it derives from must
    # still be current. If the canonical file has moved — another
    # writer saved, or the file vanished — this instance's whole
    # view is stale and any bind from it is refused until reload.
    # Unstamped instances (constructed, not loaded) carry no
    # baseline; the commit-gate CAS below still guards their save.
    stamp = getattr(program, "_td_state_fingerprint", None)
    if stamp is not None and entry_fingerprint != stamp:
        raise BindingRefused(
            "conflict",
            f"this instance's program state is stale: the "
            f"canonical state file changed since this instance "
            f"loaded/saved it (or vanished); reload before binding",
            unit_id=unit_id, persisted_idea_id=persisted,
            in_memory_idea_id=existing)

    if existing:
        # Reconciliation (R1): the persisted record is canonical.
        # If it names a DIFFERENT Idea for this unit, memory and
        # disk have split — refuse, naming both, instead of
        # trusting memory into an already_bound answer.
        if persisted and persisted != existing:
            raise BindingRefused(
                "conflict",
                f"unit {unit_id!r}: in-memory pointer {existing!r} "
                f"disagrees with the canonical persisted pointer "
                f"{persisted!r}; persisted state is canonical — "
                f"reload before binding",
                unit_id=unit_id, persisted_idea_id=persisted,
                in_memory_idea_id=existing)
        state = _validate_pointer(owner, existing)
        if state == "ok":
            return {"status": "already_bound", "unit_id": unit_id,
                    "idea_id": existing}
        kind = "target_missing" if state == "missing" else "target_invalid"
        raise BindingRefused(
            kind,
            f"unit {unit_id!r} points at Idea {existing!r} which is "
            f"{state}; refusing to rebind (H1)",
            unit_id=unit_id, idea_id=existing)

    if persisted:
        raise BindingRefused(
            "conflict",
            f"persisted state already binds unit {unit_id!r} to "
            f"Idea {persisted!r}; this instance's view is stale — "
            f"reload before binding",
            unit_id=unit_id, persisted_idea_id=persisted)

    from form.mandell.idea import Idea, Provenance, ProvenanceSource
    from form.mandell.idea_persist import save_idea

    idea = Idea(title=unit.label)
    prov = Provenance(
        source=ProvenanceSource.HUMAN,
        activity="bridge_bind",
        agent=subject,
        detail=(f"TD-1 shell minted for Plane unit {unit_id!r} "
                f"(owner {owner!r}); title only — no Plane content "
                f"copied"))
    # The shell's single provenance record: the Idea model's
    # idea-level change event (the same boundary archive/delete use).
    idea._on_information_change(
        "bridge_bind", None, None,
        f"canonical shell established for unit {unit_id}", prov)
    save_idea(idea, owner)

    # TD-1-R1 commit gate (F2): re-read the canonical state and
    # compare fingerprints with the entry read. A bind's save
    # rewrites the whole program state, so ANY intervening save
    # (or the file appearing/vanishing) invalidates this
    # instance: fail here, before the pointer is set, leaving the
    # winning writer's persisted state untouched. Residual
    # window disclosed in the module docstring.
    gate_status, gate_fingerprint, _ = _read_persisted_state(owner)
    if gate_status == "unreadable" or gate_fingerprint != entry_fingerprint:
        raise BindingFailed(
            f"concurrent state change detected at the commit gate "
            f"for unit {unit_id!r} (entry state {state_status!r}, "
            f"gate state {gate_status!r}); refusing to overwrite — "
            f"shell {idea.id} remains as census-visible history; "
            f"reload before binding",
            orphan_idea_id=idea.id, reason="concurrent_save")

    unit.idea_id = idea.id
    try:
        from form import persist_rest
        persist_rest.save(program)
    except Exception as exc:
        unit.idea_id = None
        raise BindingFailed(
            f"program save failed after minting shell {idea.id}; "
            f"pointer rolled back, shell remains as census-visible "
            f"history: {exc}",
            orphan_idea_id=idea.id) from exc
    return {"status": "bound", "unit_id": unit_id,
            "idea_id": idea.id, "subject": subject}


def binding_census(program) -> Dict[str, Any]:
    """Enumerate binding state for the program's owner.

    bound: pointer set and target validates. invalid: unit ids whose
    pointer is set but whose target is missing/corrupt (H1).
    unreferenced_idea_ids: canonical Ideas under this owner that no
    unit points at — this includes pre-existing unbound Ideas and
    any orphan shells; distinguishing those requires a pre-bind
    baseline, so the census reports the set, not a verdict.
    """
    from form.mandell.idea_persist import list_idea_ids
    plane = _plane(program)
    owner = program.owner
    bound = 0
    invalid = []
    referenced = set()
    pointed = 0
    for uid, u in plane.units.items():
        ptr = getattr(u, "idea_id", None)
        if not ptr:
            continue
        pointed += 1
        referenced.add(ptr)
        if _validate_pointer(owner, ptr) == "ok":
            bound += 1
        else:
            invalid.append(uid)
    all_ideas = set(list_idea_ids(owner))
    return {
        "units": len(plane.units),
        "bound": bound,
        "unbound": len(plane.units) - pointed,
        "invalid": sorted(invalid),
        "referenced_idea_ids": sorted(referenced),
        "unreferenced_idea_ids": sorted(all_ideas - referenced),
    }
