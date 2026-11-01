"""DAF-06 durability follow-up (Director order step 5b).

The Director declined DAF-06 as complete at 4405479 with two
reproduced failures: (1) a failing final Program.save() still
returned ok=True, leaving a durable partial import (proposal
without its seed payload); (2) a seed-recording failure whose
rollback Nursery.save() also failed left the durable partial
proposal in place while the rollback exception was suppressed
and incomplete compensation went unreported.

Contract proven here:
- an import is a journaled transaction: intent is recorded
  before landing and retained until the import is proven
  complete or proven compensated;
- a required durable save failing NEVER returns ordinary
  success; the ExchangeError carries the compensation state;
- incomplete compensation is observable (error details + the
  retained journal) and a restart (persist_rest.load) resolves
  the journaled partial import BEFORE state is exposed;
- after a resolved failure the same packet imports cleanly
  (successful-retry controls);
- AF6 batching is kept (one final program save per import);
- the damaged-import export refusal is preserved, and
  unjournaled state is never touched by recovery.

Labels: INTEGRATION (real Program/Nursery/persist paths,
injected save/recording failures, separate load instances).
"""
from __future__ import annotations

import glob
import json
import os
import shutil
import sys

RESULTS: list = []


def _rec(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, bool(ok), detail))


def _cleanup(owner: str) -> None:
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "state")
    if not os.path.isdir(base):
        return
    names = []
    for pat in (f"program_{owner}.json", f"nursery_{owner}.json",
                f"checkpoint_{owner}_*", f"confirm_{owner}.journal.json",
                f"checkpoint_{owner}.journal.json", f"gen_{owner}_*",
                f"current_{owner}.json",
                f"exchange_import_{owner}.journal.json"):
        names.extend(glob.glob(os.path.join(base, pat)))
    errors = []
    for name in names:
        try:
            os.remove(name)
        except OSError as e:
            errors.append(f"{name}: {e}")
    for d in glob.glob(os.path.join(base, f"ideas_{owner}*")):
        if os.path.isdir(d):
            try:
                shutil.rmtree(d)
            except OSError as e:
                errors.append(f"{d}: {e}")
    if errors:
        raise RuntimeError(
            f"cleanup failed for owner {owner}: {errors}")


def _packet(tag):
    return {
        "version": 1,
        "seed": {"label": f"s5b-label-{tag}", "chain": f"chain-{tag}",
                 "keep": f"S5B-KEEP-{tag}"},
        "manifest": {"author_origin": "s5b:origin",
                     "created": "2026-10-31T00:00:00Z",
                     "registry": "core1:00-50,core2:51-99",
                     "requirements": [f"req-{tag}"]},
        "receipts": [
            {"origin": "s5b:org", "guess": f"g{j}",
             "test_method": "m", "result": "r", "mirror": "mi",
             "outcome": "o"} for j in range(2)],
    }


def _journal_path(owner):
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "state")
    return os.path.join(base, f"exchange_import_{owner}.journal.json")


def _journal(owner):
    path = _journal_path(owner)
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _raw_nursery_ids(owner):
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "state")
    path = os.path.join(base, f"nursery_{owner}.json")
    if not os.path.isfile(path):
        return set()
    with open(path, encoding="utf-8") as f:
        return {k for k in json.load(f)
                if not k.startswith("__")}


