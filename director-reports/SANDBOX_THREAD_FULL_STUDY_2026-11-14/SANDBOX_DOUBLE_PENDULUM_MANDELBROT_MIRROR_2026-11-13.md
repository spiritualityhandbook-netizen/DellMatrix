# SANDBOX STUDY — THE DOUBLE PENDULUM × THE MANDELBROT
## Two chaos-and-stability machines, mirrored into
## DellMatrix, Mandell, and DuoBeta — 2026-11-13

Status: **SANDBOX STUDY.** All pendulum numbers below
were simulated live in this session (RK4 integration of
the standard double-pendulum equations, equal masses
and lengths, g = 9.81). Ace's direction: double
pendulums and the Mandelbrot both have chaos and
stability — research them, then mirror to DellMatrix,
Mandell, and DuoBeta.

---

# 1. WHAT THE DOUBLE PENDULUM TEACHES THAT THE
#    MANDELBROT ALONE COULD NOT

The Mandelbrot classifies PARAMETERS (which c?). The
double pendulum classifies STARTING STATES (which
release?) under FIXED parameters. Same machine, two
pendulum arms coupled at a joint, each feeding the
other. Its phase space is MIXED — not calm or chaotic,
but an archipelago: islands of regular, predictable
motion in a sea of chaos, at the SAME settings.

Measured in this session (twin runs: two releases
differing by 0.000001 rad):

- **Low energy** (small swings, θ = 0.1 / 0.15): after
  20 simulated seconds the twins' gap is still 0.0000
  rad at 4-decimal precision. An island. The motion is
  quasi-periodic — two incommensurate rhythms braided,
  stable forever.
- **High energy** (big throws, θ = 2.4 / 2.8): the same
  hairline gap grows to 0.5 rad in 18.85 s and to full
  decorrelation (1.23 rad) by 20 s. Lyapunov estimate
  λ ≈ 0.70 /s — the gap multiplies by e every ~1.4 s.
  The sea. Prediction has a HORIZON: ~1/λ seconds of
  foresight, after which the honest verdict is
  "unknowable from here," however good the model is.
- **Basin mini-map** (24×24 starting angles, arms
  released from rest, 8 s budget; class = does arm 2
  complete a full flip?): 242 of 576 starts flip.
  Neighbor disagreement — the fraction of adjacent
  starts with different fates — is **24.3%**: at this
  resolution, a quarter of all neighboring pairs
  DISAGREE about destiny. The border between flip and
  no-flip is not a coastline; it is lace. That is the
  measurable signature of a fractal basin boundary.
- **Stickiness** (established dynamics, stated as
  mechanism): near island shores, chaotic orbits imitate
  regular motion for very long stretches before
  escaping. A sticky orbit under a short budget reads
  SETTLED — and is not. The budget problem of the
  Mandelbrot studies, now with a mechanism and a name.

The unification, stated once: Mandelbrot bulbs and KAM
islands are the same species — PERIOD-LABELED REGIONS
OF STABILITY inside sensitive space, organized by
fractions/ratios, with sticky, lace-like shores. And
the shared law both machines teach:

**STABILITY IS NEVER A PROPERTY OF THE SYSTEM. IT IS
A PROPERTY OF (SYSTEM × REGION × STARTING STATE ×
BUDGET). Any verdict missing one of the four is
unfinished.**

# 2. MIRROR — DELLMATRIX (the program)

