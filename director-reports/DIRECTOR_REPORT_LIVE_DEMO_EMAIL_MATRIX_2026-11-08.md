# DIRECTOR REPORT — Live-model demonstration + Email Matrix live proof (2026-11-08)

Submitted by Uni Ω under the Director's live-demonstration directive
(relayed by Ace 2026-11-08 06:37 CST) and the Email Matrix directive
(Ace 2026-11-08 07:03 CST; Director review email 2026-11-08 07:32 CST,
Gmail 1a1bb5ca6319ecf2 — received via Ace's relay in chat; the main
session's direct read of that message was flagged by a safety check
and is recorded as unprocessed there; this package answers the
relayed text, which Ace also pasted in full).

No private email bodies or credentials appear in this package.
Email-derived items are referenced by ID and subject label only.

## 0. EXECUTED IDENTITY

- Code: main `7c08f1225479ca8b2a968cff752a065d0158f37d` (PR #330
  merge). All runs executed in a disposable clone at that exact SHA.
- Model/provider: **Gemini `gemini-3-flash-preview`** (transport-
  reported modelVersion), reached through the custom.gemini vault
  connector (API key held only in the Secure Vault; surrogate-based
  egress; the key never exists in the VM or process). The product
  bridge cannot carry vault credentials — the demo sessions were
  wired exactly as `inference_dock.dock()` wires them (snap
  registration, durable session record, field-snapshot coordinator)
  with a host adapter provider. Recorded as a finding (§5).
