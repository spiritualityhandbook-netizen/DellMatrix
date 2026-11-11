# C3.DIFF (DD-51 RINGS 1+2) — CIRCUIT REPORT — 2026-11-11

Routing: Director mail 1a1cb46c70141e21 (single bounded Rings 1+2 PR;
pre-coding inventory first). Inventory:
director-reports/C3_DIFF_GROUNDING_2026-11-11.md + full inventory in the
PR evidence. MWL item 130.

## BEFORE → AFTER (capability)

BEFORE: Dell 89 [Diff] compared ONLY the Core II store, and only when
the most recent mutation happened to pass the one noting site (Dell 55
Set and the Spectrum clerks). Eleven writers changed weights, groups,
references, causes, dependencies, definitions, aliases, and
compositions WITHOUT leaving a baseline — a Diff after those moves
reported on a stale or missing baseline, or refused.

AFTER: every content writer passes the ONE _note_mutation door before
mutating (Dells 74, 75, 78/79 via their shared relation site, 80, 81,
82, 83, 97, 98, plus the chain-layer flow writers), capturing the
_ckpt wide frame (store, weights, groups, refs, causes, deps, defs,
aliases, compositions). Dell 89 compares the slice(s) named by a
SCOPE WORD in its label (store / weights / groups / refs / causes /
deps / defs / aliases / compositions / all); no scope word = store
only = the legacy behavior, byte-identical in receipt shape. The
receipt widens ADDITIVELY (per-slice before/after/changed), names any
unexamined slices, and refuses baseline_missing for EVERY scope when
no baseline exists. An unknown scope word refuses
diff_scope_unknown:<word> and writes no receipt.

## EVIDENCE

- Failing-first: form/c3diff_test.py scored 3/24 on unmodified code
  (only pre-existing refusal guards passed); 24/24 after.
- Mutants (inverse-edit reverted, re-verified green): M1 Group note
  dropped → 23/24 caught; M2 weights slice dropped from `all` →
  21/24 caught; M3 unknown scope word falling through to store →
  23/24 caught.
- Focused suites: step9_diff, d1_registry_spectrum,
  spectrum_closure, unified_runtime, dd14, step8_transactions,
  step10_consistency, cac_i, p10_flow_grammar,
  af2_delimiter_addressing — all PASS.
- Regression ×3 from the main session (fresh logs): fwd 272 OK +
  1 RED; --twice 544 OK + the same RED twice; rev 272 OK + 1 RED.
  The ONLY red in all three legs is
  form.define_compose_nonpublication_test at 12/15 — the disclosed
  delta below, predicted before the campaign ran.
- regress.py LIST 272 → 273 (c3diff_test registered; sorted-import
  verification passed).

## DISCLOSED DEVIATIONS FROM THE INVENTORY RECOMMENDATIONS

