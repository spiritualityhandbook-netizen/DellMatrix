#!/usr/bin/env python3
"""LOCK-ORDER CENSUS — Part I (ARCH-002 lock graph, deadlock-freedom
evidence; PART_I_PLAN_2026-11-20 §5.2).

WHAT THIS SUITE PROVES (and what it does not):

1. STATIC CENSUS (the pin): in form/ PRODUCTION code there is
   exactly ONE lock primitive — form/owner_state_lock.py (a
   per-owner kernel file lock) — and exactly FOUR acquisition
   sites, one per file, each taking the program's OWN owner:

     form/mandell/unit_binding.py      bind transaction
     form/persist_rest.py              save funnel
     form/dell_matrix/confirm_lineage.py  confirm commit lock
     form/mandell/unit_containment.py  containment _LockGate

   No threading.Lock/RLock/Semaphore/Condition/Event/Barrier, no
   flock, no msvcrt.locking anywhere else in production code.
   A fifth site, a second primitive, or a site locking a FOREIGN
   owner turns this suite RED — that is the tripwire working.

   Classification (pinned, explicit): production = every .py
   under form/ EXCEPT test/proof/harness files: *_test.py,
   *_tests.py, *_test_spec.py, *_child.py (e.g.
   track_d_td1_r2_child.py, a test helper that legitimately calls
   the primitive), *_proof.py, *_circuit.py, *_regressions.py and
   regress.py (the harness). gui/server.py's server-local
   threading.RLock is OUTSIDE this census's scope (form/ only);
   it is censused by the CH-17 H9 suite.

2. RUNTIME LOCK-ORDER GRAPH: the four sites are instrumented
   (the lazy per-call import in all four means one patch point)
   while REAL operations run — save, bind, containment nest,
   confirm. Every held stack names exactly ONE owner (nesting is
   always a same-owner re-entrant join through the ONE
   primitive), observed nesting depth never exceeds 3, and the
   observed edge set is pinned: with a single per-owner lock key
   there is no cross-owner ordering to get wrong, so deadlock by
   lock-order inversion is impossible by construction — the storm
   legs below are the empirical belt on that argument.

3. ADVERSARIAL STORMS: threads running the production operations
   in OPPOSITE orders against one owner, and two genuine OS
   processes racing bind+save on one owner (CROSS_PROCESS),
   following the product's own multiwriter protocol — a stale
   instance is refused (BindingRefused) and a binding-losing save
   is refused (BindingLossSaveError); the writer reloads and
   retries (the TD1-R2 contract). All work completes inside a
   hard timeout, no binding is lost, and the final persisted
   state loads coherently.

State isolation: dedicated owners only; owner-scoped cleanup
(the TD1-R2 idiom) removes exactly this suite's files and FAILS
LOUDLY if a removal fails. Evidence classes are named per leg:
static census = source truth; in-process storms = INTEGRATION;
the subprocess leg = CROSS_PROCESS.
"""

from __future__ import annotations

import inspect
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}"
          + (f" | {detail}" if detail and not cond else ""))


# ---------------------------------------------------------------
# owner-scoped cleanup (TD1-R2 idiom; fails loudly)
# ---------------------------------------------------------------

def _cleanup(owner):
    from form.persist import _STATE_DIR, _safe_owner
    safe = _safe_owner(owner)
    files = [os.path.join(_STATE_DIR, f"program_{safe}.json"),
             os.path.join(_STATE_DIR, f"graph_{safe}.json"),
             os.path.join(_STATE_DIR, f"graph_{safe}.journal.json"),
             os.path.join(_STATE_DIR, ".locks", f"{safe}.lock")]
    ideas_dir = os.path.join(_STATE_DIR, f"ideas_{safe}")
    for f in files:
        if os.path.isfile(f):
            os.remove(f)
    if os.path.isdir(ideas_dir):
        shutil.rmtree(ideas_dir)
    if os.path.isdir(_STATE_DIR):
        for name in os.listdir(_STATE_DIR):
            if name.startswith(f"program_{safe}_cp_"):
                os.remove(os.path.join(_STATE_DIR, name))
    leftovers = [f for f in files if os.path.isfile(f)]
    if leftovers or os.path.isdir(ideas_dir):
        raise RuntimeError(f"lock census cleanup incomplete: {leftovers}")


# ---------------------------------------------------------------
# static census
# ---------------------------------------------------------------

_SKIP_SUFFIXES = ("_test.py", "_tests.py", "_test_spec.py", "_child.py",
                  "_proof.py", "_circuit.py", "_regressions.py")
