# DIRECTOR REPORT — Live-model demonstration + Email Matrix live proof (2026-11-08)

Submitted by Uni Ω under the Director's live-demonstration directive
(relayed by Ace 2026-11-08 06:37 CST) and the Email Matrix directive
(Ace 2026-11-08 07:03 CST; Director review email 2026-11-08 07:32 CST,
Gmail 1a1bb5ca6319ecf2 — received via Ace's relay in chat; the main
session's direct read of that message was flagged by a safety check
and is recorded as unprocessed there; this package answers the
relayed text, which Ace also pasted in full).

**TOMBSTONE — 2026-11-17 (Ace scrap ruling).** The Email Matrix was
test material only. By Ace's ruling of 2026-11-17, the email-derived
information in this report — aggregate ingest statistics, the
top-sender table, the relation units, and all subject-derived unit
IDs — has been SCRAPPED from the public tree (tree-level only; git
history is not rewritten). The sections that carried it (§§2–4, and
the email-derived identifiers in §5) are replaced by this tombstone.
The live-model demonstration (§1), the snapshot-coverage engineering
finding (§5, identifiers removed), and Proposal B (§6) are product
work records and are retained. The U8 audit
(2026-11-17) verified the dataset itself was never in the tree; only
these derivatives were.

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

## 2. EMAIL MATRIX — INGEST

**SCRAPPED 2026-11-17** (Ace scrap ruling; see the tombstone note at
the head of this report). This section carried aggregate ingest
statistics of Ace's personal inbox (message/conversation counts, the
Gmail query, exclusion counts, a top-sender frequency table naming
real senders with counts, and a month distribution). That derived
content is removed from the public tree. What remains on the record:
on 2026-11-08, at Ace's own direction, a bounded slice of his Primary
inbox was ingested locally into a disposable Nursery field as test
material for the live demonstration; the field itself was never
committed to this repository (U8 audit, 2026-11-17).

## 3. EMAIL MATRIX — RELATIONS, APPROVALS, RECEIPTS

**SCRAPPED 2026-11-17** (Ace scrap ruling). This section carried two
model-built relation units in full, including subject-derived unit
IDs and parent IDs from Ace's personal mail. That derived content is
removed from the public tree. What remains on the record: two
relation proposals produced by the docked model over the test field
were confirmed by Ace in chat on 2026-11-08 and applied exactly once
each, with duplicate confirmations refused — the exactly-once and
parent-link mechanics were verified in a fresh process. The receipts
proved the dock mechanics; the email-derived content they carried is
scrapped.

## 4. CENSUS RECONCILIATION

**SCRAPPED 2026-11-17** (Ace scrap ruling). This section reconciled
unit/proposal counts of the email-derived test field. Those counts
are removed with the rest of the derived content. The census
mechanics finding — a pre-existing system seed unit explains a +1
difference between unit and proposal counts in a fresh field — is a
product behavior note and is retained in this sentence only.

## 5. SNAPSHOT COVERAGE — VERIFIED CAP, OMISSION PROOF, THIRD RELATION

The Director's code inspection is confirmed from the running
system. `AgentCoordinator.snapshot_for`
(form/dell_matrix/agent_coordinator.py:109-110) slices
`_MAX_SNAPSHOT_UNITS = 200` Plane units and
`_MAX_SNAPSHOT_IDEAS = 200` Nursery proposals **separately**,
first-slice in collection order, and exposes no coverage counts.

Which collection the "200/N" figure describes: the **Plane
units** slice — 200 of the field's units at the relate run (the
ideas slice was independently 200 of the field's proposals at
that census). (Field totals scrubbed 2026-11-17.)

Omission proof (fresh-process probe, positions are 0-based
indices in the Plane units collection; unit identities scrubbed
2026-11-17 under Ace's scrap ruling — positions and mechanics
retained):

- One email-derived target unit: **position 219 — outside the
  200 slice; NOT in the snapshot.** All 8 units of its label
  family sit at positions 219–350+; none is in the snapshot.
  `relate_field` on it returned
  `{ok: false, reason: unknown_target}`.
- A second email-derived unit: **position 107 — inside the
  slice; present in the snapshot.** A verb relation needs BOTH
  targets resolvable, so the pair was unrelatable through the
  verbs. (This corrects any reading that both units were
  omitted: one was, one was not.)

Third relation — demonstrating reach to omitted material through
the dock's existing authorized explicit-context path
(`propose(context=...)`, scoped to exactly the two source ideas,
screens applied): Gemini authored a relation grouping the two
units by their shared subject matter (pid and subject-derived
detail scrubbed 2026-11-17). Ace confirmed in chat 2026-11-08
07:37 CST; applied exactly once (duplicate refused); unit count
rose by exactly one.
**Honest limit:** the `propose` new-idea schema carries no
machine parent links (parents []); the linkage to the two source
units is recorded here as evidence, not as graph structure.
Native parent-linked reach beyond the slice is the subject of
the accompanying proposal
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
- "Is the census inflated by duplicates?" Conversations were
  enumerated from Gmail thread IDs; duplicate subjects slug
  with _N suffixes as separate units — they are distinct
  conversations, counted once each. (Email-derived specifics
  scrubbed 2026-11-17.)

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
