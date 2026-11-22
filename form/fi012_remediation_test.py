#!/usr/bin/env python3
"""FI-012 remediation wave — parse/store intake integrity (PR #507
remediation matrix rows 5-9, Director-accepted design map 7065903337;
Director design choices 7066291209).

The Part VI adversarial probe (Q-FI012.10) landed 18 attacks across
the parse door (form/idea_create.py parse_create_line), the store
door (form/dell_matrix/nursery.py Nursery.add) and the composed
public path (form/dell_matrix/needs.py parse_and_place). This suite
is the registered failing-first control for their fixes; each attack
leg must read HELD here under the Director's two settled choices:

(1) CP2 words: the advertised 500-char contract is preserved, not
    the undocumented 120 prefix. Words derive without silent loss
    up to the declared 500; beyond it, words is the declared excerpt
    and the whole detail is preserved beside it in the same record,
    with the cap DISCLOSED in the result (words_capped) — never a
    silent ok=True loss. needs.py's sibling [:120] derivation is
    aligned to the same 500.

(2) P_OV/P_BX/CP1 parse loss: explicit typed refusal is the default.
    Each over-bound case refuses BEFORE mutation with field name,
    authored size and supported bound, and the refusal is visible
    in the public result. Boundary-exact inputs (label 80, detail
    2000, goals 12) pass with unaltered bytes. No lossy acceptance.

Row 5 (marker injection): markers are recognized only in their
ruled syntactic position. The goals section of this grammar is a
separator-delimited list (';' / ',' / 'and'); a bare "goals:"
token inside detail prose that introduces no delimited list is
detail text, never structure — it manufactures no goals and no
completeness verdict. The trade-off is pinned openly below
(P_INJ1_single_goal_form_disclosed): a single undelimited goal is
likewise detail text, and the record honestly reports the idea
incomplete with the hint showing the delimited form. Control/forged
lines in a label are refused typed.

Row 8 (parse malformed): every non-string input meets the typed
refusal IdeaCreateError; None is never silently reinterpreted as
an empty idea.

Row 9 (store malformed + replay): Nursery.add refuses a non-string
or empty label typed (NurseryLabelError) before any mutation. The
type refusal is LABEL-ONLY by design: other fields have standing
non-string usages (the lock-order census adds with words as a
token list in a real operation — this wave's first cut refused it
and crashed that suite deterministically; the boundary is pinned
by a control leg below). The replay half collides with the
standing certified duplicate policy
(DCC-VII: duplicate adds are allowed, each gets a unique ID, both
can be confirmed and landed) — true suppression of non-token adds
is therefore not the store's contract. The matrix's observed
failure was SILENCE (two live duplicates, no signal): the fix is
that an identical still-PENDING intake from the same (seed, label)
ID stream is stored as its own proposal AND receipted on the
store's duplicate_receipts stream, naming both records — never
silent, never a false suppression claim. A different seed stream,
changed content, or a non-pending twin records no receipt.
GROW-DUP's growth:token suppression stands untouched.

Labels: UNIT (parse door, pure function) + INTEGRATION (store door
on temp files; composed path on an isolated owner with loud
cleanup). Nothing touches real program state.
"""
from __future__ import annotations

import glob
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

STATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state")

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok)))
    print(f"CHECK {name}: {'PASS' if ok else 'FAIL'} — {detail}", flush=True)
    return bool(ok)


def cleanup(owner):
    # Standing rule: cleanup errors FAIL LOUDLY, never swallowed.
    for f in glob.glob(os.path.join(STATE_DIR, f"*{owner}*")):
        if os.path.isdir(f):
            shutil.rmtree(f)
        else:
            os.remove(f)


def _idea_create_error():
    """The typed parse refusal class, or a never-matching stand-in
    while the door does not define it yet (failing-first RED must
    tally, not crash on the missing class)."""
    try:
        from form.idea_create import IdeaCreateError
        return IdeaCreateError
    except ImportError:
        return type("IdeaCreateErrorMissing", (Exception,), {})


def _refusal(fn):
    """Run fn; return (error, None) if it raised, else (None, result)."""
    try:
        return None, fn()
    except Exception as exc:  # refusal or crash — the checks decide
        return exc, None


