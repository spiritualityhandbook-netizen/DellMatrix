#!/usr/bin/env python3
"""C5R.1 HOLD — failing-first READ-PATH tests (precondition (iii),
AC-1.2 half).

Written BEFORE the C5R.1 build, against AC-1.2 of the merged replan
(director-reports/C5_REPLAN_2026-11-15.md, PR #450):

  "Every read path (list, ranked, browse, ghost/all-entities) reports
   counts that AGREE with the store's true count; any view that shows
   a subset states shown/total on its face (the R42 defect class is
   closed)."

Companion to form/nursery_c5r1_holding_test.py (the persistence half,
H1-H9). This suite pins the display/read layer at the current head
(main 2e9655a3, which includes merged main cad6a43b + Keeper records;
the read-path code is byte-identical to cad6a43b).

Grounding (FACT, from code at this head):
- Program.list_proposals() (form/open.py) returns ALL pending
  proposals; Program.ranked_proposals() returns ALL of them ranked.
  The Program API does not subset. (R1/R2 pin this — expected PASS.)
- REPL _show_proposals (form/repl.py, the `proposals` door) prints
  "Nursery has {total} proposal(s):" then iterates pending[:20]
  with NO shown count anywhere. With 25 pending it silently shows
  20. (R3 — expected FAIL first.)
- REPL `rank` handler iterates ranked[:12] after a "Ranked {total}"
  header, with NO shown count. (R4 — expected FAIL first.)
- Program.all_entities() appends ranked_proposals()[:12] as
  nursery_ghost entities and returns a bare list with NO total
  metadata. With 25 pending the ghost count is 12 — this is the
  R42 defect itself (wave 8: 15 pending -> 12 ghost entries, no
  total anywhere). (R5 — expected FAIL first.)
- REPL `entities` door groups all_entities() by kind and prints
  "[nursery_ghost] x{len(items)}" — it inherits the capped 12 and
  presents it as the count, disagreeing with the true 25.
  (R6 — expected FAIL first.)
- Program.look_report() appends an "Entities: ... nursery_ghost=N"
  line counted from all_entities() — same capped count.
  (R7 — expected FAIL first.)

The pinned contract for a subset view is stated-shown/total: the
view's output must carry BOTH the number actually shown and the
true total in an explicit shown/total form (e.g. "20 of 25",
"20/25", "Showing 20 of 25"). A header stating only the total,
while silently showing fewer, does NOT satisfy it. For
all_entities() the contract is count agreement: the ghost entries
returned must equal the true pending count (the function's own
docstring promises an "Inventory of every entity on stage"), or
the return must carry the true total alongside the subset — a
bare list cannot, so count agreement is the only passing shape
at this API.

Browse: no distinct Nursery browse read path exists at this head
(the paged browse is C5R.2's build, AC-2.1). AC-1.2's browse leg
is therefore not pinnable as a failing check here and is NOT
asserted; it is dispositioned in the evidence note as C5R.2 scope,
not silently passed.

Labels: INTEGRATION / HIGH-FIDELITY DISPATCH (the REPL's own
dispatcher via capture_output, synthetic throwaway owner) +
INTEGRATION for the Program API checks. No owner state outside
the synthetic test owner in this clone is touched.
"""
from __future__ import annotations

import os
import re
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def _states_shown_total(text, shown, total):
    """True iff `text` explicitly states `shown` of `total`."""
    pats = [
        rf"\b{shown}\s*(?:of|/)\s*{total}\b",
        rf"[Ss]howing\s+{shown}\b",
        rf"[Ss]hown[:\s]+{shown}\b",
    ]
    return any(re.search(p, text) for p in pats)


def smoke() -> bool:
    from form.open import open_program
    from form.repl import _dispatch_public_line, capture_output

    owner = "C5R1RP" + uuid.uuid4().hex[:8]
    p = open_program(owner)

    N = 25
    for i in range(N):
        p.nursery.add(f"readpath probe {i:02d}", words=f"w{i}", seed=i)
    true_pending = p.nursery.summary()["pending"]

    def dispatch(line):
        _, msg = capture_output(
            lambda: _dispatch_public_line(p, line, str(uuid.uuid4())))
        return msg

    # R1/R2: Program API agreement (expected PASS — pins that the
    # defect is in the display layer, not the store/API).
    listed = p.list_proposals()
    check("R1.list_proposals_count_agrees",
          len(listed) == true_pending == N,
          f"listed={len(listed)} true={true_pending}")
    ranked = p.ranked_proposals()
    check("R2.ranked_proposals_count_agrees",
          len(ranked) == true_pending
          and {r['id'] for r in ranked} == {r['id'] for r in listed},
          f"ranked={len(ranked)} true={true_pending}")

    # R3: REPL `proposals` door — subset must state shown/total.
    out = dispatch("proposals")
    shown_list = len(re.findall(r"^\s+\d+\.\s+aff=", out, re.M))
    check("R3.list_view_states_shown_total",
          shown_list == N or _states_shown_total(out, shown_list, N),
          f"shown={shown_list} true={N} stated={_states_shown_total(out, shown_list, N)}")

    # R4: REPL `rank` door — subset must state shown/total.
    out = dispatch("rank")
    shown_rank = len(re.findall(r"^\s+\d+\.\s+aff=", out, re.M))
    check("R4.rank_view_states_shown_total",
          shown_rank == N or _states_shown_total(out, shown_rank, N),
          f"shown={shown_rank} true={N} stated={_states_shown_total(out, shown_rank, N)}")

    # R5: all_entities ghost count must agree with the true count.
    ents = p.all_entities()
    ghosts = [e for e in ents if e.get("kind") == "nursery_ghost"]
    check("R5.all_entities_ghost_count_agrees",
          len(ghosts) == true_pending,
          f"ghosts={len(ghosts)} true={true_pending}")

    # R6: REPL `entities` door ghost count must agree.
    out = dispatch("entities")
    m = re.search(r"\[nursery_ghost\]\s*.(\d+)", out)
    stated = int(m.group(1)) if m else -1
    check("R6.entities_view_ghost_count_agrees",
          stated == true_pending,
          f"stated={stated} true={true_pending}")

    # R7: look_report Entities line ghost count must agree.
    lines = p.look_report()
    ent_line = next((ln for ln in lines if ln.startswith("Entities:")), "")
    m = re.search(r"nursery_ghost=(\d+)", ent_line)
    stated = int(m.group(1)) if m else -1
    check("R7.look_report_ghost_count_agrees",
          stated == true_pending,
          f"stated={stated} true={true_pending} line={ent_line!r}")

    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"nursery_c5r1_readpath_test: {passed}/{len(RESULTS)} PASS")
    return passed == len(RESULTS)


if __name__ == "__main__":
    raise SystemExit(0 if smoke() else 1)
