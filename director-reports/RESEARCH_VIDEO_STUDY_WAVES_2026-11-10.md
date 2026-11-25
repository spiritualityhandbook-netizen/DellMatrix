# VIDEO STUDY — Waves, Strings, Chaos (Ace-flagged, 2026-11-10)

Researcher: Uni subagent (worker-reported evidence). Method per AGENTS.md
§20/§21: primary sources preferred, claims labeled FACT / DERIVED_FACT /
EXTERNAL_EVIDENCE / PROJECTION / UNKNOWN. Date of research: 2026-11-10.

**Method limitation (stated once, applies throughout):** full transcripts
were NOT obtainable — youtube-transcript-api returned IpBlocked for all
three videos and yt-dlp hit YouTube's bot check from this network. Content
below is reconstructed from (1) the creators' own official descriptions and
chapter lists (primary), (2) the software's official site and GitHub
repositories (primary), (3) independent secondary coverage (MathWorks,
MDPI, industry analyses). Spoken-word-level claims are therefore
UNVERIFIED; structural claims (what each video demonstrates, what software
it uses, what method it applies) are verified against primary sources.

---

## 1. VIDEO 1 — "Creating Logic using Waves: Photonic Gates" — Huygens Optics

URL: https://www.youtube.com/watch?v=ln0zZcQXv38

### Content (from official description + chapters — FACT, creator-published)
- Subject: how Mach–Zehnder-type photonic logic devices work at the wave
  level, shown entirely through wave animations made in **WaveDude**
  (see §4 — this is the freeware Ace asked about).
- Chapters: intro/WaveDude info (00:00) → logic gates explained (01:37) →
  XOR optical gate (02:23) → the evanescent field and its role (04:05) →
  energy transfer between two optical fibers (07:46) → coupling length
  (09:10) → building a "neat" OR gate (11:13) → building an XOR gate
  (14:14) → extro + WaveDude development (15:12–17:03).
- The physics demonstrated: two coherent wavefronts in coupled waveguides
  exchange energy through the evanescent field; the coupling length sets
  where the energy ends up; relative phase at recombination gives
  constructive/destructive interference — i.e., an XOR-like truth table
  falls out of interference alone, and directional couplers + phase
  control yield OR/XOR gate behavior in simulation.

### Evidence quality
- Demonstrated-in-simulation: the gate behaviors are shown in a real
  numerical wave solver (see §4), not asserted verbally. Strong as a
  *visualization of real wave physics* (the solver integrates the 2D wave
  equation with a refractive-index field).
- NOT demonstrated: a physical device built by the creator in this video;
  the claims rest on the simulation being faithful, which for linear wave
  propagation in 2D is well-founded textbook physics (EXTERNAL_EVIDENCE).
- The creator (Jeroen Vleggaar, Huygens Optics) is an optics engineer
  whose channel's simulation lineage is documented and reused by others;
  the video description links real industrial context (Lightmatter,
  imec photonic integrated circuits, Wim Bogaerts/UGent course material).

---

## 2. VIDEO 2 — "the most beautiful idea in physics we can't prove" — 4phy

URL: https://www.youtube.com/watch?v=xwaJQPytXuY

