#!/usr/bin/env python3
"""DCC-XVIII: Coherent checkpoint generations + cross-file recovery.

Checkpoint Generation V1 -- the layer ABOVE Persistence V2 file atomicity.

DCC-XVII guarantees each canonical file is old-complete or new-complete.
It does NOT guarantee that the files constituting one logical DellMatrix
state belong to the same committed generation (nursery G2 + program G1 is
two perfect files describing contradictory logical state).

This module provides the smallest safe generation protocol:

    IMMUTABLE GENERATION MEMBERS + ATOMIC MANIFEST POINTER

Commit model (conceptual):

    1. save the live nursery + live program (Persistence V2 each)
    2. write generation-specific member COPIES (byte-exact, immutable)
    3. validate member fingerprints
    4. write the generation manifest (V2 atomic)
    5. atomically replace the canonical CURRENT pointer  <- commit boundary
    6. best-effort directory fsync (inherited from Persistence V2)

A crash before the pointer swap leaves the previous committed generation
authoritative; a crash after exposes the new complete generation. Member
files are never overwritten after sealing, so rollback is always possible
until the next commit. Loading never constructs a hybrid from
independently valid but generation-mismatched files.

Generation artifact filenames carry a collision-safe owner namespace
(``safe_owner`` + sha256 prefix of the exact owner bytes), so raw owners
that normalize to the same safe name can never overwrite each other's
generations; the manifest and pointer additionally validate the exact
owner on read.

Authoritative member set (Phase A discovery): the live logical state is the
JOIN of ``nursery_<owner>.json`` (proposal decisions, revision lifecycle,
lineage source) and ``program_<owner>.json`` (plane membership, session
state). Neither is reconstructible from the other: the plane carries
positions/skins/sandboxes/perspectives absent from the nursery, and the
nursery carries proposal statuses/lifecycle absent from the program file
(the program file's ``nursery`` field is back-compat only and is never
restored). Checkpoint snapshots and the legacy ``_cp_latest`` pointer are
independent/explicit-rollback artifacts and are OUT_OF_SCOPE.

What this is NOT: database ACID, distributed transactions, consensus,
multi-host coordination, or power-loss immunity beyond the documented
Persistence V2 fsync assumptions. Generation IDs are uuid4-based (unique,
stable); wall-clock time is never used for uniqueness or recovery order --
the committed generation is whatever the CURRENT pointer names.

AUTONOMY = NO.
"""
from __future__ import annotations

import hashlib
import json
import os
import uuid
from typing import Any, Dict, Optional, Tuple

from form.persist import _STATE_DIR, _safe_owner
from form.persist_rest import ProgramLoadError, _load_impl, save as persist_save
from form.dell_matrix.atomic_write import AtomicWriteError, atomic_write_bytes, atomic_write_json
from form.dell_matrix.nursery import Nursery, NurseryLoadError, owner_nursery_path

CHECKPOINT_PROTOCOL_VERSION = 1

_MEMBER_KINDS = ("nursery", "program", "ideas")


class CheckpointError(Exception):
    """Base for all Checkpoint Generation V1 failures."""


class CheckpointNotEstablished(CheckpointError):
    """No committed generation exists for this owner.

    Legacy behavior applies: use the existing legacy loader
    (persist_rest.load); the next successful commit_checkpoint establishes
    Generation V1. Nothing is migrated on read.
    """


class CheckpointCommitError(CheckpointError):
    """A checkpoint commit failed before the commit boundary."""


class CheckpointLoadError(CheckpointError):
    """A committed generation cannot be loaded honestly (explicit failure)."""


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

