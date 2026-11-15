# SYSTEM END-TO-END TEST MATRIX — User Journeys

**Deliverable 7 of SYSTEM-001** (DIR-DM-SYSTEM-001). The Director's
completion condition for SYSTEM-001: *trace every proposed major
capability from user action through execution, state, dependent
engines, persistence, and visible result.* Each journey below is
that trace, with today's honest status. A journey is PROVEN only
when the full trace has executed on the public path at a pinned
head; scoped pieces are labeled with their scope.

| # | Journey (user action → visible result) | Trace | Status today |
|---|---|---|---|
| J-01 | Type a supported Mandell chain in the REPL → Dells execute → state changes → receipt shows the chain | REPL → registry/executor → Program → persist → receipt | **PROVEN (scoped)** — the certified circuits' paths (Core I/II, FLOW profiles incl. G31 refusal-by-name); not proven for all 99 Dells (69 carry plan debt) |
| J-02 | Issue an unsupported/invalid instruction → honest refusal, nothing executes, reason named | REPL → arg gates / FlowRefusal → receipt | **PROVEN (scoped)** — Core I per-atom gate; FLOW Profile B refusals (PR #417); DD-45 chain refusals |
| J-03 | Speak English intent → LatinMandell reading appears beside the receipt → chain executes | English → LM toll booth (LM-4) → Mandell → executor | **PARTIAL** — LM-4 live on main; the resource guard fires late (SYS-C34, fix in progress); ambiguity typing incomplete |
| J-04 | Create an idea → it persists → restart → the idea is intact with provenance | Nursery/Plane → persist → restart → load | **PARTIAL** — checkpoint path crash-proven; everyday save pair can expose a hybrid (SYS-C30, gated); Nursery store silently truncates long words (SYS-C29) |
| J-05 | Confirm a Nursery proposal → it lands on the Plane with placement asked/recorded | Nursery confirm → placement (Ace asked on mixed-wall; auto ⇒ sandbox first) → Plane | **PROVEN (scoped)** — confirm-placement PR #415 contract; ranking that orders proposals is designed-but-unbuilt (SYS-C27) |
| J-06 | Roll back to a sealed generation → live state converges to it | checkpoint generations → rollback | **PROVEN (scoped)** — sealed ≠ live law; eager convergence tested in its circuits |
| J-07 | Place ideas in space → see the same relationships in Flower, cube, and text views | SpatialAuthority → Plane positions → sacred_geometry / lattice readings → Studio surfaces | **VACUOUS on live content** — mechanism verified; all real ideas sit at (0,0); the readings agree because there is nothing to disagree about (SYS-C16) |
| J-08 | View the Tree of Harmonic Life in 3D → shells/slices match the admitted mathematics | FCC kernel → presentation layer | **NOT BUILT** — mathematics verified as research (THL-SM-01); admission pending (Keeper gate, then Director ruling); no runtime Tree exists |
| J-09 | Two ideas resonate → a candidate is proposed → Ace decides → accepted idea persists atomically | resonance → Nursery → confirm → persist | **BROKEN AT THE FIRST LINK** — resonance computes no geometry (its "vesica" is a log token, SYS-C24); the rest of the chain exists downstream |
| J-10 | Dock an AI (Psalm) → it assists within its permissions → its output stays PENDING until approved | Dock → Psalm surfaces → Nursery PENDING | **PARTIAL** — Gemini dock works; role/permission contracts implemented-unverified; prompt guard waste (SYS-C34) |
| J-11 | Run HCN orchestration → organs hand off with health tests and a ledger | HCN R3 → engines | **NOT BUILT** — no HCN engine exists in `form/` (grep-confirmed); R3 is a frozen design |
| J-12 | Interrupt the program mid-save (power-loss class) → restart → state is a proven old pair or target pair, or refuses loudly | persist → crash → load-time behavior | **SPLIT** — checkpoint path: PROVEN. Everyday path: FAILS the contract today (SYS-C30; repair owned by the C-A circuit under the load-time-convergence acceptance contract) |
| J-13 | Navigate the whole idea field in Studio → every perspective shows the same underlying facts | Studio surfaces → read models → canonical state | **UNVERIFIED** — surfaces exist; no cross-perspective consistency run has been executed (Grand Synchronization, Phase 8, is where this is proven) |
| J-14 | Grow a project (SELECT-scoped) → only the selected scope grows; a bare grow says so | growth path → SELECT law | **PROVEN (scoped)** — Ace's growth law implemented; sandbox-claim failures refuse by name on the receipt |
| J-15 | Address Dells through the Dell Lattice Index → the right Dells return, neighborhoods intact | registry → lattice index (FI-001) → executor | **PROPOSED** — Ace's feature, 2026-11-14; design in the Decision Register; placement law applies (measured relations only) |

## Reading the matrix

- **End-to-end system completion today: 0 of 15 journeys fully
  proven without a scope qualifier.** Four are proven within stated
  scopes (J-01, J-02, J-05, J-06, J-14 — five counting J-14), and
  their scopes are exactly the certified circuits' boundaries. This
  is the honest second measurement the Director's §6 requires,
  beside component completion (scoreboard).
- The matrix is a living test plan: each roadmap phase names the
  journeys it moves, and a journey's status changes only on executed
  public-path evidence at a pinned head — never on unit tests alone.

*End of Deliverable 7.*
