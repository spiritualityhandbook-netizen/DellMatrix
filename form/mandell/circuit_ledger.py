#!/usr/bin/env python3
"""Canonical Circuit Ledger — ONE current state authority for DellMatrix.

ARCHAEOLOGY != CURRENT STATE.

Historical files (e.g. ~/workspace/nbd-omega-001/loose_ends.md) record
discovery-time state. This ledger records CURRENT state. Both can be
correct simultaneously because they describe different times.

Laws:
- Once CLOSED, a circuit cannot silently return to OPEN/READY (no resurrection).
- Reopening requires explicit evidence (regression, reintroduced defect, etc.).
- NBD consumes this ledger; it does not duplicate state manually.
- Historical archaeology is immutable evidence, not current authority.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

# Valid states
OPEN = "OPEN"
BLOCKED = "BLOCKED"
READY = "READY"
CLOSED = "CLOSED"
SUPERSEDED = "SUPERSEDED"
HISTORICAL_ONLY = "HISTORICAL_ONLY"

VALID_STATES = {OPEN, BLOCKED, READY, CLOSED, SUPERSEDED, HISTORICAL_ONLY}

@dataclass(frozen=True)
class Circuit:
    circuit_id: str
    title: str
    state: str
    locality: str
    dependency_ids: List[str] = field(default_factory=list)
    evidence: str = ""
    closure_cycle: Optional[str] = None
    closure_commit: Optional[str] = None
    superseded_by: Optional[str] = None
    last_verified: str = "2026-10-02"
    notes: str = ""

    def __post_init__(self):
        if self.state not in VALID_STATES:
            raise ValueError(f"Invalid state {self.state} for {self.circuit_id}")

def build_ledger() -> List[Circuit]:
    """Return the canonical circuit list. Current state as of 2026-10-02."""
    return [
        # ── CLOSED ──────────────────────────────────────────────
        Circuit("LE-01", "Live Dell 27 checkpoint non-atomic",
                CLOSED, "persistence",
                evidence="RTPH-I PR #4 merge 9547409",
                closure_cycle="RTPH-I", closure_commit="9547409ea129b91e26374ef87908339fc0c5d309",
                notes="NBD-Ω-010 wrongly listed as remaining; worker reporting error."),
        Circuit("LE-02", "PR #24 unmerged",
                CLOSED, "dcc",
                evidence="PR #24 MERGED 2026-10-01T23:04:25Z",
                closure_cycle="DCC-XX", closure_commit="merged",
                notes="Dependency satisfied."),
        Circuit("LE-03", "Checkpoint Generation V1 unwired",
                CLOSED, "persistence",
                evidence="PAC-I PR #25 merge 1040da4b; Generation V1 tested",
                closure_cycle="PAC-I", closure_commit="1040da4bcee7820d147e31bf65cb94b4beebaeb6",
                notes="NBD-Ω-010 wrongly listed as remaining; worker reporting error."),
        Circuit("LE-05", "core_ii.store _last_result durability",
                CLOSED, "persistence",
                evidence="Certified EPHEMERAL_BY_DESIGN",
                closure_cycle="NBD-Ω-001", notes="Intentionally ephemeral, not a defect."),
        Circuit("LE-06", "Save/load authority asymmetry",
                CLOSED, "persistence",
                evidence="PAC-I; Persistence V2 unified (114/114)",
                closure_cycle="PAC-I"),
        Circuit("LE-07", "needs.undo second deletion authority",
                CLOSED, "runtime",
                evidence="Certified closed; undo authority singular",
                closure_cycle="NBD-Ω-001"),
        Circuit("LE-08", "Action-stack undo vs DCC revision",
                CLOSED, "runtime",
                evidence="Certified closed; DCC-XVI is authority",
                closure_cycle="NBD-Ω-001"),
        Circuit("LE-11", "DCC-XX retention design deferred",
                CLOSED, "dcc",
                evidence="DCC-XX merged; dcc_xx 159/159",
                closure_cycle="DCC-XX"),
        Circuit("LE-14", "SISTER_SETUP phantom commands",
                CLOSED, "cleanup",
                evidence="FCND-I removed network/net_push/push_main",
                closure_cycle="FCND-I", closure_commit="81a3d1e5d4e98596152386d008a004ba528479ed"),
        Circuit("LE-16", "Sidecar persistence outside authority",
                CLOSED, "persistence",
                evidence="Certified; sidecars noncanonical by design (DBEL-I)",
                closure_cycle="DBEL-I"),
        Circuit("LE-17", "gate_core_ii_bind.py dead code",
                CLOSED, "cleanup",
                evidence="FCND-I removed; zero callers",
                closure_cycle="FCND-I", closure_commit="81a3d1e5d4e98596152386d008a004ba528479ed"),
        Circuit("LE-18", "boot.py false one-path claim",
                CLOSED, "cleanup",
                evidence="FCND-I removed; zero callers",
                closure_cycle="FCND-I", closure_commit="81a3d1e5d4e98596152386d008a004ba528479ed"),
        Circuit("LE-19", "smoke_all.py disconnected",
                CLOSED, "cleanup",
                evidence="FCND-I removed; regress.py + CI are authorities",
                closure_cycle="FCND-I", closure_commit="81a3d1e5d4e98596152386d008a004ba528479ed"),
        Circuit("LE-21", "Phantom --awake CLI flag",
                CLOSED, "cleanup",
                evidence="FCND-I fixed to --awake-every",
                closure_cycle="FCND-I", closure_commit="81a3d1e5d4e98596152386d008a004ba528479ed"),
        Circuit("LE-22", "truth-of-meet terminology hazard",
                CLOSED, "cleanup",
                evidence="FCND-I renamed to coherence-of-meet (5 files)",
                closure_cycle="FCND-I", closure_commit="81a3d1e5d4e98596152386d008a004ba528479ed"),
        Circuit("LE-23", "DOC_GAP_CLOSER misleading commands",
                CLOSED, "cleanup",
                evidence="FCND-I removed phantom act commands",
                closure_cycle="FCND-I", closure_commit="81a3d1e5d4e98596152386d008a004ba528479ed"),
        Circuit("LE-24", "Stale audit snapshots",
                CLOSED, "cleanup",
                evidence="FCND-I labeled 7 docs HISTORICAL SNAPSHOT",
                closure_cycle="FCND-I", closure_commit="81a3d1e5d4e98596152386d008a004ba528479ed"),

        # ── OPEN / READY / BLOCKED ──────────────────────────────
        Circuit("LE-04", "live_visual parallel command authority",
                CLOSED, "visual",
                evidence="IAC-I Phases C-N: 135 command patterns inventoried. Forces extracted to Program.force_growth/water/breath/gravity. All others delegate to Program methods, REPL, ROS, NBDE, or EOC-I. K1 converged in REPL (numeric→ROS, word→latinmandell). K2 proven (one Outcome via EOC-I). Visual surface preserved.",
                closure_cycle="IAC-I",
                notes="live_visual is now presentation/dispatch. All unique capabilities preserved."),
        Circuit("LE-10", "attention_rank vs Relevance V2",
                CLOSED, "knowledge",
                evidence="RCCR-I Phases C-F: attention_rank serves interactive attend (Program.attend); Relevance V2 serves autonomous selection (Dell 37). No unique input for adapter; would create second ranking authority. No adapter warranted.",
                closure_cycle="RCCR-I",
                notes="Circuits separate by design. attention_rank remains in use for attend command."),
        Circuit("LE-12", "DCC-TRACE-VIEW spec",
                BLOCKED, "dcc",
                dependency_ids=["DCC-XXXII-directive"],
                evidence="Blocked on DCC-XXXII directive; NBD dcc-trace-view BLOCKED"),
        Circuit("LE-13", "NBD_LOG stamping law",
                SUPERSEDED, "nbd",
                evidence="NBDE-I fingerprint supersedes stamping (identity, temporal binding, staleness). No log file exists to overwrite. No persistence requirement in NBD contract.",
                closure_cycle="CDPC-I",
                superseded_by="NBDE-I state fingerprint architecture",
                notes="See CDPC-I Phase F-H. Underlying concern addressed by different mechanism. Persistent NBD history would be a new requirement, not LE-13."),
        Circuit("LE-15", "Preform 08 shallow-copy flaw",
                CLOSED, "runtime",
                evidence="RCCR-I Phases G-H: No copy operation in form/avatar/body.py. All BodyState fields immutable (tuples, Enums, Optional[str]). Each Avatar gets independent BodyState via default_factory. DEAD_PATH.",
                closure_cycle="RCCR-I",
                notes="Flaw not inherited; no copy path exists."),
        Circuit("LE-20", "program_strength.py not in regress.py",
                CLOSED, "testing",
                evidence="Registered in regress.py; VALID_CERTIFICATION (deterministic, safe, holistic). See CDPC-I Phase C-E.",
                closure_cycle="CDPC-I",
                notes="NBD #1 resolved correctly. Contract documented in cdpc1_program_strength.md."),
        Circuit("LE-25", "Git history secrets scan",
                CLOSED, "security",
                evidence="HIC-I: gitleaks 8.18.4 full history scan (521 commits, 53 branches, 1 tag). 1 finding: DOCUMENTATION_EXAMPLE false positive in docs/SECRETS_SCAN.md (describes patterns, not a secret). 0 confirmed, 0 probable. Manual checks: no .env, .pem, .key, AKIA, ghp_, password assignments in history.",
                closure_cycle="HIC-I",
                notes="Historical cleanliness proven. No CI secret scan exists (reported separately, not a blocker)."),

        # ── HISTORICAL_ONLY ─────────────────────────────────────
        Circuit("LE-09", "MODE_LUPE stale unrevoked law",
                HISTORICAL_ONLY, "archaeology",
                evidence="Zero matches in form/**/*.py on current main",
                notes="Law is dead; historical documentation only."),
    ]

def get_circuit(circuit_id: str) -> Optional[Circuit]:
    for c in build_ledger():
        if c.circuit_id == circuit_id:
            return c
    return None

def by_state(state: str) -> List[Circuit]:
    return [c for c in build_ledger() if c.state == state]

def ready_set() -> List[Circuit]:
    """Circuits eligible for NBD ranking."""
    return by_state(READY)

def closed_set() -> List[Circuit]:
    return by_state(CLOSED)

# No-resurrection law enforcement
def is_resurrection(circuit_id: str, new_state: str) -> bool:
    """True if this would be an illegal silent resurrection."""
    c = get_circuit(circuit_id)
    if c is None:
        return False
    if c.state == CLOSED and new_state in (OPEN, READY):
        return True
    return False
