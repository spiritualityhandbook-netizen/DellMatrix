#!/usr/bin/env python3
"""Track D planning probe — INTEGRATION level (public Program API +
canonical authorities driven directly; NOT a user/REPL path, NOT
cross-process). Runs in the nbd-omega-trackd-plan worktree whose
form/state starts empty; throwaway owner; exact cleanup at the end.

Proves, live at the planning base:
 1. A fresh Program owner has Plane units but ZERO canonical Ideas
    and an empty SemanticGraph (the two universes start unbound).
 2. The graph REFUSES to nest Plane unit ids (endpoint gate: not an
    existing idea) — the exact failure where the two systems fail
    to meet, and proof that graph-node-only binding is impossible.
 3. Nursery confirmation preserves identity into the Plane
    (unit id == proposal id).
 4. nodes_payload exposes no binding/containment field.
 5. Both candidate identity mechanics work at the canonical layer:
    (S1) an Idea minted with a fresh UUID can be nested;
    (S2) an Idea minted WITH id := unit slug can be nested.
 6. Program save/reload keeps unit ids stable and writes NO
    canonical artifacts (program persistence never touches
    ideas_<owner>/ or graph_<owner>.json content).
 7. Removing a Plane unit has no canonical effect (independent
    lifecycles today).
"""
import glob, os, sys
sys.path.insert(0, os.path.expanduser("~/workspace/nbd-omega-trackd-plan"))
os.chdir(os.path.expanduser("~/workspace/nbd-omega-trackd-plan"))

OWNER = "TrackDPlan"
checks = []
def rec(name, ok, detail=""):
    checks.append((name, bool(ok)))
    print(f"{'PASS' if ok else 'FAIL'} {name}" + (f" | {detail}" if detail else ""))

from form.persist import _STATE_DIR
def owner_files():
    out = []
    for p in glob.glob(os.path.join(_STATE_DIR, f"*{OWNER}*")):
        out.append(os.path.basename(p) + ("/" if os.path.isdir(p) else ""))
    return sorted(out)
def cleanup():
    import shutil
    n = 0
    for p in glob.glob(os.path.join(_STATE_DIR, f"*{OWNER}*")):
        if os.path.isdir(p):
            shutil.rmtree(p)
        else:
            os.remove(p)
        n += 1
    return n
cleanup()

from form.open import open_program
from form.mandell.idea import Idea, Provenance, ProvenanceSource
from form.mandell.idea_persist import save_idea, list_idea_ids, load_idea
from form.mandell.semantic_graph import SemanticGraph, GraphInvariantError

PROV = Provenance(source=ProvenanceSource.HUMAN, activity="track_d_plan_probe", agent="probe")

prog = open_program(OWNER)
plane = prog.cube.session.plane
rec("fresh program has Plane units (welcome seed)", len(plane.units) >= 1,
    f"units={sorted(plane.units)}")
rec("fresh program: ZERO canonical Ideas", list_idea_ids(OWNER) == [])
g = SemanticGraph.load(OWNER)
rec("fresh program: graph has no roots/edges", g.roots() == [])

# --- creation via the public Program surface (ids minted as Dell 8 does)
from form.idea_create import unique_unit_id
uid_house = unique_unit_id(plane.units, "House")
prog.place(uid_house, "House", words="a house", detail="container candidate")
uid_rooms = unique_unit_id(plane.units, "Rooms")
prog.place(uid_rooms, "Rooms", words="rooms inside")
rec("direct-place units carry slug ids", uid_house == "house" and uid_rooms == "rooms",
    f"{uid_house},{uid_rooms}")

# --- Nursery confirm path preserves identity
prop = prog.nursery.add("Bathroom", "bathroom words", kind="new")
# the REPL's human-approval route (repl.py:2641-2644): producer
# "repl_user" + a review context issued by this session's policy.
res = prog.confirm_proposal(
    prop.id, _producer="repl_user",
    _review_context=prog.make_review_context(prop.id, "repl_user"))
rec("confirm accepted via human-approval route", bool(res.get("ok")), str(res)[:120])
rec("confirmed unit id == proposal id", prop.id in plane.units,
    f"pid={prop.id} in units={prop.id in plane.units}")

# --- nodes_payload surface
payload = prog.nodes_payload()
keys = sorted(payload[0].keys()) if payload else []
rec("nodes_payload keys carry no binding/containment",
    not ({"idea_id", "parent", "children", "contains", "container"} & set(keys)),
    f"keys={keys}")

# --- THE GAP: nest Plane unit ids -> graph endpoint gate refuses
try:
    g.nest(uid_rooms, uid_house, PROV)
    rec("nest(unit ids) refused by endpoint gate", False, "nest unexpectedly succeeded")
except GraphInvariantError as e:
    rec("nest(unit ids) refused by endpoint gate", "not an existing idea" in str(e), str(e))

# --- S1 mechanics: UUID Idea shells nest fine
house_i = Idea(title="House"); rooms_i = Idea(title="Rooms")
save_idea(house_i, OWNER); save_idea(rooms_i, OWNER)
g.nest(rooms_i.id, house_i.id, PROV)
rec("S1 mechanics: UUID-shell Ideas nest", g.parent(rooms_i.id) == house_i.id)
g.unnest(rooms_i.id, PROV)
rec("S1 mechanics: promote restores top-level", g.parent(rooms_i.id) is None)

# --- S2 mechanics: Idea minted with id := unit slug nests fine
bath_i = Idea(idea_id=prop.id, title="Bathroom")
save_idea(bath_i, OWNER)
g.nest(prop.id, house_i.id, PROV)
rec("S2 mechanics: slug-id Idea nests by unit id", g.parent(prop.id) == house_i.id)
g.unnest(prop.id, PROV)

# --- persistence separation
before = owner_files()
prog.save()
after = owner_files()
rec("program save writes program+nursery state", any(f.startswith("program_") for f in after))
canon_before = sorted(list_idea_ids(OWNER))
from form.open import Program
prog2 = Program.load(OWNER)  # the product's restore path (repl.py:1581)
rec("reload via Program.load: unit ids stable",
    set(prog2.cube.session.plane.units) == set(plane.units),
    f"{sorted(prog2.cube.session.plane.units)}")
fresh = open_program(OWNER)
rec("fresh construct does NOT restore plane units (welcome only)",
    set(fresh.cube.session.plane.units) == {"welcome"},
    f"{sorted(fresh.cube.session.plane.units)}")
rec("canonical Ideas exist only from explicit save_idea", len(canon_before) == 3,
    f"ideas={len(canon_before)}")

# --- lifecycle independence today
prog2.cube.session.plane.remove(uid_rooms)
rec("unit removal leaves canonical side untouched",
    load_idea(rooms_i.id, OWNER).title == "Rooms" and g.parent(rooms_i.id) is None)

n_fail = sum(1 for _, ok in checks if not ok)
print(f"TOTAL {len(checks)-n_fail}/{len(checks)} PASS")
removed = cleanup()
print(f"cleanup removed {removed} owner-scoped state entries; remaining: {owner_files()}")
sys.exit(1 if n_fail else 0)
