"""DSC1_J01 R3: instrumented live-listener proof with causal controls.

R3 micro-gate requirements:
1. Observe real execution: wrapping observers installed BEFORE callback
   registration, executing the original implementation, preserving behavior.
   Record: source ID, property, callback entry, propagation attempt,
   rejection boundary. Setup-time calls cannot satisfy mutation-time witnesses.
2. Causal controls (isolated):
   - Healthy attached: source=100, dependent=100, propagation witnessed.
   - Truncated journal: source=100, dependent=42, decoding rejection
     witnessed, status unknown, bytes preserved, fresh reject.
   - Parseable invalid: source=100, dependent=42, schema rejection
     witnessed, status unknown, bytes preserved, fresh reject.
   - Missing subscription: no callback, no propagation witnessed.
3. Targeted mutants with witness/exit classification.
4. Preserve semantics: mutation may return normally; claim neither
   caller-visible exception nor rollback.

Portable: REPO from __file__. Enforced: smoke()->bool, sys.exit.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OWNER = "DSC1R3"


def _phase(name: str, code: str) -> dict:
    r = subprocess.run(
        [sys.executable, "-c", code],
        cwd=REPO, capture_output=True, text=True, timeout=120)
    results = {}
    if r.returncode != 0:
        results[f"{name}::crashed_rc{r.returncode}"] = False
        return results
    for line in r.stdout.splitlines():
        if line.startswith("RESULT "):
            try:
                d = json.loads(line[len("RESULT "):])
                for k, v in d.items():
                    # Only collect assertion keys, not raw measurements.
                    # Raw: n_callback, n_propagate, n_rejection, n_decoding,
                    #      dep_val, w_mutation_time (used by CHECKS, not a verdict).
                    if k.startswith("n_") or k in ("dep_val", "w_mutation_time"):
                        continue
                    results[f"{name}::{k}"] = bool(v)
            except json.JSONDecodeError:
                results[f"{name}::bad_json"] = False
    if not results:
        results[f"{name}::empty_evidence"] = False
    return results


# The instrumented probe. Observers wrap the original implementations,
# record witnesses, and preserve behavior by calling through.
PROBE = """
import json, os, shutil, subprocess, sys
REPO = %(REPO)r
OWNER = %(OWNER)r
sys.path.insert(0, REPO)
from form.mandell.idea import Idea, Provenance, ProvenanceSource
from form.mandell.idea_persist import save_idea, load_idea
from form.mandell import semantic_graph as sg
from form.mandell.semantic_graph import (
    SemanticGraph, DerivationKind, GraphValidationError,
    graph_path, graph_journal_path, validate_journal)
from form.persist import _STATE_DIR
BASE = _STATE_DIR
for p in [os.path.join(BASE, f"ideas_{OWNER}"), graph_path(OWNER), graph_journal_path(OWNER)]:
    if os.path.isdir(p): shutil.rmtree(p)
    elif os.path.isfile(p): os.remove(p)
PROV = Provenance(source=ProvenanceSource.HUMAN, activity="dsc1r3", agent="dsc1r3")
src = Idea(title="S"); src.set_property("v", 42, PROV); save_idea(src, OWNER)
dep = Idea(title="D"); save_idea(dep, OWNER)
g = SemanticGraph.load(OWNER)
edge = g.declare_dependency(dep.id, src.id, DerivationKind.MIRROR, "m", unit="v", provenance=PROV)
# The MIRROR establishes dep.m from src.v (42). Verify.
dep = load_idea(dep.id, OWNER)
jpath = graph_journal_path(OWNER)
r = {}
W = {"callback_entry": [], "propagate_attempt": [], "rejection": [], "decoding_reject": []}

# --- Observer 1: wrap _on_idea_event (installed BEFORE attach) ---
_orig_on_event = g._on_idea_event
def _obs_on_event(idea, event):
    # Mutation-time witness: record source ID, property, operation.
    W["callback_entry"].append((idea.id, event.property_name, event.operation))
    return _orig_on_event(idea, event)
g._on_idea_event = _obs_on_event

# --- Observer 2: wrap _propagate_property to witness propagation attempts ---
_orig_propagate = g._propagate_property
def _obs_propagate(idea_id, property_name, live_idea=None):
    W["propagate_attempt"].append((idea_id, property_name))
    return _orig_propagate(idea_id, property_name, live_idea)
