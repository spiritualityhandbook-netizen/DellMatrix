"""Snapshot revalidation follow-up — Q-SNAP.1 (Director CERTIFICATION
HOLD for G-11, Gmail 1a1bf02a4a0f00f7, 2026-11-09 00:32 CST).

PR #336 merged (693fa77) stands as delivered code + bounded evidence,
NOT certification. The Director named three revalidation gaps; this
suite pins them failing-first. Unique defect IDs:

- QSNAP1-1 (gap 1): DockedSession._revalidate_retrieved compares only
  status/label/words/detail/revision_number, while the canonical
  _source_identity (agent_coordinator) hashes goals for BOTH
  collections and x/y coordinates for units. A goals edit on an idea,
  or a goals edit / coordinate move on a unit, between retrieval and
  incorporation is therefore invisible: the verb lands on stale data.
  (Units carry no status/revision_number at all in their entries.)
- QSNAP1-2 (gap 2): relate_field retrieves an out-of-slice target via
  _retrieve_into_index and performs NO revalidation of that retrieval
  of its own before the incorporation path; whatever protection it
  gets is inherited incidentally from _verb's (incomplete, per
  QSNAP1-1) field set. Deletion/status races ARE refused through
  _verb (controls below); goals races are NOT (defect check below).
- QSNAP1-3 (gap 3): retrieve_for's 16-id bound counts INPUT elements
  (20 copies of one valid id are refused even though they dedupe to
  one), and there is no per-id length bound: a 100,000-char id is
  echoed raw in the "absent" list, an unbounded output exposure.

Race model: deterministic, in-window. The scripted judge mutates the
target INSIDE generate() — i.e. after retrieval, before
incorporation — exactly the window revalidation exists to close.
No timing, no threads.

Contract pinned by this suite:
- any semantically relevant change to a retrieved entry in-window
  (content, goals, coordinates, lifecycle, deletion) refuses the
  verb with reason stale_target and lands NOTHING;
- relate_field offers the same guarantee for its retrieved target;
- retrieve_for's bound counts DISTINCT ids (duplicates dedupe
  before the bound), >16 distinct ids is a hard refusal with no
  partial result, and pathological id lengths are refused with a
  bounded, non-reflecting error (the raw id never appears in any
  result or error text).

Controls: label mutation / deletion / status change in-window are
already refused; plain beyond-slice comprehend and relate_field
land PENDING when nothing mutates; unknown-subject retrieval is
refused.

Units note: plane units are stub objects inserted into plane.units
exercising the coordinator's getattr entry contract (label/words/
detail/goals/x/y) — the same fields _unit_entry and _source_identity
read. Ideas are real Nursery proposals.
"""
from __future__ import annotations

import glob
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from form.open import Program  # noqa: E402
from form.dell_matrix import inference_dock as idock  # noqa: E402
from form.dell_matrix.agent_coordinator import (  # noqa: E402
    new_coordinator, CoordinatorError)

RESULTS = []


def _rec(name, cond, detail=""):
    RESULTS.append((name, bool(cond), str(detail)[:200]))


def _cleanup(owner):
    base = os.path.join(os.path.dirname(__file__), "state")
    for pat in (f"program_{owner}.json", f"nursery_{owner}.json",
                f"checkpoint_{owner}_*", f"confirm_{owner}.journal.json",
                f"checkpoint_{owner}.journal.json"):
        for f in glob.glob(os.path.join(base, pat)):
            os.remove(f)
    for d in glob.glob(os.path.join(base, f"ideas_{owner}*")):
        if os.path.isdir(d):
            shutil.rmtree(d)