**M1. Behavior maps come in TWO KINDS, and the plan
now needs both.** Parameter maps (Mandelbrot kind:
vary the knobs) and BASIN maps (pendulum kind: fix the
knobs, vary the starting state). Growth's fate depends
on its settings AND on the field it starts from —
path dependence is not an anomaly, it is mechanics.
A process certified calm from one starting field is
certified for THAT basin only. (Folded into the
Afterplan §5B preamble on Ace's placement order.)

**M2. THE TWIN-RUN DIVERGENCE RECEIPT (new instrument,
ADAPT-grade).** For any iterated process: run it twice
from states differing by a hair, measure the gap's
growth rate λ̂ from the receipts. λ̂ ≈ 0 or negative =
contractive/stable: forecasts hold. λ̂ > 0 = expansive:
chaos present, and 1/λ̂ is the process's TRUST HORIZON
— the number of rounds a prediction may be trusted,
stamped on the receipt like a budget. Process-agnostic,
cheap, computable from state sequences the program
already produces. This is the Lyapunov exponent,
naturalized as a DellMatrix receipt.

**M3. LOAD IS A REGIME AXIS.** The pendulum flips
regime with total ENERGY, not with any defect. DellMatrix
maps must carry a load axis (proposal inflow, outcome
rate, growth drive): calm at low load and chaotic at
high load is a REGIME MAP, not a bug report. Profile
reads regime, not just state.

**M4. COUPLED PAIRS ARE THE HONEST UNIT.** Neither
pendulum arm has a behavior of its own; the pair does.
Where two DellMatrix loops feed each other (growth ×
learning; ranking × freshness decay; demand × supply),
single-system maps understate the truth. Map the PAIR
where a coupling exists; single maps only where a
process is provably uncoupled.

# 3. MIRROR — MANDELL (the language)

**M5. A chain is an orbit; the field is its starting
state.** The same seed executed against two nearly
identical fields is two twin runs. In contractive
regions they converge — the seed ABSORBS context
differences (a stabilizer seed). In expansive regions
they diverge — the seed AMPLIFIES whispers (a chaotic
seed: powerful, dangerous, never to be run unreceipted
near a border). **Seed sensitivity class — CONTRACTIVE /
NEUTRAL / EXPANSIVE — is measurable from twin-run
receipts** and belongs on the orbit receipt beside
X7's TERMINATED / PERIOD-k / NO-VERDICT classes.

**M6. Branch is a joint.** 60[Branch] reads a condition
and takes one side; in expansive territory a hairline
condition difference at the joint flips the entire
downstream trajectory — the pendulum's elbow, inside
the language. Route (59) chooses the road; the twin-run
receipt says how much the road amplifies weather.
Chains that pass through many joints in expansive
regions carry compounding horizons: the chain's trust
horizon is set by its most expansive joint.

# 4. MIRROR — DUOBETA (the learning pair)

DuoBeta is a genuinely COUPLED pair, and the pendulum
is its portrait: the evidence stream drives the learned
rankings; the rankings steer selection; selection
decides which outcomes ever get OBSERVED — **learning
changes what it is allowed to see.** That is the
elbow joint. Consequences, each measurable:

**M7. Mixed regimes are DuoBeta's expected geography.**
Islands where learning settles (rankings converge;
twin-run λ̂ ≤ 0), seas where it chases its own tail.
X3's oscillation hunt is the search for one pathological
island class (period-k flip-flop). The twin-run receipt
(M2) is the general instrument; oscillation is its
periodic special case. Together they give DuoBeta its
first stability diagnostics of any kind.

**M8. THE GATE IS A DAMPER.** MIN_EVIDENCE = 3 is, in
pendulum language, inertia/damping: it refuses to let
single outcomes swing the arm. Damping is TUNABLE and
its effect is mappable — behavior maps over (evidence
inflow rate × gate threshold) would show where learning
is responsive-but-calm vs frozen vs thrashing. The
gate stops being a magic number and becomes a chosen
point on a drawn map.

**M9. STICKINESS EXPLAINS THE ROLLBACK GAP.** Rankings
can sit still for long stretches (sticky shore) and
then flip on one threshold outcome. A rollback design
that assumes gradual drift will miss the flip; rollback
must key on RECORDED ORBIT POINTS (checkpoints before
regime changes), which is exactly the Afterplan §5B.1
RETURN identity, now with a mechanical reason.

**M10. DuoBeta gains a TRUST HORIZON.** With λ̂ measured
over its own replay, advisory influence can carry an
honest stamp: "these rankings are stable for ~N rounds
at the current evidence inflow." Beyond the horizon,
influence continues (DuoBeta is advisory; truth is
untouched either way) but the stamp says what it is:
past-horizon advice is weather, not climate.

# 5. WHAT IS *NOT* CLAIMED

No DellMatrix process has yet been measured for λ̂;
M2/M5/M7 are instrument DESIGNS with a working physical
exemplar, not results. The pendulum's numbers are the
pendulum's. DellMatrix quantities earn their own
measurements when the probe circuits (Afterplan §5B.2)
run — which is precisely what the falsification paths
there are for. PATTERN-grade only: Huygens sync
(coupled pendulums lock through a shared beam) as a
picture for cadence locking between authority cycles
and program beats — noted, not built on.

— Sandbox study, 2026-11-13. Placements made same day
under Ace's order: Afterplan §5A (X1 sourcing), §5B
(atlas family, mirror identities, probe family,
two-map-kinds preamble). —
