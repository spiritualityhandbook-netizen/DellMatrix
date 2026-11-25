"""Track D TD-2 — Plane Unit containment operations.

Director directive 2026-11-04 (Mode D review of Water + TD-1-R2):
TD-2 is containment operations — nest, promote, and reparent at
Program level through canonical Unit->Idea bindings, REPL first.
SemanticGraph remains the SOLE containment authority: this module
stores no containment state anywhere (no Plane field, no cache, no
persisted view); every operation loads the graph fresh and every
read resolves through it. Unit.parents is lineage, never touched.

Operation protocol (ordered for failure):

1. Prevalidate everything predictable BEFORE any mint: subject,
   both units exist, no self-nest, sandbox isolation keys match
   (TD7 — endpoints whose (sandboxed, sandbox_id) keys differ
   refuse as sandbox_boundary before any binding is created).
2. Lazy-bind child, then parent, through the TD-1 protocol (shell
   saved before pointer; validated loads; no silent rebind). A
   unit bound by this call is recorded in partial_bindings.
3. Validate both endpoint Ideas by LOADING them, and require
   LifecycleState.ACTIVE for mutation (TD4): missing refuses as
   target_missing, corrupt/id-mismatched as target_invalid,
   non-ACTIVE as idea_not_active. Historical edges are never
   rewritten by a refusal.
4. Prevalidate on the freshly loaded graph: same parent is an
   idempotent no-op; a different active parent refuses nest as
   second_parent (moving requires explicit reparent); a cycle
   refuses before the append. The graph's own invariant gate is
   the backstop and its errors are translated, never leaked raw.
5. Append through the graph (nest / unnest / reparent — the
   graph's atomic appends; promote supersedes the CONTAINS edge,
   preserving it as history).

The whole span (binds + graph mutation) runs inside the canonical
owner-state lock (TD-1-R2), so bridge operations are serialized
cross-process and a competing writer cannot silently overwrite a
binding mid-operation; a lock that stays busy past the bounded
wait refuses as state_locked — there is no unlocked fallback.
Boundary: writers that bypass the bridge entirely (direct graph
users) are outside TD-2's fence; the graph file remains theirs
and this module's sole authority.

Failure honesty: any refusal/failure raised after a lazy mint
carries partial_bindings naming what was bound, because a binding
is durable TD-1 state even when the containment step did not
complete. The operation order makes the reachable residue exactly
that: bound-but-uncontained units (an orphan shell if the parent
bind also failed) — never a dangling graph edge, since bindings
always precede the graph append and the graph gate requires the
Ideas to exist. Retrying a failed operation converges: binds and
graph ops are both idempotent. Cross-file atomicity is not
claimed.

containment_view is a derived read: it mints nothing, writes
nothing, and composes the graph's structural navigation with the
Plane's reverse pointer scan (Idea -> unit) at call time.
"""
from __future__ import annotations

from typing import Any, Dict, List


class ContainmentRefused(Exception):
    """A containment operation was refused before the graph
    mutation. `kind` is the machine-readable reason; `detail`
    carries the evidence (including partial_bindings when a lazy
    bind completed before the refusal)."""

    def __init__(self, kind: str, message: str, **detail: Any):
        super().__init__(message)
        self.kind = kind
        self.detail = detail


class ContainmentFailed(Exception):
    """The operation began but did not complete (e.g. the graph
    save failed after lazy bindings were committed). `detail`
    carries partial_bindings: the durable bindings left behind,
    which are valid TD-1 state and make a retry converge."""

    def __init__(self, message: str, **detail: Any):
        super().__init__(message)
        self.detail = detail


def _plane(program):
    return program.cube.session.plane


def _unit(program, unit_id: str):
    unit = _plane(program).units.get(unit_id)
    if unit is None:
        raise ContainmentRefused(
            "unit_not_found", f"no Plane unit {unit_id!r}",
            unit_id=unit_id)
    return unit


def _isolation_key(unit):
    """Sandbox isolation key (TD7): (sandboxed, sandbox_id) for a
    sandboxed unit, (False, None) for an unsandboxed one."""
    sandboxed = bool(getattr(unit, "sandboxed", False))
    return (sandboxed, getattr(unit, "sandbox_id", None) if sandboxed else None)


