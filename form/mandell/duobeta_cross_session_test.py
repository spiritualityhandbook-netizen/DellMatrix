"""Phase J — DuoBeta cross-session learning (README program).

README §2 listed DuoBeta cross-session learning as PARTIAL: "Works
within session; cross-process persistence of staged proposals not
observed" (a 2026-10-04 observation), and §9 repeated it as a
limitation. The existing dla_i_test "CROSS_PROCESS" section is
same-process save/load into a temp file — by the evidence ladder
that is INTEGRATION, not a process boundary.

This suite proves the real claim at CROSS_PROCESS + REAL_USER_PATH
standard: the full learning lifecycle runs through separate OS
processes of the actual REPL (`python3 -m form.repl`), using only
the documented user contract — work, `save`, restart with `--load`:

  proc A  execute 3 seeds -> 3 completed outcomes -> save
  proc B  --load: outcomes restored; learn propose -> save
  proc C  --load: ledger/inspect show PROPOSED with evidence;
          gate ACCEPTED; apply without confirm blocked (state
          unchanged); apply with confirm APPLIED -> save
  proc D  --load: ledger shows APPLIED — learning survived

Non-vacuity controls:
  - no-save control: a proposal staged in a process that exits
    WITHOUT `save` is absent in the next --load process — the
    persistence proven above comes from the save/load contract,
    not from ambient state leaking between processes.
  - no-load control: a plain start (no --load) sees an empty
    ledger — the restore is the documented --load path, not
    constructor magic.
  - rejection control: a proposal gated REJECTED in one process
    is still REJECTED, with its reason, in the next process —
    negative learning state persists too, not just success.

Isolation: unique owner per run; the owner's state-file absence is
verified before proc A. Cleanup removes exactly the owner's files
via canonical paths; a cleanup failure other than an absent file
fails the suite loudly.
"""

from __future__ import annotations

import glob
import os
import re
import shutil
import subprocess
import sys
import uuid

CHECKS: list = []


def check(name: str, cond: bool, detail: str = "") -> None:
    CHECKS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}"
          + (f" — {detail}" if detail and not cond else ""))


def _cleanup(owner: str) -> None:
    """Remove the test owner's state files via canonical paths.

    Absent files are fine (not every stage creates every file).
    Any other cleanup error is raised — a swallowed cleanup
    failure would silently contaminate later runs.
    """
    from form.dell_matrix.nursery import owner_nursery_path
    from form.persist import _path
    paths = [owner_nursery_path(owner), _path(owner)]
    paths += glob.glob(f"form/state/checkpoint_{owner}_*")
    errors = []
    for path in paths:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
        except OSError as exc:
            errors.append(f"{path}: {exc}")
    try:
        shutil.rmtree(f"form/state/ideas_{owner}")
    except FileNotFoundError:
        pass
    except OSError as exc:
        errors.append(f"ideas_{owner}: {exc}")
    if errors:
        raise AssertionError("cleanup failed: " + "; ".join(errors))


def _repl(commands: list, owner: str, load: bool,
          timeout: int = 120):
    cwd = os.path.abspath(".")
    args = [sys.executable, "-m", "form.repl", "--owner", owner]
    if load:
        args.append("--load")
    env = {**os.environ, "PYTHONPATH": cwd}
    result = subprocess.run(
        args, cwd=cwd, env=env, input="\n".join(commands) + "\n",
        capture_output=True, text=True, timeout=timeout)
    return result.returncode, result.stdout


_OID = re.compile(r"out\d+:[a-f0-9]{32}")
_STAGED = re.compile(r"proposal (\d+) staged")


