# FAR STRATUM — DESIGN PACKAGES (2026-11-20)

**Part IV plan-stage deliverable** (branch `uni/part-4-far-stratum`,
base main `af2519b6d239ef278397e277210d6da2467c36e5`). Full-depth
design packages for the Reader, FAR-1..FAR-20, the provisional
register G-29/G-30/G-31, the COMBO-9 filing note, the P07 deferral
record, and the declined Exchange Phase G (#117).

**Source of record:** the Unified Edition Part IV (§7 refinement,
2026-11-14), written against the sandbox studies named in each entry
and Grand Plan §7. Status claims below were re-checked against
current main `af2519b6` on 2026-11-20; readiness grades are the
sources' own, never upgraded.

**Stratum law (from PART_IV_PLAN §1):** DESIGNS proceed now; BUILDS
wait on Part VII's Grand Synchronization closing + each item's own
authorization. Every package states its split explicitly. Every
package carries the GP-E28 quartet: **typed unit · uncertainty ·
witness · falsifier.**

**Package field key:** STATE (evidence) · DESIGN · DEPENDS ·
ACCEPTANCE (future build proof) · FAILING-FIRST (the test the future
build writes first) · SPLIT.

---

# THE READING LINE

## THE READER — reading chains of thought from recorded streams

- **STATE:** Study complete (Reading Chains study, 2026-11-14); no
  Reader mechanism exists in the product. The reading direction exists
  in three places: the seed parser (text), LatinMandell (PARSE =
  SPLIT × STACK × CLASSIFY × MAP, honesty-scored receipts), Trace 90
  (the program's own process). Evidence grades from the study:
  ethograms REAL and formalized (strong EXTERNAL_EVIDENCE); true
  natural codes exist in pockets (waggle dance — decoded by
  prediction; vervet alarm calls — referential); body-language
  mind-reading REFUTED as a discipline (movement readable, inner
  states not); plant-network "conversation" claims CONTESTED.
  GP-E28 fence: the Reader reads only observed recorded streams,
  never claimed private inner thoughts. Readiness: **BOUNDED**
  (first TYPE vocabulary unbuilt; first stream/corpus unselected;
  tracking form waits on FAR-13).
- **DESIGN (full):** READ = SEGMENT × TYPE × CHAIN × TEST, built as
  four instruments over one ledger:
  1. **Ethogram Ledger** — append-only, timestamped raw record:
     `(stream_id, t_offset, raw_event, source_generation)`. A reading
     never edits the ledger; corrections are new entries. Ledger
     entries are the typed unit; the raw event is stored verbatim so
     any reading can be re-derived or refuted from the same record.
  2. **Segmenter** — cuts a stream into candidate events by stated
     boundary rules (gap thresholds, change-points); every boundary
     carries the rule that made it, so segmentation is itself
     receipted and contestable.
  3. **TYPE vocabulary + Chain builder** — segments are typed from a
     stream-specific ethogram vocabulary (the first vocabulary is a
     design deliverable of the first build circuit, built for ONE
     chosen stream by the protocol in step (a) below); typed segments
     compose into bilingual chains (Mandell gloss + English), every
     chain born wearing the **PROJECTION stamp (77[Infer])**. Gloss
     steps are admitted as gloss, never costumed as Dells.
     (a) *First-vocabulary protocol:* select one recorded stream with
     a known ground-truth structure (a docked Psalm's receipted
     activity is the designated first candidate — its events are
     already receipted, so types can be checked against receipts);
     draft the ethogram from the receipts; freeze it before any
     reading is graded.
  4. **Grading instruments** — THE NEXT-STEP TEST (a reading must
     predict held-out continuations better than chance AND better
     than raw base-rate/Markov counting, or be re-graded as
     narrative); THE TWO-READERS RULE (two independent readers
     transcribe blind; agreement rate receipted); THE PROJECTION
     STAMP graduation road (observed → proposed → DuoBeta gate ≥3 →
     advisory — the existing road, no new gate).
- **DEPENDS:** DuoBeta's graduation gate (exists); FAR-13 for the
  tracking form (belief states between observations). Feeds FAR-13
  (first consumer), E10's Kalman + Markov material.
- **ACCEPTANCE:** a built Reader's chains predict held-out
  continuations of a real ledger better than chance and better than
  base-rate/Markov counting; Two-Readers agreement rate on the
  receipt.
- **FAILING-FIRST:** `reader_next_step_vs_markov` — at base (no
  Reader) the test harness scores the null reader (base-rate/Markov)
  and asserts the typed-reader slot is EMPTY; the build passes only
  when a typed reading beats both baselines on a frozen held-out
  split, and the harness records NOTATION_NOT_INSTRUMENT if it does
  not.
- **SPLIT:** Design NOW (this package, incl. the vocabulary protocol
  and harness spec). Build: B-VII + own authorization; first-stream
  selection is part of that authorization ask.

## FAR-13 — THE ESTIMATOR (blueprint N1: Kalman / Bayes / least squares as a service)

- **STATE:** Premise established by G-29's dual census (converged at
  pinned main `d59649a8`): NO true estimator exists anywhere in the
  repo — nothing carries state + uncertainty + update rule. HD-4
  calls the family "the sweep's largest genuine gap." Nine
  deterministic fragments catalogued as the reuse inventory
  (SlopeTracker's ≤48-sample window; duobeta_learn's linear evidence
  counts, `form/mandell/duobeta_learn.py:34-101`; linear_algebra.py /
  eigen_stability.py exact 2×2 toolkit; decision_shells.py:193;
  inspire_pack.py:120+). Readiness: **BOUNDED** (first form unchosen;
  representation undesigned; Admission Contract classification not
  yet sought).
- **DESIGN (full):** A state-estimation service with one interface
  and a deliberately incomplete first form, per GP-E28:
  1. **Interface (typed unit):** `Estimator.estimate()` →
     `(state, uncertainty)`; `Estimator.update(observation)` →
     revised `(state, uncertainty)` + receipt naming the update rule
     applied. Uncertainty is a first-class field (interval or
     variance, per form), never a comment.
  2. **First form: least squares, deterministic, explicitly
     incomplete** — the SlopeTracker upgrade is the reference build:
     slope over the ≤48-sample window WITH a standard error, replacing
     the bare two-sample derivative. The service's receipts state
     "least-squares baseline; no process-noise model" on their face —
     incompleteness is disclosed, never hidden.
  3. **Alternate candidates (experimental only):** Kalman filter and
     Bayesian updating (duobeta_learn's counting skeleton restated as
     conjugate updating) are filed as EXPERIMENTAL candidates behind
     the same interface; neither may become a product default without
     its own admission + certification. GP-E28 fence, verbatim-grade:
     alternate candidates are "experimental candidates rather than
     secret product defaults."
  4. **Admission path:** any estimator equation enters only under the
     ledger's Mathematical Admission Contract; the classification
     request for the least-squares form is a named step of the build
     circuit, before code.
  5. **Consumers, in order:** the Reader (first), COMBO-2 the
     Tracking Reader (Reader × Estimator), Profile second.
- **DEPENDS:** G-29's finding (closed); the Admission Contract.
- **ACCEPTANCE:** an estimator demonstrated on a noisy stream with
  receipted uncertainty: predicted-vs-observed residuals behave as
  the stated noise model claims; the least-squares slope + standard
  error beats the two-sample derivative on seeded noisy data with
  known ground truth.
- **FAILING-FIRST:** `estimator_three_part_test` — the built thing is
  itself subjected to G-29's three-part test (state? uncertainty?
  update rule?): at base every repo candidate FAILS it (that is the
  census result); the build passes only when the service passes all
  three parts and the seeded-noise fixture's residuals match the
  stated model within the receipted tolerance.
