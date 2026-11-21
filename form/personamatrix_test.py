#!/usr/bin/env python3
"""Row #155 PERSONAMATRIX (C8.MultiPsalm) — user persona layer on the
canonical BIMO/persona machinery.

Authority: Ace ruling 2026-11-20 item 11 — row #155 is unblocked:
incorporate ALL of Ace's Psalm personas, analyze their abilities,
place each properly as the general setting, built on the existing
BIMO/persona machinery (form/dell_matrix/personas.py). Users can
create new personas; personamatrix is a user experimentation layer
(customizable, fun to create and test).

Fences that never move (pinned here):
- The canonical PERSONAS roster is the runtime authority for the
  built-in pack and is READ-ONLY at runtime; a user persona may never
  shadow a canonical id or alias, and canonical personas cannot be
  removed through the user layer.
- Docking confers NO authority: a persona is a setting (guidance,
  directives, abilities, limits, preferred skins). A docked/piloting
  persona — built-in or user-created — cannot confirm a Nursery
  proposal; confirmation stays behind the owner's AcceptancePolicy,
  which denies persona producers like any other unauthorized producer.
- Fusion guidance changes with the docked set (directives / abilities
  / prefer_skins), and the fused limits are always the UNION of every
  docked persona's limits — no persona's fence is dropped by fusing.

Contract under test:
- S1: the full canonical roster is incorporated and placed — every
  persona carries a known category, a known BIMO slot, a matrix
  position, and analyzed directives/abilities/limits; the Persona
  Matrix cells cover the roster exactly once; the default dock is
  consistent with each persona's own slot.
- S2: user creation through personas.create_custom_persona with
  validation (canonical/alias collision, unknown category/slot,
  limits required, duplicate custom id) and removal that refuses
  canonical ids.
- S3: Program.create_persona + save/load round-trip — a user persona
  created on a Program survives persistence, resolves, docks, and
  appears in the Persona Matrix of a freshly opened Program; the
  canonical roster is byte-identical afterwards.
- S4: switching/fusion changes guidance; limits union holds,
  including a user persona's limits.
- S5: the authority fence — with personas docked and a user persona
  piloting, confirm_proposal under persona producers is denied by the
  AcceptancePolicy and the proposal stays pending; docking changes
  nothing about confirmation outcomes.

Labels: INTEGRATION (Program state is isolated per test owner via
the canonical state-dir cleanup pattern; the module-level user
layer is emptied again before the suite exits).
"""
from __future__ import annotations

import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CHECKS = []

CANONICAL_IDS = {
    "manny", "melody", "aetheris", "mathelody", "the_ancient",
    "translator", "della", "mansplainer", "dell", "oracle", "bimo_core",
}

OWNER = "pmx155owner"
STATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state")


def check(name, cond):
    CHECKS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")
    if not cond:
        raise AssertionError(name)


def _cleanup(owner):
    import shutil
    for f in glob.glob(os.path.join(STATE_DIR, f"*{owner}*")):
        try:
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.remove(f)
        except FileNotFoundError:
            pass
        except OSError as e:
            raise RuntimeError(f"cleanup failed for {f}: {e}")


def _sable_kwargs():
    return dict(
        name="Sable Warden", category="EvoLog", role="archivist",
        focus="long memory and careful shelving",
        directives=["shelve carefully", "cite the shelf"],
        abilities=["deep recall", "shelf mapping"],
        limits=["never reshelve confirmed work"],
        prefer_skins=["building", "words"],
        bimo_slot="growth",
        matrix={"h": 1, "v": 0, "shell": 2},
    )


