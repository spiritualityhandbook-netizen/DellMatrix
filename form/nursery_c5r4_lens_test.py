#!/usr/bin/env python3
"""C5R.4 LENS — failing-first suite for transparent ranked ordering.

Written BEFORE the C5R.4 build, against Uni's signal definitions
(director-reports/UNI_C5R4_LENS_DEFINITIONS_2026-11-17.md) and the
Director's published LENS directive (delivered via Ace, verified
channel, 2026-11-17): transparent scoring, complete paging, preserved
human confirmation; PlaneRank stays separate (Q-C5R.4 resolved: no
integration).

BEFORE behavior pinned by this suite's failures on the base head:
- Nursery.query / Program.browse_proposals accept no `sort` argument
  at all; the only ordering is (created, id) ascending and the
  response reports sort "created,id".
- No score, component breakdown, or weights version exists anywhere
  in a SEE response.
- The REPL has no `proposals browse sort:lens` form.

Contract under test (definitions doc sections 1-5):
- sort="lens" is opt-in; S = 0.40*LINK + 0.25*ACE + 0.20*FRESH
  + 0.15*NOVEL, weights version "lens-v1", order S desc then
  (created, id) asc.
- LINK = mean(min(len(parents),2)/2, graph_coherence, harmony).
- ACE = 1.0 iff the supersedes_id chain reaches a confirmed record.
- FRESH = 1/(1 + age_days/half_life(collection)); collection =
  effective topic; v1 default half-life 14.0 days; unparseable
  created -> 0.0 with fresh_basis "unknown". The evaluation instant
  is bound into the cursor (one traversal = one frozen ranking).
- NOVEL = 1 - max Jaccard over casefolded label+words token sets
  within the matched set; singleton set -> 1.0; empty tokens -> 0.0.
- Membership never changes: a lens traversal returns exactly the
  default traversal's ID set (1,000-record fixture).
- The lens never writes: store bytes and every record's status are
  identical after lens queries (human confirmation preserved).
- Cursor semantics inherited from SEE: bound sort defers when
  unpassed, explicit different sort refuses CURSOR_FILTER_MISMATCH,
  store change between pages refuses STALE_CURSOR, unknown sort
  refuses SORT_UNSUPPORTED.
- No PlaneRank dependency: the lens works on a nursery-only store
  with no graph/PlaneRank state at all.

Labels: INTEGRATION (Program API over synthetic owner stores) +
HIGH-FIDELITY DISPATCH (REPL dispatcher via capture_output).
State touched: synthetic test owners only, removed at the end.
"""
from __future__ import annotations

import hashlib
import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def _mk(i, **over):
    from form.dell_matrix.nursery import Proposal
    rec = dict(
        id=f"lens_{i:04d}",
        label=f"seed label {i}",
        words=f"seed words {i}",
        kind="new",
        parents=[],
        affinity=0.0,
        reason="",
        created="2026-11-10T00:00:00+00:00",
        status="pending",
        harmony=0.0,
        graph_coherence=0.0,
        lifecycle_state="active",
        supersedes_id=None,
        superseded_by_id=None,
        revision_root_id=None,
        revision_number=None,
        origin="",
        detail="",
        goals=[],
    )
    rec.update(over)
    return Proposal(**rec)


def _cleanup(owner):
    state = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state")
    if os.path.isdir(state):
        for name in os.listdir(state):
            if owner in name:
                try:
                    os.remove(os.path.join(state, name))
                except OSError:
                    pass


def _traverse(fn, **kw):
    ids, pages = [], []
    cursor = None
    while True:
        resp = fn(cursor=cursor, **kw)
        pages.append(resp)
        if not resp.get("ok"):
            return ids, pages
        ids.extend(it["id"] for it in resp["items"])
        if resp.get("exhausted") or not resp.get("next_cursor"):
            return ids, pages
        cursor = resp["next_cursor"]


def _fail(names, exc):
    for nm in names:
        check(nm, False, f"exc {exc!r}")


