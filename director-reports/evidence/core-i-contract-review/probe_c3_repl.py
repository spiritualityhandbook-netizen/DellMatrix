"""Probe C3 — REPL in-session state witness for 37[Nurture].

TokenCount (Dell 40, intercept) prints the nursery pending count
inside the same REPL session, giving an in-session differential:
typed label (expect pending stays 0) vs seed label (expect
'Added idea' + pending 1).
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.expanduser("~/workspace/nbd-omega-corei"))
os.chdir(os.path.expanduser("~/workspace/nbd-omega-corei"))

from probe_lib import EVDIR, ROOT, cleanup  # noqa: E402

OWNER = "CoreIRepl"
LINES = (
    '37[Nurture](label="typedidea")\n'
    '40[TokenCount]\n'
    '37[Nurture] :: realidea\n'
    '40[TokenCount]\n'
)


def main():
    cleanup(OWNER)
    proc = subprocess.run(
        [sys.executable, "-m", "form.repl", "--owner", OWNER],
        input=LINES, capture_output=True, text=True, cwd=ROOT,
        timeout=180)
    out = proc.stdout + proc.stderr
    path = os.path.join(EVDIR, "repl_transcript_37.txt")
    with open(path, "w") as fh:
        fh.write(f"$ python3 -m form.repl --owner {OWNER}\n")
        fh.write("--- stdin ---\n" + LINES)
        fh.write(f"--- output (rc={proc.returncode}) ---\n" + out)
    pend = [ln.strip() for ln in out.splitlines() if "pending=" in ln]
    print(f"  TokenCount lines: {pend}")
    checks = [
        ("after typed-label 37: pending=0 (nothing added)",
         len(pend) >= 1 and "pending=0" in pend[0]),
        ("label-driven 37 added the idea ('Added idea' printed)",
         "Added idea" in out and "realidea" in out),
        ("after label 37: pending=1",
         len(pend) >= 2 and "pending=1" in pend[1]),
    ]
    for label, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    cleanup(OWNER)
    print("PROBE C3 DONE")


if __name__ == "__main__":
    main()
