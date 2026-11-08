#!/usr/bin/env python3
"""72-21 — Until/While/ForEach bounds + nested control inheritance:
stress recheck (evidence circuit; no defect expected).

Acceptance (original inventory, = SM-18): loop bounds and
nested control inheritance must be exact. Register remaining
action: "While-specific bounds; nested skip inheritance."

Grounded behavior (control_runtime.py / chain_exec.py, probed
at the public entry path before pinning):

- While with a Limit: the body runs EXACTLY the bound's
  number of iterations (Limit 3 -> 3 receipts, frame
  iterations=3, bound=3, status 'bounded', chain error
  bound_reached). The default bound is 8 with no Limit.
- While whose body clears the condition: exits after 1
  iteration, frame 'ok', bound still exposed (8).
- While with a false initial condition: zero iterations —
  the body occurrence is a skipped receipt, the Join
  passes, the frame is 'zero' (bound exposed), chain
  ok AND partial.
- Until mirrors While at its bound (Limit 3 -> 3
  iterations, 'bounded').
- The Join verdict and the chain verdict are separate
  surfaces: after a bound_reached loop, the closing Join's
  receipt is ok (it judges the EXECUTED atom receipts,
  all of which succeeded) while the chain error carries
  the loop's terminal verdict bound_reached.
- Nested skip inheritance: a skip is CONTAINED — a
  zero-iteration While nested in a Sequence leaves the
  later Sequence members running (the outer Join passes);
  an unchosen Branch arm containing a whole loop frame
  skips the entire subtree (head, body, and inner Join —
  all skipped receipts, no mutation); a ForEach with an
  empty selection skips an inner loop frame through two
  levels, and the ForEach's own Join still passes.
- An inner bound failure does NOT halt an outer body: an
  Until that hits its bound inside a Sequence leaves the
  later Sequence member running, even though the chain
  ends not-ok with bound_reached.

Existing coverage (NOT duplicated): control_runtime_test
(frame mechanics), first_failure_provenance_test (72-19,
loop provenance compositions), frame_guarantees_test
(72-20, frame verdicts and Join policies).

Labels: PUBLIC_ENTRY_PATH throughout (execute_seed).
Hygiene: uuid-unique owners; exact-pattern cleanup;
cleanup failures reported, never swallowed.
"""
from __future__ import annotations

import sys
import uuid
from pathlib import Path

REPO = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, REPO)

RESULTS = []
_CLEANUP_ERRORS = []
RUN = uuid.uuid4().hex[:8]


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def _fresh(tag):
    from form.open import open_program
    return open_program(f"T7221{tag}{RUN}")


def _run(tag, chain, pre=None):
    from form.mandell.executor import execute_seed
    p = _fresh(tag)
    if pre:
        execute_seed(p, pre)
    return p, execute_seed(p, chain)


def _recs(out):
    return [(r.get("dell"), bool(r.get("ok", True)),
             r.get("error") or "", bool(r.get("skipped")))
            for r in (out.get("atom_results") or [])]


def _settled_frame(p, kind):
    fs = [f for f in (p.core_ii.frames or []) if f.get("kind") == kind]
    return fs[-1] if fs else {}


def _join_receipt(out):
    js = [r for r in (out.get("atom_results") or []) if r.get("dell") == 61]
    return js[-1] if js else None


def _cleanup(tag):
    from form.persist import _STATE_DIR, _safe_owner
    from form.dell_matrix.nursery import owner_nursery_path
    owner = f"T7221{tag}{RUN}"
    state = Path(_STATE_DIR)
    safe = _safe_owner(owner)
    cands = [state / f"program_{safe}.json",
             Path(owner_nursery_path(owner))]
    cands += list(state.glob(f"*{safe}*"))
    for pth in set(cands):
        try:
            if pth.is_dir():
                import shutil
                shutil.rmtree(pth)
            elif pth.exists():
                pth.unlink()
        except OSError as exc:
            _CLEANUP_ERRORS.append(f"{pth}: {exc}")


TAGS = []
GO = "55[Set] :: go=1"


