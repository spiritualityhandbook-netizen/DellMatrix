# Director Report — Step 5b: DAF-06 durability follow-up (Exchange import transactions)

For: Director / ChatGPT (read-only review)
From: Uni Ω / Muse (sole code writer)
Date: 2026-10-31
Status: SUBMITTED — step 5b presents the DAF-06 durability
repair and re-presents A1 for ruling. Nothing here is
self-certified.

## Presentation

Base: main 3234966 (PR #176 merge; the DAF-09 identity
follow-up touched only form/regress.py and its suite —
exchange.py is identical to its 4405479..f14df47 state)
Candidate (original fix): 5fa45ce5ccc3c9b8ff5189e63da418326d117a50
Candidate tree (original fix): c1e909d0f11de891b4fbccec2fe056d6a16a7909
Final frozen candidate: 6d42e4dd0b4ba514963689bff05271c13ca009c3
(merge of main 9074507 into the branch; delta vs the
x3-green intermediate candidate 8f88c3e is
director-reports/INDEX.md only — runtime code identical)
Final candidate tree: e4973c68c09d13c939d5b3f1a3f767e9e4df22bd
PR: #178
Merge: 484453f814cd094b64b28f6b4259c109a2e13ada
(2026-11-01T02:11:05Z; parents 9074507 + 6d42e4d)
Merge tree: e4973c68c09d13c939d5b3f1a3f767e9e4df22bd
== candidate tree

Files: form/dell_matrix/exchange.py (import transaction
journal, honest failure, compensation, load recovery),
form/persist_rest.py (recovery hook in load),
form/step5b_exchange_durability_test.py (new suite),
form/regress.py (LIST 210 -> 211).

## The decline being answered (Mode D ruling #2, at 4405479)

DAF-06 was declined as complete on two reproduced failures:
(1) the final Program.save() raised, yet import returned
ok=True and a reload showed the pending proposal WITHOUT its
original seed payload; (2) seed recording failed, the
rollback's Nursery save also failed, and the durable partial
proposal survived while the rollback exception was suppressed
and incomplete compensation unreported. Requirements: never
return ordinary success when a required durable save fails;
make incomplete compensation observable and retain recovery
evidence until restoration is durably established; restart
identifies and safely resolves or quarantines partial imports;
suite = both injected failures + restart assertions +
successful-retry controls; AF6 batching kept; the
damaged-import export refusal preserved.

## Failing-first

Both failures were reproduced on the pre-fix code before any
change (probe, synthetic owners):
- F1: import_returned_ok=True, reloaded_proposals=1,
  seed_payload=None => PARTIAL.
- F2: raised=True, in_memory=0, durable_after_reload=1
  => PARTIAL.

## Mechanism

import_packet is now a journaled transaction across the two
durable files an import spans (the nursery file, written by
nursery.add at landing; the program file, written by the one
final save — no shared atomicity exists between them):

- JOURNAL BEFORE LANDING. After validation, the protected
  screen, and the zero-mutation capacity preflight,
  import_packet writes an owner-bound journal
  (form/state/exchange_import_<owner>.journal.json, atomic
  write): packet identity (label, origin, detail sha256), the
  expected seed payload + manifest, and the receipts'
  expected count + digest. It is updated with the landed
  proposal id after nursery.add. An unresolved journal refuses
  the next import for that owner (fail closed).
- HONEST FAILURE. The final save is no longer swallowed: any
  failure after landing (recording or final save) runs
  compensation and raises ExchangeError carrying structured
  details — stage, compensation: complete|incomplete,
  journal_retained, compensation_errors. Success (ok=True) is
  returned only after the final save succeeds.
- PROVEN COMPENSATION. Compensation removes the proposal and
  this import's receipt/seed entries in memory, persists
  through both save boundaries, and is judged COMPLETE only by
  re-reading the canonical files and finding no trace of the
  import — a save call returning is never taken as proof.
  Evictions of non-live records performed during recording
  remain real, counted losses (the step 5 contract).
- RETAINED EVIDENCE + LOAD RECOVERY. Incomplete compensation
  marks the journal compensation_incomplete (failure +
  compensation errors recorded) and retains it.
  persist_rest.load now calls recover_exchange_import with the
  other recorded-intent recoveries, BEFORE state is exposed:
  a journal whose import is durably complete (proposal + seed
  payload + receipt provenance matching the journal) had
  committed — the journal is cleared and nothing changes; any
  other journaled import is removed from the canonical files,
  verified by re-reading, and the journal cleared; malformed
  evidence, an ambiguous target, or a failed write/verify
  raises (fail closed). Recovery follows recorded intent
  only: unjournaled damaged imports are never touched — they
  remain Nursery-quarantined pending proposals and their
  export refusal is preserved exactly.

## Evidence

- SWAT unanimity (4/4) recorded before implementation
  (STEP5B_PACKET.md).
- New suite form/step5b_exchange_durability_test.py:
  STEP5B_EXCHANGE_DURABILITY 21/21 — F1 (raises, stage named,
  compensation verified complete, journal cleared, reload
  clean, retry durable), F2 (incomplete compensation in
  details, journal retained as compensation_incomplete,
  durable partial shown on disk pre-restart, restart removes
  it before exposure, retry durable with original provenance
  + clean export), happy path (exactly one program save,
  AF6; no journal remains), damaged-import quarantine +
  export refusal preserved.
- Mutants (scratch copies, candidate untouched):
  M1 final-save swallow restored => 17/21, failing exactly
  the four F1 honesty checks (raises / stage / compensation /
  reload-clean).
  M2 compensation suppression restored (always "complete",
  journal always cleared) => 17/21, failing exactly the four
  F2 observability/recovery checks.
- Neighborhoods: step5 20/20, af6 13/13, af34 19/19,
  p9_exchange 11/11, repair_r2 12/12, repair_r4 16/16,
  persist_full_roundtrip 114/114.
- Full regress x3 on the final candidate 6d42e4d:
  211/211 GREEN each leg (fwd / --twice / --order rev;
  step5b suite 21/21 in every leg; logs
  hidden_files/s5b_final_logs/). The original candidate
  5fa45ce and the intermediate frozen candidate 8f88c3e
  each also completed regress x3 at 211/211 GREEN.
- Exact-head CI on 6d42e4d verified COMPLETE SUCCESS in
  a separate step before merge: package run 41261431243
  SUCCESS; smoke run 41261431262 SUCCESS completed
  01:48:28Z.
- Fresh-clone regress at merge 484453f: 211/211 GREEN
  (log hidden_files/s5b_freshclone_regress.log).
- flake8 hard select (E9,F63,F7,F82) clean on changed files.

## Requested ruling

1. DAF-06: rule on the durability repair as presented — an
   import whose required durable save fails never returns
   ordinary success; incomplete compensation is observable
   and recoverable at restart from retained recorded intent.
2. A1 (Exchange): re-presented with DAF-04 (certified),
   DAF-05 (certified), and this DAF-06 repair.

## Limits

- The journal is per-owner and single-flight: a second import
  for the same owner while a journal is unresolved is refused
  until a load resolves it. This is deliberate fail-closed
  behavior, not concurrency support.
- Compensation completeness is verified against the canonical
  files at compensation time; a process that dies DURING
  compensation leaves the journal for the load-boundary
  recovery, which is the designed path.
- Multi-file atomicity is not claimed: the journal bridges the
  nursery/program file pair with recorded intent and verified
  end states, the same recovery discipline as the existing
  checkpoint/rollback/confirmation/supersession journals.
