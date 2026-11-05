"""Owner-state lock — the single concurrency authority for
canonical Program state (TD-1-R2, Director directive 2026-11-04).

One kernel-held lock per owner, taken around the transactions
that validate and replace the owner's canonical state file:
unit binding (form.mandell.unit_binding) and ordinary Program
saves (form.persist_rest.save). Before R2, R1's fingerprint gate
was an optimistic version check — the comparison and the final
replacement were separate moments, and two writers could both
pass the comparison before either saved. The lock closes that
window: validation and replacement happen inside one enforceable
owner-scoped transaction.

Mechanics, chosen against silent downgrade (AGENTS SS31.2):

  * The lock is an flock(2)-style kernel lock on a per-owner lock
    file beside the canonical state file. The file is NEVER
    unlinked: unlinking a lock file splits the lock across inodes
    and silently re-opens the race. Kernel-held means a holder
    that dies — including SIGKILL — releases automatically; there
    is no stale-lock guessing game and no pid-file archaeology.
  * Acquisition is bounded: LOCK_TIMEOUT_S seconds of polling,
    then OwnerLockBusy. An unbounded wait would turn contention
    into a hang; a zero wait would turn normal contention into
    spurious failures. The bound is part of the contract.
  * If no kernel lock mechanism is available on the platform,
    acquisition fails closed with OwnerLockUnavailable — it never
    falls back to running unlocked.
  * Re-entrancy is per process+thread and token-free: the kernel
    lock is held once; nested acquisitions by the same thread
    join by depth count. Different threads/processes contend for
    real.

Same-machine, same-filesystem scope only: no multi-host
coordination is claimed (mirroring atomic_write's own boundary).
"""
from __future__ import annotations

import os
import threading
import time
from contextlib import contextmanager

LOCK_TIMEOUT_S = 10.0
_POLL_S = 0.02

try:
    import fcntl as _fcntl
except ImportError:  # pragma: no cover - non-POSIX platform
    _fcntl = None
try:
    import msvcrt as _msvcrt
except ImportError:  # pragma: no cover - non-Windows platform
    _msvcrt = None


class OwnerLockBusy(Exception):
    """The owner-state lock was still held when the bounded
    acquisition wait expired. Nothing was mutated."""


class OwnerLockUnavailable(Exception):
    """No kernel lock mechanism is available on this platform.
    Raised instead of ever proceeding unlocked."""


_local = threading.local()


def _held() -> dict:
    held = getattr(_local, "held", None)
    if held is None:
        held = {}
        _local.held = held
    return held


def lock_path_for(owner: str) -> str:
    """The lock file for an owner: in the state directory's
    `.locks/` subfolder, named from the canonical state file via
    the same single authority (persist._path). Never unlinked by
    this module. The subfolder keeps owner-cleanup contracts
    intact: suites that remove an owner's `program_<owner>*`
    files are not silently handed a new residue class (found by
    regression, TD-1-R2)."""
    from form.persist import _STATE_DIR, _path
    folder = os.path.join(_STATE_DIR, ".locks")
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder,
                        os.path.basename(_path(owner)) + ".lock")


def _acquire_fd(fd: int, path: str, timeout: float) -> None:
    deadline = time.monotonic() + timeout
    while True:
        try:
            if _fcntl is not None:
                _fcntl.flock(fd, _fcntl.LOCK_EX | _fcntl.LOCK_NB)
                return
            if _msvcrt is not None:
                os.lseek(fd, 0, os.SEEK_SET)
                _msvcrt.locking(fd, _msvcrt.LK_NBLCK, 1)
                return
            raise OwnerLockUnavailable(
                "no kernel lock mechanism (fcntl/msvcrt) available; "
                "refusing to proceed unlocked")
        except BlockingIOError:
            if time.monotonic() >= deadline:
                raise OwnerLockBusy(
                    f"owner-state lock {path!r} still held after "
                    f"{timeout:.1f}s; refusing rather than waiting "
                    f"unboundedly")
            time.sleep(_POLL_S)
        except OSError:
            if time.monotonic() >= deadline:
                raise OwnerLockBusy(
                    f"owner-state lock {path!r} still held after "
                    f"{timeout:.1f}s; refusing rather than waiting "
                    f"unboundedly")
            time.sleep(_POLL_S)


def _release_fd(fd: int) -> None:
    try:
        if _fcntl is not None:
            _fcntl.flock(fd, _fcntl.LOCK_UN)
        elif _msvcrt is not None:
            os.lseek(fd, 0, os.SEEK_SET)
            _msvcrt.locking(fd, _msvcrt.LK_UNLCK, 1)
    finally:
        os.close(fd)


@contextmanager
def owner_state_lock(owner: str, timeout: float = None):
    """Hold the owner's state lock for one transaction.

    Yields the lock path. Raises OwnerLockBusy (bounded wait
    exhausted) or OwnerLockUnavailable (no kernel mechanism) —
    in both cases the caller's transaction must not proceed.
    """
    if timeout is None:
        timeout = LOCK_TIMEOUT_S
    path = lock_path_for(owner)
    held = _held()
    entry = held.get(path)
    if entry is not None:
        entry[1] += 1
        try:
            yield path
        finally:
            entry[1] -= 1
        return
    fd = os.open(path, os.O_CREAT | os.O_RDWR, 0o644)
    try:
        _acquire_fd(fd, path, timeout)
    except BaseException:
        os.close(fd)
        raise
    held[path] = [fd, 1]
    try:
        yield path
    finally:
        held.pop(path, None)
        _release_fd(fd)