def _owner_ns(owner: str) -> str:
    """Collision-safe generation namespace for ``owner``.

    Different raw owners can normalize to the same ``_safe_owner`` value
    (e.g. ``"a/b"`` and ``"a_b"``); the sha256 prefix of the EXACT owner
    bytes disambiguates the generation namespace so one owner's generation
    artifacts can never overwrite another's. Manifest and pointer already
    validate the exact owner on read; collision-safe filenames prevent the
    overwrite from ever happening.
    """
    return f"{_safe_owner(owner)}.{hashlib.sha256(owner.encode('utf-8')).hexdigest()[:12]}"


def _pointer_path(owner: str) -> str:
    return os.path.join(_STATE_DIR, f"current_{_owner_ns(owner)}.json")


def _manifest_path(owner: str, generation_id: str) -> str:
    return os.path.join(_STATE_DIR, f"gen_{_owner_ns(owner)}_{generation_id}.json")


def _member_path(owner: str, kind: str, generation_id: str) -> str:
    return os.path.join(_STATE_DIR, f"{kind}_{_owner_ns(owner)}.g_{generation_id}.json")


def has_checkpoint(owner: str) -> bool:
    """True when a CURRENT pointer names a committed generation for owner."""
    return os.path.isfile(_pointer_path(owner))


# ---------------------------------------------------------------------------
# Small primitives
# ---------------------------------------------------------------------------

def _new_generation_id() -> str:
    # Uniqueness from uuid4; stability from being written into the manifest,
    # the pointer and the member filenames. Wall-clock time is NOT used.
    return "g" + uuid.uuid4().hex[:16]


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _read_json_file(path: str, what: str) -> Dict[str, Any]:
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as exc:
        raise CheckpointLoadError(f"{what} unreadable ({os.path.basename(path)}): {exc}") from exc
    if not isinstance(data, dict):
        raise CheckpointLoadError(f"{what} is not a JSON object ({os.path.basename(path)}): refusing load")
    return data


def _check_fail(stage: str, fail_at: Optional[str]) -> None:
    if fail_at == stage:
        raise CheckpointCommitError(f"injected commit failure at stage {stage!r} (commit boundary not reached)")
    if fail_at == "crash_" + stage:
        # Literal process death at the stage boundary (mirrors the
        # Persistence V2 crash injection pattern); never returns.
        os._exit(42)  # noqa: SIO171 - intentional literal crash for tests


# ---------------------------------------------------------------------------
# Commit
# ---------------------------------------------------------------------------

