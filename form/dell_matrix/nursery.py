#!/usr/bin/env python3
"""
Nursery / Void / Op-Box

Proposed ideas live here until the user confirms them.
Rules:
- Preserved
- Quarantined
- Cannot grow further
- Cannot influence growth of anything else
- Only confirmed ideas enter the active matrix
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import json
import os
import re

_STATE_DIR = os.path.join(os.path.dirname(__file__), "..", "state")
os.makedirs(_STATE_DIR, exist_ok=True)
NURSERY_PATH = os.path.join(_STATE_DIR, "nursery.json")


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return (s[:28] or "proposal") + "_" + str(abs(hash(text)) % 10000)


@dataclass
class Proposal:
    id: str
    label: str
    words: str
    kind: str  # "new" | "evolved"
    parents: List[str] = field(default_factory=list)
    affinity: float = 0.0
    reason: str = ""
    created: str = field(default_factory=_ts)
    status: str = "pending"  # pending | confirmed | rejected

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Nursery:
    """Quarantine for unconfirmed growth."""

    proposals: Dict[str, Proposal] = field(default_factory=dict)

    def add(
        self,
        label: str,
        words: str = "",
        kind: str = "new",
        parents: Optional[List[str]] = None,
        affinity: float = 0.0,
        reason: str = "",
    ) -> Proposal:
        pid = _slug(label)
        # avoid exact id collision
        if pid in self.proposals:
            pid = pid + "_" + str(len(self.proposals))
        p = Proposal(
            id=pid,
            label=label[:80],
            words=words[:240],
            kind=kind,
            parents=parents or [],
            affinity=float(affinity),
            reason=reason[:160],
        )
        self.proposals[pid] = p
        self.save()
        return p

    def pending(self) -> List[Proposal]:
        return [p for p in self.proposals.values() if p.status == "pending"]

    def confirm(self, pid: str) -> Optional[Proposal]:
        p = self.proposals.get(pid)
        if not p or p.status != "pending":
            return None
        p.status = "confirmed"
        self.save()
        return p

    def reject(self, pid: str) -> Optional[Proposal]:
        p = self.proposals.get(pid)
        if not p or p.status != "pending":
            return None
        p.status = "rejected"
        self.save()
        return p

    def clear_rejected(self) -> int:
        before = len(self.proposals)
        self.proposals = {k: v for k, v in self.proposals.items() if v.status != "rejected"}
        self.save()
        return before - len(self.proposals)

    def summary(self) -> Dict[str, Any]:
        pending = self.pending()
        return {
            "pending": len(pending),
            "total": len(self.proposals),
            "confirmed": sum(1 for p in self.proposals.values() if p.status == "confirmed"),
            "rejected": sum(1 for p in self.proposals.values() if p.status == "rejected"),
        }

    def save(self) -> None:
        data = {k: v.to_dict() for k, v in self.proposals.items()}
        with open(NURSERY_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls) -> "Nursery":
        n = cls()
        if not os.path.isfile(NURSERY_PATH):
            return n
        try:
            with open(NURSERY_PATH, encoding="utf-8") as f:
                raw = json.load(f)
            for k, v in raw.items():
                n.proposals[k] = Proposal(**v)
        except Exception:
            pass
        return n
