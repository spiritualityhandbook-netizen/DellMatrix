#!/usr/bin/env python3
"""D1 deepening circuit 13 — Dell 58 (Match) deep contract.

Derived from query_ops.apply_query (n==58) and its typed
signature (role pattern, optional):

  pat = lab.lower()
  st.selected = [i for i in st.selected
                 if pat in str(i).lower()] if pat
                else list(st.selected)
  cell = value=list(selected), matched=list(selected)
         (the LIST, as Dell 54), count, source="match",
         predicate=pat or "*"

Pinned consequences:
  - Match REWRITES the selection (the destructive dual of
    Dell 54 Query's read-only search). Dropped ids leave
    the selection; chained Matches intersect.
  - The pattern test is a RAW substring on the lowercased
    id — Match does NOT use the shared predicate engine
    (_pred) that Select/Query use. DIVERGENCE, proven in
    one pair of checks: the spaced pattern 'garden gate'
    selects [garden_gate] under Dell 51's predicate but
    matches NOTHING under Dell 58, because ' ' != '_'.
    Same text, two engines, different answers. Pinned
    as-is and recorded for the Director: unifying the
    matching semantics is an architecture decision.
  - Case-insensitive (pattern and ids both lowercased).
  - Empty pattern is the identity: selection unchanged.
  - Match never fails: a no-match pattern is a valid
    empty selection (ok=True, matched=[]).
  - The narrowed selection persists (core_ii durable).

English: no surface — "match garden" / "filter garden"
become the Dell 9 question intent, refused at the route
and the REPL. The seed line is the REPL user path.

Signature sync in this circuit: derived_from 44-47 ->
54-59; output now states the destructive narrowing, the
matched-is-a-list fact, and the raw-substring divergence.

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
    return proc.returncode, selected


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

    owner = "D158Seed"
    p, st = _seeded(owner)
    r = execute_seed(p, "58[Match] :: garden")
    lr = st.last_result or {}
    _rec("match_narrows_and_publishes_the_list",
         r.get("ok") and st.selected == ["garden_gate", "garden_path"]
         and lr.get("matched") == st.selected
         and isinstance(lr.get("matched"), list)
         and lr.get("count") == 2 and lr.get("source") == "match",
         f"selected={st.selected}")
    execute_seed(p, "51[Select]")
    execute_seed(p, "58[Match] :: GARDEN")
    _rec("match_is_case_insensitive",
         st.selected == ["garden_gate", "garden_path"],
         f"selected={st.selected}")
    # The divergence pair: same text, two engines.
    execute_seed(p, "51[Select] :: garden gate")
    via_select = list(st.selected)
    execute_seed(p, "51[Select]")
    execute_seed(p, "58[Match] :: garden gate")
    _rec("spaced_pattern_diverges_from_predicate_engine",
         via_select == ["garden_gate"] and st.selected == [],
         f"select={via_select} match={st.selected}")
    execute_seed(p, "51[Select]")
    before = list(st.selected)
    r = execute_seed(p, "58[Match]")
    _rec("empty_pattern_is_identity",
         r.get("ok") and st.selected == before,
         f"selected={st.selected}")
    r = execute_seed(p, "58[Match] :: zzz")
    lr = st.last_result or {}
    _rec("no_match_is_valid_empty_never_a_failure",
         r.get("ok") and st.selected == [] and lr.get("matched") == [],
         f"ok={r.get('ok')} selected={st.selected}")
    execute_seed(p, "51[Select]")
    execute_seed(p, "58[Match] :: garden")
    execute_seed(p, "58[Match] :: gate")
    _rec("chained_matches_intersect_destructively",
         st.selected == ["garden_gate"],
         f"selected={st.selected}")
    r = execute_seed(p, '58[Match](pattern="river")')
    _rec("typed_match_sees_only_the_narrowed_selection",
         r.get("ok") and st.selected == [],
         f"selected={st.selected}")
    execute_seed(p, "51[Select]")
    r = execute_seed(p, '58[Match](pattern="river")')
    _rec("typed_match_after_reselect",
         r.get("ok") and st.selected == ["river_stone"],
         f"selected={st.selected}")
    _cleanup(owner)

    # English: no surface.
    owner = "D158Eng"
    p, st = _seeded(owner)
    r = _english(p, "match garden")
    _rec("english_match_does_not_reach_dell58",
         not r.ok and len(st.selected) == 4,
         f"ok={r.ok} n={len(st.selected)}")
    _cleanup(owner)

    # Persistence of the narrowed selection.
    owner = "D158Persist"
    p, st = _seeded(owner)
    execute_seed(p, "58[Match] :: garden")
    p.save()
    from form.open import Program
    p2 = Program.load(owner=owner)
    st2 = _store(p2)
    _rec("narrowed_selection_survives_save_load",
         st2.selected == ["garden_gate", "garden_path"],
         f"selected={st2.selected}")
    _cleanup(owner)

    # REAL_USER_PATH: the literal REPL.
    rc, selected = _repl(
        "D158ReplSeed",
        "51[Select]\n58[Match] :: wel\n10[Keep]\n")
    _rec("repl_seed_match_lands_in_saved_state",
         rc == 0 and selected == ["welcome"],
         f"rc={rc} selected={selected}")
    rc, selected = _repl(
        "D158ReplEng",
        "51[Select]\nmatch garden\n10[Keep]\n")
    _rec("repl_english_match_executes_no_match",
         rc == 0 and selected == ["welcome"],
         f"rc={rc} selected={selected}")

    # Docs sync.
    from form.mandell.signatures import get_signature
    from form.mandell.dell_cards import DEEP_NOTES
    sig = get_signature(58)
    _rec("signature_matches_code",
         sig.derived_from.endswith("54-59")
         and "RAW" in sig.output,
         sig.derived_from)
    _rec("proof_card_carries_the_deep_note",
         58 in DEEP_NOTES and "garden gate" in DEEP_NOTES[58],
         DEEP_NOTES.get(58, "")[:60])

    ok = all(c for _, c, _ in RESULTS)
    for name, cond, detail in RESULTS:
        print(f"[{'ok' if cond else 'FAIL'}] {name} :: {detail}")
    n = sum(1 for _, c, _ in RESULTS if c)
    print(f"D1_DELL58_MATCH: {n}/{len(RESULTS)}")
    return ok


def smoke():
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
