"""Track D TD-1-R1 — conflict and corruption guard.

Director directive 2026-11-04 (Mode D review of TD-1): TD-1's
demonstrated mechanisms are accepted, but certification is
deferred on two source-review findings requiring failing-first
reproduction:

  F1 Corrupt-state handling: _persisted_pointer() returned None
     when the persisted Program file was unreadable, and the
     subsequent save did not validate that file — a path for
     silently overwriting corrupt state.
  F2 Concurrent binding: the conflict check ran without a lock or
     compare-and-swap; two simultaneously binding instances could
     both pass it. The TD-1 suite covered sequential staleness,
     not the overlapping-writer window.

R1 contract pinned here:

  * Bind reads the canonical state file ONCE at entry. A file that
    exists but cannot be read/parsed refuses the bind with
    state_unreadable BEFORE any mint; the corrupt bytes are left
    exactly as found (no silent overwrite) and no shell is minted.
  * The entry read's SHA-256 fingerprint is the compare-and-swap
    token. Because a bind's save rewrites the WHOLE program state,
    ANY intervening save invalidates this instance: immediately
    before the save, the file is re-read; a changed fingerprint
    (including absent->present and present->absent transitions)
    fails the bind. A shell minted before that gate is reported
    as a census-visible orphan via BindingFailed; the winning
    writer's persisted binding is untouched, and this instance's
    in-memory pointer is never set.
  * Reconciliation: when the in-memory pointer and the canonical
    persisted pointer disagree, the persisted record is canonical
    — bind refuses with a conflict naming both, instead of
    trusting memory into an already_bound answer.

Run: python3 -m form.track_d_td1_r1_test
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


OWNER = "Td1R1Probe"


def _paths(owner):
    from form.persist import _STATE_DIR, _safe_owner
    safe = _safe_owner(owner)
    return {
        "program": os.path.join(_STATE_DIR, f"program_{safe}.json"),
        "ideas": os.path.join(_STATE_DIR, f"ideas_{safe}"),
        "graph": os.path.join(_STATE_DIR, f"graph_{safe}.json"),
        "graph_journal": os.path.join(
            _STATE_DIR, f"graph_{safe}.journal.json"),
        "state_dir": _STATE_DIR,
        "safe": safe,
    }


def _cleanup(owner):
    p = _paths(owner)
    for f in (p["program"], p["graph"], p["graph_journal"]):
        if os.path.isfile(f):
            os.remove(f)
    if os.path.isdir(p["ideas"]):
        shutil.rmtree(p["ideas"])
    for name in os.listdir(p["state_dir"]):
        if name.startswith(f"program_{p['safe']}_cp_"):
            os.remove(os.path.join(p["state_dir"], name))
    return p


def _hash_bytes(b):
    return hashlib.sha256(b).hexdigest()


def _file_hash(path):
    if not os.path.isfile(path):
        return None
    with open(path, "rb") as f:
        return _hash_bytes(f.read())


def run_all():
    from form.open import open_program
    from form import persist_rest
    from form.mandell import unit_binding, idea_persist
    from form.mandell.idea_persist import list_idea_ids, load_idea

    _cleanup(OWNER)
    try:
        p = _paths(OWNER)
        prog = open_program(OWNER)
        plane = prog.cube.session.plane
        prog.place("r1-alpha", "Alpha R1")
        prog.place("r1-beta", "Beta R1")
        prog.place("r1-gamma", "Gamma R1")
        persist_rest.save(prog)

        from form.mandell.semantic_graph import SemanticGraph
        SemanticGraph.load(OWNER).save()
        graph_before = (_file_hash(p["graph"]),
                        _file_hash(p["graph_journal"]))

        # -- F1: corrupt persisted state refuses before minting ----
        with open(p["program"], "wb") as f:
            f.write(b"{corrupt{{{ not json")
        corrupt_hash = _file_hash(p["program"])
        n_ideas = len(list_idea_ids(OWNER))
        try:
            prog.bind_unit_to_idea("r1-alpha", subject="Ace")
            check("F1 corrupt state refuses the bind", False)
        except unit_binding.BindingRefused as e:
            check("F1 corrupt state refuses the bind",
                  e.kind == "state_unreadable"
                  and len(list_idea_ids(OWNER)) == n_ideas
                  and plane.units["r1-alpha"].idea_id is None)
        check("F1 corrupt bytes are left exactly as found",
              _file_hash(p["program"]) == corrupt_hash)

        # restore a valid state file for the remaining checks
        persist_rest.save(prog)

        # -- F2: overlapping writers (interleaved mid-bind) ---------
        # Instance B is loaded from the same saved state as a fresh
        # instance A. A's COMPLETE bind of r1-beta lands inside B's
        # bind (injected at B's mint via the idea-persist seam).
        inst_a = persist_rest.load(OWNER, p["program"], activate=False)
        inst_b = persist_rest.load(OWNER, p["program"], activate=False)
        real_save_idea = idea_persist.save_idea
        injected = {"done": False, "a_receipt": None}

        def save_idea_with_interleave(idea, owner=None):
            if not injected["done"]:
                injected["done"] = True
                injected["a_receipt"] = inst_a.bind_unit_to_idea(
                    "r1-beta", subject="Ace")
            return real_save_idea(idea, owner)

        idea_persist.save_idea = save_idea_with_interleave
        try:
            inst_b.bind_unit_to_idea("r1-beta", subject="Mallory")
            check("F2 overlapping writer fails at the save gate", False)
        except unit_binding.BindingFailed as e:
            a_id = injected["a_receipt"]["idea_id"]
            check("F2 overlapping writer fails at the save gate",
                  bool(e.orphan_idea_id)
                  and inst_b.cube.session.plane.units["r1-beta"].idea_id
                  is None)
            orphan = e.orphan_idea_id
        finally:
            idea_persist.save_idea = real_save_idea
        on_disk = persist_rest.load(OWNER, p["program"], activate=False)
        check("F2 the winning writer's binding survives untouched",
              on_disk.cube.session.plane.units["r1-beta"].idea_id == a_id)
        check("F2 the losing shell is a census-visible orphan",
              orphan in inst_b.binding_census()["unreferenced_idea_ids"]
              and load_idea(orphan, OWNER).title == "Beta R1")

        # -- reconciliation: memory vs canonical persisted pointer --
        # prog is stale after the F2 writers moved the file; the
        # guard correctly refuses it, so reload before continuing.
        prog = persist_rest.load(OWNER, p["program"], activate=False)
        # gamma: bind honestly (-> X, saved). Then rewind the FILE
        # to a different valid shell Y. The instance's memory still
        # says X; bind must refuse, naming both — canonical wins.
        receipt_g = prog.bind_unit_to_idea("r1-gamma", subject="Ace")
        x_id = receipt_g["idea_id"]
        y_receipt = None
        other = persist_rest.load(OWNER, p["program"], activate=False)
        # mint a second shell via a throwaway unit on the other inst
        other.place("r1-donor", "Donor")
        y_receipt = other.bind_unit_to_idea("r1-donor", subject="Ace")
        y_id = y_receipt["idea_id"]
        with open(p["program"], encoding="utf-8") as f:
            raw = json.load(f)
        raw["plane"]["units"]["r1-gamma"]["idea_id"] = y_id
        with open(p["program"], "w", encoding="utf-8") as f:
            json.dump(raw, f)
        try:
            prog.bind_unit_to_idea("r1-gamma", subject="Ace")
            check("reconciliation refuses a memory/persisted split",
                  False)
        except unit_binding.BindingRefused as e:
            check("reconciliation refuses a memory/persisted split",
                  e.kind == "conflict"
                  and e.detail.get("persisted_idea_id") == y_id
                  and e.detail.get("in_memory_idea_id") == x_id)

        # -- fingerprint transitions: state file disappears ---------
        inst_c = persist_rest.load(OWNER, p["program"], activate=False)
        os.remove(p["program"])
        try:
            inst_c.bind_unit_to_idea("r1-alpha", subject="Ace")
            check("vanished state file fails the bind closed", False)
        except (unit_binding.BindingRefused,
                unit_binding.BindingFailed) as e:
            kind = getattr(e, "kind", "failed_after_mint")
            check("vanished state file fails the bind closed",
                  kind in ("conflict", "state_unreadable",
                           "failed_after_mint")
                  and inst_c.cube.session.plane.units["r1-alpha"].idea_id
                  is None)
        # the file must not have been silently resurrected by inst_c
        check("no silent resurrection of the vanished state",
              not os.path.isfile(p["program"]))

        # -- the guard does not break the honest paths --------------
        persist_rest.save(prog)  # canonical state restored by owner
        r = prog.bind_unit_to_idea("r1-alpha", subject="Ace")
        r2 = prog.bind_unit_to_idea("r1-alpha", subject="Ace")
        check("sequential binds still work under the guard",
              r.get("status") == "bound"
              and r2.get("status") == "already_bound")
        graph_after = (_file_hash(p["graph"]),
                       _file_hash(p["graph_journal"]))
        check("R1 performs zero SemanticGraph writes",
              graph_before == graph_after)

        print(f"TD1-R1: {sum(1 for _, c in RESULTS if c)}/{len(RESULTS)} GREEN")
    finally:
        _cleanup(OWNER)


def smoke() -> bool:
    try:
        run_all()
        return True
    except Exception as e:
        print(f"TD1-R1 SMOKE FAILED: {e}")
        return False


if __name__ == "__main__":
    run_all()
    sys.exit(0)
