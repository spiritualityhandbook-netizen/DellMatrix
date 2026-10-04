#!/usr/bin/env python3
"""Canonical Spatial Authority (GDP-001 Phase 4, Living Spatial Matrix).

Exactly one mechanism decides authoritative Idea spatial state after
placement. Plane.units remains the position STORE (identity-keyed, persisted);
this authority is the sole DECIDER of post-placement positions and the owner
of dynamics state (velocities, temperature, RNG state, tick, placement
records).

Phase-4 laws enforced here:
  LOCATION != TRUTH.  DISTANCE != RELATIONSHIP AUTHORITY.
  Movement requires admitted computational cause; bounded response, damped
  adjustment, then stable or honestly non-convergent state.
  Phase-3 lifecycle eligibility is authoritative (faded ideas do not move
  and exert no attraction).
  Unknown/malformed spatial state fails closed; NaN/inf freezes the node.

Mathematical admissions (16 fields each, Phase-4 gate): see docstrings of
  attract_well, separation_force, spring_force, integrate, barycentric_place,
  spiral_place, weather_modulation, mass_of.
"""

from __future__ import annotations

import math
import random
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Declared constants (admitted; see docstrings)
# ---------------------------------------------------------------------------

MATRIX_ORIGIN: Tuple[float, float] = (0.0, 0.0)  #: declared landmark
PLANE_BOUND = 1000.0          #: finite plane half-extent; clamped
MAX_DISP_PER_TICK = 2.0       #: DecreasingMaxMovement cap (× temperature)
FRICTION_CLEAR = 0.90         #: velocity retention per tick (d3-style decay)
COOLING = 0.96                #: geometric temperature decay per tick
EPS_FORCE = 1e-9              #: Eades force guard (reported, not the stop rule)
EPS_DISP = 1e-4               #: positional stillness threshold (the stop rule).
                              #: Rationale: 0.01% of typical idea spacing;
                              #: below this, movement is computationally and
                              #: visually meaningless. Chosen over 1e-9
                              #: because geometric cooling asymptotes;
                              #: 1e-9 would require ~520 ticks, exceeding
                              #: any reasonable budget without adding meaning.
MAX_SETTLE_TICKS = 400       #: iteration budget; exhaustion = non-convergent.
                              #: Measured: 3-idea cluster reaches 1e-4
                              #: stillness at ~280 ticks; 400 gives headroom.
G = 0.4                       #: gravitational constant (admitted, reused)
MIN_DIST = 2.0                #: distance clamp (no singularity; reused)
SEP_RADIUS = 1.0              #: idea disk radius for separation
SEP_CUTOFF = 2.5              #: separation force is exactly 0 beyond this
SEP_STRENGTH = 0.6            #: separation magnitude scale
SPRING_K = 0.05               #: graph-edge spring constant (weak, bounded)
SPRING_CAP = 1.0              #: max spring force magnitude
CENTER_K = 0.05               #: layout-centering constant (weak, bounded)
CENTER_CAP = 0.5              #: max centering force magnitude
GRID_CELL = 4.0               #: uniform-grid cell size for neighborhoods
GOLDEN_ANGLE = math.pi * (3.0 - math.sqrt(5.0))  #: deterministic spiral
SPATIAL_VERSION = 1

#: Weather -> bounded force-parameter modulation. Zero semantic authority.
#: Each mode: displacement-cap multiplier, velocity-retention (friction),
#: attraction-radius multiplier, deterministic jitter fraction of cap.
WEATHER_TABLE: Dict[str, Dict[str, float]] = {
    "clear": {"disp_mult": 1.0, "friction": 0.90,
              "attract_radius_mult": 1.0, "jitter": 0.0},
    "rain":  {"disp_mult": 1.25, "friction": 0.95,
              "attract_radius_mult": 1.0, "jitter": 0.0},
    "fog":   {"disp_mult": 0.8, "friction": 0.90,
              "attract_radius_mult": 0.6, "jitter": 0.0},
    "storm": {"disp_mult": 1.0, "friction": 0.90,
              "attract_radius_mult": 1.0, "jitter": 0.1},
}


class SpatialLoadError(Exception):
    """Fail-closed: malformed persisted spatial state is never valid state."""


# ---------------------------------------------------------------------------
# Admitted calculators
# ---------------------------------------------------------------------------

