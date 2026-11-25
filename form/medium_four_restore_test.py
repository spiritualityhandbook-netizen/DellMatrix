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

Correction round (Director CORRECTION_REQUIRED 7136700328): a field
PRESENT with an explicit null is not an absent field. Where the writer
never emits null for a field, a present null refuses typed instead of
receiving the from_dict default substitution (bimo active -> false,
companion pos -> [2, 1], and every sibling field of the same class);
absent fields keep their documented per-field defaults, and the lawful
null BIMO slot assignments still load whole.
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

        def _present_empty(data):
            data["duo_ledger"] = []
        f = _mutated(base, tmp / "duo_present_empty.json", _present_empty)
        before = f.read_bytes()
        rec("DUO present-but-EMPTY ledger with positive generation refuses load (typed) — no invented marker",
            _refuses(owner, f))
        rec("DUO present-empty refusal leaves the source file bytes unchanged",
            f.read_bytes() == before)

        def _present_empty_gen0(data):
            data["duo_ledger"] = []
            data["duo_generation"] = 0
        f = _mutated(base, tmp / "duo_present_empty_gen0.json",
                     _present_empty_gen0)
        load_ok = False
        resave_ok = False
        try:
            p = _load(owner, f)
            load_ok = entries(p) == [] and p.duo.generation == 0
            if load_ok:
                resave0 = tmp / "duo_present_empty_gen0_resaved.json"
                persist_rest.save(p, str(resave0))
                rdata = json.loads(resave0.read_text())
                resave_ok = (rdata["duo_ledger"] == []
                             and rdata["duo_generation"] == 0)
        except Exception:
            load_ok = False
            resave_ok = False
        rec("DUO present-empty gen=0 control loads lawful (empty ledger, generation 0)",
            load_ok)
        rec("DUO present-empty gen=0 resave parity (section stays empty, generation 0)",
            resave_ok)

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

        def _nullgen(data):
            data["duo_generation"] = None
        f = _mutated(base, tmp / "duo_nullgen.json", _nullgen)
        rec("DUO present-null duo_generation refuses load (typed) — counter already distinguishes present from absent",
            _refuses(owner, f))

        for _fld in ("gen", "detail", "ts", "meta"):
            def _nullfield(data, fld=_fld):
                data["duo_ledger"][1][fld] = None
            f = _mutated(base, tmp / f"duo_null_{_fld}.json", _nullfield)
            rec(f"DUO present-null entry field ({_fld}) refuses load (typed) — ledger validator already distinguishes present from absent",
                _refuses(owner, f))

        def _absentdetail(data):
            del data["duo_ledger"][1]["detail"]
        f = _mutated(base, tmp / "duo_absentdetail.json", _absentdetail)
        try:
            p = _load(owner, f)
            got = entries(p)
            ok = (got[1]["detail"] == ""
                  and got[0] == expected[0] and got[2] == expected[2]
                  and p.duo.generation == 3)
        except Exception:
            ok = False
        rec("DUO absent entry field keeps the documented per-field default (detail=''), siblings intact",
            ok)

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


# ============================================================ B: companion