### What the "idea" actually is (FACT, from the official description)
**String theory.** Every particle is the same tiny vibrating string;
electron, quark, and photon are "different notes from one instrument."
The video is built around Michio Kaku's *The God Equation*, and is
structurally honest about its own subject (creator's words in substance):
the theory needs ten dimensions, permits ~10^500 possible universes, and
has no direct experimental evidence; it may end up beside Newton and
Einstein or as a footnote.
- Historical spine used: Pythagoras' string harmonics → Veneziano's 1968
  formula turning out to be Euler's beta function → Nambu/Nielsen/
  Susskind reading it as vibrating strings → Schwarz & Scherk (1974)
  identifying the graviton mode. Critics Smolin and Woit are cited.
- Supporting set-pieces the description lists: QED's ~1-part-in-a-trillion
  accuracy, GPS relativity corrections, 2015 gravitational-wave detection,
  Planck length.

### Actual status in physics (EXTERNAL_EVIDENCE, standard record)
- String theory remains **unproven and unrefuted** after ~55 years: no
  experimental confirmation of strings, extra dimensions, or
  supersymmetry at accessible energies; the landscape (~10^500 vacua)
  undermines unique prediction. Its strongest results are mathematical
  (e.g., AdS/CFT-type dualities with extensive internal checks), which is
  evidence of consistency, not of physical truth.
- The video is a competent popularization, and its honesty about the
  catch is above average for the genre. It is a narrative source, not
  evidence for any engineering decision.

---

## 3. VIDEO 3 — "Pushing Simulations to the LIMIT to Turn Chaos into Order" — Drew's Campfire

URL: https://www.youtube.com/watch?v=8jVogdTJESw
Code: https://github.com/drewscampfire/Drew-s-Campfire-Videos (verified via
GitHub API listing: "contains the code that generates the animations for
my YouTube channel, Drew's Campfire")

### The method (FACT, from official description — this is the "chaos into
order" technique, and it is NOT what the title might suggest)
- The system is the **double pendulum** (deterministic chaos textbook
  case). There is no order *imposed* on chaos; order is *found* by
  mapping it:
  1. **Parameter-space sweep**: simulate an enormous grid of double
     pendulums, one per pixel, spanning all initial positions.
  2. **Per-run scalar classification**: each run is reduced to an
     observable (chiefly flip counts — a flip = either rod rotating past
     180°) and behavioral class (ordered vs chaotic-looking).
  3. **Render the grid as an image**: the classification field is itself
     a fractal containing **"islands of stability"** — regions whose
     pendulums stay ordered — including the counterintuitive finding of
     islands that flip repeatedly yet stay ordered, and chaotic-looking
     regions that never flip.
- Numerics: 8th-order Dormand–Prince Runge–Kutta (torchdiffeq `dopri8`),
  double precision, GPU-accelerated Python; rendering in Blender + Manim
  CE (both free/open-source). One zoom shot = **5.04 billion** pendulum
  simulations (42 s × 30 fps × 2000×2000 px), 70 simulated seconds each;
  the creator rented a bigger GPU because his RTX 3060 laptop would have
  needed ~105 days for that shot.
- **Validation practice (notable)**: the creator re-ran with varied
  gravity, rod-length ratios, masses, and solver tolerances (rtol/atol)
  and reports the qualitative features persist while exact shapes shift —
  a robustness differential, not a single pretty run.
- Credit chain: the "one pendulum per pixel" idea is credited to Sam
  Maksimovich's earlier double-pendulum fractal video. Independent
  corroboration of the video's content exists (Cleve Moler's MathWorks
  blog covers this video and the follow-up work it inspired).

### Evidence quality
- High for a YouTube production: explicit integrator, precision,
  tolerances, compute budget, parameter-robustness checks, public code.
  The fractal/stability-island phenomenon is consistent with known
  Hamiltonian phase-space structure (KAM-type islands), so the pictures
  are plausible physics, not artifacts — and the creator tested exactly
  the artifact hypothesis.

---

## 4. THE FREEWARE — WaveDude (Ace's specific question)

### Identity and lineage (FACT, primary sources)
- **WaveDude Next** — the tool used in Video 1. Author: **Alexander Gräf**,
  built in close cooperation with Huygens Optics. A 2D wave-optics
  simulator: place sources and optical parts (lenses, mirrors, fibers,
  GRIN lenses, zone plates, Bragg reflectors, and built-in **optical
  XOR/AND/OR gate parts**) on a canvas; it propagates the wave field in
  real time (field + time-averaged intensity side by side), with
  unlimited probes (point/line, graphs, CSV export), timeline scrubbing,
  and export to MP4/MOV/AVI/PNG/OpenEXR.
- **Numerics**: finite-difference 2D wave equation on a pixel grid with a
  spatially varying refractive index (scenes can be painted as images:
  red = refractive index, green = emitters, blue = absorption), GPU
  acceleration via OpenCL, CPU fallback, absorbing boundary rim.
- **License/price**: genuinely free software — **GPL-3.0-or-later**,
  source public. Repo: https://github.com/graealex/WaveDudeNext
  (verified: license field GPL-3.0, LICENSE.md present, ~249 stars,
  active). Downloads: https://wavedude.com and GitHub Releases — signed
  EXEs for **64-bit Windows 10/11**, needs .NET 10 Desktop Runtime (slim
  ~6 MB) or the bundled build (~139 MB). No Linux/macOS build.
- **WaveDude Classic ("WaveDude 2D")**: the original by **Jeroen
  Vleggaar** (the Huygens Optics creator himself), discontinued in favor
  of Next; same numerics.
