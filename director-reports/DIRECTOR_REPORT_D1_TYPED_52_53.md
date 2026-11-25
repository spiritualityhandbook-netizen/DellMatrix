# DIRECTOR REPORT — D1-TYPED-52-53: typed signatures for Dell 52 (Filter) and Dell 53 (Scope)

Circuit: D1-TYPED-52-53 (Director wake review 2026-11-03, authorization relayed by Ace)
Base: main b6dd46b1fa1ae48aa5387ec8f474a421e86e4b87 (tree ebc88984c217c73e7b26f0e443f413fbf86c8bba)
Candidate: PR #250, branch uni/d1-typed-52-53, code head b798cad89c3d3eb537f1cefced1773823da27c8d (tree d1210424499af53b73bc33600793d7095313dc38); commits e87a28e (fix + suite + regress wiring) and b798cad (count pins + versioning). This report and the INDEX row ride in a following docs commit; CI was re-verified at the final head (see Verification).
Status: SUBMITTED for Director review. **NOT MERGED** — per the circuit's explicit stop condition, the merge waits for the Director's ruling. Merged is not claimed; certified is not claimed.

## What shipped

- `form/mandell/signatures.py`: registered typed signatures derived from the handler contracts — Dell 52 Filter, one optional string role `predicate` (derived_from query_ops.apply_query n==52); Dell 53 Scope, one optional string role `name` (derived_from core_ii_exec.execute_core_ii n==53) — plus the two `lower_args_to_lab` branches. **Zero handler changes.** Both handlers consume the whole label and never re-split it, so lowering is the lossless transport; the structured `roles` transport Dell 55 needed (DAF-01: its legacy path re-splits on "=" and can hit ambiguous_set) is not required here, and the typed==legacy twin check below proves sameness empirically.
- `form/d1_typed_52_53_test.py`: new 28-check suite (PUBLIC_ENTRY_PATH via `execute_seed` on a real Program), wired into `form/regress.py` (entries 223 -> 224).
- Live typed count 15 -> 17, applied ONLY after the behavioral proof passed, per the ruling: pins updated in `form/step11_public_contracts_test.py` (the limitation-correction check now pins 17 typed / 83 untyped with BOTH dated corrections present and the historical fields intact) and `form/mandell/d1_proof_cards_test.py` (pin + header note); `form/mandell/DELL_PROOF_CARDS.md` regenerated through the existing renderer (diff confined to the survey count, the 52/53 rows, and their two card sections).
- Step 11 record VERSIONED, never rewritten: `director-reports/DIRECTOR_REPORT_STEP11_CONTRACTS.md` gained an appended VERSION NOTE (diff: 26 insertions, 0 deletions — its certified text is byte-identical), and `form/mandell/limitation_knowledge.py` LEGACY_ONLY_SIGNATURE gained a second APPENDED dated correction (2026-11-03, this circuit) inside `dated_correction`; the 2026-10-27 evidence line, the original limitation field, and the 2026-11-01 correction are suite-pinned byte-intact. The Step 11 certificate stands for its frozen 15-typed scope.

## The defect (failures before)

Mechanism: `chain_exec._run_atom` validates and lowers typed args only when `signatures.has_signature(n)`; with no signature the parsed args are silently ignored and the atom executes on the legacy payload under ok=True.

Failing-first evidence on the unmodified base (evidence dir `hidden_files/d1_typed_52_53/`):
- Probe through the public executor (`probe_red.py`, log `red_probe.log`): 4/4 typed defects demonstrated — typed Filter left the selection un-narrowed under ok=True; bogus role `52[Filter](bogus="x")` silently executed ok=True; typed Scope to an existing group left scope="plane" under ok=True; typed Scope to a missing group silently accepted instead of the fail-closed refusal. Legacy controls correct in the same probe (legacy Filter narrows; legacy Scope switches and refuses `scope_unknown:nope`).
- Literal REPL (REAL_USER_PATH, `repl_red.log`): `52[Filter](predicate="garden")` executed as `Filter 2->2 cond=*` — the predicate never reached the handler in the real user path either.
- New suite on the unmodified tree: 8/28 (`suite_red.log`) — all 20 typed-behavior checks red, every legacy control green.

## Behavior after

- Probe on the fixed tree: 0/4 defects, legacy controls still correct (`green_probe.log`). REPL: `Filter 2->1 cond=garden`, and `53[Scope](name="nope")` refuses in the literal REPL ("Scope refused: unknown scope 'nope' (supported: plane)") (`repl_green.log`).
- Suite: 28/28 GREEN. Coverage of the Director's contract points: direct and chain execution for both Dells; honest atom receipts (including the refused-Scope chain receipt ok=False naming `scope_unknown:nope`, and unchanged scope after refusal); honest result cells; delimiter values riding whole (space — underscore-prefix match; "=" and ":" — honest empty, no split); unknown roles refused UNKNOWN_ROLE with zero mutation; typed+legacy conflicts refused ARGUMENT_CONFLICT before mutation, equal labels proceeding; empty typed values preserving legacy semantics (identity filter; Scope default "plane"); Scope's fail-closed rule intact on both paths; typed result byte-identical to a legacy-label twin (ok, selection, result cell).
- Conflict rule (stated per the directive): the existing gate law for every typed Dell — typed args lower to a label; a non-empty legacy label that differs refuses ARGUMENT_CONFLICT before any mutation; an equal label proceeds. Refusal classes for these string roles: UNKNOWN_ROLE (bogus role names), ARGUMENT_CONFLICT, parse-level duplicate-role refusal (DAF-07), and the handler's own scope_unknown. No non-string value can arrive via seed text (the parser produces strings only), so no additional type refusal exists to add.

