# DIRECTOR REPORT — 72-13: Typed-Signature Error/Coercion Contract Audit

Circuit: 72-13 (Master Objective Register §6.7) — "Audit 17
typed-signature error/coercion contracts (P1/I) (= SM-17,
SM-19)." Remaining action as registered: "Per-signature
contract audit across all 17; no signature expansion
without authorization." Executed as an AUDIT circuit under
Sleep Protocol v2 resolving to one bounded record repair.

Branch: uni/72-13-typed-signature-audit, base main
6b0454fc8954971739c3f83bfb6bcb88562d9301 (PR #317 merge).
Suite SHA: d8c5f16dd6b04f4a08610eb641a643580f77e71c.
Record-repair SHA: 97251a51eba7a2c3d7bb10ace2befbf2fe3a1c47.
Defect classification: documentation drift (recorded in the
report, §2; no DD number — no behavior was defective).

## 1. Audit result (FACT)

The shared gate contract holds for all 17 typed Dells.
Probe 1 (39/39, PUBLIC_ENTRY_PATH via execute_seed): for
every typed Dell — UNKNOWN_ROLE refusal with zero mutation
(store/selected/scope/groups snapshot), MISSING_REQUIRED
refusal with zero mutation where constructible from valid
roles (55, 85, 87, 88, 8), ARGUMENT_CONFLICT refusal with
zero mutation (all 16 Core II typed; Dell 8 pinned in its
own suite). Probe 2 (14/14) mapped the per-Dell behaviors
the signatures imply (88 empty value allowed; 87 omitted
`new` is a documented no-op success; 85 duplicate role
refused at parse; 56's reference resolution; 57's typed
type_mismatch fails the atom) — all signature-consistent.

Existing per-Dell deep suites cover 16 of 17 (the fourteen
d1_dell* suites + the certified d1_typed_52_53 suite); the
gate suites cover the unregistered-Dell refusals. Dell 55
(Set) was the only typed Dell with no dedicated suite.

## 2. The one drift found

Dell 55's established coercions were documented NOWHERE in
its canonical signature record (signatures.py), whose
output said only "Sets st.store[key] = value (create or
overwrite)":

1. A legacy label with no "=" stores the literal "1"
   (pinned as intentional by d1_registry_coreii_a_test).
2. An empty key coerces to the literal key "value" —
   legacy ("=orphan", or a bare label) and typed
   (key="") alike (legacy pinned by the registry suite;
   typed path probe-verified in this audit).
3. The legacy path strips key/value whitespace; the typed
   roles path is lossless (the DAF-01 typed-lossless law).
4. A typed key-only call stores "" (signature-consistent:
   value optional, may be empty).

This is documentation drift, not a behavior defect:
behaviors 1–2 are pinned legacy contract — changing them
would break a certified registry pin and would need a
Director ruling, not a FIX circuit. No other Dell showed
an undocumented coercion in the sweep.

## 3. Repair (record only; no behavior change)

- New suite form/typed_signature_contracts_test.py (67
  checks; registered in form/regress.py — canonical count
  248) pins the cross-signature gate contract for all 17,
  the Dell 55 coercion contract, and asserts every typed
  signature's failures text is established (not UNKNOWN)
  and that Dell 55's signature text documents coercions
  1–4. Failing-first at the unrepaired head: 64/67 —
  exactly the three documentation checks fail.
- form/mandell/signatures.py: Dell 55's output text now
  records the four established coercions verbatim. Same
  Dell, same roles, no signature expansion.
- form/mandell/DELL_PROOF_CARDS.md regenerated with the
  existing renderer (exactly one line changes — the Dell
  55 output line); the D1 proof-cards suite, which pins
  committed == fresh render, passes 6/6.

## 4. Verification

- Suite: 64/67 failing-first → 67/67 after the repair.
- Mutant: restoring the drifted one-line output text →
  64/67, exactly the three documentation checks fail;
  inverse-reverted, tree clean, suite back to 67/67.
- Regression at the repair SHA (logs
  hidden_files/72-13_logs/run1/): TERMINAL GREEN 248/248 x3 (fwd / --twice / --order rev; LEG1_RC=LEG2_RC=LEG3_RC=0, CHAIN_DONE present; the new suite runs inside the harness at 67/67)
- CI at the final PR head: ALL TERMINAL PASS at final head 54bb854 — Python package run 42326464425 (3.10 + 3.11), Studio Browser Acceptance run 42326464409, Form smoke run 42326464379 (PASS, 16m35s). PR #318 MERGED 2026-11-06: merge commit 2893e3d390d72ade13c0f2a5da53ff00c6968503, tree 8f83b144d57906ff84129fe28a4fabf9fa65a1ad; merged-main CI terminal SUCCESS (Python package 42327922946, Form smoke 42327922971). Director verdict (2026-11-06 20:35 CST, archived in the 72-19 circuit records): ALL_AI_CONFIRMATION_PASS bounded; Q-72-13.1 YES; Q-72-13.2 legacy coercions retained as compatibility contract.

## 5. Records carried in this PR

- This report + INDEX row.
- DIRECTOR_REPORT_G04_FORCEFIELD_RESTORATION.md: the
  CI/merge receipt placeholder completed (final-head CI
  all terminal PASS — package 42319878197, browser-
  acceptance 42319878212, smoke 42319878231 PASS 16m24s;
  PR #317 merged 6b0454fc8954971739c3f83bfb6bcb88562d9301,
  tree 37eab0a206ecf4d0f12f287e54e141f84d02bce0;
  merged-main CI terminal SUCCESS — package 42321548225,
  Form smoke 42321548267).
- Register: 72-13 row updated (per-signature audit landed;
  status stays PARTIAL — the row's wider SM-17/SM-19 scope
  is not exhausted by this audit).

## Anticipated probes

- "Why is a documentation fix a circuit at all?" — The
  signature record is the canonical contract the gate,
  the proof cards, and the D1 deepening all read. A record
  that omits four established coercions is how the next
  worker 'discovers' them as bugs and 'fixes' pinned
  legacy behavior. The audit's primary deliverable is the
  17-Dell contract proof; the repair is its bounded tail.
- "Are the coercions themselves right?" — Out of this
  circuit's authority: 1–2 are Director-era pinned legacy
  contract (the registry suite pins them as intentional).
  If you want them revisited, that is a behavior-change
  ruling; Q-72-13.2 offers it explicitly rather than
  smuggling it into a record fix.

## Questions for the Director

- Q-72-13.1: Confirm the audit + record repair satisfies
  the register's per-signature audit action for 72-13
  (row stays PARTIAL for its wider scope), or name the
  signatures you want probed deeper.
- Q-72-13.2: Dell 55's legacy coercions (no-'=' stores
  '1'; empty key becomes "value") are pinned as
  intentional. Do they stand as permanent legacy contract,
  or should a future circuit propose their removal under
  your ruling?
