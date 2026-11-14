# G-29 ESTIMATION CENSUS — THE COMPARISON PASS
## Ordered by Ace, 2026-11-14 ("Do the census to compare"), following
## the Sandbox Director's G-29 assessment (UNKNOWN, correctly held).
## Executed by Uni, read-only, sandbox side chat.
## Pinned baseline: main d59649a8b23a5fb985c9fe2ba8711450fedd76d1
## (current tip at census time; the earlier scoped census used
## 16e5131f — main moved between the two passes, noted for the record).

## QUESTION
Does DellMatrix anywhere possess the machinery to ESTIMATE
uncertain information — a state carried under noise, revised
by observations, with its uncertainty reported — in any of
the three named forms (Kalman filtering, Bayesian updating,
least squares) OR under any other name or shape?

## METHOD (built to defeat the failed-search trap)
Corpus: the WHOLE repository — 597 .py + 57 .js/.ts files
(form/, src/, preform/, gui/, ops/, docs/ code, director-
reports tooling). Two batteries, then CONTEXTUAL INSPECTION
of every plausible hit (the mechanism read, not the name):
- Battery A (textbook): kalman · bayes · posterior ·
  likelihood · covariance · lstsq · least-squares · polyfit
  · pseudoinverse · normal equations · numpy · scipy.
- Battery B (disguises): predict* · confidence · uncertain*
  · smoothing · moving average · interpolat* · extrapolat*
  · fit/trend/slope definitions · weighted/running average ·
  residual · expected/expectation · mean/average helpers.
Classification standard: a TRUE ESTIMATOR maintains (1) a
state estimate, (2) an explicit noise/uncertainty quantity,
(3) an update rule that revises both from new observations.
Anything missing an element is a FRAGMENT, catalogued with
what it actually is. Callers checked for every fragment.

## RESULT — BATTERY A: EMPTY
Zero hits, repo-wide, in code files, for every textbook
term. No Kalman filter, no Bayesian updater, no least-
squares fitter, no covariance tracking, no numpy/scipy
anywhere. (The earlier form/-only scoped result replicates
exactly on the wider corpus.)

