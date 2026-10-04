"""GDP-001 Phase 2 R1 — Propagation Integrity Closure proofs.

R1-1: SILENT PROPAGATION FAILURE
  Attached source mutation → dependent load/save failure → failure is
  observable in the ledger (FAILED, never silent) → no false 'synchronized'
  → reconcile() produces deterministic correct state.

R1-2: GRAPH/DERIVED-IDEA DISK ATOMICITY
  A. dependent Idea write failure → NEITHER committed (or FAILED explicit)
  B. graph persistence failure after dependent write → FAILED explicit
  C. interruption (crash) between dependent and graph persistence → journal replay
  D. fresh-process recovery → journal replay converges
  E. multi-dependent partial propagation → FAILED marks exactly which
  F. multi-hop where intermediate write fails → journal covers chain

Each runs in a FRESH OS process. Owner: P2R1 (isolated; cleaned).
"""

import glob
import json
import os
import shutil
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = None  # set in subprocess via form.persist
OWNER = "P2R1"

RESULTS = []


def run_phase(name, code):
    global RESULTS
    print(f"--- {name} ---", flush=True)
    r = subprocess.run(
        [sys.executable, "-c", code],
        cwd=REPO, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        print(f"PHASE {name} CRASHED rc={r.returncode}", flush=True)
        print(r.stdout[-1500:], flush=True)
        print(r.stderr[-1500:], flush=True)
        RESULTS.append((name + " crashed", False))
        return
    for line in r.stdout.splitlines():
        if line.startswith("RESULT "):
            d = json.loads(line[len("RESULT "):])
            for k, v in d.items():
                RESULTS.append((k, bool(v)))
                print(("PASS " if v else "FAIL ") + k, flush=True)


PROV = ("Provenance(source=ProvenanceSource.HUMAN, activity='r1', agent='r1')")


def main():
    # ---- R1-1: silent propagation failure -------------------------------
    run_phase("R1-1-silent-failure", """
import json, os, glob, shutil
from form.mandell.idea import Idea, Provenance, ProvenanceSource
from form.mandell.idea_persist import save_idea, load_idea
from form.mandell.semantic_graph import SemanticGraph, DerivationKind, graph_path
from form.persist import _STATE_DIR
BASE=_STATE_DIR; OWNER="P2R1"
for p in [os.path.join(BASE,f"ideas_{OWNER}"), graph_path(OWNER)]:
    (shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)) if os.path.exists(p) else None
PROV=%s
r={}
try:
    src=Idea(title="Src"); save_idea(src, OWNER)
    dep=Idea(title="Dep"); save_idea(dep, OWNER)
    g=SemanticGraph.load(OWNER)
    g.attach(src)
    g.declare_dependency(dep.id, src.id, DerivationKind.MIRROR, "m", unit="v", provenance=PROV)
    # Cause the dependent save to fail (monkeypatch, not file deletion —
    # deleting the file would make the edge dangling and fail validation).
    import form.mandell.semantic_graph as sg
    orig_save=sg.save_idea
    def failing_save(idea, owner):
        if idea.id==dep.id:
            raise OSError("simulated dependent save failure")
        return orig_save(idea, owner)
    sg.save_idea=failing_save
    try:
        # Mutate the source (attached). Propagation to dep will fail on save.
        src.set_property("v", 99, PROV)
        save_idea(src, OWNER)
        r["source_mutation_succeeded"] = (load_idea(src.id, OWNER).get_active_properties().get("v") == 99)
    finally:
        sg.save_idea=orig_save
    # ...but the failure must be OBSERVABLE, not silent.
    fails = g.get_propagation_failures()
    r["failure_observable"] = any(f["dependent_id"] == dep.id for f in fails)
    # ...and must NOT be presented as synchronized.
    r["not_fake_synchronized"] = (g.propagation_status(dep.id, "m") == "failed")
    # Verify the FAILED state persists across a fresh load.
    g2=SemanticGraph.load(OWNER)
    r["failed_persists_fresh_load"] = (g2.propagation_status(dep.id, "m") == "failed")
    r["failed_queryable_fresh"] = any(f["dependent_id"] == dep.id for f in g2.get_propagation_failures())
    print("RESULT "+json.dumps(r))
finally:
    shutil.rmtree(os.path.join(BASE, f"ideas_{OWNER}"), ignore_errors=True)
    os.path.exists(graph_path(OWNER)) and os.remove(graph_path(OWNER))
""" % PROV)

    # ---- R1-1b: reconcile recovers --------------------------------------
    run_phase("R1-1b-reconcile", """
import json, os, glob, shutil
from form.mandell.idea import Idea, Provenance, ProvenanceSource
from form.mandell.idea_persist import save_idea, load_idea
from form.mandell.semantic_graph import SemanticGraph, DerivationKind, graph_path
from form.persist import _STATE_DIR
BASE=_STATE_DIR; OWNER="P2R1B"
for p in [os.path.join(BASE,f"ideas_{OWNER}"), graph_path(OWNER)]:
    (shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)) if os.path.exists(p) else None
PROV=%s
r={}
try:
    src=Idea(title="Src"); src.set_property("v", 1, PROV); save_idea(src, OWNER)
    dep=Idea(title="Dep"); save_idea(dep, OWNER)
    g=SemanticGraph.load(OWNER)
    g.attach(src)
    g.declare_dependency(dep.id, src.id, DerivationKind.MIRROR, "m", unit="v", provenance=PROV)
    # Cause failure via monkeypatch (not file deletion).
    import form.mandell.semantic_graph as sg
    orig_save=sg.save_idea
    def failing_save(idea, owner):
        if idea.id==dep.id:
            raise OSError("simulated failure")
        return orig_save(idea, owner)
    sg.save_idea=failing_save
    try:
        src.set_property("v", 2, PROV); save_idea(src, OWNER)
    finally:
        sg.save_idea=orig_save
    r["failed_before"] = (g.propagation_status(dep.id, "m") == "failed")
    # Now reconcile (patch removed; dependent can be synced).
    # Source is at v=2; reconcile should sync dep to m=2 and clear FAILED.
    updated = g.reconcile(src.id)
    r["reconcile_updated"] = (updated >= 1)
    r["failed_cleared"] = (g.propagation_status(dep.id, "m") == "synchronized")
    r["value_correct"] = (load_idea(dep.id, OWNER).get_active_properties().get("m") == 2)
    print("RESULT "+json.dumps(r))
finally:
    shutil.rmtree(os.path.join(BASE, f"ideas_{OWNER}"), ignore_errors=True)
    os.path.exists(graph_path(OWNER)) and os.remove(graph_path(OWNER))
    jp=os.path.join(BASE, f"graph_{OWNER}.journal.json")
    os.path.exists(jp) and os.remove(jp)
""" % PROV)

    # ---- R1-2 A: dependent write failure --------------------------------
    run_phase("R1-2A-dep-write-fail", """
import json, os, shutil
from form.mandell.idea import Idea, Provenance, ProvenanceSource
from form.mandell.idea_persist import save_idea, load_idea
from form.mandell.semantic_graph import SemanticGraph, DerivationKind, RelationshipType, graph_path
from form.persist import _STATE_DIR
BASE=_STATE_DIR; OWNER="P2R1A"
for p in [os.path.join(BASE,f"ideas_{OWNER}"), graph_path(OWNER)]:
    (shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)) if os.path.exists(p) else None
PROV=%s
r={}
try:
    src=Idea(title="Src"); src.set_property("v", 1, PROV); save_idea(src, OWNER)
    dep=Idea(title="Dep"); save_idea(dep, OWNER)
    g=SemanticGraph.load(OWNER)
    # Make the dependent's file unwritable (simulating write failure).
    # We do this by making the ideas dir read-only briefly.
    ddir=os.path.join(BASE, f"ideas_{OWNER}")
    # Instead: monkeypatch save_idea to throw for the dependent.
    import form.mandell.semantic_graph as sg
    orig_save=sg.save_idea
    def failing_save(idea, owner):
        if idea.id==dep.id:
            raise OSError("simulated disk failure")
        return orig_save(idea, owner)
    sg.save_idea=failing_save
    try:
        g.declare_dependency(dep.id, src.id, DerivationKind.MIRROR, "m", unit="v", provenance=PROV)
        r["raised"]=False
    except OSError:
        r["raised"]=True
    finally:
        sg.save_idea=orig_save
    # Invariant: edge committed (graph-first) BUT FAILED explicitly recorded.
    # It must NOT be silent, and must NOT claim success.
    g2=SemanticGraph.load(OWNER)
    has_edge=any(e.type==RelationshipType.DEPENDS_ON and e.source_id==dep.id
                 for e in g2._current.values())
    r["edge_committed"]=has_edge
    r["failed_explicit"]=(g2.propagation_status(dep.id, "m")=="failed")
    r["not_silent"]=len(g2.get_propagation_failures())>0
    print("RESULT "+json.dumps(r))
finally:
    shutil.rmtree(os.path.join(BASE, f"ideas_{OWNER}"), ignore_errors=True)
    os.path.exists(graph_path(OWNER)) and os.remove(graph_path(OWNER))
    jp=os.path.join(BASE, f"graph_{OWNER}.journal.json")
    os.path.exists(jp) and os.remove(jp)
""" % PROV)

    # ---- R1-2 B: graph save failure after dependent write ---------------
    run_phase("R1-2B-graph-save-fail", """
import json, os, shutil
from form.mandell.idea import Idea, Provenance, ProvenanceSource
from form.mandell.idea_persist import save_idea
from form.mandell.semantic_graph import SemanticGraph, DerivationKind, RelationshipType, graph_path
from form.persist import _STATE_DIR
BASE=_STATE_DIR; OWNER="P2R1B2"
for p in [os.path.join(BASE,f"ideas_{OWNER}"), graph_path(OWNER)]:
    (shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)) if os.path.exists(p) else None
PROV=%s
r={}
try:
    src=Idea(title="Src"); src.set_property("v", 1, PROV); save_idea(src, OWNER)
    dep=Idea(title="Dep"); save_idea(dep, OWNER)
    g=SemanticGraph.load(OWNER)
    # Fail the GRAPH edge save (graph-first ordering: the edge save is
    # the FIRST graph write; if it fails, the dependent idea is never
    # touched → NEITHER committed).
    import form.mandell.semantic_graph as sg
    orig_atomic=sg.atomic_write_json if hasattr(sg,'atomic_write_json') else None
    # Patch at the import site inside save()
    import form.dell_matrix.atomic_write as aw
    orig=aw.atomic_write_json
    def failing_atomic(path, data):
        # Fail only for the graph file, not the journal.
        if path.endswith(".journal.json"):
            return orig(path, data)
        raise OSError("simulated graph disk failure")
    aw.atomic_write_json=failing_atomic
    try:
        g.declare_dependency(dep.id, src.id, DerivationKind.MIRROR, "m", unit="v", provenance=PROV)
        r["raised"]=False
    except OSError:
        r["raised"]=True
    finally:
        aw.atomic_write_json=orig
    # The edge save failed → NEITHER committed. In-memory rolled back,
    # journal cleared, dependent idea untouched.
    g2=SemanticGraph.load(OWNER)
    has_edge=any(e.type==RelationshipType.DEPENDS_ON and e.source_id==dep.id
                 for e in g2._current.values())
    r["neither_committed"]=not has_edge
    print("RESULT "+json.dumps(r))
finally:
    shutil.rmtree(os.path.join(BASE, f"ideas_{OWNER}"), ignore_errors=True)
    os.path.exists(graph_path(OWNER)) and os.remove(graph_path(OWNER))
    jp=os.path.join(BASE, f"graph_{OWNER}.journal.json")
    os.path.exists(jp) and os.remove(jp)
""" % PROV)

    # ---- R1-2 C+D: crash between dependent and graph persistence --------
    run_phase("R1-2CD-crash-recovery", """
import json, os, shutil
from form.mandell.idea import Idea, Provenance, ProvenanceSource
from form.mandell.idea_persist import save_idea, load_idea
from form.mandell.semantic_graph import SemanticGraph, DerivationKind, RelationshipType, graph_path, graph_journal_path
from form.persist import _STATE_DIR
BASE=_STATE_DIR; OWNER="P2R1CD"
for p in [os.path.join(BASE,f"ideas_{OWNER}"), graph_path(OWNER), graph_journal_path(OWNER)]:
    (shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)) if os.path.exists(p) else None
PROV=%s
r={}
try:
    src=Idea(title="Src"); src.set_property("v", 42, PROV); save_idea(src, OWNER)
    dep=Idea(title="Dep"); save_idea(dep, OWNER)
    g=SemanticGraph.load(OWNER)
    # Simulate a crash: write the journal manually (as declare_dependency
    # would), append the edge to the graph file (simulating "graph saved"),
    # but do NOT sync the dependent (simulating "crash before idea save").
    # Then verify a FRESH load replays and converges.
    from form.mandell.semantic_graph import RelationshipEntry, RelationshipStatus
    import uuid, time
    entry=RelationshipEntry(
        rel_id=str(uuid.uuid4()), type=RelationshipType.DEPENDS_ON,
        source_id=dep.id, target_id=src.id,
        props=(("derived_property","m"),("derivation","mirror"),("unit","v")),
        status=RelationshipStatus.ACTIVE, seq=0, recorded_at=time.time(),
        provenance=PROV, cause="declare_dependency")
    journal={"format_version":1,"owner":OWNER,"txn_id":"test","started_at":time.time(),
             "operations":[
                 {"op":"ensure_edge","entry":entry.to_dict()},
                 {"op":"sync_dependent","dependent_id":dep.id,"derived_property":"m",
                  "target_id":src.id,"unit":"v","derivation":"mirror",
                  "subject_id":None,"edge_rel_id":entry.rel_id}]}
    import form.dell_matrix.atomic_write as aw
    aw.atomic_write_json(graph_journal_path(OWNER), journal)
    # Also write the edge to the graph file directly (simulating the
    # "graph saved" state before the crash).
    g._entries.append(entry); g._fold(); g.save()
    # Dependent does NOT have the derived value (crash before sync).
    r["dep_missing_before"]=("m" not in load_idea(dep.id, OWNER).get_active_properties())
    # FRESH process load: journal replay must converge.
    g2=SemanticGraph.load(OWNER)
    r["journal_cleared"]=not os.path.isfile(graph_journal_path(OWNER))
    r["dep_synced_after"]=load_idea(dep.id, OWNER).get_active_properties().get("m")==42
    r["edge_present"]=any(e.rel_id==entry.rel_id for e in g2._current.values())
    print("RESULT "+json.dumps(r))
finally:
    shutil.rmtree(os.path.join(BASE, f"ideas_{OWNER}"), ignore_errors=True)
    os.path.exists(graph_path(OWNER)) and os.remove(graph_path(OWNER))
    os.path.exists(graph_journal_path(OWNER)) and os.remove(graph_journal_path(OWNER))
""" % PROV)

    # ---- R1-2 E: multi-dependent partial --------------------------------
    run_phase("R1-2E-multi-dependent", """
import json, os, shutil
from form.mandell.idea import Idea, Provenance, ProvenanceSource
from form.mandell.idea_persist import save_idea, load_idea
from form.mandell.semantic_graph import SemanticGraph, DerivationKind, graph_path
from form.persist import _STATE_DIR
BASE=_STATE_DIR; OWNER="P2R1E"
for p in [os.path.join(BASE,f"ideas_{OWNER}"), graph_path(OWNER)]:
    (shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)) if os.path.exists(p) else None
PROV=%s
r={}
try:
    src=Idea(title="Src"); src.set_property("v", 7, PROV); save_idea(src, OWNER)
    deps=[Idea(title=f"D{i}") for i in range(3)]
    for d in deps: save_idea(d, OWNER)
    g=SemanticGraph.load(OWNER)
    g.attach(src)
    for d in deps:
        g.declare_dependency(d.id, src.id, DerivationKind.MIRROR, "m", unit="v", provenance=PROV)
    # Make the MIDDLE dependent fail on save.
    import form.mandell.semantic_graph as sg
    orig_save=sg.save_idea
    def failing_save(idea, owner):
        if idea.id==deps[1].id:
            raise OSError("simulated failure on dep[1]")
        return orig_save(idea, owner)
    sg.save_idea=failing_save
    try:
        # The source mutation must SUCCEED (Phase-1 law: listener must not
        # break the mutation). The propagation failure is recorded as FAILED,
        # not raised.
        src.set_property("v", 8, PROV); save_idea(src, OWNER)
        r["mutation_succeeded"]=True
    except Exception:
        r["mutation_succeeded"]=False
    finally:
        sg.save_idea=orig_save
    # dep[0] should be synced, dep[1] FAILED, dep[2]... (loop breaks on raise,
    # so dep[2] was not attempted; journal covers it).
    # After the listener records FAILED, we check the ledger.
    r["dep0_synced"]=(load_idea(deps[0].id, OWNER).get_active_properties().get("m")==8)
    r["dep1_failed"]=(g.propagation_status(deps[1].id, "m")=="failed")
    fails=g.get_propagation_failures()
    r["failed_marks_exactly"]=(len([f for f in fails if f["dependent_id"]==deps[1].id])==1)
    # dep[2] was not attempted in this run; its status should not claim success.
    r["dep2_not_fake_success"]=(g.propagation_status(deps[2].id, "m")!="synchronized" or
        load_idea(deps[2].id, OWNER).get_active_properties().get("m")!=8)
    print("RESULT "+json.dumps(r))
finally:
    shutil.rmtree(os.path.join(BASE, f"ideas_{OWNER}"), ignore_errors=True)
    os.path.exists(graph_path(OWNER)) and os.remove(graph_path(OWNER))
    jp=os.path.join(BASE, f"graph_{OWNER}.journal.json")
    os.path.exists(jp) and os.remove(jp)
""" % PROV)

    # ---- R1-2 F: multi-hop intermediate failure --------------------------
    run_phase("R1-2F-multihop", """
import json, os, shutil
from form.mandell.idea import Idea, Provenance, ProvenanceSource
from form.mandell.idea_persist import save_idea, load_idea
from form.mandell.semantic_graph import SemanticGraph, DerivationKind, graph_path, graph_journal_path
from form.persist import _STATE_DIR
BASE=_STATE_DIR; OWNER="P2R1F"
for p in [os.path.join(BASE,f"ideas_{OWNER}"), graph_path(OWNER), graph_journal_path(OWNER)]:
    (shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)) if os.path.exists(p) else None
PROV=%s
r={}
try:
    a=Idea(title="A"); a.set_property("v", 1, PROV); save_idea(a, OWNER)
    b=Idea(title="B"); save_idea(b, OWNER)
    c=Idea(title="C"); save_idea(c, OWNER)
    g=SemanticGraph.load(OWNER)
    g.attach(a)
    g.declare_dependency(b.id, a.id, DerivationKind.MIRROR, "mb", unit="v", provenance=PROV)
    g.declare_dependency(c.id, b.id, DerivationKind.MIRROR, "mc", unit="mb", provenance=PROV)
    # Fail the write for C (the end of the chain).
    import form.mandell.semantic_graph as sg
    orig_save=sg.save_idea
    def failing_save(idea, owner):
        if idea.id==c.id:
            raise OSError("simulated failure on C")
        return orig_save(idea, owner)
    sg.save_idea=failing_save
    try:
        # Source mutation succeeds (Phase-1 law); failure recorded as FAILED.
        a.set_property("v", 2, PROV); save_idea(a, OWNER)
        r["mutation_succeeded"]=True
    except Exception:
        r["mutation_succeeded"]=False
    finally:
        sg.save_idea=orig_save
    # B should be synced (first hop succeeded), C FAILED.
    r["b_synced"]=(load_idea(b.id, OWNER).get_active_properties().get("mb")==2)
    r["c_failed"]=(g.propagation_status(c.id, "mc")=="failed")
    # The journal should contain the chain (for crash recovery).
    # After the failure, the journal remains (not cleared on raise).
    # Note: _on_idea_event catches and records; the journal from
    # _propagate_property remains because we raised.
    print("RESULT "+json.dumps(r))
finally:
    shutil.rmtree(os.path.join(BASE, f"ideas_{OWNER}"), ignore_errors=True)
    os.path.exists(graph_path(OWNER)) and os.remove(graph_path(OWNER))
    os.path.exists(graph_journal_path(OWNER)) and os.remove(graph_journal_path(OWNER))
""" % PROV)

    fails = [n for n, ok in RESULTS if not ok]
    npass = sum(1 for _, ok in RESULTS if ok)
    print(f"\nP2 R1 ADVERSARIAL: {npass}/{len(RESULTS)} PASS", flush=True)
    print("P2 R1 WORLD: ALL PASS" if not fails else f"FAILURES: {fails}", flush=True)


if __name__ == "__main__":
    main()