def _malformed_sandbox(unit):
    """A unit is malformed when it claims sandbox isolation but
    carries no valid sandbox id (missing, empty, or not a string).
    Two such units key identically as (True, None), so key equality
    alone can never refuse them — F1 (Director review 2026-11-04):
    malformed endpoints are refused outright, before any mint,
    regardless of the other endpoint."""
    if not bool(getattr(unit, "sandboxed", False)):
        return False
    sid = getattr(unit, "sandbox_id", None)
    return not (isinstance(sid, str) and sid != "")


def _check_sandbox(child, parent, partial):
    for unit in (child, parent):
        if _malformed_sandbox(unit):
            raise ContainmentRefused(
                "sandbox_boundary",
                f"unit {unit.id!r} claims sandbox isolation but has "
                f"no valid sandbox_id "
                f"({getattr(unit, 'sandbox_id', None)!r}); refusing "
                f"malformed sandboxed endpoint before any binding",
                unit_id=unit.id,
                child_unit_id=child.id, parent_unit_id=parent.id,
                partial_bindings=list(partial))
    if _isolation_key(child) != _isolation_key(parent):
        raise ContainmentRefused(
            "sandbox_boundary",
            f"containment across sandbox isolation boundaries is "
            f"refused: {child.id!r} is in "
            f"{_isolation_key(child)!r}, {parent.id!r} is in "
            f"{_isolation_key(parent)!r}",
            child_unit_id=child.id, parent_unit_id=parent.id,
            partial_bindings=list(partial))


def _validate_active(owner: str, idea_id: str, unit_id: str, partial):
    """Validated load + ACTIVE lifecycle gate (TD4)."""
    from form.mandell.idea import LifecycleState
    from form.mandell.idea_persist import load_idea
    try:
        idea = load_idea(idea_id, owner)
    except FileNotFoundError:
        raise ContainmentRefused(
            "target_missing",
            f"unit {unit_id!r} points at Idea {idea_id!r} which is "
            f"missing; refusing — no silent rebind",
            unit_id=unit_id, idea_id=idea_id,
            partial_bindings=list(partial))
    except ValueError:
        raise ContainmentRefused(
            "target_invalid",
            f"unit {unit_id!r} points at Idea {idea_id!r} which "
            f"does not validate; refusing — no silent rebind",
            unit_id=unit_id, idea_id=idea_id,
            partial_bindings=list(partial))
    if idea.id != idea_id:
        raise ContainmentRefused(
            "target_invalid",
            f"unit {unit_id!r} points at Idea {idea_id!r} but the "
            f"stored record carries id {idea.id!r}",
            unit_id=unit_id, idea_id=idea_id,
            partial_bindings=list(partial))
    if idea.idea_state != LifecycleState.ACTIVE:
        raise ContainmentRefused(
            "idea_not_active",
            f"Idea {idea_id!r} for unit {unit_id!r} is "
            f"{idea.idea_state.value}, not active; containment "
            f"mutations refuse non-ACTIVE Ideas (historical edges "
            f"are preserved)",
            unit_id=unit_id, idea_id=idea_id,
            idea_state=idea.idea_state.value,
            partial_bindings=list(partial))
    return idea


def _ensure_binding(program, unit, subject: str, partial: List[Dict[str, str]]):
    """Lazy-bind one unit via TD-1, translating its errors and
    recording a fresh binding in `partial`."""
    from form.mandell.unit_binding import (
        BindingFailed, BindingRefused, bind_unit_to_idea)
    try:
        receipt = bind_unit_to_idea(program, unit.id, subject=subject)
    except BindingRefused as exc:
        detail = dict(exc.detail)
        detail.setdefault("unit_id", unit.id)
        detail["partial_bindings"] = list(partial)
        raise ContainmentRefused(exc.kind, str(exc), **detail) from exc
    except BindingFailed as exc:
        raise ContainmentFailed(
            str(exc), unit_id=unit.id,
            orphan_idea_id=exc.orphan_idea_id,
            partial_bindings=list(partial)) from exc
    if receipt.get("status") == "bound":
        partial.append({"unit_id": unit.id, "idea_id": receipt["idea_id"]})
    return unit.idea_id


