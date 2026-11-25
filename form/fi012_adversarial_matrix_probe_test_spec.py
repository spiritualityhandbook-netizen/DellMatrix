#!/usr/bin/env python3
"""FI-012 Q-FI012.10 — ELASTIC-INTAKE ADVERSARIAL MATRIX PROBE
(Part VI — Unknowns; Uni-built artifact for the Keeper's
adversarial-matrix ruling).

Q-FI012.10 (Keeper, exact): "the adversarial matrix — which
hostile-input classes the waves must prove against (oversize,
malformed, boundary-exact, replay)." The HOLDs on this question
(Keeper 7061156434; Director 7061260190) stand until the ACTUAL
adversarial artifacts exist. This file IS the artifact: the four
named classes (plus two Uni-proposed candidate classes, marked
CANDIDATE) executed against the current intake doors, with
outcomes recorded in the run log. It implements no FI-012 wave
and settles nothing — it gives the Keeper a demonstrated matrix
to rule against.

DOORS UNDER ATTACK (current main, verified by source census):
  - the parse door: form/idea_create.py parse_create_line — the
    single parse authority (sole production caller
    form/dell_matrix/needs.py, per the Q-FI012.8 census);
  - the store door: form/dell_matrix/nursery.py Nursery.add —
    typed-refusal bounds (label 200, words 5000, reason 1000,
    origin 120, detail 2000, goals 8 x 200);
  - the composed public path: form/dell_matrix/needs.py
    parse_and_place — parse + immediate placement into the
    Plane, reporting ok=True. (This composed leg is ALSO the
    reproducible public-path failing-first the Director
    required for the four silent truncations + the unreachable
    words cap before the W4 parse wave — decision index B6.)

DOCTRINE ASSERTED (the failing-first contract, from the
Elastic Intake Doctrine): intake accepts information of any
size; a bound, where one honestly exists, refuses WITH a typed
error or grows WITH a receipt — it never silently truncates,
never crashes untyped on malformed input, never silently
rewrites authored content, and never silently duplicates on
replay. A check PASSes when the doctrine holds at that door;
it FAILs when the hostile input is silently mangled, crashes
the door, or lands without a signal. FAILs are the deliverable:
each names its class + door so the Keeper can rule the matrix
class by class.

Labels: UNIT (parse door, pure function) + INTEGRATION (store
door on temp files; composed path on an isolated owner).
State hygiene: temp dirs for store legs; a unique owner with
loud cleanup for the composed legs. Nothing touches real
program state.
"""
from __future__ import annotations

import glob
import os
import shutil
import sys
import tempfile
import time

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


def _typed_refusal(exc: BaseException) -> bool:
    """A deliberate refusal: a ValueError whose message says so.
    AttributeError/TypeError from deep inside are crashes, not
    refusals."""
    return isinstance(exc, ValueError) and (
        "refus" in str(exc) or "exceed" in str(exc)
        or "bound" in str(exc) or "must be" in str(exc))