def main():
    # --- While bounds ----------------------------------------------
    tag = "W1"; TAGS.append(tag)
    p, out = _run(tag, "72[Limit] :: 3 > 65[store_go] "
                       "> 55[Set] :: tick=1 > 61[Join]", GO)
    body = [r for r in _recs(out) if r[0] == 55]
    check("W1.limit_3_runs_exactly_3", len(body) == 3, str(len(body)))
    fr = _settled_frame(p, "while")
    check("W1.frame_bounded_3_3", fr.get("status") == "bounded"
          and fr.get("iterations") == 3 and fr.get("bound") == 3, str(fr))
    check("W1.chain_error_bound_reached",
          out["ok"] is False and out["error"] == "bound_reached")
    check("W1.join_receipt_still_ok", (_join_receipt(out) or {}).get("ok")
          is True)

    tag = "W2"; TAGS.append(tag)
    p, out = _run(tag, "65[store_go] > 55[Set] :: tick=1 > 61[Join]", GO)
    body = [r for r in _recs(out) if r[0] == 55]
    check("W2.default_bound_8", len(body) == 8, str(len(body)))
    fr = _settled_frame(p, "while")
    check("W2.frame_bounded_8_8", fr.get("status") == "bounded"
          and fr.get("iterations") == 8 and fr.get("bound") == 8, str(fr))

    tag = "W3"; TAGS.append(tag)
    p, out = _run(tag, "65[store_go] > 86[Delete] :: go > 61[Join]", GO)
    fr = _settled_frame(p, "while")
    check("W3.body_clears_condition_exits_after_1",
          fr.get("iterations") == 1 and fr.get("status") == "ok"
          and "go" not in p.core_ii.store, str(fr))
    check("W3.clean", out["ok"] and not out["partial"])

    tag = "W4"; TAGS.append(tag)
    p, out = _run(tag, "65[store_go] > 55[Set] :: never=1 > 61[Join]")
    rec = _recs(out)
    check("W4.zero_iteration_body_skipped",
          (55, False, "", True) in rec, str(rec))
    fr = _settled_frame(p, "while")
    check("W4.frame_zero", fr.get("status") == "zero"
          and fr.get("iterations") == 0 and fr.get("bound") == 8, str(fr))
    check("W4.join_ok_chain_partial",
          (_join_receipt(out) or {}).get("ok") is True
          and out["ok"] and out["partial"])

    # --- Until bounds -----------------------------------------------
    tag = "W5"; TAGS.append(tag)
    p, out = _run(tag, "72[Limit] :: 3 > 64[store_done] "
                       "> 55[Set] :: tick=1 > 61[Join]")
    body = [r for r in _recs(out) if r[0] == 55]
    check("W5.until_limit_3_runs_exactly_3", len(body) == 3, str(len(body)))
    fr = _settled_frame(p, "until")
    check("W5.frame_bounded_3_3", fr.get("status") == "bounded"
          and fr.get("iterations") == 3 and fr.get("bound") == 3, str(fr))
    check("W5.chain_error_bound_reached",
          out["ok"] is False and out["error"] == "bound_reached")

    # --- Nested skip inheritance -------------------------------------
    tag = "N1"; TAGS.append(tag)
    p, out = _run(tag, "63[Sequence] > 65[store_go] > 55[Set] :: inner=1 "
                       "> 61[Join] > 55[Set] :: after=1 > 61[Join]")
    rec = _recs(out)
    check("N1.inner_zero_body_skipped",
          (55, False, "", True) in rec, str(rec))
    check("N1.outer_body_continues", p.core_ii.store.get("after") == "1"
          and "inner" not in p.core_ii.store)
    check("N1.outer_join_ok", (_join_receipt(out) or {}).get("ok") is True)
    check("N1.chain_ok_partial", out["ok"] and out["partial"])

    tag = "N2"; TAGS.append(tag)
    p, out = _run(tag, "60[false] > 65[store_go] > 55[Set] :: inner=1 "
                       "> 61[Join] > 59[Else] > 55[Set] :: outer=1 > 61[Join]",
                  GO)
    rec = _recs(out)
    check("N2.unchosen_loop_subtree_all_skipped",
          (65, False, "", True) in rec
          and (55, False, "", True) in rec
          and (61, False, "", True) in rec, str(rec))
    check("N2.no_inner_mutation", "inner" not in p.core_ii.store
          and p.core_ii.store.get("outer") == "1")

    tag = "N3"; TAGS.append(tag)
    p, out = _run(tag, "63[Sequence] > 72[Limit] :: 2 > 64[store_done] "
                       "> 55[Set] :: tick=1 > 61[Join] "
                       "> 55[Set] :: after=1 > 61[Join]")
    fr = _settled_frame(p, "until")
    check("N3.inner_until_bounded_2_2", fr.get("status") == "bounded"
          and fr.get("iterations") == 2 and fr.get("bound") == 2, str(fr))
    check("N3.outer_body_continues_after_inner_bound",
          p.core_ii.store.get("after") == "1")
    check("N3.outer_join_ok_chain_bound_reached",
          (_join_receipt(out) or {}).get("ok") is True
          and out["ok"] is False and out["error"] == "bound_reached")

    tag = "N4"; TAGS.append(tag)
    p, out = _run(tag, "51[Select] :: nosuchkey > 66[ForEach] "
                       "> 65[store_go] > 55[Set] :: inner=1 "
                       "> 61[Join] > 61[Join]", GO)
    rec = _recs(out)
    check("N4.two_level_skip_inherits",
          (65, False, "", True) in rec
          and (61, False, "", True) in rec, str(rec))
    fr = _settled_frame(p, "foreach")
    check("N4.foreach_frame_empty", fr.get("status") == "empty", str(fr))
    check("N4.outer_join_ok", (_join_receipt(out) or {}).get("ok") is True)

    for t in TAGS:
        _cleanup(t)
    check("cleanup.no_errors", not _CLEANUP_ERRORS, str(_CLEANUP_ERRORS))

    total = len(RESULTS)
    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"loop_bounds_test: {passed}/{total} PASS")
    return 0 if passed == total else 1


def smoke():
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