def _is_parse_refusal(exc, field, authored, bound):
    return (isinstance(exc, _idea_create_error())
            and getattr(exc, "field", None) == field
            and getattr(exc, "authored", None) == authored
            and getattr(exc, "bound", None) == bound
            and "refus" in str(exc))


# ---------------------------------------------------------------- parse door
def parse_door():
    from form.idea_create import parse_create_line

    # OVERSIZE — typed refusal, naming field / authored / bound.
    exc, _ = _refusal(lambda: parse_create_line(
        "create an idea called " + "L" * 10000 + " detail: d goals: g; h"))
    check("P_OV1_oversize_label_10000_refused",
          _is_parse_refusal(exc, "label", 10000, 80),
          f"outcome={exc!r}")
    exc, _ = _refusal(lambda: parse_create_line(
        "create an idea called x detail: " + "d" * 1000000 + " goals: g; h"))
    check("P_OV2_oversize_detail_1M_refused",
          _is_parse_refusal(exc, "detail", 1000000, 2000),
          f"outcome={exc!r}")
    goals500 = "; ".join(f"goal{i}" for i in range(500))
    exc, _ = _refusal(lambda: parse_create_line(
        f"create an idea called x detail: d goals: {goals500}"))
    check("P_OV3_oversize_goals_500_refused",
          _is_parse_refusal(exc, "goals", 500, 12),
          f"outcome={exc!r}")

    # BOUNDARY-EXACT — at the bound, content survives whole.
    r = parse_create_line("create an idea called " + "B" * 80 +
                          " detail: d goals: g; h")
    check("P_BX1_boundary_label_80_exact", len(r["label"]) == 80,
          f"stored_label_len={len(r['label'])}")
    r = parse_create_line("create an idea called x detail: " +
                          "b" * 2000 + " goals: g; h")
    check("P_BX2_boundary_detail_2000_exact", len(r["detail"]) == 2000,
          f"stored_detail_len={len(r['detail'])}")
    goals12 = "; ".join(f"g{i}" for i in range(12))
    r = parse_create_line(f"create an idea called x detail: d goals: {goals12}")
    check("P_BX3_boundary_goals_12_exact", len(r["goals"]) == 12,
          f"goals_kept={len(r['goals'])}")

    # BOUNDARY+1 — the loss begins exactly here; it refuses typed.
    exc, _ = _refusal(lambda: parse_create_line(
        "create an idea called " + "B" * 81 + " detail: d goals: g; h"))
    check("P_BX4_boundary_label_81_refused",
          _is_parse_refusal(exc, "label", 81, 80), f"outcome={exc!r}")
    exc, _ = _refusal(lambda: parse_create_line(
        "create an idea called x detail: " + "b" * 2001 + " goals: g; h"))
    check("P_BX5_boundary_detail_2001_refused",
          _is_parse_refusal(exc, "detail", 2001, 2000), f"outcome={exc!r}")
    goals13 = "; ".join(f"g{i}" for i in range(13))
    exc, _ = _refusal(lambda: parse_create_line(
        f"create an idea called x detail: d goals: {goals13}"))
    check("P_BX6_boundary_goals_13_refused",
          _is_parse_refusal(exc, "goals", 13, 12), f"outcome={exc!r}")

    # MALFORMED — every non-string input meets the typed refusal.
    for tag, raw in (("none", None), ("int", 123),
                     ("bytes", b"create an idea called x"),
                     ("list", ["create an idea called x"])):
        exc, res = _refusal(lambda raw=raw: parse_create_line(raw))
        check(f"P_MF_malformed_{tag}",
              isinstance(exc, _idea_create_error()) and res is None
              and getattr(exc, "field", None) == "input",
              f"outcome={exc!r} res={res!r}")

    # MARKER INJECTION — a bare "goals:" token inside detail prose
    # introduces no delimited list: it stays detail text, no goals
    # are manufactured, and no completeness verdict is issued.
    r = parse_create_line("create an idea called Inj detail: alpha goals: beta")
    check("P_INJ1_marker_in_detail_stays_text",
          r["detail"] == "alpha goals: beta" and r["goals"] == []
          and r["complete"] is False,
          f"detail={r['detail']!r} goals={r['goals']} "
          f"complete={r['complete']}")
    # The disclosed other face of the same rule: an undelimited
    # single goal is detail text too — reported incomplete with the
    # hint, never silently dropped or silently accepted.
    r = parse_create_line("create an idea called Solo detail: x goals: y")
    check("P_INJ1_single_goal_form_disclosed",
          r["detail"] == "x goals: y" and r["goals"] == []
          and r["complete"] is False and "goals" in r["missing"],
          f"detail={r['detail']!r} goals={r['goals']} "
          f"complete={r['complete']} missing={r['missing']}")
    # Canonical delimited form still parses as structure (control).
    r = parse_create_line(
        "create an idea called Canon detail: d goals: exhaust; honesty")
    check("P_INJ1_canonical_goals_control",
          r["goals"] == ["exhaust", "honesty"] and r["complete"] is True,
          f"goals={r['goals']} complete={r['complete']}")

    # CONTROL/FORGED LINES IN LABEL — refused typed, never carried
    # into the record.
    exc, _ = _refusal(lambda: parse_create_line(
        "create an idea called Line1\nForged: yes detail: d goals: g; h"))
    check("P_INJ2_control_chars_in_label_refused",
          isinstance(exc, _idea_create_error())
          and getattr(exc, "field", None) == "label",
          f"outcome={exc!r}")

    # REPLAY (parse leg) — determinism control.
    line = "create an idea called Replay detail: same words goals: one; two"
    r1, r2 = parse_create_line(line), parse_create_line(line)
    check("P_RP1_replay_parse_deterministic", r1 == r2,
          f"identical={r1 == r2}")