def _seal_members(program, generation_id: str, _fail_at: Optional[str] = None) -> Dict[str, Any]:
    """Stages 1-4: save live files, copy+verify members, write manifest.

    Returns the sealed descriptor. Does NOT touch the CURRENT pointer, so a
    crash anywhere in here leaves the previous committed generation
    authoritative and the new member files stale-but-inert.
    """
    owner = program.owner
    _check_fail("save_nursery", _fail_at)
    try:
        program.nursery.save()
    except Exception as exc:
        raise CheckpointCommitError(f"nursery save failed; commit aborted: {exc}") from exc
    _check_fail("save_program", _fail_at)
    try:
        persist_save(program)
    except Exception as exc:
        raise CheckpointCommitError(f"program save failed; commit aborted: {exc}") from exc

    # MF-5: Snapshot ideas before sealing. The snapshot file becomes
    # a checkpoint member, integrated with the journaled transaction.
    from form.mandell.idea_checkpoint import snapshot_ideas, ideas_snapshot_path
    try:
        snapshot_ideas(owner)
    except Exception as exc:
        raise CheckpointCommitError(f"idea snapshot failed; commit aborted: {exc}") from exc

    live = {
        "nursery": owner_nursery_path(owner),
        "program": os.path.join(_STATE_DIR, f"program_{_safe_owner(owner)}.json"),
        "ideas": ideas_snapshot_path(owner),
    }
    _check_fail("before_members", _fail_at)  # crash here: no G2 member file exists
    fps: Dict[str, str] = {}
    for kind in _MEMBER_KINDS:
        if not os.path.isfile(live[kind]):
            raise CheckpointCommitError(f"live {kind} file missing after save; commit aborted")
        with open(live[kind], "rb") as f:
            blob = f.read()
        fps[kind] = hashlib.sha256(blob).hexdigest()
        _check_fail(f"member_{kind}", _fail_at)
        try:
            atomic_write_bytes(_member_path(owner, kind, generation_id), blob)
        except AtomicWriteError as exc:
            raise CheckpointCommitError(f"member copy failed for {kind}; commit aborted: {exc}") from exc
        # Fingerprint validation: the sealed bytes are exactly what we sealed.
        if _sha256_file(_member_path(owner, kind, generation_id)) != fps[kind]:
            raise CheckpointCommitError(f"member fingerprint mismatch after write for {kind}; commit aborted")

    try:
        prev_pointer = _read_pointer(owner)
        previous_generation_id = prev_pointer.get("generation_id")
    except CheckpointNotEstablished:
        previous_generation_id = None

    manifest = {
        "checkpoint_protocol_version": CHECKPOINT_PROTOCOL_VERSION,
        "generation_id": generation_id,
        "previous_generation_id": previous_generation_id,
        "owner": owner,
        "members": {
            kind: {
                "file": os.path.basename(_member_path(owner, kind, generation_id)),
                "sha256": fps[kind],
            }
            for kind in _MEMBER_KINDS
        },
        "committed": True,
    }
    _check_fail("manifest", _fail_at)
    try:
        atomic_write_json(_manifest_path(owner, generation_id), manifest)
    except AtomicWriteError as exc:
        raise CheckpointCommitError(f"manifest write failed; commit aborted: {exc}") from exc
    _check_fail("after_members", _fail_at)  # crash here: members+manifest sealed, pointer still old
    return {
        "generation_id": generation_id,
        "previous_generation_id": previous_generation_id,
        "members": manifest["members"],
        "manifest_path": _manifest_path(owner, generation_id),
    }


def _commit_pointer(owner: str, sealed: Dict[str, Any], _fail_at: Optional[str] = None) -> Dict[str, Any]:
    """Stage 5: atomically replace the CURRENT pointer -- the commit boundary."""
    _check_fail("pointer", _fail_at)
    pointer = {
        "checkpoint_protocol_version": CHECKPOINT_PROTOCOL_VERSION,
        "generation_id": sealed["generation_id"],
        "previous_generation_id": sealed["previous_generation_id"],
        "owner": owner,
    }
    try:
        atomic_write_json(_pointer_path(owner), pointer)
    except AtomicWriteError as exc:
        raise CheckpointCommitError(f"pointer commit failed: {exc}") from exc
    return pointer


def _retain_current_and_previous(owner: str) -> Dict[str, Any]:
    """Conservative retention: keep current + previous committed generations.

    Deletes older committed generations and uncommitted stale generation
    artifacts for this owner. Never deletes the generation named by the
    CURRENT pointer; if the pointer cannot be read honestly, deletes nothing.
    """
    removed = 0
    try:
        pointer = _read_pointer(owner)
    except CheckpointError:
        return {"kept": [], "removed": 0, "note": "pointer unreadable; nothing deleted"}
    keep = {pointer["generation_id"]}
    if pointer.get("previous_generation_id"):
        keep.add(pointer["previous_generation_id"])
    ns = _owner_ns(owner)
    manifest_prefix = f"gen_{ns}_"
    member_infix = f"_{ns}.g_"
    try:
        names = os.listdir(_STATE_DIR)
    except OSError:
        return {"kept": sorted(keep), "removed": 0}
    for name in names:
        gen_id = None
        if name.startswith(manifest_prefix) and name.endswith(".json"):
            gen_id = name[len(manifest_prefix):-len(".json")]
        elif member_infix in name and name.endswith(".json"):
            gen_id = name.split(member_infix, 1)[1][:-len(".json")]
        if gen_id is None or gen_id in keep:
            continue
        try:
            os.unlink(os.path.join(_STATE_DIR, name))
            removed += 1
        except OSError:
            pass
    return {"kept": sorted(keep), "removed": removed}


