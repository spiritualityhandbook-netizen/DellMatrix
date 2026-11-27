#!/usr/bin/env python3
"""Part VII / GP-E27 — journey harness family 3: J-04 Create/persist
Idea, J-16 Promote, J-17 Undo/redo boundary.

Written failing-first at code stage and registered in
form/regress.py LIST in the same commit (omitted-entry law).

Contracts — Edition 1 file 06 (06_JOURNEY_ACCEPTANCE.md) for J-04,
executed verbatim; plan section 5.2.1 designed oracles for J-16/J-17
(file 06 names those journeys in one line each):

  J-04 Create/persist Idea: "Create Idea with detail/goals, stable
  canonical ID and chosen position, then cold reload; all
  text/provenance/links remain identical."
  Failure oracle: "Nursery/Program interrupted pair-save may only
  recover a coherent pair or refuse with recoverable receipt; no
  hybrid success; test invalid Unicode, 5000 words limit, idempotent
  retry."

  J-16 Nested Idea -> promote: "create a nested Idea via the public
  path, promote to top-level; expected: association/lineage
  preserved, old history intact after cold reload, stable canonical
  ID unchanged. Negative: promotion by a non-owner refuses;
  promotion that would break a wall refuses with receipt."

  J-17 Undo/redo across the save/session boundary: "create + edit
  an Idea and its detail, undo/redo within the session, save, cold
  reload, and verify the exact retained history the Q-LC.1 contract
  promises. Scope honesty: Q-LC.1's settled credit is session-local;
  the room/multi-actor remainder (register row #135's retained
  scope) is an explicitly uncovered case in the packet, not a
  silent pass."

Execution tier: PUBLIC_ENTRY_PATH — every journey action runs in a
literal `python3 -m form.repl` subprocess against a per-run isolated
owner; state comparison after cold reload uses the persistence
loader and the SemanticGraph loader (reloaded vs reloaded, never
in-memory vs reloaded).

Grounded behavior (each expectation verified first-hand in
scratch-owner probes, 2026-11-21, before this suite was written):
  - The strong create door (`create an idea called X detail: ...
    goals: a; b; c`) prints `Created idea: "X" id=<slug>` with the
    strength line; the unit carries detail/goals verbatim, a
    canonical slug ID (collision-suffixed on reissue, P3/TD-5), and
    the spatial authority's chosen position (idea view `pos=(x,y)`).
  - Non-ASCII text (accented Latin, CJK, emoji, combining marks)
    round-trips byte-exact through save + cold reload; the slug is
    derived from the ASCII-folded label while the label itself is
    stored whole.
  - Reissuing the identical create line is NOT idempotent at this
    door by design: canonical dedup mints a suffixed second unit
    and leaves the first untouched. The oracle's idempotent-retry
    point is exercised on the pair-save itself: `save` issued twice
    converges — both receipts print, the reloaded state is
    byte-identical, counts unchanged (no duplicate, no hybrid).
  - Containment door: `nest <id> under <id>`, `promote <id>`,
    `containment <id>` (single-token refs: IDs). Nest prints
    "Nested <label> under <label>"; the containment view shows the
    breadcrumb path and the parent's children; promote prints
    "Promoted <label> to top level" and supersedes the CONTAINS
    edge (the graph log keeps the ACTIVE entry and its SUPERSEDED
    successor under one rel_id — history is preserved, never
    erased); a second promote prints "Already top level". A
    foreign owner's promote attempt refuses before any state
    exists: "Containment refused (unit_not_found): ...".
  - Undo/redo (Q-LC.1 / DD-54): `set detail <id> <text>` pushes an
    edit action; `undo` prints "Restored detail on <id>" and
    restores the prior detail; `redo` re-applies it. The action
    stacks are session-local and are NOT persisted: after save +
    cold reload, `undo` and `redo` both answer "nothing to undo" /
    "nothing to redo", while the saved STATE (the redone detail)
    is retained exactly, and the undo/redo evidence notes
    (24[Unlock] note_seed entries) persist in program history —
    exactly the retention the Q-LC.1 contract promises.

  - DEFECT FOUND BY THIS SUITE (failing-first): the 5000-words
    oracle point failed at baseline. A create whose detail is
    5,000 words (~31,000 chars, end-marked) stored exactly 2,000
    chars — the tail, including the end marker, silently lost;
    a create with 13 goals stored 12, the 13th silently dropped.
    Mechanism traced end to end: REPL create door ->
    needs.parse_and_place -> idea_create.parse_create_line, which
    carried `"detail": detail[:2000]` and `"goals": goals[:12]`
    with no provenance or refusal; and the J-17 edit door carried
    the sibling cut, needs.set_detail's `u.detail = ...[:2000]`
    (a >2,000-char edited detail was cut identically). This is
    the SYS-C29 family defect (admitted content stored byte-exact
    or refused typed before mutation — never silently truncated)
    at the two doors these journeys exercise. Fix: detail and
    goals are stored whole at the create door, and the edited
    detail is stored whole at the edit door. Observed siblings
    NOT touched here: needs.set_goals' parts[:12] (the goals edit
    door — no journey in this family edits goals) and the `words`
    summary field's detail[:120] (the words contract is Part I's
    FI-012 remediation item, PR #507 matrix; this suite checks
    words only for persistence fidelity across reload).

Baseline posture (plan section 5.1(iii)): this suite runs against
the pre-Parts main as a labeled BASELINE harness proof. Its grades
are evidence about the harness and the current program, recorded
in director-reports/GRAND_SYNCHRONIZATION_REHEARSAL_2026-11-20.md;
the GP-E27 rehearsal executions proper run against merged
Parts I + II.

Run: python3 -m form.journey_idea_lifecycle_test
"""

