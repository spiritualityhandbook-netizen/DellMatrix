"""DD-37 / C8.Roster — dock_sessions two-tier retention contract.

Ace's ruling (plan SS12.36c/d, SS14.3 C8): the dock roster's old
10-record rotation is retired for dock sessions. The persisted
dock_sessions section is now TWO TIERS:

- LIVE tier: every OPEN session record, uncapped, full detail.
- HISTORY tier: every CLOSED session, compact form (identity +
  pid->session provenance digests), complete coverage, in the
  same section under "history".

Nothing is dropped by retention any more: the section's
dropped_total is the frozen historical count of evictions by the
retired rotation and must never grow again. The per-session
50-proposal bound stands untouched (SS12.36c). Malformed records
are still preserved as evidence. V1 sections still load.

Isolated owner; real persist round-trip (Program.save ->
persist_rest.load), in the pp2b test style.
"""
from __future__ import annotations

import glob
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from form.open import Program  # noqa: E402
from form import persist_rest  # noqa: E402
from form.dell_matrix import design_loop  # noqa: E402
from form.dell_matrix import dock_session as ds  # noqa: E402

RESULTS = []
OWNER = "DD37Roster"


def _rec(name, cond, detail=""):
    RESULTS.append((name, bool(cond), str(detail)[:220]))


