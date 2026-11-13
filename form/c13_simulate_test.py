#!/usr/bin/env python3
"""C13 Simulate — DD-21 (MWL 168/169): Dell 31 [Simulate] as a REAL
dry-run rehearsal.

Contract (plan §12.16 DD-21 + Ace's 2026-11-09 ruling + §14.3 C13
card acceptance):
- 31[Simulate] :: <seed/chain> executes its argument against an
  ISOLATED COPY of the current program state and returns an honest
  receipt: per-atom outcomes (the executor's own atom_results) and a
  SCOPED diff of what WOULD change (units created/removed/modified,
  Nursery proposals added/changed, history delta of the copy).
- Live state — Plane, Nursery, graph, history, the owner's durable
  files, the whole state directory — is BIT-IDENTICAL afterward.
  Simulate's own pre-build footprint (a note_seed history append
  under a "no mutation" banner, G2) is gone: the arm writes nothing.
- The argument is honored (G1: pre-build it was ignored entirely).
- Honest refusals, never fake success: an unparseable argument
  rehearses as a refusal receipt; durable/external-effect atoms
  (27 Checkpoint, 28 Rollback, 36 Inject, 44 Bridge, 47 Embed) and
  unsupported domains (Core II 51-99, reserved 100+) are REFUSED
  BEFORE DISPATCH with the atom and reason named; a nested
  31[Simulate] is refused; a bare 31[Simulate] (no argument) is an
  unexecuted atom — ok=False, skipped=True, reason named.
- An atom that does not execute inside the rehearsal reports
  ok=False skipped=True with its reason (standing atom-truth law).
- Determinism: the same simulation twice on unchanged state yields
  byte-identical receipts (the receipt carries no clock readings).

Checks map to the grounding's failing-first sketch (§4): sketch
1=checks 1-2, 2=check 3, 3=check 4, 4=check 5, 5=check 6, 6=check 7,
7=check 8, 8=check 9, 9=check 10 (guard, passes pre-build by
construction); sketch 10 is the build-phase live-write mutant
control, discharged outside this suite (M-A/M-B in the circuit
report). Checks 11-13 extend the sketch with the same contract's
parse-refusal, bare-argument, and nested-Simulate honesty.

Isolation (§30): per-suite owners, state cleaned before and after;
fingerprints come from the program's own serializer
(form.persist.serialize) plus sha256 over the state directory —
never from ambient assumptions.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from form.open import open_program
from form.mandell.executor import execute_seed

_STATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state")


def _cleanup(owner):
    import glob
    import shutil
    for f in glob.glob(os.path.join(_STATE_DIR, f"*{owner}*")):
        try:
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.remove(f)
        except FileNotFoundError:
            pass
        except OSError as e:
            raise RuntimeError(f"cleanup failed for {f}: {e}")


def _program(owner):
    _cleanup(owner)
    return open_program(owner)


def _fingerprint(program) -> str:
    from form import persist
    blob = json.dumps(persist.serialize(program), sort_keys=True,
                      default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _dir_snapshot() -> dict:
    out = {}
    if os.path.isdir(_STATE_DIR):
        for name in sorted(os.listdir(_STATE_DIR)):
            path = os.path.join(_STATE_DIR, name)
            if os.path.isfile(path):
                with open(path, "rb") as fh:
                    out[name] = hashlib.sha256(fh.read()).hexdigest()
    return out


def _sim(program, arg):
    """Front-door Simulate with an argument."""
    return execute_seed(program, f"31[Simulate] :: {arg}")


def smoke() -> bool:
    print("=== C13 SIMULATE (DD-21) ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}"
              + (f" | {detail}" if detail and not ok else ""))
        r.append(bool(ok))

    owners = ["C13SimT1", "C13SimT2", "C13SimT3", "C13SimT4", "C13SimT5"]
    for o in owners:
        _cleanup(o)
    try:
        # -- 1/2. Argument preview: per-atom outcome + created unit
        # named (sketch 1). BEFORE: receipt holds only 3 status lines.
        p = _program("C13SimT1")
        res = _sim(p, "08[Create] :: c13_alpha")
        rcpt = res.get("simulate") or {}
        atoms = rcpt.get("atom_results") or []
        rec("t1_atom_outcome_for_create",
            any(a.get("dell") == 8 and a.get("ok") is True for a in atoms),
            f"atom_results={atoms}")
        diff = rcpt.get("diff") or {}
        rec("t2_receipt_names_would_be_unit",
            "c13_alpha" in (diff.get("units_created") or []),
            f"diff={diff}")

        # -- 3. Live-state bit-identity after a mutating chain
        # (sketch 2): serializer fingerprint, history, state dir.
        fp0, hist0, dir0 = _fingerprint(p), list(p.history), _dir_snapshot()
        res = _sim(p, "08[Create] :: c13_beta > 07[Link] :: c13_alpha")
        rec("t3_live_bit_identical",
            _fingerprint(p) == fp0 and list(p.history) == hist0
            and _dir_snapshot() == dir0
            and "c13_beta" not in p.cube.session.plane.units,
            "live fingerprint/history/files changed by simulation")

        # -- 4. History honesty (sketch 3): no entry appended by
        # Simulate itself; live history is exactly the pre-run list.
        rec("t4_no_history_entry",
            list(p.history) == hist0,
            f"history {hist0} -> {list(p.history)}")

        # -- 5. Scoped diff matches a REAL run on a twin program
        # (sketch 4): what the diff predicts is what reality does.
        twin = _program("C13SimT2")
        real = execute_seed(twin, "08[Create] :: c13_alpha")
        real_units = set(twin.cube.session.plane.units) - {"welcome"}
        rec("t5_diff_matches_real_run",
            real.get("ok") is True
            and set(diff.get("units_created") or []) >= {"c13_alpha"}
            and "c13_alpha" in real_units,
            f"diff_created={diff.get('units_created')} real={real_units}")
        # (diff here is from check 1's single-create simulation.)

        # -- 6. Failed atom inside the simulation (sketch 5):
        # per-atom failure named at its atom; live untouched.
        fp0, hist0 = _fingerprint(p), list(p.history)
        res = _sim(p, "08[Create] :: c13_fail_a > 21[Merge] :: no_such_unit_xyz")
        rcpt = res.get("simulate") or {}
        atoms = rcpt.get("atom_results") or []
        bad = [a for a in atoms if a.get("dell") == 21]
        rec("t6_failed_atom_named",
            bool(bad) and bad[0].get("ok") is False
            and "missing_source" in str(bad[0].get("error", "")),
            f"atom_results={atoms}")
        rec("t6b_live_untouched_by_failed_sim",
            _fingerprint(p) == fp0 and list(p.history) == hist0,
            "live state changed by a failed simulation")

        # -- 7. External-effect refusal BEFORE dispatch (sketch 6):
        # Checkpoint (durable write) and Bridge (external) are
        # refused with the atom named; zero writes anywhere.
        dir0 = _dir_snapshot()
        ok7, det7 = True, ""
        for arg, dell in (("27[Checkpoint]", 27), ("44[Bridge]", 44)):
            res = _sim(p, arg)
            rcpt = res.get("simulate") or {}
            refused = rcpt.get("refused_atoms") or []
            if not (res.get("ok") is False
                    and rcpt.get("outcome") == "refused_external_effect"
                    and any(x.get("dell") == dell for x in refused)):
                ok7, det7 = False, f"{arg}: res_ok={res.get('ok')} rcpt={rcpt}"
        rec("t7_external_effect_refused", ok7, det7)
        rec("t7b_no_writes_from_refusal", _dir_snapshot() == dir0,
            "state dir changed by a refused simulation")

        # -- 8. Nested control flow (sketch 7): a Loop chain
        # rehearses with per-atom outcomes for the nested atoms.
        res = _sim(p, "13[Loop] :: 2 > 08[Create] :: c13_loop_a")
        rcpt = res.get("simulate") or {}
        atoms = rcpt.get("atom_results") or []
        rec("t8_nested_loop_outcomes",
            any(a.get("dell") == 13 for a in atoms)
            and "c13_loop_a" in ((rcpt.get("diff") or {}).get("units_created") or []),
            f"atom_results={atoms} diff={rcpt.get('diff')}")

        # -- 9. Determinism (sketch 8): same simulation twice on
        # unchanged state -> byte-identical receipts.
        r1 = _sim(p, "08[Create] :: c13_det")
        r2 = _sim(p, "08[Create] :: c13_det")
        s1 = json.dumps(r1.get("simulate"), sort_keys=True, default=str)
        s2 = json.dumps(r2.get("simulate"), sort_keys=True, default=str)
        rec("t9_deterministic_receipts",
            bool(r1.get("simulate")) and s1 == s2 and r1.get("ok") is True,
            "receipts differ across identical simulations")

        # -- 10. Cross-owner isolation (sketch 9, guard): simulating
        # under owner A leaves owner B's files + fingerprint intact.
        other = _program("C13SimT3")
        fp_b, dir0 = _fingerprint(other), _dir_snapshot()
        _sim(p, "08[Create] :: c13_cross")
        rec("t10_cross_owner_untouched",
            _fingerprint(other) == fp_b and _dir_snapshot() == dir0,
            "another owner's state changed")

        # -- 11. Unparseable argument -> refusal receipt, not a fake
        # success; live history unchanged (contract extension).
        # Board level: the harness refuses a seed the parser
        # refuses. Front door: the same broken text after "::" is
        # absorbed by the outer grammar as a DATA label (a flow
        # operator not followed by a valid atom is label data,
        # seed.py), so the atom is honestly unexecuted
        # (no_argument) rather than rehearsing a phantom.
        from form.dell_matrix.simulate_board import run_simulation
        hist0 = list(p.history)
        rcpt = run_simulation(p, "08[Create")
        rec("t11_parse_refusal_receipt",
            rcpt.get("ok") is False
            and rcpt.get("outcome") == "refused_parse"
            and list(p.history) == hist0,
            f"rcpt={rcpt}")
        res = _sim(p, "08[Create")
        rcpt = res.get("simulate") or {}
        rec("t11b_broken_atom_text_is_data_label",
            res.get("ok") is False
            and rcpt.get("outcome") == "no_argument"
            and list(p.history) == hist0,
            f"res_ok={res.get('ok')} rcpt={rcpt}")

        # -- 12. Bare Simulate: unexecuted atom, honestly reported;
        # no history entry (contract extension; DD-21 bit-identity).
        hist0 = list(p.history)
        res = execute_seed(p, "31[Simulate]")
        rcpt = res.get("simulate") or {}
        rec("t12_bare_is_honest_noop",
            res.get("ok") is False and res.get("skipped") is True
            and rcpt.get("outcome") == "no_argument"
            and list(p.history) == hist0,
            f"res={ {k: res.get(k) for k in ('ok', 'skipped', 'error')} } rcpt={rcpt}")

        # -- 13. Nested Simulate refused before dispatch
        # (contract extension): a rehearsal never recurses.
        res = _sim(p, "31[Simulate] :: 08[Create] :: c13_nested")
        rcpt = res.get("simulate") or {}
        rec("t13_nested_simulate_refused",
            res.get("ok") is False
            and rcpt.get("outcome") == "refused_nested_simulate"
            and "c13_nested" not in p.cube.session.plane.units,
            f"res_ok={res.get('ok')} rcpt={rcpt}")
    finally:
        for o in owners:
            _cleanup(o)

    print(f"C13 SIMULATE: {sum(r)}/{len(r)} checks passed")
    return all(r)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
