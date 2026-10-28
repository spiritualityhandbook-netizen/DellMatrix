"""Director completion order (2026-10-28) — residual Exchange
repair, segment #117.

The Director's independent probe (run at the repair merge and
at current main) found what repair R2 had not reached: receipt
RECORDS round-tripped exactly, but the seed payload did not —
build_packet sourced the Keep from the proposal's formatted
detail (a "KEEP: " prefix added, the tail clipped at the detail
bound), and seed.chain + manifest.requirements were never
stored at import, so re-export returned them empty.

The repair: import preserves the packet's original label /
chain / Keep / requirements as validated durable data in the
exchange_seeds section, under the imported proposal; the
Nursery detail is a rendering derived from it; export reads
the stored original. This suite pins the order's acceptance:

- the Director's exact scenario, flipped: 2,000-char Keep,
  nonempty chain/requirements, 50 receipts — exact equality of
  seed, requirements and all six receipt fields after
  save/reload, proposal PENDING;
- A->B->C across FRESH PROCESSES (subprocess drivers), with
  save/reload before each export — the third matrix's packet is
  identical to the first;
- 0 receipts round-trips (lint says "no receipts");
- over-bound packets are refused BEFORE any mutation (no
  proposal, no receipts, no payload recorded);
- missing-link lint fires at the LAST receipt;
- non-vacuity: corrupting the rendered detail after import
  cannot change the exported Keep (the old mechanism fails
  this by construction);
- a 100-char seed label round-trips from the payload even
  though the Nursery truncates its own label copy to 80;
- native (never-imported) exports are unchanged, and explicit
  build overrides remain deliberate and effective;
- the receiver's own gate can still act on the import.
"""
from __future__ import annotations

import glob
import json
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from form.open import Program  # noqa: E402
from form import persist_rest  # noqa: E402
from form.dell_matrix import exchange as ex  # noqa: E402

RESULTS = []
ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", ".."))


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


def _receipts(n, outcome_last="outcome"):
    out = []
    for i in range(n):
        out.append({
            "origin": f"lab:{i}", "guess": f"guess{i}",
            "test_method": f"method{i}", "result": f"result{i}",
            "mirror": f"mirror{i}",
            "outcome": outcome_last if i == n - 1 else f"outcome{i}"})
    return out


def _director_packet():
    return {
        "version": 1,
        "seed": {"label": "ExactKeep",
                 "chain": "51[Select] > 70[Count]",
                 "keep": "K" * 1990 + "ENDMARKER!"},
        "manifest": {"author_origin": "probe",
                     "created": "2026-10-28",
                     "registry": ex.REGISTRY_STAMP,
                     "requirements": ["preserve-seed"]},
        "receipts": _receipts(50),
    }


def _check_director_scenario():
    owner = "R4Exact"
    _cleanup(owner)
    try:
        packet = _director_packet()
        p = Program(owner)
        out = ex.import_packet(p, packet)
        pid = out["pid"]
        _rec("import lands PENDING",
             out.get("ok") and
             p.nursery.proposals[pid].status == "pending",
             f"out={out}")
        p.save()
        p2 = persist_rest.load(owner, activate=False)
        built = ex.build_packet(p2, pid)
        _rec("seed round-trips exactly after reload",
             built["seed"] == packet["seed"],
             f"keep_eq={built['seed']['keep'] == packet['seed']['keep']} "
             f"chain={built['seed']['chain']!r}")
        _rec("requirements and manifest origin round-trip",
             built["manifest"]["requirements"]
             == packet["manifest"]["requirements"]
             and built["manifest"]["author_origin"] == "probe",
             f"man={built['manifest']}")
        _rec("all 50 receipts exact, six fields, in order",
             built["receipts"] == packet["receipts"],
             f"n={len(built['receipts'])}")
        state_path = os.path.join(
            ROOT, "form", "state", f"program_{owner}.json")
        with open(state_path, encoding="utf-8") as f:
            state = json.load(f)
        seeds = (state.get("exchange_seeds") or {}).get(
            "entries") or {}
        keeps = [e.get("keep") for e in seeds.values()]
        _rec("payload is durable data in the saved state",
             packet["seed"]["keep"] in keeps,
             f"payloads={len(seeds)}")
        ctx = p2.make_review_context(pid, reviewer="human:ace")
        res = p2.confirm_proposal(pid, _producer="r4test",
                                  _review_context=ctx)
        _rec("the receiver's own gate can act on the import",
             res.get("ok") is True, f"res={res}")
    finally:
        _cleanup(owner)


