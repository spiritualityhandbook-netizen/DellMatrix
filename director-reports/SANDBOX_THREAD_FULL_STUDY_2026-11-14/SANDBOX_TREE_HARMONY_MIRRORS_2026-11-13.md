# SANDBOX — THE TREE OF HARMONY & LIFE × EVERYTHING
## Combine tests, codebase inventory mirrors, and cross-system mirrors
### Ace's order 2026-11-13 21:03 CST — SANDBOX throughout; nothing placed, nothing implemented

Companions: `SANDBOX_TREE_OF_LIFE_STUDY_2026-11-13.md` (Parts I–III,
Addenda 1–3), `SANDBOX_FLOWER_SPHERE_FIELD_STUDY_2026-11-13.md`,
`SANDBOX_FLOWER_POLYGON_LADDER_STUDY_2026-11-13.md`.
Codebase evidence: read-only inventory of clone `~/workspace/nbd-omega-wake`,
branch `uni/track-d-bridge-planning`, HEAD `05859c0` (2026-11-04 merge of
main). Findings about code are stated AT THAT HEAD; current main
(2026-11-13) may differ and any action would need re-verification there.
Grades: MECHANISM (same machinery/shape, checkable) / PATTERN (same shape,
different machinery) / METAPHOR (picture only). Claims never outrun the
grade.

---

## §1 THE COMBINE QUESTION — SETTLED (see Tree study Addendum 3 for numbers)

Blending fails (layer alternation 260–264 banned pairs; braid 268; recipe
sums 268 and 804-with-total-layer-failure). Stacking works: the chord
(A-note, B-note) repeats at most 3× in the 177-Tree with first repeat at
2√2; the triple (A, B, cube) is unique for all 177 centres. The three
recipes are three READINGS, and readings stack — which is exactly the
codebase's own perception law (§3, D11).

## §2 WHAT THE CODEBASE ACTUALLY CONTAINS (inventory headlines)

- `form/dell_matrix/` = 103 files / ~35.4k lines; `form/mandell/` = 228
  files / ~88.6k lines + 23 docs. DuoBeta has its OWN package
  (`form/duobeta/`: growth.py — generations + ledger, selfgrow.py) plus
  the learning layer `form/mandell/duobeta_learn.py` (MIN_EVIDENCE = 3;
  learned state rides the existing `duo_ledger`; no parallel ledger).
- WATER (`form/dell_matrix/forces.py:64–126`): idea → stream (volume
  1.0); last two streams merge → river (volumes ADD); stream settles →
  pool. Tick (`ForceField.tick`, :385–449): body pulse first, forces
  circulate, weather set from organ health. PERSISTENCE, exactly as
  coded: save writes Water's stream/pool COUNTS + intensity +
  evolution_level (`persist.py:298`, `forces.py:455–456`) — the stream
  and pool records themselves are NOT serialized, and `from_dict`
  ignores the counts. Project records certify Water within a canonical
  save/bind scope (PR #285); the code at this head is consistent with
  "counts + levels bind, contents do not."
- PERSISTENCE ASYMMETRY, same file family: GRAVITY's wells ARE written
  by `to_dict` (:461) but `from_dict` (:470–493) never restores them;
  SPACE's evolution_level is saved (:467) and never restored; forces
  restore is wrapped in try/except-pass (malformed → fresh field,
  silently) while the spatial restore directly below FAILS CLOSED
  (`persist_rest.py:464–480`). Pattern: several forces save less than
  they keep, or save what the load never reads.
- SPACE force (`forces.py:333–340`): description-only — "Negative space
  and voids between nodes — room to grow." No methods, no state. (Part I
  of this line already produced its honest referent candidate: a
  negative-space CLASS report — COVERED / POCKETED / CHANNELED / OPEN —
  as a report, not a force.)
- FLOW, three mechanisms: (i) Water flow (above); (ii) Mandell chain
  flow (`form/mandell/flow_executor.py`): `>` FlowTo = always run next,
  `>>` FlowThru = blocking, skip next if previous failed; all other
  operators classified and refused — flow is governed, not free;
  (iii) Resonance pulse (`resonance.py`): DIFFUSION over the resonance
  graph, score/tags spreading across edges over time, firewalled from
  RingedGrowth's one-shot pair affinity and from Verita.