_SKIP_NAMES = {"regress.py"}
_SKIP_DIRS = {"state", "__pycache__"}


def _production_files():
    out = []
    base = os.path.join(ROOT, "form")
    for d, dirs, files in os.walk(base):
        dirs[:] = [x for x in dirs if x not in _SKIP_DIRS]
        for f in sorted(files):
            if not f.endswith(".py"):
                continue
            if f in _SKIP_NAMES or f.endswith(_SKIP_SUFFIXES):
                continue
            out.append(os.path.join(d, f))
    return sorted(out)


def _rel(path):
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


_KERNEL_PATTERNS = [re.compile(r"flock\s*\("),
                    re.compile(r"msvcrt\.locking")]
_THREADING_PATTERNS = [
    re.compile(r"threading\.(Lock|RLock|Semaphore|Condition|Event"
               r"|Barrier)\s*\("),
    re.compile(r"from\s+threading\s+import\s+[^\n]*\b"
               r"(Lock|RLock|Semaphore|Condition|Event|Barrier)\b"),
    re.compile(r"multiprocessing\.(Lock|RLock|Semaphore)\s*\("),
]

# The pinned acquisition census: file -> owner-argument idiom.
_PINNED_SITES = {
    "form/mandell/unit_binding.py": "program.owner",
    "form/persist_rest.py": "program.owner",
    "form/dell_matrix/confirm_lineage.py": "program.owner",
    "form/mandell/unit_containment.py": "self._program.owner",
}


def _static_census():
    prod = _production_files()
    kernel_homes, threading_homes = {}, {}
    acq = {}
    for path in prod:
        rel = _rel(path)
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        if any(p.search(text) for p in _KERNEL_PATTERNS):
            kernel_homes[rel] = True
        if any(p.search(text) for p in _THREADING_PATTERNS):
            threading_homes[rel] = True
        if rel == "form/owner_state_lock.py":
            continue
        calls = re.findall(r"owner_state_lock\(([^)]*)\)", text)
        # drop doc/comment mentions: a call line carries no '#'
        real = [c for c in calls]
        if real:
            acq[rel] = real
    check("census_kernel_lock_lives_only_in_the_one_primitive",
          kernel_homes == {"form/owner_state_lock.py": True},
          f"kernel lock patterns found in: {sorted(kernel_homes)}")
    check("census_no_threading_or_multiprocessing_locks_in_form",
          threading_homes == {},
          f"threading/mp lock primitives found in: "
          f"{sorted(threading_homes)}")
    ok = set(acq) == set(_PINNED_SITES) and all(
        len(v) == 1 for v in acq.values())
    check("census_exactly_four_acquisition_sites_one_per_file",
          ok, f"acquisition census: "
              f"{ {k: len(v) for k, v in sorted(acq.items())} }")
    owner_ok = all(
        _PINNED_SITES[rel] in (acq.get(rel) or [""])[0]
        for rel in _PINNED_SITES)
    check("census_every_site_locks_its_own_programs_owner",
          owner_ok,
          f"site args: { {k: v for k, v in sorted(acq.items())} }")


# ---------------------------------------------------------------
# runtime lock-order graph (instrumented real operations)
# ---------------------------------------------------------------

class _Recorder:
    def __init__(self):
        self.mutex = threading.Lock()
        self.stacks = {}
        self.edges = []
        self.max_depth = 0
        self.mixed_owner_stacks = 0
        self.events = 0

    def _site(self):
        for fr in inspect.stack()[1:]:
            fn = fr.filename
            if fn.endswith(("owner_state_lock.py",
                            "lock_order_census_test.py")):
                continue
            return os.path.basename(fn)
        return "<unknown>"

    def wrap(self, factory):
        rec = self

        class _Ctx:
            def __init__(self, real, owner, site):
                self._real, self._owner, self._site = real, owner, site

            def __enter__(self):
                self._real.__enter__()
                tid = threading.get_ident()
                with rec.mutex:
                    st = rec.stacks.setdefault(tid, [])
                    if st:
                        rec.edges.append((st[-1][1], self._site))
                    st.append((self._owner, self._site))
                    rec.max_depth = max(rec.max_depth, len(st))
                    rec.events += 1
                    if len({o for o, _ in st}) > 1:
                        rec.mixed_owner_stacks += 1
                return self

            def __exit__(self, *exc):
                try:
                    return self._real.__exit__(*exc)
                finally:
                    tid = threading.get_ident()
                    with rec.mutex:
                        st = rec.stacks.get(tid, [])
                        if st:
                            st.pop()

        def _factory(owner):
            return _Ctx(factory(owner), owner, rec._site())

        return _factory


