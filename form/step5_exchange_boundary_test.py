#!/usr/bin/env python3
"""STEP 5: Exchange as a coordinated state boundary — DAF-04/05/06.

Director Certification Audit 2026-10-31, order step 5. Pre-fix
probe (step5_probe.py on a60bb22) reproduced all three:
- DAF-04: 5 imports x 50 receipts left the first (still pending)
  proposal with 0/50 receipts on export; counter correctly 50.
- DAF-05: after save/load, the receipts dict iterates newest
  first; one more record_receipt evicted origin199 (newest)
  while origin000 (oldest) survived.
- DAF-06: with 200 live seed payloads, import 201 raised
  ExchangeError but a pending proposal remained DURABLE (after
  reload) without its seed record, re-exporting as a silent
  "reconstructed" packet with chain "".

Contract proven here (real Program + real writers; save stubbed
on the instance only where a leg isolates retention logic, the
AF34 discipline — reload legs always save/load for real):
1. Backpressure: the 5th 50-receipt import refuses BEFORE any
   mutation (proposals/receipts/seeds/counters byte-unchanged);
   the first proposal still exports 50/50, provenance original.
2. Provenance: an imported proposal whose receipts are later
   evicted by a direct flood refuses export (never a truncated
   chain presented as complete); the evictions stay counted.
3. Provenance survives save/load: import, real save, reload,
   export — receipts exact, no refusal.
4. Oldest-first after reload (receipts): origin000 is the
   victim, origin199 survives, counter +1 exactly.
5. Oldest-first seed victim after reload: the oldest NON-LIVE
   payload is evicted, a newer non-live and all live survive.
6. Sibling writers (DAF-05 class sweep): design_loop and
   director_records evict their oldest by (ts, insertion order) after
   a reload, not the dict-first (newest) entry.
7. Seed-capacity preflight: import into 200 live payloads
   raises with ZERO partial import in memory AND after reload.
8. Injected post-landing failure (seed recording raises after
   receipts landed) rolls back proposal + receipts + seed in
   memory AND durably (reload shows no trace).
9. Damaged import marker: an exchange-origin proposal with no
   seed record refuses export; a native proposal still exports
   as provenance=reconstructed.
10. Legacy seed entries (no provenance pair) still validate,
    load, and export their seed byte-identical.
"""
import glob
import json
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


def _packet(i, nreceipts):
    return {
        "version": 1,
        "seed": {"label": f"s5-label-{i}", "chain": f"chain-{i}",
                 "keep": f"KEEP-{i}"},
        "manifest": {"author_origin": "s5:origin",
                     "created": "2026-10-31T00:00:00Z",
                     "registry": "core1:00-50,core2:51-99",
                     "requirements": [f"req-{i}"]},
        "receipts": [{"origin": f"s5:org-{i}-{j}", "guess": "g",
                      "test_method": "m", "result": "r",
                      "mirror": "mi", "outcome": "o"}
                     for j in range(nreceipts)],
    }


def _receipt_entry(owner, pid, i):
    return {"entry_id": f"e{i:03d}", "owner": owner,
            "ts": f"2026-01-01T00:{i // 60:02d}:{i % 60:02d}Z",
            "pid": pid, "origin": f"origin{i:03d}", "guess": "g",
            "test_method": "m", "result": "r", "mirror": "mi",
            "outcome": "o"}


