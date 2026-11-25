#!/usr/bin/env python3
"""D1-TYPED-52-53 — typed arguments for Dell 52 (Filter) and
Dell 53 (Scope), Director wake review 2026-11-03.

Defect (failing-first, probe in the circuit evidence dir):
chain_exec lowers typed args only for Dells with a registered
signature; 52/53 had none, so 52[Filter](predicate="garden")
executed on the legacy payload with ok=True and the argument
silently dropped — selection un-narrowed, bogus roles silently
accepted, typed Scope to a missing group silently accepted
instead of the handler's fail-closed scope_unknown refusal.

Contracts (derived from the handlers, not Dell names):
- Filter (query_ops n==52): one OPTIONAL string role
  `predicate`; the handler consumes the whole label via the
  shared predicate engine; empty label = identity filter.
- Scope (core_ii_exec n==53): one OPTIONAL string role `name`;
  name = label or "plane"; "plane" or an existing group
  switches the scope; anything else refuses scope_unknown
  BEFORE mutation (R1 fail-closed).
Both roles are whole-label: lowering to the label is lossless
(no handler re-splits it), so transport = signature
registration + lower_args_to_lab, zero handler changes —
unlike Dell 55 (DAF-01), whose legacy path re-splits on "=".

Gate law inherited from every typed Dell (chain_exec):
validated args lower to a label; a differing non-empty legacy
label refuses ARGUMENT_CONFLICT before mutation; an equal
label proceeds; unknown roles refuse UNKNOWN_ROLE with zero
mutation; duplicate roles refuse at parse (DAF-07).

Labels: seed execution PUBLIC_ENTRY_PATH (execute_seed on a
real Program). Setup places units directly (p.place).
"""
from __future__ import annotations

import glob
import os
import shutil

RESULTS = []

STATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "state")

TYPED_17 = [8, 51, 52, 53, 54, 55, 56, 57, 58, 67, 68, 69,
            84, 85, 86, 87, 88]


def _rec(name, cond, detail=""):
    RESULTS.append((name, bool(cond), str(detail)))


def _cleanup(owner):
    # Loud cleanup (standing law): a swallowed cleanup failure
    # is a defect; exact owner scope only.
    for f in glob.glob(os.path.join(STATE_DIR, f"*{owner}*")):
        try:
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.remove(f)
        except OSError as exc:
            raise RuntimeError(f"cleanup failed for {f}: {exc}")


def _fresh(owner):
    _cleanup(owner)
    from form.open import Program
    return Program(owner)


def _store(p):
    from form.mandell.core_ii_exec import attach
    return attach(p)


def _err_text(r):
    return str(r.get("error", "")) + " | " + " ".join(
        str(m) for m in r.get("messages", []))


def _registry():
    from form.mandell.signatures import get_signature
    s52 = get_signature(52)
    _rec("sig52: Filter registered, one optional string role "
         "'predicate'",
         s52 is not None
         and [(r.name, r.type, r.required) for r in s52.roles]
         == [("predicate", "string", False)],
         f"sig52={s52}")
    s53 = get_signature(53)
    _rec("sig53: Scope registered, one optional string role "
         "'name'",
         s53 is not None
         and [(r.name, r.type, r.required) for r in s53.roles]
         == [("name", "string", False)],
         f"sig53={s53}")
    typed = sorted(n for n in range(100) if get_signature(n))
    _rec("typed set is exactly the 17 (15 prior + 52 + 53)",
         typed == TYPED_17, f"typed={typed}")


