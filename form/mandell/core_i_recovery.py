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

from typing import Any, Dict, List, Optional
import hashlib
import json
import os

from form.persist import _STATE_DIR, _safe_owner, load


class RollbackRecoveryError(Exception):
    """Raised when a rollback transaction journal cannot be recovered
    to a proven-coherent state. Load must fail closed; never expose
    potentially hybrid live state."""


# Director 2026-10-06 (close unsafe save): per-instance recovery-required
# flag. An instance whose compensation/rollback was incomplete must reject
# normal saves until verified restoration or reconstruction.
#
# The flag is IN-MEMORY ONLY (a dict of key -> record on the program and
# its nursery). Disk recovery by another instance (which clears the disk
# journal) does not repair -- and does not clear -- this instance's
# memory. A fresh load/reconstruction yields an unflagged instance.
# Keys are the artifact (proposal) IDs, so a verified restoration of the
# same artifact clears the condition however it was marked, while an
# unrelated unresolved artifact keeps saves rejected.

def mark_recovery_required(program, key, reason, details=None):
    """Mark a program instance as requiring recovery before it may save.

    Called when compensation/rollback verification fails (ok=False).
    Both the program and its nursery are marked so that
    ``persist_rest.save`` and ``nursery.save`` both reject.
    """
    record = {"reason": reason, "details": dict(details or {})}
    for obj in (program, getattr(program, "nursery", None)):
        if obj is None:
            continue
        try:
            req = getattr(obj, "_recovery_required", None)
            if not isinstance(req, dict):
                req = {}
            else:
                req = dict(req)
            req[key] = record
            obj._recovery_required = req
        except Exception:
            pass


def clear_recovery_required(program, key):
    """Clear one recovery-required condition after verified restoration.

    Called on the success path of a rollback helper, after its
    verification passes and before its internal save. Other unrelated
    keys are preserved.
    """
    for obj in (program, getattr(program, "nursery", None)):
        if obj is None:
            continue
        try:
            req = getattr(obj, "_recovery_required", None)
            if isinstance(req, dict) and key in req:
                req = dict(req)
                del req[key]
                if req:
                    obj._recovery_required = req
                else:
                    del obj._recovery_required
        except Exception:
            pass


def check_save_allowed(obj, what="save"):
    """Raise RollbackRecoveryError if the instance requires recovery.

    Called at the top of normal save paths. No bytes are written when
    the save is rejected; recovery evidence is preserved.

    R6.3: also rejects instances marked stale after an authority-bound
    rollback restored a generation beneath them. The initiating (and
    any pre-rollback) instance must not save stale state over the
    restored outcome; the caller must reload. Cross-instance staleness
    is tracked via the per-owner restoration epoch (process-local;
    sequential saves only, no concurrent-safety claim).
    """
    req = getattr(obj, "_recovery_required", None)
    if req:
        keys = sorted(req.keys()) if isinstance(req, dict) else ["unknown"]
        raise RollbackRecoveryError(
            f"{what} rejected: this instance requires recovery "
            f"(conditions={keys}). Complete a verified rollback or "
            f"reconstruct by reloading; no bytes were written and "
            f"recovery evidence is preserved."
        )
    if getattr(obj, "_post_rollback_stale", False):
        raise RollbackRecoveryError(
            f"{what} rejected: this instance is stale after an "
            f"authority-bound rollback restored a generation beneath "
            f"it. Reload to obtain the restored state; no bytes were "
            f"written."
        )
    # Unresolved authorized transaction: another pre-existing instance
    # must not overwrite an outstanding authorized transaction. Reuse
    # the journal authority (no parallel store). Trusted recovery
    # (via _recover_rollback_active) is allowed to finish.
    if not _recover_rollback_active:
        jpath = None
        owner = getattr(obj, "owner", None)
        if owner:
            jpath = _journal_path(owner)
        else:
            # Nursery: derive journal path from nursery path.
            # Nursery path: .../nursery_<safe_owner>.json
            # Journal path: .../rollback_<safe_owner>.journal.json
            # The <safe_owner> is already sanitized; reuse directly.
            path = getattr(obj, "path", None)
            if path:
                import re as _re
                m = _re.search(r"nursery_(.+)\.json$", path)
                if m:
                    from form.persist import _STATE_DIR
                    safe = m.group(1)
                    jpath = os.path.join(
                        _STATE_DIR, f"rollback_{safe}.journal.json")
        if jpath and os.path.isfile(jpath):
            try:
                with open(jpath, encoding="utf-8") as f:
                    j = json.load(f)
                if _journal_claims_authorization(j):
                    raise RollbackRecoveryError(
                        f"{what} rejected: an authorized rollback "
                        f"transaction is unresolved. Complete recovery "
                        f"before writing; no bytes were written."
                    )
            except (OSError, ValueError):
                # Unreadable journal: fail closed via existing
                # recovery path, not here.
                pass
    # Cross-instance epoch check: if a rollback completed after this
    # instance was loaded, the instance is stale. Uses canonical
    # (_safe_owner) identity so Program and Nursery agree.
    owner = getattr(obj, "owner", None)
    if owner is None:
        # Nursery (no owner attr): derive sanitized owner from its path.
        # Path format: .../state/nursery_<safe_owner>.json
        # The path already contains the sanitized form; use it directly
        # as the canonical key (do not try to unsanitize).
        path = getattr(obj, "path", None)
        if path:
            import re as _re
            m = _re.search(r"nursery_(.+)\.json$", path)
            if m:
                # m.group(1) is already _safe_owner form; use as key
                key = m.group(1)
                current_epoch = _rollback_epochs.get(key, 0)
                instance_epoch = getattr(obj, "_rollback_epoch", 0)
                if instance_epoch != current_epoch:
                    raise RollbackRecoveryError(
                        f"{what} rejected: this instance was loaded before an "
                        f"authority-bound rollback restored a generation "
                        f"(epoch {instance_epoch} != {current_epoch}). Reload "
                        f"to obtain the restored state; no bytes were written."
                    )
                return
    if owner:
        key = _epoch_key(owner)
        current_epoch = _rollback_epochs.get(key, 0)
        instance_epoch = getattr(obj, "_rollback_epoch", 0)
        if instance_epoch != current_epoch:
            raise RollbackRecoveryError(
                f"{what} rejected: this instance was loaded before an "
                f"authority-bound rollback restored a generation "
                f"(epoch {instance_epoch} != {current_epoch}). Reload "
                f"to obtain the restored state; no bytes were written."
            )


def _gen_id_from_stamp(stamp: Optional[str]) -> str:
    """Map a caller stamp into the generation-id namespace, or mint a fresh id."""
    from form.mandell.checkpoint_generation import _new_generation_id
    if stamp:
        safe = "".join(c if c.isalnum() else "_" for c in str(stamp))[:32]
        if safe:
            return safe
    return _new_generation_id()


