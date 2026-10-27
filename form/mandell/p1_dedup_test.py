#!/usr/bin/env python3
"""P1 de-duplication proofs (Ten-Phase Master Plan, TD-1 + TD-3).

TD-1: the executor_leaf shadow arms for the core_i_ops HANDLED set
{27, 28, 34, 35, 37, 40, 44, 47} are retired (the MPC-011 treatment
Dell 37 already had). A direct leaf call for any of them refuses
honestly and mutates nothing; the front door keeps the canonical
core_i_ops semantics (27 commits a sealed generation, 28 refuses
without rollback authority, 44/47 refuse as unavailable).

TD-3: label->unit resolution has one ambiguity-honest semantics.
lifecycle.resolve_idea delegates to resolve_lineage_ref (a shared
label is an explicit ambiguity, never a silent first-match);
live_identity resolves by canonical tiers (exact-case beats a
case-insensitive collision) and merge/split refuse ambiguous source
tokens instead of silently merging a subset; needs._resolve_unit
never lands an edit on a wrong unit when labels collide.

Retirements: the nine verified-dead/duplicate modules are absent,
and the confirmation-journal infrastructure that shared a section
with the retired hybrid healer is intact.
"""
from __future__ import annotations

import glob
import importlib.util
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"  {'PASS' if cond else 'FAIL'}  {name}  {detail}")


def _cleanup(owner: str) -> None:
    from form.dell_matrix.nursery import owner_nursery_path
    from form.persist import _path
    paths = [owner_nursery_path(owner), _path(owner)]
    paths += glob.glob(f"form/state/checkpoint_{owner}_*")
    paths += glob.glob(f"form/state/confirm_journal_{owner}*")
    paths += glob.glob(f"form/state/ideas_{owner}")
    errors = []
    for path in paths:
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.unlink(path)
        except FileNotFoundError:
            pass
        except OSError as exc:
            errors.append(f"{path}: {exc}")
    if errors:
        raise RuntimeError("cleanup failed: " + "; ".join(errors))


def _owner_files(owner: str):
    return sorted(
        p for p in glob.glob("form/state/*") if owner in p)


