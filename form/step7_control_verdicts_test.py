"""Director order step 7 — control verdicts (B7/B8/B9, DAF-08).

Contracts proven here, through the public seed path
(form.mandell.executor.execute_seed):

- DAF-08: atom_results is OCCURRENCE-COMPLETE and atom-ordered —
  control heads, unchosen Branch arms, the Else marker, FlowOver
  skips and zero-iteration bodies all carry receipts with skip
  reasons; any_skipped / partial derive from those records
  (partial = occurrence-level incompleteness, NOT a failure
  verdict: a lawful-skip chain can be ok=True AND partial=True).
  A lawful conditional skip carries error="" and never fails a
  Join or the chain. Visual (flow_visual) and observer (outcome
  ledger) consumers agree with the same canonical receipt.
- B7 Join/Parallel: the closing Join evaluates the completed
  block's ACTUAL results — a captured sibling failure makes the
  Join fail (incoming=2 fails=1), the block frame status is
  "fail", and the chain error keeps the root cause. All-success
  blocks pass their Join; a post-block Join sees the finished
  block's results identically.
- B8 Until: the empty condition is true in BOTH surfaces (core
  arm and chain), zero iterations; the frame exposes bound +
  actual iterations; a bounded Until still fails bound_reached.
- B9 ForEach: empty selection = zero iterations and a valid
  empty execution in both surfaces — core arm n=0, no plane-id
  fallback; member iterations produce one receipt set per member.

Labels: INTEGRATION / PUBLIC_ENTRY (real Program via
form.open.Program, public executor).
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
                f"confirm_current_{owner}.json",
                f"exchange_journal_{owner}.json"):
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


def _dells(r):
    return [a.get("dell") for a in r.get("atom_results") or []]


def _recs(r, dell):
    return [a for a in r.get("atom_results") or []
            if a.get("dell") == dell]


def _msgs(r):
    return [m for m in r.get("messages", [])
            if not m.startswith(("Mandell:", "English:"))]


def _ctrl(p):
    return getattr(p.core_ii, "last_control", None) or {}


# ------------------------------------------------------------ DAF-08
def _daf08() -> None:
    # Director probe 1 (verbatim): FlowOver skip.
    p = _prog("S7D1")
    r = _run(p, "51[Select] >>> 08[Create] > 61[Join]")
    skip8 = _recs(r, 8)
    _rec("DAF-08 P1: FlowOver seed receipts are [51, 8, 61] in order",
         _dells(r) == [51, 8, 61], str(_dells(r)))
    _rec("DAF-08 P1: skipped Dell 8 carries a skipped receipt with reason",
         len(skip8) == 1 and skip8[0].get("skipped") is True
         and skip8[0].get("ok") is False and bool(skip8[0].get("reason")),
         str(skip8))
    _rec("DAF-08 P1: aggregates agree — any_skipped=True, partial=True, "
         "chain still ok=True (lawful skip is not a failure verdict)",
         r.get("any_skipped") is True and r.get("partial") is True
         and r.get("ok") is True and r.get("chain_skipped") == [8],
         f"{r.get('any_skipped')}/{r.get('partial')}/{r.get('ok')}")
    _cleanup("S7D1")

    # Director probe 2 (verbatim): Branch false, no Else.
    p = _prog("S7D2")
    r = _run(p, "60[false] > 08[Create] > 61[Join]")
    _rec("DAF-08 P2: Branch receipts are [60, 8, 61] — head + skipped "
         "body + join, in atom order",
         _dells(r) == [60, 8, 61], str(_dells(r)))
    _rec("DAF-08 P2: unchosen body receipt is a lawful skip (error='') "
         "and the chain verdict stays ok=True",
         _recs(r, 8)[0].get("skipped") is True
         and _recs(r, 8)[0].get("error") == ""
         and r.get("ok") is True and r.get("any_skipped") is True,
         str(_recs(r, 8)))
    _cleanup("S7D2")

    # Director probe 3 (verbatim): Until already true.
    p = _prog("S7D3")
    r = _run(p, "64[true] > 08[Create] > 61[Join]")
    _rec("DAF-08 P3: zero-iteration Until receipts are [64, 8, 61]",
         _dells(r) == [64, 8, 61], str(_dells(r)))
    _rec("DAF-08 P3: body receipt reason names zero iterations; "
         "any_skipped=True; chain ok=True",
         "zero iterations" in (_recs(r, 8)[0].get("reason") or "")
         and r.get("any_skipped") is True and r.get("ok") is True,
         str(_recs(r, 8)))
    _cleanup("S7D3")

    # Branch with Else, true arm: receipts in exact atom order,
    # Else marker + false arm skipped, Join passes (lawful skips
    # do not fail it).
    p = _prog("S7D4")
    _run(p, "82[Group] :: FalseArm")
    r = _run(p, "60[true] > 80[TrueArm] > 59[Else] > 53[FalseArm] > 61[Join]")
    _rec("DAF-08: Branch/Else receipts equal the seed atom order "
         "[60, 80, 59, 53, 61]",
         _dells(r) == [60, 80, 59, 53, 61], str(_dells(r)))
    _rec("DAF-08: Else marker + unchosen arm are skipped receipts; "
         "chain ok=True and partial=True",
         _recs(r, 59)[0].get("skipped") is True
         and _recs(r, 53)[0].get("skipped") is True
         and r.get("ok") is True and r.get("partial") is True,
         str(_dells(r)))
    _cleanup("S7D4")

    # Branch false with Else: false arm runs, receipts ordered.
    p = _prog("S7D5")
    _run(p, "82[Group] :: FalseArm")
    r = _run(p, "60[false] > 80[TrueArm] > 59[Else] > 53[FalseArm] > 61[Join]")
    _rec("DAF-08: Branch false receipts equal atom order "
         "[60, 80, 59, 53, 61] with only 80/59 skipped",
         _dells(r) == [60, 80, 59, 53, 61]
         and [a.get("dell") for a in r.get("atom_results") or []
              if a.get("skipped")] == [80, 59],
         str(_dells(r)))
    _cleanup("S7D5")

    # Multiple else: explicit failure, every body occurrence receipted.
    p = _prog("S7D6")
    r = _run(p, "60[true] > 80[TrueArm] > 59[Else] > 53[FalseArm] > "
                "59[Else] > 90[Trace] > 61[Join]")
    _rec("DAF-08: multiple_else fails explicitly and receipts cover "
         "every atom occurrence",
         r.get("error") == "multiple_else"
         and _dells(r) == [60, 80, 59, 53, 59, 90, 61],
         f"{r.get('error')} / {_dells(r)}")
    _cleanup("S7D6")

    # FlowThru skip receipt retained (pre-existing contract).
    p = _prog("S7D7")
    r = _run(p, "91[false] >> 80[TrueArm]")
    _rec("DAF-08: FlowThru-blocked atom keeps its skipped receipt "
         "with the flow_thru_block error",
         len(_recs(r, 80)) == 1
         and _recs(r, 80)[0].get("error") == "flow_thru_block"
         and r.get("any_skipped") is True,
         str(_recs(r, 80)))
    _cleanup("S7D7")

    # Repeated Dell in one body: separate receipts per occurrence.
    p = _prog("S7D8")
    r = _run(p, "63[Sequence] > 80[Alpha] > 80[Beta] > 61[Join]")
    _rec("DAF-08: repeated Dell body — two distinct 80 receipts, "
         "head receipt present, order [63, 80, 80, 61]",
         _dells(r) == [63, 80, 80, 61]
         and len(_recs(r, 80)) == 2,
         str(_dells(r)))
    _cleanup("S7D8")

    # Nested block: Branch inside Sequence — occurrence-complete.
    p = _prog("S7D9")
    r = _run(p, "63[Sequence] > 60[true] > 80[TrueArm] > 61[Join] > 61[Join]")
    _rec("DAF-08: nested Branch-in-Sequence receipts are "
         "[63, 60, 80, 61, 61] (inner + outer Join separate)",
         _dells(r) == [63, 60, 80, 61, 61] and r.get("ok") is True,
         str(_dells(r)))
    _cleanup("S7D9")

    # Consumers: flow_visual alignment + outcome ledger agree with
    # the same canonical receipt.
    from form.mandell.flow_visual import _steps
    p = _prog("S7D10")
    seed = "60[false] > 08[Create] > 61[Join]"
    r = _run(p, seed)
    _, steps, aligned = _steps(seed, r.get("atom_results") or [])
    _rec("DAF-08 consumer: flow_visual aligns the Branch receipt "
         "1:1 with the seed atoms and marks Dell 8 skipped",
         aligned is True
         and [s["status"] for s in steps].count("skipped") == 1,
         f"aligned={aligned} steps={steps}")
    _cleanup("S7D10")


# ---------------------------------------------------------------- B7
def _b7() -> None:
    p = _prog("S7B7A")
    r = _run(p, "62[Parallel] > 91[false] > 80[TrueArm] > 61[Join]")
    jm = [m for m in _msgs(r) if m.startswith("Join ")]
    _rec("B7: closing Join evaluates actual results — "
         "'Join policy=all ok=False incoming=2 fails=1'",
         jm == ["Join policy=all ok=False incoming=2 fails=1"], str(jm))
    _rec("B7: parallel frame verdict is fail; chain error keeps the "
         "root cause assert_fail (not join_fail)",
         _ctrl(p).get("kind") == "parallel"
         and _ctrl(p).get("status") == "fail"
         and r.get("ok") is False and r.get("error") == "assert_fail",
         f"{_ctrl(p).get('status')} / {r.get('error')}")
    r2 = _run(p, "61[Join]")
    jm2 = [m for m in _msgs(r2) if m.startswith("Join ")]
    _rec("B7: post-block Join (all) sees the finished block — "
         "incoming=3 fails=1 join_fail (verdict receipt not "
         "double-counted)",
         r2.get("ok") is False and r2.get("error") == "join_fail"
         and jm2 == ["Join policy=all ok=False incoming=3 fails=1"],
         str(jm2))
    r3 = _run(p, "61[Join] :: any")
    jm3 = [m for m in _msgs(r3) if m.startswith("Join ")]
    _rec("B7: post-block Join (any) passes on the same results",
         r3.get("ok") is True
         and jm3 == ["Join policy=any ok=True incoming=3 fails=1"],
         str(jm3))
    _cleanup("S7B7A")

    p = _prog("S7B7B")
    r = _run(p, "62[Parallel] > 80[TrueArm] > 80[Beta] > 61[Join]")
    jm = [m for m in _msgs(r) if m.startswith("Join ")]
    _rec("B7: all-success Parallel — Join ok with incoming=2, "
         "frame status ok, chain ok",
         jm == ["Join policy=all ok=True incoming=2 fails=0"]
         and _ctrl(p).get("status") == "ok" and r.get("ok") is True,
         str(jm))
    _cleanup("S7B7B")

    p = _prog("S7B7C")
    r = _run(p, "63[Sequence] > 91[false] > 80[TrueArm] > 61[Join]")
    jm = [m for m in _msgs(r) if m.startswith("Join ")]
    _rec("B7: Sequence with a failing child — closing Join fails "
         "on actual results and the frame verdict is fail",
         jm == ["Join policy=all ok=False incoming=2 fails=1"]
         and _ctrl(p).get("status") == "fail"
         and r.get("error") == "assert_fail",
         f"{jm} / {_ctrl(p).get('status')} / {r.get('error')}")
    _cleanup("S7B7C")


# ---------------------------------------------------------------- B8
def _b8() -> None:
    p = _prog("S7B8A")
    r = _run(p, "64[Until]")
    _rec("B8: bare Until — core arm and chain AGREE the empty "
         "condition is true (zero iterations)",
         "Until cond=true already=True bound=8" in _msgs(r)
         and "Until already true — zero iterations" in _msgs(r)
         and r.get("ok") is True,
         str([m for m in _msgs(r) if "Until" in m]))
    _rec("B8: frame exposes bound=8 alongside iterations=0, "
         "status zero, empty condition",
         _ctrl(p).get("bound") == 8 and _ctrl(p).get("iterations") == 0
         and _ctrl(p).get("status") == "zero"
         and _ctrl(p).get("condition") == "",
         str({k: _ctrl(p).get(k) for k in ("bound", "iterations", "status", "condition")}))
    _cleanup("S7B8A")

    p = _prog("S7B8B")
    _run(p, "72[Limit] :: 3")
    r = _run(p, "64[false] > 80[TrueArm] > 61[Join]")
    _rec("B8: bounded Until — frame bound=3 == iterations=3, "
         "status bounded, error bound_reached, one receipt per "
         "iteration plus head/join",
         _ctrl(p).get("bound") == 3 and _ctrl(p).get("iterations") == 3
         and _ctrl(p).get("status") == "bounded"
         and r.get("error") == "bound_reached"
         and _dells(r) == [64, 80, 80, 80, 61],
         f"{_ctrl(p)} / {_dells(r)}")
    _cleanup("S7B8B")

    p = _prog("S7B8C")
    r = _run(p, "65[false] > 08[Create] > 61[Join]")
    _rec("B8: While already false — zero iterations, body receipted "
         "as skipped, frame bound exposed",
         _dells(r) == [65, 8, 61]
         and _recs(r, 8)[0].get("skipped") is True
         and _ctrl(p).get("bound") == 8
         and _ctrl(p).get("iterations") == 0 and r.get("ok") is True,
         str(_dells(r)))
    _cleanup("S7B8C")


# ---------------------------------------------------------------- B9
def _b9() -> None:
    p = _prog("S7B9A")
    r = _run(p, "66[ForEach]")
    _rec("B9: bare ForEach — core arm reports n=0 / empty_ok=True "
         "(no plane-id fallback) and the chain agrees",
         "ForEach n=0 op=identity empty_ok=True" in _msgs(r)
         and "ForEach empty selection valid" in _msgs(r)
         and r.get("ok") is True,
         str([m for m in _msgs(r) if "ForEach" in m]))
    _cleanup("S7B9A")

    p = _prog("S7B9B")
    r = _run(p, "66[ForEach] > 80[TrueArm] > 61[Join]")
    _rec("B9: empty-selection ForEach chain — zero iterations, "
         "valid empty execution, body receipted as skipped",
         _ctrl(p).get("status") == "empty"
         and _ctrl(p).get("iterations") == 0 and r.get("ok") is True
         and _dells(r) == [66, 80, 61]
         and _recs(r, 80)[0].get("skipped") is True,
         f"{_ctrl(p).get('status')} / {_dells(r)}")
    _cleanup("S7B9B")

    p = _prog("S7B9C")
    _run(p, "08[Create] :: Garden Gate")
    _run(p, "08[Create] :: Stone Wall")
    _run(p, "51[Select]")
    r = _run(p, "66[ForEach] > 80[TrueArm] > 61[Join]")
    members = [a.get("member") for a in _ctrl(p).get("results") or []
               if a.get("member")]
    _rec("B9: ForEach over 3 members — iterations=3, one member "
         "receipt set per member, receipts [66, 80, 80, 80, 61]",
         _ctrl(p).get("iterations") == 3
         and members == ["welcome", "garden_gate", "stone_wall"]
         and _dells(r) == [66, 80, 80, 80, 61] and r.get("ok") is True,
         f"{members} / {_dells(r)}")
    _cleanup("S7B9C")


def main() -> bool:
    _daf08()
    _b7()
    _b8()
    _b9()
    total = len(RESULTS)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        if not ok:
            print(f"FAIL {name} :: {detail}")
    print(f"STEP7_CONTROL_VERDICTS: {passed}/{total}")
    return passed == total


def smoke() -> bool:
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
