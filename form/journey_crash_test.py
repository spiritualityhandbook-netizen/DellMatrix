#!/usr/bin/env python3
"""Part VII / GP-E27 — journey harness family 10: J-12 Crash-save.

Written failing-first at code stage and registered in
form/regress.py LIST in the same commit (omitted-entry law).

Contract — Edition 1 file 06 (06_JOURNEY_ACCEPTANCE.md), J-12,
executed verbatim:

  Action: "Inject crash at each phase of owner save/checkpoint/
  Program-Nursery convergence, restart and show old or complete
  new generation, never hybrid."
  Failure oracle: "Broken/corrupt envelope refuses and offers
  diagnosed recovery; no false success on directory sync
  failure; all temp cleanup bounded and accounted."

Execution tier: PUBLIC_ENTRY_PATH — every journey action runs in
a literal `python3 -m form.repl` subprocess against a per-run
isolated owner; crashes are real process deaths (SIGKILL /
SIGSTOP+SIGKILL delivered to the REPL process mid-work), and
state comparison uses the persistence loader (reloaded vs
reloaded, never in-memory vs reloaded). Two fixture mechanics
are disclosed where they occur: the corruption legs write bytes
directly to a live member file (the fault being injected — the
restart itself runs at the public path), and the temp-accounting
leg invokes atomic_write.sweep_stale_tmps explicitly (the
documented accounting mechanism; see the wiring pin below).

Grounded behavior (each expectation verified first-hand in
scratch-owner probes, 2026-11-21, before this suite was
written):
  - A REPL session killed with SIGKILL mid-work (create issued,
    no save) restarts onto exactly the last saved generation:
    the unsaved unit is absent and the saved scope is complete —
    old generation, never a hybrid.
  - A save killed mid-write (SIGKILL delivered when the write's
    `.dmtmp.` temp file appears) leaves the canonical program
    file holding either the complete old generation (byte-exact)
    or the complete new one; the loader scope after restart is
    exactly one of the two, never a mix. The killed write leaves
    exactly one orphan temp, which loaders ignore.
  - Temp accounting posture is PINNED by
    form/atomic_write_boundaries_test.py control G: no
    production module calls sweep_stale_tmps — orphan temps are
    removed only by an explicit sweep call, never as a side
    effect of a save or a load, and that check must be updated
    deliberately by any circuit that changes the wiring. This
    suite therefore proves boundedness (one orphan per killed
    write, canonical files untouched by it) and exercises the
    accounting mechanism explicitly; it does not re-litigate
    the pin.
  - A checkpoint seal killed mid-flight (SIGSTOP frozen while
    the seal is in flight — a member temp or the checkpoint
    intent journal sighted — then SIGKILL) never moves the
    CURRENT pointer: the pointer commit is the last stage, so
    the previously committed generation stays authoritative,
    the live pair converges to a complete old or complete new
    scope, and the committed generation still restores exactly.
  - Corrupt CURRENT pointer is the in-family standard for a
    diagnosed refusal: `restore` answers "Restore unavailable:
    ... committed CURRENT pointer unreadable (<file>): <cause>"
    in-session, live state loads exactly, and
    current_generation_id fails closed to None — it never
    guesses a generation.
  - Corrupt NURSERY envelope raises the typed NurseryLoadError
    at the loader ("nursery file <file> is not a complete valid
    generation (truncated/malformed JSON, N bytes on disk)") —
    the diagnosis standard the program member is held to below.
  - A first-ever session that creates + grows and quits with
    NO explicit save leaves a nursery file holding proposals
    and NO program file at all (quit does not save; the nursery
    persists its own writes) — a legitimate program-produced
    state, which is why nursery content alone can never be
    treated as evidence of a destroyed envelope.

DEFECTS found by this family's failing-first run (both fixed
in this same section; repair note at the end of this
docstring):
  1. Corrupt PROGRAM envelope escaped the loader's own typed
     refusal contract: persist_rest._load_impl raises
     ProgramLoadError for a missing member, a binding mismatch
     and every structural defect (_validate_program_data), but
     the raw decode line `json.loads(_blob.decode("utf-8"))`
     raised raw UnicodeDecodeError / JSONDecodeError. At the
     public path the REPL died on a raw traceback (rc=1) — a
     refusal in effect (no state exposed, file preserved) but
     NOT the oracle's "refuses and offers diagnosed recovery":
     no typed diagnosis naming the file and cause, and no
     recovery offer, where the nursery member and the CURRENT
     pointer both present exactly that. The nursery member's
     typed refusal died the same way at the REPL door (raw
     traceback), so the presentation gap spans the pair.
  2. Missing PROGRAM member with a surviving sealed generation
     exposed a hybrid: the loader's fresh-owner arm (D2:
     missing file yields a fresh owner) fabricated a fresh
     program and the restart exposed it WEARING the destroyed
     book's nursery proposals — pending records whose parent
     units no longer existed in the exposed scope. The
     distinguishing evidence is the committed generation:
     sealing saves the live pair first, so a generation can
     only exist if the program file existed. (Nursery content
     alone is NOT such evidence — grounded below, a first
     session that grows before its first save legitimately
     leaves proposals with no program file yet, and that flow
     is pinned as a control in this suite.)

REPAIR (this section, three seams, no other behavior change):
  - persist_rest._load_impl: the decode is wrapped in
    ProgramLoadError with the NurseryLoadError-grade message
    (file, diagnosis, bytes on disk, file preserved).
  - persist_rest.load: on the default owner path only, a
    missing program file with a committed checkpoint
    generation raises ProgramLoadError naming the surviving
    generation as the recovery source, instead of fabricating
    a fresh program. The D2 fresh arm is untouched otherwise.
  - form/repl.py startup: the two typed load refusals present
    as a printed diagnosis + recovery offer and exit 1; every
    other exception keeps its traceback.

INSTRUMENT REPAIR ROUND 2 (post-CI, 2026-11-21 — the suite
itself, not the product): CI run 44962227931 at the round-1
head (32336f8) ran this suite to its full count on both
passes — the round-1 degradation worked as designed — but
reported 24/25 with exactly one named failure both passes:
j12_kill_midwrite_landed. The seal legs landed (journal
trigger); only the mid-WRITE leg still triggered on the
directory poll alone, and it missed systematically.
Classification: TEST-INSTRUMENT DEFECT, same family, one
level deeper. Measured locally: the directory poll's cycle
grows with the shared state dir (0.23ms at 671 files ->
1.76ms median / 2.11ms p95 at 6,000 files) while the temp
window is a single small write+fsync (13-35ms on this VM's
disk, 0/6 misses at both volumes locally). On the CI runner
(5,684 / 7,905 files, load1 0.80/0.70 idle, Python 3.11.18)
the faster disk collapses the window below the poll cycle:
the poll never samples the directory during the temp's
life, the save completes, and the check fails by name.
Reproduced locally by padding the state dir to 8,000 files
and slowing only the directory sampling (+50ms/call, cycle
above the local window): 24/25, sole FAIL
j12_kill_midwrite_landed, seal legs landed, no traceback —
the exact CI signature. Repair (this suite only): the write
leg's trigger gains a second sighting source that does not
degrade with directory size — the writer holds its temp
open for the whole write+fsync, and the temp's name embeds
the writer's pid, so a watcher thread polling
/proc/<repl-pid>/fd (~0.1ms per cycle, a handful of
entries) sees the temp for its entire life; the directory
poll remains as the union trigger and as the fallback where
/proc is unavailable. The landed check additionally pins
the kill's effect (the REPL's exit is -SIGKILL), so the
check now asserts sighting AND delivery, not sighting
alone. Under the identical slowed-directory diagnostic the
repaired suite lands the kill (25/25).

INSTRUMENT REPAIR (post-CI, 2026-11-21 — the suite itself,
not the product): CI run 44956493651 at this section's first
head (dc8c1c53) failed BOTH regress passes with this suite
dying on a traceback at 0/0, after exactly the nine checks
preceding the mid-seal leg, on an idle runner — while all
318 other suites passed, including every persistence/crash
neighbor. Classification (reproduced locally by slowing the
temp poll 50x: identical death signature, ~72s runtime vs
CI's ~73s): TEST-INSTRUMENT DEFECT. The kill legs triggered
on sighting a `.dmtmp.` temp by polling the SHARED state
dir; in the regress copy that dir holds thousands of files
accumulated by the suites before this one, so a poll cycle
can outlast a small write's whole temp window. When the
mid-seal sighting missed, the leg's bare proc.wait(timeout)
raised TimeoutExpired and killed the suite before it could
report — a missed trigger became a harness crash instead of
a named check failure. Repair (this suite only): the seal
leg now triggers on the temp OR the checkpoint intent
journal (present for the whole seal, not one write window);
every spawned-REPL write goes through write_line (a REPL
that died at startup fails its leg's checks, never the
suite); every spawned-REPL wait goes through wait_exit
(never raises — a missed trigger degrades to the leg's own
named FAILs and the suite always reports its full count).

Findings recorded, NOT fixed in this family (packet + Annex):
  - Missing-member residue: deleting the nursery file loads
    the program exactly and silently drops every pending
    proposal (no dangling references result — the exposed pair
    is complete, the loss is the silent part). Deleting the
    program file when NO generation survives still starts
    fresh over surviving proposals — indistinguishable from
    the legitimate grow-before-first-save state (the program
    itself produces that state), so no honest loader rule can
    refuse it; the refusal requires the positive evidence of
    a prior book that a sealed generation provides.

Uncovered at this tier, named honestly (not silently passed):
  - Crash at EACH seal phase and directory-sync failure are
    not constructible at the public path: the injection seam
    (_fail_at, incl. "dir_fsync_fail") is a module-global test
    hook with no REPL door. That matrix is covered at API level
    by form/mandell/dcc_xviii_test.py (controls A–W: crash-at-
    stage injection, missing/corrupt/swapped members, manifest/
    pointer corruption) and form/
    checkpoint_generation_stress_test.py (directory-sync
    degradation observable in the commit receipt, member-copy
    OSError abort, missing-manifest recovery). This suite
    exercises the public-path members of the crash family:
    mid-session kill, mid-live-save kill, mid-seal kill at the
    pointer commit boundary, and the corrupt-envelope restarts.
  - Kill-during-rollback and rollback-journal recovery are
    family 5 / R6.3 territory; not re-exercised here.

Baseline posture (plan section 5.1(iii)): this suite runs
against the pre-Parts main as a labeled BASELINE harness proof.
Its grades are evidence about the harness and the current
program, recorded in
director-reports/GRAND_SYNCHRONIZATION_REHEARSAL_2026-11-20.md;
the GP-E27 rehearsal executions proper run against merged
Parts I + II.

Run: python3 -m form.journey_crash_test
"""