class MutatingJudge:
    """Scripted judge; `hook` fires inside generate() (in-window)."""

    last_actual_model = "judge:qsnap1"

    def __init__(self, hook=None):
        self.calls = 0
        self.hook = hook

    def generate(self, prompt, *, timeout_s, max_chars):
        self.calls += 1
        if self.hook is not None:
            self.hook()
        targets = []
        if "[targets]\n" in prompt:
            blob = prompt.split("[targets]\n", 1)[1].split("\n\n[", 1)[0]
            targets = json.loads(blob)
        ids = [t.get("uid") or t.get("pid") for t in targets]
        labels = [t.get("label", "") for t in targets]
        return json.dumps({
            "label": "Relation: " + " + ".join(labels),
            "words": "synthesized from all shown parents",
            "detail": "Authored from every parent's substance.",
            "goals": [],
            "reason": "All shown parents are genuinely related.",
            "parents": ids})


def _session(p, owner, judge, coord, subject="agent-a"):
    s = idock.DockedSession(
        p, subject, owner, "judge", judge, "judge:qsnap1",
        30, 8000, 8000, task="propose")
    object.__setattr__(s, "_coordinator", coord)
    return s


class _StubUnit:
    def __init__(self, label, x, y):
        self.label = label
        self.words = "alpha stub"
        self.detail = "stub detail about shared topic alpha"
        self.goals = ["g0"]
        self.x = x
        self.y = y


def smoke() -> bool:
    owner = "QsnapRevalidation"
    _cleanup(owner)
    try:
        return _run(owner)
    finally:
        _cleanup(owner)


