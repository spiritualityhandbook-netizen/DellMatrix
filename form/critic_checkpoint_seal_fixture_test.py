#!/usr/bin/env python3
"""Critic checkpoint-seal fixtures — the CORRECT contract for idea
inventory at checkpoint time.

STATUS: BUILD AUTHORIZED AND BUILT. Director ruling 7181902882
(issue #512, 2026-11-25) adopted Option 1 (honest inventory +
fail-closed seal) plus Option 2's restore protection, after reading
the failing-first receipt for this fixture (6/10 against main
91eaa5a5: the four defect legs below red, all six controls green).
The original ten legs stand unchanged in what they assert; leg (c)
additionally accepts the ruling's explicit incomplete/refused
restore result, and legs (d)–(f) pin the ruling's further terms:
no overwrite of damaged bytes at a target path, conservative
legacy-snapshot cleanup, CURRENT unchanged on refusal, and safe
retry after operator repair.

Defect — Codex Critic Master Critique (PR #530, review 6066727800,
finding comment 4702349105); Uni verdict REAL, posted on issue #512
as 7178450928 (2026-11-25). Reproduced first-hand at main 91eaa5a5
by the preparation lane (probe evidence in
hidden_files/critic_fixes_2026-11-25/):

  * form/mandell/idea_persist.py list_idea_ids() swallows
    (OSError, json.JSONDecodeError) per file with a bare `continue`:
    an unreadable/truncated idea file vanishes from the inventory
    with no signal of any kind.
  * form/mandell/idea_checkpoint.py snapshot_ideas() iterates ONLY
    over that inventory, so its per-idea skip manifest never sees
    the damaged file: the snapshot records skipped=[] while one
    idea file on disk is unaccounted for.
  * form/mandell/checkpoint_generation.py _seal_members() calls
    snapshot_ideas(owner) and never inspects the snapshot's skipped
    list; commit_checkpoint() seals the incomplete snapshot and
    returns committed=True.
  * restore_ideas_from_snapshot() then deletes every idea file not
    in the snapshot as "stale" — the damaged file, the only on-disk
    evidence of the missing idea, is destroyed by the restore that
    was supposed to protect it.

Coverage note: load-time refusal IS covered (load_idea raises
ValueError on the same truncated file — pinned by control A2 below
and the track_d H1 family). Inventory-at-checkpoint is the
uncovered seam this fixture pins.

Contract asserted here:
  (a) An unreadable/truncated idea file is SURFACED by the
      inventory path — named in the snapshot's skipped manifest
      (by id or filename) or refused with a typed error. It is
      never silently omitted.
  (b) commit_checkpoint REFUSES (raises, seals no generation) when
      the idea inventory is incomplete.
  (c) A restore never deletes a file the snapshot failed to
      account for.

Controls (must pass before AND after any fix): a complete working
set snapshots with skipped=[], commits committed=True, and
restores round-trip whole; load_idea on the truncated file refuses.

Run: python3 -m form.critic_checkpoint_seal_fixture_test
"""
from __future__ import annotations

import json
import os
import shutil
import sys

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}"
          + (f" — {detail}" if detail and not cond else ""))


CTL = "SealFixtureCtl"
DMG = "SealFixtureDmg"
OVR = "SealFixtureOvr"
LEG = "SealFixtureLeg"
CUR = "SealFixtureCur"


def _cleanup(owner):
    from form.persist import _STATE_DIR
    if not os.path.isdir(_STATE_DIR):
        return
    for fn in os.listdir(_STATE_DIR):
        if owner in fn:
            path = os.path.join(_STATE_DIR, fn)
            if os.path.isdir(path):
                shutil.rmtree(path, ignore_errors=True)
            else:
                try:
                    os.remove(path)
                except OSError:
                    pass


