"""PP2b — Ace's charter rulings B2 + B3 (2026-10-28), with the
Director completion order's precision requirements.

B2: bounded evidence stores count their evictions. The count
must reflect actual evictions ONCE, survive reload, and never
grow merely because state was serialized again. Stores covered:
the kit sections (dock_sessions 10, director_records 200,
unknowns 200, design_loop 200, exchange_receipts 200,
exchange_seeds 200), the per-record dock proposal entries
(50/session), and the AutoGrowth ledger file (200 rows).

B3: develop_loop / grow_from_root announce what the automatic
path did: gate flips, and every confirmation attempt classified
as applied / denied / failed. No broader automatic acceptance
is granted by any of this — the policy still denies the
machine producer; the denial is now visible in the result.
"""
from __future__ import annotations

import glob
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from form.open import Program  # noqa: E402
from form import persist_rest  # noqa: E402
from form.dell_matrix import auto_growth  # noqa: E402
from form.dell_matrix import code_evolution as ce  # noqa: E402
from form.dell_matrix import director_records as dr  # noqa: E402
from form.dell_matrix import dock_session as ds  # noqa: E402
from form.dell_matrix import unknowns as unk  # noqa: E402

RESULTS = []


def _rec(name, cond, detail=""):
    RESULTS.append((name, bool(cond), str(detail)[:220]))


def _cleanup(owner):
    base = os.path.join(os.path.dirname(__file__), "..", "state")
    for pat in (f"program_{owner}.json", f"nursery_{owner}.json",
                f"checkpoint_{owner}_*", f"confirm_{owner}.journal.json",
                f"checkpoint_{owner}.journal.json",
                f"gen_{owner}_*", f"current_{owner}.json"):
        for f in glob.glob(os.path.join(base, pat)):
            try:
                os.remove(f)
            except FileNotFoundError:
                pass
    for d in glob.glob(os.path.join(base, f"ideas_{owner}*")):
        if os.path.isdir(d):
            shutil.rmtree(d)