def _load_graph(owner: str, partial):
    from form.mandell.semantic_graph import SemanticGraph, GraphValidationError
    try:
        return SemanticGraph.load(owner)
    except GraphValidationError as exc:
        raise ContainmentFailed(
            f"persisted graph state for owner {owner!r} failed "
            f"validation; refusing to operate on it: {exc}",
            partial_bindings=list(partial)) from exc


def _translate_graph_error(exc, partial):
    """GraphInvariantError -> ContainmentRefused with a stable kind;
    anything else -> ContainmentFailed (the mutation did not
    complete; the persisted graph is the graph's own rollback
    responsibility and is re-read fresh on the next operation)."""
    from form.mandell.semantic_graph import GraphInvariantError
    if isinstance(exc, GraphInvariantError):
        msg = str(exc)
        if "already has an active parent" in msg:
            kind = "second_parent"
        elif "cycle" in msg:
            kind = "cycle"
        elif "itself" in msg:
            kind = "self_containment"
        elif "not an existing idea" in msg or "no idea" in msg:
            kind = "target_missing"
        elif "no active parent" in msg:
            kind = "not_contained"
        else:
            kind = "graph_invariant"
        return ContainmentRefused(kind, msg,
                                  partial_bindings=list(partial))
    return ContainmentFailed(
        f"graph mutation did not complete: {type(exc).__name__}: {exc}",
        partial_bindings=list(partial))


def _provenance(subject: str, activity: str, detail: str):
    from form.mandell.idea import Provenance, ProvenanceSource
    return Provenance(source=ProvenanceSource.HUMAN, activity=activity,
                      agent=subject, detail=detail)


class _LockGate:
    """The canonical owner-state lock as a gate: busy past the
    bounded wait -> ContainmentRefused(state_locked); no unlocked
    fallback (§31.2). Re-entrant per thread: TD-1 binds inside
    join the same hold."""
    def __init__(self, program, partial):
        self._program = program
        self._partial = partial
        self._cm = None

    def __enter__(self):
        from form.owner_state_lock import (
            OwnerLockBusy, OwnerLockUnavailable, owner_state_lock)
        self._cm = owner_state_lock(self._program.owner)
        try:
            self._cm.__enter__()
        except OwnerLockBusy as exc:
            raise ContainmentRefused(
                "state_locked",
                f"owner state is locked by another writer and the "
                f"bounded wait expired; refusing containment: {exc}",
                partial_bindings=list(self._partial)) from exc
        except OwnerLockUnavailable as exc:
            raise ContainmentRefused(
                "state_lock_unavailable",
                f"no kernel lock mechanism is available; refusing "
                f"to run unlocked: {exc}",
                partial_bindings=list(self._partial)) from exc
        return self

    def __exit__(self, *exc):
        return self._cm.__exit__(*exc)


def _require_subject(subject):
    if not isinstance(subject, str) or not subject.strip():
        raise ContainmentRefused(
            "subject_required",
            "containment requires the real invoking subject for "
            "provenance")


