#!/usr/bin/env python3
"""Q5 — Other public entry paths that can carry typed arguments.

(a) REPL literal path: REAL_USER_PATH subprocess probe
    (python3 -m form.repl), proving the same silent drop through
    the user's own interface, plus an in-REPL witness: after a
    typed 82[Group](name="greens"), Scope to 'greens' must REFUSE
    (the group was never made) while Scope to 'group' succeeds
    (the default-named group the call actually created).
(b) flow_executor program path: parse-level classification —
    its FlowNode.args are DERIVED FROM THE LABEL by a fixed
    per-action table, not read from SeedAtom.args.
(c) Studio /api/execute: equivalence by code citation
    (gui/server.py imports and calls the same execute_seed);
    not re-probed (the GUI API suite covers that surface).
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_lib import ROOT, cleanup, state_listing, verdict

results = []

# --- (b) flow_executor parse-level ---------------------------------
from form.mandell.flow_executor import parse_program

raised = None
try:
    fp = parse_program('55[Set](key="a", value="b")')
    node = fp.nodes[0] if fp.nodes else None
    print(f"flow parse 55[Set](key=a, value=b) -> node.args="
          f"{node.args if node else None}")
except ValueError as exc:
    raised = str(exc)
    print(f"flow parse 55[Set](key=a, value=b) -> ValueError: {raised}")
results.append(verdict("Q5-flow-args-channel",
                       raised is not None and "expected flow" in raised,
                       "SeedAtom-style typed args in flow-program text are "
                       "NOT silently dropped: _tokenize_program refuses "
                       "the text outright (ValueError 'expected flow') — "
                       "an unstructured exception, not a receipt"))

fp2 = parse_program("34[Stamp] :: hello")
node2 = fp2.nodes[0] if fp2.nodes else None
print(f"flow parse 34[Stamp] :: hello -> node.args={node2.args if node2 else None}")
results.append(verdict("Q5-flow-label-derived",
                       node2 is not None and node2.args == {"mark": "hello"},
                       "the flow path's 'args' are synthesized FROM the "
                       "label by _args_from_label (stamp/cycle/form only) — "
                       "a different mechanism, not a drop"))

# --- (a) REPL subprocess --------------------------------------------
before = state_listing()
owner = "ArgHonRepl"
script = "\n".join([
    "08[Create] :: Garden Gate",
    "08[Create] :: River Stone",
    "51[Select]",
    '82[Group](name="greens")',
    "53[Scope] :: greens",
    "53[Scope] :: group",
    "",
])
try:
    proc = subprocess.run(
        [sys.executable, "-m", "form.repl", "--owner", owner],
        input=script, capture_output=True, text=True,
        cwd=ROOT, timeout=120)
    out = proc.stdout + proc.stderr
    print("--- REPL transcript (filtered) ---")
    for line in out.splitlines():
        if any(k in line for k in ("Group", "Scope", "82[", "53[", "group")):
            print(f"  {line}")
    print("--- end transcript ---")
    scope_greens_refused = "scope_unknown:greens" in out or (
        "Scope refused" in out and "greens" in out)
    group_made = "Group group" in out
    scope_group_ok = "Scope -> group" in out
    results.append(verdict("Q5-repl-same-drop",
                           group_made and scope_greens_refused and scope_group_ok,
                           "REPL (real user path): typed Group(name=greens) "
                           "created the DEFAULT 'group'; Scope :: greens "
                           "refused as unknown, Scope :: group succeeded — "
                           "the identical silent drop, witnessed inside the "
                           "user's own interface"))
finally:
    removed = cleanup(owner, before)
    print(f"  (cleanup {owner}: {len(removed)} entries removed)")

print(f"\nQ5 SUMMARY: {sum(results)}/{len(results)} expectations confirmed")
sys.exit(0 if all(results) else 1)