def _state(owner):
    path = os.path.join(os.path.dirname(__file__), "..", "state",
                        f"program_{owner}.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _entry(pid="p1"):
    return {"pid": pid, "ts": "2026-10-28T00:00:00Z", "task": "t",
            "reason": "r", "origin": "dock:x",
            "prompt_hash": "a" * 64, "prompt_summary": "s",
            "prompt_chars": 3, "snapshot_id": None, "model": "m"}


def _check_dock_entries():
    rec = ds.new_record("PP2bDock", "s", "fake", "m", "t", "snap")
    _rec("new dock record starts with a zero counter",
         rec.get("dropped") == 0, f"dropped={rec.get('dropped')}")
    for _ in range(51):
        ds.append_proposal(rec, _entry())
    _rec("51st entry evicts once and the record counts it",
         len(rec["proposals"]) == 50 and rec["dropped"] == 1
         and ds.validate(rec, "PP2bDock")[0] is True,
         f"n={len(rec['proposals'])} dropped={rec['dropped']}")
    legacy = ds.new_record("PP2bDock", "s", "fake", "m", "t", "snap")
    del legacy["dropped"]
    _rec("pre-PP2b records (no counter) still validate",
         ds.validate(legacy, "PP2bDock")[0] is True)


def _fill_sessions(p, owner, n):
    p.dock_sessions = {}
    for i in range(n):
        r = ds.new_record(owner, f"s{i}", "fake", "m", "t", f"snap{i}")
        r["started"] = f"2026-10-28T00:{i:02d}:00Z"
        p.dock_sessions[r["session_id"]] = r


def _check_section_counters_exact_once():
    owner = "PP2bSec"
    _cleanup(owner)
    try:
        p = Program(owner)
        _fill_sessions(p, owner, 11)
        p.director_records = {}
        for i in range(201):
            e = dr.new_entry(owner, "sess", "director",
                             "evidence_request", note=f"n{i}")
            e["ts"] = f"2026-10-28T01:{i // 60:02d}:{i % 60:02d}Z"
            p.director_records[e["entry_id"]] = e
        for i in range(201):
            unk.register_encounter(p, f"subject {i}", f"question {i}?",
                                   "pp2b:test")
        p.save()
        st = _state(owner)
        _rec("sections serialize kept population + dropped_total",
             len(st["dock_sessions"]["sessions"]) == 10
             and st["dock_sessions"].get("dropped_total") == 1
             and len(st["director_records"]["entries"]) == 200
             and st["director_records"].get("dropped_total") == 1
             and len(st["unknowns"]["entries"]) == 200
             and st["unknowns"].get("dropped_total") == 1,
             f"dock={st['dock_sessions'].get('dropped_total')} "
             f"dir={st['director_records'].get('dropped_total')} "
             f"unk={st['unknowns'].get('dropped_total')}")
        p.save()
        st1b = _state(owner)
        _rec("saving the same in-memory program twice recounts nothing",
             st1b["dock_sessions"].get("dropped_total") == 1
             and st1b["director_records"].get("dropped_total") == 1
             and st1b["unknowns"].get("dropped_total") == 1,
             f"dock={st1b['dock_sessions'].get('dropped_total')} "
             f"dir={st1b['director_records'].get('dropped_total')} "
             f"unk={st1b['unknowns'].get('dropped_total')}")
        p2 = persist_rest.load(owner, activate=False)
        _rec("totals survive reload on the program",
             p2.dock_sessions_dropped_total == 1
             and p2.director_records_dropped_total == 1
             and p2.unknowns_dropped_total == 1,
             f"{p2.dock_sessions_dropped_total}/"
             f"{p2.director_records_dropped_total}/"
             f"{p2.unknowns_dropped_total}")
        p2.save()
        st2 = _state(owner)
        _rec("re-serializing the same population recounts nothing",
             st2["dock_sessions"].get("dropped_total") == 1
             and st2["director_records"].get("dropped_total") == 1
             and st2["unknowns"].get("dropped_total") == 1,
             f"dock={st2['dock_sessions'].get('dropped_total')}")
        p3 = persist_rest.load(owner, activate=False)
        _rec("totals are stable across a second reload",
             p3.dock_sessions_dropped_total == 1
             and p3.unknowns_dropped_total == 1)
    finally:
        _cleanup(owner)


def _check_load_side_and_malformed():
    owner = "PP2bLoad"
    _cleanup(owner)
    try:
        p = Program(owner)
        _fill_sessions(p, owner, 10)
        p.save()
        # Simulate a pre-PP2b file: 12 valid sessions, no counter.
        st = _state(owner)
        sessions = st["dock_sessions"]["sessions"]
        for i in (10, 11):
            r = ds.new_record(owner, f"extra{i}", "fake", "m", "t",
                              f"snapx{i}")
            r["started"] = f"2026-10-28T02:{i:02d}:00Z"
            sessions[r["session_id"]] = r
        st["dock_sessions"].pop("dropped_total", None)
        path = os.path.join(os.path.dirname(__file__), "..", "state",
                            f"program_{owner}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(st, f)
        p2 = persist_rest.load(owner, activate=False)
        _rec("load counts evictions from an uncounted legacy file",
             len(p2.dock_sessions) == 10
             and p2.dock_sessions_dropped_total == 2,
             f"kept={len(p2.dock_sessions)} "
             f"total={p2.dock_sessions_dropped_total}")
        p2.save()
        _rec("the load-side count persists on the next save",
             _state(owner)["dock_sessions"].get("dropped_total") == 2)
        # A malformed record is evidence, not an eviction.
        p3 = Program(owner)
        _fill_sessions(p3, owner, 11)
        bad = ds.new_record(owner, "bad", "fake", "m", "t", "snapbad")
        bad["started"] = "2026-10-28T03:00:00Z"
        bad["subject"] = 12345  # invalid: not a string
        p3.dock_sessions[bad["session_id"]] = bad
        p3.save()
        st3 = _state(owner)
        _rec("malformed records are preserved, never counted dropped",
             st3["dock_sessions"].get("dropped_total") == 1
             and "malformed" in st3["dock_sessions"],
             f"total={st3['dock_sessions'].get('dropped_total')} "
             f"malformed={'malformed' in st3['dock_sessions']}")
    finally:
        _cleanup(owner)


def _check_ledger():
    tmp = os.path.join(os.path.dirname(__file__), "..", "state",
                       "_pp2b_ledger.json")
    orig = auto_growth.LEDGER_PATH
    auto_growth.LEDGER_PATH = tmp
    try:
        if os.path.exists(tmp):
            os.remove(tmp)
        auto_growth._save_ledger([{"i": i} for i in range(201)])
        _rec("ledger counts the row its bound evicts",
             auto_growth.ledger_dropped_total() == 1
             and len(auto_growth._load_ledger()) == 200,
             f"total={auto_growth.ledger_dropped_total()} "
             f"rows={len(auto_growth._load_ledger())}")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump([{"i": i} for i in range(150)], f)
        _rec("legacy bare-list ledger still loads, total zero",
             len(auto_growth._load_ledger()) == 150
             and auto_growth.ledger_dropped_total() == 0)
        auto_growth._save_ledger(auto_growth._load_ledger())
        _rec("saving under the bound evicts nothing",
             auto_growth.ledger_dropped_total() == 0
             and len(auto_growth._load_ledger()) == 150)
    finally:
        auto_growth.LEDGER_PATH = orig
        if os.path.exists(tmp):
            os.remove(tmp)


def _check_b3_announcements():
    owner = "PP2bGrow"
    _cleanup(owner)
    try:
        p = Program(owner)
        p.nursery.add("Code Evolution Widget",
                      words="code evolution trial",
                      origin=f"host:{owner}")
        g1 = ce.grow_from_root(p, cycles=1)
        _rec("grow announces the gate flip it performed",
             g1.get("gate_flipped") is True
             and getattr(p.enhance, "on", None) is True,
             f"flipped={g1.get('gate_flipped')}")
        _rec("attempts are classified: denied is not applied",
             g1.get("confirm_attempts", 0) >= 1
             and g1.get("confirm_denied", 0) >= 1
             and g1.get("confirmed_n") == 0
             and g1.get("confirm_failed") == 0,
             f"attempts={g1.get('confirm_attempts')} "
             f"denied={g1.get('confirm_denied')} "
             f"applied={g1.get('confirmed_n')}")
        g2 = ce.grow_from_root(p, cycles=1)
        _rec("no flip is announced when the gate was already on",
             g2.get("gate_flipped") is False,
             f"flipped={g2.get('gate_flipped')}")
        out = ce.develop_loop(p, cycles=1, grow_cycles=1)
        keys = ("gate_flips", "confirm_attempts", "confirm_denied",
                "confirm_applied", "confirm_failed")
        _rec("develop_loop aggregates the announcements",
             all(k in out for k in keys)
             and out["confirm_applied"] + out["confirm_denied"]
             + out["confirm_failed"] == out["confirm_attempts"],
             f"out={ {k: out.get(k) for k in keys} }")
    finally:
        _cleanup(owner)


def main():
    _check_dock_entries()
    _check_section_counters_exact_once()
    _check_load_side_and_malformed()
    _check_ledger()
    _check_b3_announcements()
    ok = sum(1 for _, c, _ in RESULTS if c)
    for name, cond, detail in RESULTS:
        print(f"{'PASS' if cond else 'FAIL'} {name}"
              + (f" :: {detail}" if not cond else ""))
    print(f"PP2B_RULINGS: {ok}/{len(RESULTS)}")
    return ok == len(RESULTS)


def smoke() -> bool:
    return main()


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