def _filter():
    from form.mandell.executor import execute_seed
    owner = "D1T5253F"
    p = _fresh(owner)
    st = _store(p)
    p.place("garden_gate", "Garden Gate")
    p.place("garden_fern", "Garden Fern")
    p.place("river_stone", "River Stone")
    garden = ["garden_gate", "garden_fern"]

    execute_seed(p, "51[Select]")
    all_ids = list(st.selected)
    r = execute_seed(p, '52[Filter](predicate="garden")')
    lr = dict(st.last_result or {})
    _rec("typed Filter narrows the selection by its predicate",
         r.get("ok") and list(st.selected) == garden,
         f"ok={r.get('ok')} selected={st.selected}")
    _rec("typed Filter result cell is honest (source/count/"
         "matched/predicate from the typed value)",
         lr.get("source") == "filter" and lr.get("count") == 2
         and lr.get("matched") is True
         and lr.get("predicate") == "garden",
         f"cell={lr}")
    _rec("typed Filter single-atom receipt is honest",
         r.get("atom_results") == [{"dell": 52, "ok": True,
                                    "error": "", "skipped": False,
                                    "reason": ""}],
         f"atom_results={r.get('atom_results')}")

    execute_seed(p, "51[Select]")
    r = execute_seed(p, '52[Filter](predicate="zzz")')
    lr = dict(st.last_result or {})
    _rec("typed Filter matching nothing empties honestly "
         "(ok=True, matched=False, count=0)",
         r.get("ok") and list(st.selected) == []
         and lr.get("matched") is False and lr.get("count") == 0,
         f"ok={r.get('ok')} selected={st.selected} cell={lr}")

    execute_seed(p, "51[Select]")
    before = list(st.selected)
    r = execute_seed(p, '52[Filter](bogus="x")')
    _rec("typed Filter bogus role refused UNKNOWN_ROLE, "
         "zero mutation",
         not r.get("ok") and "UNKNOWN_ROLE" in _err_text(r)
         and list(st.selected) == before,
         f"ok={r.get('ok')} err={_err_text(r)[:120]}")

    r = execute_seed(p, '52[Filter](predicate="garden") :: stone')
    _rec("typed Filter conflicting legacy label refused "
         "ARGUMENT_CONFLICT before mutation",
         not r.get("ok") and "ARGUMENT_CONFLICT" in _err_text(r)
         and list(st.selected) == before,
         f"ok={r.get('ok')} err={_err_text(r)[:120]}")

    r = execute_seed(p, '52[Filter](predicate="garden") :: garden')
    _rec("typed Filter with equal legacy label proceeds",
         r.get("ok") and list(st.selected) == garden,
         f"ok={r.get('ok')} selected={st.selected}")

    execute_seed(p, "51[Select]")
    r = execute_seed(p, '52[Filter](predicate="")')
    _rec("typed Filter empty predicate is the identity "
         "(legacy empty-label semantics)",
         r.get("ok") and list(st.selected) == all_ids,
         f"ok={r.get('ok')} selected={st.selected}")

    execute_seed(p, "51[Select]")
    r = execute_seed(p, '52[Filter](predicate="garden gate")')
    _rec("typed Filter delimiter value (space) rides whole: "
         "underscore-prefix match, no split",
         r.get("ok") and list(st.selected) == ["garden_gate"],
         f"ok={r.get('ok')} selected={st.selected}")

    execute_seed(p, "51[Select]")
    r = execute_seed(p, '52[Filter](predicate="a=b:c")')
    _rec("typed Filter delimiter value (= and :) rides whole: "
         "honest empty, no split, no error",
         r.get("ok") and list(st.selected) == [],
         f"ok={r.get('ok')} selected={st.selected}")

    r = execute_seed(
        p, '51[Select] >> 52[Filter](predicate="garden") '
           '>> 54[Query]')
    ars = r.get("atom_results") or []
    lr = dict(st.last_result or {})
    _rec("chain: typed Filter mid-chain narrows; receipts for "
         "all three atoms honest; Query sees the narrowed set",
         r.get("ok") and len(ars) == 3
         and [a.get("dell") for a in ars] == [51, 52, 54]
         and all(a.get("ok") for a in ars)
         and lr.get("source") == "query"
         and lr.get("value") == garden and lr.get("count") == 2,
         f"ok={r.get('ok')} ars={ars} cell={lr}")

    # Legacy controls: behavior on the label path is unchanged.
    execute_seed(p, "51[Select]")
    r = execute_seed(p, "52[Filter] :: garden")
    _rec("legacy Filter label still narrows identically",
         r.get("ok") and list(st.selected) == garden,
         f"ok={r.get('ok')} selected={st.selected}")
    execute_seed(p, "51[Select]")
    r = execute_seed(p, "52[Filter]")
    lr = dict(st.last_result or {})
    _rec("legacy Filter bare is identity with predicate '*'",
         r.get("ok") and list(st.selected) == all_ids
         and lr.get("predicate") == "*",
         f"ok={r.get('ok')} selected={st.selected} cell={lr}")
    _cleanup(owner)


def _typed_vs_legacy_twin():
    from form.mandell.executor import execute_seed
    cells = {}
    for owner, seed in (("D1T5253T1", '52[Filter](predicate="garden")'),
                        ("D1T5253T2", "52[Filter] :: garden")):
        p = _fresh(owner)
        st = _store(p)
        p.place("garden_gate", "Garden Gate")
        p.place("river_stone", "River Stone")
        execute_seed(p, "51[Select]")
        r = execute_seed(p, seed)
        cells[owner] = (r.get("ok"), list(st.selected),
                        dict(st.last_result or {}))
        _cleanup(owner)
    _rec("typed Filter result is identical to the legacy-label "
         "twin (same ok, selection, result cell)",
         cells["D1T5253T1"] == cells["D1T5253T2"],
         f"typed={cells['D1T5253T1']} legacy={cells['D1T5253T2']}")