- **SPLIT:** Design NOW (interface, first form, admission path,
  candidate fences). Build: B-VII + Admission Contract classification
  + own authorization.

## FAR-20 — THE SOUNDING FIELD (calculated sonification)

- **STATE:** Added to §7 by Ace 2026-11-14. Toehold VERIFIED on main
  (re-checked `af2519b6`, 2026-11-20): `form/dell_matrix/
  spatial_audio.py` EXISTS (position → pan/gain/band/ear cue dicts)
  with NO callers in `form/`, `src/`, or `gui/` — a Completeness-Law
  orphan. No pitch, rhythm, or melody derived from data values exists
  anywhere. The lattice notes and THE CHORD are assigned but
  unconsumed; FAR-20 names their first consumer. THE CHORD was
  adopted by Ace 2026-11-13 as a derived reading only. Readiness:
  **BOUNDED** (mapping design, first consumer, Console integration
  all open — the mapping design is closed by this package).
- **DESIGN (full):** Sound as a WITNESS sense — derived, rebuild-only,
  testifying to nothing.
  1. **Mapping declaration (the core design):** every sonification is
     a declared mapping `M: value → (pitch, rhythm, melody-role)`
     recorded on a **mapping receipt** before any audio parameter is
     produced: the value's scale law (linear / log / rank — FAR-11
     applies to ears as to eyes), the pitch assignment rule (a named
     scale + reference), the rhythm rule (event cadence → temporal
     pattern), and the silence rule (resting components are quiet —
     the Activation Clause). Two listeners with the same data + same
     mapping receipt hear the same music; that determinism IS the
     design.
  2. **First consumers, ranked:** (i) THE CHORD audible as three-part
     harmony — a field heard as consonant or tense (flagship; the
     chord member's note moves exactly as its centre's label
     dictates); (ii) Psalm Matrix live-feed activity gaining melodic
     movement (a docked AI's work gains a sound); (iii) force and
     weather states as audible conditions.
  3. **Foundation:** spatial_audio.py's position→cue mapping is the
     spatial layer; FAR-20 adds the value→pitch/rhythm/melody layer
     beside it, same consumer shapes (UI / TTS / Web Audio cue
     dicts). No core-execution sonification (GP-E28 fence).
  4. **Console (H9)** serves FAR-20 and tunes its readings — derived
     layer only, presets as receipts.
- **DEPENDS:** step 5's windowed workspace + the Console (H9) for its
  control surface; FAR-11 (scale law); THE CHORD (H6 geometry,
  derived).
- **ACCEPTANCE:** a named dataset rendered twice from the mapping
  receipt produces identical audio parameters; a changed dataset
  produces the mapping-predicted change. Falsifier: any audible
  parameter not derivable from declared mapping + data.
- **FAILING-FIRST:** `sounding_field_determinism` — fixture dataset +
  frozen mapping receipt; at base the render function does not exist
  (FAIL by absence); build passes on byte-identical cue dicts across
  two renders and the predicted delta on the changed fixture.
- **SPLIT:** Design NOW (mapping receipt format, consumer ranking,
  layer split). Build: B-VII + own authorization; Console surface
  dependency (step 5) must exist first.

---

# THE DYNAMICS LINE

## FAR-4 — CONVERGENCE RECEIPTS

- **STATE:** From V2 (K-means; Lloyd's converges to a local optimum,
  objective decreasing every round). Classification: ADOPT as a
  reporting convention (X5 family). The Atlas grammar exists
  (PERIOD-1 / PERIOD-k / NO-VERDICT-WITHIN-BUDGET, budget stamped).
  Readiness: **READY** — convention completely specified; no process
  wired yet.
- **DESIGN (full):** One receipt schema for every iterative process:
  `(process_id, budget, rounds, moves_per_round[], settling_class)`
  where settling_class ∈ {PERIOD-1 (settled), PERIOD-k (cycling,
  k named), NO-VERDICT-WITHIN-BUDGET}. A bare "done" is a schema
  violation. **Adoption list (wiring rides each process's own
  circuit):** growth rounds; medoid rounds (FAR-3 — its receipt is
  this schema); DuoBeta rounds; authority cadences. The wiring
  pattern per process: wrap the loop's exit with the receipt
  emission; the loop's internals are untouched — this is a reporting
  convention, not a control change.
- **DEPENDS:** the Atlas verdict grammar (exists). Feeds FAR-3,
  FAR-8 (scheduled re-tests report in this grammar), E1.
- **ACCEPTANCE:** a named iterative process emits a receipt in the
  grammar whose verdict an independent rerun reproduces (same budget,
  same settling class); a process that cannot settle says
  NO-VERDICT-WITHIN-BUDGET rather than timing out silently.
- **FAILING-FIRST:** `convergence_receipt_shape` — fixture process
  with a planted cycle: at base it exits with no receipt (FAIL);
  build passes when the receipt names PERIOD-k with the correct k,
  and a planted non-settler yields NO-VERDICT-WITHIN-BUDGET.
- **SPLIT:** Design NOW (schema + adoption list + wiring pattern).
  Adoption wiring: each process's own circuit, in its own Part —
  named here so no process's lane is surprised.

## FAR-9 — THE PERIODICITY PRINCIPLE

- **STATE:** From V9 (Regev 2023; Shor's hidden PERIOD via QFT)
  mirrored against V4 (Kaluza–Klein: momentum around a hidden
  periodic dimension is quantized → charge) and the Tree/chord
  (mod-12 periodic labelling). Classification: ADAPT. §7 seats FAR-9
  with FAR-14 as one root with one desk. Readiness: **READY** —
  principle stated completely; execution lives in FAR-14.
- **DESIGN (full):** A naming/rooting act with two binding rules:
  (1) every period claim carries its detection method and its
  budget; (2) every failed hunt reports NO-VERDICT-WITHIN-BUDGET
  (FAR-4 grammar). The principle names the shared root of the Atlas
  instrument family — chord circle, Shor, KK, X3 — so period
  questions route to one desk (FAR-14) instead of being re-invented
  per consumer.
- **DEPENDS:** FAR-14 for machinery. Feeds X3 oscillation detection,
  COMBO-7 (Voynich ring spectra), HCN rhythms, authority cadences.
- **ACCEPTANCE:** instrumental — the desk (FAR-14) detecting a known
  period in a seeded signal and honestly reporting budget-expiry on
  a period-free control.
- **FAILING-FIRST:** carried by FAR-14's `spectral_desk_seeded_period`
  (below); FAR-9 itself is a principle adoption — its failing-first
  is the first period claim filed WITHOUT method + budget, which the
  adoption makes a filing defect.
- **SPLIT:** Design NOW (the adoption package). Execution: FAR-14.

## FAR-14 — THE SPECTRAL DESK (blueprint N2)

- **STATE:** Classification: NEW single system (Fourier /
  autocorrelation / wavelets — period-finding as a service).
  Component FACT (re-checked `af2519b6`): the Fourier transform is
  already INSIDE (`form/dell_matrix/fourier.py`); autocorrelation is
  the blueprint's named period-finder core (Wiener–Khinchin). No
  desk — no shared service, queue, or interface — exists. Readiness:
  **BOUNDED** (interface, windowing defaults, wavelet role — the
  first two are closed by this package; the wavelet role is stated
  as a bounded unknown with its decision path).
- **DESIGN (full):** One desk, one job interface, every period
  question receipted:
  1. **Job (typed unit):** `(signal_source, window, method, budget)`
     → **receipt** `(method, window, budget, verdict)` with verdict
     in FAR-4 grammar (PERIOD-k with the period named, or
     NO-VERDICT-WITHIN-BUDGET). Methods: DFT (via fourier.py),
     autocorrelation (Wiener–Khinchin core), wavelet (family named;
     its role — transient/localized period detection — is the desk's
     one open design decision, taken at build time with the first
     wavelet consumer as the decider).
  2. **Windowing defaults:** the job must state its window; the desk
     ships NO silent default — an unstated window is a filing defect
     (declared-bounds doctrine). Reference windows are proposed per
     consumer in their own circuits.
  3. **Consumer queue (named):** X3 oscillation detection; COMBO-7
     (Fourier × Voynich ring labels — a DFT pass over the zodiac
     ring-label sequences, **sandbox-only**); HCN rhythms; authority
     cadences. Each consumer files jobs through the same interface —
     two consumers through one interface is part of the proof.
- **DEPENDS:** FAR-9 (principle); fourier.py (exists).
- **ACCEPTANCE:** seeded-signal tests: the desk recovers planted
  periods (including a planted ring-label-style sequence) at stated
  SNR, returns NO-VERDICT-WITHIN-BUDGET on noise controls within the
  stamped budget; two consumers (X3 and COMBO-7) served through the
  same interface.
- **FAILING-FIRST:** `spectral_desk_seeded_period` — at base no desk
  exists (FAIL by absence); build passes on planted-period recovery
  at stated SNR + honest budget-expiry on the noise control.
- **SPLIT:** Design NOW (interface, receipt, queue, no-silent-default
  rule). Build: B-VII + own authorization.

## FAR-5 — ATTRACTOR READINGS

- **STATE:** From V3's grading: the video's title claim ("geometric
  reasoning obsoletes data centers") is UNSUPPORTED and REJECTED (no
  mechanism, no measurement; fails the Next-Step Test) — it is NOT
  in this register and this package does not revive it. What
  survives: energy-based/attractor models are legitimate literature
  (Hopfield networks); the Atlas's basin maps ARE attractor
  portraits (pendulum study; Lorenz as type specimen, blueprint §2C).
  Classification: ADAPT (terminology + reading). Readiness: **READY**.
- **DESIGN (full):** Two acts, both completely specified:
  1. **Vocabulary adoption:** Atlas basin maps are named attractor
     portraits in the Atlas's own vocabulary — aligning with the
     legitimate attractor literature at zero mechanism cost. No
     mechanism is imported; the naming is the deliverable.
  2. **The caution rule (standing):** any future "obsolete / free /
     infinite" efficiency claim enters only with a mechanism and a
     footprint measurement, or it enters as a REJECTED claim with V3
     cited as the type specimen.
- **DEPENDS:** the Atlas basin maps (exist as studies). Feeds §1
  Efficiency Doctrine claim discipline; FAR-12's evidence ladder.
- **ACCEPTANCE:** the Atlas vocabulary in use with portraits labeled;
  the caution demonstrated — the next mechanism-free efficiency claim
  is filed as a rejected specimen citing this rule.
- **FAILING-FIRST:** filing-level: the first efficiency claim
  arriving after adoption WITHOUT mechanism + footprint that is NOT
  filed as a rejected specimen is the failure this adoption exists
  to prevent; the adoption package itself is the test fixture.
- **SPLIT:** Design NOW (adoption package). Adoption is a
  Director/Ace filing act on this package; no build exists.

## FAR-11 — A SCALE LAW ON EVERY MAP

- **STATE:** From V8 (Schrödinger simulation with dynamic scaling;
  FACT as mathematics). The study's firewall is explicit:
  superposition, interference, tunneling are NOT imported as
  mechanisms (REJECT as mechanism — ideas are not wavefunctions;
  "resonance" is already overloaded, R4-A6). What transfers is
  DISPLAY discipline. Classification: ADAPT (witness discipline,
  H9/H10 etiquette). Readiness: **READY** — completely specified;
  filed, not yet practiced on any surface.
- **DESIGN (full):** A witness contract for every behavior map /
  profile chart: (1) the map states its scaling (linear, log, rank)
  on its face, beside the picture; (2) dynamic rescaling is allowed
  only when the law travels with the view — the view's metadata
  names the law before and after rescaling; (3) the contract applies
  to ears as to eyes: FAR-20's mapping receipts carry the scale law
  as a required field. Surfaces in scope: Profile charts, Atlas
  maps, X9 weather, FAR-20 sonification.
- **DEPENDS:** nothing unbuilt. Feeds FAR-20, Profile honesty, every
  Atlas map.
- **ACCEPTANCE:** the next behavior map shipped carries its scale law
  on its face; a dynamically rescaled view demonstrably carries the
  law with it (metadata names the law before and after).
- **FAILING-FIRST:** `scale_law_on_face` — fixture map rendered at
  base carries no scale-law field (FAIL); build/adoption passes when
  the field is present and survives a rescale operation unchanged in
  the view metadata.
- **SPLIT:** Design NOW (the contract). Practice: each surface's own
  circuit adopts it; the contract itself is this Part's deliverable.

## FAR-8 — THE MEMORIZATION AUDIT

- **STATE:** From V7 (supervised learning; overtraining on noisy
  labels memorizes the key instead of learning the rule).
  Classification: ADAPT (audit instrument). The design contrast is
  recorded: DuoBeta moves DISCRETE advisories through an evidence
  GATE (≥3 matching outcomes) and may never touch truth — gates over
  gradients, deliberately. Symbiosis composition laws owe the same
  held-out debt. Readiness: **BOUNDED** (sequestration protocol,
  cadence, thresholds — the protocol and cadence are designed here;
  thresholds are named as authority decisions with proposed defaults).
- **DESIGN (full):** An audit that keeps learned things honest:
  1. **Demand:** learned advisories and composition laws must
     predict HELD-OUT outcomes — cases that played no part in
     forming them — on a schedule, with the score receipted; a law
     that only explains its own training set retires as
     memorization.
  2. **Sequestration protocol (designed):** time-split holdout —
     outcomes arriving AFTER an advisory's formation timestamp are
     its held-out set by construction (formation cannot leak into
     the future); the audit seals the split by recording the
     formation timestamp + the outcome-stream cursor at formation.
     A hash-sealed explicit holdout is the alternate for
     non-temporal corpora (e.g., composition laws over recorded
     fields): the holdout manifest is hashed at formation time, so
     later peeking is detectable.
  3. **Cadence (proposed):** audit runs on the authority cadence —
     each advisory class is scored once per sitting cycle against
     all outcomes sealed since its last audit; scores report in
     FAR-4 grammar (the audit itself is an iterative process and
     wears a convergence receipt).
  4. **Thresholds (DECISION items, proposed defaults):** per-class
     pass thresholds are the Director's to set; proposed default —
     an advisory scoring at or below its base-rate predictor on
     held-out outcomes over one full cycle is retired as
     memorization, with the retirement receipted, never silent.
- **DEPENDS:** DuoBeta's advisory ledger (exists); an outcome stream
  to hold out from. Feeds DuoBeta credibility accounting; FAR-7's
  control-group discipline.
- **ACCEPTANCE:** the audit running: a named advisory's held-out
  score receipted over at least one full schedule cycle; the
  falsifier — a deliberately memorized control advisory (fit to its
  training outcomes only) is caught and retired by the audit.
- **FAILING-FIRST:** `memorization_audit_catches_control` — plant
  the control advisory at base; the audit (absent at base) cannot
  catch it (FAIL); build passes when the control is retired with a
  memorization verdict and a genuine advisory's held-out score is
  receipted.
- **SPLIT:** Design NOW (protocol, cadence, threshold proposal).
  Build: B-VII + Director threshold decisions + own authorization.

---

# THE STRUCTURE LINE

## FAR-1 — THE FOURTH FLOOR (the D4 Tree study)

- **STATE:** From V1 (Schläfli: 5 regular solids in 3D, 6 regular
  polytopes in 4D, exactly 3 families from 5D up). The Tree studies'
  FCC lattice has a 4D cousin: the D4 lattice, kissing number 24; the
  24-cell is one of 4D's six. Classification: ADAPT (method) — "the
  study itself is the deliverable." Not yet performed. The 3D base is
  independently verified (THL-SM-01: FCC shells, step shells
  10k²+2, slices, exclusions — all VERIFIED exact/theorem); the
  FCC-vs-HCP canonical question (Q-T1) remains a recorded choice, not
  a ruling. Readiness: **READY** as a study.
- **DESIGN (full):** The Tree study's method transferred verbatim,
  one dimension up:
  1. **Definitions published before results:** D4 centres as integer
     vectors with even coordinate sum (equivalently the
     integer/half-integer union under the D4 parity rule); adjacency
     = the 24 minimal vectors; step shells by BFS over adjacency.
  2. **Census plan:** exact integer censuses — shell counts, slice
     censuses (hyperplane slices at stated offsets), exclusion
     checks — mirroring THL-SM-01's verification shape so the 4D
     result is checkable the same way the 3D one was.
  3. **Chord-labelling search:** the Tree Harmony Mirrors brute force
     in 4D shape — candidate labellings enumerated, clean+pure
     filters applied (the 3D run: 1,728 candidates → 24 clean+pure →
     2 families; the 4D search space is computed and stated BEFORE
     the search runs, per the published-definitions rule).
  4. **Demotion frame (mandatory):** FAR-2 is this study's reporting
     frame — richness shrinks under generalization (∞ → 5 → 6 → 3);
     what dies on the way up is reported, not hidden. The study's
     report carries a demotion section by construction.
- **DEPENDS:** the 3D Tree study + THL-SM-01 (both complete). The
  Keeper-side reproduction gate (THL-SM-02) and the Director's
  admission ruling remain outstanding — neither blocks this study.
  Feeds FAR-2 (type specimen at dimension scale); the Tree's
  long-range geometry record.
- **ACCEPTANCE:** the study itself, receipted like FAR-17's:
  published definitions before results, exact counts, a stated
  falsifier — if no clean mod-12 labelling exists in D4, that
  negative is the result and closes the question.
- **FAILING-FIRST:** `d4_census_crosscheck` — two independent
  enumerations (direct parity-rule generation vs. BFS-from-origin
  closure) must agree on shell counts; at base neither exists (FAIL
  by absence); the study passes when they agree exactly, or the
  disagreement is itself the receipted result (the FAR-17 v2 lesson:
  a detected instrument defect, fixed on the receipt, is a valid
  study outcome — a silent disagreement is not).
- **SPLIT:** Design NOW (protocol complete above). Execution: a
  sandbox study circuit at step 7 — B-VII + own authorization
  (read-only sandbox computation, the SD-GP-01 pattern).

## FAR-17 — THE NERVE'S χ (= G-30, one item dual-filed, counted once)

- **STATE:** PERFORMED 2026-11-14 under SD-GP-01 authorization
  (read-only sandbox computation); receipt published
  (SANDBOX_FAR17_CHI_RECEIPT_2026-11-14). RESULT, exact scope:
  χ = 1 at patches R = 1/2/3 under the PATTERN convention — counts
  complete (R=1: 7, 18, 18, 6; R=2: 19, 72, 84, 30; R=3: 37, 162,
  198, 72); no feasible 5-fold pattern subset exists (0 of 11,628 at
  R=2; 0 of 435,897 at R=3); two cross-checking methods in full
  agreement AFTER a detected-and-fixed instrument defect (v2 method
  A initially missed tangent pairs; the disagreement counts equalled
  the tangent-pair counts exactly — 3/27/69). QUALIFICATIONS: the
  two methods share one enumeration framework (computation
  cross-checked, definitions NOT independently validated); the nerve
  theorem certifies the CLOSED convention only; χ = 1 is an
  OBSERVED BASELINE for the tested ideal patches — corroborated, NOT
  proven, NOT a universal gauge; HD-6's naive formula is RETIRED.
  GP-E28 fence: the earlier ideal χ proof is not a real
  irregular-world model. Readiness: **BOUNDED**.
- **DESIGN (full):** What remains is the gauge question, designed as
  an extension study matrix over the receipt's explicit untested
  domains — each cell is a named study leg with its own receipt:
  (1) irregular fields (open question Q-F2) — the gauge's home test:
  χ over an irregular field with a planted hole/exclusion must
  depart from 1 in the predicted direction; (2) ρ ≠ 1; (3) patches
  R ≥ 4; (4) lifted (one-layer 3D) and native FCC fields; (5)
  mixed-shape (polygon-ladder) fields; (6) fields with holes or
  exclusions by construction. Plus the certification leg: an
  **independent execution pass** — a second implementation written
  from the published definitions only (no shared enumeration
  framework) — which is what full computational certification
  requires and the one thing the 2026-11-14 receipt names as still
  owed. Until the matrix runs, χ is filed exactly as the register
  files it: "a bounded, completed sandbox computation with a
  receipt — not a capability, not a register promotion."
- **DEPENDS:** Part I's nerve counts (exist); EXT-GEO-002 (Čech/nerve
  candidate, RECOVERY_CANDIDATE in the equation ledger — status
  unchanged by the FAR-17 result). Feeds H2 field-topology gauges;
  U-5's test fixture.
- **ACCEPTANCE:** per leg — the planted-hole leg is the gauge's
  falsifier: χ departs from 1 in the predicted direction, or the
  gauge claim dies.
- **FAILING-FIRST:** `chi_gauge_planted_hole` — irregular fixture
  field with a planted exclusion; at base no gauge exists to compute
  it (FAIL); the extension study passes the leg only on the
  predicted departure, receipted either way.
- **SPLIT:** Design NOW (the matrix + the independent-pass spec).
  Execution: sandbox study legs at step 7 — B-VII + own
  authorization per leg (SD-GP-01 pattern).

## FAR-2 — THE DEMOTION CHECK

- **STATE:** From V1's demotion law: richness SHRINKS as you
  generalize (∞ → 5 → 6 → 3); DellMatrix has lived it once (1,728
  Tree labellings → 24 perfect → 2 families). Filing: a reporting
  habit (X5 family), costless. §7 seats it twice: on the structure
  line, and at step 1.5 as the census's second-seat pass (HD-2: any
  inventory is viewpoint-bound — the math seventeen and the physics
  seventeen share only ~4 entries). Readiness: **READY**.
