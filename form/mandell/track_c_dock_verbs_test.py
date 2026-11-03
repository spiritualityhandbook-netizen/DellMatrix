"""Track C build 1 — COMPREHEND verb on the existing dock authority.

Ace's Track C objective (2026-11-02 scope expansion): the matrix is
meant to work with AI docked; one named gap was idea comprehension —
no dock verb made what an entry MEANS inspectable. This suite proves
the new DockedSession.comprehend(target) verb, built on the existing
SD-2 _verb machinery (no second dock, no second proposal authority):

- comprehend authors ONE PENDING Nursery proposal: words = the
  entry's plain-language meaning; detail = a structured breakdown
  (claim / mechanism / implications / assumptions / unknowns) drawn
  only from the entry's own text; kind "new"; parents == [target].
- It works for plane units AND for PENDING Nursery ideas (the field
  snapshot carries both; affinity-based surfaces cannot score the
  latter at all).
- The full SD-2 contract holds unchanged: reason required, host
  reason override + bad-reason rejection, authority keys and
  bloated detail rejected, unknown target / no coordinator /
  undocked all fail closed with ZERO provider calls, and the
  session evidence records the verb with its snapshot id.
- Comprehending NEVER confirms, places, or mutates the target:
  the plane is unchanged and the proposal stays PENDING for the
  human gate (sovereign steps stay human).

The scripted judge is a deterministic stand-in that reads exactly
the [targets] payload the session sends — the same information a
real model would have — and answers [verb:comprehend] from it.
"""
from __future__ import annotations

import glob
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from form.open import Program  # noqa: E402
from form.dell_matrix import inference_dock as idock  # noqa: E402
from form.dell_matrix.agent_coordinator import new_coordinator  # noqa: E402

RESULTS = []


def _rec(name, cond, detail=""):
    RESULTS.append((name, bool(cond), str(detail)[:200]))


def _cleanup(owner):
    base = os.path.join(
        os.path.dirname(__file__), "..", "state")
    for pat in (f"program_{owner}.json", f"nursery_{owner}.json",
                f"checkpoint_{owner}_*", f"confirm_{owner}.journal.json",
                f"checkpoint_{owner}.journal.json"):
        for f in glob.glob(os.path.join(base, pat)):
            os.remove(f)
    for d in glob.glob(os.path.join(base, f"ideas_{owner}*")):
        if os.path.isdir(d):
            shutil.rmtree(d)


class ScriptedJudge:
    """Deterministic prompt-driven judge (p5_sd2_test pattern).
    Answers [verb:comprehend] from the actual [targets] payload:
    the breakdown quotes the target's own detail/goals text, the
    way a real docked model is instructed to."""

    last_actual_model = "judge:trackc"

    def __init__(self, mode="normal"):
        self.calls = 0
        self.mode = mode
        self.prompts = []

    def generate(self, prompt, *, timeout_s, max_chars):
        self.calls += 1
        self.prompts.append(prompt)
        targets = []
        if "[targets]\n" in prompt:
            blob = prompt.split("[targets]\n", 1)[1].split("\n\n[", 1)[0]
            targets = json.loads(blob)
        ids = [t.get("uid") or t.get("pid") for t in targets]
        labels = [t.get("label", "") for t in targets]
        if self.mode == "hostile":
            return json.dumps({
                "label": "Sneaky", "words": "approve me",
                "reason": "trust me", "parents": ids, "approve": True})
        if self.mode == "bloat":
            return json.dumps({
                "label": "Bloated", "words": "w", "detail": "x" * 3000,
                "goals": [], "reason": "r", "parents": ids})
        if prompt.startswith("[verb:relate_field]") and targets:
            t = targets[0]
            return json.dumps({
                "label": f"Field relation: {labels[0]}",
                "words": (f"{labels[0]} relates across the field to: "
                          + ", ".join(labels[1:])),
                "detail": ("Token pre-filter candidates were judged; "
                           "only entries sharing the target's "
                           "substance are claimed as relatives."),
                "goals": [],
                "reason": "Candidates were token-pre-selected by the "
                          "host; false positives rejected — the "
                          "listed parents are the entries judged "
                          "genuinely related to the target.",
                "parents": ids})
        if prompt.startswith("[verb:comprehend]") and targets:
            t = targets[0]
            detail = str(t.get("detail", ""))
            goals = t.get("goals") or []
            goals_txt = "; ".join(str(g) for g in goals) \
                or "no goals stated in the entry"
            return json.dumps({
                "label": f"Meaning: {labels[0]}",
                "words": f"In plain terms, {labels[0]} means: {detail}",
                "detail": (
                    f"Claim: {detail}\n"
                    "Mechanism: the means the entry itself describes "
                    "in its detail text.\n"
                    f"Implications: if the claim holds, its stated "
                    f"goals follow: {goals_txt}.\n"
                    "Assumptions: the entry's own premises, taken as "
                    "stated; nothing external added.\n"
                    "Unknowns: what the entry does not specify "
                    "cannot be settled from its text alone."),
                "goals": [],
                "reason": "Breakdown drawn only from the entry's own "
                          "detail and goals text; interpretation "
                          "beyond the text is marked as inference.",
                "parents": ids})
        return json.dumps({
            "label": "Judge Note", "words": "noted", "detail": "",
            "goals": [], "reason": "generic", "parents": ids})


