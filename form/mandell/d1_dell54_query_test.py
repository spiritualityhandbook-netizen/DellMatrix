#!/usr/bin/env python3
"""D1 deepening circuit 10 — Dell 54 (Query) deep contract.

Derived from query_ops.apply_query (n==54) and its typed
signature (one optional role: predicate):

  ids  = list(st.selected) — the CURRENT SELECTION is the
         whole universe. Query never consults the plane:
         an idea placed after the Select is invisible to it.
  hits = [i for i in ids if _pred(lab, i)] if lab else ids
  cell = value=hits, count=len(hits), source="query",
         predicate=lab or "*"

Pinned consequences:
  - Query is READ-ONLY: st.selected is byte-identical
    after any query, matching or not. (Contrast Dell 58
    Match, which rewrites the selection.)
  - matched is a BOOLEAN (standardized by reconciliation
    R2, Director ruling 2026-10-29, superseding circuit
    10's list pin): matched = bool(hits); the hit IDs live
    in value and the quantity in count, family-consistent
    with Dell 51. An empty query reports matched=False.
  - confidence is exactly 1.0 when hits exist, else 0.0.
  - Query never fails: empty selection and no-match both
    return ok=True with value=[] and confidence 0.0.

English: there is NO English surface for Query. "query
garden" (and search/ask/show phrasings) translate to the
Dell 9 question intent and the route refuses them;
"find garden" goes to Dell 56 (Get) instead. Query is
reachable by the Mandell seed line and typed invocation
only — in the REPL and everywhere else. Pinned as a
surface fact, not changed.

Signature sync in this circuit: derived_from 24-27 ->
24-28 (the arm includes its message line), and the
output text states the selection-only universe. (R1
later shifted the arm to 28-32; R2 standardized the
matched type to Boolean — both syncs are reflected in
the current signature.)

Labels: seed execution PUBLIC_ENTRY_PATH; translate +
route_intent = the REPL's routing authority; the final
checks are the literal REPL in subprocesses (REAL_USER_PATH).
"""
from __future__ import annotations

import glob
import os
import shutil
import subprocess
import sys

RESULTS = []

STATE_DIR = os.path.join(os.path.dirname(__file__), "..", "state")


def _rec(name, cond, detail=""):
    RESULTS.append((name, bool(cond), str(detail)))


def _cleanup(owner):
    for pat in (f"program_{owner}.json", f"nursery_{owner}.json",
                f"checkpoint_{owner}_*", f"confirm_{owner}.journal.json",
                f"current_{owner}.json"):
        for f in glob.glob(os.path.join(STATE_DIR, pat)):
            try:
                os.remove(f)
            except FileNotFoundError:
                pass
            except OSError as exc:
                raise RuntimeError(f"cleanup failed for {f}: {exc}")
    d = os.path.join(STATE_DIR, f"ideas_{owner}")
    if os.path.isdir(d):
        shutil.rmtree(d)


def _fresh(owner):
    _cleanup(owner)
    from form.open import Program
    return Program(owner)


def _store(p):
    from form.mandell.core_ii_exec import attach
    return attach(p)


def _english(p, line):
    from form.mandell.translate import translate
    from form.mandell.semantic_router import route_intent
    return route_intent(p, translate(line), line)


def _repl(owner, lines):
    root = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", ".."))
    _cleanup(owner)
    proc = subprocess.run(
        [sys.executable, "-m", "form.repl", "--owner", owner],
        input=lines, capture_output=True, text=True, cwd=root,
        timeout=180)
    from form.open import Program
    p = Program.load(owner=owner)
    selected = list(_store(p).selected)
    _cleanup(owner)
    return proc.returncode, proc.stdout, selected


def _seeded(owner):
    from form.mandell.executor import execute_seed
    p = _fresh(owner)
    st = _store(p)
    p.place("garden_gate", "Garden Gate")
    p.place("garden_path", "Garden Path")
    p.place("river_stone", "River Stone")
    execute_seed(p, "51[Select]")
    return p, st


