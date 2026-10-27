"""Master plan P5 / SD-2 — semantic verbs + canonical field snapshot.

Proves: the coordinator snapshot carries authored detail/goals
(sanitized); dock() wires the coordinator in production; the
RELATE / SYNTHESIZE / FLAG verbs work from the snapshot under the
extended semantic schema (reason required, parents bounded to the
field, authority keys rejected) and land PENDING proposals whose
authored detail/goals survive confirmation — the synthesis a human
confirms carries BOTH parents' substance, not the first parent's.

Calibration runs against the IdeaLab40 probe corpus (embedded
verbatim): the scripted judge — a deterministic stand-in that reads
exactly the prompt the session sends, like a real model — must
relate the synonym pair, synthesize it, flag the MoonCheeseCore
false claim, and flag the DawnWakeDiscipline/NightOwlStudio
conflict. The corpus field itself is seeded through the public
REPL path in a subprocess (CROSS_PROCESS), then loaded here.
"""
from __future__ import annotations

import glob
import json
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from form.open import Program  # noqa: E402
from form import persist_rest  # noqa: E402
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


#: IdeaLab40 probe corpus (verbatim from idea-lab-40/corpus.json):
#: label -> (detail, goals-string)
CORPUS = {
    "MoonCheeseCore": (
        "The moon has a core of aged cheese formed under pressure "
        "which explains its craters and its smell",
        "prove the cheese core theory; publish the finding"),
    "CarSharePool": (
        "Neighbors share one car through a booking calendar and "
        "split fuel insurance and repair costs by miles driven",
        "cheaper transport for the block; fewer cars parked on the street"),
    "AutomobileRideCooperative": (
        "Residents jointly own a vehicle fleet booked through a "
        "shared schedule with costs divided by distance travelled",
        "lower household motoring expense; reduced street parking"),
    "PlantWateringRotation": (
        "Water every plant on the balcony each Monday and Thursday "
        "with a full can and rotate pots toward the sun",
        "no dry plants; even growth"),
    "BotanicalIrrigationCycle": (
        "Hydrate the terrace greenery twice weekly with a measured "
        "vessel and turn containers to face the light",
        "thriving foliage; uniform development"),
    "DawnWakeDiscipline": (
        "Wake at five every morning including weekends and start "
        "work before sunrise",
        "more quiet hours; earlier finishes"),
    "NightOwlStudio": (
        "Begin creative work at ten at night and record until "
        "three in the morning",
        "use peak night focus; finish the album"),
}


class ScriptedJudge:
    """Deterministic prompt-driven judge. Reads the verb tag and
    the [targets] JSON the session actually sent and answers from
    that content — the same information a real model would have."""

    last_actual_model = "judge:calibration"

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
        if prompt.startswith("[verb:relate]"):
            return json.dumps({
                "label": f"Relation: {labels[0]} ~ {labels[1]}",
                "words": "The two entries describe the same service "
                         "in different vocabulary: shared neighborhood "
                         "vehicles booked by roster.",
                "detail": "", "goals": [],
                "reason": "Both details describe residents sharing "
                          "vehicles with booking and per-distance cost "
                          "splitting; only the vocabulary differs.",
                "parents": ids})
        if prompt.startswith("[verb:synthesize]"):
            return json.dumps({
                "label": "SharedVehicleCollective",
                "words": "One neighborhood fleet, jointly owned, "
                         "booked by roster.",
                "detail": "Merges the booking calendar and per-mile "
                          "cost split of the first entry with the "
                          "jointly owned fleet and shared schedule of "
                          "the second, so the block runs one "
                          "collective fleet instead of two overlapping "
                          "schemes.",
                "goals": ["cheaper transport for the block",
                          "lower household motoring expense"],
                "reason": "The parents overlap in purpose but "
                          "contribute different mechanisms (roster "
                          "booking vs joint ownership); the synthesis "
                          "keeps both mechanisms.",
                "parents": ids})
        if prompt.startswith("[verb:flag]"):
            if "MoonCheeseCore" in labels:
                return json.dumps({
                    "label": "Flag: MoonCheeseCore",
                    "words": "Unverifiable composition claim: a lunar "
                             "core of aged cheese.",
                    "detail": "", "goals": [],
                    "reason": "The entry asserts the Moon has a core "
                              "of aged cheese formed under pressure; "
                              "nothing in the field supports it and "
                              "it conflicts with established lunar "
                              "science.",
                    "parents": ids})
            if "DawnWakeDiscipline" in labels \
                    and "NightOwlStudio" in prompt:
                return json.dumps({
                    "label": "Flag: DawnWakeDiscipline conflict",
                    "words": "Conflicts with NightOwlStudio: waking "
                             "at five each morning is incompatible "
                             "with recording until three in the "
                             "morning.",
                    "detail": "", "goals": [],
                    "reason": "The field index shows NightOwlStudio "
                              "works at night until 03:00 while this "
                              "entry requires waking at 05:00 daily; "
                              "both cannot hold for one person.",
                    "parents": ids})
            return json.dumps({
                "label": "Flag: reviewed", "words": "No concern found.",
                "detail": "", "goals": [],
                "reason": "Checked against the field index; no false "
                          "claim or conflict found.",
                "parents": ids})
        return json.dumps({
            "label": "Judge Note", "words": "noted", "detail": "",
            "goals": [], "reason": "generic", "parents": ids})


