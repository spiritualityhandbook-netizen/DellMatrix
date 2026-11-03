"""Probe D — scoping: flow_executor fence + English-layer expressibility.

flow_executor (Q-D4 excluded mechanism): does arg-shaped text get
silently consumed there, or refused? English layer: can any
translate() output express seed typed args at all?
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.expanduser("~/workspace/nbd-omega-corei"))
os.chdir(os.path.expanduser("~/workspace/nbd-omega-corei"))

from form.mandell.flow_executor import parse_program  # noqa: E402
from form.mandell.seed import parse_seed  # noqa: E402
from form.mandell.translate import translate  # noqa: E402


def main():
    print("== D1: flow_executor with arg-shaped text ==")
    for raw in ('05[Tone] :: joy > 03[Logic]',
                '05[Tone](bogus="x") :: joy > 03[Logic]'):
        try:
            fp = parse_program(raw)
            print(f"  parsed OK: {raw!r} -> nodes="
                  f"{[str(x) for x in fp.nodes]}")
        except Exception as exc:  # noqa: BLE001
            print(f"  REFUSED: {raw!r} -> {type(exc).__name__}: {exc}")

    print("== D2: English layer cannot express seed typed args ==")
    phrases = ["create an idea called garden", "turn left",
               "be joyful", "save the session", "grow the garden",
               "make a sphere called orb", "stamp this moment"]
    for ph in phrases:
        intent = translate(ph)
        mandel = getattr(intent, "mandel", "") or ""
        s = parse_seed(mandel) if mandel else None
        argsets = [a.args for a in s.atoms] if s and s.atoms else []
        print(f"  {ph!r:<34} mandel={mandel!r} atom_args={argsets} "
              f"intent_args={getattr(intent, 'args', {})}")
    print("PROBE D DONE")


if __name__ == "__main__":
    main()