import copy
import os
import shutil
import signal
import subprocess
import sys
import threading
import time
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from form.persist import _STATE_DIR, _safe_owner, _path, load as persist_load
from form.persist_rest import ProgramLoadError
from form.dell_matrix.nursery import NurseryLoadError, owner_nursery_path
from form.dell_matrix.atomic_write import sweep_stale_tmps
from form.mandell.checkpoint_generation import (
    _pointer_path, current_generation_id)
from form.mandell.core_i_recovery import _checkpoint_journal_path

RESULTS = []
_CLEANUP_ERRORS = []
RUN = uuid.uuid4().hex[:8]
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

CA = ("create an idea called Alpha Stone detail: alpha stone "
      "granite quarry marker goals: hold the alpha line")
CB = ("create an idea called Beta Stone detail: beta stone "
      "granite quarry marker goals: hold the beta line")
CC = ("create an idea called Gamma Stone detail: gamma stone "
      "granite quarry marker goals: hold the gamma line")


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))
    print(f"{'PASS' if ok else 'FAIL'} {name} {detail}")


def cleanup(owner):
    safe = _safe_owner(owner)
    if not os.path.isdir(_STATE_DIR):
        return
    for name in os.listdir(_STATE_DIR):
        if safe in name:
            p = os.path.join(_STATE_DIR, name)
            try:
                shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
            except OSError as e:
                _CLEANUP_ERRORS.append(f"{p}: {e}")


