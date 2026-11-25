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
      temps whose writer pid is no longer alive AND whose writer-minted
      provenance record (see below) still binds the file's identity.
    - Provenance: at temp creation the writer appends a durable record
      (name, dev, inode) to a per-directory ledger,
      ``.dmtmp-ledger.jsonl``, and fsyncs it BEFORE any payload byte is
      written, so a crash at any later point leaves a provably
      helper-owned orphan. A successful replace (or an ordinary-failure
      cleanup unlink) appends a consumed tombstone. Filename shape is
      NOT provenance: a file with no binding ledger record is never
      swept (Director rulings 7088554768 and 7088845962).

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
import re
import stat
import time
import uuid
from typing import Any, Callable, Dict, List, Optional

PERSISTENCE_PROTOCOL_VERSION = 2

#: Infix identifying temp files owned by this helper.
TMP_INFIX = ".dmtmp."

#: Test-only failure injection (see module docstring). Production leaves None.
_FAIL_AT: Optional[str] = None

#: Test-only race injection for sweep_stale_tmps (same convention as
#: _FAIL_AT): when set, it is called with a removal candidate's path after
#: classification and immediately before the pre-unlink identity
#: revalidation, letting a test replace the candidate mid-sweep.
#: Production leaves None.
_SWEEP_HOOK: Optional[Callable[[str], None]] = None


class AtomicWriteError(OSError):
    """Honest failure of an atomic write; the canonical target was not replaced."""


class SweepRefusalError(AtomicWriteError):
    """Typed refusal by sweep_stale_tmps: the sweep root itself is unsafe
    (e.g. a symlink), so nothing was scanned for removal and nothing was
    deleted. Per-file ambiguity never raises; it keeps the file and is
    reported with a typed reason instead (see sweep_stale_tmps)."""


class SweepProvenanceError(AtomicWriteError):
    """The provenance ledger's content is structurally unusable
    (Director residual CORRECTION_REQUIRED 7136945087): a record that
    parses as JSON but is not a writer-shaped object — a non-object
    record, a non-string name or op — cannot have come from the
    writer or from a torn append, so the ledger cannot be trusted
    as provenance at all. Raised by _read_provenance; the sweep
    converts it to a SweepRefusalError (nothing removed), never a
    raw exception and never a silent pass. A strict (verification)
    read also raises it when the ledger cannot be obtained at all
    (Director CORRECTION_REQUIRED 7166216637): unavailable evidence
    is not trustworthy absence."""


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

    dir_fsynced = _atomic_replace(path, blob, fail)
    # Expose the fsync outcome honestly for tests/docs without changing
    # the return contract.
    atomic_write_json._last_dir_fsynced = dir_fsynced  # type: ignore[attr-defined]
    return blob


def atomic_write_bytes(path: str, blob: bytes, *, _fail_at: Optional[str] = None) -> bytes:
    """Atomically replace ``path`` with the exact ``blob`` bytes.

    Same Persistence V2 guarantees as :func:`atomic_write_json` (sibling
    temp, O_EXCL, fsync, atomic os.replace, best-effort directory fsync) but
    without serialization: the bytes on disk are byte-identical to ``blob``.
    Used for generation member copies where the fingerprint must bind the
    exact sealed bytes. Raises AtomicWriteError WITHOUT replacing the target
    whenever anything fails before the os.replace boundary.
    """
    fail = _fail_at if _fail_at is not None else _FAIL_AT
    if not isinstance(blob, (bytes, bytearray)):
        raise AtomicWriteError("atomic_write_bytes requires bytes-like input; target untouched")
    blob = bytes(blob)
    if fail == "serialize":
        raise AtomicWriteError("injected serialization failure (target untouched)")

    directory = os.path.dirname(os.path.abspath(path))
    try:
        os.makedirs(directory, exist_ok=True)
    except OSError as exc:
        raise AtomicWriteError(f"cannot create directory for {path}: {exc}") from exc

    dir_fsynced = _atomic_replace(path, blob, fail)
    atomic_write_bytes._last_dir_fsynced = dir_fsynced  # type: ignore[attr-defined]
    return blob


