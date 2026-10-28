"""Master plan P12 — final closure guards.

Pins the truth-reconciliation facts established by the final
audit on the closing tree, so they cannot silently rot:

- Both organ registries tell the truth: every "module" they
  name resolves to a real importable module, and every
  "legacy_source" names a file that exists. (P8/P11/P12
  failure class: entries outliving their retired modules —
  brain, trading, act_on_seen.)
- The limitation knowledge base is structurally honest:
  unique ids, valid statuses, affected paths that exist, the
  FLOW limitation RESOLVED (P10), and the two entries P12
  could not re-verify still carry their old verification
  SHA — refreshing an unverified claim requires deliberately
  changing this guard.
- The README's production anchor matches the tree this suite
  ships in (updated per phase, Phase O method).
- The master audit's retirement set stays retired and its
  kept authorities stay alive.
"""
from __future__ import annotations

import importlib.util
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

RESULTS = []

RETIRED = ["form.trading", "form.dell_matrix.network_main",
           "form.dell_matrix.shared_main",
           "form.worldwide.plant_to_dev",
           "form.dell_matrix.idea_grow",
           "form.dell_matrix.free_matrix",
           "form.dell_matrix.brain",
           "form.dell_matrix.floor_spirit"]


def _rec(name, cond, detail=""):
    RESULTS.append((name, bool(cond), str(detail)[:200]))


def smoke() -> bool:
    root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", ".."))

    # --- organ registry truth ---
    for mod_name, attr in (
            ("form.dell_matrix.matrix_body", "ORGANS"),
            ("form.dell_matrix.organ_atlas", "ORGAN_ATLAS")):
        m = __import__(mod_name, fromlist=[attr])
        reg = getattr(m, attr)
        missing_mod, missing_file = [], []
        for name, spec in reg.items():
            if not isinstance(spec, dict):
                continue
            target = spec.get("module")
            if target and importlib.util.find_spec(target) is None:
                missing_mod.append((name, target))
            legacy = spec.get("legacy_source")
            if legacy and not os.path.exists(
                    os.path.join(root, legacy)):
                missing_file.append((name, legacy))
        _rec(f"registry_truth_{attr}",
             not missing_mod and not missing_file,
             f"missing_mod={missing_mod} missing_file={missing_file}")

    # --- limitation knowledge honesty ---
    from form.mandell.limitation_knowledge import LIMITATIONS
    ids = [e["id"] for e in LIMITATIONS]
    valid = {"KNOWN", "IN_PROGRESS", "MITIGATED", "RESOLVED"}
    _rec("limitations_structurally_honest",
         len(ids) == len(set(ids)) == 5
         and all(e["status"] in valid for e in LIMITATIONS)
         and all(os.path.exists(os.path.join(
             root, e["affected_path"].split(":")[0]))
             for e in LIMITATIONS))
    by_id = {e["id"]: e for e in LIMITATIONS}
    _rec("flow_limitation_resolved",
         by_id["FLOW_PARTIAL_IMPLEMENTATION"]["status"]
         == "RESOLVED")
    _rec("unverified_limitations_stay_marked_stale",
         by_id["ARGUMENT_LOSS"]["last_verified_against"]
         .startswith("b4b7af19")
         and by_id["ENGLISH_UNREACHABLE_OPERATION"]
         ["last_verified_against"].startswith("b4b7af19"))

    # --- README anchor ---
    readme = open(os.path.join(root, "README.md")).read()
    _rec("readme_anchor_current",
         "**Production main:** `c6fd2fb`" in readme
         and "current production is main `2f98844`" not in readme)

    # --- audit reconciliation spot facts ---
    _rec("retired_stay_retired",
         all(importlib.util.find_spec(s) is None for s in RETIRED))
    from form.mandell import meta_runtime
    from form.dell_matrix import main_field
    _rec("kept_authorities_alive",
         main_field.smoke() is True
         and hasattr(meta_runtime, "cell_define")
         and hasattr(meta_runtime, "parse_directive"))

    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        print(f"[{'PASS' if ok else 'FAIL'}] {name} | {detail}")
    print(f"\n=== RESULT: {passed}/{len(RESULTS)} PASS ===")
    return passed == len(RESULTS)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
