#!/usr/bin/env python3
"""72-06 supplement probe (Director review 2026-11-05 19:38 CST):
Class E at the bare REPL process — REAL_USER_PATH.

Runs the actual terminal (python3 -m form.repl, cross-process) on:
  W1  'cycle three times'  -> word count; defect = executes x1
  W2  'grow three'         -> word count; defect = Loop requested 1
  C1  'cycle 3 times'      -> digit control; executes x3
  C2  'grow 3'             -> digit control; Loop requested 3

The FULL REPL transcript of every case is printed to stdout, so
the run logs archived with this probe are the hashed transcripts
the Director required. Assertions pin today's behavior exactly:
word forms silently default to 1 with ok=True (the OPEN Class E
defect, now proven at the real-user path); digit forms execute
the requested count. A future repair flips W1/W2 deliberately.

Usage: python3 q06_repl_probe.py <run-tag>
Exit 0 iff all assertions match; exit 2 on setup failure.
"""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]

CASES = [
    ("W1", "cycle three times", ["Cycle x1"], "word count silently defaults to 1 at the bare REPL"),
    ("W2", "grow three", ["Loop: requested 1, executed 1"], "word count silently defaults to 1 at the bare REPL"),
    ("C1", "cycle 3 times", ["Cycle x3"], "digit control executes the requested count"),
    ("C2", "grow 3", ["Loop: requested 3, executed 3"], "digit control executes the requested count"),
]

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "r1"
    for idx, (cid, phrase, needles, note) in enumerate(CASES):
        owner = f"Q06R{tag}{idx}"
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
        ok = all(n in out for n in needles) and "RESULT: ok=True" in out
        check(f"{cid}.repl_{phrase.replace(' ', '_')}", ok, note)

    failed = [n for n, ok in RESULTS if not ok]
    print(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} checks passed"
          + (f"; FAILED: {failed}" if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
