# MPC-007 COMPLETION PACKET
ADAPTIVE ACTIVATION + ENGLISH ROUTING TRUTH CLUSTER

Date: 2026-10-03
Authority: ACE > DIRECTOR > UNI / SUSX100 > REPOSITORY
Autonomy: NO

Director decisions carried in:
- C-R1-008: LIVE_ENGLISH_SAFETY_DEFECT = CLOSED / FALSIFIED. Preserved as
  DEFENSE_IN_DEPTH_HYGIENE_DEBT (not implemented). Reason recorded.
- Permanent evidence law: PUBLIC_PATH_CLAIM requires PUBLIC_PATH_PROOF.
- PR #65: MERGE AUTHORIZED at exact head f1381fc96df5c83d46f6bab4324ada312f1b1ca2
  (Director independently verified: 3.10 PASS, 3.11 PASS, smoke PASS,
  github-advanced-security PASS).

---

## PR65 MERGE

PR65_MERGE_SHA: a89961d1a4484e5ae6f8cdf93d24cea3fd6a0596 (2026-10-03T14:11:18Z)
POST_MERGE_MAIN: a89961d1a4484e5ae6f8cdf93d24cea3fd6a0596 (fresh-clone verified)
POST_MERGE_TREE: 59b413c193cc15188577ceec49211152b84856b6
Merge identity matched authorized head exactly; no STOP triggered.
ADAPTIVE_FRESH_PROCESS_PROOF (fresh clone /tmp/mpc007-main):
select_adaptive_team verified (CORE/TARGETED_SWARM/FULL_SWARM selection);
resolve_team: legacy CORE -> (DIRECTOR, UNI); legacy SWARM -> full six-persona
team; AUTONOMY=NO default in new_run (state_machine.py:228).

---

## TEAM

TEAM_SELECTED: TARGETED_SWARM + ORACLE + NULL (PRISM on demand; not required).
SELECTION_REASON: raw adaptive output was FULL_SWARM (semantic_uncertainty 0.8,
evidence_weakness 0.7 after the C-R1-008 falsification). Directive specified
UNI/ORACLE/ARGUS/NULL initial roles; that team was used. PRISM not spawned:
the one evidence disagreement (ORACLE/NULL branch-order error vs UNI live
probe) was resolved by decisive live evidence, not reconciliation.

---

## PHASE 1 — PUBLIC ENGLISH PIPELINE (reconstructed, verified)

raw English
-> _dispatch_public_line (repl.py:2454; mints interaction_id)
-> pre-dispatch: ROS / learn / why / flow (>/<:) / seed (looks_like_seed) /
   multi-step (and then) — none match the C-R1-007 inputs
-> translate(raw line) -> Intent
-> _execute_intent: normalize_english (strip -> learned -> paraphrase ->
   synonym -> strip -> passthrough); if normalized != raw, recurse with
   normalized text (_normalized=True)
-> action dispatch elif-chain (order matters — see below)
-> route_intent -> CORRESPONDENCE or _route_generalized -> bridge
   (BLOCKED_WITH_REASON) / execute_seed / execute_chain
-> Outcome V1 capture -> observable result

Critical ordering fact (missed by ORACLE and NULL, proven by live probe +
branch-offset measurement): the DCC-III vocabulary branch (repl.py:2227,
tuple includes "load") precedes the `elif action == "load": persist_load`
branch (repl.py:2408). The persist_load branch is DEAD CODE for
action=="load". Any session-restore intent for the load family must be
placed before the DCC-III branch.

---

## PHASE 2 — C-R1-007 CASES (all PUBLIC_END_TO_END via real REPL subprocess)

### Case A: "resume"

- INPUT: "resume"
- PROBE_SCOPE: PUBLIC_END_TO_END
- NORMALIZED_FORM: "load" (synonym, english_brain.py:72)
- INTENT: action=load, dell=28, mandel='28[Rollback] :: load'
- DELL: 28
- ROUTING_AUTHORITY: DCC-III branch -> route_intent -> CORRESPONDENCE("load",28)
  -> _seed_rollback -> core_i_ops rollback arm
- EXECUTOR: core_i_recovery.rollback
- STATE_BEFORE/AFTER (no checkpoint): unchanged; OBSERVABLE_RESULT:
  "Rollback missing checkpoint", ok=False
- STATE_BEFORE/AFTER (checkpoint present, ARGUS): ['alpha','beta'] -> ['alpha'];
  OBSERVABLE_RESULT: "Checkpoint restored. PROGRAM: restored from checkpoint
  (session replaced)", ok=True, NO WARNING — uncommitted work silently destroyed
- EXPECTED_AUTHORITY: CONFLICTED —
  (1) router correspondence ("load",28): "Intent('load') = restore checkpoint",
      verified live (deliberate);
  (2) dead REPL branch "Session loaded." + executor_leaf Dell28 session-load
      (executor_leaf.py:273-276) + english_brain synonym family
      (resume/restore/reload/recover->load) implying session restoration