def run_all() -> bool:
    from form.open import open_program
    from form.mandell import executor, executor_leaf

    owner = "P1Dedup"
    _cleanup(owner)
    try:
        p = open_program(owner)
        p.place("seed_unit", "SeedUnit", words="seed")

        # -- TD-1: direct leaf calls refuse for the whole HANDLED set,
        #    mutating nothing (no legacy checkpoint, no save, no swap).
        before = _owner_files(owner)
        n_units_before = len(p.cube.session.plane.units)
        handled = {27: "Checkpoint", 28: "Rollback", 34: "Stamp",
                   35: "Discover", 37: "Nurture", 40: "TokenCount",
                   44: "Bridge", 47: "Embed"}
        all_refused = True
        for n, name in handled.items():
            r = executor_leaf.execute_seed(p, f"{n:02d}[{name}]")
            if r.get("ok") is not False or "single-seed leaf" not in str(r.get("error", "")):
                all_refused = False
                print(f"    leaf {n}: ok={r.get('ok')} err={r.get('error')}")
        check("leaf_refuses_whole_handled_set", all_refused)
        check("leaf_refusal_mutates_nothing",
              _owner_files(owner) == before
              and len(p.cube.session.plane.units) == n_units_before,
              f"files {len(before)}->{len(_owner_files(owner))}, "
              f"units {n_units_before}->{len(p.cube.session.plane.units)}")

        # -- TD-1: front door keeps canonical core_i_ops semantics.
        r27 = executor.execute_seed(p, "27[Checkpoint]")
        check("front_door_27_commits_generation",
              r27.get("ok") is True and bool(r27.get("generation_id")),
              f"gen={r27.get('generation_id')}")
        r28 = executor.execute_seed(p, "28[Rollback]")
        check("front_door_28_refuses_without_authority",
              r28.get("ok") is False,
              f"err={r28.get('error')}")
        r34 = executor.execute_seed(p, "34[Stamp] :: p1mark")
        check("front_door_34_records_stamp",
              r34.get("ok") is True
              and (getattr(p, "last_stamp", None) is not None
                   or getattr(p, "last_core_i", {}).get("dell") == 34),
              f"last_core_i={getattr(p, 'last_core_i', None)}")
        r40 = executor.execute_seed(p, "40[TokenCount]")
        check("front_door_40_measures", r40.get("ok") is True)
        r44 = executor.execute_seed(p, "44[Bridge]")
        check("front_door_44_honest_refusal",
              r44.get("ok") is False
              and r44.get("error") == "bridge_unavailable")
        r47 = executor.execute_seed(p, "47[Embed]")
        check("front_door_47_honest_refusal",
              r47.get("ok") is False
              and r47.get("error") == "embed_unavailable")
        r35 = executor.execute_seed(p, "35[Discover]")
        check("front_door_35_executes", r35.get("ok") is True)

        # -- TD-3: lifecycle ambiguity is honest, never first-match.
        from form import lifecycle
        p.place("twin_a", "TwinLabel", words="a")
        p.place("twin_b", "TwinLabel", words="b")
        unit, err = lifecycle.resolve_idea(p, "TwinLabel")
        check("lifecycle_shared_label_is_ambiguous",
              unit is None and err is not None
              and "Ambiguous" in err and "twin_a" in err
              and "twin_b" in err,
              f"err={err}")
        unit, err = lifecycle.resolve_idea(p, "twin_a")
        check("lifecycle_exact_id_resolves",
              unit is not None and unit.id == "twin_a" and err is None)
        unit, err = lifecycle.resolve_idea(p, "outcome:xyz")
        check("lifecycle_protected_still_refused",
              unit is None and err is not None and "REFUSED" in err)
        unit, err = lifecycle.resolve_idea(p, "NoSuchIdea")
        check("lifecycle_miss_is_honest",
              unit is None and err is not None and "Unknown idea" in err)
        # Confirmed proposal + its plane unit share one ID (one
        # entity): lifecycle must resolve it to the UNIT, by ID and
        # by label, and fade must work on it. (Regression case: the
        # canonical resolver returns the proposal record for a shared
        # ID; mapping back by ID is required.)
        prop = p.nursery.add("ConfirmedIdea", words="confirmed words")
        cres = p.confirm_proposal(
            prop.id, _producer="test",
            _review_context=p.make_review_context(prop.id, "test"))
        check("lifecycle_fixture_confirm_ok", cres.get("ok") is True,
              f"cres={cres.get('error')}")
        unit, err = lifecycle.resolve_idea(p, prop.id)
        check("lifecycle_confirmed_resolves_by_id",
              unit is not None and unit.id == prop.id and err is None,
              f"err={err}")
        unit, err = lifecycle.resolve_idea(p, "ConfirmedIdea")
        check("lifecycle_confirmed_resolves_by_label",
              unit is not None and unit.id == prop.id and err is None,
              f"err={err}")
        _p2, msg = lifecycle.do_fade(p, prop.id, "p1-dedup")
        check("lifecycle_fade_on_confirmed_works",
              "Faded" in msg
              and lifecycle.get_presence(p, prop.id)["presence"] == "faded",
              f"msg={msg}")

        # -- TD-3: live_identity canonical tiers + merge ambiguity.
        from form.mandell import live_identity
        units = p.cube.session.plane.units
        got = live_identity.resolve_unit(units, "TwinLabel")
        check("live_identity_ambiguous_label_no_silent_pick",
              got is None)
        p.place("case_one", "CaseKey", words="1")
        p.place("case_two", "CASEKEY", words="2")
        got = live_identity.resolve_unit(units, "CaseKey")
        check("live_identity_exact_case_tier_wins",
              got is not None and got.id == "case_one",
              f"got={getattr(got, 'id', None)}")
        n_units = len(units)
        m = live_identity.merge_live(p, "TwinLabel and SeedUnit")
        check("merge_ambiguous_token_refused",
              m.get("ok") is False
              and m.get("error") == "ambiguous_source"
              and len(p.cube.session.plane.units) == n_units,
              f"m={m.get('error')}")

        # -- TD-3: needs edit target never lands on a colliding label.
        from form.dell_matrix import needs
        uid, u = needs._resolve_unit(p, "TwinLabel")
        check("needs_shared_label_no_wrong_target",
              uid is None and u is None)
        uid, u = needs._resolve_unit(p, "SeedUnit")
        check("needs_unique_label_resolves",
              uid == "seed_unit" and u is not None)

        # -- Retirements: modules absent; journal infra intact.
        retired = [
            "form.dell_matrix.transactional_ops",
            "form.dell_matrix.nature_physics",
            "form.dell_matrix.growth_engine",
            "form.dell_matrix.alpha_spirit",
            "form.dell_matrix.sense_intake",
            "form.mandell.operators_v0",
            "form.mandell.rules_v0",
            "form.mandell.nbd_equation",
            "form.dual_output",
        ]
        absent = all(importlib.util.find_spec(m) is None for m in retired)
        check("retired_modules_absent", absent)
        from form.mandell import core_i_recovery
        check("hybrid_healer_retired",
              not hasattr(core_i_recovery, "recover_confirmation_hybrid"))
        check("confirm_journal_infra_intact",
              all(hasattr(core_i_recovery, n) for n in (
                  "write_confirm_intent", "clear_confirm_intent",
                  "recover_confirmation_intent")))
    finally:
        _cleanup(owner)

    failed = [n for n, ok in RESULTS if not ok]
    print(f"p1_dedup_test: {len(RESULTS) - len(failed)}/{len(RESULTS)}")
    return not failed


def smoke() -> bool:
    return run_all()


if __name__ == "__main__":
    sys.exit(0 if run_all() else 1)