def _check_nonvacuity_and_labels():
    owner = "R4Tamper"
    _cleanup(owner)
    try:
        packet = _director_packet()
        p = Program(owner)
        pid = ex.import_packet(p, packet)["pid"]
        prop = p.nursery.proposals[pid]
        prop.detail = "KEEP: forged rendering, tail clipped..."
        p.save()
        p2 = persist_rest.load(owner, activate=False)
        built = ex.build_packet(p2, pid)
        _rec("corrupting the rendered detail cannot change the Keep",
             built["seed"]["keep"] == packet["seed"]["keep"],
             f"keep_head={built['seed']['keep'][:16]!r}")
        long_label = "L" * 100
        pkt2 = _director_packet()
        pkt2["seed"] = dict(pkt2["seed"], label=long_label)
        out2 = ex.import_packet(p, pkt2)
        built2 = ex.build_packet(p, out2["pid"])
        landed = p.nursery.proposals[out2["pid"]]
        _rec("100-char label round-trips from the payload",
             built2["seed"]["label"] == long_label
             and len(landed.label) == 80,
             f"exported={len(built2['seed']['label'])} "
             f"nursery={len(landed.label)}")
    finally:
        _cleanup(owner)


def _check_bounds_and_lint():
    owner = "R4Bounds"
    _cleanup(owner)
    try:
        p = Program(owner)
        over = _director_packet()
        over["seed"] = dict(over["seed"], keep="K" * 2001)
        raised = False
        try:
            ex.import_packet(p, over)
        except ex.ExchangeError:
            raised = True
        _rec("over-bound packet refused before any mutation",
             raised and len(p.nursery.proposals) == 0
             and not (getattr(p, "exchange_seeds", None) or {})
             and not (getattr(p, "exchange_receipts", None) or {}),
             f"raised={raised} props={len(p.nursery.proposals)}")
        zero = _director_packet()
        zero["receipts"] = []
        out = ex.import_packet(p, zero)
        built = ex.build_packet(p, out["pid"])
        _rec("zero receipts round-trip, lint names the absence",
             out.get("ok") and built["receipts"] == []
             and built["seed"] == zero["seed"]
             and "no receipts" in out["lint"]["labels"],
             f"lint={out['lint']}")
        gappy = _director_packet()
        gappy["receipts"] = _receipts(3, outcome_last="")
        out = ex.import_packet(p, gappy)
        _rec("missing-link lint fires at the last receipt",
             "receipt 3: outcome absent" in out["lint"]["labels"]
             and out["lint"]["complete"] is False,
             f"labels={out['lint']['labels']}")
    finally:
        _cleanup(owner)


def _check_native_and_overrides():
    owner = "R4Native"
    _cleanup(owner)
    try:
        p = Program(owner)
        prop = p.nursery.add("Native Keep", words="native words",
                             detail="the native detail",
                             origin="host:R4Native")
        built = ex.build_packet(p, prop.id)
        _rec("native export unchanged (detail is its keep)",
             built["seed"]["keep"] == "the native detail"
             and built["seed"]["chain"] == ""
             and built["manifest"]["requirements"] == [],
             f"seed={built['seed']}")
        over = ex.build_packet(p, prop.id, chain="51[X] > 70[Y]",
                               requirements=["explicit"])
        _rec("explicit overrides are deliberate and effective",
             over["seed"]["chain"] == "51[X] > 70[Y]"
             and over["manifest"]["requirements"] == ["explicit"],
             f"seed={over['seed']} reqs="
             f"{over['manifest']['requirements']}")
    finally:
        _cleanup(owner)