# ---------------------------------------------------------------- words (CP2)
def words_legs():
    from form.idea_create import parse_create_line

    for n in (120, 121, 300, 499, 500):
        detail = "w" * n
        r = parse_create_line(
            f"create an idea called W{n} detail: {detail} goals: g; h")
        check(f"CP2_words_lossless_{n}",
              r["words"] == detail and "words_capped" not in r,
              f"words_len={len(r['words'])} detail_len={n}")
    # Beyond the declared 500: words is the declared excerpt, the
    # authored detail is preserved whole in the same record, and
    # the cap is disclosed in the result — not silent.
    detail = "w" * 501
    r = parse_create_line(
        f"create an idea called W501 detail: {detail} goals: g; h")
    cap = r.get("words_capped") or {}
    check("CP2_words_501_preservation_disclosed",
          r["words"] == detail[:500] and r["detail"] == detail
          and cap.get("bound") == 500 and cap.get("authored") == 501,
          f"words_len={len(r['words'])} detail_len={len(r['detail'])} "
          f"cap={cap}")
    # Unicode: the derivation counts characters, not bytes.
    detail = "é" * 300
    r = parse_create_line(
        f"create an idea called WU detail: {detail} goals: g; h")
    check("CP2_words_unicode_300", r["words"] == detail,
          f"words_len={len(r['words'])}")