# Auditable record of whether the most recent atomic_write_bytes call managed
# a parent-directory fsync (False = explicit degradation, save still valid).
atomic_write_bytes._last_dir_fsynced = False  # type: ignore[attr-defined]


def _atomic_replace(path: str, blob: bytes, fail: Optional[str]) -> bool:
    """Write ``blob`` to a sibling temp and atomically replace ``path``.

    Shared Persistence V2 machinery. Returns whether the parent-directory
    fsync succeeded (best-effort, honestly reported).
    """
    tmp = _temp_path_for(path)
    dir_fsynced = False
    directory = os.path.dirname(os.path.abspath(path))
    # Phase D: sibling temp, same directory/filesystem.
    try:
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except OSError as exc:
        raise AtomicWriteError(f"cannot create temp file for {path}: {exc}") from exc
    # Durable provenance (Q-35.1 provenance law, 7088845962): record
    # the mint BEFORE any payload byte is written, so a crash at any
    # later point in this call leaves a sweepable orphan. If the
    # record cannot be written the save still proceeds; the temp
    # simply carries no provenance and a later sweep will KEEP it
    # (the safe direction — see _ledger_append).
    tmp_name = os.path.basename(tmp)
    tmp_ino: Optional[int] = None
    try:
        _st0 = os.fstat(fd)
        tmp_ino = _st0.st_ino
        _record_mint(directory, tmp_name, _st0.st_dev, _st0.st_ino)
    except OSError:
        tmp_ino = None
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
    except BaseException as exc:
        # Ordinary failure: best-effort cleanup of OUR temp. The injected
        # "temp_write" path raises above and is intentionally left in place.
        if fail != "temp_write":
            try:
                os.unlink(tmp)
                if tmp_ino is not None:
                    _record_consumed(directory, tmp_name, tmp_ino)
            except OSError:
                pass
        # 72-29 (D3): a real write/fsync OSError must surface as the
        # helper's documented error type, never raw — callers key
        # their abort/convergence handling on AtomicWriteError, and a
        # raw OSError would bypass it. AtomicWriteError itself (incl.
        # the injected temp_write failure) passes through unchanged;
        # non-OSError exceptions (KeyboardInterrupt etc.) are not
        # write failures and propagate as-is.
        if isinstance(exc, AtomicWriteError):
            raise
        if isinstance(exc, OSError):
            raise AtomicWriteError(
                f"atomic write failed; canonical untouched: {exc}") from exc
        raise

    if fail == "crash_before_replace":
        os._exit(42)  # noqa: SIO171 - literal process death before replace
    if fail == "replace":
        try:
            os.unlink(tmp)
            if tmp_ino is not None:
                _record_consumed(directory, tmp_name, tmp_ino)
        except OSError:
            pass
        raise AtomicWriteError("injected pre-replace failure (canonical untouched)")

    # Phase E: atomic same-filesystem replacement. Never delete-then-rename.
    try:
        os.replace(tmp, path)
    except OSError as exc:
        try:
            os.unlink(tmp)
            if tmp_ino is not None:
                _record_consumed(directory, tmp_name, tmp_ino)
        except OSError:
            pass
        raise AtomicWriteError(f"atomic replace failed; canonical untouched: {exc}") from exc
    if tmp_ino is not None:
        # The temp name is consumed: tombstone its mint record so a
        # later file recycling BOTH the name and the inode still
        # carries no provenance.
        _record_consumed(directory, tmp_name, tmp_ino)

    if fail == "crash_after_replace":
        os._exit(42)  # noqa: SIO171 - literal process death after replace

    dir_fsynced = _fsync_dir(directory, force_fail=(fail == "dir_fsync_fail"))
    return dir_fsynced


# Auditable record of whether the most recent atomic_write_json call managed
# a parent-directory fsync (False = explicit degradation, save still valid).
atomic_write_json._last_dir_fsynced = False  # type: ignore[attr-defined]


