#!/usr/bin/env python3
"""D1-TYPED-52-53 failing-first probe (PUBLIC_ENTRY_PATH).

Runs typed-argument seeds through form.mandell.executor.execute_seed
on the UNMODIFIED tree and demonstrates the silent argument loss for
Dell 52[Filter] and Dell 53[Scope]. Exit 0 = defect demonstrated on
every probe; exit 1 = some probe did NOT show the defect (tree may
already be fixed). Legacy controls included: they must behave
correctly in both worlds.
"""
import glob
import os
import shutil
import sys

ROOT = os.environ.get(
    "DELLMATRIX_ROOT",
    os.path.expanduser("~/workspace/nbd-omega-typed5253"))
sys.path.insert(0, ROOT)
STATE = os.path.join(ROOT, "form", "state")


def cleanup(owner):
    for f in glob.glob(os.path.join(STATE, f"*{owner}*")):
        if os.path.isdir(f):
            shutil.rmtree(f)
        else:
            os.remove(f)


def fresh(owner):
    cleanup(owner)
    from form.open import Program
    return Program(owner)


def store(p):
    from form.mandell.core_ii_exec import attach
    return attach(p)


def main():
    from form.mandell.executor import execute_seed
    defects = []

    # --- Filter (52) ---
    p = fresh("ProbeT5253F")
    st = store(p)
    p.place("garden_gate", "Garden Gate")
    p.place("garden_fern", "Garden Fern")
    p.place("river_stone", "River Stone")
    execute_seed(p, "51[Select]")
    all_ids = list(st.selected)
    r = execute_seed(p, '52[Filter](predicate="garden")')
    narrowed = [i for i in all_ids if "garden" in i]
    print(f"P1 typed Filter: ok={r.get('ok')} selected={st.selected} "
          f"expected_if_typed={narrowed}")
    if r.get("ok") and list(st.selected) == all_ids:
        defects.append("P1 typed Filter arg silently dropped "
                       "(ok=True, selection un-narrowed)")
    # legacy control
    execute_seed(p, "51[Select]")
    r = execute_seed(p, "52[Filter] :: garden")
    print(f"P2 legacy Filter: ok={r.get('ok')} selected={st.selected}")
    assert list(st.selected) == narrowed, "legacy control broken!"
    # bogus role
    execute_seed(p, "51[Select]")
    r = execute_seed(p, '52[Filter](bogus="x")')
    print(f"P3 bogus role Filter: ok={r.get('ok')} err={r.get('error')}")
    if r.get("ok"):
        defects.append("P3 bogus role silently executed (ok=True)")
    cleanup("ProbeT5253F")

    # --- Scope (53) ---
    p = fresh("ProbeT5253S")
    st = store(p)
    p.place("garden_gate", "Garden Gate")
    p.place("river_stone", "River Stone")
    execute_seed(p, "51[Select] :: garden")
    execute_seed(p, "82[Group] :: greens")
    execute_seed(p, "51[Select]")
    print(f"P4 setup: groups={list(st.groups)} scope={st.scope}")
    r = execute_seed(p, '53[Scope](name="greens")')
    print(f"P5 typed Scope existing group: ok={r.get('ok')} "
          f"scope={st.scope}")
    if r.get("ok") and st.scope == "plane":
        defects.append("P5 typed Scope arg silently dropped "
                       "(ok=True, scope stayed 'plane')")
    r = execute_seed(p, '53[Scope](name="nope")')
    print(f"P6 typed Scope missing group: ok={r.get('ok')} "
          f"err={r.get('error')} scope={st.scope}")
    if r.get("ok"):
        defects.append("P6 typed Scope to missing group silently "
                       "accepted (ok=True, no scope_unknown refusal)")
    # legacy controls
    r = execute_seed(p, "53[Scope] :: greens")
    print(f"P7 legacy Scope: ok={r.get('ok')} scope={st.scope}")
    assert r.get("ok") and st.scope == "greens", "legacy control broken!"
    r = execute_seed(p, "53[Scope] :: nope")
    print(f"P8 legacy Scope missing: ok={r.get('ok')} err={r.get('error')}")
    assert not r.get("ok") and "scope_unknown:nope" in str(r.get("error")), \
        "legacy fail-closed control broken!"
    cleanup("ProbeT5253S")

    print("---")
    for d in defects:
        print(f"DEFECT CONFIRMED: {d}")
    print(f"DEFECTS DEMONSTRATED: {len(defects)}/4 typed probes "
          f"(legacy controls all correct)")
    return 0 if len(defects) == 4 else 1


if __name__ == "__main__":
    sys.exit(main())