- **DESIGN (full):** A standing question attached to every proposed
  generalization: "does it survive one dimension/scale up, and what
  died on the way?" — with a receipt section template:
  `(generalization, survivors[], casualties[], verdict)`. Trigger
  points (named): any generalization proposal in any Part; the X11
  census's second seat (step 1.5), which produces its own row-level
  diff against the first seat. First formal uses: FAR-1's D4 study
  (its reporting frame) and the census second seat.
- **DEPENDS:** nothing unbuilt. Feeds X11 census honesty, FAR-1,
  every future generalization proposal.
- **ACCEPTANCE:** demonstrated in use: the next generalization
  proposal carries a demotion section naming what did not survive.
- **FAILING-FIRST:** filing-level: the first post-adoption
  generalization proposal WITHOUT a demotion section is the failure
  state; FAR-1's package (above) is pre-fitted with the section, so
  the habit's first use is already designed.
- **SPLIT:** Design NOW (habit + template + trigger points).
  Adoption: a filing act on this package; first uses ride FAR-1 and
  the census.

---

# THE INTEGRITY LINE

## FAR-16 — SELF-HEALING HISTORY (COMBO-5)

- **STATE:** Blueprint COMBO: error-correcting codes (Hamming /
  Reed–Solomon — §2H, INSIDE-adjacent: hash functions/checksums
  already run as the ledger hash chains and snapshot fingerprints) ×
  hash chains × sealed generations. Concept: "damage repaired, not
  only detected, up to a stated radius." No design, no prototype, no
  numbers exist — the design below is this package's work. The
  checkpoint/sealed-snapshot path it would extend passed every crash
  test on the standing record; the everyday save path's pair-safety
  defect is main-line (Q1-owned, Part I territory) and is NOT this
  item. Readiness: **RESEARCH** (scheme selection + measurement study
  needed — both designed here).
