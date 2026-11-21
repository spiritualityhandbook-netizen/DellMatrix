#!/usr/bin/env python3
"""GP-E07 — Whole addressed-Dell execution audit (Part II, §5 item 1).

Contract (PART_II_PLAN_2026-11-20.md, GP-E07): for every address
00-99: declared name/manor, actual dispatcher + handler,
mutation/read/refusal class, side effects, required Args,
expected output/error, observed public door, tests, open design
decision, one contract test. Registry ACTIVE = reachability only,
never completion. The "99 vs 100 Dells" label is reconciled as
evidence (100 addresses: 51 Core I + 49 Core II) without deleting
an address or counting address 151 as a core Dell.

The audit engine is form/mandell/dell_audit.py: an evidence sweep
over the public seed door (form.mandell.executor.execute_seed),
address by address, each on a fresh isolated owner. Verdicts:
CONTRACT_PROVEN / DEFECT / MESSAGE_ONLY / UNREACHABLE, each from
stated evidence legs (named refusal with zero canonical change;
canonical mutation; result payload; executed chain atom; minted
value; field-sensitive receipt). The published ledger is
director-reports/PART_II_GPE07_AUDIT_LEDGER_2026-11-21.md; this
suite fails if it drifts from a fresh audit.

This suite is the circuit's repair gate: a DEFECT verdict at the
current head fails audit_no_defects_at_head, so a defect the
audit proves cannot be silently carried.

Isolation: the sweep uses unique GPE07Audit owners and cleans
them up; audit_isolation fingerprints form/state (names +
sha256) before and after and requires byte-identical state —
a fresh Program() is never assumed empty, and the sweep must
leave no residue in the real state directory.

FAILING-FIRST RECORD (at Part head 53368fb1, before the build):
this suite failed on import — form.mandell.dell_audit did not
exist (the whole-address execution audit had never been run as
one body; only the static standing table and the D1 bare survey
existed, neither of which renders per-address verdicts).

REPAIR NOTE (2026-11-21, CI smoke failure at baebae3d): the
first CI run of this suite at baebae3d failed in the form-smoke
job (Python 3.11) with the suite as the only red entry
(312/313). Two instrument defects were found:

1. NO_COUNT (proven locally through the regress harness at the
   exact head): smoke() never printed an n/m tally — the tally
   was printed only under __main__ — and the harness scores an
   entry GREEN only when the last printed n/m count has
   n == m. Run through the harness at the exact CI prefix
   (the 127 LIST entries up to and including this one, in one
   private copy, accumulated state matching CI's file count
   exactly), every check passed and smoke() returned True, yet
   the entry still scored RED for lack of a count. The suite as
   committed could never be GREEN through the harness. Fixed:
   smoke() prints the tally itself.
2. The ledger byte-pinned an executor bookkeeping count:
   the Side effects column included "history +N (execution
   bookkeeping)" — a count of entries the executor journals
   per execution. The audit's own contract (dell_audit module
   docstring) states bookkeeping is never a Dell side effect;
   it is executor mechanics, not a Dell contract fact, and a
   ledger that byte-pins it drifts with journaling mechanics
   rather than with Dell contracts. In CI (Python 3.11) the
   drift check was the suite's only failing check on both
   regress passes; under 3.12 the render is byte-identical
   across clean state, foreign accumulated state, the faithful
   in-harness prefix reproduction, timezone variants and
   PYTHONHASHSEED variants, so the exact differing field could
   not be isolated locally (no 3.11 interpreter on the build
   machine; the CI capture withholds child stdout beyond the
   failing check's name by design). Fixed by excluding the
   bookkeeping count from the ledger render (disclosed in the
   ledger's Scope section and in dell_audit): every contract
   fact — verdicts, bases, reasons, legs, canonical-change
   descriptions, counts — remains byte-pinned and derived from
   the live sweep, and the drift check now names the differing
   Dell rows on failure so any recurrence is self-locating.
"""

from __future__ import annotations

import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CHECKS = []


def check(name, cond, detail=""):
    CHECKS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


def _state_fingerprint():
    from form.persist import _STATE_DIR
    fp = {}
    for name in sorted(os.listdir(_STATE_DIR)):
        path = os.path.join(_STATE_DIR, name)
        if os.path.isfile(path):
            with open(path, "rb") as f:
                fp[name] = hashlib.sha256(f.read()).hexdigest()
    return fp


