#!/usr/bin/env python3
"""AF-5: session bounds for traces / snapshots / tx frames.

Before this circuit (audit AF-5, probe af5_probe.py on ee3544f):
130 Sets grew traces to 130 AND snapshots to 130 (a full snap()
per store write); Dell 90's result cell copied the whole traces
list per call; 12 Try/Commit cycles retained all 12 terminal tx
frames forever; no dropped counter existed anywhere. All three
collections are session-only (none in CORE_II_DURABLE), so the
growth was unbounded within a session and invisible.

Contract proven here (real Program, public execute_seed path,
per-owner isolation, loud cleanup):
1. Counters exist on a fresh state and start at 0:
   traces_dropped_total / snapshots_dropped_total /
   tx_dropped_total.
2. Traces cap 512, oldest trimmed at mark(): 600 Sets retain
   the newest 512 traces, count 88 dropped, keep ALL 600 store
   keys (the bound trims the evidence trail, never the store).
3. Snapshots cap 64, oldest (bottom) trimmed: 600 Sets retain
   64 snapshots and count 536 dropped.
4. Dell 90 Trace result cell is bounded by the cap: value and
   count are 512 after the flood; executing Trace itself is
   also bounded (still 512 retained, dropped advances to 89).
5. Revert still consumes the TOP snapshot after bottom-trim:
   it restores the pre-last-Set store (k599 gone, k598 kept)
   and the retained count drops 64 -> 63.
6. Tx pruning keeps the newest 16 TERMINAL frames plus ALL
   active frames: 20 Try/Commit cycles retain exactly 16
   frames (ids tx4..tx19), count 4 dropped, and frame ids stay
   monotonic (the 21st Try is tx20, never a reused id).
7. Refusal identity survives pruning: Commit with no active
   frame on a committed newest frame is commit_illegal (not
   commit_without_try), and Revert on it is unrelated_revert.
8. Active frames are never pruned: 20 nested open Trys are
   all retained on top of the 16 terminal frames.
9. The DeltaFlow checkpoint site (chain_exec) goes through
   the same snapshot bound: a 70-checkpoint chain retains 64
   snapshots and counts 6 dropped on a fresh program.
10. Counters are session-only truth: none of the three
    counters (or collections) is in CORE_II_DURABLE or in the
    serialized blob — a durable counter would false-witness
    session loss across a reload.
"""
import glob
import os
import shutil

RESULTS = []


def _rec(name, cond, detail=""):
    RESULTS.append((name, bool(cond), str(detail)[:220]))


def _cleanup(owner):
    base = os.path.join("form", "state")
    if not os.path.isdir(base):
        return
    for pat in (f"program_{owner}.json", f"nursery_{owner}.json",
                f"checkpoint_{owner}_*", f"confirm_{owner}.journal.json",
                f"checkpoint_{owner}.journal.json",
                f"gen_{owner}_*", f"current_{owner}.json"):
        for f in glob.glob(os.path.join(base, pat)):
            os.remove(f)
    for d in glob.glob(os.path.join(base, f"ideas_{owner}*")):
        if os.path.isdir(d):
            shutil.rmtree(d)