- **WaveSimulator2D** — the ancestor both descend from: by **0x23 /
  DiffractionLimited**, https://github.com/0x23/WaveSimulator2D —
  Python + CuPy (NVIDIA GPU), same image-scene convention (red =
  refractive index ×100, green = sources/frequency, blue = absorption),
  ~352 stars. CAUTION: no LICENSE file was observed in its repo root —
  license status UNVERIFIED; treat its code as all-rights-reserved until
  checked. (Its README presents it as a shared community tool, but
  "public on GitHub" is not a license.)

### Direct answer for Ace — could DellMatrix use it?
- **Embed WaveDude Next into Studio/DellMatrix: NO — REJECT.**
  (1) Platform: Windows-only .NET/WPF desktop app; Studio is a local web
  GUI — there is no sane embed path. (2) License: GPL-3.0 copyleft would
  attach to any distributed combined work that links/bundles it.
  (3) It is a physics-teaching tool; its scene model (optical parts) is
  not DellMatrix's scene model (ideas/Dells).
- **Use it as an external freeware on Ace's own Windows machine: YES,
  zero-cost.** Making standalone wave visuals/posters/clips (e.g., for
  the NVIDIA deck or Nursery look-experiments) is ordinary use; program
  *output* (videos/images) is not GPL-encumbered. This is the correct
  way to "use the freeware" today.
- **Reimplement the technique inside Studio: YES — this is the real
  prize (see §6A).** The underlying update rule (leapfrog finite
  difference on the scalar wave equation with a per-pixel propagation
  speed and damping) is decades-old textbook numerics with many
  independent implementations; a WebGL2 fragment-shader version is a
  few hundred lines and runs at interactive rates on modest GPUs.
  Constraint: write it clean-room from the physics, do not port
  WaveDude's C# (GPL) or 0x23's Python (license unverified).

---

## 5. FOLLOW-UP RESEARCH — the substantive ideas

### (i) Interference / photonic logic — real? limits?
EXTERNAL_EVIDENCE (MDPI review literature; industry analyses; the
video's own linked industry context):
- **Real and demonstrated**: Mach–Zehnder interferometers are production
  silicon-photonics components. Interference genuinely computes: an MZI
  mesh performs unitary matrix–vector multiplication at light speed
  (this is what Lightmatter/Lightelligence accelerators sell — analog
  neural-net math, summation on a photodiode). Interference-only XOR in
  one MZI is a standard result; SOA-based all-optical NAND/XNOR gates
  are demonstrated in journals at 120 Gb/s class rates.
- **The hard limits (why there is no photonic CPU)**: photons barely
  interact, so *linear* interference gives no gain, no thresholding, no
  signal restoration. Consequences: poor cascadability and fan-out,
  accumulating insertion loss and phase noise (signals degrade after
  ~10–15 stages), AND/OR need a nonlinearity (Kerr, SOA, two-photon
  absorption) that is weak, power-hungry, or slow to recover. The
  industry's answer was to use interference for what it's good at —
  big analog weighted sums — and keep decisions in electronics.
- Design moral that survives translation to software: **superposition
  computes sums for free; decisions require an explicit threshold
  element; chained analog stages need periodic restoration or the
  signal rots.**

### (ii) Video 2's idea — status
Covered in §2: string theory; beautiful, mathematically deep,
experimentally unconfirmed; the video itself concedes this. No action
implied for DellMatrix beyond method (§6C).

### (iii) Video 3's method — what produces "order from chaos"
Covered in §3: nothing is *produced* — a deterministic system's
parameter space is exhaustively swept, each trajectory classified by a
cheap scalar observable, and the classification field is rendered as an
image, exposing fractal stability islands. The transferable algorithm
is: **sweep → classify per point → render the field**, plus
**robustness-check by perturbing solver parameters**.

---

## 6. DELLMATRIX MAPPING (classifications per AGENTS.md §21)

DellMatrix anchors used: resonance/pulse (Program.pulse → resonance),
the planned C13 Simulate cluster, the Plane-as-ROOM (3D) / SKY (2D)
display law ("visual, alive, never stagnant"), the §14 symbiosis
pairwise ledger (9,900 ordered pairs + 100 standalone: 1,989 functional /
6,375 functional-independent / 1,528 intended clashes / 8 unique /
0 defects), Dell 73 Threshold, the docked-Psalm operating model.

### (A) DISPLAY layer

**A1. Wave-equation field rendering for the SKY (2D Plane) — ADAPT.**
- Problem it solves: the standing display law — the field must feel
  alive and never stagnant — currently has no specified ambient motion
  system.
- Mechanism: implement the finite-difference wave sim in WebGL2 in
  Studio; ideas are emitters (position = Plane position, emission
  strength/frequency from idea attributes such as freshness/activity);
  a Pulse becomes a visible wavefront; interference bright spots show
  where fields reinforce. WaveDude's image-scene convention ADAPTED:
  render the idea layout into the sim's speed/damping texture (dense
  clusters slow/damp the field; links act as low-loss channels —
  waveguides, which is literally what a fiber is in Video 1).
