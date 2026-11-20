# PART I — ARCHITECTURE: PLAN (2026-11-20)

**Plan stage of plan → confirm → code → confirm. Branch
`uni/part-1-architecture`, base main
`af2519b6d239ef278397e277210d6da2467c36e5` (PR #500 merge).
Scope: 70 register rows + 13 Edition 1 circuits (GP-E05, E13–E19,
E21–E24, E26), all 3 GATED rows. Map:
`EIGHT_PART_EXECUTION_MAP_2026-11-20.md`, Part I section (a)–(g).
This plan is written at GO-BIG depth (Ace, 2026-11-20 08:54 CST):
every failing-first suite and evidence/proposal artifact the
package names, nothing held back as skeleton; anything the
package scoped "later" that is buildable now without an authority
gate is built now and the PR says so. Held code stays held.**

**Naming deviation from the package, recorded honestly:** the
package named new failing-first suites as `*_test.py`. They ship
in this PR as `*_test_spec.py`. Reason: `form/regress.py`'s
`intended_entries()` = LIST + every discovered
`form/**/*_test.py`; an unregistered failing suite turns CI smoke
RED as an omitted/red entry (failure class proven on PR #503,
smoke run 44758805458). The rename+registration for every spec
file is recorded as **code-stage step zero** (§2) — the spec
content is identical to what the package named; only the filename
changes on this side of the authority gate.

---

## §0 — Holds and gates (plain, first)

1. **R5-D implementation — HELD.** Plan + existing evidence only.
   No product code. Unlock path: Keeper challenge of prep head
   `13b33fa` → Director bounded authorization (at most S7) →
   only then code, inside this Part PR. MWL #173 → PARTIAL on the
   retention contract; COMPLETE only with R5-D built.
2. **PR #294 / Q1 C-B — GATE HOLD.** Failing-first prep + the
   C-B transaction design (this PR) only. No C-B code. #294 never
   merges under the GATE HOLD. MWL #118 stays GATED.
3. **MWL #34 (legacy-flow ownership) and #46 (pair-atomic
   ordinary save) — GATED.** Their recorded dispositions govern;
   #46's C-A scope is separately scoped, not authorized (see
   §1.3).
4. **Row #155 (multi-Psalm/BIMO execution) — RULED by Ace
   2026-11-20** (see the closing ACE RULING section): the roster
   is ALL of Ace's Psalm personas; the build is unblocked as
   scoped there.
5. **H-4 pulse rename — NEEDS_DIRECTOR.** Failing-first test
   first; rename only with Director approval.
6. **30-video P05 — BLOCKED** (frozen holdout dataset does not
   exist). **P08 — BLOCKED** (frozen R3 blueprint retrieval is
   GP-E22's first step). Both carried as blocked-with-named-blocker,
   not silently dropped.

---

## §1 — Evidence already in this PR (measured on current main)

### §1.1 Failing-first suites and spec artifacts

| Artifact | Result | What it proves / exposes |
|---|---|---|
| `form/gs4_sandbox_test.py` (extended RUN G, registered suite) | **22/22 PASS** | Growth wall holds; confirm placement inherits box membership for boxed-parent offspring (G1/G3); auto-confirm sweep skips mixed-wall proposals as non-eligible (G2, Q-U.5). #185's sweep-path reproduction no longer reproduces — the guards pin that fact. |
| `form/q1_cb_exchange_recovery_prep_test_spec.py` | **4/7** | W1/W2/W3 FAIL — recovery erases the completion marker; spurious `ExchangeError` over clean state; importer blesses an incoherent pair. Guards (W2F/P3/P5/P5D) PASS. Basis for the C-B design. |
| `form/c2_resonance_engine_test_spec.py` | **2/11** | Controls PASS (bare-float coherence exists, `grow_ideas` runs); all 9 C2 contract checks FAIL — no typed verdict, no relatedness query, no development-evidence parameter, no targeted pulse, no decay/fusion/split, Enhance is a gate object not an operation, temperature is module constants only. |
| `form/c3_witness_time_test_spec.py` | **2/8** | Undo/redo exist session-local; 7 rooms list. FAIL: Trace retrieves 27 of 40 noted entries (capture cut), fresh-load undo is `{'ok': False, 'reason': 'nothing to undo'}`, Mirror/failure-doors/room-write/Alpha ceremony all absent. |
| `form/c6_boxes_freeze_test_spec.py` | **4/9** | Box/unbox, multiple named boxes, `scope_ids`, place position PASS. FAIL: standing private box, owner put/take door, freeze/pause, named Group surface, AUTO/BIND modes. |
| `form/c12_bridge_ledger_test_spec.py` | **1/5** | `import_packet ok=True` control PASS. FAIL: export/preview door, preview binding, bridge ledger, room bridge all absent. |
| `form/r5d_history_retention_test_spec.py` (carried, byte-identical) | **3/22** | The R5-D prep suite under the outstanding Keeper challenge of `13b33fa` — failing-first by design; the 19 red checks are the R5-C policy contract. |
| `form/c13_simulate_part1_test_spec.py` | **0/2** | t18: no declared effect inventory in the Simulate receipt; t19: no parallel-preview surface on executor or Program. |
| `form/sm35_ca_qe2_test_spec.py` | **0/2** | Both crash windows on the ordinary save path expose **HYBRID** on fresh load — the C-A scoping evidence for MWL #46. |

Registry path verified GREEN on this branch after the
`_spec` remediation: `c13_simulate_test.py` 20/20 (restored),
`sm35_pair_atomic_test.py` 45/45 (restored), `gs4_sandbox_test.py`
22/22 (extended, passing). No unregistered `*_test.py` ships in
this PR; no registered suite was left failing.

### §1.2 Design and evidence documents in this PR

- `director-reports/CH17_EVIDENCE_SWEEP_2026-11-20.md` — the
  Part's opening evidence act: per-house verdicts (H1 VERIFIED,
  H2 NARROWED, H3 VERIFIED surface, H4 CONFIRMED, H5 VERIFIED, H6
  UNKNOWN at depth, H7 CONFIRMED ×2, H8 CONFIRMED, H9 UNKNOWN at
  depth, H10 VERIFIED post-repair, H11 VERIFIED surface).