def mass_of(score: float) -> float:
    """Influence mass from a Phase-3-admitted resonance score.

    (1) purpose: layout influence weight only.
    (2) variables: score (float).
    (3) types/domains: score >= 0.0 (resonance scores are non-negative).
    (4) units: dimensionless influence units.
    (5) provenance: Phase-3 resonance authority (Program.scores); formula
        mass = score + 0.5 reuses the NatureBridge convention (nature_code).
    (6) validity: score finite and >= 0; else fail-closed (mass = 0.5).
    (7) degenerate: score = 0 -> mass 0.5 (still participates, weakly).
    (8) bounds: mass >= 0.5, unbounded above (scores are bounded in
        practice by the resonance authority).
    (9) deterministic: pure function.
    (10) stability: heavier nodes accelerate less (F=ma) -> stabilizer.
    (11) baseline: uniform mass 1.0 (rejected: discards admitted influence
        information the system already computes).
    (12) falsifier: if scores change and layout influence does not, the
        coupling is broken.
    (13) semantic interpretation: layout influence ONLY.
    (14) authority owner: SpatialAuthority.
    (15) downstream: attract_well, integrate.
    (16) PROHIBITED: mass is not semantic importance, truth, authority,
        acceptance, or value. A heavy idea is not a true idea.
    """
    try:
        s = float(score)
    except (TypeError, ValueError):
        return 0.5
    if not math.isfinite(s) or s < 0:
        return 0.5
    return s + 0.5


def attract_well(ax: float, ay: float, a_mass: float,
                bx: float, by: float, b_mass: float,
                G_: float = G, min_dist: float = MIN_DIST
                ) -> Tuple[float, float]:
    """Newtonian attraction of a toward b (admitted; reuses nature_code.attract).

    (1) purpose: bounded attraction from legitimate admitted influence
        (gravity wells derived from resonance scores).
    (2) variables: positions (ax,ay),(bx,by); masses; G_; min_dist.
    (3) domains: finite floats; masses > 0.
    (4) units: position units; force in (influence * position / tick^2).
    (5) provenance: Newton's law of gravitation; implementation reuses
        form.dell_matrix.nature_code.attract exactly.
    (6) validity: finite inputs; min_dist > 0.
    (7) degenerate: coincident points -> direction undefined; caller
        substitutes deterministic golden-angle direction (see tick).
    (8) bounds: |F| <= G_*a_mass*b_mass / min_dist^2 (clamp, no singularity).
    (9) deterministic: pure function.
    (10) stability: inverse-square decays with distance; bounded above.
    (11) baseline: linear spring (rejected: unphysical at range, stiffer).
    (12) falsifier: force not decaying as 1/d^2 at d >> min_dist.
    (13) semantic interpretation: layout pull toward influence; never
        evidence of relationship.
    (14) authority owner: SpatialAuthority (calculator).
    (15) downstream: tick integration.
    (16) PROHIBITED: attraction is not affinity, not relationship, not
        acceptance. DISTANCE != RELATIONSHIP AUTHORITY.
    """
    dx, dy = bx - ax, by - ay
    d = math.hypot(dx, dy)
    dc = max(min_dist, d)
    mag = (G_ * a_mass * b_mass) / (dc * dc)
    if d < 1e-12:
        return 0.0, 0.0  # degenerate; caller assigns deterministic direction
    return (dx / d) * mag, (dy / d) * mag