def nest_units(program, child_unit_id: str, parent_unit_id: str, *,
               subject: str) -> Dict[str, Any]:
    """Nest one Plane unit inside another, through their canonical
    bindings. See the module docstring for the protocol."""
    _require_subject(subject)
    partial: List[Dict[str, str]] = []
    with _LockGate(program, partial):
        child = _unit(program, child_unit_id)
        parent = _unit(program, parent_unit_id)
        if child_unit_id == parent_unit_id:
            raise ContainmentRefused(
                "self_containment",
                f"unit {child_unit_id!r} cannot contain itself",
                unit_id=child_unit_id, partial_bindings=[])
        _check_sandbox(child, parent, partial)
        child_idea = _ensure_binding(program, child, subject, partial)
        _validate_active(program.owner, child_idea, child_unit_id, partial)
        parent_idea = _ensure_binding(program, parent, subject, partial)
        _validate_active(program.owner, parent_idea, parent_unit_id, partial)
        if child_idea == parent_idea:
            raise ContainmentRefused(
                "self_containment",
                f"units {child_unit_id!r} and {parent_unit_id!r} "
                f"resolve to the same Idea {child_idea!r}",
                child_unit_id=child_unit_id, parent_unit_id=parent_unit_id,
                partial_bindings=list(partial))
        graph = _load_graph(program.owner, partial)
        existing = graph.parent(child_idea)
        if existing == parent_idea:
            return {"status": "already_nested",
                    "child_unit_id": child_unit_id,
                    "parent_unit_id": parent_unit_id,
                    "child_idea_id": child_idea,
                    "parent_idea_id": parent_idea,
                    "partial_bindings": list(partial)}
        if existing is not None:
            raise ContainmentRefused(
                "second_parent",
                f"unit {child_unit_id!r} already has an active "
                f"containment parent (Idea {existing!r}); use "
                f"reparent to move it explicitly",
                child_unit_id=child_unit_id,
                parent_unit_id=parent_unit_id,
                existing_parent_idea_id=existing,
                partial_bindings=list(partial))
        if child_idea in graph.ancestors(parent_idea):
            raise ContainmentRefused(
                "cycle",
                f"nesting {child_unit_id!r} under "
                f"{parent_unit_id!r} would close a containment cycle",
                child_unit_id=child_unit_id,
                parent_unit_id=parent_unit_id,
                partial_bindings=list(partial))
        prov = _provenance(
            subject, "bridge_nest",
            f"TD-2 nest: unit {child_unit_id!r} under unit "
            f"{parent_unit_id!r} (owner {program.owner!r})")
        try:
            graph.nest(child_idea, parent_idea, prov)
        except Exception as exc:
            raise _translate_graph_error(exc, partial) from exc
        return {"status": "nested",
                "child_unit_id": child_unit_id,
                "parent_unit_id": parent_unit_id,
                "child_idea_id": child_idea,
                "parent_idea_id": parent_idea,
                "partial_bindings": list(partial)}


def promote_unit(program, unit_id: str, *,
                 subject: str) -> Dict[str, Any]:
    """Promote a unit to top level: supersede its active CONTAINS
    edge (history preserved). An unbound unit is already top level
    and mints nothing."""
    _require_subject(subject)
    partial: List[Dict[str, str]] = []
    with _LockGate(program, partial):
        unit = _unit(program, unit_id)
        idea_id = getattr(unit, "idea_id", None)
        if not idea_id:
            return {"status": "already_top_level", "unit_id": unit_id,
                    "idea_id": None, "partial_bindings": []}
        _validate_active(program.owner, idea_id, unit_id, partial)
        graph = _load_graph(program.owner, partial)
        former = graph.parent(idea_id)
        if former is None:
            return {"status": "already_top_level", "unit_id": unit_id,
                    "idea_id": idea_id, "partial_bindings": []}
        prov = _provenance(
            subject, "bridge_promote",
            f"TD-2 promote: unit {unit_id!r} to top level "
            f"(owner {program.owner!r})")
        try:
            graph.unnest(idea_id, prov)
        except Exception as exc:
            raise _translate_graph_error(exc, partial) from exc
        return {"status": "promoted", "unit_id": unit_id,
                "idea_id": idea_id, "former_parent_idea_id": former,
                "partial_bindings": list(partial)}