- Why it works: the technique is proven at interactive rates by three
  generations of the WaveDude lineage; the physics is honest, so the
  motion never looks like random screensaver noise — it has causal
  structure a user can learn to read.
- Where it fails: GPU-less/weak machines need the WaveDude-style
  fallback (reduced resolution / fewer steps — WaveDude itself does
  exactly this). It is decoration unless bound to real field data;
  unbound, it becomes the "pretty analogy" trap (§6C).
- License path: clean-room reimplementation only (§4). Cost estimate:
  small — days, not weeks, for a competent WebGL pass (PROJECTION).

**A2. Studio page ambience / Nursery proposal cards with wave motifs —
INSPIRE.** WaveDude's field+intensity dual view (oscillation beside
time-averaged energy) is a good *information-design* pattern: show the
instantaneous state and the accumulated state side by side. Cheap to
borrow as layout, no code.

### (B) COMPUTATION / SEMANTICS

**B1. Does wave interference map onto DellMatrix resonance? — NO, not
as it stands; verdict: analogy only, with one honest INNOVATE option.**
- The resemblance is verbal. DellMatrix resonance (as built) is a
  selection/scoring mechanism over ideas with weights — there is no
  phase, no superposition of fields, no propagation medium, no
  interference term. Claiming the photonic results "validate" DellMatrix
  resonance would be exactly the metaphor-as-evidence failure §16/§21
  exist to prevent. **REJECT** any such claim.
- The INNOVATE option, if Ace ever wants the metaphor made real: define
  an explicit field layer for C13 rehearsal where ideas emit with a
  phase/frequency derived from recorded attributes and a probe point's
  intensity = Σ interference — a *new, separately-named* affinity
  instrument. It must not silently become a second selection authority
  alongside resonance (authority-collision law); as a read-only
  instrument feeding proposals, it is legitimate. Not recommended now —
  noted as an unexplored lead.