- `director-reports/Q1_CB_TRANSACTION_DESIGN_2026-11-20.md` —
  the C-B transaction design (lock-order table, P3 journal
  identity + idempotent disposal, P5 fail-closed classification
  table, C-A separation + Q-E2 minimum, mutants M1/M2/M3).
- `director-reports/r5d-evidence/PART_I_R5D_EVIDENCE_INDEX_2026-11-20.md`
  — index of the R5-D evidence chain (census 111, path proofs,
  S7 subset, R5RD 36/94, prep heads 7aea4c2 / 13b33fa).

### §1.3 C-A separation (recorded for MWL #46)

The Q-E2 minimum (Director 7040542941) — a fresh load exposes
OLD_ONLY or NEW_PAIR, never HYBRID — is already proven for the
CHECKPOINT path (SM-35 A/B, GREEN) and NOT proven for the
ORDINARY save path (the 0/2 spec above). C-A is separately scoped
and NOT authorized by Part I; its design is not written here; no
code is written for it; #46 stays GATED. Readers bypassing the
recovery boundary are explicitly outside the guarantee.

---

## §2 — Code-stage step zero (rename + registration, per spec)

For every `*_test_spec.py` in this PR, the first code-stage
commit renames it back to `*_test.py` AND registers it in
`form/regress.py` LIST in the same commit, so the suite enters
the registry path only when its implementation exists. No spec
file is renamed without its implementation landing.

