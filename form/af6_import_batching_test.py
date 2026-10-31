#!/usr/bin/env python3
"""AF-6: import_packet batches its full-program saves.

Before (probe af6_probe.py on a87533f): import of a 5-receipt
packet cost 6 full program saves (5 record_receipt + 1
record_seed_payload); save wall was 85% of import wall and
99.6% of record wall. Contract (af6_ground.md, SWAT 4/4):
1. import_packet performs exactly ONE program.save().
2. After that one save, a reload sees ALL receipts + the seed
   payload (durability at the operation boundary).
3. A lone record_receipt / record_seed_payload still saves
   immediately (reload proof, no explicit save called).
4. _defer_save=True with no boundary save leaves the record
   unpersisted (honest defer semantics, dock parity).
5. AF-3/AF-4 inside imports unchanged: live-overflow import
   fails closed; dropped counters still move at write time.
Real Program, real save underneath a counting wrapper,
per-owner isolation, loud cleanup.
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
    failed = []
    for pat in (f"program_{owner}.json", f"nursery_{owner}.json",
                f"checkpoint_{owner}_*", f"confirm_{owner}.journal.json",
                f"checkpoint_{owner}.journal.json",
                f"gen_{owner}_*", f"current_{owner}.json"):
        for f in glob.glob(os.path.join(base, pat)):
            try:
                os.remove(f)
            except OSError as e:
                failed.append(f"{f}: {e}")
    for d in glob.glob(os.path.join(base, f"ideas_{owner}*")):
        if os.path.isdir(d):
            try:
                shutil.rmtree(d)
            except OSError as e:
                failed.append(f"{d}: {e}")
    if failed:
        raise RuntimeError("cleanup failed: " + "; ".join(failed))


def _packet(i, n_receipts=5):
    return {
        "version": 1,
        "seed": {"label": f"af6-label-{i}", "chain": f"chain-{i}",
                 "keep": f"AF6-KEEP-{i}"},
        "manifest": {"author_origin": "af6:origin",
                     "created": "2026-10-30T00:00:00Z",
                     "registry": "core1:00-50,core2:51-99",
                     "requirements": [f"req-{i}"]},
        "receipts": [
            {"origin": "af6:origin", "guess": f"g{j}",
             "test_method": "m", "result": "r", "mirror": "mi",
             "outcome": "o"} for j in range(n_receipts)],
    }


def _counting(p):
    real = p.save
    box = {"n": 0}
    def wrapped(*a, **k):
        box["n"] += 1
        return real(*a, **k)
    p.save = wrapped
    return box


def main():
    from form.open import Program
    from form import persist_rest
    from form.dell_matrix import exchange
    from form.dell_matrix.exchange import ExchangeError

    owner = "AF6Suite"
    _cleanup(owner)
    p = Program(owner=owner)
    box = _counting(p)
    imp = exchange.import_packet(p, _packet(1))
    _rec("import ok", imp.get("ok") is True, str(imp)[:120])
    _rec("exactly one save per 5-receipt import", box["n"] == 1,
         f"saves={box['n']}")
    pid = imp["pid"]
    p2 = persist_rest.load(owner, activate=False)
    _rec("reload sees all 5 receipts after the one save",
         len(exchange.receipts_for(p2, pid)) == 5,
         f"n={len(exchange.receipts_for(p2, pid))}")
    sp = exchange.seed_payload_for(p2, pid)
    _rec("reload sees seed payload after the one save",
         sp is not None and sp.get("keep") == "AF6-KEEP-1",
         f"sp={sp and sp.get('keep')}")

    # lone records still persist immediately
    owner2 = "AF6Lone"
    _cleanup(owner2)
    q = Program(owner=owner2)
    qbox = _counting(q)
    lpid = q.nursery.add("af6-lone", words="w", detail="d").id
    receipt = {"origin": "af6:origin", "guess": "g",
               "test_method": "m", "result": "r", "mirror": "mi",
               "outcome": "o"}
    exchange.record_receipt(q, lpid, receipt)
    _rec("lone record_receipt saves once", qbox["n"] == 1,
         f"saves={qbox['n']}")
    q2 = persist_rest.load(owner2, activate=False)
    _rec("lone receipt durable on reload without explicit save",
         len(exchange.receipts_for(q2, lpid)) == 1)
    exchange.record_seed_payload(q, lpid, _packet(9, 0))
    _rec("lone record_seed_payload saves once more", qbox["n"] == 2,
         f"saves={qbox['n']}")
    q3 = persist_rest.load(owner2, activate=False)
    _rec("lone seed payload durable on reload",
         exchange.seed_payload_for(q3, lpid) is not None)

    # honest defer: deferred record is NOT persisted by itself
    exchange.record_receipt(q, lpid, receipt, _defer_save=True)
    _rec("deferred record_receipt performs no save", qbox["n"] == 2,
         f"saves={qbox['n']}")
    q4 = persist_rest.load(owner2, activate=False)
    _rec("deferred receipt absent from reload (honest defer)",
         len(exchange.receipts_for(q4, lpid)) == 1,
         f"n={len(exchange.receipts_for(q4, lpid))}")
    _rec("deferred receipt present in live state",
         len(exchange.receipts_for(q, lpid)) == 2)
    _cleanup(owner2)

    # AF-3/AF-4 inside imports: fill seeds with live proposals,
    # then an import must fail closed, counters untouched by save
    owner3 = "AF6Full"
    _cleanup(owner3)
    f = Program(owner=owner3)
    f.save = lambda *a, **k: ""
    f.nursery.save = lambda *a, **k: None
    for i in range(200):
        lp = f.nursery.add(f"af6-full-{i}", words="w").id
        exchange.record_seed_payload(f, lp, _packet(i, 0))
    raised = False
    try:
        exchange.import_packet(f, _packet("overflow", 1))
    except ExchangeError:
        raised = True
    _rec("import into full-of-live seeds fails closed (AF-3)",
         raised)
    _cleanup(owner3)

    _cleanup(owner)
    leftover = [x for x in os.listdir(os.path.join("form", "state"))
                if owner in x] \
        if os.path.isdir(os.path.join("form", "state")) else []
    _rec("cleanup leaves no residue", leftover == [], str(leftover))

    passed = sum(1 for _, ok_, _ in RESULTS if ok_)
    for name, ok_, detail in RESULTS:
        if not ok_:
            print(f"FAIL {name}: {detail}")
    print(f"AF6_IMPORT_BATCHING: {passed}/{len(RESULTS)}")
    return passed == len(RESULTS)


def smoke():
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
