#!/usr/bin/env python3
"""D1 deepening circuit 12 — Dell 57 (Compare) deep contract.

Derived from query_ops.apply_query (n==57), predicate.
eval_predicate / resolve_value / _cmp_typed, and the
typed signature (role expression, required):

  head = lab's first token (before ':' or ' '), lowercased
  head in {eq, ne, lt, lte, gt, gte, contains, starts,
  ends} -> the expression is lab itself; otherwise the
  lab is REWRITTEN to "eq:" + its first two tokens —
  "N 5" means eq(N, 5), and any further tokens are dropped.

  Operands resolve (resolve_value): literals (numbers,
  true/false, strings), store keys (bare token or
  store:KEY), count (= len(selected)), selected, context,
  weights, and last_result (= the previous result cell's
  matched, as a boolean). Store strings that parse as
  numbers classify as numbers.

  The cell: value = matched (a bool), matched the same,
  source="compare", predicate = the operator, error, and
  an extra "mode" field: number / string / boolean /
  missing / type_mismatch.

Pinned consequences:
  - type_mismatch is Compare's ONE hard failure: eq/ne
    across types, or an ordering operator on non-numbers,
    fails the ATOM (ok=False, err="type_mismatch").
  - A missing operand is SOFT: the atom stays ok=True;
    the cell carries error="missing", mode="missing",
    matched=False. (The Get pattern, not the Delete one.)
  - A bare Compare (empty lab) compares two empty
    literals and answers matched=True — vacuous truth,
    pinned as-is.
  - Compare is the cluster's composition reader: count
    reads Dell 51's selection and last_result reads ANY
    previous Dell's cell — both proven live here (the
    first symbiosis seams of the query cluster).

English: no surface. "compare N to 5" becomes the Dell 9
question intent and is refused at the route and the REPL.

Signature sync in this circuit: derived_from 39-43 ->
45-53; failures gains the soft-missing distinction;
output states the operand sources and the mode field.

Labels: seed execution PUBLIC_ENTRY_PATH; translate +
route_intent = the REPL's routing authority; the final
checks are the literal REPL in subprocesses (REAL_USER_PATH).
"""
from __future__ import annotations

import glob
import os
import shutil
import subprocess
import sys

RESULTS = []

STATE_DIR = os.path.join(os.path.dirname(__file__), "..", "state")


def _rec(name, cond, detail=""):
    RESULTS.append((name, bool(cond), str(detail)))


def _cleanup(owner):
    for pat in (f"program_{owner}.json", f"nursery_{owner}.json",
                f"checkpoint_{owner}_*", f"confirm_{owner}.journal.json",
                f"current_{owner}.json"):
        for f in glob.glob(os.path.join(STATE_DIR, pat)):
            try:
                os.remove(f)
            except FileNotFoundError:
                pass
            except OSError as exc:
                raise RuntimeError(f"cleanup failed for {f}: {exc}")
    d = os.path.join(STATE_DIR, f"ideas_{owner}")
    if os.path.isdir(d):
        shutil.rmtree(d)


def _fresh(owner):
    _cleanup(owner)
    from form.open import Program
    return Program(owner)


def _store(p):
    from form.mandell.core_ii_exec import attach
    return attach(p)


def _english(p, line):
    from form.mandell.translate import translate
    from form.mandell.semantic_router import route_intent
    return route_intent(p, translate(line), line)


def _repl(owner, lines):
    root = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", ".."))
    _cleanup(owner)
    proc = subprocess.run(
        [sys.executable, "-m", "form.repl", "--owner", owner],
        input=lines, capture_output=True, text=True, cwd=root,
        timeout=180)
    _cleanup(owner)
    return proc.returncode, proc.stdout


