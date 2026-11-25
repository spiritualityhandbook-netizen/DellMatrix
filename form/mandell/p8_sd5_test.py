"""Master plan P8 / SD-5 — the inside-out loop, first full turn.

Proves the loop machinery end to end on a test dev owner: a
docked session files a kind="design" proposal with authored
detail/goals (propose schema extension, SD-2 bounds); invalid
kinds are refused before any provider call; the scoped Director
recommends; the human gate confirms; design_loop.chain()
assembles the whole receipt chain in one place (proposal, dock
filing evidence, recommendations, gate event); the host records
the implementation (PR) and the chain completes and persists.
Also proves the REPL review surface now displays Director
recommendations (the first real design, implemented), and the
dormant-cluster disposition: retired modules are absent,
AutoGrowth keeps only its live-tested auto-propose authority,
and IntrinsicAgent keeps its live state authority without the
retired free-walk behavior.
"""
from __future__ import annotations

import glob
import importlib.util
import json
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from form.open import Program  # noqa: E402
from form import persist_rest  # noqa: E402
from form.dell_matrix import design_loop as dl  # noqa: E402
from form.dell_matrix import inference_dock as idock  # noqa: E402

RESULTS = []

RETIRED = [
    "free_matrix", "matrix_awake", "act_on_seen", "delta_pressure",
    "free_matrix_150_audit", "brain", "flash_path", "world_predict",
    "floor_spirit", "idea_grow",
]


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


class DesignJudge:
    last_actual_model = "judge:sd5-suite"

    def __init__(self):
        self.calls = 0

    def generate(self, prompt, *, timeout_s, max_chars):
        self.calls += 1
        return json.dumps({
            "label": "LoopLedgerView",
            "words": "A worked design carried by the loop suite.",
            "detail": "Authored design detail from the judge, "
                      "carried on the proposal itself.",
            "goals": ["prove the loop", "keep the gate sovereign"]})


