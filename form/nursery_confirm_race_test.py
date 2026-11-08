#!/usr/bin/env python3
"""72-31 — Nursery optimistic concurrency + duplicate confirmation
(= SM-31): two live stale instances racing confirm.

Existing coverage (NOT duplicated): foundation_acceptance's
lost_update_explicit pins a stale confirm refused after an
intervening nursery ADD, and the 72-31 scoping probe
(hidden_files/72-31_probe.py) pins the Nursery level. This suite
pins the register's missing evidence at the PROGRAM level:

  Controls (must hold):
  - N* Nursery level (isolated temp file): two stale instances;
    first confirm succeeds; stale second refused with
    NurseryConflictError, in-memory status rolled back; fresh
    reload confirmed exactly once; duplicate confirm on one
    instance is a clean no-op; stale ADD refused, no lost update.
  - P* Program level, sequential stale (both instances loaded
    from the SAME generation before either confirms): first
    confirm ok; stale second refused explicitly
    (nursery_conflict), loser's in-memory proposal stays pending
    with no placed unit; canonical reload (Nursery.load +
    persist_rest.load) shows confirmed + the Idea exactly once;
    a further confirm on the reloaded instance is refused.

  Defects (fail at the unrepaired head):
  - D1 interleaved commit (deterministic): the loser's commit is
    intercepted so the winner's confirm completes first, then
    the loser's commit proceeds and is refused — but the loser's
    failure compensation restores the BASELINE BYTES captured
    before the winner committed, silently overwriting the
    winner's confirmed Nursery + Program state. Reload then
    shows pending / no unit: a reported-success confirmation is
    lost. The winner's committed state must survive the loser's
    refused attempt.
  - D1U interleaved commit + unreadable CURRENT pointer at the
    loser's compensation recheck (Director correction
    2026-11-06): an OSError injected on the pointer read must not
    be collapsed into 'not advanced' — the winner must survive
    and recovery evidence must be preserved on the loser.
  - D2 true concurrent cross-process race (barrier-synchronised
    workers, both loaded + authorised before either confirms):
    combined contract — both workers ready before release, both
    exit zero, both leave valid receipts, exactly one reports ok
    and the other the documented nursery_conflict refusal, AND
    the canonical reload shows confirmed + the Idea exactly
    once. At the unrepaired head every probed run violated the
    outcome half (8/8: double-ok, or ok+conflict with the winner
    lost); the receipt half was vacuous (a worker exiting early
    still passed) until the 2026-11-06 strengthening, whose
    rejection of sabotaged races is pinned by D2M.

Labels: CROSS_PROCESS for D2 (fresh OS processes against the real
Program authority); the rest INTEGRATION / REAL_PROGRAM.
State hygiene: uuid-unique owners; cleanup failures are reported
in the final check, never swallowed.
"""
from __future__ import annotations

import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

REPO = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, REPO)

RESULTS = []
_CLEANUP_ERRORS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def _clean(owner):
    for p in glob.glob(os.path.join(REPO, "form", "state", f"*{owner}*")):
        try:
            os.remove(p) if os.path.isfile(p) else shutil.rmtree(p)
        except Exception as e:  # noqa: BLE001
            _CLEANUP_ERRORS.append(f"{p}:{type(e).__name__}")


def _owner(tag):
    return f"T7231{tag}" + uuid.uuid4().hex[:8]


def _reload(owner, pid):
    from form.dell_matrix.nursery import Nursery, owner_nursery_path
    from form import persist_rest
    n = Nursery.load(owner_nursery_path(owner))
    status = n.proposals[pid].status if pid in n.proposals else "ABSENT"
    p = persist_rest.load(owner, activate=False)
    units = p.cube.session.plane.units
    return {"status": status, "unit": pid in units,
            "label_count": sum(1 for u in units.values()
                               if u.label == "Race Idea")}


def _confirm(p, pid):
    try:
        r = p.confirm_proposal(
            pid, _producer="test",
            _review_context=p.make_review_context(pid, "test"))
        return {"ok": r.get("ok") is True, "reason": r.get("reason"),
                "raw": r}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "reason": f"raised:{type(e).__name__}",
                "raw": {}}


