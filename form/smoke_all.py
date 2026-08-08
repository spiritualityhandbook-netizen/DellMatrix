#!/usr/bin/env python3
"""Unified Form smoke — core suite + phrase + polyglot + accept."""

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
    from form.dell_matrix.personas import smoke as personas_smoke
    from form.dell_matrix.view_rooms import smoke as rooms_smoke
    from form.dell_matrix.forces import smoke as forces_smoke
    from form.dell_matrix.pillars import smoke as pillars_smoke
    from form.dell_matrix.workshops import smoke as workshops_smoke
    from form.dell_matrix.matrices_hub import smoke as hub_smoke
    from form.dell_matrix.ascii_bodies import smoke as bodies_smoke
    from form.mandell.english_brain import smoke as english_smoke
    from form.mandell.english_brain_150_loop import smoke as english_150_smoke
    from form.dell_matrix.sacred_geometry import smoke as geometry_smoke
    from form.dell_matrix.first_person import smoke as fp_smoke
    from form.dell_matrix.inspire_pack import smoke as inspire_smoke
    from form.dell_matrix.self_model import smoke as self_model_smoke
    from form.dell_matrix.program_evolve_150_loop import smoke as evolve_150_smoke
    from form.dell_matrix.program_strength import smoke as strength_smoke
    from form.dell_matrix.needs import smoke as needs_smoke
    from form.dell_matrix.function_150_loop import smoke as function_150_smoke
    from form.dell_matrix.internet_gate import smoke as internet_smoke
    from form.dell_matrix.code_evolution import smoke as ce_smoke
    from form.idea_create import smoke as idea_create_smoke
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
        ("personas", personas_smoke),
        ("view_rooms", rooms_smoke),
        ("forces", forces_smoke),
        ("pillars", pillars_smoke),
        ("workshops", workshops_smoke),
        ("matrices_hub", hub_smoke),
        ("ascii_bodies", bodies_smoke),
        ("english_brain", english_smoke),
        ("english_brain_150", english_150_smoke),
        ("sacred_geometry", geometry_smoke),
        ("first_person", fp_smoke),
        ("inspire_pack", inspire_smoke),
        ("self_model", self_model_smoke),
        ("program_evolve_150", evolve_150_smoke),
        ("program_strength", strength_smoke),
        ("needs", needs_smoke),
        ("function_150", function_150_smoke),
        ("internet_gate", internet_smoke),
        ("code_evolution", ce_smoke),
        ("idea_create", idea_create_smoke),
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
        results.append(("phrase_hit_rate", phrase_smoke()))
    except Exception as e:
        print("ERROR:", e)
        results.append(("phrase_hit_rate", False))

    print("\n--- polyglot_es_fr ---")
    try:
        from form.mandell.polyglot_tests import smoke as poly_smoke
        results.append(("polyglot_es_fr", poly_smoke()))
    except Exception as e:
        print("ERROR:", e)
        results.append(("polyglot_es_fr", False))

    print("\n--- verify_required ---")
    try:
        from form.open import open_program
        p = open_program("SUSVerify")
        v = p.matrix.verify()
        ok = v.get("ok") is True and hasattr(p, "lattice") and p.lattice is not None
        print("PASS" if ok else "FAIL")
        results.append(("verify_required", ok))
    except Exception as e:
        print("ERROR:", e)
        results.append(("verify_required", False))

    print("\n--- acceptance_path ---")
    try:
        from form.accept import run as accept_run
        results.append(("acceptance_path", accept_run()))
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