def checkpoint(program, stamp: Optional[str] = None, *,
               keep_extra=None) -> str:
    """Seal the program's current logical state as one coherent generation.

    Delegates to Checkpoint Generation V1. Returns the committed generation id
    (observable generation identity). Raises CheckpointCommitError on failure;
    a failure before the CURRENT pointer swap leaves the previous committed
    generation authoritative — never a partial state.

    keep_extra: generation ids that retention must preserve in addition to
    current + previous (R6.3: the frozen rollback target).
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
    receipt = gen.commit_checkpoint(program, generation_id=gen_id,
                                    keep_extra=keep_extra)
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


# ---------------------------------------------------------------------------
# R6.3 integrated authorization (GDP_PHASE_6_R63_COMPLETE_OUTCOME_AND_EVIDENCE)
#
# The authorized rollback outcome is recorded IN THE EXISTING rollback
# transaction journal (_journal_path), not a parallel file. The journal's
# "authorized" phase IS the durable commit decision:
#
#   - Before the durable record: no journal; crash restores OLD safely
#     (live state is untouched; nothing to complete).
#   - After the durable record: the journal's "authorized" phase means
#     the commit decision was made. Crash recovery MUST complete the
#     recorded authorized target, even if live files are unchanged.
#     "Unchanged live files" after a commit decision is "crash before
#     restoration", not "no_change".
#
# _eager_converge_live preserves the authorization fields when it
# advances the journal to "prepared"/"staged"/"committed". There is one
# journal, one outcome, one lifecycle.
# ---------------------------------------------------------------------------

#: Required member kinds in an authorized rollback target.
_ROLLBACK_MEMBER_KINDS = ("program", "nursery", "ideas", "graph")

#: Journal phases for the integrated R6.3 lifecycle.
_ROLLBACK_PHASES = ("authorized", "prepared", "staged", "committed")


def _is_hex64(value: object) -> bool:
    """Strict 64-char lowercase hex fingerprint check."""
    return (isinstance(value, str) and len(value) == 64
            and all(c in "0123456789abcdef" for c in value))


def write_rollback_authorization(owner: str, generation_id: str,
                                 manifest_sha256: str,
                                 target_members: dict,
                                 compensating_generation_id: str) -> None:
    """Record the durable commit decision in the transaction journal.

    Must be called AFTER the live authority revalidation (the commit
    decision) and BEFORE the canonical rollback. The journal's
    "authorized" phase means: the authorized outcome is durably
    recorded; crash recovery must complete it.

    Strict validation: no malformed field is silently filtered.
    """
    from form.dell_matrix.atomic_write import atomic_write_json
    if not isinstance(owner, str) or not owner:
        raise ValueError("owner must be non-empty str")
    if not isinstance(generation_id, str) or not generation_id:
        raise ValueError("generation_id must be non-empty str")
    if not _is_hex64(manifest_sha256):
        raise ValueError("manifest_sha256 must be 64-char hex")
    if not isinstance(target_members, dict):
        raise ValueError("target_members must be a dict")
    # Exact required member set; no missing, no extra, no malformed.
    if set(target_members.keys()) != set(_ROLLBACK_MEMBER_KINDS):
        raise ValueError(
            f"target_members must name exactly {_ROLLBACK_MEMBER_KINDS}; "
            f"got {sorted(target_members.keys())}")
    for kind, sha in target_members.items():
        if not _is_hex64(sha):
            raise ValueError(
                f"target_members[{kind!r}] must be 64-char hex")
    if (not isinstance(compensating_generation_id, str)
            or not compensating_generation_id):
        raise ValueError("compensating_generation_id must be non-empty str")
    journal = {
        "phase": "authorized",
        "operation": "authority_bound_rollback",
        "owner": owner,
        "generation_id": generation_id,
        "manifest_sha256": manifest_sha256,
        "target_members": dict(target_members),
        "compensating_generation_id": compensating_generation_id,
    }
    atomic_write_json(_journal_path(owner), journal)


def _validate_authorized_journal(owner: str, journal: dict) -> dict:
    """Strictly validate an "authorized"-phase journal. Fail closed.

    Returns the journal on success. Raises RollbackRecoveryError on any
    malformed field; the journal is preserved for diagnosis. Nothing is
    silently filtered or defaulted.
    """
    def _bad(detail: str) -> RollbackRecoveryError:
        return RollbackRecoveryError(
            f"rollback journal for {owner!r}: invalid authorized phase "
            f"({detail}); journal preserved; refusing to recover")
    if journal.get("operation") != "authority_bound_rollback":
        raise _bad(f"operation={journal.get('operation')!r}")
    if journal.get("owner") != owner:
        raise _bad("owner mismatch")
    gid = journal.get("generation_id")
    if not isinstance(gid, str) or not gid:
        raise _bad("generation_id malformed")
    if not _is_hex64(journal.get("manifest_sha256")):
        raise _bad("manifest_sha256 malformed")
    members = journal.get("target_members")
    if not isinstance(members, dict):
        raise _bad("target_members not a dict")
    if set(members.keys()) != set(_ROLLBACK_MEMBER_KINDS):
        raise _bad(f"target_members keys={sorted(members.keys())}")
    for kind, sha in members.items():
        if not _is_hex64(sha):
            raise _bad(f"target_members[{kind!r}] malformed")
    comp = journal.get("compensating_generation_id")
    if not isinstance(comp, str) or not comp:
        raise _bad("compensating_generation_id malformed")
    return journal


def _revalidate_sealed_target(owner: str, journal: dict) -> None:
    """Re-validate the sealed generation against the authorized record.

    Verifies that the sealed manifest and member fingerprints still
    match the authorization. This proves the staged bytes (verified
    separately against staged hashes) represent the approved
    generation, not just that bytes were written.

    Raises RollbackRecoveryError on mismatch (journal preserved).
    """
    from form.mandell import checkpoint_generation as gen
    import hashlib as _hl
    target_gid = journal["generation_id"]
    try:
        manifest = gen._read_manifest(owner, target_gid)
    except Exception as exc:
        raise RollbackRecoveryError(
            f"rollback recovery: sealed target {target_gid!r} unreadable "
            f"(journal preserved): {exc}") from exc
    # Manifest fingerprint must match.
    _mh = _hl.sha256()
    try:
        with open(gen._manifest_path(owner, target_gid), "rb") as _mf:
            for _chunk in iter(lambda: _mf.read(65536), b""):
                _mh.update(_chunk)
    except OSError as exc:
        raise RollbackRecoveryError(
            f"rollback recovery: sealed manifest unreadable "
            f"(journal preserved): {exc}") from exc
    if _mh.hexdigest() != journal["manifest_sha256"]:
        raise RollbackRecoveryError(
            f"rollback recovery: sealed manifest changed since "
            f"authorization (journal preserved); refusing")
    # Member fingerprints must match.
    for kind, sha in journal["target_members"].items():
        spec = (manifest.get("members") or {}).get(kind) or {}
        if spec.get("sha256") != sha:
            raise RollbackRecoveryError(
                f"rollback recovery: sealed member {kind!r} changed "
                f"since authorization (journal preserved); refusing")


def _carry_authorization(owner: str, journal: dict) -> None:
    """Carry authorization evidence forward through every phase.

    If the existing transaction journal carries R6.3 authorization
    metadata (in ANY supported phase: authorized, prepared, staged,
    committed), its authorization fields are copied into the new
    journal dict (in place) before the file-level transaction advances.
    The authorization is preserved through replay; it is not a
    competing outcome.

    Fail-closed: unreadable, corrupt, non-object, or malformed
    authorization evidence RAISES (journal preserved). Never silently
    returns and overwrites it. Malformed metadata does not downgrade
    a new transaction into legacy.

    Recognizes the PRESENCE of authorization metadata before
    validating it: if the journal claims authorization
    (operation == "authority_bound_rollback" or has target_members),
    it must validate strictly.
    """
    jpath = _journal_path(owner)
    if not os.path.isfile(jpath):
        return
    try:
        with open(jpath, encoding="utf-8") as f:
            existing = json.load(f)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise RollbackRecoveryError(
            f"rollback journal for {owner!r} unreadable during "
            f"authorization carry (preserved): {exc}; refusing to "
            f"overwrite") from exc
    if not isinstance(existing, dict):
        raise RollbackRecoveryError(
            f"rollback journal for {owner!r} is not an object during "
            f"authorization carry (preserved); refusing to overwrite")
    # Recognize authorization metadata presence before validating.
    # Uses the shared presence predicate.
    if not _journal_claims_authorization(existing):
        # Genuine legacy journal: no authorization to carry. Explicit.
        return
    # Authorization claimed: must validate strictly. Malformed does
    # not downgrade to legacy; it fails closed.
    _validate_authorized_journal(owner, existing)
    for key in ("operation", "generation_id", "manifest_sha256",
                "target_members", "compensating_generation_id"):
        journal[key] = existing[key]


def _verify_rollback_outcome(owner: str, program, journal: dict) -> None:
    """Verify the complete restored rollback outcome. Shared.

    Used by both normal execution (_eager_converge_live) and restart
    recovery. Verifies:
      1. All four live member files match the sealed target fingerprints.
      2. The fresh production load reflects the target program units.
      3. Rehydrated individual idea files agree with the live snapshot.

    Raises CheckpointError on any mismatch; the journal is preserved
    (caller deletes only after this returns). Fail closed.
    """
    from form.mandell.checkpoint_generation import CheckpointError
    from form.persist import _path as _live_program_path
    from form.dell_matrix.nursery import owner_nursery_path
    from form.mandell.idea_checkpoint import (
        ideas_snapshot_path, rehydrate_ideas_from_live)
    from form.mandell.semantic_graph import graph_path as _graph_live_path
    from form import persist_rest

    # Target fingerprints: prefer the staged file hashes (what was
    # actually written to live files by the transaction). The sealed
    # target_members are used only if staged hashes are not yet
    # recorded (e.g. pre-convergence verification). Sealed member bytes
    # and re-serialized live bytes differ; the staged hash is the
    # correct expectation for live files.
    if journal.get("program_sha256"):
        want = {
            "program": journal.get("program_sha256"),
            "nursery": journal.get("nursery_sha256"),
            "ideas": journal.get("ideas_sha256"),
            "graph": journal.get("graph_sha256"),
        }
    elif journal.get("target_members"):
        want = dict(journal["target_members"])
    else:
        want = {}
    live_paths = {
        "program": _live_program_path(owner),
        "nursery": owner_nursery_path(owner),
        "ideas": ideas_snapshot_path(owner),
        "graph": _graph_live_path(owner),
    }
    for kind in _ROLLBACK_MEMBER_KINDS:
        expected = want.get(kind)
        if not _is_hex64(expected):
            raise CheckpointError(
                f"rollback verification: no valid target fingerprint "
                f"for member {kind!r}; refusing to declare complete")
        path = live_paths[kind]
        if not os.path.isfile(path):
            raise CheckpointError(
                f"rollback verification: live {kind} file missing; "
                f"expected {expected[:16]}")
        actual = _sha256_file(path)
        if actual != expected:
            raise CheckpointError(
                f"rollback verification: live {kind} hash {actual[:16]} "
                f"!= target {expected[:16]}")
    # Fresh production load must reflect the target program.
    rever = persist_rest.load(owner, activate=False)
    if rever is None:
        raise CheckpointError(
            "rollback verification: restored program failed to load")
    # If a target program was supplied (authorized path), verify units
    # match. For legacy (program=None), the staged hashes already prove
    # the members; units check is skipped.
    if program is not None:
        want_units = sorted(str(u) for u in program.cube.session.plane.units)
        got_units = sorted(str(u) for u in rever.cube.session.plane.units)
        if want_units != got_units:
            raise CheckpointError(
                f"rollback verification failed: live units {got_units} != "
                f"target {want_units}")
    # Rehydration must make individual idea files agree with the live
    # snapshot. This is idempotent and marker-guarded.
    rehydrate_ideas_from_live(owner)


# Narrowly scoped reentrancy guard: prevents recursive recovery when
# _recover_authorized calls _eager_converge_live (whose VERIFY calls
# persist_rest.load, which re-enters recover_rollback_transaction).
# This is a guard, not journal deletion — the journal persists through
# the entire recovery until verified completion.
_recover_rollback_active = False

# R6.3: per-owner restoration epoch (process-local). When an
# authority-bound rollback completes, the epoch increments. Instances
# record the epoch at load; check_save_allowed rejects saves from
# instances whose epoch is stale (loaded before the restoration).
# This protects pre-existing instances in the same process from
# overwriting the restored outcome via sequential saves. No
# concurrent-safety claim.
_rollback_epochs: dict = {}


def _epoch_key(owner: str) -> str:
    """Canonical restoration-resource identity for epoch keys.

    Uses _safe_owner (the same sanitization as storage paths) so that
    Program and Nursery agree, and owner names mapping to the same
    storage path share the epoch. Do NOT use the raw owner string.
    """
    from form.persist import _safe_owner
    return _safe_owner(owner)


def _advance_rollback_epoch(owner: str) -> None:
    """Advance the per-owner restoration epoch.

    Called at the canonical completion boundary (verified rollback
    completion, including recovery). Pre-existing instances in this
    process become stale for save purposes. Keyed by canonical
    (_safe_owner) identity.
    """
    key = _epoch_key(owner)
    _rollback_epochs[key] = _rollback_epochs.get(key, 0) + 1


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
    # Narrow reentrancy guard: if we are already inside a recovery that
    # is completing the outcome (e.g. VERIFY's fresh load re-enters
    # here), the outer recovery owns the journal. Do not recurse.
    if _recover_rollback_active:
        return None
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
    if phase == "authorized":
        return _recover_authorized(owner, jpath, journal)
    if phase == "prepared":
        return _recover_prepared(owner, jpath, journal)
    if phase in ("staged", "committed"):
        # _recover_staged completes the commit, rehydrates, verifies,
        # and deletes the journal only after complete outcome proof.
        return _recover_staged(owner, jpath, journal)
    # Unknown phase: refuse to guess; preserve journal for diagnosis.
    raise RollbackRecoveryError(
        f"rollback journal for {owner!r} has unknown phase {phase!r}; "
        f"refusing to recover; journal preserved at {jpath}"
    )


def _recover_authorized(owner: str, jpath: str, journal: dict) -> str:
    """'authorized' phase: the durable commit decision was recorded but
    the file-level convergence never started (crash after authorization,
    before/during the protected transition).

    The commit decision is durable: recovery MUST complete the recorded
    authorized target. "Unchanged live files" is crash-before-restoration,
    not "no_change" — the authorized restoration is never abandoned.

    Steps:
    1. Strictly validate the authorized journal (fail closed).
    2. Re-validate the sealed target generation (manifest + members).
    3. Check if live state already reflects the target (verified, not
       inferred from CURRENT). If so, delete journal, return
       "already_complete".
    4. Otherwise, load the target privately and run the file-level
       convergence to complete the authorized outcome. The journal
       advances to prepared/staged/committed and is deleted only after
       complete outcome verification.

    Returns "already_complete" or "completed". Raises
    RollbackRecoveryError on validation failure (journal preserved).
    """
    global _recover_rollback_active
    if _recover_rollback_active:
        # Re-entrant call from within recovery (e.g. VERIFY's fresh
        # load): the outer recovery is already completing the outcome.
        return "none"
    _validate_authorized_journal(owner, journal)
    target_gid = journal["generation_id"]
    target_members = journal["target_members"]

    from form.mandell import checkpoint_generation as gen
    # Re-validate the sealed target BEFORE any mutation (shared).
    _revalidate_sealed_target(owner, journal)

    # Check if live state ALREADY reflects the target (verified by
    # comparing live file bytes to sealed fingerprints — not by
    # inferring from the CURRENT pointer). If so, run the complete
    # shared verification (including rehydration) before clearing.
    if _live_matches_target(owner, target_members):
        # Load the target program for verification (private, no activation).
        program, _receipt = gen._load_generation(owner, target_gid, False, None)
        _recover_rollback_active = True
        try:
            # Rehydrate before deletion: individual Idea files must
            # agree with the live snapshot.
            from form.mandell.idea_checkpoint import rehydrate_ideas_from_live
            rehydrate_ideas_from_live(owner)
            _verify_rollback_outcome(owner, program, journal)
        finally:
            _recover_rollback_active = False
        os.unlink(jpath)
        _advance_rollback_epoch(owner)
        return "already_complete"

    # Complete the authorized outcome: load the target privately
    # (activation disabled) and run the file-level convergence.
    _recover_rollback_active = True
    try:
        program, receipt = gen._load_generation(owner, target_gid, False, None)
        from form.persist import _STATE_DIR
        import os as _os
        members = receipt.get("members") or {}
        ideas_path = None
        graph_path = None
        if "ideas" in members:
            ideas_path = _os.path.join(_STATE_DIR, members["ideas"]["file"])
        if "graph" in members:
            graph_path = _os.path.join(_STATE_DIR, members["graph"]["file"])
        _eager_converge_live(program, owner,
                             _ideas_snapshot_path=ideas_path,
                             _graph_member_path=graph_path)
    finally:
        _recover_rollback_active = False
    # _eager_converge_live verified the complete outcome and deleted
    # the journal. Return the completion.
    return "completed"


def _live_matches_target(owner: str, target_members: dict) -> bool:
    """Check if live files byte-match the target's sealed fingerprints.

    Returns True only if ALL four live members exist and match. This
    is verification, not inference from the CURRENT pointer.
    """
    from form.persist import _path as _live_program_path
    from form.dell_matrix.nursery import owner_nursery_path
    from form.mandell.idea_checkpoint import ideas_snapshot_path
    from form.mandell.semantic_graph import graph_path as _graph_live_path
    live_paths = {
        "program": _live_program_path(owner),
        "nursery": owner_nursery_path(owner),
        "ideas": ideas_snapshot_path(owner),
        "graph": _graph_live_path(owner),
    }
    for kind in _ROLLBACK_MEMBER_KINDS:
        expected = target_members.get(kind)
        if not _is_hex64(expected):
            return False
        path = live_paths[kind]
        if not os.path.isfile(path):
            return False
        if _sha256_file(path) != expected:
            return False
    return True


def _validate_journal_fields(owner: str, journal: dict, required: tuple) -> None:
    missing = [k for k in required if k not in journal]
    if missing:
        raise RollbackRecoveryError(
            f"rollback journal for {owner!r} missing required fields "
            f"{missing}; refusing to recover"
        )


def _journal_claims_authorization(journal: dict) -> bool:
    """Presence predicate: does the journal CLAIM authority-bound status?

    ONE shared rule used by carry, dispatch, prepared recovery, and
    staged/committed recovery. Presence identifies a claimed
    authority-bound record; strict validation (_validate_authorized_journal)
    determines whether it is valid.

    A journal claims authorization if it has:
    - operation == "authority_bound_rollback", OR
    - any authorization metadata key present (even if null/malformed)

    Malformed claimed records must be validated strictly and raise;
    they must NEVER downgrade to legacy handling.
    """
    if not isinstance(journal, dict):
        return False
    if journal.get("operation") == "authority_bound_rollback":
        return True
    # Presence of any auth metadata key, even if null/wrong-type
    for key in ("target_members", "manifest_sha256", "generation_id",
                "compensating_generation_id"):
        if key in journal:
            return True
    return False


def _journal_has_authorization(journal: dict) -> bool:
    """Check if the journal carries VALID R6.3 authorization evidence.

    DEPRECATED: Use _journal_claims_authorization for presence detection,
    then _validate_authorized_journal for strict validation. This
    function is retained for backward compatibility but should not be
    used for dispatch decisions (it permits downgrade on malformed).
    """
    return (journal.get("operation") == "authority_bound_rollback"
            and isinstance(journal.get("target_members"), dict)
            and isinstance(journal.get("generation_id"), str))


def _recover_prepared(owner: str, jpath: str, journal: dict) -> str:
    """'prepared' phase: nothing was staged.

    If the journal carries R6.3 authorization, the durable commit
    decision was made: recovery MUST complete the authorized target,
    not abandon it via legacy rollback. Delegates to the authorized
    recovery path.

    Legacy (no authorization): verify live files match the recorded
    old fingerprints (if recorded), then discard the journal. The old
    triple remains authoritative.
    """
    if _journal_claims_authorization(journal):
        # Authorized prepared: the commit decision is durable. Complete
        # the authorized target; do not fall through to legacy
        # abandonment. Strict validation raises on malformed (never
        # downgrades to legacy).
        _validate_authorized_journal(owner, journal)
        return _recover_authorized(owner, jpath, journal)
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
    then verify the complete outcome. The target becomes authoritative
    only after proof.

    If the journal carries R6.3 authorization, validate it and honor
    the authorized target through the complete verification (including
    rehydration) before journal deletion. The authorization is not
    abandoned.
    """
    global _recover_rollback_active
    if _journal_claims_authorization(journal):
        _validate_authorized_journal(owner, journal)
        # Re-validate the sealed target binding: the staged hashes
        # prove bytes were written, but not that they represent the
        # approved generation. The sealed manifest/member fingerprints
        # must still match the authorized record.
        _revalidate_sealed_target(owner, journal)
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
    # Complete verification via SHARED verifier: rehydrates individual
    # Idea files, verifies all four members, fresh load, and Idea
    # agreement BEFORE journal deletion. If verification fails, the
    # journal is preserved and recovery is repeatable.
    from form.mandell import checkpoint_generation as gen
    _recover_rollback_active = True
    try:
        # Load target program for verification (private, no activation).
        # For authorized journals, use the sealed generation; for legacy,
        # the program arg is not critical (verifier uses staged hashes).
        program = None
        if _journal_claims_authorization(journal):
            program, _receipt = gen._load_generation(
                owner, journal["generation_id"], False, None)
        _verify_rollback_outcome(owner, program, journal)
    finally:
        _recover_rollback_active = False
    os.unlink(jpath)
    # Advance epoch if this was an authorized recovery (not legacy).
    # Uses presence predicate: if auth was claimed, it was validated.
    if _journal_claims_authorization(journal):
        _advance_rollback_epoch(owner)
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
    global _recover_rollback_active
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
    # R6.3: preserve the authorization evidence if the journal already
    # records the durable commit decision ("authorized" phase). One
    # journal, one outcome, one lifecycle — the file-level transaction
    # carries the authorization forward; it is not a competing record.
    _carry_authorization(owner, journal)
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
    # Refresh the in-memory nursery's conflict baseline to the new live file.
    nursery._seen = _disk_sig(live_nurs)

    # 4. VERIFY: the complete restored outcome is verified BEFORE the
    # journal is deleted. Verification covers all four members against
    # the sealed target fingerprints plus rehydration. The journal is
    # deleted only after complete outcome verification (SQLite
    # atomic-commit ordering: commit record persists until the outcome
    # is proven).
    #
    # Narrow reentrancy: _verify_rollback_outcome calls persist_rest.load,
    # which re-enters recover_rollback_transaction. The guard prevents
    # the inner recovery from seeing the "committed" journal and
    # deleting it out from under this verification.
    _check_fail("rollback_verify", _fail_at)
    _recover_rollback_active = True
    try:
        _verify_rollback_outcome(owner, program, journal)
    finally:
        _recover_rollback_active = False
    _check_fail("rollback_cleanup", _fail_at)
    os.unlink(_journal_path(owner))
    # Canonical completion: invalidate pre-restoration instances.
    # This is the ONE completion rule for AUTHORIZED rollback;
    # called on successful _eager_converge_live (normal and recovery
    # paths). Legacy rollback does not advance (preserves existing
    # legacy test semantics).
    if _journal_claims_authorization(journal):
        _advance_rollback_epoch(owner)


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


