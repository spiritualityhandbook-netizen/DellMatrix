"""Probe B — chain path census + single-vs-chain parity table.

Chain form: NN[Name](bogus="zzprobe") > 70[Count]. The Core I atom's
receipt is atom_results[0]. Parity compares (ok, error-class) of the
single-atom typed call vs the chained typed call — the AF-1 shape,
generalized to all 51 Core I Dells.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.expanduser("~/workspace/nbd-omega-corei"))
os.chdir(os.path.expanduser("~/workspace/nbd-omega-corei"))

from probe_lib import EVDIR, cleanup, witness  # noqa: E402

from form.open import Program  # noqa: E402
from form.mandell.executor import execute_seed  # noqa: E402
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


def errclass(e):
    return (e or "").split(":")[0].strip()


def main():
    print("== SECTION 1: chain census + parity (typed, all 51) ==")
    rows = []
    breaks = []
    for n in range(0, 51):
        name = DELLS[n]["name"]
        typed_seed = f'{n:02d}[{name}](bogus="zzprobe")'
        p = fresh()
        rs = execute_seed(p, typed_seed)
        single = (bool(rs.get("ok")), errclass(rs.get("error") or ""))
        p = fresh()
        rc = execute_seed(p, typed_seed + " > 70[Count]")
        ars = rc.get("atom_results") or []
        a0 = ars[0] if ars else {}
        chain = (bool(a0.get("ok")), errclass(a0.get("error") or ""))
        parity = single == chain
        if not parity:
            breaks.append(n)
        rows.append({"dell": n, "name": name,
                     "surface": surface_of(n), "single": single,
                     "chain": chain, "parity": parity})
        print(f"  {n:02d}[{name:<10}] surf={surface_of(n):<13} "
              f"single={single} chain={chain} parity={parity}")
    with open(os.path.join(EVDIR, "census_chain.json"), "w") as fh:
        json.dump(rows, fh, indent=1)
    print(f"  PARITY BREAKS: {breaks if breaks else 'none'}")

    print("\n== SECTION 2: chain witnesses (intercept in chain) ==")
    p = fresh()
    r = execute_seed(p, '34[Stamp](mark="typedmark") > 70[Count]')
    print(f"  34 chain: last_stamp="
          f"{json.dumps(getattr(p, 'last_stamp', None), default=str)}")
    p = fresh()
    r = execute_seed(p, '27[Checkpoint](stamp="typedstamp") > 70[Count]')
    print(f"  27 chain: last_core_i="
          f"{json.dumps(getattr(p, 'last_core_i', None), default=str)}")
    p = fresh()
    r = execute_seed(p, '37[Nurture](label="typedidea") > 70[Count]')
    a0 = (r.get("atom_results") or [{}])[0]
    print(f"  37 chain typed-label-only: atom0 ok={a0.get('ok')} "
          f"error={a0.get('error')!r} (label requirement NOT met "
          f"by the typed arg)")

    print("\n== SECTION 3: Dell 8 chain battery ==")
    for label, seed in [
            ("valid", '08[Create](name="Chain Wish", skin="SPHERE")'
                      ' > 70[Count]'),
            ("invalid skin", '08[Create](name="Chain Wish", '
                             'skin="TRIANGLE") > 70[Count]'),
            ("unknown role", '08[Create](name="Chain Wish", bogus="x")'
                             ' > 70[Count]'),
            ("missing name", '08[Create](skin="SPHERE") > 70[Count]')]:
        p = fresh()
        r = execute_seed(p, seed)
        a0 = (r.get("atom_results") or [{}])[0]
        units = json.loads(witness(r, p)[2]).get("units")
        print(f"  {label:<14} atom0 ok={a0.get('ok')} "
              f"error={a0.get('error')!r} units={units}")

    print("\n== SECTION 4: 21/22 chain differential (setup) ==")
    setup = ['08[Create] :: alpha_one', '08[Create] :: beta_two']
    for dell, term, lab in [(21, "Merge", "alpha_one beta_two"),
                            (22, "Split", "alpha_one")]:
        ws = []
        for typed in (False, True):
            p = fresh()
            for s in setup:
                execute_seed(p, s)
            seed = (f"{dell}[{term}]" + ('(bogus="x")' if typed else "")
                    + f" :: {lab} > 70[Count]")
            r = execute_seed(p, seed)
            ws.append(witness(r, p))
        print(f"  {dell}[{term}] bare==typed in chain: {ws[0] == ws[1]} "
              f"(bare ok={ws[0][0]})")
    cleanup(OWNER)
    print("PROBE B DONE")


if __name__ == "__main__":
    main()
