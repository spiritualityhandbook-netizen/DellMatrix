#!/usr/bin/env python3
"""GDP-001 Phase 1 — Canonical Idea tests.

Covers R1.1-R1.5 with House and Album fixtures.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import shutil

from form.mandell.idea import (
    Idea, Provenance, ProvenanceSource, LifecycleState, PropertyVersion,
)
from form.mandell.idea_persist import save_idea, load_idea, idea_exists

_RESULTS = []

def rec(name, ok, detail=""):
    _RESULTS.append((name, bool(ok), detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" | {detail}" if detail and not ok else ""))


def _owner():
    import uuid
    return f"P1TEST_{uuid.uuid4().hex[:8]}"


# ---------------------------------------------------------------------------
# R1.1 — Canonical Idea Object
# ---------------------------------------------------------------------------

def t_111_persistent_identity():
    """1.1.1: Identity stable across rename."""
    idea = Idea(title="Original")
    iid = idea.id
    idea.rename("Renamed")
    rec("111_identity_stable_across_rename",
        idea.id == iid and idea.title == "Renamed", "")

def t_112_core_content():
    """1.1.2: Title, properties, goals, metadata."""
    idea = Idea(title="Test")
    prov = Provenance(source=ProvenanceSource.HUMAN, activity="test", agent="t")
    idea.set_property("description", "A test idea", prov)
    idea.set_property("goals", ["goal1", "goal2"], prov)
    idea.set_property("metadata", {"key": "value"}, prov)
    active = idea.get_active_properties()
    rec("112_core_content",
        active.get("description") == "A test idea"
        and active.get("goals") == ["goal1", "goal2"]
        and active.get("metadata") == {"key": "value"}, "")

def t_113_temporal_metadata():
    """1.1.3: Creation/modification timestamps; not used as identity."""
    idea = Idea(title="Test")
    iid = idea.id
    assert idea.created_at > 0 and idea.modified_at >= idea.created_at
    # Identity is UUID, not timestamp.
    rec("113_temporal_not_identity",
        iid != str(idea.created_at) and len(iid) == 36, "")

def t_114_ownership():
    """1.1.4: Provenance distinguishes source/agent."""
    prov = Provenance(
        source=ProvenanceSource.HUMAN,
        activity="human_edit",
        agent="ace",
    )
    rec("114_ownership_distinct",
        prov.source == ProvenanceSource.HUMAN and prov.agent == "ace"
        and prov.activity == "human_edit", "")

def t_115_persistence():
    """1.1.5: Idea survives save/load."""
    idea = Idea(title="Persist")
    prov = Provenance(source=ProvenanceSource.HUMAN, activity="test", agent="t")
    idea.set_property("x", 1, prov)
    iid = idea.id
    save_idea(idea)
    loaded = load_idea(iid)
    rec("115_persistence",
        loaded.id == iid and loaded.get_active_properties().get("x") == 1, "")


# ---------------------------------------------------------------------------
# R1.2 — Lifecycle
# ---------------------------------------------------------------------------

def t_121_active():
    idea = Idea(title="T")
    prov = Provenance(source=ProvenanceSource.HUMAN, activity="t", agent="t")
    idea.set_property("a", 1, prov)
    rec("121_active", idea.get_active_properties().get("a") == 1, "")

def t_122_faded():
    """1.2.2: FADED recoverable, not deleted."""
    idea = Idea(title="T")
    prov = Provenance(source=ProvenanceSource.HUMAN, activity="t", agent="t")
    idea.set_property("a", 1, prov)
    idea.fade_property("a", prov)
    rec("122_faded_not_active",
        "a" not in idea.get_active_properties()
        and idea.get_faded_properties().get("a") == 1, "")
    # History preserved.
    hist = idea.get_property_history("a")
    rec("122_faded_history_preserved", len(hist) == 1, "")

def t_123_superseded():
    """1.2.3: Replacement preserves old/new/relationship."""
    idea = Idea(title="T")
    prov = Provenance(source=ProvenanceSource.HUMAN, activity="t", agent="t")
    idea.set_property("b", 2, prov)
    idea.set_property("b", 3, prov)
    sup = idea.get_superseded_history("b")
    rec("123_superseded",
        len(sup) == 1 and sup[0].value == 2
        and idea.get_active_properties().get("b") == 3, "")
    # Replacement link.
    active_v = [v for v in idea.get_property_history("b")
                if v.state in (LifecycleState.ACTIVE, LifecycleState.ACCEPTED)][0]
    rec("123_replacement_link",
        active_v.supersedes == sup[0].version_id
        and sup[0].superseded_by == active_v.version_id, "")

def t_124_proposed_accepted_rejected():
    """1.2.4: PROPOSED != ACCEPTED; REJECTED != ERASED."""
    idea = Idea(title="T")
    prov = Provenance(source=ProvenanceSource.HUMAN, activity="t", agent="t")
    pid = idea.propose_property("c", "maybe", prov)
    rec("124_proposed_not_active", "c" not in idea.get_active_properties(), "")
    idea.accept_proposal("c", pid, prov)
    rec("124_accepted_becomes_truth",
        idea.get_active_properties().get("c") == "maybe", "")
    pid2 = idea.propose_property("d", "nope", prov)
    idea.reject_proposal("d", pid2, prov)
    hist = idea.get_property_history("d")
    rec("124_rejected_preserved_not_erased",
        len(hist) == 1 and hist[0].state == LifecycleState.REJECTED, "")

def t_125_archive_delete_restore():
    """1.2.5: Archive/delete/restore coherent."""
    idea = Idea(title="T")
    idea.archive("done")
    rec("125_archived", idea.idea_state == LifecycleState.ARCHIVED, "")
    idea.restore("needed")
    rec("125_restored", idea.idea_state == LifecycleState.RESTORED, "")
    idea.delete("remove")
    rec("125_deleted_soft", idea.idea_state == LifecycleState.DELETED, "")
    # Restoration is history.
    rec("125_restore_is_history", len(idea._idea_state_history) == 3, "")


# ---------------------------------------------------------------------------
# R1.3 — Unit-level history
# ---------------------------------------------------------------------------

def t_131_no_destructive_overwrite():
    idea = Idea(title="T")
    prov = Provenance(source=ProvenanceSource.HUMAN, activity="t", agent="t")
    idea.set_property("x", 1, prov)
    idea.set_property("x", 2, prov)
    hist = idea.get_property_history("x")
    rec("131_no_destructive_overwrite",
        len(hist) == 2 and hist[0].value == 1 and hist[1].value == 2, "")

def t_134_query_recovery():
    idea = Idea(title="T")
    prov = Provenance(source=ProvenanceSource.HUMAN, activity="t", agent="t")
    idea.set_property("x", 1, prov)
    idea.set_property("x", 2, prov)
    idea.fade_property("x", prov)
    rec("134_query_current_empty", idea.get_active_properties().get("x") is None, "")
    rec("134_query_faded", idea.get_faded_properties().get("x") == 2, "")
    rec("134_query_history", len(idea.get_property_history("x")) == 2, "")


# ---------------------------------------------------------------------------
# R1.4 — Provenance
# ---------------------------------------------------------------------------

def t_141_source_attribution():
    for src in ProvenanceSource:
        p = Provenance(source=src, activity="t", agent="t")
        assert p.source == src
    rec("141_source_attribution", True, "")

def t_144_provenance_persistence():
    idea = Idea(title="T")
    prov = Provenance(
        source=ProvenanceSource.AI,
        activity="inference",
        agent="model-x",
        detail="derived",
    )
    idea.set_property("y", "val", prov)
    iid = idea.id
    save_idea(idea)
    loaded = load_idea(iid)
    v = loaded.get_property_history("y")[0]
    rec("144_provenance_persistence",
        v.provenance.source == ProvenanceSource.AI
        and v.provenance.agent == "model-x", "")

def t_145_explanation():
    idea = Idea(title="T")
    prov = Provenance(source=ProvenanceSource.HUMAN, activity="human_edit",
                      agent="ace", detail="because")
    idea.set_property("z", 1, prov)
    expl = idea.explain("z")
    rec("145_explanation_grounded",
        "human_edit" in expl and "ace" in expl and "because" in expl, "")


# ---------------------------------------------------------------------------
# House fixture (§8)
# ---------------------------------------------------------------------------

def t_house_fixture():
    house = Idea(title="BUILD A HOUSE")
    prov = Provenance(source=ProvenanceSource.HUMAN, activity="human_edit", agent="ace")
    house.set_property("color", "blue", prov)
    house.set_property("rooms", 5, prov)
    house.set_property("bathrooms", 2, prov)
    house.set_property("front", "bushes", prov)
    # Supersede bathrooms 2 -> 3.
    house.set_property("bathrooms", 3, Provenance(
        source=ProvenanceSource.HUMAN, activity="supersession",
        agent="ace", detail="2 superseded by 3"))
    # Fade front.
    house.fade_property("front", Provenance(
        source=ProvenanceSource.HUMAN, activity="fade", agent="ace"))
    hid = house.id
    save_idea(house)

    # Verify required truth.
    active = house.get_active_properties()
    faded = house.get_faded_properties()
    sup = house.get_superseded_history("bathrooms")
    rec("house_id_stable", bool(hid), "")
    rec("house_active",
        active.get("color") == "blue" and active.get("rooms") == 5
        and active.get("bathrooms") == 3, str(active))
    rec("house_faded", faded.get("front") == "bushes", str(faded))
    rec("house_superseded", len(sup) == 1 and sup[0].value == 2, "")
    rec("house_current_bathrooms", active.get("bathrooms") == 3, "")

    # Fresh process persistence.
    code = (
        "import sys, os\n"
        f"sys.path.insert(0, {os.getcwd()!r})\n"
        "from form.mandell.idea_persist import load_idea\n"
        f"h = load_idea({hid!r})\n"
        "a = h.get_active_properties()\n"
        "f = h.get_faded_properties()\n"
        "s = h.get_superseded_history('bathrooms')\n"
        "print('FRESH_ID=' + str(h.id == " + repr(hid) + "))\n"
        "print('FRESH_ACTIVE=' + str(a.get('bathrooms') == 3))\n"
        "print('FRESH_FADED=' + str(f.get('front') == 'bushes'))\n"
        "print('FRESH_SUP=' + str(len(s) == 1 and s[0].value == 2))\n"
    )
    d = tempfile.mkdtemp()
    try:
        script = os.path.join(d, "fresh.py")
        with open(script, "w") as f:
            f.write(code)
        r = subprocess.run([sys.executable, "-B", script],
                           capture_output=True, text=True, timeout=60,
                           cwd=os.getcwd())
        rec("house_fresh_process",
            "FRESH_ID=True" in r.stdout and "FRESH_ACTIVE=True" in r.stdout
            and "FRESH_FADED=True" in r.stdout and "FRESH_SUP=True" in r.stdout,
            r.stdout[-200:] + r.stderr[-200:])
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ---------------------------------------------------------------------------
# Album fixture (§9)
# ---------------------------------------------------------------------------

def t_album_fixture():
    album = Idea(title="MAKE AN ALBUM")
    prov = Provenance(source=ProvenanceSource.HUMAN, activity="human_edit", agent="ace")
    album.set_property("songs", 12, prov)
    album.set_property("genre", "rap", prov)
    album.set_property("song", "On My Body", prov)
    album.set_property("singer", "Jazz", prov)
    album.set_property("drummer", "Philip", prov)
    aid = album.id
    save_idea(album)
    active = album.get_active_properties()
    rec("album_active",
        active.get("songs") == 12 and active.get("genre") == "rap"
        and active.get("drummer") == "Philip", str(active))
    rec("album_id", bool(aid), "")
    # Distinct from House (no contamination) — verified in integrated proof.


_TESTS = [
    t_111_persistent_identity,
    t_112_core_content,
    t_113_temporal_metadata,
    t_114_ownership,
    t_115_persistence,
    t_121_active,
    t_122_faded,
    t_123_superseded,
    t_124_proposed_accepted_rejected,
    t_125_archive_delete_restore,
    t_131_no_destructive_overwrite,
    t_134_query_recovery,
    t_141_source_attribution,
    t_144_provenance_persistence,
    t_145_explanation,
    t_house_fixture,
    t_album_fixture,
]


def main():
    for t in _TESTS:
        try:
            t()
        except Exception as e:
            rec(t.__name__, False, f"{type(e).__name__}: {e}")
    passed = sum(1 for _, ok, _ in _RESULTS if ok)
    total = len(_RESULTS)
    print(f"\n=== P1-IDEA RESULT: {passed}/{total} PASS ===")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