**B2. "Superposition sums free; decisions need a threshold; cascades
need restoration" — ABSTRACT (the photonic-logic design moral).**
- DellMatrix already embodies the first two: resonance-style weighted
  accumulation, and a literal Threshold Dell (73) plus gate/refusal
  surfaces that convert graded signals into decisions. The third —
  restoration — is the transferable warning for long Dell chains: graded
  quantities passed through many stages (weights, scores, faded ideas —
  cf. the DD-13 class, where faded/replaced ideas once voted at full
  strength) degrade unless a stage re-normalizes against a stated
  contract. Classification: ABSTRACT, largely
  SUPERSEDED_BY_DELLMATRIX in pattern; retain as a checklist question
  for chain design reviews ("where does this chain restore its
  signal?").

**B3. Sweep → classify → render-the-field, for C13 Simulate — ADAPT.**
- Problem: C13 (Simulate) needs a way to rehearse behavior across many
  possibilities, not one run (and per plan law, Try+run+Revert is NOT a
  zero-write sandbox — C13 must be an honest rehearsal instrument).
- Mechanism (from Video 3): given a chain/Dell configuration, sweep a
  grid over two chosen parameters or initial-state axes; run each cell
  in the sandbox; classify by receipt (ok / refused+reason / diverged);
  render the grid as a stability map. "Islands of stability" = parameter
  regions where the configuration behaves; fractal edges = brittle
  boundaries. This is falsifiable, receipt-backed simulation — every
  pixel is a real run with a real receipt, matching DellMatrix's
  evidence law, unlike a decorative heat map.
- Scale honesty: Drew used billions of runs on a rented GPU; DellMatrix
  is local-first — adapt at 10²–10⁴ cells with cheap runs (the pendulum
  runs were also individually cheap; the method scales down intact).
- Also applies to the **symbiosis ledger**: the 9,900-pair outcome grid
  already exists as data; rendering it as a navigable composition map
  (functional / independent / clash / unique as terrain) is the same
  technique pointed at existing evidence — a strong SKY/ROOM view
  candidate for the composition space. ADAPT (display of B3's data).

**B4. Robustness differential as validation habit — ABSTRACT /
SUPERSEDED_BY_DELLMATRIX.** Drew varied solver tolerances and physical
parameters to check his islands weren't numerical artifacts. DellMatrix
law already contains the siblings (§30 clean-copy differential, §31.3
cross-environment rule, ambient-state independence). No new machinery;
cite the video as an external worked example that the pattern is how
simulation claims earn trust.

### (C) PRETTY ANALOGIES — named so they can't smuggle weight

- **String-theory "everything is one string vibrating" ↔ "everything in
  DellMatrix is one substrate (ideas/Dells) in many modes."** Evocative,
  and it is the actual emotional core of Video 2 — but it predicts
  nothing, constrains nothing, and string theory itself is unproven.
  Classification: **INSPIRE** (aesthetic only), **REJECT** as evidence.
- **Veneziano's accident** (a formula found by fitting data, explained by
  a deeper theory  years later) — the *method* is the one transferable
  thing in Video 2, and DellMatrix already runs it deliberately: the
  symbiosis program mines 9,900 pairs for composition laws that must
  pass held-out prediction. Classification: **INSPIRE** for method
  morale; the program itself is SUPERSEDED_BY_DELLMATRIX (it exists,
  with stricter evidence rules than the video's narrative).
- **"Physics is harmonies, chemistry is melodies" (Kaku)** ↔ Mandell's
  layered representation (L3 semantic control under L1 English): a
  pleasing rhyme, nothing more. No classification action.
- **Photonic gates as a literal model for Dell composition**: REJECT
  (§6B1). Dells compose by contract and receipt, not by phase.

### Consolidated classification table

| Idea | Class | One-line reason |
|---|---|---|
| Wave-field rendering (WaveDude technique) in the SKY | ADAPT | Solves the "alive, never stagnant" law with honest physics; clean-room WebGL |
| WaveDude Next binary/code in DellMatrix | REJECT | Windows/.NET-only + GPL-3.0 copyleft + wrong scene model |
| WaveDude as Ace-side external freeware | ADOPT | Free, legitimate use today; outputs unencumbered |
| Field+intensity dual-view layout | INSPIRE | Good information design, zero-cost borrow |
| Interference = DellMatrix resonance semantics | REJECT | No phase/superposition exists in resonance; verbal resemblance only |
| Literal field/affinity instrument for C13 | INNOVATE (deferred) | Possible, but risks a second selection authority; park it |
| Superposition/threshold/restoration moral | ABSTRACT | Real design law; DellMatrix already embodies 2 of 3 |
| Sweep→classify→stability-map for C13 Simulate | ADAPT | Receipt-backed rehearsal across parameter space |
| Stability-map rendering of the symbiosis grid | ADAPT | Existing 9,900-pair evidence becomes navigable terrain |
| Robustness-by-parameter-variation | ABSTRACT / SUPERSEDED | Already DellMatrix law (§30/§31.3); video is a worked example |
| String theory as design evidence | REJECT | Unproven physics; narrative only |
| "One substrate, many modes" / Veneziano method | INSPIRE | Morale + method rhyme; DellMatrix's law-mining already stricter |

---

## 7. SOURCES (all accessed 2026-11-10)

Primary:
- Video 1 + official description/chapters: https://www.youtube.com/watch?v=ln0zZcQXv38
- Video 2 + official description/sources list: https://www.youtube.com/watch?v=xwaJQPytXuY
- Video 3 + official description (method, integrator, validation note, compute budget): https://www.youtube.com/watch?v=8jVogdTJESw
- WaveDude official site (features, downloads, lineage): https://wavedude.com
- WaveDude Next repo (license GPL-3.0, platform, README): https://github.com/graealex/WaveDudeNext
- WaveSimulator2D repo (Python/CuPy, scene convention; no LICENSE file observed): https://github.com/0x23/WaveSimulator2D
- Drew's Campfire code repo (identified via GitHub API listing): https://github.com/drewscampfire/Drew-s-Campfire-Videos

Secondary:
- MathWorks (Cleve Moler), "Double Pendulum" — independent coverage of Video 3 and its follow-ups: https://blogs.mathworks.com/cleve/2026/02/01/double-pendulum/
- MDPI Electronics review material on all-optical MZI/SOA logic gates at 120 Gb/s: https://www.mdpi.com/2079-9292/15/14/3217
- Industry analysis of photonic processors (MZI analog accelerators; "no cascadable AND/OR gates because light doesn't interact with itself"; 10–15 stage loss limit): https://medium.com/@oganmart1980/why-photonic-processors-need-quaternary-logic-introducing-gl4-423c92c52326 (advocacy source for its own GL4 system — used only for the mainstream-limits summary, which matches the review literature)
- 2Swap, "Double Pendulums are Chaoticn't" — follow-up science on the same islands (flip-based vs divergence-based classification differs): https://www.youtube.com/watch?v=dtjb2OhEQcU

## 8. UNEXPLORED LEADS
- Full transcripts (blocked by YouTube IP/bot checks from this network) —
  revisit if a transcript mirror or Ace-side download becomes available;
  spoken derivations in Video 1 (coupling-length math) would sharpen §5(i).
- WaveSimulator2D's license: check repo for a LICENSE addition or ask via
  its issue tracker before any code-level reuse is even contemplated.
- Nils Berglund's wave-simulation body of work (cited in the Huygens
  lineage) — a large, rigorous corpus of wave-equation visualizations;
  candidate reference for the Studio WebGL pass.
- Ricky Reuser's interactive double-pendulum Observable notebook (linked
  from the 2Swap follow-up) — a working in-browser stability-map
  implementation pattern relevant to B3's rendering cost estimate.
