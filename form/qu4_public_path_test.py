#!/usr/bin/env python3
"""Q-U.4 PUBLIC-PATH COMPOSITION — Part I (PART_I_PLAN_2026-11-20
§5.2; Ace ruling Q-U.4, sandbox-first for mixed ideas).

The writer-level machinery (_resolve_confirm_placement) is proven
by form/confirm_placement_test.py (25 checks). What was NOT
proven: the whole composition on the PUBLIC path — a real
growth-produced proposal whose parentage is mixed, carried
through the confirm doors a user actually walks.

THE HONEST SHAPE OF THE MIX (measured, not assumed):
- Default growth NEVER mixes: wall-respecting enumeration
  excludes cross-wall pairs (GS-4's contract), and even an
  EXPLICIT mixed scope (scope_ids spanning a boxed and an
  unboxed unit) produces no mixed proposal — the pair is
  excluded and the exclusion is receipted. This suite pins
  that negative (check 2) instead of pretending growth mixes.
- A mixed proposal arises the way it does in real use: growth
  in the open produces a two-parent proposal; LATER, one parent
  is boxed. The proposal's parentage now spans the wall, and
  confirm must ask where the offspring lands (Ace's ruling:
  sandbox-first; never auto-place a mixed idea).

THE COMPOSITION (in-process legs = INTEGRATION through the
Program's public doors; the REPL leg = REAL_USER_PATH +
CROSS_PROCESS, the literal `python3 -m form.repl` path):
  growth-produced two-parent proposal
  -> box one parent (the mix appears)
  -> confirm with NO choice: placement_choice_required,
     ZERO mutation, proposal stays pending
  -> confirm with an INVENTED box: invalid_placement_choice,
     ZERO mutation
  -> confirm with the real box: the WHOLE unit lands in the
     sandbox (never split), proposal confirmed, parentage
     record intact
  -> the landing persists across a fresh load
  -> plane.unbox releases the WHOLE unit back to the Matrix,
     identity and parentage preserved, release persists
  -> the same journey through the literal REPL: piped
     `confirm <id>` prints the placement question and leaves
     the proposal pending; `confirm <id> in vault1` confirms.

State isolation: dedicated owners only; owner-scoped cleanup
that fails loudly. Zero-mutation legs compare a structural
snapshot (units, walls, proposal statuses, sandbox members).
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}"
          + (f" | {detail}" if detail and not cond else ""))


def _cleanup(owner):
    from form.persist import _STATE_DIR, _safe_owner
    safe = _safe_owner(owner)
    files = [os.path.join(_STATE_DIR, f"program_{safe}.json"),
             os.path.join(_STATE_DIR, f"graph_{safe}.json"),
             os.path.join(_STATE_DIR, f"graph_{safe}.journal.json"),
             os.path.join(_STATE_DIR, ".locks", f"{safe}.lock")]
    ideas_dir = os.path.join(_STATE_DIR, f"ideas_{safe}")
    for f in files:
        if os.path.isfile(f):
            os.remove(f)
    if os.path.isdir(ideas_dir):
        shutil.rmtree(ideas_dir)
    if os.path.isdir(_STATE_DIR):
        for name in os.listdir(_STATE_DIR):
            if name.startswith(f"program_{safe}_cp_"):
                os.remove(os.path.join(_STATE_DIR, name))
    leftovers = [f for f in files if os.path.isfile(f)]
    if leftovers or os.path.isdir(ideas_dir):
        raise RuntimeError(f"qu4 cleanup incomplete: {leftovers}")


FIELD = [
    ("in_a", "harbor lantern inkeep",
     "harbor lantern craft timber copper kettle song inkeep cellar vault"),
    ("in_b", "harbor lantern inforge",
     "harbor lantern craft timber copper kettle song inforge cellar vault"),
    ("out_a", "harbor lantern outkeep",
     "harbor lantern craft timber copper kettle song outkeep cellar vault "
     "axolotl azurite"),
    ("out_b", "harbor copper outdrift",
     "harbor lantern craft copper song outdrift axolotl azurite basalt"),
    ("out_c", "glacier tundra outpost",
     "glacier tundra obsidian wolf outpost fjord"),
]
INSIDE = ["in_a", "in_b"]


def _build(owner, box_inside):
    from form.open import open_program
    _cleanup(owner)
    p = open_program(owner)
    plane = p.cube.session.plane
    plane.units.clear()
    plane.sandboxes.clear()
    p.nursery.proposals.clear()
    for uid, label, words in FIELD:
        p.place(uid, label, words=words, x=0.0, y=0.0)
    if box_inside:
        plane.box(list(INSIDE), "vault1", label="qu4 vault")
    return p


def _snapshot(p):
    plane = p.cube.session.plane
    return {
        "units": sorted(plane.units),
        "walls": {uid: (bool(u.sandboxed), u.sandbox_id)
                  for uid, u in sorted(plane.units.items())},
        "proposals": {pid: prop.status
                      for pid, prop in sorted(
                          p.nursery.proposals.items())},
        "members": {sid: sorted(sb.member_ids)
                    for sid, sb in sorted(plane.sandboxes.items())},
    }


def _manual_confirm(p, pid, **kw):
    return p.confirm_proposal(
        pid, _producer="repl_user",
        _review_context=p.make_review_context(pid, "repl_user"), **kw)


def _mixed_scope_negative():
    owner = "QU4SCOPE"
    p = _build(owner, box_inside=True)
    try:
        res = p.grow_ideas(1, scope_ids=["in_a", "out_a"])
        mixed = [pid for pid, prop in p.nursery.proposals.items()
                 if len(set(prop.parents or [])) > 1]
        check("qu4_mixed_scope_growth_never_mixes",
              not mixed
              and (res.get("pairs_excluded_cross_sandbox") or 0) >= 1,
              f"mixed={mixed} receipt={res.get('pairs_excluded_cross_sandbox')}")
    finally:
        _cleanup(owner)


def _composition():
    owner = "QU4PATH"
    p = _build(owner, box_inside=False)
    try:
        res = p.grow_ideas(1)
        cands = sorted(
            pid for pid, prop in p.nursery.proposals.items()
            if "in_a" in (prop.parents or [])
            and len(prop.parents or []) >= 2)
        check("qu4_growth_produces_two_parent_proposals",
              bool(cands),
              f"candidates={cands} grow_ok={res.get('ok')}")
        if not cands:
            return
        pid = cands[0]
        parents = list(p.nursery.proposals[pid].parents)
        plane = p.cube.session.plane
        plane.box(["in_a"], "vault1", label="qu4 vault")
        walls = {u: bool(plane.units[u].sandboxed) for u in parents}
        check("qu4_boxing_a_parent_makes_the_proposal_mixed",
              len(set(walls.values())) == 2,
              f"parents={parents} walls={walls}")

        before = _snapshot(p)
        out = _manual_confirm(p, pid)
        opts = {o.get("sandbox_id") for o in (out.get("options") or [])
                if isinstance(o, dict)}
        check("qu4_no_choice_refused_with_real_options",
              out.get("ok") is False
              and out.get("reason") == "placement_choice_required"
              and "vault1" in opts,
              f"out={ {k: out.get(k) for k in ('ok', 'reason')} } "
              f"options={opts}")
        check("qu4_no_choice_refusal_is_zero_mutation",
              _snapshot(p) == before
              and p.nursery.proposals[pid].status == "pending",
              "state moved on a refused confirm")

        out = _manual_confirm(p, pid, _placement="not-a-real-box")
        check("qu4_invented_box_refused_zero_mutation",
              out.get("ok") is False
              and out.get("reason") == "invalid_placement_choice"
              and _snapshot(p) == before
              and p.nursery.proposals[pid].status == "pending",
              f"out={ {k: out.get(k) for k in ('ok', 'reason')} }")

        out = _manual_confirm(p, pid, _placement="vault1")
        unit = plane.units.get(pid)
        check("qu4_choice_lands_whole_unit_in_the_sandbox",
              out.get("ok") is True and unit is not None
              and bool(unit.sandboxed)
              and unit.sandbox_id == "vault1"
              and pid in (plane.sandboxes["vault1"].member_ids)
              and p.nursery.proposals[pid].status == "confirmed"
              and list(p.nursery.proposals[pid].parents) == parents,
              f"out={ {k: out.get(k) for k in ('ok', 'reason')} } "
              f"unit={unit}")
        return owner, pid, parents
    except Exception:
        _cleanup(owner)
        raise


def _persistence_and_release(owner, pid, parents):
    from form.open import Program
    try:
        p2 = Program.load(owner)
        unit = p2.cube.session.plane.units.get(pid)
        check("qu4_landing_persists_across_load",
              unit is not None and bool(unit.sandboxed)
              and unit.sandbox_id == "vault1"
              and pid in (p2.cube.session.plane
                          .sandboxes["vault1"].member_ids)
              and p2.nursery.proposals[pid].status == "confirmed",
              f"unit={unit}")
        plane = p2.cube.session.plane
        plane.unbox(pid)
        unit = plane.units.get(pid)
        check("qu4_unbox_releases_the_whole_unit",
              unit is not None and not bool(unit.sandboxed)
              and unit.sandbox_id is None
              and pid not in (plane.sandboxes["vault1"].member_ids)
              and list(p2.nursery.proposals[pid].parents) == parents,
              f"unit={unit}")
        from form import persist_rest
        persist_rest.save(p2)
        p3 = Program.load(owner)
        unit = p3.cube.session.plane.units.get(pid)
        check("qu4_release_persists_across_load",
              unit is not None and not bool(unit.sandboxed)
              and unit.sandbox_id is None,
              f"unit={unit}")
    finally:
        _cleanup(owner)


def _repl_leg():
    owner = "QU4REPL"
    p = _build(owner, box_inside=False)
    try:
        p.grow_ideas(1)
        cands = sorted(
            pid for pid, prop in p.nursery.proposals.items()
            if "in_a" in (prop.parents or [])
            and len(prop.parents or []) >= 2)
        pid = cands[0]
        p.cube.session.plane.box(["in_a"], "vault1", label="qu4 vault")
        from form import persist_rest
        persist_rest.save(p)
        script = f"confirm {pid}\nconfirm {pid} in vault1\n"
        proc = subprocess.run(
            [sys.executable, "-m", "form.repl", "--owner", owner,
             "--load"],
            input=script, capture_output=True, text=True,
            cwd=ROOT, timeout=180)
        out = proc.stdout + proc.stderr
        check("qu4_repl_asks_the_placement_question_first",
              "has parents in more than one sandbox" in out
              and "vault1" in out,
              f"rc={proc.returncode} out_tail={out[-400:]}")
        check("qu4_repl_confirm_with_choice_lands_it",
              "Confirmed." in out and "is live." in out,
              f"out_tail={out[-400:]}")
        from form.open import Program
        p2 = Program.load(owner)
        unit = p2.cube.session.plane.units.get(pid)
        check("qu4_repl_landing_is_real_persisted_state",
              unit is not None and bool(unit.sandboxed)
              and unit.sandbox_id == "vault1"
              and p2.nursery.proposals[pid].status == "confirmed",
              f"unit={unit}")
    finally:
        _cleanup(owner)


def run_all():
    _mixed_scope_negative()
    got = _composition()
    if got:
        owner, pid, parents = got
        _persistence_and_release(owner, pid, parents)
    _repl_leg()
    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"QU4 PUBLIC PATH: {passed}/{len(RESULTS)} GREEN")
    return passed == len(RESULTS)


def smoke() -> bool:
    return run_all()


if __name__ == "__main__":
    raise SystemExit(0 if smoke() else 1)
