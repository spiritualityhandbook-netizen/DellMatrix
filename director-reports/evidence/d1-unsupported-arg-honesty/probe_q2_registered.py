#!/usr/bin/env python3
"""Q2 — Core II REGISTERED Dells: the general validation law.

PUBLIC_ENTRY_PATH (execute_seed) on Dells other than 52/53
(55[Set], 86[Delete], 56[Get]) + a programmatic census of every
registered role type. Questions: unknown roles, missing required
roles, duplicate roles, typed+legacy conflicts — which refuse,
and is refusal before mutation (store snapshot compared)?
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_lib import cleanup, fresh, snap, state_listing, verdict

from form.mandell.executor import execute_seed
from form.mandell.seed import parse_seed

results = []


def run(tag, fn):
    before = state_listing()
    owner = "ArgHonQ2" + tag
    try:
        fn(owner)
    finally:
        removed = cleanup(owner, before)
        print(f"  (cleanup {owner}: {len(removed)} entries removed)")


# --- census: which role types exist at all? ------------------------
def census(_owner):
    from form.mandell.signatures import _SIGNATURES
    total = len(_SIGNATURES)
    core2 = sorted(n for n in _SIGNATURES if 51 <= n <= 99)
    nonstring = [(n, r.name, r.type) for n, sig in _SIGNATURES.items()
                 for r in sig.roles if r.type != "string"]
    print(f"signatures total={total} core_ii={len(core2)} {core2}")
    print(f"non-string roles: {nonstring}")
    results.append(verdict("Q2-census",
                           total == 17 and len(core2) == 16
                           and nonstring == [(8, "skin", "enum")],
                           "17 signatures (16 Core II + Dell 8); the ONLY "
                           "non-string role in the registry is Dell 8's "
                           "enum 'skin' — no Core II role declares "
                           "integer/boolean/enum, so no Core II "
                           "wrong-value-type refusal surface exists"))


def s1(owner):
    p = fresh(owner)
    execute_seed(p, "55[Set] :: a=1")
    before_store = dict(snap(p)["store"])
    r = execute_seed(p, '55[Set](bogus="x")')
    after_store = dict(snap(p)["store"])
    print(f"55[Set](bogus=x) -> ok={r.get('ok')} error={r.get('error')!r} "
          f"store {before_store} -> {after_store}")
    results.append(verdict("Q2-unknown-role-masked",
                           not r.get("ok")
                           and str(r.get("error")).startswith("MISSING_REQUIRED")
                           and before_store == after_store == {"a": "1"},
                           "refusal + zero mutation hold, but the SURFACED "
                           "error is MISSING_REQUIRED: validate() checks "
                           "missing-required before unknown roles and the "
                           "receipt carries errors[0] only"))
    r2 = execute_seed(p, '55[Set](key="a", bogus="x")')
    print(f"55[Set](key=a, bogus=x) -> ok={r2.get('ok')} "
          f"error={r2.get('error')!r} store={snap(p)['store']}")
    results.append(verdict("Q2-unknown-role-surfaced",
                           not r2.get("ok")
                           and str(r2.get("error")).startswith("UNKNOWN_ROLE")
                           and snap(p)["store"] == {"a": "1"},
                           "with required roles present, the unknown role "
                           "surfaces as UNKNOWN_ROLE — error precedence is "
                           "MISSING_REQUIRED > UNKNOWN_ROLE > INVALID_VALUE"))


def s2(owner):
    p = fresh(owner)
    execute_seed(p, "55[Set] :: a=1")
    r = execute_seed(p, '55[Set](value="x")')
    print(f"55[Set](value=x) -> ok={r.get('ok')} error={r.get('error')!r} "
          f"store={snap(p)['store']}")
    results.append(verdict("Q2-missing-required",
                           not r.get("ok")
                           and str(r.get("error")).startswith("MISSING_REQUIRED")
                           and snap(p)["store"] == {"a": "1"},
                           "missing required role refuses MISSING_REQUIRED, "
                           "zero mutation"))


def s3(owner):
    p = fresh(owner)
    execute_seed(p, "55[Set] :: a=1")
    r = execute_seed(p, '55[Set](key="a", key="b")')
    print(f"55[Set](key=a, key=b) -> ok={r.get('ok')} error={r.get('error')!r} "
          f"store={snap(p)['store']}")
    results.append(verdict("Q2-duplicate-role",
                           not r.get("ok")
                           and "duplicate role" in str(r.get("error"))
                           and snap(p)["store"] == {"a": "1"},
                           "duplicate role refuses AT PARSE (DAF-07), "
                           "before any execution"))


def s4(owner):
    p = fresh(owner)
    execute_seed(p, "55[Set] :: a=1")
    r = execute_seed(p, '55[Set](key="a", value="9") :: a=1')
    mid = dict(snap(p)["store"])
    r2 = execute_seed(p, '55[Set](key="a", value="1") :: a=1')
    print(f"conflict -> ok={r.get('ok')} error={r.get('error')!r} store={mid}; "
          f"equal -> ok={r2.get('ok')} store={snap(p)['store']}")
    results.append(verdict("Q2-conflict",
                           not r.get("ok") and r.get("error") == "ARGUMENT_CONFLICT"
                           and mid == {"a": "1"} and r2.get("ok"),
                           "differing typed+legacy refuses ARGUMENT_CONFLICT "
                           "before mutation; identical pair proceeds"))


def s5(owner):
    p = fresh(owner)
    r = execute_seed(p, '86[Delete](key="ghost")')
    print(f"86[Delete](key=ghost) -> ok={r.get('ok')} error={r.get('error')!r}")
    results.append(verdict("Q2-handler-refusal",
                           not r.get("ok")
                           and str(r.get("error")).startswith("delete_missing"),
                           "validation PASSES; the refusal is the handler's "
                           "own (delete_missing) — gate and handler refusals "
                           "are distinguishable in the receipt"))


def s6(owner):
    p = fresh(owner)
    r = execute_seed(p, '56[Get](key="ghost")')
    s = snap(p)
    ar = (r.get("atom_results") or [{}])[0]
    print(f"56[Get](key=ghost) -> ok={r.get('ok')} atom_ok={ar.get('ok')} "
          f"last_result_error={s['last_result'].get('error')!r}")
    results.append(verdict("Q2-get-three-state",
                           r.get("ok") and ar.get("ok")
                           and s["last_result"].get("error") == "missing",
                           "registered + valid args can still yield a soft "
                           "miss inside the result cell with the atom ok=True"))


def s7(_owner):
    bad = parse_seed("55[Set](key=5)")
    good = parse_seed('55[Set](key="5")')
    print(f"parse (key=5) unquoted -> ok={bad.ok} error={bad.error!r}; "
          f"(key=\"5\") quoted -> ok={good.ok}")
    results.append(verdict("Q2-unquoted-value",
                           not bad.ok and good.ok,
                           "an unquoted value never reaches validation: the "
                           "arg grammar carries quoted strings only, anything "
                           "else is a parse refusal"))


for tag, fn in [("C0", census), ("S1", s1), ("S2", s2), ("S3", s3),
                ("S4", s4), ("S5", s5), ("S6", s6), ("S7", s7)]:
    run(tag, fn)

print(f"\nQ2 SUMMARY: {sum(results)}/{len(results)} expectations confirmed")
sys.exit(0 if all(results) else 1)
