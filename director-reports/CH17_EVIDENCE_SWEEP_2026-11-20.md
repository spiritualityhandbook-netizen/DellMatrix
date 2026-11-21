# CH-17 EVIDENCE SWEEP — The Eleven Houses, Caller/Writer/Source Counterexamples

**Part I (Architecture) — opening evidence act, 2026-11-20.**
Branch `uni/part-1-architecture`, base main
`af2519b6d239ef278397e277210d6da2467c36e5`.

**What CH-17 is.** Edition 1 (`10_G2_CHALLENGE_DISPOSITIONS.md`,
carried from the G3 PASS): *"All 11 H-houses still require
caller/writer/source counterexamples on current main… one case
does not certify all 11."* Protocol
(`07_UNI_INDEPENDENT_REVIEW_PROTOCOL.md` item 2): per house,
challenge the unique writer/owner, the production route, missing
interfaces, hidden second data authorities; ≥1 realistic
counterexample per house plus whether code already prevents it;
explicit checks: Idea↔Unit binding, lifecycle, mixed-parent wall,
rooms vs boxes, Program/Nursery pair-save hold.

**What this sweep is and is not.** A grep-grounded
caller/writer census plus live behavioral probes (the Part I
failing-first/spec suites, run 2026-11-20 on current main). It
does NOT certify any house. It converts CH-17 from one open
challenge into eleven per-house evidence states with named
residuals. Verdict vocabulary: **VERIFIED** (claim holds under
probe), **NARROWED** (counterexample partially discharged, named
residual remains), **CONFIRMED** (counterexample reproduces on
current main), **UNKNOWN** (not swept at depth this cycle —
stated, never silently passed).

Houses per `00_DIRECTOR_MASTER_BLUEPRINT.md` §2. Spine rule:
H1/H2/H7 unbreakable. Every feature names ONE canonical writer +
all read-model consumers.

---

## H1 — Spine (parse → dispatch → execute)

- **Canonical writer claim:** one dispatch authority,
  `execute_seed` (`form/mandell/executor.py:30`).
- **Census:** `execute_seed` is called from `form/open.py`
  (2 sites) and `form/repl.py` (1 site) — doors call the one
  dispatcher; no second dispatch implementation found.
