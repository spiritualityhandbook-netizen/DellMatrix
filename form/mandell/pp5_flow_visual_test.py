#!/usr/bin/env python3
"""PP5 / D3 — flow visuals: canonical executions rendered as a
trace and as preform-shaped animation frames.

The contract under test (Director completion order, PP5):

- rendering consumes the canonical execution record only —
  order, skip, failure and completion appear exactly as the
  executor reported them (no second executor, no invented
  outcomes);
- established text semantics are preserved: atom texts are
  the seed's own NN[Term] identities and operators are shown
  exactly as written;
- frames follow the preform Anim shape ({id, fps, frames,
  loop}) with one step frame per atom in execution order;
- when results cannot be aligned with the seed's atoms, the
  renderer says so (aligned=False) instead of decorating;
- the REPL `flow` command draws the last execution of the
  session on the real user path.

Stdlib only. Run: python3 -m form.mandell.pp5_flow_visual_test
"""
from __future__ import annotations

import glob
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from form.open import Program  # noqa: E402
from form.mandell.executor import execute_seed  # noqa: E402
from form.mandell.flow_visual import render_anim, render_trace  # noqa: E402

RESULTS = []


def _rec(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))


def _cleanup(owner):
    base = os.path.join(os.path.dirname(__file__), "..", "state")
    for pat in (f"program_{owner}.json", f"nursery_{owner}.json",
                f"checkpoint_{owner}_*", f"confirm_{owner}.journal.json",
                f"checkpoint_{owner}.journal.json", f"gen_{owner}_*",
                f"current_{owner}.json"):
        for f in glob.glob(os.path.join(base, pat)):
            try:
                os.remove(f)
            except FileNotFoundError:
                pass
            except OSError:
                raise
    for d in glob.glob(os.path.join(base, f"ideas_{owner}*")):
        if os.path.isdir(d):
            shutil.rmtree(d)


def _check_rendering():
    owner = "PP5Vis"
    _cleanup(owner)
    try:
        p = Program(owner)
        # A complete chain: Nova executes, Keep (save) executes.
        r = execute_seed(p, "00[Nova] > 10[Keep]")
        results = r.get("atom_results") or []
        trace = render_trace("00[Nova] > 10[Keep]", results)
        joined = "\n".join(trace)
        _rec("trace renders a complete chain faithfully",
             r.get("ok") and len(results) == 2
             and "00[Nova] ✓ executed" in joined
             and "10[Keep] ✓ executed" in joined
             and "> 10[Keep]" in joined
             and "complete — 2 executed, 0 skipped, 0 failed" in joined,
             joined.replace("\n", " | ")[:220])
        anim = render_anim("00[Nova] > 10[Keep]", results)
        _rec("anim has the preform shape and one frame per atom",
             anim["aligned"] is True and anim["loop"] is False
             and anim["fps"] == 2 and len(anim["frames"]) == 4
             and "chain ready" in anim["frames"][0]
             and "▸00[Nova]◂" in anim["frames"][1]
             and "▸10[Keep]◂" in anim["frames"][2]
             and "complete" in anim["frames"][3],
             str({k: anim[k] for k in ("aligned", "fps", "loop")}))
        _rec("execution records last_flow on the program",
             isinstance(getattr(p, "last_flow", None), dict)
             and p.last_flow["seed_text"] == "00[Nova] > 10[Keep]"
             and len(p.last_flow["atom_results"]) == 2)

        # A chain with a failure and a skip: Dell 86[Old] resolves
        # to Delete and fails (nothing named Old exists), and
        # FlowThru then skips Dell 10 unexecuted. The renderer
        # must show exactly that — the failure with its reported
        # reason, then the skip with its FlowThru reason.
        r2 = execute_seed(p, "86[Old] >> 10[Keep]")
        res2 = r2.get("atom_results") or []
        statuses = [(x.get("dell"), bool(x.get("skipped")),
                     bool(x.get("ok"))) for x in res2]
        trace2 = "\n".join(render_trace("86[Old] >> 10[Keep]", res2))
        _rec("trace renders failure + skip with reported reasons",
             statuses == [(86, False, False), (10, True, False)]
             and "86[Delete] ✗ failed" in trace2
             and "delete_missing:Old" in trace2
             and "10[Keep] ⊘ skipped" in trace2
             and "FlowThru" in trace2
             and "0 executed, 1 skipped, 1 failed" in trace2,
             trace2.replace("\n", " | ")[:240])
        anim2 = render_anim("86[Old] >> 10[Keep]", res2)
        _rec("anim frames carry failure + skip in order",
             anim2["aligned"] is True and len(anim2["frames"]) == 4
             and "✗ failed" in anim2["frames"][1]
             and "⊘ skipped" in anim2["frames"][2]
             and anim2["frames"][3].splitlines()[-1].startswith("■ failed"),
             anim2["frames"][1].replace("\n", " | ")[:120])

        # Unaligned input is reported, never decorated.
        anim3 = render_anim("00[Nova] > 10[Keep]",
                            [{"dell": 42, "ok": True}])
        _rec("unaligned results are reported, not decorated",
             anim3["aligned"] is False
             and any("unaligned" in f for f in anim3["frames"])
             and not any("▸" in f for f in anim3["frames"]))
        anim4 = render_anim("gibberish, not a seed", [])
        _rec("no execution renders an honest empty frame",
             anim4["frames"] and "no execution recorded"
             in anim4["frames"][0])
    finally:
        _cleanup(owner)


def _check_repl_path():
    owner = "PP5Repl"
    _cleanup(owner)
    try:
        root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", ".."))
        lines = ["flow", "86[Old] >> 10[Keep]", "flow", "quit"]
        proc = subprocess.run(
            [sys.executable, "-m", "form.repl", "--owner", owner],
            input="\n".join(lines) + "\n", capture_output=True,
            text=True, cwd=root, timeout=300)
        out = proc.stdout
        _rec("REPL flow: honest before, rendered after a chain",
             proc.returncode == 0
             and "no chain has executed" in out
             and "10[Keep] ⊘ skipped" in out
             and "[frame 1]" in out
             and "▸86[Delete]◂" in out,
             out[-400:].replace("\n", " | "))
    finally:
        _cleanup(owner)


def main():
    try:
        _check_rendering()
        _check_repl_path()
    except Exception as exc:  # a crashing suite is a failing suite
        import traceback
        traceback.print_exc()
        _rec("suite_completed_without_crash", False, repr(exc))
    ok = sum(1 for _, c, _ in RESULTS if c)
    for name, cond, detail in RESULTS:
        line = ("PASS " if cond else "FAIL ") + name
        if not cond and detail:
            line += " :: " + detail
        print(line)
    print(f"PP5_FLOW_VISUAL: {ok}/{len(RESULTS)}")
    return ok == len(RESULTS) and bool(RESULTS)


def smoke():
    return main()


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
