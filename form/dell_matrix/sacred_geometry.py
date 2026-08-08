#!/usr/bin/env python3
"""
Sacred geometry + structural pattern layer — form/ only.

  Flower of Life  — equal circles on hexagonal centers (Seed · FoL · Fruit of Life)
  Vesica / Verita — two-circle overlap (vesica piscis) + Veritas strength (truth of meet)
  Voynich rings   — organizational 5-ring metaphor only (NOT decryption)
  Fractals        — Rule 90 · bounded orbit · self-similar shells

Law: geometry is perception/structure. Voynich stays interpretive.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import math

# ---------------------------------------------------------------------------
# Flower of Life
# ---------------------------------------------------------------------------

def flower_centers(rings: int = 2, radius: float = 1.0) -> List[Tuple[float, float]]:
    """
    Flower of Life center points (hex packing).
    rings=0: origin only (seed)
    rings=1: Seed of Life (origin + 6)
    rings=2+: Flower of Life rings
    """
    centers: List[Tuple[float, float]] = [(0.0, 0.0)]
    rings = max(0, int(rings))
    if rings < 1:
        return centers
    for r in range(1, rings + 1):
        for corner in range(6):
            ang0 = math.radians(60 * corner)
            ang1 = math.radians(60 * ((corner + 1) % 6))
            c0 = (r * radius * math.cos(ang0), r * radius * math.sin(ang0))
            c1 = (r * radius * math.cos(ang1), r * radius * math.sin(ang1))
            centers.append(c0)
            for e in range(1, r):
                t = e / r
                centers.append((c0[0] * (1 - t) + c1[0] * t, c0[1] * (1 - t) + c1[1] * t))
    out: List[Tuple[float, float]] = []
    seen = set()
    for x, y in centers:
        key = (round(x, 5), round(y, 5))
        if key not in seen:
            seen.add(key)
            out.append((x, y))
    return out


def flower_circles(rings: int = 2, radius: float = 1.0) -> List[Dict[str, float]]:
    """Each FoL center as a circle of equal radius (draw payload)."""
    return [{"x": x, "y": y, "r": radius} for x, y in flower_centers(rings, radius)]


def seed_of_life() -> List[Tuple[float, float]]:
    return flower_centers(rings=1, radius=1.0)


def fruit_of_life_centers(radius: float = 1.0) -> List[Tuple[float, float]]:
    """13-circle Fruit of Life subset (origin + 6 + 6 at 2R)."""
    pts = [(0.0, 0.0)]
    for k in range(6):
        ang = math.radians(60 * k)
        pts.append((radius * math.cos(ang), radius * math.sin(ang)))
        pts.append((2 * radius * math.cos(ang), 2 * radius * math.sin(ang)))
    return pts


def flower_draw_payload(
    rings: int = 2,
    radius: float = 1.0,
    *,
    include_vesica: bool = True,
    include_fruit: bool = False,
) -> Dict[str, Any]:
    """Full draw package for live/snapshot SVG."""
    centers = flower_centers(rings, radius)
    circles = flower_circles(rings, radius)
    vesicas = vesica_pairs_from_centers(centers, radius) if include_vesica else []
    payload: Dict[str, Any] = {
        "kind": "flower_of_life",
        "rings": rings,
        "radius": radius,
        "centers": [{"x": x, "y": y} for x, y in centers],
        "circles": circles,
        "center_count": len(centers),
        "vesicas": vesicas[:48],  # cap for draw
        "vesica_count": len(vesicas),
        "seed_count": 7,
    }
    if include_fruit:
        payload["fruit"] = [{"x": x, "y": y} for x, y in fruit_of_life_centers(radius)]
    return payload


# ---------------------------------------------------------------------------
# Vesica Piscis + Verita (Veritas = truth-of-meet strength)
# ---------------------------------------------------------------------------

def vesica(
    ax: float, ay: float, ar: float,
    bx: float, by: float, br: float,
) -> Dict[str, Any]:
    """
    Vesica piscis between two circles.
    Verita (Veritas): continuous strength 0..1 of their meeting.
    """
    dx = bx - ax
    dy = by - ay
    dist = math.hypot(dx, dy)
    sum_r = ar + br
    diff_r = abs(ar - br)
    if dist < 1e-12:
        return {
            "distance": 0.0,
            "type": "coincident",
            "strength": 1.0,
            "verita": 1.0,
            "lens_width": 0.0,
            "mid": [ax, ay],
        }
    if dist >= sum_r:
        return {
            "distance": dist,
            "type": "separate",
            "strength": 0.0,
            "verita": 0.0,
            "lens_width": 0.0,
            "mid": [(ax + bx) / 2, (ay + by) / 2],
        }
    if dist <= diff_r:
        return {
            "distance": dist,
            "type": "contained",
            "strength": 1.0,
            "verita": 0.85,  # nested but not classic vesica
            "lens_width": min(ar, br) * 2,
            "mid": [bx, by] if br < ar else [ax, ay],
        }
    # classic vesica — strength peaks when dist ≈ radius (equal circles)
    strength = float(1.0 - (dist - diff_r) / max(1e-9, sum_r - diff_r))
    # Verita: favor equal-radius pure vesica (dist ≈ R for equal R)
    ideal = (ar + br) / 2.0  # for equal circles, ideal vesica center meet ~ R
    verita = strength * (1.0 - min(1.0, abs(dist - ideal) / max(ideal, 1e-9)) * 0.5)
    verita = max(0.0, min(1.0, verita))
    # approximate lens half-width
    # formula for half chord length
    try:
        a = (ar * ar - br * br + dist * dist) / (2 * dist)
        h = math.sqrt(max(0.0, ar * ar - a * a))
    except Exception:
        h = 0.0
    mid_x = ax + (dx / dist) * ((ar * ar - br * br + dist * dist) / (2 * dist))
    mid_y = ay + (dy / dist) * ((ar * ar - br * br + dist * dist) / (2 * dist))
    return {
        "distance": round(dist, 4),
        "type": "vesica",
        "strength": round(strength, 4),
        "verita": round(verita, 4),
        "lens_width": round(2 * h, 4),
        "mid": [round(mid_x, 4), round(mid_y, 4)],
        "a": [ax, ay, ar],
        "b": [bx, by, br],
    }


def vesica_pairs_from_centers(
    centers: List[Tuple[float, float]],
    radius: float = 1.0,
    *,
    min_verita: float = 0.15,
) -> List[Dict[str, Any]]:
    """All neighboring FoL pairs that form a vesica (dist ≈ radius)."""
    pairs = []
    for i, (ax, ay) in enumerate(centers):
        for bx, by in centers[i + 1 :]:
            d = math.hypot(bx - ax, by - ay)
            # neighbors in FoL are at distance ≈ radius
            if d > radius * 2.05 or d < radius * 0.2:
                continue
            v = vesica(ax, ay, radius, bx, by, radius)
            if v["verita"] >= min_verita and v["type"] in ("vesica", "contained"):
                pairs.append({
                    **v,
                    "from": [ax, ay],
                    "to": [bx, by],
                })
    return pairs


def verita_between_nodes(
    nodes: List[Dict[str, Any]],
    *,
    radius_scale: float = 1.2,
    max_dist: float = 3.5,
    min_verita: float = 0.2,
) -> List[Dict[str, Any]]:
    """
    Compute Verita/vesica edges between idea nodes (not all-pairs spam).
    Closer + higher score → stronger verita.
    """
    edges = []
    for i, a in enumerate(nodes):
        for b in nodes[i + 1 :]:
            ax, ay = float(a.get("x", 0)), float(a.get("y", 0))
            bx, by = float(b.get("x", 0)), float(b.get("y", 0))
            dist = math.hypot(bx - ax, by - ay)
            if dist < 0.01 or dist > max_dist:
                continue
            # radius from score (heavier ideas cast larger circles)
            ar = radius_scale * (0.6 + 0.4 * min(2.0, float(a.get("score") or 0)))
            br = radius_scale * (0.6 + 0.4 * min(2.0, float(b.get("score") or 0)))
            v = vesica(ax, ay, ar, bx, by, br)
            if v["type"] == "separate":
                # soft falloff if close even without full circle meet
                soft = max(0.0, 1.0 - dist / max_dist) * 0.35
                if soft < min_verita:
                    continue
                v["verita"] = round(soft, 4)
                v["type"] = "near"
            if v["verita"] < min_verita:
                continue
            edges.append({
                "source": a.get("id"),
                "target": b.get("id"),
                "kind": "vesica",
                "verita": v["verita"],
                "strength": v.get("strength", v["verita"]),
                "distance": v["distance"],
                "type": v["type"],
                "mid": v.get("mid"),
            })
    edges.sort(key=lambda e: -float(e["verita"]))
    return edges


# ---------------------------------------------------------------------------
# Voynich structural rings (organizational only — NOT decryption)
# ---------------------------------------------------------------------------

VOYNICH_RINGS: Tuple[Dict[str, Any], ...] = (
    {"id": "seed", "name": "Seed", "metaphor": "Herbal · whole live specimen",
     "role": "confirmed idea on plane", "stage": 0},
    {"id": "token", "name": "Token", "metaphor": "Pharma · parts before whole",
     "role": "nursery proposal / part", "stage": 1},
    {"id": "body", "name": "Body", "metaphor": "Balneological · flow channels",
     "role": "avatar · companion · edges", "stage": 2},
    {"id": "lens", "name": "Lens", "metaphor": "Astro · circular reading",
     "role": "perception · view room · persona", "stage": 3},
    {"id": "evolve", "name": "Evolve", "metaphor": "Recipe · executable sequence",
     "role": "grow · confirm · evolve · accept", "stage": 4},
)

# DuoBeta alias
VOYNICH_PIPELINE = ("Seed", "Token", "Body", "Lens", "Evolve")


def voynich_ring_for_unit(unit: Dict[str, Any], *, in_nursery: bool = False) -> Dict[str, Any]:
    """Assign structural ring metaphor from unit state (not translation)."""
    if in_nursery:
        return dict(VOYNICH_RINGS[1])  # Token / pharma quarantine
    sc = float(unit.get("score") or 0)
    skin = str(unit.get("skin") or "")
    if unit.get("sandboxed"):
        return dict(VOYNICH_RINGS[1])
    if sc >= 1.5 or skin in ("building", "flower"):
        return dict(VOYNICH_RINGS[4])  # Evolve-ish mature
    if sc >= 0.8:
        return dict(VOYNICH_RINGS[3])  # Lens
    if sc >= 0.3:
        return dict(VOYNICH_RINGS[2])  # Body
    return dict(VOYNICH_RINGS[0])  # Seed


def voynich_status(program=None) -> Dict[str, Any]:
    """Structural Voynich lens status for Program."""
    rings = [dict(r) for r in VOYNICH_RINGS]
    counts = {r["id"]: 0 for r in VOYNICH_RINGS}
    tagged = []
    if program is not None:
        nodes = program.nodes_payload() if hasattr(program, "nodes_payload") else []
        nursery = program.ranked_proposals() if hasattr(program, "ranked_proposals") else []
        for n in nodes:
            ring = voynich_ring_for_unit(n, in_nursery=False)
            counts[ring["id"]] = counts.get(ring["id"], 0) + 1
            tagged.append({"id": n.get("id"), "label": n.get("label"), "ring": ring["id"]})
        for prop in nursery:
            counts["token"] = counts.get("token", 0) + 1
            tagged.append({"id": prop.get("id"), "label": prop.get("label"), "ring": "token"})
        duo_rings = list(getattr(getattr(program, "duo", None), "rings", VOYNICH_PIPELINE))
    else:
        duo_rings = list(VOYNICH_PIPELINE)
    return {
        "honesty": "Organizational metaphor only · NOT Voynich decryption",
        "pipeline": list(duo_rings),
        "rings": rings,
        "counts": counts,
        "tagged": tagged[:40],
        "equation": "C_{n+1} = C_n² + Δ  (bounded orbit coherence tracker)",
    }


def voynich_ascii(status: Optional[Dict[str, Any]] = None) -> List[str]:
    st = status or voynich_status()
    lines = [
        "═══ VOYNICH RINGS (structural only) ═══",
        f"  {st.get('honesty')}",
        f"  Pipeline: {' → '.join(st.get('pipeline') or VOYNICH_PIPELINE)}",
        "",
    ]
    counts = st.get("counts") or {}
    for r in st.get("rings") or VOYNICH_RINGS:
        n = counts.get(r["id"], 0)
        bar = "█" * min(12, n) + "·" * max(0, 8 - min(8, n))
        lines.append(f"  [{r['stage']}] {r['name']:7} {bar} ×{n}")
        lines.append(f"       {r['metaphor']}")
        lines.append(f"       → {r['role']}")
    return lines


# ---------------------------------------------------------------------------
# Fractals — Rule 90 · orbit · shell self-similarity
# ---------------------------------------------------------------------------

def rule90_row(prev: List[int]) -> List[int]:
    """Elementary CA Rule 90 (XOR of neighbors) — Sierpinski generator."""
    n = len(prev)
    out = [0] * n
    for i in range(n):
        left = prev[i - 1] if i > 0 else 0
        right = prev[i + 1] if i < n - 1 else 0
        out[i] = left ^ right
    return out


def rule90(
    width: int = 33,
    steps: int = 16,
    *,
    seed_center: bool = True,
) -> List[List[int]]:
    row = [0] * width
    if seed_center:
        row[width // 2] = 1
    else:
        row[0] = 1
    grid = [list(row)]
    for _ in range(max(0, steps - 1)):
        row = rule90_row(row)
        grid.append(list(row))
    return grid


def rule90_ascii(width: int = 33, steps: int = 16) -> List[str]:
    grid = rule90(width, steps)
    lines = ["═══ FRACTAL · Rule 90 (Sierpinski) ═══"]
    for row in grid:
        lines.append("  " + "".join("█" if c else "·" for c in row))
    lines.append("  Rule 90: cell = left XOR right · deterministic")
    return lines


def complex_orbit(
    c_real: float = 0.0,
    c_imag: float = 0.0,
    z0_real: float = 0.0,
    z0_imag: float = 0.0,
    steps: int = 12,
    *,
    escape: float = 2.0,
) -> Dict[str, Any]:
    """
    Mandelbrot-style iteration z ← z² + c (interpretive fractal, not crypto).
    Also supports Julia when z0 is the seed and c fixed.
    """
    zr, zi = float(z0_real), float(z0_imag)
    cr, ci = float(c_real), float(c_imag)
    path = [[zr, zi]]
    escaped = False
    escape_step = None
    for i in range(max(0, steps)):
        # z² + c
        nr = zr * zr - zi * zi + cr
        ni = 2 * zr * zi + ci
        zr, zi = nr, ni
        path.append([round(zr, 5), round(zi, 5)])
        if zr * zr + zi * zi > escape * escape:
            escaped = True
            escape_step = i + 1
            break
    return {
        "kind": "complex_orbit",
        "equation": "z ← z² + c",
        "c": [cr, ci],
        "z0": [z0_real, z0_imag],
        "path": path,
        "escaped": escaped,
        "escape_step": escape_step,
        "final_mag": round(math.hypot(zr, zi), 5),
        "note": "Interpretive fractal tracker · not scientific proof",
    }


def fractal_shells(max_shell: int = 5, scale: float = 1.0) -> List[Dict[str, Any]]:
    """Self-similar shell radii (golden-ish growth for draw)."""
    phi = (1 + math.sqrt(5)) / 2
    out = []
    r = scale
    for s in range(1, max_shell + 1):
        out.append({"shell": s, "radius": round(r, 4), "metric": "fractal_phi"})
        r *= phi / 1.4  # tempered growth for visibility
    return out


def sierpinski_points(depth: int = 4) -> List[Tuple[float, float]]:
    """Chaos-game free: recursive midpoint Sierpinski vertices."""
    # equilateral triangle
    verts = [(0.0, 0.0), (1.0, 0.0), (0.5, math.sqrt(3) / 2)]
    pts = list(verts)

    def mid(a, b):
        return ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)

    def subdivide(tri, d):
        if d <= 0:
            return
        a, b, c = tri
        mab, mbc, mca = mid(a, b), mid(b, c), mid(c, a)
        pts.extend([mab, mbc, mca])
        subdivide((a, mab, mca), d - 1)
        subdivide((mab, b, mbc), d - 1)
        subdivide((mca, mbc, c), d - 1)

    subdivide(tuple(verts), depth)
    # unique
    seen = set()
    out = []
    for x, y in pts:
        # center and scale to ~ -1..1
        sx = (x - 0.5) * 2.2
        sy = (y - 0.35) * 2.2
        key = (round(sx, 4), round(sy, 4))
        if key not in seen:
            seen.add(key)
            out.append((sx, sy))
    return out


# ---------------------------------------------------------------------------
# Unified geometry status for Program
# ---------------------------------------------------------------------------

def geometry_status(
    program=None,
    *,
    flower_rings: int = 2,
    fractal_steps: int = 12,
) -> Dict[str, Any]:
    form = "cube"
    if program is not None and hasattr(program, "lattice"):
        form = program.lattice.perception.form.value
    flower = flower_draw_payload(rings=flower_rings, radius=1.0, include_vesica=True, include_fruit=True)
    nodes = program.nodes_payload() if program and hasattr(program, "nodes_payload") else []
    verita_edges = verita_between_nodes(nodes) if nodes else []
    from form.mandell.bounded_orbit import coherence_report
    orbit = coherence_report(0.3, 0.2, 6)
    corbit = complex_orbit(c_real=-0.4, c_imag=0.6, steps=10)
    return {
        "form": form,
        "flower": flower,
        "verita_edges": verita_edges[:30],
        "verita_count": len(verita_edges),
        "voynich": voynich_status(program),
        "fractal": {
            "rule90_width": 33,
            "rule90_steps": fractal_steps,
            "bounded_orbit": orbit,
            "complex_orbit": corbit,
            "shells": fractal_shells(5),
            "sierpinski_n": len(sierpinski_points(3)),
        },
        "principle": (
            "One lattice · Flower circles share centers · "
            "Vesica/Verita is truth-of-meet · "
            "Voynich rings are organizational · "
            "Fractals are deterministic pattern tools"
        ),
    }


def geometry_ascii(program=None) -> List[str]:
    st = geometry_status(program)
    lines = [
        "═══ SACRED GEOMETRY LAYER ═══",
        f"  form={st['form']}",
        f"  FoL centers={st['flower']['center_count']} vesicas={st['flower']['vesica_count']}",
        f"  Verita edges={st['verita_count']}",
        f"  Voynich pipeline: {' → '.join(st['voynich']['pipeline'])}",
        f"  Fractal orbit final={st['fractal']['bounded_orbit']['final']:.3f} · "
        f"complex |z|={st['fractal']['complex_orbit']['final_mag']}",
        f"  {st['principle']}",
    ]
    return lines


def smoke() -> bool:
    print("=== SACRED GEOMETRY SMOKE ===")
    r = []
    def rec(n, ok, d=""):
        print(f"[{len(r)+1}] {n}: {'PASS' if ok else 'FAIL'}" + (f" | {d}" if d else ""))
        r.append(bool(ok))
    c = flower_centers(1)
    rec("seed of life 7", len(c) == 7)
    c2 = flower_centers(2)
    rec("fol ring2", len(c2) >= 19)
    v = vesica(0, 0, 1, 1, 0, 1)
    rec("vesica type", v["type"] == "vesica", v["type"])
    rec("verita mid", 0 < v["verita"] <= 1, str(v["verita"]))
    pairs = vesica_pairs_from_centers(c, 1.0)
    rec("fol vesica pairs", len(pairs) >= 6, str(len(pairs)))
    g = rule90(17, 8)
    rec("rule90", len(g) == 8 and sum(g[0]) == 1)
    co = complex_orbit(-0.5, 0.5, steps=8)
    rec("complex orbit", len(co["path"]) >= 2)
    vs = voynich_status()
    rec("voynich honesty", "NOT" in vs["honesty"])
    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
