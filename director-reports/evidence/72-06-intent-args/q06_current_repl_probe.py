#!/usr/bin/env python3
"""72-06 CURRENT-CONTRACT REPL probe (added 2026-11-20, Director 7040506653).

REAL_USER_PATH companion to q06_current_probe.py: runs the actual
terminal (python3 -m form.repl, cross-process) and pins CURRENT
behavior for the five claims that changed since the 2026-11-05 census:

  W1  'cycle three times' -> Cycle x3            (was: silent x1)
  W2  'grow three'        -> requested 3, executed 3   (was: requested 1)
  C1  'cycle 3 times'     -> Cycle x3            (digit control, unchanged)
  C2  'grow 3'            -> requested 3, executed 3   (digit control)
  G9  'grow 9'            -> requested 9, executed 5, clamp STATED in
                             the output line (truthful requested-vs-
                             executed semantics; no silent producer clamp)
  C9  'cycle 9'           -> Cycle x5 (execution bound, executed count
                             is what the output claims)
  Z1  'zoom tokyo'        -> REPL refuses: 'Could not zoom: not found'
  WX  'weather rain'      -> REPL direct handler echoes 'Weather -> rain'
                             from the raw line; no dead arg is produced
                             (programmatic half: q06_current_probe D18)

Each case uses a fresh owner; the probe removes that owner's state
directory afterwards (safe cleanup). Full transcripts are printed so
the archived run logs are the evidence. Usage:
python3 q06_current_repl_probe.py <run-tag>
Exit 0 iff all assertions match; exit 2 on setup failure.
"""
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
STATE = ROOT / "form" / "state"

CASES = [
    ("W1", "cycle three times", ["Cycle x3", "RESULT: ok=True"], "word count honored at the bare REPL"),
    ("W2", "grow three", ["Loop: requested 3, executed 3", "RESULT: ok=True"], "word count honored at the bare REPL"),
    ("C1", "cycle 3 times", ["Cycle x3", "RESULT: ok=True"], "digit control"),
    ("C2", "grow 3", ["Loop: requested 3, executed 3", "RESULT: ok=True"], "digit control"),
    ("G9", "grow 9", ["Loop: requested 9, executed 5. (clamped to 1..5)", "RESULT: ok=True"],
     "requested-vs-executed stated; bound enforced at execution, not silently at the producer"),
    ("C9", "cycle 9", ["Cycle x5", "RESULT: ok=True"], "execution bound; output claims only the executed count"),
    ("Z1", "zoom tokyo", ["Could not zoom: not found: tokyo"], "no-dead-arg refusal at the REPL handler"),
    ("WX", "weather rain", ["Weather → rain"], "REPL direct handler serves the raw line; no dead arg produced"),
]

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "r1"
    for idx, (cid, phrase, needles, note) in enumerate(CASES):
        owner = f"Q06CR{tag}{idx}"
        try:
            cp = subprocess.run(
                [sys.executable, "-m", "form.repl", "--owner", owner],
                input=phrase + "\n", capture_output=True, text=True,
                timeout=120, cwd=str(ROOT))
        except Exception as exc:
            print(f"SETUP_FAILED {cid}: {exc}")
            return 2
        out = cp.stdout + cp.stderr
        print(f"===== TRANSCRIPT {cid} owner={owner} input={phrase!r} =====")
        print(out)
        print(f"===== END TRANSCRIPT {cid} =====")
        ok = all(n in out for n in needles)
        check(f"{cid}.repl_{phrase.replace(' ', '_')}", ok, note)
        # safe cleanup of this probe's own owner state
        for d in STATE.glob(f"ideas_{owner}*"):
            shutil.rmtree(d, ignore_errors=True)

    failed = [n for n, ok in RESULTS if not ok]
    print(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} checks passed"
          + (f"; FAILED: {failed}" if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
