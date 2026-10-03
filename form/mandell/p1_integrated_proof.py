#!/usr/bin/env python3
"""Phase-1 Integrated Proof — GDP-001 §21.

Exercises: HOUSE IDEA + ALBUM IDEA + STABLE IDENTITY + ACTIVE STATE +
SUPERSESSION + FADE + HISTORY + PROVENANCE + SAVE/LOAD +
FRESH PROCESS + PERSPECTIVE-INDEPENDENT PROCESSING +
OBSERVABLE STATE.

Note: Checkpoint/rollback integration with Phase-0 generations is
future work (see migration matrix). This proof covers save/load
persistence across fresh processes.

Verifies House and Album remain distinct (no cross-contamination).
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import shutil

from form.mandell.idea import Idea, Provenance, ProvenanceSource
from form.mandell.idea_persist import save_idea, load_idea

_RESULTS = []

def rec(name, ok, detail=""):
    _RESULTS.append((name, bool(ok)))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" | {detail}" if detail and not ok else ""))


def main():
    prov = Provenance(source=ProvenanceSource.HUMAN, activity="human_edit", agent="ace")

    # HOUSE
    house = Idea(title="BUILD A HOUSE")
    house.set_property("color", "blue", prov)
    house.set_property("rooms", 5, prov)
    house.set_property("bathrooms", 2, prov)
    house.set_property("front", "bushes", prov)
    house.set_property("bathrooms", 3, Provenance(
        source=ProvenanceSource.HUMAN, activity="supersession",
        agent="ace", detail="2->3"))
    house.fade_property("front", Provenance(
        source=ProvenanceSource.HUMAN, activity="fade", agent="ace"))
    hid = house.id
    save_idea(house)

    # ALBUM
    album = Idea(title="MAKE AN ALBUM")
    album.set_property("songs", 12, prov)
    album.set_property("genre", "rap", prov)
    album.set_property("song", "On My Body", prov)
    album.set_property("singer", "Jazz", prov)
    album.set_property("drummer", "Philip", prov)
    aid = album.id
    save_idea(album)

    # Distinct identities.
    rec("integrated_distinct_ids", hid != aid, "")

    # No cross-contamination (in-memory).
    h_active = house.get_active_properties()
    a_active = album.get_active_properties()
    rec("integrated_no_contamination",
        "drummer" not in h_active and "bathrooms" not in a_active, "")

    # Fresh process: both load correctly and remain distinct.
    code = (
        "import sys\n"
        f"sys.path.insert(0, {os.getcwd()!r})\n"
        "from form.mandell.idea_persist import load_idea\n"
        f"h = load_idea({hid!r})\n"
        f"a = load_idea({aid!r})\n"
        "ha = h.get_active_properties()\n"
        "aa = a.get_active_properties()\n"
        "hf = h.get_faded_properties()\n"
        "hs = h.get_superseded_history('bathrooms')\n"
        "print('HOUSE_OK=' + str(ha.get('bathrooms') == 3 and hf.get('front') == 'bushes' and len(hs) == 1))\n"
        "print('ALBUM_OK=' + str(aa.get('drummer') == 'Philip' and aa.get('songs') == 12))\n"
        "print('DISTINCT_OK=' + str(h.id != a.id))\n"
        "print('PROV_OK=' + str('supersession' in h.explain('bathrooms')))\n"
    )
    d = tempfile.mkdtemp()
    try:
        script = os.path.join(d, "integrated.py")
        with open(script, "w") as f:
            f.write(code)
        r = subprocess.run([sys.executable, "-B", script],
                           capture_output=True, text=True, timeout=60,
                           cwd=os.getcwd())
        rec("integrated_fresh_house",
            "HOUSE_OK=True" in r.stdout, r.stdout[-200:])
        rec("integrated_fresh_album",
            "ALBUM_OK=True" in r.stdout, r.stdout[-200:])
        rec("integrated_fresh_distinct",
            "DISTINCT_OK=True" in r.stdout, r.stdout[-200:])
        rec("integrated_fresh_provenance",
            "PROV_OK=True" in r.stdout, r.stdout[-200:])
    finally:
        shutil.rmtree(d, ignore_errors=True)

    passed = sum(1 for _, ok in _RESULTS if ok)
    total = len(_RESULTS)
    print(f"\n=== P1 INTEGRATED PROOF: {passed}/{total} PASS ===")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