def smoke() -> bool:
    owner = f"duoxsess_{uuid.uuid4().hex[:8]}"
    try:
        from form.persist import _path
        check("setup: owner state absent before proc A",
              not os.path.exists(_path(owner)))

        # ── Proc A: execute, harvest outcome IDs, save ────────────
        rc, out = _repl(["1[Keep]", "1[Keep]", "1[Keep]",
                         "outcome 1", "outcome 2", "outcome 3",
                         "save", "quit"], owner, load=False)
        check("A: exits clean", rc == 0)
        oids = []
        for m in _OID.finditer(out):
            if m.group(0) not in oids:
                oids.append(m.group(0))
        check("A: three distinct completed outcome IDs",
              len(oids) == 3, f"oids={oids}")
        check("A: session saved", "Session saved." in out)
        if len(oids) != 3:
            return False
        oid_str = " ".join(oids)

        # ── Proc B: --load, outcomes restored, propose, save ─────
        rc, out = _repl(["outcomes",
                         f"learn propose preference 1 from {oid_str}",
                         "save", "quit"], owner, load=True)
        check("B: exits clean", rc == 0)
        check("B: outcomes restored across the process boundary",
              "[3] initiate[1] · completed" in out
              and "[1] initiate[1] · completed" in out, out[-500:])
        m = _STAGED.search(out)
        check("B: proposal staged PROPOSED", m is not None, out[-500:])
        if not m:
            return False
        pid = m.group(1)

        # ── Proc C: --load, gate, guarded apply, save ────────────
        rc, out = _repl(["learn ledger", f"learn inspect {pid}",
                         f"learn gate {pid}", f"learn apply {pid}",
                         f"learn inspect {pid}",
                         f"learn apply {pid} confirm",
                         "save", "quit"], owner, load=True)
        check("C: exits clean", rc == 0)
        check("C: ledger shows the staged proposal PROPOSED",
              f"#{pid} [PROPOSED]" in out, out[-800:])
        check("C: inspect shows all evidence IDs after restart",
              all(o in out for o in oids), out[-800:])
        check("C: gate ACCEPTED in a later process",
              f"proposal {pid}: GATE ACCEPTED" in out, out[-800:])
        check("C: apply without confirm blocked",
              "explicit authorization required" in out, out[-800:])
        check("C: blocked apply left the proposal ACCEPTED, not APPLIED",
              f"proposal {pid} [ACCEPTED]" in out, out[-800:])
        check("C: apply with confirm APPLIED",
              f"proposal {pid}: APPLIED to DuoBeta learned state" in out,
              out[-800:])

        # ── Proc D: --load, APPLIED persisted ────────────────────
        rc, out = _repl(["learn ledger", "quit"], owner, load=True)
        check("D: APPLIED survives into a fourth process",
              f"#{pid} [APPLIED]" in out, out[-500:])

        # ── No-save control: staged but never saved -> absent ────
        rc, out = _repl([f"learn propose preference 1 from {oid_str}",
                         "quit"], owner, load=True)
        m2 = _STAGED.search(out)
        check("E: second proposal staged in-process", m2 is not None,
              out[-500:])
        if m2:
            pid2 = m2.group(1)
            rc, out = _repl(["learn ledger", "quit"], owner, load=True)
            check("E: unsaved proposal absent after restart "
                  "(persistence comes from save, not leakage)",
                  f"#{pid2} [" not in out and f"#{pid} [APPLIED]" in out,
                  out[-500:])

        # ── No-load control: plain start restores nothing ────────
        rc, out = _repl(["learn ledger", "quit"], owner, load=False)
        check("F: plain start (no --load) sees an empty ledger",
              "empty (no proposals yet)" in out, out[-500:])

        # ── Rejection control: REJECTED persists with reason ─────
        rc, out = _repl(["learn propose preference 1 from bad-oid-x "
                         "bad-oid-y", "learn ledger", "save", "quit"],
                        owner, load=True)
        m3 = _STAGED.search(out)
        check("G: bad-evidence proposal staged", m3 is not None,
              out[-500:])
        if m3:
            pid3 = m3.group(1)
            rc, out = _repl([f"learn gate {pid3}", "save", "quit"],
                            owner, load=True)
            check("G: gate REJECTED in a later process",
                  f"proposal {pid3}: GATE REJECTED" in out, out[-500:])
            rc, out = _repl([f"learn inspect {pid3}", "quit"],
                            owner, load=True)
            check("G: REJECTED status and reason persist",
                  f"proposal {pid3} [REJECTED]" in out
                  and "insufficient_evidence" in out, out[-600:])
    finally:
        _cleanup(owner)

    passed = sum(1 for _, ok in CHECKS if ok)
    print(f"=== DuoBeta cross-session: {passed}/{len(CHECKS)} ===")
    return passed == len(CHECKS)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
