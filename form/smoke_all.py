#!/usr/bin/env python3
"""Unified Form smoke — NBD x10 item 5."""

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
    from form.persist import smoke as persist_smoke
    from form.open import smoke as open_smoke

    run("plane", plane_smoke)
    run("main_field", main_smoke)
    run("resonance", res_smoke)
    run("enhance_gate", enh_smoke)
    run("blank_cube", blank_smoke)
    run("visual", vis_smoke)
    run("shared_main", shared_smoke)
    run("persist", persist_smoke)
    run("open", open_smoke)

    print("\n=== SMOKE ALL ===")
    for name, ok in results:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    passed = sum(1 for _, ok in results if ok)
    print(f"=== {passed}/{len(results)} PASS ===")
    sys.exit(0 if all(ok for _, ok in results) else 1)


if __name__ == "__main__":
    main()
