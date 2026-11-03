#!/usr/bin/env python3
"""Q1 — Core II chain path: typed arguments on UNTYPED Core II Dells.

PUBLIC_ENTRY_PATH (form.mandell.executor.execute_seed). Twin fresh
programs per case: legacy label form vs typed-argument form.
Expectation under investigation: for Dells with no registered
signature, chain_exec's TOAM gate (chain_exec.py:64-66) inspects
args ONLY when has_signature(n); otherwise execution proceeds on
the legacy payload and the args are silently dropped.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_lib import cleanup, fresh, setup_plane, snap, state_listing, verdict

from form.mandell.executor import execute_seed

results = []


def case(tag, fn):
    before = state_listing()
    owner = "ArgHonQ1" + tag
    try:
        fn(owner)
    finally:
        removed = cleanup(owner, before)
        print(f"  (cleanup {owner}: {len(removed)} entries removed)")


# --- 82[Group] (spectrum_ops): legacy label names the group --------
def g1(owner):
    p = fresh(owner)
    setup_plane(p)
    execute_seed(p, "51[Select]")
    r = execute_seed(p, "82[Group] :: greens")
    s = snap(p)
    print(f"legacy 82[Group] :: greens -> ok={r.get('ok')} groups={list(s['groups'])}")
    results.append(verdict("Q1-82-legacy",
                           r.get("ok") and "greens" in s["groups"],
                           "legacy label creates group 'greens'"))


def g2(owner):
    p = fresh(owner)
    setup_plane(p)
    execute_seed(p, "51[Select]")
    r = execute_seed(p, '82[Group](name="greens")')
    s = snap(p)
    ar = (r.get("atom_results") or [{}])
    print(f"typed single 82[Group](name=greens) -> ok={r.get('ok')} "
          f"groups={list(s['groups'])} atom0={ar[0] if ar else None}")
    results.append(verdict("Q1-82-typed-single",
                           r.get("ok") and "greens" not in s["groups"]
                           and "group" in s["groups"],
                           "typed arg dropped: ok=True, group created under "
                           "the DEFAULT name 'group', not 'greens'"))


def g3(owner):
    p = fresh(owner)
    setup_plane(p)
    execute_seed(p, "51[Select]")
    r = execute_seed(p, '82[Group](bogus="x")')
    s = snap(p)
    print(f"typed bogus 82[Group](bogus=x) -> ok={r.get('ok')} "
          f"error={r.get('error')!r} groups={list(s['groups'])}")
    results.append(verdict("Q1-82-typed-bogus",
                           r.get("ok") and not r.get("error"),
                           "no UNKNOWN_ROLE refusal exists for an untyped "
                           "Dell: bogus role silently accepted"))


def g4(owner):
    p = fresh(owner)
    setup_plane(p)
    execute_seed(p, "51[Select]")
    r = execute_seed(p, '82[Group](name="greens") :: blues')
    s = snap(p)
    print(f"typed+label 82[Group](name=greens) :: blues -> ok={r.get('ok')} "
          f"groups={list(s['groups'])}")
    results.append(verdict("Q1-82-typed-plus-label",
                           r.get("ok") and "blues" in s["groups"]
                           and "greens" not in s["groups"],
                           "legacy label silently WINS over typed args"))


def g5(owner):
    p = fresh(owner)
    setup_plane(p)
    r = execute_seed(p, '51[Select] >> 82[Group](name="greens")')
    s = snap(p)
    ar = r.get("atom_results") or []
    print(f"typed chain 51>>82(name=greens) -> ok={r.get('ok')} "
          f"groups={list(s['groups'])} atom_results={ar}")
    results.append(verdict("Q1-82-typed-chain",
                           r.get("ok") and "group" in s["groups"]
                           and "greens" not in s["groups"],
                           "same silent drop inside a chain; atom receipt "
                           "reports ok=True with no arg mention"))


# --- 97[Define] (spectrum_ops): legacy label is name=meaning -------
def d1(owner):
    p = fresh(owner)
    r = execute_seed(p, "97[Define] :: tempo=120")
    s = snap(p)
    print(f"legacy 97[Define] :: tempo=120 -> ok={r.get('ok')} defs={s['defs']}")
    results.append(verdict("Q1-97-legacy",
                           r.get("ok") and s["defs"].get("tempo") == "120",
                           "legacy label defines tempo=120"))


def d2(owner):
    p = fresh(owner)
    r = execute_seed(p, '97[Define](name="tempo", meaning="120")')
    s = snap(p)
    print(f"typed 97[Define](name=tempo, meaning=120) -> ok={r.get('ok')} defs={s['defs']}")
    results.append(verdict("Q1-97-typed",
                           r.get("ok") and "tempo" not in s["defs"],
                           "typed args dropped: ok=True, definition lands "
                           "under the default name, not 'tempo'"))


# --- 78[Cause] (query_ops): legacy label is a>b relation -----------
def c1(owner):
    p = fresh(owner)
    r = execute_seed(p, "78[Cause] :: rain>flood")
    s = snap(p)
    print(f"legacy 78[Cause] :: rain>flood -> ok={r.get('ok')} causes={s['causes']}")
    results.append(verdict("Q1-78-legacy",
                           r.get("ok") and ("rain", "flood") in s["causes"],
                           "legacy label records the relation"))


def c2(owner):
    p = fresh(owner)
    r = execute_seed(p, '78[Cause](cause="rain", effect="flood")')
    s = snap(p)
    print(f"typed 78[Cause](cause=rain, effect=flood) -> ok={r.get('ok')} "
          f"error={r.get('error')!r} causes={s['causes']}")
    results.append(verdict("Q1-78-typed",
                           not r.get("ok") and r.get("error") == "malformed_relation"
                           and not s["causes"],
                           "args dropped; the handler then fails on the EMPTY "
                           "label with 'malformed_relation' — an error that "
                           "never mentions the supplied arguments"))


# --- Control head 60[Branch] inside a chain ------------------------
def b1(owner):
    p = fresh(owner)
    r = execute_seed(p, '60[Branch](bogus="x") :: true >> 55[Set] :: k=v >> 61[Join]')
    s = snap(p)
    print(f"chain 60[Branch](bogus=x) :: true >> Set >> Join -> ok={r.get('ok')} "
          f"store={s['store']}")
    results.append(verdict("Q1-60-control-head",
                           r.get("ok") and s["store"].get("k") == "v",
                           "control heads share _run_atom: typed args on an "
                           "untyped control head are dropped identically"))


for tag, fn in [("G1", g1), ("G2", g2), ("G3", g3), ("G4", g4), ("G5", g5),
                ("D1", d1), ("D2", d2), ("C1", c1), ("C2", c2), ("B1", b1)]:
    case(tag, fn)

print(f"\nQ1 SUMMARY: {sum(results)}/{len(results)} expectations confirmed")
sys.exit(0 if all(results) else 1)