def reparent_unit(program, child_unit_id: str, new_parent_unit_id: str, *,
                  subject: str) -> Dict[str, Any]:
    """Move a unit's containment to a new parent explicitly (the
    graph's atomic supersede + activate). Identity is preserved."""
    _require_subject(subject)
    partial: List[Dict[str, str]] = []
    with _LockGate(program, partial):
        child = _unit(program, child_unit_id)
        parent = _unit(program, new_parent_unit_id)
        if child_unit_id == new_parent_unit_id:
            raise ContainmentRefused(
                "self_containment",
                f"unit {child_unit_id!r} cannot contain itself",
                unit_id=child_unit_id, partial_bindings=[])
        _check_sandbox(child, parent, partial)
        child_idea = _ensure_binding(program, child, subject, partial)
        _validate_active(program.owner, child_idea, child_unit_id, partial)
        parent_idea = _ensure_binding(program, parent, subject, partial)
        _validate_active(program.owner, parent_idea,
                         new_parent_unit_id, partial)
        if child_idea == parent_idea:
            raise ContainmentRefused(
                "self_containment",
                f"units {child_unit_id!r} and {new_parent_unit_id!r} "
                f"resolve to the same Idea {child_idea!r}",
                child_unit_id=child_unit_id,
                parent_unit_id=new_parent_unit_id,
                partial_bindings=list(partial))
        graph = _load_graph(program.owner, partial)
        existing = graph.parent(child_idea)
        if existing == parent_idea:
            return {"status": "already_parented",
                    "child_unit_id": child_unit_id,
                    "parent_unit_id": new_parent_unit_id,
                    "child_idea_id": child_idea,
                    "parent_idea_id": parent_idea,
                    "former_parent_idea_id": existing,
                    "partial_bindings": list(partial)}
        if child_idea in graph.ancestors(parent_idea):
            raise ContainmentRefused(
                "cycle",
                f"reparenting {child_unit_id!r} under "
                f"{new_parent_unit_id!r} would close a containment "
                f"cycle",
                child_unit_id=child_unit_id,
                parent_unit_id=new_parent_unit_id,
                partial_bindings=list(partial))
        prov = _provenance(
            subject, "bridge_reparent",
            f"TD-2 reparent: unit {child_unit_id!r} to unit "
            f"{new_parent_unit_id!r} (owner {program.owner!r})")
        try:
            graph.reparent(child_idea, parent_idea, prov)
        except Exception as exc:
            raise _translate_graph_error(exc, partial) from exc
        return {"status": "reparented",
                "child_unit_id": child_unit_id,
                "parent_unit_id": new_parent_unit_id,
                "child_idea_id": child_idea,
                "parent_idea_id": parent_idea,
                "former_parent_idea_id": existing,
                "partial_bindings": list(partial)}


def containment_view(program, unit_id: str) -> Dict[str, Any]:
    """Derived read: the unit's containment position, resolved
    through a freshly loaded graph and the Plane's pointers.
    Mints nothing, writes nothing."""
    unit = _unit(program, unit_id)
    plane = _plane(program)
    idea_id = getattr(unit, "idea_id", None)
    base = {"unit_id": unit_id, "label": unit.label, "idea_id": idea_id,
            "bound": bool(idea_id)}
    if not idea_id:
        return {**base, "idea_state": None, "parent_unit_id": None,
                "parent_idea_id": None, "children": [], "ancestors": [],
                "is_top_level": True}
    from form.mandell.idea_persist import load_idea
    try:
        idea = load_idea(idea_id, program.owner)
        idea_state = idea.idea_state.value if idea.id == idea_id else "invalid"
    except FileNotFoundError:
        idea_state = "missing"
    except ValueError:
        idea_state = "invalid"
    if idea_state in ("missing", "invalid"):
        return {**base, "idea_state": idea_state,
                "parent_unit_id": None, "parent_idea_id": None,
                "children": [], "ancestors": [], "is_top_level": None,
                "note": "binding target does not validate; "
                        "containment structure unavailable"}
    graph = _load_graph(program.owner, [])
    by_idea = {}
    for uid, u in plane.units.items():
        ptr = getattr(u, "idea_id", None)
        if ptr:
            by_idea[ptr] = uid

    def entry(iid):
        uid = by_idea.get(iid)
        return {"idea_id": iid, "unit_id": uid,
                "label": plane.units[uid].label if uid else None}

    parent_idea = graph.parent(idea_id)
    ancestors = [entry(iid) for iid in reversed(graph.ancestors(idea_id))]
    children = [entry(iid) for iid in graph.children(idea_id)]
    return {**base, "idea_state": idea_state,
            "parent_idea_id": parent_idea,
            "parent_unit_id": by_idea.get(parent_idea) if parent_idea else None,
            "parent": entry(parent_idea) if parent_idea else None,
            "children": children, "ancestors": ancestors,
            "is_top_level": parent_idea is None}
