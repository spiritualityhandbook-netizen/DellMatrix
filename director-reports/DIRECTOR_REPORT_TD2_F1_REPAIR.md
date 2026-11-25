# DIRECTOR REPORT — TD-2 F1 REPAIR (Sandbox Gate Malformed-Endpoint Refusal)

**Circuit:** TD-2 F1 repair, ordered by Director hourly review #3 (2026-11-04 23:34 CST, archived at `director-reports/responses/DIRECTOR_REVIEW_EMAIL_2026-11-04_TD2_B2.md`): TD-2 disposition was CORRECTION_REQUIRED, no ALL_AI_CONFIRMATION_PASS. This packet is the one bounded repair the review ordered. TD-3 remains unauthorized; the TD-2 line otherwise stays stopped at its frozen candidate.
**Branch:** `uni/td2-f1-sandbox-repair`. **Repair commit:** `a0f2606797476f7201916bdb0db729a4ad666959` on merged main `843a44c`. This report rides in the same PR; CI evidence is read at the PR's final head.
**Status:** SUBMITTED for Director review. Uni label on merge: MERGED_VERIFIED_BY_UNI (not a certification).

## The finding (F1) — confirmed real, reproduced failing-first

`form/mandell/unit_containment.py`: `_isolation_key()` keyed a sandboxed unit with a missing `sandbox_id` as `(True, None)`, and `_check_sandbox()` refused only *unequal* keys. Two malformed sandboxed units therefore compared **equal** and proceeded to lazy binding and graph containment — contradicting the module's fail-closed claim. The v1 suite covered distinct keys and the same valid key, and the SWAT pre-mortem covered malformed-vs-unsandboxed; **malformed-vs-malformed was never tested** — the exact sibling case. Uni owns the miss: the gate compared keys for equality but never positively validated either key's well-formedness (the §7 positive-evidence failure class, in gate form: *equality of unvalidated keys is not proof of a valid key*).

## The repair (mechanism, not symptom)

`_check_sandbox` now validates **each endpoint independently, before any mint**: a new `_malformed_sandbox(unit)` predicate (sandboxed claim with a `sandbox_id` that is missing, empty, or not a string) makes `_check_sandbox` raise `ContainmentRefused("sandbox_boundary", ...)` naming the malformed unit, **regardless of the other endpoint**. Key-equality comparison is unchanged and now only ever compares well-formed keys. Same-valid-sandbox containment is preserved (existing checks green). Sibling search: the lifecycle gate was checked for the same class — it uses validated Idea loading (positive validation), not equality of unvalidated values; no other equality-of-unvalidated-keys gate exists in the containment path.

## Evidence

- **Failing-first:** the new both-malformed check fails on the pre-repair code (nest proceeds instead of refusing) and passes after the repair — recorded in the Cycle 7 run record.
- **Targeted suite:** `form/track_d_td2_test.py` **33/33 GREEN** (28 v1 checks + 5 F1 checks ordered by the review: both endpoints `sandbox_id=None`; empty-string id; mixed valid/invalid; malformed via **reparent** as well as nest; unboxed recovery after refusal — asserting `sandbox_boundary`, zero new Ideas, unchanged graph, zero new bindings).
- **Mutant:** the F1 refusal block removed → killed by the both-malformed check; reverted by inverse edit (Cycle 7 record).
- **Full regression ×3 (sequential, main session, terminal logs):** fwd **236/236 GREEN**; `--twice` **236/236 GREEN**; `--order rev` **236/236 GREEN** at branch head `21627b7` (repair + review-archive commits).
- **Fresh clone:** clean clone checked out at `21627b7`: targeted suite **33/33 GREEN**.
- **Exact-head CI:** this PR's checks at its final head (merge only on all terminal PASS per the hard gate).
- Test realism unchanged: INTEGRATION (public Program API + REPL handler path), not REAL_USER_PATH.

## Boundaries (unchanged from the TD-2 packet, restated)

No cross-file atomicity is claimed; direct SemanticGraph writers outside the bridge are not lock-fenced; bridge-level propagation fault-injection is not in the suite. PR #291's merge stands under Uni's label only — this repair does not retroactively certify TD-2 v1, and its disposition remains the Director's to give on the repaired head.

## Anticipated probes

- *"Empty string the other way — invalid child, valid parent, via promote?"* — Promote takes a single endpoint and never crosses a sandbox boundary (it removes containment); the two-endpoint ops (nest, reparent) both route through `_check_sandbox`, and the mixed valid/invalid check covers nest while the F1 reparent check covers the second op.
- *"A unit that is not sandboxed but carries a stray sandbox_id?"* — Keys as `(False, None)` (unsandboxed); its stray id is inert metadata, never used for isolation decisions — same behavior as v1, unchanged by this repair.

## Questions for the Director

1. TD-2 disposition on the repaired head: certify within the stated boundaries, or are further probes required?
2. The B-2 evidence bundle (PR #292, head 4069d9e: probe script + JSON + SHA-256 manifest + reproducibility note + independent replay) — sufficient to close B-2 as a bounded investigation, or is a further tier of probing required?
