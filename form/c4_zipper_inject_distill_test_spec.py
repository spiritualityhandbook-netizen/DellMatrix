#!/usr/bin/env python3
"""Part II / C4 family — Zipper, Inject-by-reference, Distill.

Register contracts:
- Row #137 (DD-20 / C4.Zipper): Compress + Expand as one circuit —
  Compress preserves a resolvable source link; Expand retrieves the
  full intended source under a declared current-vs-versioned rule.
- Row #138 (DD-26 / C4.InjectRef): Inject adds a reference, not a
  duplicate; cycles/missing/foreign/superseded targets resolve
  honestly.
- Row #139 (DD-28 / C4.Distill): Distill = essence — uses actual
  words/detail/goals, carries provenance and disclosed omissions,
  usable without its source.

Measured at main af2519b6 before this suite was written
(form/mandell/executor_leaf.py:466-541, PUBLIC_ENTRY_PATH probes):
Compress (29) places a distilled slug (compress_<first-words>) with
no source link; Expand (30) expands the slug's own text and never
retrieves the compressed source; Inject (36) of an already-present
idea creates a duplicate unit (<id>_1); Distill (38) places a slug
with no provenance and no omission disclosure. Every contract
check below therefore fails-first; the existence pins pass.

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


def _prog(tag):
    from form.open import Program
    from form.mandell.core_ii_exec import attach
    TAGS.append(tag)
    return Program(owner=f"C4F{tag}{RUN}"), attach


def execute_seed(p, seed):
    from form.mandell.executor import execute_seed as _es
    return _es(p, seed)


def _units(p):
    return p.cube.session.plane.units


def _unit_blob(u):
    parts = [str(getattr(u, "label", "")), str(getattr(u, "words", "")),
             str(getattr(u, "detail", "")), str(getattr(u, "goals", "")),
             str(getattr(u, "origin", ""))]
    return " ".join(parts)


def main():
    from form.mandell.core_ii_exec import attach

    src = "quixotic zebra lantern festival manuscript aurora"
    p, _ = _prog("Z")
    attach(p)
    r = execute_seed(p, f"29[Compress] :: {src}")
    check("pin.compress_executes", bool(r.get("ok")), f"{r.get('messages')}")
    comp = [u for uid, u in _units(p).items()
            if uid.startswith("compress_")]
    check("zipper.compress_makes_unit", len(comp) == 1,
          f"units={list(_units(p))}")
    blob = _unit_blob(comp[0]) if comp else ""
    check("zipper.compress_preserves_source_link",
          src in blob,
          f"compressed unit carries: {blob[:90]!r} (full source absent)")
    comp_id = comp[0].id if comp else "compress_none"
    r = execute_seed(p, f"30[Expand] :: {comp_id}")
    check("pin.expand_executes", bool(r.get("ok")), f"{r.get('messages')}")
    retrieved = " ".join(_unit_blob(u) for u in _units(p).values())
    retrieved += " " + " ".join(str(m) for m in (r.get("messages") or []))
    check("zipper.expand_retrieves_full_source", src in retrieved,
          "Expand never reproduces the compressed source text")

    p, _ = _prog("I")
    attach(p)
    execute_seed(p, '08[Create](name="refsrcc4")')
    before = set(_units(p))
    r = execute_seed(p, "36[Inject] :: refsrcc4")
    check("pin.inject_executes", bool(r.get("ok")), f"{r.get('messages')}")
    after = set(_units(p))
    check("inject.reference_not_duplicate", after == before,
          f"new units created by Inject of a present idea: "
          f"{sorted(after - before)}")

    p, _ = _prog("D")
    attach(p)
    long_src = ("distill probe alpha bravo charlie delta echo foxtrot "
                "golf hotel india juliet kilo lima mike november")
    r = execute_seed(p, f"38[Distill] :: {long_src}")
    check("pin.distill_executes", bool(r.get("ok")), f"{r.get('messages')}")
    new_units = [u for uid, u in _units(p).items()
                 if "distill" in uid or _unit_blob(u).startswith("distill")]
    blob = " ".join(_unit_blob(u) for u in _units(p).values())
    blob += " " + " ".join(str(m) for m in (r.get("messages") or []))
    disclosed = ("omitted" in blob or "omission" in blob
                 or "source:" in blob or "provenance" in blob)
    check("distill.carries_provenance_and_disclosed_omissions",
          disclosed,
          "distilled output names neither its source nor its omissions")

    for tag in TAGS:
        _cleanup(tag)
    check("cleanup.clean", not _CLEANUP_ERRORS,
          f"errors={_CLEANUP_ERRORS}")
    ok_n = sum(1 for _, ok in RESULTS if ok)
    print(f"C4_ZIPPER_INJECT_DISTILL {ok_n}/{len(RESULTS)}")
    return 0 if ok_n == len(RESULTS) else 1


def _cleanup(tag):
    from form.persist import _STATE_DIR, _safe_owner
    from form.dell_matrix.nursery import owner_nursery_path
    owner = f"C4F{tag}{RUN}"
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