# ---------------------------------------------------------------- parse door
def parse_door():
    from form.idea_create import parse_create_line

    def has_signal(r):
        return any("trunc" in k or "cap" in k or "refus" in k
                   or "cut" in k or "dropped" in k for k in r.keys())

    # OVERSIZE — label 10,000 chars.
    r = parse_create_line("create an idea called " + "L" * 10000 +
                          " detail: d goals: g")
    check("P_OV1_oversize_label_10000",
          len(r["label"]) == 10000 or has_signal(r),
          f"stored_label_len={len(r['label'])} signal={has_signal(r)} "
          f"(silent cut to 80 = doctrine breach)")
    # OVERSIZE — detail 1,000,000 chars (also a load measure).
    t0 = time.time()
    r = parse_create_line("create an idea called x detail: " +
                          "d" * 1000000 + " goals: g")
    dt = time.time() - t0
    check("P_OV2_oversize_detail_1M",
          len(r["detail"]) == 1000000 or has_signal(r),
          f"stored_detail_len={len(r['detail'])} signal={has_signal(r)} "
          f"elapsed={dt:.2f}s")
    # OVERSIZE — 500 goals.
    goals = "; ".join(f"goal{i}" for i in range(500))
    r = parse_create_line(f"create an idea called x detail: d goals: {goals}")
    check("P_OV3_oversize_goals_500",
          len(r["goals"]) == 500 or has_signal(r),
          f"goals_kept={len(r['goals'])} signal={has_signal(r)}")

    # BOUNDARY-EXACT — at the cap: content must survive whole.
    r = parse_create_line("create an idea called " + "B" * 80 +
                          " detail: d goals: g")
    check("P_BX1_boundary_label_80_exact", len(r["label"]) == 80,
          f"stored_label_len={len(r['label'])}")
    r = parse_create_line("create an idea called x detail: " +
                          "b" * 2000 + " goals: g")
    check("P_BX2_boundary_detail_2000_exact", len(r["detail"]) == 2000,
          f"stored_detail_len={len(r['detail'])}")
    goals = "; ".join(f"g{i}" for i in range(12))
    r = parse_create_line(f"create an idea called x detail: d goals: {goals}")
    check("P_BX3_boundary_goals_12_exact", len(r["goals"]) == 12,
          f"goals_kept={len(r['goals'])}")
    # BOUNDARY-EXACT — one past the cap: the loss begins; it must
    # be signalled, never silent.
    r = parse_create_line("create an idea called " + "B" * 81 +
                          " detail: d goals: g")
    check("P_BX4_boundary_label_81",
          len(r["label"]) == 81 or has_signal(r),
          f"stored_label_len={len(r['label'])} signal={has_signal(r)}")
    r = parse_create_line("create an idea called x detail: " +
                          "b" * 2001 + " goals: g")
    check("P_BX5_boundary_detail_2001",
          len(r["detail"]) == 2001 or has_signal(r),
          f"stored_detail_len={len(r['detail'])} signal={has_signal(r)}")
    goals = "; ".join(f"g{i}" for i in range(13))
    r = parse_create_line(f"create an idea called x detail: d goals: {goals}")
    check("P_BX6_boundary_goals_13",
          len(r["goals"]) == 13 or has_signal(r),
          f"goals_kept={len(r['goals'])} signal={has_signal(r)}")

    # MALFORMED — wrong-type inputs must meet a typed refusal,
    # never an untyped crash and never silent reinterpretation.
    for tag, raw in (("none", None), ("int", 123),
                     ("bytes", b"create an idea called x"),
                     ("list", ["create an idea called x"])):
        try:
            r = parse_create_line(raw)
            outcome = (f"returned dict (complete={r.get('complete')}, "
                       f"label={r.get('label')!r}) — silently reinterpreted")
            ok = False
        except Exception as exc:  # measuring the door's behavior
            outcome = f"{type(exc).__name__}: {exc}"
            ok = _typed_refusal(exc)
        check(f"P_MF_malformed_{tag}", ok, outcome)

    # CANDIDATE CLASS — parser-marker injection: authored detail
    # containing the literal marker "goals:" is re-parsed as
    # structure: the detail is cut at the marker, phantom goals
    # are manufactured, and the record reports complete=True for
    # an idea whose author never wrote a goals section.
    r = parse_create_line("create an idea called Inj detail: alpha goals: beta")
    check("P_INJ1_candidate_marker_injection",
          r["detail"] == "alpha goals: beta",
          f"authored_detail='alpha goals: beta' parsed_detail={r['detail']!r} "
          f"parsed_goals={r['goals']} complete={r['complete']}")
    # CANDIDATE CLASS — control characters in the label survive
    # into the record (record/log injection surface).
    r = parse_create_line("create an idea called Line1\nForged: yes "
                          "detail: d goals: g")
    check("P_INJ2_candidate_control_chars_in_label",
          "\n" not in r["label"],
          f"parsed_label={r['label']!r}")

    # REPLAY (parse leg) — determinism control: the same line
    # parsed twice must give the identical record (the parse door
    # is pure; duplication policy lives at the store, below).
    line = "create an idea called Replay detail: same words goals: one; two"
    r1, r2 = parse_create_line(line), parse_create_line(line)
    check("P_RP1_replay_parse_deterministic", r1 == r2,
          f"identical={r1 == r2}")


