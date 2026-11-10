#!/usr/bin/env python3
"""DD-42 — C1.Predicate: infix conditions must REFUSE honestly.

Defect (tour SS12.47a, verified live at 7399ee5): the designed
condition grammar is PREFIX (gt:level 3). An INFIX condition
(level gt 99) matches no predicate prefix, so eval_predicate
fell through to its truthy fallback and judged only the first
token — level gt 99 and level lt 3 BOTH matched at level=5.
On the judge Dells the lie is a verdict: Assert stamped PASS
on a numerically false claim; Guard stamped ALLOW; Branch
always took the true arm; Compare silently re-answered an
eq: question nobody asked.

Contract after repair:
- A multi-token condition that matches no predicate prefix is
  UNPARSEABLE: eval_predicate returns matched=False with
  error="condition_unparseable" and predicate="unparseable".
- The verdict surfaces (Compare 57, Branch 60 leaf + chain,
  Assert 91, Guard 92, and the Threshold 73 sibling rewrite)
  surface the refusal as an atom failure carrying that error —
  never a PASS/FAIL/ALLOW/BLOCK verdict, never a taken arm,
  never a silently re-answered question.
- Designed forms keep working EXACTLY: the prefix battery,
  bare-key truthiness (a bare key ALONE), the named
  truthy/exists/falsey predicates, the empty condition, and
  Compare's two-token eq shorthand / Threshold's gte shorthand.

Labels: PUBLIC_ENTRY_PATH (execute_seed) + engine-level
eval_predicate calls (INTEGRATION). Hygiene: uuid owners,
exact-pattern cleanup, cleanup errors fail the suite.
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
TAGS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def _prog(tag):
    from form.open import Program
    from form.mandell.core_ii_exec import attach
    TAGS.append(tag)
    p = Program(owner=f"DD42{tag}{RUN}")
    attach(p)
    execute = execute_seed(p, "55[Set] :: level=5")
    assert execute is not None
    return p


def execute_seed(p, seed):
    from form.mandell.executor import execute_seed as _es
    return _es(p, seed)


def _atom(res):
    rs = res.get("atom_results") or []
    if rs:
        r = rs[-1]
        return bool(r.get("ok")), (r.get("error") or "")
    return bool(res.get("ok")), (res.get("error") or "")


def _pred(p, expr):
    from form.mandell.predicate import eval_predicate
    return eval_predicate(p.core_ii, p, expr)


def main():
    # ---------- engine level ----------
    p = _prog("E")
    st = p.core_ii
    r = _pred(p, "level gt 99")
    check("engine.infix_gt_refused",
          r["matched"] is False and r["error"] == "condition_unparseable"
          and r["predicate"] == "unparseable", str(r)[:120])
    r = _pred(p, "level lt 3")
    check("engine.infix_lt_refused",
          r["matched"] is False and r["error"] == "condition_unparseable",
          str(r)[:120])
    r = _pred(p, "level eq 5")
    check("engine.infix_eq_refused_even_when_true",
          r["matched"] is False and r["error"] == "condition_unparseable",
          str(r)[:120])
    r = _pred(p, "level banana 3")
    check("engine.garbage_multitoken_refused",
          r["matched"] is False and r["error"] == "condition_unparseable",
          str(r)[:120])
    battery = [("gt:level 3", True), ("gt:level 99", False),
               ("lt:level 99", True), ("lt:level 3", False),
               ("eq:level 5", True), ("gte:level 5", True)]
    got = [(e, _pred(p, e)["matched"]) for e, _ in battery]
    check("engine.prefix_battery_exact",
          got == battery, str(got))
    r = _pred(p, "level")
    check("engine.bare_key_truthy_preserved",
          r["predicate"] == "truthy" and r["matched"] is True
          and r["error"] == "", str(r)[:120])
    r = _pred(p, "nope")
    check("engine.bare_literal_token_truthy",
          r["matched"] is True and r["error"] == "", str(r)[:120])
    r = _pred(p, "store:nope")
    check("engine.bare_missing_store_ref_false_no_error",
          r["matched"] is False and r["error"] == "", str(r)[:120])
    named = [("truthy:level", True), ("exists:level", True),
             ("exists:store:nope", False), ("falsey:store:nope", True)]
    got = [(e, _pred(p, e)["matched"]) for e, _ in named]
    check("engine.named_predicates_preserved", got == named, str(got))
    r = _pred(p, "")
    check("engine.empty_condition_preserved",
          r["matched"] is True and r["error"] == "", str(r)[:120])
    assert st.store.get("level") == "5"

    # ---------- Compare (57) ----------
    p = _prog("C")
    st = p.core_ii
    ok, err = _atom(execute_seed(p, "57[Compare] :: level gt 99"))
    lr = st.last_result or {}
    check("compare.infix_refused",
          ok is False and err == "condition_unparseable"
          and lr.get("error") == "condition_unparseable"
          and lr.get("matched") is not True,
          f"ok={ok} err={err} lr={lr}")
    ok, err = _atom(execute_seed(p, "57[Compare] :: gt:level 99"))
    lr = st.last_result or {}
    check("compare.prefix_false_is_a_verdict",
          ok is True and lr.get("matched") is False and not lr.get("error"),
          f"ok={ok} err={err} lr={lr}")
    ok, err = _atom(execute_seed(p, "57[Compare] :: gt:level 3"))
    lr = st.last_result or {}
    check("compare.prefix_true_verdict",
          ok is True and lr.get("matched") is True,
          f"ok={ok} err={err} lr={lr}")
    ok, err = _atom(execute_seed(p, "57[Compare] :: level 5"))
    lr = st.last_result or {}
    check("compare.eq_shorthand_preserved",
          ok is True and lr.get("matched") is True,
          f"ok={ok} err={err} lr={lr}")
    ok, err = _atom(execute_seed(p, "57[Compare] :: level 5 dropped"))
    lr = st.last_result or {}
    check("compare.truncation_contract_preserved",
          ok is True and lr.get("matched") is True,
          f"ok={ok} err={err} lr={lr}")

    # ---------- English door (operator_bridge) ----------
    from form.mandell.operator_bridge import execute_english
    r = execute_english(p, "branch if ready")
    check("english.branch_if_bare_key_routes",
          r.routed and r.ok and r.resolved_dell == 60,
          f"routed={r.routed} ok={r.ok} err={r.error}")
    r = execute_english(p, "branch if level gt 99")
    check("english.branch_if_infix_refused_honestly",
          r.routed and not r.ok and "condition_unparseable" in (r.error or ""),
          f"routed={r.routed} ok={r.ok} err={r.error}")

    # ---------- Threshold (73, sibling rewrite) ----------
    ok, err = _atom(execute_seed(p, "73[Threshold] :: level gt 99"))
    lr = st.last_result or {}
    check("threshold.infix_refused",
          ok is False and err == "condition_unparseable"
          and lr.get("error") == "condition_unparseable",
          f"ok={ok} err={err} lr={lr}")
    ok, err = _atom(execute_seed(p, "73[Threshold] :: level 5"))
    lr = st.last_result or {}
    check("threshold.gte_shorthand_preserved",
          ok is True and lr.get("matched") is True,
          f"ok={ok} err={err} lr={lr}")

    # ---------- Assert (91) / Guard (92) ----------
    p = _prog("J")
    st = p.core_ii
    # Sentinel stamps first: a refusal must leave the previous
    # verdict stamp untouched (last_guard DEFAULTS to ALLOW on
    # a fresh state, so an unset check would prove nothing).
    _atom(execute_seed(p, "91[Assert] :: gt:level 99"))
    _atom(execute_seed(p, "92[Guard] :: gt:level 3"))
    assert st.last_assert == "FAIL" and st.last_guard == "ALLOW"
    ok, err = _atom(execute_seed(p, "91[Assert] :: level gt 99"))
    check("assert.infix_refused_no_verdict",
          ok is False and err == "condition_unparseable"
          and st.last_assert == "FAIL",
          f"ok={ok} err={err} last_assert={st.last_assert!r}")
    ok, err = _atom(execute_seed(p, "92[Guard] :: level gt 99"))
    check("guard.infix_refused_no_verdict",
          ok is False and err == "condition_unparseable"
          and st.last_guard == "ALLOW",
          f"ok={ok} err={err} last_guard={st.last_guard!r}")
    ok, err = _atom(execute_seed(p, "91[Assert] :: gt:level 99"))
    check("assert.prefix_false_verdict",
          ok is False and err == "assert_fail" and st.last_assert == "FAIL",
          f"ok={ok} err={err} last_assert={st.last_assert!r}")
    ok, err = _atom(execute_seed(p, "91[Assert] :: gt:level 3"))
    check("assert.prefix_true_verdict",
          ok is True and st.last_assert == "PASS",
          f"ok={ok} err={err} last_assert={st.last_assert!r}")
    ok, err = _atom(execute_seed(p, "92[Guard] :: gt:level 99"))
    check("guard.prefix_false_verdict",
          ok is False and err == "guard_block" and st.last_guard == "BLOCK",
          f"ok={ok} err={err} last_guard={st.last_guard!r}")
    ok, err = _atom(execute_seed(p, "92[Guard] :: gt:level 3"))
    check("guard.prefix_true_verdict",
          ok is True and st.last_guard == "ALLOW",
          f"ok={ok} err={err} last_guard={st.last_guard!r}")

    # ---------- Branch (60): leaf + chain ----------
    p = _prog("B")
    st = p.core_ii
    ok, err = _atom(execute_seed(p, "60[Branch] :: level gt 99"))
    check("branch.leaf_infix_refused",
          ok is False and err == "condition_unparseable"
          and not (st.branch or {}).get("taken"),
          f"ok={ok} err={err} branch={st.branch}")
    p = _prog("BC")
    out = execute_seed(p, "60[Branch] :: level gt 99 > 55[Set] :: arm=1"
                          " > 61[Join]")
    rs = out.get("atom_results") or []
    branch_rec = [r for r in rs if r.get("dell") == 60]
    body_rec = [r for r in rs if r.get("dell") == 55]
    check("branch.chain_infix_refused_body_not_executed",
          bool(branch_rec) and branch_rec[0].get("ok") is False
          and branch_rec[0].get("error") == "condition_unparseable"
          and all(r.get("skipped") for r in body_rec)
          and p.core_ii.store.get("arm") is None,
          f"branch={branch_rec} body={body_rec} store={p.core_ii.store}")
    p = _prog("BT")
    out = execute_seed(p, "60[Branch] :: gt:level 3 > 55[Set] :: arm=1"
                          " > 61[Join]")
    check("branch.chain_prefix_true_arm_runs",
          p.core_ii.store.get("arm") == "1",
          f"store={p.core_ii.store} out_err={out.get('error')!r}")

    for tag in TAGS:
        _cleanup(tag)
    ok_n = sum(1 for _, c in RESULTS if c)
    print(f"DD42_PREDICATE_INFIX: {ok_n}/{len(RESULTS)}")
    if _CLEANUP_ERRORS:
        print("CLEANUP ERRORS:", _CLEANUP_ERRORS)
        return 1
    return 0 if ok_n == len(RESULTS) else 1


def _cleanup(tag):
    from form.persist import _STATE_DIR, _safe_owner
    from form.dell_matrix.nursery import owner_nursery_path
    owner = f"DD42{tag}{RUN}"
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


def smoke():
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
