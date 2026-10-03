#!/usr/bin/env python3
"""Public Idea Circuit — GDP-001 Phase 1, §10.

Legitimate runtime circuit:
CREATE IDEA → ADD INFORMATION → INSPECT CURRENT STATE →
SUPERSEDE INFORMATION → FADE INFORMATION → INSPECT HISTORY →
SAVE → FRESH PROCESS LOAD → INSPECT SAME IDENTITY + STATE + HISTORY + PROVENANCE.

Uses the canonical Idea architecture directly (not a demo-only API).
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import shutil

from form.mandell.idea import Idea, Provenance, ProvenanceSource, LifecycleState
from form.mandell.idea_persist import save_idea, load_idea


def run_circuit():
    """Execute the full public circuit. Returns (ok, detail)."""
    # CREATE IDEA
    idea = Idea(title="CIRCUIT TEST")
    iid = idea.id
    prov = Provenance(source=ProvenanceSource.HUMAN, activity="human_edit", agent="circuit")

    # ADD INFORMATION
    idea.set_property("color", "blue", prov)
    idea.set_property("rooms", 5, prov)

    # INSPECT CURRENT STATE
    active = idea.get_active_properties()
    assert active.get("color") == "blue", f"current state failed: {active}"

    # SUPERSEDE INFORMATION
    idea.set_property("rooms", 6, Provenance(
        source=ProvenanceSource.HUMAN, activity="supersession",
        agent="circuit", detail="5 -> 6"))

    # FADE INFORMATION
    idea.set_property("temp", "x", prov)
    idea.fade_property("temp", prov)

    # INSPECT HISTORY
    hist = idea.get_property_history("rooms")
    assert len(hist) == 2, f"history failed: {len(hist)}"

    # SAVE
    save_idea(idea)

    # FRESH PROCESS LOAD
    code = (
        "import sys\n"
        f"sys.path.insert(0, {os.getcwd()!r})\n"
        "from form.mandell.idea_persist import load_idea\n"
        f"idea = load_idea({iid!r})\n"
        "a = idea.get_active_properties()\n"
        "f = idea.get_faded_properties()\n"
        "h = idea.get_property_history('rooms')\n"
        "e = idea.explain('rooms')\n"
        "print('ID_OK=' + str(idea.id == " + repr(iid) + "))\n"
        "print('STATE_OK=' + str(a.get('rooms') == 6 and a.get('color') == 'blue'))\n"
        "print('FADED_OK=' + str(f.get('temp') == 'x'))\n"
        "print('HIST_OK=' + str(len(h) == 2))\n"
        "print('PROV_OK=' + str('supersession' in e))\n"
    )
    d = tempfile.mkdtemp()
    try:
        script = os.path.join(d, "circuit.py")
        with open(script, "w") as f:
            f.write(code)
        r = subprocess.run([sys.executable, "-B", script],
                           capture_output=True, text=True, timeout=60,
                           cwd=os.getcwd())
        ok = (
            "ID_OK=True" in r.stdout
            and "STATE_OK=True" in r.stdout
            and "FADED_OK=True" in r.stdout
            and "HIST_OK=True" in r.stdout
            and "PROV_OK=True" in r.stdout
        )
        return ok, r.stdout[-300:] + r.stderr[-200:] if not ok else ""
    finally:
        shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    ok, detail = run_circuit()
    print(f"PUBLIC IDEA CIRCUIT: {'PASS' if ok else 'FAIL'}")
    if detail:
        print(detail)
    sys.exit(0 if ok else 1)
