#!/usr/bin/env python3
"""Part VII / GP-E27 — journey harness family 4: J-05 Human confirm,
J-21 Visual Nursery at scale.

Written failing-first at code stage and registered in
form/regress.py LIST in the same commit (omitted-entry law).

Contracts — Edition 1 file 06 (06_JOURNEY_ACCEPTANCE.md) for J-05,
executed verbatim; plan section 5.2.1 designed oracle for J-21
(file 06 names J-21 in one line):

  J-05 Human confirm: "Create pending cross-Idea candidate, inspect
  reason and source, manually confirm; unit appears with inherited
  wall or explicitly selected mixed-parent wall."
  Failure oracle: "Rejected remains non-live; stale proposal
  ID/conflicting generation refuses; actor-supplied text is not
  authentication; auto-confirm stays sandbox-first only where
  already permitted."

  J-21 Visual Nursery at scale: "seed a large proposal set (1,000
  proposals), browse with shown/total on every view, confirm and
  reject through the visual path; counts reconcile exactly with
  the store after cold reload; the docked organizer, if present,
  proposes only PENDING suggestions (confirmation remains the
  human's)."

Execution tier: PUBLIC_ENTRY_PATH — every journey action runs in a
literal `python3 -m form.repl` subprocess against a per-run
isolated owner; state comparison after cold reload uses the
persistence loader (reloaded vs reloaded, never in-memory vs
reloaded). The one fixture exception is J-21's seeding itself: the
plan's own word for it is "seed" — 1,000 proposals are added
through the canonical Nursery.add door (the same door growth
uses), with the per-add saves batched into one canonical save at
the end; every stored record is add()'s own. All J-21 journey
actions (browse, search, get, confirm, reject) run at the public
path, and the fixture digest is printed by the suite.

Grounded behavior (each expectation verified first-hand in
scratch-owner probes, 2026-11-21, before this suite was written):
  - `grow ideas` over two word-sharing ideas yields a [new]
    cross-Idea candidate ("Harbor Lantern × Harbor Forge") whose
    proposals-view entry shows origin (growth:token) and reason
    (Solstice harm=...); `lineage <pid>` shows parents, affinity
    and status; `proposals get <pid>` shows the pending record.
  - `confirm <pid>` prints `Confirmed. "<label>" is live.`; the
    unit lands with the proposal's ID, both parents as lineage,
    origin "confirmed", detail/goals inherited from the first
    parent; the persisted program history gains
    `50[Manifest] :: <label>`.
  - Both parents boxed in one group BEFORE growth: the confirm
    inherits that wall — the unit is a member of the parents'
    box, durable across cold reload. Unboxed parents: unboxed.
  - A parent boxed AFTER the proposal was created makes the
    confirm mixed-wall: a bare `confirm <pid>` prints the choice
    prompt (parents in more than one sandbox, the two lawful
    choices) plus "Could not confirm:
    placement_choice_required", and the proposal stays pending;
    `confirm <pid> in <parent's box>` lands it in that box;
    `confirm <pid> outside` lands it unboxed; a choice naming a
    real box that is NOT a parent wall, or a nonexistent box,
    refuses "Could not confirm: invalid_placement_choice" and
    the proposal stays pending (a caller can never name an
    arbitrary box).
  - `reject <pid>` prints "Rejected."; the rejected proposal
    never becomes a unit and stays rejected after cold reload.
    Confirm-after-confirm, confirm-after-reject,
    reject-after-reject and unknown-ID confirm/reject all refuse
    "not found or not pending" — the stale-ID refusals. A confirm
    whose parents are absent from the loaded program refuses
    "missing_parent" (fail-closed; observed when a nursery
    outlives an unsaved program).
  - Actor-supplied text: `confirm <pid> as the program
    administrator` produces the identical receipt and the
    identical record as a bare confirm — the dispatch fixes the
    producer ("repl_user") and issues the review context itself;
    the typed text appears nowhere in the persisted history and
    authenticates nothing.
  - Auto-confirm (`auto confirm on`, the explicit opt-in): the
    sweep inside the next `grow ideas` confirms every eligible
    pending proposal into the designated staging box
    (auto_staging, reserved label "Auto staging — program-placed,
    awaiting release") — sandbox-first; a mixed-wall proposal is
    non-eligible and stays pending with no unit.
  - J-21 views at 1,000 proposals: `proposals` prints "Nursery
    has 1000 proposal(s):" and "(showing 20 of 1000)";
    `proposals browse` headers state shown/total_matches/
    total_searched/total_inventory on every page (default page
    50, max page 200); five size:200 cursor pages walk the whole
    set (shown sums to 1,000) and end with "next: (none — end of
    results)"; `proposals browse size:500` refuses typed
    (PAGE_SIZE_INVALID — "sizes are never silently clamped");
    search states its totals the same way (unique term 1 of 1;
    common term 50 of 1000 on the default page).

  FINDING RECORDED, NOT FIXED HERE (receipt freshness at the
  grow door): the Dell-13 route receipt for `grow ideas` prints
  the growth stage's nursery snapshot ("Nursery pending: 3")
  even when the auto-confirm sweep inside the same grow_ideas
  call has already confirmed every proposal. grow_ideas' own
  result carries the correct post-sweep count
  (result["nursery_pending"]), and the proposals view, status
  and the loader all reconcile in the same session — the stale
  figure is confined to that one receipt line, and no J-05/J-21
  oracle point reads it. Not a confirm-path defect and outside
  Part I's FI-011 A7/A8/A12 scope (raw Nursery.confirm without
  actor/receipt, origin-blind auto-confirm, indistinguishable
  replay receipts — none of which these journeys expose at the
  public path: the REPL confirm door is policy-mediated end to
  end). Recorded for the growth-receipt owner.

Baseline posture (plan section 5.1(iii)): this suite runs against
the pre-Parts main as a labeled BASELINE harness proof. Its
grades are evidence about the harness and the current program,
recorded in
director-reports/GRAND_SYNCHRONIZATION_REHEARSAL_2026-11-20.md;
the GP-E27 rehearsal executions proper run against merged
Parts I + II.

Run: python3 -m form.journey_confirm_test
"""

