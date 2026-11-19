#!/usr/bin/env python3
"""R25 / GP-E04 — Dell 57/73 overlong shorthand must REFUSE.

Defect (Director directive 7005888828, verified on main
9f8642ab; Uni failing-first probe r25_logs/probe_prefix_red.log):
the Compare (57) shorthand rewrite kept only the first two
tokens ("eq:" + toks[:2]) and Threshold (73) mapped
len>=2 to gte of the first two — so "N 5 dropped" answered a
successful verdict on a question nobody asked in full. The
legacy pin rewrite_drops_tokens_beyond_two enshrined the
loss as a contract.

Contract after repair (query_ops.apply_query 57/73):
- Exactly two shorthand operands keep the existing 57 eq /
  73 gte semantics and result types; one-operand and bare
  Threshold forms and bare Compare keep their documented
  behavior.
- More than two shorthand operands refuse typed fail-closed:
  ok=False, error="condition_extra_operand", matched=False,
  the refusal cell is the only state written (store /
  selection / weights untouched).
- Malformed quoting in shorthand refuses
  condition_unparseable; the DD-42 infix refusal
  (condition_unparseable) is unchanged and takes precedence
  over the surplus check.
- Explicit recognized predicates (eq:, gte:, contains:,
  starts:, ends:) are the governed parser's forms and keep
  working exactly at these Dells.
- Assert (91) / Guard (92) / Branch (60) observe the shared
  predicate result: a shorthand surplus condition reaches
  them as a refusal (condition_unparseable at the engine),
  never a stamped verdict or a taken arm.

Labels: PUBLIC_ENTRY_PATH (execute_seed). Hygiene: uuid
owners, exact-pattern cleanup, cleanup errors fail the suite.
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
    p = Program(owner=f"R25{tag}{RUN}")
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


def _snap(st):
    return (dict(st.store), list(st.selected), dict(st.weights))


def main():
    # ---------- Compare (57): surplus refuses, state intact ----------
    p = _prog("C")
    st = p.core_ii
    execute_seed(p, "51[Select]")
    execute_seed(p, "74[Weight] :: N=2")
    for lab in ("N 5 dropped", "N 5 extra", "N 5 extra more"):
        before = _snap(st)
        ok, err = _atom(execute_seed(p, f"57[Compare] :: {lab}"))
        lr = st.last_result or {}
        check(f"compare.extra_refused[{lab}]",
              ok is False and err == "condition_extra_operand"
              and lr.get("error") == "condition_extra_operand"
              and lr.get("matched") is False
              and lr.get("source") == "compare",
              f"ok={ok} err={err} lr={lr}")
        check(f"compare.extra_no_mutation[{lab}]",
              _snap(st) == before, f"before={before} after={_snap(st)}")
    # Controls: exactly-two shorthand, explicit forms, soft missing,
    # mixed types, malformed comma/quote, DD-42 infix.
    ok, err = _atom(execute_seed(p, "57[Compare] :: N 5"))
    lr = st.last_result or {}
    check("compare.two_operand_shorthand_preserved",
          ok is True and lr.get("matched") is True
          and lr.get("predicate") == "eq",
          f"ok={ok} err={err} lr={lr}")
    ok, err = _atom(execute_seed(p, "57[Compare] :: eq: store:N 5"))
    lr = st.last_result or {}
    check("compare.explicit_eq_preserved",
          ok is True and lr.get("matched") is True,
          f"ok={ok} err={err} lr={lr}")
    ok, err = _atom(execute_seed(p, "57[Compare] :: contains: store:S ell"))
    lr = st.last_result or {}
    check("compare.explicit_contains_preserved",
          ok is True and lr.get("matched") is True,
          f"ok={ok} err={err} lr={lr}")
    ok, err = _atom(execute_seed(p, "57[Compare] :: eq: store:Ghost 5"))
    lr = st.last_result or {}
    check("compare.missing_key_soft_preserved",
          ok is True and lr.get("matched") is False
          and lr.get("error") == "missing",
          f"ok={ok} err={err} lr={lr}")
    ok, err = _atom(execute_seed(p, "57[Compare] :: eq: store:N hello"))
    check("compare.mixed_types_type_mismatch_preserved",
          ok is False and err == "type_mismatch",
          f"ok={ok} err={err}")
    ok, err = _atom(execute_seed(p, "57[Compare] :: N, 5, dropped"))
    check("compare.malformed_comma_surplus_refused",
          ok is False and err == "condition_extra_operand",
          f"ok={ok} err={err}")
    ok, err = _atom(execute_seed(p, '57[Compare] :: N "5'))
    check("compare.malformed_quote_refused",
          ok is False and err == "condition_unparseable",
          f"ok={ok} err={err}")
    ok, err = _atom(execute_seed(p, "57[Compare] :: N gt 5"))
    check("compare.dd42_infix_refused",
          ok is False and err == "condition_unparseable",
          f"ok={ok} err={err}")
    ok, err = _atom(execute_seed(p, "57[Compare]"))
    lr = st.last_result or {}
    check("compare.bare_vacuous_truth_preserved",
          ok is True and lr.get("value") is True,
          f"ok={ok} err={err} lr={lr}")

    # ---------- Threshold (73): surplus refuses, state intact ----------
    p = _prog("T")
    st = p.core_ii
    execute_seed(p, "51[Select]")
    execute_seed(p, "74[Weight] :: N=2")
    for lab in ("N 5 extra", "N 5 dropped"):
        before = _snap(st)
        ok, err = _atom(execute_seed(p, f"73[Threshold] :: {lab}"))
        lr = st.last_result or {}
        check(f"threshold.extra_refused[{lab}]",
              ok is False and err == "condition_extra_operand"
              and lr.get("error") == "condition_extra_operand"
              and lr.get("matched") is False
              and lr.get("source") == "threshold",
              f"ok={ok} err={err} lr={lr}")
        check(f"threshold.extra_no_mutation[{lab}]",
              _snap(st) == before, f"before={before} after={_snap(st)}")
    ok, err = _atom(execute_seed(p, "73[Threshold] :: N 5"))
    lr = st.last_result or {}
    check("threshold.two_operand_shorthand_preserved",
          ok is True and lr.get("matched") is True,
          f"ok={ok} err={err} lr={lr}")
    ok, err = _atom(execute_seed(p, "73[Threshold] :: gte: store:N 5"))
    lr = st.last_result or {}
    check("threshold.explicit_gte_preserved",
          ok is True and lr.get("matched") is True,
          f"ok={ok} err={err} lr={lr}")
    ok, err = _atom(execute_seed(p, "73[Threshold] :: threshold: N 5"))
    lr = st.last_result or {}
    check("threshold.alias_two_operand_preserved",
          ok is True and lr.get("matched") is True,
          f"ok={ok} err={err} lr={lr}")
    ok, err = _atom(execute_seed(p, "73[Threshold] :: threshold: N 5 extra"))
    check("threshold.alias_extra_refused",
          ok is False and err == "condition_extra_operand",
          f"ok={ok} err={err}")
    ok, err = _atom(execute_seed(p, "73[Threshold] :: N gt 5"))
    check("threshold.dd42_infix_refused",
          ok is False and err == "condition_unparseable",
          f"ok={ok} err={err}")
    ok, err = _atom(execute_seed(p, '73[Threshold] :: N "5 extra'))
    check("threshold.malformed_quote_refused",
          ok is False and err == "condition_unparseable",
          f"ok={ok} err={err}")
    # One-operand form maps to gte:count N — the selection
    # here holds exactly 1 id, so ":: 1" is the true verdict
    # and ":: 5" the honest false one; both atoms succeed.
    ok, err = _atom(execute_seed(p, "73[Threshold] :: 1"))
    lr = st.last_result or {}
    ok5, err5 = _atom(execute_seed(p, "73[Threshold] :: 5"))
    lr5 = st.last_result or {}
    check("threshold.one_operand_count_form_preserved",
          ok is True and lr.get("matched") is True
          and ok5 is True and lr5.get("matched") is False,
          f"1: ok={ok} lr={lr} 5: ok={ok5} lr={lr5}")
    ok, err = _atom(execute_seed(p, "73[Threshold]"))
    lr = st.last_result or {}
    check("threshold.bare_default_preserved",
          ok is True and lr.get("matched") is True,
          f"ok={ok} err={err} lr={lr}")

    # ---------- Shared consumers: no verdict on a surplus ----------
    p = _prog("J")
    st = p.core_ii
    _atom(execute_seed(p, "91[Assert] :: gt:N 3"))
    _atom(execute_seed(p, "92[Guard] :: gt:N 3"))
    assert st.last_assert == "PASS" and st.last_guard == "ALLOW"
    ok, err = _atom(execute_seed(p, "91[Assert] :: N 5 extra"))
    check("assert.shorthand_extra_no_verdict",
          ok is False and err == "condition_unparseable"
          and st.last_assert == "PASS",
          f"ok={ok} err={err} last_assert={st.last_assert!r}")
    ok, err = _atom(execute_seed(p, "92[Guard] :: N 5 extra"))
    check("guard.shorthand_extra_no_verdict",
          ok is False and err == "condition_unparseable"
          and st.last_guard == "ALLOW",
          f"ok={ok} err={err} last_guard={st.last_guard!r}")
    ok, err = _atom(execute_seed(p, "60[Branch] :: N 5 extra"))
    check("branch.shorthand_extra_no_arm",
          ok is False and err == "condition_unparseable"
          and not (st.branch or {}).get("taken"),
          f"ok={ok} err={err} branch={st.branch}")
    p = _prog("BC")
    out = execute_seed(p, "60[Branch] :: N 5 extra > 55[Set] :: arm=1"
                          " > 61[Join]")
    rs = out.get("atom_results") or []
    branch_rec = [r for r in rs if r.get("dell") == 60]
    body_rec = [r for r in rs if r.get("dell") == 55]
    check("branch.chain_extra_body_not_executed",
          bool(branch_rec) and branch_rec[0].get("ok") is False
          and all(r.get("skipped") for r in body_rec)
          and p.core_ii.store.get("arm") is None,
          f"branch={branch_rec} body={body_rec} store={p.core_ii.store}")

    for tag in TAGS:
        _cleanup(tag)
    ok_n = sum(1 for _, c in RESULTS if c)
    print(f"R25_EXTRA_OPERAND: {ok_n}/{len(RESULTS)}")
    if _CLEANUP_ERRORS:
        print("CLEANUP ERRORS:", _CLEANUP_ERRORS)
        return 1
    return 0 if ok_n == len(RESULTS) else 1


def _cleanup(tag):
    from form.persist import _STATE_DIR, _safe_owner
    from form.dell_matrix.nursery import owner_nursery_path
    owner = f"R25{tag}{RUN}"
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
