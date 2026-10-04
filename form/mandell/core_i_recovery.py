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
        result = _recover_staged(owner, jpath, journal)
        # R2 (ARGUS MF-R2-1): recovery must also complete the observable
        # working set, not just the canonical files. The transaction proved
        # TARGET COMPLETE for program+nursery+ideas-snapshot; rehydration
        # makes the individual idea files agree with the snapshot.
        # Marker-guarded and idempotent: safe under repeated recovery.
        from form.mandell.idea_checkpoint import rehydrate_ideas_from_live
        rehydrate_ideas_from_live(owner)
        return result
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
    The old triple remains authoritative."""
    _validate_journal_fields(owner, journal,
                             ("old_program_sha256", "old_nursery_sha256",
                              "old_ideas_sha256"))
    from form.persist import _path as _live_program_path
    from form.dell_matrix.nursery import owner_nursery_path
    from form.mandell.idea_checkpoint import ideas_snapshot_path
    from form.mandell.semantic_graph import graph_path as _graph_live_path
    live_prog = _live_program_path(owner)
    live_nurs = owner_nursery_path(owner)
    live_ideas = ideas_snapshot_path(owner)
    live_graph = _graph_live_path(owner)
    # Verify coherence: live files must match recorded old fingerprints.
    # None means the file did not exist at prepare time.
    members = [
        ("program", live_prog, journal["old_program_sha256"]),
        ("nursery", live_nurs, journal["old_nursery_sha256"]),
        ("ideas", live_ideas, journal["old_ideas_sha256"]),
    ]
    # Phase 2: old (3-member) journals have no graph fields; the graph was
    # never part of those transactions, so it is correctly left alone.
    if "old_graph_sha256" in journal:
        members.append(("graph", live_graph, journal["old_graph_sha256"]))
    for label, path, recorded in members:
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
    The target triple becomes authoritative only after proof."""
    _validate_journal_fields(owner, journal,
                             ("program_sha256", "nursery_sha256", "ideas_sha256"))
    from form.persist import _path as _live_program_path
    from form.dell_matrix.nursery import owner_nursery_path
    from form.mandell.idea_checkpoint import ideas_snapshot_path
    from form.mandell.semantic_graph import graph_path as _graph_live_path
    kinds = (("program", _live_program_path),
             ("nursery", owner_nursery_path),
             ("ideas", ideas_snapshot_path))
    # Phase 2: old (3-member) journals have no graph target hash; the
    # graph was never staged by those transactions, so it is left alone.
    if "graph_sha256" in journal:
        kinds = kinds + (("graph", _graph_live_path),)
    for kind, live_fn in kinds:
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
    live_ideas = ideas_snapshot_path(owner)
    members = [
        ("program", live_prog, journal["program_sha256"]),
        ("nursery", live_nurs, journal["nursery_sha256"]),
        ("ideas", live_ideas, journal["ideas_sha256"]),
    ]
    if "graph_sha256" in journal:
        members.append(("graph", _graph_live_path(owner), journal["graph_sha256"]))
    for label, path, recorded in members:
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