- **Counterexample class (historical, repaired):** semantic drift
  entered BELOW the dispatcher, in leaf/predicate layers — R25
  condition shorthand (PR #496: exactly-two-operand contract) and
  the eval-predicate surplus (PR #497). Both repaired and
  regression-pinned; neither was a second writer.
- **Verdict: VERIFIED** for the single-writer claim. Residual:
  leaf-layer semantic drift is a standing class; the guard is
  per-leaf failing-first pinning (Part II's Dell contracts), not
  an H1 mechanism.

## H2 — Field (Plane, units, boxes, growth wall)

- **Canonical writer claim:** `Plane` owns units/boxes
  (`form/dell_matrix/plane.py`: `place` :129, `box` :211,
  `unbox` :235); growth proposes, confirm places.
- **Counterexample (register #185, U-PROBE/PR #410):** confirm
  placement was wall-blind — boxed-parent offspring placed
  UNBOXED; the auto-confirm sweep confirmed cross-wall proposals
  LIVE.
- **Re-probe on current main (2026-11-20, `gs4_sandbox_test.py`
  RUN G extension, 22/22):** G2 — the sweep now SKIPS mixed-wall
  proposals as non-eligible (`skipped_noneligible=4` of 4 seeded,
  Q-U.5 treatment inside `grow_ideas`); G1 — both-parents-boxed
  offspring confirmed via the sweep lands INSIDE the vault
  (membership inherited); G3 — single-parent boxed drift
  offspring (3 seeded) all land inside the vault.
- **Verdict: NARROWED.** The register's reproduction no longer
  reproduces on the sweep path. Residuals: Q-U.2 dock-landing
  circuit (authorized, bounded — the Part I build), Q-U.3
  confirm-placement inheritance as a general contract (incl. the
  manual-confirm path, which this harness could not exercise —
  acceptance policy denies producer `unknown`), Q-U.4
  manual-confirm cross-wall semantics — an Ace sovereignty
  question, deliberately not encoded as a test verdict.

## H3 — Body (views / read models)

- **Claim:** views are read models; the write authority stays in
  the Program/Plane layer.
- **Census (surface):** `form/dell_matrix/graph_view.py` (8 defs)
  and `form/dell_matrix/view_rooms.py` (5 defs) contain no
  save/write/file-open-for-write calls (grep-verified).
  Rooms vs boxes are distinct surfaces: `list_rooms()` returns
  the 7 view rooms; boxes live separately in `plane.sandboxes`
  (both exercised live in the C3/C6 suites).
- **Verdict: VERIFIED at surface depth.** Residual: a full
  caller trace of every view consumer was not run this cycle;
  the C3 suite's room-write checks (#134) FAIL for the missing
  chosen-room write/close surface — that is a missing interface
  (Part I C3 build), not a second writer.

## H4 — Forces and witnesses

- **Claim:** witnesses return verdicts consumers can act on.
- **Counterexample CONFIRMED:** the resonance witness
  `graph_harmony.graph_coherence` returns a **bare float**
  (measured live: C2 suite control — a float coherence value,
  no typed verdict, no reasons, no with-whom/how-strong/why).
  The C2 contract surface (typed `ResonanceVerdict`, relatedness
  query) is entirely absent — C2 spec suite **2/11**, all 9
  contract checks red.
- **Verdict: CONFIRMED.** Repair = the C2 build (rows #121–#129,
  Part I cluster C2). The float is a score, not a witness
  verdict; consumers treating it as one are unguarded today.

## H5 — Gate and growth (AcceptancePolicy, Nursery gate)

- **Claim:** nothing lands without the gate; growth is
  proposal-only until confirmed.
- **Probes:** (a) a direct manual `confirm_proposal` with an
  ineligible producer is DENIED — `{'ok': False, 'reason':
  'acceptance_policy_denied'}` (measured while building the GS-4
  extension): the gate binds. (b) The opt-in auto-confirm sweep
  is exactly that — opt-in (`set_auto_confirm_grow`), and its
  mixed-wall non-eligibility (H2/G2) shows the gate's wall rules
  reach the sweep. (c) Growth-side wall repaired (GS-4 RUN A–F
  green before this Part).
- **Verdict: VERIFIED** for the gate claim. Residuals ride with
  H2 (Q-U.2/Q-U.4) and row #67 (delegation/expiry/revocation
  chain stress — retained PARTIAL remainder, Part I build).

## H6 — Senses and dynamics (geometry, spatial, audio)

- **Census (surface):** the sense modules exist —
  `form/dell_matrix/sacred_geometry.py`, `spatial_audio.py`,
  `spatial_authority.py`. No Part I circuit exercised them at
  depth this cycle; the 30-video P06 geometry fixtures placement
  belongs to this house and is unbuilt.
- **Verdict: UNKNOWN at depth** — stated plainly. Residual sweep
  debt: per-module writer census + provenance-of-derived-reading
  probes, owed in the Part I code stage alongside P06.

## H7 — Memory (history, save/load, checkpoints)

- **Claim (protocol's explicit check):** the Program/Nursery
  pair-save holds — a fresh load never exposes a torn pair.
- **Counterexample 1 CONFIRMED — ordinary path:** the
  checkpoint path is pair-atomic (SM-35 A/B GREEN), but the
  ORDINARY `Program.save` path is not: `sm35_ca_qe2_test_spec.py`
  measures **HYBRID in both crash windows (0/2)** — a fresh load
  exposes the new program generation with the old nursery
  generation. This is the C-A scope (Director 7040542941);
  separately scoped, NOT authorized; MWL #46 stays GATED.
- **Counterexample 2 CONFIRMED — history retention:** three cut
  sites silently truncate history at 24/120 entries on current
  main (`form/open.py` history cap, `persist.py:378`,
  `persist_rest.py:643`); the R5-D failing-first suite measures
  **3/22**. The R5-C policy is ADOPTED; the R5-D implementation
  is HELD (unlock: Keeper challenge of prep `13b33fa` → Director
  bounded authorization at most S7 → code).
- **Verdict: CONFIRMED (×2).** H7 is a spine house; both
  counterexamples are named, measured, and routed — C-A as a
  GATED scoping, R5-D through its recorded unlock path. Neither
  is silently carried.

## H8 — Doors (Exchange, import/export, host boundaries)

- **Counterexample CONFIRMED:** the Q1 Exchange import/recovery
  pair has no commit boundary — C-B prep suite **4/7**: recovery
  erases the completion marker (W1), errors over clean state
  (W2), and the importer blesses an incoherent pair (W3).
  Guards that HOLD: fail-closed disposal (W2F), idempotent
  disposal (P3), journal-absent purity (P5), corrupt-journal
  evidence retention (P5D).
- **Verdict: CONFIRMED.** Repair designed in
  `director-reports/Q1_CB_TRANSACTION_DESIGN_2026-11-20.md`
  (this PR); code gated on Director C-B authorization; MWL #118
  stays GATED; PR #294 never merges under the GATE HOLD.

## H9 — Surfaces (Studio / Console / human surfaces)

- **Census (surface):** the surface test instruments exist and
  are registered — `form/studio_security_test.py`,
  `form/gui_api_test.py` (Host/Origin/token + malformed HTTP,
  row #76's bounded work, PARTIAL). No deep sweep this cycle:
  no caller census of surface→Program writes was run.
- **Verdict: UNKNOWN at depth.** Residual debt: surface write
  census (every surface mutation must name its Program door),
  owed in the Part I code stage with the Studio cluster
  (#76/#77/#79/#81 remainders).

## H10 — Instruments (regress, capture, receipts)

- **Counterexample (historical, repaired):** the regress
  failure-capture instrument was blind to the FAIL format the
  profile suite writes — the #496 merged-main smoke failure's
  exact check name was lost before capture (PR #499 repaired:
  capture reads all three formats, privacy-strict, silent on
  green). A second instrument lesson landed DURING this Part:
  an unregistered `*_test.py` turns CI smoke RED as an omitted
  entry (PR #503, run 44758805458) — this Part's failing-first
  artifacts therefore ship as `*_test_spec.py` with
  rename+registration as code-stage step zero.
- **Verdict: VERIFIED post-repair**, with the standing rule
  encoded in the Part I plan: capture failed evidence before any
  re-run; instrument claims are verified against raw artifacts
  before product conclusions.

## H11 — Archive (supersession, provenance, records)

- **Census (surface):** supersession is retained in-program —
  `Nursery` proposals carry `superseded_by_id` / `supersedes_id`
  lineage fields (`form/dell_matrix/nursery.py:425`, :1122), so
  replaced proposals remain addressable rather than vanishing;
  `director-reports/` is the human-side archive of record.
- **Counterexample:** none found at surface depth. The C3
  suite's #136 check (Alpha/history ceremony — old generations
  freeze/confirm/restore) FAILS as a missing interface, which is
  an archive-adjacent build gap, recorded under C3.
- **Verdict: VERIFIED at surface depth.** Residual: a full
  provenance-chain audit (every supersession reachable end to
  end) was not run; owed with the C3 #136 build.

---

## Sweep summary

| House | Verdict | One-line basis |
|---|---|---|
| H1 Spine | VERIFIED | one dispatcher; drift class is leaf-level, pinned per leaf |
| H2 Field | NARROWED | #185 sweep-path reproduction discharged (GS-4 G1/G2/G3); Q-U.2/.3/.4 remain |
| H3 Body | VERIFIED (surface) | view modules carry no write calls; rooms≠boxes live |
| H4 Forces/witnesses | **CONFIRMED** | witness returns a bare float; typed verdict absent (C2 2/11) |
| H5 Gate & growth | VERIFIED | acceptance policy demonstrably denies; sweep is opt-in + wall-ruled |
| H6 Senses | UNKNOWN (at depth) | modules exist; not probed — debt named |
| H7 Memory | **CONFIRMED ×2** | ordinary-save HYBRID (C-A, GATED); history cuts 24/120 (R5-D, HELD) |
| H8 Doors | **CONFIRMED** | Q1 recovery pair incoherent (C-B prep 4/7); design in this PR |
| H9 Surfaces | UNKNOWN (at depth) | instruments exist; write census owed |
| H10 Instruments | VERIFIED (post-repair) | capture blindness repaired (#499); omitted-entry rule encoded |
| H11 Archive | VERIFIED (surface) | supersession lineage retained in-program |

CH-17 is thereby discharged as an *evidence* act: the challenge
is answered per house with counterexamples where they reproduce
and scoped residuals where the sweep did not reach. It certifies
nothing; the CONFIRMED houses route to their Part I clusters
(C2, C-A scoping, R5-D unlock, C-B authorization) and the
UNKNOWN houses carry named sweep debt into the code stage.