- R1's "instead of 33[Resume]": CONTRADICTED_BY_AUTHORITY — Dell33 is avatar
  locomotion ("Resumed walk", executor_leaf.py:306-315, CORE_I.md:14). Routing
  session-resume there would be the actual misroute.
- CLASSIFICATION: AMBIGUOUS (conflicting deliberate authorities) + confirmed
  HAZARD (silent unconfirmed destructive revert on an innocuous word)

### Case B: "make a macro"

- INPUT: "make a macro"
- PROBE_SCOPE: PUBLIC_END_TO_END
- NORMALIZED_FORM: "create an idea called macro" (synonym layer fires before
  phrase matching; the 48[Macro] phrase never sees the word "macro")
- INTENT: action=place, mandel='08[Create](name="macro") > 15[Map] :: macro'
- DELL: 8+15
- ROUTING_AUTHORITY: translate.py:554 generic make-X rule
- EXECUTOR: Create+Map composition
- STATE_BEFORE/AFTER: [] -> [idea "macro"]; OBSERVABLE_RESULT: idea named
  "macro" created; no macro involved
- EXPECTED_AUTHORITY: NONE — no macro-creation operation exists anywhere
  (macro_seed only echoes history; Dell48 = replay/materialize). Rerouting to
  48 would execute history replay (form/open.py:257-270), not creation.
  Bare "macro" -> 48[Macro] already works via phrase table.
- CLASSIFICATION: AMBIGUOUS — absent capability with misleading fallback
  (not a misroute to an existing semantic)

---

## PHASE 3 — TEST REALISM AUDIT

R1_TEST_REALISM_AUDIT:
- C-R1-008: R1 probe_scope = EXECUTOR (execute_seed direct); claim scope =
  public safety hole. CLAIM_SCOPE > PROBE_SCOPE. Falsified.
- C-R1-007: R1 probe_scope = TRANSLATION (translate()/english_brain labels);
  claim scope = public misroute. CLAIM_SCOPE > PROBE_SCOPE. Re-audited at
  PUBLIC_END_TO_END in MPC-007.
- Durable change (no second evidence system): `probe_scope` enum
  [UNIT, TRANSLATION, ROUTING, EXECUTOR, PUBLIC_END_TO_END] added to
  evidence items and contradiction entries in ops/swarm/run_schema.json;
  CLOSED_FALSIFIED added to contradiction status enum; both R1 entries
  annotated with actual scopes; CLAIM_SCOPE <= PROBE_SCOPE recorded as
  evidence law with the scope ladder.

C_R1_008_FINAL_RECLASSIFICATION: CLOSED / FALSIFIED (MPC-007-D1).
PATCH_HYGIENE_DEBT_RECORDED: yes — _DESTRUCTIVE_VERBS missing Patch =
DEFENSE_IN_DEPTH_HYGIENE_DEBT, not implemented, in manifest.

---

## PHASE 4/6 — IMPLEMENTATION RECORD

PROVEN_PUBLIC_MISROUTES: none (both R1 framings reclassified).
FALSIFIED_MISROUTES:
- "resume should route to 33" (Dell33 = avatar locomotion)
- "make a macro should route to 48" (Dell48 = history replay, not creation)
AMBIGUOUS_CASES: resume (authority conflict + hazard); make-a-macro (absent
capability).

One implementation was made and REVERTED: a session-restore intercept for
action=="load" (sans revert/rollback) placed before the DCC-III branch in
_execute_intent. It worked (REPL: resume -> "Session loaded."; revert ->
Dell28 intact; dcc_vi 12/12, semantic_route 59/59, core_i_maturity 20/20
green). Reverted because ARGUS's falsification round surfaced the deliberate
("load",28) checkpoint-restore correspondence — the intended semantics are
genuinely ambiguous between two deliberate authorities, and Phase 4 forbids
implementing under ambiguity. The reverted diff is not shipped; the design is
documented here for Director option (b) below.

NULL_RESULTS:
- resume: NULL returned NO_CODE_NEEDED, but on a FALSE PREMISE (same
  branch-order reading error as ORACLE: missed the DCC-III shadow at 2227).
  Corrected by UNI live evidence (three independent methods). The NULL
  *questions* were then answered honestly: the defect does not dissolve under
  correct pipeline understanding; it is public-path real; but it is
  AMBIGUOUS authority, not a clear defect — so no code per Phase 4.
- macro: NULL correct — DEFECT_SURVIVES as absent capability + misleading
  fallback; no reroute target exists.

ARGUS_ATTACKS:
- Falsification round (9 probes, PUBLIC_END_TO_END): resume hazard confirmed
  (silent destruction); macro ambiguous confirmed.
- Phase 5 attack round: TARGET ABSENT — fix had been reverted before the
  round ran. Valuable structural findings: (1) confirmed the 2408 dead-code
  analysis — any re-implementation must precede the DCC-III branch;
  (2) correction: bare "rollback" -> unknown; only "revert" is pinned to
  Dell28 (translate.py:198), so a future carve-out needs only "revert".
