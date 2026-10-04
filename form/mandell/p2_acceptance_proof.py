"""GDP-001 Phase 2 — House+Album acceptance world proof.

Each phase runs in a FRESH OS process (proves cross-process truth).
Owner: P2HOUSE (isolated; probe state cleaned).

HOUSE: House > rooms > {bathroom, bedroom}; House > exterior > bushes;
       House > music studio (nested, then promoted).
ALBUM: Album > songs > {On My Body}; Album > people > {Jazz, Philip}.

Demonstrates all 15 acceptance criteria from the Phase-2 directive.
"""

import json
import os
import shutil
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = os.path.join(REPO_ROOT, "form", "state")
OWNER = "P2HOUSE"
PREAMBLE = "import os, sys\nsys.path.insert(0, %r)\n" % REPO_ROOT
PROV = (
    "Provenance(source=ProvenanceSource.HUMAN, activity='p2_accept', "
    "agent='p2proof')"
)

RESULTS = []


def check(name, cond):
    RESULTS.append((name, bool(cond)))
    print(("PASS " if cond else "FAIL ") + name, flush=True)


def run_phase(name, code):
    print(f"--- {name} ---", flush=True)
    full = PREAMBLE + code
    r = subprocess.run([sys.executable, "-c", full], capture_output=True,
                       text=True, timeout=300)
    sys.stdout.write(r.stdout)
    sys.stderr.write(r.stderr)
    if r.returncode != 0:
        print(f"PHASE {name} CRASHED rc={r.returncode}", flush=True)
        RESULTS.append((name + " crashed", False))
    for line in r.stdout.splitlines():
        if line.startswith("RESULT "):
            try:
                data = json.loads(line[len("RESULT "):])
            except Exception:
                RESULTS.append((name + " bad RESULT json", False))
                continue
            for k, v in data.items():
                RESULTS.append((f"{name}:{k}", bool(v)))
                if not v:
                    print(f"FAIL {name}:{k}", flush=True)


SETUP = """
from form.mandell.idea import Idea, Provenance, ProvenanceSource
from form.mandell.idea_persist import save_idea, load_idea
from form.mandell.semantic_graph import (SemanticGraph, RelationshipType,
    DerivationKind, GraphInvariantError)
import json
OWNER = "P2HOUSE"
PROV = %s
def I(title):
    i = Idea(title=title); save_idea(i, OWNER); return i
house = I("House"); rooms = I("Rooms"); bath = I("Bathroom")
bed = I("Bedroom"); ext = I("Exterior"); bushes = I("Bushes")
studio = I("Music Studio")
album = I("Album"); songs = I("Songs"); omb = I("On My Body")
people = I("People"); jazz = I("Jazz"); philip = I("Philip")
g = SemanticGraph.load(OWNER)
for _i in (house, rooms, bath, bed, ext, bushes, studio, album, songs, omb, people, jazz, philip):
    g.attach(_i)
# 4. Music Studio begins nested in House
g.nest(rooms.id, house.id, PROV); g.nest(bath.id, rooms.id, PROV)
g.nest(bed.id, rooms.id, PROV); g.nest(ext.id, house.id, PROV)
g.nest(bushes.id, ext.id, PROV); g.nest(studio.id, house.id, PROV)
g.nest(songs.id, album.id, PROV); g.nest(omb.id, songs.id, PROV)
g.nest(people.id, album.id, PROV); g.nest(jazz.id, people.id, PROV)
g.nest(philip.id, people.id, PROV)
# 5. legitimate cross-link: Music Studio -> Album
g.add_relationship(RelationshipType.RELATED_TO, studio.id, album.id, PROV, cause="accept:cross-link")
# 11/12. dependency: Studio.setlist mirrors Album.songs_list
album.set_property("songs_list", ["On My Body"], PROV); save_idea(album, OWNER)
g.declare_dependency(studio.id, album.id, DerivationKind.MIRROR, "setlist", unit="songs_list", provenance=PROV)
ids = {n: v.id for n, v in [("house",house),("rooms",rooms),("bath",bath),("bed",bed),("ext",ext),("bushes",bushes),("studio",studio),("album",album),("songs",songs),("omb",omb),("people",people),("jazz",jazz),("philip",philip)]}
open("/tmp/p2house_ids.json","w").write(json.dumps(ids))
print("SETUP DONE")
""" % PROV