_DRIVER = '''
import sys
sys.path.insert(0, ".")
from form.open import Program
from form import persist_rest
from form.dell_matrix import exchange as ex
owner, infile, outfile = sys.argv[1], sys.argv[2], sys.argv[3]
p = Program(owner)
packet = ex.read_packet(infile)
out = ex.import_packet(p, packet)
assert out.get("ok"), out
p.save()
p2 = persist_rest.load(owner, activate=False)
built = ex.build_packet(p2, out["pid"])
ex.write_packet(built, outfile)
print("R4DRIVER", p2.nursery.proposals[out["pid"]].status)
'''


def _check_abc_fresh_processes():
    owners = ["R4HopB", "R4HopC"]
    for o in owners:
        _cleanup(o)
    driver = os.path.join(ROOT, "_r4_driver.py")
    f_a = os.path.join(ROOT, "_r4_a.json")
    f_b = os.path.join(ROOT, "_r4_b.json")
    f_c = os.path.join(ROOT, "_r4_c.json")
    try:
        packet = _director_packet()
        ex.write_packet(packet, f_a)
        with open(driver, "w", encoding="utf-8") as f:
            f.write(_DRIVER)
        r1 = subprocess.run(
            [sys.executable, driver, owners[0], f_a, f_b],
            capture_output=True, text=True, cwd=ROOT, timeout=300)
        _rec("hop B (fresh process) imports PENDING and exports",
             r1.returncode == 0 and "R4DRIVER pending" in r1.stdout,
             f"rc={r1.returncode} err={r1.stderr[-200:]}")
        r2 = subprocess.run(
            [sys.executable, driver, owners[1], f_b, f_c],
            capture_output=True, text=True, cwd=ROOT, timeout=300)
        final = ex.read_packet(f_c) if os.path.exists(f_c) else {}
        _rec("A->B->C across fresh processes is identical to A",
             r2.returncode == 0
             and final.get("seed") == packet["seed"]
             and final.get("manifest", {}).get("requirements")
             == packet["manifest"]["requirements"]
             and final.get("receipts") == packet["receipts"],
             f"rc={r2.returncode} seed_eq="
             f"{final.get('seed') == packet['seed']}")
    finally:
        for f in (driver, f_a, f_b, f_c):
            try:
                os.remove(f)
            except FileNotFoundError:
                pass
        for o in owners:
            _cleanup(o)


def _check_section_contract():
    owner = "R4Contract"
    good = {
        "entry_id": "a" * 32, "owner": owner,
        "ts": "2026-10-28T00:00:00Z", "pid": "somepid",
        "label": "L", "chain": "", "keep": "the keep",
        "author_origin": "probe", "created": "2026-10-28",
        "registry": ex.REGISTRY_STAMP, "requirements": []}
    bad = dict(good)
    bad["entry_id"] = "b" * 32
    bad["keep"] = "K" * 2001
    raw = {"version": 1,
           "entries": {good["entry_id"]: good, bad["entry_id"]: bad}}
    valid, malformed = ex.validate_seeds_section(raw, owner)
    _rec("payload section preserves malformed records as evidence",
         good["entry_id"] in valid and bad["entry_id"] not in valid
         and malformed is not None and bad["entry_id"] in malformed,
         f"valid={list(valid)}")


def main():
    _check_director_scenario()
    _check_nonvacuity_and_labels()
    _check_bounds_and_lint()
    _check_native_and_overrides()
    _check_abc_fresh_processes()
    _check_section_contract()
    ok = sum(1 for _, c, _ in RESULTS if c)
    for name, cond, detail in RESULTS:
        print(f"{'PASS' if cond else 'FAIL'} {name}"
              + (f" :: {detail}" if not cond else ""))
    print(f"REPAIR_R4: {ok}/{len(RESULTS)}")
    return ok == len(RESULTS)


def smoke() -> bool:
    return main()


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
