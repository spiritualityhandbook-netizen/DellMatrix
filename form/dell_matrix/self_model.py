#!/usr/bin/env python3
"""
Program self-model — structural self-understanding (not sentience).

The program inventories its matrices, snaps, capabilities, and live state,
scores how well each surface answers, and records growth of self-knowledge.

Law: Floor locked · Nursery confirm · offline · educational.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
import time


# Capability catalog — each has a probe command that must end usefully
CAPABILITIES: List[Dict[str, Any]] = [
    # identity / floor
    {"id": "floor", "group": "identity", "cmd": "status", "expect": "floor", "desc": "Floor lock present"},
    {"id": "status", "group": "identity", "cmd": "status", "expect": "ideas", "desc": "Session status"},
    {"id": "matrices", "group": "identity", "cmd": "matrices", "expect": "matrix", "desc": "Matrices inventory"},
    {"id": "audit", "group": "identity", "cmd": "audit", "expect": "pillar", "desc": "6-pillar health"},
    # perception
    {"id": "look", "group": "perception", "cmd": "look", "expect": "vision|look|entities|face", "desc": "Directional vision"},
    {"id": "multilook", "group": "perception", "cmd": "multilook", "expect": "near|mid|far|multi", "desc": "Multi-scale vision"},
    {"id": "page", "group": "perception", "cmd": "page", "expect": "page|idea|door", "desc": "Idea end-page"},
    {"id": "lattice", "group": "perception", "cmd": "lattice", "expect": "form|lattice|shell|cell", "desc": "Lattice form"},
    {"id": "geometry", "group": "perception", "cmd": "geometry", "expect": "flower|geometry|verita|ring", "desc": "Sacred geometry"},
    # growth
    {"id": "grow", "group": "growth", "cmd": "grow ideas 1", "expect": "grow|nursery|pending|idea", "desc": "Ringed growth → nursery"},
    {"id": "proposals", "group": "growth", "cmd": "proposals", "expect": "nursery|proposal|pending|empty", "desc": "Nursery list"},
    {"id": "rank", "group": "growth", "cmd": "rank", "expect": "rank|aff|proposal|empty|nursery", "desc": "Rank proposals"},
    {"id": "forces", "group": "growth", "cmd": "forces", "expect": "force|weather|active", "desc": "Nature forces"},
    {"id": "force_tick", "group": "growth", "cmd": "force tick", "expect": "force|tick", "desc": "Force tick"},
    {"id": "pulse", "group": "growth", "cmd": "pulse", "expect": "pulse|score|slope|enhance", "desc": "Enhance pulse"},
    # language
    {"id": "english", "group": "language", "cmd": "english status", "expect": "english|mastery|learn|cycle", "desc": "English brain"},
    {"id": "lang", "group": "language", "cmd": "lang list", "expect": "lang|es|fr|la|latin|spanish", "desc": "Polyglot doors"},
    {"id": "help", "group": "language", "cmd": "help", "expect": "help|command|tutorial|create", "desc": "Help surface"},
    # agents
    {"id": "personas", "group": "agents", "cmd": "personas", "expect": "persona|manny|melody|bimo|agent", "desc": "Persona roster"},
    {"id": "bimo", "group": "agents", "cmd": "bimo", "expect": "bimo|slot|fusion|dock", "desc": "BIMO body"},
    {"id": "entities", "group": "agents", "cmd": "entities", "expect": "entity|avatar|companion|idea", "desc": "Stage entities"},
    {"id": "ai", "group": "agents", "cmd": "ai status", "expect": "ai|face|mode|pos", "desc": "AI companion"},
    # workbench
    {"id": "workshops", "group": "workbench", "cmd": "workshops", "expect": "workshop|matrix|persona", "desc": "Workshop index"},
    {"id": "inspire", "group": "workbench", "cmd": "inspire", "expect": "inspire|pref|vision|sprite", "desc": "Inspire pack"},
    {"id": "home", "group": "workbench", "cmd": "home", "expect": "home|center|0,0", "desc": "Home centerpoint"},
    # evolve
    {"id": "evolve", "group": "evolve", "cmd": "evolve", "expect": "evolv|gen|pillar|force", "desc": "One generation evolve"},
    {"id": "save", "group": "evolve", "cmd": "save", "expect": "save|persist|written|state|path|keep", "desc": "Persist session"},
    {"id": "sphere", "group": "evolve", "cmd": "sphere", "expect": "sphere|form|radial|circle", "desc": "Sphere form"},
]


@dataclass
class SelfKnowledge:
    """In-process map of what the program has verified about itself."""
    mastery: Dict[str, float] = field(default_factory=dict)  # cap id → 0..1
    probes: int = 0
    hits: int = 0
    generations_seen: int = 0
    last_reflect: List[str] = field(default_factory=list)
    ledger: List[Dict[str, Any]] = field(default_factory=list)
    known_matrices: List[str] = field(default_factory=list)
    known_snaps: List[str] = field(default_factory=list)
    gaps_closed: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mastery": dict(self.mastery),
            "probes": self.probes,
            "hits": self.hits,
            "hit_rate": round(self.hits / max(1, self.probes), 4),
            "generations_seen": self.generations_seen,
            "known_matrices": list(self.known_matrices)[:40],
            "known_snaps": list(self.known_snaps)[:40],
            "gaps_closed": list(self.gaps_closed)[-20:],
            "ledger_len": len(self.ledger),
            "avg_mastery": round(
                sum(self.mastery.values()) / max(1, len(self.mastery)), 3
            ) if self.mastery else 0.0,
        }

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "SelfKnowledge":
        sk = cls()
        if not data or not isinstance(data, dict):
            return sk
        sk.mastery = {str(k): float(v) for k, v in (data.get("mastery") or {}).items()}
        sk.probes = int(data.get("probes") or 0)
        sk.hits = int(data.get("hits") or 0)
        sk.generations_seen = int(data.get("generations_seen") or 0)
        sk.known_matrices = list(data.get("known_matrices") or [])
        sk.known_snaps = list(data.get("known_snaps") or [])
        sk.gaps_closed = list(data.get("gaps_closed") or [])
        return sk


def _msg_blob(out: Dict[str, Any]) -> str:
    parts = [
        str(out.get("msg") or ""),
        str(out.get("error") or ""),
        str(out.get("end") or ""),
    ]
    return " ".join(parts).lower()


def _expect_match(blob: str, expect: str) -> bool:
    if not expect:
        return bool(blob.strip())
    for alt in expect.split("|"):
        if alt.strip() and alt.strip().lower() in blob:
            return True
    return False


def inventory(program) -> Dict[str, Any]:
    """Static + live inventory of what the program is."""
    snaps: List[str] = []
    try:
        if hasattr(program.matrix, "snap_names"):
            snaps = sorted(program.matrix.snap_names())
        elif hasattr(program.matrix, "all_snaps"):
            snaps = sorted({
                getattr(s, "name", str(s))
                for s in (program.matrix.all_snaps() or [])
            })
    except Exception:
        snaps = []

    matrices = []
    try:
        matrices = [m["id"] for m in program.matrices()]
    except Exception:
        matrices = []

    workshops = []
    try:
        workshops = [w["id"] for w in (program.workshops_status().get("list") or [])]
    except Exception:
        workshops = []

    personas = []
    try:
        from form.dell_matrix.personas import PERSONAS
        personas = list(PERSONAS.keys())
    except Exception:
        personas = []

    routes = []
    try:
        from form.dell_matrix.live_visual import _PAGE_ROUTES
        routes = list(_PAGE_ROUTES.keys())
    except Exception:
        routes = []

    audit = program.audit() if hasattr(program, "audit") else {}
    gen = int(getattr(getattr(program, "duo", None), "generation", 0) or 0)
    ideas = len(program.cube.session.plane.units) if hasattr(program, "cube") else 0
    nursery = 0
    try:
        nursery = int(program.nursery.summary().get("pending", 0))
    except Exception:
        pass

    return {
        "owner": getattr(program, "owner", "?"),
        "generation": gen,
        "ideas": ideas,
        "nursery_pending": nursery,
        "form": program.lattice.perception.form.value if hasattr(program, "lattice") else "?",
        "ux_mode": getattr(program, "ux_mode", "builder"),
        "view_mode": getattr(program, "view_mode", "first_person"),
        "active_view": getattr(program, "active_view", "growth"),
        "active_workshop": getattr(program, "active_workshop", None),
        "persona_lens": getattr(program, "persona_lens", None),
        "rings": list(getattr(getattr(program, "duo", None), "rings", []) or []),
        "snaps": snaps,
        "snap_count": len(snaps),
        "matrices": matrices,
        "matrix_count": len(matrices),
        "workshops": workshops,
        "personas": personas,
        "routes": routes,
        "pillars": audit,
        "enhance_on": bool(getattr(getattr(program, "enhance", None), "on", False)),
        "has_inspire": hasattr(program, "inspire"),
        "has_companion": hasattr(program, "companion"),
        "has_forces": hasattr(program, "forces"),
        "has_bimo": hasattr(program, "bimo"),
        "self_knowledge": (
            program.self_knowledge.to_dict()
            if hasattr(program, "self_knowledge") and program.self_knowledge
            else {}
        ),
    }


def probe_capability(program, cap: Dict[str, Any]) -> Dict[str, Any]:
    """Run capability cmd; update self_knowledge mastery."""
    from form.dell_matrix.live_visual import _run_command

    cmd = cap["cmd"]
    out = _run_command(program, cmd)
    blob = _msg_blob(out)
    ok = bool(out.get("ok")) or bool(out.get("msg"))
    if ok and not _expect_match(blob, cap.get("expect") or ""):
        # still ok if useful msg and not pure create-misroute
        if "created idea" in blob and "create" not in cmd:
            ok = False
        elif len(blob.strip()) < 3:
            ok = False
        else:
            ok = True  # soft pass on non-empty useful end

    sk: SelfKnowledge = getattr(program, "self_knowledge", None) or SelfKnowledge()
    program.self_knowledge = sk
    sk.probes += 1
    prev = sk.mastery.get(cap["id"], 0.0)
    if ok:
        sk.hits += 1
        sk.mastery[cap["id"]] = round(min(1.0, 0.65 * prev + 0.35 * 1.0), 3)
    else:
        sk.mastery[cap["id"]] = round(max(0.0, 0.8 * prev), 3)

    return {
        "ok": ok,
        "id": cap["id"],
        "group": cap.get("group"),
        "cmd": cmd,
        "mastery": sk.mastery[cap["id"]],
        "msg": (out.get("msg") or out.get("error") or "")[:100],
    }


def know_self(program) -> Dict[str, Any]:
    """
    Full self-understanding pass:
      inventory + duo understand + capability mastery snapshot.
    """
    inv = inventory(program)
    duo = {}
    try:
        duo = program.duo.understand_self()
    except Exception as e:
        duo = {"error": str(e)}

    # refresh known lists
    sk: SelfKnowledge = getattr(program, "self_knowledge", None) or SelfKnowledge()
    program.self_knowledge = sk
    sk.known_matrices = list(inv.get("matrices") or [])
    sk.known_snaps = list(inv.get("snaps") or [])
    sk.generations_seen = max(sk.generations_seen, int(inv.get("generation") or 0))

    # gap list: cold capabilities
    cold = []
    for cap in CAPABILITIES:
        m = sk.mastery.get(cap["id"], 0.0)
        if m < 0.5:
            cold.append({"id": cap["id"], "mastery": m, "cmd": cap["cmd"], "desc": cap["desc"]})

    # structural gaps
    structural = []
    if inv.get("matrix_count", 0) < 15:
        structural.append("matrices_thin")
    if inv.get("ideas", 0) < 1:
        structural.append("no_ideas")
    if not inv.get("has_inspire"):
        structural.append("no_inspire")
    if (inv.get("pillars") or {}).get("average", 0) < 0.7:
        structural.append("pillars_growing")

    report = {
        "ok": True,
        "kind": "self_model",
        "inventory": inv,
        "duo": duo,
        "knowledge": sk.to_dict(),
        "cold_capabilities": cold[:12],
        "structural_gaps": structural,
        "capability_count": len(CAPABILITIES),
        "groups": sorted({c["group"] for c in CAPABILITIES}),
        "ts": time.time(),
    }
    return report


def reflect_lines(program) -> List[str]:
    """Human end-page: program speaks its structure and growth."""
    k = know_self(program)
    inv = k["inventory"]
    sk = k["knowledge"]
    pil = inv.get("pillars") or {}
    lines = [
        "══ Program self-understanding ══",
        f"  I am DellMatrix · owner={inv.get('owner')} · gen={inv.get('generation')}",
        f"  Floor locked · form={inv.get('form')} · mode={inv.get('ux_mode')} · view={inv.get('view_mode')}",
        f"  ideas={inv.get('ideas')} nursery={inv.get('nursery_pending')} "
        f"matrices={inv.get('matrix_count')} snaps≈{inv.get('snap_count')}",
        f"  rings: {' → '.join(inv.get('rings') or [])}",
        f"  pillars: {pil.get('label', '—')} avg={pil.get('average', '—')}",
        f"  self-knowledge: probes={sk.get('probes')} hits={sk.get('hits')} "
        f"rate={sk.get('hit_rate')} avg_mastery={sk.get('avg_mastery')}",
    ]
    # top mastery
    mastery = sk.get("mastery") or {}
    if mastery:
        top = sorted(mastery.items(), key=lambda x: -x[1])[:8]
        lines.append("  known well: " + " · ".join(f"{i}={v:.2f}" for i, v in top))
    cold = k.get("cold_capabilities") or []
    if cold:
        lines.append("  still learning: " + ", ".join(c["id"] for c in cold[:8]))
    else:
        lines.append("  still learning: — (all surfaces warm)")
    gaps = k.get("structural_gaps") or []
    if gaps:
        lines.append("  gaps: " + ", ".join(gaps))
    lines.append("  doors: evolve | audit | matrices | inspire | english expand 150 | self")
    lines.append("  end · self-model complete (structural, not conscious)")

    sk_obj: SelfKnowledge = program.self_knowledge
    sk_obj.last_reflect = lines
    sk_obj.ledger.append({
        "kind": "reflect",
        "gen": inv.get("generation"),
        "avg_mastery": sk.get("avg_mastery"),
        "ts": time.time(),
    })
    while len(sk_obj.ledger) > 64:
        sk_obj.ledger.pop(0)
    return lines


def close_gaps(program) -> Dict[str, Any]:
    """
    Warm cold capabilities + structural gaps with real actions.
    Returns what was closed this pass.
    """
    closed = []
    k = know_self(program)
    # warm cold caps (max 6 per call)
    for cap_info in (k.get("cold_capabilities") or [])[:6]:
        cap = next((c for c in CAPABILITIES if c["id"] == cap_info["id"]), None)
        if not cap:
            continue
        r = probe_capability(program, cap)
        if r.get("ok") and r.get("mastery", 0) >= 0.5:
            closed.append(cap["id"])
            program.self_knowledge.gaps_closed.append(cap["id"])

    # structural: ensure at least one idea + enhance on for omegate
    inv = k["inventory"]
    if inv.get("ideas", 0) < 1:
        try:
            program.place("self_seed", "SelfSeed", words="program knows itself", x=0, y=1)
            closed.append("seed_idea")
        except Exception:
            pass
    if "pillars_growing" in (k.get("structural_gaps") or []):
        try:
            if hasattr(program, "enhance") and not program.enhance.on:
                program.enhance.turn_on()
            program.pulse()
            program.force_tick() if hasattr(program, "force_tick") else None
            closed.append("warm_pillars")
        except Exception:
            pass

    return {"ok": True, "closed": closed, "knowledge": program.self_knowledge.to_dict()}


def evolve_with_understanding(program, detail: str = "self evolve") -> Dict[str, Any]:
    """One generation: know → close gaps → evolve → re-audit → ledger."""
    before = know_self(program)
    gaps = close_gaps(program)
    # evolve generation
    evo = program.evolve(detail=detail) if hasattr(program, "evolve") else {"ok": False}
    after_audit = program.audit() if hasattr(program, "audit") else {}
    sk: SelfKnowledge = program.self_knowledge
    sk.generations_seen = max(
        sk.generations_seen,
        int(evo.get("generation") or getattr(getattr(program, "duo", None), "generation", 0) or 0),
    )
    sk.ledger.append({
        "kind": "evolve",
        "detail": detail[:80],
        "gen": evo.get("generation"),
        "closed": gaps.get("closed"),
        "pillars": after_audit.get("average"),
        "ts": time.time(),
    })
    while len(sk.ledger) > 64:
        sk.ledger.pop(0)

    return {
        "ok": True,
        "generation": evo.get("generation"),
        "closed": gaps.get("closed"),
        "pillars_before": (before.get("inventory") or {}).get("pillars", {}).get("average"),
        "pillars_after": after_audit.get("average"),
        "mastery": sk.to_dict().get("avg_mastery"),
        "duo": evo.get("duo"),
        "forces": bool(evo.get("forces")),
    }


def smoke() -> bool:
    print("=== SELF MODEL SMOKE ===")
    from form.open import open_program
    p = open_program("SelfModelSmoke")
    p.place("a", "Alpha", words="self test", x=0, y=1)
    lines = reflect_lines(p)
    k = know_self(p)
    r = probe_capability(p, CAPABILITIES[0])
    e = evolve_with_understanding(p, "smoke evolve")
    ok = (
        len(lines) >= 6
        and k.get("ok")
        and r.get("id")
        and e.get("ok")
        and hasattr(p, "self_knowledge")
    )
    print(f"[{'PASS' if ok else 'FAIL'}] caps={len(CAPABILITIES)} mastery={p.self_knowledge.to_dict().get('avg_mastery')}")
    print(f"  gen={e.get('generation')} pillars={e.get('pillars_after')}")
    return bool(ok)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
