#!/usr/bin/env python3
"""Critic Finding 8 fixture — DuoBeta evidence gate must count DISTINCT
outcome IDs only (Director disposition 7180713277, issue #512).

Defect (verified REAL first-hand 2026-11-25): in
form/mandell/duobeta_learn.py, gate_proposal counted every listed
outcome ID toward MIN_EVIDENCE=3 — the same outcome recorded three
times passed the gate as if it were three independent outcomes, and
the derived preference_index totals reported the inflated count.
One observation wearing three hats could promote learning, violating
the STORED > ELIGIBLE > ... > LEARNED separation discipline.

Contract under test:
  * one outcome x3            -> REJECTED (insufficient_evidence)
  * two distinct outcomes x3 listings ([a,a,b]) -> REJECTED
  * three distinct outcomes   -> ACCEPTED (control, unchanged)
  * distinct + duplicate listings ([a,a,b,c,a]) -> ACCEPTED, and the
    gate's supporting list holds each distinct ID exactly once
  * reported totals (preference_index success count, from which the
    bounded learned score derives) equal the DISTINCT count — never
    the inflated listing count — including for a legacy APPLIED entry
    whose stored supporting list already contains duplicates
  * duplicate failed listings for a preference proposal count once
    toward the dell-matched leg (insufficient_evidence, not a pass
    into the mismatch leg on phantom evidence)

Isolation: unique owner per program, learning ledger VERIFIED empty
before use (a new Program is not fresh by name — NBD-Ω-030 lesson);
test-owner state files removed at the end.

Run: python3 -m form.critic_duobeta_distinct_fixture_test
"""
from __future__ import annotations

import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}"
          + (f" — {detail}" if detail and not cond else ""))


_PID = os.getpid()
_COUNTER = [0]
_OWNERS = []
_STATE_DIR = os.path.join(REPO, "form", "state")


def fresh():
    """Isolated Program: unique owner, learning ledger verified empty."""
    from form.open import Program
    from form.mandell import duobeta_learn as dl
    _COUNTER[0] += 1
    owner = f"critic-f8-{_PID}-{_COUNTER[0]}"
    p = Program(owner=owner)
    if dl.learning_ledger(p):
        raise AssertionError(f"isolation violated: {owner} ledger not empty")
    _OWNERS.append(owner)
    return p


def teardown():
    import pathlib
    for owner in _OWNERS:
        for f in pathlib.Path(_STATE_DIR).glob(f"*{owner}*"):
            try:
                if f.is_file():
                    f.unlink()
            except OSError:
                pass
    _OWNERS.clear()


def completed_oids(p, n):
    """n DISTINCT completed outcomes at dell 70."""
    from form.mandell.execution_observer import observe_seed_execution
    oids = []
    for _ in range(n):
        observe_seed_execution(p, "70[Count]")
        oids.append(list(p.outcome_records.values())[-1]["outcome_id"])
    assert len(set(oids)) == n, f"setup: outcome ids not distinct: {oids}"
    return oids


def failed_oids(p, n):
    """n DISTINCT failed outcomes at dell 86."""
    from form.mandell.execution_observer import observe_seed_execution
    oids = []
    for _ in range(n):
        observe_seed_execution(p, "86[Delete]")
        oids.append(list(p.outcome_records.values())[-1]["outcome_id"])
    assert len(set(oids)) == n, f"setup: outcome ids not distinct: {oids}"
    return oids


def run_all():
    from form.mandell import duobeta_learn as dl

    # ── 1: one outcome listed three times must NOT pass the gate ─────
    p = fresh()
    one = completed_oids(p, 1)
    prop = dl.propose(p, "preference", 70, None, one * 3)
    g = dl.gate_proposal(p, prop["proposal_id"])
    check("dup_x3_gate_refused", g["accepted"] is False
          and g["reason"] == "insufficient_evidence",
          f"gate={g}")
    check("dup_x3_nothing_applied", dl.preference_index(p) == {})

    # ── 2: two distinct outcomes, three listings ([a,a,b]) ──────────
    p = fresh()
    a, b = completed_oids(p, 2)
    prop = dl.propose(p, "preference", 70, None, [a, a, b])
    g = dl.gate_proposal(p, prop["proposal_id"])
    check("dup_two_distinct_refused", g["accepted"] is False
          and g["reason"] == "insufficient_evidence",
          f"gate={g}")

    # ── 3: control — three distinct outcomes pass (unchanged) ───────
    p = fresh()
    three = completed_oids(p, 3)
    prop = dl.propose(p, "preference", 70, None, three)
    g = dl.gate_proposal(p, prop["proposal_id"])
    check("distinct_control_accepted", g["accepted"] is True
          and g["reason"] == "all_rules_pass", f"gate={g}")
    check("distinct_control_supporting", g.get("supporting") == three,
          f"supporting={g.get('supporting')}")

    # ── 4: distinct + duplicate listings: accepted, counted once ────
    p = fresh()
    a, b, c = completed_oids(p, 3)
    prop = dl.propose(p, "preference", 70, None, [a, a, b, c, a])
    g = dl.gate_proposal(p, prop["proposal_id"])
    check("mixed_accepted", g["accepted"] is True, f"gate={g}")
    check("mixed_supporting_distinct",
          g.get("supporting") == [a, b, c],
          f"supporting={g.get('supporting')}")
    ap = dl.apply_proposal(p, prop["proposal_id"])
    check("mixed_applied", ap["applied"] is True)
    idx = dl.preference_index(p)
    check("mixed_index_counts_distinct",
          idx.get((70, None), {}).get("success") == 3,
          f"index={idx}")
    check("mixed_bounded_score_uses_distinct",
          dl.bounded_learned_score(p, 70, None)
          == dl.saturate_learned_score(3),
          f"score={dl.bounded_learned_score(p, 70, None)}")

    # ── 5: legacy APPLIED entry with duplicated supporting list ─────
    # Reported totals must not inflate even when the stored record
    # already carries duplicates (pre-repair ledger entries).
    p = fresh()
    (solo,) = completed_oids(p, 1)
    dl._append_learn_entry(
        p, "LEARN APPLIED legacy duplicate supporting",
        {"kind": "learn", "proposal_kind": "preference", "dell": 70,
         "knowledge_id": None, "status": "APPLIED",
         "evidence": {"outcome_ids": [solo], "supporting": [solo, solo, solo]},
         "gate": {"accepted": True, "reason": "all_rules_pass"},
         "reason": "", "applied_ts": "2026-01-01T00:00:00Z"})
    idx = dl.preference_index(p)
    check("legacy_index_counts_distinct",
          idx.get((70, None), {}).get("success") == 1,
          f"index={idx}")

    # ── 6: duplicate failed listings count once on the dell leg ─────
    p = fresh()
    (f1,) = failed_oids(p, 1)
    prop = dl.propose(p, "preference", 86, None, [f1, f1, f1])
    g = dl.gate_proposal(p, prop["proposal_id"])
    check("dup_failed_counts_once", g["accepted"] is False
          and g["reason"] == "insufficient_evidence",
          f"gate={g}")

    teardown()


def smoke() -> bool:
    RESULTS.clear()
    try:
        run_all()
    except Exception as exc:  # noqa: BLE001 — surface as a failed check
        check("fixture_completed_without_exception", False, repr(exc))
        try:
            teardown()
        except Exception:
            pass
    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"critic_duobeta_distinct_fixture: {passed}/{len(RESULTS)}")
    return passed == len(RESULTS) and len(RESULTS) > 0


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