def main():
    from form.mandell.executor import execute_seed

    owner = "D154Seed"
    p = _fresh(owner)
    st = _store(p)
    r = execute_seed(p, "54[Query]")
    lr = st.last_result or {}
    _rec("query_on_empty_selection_is_valid_empty",
         r.get("ok") and lr.get("value") == []
         and lr.get("confidence") == 0.0,
         f"ok={r.get('ok')} value={lr.get('value')}")
    _cleanup(owner)

    owner = "D154Main"
    p, st = _seeded(owner)
    before = list(st.selected)
    r = execute_seed(p, "54[Query]")
    lr = st.last_result or {}
    _rec("query_all_publishes_hits_and_matched_is_bool",
         r.get("ok") and lr.get("value") == before
         and lr.get("matched") is True
         and isinstance(lr.get("matched"), bool)
         and lr.get("confidence") == 1.0
         and lr.get("source") == "query"
         and lr.get("predicate") == "*",
         f"hits={lr.get('value')} conf={lr.get('confidence')}")
    _rec("query_is_read_only_selection_unchanged",
         st.selected == before,
         f"selected={st.selected}")
    r = execute_seed(p, "54[Query] :: garden")
    lr = st.last_result or {}
    _rec("query_predicate_filters_within_selection",
         r.get("ok") and lr.get("value") == ["garden_gate",
                                              "garden_path"]
         and st.selected == before,
         f"hits={lr.get('value')}")
    r = execute_seed(p, "54[Query] :: zzz")
    lr = st.last_result or {}
    _rec("query_no_match_valid_empty_zero_confidence",
         r.get("ok") and lr.get("value") == []
         and lr.get("matched") is False and lr.get("confidence") == 0.0,
         f"ok={r.get('ok')} conf={lr.get('confidence')}")
    p.place("late_idea", "Late Idea")
    r = execute_seed(p, "54[Query]")
    lr = st.last_result or {}
    _rec("query_never_consults_the_plane",
         r.get("ok") and "late_idea" not in (lr.get("value") or [])
         and lr.get("value") == before,
         f"hits={lr.get('value')}")
    r = execute_seed(p, '54[Query](predicate="river")')
    lr = st.last_result or {}
    _rec("typed_args_query",
         r.get("ok") and lr.get("value") == ["river_stone"],
         f"hits={lr.get('value')}")
    _cleanup(owner)

    # English: no surface for Query.
    owner = "D154Eng"
    p, st = _seeded(owner)
    r = _english(p, "query garden")
    lr = st.last_result or {}
    _rec("english_query_does_not_reach_dell54",
         not r.ok and lr.get("source") != "query",
         f"ok={r.ok} error={(r.error or '')[:40]}")
    _cleanup(owner)

    # REAL_USER_PATH: the literal REPL. Query's hits are
    # observable in the REPL's printed message; the saved
    # selection must be untouched by the query.
    rc, out, selected = _repl(
        "D154ReplSeed",
        "51[Select]\n54[Query] :: wel\n10[Keep]\n")
    _rec("repl_seed_query_reports_hits_and_keeps_selection",
         rc == 0 and "Query scope=" in out and "hits=1" in out
         and selected == ["welcome"],
         f"rc={rc} selected={selected}")
    rc, out, selected = _repl(
        "D154ReplEng",
        "51[Select]\nquery garden\n10[Keep]\n")
    _rec("repl_english_query_executes_no_query",
         rc == 0 and "Query scope=" not in out
         and selected == ["welcome"],
         f"rc={rc} selected={selected}")

    # Docs sync.
    from form.mandell.signatures import get_signature
    from form.mandell.dell_cards import DEEP_NOTES
    sig = get_signature(54)
    _rec("signature_matches_code",
         sig.derived_from.endswith("28-32")
         and "Boolean" in sig.output,
         sig.derived_from)
    _rec("proof_card_carries_the_deep_note",
         54 in DEEP_NOTES and "matched" in DEEP_NOTES[54],
         DEEP_NOTES.get(54, "")[:60])

    ok = all(c for _, c, _ in RESULTS)
    for name, cond, detail in RESULTS:
        print(f"[{'ok' if cond else 'FAIL'}] {name} :: {detail}")
    n = sum(1 for _, c, _ in RESULTS if c)
    print(f"D1_DELL54_QUERY: {n}/{len(RESULTS)}")
    return ok


def smoke():
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
