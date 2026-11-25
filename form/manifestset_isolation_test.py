#!/usr/bin/env python3
"""72-26 — ManifestSet member isolation (evidence circuit).

Acceptance (register): "One member's failure cannot mutate
sibling definitions or the set's receipt accounting."

A ManifestSet atom (label members separated by the bullet
U+2022, form/mandell/seed.py) expands into one atom per
member; each member is judged on its own at its own
re-entry. Prior coverage proves the per-member ARG GATE
(core_i_arg_gate_test, d1_unsupported_arg_gate_test) and
one Replace case (af1_chain_args_test). This suite proves
EXECUTION-TIME isolation at the public entry path:

- A mixed Delete set: the missing member fails alone with
  its own error; BOTH sibling deletions commit (a member
  failure neither blocks nor rolls back its siblings);
  receipts are one per member, in member order.
- An all-fail set: every member carries its OWN error;
  the chain error is the last member's (the standing
  last-leaf summary contract, 72-19/72-20).
- A mixed Patch set (second Dell family): same shape.
- A shared-args Replace chainlink: the rename commits
  exactly once; the second member honestly fails
  replace_missing:<arg>; reversed member order yields the
  same single rename, with receipts interleaved
  member-major across the linked atoms.
- Inside a Sequence frame, a member failure is an
  executed failure (Join: join_fail) while later members
  still run; inside an unchosen Branch arm, EVERY member
  is skipped and nothing mutates.
- Receipt accounting: chain_ran holds one entry per
  member; partial is True exactly for the mixed case.

Create sets are accounting-checked only: no honest
per-member failure mode exists for Create (duplicate
members do not refuse), so no failure case is claimed
for it.

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


def _prog(tag):
    from form.open import Program
    from form.mandell.core_ii_exec import attach
    p = Program(owner=f"T7226{tag}{RUN}")
    attach(p)
    return p


def _run(p, chain):
    from form.mandell.executor import execute_seed
    return execute_seed(p, chain)


def _recs(out, dell=None):
    rs = out.get("atom_results", [])
    if dell is not None:
        rs = [r for r in rs if r.get("dell") == dell]
    return [(r.get("ok"), r.get("error") or None,
             bool(r.get("skipped"))) for r in rs]


def _cleanup(tag):
    from form.persist import _STATE_DIR, _safe_owner
    from form.dell_matrix.nursery import owner_nursery_path
    owner = f"T7226{tag}{RUN}"
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
    # -- A: mixed Delete set -------------------------------------------
    tag = "A"; TAGS.append(tag)
    p = _prog(tag)
    st = p.core_ii
    _run(p, "55[Set] :: Alpha=1 > 55[Set] :: Gamma=1")
    out = _run(p, "86[Alpha • Beta • Gamma]")
    check("A1.mixed_delete_receipts_per_member_in_order",
          _recs(out, 86) == [(True, None, False),
                             (False, "delete_missing:Beta", False),
                             (True, None, False)],
          f"{_recs(out, 86)}")
    check("A2.sibling_deletions_commit_despite_member_failure",
          dict(st.store) == {}, f"store={dict(st.store)}")
    check("A3.chain_error_is_the_failing_member",
          out["ok"] is False and out["error"] == "delete_missing:Beta",
          f"ok={out['ok']} err={out['error']!r}")
    check("A4.accounting_ran_per_member_partial_true",
          out.get("chain_ran") == [86, 86, 86]
          and out["partial"] is True,
          f"ran={out.get('chain_ran')} partial={out['partial']}")

    # -- B: all-fail Delete set ----------------------------------------
    tag = "B"; TAGS.append(tag)
    p = _prog(tag)
    st = p.core_ii
    out = _run(p, "86[X • Y]")
    check("B1.all_fail_each_member_own_error",
          _recs(out, 86) == [(False, "delete_missing:X", False),
                             (False, "delete_missing:Y", False)],
          f"{_recs(out, 86)}")
    check("B2.all_fail_chain_error_last_partial_false",
          out["ok"] is False and out["error"] == "delete_missing:Y"
          and out["partial"] is False and dict(st.store) == {},
          f"err={out['error']!r} partial={out['partial']}")

    # -- C: mixed Patch set --------------------------------------------
    tag = "C"; TAGS.append(tag)
    p = _prog(tag)
    st = p.core_ii
    _run(p, "55[Set] :: Alpha=1")
    out = _run(p, "88[Alpha • Beta]")
    check("C1.mixed_patch_receipts",
          _recs(out, 88) == [(True, None, False),
                             (False, "patch_miss:Beta", False)]
          and out["error"] == "patch_miss:Beta",
          f"{_recs(out, 88)} err={out['error']!r}")
    check("C2.sibling_patch_commits",
          dict(st.store) == {"Alpha": ""}, f"store={dict(st.store)}")

    # -- D: Replace chainlink, both member orders ----------------------
    tag = "D"; TAGS.append(tag)
    p = _prog(tag)
    st = p.core_ii
    _run(p, "55[Set] :: data=real")
    out = _run(p, '87[A • B](old="data", new="fresh") > 51[C • D]')
    r87 = _recs(out, 87)
    check("D1.replace_renames_once_second_member_fails",
          dict(st.store) == {"fresh": "real"}
          and sorted(r[0] for r in r87) == [False, True]
          and [r[1] for r in r87 if not r[0]] == ["replace_missing:data"],
          f"store={dict(st.store)} r87={r87}")
    check("D2.replace_chain_error_names_arg",
          out["ok"] is False and out["error"] == "replace_missing:data",
          f"err={out['error']!r}")

    tag = "E"; TAGS.append(tag)
    p = _prog(tag)
    st = p.core_ii
    _run(p, "55[Set] :: data=real")
    out = _run(p, '87[B • A](old="data", new="fresh") > 51[C • D]')
    seq = [(r.get("dell"), r.get("ok"), r.get("error") or None)
           for r in out.get("atom_results", [])]
    check("E1.reversed_order_receipts_member_major",
          seq == [(87, True, None), (51, True, None),
                  (87, False, "replace_missing:data"),
                  (51, True, None)],
          f"{seq}")
    check("E2.reversed_order_same_single_rename",
          dict(st.store) == {"fresh": "real"}
          and out["error"] == "replace_missing:data",
          f"store={dict(st.store)} err={out['error']!r}")

    # -- F: set inside frames ------------------------------------------
    tag = "F"; TAGS.append(tag)
    p = _prog(tag)
    st = p.core_ii
    _run(p, "55[Set] :: Alpha=1 > 55[Set] :: Gamma=1")
    out = _run(p, "63[Sequence] > 86[Alpha • Beta • Gamma] "
                  "> 55[Set] :: after=1 > 61[Join]")
    check("F1.sequence_member_failure_join_fail_later_runs",
          _recs(out, 86) == [(True, None, False),
                             (False, "delete_missing:Beta", False),
                             (True, None, False)]
          and _recs(out, 61) == [(False, "join_fail", False)],
          f"r86={_recs(out, 86)} r61={_recs(out, 61)}")
    check("F2.sequence_store_siblings_and_later_member",
          dict(st.store) == {"after": "1"}, f"store={dict(st.store)}")

    tag = "G"; TAGS.append(tag)
    p = _prog(tag)
    st = p.core_ii
    _run(p, "55[Set] :: Alpha=1")
    out = _run(p, "60[false] > 86[Alpha • Beta] > 59[Else] "
                  "> 55[Set] :: vis=1 > 61[Join]")
    check("G1.unchosen_arm_every_member_skipped",
          _recs(out, 86) == [(False, None, True), (False, None, True)]
          and out["ok"] is True,
          f"{_recs(out, 86)} ok={out['ok']}")
    check("G2.unchosen_arm_zero_mutation",
          dict(st.store) == {"Alpha": "1", "vis": "1"},
          f"store={dict(st.store)}")

    # -- H: Create set accounting (no honest failure mode) -------------
    tag = "H"; TAGS.append(tag)
    p = _prog(tag)
    out = _run(p, "08[One • Two • Three]")
    check("H1.create_set_accounting",
          _recs(out, 8) == [(True, None, False)] * 3
          and out.get("chain_ran") == [8, 8, 8]
          and out["ok"] is True and out["partial"] is False,
          f"{_recs(out, 8)} ran={out.get('chain_ran')}")

    for t in TAGS:
        _cleanup(t)
    check("cleanup.no_errors", not _CLEANUP_ERRORS, str(_CLEANUP_ERRORS))

    total = len(RESULTS)
    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"manifestset_isolation_test: {passed}/{total} PASS")
    return 0 if passed == total else 1


def smoke():
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