- Lightmatter/imec educational material (Bogaerts PIC lectures) if the
  team ever wants the photonic material at engineering depth rather
  than video depth.
- Cruz Godar's generative-art double-pendulum work (color-scheme/
  rendering craft for fractal maps) — display-craft lead for B3.

*End of report. Nothing published; no one contacted.*

---

## ADDENDUM — AUTHORITY ANALYSES FOLDED (2026-11-10)

**Director** (Gmail 1a1c69107898777f, folded verbatim as
DIRECTOR_ANALYSIS_PR364_WAVES_VERBATIM_2026-11-10.md): ACCEPT with
refinements. R1: restoration classified **ABSTRACT /
PARTIALLY_REALIZED / CHAIN_COVERAGE_UNKNOWN** — receipts restore
decision legibility, not the correctness of upstream graded inputs;
the bounded follow-up candidate is a graded-input-to-verdict invariant
test on one real canonical path (faded + stale/superseded injection at
a graded-to-decision boundary), only after grounding and without
duplicating DD-13. R2: field instrument **INNOVATE_DEFERRED** —
read-only, nonauthoritative, never feeding resonance scores, Nursery
admission, vote weights, or threshold decisions by default; any
semantic path is an Ace-owned architecture decision requiring
independent predictive validation. R3 audit nuances: SKY wave-field
ADAPT is future display-only DESIGN (performance + visual-meaning
calibration PROJECTED, not verified); WaveDude REJECT is scoped to the
CURRENT Studio architecture and the record's GPL wording is corrected
— GPL-3.0 does not ban use nor automatically infect independent
coexisting works; C13 sweep ADAPT is DESIGN, not certified
implementation (requires a genuinely isolated sandbox — Try+run+Revert
is not isolation — deterministic seeds, per-cell receipts, sensitivity
analysis, and no run-count promises before profiling); symbiosis map =
visualization of existing receipts, no causal prediction implied;
robustness differential ABSTRACT, not superseded until the C13 solver
and classifier carry perturbation controls. EVIDENCE BOUNDARY
(Director): the photonics "10-15 stage" cascade figure must not be
generalized — it depends on topology, loss, and regeneration; the
transferable moral is analogy, not engineering law.

**Keeper** (record KEEPER_ANALYSIS_RESEARCH_VIDEO_STUDY_WAVES_2026-11-10.md,
commit aabfe3c; PR #364 comment 6774802581): record-truth CONFIRM, no
drift, no HOLD; all classifications concurred with no moves; INNOVATE
field layer explicitly parked under second-authority risk; five
standing SWAT risks seeded for any future wave-field SKY or C13
stability-map circuit (second-authority isolation, data-binding,
clean-room license hygiene, GPU-less fallback, receipt-per-cell
honesty).
