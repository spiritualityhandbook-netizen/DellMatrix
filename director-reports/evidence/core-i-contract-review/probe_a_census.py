"""Probe A — single-atom census, Dell 8 battery, intercept deep-dive.

Surfaces: executor.py dispatch — HANDLED -> core_i_ops.apply_core_i,
21/22 -> live_identity, else executor_leaf. Every verdict is
DIFFERENTIAL: typed call vs bare call on identical fresh baselines.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.expanduser("~/workspace/nbd-omega-corei"))
os.chdir(os.path.expanduser("~/workspace/nbd-omega-corei"))

from probe_lib import (EVDIR, cleanup, state_snapshot, witness)  # noqa: E402

from form.open import Program  # noqa: E402
from form.mandell.executor import execute_seed  # noqa: E402
from form.mandell.seed import parse_seed  # noqa: E402
from form.mandell.registry import DELLS  # noqa: E402
from form.mandell.core_i_ops import HANDLED  # noqa: E402

OWNER = "CoreIRev"


def fresh():
    cleanup(OWNER)
    return Program(owner=OWNER)


def surface_of(n):
    if n in HANDLED:
        return "intercept"
    if n in (21, 22):
        return "live_identity"
    return "leaf"


def main():
    base = state_snapshot(exclude_owners=["CoreIRev", "CoreIRepl"])
    with open(os.path.join(EVDIR, "baseline_before.json"), "w") as fh:
        json.dump(base, fh, indent=1, sort_keys=True)
    print(f"BASELINE: {len(base)} non-probe state files hashed")

    # ---------- Section 1: census, all 51 Core I Dells ----------
    print("\n== SECTION 1: single-atom census (bare vs bogus-typed) ==")
    rows = []
    for n in range(0, 51):
        name = DELLS[n]["name"]
        bare_seed = f"{n:02d}[{name}]"
        typed_seed = f'{n:02d}[{name}](bogus="zzprobe")'
        ps = parse_seed(typed_seed)
        parsed = bool(ps.ok and ps.atoms
                      and ps.atoms[0].args == {"bogus": "zzprobe"})
        p = fresh()
        wb = witness(execute_seed(p, bare_seed), p)
        p = fresh()
        wt = witness(execute_seed(p, typed_seed), p)
        same = wb == wt
        if n == 8:
            verdict = "VALIDATED (see battery)" if not same else \
                "!! BARE==TYPED for Dell 8 — exception claim REFUTED"
        else:
            verdict = "IGNORED" if same else "!! DIFFERS"
        row = {"dell": n, "name": name, "surface": surface_of(n),
               "args_parsed": parsed, "bare_ok": wb[0],
               "typed_ok": wt[0], "typed_error": wt[1],
               "verdict": verdict}
        rows.append(row)
        print(f"  {n:02d}[{name:<10}] surf={surface_of(n):<13} "
              f"parsed={parsed} bare_ok={wb[0]} typed_ok={wt[0]} "
              f"-> {verdict}" + ("" if same or n == 8 else
                                 f"  bare={wb} typed={wt}"))
    with open(os.path.join(EVDIR, "census_single.json"), "w") as fh:
        json.dump(rows, fh, indent=1)

    # ---------- Section 2: Dell 8 battery ----------
    print("\n== SECTION 2: Dell 8 [Create] exception battery ==")
    bat = []

    def case(label, seed):
        p = fresh()
        r = execute_seed(p, seed)
        units = witness(r, p)[2]
        bat.append({"case": label, "seed": seed, "ok": r.get("ok"),
                    "error": r.get("error") or ""})
        print(f"  {label:<34} ok={r.get('ok')} "
              f"error={r.get('error') or ''!r}")
        return r, units

    case("valid name+skin", '08[Create](name="Wish One", skin="SPHERE")')
    r, u = case("unknown role", '08[Create](name="Wish One", bogus="x")')
    print(f"    units after unknown-role: {u}")
    case("invalid enum skin", '08[Create](name="Wish One", skin="TRIANGLE")')
    case("missing required name", '08[Create](skin="SPHERE")')
    case("precedence missing+unknown", '08[Create](bogus="x")')
    case("precedence unknown+invalid",
         '08[Create](name="W", skin="TRIANGLE", bogus="x")')
    case("conflict typed vs label",
         '08[Create](name="Wish One") :: other_label')
    case("typed name == label slug",
         '08[Create](name="Wish One") :: wish_one')
    dup = parse_seed('08[Create](name="A", name="B")')
    bat.append({"case": "duplicate role at parse", "ok": dup.ok,
                "error": getattr(dup, "error", "")})
    print(f"  {'duplicate role at parse':<34} parse_ok={dup.ok} "
          f"error={getattr(dup, 'error', '')!r}")
    with open(os.path.join(EVDIR, "dell8_battery.json"), "w") as fh:
        json.dump(bat, fh, indent=1)

    # ---------- Section 3: intercept + live_identity deep-dive ----
    print("\n== SECTION 3: intercept deep-dive (plausible roles) ==")
    deep = []

    def probe(label, setup, seed):
        p = fresh()
        for s in setup:
            execute_seed(p, s)
        r = execute_seed(p, seed)
        w = witness(r, p)
        deep.append({"case": label, "seed": seed, "ok": r.get("ok"),
                     "error": r.get("error") or "",
                     "last_core_i": json.loads(w[2]).get("last_core_i"),
                     "last_stamp": json.loads(w[2]).get("last_stamp"),
                     "last_nurture": json.loads(w[2]).get("last_nurture"),
                     "last_measure": json.loads(w[2]).get("last_measure"),
                     "units": json.loads(w[2]).get("units")})
        print(f"  {label:<44} ok={r.get('ok')} "
              f"error={r.get('error') or ''!r}")
        return r, w

    probe("34 typed mark", [], '34[Stamp](mark="typedmark")')
    r, w = probe("34 typed mark + label", [], '34[Stamp](mark="typedmark") :: labelmark')
    print(f"    last_stamp={json.loads(w[2]).get('last_stamp')}")
    probe("37 typed label, no seed label", [], '37[Nurture](label="typedidea")')
    r, w = probe("37 bogus + seed label", [], '37[Nurture](bogus="x") :: labelidea')
    print(f"    last_nurture={json.loads(w[2]).get('last_nurture')}")
    r, w = probe("44 typed capability", [], '44[Bridge](capability="typedcap")')
    print(f"    last_core_i={json.loads(w[2]).get('last_core_i')}")
    probe("44 bogus + label capability", [], '44[Bridge](bogus="x") :: labelcap')
    r, w = probe("47 typed provider", [], '47[Embed](provider="typedprov")')
    print(f"    last_core_i={json.loads(w[2]).get('last_core_i')}")
    probe("27 typed stamp", [], '27[Checkpoint](stamp="typedstamp")')
    probe("28 typed generation", [], '28[Rollback](generation="gen-x")')
    r, w = probe("40 typed unit", [], '40[TokenCount](unit="tokens")')
    print(f"    last_measure={json.loads(w[2]).get('last_measure')}")
    probe("35 typed query", [], '35[Discover](query="typedq")')
    setup2 = ['08[Create] :: alpha_one', '08[Create] :: beta_two']
    probe("21 bare, no label (setup)", setup2, '21[Merge]')
    probe("21 typed, no label (setup)", setup2, '21[Merge](bogus="x")')
    probe("21 bare + label (setup)", setup2, '21[Merge] :: alpha_one')
    probe("21 typed + label (setup)", setup2, '21[Merge](bogus="x") :: alpha_one')
    probe("22 bare + label (setup)", setup2, '22[Split] :: alpha_one')
    probe("22 typed + label (setup)", setup2, '22[Split](bogus="x") :: alpha_one')
    with open(os.path.join(EVDIR, "intercept_deep.json"), "w") as fh:
        json.dump(deep, fh, indent=1)

    # ---------- Section 4: plausible-role exhibits (leaf) ---------
    print("\n== SECTION 4: plausible-role exhibits (role names a user "
          "would guess — several mirror the English Intent arg names) ==")
    exh = []

    def ex(label, seed):
        p = fresh()
        r = execute_seed(p, seed)
        w = witness(r, p)
        msgs = json.loads(w[3])
        exh.append({"case": label, "seed": seed, "ok": r.get("ok"),
                    "error": r.get("error") or "", "messages": msgs})
        print(f"  {label:<46} ok={r.get('ok')} msgs={msgs[:3]}")
        return r

    ex("05 typed expression=calm, label joy",
       '05[Tone](expression="calm") :: joy')
    ex("05 bare, label joy", '05[Tone] :: joy')
    ex("04 typed direction=left, no label", '04[Transform](direction="left")')
    ex("04 bare, label left", '04[Transform] :: left')
    ex("06 typed cycles=3, no label", '06[Cycle](cycles="3")')
    ex("06 bare, label 3", '06[Cycle] :: 3')
    ex("03 typed bogus + label rule", '03[Logic](bogus="x") :: my rule')
    with open(os.path.join(EVDIR, "plausible_roles.json"), "w") as fh:
        json.dump(exh, fh, indent=1)

    cleanup(OWNER)
    print("\nPROBE A DONE")


if __name__ == "__main__":
    main()