def _run(owner):
    p = Program(owner=owner)
    coord = new_coordinator(p)
    coord.register_agent("agent-a")

    ids = []
    for i in range(250):
        pr = p.nursery.add(
            f"Field Entry {i:03d}", words=f"entry{i}",
            detail=f"detail for entry {i} about shared topic alpha",
            goals=["g0"])
        ids.append(pr.id)
    plane = p.cube.session.plane
    for i in range(250):
        plane.units[f"stub_{i:03d}"] = _StubUnit(f"Stub {i:03d}", i, i)

    def verb_refused(verb_call, judge):
        s = _session(p, owner, judge, coord)
        before = set(p.nursery.proposals)
        r = verb_call(s)
        new_pids = set(p.nursery.proposals) - before
        return (not r.get("ok") and r.get("reason") == "stale_target"
                and not new_pids), r

    # --- controls: boundaries already enforced ----------------------
    victim = ids[235]
    prop = p.nursery.proposals[victim]
    ok, r = verb_refused(
        lambda s: s.comprehend(victim),
        MutatingJudge(lambda: setattr(prop, "label", "MUTATED")))
    _rec("control.label_mutation_refused_stale", ok, str(r)[:120])
    prop.label = "Field Entry 235"

    victim = ids[234]

    def _delete():
        p.nursery.reject(victim)
        p.nursery.clear_rejected()
    ok, r = verb_refused(lambda s: s.comprehend(victim),
                         MutatingJudge(_delete))
    _rec("control.deletion_refused_stale", ok, str(r)[:120])

    victim = ids[237]
    prop = p.nursery.proposals[victim]
    ok, r = verb_refused(
        lambda s: s.relate_field(victim),
        MutatingJudge(lambda: p.nursery.reject(victim)))
    _rec("control.relate_field_status_change_refused_stale", ok,
         str(r)[:120])

    victim = ids[236]

    def _delete2():
        p.nursery.reject(victim)
        p.nursery.clear_rejected()
    ok, r = verb_refused(lambda s: s.relate_field(victim),
                         MutatingJudge(_delete2))
    _rec("control.relate_field_deletion_refused_stale", ok,
         str(r)[:120])

    s = _session(p, owner, MutatingJudge(), coord)
    n0 = len(p.nursery.proposals)
    r = s.comprehend(ids[233])
    _rec("control.no_mutation_comprehend_lands",
         r.get("ok") and len(p.nursery.proposals) == n0 + 1,
         str(r)[:120])
    n0 = len(p.nursery.proposals)
    r = s.relate_field(ids[232])
    _rec("control.no_mutation_relate_field_lands",
         r.get("ok") and len(p.nursery.proposals) == n0 + 1,
         str(r)[:120])

    try:
        coord.retrieve_for("agent-a", [f"fake_{i}" for i in range(17)])
        _rec("control.over_bound_distinct_refused_no_partial", False,
             "no error raised")
    except CoordinatorError:
        _rec("control.over_bound_distinct_refused_no_partial", True)
    try:
        coord.retrieve_for("no-such-subject", [ids[0]])
        _rec("control.unknown_subject_refused", False, "no error")
    except CoordinatorError:
        _rec("control.unknown_subject_refused", True)

    # --- QSNAP1-1: field-set gap in _revalidate_retrieved -----------
    victim = ids[239]
    prop = p.nursery.proposals[victim]
    ok, r = verb_refused(
        lambda s: s.comprehend(victim),
        MutatingJudge(lambda: setattr(prop, "goals", ["MUTATED-GOAL"])))
    _rec("G1.idea_goals_mutation_refused_stale", ok, str(r)[:120])
    prop.goals = ["g0"]

    unit = plane.units["stub_239"]
    ok, r = verb_refused(
        lambda s: s.comprehend("stub_239"),
        MutatingJudge(lambda: (setattr(unit, "x", 9999),
                               setattr(unit, "y", 8888))))
    _rec("G1.unit_coordinates_mutation_refused_stale", ok, str(r)[:120])
    unit.x, unit.y = 239, 239

    unit = plane.units["stub_238"]
    ok, r = verb_refused(
        lambda s: s.comprehend("stub_238"),
        MutatingJudge(lambda: setattr(unit, "goals", ["MUTATED-GOAL"])))
    _rec("G1.unit_goals_mutation_refused_stale", ok, str(r)[:120])
    unit.goals = ["g0"]

    unit = plane.units["stub_237"]
    ok, r = verb_refused(
        lambda s: s.comprehend("stub_237"),
        MutatingJudge(lambda: setattr(unit, "label", "MUTATED")))
    _rec("control.unit_label_mutation_refused_stale", ok, str(r)[:120])
    unit.label = "Stub 237"

    # --- QSNAP1-2: relate_field's own retrieved target ----------------
    victim = ids[238]
    prop = p.nursery.proposals[victim]
    ok, r = verb_refused(
        lambda s: s.relate_field(victim),
        MutatingJudge(lambda: setattr(prop, "goals", ["MUTATED-GOAL"])))
    _rec("G2.relate_field_goals_mutation_refused_stale", ok,
         str(r)[:120])
    prop.goals = ["g0"]

    # --- QSNAP1-3: bound counts distinct; id length bounded ----------
    try:
        res = coord.retrieve_for("agent-a", [ids[10]] * 20)
        entries = res.get("entries", []) if isinstance(res, dict) else []
        _rec("G3.duplicates_counted_as_distinct", len(entries) == 1
             and entries[0].get("pid") == ids[10],
             f"entries={len(entries)}")
    except CoordinatorError as e:
        _rec("G3.duplicates_counted_as_distinct", False,
             f"raised: {e}")

    big = "x" * 100000
    try:
        res = coord.retrieve_for("agent-a", [big])
        blob = json.dumps(res)
        _rec("G3.pathological_id_length_bounded",
             big not in blob and len(blob) < 5000,
             f"result_len={len(blob)} raw_echo={big in blob}")
    except CoordinatorError as e:
        _rec("G3.pathological_id_length_bounded",
             big not in str(e) and len(str(e)) < 500,
             f"error_len={len(str(e))}")

    passed = sum(1 for _, ok_, _ in RESULTS if ok_)
    for name, ok_, detail in RESULTS:
        print(f"{'PASS' if ok_ else 'FAIL'} {name} :: {detail}")
    print(f"SNAPSHOT_REVALIDATION: {passed}/{len(RESULTS)}")
    return passed == len(RESULTS)


def main() -> int:
    return 0 if smoke() else 1


if __name__ == "__main__":
    raise SystemExit(main())
