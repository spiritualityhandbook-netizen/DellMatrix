#!/usr/bin/env python3
"""Q-S2.2 — Nursery reason bound: admitted reasons stored losslessly
to the admitted 1,000-char bound; beyond it, explicit refusal before
any mutation or save.

The defect (failing-first, reproduced on the unrepaired head):
the inference dock admits a proposal reason up to 1,000 chars at
three admission points (inference_dock.py: host reason in propose(),
host reason at the semantic-verb entry, model reason in
validate_semantic_output), and director_session.py declares the same
bound (MAX_REASON_CHARS = 1000) — but Nursery.add() stored
reason[:160], silently destroying admitted content. The dock-session
evidence validator (dock_session.py) mirrored the 160 cut even
though its entries carry the stored reason verbatim; it is
reconciled to the shared bound in the same circuit (R6).

Checks (isolated temp paths throughout; no owner state touched):
- R1 admitted-max 1,000-char reason stored EXACTLY (memory + disk).
- R2 boundaries 160 / 161 stored exactly (161 was cut before).
- R3 1,001 chars refused with NurseryReasonError BEFORE mutation:
  in-memory proposal count unchanged, on-disk bytes byte-identical,
  fresh load unchanged.
- R4 unicode reason stored exactly (chars, not bytes).
- R5 legacy record (a 160-char reason as the old code wrote it)
  loads intact and round-trips through a later save.
- R6 dock_session validator accepts a 500-char reason end-to-end
  (record built via new_record + append_proposal, the same shapes
  inference_dock._record_evidence writes), and still refuses a
  1,001-char reason entry.
- R7 fresh-process reload: a separate interpreter loads the file
  and exact-compares every stored reason.

Labels: UNIT_SYNTHETIC / INTEGRATION (direct Nursery + dock_session
authorities, isolated temp files). No dock session is driven; the
public dock path is covered by the dock suites in the neighbor set.
"""
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import tempfile

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def _reason(n, seed_text="evidence for the judgment: "):
    """A deterministic n-char reason."""
    reps = (seed_text * (n // len(seed_text) + 1))[:n]
    assert len(reps) == n
    return reps


def _fresh_nursery(tmp, name="nursery_t.json"):
    from form.dell_matrix.nursery import Nursery
    return Nursery.load(os.path.join(tmp, name)), os.path.join(tmp, name)


def smoke() -> bool:
    from form.dell_matrix.nursery import (
        MAX_REASON_CHARS, Nursery, NurseryReasonError)

    tmp = tempfile.mkdtemp(prefix="nursery_reason_bound_")
    assert MAX_REASON_CHARS == 1000, MAX_REASON_CHARS

    # R1: admitted-max stored exactly, memory + disk.
    n, path = _fresh_nursery(tmp, "r1.json")
    r1000 = _reason(1000)
    p = n.add("admitted max", words="w", reason=r1000)
    check("R1.admitted1000_exact_memory", p.reason == r1000,
          f"len={len(p.reason)}")
    fresh = Nursery.load(path)
    check("R1.admitted1000_exact_disk",
          fresh.proposals[p.id].reason == r1000)

    # R2: boundaries 160 / 161 both stored exactly (161 was cut).
    n, path = _fresh_nursery(tmp, "r2.json")
    p160 = n.add("boundary 160", words="w", reason=_reason(160))
    p161 = n.add("boundary 161", words="w", reason=_reason(161))
    check("R2.boundary160_161_exact",
          p160.reason == _reason(160) and p161.reason == _reason(161),
          f"160:{len(p160.reason)} 161:{len(p161.reason)}")

    # R3: 1,001 refused BEFORE mutation — memory, disk, fresh load.
    before_count = len(n.proposals)
    with open(path, "rb") as f:
        before_bytes = f.read()
    refused = None
    try:
        n.add("oversize", words="w", reason=_reason(1001))
    except NurseryReasonError as e:
        refused = e
    except Exception as e:  # wrong error type is a failure, not a pass
        refused = None
        check("R3.refused_error_type", False, f"wrong error: {type(e)}")
    check("R3.refused_explicitly", isinstance(refused, NurseryReasonError),
          "reason-error" if refused else "no-raise")
    check("R3.no_inmemory_mutation", len(n.proposals) == before_count,
          f"count={len(n.proposals)}")
    with open(path, "rb") as f:
        after_bytes = f.read()
    check("R3.no_disk_mutation", before_bytes == after_bytes,
          f"bytes {len(before_bytes)} -> {len(after_bytes)}")
    fresh = Nursery.load(path)
    check("R3.fresh_load_unchanged",
          len(fresh.proposals) == before_count
          and fresh.proposals[p161.id].reason == _reason(161))

    # R4: unicode stored exactly (char-exact, incl. multibyte + emoji).
    n, path = _fresh_nursery(tmp, "r4.json")
    uni = ("raison d'être — l'évidence est claire, "
           "理由は明確です, and the gate reads it all 🎯 ") 
    uni = (uni * 12)[:600]
    assert len(uni) == 600
    p = n.add("unicode reason", words="w", reason=uni)
    fresh = Nursery.load(path)
    check("R4.unicode600_exact",
          p.reason == uni and fresh.proposals[p.id].reason == uni,
          f"len={len(p.reason)}")

    # R5: legacy record (160-char reason, as pre-repair code wrote it)
    # loads intact and round-trips through a later save.
    n, path = _fresh_nursery(tmp, "r5.json")
    legacy_reason = _reason(160)
    lp = n.add("legacy record", words="w", reason=legacy_reason)
    n2 = Nursery.load(path)
    ok_load = n2.proposals[lp.id].reason == legacy_reason
    n2.add("later arrival", words="w", reason=_reason(500))
    n3 = Nursery.load(path)
    check("R5.legacy_loads_and_roundtrips",
          ok_load and n3.proposals[lp.id].reason == legacy_reason
          and len(n3.proposals) == 2,
          f"legacy len={len(n3.proposals[lp.id].reason)}")

    # R6: dock_session validator, end-to-end at the shared bound.
    from form.dell_matrix import dock_session as ds
    owner = "reason-bound-owner"
    rec = ds.new_record(owner, "host", "fake", "model-x", "propose",
                        "snap")
    entry = {
        "pid": p.id,
        "ts": "2026-11-15T00:00:00Z",
        "task": "propose",
        "reason": _reason(500),
        "origin": "dock:fake:model-x",
        "prompt_hash": hashlib.sha256(b"prompt").hexdigest(),
        "prompt_summary": "a prompt",
        "prompt_chars": 6,
        "snapshot_id": None,
        "model": "model-x",
    }
    ds.append_proposal(rec, dict(entry))
    ok500, err500 = ds.validate(rec, owner)
    check("R6.validator_accepts_500", ok500, err500)
    rec_bad = ds.new_record(owner, "host", "fake", "model-x",
                            "propose", "snap")
    bad = dict(entry)
    bad["reason"] = _reason(1001)
    ds.append_proposal(rec_bad, bad)
    ok1001, _ = ds.validate(rec_bad, owner)
    check("R6.validator_refuses_1001", not ok1001)

    # R7: fresh-process reload exact-compares every stored reason.
    n, path = _fresh_nursery(tmp, "r7.json")
    expected = {}
    for i, ln in enumerate((160, 161, 500, 1000)):
        pp = n.add(f"reload {ln}", words="w", reason=_reason(ln))
        expected[pp.id] = _reason(ln)
    code = (
        "import json, sys\n"
        "from form.dell_matrix.nursery import Nursery\n"
        f"n = Nursery.load({path!r})\n"
        "out = {pid: p.reason for pid, p in n.proposals.items()}\n"
        "sys.stdout.write(json.dumps(out, sort_keys=True))\n"
    )
    r = subprocess.run([sys.executable, "-c", code],
                       capture_output=True, text=True)
    import json as _json
    got = _json.loads(r.stdout) if r.returncode == 0 else {}
    check("R7.fresh_process_exact_compare", got == expected,
          f"proposals={sorted(got)} rc={r.returncode}")

    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"nursery_reason_bound_test: {passed}/{len(RESULTS)} PASS")
    return passed == len(RESULTS)


if __name__ == "__main__":
    raise SystemExit(0 if smoke() else 1)
