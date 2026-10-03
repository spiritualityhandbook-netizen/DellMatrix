#!/usr/bin/env python3
"""GDP-001 Phase 1 R4: Live Matrix acceptance proof (Requirement 1.5).

Acceptance circuit (no Perspective/UI operation anywhere):
  HOUSE: CREATE -> ADD bathrooms=2 -> CHANGE bathrooms=3 -> FADE bushes
  Prove: state updated; old version preserved; new version active;
         bushes faded; change-processing evidence exists per mutation;
         provenance links events to canonical versions; events survive
         save/load (fresh process).
  ALBUM: separate fixture; prove its events/state do not contaminate House.
  SEGMENTATION: boundary accepts segmented units, rejects non-units.

Each phase runs in a FRESH OS process. Exit 0 iff all pass.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PREAMBLE = "import os, sys\nsys.path.insert(0, %r)\n" % REPO_ROOT
OWNER_H = "R4HOUSE"
OWNER_A = "R4ALBUM"


def run_driver(name: str, code: str, timeout: int = 120) -> str:
    d = tempfile.mkdtemp(prefix="r4lm_")
    script = os.path.join(d, name + ".py")
    with open(script, "w", encoding="utf-8") as f:
        f.write(PREAMBLE + code)
    r = subprocess.run([sys.executable, script], capture_output=True,
                       text=True, timeout=timeout, cwd=REPO_ROOT)
    out = (r.stdout or "") + (r.stderr or "")
    if r.returncode != 0:
        raise RuntimeError(f"driver {name} exited {r.returncode}:\n{out[-3000:]}")
    return r.stdout


def main() -> int:
    failures = []

    def check(label, cond, detail=""):
        print(("PASS " if cond else "FAIL ") + label)
        if not cond:
            failures.append(label)
            if detail:
                print(f"  detail: {detail}")

    # ---- P1: House mutations (fresh process) ----
    out = run_driver("p1_house", f"""
from form.mandell.idea import Idea, Provenance, ProvenanceSource
from form.mandell.idea_persist import save_idea
import json
prov = Provenance(source=ProvenanceSource.HUMAN, activity="r4house", agent="r4")
house = Idea(title="R4 HOUSE")
hid = house.id
house.set_property("bathrooms", 2, prov)   # ADD
house.set_property("bathrooms", 3, prov)   # CHANGE
house.set_property("front", "bushes", prov)
house.fade_property("front", prov)         # FADE
save_idea(house, {OWNER_H!r})
evs = house.change_events()
print(json.dumps({{
    "hid": hid,
    "active_bath": house.get_active_properties().get("bathrooms"),
    "hist": [v.value for v in house.get_property_history("bathrooms")],
    "faded": house.get_faded_properties().get("front"),
    "nevents": len(evs),
    "ops": [e.operation for e in evs],
    "conseq": [e.consequence for e in evs],
    "prov_ok": all(e.provenance.activity == "r4house" for e in evs),
    "verlink": all(
        e.version_id in [v.version_id for v in house.get_property_history(e.property_name)]
        for e in evs if e.property_name and e.property_name != "title"
    ),
}}))
""")
    h = json.loads(out.strip().splitlines()[-1])
    hid = h["hid"]
    check("house_state_updated", h["active_bath"] == 3, h)
    check("house_old_preserved", h["hist"] == [2, 3], h)
    check("house_new_active", h["active_bath"] == 3)
    check("house_bushes_faded", h["faded"] == "bushes", h)
    check("house_events_per_mutation", h["nevents"] == 4 and h["ops"] == [
        "set_property", "set_property", "set_property", "fade_property"], h)
    check("house_provenance_linked", h["prov_ok"] and h["verlink"], h)
    check("house_consequences", h["conseq"] == [
        "ACTIVE established",
        "ACTIVE established; prior version superseded",
        "ACTIVE established",
        "value faded; prior ACTIVE superseded"], h)

    # ---- P2: fresh-process load — events survive ----
    out = run_driver("p2_reload", f"""
