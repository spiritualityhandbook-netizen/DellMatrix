#!/usr/bin/env python3
"""eval_predicate surplus — explicit operands must REFUSE.

Circuit: separate bounded circuit, Director contract accepted /
bounded fix-first implementation authorized in comment 7008502649
(PR #496, 2026-11-19), NOT part of PR #496. Investigation:
EVAL_PREDICATE_SURPLUS_PROPOSAL_2026-11-19 (probes reproduced the
defect at main c2456102).

Defect: eval_predicate (form/mandell/predicate.py) silently
discarded surplus operand tokens in BOTH fixed-arity branches —
the binary branch read parts[0]/parts[1] only and the unary
branch read parts[0] only — so `eq: N 5 extra` answered the
two-operand verdict as if the surplus had never been written.

Contract after repair:
- Binary predicates (eq, ne, lt, lte, gt, gte, contains, starts,
  ends) with MORE than 2 operands refuse: matched=False,
  error="condition_extra_operand", predicate=<operator>, no
  verdict computed from the truncated form, no state mutation.
- Unary predicates (exists, empty, truthy, falsey) with MORE
  than 1 operand refuse the same way.
- Consumers propagate the refusal: Compare (57) and Threshold
  (73) explicit forms fail the atom with that error; Assert
  (91) / Guard (92) stamp no verdict; Branch (60), leaf and
  chain, takes no arm and executes no body.
- Preserved byte-for-byte: under-arity behavior (0/1-operand
  binary, 0-operand unary), set predicates any/all/none (the
  whole rest is ONE free-text needle), bare-token truthiness,
  the empty condition, DD-42 infix refusal
  (condition_unparseable), valid exact-arity forms, and the
  existing missing / type_mismatch semantics.

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

BINARY_SURPLUS = [
    "eq: N 5 extra", "ne: N 5 extra", "lt: N 99 extra",
    "lte: N 99 extra", "gt: N 3 extra", "gte: N 3 extra",
    "contains: S ell extra", "starts: S he extra",
    "ends: S lo extra",
]
UNARY_SURPLUS = [
    "exists: N extra", "empty: N extra",
    "truthy: N extra", "falsey: N extra",
]


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def _prog(tag):
    from form.open import Program
    from form.mandell.core_ii_exec import attach
    TAGS.append(tag)
    p = Program(owner=f"EVP{tag}{RUN}")
    attach(p)
    execute_seed(p, "55[Set] :: N=5")
    execute_seed(p, "55[Set] :: S=hello")
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


def _snap(st):
    return (dict(st.store), list(st.selected), dict(st.weights))


def main():
    # ---------- engine: surplus refuses, state intact ----------
    p = _prog("E")
    st = p.core_ii
    for expr in BINARY_SURPLUS:
        before = _snap(st)
        r = _pred(p, expr)
        op = expr.split(":")[0]
        check(f"engine.binary_extra_refused[{expr}]",
              r["matched"] is False
              and r["error"] == "condition_extra_operand"
              and r["predicate"] == op,
              str(r)[:140])
        check(f"engine.binary_extra_no_mutation[{expr}]",
              _snap(st) == before, "")
    for expr in UNARY_SURPLUS:
        before = _snap(st)
        r = _pred(p, expr)
        op = expr.split(":")[0]
        check(f"engine.unary_extra_refused[{expr}]",
              r["matched"] is False
              and r["error"] == "condition_extra_operand"
              and r["predicate"] == op,
              str(r)[:140])
        check(f"engine.unary_extra_no_mutation[{expr}]",
              _snap(st) == before, "")
    r = _pred(p, "eq: N, 5, extra")
    check("engine.comma_form_extra_refused",
          r["matched"] is False
          and r["error"] == "condition_extra_operand", str(r)[:140])
    r = _pred(p, "EQ: N 5 extra")
    check("engine.case_insensitive_extra_refused",
          r["matched"] is False
          and r["error"] == "condition_extra_operand", str(r)[:140])
    r = _pred(p, "eq: N 5 999")
    check("engine.surplus_verdict_not_truncated_answer",
          r["matched"] is False
          and r["error"] == "condition_extra_operand", str(r)[:140])

    # ---------- engine: preserved behavior ----------
    exact = [("eq: N 5", True), ("ne: N 6", True),
             ("gt: N 3", True), ("lt: N 99", True),
             ("gte: N 5", True), ("lte: N 5", True),
             ("contains: S ell", True), ("starts: S he", True),
             ("ends: S lo", True),
             ("exists: N", True), ("truthy: N", True),
             ("empty: S", False), ("falsey: N", False)]
    got = [(e, _pred(p, e)["matched"]) for e, _ in exact]
    check("engine.exact_arity_battery_preserved", got == exact, str(got))
    errs = [(e, _pred(p, e)["error"]) for e, _ in exact]
    check("engine.exact_arity_no_errors",
          all(e == "" for _, e in errs), str(errs))
    st.selected = ["alpha_one", "beta_two"]
    r = _pred(p, "any: alpha one")
    check("engine.set_multiword_needle_preserved",
          r["matched"] is True and r["error"] == ""
          and r["predicate"] == "any", str(r)[:140])
    r = _pred(p, "none: gamma three")
    check("engine.set_none_multiword_preserved",
          r["matched"] is True and r["error"] == "", str(r)[:140])
    st.selected = []
    r = _pred(p, "N")
    check("engine.bare_token_truthiness_preserved",
          r["predicate"] == "truthy" and r["matched"] is True
          and r["error"] == "", str(r)[:140])
    r = _pred(p, "")
    check("engine.empty_expr_preserved",
          r["predicate"] == "empty" and r["matched"] is True
          and r["error"] == "", str(r)[:140])
    r = _pred(p, "N gt 5")
    check("engine.dd42_infix_preserved",
          r["matched"] is False
          and r["error"] == "condition_unparseable", str(r)[:140])
    r = _pred(p, "eq:")
    check("engine.under_arity_binary_zero_preserved",
          r["matched"] is True and r["error"] == "", str(r)[:140])
    r = _pred(p, "eq: N")
    check("engine.under_arity_binary_one_preserved",
          r["matched"] is False and r["error"] == "type_mismatch",
          str(r)[:140])
    r = _pred(p, "contains: S")
    check("engine.under_arity_contains_preserved",
          r["matched"] is True and r["error"] == "", str(r)[:140])
    r = _pred(p, "exists:")
    check("engine.under_arity_unary_zero_preserved",
          r["matched"] is True and r["error"] == "", str(r)[:140])
    r = _pred(p, "truthy:")
    check("engine.under_arity_truthy_zero_preserved",
          r["matched"] is False and r["error"] == "", str(r)[:140])
    r = _pred(p, "eq: store:Ghost 5")
    check("engine.missing_preserved",
          r["matched"] is False and r["error"] == "missing",
          str(r)[:140])

    # ---------- public entry: Compare (57) / Threshold (73) ----------
    p = _prog("C")
    st = p.core_ii
    execute_seed(p, "51[Select]")
    execute_seed(p, "74[Weight] :: N=2")
    for lab in ("eq: N 5 extra", "contains: S ell extra"):
        before = _snap(st)
        ok, err = _atom(execute_seed(p, f"57[Compare] :: {lab}"))
        lr = st.last_result or {}
        check(f"compare.explicit_extra_refused[{lab}]",
              ok is False and err == "condition_extra_operand"
              and lr.get("error") == "condition_extra_operand"
              and lr.get("matched") is False
              and lr.get("source") == "compare",
              f"ok={ok} err={err} lr={lr}")
        check(f"compare.explicit_extra_no_mutation[{lab}]",
              _snap(st) == before, "")
    ok, err = _atom(execute_seed(p, "57[Compare] :: eq: N 5"))
    lr = st.last_result or {}
    check("compare.explicit_exact_preserved",
          ok is True and lr.get("matched") is True,
          f"ok={ok} err={err} lr={lr}")
    ok, err = _atom(execute_seed(p, "57[Compare] :: eq: store:Ghost 5"))
    lr = st.last_result or {}
    check("compare.missing_soft_preserved",
          ok is True and lr.get("matched") is False
          and lr.get("error") == "missing",
          f"ok={ok} err={err} lr={lr}")
    ok, err = _atom(execute_seed(p, "57[Compare] :: eq: N hello"))
    check("compare.type_mismatch_preserved",
          ok is False and err == "type_mismatch", f"ok={ok} err={err}")
    before = _snap(st)
    ok, err = _atom(execute_seed(p, "73[Threshold] :: gte: N 5 extra"))
    lr = st.last_result or {}
    check("threshold.explicit_extra_refused",
          ok is False and err == "condition_extra_operand"
          and lr.get("error") == "condition_extra_operand"
          and lr.get("matched") is False
          and lr.get("source") == "threshold",
          f"ok={ok} err={err} lr={lr}")
    check("threshold.explicit_extra_no_mutation",
          _snap(st) == before, "")
    ok, err = _atom(execute_seed(p, "73[Threshold] :: gte: N 5"))
    lr = st.last_result or {}
    check("threshold.explicit_exact_preserved",
          ok is True and lr.get("matched") is True,
          f"ok={ok} err={err} lr={lr}")

    # ---------- consumers: Assert / Guard / Branch ----------
    p = _prog("J")
    st = p.core_ii
    _atom(execute_seed(p, "91[Assert] :: gt: N 3"))
    _atom(execute_seed(p, "92[Guard] :: gt: N 3"))
    assert st.last_assert == "PASS" and st.last_guard == "ALLOW"
    for dell, lab in (("91[Assert]", "eq: N 5 extra"),
                      ("91[Assert]", "truthy: N extra"),
                      ("92[Guard]", "eq: N 5 extra"),
                      ("92[Guard]", "exists: N extra")):
        ok, err = _atom(execute_seed(p, f"{dell} :: {lab}"))
        check(f"consumer.refusal_no_verdict[{dell} {lab}]",
              ok is False and err == "condition_extra_operand"
              and st.last_assert == "PASS" and st.last_guard == "ALLOW",
              f"ok={ok} err={err} assert={st.last_assert!r} "
              f"guard={st.last_guard!r}")
    ok, err = _atom(execute_seed(p, "60[Branch] :: eq: N 5 extra"))
    check("branch.leaf_extra_no_arm",
          ok is False and err == "condition_extra_operand"
          and not (st.branch or {}).get("taken"),
          f"ok={ok} err={err} branch={st.branch}")
    p = _prog("BC")
    out = execute_seed(p, "60[Branch] :: eq: N 5 extra > 55[Set] :: arm=1"
                          " > 61[Join]")
    rs = out.get("atom_results") or []
    branch_rec = [r for r in rs if r.get("dell") == 60]
    body_rec = [r for r in rs if r.get("dell") == 55]
    check("branch.chain_extra_body_not_executed",
          bool(branch_rec) and branch_rec[0].get("ok") is False
          and branch_rec[0].get("error") == "condition_extra_operand"
          and all(r.get("skipped") for r in body_rec)
          and p.core_ii.store.get("arm") is None,
          f"branch={branch_rec} body={body_rec} store={p.core_ii.store}")

    for tag in TAGS:
        _cleanup(tag)
    ok_n = sum(1 for _, c in RESULTS if c)
    print(f"EVAL_PREDICATE_SURPLUS: {ok_n}/{len(RESULTS)}")
    if _CLEANUP_ERRORS:
        print("CLEANUP ERRORS:", _CLEANUP_ERRORS)
        return 1
    return 0 if ok_n == len(RESULTS) else 1


def _cleanup(tag):
    from form.persist import _STATE_DIR, _safe_owner
    from form.dell_matrix.nursery import owner_nursery_path
    owner = f"EVP{tag}{RUN}"
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