def main():
    from form.open import Program
    from form import persist_rest
    from form.dell_matrix import exchange
    from form.dell_matrix.exchange import ExchangeError

    receipt = {"origin": "s5:flood", "guess": "g", "test_method": "m",
               "result": "r", "mirror": "mi", "outcome": "o"}

    # --- 1: backpressure admission (DAF-04)
    owner = "Step5Adm"
    _cleanup(owner)
    p = Program(owner=owner)
    p.save = lambda *a, **k: ""
    p.nursery.save = lambda *a, **k: None
    pids = [exchange.import_packet(p, _packet(i, 50))["pid"]
            for i in range(4)]
    snap = (len(p.nursery.proposals), len(p.exchange_receipts),
            len(p.exchange_seeds),
            getattr(p, "exchange_receipts_dropped_total", 0))
    raised = False
    try:
        exchange.import_packet(p, _packet(4, 50))
    except ExchangeError:
        raised = True
    _rec("5th 50-receipt import refused (backpressure)", raised)
    _rec("refusal mutated nothing",
         (len(p.nursery.proposals), len(p.exchange_receipts),
          len(p.exchange_seeds),
          getattr(p, "exchange_receipts_dropped_total", 0)) == snap,
         f"snap={snap}")
    exp0 = exchange.build_packet(p, pids[0])
    _rec("first proposal exports 50/50 receipts, original",
         len(exp0["receipts"]) == 50
         and exp0["manifest"].get("provenance") == "original"
         and exp0["seed"] == _packet(0, 50)["seed"],
         f"n={len(exp0['receipts'])}")
    _cleanup(owner)

    # --- 2: provenance refusal after direct-flood eviction (DAF-04)
    owner = "Step5Prov"
    _cleanup(owner)
    p = Program(owner=owner)
    p.save = lambda *a, **k: ""
    p.nursery.save = lambda *a, **k: None
    victim_pid = exchange.import_packet(p, _packet("v", 3))["pid"]
    # The victim's receipts were recorded EARLIER than the flood:
    # receipt ts has 1s resolution, so stamp that age explicitly
    # rather than depend on uuid tie-breaking among same-second
    # entries (the policy itself is (ts, entry_id), DAF-05).
    for e in p.exchange_receipts.values():
        if e["pid"] == victim_pid:
            e["ts"] = "2026-01-01T00:00:00Z"
    flood_pid = p.nursery.add("s5-flood", words="w").id
    for _ in range(205):
        exchange.record_receipt(p, flood_pid, receipt)
    _rec("flood evicted the imported receipts (oldest-first)",
         len(exchange.receipts_for(p, victim_pid)) == 0
         and getattr(p, "exchange_receipts_dropped_total", 0) == 8,
         f"dropped={getattr(p, 'exchange_receipts_dropped_total', None)}")
    raised = False
    try:
        exchange.build_packet(p, victim_pid)
    except ExchangeError:
        raised = True
    _rec("incomplete provenance refuses export", raised)
    ok_override = exchange.build_packet(
        p, victim_pid, receipts=[])  # explicit override: deliberate
    _rec("explicit receipts override still exports",
         ok_override["receipts"] == [])
    _cleanup(owner)

    # --- 3+4: provenance + oldest-first across real save/load
    owner = "Step5Load"
    _cleanup(owner)
    p = Program(owner=owner)
    imp = exchange.import_packet(p, _packet("L", 50))
    prop = p.nursery.add("s5-anchor", words="w")
    entries = {}
    for i in range(150):  # 50 imported + 150 crafted = cap 200
        e = _receipt_entry(owner, prop.id, i)
        entries[e["entry_id"]] = e
    p.exchange_receipts.update(entries)
    p.save()
    p2 = persist_rest.load(owner, activate=False)
    exp = exchange.build_packet(p2, imp["pid"])
    _rec("provenance survives save/load (50/50 export)",
         len(exp["receipts"]) == 50
         and exp["seed"] == _packet("L", 50)["seed"],
         f"n={len(exp['receipts'])}")
    p2.save = lambda *a, **k: ""
    before = getattr(p2, "exchange_receipts_dropped_total", 0)
    exchange.record_receipt(p2, prop.id, receipt)
    origins = {e["origin"] for e in p2.exchange_receipts.values()}
    _rec("after reload the OLDEST receipt is evicted (DAF-05)",
         "origin000" not in origins and "origin149" in origins
         and len(exchange.receipts_for(p2, imp["pid"])) == 50,
         f"kept={len(origins)}")
    _rec("reload eviction counted exactly once",
         getattr(p2, "exchange_receipts_dropped_total", 0) == before + 1,
         f"{before} -> {getattr(p2, 'exchange_receipts_dropped_total', None)}")
    _cleanup(owner)

    # --- 5: oldest non-live seed victim after reload (DAF-05)
    owner = "Step5Seed"
    _cleanup(owner)
    p = Program(owner=owner)
    live_pid = p.nursery.add("s5-live", words="w").id
    exchange.record_seed_payload(p, live_pid, _packet("live", 0))
    orphans = []
    for i in range(199):
        opid = p.nursery.add(f"s5-orphan-{i}", words="w").id
        orphans.append(opid)
        exchange.record_seed_payload(p, opid, _packet(f"o{i}", 0))
    for opid in orphans:
        del p.nursery.proposals[opid]
    p.nursery.save()  # persist the departures: reload must agree
    # they have left, or every seed is (correctly) live-protected
    # Deterministic ts: oldest orphan is o0 by insertion; rewrite
    # ts so dict order cannot be the authority after reload.
    for i, opid in enumerate(orphans):
        for e in p.exchange_seeds.values():
            if e["pid"] == opid:
                e["ts"] = f"2026-02-01T00:{i // 60:02d}:{i % 60:02d}Z"
    for e in p.exchange_seeds.values():
        if e["pid"] == live_pid:
            e["ts"] = "2026-01-01T00:00:00Z"  # live AND oldest: protected
    p.save()
    p2 = persist_rest.load(owner, activate=False)
    p2.save = lambda *a, **k: ""
    p2.nursery.save = lambda *a, **k: None
    newpid = p2.nursery.add("s5-new", words="w").id
    exchange.record_seed_payload(p2, newpid, _packet("new", 0))
    _rec("seed victim is oldest NON-LIVE after reload",
         exchange.seed_payload_for(p2, orphans[0]) is None
         and exchange.seed_payload_for(p2, orphans[1]) is not None
         and exchange.seed_payload_for(p2, live_pid) is not None
         and len(p2.exchange_seeds) == 200,
         f"kept={len(p2.exchange_seeds)}")
    _cleanup(owner)

    # --- 6: sibling writers after reload (DAF-05 class sweep)
    owner = "Step5Sib"
    _cleanup(owner)
    p = Program(owner=owner)
    anchor = p.nursery.add("s5-sib", words="w").id
    from form.dell_matrix import design_loop, director_records
    dle = {}
    for i in range(200):
        e = {"entry_id": f"d{i:03d}", "owner": owner,
             "ts": f"2026-03-01T00:{i // 60:02d}:{i % 60:02d}Z",
             "pid": anchor, "event": "filed", "actor": "s5",
             "note": f"n{i}", "pr": 0, "merge_sha": ""}
        dle[e["entry_id"]] = e
    p.design_loop = dle
    dre = {}
    for i in range(200):
        e = director_records.new_entry(owner, "sess", "subj",
                                       "recommendation",
                                       pid=anchor, decision="accept",
                                       reason="s5", note=f"n{i}")
        e["entry_id"] = f"r{i:03d}"
        e["ts"] = f"2026-03-01T00:{i // 60:02d}:{i % 60:02d}Z"
        dre[e["entry_id"]] = e
    p.director_records = dre
    p.save()
    p2 = persist_rest.load(owner, activate=False)
    p2.save = lambda *a, **k: ""
    design_loop.record_event(p2, anchor, "filed", actor="s5",
                             note="newest")
    _rec("design_loop evicts oldest after reload",
         "d000" not in p2.design_loop and "d199" in p2.design_loop
         and getattr(p2, "design_loop_dropped_total", 0) == 1,
         f"total={getattr(p2, 'design_loop_dropped_total', None)}")
    from form.dell_matrix.director_session import bind_director
    ds = bind_director(p2)
    ds.recommend(anchor, "accept", "s5 sweep")
    ds.undock()
    _rec("director_records evicts oldest after reload",
         "r000" not in p2.director_records
         and "r199" in p2.director_records
         and getattr(p2, "director_records_dropped_total", 0) == 1,
         f"total={getattr(p2, 'director_records_dropped_total', None)}")
    _cleanup(owner)

    # --- 7: seed-capacity preflight, zero partial (DAF-06)
    owner = "Step5Full"
    _cleanup(owner)
    p = Program(owner=owner)
    p.save = lambda *a, **k: ""
    for i in range(200):
        lp = p.nursery.add(f"s5-full-{i}", words="w").id
        exchange.record_seed_payload(p, lp, _packet(i, 0),
                                     _defer_save=True)
    raised = False
    try:
        exchange.import_packet(p, _packet("victim", 1))
    except ExchangeError:
        raised = True
    in_mem = [pr for pr in p.nursery.proposals.values()
              if pr.label == "s5-label-victim"]
    p3 = persist_rest.load(owner, activate=False)
    durable = [pr for pr in p3.nursery.proposals.values()
               if pr.label == "s5-label-victim"]
    _rec("full-seeds import raises", raised)
    _rec("no partial import in memory or durable after reload",
         in_mem == [] and durable == []
         and len(getattr(p, "exchange_receipts", {}) or {}) == 0,
         f"mem={len(in_mem)} durable={len(durable)}")
    _cleanup(owner)

    # --- 8: injected post-landing failure rolls back (DAF-06)
    owner = "Step5Inj"
    _cleanup(owner)
    p = Program(owner=owner)
    p.save = lambda *a, **k: ""
    orig = exchange.record_seed_payload

    def boom(program, pid, packet, _defer_save=False):
        raise ExchangeError("injected seed failure")

    exchange.record_seed_payload = boom
    try:
        raised = False
        try:
            exchange.import_packet(p, _packet("inj", 2))
        except ExchangeError:
            raised = True
    finally:
        exchange.record_seed_payload = orig
    in_mem = [pr for pr in p.nursery.proposals.values()
              if pr.label == "s5-label-inj"]
    p3 = persist_rest.load(owner, activate=False)
    durable = [pr for pr in p3.nursery.proposals.values()
               if pr.label == "s5-label-inj"]
    _rec("injected failure raises and rolls back everywhere",
         raised and in_mem == [] and durable == []
         and len(getattr(p, "exchange_receipts", {}) or {}) == 0
         and len(getattr(p, "exchange_seeds", {}) or {}) == 0,
         f"mem={len(in_mem)} durable={len(durable)}")
    ok = exchange.import_packet(p, _packet("inj", 2))
    _rec("same import succeeds after the fault clears",
         ok.get("ok") is True
         and len(exchange.receipts_for(p, ok["pid"])) == 2)
    _cleanup(owner)

    # --- 9: damaged-import marker vs native (DAF-06)
    owner = "Step5Mark"
    _cleanup(owner)
    p = Program(owner=owner)
    p.save = lambda *a, **k: ""
    p.nursery.save = lambda *a, **k: None
    dmg = p.nursery.add("s5-dmg", words="w",
                        origin="exchange:s5:origin").id
    raised = False
    try:
        exchange.build_packet(p, dmg)
    except ExchangeError:
        raised = True
    _rec("exchange-origin without seed record refuses export", raised)
    nat = p.nursery.add("s5-native", words="w", origin="host:s5").id
    nat_pkt = exchange.build_packet(p, nat)
    _rec("native proposal still exports as reconstructed",
         nat_pkt["manifest"].get("provenance") == "reconstructed")
    _cleanup(owner)

    # --- 10: legacy seed entry (no provenance) stays valid
    owner = "Step5Leg"
    _cleanup(owner)
    p = Program(owner=owner)
    p.save = lambda *a, **k: ""
    p.nursery.save = lambda *a, **k: None
    pid = p.nursery.add("s5-legacy", words="w").id
    exchange.record_seed_payload(p, pid, _packet("leg", 0))
    for e in p.exchange_seeds.values():
        e.pop("receipts_expected", None)
        e.pop("receipts_hash", None)
    ok, _why = exchange._validate_seed_entry(
        next(iter(p.exchange_seeds.values())), owner)
    leg_pkt = exchange.build_packet(p, pid)
    _rec("legacy seed entry validates and exports byte-identical",
         ok and leg_pkt["seed"] == _packet("leg", 0)["seed"]
         and leg_pkt["manifest"].get("provenance") == "original")
    _cleanup(owner)

    leftovers = []
    base = os.path.join("form", "state")
    if os.path.isdir(base):
        leftovers = [f for f in os.listdir(base) if "Step5" in f]
    _rec("cleanup leaves no residue", leftovers == [], str(leftovers))

    passed = sum(1 for _, ok_, _ in RESULTS if ok_)
    for name, ok_, detail in RESULTS:
        if not ok_:
            print(f"FAIL {name}: {detail}")
    print(f"STEP5_EXCHANGE_BOUNDARY: {passed}/{len(RESULTS)}")
    return passed == len(RESULTS)


def smoke():
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
