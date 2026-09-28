#!/usr/bin/env python3
"""Dell address space 000–999.

000–099  CORE LANGUAGE (CORE_I 00–50 + CORE_II 51–99)
100–199  SEMANTIC / KNOWLEDGE
200–299  MATH / QUANTITY
300–399  SPACE / GEOMETRY
400–499  TIME / PROCESS
500–599  NATURE / PHYSICS
600–699  AGENT / COGNITION
700–799  INTERFACE / PERCEPTION
800–899  SYSTEM / COMPUTATION
900–999  BRIDGE / EXTERNAL / META

Numbers 100–999 stay unallocated until a concept earns a number by DVS.
Former gate_discipline 51–99 domain names are preserved here as
RESERVED_DOMAIN aliases so they are not erased and not silently active.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

FAMILIES = {
    "000-099": "CORE_LANGUAGE",
    "100-199": "SEMANTIC_KNOWLEDGE",
    "200-299": "MATH_QUANTITY",
    "300-399": "SPACE_GEOMETRY",
    "400-499": "TIME_PROCESS",
    "500-599": "NATURE_PHYSICS",
    "600-699": "AGENT_COGNITION",
    "700-799": "INTERFACE_PERCEPTION",
    "800-899": "SYSTEM_COMPUTATION",
    "900-999": "BRIDGE_EXTERNAL_META",
}

RESERVED_DOMAIN: Dict[int, Dict[str, str]] = {
    151: {"name": "Harmonic", "manor": "frequency / Fourier bind", "from": "old-51"},
    167: {"name": "Seed", "manor": "Mandel seed emit", "from": "old-67"},
    168: {"name": "Tag", "manor": "intent/lattice/persona tags", "from": "old-68"},
    176: {"name": "Polyglot", "manor": "multi-lang bridge", "from": "old-76"},
    257: {"name": "Eigen", "manor": "stability spectrum", "from": "old-57"},
    258: {"name": "Logistic", "manor": "growth intensity / chaos regime", "from": "old-58"},
    259: {"name": "Fourier", "manor": "DFT / spectrum", "from": "old-59"},
    361: {"name": "Lattice", "manor": "Dual Lattice op", "from": "old-61"},
    463: {"name": "Orbit", "manor": "orbit step C2+delta", "from": "old-63"},
    560: {"name": "Nature", "manor": "nature-force tick", "from": "old-60"},
    564: {"name": "Nursery", "manor": "quarantine grow", "from": "old-64"},
    571: {"name": "Grow", "manor": "recursive language growth", "from": "old-71"},
    583: {"name": "Force", "manor": "ForceField tick", "from": "old-83"},
    584: {"name": "Particle", "manor": "NoC particle", "from": "old-84"},
    586: {"name": "CA", "manor": "cellular automata", "from": "old-86"},
    587: {"name": "Fractal", "manor": "ringed growth", "from": "old-87"},
    654: {"name": "Hypo", "manor": "under-surface foresight", "from": "old-54"},
    655: {"name": "Hypothermia", "manor": "deep foresight", "from": "old-55"},
    662: {"name": "Verita", "manor": "coherence gate", "from": "old-62"},
    666: {"name": "EnglishBrain", "manor": "paraphrase / verb map", "from": "old-66"},
    673: {"name": "OneBody", "manor": "unify all parts", "from": "old-73"},
    679: {"name": "Fusion", "manor": "multi-persona bind", "from": "old-79"},
    685: {"name": "Agent", "manor": "seek/flee", "from": "old-85"},
    688: {"name": "NeuroEvo", "manor": "evolution loop", "from": "old-88"},
    692: {"name": "Oracle", "manor": "projection PROJECTED_NOT_FACT", "from": "old-92"},
    696: {"name": "Unify", "manor": "one initiative", "from": "old-96"},
    697: {"name": "Depth", "manor": "deep stack walk", "from": "old-97"},
    698: {"name": "Horizon", "manor": "context horizon", "from": "old-98"},
    775: {"name": "Mandellmoji", "manor": "compound visual seed", "from": "old-75"},
    777: {"name": "Residue", "manor": "stigmergic signal", "from": "old-77"},
    778: {"name": "Workshop", "manor": "structured edit session", "from": "old-78"},
    782: {"name": "Vision", "manor": "act-on-seen", "from": "old-82"},
    821: {"name": "Chess", "manor": "precise pathing (legacy named)", "from": "old-52"},
    822: {"name": "Checkers", "manor": "probabilistic pathing", "from": "old-53"},
    850: {"name": "ManifestAct", "manor": "Manifest action pair", "from": "old-56"},
    865: {"name": "Floor", "manor": "boolean host lock", "from": "old-65"},
    869: {"name": "PlanRoute", "manor": "Dell router plan", "from": "old-69"},
    870: {"name": "Audit", "manor": "incorporation / universal props", "from": "old-70"},
    872: {"name": "Handicap", "manor": "detect limitation", "from": "old-72"},
    874: {"name": "Background", "manor": "symbolic bg process", "from": "old-74"},
    880: {"name": "SnapIn", "manor": "capability registry", "from": "old-80"},
    881: {"name": "Offline", "manor": "local-only path", "from": "old-81"},
    889: {"name": "Trade", "manor": "trading matrix", "from": "old-89"},
    890: {"name": "Business", "manor": "US&S bridge", "from": "old-90"},
    891: {"name": "Sister", "manor": "family deploy path", "from": "old-91"},
    893: {"name": "SUS", "manor": "Superior Ultimate Standard", "from": "old-93"},
    894: {"name": "Lupe", "manor": "multi-pass loop", "from": "old-94"},
    895: {"name": "NBD", "manor": "note-build-deploy stamp", "from": "old-95"},
    999: {"name": "Omega", "manor": "terminal / full cycle close", "from": "old-99"},
}

OLD_TO_NEW = {int(v["from"].split("-")[1]): n for n, v in RESERVED_DOMAIN.items()}


def family_of(n: int) -> str:
    if n < 0 or n > 999:
        return "OUT_OF_RANGE"
    band = (n // 100) * 100
    key = f"{band:03d}-{band+99:03d}"
    return FAMILIES.get(key, "UNKNOWN")


def get_reserved(n: int) -> Optional[Dict[str, Any]]:
    row = RESERVED_DOMAIN.get(n)
    if not row:
        return None
    return {"dell": n, **row, "status": "RESERVED_NOT_ACTIVE", "family": family_of(n)}


def promotion_requirements() -> Dict[str, str]:
    return {
        "registry": "required",
        "parser": "required",
        "executor": "required",
        "program_state": "required",
        "persistence": "required",
        "ui": "required",
        "tests": "required",
        "documentation": "required",
        "dvs": "required",
        "note": "Do not declare 100-999 active unless promoted through this pipeline.",
    }
