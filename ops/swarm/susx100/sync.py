"""SUSX100 synchronization.

Agents synchronize at dependency boundaries, not through continuous
chatter. Independent verification must complete BEFORE its conclusions
can contaminate other agents (independence guard).
"""
from __future__ import annotations

PHASES = [
    "FAN_OUT",
    "INDEPENDENT_WORK",
    "CHECKPOINT",
    "EVIDENCE_INGEST",
    "CONTRADICTION_SCAN",
    "TARGETED_REQUERY",
    "FAN_IN",
    "PRISM_RECONCILIATION",
]


class SyncError(ValueError):
    pass


class Synchronizer:
    def __init__(self) -> None:
        self.phase_idx = 0
        self.log: list[dict] = []
        self._independent_done: set[str] = set()

    @property
    def phase(self) -> str:
        return PHASES[self.phase_idx]

    def advance(self, note: str = "") -> str:
        if self.phase_idx >= len(PHASES) - 1:
            raise SyncError("synchronization already at PRISM_RECONCILIATION")
        self.phase_idx += 1
        self.log.append({"phase": self.phase, "note": note})
        return self.phase

    def mark_independent_done(self, instance_id: str) -> None:
        self._independent_done.add(instance_id)

    def ingest(self, instance_id: str, evidence: dict) -> None:
        """EVIDENCE_INGEST refuses conclusions from agents whose independent
        work is not marked done — prevents contamination of independent
        verification with expected answers."""
        if self.phase != "EVIDENCE_INGEST":
            raise SyncError(f"ingest only in EVIDENCE_INGEST, currently {self.phase}")
        self.log.append({"phase": "EVIDENCE_INGEST", "instance": instance_id,
                         "independent": instance_id in self._independent_done,
                         "evidence": evidence})