def commit_checkpoint(program, generation_id: Optional[str] = None,
                      _fail_at: Optional[str] = None) -> Dict[str, Any]:
    """Seal the program's current logical state as one coherent generation.

    Saves the live nursery + program (Persistence V2), seals byte-exact
    immutable member copies, validates fingerprints, writes the manifest,
    then atomically swaps the CURRENT pointer (the commit boundary).
    Returns the checkpoint receipt (Phase H). Any failure before the
    pointer swap raises CheckpointCommitError and leaves the previous
    committed generation authoritative.
    """
    owner = program.owner
    gen_id = generation_id or _new_generation_id()
    sealed = _seal_members(program, gen_id, _fail_at=_fail_at)
    _commit_pointer(owner, sealed, _fail_at=_fail_at)
    _check_fail("after_commit", _fail_at)  # crash here: new generation committed
    retention = _retain_current_and_previous(owner)
    return {
        "checkpoint_protocol_version": CHECKPOINT_PROTOCOL_VERSION,
        "generation_id": gen_id,
        "previous_generation_id": sealed["previous_generation_id"],
        "owner": owner,
        "members": sealed["members"],
        "committed": True,
        "retention": retention,
    }


# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------

def _read_pointer(owner: str) -> Dict[str, Any]:
    path = _pointer_path(owner)
    if not os.path.isfile(path):
        raise CheckpointNotEstablished(
            f"no committed checkpoint generation for owner {owner!r}; legacy load path applies"
        )
    data = _read_json_file(path, "committed CURRENT pointer")
    if (
        data.get("checkpoint_protocol_version") != CHECKPOINT_PROTOCOL_VERSION
        or not isinstance(data.get("generation_id"), str)
        or not data["generation_id"]
    ):
        raise CheckpointLoadError("committed CURRENT pointer corrupt: refusing load (never guessing)")
    if data.get("owner") != owner:
        raise CheckpointLoadError("committed CURRENT pointer owner mismatch: refusing load")
    return data


def current_generation_id(owner: str) -> Optional[str]:
    """Best-effort committed generation ID for an owner (epoch context).

    Returns the generation_id from the committed CURRENT pointer, or
    None when no checkpoint is established. Used by DCC-XX as epoch
    context on outcome records — never as identity input, never raising.
    """
    try:
        return _read_pointer(owner).get("generation_id")
    except Exception:
        return None


def _read_manifest(owner: str, generation_id: str) -> Dict[str, Any]:
    data = _read_json_file(_manifest_path(owner, generation_id), "generation manifest")
    if data.get("checkpoint_protocol_version") != CHECKPOINT_PROTOCOL_VERSION:
        raise CheckpointLoadError(f"manifest protocol version unsupported for {generation_id}: refusing load")
    if data.get("generation_id") != generation_id:
        raise CheckpointLoadError(f"manifest generation identity mismatch for {generation_id}: refusing load")
    if data.get("committed") is not True:
        raise CheckpointLoadError(f"manifest for {generation_id} is not marked committed: refusing load")
    if data.get("owner") != owner:
        raise CheckpointLoadError(f"manifest owner mismatch for {generation_id}: refusing load")
    members = data.get("members")
    if not isinstance(members, dict):
        raise CheckpointLoadError(f"manifest members invalid for {generation_id}: refusing load")
    for kind in _MEMBER_KINDS:
        spec = members.get(kind)
        if not isinstance(spec, dict):
            raise CheckpointLoadError(f"manifest member {kind!r} missing for {generation_id}: refusing load")
        fp = spec.get("sha256")
        if not isinstance(fp, str) or len(fp) != 64 or any(c not in "0123456789abcdef" for c in fp):
            raise CheckpointLoadError(f"manifest fingerprint invalid for {kind!r}: refusing load")
        expected = os.path.basename(_member_path(owner, kind, generation_id))
        if spec.get("file") != expected:
            raise CheckpointLoadError(
                f"manifest member identity mismatch for {kind!r}: refusing load"
            )
    return data


