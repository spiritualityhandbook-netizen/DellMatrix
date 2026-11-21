"""Part V code-stage suite — morning-report reconciliation automation.

Register rows #90 / #93 / #94 (Part V plan,
director-reports/PART_V_PLAN_2026-11-20.md sections 4-6; Director
FINAL SCOPED PLAN-CONFIRM 7052953889):

- #90: a deterministic reconciliation pass over ONE pinned register:
  pin & render proof (F1), staleness labeling (F2), drift diff vs the
  crosswalk (F3), gate & hold digest (F4), next-best recommendations
  with reason strings (F5).
- #93: the standard morning Director report format — the #90 pass's
  output format. Six fixed sections; a section that cannot be filled
  prints UNVERIFIED / its empty state, never omitted.
- #94: the NBD ranking connection — ranking reads REAL register
  status at the same pin as the report; a candidate whose row changed
  since the ranking's input pin is a STALE candidate: flagged with the
  changed field, excluded from the ranking, and listed — never
  silently re-ranked on new data and never silently dropped.

False-credit discipline (the confirm's required negatives): a
behind-main figure is never presented as current; a PARTIAL row never
blends into the COMPLETE count; a COMPLETE row is never recommended
as remaining work; drift is an alarm line, not a footnote; an
unreadable input yields UNVERIFIED, never a guessed figure.

The functions under test live in director-reports/master_list.py (the
ONE register parser; Part V owns that file):
    parse_crosswalk_rows(text) -> {n: {"status":..., "title":...}}
    drift_diff(items, crosswalk_rows) -> [DRIFT line, ...] (sorted)
    staleness(pin_sha, live_sha, pin_items, live_items)
        -> (is_stale, [delta line, ...])
    rank_next_best(current_items, pin_items, deps=None, limit=10)
        -> {"ranked": [{n, status, reason}], "stale": [{n, field, ...}]}
    render_morning(board_items, pin_sha, live_sha=None, live_items=None,
                   crosswalk_rows=None, facts=None, prev_complete=None,
                   sitting=None, top=5) -> str

Written failing-first: while those functions are absent this suite is
red. The suite plants synthetic fixtures only — no network, no gh, no
form/state, no Program().
"""
import importlib.util
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(("PASS " if cond else "FAIL ") + name +
          ((": " + detail) if (detail and not cond) else ""), flush=True)


