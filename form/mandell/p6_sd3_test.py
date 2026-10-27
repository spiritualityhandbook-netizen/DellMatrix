"""Master plan P6 / SD-3 — growth demotion: docked synthesis routing.

Proves: with a docked session, RingedGrowth's Solstice pair crosses
are authored by the docked mind through SYNTHESIZE (token affinity
is only the pre-filter that picks and orders the pairs); a failed
verb call falls back to the token composition for that pair; token
growth (undocked, or single-parent drift in both modes) is labeled
origin="growth:token" (body restores "growth:body") so the review
gate always knows which mechanism authored a proposal; and the
REPL connect surface exposes `grow` with honest mode reporting
(CROSS_PROCESS).
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


FIELD = [
    ("VocalChain",
     "fixed mixing chain for rap vocals with compression saturation "
     "and loudness target for streaming release",
     ["consistent vocal level", "faster mix turnaround"]),
    ("MixBusChain",
     "fixed mixing chain for rap vocals with compression saturation "
     "and loudness target for streaming release daily",
     ["consistent vocal level", "faster mix turnaround"]),
    ("SleepShutdown",
     "night routine that closes screens and dims lights for deep "
     "sleep and recovery before early studio work",
     ["deep sleep", "early studio energy"]),
    ("NightRecovery",
     "night routine that closes screens and dims lights for deep "
     "sleep and recovery before morning studio work",
     ["deep sleep", "morning studio energy"]),
    ("QuantumLatticeX",
     "quixotic zephyr jumbles vexed boulders with cryptic fjord "
     "harmonics under ultraviolet moonlight",
     ["oblique objective"]),
    ("ZebraQuiltY",
     "striped equine blanket patterns woven from savanna grasses "
     "and dyed with ochre pigments",
     ["textile objective"]),
]


def _seed(p):
    for label, detail, goals in FIELD:
        pr = p.nursery.add(label, words=label, detail=detail,
                           goals=goals)
        ctx = p.make_review_context(pr.id, reviewer="human:ace")
        r = p.confirm_proposal(pr.id, _producer="p6test",
                               _review_context=ctx)
        assert r.get("ok"), r


class GrowthJudge:
    """Prompt-driven judge: synthesizes whatever pair the session
    sends (reads the [targets] JSON), or returns garbage in
    'garbage' mode to exercise the token fallback."""

    last_actual_model = "judge:growth"

    def __init__(self, mode="normal"):
        self.calls = 0
        self.mode = mode

    def generate(self, prompt, *, timeout_s, max_chars):
        self.calls += 1
        if self.mode == "garbage":
            return "this is not JSON at all {{{"
        tg = json.loads(
            prompt.split("[targets]\n", 1)[1].split("\n\n[", 1)[0])
        ids = [t.get("uid") or t.get("pid") for t in tg]
        labels = [t["label"] for t in tg]
        return json.dumps({
            "label": f"{labels[0]}Synthesis",
            "words": "authored synthesis of the pair",
            "detail": f"Authored combination of {labels[0]} and "
                      f"{labels[1]} drawing on both entries' "
                      f"substance.",
            "goals": ["combined goal"],
            "reason": "The pair shares mechanism and purpose; "
                      "synthesis stated by the judge.",
            "parents": ids})


def _judge_session(p, owner, judge):
    s = idock.DockedSession(
        p, "agent-a", owner, "judge", judge, "judge:growth",
        30, 8000, 8000, task="propose")
    coord = new_coordinator(p)
    coord.register_agent("agent-a")
    object.__setattr__(s, "_coordinator", coord)
    return s


def smoke() -> bool:
    owners = ["P6SD3Docked", "P6SD3Token", "P6SD3Fallback",
              "P6SD3Repl"]
    for o in owners:
        _cleanup(o)
    root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", ".."))
    try:
        # --- docked growth authors the crosses ---
        o = "P6SD3Docked"
        p = Program(owner=o)
        _seed(p)
        judge = GrowthJudge()
        s = _judge_session(p, o, judge)
        out = p.grow_ideas(1, session=s)
        docked_props = [pr for pr in p.nursery.proposals.values()
                        if pr.origin.startswith("dock:")]
        _rec("docked_growth_authors_crosses",
             out["growth_mode"] == "docked"
             and out["docked_new"] >= 2
             and len(docked_props) == out["docked_new"]
             and all(pr.detail.startswith("Authored combination")
                     for pr in docked_props)
             and all(pr.status == "pending" for pr in docked_props),
             f"mode={out['growth_mode']} docked={out['docked_new']}")
        # Affinity is only the pre-filter: the judge was called
        # exactly once per docked cross, and never for the
        # zero-affinity disjoint pair.
        disjoint = {"QuantumLatticeX", "ZebraQuiltY"}
        pair_labels = []
        units = p.cube.session.plane.units
        for dp in out["docked_pairs"]:
            pair_labels.append(
                {units[dp["a"]].label, units[dp["b"]].label})
        _rec("affinity_remains_prefilter",
             judge.calls == out["docked_new"]
             and all(not (pl & disjoint) or len(pl & disjoint) == 2
                     for pl in pair_labels)
             and all(pl != disjoint for pl in pair_labels)
             and all(dp["affinity"] >= 0.28
                     for dp in out["docked_pairs"]),
             str(pair_labels)[:160])
        # Single-parent drift stays token machinery, labeled.
        drift = [pr for pr in p.nursery.proposals.values()
                 if pr.origin == "growth:token"]
        _rec("docked_run_drift_labeled_token",
             len(drift) >= 1
             and all(pr.origin in ("growth:token", "growth:body")
                     or pr.origin.startswith("dock:")
                     for pr in p.nursery.proposals.values()
                     if pr.status == "pending"),
             f"drift={len(drift)}")
        # Evidence: the growth syntheses are in the session record.
        ev_tasks = [e["task"] for rec in p.dock_sessions.values()
                    for e in rec["proposals"]]
        _rec("evidence_for_docked_growth",
             ev_tasks.count("synthesize") == out["docked_new"],
             str(ev_tasks))
        s.undock()
        # An undocked session no longer routes: token mode.
        out2 = p.grow_ideas(1, session=s)
        _rec("undocked_session_is_token_mode",
             out2["growth_mode"] == "token"
             and out2["docked_new"] == 0)

        # --- undocked growth: token, labeled, complete ---
        o = "P6SD3Token"
        p = Program(owner=o)
        _seed(p)
        out = p.grow_ideas(1)
        pend = [pr for pr in p.nursery.proposals.values()
                if pr.status == "pending"]
        crosses = [pr for pr in pend if pr.kind == "new"]
        _rec("token_growth_labeled",
             out["growth_mode"] == "token"
             and out["proposed_new"] >= 2
             and len(crosses) >= 2
             and all(pr.origin == "growth:token" for pr in crosses)
             and all(pr.origin in ("growth:token", "growth:body")
                     for pr in pend),
             f"new={out['proposed_new']} origins="
             f"{sorted({pr.origin for pr in pend})}")

        # --- judge failure falls back per pair, labeled ---
        o = "P6SD3Fallback"
        p = Program(owner=o)
        _seed(p)
        judge = GrowthJudge(mode="garbage")
        s = _judge_session(p, o, judge)
        out = p.grow_ideas(1, session=s)
        pend_crosses = [pr for pr in p.nursery.proposals.values()
                        if pr.status == "pending" and pr.kind == "new"]
        _rec("judge_failure_falls_back_labeled",
             out["growth_mode"] == "docked"
             and out["docked_new"] == 0
             and out["token_fallback"] >= 2
             and len(pend_crosses) >= 2
             and all(pr.origin == "growth:token"
                     for pr in pend_crosses),
             f"fallback={out['token_fallback']}")
        s.undock()

        # --- REPL connect grow (CROSS_PROCESS) ---
        o = "P6SD3Repl"
        lines = []
        for label, detail, goals in FIELD[:4]:
            lines.append(f"create an idea called {label}")
            lines.append(f"set detail {label} {detail}")
            lines.append(
                f"set goals {label} {'; '.join(goals)}")
        lines += ["save", "quit"]
        r1 = subprocess.run(
            [sys.executable, "-m", "form.repl", "--owner", o],
            input="\n".join(lines) + "\n", capture_output=True,
            text=True, cwd=root, timeout=300)
        # Connect docks the default 'fake' provider lazily on grow
        # (exactly as on ask). The fake cannot answer the semantic
        # schema, so every cross falls back to labeled token growth
        # while the reported mode stays honestly "docked".
        script = "\n".join([
            "connect", "grow 1", "leave", "quit"]) + "\n"
        r2 = subprocess.run(
            [sys.executable, "-m", "form.repl", "--owner", o,
             "--load"],
            input=script, capture_output=True, text=True, cwd=root,
            timeout=300)
        _rec("repl_connect_grow_docked_fallback",
             r1.returncode == 0 and r2.returncode == 0
             and "Growth (docked):" in r2.stdout,
             (r2.stdout[-300:] if r2.returncode else r2.stderr[-200:]))
        p = persist_rest.load(o, activate=False)
        pend = [pr for pr in p.nursery.proposals.values()
                if pr.status == "pending"]
        _rec("repl_growth_proposals_labeled",
             len(pend) >= 2
             and all(pr.origin in ("growth:token", "growth:body")
                     for pr in pend),
             str(sorted({pr.origin for pr in pend})))
        conn_text = str(list(p.connection_sessions.values()))
        _rec("repl_grow_recorded_in_connection",
             "mode=docked" in conn_text and "fallback=" in conn_text,
             conn_text[:160])
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