_ALLOWED_EDGES = {
    # outer site -> inner site, observed on the real paths:
    ("unit_binding.py", "persist_rest.py"),      # bind saves inside
    ("unit_binding.py", "unit_binding.py"),      # bind re-joins bind
    ("unit_containment.py", "unit_binding.py"),  # nest binds inside
    ("unit_containment.py", "persist_rest.py"),  # containment saves
    ("confirm_lineage.py", "persist_rest.py"),   # confirm saves
    ("confirm_lineage.py", "confirm_lineage.py"),
    ("persist_rest.py", "persist_rest.py"),      # save re-joins save
    ("open.py", "persist_rest.py"),              # Program.save funnel
}


def _runtime_graph():
    from form import owner_state_lock as ols
    from form.open import open_program
    from form.mandell.unit_binding import bind_unit_to_idea
    from form.mandell.unit_containment import nest_units
    from form import persist_rest

    owner = "LockCensusGraph"
    _cleanup(owner)
    rec = _Recorder()
    real_factory = ols.owner_state_lock
    ols.owner_state_lock = rec.wrap(real_factory)
    try:
        p = open_program(owner)
        p.place("loc-a", "Lock A")
        p.place("loc-b", "Lock B")
        persist_rest.save(p)                                # depth 1
        bind_unit_to_idea(p, "loc-a", subject="Ace")        # bind>save
        nest_units(p, "loc-b", "loc-a", subject="Ace")      # gate>bind
        pid = p.nursery.add(label="lock census idea",
                            words=["lock", "census"], kind="new",
                            parents=[], origin="suite:lock-census",
                            reason="lock-order census").id
        out = p.confirm_proposal(
            pid, _producer="repl_user",
            _review_context=p.make_review_context(pid, "repl_user"))
        confirm_ran = isinstance(out, dict) and out.get("ok") is not False
    finally:
        ols.owner_state_lock = real_factory
        _cleanup(owner)
    check("graph_instrumentation_saw_real_acquisitions",
          rec.events >= 8 and confirm_ran,
          f"events={rec.events} confirm_out={out}")
    check("graph_no_stack_ever_holds_two_owners",
          rec.mixed_owner_stacks == 0,
          f"mixed stacks: {rec.mixed_owner_stacks}")
    check("graph_nesting_depth_never_exceeds_three",
          1 <= rec.max_depth <= 3, f"max_depth={rec.max_depth}")
    bad = [e for e in rec.edges if e not in _ALLOWED_EDGES]
    check("graph_edges_within_the_pinned_lock_order",
          not bad, f"edges={sorted(set(rec.edges))} bad={bad}")
    check("graph_deep_nesting_actually_exercised",
          rec.max_depth >= 2 and any(
              e[0] == "unit_containment.py" for e in rec.edges),
          f"max_depth={rec.max_depth} edges={sorted(set(rec.edges))}")


# ---------------------------------------------------------------
# adversarial storms
# ---------------------------------------------------------------

def _storm_threads():
    from form.open import open_program
    from form.mandell.unit_binding import bind_unit_to_idea
    from form.owner_state_lock import OwnerLockBusy

    owner = "LockCensusStorm"
    _cleanup(owner)
    units = [f"storm-{i}" for i in range(8)]
    setup = open_program(owner)
    for u in units:
        setup.place(u, f"Storm {u}")
    from form import persist_rest
    persist_rest.save(setup)

    errors, retries = [], [0]
    barrier = threading.Barrier(len(units))

    from form.mandell.unit_binding import BindingRefused
    from form.persist_rest import BindingLossSaveError

    def worker(idx, unit):
        try:
            from form.open import Program
            prog = Program.load(owner)
            barrier.wait(timeout=30)
            for rnd in range(12):
                # Opposite orders across the two halves of the
                # storm: bind-then-save vs save-then-bind. The
                # product's multiwriter contract (TD1-R2 / SM-08):
                # a stale instance is REFUSED (BindingRefused) and
                # a save that would drop another writer's binding
                # is REFUSED (BindingLossSaveError) — the writer
                # reloads and retries. The storm follows that
                # protocol; deadlock or a lost binding fails it.
                for attempt in range(80):
                    try:
                        if idx % 2 == 0:
                            bind_unit_to_idea(
                                prog, unit, subject=f"Storm{idx}")
                            persist_rest.save(prog)
                        else:
                            persist_rest.save(prog)
                            bind_unit_to_idea(
                                prog, unit, subject=f"Storm{idx}")
                        break
                    except OwnerLockBusy:
                        retries[0] += 1
                        time.sleep(0.05)
                    except (BindingRefused, BindingLossSaveError):
                        retries[0] += 1
                        prog = Program.load(owner)
                        time.sleep(0.02)
                else:
                    raise RuntimeError(
                        f"round {rnd} never landed for {unit}")
        except Exception as exc:  # noqa: BLE001 - recorded, asserted
            errors.append(f"{unit}: {type(exc).__name__}: {exc}")

    threads = [threading.Thread(target=worker, args=(i, u))
               for i, u in enumerate(units)]
    t0 = time.monotonic()
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=90)
    elapsed = time.monotonic() - t0
    alive = [t.name for t in threads if t.is_alive()]
    try:
        from form.open import Program
        final = Program.load(owner)
        bound = [u for u in units
                 if getattr(final.cube.session.plane.units.get(u),
                            "idea_id", None)]
        check("storm_threads_opposite_orders_all_complete",
              not alive and not errors and elapsed < 90,
              f"alive={alive} errors={errors} elapsed={elapsed:.1f}s "
              f"busy_retries={retries[0]}")
        check("storm_threads_final_state_coherent_all_bound",
              bound == units, f"bound={bound}")
    finally:
        _cleanup(owner)