import hashlib
import os
import re
import shutil
import subprocess
import sys
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from form.persist import _STATE_DIR, _safe_owner, load as persist_load
from form.dell_matrix.confirm_lineage import STAGING_BOX_LABEL

RESULTS = []
_CLEANUP_ERRORS = []
RUN = uuid.uuid4().hex[:8]
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

CA = ("create an idea called Harbor Lantern detail: harbor lantern "
      "craft timber copper kettle song cellar vault goals: keep "
      "the harbor lit")
CB = ("create an idea called Harbor Forge detail: harbor lantern "
      "craft timber copper kettle song forge cellar vault goals: "
      "work the harbor forge")
CROSS_LABEL = "Harbor Lantern × Harbor Forge"

SCALE_N = 1000


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


def run_repl(owner, lines, load=False, timeout=300):
    args = [sys.executable, "-m", "form.repl", "--owner", owner]
    if load:
        args.append("--load")
    proc = subprocess.run(args, input="\n".join(lines) + "\n",
                          capture_output=True, text=True, cwd=ROOT,
                          timeout=timeout)
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def snap(owner):
    """Loader-basis snapshot: units, nursery, boxes, history."""
    prog = persist_load(owner)
    plane = prog.cube.session.plane
    units = {}
    for uid, u in plane.units.items():
        units[uid] = {
            "label": u.label,
            "sandboxed": bool(getattr(u, "sandboxed", False)),
            "sandbox_id": getattr(u, "sandbox_id", None),
            "parents": list(getattr(u, "parents", None) or []),
            "origin": getattr(u, "origin", None),
        }
    boxes = {sid: sorted(sb.member_ids)
             for sid, sb in plane.sandboxes.items()}
    props = {pid: p.status
             for pid, p in prog.nursery.proposals.items()}
    return {"units": units, "boxes": boxes, "props": props,
            "summary": prog.nursery.summary(),
            "history": list(getattr(prog, "history", []) or [])}


