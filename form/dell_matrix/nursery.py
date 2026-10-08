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


class NurseryLoadError(ValueError):
    """The owner's canonical nursery file exists but is not a complete valid
    generation (truncated/malformed JSON or invalid proposal records).

    Raised explicitly and honestly (DCC-XVII): a corrupt canonical file is
    NEVER silently replaced with an empty nursery. Precedence is
    valid-canonical -> load, else -> this error. No recovery generation is
    fabricated."""


# Reserved nursery-file key for DCC-XIX conflict dispositions. Can never
# collide with a proposal ID: _slug() output is lowercase alnum plus
# underscores, stripped of leading/trailing underscores, with a numeric
# hash suffix -- it can never equal this dunder constant.
DISPOSITION_SECTION_KEY = "__conflict_dispositions__"


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


def _slug(text: str, seed: int = 0) -> str:
    """Deterministic proposal ID: slugified label prefix + stable digest suffix.

    GDP-001 Phase 3, 3.1.4: the digest is SHA-256 over (seed, text), NOT
    Python's built-in hash() — hash() of str is salted per process
    (PYTHONHASHSEED), so pre-Phase-3 IDs were deterministic only WITHIN one
    process and differed across processes for the same label. With this
    change, the same (seed, label) yields the same ID in every process.
    The exact-collision fallback suffix ("_<count>") is deterministic given
    the same add sequence on an equal starting nursery.
    """
    s = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    digest = hashlib.sha256(f"{int(seed)}:{text}".encode("utf-8")).hexdigest()
    return (s[:28] or "proposal") + "_" + str(int(digest[:8], 16) % 10000)


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
    # P3 R3.6: harmony + graph coherence written by RingedGrowth.run.
    # harmony: harmony_score over the scored proposal pair (the two units
    #   whose _affinity produced the proposal), in [0, 1]; 0.0 neutral for
    #   non-pair proposals (e.g. body-restore) or when no pair content
    #   exists.
    # graph_coherence: graph_coherence() over the scored pair's canonical
    #   Idea IDs from the attached Phase-2 graph, in [0, 1]; 0.0 = no
    #   graph evidence (neutral), never fabricated. Both default 0.0 so
    #   pre-R3.6 nursery files load unchanged (Proposal(**record) fills
    #   defaults for missing keys).
    harmony: float = 0.0
    graph_coherence: float = 0.0
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
    # DCC-XIX: operator-governed conflict dispositions (conflict_id ->
    # disposition record). Serialized under a reserved key that can never
    # be a proposal ID (proposal IDs are _slug() output: lowercase
    # alnum/underscores, never leading/trailing double underscores plus a
    # hash suffix). Absence of a record means the default unresolved state.
    conflict_dispositions: Dict[str, Dict[str, Any]] = field(
        default_factory=dict, repr=False, compare=False)

    def repoint_to_live(self, live_path: str) -> None:
        """Re-point this instance's file ownership to the live owner file.

        DCC-XVIII repair (GDP-001 Phase 0, R1): a nursery staged from a
        sealed generation member arrives bound to the IMMUTABLE member file.
        Re-pointing gives committed/sealed state and mutable working state
        explicit, non-aliased ownership -- the sealed member can never be
        overwritten through this instance again.

        Only the binding changes: in-memory proposals and conflict
        dispositions are untouched, and no file is written here. ``_seen``
        is refreshed to the live file's current signature so the
        optimistic-concurrency guard keeps working against the live file;
        the next save() persists this (e.g. rolled-back) working state to
        the live file.
        """
        self.path = live_path
        self._seen = _disk_sig(live_path)

    def add(
        self,
        label: str,
        words: str = "",
        kind: str = "new",
        parents: Optional[List[str]] = None,
        affinity: float = 0.0,
        reason: str = "",
        seed: int = 0,
        harmony: float = 0.0,
        graph_coherence: float = 0.0,
    ) -> Proposal:
        """Add a proposal. ID = _slug(label, seed): deterministic given
        (seed, label, add-sequence) across processes (GDP-001 Phase 3, 3.1.4).
        Default seed=0 keeps a stable deterministic ID stream.

        P3 R3.6: harmony (harmony_score over the scored proposal pair,
        [0,1]) and graph_coherence (Phase-2 graph signal over the scored
        pair's canonical Idea IDs, [0,1]; 0.0 = no graph evidence) are
        persisted on the proposal. Program.ranked_proposals consumes them
        as tie-breakers, so the scores are read by a real consumer, not
        merely stored.
        """
        pid = _slug(label, seed)
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
            harmony=float(harmony),
            graph_coherence=float(graph_coherence),
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

    def save(self, *, _fail_at: Optional[str] = None) -> None:
        """Whole-file write of this owner's nursery via Persistence V2
        (crash-safe atomic replacement; DCC-XVII).

        Refuses (NurseryConflictError) if the file changed on disk since this
        instance last loaded/saved it, instead of silently overwriting another
        instance. After interruption the canonical file holds either the
        previous complete generation or the new complete generation.

        Director 2026-10-06 (close unsafe save): an instance whose
        compensation/rollback was incomplete rejects the save with
        RollbackRecoveryError until verified restoration or reconstruction.
        No bytes are written on rejection.
        """
        from form.mandell.core_i_recovery import check_save_allowed
        check_save_allowed(self, "nursery.save")
        from form.dell_matrix.atomic_write import atomic_write_json

        if not self.path:
            raise ValueError("Nursery has no owner path; construct it with Nursery.load(owner_nursery_path(owner))")
        current = _disk_sig(self.path)
        if current != self._seen:
            raise NurseryConflictError(
                f"nursery file changed on disk since load: {os.path.basename(self.path)} (lost update refused)"
            )
        payload = {k: v.to_dict() for k, v in self.proposals.items()}
        # DCC-XIX: the operator's conflict-disposition map rides the same
        # atomic write as the proposals, so the durable file always holds
        # one complete policy: the old one or the new one, never a mix.
        # A validated in-memory record is JSON-safe by construction
        # (validate_record at the command layer); the section is still
        # shape-checked on load.
        payload[DISPOSITION_SECTION_KEY] = {
            cid: dict(rec) for cid, rec in self.conflict_dispositions.items()
        }
        blob = atomic_write_json(self.path, payload, _fail_at=_fail_at)
        self._seen = hashlib.sha256(blob).hexdigest()

    @classmethod
    def load(cls, path: Optional[str] = None) -> "Nursery":
        """Load the nursery owned by ``path``. No path -> empty ownerless in-memory nursery (save refuses).
        The legacy ownerless NURSERY_PATH is never read implicitly.

        DCC-XVII load contract (Control T): the complete file is read,
        decoded, parsed and every proposal record validated into PRIVATE
        staging before anything is applied to the returned Nursery. A corrupt
        canonical file raises NurseryLoadError explicitly -- it is never
        silently replaced with an empty nursery and a failed load never
        leaves a partially mutated nursery behind.
        """
        n = cls(path=path)
        # R6.3: record restoration epoch; pre-restoration instances
        # are stale for save purposes (checked by check_save_allowed).
        # Uses canonical (_safe_owner) key from path (already sanitized).
        if path:
            import re as _re
            m = _re.search(r"nursery_(.+)\.json$", path)
            if m:
                from form.mandell.core_i_recovery import _rollback_epochs
                n._rollback_epoch = _rollback_epochs.get(m.group(1), 0)
        if not path or not os.path.isfile(path):
            return n
        try:
            with open(path, "rb") as f:
                blob = f.read()
        except OSError as exc:
            raise NurseryLoadError(f"cannot read nursery file {path}: {exc}") from exc
        try:
            raw = json.loads(blob.decode("utf-8"))
        except (UnicodeDecodeError, ValueError) as exc:
            raise NurseryLoadError(
                f"nursery file {os.path.basename(path)} is not a complete valid generation "
                f"(truncated/malformed JSON, {len(blob)} bytes on disk)"
            ) from exc
        if not isinstance(raw, dict):
            raise NurseryLoadError(
                f"nursery file {os.path.basename(path)} is not a complete valid generation "
                "(top-level JSON is not an object)"
            )
        staged: Dict[str, Proposal] = {}
        staged_dispositions: Dict[str, Dict[str, Any]] = {}
        try:
            for k, v in raw.items():
                # DCC-XIX: the reserved disposition section is staged
                # separately; it is never mistaken for a proposal.
                if k == DISPOSITION_SECTION_KEY:
                    if not isinstance(v, dict):
                        raise NurseryLoadError(
                            f"nursery file {os.path.basename(path)} has a malformed "
                            f"{DISPOSITION_SECTION_KEY} section (not an object)"
                        )
                    for cid, rec in v.items():
                        if not isinstance(cid, str) or not isinstance(rec, dict):
                            raise NurseryLoadError(
                                f"nursery file {os.path.basename(path)} has a malformed "
                                f"disposition record for {cid!r}"
                            )
                    staged_dispositions = {cid: dict(rec) for cid, rec in v.items()}
                    continue
                if not isinstance(v, dict):
                    raise NurseryLoadError(
                        f"nursery file {os.path.basename(path)} has an invalid proposal record for {k!r}"
                    )
                staged[k] = Proposal(**v)
        except NurseryLoadError:
            raise
        except Exception as exc:
            raise NurseryLoadError(
                f"nursery file {os.path.basename(path)} has an invalid proposal record: {exc}"
            ) from exc
        # Only now apply: nothing partial can escape.
        n.proposals = staged
        n.conflict_dispositions = staged_dispositions
        n._seen = hashlib.sha256(blob).hexdigest()
        return n