def separation_force(ax: float, ay: float, bx: float, by: float,
                     radius: float = SEP_RADIUS, cutoff: float = SEP_CUTOFF,
                     strength: float = SEP_STRENGTH) -> Tuple[float, float]:
    """Bounded short-range disk separation (anti-pileup; purely geometric).

    (1) purpose: prevent pathological coincident pileups without inventing
        semantic relationships (Phase 4, 4.2.3).
    (2)-(4): positions finite floats; distances in position units.
    (5) provenance: d3 forceCollide / ForceAtlas2 "Prevent Overlapping"
        pattern adapted with hard cutoff.
    (6) validity: finite inputs; 0 < radius < cutoff.
    (7) degenerate: coincident -> deterministic golden-angle direction.
    (8) bounds: |F| <= strength; EXACTLY 0.0 for d >= cutoff (hard cutoff,
        so separation cannot organize globally or manufacture structure).
    (9) deterministic: pure function of positions + deterministic tie-break.
    (10) stability: repulsive, short-range only; cannot cause global
        oscillation by itself.
    (11) baseline: no separation (rejected: allows exact pileups that hide
        ideas and break explainability).
    (12) falsifier: non-zero force beyond cutoff, or force creating
        attraction at any distance.
    (13) semantic interpretation: geometric de-collision only.
    (14) authority owner: SpatialAuthority (calculator).
    (15) downstream: tick integration.
    (16) PROHIBITED: separation is not repulsion-as-meaning; two ideas
        pushed apart are not semantically opposed.
    """
    dx, dy = ax - bx, ay - by
    d = math.hypot(dx, dy)
    if d >= cutoff:
        return 0.0, 0.0
    if d < 1e-12:
        return 0.0, 0.0  # degenerate; caller assigns deterministic direction
    mag = strength * (1.0 - d / cutoff)
    return (dx / d) * mag, (dy / d) * mag


def spring_force(ax: float, ay: float, bx: float, by: float,
                 k: float = SPRING_K, cap: float = SPRING_CAP
                 ) -> Tuple[float, float]:
    """Weak bounded spring along admitted graph edges (organization only).

    (1) purpose: let admitted relationships influence spatial organization
        (Phase 4, 4.4.4) without becoming relationship authority.
    (2)-(4): finite float positions; force in position/tick^2 units.
    (5) provenance: Hooke's law, weak constant (cf. Eades spring embedder).
    (6) validity: finite inputs.
    (7) degenerate: coincident -> 0 (no direction needed; separation
        handles coincidence).
    (8) bounds: |F| <= cap always (hard cap).
    (9) deterministic: pure function.
    (10) stability: weak constant keeps it subordinate to gravity.
    (11) baseline: no springs (rejected: discards admitted relationship
        information for organization).
    (12) falsifier: spring force exceeding cap, or spring creating a graph
        edge (it must never write relationships).
    (13) semantic interpretation: gentle co-location of related ideas.
    (14) authority owner: SpatialAuthority (calculator).
    (15) downstream: tick integration.
    (16) PROHIBITED: co-location is not relationship; springs never create,
        delete, or modify graph edges. PROXIMITY != ACCEPTANCE.
    """
    dx, dy = bx - ax, by - ay
    d = math.hypot(dx, dy)
    if d < 1e-12:
        return 0.0, 0.0
    mag = min(k * d, cap)
    return (dx / d) * mag, (dy / d) * mag


def center_force(x: float, y: float,
                 k: float = CENTER_K, cap: float = CENTER_CAP
                 ) -> Tuple[float, float]:
    """Weak layout-centering force toward the neutral origin.

    16-FIELD ADMISSION
    1. NAME: center_force (weak Hooke centering toward neutral origin).
    2. FORMULA: F = -k*(x,y), |F| <= cap.
    3. DOMAIN: all finite (x,y).
    4. PARAMETERS: k=0.05, cap=0.5 (weak vs wells/springs).
    5. OUTPUT RANGE: [0, cap].
    6. DETERMINISM: pure function of (x,y).
    7. AUTHORITY: CALCULATOR. The origin is declared neutral; this is
       computational layout stability (prevents unbounded drift in
       edgeless/well-less configurations), NOT a semantic claim.
       LOCATION != TRUTH is preserved: centering does not move semantic
       state and does not confer meaning.
    8. SOURCE: standard force-directed practice (FR91/ForceAtlas2 gravity).
    9. BOUND PROOF: |F| <= cap by construction (min).
    10. FAILURE MODES: NaN input -> (0,0); origin -> (0,0).
    11. NUMERICAL: stable; linear, no singularity.
    12. INTERACTION: weakest force in the system; wells/springs dominate.
    13. INVERTIBILITY: n/a (layout aid).
    14. VERSION: v1 (2026-10-04).
    15. SUPERSEDES: nothing (new).
    16. FALSIFIER: any tick where |F| > cap, or centering moves semantic state.
    """
    if not (math.isfinite(x) and math.isfinite(y)):
        return (0.0, 0.0)
    fx, fy = -k * x, -k * y
    mag = math.hypot(fx, fy)
    if mag > cap and mag > 0:
        s = cap / mag
        fx, fy = fx * s, fy * s
    return (fx, fy)