## RESULT — BATTERY B: NINE FRAGMENTS, NO ESTIMATOR
1. **inspire_pack.SlopeTracker** (form/dell_matrix/
   inspire_pack.py:120+): keeps ≤48 score samples per unit;
   slope() = Δscore/Δt over the LAST TWO samples only.
   A discrete derivative — a rate reading from exact
   samples. No fit over the window, no noise model, no
   uncertainty. Callers: open.py slopes_report. FRAGMENT
   (the nearest miss: it reads a changing quantity's trend).
2. **duobeta_learn learned score** (form/mandell/
   duobeta_learn.py:34-101, its own comments): a LINEAR
   COUNT (success − failure − blocked), saturating squash,
   gate at MIN_EVIDENCE = 3. Evidence accumulation by
   counting — the deterministic skeleton of belief revision
   with no probabilities, likelihoods, or uncertainty.
   Callers: program ranking/selection (advisory). FRAGMENT.
3. **correction_graph confidence classes** (form/mandell/
   correction_graph.py:81+): _confidence_for assigns one of
   three LABELS (STRONG / CANDIDATE / UNKNOWN) by provenance
   rules. Deterministic classification, by design.
   NOT estimation (epistemic labels, honestly kept).
4. **ProbabilisticShell** (form/dell_matrix/
   decision_shells.py:193): stores a probability scalar and
   echoes it as a grade. No update rule exists. FRAGMENT
   (a probability kept, never revised).
5. **canonical.py / activation.py "uncertainty" values**:
   minted by formula (0.25·i, 0.3·i), labeled
   PROJECTED_NOT_FACT. Placeholder stamps on projections.
   NOT estimation — and honestly labeled as not-fact, which
   is the correct behavior for a placeholder.
6. **Percentile linear interpolation** (docs/perf_*
   harnesses): descriptive statistics inside measurement
   instruments. NOT a state estimator (H10 territory).
7. **oracle_protocol.js** (src/core/, Era-1 frozen):
   "deferred prediction with horizon + direction" — a
   prediction LEDGER (write a prediction, score it later).
   Bookkeeping about predictions, not estimation from
   noise. FRAGMENT (historical; frozen with src/).
8. **Noise/signal shapes**: nature_code.gaussian (an RNG
   sampler), fourier.gaussian_pulse (a waveform). The raw
   ingredients of noise modeling, used for generation and
   display only. NOT estimation.
9. **linear_algebra.py / eigen_stability.py**: exact 2×2
   matrix algebra (inverse, eigenvalues) and stability
   classification of KNOWN systems. Exact mathematics —
   the kind of toolkit a least-squares fitter would build
   on, never used to fit anything. NOT estimation.

Also inspected and cleared: nbd_engine (self-described
"not probabilistic forecasting — deterministic
recomputation"); resonance diffusion (deterministic score
propagation, no uncertainty); gui/server.py confidence
(a stored field passed through for display).

## VERDICT (comparison against the earlier scoped search)
**CONFIRMED AND EXTENDED.** The gap survives a search
designed to find the capability under any name, in any
directory, wearing any disguise: DellMatrix contains NO
true estimator. What it contains is a coherent set of
deterministic neighbors — counting, labeling, differencing,
storing — each honest about what it is. The program's
epistemics are deliberately exact-state: where uncertainty
exists it is STAMPED (PROJECTED, UNKNOWN classes) rather
than MEASURED. That is a design posture, and G-29 is the
record of its cost: nothing in the building can yet say
"the animal is probably HERE, ± this much."

STATUS RECOMMENDED: the gap is established to census
standard FOR THE SEARCHED SCOPE (this repository, pinned
SHA d59649a8, the method above). FAR-13 (the Estimator)
stands as the implementation path, and the nine fragments
are its reuse inventory — most valuably SlopeTracker's
sample window (a least-squares slope over its 48 samples
is a one-function upgrade), DuoBeta's evidence counts (the
counting skeleton a Bayesian restatement would formalize,
cf. blueprint E2), and the 2×2 algebra toolkit.
The step-1.5 X11 census may re-run this census inside the
full component census; nothing here binds it.

## WHAT WOULD CHANGE THIS VERDICT
A mechanism, anywhere in the corpus, maintaining a state
estimate AND an uncertainty quantity AND an update rule
revising both — under any name. The batteries were built
to surface one if it exists; a reader who finds a candidate
the batteries missed falsifies this census cleanly, and
the census asks to be falsified that way rather than
believed.

---

## CONVERGENCE ADDENDUM — DIRECTOR DUAL-CENSUS MIRROR, 2026-11-14
Directive G29-DUAL-CENSUS-01 (MODE B): the Director's
independent GitHub census and this census agree on every
mirror row — Kalman filtering, Bayesian updating,
least-squares fitting, covariance tracking: NOT FOUND by
either; probability representation: PRESENT in both;
uncertainty labels: PRESENT in both; observation-driven
estimator: NOT DEMONSTRATED (Director) / NOT FOUND (Uni)
— CONVERGENT. Shared evidence baseline:
d59649a8b23a5fb985c9fe2ba8711450fedd76d1.
DISPOSITION: **G-29 GAP CONFIRMED — SCOPED TO THE PINNED
REPOSITORY CENSUS** (advanced from UNKNOWN). The finding
remains falsifiable exactly as stated in this report's
final section; X11 retains authority to revisit it; the
nine-fragment inventory stands as FAR-13's reuse base,
with SlopeTracker, duobeta_learn, and linear_algebra named
by the Director as the strongest candidates (reuse
opportunities, not modification authorization). No
estimator implementation, product-code change, or merge is
authorized by this disposition. No further standalone G-29
search is required unless contradictory evidence appears
or X11 revisits the coverage.
