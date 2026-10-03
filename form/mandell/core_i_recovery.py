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
import hashlib
import json
import os

from form.persist import _STATE_DIR, _safe_owner, load


class RollbackRecoveryError(Exception):
    """Raised when a rollback transaction journal cannot be recovered
    to a proven-coherent state. Load must fail closed; never expose
    potentially hybrid live state."""


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


def _journal_path(owner: str) -> str:
    """Path of the rollback transaction journal for ``owner``."""
    from form.persist import _STATE_DIR, _safe_owner
    return os.path.join(_STATE_DIR, f"rollback_{_safe_owner(owner)}.journal.json")


def _staging_path(owner: str, kind: str) -> str:
    """Staging file for a rollback transaction (kind: 'program'|'nursery')."""
    from form.persist import _STATE_DIR, _safe_owner
    return os.path.join(_STATE_DIR, f"rollback_{_safe_owner(owner)}.{kind}.staging")


def _write_journal(owner: str, journal: dict, _fail_at: Optional[str] = None) -> None:
    """Atomically write the rollback transaction journal."""
    from form.dell_matrix.atomic_write import atomic_write_json
    from form.mandell.checkpoint_generation import _check_fail
    _check_fail("rollback_journal", _fail_at)
    atomic_write_json(_journal_path(owner), journal)


def recover_rollback_transaction(owner: str) -> Optional[str]:
    """Deterministically recover an interrupted rollback transaction.

    FAIL-CLOSED: Called before live state is exposed (e.g. at load).
    Either establishes a proven-coherent pair or raises
    RollbackRecoveryError. Never suppresses, never guesses, never
    exposes potentially hybrid state.

    Returns:
    - None: no journal; live state is authoritative as-is.
    - "rolled_back": journal was in 'prepared' phase; transaction never
      staged; old live pair verified against recorded fingerprints;
      journal removed.
    - "completed": journal was in 'staged' or 'committed' phase; the
      staged pair was deterministically committed; resulting canonical
      files verified against recorded target fingerprints; journal removed.

    Raises RollbackRecoveryError on: corrupt journal JSON, unknown phase,
    missing required fields, missing staging files when needed,
    fingerprint mismatch, or I/O failure during recovery.
    """
    jpath = _journal_path(owner)
    if not os.path.isfile(jpath):
        return None

    # Validate journal JSON.
    try:
        with open(jpath, encoding="utf-8") as f:
            journal = json.load(f)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
        raise RollbackRecoveryError(
            f"rollback journal corrupt/unreadable for owner {owner!r}: {exc}; "
            f"refusing to expose live state"
        ) from exc
    if not isinstance(journal, dict):
        raise RollbackRecoveryError(
            f"rollback journal for {owner!r} is not a JSON object; refusing"
        )

    phase = journal.get("phase")
    if phase == "prepared":
        return _recover_prepared(owner, jpath, journal)
    if phase in ("staged", "committed"):
        return _recover_staged(owner, jpath, journal)
    # Unknown phase: refuse to guess; preserve journal for diagnosis.
    raise RollbackRecoveryError(
        f"rollback journal for {owner!r} has unknown phase {phase!r}; "
        f"refusing to recover; journal preserved at {jpath}"
    )


def _validate_journal_fields(owner: str, journal: dict, required: tuple) -> None:
    missing = [k for k in required if k not in journal]
    if missing:
        raise RollbackRecoveryError(
            f"rollback journal for {owner!r} missing required fields "
            f"{missing}; refusing to recover"
        )


