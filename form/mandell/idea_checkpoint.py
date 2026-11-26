#!/usr/bin/env python3
"""Idea checkpoint integration — GDP-001 Phase 1, MF-5 resolution.

Integrates canonical Idea state with Phase-0 checkpoint/rollback WITHOUT
creating a second checkpoint system and WITHOUT weakening Phase-0.

Seam: Ideas are snapshotted to a single owner-scoped file
(`ideas_{owner}.json`) which becomes a third member of the Phase-0
journaled transaction (program + nursery + ideas).

On checkpoint: the snapshot is written atomically, then sealed.
On rollback: the snapshot is restored, then individual idea files
are rehydrated from it.

This preserves:
- Phase-0 sealed-generation authority (no bypass)
- Journaled transaction guarantees (no hybrids)
- Fail-closed recovery (existing machinery)
"""

from __future__ import annotations

import json
import os
from typing import Dict, List

from form.dell_matrix.atomic_write import atomic_write_json
from form.persist import _STATE_DIR, _safe_owner


class CheckpointError(Exception):
    """Local checkpoint error (avoids import cycle with checkpoint_generation)."""
    pass


def ideas_snapshot_path(owner: str) -> str:
    """Single-file snapshot of all Ideas for an owner."""
    return os.path.join(_STATE_DIR, f"ideas_{_safe_owner(owner)}.json")


def ideas_rehydrate_marker_path(owner: str) -> str:
    """Marker for an interrupted rehydration (R2, NULL N2).

    Present => a rehydration from the live canonical snapshot did not
    complete. The next reader must complete it before observing state.
    """
    return os.path.join(_STATE_DIR, f"ideas_rehydrate_{_safe_owner(owner)}.pending")


def rehydrate_ideas_from_live(owner: str) -> None:
    """Guarded rehydration of individual idea files from the live canonical
    snapshot (R2, ARGUS MF-R2-1).

    Marker-based and idempotent. A crash mid-rehydration leaves the marker;
    the next reader completes it via ensure_ideas_rehydrated before
    observing state. No-op if the live snapshot is absent.
    """
    live_snap = ideas_snapshot_path(owner)
    if not os.path.isfile(live_snap):
        return
    marker = ideas_rehydrate_marker_path(owner)
    atomic_write_json(marker, {"owner": owner, "phase": "pending"})
    try:
        restore_ideas_from_snapshot(owner, live_snap)
    except Exception:
        # Marker stays: the next reader will retry from the snapshot.
        raise
    if os.path.isfile(marker):
        os.remove(marker)


def ensure_ideas_rehydrated(owner: str) -> None:
    """Complete any interrupted rehydration from the live canonical snapshot.

    Idempotent. Fail-closed: if the marker exists but the live snapshot
    is missing, refuse to guess.
    """
    marker = ideas_rehydrate_marker_path(owner)
    if not os.path.isfile(marker):
        return
    snap = ideas_snapshot_path(owner)
    if not os.path.isfile(snap):
        raise CheckpointError(
            f"ideas rehydration marker present for {owner!r} but live "
            f"snapshot missing; refusing to guess"
        )
    restore_ideas_from_snapshot(owner, snap)
    os.remove(marker)