#: The exact basename shape _temp_path_for mints:
#: ``<base>.dmtmp.<pid>.<rand8>`` with rand8 = 8 lowercase hex chars
#: (uuid4().hex[:8]). A name that does not match this shape in FULL was
#: not minted by this helper, whatever substrings it contains.
_TMP_NAME_RE = re.compile(
    r"^(?P<base>.+)\.dmtmp\.(?P<pid>[0-9]+)\.(?P<rand>[0-9a-f]{8})$")


def _pid_liveness(pid: int) -> Optional[bool]:
    """True = a process with this number exists now; False = proven dead
    (ProcessLookupError); None = unknowable (never probed / probe error).
    Only False may ever lead to removal: a live number may be the writer
    or an unrelated process that reused the number (PID reuse resolves
    to KEEP), and an unknowable answer is ambiguity, which also keeps."""
    if pid <= 0:
        return None
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True  # pid exists but is not ours
    except (OSError, OverflowError):
        return None
    return True


def _identity(st: os.stat_result) -> tuple:
    """The file identity a removal decision is bound to."""
    return (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns)


#: Durable provenance ledger, one per directory that receives helper
#: temps. The name deliberately contains neither TMP_INFIX nor the
#: "*.dmtmp.*" glob shape, so no temp census or sweep scan ever
#: mistakes the ledger for a temp.
PROVENANCE_LEDGER_NAME = ".dmtmp-ledger.jsonl"


def _ledger_append(directory: str, record: Dict[str, Any], *,
                   fsync: bool) -> None:
    """Append one JSON record to the directory's provenance ledger.

    Best-effort BY DESIGN: a ledger failure never fails a save. Its
    only consequence is that the temp it described carries no (or
    stale) provenance, and a later sweep resolves that ambiguity to
    KEEP. The ledger path is opened with O_NOFOLLOW: a symlinked
    ledger is not written through. It is also opened with
    O_NONBLOCK and accepted only if the opened file is a regular
    file (Director CORRECTION_REQUIRED 7136552041): an unsupported
    file type at the ledger path — a FIFO blocks a plain open
    indefinitely — must fail fast so auxiliary bookkeeping can
    never block or corrupt an ordinary save."""
    flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
    flags |= getattr(os, "O_NOFOLLOW", 0)
    flags |= getattr(os, "O_NONBLOCK", 0)
    try:
        fd = os.open(os.path.join(directory, PROVENANCE_LEDGER_NAME),
                     flags, 0o644)
    except OSError:
        return
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            return
        line = (json.dumps(record, separators=(",", ":")) + "\n"
                ).encode("utf-8")
        while line:
            try:
                n = os.write(fd, line)
            except OSError:
                return
            line = line[n:]
        if fsync:
            try:
                os.fsync(fd)
            except OSError:
                pass
    finally:
        try:
            os.close(fd)
        except OSError:
            pass


def _ledger_append_at(dir_fd: int, record: Dict[str, Any], *,
                      fsync: bool) -> bool:
    """Append one JSON record to the ledger of the directory pinned
    by ``dir_fd`` and report success — the fd-relative twin of
    _ledger_append, for callers (the sweep's ownership retirement)
    that must KNOW the append landed and must write through the
    pinned directory, never through a path a swapped root could
    redirect. Same hardening: O_NOFOLLOW, O_NONBLOCK, regular
    files only. Returns False on any failure; the caller resolves
    that ambiguity to KEEP."""
    flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
    flags |= getattr(os, "O_NOFOLLOW", 0)
    flags |= getattr(os, "O_NONBLOCK", 0)
    try:
        fd = os.open(PROVENANCE_LEDGER_NAME, flags, 0o644,
                     dir_fd=dir_fd)
    except OSError:
        return False
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            return False
        line = (json.dumps(record, separators=(",", ":")) + "\n"
                ).encode("utf-8")
        while line:
            try:
                n = os.write(fd, line)
            except OSError:
                return False
            line = line[n:]
        if fsync:
            try:
                os.fsync(fd)
            except OSError:
                return False
        return True
    except OSError:
        return False
    finally:
        try:
            os.close(fd)
        except OSError:
            pass


