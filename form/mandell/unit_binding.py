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
    """The mint succeeded but the Program save failed. The pointer
    was rolled back; `orphan_idea_id` names the shell left as
    census-visible history."""

    def __init__(self, message: str, orphan_idea_id: str = None):
        super().__init__(message)
        self.orphan_idea_id = orphan_idea_id


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


def _persisted_pointer(owner: str, unit_id: str):
    """The pointer the canonical state file currently carries for
    this unit, or None. An unreadable state file yields None here;
    the Program's own fail-closed load law governs that case, and
    the guarded save that follows a bind would refuse separately."""
    from form.persist import _path
    path = _path(owner)
    if not os.path.isfile(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)
    except (OSError, ValueError):
        return None
    units = (raw.get("plane") or {}).get("units") or {}
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
    if existing:
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

    persisted = _persisted_pointer(owner, unit_id)
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