- ROUTE: Dell 59 = a direction label ("Choose/direct execution path";
  in a Branch chain a 59 atom is consumed as the Else marker);
  `semantic_router.route_intent` is the typed routing boundary;
  `inspire_pack.route_cost` prices a route. NO trajectory/movement
  mechanism exists in these folders (inventory-verified absence of a
  mechanism, stated as such): Route is a signpost without terrain.
- HARMONIC material: `harmonic_core.py` — by its own header "not a
  harmonic engine and computes nothing musical; the 'harmonic' name is
  historical" — it holds PULSE CONSTANTS (Subkey 4 : Core 1 : Relay
  0.25 — the Harvest Core's heartbeat numbers), a lattice SIZE POLICY
  (12 | 14), and the KeyLedger (permanent addresses, radial soft-forget
  of payloads). `harmonic_lattice.py` — the real note machine:
  `note_at(h,v,f) = (origin + 7h + 4v) mod 12`, octave by layer;
  DERIVED projection, lossless members, rebuild-only. `harmony.py` —
  set coherence `C × (1 − R)`, R = mean pairwise Jaccard³: a PAIRWISE
  statistic. `graph_harmony.py` adapts it read-only over the
  SemanticGraph, returning honest 0.0 when no association exists.
- HARMONIC TRUTHS (`form/mandell/harmonic_truths.py`, 50 lines): Three
  Absolute Truths from the historic Harmonic 14×14 analysis —
  EXISTENCE ("Keys permanent. Floor locked. Units may move or
  soft-forget payload; address remains."), CHANGE ("RingedGrowth never
  silent-writes live plane."), ONENESS ("The All is the One — different
  frequencies of one spine. One lattice · many perceptions. One Dell
  spine · many surface languages."). Marked in its own header:
  "Practical law only." The Tri-Harmonic Fusion document
  (`HARMONIC_FUSION.md`) carries a HISTORICAL RECORD banner and records
  `harmonic_link.py` REMOVED as dead code (GDP-001, zero callers).
- NAME COLLISION, on the program's own ledger
  (`docs/DELLMATRIX_EQUATION_LEDGER.md` R4-A5/R4-A6, EQ-RES-001):
  "Harmonic" already names ≥3 mechanisms (lattice notes; the
  harmonic-mean-like `_harmonic()` combiner in ringed_growth.py —
  "un-derived; must not be read as musical"; legacy 5-tier memory JS);
  the ledger's standing instruction is RECONCILE-DON'T-MERGE. A Tree
  labelling would be a FOURTH "harmonic" — it must carry its own name
  (the chord / Tree labelling), never the bare word.
- THE NERVE'S DOOR ALREADY EXISTS: `sacred_geometry.py` header records
  Čech nerve / power diagrams / alpha filtration as DEFERRED — "not
  implemented anywhere in form/", pending (a) proven consumers and
  (b) an admitted mathematical derivation. Part I's thick-nerve kernel
  sits exactly in that deferred slot and now knows its two keys.
- PERCEPTION LAW (`perception.py` + `harmonic_lattice.py` header):
  cube/circle/sphere/Flower are perception MODES of one lattice —
  "coordinates stay; reading changes." Forms are stacked readings,
  never blended.
- OTHER: `fourier.py` (offline DFT, links the lattice); `bounded_orbit.py`
  (Cₙ₊₁ = Cₙ² + Δ Mandelbrot recurrence as an interpretive helper, honest
  header); `logistic_map.py` (bifurcation; header claims it drives
  growth intensity/weather variability — wiring into ForceField NOT
  verified); Dell `151[Harmonic]` cited in seed.py's docstring (registry
  contract not opened this pass — UNKNOWN); NO tree-structure module
  exists in either folder (the Tree remains a new sandbox object).

## §3 MIRRORS — Tree × Harmony against the five named systems

