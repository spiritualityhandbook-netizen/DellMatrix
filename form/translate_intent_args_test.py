#!/usr/bin/env python3
"""SM-11 — English Intent.args dropped-count regression.

Defect (confirmed, reproduced at baseline 0cd1fd6): the phrase
dictionary captures an explicit count for "grow 3" / "grow ideas 2" /
"evolve ideas 4" (and step counts for "walk forward 3" / "walk 2")
into the phrase hit label, but translate()'s phrase branch
hard-coded ``{"cycles": 1}`` / ``{"steps": 1}``. The digit-aware grow
branch was unreachable dead code. Downstream consumers read the
count from Intent.args (semantic_router._seed_grow; the REPL walk
handler), so the user's count was silently dropped: "grow 3" routed
to ``13[Loop] :: 1`` with ok=True, and "walk forward 3" moved one
step. Intent.args is a consumer channel, not SeedAtom.args — every
value placed in it must either reach its consumer or not be placed.

Repair (canonical owner form/mandell/translate.py only): the grow
and walk phrase branches now carry the captured digit (grow clamped
to >=1, mirroring _seed_grow; Dell 13 itself clamps/reports 1..5),
and the dead grow branch is removed.

Labels: translate()/route_intent checks are INTEGRATION; the REPL
_execute_intent walk check is HIGH-FIDELITY DISPATCH. Synthetic
throwaway owners only.
"""
from __future__ import annotations

import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CHECKS = []


def check(name, cond):
    CHECKS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")
    if not cond:
        raise AssertionError(name)


def run_all():
    from form.mandell.translate import translate

    # 1. translate level: explicit grow counts survive into Intent.args.
    check("grow 3 -> cycles 3", translate("grow 3").args.get("cycles") == 3)
    check("grow ideas 2 -> cycles 2",
          translate("grow ideas 2").args.get("cycles") == 2)
    check("evolve ideas 4 -> cycles 4",
          translate("evolve ideas 4").args.get("cycles") == 4)
    check("grow (no count) -> cycles 1",
          translate("grow").args.get("cycles") == 1)
    check("grow ideas (no count) -> cycles 1",
          translate("grow ideas").args.get("cycles") == 1)
    check("grow 0 -> cycles clamped to 1 (mirrors _seed_grow)",
          translate("grow 0").args.get("cycles") == 1)

    # 2. translate level: explicit walk step counts survive.
    check("walk forward 3 -> steps 3",
          translate("walk forward 3").args.get("steps") == 3)
    check("walk 2 -> steps 2", translate("walk 2").args.get("steps") == 2)
    check("walk forward (no count) -> steps 1",
          translate("walk forward").args.get("steps") == 1)

    # 3. Adversarial: a non-numeric grow phrase must not fabricate a
    # count, and unrelated phrase args are unchanged.
    g = translate("grow abc")
    check("grow abc -> no fabricated cycles",
          g.action != "grow" or g.args.get("cycles") in (None, 1))
    check("turn left unchanged",
          translate("turn left").args.get("direction") == "left")
    check("cycle 3 (fallback path) unchanged",
          translate("cycle 3").args.get("count") == 3)
    check("get typed key unchanged",
          translate("get My Key").args.get("key") == "My Key")

    # 4. Downstream consumer proof: route_intent carries the count
    # into the Mandell seed Dell 13 executes.
    from form.open import open_program
    from form.mandell.semantic_router import route_intent

    owner = "SM11ArgsTest" + uuid.uuid4().hex[:6]
    p = open_program(owner)
    r3 = route_intent(p, translate("grow 3"), "grow 3")
    check("route grow 3 -> seed 13[Loop] :: 3, ok",
          r3.ok and r3.seed == "13[Loop] :: 3")
    r1 = route_intent(p, translate("grow"), "grow")
    check("route grow -> seed 13[Loop] :: 1, ok",
          r1.ok and r1.seed == "13[Loop] :: 1")
    r9 = route_intent(p, translate("grow 9"), "grow 9")
    msgs = " | ".join(r9.messages or [])
    check("route grow 9 -> Dell 13 honestly reports requested 9, executed 5",
          r9.ok and "requested 9, executed 5" in msgs)

    # 5. REPL dispatch proof: walk actually moves the requested steps.
    import io
    import contextlib
    from form.repl import _execute_intent

    before = p.avatar.body.pos
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        _execute_intent(p, translate("walk forward 3"),
                        raw_line="walk forward 3")
    after = p.avatar.body.pos
    moved = abs(after[0] - before[0]) + abs(after[1] - before[1])
    check("REPL walk forward 3 moves 3 steps", moved == 3)
    check("REPL walk message reports 3",
          "walked forward 3" in buf.getvalue())

    print(f"SM-11 intent-args: {len(CHECKS)}/{len(CHECKS)} checks passed")


def smoke() -> bool:
    try:
        run_all()
        return True
    except Exception as e:
        print(f"SM11 SMOKE FAILED: {e}")
        return False


if __name__ == "__main__":
    run_all()