def _validate_rollback_mediation(owner: str, path: Optional[str],
                                 mediation: Optional[Dict[str, Any]]) -> str:
    """Validate the mediation token for canonical rollback (R6.3).

    An owner string alone denies. The token is minted by
    Program.confirm_rollback after the live revalidation (the commit
    decision); recover_rollback_transaction completes recorded outcomes
    via the integrated journal and does not use this path.

    Returns the authorized generation id. Raises RollbackRecoveryError
    on missing/forged/mismatched mediation (fail closed, zero mutation).
    """
    if not isinstance(mediation, dict):
        raise RollbackRecoveryError(
            "rollback denied: missing mediation — an owner string alone "
            "denies. Use Program.confirm_rollback (authority-mediated).")
    if mediation.get("operation") != "checkpoint.rollback":
        raise RollbackRecoveryError(
            "rollback denied: mediation operation mismatch.")
    if mediation.get("owner") != owner:
        raise RollbackRecoveryError(
            "rollback denied: mediation owner mismatch.")
    gid = mediation.get("generation_id")
    if not isinstance(gid, str) or not gid:
        raise RollbackRecoveryError(
            "rollback denied: mediation names no generation.")
    # The requested target must be the authorized generation id.
    # (Legacy .json paths are not mediation-authorized.)
    want = path
    if want is None:
        # CURRENT resolved once here; the mediated Program path always
        # passes an explicit id, but the primitive preserves the
        # None→CURRENT semantic under mediation.
        from form.mandell import checkpoint_generation as gen
        try:
            want = gen._read_pointer(owner).get("generation_id")
        except Exception as exc:
            raise RollbackRecoveryError(
                f"rollback denied: CURRENT unreadable: {exc}") from exc
    if want != gid:
        raise RollbackRecoveryError(
            "rollback denied: requested target != authorized generation.")
    return gid