ARGUS_RESULTS: no fix certified (none exists); hazard and ambiguity findings
stand as reported.

FILES_CHANGED (branch mpc-007-routing, vs main a89961d):
- ops/swarm/runs/MPC-004-R1/manifest.json (evidence laws, scope annotations,
  C-R1-007 reconciliation, semantic decision requests)
- ops/swarm/run_schema.json (probe_scope enum, CLOSED_FALSIFIED status)
- form/repl.py: implemented then fully REVERTED — net zero production change
SEMANTIC_DELTA: none. No production semantics changed in MPC-007.

TEST_RESULTS: dcc_vi 12/12, semantic_route 59/59, core_i_maturity 20/20
(run with the fix applied; all suites bypass _execute_intent's load dispatch
via route_intent directly, so results hold for the reverted state).
CI_RESULTS: PR65 exact-head (Director-verified): 3.10 PASS, 3.11 PASS, smoke
PASS, github-advanced-security PASS.
CANDIDATE_HEAD: b1fa4b6 (mpc-007-routing)
PR_STATE: no product PR opened (nothing to ship). Evidence-branch PR to be
opened for the ops/swarm record commits; merge NOT authorized.

CAPABILITY_BEFORE / CAPABILITY_AFTER: unchanged. No user capability moved;
two false-fix framings prevented (Patch guard change in MPC-006, resume
reroute in MPC-007).

---

## PHASE 7 — SYSTEM RECONCILIATION

R1_DEBT_RECALCULATED:
- C-R1-001 inventory taxonomy 99/100/101: OPEN (needs Director taxonomy)
- C-R1-002 Flow: RESOLVED
- C-R1-003 registry overstates Dell90/94/95: OPEN
- C-R1-004 Dell37 identity: OPEN
- C-R1-005 Dell87 key-rename: OPEN, blast radius narrowed (bridge-blocked,
  raw-Mandell-only); needs Director semantic ruling
- C-R1-006 conditional slot: OPEN (narrowed)
- C-R1-007: RESOLVED as misroute claims; AMBIGUOUS items moved to Director
  semantic decisions (MPC-007-D2-REQUEST)
- C-R1-008: CLOSED_FALSIFIED
- C-R1-009 stale reserve names: OPEN (low value)
- Reachability caveat (new): any remaining R1 finding whose severity assumed
  public reachability but was probed below PUBLIC_END_TO_END is suspect.
  Flagged: place() uid-collision silent overwrite (severity depends on public
  reachability — unproven).

NEXT_BROKEN_LINK: place() uid-collision silent overwrite on 8/14 — silent
data loss is the highest-severity *unresolved* class, and its public
reachability has never been proven at PUBLIC_END_TO_END.
NEXT_PRODUCT_CLUSTER (bounded, needs Director authorization): TARGETED_SWARM
re-audit of the place-collision finding at PUBLIC_END_TO_END scope; implement
only if publicly reachable and no existing authority prevents it.
Note: resume, macro, and Dell87 all await Director semantic rulings and are
not implementable clusters.

UNKNOWNS:
- Director's semantic rulings (resume a/b, macro i/ii, Dell87 rename-vs-substitute)
- place-collision public reachability
- GitHub AI security quota restoration (affects future PR gates)

---

## SUSX100 VALUE/OVERHEAD (Progress Law)

Overhead: 4 subagent spawns (ORACLE, ARGUS-falsify, NULL, ARGUS-attack).
Value:
- Prevented shipping a cosmetic Patch guard change as a safety repair (MPC-006).
- Prevented shipping a premature resume reroute that overrode deliberate
  verified router authority (MPC-007) — the fix was implemented, proven,
  then correctly reverted.
- Two specialists made the same code-reading error (missed DCC-III shadow);
  live public-path probing caught it. Lesson: specialist code reads do not
  outrank executed probes; PUBLIC_PATH_PROOF remains the standard.
- Net: 0 production changes, 2 false framings killed, 1 real hazard
  characterized, 1 durable schema improvement, 3 Director decisions queued.
  Infrastructure cost justified.

---

AUTONOMY: NO
DIRECTOR_DECISION_REQUIRED: YES
Decisions queued:
1. MPC-007-D2-REQUEST(a)/(b): resume semantics — keep checkpoint-restore +
   add confirmation/warning, or remap session-restore family to persist_load
   (reverted fix available).
2. MPC-007-D2-REQUEST(i)/(ii): macro — build macro-definition capability, or
   honest UNKNOWN for "make a macro".
3. C-R1-005: Dell87 key-rename vs value-substitution (carried).
4. Authorize next product cluster: place-collision PUBLIC_END_TO_END re-audit.
5. Merge evidence-branch PR (ops/swarm record only) — to be opened.

STOP.