def _make_ideas(owner, count=3):
    from form.mandell.idea import Idea, Provenance, ProvenanceSource
    from form.mandell.idea_persist import save_idea
    prov = Provenance(source=ProvenanceSource.HUMAN,
                      activity="fixture", agent="seal-fixture")
    ids = []
    for i in range(count):
        idea = Idea(title=f"SEAL FIXTURE {owner} {i}")
        idea.set_property("rooms", i + 1, prov)
        save_idea(idea, owner)
        ids.append(idea.id)
    return ids


def run_all():
    from form.open import open_program
    from form.mandell.idea_persist import (
        list_idea_ids, load_idea, _idea_path)
    from form.mandell.idea_checkpoint import (
        snapshot_ideas, ideas_snapshot_path, restore_ideas_from_snapshot)
    from form.mandell import checkpoint_generation as cg

    try:
        # ---------------- controls: the healthy path ----------------
        open_program(CTL)
        ctl_ids = _make_ideas(CTL)
        check("ctl_inventory_complete",
              sorted(list_idea_ids(CTL)) == sorted(ctl_ids))
        ctl_snap_path = snapshot_ideas(CTL)
        with open(ctl_snap_path, encoding="utf-8") as f:
            ctl_snap = json.load(f)
        check("ctl_snapshot_accounts_all",
              sorted(ctl_snap["ideas"].keys()) == sorted(ctl_ids)
              and ctl_snap["skipped"] == [],
              f"ideas={len(ctl_snap['ideas'])} skipped={ctl_snap['skipped']}")
        ctl_receipt = cg.commit_checkpoint(open_program(CTL))
        check("ctl_commit_seals", ctl_receipt.get("committed") is True)
        restore_ideas_from_snapshot(CTL, ctl_snap_path)
        check("ctl_restore_roundtrip",
              sorted(list_idea_ids(CTL)) == sorted(ctl_ids)
              and all(os.path.isfile(_idea_path(i, CTL)) for i in ctl_ids))

        # ---------------- damaged owner: setup ----------------
        open_program(DMG)
        dmg_ids = _make_ideas(DMG)
        check("dmg_setup_inventory_complete",
              sorted(list_idea_ids(DMG)) == sorted(dmg_ids))
        victim = dmg_ids[1]
        vpath = _idea_path(victim, DMG)
        with open(vpath, "r+b") as f:
            f.truncate(81)

        # Control A2: the load path already refuses this file
        # (existing track_d H1 behavior — must stay true).
        try:
            load_idea(victim, DMG)
            check("ctl_load_refuses_truncated", False,
                  "load_idea returned the truncated idea")
        except (ValueError, FileNotFoundError):
            check("ctl_load_refuses_truncated", True)

        # -------- (a) inventory must surface the damaged file -------
        snap = None
        snap_raised = None
        try:
            dmg_snap_path = snapshot_ideas(DMG)
            with open(dmg_snap_path, encoding="utf-8") as f:
                snap = json.load(f)
        except Exception as exc:  # typed refusal also satisfies (a)
            snap_raised = exc
        if snap_raised is not None:
            check("a_inventory_surfaces_damage", True)
        else:
            accounted = set(snap["ideas"].keys())
            for entry in snap.get("skipped", []):
                if isinstance(entry, dict):
                    if entry.get("id"):
                        accounted.add(entry["id"])
                    if os.path.basename(vpath) in str(entry.get("error", "")):
                        accounted.add(victim)
                    if os.path.basename(vpath) in str(entry.get("file", "")):
                        accounted.add(victim)
            check("a_inventory_surfaces_damage", victim in accounted,
                  f"snapshot ideas={len(snap['ideas'])} "
                  f"skipped={snap['skipped']} — victim unaccounted")

        # -------- (b) checkpoint must refuse on incomplete inventory --
        committed = False
        refused = False
        try:
            receipt = cg.commit_checkpoint(open_program(DMG))
            committed = receipt.get("committed") is True
        except Exception:
            refused = True
        check("b_checkpoint_refuses_incomplete", refused and not committed,
              f"committed={committed} refused={refused}")
        check("b_no_generation_sealed",
              refused and not cg.has_checkpoint(DMG),
              "a CURRENT pointer exists for the damaged owner")

        # -------- (c) restore must not delete unaccounted files -----
        # Ruling 7181902882: when preserved extras prevent exact
        # convergence the restore returns an explicit incomplete /
        # refused result (raises) and modifies nothing; in every case
        # the damaged file's bytes survive byte-identical.
        if snap is None:
            check("c_restore_preserves_unaccounted", True,
                  "no incomplete snapshot exists to restore from")
        else:
            with open(vpath, "rb") as f:
                victim_bytes = f.read()
            try:
                restore_ideas_from_snapshot(DMG, ideas_snapshot_path(DMG))
            except Exception:
                pass  # explicit refused result is the designed outcome
            check("c_restore_preserves_unaccounted",
                  os.path.isfile(vpath)
                  and open(vpath, "rb").read() == victim_bytes,
                  "restore deleted or altered the truncated idea file")

        # -------- (d) restore must not OVERWRITE damaged target bytes --
        open_program(OVR)
        ovr_ids = _make_ideas(OVR, count=2)
        ovr_snap_path = snapshot_ideas(OVR)
        ovr_victim = _idea_path(ovr_ids[0], OVR)
        ovr_sibling = _idea_path(ovr_ids[1], OVR)
        with open(ovr_sibling, "rb") as f:
            ovr_sibling_bytes = f.read()
        with open(ovr_victim, "r+b") as f:
            f.truncate(64)
        with open(ovr_victim, "rb") as f:
            ovr_damaged_bytes = f.read()
        ovr_refused = False
        try:
            restore_ideas_from_snapshot(OVR, ovr_snap_path)
        except Exception:
            ovr_refused = True
        check("d_restore_refuses_damaged_target", ovr_refused,
              "restore overwrote a damaged target file without refusing")
        check("d_damaged_target_bytes_preserved",
              os.path.isfile(ovr_victim)
              and open(ovr_victim, "rb").read() == ovr_damaged_bytes,
              "restore overwrote the damaged bytes at a target path")
        check("d_preflight_modified_nothing",
              open(ovr_sibling, "rb").read() == ovr_sibling_bytes,
              "a refused restore modified a healthy sibling file")

        # -------- (e) legacy snapshots: conservative cleanup ---------
        open_program(LEG)
        leg_ids = _make_ideas(LEG, count=2)
        with open(_idea_path(leg_ids[0], LEG), encoding="utf-8") as f:
            leg_data0 = json.load(f)
        # Hand-built LEGACY snapshot: no accounted-files manifest.
        leg_snap = {"owner": LEG, "ideas": {leg_ids[0]: leg_data0},
                    "skipped": []}
        leg_snap_path = os.path.join(
            os.path.dirname(ideas_snapshot_path(LEG)),
            "legacy_snap_fixture.json")
        with open(leg_snap_path, "w", encoding="utf-8") as f:
            json.dump(leg_snap, f)
        # (e1) a validated stale extra (canonical filename, absent
        # from the snapshot) is normal cleanup under a legacy snapshot.
        e1_completed = True
        try:
            restore_ideas_from_snapshot(LEG, leg_snap_path)
        except Exception:
            e1_completed = False
        check("e1_legacy_stale_cleanup",
              e1_completed
              and not os.path.isfile(_idea_path(leg_ids[1], LEG))
              and os.path.isfile(_idea_path(leg_ids[0], LEG)),
              "legacy restore failed to converge on a validated stale file")
        # (e2) a damaged extra under a legacy snapshot is preserved
        # byte-identical and the restore refuses exact convergence.
        leg_dir = os.path.dirname(_idea_path(leg_ids[0], LEG))
        leg_dmg = os.path.join(leg_dir, "idea_foreign_0123456789abcdef.json")
        leg_dmg_bytes = b'{"id": "foreign", "title": "truncated'
        with open(leg_dmg, "wb") as f:
            f.write(leg_dmg_bytes)
        e2_refused = False
        try:
            restore_ideas_from_snapshot(LEG, leg_snap_path)
        except Exception:
            e2_refused = True
        check("e2_legacy_damaged_extra_preserved",
              e2_refused and os.path.isfile(leg_dmg)
              and open(leg_dmg, "rb").read() == leg_dmg_bytes,
              "legacy restore deleted or altered a damaged extra file")
        try:
            os.remove(leg_snap_path)
        except OSError:
            pass

        # -------- (f) refusal keeps CURRENT; repair + retry seals ----
        open_program(CUR)
        cur_ids = _make_ideas(CUR, count=2)
        cur_receipt = cg.commit_checkpoint(open_program(CUR))
        cur_g1 = cur_receipt.get("generation_id")
        check("f_setup_commit_seals",
              cur_receipt.get("committed") is True and bool(cur_g1))
        cur_victim = _idea_path(cur_ids[1], CUR)
        with open(cur_victim, "rb") as f:
            cur_good_bytes = f.read()
        with open(cur_victim, "r+b") as f:
            f.truncate(48)
        cur_refused = False
        try:
            cg.commit_checkpoint(open_program(CUR))
        except Exception:
            cur_refused = True
        check("f_current_unchanged_on_refusal",
              cur_refused and cg.has_checkpoint(CUR)
              and cg.current_generation_id(CUR) == cur_g1,
              "a refused commit advanced or destroyed CURRENT")
        try:
            _prog, _rcpt = cg.load_checkpoint(CUR)
            prev_loads = _rcpt.get("generation_id") == cur_g1
        except Exception:
            prev_loads = False
        check("f_previous_generation_loads", prev_loads,
              "the previous generation no longer loads after a refusal")
        # Operator-style repair: restore the damaged file's bytes by
        # hand (the repair/removal tool itself is a named follow-on),
        # then the normal commit path retries and seals.
        with open(cur_victim, "wb") as f:
            f.write(cur_good_bytes)
        cur_receipt2 = cg.commit_checkpoint(open_program(CUR))
        check("f_retry_after_repair_seals",
              cur_receipt2.get("committed") is True
              and cur_receipt2.get("generation_id") != cur_g1,
              "commit after repair did not seal a new generation")
        # Clean rollback: mutate an idea, then restore G1's sealed
        # ideas member; the mutation reverts.
        from form.mandell.idea import Provenance, ProvenanceSource
        from form.mandell.idea_persist import load_idea, save_idea
        _prov = Provenance(source=ProvenanceSource.HUMAN,
                           activity="fixture", agent="seal-fixture")
        _mut = load_idea(cur_ids[0], CUR)
        _mut.set_property("rooms", 99, _prov)
        save_idea(_mut, CUR)
        restore_ideas_from_snapshot(CUR, cg._member_path(CUR, "ideas", cur_g1))
        _back = load_idea(cur_ids[0], CUR)
        check("f_clean_rollback_restores",
              _back.get_active_properties().get("rooms") == 1,
              "rollback to the sealed member did not revert the mutation")

        passed = sum(1 for _, c in RESULTS if c)
        print(f"CRITIC CHECKPOINT SEAL FIXTURE: {passed}/{len(RESULTS)} GREEN")
    finally:
        _cleanup(CTL)
        _cleanup(DMG)
        _cleanup(OVR)
        _cleanup(LEG)
        _cleanup(CUR)


def smoke() -> bool:
    try:
        run_all()
        return all(c for _, c in RESULTS)
    except Exception as e:
        print(f"CRITIC CHECKPOINT SEAL FIXTURE SMOKE FAILED: {e}")
        return False


if __name__ == "__main__":
    run_all()
    sys.exit(0 if all(c for _, c in RESULTS) else 1)