def _retire_mint(dir_fd: int, name: str, dev: int, ino: int) -> bool:
    """Durably retire the mint record binding ``name`` to (dev, ino),
    through the pinned directory, and PROVE the retirement with a
    fresh ledger read: the tombstone append must be fsynced AND a
    re-read must no longer bind the name to that identity.

    The ledger stays append-only (7136552041): retirement is a
    consumed tombstone, never a rewrite. Returns False whenever
    retirement cannot be established — the caller keeps the
    candidate rather than deleting it over live ownership.

    The proving read is STRICT (Director CORRECTION_REQUIRED
    7166216637): the lenient read returns the same empty dict for a
    successful empty ledger and for an open/fstat/read failure, so
    absence from that dict was not positive proof of retirement —
    a failed re-read silently "proved" a retirement it never
    observed and the candidate was deleted over unavailable
    evidence. The strict read raises SweepProvenanceError on any
    failure to obtain the ledger, and this function resolves that
    to False: retirement UNPROVEN, candidate kept."""
    if not _ledger_append_at(dir_fd,
                             {"v": 1, "op": "consumed", "name": name,
                              "ino": ino},
                             fsync=True):
        return False
    try:
        fresh = _read_provenance(dir_fd, strict=True)
    except SweepProvenanceError:
        return False
    return fresh.get(name) != (dev, ino)


def _record_mint(directory: str, name: str, dev: int, ino: int) -> None:
    """Record, durably (fsync), that THIS writer minted temp ``name``
    with identity (dev, ino). Called at temp creation, before any
    payload byte is written, so the record survives a writer crash
    or SIGKILL at any later point (7088845962)."""
    _ledger_append(directory,
                   {"v": 1, "op": "mint", "name": name, "dev": dev,
                    "ino": ino, "pid": os.getpid()},
                   fsync=True)


def _record_consumed(directory: str, name: str, ino: int) -> None:
    """Tombstone a mint record: the temp name was consumed (replaced
    onto its canonical target, or cleaned up after an ordinary
    failure), so its provenance must not transfer to any later file
    that recycles the name."""
    _ledger_append(directory,
                   {"v": 1, "op": "consumed", "name": name, "ino": ino},
                   fsync=False)


