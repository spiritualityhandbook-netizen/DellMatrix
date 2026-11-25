#!/usr/bin/env python3
"""SM-16 — Dell 37 REPL error-visibility regression.

Defect (confirmed, reproduced at baseline c5bb3a2): executing the bare
seed ``37[Nurture]`` fails honestly at the executor —
``ok=False, error="add idea requires a label"`` with zero mutation —
but the REPL showed nothing but the Mandell/English echo. The handler
in core_i_ops returned the failure without appending any message, and
the REPL's seed-result display (_apply_seed_result) printed only
``messages``, never ``error``. The user saw a silent no-op.

Repair (two layers, no new authority):
- core_i_ops Dell 37 default-add appends a failure message before
  returning, following the file's own sibling pattern (Confirm failed /
  Reject failed / Use failed all append before returning).
- repl._apply_seed_result surfaces ``error`` for any failed seed
  result whose messages do not already convey it (underscore- and
  case-normalized containment), so no Dell's failure can be silent at
  the public display boundary, and visible failures print once.

Labels: execute_seed checks are PUBLIC_ENTRY_PATH; the dispatch
capture checks are HIGH-FIDELITY DISPATCH (the REPL's own dispatcher);
the subprocess session is REAL_USER_PATH (literal ``python3 -m
form.repl`` with piped input). Synthetic throwaway owners only.
"""
from __future__ import annotations

import os
import subprocess
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CHECKS = []


def check(name, cond):
    CHECKS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")
    if not cond:
        raise AssertionError(name)


def run_all():
    from form.open import open_program
    from form.mandell.executor import execute_seed
    from form.repl import _apply_seed_result, _dispatch_public_line, capture_output

    owner = "SM16VisTest"
    p = open_program(owner)

    def dispatch(line):
        _, msg = capture_output(
            lambda: _dispatch_public_line(p, line, str(uuid.uuid4())))
        return msg

    # 1. Executor level: bare 37 fails honestly, zero mutation, and the
    #    failure is now carried in messages as well as error.
    before = p.nursery.summary().get("pending", 0)
    r = execute_seed(p, "37[Nurture]")
    check("executor: bare 37 ok=False with exact error",
          r.get("ok") is False
          and r.get("error") == "add idea requires a label")
    check("executor: bare 37 failure carried in messages",
          any("add idea requires a label" in str(m)
              for m in (r.get("messages") or [])))
    check("executor: bare 37 zero nursery mutation",
          p.nursery.summary().get("pending", 0) == before)

    # 2. REPL dispatch: the error is visible to the user.
    msg = dispatch("37[Nurture]")
    check("repl: bare 37 error visible",
          "add idea requires a label" in msg)
    check("repl: bare 37 still zero nursery mutation",
          p.nursery.summary().get("pending", 0) == before)

    # 3. Already-visible failure prints once (no duplicate Error line):
    #    confirm-unknown appends its own message in core_i_ops.
    msg = dispatch("37[Nurture] :: confirm NOPE_SM16")
    check("repl: confirm-unknown failure visible",
          "Confirm failed: NOPE_SM16" in msg)
    check("repl: confirm-unknown failure not duplicated",
          msg.lower().count("confirm failed") == 1)

    # 4. Underscore error codes already messaged are not duplicated:
    #    Dell 44 error "bridge_unavailable" vs message "Bridge
    #    unavailable: ..." must dedup after normalization.
    msg = dispatch("44[Bridge]")
    check("repl: bridge refusal visible",
          "Bridge unavailable" in msg)
    check("repl: bridge refusal not duplicated as raw code",
          # the English echo already carries the code once at baseline;
          # the fix must add no Error line and no second occurrence
          "Error:" not in msg and msg.count("bridge_unavailable") == 1)

    # 5. Success path unchanged: a labelled 37 add shows its message
    #    and no Error line.
    msg = dispatch("37[Nurture] :: SM16 Valid Label")
    check("repl: labelled 37 add succeeds visibly",
          "Added idea:" in msg and "Error:" not in msg)
    check("repl: labelled 37 add mutated nursery exactly once",
          p.nursery.summary().get("pending", 0) == before + 1)

    # 6. General guarantee: _apply_seed_result surfaces ANY failed
    #    result whose messages omit the error (future silent Dell).
    _, msg = capture_output(lambda: _apply_seed_result(p, {
        "ok": False, "error": "synthetic silent failure SM16",
        "messages": ["Mandell: 99[Synthetic]"], "new_program": None}))
    check("repl: generic silent failure surfaced",
          "Error: synthetic silent failure SM16" in msg)

    # 7. REAL_USER_PATH: literal REPL subprocess, piped input.
    proc = subprocess.run(
        [sys.executable, "-m", "form.repl", "--owner", "SM16ReplUser"],
        input="37[Nurture]\nquit\n", capture_output=True, text=True,
        cwd=ROOT, timeout=120)
    check("real repl: bare 37 error printed in session stdout",
          "add idea requires a label" in proc.stdout)

    print(f"SM16-REPL-ERROR-VISIBILITY: "
          f"{sum(1 for _, c in CHECKS if c)}/{len(CHECKS)} GREEN")


def smoke() -> bool:
    try:
        run_all()
        return True
    except Exception as e:
        print(f"SM16 SMOKE FAILED: {e}")
        return False


if __name__ == "__main__":
    run_all()
