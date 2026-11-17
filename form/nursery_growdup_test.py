#!/usr/bin/env python3
"""GROW-DUP — token-growth duplicate prevention (Director 6931279746).

Scoped repair, NOT a broad Nursery admission-policy change: an add is
suppressed only when it is demonstrably identical to a still-PENDING
proposal and BOTH carry origin="growth:token" (token provenance on
both sides). Equality covers kind, full label, full words, detail,
goals, parents (ordered — the growth enumeration emits one canonical
order and lineage is spelled out in words), reason, and the score
fields affinity / harmony / graph_coherence. Generated ID and
creation time are excluded. Everything else is stored as before:
changed content, changed scores, different provenance (human, dock,
growth:body), and adds whose identical predecessor is confirmed or
rejected all remain distinct proposals. Existing duplicate records
are never merged, rejected, deleted, or confirmed by this repair.

Checks (isolated temp paths; no owner state touched except G8, which
uses its own tagged owner under form/state and cleans up):
- G1: three identical pending growth:token adds -> ONE survivor;
  two suppression receipts naming the survivor; survivor payload
  byte-identical to the first add.
- G2: save/reload — the survivor persists alone, and an identical
  add against the RELOADED nursery is still suppressed.
- G3: negatives stay distinct — changed words, label, detail, goals,
  parents order, reason, affinity, harmony, graph_coherence.
- G4: provenance separation — identical content with origin dock /
  human ("") / growth:body is never suppressed, and a growth:token
  add is not suppressed by a pending non-token twin.
- G5: status separation — identical add after the survivor is
  confirmed, and after it is rejected, is stored as a new proposal.
- G6: pre-existing duplicates are preserved untouched: two identical
  pending records inserted directly stay; a third identical add is
  suppressed against the first and neither record changes.
- G7 (re-pinned by G-DUP.1, Director 6933752017): freshness BEFORE
  suppression — a fresh instance's genuine skip performs no save and
  writes nothing; a STALE instance's duplicate add falls through to
  the canonical NurseryConflictError (external bytes survive), as
  does a distinct add. The original G7 pinned stale-skip-returns-
  survivor; G-DUP.1 showed that return can misrepresent owner state.
- G9: two-instance mutation — B confirms (and, separately, rejects)
  the survivor and saves; stale A's identical add refuses
  canonically, records no receipt, and never returns the decided
  proposal as pending.
- G8 (growth level, PUBLIC path via Program.grow_ideas): growing the
  same unchanged field twice stores each token cross once; the
  second run reports duplicates_suppressed > 0, adds zero new token
  proposals, and run totals reconcile with the nursery receipts.
- G10 (G-DUP.2 transcript disclosure): on a repeat growth, the Loop
  leaf line and the REPL grow door both disclose the suppressed
  count — a duplicates-only run never reads as bare "+0 new
  +0 evolved".

Failing-first: on the unmodified base G1/G2/G6/G7/G8 fail (identical
adds mint suffixed IDs and accumulate); G3/G4/G5 pass both before
and after (they pin what the repair must NOT change).

Labels: UNIT_SYNTHETIC / INTEGRATION (direct Nursery authority,
isolated temp files) + PUBLIC_ENTRY_PATH for G8 (Program.grow_ideas).
"""
from __future__ import annotations

import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from form.dell_matrix.nursery import Nursery, NurseryConflictError, Proposal

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}"
          + (f" — {detail}" if detail and not cond else ""))


BASE = dict(
    label="Alpha Beta",
    words="[Ring:Evolve] Solstice resonance. Parents: Alpha + Beta. "
          "Lineage: a|b.",
    kind="new",
    parents=["a", "b"],
    affinity=0.75,
    reason="Solstice harm=0.50 goals=0.10 hs=0.50 gcoh=0.00",
    seed=0,
    harmony=0.5,
    graph_coherence=0.0,
    origin="growth:token",
    detail="",
    goals=[],
)