def run_all():
    from form.dell_matrix import personas
    from form.dell_matrix.personas import (
        PERSONAS, CATEGORIES, BIMO_SLOTS, DEFAULT_DOCK,
        PersonaMatrix, BIMOBody,
        list_personas, get_persona, normalize_persona_id,
        create_custom_persona, remove_custom_persona,
        activate_custom_personas, custom_personas,
    )
    from form.open import open_program

    activate_custom_personas([])
    try:
        # ---------------- S1: roster incorporated + placed ----------
        roster = list_personas()
        ids = [p["id"] for p in roster]
        check("pm_roster_complete", set(ids) == CANONICAL_IDS
              and len(ids) == len(CANONICAL_IDS))
        check("pm_every_persona_placed", all(
            p.get("category") in CATEGORIES
            and p.get("bimo_slot") in BIMO_SLOTS
            and isinstance(p.get("matrix"), dict)
            and isinstance(p["matrix"].get("h"), int)
            and isinstance(p["matrix"].get("v"), int)
            and isinstance(p["matrix"].get("shell"), int)
            for p in roster))
        check("pm_abilities_analyzed", all(
            p.get("directives") and p.get("abilities") and p.get("limits")
            and p.get("role") and p.get("focus")
            for p in roster))
        cells = PersonaMatrix().cells()
        check("pm_matrix_cells_cover_roster",
              sorted(c["id"] for c in cells) == sorted(CANONICAL_IDS))
        check("pm_default_dock_consistent",
              set(DEFAULT_DOCK.keys()) == set(BIMO_SLOTS) and all(
                  get_persona(pid) is not None
                  and get_persona(pid).get("bimo_slot") == slot
                  for slot, pid in DEFAULT_DOCK.items()))
        psalm = [p for p in roster if p.get("category") == "Ancient_Psalms"]
        check("pm_psalm_family_incorporated",
              len(psalm) >= 1 and any(p["id"] == "the_ancient" for p in psalm))

        # ---------------- S2: user creation + validation ------------
        res = create_custom_persona(**_sable_kwargs())
        check("pm_create_ok", res.get("ok") is True
              and res["persona"]["id"] == "sable_warden"
              and res["persona"].get("custom") is True)
        got = get_persona("Sable Warden")
        check("pm_create_resolvable", got is not None
              and got["id"] == "sable_warden"
              and normalize_persona_id("sable-warden") == "sable_warden")
        cells = PersonaMatrix().cells()
        cell = [c for c in cells if c["id"] == "sable_warden"]
        check("pm_create_listed_and_placed",
              any(p["id"] == "sable_warden" for p in list_personas())
              and len(cell) == 1 and cell[0]["h"] == 1 and cell[0]["v"] == 0
              and cell[0]["bimo_slot"] == "growth")
        kw = _sable_kwargs(); kw["name"] = "Manny"
        check("pm_create_collision_canonical",
              create_custom_persona(**kw).get("ok") is False)
        kw = _sable_kwargs(); kw["name"] = "Ancient"
        check("pm_create_collision_alias",
              create_custom_persona(**kw).get("ok") is False)
        kw = _sable_kwargs(); kw["name"] = "Other One"; kw["category"] = "Nope"
        check("pm_create_unknown_category",
              create_custom_persona(**kw).get("ok") is False)
        kw = _sable_kwargs(); kw["name"] = "Other One"; kw["limits"] = []
        check("pm_create_limits_required",
              create_custom_persona(**kw).get("ok") is False)
        kw = _sable_kwargs(); kw["name"] = "Other One"; kw["bimo_slot"] = "throne"
        check("pm_create_unknown_slot",
              create_custom_persona(**kw).get("ok") is False)
        check("pm_create_duplicate_custom",
              create_custom_persona(**_sable_kwargs()).get("ok") is False)
        check("pm_remove_canonical_refused",
              remove_custom_persona("manny").get("ok") is False
              and get_persona("manny") is not None)
        check("pm_remove_custom_ok",
              remove_custom_persona("Sable Warden").get("ok") is True
              and get_persona("sable_warden") is None)

        # ---------------- S3: Program + persistence -----------------
        _cleanup(OWNER)
        p = open_program(OWNER)
        res = p.create_persona(
            name="Harbor Light", category="AutoLog", role="harbor watch",
            focus="calm monitoring of the whole board",
            directives=["watch quietly", "surface drift early"],
            abilities=["drift sensing", "quiet reports"],
            limits=["observes only — never confirms"],
            prefer_skins=["sphere", "core"],
            bimo_slot="watch",
            matrix={"h": -1, "v": 1, "shell": 2},
        )
        check("pm_program_create", res.get("ok") is True
              and any(r.get("id") == "harbor_light" for r in p.user_personas))
        dock = p.bimo.dock("watch", "harbor_light")
        lens = p.set_persona_lens("Harbor Light")
        check("pm_program_dock_and_lens", dock.get("ok") is True
              and lens == "harbor_light"
              and p.persona_matrix.active == "harbor_light")
        from form import persist_rest
        saved_path = p.save()
        p2 = persist_rest.load(OWNER, saved_path, activate=False)
        got2 = get_persona("harbor_light")
        cells2 = p2.persona_matrix_status()["cells"]
        check("pm_persistence_roundtrip", got2 is not None
              and got2.get("custom") is True
              and p2.bimo.dock("watch", "harbor_light").get("ok") is True
              and any(c["id"] == "harbor_light" for c in cells2)
              and any(r.get("id") == "harbor_light" for r in p2.user_personas))
        check("pm_canonical_roster_untouched",
              set(PERSONAS.keys()) == CANONICAL_IDS
              and "custom" not in get_persona("manny"))

        # ---------------- S4: guidance / fusion ---------------------
        b = BIMOBody()
        b.clear()
        b.dock("logic", "manny")
        f1 = b.fuse()
        check("pm_switch_changes_guidance",
              "validate" in f1["directives"]
              and "nurture nursery" not in f1["directives"])
        b.clear()
        b.dock("growth", "melody")
        f2 = b.fuse()
        check("pm_switch_changes_guidance_2",
              f2["directives"] != f1["directives"]
              and "evolve" in f2["directives"]
              and "validate" not in f2["directives"])
        b.dock("quality", "della")
        b.dock("watch", "harbor_light")
        f3 = b.fuse()
        harbor = get_persona("harbor_light")
        della = get_persona("della")
        melody = get_persona("melody")
        union = set(della["limits"]) | set(melody["limits"]) | set(harbor["limits"])
        check("pm_limits_union_holds", union <= set(f3["limits"]))
        check("pm_custom_in_fusion",
              "harbor_light" in f3["threads"]
              and "watch quietly" in f3["directives"]
              and "sphere" in f3["prefer_skins"])
        b.set_pilot("della")
        check("pm_pilot_switch", b.fuse()["pilot"] == "della")

        # ---------------- S5: authority fence -----------------------
        prop = p2.nursery.add(label="pm fence probe",
                              words="personamatrix fence probe",
                              kind="new")
        pid = prop.id
        p2.bimo.dock_defaults()
        p2.bimo.dock("watch", "harbor_light")
        p2.bimo.set_pilot("harbor_light")
        denied = []
        for producer in ("persona:manny", "harbor_light", "bimo", "persona"):
            r = p2.confirm_proposal(pid, _producer=producer)
            denied.append(r.get("ok") is False
                          and r.get("reason") == "acceptance_policy_denied")
        check("pm_fence_persona_producers_denied", all(denied)
              and any(pr["id"] == pid for pr in p2.list_proposals()))
        r_user = p2.confirm_proposal(pid, _producer="repl_user")
        b2 = BIMOBody()
        check("pm_fence_docking_orthogonal",
              r_user.get("ok") is False
              and r_user.get("reason") == "acceptance_policy_denied"
              and not hasattr(b2, "confirm")
              and not hasattr(b2, "confirm_proposal")
              and not hasattr(personas, "confirm_proposal"))
    finally:
        activate_custom_personas([])
        _cleanup(OWNER)

    passed = sum(1 for _, ok in CHECKS if ok)
    print(f"Personamatrix: {passed}/{len(CHECKS)} checks passed")


def smoke() -> bool:
    try:
        run_all()
        return all(ok for _, ok in CHECKS)
    except Exception as e:
        print(f"PERSONAMATRIX SMOKE FAILED: {e}")
        return False


if __name__ == "__main__":
    run_all()