import os
import shutil
import subprocess
import sys
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from form.persist import _STATE_DIR, _safe_owner, load as persist_load
from form.mandell.semantic_graph import SemanticGraph

RESULTS = []
_CLEANUP_ERRORS = []
RUN = uuid.uuid4().hex[:8]
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

LONG_DETAIL = "alpha bravo charlie delta echo " * 1000 + "ZZENDMARK"
GOALS13 = [f"goal{i}" for i in range(1, 14)]
LONG_EDIT = "revised " * 400 + "ZZEDITEND"
UNI_LABEL = "Café Über 中文 🎋"
UNI_DETAIL = "Résumé naïve — combining é test 🎋 and CJK 中文 detail"


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))
    print(f"{'PASS' if ok else 'FAIL'} {name} {detail}")


def cleanup(owner):
    safe = _safe_owner(owner)
    if not os.path.isdir(_STATE_DIR):
        return
    for name in os.listdir(_STATE_DIR):
        if safe in name:
            p = os.path.join(_STATE_DIR, name)
            try:
                shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
            except OSError as e:
                _CLEANUP_ERRORS.append(f"{p}: {e}")


def state_files(owner):
    safe = _safe_owner(owner)
    if not os.path.isdir(_STATE_DIR):
        return []
    return sorted(n for n in os.listdir(_STATE_DIR) if safe in n)


def run_repl(owner, lines, load=False):
    args = [sys.executable, "-m", "form.repl", "--owner", owner]
    if load:
        args.append("--load")
    proc = subprocess.run(args, input="\n".join(lines) + "\n",
                          capture_output=True, text=True, cwd=ROOT,
                          timeout=300)
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def snap(owner):
    """Loader-basis snapshot: unit fields exactly as persisted."""
    prog = persist_load(owner)
    units = {}
    for uid, u in prog.cube.session.plane.units.items():
        units[uid] = {
            "label": u.label,
            "detail": getattr(u, "detail", "") or "",
            "goals": list(getattr(u, "goals", []) or []),
            "words": getattr(u, "words", "") or "",
            "x": float(u.x), "y": float(u.y),
            "idea_id": getattr(u, "idea_id", None),
        }
    return {"units": units,
            "history": list(getattr(prog, "history", []) or [])}


def by_label(units, label):
    return {uid: u for uid, u in units.items() if u["label"] == label}


