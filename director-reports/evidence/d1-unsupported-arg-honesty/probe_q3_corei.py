#!/usr/bin/env python3
"""Q3 — Core I leaf path: typed arguments on Dells 00-50.

Branches covered: (a) parse (shared grammar), (b) single-atom leaf
dispatch in executor_leaf.py, (c) the front-door core_i_ops
intercept (HANDLED = 27/28/34/35/37/40/44/47), (d) chain path,
where chain_exec AF-1 re-emits args into a leaf re-execution.
Dell 8[Create] is the ONLY Core I Dell with a signature.
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
    owner = "ArgHonQ3" + tag
    try:
        fn(owner)
    finally:
        removed = cleanup(owner, before)
        print(f"  (cleanup {owner}: {len(removed)} entries removed)")


def units(p):
    return p.cube.session.plane.units


def p0(_owner):
    s = parse_seed('03[Logic](bogus="x")')
    print(f"parse 03[Logic](bogus=x) -> ok={s.ok} args={s.atoms[0].args}")
    results.append(verdict("Q3-parse",
                           s.ok and s.atoms[0].args == {"bogus": "x"},
                           "Core I atoms PARSE typed args (shared grammar); "
                           "the question is purely what execution does"))


def l1(owner):
    p = fresh(owner)
    bare = execute_seed(p, "03[Logic]")
    p2 = fresh(owner + "B")
    typed = execute_seed(p2, '03[Logic](bogus="x")')
    strip = lambda r: [m for m in r["messages"]
                       if not m.startswith(("Mandell:", "English:"))]
    print(f"bare ok={bare.get('ok')}; typed ok={typed.get('ok')} "
          f"same_body={strip(bare) == strip(typed)}")
    results.append(verdict("Q3-leaf-ignore",
                           bare.get("ok") and typed.get("ok")
                           and strip(bare) == strip(typed),
                           "single-atom leaf: args on an unvalidated Core I "
                           "Dell are silently ignored (identical body)"))


def l2(owner):
    p = fresh(owner)
    r = execute_seed(p, '05[Tone](bogus="x") :: joy')
    tone = [m for m in r["messages"] if "tone=" in m]
    print(f"05[Tone](bogus=x) :: joy -> ok={r.get('ok')} tone_msgs={tone}")
    results.append(verdict("Q3-leaf-label-drives",
                           r.get("ok") and any("tone=joy" in m for m in tone),
                           "the LABEL drives execution; the typed arg is "
                           "never consulted"))


def l3(owner):
    p = fresh(owner)
    r = execute_seed(p, '08[Create](bogus="x")')
    print(f"08[Create](bogus=x) -> ok={r.get('ok')} error={r.get('error')!r} "
          f"units={list(units(p))}")
    results.append(verdict("Q3-create-unknown-role",
                           not r.get("ok")
                           and str(r.get("error")).startswith("MISSING_REQUIRED")
                           and set(units(p)) == {"welcome"},
                           "Dell 8 is the exception: its leaf TOAM block "
                           "validates and refuses before mutation (surfaced "
                           "error is MISSING_REQUIRED — same validate() "
                           "precedence as the chain gate)"))
    r2 = execute_seed(p, '08[Create](name="named", bogus="y")')
    print(f"08[Create](name=named, bogus=y) -> ok={r2.get('ok')} "
          f"error={r2.get('error')!r} units={list(units(p))}")
    results.append(verdict("Q3-create-unknown-role-surfaced",
                           not r2.get("ok")
                           and str(r2.get("error")).startswith("UNKNOWN_ROLE")
                           and set(units(p)) == {"welcome"},
                           "with the required role present, the unknown "
                           "role surfaces as UNKNOWN_ROLE, still zero "
                           "mutation"))


def l4(owner):
    p = fresh(owner)
    r = execute_seed(p, '08[Create](name="typed garden", skin="SPHERE")')
    us = units(p)
    skin = us["typed_garden"].skin.value if "typed_garden" in us else None
    r2 = execute_seed(p, '08[Create](name="bad skin", skin="BANANA")')
    print(f"create typed -> ok={r.get('ok')} units={list(us)} skin={skin}; "
          f"bad skin -> ok={r2.get('ok')} error={r2.get('error')!r} "
          f"units={list(units(p))}")
    results.append(verdict("Q3-create-enum",
                           r.get("ok") and skin == "sphere"
                           and not r2.get("ok")
                           and "INVALID_VALUE" in str(r2.get("error"))
                           and "bad_skin" not in units(p),
                           "typed name+skin wire through; a non-enum skin "
                           "refuses INVALID_VALUE with no unit created — "
                           "the only wrong-value-type refusal in Core I"))


def l5(owner):
    p = fresh(owner)
    r = execute_seed(p, '08[Create](name="alpha") :: beta')
    print(f"08[Create](name=alpha) :: beta -> ok={r.get('ok')} "
          f"error={r.get('error')!r} units={list(units(p))}")
    results.append(verdict("Q3-create-conflict",
                           not r.get("ok")
                           and r.get("error") == "ARGUMENT_CONFLICT"
                           and set(units(p)) == {"welcome"},
                           "typed name vs a differing legacy label refuses "
                           "ARGUMENT_CONFLICT (leaf variant of the law)"))


def h1(owner):
    p = fresh(owner)
    r = execute_seed(p, '27[Checkpoint](bogus="x")')
    p2 = fresh(owner + "B")
    r2 = execute_seed(p2, "27[Checkpoint]")
    print(f"27 typed -> ok={r.get('ok')} gen={r.get('generation_id')!r}; "
          f"27 bare -> ok={r2.get('ok')} gen={r2.get('generation_id')!r}")
    results.append(verdict("Q3-coreiops-ignore",
                           r.get("ok") and r2.get("ok")
                           and r.get("generation_id") and r2.get("generation_id"),
                           "front-door core_i_ops intercept: apply_core_i "
                           "reads seed.label only — args silently ignored "
                           "for HANDLED Dells (27/28/34/35/37/40/44/47)"))


def h2(owner):
    p = fresh(owner)
    a = execute_seed(p, '34[Stamp](bogus="x") :: mark1')
    p2 = fresh(owner + "B")
    b = execute_seed(p2, "34[Stamp] :: mark1")
    print(f"34 typed -> ok={a.get('ok')} err={a.get('error')!r}; "
          f"34 bare -> ok={b.get('ok')} err={b.get('error')!r}")
    results.append(verdict("Q3-stamp-ignore",
                           a.get("ok") == b.get("ok")
                           and a.get("error") == b.get("error"),
                           "second HANDLED witness (34[Stamp]): identical "
                           "outcome with and without typed args"))


def ch1(owner):
    p = fresh(owner)
    r = execute_seed(p, '03[Logic](bogus="x") > 55[Set] :: k=v')
    ar = r.get("atom_results") or []
    print(f"chain 03(bogus) > Set -> ok={r.get('ok')} atoms={ar} "
          f"store={snap(p)['store']}")
    results.append(verdict("Q3-chain-ignore",
                           r.get("ok") and ar and ar[0].get("ok")
                           and snap(p)["store"] == {"k": "v"},
                           "chain path AF-1 re-emits the args into the leaf "
                           "re-execution, which ignores them identically"))


def ch2(owner):
    p = fresh(owner)
    r = execute_seed(p, '08[Create](bogus="x") > 55[Set] :: k=v')
    ar = r.get("atom_results") or []
    print(f"chain 08(bogus) > Set -> ok={r.get('ok')} atoms={ar} "
          f"units={list(units(p))} store={snap(p)['store']}")
    results.append(verdict("Q3-chain-create-refusal",
                           not r.get("ok") and len(ar) == 2
                           and not ar[0].get("ok")
                           and str(ar[0].get("error")).startswith("MISSING_REQUIRED")
                           and ar[1].get("ok")
                           and snap(p)["store"] == {"k": "v"}
                           and set(units(p)) == {"welcome"},
                           "chained Dell 8 IS validated (leaf refusal "
                           "surfaces as the atom's ok=False receipt) and "
                           "FlowTo continues to the next atom"))


for tag, fn in [("P0", p0), ("L1", l1), ("L2", l2), ("L3", l3), ("L4", l4),
                ("L5", l5), ("H1", h1), ("H2", h2), ("C1", ch1), ("C2", ch2)]:
    run(tag, fn)

print(f"\nQ3 SUMMARY: {sum(results)}/{len(results)} expectations confirmed")
sys.exit(0 if all(results) else 1)