def run_companion():
    from form.dell_matrix.companion import AICompanion

    owner, other = "MediumFourCom", "MediumFourComOther"
    expected = {"name": "ProbePal", "label": "Probe Pal", "pos": [7.0, 3.0],
                "facing": "SE", "mode": "follow", "doing": "testing",
                "last_action": "probe-setup",
                "trail": [[1.0, 1.0], [2.0, 2.0], [3.0, 3.0]]}
    defaults = {"name": "AI", "label": "AI", "pos": [2.0, 1.0],
                "facing": "N", "mode": "manual", "doing": "idle", "trail": []}

    def build(own, path):
        p = open_program(own)
        c = AICompanion(name="ProbePal", label="Probe Pal", pos=[7.0, 3.0],
                        facing="SE", mode="follow", doing="testing",
                        last_action="probe-setup")
        c.trail = [[1.0, 1.0], [2.0, 2.0], [3.0, 3.0]]
        p.companion = c
        persist_rest.save(p, str(path))
        return path

    def fields(c):
        return {"name": c.name, "label": c.label,
                "pos": [float(c.pos[0]), float(c.pos[1])],
                "facing": c.facing, "mode": c.mode, "doing": c.doing,
                "last_action": c.last_action,
                "trail": [[float(pt[0]), float(pt[1])] for pt in c.trail]}

    tmp = Path(tempfile.mkdtemp(prefix="medium4_com_"))
    try:
        base = build(owner, tmp / "com_base.json")
        orig_section = json.loads(base.read_text())["companion"]

        p = _load(owner, base)
        rec("COM clean load preserves all fields",
            fields(p.companion) == expected)
        resaved = tmp / "com_resaved.json"
        persist_rest.save(p, str(resaved))
        rec("COM clean save->load->resave parity (section identical)",
            json.loads(resaved.read_text())["companion"] == orig_section)
        p2 = _load(owner, resaved)
        rec("COM second-generation continuity (clean): load of resave identical",
            fields(p2.companion) == expected)

        def _absent(data):
            del data["companion"]
        f = _mutated(base, tmp / "com_absent.json", _absent)
        p = _load(owner, f)
        got = fields(p.companion)
        rec("COM legacy ABSENT section loads as the documented constructor default",
            all(got[k] == v for k, v in defaults.items()))

        def _extra_key(data):
            data["companion"]["future_field"] = "additive"
        f = _mutated(base, tmp / "com_extrakey.json", _extra_key)
        try:
            p = _load(owner, f)
            ok = fields(p.companion) == expected
        except Exception:
            ok = False
        rec("COM negative mutant: extra unknown key loads whole (no over-refusal)",
            ok)

        def _missing_field(data):
            del data["companion"]["doing"]
        f = _mutated(base, tmp / "com_missing.json", _missing_field)
        try:
            p = _load(owner, f)
            got = fields(p.companion)
            ok = (got["doing"] == "idle"
                  and all(got[k] == v for k, v in expected.items()
                          if k != "doing"))
        except Exception:
            ok = False
        rec("COM negative mutant: missing optional field falls back per-field, siblings intact",
            ok)

        def _as_list(data):
            data["companion"] = ["not-a-mapping", 42]
        f = _mutated(base, tmp / "com_list.json", _as_list)
        before = f.read_bytes()
        rec("COM-A wrong container (list) refuses load (typed), no default substitution",
            _refuses(owner, f))
        rec("COM-A refused load leaves the source file bytes unchanged",
            f.read_bytes() == before)

        def _as_str(data):
            data["companion"] = "GARBAGE-STRING"
        f = _mutated(base, tmp / "com_str.json", _as_str)
        rec("COM-B garbage scalar section refuses load (typed)",
            _refuses(owner, f))

        def _as_null(data):
            data["companion"] = None
        f = _mutated(base, tmp / "com_null.json", _as_null)
        rec("COM explicit-null section refuses load (typed) — present != absent",
            _refuses(owner, f))

        def _badpos(data):
            data["companion"]["pos"] = 42
        f = _mutated(base, tmp / "com_badpos.json", _badpos)
        before = f.read_bytes()
        rec("COM-C one corrupt scalar (pos:=42) refuses load (typed), no total default substitution",
            _refuses(owner, f))
        rec("COM-C refused load leaves the source file bytes unchanged",
            f.read_bytes() == before)

        def _badtrail(data):
            data["companion"]["trail"] = [[1.0, 1.0], ["x", "y"], [3.0, 3.0]]
        f = _mutated(base, tmp / "com_badtrail.json", _badtrail)
        rec("COM-D one malformed trail point among valid refuses load (typed)",
            _refuses(owner, f))
        try:
            p = _load(owner, f)
            resave2 = tmp / "com_badtrail_resaved.json"
            persist_rest.save(p, str(resave2))
            kept = json.loads(resave2.read_text())["companion"]
            ok = kept == orig_section
            detail = "resaved section is the constructor default" if not ok else ""
        except ProgramLoadError:
            ok, detail = True, ""
        rec("COM-D second-generation continuity: load+resave preserves the original section",
            ok, detail)

        def _shortpos(data):
            data["companion"]["pos"] = [5]
        f = _mutated(base, tmp / "com_shortpos.json", _shortpos)
        rec("COM-E truncated pos ([5]) refuses load (typed)",
            _refuses(owner, f))

        def _boolpos(data):
            data["companion"]["pos"] = [True, 3.0]
        f = _mutated(base, tmp / "com_boolpos.json", _boolpos)
        rec("COM bool pos element refuses load (typed) — JSON type confusion (float(True)==1.0)",
            _refuses(owner, f))

        def _hugepos(data):
            data["companion"]["pos"] = [10 ** 1000, 3.0]
        f = _mutated(base, tmp / "com_hugepos.json", _hugepos)
        rec("COM-F oversized integer coordinate (10**1000) refuses load (typed), no OverflowError escape",
            _refuses(owner, f))

        def _extracoordpos(data):
            data["companion"]["pos"] = [1, 2, 3]
        f = _mutated(base, tmp / "com_extracoord.json", _extracoordpos)
        rec("COM-G extra-coordinate pos ([1,2,3]) refuses load (typed), no silent resave truncation",
            _refuses(owner, f))

        def _extracoordtrail(data):
            data["companion"]["trail"] = [[1, 2, 3]]
        f = _mutated(base, tmp / "com_extracoordtrail.json", _extracoordtrail)
        rec("COM-H extra-coordinate trail point refuses load (typed), no silent resave truncation",
            _refuses(owner, f))

        def _overtrail(data):
            data["companion"]["trail"] = [[float(i), float(i)] for i in range(17)]
        f = _mutated(base, tmp / "com_overtrail.json", _overtrail)
        rec("COM-I trail longer than the writer cap (17 > 16) refuses load (typed), no silent next-save cut",
            _refuses(owner, f))

        def _intfacing(data):
            data["companion"]["facing"] = 42
        f = _mutated(base, tmp / "com_intfacing.json", _intfacing)
        rec("COM non-string scalar in a string field (facing:=42) refuses load (typed)",
            _refuses(owner, f))

        def _nullpos(data):
            data["companion"]["pos"] = None
        f = _mutated(base, tmp / "com_nullpos.json", _nullpos)
        before = f.read_bytes()
        rec("COM present-null pos refuses load (typed) — present != absent, no default [2, 1] substitution",
            _refuses(owner, f))
        rec("COM present-null pos refusal leaves the source file bytes unchanged",
            f.read_bytes() == before)

        def _absentpos(data):
            del data["companion"]["pos"]
        f = _mutated(base, tmp / "com_absentpos.json", _absentpos)
        try:
            p = _load(owner, f)
            got = fields(p.companion)
            ok = (got["pos"] == [2.0, 1.0]
                  and all(got[k] == v for k, v in expected.items()
                          if k != "pos"))
        except Exception:
            ok = False
        rec("COM absent pos keeps the documented per-field default, siblings intact",
            ok)

        def _nulltrail(data):
            data["companion"]["trail"] = None
        f = _mutated(base, tmp / "com_nulltrail.json", _nulltrail)
        rec("COM present-null trail refuses load (typed) — writer emits a list",
            _refuses(owner, f))

        for _fld in ("name", "label", "facing", "mode", "doing", "last_action"):
            def _nullstr(data, fld=_fld):
                data["companion"][fld] = None
            f = _mutated(base, tmp / f"com_null_{_fld}.json", _nullstr)
            rec(f"COM present-null string field ({_fld}) refuses load (typed) — writer emits a string",
                _refuses(owner, f))

        other_path = build(other, tmp / "com_other.json")
        obefore = other_path.read_bytes()
        f = _mutated(base, tmp / "com_badtrail2.json", _badtrail)
        refused = _refuses(owner, f)
        p = _load(other, other_path)
        rec("COM cross-owner: corrupt load refuses; foreign file untouched + loads intact",
            refused and other_path.read_bytes() == obefore
            and fields(p.companion) == expected)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ============================================================ C: self_knowledge