def state_files(owner):
    safe = _safe_owner(owner)
    if not os.path.isdir(_STATE_DIR):
        return []
    return sorted(n for n in os.listdir(_STATE_DIR) if safe in n)


def tmp_files(owner):
    safe = _safe_owner(owner)
    return [n for n in state_files(owner) if ".dmtmp." in n]


def run_repl(owner, lines, load=False, timeout=300):
    args = [sys.executable, "-m", "form.repl", "--owner", owner]
    if load:
        args.append("--load")
    proc = subprocess.run(args, input="\n".join(lines) + "\n",
                          capture_output=True, text=True, cwd=ROOT,
                          timeout=timeout)
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def spawn_repl(owner):
    """A live REPL subprocess under the suite's control (for
    delivering real signals mid-work). Output goes to DEVNULL:
    the kill legs assert on loader scope, not on session text,
    and an unread pipe could block the REPL on a full buffer."""
    return subprocess.Popen(
        [sys.executable, "-m", "form.repl", "--owner", owner, "--load"],
        stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL, text=True, cwd=ROOT)


def _fd_tmp_name(fd_dir, safe):
    """Name of the writer's in-flight `.dmtmp.` temp, seen
    through /proc/<writer-pid>/fd, or None. The writer holds
    its temp open for the whole write+fsync (atomic_write's
    contract), so the temp is visible here for its entire
    life — and the fd directory holds a handful of entries,
    so this sighting's cost does NOT grow with the shared
    state directory's population (round-2 repair, below)."""
    try:
        fds = os.listdir(fd_dir)
    except OSError:
        return None
    for fd in fds:
        try:
            target = os.readlink(os.path.join(fd_dir, fd))
        except OSError:
            continue
        base = os.path.basename(target)
        if ".dmtmp." in base and safe in base:
            return base
    return None


