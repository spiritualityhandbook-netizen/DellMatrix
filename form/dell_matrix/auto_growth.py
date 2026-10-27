#!/usr/bin/env python3
"""
Auto Growth — the automated Nursery producer (WO-5.1).

KEPT AUTHORITY (SD-5 trim): AutoGrowth._nursery_auto is the
canonical auto-propose path, contract-proven by
form/lineage_authority_test.py: AUTO PROPOSE >
Program.confirm_proposal (VALIDATE > PLACE > Nursery.confirm >
PERSIST) > {ok:True} > COUNT SUCCESS. AUTO never mutates
confirmation status itself; acceptance requires explicit opt-in
(auto=True) plus AcceptancePolicy's producer gate — denied by
default. The judge is INJECTED as a dict by the caller; this
module no longer computes verita/floor judgments itself.

RETIRED in SD-5 (master plan P8) with the dormant free-matrix
cluster: the continuous growth orchestration (step /
run_continuous / harvest_net / next_query / _judge) — it had no
production caller, and its judging coupled to the retired
floor_spirit / delta_pressure modules. The docked semantic
layer (SD-1..SD-4) is the growth judge now; RingedGrowth is
the growth engine.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import json
import os
import time

_STATE = os.path.join(os.path.dirname(__file__), "..", "state")
try:
    os.makedirs(_STATE, exist_ok=True)
except OSError:
    _STATE = os.environ.get("DELLMATRIX_STATE", "/tmp/dellmatrix_state")
    os.makedirs(_STATE, exist_ok=True)
LEDGER_PATH = os.path.join(_STATE, "auto_growth_ledger.json")

MIN_VERITA = 0.45
MIN_COMBINED = 0.40


def _load_ledger() -> List[Dict[str, Any]]:
    if not os.path.isfile(LEDGER_PATH):
        return []
    try:
        with open(LEDGER_PATH, encoding="utf-8") as f:
            data = json.load(f)
        return list(data) if isinstance(data, list) else []
    except Exception:
        return []


def _save_ledger(rows: List[Dict[str, Any]]) -> None:
    rows = rows[-200:]
    try:
        with open(LEDGER_PATH, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2)
    except OSError:
        pass  # never crash growth on ledger IO


@dataclass
class AutoGrowth:
    # WO-5.1: Default OFF. Automated acceptance requires explicit opt-in.
    auto: bool = False
    internet: bool = True
    queries: List[str] = field(default_factory=lambda: [
        "systems thinking coherence",
        "eigenvalue stability dynamical systems",
        "offline first software architecture",
        "harmonic resonance pattern formation",
        "autonomous agent memory architecture",
    ])
    query_index: int = 0
    tick: int = 0
    confirmed_total: int = 0
    rejected_total: int = 0
    last_report: Dict[str, Any] = field(default_factory=dict)
    # Program owner whose canonical confirmation authority AUTO uses (persisted live Program).
    owner: str = "AutoGrow"

    def _should_auto_confirm(self, judge: Dict[str, Any], delta_band: str) -> bool:
        if not self.auto:
            return False
        if not judge.get("floor_accept"):
            return False
        if float(judge.get("verita_score") or 0) < MIN_VERITA:
            return False
        if float(judge.get("combined") or 0) < MIN_COMBINED:
            return False
        if judge.get("grade") in ("fog", "weak"):
            return False
        if delta_band == "critical":
            return "restore" in (judge.get("reason") or "") or float(judge.get("combined") or 0) >= 0.55
        return True

    def _nursery_auto(self, label: str, words: str, judge: Dict[str, Any], source: str) -> Dict[str, Any]:
        """AUTO PROPOSE > Program.confirm_proposal (VALIDATE > PLACE > Nursery.confirm > PERSIST) > {ok:True}
        > COUNT SUCCESS. AUTO never mutates confirmation status itself; failures and errors count nothing.
        A confirmed result changes the owner Program's semantic state, so that Program is saved."""
        try:
            from form.persist import load, save
            p = self._load_owner_program(load)
            prop = p.nursery.add(
                label=label,
                words=words,
                kind="auto",
                affinity=float(judge.get("combined") or 0),
                reason=f"auto:{source}:{judge.get('reason', '')}"[:160],
            )
            if self._should_auto_confirm(judge, self.last_report.get("delta_band", "elevated")):
                # WO-5.1: Pass producer ID. Denied by default without opt-in.
                res = p.confirm_proposal(prop.id, _producer="auto_growth")
                if res.get("ok") is True:
                    save(p)
                    self.confirmed_total += 1
                    status = "auto_confirmed"
                else:
                    status = "auto_confirm_failed"
            else:
                res = p.reject_proposal(prop.id)
                if res.get("ok") is True:
                    self.rejected_total += 1
                    status = "auto_rejected"
                else:
                    status = "auto_reject_failed"
            return {
                "id": prop.id,
                "status": status,
                "label": label[:72],
                "affinity": prop.affinity,
                "reason": res.get("reason"),
                "nursery": p.nursery.summary(),
            }
        except Exception as e:
            return {"id": None, "status": "auto_error", "label": label[:72], "error": str(e)}

    def _load_owner_program(self, load):
        """AutoGrow is an owner (D4): load its persisted Program WITHOUT binding it (activate=False). The caller's
        bound owner and working language stay untouched, and save(p) persists AutoGrow's own language."""
        return load(self.owner, activate=False)

    def _commit_ledger(self, item: Dict[str, Any]) -> None:
        rows = _load_ledger()
        rows.append({**item, "ts": time.time()})
        _save_ledger(rows)