def _fresh(tmp, name):
    path = os.path.join(tmp, name)
    return Nursery(path=path), path


def smoke() -> bool:
    tmp = tempfile.mkdtemp(prefix="growdup_test_")

    # G1: identical x3 -> one survivor + receipts + payload unchanged.
    n1, _ = _fresh(tmp, "g1.json")
    p1 = n1.add(**BASE)
    snap = p1.to_dict()
    r2 = n1.add(**BASE)
    r3 = n1.add(**BASE)
    pend = [p for p in n1.proposals.values() if p.status == "pending"]
    check("G1.one_survivor", len(n1.proposals) == 1 and len(pend) == 1,
          f"total={len(n1.proposals)} pending={len(pend)}")
    check("G1.skip_returns_survivor", r2.id == p1.id and r3.id == p1.id)
    check("G1.receipts", len(n1.suppression_receipts) == 2
          and all(r["surviving_id"] == p1.id
                  and r["reason"] == "identical_pending_growth_token"
                  for r in n1.suppression_receipts),
          f"receipts={n1.suppression_receipts}")
    check("G1.survivor_payload_unchanged", n1.proposals[p1.id].to_dict() == snap)

    # G2: reload keeps the single survivor; suppression survives reload.
    n2 = Nursery.load(_fresh(tmp, "g1.json")[1])
    check("G2.reload_one", len(n2.proposals) == 1)
    n2.add(**BASE)
    check("G2.suppressed_after_reload", len(n2.proposals) == 1
          and len(n2.suppression_receipts) == 1)

    # G3: changed-content negatives stay distinct.
    n3, _ = _fresh(tmp, "g3.json")
    n3.add(**BASE)
    variants = [
        {**BASE, "words": BASE["words"] + " changed"},
        {**BASE, "label": "Alpha Beta Gamma"},
        {**BASE, "detail": "authored detail"},
        {**BASE, "goals": ["goal one"]},
        {**BASE, "parents": ["b", "a"]},
        {**BASE, "reason": "Solstice harm=0.51 goals=0.10 hs=0.50 gcoh=0.00"},
        {**BASE, "affinity": 0.5},
        {**BASE, "harmony": 0.25},
        {**BASE, "graph_coherence": 0.25},
    ]
    for v in variants:
        n3.add(**v)
    check("G3.negatives_distinct", len(n3.proposals) == 1 + len(variants),
          f"count={len(n3.proposals)} expected={1 + len(variants)}")
    check("G3.no_receipts", len(n3.suppression_receipts) == 0)

    # G4: provenance separation.
    n4, _ = _fresh(tmp, "g4.json")
    n4.add(**{**BASE, "origin": "dock:test:model"})
    n4.add(**{**BASE, "origin": ""})
    n4.add(**{**BASE, "origin": "growth:body"})
    t1 = n4.add(**BASE)  # token twin of non-token pendings: stored
    check("G4.token_not_suppressed_by_nontoken", len(n4.proposals) == 4
          and t1.origin == "growth:token", f"count={len(n4.proposals)}")
    n4.add(**{**BASE, "origin": "dock:test:model"})
    check("G4.nontoken_never_suppressed", len(n4.proposals) == 5
          and len(n4.suppression_receipts) == 0)

    # G5: status separation.
    n5, _ = _fresh(tmp, "g5.json")
    q1 = n5.add(**BASE)
    n5.confirm(q1.id)
    q2 = n5.add(**BASE)
    check("G5.after_confirm_stored", q2.id != q1.id and q2.status == "pending")
    n5.reject(q2.id)
    q3 = n5.add(**BASE)
    check("G5.after_reject_stored", q3.id not in (q1.id, q2.id)
          and q3.status == "pending" and len(n5.proposals) == 3)

    # G6: pre-existing duplicates preserved.
    n6, path6 = _fresh(tmp, "g6.json")
    first = n6.add(**BASE)
    legacy = Proposal(id="legacy_dup_0001", label=BASE["label"],
                      words=BASE["words"], kind=BASE["kind"],
                      parents=list(BASE["parents"]),
                      affinity=BASE["affinity"], reason=BASE["reason"],
                      harmony=BASE["harmony"],
                      graph_coherence=BASE["graph_coherence"],
                      origin="growth:token")
    n6.proposals[legacy.id] = legacy
    n6.save()
    before = {pid: p.to_dict() for pid, p in n6.proposals.items()}
    n6.add(**BASE)
    check("G6.existing_duplicates_preserved",
          len(n6.proposals) == 2
          and {pid: p.to_dict() for pid, p in n6.proposals.items()} == before)
    check("G6.suppressed_against_first_pending",
          len(n6.suppression_receipts) == 1
          and n6.suppression_receipts[0]["surviving_id"] == first.id)

    # G7 (re-pinned by G-DUP.1, Director 6933752017): freshness
    # BEFORE suppression. A stale instance's duplicate add falls
    # through to the canonical lost-update refusal — it may NOT
    # return a survivor whose on-disk state it cannot prove. A
    # FRESH instance's genuine skip still performs no save.
    n7, path7 = _fresh(tmp, "g7.json")
    s1 = n7.add(**BASE)
    with open(path7, "rb") as f:
        before = f.read()
    r = n7.add(**BASE)
    with open(path7, "rb") as f:
        check("G7.fresh_skip_no_write",
              r.id == s1.id and f.read() == before
              and len(n7.suppression_receipts) == 1)
    with open(path7, "wb") as f:
        f.write(before.replace(b"Alpha", b"AlphX"))
    with open(path7, "rb") as f:
        external = f.read()
    stale_dup_refused = False
    try:
        n7.add(**BASE)
    except NurseryConflictError:
        stale_dup_refused = True
    check("G7.stale_duplicate_refused_canonically",
          stale_dup_refused and len(n7.suppression_receipts) == 1)
    with open(path7, "rb") as f:
        check("G7.external_bytes_preserved", f.read() == external)
    conflict = False
    try:
        n7.add(**{**BASE, "label": "Distinct Label"})
    except NurseryConflictError:
        conflict = True
    check("G7.distinct_add_conflict_refused", conflict)

    # G9 (G-DUP.1 two-instance mutation case): instance B confirms
    # (then, in a second store, rejects) the survivor and saves;
    # stale instance A's identical add must refuse canonically —
    # never return the decided proposal as pending, never record
    # a suppression receipt for it.
    for verb, act in (("confirm", "confirm"), ("reject", "reject")):
        nA, pathA = _fresh(tmp, f"g9_{verb}.json")
        pA = nA.add(**BASE)
        nB = Nursery.load(pathA)
        getattr(nB, act)(pA.id)
        refused = False
        try:
            nA.add(**BASE)
        except NurseryConflictError:
            refused = True
        check(f"G9.stale_add_after_external_{verb}_refused",
              refused and len(nA.suppression_receipts) == 0
              and Nursery.load(pathA).proposals[pA.id].status
              == ("confirmed" if verb == "confirm" else "rejected"))

    # G10 (G-DUP.2): public transcripts disclose suppressions.
    check("G10.transcript_disclosure", _transcript_level())

    # G8: growth level via the public Program.grow_ideas path.
    check("G8.growth_level", _growth_level())

    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"nursery_growdup_test: {passed}/{len(RESULTS)} PASS")
    return passed == len(RESULTS)