- Available-model evidence (API's own errors, 2026-11-08):
  gemini-2.5-flash / -lite / -pro return 404 "no longer available
  to new users" on this account; gemini-flash-latest returned 503
  (high demand); gemini-3-flash-preview is served.

## 1. LIVE-MODEL DEMO — STEPS 1–5 (milestone 1)

Seed ideas (owner LIVEDEMO12DF79): "Build a House"
(uid build_a_house_2795), "Make an Album" (uid make_an_album_6833).

- Step 1 (connect): real Gemini through the dock. An offline probe
  first showed the failure path: with no provider configured,
  propose returns `{ok: false, reason: provider_failure}` — but
  the detail is only "ProviderError": **the dock discards the
  bridge's actionable cause** (Proposal B, §6).
- Step 2 (scoped context): the semantic verbs build prompts from
  the canonical field snapshot for named target IDs only;
  `propose(context=...)` screens an explicit bounded context
  (structured + decoded protected-material screens) before any
  provider call (SD-4 lineage).
- Step 3 (PENDING proposal): free-form ask returned real prose →
  dock receipt `{ok: false, reason: invalid_output, detail:
  "malformed model output: not JSON"}` (the ask path never states
  the JSON contract — Proposal B). `synthesize([house, album])`
  returned clean schema JSON on the first attempt → PENDING
  proposal **"The Sonic Homestead Residency"**
  (pid the_sonic_homestead_residenc_4804; parents
  [build_a_house_2795, make_an_album_6833]; origin
  `dock:host:demo:gemini:gemini-3-flash-preview`). The model's
  raw JSON was shown to Ace verbatim in chat. The model proposed
  its own variant (a live-work residential studio), not the
  plain "music studio" of the example — as the directive
  anticipated ("even when it suggests something different").
- Step 4 (human gate): Ace confirmed in chat 2026-11-08 06:57 CST.
  Applied exactly once (units 0 → 1, authored detail/goals
  intact); a second confirm refused "not found or not pending",
  count unchanged.
- Step 5 (restart): fresh process reload — the accepted idea,
  both parents, the confirmed proposal status and the origin all
  survive. **Milestone 1 (steps 1–5 together, real model):
  ACHIEVED.** Step 6 (Ace's timed usefulness testing) and the
  recording/brief remain open.

## 2. EMAIL MATRIX — INGEST (Ace's slice: last 90 days, Primary)

- Enumeration: 1,075 messages / 1,055 conversations
  (`in:inbox category:primary after:2026/08/09`).
- Metadata fetch (local only): **kept 1,048; excluded 7
  credential-shaped** by subject screen BEFORE storage (including
  the emailed Gemini API key message, never opened); 0 failed.
- Build (owner EMAILFIELD8B0610): one confirmed unit per
  conversation (label = subject; detail = correspondent + date +
  count + Gmail snippet; origin `gmail:conversation`; reviewer
  human:ace, producer email-ingest — Ace directed the ingest of
  his own data; his gate applies to model proposals). 1,048/1,048
  confirmed, 0 failures, saved.
- Local shape (no model): top senders MyClaw Newsletter 64,
  Ridge 61, NFL Daily 57, Acetoocold (Director relays) 54, Chase
  alerts 45, Word Smarts 39, Aaron's 31, DistroKid 30, Experian
  30; months Aug 244 / Sep 338 / Oct 334 / Nov (8 days) 132; only
  20 of 1,055 threads are multi-message.

## 3. EMAIL MATRIX — RELATIONS, APPROVALS, RECEIPTS

Relate pass (real Gemini, docked session `host:email-test`):

1. **"DellMatrix Director Review Sequence: PRs #318, #328, #329,
   #330"** — pid dellmatrix_director_review_s_9452, via
   `relate_field` on a Director-review anchor. Parents (4):
   dellmatrix_director_review_7_3780, _7_3542, _3_3136, _7_3674.
   The model's reason narrates the sequence and #330's hold.
2. **"Google Business Profile management for Ultimate Stain And
   Seal (Oct-Nov 2026)"** — pid google_business_profile_mana_6542,
   via `relate_field` on the mentor-business anchor. Parents (3):
   ultimate_stain_and_seal_your_9688, ultimate_stain_and_seal_are__927,
   action_required_ultimate_sta_4129. The model's reason explicitly
   REJECTS a Director-review candidate as a false positive.

- Ace approval evidence: Ace tapped "Confirm both relation
  proposals" in chat 2026-11-08 07:29 CST.
- Application receipts: both confirms `{ok: true}`; units
  1,049 → 1,051 (exactly +2); pending → 0; saved.
- Exactly-once receipts: duplicate confirm on each pid returns
  `{ok: false, reason: "not found or not pending"}`; unit count
  unchanged (re-verified 2026-11-08 in a fresh process).
- Parent-link verification (fresh process): relation 1 parents
  4/4 resolve to Plane units; relation 2 parents 3/3 resolve.
- Independent fresh-process reload: final census (§4) and both
  relation units present with authored detail/goals intact.

## 4. CENSUS RECONCILIATION (the 1,051 question)

At the two-relation checkpoint:

| Class | Count | Identity |
|---|---|---|
| Source conversations (origin `gmail:conversation`) | 1,048 | one unit per kept conversation |
| Accepted relation ideas (origin `dock:host:email-test:gemini:gemini-3-flash-preview`) | 2 | §3 items 1–2 |
| Pre-existing / system idea | 1 | uid `welcome`, label "Welcome" — the seed unit every new Program carries; no proposal record, origin None; position 0 in the units collection |
| **Total Plane units** | **1,051** | 1,048 + 2 + 1 |
| Proposal records | 1,050 | 1,048 ingest + 2 relations (Welcome has none) |
| Pending proposals | 0 | |

1,048 + 2 = 1,050 counts only email-derived + relation units;
the +1 is the pre-existing system seed, not an ingest artifact.
After §5's third relation was confirmed (Ace, 2026-11-08 07:37
CST), the live census is **1,052 units / 1,051 proposals / 0
pending**.

## 5. SNAPSHOT COVERAGE — VERIFIED CAP, OMISSION PROOF, THIRD RELATION

The Director's code inspection is confirmed from the running
system. `AgentCoordinator.snapshot_for`
(form/dell_matrix/agent_coordinator.py:109-110) slices
`_MAX_SNAPSHOT_UNITS = 200` Plane units and
`_MAX_SNAPSHOT_IDEAS = 200` Nursery proposals **separately**,
first-slice in collection order, and exposes no coverage counts.

Which collection the "200/1,049" figure describes: the **Plane
units** slice — 200 of 1,049 units at the relate run (the ideas
slice was independently 200 of 1,050 proposals at that census).

Omission proof (fresh-process probe, positions are 0-based
indices in the Plane units collection):

- DistroKid target `problem_with_your_distrokid__1598`
  ("Problem with your DistroKid account!"): **position 219 —
  outside the 200 slice; NOT in the snapshot.** All 8
  DistroKid-labeled units sit at positions 219–350+; none is in
  the snapshot. `relate_field` on it returned
  `{ok: false, reason: unknown_target}`.
- Stripe unit `8_00_payment_to_x_was_unsucc_2745`
  ("$8.00 payment to X was unsuccessful"): **position 107 —
  inside the slice; present in the snapshot.** A verb relation
  needs BOTH targets resolvable, so the pair was unrelatable
  through the verbs. (This corrects any reading that both IDs
  were omitted: one was, one was not.)

Third relation — demonstrating reach to omitted material through
the dock's existing authorized explicit-context path
(`propose(context=...)`, scoped to exactly the two source ideas,
screens applied): Gemini authored **"Payment Failures"**
(pid payment_failures_4286; raw output shown to Ace verbatim;
detail: both vendors reported failed card payments within ten
days, indicating a broader issue with the primary payment
method). Ace confirmed in chat 2026-11-08 07:37 CST; applied
exactly once (duplicate refused); units 1,051 → 1,052.
**Honest limit:** the `propose` new-idea schema carries no
machine parent links (parents []); the linkage to
problem_with_your_distrokid__1598 and
8_00_payment_to_x_was_unsucc_2745 is recorded here as evidence,
not as graph structure. Native parent-linked reach beyond the
slice is the subject of the accompanying proposal
(DIRECTOR_PROPOSAL_SNAPSHOT_COVERAGE_2026-11-08).

## 6. PROPOSAL B — DOCK READINESS (bounded; ruling requested)

Observed live, two small admission defects:
(a) `_BridgeProvider` discards the bridge's error text — a dead
provider reports only "ProviderError", against the directive's
"provider failures reported clearly".
(b) The validators accept only bare JSON; a single ```json
fenced block from a real model is dropped as invalid_output,
and the ask/propose path never states the JSON contract.

Proposal (one PR, no schema weakening): (1) carry the bridge's
error text into ProviderError and surface it through the
existing sanitize_error (credentials/handles still redacted,
canary-tested); (2) accept a single fenced JSON block, then
enforce the SAME strict schema (keys, bounds, authority-key
rejection unchanged); no prose tolerance, no retry loop.
Acceptance: new registered suite with a scripted real-shaped
provider — fenced JSON lands PENDING (fails-first today); prose
still invalid_output; fenced JSON with an authority key still
rejected; provider-down propose returns provider_failure whose
detail carries the sanitized cause and never a planted canary
credential; r62 + p5 dock suites + full regression green; then
the live acceptance run.

Raw-output retention (the directive's "the model's actual
output must remain visible") is a SEPARATE ruling request: by
design the dock retains only prompt digest + context hash;
parsed fields are visible on the proposal, non-conformant raw
output is dropped with a reason code only. Q-LD.2 below.

## Anticipated probes

- "Is the Email Matrix evidence REAL_USER_PATH?" No — it is a
  host-driven docked session at INTEGRATION / PUBLIC_ENTRY_PATH
  level (product loaders + product dock wiring), with Ace's
  live approvals in chat. Labels are not upgraded.
- "Did any email body leave the machine?" No. Ingest is local;
  model calls carried only the snapshot-bounded entries the
  verbs selected, or the two explicitly scoped ideas in §5,
  under the dock's screens. The published package contains no
  bodies or snippets.
- "Why is 'copilot' not the demo provider?" It returns canned
  text, not a model call (bridge.py); using it would fake the
  demonstration.
- "Is the census inflated by duplicates?" 1,055 conversations
  were enumerated from Gmail thread IDs; duplicate subjects
  slug with _N suffixes as separate units (e.g. four
  "Problem with your DistroKid account!" units) — they are
  distinct conversations, counted once each.

## Questions for the Director

- Q-LD.1: Rule on Proposal B (§6) — authorize implementation,
  or hold?
- Q-LD.2: Raw model output retention for visibility — retain
  (bounded, sanitized, per-proposal) or keep the current
  digest-only design?
- Q-LD.3: Rule on the snapshot-coverage proposal
  (DIRECTOR_PROPOSAL_SNAPSHOT_COVERAGE_2026-11-08): is
  retrieval reachability the intended guarantee?
- Q-LD.4: Step 6 usefulness testing — proceed on Ace's
  schedule, with results appended to this report's line?