def _cleanup(owner):
    base = os.path.join(os.path.dirname(__file__), "state")
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
    path = os.path.join(os.path.dirname(__file__), "state",
                        f"program_{owner}.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _entry(pid):
    return {"pid": pid, "ts": "2026-11-09T10:30:00Z", "task": "t",
            "reason": "r", "origin": "dock:x",
            "prompt_hash": "b" * 64, "prompt_summary": "s",
            "prompt_chars": 3, "snapshot_id": None, "model": "m"}


def _build_sessions(owner):
    """12 records, staggered started. Index 0 (oldest) OPEN,
    index 6 OPEN mid-window, the other 10 closed. One closed
    record (index 3) and the oldest open record carry proposal
    evidence entries."""
    recs = {}
    ids = []
    for i in range(12):
        r = ds.new_record(owner, f"s{i}", "fake", "m", "t",
                          f"snap{i}")
        r["started"] = f"2026-11-09T10:{i:02d}:00Z"
        if i not in (0, 6):
            r["closed"] = f"2026-11-09T11:{i:02d}:00Z"
        recs[r["session_id"]] = r
        ids.append(r["session_id"])
    ds.append_proposal(recs[ids[3]], _entry("dd37-arch-pid"))
    ds.append_proposal(recs[ids[0]], _entry("dd37-live-pid"))
    return recs, ids


def main() -> int:
    _cleanup(OWNER)
    try:
        recs, ids = _build_sessions(OWNER)
        open_ids = {ids[0], ids[6]}
        closed_ids = [i for i in ids if i not in open_ids]
        p = Program(OWNER)
        p.dock_sessions = dict(recs)
        p.save()
        st = _state(OWNER)
        sec = st["dock_sessions"]
        _rec("section is the two-tier version",
             sec.get("version") == 2, f"version={sec.get('version')}")
        _rec("live tier holds exactly the open sessions, full detail",
             set(sec.get("sessions", {})) == open_ids,
             f"live={sorted(sec.get('sessions', {}))}")
        hist = sec.get("history", {})
        _rec("history tier holds every closed session (coverage)",
             set(hist) == set(closed_ids),
             f"history={len(hist)} of {len(closed_ids)} closed")
        _rec("complete coverage across tiers: 12 of 12 accounted for",
             set(sec.get("sessions", {})) | set(hist)
             == set(ids))
        arch = hist.get(ids[3], {})
        aent = (arch.get("proposals") or [{}])[0]
        _rec("history records are compact (no prompt material)",
             "prompt_hash" not in aent
             and "prompt_summary" not in aent
             and "reason" not in aent,
             f"entry keys={sorted(aent)}")
        _rec("history keeps pid->session provenance digests",
             aent.get("pid") == "dd37-arch-pid"
             and arch.get("session_id") == ids[3])
        _rec("nothing dropped: dropped_total stays zero",
             sec.get("dropped_total") == 0,
             f"dropped_total={sec.get('dropped_total')}")

        p2 = persist_rest.load(OWNER, activate=False)
        _rec("all 12 sessions present after load",
             set(p2.dock_sessions) == set(ids),
             f"loaded={len(p2.dock_sessions)}")
        _rec("the oldest OPEN session survives (live tier uncapped)",
             ids[0] in p2.dock_sessions
             and p2.dock_sessions[ids[0]].get("closed") is None)
        _rec("loaded dropped_total is zero",
             p2.dock_sessions_dropped_total == 0,
             f"total={p2.dock_sessions_dropped_total}")
        # The provenance joins (repl._show_proposals /
        # design_loop.chain) read p.dock_sessions only: an
        # archived session's proposal must still resolve.
        chain = design_loop.chain(p2, "dd37-arch-pid")
        filed = chain.get("filed") or {}
        _rec("provenance join resolves an archived session",
             filed.get("session_id") == ids[3]
             and filed.get("subject") == "s3",
             f"filed={filed}")
        # Re-saving the loaded population changes nothing.
        p2.save()
        sec2 = _state(OWNER)["dock_sessions"]
        _rec("round-trip is stable (tiers + total unchanged)",
             set(sec2.get("sessions", {})) == open_ids
             and set(sec2.get("history", {})) == set(closed_ids)
             and sec2.get("dropped_total") == 0)

        # Malformed preservation under the new path.
        p3 = Program(OWNER)
        bad = ds.new_record(OWNER, "bad", "fake", "m", "t",
                            "snapbad")
        bad["started"] = "2026-11-09T12:00:00Z"
        bad["subject"] = 12345  # invalid: not a string
        p3.dock_sessions = dict(recs)
        p3.dock_sessions[bad["session_id"]] = bad
        p3.save()
        sec3 = _state(OWNER)["dock_sessions"]
        _rec("malformed record preserved as evidence, not dropped",
             bad["session_id"] in (sec3.get("malformed") or {})
             and sec3.get("dropped_total") == 0
             and set(sec3.get("sessions", {})) == open_ids
             and len(sec3.get("history", {})) == len(closed_ids),
             f"malformed={'malformed' in sec3}")

        # V1 sections still load, with complete coverage.
        p4 = Program(OWNER)
        p4.dock_sessions = dict(recs)
        p4.save()
        path = os.path.join(os.path.dirname(__file__), "state",
                            f"program_{OWNER}.json")
        st4 = _state(OWNER)
        st4["dock_sessions"] = {"version": 1,
                                "sessions": dict(recs)}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(st4, f)
        p5 = persist_rest.load(OWNER, activate=False)
        _rec("v1 section loads with all 12 sessions",
             set(p5.dock_sessions) == set(ids),
             f"loaded={len(p5.dock_sessions)}")

        # The 50-proposal bound stands (SS12.36c).
        rec = ds.new_record(OWNER, "s", "fake", "m", "t", "snap")
        for _ in range(51):
            ds.append_proposal(rec, _entry("dd37-x"))
        _rec("51st proposal entry still FIFO-drops, counted once",
             len(rec["proposals"]) == 50 and rec["dropped"] == 1,
             f"n={len(rec['proposals'])} "
             f"dropped={rec['dropped']}")
    finally:
        _cleanup(OWNER)
    failed = [r for r in RESULTS if not r[1]]
    for name, ok, detail in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'}  {name}"
              + (f"  [{detail}]" if detail and not ok else ""))
    print(f"dd37_roster: {len(RESULTS) - len(failed)}/"
          f"{len(RESULTS)} checks passed")
    return 1 if failed else 0


def smoke() -> bool:
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
