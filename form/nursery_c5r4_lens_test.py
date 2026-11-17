#!/usr/bin/env python3
"""C5R.4 LENS — failing-first acceptance suite v3 (standalone).

Written BEFORE the C5R.4 build, against Uni's definitions v3
(director-reports/UNI_C5R4_LENS_DEFINITIONS_2026-11-17.md), the
Director's LENS directive (via Ace, 2026-11-17), EXE 6945952130
(PR #444), and Director source review 6946155095 (PR #468), whose
seven corrections this suite revision implements:

- S is the DEFAULT SEE ordering (not opt-in); newest/oldest/
  alphabetical are explicit alternatives; oldest pins the
  historical (created, id) order.
- ACE is explicitly MISSING in v1 (status proves no actor): zero
  contribution, weights unchanged, every score partial;
  ace_proxy (confirmed lineage) is disclosed separately and
  contributes nothing. Lineage traversal is cycle-safe and
  reports broken references.
- FRESH = reciprocal fade v1 (NOT half-life decay):
  1/(1 + age_days/tau), tau provisional uniform 14.0 days
  (Director-accepted parameter, NOT Ace's selection; Q-C5R.2
  open). age = max(0, instant - created); naive/invalid
  timestamps are disclosed missing; future dates clamp + flag.
- LINK counts UNIQUE VALIDATED parents; harmony/graph evidence
  distinguishes measured zero from missing (key absent at load)
  and malformed (out-of-range / non-numeric / non-finite), which
  is named, never clamped, never rewritten.
- NOVEL is a labeled lexical dissimilarity proxy over the
  matched corpus; corpus size disclosed; filter changes can
  change scores.
- Continuation binds the effective CONFIG identity (weights +
  fade table + function version), not just the file digest:
  config change refuses CURSOR_CONFIG_CHANGED. lens_now injects
  a frozen evaluation instant; a frozen traversal's scores are
  identical even as the wall clock advances.
- Migration: ranked_proposals keeps signature/scope/membership,
  order becomes S; the suite's consumption checks (L20) replace
  the superseded p3_r35/p3_r36 legacy-consumer assertions.
- L11 is an executed tripwire (subprocess import blocker on any
  "plane" module), not an unconditional pass.

REGISTRATION (Director clarification 6946155095): this suite is
explicitly STANDALONE at plan stage — not in form/regress.py.
Mandatory registration rides the implementation candidate.

Labels: INTEGRATION (Program API over synthetic owner stores) +
HIGH-FIDELITY DISPATCH (REPL dispatcher via capture_output) +
one SUBPROCESS tripwire. State: synthetic owners only, removed
at the end.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RESULTS = []
T = "2026-11-17T00:00:00Z"  # frozen evaluation instant


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def _fail(names, exc):
    for nm in names:
        check(nm, False, f"exc {exc!r}")


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
        created="2026-11-10T00:00:00Z",
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


def _find_rec(node, pid):
    if isinstance(node, dict):
        if node.get("id") == pid:
            return node
        for v in node.values():
            hit = _find_rec(v, pid)
            if hit is not None:
                return hit
    elif isinstance(node, list):
        for v in node:
            hit = _find_rec(v, pid)
            if hit is not None:
                return hit
    return None


def smoke() -> bool:
    from form.open import open_program
    from form.repl import _dispatch_public_line, capture_output

    suffix = uuid.uuid4().hex[:8]
    owners = []
    try:
        # ===== Fixture A: 1,000 mixed-status records =====
        owner_a = "C5R4VA" + suffix
        owners.append(owner_a)
        pa = open_program(owner_a)
        for i in range(1000):
            block = i % 20
            status = "pending" if block < 12 else (
                "confirmed" if block < 17 else "rejected")
            rec = _mk(i, status=status)
            pa.nursery.proposals[rec.id] = rec
        pa.nursery.save()

        # ===== Fixture B: hand-computed arithmetic =====
        owner_b = "C5R4VB" + suffix
        owners.append(owner_b)
        pb = open_program(owner_b)
        b0 = _mk(0, id="lb_1000", status="confirmed",
                 created="2026-11-09T00:00:00Z",
                 label="alpha base", words="alpha base")
        bx = _mk(1, id="lb_1001", parents=["lb_1000"],
                 graph_coherence=0.6, harmony=0.3,
                 supersedes_id="lb_1000",
                 created="2026-11-10T00:00:00Z",
                 label="bravo unique", words="bravo unique")
        by = _mk(2, id="lb_1002", created="2026-11-03T00:00:00Z",
                 label="charlie solo", words="charlie solo")
        for r in (b0, bx, by):
            pb.nursery.proposals[r.id] = r
        pb.nursery.save()
        # At T: S(bx)=.4*(0.5+0.6+0.3)/3 + .2*(2/3) + .15*1 = .47
        #       S(b0)=.2*(1/(1+8/14)) + .15 = .277...
        #       S(by)=.2*0.5 + .15 = .25   (ACE missing for all)

        try:
            resp = pb.browse_proposals(lens_now=T, page_size=50)
            order = [it["id"] for it in resp["items"]]
            check("L1.default_order_is_lens",
                  resp.get("sort") == "lens-v1"
                  and order == ["lb_1001", "lb_1000", "lb_1002"],
                  f"sort={resp.get('sort')!r} order={order}")
        except Exception as e:
            _fail(["L1.default_order_is_lens"], e)

        try:
            resp = pb.browse_proposals(sort="oldest", page_size=50)
            order = [it["id"] for it in resp["items"]]
            check("L2.oldest_is_historical_order",
                  order == ["lb_1002", "lb_1000", "lb_1001"],
                  f"order={order}")
        except Exception as e:
            _fail(["L2.oldest_is_historical_order"], e)

        # L21/L22 added 2026-11-17 for the Codex P2 findings on
        # PR #473 (disclosed here and in the PR): the transparency
        # contract applies to EVERY ordering, and the accepted
        # "lens-v1" alias must survive cursor continuation.
        try:
            resp = pb.browse_proposals(sort="oldest", lens_now=T,
                                       page_size=50)
            check("L21.oldest_carries_lens_disclosures",
                  resp.get("ok") is True and len(resp["items"]) == 3
                  and all("lens" in it
                          and "score" in it["lens"]
                          and "evidence" in it["lens"]
                          and "ace_proxy" in it
                          and "ace_proxy_evidence" in it
                          for it in resp["items"]),
                  f"items={len(resp.get('items') or [])}")
        except Exception as e:
            _fail(["L21.oldest_carries_lens_disclosures"], e)

        try:
            page1 = pb.browse_proposals(sort="lens-v1", lens_now=T,
                                        page_size=2)
            page2 = pb.browse_proposals(
                cursor=page1["next_cursor"], sort="lens-v1",
                lens_now=T, page_size=2)
            ids1 = [it["id"] for it in page1["items"]]
            ids2 = [it["id"] for it in page2.get("items") or []]
            check("L22.lens_v1_alias_cursor_continuation",
                  page1.get("ok") is True
                  and page2.get("ok") is True
                  and sorted(ids1 + ids2)
                  == ["lb_1000", "lb_1001", "lb_1002"]
                  and not set(ids1) & set(ids2),
                  f"p1={ids1} p2={ids2} err={page2.get('code')!r}")
        except Exception as e:
            _fail(["L22.lens_v1_alias_cursor_continuation"], e)

        try:
            base_ids, _ = _traverse(pa.browse_proposals, sort="oldest",
                                    page_size=200)
            ok = len(base_ids) == 1000
            for lens_name in ("lens", "newest", "alphabetical"):
                ids_l, _ = _traverse(pa.browse_proposals, sort=lens_name,
                                     lens_now=T, page_size=200)
                ok = ok and sorted(ids_l) == sorted(base_ids) \
                    and len(ids_l) == len(set(ids_l)) == 1000
            ids_p, _ = _traverse(pa.browse_proposals, sort="lens",
                                 status="pending", lens_now=T,
                                 page_size=200)
            ids_po, _ = _traverse(pa.browse_proposals, sort="oldest",
                                  status="pending", page_size=200)
            ok = ok and sorted(ids_p) == sorted(ids_po) and len(ids_p) == 600
            check("L3.membership_all_lenses_and_filters", ok,
                  f"pending n={len(ids_p)}")
        except Exception as e:
            _fail(["L3.membership_all_lenses_and_filters"], e)

        try:
            resp = pb.browse_proposals(lens_now=T, page_size=50)
            items = {it["id"]: it for it in resp["items"]}
            lx = items["lb_1001"]["lens"]
            exp_link = (0.5 + 0.6 + 0.3) / 3
            exp_fresh = 2 / 3
            exp_s = 0.40 * exp_link + 0.20 * exp_fresh + 0.15 * 1.0
            check("L4.arithmetic_distinct_components",
                  abs(lx["link"] - exp_link) < 1e-9
                  and abs(lx["fresh"] - exp_fresh) < 1e-9
                  and abs(lx["novel"] - 1.0) < 1e-9
                  and abs(lx["score"] - exp_s) < 1e-9
                  and lx["partial"] is True
                  and lx["evidence"]["ace"] == "missing"
                  and items["lb_1001"].get("ace_proxy") == 1.0,
                  f"lens={lx}")
        except Exception as e:
            _fail(["L4.arithmetic_distinct_components"], e)

        try:
            r1 = pb.browse_proposals(lens_now=T, page_size=50)
            r2 = pb.browse_proposals(lens_now=T, page_size=50)
            same = [i["lens"]["score"] for i in r1["items"]] == \
                   [i["lens"]["score"] for i in r2["items"]]
            page1 = pb.browse_proposals(lens_now=T, page_size=2)
            cont = pb.browse_proposals(cursor=page1["next_cursor"])
            frozen = [i["lens"]["score"] for i in page1["items"]] + \
                     [i["lens"]["score"] for i in cont["items"]] == \
                     [i["lens"]["score"] for i in r1["items"]]
            check("L5.determinism_and_frozen_continuation",
                  same and frozen)
        except Exception as e:
            _fail(["L5.determinism_and_frozen_continuation"], e)

        try:
            import form.dell_matrix.nursery as nz
            page1 = pb.browse_proposals(lens_now=T, page_size=2)
            cur = page1["next_cursor"]
            bad = pb.browse_proposals(cursor=cur, sort="newest")
            mismatch = bad.get("ok") is False \
                and bad.get("code") == "CURSOR_FILTER_MISMATCH"
            orig = getattr(nz, "LENS_FADE_DAYS", None)
            cfg_refused = False
            if isinstance(orig, dict):
                try:
                    nz.LENS_FADE_DAYS = {**orig, "unclassified": 3.0}
                    badc = pb.browse_proposals(cursor=cur)
                    cfg_refused = badc.get("ok") is False and badc.get(
                        "code") == "CURSOR_CONFIG_CHANGED"
                finally:
                    nz.LENS_FADE_DAYS = orig
            check("L6.cursor_mismatch_and_config_change_refused",
                  mismatch and cfg_refused,
                  f"mismatch={mismatch} cfg={cfg_refused}")
        except Exception as e:
            _fail(["L6.cursor_mismatch_and_config_change_refused"], e)

        try:
            page1 = pb.browse_proposals(lens_now=T, page_size=2)
            cur = page1["next_cursor"]
            pb.nursery.proposals["lb_1002"].reason = "mutated"
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
            snap_before = {k: v.to_dict()
                           for k, v in pb.nursery.proposals.items()}
            for lens_name in ("lens", "newest", "oldest", "alphabetical"):
                _traverse(pb.browse_proposals, sort=lens_name,
                          lens_now=T, page_size=2)
            sig_after = hashlib.sha256(
                open(pb.nursery.path, "rb").read()).hexdigest()
            snap_after = {k: v.to_dict()
                          for k, v in pb.nursery.proposals.items()}
            check("L9.read_only_full_records",
                  sig_before == sig_after and snap_before == snap_after)
        except Exception as e:
            _fail(["L9.read_only_full_records"], e)

        # ===== NOVEL corpus cases (fixture E) =====
        owner_e = "C5R4VE" + suffix
        owners.append(owner_e)
        try:
            pe = open_program(owner_e)
            solo = _mk(0, id="ln_0001", label="only one", words="only one")
            pe.nursery.proposals[solo.id] = solo
            pe.nursery.save()
            resp = pe.browse_proposals(lens_now=T, page_size=50)
            it = resp["items"][0]
            check("L10.novel_singleton_corpus",
                  it["lens"]["novel"] == 1.0
                  and it["lens"]["evidence"]["novel"] == "measured",
                  f"lens={it.get('lens')}")
            d1 = _mk(1, id="ln_0002", label="same tokens here",
                     words="same tokens here")
            d2 = _mk(2, id="ln_0003", label="same tokens here",
                     words="same tokens here")
            d3 = _mk(3, id="ln_0004", label="completely different zzz",
                     words="completely different zzz")
            d4 = _mk(4, id="ln_0005", label="same tokens",
                     words="same tokens")
            d5 = _mk(5, id="ln_0006", label="", words="")
            for r in (d1, d2, d3, d4, d5):
                pe.nursery.proposals[r.id] = r
            pe.nursery.save()
            resp = pe.browse_proposals(lens_now=T, page_size=50)
            items = {i["id"]: i for i in resp["items"]}
            # tokens: d1/d2 {same,tokens,here}; d4 {same,tokens}
            # J(d1,d4)=2/3 -> NOVEL(d4)=1/3; NOVEL(d1)=0 (dup of d2)
            # d3 disjoint from all -> 1.0; d5 empty -> missing/0
            check("L10.novel_duplicate_disjoint_partial_empty",
                  items["ln_0002"]["lens"]["novel"] == 0.0
                  and items["ln_0004"]["lens"]["novel"] == 1.0
                  and abs(items["ln_0005"]["lens"]["novel"] - 1 / 3) < 1e-9
                  and items["ln_0006"]["lens"]["novel"] == 0.0
                  and items["ln_0006"]["lens"]["evidence"]["novel"]
                  == "missing",
                  f"d4={items['ln_0005']['lens']}")
        except Exception as e:
            _fail(["L10.novel_singleton_corpus",
                   "L10.novel_duplicate_disjoint_partial_empty"], e)

        # ===== PlaneRank tripwire (subprocess import blocker) =====
        try:
            script = (
                "import sys\n"
                "class Blocker:\n"
                "    def find_module(self, name, path=None):\n"
                "        if 'plane' in name.casefold():\n"
                "            return self\n"
                "        return None\n"
                "    def load_module(self, name):\n"
                "        raise ImportError('plane import blocked: ' + name)\n"
                "sys.meta_path.insert(0, Blocker())\n"
                f"sys.path.insert(0, {os.path.dirname(os.path.dirname(os.path.abspath(__file__)))!r})\n"
                "from form.open import open_program\n"
                f"p = open_program({owner_b!r})\n"
                f"r = p.browse_proposals(lens_now={T!r}, page_size=5)\n"
                "assert r.get('ok'), r\n"
                "print('TRIPWIRE_OK', r['items'][0]['id'])\n"
            )
            with tempfile.NamedTemporaryFile(
                    "w", suffix=".py", delete=False) as fh:
                fh.write(script)
                script_path = fh.name
            try:
                out = subprocess.run(
                    [sys.executable, script_path], capture_output=True,
                    text=True, timeout=120)
            finally:
                os.remove(script_path)
            resp = pb.browse_proposals(lens_now=T, page_size=50)
            no_plane_keys = "plane" not in json.dumps(resp).casefold()
            check("L11.planerank_tripwire_executed",
                  out.returncode == 0 and "TRIPWIRE_OK lb_1001" in out.stdout
                  and no_plane_keys,
                  f"rc={out.returncode} out={out.stdout.strip()!r} "
                  f"err={out.stderr.strip()[-120:]!r}")
        except Exception as e:
            _fail(["L11.planerank_tripwire_executed"], e)

        # ===== REPL doors =====
        try:
            def dispatch(line, prog):
                _, msg = capture_output(
                    lambda: _dispatch_public_line(prog, line, "lens-test"))
                return msg
            out = dispatch("proposals browse", pb)
            i1, i2 = out.find("lb_1001"), out.find("lb_1002")
            door_default = i1 != -1 and i2 != -1 and i1 < i2
            import re as _re
            has_score = bool(_re.search(r"0\.\d{2,}", out))
            out_old = dispatch("proposals browse sort:oldest", pb)
            j1, j2 = out_old.find("lb_1002"), out_old.find("lb_1001")
            door_oldest = j1 != -1 and j2 != -1 and j1 < j2
            out_rank = dispatch("rank", pb)
            k1, k2 = out_rank.find("lb_1001"), out_rank.find("lb_1002")
            door_rank = k1 != -1 and k2 != -1 and k1 < k2
            check("L12.repl_doors_show_lens_order_and_scores",
                  door_default and has_score and door_oldest and door_rank,
                  f"default={door_default} score={has_score} "
                  f"oldest={door_oldest} rank={door_rank}")
        except Exception as e:
            _fail(["L12.repl_doors_show_lens_order_and_scores"], e)

        # ===== Equal S, different dates: ID tie-break =====
        owner_c = "C5R4VC" + suffix
        owners.append(owner_c)
        try:
            pc = open_program(owner_c)
            early_big_id = _mk(0, id="lt_0009", created="stamp001",
                               label="tie twin", words="tie twin")
            late_small_id = _mk(1, id="lt_0001", created="stamp002",
                                label="tie twin", words="tie twin")
            for r in (early_big_id, late_small_id):
                pc.nursery.proposals[r.id] = r
            pc.nursery.save()
            resp = pc.browse_proposals(lens_now=T, page_size=50)
            order = [it["id"] for it in resp["items"]]
            scores = [it["lens"]["score"] for it in resp["items"]]
            check("L13.equal_score_different_date_id_tiebreak",
                  order == ["lt_0001", "lt_0009"] and scores[0] == scores[1],
                  f"order={order}")
        except Exception as e:
            _fail(["L13.equal_score_different_date_id_tiebreak"], e)

        # ===== Missing vs measured; malformed (fixture D) =====
        owner_d = "C5R4VD" + suffix
        owners.append(owner_d)
        try:
            pd_ = open_program(owner_d)
            kept = _mk(0, id="lm_0001", harmony=0.0, graph_coherence=0.0)
            stripped = _mk(1, id="lm_0002", harmony=0.0,
                           graph_coherence=0.0)
            bad = _mk(2, id="lm_0003", harmony=0.0, graph_coherence=0.0)
            for r in (kept, stripped, bad):
                pd_.nursery.proposals[r.id] = r
            pd_.nursery.save()
            raw = json.loads(open(pd_.nursery.path).read())
            rec = _find_rec(raw, "lm_0002")
            rec.pop("harmony", None)
            rec.pop("graph_coherence", None)
            rec = _find_rec(raw, "lm_0003")
            rec["harmony"] = 1.7            # out of range
            rec["graph_coherence"] = "high"  # non-numeric
            with open(pd_.nursery.path, "w") as fh:
                json.dump(raw, fh)
            pd2 = open_program(owner_d)
            resp = pd2.browse_proposals(lens_now=T, page_size=50)
            items = {it["id"]: it for it in resp["items"]}
            ev_k = items["lm_0001"]["lens"]["evidence"]
            ev_s = items["lm_0002"]["lens"]["evidence"]
            ev_b = items["lm_0003"]["lens"]["evidence"]
            check("L14.measured_zero_not_missing",
                  ev_k.get("link_harmony") == "measured"
                  and ev_s.get("link_harmony") == "missing"
                  and ev_s.get("link_graph") == "missing"
                  and items["lm_0002"]["lens"]["partial"] is True,
                  f"kept={ev_k} stripped={ev_s}")
            check("L15.malformed_named_not_clamped",
                  ev_b.get("link_harmony") == "malformed"
                  and ev_b.get("link_graph") == "malformed"
                  and items["lm_0003"]["lens"]["partial"] is True
                  and pd2.nursery.proposals["lm_0003"].harmony == 1.7,
                  f"bad={ev_b} (stored 1.7 preserved, not clamped)")
            # L23 added 2026-11-17 for the Codex P2 finding on
            # PR #473: missing-evidence provenance must survive a
            # save/reload round trip — saving the loaded instance
            # must not insert default zeros that the reload then
            # reports as measured.
            pd2.nursery.save()
            raw2 = json.loads(open(pd2.nursery.path).read())
            rec2 = _find_rec(raw2, "lm_0002")
            pd3 = open_program(owner_d)
            resp3 = pd3.browse_proposals(lens_now=T, page_size=50)
            items3 = {it["id"]: it for it in resp3["items"]}
            ev_s3 = items3["lm_0002"]["lens"]["evidence"]
            ev_k3 = items3["lm_0001"]["lens"]["evidence"]
            check("L23.missing_evidence_survives_save_reload",
                  "harmony" not in rec2
                  and "graph_coherence" not in rec2
                  and ev_s3.get("link_harmony") == "missing"
                  and ev_s3.get("link_graph") == "missing"
                  and ev_k3.get("link_harmony") == "measured",
                  f"stripped={ev_s3} kept={ev_k3}")
        except Exception as e:
            _fail(["L14.measured_zero_not_missing",
                   "L15.malformed_named_not_clamped",
                   "L23.missing_evidence_survives_save_reload"], e)

        # ===== FRESH boundaries under frozen instant =====
        owner_f = "C5R4VF" + suffix
        owners.append(owner_f)
        try:
            pf = open_program(owner_f)
            recs = [
                _mk(0, id="lf_0001", created="2026-11-17T00:00:00Z"),
                _mk(1, id="lf_0002", created="2026-11-03T00:00:00Z"),
                _mk(2, id="lf_0003", created="2026-07-30T00:00:00Z"),
                _mk(3, id="lf_0004", created="2026-11-18T00:00:00Z"),
                _mk(4, id="lf_0005", created="2026-11-10 00:00:00"),
            ]
            for r in recs:
                pf.nursery.proposals[r.id] = r
            pf.nursery.save()
            resp = pf.browse_proposals(lens_now=T, page_size=50)
            items = {it["id"]: it for it in resp["items"]}
            f = {k: v["lens"]["fresh"] for k, v in items.items()}
            # BUILD CORRECTION (2026-11-17, disclosed in the build
            # PR): lf_0003's age at T is 110 days (2026-07-30 ->
            # 2026-11-17), so reciprocal fade at tau 14 gives
            # 1/(1+110/14) = 0.1129..., not the 1/11 originally
            # written here (that value implies a 140-day age).
            # The definitions v3 formula governs; the expectation
            # is corrected, the boundary intent is unchanged.
            check("L16.fresh_boundaries_frozen",
                  f["lf_0001"] == 1.0
                  and abs(f["lf_0002"] - 0.5) < 1e-9
                  and abs(f["lf_0003"] - 1 / (1 + 110 / 14)) < 1e-9
                  and f["lf_0004"] == 1.0
                  and items["lf_0004"]["lens"].get("future_dated") is True
                  and f["lf_0005"] == 0.0
                  and items["lf_0005"]["lens"]["evidence"]["fresh"]
                  == "missing",
                  f"fresh={f}")
        except Exception as e:
            _fail(["L16.fresh_boundaries_frozen"], e)

        # ===== Weight-permutation control (frozen instant) =====
        owner_g = "C5R4VG" + suffix
        owners.append(owner_g)
        try:
            pg = open_program(owner_g)
            # BUILD CORRECTION (2026-11-17, disclosed in the build
            # PR): the fixture originally named parents "x"/"y",
            # which resolve to no record in this store — under
            # definitions v3 section 3.1, LINK counts only UNIQUE
            # VALIDATED (resolving) parents, so the stated LINK=1.0
            # arithmetic was unreachable. The parents now name the
            # two other fixture records, which is what the stated
            # arithmetic (.4*1 + .15*.2) always assumed.
            a = _mk(0, id="lp_0001", parents=["lp_0002", "lp_0003"],
                    graph_coherence=1.0, harmony=1.0,
                    created="2026-11-10T00:00:00Z",
                    label="t1 t2 t3 t4 t5 t6 t7 t8 t9", words="")
            b = _mk(1, id="lp_0002", graph_coherence=0.3,
                    created="2026-11-10T00:00:00Z",
                    label="z1 z2", words="")
            c = _mk(2, id="lp_0003", created="2026-11-10T00:00:00Z",
                    label="t1 t2 t3 t4 t5 t6 t7 t8 u1", words="")
            for r in (a, b, c):
                pg.nursery.proposals[r.id] = r
            pg.nursery.save()
            # Stated: A .4*1+.15*.2=.43, B .4*.1+.15*1=.19 (+.2f both)
            # Permuted LINK<->NOVEL: B .415 > A .23. Winners disagree.
            resp = pg.browse_proposals(lens_now=T, page_size=50)
            order = [it["id"] for it in resp["items"]]
            items = {it["id"]: it for it in resp["items"]}
            check("L17.weight_permutation_control",
                  order[0] == "lp_0001"
                  and abs(items["lp_0001"]["lens"]["link"] - 1.0) < 1e-9
                  and abs(items["lp_0001"]["lens"]["novel"] - 0.2) < 1e-9
                  and abs(items["lp_0002"]["lens"]["link"] - 0.1) < 1e-9
                  and abs(items["lp_0002"]["lens"]["novel"] - 1.0) < 1e-9,
                  f"order={order}")
        except Exception as e:
            _fail(["L17.weight_permutation_control"], e)

        # ===== Lineage negatives: cycle + dangling =====
        owner_h = "C5R4VH" + suffix
        owners.append(owner_h)
        try:
            ph = open_program(owner_h)
            cyc_a = _mk(0, id="lg_0001", supersedes_id="lg_0002")
            cyc_b = _mk(1, id="lg_0002", supersedes_id="lg_0001",
                        status="confirmed")
            dangle = _mk(2, id="lg_0003", supersedes_id="lg_9999")
            for r in (cyc_a, cyc_b, dangle):
                ph.nursery.proposals[r.id] = r
            ph.nursery.save()
            resp = ph.browse_proposals(lens_now=T, page_size=50)
            items = {it["id"]: it for it in resp["items"]}
            check("L18.lineage_cycle_and_dangling_disclosed",
                  resp.get("ok") is True
                  and items["lg_0001"]["lens"]["evidence"]["ace"]
                  == "missing"
                  and items["lg_0001"].get("ace_proxy") == 1.0
                  and items["lg_0001"].get("ace_proxy_evidence")
                  == "partial"
                  and items["lg_0003"].get("ace_proxy_evidence")
                  == "partial",
                  f"a={items['lg_0001'].get('ace_proxy')} "
                  f"d={items['lg_0003'].get('ace_proxy_evidence')}")
        except Exception as e:
            _fail(["L18.lineage_cycle_and_dangling_disclosed"], e)

        # ===== Lowest-ranked pending confirms (public path) =====
        try:
            resp = pb.browse_proposals(lens_now=T, page_size=50)
            pending_ranked = [it["id"] for it in resp["items"]
                              if it["status"] == "pending"]
            last_pid = pending_ranked[-1]
            # BUILD CORRECTION (2026-11-17, disclosed in the build
            # PR): the public human path is the REPL's exact call
            # (form/repl.py manual confirm: producer "repl_user"
            # with an issued review context). A bare
            # confirm_proposal(pid) carries producer "unknown" and
            # the acceptance policy denies it by design — that
            # denial is the policy working, not the lens blocking
            # confirmation, which is what this check proves.
            result = pb.confirm_proposal(
                last_pid, _producer="repl_user",
                _review_context=pb.make_review_context(
                    last_pid, "repl_user"))
            check("L19.last_ranked_pending_confirms_public_path",
                  bool(result)
                  and pb.nursery.proposals[last_pid].status == "confirmed",
                  f"pid={last_pid}")
        except Exception as e:
            _fail(["L19.last_ranked_pending_confirms_public_path"], e)

        # ===== Consumption proof (replaces p3_r35/p3_r36 pins) =====
        owner_i = "C5R4VI" + suffix
        owners.append(owner_i)
        try:
            pi = open_program(owner_i)
            lo_g = _mk(0, id="lc_0001", created="stamp000",
                       label="twin", words="twin", graph_coherence=0.0)
            hi_g = _mk(1, id="lc_0002", created="stamp000",
                       label="twin", words="twin", graph_coherence=0.9)
            lo_h = _mk(2, id="lc_0003", created="stamp000",
                       label="twin", words="twin", harmony=0.0)
            hi_h = _mk(3, id="lc_0004", created="stamp000",
                       label="twin", words="twin", harmony=0.9)
            for r in (lo_g, hi_g, lo_h, hi_h):
                pi.nursery.proposals[r.id] = r
            pi.nursery.save()
            resp = pi.browse_proposals(lens_now=T, page_size=50)
            order = [it["id"] for it in resp["items"]]
            check("L20.consumption_graph_and_harmony_move_order",
                  order.index("lc_0002") < order.index("lc_0001")
                  and order.index("lc_0004") < order.index("lc_0003"),
                  f"order={order}")
        except Exception as e:
            _fail(["L20.consumption_graph_and_harmony_move_order"], e)
    finally:
        for o in owners:
            _cleanup(o)

    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"nursery_c5r4_lens_test: {passed}/{len(RESULTS)} PASS")
    return passed == len(RESULTS)


if __name__ == "__main__":
    raise SystemExit(0 if smoke() else 1)
