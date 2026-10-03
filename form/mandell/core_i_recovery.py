#!/usr/bin/env python3
"""Core I 27/28 program checkpoints. Distinct from Core II 93-96 transactions.

PAC-I authority law: Dell 27/28 delegate to the canonical checkpoint
authority — Checkpoint Generation V1 (form.mandell.checkpoint_generation),
which seals nursery + program members under Persistence V2 atomic writes and
commits via the atomic CURRENT pointer.

    Dell 27 > canonical checkpoint operation > Persistence V2 >
    Checkpoint Generation V1 > atomic durable generation

Legacy timestamp-file checkpoints (program_<owner>_cp_<stamp>.json +
*_cp_latest.json) remain READABLE (LEGACY_COMPAT) but are never written by
this module. AUTHORITY SINGULARITY: one durable state path.
"""
from __future__ import annotations

from typing import Dict, List, Optional
import json
import os

from form.persist import _STATE_DIR, _safe_owner, load


def _gen_id_from_stamp(stamp: Optional[str]) -> str:
    """Map a caller stamp into the generation-id namespace, or mint a fresh id."""
    from form.mandell.checkpoint_generation import _new_generation_id
    if stamp:
        safe = "".join(c if c.isalnum() else "_" for c in str(stamp))[:32]
        if safe:
            return safe
    return _new_generation_id()


def checkpoint(program, stamp: Optional[str] = None) -> str:
    """Seal the program's current logical state as one coherent generation.

    Delegates to Checkpoint Generation V1. Returns the committed generation id
    (observable generation identity). Raises CheckpointCommitError on failure;
    a failure before the CURRENT pointer swap leaves the previous committed
    generation authoritative — never a partial state.
    """
    from form.mandell import checkpoint_generation as gen
    owner = program.owner
    gen_id = _gen_id_from_stamp(stamp)
    # Collision guard: a caller-supplied stamp that already names a committed
    # generation must not silently alias it — mint a fresh id instead.
    try:
        gen._read_manifest(owner, gen_id)
        gen_id = gen._new_generation_id()
    except Exception:
        pass
    receipt = gen.commit_checkpoint(program, generation_id=gen_id)
    committed = receipt["generation_id"]
    program.last_checkpoint = committed
    return committed


def _legacy_list(owner: str) -> List[str]:
    prefix = f"program_{_safe_owner(owner)}_cp_"
    if not os.path.isdir(_STATE_DIR):
        return []
    return [
        os.path.join(_STATE_DIR, name)
        for name in sorted(os.listdir(_STATE_DIR))
        if name.startswith(prefix) and name.endswith(".json") and not name.endswith("_cp_latest.json")
    ]


def list_checkpoints(owner: str) -> List[Dict[str, str]]:
    """All known checkpoints: committed generations first, then legacy files.

    Each entry: {"kind": "generation"|"legacy", "id": <gen id or path>,
    "path": <manifest path or file path>}.
    """
    from form.mandell import checkpoint_generation as gen
    out: List[Dict[str, str]] = []
    try:
        pointer = gen._read_pointer(owner)
        seen = []
        gid = pointer.get("generation_id")
        if gid:
            seen.append(gid)
        prev = pointer.get("previous_generation_id")
        if prev:
            seen.append(prev)
        for gid in seen:
            try:
                mpath = gen._manifest_path(owner, gid)
                if os.path.isfile(mpath):
                    out.append({"kind": "generation", "id": gid, "path": mpath})
            except Exception:
                continue
    except Exception:
        pass
    for legacy in _legacy_list(owner):
        out.append({"kind": "legacy", "id": legacy, "path": legacy})
    return out


def latest_checkpoint(owner: str) -> Optional[str]:
    """Return the latest committed checkpoint as a loadable program path.

    PAC-I contract note: the authoritative identity of a checkpoint is its
    generation ID, but the historical public contract of THIS function is "a
    path that ``persist_rest.load(owner, path)`` can restore" (callers:
    core_i_maturity_test). That contract is preserved: for a committed
    generation this returns the generation's program member — a byte-exact
    sealed copy of the program payload, hence directly loadable. When no
    generation is committed, falls back to the legacy pointer / newest
    timestamped checkpoint (read-only compatibility).
    """
    from form.mandell import checkpoint_generation as gen
    try:
        gid = gen.current_generation_id(owner)
        if gid:
            manifest = gen._read_manifest(owner, gid)
            member_file = manifest.get("members", {}).get("program", {}).get("file")
            if member_file:
                mpath = os.path.join(_STATE_DIR, member_file)
                if os.path.isfile(mpath):
                    return mpath
    except Exception:
        pass
    # LEGACY_COMPAT: fall back to the old pointer / newest timestamp file.
    pointer = os.path.join(_STATE_DIR, f"program_{_safe_owner(owner)}_cp_latest.json")
    if os.path.isfile(pointer):
        try:
            with open(pointer, encoding="utf-8") as f:
                path = (json.load(f) or {}).get("path")
            if path and os.path.isfile(path):
                return path
        except Exception:
            pass
    named = [p for p in _legacy_list(owner) if os.path.isfile(p)]
    return named[-1] if named else None


