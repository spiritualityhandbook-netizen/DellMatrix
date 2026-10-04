# GDP-001 Phase 4 — Living Spatial Matrix: Acceptance Matrix

**Branch:** gdp-phase4-work · **Base:** 416620d996acebc5bbcff5e8de7376b737642a9e
**Status legend:** IMPLEMENTED / PARTIAL / DEFERRED / BLOCKED (no objective may quietly disappear)

## 4.1 MEANINGFUL PLACEMENT
| ID | Objective | Status | Evidence |
|---|---|---|---|
| 4.1.1 | Eliminate dishonest universal (0,0) | | |
| 4.1.2 | Deterministic traceable initial placement | | |
| 4.1.3 | Placement without destabilizing established state | | |
| 4.1.4 | Persist + reconstruct across save/load/checkpoint/rollback/fresh | | |
| 4.1.5 | Explanation of location + contributing inputs | | |

## 4.2 GRAVITY AND MOVEMENT
| ID | Objective | Status | Evidence |
|---|---|---|---|
| 4.2.1 | Legitimate mass/influence semantics | | |
| 4.2.2 | Bounded attraction from admitted influences | | |
| 4.2.3 | Bounded separation, no pathological pileups | | |
| 4.2.4 | Mental-map preservation | | |
| 4.2.5 | Convergence/equilibrium defined + measured; honest non-convergence | | |

## 4.3 PLANE
| ID | Objective | Status | Evidence |
|---|---|---|---|
| 4.3.1 | Plane coordinates computationally meaningful | | |
| 4.3.2 | Movement = explicit authorized mechanism with traceable cause | | |
| 4.3.3 | Regions/neighborhoods without geometric membership as truth | | |
| 4.3.4 | Read/mutate authority for spatial state defined | | |
| 4.3.5 | Location alone cannot mutate semantic truth | | |

## 4.4 LATTICE
| ID | Objective | Status | Evidence |
|---|---|---|---|
| 4.4.1 | One canonical spatial authority; Plane/Lattice reconciled | | |
| 4.4.2 | Computational neighborhoods | | |
| 4.4.3 | Legitimate clustering without forced semantic hierarchy | | |
| 4.4.4 | Resonance/relationship influence without becoming authority | | |
| 4.4.5 | Stable evolving placement on information change | | |

## 4.5 ENVIRONMENTAL FORCES
| ID | Objective | Status | Evidence |
|---|---|---|---|
| 4.5.1 | Weather = precise bounded computation (or retired claims) | | |
| 4.5.2 | Computational semantics for CLEAR/RAIN/FOG/STORM | | |
| 4.5.3 | Weather reconciled with Nature/Force; no duplicate authority | | |
| 4.5.4 | Environmental forces bounded; no silent semantic mutation | | |
| 4.5.5 | Every observable effect has traceable algorithmic referent | | |

## Authority map
| Mechanism | Classification |
|---|---|
| SpatialAuthority | AUTHORITATIVE OWNER (position decisions, dynamics state) |
| Plane.units | STORE (identity-keyed, persisted) |
| attract/separation/spring/friction/cooling | CALCULATOR (admitted equations) |
| resonance scores, graph edges, lifecycle, Weather | INPUT PROVIDER (read-only; Weather modulates force params only) |
| uniform grid hash | INDEX (rebuilt per tick) |
| HarmonicLattice, graph_view | PROJECTION (derived) |
| nature_physics | ADAPTER (retired as writer) |
| NatureBridge (writer), Plane.move | RETIRED |

## Mathematical admissions (16-field)
- mass_of, attract_well, separation_force, spring_force, weather_modulation: see spatial_authority.py docstrings.

## Preserved
- Verita transformation: PARKED. Advanced geometry (3.4.2–3.4.4): DEFERRED.
- EVALUATION_UNAVAILABLE_QUOTA: separate from required CI; never PASS.
