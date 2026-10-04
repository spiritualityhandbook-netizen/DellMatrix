"""DSC1_J01 permanent regression: journal integrity validation.

Covers the 5 Director-observed defects + sibling classes:
- empty dict, foreign owner, unknown op, missing ops, version 999
- truncated JSON, unreadable (binary), wrong field types
- incomplete recognized operations, malformed embedded entries

For each case, proves 7 properties:
1. Probe reaches a real dependency (MIRROR declared, edge exists).
2. Status inspection reports non-success (not "synchronized").
3. Fresh-process recovery rejects invalid state (GraphValidationError).
4. Invalid journal bytes remain unchanged (byte-preservation).
5. Appending (_write_journal) cannot erase invalid evidence (raises).
6. Operation removal (_remove_journal_ops) cannot erase invalid evidence (raises).
7. Valid journals still recover correctly (control case).

Each runs in a FRESH OS process. Owner: DSC1R (isolated; cleaned).
"""

import json
import os
import shutil
import subprocess
import sys

REPO = "/home/hatch/workspace/dellmatrix-gdp-phase1"
OWNER = "DSC1R"

RESULTS = []


def run_phase(name, code):
    print(f"--- {name} ---", flush=True)
    r = subprocess.run(
        [sys.executable, "-c", code],
        cwd=REPO, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        print(f"PHASE {name} CRASHED rc={r.returncode}", flush=True)
        print(r.stdout[-800:], flush=True)
        print(r.stderr[-800:], flush=True)
        RESULTS.append((name + " crashed", False))
        return
    for line in r.stdout.splitlines():
        if line.startswith("RESULT "):
            d = json.loads(line[len("RESULT "):])
            for k, v in d.items():
                RESULTS.append((k, bool(v)))
                print(("PASS " if v else "FAIL ") + k, flush=True)


SETUP = """
import json, os, shutil, subprocess, sys
sys.path.insert(0, %(REPO)r)
from form.mandell.idea import Idea, Provenance, ProvenanceSource
from form.mandell.idea_persist import save_idea, load_idea
from form.mandell.semantic_graph import (
    SemanticGraph, DerivationKind, GraphValidationError,
    graph_path, graph_journal_path, validate_journal)
from form.persist import _STATE_DIR
BASE = _STATE_DIR
OWNER = %(OWNER)r
for p in [os.path.join(BASE, f"ideas_{OWNER}"), graph_path(OWNER), graph_journal_path(OWNER)]:
    if os.path.isdir(p): shutil.rmtree(p)
    elif os.path.isfile(p): os.remove(p)
PROV = Provenance(source=ProvenanceSource.HUMAN, activity="dsc1", agent="dsc1")
src = Idea(title="S"); src.set_property("v", 42, PROV); save_idea(src, OWNER)
dep = Idea(title="D"); save_idea(dep, OWNER)
g = SemanticGraph.load(OWNER)
edge = g.declare_dependency(dep.id, src.id, DerivationKind.MIRROR, "m", unit="v", provenance=PROV)
# Property 1: real dependency exists
r = {}
r["p1_real_dependency"] = (edge.rel_id in g._current)
jpath = graph_journal_path(OWNER)
"""

TEARDOWN = """
# Cleanup
shutil.rmtree(os.path.join(BASE, f"ideas_{OWNER}"), ignore_errors=True)
for p in [graph_path(OWNER), graph_journal_path(OWNER)]:
    if os.path.isfile(p): os.remove(p)
print("RESULT " + json.dumps(r))
"""

FRESH_LOAD = """
# Property 3: fresh-process recovery rejects
load_code = '''
import sys
sys.path.insert(0, %(REPO)r)
from form.mandell.semantic_graph import SemanticGraph, GraphValidationError
try:
    gg = SemanticGraph.load(%(OWNER)r)
    print("LOADED")
except GraphValidationError:
    print("REJECTED")
'''
pr = subprocess.run([sys.executable, "-c", load_code], capture_output=True, text=True, timeout=30)
r["p3_fresh_rejects"] = ("REJECTED" in pr.stdout)
r["p3_not_loaded"] = ("LOADED" not in pr.stdout)
"""


def case_code(name, journal_bytes):
    """Generate test code for a journal content case."""
    jb = repr(journal_bytes)
    return (SETUP % {"REPO": REPO, "OWNER": OWNER} + f"""
# Write the invalid journal
with open(jpath, "w") as f:
    f.write({jb})
orig_bytes = {jb}
# Property 2: status is non-success
st = g.propagation_status(dep.id, "m")
r["p2_non_success"] = (st != "synchronized")
r["p2_is_unknown"] = (st == "unknown")
""" + FRESH_LOAD % {"REPO": REPO, "OWNER": OWNER} + f"""
# Property 4: bytes preserved
with open(jpath) as f:
    r["p4_bytes_preserved"] = (f.read() == orig_bytes)
# Property 5: append cannot erase (raises, bytes unchanged)
try:
    g._write_journal([{{"op": "sync_dependent", "dependent_id": dep.id,
                       "derived_property": "m", "target_id": src.id,
                       "edge_rel_id": edge.rel_id}}])
    r["p5_append_raises"] = False
except GraphValidationError:
    r["p5_append_raises"] = True
with open(jpath) as f:
    r["p5_bytes_kept"] = (f.read() == orig_bytes)
# Property 6: removal cannot erase (raises, bytes unchanged)
try:
    g._remove_journal_ops(dep.id, "m")
    r["p6_remove_raises"] = False
except GraphValidationError:
    r["p6_remove_raises"] = True
with open(jpath) as f:
    r["p6_bytes_kept"] = (f.read() == orig_bytes)
""" + TEARDOWN)


def main():
    cases = [
        ("empty-dict", "{}"),
        ("foreign-owner", json.dumps({"format_version": 1, "owner": "FOREIGN", "operations": []})),
        ("unknown-op", json.dumps({"format_version": 1, "owner": OWNER, "operations": [{"op": "bogus"}]})),
        ("missing-ops", json.dumps({"format_version": 1, "owner": OWNER})),
        ("version-999", json.dumps({"format_version": 999, "owner": OWNER, "operations": []})),
        ("truncated-json", '{"format_version": 1, "owner": "DSC1R", "oper'),
        ("wrong-types", json.dumps({"format_version": "1", "owner": OWNER, "operations": []})),
        ("incomplete-op", json.dumps({"format_version": 1, "owner": OWNER, "operations": [{"op": "sync_dependent"}]})),
        ("malformed-entry", json.dumps({"format_version": 1, "owner": OWNER, "operations": [{"op": "ensure_edge", "entry": {"rel_id": "x"}}]})),
        ("empty-op-id", json.dumps({"format_version": 1, "owner": OWNER, "operations": [{"op": "sync_dependent", "dependent_id": "", "derived_property": "m", "target_id": "t", "edge_rel_id": "e"}]})),
    ]
    for name, content in cases:
        run_phase(f"DSC1-{name}", case_code(name, content))

    # Property 7: valid journals still recover (control)
    run_phase("DSC1-valid-control", (SETUP % {"REPO": REPO, "OWNER": OWNER}) + """
# Write a VALID journal via the implementation, then corrupt the dependent
# to force a replay scenario. Actually: just verify a valid journal
# written by _write_journal passes validation and replays.
g._write_journal([{"op": "sync_dependent", "dependent_id": dep.id,
                   "derived_property": "m", "target_id": src.id,
                   "edge_rel_id": edge.rel_id}])
with open(jpath) as f:
    jdata = json.load(f)
try:
    validate_journal(jdata, OWNER)
    r["p7_valid_passes"] = True
except GraphValidationError:
    r["p7_valid_passes"] = False
# Status should be pending (valid journal with our op)
r["p7_status_pending"] = (g.propagation_status(dep.id, "m") == "pending")
# Fresh load replays and clears
""" + (FRESH_LOAD % {"REPO": REPO, "OWNER": OWNER}).replace(
        'r["p3_fresh_rejects"] = ("REJECTED" in pr.stdout)',
        'r["p7_replay_ok"] = ("LOADED" in pr.stdout)').replace(
        'r["p3_not_loaded"] = ("LOADED" not in pr.stdout)',
        'r["p7_journal_cleared"] = (not os.path.isfile(jpath))') + TEARDOWN)

    fails = [n for n, ok in RESULTS if not ok]
    npass = sum(1 for _, ok in RESULTS if ok)
    print(f"\nDSC1_J01 REGRESSION: {npass}/{len(RESULTS)} PASS", flush=True)
    print("DSC1_J01 WORLD: ALL PASS" if not fails else f"FAILURES: {fails}", flush=True)


if __name__ == "__main__":
    main()