def _wipe():
    d = os.path.join(BASE, f"ideas_{OWNER}")
    if os.path.isdir(d):
        shutil.rmtree(d)
    for fn in os.listdir(BASE):
        if OWNER in fn:
            fp = os.path.join(BASE, fn)
            if os.path.isfile(fp):
                os.remove(fp)
            elif os.path.isdir(fp):
                shutil.rmtree(fp)
    if os.path.isfile("/tmp/p2house_ids.json"):
        os.remove("/tmp/p2house_ids.json")


def main():
    _wipe()

    run_phase("P1-setup", SETUP)

    # P2: criteria 1-10 (fresh process)
    run_phase("P2-structure", PREAMBLE + """
import json
from form.mandell.idea import Idea, Provenance, ProvenanceSource
from form.mandell.idea_persist import load_idea
from form.mandell.semantic_graph import SemanticGraph, RelationshipType
OWNER="P2HOUSE"; ids=json.load(open("/tmp/p2house_ids.json"))
g = SemanticGraph.load(OWNER)
H,A,B,S = ids["house"], ids["album"], ids["bath"], ids["studio"]
print("RESULT " + json.dumps({
  "c1_depth": g.breadcrumb(ids["bushes"]) == [H, ids["ext"], ids["bushes"]],
  "c2_arb": len(g.ancestors(ids["omb"])) == 2 and g.breadcrumb(ids["omb"])[0] == A,
  "c3_independent": g.parent(H) is None and g.parent(A) is None and H != A,
  "c4_nested": g.parent(S) == H,
  "c5_crosslink": any(e.target_id==A and e.type==RelationshipType.RELATED_TO for e in g.outgoing(S)),
  "c10_no_coexist": all(e.target_id!=H for e in g.outgoing(A)) and all(e.target_id!=A for e in g.outgoing(H) if e.type!=RelationshipType.CONTAINS),
  "desc_house": sorted(g.descendants(H)) == sorted([ids["rooms"],ids["bath"],ids["bed"],ids["ext"],ids["bushes"],S]),
}))
""")

    # P3: promote (criteria 6-9), fresh process
    run_phase("P3-promote", PREAMBLE + """
import json
from form.mandell.idea import Provenance, ProvenanceSource
from form.mandell.idea_persist import load_idea
from form.mandell.semantic_graph import SemanticGraph, RelationshipType, RelationshipStatus
OWNER="P2HOUSE"; ids=json.load(open("/tmp/p2house_ids.json"))
PROV = %s
g = SemanticGraph.load(OWNER)
S,H,A = ids["studio"], ids["house"], ids["album"]
before = load_idea(S, OWNER)
n_events_before = len(before.change_events())
props_before = dict(before.get_active_properties())
g.unnest(S, PROV)
after = load_idea(S, OWNER)
hist = [e for e in g._entries if e.type==RelationshipType.CONTAINS and e.target_id==S]
print("RESULT " + json.dumps({
  "c6_top": g.is_top_level(S),
  "c7_id": after.id == S,
  "c8_history": any(e.source_id==H and e.status==RelationshipStatus.SUPERSEDED for e in hist),
  "c8_events_kept": len(after.change_events()) == n_events_before,
  "c8_props_kept": after.get_active_properties().get("setlist") == props_before.get("setlist"),
  "c9_crosslink": any(e.target_id==A and e.status==RelationshipStatus.ACTIVE for e in g.outgoing(S)),
}))
""" % PROV)

    # P4: propagation (criteria 11-12), fresh process
    run_phase("P4-propagate", PREAMBLE + """
import json
from form.mandell.idea import Provenance, ProvenanceSource
from form.mandell.idea_persist import load_idea, save_idea
from form.mandell.semantic_graph import SemanticGraph
OWNER="P2HOUSE"; ids=json.load(open("/tmp/p2house_ids.json"))
PROV = %s
g = SemanticGraph.load(OWNER)
A,S,H = ids["album"], ids["studio"], ids["house"]
alb = load_idea(A, OWNER); g.attach(alb)
house_before = dict(load_idea(H, OWNER).get_active_properties())
alb.set_property("songs_list", ["On My Body", "Second Song"], PROV); save_idea(alb, OWNER)
std = load_idea(S, OWNER)
house_after = load_idea(H, OWNER)
print("RESULT " + json.dumps({
  "c11_propagated": std.get_active_properties().get("setlist") == ["On My Body", "Second Song"],
  "c11_evidence": std.last_change() is not None and std.last_change().provenance.activity == "dependency_propagation",
  "c12_untouched": dict(house_after.get_active_properties()) == house_before,
}))
""" % PROV)

    # P5: save/load + fresh-process identical truth (criteria 13, 15)
    run_phase("P5-reload", PREAMBLE + """
import json
from form.mandell.semantic_graph import SemanticGraph, RelationshipType, RelationshipStatus
OWNER="P2HOUSE"; ids=json.load(open("/tmp/p2house_ids.json"))
g = SemanticGraph.load(OWNER)
H,S,A = ids["house"], ids["studio"], ids["album"]
hist = [e for e in g._entries if e.type==RelationshipType.CONTAINS and e.target_id==S]
print("RESULT " + json.dumps({
  "c13_parent": g.parent(ids["bath"]) == ids["rooms"],
  "c13_top": g.is_top_level(S),
  "c13_history": any(e.source_id==H and e.status==RelationshipStatus.SUPERSEDED for e in hist),
  "c13_crosslink": any(e.target_id==A and e.status==RelationshipStatus.ACTIVE for e in g.outgoing(S)),
  "c15_desc": len(g.descendants(H)) == 5,
}))
""")

    # P6: checkpoint/rollback preserves graph coherently (criterion 14)
    run_phase("P6-checkpoint", PREAMBLE + """
import json
from form.open import open_program
from form.mandell.language import bind
from form.mandell import checkpoint_generation as CG
from form.mandell.core_i_recovery import rollback
from form.mandell.idea import Idea, Provenance, ProvenanceSource
from form.mandell.idea_persist import save_idea
from form.mandell.semantic_graph import SemanticGraph, RelationshipType
OWNER="P2HOUSE"; ids=json.load(open("/tmp/p2house_ids.json"))
PROV = %s
p = open_program(OWNER); bind(p)
g = SemanticGraph.load(OWNER)
# mutate AFTER checkpoint: nest a new idea, then roll back
nb = Idea(title="NewBath"); save_idea(nb, OWNER)
r1 = CG.commit_checkpoint(p)
n_before = len([e for e in g._entries if e.status.value=="active"])
g.nest(nb.id, ids["rooms"], PROV)
assert g.parent(nb.id) == ids["rooms"]
rollback(OWNER)
g2 = SemanticGraph.load(OWNER)
n_after = len([e for e in g2._entries if e.status.value=="active"])
print("RESULT " + json.dumps({
  "c14_rolled_back": g2.parent(nb.id) is None,
  "c14_count": n_after == n_before,
  "c14_promotion_kept": g2.is_top_level(ids["studio"]),
  "c14_crosslink_kept": any(e.target_id==ids["album"] and e.status.value=="active" for e in g2.outgoing(ids["studio"])),
}))
""" % PROV)

    # collect RESULT lines
    fails = [n for n, ok in RESULTS if not ok]
    npass = sum(1 for _, ok in RESULTS if ok)
    print(f"\nP2 ACCEPTANCE: {npass}/{len(RESULTS)} PASS", flush=True)
    if fails:
        print("FAILURES:", fails, flush=True)
    else:
        print("P2 HOUSE+ALBUM WORLD: ALL PASS", flush=True)
    # cleanup probe state (ideas, graph, program, nursery, checkpoints)
    _wipe()


if __name__ == "__main__":
    main()