def run_self_knowledge():
    owner, other = "MediumFourSK", "MediumFourSKOther"
    expected = {"mastery": {"floor": 0.9, "grow": 0.5}, "probes": 10,
                "hits": 7, "generations_seen": 4,
                "known_matrices": ["alpha-matrix", "beta-matrix"],
                "known_snaps": ["snap-one"], "gaps_closed": ["gap-a"]}
    blank = {"mastery": {}, "probes": 0, "hits": 0, "generations_seen": 0,
             "known_matrices": [], "known_snaps": [], "gaps_closed": []}

    def build(own, path):
        p = open_program(own)
        sk = p.self_knowledge
        sk.mastery = {"floor": 0.9, "grow": 0.5}
        sk.probes = 10
        sk.hits = 7
        sk.generations_seen = 4
        sk.known_matrices = ["alpha-matrix", "beta-matrix"]
        sk.known_snaps = ["snap-one"]
        sk.gaps_closed = ["gap-a"]
        persist_rest.save(p, str(path))
        return path

    def fields(sk):
        return {"mastery": dict(sk.mastery), "probes": sk.probes,
                "hits": sk.hits, "generations_seen": sk.generations_seen,
                "known_matrices": list(sk.known_matrices),
                "known_snaps": list(sk.known_snaps),
                "gaps_closed": list(sk.gaps_closed)}

    tmp = Path(tempfile.mkdtemp(prefix="medium4_sk_"))
    try:
        base = build(owner, tmp / "sk_base.json")
        orig_section = json.loads(base.read_text())["self_knowledge"]

        p = _load(owner, base)
        rec("SK clean load preserves all fields",
            fields(p.self_knowledge) == expected)
        resaved = tmp / "sk_resaved.json"
        persist_rest.save(p, str(resaved))
        rec("SK clean save->load->resave parity (section identical)",
            json.loads(resaved.read_text())["self_knowledge"] == orig_section)
        p2 = _load(owner, resaved)
        rec("SK second-generation continuity (clean): load of resave identical",
            fields(p2.self_knowledge) == expected)

        def _absent(data):
            del data["self_knowledge"]
        f = _mutated(base, tmp / "sk_absent.json", _absent)
        p = _load(owner, f)
        rec("SK legacy ABSENT section loads as the documented blank model",
            fields(p.self_knowledge) == blank)

        def _extra_key(data):
            data["self_knowledge"]["future_field"] = "additive"
        f = _mutated(base, tmp / "sk_extrakey.json", _extra_key)
        try:
            p = _load(owner, f)
            ok = fields(p.self_knowledge) == expected
        except Exception:
            ok = False
        rec("SK negative mutant: extra unknown key loads whole (no over-refusal)",
            ok)

        def _stale_derived(data):
            data["self_knowledge"]["hit_rate"] = 0.1234
            data["self_knowledge"]["avg_mastery"] = 9.99
        f = _mutated(base, tmp / "sk_derived.json", _stale_derived)
        try:
            p = _load(owner, f)
            ok = (fields(p.self_knowledge) == expected
                  and p.self_knowledge.to_dict()["hit_rate"] == 0.7)
        except Exception:
            ok = False
        rec("SK negative mutant: stale derived keys are ignored and recomputed, not trusted",
            ok)

        def _as_list(data):
            data["self_knowledge"] = ["not-a-mapping"]
        f = _mutated(base, tmp / "sk_list.json", _as_list)
        before = f.read_bytes()
        rec("SK-A wrong container (list) refuses load (typed), no silent blanking",
            _refuses(owner, f))
        rec("SK-A refused load leaves the source file bytes unchanged",
            f.read_bytes() == before)

        def _as_str(data):
            data["self_knowledge"] = "GARBAGE-STRING"
        f = _mutated(base, tmp / "sk_str.json", _as_str)
        rec("SK-B garbage scalar section refuses load (typed)",
            _refuses(owner, f))

        def _as_null(data):
            data["self_knowledge"] = None
        f = _mutated(base, tmp / "sk_null.json", _as_null)
        rec("SK explicit-null section refuses load (typed) — present != absent",
            _refuses(owner, f))

        def _badmastery(data):
            data["self_knowledge"]["mastery"] = {"floor": "not-a-number",
                                                  "grow": 0.5}
        f = _mutated(base, tmp / "sk_badmastery.json", _badmastery)
        before = f.read_bytes()
        rec("SK-C one corrupt mastery value refuses load (typed), no whole-model blanking",
            _refuses(owner, f))
        rec("SK-C refused load leaves the source file bytes unchanged",
            f.read_bytes() == before)

        def _hugemastery(data):
            data["self_knowledge"]["mastery"] = {"floor": 10 ** 1000,
                                                 "grow": 0.5}
        f = _mutated(base, tmp / "sk_hugemastery.json", _hugemastery)
        rec("SK oversized integer mastery (10**1000) refuses load (typed), no OverflowError escape",
            _refuses(owner, f))

        def _badprobes(data):
            data["self_knowledge"]["probes"] = "not-a-number"
        f = _mutated(base, tmp / "sk_badprobes.json", _badprobes)
        rec("SK-D one corrupt counter (probes:=string) refuses load (typed)",
            _refuses(owner, f))

        def _strmatrices(data):
            data["self_knowledge"]["known_matrices"] = "GARBAGE-STRING"
        f = _mutated(base, tmp / "sk_strmatrices.json", _strmatrices)
        rec("SK-E string in a list field refuses load (typed) — no character splitting",
            _refuses(owner, f))
        try:
            p = _load(owner, f)
            mangled = p.self_knowledge.known_matrices == list("GARBAGE-STRING")
            detail = ("loaded as 14 single characters" if mangled else "")
            ok = not mangled and p.self_knowledge.known_matrices == ["alpha-matrix", "beta-matrix"]
        except ProgramLoadError:
            ok, detail = True, ""
        rec("SK-E loaded known_matrices is never a character list",
            ok, detail)
        try:
            p = _load(owner, f)
            resave2 = tmp / "sk_strmatrices_resaved.json"
            persist_rest.save(p, str(resave2))
            kept = json.loads(resave2.read_text())["self_knowledge"]["known_matrices"]
            ok = kept == ["alpha-matrix", "beta-matrix"]
            detail = f"resaved known_matrices = {kept!r}" if not ok else ""
        except ProgramLoadError:
            ok, detail = True, ""
        rec("SK-E second-generation continuity: load+resave keeps the original inventory",
            ok, detail)

        def _strsnaps(data):
            data["self_knowledge"]["known_snaps"] = "snap-one"
        f = _mutated(base, tmp / "sk_strsnaps.json", _strsnaps)
        rec("SK string in known_snaps refuses load (typed) — no character splitting",
            _refuses(owner, f))

        def _mastery_high(data):
            data["self_knowledge"]["mastery"] = {"floor": 1.5, "grow": 0.5}
        f = _mutated(base, tmp / "sk_mastery_high.json", _mastery_high)
        rec("SK mastery value above 1.0 refuses load (typed) — documented range 0..1",
            _refuses(owner, f))

        def _mastery_neg(data):
            data["self_knowledge"]["mastery"] = {"floor": -0.25, "grow": 0.5}
        f = _mutated(base, tmp / "sk_mastery_neg.json", _mastery_neg)
        rec("SK negative mastery value refuses load (typed)",
            _refuses(owner, f))

        def _probes_neg(data):
            data["self_knowledge"]["probes"] = -3
        f = _mutated(base, tmp / "sk_probes_neg.json", _probes_neg)
        rec("SK negative counter (probes:=-3) refuses load (typed)",
            _refuses(owner, f))

        def _hits_gt(data):
            data["self_knowledge"]["hits"] = 99
        f = _mutated(base, tmp / "sk_hits_gt.json", _hits_gt)
        rec("SK hits > probes refuses load (typed) — writer invariant",
            _refuses(owner, f))

        def _probes_bool(data):
            data["self_knowledge"]["probes"] = True
        f = _mutated(base, tmp / "sk_probes_bool.json", _probes_bool)
        rec("SK bool counter refuses load (typed) — JSON type confusion (int(True)==1)",
            _refuses(owner, f))

        def _nullmastery(data):
            data["self_knowledge"]["mastery"] = None
        f = _mutated(base, tmp / "sk_nullmastery.json", _nullmastery)
        rec("SK present-null mastery refuses load (typed) — writer emits an object",
            _refuses(owner, f))

        for _fld in ("probes", "hits", "generations_seen"):
            def _nullcounter(data, fld=_fld):
                data["self_knowledge"][fld] = None
            f = _mutated(base, tmp / f"sk_null_{_fld}.json", _nullcounter)
            rec(f"SK present-null counter ({_fld}) refuses load (typed) — writer emits an int, no silent 0",
                _refuses(owner, f))

        for _fld in ("known_matrices", "known_snaps", "gaps_closed"):
            def _nulllist(data, fld=_fld):
                data["self_knowledge"][fld] = None
            f = _mutated(base, tmp / f"sk_null_{_fld}.json", _nulllist)
            rec(f"SK present-null inventory ({_fld}) refuses load (typed) — writer emits a list",
                _refuses(owner, f))

        def _absentcounter(data):
            del data["self_knowledge"]["generations_seen"]
        f = _mutated(base, tmp / "sk_absentcounter.json", _absentcounter)
        try:
            p = _load(owner, f)
            got = fields(p.self_knowledge)
            ok = (got["generations_seen"] == 0
                  and all(got[k] == v for k, v in expected.items()
                          if k != "generations_seen"))
        except Exception:
            ok = False
        rec("SK absent counter keeps the documented per-field default (0), siblings intact",
            ok)

        def _absentmastery(data):
            del data["self_knowledge"]["mastery"]
        f = _mutated(base, tmp / "sk_absentmastery.json", _absentmastery)
        try:
            p = _load(owner, f)
            got = fields(p.self_knowledge)
            ok = (got["mastery"] == {}
                  and all(got[k] == v for k, v in expected.items()
                          if k != "mastery"))
        except Exception:
            ok = False
        rec("SK absent mastery keeps the documented per-field default ({}), siblings intact",
            ok)

        def _null_derived(data):
            data["self_knowledge"]["hit_rate"] = None
            data["self_knowledge"]["ledger_len"] = None
            data["self_knowledge"]["avg_mastery"] = None
        f = _mutated(base, tmp / "sk_null_derived.json", _null_derived)
        try:
            p = _load(owner, f)
            ok = (fields(p.self_knowledge) == expected
                  and p.self_knowledge.to_dict()["hit_rate"] == 0.7)
        except Exception:
            ok = False
        rec("SK negative mutant: null derived keys are ignored and recomputed, never trusted (derived keys are not restored fields)",
            ok)

        other_path = build(other, tmp / "sk_other.json")
        obefore = other_path.read_bytes()
        f = _mutated(base, tmp / "sk_badmastery2.json", _badmastery)
        refused = _refuses(owner, f)
        p = _load(other, other_path)
        rec("SK cross-owner: corrupt load refuses; foreign file untouched + loads intact",
            refused and other_path.read_bytes() == obefore
            and fields(p.self_knowledge) == expected)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ============================================================ D: bimo / persona_matrix

