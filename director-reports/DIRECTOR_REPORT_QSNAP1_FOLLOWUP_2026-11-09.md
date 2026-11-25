# DIRECTOR REPORT — Q-SNAP.1 FOLLOW-UP REPAIR: revalidation completeness (QSNAP1-1/2/3)

Circuit: bounded FIX-FIRST follow-up ordered by the Director's 2026-11-09 00:32 CST
ruling (archived: responses/DIRECTOR_REVIEW_EMAIL_2026-11-09_QSNAP1_HOLD.md).
Scope: the G-11 snapshot-retrieval build merged as PR #336 (main 693fa77).
NOT in scope: Proposal B (resequenced by the ruling to follow this circuit),
Q1/#294, R-1 implementation, C-A/F2.

Disposition requested: Q-SNAP.1 certification of G-11, resubmitted on the
repaired code (see Questions).

## Gap -> repair (unique defect IDs, per the ruling)

**QSNAP1-1 — revalidation field incompleteness (gap 1).**
`_revalidate_retrieved` compared status/label/words/detail/revision_number
while `_source_identity` hashes goals and coordinates: a goals or coordinates
edit between retrieval and incorporation passed revalidation against a
changed source identity. REPAIR: revalidation now compares the full
semantically relevant field set, including goals and the unit x/y
coordinates. The suite demonstrates a goals edit and a coordinates edit in
the retrieval->incorporation window; both are refused as stale.

**QSNAP1-2 — relate_field retrieval revalidation boundary (gap 2).**
`relate_field` retrieves an out-of-slice target via `_retrieve_into_index`
and incorporated it without the explicit retrieval revalidation the `_verb`
path performs. REPAIR: explicit revalidation plumbing on the relate_field
path before Nursery incorporation, with deterministic mutation / deletion /
fade / supersede race tests in the suite.

**QSNAP1-3 — retrieval bound counted input elements (gap 3).**
The 16-ID bound counted caller input elements, so duplicate IDs consumed
the budget ambiguously and ID length was unbounded. REPAIR: the bound
applies to DISTINCT ids (16 distinct per round); each ID is length-bounded
(256 chars) with a sanitized refusal — no unbounded input, no raw-error
exposure. Pathological-length and duplicate-heavy inputs are tested.

## Evidence (T3, stateful)

- Failing-first at base 693fa77 (commit 43caa50): suite
  form/snapshot_revalidation_test.py **9/15** — all 6 defect checks fail,
  9 controls pass.
- Post-repair (commit 5a3e96a): **15/15**.
- Mutant (pre-repair narrow field set restored): **11/15**, failing with
  exactly the QSNAP1-1/2 profile — killed; reverted by inverse edit.
- Neighbours at the same head: snapshot_retrieval 16/16,
  track_c_dock_verbs 29/29, pp4_bimo_dock 16/16, nursery_confirm_race 57/57.
- Regression x3 at candidate head 5a3e96a: **261/261 TERMINAL GREEN x3**
  (fwd / --twice / --order rev), logs at evidence/qsnap1-followup/
  (chain_fixed.log, fixed_leg1-3.log). Suite registered in form/regress.py
  (canonical count 260 -> 261).
- Exact-head CI and the §32 pre-merge freshness check are recorded in the
  INDEX row for this report at merge time.

## The in-chain daf09 discrepancy — full disclosure (NOT a G-11 defect)

The first two regression campaigns at this head failed ONLY
form.daf09_timeout_tree_test (28/31) inside full chains, in its
cancellation block: the suite's cancel_driver subprocess did not exit
within its 20s window after SIGINT; the no-post-cancel-marker and
bystander checks failed consequentially. A third campaign was lost to a
VM replacement mid-leg (NO RESULT). Differentials at the same head:
suite standalone 31/31 (repeated, incl. fresh clones); harness --passk
x3 green; reverse-order predecessor replication (25 suites) green with
daf09 31/31; the post-hoc rerun inside the failed chain's own copy
31/31. The Q-SNAP.1 diff touches no daf09 path.

Mechanism, identified by instrumented reproduction (diag2/diag3 logs in
evidence/qsnap1-followup/): a watchdog sampling /proc/<cancel_driver>/
status during the hang captured **SigIgn 0000000001001007 — SIGINT
inherited as SIG_IGN**. A non-interactive shell launching a process in
the background sets SIGINT/SIGQUIT to SIG_IGN in the child (no job
control); the disposition is inherited by every descendant, and CPython
preserves an inherited SIG_IGN for SIGINT instead of installing the
KeyboardInterrupt handler — so the driver's SIGINT was a no-op. Every
passing differential had been launched in a shell foreground; every
failing chain in the background. Correcting the LAUNCH (the chain
process resets SIGINT/SIGQUIT to SIG_DFL before running) produced the
x3 GREEN above with no product or suite code changed. The operational
rule is recorded in the workspace TOOLS.md (Background-Shell Signal
Inheritance, 2026-11-09).

Non-claims, explicitly: this accounts for the in-chain failures on THIS
machine's chains. It is not evidence about the Director's independent
DAF-09 environment result, and DAF-09 certification remains WITHHELD;
nothing in this circuit touches that question.

## Product-relevant finding (no change made)

The same inheritance applies to any real DellMatrix process launched
from a background/nohup context: its cancellation surface starts deaf.
Whether run_entry / the REPL entry should explicitly establish the
SIGINT disposition for itself or its children is a design question —
posed as Q-SNAP.3 below; this circuit changed no product behavior for it.

## Anticipated probes

- "Why did the snapshot circuit's own x3 (36d1231) not hit this?" —
  That chain was launched through the runtime's background-exec path,
  whose shell does not apply the background-ignore; the Q-SNAP.1 chains
  were launched via setsid/nohup from an interactive-less shell, which
  does. Launch method, not code, is the variable in both directions.
- "Is 256 chars principled?" — It bounds caller input at the retrieval
  boundary; canonical unit IDs in the field are far shorter (content-
  derived hex). The bound is a refusal limit, not a truncation.
- "Does relate_field revalidation duplicate _verb?" — It reuses the same
  revalidation boundary; no second authority was created.

## Questions for the Director

- **Q-SNAP.1 (resubmitted):** certification of G-11 within the amended
  Q-SC.3 scope, on the repaired head and the evidence above.
- **Q-SNAP.3:** the inherited-SIG_IGN finding — authorize a bounded
  hardening circuit (entry points establish SIGINT disposition),
  record as a finding only, or decline?