def main():
    from form.mandell.executor import execute_seed

    owner = "D157Seed"
    p = _fresh(owner)
    st = _store(p)
    execute_seed(p, "55[Set] :: N=5")
    execute_seed(p, "55[Set] :: S=hello")

    def cmp(lab):
        if lab:
            r = execute_seed(p, f"57[Compare] :: {lab}")
        else:
            r = execute_seed(p, "57[Compare]")
        return r, (st.last_result or {})

    r, lr = cmp("eq: store:N 5")
    _rec("numeric_eq_via_store_ref",
         r.get("ok") and lr.get("value") is True
         and lr.get("mode") == "number"
         and lr.get("source") == "compare",
         f"value={lr.get('value')} mode={lr.get('mode')}")
    r, lr = cmp("N 5")
    _rec("bare_form_rewrites_to_eq_of_first_two_tokens",
         r.get("ok") and lr.get("value") is True
         and lr.get("predicate") == "eq",
         f"pred={lr.get('predicate')} value={lr.get('value')}")
    r, lr = cmp("N 5 dropped")
    _rec("rewrite_drops_tokens_beyond_two",
         r.get("ok") and lr.get("value") is True,
         f"value={lr.get('value')}")
    r1, lr1 = cmp("gt: store:N 3")
    r2, lr2 = cmp("lt: store:N 3")
    _rec("ordering_operators_on_numbers",
         r1.get("ok") and lr1.get("value") is True
         and r2.get("ok") and lr2.get("value") is False,
         f"gt={lr1.get('value')} lt={lr2.get('value')}")
    r, lr = cmp("contains: store:S ell")
    r2, lr2 = cmp("starts: store:S he")
    r3, lr3 = cmp("ends: store:S lo")
    _rec("string_operators",
         lr.get("value") is True and lr2.get("value") is True
         and lr3.get("value") is True
         and lr.get("mode") == "string",
         f"contains={lr.get('value')} starts={lr2.get('value')} "
         f"ends={lr3.get('value')}")
    r, lr = cmp("eq: store:N hello")
    _rec("type_mismatch_eq_fails_the_atom",
         not r.get("ok") and r.get("error") == "type_mismatch"
         and lr.get("mode") == "type_mismatch"
         and lr.get("matched") is False,
         f"ok={r.get('ok')} err={r.get('error')}")
    r, lr = cmp("lt: store:S 3")
    _rec("type_mismatch_ordering_on_string_fails_the_atom",
         not r.get("ok") and r.get("error") == "type_mismatch",
         f"ok={r.get('ok')} err={r.get('error')}")
    r, lr = cmp("eq: store:Ghost 5")
    _rec("missing_operand_is_soft_atom_stays_ok",
         r.get("ok") and lr.get("matched") is False
         and lr.get("error") == "missing"
         and lr.get("mode") == "missing",
         f"ok={r.get('ok')} error={lr.get('error')}")
    r, lr = cmp("")
    _rec("bare_compare_is_vacuous_truth",
         r.get("ok") and lr.get("value") is True
         and lr.get("mode") == "string",
         f"value={lr.get('value')} mode={lr.get('mode')}")
    # Composition seams: count reads Select's output;
    # last_result reads the previous Dell's cell.
    p.place("garden_gate", "Garden Gate")
    p.place("river_stone", "River Stone")
    execute_seed(p, "51[Select]")
    r, lr = cmp("eq: count 3")
    _rec("count_operand_reads_the_selection",
         r.get("ok") and lr.get("value") is True,
         f"value={lr.get('value')}")
    execute_seed(p, "56[Get] :: S")
    r, lr = cmp("eq: last_result true")
    execute_seed(p, "56[Get] :: Ghost")
    r2, lr2 = cmp("eq: last_result false")
    _rec("last_result_operand_reads_the_previous_cell",
         lr.get("value") is True and lr2.get("value") is True
         and lr.get("mode") == "boolean",
         f"after_hit={lr.get('value')} after_miss={lr2.get('value')}")
    r = execute_seed(p, '57[Compare](expression="eq: store:N 5")')
    lr = st.last_result or {}
    _rec("typed_args_compare",
         r.get("ok") and lr.get("value") is True,
         f"value={lr.get('value')}")
    _cleanup(owner)

    # English: no surface.
    owner = "D157Eng"
    p = _fresh(owner)
    st = _store(p)
    execute_seed(p, "55[Set] :: N=5")
    r = _english(p, "compare N to 5")
    lr = st.last_result or {}
    _rec("english_compare_does_not_reach_dell57",
         not r.ok and lr.get("source") != "compare",
         f"ok={r.ok} error={(r.error or '')[:40]}")
    _cleanup(owner)

    # REAL_USER_PATH: the literal REPL.
    rc, out = _repl(
        "D157ReplSeed",
        "51[Select]\n57[Compare] :: eq: count 1\n10[Keep]\n")
    _rec("repl_seed_compare_reports_match_in_output",
         rc == 0 and "matched=True" in out and "mode=number" in out,
         f"rc={rc}")
    rc, out = _repl(
        "D157ReplEng",
        "55[Set] :: N=5\ncompare N to 5\n10[Keep]\n")
    _rec("repl_english_compare_executes_no_compare",
         rc == 0 and "mode=number" not in out,
         f"rc={rc}")

    # Docs sync.
    from form.mandell.signatures import get_signature
    from form.mandell.dell_cards import DEEP_NOTES
    sig = get_signature(57)
    _rec("signature_matches_code",
         sig.derived_from.endswith("45-53")
         and "missing" in sig.failures,
         sig.derived_from)
    _rec("proof_card_carries_the_deep_note",
         57 in DEEP_NOTES and "type_mismatch" in DEEP_NOTES[57],
         DEEP_NOTES.get(57, "")[:60])

    ok = all(c for _, c, _ in RESULTS)
    for name, cond, detail in RESULTS:
        print(f"[{'ok' if cond else 'FAIL'}] {name} :: {detail}")
    n = sum(1 for _, c, _ in RESULTS if c)
    print(f"D1_DELL57_COMPARE: {n}/{len(RESULTS)}")
    return ok


def smoke():
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
