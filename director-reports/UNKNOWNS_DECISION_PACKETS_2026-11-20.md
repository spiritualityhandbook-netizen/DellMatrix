# PART VI — UNKNOWNS: PLAN + DECISION PACKETS (2026-11-20)

**Program:** DellMatrix Eight-Part Program (AGENTS.md §46; Ace
ruling 2026-11-20 — whole program planned in full, executed as
8 PRs, one per Part; GO-BIG amendment 2026-11-20 08:54 CST:
maximum content buildable under current authorizations, every
probeable unknown probed NOW).
**Part:** VI — The Unified Unknowns Register.
**Stage:** PLAN (of plan → confirm → code → confirm). This PR is
the plan stage: decision packets at full depth + every read-only
probe that could discharge or narrow an unknown, run and filed
as evidence. No production code. No register edits — flips are
PROPOSED below, effective only as ruled.
**Base pin:** main `af2519b6d239ef278397e277210d6da2467c36e5`.
**Branch:** `uni/part-6-unknowns`.
**Register rows owned:** #119 (OPEN), #175 (OPEN).

---

## 0. PROBE EVIDENCE INDEX (all run at base af2519b6, this PR)

Three new probe suites ride this PR. All are read-only
(temp files / uuid owners with exact cleanup / subprocess
micro-probes). Per the failure class proven on PR #503
(unregistered `*_test.py` → CI smoke OMITTED INTENDED ENTRY),
all three ARE registered in `form/regress.py` LIST in this
same PR (`:smoke` entries) and pass through the harness path
(smoke()=True; last tally tokens 8/8, 18/18, 12/12). No
campaign is run by this lane; the suites pin CURRENT behavior,
so a deliberate future change to a probed behavior updates
the probe in the same circuit (the atomic_write pin pattern).

