"""Probe D2 — scoping, corrected: flow_executor with a composable
control pair, and a translate() sweep testing whether any English
output puts typed args on an UNREGISTERED Dell.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.expanduser("~/workspace/nbd-omega-corei"))
os.chdir(os.path.expanduser("~/workspace/nbd-omega-corei"))

from form.mandell.flow_executor import parse_program  # noqa: E402
from form.mandell.seed import parse_seed  # noqa: E402
from form.mandell.signatures import has_signature  # noqa: E402
from form.mandell.translate import translate  # noqa: E402


def main():
    print("== D2.1: flow_executor, composable control (10[Keep] > "
          "12[Test]) ==")
    for raw in ("10[Keep] > 12[Test]",
                '10[Keep](bogus="x") > 12[Test]'):
        try:
            fp = parse_program(raw)
            print(f"  parsed OK: {raw!r} -> {len(fp.nodes)} nodes")
        except Exception as exc:  # noqa: BLE001
            print(f"  REFUSED: {raw!r} -> {type(exc).__name__}: {exc}")

    print("== D2.2: translate sweep — args only ever on registered "
          "Dells ==")
    phrases = ["create an idea called garden", "turn left",
               "be joyful", "save the session", "grow the garden",
               "make a sphere called orb", "stamp this moment",
               "copy data to backup", "delete the key temp",
               "replace old with new", "get the key data",
               "select the garden ideas", "match pattern leaf",
               "move data to archive", "patch the key status",
               "checkpoint now", "count the tokens",
               "discover garden", "nurture the seed idea"]
    bad = []
    for ph in phrases:
        intent = translate(ph)
        mandel = getattr(intent, "mandel", "") or ""
        s = parse_seed(mandel) if mandel else None
        for a in (s.atoms if s and s.atoms else []):
            if a.args and not has_signature(int(a.dell)):
                bad.append((ph, mandel, int(a.dell), a.args))
            if a.args:
                print(f"  args emitted: {ph!r} -> Dell "
                      f"{int(a.dell)} args={a.args} "
                      f"registered={has_signature(int(a.dell))}")
    print(f"  unregistered-arg emissions: {bad if bad else 'NONE'}")
    print("PROBE D2 DONE")


if __name__ == "__main__":
    main()
