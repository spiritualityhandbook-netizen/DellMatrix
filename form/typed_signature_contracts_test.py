#!/usr/bin/env python3
"""72-13 — cross-signature error/coercion contract audit for the
17 typed Dells (8, 51-58, 67-69, 84-88) (= SM-17, SM-19).

What was already pinned before this suite: per-Dell deep suites
for 14 of the 17, the 52/53 suite, and the two arg-gate suites.
What was NOT pinned anywhere:
- the shared gate contract (UNKNOWN_ROLE / MISSING_REQUIRED /
  ARGUMENT_CONFLICT, each with ZERO mutation) applied per-Dell
  across all 17 signatures — it was pinned only for Dell 8 and
  Dells 52/53 (plus Dell 84's conflict case);
- Dell 55 (Set), the only typed Dell with no dedicated suite:
  its established coercion contract (legacy no-"=" stores "1";
  an empty key coerces to the literal key "value" on BOTH the
  legacy and typed paths; legacy strips whitespace while typed
  role values are stored exactly; typed key-only stores "") —
  behaviors 1-2 are pinned as intentional legacy contract by
  d1_registry_coreii_a_test, and this suite pins the typed side;
- that Dell 55's canonical signature text DOCUMENTS those
  coercions. At the unrepaired head the signature text is silent
  about all of them: those checks are the failing-first defect
  (documentation drift between the signature record and the
  established contract — no behavior change is asserted).

Labels: seed execution PUBLIC_ENTRY_PATH (execute_seed on a real
Program, isolated owners, loud cleanup).
"""
from __future__ import annotations

import glob
import os
import shutil

RESULTS = []

STATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "state")


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


def _snap(p):
    st = _store(p)
    return (dict(st.store), list(st.selected),
            getattr(st, "scope", None),
            {k: list(v) for k, v in (st.groups or {}).items()})


def _seeded(owner):
    from form.mandell.executor import execute_seed
    p = _fresh(owner)
    execute_seed(p, "55[Set] :: A=hello")
    execute_seed(p, "55[Set] :: B=second")
    execute_seed(p, '08[Create](name="garden gate")')
    execute_seed(p, '08[Create](name="river stone")')
    execute_seed(p, "51[Select]")
    return p


# (dell, term, valid typed seed, missing-required seed or None,
#  conflicting typed+legacy seed)
CASES = [
    (51, "Select", '51[Select](predicate="garden")', None,
     '51[Select](predicate="garden") :: river'),
    (52, "Filter", '52[Filter](predicate="garden")', None,
     '52[Filter](predicate="garden") :: river'),
    (53, "Scope", '53[Scope](name="plane")', None,
     '53[Scope](name="plane") :: other'),
    (54, "Query", '54[Query](predicate="river")', None,
     '54[Query](predicate="river") :: garden'),
    (55, "Set", '55[Set](key="K1", value="v1")', '55[Set](value="v")',
     '55[Set](key="K1", value="v1") :: K2=v2'),
    (56, "Get", '56[Get](key="A")', None,
     '56[Get](key="A") :: B'),
    (57, "Compare", '57[Compare](expression="eq: store:A hello")', None,
     '57[Compare](expression="eq: store:A hello") :: eq: store:B second'),
    (58, "Match", '58[Match](pattern="river")', None,
     '58[Match](pattern="river") :: garden'),
    (67, "Any", '67[Any](predicate="gate")', None,
     '67[Any](predicate="gate") :: river'),
    (68, "All", '68[All](predicate="garden")', None,
     '68[All](predicate="garden") :: river'),
    (69, "None", '69[None](predicate="zzz")', None,
     '69[None](predicate="zzz") :: garden'),
    (84, "Copy", '84[Copy](source="A")', None,
     '84[Copy](source="A") :: B'),
    (85, "Move", '85[Move](source="A", destination="AMoved")',
     '85[Move](destination="D")',
     '85[Move](source="A", destination="AMoved") :: B>C'),
    (86, "Delete", '86[Delete](key="B")', None,
     '86[Delete](key="B") :: A'),
    (87, "Replace", '87[Replace](old="B", new="B2")', '87[Replace](new="X")',
     '87[Replace](old="B", new="B2") :: A>C'),
    (88, "Patch", '88[Patch](key="A", value="v2")', '88[Patch](key="A")',
     '88[Patch](key="A", value="v2") :: B=v3'),
]


def _gate_sweep():
    from form.mandell.executor import execute_seed
    owner = "TS13Gate"
    p = _seeded(owner)
    for n, term, valid, missing, conflict in CASES:
        bogus = valid[:-1] + ', bogus="1")'
        before = _snap(p)
        r = execute_seed(p, bogus)
        _rec(f"{n:02d}[{term}] unknown_role_refuses_zero_mutation",
             (not r.get("ok"))
             and "UNKNOWN_ROLE" in str(r.get("error", ""))
             and _snap(p) == before,
             f"ok={r.get('ok')} err={r.get('error')}")
        if missing:
            before = _snap(p)
            r = execute_seed(p, missing)
            _rec(f"{n:02d}[{term}] missing_required_refuses_zero_mutation",
                 (not r.get("ok"))
                 and "MISSING_REQUIRED" in str(r.get("error", ""))
                 and _snap(p) == before,
                 f"ok={r.get('ok')} err={r.get('error')}")
        p2 = _seeded(owner + "C")
        before = _snap(p2)
        r = execute_seed(p2, conflict)
        _rec(f"{n:02d}[{term}] argument_conflict_refuses_zero_mutation",
             (not r.get("ok"))
             and "ARGUMENT_CONFLICT" in str(r.get("error", ""))
             and _snap(p2) == before,
             f"ok={r.get('ok')} err={r.get('error')}")
        _cleanup(owner + "C")
    _cleanup(owner)