- **DESIGN (full):** A research design in three legs:
  1. **Scheme-selection study:** candidate families (Hamming,
     Reed–Solomon, one modern alternative) scored against the actual
     sealed-generation format on: repair radius per redundancy byte,
     decode cost at generation scale, failure behaviour beyond
     radius (must be detect-and-refuse, never silent miscorrection).
     The study's output is a recommendation WITH the measurements,
     not a preference.
  2. **Format integration design:** redundancy lives INSIDE the
     sealed generation (the seal covers data + redundancy together);
     the rollback law is a hard constraint — rollback converges
     eagerly by copying the sealed target into independent live
     state; any coding layer must preserve that exactly (repair
     happens at seal/open time, never by aliasing live state to a
     sealed member).
  3. **Radius/overhead budget:** the study measures overhead at the
     radius the scheme study recommends; the radius value itself is
     a Director decision taken on the study's numbers.
- **DEPENDS:** the sealed-generation path (exists, crash-tested);
  hash chains (exist). Feeds durability claims — which still ride
  the sealed path only.
- **ACCEPTANCE:** a corruption-injection test on a sealed generation:
  damage within the stated radius → byte-identical restoration with
  a repair receipt; damage beyond the radius → detected and refused,
  never silently "healed" wrong.
- **FAILING-FIRST:** `sealed_generation_repair_radius` — at base a
  sealed generation with flipped bytes is detected (hash) but NOT
  repaired (FAIL on the repair leg); build passes inside radius and
  refuses outside it, both receipted.