def _load_master_list():
    path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "director-reports", "master_list.py")
    try:
        spec = importlib.util.spec_from_file_location("master_list", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception:
        return None


ML = _load_master_list()


def _fn(name):
    return getattr(ML, name, None) if ML is not None else None


# ---------------------------------------------------------------- fixtures

def _row(n, status, title=None, ids=None, block="B — fixture"):
    return {"n": n, "title": title or f"Fixture row {n}",
            "ids": ids or f"FX-{n:02d}", "status": status, "block": block}


def _register(statuses):
    return [_row(i + 1, s) for i, s in enumerate(statuses)]


def _crosswalk_text(items):
    lines = ["| MWL # | Item (short title) | Status at pin | Disposition |",
             "|---|---|---|---|"]
    for i in items:
        lines.append(f"| {i['n']} | {i['title']} | {i['status']} | CARRIED |")
    return "\n".join(lines)


PIN = "a" * 40
LIVE = "b" * 40
SITTING = {"label": "Sitting #002 (Mon 2026-11-23)", "primary": 42,
           "secondary": 39}


# ------------------------------------------------------------------- tests

def test_board_line_counts_only_complete():
    render = _fn("render_morning")
    if render is None:
        check("board_line_counts_only_complete", False, "render_morning absent")
        return
    items = _register(["COMPLETE", "PARTIAL", "OPEN", "COMPLETE",
                       "SANDBOXED", "GATED"])
    out = render(items, PIN, live_sha=PIN)
    check("board_line_counts_only_complete",
          "2/5 COMPLETE = 40.0%" in out, out.splitlines()[2] if out else "empty")


def test_neg_partial_credit_never_blended():
    render = _fn("render_morning")
    if render is None:
        check("neg_partial_credit_never_blended", False, "render_morning absent")
        return
    items = _register(["PARTIAL", "PARTIAL", "OPEN"])
    out = render(items, PIN, live_sha=PIN)
    check("neg_partial_credit_never_blended",
          "0/3 COMPLETE = 0.0%" in out and "1/3" not in out.split("## 2")[0],
          "PARTIAL rows leaked into the headline count")


def test_staleness_clean_pin_no_label():
    staleness = _fn("staleness")
    if staleness is None:
        check("staleness_clean_pin_no_label", False, "staleness absent")
        return
    items = _register(["COMPLETE", "OPEN"])
    stale, delta = staleness(PIN, PIN, items, items)
    check("staleness_clean_pin_no_label", stale is False and delta == [],
          f"stale={stale} delta={delta}")


def test_neg_stale_pin_never_presented_current():
    render = _fn("render_morning")
    staleness = _fn("staleness")
    if render is None or staleness is None:
        check("neg_stale_pin_never_presented_current", False, "functions absent")
        return
    pin_items = _register(["COMPLETE", "OPEN"])
    live_items = _register(["COMPLETE", "COMPLETE"])
    stale, delta = staleness(PIN, LIVE, pin_items, live_items)
    out = render(pin_items, PIN, live_sha=LIVE, live_items=live_items)
    board_section = out.split("## 2")[0]
    check("neg_stale_pin_never_presented_current",
          stale is True and "STALE" in board_section
          and any("#2" in d and "OPEN -> COMPLETE" in d for d in delta),
          f"stale={stale} delta={delta}")


def test_drift_none_on_matching_crosswalk():
    parse = _fn("parse_crosswalk_rows")
    drift = _fn("drift_diff")
    if parse is None or drift is None:
        check("drift_none_on_matching_crosswalk", False, "functions absent")
        return
    items = _register(["COMPLETE", "PARTIAL", "OPEN"])
    rows = parse(_crosswalk_text(items))
    check("drift_none_on_matching_crosswalk",
          len(rows) == 3 and drift(items, rows) == [],
          f"rows={len(rows)} drift={drift(items, rows)}")


def test_neg_drift_planted_status_flip_flagged_exactly():
    parse = _fn("parse_crosswalk_rows")
    drift = _fn("drift_diff")
    if parse is None or drift is None:
        check("neg_drift_planted_status_flip_flagged_exactly", False,
              "functions absent")
        return
    items = _register(["COMPLETE", "PARTIAL", "OPEN"])
    flipped = _register(["COMPLETE", "OPEN", "OPEN"])  # row 2 flipped
    rows = parse(_crosswalk_text(items))
    d = drift(flipped, rows)
    check("neg_drift_planted_status_flip_flagged_exactly",
          len(d) == 1 and "#2" in d[0] and "PARTIAL" in d[0] and "OPEN" in d[0],
          f"drift={d}")


def test_neg_drift_register_row_missing_from_crosswalk():
    parse = _fn("parse_crosswalk_rows")
    drift = _fn("drift_diff")
    if parse is None or drift is None:
        check("neg_drift_register_row_missing_from_crosswalk", False,
              "functions absent")
        return
    items = _register(["COMPLETE", "OPEN"])
    rows = parse(_crosswalk_text(items[:1]))  # crosswalk knows only row 1
    d = drift(items, rows)
    check("neg_drift_register_row_missing_from_crosswalk",
          len(d) == 1 and "#2" in d[0], f"drift={d}")


def test_neg_drift_crosswalk_row_not_in_register():
    parse = _fn("parse_crosswalk_rows")
    drift = _fn("drift_diff")
    if parse is None or drift is None:
        check("neg_drift_crosswalk_row_not_in_register", False,
              "functions absent")
        return
    items = _register(["COMPLETE"])
    rows = parse(_crosswalk_text(_register(["COMPLETE", "OPEN"])))
    d = drift(items, rows)
    check("neg_drift_crosswalk_row_not_in_register",
          len(d) == 1 and "#2" in d[0], f"drift={d}")


def test_ranking_deterministic_byte_identical():
    rank = _fn("rank_next_best")
    render = _fn("render_morning")
    if rank is None or render is None:
        check("ranking_deterministic_byte_identical", False, "functions absent")
        return
    items = _register(["OPEN", "PARTIAL", "COMPLETE", "OPEN", "PARTIAL"])
    r1 = rank(items, items)
    r2 = rank(items, items)
    o1 = render(items, PIN, live_sha=PIN)
    o2 = render(items, PIN, live_sha=PIN)
    check("ranking_deterministic_byte_identical",
          r1 == r2 and o1 == o2, "same inputs produced different outputs")


def test_ranking_finish_before_start_with_reasons():
    rank = _fn("rank_next_best")
    if rank is None:
        check("ranking_finish_before_start_with_reasons", False, "rank absent")
        return
    items = _register(["OPEN", "PARTIAL", "COMPLETE", "OPEN", "PARTIAL"])
    deps = {4: [2]}
    r = rank(items, items, deps=deps)
    order = [x["n"] for x in r["ranked"]]
    reasons_ok = all(x["reason"] for x in r["ranked"])
    dep_reason = [x for x in r["ranked"] if x["n"] == 4]
    check("ranking_finish_before_start_with_reasons",
          order == [2, 5, 1, 4] and reasons_ok
          and dep_reason and "#2" in dep_reason[0]["reason"],
          f"order={order} ranked={r['ranked']}")


def test_neg_completed_row_never_recommended():
    rank = _fn("rank_next_best")
    if rank is None:
        check("neg_completed_row_never_recommended", False, "rank absent")
        return
    items = _register(["COMPLETE", "OPEN", "GATED", "NEEDS_OVERSEER"])
    r = rank(items, items)
    check("neg_completed_row_never_recommended",
          [x["n"] for x in r["ranked"]] == [2] and r["stale"] == [],
          f"ranked={r['ranked']} stale={r['stale']}")


def test_stale_candidate_flagged_and_excluded():
    rank = _fn("rank_next_best")
    if rank is None:
        check("stale_candidate_flagged_and_excluded", False, "rank absent")
        return
    pin_items = _register(["OPEN", "PARTIAL", "OPEN"])
    now_items = _register(["OPEN", "PARTIAL", "OPEN"])
    now_items[2] = _row(3, "OPEN", title="Fixture row 3 — retitled")
    r = rank(now_items, pin_items)
    check("stale_candidate_flagged_and_excluded",
          [x["n"] for x in r["ranked"]] == [2, 1]
          and len(r["stale"]) == 1 and r["stale"][0]["n"] == 3
          and r["stale"][0]["field"] == "title",
          f"ranked={r['ranked']} stale={r['stale']}")


def test_neg_stale_candidate_not_silently_dropped():
    rank = _fn("rank_next_best")
    if rank is None:
        check("neg_stale_candidate_not_silently_dropped", False, "rank absent")
        return
    pin_items = _register(["OPEN", "OPEN"])
    now_items = _register(["COMPLETE", "OPEN"])  # row 1 finished since pin
    r = rank(now_items, pin_items)
    check("neg_stale_candidate_not_silently_dropped",
          [x["n"] for x in r["ranked"]] == [2]
          and len(r["stale"]) == 1 and r["stale"][0]["n"] == 1
          and r["stale"][0]["field"] == "status",
          f"ranked={r['ranked']} stale={r['stale']}")


def test_format_all_sections_present():
    render = _fn("render_morning")
    if render is None:
        check("format_all_sections_present", False, "render_morning absent")
        return
    items = _register(["COMPLETE", "PARTIAL", "OPEN"])
    facts = {"prs": [{"n": 504, "head": "f2dc80bd", "checks": "SUCCESS",
                      "outstanding": "Keeper CODE CONFIRM",
                      "next_owner": "Keeper"}],
             "holds": [{"name": "Q1 GATE HOLD", "authority": "Director",
                        "date": "2026-11-14", "release": "Director ruling"}]}
    out = render(items, PIN, live_sha=PIN,
                 crosswalk_rows=_fn("parse_crosswalk_rows")(
                     _crosswalk_text(items)),
                 facts=facts, prev_complete=0, sitting=SITTING)
    heads = ["## 1. Board", "## 2. Gates", "## 3. Holds", "## 4. Drift",
             "## 5. Next-best", "## 6. Sitting"]
    check("format_all_sections_present",
          all(h in out for h in heads) and "no drift" in out
          and "f2dc80bd" in out and "Q1 GATE HOLD" in out
          and "+1 COMPLETE" in out and "distance" in out,
          "a section or fixture fact is missing from the standard format")


def test_neg_missing_inputs_sections_unverified_not_omitted():
    render = _fn("render_morning")
    if render is None:
        check("neg_missing_inputs_sections_unverified_not_omitted", False,
              "render_morning absent")
        return
    items = _register(["COMPLETE", "OPEN"])
    out = render(items, PIN, live_sha=PIN)  # no crosswalk, no facts
    check("neg_missing_inputs_sections_unverified_not_omitted",
          "## 2. Gates" in out and "## 3. Holds" in out
          and "## 4. Drift" in out and out.count("UNVERIFIED") >= 3,
          "missing inputs were silently omitted instead of UNVERIFIED")


def test_neg_unreadable_register_reports_unverified():
    render = _fn("render_morning")
    if render is None:
        check("neg_unreadable_register_reports_unverified", False,
              "render_morning absent")
        return
    out = render(None, PIN, live_sha=PIN)
    check("neg_unreadable_register_reports_unverified",
          "UNVERIFIED" in out and "COMPLETE =" not in out
          and "## 1. Board" in out,
          "an unreadable register produced a figure instead of UNVERIFIED")


def main():
    test_board_line_counts_only_complete()
    test_neg_partial_credit_never_blended()
    test_staleness_clean_pin_no_label()
    test_neg_stale_pin_never_presented_current()
    test_drift_none_on_matching_crosswalk()
    test_neg_drift_planted_status_flip_flagged_exactly()
    test_neg_drift_register_row_missing_from_crosswalk()
    test_neg_drift_crosswalk_row_not_in_register()
    test_ranking_deterministic_byte_identical()
    test_ranking_finish_before_start_with_reasons()
    test_neg_completed_row_never_recommended()
    test_stale_candidate_flagged_and_excluded()
    test_neg_stale_candidate_not_silently_dropped()
    test_format_all_sections_present()
    test_neg_missing_inputs_sections_unverified_not_omitted()
    test_neg_unreadable_register_reports_unverified()
    n = sum(1 for _, ok in RESULTS if ok)
    print(f"MORNING_RECONCILIATION: {n}/{len(RESULTS)}", flush=True)
    return 0 if n == len(RESULTS) else 1


def smoke():
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
