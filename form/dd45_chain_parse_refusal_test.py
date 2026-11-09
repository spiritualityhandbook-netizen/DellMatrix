#!/usr/bin/env python3
"""DD-45 — a chain over a FAILED seed must never report success
(Ace-ordered fix-first, 2026-11-09; extension-register defect).

Verified behaviorally at base 7399ee5 (tour probes T66C/T66D/T66E,
mechanism trace in the DD-45 Director report):

- parse_seed REFUSES certain seed texts outright (ok=False,
  atoms=[]): e.g. a trailing '::' with an empty label
  ('08[Create] :: Alpha > 51[Select] :: ' ->
  error "too many flow operators"), an unknown Dell, a
  duplicate typed role, two atoms with no flow operator.
- The FRONT DOOR (executor.execute_seed) checks seed.ok and
  refuses honestly. But chain_exec.execute_chain — the chain
  authority itself, called directly by other surfaces — never
  checked seed.ok. It executed the empty atom list and returned
  ok=True: a success receipt covering ZERO executed atoms. The
  tour read this as "Select erases same-chain creates": the
  creates never ran at all; the caller's fresh plane still held
  only its starter unit.

Contract proven here:
A. A failed seed handed DIRECTLY to execute_chain returns
   ok=False with the parse error NAMED (out.error == seed.error),
   zero atom_results, zero chain_ran, and the program state
   (plane, store, selection) byte-identical to before the call.
   The front door refuses the same texts the same way (control).
B. Blast radius: with VALID grammar, same-chain Create work
   survives EVERY QUERY_DELLS atom (51-59, 67-79) placed after
   it, and every atom carries a receipt. Select in a chain sees
   same-chain creates (select-all and predicate forms), and a
   Select -> ForEach composition runs its body once per member.
C. Receipt honesty both directions: a valid chain containing a
   genuinely failing atom reports ok=False while its successful
   work stands (no silent rollback, no silent success); a valid
   all-good chain's ok=True is backed by all-ok atom receipts
   and the created units present on the plane.

Evidence class: INTEGRATION (chain authority called directly,
front door as public-entry control). Isolated synthetic owners,
uuid-unique; cleanup via canonical form.persist paths, cleanup
errors FAIL the suite.
"""
import os
import shutil
import sys
import uuid

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

RESULTS = []
_CLEANUP_ERRORS = []
_OWNERS = []


def _rec(name, cond, detail=""):
    RESULTS.append((name, bool(cond), str(detail)[:220]))


def _owner(tag):
    owner = f"DD45{tag}{uuid.uuid4().hex[:8].upper()}"
    _OWNERS.append(owner)
    return owner


def _cleanup(owner):
    from pathlib import Path

    from form.persist import _STATE_DIR, _safe_owner
    from form.dell_matrix.nursery import owner_nursery_path

    state = Path(_STATE_DIR)
    safe = _safe_owner(owner)
    cands = [state / f"program_{safe}.json", Path(owner_nursery_path(owner))]
    cands += list(state.glob(f"*{safe}*"))
    for pth in set(cands):
        try:
            if pth.is_dir():
                shutil.rmtree(pth)
            elif pth.exists():
                pth.unlink()
        except OSError as exc:
            _CLEANUP_ERRORS.append(f"{pth}: {exc}")


def _plane(p):
    return sorted(p.cube.session.plane.units.keys())


def _chain(p, raw):
    from form.mandell.chain_exec import execute_chain
    from form.mandell.seed import parse_seed

    seed = parse_seed(raw)
    return seed, execute_chain(p, seed, seed.raw)


FAILED_SHAPES = [
    ("trailing_empty_label_select", "08[Create] :: Alpha > 51[Select] :: "),
    ("trailing_empty_label_single", "51[Select] :: "),
    ("trailing_empty_label_filter", "08[Create] :: Alpha > 52[Filter] :: "),
    ("trailing_empty_label_query", "08[Create] :: Alpha > 54[Query] :: "),
    ("unknown_dell", "08[Create] :: Alpha > 200[Nope] :: x"),
    ("duplicate_role", '08[Create](a="1", a="2") :: Alpha'),
    ("missing_flow", "08[Create] :: Alpha 08[Create] :: Beta"),
]

# Valid-grammar label per QUERY Dell: harmless operands, none of
# these Dells' semantics remove plane units (query_ops arms read
# first-hand at base; they touch selected/store/weights/relations).
QUERY_LABELS = {
    51: "alpha", 52: "alpha", 54: "alpha", 55: "probe=1", 56: "probe",
    57: "eq:alpha alpha", 58: "alpha", 59: "alpha", 67: "alpha",
    68: "alpha", 69: "alpha", 70: "alpha", 71: "count", 72: "3",
    73: "gte:count 0", 74: "alpha=2", 75: "", 76: "Create",
    77: "alpha", 78: "alpha > beta", 79: "alpha > beta",
}


