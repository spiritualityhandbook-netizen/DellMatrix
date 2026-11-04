"""Track D TD-1-R2 — atomic owner-state commit protection.

Director directive 2026-11-04: R1's fingerprint gate is an
optimistic version check, not an atomic compare-and-swap — the
comparison and the final replacement were separate moments.
R2 closes that window: validation and replacement run inside
one enforceable owner-scoped transaction (form.owner_state_lock,
a kernel-held flock that is never unlinked and never silently
downgraded), and ordinary Program saves join the same
transaction with a stale-instance refusal, so a stale save can
no longer silently overwrite a newer binding.

Semantics pinned (from the circuit ground, agreed before coding):
a lock serializes writers; it does not merge them. The loser of
a race gets an EXPLICIT refusal, reloads, retries, and succeeds
— 'no lost bindings' means the winner is never overwritten and
the final state can carry both bindings, never that two stale
writers both succeed in one pass.

Check 1 (a stale save that would lose a binding) is the
failing-first point: on pre-R2 code that save succeeds silently
and the binding is gone. Check 0b pins the narrowed contract's
other half: a stale save losing NO binding proceeds — the
refusal is keyed to bindings (the harm the Director named),
after regression showed the general stale refusal breaking
legitimate snapshot-restore / rollback / unbound-authoring
flows. The race checks use GENUINE subprocesses (CROSS_PROCESS)
coordinated by barrier files with bounded waits — no sleeps as
synchronization, no seam injection.

Run: python3 -m form.track_d_td1_r2_test
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import threading
import time

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}"
          + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        raise AssertionError(name)


OWNER = "Td1R2Probe"
OWNER2 = "Td1R2ProbeB"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _paths(owner):
    from form.persist import _STATE_DIR, _safe_owner
    safe = _safe_owner(owner)
    return {
        "program": os.path.join(_STATE_DIR, f"program_{safe}.json"),
        "lock": os.path.join(_STATE_DIR, ".locks",
                             f"program_{safe}.json.lock"),
        "ideas": os.path.join(_STATE_DIR, f"ideas_{safe}"),
        "graph": os.path.join(_STATE_DIR, f"graph_{safe}.json"),
        "graph_journal": os.path.join(
            _STATE_DIR, f"graph_{safe}.journal.json"),
        "state_dir": _STATE_DIR,
        "safe": safe,
    }


def _cleanup(owner):
    p = _paths(owner)
    for f in (p["program"], p["graph"], p["graph_journal"],
              p["lock"]):
        if os.path.isfile(f):
            os.remove(f)
    if os.path.isdir(p["ideas"]):
        shutil.rmtree(p["ideas"])
    for name in os.listdir(p["state_dir"]):
        if name.startswith(f"program_{p['safe']}_cp_"):
            os.remove(os.path.join(p["state_dir"], name))
    return p


def _file_hash(path):
    if not os.path.isfile(path):
        return None
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _wait_for(path, timeout=30.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if os.path.isfile(path):
            return True
        time.sleep(0.01)
    return False


def _spawn(tmpdir, name, **kw):
    args = [sys.executable, "-m", "form.track_d_td1_r2_child"]
    for k, v in kw.items():
        args += [f"--{k}", str(v)]
    return subprocess.Popen(args, cwd=ROOT,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)


def _read_result(path, proc, timeout=60.0):
    ok = _wait_for(path, timeout)
    if proc.poll() is None:
        proc.wait(timeout=10)
    if not ok:
        return {"outcome": "no_result"}
    with open(path) as f:
        return json.load(f)


def run_all():
    from form.open import open_program
    from form import persist_rest
    from form.mandell import unit_binding
    from form.mandell.idea_persist import list_idea_ids

    import tempfile
    tmpdir = tempfile.mkdtemp(prefix="td1r2-")
    _cleanup(OWNER)
    _cleanup(OWNER2)
    try:
        p = _paths(OWNER)
        prog = open_program(OWNER)
        prog.place("r2-alpha", "Alpha R2")
        prog.place("r2-beta", "Beta R2")
        prog.place("r2-gamma", "Gamma R2")
        persist_rest.save(prog)
        from form.mandell.semantic_graph import SemanticGraph
        SemanticGraph.load(OWNER).save()
        graph_before = (_file_hash(p["graph"]),
                        _file_hash(p["graph_journal"]))

        # -- 0b. narrowed contract: a stale save losing NO binding
        # proceeds (the refusal is keyed to bindings — the harm
        # the Director named — not to any state change; snapshot
        # restore / rollback / unbound authoring flows keep their
        # whole-state semantics).
        pre_a = persist_rest.load(OWNER, activate=False)
        pre_b = persist_rest.load(OWNER, activate=False)
        pre_a.place("r2-ephemeral", "Ephemeral")
        persist_rest.save(pre_a)
        persist_rest.save(pre_b)  # stale, but no binding exists yet
        after = persist_rest.load(OWNER, activate=False)
        check("a stale save that loses no binding proceeds "
              "(refusal is binding-keyed)",
              "r2-ephemeral" not in after.cube.session.plane.units)

        # -- 1. stale save losing a BINDING refused (FAILING-FIRST) -
        inst_a = persist_rest.load(OWNER, activate=False)
        inst_b = persist_rest.load(OWNER, activate=False)
        receipt = inst_a.bind_unit_to_idea("r2-alpha", subject="Ace")
        hash_after_bind = _file_hash(p["program"])
        try:
            persist_rest.save(inst_b)
            check("stale save losing a binding is refused", False)
        except persist_rest.BindingLossSaveError:
            check("stale save losing a binding is refused",
                  _file_hash(p["program"]) == hash_after_bind)
        on_disk = persist_rest.load(OWNER, activate=False)
        check("the newer binding survives the stale save attempt",
              on_disk.cube.session.plane.units["r2-alpha"].idea_id
              == receipt["idea_id"])

        # -- 2. current / fresh instances save normally ------------
        inst_b2 = persist_rest.load(OWNER, activate=False)
        persist_rest.save(inst_b2)
        prog_b = open_program(OWNER2)
        prog_b.place("r2-other", "Other owner unit")
        persist_rest.save(prog_b)
        check("current and fresh instances save normally",
              os.path.isfile(_paths(OWNER2)["program"]))

        # -- 3. corrupt-file save allowance (disclosed) ------------
        with open(p["program"], "wb") as f:
            f.write(b"{corrupt{{{ not json")
        persist_rest.save(inst_b2)  # the live instance is the repair
        with open(p["program"], "rb") as f:
            json.loads(f.read().decode("utf-8"))
        check("a live instance's save repairs corrupt bytes "
              "(no readable state existed to protect)", True)

        # -- 4. lock busy: another thread, bounded wait ------------
        from form.owner_state_lock import (OwnerLockBusy,
                                           owner_state_lock)
        busy = {}

        def contender():
            t0 = time.monotonic()
            try:
                with owner_state_lock(OWNER, timeout=0.5):
                    busy["outcome"] = "acquired"
            except OwnerLockBusy:
                busy["outcome"] = "busy"
                busy["elapsed"] = time.monotonic() - t0

        with owner_state_lock(OWNER):
            th = threading.Thread(target=contender)
            th.start()
            th.join(timeout=10)
        check("a contending thread gets a bounded busy refusal",
              busy.get("outcome") == "busy"
              and busy.get("elapsed", 99) < 5.0)

        # -- 4b. an ordinary canonical save waits for the lock -----
        save_done = threading.Event()
        saver = {}

        def saving_thread():
            inst = persist_rest.load(OWNER, activate=False)
            persist_rest.save(inst)
            saver["done"] = True
            save_done.set()

        with owner_state_lock(OWNER):
            th2 = threading.Thread(target=saving_thread)
            th2.start()
            waited = save_done.wait(timeout=1.5)
        th2.join(timeout=15)
        check("an ordinary canonical save cannot bypass a held lock",
              not waited and saver.get("done") is True)

        # -- 5/6. lock recovery: SIGKILLed holder frees the lock ---
        ready = os.path.join(tmpdir, "hold.ready")
        holder = _spawn(tmpdir, "hold", mode="hold", owner=OWNER,
                        ready=ready, sleep=60)
        try:
            check("holder child acquired the lock",
                  _wait_for(ready, 30))
            t0 = time.monotonic()
            try:
                with owner_state_lock(OWNER, timeout=0.5):
                    blocked = False
            except OwnerLockBusy:
                blocked = True
            check("a live holder blocks acquisition", blocked)
            holder.send_signal(signal.SIGKILL)
            holder.wait(timeout=10)
            with owner_state_lock(OWNER, timeout=5):
                pass
            check("a SIGKILLed holder's lock recovers (kernel "
                  "release), within the bound",
                  time.monotonic() - t0 < 8.0)
        finally:
            if holder.poll() is None:
                holder.kill()
                holder.wait(timeout=10)

        # -- 6b. a bind against a live holder refuses state_locked -
        import form.owner_state_lock as _lock_mod
        ready3 = os.path.join(tmpdir, "hold3.ready")
        holder3 = _spawn(tmpdir, "hold3", mode="hold", owner=OWNER,
                         ready=ready3, sleep=30)
        try:
            _wait_for(ready3, 30)
            old_timeout = _lock_mod.LOCK_TIMEOUT_S
            _lock_mod.LOCK_TIMEOUT_S = 1.0
            try:
                fresh2 = persist_rest.load(OWNER, activate=False)
                fresh2.bind_unit_to_idea("r2-gamma", subject="Ace")
                locked_ok = False
            except unit_binding.BindingRefused as e:
                locked_ok = e.kind == "state_locked"
            finally:
                _lock_mod.LOCK_TIMEOUT_S = old_timeout
            check("bind refuses state_locked against a live holder",
                  locked_ok)
        finally:
            if holder3.poll() is None:
                holder3.kill()
                holder3.wait(timeout=10)

        # -- 7. re-entrancy: bind + save inside an outer lock ------
        fresh = persist_rest.load(OWNER, activate=False)
        with owner_state_lock(OWNER):
            r = fresh.bind_unit_to_idea("r2-beta", subject="Ace")
            persist_rest.save(fresh)
        check("bind and save join an outer lock without deadlock",
              r["status"] in ("bound", "already_bound"))

        # -- 8. genuine race, SAME unit ----------------------------
        n_ideas_before = len(list_idea_ids(OWNER))
        setup = persist_rest.load(OWNER, activate=False)
        setup.place("r2-race", "Race R2")
        persist_rest.save(setup)
        barrier = os.path.join(tmpdir, "go")
        ra, rb = (os.path.join(tmpdir, "a.ready"),
                  os.path.join(tmpdir, "b.ready"))
        pa = _spawn(tmpdir, "a", mode="bind", owner=OWNER,
                    unit="r2-race", subject="RacerA", ready=ra,
                    barrier=barrier,
                    result=os.path.join(tmpdir, "a.json"))
        pb = _spawn(tmpdir, "b", mode="bind", owner=OWNER,
                    unit="r2-race", subject="RacerB", ready=rb,
                    barrier=barrier,
                    result=os.path.join(tmpdir, "b.json"))
        both_ready = _wait_for(ra, 60) and _wait_for(rb, 60)
        check("both racers loaded and ready", both_ready)
        with open(barrier, "w") as f:
            f.write("go")
        out_a = _read_result(os.path.join(tmpdir, "a.json"), pa)
        out_b = _read_result(os.path.join(tmpdir, "b.json"), pb)
        outcomes = sorted([out_a.get("outcome"), out_b.get("outcome")])
        winner = out_a if out_a.get("outcome") == "bound" else out_b
        check("same-unit race: exactly one process binds",
              outcomes == ["bound", "refused"]
              and (out_a if out_a.get("outcome") == "refused"
                   else out_b).get("kind") in ("conflict",
                                               "state_locked"),
              detail=f"A={out_a} B={out_b}")
        final = persist_rest.load(OWNER, activate=False)
        check("the persisted pointer is the winner's; exactly one "
              "shell was minted",
              final.cube.session.plane.units["r2-race"].idea_id
              == winner.get("idea_id")
              and len(list_idea_ids(OWNER)) == n_ideas_before + 1)

        # -- 9. genuine race, DIFFERENT units + retry --------------
        prog2 = persist_rest.load(OWNER, activate=False)
        for u in ("r2-duo-a", "r2-duo-b"):
            if u not in prog2.cube.session.plane.units:
                prog2.place(u, f"Duo {u}")
        persist_rest.save(prog2)
        barrier2 = os.path.join(tmpdir, "go2")
        rc, rd = (os.path.join(tmpdir, "c.ready"),
                  os.path.join(tmpdir, "d.ready"))
        pc = _spawn(tmpdir, "c", mode="bind", owner=OWNER,
                    unit="r2-duo-a", subject="RacerC", ready=rc,
                    barrier=barrier2,
                    result=os.path.join(tmpdir, "c.json"))
        pd = _spawn(tmpdir, "d", mode="bind", owner=OWNER,
                    unit="r2-duo-b", subject="RacerD", ready=rd,
                    barrier=barrier2,
                    result=os.path.join(tmpdir, "d.json"))
        _wait_for(rc, 60) and _wait_for(rd, 60)
        with open(barrier2, "w") as f:
            f.write("go")
        out_c = _read_result(os.path.join(tmpdir, "c.json"), pc)
        out_d = _read_result(os.path.join(tmpdir, "d.json"), pd)
        duo = sorted([out_c.get("outcome"), out_d.get("outcome")])
        check("different-units race: one binds, one is refused "
              "(no silent overwrite)", duo == ["bound", "refused"],
              detail=f"C={out_c} D={out_d}")
        loser_unit = ("r2-duo-b" if out_c.get("outcome") == "bound"
                      else "r2-duo-a")
        retry = persist_rest.load(OWNER, activate=False)
        rr = retry.bind_unit_to_idea(loser_unit, subject="Retry")
        final2 = persist_rest.load(OWNER, activate=False)
        units = final2.cube.session.plane.units
        check("after reload+retry BOTH bindings persist — none lost",
              rr["status"] == "bound"
              and units["r2-duo-a"].idea_id
              and units["r2-duo-b"].idea_id)

        # -- 10. failed commit releases the lock --------------------
        try:
            persist_rest.save(retry, _fail_at="replace")
            failed_ok = False
        except Exception:
            failed_ok = True
        t0 = time.monotonic()
        with owner_state_lock(OWNER, timeout=5):
            pass
        check("a failed commit inside the lock releases it",
              failed_ok and time.monotonic() - t0 < 4.0)

        # -- 11. two owners never block each other ------------------
        ready2 = os.path.join(tmpdir, "other.ready")
        res2 = os.path.join(tmpdir, "other.json")
        with owner_state_lock(OWNER):
            pe = _spawn(tmpdir, "e", mode="bind", owner=OWNER2,
                        unit="r2-other", subject="Other",
                        ready=ready2, result=res2)
            out_e = _read_result(res2, pe, timeout=15)
        check("another owner's bind completes while this owner's "
              "lock is held", out_e.get("outcome") in ("bound",
                                                       "already_bound"),
              detail=str(out_e))

        # -- 12. F1 still fires, now inside the lock ----------------
        with open(p["program"], "wb") as f:
            f.write(b"{corrupt{{{ not json")
        corrupt_hash = _file_hash(p["program"])
        try:
            retry.bind_unit_to_idea("r2-gamma", subject="Ace")
            check("corrupt state still refuses before minting", False)
        except unit_binding.BindingRefused as e:
            check("corrupt state still refuses before minting",
                  e.kind == "state_unreadable"
                  and _file_hash(p["program"]) == corrupt_hash)

        graph_after = (_file_hash(p["graph"]),
                       _file_hash(p["graph_journal"]))
        check("R2 performs zero SemanticGraph writes",
              graph_before == graph_after)

        print(f"TD1-R2: {sum(1 for _, c in RESULTS if c)}/"
              f"{len(RESULTS)} GREEN")
    finally:
        _cleanup(OWNER)
        _cleanup(OWNER2)
        shutil.rmtree(tmpdir, ignore_errors=True)


def smoke() -> bool:
    try:
        run_all()
        return True
    except Exception as e:
        print(f"TD1-R2 SMOKE FAILED: {e}")
        return False


if __name__ == "__main__":
    run_all()
    sys.exit(0)
