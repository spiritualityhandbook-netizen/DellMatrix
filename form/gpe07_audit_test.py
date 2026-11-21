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
    check("audit_ledger_drift",
          committed == dell_audit.render_ledger_md(records),
          "committed ledger == fresh render")

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
    return all(ok for _, ok in CHECKS)


if __name__ == "__main__":
    ok = smoke()
    n = sum(1 for _, c in CHECKS if c)
    print(f"GP-E07 audit: {n}/{len(CHECKS)} checks passed")
    sys.exit(0 if ok else 1)