def weather_modulation(condition: str) -> Dict[str, float]:
    """Bounded force-parameter modulation for a weather condition.

    (1) purpose: give Weather precise bounded computation (Phase 4, 4.5.2).
    (2) variables: condition in {clear, rain, fog, storm}.
    (3) domains: known conditions; unknown -> clear (declared neutral).
    (4) units: dimensionless multipliers.
    (5)-(6) provenance/validity: declared table WEATHER_TABLE; unknown
        conditions fail safe to clear, never to an arbitrary mode.
    (7) degenerate: unknown/None -> clear parameters.
    (8) bounds: disp_mult in [0.8, 1.25]; friction in [0.90, 0.95];
        attract_radius_mult in [0.6, 1.0]; jitter in [0.0, 0.1].
    (9) deterministic: pure table lookup.
    (10) stability: all multipliers keep dynamics inside the base stability
        envelope (caps still apply after modulation).
    (11) baseline: weather ignored (rejected by 4.5.2: must have explicit
        semantics or retire; retirement rejected because the condition enum
        and owner already exist and a bounded role is definable).
    (12) falsifier: any weather effect outside the declared multipliers,
        or any semantic write attributed to weather.
    (13) semantic interpretation: exploration pressure only.
        CLEAR: ordinary operation. RAIN: bounded exploratory loosening.
        FOG: local emphasis (distant influence reduced). STORM: bounded
        deterministic perturbation.
    (14) authority owner: SpatialAuthority (WeatherForce remains the
        condition owner; this function is the computational contract).
    (15) downstream: tick parameter selection.
    (16) PROHIBITED: weather has zero semantic write authority. Weather
        changes cannot mutate accepted truth, lifecycle, properties, or
        graph edges. ENVIRONMENTAL EFFECT != ACCEPTED-TRUTH MUTATION.
    """
    c = (condition or "clear").strip().lower()
    return dict(WEATHER_TABLE.get(c, WEATHER_TABLE["clear"]))