def smoke() -> bool:
    owners = ["P8DevLoop", "P8DevRepl"]
    for o in owners:
        _cleanup(o)
    root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", ".."))
    try:
        # --- file a design in a dev-scope matrix ---
        o = "P8DevLoop"
        dev = Program(owner=o)
        judge = DesignJudge()
        session = idock.DockedSession(
            dev, "agent:uni", o, "judge", judge, "judge:sd5-suite",
            30, 8000, 8000, task="design")
        bad = session.propose("file a widget", kind="widget")
        _rec("invalid_kind_refused_before_provider",
             bad.get("ok") is False
             and bad.get("reason") == "invalid_kind"
             and judge.calls == 0)
        out = session.propose(
            "Design: prove the inside-out loop end to end.",
            reason="SD-5 acceptance: one real design travels the "
                   "full loop.",
            kind="design")
        pid = out.get("pid")
        prop = dev.nursery.proposals.get(pid or "")
        _rec("design_filed_with_authored_content",
             out.get("ok") is True and prop is not None
             and prop.kind == "design"
             and prop.detail.startswith("Authored design detail")
             and prop.goals == ["prove the loop",
                                "keep the gate sovereign"]
             and prop.status == "pending"
             and prop.origin.startswith("dock:agent:uni:judge:"),
             f"pid={pid}")
        dl.record_event(dev, pid, "filed", actor="agent:uni",
                        note="suite loop turn")

        # --- Director recommends; human gate decides ---
        director = dev.bind_director_endpoint()
        rec_out = director.recommend(
            pid, "accept", "machinery is the acceptance test itself")
        _rec("director_recommends_design",
             rec_out.get("ok") is True
             and dev.nursery.proposals[pid].status == "pending")
        ctx = dev.make_review_context(pid, reviewer="human:ace")
        conf = dev.confirm_proposal(pid, _producer="host:uni",
                                    _review_context=ctx)
        _rec("human_gate_confirms_design",
             conf.get("ok") is True
             and dev.nursery.proposals[pid].status == "confirmed")
        dl.record_event(dev, pid, "gate", actor="human:ace",
                        note="suite gate")

        # --- chain assembles before implementation ---
        ch = dl.chain(dev, pid)
        _rec("chain_assembles_filed_gate",
             ch["found"] is True
             and ch["proposal"]["kind"] == "design"
             and ch["filed"]["subject"] == "agent:uni"
             and ch["filed"]["task"] == "design"
             and len(ch["recommendations"]) == 1
             and ch["recommendations"][0]["decision"] == "accept"
             and ch["gate"]["actor"] == "human:ace"
             and ch["implemented"] is None)

        # --- host records the implementation; chain completes ---
        dl.record_event(dev, pid, "implemented", actor="host:uni",
                        pr=116, merge_sha="deadbeefcafe",
                        note="suite stand-in for the merged PR")
        try:
            dl.record_event(dev, pid, "implemented",
                            actor="host:uni", pr=0)
            bad_impl = False
        except ValueError:
            bad_impl = True
        _rec("implemented_event_requires_pr", bad_impl)
        dev.save()
        dev2 = persist_rest.load(o, activate=False)
        ch2 = dl.chain(dev2, pid)
        _rec("chain_persists_complete",
             ch2["implemented"]["pr"] == 116
             and ch2["implemented"]["merge_sha"] == "deadbeefcafe"
             and [e["event"] for e in ch2["events"]] ==
             ["filed", "gate", "implemented"],
             str([e["event"] for e in ch2["events"]]))
        session.undock()
        director.undock()

        # --- the implemented design: REPL shows recommendations ---
        o = "P8DevRepl"
        script = "\n".join([
            "connect", "ask draft a plan for the loop", "leave",
            "quit"]) + "\n"
        r1 = subprocess.run(
            [sys.executable, "-m", "form.repl", "--owner", o],
            input=script, capture_output=True, text=True, cwd=root,
            timeout=300)
        # Give the pending proposal a Director recommendation via
        # the API, persist, then view proposals in a fresh REPL.
        p = persist_rest.load(o, activate=False)
        pend = [pr for pr in p.nursery.proposals.values()
                if pr.status == "pending"]
        d = p.bind_director_endpoint()
        d.recommend(pend[0].id, "accept",
                    "suite recommendation marker ZQ7")
        d.undock()
        p.save()
        r2 = subprocess.run(
            [sys.executable, "-m", "form.repl", "--owner", o,
             "--load"],
            input="proposals\nquit\n", capture_output=True,
            text=True, cwd=root, timeout=300)
        _rec("repl_review_shows_director_recommendation",
             r1.returncode == 0 and r2.returncode == 0
             and "director: recommends accept" in r2.stdout
             and "ZQ7" in r2.stdout,
             r2.stdout[-200:] if r2.returncode == 0
             else r2.stderr[-200:])

        # --- dormant-cluster disposition ---
        absent = [m for m in RETIRED
                  if importlib.util.find_spec(
                      f"form.dell_matrix.{m}") is not None]
        _rec("retired_modules_absent", absent == [], str(absent))
        from form.dell_matrix import auto_growth, intrinsic_agent
        _rec("autogrowth_keeps_only_live_authority",
             hasattr(auto_growth.AutoGrowth, "_nursery_auto")
             and not hasattr(auto_growth.AutoGrowth, "step")
             and not hasattr(auto_growth.AutoGrowth, "_judge")
             and not hasattr(auto_growth.AutoGrowth, "harvest_net"))
        _rec("intrinsic_agent_state_authority_kept_walk_retired",
             hasattr(intrinsic_agent.IntrinsicAgent, "observe")
             and hasattr(intrinsic_agent.IntrinsicAgent, "to_dict")
             and hasattr(intrinsic_agent.IntrinsicAgent,
                         "propose_action")
             and not hasattr(intrinsic_agent.IntrinsicAgent, "step"))
        _rec("dev_owner_constant", dl.DEV_OWNER == "DellMatrixDev")
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
