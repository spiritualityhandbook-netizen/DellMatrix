#!/usr/bin/env python3
"""NBDE-I: current frontier candidate ledger (NBD-Ω-009 Phase N).

Builds the first real candidate set from verified current evidence.
Each candidate carries source/scope/kind per the evidence contract.

READ-ONLY: this module discovers and classifies. It does not execute,
mutate, or issue work.
"""
from __future__ import annotations

from typing import Any, List

from .nbd_engine import (
    Candidate, Evidence, FACT, DERIVED_FACT, PROJECTION, UNKNOWN,
    OPEN, BLOCKED, READY, CLOSED,
)


def _e(source: str, scope: str, detail: str, kind: str = FACT,
       verification: str = "") -> Evidence:
    return Evidence(source=source, scope=scope, detail=detail, kind=kind,
                    verification=verification)


def build_frontier(program: Any = None) -> List[Candidate]:
    """Construct the verified frontier candidate set."""
    out: List[Candidate] = []

    # ── 1. live-visual convergence (LE-04) ──────────────────────────
    out.append(Candidate(
        candidate_id="live-visual-convergence",
        title="live_visual command-authority convergence",
        target_circuit="ux/live_visual",
        locality="ux",
        evidence=[
            _e("form/dell_matrix/live_visual.py", "command routing",
               "live_visual._run_command is a parallel command authority "
               "vs the spine (C1); ROS-I recorded K1/K2 for later convergence",
               FACT, "code grep + NBD-Ω-007 K1/K2 record"),
            _e("NBD-Ω-001 loose ends", "LE-04",
               "LE-04 OPEN: live_visual parallel command authority; "
               "dependency R1 mapping design", FACT, "loose_ends.md"),
        ],
        expected_closures=1,
        expected_reuse=0.6,
        expected_future_work_avoided=2,
        verification_plan="Route sample commands through spine; verify "
                          "identical outcomes; no _run_command bypass.",
        risk=0.6, scope_interference=0.7, movement_cost=0.6,
        resonance=0.6, urgency=0.4,
        verification_confidence=0.5,
        projection_flags=["expected_closures", "expected_reuse",
                          "expected_future_work_avoided", "risk",
                          "resonance", "urgency"],
    ))

    # ── 2. NBD dogfooding ─────────────────────────────────────────
    out.append(Candidate(
        candidate_id="nbd-dogfood",
        title="NBD-Ω self-application after engine implementation",
        target_circuit="nbd",
        locality="nbd",
        evidence=[
            _e("NBD-Ω-009 directive", "Phase N",
               "Directive lists 'NBD itself after engine implementation' "
               "as a frontier candidate", FACT, "directive text"),
            _e("form/mandell/nbd_engine.py", "engine",
               "NBDE-I engine exists; first ranking produced", DERIVED_FACT,
               "nbd_packet output"),
        ],
        expected_closures=1,
        expected_reuse=0.8,
        expected_future_work_avoided=1,
        verification_plan="Run NBD on its own output; verify stable ranking.",
        risk=0.3, scope_interference=0.2, movement_cost=0.2,
        resonance=0.7, urgency=0.2,
        verification_confidence=0.6,
        historical_recovery=0.5,
        projection_flags=["expected_closures", "expected_reuse",
                          "expected_future_work_avoided", "risk",
                          "resonance", "urgency"],
    ))

    # ── 3. attention-rank adapter (LE-10) ──────────────────────────
    out.append(Candidate(
        candidate_id="attention-rank-adapter",
        title="attention_rank / Program.attend vs Relevance V2 adapter",
        target_circuit="knowledge/selection",
        locality="knowledge",
        evidence=[
            _e("NBD-Ω-001 loose ends", "LE-10",
               "LE-10 OPEN: attention_rank/Program.attend vs Relevance V2 "
               "adapter", FACT, "loose_ends.md"),
        ],
        expected_closures=1,
        expected_reuse=0.5,
        expected_future_work_avoided=1,
        verification_plan="Adapter routes attend through Relevance V2; "
                          "verify identical ranking.",
        risk=0.4, scope_interference=0.4, movement_cost=0.4,
        resonance=0.5, urgency=0.3,
        verification_confidence=0.5,
        projection_flags=["expected_closures", "expected_reuse",
                          "expected_future_work_avoided", "risk",
                          "resonance", "urgency"],
    ))

    # ── 4. DCC-TRACE-VIEW (LE-12) — BLOCKED ────────────────────────
    out.append(Candidate(
        candidate_id="dcc-trace-view",
        title="DCC-TRACE-VIEW dependency",
        target_circuit="dcc/trace",
        locality="dcc",
        evidence=[
            _e("NBD-Ω-001 loose ends", "LE-12",
               "LE-12: DCC-TRACE-VIEW spec blocked on DCC-XXXII directive",
               FACT, "loose_ends.md"),
        ],
        dependencies=["dcc-xxxii-directive"],
        expected_closures=1,
        verification_plan="N/A (blocked)",
        risk=0.5, scope_interference=0.3, movement_cost=0.3,
        projection_flags=["expected_closures", "risk"],
    ))

    # ── 5. explicit knowledge-choice mechanism ─────────────────────
    out.append(Candidate(
        candidate_id="explicit-knowledge-choice",
        title="Explicit knowledge-choice / exact-ID reference mechanism",
        target_circuit="knowledge/selection",
        locality="knowledge",
        evidence=[
            _e("NBD-Ω-008 ASI-I", "Phase K",
               "ASI-I verified: no explicit knowledge-choice mechanism "
               "exists; contextual selector is the only path", FACT,
               "asi_i_test.py test_i"),
            _e("NBD-Ω-008 loose ends", "frontier",
               "ASI-I packet lists explicit knowledge-choice as open "
               "frontier", FACT, "NBD_OMEGA_008_PACKET"),
        ],
        expected_closures=1,
        expected_reuse=0.4,
        expected_future_work_avoided=2,
        verification_plan="New command routes explicit ID; verify it "
                          "outranks learned preference; no selector duplication.",
        risk=0.5, scope_interference=0.5, movement_cost=0.4,
        resonance=0.6, urgency=0.3,
        verification_confidence=0.4,
        projection_flags=["expected_closures", "expected_reuse",
                          "expected_future_work_avoided", "risk",
                          "resonance", "urgency"],
    ))

    # ── 6. adaptive-cap measurement ────────────────────────────────
    out.append(Candidate(
        candidate_id="adaptive-cap-measurement",
        title="ASI learned-cap measurement experiment",
        target_circuit="asi/learning",
        locality="learning",
        evidence=[
            _e("NBD-Ω-008 ASI-I", "frontier",
               "ASI-I packet recommends measuring whether ±5 cap binds in "
               "practice", FACT, "NBD_OMEGA_008_PACKET"),
            _e("form/mandell/duobeta_learn.py", "ASI_LEARNED_CAP",
               "Cap is 5; no production data on binding frequency", FACT,
               "code read"),
        ],
        expected_closures=0,
        expected_reuse=0.3,
        expected_future_work_avoided=1,
        verification_plan="Sandboxed multi-cycle experiment; report cap "
                          "binding frequency; no selector change.",
        risk=0.2, scope_interference=0.1, movement_cost=0.3,
        resonance=0.4, urgency=0.2,
        verification_confidence=0.6,
        projection_flags=["expected_reuse", "expected_future_work_avoided",
                          "risk", "resonance", "urgency"],
    ))

    # ── 7. dead-path cleanup batch (LE-17/18/19) ───────────────────
    out.append(Candidate(
        candidate_id="dead-path-cleanup",
        title="Dead-path cleanup: gate_core_ii_bind, boot, smoke_all",
        target_circuit="cleanup",
        locality="cleanup",
        evidence=[
            _e("NBD-Ω-001 loose ends", "LE-17/18/19",
               "LE-17 gate_core_ii_bind dead; LE-18 boot.py false claim; "
               "LE-19 smoke_all disconnected", FACT, "loose_ends.md"),
            _e("form/mandell/gate_core_ii_bind.py", "existence",
               "File exists", FACT, "filesystem"),
        ],
        expected_closures=3,
        expected_reuse=0.2,
        expected_future_work_avoided=1,
        verification_plan="Remove or wire each; verify no importers break; "
                          "regress green.",
        risk=0.3, scope_interference=0.2, movement_cost=0.2,
        resonance=0.5, urgency=0.2,
        verification_confidence=0.7,
        projection_flags=["expected_reuse", "expected_future_work_avoided",
                          "risk", "resonance", "urgency"],
    ))

    # ── 8. phantom commands (LE-14/21) ────────────────────────────
    out.append(Candidate(
        candidate_id="phantom-commands",
        title="Phantom commands: SISTER_SETUP, --awake flag",
        target_circuit="docs/ux",
        locality="cleanup",
        evidence=[
            _e("NBD-Ω-001 loose ends", "LE-14/21",
               "LE-14 SISTER_SETUP phantom; LE-21 phantom --awake flag",
               FACT, "loose_ends.md"),
        ],
        expected_closures=2,
        expected_reuse=0.1,
        expected_future_work_avoided=0,
        verification_plan="Remove phantom docs/commands; verify no references.",
        risk=0.2, scope_interference=0.1, movement_cost=0.2,
        resonance=0.4, urgency=0.2,
        verification_confidence=0.7,
        projection_flags=["expected_reuse", "risk", "resonance", "urgency"],
    ))

    # ── 9. terminology/docs (LE-22/23/24) ──────────────────────────
    out.append(Candidate(
        candidate_id="terminology-docs",
        title="Terminology hazards: truth-of-meet, DOC_GAP_CLOSER, stale audits",
        target_circuit="docs",
        locality="cleanup",
        evidence=[
            _e("NBD-Ω-001 loose ends", "LE-22/23/24",
               "LE-22 truth-of-meet; LE-23 DOC_GAP_CLOSER; LE-24 stale audits",
               FACT, "loose_ends.md"),
        ],
        expected_closures=3,
        expected_reuse=0.1,
        expected_future_work_avoided=0,
        verification_plan="Fix terminology; date or refresh audits.",
        risk=0.1, scope_interference=0.1, movement_cost=0.1,
        resonance=0.3, urgency=0.1,
        verification_confidence=0.8,
        projection_flags=["expected_reuse", "risk", "resonance", "urgency"],
    ))

    # ── 10. program-strength registration (LE-20) ──────────────────
    out.append(Candidate(
        candidate_id="program-strength-registration",
        title="program_strength.py registration in regress",
        target_circuit="testing",
        locality="testing",
        evidence=[
            _e("NBD-Ω-001 loose ends", "LE-20",
               "LE-20: program_strength.py not in regress.py", FACT,
               "loose_ends.md"),
            _e("form/dell_matrix/program_strength.py", "existence",
               "File exists", FACT, "filesystem"),
        ],
        expected_closures=1,
        expected_reuse=0.3,
        expected_future_work_avoided=0,
        verification_plan="Wire into regress; verify green.",
        risk=0.2, scope_interference=0.1, movement_cost=0.1,
        resonance=0.4, urgency=0.2,
        verification_confidence=0.7,
        projection_flags=["expected_reuse", "risk", "resonance", "urgency"],
    ))

    # ── 11. NBD_LOG stamping (LE-13) ───────────────────────────────
    out.append(Candidate(
        candidate_id="nbd-log-stamping",
        title="NBD_LOG stamping law vs overwrite behavior",
        target_circuit="nbd",
        locality="nbd",
        evidence=[
            _e("NBD-Ω-001 loose ends", "LE-13",
               "LE-13 OPEN: NBD_LOG stamping law vs overwrite", FACT,
               "loose_ends.md"),
        ],
        expected_closures=1,
        expected_reuse=0.4,
        expected_future_work_avoided=1,
        verification_plan="Define stamping law; verify append-only.",
        risk=0.3, scope_interference=0.2, movement_cost=0.2,
        resonance=0.6, urgency=0.2,
        verification_confidence=0.5,
        projection_flags=["expected_closures", "expected_reuse",
                          "expected_future_work_avoided", "risk",
                          "resonance", "urgency"],
    ))

    # ── 12. body shallow-copy research (LE-15) ─────────────────────
    out.append(Candidate(
        candidate_id="body-shallow-copy",
        title="body.py shallow-copy flaw research",
        target_circuit="avatar",
        locality="avatar",
        evidence=[
            _e("NBD-Ω-001 loose ends", "LE-15",
               "LE-15: Preform 08 shallow-copy flaw; inherited by live "
               "form/avatar/body.py?", FACT, "loose_ends.md"),
            _e("form/avatar/body.py", "existence",
               "File exists at form/avatar/body.py", FACT, "filesystem"),
        ],
        expected_closures=1,
        expected_reuse=0.3,
        expected_future_work_avoided=1,
        verification_plan="Research copy semantics; fix if flawed.",
        risk=0.4, scope_interference=0.3, movement_cost=0.3,
        resonance=0.3, urgency=0.3,
        verification_confidence=0.4,
        projection_flags=["expected_closures", "expected_reuse",
                          "expected_future_work_avoided", "risk",
                          "resonance", "urgency"],
    ))

    return out

# ── LEAS-I: candidate → circuit mapping ──────────────────────────────
# Maps NBD candidate IDs to canonical circuit IDs from circuit_ledger.py.
# This is the ONE mapping table. Do not duplicate circuit state elsewhere.
CANDIDATE_CIRCUIT_MAP = {
    "dead-path-cleanup": ["LE-17", "LE-18", "LE-19"],
    "phantom-commands": ["LE-14", "LE-21"],
    "terminology-docs": ["LE-22", "LE-23", "LE-24"],
    "program-strength-registration": ["LE-20"],
    "nbd-log-stamping": ["LE-13"],
    "attention-rank-adapter": ["LE-10"],
    "dcc-trace-view": ["LE-12"],
    "body-shallow-copy": ["LE-15"],
    "live-visual-convergence": ["LE-04"],
    # nbd-dogfood, explicit-knowledge-choice, adaptive-cap-measurement
    # have no single LE mapping; they are frontier work, not loose-end closure.
}