def rollback(owner: str, path: Optional[str] = None, *, _fail_at: Optional[str] = None,
             _mediation: Optional[Dict[str, Any]] = None):
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
    Raises RollbackRecoveryError when mediation is missing/invalid (R6.3:
    an owner string alone denies).
    """
    from form.mandell import checkpoint_generation as gen
    from form.mandell.checkpoint_generation import (
        CheckpointError,
        _load_generation,
    )
    # R6.3: mediation is mandatory and validated BEFORE any state access.
    _validate_rollback_mediation(owner, path, _mediation)
    target = path
    receipt = None
    if target is None:
        try:
            # R6.3: activate=False. The target is staged privately;
            # activation happens only after verified durable restoration.
            program, receipt = gen.load_checkpoint(owner, activate=False)
        except CheckpointError as exc:
            raise FileNotFoundError(f"rollback_missing: {exc}") from exc
    # Legacy explicit file path.
    elif isinstance(target, str) and target.endswith(".json") and os.path.isfile(target):
        program = load(owner, target)
    # Otherwise treat as a generation id.
    else:
        try:
            # R6.3: activate=False. Private staging; activation after
            # verified restoration (see below).
            program, receipt = _load_generation(owner, str(target), False, None)
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
    # R6.3: Activate ONLY after complete durable restoration is
    # verified. The target was staged privately; the live files are
    # now proven to reflect the target; session binding happens here.
    from form.persist_rest import bind as _bind_session
    _bind_session(program)
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


# ---------------------------------------------------------------------------
# Rollback-intent journal (GDP_PHASE_6_R63_AUTHORITY_BOUND_ROLLBACK)
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
    # F4: Strict version check - exclude bool (True == 1)
    _cjv = journal.get("journal_version")
    if not isinstance(_cjv, int) or isinstance(_cjv, bool) or _cjv != CONFIRM_JOURNAL_VERSION:
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
    # F4: Same strict standard as supersession. Valid values: 64-char hex
    # SHA-256 (file existed) or "absent" (file didn't exist). Missing/None/
    # empty/arbitrary strings fail closed.
    import re
    _sha256_re = re.compile(r'^[0-9a-f]{64}$')
    for fp_key, fp_val in (("old_nursery_sha256", old_nursery_fp),
                           ("old_program_sha256", old_program_fp)):
        if fp_val == "absent":
            continue
        if not isinstance(fp_val, str) or not _sha256_re.match(fp_val):
            raise RollbackRecoveryError(
                f"confirmation intent: missing or invalid {fp_key} (journal preserved)"
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

    # F5: Validate present members BEFORE fingerprint comparison.
    # Malformed present files must not be accepted as no_change merely
    # because their bytes match. Structure validation comes first.
    if os.path.isfile(npath):
        try:
            with open(npath, encoding="utf-8") as f:
                _nd = json.load(f)
            if not isinstance(_nd, dict):
                raise RollbackRecoveryError(
                    "confirmation intent: nursery malformed (journal preserved)")
        except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
            raise RollbackRecoveryError(
                f"confirmation intent: nursery unreadable (journal preserved): {exc}"
            ) from exc
    if os.path.isfile(ppath):
        try:
            with open(ppath, encoding="utf-8") as f:
                _pd = json.load(f)
            if not isinstance(_pd, dict):
                raise RollbackRecoveryError(
                    "confirmation intent: program malformed (journal preserved)")
            # F5: Present Program must have dict plane AND dict units.
            # None is malformed, not valid. Only "absent" file is legitimate absence.
            _plane = _pd.get("plane")
            if not isinstance(_plane, dict):
                raise RollbackRecoveryError(
                    "confirmation intent: plane must be dict (journal preserved)")
            _units = _plane.get("units")
            if not isinstance(_units, dict):
                raise RollbackRecoveryError(
                    "confirmation intent: units must be dict (journal preserved)")
        except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
            raise RollbackRecoveryError(
                f"confirmation intent: program unreadable (journal preserved): {exc}"
            ) from exc

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

    F6: Records the old proposal's revision root and number at intent-write
    time, read from the actual top-level Nursery contract (ndata[old_id] --
    proposals are stored directly under their IDs; there is no "proposals"
    key). Uses the established canonical normalization: root defaults to
    the proposal's own ID, number defaults to 1.

    All ancestry-reading failures (unreadable file, malformed JSON,
    non-dict top level, missing predecessor, malformed predecessor,
    unconfirmed predecessor, malformed root/number values) PROPAGATE as
    exceptions before any intent is written. The writer never guesses
    first-revision identity.

    The journal carries journal_format="ancestry_v2" with required
    intent_old_root (non-empty str) and intent_old_number (int, not bool).
    """
    from form.persist import _path
    from form.dell_matrix.nursery import owner_nursery_path
    from form.dell_matrix.atomic_write import atomic_write_json
    import json as _json

    # F6: Read the actual Nursery file. Failures propagate; no guessing.
    npath = owner_nursery_path(owner)
    with open(npath, encoding="utf-8") as f:
        ndata = _json.load(f)
    if not isinstance(ndata, dict):
        raise ValueError(
            f"supersede intent: nursery top level not a dict for owner {owner}")
    old_prop = ndata.get(old_id)
    if not isinstance(old_prop, dict):
        raise ValueError(
            f"supersede intent: predecessor {old_id} missing or malformed "
            f"in nursery (not a dict)")
    # Verify the predecessor is the recorded confirmed revision.
    if old_prop.get("status") != "confirmed":
        raise ValueError(
            f"supersede intent: predecessor {old_id} not confirmed "
            f"(status={old_prop.get('status')!r}); refusing intent")

    # F6: Capture and strictly validate revision identity.
    # Distinguish: absent (legitimate first revision) vs malformed.
    raw_root = old_prop.get("revision_root_id")
    if raw_root is None:
        old_root = old_id  # canonical normalization: first revision
    elif isinstance(raw_root, str) and raw_root:
        old_root = raw_root
    else:
        raise ValueError(
            f"supersede intent: predecessor {old_id} has malformed "
            f"revision_root_id {raw_root!r}")
    raw_num = old_prop.get("revision_number")
    if raw_num is None:
        old_num = 1  # canonical normalization: first revision
    elif isinstance(raw_num, int) and not isinstance(raw_num, bool):
        old_num = raw_num
    else:
        raise ValueError(
            f"supersede intent: predecessor {old_id} has malformed "
            f"revision_number {raw_num!r}")

    journal = {
        "journal_version": SUPERSEDE_JOURNAL_VERSION,
        "journal_format": "ancestry_v2",
        "operation": "supersede_proposal",
        "owner": owner,
        "old_id": old_id,
        "new_id": new_id,
        "phase": "prepared",
        "old_nursery_sha256": _sha256_file_absent(owner_nursery_path(owner)),
        "old_program_sha256": _sha256_file_absent(_path(owner)),
        # F6: Intent-fixed ancestry evidence, normalized, strictly typed.
        "intent_old_root": old_root,
        "intent_old_number": old_num,
    }
    atomic_write_json(_supersede_journal_path(owner), journal)


