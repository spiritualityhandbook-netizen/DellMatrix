"""GDP-001 Phase 2 — adversarial world proof.

Attempts every forbidden graph operation; each MUST fail honestly.
Fresh processes per attack group. Owner: P2ADV (isolated; cleaned).
"""

import json
import os
import shutil
import subprocess
import sys

REPO_ROOT = os.path.expanduser("~/workspace/dellmatrix-gdp-phase1")
BASE = os.path.join(REPO_ROOT, "form", "state")
OWNER = "P2ADV"
PREAMBLE = "import os, sys\nsys.path.insert(0, %r)\n" % REPO_ROOT
PROV = ("Provenance(source=ProvenanceSource.HUMAN, activity='p2_adv', agent='p2proof')")
RESULTS = []


def run_phase(name, code):
    print(f"--- {name} ---", flush=True)
    r = subprocess.run([sys.executable, "-c", PREAMBLE + code],
                       capture_output=True, text=True, timeout=300)
    sys.stdout.write(r.stdout)
    sys.stderr.write(r.stderr)
    if r.returncode != 0:
        print(f"PHASE {name} CRASHED rc={r.returncode}", flush=True)
        RESULTS.append((name + " crashed", False))
    for line in r.stdout.splitlines():
        if line.startswith("RESULT "):
            for k, v in json.loads(line[7:]).items():
                RESULTS.append((f"{name}:{k}", bool(v)))
                if not v:
                    print(f"FAIL {name}:{k}", flush=True)


SETUP = """
from form.mandell.idea import Idea, Provenance, ProvenanceSource
from form.mandell.idea_persist import save_idea
from form.mandell.semantic_graph import SemanticGraph
OWNER="P2ADV"; PROV=%s
def I(t):
    i=Idea(title=t); save_idea(i, OWNER); return i
a=I("A"); b=I("B"); c=I("C"); d=I("D")
import json
open("/tmp/p2adv_ids.json","w").write(json.dumps({"a":a.id,"b":b.id,"c":c.id,"d":d.id}))
print("SETUP DONE")
""" % PROV