- **SPLIT:** Design NOW (study protocol + integration constraints).
  Execution: the study is a research circuit at step 7 — B-VII +
  own authorization; any product build is a further circuit after
  the study, under the Director's radius decision.

## FAR-6 — THE RESIDUE RULE

- **STATE:** From V4 (Kaluza–Klein; the leftover scalar Φ — the
  radion — must be stabilized by hand, and nothing in the theory
  does it). Filing: a design law CANDIDATE. Working exemplar inside
  DellMatrix: Verita already NAMES its leftover (residue marks).
  Cautionary exhibits: Split's unclassifiable remainder (DD-16), a
  projection's discarded dimension, a merge's un-inherited data
  (DD-15). Readiness: **DECISION** — completely figured; adoption as
  binding law belongs to the Director (design-law authority), Ace as
  Overseer.
- **DESIGN (full):** The adoption package, complete:
  1. **Rule text:** every split, merge, or projection names its
     leftover — the quantity the operation creates but does not
     govern — on the receipt, or the operation is incomplete.
  2. **Receipt section spec:** `(operation, leftover_name,
     leftover_disposition)` where disposition ∈ {governed-by
     (named owner), parked (named register seat), discarded-with-
     reason}. An operation whose receipt names no leftover is
     incomplete BY DEFINITION — reviewers refuse it on that ground
     alone.
  3. **Exemplar table:** Verita's residue marks (working exemplar —
     the rule already practiced); DD-16's remainder and DD-15's
     un-inherited data (cautionary — the defect shape the rule
     exists to catch at design time instead of in production).
- **DEPENDS:** nothing unbuilt. Feeds every future decomposition
  design; FAR-7 (the leftover is where projection claims go to be
  tested).
- **ACCEPTANCE:** applied in anger: the next split/merge/projection
  circuit's receipt carries a named leftover section, and a design
  review can point to an operation refused as incomplete for lacking
  one.
- **FAILING-FIRST:** filing-level: the first post-adoption
  decomposition design whose receipt lacks the leftover section and
  is NOT refused is the failure state.
- **SPLIT:** Design NOW (this adoption package). **Future ask
  (named, not requested in this PR's PLAN-CONFIRM): Director
  adoption of the Residue Rule as binding design law.**

## FAR-15 — THE CONSERVATION AUDITOR (blueprint N3; COMBO-8's home)

- **STATE:** Classification: NEW single system (Kirchhoff /
  continuity / Noether's question). Mirrors stated: continuity
  (∂ρ/∂t + ∇·(ρv) = 0) is the conservation law of FLOW; Kirchhoff's
  node law is COMBO-8's law (chain joints balance or leak,
  receipted); Ohm's law files as PATTERN (a joint's "voltage drop"
  is its failure pressure). No auditor exists. Readiness:
  **BOUNDED** (first joint set, FlowThru record sufficiency, receipt
  format/cadence — the sufficiency question is designed as leg 1
  below; format/cadence are designed here).
- **DESIGN (full):** A bookkeeping service asking of every flow and
  ledger "accounted?":
  1. **Audit equation (per joint):** `in = out + stored + lost`,
     receipted per joint; a leak is a named defect with a joint
     address, never a global shrug.
  2. **Leg 1 — records-sufficiency study (designed):** before any
     instrumentation is built, audit whether FlowThru's existing
     records carry enough per-joint data; the study's output is the
     first instrumented joint set (joints whose records suffice) +
     the instrumentation delta for the rest. Building the auditor
     before this study would be building on a guess.
  3. **Receipt format + cadence (designed):** per-audit receipt
     `(joint, in, out, stored, lost, verdict)`; verdicts in FAR-4
     grammar; cadence = on-demand per chain execution for the
     instrumented set, plus a scheduled full pass per sitting cycle.
  4. **Noether half:** the auditor's second question — of every
     symmetry, what's conserved (HD-5) — is operated from FAR-7's
     program; this service supplies the joint data it asks over.
- **DEPENDS:** Flow's records (main line; G-31's flow contract work
  is the adjacent substrate — see G-31); the Receipt Commons. Feeds
  FAR-7; chain-defect detection generally.
- **ACCEPTANCE:** a seeded-leak test: a chain with a known, planted
  loss at a named joint — the auditor's report names that joint and
  the lost quantity, and balances clean chains to zero unexplained
  loss.
- **FAILING-FIRST:** `conservation_auditor_seeded_leak` — at base no
  auditor exists (FAIL); build passes on the planted joint named
  with the exact lost quantity, clean chains at zero.
- **SPLIT:** Design NOW (equation, leg-1 study, receipt, cadence).
  Build: B-VII + own authorization, leg 1 first.

## FAR-18 — THE ENTROPY GAUGE (blueprint N5 + COMBO-1)

