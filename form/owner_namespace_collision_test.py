#!/usr/bin/env python3
"""72-34 — Owner namespace collision + foreign-state
rejection (evidence circuit).

Register: "Test owner namespace collision + foreign-state
rejection (P1/E)." Already proven: cross-owner isolation +
foreign-state refusal for DISTINCT owners
(persist_full_roundtrip). Remaining action: the NORMALIZED
owner-name collision case specifically.

form.persist._safe_owner is the single canonical sanitizer:
it maps every character that is not alphanumeric / '-' / '_'
to '_'. Distinct raw owners can therefore normalize to the
same safe name ("a/b" and "a_b"). Every live owner-state
path is keyed by that safe name alone:

  program_<safe>.json          (persist._path)
  program_<safe>_cp_*           (persist checkpoints)
  nursery_<safe>.json           (owner_nursery_path)
  ideas_<safe>/ + ideas_<safe>.json + rehydrate marker
  graph_<safe>.json + graph journal
  rollback / confirm / checkpoint / supersede /
  exchange_import journals      (core_i_recovery, exchange)

The ONE collision-safe surface is the checkpoint GENERATION
namespace: checkpoint_generation._owner_ns appends
sha256(owner)[:12] to the safe name (DCC-XVIII, proven by
dcc_xviii_test P.collision_*).

Contract under test (shape-agnostic — a repair may either
give colliding owners disjoint namespaces OR refuse the
foreign state loudly; both satisfy isolation, silent
adoption satisfies neither):

- K1 premise: the chosen pair is distinct raw and DOES
  collide under _safe_owner.
- K2 control: the generation namespace stays disjoint for
  the colliding pair (checkpoint committed under X is not
  visible as Y's checkpoint).
- D1 loading the colliding owner Y after X saved must not
  silently return an X-owned program: it raises, or it
  returns a Y-owned program.
- D2 that load must not expose X's marker state (avatar
  marker / nursery proposal).
- D2X same as D1/D2 in a fresh OS process (CROSS_PROCESS).
- D3 constructing Y directly (open_program) must not show
  X's nursery proposals.
- D4 saving a fresh Y program must not destroy X's saved
  state: afterwards load(X) still returns X's marker
  (a loud refusal of the Y save is acceptable).
- D5 symmetry: the same holds in the reverse direction
  (Y saves first, X must not adopt or destroy Y's state).
- K3 control: two NON-colliding owners stay fully
  isolated through the same save/load flow.
- K4 control: an explicit-path load of another owner's
  file resolves consistently to the file owner (the
  pinned Q-016/L14 behavior) — collision aliasing is not
  excused by it, because for colliding owners the shared
  path is the DEFAULT path, not an explicit choice.

Labels: INTEGRATION in-process; CROSS_PROCESS for D2X.
Hygiene: uuid-unique owners; exact-pattern cleanup
(files + the ideas_<safe> directory); cleanup failures
reported as a failing check, never swallowed.
"""
from __future__ import annotations

import glob
import json
import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

REPO = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, REPO)

from form.persist import _STATE_DIR, _path, _safe_owner, load, save
from form.dell_matrix.nursery import owner_nursery_path
from form.mandell.checkpoint_generation import (
    _owner_ns, commit_checkpoint, has_checkpoint)
from form.open import open_program

RESULTS = []
_CLEANUP_ERRORS = []
RUN = uuid.uuid4().hex[:8]

X = f"C34{RUN}/A"   # raw owner with a separator
Y = f"C34{RUN}_A"   # distinct raw owner, same safe name
P = f"C34{RUN}P"    # non-colliding control pair
Q = f"C34{RUN}Q"


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))
    print(f"{'PASS' if cond else 'FAIL'} {name} {detail}")


def cleanup():
    for f in glob.glob(os.path.join(_STATE_DIR, f"*{RUN}*")):
        try:
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.unlink(f)
        except OSError as e:
            _CLEANUP_ERRORS.append(f"{f}: {e}")


def build(owner, marker, label):
    p = open_program(owner)
    p.avatar.name = marker
    prop = p.nursery.add(label, f"{marker} content words")
    p.nursery.save()
    save(p)
    return prop.id


def load_or_none(owner):
    """Return (program, raised) — a loud refusal is a
    legitimate isolation outcome; silent foreign adoption
    is not."""
    try:
        return load(owner), False
    except Exception:
        return None, True


