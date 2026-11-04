"""Probe C2 — REPL, corrected assertions + post-session state readback.

Probe C's two FAILs were assertion-string errors, not behavior:
the 82[Group] refusal surfaces in the REPL as a TOAM message (the
UNSUPPORTED_ARGS class lives in the result dict, not the printed
messages), and the 37 failure prints nothing at all. This probe
asserts on what the REPL actually prints and then reads the
persisted session state back to prove effect/no-effect.
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.expanduser("~/workspace/nbd-omega-corei"))
os.chdir(os.path.expanduser("~/workspace/nbd-omega-corei"))

from probe_lib import EVDIR, ROOT, cleanup, witness  # noqa: E402

from form.open import Program  # noqa: E402

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

    # Read the persisted session back: what did the lines DO?
    p = Program(owner=OWNER)
    w = witness({"ok": True}, p)
    state = json.loads(w[2])
    print(f"  readback units={state.get('units')}")
    print(f"  readback nursery_pending={state.get('nursery_pending')} "
          f"last_stamp={state.get('last_stamp')}")

    checks = [
        ("Tone: label drove, bogus ignored (tone=joy, no refusal)",
         "tone=joy" in out),
        ("Tone: typed expression=calm did not drive (no tone=calm)",
         "tone=calm" not in out),
        ("Stamp: execution used default mark ('Stamp: stamp @'), "
         "typedmark appears only in the seed echo",
         "Stamp: stamp @" in out),
        ("Nurture: NO 'Added idea' line for the typed label",
         "Added idea" not in out),
        ("Nurture: typed idea absent from persisted nursery "
         "(pending=0 at readback)",
         state.get("nursery_pending") == 0),
        ("Create: valid typed args executed (Repl Wish unit, SPHERE)",
         any("repl_wish" in u and "SPHERE" in u
             for u in state.get("units") or [])),
        ("Create: invalid skin refused visibly (INVALID_VALUE msg)",
         "INVALID_VALUE" in out),
        ("Core II asymmetry: 82[Group] typed args refused VISIBLY "
         "('typed arguments refused before execution (roles: bogus)')",
         "typed arguments refused before execution" in out
         and "(roles: bogus)" in out),
        ("Stamp readback: last_stamp mark is the default 'stamp'",
         (state.get("last_stamp") or {}).get("mark") == "stamp"),
    ]
    for label, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    cleanup(OWNER)
    print("PROBE C2 DONE")


if __name__ == "__main__":
    main()
