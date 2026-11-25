#!/usr/bin/env python3
"""72-10 — Seed grammar stress battery (evidence circuit).

Register action: "Full stress battery (nested delimiters,
escaped Unicode, ManifestSet, no-mutation-on-reject) as
one suite — not evidenced." DAF-07 is certified within
its tested grammar scope and af1/af2 pin chainlinks and
delimiters in part; this battery pins the remaining
grammar surface as ONE suite at the public entry path
(probes: hidden_files/72-10_probe.py, 72-10_probe3.py;
grounding: hidden_files/72-10_ground.md):

- Nested delimiters: a label may carry '>' and '=' in
  its data (the store split is first-'=' against the
  longest existing discipline); brackets inside label
  data are stored verbatim; parentheses inside typed-arg
  strings are carried (and the created unit id is
  sanitized). A '::' INSIDE a label is a loud parse
  refusal with zero mutation (AF-2 HT-02).
- Unicode: non-ASCII labels/values and combining marks
  are stored verbatim; a literal backslash-u sequence
  is stored LITERALLY (no escape decoding anywhere in
  the label path); an emoji Create label falls to the
  leaf path and creates the fallback unit 'idea'.
- ManifestSet rejects: every malformed shape refuses
  LOUDLY at parse time, each with a DISTINCT error, and
  with zero receipts and zero mutation — comma
  separator, bullet lookalikes, empty member, nested
  brackets, delimiter characters in a member, and a
  non-ASCII member (the member charset is ASCII-only;
  pinned as observed contract, Q-72-10.1).
- Well-formed sets inside the battery keep the 72-26
  isolation accounting (per-member receipts in order).
- No-mutation-on-reject, scoped exactly: parse-level
  rejects and per-atom gate rejects mutate NOTHING.
  A mid-chain atom failure does NOT roll back earlier
  atoms — that is the established failure-continuation
  semantics (72-19/72-20), pinned here as the scope
  boundary of the register phrase.
- Error precedence: parse errors pre-empt execution
  AND the arg gate (zero receipts); per-atom gate
  errors surface in atom order with the chain error
  equal to the LAST atom's (last-leaf summary, 72-19);
  an unknown composition name carrying typed args
  reports UNSUPPORTED_ARGS — the gate judges before
  existence.

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
B = "•"  # ManifestSet separator


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def _prog(tag):
    from form.open import Program
    from form.mandell.core_ii_exec import attach
    p = Program(owner=f"T7210{tag}{RUN}")
    attach(p)
    return p


def _run(p, chain):
    from form.mandell.executor import execute_seed
    return execute_seed(p, chain)


def _recs(out, dell=None):
    rs = out.get("atom_results", [])
    if dell is not None:
        rs = [r for r in rs if r.get("dell") == dell]
    return [(r.get("ok"), r.get("error") or None) for r in rs]


def _units(p):
    units = p.cube.session.plane.units
    if isinstance(units, dict):
        return sorted(units.keys())
    return sorted(x if isinstance(x, str) else x.id for x in units)


def _snap(p):
    return (dict(p.core_ii.store), _units(p))


def _cleanup(tag):
    from form.persist import _STATE_DIR, _safe_owner
    from form.dell_matrix.nursery import owner_nursery_path
    owner = f"T7210{tag}{RUN}"
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


def main():
    # -- N: nested delimiters -------------------------------------------
    tag = "N"; TAGS.append(tag)
    p = _prog(tag)
    st = p.core_ii
    out = _run(p, "55[Set] :: a>b=c")
    check("N1.label_gt_eq_first_eq_split",
          out["ok"] is True and dict(st.store) == {"a>b": "c"},
          f"store={dict(st.store)}")
    out = _run(p, "55[Set] :: k=v[1]")
    check("N2.brackets_in_label_data_verbatim",
          out["ok"] is True and st.store.get("k") == "v[1]",
          f"store={dict(st.store)}")
    before = _snap(p)
    out = _run(p, "55[Set] :: note=a::b")
    check("N3.colons_in_label_loud_refusal_zero_mutation",
          out["ok"] is False
          and str(out.get("error", "")).startswith("unexpected at")
          and out.get("atom_results", []) == []
          and _snap(p) == before,
          f"err={out.get('error')!r}")
    out = _run(p, "55[Set] :: x=1 > 55[Set] :: y=a>b > 70[Count]")
    check("N4.deep_chain_delimiter_labels",
          out["ok"] is True and st.store.get("y") == "a>b"
          and len(_recs(out)) == 3,
          f"store={dict(st.store)} recs={_recs(out)}")
    out = _run(p, '8[Create](name="x(y)") > 70[Count]')
    check("N5.parens_in_typed_arg_unit_sanitized",
          out["ok"] is True and "x_y" in _units(p),
          f"units={_units(p)}")

    # -- U: unicode -------------------------------------------------------
    tag = "U"; TAGS.append(tag)
    p = _prog(tag)
    st = p.core_ii
    out = _run(p, "55[Set] :: café=☃")
    check("U1.nonascii_label_value_verbatim",
          out["ok"] is True and st.store.get("café") == "☃",
          f"store={dict(st.store)}")
    out = _run(p, "55[Set] :: é=1")
    check("U2.combining_marks_preserved",
          out["ok"] is True and st.store.get("é") == "1",
          f"keys={list(st.store)}")
    out = _run(p, "55[Set] :: k=\\u2603")
    check("U3.backslash_u_stored_literally",
          out["ok"] is True and st.store.get("k") == "\\u2603",
          f"store={dict(st.store)}")
    out = _run(p, "8[Create] :: 🚀")
    check("U4.emoji_create_leaf_fallback_unit",
          out.get("ok") is True and "idea" in _units(p),
          f"units={_units(p)}")

    # -- M: ManifestSet ---------------------------------------------------
    tag = "M"; TAGS.append(tag)
    p = _prog(tag)
    st = p.core_ii
    _run(p, "55[Set] :: Alpha=1 > 55[Set] :: Gamma=1")
    out = _run(p, f"86[Alpha {B} Missing {B} Gamma]")
    check("M1.wellformed_set_isolation_accounting",
          _recs(out, 86) == [(True, None),
                             (False, "delete_missing:Missing"),
                             (True, None)]
          and dict(st.store) == {},
          f"{_recs(out, 86)} store={dict(st.store)}")
    _run(p, "55[Set] :: Alpha=1 > 55[Set] :: Gamma=1")
    rejects = [
        ("M2.comma_separator", "86[Alpha, Gamma]", "• not ,"),
        ("M3.lookalike_middot", "86[Alpha · Gamma]",
         "invalid unicode — ManifestSet separator is •"),
        ("M4.lookalike_operator", "86[Alpha ∙ Gamma]",
         "invalid unicode — ManifestSet separator is •"),
        ("M5.empty_member", f"86[Alpha {B}  {B} Gamma]",
         "empty member"),
        ("M6.nested_brackets", "86[Alpha [Beta]]",
         "aggregate Dell conflict — use explicit atom form"),
        ("M7.member_delim_chars", f"86[A=B {B} C>D]",
         "invalid manifest member 'A=B'"),
        ("M8.nonascii_member", f"08[One {B} Twø {B} Three]",
         "invalid manifest member 'Twø'"),
    ]
    for name, seed, err in rejects:
        before = _snap(p)
        out = _run(p, seed)
        check(name,
              out["ok"] is False and out.get("error") == err
              and out.get("atom_results", []) == []
              and _snap(p) == before,
              f"err={out.get('error')!r}")
    out = _run(p, f"08[One {B} Two {B} Three]")
    check("M9.create_set_three_receipts",
          _recs(out, 8) == [(True, None)] * 3
          and all(u in _units(p) for u in ("idea", "idea_1", "idea_2")),
          f"{_recs(out, 8)} units={_units(p)}")

    # -- R: no-mutation-on-reject (scoped) --------------------------------
    tag = "R"; TAGS.append(tag)
    p = _prog(tag)
    st = p.core_ii
    _run(p, "55[Set] :: keep=1")
    before = _snap(p)
    out = _run(p, '86[Delete](bogus="1") :: keep')
    check("R1.gate_reject_mutates_nothing",
          _recs(out) == [(False, "MISSING_REQUIRED: key")]
          and _snap(p) == before,
          f"{_recs(out)} store={dict(st.store)}")
    out = _run(p, ">>> :: ::")
    check("R2.parse_reject_mutates_nothing",
          out["ok"] is False
          and out.get("error") == "flow '>>>' without left atom"
          and out.get("atom_results", []) == []
          and _snap(p) == before,
          f"err={out.get('error')!r}")
    out = _run(p, "55[Set] :: new=2 > 99[Nope] :: x=1")
    check("R3.midchain_failure_no_rollback_scope",
          _recs(out) == [(True, None),
                         (False, "malformed_composition")]
          and st.store.get("new") == "2",
          f"{_recs(out)} store={dict(st.store)}")

    # -- P: error precedence ----------------------------------------------
    tag = "P"; TAGS.append(tag)
    p = _prog(tag)
    out = _run(p, '8[Create](bogus="1") :: ::')
    check("P1.parse_preempts_gate",
          out["ok"] is False
          and out.get("error") == "too many flow operators"
          and out.get("atom_results", []) == [],
          f"err={out.get('error')!r}")
    out = _run(p, '99[Nope](bogus="1") :: x')
    check("P2.gate_before_existence",
          _recs(out) == [(False, "UNSUPPORTED_ARGS: bogus")]
          and out["error"] == "UNSUPPORTED_ARGS: bogus",
          f"{_recs(out)}")
    out = _run(p, '86[Delete](bogus="1") :: k > 87[Patch](bogus="2") :: k')
    check("P3.gate_errors_in_order_chain_error_last",
          _recs(out) == [(False, "MISSING_REQUIRED: key"),
                         (False, "MISSING_REQUIRED: old")]
          and out["error"] == "MISSING_REQUIRED: old",
          f"{_recs(out)} err={out['error']!r}")

    for t in TAGS:
        _cleanup(t)
    check("cleanup.no_errors", not _CLEANUP_ERRORS, str(_CLEANUP_ERRORS))

    total = len(RESULTS)
    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"seed_grammar_stress_test: {passed}/{total} PASS")
    return 0 if passed == total else 1


def smoke():
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