def _dell8_gate():
    from form.mandell.executor import execute_seed
    owner = "TS13D8"
    p = _fresh(owner)
    r = execute_seed(p, '08[Create](name="X", bogus="1")')
    _rec("08[Create] unknown_role_refuses",
         (not r.get("ok")) and "UNKNOWN_ROLE" in str(r.get("error", "")),
         f"ok={r.get('ok')} err={r.get('error')}")
    r = execute_seed(p, '08[Create](skin="SPHERE")')
    _rec("08[Create] missing_required_name_refuses",
         (not r.get("ok"))
         and "MISSING_REQUIRED" in str(r.get("error", "")),
         f"ok={r.get('ok')} err={r.get('error')}")
    r = execute_seed(p, '08[Create](name="Bad Skin", skin="TRIANGLE")')
    _rec("08[Create] enum_invalid_value_refuses",
         (not r.get("ok"))
         and "INVALID_VALUE" in str(r.get("error", "")),
         f"ok={r.get('ok')} err={r.get('error')}")
    _cleanup(owner)


def _dell55_coercions():
    from form.mandell.executor import execute_seed
    owner = "TS13Set"
    p = _fresh(owner)
    st = _store(p)
    execute_seed(p, "55[Set] :: Solo")
    _rec("55 legacy_no_equals_stores_literal_1",
         st.store.get("Solo") == "1", f"Solo={st.store.get('Solo')!r}")
    execute_seed(p, "55[Set] :: Empty=")
    _rec("55 legacy_trailing_equals_stores_empty",
         st.store.get("Empty") == "", f"Empty={st.store.get('Empty')!r}")
    execute_seed(p, "55[Set] ::  Spaced  =  padded  ")
    _rec("55 legacy_strips_key_and_value",
         st.store.get("Spaced") == "padded",
         f"Spaced={st.store.get('Spaced')!r}")
    execute_seed(p, "55[Set] :: =orphan")
    _rec("55 legacy_empty_key_coerces_to_value_key",
         st.store.get("value") == "orphan",
         f"value={st.store.get('value')!r}")
    execute_seed(p, '55[Set](key="TypedSpaced", value="  padded  ")')
    _rec("55 typed_value_stored_exactly_not_stripped",
         st.store.get("TypedSpaced") == "  padded  ",
         f"TypedSpaced={st.store.get('TypedSpaced')!r}")
    execute_seed(p, '55[Set](key="KeyOnly")')
    _rec("55 typed_key_only_stores_empty",
         st.store.get("KeyOnly") == "",
         f"KeyOnly={st.store.get('KeyOnly')!r}")
    execute_seed(p, '55[Set](key="", value="emptykey")')
    _rec("55 typed_empty_key_coerces_to_value_key",
         st.store.get("value") == "emptykey",
         f"value={st.store.get('value')!r}")
    execute_seed(p, "55[Set] :: A=1")
    execute_seed(p, '55[Set](key="A=B", value="2")')
    before = dict(st.store)
    r = execute_seed(p, "55[Set] :: A=B=C")
    _rec("55 legacy_ambiguous_set_refuses_zero_mutation",
         (not r.get("ok")) and r.get("error") == "ambiguous_set"
         and dict(st.store) == before,
         f"ok={r.get('ok')} err={r.get('error')}")
    _cleanup(owner)


def _signature_records():
    from form.mandell.signatures import get_signature
    for n in (8, 51, 52, 53, 54, 55, 56, 57, 58, 67, 68, 69,
              84, 85, 86, 87, 88):
        sig = get_signature(n)
        _rec(f"{n:02d} signature_failures_established_not_unknown",
             sig is not None and sig.failures.strip() != "UNKNOWN",
             f"failures={getattr(sig, 'failures', None)!r}")
    sig = get_signature(55)
    text = (sig.output + " " + sig.failures).lower()
    _rec("55 signature_documents_no_equals_default_1",
         "'1'" in text or '"1"' in text,
         f"output={sig.output!r}")
    _rec("55 signature_documents_empty_key_value_coercion",
         "empty key" in text and '"value"' in text or
         ("empty key" in text and "'value'" in text),
         f"output={sig.output!r}")
    _rec("55 signature_documents_whitespace_asymmetry",
         ("strip" in text or "whitespace" in text) and "typed" in text,
         f"output={sig.output!r}")


def main():
    _gate_sweep()
    _dell8_gate()
    _dell55_coercions()
    _signature_records()
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        print(("PASS " if ok else "FAIL ") + name +
              ("" if ok else " :: " + detail[:200]))
    print(f"typed_signature_contracts: {passed}/{len(RESULTS)}")
    return 0 if passed == len(RESULTS) else 1


def smoke():
    return main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
