"""Persistence V2: crash-safe JSON file replacement (DCC-XVII).

Contract
--------
A save exposes, after interruption, either the PREVIOUS COMPLETE
generation or the NEW COMPLETE generation. Never a partially serialized
generation presented as valid state.

Save sequence (``atomic_write_json``):
    1. Serialize the complete JSON payload FIRST, before touching the target.
       Serialization failure leaves the existing target untouched.
    2. Write a sibling temporary file in the SAME directory/filesystem as
       the target (collision-safe name; never interpreted as canonical state).
    3. flush() the temp file, then os.fsync() it.
    4. Atomically replace the target with os.replace(temp, target)
       (atomic same-filesystem rename on POSIX and Windows).
    5. Best-effort fsync() of the parent directory so the rename itself is
       durable where the platform supports it. Degradation is explicit:
       when directory fsync is unavailable the save still succeeds and the
       caller can observe ``dir_fsynced=False``.

Guarantees actually provided (no more, no less):
    - No torn canonical file: readers of ``path`` see only complete
      generations written by this helper.
    - fsync boundaries are exactly the two above; no claim of hardware
      power-loss immunity beyond what the OS/filesystem honors for fsync,
      and no multi-host coordination.
    - Not a database: no transactions across multiple files, no consensus.

Recovery contract:
    Atomic replacement alone is sufficient for the crash-safety contract,
    so NO backup generation is introduced (a backup would add a second
    writer path and a stale-resurrection risk). Precedence on load is:
        valid canonical -> load it
        else -> explicit, honest load failure
    Corrupt canonical state is never silently replaced with empty state and
    never silently "recovered" from an arbitrary generation.

Temp-file contract:
    - Same directory as the target (same filesystem -> os.replace is atomic).
    - Name: ``<basename>.dmtmp.<pid>.<rand8>``; the ``.dmtmp.`` infix marks
      helper-owned temps so stale ones can be swept.
    - The loader reads ONLY the exact canonical path; a temp can never
      masquerade as canonical state.
    - Best-effort unlink on ordinary failure. A hard crash may leave a stale
      temp; loaders ignore it. ``sweep_stale_tmps()`` removes helper-owned
      temps whose writer pid is no longer alive.

persistence_protocol_version = 2 marks the WRITE MECHANICS. The JSON schema
is unchanged from V1, so valid V1 files load without migration and the next
successful save simply uses V2 mechanics.

Test hooks (same convention as supersession._FAIL_AT):
    _FAIL_AT may be set to one of:
        "serialize"            raise before serialization (target untouched)
        "temp_write"           write a partial temp, then raise (no cleanup,
                               to simulate a hard mid-write failure)
        "replace"              raise after temp fsync, before os.replace
        "dir_fsync_fail"       force the directory-fsync fallback path
        "crash_before_replace" os._exit(42) after temp fsync, before replace
        "crash_after_replace"  os._exit(42) immediately after os.replace
        "slow_write"           write the temp in small chunks with sleeps
                               (lets a test harness SIGKILL mid-write)
"""
from __future__ import annotations

import json
import os
import uuid
from typing import Any, Dict, Optional

PERSISTENCE_PROTOCOL_VERSION = 2

#: Infix identifying temp files owned by this helper.
TMP_INFIX = ".dmtmp."

#: Test-only failure injection (see module docstring). Production leaves None.
_FAIL_AT: Optional[str] = None


class AtomicWriteError(OSError):
    """Honest failure of an atomic write; the canonical target was not replaced."""


def _fail_at() -> Optional[str]:
    return _FAIL_AT


def _temp_path_for(target: str) -> str:
    directory = os.path.dirname(os.path.abspath(target))
    base = os.path.basename(target)
    return os.path.join(
        directory,
        f"{base}{TMP_INFIX}{os.getpid()}.{uuid.uuid4().hex[:8]}",
    )


def _fsync_dir(dirpath: str, *, force_fail: bool = False) -> bool:
    """fsync the directory entry so the rename is durable. Returns True when
    the fsync actually happened; False when the platform cannot do it
    (explicit degradation, never silent)."""
    if force_fail:
        return False
    open_dir = getattr(os, "O_DIRECTORY", None)
    if open_dir is None:
        return False
    try:
        fd = os.open(dirpath, os.O_RDONLY | open_dir)
    except OSError:
        return False
    try:
        os.fsync(fd)
        return True
    except OSError:
        return False
    finally:
        try:
            os.close(fd)
        except OSError:
            pass