def main():
    from form.mandell.executor import execute_seed
    from form.mandell.query_ops import QUERY_DELLS
    from form.mandell.registry import get_dell
    from form.open import Program

    # ---------- A: failed seeds refuse at the chain authority ----
    for tag, raw in FAILED_SHAPES:
        owner = _owner("A")
        _cleanup(owner)
        p = Program(owner=owner)
        before_plane = _plane(p)
        seed, out = _chain(p, raw)
        _rec(f"A.{tag}.precondition_parse_refused", seed.ok is False,
             f"seed.ok={seed.ok} err={seed.error!r}")
        _rec(f"A.{tag}.chain_refuses", out.get("ok") is False,
             f"chain ok={out.get('ok')} err={out.get('error')!r}")
        _rec(f"A.{tag}.error_names_parse_failure",
             out.get("error") == seed.error,
             f"chain err={out.get('error')!r} seed err={seed.error!r}")
        _rec(f"A.{tag}.zero_atoms_executed",
             out.get("atom_results") == [] and out.get("chain_ran") == [],
             f"atom_results={out.get('atom_results')} ran={out.get('chain_ran')}")
        _rec(f"A.{tag}.state_untouched",
             _plane(p) == before_plane
             and dict(p.core_ii.store) == {}
             and list(p.core_ii.selected or []) == [],
             f"plane={_plane(p)} store={dict(p.core_ii.store)}")
        door = execute_seed(p, raw)
        _rec(f"A.{tag}.front_door_control_refuses",
             door.get("ok") is False and door.get("error") == seed.error,
             f"door ok={door.get('ok')} err={door.get('error')!r}")
        _cleanup(owner)

    # ---------- B: blast radius over every QUERY Dell ------------
    for n in sorted(QUERY_DELLS):
        d = get_dell(n) or {}
        term = d.get("name") or str(n)
        lab = QUERY_LABELS[n]
        seg = f"{n:02d}[{term}]" + (f" :: {lab}" if lab else "")
        owner = _owner("B")
        _cleanup(owner)
        p = Program(owner=owner)
        raw = f"08[Create] :: Alpha > 08[Create] :: Beta > {seg}"
        seed, out = _chain(p, raw)
        plane = _plane(p)
        receipts = out.get("atom_results") or []
        _rec(f"B.{n:02d}.precondition_parse_ok", seed.ok is True,
             f"err={seed.error!r}")
        _rec(f"B.{n:02d}.creates_survive",
             "alpha" in plane and "beta" in plane,
             f"plane={plane} chain_ok={out.get('ok')}")
        _rec(f"B.{n:02d}.every_atom_receipted",
             len(receipts) == 3
             and [r.get('dell') for r in receipts] == [8, 8, n],
             f"receipts={[(r.get('dell'), r.get('ok')) for r in receipts]}")
        _cleanup(owner)

    # Select sees same-chain creates — select-all and predicate.
    owner = _owner("S")
    _cleanup(owner)
    p = Program(owner=owner)
    seed, out = _chain(p, "08[Create] :: Alpha > 08[Create] :: Beta > 51[Select]")
    sel = list(p.core_ii.selected or [])
    _rec("B.select_all_sees_same_chain_creates",
         out.get("ok") is True and "alpha" in sel and "beta" in sel,
         f"selected={sel}")
    seed, out = _chain(p, "51[Select] :: alpha")
    _rec("B.select_predicate_exact",
         list(p.core_ii.selected or []) == ["alpha"],
         f"selected={list(p.core_ii.selected or [])}")
    # Select -> ForEach composition over the same-chain selection.
    seed, out = _chain(
        p, "51[Select] > 66[ForEach] > 55[Set] :: touched=1 > 61[Join]")
    body = [r for r in (out.get("atom_results") or [])
            if r.get("dell") == 55 and not r.get("skipped")]
    members = [r.get("member") for r in body]
    _rec("B.foreach_over_same_chain_selection",
         out.get("ok") is True and "alpha" in members and "beta" in members,
         f"members={members}")
    _cleanup(owner)

    # ---------- C: receipt honesty, both directions --------------
    owner = _owner("C")
    _cleanup(owner)
    p = Program(owner=owner)
    seed, out = _chain(p, "08[Create] :: Alpha > 53[Scope] :: Nowhere")
    _rec("C.failing_atom_chain_reports_failure",
         seed.ok is True and out.get("ok") is False
         and "scope_unknown" in (out.get("error") or ""),
         f"ok={out.get('ok')} err={out.get('error')!r}")
    _rec("C.failed_chain_keeps_executed_work",
         "alpha" in _plane(p), f"plane={_plane(p)}")
    seed, out = _chain(p, "08[Create] :: Beta > 55[Set] :: k=1")
    receipts = out.get("atom_results") or []
    _rec("C.good_chain_success_is_backed",
         out.get("ok") is True and len(receipts) == 2
         and all(r.get("ok") for r in receipts)
         and "beta" in _plane(p),
         f"ok={out.get('ok')} receipts={receipts} plane={_plane(p)}")
    _cleanup(owner)

    # ---------- cleanup residue ----------------------------------
    for owner in _OWNERS:
        _cleanup(owner)
    residue = []
    from pathlib import Path

    from form.persist import _STATE_DIR, _safe_owner
    state = Path(_STATE_DIR)
    for owner in _OWNERS:
        safe = _safe_owner(owner)
        residue += [str(x) for x in state.glob(f"*{safe}*")]
    _rec("cleanup.no_errors", _CLEANUP_ERRORS == [], str(_CLEANUP_ERRORS))
    _rec("cleanup.leaves_no_residue", residue == [], str(residue))

    passed = sum(1 for _, ok_, _ in RESULTS if ok_)
    for name, ok_, detail in RESULTS:
        if not ok_:
            print(f"FAIL {name}: {detail}")
    print(f"DD45_CHAIN_PARSE_REFUSAL: {passed}/{len(RESULTS)}")
    return passed == len(RESULTS) and len(RESULTS) > 0


def smoke():
    return main()


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