1. In-frame baseline gating (inventory rec #4b) and Revert
   invalidation (rec #3b) NOT implemented: the registered suite
   step9_diff PINS the opposite (in-frame notes set the standalone
   baseline; a frame Revert leaves it governing). A pinned contract
   suite outranks a recommendation; the new suite re-pins both
   behaviors per slice. The latent stale-baseline corner after a
   snapshot-fallback Revert remains, flagged, unchanged.
2. Dell 99 publication does NOT note (inventory rec #7 listed it).
   Evidence: noting publication alone flipped step10_consistency —
   a clean define-run's publication manufactured the only baseline
   in a program whose next act redefines the same name with a Diff
   body, making the define-run self-fulfilling. Publication is still
   REPORTED by Diff(compositions) inside the standing baseline
   window (pinned). The exclusion is documented at the Dell 99 site.
3. The generated composition wrapper term 89[ComposeStep] maps to
   legacy store behavior (it is a generated name arriving as Diff's
   payload, not a scope aim); without this, digit-body Diffs inside
   compositions would refuse instead of executing.

## KNOWN DELTA REQUIRING A DIRECTOR RULING

define_compose_nonpublication_test A7/P2/P3 (12/15): in that suite's
program the only arming write before A7 is A6's successful Alias
(98) — an explicitly ordered Ring-1 writer. Post-Ring-1, A7's
Diff-bodied define-run legitimately succeeds (baseline exists,
changed=[]), so the redefinition publishes and the prior body is not
retained. The suite's underlying contract B18 — a FAILED define-run
never publishes — is INTACT (A1/A3/A4/A5/P1/P4 pass; A1's error is
baseline_missing again). What Ring 1 retired is the suite's scenario
prop: "a Diff body is a reliably failing define-run after other
content writes." Uni did not edit the pinned suite.


## AMENDMENT ROUND (Director Q-C3.1 ruling, mail 1a1cb916b4f20117)

Q-C3.1 APPROVED the bounded scenario amendment in this same PR;
Q-C3.2 ACCEPTED the three deviations as scoped; Q-C3.3 barred any
merge while smoke is red and set the return path (amendment ->
campaign -> terminal-green exact-head CI -> Keeper scoped review ->
Director final disposition).

AMENDMENT (head 449c5dc9444e56f2c2a5bdb8bca487754b81c81f, one file:
form/define_compose_nonpublication_test.py, +31/-3):
- OLD A7 trigger: 99[Compose] :: keep=89[Diff] — failed only because
  no baseline existed; Ring 1 retired it (A6 Alias arms a baseline).
- NEW A7 trigger: 99[Compose] :: keep=47[Embed] — fails with
  embed_unavailable. Dell 47's binding is runtime-only, per-Program,
  never persisted; nothing in this suite binds one, so the failure
  is independent of baselines, store contents, and ambient state:
  deterministic by construction.
- The Assert-body alternative was REJECTED on probe evidence: a
  nested :: inside a Compose label fails at outer-chain parse, so
  the body never runs and cannot evidence a failed define-run.
- A7's assertion is strictly STRONGER (adds out["error"] ==
  "embed_unavailable"); P2/P3 and all other checks byte-identical;
  A3 keeps its 89[Diff] body (still fails legitimately — no baseline
  exists at that point). ADDED A9: after A6, standalone 89[Diff]
  returns ok — the Ring-1 success path the old scenario denied.
- Failing-first: unmodified suite 12/15 (log amend_before); probe in
  the exact post-A6 state (log amend_probe): baseline armed, old
  trigger succeeds and republishes, Embed trigger fails
  embed_unavailable repeatably, keep retained.
- Amended suite: 16/16 PASS (denominator 15 -> 16 by the one added
  check, documented in-code). Focused suites: c3diff 24/24,
  step9_diff 24/24, step10_consistency 34/34, spectrum_closure
  57/57, unified_runtime 37/37, dd14 11/11.
- Main-session campaign x3 on the amended head a3c77ab (logs
  c3diff/logs/amend_*): fwd 273/273 OK EXIT 0; --twice 546 OK
  EXIT 0; rev 273/273 OK EXIT 0. ZERO red in all three legs.
- Exact-head CI on a3c77ab: TERMINAL GREEN (smoke PASS 16m30s;
  build 3.10/3.11 PASS; browser-acceptance PASS; MERGEABLE/CLEAN).
- This appendix commit changes no form/ file (tree under form/
  identical to a3c77ab); CI reruns on the new head for exact-head
  discipline. RETURNING for Director final disposition per Q-C3.3,
  with Keeper scoped review at the amended head.

## Questions for the Director — RULED (mails 1a1cb916b4f20117, 1a1cbb30652fef84)

- Q-C3.1 RULED: bounded scenario amendment APPROVED in this same PR
  (deterministic failing trigger; B18 preserved; failing-first +
  Alias->Diff success check required). EXECUTED as the AMENDMENT
  ROUND above; amendment then received SCOPED CODE/SCENARIO PASS
  (mail 1a1cbb30652fef84).
- Q-C3.2 RULED: the three deviations ACCEPTED as scoped, bounded
  compatibility choices — not approval of the stale-baseline corner,
  all-writer completeness, or global certification. Residual
  limitations stay in this report (below).
- Q-C3.3 RULED: NO MERGE WHILE FORM SMOKE RED. Return path set:
  amendment + campaign + terminal-green exact-head CI + Keeper
  scoped review + Director FINAL disposition. This packet is that
  return; merge awaits the final disposition and the Keeper stamp.

## CAMPAIGN RECEIPT (final, amended code head 449c5dc; records heads above it change no form/ file)

Failing-first: build suite form/c3diff_test.py 3/24 on unmodified
code -> 24/24 after implementation. Amendment suite
define_compose_nonpublication_test 12/15 before -> 16/16 after
(trigger probe logs: amend_before, amend_probe, amend_suite in the
circuit log archive). Mutants killed: 3/3 (M1/M2/M3, inverse-edit
reverts).
Local campaign on the amended head (main session, logs amend_fwd /
amend_twice / amend_rev): fwd 273/273 OK EXIT 0; --twice 546 OK
EXIT 0; rev 273/273 OK EXIT 0 — zero red in all legs.
Exact-head CI: at a3c77ab — smoke run 43065038983 SUCCESS, package
run 43065038971 SUCCESS, browser-acceptance run 43065039015
SUCCESS (all terminal). Records-only heads after a3c77ab re-run CI
for exact-head discipline; their form/ tree is identical
(diff-verified).
Residual limitations: (i) latent stale-baseline corner after a
snapshot-fallback Revert remains as-is (pinned step9 semantics);
(ii) Dell 99 publication does not arm baselines (documented
exclusion); (iii) Ring 3 (Plane/Nursery/generation diffs) is a
later circuit; (iv) scoped acceptances are not global
certification; MWL 130 uncredited until independent closure.
Proposed MWL 130 transition on closure: OPEN -> COMPLETE (scoped:
Rings 1+2 as built), headline 35/179 -> 36/179 = 20.1%.

Anticipated probes: a baseline armed by 98[Alias] then consumed by
89[Diff]:: all after unrelated writes (covered, per-slice pins);
89[Diff] inside an open Try frame after Commit (pinned by step9 +
new suite); 89[Diff] with a nonsense scope word (refuses, no
receipt); persistence round-trip (baseline stays session-only —
nothing new serialized; last_diff not serialized, zero production
readers).

Scoreboard effect on closure: MWL 130 → COMPLETE moves the headline
to 36/179 = 20.1%. This report claims BUILT + EVIDENCE, not
certification.
