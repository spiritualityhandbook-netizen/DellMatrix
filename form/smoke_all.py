#!/usr/bin/env python3
"""Unified Form smoke — SUS suite + phrase hit-rate + accept."""

from __future__ import annotations

import sys


def main() -> None:
    results = []

    def run(name, fn):
        print(f"\n--- {name} ---")
        try:
            ok = bool(fn())
        except Exception as e:
            print(f"ERROR: {e}")
            ok = False
        results.append((name, ok))

    from form.dell_matrix.plane import smoke as plane_smoke
    from form.dell_matrix.main_field import smoke as main_smoke
    from form.dell_matrix.resonance import smoke as res_smoke
    from form.dell_matrix.enhance_gate import smoke as enh_smoke
    from form.dell_matrix.blank_cube import smoke as blank_smoke
    from form.dell_matrix.visual import smoke as vis_smoke
    from form.dell_matrix.shared_main import smoke as shared_smoke
    from form.dell_matrix.ambient_gate import smoke as ambient_smoke
    from form.dell_matrix.sandbox_gate import smoke as sandbox_smoke
    from form.dell_matrix.ringed_growth import smoke as ringed_smoke
    from form.dell_matrix.harmonic_lattice import smoke as lattice_smoke
    from form.dell_matrix.perception import smoke as perception_smoke
    from form.dell_matrix.network_main import smoke as net_smoke
    from form.dell_matrix.graph_view import smoke as graph_smoke
    from form.persist import smoke as persist_smoke
    from form.open import smoke as open_smoke
    from form.dual_output import smoke as dual_smoke
    from form.invariants import smoke as inv_smoke

    suite = [
        ("plane", plane_smoke),
        ("main_field", main_smoke),
        ("resonance", res_smoke),
        ("enhance_gate", enh_smoke),
        ("blank_cube", blank_smoke),
        ("visual", vis_smoke),
        ("shared_main", shared_smoke),
        ("ambient_gate", ambient_smoke),
        ("sandbox_gate", sandbox_smoke),
        ("ringed_growth", ringed_smoke),
        ("harmonic_lattice", lattice_smoke),
        ("perception", perception_smoke),
        ("network_main", net_smoke),
        ("graph_view", graph_smoke),
        ("persist_v7", persist_smoke),
        ("open", open_smoke),
        ("dual_output", dual_smoke),
        ("invariants", inv_smoke),
    ]
    for name, fn in suite:
        run(name, fn)

    print("\n--- phrase_hit_rate ---")
    try:
        from form.mandell.phrase_tests import smoke as phrase_smoke
        ok = phrase_smoke()
        results.append(("phrase_hit_rate", ok))
    except Exception as e:
        print("ERROR:", e)
        results.append(("phrase_hit_rate", False))

    print("\n--- verify_required ---")
    try:
        from form.open import open_program
        p = open_program("SUSVerify")
        v = p.matrix.verify()
        ok = v.get("ok") is True and hasattr(p, "lattice") and p.lattice is not None
        if not v.get("ok"):
            print("missing:", v.get("missing"))
        print("PASS" if ok else "FAIL")
        results.append(("verify_required", ok))
    except Exception as e:
        print("ERROR:", e)
        results.append(("verify_required", False))

    print("\n--- acceptance_path ---")
    try:
        from form.accept import run as accept_run
        ok = accept_run()
        results.append(("acceptance_path", ok))
    except Exception as e:
        print("ERROR:", e)
        results.append(("acceptance_path", False))

    print("\n=== SMOKE ALL SUS ===")
    for name, ok in results:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    passed = sum(1 for _, ok in results if ok)
    print(f"=== {passed}/{len(results)} PASS ===")
    ready = all(ok for _, ok in results)
    print("SUS:", "READY" if ready else "NOT_READY")
    sys.exit(0 if ready else 1)


if __name__ == "__main__":
    main()