# ---------------------------------------------------------------- store door
def store_door():
    from form.dell_matrix import nursery as nz

    def fresh(td):
        return nz.Nursery(path=os.path.join(td, "nursery_fi012.json"))

    with tempfile.TemporaryDirectory() as td:
        n = fresh(td)
        # MALFORMED — non-string / empty label: typed refusal,
        # nothing stored.
        for tag, fn in (
                ("label_none", lambda: n.add(None)),
                ("label_int", lambda: n.add(123)),
                ("label_empty", lambda: n.add(""))):
            before = len(n.proposals)
            try:
                prop = fn()
                outcome, ok = f"STORED id={prop.id} label={prop.label!r}", False
            except nz.NurseryLabelError as exc:
                outcome, ok = f"NurseryLabelError: {exc}", \
                    len(n.proposals) == before
            except Exception as exc:
                outcome, ok = f"{type(exc).__name__}: {exc}", False
            check(f"S_MF_{tag}", ok, outcome)
        # Boundary control — the row-9 type refusal is LABEL-ONLY:
        # standing non-string usages for other fields (the
        # lock-order census adds with words as a token list in a
        # real operation) are NOT refused.
        try:
            wp = n.add("words list tolerated", words=["lock", "census"])
            outcome, ok = f"stored id={wp.id}", True
        except Exception as exc:
            outcome, ok = f"{type(exc).__name__}: {exc}", False
        check("S_MF_words_list_tolerated_control", ok, outcome)
        # Controls — the standing typed bounds still hold.
        before = len(n.proposals)
        try:
            n.add("x" * 201)
            outcome, ok = "STORED (no refusal)", False
        except nz.NurseryLabelError:
            outcome, ok = "NurseryLabelError (typed refusal)", \
                len(n.proposals) == before
        check("S_OV_label_201_control", ok, outcome)
        before = len(n.proposals)
        try:
            n.add("ok", goals=[123])
            outcome, ok = "STORED (no refusal)", False
        except nz.NurseryGoalsError:
            outcome, ok = "NurseryGoalsError (typed refusal)", \
                len(n.proposals) == before
        check("S_MF_goal_nonstring_control", ok, outcome)
        # Control characters round-trip byte-exact (standing HELD).
        weird = "bad\x00label\nline2\ttab"
        prop = n.add(weird)
        n.save()
        n2 = nz.Nursery.load(n.path)
        check("S_MF5_control_chars_roundtrip_control",
              n2.proposals[prop.id].label == weird,
              f"reloaded={n2.proposals[prop.id].label!r}")

        # REPLAY — identical intake twice. The standing duplicate
        # policy (DCC-VII) stores BOTH, each with a unique ID; the
        # FI-012 fix is that the duplicate is never SILENT: the
        # second add records a duplicate receipt naming both
        # records, and nothing enters suppression_receipts (whose
        # entries growth accounting reconciles as true
        # suppressions).
        before = len(n.proposals)
        dup_before = len(n.duplicate_receipts)
        sup_before = len(n.suppression_receipts)
        a = n.add("replay target", words="same words", kind="new",
                  origin="suite:replay", reason="matrix probe")
        b = n.add("replay target", words="same words", kind="new",
                  origin="suite:replay", reason="matrix probe")
        dup = n.duplicate_receipts[-1] if n.duplicate_receipts else {}
        check("S_RP1_replay_duplicate_receipted_not_silent",
              len(n.proposals) == before + 2 and a.id != b.id
              and len(n.duplicate_receipts) == dup_before + 1
              and dup.get("existing_id") == a.id
              and dup.get("stored_id") == b.id
              and dup.get("reason")
              == "identical_pending_duplicate_stored"
              and len(n.suppression_receipts) == sup_before,
              f"proposals {before}->{len(n.proposals)} "
              f"ids=({a.id},{b.id}) dup_receipt={dup} "
              f"suppression_receipts {sup_before}->"
              f"{len(n.suppression_receipts)}")
        # Changed content is NOT a duplicate: stored as its own,
        # and no duplicate receipt is recorded.
        dup_before = len(n.duplicate_receipts)
        c = n.add("replay target", words="different words", kind="new",
                  origin="suite:replay", reason="matrix probe")
        check("S_RP1_changed_content_stored_no_receipt",
              c.id not in (a.id, b.id)
              and n.proposals[c.id].words == "different words"
              and len(n.duplicate_receipts) == dup_before,
              f"id={c.id} dup_receipts={len(n.duplicate_receipts)}")
        # A different seed stream is a different intake: stored as
        # its own, no duplicate receipt.
        dup_before = len(n.duplicate_receipts)
        d = n.add("replay target", words="same words", kind="new",
                  origin="suite:replay", reason="matrix probe", seed=9)
        check("S_RP1_different_seed_stored_no_receipt",
              d.id not in (a.id, b.id)
              and len(n.duplicate_receipts) == dup_before,
              f"id={d.id} dup_receipts={len(n.duplicate_receipts)}")
        # A non-pending twin does not receipt: after both pending
        # twins are rejected, the identical intake is stored as its
        # own proposal with no duplicate receipt (it is not a live
        # duplicate of anything still pending).
        n.reject(a.id)
        n.reject(b.id)
        dup_before = len(n.duplicate_receipts)
        e = n.add("replay target", words="same words", kind="new",
                  origin="suite:replay", reason="matrix probe")
        check("S_RP1_nonpending_twin_stored_no_receipt",
              e.id not in (a.id, b.id)
              and n.proposals[e.id].status == "pending"
              and len(n.duplicate_receipts) == dup_before,
              f"id={e.id} status={n.proposals[e.id].status} "
              f"dup_receipts={len(n.duplicate_receipts)}")
        # GROW-DUP control — the ruled growth:token suppression
        # keeps its original receipt reason.
        g1 = n.add("growth target", words="gw", kind="evolved",
                   origin="growth:token", reason="growth control")
        receipts_before = len(n.suppression_receipts)
        g2 = n.add("growth target", words="gw", kind="evolved",
                   origin="growth:token", reason="growth control")
        last = n.suppression_receipts[-1] if n.suppression_receipts else {}
        check("S_RP1_growdup_control",
              g1.id == g2.id
              and len(n.suppression_receipts) == receipts_before + 1
              and last.get("reason") == "identical_pending_growth_token",
              f"ids=({g1.id},{g2.id}) last_receipt={last}")