| Suite | Tally | Discharges / narrows |
|---|---|---|
| `form/fi012_q8_census_probe_test.py` | **FI012_Q8_CENSUS 8/8** | Q-FI012.8 — DISCHARGED (Uni-owed census delivered) |
| `form/part6_unknowns_probe_test.py` | **PART6_UNKNOWNS_PROBE 18/18** | #119 census; #175 census + mechanism; R21 caps; Q-DD42.2 behavior; Q-DD18.2 behavior; Q-U.3/.4/.5 current-main status; Q-GS.1 caller census |
| `form/fi016_capability_probe_test.py` | **FI016_CAPABILITY 12/12** | Q-FI016.1 — measured capability + scale calculation delivered (classification remains Ace's) |

Re-run: `python3 form/<suite>.py` from the repo root; each
prints its tally line LAST.

**Headline narrowings (details in the packets):**

1. **Q-FI012.8 is DONE.** M-34's caps live at
   `form/idea_create.py parse_create_line` at the census values,
   silently truncating — while the Nursery store layer refuses
   over-bound input honestly. The defect is parse-layer only.
2. **The GS-4 confirm-placement remainder (Q-U.3/.4/.5) is
   BUILT.** Commit `60f1516` (2026-11-13, "Confirm-placement
   circuit: Q-U.3 + Q-U.4 + Q-U.5 + AUTO => SANDBOX FIRST")
   landed the repairs; this PR re-verified all three behaviors
   at current main. Register row #185's text still carries the
   pre-repair defect description — the remaining work is
   ratification + credit reconciliation, not a build.
3. **Q-DD42.2 is sharper than posed.** At current main an
   unparseable infix condition on While is silently read as
   FALSE (head reports ok=True); on Until it triggers a
   bound refusal that misattributes the cause. Receipts in
   Packet 7.
4. **Q-FI016.1 has its measured answer.** Query-side SQL
   analogues are real and fast into the thousands of records;
   the write path (per-add whole-file rewrite) is the measured
   quadratic cost. Numbers in Packet 6.
5. **Row #119 has a prior ruling on record.** The Director
   ruled Q-35.1 on 2026-11-06 ("sweep stays manual"); the
   register row was later written as if unruled. Packet 1 asks
   for confirmation-or-reopening, with the census refreshed:
   still zero production callers at af2519b6.

---

## PACKET 1 — Row #119 / Q-35.1: atomic-write sweep wiring

**Question (register text, exact):** "Atomic-write sweep wiring
decision (Q-35.1): sweep_stale_tmps has no production caller —
orphan .dmtmp cleanup is manual-only until the Director rules
(follow-up of the 72-35 row)."

**Owner:** Director. **Unblocks:** row #119 closure; closes the
last open thread of the 72-35 atomic-write circuit.

**Evidence:**
- Original finding (DIRECTOR_REPORT_72_35_ATOMIC_WRITE_
  BOUNDARIES.md §3): `sweep_stale_tmps` has NO production
  caller; orphan `.dmtmp` temps persist in the state directory
  until a manual sweep; they are inert (no loader reads them);
  generation-MEMBER orphans have an automatic reaper (the
  retention GC), raw `.dmtmp` orphans do not.
- **Prior ruling on record:** the same report (§5, Director
  verdict 2026-11-06 18:04 CST): "Q-35.2 YES; **Q-35.1 sweep
  stays manual, no production wiring authorized**." The MWL
  row, written later, presents the question as unruled — a
  records inconsistency this packet surfaces rather than
  silently resolving.
- **Refreshed census (this PR, PART6_UNKNOWNS_PROBE §119):**
  AST census over `form/**/*.py` at af2519b6 — production call
  sites of `sweep_stale_tmps`: **zero** (unchanged); test call
  sites: `form/atomic_write_boundaries_test.py` (which also
  pins the no-production-caller fact as check G — if a future
  circuit wires the sweep, that check fails deliberately).

**Options:** (a) Confirm the 2026-11-06 ruling stands → row
#119 COMPLETE as ruled-manual, packet cited. (b) Re-open: wire
the sweep into a production path (program open / load) as a new
bounded circuit — then this row stays OPEN and the circuit is
scoped in Part I (persistence territory). (c) Re-open
differently: wire into the save path only.

**Uni recommendation:** (a). Fourteen days of production since
the ruling produced no orphan-temp incident on record, the
temps are provably inert, and the retention GC already covers
generation members. Re-opening buys machinery against an
unobserved harm.

**Discharge path + cost:** one Director sentence (confirm or
re-open). If (a): the flip rides this Part's landing (records
only). If (b)/(c): a Part I circuit, est. one failing-first
suite + ×3 campaign — NOT in this PR's scope.

**PROPOSED register flip (as ruled only):** #119 OPEN →
COMPLETE under (a), citing the 2026-11-06 verdict + this
packet; otherwise stays OPEN with this packet cited.

---

## PACKET 2 — Row #175 / Q-SNAP.3: launch/signal hardening

**Question (register text, exact):** "Q-SNAP.3 launch/signal-
hardening proposal — proposal-only product change if still
desired; no G-11 or DAF-09 certification inference (Director
F6)."

**Question as posed at origin (DIRECTOR_REPORT_QSNAP1_
FOLLOWUP_2026-11-09, exact):** "Q-SNAP.3: the inherited-SIG_IGN
finding — authorize a bounded hardening circuit (entry points
establish SIGINT disposition), record as a finding only, or
decline?"

**Owner:** Director. **Unblocks:** row #175 closure; removes a
known launch-environment hazard class (the Q-SNAP.1 daf09
in-chain failures of 2026-11-09, where background-launched
chains inherited SIGINT=SIG_IGN and cancellation silently
never fired).

**Evidence (this PR, PART6_UNKNOWNS_PROBE §175):**
- **Entry-point census:** 122 modules under `form/` carry a
  `__main__` entry (plus the `form/repl.py` / `form/regress.py`
  doors). **The set that installs any SIGINT disposition
  handling is EMPTY** — no in-repo entry point hardens today.
  (The disposition reset the project relies on lives in
  out-of-repo chain launchers, per TOOLS.md's standing rule.)
- **Mechanism reproduced in this environment, today:** a
  Python child launched as a shell background job starts with
  SIGINT == SIG_IGN (measured 1); the same child launched in
  the foreground starts with the default handler (measured 0).
  The hazard is environmental and live, not historical.

**Options:** (a) Authorize the bounded hardening circuit:
production entry points (REPL door, regress driver, and the
`__main__` modules that launch work) establish SIGINT/SIGQUIT
disposition at startup; failing-first suite proves a
background-launched entry regains cancellation. (b) Finding
only: row closes as a recorded finding with this census
attached; the launcher-side rule stays the mitigation.
(c) Decline: row closes as declined.

**Uni recommendation:** (a), scoped to the two doors +
`__main__` modules that spawn subprocess trees (the census
table in the probe output is the work list). The failure mode
is silent cancellation loss — exactly the class that already
burned one campaign day (2026-11-09).

**Discharge path + cost:** Director ruling (one of a/b/c).
Under (a): the circuit itself belongs to Part 0/Part VII
territory (regress driver) + Part II (REPL door) — est. one
suite + one ×3 campaign slot. Under (b)/(c): records only,
flip rides this Part's landing.

**PROPOSED register flip (as ruled only):** #175 OPEN →
COMPLETE under (b) or (c), or under (a) when the hardening
circuit lands; otherwise stays OPEN with this packet cited.
No G-11 or DAF-09 inference is drawn from any outcome
(per the row's own fence).

---

## PACKET 3 — Q-GS.1–Q-GS.11: growth selection (Director) + Q-ACE-GS.1/.2 (Ace)

Source of record: `director-reports/GROWTH_SELECTION_PROPOSAL_
2026-11-12.md` §9 (PR #402, records; Ace's Growth Selection
Doctrine 2026-11-12). Status: "Q-GS.1–Q-GS.11 remain OWED and
unchanged" (DIRECTOR_REVIEW_QUEUE, post-merge disposition).
**Owners:** Director for Q-GS.1–.11; **Ace (NEEDS_OVERSEER)**
for Q-ACE-GS.1/.2 — routed non-blocking since 2026-11-12.
**Unblocks:** the growth-selection build (Part II territory);
Part I row #185's queued repair split is governed by the
companion Q-U rulings (Packet 3B).

**Questions (exact, from the proposal §9):**

- **Q-GS.1 Default:** bare growth = refuse-with-guidance (a),
  bridge (c), or other? Migration policy for the ~10 internal
  autonomous loops — each a deliberate ALL, or scoped by their
  own context?
- **Q-GS.2 Grammar home:** additive `scope=` parameter vs a
  typed scope_ids; receipt provenance shape (spec text +
  per-branch counts + exclusions)?
- **Q-GS.3 Core II bridge:** should growth honor `st.scope`
  (Dell 53) when set — one scope authority shared with
  spectrum ops, or growth-local resolution only (two scope
  systems risk)?
- **Q-GS.4 RESONATING:** affinity-to-seed at which gate
  (0.10/0.16/0.28)? Seed-required, or set-internal (all pairs
  within the candidate set)? May selection run a resonance
  pulse (side effects) or must it stay pulse-free (affinity
  only)?
- **Q-GS.5 WITHIN edge law:** unbound unit → self-only +
  named, or refuse? Partially-bound descendant sets → resolve
  with exclusions named (EKC-I style) — confirm.
- **Q-GS.6 SANDBOX semantics:** selection-only (PENDING
  proposals in the real nursery, evolve/forces untouched) vs
  isolation (no effects outside — GS-4 + side-effect
  scoping)? Which does the doctrine require at v1?
- **Q-GS.7 FAMILY:** lineage-root grouping as the v1 meaning
  of "family" — confirm, or name the intended structure.
- **Q-GS.8 CATEGORY:** v1 facets (skin/origin/lifecycle) only,
  or is a user-defined category/tag field on units wanted
  (new state)?
- **Q-GS.9 "Use idea to grow":** migrate from full-plane +
  post-filter to WITHIN(pid)-based scope? Preserve its
  deliberate include_superseded?
- **Q-GS.10 Profile benchmark:** growth stage names ALL
  explicitly on disposable state — confirm intended shape.
- **Q-GS.11 Eligibility:** unify the scope_ids branch under
  the contextual branch's eligibility/conflict/disposition
  gates, or keep the documented asymmetry (any live unit
  selectable by explicit ID/group/etc.)?

**For Ace (NEEDS_OVERSEER, non-blocking):**

- **Q-ACE-GS.1 What is a "project"?** A named set you curate
  (≈ a group), a root idea whose contents are the project
  (WITHIN already covers it), or a separate workspace?
  PROJECT selection cannot be built until this has a shape.
- **Q-ACE-GS.2** When you say "grow" with no selection
  picked, what should happen at the surface: stop and ask you
  to pick (or say ALL), or grow what you're currently looking
  at? (The user-facing face of Q-GS.1.)

**Evidence:**
- The proposal's grounding verdict stands: the doctrine is
  implementable mostly from existing machinery (ScopedPlaneView
  + scope_ids door, Core II named-group store with
  refuse-on-unknown, lineage grouping, SemanticGraph
  vocabulary + TD-1/TD-2 bridge, plane sandbox membership,
  affinity gates). Absent: the unified resolver, surface
  grammar for scope on the growth entry, a project construct,
  a user category system, and the bare-growth default ruling.
- The GS-4 sandbox finding that rode with this family is
  DISPOSED (repaired via PR #405; MWL #184) — it no longer
  waits on this packet; see Packet 3B for its residual.
- **Q-GS.1 blast radius, refreshed (this PR, PART6_UNKNOWNS_
  PROBE §GS1):** production callers of the `grow_ideas` entry
  at af2519b6 — 14 files: `form/accept.py`,
  `form/ancient/stonehenge_seed.py`,
  `form/dell_matrix/code_evolution.py`,
  `form/dell_matrix/function_150_loop.py`,
  `form/dell_matrix/live_host.py`,
  `form/dell_matrix/live_visual.py`,
  `form/dell_matrix/profile_board.py`,
  `form/dell_matrix/program_evolve_150_loop.py`,
  `form/dell_matrix/program_strength.py`,
  `form/dell_matrix/visual_evolve_loop.py`,
  `form/invariants.py`, `form/mandell/core_i_ops.py`,
  `form/mandell/executor_leaf.py`, `form/repl.py`
  (+ 16 test files). The 2026-11-12 estimate was "~10 internal
  autonomous loops"; the measured surface is these 14 — the
  migration policy half of Q-GS.1 prices against this list.

**Uni recommendation:** rule the family as one bundle (the
questions interlock: .1/.2/.3 fix the resolver's shape, .5/.11
its edge law, .6 its sandbox contract). On Q-GS.1 itself Uni
recommends (a) refuse-with-guidance for the interactive door
with per-caller deliberate ALL for the 14 production callers
migrated explicitly — the doctrine's own "GROW works only
with SELECT" (Ace, 2026-11-12) points there; the final call
is the Director's, with Q-ACE-GS.2 as Ace's surface check.

**Discharge path + cost:** Director rulings on .1–.11 (one
bundle sitting) + Ace's two answers at his convenience
(non-blocking). The build that follows is Part II's; nothing
in this PR builds it.

---

## PACKET 3B — Q-U.2/.3/.4/.5: the GS-4 repair split (Part I row #185 remainder)

Row #185's retained remainder, per the Director's Q-U rulings:
dock-landing circuit AUTHORIZED as a bounded safety circuit
(Q-U.2); confirm-placement inheritance QUEUED (Q-U.3);
auto-confirm sweep treatment QUEUED (Q-U.5); manual-confirm
cross-wall semantics HELD pending Ace's sovereignty ruling
(Q-U.4). (Q-U.1, the denominator disclosure, is discharged —
row #185 itself carries it; the 181→182 move is recorded
history.)

**What this PR's probes established at af2519b6
(PART6_UNKNOWNS_PROBE §QU, GS-4 field, PUBLIC_ENTRY_PATH):**

- **Provenance:** commit `60f1516` (2026-11-13) — "Confirm-
  placement circuit: Q-U.3 + Q-U.4 + Q-U.5 + AUTO => SANDBOX
  FIRST (Ace build-all order 2026-11-13)" — built all three
  queued items, and the build carries its own registered
  suite (`form/confirm_placement_test.py`, in the regress
  LIST). The register row was never reconciled to it.
- **Q-U.3 (confirm-placement inheritance) — behavior
  verified:** confirming a proposal whose parents share one
  wall, with no placement named, lands the offspring INSIDE
  that wall — receipt `placement.mode = "inherited_wall"`,
  and the offspring is added to the box's member list. The
  row's recorded defect ("placed UNBOXED and NOT added to
  box membership") **does not reproduce at af2519b6**.
- **Q-U.4 (manual-confirm cross-wall) — mechanism built,
  semantics awaiting Ace:** confirming a mixed-wall proposal
  with no placement named REFUSES with
  `placement_choice_required`; with `_placement="outside"` it
  confirms as `manual_choice`. This is the FI-011 placement
  law's shape (ask each time; the choice on the receipt).
- **Q-U.5 (auto-confirm sweep) — treatment built:** with the
  sweep opted in, same-wall and unboxed proposals confirm
  (6 confirmed on the probe field, boxed offspring landing
  inside the wall by inheritance); the 4 mixed-wall proposals
  are SKIPPED as non-eligible with a bounded receipt
  (`skipped_noneligible` + ids) and stay PENDING — the sweep
  never places a mixed-wall offspring at all, so the
  sandbox-first auto default never fires for mixed-wall.

**What genuinely remains open:**
1. **Q-U.4 — Ace sovereignty ruling (NEEDS_OVERSEER):** is
   the shipped semantics his intent — manual mixed-wall asks
   every time; the auto sweep DECLINES mixed-wall (skip +
   receipt) rather than placing sandbox-first? The build
   exists either way; the ruling ratifies or redirects the
   defaults. This is the one question in the family only Ace
   can answer.
2. **Credit/closure reconciliation for row #185's
   remainder** (Director + Keeper): given the build (60f1516)
   + this re-verification, what remains of the remainder
   beyond Q-U.2? Uni's reading: Q-U.3/.5 close on this
   evidence; Q-U.4 closes on Ace's ratification.
3. **Q-U.2 (dock-landing circuit)** — authorized, unbuilt;
   it is Part I's build item, unchanged by this packet.

**Discharge path + cost:** Ace's ratification (one answer);
Director/Keeper reconciliation act on row #185 citing this
packet + 60f1516. No build is requested in this Part.

---

## PACKET 4 — Q-FI011.1/.2/.4: Psalm workflow Nursery gates

Source of record: FI-011 development record
(`FI011_PSALM_WORKFLOW_NURSERY_GATES_2026-11-15.md` §"Open
questions for the authorities"). FI-011 = Ace's intake:
user-authored gates + Psalm-authored workflows over the
Nursery, fenced by the placement law and the confirmation
doctrine (nothing confirms itself; a docked organizer only
ever proposes PENDING). **Owners:** Director (.1, .2),
Keeper (.4). Q-FI011.3 (Ace: gate placement default) is
**ANSWERED** — sandbox-first, per the FI-011 record; it is
not re-asked. **Unblocks:** the FI-011 build waves W1–W4
(Part I territory); .1/.2 rulings precede ANY FI-011 build.

**Questions (exact):**

- **Q-FI011.1 (Director):** "Is a user-set standing gate a
  'human confirmation' within C5.Door's meaning, and does the
  PENDING-only doctrine admit the gate-matched refinement (an
  item matching a user's own standing gate may confirm
  without a per-item act, while everything unmatched stays
  PENDING)?"
- **Q-FI011.2 (Director):** "The ungateable category list
  under hard law — the development record proposes hard-safety
  / eligibility categories and anything touching another
  actor's state; the authorities name the list."
- **Q-FI011.4 (Keeper):** "W4 adversarial scope — which
  attack classes the hardening wave must cover: gate-widening
  attempts, origin spoofing, placement escapes, receipt
  completeness, held-out probes."

**Evidence:**
- The design is fully specified in the development record:
  W1 GATES (gate store + editor semantics + strict matcher +
  receipts + ungateable categories + kill switch; failing-
  first: an unmatched item stays PENDING; a gate set by any
  non-user caller is impossible — caller-trace proof), W2
  WORKFLOWS (Psalm Matrix stage; PENDING proposals only),
  W3 HAND-IN-HAND (gates evaluated at landing; placement law
  binding), W4 HARDENING (the adversarial pass Q-FI011.4
  scopes).
- The doctrine fences are already law and are NOT part of
  the questions: hard eligibility/safety laws precede gates;
  confirmation remains Ace's sovereign act except as .1
  rules; the placement law (Packet 3B) binds workflow output
  identically to manual output.

**Uni recommendation:** on .1 — the refinement is sound ONLY
in its narrow form: a gate is Ace's own standing instruction,
so a gate-matched confirmation is a confirmation BY Ace's
prior act, never by the system; anything unmatched, widened,
or ambiguous stays PENDING, and the receipt must name the
gate that fired. On .2 — the proposed list (hard-safety /
eligibility categories; another actor's state) is the
minimum; the Director names the final list. Both are the
Director's calls; Uni builds to the ruling.

**Discharge path + cost:** Director rulings on .1/.2 (one
sitting); Keeper's W4 scope list (one pass). No probe can
narrow these — they are doctrine, not behavior. The FI-011
build waves follow in Part I.

---

## PACKET 5 — Q-FI012.1–.10: elastic intake

Source of record: FI-012 development record
(`FI012_ELASTIC_INTAKE_DEVELOPMENT_2026-11-16.md` §"Open
questions"). FI-012 = the Elastic Intake Doctrine (Ace,
2026-11-16): DellMatrix must accept information of any size;
internal bounds are growth points; honest limits live only
at external consumers (windowing/chunking). The record's
census (M-27…M-36) found the bounded sites; waves W1–W5
build the growth mechanisms. **Owners:** Director
(.1/.2/.4/.5/.6/.7/.9), Keeper (.10), Uni (.8 — DISCHARGED
below). Q-FI012.3 (Ace: soft alert threshold) is treated as
answered/excluded per the program map and is not re-asked.
**Unblocks:** FI-012 waves W1–W5 (Part I builds).

**Questions (exact, from the development record):**

- **Q-FI012.1 (Director):** the placement question — which
  home/wave order the growth mechanisms take (the record's
  W1–W5 sequencing vs another placement).
- **Q-FI012.2 (Director):** growth step geometry — how a
  bounded site grows on demand (doubling vs additive steps
  vs unbounded-with-receipt), per site class.
- **Q-FI012.4 (Director):** counts vs sizes — whether the
  M-27-class bounds are governed as item counts, byte sizes,
  or both; and the MAX_PARENTS question it carries.
- **Q-FI012.5 (Director):** the snapshot windowing contract —
  how an oversized snapshot is windowed/chunked at the
  external consumer rather than refused at intake.
- **Q-FI012.6 (Director):** the A4 done-state — what
  "done" means for the A4 decomposition bound under the
  doctrine.
- **Q-FI012.7 (Director):** the exchange trust boundary —
  which exchange surfaces may carry oversized payloads and
  under what trust rules.
- **Q-FI012.9 (Director):** capacity authority — who may
  raise a growth bound in production (standing rule vs
  per-incident ruling).
- **Q-FI012.10 (Keeper):** the adversarial matrix — which
  hostile-input classes the waves must prove against
  (oversize, malformed, boundary-exact, replay).

**Q-FI012.8 (Uni, owed) — DISCHARGED BY THIS PR.**
The question: the idea_create parse-path census (M-34) —
where the census-era caps live at current main and how they
fail. Evidence (FI012_Q8_CENSUS 8/8, at af2519b6):

- The caps live at **`form/idea_create.py`
  `parse_create_line`**, the single parse door (sole
  production caller: `form/dell_matrix/needs.py`):
  `label[:80]`, `detail[:2000]`, `goals[:12]`,
  `words[:500]` — all at census values.
- **All four truncate SILENTLY** — the result dict carries
  no truncation flag, count, or receipt. The caller's only
  signal is the existing ok/error channel, which reports
  success.
- **The words cap is effectively 120, not 500:** words are
  derived from `detail[:120]` first, so the `[:500]` slice
  can never see more than 120 characters. The census's 500
  figure is unreachable code as wired.
- **The store layer already behaves honestly:** the same
  150-character label the parser cuts at 80 is stored WHOLE
  by `Nursery.add` (its bound is `MAX_LABEL_CHARS = 200`,
  `form/dell_matrix/nursery.py`, enforced by a typed
  refusal, not a cut). The dishonesty is parse-layer only.

So W4 (the parse wave) is scoped exactly: one door, four
silent cuts, one unreachable cap — replace silent truncation
with the doctrine's growth/refusal-with-receipt behavior at
`parse_create_line`, with the store layer as the honesty
model. No Director question remains inside .8.

**Discharge path + cost (family):** Director rulings on the
seven questions (one bundle sitting) + Keeper's adversarial
matrix. .8 cost was one probe suite — paid in this PR.

---

## PACKET 6 — Q-FI016.1: database/SQL-style operations on ideas (Ace)

**Question (Ace's own, exact):** "can DellMatrix / Mandell
handle database- and SQL-style operations on ideas — set
operations, indexed query, relational joins over idea data?"
Status before this probe: **UNKNOWN**. Ace's method ruling
governs the discharge: it "has to be calculated and proven,
not just based on my opinion."

**Owner:** Ace (NEEDS_OVERSEER — the classification and any
build mandate are his). **Unblocks:** nothing is blocked on
it; it decides whether a future query/index build exists.

**The measured answer (FI016_CAPABILITY 12/12, at af2519b6):**

Functional analogues, against the real store machinery
(`Nursery.query` — the C5R.2 SEE service — plus `fetch_many`):

| SQL analogue | Native mechanism | Measured behavior |
|---|---|---|
| PK lookup | `fetch_many(ids)` | exact; missing ids reported by name |
| WHERE (term) | `query(mode="search", term=...)` | exact on discriminating terms; **lineage-aware** — a child matches its parent's terms (search corpus includes lineage) |
| WHERE (field) | `query(mode="browse", topic=...)` | exact set |
| GROUP BY | `query(group_by="topic")` | partitions with per-group counts; membership/distinct totals consistent |
| LIMIT/OFFSET | cursor pagination | exact-once walk; cursor binds owner/mode/filter/sort/page-size (mismatch refuses `CURSOR_FILTER_MISMATCH`) |
| Set operations | composition at the door | intersection/difference of two query result sets equal fixture truth — there is **no set-op door**; sets compose in the caller |
| JOIN | two-step composition | children-of-X by scan + binding; parents resolved by `fetch_many` — there is **no join primitive** in the store API (mechanical census of the 12 public Nursery methods) |

Scale calculation (temp stores; save/load are whole-file
JSON operations):

| N | file | save | load | term search | PK ×50 |
|---|---|---|---|---|---|
| 200 | 154 KB | 8 ms | 5 ms | 2.5 ms | 0.9 ms |
| 1,000 | 771 KB | 50 ms | 29 ms | 19.5 ms | 2.3 ms |
| 4,000 | 2.92 MB | 191 ms | 100 ms | 230 ms | 5.7 ms |

The write path is the measured constraint: `add()` persists
by rewriting the whole file per add, so a door-realistic
build of 1,000 proposals took **37.98 s** (vs 1.33 s at 200)
— quadratic write behavior. Read-side operations scale
near-linearly and stay sub-second at 4,000 records.

**Uni's derived reading (for Ace's classification, not a
substitute for it):** DellMatrix today answers SQL-style
READ questions over idea data with native machinery —
filtered, grouped, paginated query and exact PK lookup are
real services, not simulations. Set operations and joins
exist only as caller-side compositions over those services.
There is no index, no query planner, and no incremental
write; the store is a whole-file document store whose write
cost grows quadratically. Whether that constitutes
"handling database-style operations" for Ace's purposes —
and whether an index/incremental-write build is warranted —
is Ace's call on this evidence.

**Discharge path + cost:** Ace's classification (one
answer). Any build he mandates is a new circuit, scoped
from the cost table above; none is proposed in this PR.

---

## PACKET 7 — Q-DD42.2: While/Until refusal surfaces (Director)

**Question (exact, DIRECTOR_REPORT_DD42_PREDICATE_INFIX_
2026-11-10):** "While/Until boundary — add refusal surfaces
there in a follow-up circuit, or accept the fail-closed bool
behavior as the standing contract?"

**Owner:** Director. **Unblocks:** Part II row #12's
remainder (the DD-42 circuit's retained question).

**Current-main behavior (this PR, PART6_UNKNOWNS_PROBE §42,
real seed execution at af2519b6):**

- **While + infix condition** (`65[While]:: level lt 99`,
  level = 5, so the infix reading would be TRUE): the
  condition is **silently read as already-false** — zero
  iterations, the head atom reports **ok=True**, and NOTHING
  is surfaced: no error, no refusal receipt, no marker that
  the condition never parsed. The "fail-closed bool"
  framing in the question understates this case: the
  failure is silent AND the head claims success.
- **Until + infix condition** (`64[Until]:: level gt 99`):
  refuses `bound_unspecified` (the DD-44 bound law) — a
  refusal fires, but it names the missing bound, never the
  unparseable condition that actually caused it. Cause
  misattributed.
- **Control (While + prefix condition):** refuses honestly
  with `bound_unspecified` and a "nothing ran" receipt —
  the DD-44 contract is intact where the condition parses.

**Options:** (a) Follow-up circuit: condition-parse honesty
at the While/Until boundary — an unparseable condition
refuses BY NAME (condition-side), at both verbs, before any
bound interaction. (b) Accept current behavior as the
standing contract (with the While case's silent-true head
now on record as the accepted behavior).

**Uni recommendation:** (a). The DD-42/DD-44 arc has
consistently chosen named refusals over silent coercion;
the While case is the one place in the measured surface
where an unexecuted semantic reports ok=True, which the
program's atom-honesty law forbids inferring.

**Discharge path + cost:** Director ruling. Under (a): one
bounded Part II circuit (failing-first suite exists in
embryo — §42 of this PR's probe flips from pin to spec).
Under (b): records only.

---

## PACKET 8 — Q-DD18.2: Pulse refusal chain policy (Director, dormant)

**Question (exact, DIRECTOR_REPORT_DD18_PULSE_RECEIPT_
2026-11-10):** "should a refused Pulse inside a chain also
STOP the chain (policy), or continue with the atom marked
not-ok (current inherited behavior, DD-19 receipts)? Uni's
reading: continue + honest atom receipt; chain policy is a
separate decision."

**Owner:** Director. Dormant — no build waits on it; it is
retained so the policy is decided before a surface depends
on it (Part I H-4 cluster neighbor).

**Current-main behavior (this PR, PART6_UNKNOWNS_PROBE §18,
at af2519b6):** chain `25[Pulse] > 55[Set]:: after_pulse=yes
> 61[Join]` with enhance OFF — the chain **CONTINUES**: the
Set executes, Join runs ok; the Pulse atom carries ok=False
with its receipt ("Pulse NOT sent (enhance OFF)."); the
chain result is ok=False. This matches the program law
(AGENTS.md): an atom's execution result is NOT a chain
continuation policy — the two are reported separately, and
both are reported honestly here.

**Options:** (a) Ratify current behavior as the standing
policy (continue + honest atom receipt; chain ok=False).
(b) Rule stop-on-refused-Pulse as chain policy — a behavior
change requiring its own circuit and a DD-19 receipt review.

**Uni recommendation:** (a), per the original reading: the
atom receipt already tells the truth; making one verb's
refusal a chain-halting policy by default would smuggle a
continuation rule into an atom contract.

**Discharge path + cost:** Director ruling; records only
under (a).

---

## PACKET 9 — R21: the DD-54 snapshot-cap question (Director)

**Question (exact, LIMITS_RECONCILIATION_MATRIX_R2_R26_
2026-11-18):** whether DD-54's snapshot-cap retirement
remains owed after PR #481's Q-LC.1 build discharged it for
the action stack, or is discharged — a plan-reading question
for the Director. (Part I row #135's retained remainder
carries it.)

**Owner:** Director. **Unblocks:** row #135 remainder
closure in Part I.

**Evidence:**
- The matrix classifies both caps LEGITIMATE-GUARD:
  `SNAPSHOTS_CAP = 64` and `TRACES_CAP = 512`
  (`form/mandell/core_ii_exec.py`), evictions COUNTED at
  their sites (`dropped_total`), session-only scope
  documented as design.
- **Behavior re-verified (this PR, PART6_UNKNOWNS_PROBE
  §R21):** 65 snapshot appends → 64 kept, `dropped_total`
  1; 513 trace appends → 512 kept, `dropped_total` 1. The
  caps behave exactly as the matrix describes at af2519b6.
- The question is purely whether the Q-LC.1 build (PR #481,
  session-local action stack) retired the DD-54 obligation
  for this surface too, or whether DD-54's retirement
  language reaches the Core II exec caps independently.
  That is a reading of two Director-era records against
  each other — authority work, not probe work.

**Discharge path + cost:** Director ruling (one reading).
No probe can narrow it further; the behavior evidence above
is complete.

---

## PACKET 10 — DAF-09: certification evidence (Director) — WITHHELD

**Status: whole-program certification remains WITHHELD.
This packet does NOT resolve DAF-09, and no local evidence
in this PR is offered toward resolving it.** (Standing law
for this item: Uni once prematurely called DAF-09
"resolved"; the correction is permanent — local runs cannot
discharge it.)

**What is certified and what is not (record):**
- Director Mode D ruling (2026-10-31): CERTIFIED WITH NOTED
  EXCEPTIONS, narrowed to Linux ordinary-descendant cleanup,
  the timeout verdict, and bystander survival. Session-escape
  and cancellation were NOT certified in that ruling.
- Addendum evidence (PR #170, merged f1c02051; candidate
  2aa1a30): witnessed-union kill in `form/regress.py`;
  suite `form/daf09_timeout_tree_test.py` 16/16 locally,
  mutant-verified.
- ESRCH follow-up (PR #210, merged 4ba052c): pidfd_open
  ESRCH → "refused" classification contract; suite 23/23
  locally. Cancellation is CERTIFIED per the ESRCH report
  and is not re-opened here.
- **The open discrepancy (§31.3, UNRESOLVED):** the
  Director's environment produced **19/22** on the timeout-
  tree suite; Uni's local runs pass fully. Local evidence
  cannot explain the difference, and no amount of additional
  local passing changes that.

**The authority evidence required (exact):** an
instrumented-driver rerun **in the Director's environment**
— Q1 of DIRECTOR_REPORT_DAF09_INSTRUMENTED_
INVESTIGATION.md — capturing which of the three failing
checks diverges there and why. Until that evidence exists
and the Director rules on it, DAF-09 stays open and
whole-program certification stays WITHHELD; Part III row
#21, Part 0 row #116, and Part VII row #112's certification
elements remain gated on it. Nothing in Parts 0–VII may
cite this packet as DAF-09 progress beyond "evidence
requirement restated."

**Owner:** Director (environment + ruling). **Cost:** one
instrumented rerun in the Director's environment + his
disposition. Uni-side cost is zero — by design; Uni cannot
supply this evidence.

---

## EDITION 1 CLOSURE-EVIDENCE INDEX (UU / DC families)

Edition 1 (`director-reports/GRAND_PLAN_DIRECTOR_EDITION1_
2026-11-18/03_DECISION_AND_UNKNOWN_REGISTER.md`) recorded
UU-1…UU-15 with Director design decisions and DC-1…DC-11
dispositions. Per the program map, where Edition 1 already
decided, Part VI carries closure evidence rather than
re-asking. Index (statuses as recorded in Edition 1; this
packet adds no new evidence to items owned by other Parts):

- **DC-1 / DC-6 / DC-7 / DC-11:** RESOLVED in Edition 1 —
  closed; no Part VI action.
- **DC-2 / DC-3:** RESEARCH class — evidence owed by their
  owning Parts.
- **DC-4 / DC-5:** EVIDENCE class — same.
- **DC-8 / DC-9 / DC-10:** ACE items — carried on the
  NEEDS_OVERSEER list with the PR body; non-blocking.
- **UU-1…UU-15:** Director design decisions recorded;
  closure evidence rides the owning Parts' PRs. (UU-14's
  "39/182" numerator is historical — the board reads 40/182
  at this PR's base.)

---

## PROPOSED REGISTER FLIPS (proposed only — effective as ruled)

| Row | Flip | Condition |
|---|---|---|
| #119 | OPEN → COMPLETE | Director confirms the 2026-11-06 Q-35.1 manual-only ruling stands (Packet 1, option a) |
| #175 | OPEN → COMPLETE | Director rules Q-SNAP.3 finding-only or decline, or the authorized hardening circuit lands (Packet 2) |
| #185 (Part I row; noted here) | remainder reconciliation | Director + Keeper reconciliation on Packet 3B evidence + Ace's Q-U.4 ratification |

No other Part VI item proposes a flip: the Q-GS / Q-FI011 /
Q-FI012 / Q-DD families gate BUILDS in other Parts, and
Q-FI016.1 / DAF-09 close only on their owners' acts above.

## DISCHARGE COST SUMMARY

| Item | Discharge | Cost |
|---|---|---|
| #119 / Q-35.1 | Director confirm-or-reopen | one ruling |
| #175 / Q-SNAP.3 | Director ruling a/b/c | one ruling (+ circuit under a) |
| Q-GS.1–.11 | Director bundle ruling | one sitting |
| Q-ACE-GS.1/.2 | Ace answers | non-blocking, at his convenience |
| Q-U.4 | Ace ratification | one answer |
| Q-U.3/.5 credit | Director + Keeper reconciliation | one act on this evidence |
| Q-FI011.1/.2 | Director rulings | one sitting |
| Q-FI011.4 | Keeper W4 scope | one pass |
| Q-FI012.1/.2/.4–.7/.9 | Director bundle ruling | one sitting |
| Q-FI012.8 | — | **DISCHARGED in this PR** (probe suite) |
| Q-FI012.10 | Keeper adversarial matrix | one pass |
| Q-FI016.1 | Ace classification | one answer on measured evidence |
| Q-DD42.2 | Director ruling | one ruling (+ circuit under a) |
| Q-DD18.2 | Director ruling | one ruling |
| R21 / DD-54 | Director reading | one ruling |
| DAF-09 | Director-environment instrumented rerun + ruling | Director-side only; certification WITHHELD until then |

## THE ASK (mirrors the PR body)

1. **PLAN-CONFIRM (Director + Keeper)** on the Part VI
   packet set as presented — one bundle.
2. **Per-family rulings** as tabled above (Director: #119,
   #175, Q-GS, Q-FI011.1/.2, Q-FI012 Director items,
   Q-DD42.2, Q-DD18.2, R21; Keeper: Q-FI011.4, Q-FI012.10,
   #185 reconciliation with the Director).
3. **NEEDS_OVERSEER (Ace, non-blocking):** Q-U.4
   ratification; Q-ACE-GS.1 ("what is a project?");
   Q-ACE-GS.2 (bare-"grow" surface); Q-FI016.1
   classification; Edition 1 DC-8/DC-9/DC-10.
4. **RECORDS-CONFIRM at exact head** when the plan is
   confirmed, so the code stage (the builds these packets
   gate, in their owning Parts) can proceed under §46.
