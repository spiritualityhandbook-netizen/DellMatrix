"""SUSX100 per-persona performance ledger (self-diagnosis).

No vanity score. Every metric is inspectable. The ledger informs proposals;
it never authorizes them.
"""
from __future__ import annotations

import time

FIELDS = [
    "missions",
    "useful_findings",
    "contradictions_found",
    "false_positives",
    "claims_later_falsified",
    "escaped_defects",
    "unnecessary_work_prevented",
    "unknowns_correctly_preserved",
    "rework_caused",
    "token_input_cost",
    "production_delta_contributed",
]


def new_ledger(persona: str) -> dict:
    return {"persona": persona, "updated": None,
            **{f: 0 for f in FIELDS}, "notes": []}


def record(ledger: dict, field: str, delta: int | float = 1, note: str = "") -> dict:
    if field not in FIELDS:
        raise ValueError(f"unknown ledger field: {field}")
    ledger[field] += delta
    ledger["updated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    if note:
        ledger["notes"].append(note)
    return ledger


def diagnose(ledger: dict) -> dict:
    """Self-diagnosis: surface weaknesses as inspectable statements.
    Returns weaknesses; proposes nothing (proposals live in improvement.py)."""
    weaknesses = []
    if ledger["false_positives"] > ledger["useful_findings"]:
        weaknesses.append("false positives exceed useful findings: evidence threshold too low")
    if ledger["claims_later_falsified"] > 0:
        weaknesses.append(f"{ledger['claims_later_falsified']} claims later falsified: classification discipline weak")
    if ledger["escaped_defects"] > 0:
        weaknesses.append(f"{ledger['escaped_defects']} escaped defects: attack surface incomplete")
    if ledger["rework_caused"] > 2:
        weaknesses.append("repeated rework: output contract not respected")
    if ledger["missions"] > 0 and ledger["useful_findings"] == 0:
        weaknesses.append("missions produced no useful findings: spawning policy or task fit wrong")
    return {"persona": ledger["persona"], "weaknesses": weaknesses,
            "raw": {f: ledger[f] for f in FIELDS}}