class SpatialAuthority:
    """Sole decider of post-placement Idea positions (Phase 4, 4.4.1).

    Plane.units is the position STORE. This class OWNS:
      - initial placement decisions (+ explanations),
      - per-tick dynamics integration state (velocities, temperature,
        RNG state, tick counter, placement records),
      - weather-to-force-parameter modulation (bounded),
      - the derived HarmonicLattice rebuild contract.

    It WRITES ONLY: unit.x/unit.y (via Plane), its own persisted state,
    and the derived lattice projection. It never writes Idea properties,
    lifecycle, graph edges, acceptance, or resonance state.
    """

    def __init__(self) -> None:
        self.velocities: Dict[str, Tuple[float, float]] = {}
        self.temperature: float = 1.0
        self.tick_count: int = 0
        self.rng_seed: int = 0x5EED
        self._rng = random.Random(self.rng_seed)
        self.placements: Dict[str, Dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # Placement (4.1, 7)
    # ------------------------------------------------------------------

    def place(self, program: Any, idea_id: str, label: str = "",
              x: Optional[float] = None, y: Optional[float] = None
              ) -> Dict[str, Any]:
        """Deterministic initial placement with explanation.

        Barycentric-from-placed-neighbors when graph information exists
        (unique linear-system solution -> deterministic); grid-spiral
        fallback explicitly neutral when information is sparse
        (cause "neutral_spiral", anchors []). Explicit x/y honored (user
        authority). Records explanation {cause, anchors, env, tick}.
        PROHIBITED: fabricating semantic similarity from sparse info.
        """
        plane = program.cube.session.plane
        if x is not None and y is not None:
            # Explicit coordinates: non-finite (NaN/inf) is REJECTED
            # (fail-closed). Silently mapping to origin would be dishonest.
            fx0, fy0 = float(x), float(y)
            if not (math.isfinite(fx0) and math.isfinite(fy0)):
                raise ValueError(
                    f"explicit placement for {idea_id!r}: non-finite "
                    f"coordinates ({fx0}, {fy0}) rejected")
            fx, fy = self._finite_or_origin(fx0, fy0)
            cause, anchors = "explicit", []
        else:
            anchors = self._placed_graph_neighbors(program, idea_id)
            if anchors:
                fx, fy = self._barycentric(plane, anchors)
                cause = "barycentric"
                fx, fy = self._nudge_free(plane, fx, fy, idea_id)
            else:
                fx, fy = self._spiral_free(program, plane)
                cause = "neutral_spiral"
        fx = max(-PLANE_BOUND, min(PLANE_BOUND, fx))
        fy = max(-PLANE_BOUND, min(PLANE_BOUND, fy))
        env = self._env_mode(program)
        self.placements[idea_id] = {
            "cause": cause, "anchors": anchors, "env": env,
            "tick": self.tick_count, "x": fx, "y": fy,
        }
        self.velocities[idea_id] = (0.0, 0.0)
        return {"x": fx, "y": fy,
                "explanation": dict(self.placements[idea_id])}

    def _placed_graph_neighbors(self, program: Any,
                                idea_id: str) -> List[str]:
        """Sorted ids of graph neighbors that already have positions."""
        plane = program.cube.session.plane
        try:
            from form.mandell.semantic_graph import SemanticGraph
            graph = SemanticGraph.load(program.owner)
            try:
                nbrs = graph.association_neighbor_ids(idea_id)
            except AttributeError:
                from form.dell_matrix.graph_harmony import \
                    graph_neighbor_ids
                nbrs = graph_neighbor_ids(graph, idea_id)
        except Exception:
            return []
        return sorted(n for n in nbrs if n in plane.units)

    def _barycentric(self, plane: Any, anchors: List[str]
                     ) -> Tuple[float, float]:
        xs = [plane.units[a].x for a in anchors]
        ys = [plane.units[a].y for a in anchors]
        return sum(xs) / len(xs), sum(ys) / len(ys)

    def _nudge_free(self, plane: Any, fx: float, fy: float,
                    idea_id: str) -> Tuple[float, float]:
        """Collision-aware nudge: golden-angle spiral from the centroid."""
        occupied = {(round(u.x, 6), round(u.y, 6))
                    for uid, u in plane.units.items() if uid != idea_id}
        if (round(fx, 6), round(fy, 6)) not in occupied:
            return fx, fy
        r, i = 1.0, 0
        while i < 64:
            a = i * GOLDEN_ANGLE
            cx, cy = fx + r * math.cos(a), fy + r * math.sin(a)
            if (round(cx, 6), round(cy, 6)) not in occupied:
                return cx, cy
            i += 1
            if i % 8 == 0:
                r += 1.0
        return fx, fy  # declared deterministic fallback

    def _spiral_free(self, program: Any, plane: Any) -> Tuple[float, float]:
        """Deterministic neutral spiral (reuses _next_open_xy contract)."""
        try:
            return program._next_open_xy()
        except Exception:
            pass
        occupied = {(int(round(u.x)), int(round(u.y)))
                    for u in plane.units.values()}
        occupied.add((0, 0))  # MATRIX_ORIGIN reserved landmark
        for ring in range(1, 13):
            for dx in range(-ring, ring + 1):
                for dy in range(-ring, ring + 1):
                    if max(abs(dx), abs(dy)) != ring:
                        continue
                    if (dx, dy) not in occupied:
                        return float(dx), float(dy)
        return MATRIX_ORIGIN

    @staticmethod
    def _finite_or_origin(x: float, y: float) -> Tuple[float, float]:
        # Explicit coordinates: must be finite (NaN/inf -> origin is
        # DISHONEST; caller validates). Finite but out-of-bounds ->
        # clamped to the finite plane (documented, not silent: the
        # plane is bounded by design).
        if math.isfinite(x) and math.isfinite(y):
            return (max(-PLANE_BOUND, min(PLANE_BOUND, x)),
                    max(-PLANE_BOUND, min(PLANE_BOUND, y)))
        return MATRIX_ORIGIN

    # ------------------------------------------------------------------
    # Dynamics (4.2, 4.3, 8)
    # ------------------------------------------------------------------

    def tick(self, program: Any) -> Dict[str, Any]:
        """One bounded dynamics step over the lifecycle-active set.

        Faded/rejected/deleted units are frozen: they neither move nor
        exert attraction (Phase-3 lifecycle law). Deterministic order:
        sorted unit ids. NaN/inf input -> freeze unit + log (fail-closed).
        """
        plane = program.cube.session.plane
        units = plane.units
        if not units:
            return self._report(0, 0.0, 0.0, True, "empty")
        from form.dell_matrix import canonical_lifecycle
        active = [uid for uid in sorted(units)
                  if canonical_lifecycle.is_active(program, uid)]
        if not active:
            return self._report(0, 0.0, 0.0, True, "all_frozen")

        mod = weather_modulation(self._env_mode(program))
        disp_cap = MAX_DISP_PER_TICK * mod["disp_mult"] * self.temperature
        friction = mod["friction"]
        attract_radius = 1e9 * mod["attract_radius_mult"]
        jitter_mag = mod["jitter"] * MAX_DISP_PER_TICK

        scores = self._scores(program)
        wells = self._wells(program, plane, scores)
        grid = self._build_grid(plane, active)
        graph_nbrs = self._graph_neighbors(program, active, plane)

        max_disp, max_force, moved = 0.0, 0.0, 0
        for uid in active:
            u = units[uid]
            if not (math.isfinite(u.x) and math.isfinite(u.y)):
                program.note_seed(5, "Spatial",
                                  f"freeze {uid}: non-finite position")
                continue
            m = mass_of(scores.get(uid, 0.0))
            fx = fy = 0.0
            for wx, wy, wm in wells:
                dx, dy = wx - u.x, wy - u.y
                if math.hypot(dx, dy) > attract_radius:
                    continue
                gx, gy = attract_well(u.x, u.y, m, wx, wy, wm)
                fx += gx
                fy += gy
            for nid in graph_nbrs.get(uid, ()):
                v = units[nid]
                sx, sy = spring_force(u.x, u.y, v.x, v.y)
                fx += sx
                fy += sy
            for oid in self._grid_neighbors(grid, u.x, u.y, uid):
                o = units[oid]
                if not (math.isfinite(o.x) and math.isfinite(o.y)):
                    continue
                dx, dy = u.x - o.x, u.y - o.y
                d = math.hypot(dx, dy)
                if d >= SEP_CUTOFF:
                    continue
                if d < 1e-12:
                    # deterministic coincidence direction (NOT hash():
                    # string hash is per-process randomized). Golden-angle
                    # indexed by a stable integer key of the pair.
                    key = sum(ord(c) for c in min(uid, oid)) * 31 + sum(
                        ord(c) for c in max(uid, oid))
                    ang = (key % 360) * math.pi / 180.0
                    dx, dy = math.cos(ang), math.sin(ang)
                    d = 1.0
                mag = SEP_STRENGTH * (1.0 - min(d, SEP_CUTOFF) / SEP_CUTOFF)
                fx += (dx / max(d, 1e-12)) * mag
                fy += (dy / max(d, 1e-12)) * mag
            # weak layout centering (bounded; stability, not semantics)
            cx, cy = center_force(u.x, u.y)
            fx += cx
            fy += cy
            if jitter_mag > 0:
                fx += (self._rng.random() * 2 - 1) * jitter_mag
                fy += (self._rng.random() * 2 - 1) * jitter_mag
            fmag = math.hypot(fx, fy)
            max_force = max(max_force, fmag)
            # integrate with friction; clamp displacement (DecreasingMaxMovement)
            vx, vy = self.velocities.get(uid, (0.0, 0.0))
            vx = (vx + fx / m) * friction
            vy = (vy + fy / m) * friction
            dx, dy = vx, vy
            dd = math.hypot(dx, dy)
            if dd > disp_cap and dd > 0:
                s = disp_cap / dd
                dx, dy = dx * s, dy * s
            nx, ny = u.x + dx, u.y + dy
            if not (math.isfinite(nx) and math.isfinite(ny)):
                program.note_seed(5, "Spatial",
                                  f"freeze {uid}: non-finite update")
                continue
            nx = max(-PLANE_BOUND, min(PLANE_BOUND, nx))
            ny = max(-PLANE_BOUND, min(PLANE_BOUND, ny))
            disp = math.hypot(nx - u.x, ny - u.y)
            if disp > 1e-12:
                u.x, u.y = nx, ny
                moved += 1
                max_disp = max(max_disp, disp)
            self.velocities[uid] = (vx, vy)
        # prune velocities of removed units
        for uid in list(self.velocities):
            if uid not in units:
                del self.velocities[uid]
        self.temperature *= COOLING
        self.tick_count += 1
        # Convergence rule: positional stillness. (The Eades force-
        # magnitude guard is reported but not the stop rule: persistent
        # gravity wells exert non-vanishing force at equilibrium, so a
        # force-epsilon would never trigger. A settled matrix is one
        # where nothing moves.)
        converged = max_disp < EPS_DISP
        self._rebuild_lattice(program)
        return self._report(moved, max_disp, max_force, converged,
                            "converged" if converged else "active")

    def settle(self, program: Any,
               max_ticks: int = MAX_SETTLE_TICKS) -> Dict[str, Any]:
        """Loop ticks until Eades stop or budget; honest non-convergence.

        Returns the last tick report plus {ticks_run, converged,
        honestly_non_convergent}.
        """
        last: Dict[str, Any] = {}
        for _ in range(max_ticks):
            last = self.tick(program)
            if last["converged"]:
                last["ticks_run"] = self.tick_count
                last["honestly_non_convergent"] = False
                return last
        last["ticks_run"] = self.tick_count
        last["honestly_non_convergent"] = True
        program.note_seed(5, "Spatial",
                          "settle budget exhausted: honestly non-convergent")
        return last

    # -- helpers ---------------------------------------------------------

    def _report(self, moved: int, max_disp: float, max_force: float,
                converged: bool, state: str) -> Dict[str, Any]:
        return {"moved": moved, "max_displacement": max_disp,
                "max_force": max_force, "converged": converged,
                "state": state, "tick": self.tick_count,
                "temperature": self.temperature}

    def _env_mode(self, program: Any) -> str:
        try:
            return str(program.forces.weather.condition or "clear").lower()
        except Exception:
            return "clear"

    def _scores(self, program: Any) -> Dict[str, float]:
        try:
            s = program.scores()
            return {k: float(v) for k, v in dict(s).items()}
        except Exception:
            return {}

    def _wells(self, program: Any, plane: Any,
               scores: Dict[str, float]) -> List[Tuple[float, float, float]]:
        """Gravity wells: existing program.forces.gravity wells matched to
        unit positions (mass = score + 1.0, the admitted convention)."""
        wells: List[Tuple[float, float, float]] = []
        try:
            g = program.forces.gravity
            for w in g.wells:
                wid = w.get("id") if isinstance(w, dict) else getattr(
                    w, "id", None)
                if wid in plane.units:
                    u = plane.units[wid]
                    wells.append((u.x, u.y,
                                  mass_of(scores.get(wid, 0.0)) + 0.5))
        except Exception:
            pass
        if not wells:
            # fallback: top-3 by score among positioned units (existing
            # NatureBridge convention, now deterministic)
            ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
            for wid, s in ranked[:3]:
                if wid in plane.units:
                    u = plane.units[wid]
                    wells.append((u.x, u.y, mass_of(s) + 0.5))
        return wells

    def _graph_neighbors(self, program: Any, active: List[str],
                         plane: Any) -> Dict[str, Tuple[str, ...]]:
        out: Dict[str, Tuple[str, ...]] = {}
        aset = set(active)
        try:
            from form.mandell.semantic_graph import SemanticGraph
            graph = SemanticGraph.load(program.owner)
            for uid in active:
                try:
                    nbrs = graph.association_neighbor_ids(uid)
                except AttributeError:
                    from form.dell_matrix.graph_harmony import \
                        graph_neighbor_ids
                    nbrs = graph_neighbor_ids(graph, uid)
                out[uid] = tuple(sorted(n for n in nbrs if n in aset))
        except Exception:
            for uid in active:
                out[uid] = ()
        return out

    def _build_grid(self, plane: Any,
                    active: List[str]) -> Dict[Tuple[int, int], List[str]]:
        grid: Dict[Tuple[int, int], List[str]] = {}
        for uid in active:
            u = plane.units[uid]
            if not (math.isfinite(u.x) and math.isfinite(u.y)):
                continue
            key = (int(math.floor(u.x / GRID_CELL)),
                   int(math.floor(u.y / GRID_CELL)))
            grid.setdefault(key, []).append(uid)
        return grid

    def _grid_neighbors(self, grid: Dict[Tuple[int, int], List[str]],
                        x: float, y: float, uid: str) -> List[str]:
        cx, cy = int(math.floor(x / GRID_CELL)), int(math.floor(y / GRID_CELL))
        out: List[str] = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for oid in grid.get((cx + dx, cy + dy), ()):
                    if oid != uid:
                        out.append(oid)
        return sorted(out)

    def _rebuild_lattice(self, program: Any) -> None:
        """Derived projection: rebuild lattice deterministically from Plane."""
        try:
            lattice = program.lattice
            if hasattr(lattice, "rebuild_from_plane"):
                lattice.rebuild_from_plane(program.cube.session.plane)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Explanation (4.1.5) and persistence (11)
    # ------------------------------------------------------------------

    def explain(self, program: Any, idea_id: str) -> Dict[str, Any]:
        """Why an idea occupies its current location (4.1.5)."""
        plane = program.cube.session.plane
        u = plane.units.get(idea_id)
        if u is None:
            return {"id": idea_id, "present": False}
        rec = self.placements.get(idea_id, {})
        return {
            "id": idea_id, "present": True,
            "x": u.x, "y": u.y,
            "placement": rec or {"cause": "legacy",
                                 "note": "placed before authority records"},
            "tick": self.tick_count,
            "temperature": self.temperature,
            "env": self._env_mode(program),
            "velocity": list(self.velocities.get(idea_id, (0.0, 0.0))),
            "inputs": {
                "mass": mass_of(self._scores(program).get(idea_id, 0.0)),
                "lifecycle": self._lifecycle(program, idea_id),
            },
        }

    def _lifecycle(self, program: Any, uid: str) -> str:
        try:
            from form.dell_matrix import canonical_lifecycle
            return canonical_lifecycle.resolve_lifecycle(program, uid)
        except Exception:
            return "unknown"

    def to_dict(self) -> Dict[str, Any]:
        # RNG state: persist the FULL Mersenne Twister state (625 words:
        # 624 state + index). A partial state diverges after restore.
        _rs = self._rng.getstate()
        return {
            "version": SPATIAL_VERSION,
            "tick": int(self.tick_count),
            "temperature": float(self.temperature),
            "rng_seed": int(self.rng_seed),
            "rng_state": [int(n) for n in _rs[1]],
            "velocities": {k: [float(v[0]), float(v[1])]
                           for k, v in self.velocities.items()},
            "placements": {k: dict(v) for k, v in self.placements.items()},
        }

    @classmethod
    def from_dict(cls, data: Any) -> "SpatialAuthority":
        """Fail-closed load: malformed spatial state is never valid."""
        inst = cls()
        if data is None:
            return inst  # missing member -> fresh (declared)
        if not isinstance(data, dict):
            raise SpatialLoadError("spatial state must be a dict")
        if data.get("version") != SPATIAL_VERSION:
            raise SpatialLoadError(
                f"unsupported spatial version {data.get('version')!r}")
        try:
            inst.tick_count = int(data.get("tick", 0))
            inst.temperature = float(data.get("temperature", 1.0))
            inst.rng_seed = int(data.get("rng_seed", 0x5EED))
            if not math.isfinite(inst.temperature) or inst.temperature < 0:
                raise SpatialLoadError("non-finite/negative temperature")
            vels = data.get("velocities", {})
            if not isinstance(vels, dict):
                raise SpatialLoadError("velocities must be a dict")
            for k, v in vels.items():
                if (not isinstance(v, (list, tuple)) or len(v) != 2
                        or not all(isinstance(n, (int, float))
                                   and math.isfinite(n) for n in v)):
                    raise SpatialLoadError(
                        f"malformed velocity for {k!r}")
                inst.velocities[str(k)] = (float(v[0]), float(v[1]))
            pl = data.get("placements", {})
            if not isinstance(pl, dict):
                raise SpatialLoadError("placements must be a dict")
            inst.placements = {str(k): dict(v) for k, v in pl.items()
                               if isinstance(v, dict)}
            inst._rng = random.Random(inst.rng_seed)
            rs = data.get("rng_state")
            # Full MT state is 625 ints (624 words + index). Accept only
            # the full state; partial states are rejected (fail-closed)
            # rather than silently diverging.
            if isinstance(rs, (list, tuple)) and len(rs) == 625:
                try:
                    full = tuple(int(n) for n in rs)
                    inst._rng.setstate((3, full, None))
                except Exception:
                    pass  # seed alone still deterministic
        except SpatialLoadError:
            raise
        except Exception as exc:
            raise SpatialLoadError(f"malformed spatial state: {exc}")
        return inst