def snapshot_ideas(owner: str) -> str:
    """Atomically snapshot all Ideas to the owner file.

    Returns the snapshot path. This file is a checkpoint member.

    R2: records per-idea validation and a skip manifest. Structural
    failures are recorded (not silently dropped).
    """
    from form.mandell.idea_persist import scan_idea_files, _idea_path
    from form.mandell.idea import Idea

    # R2 (PRISM R2-P1): never bake a partially-rehydrated working set into
    # a new sealed generation. Complete any pending rehydration first.
    ensure_ideas_rehydrated(owner)

    # Critic F4 (Director ruling 7181902882): the snapshot is judged
    # against a FULL inventory accounting, never against the legacy
    # readable-only ID list. Every idea file is accounted by filename:
    # healthy files are included; unreadable, undecodable, or
    # structurally invalid files are recorded in ``skipped`` keyed by
    # filename (their id is unknowable — that is the point) and marked
    # "refused" in the accounted-files manifest (``files``). The seal
    # refuses any snapshot whose ``skipped`` is non-empty.
    ideas_data = {}
    skipped = []
    files_manifest = {}
    for entry in scan_idea_files(owner):
        fn = entry["file"]
        if entry["error"] is not None:
            skipped.append({"file": fn, "error": entry["error"]})
            files_manifest[fn] = {
                "disposition": "refused", "error": entry["error"]}
            continue
        idea_id = entry["id"]
        path = _idea_path(idea_id, owner)
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            # Structural validation: Idea.from_dict must accept it.
            Idea.from_dict(data)
            ideas_data[idea_id] = data
            files_manifest[fn] = {"disposition": "included", "id": idea_id}
        except (OSError, json.JSONDecodeError, UnicodeDecodeError,
                ValueError, KeyError) as exc:
            skipped.append({"id": idea_id, "file": fn,
                            "error": str(exc)[:120]})
            files_manifest[fn] = {
                "disposition": "refused", "id": idea_id,
                "error": str(exc)[:120]}

    snapshot = {
        "owner": owner,
        "ideas": ideas_data,
        "skipped": skipped,
        "files": files_manifest,
    }
    path = ideas_snapshot_path(owner)
    atomic_write_json(path, snapshot)
    return path


def _probe_idea_file(path: str):
    """Validate one on-disk idea file at restore time.

    Returns ``(idea_id, None)`` for a validated idea file (reads,
    decodes, parses, and ``Idea.from_dict`` accepts it — the same
    standard ``load_idea`` enforces) or ``(None, reason)`` for
    anything else. Used by the restore preflight to decide what may
    be overwritten or deleted and what must be preserved.
    """
    from form.mandell.idea import Idea

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return None, f"unreadable: {exc}"[:120]
    if not isinstance(data, dict) or not isinstance(data.get("id"), str):
        return None, "structurally invalid: not an idea object with a string id"
    try:
        Idea.from_dict(data)
    except Exception as exc:
        return None, f"structurally invalid: {exc}"[:120]
    return data["id"], None


def _manifest_valid(manifest) -> bool:
    """Shape check for a snapshot's accounted-files manifest.

    A present-but-malformed manifest is never a legacy snapshot
    (Director ruling 7181902882): the caller refuses the restore
    rather than falling back to manifest-less rules.
    """
    if not isinstance(manifest, dict):
        return False
    for fn, rec in manifest.items():
        if not isinstance(fn, str) or not isinstance(rec, dict):
            return False
        if rec.get("disposition") not in ("included", "refused"):
            return False
        if rec["disposition"] == "included" and not isinstance(rec.get("id"), str):
            return False
    return True