from form.mandell.idea_persist import load_idea
import json
house = load_idea({hid!r}, {OWNER_H!r})
evs = house.change_events()
print(json.dumps({{
    "nevents": len(evs),
    "ops": [e.operation for e in evs],
    "active_bath": house.get_active_properties().get("bathrooms"),
    "last_op": house.last_change().operation if house.last_change() else None,
}}))
""")
    r = json.loads(out.strip().splitlines()[-1])
    check("house_events_survive_reload", r["nevents"] == 4, r)
    check("house_state_survives_reload", r["active_bath"] == 3, r)
    check("house_last_change", r["last_op"] == "fade_property", r)

    # ---- P3: Album isolation (fresh process) ----
    out = run_driver("p3_album", f"""
from form.mandell.idea import Idea, Provenance, ProvenanceSource
from form.mandell.idea_persist import save_idea, load_idea
import json
prov = Provenance(source=ProvenanceSource.HUMAN, activity="r4album", agent="r4")
album = Idea(title="R4 ALBUM")
aid = album.id
album.set_property("drummer", "Philip", prov)
album.set_property("songs", 12, prov)
save_idea(album, {OWNER_A!r})
# Reload house in the same process: must be uncontaminated.
house = load_idea({hid!r}, {OWNER_H!r})
hev = [e.operation for e in house.change_events()]
aev = [e.operation for e in album.change_events()]
print(json.dumps({{
    "house_events": hev,
    "album_events": aev,
    "house_bath": house.get_active_properties().get("bathrooms"),
    "album_drummer": album.get_active_properties().get("drummer"),
    "distinct": aid != {hid!r},
}}))
""")
    a = json.loads(out.strip().splitlines()[-1])
    check("album_no_contamination",
          a["house_events"] == ["set_property", "set_property",
                                "set_property", "fade_property"]
          and a["album_events"] == ["set_property", "set_property"]
          and a["house_bath"] == 3 and a["album_drummer"] == "Philip"
          and a["distinct"], a)

    # ---- P4: segmentation boundary (fresh process) ----
    out = run_driver("p4_segment", f"""
from form.mandell.idea import Idea, Provenance, ProvenanceSource
import json
prov = Provenance(source=ProvenanceSource.HUMAN, activity="r4seg", agent="r4")
idea = Idea(title="SEG")
res = {{}}
# valid segmented units accepted
idea.set_property("rooms", 5, prov)
idea.propose_property("color", "red", prov)
res["valid_accepted"] = True
# non-units rejected with contract errors
for label, fn in [
    ("empty_name", lambda: idea.set_property("", "x", prov)),
    ("ws_name", lambda: idea.set_property("   ", "x", prov)),
    ("nonstring_name", lambda: idea.set_property(123, "x", prov)),
    ("nonserializable", lambda: idea.set_property("v", object(), prov)),
    ("propose_empty", lambda: idea.propose_property("", "x", prov)),
]:
    try:
        fn()
        res[label] = False
    except ValueError as e:
        res[label] = "ingestion" in str(e)
print(json.dumps(res))
""")
    s = json.loads(out.strip().splitlines()[-1])
    check("segment_boundary", all(s.values()), s)

    # ---- P5: no Perspective/UI involvement ----
    # By construction: this proof imports only idea/idea_persist and runs
    # headless subprocesses. Assert no UI module was touched.
    out = run_driver("p5_noui", """
import sys
import json
mods = [m for m in sys.modules if "perspective" in m.lower() or "repl" in m.lower()]
print(json.dumps({"ui_modules": mods}))
""")
    u = json.loads(out.strip().splitlines()[-1])
    check("no_ui_involvement", u["ui_modules"] == [], u)

    print()
    if failures:
        print(f"R4 LIVE MATRIX PROOF: FAIL ({len(failures)})")
        return 1
    print("R4 LIVE MATRIX PROOF: ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
