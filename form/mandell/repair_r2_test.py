"""Director review repair R2 — Exchange receipt preservation.

Independent review (Mode D, 2026-10-27) declined PR #117:
import_packet accepted a packet carrying 50 receipts, silently
truncated them (they existed only as text inside the imported
proposal's 2000-char detail rendering), and re-export then
FAILED (build_packet sources keep from Proposal.detail, whose
2000-char bound exceeded the packet keep bound of 1000).

Fixed on the existing authorities:
* import records every packet receipt into the receiver's
  exchange_receipts section under the imported proposal, via
  the canonical record_receipt path — each receipt keeps its
  own origin (provenance is never rewritten to the receiver),
  so receipts_for and re-export see them all;
* the packet keep bound is 2000, aligned with the Nursery
  detail bound the keep is sourced from.
"""
from __future__ import annotations

import glob
import os
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from form.open import Program  # noqa: E402
from form.dell_matrix import exchange as ex  # noqa: E402

RESULTS = []


def _rec(name, cond, detail=""):
    RESULTS.append((name, bool(cond), str(detail)[:200]))


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


def _receipts(n):
    return [{
        "origin": f"lab:{i % 5}", "guess": f"guess {i}",
        "test_method": "count pulses", "result": f"result {i}",
        "mirror": "mirror matched", "outcome": "held",
    } for i in range(n)]


def smoke() -> bool:
    owners = ["RepairX1", "RepairX2", "RepairX3"]
    for o in owners:
        _cleanup(o)
    try:
        sender = Program(owner="RepairX1")
        prop = sender.nursery.add(
            "Counted Heart Trial", words="a keep about counting",
            detail="the heart of the trial", origin="host:RepairX1")
        packet = ex.build_packet(sender, prop.id,
                                 receipts=_receipts(50))
        _rec("packet_carries_50", len(packet["receipts"]) == 50)

        receiver = Program(owner="RepairX2")
        out = ex.import_packet(receiver, packet)
        _rec("import_ok", out.get("ok") is True, str(out))
        pid = out["pid"]
        landed = receiver.nursery.proposals[pid]
        _rec("import_stays_pending", landed.status == "pending",
             landed.status)
        stored = ex.receipts_for(receiver, pid)
        _rec("all_50_receipts_preserved", len(stored) == 50,
             f"stored={len(stored)}")
        _rec("receipt_origins_preserved",
             {e["origin"] for e in stored}
             == {f"lab:{i}" for i in range(5)}
             and all(e["origin"] != "host:RepairX2" for e in stored))

        again = ex.build_packet(receiver, pid)
        _rec("reexport_validates", isinstance(again, dict))
        _rec("reexport_carries_50", len(again["receipts"]) == 50,
             f"receipts={len(again['receipts'])}")
        _rec("reexport_distinct_origins",
             ex.lint_packet(again)["distinct_origins"] == 5)

        third = Program(owner="RepairX3")
        out3 = ex.import_packet(third, again)
        stored3 = ex.receipts_for(third, out3["pid"])
        _rec("second_generation_keeps_50", len(stored3) == 50,
             f"stored={len(stored3)}")

        # keep bound alignment: a local idea whose detail is
        # 1500 chars exports (pre-fix this raised in validate).
        big = sender.nursery.add("Long Keep Idea", words="w",
                                 detail="k" * 1500,
                                 origin="host:RepairX1")
        pkt_big = ex.build_packet(sender, big.id)
        _rec("long_detail_exports", len(pkt_big["seed"]["keep"]) == 1500)
        bad = dict(packet)
        bad_seed = dict(packet["seed"])
        bad_seed["keep"] = "k" * 2001
        bad = dict(packet, seed=bad_seed)
        try:
            ex.validate_packet(bad)
            _rec("keep_over_2000_refused", False, "no error raised")
        except ex.ExchangeError:
            _rec("keep_over_2000_refused", True)

        # zero-receipt packets still import (behavior unchanged)
        bare = ex.build_packet(sender, prop.id, receipts=[])
        out0 = ex.import_packet(receiver, bare)
        _rec("zero_receipt_import_unchanged", out0.get("ok") is True
             and ex.receipts_for(receiver, out0["pid"]) == [])
    finally:
        for o in owners:
            _cleanup(o)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'} {name} {detail}")
    print(f"repair_r2_test {passed}/{len(RESULTS)}")
    return passed == len(RESULTS)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