def restore_ideas_from_snapshot(owner: str, snapshot_path: str) -> None:
    """Restore individual idea files from a snapshot.

    Called during rollback eager convergence.

    R2 (PRISM R2-P1): WRITE-THEN-DELETE. All target files are written
    FIRST, then stale files deleted. An interruption leaves a superset
    (stale extras, no data loss) rather than a partial target. Stale
    files have IDs not in the snapshot and can be garbage-collected;
    load_idea of a stale ID still works (it is a complete idea file),
    so the reader never observes missing data.

    Critic F4 (Director ruling 7181902882): deletion and overwrite are
    preservation-bound. A PREFLIGHT classifies every divergence
    BEFORE any file is modified:

    - A target path whose current bytes are damaged (unreadable or
      not a validated file for that idea) is PRESERVED — never
      overwritten by the snapshot's healthy copy.
    - An extra file is deleted ONLY when proven disposable: a
      validated idea whose ID matches its canonical filename and is
      absent from the snapshot (normal stale cleanup, both snapshot
      vintages), or a file the snapshot's accounted-files manifest
      explicitly records as "included" under the same ID its current
      bytes validate to (its content survives inside the snapshot).
      A manifest entry of "refused", a damaged file, or a file no
      accounting covers is PRESERVED. Absence from a capture-time
      manifest never by itself proves a later addition disposable.
    - A present-but-malformed manifest refuses the restore outright;
      it never triggers the legacy (manifest-less) rules.

    Any preserved file prevents exact convergence: the preflight
    raises CheckpointError naming every preserved file, NO file has
    been modified, and recovery state (rehydration markers, rollback
    journals) is left in place for a safe retry after an operator
    repairs or removes the named files.
    """
    from form.mandell.idea_persist import _idea_path, _idea_dir

    with open(snapshot_path, encoding="utf-8") as f:
        snapshot = json.load(f)
    if not isinstance(snapshot, dict):
        raise ValueError("rollback: ideas snapshot member is not an object")

    ideas_data = snapshot.get("ideas", {})
    if not isinstance(ideas_data, dict):
        raise ValueError("rollback: ideas snapshot member has invalid structure")

    manifest = None
    if "files" in snapshot:
        manifest = snapshot["files"]
        if not _manifest_valid(manifest):
            raise CheckpointError(
                f"ideas restore refused for {owner!r}: the snapshot's "
                "accounted-files manifest is malformed; refusing to "
                "fall back to legacy cleanup rules"
            )

    idea_dir = _idea_dir(owner)
    os.makedirs(idea_dir, exist_ok=True)

    target_ids = set(ideas_data.keys())
    target_files = {os.path.basename(_idea_path(iid, owner)): iid
                    for iid in target_ids}

    # ---- Preflight: classify every divergence before modifying. ----
    preserved = []
    deletable = []
    for fn in sorted(os.listdir(idea_dir)):
        if not (fn.startswith("idea_") and fn.endswith(".json")):
            continue
        path = os.path.join(idea_dir, fn)
        if fn in target_files:
            # Overwrite candidate: the current bytes must be a
            # validated file for THIS idea. Damaged bytes at a target
            # path are preserved, never overwritten.
            cur_id, cur_err = _probe_idea_file(path)
            if cur_err is not None or cur_id != target_files[fn]:
                preserved.append(
                    (fn, "damaged file at a snapshot target path"))
            continue
        # Extra file (not a restore target).
        if (manifest is not None and fn in manifest
                and manifest[fn].get("disposition") == "refused"):
            preserved.append(
                (fn, "file the snapshot refused at capture time"))
            continue
        cur_id, cur_err = _probe_idea_file(path)
        if cur_err is not None:
            preserved.append((fn, f"unaccounted damaged file ({cur_err})"))
            continue
        if (os.path.basename(_idea_path(cur_id, owner)) == fn
                and cur_id not in target_ids):
            # Normal stale cleanup: a validated idea, at its canonical
            # filename, absent from the snapshot.
            deletable.append(fn)
        elif (manifest is not None and fn in manifest
                and manifest[fn].get("disposition") == "included"
                and manifest[fn].get("id") == cur_id):
            # Explicit accounting permits deletion: the file's full
            # content is captured inside the snapshot under this ID.
            deletable.append(fn)
        else:
            preserved.append(
                (fn, "healthy file not proven disposable "
                     "(id/filename mismatch or duplicate)"))
    if preserved:
        raise CheckpointError(
            f"ideas restore refused for {owner!r}: preserved file(s) "
            "prevent exact rollback: "
            + "; ".join(f"{fn} ({reason})" for fn, reason in preserved)
            + ". No files were modified; repair or remove the named "
            "file(s) and retry."
        )

    # 1. Write all target files FIRST (each atomic via atomic_write_json).
    for idea_id, data in ideas_data.items():
        path = _idea_path(idea_id, owner)
        atomic_write_json(path, data)

    # 2. Delete proven-disposable stale files AFTER targets written.
    for fn in deletable:
        os.remove(os.path.join(idea_dir, fn))

    # 3. R2 (NULL N2): post-rehydration verification. Every snapshot ID
    # must have its file present, and the file count must match (no
    # extras). Any mismatch fails closed rather than leaving a silently
    # divergent working set. (Filenames embed a hash of the ID, so we
    # verify via _idea_path rather than filename parsing.)
    files = [fn for fn in os.listdir(idea_dir)
             if fn.startswith("idea_") and fn.endswith(".json")]
    if len(files) != len(target_ids):
        raise CheckpointError(
            f"ideas rehydration verification failed for {owner!r}: "
            f"{len(files)} files != {len(target_ids)} snapshot ideas"
        )
    for idea_id in target_ids:
        if not os.path.isfile(_idea_path(idea_id, owner)):
            raise CheckpointError(
                f"ideas rehydration verification failed for {owner!r}: "
                f"idea {idea_id!r} file missing after restore"
            )
