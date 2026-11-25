#!/usr/bin/env python3
"""Q-FI016.1 capability probe (Part VI — Unknowns; Ace's question).

Q-FI016.1 (Ace's own question, with his proof standard — "it has
to be calculated and proven, not just based on my opinion"):
can DellMatrix / Mandell handle database- and SQL-style
operations on ideas — set operations, indexed query, relational
joins over idea data? Status before this probe: UNKNOWN. The
discharge path Ace's record names is a measured capability probe.

This probe measures, against the REAL store machinery
(form/dell_matrix/nursery.py — the C5R.2 SEE query service):

  FUNCTIONAL analogues (fixture with known truth):
    F1  primary-key lookup (fetch_many) — exact, missing reported
    F2  term search (WHERE-like) — exact on discriminating terms
    F3  term search is lineage-aware: a child matches its
        parent's terms (observed, asserted as measured fact)
    F4  field filters (topic) + GROUP BY partition with totals
    F5  cursor pagination (LIMIT/OFFSET analogue) — exact-once
    F6  set operations — door results compose: intersection and
        difference of two query result sets equal fixture truth
    F7  join analogue — children-of-X resolved by composing the
        query door with fetch_many over parent ids (two-step);
        API census: the store exposes NO single join primitive
    F8  aggregation — group_by counts equal the fixture's
        hand-computed GROUP BY

  SCALE (the calculation): stores of 200 / 1,000 / 4,000
  proposals built in temp files; save (whole-file JSON rewrite),
  load (whole-file parse), term search, and PK lookup timed at
  each scale, with correctness re-verified at each scale. The
  printed table is the evidence; the Part VI packet carries the
  interpretation. This probe asserts NO capability claim — it
  reports measurements, per Ace's proof standard.

Labels: INTEGRATION (real Nursery on temp files). No real state
is touched.
"""
from __future__ import annotations

import os
import sys
import tempfile
import time
from pathlib import Path

REPO = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, REPO)

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def _ids(result):
    return sorted(i["id"] for i in result["items"])


def functional():
    print("--- FI-016 functional analogues (fixture, known truth) ---")
    from form.dell_matrix.nursery import Nursery
    td = tempfile.mkdtemp()
    n = Nursery(path=os.path.join(td, "fx.json"))
    a = n.add("harbor lantern alpha", words="harbor lantern craft")
    b = n.add("glacier stone beta", words="glacier stone cold",
              parents=[a.id])
    c = n.add("harbor copper gamma", words="harbor copper song",
              parents=[a.id])
    d = n.add("tundra wolf delta", words="tundra wolf fjord")
    n.organize_proposal(a.id, actor="probe", topic="harbor")
    n.organize_proposal(c.id, actor="probe", topic="harbor")
    n.organize_proposal(b.id, actor="probe", topic="stone")

    fm = n.fetch_many([a.id, c.id, "no_such_id"])
    check("F1_pk_lookup_exact",
          sorted(f["id"] for f in fm["found"]) == sorted([a.id, c.id])
          and fm["missing"] == ["no_such_id"],
          f"found={len(fm['found'])} missing={fm['missing']}")

    check("F2_term_search_exact",
          _ids(n.query(owner="probe", mode="search",
                       term="glacier")) == [b.id]
          and _ids(n.query(owner="probe", mode="search",
                       term="copper")) == [c.id]
          and n.query(owner="probe", mode="search",
                      term="zzzznope")["total_matches"] == 0,
          "glacier->{beta}, copper->{gamma}, nonsense->{}")

    check("F3_term_search_lineage_aware",
          _ids(n.query(owner="probe", mode="search",
                       term="lantern"))
          == sorted([a.id, b.id, c.id]),
          "beta (child of alpha) matches alpha's term 'lantern' "
          "— search corpus includes lineage")

    check("F4_topic_filter_and_group_partition",
          _ids(n.query(owner="probe", mode="browse",
                       topic="harbor")) == sorted([a.id, c.id]),
          "topic=harbor -> {alpha, gamma} exactly")
    g = n.query(owner="probe", mode="browse", group_by="topic")
    groups = {gr["key"]: gr["count"] for gr in g["groups"]}
    check("F8_group_by_counts",
          groups.get("harbor") == 2 and groups.get("stone") == 1
          and g["group_membership_total"] == 4
          and g["group_distinct_total"] == 4,
          f"groups={groups}")

    seen = []
    cursor = None
    while True:
        page = n.query(owner="probe", mode="browse", page_size=3,
                       cursor=cursor)
        seen.extend(i["id"] for i in page["items"])
        cursor = page["next_cursor"]
        if not cursor:
            break
    check("F5_cursor_pagination_exact_once",
          sorted(seen) == sorted([a.id, b.id, c.id, d.id])
          and len(seen) == 4,
          f"walked {len(seen)} records over pages of 3")

    harbor_set = set(_ids(n.query(owner="probe", mode="search",
                                   term="harbor")))
    stone_set = set(_ids(n.query(owner="probe", mode="browse",
                                  topic="stone")))
    check("F6_set_ops_compose",
          harbor_set & stone_set == {b.id}
          and harbor_set - stone_set == {a.id, c.id},
          "intersection/difference of two door result sets equal "
          "fixture truth (composition at the door, no set-op door)")

    children = [i["id"] for i in
                n.query(owner="probe", mode="browse")["items"]
                if a.id in (i.get("parents") or [])]
    resolved = n.fetch_many(
        sorted({p for i in
                n.query(owner="probe", mode="browse")["items"]
                for p in (i.get("parents") or [])}))
    check("F7_join_analogue_two_step",
          sorted(children) == sorted([b.id, c.id])
          and sorted(f["id"] for f in resolved["found"]) == [a.id],
          "children-of-alpha found by scan+binding; parents "
          "resolved by fetch_many — a two-step composition")
    public = [m for m in dir(Nursery) if not m.startswith("_")
              and callable(getattr(Nursery, m))]
    print(f"  Nursery public API: {public}")
    check("F7_no_join_primitive",
          not any("join" in m or "relat" in m for m in public),
          "no join/relational primitive in the store API — joins "
          "are procedural compositions, not a door")


