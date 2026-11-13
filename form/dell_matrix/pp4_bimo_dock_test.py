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
        # LM-4 re-pin (2026-11-13): the pair keeps ONE shared small
        # explicit bound and its exact original meanings. Measured
        # through the real code path, "short prompt" assembles to
        # 382 chars unworn and 680 worn (scout framing = 298), so
        # the shared bound moves 200 -> 500: 382 <= 500 < 680. The
        # decomposition now rides every propose (it is part of the
        # outbound text the bound governs), which is what made the
        # old 200 refuse the unworn case.
        s = dock(p, "guest:bound", bimo="scout", max_prompt_chars=500)
        out = s.propose("short prompt")
        _rec("framing counts toward the prompt bound",
             out.get("ok") is False
             and out.get("reason") == "prompt_too_large"
             and s._provider.last_prompt is None,
             f"out={out}")
        s.undock()
        s2 = dock(p, "guest:plain", max_prompt_chars=500)
        out2 = s2.propose("short prompt")
        _rec("the same bound passes unworn",
             out2.get("ok") is True, f"out={out2}")
        s2.undock()
        # Ace Elastic Limits Doctrine (2026-11-13): the DEFAULT
        # bound must never hinder the program's own legitimate
        # work. The LM-4 decomposition expands dense prose ~10x —
        # this natural 6,300-char prompt assembles to 70,445 chars
        # outbound (measured through the real code path; LM-4 limit
        # grounding) and was REFUSED at the old 8000 default.
        s3 = dock(p, "guest:elastic")
        big = ("the harbor lantern keeper watches the tide and "
               "records every returning boat in the ledger ") * 70
        out3 = s3.propose(big)
        _rec("elastic default admits a large legitimate decomposed "
             "propose",
             out3.get("ok") is True
             and len(s3._provider.last_prompt or "") > 8000,
             f"out={out3}")
        s3.undock()
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


_G2_SENT = ("the harbor lantern keeper watches the tide and "
            "records every returning boat in the ledger ")


