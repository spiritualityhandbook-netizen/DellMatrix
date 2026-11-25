# STEP 11 PACKET — public-contract wording reconciliation
## B10/B17/B19-B21, C1/C2 + deferred cross-surface items

Base: c438956 (main, PR #203 merge). Branch: uni/step11-contracts,
worktree ~/workspace/nbd-omega-step11. Ground:
hidden_files/step11_ground.md (re-verified at c438956; all false
sites re-confirmed first-hand this run 2026-11-01 16:30 CST).

## Nature
Every item is an ACCEPT ruling: mechanisms unchanged, WORDING on
registry/manor/runtime surfaces is false. NO mechanism changes,
NO new staging subsystem (B17 forbids), NO property-measurement
vocabulary (C2 DEFERRED), NO gate-reason rewording (step 6 Q2
unsettled — out of scope).

## SWAT Director's-eye pre-mortem (recorded BEFORE implementation)
How would the Director break this submission?
1. Reword a manor but leave DELL_PROOF_CARDS.md stale -> render
   drift / a second stale public surface. Counter: regenerate via
   the existing renderer; suite + d1_proof_cards_test pin equality;
   typed count must stay 15 (any count change = red flag).
2. Blind "atomic" sweep rewords LEGITIMATE atomic claims
   (atomic_write.py os.replace; README confirmation-atomicity
   journal row; checkpoint snapshot row) -> false wording in the
   opposite direction. Counter: suite pins those surfaces intact;
   only Commit (95), Replace (87) and DELL_RUNTIME 87 row change.
3. Join-vs-Any / partial-vs-ok statement pasted into several
   surfaces -> second authority, future drift. Counter: ONE
   canonical home (card 61); suite asserts it there only.
4. Limitation "correction" silently rewrites the 2026-10-27
   evidence line -> historical evidence falsified. Counter:
   dated correction APPENDED as a new field; suite pins the
   historical evidence line byte-intact.
5. B19 test duplicates step 7's receipt-order coverage and proves
   nothing new. Counter: step 11's witness is Route SEMANTICS:
   outside a Branch, 59 executes as Route (route channel + cell);
   inside a Branch chain, the 59 atom never executes as Route
   (route channel unchanged by it, receipt skipped as Else).
6. Measure wording invents property vocabulary to fill the gap
   -> violates C2 DEFER. Counter: wording states cardinality
   only + label-is-annotation + deferral, explicitly.
7. "43 Dells lack typed signatures" restated with a new invented
   number. Established this run: 43 reconciles with NOTHING —
   at probe time 14 typed => 86 untyped (not 43); today
   (verified by execution) 15 typed [8,51,54,55,56,57,58,67,68,
   69,84,85,86,87,88] => 85 untyped. The dated correction states
   exactly that: original figure irreconcilable with its own
   evidence; current verified figure 15/85 at this candidate.

## SWAT unanimity (4 personas; dissent recorded per DIR-WF-001 —
## unanimity is not a truth gate)
- Custodian: AGREE — history preserved (dated correction append,
  historical reports untouched); one canonical home per statement.
- Interpreter: AGREE — wording must say what the runtime does in
  the runtime's own terms (cards are the model); manifest alias
  lists are invocation vocabulary, NOT descriptions — LEAVE them
  (trimming would be a behavior change needing its own witness).
- Sentinel: AGREE with note — 87 "Atomic" is in B20 scope (same
  false-word class as B17); legitimate atomic claims pinned.
- Mechanic: AGREE — wording-only diff in core_ii.py manors,
  registry.py CORE_I manors, DELL_RUNTIME.md rows 85/87,
  dell_cards.py card 61 append, limitation_knowledge.py append;
  regenerate proof cards; no executor changes.
UNANIMITY 4/4 on the repair shapes above. Decisions on the
ground's open questions: Q1 in scope; Q2 leave manifests;
Q3 card 61 is the single home; Q4 README needs no B-item rewrite
(README_EVIDENCE_MAP carries no Measure/Commit/Lock claims;
README truthful/silent) — the dated correction lives in
limitation_knowledge; Q5 resolved as in pre-mortem item 7.

## Wording (manor = public contract)
- 71 Measure: "Count selected-set cardinality only (kind/unit
  label is annotation, not a property measurement; property
  vocabulary deferred)"
- 95 Commit: "Mark/accept current live state (no atomic staged
  isolation; Revert covers only the Try checkpoint fields)"
- 59 Route: "Choose/direct execution path (in a Branch chain a
  59 atom is consumed as the Else marker, never as Route)"
- 85 Move: "Relocate ownership/location/state (overwrites an
  existing destination)"
- 87 Replace: "Key rename old to new (refuses an occupied
  destination — replace_occupied, no mutation)"
- 23 Lock: "Sandbox switch over units (sandboxed=True on every
  live unit; not per-unit immutability, not a permission grant)"
