#!/usr/bin/env python3
"""DD-45 RECON — what exactly mutates when a chain is refused?

Director scoped hold on PR #345 (mail 1a1c72ded8c73827, 2026-11-10):
the DD-45 guard's unconditional claim "zero state mutates" was
challenged because the guard calls _note_unknown(program, ...).
This suite settles the claim empirically, through the PUBLIC entry
path (executor.execute_seed) and the chain authority directly:

1. DURABLE FILES: every state file owned by the test owner (program
   file + nursery file) is byte-identical before/after a refused
   chain — the refusal itself writes nothing to disk.
2. CANONICAL IN-MEMORY STATE: plane units, core_ii store/selection,
   and nursery pending proposals are identical after refusal.
3. THE ONE MUTATION, CLASSIFIED: the unknowns register
   (program.unknowns — a first-class PERSISTED section, see
   form/persist.py unknowns section + persist_rest restore) gains
   exactly one OPEN entry per distinct refused seed (deduped:
   a repeat refusal increments `seen`). The refusal does NOT call
   save(); the entry reaches disk only via the program's normal
   save path — proven here by an explicit save() + reload, after
   which the entries are present in the reloaded program.

So the honest claim is NOT "zero state mutates" and NOT "a
diagnostic note that is never persisted": one durable-register
entry is recorded in memory at refusal time and persists on the
next ordinary save, by the PP3 design that governs every
encountered unknown in the system.

Evidence class: INTEGRATION (public front door + chain authority,
isolated synthetic owner, uuid-unique; cleanup via canonical
form.persist paths; cleanup errors FAIL the suite).
"""
import copy
import hashlib
import json
import os
import shutil
import sys
import uuid
from pathlib import Path

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

RESULTS = []
_CLEANUP_ERRORS = []
_OWNERS = []


def _rec(name, cond, detail=""):
    RESULTS.append((name, bool(cond), str(detail)[:220]))


def _cleanup(owner):
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


def _files(owner):
    """{filename: sha256} for every state file owned by `owner`."""
    from form.persist import _STATE_DIR, _safe_owner
    from form.dell_matrix.nursery import owner_nursery_path

    state = Path(_STATE_DIR)
    safe = _safe_owner(owner)
    out = {}
    paths = list(state.glob(f"*{safe}*")) + [Path(owner_nursery_path(owner))]
    for pth in paths:
        if pth.is_file():
            out[pth.name] = hashlib.sha256(pth.read_bytes()).hexdigest()
    return out


def _mem(p):
    from form.mandell.core_ii_exec import attach

    st = attach(p)  # canonical lazy attach; identity once attached
    return {
        "plane": sorted(p.cube.session.plane.units.keys()),
        "store": dict(st.store),
        "selected": list(st.selected or []),
        "nursery_pending": sorted(
            (pr.label, pr.status) for pr in p.nursery.pending()),
    }