def _eager_converge_live(program, owner: str, _fail_at: Optional[str] = None) -> None:
    """Eagerly converge live working state to the rolled-back program.

    DIRECTOR DECISION 2 (GDP-001 Phase-0 gate R1): successful rollback means
    current live state already reflects the selected committed generation
    when rollback returns. Do NOT wait for the next save.

    Conceptual operation:
      SELECT (caller) > VALIDATE (caller) > RESTORE/COPY INTO LIVE >
      ESTABLISH INDEPENDENT OWNERSHIP > UPDATE CURRENT STATE > VERIFY > RETURN.

    Never restores by aliasing live mutable state to a sealed member: the
    validated in-memory program is serialized and atomically written to the
    live owner files as independent copies. Sealed members are never written
    (Dell28 anti-corruption invariant preserved).

    Failure atomicity: all validation and serialization precede all writes.
    A failure before the first write leaves live state byte-identical
    (zero partial mutation). Each file write is crash-safe atomic
    (Persistence V2); a failure between the two writes leaves each file
    internally consistent (old or new, never corrupt).
    """
    from form import persist_rest
    from form.persist import serialize
    from form.mandell.checkpoint_generation import _check_fail, CheckpointError

    # RESTORE/COPY: serialize both payloads BEFORE touching any live file.
    _check_fail("rollback_serialize", _fail_at)
    program_data = serialize(program)
    nursery = program.nursery
    if nursery is None or not getattr(nursery, "path", None):
        raise CheckpointError("rollback: program has no bound nursery; refusing to converge")
    nursery_payload = {k: v.to_dict() for k, v in nursery.proposals.items()}
    from form.dell_matrix.nursery import DISPOSITION_SECTION_KEY
    nursery_payload[DISPOSITION_SECTION_KEY] = {
        cid: dict(rec) for cid, rec in nursery.conflict_dispositions.items()
    }
    # Pre-flight the nursery conflict guard BEFORE the program write, so a
    # concurrent live-nursery modification fails before any mutation.
    from form.dell_matrix.nursery import _disk_sig
    _check_fail("rollback_nursery_conflict", _fail_at)
    if _disk_sig(nursery.path) != nursery._seen:
        from form.dell_matrix.nursery import NurseryConflictError
        raise NurseryConflictError(
            "rollback: live nursery changed since generation load; "
            "refusing to overwrite (zero partial mutation)"
        )

    # ESTABLISH INDEPENDENT OWNERSHIP: atomic writes of independent copies.
    _check_fail("rollback_write_program", _fail_at)
    persist_rest.save(program)
    _check_fail("rollback_write_nursery", _fail_at)
    nursery.save()

    # UPDATE CURRENT STATE + VERIFY: fresh load must reflect the target.
    _check_fail("rollback_verify", _fail_at)
    rever = persist_rest.load(owner, activate=False)
    want_units = sorted(str(u) for u in program.cube.session.plane.units)
    got_units = sorted(str(u) for u in rever.cube.session.plane.units)
    if want_units != got_units:
        raise CheckpointError(
            f"rollback verification failed: live units {got_units} != "
            f"target {want_units}; live state may need repair"
        )


def rollback(owner: str, path: Optional[str] = None, *, _fail_at: Optional[str] = None):
    """Restore a checkpoint. ``path`` may be:

    - None → the current committed generation (CURRENT pointer authority);
    - a generation id → that generation, fingerprint-validated, never hybrid;
    - a legacy ``*.json`` checkpoint path → LEGACY_COMPAT load.

    DIRECTOR DECISION 2: on success, the live working state already reflects
    the selected committed generation when this returns (eager convergence).
    A fresh ``persist_rest.load(owner)`` observes the rolled-back state with
    no subsequent save required.

    Returns the restored program (Dell 28 activates it via new_program).
    Raises FileNotFoundError("rollback_missing") when nothing restorable exists.
    Raises CheckpointError/NurseryConflictError on convergence failure, with
    zero partial mutation for failures before the first live write.
    """
    from form.mandell import checkpoint_generation as gen
    from form.mandell.checkpoint_generation import (
        CheckpointError,
        _load_generation,
    )
    target = path
    if target is None:
        try:
            # activate=True: same session binding the legacy load path performed.
            program, _receipt = gen.load_checkpoint(owner, activate=True)
        except CheckpointError as exc:
            raise FileNotFoundError(f"rollback_missing: {exc}") from exc
    # Legacy explicit file path.
    elif isinstance(target, str) and target.endswith(".json") and os.path.isfile(target):
        program = load(owner, target)
    # Otherwise treat as a generation id.
    else:
        try:
            program, _receipt = _load_generation(owner, str(target), True, None)
        except CheckpointError as exc:
            raise FileNotFoundError(f"rollback_missing: {exc}") from exc
    # Eager convergence: live files reflect the target before we return.
    _eager_converge_live(program, owner, _fail_at=_fail_at)
    return program
