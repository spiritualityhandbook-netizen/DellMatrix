#!/usr/bin/env python3
"""AF-3+AF-4: Exchange seed protection, provenance, writer counters.

Before this circuit (audit AF-3/AF-4, probe af34_probe.py on
4fb07b2):
- record_seed_payload evicted the OLDEST payload past the 200
  cap even when its proposal was still live in the Nursery;
  re-export of that proposal then silently degraded (rendered
  detail as Keep, chain "", requirements [], no flag).
- The four writer-side pop sites (exchange seeds, exchange
  receipts, design_loop events, director_records via
  DirectorSession._record) evicted WITHOUT incrementing the
  PP2b dropped_total counters; the counters only moved at the
  serialize boundary, which the writers' own trimming made
  unreachable — serialized dropped_total stayed 0 while
  records were lost.

Contract proven here (real Program + real writer functions;
Program.save stubbed on the instance ONLY to isolate retention
logic from AF-6 full-save cost, exactly as the probe did —
every writer treats save as best-effort, and the serialize leg
unstubs and saves for real):
1. Seeds: a payload whose pid is live in the Nursery is never
   evicted; true overflow (all retained payloads live) raises
   ExchangeError and stores nothing new.
2. Seeds: a payload whose proposal has left the Nursery IS
   evictable (oldest first) and the eviction is counted.
3. Provenance: build_packet marks the manifest "original" when
   the seed comes from the stored payload and "reconstructed"
   when it falls back to the rendered/native source.
4. Provenance validation is back-compatible: packets without
   the flag validate, packets with a valid flag validate, a
   bogus flag is refused.
5. Receipts: 205 records keep 200 and count 5 at write time.
6. Design loop: 205 events keep 200 and count 5 at write time.
7. Director records: 205 records keep 200 and count 5.
8. Serialize + reload: the file totals equal the writer counts
   EXACTLY (no double counting at the persistence boundary)
   and the totals survive reload.
9. Import regression: a legacy packet (no provenance flag)
   imports, and its re-export is byte-identical in seed +
   requirements and now flagged "original".
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


def _packet(i):
    return {
        "version": 1,
        "seed": {"label": f"orig-label-{i}", "chain": f"chain-{i}",
                 "keep": f"ORIGINAL-KEEP-{i}"},
        "manifest": {"author_origin": "af34:origin",
                     "created": "2026-10-30T00:00:00Z",
                     "registry": "core1:00-50,core2:51-99",
                     "requirements": [f"req-{i}"]},
        "receipts": [],
    }


def main():
    from form.open import Program
    from form.dell_matrix import design_loop, exchange
    from form.dell_matrix.exchange import ExchangeError

    owner = "AF34Suite"
    _cleanup(owner)
    p = Program(owner=owner)
    p.save = lambda *a, **k: ""           # AF-6 isolation, see header
    p.nursery.save = lambda *a, **k: None

    def add_prop(i):
        return p.nursery.add(f"af34-prop-{i}", words=f"words-{i}",
                             detail=f"RENDERED-DETAIL-{i}").id

    # --- 1+2: seed protection, evictable non-live, counted
    orphan = add_prop("orphan")
    exchange.record_seed_payload(p, orphan, _packet("orphan"))
    del p.nursery.proposals[orphan]       # proposal leaves the Nursery
    live_pids = []
    for i in range(200):
        pid = add_prop(i)
        live_pids.append(pid)
        exchange.record_seed_payload(p, pid, _packet(i))
    _rec("non-live payload evicted past cap",
         exchange.seed_payload_for(p, orphan) is None
         and len(p.exchange_seeds) == 200,
         f"kept={len(p.exchange_seeds)}")
    _rec("seed eviction counted at write time",
         getattr(p, "exchange_seeds_dropped_total", None) == 1,
         f"total={getattr(p, 'exchange_seeds_dropped_total', None)}")
    _rec("all live payloads retained",
         all(exchange.seed_payload_for(p, pid) is not None
             for pid in live_pids))
    extra = add_prop("extra")
    raised = False
    try:
        exchange.record_seed_payload(p, extra, _packet("extra"))
    except ExchangeError:
        raised = True
    _rec("true overflow raises ExchangeError (fail-closed)",
         raised)
    _rec("overflow stores nothing and evicts nothing",
         len(p.exchange_seeds) == 200
         and exchange.seed_payload_for(p, extra) is None
         and exchange.seed_payload_for(p, live_pids[0]) is not None
         and getattr(p, "exchange_seeds_dropped_total", None) == 1,
         f"kept={len(p.exchange_seeds)}")

    # --- 3+4: provenance flag + validation back-compat
    pkt_orig = exchange.build_packet(p, live_pids[0])
    _rec("stored seed exports as provenance=original",
         pkt_orig["manifest"].get("provenance") == "original",
         f"manifest={sorted(pkt_orig['manifest'])}")
    _rec("original export is byte-identical",
         pkt_orig["seed"] == _packet(0)["seed"]
         and pkt_orig["manifest"]["requirements"] == ["req-0"])
    native = add_prop("native")
    pkt_nat = exchange.build_packet(p, native)
    _rec("native seed exports as provenance=reconstructed",
         pkt_nat["manifest"].get("provenance") == "reconstructed",
         f"prov={pkt_nat['manifest'].get('provenance')}")
    legacy = _packet("legacy")
    try:
        exchange.validate_packet(legacy)
        legacy_ok = True
    except ExchangeError:
        legacy_ok = False
    _rec("legacy packet without flag validates", legacy_ok)
    flagged = _packet("flagged")
    flagged["manifest"]["provenance"] = "original"
    try:
        out = exchange.validate_packet(flagged)
        flag_ok = out["manifest"].get("provenance") == "original"
    except ExchangeError:
        flag_ok = False
    _rec("packet with valid flag validates and keeps it", flag_ok)
    bogus = _packet("bogus")
    bogus["manifest"]["provenance"] = "immaculate"
    try:
        exchange.validate_packet(bogus)
        bogus_ok = True
    except ExchangeError:
        bogus_ok = False
    _rec("bogus provenance flag refused", not bogus_ok)

    # --- 5: receipts counter at write time
    receipt = {"origin": "af34:origin", "guess": "g",
               "test_method": "m", "result": "r", "mirror": "mi",
               "outcome": "o"}
    first_rid = None
    for _ in range(205):
        e = exchange.record_receipt(p, live_pids[-1], receipt)
        if first_rid is None:
            first_rid = e["entry_id"]
    _rec("receipts keep 200, count 5 at write time",
         len(p.exchange_receipts) == 200
         and first_rid not in p.exchange_receipts
         and getattr(p, "exchange_receipts_dropped_total", None) == 5,
         f"kept={len(p.exchange_receipts)} "
         f"total={getattr(p, 'exchange_receipts_dropped_total', None)}")

    # --- 6: design_loop counter at write time
    for i in range(205):
        design_loop.record_event(p, live_pids[-1], "filed",
                                 actor="af34", note=f"n{i}")
    _rec("design_loop keeps 200, counts 5 at write time",
         len(p.design_loop) == 200
         and getattr(p, "design_loop_dropped_total", None) == 5,
         f"kept={len(p.design_loop)} "
         f"total={getattr(p, 'design_loop_dropped_total', None)}")

    # --- 7: director_records counter at write time
    from form.dell_matrix.director_session import bind_director
    ds = bind_director(p)
    for _ in range(205):
        ds.recommend(live_pids[-1], "accept", "af34 counter check")
    _rec("director_records keep 200, count 5 at write time",
         len(p.director_records) == 200
         and getattr(p, "director_records_dropped_total", None) == 5,
         f"kept={len(p.director_records)} "
         f"total={getattr(p, 'director_records_dropped_total', None)}")
    ds.undock()

    # --- 9: import leg on its own program (the store above is
    # deliberately full of live payloads, where a new import
    # must now fail closed instead of evicting an original)
    owner2 = "AF34Imp"
    _cleanup(owner2)
    p_imp = Program(owner=owner2)
    p_imp.save = lambda *a, **k: ""
    p_imp.nursery.save = lambda *a, **k: None
    imp = exchange.import_packet(p_imp, _packet("imported"))
    _rec("legacy packet imports", imp.get("ok") is True, str(imp)[:120])
    if imp.get("ok"):
        re_exp = exchange.build_packet(p_imp, imp["pid"])
        _rec("imported re-export byte-identical + original",
             re_exp["seed"] == _packet("imported")["seed"]
             and re_exp["manifest"]["requirements"] == ["req-imported"]
             and re_exp["manifest"].get("provenance") == "original")
    _cleanup(owner2)

    # --- 8: serialize once for real; totals exact, survive reload
    del p.save
    if hasattr(p.nursery, "save"):
        try:
            del p.nursery.save
        except AttributeError:
            pass
    p.save()
    state_path = os.path.join("form", "state", f"program_{owner}.json")
    with open(state_path, encoding="utf-8") as f:
        st = json.load(f)
    ser = {k: (st.get(k) or {}).get("dropped_total")
           for k in ("exchange_seeds", "exchange_receipts",
                     "design_loop", "director_records")}
    _rec("serialized totals equal writer counts (no double count)",
         ser == {"exchange_seeds": 1, "exchange_receipts": 5,
                 "design_loop": 5, "director_records": 5},
         f"ser={ser}")
    from form import persist_rest
    p2 = persist_rest.load(owner, activate=False)
    _rec("totals survive reload",
         getattr(p2, "exchange_seeds_dropped_total", None) == 1
         and getattr(p2, "exchange_receipts_dropped_total", None) == 5
         and getattr(p2, "design_loop_dropped_total", None) == 5
         and getattr(p2, "director_records_dropped_total", None) == 5,
         f"{getattr(p2, 'exchange_seeds_dropped_total', None)}/"
         f"{getattr(p2, 'exchange_receipts_dropped_total', None)}/"
         f"{getattr(p2, 'design_loop_dropped_total', None)}/"
         f"{getattr(p2, 'director_records_dropped_total', None)}")

    _cleanup(owner)
    leftover = [f for f in os.listdir(os.path.join("form", "state"))
                if owner in f] \
        if os.path.isdir(os.path.join("form", "state")) else []
    _rec("cleanup leaves no residue", leftover == [], str(leftover))

    passed = sum(1 for _, ok_, _ in RESULTS if ok_)
    for name, ok_, detail in RESULTS:
        if not ok_:
            print(f"FAIL {name}: {detail}")
    print(f"AF34_EXCHANGE_COUNTERS: {passed}/{len(RESULTS)}")
    return passed == len(RESULTS)


def smoke():
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
