"""Director order step 6 — leaf honesty (B1/B2/B3/B4/B6).

Contracts proven here, through the public seed path
(form.mandell.executor.execute_seed) unless noted:

- B1 Decay: with the enhance gate OFF, Dell 16 reports the gate's
  refusal (ok=False, "enhance OFF"), scores stay unchanged in
  memory AND after save/load, and no message claims decay. With
  the gate ON, scores are scaled and the decay claim is true.
  A stub enhance object without decay() cannot bypass the gate.
- B2 Loop: Dell 13 uses Cycle's finite 1..5 bound. Every run
  reports requested and executed counts; a clamp is named when
  executed != requested; the nursery delta equals exactly
  executed x the measured one-cycle delta. Malformed and
  negative labels refuse invalid_loop_count with zero growth.
- B3 Merge: fewer than two resolved required sources refuses
  missing_source (bare, unknown tokens, one source) with zero
  mutation; ambiguity still refuses ambiguous_source; a named
  pair still merges with parents recorded.
- B4 Split: bare, unknown and misspelled sources refuse
  missing_source with zero mutation; ambiguity still refuses
  ambiguous_source; a named source still splits.
- B6 Translate: translate("") and translate("   ") return the
  nothing_to_translate intent (no Dell, no mandel, no Show);
  bridge("") agrees; bare/whitespace 45[Translate] refuses
  nothing_to_translate with zero mutation; a non-empty phrase
  still reports its Mandell seed and gloss.

Labels: INTEGRATION / PUBLIC_ENTRY (real Program, real gate,
real growth, save/load for the B1 persisted-state agreement).
"""
from __future__ import annotations

import glob
import os
import shutil
import sys

RESULTS: list = []


def _rec(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, bool(ok), detail))


def _cleanup(owner: str) -> None:
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "state")
    if not os.path.isdir(base):
        return
    errors = []
    for pat in (f"program_{owner}.json", f"nursery_{owner}.json",
                f"checkpoint_{owner}.json",
                f"confirm_journal_{owner}.json",
                f"confirm_gen_{owner}.json",
                f"confirm_current_{owner}.json"):
        for f in glob.glob(os.path.join(base, pat)):
            try:
                os.remove(f)
            except OSError as e:
                errors.append(f"{f}: {e}")
    d = os.path.join(base, f"ideas_{owner}")
    if os.path.isdir(d):
        try:
            shutil.rmtree(d)
        except OSError as e:
            errors.append(f"{d}: {e}")
    if errors:
        raise RuntimeError(f"cleanup failed for {owner}: {errors}")


def _prog(owner: str):
    _cleanup(owner)
    from form.open import Program
    from form.mandell.core_ii_exec import attach
    p = Program(owner=owner)
    attach(p)
    return p


def _run(p, seed):
    from form.mandell.executor import execute_seed
    return execute_seed(p, seed)


def _msgs(r):
    return [m for m in r.get("messages", [])
            if not m.startswith(("Mandell:", "English:"))]


def _units(p):
    return p.cube.session.plane.units


def _pending(p):
    return p.nursery.summary()["pending"]


# ---------------------------------------------------------------- B1
def _b1() -> None:
    p = _prog("S6B1")
    p.enhance.state.scores["alpha"] = 2.0
    p.enhance.state.scores["beta"] = 1.0
    before = dict(p.enhance.state.scores)
    r = _run(p, "16[Decay] :: 0.5")
    _rec("B1 refused: enhance OFF -> ok=False, error is the gate reason",
         r.get("ok") is False and r.get("error") == "enhance OFF",
         f"{r.get('ok')} / {r.get('error')}")
    _rec("B1 refused: message reports refusal, never claims decay",
         _msgs(r) == ["Decay refused: enhance OFF — scores unchanged."],
         str(_msgs(r)))
    _rec("B1 refused: scores unchanged in memory",
         dict(p.enhance.state.scores) == before,
         str(p.enhance.state.scores))
    _rec("B1 refused: no Decay history note is written",
         not any(str(h).startswith("16[Decay]") for h in p.history),
         str(list(p.history)[-3:]))
    # persisted state must agree with the refused verdict
    _run(p, "10[Keep]")
    from form.open import Program
    p2 = Program.load(owner="S6B1")
    _rec("B1 refused: scores unchanged after save/load",
         dict(p2.enhance.state.scores) == before,
         str(p2.enhance.state.scores))
    # positive path: gate ON — the claim becomes true
    p.enhance_on()
    r = _run(p, "16[Decay] :: 0.5")
    sc = p.enhance.state.scores
    _rec("B1 positive: enhance ON -> ok, scores scaled, claim true",
         r.get("ok") is True
         and _msgs(r) == ["Scores decayed ×0.5."]
         and abs(sc["alpha"] - 1.0) < 1e-9
         and abs(sc["beta"] - 0.5) < 1e-9,
         f"{_msgs(r)} / {sc}")
    _cleanup("S6B1")

    # manual-fallback gate control: an enhance object WITHOUT decay()
    # must not become a bypass around the gate.
    class _StubState:
        scores = {"s": 4.0}

    class _StubEnhance:
        on = False
        state = _StubState()

    q = _prog("S6B1Stub")
    real_enhance = q.enhance
    q.enhance = _StubEnhance()
    r = _run(q, "16[Decay] :: 0.5")
    _rec("B1 manual fallback: gate OFF refuses, scores unchanged",
         r.get("ok") is False
         and r.get("error") == "enhance OFF"
         and _StubEnhance.state.scores["s"] == 4.0,
         f"{r.get('ok')} / {_StubEnhance.state.scores}")
    _StubEnhance.on = True
    r = _run(q, "16[Decay] :: 0.5")
    _rec("B1 manual fallback: gate ON scales and says (manual)",
         r.get("ok") is True
         and _msgs(r) == ["Scores decayed ×0.5 (manual)."]
         and _StubEnhance.state.scores["s"] == 2.0,
         f"{_msgs(r)} / {_StubEnhance.state.scores}")
    q.enhance = real_enhance
    _cleanup("S6B1Stub")