## Mutants (defect-restoring, all reverted by inverse edit, diff verified clean)

- M1 — Filter registered under a wrong key (registration effectively removed): suite 16/28, reds exactly the typed-Filter + registry checks. Killed.
- M2 — Scope registered under a wrong key: suite 19/28, reds exactly the typed-Scope checks. Killed.
- M3 — Filter lowering branch neutralized (registration intact): suite 20/28 — lowering proven load-bearing, not decorative. Killed.
Restored tree re-verified 28/28 with an empty git diff before proceeding.

## Verification

- Siblings: d1_recon1_scope 17/17, d1_dell51_select 15/15, d1_dell54_query 12/12, d1_stale_probes 12/12, p12_closure 8/8.
- Pin suites after the count update: step11_public_contracts 31/31, d1_proof_cards 6/6 (includes committed-cards == fresh-render).
- Full regression, SEQUENTIALLY from the executing session, durable logs in the evidence dir: forward 224/224 GREEN (`regress_fwd.log`); --twice 224/224 + 224/224 GREEN (`regress_twice.log`); --order rev 224/224 GREEN (`regress_rev.log`).
- Exact-head CI at code head b798cad, verdict by direct gh query: package run 41651425500 completed/success (build 3.10 PASS, build 3.11 PASS), smoke run 41651425558 completed/success (10m47s).
- Fresh clone at exact head b798cad (tree d1210424 re-verified in the clone): suite 28/28, step11 31/31, proof cards 6/6, defect probe 0/4 with legacy controls correct, full clone regress 224/224 GREEN (`freshclone_regress.log`).
- Environment: Linux, Python 3.12.3 local; CI builds 3.10/3.11 + smoke. No environment-sensitive checks and no cross-environment discrepancy in this circuit.

## Scope discipline

Touched: form/mandell/signatures.py (mechanism), form/d1_typed_52_53_test.py + form/regress.py (suite), the two authorized count pins, the limitation dated_correction append, the regenerated proof-cards render, and the Step 11 report's appended version note. NOT touched: any handler (query_ops.py, core_ii_exec.py byte-identical), any other Dell, the DIR-CERT-2026-11-02 certified scopes beyond the authorized pins/versioning, DAF-09, gui/.

Failure-class note (bounded, per AGENTS §15): the gate drops typed args for EVERY untyped Dell identically. This circuit's authorized scope was 52/53 only; the class is recorded here, not repaired beyond it (see Q2).

## Anticipated probes

1. Bare/direct behavior changed? No handler diff exists; bare 52/53 and direct `execute_core_ii(..., roles=None)` paths are byte-identical code. The proof-cards bare-invocation distribution is unchanged (79 executed / 21 named failures — suite-pinned).
2. Why no `roles` transport like Dell 55? Because 55's legacy branch re-splits the label on "=" (ambiguity is real there); Filter and Scope consume the whole label. The twin check compares typed vs legacy outcomes including the full result cell, and M3 shows the lowering branch is the load-bearing transport.
3. Reference resolution (`last_result`, `store:`) now applies to 52/53 typed values: yes — inherited from the shared gate, identical to 51/54/55; it is a consequence of registration, disclosed here, not new machinery.
4. Delimiter edge: a typed value containing a double quote cannot be expressed — the seed parser's arg charset (`[^"]*`) excludes it for EVERY typed Dell (pre-existing grammar, unchanged). Spaces, "=", ":", ">" inside quotes ride whole (">" proven by the chain checks' parse integrity; space and "=:" proven behaviorally).
5. Step 14's admission report still says 15: it is a frozen dated admission record of a past candidate — historical evidence, not live documentation. Uni's reading is that versioning it would violate the same append-only discipline; the live count is carried by the limitation entry, the proof cards, and this circuit's pins. Put as Q3 for confirmation.
6. Chain policy after a refused typed Scope: unchanged pre-existing chain semantics; the suite asserts the honest receipt and that scope did not move — it does not invent a chain-stop claim.

## Questions for the Director

Q1. Ruling requested on D1-TYPED-52-53 as submitted (PR #250, head as above). The PR is deliberately unmerged; merge authorization for this circuit is the unblock. (Recommended: certify within the stated scope — every contract point is failing-first, mutant-killed, regress x3 and fresh-clone green at the exact head.)
Q2. The gate's silent typed-argument loss applies to every remaining untyped Dell. Should systematic typing continue as per-Dell D1-arc circuits in registry order (contract-derived, one bounded circuit per Dell or family), or is typing on-demand only when a Dell is exercised? (Unblocks: scoping of future D1 work. Recommended: continue systematically — silent argument loss is an execution-integrity defect wherever a user reasonably types args, and the per-Dell cost is now proven small.)
Q3. Confirm Uni's reading on DIRECTOR_REPORT_STEP14_ADMISSION.md: it remains unversioned as a frozen admission record, while DIRECTOR_REPORT_STEP11_CONTRACTS.md carries the appended version note because the wake review named the Step 11 documentation. (Unblocks: nothing operational; closes the documentation-integrity question raised in probe 5.)