def run_all():
    from form.mandell import dell_audit
    from form.mandell.dell_cards import english_named_dells
    from form.mandell.registry import (
        NAMED, active_core_count, execution_standing)

    fp_before = _state_fingerprint()
    records = dell_audit.run_audit()
    by_dell = {r["dell"]: r for r in records}

    check("audit_coverage_exactly_100",
          len(records) == 100 and sorted(by_dell) == list(range(100)),
          f"records={len(records)}")

    required_cols = ("name", "manor", "namespace", "dispatch",
                     "handler", "signature", "required_args",
                     "expected", "class", "side_effects", "door",
                     "bare_outcome", "tests", "verdict", "basis")
    missing = [(r["dell"], c) for r in records for c in required_cols
               if r.get(c) in (None, "")]
    check("audit_columns_complete", not missing,
          f"missing={missing[:5]}")

    check("audit_verdict_vocabulary",
          all(r["verdict"] in dell_audit.VERDICTS for r in records),
          "verdicts="
          + ",".join(sorted({r['verdict'] for r in records})))

    unresolved = [r["dell"] for r in records if not r["handler_resolved"]]
    check("audit_handlers_resolve", not unresolved,
          f"unresolved={unresolved}")

    n_i = sum(1 for r in records if r["namespace"] == "CORE_I")
    n_ii = sum(1 for r in records if r["namespace"] == "CORE_II")
    check("audit_reconciliation_51_49_100",
          n_i == 51 and n_ii == 49 and active_core_count() == 100,
          f"core_i={n_i} core_ii={n_ii} active={active_core_count()}")

    st151 = execution_standing(151)
    check("audit_151_not_a_core_dell",
          151 not in by_dell
          and st151["standing"] == "RESERVED_NOT_ACTIVE"
          and NAMED.get("Harmonidell") == 151,
          f"standing151={st151['standing']}")

    bad_refusals = [r["dell"] for r in records
                    if r["bare_outcome"] == "refused"
                    and (not r["reason"] or r["canonical_change"])]
    check("audit_refusal_integrity", not bad_refusals,
          f"bad={bad_refusals}")

    unproven = [r["dell"] for r in records
                if r["verdict"] == "CONTRACT_PROVEN" and not r["legs"]]
    check("audit_success_honesty", not unproven,
          f"unproven={unproven}")

    defects = [r["dell"] for r in records if r["verdict"] == "DEFECT"]
    check("audit_no_defects_at_head", not defects,
          f"defects={defects}")

    mo = [r["dell"] for r in records if r["verdict"] == "MESSAGE_ONLY"]
    check("audit_message_only_named",
          len(mo) >= 1
          and all("bare" in r["basis"] for r in records
                  if r["verdict"] == "MESSAGE_ONLY"),
          f"message_only={mo}")

    check("audit_honest_refusals_pinned",
          by_dell[44]["reason"] == "bridge_unavailable"
          and by_dell[47]["reason"] == "embed_unavailable"
          and by_dell[44]["verdict"] == "CONTRACT_PROVEN"
          and by_dell[47]["verdict"] == "CONTRACT_PROVEN",
          f"44={by_dell[44]['reason']} 47={by_dell[47]['reason']}")

    sig_tokens = {85: "malformed_move", 86: "delete_missing",
                  87: "replace_missing", 88: "patch_miss"}
    sig_ok = all(by_dell[n]["bare_outcome"] == "refused"
                 and by_dell[n]["reason"].startswith(tok)
                 for n, tok in sig_tokens.items())
    check("audit_signature_refusals_match", sig_ok,
          "85-88 bare refusals name their signature-declared failures")

    named = english_named_dells()
    check("audit_english_reachability_recorded",
          all(r["english_named"] == (r["dell"] in named) for r in records),
          f"english_named={sum(1 for r in records if r['english_named'])}")

    records2 = dell_audit.run_audit()
    seq1 = [(r["dell"], r["verdict"], r["basis"], r["reason"])
            for r in records]
    seq2 = [(r["dell"], r["verdict"], r["basis"], r["reason"])
            for r in records2]
    check("audit_determinism", seq1 == seq2,
          "two sweeps -> identical verdicts/bases/reasons")

    ledger_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "director-reports", "PART_II_GPE07_AUDIT_LEDGER_2026-11-21.md")
    with open(ledger_path, encoding="utf-8") as f:
        committed = f.read()
    fresh_render = dell_audit.render_ledger_md(records)
    drift_detail = "committed ledger == fresh render"
    if committed != fresh_render:
        # Name the differing Dell rows so a drift failure is
        # self-locating in any environment that runs the suite.
        old_rows = {ln.split("|")[1].strip(): ln
                    for ln in committed.splitlines()
                    if ln.startswith("| ") and ln.split("|")[1].strip()
                    .isdigit()}
        new_rows = {ln.split("|")[1].strip(): ln
                    for ln in fresh_render.splitlines()
                    if ln.startswith("| ") and ln.split("|")[1].strip()
                    .isdigit()}
        differing = sorted(
            (k for k in set(old_rows) | set(new_rows)
             if old_rows.get(k) != new_rows.get(k)), key=int)
        header_diff = (committed.split("## Per-address records")[0]
                       != fresh_render.split("## Per-address records")[0])
        drift_detail = (f"ledger drift: differing Dell rows={differing[:8]}"
                        f" header_differs={header_diff}")
    check("audit_ledger_drift",
          committed == fresh_render,
          drift_detail)

    fp_after = _state_fingerprint()
    check("audit_isolation", fp_before == fp_after,
          f"state files before={len(fp_before)} after={len(fp_after)}")


def smoke() -> bool:
    CHECKS.clear()
    try:
        run_all()
    except Exception as e:
        print(f"FAIL gpe07_audit raised {type(e).__name__}: {e}")
        return False
    ok = all(c for _, c in CHECKS)
    # The regress harness scores an entry by the last n/m count
    # printed on stdout; the tally must be printed here, in the
    # harness-called function — not only under __main__ (repair
    # note, 2026-11-21: without it the entry scored NO_COUNT and
    # could never be GREEN through the harness).
    n = sum(1 for _, c in CHECKS if c)
    print(f"GP-E07 audit: {n}/{len(CHECKS)} checks passed")
    return ok


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