def wait_for_tmp(owner, timeout=30.0, proc=None):
    """Poll until a `.dmtmp.` temp for this owner appears (a
    write is in flight) — the deterministic crash trigger.

    Two sighting sources, unioned (round-2 repair): the
    shared-directory poll (tmp_files) and — when the writer
    process is given and /proc is available — a watcher
    thread polling the writer's fd table for the temp it
    holds open. The directory poll alone missed
    systematically in CI (run 44962227931, both passes,
    24/25 with only j12_kill_midwrite_landed failing): its
    cycle grows with the thousands of files the preceding
    suites leave in the shared state dir, while the CI
    runner's faster disk collapses the single small
    write+fsync window below that cycle, so no directory
    sample ever fell inside the temp's life. The fd
    sighting's cycle is ~0.1ms regardless of directory
    population, and the temp is open for the whole window
    it must be caught in. Where /proc is unavailable the
    directory poll remains, exactly as before."""
    safe = _safe_owner(owner)
    fd_dir = f"/proc/{proc.pid}/fd" if proc is not None else None
    if fd_dir and not os.path.isdir(fd_dir):
        fd_dir = None
    found = []
    stop = threading.Event()

    def watch():
        while not stop.is_set():
            name = _fd_tmp_name(fd_dir, safe)
            if name:
                found.append(name)
                return
            stop.wait(0.0002)

    watcher = None
    if fd_dir:
        watcher = threading.Thread(target=watch, daemon=True)
        watcher.start()
    try:
        deadline = time.time() + timeout
        while time.time() < deadline:
            if found:
                return list(found)
            tmps = tmp_files(owner)
            if tmps:
                return tmps
            time.sleep(0.0005)
        return list(found)
    finally:
        stop.set()
        if watcher is not None:
            watcher.join(timeout=2)


def write_line(proc, line):
    """Write one command line to a spawned REPL. Returns False
    when the REPL has already died (broken pipe) instead of
    raising: a dead REPL is a leg outcome the checks classify,
    never a suite-killing traceback (instrument repair, below)."""
    try:
        proc.stdin.write(line + "\n")
        proc.stdin.flush()
        return True
    except (BrokenPipeError, OSError):
        return False


def wait_exit(proc, timeout=30):
    """Wait for a spawned REPL to exit; returns its exit code,
    or None when it is still running at the timeout. Never
    raises TimeoutExpired: a missed crash trigger must degrade
    to the leg's own named check failures, not kill the whole
    suite before it can report (instrument repair, below)."""
    try:
        return proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        return None


def wait_for_seal_flight(owner, timeout=30.0):
    """Poll until the owner's checkpoint seal is observably in
    flight. Two triggers, in sighting order: a `.dmtmp.` temp
    (a member/save write in flight), or the checkpoint intent
    journal — written before the seal's first save and cleared
    only after the pointer commit, so it marks the WHOLE seal
    as in flight, not one millisecond-lived write window.
    Returns ("tmp", names) / ("journal", path) / (None, None).
    The temp-only trigger this replaces could miss every write
    window on a slow runner with a large shared state dir,
    leaving the leg's bare proc.wait to raise TimeoutExpired
    and kill the suite (CI 44956493651, both passes)."""
    journal = _checkpoint_journal_path(owner)
    deadline = time.time() + timeout
    while time.time() < deadline:
        tmps = tmp_files(owner)
        if tmps:
            return "tmp", tmps
        if os.path.isfile(journal):
            return "journal", journal
        time.sleep(0.0005)
    return None, None


def snap(owner):
    """Loader-basis snapshot: the full persisted scope — units
    with content fields, nursery statuses, boxes, history."""
    prog = persist_load(owner)
    plane = prog.cube.session.plane
    units = {}
    for uid, u in plane.units.items():
        units[uid] = {
            "label": u.label,
            "detail": getattr(u, "detail", "") or "",
            "goals": list(getattr(u, "goals", []) or []),
            "words": getattr(u, "words", "") or "",
            "parents": list(getattr(u, "parents", None) or []),
            "origin": getattr(u, "origin", None),
            "sandboxed": bool(getattr(u, "sandboxed", False)),
            "sandbox_id": getattr(u, "sandbox_id", None),
        }
    boxes = {sid: sorted(sb.member_ids)
             for sid, sb in plane.sandboxes.items()}
    props = {pid: p.status
             for pid, p in prog.nursery.proposals.items()}
    return {"units": units, "boxes": boxes, "props": props,
            "summary": prog.nursery.summary(),
            "history": list(getattr(prog, "history", []) or [])}