def _load_generation(owner: str, generation_id: str,
                     activate: bool, recovered_from: Optional[str]) -> Tuple[Any, Dict[str, Any]]:
    """Load one generation: locate > validate > stage privately > return.

    Any failure before the staged program is fully built raises
    CheckpointLoadError and leaves live in-memory state unchanged.
    """
    manifest = _read_manifest(owner, generation_id)
    member_paths = {}
    for kind in _MEMBER_KINDS:
        spec = manifest["members"][kind]
        mpath = os.path.join(_STATE_DIR, spec["file"])
        if not os.path.isfile(mpath):
            raise CheckpointLoadError(
                f"committed manifest references absent member {kind!r} "
                f"for generation {generation_id}: refusing to mix generations"
            )
        if _sha256_file(mpath) != spec["sha256"]:
            raise CheckpointLoadError(
                f"member fingerprint mismatch for {kind!r} "
                f"in generation {generation_id}: refusing to mix generations"
            )
        member_paths[kind] = mpath
    try:
        nursery = Nursery.load(member_paths["nursery"])
    except NurseryLoadError as exc:
        raise CheckpointLoadError(
            f"committed nursery member failed validation for {generation_id}: {exc}"
        ) from exc
    try:
        program = _load_impl(owner, member_paths["program"], nursery, activate)
    except (ProgramLoadError, NurseryLoadError, ValueError, RuntimeError, OSError) as exc:
        # OSError covers TOCTOU read failures between fingerprint validation
        # and parse; they become honest load failures, never ambiguous ones.
        raise CheckpointLoadError(
            f"committed program member failed validation for {generation_id}: {exc}"
        ) from exc
    receipt = {
        "checkpoint_protocol_version": CHECKPOINT_PROTOCOL_VERSION,
        "generation_id": generation_id,
        "previous_generation_id": manifest.get("previous_generation_id"),
        "owner": owner,
        "members": manifest["members"],
        "committed": True,
        "recovered_from": recovered_from,
        "legacy": False,
    }
    return program, receipt


def load_checkpoint(owner: str, activate: bool = False) -> Tuple[Any, Dict[str, Any]]:
    """Load the committed checkpoint generation for ``owner``.

    Loader contract (Phase F):
      1. locate the committed generation via the CURRENT pointer
         (absent pointer -> CheckpointNotEstablished: legacy path applies)
      2. validate the manifest (protocol, identity, committed, owner)
      3. validate every required member's identity + sha256 fingerprint
      4. parse all members through the existing staged loaders
      5. build the private staged Program (never touches live state)
      6. only then return it with the checkpoint receipt

    Recovery policy (Control T): if the committed generation is invalid but
    names a previous committed generation, the previous generation is
    verified (manifest + every required member) and loaded instead; the
    receipt records ``recovered_from``. If no usable previous generation
    exists, raises CheckpointLoadError explicitly. Recovery is deterministic:
    it follows the manifest's ``previous_generation_id`` link, never
    timestamps or directory listings.
    """
    pointer = _read_pointer(owner)
    generation_id = pointer["generation_id"]
    try:
        return _load_generation(owner, generation_id, activate, recovered_from=None)
    except CheckpointLoadError as exc:
        previous = pointer.get("previous_generation_id")
        if not previous:
            raise
        try:
            return _load_generation(owner, previous, activate, recovered_from=generation_id)
        except CheckpointLoadError as prev_exc:
            raise CheckpointLoadError(
                f"committed generation {generation_id} invalid ({exc}); "
                f"previous generation {previous} also invalid ({prev_exc}): refusing load"
            ) from prev_exc