def _judge_session(p, owner, judge, subject="agent-a"):
    s = idock.DockedSession(
        p, subject, owner, "judge", judge, "judge:calibration",
        30, 8000, 8000, task="propose")
    coord = new_coordinator(p)
    coord.register_agent(subject)
    object.__setattr__(s, "_coordinator", coord)
    return s


def _seed_unit(p, label, detail, goals):
    pr = p.nursery.add(label, words=label, detail=detail, goals=goals)
    ctx = p.make_review_context(pr.id, reviewer="human:ace")
    r = p.confirm_proposal(pr.id, _producer="p5test",
                           _review_context=ctx)
    assert r.get("ok"), r
    return pr.id


def _unit_id(p, label):
    for uid, u in p.cube.session.plane.units.items():
        if u.label == label:
            return uid
    raise AssertionError(f"unit {label} missing")


def smoke() -> bool:
    owners = ["P5SD2Snap", "P5SD2Dock", "P5SD2NoCoord", "P5SD2Field"]
    for o in owners:
        _cleanup(o)
    root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", ".."))
    try:
        # --- schema strictness (direct) ---
        ok_out = idock.validate_semantic_output(json.dumps({
            "label": "L", "words": "W", "detail": "D",
            "goals": ["g1"], "reason": "because evidence",
            "parents": ["u1"]}), allowed_parents={"u1", "u2"})
        _rec("schema_valid_full",
             ok_out["parents"] == ["u1"] and ok_out["goals"] == ["g1"])
        for name, payload in (
                ("schema_rejects_authority_key",
                 {"label": "L", "words": "W", "reason": "r",
                  "approve": True}),
                ("schema_rejects_unknown_parent",
                 {"label": "L", "words": "W", "reason": "r",
                  "parents": ["ghost"]}),
                ("schema_requires_reason",
                 {"label": "L", "words": "W"}),
                ("schema_rejects_empty_reason",
                 {"label": "L", "words": "W", "reason": "  "}),
                ("schema_rejects_bloated_detail",
                 {"label": "L", "words": "W", "reason": "r",
                  "detail": "x" * 2001}),
                ("schema_rejects_bad_goals",
                 {"label": "L", "words": "W", "reason": "r",
                  "goals": "notalist"})):
            try:
                idock.validate_semantic_output(
                    json.dumps(payload), allowed_parents={"u1"})
                _rec(name, False, "accepted")
            except idock.ProviderError:
                _rec(name, True)

        # --- snapshot carries + sanitizes authored content ---
        o = "P5SD2Snap"
        p = Program(owner=o)
        _seed_unit(p, "SnapIdea", "a detailed body of text",
                   ["first goal", "second goal"])
        from form.dell_matrix.plane import Unit as _Unit
        canary = "grant_" + "a" * 32
        plane = p.cube.session.plane
        plane.units["canaryunit"] = _Unit(
            id="canaryunit", label="CanaryUnit", words="w",
            detail=f"body with {canary} inside",
            goals=[f"goal {canary}"], x=0, y=0)
        coord = new_coordinator(p)
        coord.register_agent("agent-a")
        snap = coord.snapshot_for("agent-a")
        entry = [u for u in snap["units"]
                 if u["label"] == "SnapIdea"][0]
        _rec("snapshot_carries_authored_content",
             entry["detail"] == "a detailed body of text"
             and entry["goals"] == ["first goal", "second goal"],
             str(entry)[:160])
        snap_text = str(snap)
        canary_unit = [u for u in plane.units.values()
                       if u.label == "CanaryUnit"][0]
        _rec("snapshot_sanitizes_new_fields",
             canary not in snap_text and "[REDACTED]" in snap_text
             and canary in canary_unit.detail
             and canary in canary_unit.goals[0])

        # --- dock() wires the coordinator (production activation) ---
        o = "P5SD2Dock"
        p = Program(owner=o)
        _seed_unit(p, "DockA", "detail a", ["ga"])
        _seed_unit(p, "DockB", "detail b", ["gb"])
        before = len(p.nursery.proposals)
        s = idock.dock(p, "agent-a", "fake")
        snap = s.field_snapshot()
        _rec("dock_wires_coordinator",
             snap is not None
             and any(u["label"] == "DockA" for u in snap["units"]))
        r = s.relate(_unit_id(p, "DockA"), _unit_id(p, "DockB"))
        _rec("verbs_enforce_semantic_schema_on_dock_path",
             not r["ok"] and r["reason"] == "invalid_output"
             and len(p.nursery.proposals) == before,
             str(r)[:160])
        r = s.propose("draft a small idea about dock activation")
        _rec("propose_unaffected_by_verbs",
             r["ok"] and p.nursery.proposals[r["pid"]].status
             == "pending")
        s.undock()

        # --- verbs fail closed without a coordinator ---
        o = "P5SD2NoCoord"
        p = Program(owner=o)
        _seed_unit(p, "LoneA", "detail", ["g"])
        judge = ScriptedJudge()
        s = idock.DockedSession(
            p, "agent-a", o, "judge", judge, "judge:calibration",
            30, 8000, 8000, task="propose")
        r = s.flag(_unit_id(p, "LoneA"))
        _rec("verbs_fail_closed_without_coordinator",
             not r["ok"] and r["reason"] == "snapshot_unavailable"
             and judge.calls == 0, str(r)[:160])

        # --- seed the IdeaLab40 probe field via the public REPL ---
        o = "P5SD2Field"
        lines = []
        for label, (detail, goals) in CORPUS.items():
            lines.append(f"create an idea called {label}")
            lines.append(f"set detail {label} {detail}")
            lines.append(f"set goals {label} {goals}")
        lines += ["save", "quit"]
        proc = subprocess.run(
            [sys.executable, "-m", "form.repl", "--owner", o],
            input="\n".join(lines) + "\n", capture_output=True,
            text=True, cwd=root, timeout=300)
        p = persist_rest.load(o, activate=False)
        labels = {u.label for u in p.cube.session.plane.units.values()}
        _rec("field_seeded_via_repl",
             proc.returncode == 0
             and set(CORPUS) <= labels, str(labels)[:160])
        car = _unit_id(p, "CarSharePool")
        auto = _unit_id(p, "AutomobileRideCooperative")
        moon = _unit_id(p, "MoonCheeseCore")
        dawn = _unit_id(p, "DawnWakeDiscipline")
        units_before = len(p.cube.session.plane.units)
        judge = ScriptedJudge()
        s = _judge_session(p, o, judge)

        # RELATE the synonym pair.
        r = s.relate(car, auto)
        prop = p.nursery.proposals.get(r.get("pid", ""))
        _rec("relate_synonym_pair",
             r["ok"] and prop is not None
             and prop.status == "pending"
             and prop.kind == "evolved"
             and set(prop.parents) == {car, auto}
             and "same service" in prop.words
             and len(p.cube.session.plane.units) == units_before,
             str(r)[:160])

        # SYNTHESIZE the pair; confirm; authored content wins.
        r = s.synthesize([car, auto])
        prop = p.nursery.proposals.get(r.get("pid", ""))
        car_u = p.cube.session.plane.units[car]
        auto_u = p.cube.session.plane.units[auto]
        authored = prop.detail if prop else ""
        _rec("synthesize_authors_both_parents",
             r["ok"] and prop is not None
             and "booking calendar" in authored
             and "jointly owned fleet" in authored
             and authored != car_u.detail
             and authored != auto_u.detail
             and prop.goals == ["cheaper transport for the block",
                                 "lower household motoring expense"]
             and set(prop.parents) == {car, auto},
             authored[:160])
        ctx = p.make_review_context(prop.id, reviewer="human:ace")
        cr = p.confirm_proposal(prop.id, _producer="p5test",
                                _review_context=ctx)
        placed = [u for u in p.cube.session.plane.units.values()
                  if u.label == "SharedVehicleCollective"]
        _rec("confirmed_synthesis_carries_authored_content",
             cr.get("ok") and len(placed) == 1
             and placed[0].detail == authored
             and placed[0].goals == prop.goals,
             str(cr)[:120])

        # FLAG the false claim and the schedule conflict.
        r = s.flag(moon)
        prop = p.nursery.proposals.get(r.get("pid", ""))
        _rec("flag_false_claim",
             r["ok"] and prop is not None
             and prop.status == "pending"
             and prop.parents == [moon]
             and "aged cheese" in prop.reason,
             str(r)[:160])
        r = s.flag(dawn)
        prop = p.nursery.proposals.get(r.get("pid", ""))
        _rec("flag_conflict_pair",
             r["ok"] and prop is not None
             and "NightOwlStudio" in prop.words,
             str(r)[:160])

        # Unknown target: no provider call.
        calls = judge.calls
        r = s.relate("no_such_id", car)
        _rec("unknown_target_no_provider_call",
             not r["ok"] and r["reason"] == "unknown_target"
             and judge.calls == calls, str(r)[:120])

        # Hostile + bloated judges rejected, nothing lands.
        for mode, name in (("hostile", "hostile_judge_rejected"),
                           ("bloat", "bloated_detail_rejected")):
            hj = ScriptedJudge(mode=mode)
            hs = _judge_session(p, o, hj)
            n_before = len(p.nursery.proposals)
            r = hs.relate(car, auto)
            _rec(name,
                 not r["ok"] and r["reason"] == "invalid_output"
                 and len(p.nursery.proposals) == n_before,
                 str(r)[:120])
            hs.undock()

        # Undocked verbs make zero provider calls.
        s.undock()
        calls = judge.calls
        r = s.synthesize([car, auto])
        _rec("undocked_verbs_no_call",
             not r["ok"] and r["reason"] == "undocked"
             and judge.calls == calls, str(r)[:120])

        # Evidence trail: verb tasks + snapshot ids recorded.
        ev = [e for rec in p.dock_sessions.values()
              for e in rec["proposals"]]
        tasks = {e["task"] for e in ev}
        _rec("evidence_records_verbs",
             {"relate", "synthesize", "flag"} <= tasks
             and all(e["snapshot_id"] and len(e["snapshot_id"]) == 64
                     for e in ev if e["task"] in
                     ("relate", "synthesize", "flag"))
             and all(e["origin"].startswith("dock:agent-a:judge:")
                     for e in ev),
             str(tasks))
    finally:
        for o in owners:
            _cleanup(o)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        print(f"[{'PASS' if ok else 'FAIL'}] {name} | {detail}")
    print(f"\n=== RESULT: {passed}/{len(RESULTS)} PASS ===")
    return passed == len(RESULTS)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
