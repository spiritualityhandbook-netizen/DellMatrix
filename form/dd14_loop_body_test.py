#!/usr/bin/env python3
"""DD-14 — Dell 13 Loop must repeat its CHAINED BODY per round
(Ace-directed fix-first, 2026-11-09; extension-register defect).

Verified behaviorally at base 7399ee5 (grounding:
hidden_files/dd14_ground.md; probe hidden_files/dd14_probe.py):

- Chain `13[Loop] :: 3 > 25[Pulse] > 16[Decay]` prints
  "Loop: requested 3, executed 3" and Loop's own ringed growth
  DOES run 3 rounds (Nursery pending +9), but Pulse and Decay
  each execute exactly ONCE: one receipt each, and the score
  arithmetic is identical to the no-Loop control chain
  (0.45 = one pulse +0.5 then one decay x0.9).
- Mechanism: executor_leaf primary==13 only calls
  program.grow_ideas(count); it cannot see downstream atoms.
  chain_exec CONTROL_HEADS are Dells 60-66 only, so Dell 13
  runs as an ordinary leaf atom once. No Loop-body semantics
  exist in the chain layer.

Contract proven here (Ace's recorded lean, 2026-11-08: a Loop
that actually repeats the chain is genuinely different from
Cycle, the growth-only repeater):
A. With Loop count N at the chain head, every downstream body
   atom executes N times: score arithmetic equals N rounds of
   (Pulse then Decay) — round r: s -> (s + 0.5) * 0.9 — and the
   chain receipts show one receipt per body atom per round.
B. The count grammar is unchanged in the chain: requested 2
   runs 2 rounds; requested 7 clamps to 5 rounds (DIR-F13).
C. Controls that must hold before AND after the repair: bare
   Loop behavior unchanged (growth rounds, pending +9 for 3,
   no score effect); the no-Loop Pulse>Decay chain still runs
   exactly one round; the Loop receipt line still claims the
   executed count; a genuinely failing body atom still makes
   the chain report ok=False (first-failure truth, 72-19).

Evidence class: INTEGRATION / public seed path
(form.mandell.executor.execute_seed on an attached Program,
the same door the grounding probe used). Isolated synthetic
owners, uuid-unique; cleanup via canonical form.persist paths,
cleanup errors FAIL the suite. The suite defines smoke() for
the regress harness (72-32 lesson: a registered suite without
smoke() is a suite-contract defect).
"""
import os
import sys
import uuid

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

RESULTS = []
_CLEANUP_ERRORS = []
_OWNERS = []

TOL = 1e-6


def _rec(name, cond, detail=""):
    RESULTS.append((name, bool(cond), str(detail)[:220]))


def _owner(tag):
    owner = f"DD14{tag}{uuid.uuid4().hex[:8].upper()}"
    _OWNERS.append(owner)
    return owner


def _cleanup(owner):
    from pathlib import Path

    from form.persist import _STATE_DIR, _safe_owner
    from form.dell_matrix.nursery import owner_nursery_path

    state = Path(_STATE_DIR)
    safe = _safe_owner(owner)
    cands = [state / f"program_{safe}.json", Path(owner_nursery_path(owner))]
    cands += list(state.glob(f"*{safe}*"))
    for pth in set(cands):
        try:
            if pth.is_dir():
                import shutil

                shutil.rmtree(pth)
            elif pth.exists():
                pth.unlink()
        except Exception as exc:  # cleanup errors fail the suite
            _CLEANUP_ERRORS.append(f"{pth}: {exc!r}")


def _prog(owner):
    _cleanup(owner)
    from form.open import Program
    from form.mandell.core_ii_exec import attach

    p = Program(owner=owner)
    attach(p)
    return p


def _run(p, seed):
    from form.mandell.executor import execute_seed

    return execute_seed(p, seed)


def _seeded(owner):
    p = _prog(owner)
    _run(p, "08[Create] :: Alpha")
    _run(p, "08[Create] :: Beta")
    p.enhance_on()
    return p


def _rounds_score(rounds):
    s = 0.0
    for _ in range(rounds):
        s = (s + 0.5) * 0.9
    return s


def _receipt_counts(result):
    counts = {}
    for r in result.get("atom_results") or []:
        counts[r.get("dell")] = counts.get(r.get("dell"), 0) + 1
    return counts


