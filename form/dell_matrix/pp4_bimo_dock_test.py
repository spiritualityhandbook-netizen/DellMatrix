"""PP4 — D2: a committed Bimo configuration binds to the docked
session (Director completion order, PP4 authorized).

Contract pinned here:
- dock(bimo=<name>) resolves the configuration from the
  COMMITTED Forge store (program.bimo_configurations) and
  refuses — DockError, before any session/evidence/snap exists —
  when the name is unknown, only staged, or the stored record
  fails its closed schema (slots/pilot only, no grant fields).
- A worn session carries the configuration's identity in its
  evidence record (bimo == name, surviving save/reload) and its
  personas OBSERVABLY frame every prompt: propose and the
  semantic verbs both reach the provider with the [bimo: name]
  block (pilot + filled slots, focus and limits) prepended, and
  the framing counts toward the prompt bound.
- Personas describe, never grant: a worn session's proposal
  still lands PENDING and a machine confirm is still denied by
  AcceptancePolicy; the human gate still works.
- Unworn docks are unchanged (no framing, bimo == "").
"""
from __future__ import annotations

import glob
import os
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from form.open import Program  # noqa: E402
from form import persist_rest  # noqa: E402
from form.dell_matrix import bimo_forge  # noqa: E402
from form.dell_matrix.inference_dock import DockError, dock  # noqa: E402

RESULTS = []


def _rec(name, cond, detail=""):
    RESULTS.append((name, bool(cond), str(detail)[:220]))


def _cleanup(owner):
    base = os.path.join(os.path.dirname(__file__), "..", "state")
    for pat in (f"program_{owner}.json", f"nursery_{owner}.json",
                f"checkpoint_{owner}_*", f"confirm_{owner}.journal.json",
                f"checkpoint_{owner}.journal.json",
                f"gen_{owner}_*", f"current_{owner}.json"):
        for f in glob.glob(os.path.join(base, pat)):
            try:
                os.remove(f)
            except FileNotFoundError:
                pass
    for d in glob.glob(os.path.join(base, f"ideas_{owner}*")):
        if os.path.isdir(d):
            shutil.rmtree(d)


def _commit(p, name="scout"):
    cfg = bimo_forge.make_configuration(
        name, p.owner,
        {"logic": "manny", "growth": "melody"}, "della")
    configs = getattr(p, "bimo_configurations", None)
    if not isinstance(configs, dict):
        configs = {}
        p.bimo_configurations = configs
    configs[name] = cfg
    return cfg


def _check_unworn_baseline():
    owner = "PP4Base"
    _cleanup(owner)
    try:
        p = Program(owner)
        s = dock(p, "guest:base")
        out = s.propose("propose a trial idea about tides")
        prompt = s._provider.last_prompt or ""
        _rec("unworn dock: no bimo identity, no framing",
             s.bimo == "" and s._evidence.get("bimo") == ""
             and out.get("ok") and "[bimo:" not in prompt,
             f"bimo={s.bimo!r} ok={out.get('ok')}")
        s.undock()
    finally:
        _cleanup(owner)


def _check_worn_session():
    owner = "PP4Worn"
    _cleanup(owner)
    try:
        p = Program(owner)
        _commit(p)
        s = dock(p, "guest:worn", bimo="scout")
        _rec("worn session carries the configuration identity",
             s.bimo == "scout" and s._evidence.get("bimo") == "scout"
             and s.bimo_config["pilot"] == "della",
             f"bimo={s.bimo!r} rec={s._evidence.get('bimo')!r}")
        out = s.propose("propose a trial idea about tides")
        prompt = s._provider.last_prompt or ""
        _rec("propose prompt is framed by the worn configuration",
             out.get("ok") and prompt.startswith("[bimo: scout]")
             and "Della" in prompt and "Manny" in prompt
             and "limits" in prompt,
             f"head={prompt[:60]!r}")
        pid = out["pid"]
        prop = p.nursery.proposals[pid]
        _rec("worn proposal still lands PENDING",
             prop.status == "pending", f"status={prop.status}")
        denied = p.confirm_proposal(pid, _producer="inference_dock")
        _rec("wearing grants nothing: machine confirm still denied",
             denied.get("ok") is False
             and denied.get("reason") == "acceptance_policy_denied",
             f"res={denied}")
        ctx = p.make_review_context(pid, reviewer="human:ace")
        human = p.confirm_proposal(pid, _producer="pp4test",
                                   _review_context=ctx)
        _rec("the human gate still acts on a worn proposal",
             human.get("ok") is True, f"res={human}")
        a = p.nursery.add("Tide Chart", words="chart of tides",
                          origin=f"host:{owner}")
        b = p.nursery.add("Moon Phase", words="phase of the moon",
                          origin=f"host:{owner}")
        # The contract under test is the PROMPT the provider
        # receives. (The fake provider's verb output then fails
        # the semantic schema by design — p5_sd2 pins that same
        # behavior — so the verb's own ok is not asserted here.)
        s.relate(a.id, b.id)
        vprompt = s._provider.last_prompt or ""
        _rec("verb prompts are framed too",
             vprompt.startswith("[bimo: scout]")
             and "[targets]" in vprompt,
             f"head={vprompt[:40]!r}")
        s.undock()
        p.save()
        p2 = persist_rest.load(owner, activate=False)
        restored = [r for r in (p2.dock_sessions or {}).values()
                    if r.get("bimo") == "scout"]
        _rec("the worn identity survives save/reload as evidence",
             len(restored) == 1, f"restored={len(restored)}")
        s2 = dock(p2, "guest:again", bimo="scout")
        out2 = s2.propose("propose another trial idea")
        _rec("a reloaded program can wear the configuration again",
             out2.get("ok")
             and (s2._provider.last_prompt or "").startswith(
                 "[bimo: scout]"),
             f"ok={out2.get('ok')}")
        s2.undock()
    finally:
        _cleanup(owner)


