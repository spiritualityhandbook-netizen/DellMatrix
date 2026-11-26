#!/usr/bin/env python3
"""Persist save/load/checkpoint/smoke bound from persist.py."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
import json
import math
import os
import sys

from form.mandell.floor import FLOOR, assert_floor_intact
from form.mandell.language import bind, empty_language, parse_language
from form.dell_matrix.plane import Perspective, Skin
from form.dell_matrix.resonance import ResonanceState
from form.dell_matrix.main_field import MainContribution, PullRecord
from form.dell_matrix.harmonic_lattice import HarmonicLattice, OverlayMode, Perspective as LatPerspective, SnapModule
from form.dell_matrix.perception import Form
from form.avatar import Facing, Posture, Locomotion, Reach, Expression
from form.open import Program, open_program
from form.persist_core_ii import restore_core_ii
from form.persist import serialize, _path, _cp_path, _safe_owner, _STATE_DIR, VERSION, _finite_json_violation
from form.dell_matrix.companion import _MAX_TRAIL as _COMPANION_MAX_TRAIL


def _is_finite_number(v: Any) -> bool:
    """True only for a finite int/float value.

    math.isfinite raises OverflowError on an oversized int (a 1001-digit
    integer token is valid JSON); such a value is not finite for any
    writer in this program, so the overflow reads as not-finite here
    instead of escaping as an untyped error.
    """
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return False
    try:
        return math.isfinite(v)
    except OverflowError:
        return False


class BindingLossSaveError(Exception):
    """TD-1-R2: a canonical save was refused because it would
    silently drop or re-point a persisted unit->Idea binding —
    the exact harm the Director's R2 directive names ('ordinary
    Program saves must not bypass it or silently overwrite a
    newer binding'). Reload so the binding is carried, then save.
    No bytes were written."""


def _persisted_bindings(target: str) -> dict:
    """{unit_id: idea_id} for bindings readable in the canonical
    file. Absent or unparseable state yields {} — unreadable
    bytes carry no binding to lose (a live instance's save over
    them is the repair; the load law and bind's F1 rule still
    refuse their own operations over corruption)."""
    if not os.path.isfile(target):
        return {}
    try:
        with open(target, "rb") as f:
            data = json.loads(f.read().decode("utf-8"))
        units = (data.get("plane") or {}).get("units") or {}
    except (OSError, UnicodeDecodeError, ValueError,
            AttributeError):
        return {}
    return {u: rec["idea_id"] for u, rec in units.items()
            if isinstance(rec, dict) and rec.get("idea_id")}


def _current_fingerprint(path: str):
    import hashlib as _hl
    if not os.path.isfile(path):
        return None
    with open(path, "rb") as f:
        return _hl.sha256(f.read()).hexdigest()


def _refuse_if_binding_loss(program: Program, target: str) -> None:
    """The save-side contract, scoped by regression evidence to
    the Director's exact words. All canonical saves serialize
    through the owner lock; the REFUSAL guards one harm — a
    binding silently lost to a writer that never saw it:

    * A CURRENT instance (its R1 version stamp matches the
      canonical file it last loaded/saved) is authoritative:
      its in-memory bindings ARE the latest intent, including
      deliberately clearing a pointer — TD-1's own round-trip
      contract does exactly that, and refusing it was a false
      positive found by full regression (234/235, TD-1 red in
      all three legs while green standalone).
    * A STALE or UNSTAMPED instance may save only if it carries
      every persisted (unit -> idea_id) binding identically.
      Losing or re-pointing one it never saw refuses the save.

    Legitimate whole-state flows (snapshot restore, generation
    rollback, two-instance authoring of unbound state) pass the
    stale-path comparison because they carry — or never had —
    the bindings; nothing is exempted by name."""
    stamp = getattr(program, "_td_state_fingerprint", None)
    if stamp is not None and _current_fingerprint(target) == stamp:
        return
    persisted = _persisted_bindings(target)
    if not persisted:
        return
    try:
        saver_units = program.cube.session.plane.units
    except AttributeError:
        return
    lost = sorted(
        u for u, iid in persisted.items()
        if getattr(saver_units.get(u), "idea_id", None) != iid)
    if lost:
        raise BindingLossSaveError(
            f"save for owner {program.owner!r} would silently "
            f"lose persisted unit binding(s) {lost}: the saver "
            f"does not carry them (reload so the bindings are "
            f"carried, then save)")


def _write_program_file(program: Program, target: str,
                        _fail_at: Optional[str]) -> str:
    from form.dell_matrix.atomic_write import atomic_write_json
    data = serialize(program)
    atomic_write_json(target, data, _fail_at=_fail_at)
    # TD-1-R1: stamp the saver with the version it just wrote (the
    # canonical state's SHA-256), so unit binding can detect that
    # the file has since moved under this instance. Best-effort:
    # a stamp failure never fails the save itself.
    try:
        import hashlib as _hl
        with open(target, "rb") as _f:
            program._td_state_fingerprint = _hl.sha256(
                _f.read()).hexdigest()
    except Exception:
        program._td_state_fingerprint = None
    return target


def save(program: Program, path: Optional[str] = None, *, _fail_at: Optional[str] = None) -> str:
    """Persist the program via Persistence V2 (crash-safe atomic replacement; DCC-XVII).

    The complete payload is serialized BEFORE the existing target is touched:
    serialization failure leaves the previous generation intact. After
    interruption the canonical file holds either the previous complete
    generation or the new complete generation -- never a partially
    serialized generation.

    Director 2026-10-06 (close unsafe save): an instance whose
    compensation/rollback was incomplete rejects the save with
    RollbackRecoveryError until verified restoration or reconstruction.
    No bytes are written on rejection.

    TD-1-R2 (atomic owner-state commit protection): a save to the
    CANONICAL owner path runs inside the owner-state lock
    (form.owner_state_lock) — no canonical save bypasses the
    transaction — and under that lock a save that would silently
    drop or re-point a persisted unit binding is refused with
    BindingLossSaveError (see _refuse_if_binding_loss for the
    contract and its regression-driven scoping). Saves to
    non-canonical paths (explicit temp or checkpoint files) are
    outside the transaction: they are not the canonical state.
    Journaled recovery/import writes that bypass this funnel
    entirely (Exchange import, core_i_recovery) are likewise
    outside R2's fence — a boundary stated in the R2 Director
    report, not silently expanded.
    """
    from form.mandell.core_i_recovery import check_save_allowed
    check_save_allowed(program, "persist_rest.save")
    target = path or _path(program.owner)
    canonical = os.path.abspath(target) == os.path.abspath(
        _path(program.owner))
    if not canonical:
        return _write_program_file(program, target, _fail_at)
    from form.owner_state_lock import owner_state_lock
    with owner_state_lock(program.owner):
        # 72-34 / DD-12: never overwrite a canonical file proven
        # to belong to a different raw owner (safe-name collision).
        from form.persist import assert_program_owner_access
        assert_program_owner_access(program.owner, target,
                                    "persist_rest.save")
        _refuse_if_binding_loss(program, target)
        return _write_program_file(program, target, _fail_at)


def checkpoint(program: Program, *, _fail_at: Optional[str] = None) -> str:
    """Write a legacy checkpoint file, then persist the program via guarded save().

    Director 2026-10-06 (close all exposed save paths): an instance whose
    compensation/rollback was incomplete rejects the checkpoint with
    RollbackRecoveryError at the FIRST write boundary -- before
    serialization, before the checkpoint file, and before the downstream
    save. No bytes are written on rejection.
    """
    from form.mandell.core_i_recovery import check_save_allowed
    check_save_allowed(program, "persist_rest.checkpoint")
    cp = _cp_path(program.owner)
    from form.dell_matrix.atomic_write import atomic_write_json

    atomic_write_json(cp, serialize(program), _fail_at=_fail_at)
    save(program, _fail_at=_fail_at)
    return cp


def list_checkpoints(owner: str) -> List[str]:
    prefix = f"program_{_safe_owner(owner)}_cp_"
    if not os.path.isdir(_STATE_DIR):
        return []
    return [
        os.path.join(_STATE_DIR, name)
        for name in sorted(os.listdir(_STATE_DIR))
        if name.startswith(prefix) and name.endswith(".json")
    ]


def _restore_avatar(p: Program, data: Dict[str, Any]) -> None:
    av = data.get("avatar") or {}
    if not av:
        return
    body = p.avatar.body
    if "name" in av:
        p.avatar.name = av["name"]
    if "pos" in av and isinstance(av["pos"], (list, tuple)) and len(av["pos"]) >= 2:
        body.pos = (int(av["pos"][0]), int(av["pos"][1]))
    for enum, attr, default in ((Facing, "facing", "N"), (Posture, "posture", "STAND"), (Locomotion, "locomotion", "IDLE"), (Reach, "reach", "CLOSE")):
        try:
            setattr(body, attr, enum[av.get(attr, default)])
        except Exception:
            setattr(body, attr, enum[default])
    body.holding = av.get("holding")
    try:
        p.face.current = Expression(av.get("expression", "neutral"))
    except Exception:
        p.face.current = Expression.NEUTRAL
    p.face.custom_face = av.get("custom_face")


# P0-R (Director 7085151190 item 2): lattice SnapModule registry format.
# Lattice-local marker inside the lattice section (NOT an envelope
# version bump): modules_format == 2 means `modules` is a list of
# lossless records {id, kind, axis, index, meta, cells:[[h,v,f],...]}
# whose coordinates reference the serialized lattice cells. Absence of
# the marker is the legacy shape: the pre-fix writer emitted module IDs
# only, so the records were never written.
_LATTICE_MODULES_FORMAT = 2
_LATTICE_MODULE_KEYS = frozenset(("id", "kind", "axis", "index", "meta", "cells"))


def _stage_lattice_modules(raw: Dict[str, Any], owner: str):
    """Validate the lattice modules field and return staged specs
    [(id, kind, axis, index, meta, coords)] in file order.

    Runs BEFORE the lattice is rebuilt and raises ProgramLoadError on
    any violation; _load_impl builds a private Program and load never
    writes, so a refusal swaps nothing and preserves the source bytes.

    Legacy rule: with no format marker, an absent or empty modules
    field is supported (empty registry). A NONEMPTY IDs-only list is
    IRRECOVERABLE -- the payloads were never written -- so it fails
    closed here; IDs are never dressed up as empty modules and no
    facts are reconstructed from geometry.

    Presence pin (Director CORRECTION_REQUIRED 7166217199): the
    modules field itself is presence-checked, exactly like the format
    marker below. A PRESENT null modules field is NOT an absent one:
    the lawful legacy shapes are only a missing field or an empty
    list, so a present null refuses typed here instead of loading as
    an empty registry that a later save would rewrite as fact.

    Marker pin (Director REVIEW 7137053864): legacy treatment keys on
    the marker being ABSENT from the record. A PRESENT marker --
    including an explicit null -- is never legacy; it falls through
    to the format check below and refuses typed when it is not the
    supported format.
    """
    mods = raw.get("modules")
    if "modules_format" not in raw:
        if "modules" in raw and mods is None:
            raise ProgramLoadError(
                "lattice modules field is present but null (records "
                "without the modules_format marker): refusing load "
                "rather than treating a present null as an absent "
                "field or an empty registry")
        if mods is None or mods == []:
            return []
        if isinstance(mods, list) and all(isinstance(m, str) for m in mods):
            raise ProgramLoadError(
                "lattice modules field is a legacy IDs-only list: the module "
                "records were never written and are irrecoverable; refusing "
                "load rather than fabricating modules from IDs")
        raise ProgramLoadError(
            "lattice modules field is malformed (records without the "
            "modules_format marker): refusing load")
    fmt = raw["modules_format"]
    if isinstance(fmt, bool) or not isinstance(fmt, int) or fmt != _LATTICE_MODULES_FORMAT:
        raise ProgramLoadError(
            f"lattice modules_format {fmt!r} is not supported "
            f"(current {_LATTICE_MODULES_FORMAT}): refusing load")
    if not isinstance(mods, list):
        raise ProgramLoadError(
            "lattice modules field must be a list of module records "
            "under modules_format 2: refusing load")
    cells_raw = raw.get("cells") or {}
    if not isinstance(cells_raw, dict):
        raise ProgramLoadError("lattice cells field is not an object: refusing load")
    seen_ids = set()
    claimed: Dict[Any, str] = {}
    staged = []
    for i, item in enumerate(mods):
        if not isinstance(item, dict):
            raise ProgramLoadError(
                f"lattice module record #{i} is not an object: refusing load")
        if "owner" in item and item["owner"] != owner:
            raise ProgramLoadError(
                f"lattice module record #{i} carries foreign owner "
                f"{item['owner']!r} (file owner {owner!r}): refusing load")
        keys = set(item.keys())
        if keys != _LATTICE_MODULE_KEYS:
            raise ProgramLoadError(
                f"lattice module record #{i} has inconsistent keys "
                f"{sorted(keys)} (expected {sorted(_LATTICE_MODULE_KEYS)}): refusing load")
        mid = item["id"]
        if not isinstance(mid, str) or not mid:
            raise ProgramLoadError(
                f"lattice module record #{i} has invalid id {mid!r}: refusing load")
        if mid in seen_ids:
            raise ProgramLoadError(
                f"duplicate lattice module id {mid!r}: refusing load")
        seen_ids.add(mid)
        kind, axis, index, meta = item["kind"], item["axis"], item["index"], item["meta"]
        if not isinstance(kind, str) or not kind:
            raise ProgramLoadError(
                f"lattice module {mid!r} has invalid kind {kind!r}: refusing load")
        if not isinstance(axis, str) or not axis:
            raise ProgramLoadError(
                f"lattice module {mid!r} has invalid axis {axis!r}: refusing load")
        if isinstance(index, bool) or not isinstance(index, int):
            raise ProgramLoadError(
                f"lattice module {mid!r} has invalid index {index!r}: refusing load")
        if not isinstance(meta, dict):
            raise ProgramLoadError(
                f"lattice module {mid!r} meta is not an object: refusing load")
        violation = _finite_json_violation(meta)
        if violation is not None:
            raise ProgramLoadError(
                f"lattice module {mid!r} meta is not finite JSON "
                f"({violation}): refusing load")
        cells_field = item["cells"]
        if not isinstance(cells_field, list):
            raise ProgramLoadError(
                f"lattice module {mid!r} cells is not a coordinate list: refusing load")
        coords = []
        local = set()
        for c in cells_field:
            if (not isinstance(c, (list, tuple)) or len(c) != 3
                    or any(isinstance(x, bool) or not isinstance(x, int) for x in c)):
                raise ProgramLoadError(
                    f"lattice module {mid!r} has invalid cell coordinate {c!r}: refusing load")
            coord = (c[0], c[1], c[2])
            if coord in local:
                raise ProgramLoadError(
                    f"lattice module {mid!r} lists cell {coord} twice: refusing load")
            local.add(coord)
            if f"{coord[0]},{coord[1]},{coord[2]}" not in cells_raw:
                raise ProgramLoadError(
                    f"lattice module {mid!r} references cell {coord} absent "
                    "from the lattice cells: refusing load")
            if coord in claimed:
                raise ProgramLoadError(
                    f"lattice modules {claimed[coord]!r} and {mid!r} overlap "
                    f"at cell {coord}: refusing load")
            claimed[coord] = mid
            coords.append(coord)
        staged.append((mid, kind, axis, index, meta, coords))
    return staged


def _restore_lattice(p: Program, data: Dict[str, Any]) -> None:
    # Persistence-integrity (Part I SAVE/JOURNAL; Director clearance
    # PR #505 comment 7076723491): the lattice is user-authored content.
    # An ABSENT section is a legacy save and leaves the prepared
    # program's default lattice. A PRESENT but malformed section (wrong
    # type, unparseable scalar, invalid setting, malformed cell) FAILS
    # CLOSED with ProgramLoadError, raised before any swap or write —
    # the candidate is staged privately and swapped only after complete
    # validation, so one corrupt value can never wipe the owner's
    # authored lattice or be made permanent by a later save.
    #
    # Composition (PR #519 x PR #526, Uni, 2026-11-25): the staged
    # fail-closed cell restore above is main's body; the modules
    # registry staging and binding below is PR #519's P0-R repair,
    # retargeted onto the staged lattice so both contracts hold at
    # once — a malformed registry refuses the whole load typed, and a
    # module referencing a cell that did not survive the staged cell
    # restore refuses before the swap. This discharges the former
    # KNOWN RESIDUAL noted against the modules field.
    if "lattice" not in data:
        return
    raw = data["lattice"]
    if not isinstance(raw, dict):
        raise ProgramLoadError(
            "lattice section is not an object: "
            f"{type(raw).__name__}; refusing load")
    # P0-R: validate the modules field STAGED, before the cell
    # restore — a malformed registry refuses the whole load typed
    # instead of being swallowed into a default lattice.
    staged_modules = _stage_lattice_modules(raw, p.owner)

    def _int_field(name: str, default: int) -> int:
        value = raw.get(name, default)
        if isinstance(value, bool) or not isinstance(value, int):
            raise ProgramLoadError(
                f"lattice.{name} is not an integer: {value!r}; "
                "refusing load")
        return value

    staged = HarmonicLattice(size=_int_field("size", 12))
    if "overlay" in raw:
        try:
            staged.overlay = OverlayMode(raw["overlay"])
        except (TypeError, ValueError):
            raise ProgramLoadError(
                "lattice.overlay is not a known overlay: "
                f"{raw['overlay']!r}; refusing load")
    if "perspective" in raw:
        try:
            staged.perspective = LatPerspective(raw["perspective"])
        except (TypeError, ValueError):
            raise ProgramLoadError(
                "lattice.perspective is not a known perspective: "
                f"{raw['perspective']!r}; refusing load")
    if "form" in raw:
        try:
            staged.perception.set_form(Form(raw["form"]))
        except (TypeError, ValueError):
            raise ProgramLoadError(
                "lattice.form is not a known form: "
                f"{raw['form']!r}; refusing load")
    staged.origin_note = _int_field("origin_note", 0)
    raw_cells = raw.get("cells", {})
    if not isinstance(raw_cells, dict):
        raise ProgramLoadError(
            "lattice.cells is not an object: "
            f"{type(raw_cells).__name__}; refusing load")
    for key, cell in raw_cells.items():
        if not isinstance(cell, dict):
            raise ProgramLoadError(
                f"lattice cell {key!r} is not an object; refusing load")
        coords: Dict[str, int] = {}
        for axis in ("h", "v", "f"):
            value = cell.get(axis, 0)
            if isinstance(value, bool) or not isinstance(value, int):
                raise ProgramLoadError(
                    f"lattice cell {key!r} has non-integer {axis}: "
                    f"{value!r}; refusing load")
            coords[axis] = value
        # Finding B (Director CORRECTION_REQUIRED 7079022510): the
        # saved key is part of the cell's identity. The writer emits
        # exactly the canonical "h,v,f" key for a cell's own
        # coordinates, one cell per coordinate — so a key that
        # disagrees with its cell's coordinates, or a second cell
        # claiming coordinates already restored, is not
        # legacy-producible and fails closed instead of silently
        # overwriting (HarmonicLattice.put assigns by coordinate).
        canonical = f"{coords['h']},{coords['v']},{coords['f']}"
        if key != canonical:
            raise ProgramLoadError(
                f"lattice cell key {key!r} does not match its "
                f"coordinates {canonical!r}; refusing load")
        if (coords["h"], coords["v"], coords["f"]) in staged.cells:
            raise ProgramLoadError(
                f"lattice cell {key!r} duplicates coordinates "
                f"{canonical!r}; refusing load")
        tags = cell.get("tags", [])
        members = cell.get("members", [])
        if not isinstance(tags, list) or not isinstance(members, list):
            raise ProgramLoadError(
                f"lattice cell {key!r} has non-list tags/members; "
                "refusing load")
        try:
            staged.put(coords["h"], coords["v"], coords["f"],
                       content=cell.get("content"),
                       label=cell.get("label", ""),
                       tags=list(tags), members=list(members))
        except Exception as exc:
            raise ProgramLoadError(
                f"lattice cell {key!r} failed to restore: {exc}; "
                "refusing load")
    # Bind staged modules to the staged lattice cells by coordinate
    # (Option B). A referenced coordinate that did not survive the
    # staged cell restore refuses the load rather than binding a
    # partial membership; the swap below has not happened yet, so the
    # refusal swaps nothing.
    for mid, kind, axis, index, meta, coords_list in staged_modules:
        bound = {}
        for coord in coords_list:
            cell = staged.cells.get(coord)
            if cell is None:
                raise ProgramLoadError(
                    f"lattice module {mid!r} references cell {coord} that did "
                    "not survive lattice restore: refusing load")
            bound[coord] = cell
        staged.modules[mid] = SnapModule(
            id=mid, kind=kind, axis=axis, index=index, cells=bound, meta=dict(meta))
    p.lattice = staged


class ProgramLoadError(ValueError):
    """Program file content is missing/invalid or its owner binding is inconsistent; raised before any swap."""


# Proven historical envelope versions (RTPH-I-R4C): every value below was written by
# serialize() into the DellMatrixProgramState envelope at the cited commit. No version 0
# or negative version was ever emitted by the supported writer.
#   v1  2e786ce  NBD: Persist (first envelope)
#   v2  2818dfc  NBD: Surface coherence
#   v3  b3c72d5  NBD: Persist L3
#   v4  c13d7c9  Form 1.00 scope lock
#   v5  747d3e3  SUS code pass
#   v6  4c3ab5c  Solid session save/load v6 (VERSION = 6)
#   v7  7768f20  NBD 1: HarmonicLattice (VERSION = 7, current)
_LEGACY_VERSIONS = frozenset((1, 2, 3, 4, 5, 6))


def _validate_envelope_version(data: Dict[str, Any]) -> None:
    """Explicit envelope-version contract (RTPH-I R4, narrowed by RTPH-I-R4C).

    Raises ProgramLoadError LOUDLY on unsupported versions. This runs inside
    _validate_program_data, i.e. before any semantic swap: a failed validation changes no binding,
    no CELLS/customs, no Program, and rewrites no file (load() never writes).

    Policy:
      version == VERSION (7)  → current format: ACCEPT.
      version missing         → legacy envelope: ACCEPT explicitly (deliberate RTPH-I leniency;
                                no migration invented; resave stamps the current version).
      version in {1, 2, 3, 4, 5, 6} → legacy envelope: ACCEPT explicitly. Git history proves
                                each of v1..v6 was emitted by the supported writer
                                (see _LEGACY_VERSIONS). No migration semantics are invented:
                                the file is read by the current reader, and any resave stamps
                                the current version.
      any other explicit int  → REJECT. Version 0 and negatives never existed; versions > 7
                                are unknown future schemas that must never be silently misread.
      version present but not an int → REJECT (covers "7", null/None, bool, float, ...).
          bool is rejected explicitly: isinstance(True, int) is True in Python.
    """
    if "version" not in data:
        return  # legacy envelope: accepted explicitly, no migration invented
    v = data["version"]
    if isinstance(v, bool) or not isinstance(v, int):
        raise ProgramLoadError(f"program file has non-integer envelope version {v!r}: refusing load")
    if v == VERSION:
        return  # current format
    if v in _LEGACY_VERSIONS:
        return  # legacy envelope: proven historical version, no migration invented
    raise ProgramLoadError(
        f"program file envelope version {v} is not supported (current {VERSION}, legacy 1-6): refusing load"
    )


def _validate_program_data(data: Any, owner: str) -> str:
    """VALIDATE the program envelope (language is validated by parse_language). Returns the resolved owner."""
    if not isinstance(data, dict):
        raise ProgramLoadError("program file is not a JSON object")
    _validate_envelope_version(data)
    if data.get("floor") != list(FLOOR):
        raise RuntimeError("Floor mismatch — refuse load")
    plane = data.get("plane")
    if not isinstance(plane, dict) or not isinstance(plane.get("units", {}), dict):
        raise ProgramLoadError("program data missing or invalid: 'plane' (with 'units') must be an object")
    file_owner = data.get("owner")
    if file_owner is not None and (not isinstance(file_owner, str) or not file_owner):
        raise ProgramLoadError("program data invalid: 'owner' must be a non-empty string")
    return file_owner or owner


def load(owner: str = "Operator", path: Optional[str] = None, activate: bool = True) -> Program:
    """READ > VALIDATE COMPLETE INPUT > PREPARE language > PREPARE Program > ASSERT OWNER/BINDING > SWAP > RETURN.

    Every step before the swap only builds private objects: a failure raises and leaves the bound owner, the
    working copy (CELLS/customs) and every existing Program unchanged. The swap is bind(p) (skipped with
    activate=False, e.g. AUTO loading AutoGrow). The Program's owner is the file's owner (Q-016 resolution);
    its nursery and language are that owner's and nothing of the previously bound owner is combined into it.
    A missing file yields a fresh owner: empty cells + default customs (D2), never the active owner's language.
    load() writes no file.

    Gate R2 (Finding 1): before exposing live state, deterministically
    recover any interrupted rollback transaction for this owner, so a
    reader never accepts a hybrid program/nursery pair.
    """
    assert_floor_intact()
    # 72-34 / DD-12: on the DEFAULT path, refuse a proven foreign
    # owner BEFORE any recovery journal is replayed or state is
    # adopted — the shared safe-name file may belong to a colliding
    # raw owner. An explicit path keeps the pinned Q-016 behavior
    # (the load resolves to the file's owner).
    if path is None:
        from form.persist import assert_program_owner_access
        assert_program_owner_access(owner, _path(owner),
                                    "persist_rest.load")
    # Checkpoint-intent recovery (Ten-Phase P2, t11 closure) runs FIRST:
    # it restores the raw pre-seal live pair that the transaction
    # recoveries below reason about. A checkpoint journal means the
    # seal's sequential saves were interrupted mid-commit.
    from form.mandell.core_i_recovery import recover_checkpoint_intent
    recover_checkpoint_intent(owner)
    # Transactional rollback recovery (Gate R3: FAIL-CLOSED). If a journal
    # exists, recovery must establish a proven-coherent pair or raise
    # RollbackRecoveryError. Never suppress; never expose potentially
    # hybrid state.
    from form.mandell.core_i_recovery import recover_rollback_transaction
    recover_rollback_transaction(owner)
    # Confirmation-intent recovery (GDP_R3_IDEA_PRESERVATION_ADDENDUM).
    # Recovers from RECORDED INTENT (journal), not inferred visibility.
    from form.mandell.core_i_recovery import recover_confirmation_intent
    recover_confirmation_intent(owner)
    # Supersession-intent recovery (GDP_R3_COMPLETION_GATE req. 3).
    # Recovers the complete supersession transition (successor, predecessor,
    # links) from the enclosing journal.
    from form.mandell.core_i_recovery import recover_supersede_intent
    recover_supersede_intent(owner)
    # Exchange import recovery (DAF-06, step 5b). An import spans
    # the nursery file and the program file; its journal is the
    # recorded intent. Resolve it here — complete imports stand,
    # partial/aborted imports are removed and verified — before
    # any state is exposed. No journal: no-op.
    from form.dell_matrix.exchange import recover_exchange_import
    recover_exchange_import(owner)
    path = path or _path(owner)
    if not os.path.isfile(path):
        p = open_program(owner)
        p.language = empty_language()
        # R7.4 (D1): a brand-new owner (no persisted state at all)
        # starts at the first-run disclosure level with onboarding
        # begun. Legacy owners always take the file path above, where
        # an absent onboarding section leaves their mode untouched.
        from form.dell_matrix.onboarding_session import mark_new_owner
        mark_new_owner(p)
        if activate:
            bind(p)
        # R6.3: record the restoration epoch at load; saves from a
        # pre-restoration instance are rejected by check_save_allowed.
        from form.mandell.core_i_recovery import _rollback_epochs
        p._rollback_epoch = _rollback_epochs.get(owner, 0)
        return p
    p = _load_impl(owner, path, None, activate)
    # R6.3: record the restoration epoch at load.
    from form.mandell.core_i_recovery import _rollback_epochs
    p._rollback_epoch = _rollback_epochs.get(owner, 0)
    return p


def _load_impl(owner: str, path: str, nursery, activate: bool) -> Program:
    """Shared staged-load core: READ > VALIDATE > PREPARE > ASSERT BINDING > SWAP.

    ``nursery`` is None on the live path: Program loads the owner's live
    nursery file and the Q-016 live binding is asserted. A provided Nursery
    stages a generation member: the program is built against exactly that
    staged nursery and no live file is consulted. Every step before the swap
    only builds private objects; a failure raises and leaves live state
    untouched.
    """
    assert_floor_intact()
    if not os.path.isfile(path):
        raise ProgramLoadError(
            f"program member file missing: {os.path.basename(path)} (refusing to fabricate state)"
        )
    with open(path, "rb") as f:
        _blob = f.read()
    data = json.loads(_blob.decode("utf-8"))
    resolved = _validate_program_data(data, owner)
    lang = parse_language(data)
    p = _prepare_program(resolved, data, _nursery=nursery)
    if nursery is None:
        # TD-1-R1: stamp the loaded instance with the version it
        # derives from (live path only — staged generation members
        # are not a baseline for canonical-state binding).
        import hashlib as _hl
        p._td_state_fingerprint = _hl.sha256(_blob).hexdigest()
    p.language = lang
    if nursery is None:
        from form.dell_matrix.nursery import owner_nursery_path
        if p.owner != resolved or getattr(p.nursery, "path", None) != owner_nursery_path(resolved):
            raise ProgramLoadError(f"owner binding mismatch: prepared {p.owner!r} for file owner {resolved!r}")
    elif p.owner != resolved or p.nursery is not nursery:
        raise ProgramLoadError("generation member binding mismatch: staged nursery was not used")
    if nursery is not None:
        # DCC-XVIII repair (GDP-001 Phase 0, R1): the staged nursery is bound
        # to the SEALED generation member file. Copy-on-rollback + re-point:
        # re-point the instance to the live owner file NOW, so committed /
        # sealed state and mutable working state have explicit, non-aliased
        # ownership. The sealed member is never written through this program
        # again; the next nursery save() persists the rolled-back working
        # state to the live file. No live file is written here (load stays
        # read-pure) and the staged in-memory proposals are untouched.
        from form.dell_matrix.nursery import owner_nursery_path
        nursery.repoint_to_live(owner_nursery_path(resolved))
    if activate:
        bind(p)
    return p


def _duo_target_generation(data: Dict[str, Any]) -> int:
    """The saved duo_generation counter, type-checked (MEDIUM-four A).

    The writer (form/persist.py) always emits an int. Anything else
    present under the key is malformed and refuses typed instead of
    crashing int() with an untyped error.
    """
    raw = data.get("duo_generation", 0)
    if isinstance(raw, bool) or not isinstance(raw, int):
        raise ProgramLoadError(
            f"program file 'duo_generation' is not an integer (got {raw!r}): refusing load")
    return raw


def _validate_duo_ledger_section(raw: Any) -> List[Dict[str, Any]]:
    """Stage-validate a PRESENT duo_ledger section (MEDIUM-four A).

    Returns the staged entry dicts in file order; raises ProgramLoadError
    before any state is touched. The writer emits a list of
    {gen:int, detail:str, ts:str, meta:dict} entries with gen >= 1 and
    strictly increasing gens (generation gaps are lawful — the counter
    can advance without an entry surviving — duplicates and regressions
    are not). A malformed entry refuses the whole load: no silent entry
    drops, no per-field emptying. Extra unknown keys on an entry are
    forward compatibility, not refusal.
    """
    if not isinstance(raw, list):
        raise ProgramLoadError(
            f"program file 'duo_ledger' section is not a list "
            f"(got {type(raw).__name__}): refusing load")
    staged: List[Dict[str, Any]] = []
    last = 0
    for i, e in enumerate(raw):
        if not isinstance(e, dict):
            raise ProgramLoadError(
                f"program file 'duo_ledger' entry {i} is not an object "
                f"(got {type(e).__name__}): refusing load")
        gen = e.get("gen")
        if isinstance(gen, bool) or not isinstance(gen, int):
            raise ProgramLoadError(
                f"program file 'duo_ledger' entry {i} has non-integer gen {gen!r}: refusing load")
        if gen < 1:
            raise ProgramLoadError(
                f"program file 'duo_ledger' entry {i} has gen {gen} < 1 "
                f"(writer generations start at 1): refusing load")
        if gen <= last:
            raise ProgramLoadError(
                f"program file 'duo_ledger' entry {i} has gen {gen} not greater than "
                f"the previous entry's gen {last} (duplicate or non-monotonic): refusing load")
        detail = e.get("detail", "")
        if not isinstance(detail, str):
            raise ProgramLoadError(
                f"program file 'duo_ledger' entry {i} has non-string detail "
                f"(got {type(detail).__name__}): refusing load")
        ts = e.get("ts", "")
        if not isinstance(ts, str):
            raise ProgramLoadError(
                f"program file 'duo_ledger' entry {i} has non-string ts "
                f"(got {type(ts).__name__}): refusing load")
        meta = e.get("meta", {})
        if not isinstance(meta, dict):
            raise ProgramLoadError(
                f"program file 'duo_ledger' entry {i} has non-object meta "
                f"(got {type(meta).__name__}): refusing load")
        staged.append({"gen": gen, "detail": detail, "ts": ts, "meta": dict(meta)})
        last = gen
    return staged


def _restore_duo_ledger(p: Program, data: Dict[str, Any], target_gen: int) -> None:
    """Restore the DuoBeta growth ledger faithfully (DCC-I).

    Envelopes written with duo_ledger carry the actual recorded entries; they
    are restored exactly, in order, with no synthetic entries. Legacy envelopes
    (no duo_ledger) restore the generation count with a single honest marker
    entry instead of fabricating per-generation history.

    MEDIUM-four A: a PRESENT duo_ledger section is stage-validated whole
    (_validate_duo_ledger_section) and any malformed entry refuses the load
    with ProgramLoadError before the ledger is touched — the former
    skip-and-continue restore silently dropped malformed entries and
    emptied non-dict meta, and the next save made the loss permanent.

    Present-but-empty with a positive generation is malformed, not legacy:
    the writer pairs every generation increment with exactly one ledger
    append (DuoBeta.evolve; duobeta_learn._append_learn_entry) and never
    removes entries, so the serializer cannot emit it. It refuses typed
    instead of receiving the legacy marker, which is for ABSENT keys only
    (Director CORRECTION REQUIRED 7083412844).
    """
    from datetime import datetime, timezone
    from form.duobeta.growth import GrowthEntry

    # Stage first: validation raises before any mutation below.
    staged: List[Dict[str, Any]] = []
    if "duo_ledger" in data:
        staged = _validate_duo_ledger_section(data["duo_ledger"])
        if not staged and target_gen > 0:
            raise ProgramLoadError(
                f"program file 'duo_ledger' section is present but empty while "
                f"'duo_generation' is {target_gen} (the writer pairs every "
                f"generation with a ledger entry): refusing load")
    clean = [GrowthEntry(
        gen=s["gen"],
        # R26: detail restored WHOLE (former [:120] re-cut
        # at load any whole entry written by repaired code).
        detail=s["detail"],
        ts=s["ts"],
        # DBEL-I: restore learning metadata (additive; {} for legacy).
        meta=s["meta"],
    ) for s in staged]

    # The fresh Program from open_program() already carries one startup entry
    # ("Open"); the saved ledger is the truth, so reset before restoring.
    p.duo.ledger.clear()
    p.duo.generation = 0

    if clean:
        p.duo.ledger.extend(clean)
        p.duo.generation = max(target_gen, clean[-1].gen)
    elif target_gen > 0:
        p.duo.ledger.append(GrowthEntry(
            gen=target_gen,
            detail="restored from pre-ledger envelope (prior history not recorded)",
            ts=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        ))
        p.duo.generation = target_gen


def _admit_custom_personas(section: List[Any]) -> None:
    """Scope A restore admission (Director §5 ruling 7079370876).

    A PRESENT custom_personas list is admitted only if EVERY record
    is a mapping passing validate_custom_persona AND the normalized
    ids (same strip().lower() as _normalize_record) are unique.
    Otherwise PersonaLoadError naming the record index / id and the
    reason — raised BEFORE activate_custom_personas or
    _bind_persona_layer run, so a refusal mutates nothing: not the
    input list, not the bound Program, not the source file, not the
    default global persona layer, not any other owner's state.

    Why refusal, not the previous skip-and-report: every saved
    custom_personas record is user-authored. The skip policy dropped
    a skipped record from user_personas, so the next ordinary save
    destroyed its original bytes durably (isolation evidence
    PR505_ISOLATION_EVIDENCE_2026-11-22 §4(1)), and duplicate
    normalized ids silently overwrote last-write-wins (§4(2)). The
    standalone activate_custom_personas skip contract is unchanged
    for its other callers — this gate localizes to the persist
    restore path only. No quarantine field is introduced (forbidden
    this circuit: a downgraded v7 writer could silently delete an
    unknown persisted field on ordinary save).

    Admission validates with persisted=True (Director
    CORRECTION_REQUIRED 7136802347): a PRESENT matrix /
    prefer_skins field must carry its lawful container type as
    recorded — the validator's permissive ``or {}`` / ``or []``
    coercions are for the standalone contract only, since on this
    path a coerced record is normalized into user_personas and
    the next ordinary save erases the original form."""
    from form.dell_matrix.personas import (
        PersonaLoadError, validate_custom_persona)
    seen: Dict[str, int] = {}
    for index, record in enumerate(section):
        if not isinstance(record, dict):
            raise PersonaLoadError(
                f"custom_personas record {index}: "
                "persona record must be a mapping")
        reason = validate_custom_persona(record, persisted=True)
        if reason:
            raise PersonaLoadError(
                f"custom_personas record {index} "
                f"(id {record.get('id')!r}): {reason}")
        norm_id = record["id"].strip().lower()
        if norm_id in seen:
            raise PersonaLoadError(
                f"custom_personas record {index} "
                f"(id {record.get('id')!r}): duplicate normalized id "
                f"{norm_id!r} (first at record {seen[norm_id]})")
        seen[norm_id] = index


def _validate_companion_section(raw: Any) -> None:
    """Stage-validate a PRESENT companion section (MEDIUM-four B).

    Raises ProgramLoadError before any state is touched. The writer
    (AICompanion.to_dict) emits a dict of string fields, a 2-number pos,
    and a trail of 2-number points. Any field failing that shape —
    wrong container, non-string scalar in a string field, a bool or
    nonfinite or non-numeric coordinate, a truncated or extra-coordinate
    pos, one malformed trail point, a trail longer than the writer cap
    — refuses the whole load: the former restore wrapped
    from_dict in a blanket except/pass, so a single bad trail point
    silently reset the companion's entire continuity state (identity,
    position, mode, full trail) to the constructor default. Missing
    fields keep from_dict's per-field defaults; extra unknown keys are
    forward compatibility, not refusal; the derived z key is ignored.
    A field PRESENT with an explicit null is not missing (Director
    CORRECTION_REQUIRED 7136700328): the writer never emits null for
    any companion field, so a present null refuses typed instead of
    receiving from_dict's default substitution (pos -> [2, 1], a
    string field -> its default, trail -> []).
    """
    if not isinstance(raw, dict):
        raise ProgramLoadError(
            f"program file 'companion' section is not an object "
            f"(got {type(raw).__name__}): refusing load")
    for field in ("name", "label", "facing", "mode", "doing", "last_action"):
        if field not in raw:
            continue
        v = raw[field]
        if not isinstance(v, str):
            raise ProgramLoadError(
                f"program file 'companion' field {field!r} is not a string "
                f"(got {type(v).__name__}): refusing load")

    def _coord(v: Any, where: str) -> None:
        if not _is_finite_number(v):
            raise ProgramLoadError(
                f"program file 'companion' {where} is not a finite number "
                f"(got {v!r}): refusing load")

    def _point(pt: Any, where: str) -> None:
        if not isinstance(pt, (list, tuple)) or len(pt) != 2:
            raise ProgramLoadError(
                f"program file 'companion' {where} is not a 2-number point: refusing load")
        _coord(pt[0], where)
        _coord(pt[1], where)

    if "pos" in raw:
        _point(raw["pos"], "'pos'")
    if "trail" in raw:
        trail = raw["trail"]
        if not isinstance(trail, list):
            raise ProgramLoadError(
                f"program file 'companion' field 'trail' is not a list "
                f"(got {type(trail).__name__}): refusing load")
        if len(trail) > _COMPANION_MAX_TRAIL:
            raise ProgramLoadError(
                f"program file 'companion' field 'trail' holds "
                f"{len(trail)} points, more than the writer ever emits "
                f"({_COMPANION_MAX_TRAIL}): refusing load")
        for i, pt in enumerate(trail):
            _point(pt, f"'trail' point {i}")


def _validate_self_knowledge_section(raw: Any) -> None:
    """Stage-validate a PRESENT self_knowledge section (MEDIUM-four C).

    Raises ProgramLoadError before any state is touched. The writer
    (SelfKnowledge.to_dict) emits mastery as a dict of floats in
    [0, 1], the counters probes/hits/generations_seen as non-negative
    ints with hits <= probes, and the three inventories as lists of
    strings. Anything failing that shape refuses the whole load: the
    former restore wrapped from_dict in a blanket except/pass, so one
    non-numeric mastery value silently blanked the entire self-model,
    and list() on a string inventory silently rewrote it into single
    characters (SK-E corruption). The derived keys (hit_rate,
    ledger_len, avg_mastery) are serializer-computed and stay ignored
    — recomputed from the restored fields, never trusted, never
    validated. The dataclass fields last_reflect/ledger are NOT
    serialized (ledger survives only as its length); that asymmetry is
    intended nonpersistence, not corruption, and is left untouched.
    A field PRESENT with an explicit null is not missing (Director
    CORRECTION_REQUIRED 7136700328): the writer never emits null for
    mastery, the counters, or the inventories, so a present null
    refuses typed instead of receiving from_dict's default
    substitution ({} / 0 / []). The derived keys stay exempt: they
    are never read on restore, so a null there substitutes nothing.
    """
    if not isinstance(raw, dict):
        raise ProgramLoadError(
            f"program file 'self_knowledge' section is not an object "
            f"(got {type(raw).__name__}): refusing load")
    if "mastery" in raw:
        mastery = raw["mastery"]
        if not isinstance(mastery, dict):
            raise ProgramLoadError(
                f"program file 'self_knowledge' field 'mastery' is not an object "
                f"(got {type(mastery).__name__}): refusing load")
        for k, v in mastery.items():
            if not _is_finite_number(v) or not (0.0 <= v <= 1.0):
                raise ProgramLoadError(
                    f"program file 'self_knowledge' mastery[{k!r}] is not a "
                    f"finite number in [0, 1] (got {v!r}): refusing load")
    counters: Dict[str, int] = {}
    for field in ("probes", "hits", "generations_seen"):
        if field not in raw:
            counters[field] = 0
            continue
        v = raw[field]
        if isinstance(v, bool) or not isinstance(v, int) or v < 0:
            raise ProgramLoadError(
                f"program file 'self_knowledge' field {field!r} is not a "
                f"non-negative integer (got {v!r}): refusing load")
        counters[field] = v
    if counters["hits"] > counters["probes"]:
        raise ProgramLoadError(
            f"program file 'self_knowledge' hits ({counters['hits']}) exceeds "
            f"probes ({counters['probes']}): refusing load")
    for field in ("known_matrices", "known_snaps", "gaps_closed"):
        if field not in raw:
            continue
        v = raw[field]
        if not isinstance(v, list):
            raise ProgramLoadError(
                f"program file 'self_knowledge' field {field!r} is not a list "
                f"(got {type(v).__name__}): refusing load")
        for i, item in enumerate(v):
            if not isinstance(item, str):
                raise ProgramLoadError(
                    f"program file 'self_knowledge' field {field!r} entry {i} "
                    f"is not a string (got {type(item).__name__}): refusing load")


def _validate_bimo_section(raw: Any) -> None:
    """Stage-validate a PRESENT bimo section (MEDIUM-four D).

    Raises ProgramLoadError before any state is touched. The writer
    (BIMOBody.to_dict) emits slots as a dict over the canonical
    BIMO_SLOTS roster with persona-id-or-None values, active as a
    bool, and pilot/mode as strings. An unknown slot key is a
    malformed present entry and refuses — the former restore silently
    FILTERED unknown keys, so a renamed or newer-version slot
    assignment vanished with no report — and a non-string slot value
    or pilot is type confusion the writer cannot produce. Extra
    unknown TOP-LEVEL keys are forward compatibility, not refusal.
    A field PRESENT with an explicit null is not missing (Director
    CORRECTION_REQUIRED 7136700328): the writer emits slots as an
    object, active as a bool, and pilot/mode as strings, so a present
    null in any of them refuses typed instead of receiving
    from_dict's default substitution (active -> false). Null remains
    lawful exactly where the writer emits it: a slot VALUE (an
    undocked slot), which still loads whole.
    """
    from form.dell_matrix.personas import BIMO_SLOTS
    if not isinstance(raw, dict):
        raise ProgramLoadError(
            f"program file 'bimo' section is not an object "
            f"(got {type(raw).__name__}): refusing load")
    if "slots" in raw:
        slots = raw["slots"]
        if not isinstance(slots, dict):
            raise ProgramLoadError(
                f"program file 'bimo' field 'slots' is not an object "
                f"(got {type(slots).__name__}): refusing load")
        for slot, pid in slots.items():
            if slot not in BIMO_SLOTS:
                raise ProgramLoadError(
                    f"program file 'bimo' slots key {slot!r} is not a canonical "
                    f"BIMO slot: refusing load")
            if pid is not None and not isinstance(pid, str):
                raise ProgramLoadError(
                    f"program file 'bimo' slot {slot!r} value is not a persona "
                    f"id string or null (got {type(pid).__name__}): refusing load")
    if "active" in raw:
        active = raw["active"]
        if not isinstance(active, bool):
            raise ProgramLoadError(
                f"program file 'bimo' field 'active' is not a boolean "
                f"(got {type(active).__name__}): refusing load")
    for field in ("pilot", "mode"):
        if field not in raw:
            continue
        v = raw[field]
        if not isinstance(v, str):
            raise ProgramLoadError(
                f"program file 'bimo' field {field!r} is not a string "
                f"(got {type(v).__name__}): refusing load")


def _prepare_program(owner: str, data: Dict[str, Any], _nursery=None) -> Program:
    """PREPARE a private Program from validated data. Touches no process language state.

    ``_nursery``: when provided, the Program is built against that staged
    Nursery instead of the owner's live nursery file (generation-member load).
    """
    p = open_program(owner, _nursery=_nursery)
    plane = p.cube.session.plane
    plane.units.clear()
    plane.sandboxes.clear()
    for uid, u in data.get("plane", {}).get("units", {}).items():
        try:
            skin = Skin(u.get("skin", "cube"))
        except ValueError:
            skin = Skin.CUBE
        plane.place(uid, u.get("label", uid), words=u.get("words", ""), detail=u.get("detail", "") or "", goals=list(u.get("goals") or []), skin=skin, x=float(u.get("x", 0)), y=float(u.get("y", 0)), parents=list(u.get("parents") or []), origin=str(u.get("origin") or "placed"), lineage_version=int(u.get("lineage_version") or 1), restore=True)
        unit = plane.units[uid]
        unit.sandboxed = bool(u.get("sandboxed", False))
        unit.sandbox_id = u.get("sandbox_id")
        # Track D TD-1: restore the binding pointer verbatim. Loading
        # never validates-away or rebinds it — a dangling pointer is
        # H1 state, surfaced by binding_census, refused by bind.
        unit.idea_id = u.get("idea_id")
    for sid, entry in data.get("plane", {}).get("sandboxes", {}).items():
        # Phase M: current shape is {"label": ..., "members": [...]};
        # legacy saves stored a bare member list — accept both.
        # Gate-2 (2026-11-13): provenance restores verbatim; shapes
        # without it (pre-provenance saves, legacy lists) restore as
        # unattributed ("") — fail-closed for any consumer that
        # requires positive ownership evidence, never a crash.
        if isinstance(entry, dict):
            plane.box(list(entry.get("members") or []), sid,
                      label=str(entry.get("label") or "sandbox"),
                      provenance=str(entry.get("provenance") or ""))
        else:
            plane.box(list(entry), sid)
    try:
        plane.set_perspective(Perspective(data.get("plane", {}).get("perspective", "table")))
    except Exception:
        pass
    zoom = data.get("plane", {}).get("zoom")
    if zoom:
        plane.zoom_in(zoom)
    if data.get("enhance_on"):
        p.enhance.turn_on()
    else:
        p.enhance.turn_off()
    if data.get("sandbox_on"):
        p.sandbox.turn_on()
    else:
        p.sandbox.turn_off()
    p.network_url = data.get("network_url") or ""
    try:
        from form.dell_matrix.internet_gate import InternetGate
        p.internet = InternetGate.from_dict(data.get("internet") or {})
    except Exception:
        pass
    amb = data.get("ambient", {})
    if amb.get("master_on"):
        p.ambient.turn_on()
    else:
        p.ambient.turn_off()
    for src, on in (amb.get("enabled") or {}).items():
        if on:
            p.ambient.enable_source(src)
        else:
            p.ambient.disable_source(src)
    res = data.get("resonance", {})
    st = ResonanceState(scores={k: float(v) for k, v in res.get("scores", {}).items()}, tags={k: {t: float(w) for t, w in bucket.items()} for k, bucket in res.get("tags", {}).items()})
    st.pulse_count = int(res.get("pulse_count", 0))
    p.enhance.state = st
    p.main.tags = {k: float(v) for k, v in data.get("main", {}).get("tags", {}).items()}
    p.main.contributions = []
    for c in data.get("main", {}).get("contributions", []):
        p.main.contributions.append(MainContribution(from_units=tuple(c.get("from_units", ("", ""))), labels=tuple(c.get("labels", ("", ""))), note=c.get("note", ""), weight=float(c.get("weight", 1.0)), ts=c.get("ts", "")))
    p.main.pulls = []
    for pr in data.get("main", {}).get("pulls", []):
        p.main.pulls.append(PullRecord(unit_id=pr.get("unit_id", ""), tag=pr.get("tag", ""), weight=float(pr.get("weight", 0)), ts=pr.get("ts", "")))
    target_gen = _duo_target_generation(data)
    _restore_duo_ledger(p, data, target_gen)
    _restore_avatar(p, data)
    # Nursery decisions are NOT restored from the serialized "nursery" field (kept in the file format for
    # back-compat only). p.nursery is the owner's live nursery file loaded by Program; restore never
    # creates pending/confirmed/rejected transitions and never writes any nursery file.
    _restore_lattice(p, data)
    # MEDIUM-four B: a PRESENT companion section is stage-validated whole
    # (_validate_companion_section) and refuses typed before the swap;
    # the former blanket except/pass silently substituted the constructor
    # default for the whole section on any single malformed field. An
    # ABSENT section keeps the documented constructor default.
    from form.dell_matrix.companion import AICompanion
    if "companion" in data:
        _validate_companion_section(data["companion"])
        p.companion = AICompanion.from_dict(data["companion"])
    else:
        p.companion = AICompanion.from_dict({})
    try:
        from form.dell_matrix.inspire_pack import InspireState
        p.inspire = InspireState.from_dict(data.get("inspire") or {})
    except Exception:
        pass
    # MEDIUM-four C: a PRESENT self_knowledge section is stage-validated
    # whole (_validate_self_knowledge_section) and refuses typed before
    # the swap; the former blanket except/pass silently blanked the
    # whole self-model on any single bad scalar, and list() on a string
    # inventory silently character-split it. An ABSENT section keeps
    # the documented blank model.
    from form.dell_matrix.self_model import SelfKnowledge
    if "self_knowledge" in data:
        _validate_self_knowledge_section(data["self_knowledge"])
        p.self_knowledge = SelfKnowledge.from_dict(data["self_knowledge"])
    else:
        p.self_knowledge = SelfKnowledge.from_dict({})
    ux = data.get("ux") or {}
    if ux:
        try:
            from form.dell_matrix.actions_registry import normalize_mode
            p.ux_mode = normalize_mode(ux.get("mode", "builder"))
        except Exception:
            p.ux_mode = ux.get("mode") or "builder"
        p.skin_filter = ux.get("skin_filter")
        p.persona_lens = ux.get("persona_lens")
        p.grid_snap = bool(ux.get("grid_snap", False))
        p.active_workshop = ux.get("active_workshop")
        p.click_mode = ux.get("click_mode") or "inspect"
        p.camera_follow = bool(ux.get("camera_follow", True))
        p.show_nursery_ghosts = bool(ux.get("show_nursery_ghosts", True))
        trail = ux.get("user_trail") or []
        p.user_trail = [[float(t[0]), float(t[1])] for t in trail if isinstance(t, (list, tuple)) and len(t) >= 2][-16:]
        p.active_view = ux.get("active_view") or "growth"
        p.body_style = ux.get("body_style") or "stick"
        p.auto_confirm_grow = bool(ux.get("auto_confirm_grow", False))
        # Q-LC.1: restore the undo-depth setting only when it is a
        # valid in-range integer; anything else keeps the ruled
        # default of 30 (legacy saves carry no key at all).
        try:
            _ud = int(ux.get("undo_depth", 30))
            if 1 <= _ud <= 200:
                p.undo_depth = _ud
        except (TypeError, ValueError):
            pass
    try:
        from form.dell_matrix.forces import ForceField
        p.forces = ForceField.from_dict(data.get("forces") or {})
    except Exception:
        pass
    # Phase 4: spatial authority state. Missing member -> fresh (declared,
    # pre-Phase-4 generations). Malformed member -> FAIL CLOSED (never
    # silent defaults that change meaning).
    from form.dell_matrix.spatial_authority import (
        SpatialAuthority, SpatialLoadError)
    try:
        p.spatial = SpatialAuthority.from_dict(data.get("spatial"))
    except SpatialLoadError:
        raise
    except Exception as exc:
        raise SpatialLoadError(f"spatial restore failed: {exc}")
    # MEDIUM-four D: BIMO and PersonaMatrix are staged SEPARATELY — the
    # former single try/except-pass coupled them, so one malformed bimo
    # section silently dropped BOTH the dock arrangement and the
    # PersonaMatrix rebuild (persona_matrix.active lost). A PRESENT
    # bimo section is stage-validated whole (_validate_bimo_section)
    # and refuses typed before any bound state mutates; the matrix
    # rebuild from the owner's persona lens is its own step with its
    # own failure domain and proceeds independently of the bimo
    # section's presence. An ABSENT bimo section keeps the default body.
    from form.dell_matrix.personas import BIMOBody, PersonaMatrix
    if "bimo" in data:
        _validate_bimo_section(data["bimo"])
        p.bimo = BIMOBody.from_dict(data["bimo"])
    else:
        p.bimo = BIMOBody.from_dict({})
    p.persona_matrix = PersonaMatrix(active=getattr(p, "persona_lens", None))
    # Row #155 PERSONAMATRIX: restore the user persona layer into the
    # loaded program's OWN layer (owner-scoped, Director 7069171691 —
    # never the module default layer, so loading owner B cannot clear
    # or expose owner A's personas). Absent section = legacy (no user
    # personas) — but the replaced surfaces are STILL re-bound to the
    # program's own layer in that case (the else branch below; Critic
    # Finding 1, Director ruling 7180708590). FAIL CLOSED, like the
    # spatial / agent-local sections above (except-pass finding
    # 7075379118): a present-but-malformed
    # section (not a list) or any activation / re-bind failure refuses
    # the load with PersonaLoadError — never a silent empty layer.
    # Scope A admission (_admit_custom_personas, Director 7079370876)
    # runs BEFORE activation: every record of a present list must be
    # lawful with a unique normalized id, or the load refuses with
    # the file untouched — a malformed or duplicate user-authored
    # record is never skipped-and-dropped (its bytes would be
    # destroyed by the next save) and never silently overwritten.
    # Admitted records all activate, so the report that LANDS on the
    # loaded program (p.persona_restore_report) accounts for every
    # record exactly once and user_personas mirrors the layer. The
    # BIMO / matrix surfaces replaced just above are re-bound to
    # the layer.
    from form.dell_matrix.personas import (
        PersonaLoadError, activate_custom_personas)
    if "custom_personas" in data:
        _section = data["custom_personas"]
        if not isinstance(_section, list):
            raise PersonaLoadError(
                "custom_personas section is not a list: "
                f"{type(_section).__name__}")
        _admit_custom_personas(_section)
        _player = getattr(p, "persona_layer", None)
        if _player is None:
            raise PersonaLoadError(
                "user persona restore failed: program has no persona layer")
        try:
            _report = activate_custom_personas(_section, layer=_player)
            p._bind_persona_layer()
        except PersonaLoadError:
            raise
        except Exception as exc:
            raise PersonaLoadError(f"user persona restore failed: {exc}")
        p.persona_restore_report = {
            "activated": list(_report.get("activated", [])),
            "skipped": list(_report.get("skipped", [])),
        }
        p.user_personas = _player.all()
    else:
        # Critic Finding 1 (Director ruling 7180708590): a legacy save
        # with NO custom_personas section still had its BIMO / matrix
        # surfaces replaced unconditionally above, and the re-bind to
        # the program's OWN layer used to run only inside the presence
        # block — so a legacy restore's surfaces fell back to the
        # process-default layer and could resolve (even dock) personas
        # that exist only there, while the program's own layer stayed
        # clean. The re-bind is part of surface replacement, not of
        # section admission: run it for every successful restore.
        try:
            p._bind_persona_layer()
        except Exception as exc:
            raise PersonaLoadError(f"user persona restore failed: {exc}")
    hist = data.get("history") or []
    if isinstance(hist, list):
        p.history = [str(h)[:120] for h in hist][-24:]
    # DCC-XX: restore the durable execution-outcome ledger. Records are
    # historical evidence: non-derivable, never reinterpreted, never
    # rewritten — so a PRESENT but malformed section FAILS CLOSED
    # (ProgramLoadError, raised before any swap or write), exactly as
    # the spatial and agent_local restores do (persistence-integrity,
    # Part I SAVE/JOURNAL; Director clearance PR #505 comment
    # 7076723491). An ABSENT section is a legacy save (pre-ledger
    # writer): the prepared program's empty ledger stands, as before.
    if "outcome_ledger" in data:
        from form.mandell.outcome_ledger import validate_record_shape
        ledger = data["outcome_ledger"]
        if not isinstance(ledger, dict):
            raise ProgramLoadError(
                "outcome_ledger section is not an object: "
                f"{type(ledger).__name__}; refusing load")
        seq = ledger.get("outcome_seq", 0)
        if isinstance(seq, bool) or not isinstance(seq, int):
            raise ProgramLoadError(
                "outcome_ledger.outcome_seq is not an integer: "
                f"{seq!r}; refusing load")
        # Findings A/C (Director CORRECTION_REQUIRED 7079022510):
        # identity and counter consistency are part of the malformed-
        # present contract. The ledger's sole writer (build_outcome /
        # capture_outcome, DCC-XX) always emits records owned by the
        # program owner, keyed by their own outcome_id, each with a
        # positive integer outcome_seq, under a section counter equal
        # to the highest record sequence — and no production path
        # deletes or trims records. None of the states refused below
        # is therefore legacy-producible, so each fails closed with a
        # typed refusal: no silent counter normalize, auto-advance, or
        # reset. A counter AHEAD of the records is a harmless gap and
        # is preserved verbatim (never reset downward).
        if seq < 0:
            raise ProgramLoadError(
                "outcome_ledger.outcome_seq is negative: "
                f"{seq!r}; refusing load")
        raw_records = ledger.get("records", {})
        if not isinstance(raw_records, dict):
            raise ProgramLoadError(
                "outcome_ledger.records is not an object: "
                f"{type(raw_records).__name__}; refusing load")
        restored: Dict[str, Dict[str, Any]] = {}
        max_record_seq = 0
        seen_seqs: Dict[int, str] = {}
        for oid, rec in raw_records.items():
            if not isinstance(oid, str) or not validate_record_shape(rec):
                raise ProgramLoadError(
                    f"outcome_ledger record {oid!r} fails shape "
                    "validation; refusing load")
            if rec.get("outcome_id") != oid:
                raise ProgramLoadError(
                    f"outcome_ledger record key {oid!r} does not match "
                    f"its outcome_id {rec.get('outcome_id')!r}; "
                    "refusing load")
            if rec.get("owner") != p.owner:
                raise ProgramLoadError(
                    f"outcome_ledger record {oid!r} owner "
                    f"{rec.get('owner')!r} does not match the loaded "
                    f"owner {p.owner!r}; refusing load")
            rseq = rec.get("outcome_seq")
            if (isinstance(rseq, bool) or not isinstance(rseq, int)
                    or rseq < 1):
                raise ProgramLoadError(
                    f"outcome_ledger record {oid!r} outcome_seq is "
                    f"not a positive integer: {rseq!r}; refusing load")
            # Finding D (Director 7079147473): per-record sequences
            # are unique across the ledger. The capture writer
            # advances the counter exactly once per accepted record,
            # in the same step as the append, so two different
            # outcome_ids sharing one sequence are not writer-
            # producible; left standing, the duplicate would make
            # get_outcome_by_seq select a record by dict order.
            if rseq in seen_seqs:
                raise ProgramLoadError(
                    f"outcome_ledger records {seen_seqs[rseq]!r} and "
                    f"{oid!r} share outcome_seq {rseq}; "
                    "refusing load")
            seen_seqs[rseq] = oid
            if rseq > max_record_seq:
                max_record_seq = rseq
            restored[oid] = dict(rec)
        if seq < max_record_seq:
            raise ProgramLoadError(
                "outcome_ledger.outcome_seq "
                f"{seq} is behind the records' highest sequence "
                f"{max_record_seq}; refusing load")
        p.outcome_records = restored
        p.outcome_seq = seq
    # R7.2: restore Perspective Studio session evidence with the shared
    # strict schema. Closed records only; the active studio mode is
    # session-only and never restored. validate_section never raises;
    # no broad suppression. The _MISSING sentinel distinguishes absent
    # (legacy) from explicit null (malformed). Malformed evidence is
    # preserved (in memory and through save/reload via the section's
    # "malformed" key). Retention: 10 most recent closed sessions.
    from form.dell_matrix.perspective_studio import validate_section, _MISSING
    sessions, malformed = validate_section(data.get("studio_sessions", _MISSING), p.owner)
    p.studio_sessions = sessions
    p.studio_sessions_malformed = malformed
    # R7.3: restore general workshop session evidence with the same
    # strict schema and sentinel distinction (absent = legacy, explicit
    # null = malformed). Closed records only; the active workshop mode
    # is session-only and never restored as an active session (the
    # Program's active_workshop flag has its own pre-existing restore).
    from form.dell_matrix.workshop_session import (
        validate_section as validate_workshop_section,
        _MISSING as _WS_MISSING)
    wsessions, wmalformed = validate_workshop_section(
        data.get("workshop_sessions", _WS_MISSING), p.owner)
    p.workshop_sessions = wsessions
    p.workshop_sessions_malformed = wmalformed
    # R7.4: restore onboarding session evidence (draft 7.1.4, D1/D2)
    # with the same strict schema and sentinel distinction, then apply
    # the D1 starting-level rule. Absent section = legacy (owner never
    # demoted); begun without completion = first-run on load; a valid
    # completed record graduates a persisted first-run mode to
    # beginner; section-level malformation fails closed to first-run
    # with the evidence preserved.
    from form.dell_matrix.onboarding_session import (
        validate_section as validate_onboarding_section,
        _MISSING as _OB_MISSING,
        apply_restored_level as _apply_onboarding_level,
        has_completed as _onboarding_has_completed)
    osessions, omalformed, ometa = validate_onboarding_section(
        data.get("onboarding_sessions", _OB_MISSING), p.owner)
    p.onboarding_sessions = osessions
    p.onboarding_sessions_malformed = omalformed
    p.onboarding_begun = bool(ometa.get("begun"))
    p.onboarding_completed = _onboarding_has_completed(osessions)
    _apply_onboarding_level(p, osessions, ometa)
    # R7.5: restore BIMO Forge session evidence and named configurations
    # with the same strict schema and sentinel distinction (absent =
    # legacy, explicit null = malformed). The active forge session is
    # session-only and never restored. Configurations are validated
    # against the canonical slot roster and persona registry here, so a
    # hand-edited configuration can never apply unknown state.
    from form.dell_matrix.bimo_forge import (
        validate_sessions_section as validate_forge_section,
        validate_configurations_section as validate_configurations_section,
        _MISSING as _FG_MISSING)
    fsessions, fmalformed = validate_forge_section(
        data.get("forge_sessions", _FG_MISSING), p.owner)
    p.forge_sessions = fsessions
    p.forge_sessions_malformed = fmalformed
    configs, cmalformed = validate_configurations_section(
        data.get("bimo_configurations", _FG_MISSING), p.owner,
        layer=getattr(p, "persona_layer", None))
    p.bimo_configurations = configs
    p.bimo_configurations_malformed = cmalformed
    # R7.6: restore Connected World session evidence with the same
    # strict schema and sentinel distinction (absent = legacy,
    # explicit null = malformed). The active connect session and its
    # provider selection are session-only and never restored.
    from form.dell_matrix.connection_session import (
        validate_section as validate_connection_section,
        _MISSING as _CN_MISSING)
    csessions, cmalformed2 = validate_connection_section(
        data.get("connection_sessions", _CN_MISSING), p.owner)
    p.connection_sessions = csessions
    p.connection_sessions_malformed = cmalformed2
    # SD-1: restore dock session evidence with the same strict
    # schema and sentinel distinction (absent = legacy, explicit
    # null = malformed). Live DockedSession handles are runtime-only
    # and never restored; the evidence records are.
    from form.dell_matrix.dock_session import (
        validate_section as validate_dock_section,
        _MISSING as _DS_MISSING)
    dsessions, dmalformed = validate_dock_section(
        data.get("dock_sessions", _DS_MISSING), p.owner)
    p.dock_sessions = dsessions
    p.dock_sessions_malformed = dmalformed
    # SD-4: restore Director records (recommendations and
    # refusals — records only, never decisions).
    from form.dell_matrix.director_records import (
        validate_section as validate_director_section,
        _MISSING as _DR_MISSING)
    drecords, drmalformed = validate_director_section(
        data.get("director_records", _DR_MISSING), p.owner)
    p.director_records = drecords
    p.director_records_malformed = drmalformed
    # PP3: restore the unknowns register.
    from form.dell_matrix.unknowns import (
        validate_section as validate_unknowns_section,
        _MISSING as _UNK_MISSING)
    unk_entries, unk_malformed = validate_unknowns_section(
        data.get("unknowns", _UNK_MISSING), p.owner)
    p.unknowns = unk_entries
    p.unknowns_malformed = unk_malformed
    # SD-5: restore the inside-out loop ledger.
    from form.dell_matrix.design_loop import (
        validate_section as validate_design_loop_section,
        _MISSING as _DL_MISSING)
    dlevents, dlmalformed = validate_design_loop_section(
        data.get("design_loop", _DL_MISSING), p.owner)
    p.design_loop = dlevents
    p.design_loop_malformed = dlmalformed
    # P9: restore Exchange receipts recorded against proposals.
    from form.dell_matrix.exchange import (
        validate_receipts_section, _MISSING as _EX_MISSING)
    exentries, exmalformed = validate_receipts_section(
        data.get("exchange_receipts", _EX_MISSING), p.owner)
    p.exchange_receipts = exentries
    p.exchange_receipts_malformed = exmalformed
    # Completion-order residual repair: restore imported seed
    # payloads (originals that export must reproduce exactly).
    from form.dell_matrix.exchange import (
        validate_seeds_section as validate_exchange_seeds_section)
    xsentries, xsmalformed = validate_exchange_seeds_section(
        data.get("exchange_seeds", _EX_MISSING), p.owner)
    p.exchange_seeds = xsentries
    p.exchange_seeds_malformed = xsmalformed
    # PP2b (charter ruling B2): restore the eviction totals for
    # the counted sections: the total stored in the section,
    # plus any records the load-side retention just evicted (a
    # file written before counting existed can hold more valid
    # records than the bound; those drops are real evictions,
    # counted here once — the next save persists the total and
    # the trimmed population, so they are never recounted). A
    # section whose shell failed validation is preserved as
    # malformed evidence, not evicted, and counts nothing.
    from form.persist import _counted_sections as _counted
    from form.dell_matrix.session_section import (
        collect_valid as _collect_valid)
    _malformed_by_attr = {
        "dock_sessions": dmalformed,
        "director_records": drmalformed,
        "unknowns": unk_malformed,
        "design_loop": dlmalformed,
        "exchange_receipts": exmalformed,
        "exchange_seeds": xsmalformed,
    }
    for _key, _attr, _id_field, _sort, _max_keep, _vrec in \
            _counted(p.owner):
        _raw = data.get(_key)
        _stored = 0
        _load_drops = 0
        if isinstance(_raw, dict):
            _dt = _raw.get("dropped_total")
            if isinstance(_dt, int) and not isinstance(_dt, bool) \
                    and _dt >= 0:
                _stored = _dt
            _records = _raw.get(
                "sessions" if _key == "dock_sessions" else "entries")
            _shell_failed = "_section" in (
                _malformed_by_attr.get(_attr) or {})
            if isinstance(_records, dict) and not _shell_failed:
                _pre = _collect_valid(
                    _records, _vrec, _id_field, {},
                    key_not_string="entry key not a string",
                    mismatch="entry key/ID mismatch")
                _kept = len(getattr(p, _attr, None) or {})
                _load_drops = max(0, len(_pre) - _kept)
        setattr(p, _attr + "_dropped_total", _stored + _load_drops)
    # TPP-I: Restore lifecycle presence metadata (NBD-Ω-048).
    try:
        lc_data = data.get("lifecycle")
        if isinstance(lc_data, dict):
            p.lifecycle = {str(k): dict(v) for k, v in lc_data.items() if isinstance(v, dict)}
        else:
            p.lifecycle = {}
    except Exception:
        p.lifecycle = {}
    # R6.4: restore agent-local behavioral state (IntrinsicAgent).
    # Directive §4: a sentinel distinguishes genuine absence (section
    # missing -> fresh default, pre-R6.4 generations) from explicit null
    # (section present with null -> fail closed). The outer
    # agent_local_version is validated strictly, as are inner record
    # versions. Malformed -> FAIL CLOSED (AgentLocalLoadError);
    # malformed is not absence.
    try:
        from form.dell_matrix.intrinsic_agent import (
            IntrinsicAgent, AgentLocalLoadError)
        _ABSENT = object()
        al = data.get("agent_local", _ABSENT)
        if al is _ABSENT:
            p.agent_local_states = {}
        elif al is None:
            raise AgentLocalLoadError(
                "agent_local section: explicit null is malformed, not absence")
        elif not isinstance(al, dict):
            raise AgentLocalLoadError("agent_local section is not a dict")
        else:
            # Outer version: strict int, must match. Explicit null or
            # missing version on a present section is malformed.
            outer_v = al.get("agent_local_version", _ABSENT)
            if outer_v is _ABSENT or outer_v is None:
                raise AgentLocalLoadError(
                    "agent_local.agent_local_version: missing or null")
            if isinstance(outer_v, bool) or not isinstance(outer_v, int):
                raise AgentLocalLoadError(
                    "agent_local.agent_local_version: expected int, "
                    f"got {type(outer_v).__name__}")
            from form.dell_matrix.intrinsic_agent import AGENT_LOCAL_VERSION
            if outer_v != AGENT_LOCAL_VERSION:
                raise AgentLocalLoadError(
                    f"unsupported agent_local_version: {outer_v}")
            agents = al.get("agents", _ABSENT)
            if agents is _ABSENT:
                agents = {}
            elif agents is None:
                raise AgentLocalLoadError(
                    "agent_local.agents: explicit null is malformed")
            if not isinstance(agents, dict):
                raise AgentLocalLoadError("agent_local.agents is not a dict")
            states: Dict[str, Dict[str, Any]] = {}
            for subject, raw in agents.items():
                if not isinstance(subject, str):
                    raise AgentLocalLoadError(
                        "agent-local subject key is not str")
                if raw is None:
                    raise AgentLocalLoadError(
                        f"agent-local state for {subject!r}: explicit null "
                        "is malformed, not absence")
                # from_dict validates; stored null is malformed, not absence.
                states[subject] = IntrinsicAgent.from_dict(raw, subject).to_dict()
            p.agent_local_states = states
        p.agent_local_agents = {}
    except AgentLocalLoadError:
        raise
    except Exception as exc:
        raise AgentLocalLoadError(f"agent-local restore failed: {exc}")
    # R6.4: restore agent-action audit records. Shape-checked; valid
    # records restored. Directive §5: malformed records are NOT silently
    # dropped and their original bytes are NOT discarded. The COMPLETE
    # original malformed record is preserved in program.agent_audit_malformed
    # (through the existing agent_audit payload section — no parallel
    # store), so a subsequent save cannot silently overwrite the evidence.
    # A note is not a backup.
    try:
        import copy as _copy
        _ABSENT2 = object()
        aa = data.get("agent_audit", _ABSENT2)
        if aa is _ABSENT2:
            p.agent_audit_records = {}
            p.agent_audit_seq = 0
            p.agent_audit_malformed = []
        elif aa is None:
            p.agent_audit_records = {}
            p.agent_audit_seq = 0
            p.agent_audit_malformed = [{
                "note": "agent_audit section: explicit null is malformed",
                "original": None,
            }]
        elif not isinstance(aa, dict):
            p.agent_audit_records = {}
            p.agent_audit_seq = 0
            p.agent_audit_malformed = [{
                "note": "agent_audit section is not a dict",
                "type": type(aa).__name__,
                "original": _copy.deepcopy(aa),
            }]
        else:
            seq = aa.get("audit_seq", 0)
            try:
                if isinstance(seq, bool):
                    raise TypeError("bool")
                p.agent_audit_seq = max(0, int(seq))
            except (TypeError, ValueError):
                p.agent_audit_seq = 0
            # Previously preserved malformed evidence (complete originals)
            # is restored first; it is not re-validated or "fixed".
            preserved = aa.get("malformed", _ABSENT2)
            malformed: List[Dict[str, Any]] = []
            if preserved is _ABSENT2 or preserved is None:
                pass
            elif isinstance(preserved, list):
                for entry in preserved:
                    malformed.append(_copy.deepcopy(entry)
                                     if isinstance(entry, dict)
                                     else {"note": "malformed entry not a dict",
                                           "original": _copy.deepcopy(entry)})
            else:
                malformed.append({
                    "note": "agent_audit.malformed is not a list",
                    "type": type(preserved).__name__,
                    "original": _copy.deepcopy(preserved),
                })
            raw_audit = aa.get("records")
            if raw_audit is None:
                raw_audit = {}
            restored_audit: Dict[str, Dict[str, Any]] = {}
            if isinstance(raw_audit, dict):
                for aid, rec in raw_audit.items():
                    if (isinstance(aid, str) and isinstance(rec, dict)
                            and rec.get("audit_id") == aid):
                        restored_audit[aid] = dict(rec)
                    else:
                        malformed.append({
                            "audit_id": aid if isinstance(aid, str) else None,
                            "note": "record failed shape check",
                            "record_type": type(rec).__name__,
                            "original": _copy.deepcopy(rec),
                        })
            else:
                malformed.append({
                    "note": "agent_audit.records is not a dict",
                    "type": type(raw_audit).__name__,
                    "original": _copy.deepcopy(raw_audit),
                })
            p.agent_audit_records = restored_audit
            p.agent_audit_malformed = malformed
            max_aseq = p.agent_audit_seq
            for rec in restored_audit.values():
                try:
                    s = int(rec.get("audit_seq", 0) or 0)
                except (TypeError, ValueError):
                    s = 0
                if s > max_aseq:
                    max_aseq = s
            p.agent_audit_seq = max_aseq
    except Exception:
        p.agent_audit_records = {}
        p.agent_audit_seq = 0
        p.agent_audit_malformed = [{"note": "agent_audit restore raised",
                                    "original": None}]
    restore_core_ii(p, data)
    return p


DURABLE_KEYS = (
    "type", "version", "level", "floor", "owner",
    "enhance_on", "sandbox_on", "network_url", "internet", "ambient",
    "resonance", "main", "plane", "duo_generation", "duo_ledger", "avatar",
    "companion", "inspire", "self_knowledge", "ux", "forces", "bimo",
    "nursery", "lattice", "history", "latinmandell_customs",
    "mandell_language", "core_ii", "outcome_ledger", "spatial",
    "lifecycle", "agent_local", "agent_audit", "studio_sessions",
    "workshop_sessions", "onboarding_sessions", "forge_sessions",
    "bimo_configurations", "connection_sessions", "dock_sessions",
    "director_records", "design_loop",
    "director_records", "exchange_receipts", "unknowns",
    "exchange_seeds",
)


def durable(data: Dict[str, Any]) -> Dict[str, Any]:
    return {k: data.get(k) for k in DURABLE_KEYS}


def smoke() -> bool:
    print("=== PERSIST v7 SESSION SMOKE ===")
    r = []
    def rec(name, ok, detail=""):
        print(f"[{len(r)+1}] {name}: {'PASS' if ok else 'FAIL'}" + (f" | {detail}" if detail else ""))
        r.append(bool(ok))
    from form.mandell.latinmandell import customize, root_of, clear_customs as cc
    from form.mandell.seed import CELLS, define_cell, expand_cell
    from form.avatar import Expression
    p = open_program("PersistV7")
    bind(p)  # owner-bound language: edits below belong to PersistV7, whatever owner was bound before
    cc()
    p.place("biz", "Business", words="CRM", detail="field ops", goals=["reliability"], skin=Skin.BUILDING, x=1)
    p.avatar.step(3)
    p.face.set(Expression.JOY)
    p.lattice.to_sphere()
    customize("lumen", dell=9, term="Show", sense="light made visible", la="lumen")
    define_cell("PersistCell", "08[Create] :: persist-cell")
    path = save(p)
    rec("save file", os.path.isfile(path))
    cc()
    CELLS.clear()
    p2 = load("PersistV7")
    rec("units", "biz" in p2.cube.session.plane.units)
    u = p2.cube.session.plane.units["biz"]
    rec("detail", getattr(u, "detail", "") == "field ops")
    rec("goals", list(getattr(u, "goals", [])) == ["reliability"])
    rec("latinmandell custom", root_of("lumen") is not None and root_of("lumen").get("custom") is True)
    rec("avatar nondefault", p2.face.current == Expression.JOY)
    rec("lattice nondefault", p2.lattice.perception.form.value == "sphere")
    rec("mandell language cells", "PersistCell" in CELLS and expand_cell("PersistCell").ok)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    rec("version 7", data.get("version") == 7)
    rec("unit has detail key", "detail" in data.get("plane", {}).get("units", {}).get("biz", {}))
    rec("mandell_language key", isinstance(data.get("mandell_language"), dict))
    rec("serialize load domain parity", set(DURABLE_KEYS) <= set(data.keys()))
    cc()
    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


USAGE = "usage: python -m form.persist --smoke   (persist v7 session smoke; the module is otherwise a library)"


def main(argv: Optional[List[str]] = None) -> int:
    """Explicit module entry: `--smoke` runs the smoke (exit 0/1); no argument prints usage (exit 0, no work);
    anything else is a usage error (exit 2)."""
    args = list(sys.argv[1:] if argv is None else argv)
    if args == ["--smoke"]:
        return 0 if smoke() else 1
    if not args:
        print(USAGE)
        return 0
    print(f"{USAGE}\nerror: unrecognized arguments: {' '.join(args)}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