def _read_provenance(dir_fd: int, *, strict: bool = False
                     ) -> Dict[str, tuple]:
    """{name: (dev, ino)} of temps the writer minted and has not
    consumed, from the ledger in the directory pinned by ``dir_fd``.

    Malformed lines are ignored: a torn final append (crash during
    the ledger write itself) degrades to missing provenance, which
    the sweep resolves to KEEP. A symlinked ledger is not read
    through (O_NOFOLLOW); it degrades to no provenance. An
    unsupported file type at the ledger path (a FIFO can block a
    plain open) likewise degrades to no provenance: the read opens
    with O_NONBLOCK and accepts only a regular file (7136552041).

    Structurally unusable content is different from a torn line
    (7136945087): a line that parses as JSON but is not an object,
    or whose name/op is not a string, cannot be writer output or a
    torn append — it raises SweepProvenanceError, the conservative
    typed outcome, and every descriptor opened here is closed on
    every path.

    STRICT mode (``strict=True``, Director CORRECTION_REQUIRED
    7166216637) is the verification read used to PROVE a state of
    the ledger — ownership retirement. The lenient read above
    cannot distinguish a trustworthy absence (a ledger that was
    successfully opened and read, and does not bind a name) from
    unavailable evidence (the open, fstat, file-type check, or
    read failed), because both return the same empty dict. A
    consumer that treats absence as positive proof — retirement
    proven, deletion permitted — fails open on unavailable
    evidence. In strict mode every failure to obtain the ledger
    raises SweepProvenanceError instead: absence is reported only
    when the read actually succeeded. The lenient default is
    unchanged for classification reads, whose consumers resolve
    missing provenance to KEEP."""
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    flags |= getattr(os, "O_NONBLOCK", 0)

    def _unavailable(what: str, exc: Optional[BaseException] = None):
        raise SweepProvenanceError(
            f"provenance ledger unavailable ({what}): "
            f"{PROVENANCE_LEDGER_NAME}") from exc

    try:
        fd = os.open(PROVENANCE_LEDGER_NAME, flags, dir_fd=dir_fd)
    except OSError as exc:
        if strict:
            _unavailable("open failed", exc)
        return {}
    try:
        try:
            opened_mode = os.fstat(fd).st_mode
        except OSError as exc:
            if strict:
                _unavailable("fstat failed", exc)
            return {}
        if not stat.S_ISREG(opened_mode):
            if strict:
                _unavailable("ledger path is not a regular file")
            return {}
        try:
            f = os.fdopen(fd, "rb")
        except OSError as exc:
            if strict:
                _unavailable("fdopen failed", exc)
            return {}
        fd = -1  # descriptor ownership transferred to f
        out: Dict[str, tuple] = {}
        try:
            for raw in f:
                try:
                    rec = json.loads(raw.decode("utf-8"))
                except (ValueError, UnicodeDecodeError):
                    continue
                if not isinstance(rec, dict):
                    raise SweepProvenanceError(
                        f"provenance record is not an object: {rec!r}")
                try:
                    name = rec["name"]
                    ino = int(rec["ino"])
                    op = rec["op"]
                except (ValueError, KeyError, TypeError):
                    continue
                if not isinstance(name, str) or \
                        not isinstance(op, str):
                    raise SweepProvenanceError(
                        f"provenance record has non-string name/op: "
                        f"{rec!r}")
                if op == "mint":
                    try:
                        out[name] = (int(rec["dev"]), ino)
                    except (ValueError, KeyError, TypeError):
                        continue
                elif op == "consumed":
                    if out.get(name, (None, None))[1] == ino:
                        out.pop(name, None)
        except SweepProvenanceError:
            raise
        except OSError as exc:
            if strict:
                _unavailable("read failed", exc)
            return {}
        finally:
            try:
                f.close()
            except OSError:
                pass
        return out
    finally:
        if fd >= 0:
            try:
                os.close(fd)
            except OSError:
                pass