def scale():
    print("--- FI-016 scale calculation (temp stores) ---")
    from form.dell_matrix.nursery import Nursery, Proposal, _slug
    rows = []
    for count in (200, 1000, 4000):
        td = tempfile.mkdtemp()
        path = os.path.join(td, "scale.json")
        n = Nursery(path=path)
        t0 = time.perf_counter()
        if count <= 1000:
            # Door-realistic build: add() validates, seeds
            # organization, and saves the whole file per add.
            for i in range(count):
                token = "needle" if i % 10 == 0 else "hay"
                n.add(f"{token} unit {i}",
                      words=f"{token} words {i} common filler text",
                      seed=i)
            build_mode = "door add() (per-add whole-file save)"
        else:
            # State construction only: genuine Proposal records
            # injected, then persisted through the store's own
            # save(). add()-path cost is measured at 200/1000;
            # at 4000 this measures save/load/query vs size.
            for i in range(count):
                token = "needle" if i % 10 == 0 else "hay"
                label = f"{token} unit {i}"
                pid = _slug(label, i)
                n.proposals[pid] = Proposal(
                    id=pid, label=label,
                    words=f"{token} words {i} common filler text",
                    kind="new")
            build_mode = "direct Proposal records + save()"
        t_build = time.perf_counter() - t0
        t0 = time.perf_counter()
        n.save()
        t_save = time.perf_counter() - t0
        size = os.path.getsize(path)
        t0 = time.perf_counter()
        m = Nursery.load(path)
        t_load = time.perf_counter() - t0
        t0 = time.perf_counter()
        hit = m.query(owner="probe", mode="search", term="needle")
        t_search = time.perf_counter() - t0
        want = count // 10
        t0 = time.perf_counter()
        fm = m.fetch_many(sorted(m.proposals)[:50])
        t_pk = time.perf_counter() - t0
        ok = (hit["total_matches"] == want
              and len(fm["found"]) == 50
              and len(m.proposals) == count)
        check(f"S{count}_correct_at_scale", ok,
              f"search hits={hit['total_matches']} (want {want}), "
              f"pk found={len(fm['found'])}/50")
        rows.append((count, size, t_save, t_load, t_search, t_pk))
        print(f"  N={count} [{build_mode}]: build={t_build:.3f}s "
              f"file={size}B save={t_save:.3f}s "
              f"load={t_load:.3f}s search={t_search:.4f}s "
              f"pk50={t_pk:.4f}s")
    print("  cost model (measured): save and load are whole-file "
          "operations — O(file bytes) per mutation/read; query "
          "operates on the loaded in-memory store; PK lookup is "
          "a dict hit after load.")
    return rows


def main() -> int:
    print("=== FI016 CAPABILITY PROBE (Q-FI016.1) ===")
    functional()
    scale()
    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"FI016_CAPABILITY {passed}/{len(RESULTS)}")
    return 0 if passed == len(RESULTS) else 1


def smoke():
    return main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