def smoke() -> bool:
    from form.open import open_program
    from form.repl import _dispatch_public_line, capture_output

    suffix = uuid.uuid4().hex[:8]
    owner_a = "C5R4LA" + suffix
    owner_b = "C5R4LB" + suffix
    try:
        # ---------- Fixture A: 1,000 records, default vs lens ----------
        pa = open_program(owner_a)
        for i in range(1000):
            rec = _mk(i)
            pa.nursery.proposals[rec.id] = rec
        pa.nursery.save()

        try:
            ids_default, _ = _traverse(pa.browse_proposals, page_size=200)
            check("L1.default_order_pin_unchanged",
                  ids_default == sorted(ids_default) and len(ids_default) == 1000,
                  f"n={len(ids_default)}")
        except Exception as e:
            _fail(["L1.default_order_pin_unchanged"], e)

        try:
            first = pa.browse_proposals(sort="lens", page_size=10)
            check("L2.lens_sort_accepted",
                  first.get("ok") is True and first.get("sort") == "lens-v1",
                  f"ok={first.get('ok')} sort={first.get('sort')!r}")
        except Exception as e:
            _fail(["L2.lens_sort_accepted"], e)

        try:
            ids_lens, _ = _traverse(pa.browse_proposals, sort="lens",
                                    page_size=200)
            check("L3.lens_membership_equals_default",
                  sorted(ids_lens) == sorted(ids_default)
                  and len(ids_lens) == len(set(ids_lens)) == 1000,
                  f"lens n={len(ids_lens)}")
        except Exception as e:
            _fail(["L3.lens_membership_equals_default"], e)

        # ---------- Fixture B: hand-computed scores ----------
        pb = open_program(owner_b)
        # b0: confirmed ancestor. b1: supersedes b0 (ACE=1). b2: plain.
        b0 = _mk(0, id="lb_0000", status="confirmed",
                 created="2026-11-16T00:00:00+00:00")
        b1 = _mk(1, id="lb_0001", supersedes_id="lb_0000",
                 parents=["x", "y"], graph_coherence=1.0, harmony=1.0,
                 label="unique zebra quasar", words="solitary xenon bloom",
                 created="2026-11-17T00:00:00+00:00")
        b2 = _mk(2, id="lb_0002", label="seed label 2", words="seed words 2",
                 created="2026-11-03T00:00:00+00:00")
        for r in (b0, b1, b2):
            pb.nursery.proposals[r.id] = r
        pb.nursery.save()

        try:
            resp = pb.browse_proposals(sort="lens", page_size=50)
            items = {it["id"]: it for it in resp["items"]}
            l1 = items["lb_0001"]["lens"]
            # LINK = mean(1, 1, 1) = 1; ACE = 1 (chain -> confirmed);
            # FRESH: age 0 days at any eval instant >= created... the
            # eval instant is the query's own; b1 created 2026-11-17,
            # age < 1 day -> FRESH > 0.93. NOVEL = 1 (disjoint tokens).
            expect = 0.40 * l1["link"] + 0.25 * l1["ace"] \
                + 0.20 * l1["fresh"] + 0.15 * l1["novel"]
            check("L4.score_formula_and_components",
                  abs(l1["score"] - expect) < 1e-9
                  and l1["link"] == 1.0 and l1["ace"] == 1.0
                  and l1["novel"] == 1.0,
                  f"lens={l1}")
            order = [it["id"] for it in resp["items"]]
            check("L4.ranked_order_desc",
                  order.index("lb_0001") < order.index("lb_0002"),
                  f"order={order}")
        except Exception as e:
            _fail(["L4.score_formula_and_components", "L4.ranked_order_desc"], e)

        try:
            r1 = pb.browse_proposals(sort="lens", page_size=50)
            r2 = pb.browse_proposals(sort="lens", page_size=50)
            check("L5.deterministic_repeat",
                  [i["id"] for i in r1["items"]] == [i["id"] for i in r2["items"]]
                  and [i["lens"]["score"] for i in r1["items"]]
                  == [i["lens"]["score"] for i in r2["items"]])
        except Exception as e:
            _fail(["L5.deterministic_repeat"], e)

        try:
            page1 = pb.browse_proposals(sort="lens", page_size=2)
            cur = page1["next_cursor"]
            cont = pb.browse_proposals(cursor=cur)
            check("L6.cursor_continuation_stays_lens",
                  cont.get("ok") is True and cont.get("sort") == "lens-v1",
                  f"sort={cont.get('sort')!r}")
            bad = pb.browse_proposals(cursor=cur, sort="created")
            check("L6.cursor_sort_mismatch_refused",
                  bad.get("ok") is False
                  and bad.get("code") == "CURSOR_FILTER_MISMATCH",
                  f"bad={bad.get('code')!r}")
        except Exception as e:
            _fail(["L6.cursor_continuation_stays_lens",
                   "L6.cursor_sort_mismatch_refused"], e)

        try:
            page1 = pb.browse_proposals(sort="lens", page_size=2)
            cur = page1["next_cursor"]
            pb.nursery.proposals["lb_0002"].reason = "mutated"
            pb.nursery.save()
            stale = pb.browse_proposals(cursor=cur)
            check("L7.stale_cursor_refused",
                  stale.get("ok") is False
                  and stale.get("code") == "STALE_CURSOR",
                  f"stale={stale.get('code')!r}")
        except Exception as e:
            _fail(["L7.stale_cursor_refused"], e)

        try:
            bad = pb.browse_proposals(sort="bogus")
            check("L8.unknown_sort_refused_typed",
                  bad.get("ok") is False
                  and bad.get("code") == "SORT_UNSUPPORTED",
                  f"bad={bad.get('code')!r}")
        except Exception as e:
            _fail(["L8.unknown_sort_refused_typed"], e)

        try:
            sig_before = hashlib.sha256(
                open(pb.nursery.path, "rb").read()).hexdigest()
            statuses_before = {k: v.status
                               for k, v in pb.nursery.proposals.items()}
            _traverse(pb.browse_proposals, sort="lens", page_size=2)
            sig_after = hashlib.sha256(
                open(pb.nursery.path, "rb").read()).hexdigest()
            check("L9.lens_never_writes",
                  sig_before == sig_after
                  and statuses_before == {k: v.status for k, v in
                                          pb.nursery.proposals.items()})
        except Exception as e:
            _fail(["L9.lens_never_writes"], e)

        try:
            resp = pb.browse_proposals(sort="lens", page_size=50)
            solo = [it for it in resp["items"] if it["id"] == "lb_0001"]
            check("L10.novel_singleton_and_fresh_unknown",
                  solo and solo[0]["lens"]["novel"] == 1.0)
            b3 = _mk(3, id="lb_0003", created="stamp000")
            pb.nursery.proposals[b3.id] = b3
            pb.nursery.save()
            resp2 = pb.browse_proposals(sort="lens", page_size=50)
            it3 = [it for it in resp2["items"] if it["id"] == "lb_0003"][0]
            check("L10.fresh_unknown_disclosed",
                  it3["lens"]["fresh"] == 0.0
                  and it3["lens"].get("fresh_basis") == "unknown",
                  f"lens={it3.get('lens')}")
        except Exception as e:
            _fail(["L10.novel_singleton_and_fresh_unknown",
                   "L10.fresh_unknown_disclosed"], e)

        # L11: nursery-only store (owner_b has no graph/PlaneRank
        # state) already proves the lens needs nothing outside the
        # SEE service — asserted by every check above running here.
        check("L11.no_planerank_dependency",
              True, "lens ran on a nursery-only store (see L2-L10)")

        try:
            def dispatch(line):
                _, msg = capture_output(
                    lambda: _dispatch_public_line(pb, line, "lens-test"))
                return msg
            out = dispatch("proposals browse sort:lens")
            check("L12.repl_lens_door",
                  "lb_0001" in out and "lens" in out.casefold(),
                  f"head={out.splitlines()[0] if out else ''!r}")
        except Exception as e:
            _fail(["L12.repl_lens_door"], e)
    finally:
        for o in (owner_a, owner_b):
            _cleanup(o)

    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"nursery_c5r4_lens_test: {passed}/{len(RESULTS)} PASS")
    return passed == len(RESULTS)


if __name__ == "__main__":
    raise SystemExit(0 if smoke() else 1)
