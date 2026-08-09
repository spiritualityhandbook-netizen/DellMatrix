#!/usr/bin/env python3
"""
Organ Atlas — body map expanded from docs · form · preform · src scan.

Every resonant module is a body part. MatrixBody imports this catalog.
Solo Verita judges one idea at a time; pair Verita judges links.
"""
from __future__ import annotations

from typing import Any, Dict

# role = anatomical metaphor · module = import path · dell · vital
ORGAN_ATLAS: Dict[str, Dict[str, Any]] = {
    # --- skeleton / structure ---
    "floor": {
        "role": "skeleton", "module": "form.mandell.floor", "dell": 65, "vital": True,
        "source": "form/mandell · boolean host",
    },
    "pillars": {
        "role": "spine", "module": "form.dell_matrix.pillars", "dell": 12, "vital": True,
        "source": "form pillars · 6-pillar audit",
    },
    "plane": {
        "role": "tissue", "module": "form.dell_matrix.plane", "dell": 15, "vital": True,
        "source": "form plane · live ideas",
    },
    "lattice": {
        "role": "nervous", "module": "form.dell_matrix.harmonic_lattice", "dell": 61, "vital": True,
        "source": "form harmonic_lattice · dual lattice",
    },
    "sacred_geometry": {
        "role": "spatial_intuition", "module": "form.dell_matrix.sacred_geometry", "dell": 51, "vital": False,
        "source": "form sacred_geometry · FoL / vesica",
    },
    # --- immune / isolation ---
    "nursery": {
        "role": "immune", "module": "form.dell_matrix.nursery", "dell": 64, "vital": True,
        "source": "form nursery · quarantine proposals",
    },
    "sandbox": {
        "role": "isolation_membrane", "module": "form.dell_matrix.sandbox_gate", "dell": 23, "vital": False,
        "source": "form sandbox_gate · box isolates",
    },
    # --- circulation / force ---
    "forces": {
        "role": "circulation", "module": "form.dell_matrix.forces", "dell": 83, "vital": True,
        "source": "form forces · src/forces nature",
    },
    "nature": {
        "role": "muscle", "module": "form.dell_matrix.nature_code", "dell": 60, "vital": True,
        "source": "form nature_code · movers particles agents",
    },
    "ringed_growth": {
        "role": "growth_plate", "module": "form.dell_matrix.ringed_growth", "dell": 87, "vital": True,
        "source": "form ringed_growth · sole growth path",
    },
    "resonance": {
        "role": "sympathetic_nervous", "module": "form.dell_matrix.resonance", "dell": 25, "vital": False,
        "source": "form resonance · peer enhance",
    },
    # --- brain / mind ---
    "gate": {
        "role": "brainstem", "module": "form.mandell.gate_discipline", "dell": 72, "vital": True,
        "source": "form mandell gate_discipline",
    },
    "brain": {
        "role": "cerebrum", "module": "form.dell_matrix.brain", "dell": 73, "vital": True,
        "source": "form brain · think cycle",
    },
    "verita": {
        "role": "judgment", "module": "form.dell_matrix.verita", "dell": 62, "vital": True,
        "source": "form verita · solo + pair truth",
    },
    "decision_shells": {
        "role": "prefrontal_soft", "module": "form.dell_matrix.decision_shells", "dell": 3, "vital": False,
        "source": "form decision_shells · graded decisions",
    },
    "english_brain": {
        "role": "language_cortex", "module": "form.mandell.english_brain", "dell": 66, "vital": True,
        "source": "form mandell english_brain",
    },
    "self_model": {
        "role": "interoception", "module": "form.dell_matrix.self_model", "dell": 18, "vital": False,
        "source": "form self_model · structural self-scan",
    },
    "thinks": {
        "role": "deliberation", "module": "preform.code.13_THINKS", "dell": 3, "vital": False,
        "source": "preform 13_THINKS · deliberation surface",
    },
    # --- memory ---
    "workmem": {
        "role": "hippocampus_work", "module": "preform.code.14_TOKEN_WORKMEM", "dell": 40, "vital": False,
        "source": "preform token workmem · context budget",
    },
    "stigmergic": {
        "role": "trail_memory", "module": "src.core.stigmergic", "dell": 77, "vital": False,
        "source": "src stigmergic · externalized residue trails",
    },
    "harmonic_core": {
        "role": "long_term_keys", "module": "form.dell_matrix.harmonic_core", "dell": 10, "vital": False,
        "source": "form harmonic_core · permanent keys soft-forget",
    },
    # --- senses / face / hand ---
    "vision": {
        "role": "eye", "module": "form.dell_matrix.vision", "dell": 82, "vital": False,
        "source": "form vision · directional look",
    },
    "perception": {
        "role": "proprioception", "module": "form.dell_matrix.perception", "dell": 82, "vital": False,
        "source": "form perception · form duals",
    },
    "act_on_seen": {
        "role": "hand", "module": "form.dell_matrix.act_on_seen", "dell": 82, "vital": False,
        "source": "form act_on_seen · act on vision",
    },
    "live_visual": {
        "role": "face_surface", "module": "form.dell_matrix.live_visual", "dell": 9, "vital": False,
        "source": "form live_visual · live render",
    },
    "face": {
        "role": "expression", "module": "form.avatar.face", "dell": 5, "vital": False,
        "source": "form avatar face · expression cycles",
    },
    "kaomoji": {
        "role": "microexpression", "module": "form.avatar.kaomoji", "dell": 5, "vital": False,
        "source": "form avatar kaomoji · expression packs",
    },
    "avatar_body": {
        "role": "locomotor", "module": "form.avatar.body", "dell": 19, "vital": False,
        "source": "form avatar body · FSM posture locomotion",
    },
    "first_person": {
        "role": "embodied_nav", "module": "form.dell_matrix.first_person", "dell": 19, "vital": False,
        "source": "form first_person · walk look world",
    },
    "ear": {
        "role": "microphone", "module": "form.dell_matrix.sense_intake", "dell": 75, "vital": False,
        "hardware": "mic", "source": "sense_intake gated",
    },
    "eye_cam": {
        "role": "camera", "module": "form.dell_matrix.sense_intake", "dell": 75, "vital": False,
        "hardware": "camera", "source": "sense_intake gated",
    },
    "screen": {
        "role": "screen_share", "module": "form.dell_matrix.sense_intake", "dell": 75, "vital": False,
        "hardware": "screen", "source": "sense_intake gated",
    },
    "content": {
        "role": "high_quality_intake", "module": "form.dell_matrix.sense_intake", "dell": 75, "vital": False,
        "source": "sense_intake content always",
    },
    # --- identity / social / livelihood ---
    "personas": {
        "role": "identity", "module": "form.dell_matrix.personas", "dell": 2, "vital": False,
        "source": "form personas",
    },
    "companion": {
        "role": "social_bond", "module": "form.dell_matrix.companion", "dell": 2, "vital": False,
        "source": "form companion · AI companion",
    },
    "trading": {
        "role": "livelihood", "module": "form.trading", "dell": 89, "vital": False,
        "source": "form trading",
    },
    # --- pattern / adaptation / math tissue ---
    "fourier": {
        "role": "auditory_cortex", "module": "form.dell_matrix.fourier", "dell": 59, "vital": False,
        "source": "form fourier · spectrum",
    },
    "eigen": {
        "role": "balance", "module": "form.dell_matrix.eigen_stability", "dell": 57, "vital": False,
        "source": "form eigen_stability",
    },
    "logistic": {
        "role": "metabolism", "module": "form.dell_matrix.logistic_map", "dell": 58, "vital": False,
        "source": "form logistic_map",
    },
    "linear_algebra": {
        "role": "spatial_reasoning", "module": "form.dell_matrix.linear_algebra", "dell": 15, "vital": False,
        "source": "form linear_algebra",
    },
    "neuroevo": {
        "role": "adaptation", "module": "form.dell_matrix.neuroevo", "dell": 88, "vital": False,
        "source": "form neuroevo",
    },
    "neural_patterns": {
        "role": "pattern_tissue", "module": "src.core.neural_patterns", "dell": 88, "vital": False,
        "source": "src neural_patterns",
    },
    "dna_profile": {
        "role": "genotype", "module": "src.core.dna_profile", "dell": 36, "vital": False,
        "source": "src dna_profile",
    },
    # --- conscience / drive / practice ---
    "audit": {
        "role": "conscience", "module": "form.dell_matrix.incorporation_audit", "dell": 70, "vital": False,
        "source": "form incorporation_audit",
    },
    "inspire": {
        "role": "curiosity", "module": "form.dell_matrix.inspire_pack", "dell": 35, "vital": False,
        "source": "form inspire_pack",
    },
    "workshops": {
        "role": "practice", "module": "form.dell_matrix.workshops", "dell": 78, "vital": False,
        "source": "form workshops",
    },
    "program_strength": {
        "role": "fitness", "module": "form.dell_matrix.program_strength", "dell": 46, "vital": False,
        "source": "form program_strength",
    },
    "ambient": {
        "role": "peripheral_attention", "module": "form.dell_matrix.ambient_gate", "dell": 17, "vital": False,
        "source": "form ambient_gate · shadow intake",
    },
}


def atlas_summary() -> Dict[str, Any]:
    vital = [k for k, v in ORGAN_ATLAS.items() if v.get("vital")]
    return {
        "organs": len(ORGAN_ATLAS),
        "vital": vital,
        "vital_count": len(vital),
        "roles": sorted({v["role"] for v in ORGAN_ATLAS.values()}),
        "law": "scan-derived body map · every resonant module is an organ",
    }


def smoke() -> bool:
    print("=== ORGAN ATLAS SMOKE ===")
    s = atlas_summary()
    ok = s["organs"] >= 30 and s["vital_count"] >= 8
    print(f"organs={s['organs']} vital={s['vital_count']} roles={len(s['roles'])}")
    print(f"[{'PASS' if ok else 'FAIL'}] atlas density")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