def main():
    d = os.path.join(BASE, f"ideas_{OWNER}")
    if os.path.isdir(d):
        shutil.rmtree(d)
    p = os.path.join(BASE, f"graph_{OWNER}.json")
    if os.path.isfile(p):
        os.remove(p)

    run_phase("P1-setup", SETUP)

    run_phase("P2-cycles", """
import json
from form.mandell.idea import Provenance, ProvenanceSource
from form.mandell.semantic_graph import SemanticGraph, GraphInvariantError
OWNER="P2ADV"; ids=json.load(open("/tmp/p2adv_ids.json")); PROV=%s
g=SemanticGraph.load(OWNER)
g.nest(ids["b"], ids["a"], PROV); g.nest(ids["c"], ids["b"], PROV)
r={}
try: g.nest(ids["a"], ids["c"], PROV); r["c_cycle_rejected"]=False
except GraphInvariantError: r["c_cycle_rejected"]=True
try: g.nest(ids["a"], ids["a"], PROV); r["self_rejected"]=False
except GraphInvariantError: r["self_rejected"]=True
try: g.reparent(ids["a"], ids["c"], PROV); r["reparent_cycle_rejected"]=False
except GraphInvariantError: r["reparent_cycle_rejected"]=True
r["acyclic_still"]=g.parent(ids["c"])==ids["b"] and g.parent(ids["b"])==ids["a"]
print("RESULT "+json.dumps(r))
""" % PROV)

    run_phase("P3-dangling", """
import json
from form.mandell.idea import Provenance, ProvenanceSource
from form.mandell.semantic_graph import (SemanticGraph, RelationshipType,
    GraphInvariantError, GraphValidationError)
OWNER="P2ADV"; ids=json.load(open("/tmp/p2adv_ids.json"))
PV=Provenance(source=ProvenanceSource.HUMAN, activity="p2_adv", agent="p2proof")
g=SemanticGraph.load(OWNER)
r={}
try: g.add_relationship(RelationshipType.RELATED_TO, ids["a"], "nonexistent-id", PV); r["bad_target"]=False
except GraphInvariantError: r["bad_target"]=True
try: g.add_relationship(RelationshipType.RELATED_TO, "nonexistent-id", ids["a"], PV); r["bad_source"]=False
except GraphInvariantError: r["bad_source"]=True
try: g.nest(ids["a"], "nonexistent-id", PV); r["nest_bad_parent"]=False
except GraphInvariantError: r["nest_bad_parent"]=True
try: g.add_relationship("bogus_type", ids["a"], ids["b"], PV); r["bad_type"]=False
except (GraphInvariantError, ValueError): r["bad_type"]=True
try: g.add_relationship(RelationshipType.CONTAINS, ids["a"], ids["b"], PV); r["contains_via_add"]=False
except GraphInvariantError: r["contains_via_add"]=True
# corrupt the persisted file: dangling edge -> load must fail closed
import os
from form.mandell.semantic_graph import graph_path
gp=graph_path(OWNER)
data=json.load(open(gp)); data["relationships"].append({
  "rel_id":"evil","type":"related_to","source_id":ids["a"],"target_id":"ghost",
  "props":{},"status":"active","seq":9999,"recorded_at":1.0,
  "provenance":PV.to_dict(),"cause":"x"})
json.dump(data, open(gp,"w"))
try: SemanticGraph.load(OWNER); r["dangling_load_fails_closed"]=False
except GraphValidationError: r["dangling_load_fails_closed"]=True
print("RESULT "+json.dumps(r))
""")

    run_phase("P4-duplicates", """
import json
from form.mandell.idea import Provenance, ProvenanceSource
from form.mandell.semantic_graph import (SemanticGraph, RelationshipType,
    DerivationKind, GraphInvariantError)
OWNER="P2ADV"; ids=json.load(open("/tmp/p2adv_ids.json")); PROV=%s
# restore clean graph (P3 corrupted it)
import os
from form.mandell.semantic_graph import graph_path
gp=graph_path(OWNER)
if os.path.isfile(gp): os.remove(gp)
g=SemanticGraph.load(OWNER)
r={}
e1=g.nest(ids["b"], ids["a"], PROV)
e2=g.nest(ids["b"], ids["a"], PROV)
r["dup_nest_idempotent"]=e1.rel_id==e2.rel_id and len([e for e in g._entries if e.type==RelationshipType.CONTAINS])==1
try: g.nest(ids["b"], ids["c"], PROV); r["nest_other_parent_rejected"]=False
except GraphInvariantError: r["nest_other_parent_rejected"]=True
g.reparent(ids["b"], ids["c"], PROV)
act=[e for e in g._current.values() if e.type==RelationshipType.CONTAINS and e.target_id==ids["b"] and e.status.value=="active"]
r["one_active_parent"]=len(act)==1 and act[0].source_id==ids["c"]
# duplicate DEPENDS_ON rejected (would double-propagate)
g.declare_dependency(ids["d"], ids["a"], DerivationKind.MIRROR, "m", unit="u", provenance=PROV)
try: g.declare_dependency(ids["d"], ids["a"], DerivationKind.MIRROR, "m", unit="u", provenance=PROV); r["dup_dependson_rejected"]=False
except GraphInvariantError: r["dup_dependson_rejected"]=True
# RELATED_TO allows multiples (distinguished by id)
r1=g.add_relationship(RelationshipType.RELATED_TO, ids["a"], ids["b"], PROV)
r2=g.add_relationship(RelationshipType.RELATED_TO, ids["a"], ids["b"], PROV)
r["related_multi_ok"]=r1.rel_id!=r2.rel_id
print("RESULT "+json.dumps(r))
""" % PROV)

    run_phase("P5-crossowner", """
import json
from form.mandell.idea import Idea, Provenance, ProvenanceSource
from form.mandell.idea_persist import save_idea
from form.mandell.semantic_graph import SemanticGraph, RelationshipType, GraphInvariantError
PROV=%s
outsider=Idea(title="Outsider"); save_idea(outsider, "P2OUT")
import shutil
d=os.path.join(%r, "ideas_P2OUT")
try:
    g=SemanticGraph.load("P2ADV")
    ids=json.load(open("/tmp/p2adv_ids.json"))
    try: g.nest(outsider.id, ids["a"], PROV); r={"crossowner_nest_rejected": False}
    except GraphInvariantError: r={"crossowner_nest_rejected": True}
    try: g.add_relationship(RelationshipType.RELATED_TO, ids["a"], outsider.id, PROV); r["crossowner_edge_rejected"]=False
    except GraphInvariantError: r["crossowner_edge_rejected"]=True
    print("RESULT "+json.dumps(r))
finally:
    shutil.rmtree(d, ignore_errors=True)
""" % (PROV, BASE))

    fails = [n for n, ok in RESULTS if not ok]
    npass = sum(1 for _, ok in RESULTS if ok)
    print(f"\nP2 ADVERSARIAL: {npass}/{len(RESULTS)} PASS", flush=True)
    print("P2 ADVERSARIAL WORLD: ALL PASS" if not fails else f"FAILURES: {fails}", flush=True)
    # cleanup
    d = os.path.join(BASE, f"ideas_{OWNER}")
    if os.path.isdir(d):
        shutil.rmtree(d)
    p = os.path.join(BASE, f"graph_{OWNER}.json")
    if os.path.isfile(p):
        os.remove(p)


if __name__ == "__main__":
    main()