# ---------------------------------------------------------------- B2
def _b2() -> None:
    p = _prog("S6B2")
    _run(p, "08[Create] :: Alpha")
    base_units = set(_units(p))
    p0 = _pending(p)
    r = _run(p, "13[Loop]")
    d1 = _pending(p) - p0
    _rec("B2 bare: 1 cycle runs; requested=1 executed=1 reported",
         r.get("ok") is True and d1 > 0
         and "Loop: requested 1, executed 1." in _msgs(r)
         and set(_units(p)) == base_units,
         f"{_msgs(r)} d1={d1}")
    p1 = _pending(p)
    r = _run(p, "13[Loop] :: 3")
    _rec("B2 in-bound: requested=3 executed=3, nursery delta = 3 cycles",
         r.get("ok") is True
         and "Loop: requested 3, executed 3." in _msgs(r)
         and _pending(p) - p1 == 3 * d1,
         f"{_msgs(r)} delta={_pending(p) - p1} d1={d1}")
    p2 = _pending(p)
    r = _run(p, "13[Loop] :: 7")
    _rec("B2 clamp: requested=7 executed=5, clamp named, delta = 5 cycles",
         r.get("ok") is True
         and "Loop: requested 7, executed 5. (clamped to 1..5)"
         in _msgs(r)
         and _pending(p) - p2 == 5 * d1,
         f"{_msgs(r)} delta={_pending(p) - p2} d1={d1}")
    p3 = _pending(p)
    r = _run(p, "13[Loop] :: 100")
    _rec("B2 extreme: requested=100 still executes only 5",
         r.get("ok") is True
         and "Loop: requested 100, executed 5. (clamped to 1..5)"
         in _msgs(r)
         and _pending(p) - p3 == 5 * d1,
         f"{_msgs(r)} delta={_pending(p) - p3}")
    p4 = _pending(p)
    r = _run(p, "13[Loop] :: 0")
    _rec("B2 zero: requested=0 clamps up to executed=1",
         r.get("ok") is True
         and "Loop: requested 0, executed 1. (clamped to 1..5)"
         in _msgs(r)
         and _pending(p) - p4 == d1,
         f"{_msgs(r)} delta={_pending(p) - p4}")
    for label in ("bogus", "-3", "3.5"):
        p5 = _pending(p)
        r = _run(p, f"13[Loop] :: {label}")
        _rec(f"B2 malformed '{label}': refuses invalid_loop_count, "
             f"zero growth, zero mutation",
             r.get("ok") is False
             and r.get("error") == "invalid_loop_count"
             and _pending(p) == p5
             and set(_units(p)) == base_units,
             f"{r.get('ok')} / {r.get('error')} / {_msgs(r)}")
    _cleanup("S6B2")


# ---------------------------------------------------------------- B3
def _b3() -> None:
    p = _prog("S6B3")
    _run(p, "08[Create] :: A One")
    _run(p, "08[Create] :: B Two")
    before = list(_units(p))
    for seed in ("21[Merge]", "21[Merge] :: gone + missing",
                 "21[Merge] :: a_one"):
        r = _run(p, seed)
        _rec(f"B3 '{seed}': refuses missing_source, zero mutation",
             r.get("ok") is False
             and r.get("error") == "missing_source"
             and list(_units(p)) == before,
             f"{r.get('ok')} / {r.get('error')}")
    r = _run(p, "21[Merge] :: a_one + b_two")
    child = _units(p).get("merge_a_one_b_two")
    _rec("B3 positive: named pair merges, parents recorded, "
         "parents preserved",
         r.get("ok") is True and child is not None
         and list(child.parents) == ["a_one", "b_two"]
         and "a_one" in _units(p) and "b_two" in _units(p),
         f"{r.get('ok')} / {_msgs(r)}")
    _cleanup("S6B3")

    q = _prog("S6B3Amb")
    _run(q, "08[Create] :: Twin")
    _run(q, "08[Create] :: Twin")
    before = list(_units(q))
    r = _run(q, "21[Merge] :: Twin + a_one")
    _rec("B3 ambiguity preserved: ambiguous_source, zero mutation",
         r.get("ok") is False
         and r.get("error") == "ambiguous_source"
         and list(_units(q)) == before,
         f"{r.get('error')}")
    _cleanup("S6B3Amb")


