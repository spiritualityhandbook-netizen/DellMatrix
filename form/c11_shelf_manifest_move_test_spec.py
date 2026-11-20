#!/usr/bin/env python3
"""Part II / C11 family — Shelf, Manifest split, Universal Move.

Register contracts:
- Row #160 (DD-38 / C11.Shelf): Macro read back as one seed.
- Row #162 (DD-40 / C11.Manifest): Confirm is the yes, Manifest is
  the walk — confirmed-but-unmanifested is explicit, durable,
  recoverable; retry produces one result.
- Row #163 (DD-50 / C11.Move): Move moves anything movable —
  dispatches by explicit object class to EXISTING engines,
  preserves identity, refuses ambiguity/collisions.

Measured at main af2519b6 before this suite was written:
- Program.macro_seed (form/open.py:367-371) joins recent history
  into one seed but slices the result [:200]; measured read-back
  of three ~154-char history entries came back 178 chars with the
  tail entry absent — entry-level note cuts and the [:200] join
  slice compound, and the macro does NOT read back whole.
- 50[Manifest] :: mani created a DUPLICATE idea (mani_1) and
  printed "Manifested.", while the original unit's manifest
  attribute stayed None: Manifest duplicates instead of walking
  the confirmed item, and confirmed-but-unmanifested is not an
  explicit readable state (PUBLIC_ENTRY_PATH probe).
- translate("move stampme to the shelf") routes to 19[Drive]
  walk — there is no Move dispatch at the English door; "move" is
  captured by the locomotion branch (INTEGRATION probe).

Labels: PUBLIC_ENTRY_PATH (execute_seed) + INTEGRATION
(translate). Hygiene: uuid owners, exact-pattern cleanup,
cleanup errors fail the suite.
"""
from __future__ import annotations

import sys
import uuid
from pathlib import Path

REPO = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, REPO)

RESULTS = []
_CLEANUP_ERRORS = []
RUN = uuid.uuid4().hex[:8]
TAGS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def execute_seed(p, seed):
    from form.mandell.executor import execute_seed as _es
    return _es(p, seed)


def main():
    from form.open import Program
    from form.mandell.core_ii_exec import attach
    from form.mandell.translate import translate

    TAGS.append("F")
    p = Program(owner=f"C11F{RUN}")
    attach(p)
    execute_seed(p, '08[Create](name="mani")')
    units_before = set(p.cube.session.plane.units)
    r = execute_seed(p, "50[Manifest] :: mani")
    check("pin.manifest_executes", bool(r.get("ok")),
          f"{r.get('messages')}")
    units_after = set(p.cube.session.plane.units)
    check("manifest.walks_item_not_duplicate",
          units_after == units_before,
          f"new units from Manifest: {sorted(units_after - units_before)}")
    unit = p.cube.session.plane.units.get("mani")
    mstate = getattr(unit, "manifest", None) if unit else None
    check("manifest.state_explicit_on_item",
          mstate not in (None, ""),
          f"mani.manifest={mstate!r} after Manifest")

    # Stage history through the Program's own history writer (the
    # API the Dell handlers themselves call), three long entries
    # whose joined seed is ~490 chars: an uncut read-back must
    # contain the LAST entry's tail; the [:200] slice at
    # form/open.py:371 makes that impossible today.
    tail_mark = "shelfmark tail " + "y" * 140
    p.note_seed(34, "Stamp", "shelfmark one " + "x" * 140)
    p.note_seed(34, "Stamp", "shelfmark two " + "x" * 140)
    p.note_seed(34, "Stamp", tail_mark)
    seed_back = p.macro_seed(3)
    check("macro.readback_one_seed_uncut",
          tail_mark in seed_back and len(seed_back) > 200,
          f"macro_seed len={len(seed_back)}, tail entry absent "
          f"(entry cuts + [:200] join slice at open.py:371)")

    it = translate("move mani to the shelf")
    check("move.dispatches_not_drive",
          it.action not in ("walk",) and "19[Drive]" not in it.mandel,
          f"action={it.action} mandel={it.mandel!r}")

    for tag in TAGS:
        _cleanup(tag)
    check("cleanup.clean", not _CLEANUP_ERRORS,
          f"errors={_CLEANUP_ERRORS}")
    ok_n = sum(1 for _, ok in RESULTS if ok)
    print(f"C11_SHELF_MANIFEST_MOVE {ok_n}/{len(RESULTS)}")
    return 0 if ok_n == len(RESULTS) else 1


def _cleanup(tag):
    from form.persist import _STATE_DIR, _safe_owner
    from form.dell_matrix.nursery import owner_nursery_path
    owner = f"C11{tag}{RUN}"
    state = Path(_STATE_DIR)
    safe = _safe_owner(owner)
    cands = [state / f"program_{safe}.json",
             Path(owner_nursery_path(owner))]
    cands += list(state.glob(f"*{safe}*"))
    for pth in set(cands):
        try:
            if pth.is_dir():
                import shutil
                shutil.rmtree(pth)
            elif pth.exists():
                pth.unlink()
        except OSError as exc:
            _CLEANUP_ERRORS.append(f"{pth}: {exc}")


def smoke():
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