def main():
    from form.mandell.chain_exec import execute_chain
    from form.mandell.executor import execute_seed
    from form.mandell.seed import parse_seed
    from form.open import Program
    from form.persist import _STATE_DIR, _safe_owner

    owner = f"DD45R{uuid.uuid4().hex[:8].upper()}"
    _OWNERS.append(owner)
    _cleanup(owner)
    p = Program(owner=owner)

    # ---- seed real, saved state through the public door ----------
    r1 = execute_seed(p, "08[Create] :: Alpha")
    r2 = execute_seed(p, "08[Create] :: Beta")
    _rec("setup.creates_ok", r1.get("ok") and r2.get("ok"),
         f"r1={r1.get('ok')} r2={r2.get('ok')}")
    p.nursery.add("ReconIdea", "recon words")
    p.save()
    files0 = _files(owner)
    _rec("setup.durable_files_exist", len(files0) >= 2,
         f"files={sorted(files0)}")
    mem0 = _mem(p)
    unk0 = copy.deepcopy(getattr(p, "unknowns", None) or {})
    _rec("setup.unknowns_start_empty", unk0 == {}, f"unknowns={unk0}")

    # ---- 1. refused chain via the PUBLIC entry path ---------------
    raw = "08[Create] :: Alpha > 51[Select] :: "
    out = execute_seed(p, raw)
    _rec("public.refused", out.get("ok") is False,
         f"ok={out.get('ok')} err={out.get('error')!r}")
    _rec("public.durable_files_byte_identical", _files(owner) == files0,
         f"after={sorted(_files(owner))}")
    _rec("public.canonical_state_unchanged", _mem(p) == mem0,
         f"mem={_mem(p)}")
    unk1 = copy.deepcopy(getattr(p, "unknowns", None) or {})
    new1 = [e for k, e in unk1.items() if k not in unk0]
    _rec("public.exactly_one_unknown_entry_added", len(new1) == 1,
         f"added={len(new1)} total={len(unk1)}")
    if new1:
        e = new1[0]
        _rec("public.entry_shape",
             e.get("status") == "OPEN" and e.get("seen") == 1
             and e.get("source") == "executor:parse"
             and e.get("subject") == f"seed: {raw[:160]}"
             and (e.get("question") or "").startswith(
                 "Seed could not be parsed:"),
             f"entry={ {k: e.get(k) for k in ('status', 'seen', 'source')} }")

    # ---- 2. refused chain at the chain authority directly ---------
    raw2 = "51[Select] :: "
    seed2 = parse_seed(raw2)
    out2 = execute_chain(p, seed2, seed2.raw)
    _rec("chain.refused", seed2.ok is False and out2.get("ok") is False
         and out2.get("atom_results") == []
         and out2.get("chain_ran") == [],
         f"ok={out2.get('ok')} err={out2.get('error')!r}")
    _rec("chain.durable_files_byte_identical", _files(owner) == files0,
         f"after={sorted(_files(owner))}")
    _rec("chain.canonical_state_unchanged", _mem(p) == mem0,
         f"mem={_mem(p)}")
    unk2 = copy.deepcopy(getattr(p, "unknowns", None) or {})
    new2 = [e for k, e in unk2.items() if k not in unk1]
    _rec("chain.exactly_one_unknown_entry_added", len(new2) == 1
         and new2[0].get("source") == "chain_exec:parse",
         f"added={len(new2)} sources={[e.get('source') for e in new2]}")

    # ---- 3. dedupe: same refused text again via the public door ---
    out3 = execute_seed(p, raw)
    unk3 = copy.deepcopy(getattr(p, "unknowns", None) or {})
    _rec("dedupe.no_new_entry", len(unk3) == len(unk2),
         f"before={len(unk2)} after={len(unk3)}")
    seen_vals = [e.get("seen") for e in unk3.values()
                 if e.get("source") == "executor:parse"]
    _rec("dedupe.seen_incremented", seen_vals == [2],
         f"seen={seen_vals}")
    _rec("dedupe.durable_files_still_identical", _files(owner) == files0,
         f"after={sorted(_files(owner))}")

    # ---- 4. the persistence ride: normal save + reload ------------
    p.save()
    prog_path = Path(_STATE_DIR) / f"program_{_safe_owner(owner)}.json"
    data = json.loads(prog_path.read_text())
    section = data.get("unknowns") or {}
    entries = section.get("entries") or {}
    saved_ids = set(entries.keys())
    want_ids = set(unk3.keys())
    _rec("persist.entries_in_saved_file", want_ids <= saved_ids
         and len(saved_ids) >= 2,
         f"saved={len(saved_ids)} want={sorted(want_ids)[:2]}")
    p2 = Program.load(owner)
    unk_re = getattr(p2, "unknowns", None) or {}
    _rec("persist.entries_survive_reload",
         set(unk_re.keys()) == want_ids
         and all(unk_re[k].get("status") == "OPEN" for k in want_ids),
         f"reloaded={len(unk_re)}")
    _rec("persist.reloaded_canonical_state_intact",
         _mem(p2) == mem0, f"mem={_mem(p2)}")

    # ---- cleanup residue ------------------------------------------
    for o in _OWNERS:
        _cleanup(o)
    residue = []
    state = Path(_STATE_DIR)
    for o in _OWNERS:
        safe = _safe_owner(o)
        residue += [str(x) for x in state.glob(f"*{safe}*")]
    _rec("cleanup.no_errors", _CLEANUP_ERRORS == [], str(_CLEANUP_ERRORS))
    _rec("cleanup.leaves_no_residue", residue == [], str(residue))

    passed = sum(1 for _, ok_, _ in RESULTS if ok_)
    for name, ok_, detail in RESULTS:
        if not ok_:
            print(f"FAIL {name}: {detail}")
    print(f"DD45_RECON: {passed}/{len(RESULTS)}")
    return passed == len(RESULTS) and len(RESULTS) > 0


def smoke():
    return main()


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