def _recover_prepared(owner: str, jpath: str, journal: dict) -> str:
    """'prepared' phase: nothing was staged. Verify live files match the
    recorded old fingerprints (if recorded), then discard the journal.
    The old pair remains authoritative."""
    _validate_journal_fields(owner, journal,
                             ("old_program_sha256", "old_nursery_sha256"))
    from form.persist import _path as _live_program_path
    from form.dell_matrix.nursery import owner_nursery_path
    live_prog = _live_program_path(owner)
    live_nurs = owner_nursery_path(owner)
    # Verify coherence: live files must match recorded old fingerprints.
    # None means the file did not exist at prepare time.
    for label, path, recorded in (
        ("program", live_prog, journal["old_program_sha256"]),
        ("nursery", live_nurs, journal["old_nursery_sha256"]),
    ):
        if recorded is None:
            continue  # legitimately absent at prepare time
        if not os.path.isfile(path):
            raise RollbackRecoveryError(
                f"rollback recovery: live {label} file missing but journal "
                f"records old hash {recorded[:16]}; cannot prove old pair; "
                f"refusing"
            )
        actual = _sha256_file(path)
        if actual != recorded:
            raise RollbackRecoveryError(
                f"rollback recovery: live {label} hash {actual[:16]} != "
                f"recorded old {recorded[:16]}; cannot prove old pair; refusing"
            )
    os.unlink(jpath)
    return "rolled_back"


def _recover_staged(owner: str, jpath: str, journal: dict) -> str:
    """'staged'/'committed' phase: deterministically complete the commit,
    then verify the canonical files match the recorded target fingerprints.
    The target pair becomes authoritative only after proof."""
    _validate_journal_fields(owner, journal,
                             ("program_sha256", "nursery_sha256"))
    from form.persist import _path as _live_program_path
    from form.dell_matrix.nursery import owner_nursery_path
    for kind, live_fn in (("program", _live_program_path),
                          ("nursery", owner_nursery_path)):
        staging = _staging_path(owner, kind)
        live = live_fn(owner)
        if os.path.isfile(staging):
            try:
                os.replace(staging, live)
            except OSError as exc:
                raise RollbackRecoveryError(
                    f"rollback recovery: failed to commit {kind} staging "
                    f"for {owner!r}: {exc}; refusing"
                ) from exc
        # If no staging file: the rename already happened (idempotent), or
        # the transaction never staged this member. Either way, the
        # fingerprint check below proves the final state.
    # Prove coherence: canonical files must match target fingerprints.
    live_prog = _live_program_path(owner)
    live_nurs = owner_nursery_path(owner)
    for label, path, recorded in (
        ("program", live_prog, journal["program_sha256"]),
        ("nursery", live_nurs, journal["nursery_sha256"]),
    ):
        if not os.path.isfile(path):
            raise RollbackRecoveryError(
                f"rollback recovery: canonical {label} file missing after "
                f"commit for {owner!r}; cannot prove target pair; refusing"
            )
        actual = _sha256_file(path)
        if actual != recorded:
            raise RollbackRecoveryError(
                f"rollback recovery: canonical {label} hash {actual[:16]} != "
                f"recorded target {recorded[:16]} for {owner!r}; cannot prove "
                f"target pair; refusing"
            )
    os.unlink(jpath)
    return "completed"


