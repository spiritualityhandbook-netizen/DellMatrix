"""DSC1_J01 permanent regression: journal integrity validation.

R1 findings covered:
- F1: complete embedded entry validation (via RelationshipEntry.from_dict)
- F2: outgoing journal validation (assembled journal before write)
- F3: strict version types (bool/float/str rejected)

Portable: derives REPO from __file__. Enforced: smoke() -> bool,
sys.exit(0/1), registered in form.regress.

Each case proves (fresh OS process, isolated owner):
1. Real dependency exists
2. Status is non-success (never "synchronized")
3. Fresh-process recovery rejects
4. Bytes preserved
5. Append cannot erase (raises)
6. Removal cannot erase (raises)
7. Valid control: stale -> correct value, journal cleared
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

# Portable: derive repo root from this file's location.
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OWNER = "DSC1R2"  # Isolated namespace (v2 for R1 findings)


def _phase(name: str, code: str) -> dict:
    """Run one phase in a fresh process. Returns {check_name: bool}."""
    r = subprocess.run(
        [sys.executable, "-c", code],
        cwd=REPO, capture_output=True, text=True, timeout=120)
    results = {}
    if r.returncode != 0:
        # Crashed subprocess = failed evidence.
        results[f"{name}::crashed"] = False
        return results
    for line in r.stdout.splitlines():
        if line.startswith("RESULT "):
            try:
                d = json.loads(line[len("RESULT "):])
                for k, v in d.items():
                    results[f"{name}::{k}"] = bool(v)
            except json.JSONDecodeError:
                results[f"{name}::bad_json"] = False
    if not results:
        # Empty evidence = failure.
        results[f"{name}::empty_evidence"] = False
    return results


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
r = {}
r["p1_real_dependency"] = (edge.rel_id in g._current)
jpath = graph_journal_path(OWNER)
"""

TEARDOWN = """
shutil.rmtree(os.path.join(BASE, f"ideas_{OWNER}"), ignore_errors=True)
for p in [graph_path(OWNER), graph_journal_path(OWNER)]:
    if os.path.isfile(p): os.remove(p)
print("RESULT " + json.dumps(r))
"""

FRESH_LOAD = """
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


def _invalid_case(name: str, journal_bytes: str) -> tuple[str, str]:
    """Generate (name, code) for an invalid journal case."""
    jb = repr(journal_bytes)
    code = (SETUP % {"REPO": REPO, "OWNER": OWNER} + f"""
with open(jpath, "w") as f:
    f.write({jb})
orig_bytes = {jb}
st = g.propagation_status(dep.id, "m")
r["p2_non_success"] = (st != "synchronized")
r["p2_is_unknown"] = (st == "unknown")
""" + FRESH_LOAD % {"REPO": REPO, "OWNER": OWNER} + f"""
with open(jpath) as f:
    r["p4_bytes_preserved"] = (f.read() == orig_bytes)
try:
    g._write_journal([{{"op": "sync_dependent", "dependent_id": dep.id,
                       "derived_property": "m", "target_id": src.id,
                       "edge_rel_id": edge.rel_id}}])
    r["p5_append_raises"] = False
except GraphValidationError:
    r["p5_append_raises"] = True
with open(jpath) as f:
    r["p5_bytes_kept"] = (f.read() == orig_bytes)
try:
    g._remove_journal_ops(dep.id, "m")
    r["p6_remove_raises"] = False
except GraphValidationError:
    r["p6_remove_raises"] = True
with open(jpath) as f:
    r["p6_bytes_kept"] = (f.read() == orig_bytes)
""" + TEARDOWN)
    return (name, code)


def _outgoing_case() -> tuple[str, str]:
    """F2: invalid NEW operations must not be written."""
    code = (SETUP % {"REPO": REPO, "OWNER": OWNER} + """
# F2: try to write an invalid new operation (bad ensure_edge entry).
# Must raise; existing journal (if any) preserved, no new journal created.
bad_op = {"op": "ensure_edge", "entry": {"rel_id": "BAD", "seq": 999}}
existed_before = os.path.isfile(jpath)
try:
    g._write_journal([bad_op])
    r["f2_raises"] = False
except GraphValidationError:
    r["f2_raises"] = True
# If no journal existed before, none should exist now.
# If one existed, it must be unchanged (but setup creates none).
r["f2_no_journal_created"] = (os.path.isfile(jpath) == existed_before)
# F2b: invalid op appended to EXISTING valid journal must preserve it.
g._write_journal([{"op": "sync_dependent", "dependent_id": dep.id,
                   "derived_property": "m", "target_id": src.id,
                   "edge_rel_id": edge.rel_id}])
with open(jpath) as f:
    valid_bytes = f.read()
try:
    g._write_journal([bad_op])
    r["f2b_raises"] = False