_CHILD_SRC = r'''
import json, os, sys, time
sys.path.insert(0, {root!r})
owner, unit, gofile, rounds = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
deadline = time.time() + 60
while not os.path.exists(gofile):
    if time.time() > deadline:
        print("child: go-file timeout"); sys.exit(3)
    time.sleep(0.02)
from form.open import Program
from form.mandell.unit_binding import (
    bind_unit_to_idea, BindingRefused)
from form.persist_rest import BindingLossSaveError
from form.owner_state_lock import OwnerLockBusy
from form import persist_rest
prog = Program.load(owner)
for i in range(rounds):
    for attempt in range(120):
        try:
            bind_unit_to_idea(prog, unit, subject="StormChild")
            persist_rest.save(prog)
            break
        except OwnerLockBusy:
            time.sleep(0.05)
        except (BindingRefused, BindingLossSaveError):
            prog = Program.load(owner)
            time.sleep(0.02)
    else:
        print("child: round never landed"); sys.exit(4)
print(json.dumps({"ok": True, "unit": unit}))
'''


def _storm_processes():
    import tempfile
    from form.open import open_program, Program
    from form import persist_rest

    owner = "LockCensusProc"
    _cleanup(owner)
    setup = open_program(owner)
    setup.place("proc-a", "Proc A")
    setup.place("proc-b", "Proc B")
    persist_rest.save(setup)
    tmp = tempfile.mkdtemp(prefix="lock_census_")
    gofile = os.path.join(tmp, "go")
    child = os.path.join(tmp, "child.py")
    with open(child, "w", encoding="utf-8") as fh:
        fh.write(_CHILD_SRC.replace("{root!r}", repr(ROOT)))
    procs = []
    try:
        for unit in ("proc-a", "proc-b"):
            procs.append(subprocess.Popen(
                [sys.executable, child, owner, unit, gofile, "10"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True))
        with open(gofile, "w", encoding="utf-8") as fh:
            fh.write("go")
        outs, errs, rcs = [], [], []
        for pr in procs:
            o, e = pr.communicate(timeout=120)
            outs.append(o.strip())
            errs.append(e.strip()[-300:])
            rcs.append(pr.returncode)
        final = Program.load(owner)
        bound = [u for u in ("proc-a", "proc-b")
                 if getattr(final.cube.session.plane.units.get(u),
                            "idea_id", None)]
        check("storm_cross_process_both_children_complete",
              rcs == [0, 0] and all('"ok": true' in o for o in outs),
              f"rcs={rcs} outs={outs} errs={errs}")
        check("storm_cross_process_final_state_coherent",
              bound == ["proc-a", "proc-b"], f"bound={bound}")
    finally:
        for pr in procs:
            if pr.poll() is None:
                pr.kill()
        shutil.rmtree(tmp, ignore_errors=True)
        _cleanup(owner)


def run_all():
    _static_census()
    _runtime_graph()
    _storm_threads()
    _storm_processes()
    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"LOCK ORDER CENSUS: {passed}/{len(RESULTS)} GREEN")
    return passed == len(RESULTS)


def smoke() -> bool:
    return run_all()


if __name__ == "__main__":
    raise SystemExit(0 if smoke() else 1)
