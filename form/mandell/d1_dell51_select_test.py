#!/usr/bin/env python3
"""D1 deepening circuit 9 — Dell 51 (Select) deep contract.

Derived from query_ops.apply_query (n==51), core_ii_exec
_ids/_pred, and the typed signature (one optional role:
predicate):

  ids        = the keys of program.cube.session.plane.units
               (the ideas on the plane, insertion order; a
               fresh program's plane already holds 'welcome')
  no lab     -> selected = ALL ids
  lab        -> selected = [i for i in ids if _pred(lab, i)]
  _pred      = case-insensitive: lab is a substring of the
               id, OR the id starts with lab with spaces
               turned into underscores ("garden gate"
               matches 'garden_gate' by prefix, not substring)
  result     = value=list(selected), matched=bool(selected),
               count=len(selected), source="select",
               predicate=lab or "*"

Pinned consequences:
  - Select NEVER fails. A predicate matching nothing is a
    successful empty selection (ok=True, matched=False,
    count=0) — the signature's "None established" failures
    is exact. An empty selection is a result, not an error.
  - Select REPLACES the selection; it never appends.
  - Scope (Dell 53) is a real filter since reconciliation
    R1 (Director ruling 2026-10-29, superseding circuit
    9's label pin): the universe is the plane under scope
    'plane', or the named group's membership under a group
    scope. An unknown scope name refuses at Dell 53, and
    Select refuses on a dangling scope — Select's only
    failure mode; predicate outcomes still never fail.
    The full R1 proof lives in d1_recon1_scope_test.
  - The selection persists (core_ii durable state).

English: Select is NOT in the blocked set — "select
garden" routes and executes through the real route, and
in the literal REPL. Signature sync in this circuit:
derived_from pointed at 18-21 (the arm is 14-18) and the
output text now states the never-fails law and the
scope-label fact.

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


def main():
    from form.mandell.executor import execute_seed

    owner = "D151Seed"
    p = _fresh(owner)
    st = _store(p)
    p.place("garden_gate", "Garden Gate")
    p.place("garden_path", "Garden Path")
    p.place("river_stone", "River Stone")
    r = execute_seed(p, "51[Select]")
    lr = st.last_result or {}
    _rec("select_all_takes_whole_plane_in_order",
         r.get("ok") and st.selected[-3:] == ["garden_gate",
                                               "garden_path",
                                               "river_stone"]
         and "welcome" in st.selected
         and lr.get("value") == st.selected
         and lr.get("count") == len(st.selected)
         and lr.get("source") == "select"
         and lr.get("predicate") == "*"
         and lr.get("matched") is True,
         f"selected={st.selected}")
    r = execute_seed(p, "51[Select] :: garden")
    _rec("predicate_is_case_insensitive_substring",
         r.get("ok") and st.selected == ["garden_gate", "garden_path"],
         f"selected={st.selected}")
    execute_seed(p, "51[Select] :: GARDEN")
    _rec("uppercase_predicate_matches_the_same",
         st.selected == ["garden_gate", "garden_path"],
         f"selected={st.selected}")
    execute_seed(p, "51[Select] :: garden gate")
    _rec("spaced_predicate_uses_underscore_prefix",
         st.selected == ["garden_gate"],
         f"selected={st.selected}")
    r = execute_seed(p, "51[Select] :: zzz")
    lr = st.last_result or {}
    _rec("no_match_is_successful_empty_never_a_failure",
         r.get("ok") and st.selected == []
         and lr.get("matched") is False and lr.get("count") == 0
         and not lr.get("error"),
         f"ok={r.get('ok')} matched={lr.get('matched')}")
    execute_seed(p, "51[Select] :: garden")
    execute_seed(p, "51[Select] :: river")
    _rec("select_replaces_never_appends",
         st.selected == ["river_stone"],
         f"selected={st.selected}")
    r53 = execute_seed(p, "53[Scope] :: vault")
    r = execute_seed(p, "51[Select]")
    _rec("unknown_scope_refused_and_default_plane_remains",
         r53.get("ok") is False
         and "scope_unknown" in str(r53.get("error"))
         and st.scope == "plane"
         and r.get("ok") and "garden_gate" in st.selected
         and "river_stone" in st.selected
         and any("scope=plane" in m for m in r.get("messages") or []),
         f"scope={st.scope} n={len(st.selected)}")
    # Corrected contract (R1): a group scope DOES filter.
    execute_seed(p, "51[Select] :: garden")
    execute_seed(p, "82[Group] :: greens")
    execute_seed(p, "53[Scope] :: greens")
    execute_seed(p, "51[Select]")
    _rec("group_scope_filters_the_universe",
         st.selected == ["garden_gate", "garden_path"]
         and st.scope == "greens",
         f"selected={st.selected}")
    execute_seed(p, "53[Scope] :: plane")
    r = execute_seed(p, '51[Select](predicate="garden")')
    _rec("typed_args_select",
         r.get("ok") and st.selected == ["garden_gate", "garden_path"],
         f"selected={st.selected}")
    _cleanup(owner)

    # English: not blocked — routes and executes.
    owner = "D151Eng"
    p = _fresh(owner)
    st = _store(p)
    p.place("garden_gate", "Garden Gate")
    p.place("river_stone", "River Stone")
    r = _english(p, "select garden")
    _rec("english_select_routes_and_executes",
         r.ok and r.routed and st.selected == ["garden_gate"],
         f"routed={r.routed} selected={st.selected}")
    _cleanup(owner)

    # Persistence of the selection.
    owner = "D151Persist"
    p = _fresh(owner)
    st = _store(p)
    p.place("garden_gate", "Garden Gate")
    p.place("river_stone", "River Stone")
    execute_seed(p, "51[Select] :: garden")
    p.save()
    from form.open import Program
    p2 = Program.load(owner=owner)
    st2 = _store(p2)
    _rec("selection_survives_save_load",
         st2.selected == ["garden_gate"],
         f"selected={st2.selected}")
    _cleanup(owner)

    # REAL_USER_PATH: the literal REPL, both surfaces. The
    # seeded 'welcome' unit is the known universe member.
    rc, selected = _repl("D151ReplSeed", "51[Select]\n10[Keep]\n")
    _rec("repl_seed_select_lands_in_saved_state",
         rc == 0 and "welcome" in selected,
         f"rc={rc} selected={selected}")
    rc, selected = _repl("D151ReplEng", "select wel\n10[Keep]\n")
    _rec("repl_english_select_executes_in_saved_state",
         rc == 0 and selected == ["welcome"],
         f"rc={rc} selected={selected}")

    # Docs sync.
    from form.mandell.signatures import get_signature
    from form.mandell.dell_cards import DEEP_NOTES
    sig = get_signature(51)
    _rec("signature_derived_from_matches_code",
         sig.derived_from.endswith("14-22")
         and "scope-bound" in sig.output
         and "scope_unknown" in sig.failures,
         sig.derived_from)
    _rec("proof_card_carries_the_deep_note",
         51 in DEEP_NOTES and "scope" in DEEP_NOTES[51],
         DEEP_NOTES.get(51, "")[:60])

    ok = all(c for _, c, _ in RESULTS)
    for name, cond, detail in RESULTS:
        print(f"[{'ok' if cond else 'FAIL'}] {name} :: {detail}")
    n = sum(1 for _, c, _ in RESULTS if c)
    print(f"D1_DELL51_SELECT: {n}/{len(RESULTS)}")
    return ok


def smoke():
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
