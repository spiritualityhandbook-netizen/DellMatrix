#!/usr/bin/env python3
"""C5R.2 SEE — failing-first suite for complete Nursery visibility.

Written BEFORE the C5R.2 build, against the Director plan
director-reports/DIRECTOR_PLAN_C5R2_SEE_2026-11-16.md (merged via
PR #460), the C5 replan AC-2.1-AC-2.4 (with the plan's corrected
status mapping: pending + confirmed + rejected; `archived` deferred
to C5R.5 and refused here), and Director frozen defaults Q-SEE.1-5
(ruling on PR #460, 2026-11-16). Ace confirmed the build in chat
2026-11-16 16:20 CST.

BEFORE behavior pinned by this suite's failures on the base head:
- No Program browse/search/get read path exists at all
  (list_proposals is pending-only; ranked_proposals is pending-only).
- The REPL has no `proposals browse|search|get` forms; `proposals`
  shows at most 20 pending and `rank` at most 12 pending, with no
  way to page past them, search fields, or see decided records.

Design answers recorded per plan section 4 (Uni, with code anchors):
(1) Cursor version = the owner file's on-disk SHA-256 (nursery.py
    _disk_sig), re-read at every page; the serving instance's _seen
    must equal it or the query refuses STALE_OWNER_STATE before
    page 1, and a generation change between pages refuses
    STALE_CURSOR. An old in-memory instance never pretends to
    represent a newer on-disk version.
(2) REPL grammar: `proposals browse [status:<s>] [size:<n>]`,
    `proposals search [status:<s>] [size:<n>] <term...>`,
    continuations `proposals browse|search cursor:<token>`,
    `proposals get <id> [id...]`. Prefix dispatch cannot shadow the
    exact-match `proposals` tuple (repl.py grounding, PR #460 cycle).
(3) Search = Unicode casefold substring over every persisted text
    field (id, label, words, kind, parents, reason, origin, detail,
    goals, created, status, lifecycle_state, supersession lineage
    IDs) plus canonical scalars (revision_number, affinity,
    harmony, graph_coherence via their str() form). Conflict
    dispositions are not proposal fields and are not searched.
(4) Default sort (created, id) ascending, id the final tie-break.
    Page size default 50, max 200; invalid sizes refuse with
    PAGE_SIZE_INVALID — never silently clamped (Q-SEE.4/5).
    Duplicate IDs in a get request collapse to first occurrence;
    the response states that policy explicitly.

Labels: INTEGRATION (Program API over a synthetic owner store) +
HIGH-FIDELITY DISPATCH (the REPL's own dispatcher via
capture_output). State touched: synthetic test owners only, in
this clone's form/state, removed at the end.
"""
from __future__ import annotations