- **STATE:** Blueprint: Shannon entropy H = −Σp log p (Stewart #15),
  ENHANCES ×3 — (1) the Zipper's bound (no Distill/Compress beats
  its source's entropy; footprint receipts can state their floor —
  E6, with the Kolmogorov confession that the receipt bounds K,
  never equals it), (2) Nursery weather (topic entropy is X9's
  missing gauge — COMBO-1), (3) a field's entropy trend as a health
  line. N5: one derived gauge family, all rebuild-only views under
  HS-1. No gauge is built; the mathematics is elementary and
  undisputed. Readiness: **BOUNDED** (per-surface distributions,
  windowing, display contract — all three are designed here).
- **DESIGN (full):** One gauge family, three surfaces, each with its
  distribution defined:
  1. **COMBO-1 Topic Entropy Weather (most specified):** per-topic
     entropy of the proposal pool over time. Distribution: proposals
     by topic tag over a sliding window; window = the pool's last N
     proposals with N stated on the gauge (declared-bounds rule —
     no silent window); the weather line is H(topic) plotted against
     pool time, moving as the pool provably concentrates/disperses.
  2. **Field diversity:** H over field membership by Dell/topic
     class, unweighted count distribution (weighting, if ever
     wanted, is a separate declared variant, never a silent change).
  3. **Ledger spread:** H over the outcome ledger's verdict classes.
  4. **Footprint floors (E6):** footprint receipts may state the
     source's entropy as a floor, worded as a bound ("no compression
     below H(source) is claimed"), with the Kolmogorov confession
     attached where K is invoked.
  5. **Display contract:** gauges are derived views (HS-1) — they
     render from records, never write to them; each gauge face
     carries its distribution definition + window (FAR-11's scale
     law applies: the definition travels with the view).
- **DEPENDS:** Nursery pool records (exist); X9's weather surface.
  Feeds E3, E6, field health reporting.
- **ACCEPTANCE:** COMBO-1 computed over a recorded pool history: the
  weather line moves as the pool's topic distribution provably
  concentrates/disperses (checked against hand-computed H on a small
  fixture pool); a footprint receipt states an entropy floor that a
  compression run then respects or refutes.
- **FAILING-FIRST:** `entropy_gauge_hand_computed_fixture` — small
  fixture pool with hand-computed H; at base no gauge exists (FAIL);
  build passes when the gauge's reading equals the hand computation
  exactly and the concentration fixture moves the line the predicted
  direction.
- **SPLIT:** Design NOW (distributions, windows, display contract).
  Build: B-VII + own authorization.

---

# THE DOORS & PANELS LINE

## FAR-10 — THE THROAT RULE