g._propagate_property = _obs_propagate

# --- Observer 3: wrap validate_journal to witness rejection boundary ---
_orig_validate = sg.validate_journal
def _obs_validate(data, owner):
    try:
        return _orig_validate(data, owner)
    except GraphValidationError as e:
        # Rejection boundary witnessed: record where it rejected.
        W["rejection"].append(("validate_journal", str(e)[:50]))
        raise
sg.validate_journal = _obs_validate

# --- Observer 4 (R3 closeout): wrap _write_journal to witness DECODING ---
# Delegate unchanged; record when GraphValidationError has a
# json.JSONDecodeError cause; re-raise unchanged.
_orig_write_journal = g._write_journal
def _obs_write_journal(operations):
    try:
        return _orig_write_journal(operations)
    except GraphValidationError as e:
        cause = e.__cause__
        if isinstance(cause, json.JSONDecodeError):
            W["decoding_reject"].append(str(cause)[:50])
        raise
g._write_journal = _obs_write_journal
# (Methods call the module-global validate_journal.)

# --- Attach AFTER observers installed ---
%(ATTACH)s

# --- Write journal (or not) ---
%(JOURNAL)s

# --- Mutation (the witnessed event) ---
%(MUTATE)s

# --- Collect witnesses (case-specific expectations in CHECKS) ---
# Generic: record raw witness counts; CHECKS defines pass/fail.
r["n_callback"] = len(W["callback_entry"])
r["n_propagate"] = len(W["propagate_attempt"])
r["n_rejection"] = len(W["rejection"])
r["n_decoding"] = len(W["decoding_reject"])
r["w_mutation_time"] = any(p == "v" for _, p, _ in W["callback_entry"])
# Invariants.
src_after = load_idea(src.id, OWNER)
dep_after = load_idea(dep.id, OWNER)
r["src_100"] = (src_after.get_property("v") == 100)
r["dep_val"] = dep_after.get_property("m")
%(CHECKS)s
# Cleanup.
shutil.rmtree(os.path.join(BASE, f"ideas_{OWNER}"), ignore_errors=True)
for p in [graph_path(OWNER), graph_journal_path(OWNER)]:
    if os.path.isfile(p): os.remove(p)
print("RESULT " + json.dumps(r))
"""


def _healthy() -> tuple[str, str]:
    """Healthy attached mutation: source=100, dependent=100, propagation witnessed."""
    code = PROBE % {
        "REPO": REPO, "OWNER": OWNER,
        "ATTACH": "g.attach(src)",
        "JOURNAL": "# No journal (healthy).",
        "MUTATE": "src.set_property(\"v\", 100, PROV); save_idea(src, OWNER)",
        "CHECKS": """
r["dep_100"] = (r["dep_val"] == 100)
r["status_sync"] = (g.propagation_status(dep.id, "m") == "synchronized")
r["witness_callback"] = (r["n_callback"] > 0)
r["witness_propagate"] = (r["n_propagate"] > 0)
r["witness_no_reject"] = (r["n_rejection"] == 0)
r["witness_no_decoding"] = (r["n_decoding"] == 0)
""",
    }
    return ("r3-healthy", code)


def _truncated() -> tuple[str, str]:
    """Truncated journal: decoding rejection witnessed."""
    code = PROBE % {
        "REPO": REPO, "OWNER": OWNER,
        "ATTACH": "g.attach(src)",
        "JOURNAL": """
with open(jpath, "w") as f: f.write("{trunc")
with open(jpath) as f: jb = f.read()
""",
        "MUTATE": "src.set_property(\"v\", 100, PROV); save_idea(src, OWNER)",
        "CHECKS": """
