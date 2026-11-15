> **Deliverable 5 of SYSTEM-001 (DIR-DM-SYSTEM-001) — gap & conflict ledger from the self-mirror sweep at pin 62bdcbc.**

# SYSTEM-001 — LANE 3: GAP & CONFLICT SWEEP

**Directive:** DIR-DM-SYSTEM-001 (Director, MODE A), initial circuit
SYSTEM-001. **Lane:** 3 of the self-mirror — duplicates, disconnected
mechanisms, orphans, contradictions, reuse opportunities, decision
candidates.
**Sources:** the Unified Grand Plan (esp. Part 0, Part VI UU-1..UU-15);
`docs/DELLMATRIX_EQUATION_LEDGER.md` in the SYSTEM-001 clone (§7, §8,
§10, §11 and the DISCONNECTED / CONTRADICTORY / DUPLICATE entries);
the Self-Mirror Reconciliation (2026-11-14); refinement Batches A–E;
spot greps against the clone at `~/workspace/sys001_clone` (read-only;
clone HEAD = current main at lane start).
**Method note (instrument honesty):** the lane's first orphan scan was
run with a broken grep (basic-regex alternation) and returned garbage
(nearly every module "unimported"). It was **discarded in full** and
re-run as a Python regex scan over every `.py` file under `form/`.
Only the second scan's results appear below. All "no callers" claims
state their grep scope; a failed or out-of-scope search is reported
as *unproven*, never as *absent*.

## Summary counts

| Section | Count | Notes |
|---|---|---|
| 1. Duplicates | 5 live + 1 checked-and-clear | 1 already deduped in code (ledger stale) |
| 2. Disconnected mechanisms | 8 | 2 ledger-carried, 6 verified/extended here |
| 3. Orphans | 13 no-static-importer candidates + 7 test/proof-only surfaces | lawful stand-downs: 3 classes, distinguished |
| 4. Contradictions | 10 | highest severity: C-3, C-4, C-5 |
| 5. Reuse opportunities | 8 | each names the existing mechanism |
| 6. Decision candidates | 11 | Director 7 · Ace 2 · joint 2 |

---

## 1. DUPLICATES — two mechanisms/stores/registers doing one job

### D-1. Vesica overlap core, implemented twice live — **DEDUP EXECUTED IN CODE; ledger stale**
- **Parties:** `form/dell_matrix/sacred_geometry.py::vesica`
  (EQ-GEO-001, canonical) and `form/dell_matrix/verita.py::vesica_strength`
  (EQ-VER-001). A third copy exists in legacy `src/core/dual_lattice.js`
  (frozen 2026-08-01 — no action, HISTORICAL).
- **Evidence:** ledger §7 R4-A1 classifies EQ-VER-001 `DUPLICATE` and
  records the delegation as a required source change "**NOT performed**."
  The clone contradicts the ledger's present tense: `verita.py:56`
  `vesica_strength` is now a documented thin compatibility wrapper —
  *"GDP-001 Phase 3 (3.4.1): … The ONE canonical overlap implementation
  is `form.dell_matrix.sacred_geometry.vesica` … nothing is
  reimplemented here"* — and `form/mandell/p3_r34_geometry_proof.py`
  proves the delegation.
- **Canonical:** `sacred_geometry.vesica` (already, in code).
- **Resolution class:** DEDUP — *done in code*; what remains is a
  ledger reclassification (see C-3, DC-1).

### D-2. Parallel 0..1 overlap-like authorities — **RECONCILE (partially discharged in code)**
- **Parties (ledger form, R4-A5):** `ringed_growth._harmonic()`
  (EQ-RES-001), pair verita (EQ-VER-003), sacred verita (EQ-GEO-002) —
  "shared callers (brain, auto_growth) but no documented relationship…
  Do NOT average them into one number."
- **Evidence the picture moved:** current code carries two more
  parties and an explicit separation architecture the ledger predates:
  `form/dell_matrix/harmony.py::harmony_score` (set-level coherence;
  its docstring separates it from `resonance.pulse`, `harmonize_pair`,
  `_affinity`, and verita pair coherence, "proven, not asserted, in
  `form/mandell/p3_r32_harmony_proof.py`") and
  `form/dell_matrix/graph_harmony.py::graph_coherence`.
  `ringed_growth.py` now runs them as a layered pipeline: `_affinity`
  is the canonical gate (graph_harmony.py:98), `harmony_score` is
  imported at ringed_growth.py:32 as "canonical harmony authority"
  and called at :640 (P3 R3.6 wiring); nursery.py:101-102,198
  documents the same wiring from the consumer side.
- **Canonical:** no single number — by design (firewall F5). The
  pipeline's division of labour (gate → graph coherence → set
  harmony) is the de-facto reconciliation.
