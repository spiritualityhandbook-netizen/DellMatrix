"""Track D TD-2 — canonical Idea containment operations.

Director directive 2026-11-04 (Mode D review, Water + TD-1-R2):
TD-2 is containment operations — nest / promote / reparent at
Program level through canonical Unit->Idea bindings, REPL first;
SemanticGraph remains the sole containment authority. Contract
pinned here:

  * Program.nest_units / promote_unit / reparent_unit /
    containment_view (form/mandell/unit_containment.py). Ops take
    UNIT ids and a real invoking subject; bindings are lazy via
    the TD-1 protocol (shell saved before pointer; no rebind).
  * Mutations require both endpoint Ideas to load validly and be
    LifecycleState.ACTIVE (TD4); missing/corrupt pointers refuse
    as target_missing / target_invalid with no silent replacement.
  * Sandbox isolation (TD7): endpoints whose isolation keys
    (sandboxed, sandbox_id) differ refuse BEFORE any mint. A
    MALFORMED sandboxed endpoint (sandboxed with a missing or
    empty sandbox_id) refuses outright regardless of the other
    endpoint — two malformed units key identically (F1 repair,
    Director review 2026-11-04).
  * Single parent: nest under a different parent refuses
    (second_parent) — moving requires explicit reparent. Same
    parent nest is idempotent. Self-nest and cycles refuse.
  * Promote supersedes the active CONTAINS edge; history is
    preserved in the persisted graph log; unit and Idea identities
    never change. Promote of an unbound unit mints nothing.
  * Failures after a lazy mint disclose partial_bindings; a failed
    graph save leaves the persisted graph unchanged and a retry
    converges. A stale instance refuses via the TD-1 conflict
    rule instead of overwriting a binding.
  * containment_view is a derived read (no mint, no store):
    parent / children / ancestors resolved back to units, read
    from a freshly loaded graph every call. NO containment state
    is persisted on the Plane or the Program.
  * REPL surface: nest <child> under <parent> | promote <unit> |
    reparent <child> to <parent> | containment <unit>, with every
    refusal printed (kind + message), never invisible.

Run: python3 -m form.track_d_td2_test
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import uuid

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}"
          + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        raise AssertionError(name)


OWNER = "Td2Probe"


def _paths(owner):
    from form.persist import _STATE_DIR, _safe_owner
    safe = _safe_owner(owner)
    return {
        "program": os.path.join(_STATE_DIR, f"program_{safe}.json"),
        "ideas": os.path.join(_STATE_DIR, f"ideas_{safe}"),
        "graph": os.path.join(_STATE_DIR, f"graph_{safe}.json"),
        "graph_journal": os.path.join(
            _STATE_DIR, f"graph_{safe}.journal.json"),
        "lock": os.path.join(_STATE_DIR, ".locks",
                             f"program_{safe}.json.lock"),
        "state_dir": _STATE_DIR,
        "safe": safe,
    }


def _cleanup(owner):
    p = _paths(owner)
    for f in (p["program"], p["graph"], p["graph_journal"], p["lock"]):
        if os.path.isfile(f):
            os.remove(f)
    if os.path.isdir(p["ideas"]):
        shutil.rmtree(p["ideas"])
    for name in os.listdir(p["state_dir"]):
        if name.startswith(f"program_{p['safe']}_cp_"):
            os.remove(os.path.join(p["state_dir"], name))
    return p


def _graph_log(owner):
    p = _paths(owner)
    if not os.path.isfile(p["graph"]):
        return []
    with open(p["graph"], encoding="utf-8") as f:
        return json.load(f).get("relationships", [])


def run_all():
    from form.open import open_program
    from form import persist_rest
    from form.mandell import unit_containment as uc
    from form.mandell.idea_persist import load_idea, list_idea_ids, save_idea
    from form.mandell.semantic_graph import SemanticGraph

    _cleanup(OWNER)
    try:
        prog = open_program(OWNER)
        plane = prog.cube.session.plane
        for uid, label in (
                ("td2-house", "House"), ("td2-rooms", "Rooms"),
                ("td2-bed", "Bed"), ("td2-garage", "Garage"),
                ("td2-loose", "Loose"), ("td2-arch", "Archived One"),
                ("td2-ghost", "Ghost"), ("td2-sb-a", "Sandboxed A"),
                ("td2-sb-b", "Sandboxed B"), ("td2-fragile", "Fragile"),
                ("td2-fragile-p", "Fragile Parent")):
            prog.place(uid, label)

        # -- lazy binding + nest --------------------------------------
        r = prog.nest_units("td2-rooms", "td2-house", subject="Ace")
        rooms_id = plane.units["td2-rooms"].idea_id
        house_id = plane.units["td2-house"].idea_id
        check("nest lazy-binds both units and reports nested",
              r.get("status") == "nested" and bool(rooms_id)
              and bool(house_id) and r.get("child_idea_id") == rooms_id
              and r.get("parent_idea_id") == house_id)
        edge_prov = [e for e in _graph_log(OWNER)
                     if e["type"] == "contains"
                     and e["target_id"] == rooms_id]
        check("graph edge provenance carries the real subject",
              len(edge_prov) == 1
              and edge_prov[0]["provenance"]["agent"] == "Ace"
              and edge_prov[0]["provenance"]["source"] == "human")

        # -- three levels + ancestry -----------------------------------
        prog.nest_units("td2-bed", "td2-rooms", subject="Ace")
        bed_id = plane.units["td2-bed"].idea_id
        view = prog.containment_view("td2-bed")
        check("three-level ancestry resolves to units root-first",
              [a["unit_id"] for a in view["ancestors"]]
              == ["td2-house", "td2-rooms"]
              and view["parent_unit_id"] == "td2-rooms"
              and view["idea_id"] == bed_id)
        g = SemanticGraph.load(OWNER)
        check("graph is the authority (breadcrumb agrees)",
              g.breadcrumb(bed_id) == [house_id, rooms_id, bed_id]
              and g.children(house_id) == [rooms_id])

        # -- idempotent nest --------------------------------------------
        n_entries = len(_graph_log(OWNER))
        r2 = prog.nest_units("td2-rooms", "td2-house", subject="Ace")
        check("same-parent nest is an idempotent no-op",
              r2.get("status") == "already_nested"
              and len(_graph_log(OWNER)) == n_entries)

        # -- second parent refuses; explicit reparent moves ------------
        try:
            prog.nest_units("td2-rooms", "td2-garage", subject="Ace")
            check("second parent refuses", False)
        except uc.ContainmentRefused as e:
            check("second parent refuses without explicit reparent",
                  e.kind == "second_parent"
                  and SemanticGraph.load(OWNER).parent(rooms_id) == house_id)
        rp = prog.reparent_unit("td2-rooms", "td2-garage", subject="Ace")
        garage_id = plane.units["td2-garage"].idea_id
        check("reparent retains both identities and moves the child",
              rp.get("status") == "reparented"
              and plane.units["td2-rooms"].idea_id == rooms_id
              and SemanticGraph.load(OWNER).parent(rooms_id) == garage_id)
        hist = [e for e in _graph_log(OWNER)
                if e["type"] == "contains" and e["target_id"] == rooms_id
                and e["source_id"] == house_id
                and e["status"] == "superseded"]
        check("reparent preserves the historical edge as superseded",
              len(hist) == 1)
        # move it back for the promote checks
        prog.reparent_unit("td2-rooms", "td2-house", subject="Ace")

        # -- promote ------------------------------------------------------
        pr = prog.promote_unit("td2-rooms", subject="Ace")
        check("promote retains identities, drops the active parent, "
              "keeps history",
              pr.get("status") == "promoted"
              and plane.units["td2-rooms"].idea_id == rooms_id
              and SemanticGraph.load(OWNER).parent(rooms_id) is None
              and any(e["type"] == "contains"
                      and e["target_id"] == rooms_id
                      and e["status"] == "superseded"
                      for e in _graph_log(OWNER)))
        check("promoted child's own subtree is untouched",
              SemanticGraph.load(OWNER).parent(bed_id) == rooms_id)
        n_ideas = len(list_idea_ids(OWNER))
        pr2 = prog.promote_unit("td2-loose", subject="Ace")
        check("promote of an unbound unit mints nothing",
              pr2.get("status") == "already_top_level"
              and plane.units["td2-loose"].idea_id is None
              and len(list_idea_ids(OWNER)) == n_ideas)

        # -- self + cycle ---------------------------------------------------
        try:
            prog.nest_units("td2-house", "td2-house", subject="Ace")
            check("self-nest refuses", False)
        except uc.ContainmentRefused as e:
            check("self-nest refuses", e.kind == "self_containment")
        prog.nest_units("td2-rooms", "td2-house", subject="Ace")
        try:
            prog.nest_units("td2-house", "td2-bed", subject="Ace")
            check("cycle refuses", False)
        except uc.ContainmentRefused as e:
            check("cycle refuses", e.kind == "cycle")

        # -- sandbox isolation ---------------------------------------------
        plane.box(["td2-sb-a"], sandbox_id="sb-one")
        n_ideas = len(list_idea_ids(OWNER))
        try:
            prog.nest_units("td2-sb-a", "td2-house", subject="Ace")
            check("cross-sandbox nest refuses", False)
        except uc.ContainmentRefused as e:
            check("cross-sandbox nest refuses BEFORE any mint",
                  e.kind == "sandbox_boundary"
                  and plane.units["td2-sb-a"].idea_id is None
                  and len(list_idea_ids(OWNER)) == n_ideas)
        plane.box(["td2-sb-b"], sandbox_id="sb-one")
        rsb = prog.nest_units("td2-sb-b", "td2-sb-a", subject="Ace")
        check("same-sandbox nest is allowed", rsb.get("status") == "nested")
        plane.box(["td2-sb-b"], sandbox_id="sb-two")
        # sb-b already nested under sb-a in sb-one; moving its sandbox
        # must not retroactively matter — a NEW cross-boundary op refuses:
        try:
            prog.reparent_unit("td2-sb-b", "td2-house", subject="Ace")
            check("cross-sandbox reparent refuses", False)
        except uc.ContainmentRefused as e:
            check("cross-sandbox reparent refuses",
                  e.kind == "sandbox_boundary")
        plane.unbox("td2-sb-a")
        plane.unbox("td2-sb-b")

        # -- F1: malformed sandboxed endpoints refuse (Director
        # review 2026-11-04) — sandboxed with a missing/empty id
        # keys as (True, None); two such units compare EQUAL, so
        # key equality alone let them nest. Any malformed endpoint
        # must refuse before mint, regardless of the other side.
        for uid, label in (("td2-f1-a", "F1 A"), ("td2-f1-b", "F1 B"),
                           ("td2-f1-empty", "F1 Empty"),
                           ("td2-f1-valid", "F1 Valid")):
            prog.place(uid, label)
        for uid in ("td2-f1-a", "td2-f1-b"):
            plane.units[uid].sandboxed = True
            plane.units[uid].sandbox_id = None
        plane.units["td2-f1-empty"].sandboxed = True
        plane.units["td2-f1-empty"].sandbox_id = ""
        plane.box(["td2-f1-valid"], sandbox_id="sb-ok")
        n_ideas = len(list_idea_ids(OWNER))
        n_graph = len(_graph_log(OWNER))

        def _f1_clean():
            return (len(list_idea_ids(OWNER)) == n_ideas
                    and len(_graph_log(OWNER)) == n_graph
                    and all(plane.units[u].idea_id is None for u in
                            ("td2-f1-a", "td2-f1-b", "td2-f1-empty",
                             "td2-f1-valid")))

        try:
            prog.nest_units("td2-f1-a", "td2-f1-b", subject="Ace")
            check("F1 both-malformed nest refuses", False)
        except uc.ContainmentRefused as e:
            check("F1 both-malformed nest refuses BEFORE any mint",
                  e.kind == "sandbox_boundary" and _f1_clean())
        try:
            prog.nest_units("td2-f1-empty", "td2-house", subject="Ace")
            check("F1 empty-string sandbox id refuses", False)
        except uc.ContainmentRefused as e:
            check("F1 empty-string sandbox id refuses BEFORE any mint",
                  e.kind == "sandbox_boundary" and _f1_clean())
        try:
            prog.nest_units("td2-f1-valid", "td2-f1-a", subject="Ace")
            check("F1 mixed valid/malformed nest refuses", False)
        except uc.ContainmentRefused as e:
            check("F1 mixed valid/malformed nest refuses BEFORE mint",
                  e.kind == "sandbox_boundary" and _f1_clean())
        try:
            prog.reparent_unit("td2-f1-a", "td2-f1-valid", subject="Ace")
            check("F1 malformed reparent refuses", False)
        except uc.ContainmentRefused as e:
            check("F1 malformed reparent refuses BEFORE any mint",
                  e.kind == "sandbox_boundary" and _f1_clean())
        # same-valid-sandbox behavior is preserved (covered above by
        # td2-sb-a/td2-sb-b); malformed units unboxed nest normally:
        for uid in ("td2-f1-a", "td2-f1-b", "td2-f1-empty"):
            plane.units[uid].sandboxed = False
            plane.units[uid].sandbox_id = None
        rf1 = prog.nest_units("td2-f1-a", "td2-f1-b", subject="Ace")
        check("F1 units nest normally once unboxed",
              rf1.get("status") == "nested")

        # -- lifecycle: non-ACTIVE Ideas refuse ------------------------------
        prog.bind_unit_to_idea("td2-arch", subject="Ace")
        arch = load_idea(plane.units["td2-arch"].idea_id, OWNER)
        arch.archive("td2 test")
        save_idea(arch, OWNER)
        try:
            prog.nest_units("td2-arch", "td2-house", subject="Ace")
            check("archived child refuses", False)
        except uc.ContainmentRefused as e:
            check("archived child refuses (idea_not_active)",
                  e.kind == "idea_not_active")

        # -- H1: missing / corrupt pointers refuse, never rebind -------------
        ghost = str(uuid.uuid4())
        plane.units["td2-ghost"].idea_id = ghost
        persist_rest.save(prog)
        n_ideas = len(list_idea_ids(OWNER))
        try:
            prog.nest_units("td2-ghost", "td2-house", subject="Ace")
            check("missing target refuses", False)
        except uc.ContainmentRefused as e:
            check("missing target refuses with no silent rebind",
                  e.kind == "target_missing"
                  and plane.units["td2-ghost"].idea_id == ghost
                  and len(list_idea_ids(OWNER)) == n_ideas)
        plane.units["td2-ghost"].idea_id = None
        persist_rest.save(prog)
        prog.bind_unit_to_idea("td2-ghost", subject="Ace")
        from form.mandell.idea_persist import _idea_path
        with open(_idea_path(plane.units["td2-ghost"].idea_id, OWNER),
                  "w", encoding="utf-8") as f:
            f.write("{not json")
        try:
            prog.nest_units("td2-ghost", "td2-house", subject="Ace")
            check("corrupt target refuses", False)
        except uc.ContainmentRefused as e:
            check("corrupt target refuses (validated load)",
                  e.kind == "target_invalid")
        plane.units["td2-ghost"].idea_id = None
        persist_rest.save(prog)

        # -- graph failure: partial bindings disclosed, retry converges ------
        real_save = SemanticGraph.save

        def boom(self):
            raise OSError("injected graph save failure")

        SemanticGraph.save = boom
        try:
            prog.nest_units("td2-fragile", "td2-fragile-p", subject="Ace")
            check("graph failure is reported", False)
        except uc.ContainmentFailed as e:
            partial = e.detail.get("partial_bindings") or []
            check("graph failure discloses the partial bindings and "
                  "leaves the persisted graph unchanged",
                  len(partial) == 2
                  and SemanticGraph.load(OWNER).parent(
                      plane.units["td2-fragile"].idea_id) is None)
        finally:
            SemanticGraph.save = real_save
        rr = prog.nest_units("td2-fragile", "td2-fragile-p", subject="Ace")
        check("retry after graph failure converges",
              rr.get("status") == "nested")

        # -- stale instance cannot overwrite a binding ------------------------
        prog.place("td2-stale", "Stale Target")
        persist_rest.save(prog)
        path = _paths(OWNER)["program"]
        stale = persist_rest.load(OWNER, path, activate=False)
        prog.nest_units("td2-stale", "td2-house", subject="Ace")
        try:
            stale.nest_units("td2-stale", "td2-garage", subject="Mallory")
            check("stale instance refuses", False)
        except uc.ContainmentRefused as e:
            check("stale instance refuses instead of overwriting",
                  e.kind == "conflict"
                  and SemanticGraph.load(OWNER).parent(
                      plane.units["td2-stale"].idea_id) == house_id)

        # -- no second store ---------------------------------------------------
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)
        keys = set()
        for u in raw["plane"]["units"].values():
            keys |= set(u.keys())
        check("persisted units carry no containment store "
              "(pointer only)",
              keys <= {"id", "label", "words", "detail", "goals", "skin",
                       "x", "y", "sandboxed", "sandbox_id", "manifest",
                       "parents", "origin", "lineage_version", "idea_id"})
        check("lineage parents are untouched by containment",
              all(u.parents == [] for u in plane.units.values()
                  if u.id.startswith("td2-")))

        # -- REPL surface ---------------------------------------------------------
        from form import repl
        prog.place("td2-r-a", "Repl A")
        prog.place("td2-r-b", "Repl B")
        prog.place("td2-r-c", "Repl C")
        persist_rest.save(prog)

        def drive(line):
            return repl.capture_output(
                lambda: repl._dispatch_public_line(
                    prog, line, interaction_id="td2-test"))

        _, out = drive("nest td2-r-a under td2-r-b")
        check("REPL nest works by unit id", "Nested" in out, out[:200])
        _, out = drive("containment td2-r-a")
        check("REPL containment view shows the breadcrumb by label",
              "Repl B" in out and "Repl A" in out, out[:200])
        _, out = drive("nest td2-r-a under td2-r-c")
        check("REPL refusal is visible with its kind",
              "second_parent" in out, out[:200])
        _, out = drive("promote td2-r-a")
        check("REPL promote works", "Promoted" in out, out[:200])

        print(f"TD2: {sum(1 for _, c in RESULTS if c)}/{len(RESULTS)} GREEN")
    finally:
        _cleanup(OWNER)


def smoke() -> bool:
    try:
        run_all()
        return True
    except Exception as e:
        print(f"TD2 SMOKE FAILED: {e}")
        return False


if __name__ == "__main__":
    run_all()
    sys.exit(0)
