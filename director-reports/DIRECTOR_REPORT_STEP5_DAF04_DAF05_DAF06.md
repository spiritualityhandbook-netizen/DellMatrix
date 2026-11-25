# DIRECTOR REPORT — Step 5: DAF-04 + DAF-05 + DAF-06
Director Certification Audit 2026-10-31, §8 step 5.
Submitted by Uni; HELD for the Director. This report is
evidence submitted for re-ruling, never a certificate.

## Findings addressed
- DAF-04 (P1): pending proposals lose receipt history —
  five imports of 50 receipts left the first proposal's
  export at 0/50 receipts; the global dropped counter (50)
  was correct, the proposal's provenance was silently
  incomplete.
- DAF-05 (P2): reload reverses the effective eviction
  order — the shared loader returns records newest-first,
  so pop-first writers evicted the NEWEST record
  (origin199 died, origin000 survived).
- DAF-06 (P1): capacity refusal left a durable partial
  import — import 201 into 200 live seed payloads raised
  ExchangeError, but the pending proposal remained durable
  after reload with NO seed record, re-exporting as a
  silent "reconstructed" packet with chain "".

## Frozen candidate
PR #166. Candidate f1c581d3ef1c70bf7378ea612e4a891be9f1d8b3,
tree 2cafa4e54a31ff5d2c067c9b755388de741c8be7, base a60bb22.
Merged as 4405479bc1ca7126e8f926adb08f2a495d18185a (normal
merge commit; parents a60bb22 + f1c581d; merge tree
2cafa4e == candidate tree).

## Before (executed on unmodified a60bb22, probe)
step5_probe.py: DAF-04 first proposal receipts 0, export 0,
dropped_total 50 (BUG). DAF-05 loaded-first origin199,
origin199 evicted, origin000 survives (BUG). DAF-06
raised=true but proposals 200 -> 201, partial proposal
durable after reload, seed payload null, re-export
provenance=reconstructed chain="" (BUG).

## Fix (bounded, canonical owners only)
- session_section.oldest_key: the one explicit eviction
  victim — oldest by ts, ties by iteration/insertion order
  (stable across save/load). Raw dict order is never the
  authority. Applied to exchange.record_receipt,
  design_loop.record_event, director_session._record, and
  the exchange seed victim (oldest NON-LIVE payload).
- exchange._preflight_import (after the protected-material
  screen, BEFORE nursery.add): seeds at cap with no
  non-live victim -> ExchangeError, zero mutation; receipts
  overflow whose oldest-first victims include any live
  proposal's receipts -> ExchangeError, zero mutation.
- Receipt provenance: record_seed_payload stamps
  receipts_expected + receipts_hash (sha256 over the
  order-insensitive canonical receipt multiset). The seed
  validator accepts the pair optionally (legacy entries
  stay valid). build_packet, on the inherited-receipts path
  only, refuses when present receipts differ in count or
  digest; it also refuses an exchange-origin proposal with
  no stored seed payload ("reconstructed" remains only for
  native proposals).
- Rollback: any failure after nursery.add removes the
  proposal's receipts, its seed payload, and the proposal,
  and persists via nursery.save() before the original
  ExchangeError propagates. Evictions already performed
  against non-live records stay counted.

## After (executed)
Post-fix probe: 5th import refused at index 4, first
proposal 50/50 in store and export; origin000 evicted,
origin199 survives; proposals 200 -> 200, no partial after
reload. All three BUG flags false.

## Suite, mutants, regressions
- New suite form/step5_exchange_boundary_test.py: 20/20,
  in the regress LIST (207 -> 208 entries).
- Defect-restoring mutants, each killed, worktree verified
  clean after each inverse-edit revert: M1 preflight
  removed -> suite RED; M2 receipts eviction restored to
  dict-first -> 19/20 (DAF-05 reload leg fails); M3
  provenance check removed -> 19/20; M4 rollback removed
  -> 19/20 (partial proposal remains in memory AND
  durable). Restored code re-verified 20/20.
- Neighborhoods green: af34 19/19, af6 13/13, af5,
  p9_exchange, repair_r2, repair_r4,
  persist_full_roundtrip 114/114, pp2b 18/18, step3 23/23,
  step4 27/27, symbiosis_ledger 39/39.
- Regress x3 on the candidate: 208/208 GREEN
  (fwd / --twice / --order rev).

## Exact-head CI (verified complete in a separate step,
before merge)
- Python package run 41213256472: SUCCESS, completed
  2026-10-31T15:07:01Z, headSha f1c581d.
- Form smoke run 41213256194: SUCCESS, completed
  2026-10-31T15:19:45Z, headSha f1c581d.

## Fresh clone
Clone at merge 4405479: regress 208/208 GREEN.

## Limitations
- Receipt provenance is stamped at import (the Director's
  executed DAF-04 case). Receipts recorded directly via
  record_receipt for a native proposal carry no
  per-proposal expected-count witness; their eviction
  remains oldest-first and globally counted (AF34
  contract), and their export presents what is present.
- Legacy imported proposals whose seed entries predate
  the provenance pair export their seed byte-identical
  (AF34 pin) with no receipt-completeness check — absence
  of the pair is never upgraded to a completeness claim.
- Rollback cannot un-evict non-live records a failed
  import already displaced; those losses stay counted,
  and the import itself leaves no trace.
- Third-party scanning remains EVALUATION_UNAVAILABLE.

## Ruling requested (bounded)
Re-rule DAF-04, DAF-05, and DAF-06 at candidate f1c581d /
merge 4405479: coordinated Exchange boundary (shared
oldest-first eviction, preflight zero-mutation refusal,
witnessed receipt provenance, rollback with no durable
partial import, damaged-import export refusal). This also
re-presents finding A1 (Exchange as a whole) for the
step-14 admission packet.