def run_bimo():
    owner, other = "MediumFourBimo", "MediumFourBimoOther"
    filled = {"logic": "manny", "growth": "melody"}

    def build(own, path):
        p = open_program(own)
        p.bimo.slots["logic"] = "manny"
        p.bimo.slots["growth"] = "melody"
        p.bimo.active = True
        p.bimo.pilot = "manny"
        p.bimo.mode = "docked"
        p.persona_lens = "manny"
        persist_rest.save(p, str(path))
        return path

    def filled_of(bimo):
        return {s: pid for s, pid in bimo.slots.items() if pid}

    tmp = Path(tempfile.mkdtemp(prefix="medium4_bimo_"))
    try:
        base = build(owner, tmp / "bimo_base.json")
        orig_section = json.loads(base.read_text())["bimo"]

        p = _load(owner, base)
        rec("BIMO clean load preserves slots/pilot/mode/active",
            filled_of(p.bimo) == filled and p.bimo.pilot == "manny"
            and p.bimo.mode == "docked" and p.bimo.active is True)
        rec("BIMO clean load rebuilds persona_matrix from the lens",
            getattr(p.persona_matrix, "active", None) == "manny")
        resaved = tmp / "bimo_resaved.json"
        persist_rest.save(p, str(resaved))
        rec("BIMO clean save->load->resave parity (section identical)",
            json.loads(resaved.read_text())["bimo"] == orig_section)
        p2 = _load(owner, resaved)
        rec("BIMO second-generation continuity (clean): load of resave identical",
            filled_of(p2.bimo) == filled and p2.bimo.pilot == "manny"
            and getattr(p2.persona_matrix, "active", None) == "manny")

        def _absent(data):
            del data["bimo"]
        f = _mutated(base, tmp / "bimo_absent.json", _absent)
        p = _load(owner, f)
        rec("BIMO legacy ABSENT section loads defaults AND persona_matrix still rebuilds",
            filled_of(p.bimo) == {} and p.bimo.pilot == "mathelody"
            and getattr(p.persona_matrix, "active", None) == "manny")

        def _extra_key(data):
            data["bimo"]["future_field"] = "additive"
        f = _mutated(base, tmp / "bimo_extrakey.json", _extra_key)
        try:
            p = _load(owner, f)
            ok = (filled_of(p.bimo) == filled and p.bimo.pilot == "manny"
                  and getattr(p.persona_matrix, "active", None) == "manny")
        except Exception:
            ok = False
        rec("BIMO negative mutant: extra unknown top-level key loads whole (no over-refusal)",
            ok)

        def _as_list(data):
            data["bimo"] = ["not-a-mapping"]
        f = _mutated(base, tmp / "bimo_list.json", _as_list)
        before = f.read_bytes()
        rec("BIMO-A wrong container (list) refuses load (typed), no default substitution",
            _refuses(owner, f))
        rec("BIMO-A refused load leaves the source file bytes unchanged",
            f.read_bytes() == before)

        def _as_str(data):
            data["bimo"] = "GARBAGE-STRING"
        f = _mutated(base, tmp / "bimo_str.json", _as_str)
        rec("BIMO-B garbage scalar section refuses load (typed)",
            _refuses(owner, f))

        def _as_null(data):
            data["bimo"] = None
        f = _mutated(base, tmp / "bimo_null.json", _as_null)
        rec("BIMO explicit-null section refuses load (typed) — present != absent",
            _refuses(owner, f))

        def _badslots(data):
            data["bimo"]["slots"] = "GARBAGE-STRING"
        f = _mutated(base, tmp / "bimo_badslots.json", _badslots)
        before = f.read_bytes()
        rec("BIMO-C garbage slots sub-value refuses load (typed), valid pilot not discarded",
            _refuses(owner, f))
        rec("BIMO-C refused load leaves the source file bytes unchanged",
            f.read_bytes() == before)
        try:
            p = _load(owner, f)
            active = getattr(p.persona_matrix, "active", None)
            ok = active == "manny"
            detail = f"persona_matrix.active = {active!r} after bimo defect" if not ok else ""
        except ProgramLoadError:
            ok, detail = True, ""
        rec("BIMO-C decoupling: a malformed bimo section does not destroy persona_matrix",
            ok, detail)

        def _unknown_slot(data):
            data["bimo"]["slots"]["no_such_slot"] = "manny"
        f = _mutated(base, tmp / "bimo_unknownslot.json", _unknown_slot)
        rec("BIMO-D unknown slot key among valid refuses load (typed), no silent per-entry drop",
            _refuses(owner, f))
        try:
            p = _load(owner, f)
            resave2 = tmp / "bimo_unknownslot_resaved.json"
            persist_rest.save(p, str(resave2))
            kept = json.loads(resave2.read_text())["bimo"]["slots"]
            ok = kept.get("no_such_slot") == "manny"
            detail = "unknown slot assignment erased by resave" if not ok else ""
        except ProgramLoadError:
            ok, detail = True, ""
        rec("BIMO-D second-generation continuity: load+resave keeps every slot assignment",
            ok, detail)

        def _slots_pairs(data):
            data["bimo"]["slots"] = [["logic", "manny"]]
        f = _mutated(base, tmp / "bimo_slotspairs.json", _slots_pairs)
        rec("BIMO-E slots as list-of-pairs refuses load (typed)",
            _refuses(owner, f))

        def _intslot(data):
            data["bimo"]["slots"]["logic"] = 42
        f = _mutated(base, tmp / "bimo_intslot.json", _intslot)
        rec("BIMO non-string slot value (logic:=42) refuses load (typed) — type confusion",
            _refuses(owner, f))

        def _intpilot(data):
            data["bimo"]["pilot"] = 42
        f = _mutated(base, tmp / "bimo_intpilot.json", _intpilot)
        rec("BIMO non-string pilot (pilot:=42) refuses load (typed) — no str() coercion",
            _refuses(owner, f))

        def _nullactive(data):
            data["bimo"]["active"] = None
        f = _mutated(base, tmp / "bimo_nullactive.json", _nullactive)
        before = f.read_bytes()
        rec("BIMO present-null active refuses load (typed) — present != absent, no bool(null) substitution",
            _refuses(owner, f))
        rec("BIMO present-null active refusal leaves the source file bytes unchanged",
            f.read_bytes() == before)

        def _absentactive(data):
            del data["bimo"]["active"]
        f = _mutated(base, tmp / "bimo_absentactive.json", _absentactive)
        try:
            p = _load(owner, f)
            ok = (p.bimo.active is True and filled_of(p.bimo) == filled
                  and p.bimo.pilot == "manny")
        except Exception:
            ok = False
        rec("BIMO absent active keeps the documented default (True), siblings intact",
            ok)

        def _nullslots(data):
            data["bimo"]["slots"] = None
        f = _mutated(base, tmp / "bimo_nullslots.json", _nullslots)
        rec("BIMO present-null slots refuses load (typed) — writer emits an object",
            _refuses(owner, f))

        def _absentslots(data):
            del data["bimo"]["slots"]
        f = _mutated(base, tmp / "bimo_absentslots.json", _absentslots)
        try:
            p = _load(owner, f)
            ok = (filled_of(p.bimo) == {} and p.bimo.pilot == "manny"
                  and p.bimo.active is True)
        except Exception:
            ok = False
        rec("BIMO absent slots keeps the documented empty roster, siblings intact",
            ok)

        def _nullpilot(data):
            data["bimo"]["pilot"] = None
        f = _mutated(base, tmp / "bimo_nullpilot.json", _nullpilot)
        rec("BIMO present-null pilot refuses load (typed) — writer emits a string",
            _refuses(owner, f))

        def _nullmode(data):
            data["bimo"]["mode"] = None
        f = _mutated(base, tmp / "bimo_nullmode.json", _nullmode)
        rec("BIMO present-null mode refuses load (typed) — writer emits a string",
            _refuses(owner, f))

        def _nullslotvalue(data):
            data["bimo"]["slots"]["logic"] = None
        f = _mutated(base, tmp / "bimo_nullslotvalue.json", _nullslotvalue)
        try:
            p = _load(owner, f)
            ok = (filled_of(p.bimo) == {"growth": "melody"}
                  and p.bimo.slots["logic"] is None
                  and p.bimo.pilot == "manny")
        except Exception:
            ok = False
        rec("BIMO lawful-null control: an explicit null slot assignment loads whole (undocked slot), siblings intact",
            ok)

        # Owner A->B->A (the #505 composition fence): owner B's valid
        # file loads with B's own arrangement and lens; returning to
        # owner A restores A's arrangement exactly — neither owner's
        # persona surface leaks into the other's.
        other_path = build(other, tmp / "bimo_other.json")
        obefore = other_path.read_bytes()
        f = _mutated(base, tmp / "bimo_badslots2.json", _badslots)
        refused = _refuses(owner, f)
        pb = _load(other, other_path)
        pa = _load(owner, base)
        rec("BIMO cross-owner + A->B->A: corrupt load refuses; foreign file untouched; "
            "each owner's arrangement + active persona restored as its own",
            refused and other_path.read_bytes() == obefore
            and filled_of(pb.bimo) == filled
            and getattr(pb.persona_matrix, "active", None) == "manny"
            and filled_of(pa.bimo) == filled
            and getattr(pa.persona_matrix, "active", None) == "manny")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


SECTIONS = [run_duo, run_companion, run_self_knowledge, run_bimo]


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