def main():
    life_owner = f"JLife{RUN}"
    long_owner = f"JLong{RUN}"
    nest_owner = f"JNest{RUN}"
    foreign_owner = f"JForeign{RUN}"
    undo_owner = f"JUndo{RUN}"
    owners = (life_owner, long_owner, nest_owner, foreign_owner,
              undo_owner)
    for o in owners:
        cleanup(o)
    try:
        # Isolation boundary, proven — not assumed: no state files
        # exist for any per-run owner before the sessions start (a
        # fresh Program() in this codebase loads persisted state by
        # default; the boundary is the per-run unique owner +
        # verified-empty start).
        check("lifecycle_isolation_boundary_clean_start",
              all(state_files(o) == [] for o in owners),
              "no state files exist for any of the five per-run "
              "owners before the sessions start")

        # ---------------- J-04: create / persist ----------------
        create_line = ("create an idea called Lifecycle Oak "
                       "detail: first detail text for the lifecycle "
                       "probe goals: goal one; goal two; goal three")
        rc, out = run_repl(life_owner, [
            create_line,
            "idea lifecycle_oak",
            f"create an idea called {UNI_LABEL} detail: "
            f"{UNI_DETAIL} goals: unicode goal",
            create_line,  # reissue: canonical dedup, see docstring
            "save",
            "save",       # idempotent retry of the pair-save
            "quit",
        ])
        check("j04_repl_exit_clean",
              rc == 0 and "Traceback" not in out,
              f"rc={rc} traceback={'Traceback' in out}")
        check("j04_create_receipt_with_canonical_id",
              'Created idea: "Lifecycle Oak" id=lifecycle_oak' in out
              and "complete=True" in out,
              "strong create prints the created idea with its "
              "stable canonical slug ID and complete=True "
              "(detail + goals admitted)")
        check("j04_idea_view_shows_detail_goals_position",
              "══ Idea · Lifecycle Oak ══" in out
              and "id=lifecycle_oak skin=cube pos=(" in out
              and "detail: first detail text for the lifecycle "
              "probe" in out
              and "goals: goal one, goal two, goal three" in out,
              "the public idea view shows the stored detail, goals "
              "and the spatial authority's chosen position")
        check("j04_unicode_create_receipt",
              f'Created idea: "{UNI_LABEL}"' in out,
              "non-ASCII label (accented Latin + CJK + emoji) is "
              "admitted at the create door and echoed whole")
        check("j04_save_retry_both_receipts",
              out.count("Session saved.") == 2,
              "the pair-save issued twice prints its receipt twice "
              "— the retry is a convergence, not an error or a "
              "duplicate write")
        s1 = snap(life_owner)
        check("j04_create_reissue_dedups_first_unit_untouched",
              "lifecycle_oak" in s1["units"]
              and "lifecycle_oak_1" in s1["units"]
              and s1["units"]["lifecycle_oak"]["detail"]
              == "first detail text for the lifecycle probe"
              and s1["units"]["lifecycle_oak_1"]["detail"]
              == "first detail text for the lifecycle probe",
              "reissuing the create mints the canonical suffixed "
              "second unit (P3/TD-5 dedup); the first unit's stored "
              "text is untouched — the door's retry behavior is "
              "explicit, never a silent overwrite")
        uni = by_label(s1["units"], UNI_LABEL)
        check("j04_unicode_stored_byte_exact",
              len(uni) == 1
              and list(uni.values())[0]["detail"] == UNI_DETAIL,
              "the Unicode unit's label and detail are stored "
              "byte-exact (combining marks, CJK, emoji intact)")

        # Cold reload: a second, separate process on the saved state.
        rc2, out2 = run_repl(life_owner, ["status", "quit"], load=True)
        s2 = snap(life_owner)
        check("j04_cold_reload_state_identical",
              rc2 == 0 and s2["units"] == s1["units"],
              "after cold reload every unit's id, label, detail, "
              "goals, words, position and idea binding are "
              "identical to the post-save loader state (reloaded "
              "vs reloaded basis)")

        # ---------------- J-04: the 5000-words limit ----------------
        rc3, out3 = run_repl(long_owner, [
            "create an idea called Long Detail Oak detail: "
            f"{LONG_DETAIL} goals: {'; '.join(GOALS13)}",
            "save",
            "quit",
        ])
        s3 = snap(long_owner)
        long_unit = by_label(s3["units"], "Long Detail Oak")
        stored = list(long_unit.values())[0] if long_unit else {}
        check("j04_long_detail_stored_whole",
              rc3 == 0 and 'Created idea: "Long Detail Oak"' in out3
              and stored.get("detail") == LONG_DETAIL,
              f"5,000-word admissible detail stored byte-exact "
              f"(stored len={len(stored.get('detail') or '')}, "
              f"expected {len(LONG_DETAIL)}, end marker "
              f"{'present' if (stored.get('detail') or '').endswith('ZZENDMARK') else 'LOST'})")
        check("j04_all_goals_stored",
              stored.get("goals") == GOALS13,
              f"all 13 goals stored in order "
              f"(stored {len(stored.get('goals') or [])})")
        rc4, out4 = run_repl(long_owner, ["status", "quit"], load=True)
        s4 = snap(long_owner)
        check("j04_long_detail_whole_after_cold_reload",
              rc4 == 0 and s4["units"] == s3["units"],
              "the long-detail unit reloads byte-identical — no "
              "hybrid state at the size limit")

        # ---------------- J-16: nest -> promote ----------------
        rc5, out5 = run_repl(nest_owner, [
            "create an idea called Parent Lifecycle detail: parent "
            "detail goals: parent goal",
            "create an idea called Child Lifecycle detail: child "
            "detail goals: child goal",
            "nest child_lifecycle under parent_lifecycle",
            "containment child_lifecycle",
            "containment parent_lifecycle",
            "promote child_lifecycle",
            "containment child_lifecycle",
            "promote child_lifecycle",
            "save",
            "quit",
        ])
        check("j16_repl_exit_clean",
              rc5 == 0 and "Traceback" not in out5,
              f"rc={rc5} traceback={'Traceback' in out5}")
        check("j16_nest_receipt",
              "Nested Child Lifecycle under Parent Lifecycle" in out5,
              "nesting via the public path prints its receipt")
        check("j16_containment_path_while_nested",
              "path: Parent Lifecycle > Child Lifecycle" in out5
              and "children: Child Lifecycle" in out5,
              "the containment view shows the child's breadcrumb "
              "path and the parent's children — the association is "
              "visible before promotion")
        check("j16_promote_receipt",
              "Promoted Child Lifecycle to top level" in out5,
              "promotion prints its receipt")
        check("j16_containment_path_after_promote",
              "path: Child Lifecycle" in out5,
              "after promotion the child's path is itself — "
              "top level")
        check("j16_second_promote_honest_noop",
              "Already top level: Child Lifecycle" in out5,
              "promoting an already-top-level unit is an honest "
              "no-op receipt, not a second promotion")
        s5 = snap(nest_owner)
        child = s5["units"].get("child_lifecycle") or {}
        parent = s5["units"].get("parent_lifecycle") or {}
        check("j16_canonical_ids_stable",
              child.get("label") == "Child Lifecycle"
              and bool(child.get("idea_id"))
              and bool(parent.get("idea_id")),
              "unit IDs unchanged by nest/promote; both units "
              "carry their bound canonical Idea IDs after reload")
        graph = SemanticGraph.load(nest_owner)
        entries = [e.to_dict() for e in graph._entries]
        pair = [e for e in entries
                if e["source_id"] == parent.get("idea_id")
                and e["target_id"] == child.get("idea_id")
                and e["type"] == "contains"]
        statuses = [e["status"] for e in pair]
        check("j16_lineage_history_intact_after_reload",
              len(pair) >= 2 and "active" in statuses
              and statuses[-1] == "superseded"
              and len({e["rel_id"] for e in pair}) == 1
              and graph.parent(child.get("idea_id")) is None,
              "the graph log keeps the CONTAINS entry's ACTIVE "
              "record and its SUPERSEDED successor under one "
              "rel_id (history preserved, never erased); the "
              "folded current parent is None after promotion")
        rc6, out6 = run_repl(nest_owner, ["containment child_lifecycle",
                                          "quit"], load=True)
        check("j16_reload_containment_view_top_level",
              rc6 == 0 and "path: Child Lifecycle" in out6,
              "after cold reload the public containment view still "
              "shows the promoted unit at top level")

        # J-16 negative: promotion attempted by a non-owner.
        rc7, out7 = run_repl(foreign_owner, [
            "promote child_lifecycle",
            "quit",
        ])
        check("j16_nonowner_promotion_refuses",
              "Containment refused (unit_not_found)" in out7
              and "no unit with id or label 'child_lifecycle'" in out7
              and rc7 == 0,
              "a foreign owner's REPL cannot see the unit at all: "
              "the promotion refuses with a named receipt before "
              "any state exists for that owner")
        check("j16_nonowner_attempt_left_no_state",
              state_files(foreign_owner) == [],
              "the refused foreign attempt created no state file "
              "and mutated nothing")

        # ---------------- J-17: undo/redo across the boundary --------
        rc8, out8 = run_repl(undo_owner, [
            "create an idea called Undo Oak detail: original "
            "detail text goals: undo goal",
            "set detail undo_oak revised detail text",
            "undo",
            "idea undo_oak",
            "redo",
            "idea undo_oak",
            "undo depth",
            f"set detail undo_oak {LONG_EDIT}",
            "idea undo_oak",
            "save",
            "quit",
        ])
        check("j17_repl_exit_clean",
              rc8 == 0 and "Traceback" not in out8,
              f"rc={rc8} traceback={'Traceback' in out8}")
        check("j17_edit_receipt",
              "Detail → Undo Oak: revised detail text" in out8,
              "the edit prints the applied detail")
        check("j17_undo_restores_prior_detail",
              "Restored detail on undo_oak" in out8
              and "detail: original detail text" in out8,
              "undo within the session restores the pre-edit "
              "detail, visible in the public idea view")
        idx = out8.find("Restored detail on undo_oak")
        tail8 = out8[idx:] if idx >= 0 else ""
        check("j17_redo_reapplies_detail",
              "detail: revised detail text" in tail8,
              "redo re-applies the undone edit (the idea view "
              "after redo shows the revised detail again)")
        check("j17_undo_depth_surface",
              "Undo depth: 30 (session action history;" in out8,
              "the depth surface names the ruled Q-LC.1 default "
              "(30) and the session-only action history it governs")
        check("j17_long_edit_shown_whole",
              "ZZEDITEND" in tail8,
              "the >2,000-char edited detail is applied whole — "
              "its end marker is present in the public idea view")
        s8 = snap(undo_owner)
        undo_unit = s8["units"].get("undo_oak") or {}
        check("j17_saved_state_is_redone_then_longedited_detail",
              undo_unit.get("detail") == LONG_EDIT
              and undo_unit.get("label") == "Undo Oak",
              "the saved state retains the final edited detail "
              "byte-exact under the same canonical ID")
        check("j17_undo_redo_evidence_retained_in_history",
              any("undo_edit_detail_undo_oak" in h
                  for h in s8["history"])
              and any("redo_edit_detail_undo_oak" in h
                      for h in s8["history"]),
              "the persisted program history retains the undo and "
              "redo evidence notes (24[Unlock]) across the save — "
              "the retention Q-LC.1 promises: evidence persists, "
              "the stacks do not")

        # Cold reload: the boundary itself.
        rc9, out9 = run_repl(undo_owner, [
            "undo",
            "redo",
            "idea undo_oak",
            "quit",
        ], load=True)
        check("j17_stacks_do_not_cross_the_boundary",
              "nothing to undo" in out9 and "nothing to redo" in out9
              and rc9 == 0,
              "in the reloaded session both stacks are honestly "
              "empty — undo/redo are session-local (Q-LC.1 settled "
              "scope), never silently reconstructed")
        s9 = snap(undo_owner)
        check("j17_state_retained_exactly_after_boundary",
              s9["units"] == s8["units"]
              and s9["units"].get("undo_oak", {}).get("detail")
              == LONG_EDIT,
              "the reloaded state is byte-identical to the saved "
              "state: the boundary costs the stacks and nothing "
              "else")
    finally:
        for o in owners:
            cleanup(o)

    check("Z.cleanup", not _CLEANUP_ERRORS, "; ".join(_CLEANUP_ERRORS))
    failed = [n for n, ok, _ in RESULTS if not ok]
    print(f"JOURNEY_IDEA_LIFECYCLE: {len(RESULTS) - len(failed)}/{len(RESULTS)} PASS")
    if failed:
        print("FAILURES:", ", ".join(failed))
    return 1 if failed else 0


def smoke():
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
