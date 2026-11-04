"""Probe C — literal REPL transcript (REAL_USER_PATH).

Drives python3 -m form.repl --owner CoreIRepl as a subprocess with
piped stdin, the established pattern from the gate suite. The full
transcript is saved verbatim as repl_transcript.txt; checks below
only read it.
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
    '05[Tone](bogus="x") :: joy\n'
    '05[Tone](expression="calm") :: joy\n'
    '34[Stamp](mark="typedmark")\n'
    '37[Nurture](label="typedidea")\n'
    '08[Create](name="Repl Wish", skin="SPHERE")\n'
    '08[Create](name="Repl Bad", skin="TRIANGLE")\n'
    '82[Group](bogus="x")\n'
)


def main():
    cleanup(OWNER)
    proc = subprocess.run(
        [sys.executable, "-m", "form.repl", "--owner", OWNER],
        input=LINES, capture_output=True, text=True, cwd=ROOT,
        timeout=180)
    out = proc.stdout + proc.stderr
    path = os.path.join(EVDIR, "repl_transcript.txt")
    with open(path, "w") as fh:
        fh.write(f"$ python3 -m form.repl --owner {OWNER}\n")
        fh.write("--- stdin ---\n" + LINES)
        fh.write(f"--- output (rc={proc.returncode}) ---\n" + out)
    checks = [
        ("Tone label drove (tone=joy present)",
         "tone=joy" in out),
        ("Tone typed expression=calm did NOT drive "
         "(no tone=calm anywhere)", "tone=calm" not in out),
        ("Stamp used default mark, not typedmark",
         "Stamp: stamp @" in out and "typedmark" not in
         out.replace('(mark="typedmark")', "")),
        ("Nurture typed label did not satisfy label requirement",
         "add idea requires a label" in out),
        ("Dell 8 valid typed args work in REPL (Repl Wish)",
         "Repl Wish" in out),
        ("Dell 8 invalid skin refused in REPL (INVALID_VALUE)",
         "INVALID_VALUE" in out),
        ("Core II gate refusal visible in REPL (UNSUPPORTED_ARGS) "
         "— the asymmetry at the real user surface",
         "UNSUPPORTED_ARGS" in out),
    ]
    for label, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    print(f"  transcript: {path} ({len(out)} chars, rc={proc.returncode})")
    cleanup(OWNER)
    print("PROBE C DONE")


if __name__ == "__main__":
    main()