| Spec file (this PR) | Step zero | Implementation it waits on |
|---|---|---|
| `q1_cb_exchange_recovery_prep_test_spec.py` | rename + LIST register | C-B code (needs Director authorization) |
| `c2_resonance_engine_test_spec.py` | rename + LIST register | C2 build (#121–#129) |
| `c3_witness_time_test_spec.py` | rename + LIST register | C3 build (#131–#136) |
| `c6_boxes_freeze_test_spec.py` | rename + LIST register | C6 build (#144–#147) |
| `c12_bridge_ledger_test_spec.py` | rename + LIST register | C12 build (#164–#166; #166 after #134) |
| `c13_simulate_part1_test_spec.py` | merge t18/t19 into `c13_simulate_test.py`, delete spec | C13 build (#167/#170) |
| `sm35_ca_qe2_test_spec.py` | merge CA-QE2-A/B into `sm35_pair_atomic_test.py` run_all, delete spec | C-A scope + authorization (not requested here) |
| `r5d_history_retention_test_spec.py` | rename + LIST register | R5-D code (Keeper challenge → Director bounded authorization, at most S7) |

---

## §3 — Campaign terms (binding)

- **×3 per state-sharing cluster**, strictly **one campaign at a
  time globally** (separate worktrees do not soften this —
  sharpened 2026-11-19; heavy standalone probes also wait for
  campaign terminal).
- Existing battery per cluster (package (g)): `persist_full_
  roundtrip_test`, `checkpoint_generation_stress_test`,
  `graph_journal_crash_test`, `supersession_lineage_restart_test`,
  `water_persistence_test`, `atomic_write_boundaries_test`,
  `owner_namespace_collision_test`, `nursery_confirm_race_test`,
  `growth_persistence_test`, `confirm_placement_test`,
  `resonance_lifecycle_gate_test`, `c13_simulate_test`,
  `duobeta_live_test`, `studio_security_test`, `gui_api_test`,
  plus each new cluster suite (after step zero).
- Campaign drivers reset SIGINT/SIGQUIT to SIG_DFL before
  running; logs under the goal's `hidden_files/` (never /tmp);
  full ×3 ≈ 35–60 min per cluster; a killed leg is NO RESULT
  and re-runs immediately from last verified state.
- **Tally contract:** every suite prints its own final tally line
  LAST; `form/regress.py` scores `smoke()` True AND the last
  `N/M` token n==m.
- Exact-head CI at the Part head (smoke + Python package) before
  any code-confirm ask.

---

## §4 — Dependencies and sequencing

- **Cross-Part (named, binding):** the C13 Simulate integration
  pass consumes **Part II's GP-E07 output** (settled Dell
  contracts — Simulate executes Dells). The C13 mechanism builds
  in parallel; only its contract-conformance pass waits for
  Part II's GP-E07 audit output.
- **Internal sequence:** #166 (room-to-room bridge) waits on #134
  (C3 Rooms) — C3 before C12 inside this Part. P08 waits on
  GP-E22's R3 blueprint retrieval (same Part). R5-D code waits on
  the Keeper challenge + Director authorization (authority
  dependency, not a Part dependency).
- **Part VI answers** Q-FI012.* (elastic intake waves touching
  H7/H8) and Q-GS.* (row #185's queued repair split) feed this
  Part's rows; this Part does not wait on them to build what is
  authorized here.
- **Collisions (map, binding):** `form/open.py` — Part I owns
  persistence/save/history/rooms/dock/growth regions; Part II
  owns parse/translate/condition/count regions (cross-region
  needs arrive as patch notes, never direct edits). Part I
  exclusive: `form/persist*.py`, `form/owner_state_lock.py`,
  `form/lifecycle.py`, `form/grow.py`,
  `form/dell_matrix/confirm_lineage.py`,
  `form/dell_matrix/dock_session.py`. Register JSON: each lane
  edits ONLY its own rows (surgical per-row edits, indent=1,
  ensure_ascii=False, re-render + `--check` byte-identical).

---

## §5 — Cluster plans (all 70 rows)

### §5.1 H7 — Memory & persistence (GP-E05, GP-E15)

| Row | Status → Target | Build (remainder) | Failing-first / battery |
|---|---|---|---|
| #46 pair-atomic audit | **GATED → GATED** | C-A scope only: the ordinary-save HYBRID is measured and recorded (§1.3). No build without a separate Director scope + authorization. | `sm35_ca_qe2_test_spec.py` **0/2** (HYBRID ×2) — shipped in this PR |
| #47 checkpoint sealing/rollback/directory-sync | PARTIAL → COMPLETE | Retained remainder of the DD-04 family: directory-sync failure modes beyond the landed checkpoint family. | `checkpoint_generation_stress_test` + `sm35_pair_atomic_test` (45/45 GREEN today) |
| #53 atomic-write orphan-temp + rollback cleanup bounds | PARTIAL → COMPLETE | Remainder: orphan-temp bounds under crash at every seam of `atomic_write`. | `atomic_write_boundaries_test` |
| #54 persistent envelopes under corrupt/unknown versions | PARTIAL → COMPLETE | Remainder: unknown-version envelopes must fail closed, never coerce. | `persist_full_roundtrip_test` + corrupt-envelope cases at code stage |
| #173 history retention/compaction contract | OPEN → PARTIAL | The retention contract lands (R5-C P1–P6 as the contract of record, indexed in `r5d-evidence/`). COMPLETE only with R5-D built (§0.1). | `r5d_history_retention_test_spec.py` **3/22** — shipped |

### §5.2 H8 — Doors, admission, host boundaries (GP-E17)

| Row | Status → Target | Build (remainder) | Failing-first / battery |
|---|---|---|---|
| #25 per-scope admission/registry certification remainder | PARTIAL → COMPLETE | Dispose the remaining per-scope admission/registry certification requests (72-07/SM-04 retained scope). | admission battery at code stage |
| #52 owner namespace collision + foreign-state rejection | PARTIAL → COMPLETE | Remainder of DD-12: foreign-state rejection at every load door, not only the audited one. | `owner_namespace_collision_test` |
| #65 stale field-snapshot + agent reconnect boundaries | PARTIAL → COMPLETE | Reconnect must revalidate the field snapshot or fail closed; no silent stale-field work. | code-stage spec suite (to be authored) |
| #66 agent host-bound idempotency, retries, conflicting envelopes | PARTIAL → COMPLETE | Remainder of SM-45: conflicting-envelope resolution is declared, never last-write-wins by accident. | code-stage spec suite (to be authored) |
| #118 Q1 journaled Exchange import/recovery | **GATED → GATED** | C-B design (this PR) + prep suite. Code only under Director C-B authorization. | `q1_cb_exchange_recovery_prep_test_spec.py` **4/7** — shipped |

### §5.3 Save & journal transactions (GP-E15, GP-E17)

| Row | Status → Target | Build (remainder) | Failing-first / battery |
|---|---|---|---|
| #48 Exchange journaled import/recovery + receipt disposal | PARTIAL → COMPLETE | The non-GATED half of the Q1 family: journal/recovery/receipt-disposal behavior outside the #118 transaction scope; lands with or without C-B code per its own scope. Includes the **R14 residual**: `exchange.py:739` detail `[:2000]` cut removed (H8/C12 fold-in). | prep spec (shared with #118) + `graph_journal_crash_test` |
| #49 Nursery optimistic concurrency + duplicate confirmation | PARTIAL → COMPLETE | Remainder of DD-09: duplicate confirmation is idempotent or refused, never double-placed. | `nursery_confirm_race_test` |
| #50 semantic-graph journals vs derived Program effects | PARTIAL → COMPLETE | Remainder of DD-05: journal validation must catch graph/Program divergence at load, not at use. | `graph_journal_crash_test` |
| #51 supersession crash + acceptance lineage across restart | PARTIAL → COMPLETE | Remainder of SM-30: acceptance lineage survives restart byte-for-byte or fails closed. | `supersession_lineage_restart_test` |

### §5.4 Field / placement / Idea machinery (GP-E13, GP-E16, GP-E18)

| Row | Status → Target | Build (remainder) | Failing-first / battery |
|---|---|---|---|
| #55 Plane-to-Idea bridge / Track D | PARTIAL → COMPLETE | Remainder of SM-27/SM-28: the bridge carries identity + provenance in both directions. | code-stage spec suite (to be authored) |
| #56 Idea + semantic-graph node identity through lifecycle | PARTIAL → COMPLETE | Remainder of SM-26: one identity across create/grow/supersede/archive — no re-minting at lifecycle edges. | `graph_journal_crash_test` + identity cases |
| #57 nested Idea parent/child + promotion invariants | PARTIAL → COMPLETE | Remainder of G-01/SM-26/SM-28: promotion preserves child invariants or refuses. | code-stage spec suite (to be authored) |
| #144 Boxes — standing/named sandboxes | OPEN → COMPLETE | Standing private box, owner put/take door, multiple named boxes as one surface (DD-17). | `c6_boxes_freeze_test_spec.py` (box checks) **4/9** — shipped |
| #145 Freeze — room/item pause | OPEN → COMPLETE | Paused items stay visible, retain contents/position, stop aging/growth (DD-22). | `c6_boxes_freeze_test_spec.py` (freeze check) — shipped |
| #146 Scope/Group integration | OPEN → COMPLETE | The 53↔82 partnership as one pair; a named Group is never automatically a box or a scope. | `c6_boxes_freeze_test_spec.py` (Group check) — shipped |
| #147 Placement — idea/body/both, AUTO/BIND | OPEN → COMPLETE | Replacement retains intended position; child placement respects AUTO/BIND (DD-50 grounding). | `c6_boxes_freeze_test_spec.py` (placement checks) — shipped |

### §5.5 Gate & Growth (GP-E19 adjacent, GP-E16)

| Row | Status → Target | Build (remainder) | Failing-first / battery |
|---|---|---|---|
| #58 active/faded/superseded participation across all consumers | PARTIAL → COMPLETE | Remainder of DD-13: every consumer honors participation state — no consumer re-derives it. | `resonance_lifecycle_gate_test` |
| #60 knowledge selection, scope, lineage, dependencies | PARTIAL → COMPLETE | Remainder of SM-37: selection respects scope + lineage + dependency closure together. | code-stage spec suite (to be authored) |
| #62 resonance/harmony → Nursery proposals at the human gate | PARTIAL → COMPLETE | Proposals arrive at Ace's gate with their evidence attached; the gate remains Ace's sovereign act. | `resonance_lifecycle_gate_test` + C2 suite overlap |
| #67 AcceptancePolicy delegation, expiry, revocation chains | PARTIAL → COMPLETE | Remainder of SM-32: a revoked delegation fails closed everywhere, including mid-chain. | code-stage spec suite (to be authored) |
| #185 sandbox dock-landing + confirm-placement wall blindness | OPEN → PARTIAL | The Q-U.2 dock-landing circuit (authorized, bounded): docked proposals land under the same wall rules verified in GS-4 RUN G. Full close awaits Part VI Q-U answers; Q-U.4 manual-confirm semantics need Ace's ruling (§0). | `gs4_sandbox_test.py` RUN G **22/22** guards — shipped |

### §5.6 Semantic graph & views (GP-E13)

| Row | Status → Target | Build (remainder) | Failing-first / battery |
|---|---|---|---|
| #61 cause/depend/provenance explanations to real graph evidence | PARTIAL → COMPLETE | Remainder of SM-38: every explanation resolves to graph evidence or says UNKNOWN — no narrative-only provenance. | code-stage spec suite (to be authored) |
| #63 epistemic source/status through views + spatial consumers | PARTIAL → COMPLETE | Source/status survive every view transform; a view may narrow, never launder status. | code-stage spec suite (to be authored) |

### §5.7 Learning persistence (GP-E21)

| Row | Status → Target | Build (remainder) | Failing-first / battery |
|---|---|---|---|
| #69 DuoBeta outcome evidence + learning ledger persistence | PARTIAL → COMPLETE | Remainder of SM-41: the ledger persists outcome evidence with the observation/learning separation intact (observation never silently becomes learning). | `duobeta_live_test` |
| #70 learned-score saturation + opt-out reversibility | PARTIAL → COMPLETE | Remainder of SM-42: saturation is bounded and declared; opt-out reverses learned influence fully. | `duobeta_live_test` + saturation cases |
| #71 provider errors, prompt/output validation, protected values | PARTIAL → COMPLETE | Remainder of SM-43: provider failure surfaces as typed refusal; protected values never enter prompts/outputs unguarded. | code-stage spec suite (to be authored) |
| #72 selfgrow auxiliary ledger isolation | PARTIAL → COMPLETE | The auxiliary ledger can never write canonical state — isolation proven by attempted-write cases. | code-stage spec suite (to be authored) |

### §5.8 Studio & surfaces machinery (GP-E24)

| Row | Status → Target | Build (remainder) | Failing-first / battery |
|---|---|---|---|
| #76 Studio Host/Origin/token + malformed HTTP regression | PARTIAL → COMPLETE | Remainder of SM-51: the regression battery becomes a standing suite, not a one-off pass. | `studio_security_test` |
| #77 Studio state refresh, stale owner state, receipt reconstruction | PARTIAL → COMPLETE | Stale owner state is detected and receipted, never rendered as current. | `gui_api_test` + refresh cases |
| #79 Studio keyboard, focus, constrained viewport | PARTIAL → COMPLETE | Remainder of SM-56: keyboard/focus contract under constrained viewports. | `gui_api_test` |
| #81 2D spatial placement, rendering, restore invariants | PARTIAL → COMPLETE | Remainder of SM-40: restore reproduces placement exactly or fails closed. | `gui_api_test` + placement cases |

### §5.9 Instruments (GP-E26)

| Row | Status → Target | Build (remainder) | Failing-first / battery |
|---|---|---|---|
| #83 Form as source of truth vs frozen JS/preform drift | PARTIAL → COMPLETE | Remainder of SM-63: drift between Form and frozen surfaces is detected by a standing check. | code-stage check (to be authored) |
| #84 changed-file lint + Python-version compatibility | PARTIAL → COMPLETE | Remainder of SM-61: lint/version checks run on the changed-file set, CI-shaped. | code-stage check (to be authored) |
| #87 low-memory + large-state performance baselines | PARTIAL → COMPLETE | Remainder of SM-59/SM-60: repeatable baselines with recorded numbers, re-runnable. | baseline harness at code stage |
| #89 protected-value canaries across outward evidence surfaces | PARTIAL → COMPLETE | Remainder of SM-20: canaries on every outward surface (reports, receipts, logs), not only the audited ones. | canary cases at code stage |
| #98 traceability: runtime behavior → receipts, outcomes, persisted evidence | OPEN → COMPLETE | SM-64: every runtime behavior named in a receipt resolves to persisted evidence. Includes the **R4-A7 source-comment repair** (H10 instrument hygiene fold-in). | code-stage spec suite (to be authored) |

### §5.10 Spine / flow / coupling

| Row | Status → Target | Build (remainder) | Failing-first / battery |
|---|---|---|---|
| #34 legacy flow executor vs canonical chain ownership | **GATED → GATED** | No build. The reconciliation closes only under its recorded disposition. | — (gate) |
| #44 per-member ManifestSet + typed chainlink transport stress | PARTIAL → COMPLETE | Remainder of SM-21: typed transport under stress; untyped fallbacks refuse. | code-stage stress cases |
| #88 reduce oversized live-module coupling, no behavior change | OPEN → PARTIAL | Incremental, behavior-preserving decoupling of the largest live modules (Part I regions first). PARTIAL is the honest target for one Part's pass. | full battery green before/after each step |

### §5.11 Persona & Dock (GP-E23)

| Row | Status → Target | Build (remainder) | Failing-first / battery |
|---|---|---|---|
| #68 DirectorSession remains recommendations-only | PARTIAL → COMPLETE | Remainder of SM-46: a DirectorSession can recommend; any actuation path is refused and receipted. | code-stage spec suite (to be authored) |
| #97 BIMO/persona views advisory; cannot bypass host-bound authority | OPEN → COMPLETE | SM-47: persona views are advisory surfaces; authority checks bind at the host door regardless of the active persona. | code-stage spec suite (to be authored) |
| #154 Resident Psalm | OPEN → COMPLETE | Visible start/stop, bounded work, proposal-only output; presence grants no authority. | code-stage spec suite (to be authored) |
| #155 multi-Psalm / BIMO execution design | OPEN → OPEN (design only) | Design placement in this Part: instance semantics + the Ace-approved-roster requirement recorded. **Build blocked on Ace's roster approval (NEEDS_OVERSEER).** | — (no build) |

### §5.12 C2 — Resonance Core (GP-E19)

The C2 candidate engine, rows #121–#129, all OPEN → COMPLETE as
one circuit (the Director R1 §14.9 bounded candidate first, then
the family). Failing-first: `c2_resonance_engine_test_spec.py`
**2/11** — shipped in this PR.

| Row | Build |
|---|---|
| #121 bounded candidate | Graded-input-to-verdict invariant on one real canonical path — the first C2 landing; everything else in the family keys off its verdict type. |
| #122 relatedness model | Resonance exposes with-whom / how-strong / why over agreed fixtures (replaces the bare float as the consumer surface; the float remains as the score field inside the verdict). |
| #123 development-coupled growth | Growth responds to agreed development evidence; attention is the shared currency — `grow_ideas` gains the development-evidence parameter the spec probes for. |
| #124 targeted Pulse | Pulse obeys selected targets and exclusions (pairs with the **H-4 pulse rename** — Director approval, failing-first first). |
| #125 decline-coupled Decay | Decay coupled to decline evidence, with the same typed-verdict discipline. |
| #126 fusion (Merge) | Merge carries parent substance + provenance while preserving parents (DD-15). |
| #127 partition (Split) | Split keeps each resonating cluster intact; zero/one-cluster and ties handled honestly (DD-16). |
| #128 enhancement outcome | Enhance redefined per Ace's ruling (DD-23) — from gate object to an operation with an outcome contract. |
| #129 temperature design | Temperature as a typed per-consumer intensity control, not a secret global switch (DD-19). |

### §5.13 C3 — Failure & Time (GP-E16)

Rows #131–#136. Failing-first: `c3_witness_time_test_spec.py`
**2/8** — shipped. Internal order: #134 (Rooms) before C12's
#166 (§4).

| Row | Status → Target | Build |
|---|---|---|
| #131 Mirror true compare | OPEN → COMPLETE | Pair comparison through the C3 comparator, honest pagination (shown/total). |
| #132 Trace full coverage | OPEN → COMPLETE | Trace covers the entire current process — full retrieval beyond 512 entries without silent loss (the measured cut: 27 of 40 returned). Shown/total truthfulness binds (DD-52). |
| #133 Failure doors | OPEN → COMPLETE | Analyze / Revert / Retry per Ace's failure doctrine: Retry targets an identified failure, never a blind re-run (DD-32). |
| #134 Rooms are Ace's to close | OPEN → COMPLETE | Chosen-room write/close operations cannot overwrite another room's later work; session scope declared (DD-53). |
| #135 Undo/redo like a real program | PARTIAL → COMPLETE | The R21 remainder: 30-step adjustable window, new-write tail invalidation, history crossing save/load (fresh-load undo measured absent today). SNAPSHOTS_CAP question (DD-54) is the Director's open ruling attached to this row. |
| #136 Alpha / history ceremony | OPEN → COMPLETE | Old generations freeze/confirm/restore under new code; the ceremony is explicit, never implicit migration. |

### §5.14 C12 — Bridge (GP-E17)

Rows #164–#166. Failing-first: `c12_bridge_ledger_test_spec.py`
**1/5** — shipped.

| Row | Status → Target | Build |
|---|---|---|
| #164 Bridge ledger | OPEN → COMPLETE | The ledger of all bridges: reports dock/Exchange facts without taking over their authority (DD-34). |
| #165 Exchange front door | OPEN → COMPLETE | Local export/import door: preview binds to payload (the previewed bytes are the imported bytes), imports stay Program-bound. |
| #166 Room-to-room bridge | OPEN → COMPLETE | Preview/transfer between rooms — only after #134 settles room semantics (§4); no cross-room writes without preview. |

### §5.15 C13 — Simulate (GP-E14)

Rows #167–#170. Failing-first: `c13_simulate_part1_test_spec.py`
**0/2** — shipped; parent suite `c13_simulate_test.py` stands
20/20 GREEN (the landed Simulate mechanism is not regressed by
this Part's remainder work).

| Row | Status → Target | Build |
|---|---|---|
| #167 explicit effect inventory | OPEN → COMPLETE | The Simulate receipt DECLARES its effect inventory — every state class the run touched (chains, compositions, planes, nursery, history). Credit settlement for merged circuit **#413** (C13 Simulate) rides this Part's register package per Director triage 7040622309. |
| #168 isolated executor adapter | OPEN → COMPLETE | The supported command executes against an isolated copy — never live state (DD-21). |
| #169 supported dry-run | OPEN → COMPLETE | A bounded supported subset FIRST; per-atom outcomes and a scoped diff. |
| #170 parallel preview | OPEN → COMPLETE | Per-arm preview shows each arm and its conflicts, never one blended answer. **Final integration consumes Part II's GP-E07 output (§4).** |

---

## §6 — Edition 1 circuit mapping

| Circuit | Clusters / rows |
|---|---|
| GP-E05 (R5 history + R27 presentation) | §5.1 (#173, R5-D anchor) |
| GP-E13 (semantic/Plane identity & state ownership) | §5.4, §5.6 (#55–#57, #61, #63) |
| GP-E14 (one bounded Simulate mechanism) | §5.15 (#167–#170) |
| GP-E15 (save/recovery & atomic cross-owner writes) | §5.1, §5.3 (#46–#54) |
| GP-E16 (rooms, boxes, user undo, staged edits) | §5.4 (#144–#147), §5.13 (#131–#136) |
| GP-E17 (Exchange/Bridge/referential integrity) | §5.2, §5.3, §5.14 (#25, #48, #52, #118, #164–#166) |
| GP-E18 (geometry admission & Tree L1–L5) | §5.4 placement surfaces; H6 sweep debt (§7) |
| GP-E19 (resonance/harmony candidate engine) | §5.12 (#121–#129), §5.5 (#62) |
| GP-E21 (DuoBeta learning & rollback) | §5.7 (#69–#72) |
| GP-E22 (HCN R3 builder interface) | P08's prerequisite (blueprint retrieval is this circuit's first step) |
| GP-E23 (Dock & Psalm Matrix) | §5.11 (#97, #154, #155), §5.5 (#185 dock-landing) |
| GP-E24 (Studio/Console & human surfaces) | §5.8 (#76, #77, #79, #81) |
| GP-E26 (product audit / security / offline / performance) | §5.9 (#83, #84, #87, #89, #98) |

**Credit settlements riding this Part's register package**
(Director triage 7040622309): merged circuit **#413** (C13
Simulate — identity/credit decision, anchors #167–#170) and
merged circuit **#417** (FLOW_CONTRACT execution profiles —
anchors in the spine/flow cluster, §5.10). No auto-credit: the
settlements land exactly as the authorities decide them, inside
this Part's register write at code stage.

**30-video placements in this Part:** P01 (H10+H6), P02 (H7 —
inside existing persistence, no new component), P03 (H10 +
ledger + Nursery), P04 (H5) build at their houses in the code
stage; P06 (H9 geometry fixtures) builds with the H6 sweep debt;
**P05 BLOCKED** (frozen holdout dataset does not exist);
**P08 BLOCKED** (frozen R3 blueprint retrieval = GP-E22 step
one). Both blocks are named here so they cannot silently drop.

---

## §7 — CH-17 residuals carried into the code stage

From the sweep filed in this PR
(`CH17_EVIDENCE_SWEEP_2026-11-20.md`): H6 (senses) and H9
(surfaces) carry named sweep debt — per-module writer census for
the sense modules, surface write census for Studio/Console —
owed in the code stage alongside P06 and the Studio cluster.
The CONFIRMED counterexamples route to their clusters: H4 → C2
(§5.12), H7 → C-A scoping (GATED) + R5-D unlock (§5.1), H8 →
C-B authorization ask (§5.2). The sweep certifies nothing; it
converted one open challenge into per-house evidence states.

---

## §8 — Register flips PROPOSED (not applied in this PR)

This PR does **not** edit
`director-reports/master_work_list_items.json`. The flips below
are proposed for the code-stage register write that rides inside
this Part PR on confirm (surgical per-row edits to Part I rows
only, indent=1, ensure_ascii=False, re-render + `--check`
byte-identical). Current statuses verified against the register
at base af2519b6 (70 rows: PARTIAL 35, OPEN 32, GATED 3).

**PARTIAL → COMPLETE (35):** #25, #44, #47, #48, #49, #50, #51,
#52, #53, #54, #55, #56, #57, #58, #60, #61, #62, #63, #65, #66,
#67, #68, #69, #70, #71, #72, #76, #77, #79, #81, #83, #84, #87,
#89, #135 — each on its retained remainder closing with battery +
campaign + exact-head CI evidence at code-confirm.

**OPEN → COMPLETE (28):** #97, #98, #121, #122, #123, #124, #125,
#126, #127, #128, #129, #131, #132, #133, #134, #136, #144, #145,
#146, #147, #154, #164, #165, #166, #167, #168, #169, #170 — on
their first builds closing the named circuit scope.

**OPEN → PARTIAL (3):** #88 (incremental coupling — one Part's
pass cannot honestly complete it), #173 (retention contract
lands; COMPLETE only with R5-D built), #185 (dock-landing
circuit lands; full close awaits Part VI Q-U answers).

**Unchanged (4):** #34 **GATED**, #46 **GATED**, #118 **GATED**
(their recorded dispositions govern), #155 **OPEN** (design
placement only; build blocked on Ace's roster approval).

**Credit settlements (no status arithmetic invented):** #413
and #417 settlements land in the same register write exactly as
the authorities decide them (Director triage 7040622309).

Projected board effect IF every proposed flip confirms: 40/182 →
up to 103/182 COMPLETE over the Part's life — stated as a
projection, not a promise; flips land per-cluster as evidence
confirms, never in bulk ahead of proof.

---

## §9 — Authority asks (exact)

1. **PLAN-CONFIRM (this PR):** Director + Keeper — confirm the
   Part I plan as a whole (70 rows, 13 circuits, holds as
   stated) in the one-bundle presentation of the eight Parts.
2. **CODE-CONFIRM (later, at exact head):** Director + Keeper —
   scoped per cluster as campaigns + CI land.
3. **Standing separate asks (not created by this plan):**
   - Keeper challenge of R5-D prep `13b33fa` (outstanding), then
     Director bounded R5-D authorization (at most S7).
   - Director **C-B code authorization** on the design filed in
     this PR (`Q1_CB_TRANSACTION_DESIGN_2026-11-20.md`). Not
     requested by the prep alone; requested on the design.
   - Director **H-4 pulse rename approval** (failing-first test
     precedes any rename).
   - **Ace:** row #155 — RULED 2026-11-20 (closing section);
     Q-U.4 — RULED 2026-11-20 in Part VI (mixed ideas fully
     sandboxed first; Matrix placement decided as a whole).

---

## §10 — Files in this PR

**Created:**
- `director-reports/PART_I_PLAN_2026-11-20.md` (this plan)
- `director-reports/CH17_EVIDENCE_SWEEP_2026-11-20.md`
- `director-reports/Q1_CB_TRANSACTION_DESIGN_2026-11-20.md`
- `director-reports/r5d-evidence/PART_I_R5D_EVIDENCE_INDEX_2026-11-20.md`
- `form/q1_cb_exchange_recovery_prep_test_spec.py` (4/7)
- `form/c2_resonance_engine_test_spec.py` (2/11)
- `form/c3_witness_time_test_spec.py` (2/8)
- `form/c6_boxes_freeze_test_spec.py` (4/9)
- `form/c12_bridge_ledger_test_spec.py` (1/5)
- `form/c13_simulate_part1_test_spec.py` (0/2)
- `form/sm35_ca_qe2_test_spec.py` (0/2)
- `form/r5d_history_retention_test_spec.py` (3/22; content
  byte-identical to the challenged prep artifact)

**Modified:**
- `form/gs4_sandbox_test.py` — RUN G extension only (G1/G2/G3
  guards); suite 19/19 → 22/22, still GREEN, still registered.

**Not touched:** `director-reports/master_work_list_items.json`
(flips proposed in §8 only); `form/c13_simulate_test.py` and
`form/sm35_pair_atomic_test.py` (extensions shipped as companion
spec files instead — §2); all product code; PR #294's branch;
PR #498's branch; every other Part's files. No merges, no
regression campaigns in this lane (plan stage).

---

## ACE RULING ON ROW #155 — PERSONAMATRIX (2026-11-20)

Ace ruled (2026-11-20, answering the NEEDS_OVERSEER set): **he
trusts all his Psalm personas — incorporate them ALL.** The
build scope for row #155 / GP-E23 is therefore:

- **Incorporate every Psalm persona**; analyze each persona's
  abilities and place each in its proper position within
  DellMatrix as the **general setting** (placement by analyzed
  ability, not by arrival order).
- **Users can create new personas.** The persona layer —
  Ace's word: **personamatrix** — is a user experimentation
  layer: customizable, fun to create and test.
- The build stands on the EXISTING BIMO/persona machinery
  (`form/dell_matrix/personas.py` — BIMOBody with dock slots;
  docking confers no authority) — presentation, wiring,
  analysis and placement on that authority, no second engine.
- Fences unchanged: docking/persona presence grants no
  authority; Nursery confirmation remains Ace's sovereign act;
  personas propose, they do not land.

This ruling supersedes the earlier "design only, build blocked
on Ace's roster approval" framing wherever it appears in this
plan (the row table's #155 line included): the roster question
is answered — the roster is all of them.