def clear_supersede_intent(owner: str) -> None:
    """Delete the supersession journal after successful commit."""
    try:
        os.unlink(_supersede_journal_path(owner))
    except OSError:
        pass


def _validate_durable_program(pdata: dict, context: str) -> dict:
    """Validate reread Program structure with strict member validator.

    F7: Post-heal/repair rereads must validate the complete state with the
    same strict validator before clearing. Returns the validated units dict.

    Raises RollbackRecoveryError if plane is not a dict or units is not
    a dict. Journal preserved.
    """
    if not isinstance(pdata, dict):
        raise RollbackRecoveryError(
            f"supersede intent: {context}: program not a dict (preserved)")
    plane = pdata.get("plane")
    if not isinstance(plane, dict):
        raise RollbackRecoveryError(
            f"supersede intent: {context}: bad plane (preserved)")
    units = plane.get("units")
    if not isinstance(units, dict):
        raise RollbackRecoveryError(
            f"supersede intent: {context}: bad units (preserved)")
    return units


def _validate_revision_identity(old_prop: dict, new_prop: dict, old_id: str,
                                intent_old_root=None, intent_old_number=None) -> None:
    """Validate revision identity using canonical semantics.

    Strict type contract (no coercion):
    - revision_root_id must be str (non-empty) or None/absent
    - revision_number must be int (not bool, not float, not str) or None/absent

    F6: Uses intent-fixed ancestry evidence (normalized at intent-write time:
    root=old_id and number=1 for verified first revision) as the canonical
    reference. The current old's normalized root/number must match the
    intent exactly. This prevents paired unrelated roots from passing.

    The successor's root must equal the canonical root. The successor's
    number must be exactly old's number + 1, using strict integer
    arithmetic (no int() coercion of floats/strings).

    Raises RollbackRecoveryError on any contradiction. Journal preserved.
    """
    old_root = old_prop.get("revision_root_id")
    new_root = new_prop.get("revision_root_id")

    # Strict type: root must be str or None
    if old_root is not None:
        if not isinstance(old_root, str) or not old_root:
            raise RollbackRecoveryError(
                "supersede intent: invalid old revision root type (preserved).")
    if not isinstance(new_root, str) or not new_root:
        raise RollbackRecoveryError(
            "supersede intent: missing or invalid new revision root (preserved).")

    # F6: Normalize current old using the same canonical contract the
    # writer uses (root defaults to own ID). Must match intent exactly.
    # intent_old_root/intent_old_number are required (validated by caller).
    normalized_old_root = old_root if old_root is not None else old_id
    if normalized_old_root != intent_old_root:
        raise RollbackRecoveryError(
            f"supersede intent: old root {normalized_old_root} does not match "
            f"intent-recorded root {intent_old_root} (preserved).")
    canonical_root = intent_old_root

    if new_root != canonical_root:
        raise RollbackRecoveryError(
            f"supersede intent: revision root {new_root} does not match "
            f"canonical root {canonical_root} (preserved)."
        )

    old_num = old_prop.get("revision_number")
    new_num = new_prop.get("revision_number")

    # Strict type: numbers must be int (not bool), or None (defaults to 1)
    # No float, no string, no coercion.
    def _strict_int(val, name):
        if val is None:
            return 1
        if isinstance(val, bool) or not isinstance(val, int):
            raise RollbackRecoveryError(
                f"supersede intent: {name} must be int, got {type(val).__name__} (preserved).")
        return val

    canonical_old_num = _strict_int(old_num, "old revision_number")
    canonical_new_num = _strict_int(new_num, "new revision_number")
    # new_num was None → defaults to 1, but new must have explicit number
    if new_num is None:
        raise RollbackRecoveryError(
            "supersede intent: missing new revision number (preserved).")

    # F6: Old's number must match intent-fixed evidence exactly.
    # intent_old_number is required (validated by caller).
    if canonical_old_num != intent_old_number:
        raise RollbackRecoveryError(
            f"supersede intent: old number {canonical_old_num} does not match "
            f"intent-recorded number {intent_old_number} (preserved).")

    if canonical_new_num != canonical_old_num + 1:
        raise RollbackRecoveryError(
            f"supersede intent: revision number not sequential "
            f"({canonical_old_num} -> {canonical_new_num}) (preserved)."
        )


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
    # F4: Strict version check - exclude bool (True == 1 in Python)
    jv = journal.get("journal_version")
    if not isinstance(jv, int) or isinstance(jv, bool) or jv != SUPERSEDE_JOURNAL_VERSION:
        raise RollbackRecoveryError("supersede intent: bad version (preserved)")
    if journal.get("owner") != owner:
        raise RollbackRecoveryError("supersede intent: owner mismatch (preserved)")
    if journal.get("operation") != "supersede_proposal":
        raise RollbackRecoveryError("supersede intent: bad operation (preserved)")
    if journal.get("phase") != "prepared":
        raise RollbackRecoveryError("supersede intent: bad phase (preserved)")
    # F6: Require ancestry_v2 format explicitly. Old-format journals (missing
    # journal_format) are preserved, not silently reinterpreted: without
    # verified intent-fixed ancestry, recovery cannot prove the outcome.
    if journal.get("journal_format") != "ancestry_v2":
        raise RollbackRecoveryError(
            "supersede intent: old journal format without verified ancestry "
            "(preserved; not reinterpreted)")
    _ior = journal.get("intent_old_root")
    if not isinstance(_ior, str) or not _ior:
        raise RollbackRecoveryError(
            "supersede intent: missing or invalid intent_old_root (preserved)")
    _ion = journal.get("intent_old_number")
    if not isinstance(_ion, int) or isinstance(_ion, bool):
        raise RollbackRecoveryError(
            "supersede intent: missing or invalid intent_old_number (preserved)")

    old_id = journal.get("old_id")
    new_id = journal.get("new_id")
    if not isinstance(old_id, str) or not old_id:
        raise RollbackRecoveryError("supersede intent: bad old_id (preserved)")
    if not isinstance(new_id, str) or not new_id:
        raise RollbackRecoveryError("supersede intent: bad new_id (preserved)")
    # F4: Validate fingerprint fields are present with valid values.
    # Legitimate values: 64-char hex SHA-256 (file existed) or "absent"
    # (file didn't exist, via _sha256_file_absent). Missing/None/empty
    # fail closed - do not accept incomplete schema.
    import re
    _sha256_re = re.compile(r'^[0-9a-f]{64}$')
    for fp_key in ("old_nursery_sha256", "old_program_sha256"):
        fp_val = journal.get(fp_key)
        if fp_val == "absent":
            continue  # Legitimate explicit absence
        if not isinstance(fp_val, str) or not _sha256_re.match(fp_val):
            raise RollbackRecoveryError(
                f"supersede intent: missing or invalid {fp_key} (preserved)")

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

    # Check if BOTH members were modified.
    # Must verify Program as well as Nursery before claiming no_change.
    # Do not clear intent merely because a proposal is absent/pending.
    current_nursery_fp = _sha256_file(npath)
    current_program_fp = _sha256_file(ppath)
    if (current_nursery_fp == journal.get("old_nursery_sha256") and
        current_program_fp == journal.get("old_program_sha256")):
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
        # Validate revision identity before accepting complete NEW.
        _validate_revision_identity(old_prop, new_prop, old_id,
            intent_old_root=journal.get("intent_old_root"),
            intent_old_number=journal.get("intent_old_number"))
        clear_supersede_intent(owner)
        return "already_complete"

    # Before link commit: predecessor active, successor confirmed with durable Idea.
    # This is a permitted intermediate state ONLY if:
    # - Predecessor lifecycle is valid "active" (not None; None is malformed)
    # - Successor is confirmed with durable Idea
    # - NEITHER proposal carries supersession links (no superseded_by_id, no supersedes_id)
    # If links exist (one-way or contradictory) → fail closed, preserve evidence.
    old_active_valid = (
        isinstance(old_prop, dict)
        and old_prop.get("lifecycle_state") == "active"
        # Explicit None is malformed, not legacy. Must be "active".
    )
    # Check for any supersession links (incomplete relationship)
    old_has_link = isinstance(old_prop, dict) and old_prop.get("superseded_by_id") is not None
    new_has_link = isinstance(new_prop, dict) and new_prop.get("supersedes_id") is not None
    if new_ok and old_active_valid:
        if old_has_link or new_has_link:
            # Contradictory: active predecessor but links present → fail closed
            raise RollbackRecoveryError(
                "supersede intent: active predecessor with supersession links "
                "(journal preserved). Contradictory state."
            )
        # Valid pre-commit: no links, predecessor active, successor confirmed.
        # Accept as-is, clear journal.
        clear_supersede_intent(owner)
        return "already_complete"

    # If successor and predecessor are both in correct states but links
    # are incomplete, repair ONLY the revision links (not derivation chain).
    # R3-COMPLETE-EXISTING-CONTRACT req. 2: Supersession uses supersedes_id
    # and superseded_by_id, with revision root and number. Do NOT add
    # revision ancestry to derivation chain. The two relationship types
    # remain distinct.
    if new_ok and old_ok and not links_ok:
        # Validate full revision identity before repairing links.
        # Do not repair if identity is contradictory or missing.
        _validate_revision_identity(old_prop, new_prop, old_id,
            intent_old_root=journal.get("intent_old_root"),
            intent_old_number=journal.get("intent_old_number"))
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
        # Reread durable Nursery (not ndata in memory) and validate
        # saved identities and reciprocal links against Program/journal
        # before clearing intent. Checking ndata proves memory, not persistence.
        try:
            with open(npath, encoding="utf-8") as f:
                durable_nd = json.load(f)
            with open(ppath, encoding="utf-8") as f:
                durable_pd = json.load(f)
        except Exception as exc:
            raise RollbackRecoveryError(
                f"supersede intent: reread after repair failed (preserved): {exc}"
            ) from exc
        durable_old = durable_nd.get(old_id)
        durable_new = durable_nd.get(new_id)
        if not isinstance(durable_old, dict) or not isinstance(durable_new, dict):
            raise RollbackRecoveryError(
                "supersede intent: repaired members missing from durable Nursery "
                "(preserved)."
            )
        # Validate reciprocal links in durable state
        if durable_old.get("superseded_by_id") != new_id:
            raise RollbackRecoveryError(
                "supersede intent: durable old link not repaired (preserved)."
            )
        if durable_new.get("supersedes_id") != old_id:
            raise RollbackRecoveryError(
                "supersede intent: durable new link not repaired (preserved)."
            )
        # Validate revision identity in durable state
        _validate_revision_identity(durable_old, durable_new, old_id,
            intent_old_root=journal.get("intent_old_root"),
            intent_old_number=journal.get("intent_old_number"))
        # F7: Validate successor Idea still present in durable Program.
        # Use strict member validator on reread.
        durable_units = _validate_durable_program(durable_pd, "after repair")
        if new_id not in durable_units:
            raise RollbackRecoveryError(
                "supersede intent: successor Idea missing from durable Program "
                "after repair (preserved)."
            )
        clear_supersede_intent(owner)
        return "already_complete"

    # Incomplete: heal to OLD.
    # Aborted persistence: new may not exist or is pending, old is active.
    # This is the OLD state; clear journal.
    new_absent_or_pending = (
        new_prop is None or
        (isinstance(new_prop, dict) and new_prop.get("status") == "pending")
    )
    if new_absent_or_pending and old_active_valid:
        # Operation never completed. But verify no successor Idea remains.
        # If Idea exists, this is evidence that must be preserved, not cleared.
        if new_id in units:
            raise RollbackRecoveryError(
                "supersede intent: successor Idea present but proposal not confirmed "
                "(journal preserved). Cannot clear as healed."
            )
        # F7: Reject contradictory links. If old has successor link or new
        # has predecessor link, this is not a clean OLD state. Fail closed.
        if isinstance(old_prop, dict) and old_prop.get("superseded_by_id") is not None:
            raise RollbackRecoveryError(
                "supersede intent: old has successor link but is active "
                "(journal preserved). Contradictory state."
            )
        if isinstance(new_prop, dict) and new_prop.get("supersedes_id") is not None:
            raise RollbackRecoveryError(
                "supersede intent: pending new has predecessor link "
                "(journal preserved). Contradictory state."
            )
        # No Idea, no links, old active, new absent/pending → true OLD state.
        clear_supersede_intent(owner)
        return "healed_to_old"

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
        # F7: Reread durable Nursery and verify the heal before clearing.
        # Do not clear intent based on in-memory state alone.
        try:
            with open(npath, encoding="utf-8") as f:
                durable_nd = json.load(f)
        except Exception as exc:
            raise RollbackRecoveryError(
                f"supersede intent: reread after heal failed (preserved): {exc}"
            ) from exc
        durable_old = durable_nd.get(old_id)
        durable_new = durable_nd.get(new_id)
        # Verify old is active in durable state
        if not isinstance(durable_old, dict):
            raise RollbackRecoveryError(
                "supersede intent: old missing from durable Nursery after heal "
                "(preserved).")
        if durable_old.get("lifecycle_state") != "active":
            raise RollbackRecoveryError(
                "supersede intent: old not active in durable Nursery after heal "
                "(preserved).")
        if durable_old.get("superseded_by_id") is not None:
            raise RollbackRecoveryError(
                "supersede intent: old still has successor link after heal "
                "(preserved).")
        # Verify new is pending or absent in durable state
        if isinstance(durable_new, dict):
            if durable_new.get("status") != "pending":
                raise RollbackRecoveryError(
                    "supersede intent: new not pending in durable Nursery after heal "
                    "(preserved).")
            if durable_new.get("supersedes_id") is not None:
                raise RollbackRecoveryError(
                    "supersede intent: new still has predecessor link after heal "
                    "(preserved).")
        # Verify no successor Idea in durable Program
        try:
            with open(ppath, encoding="utf-8") as f:
                durable_pd = json.load(f)
        except Exception as exc:
            raise RollbackRecoveryError(
                f"supersede intent: reread Program after heal failed (preserved): {exc}"
            ) from exc
        # F7: Use strict member validator on reread. Malformed units
        # (e.g., []) fail closed with journal preserved.
        durable_units = _validate_durable_program(durable_pd, "after heal")
        if new_id in durable_units:
            raise RollbackRecoveryError(
                "supersede intent: successor Idea present in durable Program "
                "after heal (preserved).")
        clear_supersede_intent(owner)
        return "healed_to_old"

    # Cannot prove safe heal; preserve journal and fail closed.
    raise RollbackRecoveryError(
        "supersede intent: incomplete transition, cannot safely heal (preserved)"
    )