def _scope():
    from form.mandell.executor import execute_seed
    owner = "D1T5253S"
    p = _fresh(owner)
    st = _store(p)
    p.place("garden_gate", "Garden Gate")
    p.place("river_stone", "River Stone")
    execute_seed(p, "51[Select] :: garden")
    execute_seed(p, "82[Group] :: greens")
    execute_seed(p, "51[Select]")

    r = execute_seed(p, '53[Scope](name="greens")')
    _rec("typed Scope switches to an existing group",
         r.get("ok") and st.scope == "greens",
         f"ok={r.get('ok')} scope={st.scope}")
    r = execute_seed(p, "51[Select]")
    _rec("after typed Scope, Select's universe is the group "
         "(scope is a real boundary)",
         r.get("ok") and list(st.selected) == ["garden_gate"],
         f"ok={r.get('ok')} selected={st.selected}")

    r = execute_seed(p, '53[Scope](name="")')
    _rec("typed Scope empty name defaults to 'plane' "
         "(legacy empty-label semantics)",
         r.get("ok") and st.scope == "plane",
         f"ok={r.get('ok')} scope={st.scope}")

    r = execute_seed(p, '53[Scope](name="nope")')
    _rec("typed Scope to a missing group refuses fail-closed "
         "scope_unknown, scope unchanged",
         not r.get("ok") and r.get("error") == "scope_unknown:nope"
         and st.scope == "plane",
         f"ok={r.get('ok')} err={r.get('error')} scope={st.scope}")

    r = execute_seed(p, '53[Scope](bogus="x")')
    _rec("typed Scope bogus role refused UNKNOWN_ROLE, "
         "scope unchanged",
         not r.get("ok") and "UNKNOWN_ROLE" in _err_text(r)
         and st.scope == "plane",
         f"ok={r.get('ok')} err={_err_text(r)[:120]}")

    r = execute_seed(p, '53[Scope](name="greens") :: plane')
    _rec("typed Scope conflicting legacy label refused "
         "ARGUMENT_CONFLICT, scope unchanged",
         not r.get("ok") and "ARGUMENT_CONFLICT" in _err_text(r)
         and st.scope == "plane",
         f"ok={r.get('ok')} err={_err_text(r)[:120]}")

    r = execute_seed(p, '53[Scope](name="greens") >> 51[Select]')
    ars = r.get("atom_results") or []
    _rec("chain: typed Scope then Select — receipts honest, "
         "selection scope-bound",
         r.get("ok") and len(ars) == 2
         and [a.get("dell") for a in ars] == [53, 51]
         and all(a.get("ok") for a in ars)
         and list(st.selected) == ["garden_gate"],
         f"ok={r.get('ok')} ars={ars} selected={st.selected}")

    execute_seed(p, "53[Scope]")
    r = execute_seed(p, '53[Scope](name="nope") >> 51[Select]')
    ars = r.get("atom_results") or []
    _rec("chain: refused typed Scope carries an honest "
         "ok=False receipt naming scope_unknown",
         len(ars) >= 1 and ars[0].get("dell") == 53
         and ars[0].get("ok") is False
         and "scope_unknown:nope" in str(ars[0].get("error", ""))
         and st.scope == "plane",
         f"ars={ars} scope={st.scope}")

    # Legacy controls.
    r = execute_seed(p, "53[Scope] :: greens")
    _rec("legacy Scope label still switches",
         r.get("ok") and st.scope == "greens",
         f"ok={r.get('ok')} scope={st.scope}")
    r = execute_seed(p, "53[Scope] :: nope")
    _rec("legacy Scope missing group still refuses fail-closed",
         not r.get("ok") and r.get("error") == "scope_unknown:nope"
         and st.scope == "greens",
         f"ok={r.get('ok')} err={r.get('error')} scope={st.scope}")
    r = execute_seed(p, "53[Scope]")
    _rec("legacy Scope bare still defaults to 'plane'",
         r.get("ok") and st.scope == "plane",
         f"ok={r.get('ok')} scope={st.scope}")
    _cleanup(owner)


def main() -> bool:
    _registry()
    _filter()
    _typed_vs_legacy_twin()
    _scope()
    total = len(RESULTS)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        if not ok:
            print(f"FAIL {name} :: {detail}")
    print(f"D1_TYPED_52_53: {passed}/{total}")
    return passed == total


def smoke() -> bool:
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