def atomic_write_json(path: str, payload: Any, *, _fail_at: Optional[str] = None) -> bytes:
    """Serialize ``payload`` to JSON and atomically replace ``path`` with it.

    Returns the exact bytes written (callers use them for signature caches).
    Raises AtomicWriteError (or the injected failure) WITHOUT replacing the
    target whenever anything fails before the os.replace boundary.
    """
    fail = _fail_at if _fail_at is not None else _FAIL_AT

    # Phase C: complete serialization BEFORE touching the existing target.
    if fail == "serialize":
        raise AtomicWriteError("injected serialization failure (target untouched)")
    try:
        text = json.dumps(payload, indent=2)
    except (TypeError, ValueError) as exc:
        raise AtomicWriteError(f"serialization failed; target untouched: {exc}") from exc
    blob = text.encode("utf-8")

    directory = os.path.dirname(os.path.abspath(path))
    try:
        os.makedirs(directory, exist_ok=True)
    except OSError as exc:
        raise AtomicWriteError(f"cannot create directory for {path}: {exc}") from exc

    tmp = _temp_path_for(path)
    dir_fsynced = False
    try:
        # Phase D: sibling temp, same directory/filesystem.
        try:
            fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        except OSError as exc:
            raise AtomicWriteError(f"cannot create temp file for {path}: {exc}") from exc
        try:
            with os.fdopen(fd, "wb") as f:
                if fail == "temp_write":
                    # Partial write, then hard failure WITHOUT cleanup: this
                    # simulates a crash mid-write; the temp must never be
                    # mistaken for canonical state.
                    f.write(blob[: max(1, len(blob) // 2)])
                    f.flush()
                    raise AtomicWriteError("injected temp-write failure (partial temp left)")
                if fail == "slow_write":
                    chunk = 65536
                    for i in range(0, len(blob), chunk):
                        f.write(blob[i : i + chunk])
                        f.flush()
                        import time as _t

                        _t.sleep(0.02)
                else:
                    f.write(blob)
                f.flush()
                os.fsync(f.fileno())
        except BaseException:
            # Ordinary failure: best-effort cleanup of OUR temp. The injected
            # "temp_write" path raises above and is intentionally left in place.
            if fail != "temp_write":
                try:
                    os.unlink(tmp)
                except OSError:
                    pass
            raise

        if fail == "crash_before_replace":
            os._exit(42)  # noqa: SIO171 - literal process death before replace
        if fail == "replace":
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise AtomicWriteError("injected pre-replace failure (canonical untouched)")

        # Phase E: atomic same-filesystem replacement. Never delete-then-rename.
        try:
            os.replace(tmp, path)
        except OSError as exc:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise AtomicWriteError(f"atomic replace failed; canonical untouched: {exc}") from exc

        if fail == "crash_after_replace":
            os._exit(42)  # noqa: SIO171 - literal process death after replace

        dir_fsynced = _fsync_dir(directory, force_fail=(fail == "dir_fsync_fail"))
        return blob
    finally:
        # Expose the fsync outcome honestly for tests/docs without changing
        # the return contract: stash on the function object is ugly; instead
        # the caller-visible contract is "save succeeded". Directory-fsync
        # degradation is observable via _last_dir_fsynced for audit.
        atomic_write_json._last_dir_fsynced = dir_fsynced  # type: ignore[attr-defined]


# Auditable record of whether the most recent atomic_write_json call managed
# a parent-directory fsync (False = explicit degradation, save still valid).
atomic_write_json._last_dir_fsynced = False  # type: ignore[attr-defined]


def sweep_stale_tmps(directory: str) -> Dict[str, int]:
    """Remove helper-owned temp files whose writer pid is no longer alive.

    Returns {"scanned": n, "removed": m}. Never touches the canonical file or
    any temp whose pid is still running (a live concurrent writer).
    """
    scanned = removed = 0
    try:
        names = os.listdir(directory)
    except OSError:
        return {"scanned": 0, "removed": 0}
    for name in names:
        if TMP_INFIX not in name:
            continue
        scanned += 1
        # name pattern: <base>.dmtmp.<pid>.<rand8>
        try:
            pid = int(name.split(TMP_INFIX, 1)[1].split(".", 1)[0])
        except (ValueError, IndexError):
            continue
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            dead = True
        except PermissionError:
            dead = False  # pid exists but not ours; leave it alone
        except OSError:
            dead = False
        else:
            dead = False
        if not dead:
            continue
        try:
            os.unlink(os.path.join(directory, name))
            removed += 1
        except OSError:
            pass
    return {"scanned": scanned, "removed": removed}