def sweep_stale_tmps(directory: str, *,
                     min_age_seconds: float = 0.0,
                     report: Optional[List[Dict[str, Any]]] = None
                     ) -> Dict[str, int]:
    """Remove helper-owned temp files whose writer pid is no longer alive.

    MANUAL-ONLY: this helper has no production caller and is never
    invoked automatically; removal happens only when an operator (or a
    test) calls it explicitly (Q-35.1, Director ruling 7085151190
    item 7).

    A file is removed ONLY when every check passes, in this order:

    1. Its name matches the exact mint shape ``<base>.dmtmp.<pid>.
       <rand8>`` in full (``_TMP_NAME_RE``), and the base does not
       itself contain the infix. A substring match proves nothing:
       foreign names that merely contain ``.dmtmp.`` are kept with
       reason MALFORMED_NAME.
    2. A directory-fd-relative stat (never following symlinks) shows
       a regular file owned by this process's uid. Symlinks are never
       followed and never unlinked (NOT_A_REGULAR_FILE); another
       owner's file is kept (NOT_OWNER).
    3. The pid is PROVEN dead by two probes (at classification and
       again immediately before unlink). Alive or unknowable keeps
       the file (LIVE_PID / PID_UNPROBEABLE) — the PID-reuse-safe
       direction.
    4. PROVENANCE: the writer's durable ledger record for this exact
       name binds the file's CURRENT (dev, ino). Filename shape and
       uid are not proof of helper origin (7088554768): a same-uid
       foreign file wearing an exact-shaped fabricated name has no
       record and is kept with reason NOT_PROVEN_OWNED, bytes intact.
       A record whose inode does not match the file (recycled name)
       is likewise not provenance.
    5. The file's age meets the caller's grace rail
       (``min_age_seconds``; default 0 preserves the proven
       immediate-sweep contract of the 72-35 suites — the age rail is
       a grace period, never permission to delete an unproven file).
       Younger is kept (TOO_YOUNG).
    6. Identity revalidation: the candidate is re-stated through the
       pinned directory fd before the removal phase proceeds; any
       change of (dev, ino, size, mtime_ns) since classification
       keeps the file (CHANGED_SINCE_SCAN). The unlink itself is
       issued relative to the pinned directory fd, so a swapped or
       renamed sweep root cannot redirect it.
    7. Ownership retirement (7136945087): before the unlink, the
       candidate's mint record is durably retired — a fsynced
       consumed tombstone appended through the pinned directory
       (the ledger stays append-only) and proven by a fresh read
       that no longer binds the name to the candidate's identity.
       The proving read is strict (7166216637): a read failure is
       unavailable evidence, not proof of absence, so retirement
       that cannot be positively proven keeps the candidate
       (RETIREMENT_UNPROVEN). A removal therefore never leaves
       reusable ownership behind: no later file, even one recycling
       the name and inode, can inherit the swept file's provenance.
    8. Post-retirement identity revalidation (7166216637): because
       step 7 itself appends, fsyncs, and re-reads the ledger, the
       step-6 check is not immediately before the unlink — so the
       candidate is re-stated once more after retirement, just
       before the relative removal, and any change of identity in
       the interval keeps the candidate (CHANGED_SINCE_SCAN).

    Removal guarantee, stated exactly: a candidate is unlinked only
    when the writer's own ledger record binds its name to the
    (dev, ino) the file still has at the final (post-retirement)
    revalidation, its pid is proven dead twice, the age rail
    passes, and its mint has been durably retired and the
    retirement proven by a fresh strict read. The ledger is
    durable evidence, not a cryptographic proof: a same-uid actor
    who can rewrite the ledger could forge provenance, so the
    guarantee is "no file is removed without writer-minted
    provenance", not "provenance cannot be forged by the owning
    uid". Temps minted before the provenance law existed carry no
    record and are kept.

    Ambiguity always resolves to KEEP with a typed reason; nothing
    ambiguous is ever deleted. Unlink failures are never swallowed:
    they are reported as REMOVE_FAILED with the error class.

    The sweep root itself must be trustworthy: a symlinked or
    non-directory root raises SweepRefusalError before anything is
    scanned or removed. The root open is identity-pinned to the
    root check (7113892787): it does not follow symlinks
    (O_NOFOLLOW where supported) and the opened fd's fstat
    (dev, ino) must equal the checked lstat identity, so a root
    swapped between check and open — by symlink or by rename — is
    a typed refusal, never a redirected sweep. A missing/unreadable directory keeps the
    proven legacy contract: exactly ``{"scanned": 0, "removed": 0}``,
    no raise (atomic_write_boundaries E3).

    Returns exactly ``{"scanned": n, "removed": m}`` (scanned = names
    containing the infix). When ``report`` is a list, one entry per
    scanned candidate is appended: {"name", "action":
    "removed"|"kept"|"failed", "reason": <typed code or None>,
    "error": <exception class name for REMOVE_FAILED else None>,
    "pid": <int or None>}.
    """
    if os.path.islink(directory):
        raise SweepRefusalError(
            f"sweep refused: root is a symlink, nothing removed: "
            f"{directory!r}")
    try:
        root_st = os.lstat(directory)
    except OSError:
        return {"scanned": 0, "removed": 0}
    if not stat.S_ISDIR(root_st.st_mode):
        raise SweepRefusalError(
            f"sweep refused: root is not a directory, nothing removed: "
            f"{directory!r}")
    # Pin the sweep root with a directory fd: every stat and the
    # unlink itself are issued relative to it, so a swapped or
    # renamed root cannot redirect a removal after classification.
    # The open itself is identity-pinned against the check above
    # (Director CORRECTION_REQUIRED 7113892787): islink/lstat and
    # open are separate path lookups, so a rename/symlink swap
    # between them could otherwise pin a DIFFERENT directory than
    # the one that was checked. The open does not follow a swapped
    # symlink (O_NOFOLLOW where supported), and the opened fd's
    # fstat identity must equal the checked lstat identity — same
    # (dev, ino), still a directory — or the sweep refuses before
    # anything is scanned. The fstat comparison is unconditional
    # and load-bearing: where O_NOFOLLOW is unavailable, an fd
    # opened through a swapped symlink stats the TARGET directory,
    # whose identity cannot equal the lstat identity of the symlink
    # path itself, and a renamed replacement directory carries its
    # own identity — so the contract is not silently weakened on
    # platforms without the flag.
    try:
        dir_fd = os.open(directory,
                         os.O_RDONLY
                         | getattr(os, "O_DIRECTORY", 0)
                         | getattr(os, "O_NOFOLLOW", 0))
    except OSError as exc:
        raise SweepRefusalError(
            f"sweep refused: root cannot be opened, nothing removed: "
            f"{directory!r}: {exc}") from exc
    try:
        opened_st = os.fstat(dir_fd)
    except OSError as exc:
        os.close(dir_fd)
        raise SweepRefusalError(
            f"sweep refused: opened root cannot be stated, nothing "
            f"removed: {directory!r}: {exc}") from exc
    if (opened_st.st_dev, opened_st.st_ino) != \
            (root_st.st_dev, root_st.st_ino) or \
            not stat.S_ISDIR(opened_st.st_mode):
        os.close(dir_fd)
        raise SweepRefusalError(
            f"sweep refused: root changed between check and open, "
            f"nothing removed: {directory!r}")
    try:
        names = os.listdir(dir_fd)
    except OSError:
        os.close(dir_fd)
        return {"scanned": 0, "removed": 0}

    getuid = getattr(os, "getuid", None)
    scanned = removed = 0

    def _emit(name, action, reason, pid=None, error=None):
        if report is not None:
            report.append({"name": name, "action": action,
                           "reason": reason, "pid": pid,
                           "error": error})

    try:
        # The provenance read sits INSIDE the descriptor's cleanup
        # block (7136945087): a provenance failure of any kind —
        # including structurally unusable ledger content — closes
        # dir_fd on its way out, and unusable provenance is a typed
        # refusal (nothing removed), never a raw exception.
        try:
            provenance = _read_provenance(dir_fd)
        except SweepProvenanceError as exc:
            raise SweepRefusalError(
                f"sweep refused: provenance ledger unusable, "
                f"nothing removed: {directory!r}: {exc}") from exc
        for name in sorted(names):
            if TMP_INFIX not in name:
                continue
            scanned += 1
            match = _TMP_NAME_RE.match(name)
            if match is None or TMP_INFIX in match.group("base"):
                _emit(name, "kept", "MALFORMED_NAME")
                continue
            pid = int(match.group("pid"))
            if pid <= 0:
                _emit(name, "kept", "INVALID_PID", pid=pid)
                continue
            path = os.path.join(directory, name)
            try:
                st = os.stat(name, dir_fd=dir_fd, follow_symlinks=False)
            except OSError:
                _emit(name, "kept", "STAT_FAILED", pid=pid)
                continue
            if stat.S_ISLNK(st.st_mode) or not stat.S_ISREG(st.st_mode):
                _emit(name, "kept", "NOT_A_REGULAR_FILE", pid=pid)
                continue
            if getuid is not None and st.st_uid != getuid():
                _emit(name, "kept", "NOT_OWNER", pid=pid)
                continue
            alive = _pid_liveness(pid)
            if alive is True:
                _emit(name, "kept", "LIVE_PID", pid=pid)
                continue
            if alive is None:
                _emit(name, "kept", "PID_UNPROBEABLE", pid=pid)
                continue
            if provenance.get(name) != (st.st_dev, st.st_ino):
                _emit(name, "kept", "NOT_PROVEN_OWNED", pid=pid)
                continue
            if min_age_seconds > 0 and \
                    (time.time() - st.st_mtime) < min_age_seconds:
                _emit(name, "kept", "TOO_YOUNG", pid=pid)
                continue
            identity = _identity(st)

            # Removal phase: re-prove everything before the unlink.
            if _SWEEP_HOOK is not None:
                _SWEEP_HOOK(path)
            alive = _pid_liveness(pid)
            if alive is True:
                _emit(name, "kept", "LIVE_PID", pid=pid)
                continue
            if alive is None:
                _emit(name, "kept", "PID_UNPROBEABLE", pid=pid)
                continue
            try:
                st_now = os.stat(name, dir_fd=dir_fd,
                                 follow_symlinks=False)
            except OSError:
                _emit(name, "kept", "STAT_FAILED", pid=pid)
                continue
            if _identity(st_now) != identity or \
                    stat.S_ISLNK(st_now.st_mode) or \
                    not stat.S_ISREG(st_now.st_mode):
                _emit(name, "kept", "CHANGED_SINCE_SCAN", pid=pid)
                continue
            # Ownership retirement (7136945087): durably retire the
            # mint through the pinned directory BEFORE the unlink,
            # so the removal never leaves reusable ownership behind
            # — a later file recycling this name AND inode would
            # otherwise inherit the live mint and look deletable.
            # The ledger stays append-only: retirement is a fsynced
            # consumed tombstone, proven by a fresh read. If
            # retirement cannot be established, the candidate is
            # KEPT and the reason disclosed. An interruption after
            # retirement but before unlink leaves the file in place
            # with its mint retired — later sweeps keep it
            # NOT_PROVEN_OWNED; the safe direction on every path.
            if not _retire_mint(dir_fd, name, st_now.st_dev,
                                st_now.st_ino):
                _emit(name, "kept", "RETIREMENT_UNPROVEN", pid=pid)
                continue
            provenance.pop(name, None)
            # Final identity revalidation (Director
            # CORRECTION_REQUIRED 7166216637): the identity check
            # above precedes retirement, and retirement itself
            # appends a tombstone, fsyncs, and re-reads the whole
            # ledger — so that check is NOT immediately before the
            # unlink. Re-stat the candidate through the pinned
            # directory NOW, after retirement and just before the
            # relative removal; any change of identity in the
            # interval keeps the candidate. (The mint is already
            # retired at this point; a kept candidate therefore
            # stays kept by later sweeps as NOT_PROVEN_OWNED — the
            # safe direction, as with an interrupted removal.)
            try:
                st_final = os.stat(name, dir_fd=dir_fd,
                                   follow_symlinks=False)
            except OSError:
                _emit(name, "kept", "STAT_FAILED", pid=pid)
                continue
            if _identity(st_final) != identity or \
                    stat.S_ISLNK(st_final.st_mode) or \
                    not stat.S_ISREG(st_final.st_mode):
                _emit(name, "kept", "CHANGED_SINCE_SCAN", pid=pid)
                continue
            try:
                os.unlink(name, dir_fd=dir_fd)
            except OSError as exc:
                _emit(name, "failed", "REMOVE_FAILED", pid=pid,
                      error=type(exc).__name__)
                continue
            removed += 1
            _emit(name, "removed", None, pid=pid)
    finally:
        # The ledger is APPEND-ONLY: the sweep never rewrites or
        # unlinks it (Director CORRECTION_REQUIRED 7136552041 —
        # compaction deferred). The former end-of-sweep prune
        # rebuilt the ledger from the snapshot read at sweep start,
        # so an ordinary save appending mint/consumed records during
        # the sweep could lose its new evidence or have a consumed
        # record resurrected; and its rewrite went through a fixed
        # working filename opened with O_TRUNC and no exclusive
        # creation, destroying any unrelated file at that path.
        # Stale records are harmless under the provenance law: a
        # record authorizes nothing unless a file exists with BOTH
        # the recorded name and the recorded inode, and consumed
        # temps are tombstoned at replace time.
        os.close(dir_fd)
    return {"scanned": scanned, "removed": removed}
