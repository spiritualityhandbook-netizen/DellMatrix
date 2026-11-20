"""C13 Simulate — Part I failing-first spec (MWL #167 / #170 remainders).

WHY A *_test_spec.py FILE (not a *_test.py): form/regress.py's
intended_entries() = LIST + every discovered form/**/*_test.py;
an unregistered failing suite in the registry path turns CI
smoke RED as an omitted/red entry (failure class proven on
PR #503, smoke run 44758805458). These two checks FAIL on current
main by design — the contracts they assert do not exist yet.
CODE-STAGE STEP ZERO (recorded in the Part I plan): when the
C13 remainder is authorized and built, merge these two checks
into form/c13_simulate_test.py as its t18/t19 (the parent suite
already carries t1-t17) and delete this spec file.

Checks (both EXPECTED TO FAIL on current main):

  t18 (#167) — a Simulate receipt DECLARES its effect inventory:
      the nested Core-II receipt carries an explicit
      effect-inventory key (effects / effect_inventory /
      inventory) naming every state class the run touched
      (chains, compositions, planes, nursery, history). Today the
      receipt exposes raw atom results but no declared inventory.
  t19 (#170) — a named PARALLEL PREVIEW surface exists: an
      executor-level or Program-level symbol whose name carries
      both the parallel and the preview/simulate contract, so a
      caller can request a parallel preview without the serial
      Simulate path. Today no such symbol exists on either layer.

Both checks run the parent suite's own helpers (imported, not
copied) against an ISOLATED owner and clean it up, mirroring the
parent suite's hygiene. Tier: INTEGRATION (in-process dispatch
through the public execute_seed door, same as the parent suite).

Standalone:  python3 form/c13_simulate_part1_test_spec.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from form.c13_simulate_test import _cleanup, _program, _sim  # noqa: E402

RESULTS = []


def rec(name, ok, detail=""):
    RESULTS.append(bool(ok))
    line = f"[{'PASS' if ok else 'FAIL'}] {name}"
    if detail and not ok:
        line += f" | {detail}"[:400]
    print(line)


def main() -> bool:
    p = _program("C13SimT9")
    try:
        # t18 — declared effect inventory in the Simulate receipt.
        r = _sim(p, "31[Simulate]:: 31[Chain]:: Alpha => Beta => Gamma")
        nested = {}
        if isinstance(r, dict):
            prim = r.get("primary")
            if isinstance(prim, dict) and isinstance(prim.get("result"), dict):
                nested = prim["result"]
            elif isinstance(r.get("result"), dict):
                nested = r["result"]
        inv_keys = [k for k in nested
                    if "effect" in k.lower() or "inventor" in k.lower()]
        rec("t18_part1_167_effect_inventory_declared",
            bool(inv_keys),
            f"receipt keys={sorted(r.keys()) if isinstance(r, dict) else type(r)} "
            f"nested={sorted(nested.keys())} inventory/effect keys="
            f"{inv_keys or 'none'}")

        # t19 — named parallel-preview surface on either layer.
        from form.mandell import executor as _ex
        ex_syms = [s for s in dir(_ex)
                   if ("parallel" in s.lower() and "preview" in s.lower())
                   or ("parallel" in s.lower() and "simulat" in s.lower())]
        pg_syms = [s for s in dir(type(p))
                   if ("parallel" in s.lower() and "preview" in s.lower())
                   or ("parallel" in s.lower() and "simulat" in s.lower())]
        rec("t19_part1_170_parallel_preview_surface",
            bool(ex_syms or pg_syms),
            f"executor parallel/preview symbols={ex_syms or 'none'}; "
            f"Program symbols={pg_syms or 'none'}")
    finally:
        _cleanup("C13SimT9")
    print(f"C13 SIMULATE PART1 SPEC: {sum(RESULTS)}/{len(RESULTS)} "
          f"checks passed")
    return all(RESULTS)


def smoke() -> bool:
    try:
        return main()
    except Exception as exc:  # noqa: BLE001
        print(f"C13 SIMULATE PART1 SPEC SMOKE FAILED: {exc!r}")
        return False


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