# ---------------------------------------------------------------- composed path
def composed_path():
    from form.dell_matrix.needs import parse_and_place
    from form.open import open_program

    owner = "FI012CP"
    cleanup(owner)
    p = open_program(owner)
    p.cube.session.plane.units.clear()

    # CP1 — one oversize create line end-to-end: the public result
    # refuses visibly (field / authored / bound) and NOTHING is
    # placed — no ok=True report over partial content.
    before = len(p.cube.session.plane.units)
    raw = ("create an idea called " + "C" * 300 +
           " detail: " + "d" * 5000 +
           " goals: " + "; ".join(f"g{i}" for i in range(20)))
    res = parse_and_place(p, raw)
    refusal = res.get("refusal") or {}
    check("CP1_composed_oversize_refused_not_placed",
          res.get("ok") is False and res.get("refused") is True
          and refusal.get("field") == "label"
          and refusal.get("authored") == 300
          and refusal.get("bound") == 80
          and len(p.cube.session.plane.units) == before,
          f"ok={res.get('ok')} refusal={refusal} "
          f"units {before}->{len(p.cube.session.plane.units)}")
    # The REPL-facing surface must not dress the refusal up as a
    # creation: the command result is ok=False and its message
    # never claims an idea was created.
    from form.dell_matrix.live_visual import _run_command
    out = _run_command(p, raw)
    check("CP1_public_face_refusal_visible",
          out.get("ok") is False
          and "Created idea" not in (out.get("msg") or "")
          and "refus" in (out.get("msg") or out.get("error") or ""),
          f"ok={out.get('ok')} msg={(out.get('msg') or '')[:80]!r} "
          f"error={out.get('error')!r}")
    # CP2 — the composed words contract: a 300-char detail places
    # words equal to the full authored detail.
    detail = "w" * 300
    res = parse_and_place(
        p, f"create an idea called Words detail: {detail} goals: g; h")
    unit = p.cube.session.plane.units.get(res["id"])
    words = getattr(unit, "words", None) if unit else None
    check("CP2_composed_words_effective_cap",
          res.get("ok") is True and words == detail,
          f"ok={res.get('ok')} placed_words_len="
          f"{len(words) if words is not None else None}")
    # CP2 sibling — the edit door derives words at the same 500:
    # set_detail on a unit with empty words fills words from the
    # new detail without the old silent 120 cut.
    from form.dell_matrix.needs import set_detail
    res2 = parse_and_place(p, "create an idea called EditWords")
    uid = res2["id"]
    unit2 = p.cube.session.plane.units[uid]
    unit2.words = ""
    long_detail = "e" * 300
    sd = set_detail(p, uid, long_detail)
    check("CP2_set_detail_words_aligned_500",
          sd.get("ok") is True and unit2.words == long_detail,
          f"words_len={len(unit2.words)}")
    cleanup(owner)


def main() -> int:
    print("=== FI012 REMEDIATION (rows 5-9) ===")
    parse_door()
    words_legs()
    store_door()
    composed_path()
    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"FI012_REMEDIATION {passed}/{len(RESULTS)}")
    for name, ok in RESULTS:
        if not ok:
            print(f"  ATTACK LANDED / CONTRACT OPEN: {name}")
    return 0 if passed == len(RESULTS) else 1


def smoke():
    return main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