def _judge_session(p, owner, judge, subject="agent-a"):
    s = idock.DockedSession(
        p, subject, owner, "judge", judge, "judge:trackc",
        30, 8000, 8000, task="propose")
    coord = new_coordinator(p)
    coord.register_agent(subject)
    object.__setattr__(s, "_coordinator", coord)
    return s


def _seed_unit(p, label, detail, goals):
    pr = p.nursery.add(label, words=label, detail=detail, goals=goals)
    ctx = p.make_review_context(pr.id, reviewer="human:ace")
    r = p.confirm_proposal(pr.id, _producer="trackctest",
                           _review_context=ctx)
    assert r.get("ok"), r
    return pr.id


def _unit_id(p, label):
    for uid, u in p.cube.session.plane.units.items():
        if u.label == label:
            return uid
    raise AssertionError(f"unit {label} missing")


DETAIL = ("Neighbors share one car through a booking calendar and "
          "split fuel insurance and repair costs by miles driven")
GOALS = ["cheaper transport for the block",
         "fewer cars parked on the street"]


def smoke() -> bool:
    owners = ["TrackCDock", "TrackCNoCoord"]
    for o in owners:
        _cleanup(o)
    try:
        o = "TrackCDock"
        p = Program(owner=o)
        _seed_unit(p, "CarSharePool", DETAIL, GOALS)
        unit = _unit_id(p, "CarSharePool")
        # A PENDING Nursery idea: in the field snapshot as an idea,
        # never placed on the plane.
        pending = p.nursery.add(
            "RainBarrelMesh", words="RainBarrelMesh",
            detail="Roof barrels catch rain and share overflow "
                   "through linked hoses to garden beds",
            goals=["less tap water for gardens"])
        units_before = len(p.cube.session.plane.units)

        judge = ScriptedJudge()
        s = _judge_session(p, o, judge)

        _rec("comprehend_verb_present",
             callable(getattr(s, "comprehend", None)))
        if not callable(getattr(s, "comprehend", None)):
            return _finish(owners)

        # --- relate_field: field-wide relatability ------------------
        # Runs BEFORE the comprehend calls so the field is exactly
        # the seeded entries (comprehend proposals are legitimate
        # field entries too and would be candidates themselves).
        _rec("relate_field_verb_present",
             callable(getattr(s, "relate_field", None)))
        if callable(getattr(s, "relate_field", None)):
            # A true relative, still PENDING (affinity surfaces cannot
            # score Nursery ideas at all — the dock verb must see it).
            bike = p.nursery.add(
                "BikeShareDock", words="BikeShareDock",
                detail="Neighbors share one bike through a booking "
                       "calendar and split repair costs by miles",
                goals=["cheaper transport for the block"])
            # An unrelated entry: zero token overlap with the target.
            zebra = p.nursery.add(
                "ZebraQuilt", words="ZebraQuilt",
                detail="Striped fabric panels stitched for winter "
                       "warmth and cozy blankets",
                goals=["warm bedding"])
            # limit=1 on the clean field: only the top-ranked
            # candidate (the true relative) reaches the judge.
            r = s.relate_field(unit, limit=1)
            rf1 = [pm for pm in judge.prompts
                   if pm.startswith("[verb:relate_field]")]
            _rec("relate_field_limit_one_top_candidate_only",
                 r["ok"] and len(rf1) == 1
                 and "BikeShareDock" in rf1[0]
                 and "RainBarrelMesh" not in rf1[0]
                 and "ZebraQuilt" not in rf1[0], str(r)[:120])
            # Default call: ONE PENDING evolved proposal; the judge's
            # parents are a subset of the entries it was shown and
            # include the target and the true relative.
            judge.prompts.clear()
            n_before = len(p.nursery.proposals)
            r = s.relate_field(unit)
            prop = p.nursery.proposals.get(r.get("pid", ""))
            rf_prompts = [pm for pm in judge.prompts
                          if pm.startswith("[verb:relate_field]")]
            shown_ids = set()
            if rf_prompts and "[targets]\n" in rf_prompts[0]:
                blob = rf_prompts[0].split("[targets]\n", 1)[1] \
                    .split("\n\n[", 1)[0]
                shown_ids = {t.get("uid") or t.get("pid")
                             for t in json.loads(blob)}
            _rec("relate_field_lands_one_pending_evolved",
                 r["ok"] and r.get("verb") == "relate_field"
                 and prop is not None and prop.status == "pending"
                 and prop.kind == "evolved"
                 and len(p.nursery.proposals) == n_before + 1,
                 str(r)[:160])
            _rec("relate_field_parents_subset_of_shown",
                 prop is not None and set(prop.parents) <= shown_ids
                 and unit in prop.parents and bike.id in prop.parents,
                 f"parents={getattr(prop, 'parents', None)}")
            _rec("relate_field_prefilter_picks_true_relative",
                 len(rf_prompts) == 1 and "BikeShareDock" in rf_prompts[0]
                 and "ZebraQuilt" not in rf_prompts[0],
                 (rf_prompts[0][:200] if rf_prompts else "no prompt"))
            _rec("relate_field_pending_idea_is_candidate",
                 bool(rf_prompts) and bike.id in rf_prompts[0])
            # No candidate clears the pre-filter: honest receipt,
            # ZERO provider calls, nothing lands.
            calls = judge.calls
            n_before = len(p.nursery.proposals)
            r = s.relate_field(zebra.id)
            _rec("relate_field_no_candidates_receipt",
                 not r["ok"] and r["reason"] == "no_candidates"
                 and judge.calls == calls
                 and len(p.nursery.proposals) == n_before,
                 str(r)[:140])
            # Bad limit + unknown target: fail closed, no calls.
            calls = judge.calls
            r = s.relate_field(unit, limit=0)
            r2 = s.relate_field("no_such_id")
            _rec("relate_field_bad_limit_and_unknown_target",
                 not r["ok"] and r["reason"] == "bad_limit"
                 and not r2["ok"] and r2["reason"] == "unknown_target"
                 and judge.calls == calls, str(r)[:120])
            # Hostile + bloated judges rejected, nothing lands.
            for mode, name in (
                    ("hostile", "relate_field_hostile_rejected"),
                    ("bloat", "relate_field_bloat_rejected")):
                hj = ScriptedJudge(mode=mode)
                hs = _judge_session(p, o, hj)
                n_before = len(p.nursery.proposals)
                r = hs.relate_field(unit)
                _rec(name,
                     not r["ok"] and r["reason"] == "invalid_output"
                     and len(p.nursery.proposals) == n_before,
                     str(r)[:120])
                hs.undock()
            ev = [e for rec in p.dock_sessions.values()
                  for e in rec["proposals"]
                  if e["task"] == "relate_field"]
            _rec("relate_field_evidence_recorded",
                 len(ev) >= 2
                 and all(e["snapshot_id"] and len(e["snapshot_id"]) == 64
                         for e in ev), f"entries={len(ev)}")

        # --- comprehend a plane unit --------------------------------
        n_before = len(p.nursery.proposals)
        r = s.comprehend(unit)
        prop = p.nursery.proposals.get(r.get("pid", ""))
        _rec("comprehend_lands_one_pending",
             r["ok"] and r.get("verb") == "comprehend"
             and r.get("task") == "comprehend"
             and prop is not None and prop.status == "pending"
             and len(p.nursery.proposals) == n_before + 1,
             str(r)[:160])
        _rec("comprehend_kind_and_parents",
             prop is not None and prop.kind == "new"
             and prop.parents == [unit],
             f"kind={getattr(prop, 'kind', None)} "
             f"parents={getattr(prop, 'parents', None)}")
        _rec("comprehend_meaning_in_words",
             prop is not None and "In plain terms" in prop.words
             and "booking calendar" in prop.words,
             (prop.words if prop else "")[:160])
        _rec("comprehend_breakdown_sections",
             prop is not None and all(
                 sec in prop.detail for sec in (
                     "Claim:", "Mechanism:", "Implications:",
                     "Assumptions:", "Unknowns:"))
             and "cheaper transport for the block" in prop.detail,
             (prop.detail if prop else "")[:200])
        _rec("comprehend_prompt_carried_target_text",
             any(pm.startswith("[verb:comprehend]")
                 and DETAIL in pm for pm in judge.prompts))
        _rec("comprehend_never_places_or_confirms",
             len(p.cube.session.plane.units) == units_before
             and prop is not None and prop.status == "pending")

        # --- comprehend a PENDING nursery idea ----------------------
        r = s.comprehend(pending.id)
        prop2 = p.nursery.proposals.get(r.get("pid", ""))
        _rec("comprehend_pending_idea_target",
             r["ok"] and prop2 is not None
             and prop2.status == "pending" and prop2.kind == "new"
             and prop2.parents == [pending.id]
             and "Roof barrels catch rain" in prop2.words
             and p.nursery.proposals[pending.id].status == "pending",
             str(r)[:160])

        # --- host reason override + bad reason ----------------------
        r = s.comprehend(unit, reason="Host review: explain for Ace.")
        prop3 = p.nursery.proposals.get(r.get("pid", ""))
        _rec("comprehend_host_reason_wins",
             r["ok"] and prop3 is not None
             and prop3.reason == "Host review: explain for Ace.",
             str(r)[:160])
        calls = judge.calls
        r = s.comprehend(unit, reason="   ")
        _rec("comprehend_bad_reason_rejected",
             not r["ok"] and r["reason"] == "bad_reason"
             and judge.calls == calls, str(r)[:120])

        # --- unknown target: no provider call -----------------------
        calls = judge.calls
        r = s.comprehend("no_such_id")
        _rec("comprehend_unknown_target_no_call",
             not r["ok"] and r["reason"] == "unknown_target"
             and judge.calls == calls, str(r)[:120])

        # --- hostile + bloated judges rejected, nothing lands -------
        for mode, name in (("hostile", "comprehend_hostile_rejected"),
                           ("bloat", "comprehend_bloat_rejected")):
            hj = ScriptedJudge(mode=mode)
            hs = _judge_session(p, o, hj)
            n_before = len(p.nursery.proposals)
            r = hs.comprehend(unit)
            _rec(name,
                 not r["ok"] and r["reason"] == "invalid_output"
                 and len(p.nursery.proposals) == n_before,
                 str(r)[:120])
            hs.undock()

        # --- evidence trail -----------------------------------------
        ev = [e for rec in p.dock_sessions.values()
              for e in rec["proposals"]
              if e["task"] == "comprehend"]
        _rec("comprehend_evidence_recorded",
             len(ev) >= 3
             and all(e["snapshot_id"] and len(e["snapshot_id"]) == 64
                     for e in ev)
             and all(e["origin"].startswith("dock:agent-a:judge:")
                     for e in ev),
             f"entries={len(ev)}")

        # --- undocked: zero provider calls --------------------------
        s.undock()
        calls = judge.calls
        r = s.comprehend(unit)
        _rec("comprehend_undocked_no_call",
             not r["ok"] and r["reason"] == "undocked"
             and judge.calls == calls, str(r)[:120])
        if callable(getattr(s, "relate_field", None)):
            r = s.relate_field(unit)
            _rec("relate_field_undocked_no_call",
                 not r["ok"] and r["reason"] == "undocked"
                 and judge.calls == calls, str(r)[:120])

        # --- no coordinator: fail closed ----------------------------
        o2 = "TrackCNoCoord"
        p2 = Program(owner=o2)
        _seed_unit(p2, "LoneIdea", "detail", ["g"])
        lone = _unit_id(p2, "LoneIdea")
        judge2 = ScriptedJudge()
        s2 = idock.DockedSession(
            p2, "agent-a", o2, "judge", judge2, "judge:trackc",
            30, 8000, 8000, task="propose")
        r = s2.comprehend(lone)
        _rec("comprehend_fail_closed_without_coordinator",
             not r["ok"] and r["reason"] == "snapshot_unavailable"
             and judge2.calls == 0, str(r)[:160])
        if callable(getattr(s2, "relate_field", None)):
            r = s2.relate_field(lone)
            _rec("relate_field_fail_closed_without_coordinator",
                 not r["ok"] and r["reason"] == "snapshot_unavailable"
                 and judge2.calls == 0, str(r)[:160])
    finally:
        pass
    return _finish(owners)


def _finish(owners) -> bool:
    for o in owners:
        _cleanup(o)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        print(f"[{'PASS' if ok else 'FAIL'}] {name} | {detail}")
    print(f"\n=== RESULT: {passed}/{len(RESULTS)} PASS ===")
    return passed == len(RESULTS)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