def _check_gate2():
    """Director gate (mail 1a1d6d1d64b72589, 2026-11-13 15:30 CST)
    on the elastic ceiling at head c27ee89: A1 the prompt-size
    guard fires BEFORE any provider call at every assembly
    checkpoint; A2 explicit caller bounds still refuse (the 1M
    default did not weaken caller sovereignty); A3 the protected
    screen judges the FINAL assembled payload, never a
    pre-assembly version; A4 assembly cost is linear in token
    count at fixed word shape, the worst admitted assembly is
    bounded in size and memory, and its refusal costs seconds,
    not minutes; A5 the program's own verb path on a 100-unit
    field is admitted at the default bound it was refused at
    under the old 8000 ceiling."""
    import time
    import tracemalloc
    from form.dell_matrix import inference_dock as idock
    from form.open import open_program

    # ---- A1: four distinct bound checkpoints, zero provider
    # calls at each; the refusal detail names the checkpoint.
    owner = "PP4G2A1"
    _cleanup(owner)
    try:
        p = Program(owner)
        _commit(p)
        s = dock(p, "guest:g2", max_prompt_chars=10)
        out = s.propose("x" * 50)
        _rec("A1 raw-prompt checkpoint refuses before provider call",
             out.get("reason") == "prompt_too_large"
             and "Prompt exceeds 10 chars" in (out.get("detail") or "")
             and s._provider.calls == 0, f"out={out}")
        s.undock()
        s = dock(p, "guest:g2", max_prompt_chars=200)
        out = s.propose("short prompt")
        _rec("A1 decomposition checkpoint refuses before provider "
             "call",
             out.get("reason") == "prompt_too_large"
             and "decomposition" in (out.get("detail") or "")
             and s._provider.calls == 0, f"out={out}")
        s.undock()
        s = dock(p, "guest:g2", max_prompt_chars=500)
        out = s.propose("short prompt", context={"note": "y" * 400})
        _rec("A1 context checkpoint refuses before provider call",
             out.get("reason") == "prompt_too_large"
             and "Prompt+context" in (out.get("detail") or "")
             and s._provider.calls == 0, f"out={out}")
        s.undock()
        s = dock(p, "guest:g2", bimo="scout", max_prompt_chars=500)
        out = s.propose("short prompt")
        _rec("A1 framing checkpoint refuses before provider call",
             out.get("reason") == "prompt_too_large"
             and "Prompt+framing" in (out.get("detail") or "")
             and s._provider.calls == 0, f"out={out}")
        s.undock()
    finally:
        _cleanup(owner)

    # ---- A2: caller sovereignty at an explicit bound of 1000.
    owner = "PP4G2A2"
    _cleanup(owner)
    try:
        p = Program(owner)
        s0 = dock(p, "guest:g2")
        out0 = s0.propose(_G2_SENT * 3)
        asm = len(s0._provider.last_prompt or "")
        s0.undock()
        s = dock(p, "guest:g2", max_prompt_chars=1000)
        out = s.propose(_G2_SENT * 3)
        _rec("A2 explicit bound 1000 still refuses a decomposed "
             "propose",
             out0.get("ok") is True and asm > 1000
             and out.get("reason") == "prompt_too_large"
             and s._provider.calls == 0,
             f"asm={asm} out={out}")
        out2 = s.propose("short prompt")
        _rec("A2 the same explicit bound admits what fits it",
             out2.get("ok") is True and s._provider.calls == 1,
             f"out={out2}")
        s.undock()
    finally:
        _cleanup(owner)

    # ---- A3: the screen judges the assembled payload.
    owner = "PP4G2A3"
    _cleanup(owner)
    try:
        p = Program(owner)
        handle = "grant_" + "cd" * 16
        s = dock(p, "guest:g2")
        out = s.propose("draft", context={"note": handle})
        _rec("A3 context-borne handle refused at the default bound",
             out.get("reason") == "protected_input"
             and s._provider.calls == 0
             and s._provider.last_prompt is None, f"out={out}")
        s.undock()
        # Canary discipline (r62 D7 family): neutralize ONLY the
        # structured pre-serialization screen; the assembled-text
        # screen alone must still refuse the handle riding in the
        # final payload's [context] block.
        real = idock._screen_decoded_values
        idock._screen_decoded_values = lambda obj, prot: False
        try:
            s = dock(p, "guest:g2")
            out = s.propose("draft", context={"note": handle})
            _rec("A3 assembled-text screen alone refuses the "
                 "context handle",
                 out.get("reason") == "protected_input"
                 and s._provider.calls == 0, f"out={out}")
            s.undock()
        finally:
            idock._screen_decoded_values = real
        raw = "draft about \\u0067rant_" + "cd" * 16
        s = dock(p, "guest:g2")
        out = s.propose(raw)
        _rec("A3 escaped handle exists only in the decoded "
             "assembled view and is refused",
             "grant_" not in raw
             and out.get("reason") == "protected_input"
             and s._provider.calls == 0, f"out={out}")
        s.undock()
    finally:
        _cleanup(owner)

    # ---- A4: assembly cost. Measured at c27ee89 (this VM):
    # decomposition time per token is CONSTANT as token count
    # scales (0.498/0.447/0.393 ms at 700/1400/2800 tokens) and
    # FALLS with word length (per-token 0.51/0.51/0.54/1.4 ms at
    # lengths 7/70/700/7000); a 70,001-char single token composes
    # in ~2 ms. Expansion tops out at 18.84x (short-token prose);
    # the worst assembly the 100,000-char context ceiling can
    # drive is ~1.9M chars.
    owner = "PP4G2A4"
    _cleanup(owner)
    try:
        p = Program(owner)

        def _tmin(fn, reps=3):
            best = None
            for _ in range(reps):
                t0 = time.perf_counter()
                fn()
                dt = time.perf_counter() - t0
                best = dt if best is None else min(best, dt)
            return best

        idock._lm4_text_block("warm the lantern keeper now")
        t1 = _tmin(lambda: idock._lm4_text_block("lantern " * 700))
        t2 = _tmin(lambda: idock._lm4_text_block("lantern " * 2800))
        _rec("A4 decomposition cost is linear in token count",
             t2 < 6.0 * t1,
             f"t700={t1:.3f}s t2800={t2:.3f}s ratio={t2 / t1:.2f} "
             "(4x tokens; linear ~= 4, quadratic ~= 16)")
        # Worst admitted assembly: expansion-maximal prose at the
        # validate_context ceiling (100,000 chars).
        worst = ("a b c " * 16667)[:100000]
        s = dock(p, "guest:g2")
        t0 = time.perf_counter()
        out = s.propose(worst)
        dt = time.perf_counter() - t0
        _rec("A4 worst admitted assembly is bounded and refused "
             "fast",
             len(worst) == 100000
             and out.get("reason") == "prompt_too_large"
             and s._provider.calls == 0 and dt < 45.0,
             f"dt={dt:.1f}s out={out.get('reason')}")
        s.undock()
        # The gate-2 finding: a 214,200-char raw prompt (PAST the
        # context ceiling) is decomposed in full (~2.2M chars)
        # BEFORE the assembled-length guard can fire -- measured
        # 23.1 s / 98.9 MB peak at c27ee89. The guard still fires
        # before any provider call; the exposure window is host
        # CPU/memory only, bounded by the caller's own input.
        big = _G2_SENT * 2380
        s = dock(p, "guest:g2")
        tracemalloc.start()
        t0 = time.perf_counter()
        out = s.propose(big)
        dt = time.perf_counter() - t0
        _cur, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        _rec("A4 oversize raw refuses pre-provider, bounded cost "
             "(disclosed exposure)",
             out.get("reason") == "prompt_too_large"
             and "decomposition" in (out.get("detail") or "")
             and s._provider.calls == 0 and dt < 60.0
             and peak < 400 * 1000 * 1000,
             f"dt={dt:.1f}s peakMB={peak / 1e6:.1f} out={out}")
        s.undock()
    finally:
        _cleanup(owner)

    # ---- A5: the program's own verbs at field scale.
    for bound, tag in ((None, "default"), (8000, "the old 8000")):
        owner = "PP4G2A5" + ("Def" if bound is None else "Old")
        _cleanup(owner)
        try:
            p = open_program(owner)
            for i in range(100):
                p.place(f"u{i:03d}", f"harbor lantern unit {i}",
                        words=("the keeper tends the lantern and "
                               "watches the returning boats each "
                               "evening tide ") * 2,
                        x=float(i), y=0.0)
            kw = ({} if bound is None
                  else {"max_prompt_chars": bound})
            s = dock(p, "guest:g2", **kw)
            for name, fn in (
                    ("relate_field", lambda: s.relate_field("u000")),
                    ("flag", lambda: s.flag(
                        "u002", concern="check the lantern stores")),
                    ("synthesize", lambda: s.synthesize(
                        ["u000", "u001", "u002", "u003"]))):
                before = s._provider.calls
                r = fn()
                plen = len(s._provider.last_prompt or "")
                if bound is None:
                    _rec(f"A5 {name} admitted at the default bound "
                         f"({tag})",
                         r.get("reason") != "prompt_too_large"
                         and s._provider.calls > before and plen > 8000,
                         f"reason={r.get('reason')} len={plen}")
                else:
                    _rec(f"A5 {name} refused at {tag} (control)",
                         r.get("reason") == "prompt_too_large"
                         and s._provider.calls == before,
                         f"reason={r.get('reason')}")
            s.undock()
        finally:
            _cleanup(owner)


def main():
    _check_unworn_baseline()
    _check_worn_session()
    _check_refusals()
    _check_framing_bound()
    _check_gate2()
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
