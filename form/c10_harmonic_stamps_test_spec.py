#!/usr/bin/env python3
"""Part II / C10 family — Harmonic stamps (row #158) + lenses note.

Register contract (row #158, DD-24 / C10.Stamp): item-attached
stamps with provenance in stable order; moving an item never
silently changes its note; stamps round-trip.

Measured at main af2519b6 before this suite was written
(PUBLIC_ENTRY_PATH probe): 34[Stamp] :: verified returns ok and a
timestamped MESSAGE ("Stamp: verified @ 2026-11-20T14:58:52Z"), but
the stamped idea unit carries no stamp at all — its attribute set
(detail, goals, id, idea_id, label, lineage_version, manifest,
origin, parents, sandbox_id, sandboxed, skin, words, x, y) has no
stamp field. The stamp lives only in the transient message/history,
never on the item. The attachment checks therefore fail-first;
the execution pin passes.

Row #159 (C10.Lenses — views rearrange DISPLAY only) has no public
lens execution surface to probe at this tier; its failing-first
suite is specified in the Part II plan and lands with the code
stage, after the lens surface is designed. Not faked here.

Labels: PUBLIC_ENTRY_PATH (execute_seed). Hygiene: uuid owners,
exact-pattern cleanup, cleanup errors fail the suite.
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


def _stamps_of(unit):
    for attr in ("stamps", "stamp", "marks", "annotations"):
        val = getattr(unit, attr, None)
        if val:
            return val
    return None


def main():
    from form.open import Program
    from form.mandell.core_ii_exec import attach
    TAGS.append("S")
    p = Program(owner=f"C10S{RUN}")
    attach(p)
    execute_seed(p, '08[Create](name="stampme")')
    r = execute_seed(p, "34[Stamp] :: verified")
    check("pin.stamp_executes_with_timestamp",
          bool(r.get("ok"))
          and any("Stamp:" in str(m) and "@" in str(m)
                  for m in (r.get("messages") or [])),
          f"{r.get('messages')}")
    unit = p.cube.session.plane.units.get("stampme")
    stamps = _stamps_of(unit) if unit else None
    check("stamp.attaches_to_item", stamps is not None,
          f"unit attrs carry no stamp: "
          f"{sorted(vars(unit).keys()) if unit else 'unit missing'}")
    execute_seed(p, "34[Stamp] :: reviewed")
    stamps2 = _stamps_of(unit) if unit else None
    n = len(stamps2) if isinstance(stamps2, (list, tuple)) else 0
    check("stamp.provenance_in_stable_order", n >= 2,
          f"two stamps on the item in order expected; found {n}")

    for tag in TAGS:
        _cleanup(tag)
    check("cleanup.clean", not _CLEANUP_ERRORS,
          f"errors={_CLEANUP_ERRORS}")
    ok_n = sum(1 for _, ok in RESULTS if ok)
    print(f"C10_HARMONIC_STAMPS {ok_n}/{len(RESULTS)}")
    return 0 if ok_n == len(RESULTS) else 1


def _cleanup(tag):
    from form.persist import _STATE_DIR, _safe_owner
    from form.dell_matrix.nursery import owner_nursery_path
    owner = f"C10{tag}{RUN}"
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