def _transcript_level() -> bool:
    """G-DUP.2 (Director delta on PR #466, 2026-11-16): when a
    growth run suppresses duplicates, the PUBLIC transcript — the
    Loop leaf line and the REPL grow door — must say so. A run
    that only re-derived duplicates must not read as '+0 new
    +0 evolved' with the suppressions hidden."""
    import glob
    import io
    import shutil
    from contextlib import redirect_stdout
    from form.mandell.executor import execute_seed
    from form.open import open_program
    from form.repl import _dispatch_public_line

    owner = "GROWDUP2116"
    state = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "state")

    def cleanup():
        for f in glob.glob(os.path.join(state, f"*{owner}*")):
            try:
                if os.path.isdir(f):
                    shutil.rmtree(f)
                else:
                    os.remove(f)
            except FileNotFoundError:
                pass
            except OSError as e:
                raise RuntimeError(f"cleanup failed for {f}: {e}")

    field = [
        ("ta", "harbor lantern keep",
         "harbor lantern craft timber copper kettle song keep cellar vault"),
        ("tb", "harbor lantern forge",
         "harbor lantern craft timber copper kettle song forge cellar vault"),
        ("tc", "harbor copper drift",
         "harbor lantern craft copper song drift axolotl azurite basalt"),
    ]
    try:
        cleanup()
        p = open_program(owner)
        plane = p.cube.session.plane
        plane.units.clear()
        plane.sandboxes.clear()
        p.nursery.proposals.clear()
        for uid, label, words in field:
            p.place(uid, label, words=words, x=0.0, y=0.0)
        r = execute_seed(p, "13[Loop] :: 2")
        msgs = r.get("messages") or []
        growth_lines = [m for m in msgs
                        if m.startswith("Ringed growth:")]
        # Cycle 1 stores the field's 3 crosses; cycle 2 re-derives
        # them identically and suppresses all 3 — the line must
        # disclose the suppressions, not hide them behind the
        # stored counts.
        loop_ok = (growth_lines == [
            "Ringed growth: +3 new +0 evolved "
            "(3 duplicates suppressed)"])
        buf = io.StringIO()
        with redirect_stdout(buf):
            _dispatch_public_line(p, "grow ideas 1", "g10-repl")
        repl_ok = ("Ringed growth: +0 new +0 evolved "
                   "(3 duplicates suppressed)"
                   in buf.getvalue())
        return loop_ok and repl_ok
    finally:
        cleanup()