# ---------------------------------------------------------------- store door
def store_door():
    from form.dell_matrix import nursery as nz

    def fresh(td):
        return nz.Nursery(path=os.path.join(td, "nursery_probe.json"))

    with tempfile.TemporaryDirectory() as td:
        n = fresh(td)
        # OVERSIZE — typed refusals, nothing stored (the honest
        # bound behavior the doctrine holds up as the model).
        cases = [
            ("label_201", lambda: n.add("x" * 201), nz.NurseryLabelError),
            ("label_100k", lambda: n.add("x" * 100000), nz.NurseryLabelError),
            ("words_over", lambda: n.add("ok", words="w" * (nz.MAX_WORDS_CHARS + 1)),
             nz.NurseryWordsError),
            ("detail_over", lambda: n.add("ok", detail="d" * (nz.MAX_DETAIL_CHARS + 1)),
             nz.NurseryDetailError),
            ("goals_9", lambda: n.add("ok", goals=[f"g{i}" for i in range(9)]),
             nz.NurseryGoalsError),
            ("goal_201c", lambda: n.add("ok", goals=["g" * (nz.MAX_GOAL_CHARS + 1)]),
             nz.NurseryGoalsError),
            ("origin_over", lambda: n.add("ok", origin="o" * (nz.MAX_ORIGIN_CHARS + 1)),
             nz.NurseryOriginError),
        ]
        for tag, fn, exc_type in cases:
            before = len(n.proposals)
            try:
                fn()
                outcome, ok = "STORED (no refusal)", False
            except exc_type:
                outcome, ok = f"{exc_type.__name__} (typed refusal)", \
                    len(n.proposals) == before
            except Exception as exc:  # wrong failure mode
                outcome, ok = f"{type(exc).__name__}: {exc}", False
            check(f"S_OV_{tag}", ok, outcome)
        # BOUNDARY-EXACT — at the bound, stored whole.
        p = n.add("y" * nz.MAX_LABEL_CHARS, words="w" * nz.MAX_WORDS_CHARS)
        check("S_BX1_boundary_label200_words5000_exact",
              n.proposals[p.id].label == "y" * nz.MAX_LABEL_CHARS
              and n.proposals[p.id].words == "w" * nz.MAX_WORDS_CHARS,
              f"label_len={len(n.proposals[p.id].label)} "
              f"words_len={len(n.proposals[p.id].words)}")
        # MALFORMED — non-string / empty label, non-string goal.
        for tag, fn in (
                ("label_none", lambda: n.add(None)),
                ("label_int", lambda: n.add(123)),
                ("label_empty", lambda: n.add("")),
                ("goal_nonstring", lambda: n.add("ok", goals=[123]))):
            before = len(n.proposals)
            try:
                prop = fn()
                outcome = (f"STORED id={prop.id} label={prop.label!r} "
                           f"count {before}->{len(n.proposals)}")
                ok = False
            except Exception as exc:
                outcome = f"{type(exc).__name__}: {exc}"
                ok = _typed_refusal(exc) and len(n.proposals) == before
            check(f"S_MF_{tag}", ok, outcome)
        # MALFORMED/integrity — control characters in a label:
        # either a typed refusal, or byte-exact storage that
        # round-trips save/load unchanged. Silent alteration
        # fails.
        weird = "bad\x00label\nline2\ttab"
        try:
            prop = n.add(weird)
            n.save()
            n2 = nz.Nursery.load(n.path)
            got = n2.proposals[prop.id].label
            check("S_MF5_control_chars_roundtrip",
                  got == weird,
                  f"stored_and_reloaded={got!r} authored={weird!r}")
        except Exception as exc:
            check("S_MF5_control_chars_roundtrip",
                  _typed_refusal(exc),
                  f"{type(exc).__name__}: {exc}")
        # REPLAY — the identical intake submitted twice: either
        # deduplicated WITH a signal/receipt, or refused. Two
        # silent live duplicates fail.
        before = len(n.proposals)
        receipts_before = len(n.suppression_receipts)
        a = n.add("replay target", words="same words", kind="new",
                  origin="suite:replay", reason="matrix probe")
        b = n.add("replay target", words="same words", kind="new",
                  origin="suite:replay", reason="matrix probe")
        check("S_RP1_replay_duplicate_add",
              len(n.proposals) == before + 1
              or len(n.suppression_receipts) > receipts_before,
              f"proposals {before}->{len(n.proposals)} "
              f"ids=({a.id},{b.id}) same_id={a.id == b.id} "
              f"suppression_receipts {receipts_before}->"
              f"{len(n.suppression_receipts)}")


# ---------------------------------------------------------------- composed public path
def composed_path():
    from form.dell_matrix.needs import parse_and_place
    from form.open import open_program
    owner = "FI012CP1"
    cleanup(owner)
    p = open_program(owner)
    p.cube.session.plane.units.clear()
    # CP1 — one oversize create line end-to-end: label 300,
    # detail 5000, 20 goals. Doctrine: no silent loss under an
    # ok=True report.
    raw = ("create an idea called " + "C" * 300 +
           " detail: " + "d" * 5000 +
           " goals: " + "; ".join(f"g{i}" for i in range(20)))
    res = parse_and_place(p, raw)
    unit = p.cube.session.plane.units.get(res["id"])
    sig_keys = [k for k in res.keys()
                if "trunc" in k or "cap" in k or "refus" in k]
    check("CP1_composed_oversize_no_silent_loss",
          len(res["label"]) == 300 and len(res["detail"]) == 5000
          and len(res["goals"]) == 20,
          f"ok={res['ok']} placed_label_len={len(res['label'])} "
          f"placed_detail_len={len(res['detail'])} "
          f"placed_goals={len(res['goals'])} unit_label_len="
          f"{len(unit.label) if unit else None} signal_keys={sig_keys}")
    # CP2 — the unreachable words cap on the public path: a
    # 300-char detail yields placed words of 120 chars (the
    # [:120] derivation), not the nominal 500 the source slice
    # advertises and not the full 300 the author wrote.
    detail = "w" * 300
    res = parse_and_place(
        p, f"create an idea called Words detail: {detail} goals: g")
    unit = p.cube.session.plane.units.get(res["id"])
    words = getattr(unit, "words", None) if unit else None
    check("CP2_composed_words_effective_cap",
          words == detail,
          f"authored_detail_len=300 placed_words_len="
          f"{len(words) if words is not None else None}")
    cleanup(owner)


def main() -> int:
    print("=== FI012 ADVERSARIAL MATRIX PROBE (Q-FI012.10) ===")
    parse_door()
    store_door()
    composed_path()
    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"FI012_ADVERSARIAL_MATRIX {passed}/{len(RESULTS)} HELD")
    for name, ok in RESULTS:
        if not ok:
            print(f"  ATTACK LANDED: {name}")
    return 0 if passed == len(RESULTS) else 1


def smoke():
    return main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
