# GDP-001 Phase 4 — Living Spatial Matrix: Acceptance Matrix

**Branch:** gdp-phase4-work · **Base:** 416620d996acebc5bbcff5e8de7376b737642a9e
**Status legend:** IMPLEMENTED / PARTIAL / DEFERRED / BLOCKED (no objective may quietly disappear)

## 4.1 MEANINGFUL PLACEMENT
| ID | Objective | Status | Evidence |
|---|---|---|---|
| 4.1.1 | Eliminate dishonest universal (0,0) | IMPLEMENTED | p4_placement_dynamics_proof t1: 5 ideas, none at (0,0); spiral starts (-1,-1); (0,0) reserved neutral origin | |
| 4.1.2 | Deterministic traceable initial placement | IMPLEMENTED | t2: bit-identical across fresh processes; barycentric from graph neighbors else neutral spiral | |
| 4.1.3 | Placement without destabilizing established state | IMPLEMENTED | t7 mental-map: insert 1 into settled 5, originals move < 2.0 | |
| 4.1.4 | Persist + reconstruct across save/load/checkpoint/rollback/fresh | IMPLEMENTED | p4_acceptance_circuit phases 3-4: bit-identical reload; 'spatial' in DURABLE_KEYS | |
| 4.1.5 | Explanation of location + contributing inputs | IMPLEMENTED | spatial_explain: cause/anchors/env/tick; REPL 'spatial explain <id>' | |

## 4.2 GRAVITY AND MOVEMENT
| ID | Objective | Status | Evidence |
|---|---|---|---|
| 4.2.1 | Legitimate mass/influence semantics | IMPLEMENTED | mass_of admitted (16-field); docstring prohibits truth/importance reading | |
| 4.2.2 | Bounded attraction from admitted influences | IMPLEMENTED | attract_well admitted; MIN_DIST clamp; per-tick displacement cap | |
| 4.2.3 | Bounded separation, no pathological pileups | IMPLEMENTED | separation_force admitted; hard cutoff; coincidence deterministic | |
| 4.2.4 | Mental-map preservation | IMPLEMENTED | t7: bounded local consequence < 2.0 on insertion | |
| 4.2.5 | Convergence/equilibrium defined + measured; honest non-convergence | IMPLEMENTED | t6: converges ~244 ticks; EPS_DISP=1e-4 documented; honestly_non_convergent flag | |

## 4.3 PLANE
| ID | Objective | Status | Evidence |
|---|---|---|---|
| 4.3.1 | Plane coordinates computationally meaningful | IMPLEMENTED | Plane.units = authoritative store; positions drive dynamics, not decoration | |
| 4.3.2 | Movement = explicit authorized mechanism with traceable cause | IMPLEMENTED | SpatialAuthority.tick sole post-placement writer; tick reports moved/max_disp/state | |
| 4.3.3 | Regions/neighborhoods without geometric membership as truth | IMPLEMENTED | uniform grid = computational index only; neighborhoods are queries, not claims | |
| 4.3.4 | Read/mutate authority for spatial state defined | IMPLEMENTED | Authority map in matrix; Plane.move retired; nature_physics retired as writer | |
| 4.3.5 | Location alone cannot mutate semantic truth | IMPLEMENTED | p4_lattice_environment_proof semantic isolation: 20 ticks x 4 weathers, zero semantic change | |

## 4.4 LATTICE
| ID | Objective | Status | Evidence |
|---|---|---|---|
| 4.4.1 | One canonical spatial authority; Plane/Lattice reconciled | IMPLEMENTED | rebuild_from_plane derived projection; lattice.put mirror removed | |
| 4.4.2 | Computational neighborhoods | IMPLEMENTED | uniform grid hash rebuilt per tick; neighbor queries O(1) avg | |
| 4.4.3 | Legitimate clustering without forced semantic hierarchy | IMPLEMENTED | springs/separation create spatial clusters; no semantic hierarchy imposed | |
| 4.4.4 | Resonance/relationship influence without becoming authority | IMPLEMENTED | scores->mass, edges->springs; both INPUT PROVIDER, never deciders | |
| 4.4.5 | Stable evolving placement on information change | IMPLEMENTED | acceptance circuit phase 3: fade+storm -> bounded affected update | |

## 4.5 ENVIRONMENTAL FORCES
| ID | Objective | Status | Evidence |
|---|---|---|---|
| 4.5.1 | Weather = precise bounded computation (or retired claims) | IMPLEMENTED | WEATHER_TABLE: exact disp_mult/friction/radius_mult/jitter per mode | |
| 4.5.2 | Computational semantics for CLEAR/RAIN/FOG/STORM | IMPLEMENTED | weather_modulation admitted (16-field); unknown -> clear fail-safe | |
| 4.5.3 | Weather reconciled with Nature/Force; no duplicate authority | IMPLEMENTED | WeatherForce owns mode; SpatialAuthority owns spatial effects; nature retired | |
| 4.5.4 | Environmental forces bounded; no silent semantic mutation | IMPLEMENTED | storm jitter <= 0.1*cap; environmental isolation proof | |
| 4.5.5 | Every observable effect has traceable algorithmic referent | IMPLEMENTED | tick report: moved/max_disp/max_force/state/tick/temperature | |

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
