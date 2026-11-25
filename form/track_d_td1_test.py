"""Track D TD-1 — Plane Unit -> canonical Idea binding foundation.

Director ruling 2026-11-04 (PR #261, planning accepted with
amendments; TD-1 authorized as a bounded circuit; TD-2..TD-5 NOT
authorized). Contract pinned here:

  * Unit gains an optional idea_id, carried end to end: Plane.place,
    Program persist serialization/restore, legacy checkpoint files,
    BlankCube packs. Legacy state without the field loads unbound.
  * Program.bind_unit_to_idea(unit_id, subject=...) is the ONLY
    binding operation. It mints a canonical shell (fresh UUID, title
    = unit label, provenance = the real invoking subject, NO other
    content) via save_idea FIRST, writes the pointer second, then
    the normal Program save — a crash can leave an orphan shell,
    never a dangling pointer.
  * A set pointer is validated by LOADING the Idea (the Director's
    amendment: file existence is not validity). Missing -> H1
    refusal; corrupt/mismatched -> H1 refusal; another owner's Idea
    is missing for this owner. Refusals never rebind, never mint.
  * If the Program save fails after the mint, the in-memory pointer
    is rolled back and the failure reported; the shell remains as a
    census-visible orphan (canonical history is not erased).
  * A competing instance must not silently overwrite: if the
    persisted state already carries a pointer this instance does
    not hold, bind refuses with a conflict report.
  * binding_census() enumerates units/bound/unbound/invalid and
    unreferenced Ideas. Load paths never bind. TD-1 performs ZERO
    SemanticGraph writes.

Run: python3 -m form.track_d_td1_test
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}"
          + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        raise AssertionError(name)


OWNER = "Td1Probe"
OWNER2 = "Td1ProbeOther"


def _paths(owner):
    from form.persist import _STATE_DIR, _safe_owner
    safe = _safe_owner(owner)
    return {
        "program": os.path.join(_STATE_DIR, f"program_{safe}.json"),
        "ideas": os.path.join(_STATE_DIR, f"ideas_{safe}"),
        "graph": os.path.join(_STATE_DIR, f"graph_{safe}.json"),
        "state_dir": _STATE_DIR,
        "safe": safe,
    }


def _cleanup(owner):
    p = _paths(owner)
    for f in (p["program"], p["graph"]):
        if os.path.isfile(f):
            os.remove(f)
    journal = os.path.join(p["state_dir"], f"graph_{p['safe']}.journal.json")
    if os.path.isfile(journal):
        os.remove(journal)
    if os.path.isdir(p["ideas"]):
        shutil.rmtree(p["ideas"])
    # legacy checkpoint files for this owner
    for name in os.listdir(p["state_dir"]):
        if name.startswith(f"program_{p['safe']}_cp_"):
            os.remove(os.path.join(p["state_dir"], name))
    return p


def _hash(path):
    if not os.path.isfile(path):
        return None
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def run_all():
    from form.open import open_program
    from form import persist_rest
    from form.mandell import unit_binding
    from form.mandell.idea_persist import (
        load_idea, list_idea_ids, _idea_path)
    from form.mandell.runtime_observe import runtime_state

    for o in (OWNER, OWNER2):
        _cleanup(o)
    try:
        prog = open_program(OWNER)
        plane = prog.cube.session.plane
        prog.place("td1-alpha", "Alpha Binding")
        prog.place("td1-beta", "Beta Binding")
        prog.place("td1-gamma", "Gamma Binding")

        check("new units start unbound",
              all(plane.units[u].idea_id is None
                  for u in ("td1-alpha", "td1-beta", "td1-gamma")))

        # -- schema carriage: place() accepts a pointer -------------
        prog.place("td1-pre", "Prebound", idea_id="preset-id")
        check("Plane.place carries an explicit idea_id",
              plane.units["td1-pre"].idea_id == "preset-id")
        plane.units["td1-pre"].idea_id = None

        # -- persist round-trip -------------------------------------
        plane.units["td1-alpha"].idea_id = "alpha-pointer"
        path = persist_rest.save(prog)
        prog2 = persist_rest.load(OWNER, path, activate=False)
        check("persist round-trip preserves the pointer",
              prog2.cube.session.plane.units["td1-alpha"].idea_id
              == "alpha-pointer")
        plane.units["td1-alpha"].idea_id = None
        prog2.cube.session.plane.units["td1-alpha"].idea_id = None

        # -- legacy state (no idea_id key) loads unbound ------------
        persist_rest.save(prog)
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)
        for u in raw["plane"]["units"].values():
            u.pop("idea_id", None)
        legacy_path = path + ".legacy.json"
        with open(legacy_path, "w", encoding="utf-8") as f:
            json.dump(raw, f)
        prog3 = persist_rest.load(OWNER, legacy_path, activate=False)
        check("legacy state without idea_id loads unbound",
              prog3.cube.session.plane.units["td1-alpha"].idea_id is None)
        os.remove(legacy_path)

        # -- checkpoint round-trip ----------------------------------
        plane.units["td1-beta"].idea_id = "beta-pointer"
        cp = persist_rest.checkpoint(prog)
        prog4 = persist_rest.load(OWNER, cp, activate=False)
        check("checkpoint round-trip preserves the pointer",
              prog4.cube.session.plane.units["td1-beta"].idea_id
              == "beta-pointer")
        plane.units["td1-beta"].idea_id = None
        persist_rest.save(prog)

        # -- blank cube pack round-trip ------------------------------
        from form.dell_matrix.blank_cube import BlankCube
        plane.units["td1-gamma"].idea_id = "gamma-pointer"
        cube = BlankCube(owner=OWNER)
        cube.session.plane.units.clear()
        for uid, u in plane.units.items():
            cube.session.plane.place(
                uid, u.label, words=u.words, detail=u.detail,
                goals=list(u.goals), skin=u.skin, x=u.x, y=u.y,
                parents=list(u.parents), origin=u.origin,
                lineage_version=u.lineage_version, restore=True)
            cube.session.plane.units[uid].idea_id = u.idea_id
        pack = cube.export()
        packed = pack["plane"]["units"]["td1-gamma"]
        check("blank cube pack serializes the pointer",
              packed.get("idea_id") == "gamma-pointer")
        import tempfile
        with tempfile.NamedTemporaryFile(
                "w", suffix=".json", delete=False) as tf:
            json.dump(pack, tf)
            pack_path = tf.name
        loaded_cube = BlankCube.from_pack(pack_path)
        os.remove(pack_path)
        check("blank cube pack restore preserves the pointer",
              loaded_cube.session.plane.units["td1-gamma"].idea_id
              == "gamma-pointer")
        plane.units["td1-gamma"].idea_id = None
        persist_rest.save(prog)

        # -- graph silence baseline ----------------------------------
        from form.mandell.semantic_graph import SemanticGraph
        g = SemanticGraph.load(OWNER)
        g.save()
        p = _paths(OWNER)
        graph_before = (_hash(p["graph"]),
                        _hash(os.path.join(
                            p["state_dir"],
                            f"graph_{p['safe']}.journal.json")))

        # -- bind: the happy path -------------------------------------
        ideas_before = set(list_idea_ids(OWNER))
        receipt = prog.bind_unit_to_idea("td1-alpha", subject="Ace")
        alpha_id = plane.units["td1-alpha"].idea_id
        check("bind reports bound and sets the pointer",
              receipt.get("status") == "bound" and bool(alpha_id)
              and receipt.get("idea_id") == alpha_id)
        shell = load_idea(alpha_id, OWNER)
        check("shell title is the unit label, with no other content",
              shell.title == "Alpha Binding"
              and shell.get_active_properties() == {})
        events = shell.change_events()
        check("shell provenance carries the real invoking subject",
              len(events) == 1
              and events[0].operation == "bridge_bind"
              and events[0].provenance.agent == "Ace"
              and events[0].provenance.source.value == "human")
        prog5 = persist_rest.load(OWNER, path, activate=False)
        check("bind is durable across a fresh load",
              prog5.cube.session.plane.units["td1-alpha"].idea_id
              == alpha_id)

        # -- idempotency ----------------------------------------------
        receipt2 = prog.bind_unit_to_idea("td1-alpha", subject="Ace")
        check("second bind is an idempotent no-op",
              receipt2.get("status") == "already_bound"
              and set(list_idea_ids(OWNER)) - ideas_before == {alpha_id})

        # -- zero graph writes -----------------------------------------
        graph_after = (_hash(p["graph"]),
                       _hash(os.path.join(
                           p["state_dir"],
                           f"graph_{p['safe']}.journal.json")))
        check("TD-1 performs zero SemanticGraph writes",
              graph_before == graph_after)

        # -- unknown unit ----------------------------------------------
        try:
            prog.bind_unit_to_idea("td1-nope", subject="Ace")
            check("unknown unit refuses", False)
        except unit_binding.BindingRefused as e:
            check("unknown unit refuses", e.kind == "unit_not_found")

        # -- H1: pointer to a missing Idea ------------------------------
        import uuid
        ghost = str(uuid.uuid4())
        plane.units["td1-beta"].idea_id = ghost
        persist_rest.save(prog)
        n_ideas = len(list_idea_ids(OWNER))
        try:
            prog.bind_unit_to_idea("td1-beta", subject="Ace")
            check("H1 missing refuses", False)
        except unit_binding.BindingRefused as e:
            check("H1 missing refuses (no silent rebind)",
                  e.kind == "target_missing"
                  and plane.units["td1-beta"].idea_id == ghost
                  and len(list_idea_ids(OWNER)) == n_ideas)

        # -- H1: pointer to a corrupt Idea ------------------------------
        # Repair the H1 state first (clear + save): with the ghost
        # still persisted, bind would correctly refuse 'conflict'
        # before ever reaching the mint path.
        plane.units["td1-beta"].idea_id = None
        persist_rest.save(prog)
        receipt_b = prog.bind_unit_to_idea("td1-beta", subject="Ace")
        beta_id = plane.units["td1-beta"].idea_id
        with open(_idea_path(beta_id, OWNER), "w", encoding="utf-8") as f:
            f.write("{not json")
        try:
            prog.bind_unit_to_idea("td1-beta", subject="Ace")
            check("H1 corrupt refuses", False)
        except unit_binding.BindingRefused as e:
            check("H1 corrupt refuses (validated load, not existence)",
                  e.kind == "target_invalid")

        # -- wrong-owner pointer is missing for this owner --------------
        prog_other = open_program(OWNER2)
        prog_other.place("td1-x", "Other Owner Unit")
        r_other = prog_other.bind_unit_to_idea("td1-x", subject="Ace")
        foreign_id = r_other["idea_id"]
        plane.units["td1-gamma"].idea_id = foreign_id
        try:
            prog.bind_unit_to_idea("td1-gamma", subject="Ace")
            check("foreign-owner pointer refuses as missing", False)
        except unit_binding.BindingRefused as e:
            check("foreign-owner pointer refuses as missing",
                  e.kind == "target_missing")
        plane.units["td1-gamma"].idea_id = None
        persist_rest.save(prog)

        # -- save-failure rollback --------------------------------------
        real_save = persist_rest.save

        def boom(program, *a, **k):
            raise OSError("injected save failure")

        persist_rest.save = boom
        try:
            prog.bind_unit_to_idea("td1-gamma", subject="Ace")
            check("save failure is reported, not swallowed", False)
        except unit_binding.BindingFailed as e:
            orphan = e.orphan_idea_id
            check("save failure rolls the pointer back and reports "
                  "the orphan shell",
                  plane.units["td1-gamma"].idea_id is None
                  and bool(orphan)
                  and load_idea(orphan, OWNER).title == "Gamma Binding")
        finally:
            persist_rest.save = real_save
        census = prog.binding_census()
        check("census enumerates the orphan as unreferenced",
              orphan in census["unreferenced_idea_ids"])
        receipt_g = prog.bind_unit_to_idea("td1-gamma", subject="Ace")
        check("bind after recovery mints a fresh shell (orphan kept "
              "as history)",
              receipt_g.get("status") == "bound"
              and receipt_g["idea_id"] != orphan
              and orphan in prog.binding_census()["unreferenced_idea_ids"])

        # -- competing instance conflict --------------------------------
        stale = persist_rest.load(OWNER, path, activate=False)
        # stale was loaded from the same file prog just saved, so give
        # it a genuinely stale view: rewind its gamma pointer.
        stale.cube.session.plane.units["td1-gamma"].idea_id = None
        try:
            stale.bind_unit_to_idea("td1-gamma", subject="Mallory")
            check("competing instance refuses instead of overwriting",
                  False)
        except unit_binding.BindingRefused as e:
            check("competing instance refuses instead of overwriting",
                  e.kind == "conflict"
                  and e.detail.get("persisted_idea_id")
                  == receipt_g["idea_id"]
                  and stale.cube.session.plane.units["td1-gamma"].idea_id
                  is None)

        # -- census accuracy + REPL visibility ---------------------------
        census = prog.binding_census()
        check("census counts are exact",
              census["units"] >= 4 and census["bound"] == 2
              and census["invalid"] == ["td1-beta"])
        state = runtime_state(prog)
        check("runtime state exposes binding read-only",
              (state.get("binding") or {}).get("bound") == 2
              and (state.get("binding") or {}).get("status") == "known")

        # -- load never binds ---------------------------------------------
        before = len(list_idea_ids(OWNER))
        persist_rest.load(OWNER, path, activate=False)
        check("loading a program never mints or binds",
              len(list_idea_ids(OWNER)) == before)

        print(f"TD1: {sum(1 for _, c in RESULTS if c)}/{len(RESULTS)} GREEN")
    finally:
        for o in (OWNER, OWNER2):
            _cleanup(o)


def smoke() -> bool:
    try:
        run_all()
        return True
    except Exception as e:
        print(f"TD1 SMOKE FAILED: {e}")
        return False


if __name__ == "__main__":
    run_all()
    sys.exit(0)