def main() -> bool:
    from form.open import Program
    from form import persist_rest
    from form.dell_matrix import exchange
    from form.dell_matrix.exchange import ExchangeError

    def dead_save(*a, **k):
        raise RuntimeError("injected save failure")

    # ---- 1. F1: final Program.save() raises -> NO ok=True;
    # compensation is verified durable -> journal cleared;
    # reload exposes no trace of the import.
    owner = "Step5bFinalSave"
    _cleanup(owner)
    p = Program(owner=owner)
    p.save = dead_save
    err = None
    try:
        exchange.import_packet(p, _packet("one"))
    except ExchangeError as e:
        err = e
    _rec("F1: final-save failure raises (never ok=True)", err is not None)
    _rec("F1: error names the final-save stage",
         err is not None
         and err.details.get("stage") == "final_save",
         str(err and err.details))
    _rec("F1: compensation verified complete",
         err is not None
         and err.details.get("compensation") == "complete",
         str(err and err.details))
    _rec("F1: journal cleared after proven compensation",
         _journal(owner) is None)
    p2 = persist_rest.load(owner, activate=False)
    _rec("F1: reload has no partial proposal",
         all(pr.label != "s5b-label-one"
             for pr in p2.nursery.proposals.values()))
    # retry control: the same packet imports cleanly afterwards
    p3 = persist_rest.load(owner, activate=False)
    imp = exchange.import_packet(p3, _packet("one"))
    _rec("F1: retry after resolved failure succeeds",
         imp.get("ok") is True)
    p4 = persist_rest.load(owner, activate=False)
    sp = exchange.seed_payload_for(p4, imp["pid"])
    _rec("F1: retry is durable (seed + receipts exact)",
         sp is not None and sp.get("keep") == "S5B-KEEP-one"
         and len(exchange.receipts_for(p4, imp["pid"])) == 2)
    _cleanup(owner)

    # ---- 2. F2: seed recording fails AND rollback nursery.save
    # fails -> incomplete compensation is OBSERVABLE (details +
    # retained journal); restart resolves before exposure.
    owner = "Step5bRollback"
    _cleanup(owner)
    p = Program(owner=owner)
    orig_seed = exchange.record_seed_payload

    def boom_seed(program, pid, pkt, _defer_save=False):
        raise ExchangeError("injected seed failure")

    real_nsave = p.nursery.save
    calls = {"n": 0}

    def flaky_nsave(*a, **k):
        calls["n"] += 1
        if calls["n"] > 1:
            raise RuntimeError("injected rollback nursery failure")
        return real_nsave(*a, **k)

    p.nursery.save = flaky_nsave
    exchange.record_seed_payload = boom_seed
    err = None
    try:
        exchange.import_packet(p, _packet("two"))
    except ExchangeError as e:
        err = e
    finally:
        exchange.record_seed_payload = orig_seed
        try:
            del p.nursery.save
        except AttributeError:
            pass
    _rec("F2: import raises", err is not None)
    _rec("F2: incomplete compensation reported in details",
         err is not None
         and err.details.get("compensation") == "incomplete"
         and err.details.get("journal_retained") is True,
         str(err and err.details))
    _rec("F2: memory rolled back (no proposal in memory)",
         all(pr.label != "s5b-label-two"
             for pr in p.nursery.proposals.values()))
    j = _journal(owner)
    _rec("F2: journal retained as compensation_incomplete",
         j is not None
         and j.get("status") == "compensation_incomplete"
         and j.get("pid"),
         str(j and {k: j.get(k) for k in ("status", "pid")}))
    _rec("F2: durable partial still on disk before restart",
         j is not None and j.get("pid") in _raw_nursery_ids(owner),
         f"pid={j and j.get('pid')}")
    # restart: load-boundary recovery resolves the journal first
    p2 = persist_rest.load(owner, activate=False)
    _rec("F2: restart removes the partial before exposure",
         all(pr.label != "s5b-label-two"
             for pr in p2.nursery.proposals.values()))
    _rec("F2: journal cleared by recovery", _journal(owner) is None)
    # retry control on the recovered program
    imp = exchange.import_packet(p2, _packet("two"))
    _rec("F2: retry after recovery succeeds", imp.get("ok") is True)
    p5 = persist_rest.load(owner, activate=False)
    sp = exchange.seed_payload_for(p5, imp["pid"])
    _rec("F2: retry durable with original provenance",
         sp is not None and sp.get("keep") == "S5B-KEEP-two"
         and sp.get("author_origin") == "s5b:origin"
         and len(exchange.receipts_for(p5, imp["pid"])) == 2)
    out = exchange.build_packet(p5, imp["pid"])
    _rec("F2: retried import exports cleanly",
         out["seed"]["keep"] == "S5B-KEEP-two")
    _cleanup(owner)

    # ---- 3. Happy path: AF6 batching kept, journal transient.
    owner = "Step5bHappy"
    _cleanup(owner)
    p = Program(owner=owner)
    real_save = p.save
    box = {"n": 0}

    def counting(*a, **k):
        box["n"] += 1
        return real_save(*a, **k)

    p.save = counting
    imp = exchange.import_packet(p, _packet("three"))
    _rec("happy: import ok with exactly one program save (AF6)",
         imp.get("ok") is True and box["n"] == 1,
         f"saves={box['n']}")
    _rec("happy: no journal remains after success",
         _journal(owner) is None)
    _cleanup(owner)

    # ---- 4. Damaged-import marker preserved: an unjournaled
    # exchange-origin proposal without a seed record is NOT
    # touched by recovery and its export stays refused.
    owner = "Step5bDamaged"
    _cleanup(owner)
    p = Program(owner=owner)
    dmg = p.nursery.add("dmg-label", words="w",
                        origin="exchange:peer-x", detail="d")
    p.save()
    p2 = persist_rest.load(owner, activate=False)
    _rec("damaged: unjournaled partial survives load (quarantine)",
         dmg.id in p2.nursery.proposals)
    refused = False
    try:
        exchange.build_packet(p2, dmg.id)
    except ExchangeError:
        refused = True
    _rec("damaged: export stays refused", refused)
    _cleanup(owner)

    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        print(f"[{'PASS' if ok else 'FAIL'}] {name}"
              + (f" | {detail}" if detail and not ok else ""))
    print(f"STEP5B_EXCHANGE_DURABILITY: {passed}/{len(RESULTS)}")
    return passed == len(RESULTS)


def smoke() -> bool:
    return main()


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
