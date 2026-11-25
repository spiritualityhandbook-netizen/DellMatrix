#!/usr/bin/env python3
"""GP-E08 — Typed English/LM/Seed admission (Part II, anchor row #24).

Contract (PART_II_PLAN_2026-11-20.md, GP-E08): one lossless AST —
raw user text -> explicit typed roles -> operator -> operand ->
execution mode — with source-span provenance and an ambiguity
verdict; legacy seed semantics preserved for unambiguous cases;
ambiguous delimiter and mis-typed roles rejected BEFORE mutation.

The layer under test is form/mandell/admission.py, built over the
three existing doors (seed.parse_seed, translate.translate,
polyglot.bridge_lang for the la/latin door) — it creates no second
parser. Verification instrument: the modernized #308 oracle
(director-reports/evidence/72-06-intent-args/q06_current_probe.py
+ q06_current_repl_probe.py, merged at f9a275ca), cited by
reference, plus the route-agreement checks below.

Isolation: route checks use unique Program owners and snapshot
idea counts before/after (the q06 probe pattern) — a fresh
Program() is never assumed empty. The macro check registers one
uniquely-named cell and removes it in a finally block.

FAILING-FIRST RECORD (at Part head afc7fd66, before the build):
this suite failed on import — form.mandell.admission did not
exist (the typed admission layer was absent, not misbehaving).
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CHECKS = []


def check(name, cond, detail=""):
    CHECKS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


def run_all():
    from form.mandell.admission import admit, _from_intent
    from form.mandell.translate import Intent
    from form.mandell.seed import CELLS, define_cell, expand_cell
    from form.mandell.semantic_router import route_intent
    from form.open import Program

    # ---------------- Seed door ----------------
    a = admit("10[Keep] > 27[Checkpoint]")
    check("seed_chain_admitted",
          a.verdict == "admitted" and a.kind == "seed" and a.mode == "chain",
          f"verdict={a.verdict} kind={a.kind} mode={a.mode}")
    atoms = [r for r in a.roles if r.name == "atom"]
    check("seed_atom_roles_typed",
          len(atoms) == 2
          and atoms[0].value["dell"] == 10 and atoms[0].value["term"] == "Keep"
          and atoms[1].value["dell"] == 27 and atoms[1].value["term"] == "Checkpoint"
          and all(r.type == "dell_atom" for r in atoms),
          f"atoms={[(r.value, r.type) for r in atoms]}")
    check("seed_atom_spans_literal",
          all(r.span is not None and a.raw[r.span[0]:r.span[1]] == surf
              for r, surf in zip(atoms, ["10[Keep]", "27[Checkpoint]"]))
          and any(r.name == "flow" and r.value == ">" and r.span is not None
                  and a.raw[r.span[0]:r.span[1]] == ">" for r in a.roles),
          f"spans={[r.span for r in a.roles]}")
    check("seed_lossless_raw",
          a.raw == "10[Keep] > 27[Checkpoint]"
          and a.seed is not None and a.seed.as_mandel() == a.raw,
          f"raw={a.raw!r}")

    a = admit("10[Keep] > banana")
    check("seed_ambiguous_delimiter_rejected",
          a.verdict == "rejected" and a.reason == "seed_parse_refusal"
          and "unexpected" in a.detail,
          f"verdict={a.verdict} reason={a.reason} detail={a.detail!r}")
    a = admit("10[Keep")
    check("seed_fragment_not_english",
          a.verdict == "rejected" and a.kind == "seed"
          and a.reason == "seed_parse_refusal",
          f"verdict={a.verdict} kind={a.kind} reason={a.reason}")
    a = admit('47[Embed](path=)')
    check("seed_missing_field_rejected",
          a.verdict == "rejected" and a.reason == "seed_parse_refusal",
          f"verdict={a.verdict} reason={a.reason} detail={a.detail!r}")
    a = admit('47[Embed](path="a=b") > 10[Keep]')
    arg_roles = [r for r in a.roles if r.name == "arg:path"]
    check("seed_toam_arg_typed",
          a.verdict == "admitted" and len(arg_roles) == 1
          and arg_roles[0].value == "a=b" and arg_roles[0].type == "str"
          and arg_roles[0].span is not None
          and a.raw[arg_roles[0].span[0]:arg_roles[0].span[1]] == 'path="a=b"',
          f"arg_roles={[(r.value, r.type, r.span) for r in arg_roles]}")
    a = admit(r"10[Keep] :: label with \] bracket")
    lab = [r for r in a.roles if r.name == "label"]
    check("seed_label_escape_lossless",
          a.verdict == "admitted" and len(lab) == 1
          and lab[0].value == r"label with \] bracket",
          f"label={[(r.value,) for r in lab]}")
    a = admit("151[Harmonic]")
    atoms = [r for r in a.roles if r.name == "atom"]
    check("seed_reserved_151_form_admitted",
          a.verdict == "admitted" and len(atoms) == 1
          and atoms[0].value["dell"] == 151
          and atoms[0].value["term"] == "Harmonic",
          f"atoms={[(r.value,) for r in atoms]} (form admission only; "
          "DC-8 execution refusal is the executor's, not claimed here)")

    cell = "gpe08_macro_probe"
    try:
        define_cell(cell, "10[Keep] > 27[Checkpoint]")
        a = admit(f"55[Chain] :: {cell}")
        lab = [r for r in a.roles if r.name == "label"]
        exp = expand_cell(cell)
        check("seed_macro_label_agreement",
              a.verdict == "admitted" and len(lab) == 1
              and lab[0].value == cell
              and [at.dell for at in exp.atoms] == [10, 27],
              f"label={[(r.value,) for r in lab]} "
              f"expanded={[at.dell for at in exp.atoms]}")
    finally:
        CELLS.pop(cell, None)

    # ---------------- English door ----------------
    a = admit("cycle three times")
    cnt = [r for r in a.roles if r.name == "arg:count"]
    check("eng_word_count_typed_span",
          a.verdict == "admitted" and a.kind == "english"
          and len(cnt) == 1 and cnt[0].value == 3 and cnt[0].type == "int"
          and cnt[0].provenance == "literal" and cnt[0].span is not None
          and a.raw[cnt[0].span[0]:cnt[0].span[1]] == "three",
          f"count={[(r.value, r.type, r.provenance, r.span) for r in cnt]}")
    a2 = admit("cycle 3")
    cnt2 = [r for r in a2.roles if r.name == "arg:count"]
    check("eng_digit_count_same_ast",
          len(cnt2) == 1 and cnt2[0].value == 3 and cnt2[0].type == "int"
          and cnt2[0].span is not None
          and a2.raw[cnt2[0].span[0]:cnt2[0].span[1]] == "3",
          f"count={[(r.value, r.span) for r in cnt2]}")
    a = admit("cycle")
    cnt = [r for r in a.roles if r.name == "arg:count"]
    check("eng_default_disclosed",
          a.verdict == "admitted" and len(cnt) == 1 and cnt[0].value == 1
          and cnt[0].provenance == "default" and cnt[0].span is None,
          f"count={[(r.value, r.provenance, r.span) for r in cnt]} "
          "(Class E: the door default is disclosed in the AST, never silent)")
    a = admit("walk forward three")
    stp = [r for r in a.roles if r.name == "arg:steps"]
    check("eng_steps_typed",
          a.verdict == "admitted" and len(stp) == 1
          and stp[0].value == 3 and stp[0].type == "int",
          f"steps={[(r.value, r.type) for r in stp]}")
    a = admit("flibberty gibbet snarp")
    check("eng_no_intent_rejected",
          a.verdict == "rejected" and a.reason == "no_intent",
          f"verdict={a.verdict} reason={a.reason}")
    a = admit("delete the thing if it rains")
    check("eng_semantic_loss_guard_rejected",
          a.verdict == "rejected" and a.reason == "no_intent",
          f"verdict={a.verdict} reason={a.reason}")
    a = admit("   ")
    check("eng_empty_rejected",
          a.verdict == "rejected" and a.reason == "nothing_to_translate"
          and a.kind == "empty",
          f"verdict={a.verdict} reason={a.reason} kind={a.kind}")
    a = admit("save this then show the map")
    op = [r for r in a.roles if r.name == "operand"]
    check("eng_sequence_mode",
          a.verdict == "admitted" and a.mode == "sequence"
          and len(op) == 1 and op[0].value == "10[Keep] > 09[Show]",
          f"mode={a.mode} operand={[(r.value,) for r in op]}")

    # Mis-typed role guard, exercised at the layer's own seam: a
    # hand-built Intent whose count arrives as text must be refused
    # before any caller can route it.
    bad = _from_intent(
        Intent("cycle", 6, "Cycle", {"count": "three"}, "06[Cycle] :: 3",
               "cycle three times"),
        "cycle three times", "english")
    check("eng_mistyped_role_rejected",
          bad.verdict == "rejected" and bad.reason == "mistyped_role:count",
          f"verdict={bad.verdict} reason={bad.reason}")

    # Route agreement + rejection-before-mutation, isolated owners.
    p = Program(owner="GPE08ROUTE")
    before = len(getattr(p, "ideas", []) or [])
    a = admit("grow three")
    cyc = [r for r in a.roles if r.name == "arg:cycles"]
    r = route_intent(p, a.intent, "grow three") if a.intent else None
    check("eng_route_agreement",
          a.verdict == "admitted" and len(cyc) == 1 and cyc[0].value == 3
          and r is not None and r.ok and r.seed == "13[Loop] :: 3",
          f"cycles={[(x.value,) for x in cyc]} "
          f"route_ok={None if r is None else r.ok} "
          f"seed={None if r is None else r.seed!r}")
    p2 = Program(owner="GPE08REFUSE")
    before2 = len(getattr(p2, "ideas", []) or [])
    rejected_all = True
    for text in ("10[Keep] > banana", "flibberty gibbet snarp",
                 "delete the thing if it rains", "la zzqq"):
        ax = admit(text)
        if ax.verdict == "admitted" and ax.intent is not None:
            route_intent(p2, ax.intent, text)  # caller contract: admitted only
            rejected_all = False
    after2 = len(getattr(p2, "ideas", []) or [])
    check("eng_rejection_before_mutation",
          rejected_all and after2 == before2,
          f"ideas {before2} -> {after2} across 4 rejected admissions")
    _ = before  # route-agreement program is evidence, not asserted on count

    # ---------------- LatinMandell door ----------------
    a = admit("la serva")
    op = [r for r in a.roles if r.name == "operand"]
    check("lm_admitted",
          a.verdict == "admitted" and a.kind == "latinmandell"
          and a.intent is not None and a.intent.action == "save"
          and len(op) == 1 and op[0].value == "10[Keep]",
          f"verdict={a.verdict} kind={a.kind} "
          f"action={None if a.intent is None else a.intent.action} "
          f"operand={[(r.value,) for r in op]}")
    a = admit("la zzqq")
    check("lm_unresolved_rejected",
          a.verdict == "rejected" and a.reason == "unresolved_latinmandell",
          f"verdict={a.verdict} reason={a.reason}")

    passed = sum(1 for _, ok in CHECKS if ok)
    print(f"GP-E08 admission: {passed}/{len(CHECKS)} checks passed")
    if passed != len(CHECKS):
        raise AssertionError(
            f"GP-E08: {len(CHECKS) - passed} check(s) failed: "
            + ", ".join(n for n, ok in CHECKS if not ok))


def smoke() -> bool:
    try:
        run_all()
        return True
    except Exception as e:
        print(f"GP-E08 SMOKE FAILED: {e}")
        return False


if __name__ == "__main__":
    run_all()