def _eager_converge_live(program, owner: str, _fail_at: Optional[str] = None,
                        _ideas_snapshot_path: Optional[str] = None,
                        _graph_member_path: Optional[str] = None) -> None:
    """Eagerly converge live working state to the rolled-back program.

    DIRECTOR DECISION 2 (gate R1) + FINDING 1 (gate R2): successful rollback
    means current live state already reflects the selected committed
    generation when rollback returns, with PAIR-ATOMICITY — a reader must
    never accept a hybrid program/nursery live state.

    Transactional model (journaled multi-file transaction, Director option B,
    generalized to four members in Phase 2: program+nursery+ideas+graph):

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

    # 1. PREPARE: serialize all three payloads BEFORE touching any live file.
    _check_fail("rollback_serialize", _fail_at)
    program_data = serialize(program)
    nursery = program.nursery
    if nursery is None or not getattr(nursery, "path", None):
        raise CheckpointError("rollback: program has no bound nursery; refusing to converge")
    nursery_payload = {k: v.to_dict() for k, v in nursery.proposals.items()}
    nursery_payload[DISPOSITION_SECTION_KEY] = {
        cid: dict(rec) for cid, rec in nursery.conflict_dispositions.items()
    }
    # R2: Ideas payload. The ideas_snapshot_path_for_rollback is passed
    # explicitly to avoid guessing. It points to the sealed generation's
    # ideas member file.
    ideas_data = None
    if _ideas_snapshot_path:
        try:
            with open(_ideas_snapshot_path, "rb") as f:
                ideas_blob = f.read()
            # Validate it's valid JSON with expected structure.
            ideas_data = json.loads(ideas_blob.decode("utf-8"))
            if not isinstance(ideas_data, dict) or "ideas" not in ideas_data:
                raise CheckpointError("rollback: sealed ideas member invalid structure")
        except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise CheckpointError(f"rollback: sealed ideas member unreadable: {exc}") from exc
    # Phase 2: graph payload. The sealed graph member is the relationship
    # log; validated structurally here, fully validated on next graph load.
    graph_data = None
    if _graph_member_path:
        try:
            with open(_graph_member_path, "rb") as f:
                graph_blob = f.read()
            graph_data = json.loads(graph_blob.decode("utf-8"))
            if not isinstance(graph_data, dict) or not isinstance(
                    graph_data.get("relationships"), list):
                raise CheckpointError("rollback: sealed graph member invalid structure")
        except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise CheckpointError(f"rollback: sealed graph member unreadable: {exc}") from exc
    # Pre-flight the nursery conflict guard BEFORE any mutation.
    _check_fail("rollback_nursery_conflict", _fail_at)
    if _disk_sig(nursery.path) != nursery._seen:
        raise NurseryConflictError(
            "rollback: live nursery changed since generation load; "
            "refusing to overwrite (zero partial mutation)"
        )
    live_prog = _live_program_path(owner)
    live_nurs = owner_nursery_path(owner)
    from form.mandell.idea_checkpoint import ideas_snapshot_path
    live_ideas = ideas_snapshot_path(owner)
    from form.mandell.semantic_graph import graph_path as _graph_live_path
    live_graph = _graph_live_path(owner)
    journal = {
        "phase": "prepared",
        "owner": owner,
        # Target hashes are filled after staging with the actual staged
        # file bytes (not canonical JSON).
        "program_sha256": None,
        "nursery_sha256": None,
        "ideas_sha256": None,
        "graph_sha256": None,
        "old_program_sha256": _sha256_file(live_prog) if os.path.isfile(live_prog) else None,
        "old_nursery_sha256": _sha256_file(live_nurs) if os.path.isfile(live_nurs) else None,
        "old_ideas_sha256": _sha256_file(live_ideas) if os.path.isfile(live_ideas) else None,
        "old_graph_sha256": _sha256_file(live_graph) if os.path.isfile(live_graph) else None,
    }
    _write_journal(owner, journal, _fail_at=_fail_at)

    # 2. STAGE: write all four payloads to staging files (live untouched).
    _check_fail("rollback_stage", _fail_at)
    staging_prog = _staging_path(owner, "program")
    staging_nurs = _staging_path(owner, "nursery")
    staging_ideas = _staging_path(owner, "ideas")
    staging_graph = _staging_path(owner, "graph")
    prog_blob = atomic_write_json(staging_prog, program_data)
    nurs_blob = atomic_write_json(staging_nurs, nursery_payload)
    # R2: Stage ideas payload. If no ideas snapshot was provided (e.g.,
    # legacy generation without ideas member), stage an empty snapshot
    # to maintain the three-member invariant.
    if ideas_data is not None:
        ideas_blob = atomic_write_json(staging_ideas, ideas_data)
    else:
        ideas_blob = atomic_write_json(staging_ideas, {"owner": owner, "ideas": {}})
    # Phase 2: stage the graph payload. A generation without a graph
    # member (pre-Phase-2) stages an empty graph log: the coherent "graph
    # cleared" semantic — the live 4-tuple always reflects exactly the
    # selected generation's members.
    from form.mandell.semantic_graph import _GRAPH_FORMAT_VERSION
    if graph_data is not None:
        graph_blob = atomic_write_json(staging_graph, graph_data)
    else:
        graph_blob = atomic_write_json(staging_graph, {
            "format_version": _GRAPH_FORMAT_VERSION, "owner": owner,
            "relationships": [], "paths": []})
    # Record the ACTUAL staged file hashes (not canonical JSON), so
    # recovery can prove the committed files are byte-identical to what
    # was staged. atomic_write_json returns the exact bytes written.
    journal["program_sha256"] = hashlib.sha256(prog_blob).hexdigest()
    journal["nursery_sha256"] = hashlib.sha256(nurs_blob).hexdigest()
    journal["ideas_sha256"] = hashlib.sha256(ideas_blob).hexdigest()
    journal["graph_sha256"] = hashlib.sha256(graph_blob).hexdigest()
    journal["phase"] = "staged"
    _write_journal(owner, journal, _fail_at=_fail_at)

    # 3. COMMIT: atomic renames (the commit boundary). After the first
    # rename, a crash leaves the journal in 'staged' -> recovery completes
    # the remaining renames deterministically. No hybrid is ever exposed.
    _check_fail("rollback_commit_program", _fail_at)
    os.replace(staging_prog, live_prog)
    _check_fail("rollback_commit_nursery", _fail_at)
    os.replace(staging_nurs, live_nurs)
    _check_fail("rollback_commit_ideas", _fail_at)
    os.replace(staging_ideas, live_ideas)
    _check_fail("rollback_commit_graph", _fail_at)
    os.replace(staging_graph, live_graph)
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
    """SHA256 hex digest of file bytes, or empty string if missing.
    
    Note: This is the legacy version used by rollback/supersession.
    The confirmation recovery uses a separate version that returns "absent".
    """
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
    except OSError:
        return ""
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

    R2 legacy semantic (ARGUS A-R2-1, advisory): rolling back to a pre-R1
    generation whose manifest has no ideas member stages and commits an
    EMPTY ideas snapshot, and rehydration clears stale individual idea
    files. The coherent semantic is "ideas cleared", not "ideas preserved".
    This is destructive but explicit and consistent: the live triple always
    reflects exactly the selected generation's members.

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
    receipt = None
    if target is None:
        try:
            # activate=True: same session binding the legacy load path performed.
            program, receipt = gen.load_checkpoint(owner, activate=True)
        except CheckpointError as exc:
            raise FileNotFoundError(f"rollback_missing: {exc}") from exc
    # Legacy explicit file path.
    elif isinstance(target, str) and target.endswith(".json") and os.path.isfile(target):
        program = load(owner, target)
    # Otherwise treat as a generation id.
    else:
        try:
            program, receipt = _load_generation(owner, str(target), True, None)
        except CheckpointError as exc:
            raise FileNotFoundError(f"rollback_missing: {exc}") from exc
    # Eager convergence: live files reflect the target before we return.
    # R2: The three-member transaction (program+nursery+ideas) is atomic.
    # The ideas snapshot path is passed for the transaction; the separate
    # restore_ideas_from_snapshot call is removed (was outside transaction).
    ideas_snapshot_path = None
    if receipt and "members" in receipt and "ideas" in receipt["members"]:
        from form.persist import _STATE_DIR
        ideas_spec = receipt["members"]["ideas"]
        ideas_snapshot_path = os.path.join(_STATE_DIR, ideas_spec["file"])
    # Phase 2: the sealed graph member restores alongside the other three.
    # A generation without a graph member (pre-Phase-2) converges to an
    # empty graph log — the coherent "graph cleared" semantic.
    graph_member_path = None
    if receipt and "members" in receipt and "graph" in receipt["members"]:
        from form.persist import _STATE_DIR
        graph_spec = receipt["members"]["graph"]
        graph_member_path = os.path.join(_STATE_DIR, graph_spec["file"])
    _eager_converge_live(program, owner, _fail_at=_fail_at,
                         _ideas_snapshot_path=ideas_snapshot_path,
                         _graph_member_path=graph_member_path)
    # R2 (NULL N1/N2): Rehydrate individual idea files from the LIVE
    # canonical snapshot just committed by the transaction. This is
    # UNCONDITIONAL: even a legacy rollback (no sealed ideas member,
    # empty snapshot staged) must clear stale files, giving the coherent
    # "ideas cleared" semantic. Marker-guarded (see idea_checkpoint).
    from form.mandell.idea_checkpoint import rehydrate_ideas_from_live
    rehydrate_ideas_from_live(owner)
    return program


# ---------------------------------------------------------------------------
# Confirmation-hybrid recovery (GDP_ARGUS_CONFIRMATION_CONVERGENCE_R2)
# ---------------------------------------------------------------------------

def recover_confirmation_hybrid(owner: str) -> int:
    """Heal crashed confirmations: nursery=confirmed but Idea absent.

    FAIL-CLOSED recovery, called before live state is exposed (e.g. at load).
    Detects the hybrid left by a crash between nursery.save() and
    program.save() during confirm_proposal, and heals to OLD by reverting
    the proposal status to "pending".

    This is the production-reader counterpart to the checkpoint transaction.
    The checkpoint pointer provides atomicity only for checkpoint-aware
    readers; the production loader reads live files directly. This recovery
    ensures the loader never exposes a hybrid.

    Returns the number of healed proposals (0 = no hybrid found).

    Raises:
        RollbackRecoveryError: If the nursery or program file is unreadable
            or malformed (fail closed, never expose potentially hybrid state).

    Note (R3): This visibility-based heuristic is DEPRECATED. It cannot
    distinguish a crashed confirmation from a legitimate historical record
    (e.g., faded Idea). Use recover_confirmation_intent() which recovers
    from the recorded journal instead. This function is retained for
    backward compatibility during migration.
    """
    from form.persist import _path, _STATE_DIR
    from form.dell_matrix.nursery import owner_nursery_path
    from form.dell_matrix.atomic_write import atomic_write_json

    npath = owner_nursery_path(owner)
    ppath = _path(owner)

    # If either file is missing, no hybrid is possible.
    if not os.path.isfile(npath) or not os.path.isfile(ppath):
        return 0

    # Read live nursery file.
    try:
        with open(npath, encoding="utf-8") as f:
            ndata = json.load(f)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
        raise RollbackRecoveryError(
            f"confirmation recovery: unreadable nursery file: {exc}"
        ) from exc

    # Read live program file, extract plane unit IDs.
    try:
        with open(ppath, encoding="utf-8") as f:
            pdata = json.load(f)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
        raise RollbackRecoveryError(
            f"confirmation recovery: unreadable program file: {exc}"
        ) from exc

    # Extract unit IDs from program plane.
    unit_ids = set()
    try:
        plane = pdata.get("plane", {})
        units = plane.get("units", {})
        if isinstance(units, dict):
            unit_ids = set(units.keys())
    except (AttributeError, TypeError):
        # Malformed program structure: fail closed.
        raise RollbackRecoveryError(
            "confirmation recovery: malformed program plane structure"
        )

    # Find confirmed proposals without corresponding Ideas.
    healed = 0
    for pid, prop in ndata.items():
        # Skip non-proposal keys (e.g., __conflict_dispositions__).
        if not isinstance(prop, dict):
            continue
        if pid.startswith("__"):
            continue
        status = prop.get("status")
        if status == "confirmed" and pid not in unit_ids:
            # Hybrid detected: confirmed proposal without Idea.
            # Heal to OLD by reverting to pending.
            prop["status"] = "pending"
            healed += 1

    # Write back if any healed (atomic).
    if healed > 0:
        try:
            atomic_write_json(npath, ndata)
        except Exception as exc:
            raise RollbackRecoveryError(
                f"confirmation recovery: failed to write healed nursery: {exc}"
            ) from exc

    return healed


# ---------------------------------------------------------------------------
# Confirmation intent journal (GDP_R3_IDEA_PRESERVATION_ADDENDUM)
# ---------------------------------------------------------------------------
# R2 used visibility-based healing ("confirmed without Idea = crash").
# R3 corrects this: absence from Plane does NOT prove acceptance never
# committed. Historical records (faded, superseded) may legitimately lack
# Plane Ideas. Recovery must use RECORDED INTENT, not inferred visibility.
#
# Protocol:
#   1. Before any file writes, journal records: operation, proposal_id,
#      owner, phase="prepared", old fingerprints.
#   2. Perform file writes (nursery, program).
#   3. On success, delete journal (phase="committed" implied by deletion).
#   4. On recovery, if journal exists: check the RECORDED proposal only.
#      Do not scan all proposals. Historical records without journals
#      are never touched.

CONFIRM_JOURNAL_VERSION = 1


def _confirm_journal_path(owner: str) -> str:
    """Path of the confirmation intent journal for ``owner``."""
    from form.persist import _STATE_DIR, _safe_owner
    return os.path.join(_STATE_DIR, f"confirm_{_safe_owner(owner)}.journal.json")


def _sha256_file_absent(path: str) -> str:
    """SHA256 hex digest of file bytes.
    
    Returns:
        - Hex digest if file exists and is readable
        - "absent" if file does not exist (legitimate pre-operation absence)
        - Raises OSError if file exists but is unreadable (corrupt storage)
    
    Used by confirmation recovery. Supersession uses _sha256_file (returns "").
    """
    import hashlib, os
    if not os.path.exists(path):
        return "absent"
    # File exists; if unreadable, let the exception propagate (don't mask I/O errors)
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def write_confirm_intent(owner: str, proposal_id: str) -> None:
    """Record intent to confirm before any durable writes.

    Must be called BEFORE modifying nursery/program files. The journal
    enables crash recovery to distinguish "crashed confirmation" from
    "legitimate historical record".
    """
    from form.persist import _path
    from form.dell_matrix.nursery import owner_nursery_path
    from form.dell_matrix.atomic_write import atomic_write_json

    journal = {
        "journal_version": CONFIRM_JOURNAL_VERSION,
        "operation": "confirm_proposal",
        "owner": owner,
        "proposal_id": proposal_id,
        "phase": "prepared",
        "old_nursery_sha256": _sha256_file_absent(owner_nursery_path(owner)),
        "old_program_sha256": _sha256_file_absent(_path(owner)),
    }
    atomic_write_json(_confirm_journal_path(owner), journal)


def clear_confirm_intent(owner: str) -> None:
    """Delete the confirmation journal after successful commit."""
    try:
        os.unlink(_confirm_journal_path(owner))
    except OSError:
        pass


def recover_confirmation_intent(owner: str) -> str:
    """Recover from recorded confirmation intent (not inferred visibility).

    STRICT CONTRACT (GDP_R3_COMPLETION_GATE req. 2):
    - Validates exact owner, supported operation, strict version/type,
      phase, proposal identity, and required fingerprints BEFORE mutation.
    - Missing, malformed, or conflicting authoritative members → PRESERVE
      journal and fail closed (raise), unless transaction evidence proves
      a safe outcome.
    - Malformed Units are NOT interpreted as empty valid Plane.
    - Journal is cleared ONLY after proving coherence of every affected
      member (nursery AND program) for either NEW-complete or OLD-complete.
    - Stale journals (proposal already resolved) do not mutate history.

    Returns:
        "none": No journal; nothing to recover.
        "already_complete": Journal existed and both files provably reflect
            the confirmed state; journal cleared.
        "healed_to_old": Journal existed, nursery was modified but program
            lacks the Idea; proposal reverted to pending, journal cleared.
        "no_change": Journal existed but nursery still matches OLD AND
            program is coherent; journal cleared.

    Raises:
        RollbackRecoveryError: Journal corrupt, files missing/unreadable,
            or members malformed/conflicting (fail closed, journal preserved).
    """
    jpath = _confirm_journal_path(owner)
    if not os.path.isfile(jpath):
        return "none"

    # --- Validate journal strictly BEFORE any mutation ---
    try:
        with open(jpath, encoding="utf-8") as f:
            journal = json.load(f)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
        raise RollbackRecoveryError(
            f"confirmation intent: corrupt journal (preserved): {exc}"
        ) from exc

    if not isinstance(journal, dict):
        raise RollbackRecoveryError(
            "confirmation intent: journal is not a dict (preserved)"
        )
    if journal.get("journal_version") != CONFIRM_JOURNAL_VERSION:
        raise RollbackRecoveryError(
            f"confirmation intent: unsupported version {journal.get('journal_version')} (preserved)"
        )
    # Exact owner match (prevent foreign-owner journal application)
    if journal.get("owner") != owner:
        raise RollbackRecoveryError(
            f"confirmation intent: owner mismatch journal={journal.get('owner')} expected={owner} (preserved)"
        )
    # Supported operation
    if journal.get("operation") != "confirm_proposal":
        raise RollbackRecoveryError(
            f"confirmation intent: unsupported operation {journal.get('operation')} (preserved)"
        )
    # Phase must be prepared (we only write prepared; committed is deletion)
    if journal.get("phase") != "prepared":
        raise RollbackRecoveryError(
            f"confirmation intent: unexpected phase {journal.get('phase')} (preserved)"
        )
    proposal_id = journal.get("proposal_id")
    # Validate required fields. Malformed transaction evidence is FAIL-CLOSED:
    # preserve the journal and refuse unverified live state.
    # "absent" is a valid value for fingerprints (legitimate pre-operation absence).
    # Empty string or missing field is malformed.
    if not proposal_id or not isinstance(proposal_id, str):
        raise RollbackRecoveryError(
            "confirmation intent: missing or invalid proposal_id (journal preserved)"
        )
    old_nursery_fp = journal.get("old_nursery_sha256")
    old_program_fp = journal.get("old_program_sha256")
    # "absent" is valid (file didn't exist at journal time).
    # Empty string, None, or non-string is malformed.
    if not isinstance(old_nursery_fp, str) or old_nursery_fp == "":
        raise RollbackRecoveryError(
            "confirmation intent: missing or invalid old_nursery_sha256 (journal preserved)"
        )
    if not isinstance(old_program_fp, str) or old_program_fp == "":
        raise RollbackRecoveryError(
            "confirmation intent: missing or invalid old_program_sha256 (journal preserved)"
        )

    from form.persist import _path
    from form.dell_matrix.nursery import owner_nursery_path
    from form.dell_matrix.atomic_write import atomic_write_json

    npath = owner_nursery_path(owner)
    ppath = _path(owner)

    # --- Files must exist and be readable; otherwise fail closed ---
    # If a member file is missing, we cannot assume the operation never wrote.
    # The journal records "absent" for legitimately missing files at journal time.
    # But we must verify BOTH members against recorded evidence before clearing.
    # Do NOT use one-member shortcuts.
    #
    # If a file is missing and the journal did NOT record "absent" for it,
    # the file was deleted/corrupted → fail closed.
    if not os.path.isfile(npath) and old_nursery_fp != "absent":
        raise RollbackRecoveryError(
            f"confirmation intent: nursery file missing (journal preserved): {npath}"
        )
    if not os.path.isfile(ppath) and old_program_fp != "absent":
        raise RollbackRecoveryError(
            f"confirmation intent: program file missing (journal preserved): {ppath}"
        )

    # --- Compute BOTH fingerprints FIRST, including explicit absence ---
    # _sha256_file returns "absent" for missing files.
    # Handle proven unchanged OLD before attempting to open missing files.
    current_nursery_fp = _sha256_file_absent(npath)
    current_program_fp = _sha256_file_absent(ppath)

    if current_nursery_fp == old_nursery_fp and current_program_fp == old_program_fp:
        # Both members unchanged, including legitimate absence ("absent"=="absent").
        # Operation never wrote. Safe to clear.
        clear_confirm_intent(owner)
        return "no_change"

    # --- Read and validate PRESENT members ---
    # Do not interpret malformed content as absence.
    # Only open files that exist; absent files were already handled above.
    if os.path.isfile(npath):
        try:
            with open(npath, encoding="utf-8") as f:
                ndata = json.load(f)
        except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
            raise RollbackRecoveryError(
                f"confirmation intent: unreadable nursery (journal preserved): {exc}"
            ) from exc
        if not isinstance(ndata, dict):
            raise RollbackRecoveryError(
                "confirmation intent: nursery is not a dict (journal preserved)"
            )
    else:
        ndata = None  # Absent; was recorded as "absent" in journal

    if os.path.isfile(ppath):
        try:
            with open(ppath, encoding="utf-8") as f:
                pdata = json.load(f)
        except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
            raise RollbackRecoveryError(
                f"confirmation intent: unreadable program (journal preserved): {exc}"
            ) from exc
        if not isinstance(pdata, dict):
            raise RollbackRecoveryError(
                "confirmation intent: program is not a dict (journal preserved)"
            )
    else:
        pdata = None  # Absent; was recorded as "absent" in journal

    # --- Validate Program structure strictly (if present) ---
    # Do NOT interpret malformed Units as empty valid Plane.
    # If pdata is None (absent), skip validation; the fingerprint check already handled it.
    # For changed companion + absent member, we fail closed below (cannot prove outcome).
    if pdata is None:
        # Program absent. If we reach here, the fingerprint check did NOT clear as no_change,
        # meaning at least one member changed. Changed companion + absent member → fail closed
        # unless the journal proves a coherent outcome. For now, fail closed.
        raise RollbackRecoveryError(
            "confirmation intent: program absent but nursery changed (journal preserved). "
            "Cannot prove safe outcome."
        )
    plane = pdata.get("plane")
    if plane is None:
        raise RollbackRecoveryError(
            "confirmation intent: program missing 'plane' member (journal preserved)"
        )
    if not isinstance(plane, dict):
        raise RollbackRecoveryError(
            "confirmation intent: program 'plane' is not a dict (journal preserved)"
        )
    units = plane.get("units")
    if units is None:
        raise RollbackRecoveryError(
            "confirmation intent: program plane missing 'units' (journal preserved)"
        )
    if not isinstance(units, dict):
        raise RollbackRecoveryError(
            f"confirmation intent: program units is {type(units).__name__}, not dict (journal preserved)"
        )
    unit_ids = set(units.keys())

    # Fingerprints already computed and checked above for no_change.
    # If we reach here, at least one member changed.
    # Continue with proposal status verification below.
    # (The nursery-unchanged-but-program-modified check is handled by the
    #  specific proposal status logic that follows.)

    # --- Nursery was modified. Examine the RECORDED proposal ---
    prop = ndata.get(proposal_id)
    if not isinstance(prop, dict):
        # Proposal not in nursery. This could be:
        # (a) Stale journal (proposal was deleted/superseded after), or
        # (b) Corrupted state.
        # We cannot prove safe outcome, so preserve journal and fail closed.
        # EXCEPTION: If the proposal_id looks like a stale reference and
        # the nursery is otherwise coherent, we may clear. But we cannot
        # distinguish, so fail closed.
        raise RollbackRecoveryError(
            f"confirmation intent: proposal {proposal_id} not in nursery (journal preserved)"
        )

    status = prop.get("status")
    if status != "confirmed":
        # Proposal exists but is not confirmed.
        # GDP_R3_CLOSE_STALE_INTENT_ESCAPE req. 1: Pending status alone does
        # NOT prove Program stayed OLD. Must check if the specific Idea was
        # written.
        if status == "pending":
            # If the Idea IS in the program, the operation partially completed
            # (wrote Program but not Nursery). This is an incomplete transition,
            # NOT a stale journal. Fail closed; do NOT clear.
            if proposal_id in unit_ids:
                raise RollbackRecoveryError(
                    f"confirmation intent: proposal {proposal_id} pending but "
                    f"Idea present in program (journal preserved). Incomplete transition."
                )
            # Idea NOT in program. The operation did not write the Program.
            # The nursery fingerprint difference (if any) is from unrelated
            # concurrent writes. The journal is stale. Safe to clear.
            # Note: We do NOT require program fp == OLD, because unrelated
            # writes (other Ideas, timestamps) may have changed it. The
            # absence of the specific Idea proves the operation didn't complete.
            clear_confirm_intent(owner)
            return "no_change"
        # Status is neither confirmed nor pending (e.g., rejected, etc.).
        # Cannot prove safe outcome; preserve journal and fail closed.
        raise RollbackRecoveryError(
            f"confirmation intent: proposal {proposal_id} status={status}, not confirmed (journal preserved)"
        )

    # --- Proposal is confirmed. Check Idea presence ---
    if proposal_id in unit_ids:
        # Both files reflect NEW state. Prove program coherence:
        # The Idea must be a valid dict (not just present).
        idea = units.get(proposal_id)
        if not isinstance(idea, dict):
            raise RollbackRecoveryError(
                f"confirmation intent: Idea {proposal_id} is malformed (journal preserved)"
            )
        # NEW is complete and coherent. Safe to clear.
        clear_confirm_intent(owner)
        return "already_complete"

    # --- Hybrid: nursery confirmed, program lacks Idea, journal proves intent ---
    # Heal to OLD by reverting proposal to pending.
    # This is the ONLY case where we mutate.
    #
    # R3-COMPLETE-EXISTING-CONTRACT req. 1: When claiming OLD, compare the
    # recorded Program fingerprint. The heal is only valid if the Program
    # was never modified (still matches OLD). If Program was modified,
    # we cannot prove OLD coherence; fail closed.
    current_program_fp = _sha256_file_absent(ppath)
    if current_program_fp != old_program_fp:
        raise RollbackRecoveryError(
            f"confirmation intent: program modified (fp mismatch), cannot prove OLD "
            f"(journal preserved). Expected {old_program_fp[:8]}, got {current_program_fp[:8]}"
        )
    # Program matches OLD. Safe to revert nursery.
    prop["status"] = "pending"
    try:
        atomic_write_json(npath, ndata)
    except Exception as exc:
        raise RollbackRecoveryError(
            f"confirmation intent: failed to heal nursery (journal preserved): {exc}"
        ) from exc
    # Verify the heal succeeded before clearing journal.
    healed_fp = _sha256_file_absent(npath)
    if healed_fp == current_nursery_fp:
        raise RollbackRecoveryError(
            "confirmation intent: heal did not change nursery (journal preserved)"
        )
    clear_confirm_intent(owner)
    return "healed_to_old"


# ---------------------------------------------------------------------------
# Supersession intent journal (GDP_R3_COMPLETION_GATE req. 3)
# ---------------------------------------------------------------------------
# A supersession is ONE logical transition, not two independent operations.
# It must record and recover:
#   - Successor acceptance/content (new proposal confirmed, Idea present)
#   - Predecessor lifecycle (old proposal marked superseded)
#   - Complete revision links (bidirectional chain)
#
# The successor's confirmation journal must NOT be cleared until the
# entire supersession is recoverable. Use this enclosing journal instead.

SUPERSEDE_JOURNAL_VERSION = 1


def _supersede_journal_path(owner: str) -> str:
    """Path of the supersession intent journal for ``owner``."""
    from form.persist import _STATE_DIR, _safe_owner
    return os.path.join(_STATE_DIR, f"supersede_{_safe_owner(owner)}.journal.json")


def write_supersede_intent(owner: str, old_id: str, new_id: str) -> None:
    """Record supersession intent before any durable writes.

    Covers the complete transition: successor acceptance, predecessor
    lifecycle change, and revision links. Must be called BEFORE modifying
    any files.
    """
    from form.persist import _path
    from form.dell_matrix.nursery import owner_nursery_path
    from form.dell_matrix.atomic_write import atomic_write_json

    journal = {
        "journal_version": SUPERSEDE_JOURNAL_VERSION,
        "operation": "supersede_proposal",
        "owner": owner,
        "old_id": old_id,
        "new_id": new_id,
        "phase": "prepared",
        "old_nursery_sha256": _sha256_file_absent(owner_nursery_path(owner)),
        "old_program_sha256": _sha256_file_absent(_path(owner)),
    }
    atomic_write_json(_supersede_journal_path(owner), journal)


def clear_supersede_intent(owner: str) -> None:
    """Delete the supersession journal after successful commit."""
    try:
        os.unlink(_supersede_journal_path(owner))
    except OSError:
        pass


def recover_supersede_intent(owner: str) -> str:
    """Recover from recorded supersession intent.

    Validates the complete transition:
    - Successor: confirmed in nursery, Idea present in program
    - Predecessor: marked superseded in nursery
    - Links: bidirectional (old.superseded_by_id == new_id,
      new.chain includes old_id)

    Returns:
        "none": No journal.
        "already_complete": All members coherent; journal cleared.
        "healed_to_old": Incomplete; reverted to pre-supersession state.

    Raises:
        RollbackRecoveryError: Cannot prove safe outcome (journal preserved).
    """
    jpath = _supersede_journal_path(owner)
    if not os.path.isfile(jpath):
        return "none"

    # Strict validation (same pattern as confirmation)
    try:
        with open(jpath, encoding="utf-8") as f:
            journal = json.load(f)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
        raise RollbackRecoveryError(
            f"supersede intent: corrupt journal (preserved): {exc}"
        ) from exc

    if not isinstance(journal, dict):
        raise RollbackRecoveryError("supersede intent: not a dict (preserved)")
    if journal.get("journal_version") != SUPERSEDE_JOURNAL_VERSION:
        raise RollbackRecoveryError("supersede intent: bad version (preserved)")
    if journal.get("owner") != owner:
        raise RollbackRecoveryError("supersede intent: owner mismatch (preserved)")
    if journal.get("operation") != "supersede_proposal":
        raise RollbackRecoveryError("supersede intent: bad operation (preserved)")
    if journal.get("phase") != "prepared":
        raise RollbackRecoveryError("supersede intent: bad phase (preserved)")

    old_id = journal.get("old_id")
    new_id = journal.get("new_id")
    if not old_id or not new_id:
        raise RollbackRecoveryError("supersede intent: missing ids (preserved)")

    from form.persist import _path
    from form.dell_matrix.nursery import owner_nursery_path
    from form.dell_matrix.atomic_write import atomic_write_json

    npath = owner_nursery_path(owner)
    ppath = _path(owner)

    if not os.path.isfile(npath):
        raise RollbackRecoveryError("supersede intent: nursery missing (preserved)")
    if not os.path.isfile(ppath):
        raise RollbackRecoveryError("supersede intent: program missing (preserved)")

    try:
        with open(npath, encoding="utf-8") as f:
            ndata = json.load(f)
        with open(ppath, encoding="utf-8") as f:
            pdata = json.load(f)
    except Exception as exc:
        raise RollbackRecoveryError(
            f"supersede intent: unreadable files (preserved): {exc}"
        ) from exc

    # Validate program structure
    plane = pdata.get("plane")
    if not isinstance(plane, dict):
        raise RollbackRecoveryError("supersede intent: bad plane (preserved)")
    units = plane.get("units")
    if not isinstance(units, dict):
        raise RollbackRecoveryError("supersede intent: bad units (preserved)")

    # Check if nursery was modified
    current_fp = _sha256_file(npath)
    if current_fp == journal.get("old_nursery_sha256"):
        clear_supersede_intent(owner)
        return "no_change"

    # Examine both proposals
    old_prop = ndata.get(old_id)
    new_prop = ndata.get(new_id)

    # Complete NEW state requires:
    # - new confirmed, Idea present
    # - old superseded
    # - links bidirectional
    new_ok = (
        isinstance(new_prop, dict)
        and new_prop.get("status") == "confirmed"
        and new_id in units
        and isinstance(units.get(new_id), dict)
    )
    old_ok = (
        isinstance(old_prop, dict)
        and old_prop.get("lifecycle_state") == "superseded"
    )
    # R3-COMPLETE-EXISTING-CONTRACT req. 2: Revision links use
    # supersedes_id/superseded_by_id. Do NOT check chain (derivation).
    links_ok = (
        isinstance(old_prop, dict)
        and old_prop.get("superseded_by_id") == new_id
        and isinstance(new_prop, dict)
        and new_prop.get("supersedes_id") == old_id
    )

    if new_ok and old_ok and links_ok:
        clear_supersede_intent(owner)
        return "already_complete"

    # If successor and predecessor are both in correct states but links
    # are incomplete, repair ONLY the revision links (not derivation chain).
    # R3-COMPLETE-EXISTING-CONTRACT req. 2: Supersession uses supersedes_id
    # and superseded_by_id, with revision root and number. Do NOT add
    # revision ancestry to derivation chain. The two relationship types
    # remain distinct.
    if new_ok and old_ok and not links_ok:
        # Repair ONLY revision links (superseded_by_id, supersedes_id).
        # Do NOT touch chain (derivation lineage).
        if isinstance(old_prop, dict):
            old_prop["superseded_by_id"] = new_id
        if isinstance(new_prop, dict):
            new_prop["supersedes_id"] = old_id
        try:
            atomic_write_json(npath, ndata)
        except Exception as exc:
            raise RollbackRecoveryError(
                f"supersede intent: link repair failed (preserved): {exc}"
            ) from exc
        clear_supersede_intent(owner)
        return "already_complete"

    # Incomplete: heal to OLD.
    # This requires restoring the old proposal to active and removing
    # the new proposal's confirmation. We use the OLD fingerprint to
    # verify, but we don't have the full OLD content. Instead, we revert
    # the specific changes:
    # - new proposal -> pending (if it exists and was newly created)
    # - old proposal -> active (if it was marked superseded)
    # Note: This is a best-effort heal. If we cannot prove the revert
    # is safe, fail closed.
    healed = False
    if isinstance(new_prop, dict) and new_prop.get("status") == "confirmed":
        # Only revert if the Idea is also missing (true hybrid)
        # If Idea is present but links are incomplete, it's a different
        # kind of partial state that needs manual review.
        if new_id not in units:
            new_prop["status"] = "pending"
            healed = True
    if isinstance(old_prop, dict) and old_prop.get("lifecycle_state") == "superseded":
        # Only revert if the successor is being reverted too
        if healed:
            old_prop["lifecycle_state"] = "active"
            old_prop.pop("superseded_by_id", None)

    if healed:
        try:
            atomic_write_json(npath, ndata)
        except Exception as exc:
            raise RollbackRecoveryError(
                f"supersede intent: heal failed (preserved): {exc}"
            ) from exc
        clear_supersede_intent(owner)
        return "healed_to_old"

    # Cannot prove safe heal; preserve journal and fail closed.
    raise RollbackRecoveryError(
        "supersede intent: incomplete transition, cannot safely heal (preserved)"
    )