except GraphValidationError:
    r["f2b_raises"] = True
with open(jpath) as f:
    r["f2b_preserved"] = (f.read() == valid_bytes)
""" + TEARDOWN)
    return ("f2-outgoing", code)


def _valid_control() -> tuple[str, str]:
    """Valid control: stale dependent -> correct value, journal cleared."""
    code = (SETUP % {"REPO": REPO, "OWNER": OWNER} + """
# Make the dependent stale: change source, write journal for propagation.
src.set_property("v", 100, PROV); save_idea(src, OWNER)
# Manually set dependent to stale value.
dep_stale = load_idea(dep.id, OWNER)
dep_stale.set_property("m", 999, PROV)  # stale
save_idea(dep_stale, OWNER)
# Write a valid journal and verify it passes validation.
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
r["p7_status_pending"] = (g.propagation_status(dep.id, "m") == "pending")
# Fresh load replays: dependent should get correct value (100, not 999).
""" + (FRESH_LOAD % {"REPO": REPO, "OWNER": OWNER}).replace(
        'r["p3_fresh_rejects"] = ("REJECTED" in pr.stdout)',
        'r["p7_replay_ok"] = ("LOADED" in pr.stdout)').replace(
        'r["p3_not_loaded"] = ("LOADED" not in pr.stdout)',
        '''r["p7_journal_cleared"] = (not os.path.isfile(jpath))
dep_after = load_idea(dep.id, OWNER)
r["p7_recomputed"] = (dep_after.get_property("m") == 100)''') + TEARDOWN)
    return ("valid-control", code)


def smoke() -> bool:
    """Run all DSC1_J01 R1 cases. Returns True iff all pass."""
    cases = [
        _invalid_case("empty-dict", "{}"),
        _invalid_case("foreign-owner",
            json.dumps({"format_version": 1, "owner": "FOREIGN", "operations": []})),
        _invalid_case("unknown-op",
            json.dumps({"format_version": 1, "owner": OWNER, "operations": [{"op": "bogus"}]})),
        _invalid_case("missing-ops",
            json.dumps({"format_version": 1, "owner": OWNER})),
        # F3: version type coercion cases.
        _invalid_case("version-bool-true",
            json.dumps({"format_version": True, "owner": OWNER, "operations": []})),
        _invalid_case("version-float",
            json.dumps({"format_version": 1.0, "owner": OWNER, "operations": []})),
        _invalid_case("version-string",
            json.dumps({"format_version": "1", "owner": OWNER, "operations": []})),
        _invalid_case("version-missing",
            json.dumps({"owner": OWNER, "operations": []})),
        _invalid_case("version-999",
            json.dumps({"format_version": 999, "owner": OWNER, "operations": []})),
        _invalid_case("truncated-json",
            '{"format_version": 1, "owner": "DSC1R2", "oper'),
        _invalid_case("wrong-types",
            json.dumps({"format_version": "1", "owner": OWNER, "operations": []})),
        _invalid_case("incomplete-op",
            json.dumps({"format_version": 1, "owner": OWNER,
                        "operations": [{"op": "sync_dependent"}]})),
        # F1: malformed embedded entries.
        _invalid_case("malformed-entry-new-id",
            json.dumps({"format_version": 1, "owner": OWNER,
                        "operations": [{"op": "ensure_edge",
                                        "entry": {"rel_id": "NEW", "seq": 2}}]})),
        _invalid_case("malformed-entry-missing-type",
            json.dumps({"format_version": 1, "owner": OWNER,
                        "operations": [{"op": "ensure_edge",
                                        "entry": {"rel_id": "X", "seq": 1,
                                                  "source_id": "s", "target_id": "t"}}]})),
        _invalid_case("empty-op-id",
            json.dumps({"format_version": 1, "owner": OWNER,
                        "operations": [{"op": "sync_dependent", "dependent_id": "",
                                        "derived_property": "m", "target_id": "t",
                                        "edge_rel_id": "e"}]})),
        _outgoing_case(),
        _valid_control(),
    ]

    all_results = {}
    for name, code in cases:
        all_results.update(_phase(name, code))

    fails = [k for k, v in all_results.items() if not v]
    npass = sum(1 for v in all_results.values() if v)
    ntotal = len(all_results)
    print(f"DSC1_J01 R1: {npass}/{ntotal} PASS", flush=True)
    if fails:
        print(f"FAILURES: {fails[:10]}", flush=True)
        return False
    # Fail on empty evidence.
    if ntotal == 0:
        print("FAIL: empty evidence", flush=True)
        return False
    print("DSC1_J01 WORLD: ALL PASS", flush=True)
    return True


def main() -> None:
    """Entry point with honest exit status."""
    ok = smoke()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