- **STATE:** From V6 (wormhole simulation; graded: a visualization
  of lawful GR solutions — it transports nothing and proves nothing
  about the world; precisely Dell 31 Simulate's contract and the
  Smith tab's labeled-drawing rule). The mirror: DellMatrix's
  unbuilt shortcut is Reference (81) — its mouths exist as a Dell;
  the throat (traversal rules, receipts, what's allowed through) is
  the unbuilt part, owned by the main plan as G-08. Filing:
  PATTERN-grade. Readiness: **BOUNDED** — the rule is figured; the
  item cannot execute until G-08 exists.
- **DESIGN (full):** The rule, stated completely so G-08's design
  inherits it as a precondition: any shortcut mechanism's first
  receipt names **both mouths, what may pass, and its toll** —
  before the mechanism is designed further. Application protocol:
  (1) the rule binds at DESIGN time, not build time — a shortcut
  design lacking any of the three is refused under this rule at
  review; (2) the toll is named in the mechanism's own currency
  (what the traversal costs: authority spent, provenance lost,
  checks skipped — a toll of "none" must be argued, not assumed);
  (3) Part IV carries the rule only — Reference 81's design itself
  stays main-plan-owned (G-08, Part II territory); nothing here
  designs the throat.
- **DEPENDS:** G-08 (main-plan-owned, earlier sequence). Feeds any
  future shortcut/door design in H8.
- **ACCEPTANCE:** when G-08's design arrives, its first receipt
  carries mouths + passable set + toll named.
- **FAILING-FIRST:** filing-level: a G-08 design arriving without the
  triple and NOT refused is the failure state.
- **SPLIT:** Design NOW (the rule + protocol). Execution: bound to
  G-08's own circuit whenever it runs.

## FAR-19 — THE EQUILIBRIUM FINDER (blueprint N4)

- **STATE:** Classification: NEW single system (Nash equilibrium /
  fixed-point theorems — Brouwer/Kakutani, §2J: "where multi-party
  systems settle — panels, gates, deadlocks"). §7's bound: advisory
  computations for panels and gate standoffs, **NEVER rulings**.
  One-line specification only in the sources; no design, no worked
  use-case — both are designed here as a research package.
  Readiness: **RESEARCH**.
- **DESIGN (full):** A research design in two legs:
  1. **First use-case specification (the named study):** one real
     DellMatrix multi-party configuration written as a game —
     designated candidate: **dock contention** (multiple docked
     operators proposing into one Nursery gate: players = operators,
     strategies = propose/wait/escalate, payoffs = gate throughput
     vs. proposal survival, all definable from existing dock
     receipts). Panel composition and gate standoffs are the second
     and third candidates, in that order. The study's deliverable is
     the game written down with its payoff sources cited from real
     process records — an invented payoff table is a filing defect.
  2. **Solver selection study:** enumeration (exact, small games)
     vs. fixed-point iteration (larger games, receipted convergence
     in FAR-4 grammar) — scored on the use-case game's size; the
     study recommends, the build circuit decides with the
     recommendation on record.
  3. **Advisory bound (hard):** the finder's output is a receipted
     computation an authority may consult; it is never a decision,
     never a gate input with authority, and its receipts carry the
     advisory stamp on their face.
- **DEPENDS:** a first concrete case (leg 1 supplies it); panels/
  gates exist as processes, not yet as games. Feeds gate-standoff
  and panel deliberation support; COMBO-9 is its attention-side
  sibling.
- **ACCEPTANCE:** a worked case: a named standoff modeled, the
  computed equilibrium compared against the configuration the
  process actually settled into — or a constructed game whose known
  equilibrium the finder reproduces exactly.
- **FAILING-FIRST:** `equilibrium_finder_known_game` — constructed
  game with a known unique equilibrium; at base no finder exists
  (FAIL); build passes on exact reproduction, with the advisory
  stamp on the receipt.
- **SPLIT:** Design NOW (study legs + advisory bound). Execution:
  research circuit at step 7 — B-VII + own authorization.

## FAR-3 — RESONANCE MEDOIDS

- **STATE:** From V2 (K-means). The naive import is REFUSED in the
  study, on authority grounds: Group (82) + Scope (53) group by
  membership and meaning; a positional clustering would create a
  second grouping authority. The honest transfer: DISTANCE →
  RESONANCE (`_affinity`), MEAN → MEDOID (the most central EXISTING
  member). Classification: ADAPT. Ledger caution: `_affinity`
  (EQ-RES-002) is ACTIVE_UNVALIDATED — weights un-derived, its
  "harmonic" name has no harmonic-series basis. Readiness:
  **BOUNDED** (seed/K selection; _affinity validation state — the
  selection rule is designed here as a proposal with its decision
  owner named).
- **DESIGN (full):** An advisory grouping instrument, fully
  specified:
  1. **Iteration (Lloyd's shape, substituted):** assign each member
     to the nearest seed by resonance distance `d = 1 − _affinity`;
     recompute each cluster's medoid (the existing member minimizing
     total intra-cluster distance); repeat until stable. Stability
     is reported in FAR-4 grammar (rounds, moves per round, final
     stability) — the convergence receipt is part of the output,
     not an extra.
  2. **Output discipline (hard):** results enter ONLY as Nursery
     proposals (Gate Economy). The instrument proposes groups; Group
     (82) remains the authority that makes them. No output path may
     write a group directly — that refusal is the design's reason to
     exist.
  3. **Seed/K selection (proposed rule, Director decision):**
     deterministic seeding — initial seeds are the K members with
     the highest total affinity to the field (the field's own
     medoid candidates), so runs are reproducible by construction;
     K is bounded by a stated budget on the run's receipt (declared
     bounds), with K-sensitivity reported across a small K range
     rather than a single K asserted. Alternate (k-means++-style
     randomized seeding) is rejected for this instrument:
     reproducibility outranks spread here, and seed-sensitivity
     honesty (below) covers the local-optimum risk.
  4. **Seed-sensitivity honesty:** runs under perturbed seeds are
     reported alongside the canonical run — different seeds' results
     are shown, not hidden (the local-optimum honesty V2 teaches).
  5. **Affinity dependency:** the instrument inherits EQ-RES-002's
     ACTIVE_UNVALIDATED state on its face — every output receipt
     names the affinity version + its validation state.
- **DEPENDS:** `_affinity` (exists, unvalidated); the Nursery
  proposal path (exists). Feeds Group (82) with proposal-grade
  groupings only.
- **ACCEPTANCE:** a run over a recorded field: convergence receipt
  shows PERIOD-1 settling within budget; every output lands as a
  Nursery proposal (none as a group); seed-sensitivity results
  reported.
- **FAILING-FIRST:** `medoids_proposals_only` — at base no instrument
  exists (FAIL); build passes when the fixture run settles PERIOD-1,
  the proposal sink contains ONLY proposals (a direct group write
  fails the test outright), and the sensitivity annex is present.
- **SPLIT:** Design NOW (algorithm, output discipline, seed/K
  proposal). Build: B-VII + Director decision on the seed/K rule +
  own authorization.

## COMBO-9 — BET-SIZED ATTENTION (filing note, not a FAR item)

COMBO-9 (Kelly × Nursery ranking) is recorded in §7's doors & panels
line as a PROJECTION-grade display candidate for the Psalm Matrix. It
carries no FAR number and no package here; its refinement belongs
with the Psalm Matrix / Nursery ranking work (Part II territory,
cross-filed with V-10 in the Vision plan). Recorded so the line is
complete and the item is not silently dropped.

---

# THE RESEARCH LINE (standing programs)

## FAR-7 — THE PROJECTION QUESTION

- **STATE:** From V4's mirror (one 5D structure presenting as
  gravity + a force + a leftover). Filing: the Far Plan's standing
  research program, "KK-shaped and firewall-disciplined." The
  control group already exists: the firewalls — resonance/affinity/
  Verita kept separate ON EVIDENCE (ledger R4-A5: three parallel
  0..1 overlap authorities, RECONCILE-DON'T-MERGE; R4-A6: "harmonic"
  names three mechanisms, no semantic merge — mathematics itself
  keeps Jaccard, cosine, and correlation as separate citizens,
  blueprint §3). HD-5 (Noether's question) is this program's
  sharpest instrument. Readiness: **RESEARCH** — a standing program;
  by design it has no completion state.
- **DESIGN (full):** The program charter, complete:
  1. **The question (per pair):** for each pair of DellMatrix
     mechanisms that LOOK separate — one structure in two views, or
     two structures? — answered with tests, never by rhyme.
  2. **Pair-study protocol:** a pair study delivers exactly one of
     two receipts: (a) MERGE — a stated isomorphism under which both
     views' behaviors are reproduced; or (b) KEEP-SEPARATE — the
     distinguishing test on record. No third outcome; "they feel
     similar" is not a receipt.
  3. **Control group:** the firewalls (R4-A5/R4-A6) are the
     adjudicated exemplars — their receipts are the format's proof
     of feasibility, and any merge proposal must explain why it is
     not the firewalls' case.
  4. **HD-5 instrument (designed):** the symmetry inventory method —
     for a named subsystem, enumerate its transformations, test
     which quantities survive them, and file the conserved
     quantities as candidates for FAR-15's auditor to check
     operationally. HD-5's home receipt lives here; its operational
     half lives in FAR-15.
  5. **Pair queue (seeded):** beyond the control group, pairs enter
     the queue only when a lane files a pair-study proposal naming
     the two mechanisms + the suspected isomorphism or the
     distinguishing test to run. The queue is deliberately not
     pre-populated by speculation.
- **DEPENDS:** the ledger's firewall record (exists). Feeds FAR-15;
  the Completeness Law's duplicate-authority vigilance.
- **ACCEPTANCE:** per-pair receipts in the protocol's two forms.
- **FAILING-FIRST:** program-level: a merge executed on rhyme
  (similarity without a stated isomorphism + reproduced behaviors)
  is the failure state the charter exists to prevent.
- **SPLIT:** Design NOW (the charter). Execution: standing — each
  pair is its own named study, authorized individually; the program
  itself never "completes."

## FAR-12 — FORMALIZATION AS THE TOP RUNG

- **STATE:** From V5 — the claim that CHECKED OUT: the short's
  Navier–Stokes story verified against its cited Quanta article
  (~10,000 autonomous agents, a human structural strategy, a proof
  FORMALIZED IN LEAN — machine-checked; priority contested; ONE
  named human step outstanding: verifying the Lean statement is
  logically equivalent to the Clay problem statement). Grade:
  REPORTED + MACHINE-CHECKED, not "prize awarded." Classification:
  ADAPT (the ladder's horizon, not a build). §7: parse-verified
  seeds are the seed-form at home. Readiness: **RESEARCH**.
- **DESIGN (full):** The rung, defined completely:
  1. **Rung definition:** MACHINE-CHECKED — a chain whose every step
     a checker re-verifies, with the **equivalence duty** named
     beside it: the formal statement must be shown to say what the
     claim asked. A machine-checked proof of the wrong statement
     does not reach the rung.
  2. **Candidate-selection protocol (designed):** a home claim is a
     candidate iff (a) it exists in formalizable shape — parse-
     verified seeds are the seed-form (a claim whose statement
     already survives the program's own parser verbatim); (b) its
     falsifier is statable in the same formalism; (c) the
     equivalence duty is dischargeable by named humans/processes.
     The first candidate selection is a named study under this
     program; no candidate is pre-claimed here.
  3. **Equivalence-duty protocol (designed):** the Reader's
     Two-Readers rule applied to formalization — two independent
     readers verify the formal statement against the natural claim,
     blind; disagreements are receipted and block the rung.
  4. **Standing caution (carried on the rung's face):** V5's cascade
     warning (LM-7's dangerous direction) — infinitely many lawful
     layers whose combination exits the category; formalization
     depth is not the same as truth.
- **DEPENDS:** a first candidate claim in formalizable shape. Feeds
  the evidence ladder's horizon definition; FAR-5's claim discipline
  is its lower-rung sibling.
- **ACCEPTANCE:** a first home claim carried to the rung: a
  machine-checked chain plus a discharged equivalence duty, both
  receipted — or the honest record that no current claim survives
  the attempt, and why.
- **FAILING-FIRST:** `formalization_equivalence_duty` — a fixture
  claim with a subtly non-equivalent formalization; at base no
  protocol exists to catch it (FAIL); the protocol passes when the
  Two-Readers equivalence check blocks the fixture and passes a
  faithful one.
- **SPLIT:** Design NOW (rung, protocols, caution). Execution: the
  candidate-selection study is a named research circuit at step 7 —
  B-VII + own authorization.

---

# PROVISIONAL RESEARCH REGISTER (quarantined from §4 per SD-GP-01;
# no closing obligation attaches to any item below)

## G-29 — ESTIMATION COVERAGE (a closed finding)

- **STATE:** GAP CONFIRMED WITHIN CENSUS SCOPE — stated exactly: the
  original absence assertion (HD-4) was WITHDRAWN as stated (audit
  F2: it rested on a stale, partial inventory) and replaced by two
  censuses. (1) Scoped census at pinned main `16e5131f` (form/ only,
  419 .py): no implementation; fragments only. (2) Comparison pass
  at pinned main `d59649a8` — whole repo (597 .py + 57 .js),
  textbook + disguise batteries, every plausible hit inspected in
  context: NO true estimator anywhere; nine deterministic fragments
  catalogued. (3) DIRECTOR DUAL-CENSUS CONVERGENCE
  (G29-DUAL-CENSUS-01): the Director's independent GitHub census and
  Uni's census AGREE ON EVERY ROW. Register status: **GAP CONFIRMED
  — SCOPED TO THE PINNED REPOSITORY CENSUS.** The finding is
  falsifiable — a mechanism meeting the three-part test under any
  name overturns it — and X11 retains full authority to revisit it
  (step-1.5 census). Strongest reuse candidates (Director):
  SlopeTracker's observation history, duobeta_learn's evidence
  accumulation, linear_algebra's matrix operations (reuse
  opportunities, NOT modification authorization).
- **DESIGN:** None required — G-29 is a FINDING, and the finding is
  delivered. Its design content is the census method itself
  (complete): two batteries built to defeat the failed-search trap
  (textbook terms + disguises), contextual inspection of every hit
  against the three-part estimator test, caller checks, dual
  independent execution, convergence record. The capability the gap
  points to is FAR-13's (packaged above), not G-29's.
- **SPLIT:** Closed as a finding. No build, no further standalone
  search unless contradictory evidence appears or X11 revisits at
  step 1.5 (a revisit right, not a debt).

## G-30 — THE NERVE'S χ (the register filing of FAR-17)

- **STATE:** COMPUTED; THE NAIVE FORMULA CORRECTED. FAR-17's
  provisional-register seat (SD-GP-01 quarantined it here from §4;
  provenance and cross-references preserved). The register text and
  the FAR-17 receipt agree exactly: pattern-convention χ = 1 at
  R = 1/2/3, complete counts, two cross-checking methods in full
  agreement (one shared enumeration framework — computation
  cross-checked, definitions not independently validated); the
  closed convention reaches χ = 1 only when counted to all orders
  (R=1: 7 − 21 + 35 − 35 + 21 − 7 + 1 = 1); χ = 1 is the OBSERVED
  BASELINE for the tested patches; other configurations may
  legitimately differ. Register status verbatim: "a bounded,
  completed sandbox computation with a receipt — not a capability,
  not a register promotion."
- **DESIGN:** Identical to FAR-17's (packaged above, including the
  extension matrix and the independent-execution-pass leg).
  **Movement rule:** any future movement happens to both filings at
  once or neither — the register and the FAR line never drift apart.
- **SPLIT:** As FAR-17.

## G-31 — FLOW UNIFICATION

- **STATE:** The register entry as filed (Director FLOW ARCHITECTURE
  REVIEW, 2026-11-14): PROPOSED — one flow contract, multiple
  execution paths, identical observable semantics; NOT an operative
  closure requirement, NOT part of §4's closing condition. Since
  filing, its first contract circuit ran end to end:
  G31-CONTRACT-01 design CONFIRMED by the Director (one vocabulary
  in `control_runtime.FLOW_CONTRACT`; Profile A canonical chain of
  nine; Profile B correspondence composition — `>`/`>>` execute, the
  other seven refuse by name under D-6 FlowRefusal; C-2 persistence
  contract: generations minted only by the checkpoint authority),
  and G31-CONTRACT-02 IMPLEMENTED it, MERGED as PR #417 (head
  `a20997d`, merge `b39c6a0`, 2026-11-14; failing-first 12/20 →
  20/20; canonical regress 286/286; exact-head CI all green;
  post-merge live REPL refusal proof on merged main). The register
  text's "no implementation is authorized by this entry" was
  superseded by those circuits' own authorizations, not by the
  entry itself. Product seats: `form/mandell/control_runtime.py`
  (FLOW_CONTRACT + FLOW_PROFILES), `form/mandell/flow_executor.py`
  (FlowRefusal), `form/repl.py` (DCC-IV branch), `form/mandell/
  g31_contract_test.py` (20 checks).
- **DESIGN (the unbuilt remainder, full):** two ruling items from the
  filing (Q-FL1–Q-FL4) remain open research, designed here:
  1. **Q-FL2 — demand-flow pilots at Nursery intake (bounded):**
     pilot spec — demand/backpressure signalling at the intake door
     ONLY, with existing capacity enforcement preserved byte-for-byte
     in behaviour (the pilot observes and signals; it does not
     enforce anything new); success measured against the flow
     census's F-N1 (demand/backpressure) candidate shape; the
     Director's correction is carried on the pilot's face: bounded
     FIFO ≠ deadlock freedom.
  2. **Q-FL4 — hidden-flow audit:** an audit tracing ACTUAL
     dependencies (call/data flow as executed) against declared
     flow contracts; method — instrumented runs over the contract
     fixtures, dependency edges extracted from execution, diffed
     against FLOW_PROFILES; the filing's caution is the method's
     first rule: a projection label is not a taint system — the
     audit reports executed edges only, never inferred taint.
  Feeds FAR-15 (flow records are the Conservation Auditor's
  substrate); the flow census's new-flow candidates (F-N1
  demand/backpressure, F-N2 token/Petri, F-N3 channel/Kahn, F-N5
  watermarks) advance only if Q-FL2/Q-FL4 advance.
- **REMAINING STEP for the built scope:** the authorities'
  credit/certification decision for G-31 (merged ≠ certified). That
  decision is being sought in the program's grouped seven-circuit
  credit backlog (PR #417 rides it, in Part I's lane per the
  Eight-Part map's fold-in inventory) — **this Part does not
  double-ask it.** Q-FL2/Q-FL4 are separately BOUNDED research,
  authorized only by their own future circuits.
- **SPLIT:** Built scope: complete, merged, awaiting credit (not
  this Part's ask). Research remainder: designs NOW (above); builds
  B-VII + own authorization.

---

# CARRIED ITEMS (no FAR number)

## §117 / G-10 — EXCHANGE PHASE G (cloud perspectives) — DECLINED

Register #117: DECLINED (deferred by adoption, Ace 2026-10-26);
historical record, not reactivated. This Part carries it as
DECLINED with its history intact. **No design work is proposed and
none was done.** Reactivation would be Ace's act; nothing in this PR
asks for it.

## §P07 — 30-VIDEO PLACEMENT P07 (model editing / hyperchaotic control) — DEFERRED

Per the Grand Plan Addendum (30-video upgrades, 2026-11-17) §3:
P07 is DEFERRED, all lanes, excluded from the addendum by design;
its material is retained only as negative examples inside P03/P04
(Part I territory). **No design work is proposed here.** Revisit
condition: Director un-deferral. Until then P07 stays exactly where
the Director put it.

---

*End of FAR design packages. Verification: every FAR-1..20 item, the
Reader, G-29/G-30/G-31, COMBO-9, P07, and #117 appears above with
state, design, acceptance, failing-first, and split — cross-checked
against the Unified Edition Part IV closing summary table (24
entries: Reader + FAR-1..20 + G-29..31).*
