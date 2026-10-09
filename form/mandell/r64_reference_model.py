"""R6.4 independent reference model.

A small, independent implementation of the EXPECTED outcomes for the
multi-agent shared-state protocol: agent identity, request ordering,
revocation, and retry semantics.

This model does NOT call any production decision helper (no
AcceptancePolicy, no coordinator, no writer). It computes expected
allow/deny outcomes from first principles given the same input
sequence. The proof suite compares production behavior against this
model; disagreement is a defect in either.

Scope: identity binding, grant subject matching, content freshness,
revocation, idempotent retry, request_id reuse, and rollback-epoch
staleness. The model is deliberately simpler than production (no
persistence, no real crypto) — it models the DECISION LOGIC only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class RefGrant:
    grant_id: str
    subject: str
    target: str
    content_hash: str
    revoked: bool = False
    max_uses: int = 1
    uses: int = 0


@dataclass
class RefAgent:
    subject: str
    registered: bool = True


class ReferenceModel:
    """Independent decision model for the R6.4 protocol."""

    def __init__(self):
        self.agents: Dict[str, RefAgent] = {}
        self.grants: Dict[str, RefGrant] = {}
        self.committed_pids: set = set()
        self.receipts: Dict[str, dict] = {}
        self.epoch: int = 0
        self.content: Dict[str, str] = {}  # pid -> content_hash

    # -- setup (trusted host actions) ------------------------------------

    def register(self, subject: str):
        self.agents[subject] = RefAgent(subject=subject)

    def issue(self, grant_id: str, subject: str, target: str,
              content_hash: str, max_uses: int = 1):
        self.grants[grant_id] = RefGrant(
            grant_id=grant_id, subject=subject, target=target,
            content_hash=content_hash, max_uses=max_uses)

    def revoke(self, grant_id: str):
        g = self.grants.get(grant_id)
        if g:
            g.revoked = True

    def set_content(self, pid: str, content_hash: str):
        self.content[pid] = content_hash

    def advance_epoch(self):
        self.epoch += 1

    # -- decision ---------------------------------------------------------

    def decide(self, subject: str, request_id: str, pid: str,
               grant_id: str, expected_hash: Optional[str],
               epoch_at_enqueue: int) -> Tuple[bool, str]:
        """Return (allowed, reason). Pure decision logic."""
        # Idempotency: exact retry.
        prior = self.receipts.get(request_id)
        if prior is not None:
            if prior["pid"] == pid and prior["hash"] == expected_hash:
                return True, "idempotent_retry"
            return False, "request_id_reuse"
        # Identity.
        if subject not in self.agents:
            return False, "unknown_subject"
        # Epoch staleness.
        if epoch_at_enqueue != self.epoch:
            return False, "stale_after_rollback"
        # Grant checks.
        g = self.grants.get(grant_id)
        if g is None:
            return False, "unknown_grant"
        if g.revoked:
            return False, "grant_revoked"
        if g.subject != subject:
            return False, "subject_mismatch"
        if g.target != pid:
            return False, "target_mismatch"
        if g.uses >= g.max_uses:
            return False, "grant_exhausted"
        # Freshness.
        live_hash = self.content.get(pid, "")
        if expected_hash and expected_hash != live_hash:
            return False, "content_changed"
        # Commit.
        g.uses += 1
        self.committed_pids.add(pid)
        self.receipts[request_id] = {"pid": pid, "hash": expected_hash}
        return True, "committed"

    def expect_sequence(self, steps: List[dict]) -> List[Tuple[bool, str]]:
        """Run a scripted sequence; return expected (allowed, reason) pairs."""
        out = []
        for s in steps:
            kind = s["kind"]
            if kind == "register":
                self.register(s["subject"])
                out.append((True, "registered"))
            elif kind == "issue":
                self.issue(s["grant_id"], s["subject"], s["pid"],
                           s["content_hash"], s.get("max_uses", 1))
                out.append((True, "issued"))
            elif kind == "revoke":
                self.revoke(s["grant_id"])
                out.append((True, "revoked"))
            elif kind == "set_content":
                self.set_content(s["pid"], s["content_hash"])
                out.append((True, "content_set"))
            elif kind == "advance_epoch":
                self.advance_epoch()
                out.append((True, "epoch_advanced"))
            elif kind == "request":
                out.append(self.decide(
                    s["subject"], s["request_id"], s["pid"],
                    s["grant_id"], s.get("expected_hash"),
                    s.get("epoch_at_enqueue", self.epoch)))
            else:
                raise ValueError(f"unknown step kind: {kind}")
        return out