r["dep_42"] = (r["dep_val"] == 42)
r["status_unknown"] = (g.propagation_status(dep.id, "m") == "unknown")
with open(jpath) as f: r["bytes_intact"] = (f.read() == jb)
# Fresh-process rejection.
fc_lines = [
    "import sys",
    "sys.path.insert(0, " + repr(REPO) + ")",
    "from form.mandell.semantic_graph import SemanticGraph, GraphValidationError",
    "try:",
    "    SemanticGraph.load(" + repr(OWNER) + ")",
    '    print("LOADED")',
    "except GraphValidationError:",
    '    print("REJECTED")',
]
fc = chr(10).join(fc_lines)
pr = subprocess.run([sys.executable, "-c", fc], capture_output=True, text=True, timeout=30)
r["fresh_reject"] = ("REJECTED" in pr.stdout)
# Witnesses: callback entered, propagation attempted, decoding rejected.
r["witness_callback"] = (r["n_callback"] > 0)
r["witness_propagate"] = (r["n_propagate"] > 0)
# R3 closeout: exactly one decoding rejection for truncated JSON.
r["witness_decoding"] = (r["n_decoding"] == 1)
r["witness_mutation_time"] = r["w_mutation_time"]
""",
    }
    return ("r3-truncated", code)


def _parseable_invalid() -> tuple[str, str]:
    """Parseable invalid journal: schema rejection witnessed."""
    code = PROBE % {
        "REPO": REPO, "OWNER": OWNER,
        "ATTACH": "g.attach(src)",
        "JOURNAL": """
import json as _j
with open(jpath, "w") as f:
    f.write(_j.dumps({"format_version": 999, "owner": OWNER, "operations": []}))
with open(jpath) as f: jb = f.read()
""",
        "MUTATE": "src.set_property(\"v\", 100, PROV); save_idea(src, OWNER)",
        "CHECKS": """
r["dep_42"] = (r["dep_val"] == 42)
r["status_unknown"] = (g.propagation_status(dep.id, "m") == "unknown")
with open(jpath) as f: r["bytes_intact"] = (f.read() == jb)
fc_lines = [
    "import sys",
    "sys.path.insert(0, " + repr(REPO) + ")",
    "from form.mandell.semantic_graph import SemanticGraph, GraphValidationError",
    "try:",
    "    SemanticGraph.load(" + repr(OWNER) + ")",
    '    print("LOADED")',
    "except GraphValidationError:",
    '    print("REJECTED")',
]
fc = chr(10).join(fc_lines)
pr = subprocess.run([sys.executable, "-c", fc], capture_output=True, text=True, timeout=30)
r["fresh_reject"] = ("REJECTED" in pr.stdout)
# Schema rejection witnessed via validate_journal observer.
r["witness_schema_reject"] = (r["n_rejection"] > 0)
r["witness_callback"] = (r["n_callback"] > 0)
r["witness_propagate"] = (r["n_propagate"] > 0)
# R3 closeout: no decoding rejection for parseable-invalid (it's valid JSON).
r["witness_no_decoding"] = (r["n_decoding"] == 0)
""",
    }
    return ("r3-parseable-invalid", code)


def _missing_subscription() -> tuple[str, str]:
    """Counterfactual: no attach → no propagation witnessed."""
    code = PROBE % {
        "REPO": REPO, "OWNER": OWNER,
        "ATTACH": "# No attach (counterfactual).",
        "JOURNAL": "# No journal.",
        "MUTATE": "src.set_property(\"v\", 100, PROV); save_idea(src, OWNER)",
        "CHECKS": """
r["dep_42"] = (r["dep_val"] == 42)
r["witness_no_callback"] = (r["n_callback"] == 0)
r["witness_no_propagate"] = (r["n_propagate"] == 0)
# Counterfactual: absent callback cannot satisfy positive proof.
r["counterfactual_holds"] = (r["n_callback"] == 0 and r["dep_val"] == 42)
""",
    }
    return ("r3-missing-subscription", code)


def smoke() -> bool:
    cases = [_healthy(), _truncated(), _parseable_invalid(), _missing_subscription()]
    all_results = {}
    for name, code in cases:
        all_results.update(_phase(name, code))
    fails = [k for k, v in all_results.items() if not v]
    npass = sum(1 for v in all_results.values() if v)
    ntotal = len(all_results)
    print(f"DSC1_J01 R3: {npass}/{ntotal} PASS", flush=True)
    if fails:
        print(f"FAILURES: {fails[:12]}", flush=True)
        return False
    if ntotal == 0:
        print("FAIL: empty evidence", flush=True)
        return False
    print("DSC1_J01 R3 WORLD: ALL PASS", flush=True)
    return True


def main() -> None:
    sys.exit(0 if smoke() else 1)


if __name__ == "__main__":
    main()