def grow_session(owner):
    """Create the two parents, grow, list, save. Returns (rc, out,
    cross_pid, evolved_pids) parsed from the proposals view."""
    rc, out = run_repl(owner, [CA, CB, "grow ideas", "proposals",
                               "save", "quit"])
    m = re.search(r"\[new\] (\S+)", out)
    cross = m.group(1) if m else None
    evolved = re.findall(r"\[evolved\] (\S+)", out)
    return rc, out, cross, evolved


def main():
    conf_owner = f"JConf{RUN}"
    wall_owner = f"JWall{RUN}"
    mixed_owner = f"JMixed{RUN}"
    outside_owner = f"JOutside{RUN}"
    actor_owner = f"JActor{RUN}"
    auto_owner = f"JAuto{RUN}"
    automix_owner = f"JAutoMix{RUN}"
    scale_owner = f"JScale{RUN}"
    owners = (conf_owner, wall_owner, mixed_owner, outside_owner,
              actor_owner, auto_owner, automix_owner, scale_owner)
    for o in owners:
        cleanup(o)
    try:
        # Isolation boundary, proven — not assumed (a fresh
        # Program() in this codebase loads persisted state by
        # default; the boundary is the per-run unique owner +
        # verified-empty start).
        check("confirm_isolation_boundary_clean_start",
              all(state_files(o) == [] for o in owners),
              "no state files exist for any of the eight per-run "
              "owners before the sessions start")

        # ---------------- J-05: inspect -> confirm -> stale -------
        rc, out, cross, evolved = grow_session(conf_owner)
        check("j05_repl_exit_clean",
              rc == 0 and "Traceback" not in out,
              f"rc={rc} traceback={'Traceback' in out}")
        check("j05_grow_produces_cross_candidate",
              cross is not None and CROSS_LABEL in out,
              f"cross-Idea candidate pid={cross}")
        check("j05_proposals_view_shows_reason_and_source",
              "origin: growth:token" in out
              and "reason: Solstice" in out,
              "the review face shows the candidate's source "
              "(origin) and its reason (Solstice scores) before "
              "any decision")
        ev1 = evolved[0] if evolved else "missing_evolved"
        rc, out = run_repl(conf_owner, [
            f"lineage {cross}",
            f"proposals get {cross}",
            f"confirm {cross}",
            f"idea {cross}",
            f"confirm {cross}",
            f"reject {ev1}",
            f"confirm {ev1}",
            f"reject {ev1}",
            "confirm ghost_pid_999",
            "reject ghost_pid_999",
            "proposals",
            "save",
            "quit",
        ], load=True)
        check("j05_lineage_inspect_shows_parents_and_status",
              "parents: ['harbor_lantern', 'harbor_forge']" in out
              and "status: pending" in out,
              "lineage names both parents and the pending status "
              "at inspection time")
        check("j05_get_shows_pending_record",
              "proposals get — found 1 of 1 requested" in out
              and f"[pending] {cross} — {CROSS_LABEL}" in out,
              "the get door returns the candidate's pending record")
        check("j05_confirm_receipt",
              f'Confirmed. "{CROSS_LABEL}" is live.' in out,
              "manual confirm prints its receipt")
        check("j05_confirmed_unit_visible",
              f"══ Idea · {CROSS_LABEL} ══" in out
              and f"id={cross} skin=seed" in out,
              "the confirmed unit is visible at the public idea "
              "view under the proposal's own ID")
        check("j05_double_confirm_refuses",
              "Could not confirm: not found or not pending" in out,
              "re-confirming a confirmed proposal refuses as stale")
        check("j05_reject_receipt_and_stale_battery",
              out.count("Rejected.") >= 1
              and out.count("Could not confirm: not found or "
                            "not pending") >= 3
              and "Could not reject: not found or not pending" in out,
              "reject prints its receipt; confirm-after-reject, "
              "reject-after-reject and unknown-ID confirm/reject "
              "all refuse 'not found or not pending'")
        s = snap(conf_owner)
        cu = s["units"].get(cross) or {}
        check("j05_loader_unit_placed_with_lineage",
              cu.get("label") == CROSS_LABEL
              and cu.get("parents") == ["harbor_lantern",
                                         "harbor_forge"]
              and cu.get("origin") == "confirmed"
              and cu.get("sandboxed") is False
              and s["props"].get(cross) == "confirmed",
              "loader basis: the unit is placed with both parents "
              "as lineage, origin 'confirmed', unboxed (unboxed "
              "parents), and the proposal record reads confirmed")
        check("j05_rejected_remains_nonlive",
              s["props"].get(ev1) == "rejected"
              and ev1 not in s["units"],
              "the rejected proposal is recorded rejected and "
              "never became a live unit")
        check("j05_confirm_recorded_in_history",
              f"50[Manifest] :: {CROSS_LABEL}" in s["history"],
              "the persisted program history carries the Manifest "
              "note for the confirmation")
        rc, out = run_repl(conf_owner, [
            f"confirm {cross}",
            "status",
            "quit",
        ], load=True)
        s2 = snap(conf_owner)
        check("j05_reload_stale_confirm_refuses",
              "Could not confirm: not found or not pending" in out
              and rc == 0,
              "after cold reload the same stale confirm refuses "
              "identically — the confirmed state is durable, not "
              "session luck")
        check("j05_reload_state_reconciles",
              s2["units"] == s["units"] and s2["props"] == s["props"],
              "units and proposal statuses are identical before "
              "and after the cold-reload session")

        # ---------------- J-05: same-wall inheritance -------------
        rc, out = run_repl(wall_owner, [
            CA, CB,
            "group create Vault One",
            "group add harbor_lantern to Vault One",
            "group add harbor_forge to Vault One",
            "grow ideas",
            "proposals",
            "save",
            "quit",
        ])
        m = re.search(r"\[new\] (\S+)", out)
        wcross = m.group(1) if m else None
        check("j05_wall_group_receipts",
              rc == 0 and "Group created: Vault One "
              "[project_vault_one]" in out
              and "Added Harbor Lantern (harbor_lantern) to group "
              "'Vault One'" in out
              and "Added Harbor Forge (harbor_forge) to group "
              "'Vault One'" in out and wcross is not None,
              "both parents boxed into one group at the public "
              "path; the cross candidate is born inside the wall")
        rc, out = run_repl(wall_owner, [
            f"confirm {wcross}",
            "save",
            "quit",
        ], load=True)
        s = snap(wall_owner)
        wu = s["units"].get(wcross) or {}
        check("j05_same_wall_confirm_inherits_wall",
              f'Confirmed. "{CROSS_LABEL}" is live.' in out
              and wu.get("sandboxed") is True
              and wu.get("sandbox_id") == "project_vault_one"
              and wcross in s["boxes"].get("project_vault_one", [])
              and s["props"].get(wcross) == "confirmed",
              "the confirmed unit inherits the parents' wall: "
              "sandboxed into project_vault_one AND a member of "
              "the box record (the canonical pair, both sides)")
        rc, out = run_repl(wall_owner, ["status", "quit"], load=True)
        s2 = snap(wall_owner)
        check("j05_same_wall_survives_reload",
              rc == 0 and s2["units"] == s["units"]
              and s2["boxes"] == s["boxes"],
              "the inherited wall and box membership reload "
              "byte-identical")

        # ---------------- J-05: mixed wall — choice ---------------
        rc, out, mcross, _ = grow_session(mixed_owner)
        rc, out = run_repl(mixed_owner, [
            "group create Vault Two",
            "group create Other Box",
            "group add harbor_lantern to Vault Two",
            f"confirm {mcross}",
            "proposals",
            f"confirm {mcross} in project_other_box",
            f"confirm {mcross} in no_such_box",
            f"confirm {mcross} in project_vault_two",
            "save",
            "quit",
        ], load=True)
        check("j05_mixed_confirm_requires_choice",
              f'"{mcross}" has parents in more than one sandbox '
              f"(project_vault_two + outside). Where should it "
              f"land?" in out
              and "Could not confirm: placement_choice_required"
              in out,
              "a bare confirm of a mixed-wall candidate asks, "
              "naming the actual parent walls and both lawful "
              "choices — it never places silently")
        idx = out.find("placement_choice_required")
        tail = out[idx:] if idx >= 0 else ""
        check("j05_mixed_stays_pending_without_choice",
              "Nursery has 3 proposal(s):" in tail
              and f"[new] {mcross}" in tail,
              "the proposals view after the refused confirm still "
              "lists the candidate as pending")
        check("j05_invalid_placement_choices_refuse",
              out.count("Could not confirm: "
                        "invalid_placement_choice") == 2,
              "choices naming a real non-parent box and a "
              "nonexistent box both refuse — a caller can never "
              "name an arbitrary box")
        s = snap(mixed_owner)
        mu = s["units"].get(mcross) or {}
        check("j05_mixed_choice_in_box_places",
              f'Confirmed. "{CROSS_LABEL}" is live.' in out
              and mu.get("sandboxed") is True
              and mu.get("sandbox_id") == "project_vault_two"
              and mcross in s["boxes"].get("project_vault_two", []),
              "the explicit choice lands the unit in the chosen "
              "parent wall, as a member of that box")

        # ---------------- J-05: mixed wall — outside --------------
        rc, out, ocross, _ = grow_session(outside_owner)
        rc, out = run_repl(outside_owner, [
            "group create Vault Three",
            "group add harbor_forge to Vault Three",
            f"confirm {ocross} outside",
            "save",
            "quit",
        ], load=True)
        s = snap(outside_owner)
        ou = s["units"].get(ocross) or {}
        check("j05_mixed_choice_outside_places_unboxed",
              f'Confirmed. "{CROSS_LABEL}" is live.' in out
              and ou.get("sandboxed") is False
              and ou.get("sandbox_id") is None
              and s["props"].get(ocross) == "confirmed",
              "the explicit 'outside' choice lands the unit on "
              "the open field — the other lawful mixed-parent "
              "outcome")

        # ---------------- J-05: actor text -------------------------
        rc, out, across, _ = grow_session(actor_owner)
        rc, out = run_repl(actor_owner, [
            f"confirm {across} as the program administrator",
            "save",
            "quit",
        ], load=True)
        s = snap(actor_owner)
        check("j05_actor_text_is_not_authentication",
              f'Confirmed. "{CROSS_LABEL}" is live.' in out
              and s["props"].get(across) == "confirmed"
              and f"50[Manifest] :: {CROSS_LABEL}" in s["history"]
              and not any("administrator" in h for h in s["history"]),
              "confirming 'as the program administrator' yields "
              "the identical receipt and record as a bare confirm: "
              "the session's own authority acted; the supplied "
              "actor text appears nowhere in the persisted record "
              "and authenticated nothing")

        # ---------------- J-05: auto-confirm sweep ----------------
        rc, out = run_repl(auto_owner, [
            "auto confirm on",
            CA, CB,
            "grow ideas",
            "proposals",
            "save",
            "quit",
        ])
        s = snap(auto_owner)
        staged = [pid for pid, st in s["props"].items()
                  if st == "confirmed"]
        check("j05_auto_sweep_confirms_into_staging",
              "Grow mode → auto confirm all ON" in out
              and "Nursery is empty." in out
              and len(staged) == 3
              and all(s["units"].get(pid, {}).get("sandbox_id")
                      == "auto_staging" for pid in staged)
              and all(pid in s["boxes"].get("auto_staging", [])
                      for pid in staged),
              "under the explicit opt-in the sweep confirms every "
              "eligible proposal — and every one lands in the "
              "designated staging box, never on the open field "
              "(sandbox-first)")
        _prog = persist_load(auto_owner)
        _sb = _prog.cube.session.plane.sandboxes.get("auto_staging")
        check("j05_staging_box_carries_reserved_label",
              _sb is not None and _sb.label == STAGING_BOX_LABEL,
              "the staging box is the program's own: it carries "
              "the reserved staging label")

        rc, out, xcross, _ = grow_session(automix_owner)
        rc, out = run_repl(automix_owner, [
            "group create Vault Nine",
            "group add harbor_lantern to Vault Nine",
            "auto confirm on",
            "grow ideas",
            "proposals",
            "save",
            "quit",
        ], load=True)
        s = snap(automix_owner)
        others = [pid for pid, st in s["props"].items()
                  if pid != xcross]
        check("j05_auto_sweep_mixed_wall_noneligible",
              s["props"].get(xcross) == "pending"
              and xcross not in s["units"]
              and all(s["props"].get(pid) == "confirmed"
                      for pid in others),
              "the sweep confirms the eligible proposals and "
              "leaves the mixed-wall candidate pending with no "
              "unit — auto-confirm never makes the placement "
              "choice for the human")

        # ---------------- J-21: Nursery at scale ------------------
        seeded_ids = seed_scale_fixture(scale_owner)
        s = snap(scale_owner)
        check("j21_fixture_seeded_1000",
              len(seeded_ids) == SCALE_N
              and s["summary"].get("total") == SCALE_N
              and s["summary"].get("pending") == SCALE_N,
              f"fixture: {SCALE_N} pending proposals in the "
              f"owner's canonical store (digest "
              f"{fixture_digest(seeded_ids)})")
        rc, out = run_repl(scale_owner, [
            "proposals",
            "proposals browse size:200",
            "quit",
        ], load=True, timeout=600)
        check("j21_proposals_view_shown_total",
              f"Nursery has {SCALE_N} proposal(s):" in out
              and f"(showing 20 of {SCALE_N})" in out,
              "the plain proposals face states shown/total at "
              "scale")
        hdr = re.search(r"shown (\d+) of (\d+) matches — "
                        r"total_matches (\d+) · total_searched "
                        r"(\d+) · total_inventory (\d+)", out)
        check("j21_browse_first_page_totals",
              hdr is not None and hdr.groups() == ("200", "1000",
                                                   "1000", "1000",
                                                   "1000"),
              f"first browse page header: {hdr.groups() if hdr else None}")
        # Cursor walk: five size:200 pages must cover the set.
        shown_sum = 200
        pages_ok = True
        m = re.search(r"next: proposals browse cursor:(\S+)", out)
        cursor = m.group(1) if m else None
        for _page in range(4):
            if cursor is None:
                pages_ok = False
                break
            rc, out = run_repl(scale_owner, [
                f"proposals browse size:200 cursor:{cursor}",
                "quit",
            ], load=True, timeout=600)
            hdr = re.search(r"shown (\d+) of (\d+) matches", out)
            items = re.findall(r"(?m)^\s+\d+\. \[pending\] ", out)
            if hdr is None or int(hdr.group(1)) != len(items):
                pages_ok = False
                break
            shown_sum += int(hdr.group(1))
            m = re.search(r"next: proposals browse cursor:(\S+)",
                          out)
            cursor = m.group(1) if m else None
        check("j21_browse_cursor_walk_reconciles",
              pages_ok and shown_sum == SCALE_N and cursor is None
              and "next: (none — end of results)" in out,
              f"five 200-pages walk the whole set: shown sums to "
              f"{shown_sum} and the walk ends at end-of-results")
        rc, out = run_repl(scale_owner, [
            "proposals search token1000",
            "proposals search commonmass",
            "proposals browse size:500",
            "quit",
        ], load=True, timeout=600)
        check("j21_search_unique_and_common_totals",
              "shown 1 of 1 matches — total_matches 1 · "
              "total_searched 1000" in out
              and f"[pending] {seeded_ids[999]}" in out
              and "shown 50 of 1000 matches — total_matches 1000"
              in out,
              "search states its totals truthfully: the unique "
              "term finds exactly its one proposal; the common "
              "term reports all 1,000 matches on a 50-shown page")
        check("j21_browse_oversize_page_refused_typed",
              "proposals browse refused: PAGE_SIZE_INVALID — "
              "page size must be an integer 1..200 (got 500); "
              "sizes are never silently clamped" in out,
              "an over-max page size refuses typed instead of "
              "silently clamping to the cap")
        keep = [seeded_ids[0], seeded_ids[499], seeded_ids[999]]
        drop = [seeded_ids[1], seeded_ids[998]]
        lines = ([f"confirm {pid}" for pid in keep]
                 + [f"reject {pid}" for pid in drop]
                 + ["save", "quit"])
        rc, out = run_repl(scale_owner, lines, load=True,
                           timeout=600)
        check("j21_confirm_reject_at_scale_receipts",
              out.count('Confirmed. "Scale Fixture') == 3
              and out.count("is live.") == 3
              and out.count("Rejected.") == 2,
              "three confirms and two rejects execute through "
              "the public path at scale, each with its receipt")
        s = snap(scale_owner)
        check("j21_store_counts_reconcile",
              s["summary"].get("total") == SCALE_N
              and s["summary"].get("pending") == SCALE_N - 5
              and s["summary"].get("confirmed") == 3
              and s["summary"].get("rejected") == 2,
              f"store summary after the decisions: "
              f"{s['summary']}")
        check("j21_confirmed_live_rejected_nonlive_at_scale",
              all(pid in s["units"] for pid in keep)
              and all(pid not in s["units"] for pid in drop),
              "the three confirmed proposals are live units; "
              "the two rejected are not")
        rc, out = run_repl(scale_owner, [
            "proposals browse status:pending",
            "proposals browse status:confirmed",
            "quit",
        ], load=True, timeout=600)
        s2 = snap(scale_owner)
        check("j21_reload_counts_reconcile",
              "shown 50 of 995 matches — total_matches 995" in out
              and "shown 3 of 3 matches — total_matches 3" in out
              and s2["summary"] == s["summary"]
              and s2["props"] == s["props"],
              "after cold reload the views and the store agree "
              "exactly: 995 pending, 3 confirmed, 1,000 total")
    finally:
        for o in owners:
            cleanup(o)

    check("Z.cleanup", not _CLEANUP_ERRORS, "; ".join(_CLEANUP_ERRORS))
    failed = [n for n, ok, _ in RESULTS if not ok]
    print(f"JOURNEY_CONFIRM: {len(RESULTS) - len(failed)}/{len(RESULTS)} PASS")
    if failed:
        print("FAILURES:", ", ".join(failed))
    return 1 if failed else 0


def seed_scale_fixture(owner):
    """Seed SCALE_N pending proposals through the canonical
    Nursery.add door (the door growth itself uses), batching the
    per-add saves into one canonical save at the end; every stored
    record is add()'s own. Returns the proposal IDs in creation
    order."""
    from form.open import open_program
    from form.dell_matrix.nursery import Nursery
    prog = open_program(owner)
    real_save = Nursery.save
    Nursery.save = lambda self: None
    ids = []
    try:
        for i in range(1, SCALE_N + 1):
            prop = prog.nursery.add(
                label=f"Scale Fixture {i:04d}",
                words=f"scale fixture token{i:04d} commonmass",
                kind="new", parents=[], origin="suite:seeded",
                reason="J-21 scale fixture")
            ids.append(prop.id)
    finally:
        Nursery.save = real_save
    prog.nursery.save()
    prog.save()
    return ids


def fixture_digest(ids):
    h = hashlib.sha256()
    for i, pid in enumerate(ids, 1):
        h.update(f"{pid}|Scale Fixture {i:04d}|scale fixture "
                 f"token{i:04d} commonmass\n".encode())
    return h.hexdigest()[:16]


def smoke():
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