def scope_view(s):
    """The scope members compared on the 'complete new' arm of a
    crash disjunction (history is compared exactly on the 'old'
    arm via the full snapshot; the new arm's history carries the
    interrupted session's own note, so the never-hybrid claim is
    pinned on units/boxes/proposals/summary)."""
    return {"units": s["units"], "boxes": s["boxes"],
            "props": s["props"], "summary": s["summary"]}


def read_bytes(path):
    with open(path, "rb") as f:
        return f.read()


def write_bytes(path, blob):
    with open(path, "wb") as f:
        f.write(blob)


def flipped(blob):
    bad = bytearray(blob)
    bad[len(bad) // 2] ^= 0xFF
    return bytes(bad)


def main():
    mid_owner = f"JCrashMid{RUN}"
    write_owner = f"JCrashWrite{RUN}"
    write_ref = f"JCrashWriteRef{RUN}"
    seal_owner = f"JCrashSeal{RUN}"
    seal_ref = f"JCrashSealRef{RUN}"
    prog_owner = f"JCrashProg{RUN}"
    nurs_owner = f"JCrashNurs{RUN}"
    torn_owner = f"JCrashTorn{RUN}"
    ptr_owner = f"JCrashPtr{RUN}"
    fresh_owner = f"JCrashFresh{RUN}"
    owners = (mid_owner, write_owner, write_ref, seal_owner,
              seal_ref, prog_owner, nurs_owner, torn_owner,
              ptr_owner, fresh_owner)
    for o in owners:
        cleanup(o)
    try:
        # Isolation boundary, proven — not assumed (a fresh
        # Program() in this codebase loads persisted state by
        # default; the boundary is the per-run unique owner +
        # verified-empty start).
        check("crash_isolation_boundary_clean_start",
              all(state_files(o) == [] for o in owners),
              "no state files exist for any of the ten per-run "
              "owners before the sessions start")

        # ---------------- mid-session kill ---------------------
        rc, out = run_repl(mid_owner, [
            CA, CB, "save", "27[Checkpoint] :: base_one", "quit"])
        snap0 = snap(mid_owner)
        check("j12_mid_setup_sealed_baseline",
              rc == 0
              and current_generation_id(mid_owner) == "base_one"
              and set(snap0["units"]) == {"welcome", "alpha_stone",
                                          "beta_stone"},
              f"baseline saved and sealed; units="
              f"{sorted(snap0['units'])}")
        proc = spawn_repl(mid_owner)
        try:
            write_line(proc, CC)
            time.sleep(3.0)  # the create is processed in-memory
            proc.send_signal(signal.SIGKILL)
            wait_exit(proc)
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.wait()
        check("j12_kill_midsession_restart_shows_last_saved",
              snap(mid_owner) == snap0,
              "SIGKILL with an unsaved create in flight: after "
              "restart the loader scope equals the last saved "
              "generation EXACTLY — Gamma is absent, the saved "
              "scope is complete, nothing is hybrid")
        rc, out = run_repl(mid_owner, ["status", "quit"], load=True)
        check("j12_kill_midsession_restart_clean",
              rc == 0 and "Traceback" not in out
              and snap(mid_owner) == snap0,
              "a fresh public-path session loads the surviving "
              "generation cleanly")

        # ---------------- mid-save kill ------------------------
        rc, out = run_repl(write_owner, [CA, CB, "save", "quit"])
        snap_pre = snap(write_owner)
        prog_path = _path(write_owner)
        pre_bytes = read_bytes(prog_path)
        rc, out = run_repl(write_ref, [CA, CB, "save", CC, "save",
                                       "quit"])
        snap_new = snap(write_ref)
        check("j12_write_setup_scopes",
              rc == 0
              and set(snap_pre["units"]) == {"welcome",
                                             "alpha_stone",
                                             "beta_stone"}
              and set(snap_new["units"]) == {"welcome",
                                             "alpha_stone",
                                             "beta_stone",
                                             "gamma_stone"},
              "reference scopes built: the old generation and "
              "the complete new generation the killed save was "
              "writing toward")
        proc = spawn_repl(write_owner)
        caught = []
        kill_rc = None
        try:
            write_line(proc, CC)
            time.sleep(3.0)
            write_line(proc, "save")
            caught = wait_for_tmp(write_owner, proc=proc)
            if caught:
                proc.send_signal(signal.SIGKILL)
            # A missed sighting (slow runner, large state dir)
            # leaves the REPL alive at its prompt: wait_exit
            # returns None, the finally below kills it, and the
            # leg's checks fail by name — the baseline code let
            # this wait raise TimeoutExpired and kill the suite.
            kill_rc = wait_exit(proc)
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.wait()
        check("j12_kill_midwrite_landed",
              bool(caught) and kill_rc == -signal.SIGKILL,
              f"a write temp ({caught}) was sighted in flight "
              f"and the SIGKILL took the REPL down mid-save "
              f"(exit={kill_rc}) — the crash landed inside "
              f"the save, not before or after it")
        snap_after = snap(write_owner)
        old_arm = snap_after == snap_pre
        new_arm = scope_view(snap_after) == scope_view(snap_new)
        check("j12_kill_midwrite_old_or_new_never_hybrid",
              old_arm or new_arm,
              f"after the mid-save kill the loader scope is "
              f"exactly the old generation (old_arm={old_arm}) "
              f"or exactly the complete new one (new_arm="
              f"{new_arm}) — the canonical file was never left "
              f"as a torn mix")
        post_bytes = read_bytes(prog_path)
        orphans = tmp_files(write_owner)
        if post_bytes == pre_bytes:
            swept = sweep_stale_tmps(_STATE_DIR)
            check("j12_orphan_temp_bounded_and_accounted",
                  len(orphans) == 1
                  and swept["removed"] >= 1
                  and tmp_files(write_owner) == [],
                  f"old-generation arm: the killed write left "
                  f"exactly one orphan temp ({orphans}), loaders "
                  f"ignored it (the scope above loaded), and the "
                  f"explicit sweep accounted for it (removed="
                  f"{swept['removed']}); no temp remains")
        else:
            check("j12_orphan_temp_bounded_and_accounted",
                  orphans == [],
                  "new-generation arm: the write completed its "
                  "atomic replace before the kill landed, so no "
                  "orphan temp exists to account for")

        # ---------------- mid-seal kill ------------------------
        rc, out = run_repl(seal_owner, [
            CA, "save", "27[Checkpoint] :: seal_one", "quit"])
        snap_seal = snap(seal_owner)
        rc, out = run_repl(seal_owner, [CB, "save", "quit"],
                           load=True)
        snap_pre_seal = snap(seal_owner)
        rc, out = run_repl(seal_ref, [
            CA, "save", "27[Checkpoint] :: seal_one",
            CB, "save", CC, "save", "quit"])
        snap_seal_new = snap(seal_ref)
        check("j12_seal_setup_committed_baseline",
              current_generation_id(seal_owner) == "seal_one"
              and set(snap_pre_seal["units"]) == {"welcome",
                                                  "alpha_stone",
                                                  "beta_stone"}
              and "gamma_stone" in snap_seal_new["units"],
              "seal_one committed; the live pair has since "
              "advanced by Beta; the reference holds the scope "
              "the killed seal was converging toward")
        proc = spawn_repl(seal_owner)
        inflight_pointer = None
        flight_trigger = None
        try:
            write_line(proc, CC)
            time.sleep(3.0)
            write_line(proc, "27[Checkpoint] :: seal_two")
            flight_trigger, _seen = wait_for_seal_flight(seal_owner)
            if flight_trigger:
                proc.send_signal(signal.SIGSTOP)
                inflight_pointer = current_generation_id(seal_owner)
                proc.send_signal(signal.SIGKILL)
            # No sighting within the window: wait_exit returns
            # None, the finally below kills the REPL, and the
            # checks below fail by name — the baseline code let
            # this wait raise TimeoutExpired and kill the suite
            # (CI 44956493651: this leg, both passes, 0/0).
            wait_exit(proc)
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.wait()
        check("j12_kill_midseal_pointer_unmoved_in_flight",
              inflight_pointer == "seal_one",
              f"frozen mid-seal ({flight_trigger} in flight), "
              f"the CURRENT pointer still names seal_one "
              f"(observed={inflight_pointer!r}) — the pointer "
              f"commit is the last stage, so a crash anywhere "
              f"in the seal leaves the old generation "
              f"authoritative")
        snap_after_seal = snap(seal_owner)
        old_arm = snap_after_seal == snap_pre_seal
        new_arm = (scope_view(snap_after_seal)
                   == scope_view(snap_seal_new))
        check("j12_kill_midseal_old_or_new_live_pair",
              current_generation_id(seal_owner) == "seal_one"
              and (old_arm or new_arm),
              f"after the kill, CURRENT still names seal_one "
              f"and the live pair is exactly the pre-seal scope "
              f"(old_arm={old_arm}) or the complete saved scope "
              f"the seal's first stages wrote (new_arm="
              f"{new_arm}) — never a hybrid pair")
        rc, out = run_repl(seal_owner, [
            "restore confirm seal_one", "quit"], load=True)
        check("j12_kill_midseal_committed_generation_intact",
              "Restored generation seal_one." in out
              and snap(seal_owner) == snap_seal,
              "the previously committed generation survived the "
              "killed seal untouched and still restores its "
              "exact sealed scope at the public path")

        # ---------------- corrupt program envelope -------------
        rc, out = run_repl(prog_owner, [
            CA, CB, "save", "27[Checkpoint] :: base_one", "quit"])
        snap_p = snap(prog_owner)
        prog_path = _path(prog_owner)
        good_bytes = read_bytes(prog_path)
        bad_bytes = flipped(good_bytes)
        write_bytes(prog_path, bad_bytes)
        try:
            try:
                persist_load(prog_owner)
                loader_exc = None
            except Exception as e:  # classified below
                loader_exc = e
            check("j12_corrupt_program_loader_typed_refusal",
                  isinstance(loader_exc, ProgramLoadError)
                  and "not a complete valid generation"
                  in str(loader_exc)
                  and os.path.basename(prog_path) in str(loader_exc),
                  f"one flipped byte in the program member: the "
                  f"loader refuses with its typed ProgramLoadError "
                  f"naming the file and the diagnosis (observed: "
                  f"{type(loader_exc).__name__}: "
                  f"{str(loader_exc)[:120]})")
            rc, out = run_repl(prog_owner, ["status", "quit"],
                               load=True)
            check("j12_corrupt_program_repl_diagnosed_refusal",
                  rc != 0 and "Traceback" not in out
                  and os.path.basename(prog_path) in out
                  and "not a complete valid generation" in out
                  and "base_one" in out
                  and read_bytes(prog_path) == bad_bytes,
                  "at the public door the restart is a diagnosed "
                  "refusal, not a crash: no traceback, the file "
                  "and diagnosis are named, the surviving sealed "
                  "generation 'base_one' is offered as the "
                  "recovery source, and the corrupt file is "
                  "preserved byte-exact (never overwritten by a "
                  "fresh book, no false success)")
            write_bytes(prog_path, good_bytes[: len(good_bytes) // 2])
            rc, out = run_repl(prog_owner, ["status", "quit"],
                               load=True)
            check("j12_truncated_program_repl_diagnosed_refusal",
                  rc != 0 and "Traceback" not in out
                  and "not a complete valid generation" in out,
                  "a program member truncated to half its bytes "
                  "refuses identically — diagnosed, not a raw "
                  "decode traceback")
        finally:
            write_bytes(prog_path, good_bytes)
        rc, out = run_repl(prog_owner, ["status", "quit"], load=True)
        check("j12_repaired_program_loads_exact",
              rc == 0 and snap(prog_owner) == snap_p,
              "with the member's original bytes restored, the "
              "same restart loads the exact original scope — "
              "the refusals were the corruption, not a broken "
              "door")

        # ---------------- corrupt nursery envelope -------------
        rc, out = run_repl(nurs_owner, [
            CA, CB, "grow ideas", "save", "quit"])
        snap_n = snap(nurs_owner)
        nurs_path = owner_nursery_path(nurs_owner)
        good_nurs = read_bytes(nurs_path)
        prog_bytes_n = read_bytes(_path(nurs_owner))
        write_bytes(nurs_path, flipped(good_nurs))
        try:
            try:
                persist_load(nurs_owner)
                loader_exc = None
            except Exception as e:  # classified below
                loader_exc = e
            check("j12_corrupt_nursery_loader_typed_refusal",
                  isinstance(loader_exc, NurseryLoadError)
                  and "not a complete valid generation"
                  in str(loader_exc),
                  f"one flipped byte in the nursery member: the "
                  f"loader's typed NurseryLoadError is the "
                  f"diagnosis standard (observed: "
                  f"{type(loader_exc).__name__})")
            rc, out = run_repl(nurs_owner, ["status", "quit"],
                               load=True)
            check("j12_corrupt_nursery_repl_diagnosed_refusal",
                  rc != 0 and "Traceback" not in out
                  and os.path.basename(nurs_path) in out
                  and "not a complete valid generation" in out
                  and read_bytes(nurs_path) != good_nurs
                  and read_bytes(_path(nurs_owner)) == prog_bytes_n,
                  "the pair's other member presents the same "
                  "diagnosed refusal at the public door — no "
                  "traceback, and neither file is touched by the "
                  "refused restart")
        finally:
            write_bytes(nurs_path, good_nurs)
        rc, out = run_repl(nurs_owner, ["status", "quit"], load=True)
        check("j12_repaired_nursery_loads_exact",
              rc == 0 and snap(nurs_owner) == snap_n
              and len(snap_n["props"]) >= 1,
              f"repaired nursery loads exactly, pending "
              f"proposals intact (props={len(snap_n['props'])})")

        # ---------------- missing members (findings) -----------
        rc, out = run_repl(torn_owner, [
            CA, CB, "grow ideas", "save",
            "27[Checkpoint] :: base_one", "quit"])
        snap_t = snap(torn_owner)
        prog_path = _path(torn_owner)
        nurs_path = owner_nursery_path(torn_owner)
        good_prog = read_bytes(prog_path)
        good_nurs = read_bytes(nurs_path)
        os.remove(prog_path)
        try:
            try:
                persist_load(torn_owner)
                loader_exc = None
            except Exception as e:  # classified below
                loader_exc = e
            rc, out = run_repl(torn_owner, ["status", "quit"],
                               load=True)
            check("j12_missing_program_with_generation_refused",
                  isinstance(loader_exc, ProgramLoadError)
                  and "base_one" in str(loader_exc)
                  and rc != 0 and "Traceback" not in out
                  and "base_one" in out
                  and not os.path.exists(prog_path),
                  "DEFECT 2 (fixed in this section): with the "
                  "program member deleted but sealed generation "
                  "'base_one' surviving, the restart refuses "
                  "diagnosed — typed ProgramLoadError at the "
                  "loader, no traceback at the door, the "
                  "generation named as the recovery source — "
                  "instead of the baseline behavior this leg "
                  "caught: a fabricated fresh program exposing "
                  "the destroyed book's orphaned proposals "
                  "(parents absent from the exposed scope), a "
                  "hybrid pair. The refusal fabricates no file")
        finally:
            write_bytes(prog_path, good_prog)
        # Control for the refusal's boundary: the legitimate
        # program-produced state that resembles it — a first
        # session that grows before any save leaves proposals
        # and no program file, and NO generation. It must still
        # open (the D2 fresh arm), carrying its proposals.
        rc, out = run_repl(fresh_owner, [CA, CB, "grow ideas",
                                         "quit"])
        no_prog_yet = not os.path.isfile(_path(fresh_owner))
        rc2, out2 = run_repl(fresh_owner, ["status", "quit"],
                             load=True)
        s = snap(fresh_owner)
        check("j12_fresh_owner_grow_before_save_still_opens",
              rc == 0 and no_prog_yet and rc2 == 0
              and set(s["units"]) == {"welcome"}
              and len(s["props"]) >= 1,
              f"a brand-new owner who grew before its first "
              f"save (no program file, no generation, nursery "
              f"holding {len(s['props'])} proposals) still "
              f"opens at the public path with its proposals "
              f"carried — the Defect-2 refusal fires only on "
              f"the positive evidence of a sealed generation")
        os.remove(nurs_path)
        try:
            rc, out = run_repl(torn_owner, ["status", "quit"],
                               load=True)
            s = snap(torn_owner)
            check("j12_missing_nursery_no_hybrid_exposed",
                  rc == 0 and s["units"] == snap_t["units"]
                  and s["props"] == {},
                  "FINDING (recorded, not fixed): with the "
                  "nursery member deleted, the program scope "
                  "loads exactly and no phantom proposals are "
                  "exposed; the pending proposals' loss is "
                  "silent (props went from "
                  f"{len(snap_t['props'])} to 0 with no "
                  "diagnosis)")
        finally:
            write_bytes(nurs_path, good_nurs)

        # ---------------- corrupt CURRENT pointer --------------
        rc, out = run_repl(ptr_owner, [
            CA, CB, "save", "27[Checkpoint] :: base_one", "quit"])
        snap_ptr = snap(ptr_owner)
        ptr_path = _pointer_path(ptr_owner)
        good_ptr = read_bytes(ptr_path)
        write_bytes(ptr_path, b"{not json at all")
        try:
            rc, out = run_repl(ptr_owner, [
                "status", "restore", "quit"], load=True)
            check("j12_corrupt_pointer_diagnosed_unavailable",
                  rc == 0
                  and "committed CURRENT pointer unreadable" in out
                  and current_generation_id(ptr_owner) is None
                  and snap(ptr_owner) == snap_ptr,
                  "a garbage CURRENT pointer is refused with an "
                  "in-session diagnosis naming the pointer and "
                  "the cause, the generation query fails closed "
                  "to None (never a guess), and live state loads "
                  "exactly — the diagnosed-refusal standard the "
                  "corrupt-member legs are held to")
        finally:
            write_bytes(ptr_path, good_ptr)
        check("j12_pointer_repair_restores_current",
              current_generation_id(ptr_owner) == "base_one",
              "with the pointer's original bytes restored, the "
              "committed generation is named again")
    finally:
        for o in owners:
            cleanup(o)

    check("Z.cleanup", not _CLEANUP_ERRORS, "; ".join(_CLEANUP_ERRORS))
    failed = [n for n, ok, _ in RESULTS if not ok]
    print(f"JOURNEY_CRASH: {len(RESULTS) - len(failed)}/{len(RESULTS)} PASS")
    if failed:
        print("FAILURES:", ", ".join(failed))
    return 1 if failed else 0


def smoke():
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