def _check_refusals():
    owner = "PP4Refuse"
    _cleanup(owner)
    try:
        p = Program(owner)
        _commit(p)
        before = len(getattr(p, "dock_sessions", None) or {})

        def _refused(name):
            try:
                dock(p, "guest:x", bimo=name)
                return False
            except DockError:
                return True

        _rec("unknown configuration refuses the dock",
             _refused("ghost")
             and len(getattr(p, "dock_sessions", None) or {}) == before)
        # A staged Forge arrangement is not a configuration.
        fs = bimo_forge.ForgeSession.open(owner, {}, "della")
        body = fs.staged_body()
        fs.adopt(body)
        _rec("staged-only arrangement cannot be worn",
             "stagedname" not in (getattr(p, "bimo_configurations", None)
                                  or {})
             and _refused("stagedname")
             and len(getattr(p, "dock_sessions", None) or {}) == before)
        tampered = dict(p.bimo_configurations["scout"])
        tampered["grants"] = ["confirm"]
        p.bimo_configurations["tampered"] = tampered
        _rec("a record with grant fields fails the closed schema",
             _refused("tampered")
             and len(getattr(p, "dock_sessions", None) or {}) == before)
        _rec("a non-canonical name refuses the dock",
             _refused("Not A Name!")
             and len(getattr(p, "dock_sessions", None) or {}) == before)
    finally:
        _cleanup(owner)


def _check_framing_bound():
    owner = "PP4Bound"
    _cleanup(owner)
    try:
        p = Program(owner)
        _commit(p)
        s = dock(p, "guest:bound", bimo="scout", max_prompt_chars=200)
        out = s.propose("short prompt")
        _rec("framing counts toward the prompt bound",
             out.get("ok") is False
             and out.get("reason") == "prompt_too_large"
             and s._provider.last_prompt is None,
             f"out={out}")
        s.undock()
        s2 = dock(p, "guest:plain", max_prompt_chars=200)
        out2 = s2.propose("short prompt")
        _rec("the same bound passes unworn",
             out2.get("ok") is True, f"out={out2}")
        s2.undock()
    finally:
        _cleanup(owner)


def _check_repl_path():
    """REAL_USER_PATH: the REPL connect session can select the
    configuration ('bimo scout') and the ask that follows docks
    worn — the saved evidence record carries the identity."""
    import subprocess
    owner = "PP4Repl"
    _cleanup(owner)
    try:
        p = Program(owner)
        _commit(p)
        p.save()
        root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", ".."))
        lines = ["connect", "bimo scout",
                 "ask propose a trial idea about tides",
                 "leave", "quit"]
        proc = subprocess.run(
            [sys.executable, "-m", "form.repl", "--owner", owner,
             "--load"],
            input="\n".join(lines) + "\n", capture_output=True,
            text=True, cwd=root, timeout=300)
        p2 = persist_rest.load(owner, activate=False)
        worn = [r for r in (p2.dock_sessions or {}).values()
                if r.get("bimo") == "scout"]
        pend = [pr for pr in p2.nursery.proposals.values()
                if pr.status == "pending"]
        _rec("REPL: 'bimo scout' + ask docks worn on the real path",
             proc.returncode == 0 and len(worn) == 1 and len(pend) >= 1,
             f"rc={proc.returncode} worn={len(worn)} "
             f"pending={len(pend)}")
    finally:
        _cleanup(owner)


def main():
    _check_unworn_baseline()
    _check_worn_session()
    _check_refusals()
    _check_framing_bound()
    _check_repl_path()
    ok = sum(1 for _, c, _ in RESULTS if c)
    for name, cond, detail in RESULTS:
        print(f"{'PASS' if cond else 'FAIL'} {name}"
              + (f" :: {detail}" if not cond else ""))
    print(f"PP4_BIMO_DOCK: {ok}/{len(RESULTS)}")
    return ok == len(RESULTS)


def smoke() -> bool:
    return main()


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
