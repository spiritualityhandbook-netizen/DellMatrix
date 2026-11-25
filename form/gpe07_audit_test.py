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

REPAIR NOTE — AUDIT BOUNDARY (2026-11-25, Director contract
ruling 7176510943 on classification 7175094313): two product
contracts collided on any tree carrying both. Q-35.1's
atomic_write appends a mint/tombstone record to the written
directory's .dmtmp-ledger.jsonl on EVERY save (append-only
provenance ledger), and ordinary Program construction during
the sweep saves each audit owner's nursery file through it —
so the sweep deterministically grew a ledger file in the real
state directory that is not owner-named and that cleanup may
never touch, and the byte-identical fingerprint could never
match. Neither contract moves: GP-E07's byte-identical
real-state guarantee and Q-35.1's append-only ledger both
stand at full strength. The repair moves the AUDIT BOUNDARY
instead, exactly as the ruling directs: the sweep's real
Program operations — nursery writes and ledger creation
included — run through the normal dell_audit.run_audit entry
point in a child process whose tree is a private disposable
copy of this one (state paths are file-location-relative
across form/persist and form/dell_matrix, i.e. process-global,
so process isolation is the lawful seam). The fingerprint over
the ENTIRE real state directory is kept unchanged and now
passes by construction: the audit never writes to the real
directory at all. The shared ledger is never truncated,
filtered or restored by audit cleanup — it is simply never
the audit's directory. Demonstrated at the repair head: a
pre-existing real ledger and unrelated owner bytes survive
repeated audits byte-identically, and the 100-Dell report
still returns.

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

REPAIR NOTE — ROUND 2 (2026-11-21, CI smoke failure at
e084b82, the round-1 repair head): audit_ledger_drift failed
again in CI on both regress passes (15/16, drift the only red),
while every local run at the branch head stayed green. The
round-1 disclosure stood: the differing byte could not be
isolated without a 3.11 interpreter. With Python 3.11.18
installed, the bisection was completed and the cause is NOT
an interpreter, state, hash-seed or environment effect:

- Clean-state sweeps under 3.11.18 and 3.12.3 are
  byte-identical to the committed ledger; a faithful harness
  repro (regress._copy_tree + the 126-entry prefix as harness
  children under 3.11.18, 3,556 accumulated state files) is
  also byte-identical. Hash seeds 0-5 identical; the eleven
  MESSAGE_ONLY Dells' raw receipts are byte-identical before
  and after field enrichment.
- PR CI does not sweep the branch tree: it sweeps the PR's
  MERGE tree (branch merged into current main). In that tree
  exactly one record field differs — Dell 92 [Guard]'s
  `manor`, the declared registry description sourced from
  form/mandell/core_ii.py. Main revised that declared fact
  after this branch's ledger was generated ("Prevent
  execution unless conditions hold" -> "Ask 'may this
  proceed?': ALLOW when conditions hold, BLOCK when they do
  not"; dell_cards DEEP_NOTES and DELL_PROOF_CARDS moved with
  it). A suite run in the merge tree under 3.11.18 reproduces
  the CI signature exactly: 15/16, sole FAIL
  audit_ledger_drift, "differing Dell rows=['92']".

Classification: the varying field is a DECLARED CONTRACT
FACT (the GP-E07 contract requires declared name/manor per
address), revised on main by landed Part III work — not
executor mechanics, so it is NOT normalized or excluded;
the ledger keeps byte-pinning it. No verdict was derived
from it (Dell 92 is CONTRACT_PROVEN with identical legs and
basis in both trees; totals stay 89/11). The repair is the
honest one for a stale generated artifact: sync the branch
with main (merge ace82fa) and regenerate the ledger at the
new head — the regenerated ledger differs from the old one
in exactly the Dell 92 manor cell. Standing consequence,
disclosed: a ledger that byte-pins declared registry facts
goes stale whenever main revises a declared fact ahead of
the branch; the cure is branch sync + regeneration, never
editing the ledger to match an un-synced sweep.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

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


def _tree_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _run_audit_isolated():
    """Run the audit's two sweeps through the normal
    dell_audit.run_audit entry point in a child process whose
    tree is a private disposable copy of this one (Director
    contract ruling 7176510943; see the module docstring's
    audit-boundary repair note).

    State paths across form/persist and form/dell_matrix are
    derived from file locations, so a copied tree redirects
    every one of them — nursery writes and .dmtmp-ledger.jsonl
    creation included — into the private copy, which starts
    with NO state directory (the codebase's own regress
    _copy_tree idiom) and is deleted whole afterwards. The
    real state directory is never written by the audit, so the
    audit_isolation fingerprint over it stays at full strength.
    Returns (records, records2) — the two sweeps, run back to
    back in the child exactly as they ran in-process before.
    """
    root = _tree_root()
    tmp = tempfile.mkdtemp(prefix="gpe07_audit_")
    try:
        def ignore(d, names):
            skip = {n for n in names
                    if n == "__pycache__" or n.endswith((".pyc", ".pyo"))}
            if os.path.abspath(d) == os.path.abspath(root):
                skip |= {".git"} & set(names)
            if os.path.abspath(d) == os.path.join(root, "form"):
                # The private copy starts with no state directory
                # at all: the state dir is created fresh inside
                # the copy by the code under audit.
                skip |= {"state"} & set(names)
            return skip

        work = os.path.join(tmp, "src")
        shutil.copytree(root, work, ignore=ignore, symlinks=True)
        out_path = os.path.join(tmp, "records.json")
        child = os.path.join(work, "form", "gpe07_audit_test.py")
        env = dict(os.environ)
        env["PYTHONPATH"] = work
        proc = subprocess.run(
            [sys.executable, child, "--audit-child", out_path],
            cwd=work, env=env, capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(
                "isolated audit child failed "
                f"(rc={proc.returncode}): {(proc.stderr or '')[-800:]}")
        with open(out_path, encoding="utf-8") as f:
            sweeps = json.load(f)["sweeps"]
        return sweeps[0], sweeps[1]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _audit_child_main(argv):
    """Child-process entry (private disposable tree): run the
    normal audit entry point twice and write both sweeps'
    records as JSON to the path named by --audit-child."""
    from form.mandell import dell_audit
    out_path = argv[argv.index("--audit-child") + 1]
    sweeps = [dell_audit.run_audit(), dell_audit.run_audit()]
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"sweeps": sweeps}, f)
    return 0


def run_all():
    from form.mandell import dell_audit
    from form.mandell.dell_cards import english_named_dells
    from form.mandell.registry import (
        NAMED, active_core_count, execution_standing)

    fp_before = _state_fingerprint()
    records, records2 = _run_audit_isolated()
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
    if "--audit-child" in sys.argv:
        sys.exit(_audit_child_main(sys.argv))
    sys.exit(0 if smoke() else 1)