- **Resolution class:** RECONCILE — the which-quantity-gates-what
  contract exists in module docstrings and proofs; it has not been
  written back into the ledger or one contract register (see DC-1).

### D-3. MWL "G-" numbers vs §4 register "G-" numbers — **RESOLVED-BY-RULING**
- **Parties:** Master Work List G-rows and Grand Plan §4 GP-G01..28 —
  different registers sharing one prefix; all twelve overlapping
  numbers collide (Batch A header note; Batch E §4; miniature case:
  MWL #15's own register ID is G-04 while its subject is GP-G03's
  defect, Batch E:157).
- **Resolution:** the Unified Plan's namespace ruling (§4 = GP-G,
  MWL = MWL-#, §7 provisional = G-29/30/31 in the Far register).
  Historical records are unchanged; the collision survives inside
  them and must be read under the ruling. **Class: NAMESPACE —
  RESOLVED-BY-RULING (Ace's unification, 2026-11-14).**

### D-4. Duplicates inside the Master Work List itself — **DEDUP (counting)**
- **Parties (Batch E §4, proven from the rows' own text):**
  MWL-#178 (Embed provider, OPEN) ≡ #153 (COMPLETE — #178's text says
  "implementation = item 153"); #177 (FRESH aging) → part of #140;
  #179 (Distill mode) → part of #139; #171 is an H-track rollup
  restating Block F rows (its three orphaned extras need re-homing,
  UU-15).
- **Resolution class:** DEDUP — already deducted in the unified
  recount (T = 224); the MWL file itself is a historical render and
  is not edited.

### D-5. Duplicate scoreboard surfaces — **RECONCILE**
- **Parties:** the MWL render (2026-11-10, 182 rows / 35 verified
  COMPLETE), the main-line board figure (39/182, post-render
  credits), Manifest Sitting #001's record (baseline 36/179), and
  now the Unified Plan Part 0 (T = 224).
- **Canonical:** the Unified Plan is the scoreboard of record by
  Ace's unification order; the Nov 26 sitting renders fresh and
  supersedes all four surfaces' completes numbers.
- **Resolution class:** RECONCILE — one scoreboard going forward;
  the completes discrepancy itself is C-4.

### D-6. Checked and CLEAR: token-overlap (Jaccard) is NOT duplicated
- `grep -rn 'def .*jaccard' form/` returns exactly one definition,
  `form/dell_matrix/text_metrics.py:54`; 17 further files *consume*
  it (verita.py's header: "Canonical tokenization substrate:
  text_metrics (P3/TD-6)"). Recorded so the sweep's negative result
  is on file: this is the dedup pattern done right (see R-1).

---

## 2. DISCONNECTED mechanisms — computed-but-unconsumed / named-but-uncomputed

### X-1. `resonance.py` logs "vesica", computes no geometry — ledger EQ-RES-003
- **Evidence:** ledger §4: the log string `"vesica {a}⊗{b} → {mid}"`
  (resonance.py:140) is `DISCONNECTED` — `harmonize_pair` accumulates
  scores/tags only. Lane grep refines the scope: the *module* is not
  orphaned — `enhance_gate.py:106` calls `harmonize_pair`, and
  `form/dell_matrix/__init__.py:7` exports it. The disconnect is
  exactly the geometric claim in the token, and the misdirection
  that the file named `resonance.py` is not where resonance is
  computed (the real computation is `ringed_growth._affinity`,
  ledger §4 headnote).
- **Class:** named-not-computed (the token). Ledger action R4-A4
  (rename-or-wire) still open → DC-6.

### X-2. Gravity as pull — ledger EQ-GRV-001
- **Evidence:** `forces.py:267` `set_wells_from_scores` runs on
  product paths (forces.py:429; `form/open.py:928`; `form/repl.py:2162`),
  wells are reported (forces.py:447,475) and persisted/restored
  (forces.py:557-572). Lane grep over forces.py shows `wells` only
  assigned, reported, saved, restored — **no consumer applies mass
  to move anything**; the class text ("Heavy ideas pull others
  toward them") describes behaviour no equation implements (ledger
  §5 honesty note; `ForceMatrix.evolve` is uniform decay, not a
  pull law).
- **Class:** computed-but-unconsumed (the pull itself:
  named-not-computed). DISCONNECTED as mechanism stands.

### X-3. The nerve — no derivation, no consumer, no API
- **Evidence:** unified plan UU-4 (the taxonomy's one genuinely
  name-only member; admission conditions stated — proven consumer +
  admitted derivation — neither exists). In-code corroboration,
  `form/dell_matrix/verita.py` module docstring: *"no transformation
  API exists anywhere in form/ (grep for cech|nerve|power
  diagram|alpha filtration across form/ = empty…)"*. Lane grep for
  `nerve` over `form/**/*.py` returns only sacred_geometry.py,
  verita.py, and a proof file — mentions, not a mechanism.
- **Class:** named-not-computed, named-not-consumed. The measured
  nerve *data* (sandbox Part I: thick nerve, order-4 ceiling) waits
  on EXT-GEO-002 (Čech), a RECOVERY_CANDIDATE — see R-6/DC-3 family.

### X-4. Known/unknown "equations" — ledger EQ-KNG-001, UNKNOWN
- **Evidence:** ledger §6: no equation recovered; prose only in
  `form/dell_matrix/decision_shells.py:8-9`. The Overseer's
  occupied/void/boundary ↔ KNOWN/UNKNOWN/POTENTIAL/GROWTH mapping is
  **unconfirmed by repository evidence** (ledger, citing the
  recovery study). R4-A8: recovery target — do not invent.
- **Class:** named-not-computed. (UU-7's negative-space semantics
  is the same hole seen from the product side.)

### X-5. Lattice notes and THE CHORD — assigned, unconsumed
- **Evidence:** Batch B (FAR-20 entry): "the lattice notes and THE
  CHORD are assigned but unconsumed — FAR-20 names their first
  consumer." `HarmonicLattice.note_at` assigns notes from addresses
  (fifth +7, major third +4 semitones); no product path reads them
  as data. THE CHORD is adopted as a *derived reading* (Ace,
  2026-11-13) — a witness, deliberately not a mechanism; the
  disconnect is recorded so no future circuit mistakes the reading
  for an input.
- **Class:** computed-but-unconsumed (notes); by-design witness
  (THE CHORD — lawful, receipt = the adoption record).

### X-6. `verita_between_nodes` — live mechanism, vacuous on real content
- **Evidence:** Self-Mirror reconciliation §2/§3 and ledger §3
  header (MPC-012 Agent C): all real user ideas sit at (0,0), so
  live overlap is computed over stacked positions. In-code
  corroboration, verita.py docstring: *"Unit.x/Unit.y default to
  0.0 and Plane.place() defaults x=0.0, y=0.0… verita_between_nodes()
  skips pairs with dist < 0.01, so default-placed ideas yield NO
  vesica edges at all."* Unified plan UU-6/U-6 (positions leaving
  (0,0)) gates it.
- **Class:** computed-but-effectively-unconsumed — the geometric
  relationship layer produces no edges on the default path. This is
  the Director's §4 slice/projection boundary in live form.

### X-7. DuoBeta `suggest_preferred` — production-bypassed selector
- **Evidence:** defined `form/mandell/duobeta_learn.py:352`. Lane
  grep over `form/`: every caller is a test (`dbel_i_test.py:320,
  323,327,390,435`) or a doc reference; `asi_i_test.py:221` states
  the production path explicitly: *"Execution after learning →
  Outcome V1 (production path, not suggest_preferred)"*.
- **Class:** computed-but-unconsumed-by-production — a dead surface
  the Completeness Law exhibit list already names; it survives as a
  test fixture for the learning contract, which is a lawful role
  only if recorded as one (see §3 stand-down note).

### X-8. Space (GP-G01) — "an orphan with a famous name"
- **Evidence:** Batch A G-01, on the 05859c0 inventory: Space
  "states 'room to grow' / does nothing at all." A named force with
  a stated meaning and no function. Current-main state is subject
  to UU-1 (stale inventory) — the X11 census re-verifies.
- **Class:** named-not-computed; disposition (build the quantity or
  retire with receipt) is DC-10.

---

## 3. ORPHANS — Completeness Law sweep

**Law:** a component is PARTICIPATING or STOOD DOWN BY DECISION WITH
A RECEIPT; silent absence (no caller, no map, no receipt trail, no
recorded reason) is NEGLECT.
**Instrument:** Python regex scan for static import edges
(`from .M import`, `from form.dell_matrix.M import`,
`import form.dell_matrix.M`, package-level `from form.dell_matrix
import … M`, `import_module("…M")`) across every `.py` under
`form/`. **Scope limit, stated plainly:** static imports inside
`form/` only. REPL command dispatch, string-built imports, and
entry points outside `form/` can hide a caller this scan cannot
see; each candidate below is therefore an orphan *candidate* whose
final classification belongs to the X11 census's runtime
reachability pass (UU-1's discharge). The one repo-wide check
(O-1) used a whole-clone `*.py` grep.

### O-1. `spatial_audio.py` — NEGLECT (named by its future circuit)
- Whole-clone grep: `grep -rn 'spatial_audio' --include='*.py' .`
  returns **zero references outside the module itself** (position →
  pan/gain/band/ear-cue computation, built for UI/TTS/Web Audio
  consumers that do not exist). No stand-down receipt. It is a
  pre-built orphan: FAR-20 (opened §7) names it as its toehold and
  first consumer — until that circuit runs, its absence from every
  caller map is exactly the Completeness Law's defect shape.
  Reuse path: R-4.

### O-2..O-13. No static importers anywhere in `form/` — ORPHAN-CANDIDATES
`allwhere` · `dynamic_view_switch` · `function_150_loop` ·
`incorporation_audit` · `live_host` · `neuroevo` · `organ_atlas` ·
`perspective_runtime_truth_checks` · `procedural_assets` ·
`program_evolve_150_loop` · `sync_ux_150_loop` · `visual_terminal`.
- No caller, and (from the sources this lane read) no stand-down
  receipt for any of them. Several wear loop/150-era names
  suggesting historical experiment modules; `organ_atlas` is
  notable because other modules cite its *data* (e.g.
  harmonic_core's atlas entry) while nothing imports the atlas
  itself. **Classification: NEGLECT-candidate ×12** — each needs
  the X11 runtime check, then either wiring or a stand-down
  receipt (DC-9). Not asserted as proven-dead: the scan's scope
  limit above is the reason.

### O-14. Test/proof-only surfaces — participation by fixture only
Static importers exist but are exclusively tests/proofs:
`auto_growth` · `embed_bind` · `lineage_bind` · `page_enhance_loop` ·
`program_strength` · `verita` · `visual_evolve_loop`.
- **`verita` is the sharp case:** within `form/`, `verita.py`'s
  only static importers are `form/equation_ledger_invariants_test.py`
  and `form/mandell/p3_r34_geometry_proof.py`; `auto_growth`'s only
  importers are two tests. The ledger (§8, Verita lineage) calls
  Era-2 verita "**live on brain/auto_growth**" — that liveness is
  **unproven against current main by this grep** (dynamic dispatch
  caveat applies). Either the ledger's claim is stale (another
  C-3 instance) or a non-static path reaches it; X11 must decide
  with runtime evidence. → DC-4.
- The other five are lawful *if* their fixture role is their
  recorded role; none carries a stand-down/participation receipt
  in the sources read. Class: FIXTURE-ONLY, receipt owed.

### Lawful stand-downs (receipts exist — NOT orphans)
- **Era-1 Smith / VERITA-SMITH:** frozen as LEGACY with the §10
  firewall as its receipt; do-not-port is written law.
- **Legacy JS line** (`dual_lattice.js`, `harmonic_cube_5ring.js`):
  frozen 2026-08-01, preserved as evidence (DUAL_LATTICE.md banner;
  ledger §8).
- **`idea_grow`:** retired under SD-5 — `p3_wiring_test.py:10`
  records the retirement and the guard that replaced it. This is
  the model receipt shape the O-2..O-13 dispositions should copy.
- **THE CHORD as witness:** adopted as derived reading only
  (X-5) — a recorded decision, not an absence.

---

## 4. CONTRADICTIONS — documentary and semantic

### C-1. EQ-GEO-013 — code comment contradicts its own formula
`sacred_geometry.py` comment claims strength peaks at the classic
vesica; the formula (EQ-GEO-001) gives 0.5 at dist = R and 1.0 at
containment. Ledger: CONTRADICTORY. **Severity: LOW** (documentary;
the code is right). Path: R4-A7 correction — a
supersession-preserving draft already exists (THL-SM-01 drafts,
PR #419 package); comment now at line 157 (the ledger's :143
reference has itself drifted — see C-3).

### C-2. EQ-GEO-014 — "recursive" Flower claim contradicts the construction
`docs/DUAL_LATTICE.md` calls the Flower recursive; `flower_centers`
is a finite two-ring construction with no scaling law. Ledger:
CONTRADICTORY. **Severity: LOW.** Path: R4-A7 supersession note
(draft exists, same package as C-1).

### C-3. THE LEDGER vs CURRENT CODE — the authority record is stale ⚠
- **Parties:** `docs/DELLMATRIX_EQUATION_LEDGER.md` (Ledger V1,
  committed on branch `gdp-p0r4`, base `1c90cec`) vs the clone's
  current `form/`.
- **Evidence:** (i) R4-A1 records the vesica dedup as "NOT
  performed" — performed (D-1). (ii) R4-A5 lists the overlap
  reconciliation as future Phase-3 work — the R3.2 separation
  proof and R3.6 wiring exist in code (D-2). (iii) EQ-GEO-013's
  line citation (:143) has drifted to :157. (iv) §8's "live on
  brain/auto_growth" for VERITA-JUDGE is unproven by grep (O-14).
- **Severity: HIGH.** The ledger is the mathematical authority of
  record; a worker who trusts it re-does finished work or defends
  dead classifications — the precise waste the Director's
  efficiency rules (H) forbid. The ledger's own §12 permits the
  cure: append-only reclassification with evidence cited.
- **Resolution path:** reclassification entries for EQ-VER-001 and
  R4-A5's status, citing the code evidence (DC-1); plus a process
  ruling on ledger upkeep (DC-11). No winner was picked by this
  lane beyond what the code itself proves.

### C-4. The completes discrepancy — 35 vs 39 (UU-14)
- **Parties:** the MWL render's verified 35 COMPLETE vs main-line
  records' 39; plus the open +3 credit question (GP-G24 closed by
  filing, G-29 census closed, FAR-17 computed — do closed findings
  earn COMPLETE credit?).
- **Evidence:** Unified Plan Part 0 records both numbers with
  their provenance; Batch E §6 lists the exact ambiguities.
- **Severity: HIGH for scoring integrity** (the Nov 26 sitting
  scores against this number), LOW for engineering.
- **Resolution path:** the Nov 26 fresh render settles the count;
  the credit question is a ruling (DC-7).

### C-5. "Verita" names three mechanisms — firewall exists, surfaces lag ⚠
- **Parties:** VERITA-SMITH (era-1 match flag), VERITA-MEET
  (EQ-GEO-002 coherence-of-meet), VERITA-JUDGE (EQ-VER-003 pair
  coherence). Ledger §10 firewall F1–F5 is binding law; R4-A2
  records the owed cleanup: namespace or rename at least two of
  the three, and until then *every public surface must say which
  verita it reports*.
- **Severity: HIGH (semantic safety).** The failure mode is F3:
  an overlap number read as a truth judgment — the one confusion
  the system's epistemic doctrine exists to prevent.
- **Resolution path:** the rename/namespace scope is a Director
  decision (DC-2); surface labelling is engineering that can
  proceed under F4 once scope is set.

### C-6. "Harmonic" — the collision is larger than the ledger counted
- Ledger R4-A6 counts three: `harmonic_cube_5ring.js` (5-tier
  memory, zero math), `Form.CUBE` perception, `_harmonic()`
  (EQ-RES-001). Current code adds at least four more bearers:
  `harmonic_core.py` (long-term keys / `pulse_status`; organ
  atlas: "permanent keys soft-forget" — a memory mechanism, not
  an engine, matching the standing "harmonic_core is honestly not
  an engine" finding), `harmonic_lattice.py` (coordinate cell
  store), `harmony.py::harmony_score` (set coherence),
  `graph_harmony.py::graph_coherence`.
- **Severity: MEDIUM.** No two of these compute the same thing;
  the risk is conversational and documentary (a "harmonic" result
  cited across mechanisms), exactly R4-A6's concern, now with
  seven bearers. **Path:** the naming audit R4-A6 already orders,
  extended to the full bearer list; no semantic merge (DC-2's
  sibling — may be folded into one naming ruling).

### C-7. GP-G03 gravity wells — three-way status conflict
- **Parties:** §4 register ("saved/never restored" — on the stale
  05859c0 inventory) vs MWL #15 ("restore built via PR #317") vs
  current code (wells persisted *and* restored, forces.py:557-572;
  Batch A: main line records the repair COMPLETE) vs Batch E:157
  ("CONFLICTING SOURCES on status — mapped for counting, status
  NOT imported").
- **Severity: MEDIUM.** The code evidence favours *restored*; the
  register's claim is the stale one (UU-1's proof case). But
  "restored" in code is not "verified on the public path," and
  X-2's pull disconnect is unaffected either way.
- **Resolution path:** X11 current-main verification closes it
  with runtime evidence; no lane picks a winner from documents.

### C-8. Dell 151[Harmonic] — the language cites a Dell the registry doesn't contain
- **Evidence:** `form/mandell/seed.py:2` docstring: *"Atoms:
  08[Create] or 151[Harmonic]"*; the live registry holds 00–99
  (100 unnamed / ADDRESS_RESERVED per Batch D). Tests pin the
  honest behaviour — `core_i_arg_gate_test.py:366`: "Dell 151 not
  executable via single-seed leaf" — so the citation fails closed,
  but Batch A (U-A3) records that the 151 contract is *entirely
  unopened*: no source says what 151[Harmonic] is.
- **Severity: LOW–MEDIUM** (refusal is honest; the dangling
  citation in the language's own docstring invites future
  confusion). **Path:** DC-8.

### C-9. DISCONNECTED class double-aspect counting (ledger hygiene)
- Batch A (G-19 entry): "several DISCONNECTED entries are the
  same mechanisms" — EQ-RES-003 and EQ-GRV-001 each carry two
  aspects (arithmetic + reference; assignment + pull), and ledger
  §11 discloses this itself ("counts are distinct equations,
  aspects listed separately"). Not a falsehood — a class whose
  headline count (2) understates its surface (4 aspects).
  **Severity: LOW.** Path: G-19's disposition circuit reads the
  class by aspects.

### C-10. FAR-17 ≡ G-30 dual filing
- One item (the χ computation) filed in two registers (Batch B).
  Counted once in T = 224; the dual filing is preserved in both
  registers by design (§7 provisional register vs FAR register).
  **Severity: LOW** (counting hazard only). Class: NAMESPACE —
  handled by the unified plan's register prefixes; flagged so
  future renders dedupe on sight.

---

## 5. REUSE OPPORTUNITIES — the existing mechanism, named

### R-1. `text_metrics` (TOKEN_RE + `jaccard`) — the canonical-substrate pattern
One definition, 17 consumers (D-6). Any new token-overlap or
tokenization need in the integration plan routes here; the pattern
itself (one substrate module, thin consumers) is the template for
every dedup in §1.

### R-2. `sacred_geometry.vesica` — the one overlap core
The delegation in D-1 proves the wrapper pattern works. Any new
overlap consumer the integration plan admits (Tree derived layer,
nerve research, FAR geometry) builds on EQ-GEO-001/003/004 — it
does not re-derive lens math.

### R-3. The ringed_growth scorer pipeline — gate → coherence → set metric
`_affinity` (gate) + `graph_coherence` (graph layer) +
`harmony_score` (set layer), with a separation proof (p3_r32) and
fail-closed filters. When Tree/resonance quantities are admitted,
this layered shape — not a new monolithic scorer — is the existing
architecture to extend. It is also D-2's reconciliation, already
built.

### R-4. `spatial_audio` — FAR-20's toehold is already built
The orphan (O-1) already computes position → pan/gain/band/ear
cues. FAR-20's calculated sonification should consume and extend
this module (adding value-derived pitch/rhythm under a declared
mapping) rather than build a second audio mapper.

### R-5. `HarmonicLattice` perception forms — the projection machinery exists
`to_core / to_cube / to_sphere / to_flower` already switch readings
over one coordinate store ("coordinates stay; reading changes").
The Tree presentation layer the Director specifies (Integration
Plan §4, layer 5) should reuse this reading-switch machinery —
with the slice-vs-projection distinction he names enforced by
sacred_geometry's exact slice census (the (111) *slice* is the
Flower; an unrestricted *projection* superimposes points and is a
different, labelled view).

### R-6. EXT-GEO-001 two-sphere lens volume — verified formula, awaiting admission
Ledger §9: closed form, numerically verified in recovery (1000
random cases), RECOVERY_CANDIDATE. If a 3D overlap quantity is
ever admitted, this is the cheapest candidate — admitted through
the Admission Contract, not re-derived. (EXT-GEO-002/003/004 are
the same shape for nerve/void/weighted questions, X-3.)

### R-7. `forces.py` wells persistence — the restore pattern already exists
GP-G03's register path proposed "derive on load"; the code already
persists *and* restores wells (forces.py:557-572) and the
ForceField family has a save/restore frame. Whatever the census
finds missing (UU-1), the repair reuses this frame — no new
persistence mechanism for forces.

### R-8. `equation_ledger_invariants_test.py` — the anti-drift instrument exists
A test already pins ledger equations to code behaviour (it imports
both `sacred_geometry.vesica` and `verita.vesica_strength` and
checks them). Extending this suite to assert *classifications*
(delegation present ⇒ not DUPLICATE; wiring present ⇒ R4-A5
status) is the cheapest permanent cure for C-3-class drift — the
instrument exists; it needs the assertions.

---

## 6. DECISION REGISTER CANDIDATES — rulings, not engineering

One line each; the question stated exactly as the authority must
answer it.

**Director**
- **DC-1.** Shall the equation ledger carry append-only
  reclassification entries — EQ-VER-001 from DUPLICATE to
  delegated-canonical, and R4-A5's status updated to the R3.2/R3.6
  reconciliation — citing the code evidence in C-3?
- **DC-2.** What is the rename/namespace scope for the name
  collisions: which two of the three "verita" mechanisms rename
  (R4-A2), and does the same ruling cover the seven "harmonic"
  bearers (R4-A6 extended, C-6)?
- **DC-3.** Which defined metric replaces EQ-GEO-002 under the
  Admission Contract — lens-area fraction or Jaccard-of-disks
  (R4-A3) — and in which phase does the replacement circuit run?
- **DC-4.** Is VERITA-JUDGE (verita.py) production-live or a
  test/proof surface only — the ledger's "live on brain/
  auto_growth" against this lane's grep (O-14) — and if the grep
  stands, what is verita's recorded participation?
- **DC-5.** Does the Director confirm GP-G03's status from the
  X11 census's runtime evidence when it lands, closing the
  register-vs-MWL-vs-code conflict (C-7) — or rule on the
  documents now?
- **DC-6.** R4-A4, resonance's "vesica" log token: rename the
  token (to what?) or wire real overlap geometry into
  `harmonize_pair`?
- **DC-7 (Director/Keeper, credit).** Do closed findings earn
  COMPLETE credit — GP-G24 (closed by filing), G-29 (census
  closed), FAR-17 (computed) — the +3 question inside UU-14/C-4?

**Ace**
- **DC-8.** Dell 151[Harmonic]: open a contract for it, extend
  the registry beyond 99, or strike the citation from seed.py's
  docstring examples (C-8)?
- **DC-9.** The twelve O-2..O-13 orphan-candidate modules: one
  class ruling — stand-down receipts for the class (on the SD-5
  `idea_grow` receipt model) after X11's runtime check, or
  case-by-case dispositions?
- **DC-10.** Space (GP-G01): after the negative-space report,
  build the room-to-grow quantity or retire the force with a
  receipt (X-8)?
- **DC-11 (Ace/Director, process).** Does the equation ledger
  become a living document — a reclassification check owed by
  every circuit that touches a ledgered mechanism — or remain a
  V1 snapshot to be succeeded by a Ledger V2 (C-3's process
  form)?

*Already owned, not candidates: the Keeper's THL-SM-02
reproduction verdict and the Director's subsequent FCC admission
ruling (UU-6) are assigned gates, listed here only so this
register is not mistaken for the whole decision surface.*

---

*End of Lane 3. All grep claims are scoped to the commands stated;
all ledger citations are to Ledger V1 in the SYSTEM-001 clone; no
repository file was modified by this lane.*