def _eager_converge_live(program, owner: str, _fail_at: Optional[str] = None) -> None:
    """Eagerly converge live working state to the rolled-back program.

    DIRECTOR DECISION 2 (gate R1) + FINDING 1 (gate R2): successful rollback
    means current live state already reflects the selected committed
    generation when rollback returns, with PAIR-ATOMICITY — a reader must
    never accept a hybrid program/nursery live state.

    Transactional model (journaled two-file transaction, Director option B):

      1. PREPARE: serialize both payloads; write journal {phase: prepared}
         with old/new fingerprints. No live file touched.
      2. STAGE: write both payloads to staging files; journal -> {staged}.
         Live files untouched.
      3. COMMIT: atomic rename staging -> live for both files (the commit
         boundary); journal -> {committed}; journal removed.
      4. VERIFY: fresh load reflects the target.

    Crash recovery: `recover_rollback_transaction` (called before live
    state is exposed) deterministically finishes or rolls back:
    - 'prepared'  -> old pair authoritative (nothing staged).
    - 'staged'/'committed' -> complete the renames; target pair authoritative.
    After recovery, the reader sees EITHER the complete old pair OR the
    complete target pair. NEVER hybrid.

    Never aliases live state to a sealed member: staged payloads are
    serialized independent copies. Sealed members are never written
    (Dell28 invariant preserved).
    """
    import hashlib
    from form import persist_rest
    from form.persist import serialize, _path as _live_program_path
    from form.mandell.checkpoint_generation import _check_fail, CheckpointError
    from form.dell_matrix.atomic_write import atomic_write_json
    from form.dell_matrix.nursery import (
        DISPOSITION_SECTION_KEY, _disk_sig, NurseryConflictError,
        owner_nursery_path,
    )

    # 1. PREPARE: serialize both payloads BEFORE touching any live file.
    _check_fail("rollback_serialize", _fail_at)
    program_data = serialize(program)
    nursery = program.nursery
    if nursery is None or not getattr(nursery, "path", None):
        raise CheckpointError("rollback: program has no bound nursery; refusing to converge")
    nursery_payload = {k: v.to_dict() for k, v in nursery.proposals.items()}
    nursery_payload[DISPOSITION_SECTION_KEY] = {
        cid: dict(rec) for cid, rec in nursery.conflict_dispositions.items()
    }
    # Pre-flight the nursery conflict guard BEFORE any mutation.
    _check_fail("rollback_nursery_conflict", _fail_at)
    if _disk_sig(nursery.path) != nursery._seen:
        raise NurseryConflictError(
            "rollback: live nursery changed since generation load; "
            "refusing to overwrite (zero partial mutation)"
        )
    live_prog = _live_program_path(owner)
    live_nurs = owner_nursery_path(owner)
    journal = {
        "phase": "prepared",
        "owner": owner,
        # Target hashes are filled after staging with the actual staged
        # file bytes (not canonical JSON).
        "program_sha256": None,
        "nursery_sha256": None,
        "old_program_sha256": _sha256_file(live_prog) if os.path.isfile(live_prog) else None,
        "old_nursery_sha256": _sha256_file(live_nurs) if os.path.isfile(live_nurs) else None,
    }
    _write_journal(owner, journal, _fail_at=_fail_at)

    # 2. STAGE: write both payloads to staging files (live untouched).
    _check_fail("rollback_stage", _fail_at)
    staging_prog = _staging_path(owner, "program")
    staging_nurs = _staging_path(owner, "nursery")
    prog_blob = atomic_write_json(staging_prog, program_data)
    nurs_blob = atomic_write_json(staging_nurs, nursery_payload)
    # Record the ACTUAL staged file hashes (not canonical JSON), so
    # recovery can prove the committed files are byte-identical to what
    # was staged. atomic_write_json returns the exact bytes written.
    journal["program_sha256"] = hashlib.sha256(prog_blob).hexdigest()
    journal["nursery_sha256"] = hashlib.sha256(nurs_blob).hexdigest()
    journal["phase"] = "staged"
    _write_journal(owner, journal, _fail_at=_fail_at)

    # 3. COMMIT: atomic renames (the commit boundary). After the first
    # rename, a crash leaves the journal in 'staged' -> recovery completes
    # the second rename deterministically. No hybrid is ever exposed.
    _check_fail("rollback_commit_program", _fail_at)
    os.replace(staging_prog, live_prog)
    _check_fail("rollback_commit_nursery", _fail_at)
    os.replace(staging_nurs, live_nurs)
    journal["phase"] = "committed"
    _write_journal(owner, journal, _fail_at=_fail_at)
    _check_fail("rollback_cleanup", _fail_at)
    os.unlink(_journal_path(owner))
    # Refresh the in-memory nursery's conflict baseline to the new live file.
    nursery._seen = _disk_sig(live_nurs)

    # 4. VERIFY: fresh load (with recovery) must reflect the target.
    _check_fail("rollback_verify", _fail_at)
    rever = persist_rest.load(owner, activate=False)
    want_units = sorted(str(u) for u in program.cube.session.plane.units)
    got_units = sorted(str(u) for u in rever.cube.session.plane.units)
    if want_units != got_units:
        raise CheckpointError(
            f"rollback verification failed: live units {got_units} != "
            f"target {want_units}; live state may need repair"
        )


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


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
