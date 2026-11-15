# SYSTEM DECISION REGISTER — Rulings Owed + Feature Intake

**Deliverable 8 of SYSTEM-001** (DIR-DM-SYSTEM-001). Two registers
in one file: **Part A**, decisions requiring an authority (from Lane
3's sweep, questions stated exactly); **Part B**, the standing
**Feature Intake** — Ace's late-arriving features are logged here
the moment he states them, numbered, and never lost (Ace,
2026-11-14: *"I may add features to this as time passes by… I know
I'm forgetting plenty"*).

## Part A — Decisions requiring authority

| ID | Authority | Question (exact) |
|---|---|---|
| DC-1 | Director | Shall the ledger carry append-only reclassifications — EQ-VER-001 DUPLICATE → delegated-canonical, R4-A5 status updated — citing the code evidence? |
| DC-2 | Director | Which two of the three "verita" mechanisms rename (R4-A2), and does the ruling cover the seven "harmonic" bearers (R4-A6 extended)? |
| DC-3 | Director | Which metric replaces EQ-GEO-002 — lens-area fraction or Jaccard-of-disks (R4-A3) — and in which phase? |
| DC-4 | Director | Is VERITA-JUDGE production-live or test/proof-only — the ledger's "live on brain/auto_growth" vs Lane 3's grep — and if the grep stands, what is its recorded participation? |
| DC-5 | Director | Confirm GP-G03's status from X11 runtime evidence when it lands, or rule on the documents now? |
| DC-6 | Director | Resonance's "vesica" log token — rename it (to what?) or wire real geometry into `harmonize_pair` (R4-A4)? |
| DC-7 | Director/Keeper | Do closed findings earn COMPLETE credit — GP-G24, G-29, FAR-17 (the +3 inside UU-14, which the Nov 26 score depends on)? |
| DC-8 | Ace | Dell 151[Harmonic] — open a contract, extend the registry beyond 99, or strike the citation from seed.py's docstring? |
| DC-9 | Ace | The twelve orphan-candidate modules — one class stand-down ruling (SD-5 receipt model) after X11's check, or case-by-case? |
| DC-10 | Ace | Space (GP-G01) — build the room-to-grow quantity or retire the force with a receipt? |
| DC-11 | Ace/Director | Does the ledger become a living document with a per-circuit reclassification duty, or remain a V1 snapshot succeeded by Ledger V2? |

Carried standing decisions (not re-asked; recorded so nothing
double-owns them): Q-F1 idea radius (Director admission; gates Tree
L3); FCC admission (Keeper THL-SM-02 reproduction → Director
ruling; UU-6); everyday-save acceptance = load-time convergence
(Director's C-A circuit owns the repair; SYS-C30); the +3
register-closure credit (DC-7 above); completes 35 vs 39 (UU-14 —
settled by the Nov 26 fresh render, not by argument).

## Part B — Feature Intake (Ace's register, upgraded by his ruling 2026-11-14 18:36 CST)

### The Intake Law (Ace, verbatim substance)

Every feature Ace states — in any chat, at any hour — is logged
**the moment he says it**, with a number and a status. Logging is
not a stub and not a sketch. At intake, the feature is:

1. **MIRRORED** against the entire plan *as the plan stands at that
   moment* — what is done, what is not done, calculated at intake
   time (current totals, the feature's neighborhood state, its
   dependencies' states, the live pins and open gates).
2. **EXAMINED AND FULLY DEVELOPED** — the full plan of the idea is
   brought into the plan: purpose, mechanism, contracts touched,
   dependencies, failure behavior, acceptance test, evidence path —
   to the same standard as a refined Grand Plan entry, so that when
   its turn comes it can **just be executed**, with nothing left to
   invent.
3. **PLACED** — in its correct position: category, plan location,
   and timeline position (which phase, what it waits for, what waits
   for it). Intake is placement, **not** immediate work; a feature
   is worked when its position's turn arrives or an authority moves
   it.
4. **DONE-DEFINED** — its completion criteria and its *why* are
   written at intake, so "done" is checkable later against what was
   meant.

Nothing in this register is ever deleted; superseded entries are
marked, not erased. Status lifecycle: `INTAKE → DEVELOPED → PLACED
→ QUEUED → IN PROGRESS → BUILT → CERTIFIED`, with `BOUNDED` /
`RESEARCH` / `DECISION` naming what a placement waits on.

### The register

| ID | Stated | Feature (Ace's words) | Placed | Status |
|---|---|---|---|---|
| FI-001 | 2026-11-14 18:27 | "Dells as numbers — since they are numbers can we put them in a lattice in a way to use them faster and pull them faster" | Part I (Architecture / spatial-indexing); Roadmap Phase 4 | DEVELOPED + PLACED (below); BOUNDED on the placement-derivation ruling |
| FI-002 | 2026-11-14 18:27, upgraded 18:36 | "I may add features to this as time passes by… I know I'm forgetting plenty" + the 18:36 development-and-placement ruling | Governance — this register | ADOPTED AS LAW — the mechanism described above |

---

### FI-001 — THE DELL LATTICE INDEX (fully developed at intake)

**Ace's words.** "Dells as numbers — since they are numbers can we
put them in a lattice in a way to use them faster and pull them
faster."

**Why (his purpose, and the boundary it sets).** Speed of use and
retrieval: reach the right Dell, and the right *company* of Dells,
without scanning the registry. The why also bounds the design — the
index is an accelerator over the truth, never a source of it.

**Mirror — the plan as it stood at intake (2026-11-14 18:36 CST,
calculated).** Unified plan: **35 COMPLETE verified of 224 (15.6%)**,
target ≥56 by Nov 26. Done neighbors: the canonical registry (99
Dells, live), the executor (128 importers — the retrieval consumer),
HarmonicLattice (coordinate store + readings, exists), FLOW profiles
(merged), LM-4 (live). Not done: the Dell Plan gate has not started
under the unified order (69 of 99 Dells carry plan debt — the index
accelerates *reaching* Dells, it does not repair what they do); the
symbiosis composition laws have not yet passed their held-out
prediction test (the pairwise evidence exists; the laws are
pending); Tree admission is gated (THL-SM-02 Keeper reproduction,
then the Director's ruling); placement contract SYS-C12 is PROPOSED;
Boundary 4 is PARTIAL; the census's runtime half (X11) is
outstanding. Pins: main `62bdcbc`; PRs open — #418, #420, #421
(unified plan; Director HOLD, crosswalk required), #422 (SYSTEM-001,
this package).

**What.** A derived spatial index over the canonical registry:
every Dell's number is its address; the index assigns each address
lattice coordinates plus neighborhood sets, and serves three
retrievals — by coordinate (direct resolution), by neighborhood
(measured kin in one grab), by route (composition paths read as
lattice paths).

**How.** A build pass reads (a) the canonical registry, (b) the
relation evidence — Dell family structure, chain co-use counts from
executor receipts, the symbiosis pairwise classifications — and
derives coordinates **deterministically**. Runtime consumers (REPL,
executor, Studio navigation) consult the index for retrieval; on
any index doubt they fall back to the registry, which the index can
never outrank.

**Where.** A new index module in `form/dell_matrix/` beside
`harmonic_lattice.py` (the candidate substrate), a build/rebuild
tool beside the LM build tools, and the derived index stored under
`form/state/` as a cache carrying a provenance header (registry
fingerprint + evidence ids + build pin). New contract proposed at
build time: SYS-C45 (registry → index derivation).

**Placement law (the honest constraint, from the Tree's law).**
Coordinates are derived from **measured relations only** — never
assigned for looks. A decorative lattice makes "near" meaningless
and fast retrieval retrieves the wrong Dells confidently. Where a
relation is unmeasured, the Dell carries an UNKNOWN placement class:
still retrievable by address, honestly unplaced by relation.

**Failure behavior.** Stale index (registry changed since build) →
fingerprint mismatch → the index refuses and rebuilds or falls back
to the registry; a Dell is never made unreachable by the index.
Corrupt index → same path. The index failing can only ever cost
speed, never correctness.

**Acceptance — what "done" means (checkable).** (1) Round-trip: all
99 addresses resolve through the index to exactly the registry's
Dells. (2) Neighborhood queries return only relations over a stated
threshold, with evidence ids on the receipt. (3) Rebuild from
scratch reproduces the index bit-for-bit. (4) The "faster" claim is
**measured** — a retrieval benchmark against registry list-scan,
recorded (§1 doctrine: efficiency claims are requirements until
measured). (5) Public-path proof through the REPL.

**Placement (position, category, timeline).** Category: Part I —
Architecture / spatial + indexing; contract family Boundary 4.
Timeline: **Roadmap Phase 4** (spatial reconciliation), beside
SYS-C12 (idea placement) — both consume measured-relation evidence,
so they share a derivation ruling. It is deliberately **not** in the
Dell Plan gate: the gate repairs what Dells *do*; the index changes
how they are *reached* — a different layer, and mixing them would
slow both. Waits for: (1) the Director's placement-derivation
ruling (which relations, which thresholds — Q-S1.3 carries the
recommendation); (2) the symbiosis laws' held-out test, **or** a
fallback derivation from family + co-use alone, labeled weaker on
the index's own provenance header. Nothing on the critical path
waits for FI-001; journeys J-13/J-15 gain from it when it lands.

**Readiness: BOUNDED** (derivation ruling + evidence status). When
its turn comes: one bounded circuit, execution-ready as written.

*End of Deliverable 8.*