def main():
    from form.open import Program
    from form.mandell.executor import execute_seed
    from form.mandell.core_ii_exec import attach

    owner = "AF5Bounds"
    _cleanup(owner)
    p = Program(owner=owner)
    st = attach(p)

    # --- 1: counters exist and start at 0
    _rec("counters start at 0",
         getattr(st, "traces_dropped_total", None) == 0
         and getattr(st, "snapshots_dropped_total", None) == 0
         and getattr(st, "tx_dropped_total", None) == 0,
         f"{getattr(st, 'traces_dropped_total', None)}/"
         f"{getattr(st, 'snapshots_dropped_total', None)}/"
         f"{getattr(st, 'tx_dropped_total', None)}")

    # --- 2+3: 600 Sets flood traces and snapshots
    for i in range(600):
        r = execute_seed(p, f"55[Set] :: k{i}={i}")
        assert r.get("ok"), r
    _rec("traces capped at 512, newest retained",
         len(st.traces) == 512 and "k88" in st.traces[0]
         and "k599" in st.traces[-1],
         f"len={len(st.traces)} first={st.traces[:1]} last={st.traces[-1:]}")
    _rec("traces dropped counted 88",
         st.traces_dropped_total == 88, str(st.traces_dropped_total))
    _rec("snapshots capped at 64",
         len(st.snapshots) == 64, str(len(st.snapshots)))
    _rec("snapshots dropped counted 536",
         st.snapshots_dropped_total == 536,
         str(st.snapshots_dropped_total))
    _rec("store untouched by bounds (600 keys)",
         len(st.store) == 600, str(len(st.store)))

    # --- 4: Trace result cell bounded; Trace execution bounded too
    r = execute_seed(p, "90[Trace]")
    cell = st.last_result or {}
    _rec("Trace cell bounded at cap",
         r.get("ok") and len(cell.get("value") or []) == 512
         and cell.get("count") == 512,
         f"value={len(cell.get('value') or [])} count={cell.get('count')}")
    _rec("Trace execution itself bounded (512 retained, 89 dropped)",
         len(st.traces) == 512 and st.traces_dropped_total == 89,
         f"len={len(st.traces)} dropped={st.traces_dropped_total}")

    # --- 5: Revert consumes the TOP snapshot after bottom-trim
    r = execute_seed(p, "96[Revert]")
    _rec("Revert pops top snapshot 64 -> 63",
         r.get("ok") and len(st.snapshots) == 63
         and any("Revert snapshot snapshots=63" in m
                 for m in r.get("messages", [])),
         f"len={len(st.snapshots)} msgs={r.get('messages')}")
    _rec("Revert restored pre-last-Set store",
         "k599" not in st.store and "k598" in st.store
         and len(st.store) == 599,
         f"len={len(st.store)}")

    # --- 6: tx pruning — 20 Try/Commit cycles
    for _ in range(20):
        assert execute_seed(p, "93[Try]").get("ok")
        assert execute_seed(p, "95[Commit]").get("ok")
    ids = [f.get("id") for f in st.tx]
    _rec("tx terminal frames capped at 16 (tx4..tx19)",
         len(st.tx) == 16 and ids == [f"tx{i}" for i in range(4, 20)],
         f"len={len(st.tx)} ids={ids[:3]}...{ids[-2:]}")
    _rec("tx dropped counted 4",
         st.tx_dropped_total == 4, str(st.tx_dropped_total))
    _rec("newest terminal frame retained (committed)",
         st.tx[-1].get("status") == "committed",
         str(st.tx[-1].get("status")))

    # --- 7: refusal identity survives pruning
    r = execute_seed(p, "95[Commit]")
    _rec("Commit after pruning is commit_illegal",
         r.get("ok") is False and r.get("error") == "commit_illegal",
         f"ok={r.get('ok')} err={r.get('error')}")
    r = execute_seed(p, "96[Revert]")
    _rec("Revert on committed newest is unrelated_revert",
         r.get("ok") is False and r.get("error") == "unrelated_revert",
         f"ok={r.get('ok')} err={r.get('error')}")

    # --- 6b: next Try id is monotonic, never reused after pruning
    r = execute_seed(p, "93[Try]")
    _rec("21st Try id is tx20 (monotonic)",
         r.get("ok") and st.tx[-1].get("id") == "tx20",
         f"id={st.tx[-1].get('id') if st.tx else None}")
    assert execute_seed(p, "95[Commit]").get("ok")

    # --- 8: active frames never pruned (20 nested open Trys)
    for _ in range(20):
        assert execute_seed(p, "93[Try]").get("ok")
    active = [f for f in st.tx if f.get("status") in ("open", "failed", "caught")]
    _rec("20 active frames retained above the terminal cap",
         len(active) == 20 and st.try_depth == 20
         and len(st.tx) == 16 + 20,
         f"active={len(active)} depth={st.try_depth} total={len(st.tx)}")

    _cleanup(owner)
    leftover = [f for f in os.listdir(os.path.join("form", "state"))
                if owner in f] \
        if os.path.isdir(os.path.join("form", "state")) else []
    _rec("cleanup leaves no residue (owner 1)", leftover == [], str(leftover))

    # --- 9: DeltaFlow checkpoint site bounded (fresh program)
    owner2 = "AF5Delta"
    _cleanup(owner2)
    p2 = Program(owner=owner2)
    st2 = attach(p2)
    chain = " <<[Delta] ".join(["70[Count]"] * 71)
    r = execute_seed(p2, chain)
    _rec("DeltaFlow snapshots capped at 64, 6 dropped",
         r.get("ok") and len(st2.snapshots) == 64
         and st2.snapshots_dropped_total == 6,
         f"ok={r.get('ok')} len={len(st2.snapshots)} "
         f"dropped={getattr(st2, 'snapshots_dropped_total', None)}")
    _cleanup(owner2)
    leftover = [f for f in os.listdir(os.path.join("form", "state"))
                if owner2 in f] \
        if os.path.isdir(os.path.join("form", "state")) else []
    _rec("cleanup leaves no residue (owner 2)", leftover == [], str(leftover))

    # --- 10: counters + collections are session-only
    from form.persist_core_ii import serialize_core_ii, CORE_II_DURABLE
    blob = serialize_core_ii(p)
    names = ("traces_dropped_total", "snapshots_dropped_total",
             "tx_dropped_total", "traces", "snapshots", "tx")
    _rec("counters/collections not durable, not serialized",
         all(n not in CORE_II_DURABLE for n in names)
         and all(n not in blob for n in names),
         f"durable={list(CORE_II_DURABLE)} blob={sorted(blob.keys())}")

    passed = sum(1 for _, ok_, _ in RESULTS if ok_)
    for name, ok_, detail in RESULTS:
        if not ok_:
            print(f"FAIL {name}: {detail}")
    print(f"AF5_SESSION_BOUNDS: {passed}/{len(RESULTS)}")
    return passed == len(RESULTS)


def smoke():
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