- 28 Rollback: "Authority-mediated checkpoint restore (bare use
  denied; freeze + grant + confirm_rollback required)"
- 44 Bridge: "Honest refusal — no external tool provider bound
  (bridge_unavailable, offline)"
- 47 Embed: "Honest refusal — no embedding provider bound
  (embed_unavailable, representation none)"
- DELL_RUNTIME.md: 85 row -> "relocate (overwrites destination)";
  87 row -> "key rename (refuses occupied destination)".
- Card 61 append (ONE home): Join-vs-Any empty-set distinction
  (empty executed child set = successful Join under both
  policies; Any(empty)=False is Dell 67's rule, not Join's) +
  partial/ok (partial = occurrence-level incompleteness,
  omission OR failure; ok is the separate success verdict;
  never infer failure from partial alone).
- limitation_knowledge LEGACY_ONLY_SIGNATURE: append
  "dated_correction" (2026-11-01, step 11): evidence line and
  original limitation text untouched; correction states the
  14->15 change (step 4, Dell 55), the irreconcilability of
  "43", and the verified current count 15 typed / 85 untyped.
  NOTE: the entry's "limitation" field itself is the claim
  being corrected — per audit discipline the correction is
  appended, the field is NOT silently rewritten. (If the
  Director wants the field itself amended, that is Q1 for him.)

## C1 disposition
README.md:86 already states the truthful nine-operator version;
flow_executor.py's narrower classification is true FOR THE
ADAPTER and its explicit refusal stays; no surface found in
this circuit's sweep claims the adapter IS the whole runtime.
Recorded as verified-consistent; no edit invented. Step 9 Q2
(Diff/Set cross-surface): no durable-baseline implication found
on README/limitation surfaces — verified-consistent, recorded.

## Closure discipline (to run)
failing-first suite form/step11_public_contracts_test.py ->
wording pass -> suite green -> mutants (restore 95 "Atomically
accept staged mutation"; restore 47 "Vectorize"; each must fail
the suite) -> neighborhoods (d1_proof_cards, d1_registry_*,
r2_registry_reconciliation, step7, step8, step9, step10,
p10_flow_grammar, p12_closure) -> regress x3 -> packet closure
-> PR -> exact-head CI in a SEPARATE step -> merge (tree
equality) -> fresh-clone regress -> ledger + POST_PLAN +
register -> Director report published to director-reports/
(held; Director asleep; nothing certified).

## CLOSURE ADDENDUM — 2026-11-01 (implementation verified)
Candidate 91a422b on uni/step11-contracts (base c438956;
tree recorded at push). Failing-first: probe 11/11 wording
witnesses FAIL on unfixed c438956; suite 7/31 pre-fix ->
31/31 post-fix. Mutants killed: M1 (restore 95 manor
"Atomically accept staged mutation") 28/31; M2 (restore 47
manor "Vectorize") 29/31; restored 31/31, tree clean.
Neighborhoods green: d1_proof_cards 6/6, p12_closure 8/8,
p10_flow_grammar 12/12, step7 28/28, step8 22/22, step9
24/24, step10 34/34, d1_registry_coreii_a 30/30, _b 43/43,
d1_registry_spectrum 48/48, r2_registry_reconciliation
323/323. Regress x3 on 91a422b: fwd 220/220 GREEN
(step11_logs/reg_leg1_fwd.log), --twice both passes
220/220 GREEN (reg_leg2_twice.log), --order rev 220/220
GREEN (reg_leg3_rev.log). Proof cards regenerated via
the existing renderer — headings/notes only, survey
counts unchanged (typed 15). Remaining: PR + exact-head
CI verified in a SEPARATE step + merge with tree
equality + fresh-clone regress + ledger/POST_PLAN/
register + Director report publication.

## FINAL CLOSURE ADDENDUM — 2026-11-01 (step 11 fully closed, implementation)
Exact-head CI on candidate 91a422b (tree fc87d85) verified
COMPLETE SUCCESS in a SEPARATE step this run (package
41360753305 SUCCESS; smoke 41360753367 SUCCESS completed
23:21:43Z; fresh verification showed PR CLEAN/MERGEABLE).
PR #204 MERGED as 195fafa (merge tree fc87d85 == candidate
tree; parents c438956 + 91a422b). Fresh-clone regress at
merge 195fafa: 220/220 GREEN (step11_logs/
freshclone_regress.log; fresh-clone HEAD verified 195fafa
before the run). Ledger row + POST_PLAN note + register
entry (B10/B17/B19-B21 -> IMPLEMENTED-VERIFIED) done.
Director report DIRECTOR_REPORT_STEP11_CONTRACTS.md
finalized (Anticipated probes + Questions Q1/Q2);
publication via docs PR follows (held — Director asleep;
nothing certified). Next: step 13 freeze + pairwise re-run.
