"""Master plan P11 — satellite disposition guards.

Origin (Ace, 2026-10-27): the multiple matrices were
sandboxes — testing whether two matrices could exist and
combine, what a worldwide/shared matrix would look like vs a
personal one, a dev matrix for developing the program, and a
trading sandbox. His ruling: "if they aren't useful for the
whole then let them go — take what is useful."

Dispositions proven here:
- REMOVED: form/trading (Ace excluded trading 2026-10-26/27),
  network_main + shared_main (the sync island — main_field is
  the Main authority; cross-mind transfer is Exchange's gated
  job), plant_to_dev (one-off planting CLI).
- KEPT LIVE: main_field (the shared-Main authority),
  WORLDWIDE_IDEAS (feeds code_evolution, the worldwide root).
- KEPT EXPERIMENTAL: duobeta/selfgrow — isolated by design
  (own state file, self-classified NONCANONICAL/EXPERIMENTAL,
  not imported by the Program/REPL core).
- ARCHIVED: form/ancient carries its pointer README and is
  imported by nothing.
"""
from __future__ import annotations

import importlib.util
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

RESULTS = []


def _rec(name, cond, detail=""):
    RESULTS.append((name, bool(cond), str(detail)[:200]))


def _absent(spec):
    return importlib.util.find_spec(spec) is None


def smoke() -> bool:
    root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", ".."))

    _rec("trading_package_removed", _absent("form.trading"))
    _rec("sync_island_retired",
         _absent("form.dell_matrix.network_main")
         and _absent("form.dell_matrix.shared_main"))
    _rec("plant_to_dev_retired",
         _absent("form.worldwide.plant_to_dev"))

    # Organ registries no longer point at the removed package.
    body_src = open(os.path.join(
        root, "form", "dell_matrix", "matrix_body.py")).read()
    atlas_src = open(os.path.join(
        root, "form", "dell_matrix", "organ_atlas.py")).read()
    _rec("organ_registries_have_no_trading",
         "form.trading" not in body_src
         and "form.trading" not in atlas_src)

    # The body pulse runs whole without the trading organ: no
    # organ reports missing (the failure the registry entry
    # would have caused once the package was deleted).
    from form.dell_matrix import matrix_body
    pulse = matrix_body.body_pulse()
    _rec("body_pulse_runs_without_trading",
         matrix_body.smoke() is True
         and pulse.get("missing") == []
         and int(pulse.get("organ_count") or 0) > 10
         and "trading" not in str(pulse.get("present")),
         f"count={pulse.get('organ_count')} "
         f"missing={pulse.get('missing')}")

    # main_field: the surviving shared-Main authority.
    from form.dell_matrix import main_field
    _rec("main_field_live", main_field.smoke() is True)

    # Worldwide catalog still feeds code_evolution.
    from form.worldwide.WORLDWIDE_IDEAS import WORLDWIDE_IDEAS
    from form.dell_matrix import code_evolution
    _rec("worldwide_catalog_live",
         len(WORLDWIDE_IDEAS) > 0
         and hasattr(code_evolution, "develop_loop")
         and code_evolution.smoke() is True,
         f"ideas={len(WORLDWIDE_IDEAS)}")

    # selfgrow isolation: own state file + NONCANONICAL header,
    # and the Program/REPL core does not import it.
    from form.duobeta import selfgrow
    open_src = open(os.path.join(root, "form", "open.py")).read()
    repl_src = open(os.path.join(root, "form", "repl.py")).read()
    _rec("selfgrow_stays_isolated_experimental",
         os.path.basename(selfgrow.STATE_PATH)
         == "selfgrow_state.json"
         and "NONCANONICAL" in open(selfgrow.__file__).read()
         and "selfgrow" not in open_src
         and "selfgrow" not in repl_src)

    # ancient: archived with pointer, imported by nothing.
    pointer = os.path.join(root, "form", "ancient", "README.md")
    _rec("ancient_archived_with_pointer",
         os.path.exists(pointer)
         and "ARCHIVED" in open(pointer).read())

    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        print(f"[{'PASS' if ok else 'FAIL'}] {name} | {detail}")
    print(f"\n=== RESULT: {passed}/{len(RESULTS)} PASS ===")
    return passed == len(RESULTS)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