def main():
    cleanup()
    check("K1.collision_premise",
          X != Y and _safe_owner(X) == _safe_owner(Y)
          and _path(P) != _path(Q),
          f"safe={_safe_owner(X)}")

    # --- X builds and saves distinctive state -------------
    x_prop = build(X, "XRAYMARKER", "xray marker idea")

    # --- K2: generation namespace stays disjoint ----------
    try:
        px = load(X)
        commit_checkpoint(px, generation_id="g34x000000000001")
        k2 = has_checkpoint(X) and not has_checkpoint(Y) \
            and _owner_ns(X) != _owner_ns(Y)
    except Exception as e:
        k2 = False
        print("K2 raised", type(e).__name__, e)
    check("K2.generation_namespace_disjoint", k2)

    # --- D1/D2: load(Y) must not adopt X ------------------
    py, raised = load_or_none(Y)
    check("D1.load_colliding_not_foreign_owned",
          raised or (py is not None and py.owner == Y),
          f"raised={raised} owner={getattr(py, 'owner', None)!r}")
    check("D2.load_colliding_no_foreign_marker",
          raised or (py is not None
                     and py.avatar.name != "XRAYMARKER"
                     and x_prop not in py.nursery.proposals),
          f"raised={raised}")

    # --- D2X: same in a fresh OS process ------------------
    child = (
        "import json, sys\n"
        "sys.path.insert(0, sys.argv[1])\n"
        "from form.persist import load\n"
        "try:\n"
        "    p = load(sys.argv[2])\n"
        "    print(json.dumps({'owner': p.owner,"
        " 'marker': p.avatar.name,"
        " 'props': sorted(p.nursery.proposals)}))\n"
        "except Exception as e:\n"
        "    print(json.dumps({'raised': type(e).__name__}))\n"
    )
    try:
        out = subprocess.run(
            [sys.executable, "-c", child, REPO, Y],
            capture_output=True, text=True, timeout=120)
        res = json.loads(out.stdout.strip().splitlines()[-1])
        d2x = "raised" in res or (
            res.get("owner") == Y
            and res.get("marker") != "XRAYMARKER"
            and x_prop not in (res.get("props") or []))
    except Exception as e:
        d2x = False
        print("D2X child failed", type(e).__name__, e)
    check("D2X.cross_process_load_colliding_isolated", d2x)

    # --- D3: direct construction must not leak nursery ----
    try:
        py2 = open_program(Y)
        d3 = x_prop not in py2.nursery.proposals
    except Exception:
        d3 = True  # loud refusal at construction also isolates
    check("D3.open_colliding_nursery_isolated", d3)

    # --- D4: saving fresh Y must not destroy X ------------
    try:
        py3 = open_program(Y)
        py3.avatar.name = "YANKEEMARKER"
        save(py3)
    except Exception:
        pass  # loud refusal preserves X — acceptable
    px2, raised_x = load_or_none(X)
    check("D4.save_colliding_preserves_other",
          not raised_x and px2 is not None and px2.owner == X
          and px2.avatar.name == "XRAYMARKER",
          f"owner={getattr(px2, 'owner', None)!r} "
          f"marker={getattr(getattr(px2, 'avatar', None), 'name', None)!r}")

    cleanup()

    # --- D5: reverse direction ----------------------------
    y_prop = build(Y, "YANKEEMARKER", "yankee marker idea")
    px3, raised_rx = load_or_none(X)
    d5a = raised_rx or (px3 is not None and px3.owner == X
                        and px3.avatar.name != "YANKEEMARKER"
                        and y_prop not in px3.nursery.proposals)
    check("D5.reverse_load_colliding_isolated", d5a)
    try:
        px4 = open_program(X)
        px4.avatar.name = "XRAYMARKER"
        save(px4)
    except Exception:
        pass
    py4, raised_ry = load_or_none(Y)
    check("D5.reverse_save_preserves_other",
          not raised_ry and py4 is not None and py4.owner == Y
          and py4.avatar.name == "YANKEEMARKER")

    cleanup()

    # --- K3: non-colliding control pair -------------------
    p_prop = build(P, "PAPAMARKER", "papa marker idea")
    pq, raised_q = load_or_none(Q)
    k3a = not raised_q and pq is not None and pq.owner == Q \
        and pq.avatar.name != "PAPAMARKER" \
        and p_prop not in pq.nursery.proposals
    pp, raised_p = load_or_none(P)
    k3b = not raised_p and pp is not None and pp.owner == P \
        and pp.avatar.name == "PAPAMARKER"
    check("K3.noncolliding_pair_isolated", k3a and k3b)

    # --- K4: explicit-path mismatch resolves to file owner
    try:
        pk = load(Q, path=_path(P))
        k4 = pk.owner == P and pk.avatar.name == "PAPAMARKER"
    except Exception:
        k4 = False
    check("K4.explicit_path_resolves_to_file_owner", k4)

    cleanup()
    check("Z.cleanup_complete", not _CLEANUP_ERRORS,
          "; ".join(_CLEANUP_ERRORS))

    failed = [n for n, ok, _ in RESULTS if not ok]
    print(f"owner_namespace_collision: "
          f"{len(RESULTS) - len(failed)}/{len(RESULTS)} PASS")
    if failed:
        print("FAILURES:", ", ".join(failed))
    return 1 if failed else 0


def smoke():
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
