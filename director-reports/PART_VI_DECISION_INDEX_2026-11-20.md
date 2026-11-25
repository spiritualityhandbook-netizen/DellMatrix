# PART VI — DECISION INDEX + PER-FAMILY RULINGS DISPOSITION (2026-11-20)

**Part:** VI — The Unified Unknowns Register (PR #507).
**Purpose:** the completeness record the Keeper's deep pass
7055054831 named as missing for PLAN-CONFIRM — (a) a decision
index over every question packet in Part VI's scope, each
ruling verified first-hand against the GitHub record, and
(b) a per-family rulings disposition: what each ruling
settles, what it leaves open, and what Uni still owes.
**Companion:** `UNKNOWNS_DECISION_PACKETS_2026-11-20.md`
(packet texts unchanged; its two deltas are incorporated
here and superseded as the index of record).
**Verification method:** every ruling below was read
first-hand via `gh` on 2026-11-20 (comment bodies and
check-runs), not copied from plan text. Items whose ruling
is not pinned to a verifiable record are flagged UNPROVEN
rather than smoothed over.

---

## A0. FINAL PLAN RULING — SCOPED (PARTIAL) PLAN ACCEPTANCE
## (Director 7079043239, 2026-11-22)

**Verdict:** the Director's final plan-stage disposition at
PR #507 head 5a0bb10ea7dd91984e533dcc3ed7b3e555262a9e is a
**SCOPED (PARTIAL) PLAN ACCEPTANCE** of this unknowns
decision index, the adversarial source maps
(`PART_VI_ADVERSARIAL_ARTIFACTS_2026-11-21.md`), and the
work-order/artifact designs. The two adverse sets materially
satisfy the requirement to DOCUMENT the FI-011 W4 and
FI-012 intake attack surfaces and their planned negative
oracles.

**What this verdict is NOT:** it is not whole-Part plan
completion, not code, not an implementation-success claim,
and not an all-questions-cleared claim. No completion
credit is awarded. The existing MERGE HOLD remains pending
a separately scoped co-equal reconciliation of the held
claims below, and a clean §32 transaction remains required
for any lawful records-only disposition or future code
merge.

**HELD — Q-FI011.4 and Q-FI012.10 remain UNRESOLVED WITH
LIVE HOLDS** for the product stage and for any claim they
are closed:

- **Q-FI011.4 — HELD (FI-011 W4).** Affected paths:
  the confirmation surfaces the W4 hardening wave inherits —
  AcceptancePolicy grants + the canonical (Program) writer
  path, the raw Nursery store (`Nursery.confirm`), the
  owner opt-in auto-confirm sweep, and persisted store-file
  load. Owner of the resolution: the FI-011 W4
  implementation home, Part I. Must resolve: A7 grant
  reuse/single-use receipts; A8 raw `Nursery.confirm`
  actor/receipt bypass; A12 docked-agent origin-blind
  auto-confirm; A9 unknown-status load refusal — while
  explicitly retaining the local file-tamper trust-boundary
  disclosure.
- **Q-FI012.10 — HELD (FI-012 elastic intake).** Affected
  paths: the parse door (`form/idea_create.py`
  `parse_create_line`), the store door (`Nursery.add`), and
  the composed public path (`needs.parse_and_place`).
  Owner of the resolution: the FI-012 intake waves home,
  Part I. Must resolve: parse-door oversize/malformed;
  marker injection/forged line; effective words 120 vs
  declared 500 (Director selected 500 where authorized);
  boundary exact behavior; duplicate-add allowed with
  distinct IDs/receipts; plain public-path errors.
  Candidate Q1/R5-D/file-atomic code is EXCLUDED — no
  hidden re-authorizations.

**Red-outcome scope:** the red outcomes in the adversarial
artifacts are factual failing-first probes of EXISTING
behavior, not regressions introduced by this records/spec
PR; the claims are scoped to the measured entry paths, not
every runtime caller.

**Uni next (per the ruling):** present the next CODE attempt
at a new exact head with failing-first tests flipped for the
right reason and independent Keeper challenge.

---

## A. DECISION INDEX

Legend: **RULED** = owner's ruling on the record, verified.
**DISCHARGED** = closed by evidence in this PR. **OWED** =
no ruling exists yet; the named owner owes it. **HELD** =
plan-stage documentation accepted, but the question remains
UNRESOLVED under a live HOLD for the product stage and for
any closure claim. **UNPROVEN** =
a ruling is asserted in the packet record but is not pinned
to a verifiable GitHub comment ID.

| # | Question | Owner | Ruling / status | Authority record (verified) | Date |
|---|---|---|---|---|---|
| 1 | Q-35.1 — atomic-write sweep wiring (row #119) | Director | **RULED** — manual-only sweep CONFIRMED; the 2026-11-06 ruling stands | Director 7044836836 item 1; original verdict in `DIRECTOR_REPORT_72_35_ATOMIC_WRITE_BOUNDARIES.md` §4 (2026-11-06 18:04 CST, PR #316 records) | 2026-11-20 (confirming 2026-11-06) |
| 2 | Q-SNAP.3 — launch/signal hardening (row #175) | Director | **RULED** — Option A: bounded hardening circuit authorized; row stays OPEN until tested, reviewed code lands | Director 7044836836 item 2 | 2026-11-20 |
| 3 | Q-GS.1–Q-GS.11 — growth-selection mechanics | Director | **RULED** — scoped fail-closed resolver defaults (no silent ALL; typed `scope_ids` canonical; WITHIN refuses unbound; no invented RESONATING threshold; SANDBOX = isolation) | Director 7044836836 item 8 | 2026-11-20 |
| 4 | Q-ACE-GS.1 — "what is a project?" | Ace | **RULED** — B confirmed: a project is any idea and all the ideas within that idea (Ace's standing definition) | Ace rulings recorded 7045163243 | 2026-11-20 |
| 5 | Q-ACE-GS.2 — bare-"grow" surface | Ace | **RULED** — Keep: bare grow stays a lawful no-op that says so | Ace rulings recorded 7045163243 | 2026-11-20 |
| 6 | Q-U.2 — dock-landing circuit | Director | **RULED** — authorized as a bounded safety circuit; acknowledged standing in 7044836836 item 9 ("Q-U.2 dock landing remains separate"). Original authorizing comment ID not cited in the packet record — status corroborated, original ID UNPROVEN | Director 7044836836 item 9 (corroboration) | 2026-11-20 |
| 7 | Q-U.3 / Q-U.5 — confirm-placement inheritance; auto-confirm sweep treatment | Director + Keeper | **RULED (scoped)** — repair evidence accepted for the exact branches proven only; #185 NOT blanket COMPLETE; independent Keeper review of the #508 RUN G evidence at current head still required | Director 7044836836 item 9 | 2026-11-20 |
| 8 | Q-U.4 — manual-confirm cross-wall semantics | Ace | **RULED** — NO to the proposed ratification: ALL mixed ideas become fully sandboxed first; Matrix placement decided afterward, as a whole. Supersedes the shipped auto-skip-with-receipt semantics | Ace rulings recorded 7045163243 (after Director kept it ACE-RESERVED, 7044836836 item 9) | 2026-11-20 |
| 9 | Q-FI011.1 / .2 — standing-gate doctrine; ungateable list | Director | **RULED** — conditional standing-gate confirmation design (Ace-created, authenticated, revocable, exact-match only; receipt names the gate); ungateable categories named (other actors' state, security/permission changes, sandbox-crossing placement, destructive irreversible ops, hard eligibility/safety refusals, external effects needing fresh confirmation, undeclared side effects, unbounded blast radius). Design only — no product auto-confirm code authorized yet | Director 7044836836 item 6 | 2026-11-20 |
| 10 | Q-FI011.3 — gate placement default | Ace | Answered per the FI-011 development record (sandbox-first); not re-asked. **UNPROVEN by comment ID** — no GitHub comment ID is cited for it in the packet record | FI-011 development record (as cited in Packet 4) | pre-2026-11-20 |
| 11 | Q-FI011.4 — W4 adversarial scope | Keeper | **HELD — UNRESOLVED WITH LIVE HOLD** (plan-stage documentation ACCEPTED under the Director's SCOPED/PARTIAL plan acceptance; NOT closed, and no product-stage claim may treat it as closed). FI-011 W4 must resolve A7 grant reuse/single-use receipts, A8 raw `Nursery.confirm` actor/receipt bypass, A12 docked-agent origin-blind auto-confirm, A9 unknown-status load refusal, retaining the local file-tamper trust-boundary disclosure. Affected paths: AcceptancePolicy grants + canonical writer path, raw Nursery store, auto-confirm sweep, store-file load. Owner: Part I (FI-011 W4 implementation home) | Director final plan ruling 7079043239 (SCOPED/PARTIAL plan acceptance; Q-FI011.4 HELD); obligation stated in Director 7044836836 item 6 | 2026-11-22 |
| 12 | Q-FI012.1/.2/.4/.5/.6/.7/.9 — elastic-intake technical baseline | Director | **RULED** — technical baseline (owner/caller-boundary placement; amortized doubling where measured; counts AND canonical bytes; MAX_PARENTS refuses, never prunes; paged snapshots with shown/total + cursor/checksum; A4 done-state defined; Exchange via authenticated journaled gates; R5-C 2MiB/10k policy NOT repealed) | Director 7044836836 item 7 | 2026-11-20 |
| 13 | Q-FI012.3 — soft alert threshold | Ace | Treated as answered/excluded per the program map; not re-asked. **UNPROVEN by comment ID** — no GitHub comment ID is cited for it in the packet record | Program map (as cited in Packet 5) | pre-2026-11-20 |
| 14 | Q-FI012.8 — idea_create parse-path census | Uni | **DISCHARGED** — census delivered by probe in this PR (`FI012_Q8_CENSUS 8/8`): caps at `form/idea_create.py parse_create_line` (`label[:80]`, `detail[:2000]`, `goals[:12]`, `words[:500]`), all silently truncating; effective words cap is 120, not 500; store layer already honest | This PR (probe suite + CI) | 2026-11-20 |
| 15 | Q-FI012.10 — elastic-intake adversarial matrix | Keeper | **HELD — UNRESOLVED WITH LIVE HOLD** (plan-stage documentation ACCEPTED under the Director's SCOPED/PARTIAL plan acceptance; NOT closed). FI-012 must resolve parse-door oversize/malformed, marker injection/forged line, effective words 120 vs declared 500 (Director selected 500 where authorized), boundary exact behavior, duplicate-add allowed with distinct IDs/receipts, plain public-path errors. Candidate Q1/R5-D/file-atomic code EXCLUDED. Affected paths: parse door `form/idea_create.py parse_create_line`, store door `Nursery.add`, composed public path `needs.parse_and_place`. Owner: Part I (FI-012 intake waves home) | Director final plan ruling 7079043239 (SCOPED/PARTIAL plan acceptance; Q-FI012.10 HELD); Director 7044836836 item 7 | 2026-11-22 |
| 16 | Q-FI016.1 — database/SQL-style operations on ideas | Ace | **RULED** — A for now: measured read capability counts as the capability; index / incremental-write build DEFERRED until the program is in a more finished state, then revisited | Ace rulings recorded 7045163243; measured evidence in Packet 6 (FI016_CAPABILITY 12/12) | 2026-11-20 |
| 17 | Q-DD42.2 — While/Until refusal surfaces (row #12 remainder) | Director | **RULED** — Option A: typed condition-parse refusal at BOTH boundaries, before bound evaluation; zero-iterations + ok=True prohibited; `bound_unspecified` must not mask a parse failure | Director 7044836836 item 3 | 2026-11-20 |
| 18 | Q-DD18.2 — Pulse refusal chain policy | Director | **RULED** — ratified: continue + honest atom receipt (Pulse ok=false, chain ok=false); no universal chain-abort inference | Director 7044836836 item 4 | 2026-11-20 |
| 19 | R21 — DD-54 snapshot-cap question (row #135 remainder) | Director | **RULED** — `SNAPSHOTS_CAP=64` / `TRACES_CAP=512` are independent, counted, legitimate guards; PR #481's Q-LC.1 does NOT retire or unify them; row #135 correctly stays PARTIAL | Director 7044836836 item 5 | 2026-11-20 |
| 20 | DAF-09 / G-05 — whole-program certification | Director | **WITHHELD** — certification continues withheld pending Director-environment instrumented reproduction with raw logs (19/22 discrepancy, §31.3). This index offers NO local evidence toward it and does not touch the gate | Director 7044836836 item 11; restated Director 7056445974 | 2026-11-20 |
| 21 | Edition 1 DC-8 — 151[Harmonic] | Ace | **RULED** — A: stays documented, non-executing, explicit refusal | Ace rulings recorded 7045162604 (on #506) | 2026-11-20 |
| 22 | Edition 1 DC-9 — orphan Dells | Ace | **RULED** — A + maturation directive: orphans intact + labeled, case-by-case; post-code-stage, each Dell individually completed to full maturity until the Dells are universal (future scope) | Ace rulings recorded 7045162604 | 2026-11-20 |
| 23 | Edition 1 DC-10 — Space | Ace | **RULED** — A: Space = advisory measured capacity, not a new force | Ace rulings recorded 7045162604 | 2026-11-20 |
| 24 | Edition 1 DC-1 / DC-6 / DC-7 / DC-11 | Director | **RULED** — RESOLVED in Edition 1; closed, no Part VI action | Edition 1 register (`03_DECISION_AND_UNKNOWN_REGISTER.md`) | 2026-11-18 |
| 25 | Edition 1 DC-2 / DC-3 (RESEARCH), DC-4 / DC-5 (EVIDENCE) | Owning Parts | **OPEN by design** — evidence owed by their owning Parts, not Part VI | Edition 1 register | 2026-11-18 |
| 26 | Edition 1 UU-1…UU-15 | Director | **RULED** — Director design decisions recorded; closure evidence rides the owning Parts' PRs | Edition 1 register | 2026-11-18 |

**Completeness count:** 26 index entries covering every
packet in Part VI's scope (Packets 1–10 + the Edition 1
index). **23 carry a verified ruling or discharge on the
record; 2 are HELD (both Keeper: Q-FI011.4, Q-FI012.10 —
plan-stage documentation accepted 2026-11-22 under the
Director's SCOPED/PARTIAL plan acceptance 7079043239, but
both remain UNRESOLVED WITH LIVE HOLDS for the product
stage and for any closure claim);
2 ruling-assertions are UNPROVEN by comment ID (Q-FI011.3,
Q-FI012.3 — both already answered/excluded and outside the
ask; Q-U.2's status is corroborated by 7044836836 with its
original ID uncited, counted inside the 23).** No answered
question is reopened by this index.

---

## B. PER-FAMILY RULINGS DISPOSITION

For each family: what the ruling SETTLES, what it LEAVES
OPEN, and what UNI STILL OWES.

### B1. Row #119 / Q-35.1 (Packet 1)
- **Settles:** sweep stays manual-only; no production wiring
  is or was authorized; the MWL row is the decision itself,
  not a repair mandate.
- **Leaves open:** nothing doctrinal. The residual
  orphan-`.dmtmp` risk (inert temps accumulate only on
  crashed writes) is stated, accepted, and carried by the
  manual sweep.
- **Uni owes:** the row #119 OPEN → COMPLETE flip with this
  citation, executed in Part VI's records-landing stage
  (after PLAN-CONFIRM + records-confirm at exact head) —
  not before, and not in this PR.

### B2. Row #175 / Q-SNAP.3 (Packet 2)
- **Settles:** the hardening direction (Option A) and its
  scope discipline — real launch entry points (REPL door,
  regress driver) and only `__main__` modules that spawn
  subprocess trees; no indiscriminate 122-module mutation;
  no DAF-09/G-11 inference.
- **Leaves open:** the build itself; row #175 stays OPEN
  until tested, independently reviewed code lands.
- **Uni owes:** the failing-first real-subprocess proof +
  build, in the owning Parts' territory (Part 0/VII for the
  regress driver, Part II for the REPL door). Not this PR.

### B3. Growth selection — Q-GS.1–.11 + Q-ACE-GS.1/.2 (Packet 3)
- **Settles:** the resolver's shape (fail-closed defaults,
  typed `scope_ids` canonical, Core II scope authority
  reused, WITHIN edge law, FAMILY = lineage-root set,
  CATEGORY = existing facets first, eligibility parity for
  explicit selectors, SANDBOX = isolation) and Ace's two
  surface answers (PROJECT = B; bare grow = lawful no-op).
- **Leaves open:** the build (Part II). RESONATING has NO
  numeric threshold — none may be invented; only existing
  typed affinity gates with pinned calibration + Keeper
  challenge, no pulse side effects by mere selection.
- **Uni owes:** in Part II — the 14-file production-caller
  audit/migration to deliberate ALL where intended, and the
  resolver build under these defaults. Nothing in Part VI.

### B4. GS-4 repair split — Q-U.2/.3/.4/.5 (Packet 3B, row #185 remainder)
- **Settles:** Q-U.4's semantics by Ace's rule (mixed ideas
  fully sandboxed first, whole; Matrix placement decided
  afterward as a whole) — this SUPERSEDES the shipped
  auto-skip-with-receipt behavior for mixed-wall proposals.
  Q-U.3/.5 evidence accepted for the exact branches proven.
- **Leaves open:** #185 is NOT blanket COMPLETE. Q-U.2
  (dock-landing) is authorized but unbuilt. The shipped
  sweep behavior (skip + receipt) does not yet implement
  Ace's sandbox-first-whole rule.
- **Uni owes:** (i) the Q-U.4 behavior-correction build —
  mixed arrivals sandbox whole instead of being skipped —
  as Part I's #185-remainder work; (ii) the Q-U.2
  dock-landing build (Part I). **Keeper owes:** independent
  review of the #508 RUN G 22/22 evidence at current head.
  **Director + Keeper owe:** the #185 reconciliation act on
  this evidence.

### B5. FI-011 Psalm Nursery gates — Q-FI011.1/.2/.4 (Packet 4)
- **Settles:** the standing-gate doctrine in its narrow
  form (a gate is Ace's own prior act; exact match only;
  anything ambiguous/widened/unmatched/stale stays PENDING;
  receipt names the gate) and the ungateable category list.
- **Leaves open:** Q-FI011.4 is **HELD** (Director
  7079043239, 2026-11-22): the plan-stage documentation of
  the W4 adversarial scope is ACCEPTED under the SCOPED
  (PARTIAL) plan acceptance, but the question remains
  UNRESOLVED WITH A LIVE HOLD for the product stage and
  for any claim it is closed. FI-011 W4 must resolve A7
  grant reuse/single-use receipts, A8 raw `Nursery.confirm`
  actor/receipt bypass, A12 docked-agent origin-blind
  auto-confirm, and A9 unknown-status load refusal, while
  explicitly retaining the local file-tamper trust-boundary
  disclosure. Affected paths: AcceptancePolicy grants +
  canonical writer path, raw Nursery store, auto-confirm
  sweep, store-file load.
- **Uni owes:** the next CODE attempt at a new exact head
  with failing-first tests flipped for the right reason and
  independent Keeper challenge; then the W1–W4 builds in
  Part I (the FI-011 W4 implementation home) under the
  ruled design, only where separately authorized. Gate
  authoring is never a Psalm/agent act under any outcome.

### B6. FI-012 elastic intake — Q-FI012.1–.10 (Packet 5)
- **Settles:** the technical baseline for waves W1–W5
  (see index row 12), including that R5-C's explicit
  2MiB/10k owner-history policy is NOT repealed by the
  doctrine's "any size" language, and that Q1 holds take
  precedence over elastic intake.
- **Leaves open:** Q-FI012.10 is **HELD** (Director
  7079043239, 2026-11-22): the plan-stage documentation of
  the adversarial matrix is ACCEPTED under the SCOPED
  (PARTIAL) plan acceptance, but the question remains
  UNRESOLVED WITH A LIVE HOLD for the product stage and
  for any claim it is closed. FI-012 must resolve
  parse-door oversize/malformed, marker injection/forged
  line, effective words 120 vs declared 500 (Director
  selected 500 where authorized), boundary exact behavior,
  duplicate-add allowed with distinct IDs/receipts, and
  plain public-path errors. Candidate Q1/R5-D/file-atomic
  code is EXCLUDED. Affected paths: parse door
  `form/idea_create.py parse_create_line`, store door
  `Nursery.add`, composed public path
  `needs.parse_and_place`. Implementation of every wave.
- **Uni owes:** Q-FI012.8 is discharged, BUT the Director
  requires a reproducible public-path failing-first for the
  four silent truncations + the unreachable words cap
  BEFORE the W4 parse-wave implementation (the probe is
  accepted as source hypothesis, not as the failing-first).
  Waves build in Part I (the FI-012 intake waves home);
  the next CODE attempt is presented at a new exact head
  with failing-first tests flipped for the right reason and
  independent Keeper challenge.

### B7. FI-016 — Q-FI016.1 (Packet 6)
- **Settles:** the classification for now — measured native
  read capability (query/filter/group/cursor/PK + caller-side
  set/join composition) counts as the capability. No index,
  no query planner, no incremental write is claimed.
- **Leaves open:** the deferred index/incremental-write
  build, revisited when the program is in a more finished
  state (Ace's revisit condition, on record).
- **Uni owes:** nothing now. The measured cost table
  (quadratic whole-file write path; 37.98 s per 1,000-add
  build vs 1.33 s at 200) is the standing evidence for the
  revisit.

### B8. Q-DD42.2 (Packet 7, row #12 remainder)
- **Settles:** the contract — typed condition-parse refusal
  at both While and Until, before any bound interaction;
  the While case's silent zero-iterations + ok=True is
  prohibited behavior, on record as such.
- **Leaves open:** the build; row #12 stays OPEN until
  implementation + credit.
- **Uni owes:** one bounded failing-first circuit in
  Part II (the probe's §42 flips from pin to spec there).

### B9. Q-DD18.2 (Packet 8)
- **Settles:** chain policy — continue + honest atom
  receipt is the standing contract. Any strict stop-on-fail
  must be separately explicit, typed, and tested.
- **Leaves open:** nothing.
- **Uni owes:** nothing. Records only.

### B10. R21 / DD-54 (Packet 9, row #135 remainder)
- **Settles:** the two Core II caps are independent
  legitimate guards; no unified-cap reading; row #135
  correctly stays PARTIAL.
- **Leaves open:** only a hypothetical future unified undo
  interface, which would need its own design + pre-fix
  proofs — not owed by anyone now.
- **Uni owes:** nothing.

### B11. DAF-09 / G-05 (Packet 10) — GATE UNTOUCHED
- **Settles:** nothing, by design. Certification remains
  WITHHELD; the §31.3 discrepancy (Director environment
  19/22 vs local full pass) is unresolved and local evidence
  cannot discharge it.
- **Leaves open:** the instrumented-driver rerun in the
  Director's environment + his disposition — Director-side
  only.
- **Uni owes:** nothing on this gate, and offers nothing.
  Part VI cites this packet only as "evidence requirement
  restated."

### B12. Edition 1 UU / DC families
- **Settles:** UU-1…UU-15 carry Director design decisions;
  DC-1/6/7/11 are closed; DC-8/9/10 now carry Ace's
  2026-11-20 rulings (index rows 21–23).
- **Leaves open:** DC-2/3/4/5 evidence, owed by their owning
  Parts; DC-9's maturation directive is future scope that
  activates after the plan's code runs properly.
- **Uni owes:** nothing inside Part VI.

---

## C. PLAN VERDICT AND WHAT REMAINS

The Director's final plan ruling landed 2026-11-22
(7079043239): **SCOPED (PARTIAL) PLAN ACCEPTANCE** of this
index, the adversarial source maps, and the
work-order/artifact designs — integrated at §A0 above. The
earlier withholding position (Director 7056445974:
PLAN-CONFIRM withheld pending the Keeper's independent
challenge, discharged via the Keeper-carried Gemini
CHALLENGE PASS 7065606534 and Director design rulings
7065729752 / 7066291209) is superseded by that ruling as
the plan-stage disposition of record. This acceptance is
PARTIAL: it is not whole-Part plan completion, not code,
and not an all-questions-cleared claim.

What remains:

- **Q-FI011.4 and Q-FI012.10 stay HELD** — UNRESOLVED WITH
  LIVE HOLDS (§A0, index rows 11 and 15, B5, B6). The held
  claims may not be merged as closed without a separately
  scoped co-equal reconciliation.
- **MERGE HOLD stands** pending that reconciliation; a
  clean §32 transaction remains required for any lawful
  records-only disposition or future code merge.
- **Uni next:** present the next CODE attempt at a new
  exact head with failing-first tests flipped for the right
  reason and independent Keeper challenge.

No merge is requested or implied by this record; register
flips ride the records-landing stage as ruled (B1).
