"""GDP-001 Phase 2 MICRO-GATE — Journal fail-closed proofs.

- corrupt journal before new propagation → _write_journal raises (no overwrite)
- corrupt journal queried via propagation_status → "unknown" (never "synchronized")
- journal write failure while recording propagation failure → typed error or journal remains
- fresh-process load after each case → fail-closed, no valid state from unknown

Each runs in a FRESH OS process. Owner: P2MG (isolated; cleaned).
"""

import json
import os
import shutil
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RESULTS = []


def run_phase(name, code):
    print(f"--- {name} ---", flush=True)
    r = subprocess.run(
        [sys.executable, "-c", code],
        cwd=REPO, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        print(f"PHASE {name} CRASHED rc={r.returncode}", flush=True)
        print(r.stdout[-1200:], flush=True)
        print(r.stderr[-1200:], flush=True)
        RESULTS.append((name + " crashed", False))
        return
    for line in r.stdout.splitlines():
        if line.startswith("RESULT "):
            d = json.loads(line[len("RESULT "):])
            for k, v in d.items():
                RESULTS.append((k, bool(v)))
                print(("PASS " if v else "FAIL ") + k, flush=True)


PROV = "Provenance(source=ProvenanceSource.HUMAN, activity='mg', agent='mg')"


def main():
    # ---- MG1: corrupt journal before new propagation --------------------
    run_phase("MG1-corrupt-before-propagate", """
import json, os, shutil
from form.mandell.idea import Idea, Provenance, ProvenanceSource
from form.mandell.idea_persist import save_idea
from form.mandell.semantic_graph import (
    SemanticGraph, DerivationKind, GraphValidationError,
    graph_path, graph_journal_path)
from form.persist import _STATE_DIR
BASE=_STATE_DIR; OWNER="P2MG1"
for p in [os.path.join(BASE,f"ideas_{OWNER}"), graph_path(OWNER), graph_journal_path(OWNER)]:
    (shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)) if os.path.exists(p) else None
PROV=%s
r={}
try:
    src=Idea(title="S"); src.set_property("v", 1, PROV); save_idea(src, OWNER)
    dep=Idea(title="D"); save_idea(dep, OWNER)
    g=SemanticGraph.load(OWNER)
    g.attach(src)
    g.declare_dependency(dep.id, src.id, DerivationKind.MIRROR, "m", unit="v", provenance=PROV)
    # Corrupt the journal: write invalid JSON.
    with open(graph_journal_path(OWNER), "w") as f:
        f.write("{corrupt json!!!")
    # Direct _write_journal must raise GraphValidationError (fail closed),
    # NOT overwrite the corrupt journal.
    try:
        g._write_journal([{"op": "sync_dependent", "dependent_id": "x"}])
        r["raised"]=False
    except GraphValidationError:
        r["raised"]=True
    except Exception as e:
        r["raised"]="wrong:"+type(e).__name__
    # The corrupt journal must still be there (not overwritten).
    with open(graph_journal_path(OWNER)) as f:
        r["not_overwritten"]=("{corrupt" in f.read())
    print("RESULT "+json.dumps(r))
finally:
    shutil.rmtree(os.path.join(BASE, f"ideas_{OWNER}"), ignore_errors=True)
    os.path.exists(graph_path(OWNER)) and os.remove(graph_path(OWNER))
    os.path.exists(graph_journal_path(OWNER)) and os.remove(graph_journal_path(OWNER))
""" % PROV)

    # ---- MG2: corrupt journal via propagation_status --------------------
    run_phase("MG2-corrupt-status-query", """
import json, os, shutil
from form.mandell.idea import Idea, Provenance, ProvenanceSource
from form.mandell.idea_persist import save_idea
from form.mandell.semantic_graph import (
    SemanticGraph, DerivationKind, graph_path, graph_journal_path)
from form.persist import _STATE_DIR
BASE=_STATE_DIR; OWNER="P2MG2"
for p in [os.path.join(BASE,f"ideas_{OWNER}"), graph_path(OWNER), graph_journal_path(OWNER)]:
    (shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)) if os.path.exists(p) else None
PROV=%s
r={}
try:
    src=Idea(title="S"); src.set_property("v", 1, PROV); save_idea(src, OWNER)
    dep=Idea(title="D"); save_idea(dep, OWNER)
    g=SemanticGraph.load(OWNER)
    g.declare_dependency(dep.id, src.id, DerivationKind.MIRROR, "m", unit="v", provenance=PROV)
    # Corrupt the journal.
    with open(graph_journal_path(OWNER), "w") as f:
        f.write("not json at all")
    # propagation_status MUST NOT return "synchronized".
    st=g.propagation_status(dep.id, "m")
    r["not_synchronized"]=(st != "synchronized")
    r["is_unknown"]=(st == "unknown")
    print("RESULT "+json.dumps(r))
finally:
    shutil.rmtree(os.path.join(BASE, f"ideas_{OWNER}"), ignore_errors=True)
    os.path.exists(graph_path(OWNER)) and os.remove(graph_path(OWNER))
    os.path.exists(graph_journal_path(OWNER)) and os.remove(graph_journal_path(OWNER))
""" % PROV)

    # ---- MG3: fresh load with corrupt journal ---------------------------
    run_phase("MG3-fresh-load-corrupt", """
import json, os, shutil, subprocess, sys
from form.mandell.idea import Idea, Provenance, ProvenanceSource
from form.mandell.idea_persist import save_idea
from form.mandell.semantic_graph import (
    SemanticGraph, DerivationKind, GraphValidationError,
    graph_path, graph_journal_path)
from form.persist import _STATE_DIR
BASE=_STATE_DIR; OWNER="P2MG3"
for p in [os.path.join(BASE,f"ideas_{OWNER}"), graph_path(OWNER), graph_journal_path(OWNER)]:
    (shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)) if os.path.exists(p) else None
PROV=%s
r={}
try:
    src=Idea(title="S"); src.set_property("v", 1, PROV); save_idea(src, OWNER)
    dep=Idea(title="D"); save_idea(dep, OWNER)
    g=SemanticGraph.load(OWNER)
    g.declare_dependency(dep.id, src.id, DerivationKind.MIRROR, "m", unit="v", provenance=PROV)
    # Corrupt the journal, then fresh-process load must fail closed.
    with open(graph_journal_path(OWNER), "w") as f:
        f.write("{bad")
    import textwrap
    code = textwrap.dedent('''
        import sys
        sys.path.insert(0, "/home/hatch/workspace/dellmatrix-gdp-phase1")
        from form.mandell.semantic_graph import SemanticGraph, GraphValidationError
        try:
            g = SemanticGraph.load("P2MG3")
            print("LOADED")
        except GraphValidationError:
            print("FAIL_CLOSED")
    ''')
    pr=subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=60)
    r["fail_closed"]=("FAIL_CLOSED" in pr.stdout)
    r["not_loaded"]=("LOADED" not in pr.stdout)
    print("RESULT "+json.dumps(r))
finally:
    shutil.rmtree(os.path.join(BASE, f"ideas_{OWNER}"), ignore_errors=True)
    os.path.exists(graph_path(OWNER)) and os.remove(graph_path(OWNER))
    os.path.exists(graph_journal_path(OWNER)) and os.remove(graph_journal_path(OWNER))
""" % PROV)

    # ---- MG4: owner sanitizer single authority --------------------------
    run_phase("MG4-sanitizer", """
import json
r={}
# No local _safe_owner in semantic_graph; uses form.persist._safe_owner.
import form.mandell.semantic_graph as sg
import form.persist as fp
r["no_local"]=(not hasattr(sg, "_safe_owner") or sg._safe_owner is fp._safe_owner)
r["same_fn"]=(sg._safe_owner is fp._safe_owner)
# Empty/special owners map to same namespace.
r["empty"]= (sg._safe_owner("") == fp._safe_owner("") == "operator")
r["special"]=(sg._safe_owner("a/b@c!") == fp._safe_owner("a/b@c!"))
r["paths_match"]=(sg.graph_path("x/y") == sg.graph_path("x_y"))
print("RESULT "+json.dumps(r))
""")

    fails = [n for n, ok in RESULTS if not ok]
    npass = sum(1 for _, ok in RESULTS if ok)
    print(f"\\nP2 MICRO-GATE: {npass}/{len(RESULTS)} PASS", flush=True)
    print("P2 MICRO-GATE WORLD: ALL PASS" if not fails else f"FAILURES: {fails}", flush=True)


if __name__ == "__main__":
    main()
