#!/usr/bin/env python3
"""MEDIUM-four persistence-restore contract suite (Director Gate 2
clearance 7081067283, on the failing-first harness packages delivered
under 7079138987 / Gate 1 receipt 7079281654).

Contract per subscope of form/persist_rest.py: an ABSENT legacy section
keeps its documented defaults/marker; a PRESENT-but-malformed section
refuses the load with the typed ProgramLoadError BEFORE any state swap
or save, and the source file's bytes are unchanged by the refusal;
clean writer-shaped data round-trips exactly. One owner's corrupt file
never touches another owner's file.

Sections land one subscope per commit, in the ruling's order:
A duo_ledger, B companion, C self_knowledge, D bimo/persona_matrix.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
os.chdir(REPO)

from form.open import open_program
from form import persist_rest
from form.persist_rest import ProgramLoadError

RESULTS = []


def rec(name, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name}"
          + (f" | {detail}" if detail and not ok else ""))
    RESULTS.append((name, bool(ok)))


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


def _mutated(base: Path, target: Path, fn):
    data = json.loads(base.read_text())
    fn(data)
    target.write_text(json.dumps(data))
    return target


# ============================================================ A: duo_ledger

def run_duo():
    from form.duobeta.growth import GrowthEntry

    owner, other = "MediumFourDuo", "MediumFourDuoOther"
    expected = [
        {"gen": 1, "detail": "probe-entry-one", "ts": "2026-11-20T00:00:00Z",
         "meta": {"probe": "m1"}},
        {"gen": 2, "detail": "probe-entry-two", "ts": "2026-11-21T00:00:00Z",
         "meta": {"probe": "m2"}},
        {"gen": 3, "detail": "probe-entry-three", "ts": "2026-11-22T00:00:00Z",
         "meta": {"probe": "m3"}},
    ]

    def build(own, path):
        p = open_program(own)
        p.duo.ledger.clear()
        for e in expected:
            p.duo.ledger.append(GrowthEntry(
                gen=e["gen"], detail=e["detail"], ts=e["ts"],
                meta=dict(e["meta"])))
        p.duo.generation = 3
        persist_rest.save(p, str(path))
        return path

    def entries(p):
        return [{"gen": e.gen, "detail": e.detail, "ts": e.ts,
                 "meta": dict(getattr(e, "meta", None) or {})}
                for e in p.duo.ledger]

    tmp = Path(tempfile.mkdtemp(prefix="medium4_duo_"))
    try:
        base = build(owner, tmp / "duo_base.json")
        orig_section = json.loads(base.read_text())["duo_ledger"]

        p = _load(owner, base)
        rec("DUO clean load preserves all entries + generation",
            entries(p) == expected and p.duo.generation == 3)
        resaved = tmp / "duo_resaved.json"
        persist_rest.save(p, str(resaved))
        rec("DUO clean save->load->resave parity (section identical)",
            json.loads(resaved.read_text())["duo_ledger"] == orig_section)
        p2 = _load(owner, resaved)
        rec("DUO second-generation continuity (clean): load of resave identical",
            entries(p2) == expected and p2.duo.generation == 3)

        def _absent(data):
            del data["duo_ledger"]
        f = _mutated(base, tmp / "duo_absent.json", _absent)
        p = _load(owner, f)
        rec("DUO legacy ABSENT section loads with the documented honest marker",
            p.duo.generation == 3 and len(p.duo.ledger) == 1
            and "prior history not recorded" in p.duo.ledger[0].detail)

        def _extra_key(data):
            data["duo_ledger"][1]["future_field"] = "additive"
        f = _mutated(base, tmp / "duo_extrakey.json", _extra_key)
        try:
            p = _load(owner, f)
            ok = entries(p) == expected
        except Exception:
            ok = False
        rec("DUO negative mutant: entry with extra unknown key loads whole (no over-refusal)",
            ok)

        def _as_dict(data):
            data["duo_ledger"] = {"gen": 1, "detail": "dict-not-list"}
        f = _mutated(base, tmp / "duo_dict.json", _as_dict)
        before = f.read_bytes()
        rec("DUO-A wrong container (dict) refuses load (typed)",
            _refuses(owner, f))
        rec("DUO-A refused load leaves the source file bytes unchanged",
            f.read_bytes() == before)

        def _as_str(data):
            data["duo_ledger"] = "GARBAGE-STRING"
        f = _mutated(base, tmp / "duo_str.json", _as_str)
        rec("DUO-B garbage scalar section refuses load (typed)",
            _refuses(owner, f))

        def _as_null(data):
            data["duo_ledger"] = None
        f = _mutated(base, tmp / "duo_null.json", _as_null)
        rec("DUO explicit-null section refuses load (typed) — present != absent",
            _refuses(owner, f))

        def _mixed(data):
            data["duo_ledger"].insert(2, {"gen": "not-a-gen", "detail": "bad",
                                          "ts": "x", "meta": {}})
            data["duo_ledger"].insert(3, 42)
        f = _mutated(base, tmp / "duo_mixed.json", _mixed)
        before = f.read_bytes()
        rec("DUO-C malformed entries among valid refuse load (typed), no silent drop",
            _refuses(owner, f))
        rec("DUO-C refused load leaves the source file bytes unchanged",
            f.read_bytes() == before)
        try:
            p = _load(owner, f)
            resave2 = tmp / "duo_mixed_resaved.json"
            persist_rest.save(p, str(resave2))
            kept = json.loads(resave2.read_text())["duo_ledger"]
            ok = len(kept) == 5
            detail = f"resave carries {len(kept)}/5 original entries"
        except ProgramLoadError:
            ok, detail = True, ""
        rec("DUO-C second-generation continuity: load+resave drops no entry",
            ok, detail)

        def _dup(data):
            data["duo_ledger"].append({"gen": 2, "detail": "duplicate-gen",
                                        "ts": "2026-11-22T00:00:00Z", "meta": {}})
        f = _mutated(base, tmp / "duo_dup.json", _dup)
        rec("DUO-D duplicate / non-monotonic gen refuses load (typed)",
            _refuses(owner, f))

        def _badmeta(data):
            data["duo_ledger"][1]["meta"] = "GARBAGE-STRING"
        f = _mutated(base, tmp / "duo_badmeta.json", _badmeta)
        rec("DUO-E non-dict meta refuses load (typed), no silent emptying",
            _refuses(owner, f))

        def _gen0(data):
            data["duo_ledger"].insert(0, {"gen": 0, "detail": "gen-zero",
                                          "ts": "x", "meta": {}})
        f = _mutated(base, tmp / "duo_gen0.json", _gen0)
        rec("DUO gen=0 entry refuses load (typed) — writer gens start at 1",
            _refuses(owner, f))

        def _genneg(data):
            data["duo_ledger"].append({"gen": -2, "detail": "gen-negative",
                                       "ts": "x", "meta": {}})
        f = _mutated(base, tmp / "duo_genneg.json", _genneg)
        rec("DUO negative gen refuses load (typed)",
            _refuses(owner, f))

        def _genbool(data):
            data["duo_ledger"].append({"gen": True, "detail": "gen-bool",
                                       "ts": "x", "meta": {}})
        f = _mutated(base, tmp / "duo_genbool.json", _genbool)
        rec("DUO bool gen refuses load (typed) — JSON type confusion (int(True)==1)",
            _refuses(owner, f))

        other_path = build(other, tmp / "duo_other.json")
        obefore = other_path.read_bytes()
        f = _mutated(base, tmp / "duo_mixed2.json", _mixed)
        refused = _refuses(owner, f)
        p = _load(other, other_path)
        rec("DUO cross-owner: corrupt load refuses; foreign file untouched + loads intact",
            refused and other_path.read_bytes() == obefore
            and entries(p) == expected and p.duo.generation == 3)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


SECTIONS = [run_duo]


def run_all():
    for section in SECTIONS:
        section()
    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"MEDIUM-FOUR RESTORE: {passed}/{len(RESULTS)} PASS")
    return passed == len(RESULTS) and len(RESULTS) > 0


def smoke() -> bool:
    try:
        return run_all()
    except Exception as e:
        print(f"MEDIUM-FOUR RESTORE SMOKE FAILED: {e}")
        return False


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
