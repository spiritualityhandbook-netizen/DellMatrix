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
import hashlib
import json
import os
import re

_STATE_DIR = os.path.join(os.path.dirname(__file__), "..", "state")
os.makedirs(_STATE_DIR, exist_ok=True)
# Legacy ownerless file (pre per-owner nursery). Stranded: no Program reads, writes, or migrates it.
NURSERY_PATH = os.path.join(_STATE_DIR, "nursery.json")


class NurseryConflictError(RuntimeError):
    """The owner's nursery file changed on disk since this instance loaded/saved it (lost update refused)."""


def owner_nursery_path(owner: str) -> str:
    """Per-owner nursery file: nursery_<_safe_owner(owner)>.json (existing persist._safe_owner, no new sanitizer)."""
    from form.persist import _safe_owner
    return os.path.join(_STATE_DIR, f"nursery_{_safe_owner(owner)}.json")


def _disk_sig(path: str) -> Optional[str]:
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except FileNotFoundError:
        return None


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
    # DCC-XVI: versioned supersession (additive; confirmation untouched).
    # lifecycle_state: "active" | "superseded" — is this accepted revision
    # currently active for contextual routing? Legacy (None/absent) means
    # active with no revision history.
    lifecycle_state: str = "active"
    supersedes_id: Optional[str] = None      # predecessor this revision replaces
    superseded_by_id: Optional[str] = None   # successor that replaced this one
    revision_root_id: Optional[str] = None   # id of revision #1 in this chain
    revision_number: Optional[int] = None     # 1-based position in revision chain

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Nursery:
    """Quarantine for unconfirmed growth."""

    proposals: Dict[str, Proposal] = field(default_factory=dict)
    path: Optional[str] = None
    # Optimistic version of the owner file as last seen by this instance (sha256 of bytes; None = absent).
    _seen: Optional[str] = field(default=None, repr=False, compare=False)

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
        try:
            self.save()
        except Exception:
            self.proposals.pop(pid, None)
            raise
        return p

    def pending(self) -> List[Proposal]:
        return [p for p in self.proposals.values() if p.status == "pending"]

    def confirm(self, pid: str) -> Optional[Proposal]:
        p = self.proposals.get(pid)
        if not p or p.status != "pending":
            return None
        p.status = "confirmed"
        try:
            self.save()
        except Exception:
            p.status = "pending"
            raise
        return p

    def reject(self, pid: str) -> Optional[Proposal]:
        p = self.proposals.get(pid)
        if not p or p.status != "pending":
            return None
        p.status = "rejected"
        try:
            self.save()
        except Exception:
            p.status = "pending"
            raise
        return p

    def clear_rejected(self) -> int:
        before = dict(self.proposals)
        self.proposals = {k: v for k, v in self.proposals.items() if v.status != "rejected"}
        try:
            self.save()
        except Exception:
            self.proposals = before
            raise
        return len(before) - len(self.proposals)

    def summary(self) -> Dict[str, Any]:
        pending = self.pending()
        return {
            "pending": len(pending),
            "total": len(self.proposals),
            "confirmed": sum(1 for p in self.proposals.values() if p.status == "confirmed"),
            "rejected": sum(1 for p in self.proposals.values() if p.status == "rejected"),
        }

    def save(self) -> None:
        """Whole-file write of this owner's nursery. Refuses (NurseryConflictError) if the file changed on
        disk since this instance last loaded/saved it, instead of silently overwriting another instance."""
        if not self.path:
            raise ValueError("Nursery has no owner path; construct it with Nursery.load(owner_nursery_path(owner))")
        current = _disk_sig(self.path)
        if current != self._seen:
            raise NurseryConflictError(
                f"nursery file changed on disk since load: {os.path.basename(self.path)} (lost update refused)"
            )
        text = json.dumps({k: v.to_dict() for k, v in self.proposals.items()}, indent=2)
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(text)
        self._seen = hashlib.sha256(text.encode("utf-8")).hexdigest()

    @classmethod
    def load(cls, path: Optional[str] = None) -> "Nursery":
        """Load the nursery owned by ``path``. No path -> empty ownerless in-memory nursery (save refuses).
        The legacy ownerless NURSERY_PATH is never read implicitly."""
        n = cls(path=path)
        if not path or not os.path.isfile(path):
            return n
        try:
            with open(path, "rb") as f:
                blob = f.read()
            n._seen = hashlib.sha256(blob).hexdigest()
            raw = json.loads(blob.decode("utf-8"))
            for k, v in raw.items():
                n.proposals[k] = Proposal(**v)
        except Exception:
            pass
        return n