**Harvest Core Network.** MECHANISM-adjacency: the HCN pulse constants
(4:1:0.25) live INSIDE `harmonic_core.py`, beside the lattice size
policy — the program already files its rhythm and its note-painting in
the same drawer. PATTERN: Tree shells (centres by step: 12, 42, 92,
162 = 10k²+2) are growth rings; a centre + its 12 neighbours is a
definite coordination unit (an organ's local world); WARD's watchlist
= shell boundaries; SEED VAULT = the chord census computed once at deep
budget and served by address. The chord gives each organ-address a
three-reading fingerprint without touching organ truth.

**Route Path.** PATTERN + instrument candidate: the Tree supplies the
terrain Route lacks, and with it TWO honest lengths for any journey —
hop count (which step-shell the destination sits in) and straight span
(Euclidean shell). A route receipt carrying both numbers can never
confuse "far to walk" with "far away" (the Tree's own two censuses
disagree exactly there: a √5 centre is nearer in space than a √7
centre but one hop farther). Route stays a label in code today; this
is the ground a trajectory mechanism would stand on, if one is ever
admitted.

**Voynich.** MECHANISM (method): refutation absolutes. Voynich: 'n'
never opens a word, 'q' never closes one — any claimed reading that
violates them is dead on arrival. Tree: distance √14 is impossible in
ANY FCC tree (28 is not a sum of three squares) — any claimed Tree
measurement containing it is dead on arrival. Same instrument class:
impossible configurations as cheap lie detectors. PATTERN: Voynich's
per-word positional habits (a word's blocks behave by position, not by
meaning) are the same species as note-by-address (pattern carried by
position, content-free) — and the Voynich honesty lock applies verbatim:
positional pattern established, meaning = ZERO in both. The -dy…qo-
handshake (a pair correlation at fixed lag, 2.26×) is the textual
cousin of the Tree's pair-correlation fingerprint.

**Smith Chart.** PATTERN only, and the park stands: no Smith code
exists under `form/` (legacy JS only). The one live rhyme: a Smith
picture plots TWO independent quantities (resistance + reactance) as
ONE point — the chord does the same with three readings as one
identity. If the Smith tab (§5A) ever gets its data spec, the chord is
the shape its points would take: several honest numbers, one address,
radii/angles that resolve back to records.

**Mandelbrot.** PATTERN, and it discriminates the families: the
Mandelbrot's deep copies are BENT (Tan Lei asymptotic similarity —
kin, not photocopies; measured in-house Jaccard 0.299). Family A's
slices are EXACT photocopies (the trivial self-similarity of a plain
zoom). Family B's slices are the same pattern TRANSPOSED — the same
shape in a shifted key, which is the harmonic form of a bent copy.
`bounded_orbit.py` already carries the recurrence Cₙ₊₁ = Cₙ² + Δ as a
helper: an orbit is a walk that may cycle; a walk on the Tree is the
same grammar (period = a route that returns; escape = a route that
leaves the shells). If the Tree's harmony is ever asked to rhyme with
the program's founding fractal, B (or the chord, which contains B)
carries the bent-copy character; A carries the circle's.

**DuoBeta (from §2).** PATTERN with a mechanism rhyme: DuoBeta's gate
needs ≥3 matching outcomes before learning (MIN_EVIDENCE = 3) — three
weak signals combine into one admissible conclusion. The chord is the
same arithmetic in space: three weak positional readings combine into
one unique address fingerprint (177/177). And DuoBeta's generations
(evolve → gen+1, ledger-append) are iteration with a receipt — orbit
receipts (X7) remain the bridge candidate. Learning stays behind its
gate either way; chord changes are observations, never learning.

## §4 WHAT THIS DOES TO THE DECISION

The either/or dissolves. Under the program's own perception law,
readings are stacked, not blended — so the standing recommendation of
this study line is: **carry the chord (all three channels), and let
Ace's pick choose only the PRIMARY display channel** — the one whose
note is shown first / loudest when a future Tree overlay paints a
sphere. The pick then costs nothing in identity (the chord identifies
regardless) and remains reversible (channels are derived, rebuildable).
Nothing here is implemented, placed, or authorized; the Flower/Tree
line's acceptance remains Ace's call, whole.

## §5 OPEN THREADS

- Q-M1: persistence-asymmetry findings are at clone HEAD 05859c0
  (2026-11-04); re-verify on current main before any use.
- Q-M2: Dell 151[Harmonic]'s registry contract — unopened.
- Q-M3: does anything call `suggest_preferred` (duobeta_learn.py:352)?
  This pass: UNKNOWN (project records list it as an orphan exhibit).
- Q-M4: is `logistic_map` wired into ForceField by any caller? UNKNOWN.
- Q-M5: the chord as the Smith tab's point shape — data-spec question
  for that circuit, not this one.
