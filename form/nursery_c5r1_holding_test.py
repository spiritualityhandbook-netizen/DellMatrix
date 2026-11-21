#!/usr/bin/env python3
"""C5R.1 HOLD — failing-first persistence tests (precondition (iii)).

Written BEFORE the C5R.1 build, against the merged replan's acceptance
criteria (director-reports/C5_REPLAN_2026-11-15.md, PR #450) and the
precondition (ii) source-contract review (findings 3-5). The contract
pinned here is the SYS-C29 family contract generalized to every
proposal field: admitted content is stored byte-exact, or refused
with a typed error BEFORE any mutation — never silently truncated.

Checks (isolated temp paths throughout; no owner state touched):
- H1 (AC-1.1): 1,000 pending proposals, each with maximal admitted
  fields (words 5,000, label 200, reason 1,000), are stored; a
  same-process reload returns all 1,000 with every field byte-exact
  and summary() counts agreeing with the true count.
- H2 (AC-1.1, CROSS_PROCESS): a separate interpreter loads the H1
  file and returns a digest over every stored (id, label, words,
  reason); it must equal the digest computed in this process.
- H3 (precondition (ii) finding 3): origin of 500 chars is stored
  byte-exact OR refused typed before mutation (count and disk bytes
  unchanged). On the unrepaired head Nursery.add stores origin[:120]
  silently — this check FAILS first.
- H4 (finding 3): detail of 5,000 chars, same contract. Unrepaired
  head stores detail[:2000] silently — FAILS first.
- H5 (finding 3): goals — 12 goals of 500 chars each, same contract
  (all goals byte-exact, or typed refusal before mutation).
  Unrepaired head stores each goal[:200] and the list[:8] silently
  — FAILS first.
- H6 (AC-1.2, store side): summary() counts agree with the true
  stored counts across pending/confirmed/rejected after a reload.
- H7 (persistence integrity): a truncated canonical file raises
  NurseryLoadError and its bytes are left untouched; a record with
  an unknown key also raises NurseryLoadError (the fail-closed
  forward-compatibility cost named in precondition (ii) finding 2).
- H8 (persistence integrity): an external on-disk change makes the
  next save raise NurseryConflictError and the external bytes are
  preserved (no lost update).
- H9 (AC-1.3): add/confirm/reject never remove any proposal as a
  side effect; the only removal is the explicit clear_rejected(),
  which removes exactly the rejected set and returns its count.

Labels: UNIT_SYNTHETIC / INTEGRATION (direct Nursery authority,
isolated temp files) + CROSS_PROCESS for H2 (separate interpreter).
The REPL read-path half of AC-1.2 (list / ranked / browse /
ghost views stating shown/total) is NOT covered here; it is pinned
by the C5R.1 slice's own read-path probe, recorded as an open item
in the precondition (iii) evidence note.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def _fill(seed_text, n):
    reps = (seed_text * (n // len(seed_text) + 1))[:n]
    assert len(reps) == n
    return reps


def _fresh(tmp, name):
    from form.dell_matrix.nursery import Nursery
    path = os.path.join(tmp, name)
    return Nursery.load(path), path


def _stored_or_refused(n, path, field, value, **kw):
    """Add one proposal carrying `value` in `field`; return True iff
    the field is stored byte-exact (memory + fresh reload) OR add()
    refused with a ValueError before any mutation (in-memory count
    and on-disk bytes unchanged). Silent truncation returns False."""
    before_count = len(n.proposals)
    before_bytes = None
    if os.path.isfile(path):
        with open(path, "rb") as f:
            before_bytes = f.read()
    try:
        p = n.add("probe " + field, words="w", **{field: value}, **kw)
    except ValueError:
        ok_state = len(n.proposals) == before_count
        if before_bytes is not None and os.path.isfile(path):
            with open(path, "rb") as f:
                ok_state = ok_state and f.read() == before_bytes
        return ok_state
    from form.dell_matrix.nursery import Nursery
    fresh = Nursery.load(path)
    got = getattr(fresh.proposals[p.id], field)
    return getattr(p, field) == value and got == value


def smoke() -> bool:
    from form.dell_matrix.nursery import (
        Nursery, NurseryConflictError, NurseryLoadError)

    tmp = tempfile.mkdtemp(prefix="nursery_c5r1_holding_")

    # H1: AC-1.1 — 1,000 proposals at maximal admitted fields.
    n, path = _fresh(tmp, "h1.json")
    expected = {}
    for i in range(1000):
        label = _fill(f"p{i} ", 200)
        words = _fill(f"words-{i}-", 5000)
        reason = _fill(f"reason-{i}-", 1000)
        p = n.add(label, words=words, reason=reason, seed=i)
        expected[p.id] = (label, words, reason)
    check("H1.count_1000", len(n.proposals) == 1000,
          f"count={len(n.proposals)}")
    s = n.summary()
    check("H1.summary_agrees", s["pending"] == 1000 and s["total"] == 1000,
          str(s))
    fresh = Nursery.load(path)
    exact = len(fresh.proposals) == 1000 and all(
        (p.label, p.words, p.reason) == expected[p.id]
        for p in fresh.proposals.values())
    check("H1.reload_byte_exact", exact)

    # H2: cross-process reload digest over the H1 file.
    def _digest(proposals):
        rows = sorted(
            (p.id, p.label, p.words, p.reason) for p in proposals)
        return hashlib.sha256(
            json.dumps(rows).encode("utf-8")).hexdigest()

    mine = _digest([type("P", (), dict(zip(
        ("id", "label", "words", "reason"), (pid,) + vals)))()
        for pid, vals in expected.items()])
    repo_root = os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))
    verifier = (
        "import hashlib, json, sys\n"
        f"sys.path.insert(0, {repo_root!r})\n"
        "from form.dell_matrix.nursery import Nursery\n"
        f"n = Nursery.load({path!r})\n"
        "rows = sorted((p.id, p.label, p.words, p.reason)"
        " for p in n.proposals.values())\n"
        "print(len(rows))\n"
        "print(hashlib.sha256(json.dumps(rows).encode('utf-8'))"
        ".hexdigest())\n")
    pr = subprocess.run([sys.executable, "-c", verifier],
                        capture_output=True, text=True, timeout=300)
    lines = pr.stdout.strip().splitlines()
    check("H2.cross_process_reload",
          pr.returncode == 0 and len(lines) == 2
          and lines[0] == "1000" and lines[1] == mine,
          (lines[-1][:16] if lines else pr.stderr[-200:]))

    # H3-H5: the remaining silent truncations (finding 3).
    n3, path3 = _fresh(tmp, "h3.json")
    n3.add("seed", words="w")
    check("H3.origin_no_silent_truncation",
          _stored_or_refused(n3, path3, "origin", _fill("origin-", 500)))
    check("H4.detail_no_silent_truncation",
          _stored_or_refused(n3, path3, "detail", _fill("detail-", 5000)))
    check("H5.goals_no_silent_truncation",
          _stored_or_refused(n3, path3, "goals",
                             [_fill(f"goal-{i}-", 500) for i in range(12)]))

    # H6: summary agreement across statuses after reload.
    n6, path6 = _fresh(tmp, "h6.json")
    ids = [n6.add(f"s{i}", words="w", seed=i).id for i in range(15)]
    for pid in ids[:3]:
        n6.confirm(pid, actor="suite:c5r1")
    for pid in ids[3:5]:
        n6.reject(pid)
    fresh6 = Nursery.load(path6)
    s6 = fresh6.summary()
    check("H6.summary_mixed_status",
          s6 == {"pending": 10, "total": 15, "confirmed": 3,
                 "rejected": 2}
          and len(fresh6.pending()) == 10, str(s6))

    # H7: fail-closed load.
    n7, path7 = _fresh(tmp, "h7.json")
    n7.add("victim", words="w")
    with open(path7, "rb") as f:
        good = f.read()
    with open(path7, "wb") as f:
        f.write(good[: len(good) // 2])
    with open(path7, "rb") as f:
        truncated = f.read()
    try:
        Nursery.load(path7)
        raised = False
    except NurseryLoadError:
        raised = True
    with open(path7, "rb") as f:
        untouched = f.read() == truncated
    check("H7.truncated_fails_closed", raised and untouched)
    bad = json.loads(good.decode("utf-8"))
    first_key = next(k for k in bad if not k.startswith("__"))
    bad[first_key]["unknown_future_field"] = 1
    with open(path7, "w") as f:
        json.dump(bad, f)
    try:
        Nursery.load(path7)
        raised2 = False
    except NurseryLoadError:
        raised2 = True
    check("H7.unknown_key_fails_closed", raised2)

    # H8: optimistic concurrency.
    n8, path8 = _fresh(tmp, "h8.json")
    n8.add("first", words="w")
    with open(path8, "rb") as f:
        external = f.read().replace(b"first", b"extnl")
    with open(path8, "wb") as f:
        f.write(external)
    try:
        n8.add("second", words="w")
        conflict = False
    except NurseryConflictError:
        conflict = True
    with open(path8, "rb") as f:
        preserved = f.read() == external
    check("H8.conflict_refused_bytes_preserved", conflict and preserved)

    # H9: no side-effect removal; clear_rejected is explicit + exact.
    n9, path9 = _fresh(tmp, "h9.json")
    ids9 = [n9.add(f"k{i}", words="w", seed=i).id for i in range(6)]
    n9.confirm(ids9[0], actor="suite:c5r1")
    n9.reject(ids9[1])
    n9.reject(ids9[2])
    check("H9.no_side_effect_removal", len(n9.proposals) == 6,
          f"count={len(n9.proposals)}")
    removed = n9.clear_rejected()
    check("H9.clear_rejected_exact",
          removed == 2 and len(n9.proposals) == 4
          and ids9[1] not in n9.proposals
          and ids9[2] not in n9.proposals
          and len(Nursery.load(path9).proposals) == 4,
          f"removed={removed}")

    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"nursery_c5r1_holding_test: {passed}/{len(RESULTS)} PASS")
    return passed == len(RESULTS)


if __name__ == "__main__":
    raise SystemExit(0 if smoke() else 1)