def main():
    # ---------- A: Loop head repeats the chained body ---------
    owner = _owner("A")
    p = _seeded(owner)
    r = _run(p, "13[Loop] :: 3 > 25[Pulse] > 16[Decay]")
    scores = p.scores()
    expect3 = _rounds_score(3)
    _rec("A.loop3_scores_equal_three_rounds",
         abs(scores.get("alpha", -1) - expect3) < TOL
         and abs(scores.get("beta", -1) - expect3) < TOL,
         f"scores={scores} expected~{expect3}")
    counts = _receipt_counts(r)
    _rec("A.loop3_receipts_per_round",
         counts.get(25) == 3 and counts.get(16) == 3,
         f"receipt_counts={counts}")
    ran = r.get("chain_ran") or []
    _rec("A.loop3_chain_ran_per_round",
         ran.count(25) == 3 and ran.count(16) == 3,
         f"chain_ran={ran}")
    _cleanup(owner)

    # ---------- B: count grammar in chains --------------------
    owner = _owner("B2")
    p = _seeded(owner)
    _run(p, "13[Loop] :: 2 > 25[Pulse] > 16[Decay]")
    s2 = p.scores().get("alpha", -1)
    _rec("B.loop2_scores_equal_two_rounds",
         abs(s2 - _rounds_score(2)) < TOL,
         f"alpha={s2} expected~{_rounds_score(2)}")
    _cleanup(owner)

    owner = _owner("B7")
    p = _seeded(owner)
    _run(p, "13[Loop] :: 7 > 25[Pulse] > 16[Decay]")
    s7 = p.scores().get("alpha", -1)
    _rec("B.loop7_clamps_to_five_rounds",
         abs(s7 - _rounds_score(5)) < TOL,
         f"alpha={s7} expected~{_rounds_score(5)}")
    _cleanup(owner)

    # ---------- C: controls (hold before and after) -----------
    owner = _owner("C1")
    p = _seeded(owner)
    r = _run(p, "13[Loop] :: 3")
    _rec("C.bare_loop_unchanged",
         r.get("ok") is True and p.nursery.summary()["pending"] == 9
         and p.scores() == {},
         f"ok={r.get('ok')} pending={p.nursery.summary()['pending']} "
         f"scores={p.scores()}")
    _cleanup(owner)

    owner = _owner("C2")
    p = _seeded(owner)
    _run(p, "25[Pulse] > 16[Decay]")
    sc = p.scores().get("alpha", -1)
    _rec("C.no_loop_control_one_round",
         abs(sc - _rounds_score(1)) < TOL,
         f"alpha={sc} expected~{_rounds_score(1)}")
    _cleanup(owner)

    owner = _owner("C3")
    p = _seeded(owner)
    r = _run(p, "13[Loop] :: 3 > 25[Pulse] > 16[Decay]")
    joined = "\n".join(r.get("messages") or [])
    _rec("C.loop_receipt_claims_executed_3",
         "requested 3, executed 3" in joined,
         f"messages={r.get('messages')}")
    _cleanup(owner)

    # ---------- D: failure honesty ----------------------------
    owner = _owner("D")
    p = _seeded(owner)
    r = _run(p, "13[Loop] :: 2 > 53[Scope] :: Nowhere")
    _rec("D.failing_body_atom_chain_reports_failure",
         r.get("ok") is False,
         f"ok={r.get('ok')} error={r.get('error')!r}")
    _cleanup(owner)

    # ---------- cleanup residue -------------------------------
    for owner in _OWNERS:
        _cleanup(owner)
    residue = []
    from pathlib import Path

    from form.persist import _STATE_DIR, _safe_owner

    state = Path(_STATE_DIR)
    for owner in _OWNERS:
        safe = _safe_owner(owner)
        residue += [str(x) for x in state.glob(f"*{safe}*")]
    _rec("cleanup.no_errors", _CLEANUP_ERRORS == [], str(_CLEANUP_ERRORS))
    _rec("cleanup.leaves_no_residue", residue == [], str(residue))

    passed = sum(1 for _, ok_, _ in RESULTS if ok_)
    for name, ok_, detail in RESULTS:
        if not ok_:
            print(f"FAIL {name}: {detail}")
    print(f"DD14_LOOP_BODY: {passed}/{len(RESULTS)}")
    return passed == len(RESULTS) and len(RESULTS) > 0


def smoke():
    return main()


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
