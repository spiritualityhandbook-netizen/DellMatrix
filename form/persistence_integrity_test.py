#!/usr/bin/env python3
"""Persistence-integrity regression suite (Part I SAVE/JOURNAL).

Director clearance: PR #505 comment 7076723491. This suite is the
registered form of the two failing-first gates that proved the
outcome_ledger and lattice silent-loss defects at main 363d37bc
(hidden_files/PERSISTENCE_INTEGRITY_GATES_2026-11-22.md).

Contract under test (form/persist_rest.py restore logic):
  * outcome_ledger holds non-derivable execution evidence. An ABSENT
    section is a legacy save and loads as an empty ledger; a PRESENT
    but malformed section (wrong container, non-integer sequence,
    non-dict records, any record failing validate_record_shape)
    refuses the load with ProgramLoadError BEFORE any swap or write —
    no silent zeroing, no dropped records, no counter reset/reuse,
    and a refused load never rewrites the source file.
  * lattice holds user-authored content. An ABSENT section leaves the
    default lattice; a PRESENT but malformed section (wrong type,
    unparseable scalar, invalid setting, malformed cell) refuses the
    load with ProgramLoadError — the candidate is staged privately and
    swapped only after complete validation, so one corrupt value can
    never wipe the owner's authored lattice.
  * one owner's corrupt file never touches another owner's file.

Director CORRECTION_REQUIRED 7079022510 (PR #508 source-to-test
review) added three adversarial families, with the refusal-vs-legacy
policy ruled from the writer's own evidence: the outcome ledger's
sole writer (build_outcome/capture_outcome, DCC-XX) ALWAYS emits a
record whose owner is the program owner, whose outcome_seq is a
positive integer, keyed by its own outcome_id, under a section
counter equal to the highest record sequence — and no production
path ever deletes or trims records. Therefore:
  * A — a negative section counter, or a counter BEHIND the records'
    highest sequence, is not legacy-producible: typed refusal, never
    a silent normalize/auto-advance/reset. A counter AHEAD of the
    records is accepted verbatim (a harmless gap; never reset down).
  * B — a lattice cell's saved key must equal the canonical
    "h,v,f" of its own coordinates, and no two cells may share
    coordinates: typed refusal. (The writer emits exactly the
    canonical key per cell, one cell per coordinate.)
  * C — every record's owner must equal the loaded program's owner,
    its dict key must equal its outcome_id, and its outcome_seq must
    be a positive non-bool integer: typed refusal. A record missing
    owner or outcome_seq is likewise not writer-producible.
The one legacy case remains the ABSENT section (pre-ledger /
pre-lattice saves), unchanged.
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

from form.open import open_program
from form import persist_rest
from form.persist_rest import ProgramLoadError
from form.mandell.outcome_ledger import capture_outcome
from form.dell_matrix.harmonic_lattice import (
    HarmonicLattice, OverlayMode, Perspective)

RESULTS = []


def rec(name, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name}"
          + (f" | {detail}" if detail and not ok else ""))
    RESULTS.append((name, bool(ok)))


# ------------------------------------------------------------------ builders
def _receipt(action, mandell, dell, ok=True, err=""):
    return SimpleNamespace(
        routed=True, ok=ok, error=err, action=action, mandell=mandell,
        dell=dell, semantic="integrity", input=f"input-for-{action}",
        messages=[f"msg-{action}"], state_note=f"note-{action}")


def _build_ledger(owner, path):
    p = open_program(owner)
    ids = []
    for action, mandell, dell, ok, err in (
            ("create", "08[Create] :: alpha-integ", 8, True, ""),
            ("select", "51[Select] :: beta-integ", 51, True, ""),
            ("grow", "37[Grow] :: gamma-integ", 37, False, "integ marker")):
        record = capture_outcome(p, _receipt(action, mandell, dell, ok, err))
        assert record is not None
        ids.append(record["outcome_id"])
    assert len(p.outcome_records) == 3 and p.outcome_seq == 3
    persist_rest.save(p, str(path))
    return sorted(ids)


def _build_lattice(owner, path):
    p = open_program(owner)
    lat = HarmonicLattice(size=9, overlay=OverlayMode.CONCEPTUAL,
                          perspective=Perspective.SIDE)
    lat.origin_note = 5
    lat.put(1, 2, 0, content="idea-alpha", label="Alpha cell",
            tags=["probe", "alpha"], members=["idea-alpha"])
    lat.put(3, 4, 1, content="idea-beta", label="Beta cell",
            tags=["probe"], members=["idea-beta", "idea-beta-2"])
    lat.put(0, 0, 2, content=42, label="Answer cell", tags=[], members=[])
    p.lattice = lat
    p.lattice.to_sphere()
    persist_rest.save(p, str(path))


EXPECTED_CELLS = {"1,2,0": "idea-alpha", "3,4,1": "idea-beta", "0,0,2": 42}
EXPECTED_SETTINGS = {"size": 9, "overlay": "conceptual",
                     "perspective": "side", "form": "sphere",
                     "origin_note": 5}


def _load(owner, path):
    return persist_rest.load(owner, path=str(path), activate=False)


def _refuses(owner, path):
    """True only when the load fails closed with the typed refusal."""
    try:
        _load(owner, path)
    except ProgramLoadError:
        return True
    except Exception:
        return False
    return False


def _mutated(base: Path, target: Path, section: str, fn):
    data = json.loads(base.read_text())
    fn(data[section])
    target.write_text(json.dumps(data))
    return target


def _settings_intact(lat):
    return (lat.size == EXPECTED_SETTINGS["size"]
            and lat.overlay.value == EXPECTED_SETTINGS["overlay"]
            and lat.perspective.value == EXPECTED_SETTINGS["perspective"]
            and lat.perception.form.value == EXPECTED_SETTINGS["form"]
            and lat.origin_note == EXPECTED_SETTINGS["origin_note"])


def _cells_intact(lat):
    got = {f"{h},{v},{f}": cell.content
           for (h, v, f), cell in lat.cells.items()}
    return got == EXPECTED_CELLS


# ------------------------------------------------------------------ suite
def run_all():
    tmp = Path(tempfile.mkdtemp(prefix="persist_integ_"))
    try:
        # ------------------------------------------------ outcome_ledger
        base = tmp / "ol_base.json"
        ids = _build_ledger("IntegLedger", base)
        orig_section = json.loads(base.read_text())["outcome_ledger"]

        p = _load("IntegLedger", base)
        rec("OL clean load succeeds with seq preserved",
            p.outcome_seq == 3)
        rec("OL clean load preserves all records",
            sorted(p.outcome_records.keys()) == ids)
        resaved = tmp / "ol_resaved.json"
        persist_rest.save(p, str(resaved))
        rec("OL clean resave reproduces the original section",
            json.loads(resaved.read_text())["outcome_ledger"] == orig_section)

        data = json.loads(base.read_text())
        data["outcome_ledger"] = ["not-a-mapping", 42]
        f = tmp / "ol_list.json"
        f.write_text(json.dumps(data))
        before = f.read_bytes()
        rec("OL wrong-typed section refuses load (typed)",
            _refuses("IntegLedger", f))
        rec("OL refused load leaves the source file bytes unchanged",
            f.read_bytes() == before)

        data = json.loads(base.read_text())
        data["outcome_ledger"] = None
        f = tmp / "ol_null.json"
        f.write_text(json.dumps(data))
        rec("OL explicit-null section refuses load (typed)",
            _refuses("IntegLedger", f))

        f = _mutated(base, tmp / "ol_garbage.json", "outcome_ledger",
                     lambda s: s.update(records="GARBAGE-STRING"))
        rec("OL garbage records container refuses load (typed)",
            _refuses("IntegLedger", f))

        f = _mutated(base, tmp / "ol_badseq.json", "outcome_ledger",
                     lambda s: s.update(outcome_seq="three"))
        rec("OL non-integer sequence refuses load (typed)",
            _refuses("IntegLedger", f))

        def _mix(section):
            good = section["records"][ids[0]]
            section["records"]["out1:badmalformed00000000000000aa"] = dict(
                good, result="not-a-result")
            section["records"]["out1:junkentry0000000000000000bb"] = 42
        f = _mutated(base, tmp / "ol_mixed.json", "outcome_ledger", _mix)
        rec("OL mixed valid+invalid records refuse load (typed)",
            _refuses("IntegLedger", f))

        p = _load("IntegLedger", base)
        record = capture_outcome(
            p, _receipt("observe", "02[Observe] :: delta-integ", 2))
        rec("OL counter continuity: next capture reuses no sequence",
            record is not None and record["outcome_seq"] == 4
            and p.outcome_seq == 4 and len(p.outcome_records) == 4)

        data = json.loads(base.read_text())
        del data["outcome_ledger"]
        f = tmp / "ol_legacy.json"
        f.write_text(json.dumps(data))
        p = _load("IntegLedger", f)
        rec("OL legacy absent section loads as an empty ledger",
            p.outcome_records == {} and p.outcome_seq == 0)

        # -------------------------------------- Finding A (7079022510)
        f = _mutated(base, tmp / "ol_negseq.json", "outcome_ledger",
                     lambda s: s.update(outcome_seq=-1))
        before = f.read_bytes()
        rec("OL-A negative section counter refuses load (typed)",
            _refuses("IntegLedger", f))
        rec("OL-A refused load leaves the source file bytes unchanged",
            f.read_bytes() == before)

        f = _mutated(base, tmp / "ol_behind.json", "outcome_ledger",
                     lambda s: s.update(outcome_seq=1))
        rec("OL-A counter behind the records' max seq refuses (typed)",
            _refuses("IntegLedger", f))

        f = _mutated(base, tmp / "ol_ahead.json", "outcome_ledger",
                     lambda s: s.update(outcome_seq=10))
        p = _load("IntegLedger", f)
        rec("OL-A counter ahead of records loads verbatim, never reset",
            p.outcome_seq == 10
            and sorted(p.outcome_records.keys()) == ids)

        # -------------------------------------- Finding C (7079022510)
        def _foreign_owner(section):
            section["records"][ids[0]] = dict(
                section["records"][ids[0]], owner="IntegLedgerForeign")
        f = _mutated(base, tmp / "ol_foreign.json", "outcome_ledger",
                     _foreign_owner)
        before = f.read_bytes()
        rec("OL-C foreign-owner record refuses load (typed)",
            _refuses("IntegLedger", f))
        rec("OL-C refused load leaves the source file bytes unchanged",
            f.read_bytes() == before)

        def _id_field_mismatch(section):
            section["records"][ids[0]] = dict(
                section["records"][ids[0]], outcome_id=ids[1])
        f = _mutated(base, tmp / "ol_idfield.json", "outcome_ledger",
                     _id_field_mismatch)
        rec("OL-C record outcome_id != its key refuses load (typed)",
            _refuses("IntegLedger", f))

        def _rekeyed(section):
            section["records"]["out1:rekeyed0000000000000000000cc"] = (
                section["records"].pop(ids[0]))
        f = _mutated(base, tmp / "ol_rekeyed.json", "outcome_ledger",
                     _rekeyed)
        rec("OL-C record stored under a foreign key refuses (typed)",
            _refuses("IntegLedger", f))

        def _owner_missing(section):
            rec0 = dict(section["records"][ids[0]])
            del rec0["owner"]
            section["records"][ids[0]] = rec0
        f = _mutated(base, tmp / "ol_noowner.json", "outcome_ledger",
                     _owner_missing)
        rec("OL-C record missing owner refuses load (typed)",
            _refuses("IntegLedger", f))

        for label, bad in (("zero", 0), ("negative", -2), ("bool", True)):
            def _bad_rec_seq(section, bad=bad):
                section["records"][ids[0]] = dict(
                    section["records"][ids[0]], outcome_seq=bad)
            f = _mutated(base, tmp / f"ol_recseq_{label}.json",
                         "outcome_ledger", _bad_rec_seq)
            rec(f"OL-C record outcome_seq {label} refuses load (typed)",
                _refuses("IntegLedger", f))

        def _rec_seq_missing(section):
            rec0 = dict(section["records"][ids[0]])
            del rec0["outcome_seq"]
            section["records"][ids[0]] = rec0
        f = _mutated(base, tmp / "ol_recseq_missing.json",
                     "outcome_ledger", _rec_seq_missing)
        rec("OL-C record missing outcome_seq refuses load (typed)",
            _refuses("IntegLedger", f))

        other = tmp / "ol_other.json"
        other_ids = _build_ledger("IntegLedgerOther", other)
        before = other.read_bytes()
        p = _load("IntegLedgerOther", other)
        rec("OL foreign owner's file untouched and loads intact",
            other.read_bytes() == before
            and sorted(p.outcome_records.keys()) == other_ids
            and p.outcome_seq == 3)

        # ------------------------------------------------ lattice
        lbase = tmp / "lat_base.json"
        _build_lattice("IntegLattice", lbase)
        orig_lat = json.loads(lbase.read_text())["lattice"]

        p = _load("IntegLattice", lbase)
        rec("LAT clean load preserves settings",
            _settings_intact(p.lattice))
        rec("LAT clean load preserves all cells",
            _cells_intact(p.lattice))
        cell = p.lattice.cells[(3, 4, 1)]
        rec("LAT clean load preserves cell tags/members/labels",
            cell.tags == ["probe"]
            and cell.members == ["idea-beta", "idea-beta-2"]
            and cell.label == "Beta cell")
        lresaved = tmp / "lat_resaved.json"
        persist_rest.save(p, str(lresaved))
        rec("LAT clean resave reproduces the original section",
            json.loads(lresaved.read_text())["lattice"] == orig_lat)

        data = json.loads(lbase.read_text())
        data["lattice"] = ["not-a-mapping"]
        f = tmp / "lat_list.json"
        f.write_text(json.dumps(data))
        rec("LAT wrong-typed section refuses load (typed)",
            _refuses("IntegLattice", f))

        data = json.loads(lbase.read_text())
        data["lattice"] = None
        f = tmp / "lat_null.json"
        f.write_text(json.dumps(data))
        rec("LAT explicit-null section refuses load (typed)",
            _refuses("IntegLattice", f))

        f = _mutated(lbase, tmp / "lat_badsize.json", "lattice",
                     lambda s: s.update(size="twelve"))
        before = f.read_bytes()
        rec("LAT malformed size scalar refuses load (typed)",
            _refuses("IntegLattice", f))
        rec("LAT refused load leaves the source file bytes unchanged",
            f.read_bytes() == before)

        f = _mutated(lbase, tmp / "lat_badnote.json", "lattice",
                     lambda s: s.update(origin_note="five"))
        rec("LAT malformed origin_note scalar refuses load (typed)",
            _refuses("IntegLattice", f))

        f = _mutated(lbase, tmp / "lat_badoverlay.json", "lattice",
                     lambda s: s.update(overlay="bogus"))
        rec("LAT invalid overlay setting refuses load (typed)",
            _refuses("IntegLattice", f))

        f = _mutated(lbase, tmp / "lat_badform.json", "lattice",
                     lambda s: s.update(form="bogus"))
        rec("LAT invalid form setting refuses load (typed)",
            _refuses("IntegLattice", f))

        f = _mutated(lbase, tmp / "lat_garbagecells.json", "lattice",
                     lambda s: s.update(cells="GARBAGE-STRING"))
        rec("LAT garbage cells container refuses load (typed)",
            _refuses("IntegLattice", f))

        def _badcell(section):
            section["cells"]["9,9,9"] = {
                "h": "abc", "v": 9, "f": 9, "content": "idea-bad",
                "label": "Bad cell", "tags": [], "members": []}
        f = _mutated(lbase, tmp / "lat_badcell.json", "lattice", _badcell)
        rec("LAT malformed cell refuses load (typed)",
            _refuses("IntegLattice", f))

        f = _mutated(lbase, tmp / "lat_scalar_cell.json", "lattice",
                     lambda s: s["cells"].update({"9,9,9": 42}))
        rec("LAT non-object cell refuses load (typed)",
            _refuses("IntegLattice", f))

        # -------------------------------------- Finding B (7079022510)
        def _lying_key(section):
            section["cells"]["9,9,9"] = {
                "h": 1, "v": 2, "f": 0, "content": "idea-intruder",
                "label": "Intruder cell", "tags": [], "members": []}
        f = _mutated(lbase, tmp / "lat_lyingkey.json", "lattice",
                     _lying_key)
        before = f.read_bytes()
        rec("LAT-B key/coords mismatch refuses load (typed)",
            _refuses("IntegLattice", f))
        rec("LAT-B refused load leaves the source file bytes unchanged",
            f.read_bytes() == before)

        def _dup_coords(section):
            section["cells"]["01,2,0"] = {
                "h": 1, "v": 2, "f": 0, "content": "idea-intruder",
                "label": "Intruder cell", "tags": [], "members": []}
        f = _mutated(lbase, tmp / "lat_dupcoords.json", "lattice",
                     _dup_coords)
        rec("LAT-B duplicate coordinates refuse load (typed)",
            _refuses("IntegLattice", f))

        def _moved_cell(section):
            section["cells"]["1,2,0"] = dict(
                section["cells"]["1,2,0"], h=5)
        f = _mutated(lbase, tmp / "lat_movedcell.json", "lattice",
                     _moved_cell)
        rec("LAT-B cell coords disagreeing with its key refuse (typed)",
            _refuses("IntegLattice", f))

        data = json.loads(lbase.read_text())
        del data["lattice"]
        f = tmp / "lat_legacy.json"
        f.write_text(json.dumps(data))
        p = _load("IntegLattice", f)
        rec("LAT legacy absent section leaves the default lattice",
            p.lattice.size == 12 and p.lattice.cells == {})

        lother = tmp / "lat_other.json"
        _build_lattice("IntegLatticeOther", lother)
        before = lother.read_bytes()
        p = _load("IntegLatticeOther", lother)
        rec("LAT foreign owner's file untouched and loads intact",
            lother.read_bytes() == before
            and _settings_intact(p.lattice) and _cells_intact(p.lattice))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"PERSISTENCE-INTEGRITY: {passed}/{len(RESULTS)} GREEN")
    return passed == len(RESULTS) and len(RESULTS) > 0


def smoke() -> bool:
    try:
        return run_all()
    except Exception as e:
        print(f"PERSISTENCE-INTEGRITY SMOKE FAILED: {e}")
        return False


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