# ---------------------------------------------------------------- N
def case_nursery():
    from form.dell_matrix.nursery import Nursery, NurseryConflictError
    tmp = tempfile.mkdtemp(prefix="n31_")
    path = os.path.join(tmp, "nursery_test.json")
    try:
        s = Nursery.load(path)
        pid = s.add("Race Idea", words="alpha beta").id
        a, b = Nursery.load(path), Nursery.load(path)
        check("N.both_see_pending",
              a.proposals[pid].status == "pending"
              and b.proposals[pid].status == "pending")
        ra = a.confirm(pid)
        check("N.first_confirm_ok",
              ra is not None and ra.status == "confirmed")
        try:
            b.confirm(pid)
            bout = "no-raise"
        except NurseryConflictError:
            bout = "conflict"
        except Exception as e:  # noqa: BLE001
            bout = f"other:{type(e).__name__}"
        check("N.stale_confirm_refused", bout == "conflict", bout)
        check("N.stale_inmemory_rolled_back",
              b.proposals[pid].status == "pending")
        c = Nursery.load(path)
        check("N.reload_confirmed_once",
              c.proposals[pid].status == "confirmed"
              and c.summary()["confirmed"] == 1
              and c.summary()["total"] == 1)
        check("N.dup_confirm_noop", c.confirm(pid) is None)
        d, e = Nursery.load(path), Nursery.load(path)
        d.add("Second Idea", words="gamma")
        try:
            e.add("Third Idea", words="delta")
            eout = "no-raise"
        except NurseryConflictError:
            eout = "conflict"
        except Exception as ex:  # noqa: BLE001
            eout = f"other:{type(ex).__name__}"
        labels = sorted(p.label for p in Nursery.load(path).proposals.values())
        check("N.stale_add_refused_no_lost_update",
              eout == "conflict" and labels == ["Race Idea", "Second Idea"],
              f"{eout} {labels}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------- P
def case_program_sequential():
    from form.open import open_program
    owner = _owner("SEQ")
    _clean(owner)
    try:
        pid = open_program(owner).nursery.add(
            "Race Idea", words="alpha beta").id
        a, b = open_program(owner), open_program(owner)
        check("P.both_see_pending",
              a.nursery.proposals[pid].status == "pending"
              and b.nursery.proposals[pid].status == "pending"
              and pid not in a.cube.session.plane.units
              and pid not in b.cube.session.plane.units)
        ra = _confirm(a, pid)
        check("P.first_confirm_ok", ra["ok"], str(ra["raw"])[:200])
        rb = _confirm(b, pid)
        check("P.stale_confirm_refused_conflict",
              not rb["ok"] and rb["reason"] == "nursery_conflict",
              str(rb["raw"])[:200])
        check("P.loser_inmemory_pending_no_unit",
              b.nursery.proposals[pid].status == "pending"
              and pid not in b.cube.session.plane.units)
        rel = _reload(owner, pid)
        check("P.reload_confirmed_exactly_once",
              rel["status"] == "confirmed" and rel["unit"]
              and rel["label_count"] == 1, str(rel))
        c = open_program(owner)
        rdup = _confirm(c, pid)
        check("P.reload_dup_confirm_refused", not rdup["ok"],
              str(rdup["raw"])[:200])
    finally:
        _clean(owner)


# ---------------------------------------------------------------- D1
def case_interleaved_commit():
    from form.open import open_program
    import form.mandell.checkpoint_generation as cg
    owner = _owner("INT")
    _clean(owner)
    try:
        pid = open_program(owner).nursery.add(
            "Race Idea", words="alpha beta").id
        loser, winner = open_program(owner), open_program(owner)
        orig_commit = cg.commit_checkpoint
        state = {"fired": False, "winner": None}

        def intercept(program, *a, **kw):
            if not state["fired"]:
                state["fired"] = True
                # Winner's confirm completes ENTIRELY (its own commit
                # goes through the original function) before the
                # loser's commit proceeds.
                state["winner"] = _confirm(winner, pid)
            return orig_commit(program, *a, **kw)

        cg.commit_checkpoint = intercept
        try:
            rl = _confirm(loser, pid)
        finally:
            cg.commit_checkpoint = orig_commit
        check("D1.winner_confirm_ok",
              bool(state["winner"] and state["winner"]["ok"]),
              str(state["winner"]))
        check("D1.loser_refused", not rl["ok"], str(rl["raw"])[:200])
        rel = _reload(owner, pid)
        check("D1.winner_state_survives_loser_refusal",
              rel["status"] == "confirmed" and rel["unit"]
              and rel["label_count"] == 1, str(rel))
    finally:
        _clean(owner)


_FRESH_RELOAD = r"""
import json, os, sys
sys.path.insert(0, %(REPO)r)
owner, pid = sys.argv[1:3]
from form.mandell.core_i_recovery import _confirm_journal_path
jp = _confirm_journal_path(owner)
journal = None
if os.path.exists(jp):
    try:
        journal = json.loads(open(jp).read()).get("proposal_id")
    except Exception:
        journal = "UNREADABLE"
from form.dell_matrix.nursery import Nursery, owner_nursery_path
from form import persist_rest
n = Nursery.load(owner_nursery_path(owner))
status = n.proposals[pid].status if pid in n.proposals else "ABSENT"
p = persist_rest.load(owner, activate=False)
units = p.cube.session.plane.units
print(json.dumps({
    "status": status, "unit": pid in units,
    "label_count": sum(1 for u in units.values()
                       if u.label == "Race Idea"),
    "journal_pid": journal}))
"""


def _reload_fresh(owner, pid):
    """Reload in a FRESH OS process: proposal status, unit
    presence/count, and confirm-journal disposition."""
    out = subprocess.run(
        [sys.executable, "-c", _FRESH_RELOAD % {"REPO": REPO},
         owner, pid],
        cwd=REPO, capture_output=True, text=True, timeout=120)
    return json.loads(out.stdout.strip().splitlines()[-1])


def _pointer_fault(*, fire_after_winner=False, fire_on_call=None):
    """Build a _read_pointer wrapper injecting OSError into the
    generation-identity reads made by confirm_proposal (routed
    through current_generation_id at the original head, through
    committed_generation_state after the repair). Modes:
    fire_on_call=N — raise on the Nth such call after arming;
    fire_after_winner — raise on every such call made after the
    interleaved winner's confirm has completed (i.e. exactly the
    loser's compensation recheck)."""
    import traceback
    state = {"n": 0, "armed": False}

    def wrap(orig_rp, winner_done):
        def counting_rp(owner_):
            stack = [f.name for f in traceback.extract_stack()]
            routed = ("current_generation_id" in stack
                      or "committed_generation_state" in stack)
            if (state["armed"] and routed
                    and "confirm_proposal" in stack):
                state["n"] += 1
                if fire_on_call is not None and state["n"] == fire_on_call:
                    raise OSError("INJECTED_POINTER_READ_FAILURE")
                if fire_after_winner and winner_done():
                    raise OSError("INJECTED_POINTER_READ_FAILURE")
            return orig_rp(owner_)
        return counting_rp

    return state, wrap


# ---------------------------------------------------------------- D1U
def case_interleaved_unreadable_pointer():
    """Director correction 2026-11-06: the loser's compensation
    recheck reads the committed generation through a best-effort
    accessor; inject OSError on exactly that read (at the original
    head: the third _read_pointer call routed through
    confirm_proposal -> current_generation_id — loser baseline,
    winner baseline, loser recheck). The accessor collapses the
    failure to None, the recheck concludes 'not advanced', and the
    loser restores stale baseline bytes: the winner's successful
    confirmation disappears on reload. The repair must distinguish
    proven absence / verified identity / unreadable pointer, and
    on uncertainty preserve recovery evidence (the affected
    instance is fenced recovery-required; no stale journal is
    left misrepresenting the durable state)."""
    from form.open import open_program
    import form.mandell.checkpoint_generation as cg
    owner = _owner("D1U")
    _clean(owner)
    try:
        pid = open_program(owner).nursery.add(
            "Race Idea", words="alpha beta").id
        loser, winner = open_program(owner), open_program(owner)
        state = {"fired": False, "winner": None}
        fault, wrap = _pointer_fault(fire_after_winner=True)
        orig_commit = cg.commit_checkpoint

        def intercept(program, *a, **kw):
            if not state["fired"]:
                state["fired"] = True
                state["winner"] = _confirm(winner, pid)
            return orig_commit(program, *a, **kw)

        orig_rp = cg._read_pointer
        cg._read_pointer = wrap(
            orig_rp, lambda: state["winner"] is not None)
        cg.commit_checkpoint = intercept
        fault["armed"] = True
        try:
            rl = _confirm(loser, pid)
        finally:
            cg.commit_checkpoint = orig_commit
            cg._read_pointer = orig_rp
        check("D1U.winner_confirm_ok",
              bool(state["winner"] and state["winner"]["ok"]),
              str(state["winner"]))
        check("D1U.loser_refused_conflict",
              not rl["ok"] and rl["reason"] == "nursery_conflict",
              str(rl))
        rel = _reload_fresh(owner, pid)
        check("D1U.winner_survives_unreadable_recheck",
              rel["status"] == "confirmed" and rel["unit"]
              and rel["label_count"] == 1, str(rel))
        req = getattr(loser, "_recovery_required", None)
        check("D1U.recovery_evidence_preserved",
              isinstance(req, dict) and pid in req
              and "unreadable" in str(req[pid].get("reason", "")),
              str(req))
        check("D1U.journal_disposition_clean",
              rel["journal_pid"] is None, str(rel))
    finally:
        _clean(owner)


# ---------------------------------------------------------------- D1B
def case_baseline_unreadable():
    """Companion to D1U (Director work order: cover failure
    reading the baseline as well as failure rechecking it). The
    winner has already committed. The loser's confirm then fails
    to READ the committed generation at baseline capture (OSError
    on the first identity-routed pointer read of its attempt):
    compensation is unverifiable, so the attempt must fail
    closed — loser refused, winner's durable state untouched,
    and the loser's confirm intent journal left in place as
    recovery evidence (verified from a fresh process). The
    owner lock must be released: a fresh instance confirms a
    new proposal immediately afterwards."""
    from form.open import open_program
    import form.mandell.checkpoint_generation as cg
    owner = _owner("D1B")
    _clean(owner)
    try:
        pid = open_program(owner).nursery.add(
            "Race Idea", words="alpha beta").id
        loser, winner = open_program(owner), open_program(owner)
        rw = _confirm(winner, pid)
        check("D1B.winner_confirm_ok", rw["ok"], str(rw))
        fault, wrap = _pointer_fault(fire_on_call=1)
        orig_rp = cg._read_pointer
        cg._read_pointer = wrap(orig_rp, lambda: False)
        fault["armed"] = True
        try:
            rl = _confirm(loser, pid)
        finally:
            cg._read_pointer = orig_rp
        check("D1B.loser_refused_not_ok", not rl["ok"], str(rl))
        rel = _reload_fresh(owner, pid)
        check("D1B.winner_survives_baseline_failure",
              rel["status"] == "confirmed" and rel["unit"]
              and rel["label_count"] == 1, str(rel))
        check("D1B.journal_preserved_as_evidence",
              rel["journal_pid"] == pid, str(rel))
        fresh = open_program(owner)
        pid2 = fresh.nursery.add("Second Idea", words="gamma").id
        r2 = _confirm(fresh, pid2)
        check("D1B.lock_released_followup_confirm_ok", r2["ok"],
              str(r2))
    finally:
        _clean(owner)


# ---------------------------------------------------------------- D1S
def case_single_worker_baseline_unreadable():
    """Director correction round 2 (2026-11-06, on PR head
    616449f): a SINGLE worker with an otherwise healthy checkpoint
    whose baseline generation read fails must be REFUSED before
    any commit — the earlier D1B case could not see this defect
    because its stale loser was refused independently by the
    nursery guard, while the lone worker's commit simply
    succeeded (commit_checkpoint ran once, confirm returned ok).
    Required: explicit refusal, zero checkpoint calls, proposal
    still pending after fresh-process reload, intent journal
    preserved as recovery evidence, owner lock released (a fresh
    instance's retry of the same proposal succeeds)."""
    from form.open import open_program
    import form.mandell.checkpoint_generation as cg
    owner = _owner("D1S")
    _clean(owner)
    try:
        p0 = open_program(owner)
        pid_a = p0.nursery.add("First Idea", words="alpha").id
        ra = _confirm(p0, pid_a)
        check("D1S.setup_checkpoint_established", ra["ok"], str(ra))
        worker = open_program(owner)
        pid = worker.nursery.add("Race Idea", words="alpha beta").id
        commits = {"n": 0}
        orig_commit = cg.commit_checkpoint

        def counting_commit(program, *a, **kw):
            commits["n"] += 1
            return orig_commit(program, *a, **kw)

        fault, wrap = _pointer_fault(fire_on_call=1)
        orig_rp = cg._read_pointer
        cg._read_pointer = wrap(orig_rp, lambda: False)
        cg.commit_checkpoint = counting_commit
        fault["armed"] = True
        try:
            r = _confirm(worker, pid)
        finally:
            cg._read_pointer = orig_rp
            cg.commit_checkpoint = orig_commit
        check("D1S.refused_baseline_unverifiable",
              not r["ok"] and r["reason"] == "baseline_unverifiable",
              str(r))
        check("D1S.zero_commit_calls", commits["n"] == 0,
              str(commits))
        rel = _reload_fresh(owner, pid)
        check("D1S.reload_still_pending_no_unit",
              rel["status"] == "pending" and not rel["unit"]
              and rel["label_count"] == 0, str(rel))
        check("D1S.journal_preserved_as_evidence",
              rel["journal_pid"] == pid, str(rel))
        fresh = open_program(owner)
        r2 = _confirm(fresh, pid)
        check("D1S.lock_released_retry_succeeds", r2["ok"], str(r2))
    finally:
        _clean(owner)


# ---------------------------------------------------------------- D1P
def case_pointer_classification():
    """Director correction round 2: the CURRENT pointer path
    holding a DIRECTORY or a DANGLING SYMLINK is present but
    unreadable — never proven absence. Proven absence is only a
    pointer path that does not exist at all. At 616449f both
    sabotage shapes returned ('absent', None) because absence
    was inferred from isfile() on the resolved path."""
    import form.mandell.checkpoint_generation as cg
    owner = _owner("D1P")
    _clean(owner)
    try:
        path = cg._pointer_path(owner)
        st, _gen = cg.committed_generation_state(owner)
        check("D1P.missing_pointer_proven_absent", st == "absent", st)
        os.makedirs(path)
        try:
            st2, _g2 = cg.committed_generation_state(owner)
            check("D1P.directory_pointer_unreadable",
                  st2 == "unreadable", st2)
        finally:
            os.rmdir(path)
        os.symlink(path + ".missing-target", path)
        try:
            st3, _g3 = cg.committed_generation_state(owner)
            check("D1P.dangling_symlink_unreadable",
                  st3 == "unreadable", st3)
        finally:
            os.unlink(path)
    finally:
        _clean(owner)


# ---------------------------------------------------------------- D1PE
_EACCES_WORKER = r"""
import json, os, sys, time
tree, owner, spool = sys.argv[1:4]
sys.path.insert(0, tree)
# Import EVERYTHING while the state dir is still searchable:
# several form modules create state subdirectories at import.
from form.mandell.checkpoint_generation import (
    committed_generation_state, _pointer_path)
p = _pointer_path(owner)
open(os.path.join(spool, "ready"), "w").write("ready")
deadline = time.time() + 60
while not os.path.exists(os.path.join(spool, "lock")):
    if time.time() > deadline:
        print(json.dumps({"proof": {"lstat": "no-lock-signal",
                                     "errno": None},
                          "state": "subprocess_failed"}))
        sys.exit(0)
    time.sleep(0.02)
try:
    os.lstat(p)
    proof = {"lstat": "ok", "errno": None}
except PermissionError as e:
    proof = {"lstat": "PermissionError", "errno": e.errno}
except Exception as e:
    proof = {"lstat": type(e).__name__, "errno": getattr(e, "errno", None)}
st, _gen = committed_generation_state(owner)
print(json.dumps({"proof": proof, "state": st}))
"""


def case_pointer_eacces():
    """Director correction round 3 (2026-11-06, on head 79c3c46):
    a real CURRENT file whose parent directory denies search —
    os.lstat raises PermissionError (EACCES), but os.path.lexists
    swallows it, so the state classified ('absent', None). The
    case runs the classification in a worker process whose user
    genuinely cannot search the state directory, against a
    world-traversable copy of the tree: it first PROVES EACCES
    on a direct os.lstat of the pointer, then asserts the
    classification of the same lookup is 'unreadable'.

    Privilege geometry (fixture correction, 2026-11-06): the
    worker must be an UNPRIVILEGED user relative to the state
    dir in both worlds. When the suite itself runs as root
    (EACCES cannot occur for root), the worker drops to user
    'nobody' via setpriv and the root-owned state dir is chmod
    0o700 (nobody is 'other': no search). When the suite runs
    as a NON-root user (e.g. CI runners), setpriv to another
    uid is itself forbidden — the original fixture died there
    (55/57 on GitHub, reproduced locally under a non-root uid)
    — so the worker runs as the SAME user and the state dir is
    chmod 0o000: the owner is denied search on its own
    directory, and os.lstat raises the same EACCES. The proof
    obligations are identical in both geometries."""
    import form.mandell.checkpoint_generation as cg
    owner = _owner("EAC")
    base = tempfile.mkdtemp(prefix="n31eac_")
    try:
        tree = os.path.join(base, "tree")
        shutil.copytree(os.path.join(REPO, "form"),
                        os.path.join(tree, "form"))
        os.chmod(base, 0o755)
        for root, dirs, files in os.walk(tree):
            os.chmod(root, 0o755)
            for fn in files:
                os.chmod(os.path.join(root, fn), 0o644)
        pointer = os.path.join(
            tree, "form", "state",
            os.path.basename(cg._pointer_path(owner)))
        with open(pointer, "w") as f:
            f.write("{}")
        spool = os.path.join(base, "spool")
        os.makedirs(spool)
        os.chmod(spool, 0o777)
        as_root = os.getuid() == 0
        if as_root:
            worker_cmd = ["setpriv", "--reuid=nobody",
                          "--regid=nogroup", "--clear-groups",
                          sys.executable, "-c",
                          _EACCES_WORKER, tree, owner, spool]
            deny_mode = 0o700
        else:
            worker_cmd = [sys.executable, "-c",
                          _EACCES_WORKER, tree, owner, spool]
            deny_mode = 0o000
        proc = subprocess.Popen(
            worker_cmd,
            cwd=base, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True)
        deadline = time.time() + 60
        while (time.time() < deadline
               and not os.path.exists(os.path.join(spool, "ready"))):
            time.sleep(0.05)
        # Worker has imported; NOW remove search permission from
        # the state dir (0o700 root-owned denies 'nobody' as
        # other; 0o000 denies the same-user worker as owner), so
        # the pointer lookup raises EACCES although the CURRENT
        # file exists.
        os.chmod(os.path.join(tree, "form", "state"), deny_mode)
        open(os.path.join(spool, "lock"), "w").write("lock")
        out_stdout, out_stderr = proc.communicate(timeout=120)
        lines = out_stdout.strip().splitlines()
        res = (json.loads(lines[-1]) if lines else
               {"proof": {"lstat": "no-output", "errno": None},
                "state": "subprocess_failed",
                "stderr": out_stderr.strip()[-300:]})
        check("D1PE.eacces_proven_on_lstat",
              res["proof"]["lstat"] == "PermissionError"
              and res["proof"]["errno"] == 13, str(res))
        check("D1PE.classified_unreadable_not_absent",
              res["state"] == "unreadable", str(res))
    finally:
        # Restore search permission so a non-root owner can
        # traverse and delete its own tree (root ignores modes).
        try:
            os.chmod(os.path.join(base, "tree", "form", "state"),
                     0o755)
        except OSError:
            pass
        shutil.rmtree(base, ignore_errors=True)


# ---------------------------------------------------------------- D1SE
def case_single_worker_eacces():
    """Carry the EACCES lookup fault (proven against the real
    filesystem in D1PE) through a lone worker's confirmation:
    os.lstat on the owner's CURRENT path raises PermissionError.
    At 79c3c46 lexists() hides the error, the baseline classifies
    'absent', and the confirm commits. Required:
    baseline_unverifiable refusal with zero checkpoint calls and
    the proposal still pending after fresh-process reload."""
    from form.open import open_program
    import form.mandell.checkpoint_generation as cg
    owner = _owner("D1SE")
    _clean(owner)
    try:
        p0 = open_program(owner)
        pid_a = p0.nursery.add("First Idea", words="alpha").id
        ra = _confirm(p0, pid_a)
        check("D1SE.setup_checkpoint_established", ra["ok"], str(ra))
        worker = open_program(owner)
        pid = worker.nursery.add("Race Idea", words="alpha beta").id
        pointer = cg._pointer_path(owner)
        commits = {"n": 0}
        orig_commit = cg.commit_checkpoint

        def counting_commit(program, *a, **kw):
            commits["n"] += 1
            return orig_commit(program, *a, **kw)

        orig_lstat = os.lstat

        def eacces_lstat(path, *a, **kw):
            if os.fspath(path) == pointer:
                raise PermissionError(
                    13, "Permission denied (injected EACCES)", pointer)
            return orig_lstat(path, *a, **kw)

        cg.commit_checkpoint = counting_commit
        os.lstat = eacces_lstat
        try:
            r = _confirm(worker, pid)
        finally:
            os.lstat = orig_lstat
            cg.commit_checkpoint = orig_commit
        check("D1SE.refused_baseline_unverifiable",
              not r["ok"] and r["reason"] == "baseline_unverifiable",
              str(r))
        check("D1SE.zero_commit_calls", commits["n"] == 0,
              str(commits))
        rel = _reload_fresh(owner, pid)
        check("D1SE.reload_still_pending_no_unit",
              rel["status"] == "pending" and not rel["unit"]
              and rel["label_count"] == 0, str(rel))
    finally:
        _clean(owner)


# ---------------------------------------------------------------- L1
def case_legacy_first_confirm():
    """Clean legacy behavior: an owner with NO established
    checkpoint (proven absence of the CURRENT pointer) confirms
    its first proposal cleanly — the tri-state repair must not
    turn legitimate absence into a failure."""
    from form.open import open_program
    from form.mandell.checkpoint_generation import (
        CheckpointNotEstablished, _read_pointer)
    owner = _owner("LEG")
    _clean(owner)
    try:
        p = open_program(owner)
        pid = p.nursery.add("Race Idea", words="alpha beta").id
        try:
            _read_pointer(owner)
            st = "established"
        except CheckpointNotEstablished:
            st = "absent"
        check("L1.pointer_proven_absent_before_confirm",
              st == "absent", st)
        r = _confirm(p, pid)
        check("L1.first_confirm_ok", r["ok"], str(r))
        rel = _reload_fresh(owner, pid)
        check("L1.reload_confirmed_once",
              rel["status"] == "confirmed" and rel["unit"]
              and rel["label_count"] == 1, str(rel))
    finally:
        _clean(owner)


# ---------------------------------------------------------------- D2
_WORKER = r"""
import json, os, sys, time
sys.path.insert(0, %(REPO)r)
owner, pid, barrier, ready, outp = sys.argv[1:6]
sabotage = sys.argv[6] if len(sys.argv) > 6 else ""
from form.open import open_program
p = open_program(owner)
ctx = p.make_review_context(pid, "test")
open(ready, "w").write("ready")
deadline = time.time() + 60
while not os.path.exists(barrier):
    if time.time() > deadline: sys.exit(3)
    time.sleep(0.02)
if sabotage == "exit17":
    sys.exit(17)
if sabotage == "raise":
    res = {"ok": False, "reason": "raised:RuntimeError"}
    open(outp, "w").write(json.dumps(res))
    print(json.dumps(res))
    sys.exit(0)
try:
    r = p.confirm_proposal(pid, _producer="test", _review_context=ctx)
    res = {"ok": r.get("ok") is True, "reason": r.get("reason")}
except Exception as e:
    res = {"ok": False, "reason": "raised:" + type(e).__name__}
open(outp, "w").write(json.dumps(res))
print(json.dumps(res))
"""


def _race_facts(sabotage=("", "")):
    """Run one barrier-synchronised two-worker race and return the
    raw facts (readiness, exit codes, receipts, reload state)."""
    from form.open import open_program
    owner = _owner("CON")
    _clean(owner)
    tmp = tempfile.mkdtemp(prefix="n31con_")
    try:
        pid = open_program(owner).nursery.add(
            "Race Idea", words="alpha beta").id
        barrier = os.path.join(tmp, "go")
        procs = []
        for k in range(2):
            procs.append(subprocess.Popen(
                [sys.executable, "-c", _WORKER % {"REPO": REPO},
                 owner, pid, barrier, os.path.join(tmp, f"ready{k}"),
                 os.path.join(tmp, f"out{k}.json"), sabotage[k]],
                cwd=REPO, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, text=True))
        deadline = time.time() + 60
        while time.time() < deadline and not all(
                os.path.exists(os.path.join(tmp, f"ready{k}"))
                for k in range(2)):
            time.sleep(0.05)
        both_ready = all(
            os.path.exists(os.path.join(tmp, f"ready{k}"))
            for k in range(2))
        open(barrier, "w").write("go")
        rcs = []
        for prc in procs:
            prc.communicate(timeout=120)
            rcs.append(prc.returncode)
        outs = []
        for k in range(2):
            try:
                outs.append(json.loads(
                    open(os.path.join(tmp, f"out{k}.json")).read()))
            except Exception:  # noqa: BLE001
                outs.append({"ok": None, "reason": "no-output"})
        rel = _reload_fresh(owner, pid)
        return {"both_ready": both_ready, "rcs": rcs, "outs": outs,
                "reload": rel}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        _clean(owner)


def _race_predicates(f):
    """The D2 acceptance contract, as named predicates. Strengthened
    by the Director's 2026-11-06 correction: at the prior head a
    worker exiting 17 after the barrier (no receipt at all) still
    passed, because exit codes were collected but never asserted
    and a missing receipt parsed as ok=None."""
    outs = f["outs"]
    valid = all(isinstance(o.get("ok"), bool) for o in outs)
    winners = [o for o in outs if o.get("ok") is True]
    losers = [o for o in outs if o.get("ok") is False]
    return {
        "both_ready": bool(f["both_ready"]),
        "both_exit_zero": f["rcs"] == [0, 0],
        "both_valid_receipts": valid,
        "exactly_one_ok_one_conflict": (
            len(winners) == 1 and len(losers) == 1
            and losers[0].get("reason") == "nursery_conflict"),
        "winner_preserved": (
            f["reload"]["status"] == "confirmed" and f["reload"]["unit"]
            and f["reload"]["label_count"] == 1),
    }


def case_concurrent(attempt):
    f = _race_facts()
    p = _race_predicates(f)
    detail = f"rcs={f['rcs']} outs={f['outs']} reload={f['reload']}"
    check(f"D2.both_ready_before_release[{attempt}]",
          p["both_ready"], detail)
    check(f"D2.both_exit_zero[{attempt}]", p["both_exit_zero"], detail)
    check(f"D2.both_valid_receipts[{attempt}]",
          p["both_valid_receipts"], detail)
    check(f"D2.exactly_one_ok_one_conflict[{attempt}]",
          p["exactly_one_ok_one_conflict"], detail)
    check(f"D2.concurrent_winner_preserved[{attempt}]",
          p["winner_preserved"], detail)


def case_concurrent_mutants():
    """The strengthened contract must REJECT sabotaged races: a
    worker that exits 17 after the barrier without confirming (the
    Director's mutant) and a worker whose confirm raised. At the
    prior head the first of these was accepted."""
    f = _race_facts(sabotage=("", "exit17"))
    p = _race_predicates(f)
    check("D2M.missing_worker_rejected", not all(p.values()),
          f"predicates={p} rcs={f['rcs']} outs={f['outs']}")
    f2 = _race_facts(sabotage=("", "raise"))
    p2 = _race_predicates(f2)
    check("D2M.raised_worker_rejected", not all(p2.values()),
          f"predicates={p2} rcs={f2['rcs']} outs={f2['outs']}")


def main():
    case_nursery()
    case_program_sequential()
    case_interleaved_commit()
    case_interleaved_unreadable_pointer()
    case_baseline_unreadable()
    case_single_worker_baseline_unreadable()
    case_pointer_classification()
    case_pointer_eacces()
    case_single_worker_eacces()
    case_legacy_first_confirm()
    case_concurrent(1)
    case_concurrent(2)
    case_concurrent_mutants()
    check("cleanup.no_errors", not _CLEANUP_ERRORS, str(_CLEANUP_ERRORS))
    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"nursery_confirm_race_test: {passed}/{len(RESULTS)} PASS")
    return 0 if passed == len(RESULTS) else 1


def smoke() -> bool:
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
