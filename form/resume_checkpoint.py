"""SM-08 — durable resumability checkpoints (Part 0, register row #92).

Implements the completion envelope (AGENTS.md section 4) as a
mechanism instead of a convention:

    write_checkpoint(path, state)  -> path
    read_checkpoint(path)          -> state dict
    verify_checkpoint(state)       -> list of problem strings ([] = sound)

Laws (Part 0 plan, director-reports/PART_0_PLAN_2026-11-20.md §3.2):
  * the state carries every completion-envelope field; a missing
    field is named by verify_checkpoint;
  * the on-disk record carries a checksum over the canonical
    serialization of the state; any post-write tampering is
    detected at read (read raises) and by verify_checkpoint when a
    checksum is present in the state handed to it;
  * write is atomic (temp file in the same directory + replace);
    no temp residue; a torn checkpoint is never silently trusted;
  * COMPLETED_PHASES is append-only across writes to the same
    path: a write that drops a completed phase is refused;
  * unknown extra fields round-trip untouched (forward
    compatibility);
  * compactness discipline: the writer refuses a state whose
    canonical form exceeds MAX_CANONICAL_BYTES, naming the
    oversized field (the envelope is a recovery state, not a log).

The on-disk form is the state dict itself plus one ``checksum``
key over the canonical form of the rest — so any reader, including
a separate OS process doing a plain ``json.load``, sees the
envelope fields at top level, and ``read_checkpoint`` strips the
checksum key so the caller's state round-trips exactly. Standard
library only; no network; the module never touches form/state.
"""
import hashlib
import json
import os
import tempfile

ENVELOPE_FIELDS = [
    "DIRECTIVE_ID", "PARENT_GOAL", "BASE", "BRANCH", "HEAD",
    "WORKTREE", "FILES_CHANGED", "COMPLETED_PHASES", "CURRENT_PHASE",
    "TESTS_RUN", "TESTS_REMAINING", "UNCOMMITTED_WORK", "BLOCKERS",
    "FALLBACK_PATHS", "NEXT_EXECUTABLE_ACTION",
]

MAX_CANONICAL_BYTES = 16 * 1024


def _canonical(state):
    return json.dumps(state, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False)


def _checksum(state):
    return hashlib.sha256(_canonical(state).encode("utf-8")).hexdigest()


def _largest_field(state):
    """(field, byte size) of the largest single field, canonical form."""
    best, best_size = None, -1
    for key, value in state.items():
        size = len(json.dumps({key: value}, sort_keys=True,
                              ensure_ascii=False).encode("utf-8"))
        if size > best_size:
            best, best_size = key, size
    return best, best_size


def verify_checkpoint(state):
    """Return a list of problem strings; [] means the state is sound.

    Names every missing envelope field and any checksum mismatch
    (when the state carries a ``checksum`` key). Also flags a
    canonical form over the compactness bound, naming the largest
    field.
    """
    problems = []
    if not isinstance(state, dict):
        return ["state is not a dict: %r" % (type(state).__name__,)]
    for field in ENVELOPE_FIELDS:
        if field not in state:
            problems.append("missing envelope field: %s" % field)
    if "COMPLETED_PHASES" in state and not isinstance(
            state["COMPLETED_PHASES"], list):
        problems.append("COMPLETED_PHASES is not a list")
    if "checksum" in state:
        payload = {k: v for k, v in state.items() if k != "checksum"}
        if state["checksum"] != _checksum(payload):
            problems.append("checksum mismatch")
    try:
        size = len(_canonical(state).encode("utf-8"))
    except (TypeError, ValueError) as exc:
        problems.append("state is not JSON-serializable: %s" % (exc,))
        return problems
    if size > MAX_CANONICAL_BYTES:
        field, _ = _largest_field(state)
        problems.append(
            "canonical form %d bytes exceeds %d-byte bound; "
            "largest field: %s" % (size, MAX_CANONICAL_BYTES, field))
    return problems


def write_checkpoint(path, state):
    """Atomically write ``state`` to ``path``; return ``path``.

    Refuses (ValueError) a state with missing envelope fields, a
    state over the compactness bound (naming the oversized field),
    and a write that would drop a phase already recorded in the
    existing checkpoint's COMPLETED_PHASES.
    """
    problems = [p for p in verify_checkpoint(state)
                if not p.startswith("checksum")]
    if problems:
        raise ValueError("refusing to write unsound checkpoint: "
                         + "; ".join(problems))
    if os.path.exists(path):
        existing = read_checkpoint(path)
        prior = existing.get("COMPLETED_PHASES") or []
        new = state.get("COMPLETED_PHASES") or []
        dropped = [p for p in prior if p not in new]
        if dropped:
            raise ValueError(
                "COMPLETED_PHASES is append-only; write drops: %s"
                % (", ".join(str(d) for d in dropped),))
    payload = {k: v for k, v in state.items() if k != "checksum"}
    record = dict(payload)
    record["checksum"] = _checksum(payload)
    text = json.dumps(record, sort_keys=True, indent=1,
                      ensure_ascii=False)
    directory = os.path.dirname(os.path.abspath(path))
    os.makedirs(directory, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".checkpoint-", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    return path


def read_checkpoint(path):
    """Read and integrity-check the checkpoint at ``path``.

    Returns the exact state dict that was written. Raises ValueError
    on a torn/truncated file, a malformed record, or a checksum
    mismatch — a damaged checkpoint is never silently trusted.
    """
    with open(path, "r", encoding="utf-8") as fh:
        raw = fh.read()
    try:
        record = json.loads(raw)
    except ValueError as exc:
        raise ValueError("checkpoint at %s is not valid JSON "
                         "(torn or truncated?): %s" % (path, exc))
    if not isinstance(record, dict) or "checksum" not in record:
        raise ValueError("checkpoint at %s lacks its checksum "
                         "field" % (path,))
    state = {k: v for k, v in record.items() if k != "checksum"}
    if record["checksum"] != _checksum(state):
        raise ValueError("checkpoint at %s fails its checksum "
                         "(tampered or torn)" % (path,))
    return state