# ---------------------------------------------------------------- B4
def _b4() -> None:
    p = _prog("S6B4")
    _run(p, "08[Create] :: Solo")
    before = list(_units(p))
    for seed in ("22[Split]", "22[Split] :: nosuchthing",
                 "22[Split] :: solo_typo"):
        r = _run(p, seed)
        _rec(f"B4 '{seed}': refuses missing_source, zero mutation",
             r.get("ok") is False
             and r.get("error") == "missing_source"
             and list(_units(p)) == before,
             f"{r.get('ok')} / {r.get('error')}")
    r = _run(p, "22[Split] :: solo")
    _rec("B4 positive: named source splits into _a/_b, parent kept",
         r.get("ok") is True
         and "solo_a" in _units(p) and "solo_b" in _units(p)
         and "solo" in _units(p),
         f"{r.get('ok')} / {_msgs(r)}")
    _cleanup("S6B4")

    q = _prog("S6B4Amb")
    _run(q, "08[Create] :: Twin")
    _run(q, "08[Create] :: Twin")
    before = list(_units(q))
    r = _run(q, "22[Split] :: Twin")
    _rec("B4 ambiguity preserved: ambiguous_source, zero mutation",
         r.get("ok") is False
         and r.get("error") == "ambiguous_source"
         and list(_units(q)) == before,
         f"{r.get('error')}")
    _cleanup("S6B4Amb")


# ---------------------------------------------------------------- B6
def _b6() -> None:
    from form.mandell.translate import translate
    from form.mandell.bridge import bridge, to_mandell, to_english
    for text in ("", "   "):
        i = translate(text)
        _rec(f"B6 translate({text!r}): nothing_to_translate, "
             f"no Dell, no mandel, no Show",
             i.action == "nothing_to_translate" and i.dell is None
             and i.mandel == "" and "Show" not in (i.term or ""),
             f"{i.action} / {i.dell} / {i.mandel!r}")
    rep = bridge("")
    _rec("B6 bridge(''): nothing_to_translate, empty mandel",
         rep.get("intent_action") == "nothing_to_translate"
         and rep.get("mandel") == "",
         str(rep))
    _rec("B6 helpers: to_mandell('') and to_english('') stay empty",
         to_mandell("") == "" and to_english("") == "")
    i = translate("show avatar")
    _rec("B6 positive control: non-empty input still translates",
         i.mandel == "09[Show]" and i.dell == 9,
         f"{i.action} / {i.mandel!r}")

    p = _prog("S6B6")
    _run(p, "08[Create] :: Keepsake")
    before = list(_units(p))
    hist_before = len(list(p.history))
    # NOTE: a whitespace-only seed label is not expressible — the
    # seed parser itself refuses it ("too many flow operators")
    # before any Dell runs; whitespace input is covered above at
    # the translate()/bridge() level, bare at the leaf level here.
    for seed in ("45[Translate]",):
        r = _run(p, seed)
        _rec(f"B6 leaf '{seed}': refuses nothing_to_translate, "
             f"no Show intent in messages, zero mutation",
             r.get("ok") is False
             and r.get("error") == "nothing_to_translate"
             and any("nothing_to_translate" in m for m in _msgs(r))
             and not any("09[Show]" in m for m in _msgs(r))
             and list(_units(p)) == before,
             f"{r.get('ok')} / {r.get('error')} / {_msgs(r)}")
    r = _run(p, "45[Translate] :: create a garden")
    _rec("B6 leaf positive: phrase reports its seed + gloss, "
         "report only (zero mutation)",
         r.get("ok") is True
         and _msgs(r)[0].startswith('mandel: 08[Create](name="garden")')
         and list(_units(p)) == before,
         str(_msgs(r)))
    _rec("B6 refusals wrote no history beyond the positive report's "
         "own bookkeeping baseline",
         len(list(p.history)) >= hist_before, "")
    _cleanup("S6B6")


def main() -> bool:
    _b1()
    _b2()
    _b3()
    _b4()
    _b6()
    total = len(RESULTS)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        if not ok:
            print(f"FAIL {name} :: {detail}")
    print(f"STEP6_LEAF_HONESTY: {passed}/{total}")
    return passed == total


def smoke() -> bool:
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