def _growth_level() -> bool:
    import glob
    import shutil
    from form.open import open_program

    owner = "GROWDUP1116"
    state = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state")

    def cleanup():
        for f in glob.glob(os.path.join(state, f"*{owner}*")):
            try:
                if os.path.isdir(f):
                    shutil.rmtree(f)
                else:
                    os.remove(f)
            except FileNotFoundError:
                pass
            except OSError as e:
                raise RuntimeError(f"cleanup failed for {f}: {e}")

    field = [
        ("ga", "harbor lantern keep",
         "harbor lantern craft timber copper kettle song keep cellar vault"),
        ("gb", "harbor lantern forge",
         "harbor lantern craft timber copper kettle song forge cellar vault"),
        ("gc", "harbor copper drift",
         "harbor lantern craft copper song drift axolotl azurite basalt"),
    ]
    try:
        cleanup()
        p = open_program(owner)
        plane = p.cube.session.plane
        plane.units.clear()
        plane.sandboxes.clear()
        p.nursery.proposals.clear()
        for uid, label, words in field:
            p.place(uid, label, words=words, x=0.0, y=0.0)

        def token_pending():
            return [q for q in p.nursery.proposals.values()
                    if q.origin == "growth:token" and q.status == "pending"]

        res1 = p.grow_ideas(1)
        after1 = len(token_pending())
        receipts1 = len(p.nursery.suppression_receipts)
        res2 = p.grow_ideas(1)
        after2 = len(token_pending())
        receipts2 = len(p.nursery.suppression_receipts)
        suppressed2 = res2.get("duplicates_suppressed", 0)
        added2 = (res2.get("proposed_new", 0)
                  + res2.get("proposed_evolved", 0))
        return (after1 > 0 and after2 == after1 and suppressed2 > 0
                and added2 == 0
                and receipts2 - receipts1 == suppressed2)
    finally:
        cleanup()


if __name__ == "__main__":
    raise SystemExit(0 if smoke() else 1)