import hashlib
import os
import re
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def _mk(i, **over):
    from form.dell_matrix.nursery import Proposal
    block = i % 20
    status = "pending" if block < 12 else ("confirmed" if block < 17 else "rejected")
    rec = dict(
        id=f"see_{i:04d}",
        label=f"seed label {i}",
        words=f"seed words {i}",
        kind="new",
        parents=[],
        affinity=0.0,
        reason="",
        created=f"stamp{(i // 10):03d}",
        status=status,
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


def _seed_1000(p):
    """Insert the canonical 1,000-record fixture and persist once."""
    planted = {
        100: dict(label="has zqxlabel inside"),
        101: dict(words="has zqxwords inside"),
        102: dict(kind="zqxkind"),
        103: dict(parents=["zqxparent"]),
        104: dict(reason="has zqxreason inside"),
        105: dict(origin="zqxorigin"),
        106: dict(detail="has zqxdetail inside"),
        107: dict(goals=["zqxgoal"]),
        108: dict(supersedes_id="zqxsupersedes"),
        109: dict(affinity=0.125),
        110: dict(lifecycle_state="zqxlifecycle"),
        500: dict(label="Straße und Meer"),
    }
    for i in range(1000):
        over = dict(planted.get(i, {}))
        if i < 40:
            over["label"] = "twin label"
        rec = _mk(i, **over)
        p.nursery.proposals[rec.id] = rec
    p.nursery.save()
    return sorted(p.nursery.proposals.values(),
                  key=lambda r: (r.created, r.id))


def _traverse(fn, **kw):
    """Collect all pages from a query callable; returns (ids, pages)."""
    ids, pages = [], []
    cursor = None
    while True:
        resp = fn(cursor=cursor, **kw)
        pages.append(resp)
        if not resp.get("ok"):
            return ids, pages
        ids.extend(it["id"] for it in resp["items"])
        if resp.get("exhausted"):
            return ids, pages
        cursor = resp.get("next_cursor")
        if not cursor:
            return ids, pages


def _cleanup(owner):
    state = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state")
    if os.path.isdir(state):
        for name in os.listdir(state):
            if owner in name:
                try:
                    os.remove(os.path.join(state, name))
                except OSError:
                    pass


def smoke() -> bool:
    from form.open import open_program
    from form.repl import _dispatch_public_line, capture_output
    from form.dell_matrix.nursery import Nursery

    suffix = uuid.uuid4().hex[:8]
    owner_a = "C5R2SA" + suffix
    owner_b = "C5R2SB" + suffix
    owner_c = "C5R2SC" + suffix
    try:
        pa = open_program(owner_a)
        expected = _seed_1000(pa)
        expected_ids = [r.id for r in expected]
        file_sig_before = hashlib.sha256(
            open(pa.nursery.path, "rb").read()).hexdigest()
        snapshot_before = {k: v.to_dict()
                           for k, v in pa.nursery.proposals.items()}

        # ---- S1: full traversal, stable order, truthful totals ----
        try:
            ids, pages = _traverse(pa.browse_proposals, page_size=200)
            check("S1.traversal_exact_set_and_order",
                  ids == expected_ids,
                  f"got {len(ids)} ids, pages={len(pages)}")
            check("S1.no_repeats", len(set(ids)) == len(ids) == 1000)
            first = pages[0]
            check("S1.totals_on_page",
                  first.get("total_inventory") == 1000
                  and first.get("total_searched") == 1000
                  and first.get("total_matches") == 1000
                  and first.get("shown") == 200,
                  f"first={ {k: first.get(k) for k in ('total_inventory', 'total_searched', 'total_matches', 'shown')} }")
            ids2, _ = _traverse(pa.browse_proposals, page_size=200)
            check("S1.second_run_byte_identical_order", ids2 == ids)
            dflt = pa.browse_proposals()
            check("S1.default_page_size_50",
                  dflt.get("ok") and dflt.get("shown") == 50
                  and dflt.get("page_size") == 50)
        except Exception as e:  # base head: API does not exist yet
            check("S1.traversal_exact_set_and_order", False, f"exc {e!r}")
            check("S1.no_repeats", False, "exc")
            check("S1.totals_on_page", False, "exc")
            check("S1.second_run_byte_identical_order", False, "exc")
            check("S1.default_page_size_50", False, "exc")

        # ---- S2: status-filtered browse keeps inventory separate ----
        try:
            rej_ids, rej_pages = _traverse(
                pa.browse_proposals, status="rejected", page_size=200)
            want_rej = [r.id for r in expected if r.status == "rejected"]
            check("S2.rejected_traversal_exact",
                  rej_ids == want_rej and len(rej_ids) == 150,
                  f"got {len(rej_ids)}")
            p0 = rej_pages[0]
            check("S2.filtered_totals",
                  p0.get("total_searched") == 150
                  and p0.get("total_matches") == 150
                  and p0.get("total_inventory") == 1000,
                  f"searched={p0.get('total_searched')} inv={p0.get('total_inventory')}")
        except Exception as e:
            check("S2.rejected_traversal_exact", False, f"exc {e!r}")
            check("S2.filtered_totals", False, "exc")

        # ---- S3: search every field, casefold, twin labels ----
        try:
            def match_ids(term, **kw):
                got, _ = _traverse(pa.search_proposals, term=term,
                                   page_size=200, **kw)
                return got
            field_cases = [
                ("zqxlabel", "see_0100"), ("zqxwords", "see_0101"),
                ("zqxkind", "see_0102"), ("zqxparent", "see_0103"),
                ("zqxreason", "see_0104"), ("zqxorigin", "see_0105"),
                ("zqxdetail", "see_0106"), ("zqxgoal", "see_0107"),
                ("zqxsupersedes", "see_0108"), ("0.125", "see_0109"),
                ("zqxlifecycle", "see_0110"),
            ]
            all_fields_ok = all(match_ids(t) == [want]
                                for t, want in field_cases)
            check("S3.every_field_searchable", all_fields_ok,
                  "label/words/kind/parents/reason/origin/detail/goals/"
                  "supersedes/affinity/lifecycle")
            check("S3.created_stamp_search",
                  len(match_ids("stamp042")) == 10)
            check("S3.status_is_a_searchable_field",
                  len(match_ids("confirmed")) == 250
                  and len(match_ids("rejected")) == 150)
            twins = match_ids("twin label")
            check("S3.identical_labels_stay_separate_hits",
                  len(twins) == 40 and len(set(twins)) == 40,
                  f"twins={len(twins)}")
            check("S3.unicode_casefold",
                  match_ids("STRASSE") == ["see_0500"]
                  and match_ids("strasse") == ["see_0500"])
            scoped = pa.search_proposals("zqxlabel", status="rejected")
            check("S3.zero_match_in_filtered_scope",
                  scoped.get("ok") and scoped.get("shown") == 0
                  and scoped.get("total_matches") == 0
                  and scoped.get("total_searched") == 150,
                  f"scoped={ {k: scoped.get(k) for k in ('shown', 'total_matches', 'total_searched')} }")
        except Exception as e:
            for nm in ("S3.every_field_searchable", "S3.created_stamp_search",
                       "S3.status_is_a_searchable_field",
                       "S3.identical_labels_stay_separate_hits",
                       "S3.unicode_casefold",
                       "S3.zero_match_in_filtered_scope"):
                check(nm, False, f"exc {e!r}")

        # ---- S4: empty store + zero-match totals ----
        try:
            pc = open_program(owner_c)
            empty = pc.browse_proposals()
            check("S4.empty_store_zero_totals",
                  empty.get("ok") and empty.get("shown") == 0
                  and empty.get("total_matches") == 0
                  and empty.get("total_searched") == 0
                  and empty.get("total_inventory") == 0
                  and empty.get("exhausted") is True)
            zm = pa.search_proposals("termthatmatchesnothing")
            check("S4.zero_match_nonempty_store",
                  zm.get("ok") and zm.get("shown") == 0
                  and zm.get("total_matches") == 0
                  and zm.get("total_searched") == 1000)
        except Exception as e:
            check("S4.empty_store_zero_totals", False, f"exc {e!r}")
            check("S4.zero_match_nonempty_store", False, "exc")

        # ---- S5: page-size discipline ----
        try:
            bad = [pa.browse_proposals(page_size=n)
                   for n in (0, -3, 201)]
            bad.append(pa.browse_proposals(page_size="abc"))
            check("S5.invalid_page_sizes_refused_typed",
                  all((not r.get("ok"))
                      and r.get("error") == "PAGE_SIZE_INVALID"
                      for r in bad),
                  f"errors={[r.get('error') for r in bad]}")
            ok200 = pa.browse_proposals(page_size=200)
            ok1 = pa.browse_proposals(page_size=1)
            check("S5.boundary_sizes_accepted",
                  ok200.get("ok") and ok1.get("ok")
                  and ok1.get("shown") == 1)
        except Exception as e:
            check("S5.invalid_page_sizes_refused_typed", False, f"exc {e!r}")
            check("S5.boundary_sizes_accepted", False, "exc")

        # ---- S6: cursor discipline ----
        try:
            page1 = pa.browse_proposals(page_size=10)
            cur = page1.get("next_cursor")
            malformed = pa.browse_proposals(cursor="!!!not-a-cursor!!!")
            check("S6.malformed_cursor_refused",
                  (not malformed.get("ok"))
                  and malformed.get("error") == "CURSOR_MALFORMED")
            pb = open_program(owner_b)
            cross = pb.browse_proposals(cursor=cur)
            check("S6.cross_owner_cursor_refused_no_leak",
                  (not cross.get("ok"))
                  and cross.get("error") == "CURSOR_OWNER_MISMATCH"
                  and not cross.get("items"),
                  f"err={cross.get('error')}")
            ext = Nursery.load(pa.nursery.path)
            ext.add("external writer probe", words="x", seed=999999)
            stale = pa.browse_proposals(cursor=cur)
            check("S6.external_write_stales_cursor",
                  (not stale.get("ok"))
                  and stale.get("error") == "STALE_CURSOR",
                  f"err={stale.get('error')}")
            stale1 = pa.browse_proposals()
            check("S6.stale_instance_refuses_page_one",
                  (not stale1.get("ok"))
                  and stale1.get("error") == "STALE_OWNER_STATE",
                  f"err={stale1.get('error')}")
            fresh = open_program(owner_a)
            retry = fresh.browse_proposals(page_size=10)
            check("S6.fresh_instance_retry_succeeds",
                  retry.get("ok") and retry.get("shown") == 10
                  and retry.get("total_inventory") == 1001)
            arch = fresh.browse_proposals(status="archived")
            check("S6.archived_status_refused_until_c5r5",
                  (not arch.get("ok"))
                  and arch.get("error") == "STATUS_UNSUPPORTED",
                  f"err={arch.get('error')}")
            # Crafted cursors with wrong field types refuse typed,
            # never crash (Codex P2 on PR #465, accepted).
            import json as _json
            def _craft(**over):
                payload = {"v": 1, "owner": owner_a, "mode": "browse",
                           "sig": None, "status": None, "term": "",
                           "size": 50, "last": None}
                payload.update(over)
                return _json.dumps(payload).encode().hex()
            crafted_ok = True
            for bc in (_craft(size="fifty"), _craft(term=7),
                       _craft(last="see_0001"),
                       _craft(last=["only-one"]),
                       _craft(mode="teleport"), _craft(owner=42)):
                try:
                    rr = fresh.browse_proposals(cursor=bc)
                    crafted_ok = crafted_ok and (
                        not rr.get("ok")
                        and rr.get("error") == "CURSOR_MALFORMED")
                except Exception:
                    crafted_ok = False
            check("S6.crafted_cursor_types_refused_not_crash",
                  crafted_ok)
            # A continuation that changes the filter/term/size must
            # refuse loudly, never silently ignore the change
            # (Director source review on PR #465, 2026-11-16).
            pg1 = fresh.browse_proposals(page_size=10)
            cur = pg1.get("next_cursor")
            chg_status = fresh.browse_proposals(
                status="pending", cursor=cur)
            chg_size = fresh.browse_proposals(
                page_size=11, cursor=cur)
            spg1 = fresh.search_proposals("see_", page_size=10)
            chg_term = fresh.search_proposals(
                "different", cursor=spg1.get("next_cursor"))
            same_args = fresh.browse_proposals(
                status=None, page_size=10, cursor=cur)
            unset_args = fresh.search_proposals(
                cursor=spg1.get("next_cursor"))
            check("S6.changed_filter_on_continuation_refused",
                  all((not r.get("ok"))
                      and r.get("error") == "CURSOR_FILTER_MISMATCH"
                      for r in (chg_status, chg_size, chg_term))
                  and same_args.get("ok")
                  and same_args.get("shown") == 10
                  and unset_args.get("ok"),
                  f"status={chg_status.get('error')} "
                  f"size={chg_size.get('error')} "
                  f"term={chg_term.get('error')}")
            pa = fresh  # continue on the fresh instance
        except Exception as e:
            for nm in ("S6.malformed_cursor_refused",
                       "S6.cross_owner_cursor_refused_no_leak",
                       "S6.external_write_stales_cursor",
                       "S6.stale_instance_refuses_page_one",
                       "S6.fresh_instance_retry_succeeds",
                       "S6.archived_status_refused_until_c5r5",
                       "S6.crafted_cursor_types_refused_not_crash",
                       "S6.changed_filter_on_continuation_refused"):
                check(nm, False, f"exc {e!r}")

        # ---- S7: ID-set retrieval, 1/16/17/100/1000, missing named ----
        try:
            def get(ids):
                return pa.get_proposals(ids)
            one = get(expected_ids[:1])
            check("S7.get_one", one.get("ok")
                  and [f["id"] for f in one["found"]] == expected_ids[:1]
                  and one["missing"] == [])
            g16 = get(expected_ids[:16])
            g17 = get(expected_ids[:17])
            check("S7.get_16_and_17_no_cap",
                  len(g16["found"]) == 16 and len(g17["found"]) == 17)
            g100 = get(expected_ids[:100])
            check("S7.get_100_in_declared_order",
                  [f["id"] for f in g100["found"]] == expected_ids[:100])
            gall = get(expected_ids)
            check("S7.get_1000", len(gall["found"]) == 1000
                  and gall["missing"] == [])
            mixed = get(expected_ids[:5] + ["missing_a", "missing_b"])
            check("S7.missing_named_individually",
                  mixed["missing"] == ["missing_a", "missing_b"]
                  and len(mixed["found"]) == 5)
            dup = get([expected_ids[0], expected_ids[0], expected_ids[1]])
            check("S7.duplicate_input_policy_exposed",
                  [f["id"] for f in dup["found"]]
                  == [expected_ids[0], expected_ids[1]]
                  and dup.get("duplicates_collapsed") == 1
                  and bool(dup.get("policy")))
        except Exception as e:
            for nm in ("S7.get_one", "S7.get_16_and_17_no_cap",
                       "S7.get_100_in_declared_order", "S7.get_1000",
                       "S7.missing_named_individually",
                       "S7.duplicate_input_policy_exposed"):
                check(nm, False, f"exc {e!r}")

        # ---- S8: read-only safety + payload immutability ----
        # Runs real queries first, so on a head without the API both
        # checks fail instead of passing vacuously.
        try:
            pa.browse_proposals(page_size=5)
            pa.search_proposals("seed")
            pa.get_proposals(expected_ids[:3])
            file_sig_after = hashlib.sha256(
                open(pa.nursery.path, "rb").read()).hexdigest()
            # owner A gained one external record in S6; the file must
            # equal exactly that post-external-write generation, i.e.
            # querying added no writes of its own: compare against a
            # fresh load's view instead of the pre-S6 digest.
            reloaded = Nursery.load(pa.nursery.path)
            same_store = ({k: v.to_dict() for k, v in
                           reloaded.proposals.items()}
                          == {k: v.to_dict() for k, v in
                              pa.nursery.proposals.items()})
            check("S8.queries_write_nothing", same_store
                  and file_sig_after == reloaded._seen)
        except Exception as e:
            check("S8.queries_write_nothing", False, f"exc {e!r}")
        try:
            victim = pa.get_proposals([expected_ids[0]])["found"][0]
            victim["label"] = "MUTATED BY TEST"
            again = pa.get_proposals([expected_ids[0]])["found"][0]
            check("S8.returned_payloads_are_copies",
                  again["label"] != "MUTATED BY TEST")
        except Exception as e:
            check("S8.returned_payloads_are_copies", False, f"exc {e!r}")

        # ---- S9: the real REPL dispatch path ----
        try:
            pb2 = open_program(owner_b)
            for i in range(60):
                rec = _mk(i, id=f"repl_{i:03d}",
                          label=(f"rpl label {i}" if i != 7
                                 else "rpl rqxtoken here"),
                          status=("pending" if i < 45 else
                                  "confirmed" if i < 55 else "rejected"))
                pb2.nursery.proposals[rec.id] = rec
            pb2.nursery.save()

            def dispatch(line):
                _, msg = capture_output(
                    lambda: _dispatch_public_line(
                        pb2, line, str(uuid.uuid4())))
                return msg

            # Prefix doors must win over content handlers: the
            # restore handler and the ":" chain parser both tried
            # to claim SEE lines (Codex P2 on PR #465, probe-found).
            outr = dispatch("proposals search restore")
            check("S9.see_door_beats_restore_handler",
                  outr.startswith("proposals search"),
                  f"head={outr.splitlines()[0] if outr else ''!r}")
            outc = dispatch("proposals browse status:pending")
            check("S9.see_door_beats_chain_parser",
                  "status: pending" in outc
                  and "total_matches 45" in outc,
                  f"head={outc.splitlines()[0] if outc else ''!r}")
            out1 = dispatch("proposals browse")
            m = re.search(r"cursor:(\S+)", out1)
            if m:
                outm = dispatch(
                    f"proposals browse status:pending "
                    f"cursor:{m.group(1)}")
                check("S9.repl_changed_filter_refused_loudly",
                      "CURSOR_FILTER_MISMATCH" in outm,
                      f"head={outm.splitlines()[0] if outm else ''!r}")
            else:
                check("S9.repl_changed_filter_refused_loudly", False,
                      "no cursor on page 1")
            check("S9.repl_browse_first_page",
                  "shown 50 of 60" in out1 and m is not None,
                  f"head={out1.splitlines()[0] if out1 else ''!r}")
            out2 = dispatch(f"proposals browse cursor:{m.group(1)}") \
                if m else ""
            check("S9.repl_browse_continuation",
                  "shown 10 of 60" in out2 and "end of results" in out2,
                  f"head={out2.splitlines()[0] if out2 else ''!r}")
            outs = dispatch("proposals search rqxtoken")
            check("S9.repl_search_finds_planted",
                  "repl_007" in outs and "total_matches 1" in outs,
                  f"out={outs.splitlines()[0] if outs else ''!r}")
            ids17 = " ".join(f"repl_{i:03d}" for i in range(17))
            outg = dispatch(f"proposals get {ids17}")
            check("S9.repl_get_beyond_16",
                  "found 17 of 17" in outg and "repl_016" in outg,
                  "17 ids through the door, SEE header stated")
            outbad = dispatch("proposals browse size:201")
            check("S9.repl_page_size_refusal_typed",
                  "PAGE_SIZE_INVALID" in outbad)
            legacy = dispatch("proposals")
            check("S9.legacy_proposals_door_preserved",
                  "proposal(s)" in legacy)
        except Exception as e:
            for nm in ("S9.repl_browse_first_page",
                       "S9.repl_browse_continuation",
                       "S9.repl_search_finds_planted",
                       "S9.repl_get_beyond_16",
                       "S9.repl_page_size_refusal_typed",
                       "S9.legacy_proposals_door_preserved"):
                check(nm, False, f"exc {e!r}")
    finally:
        for o in (owner_a, owner_b, owner_c):
            _cleanup(o)

    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"nursery_c5r2_see_test: {passed}/{len(RESULTS)} PASS")
    return passed == len(RESULTS)


if __name__ == "__main__":
    raise SystemExit(0 if smoke() else 1)
