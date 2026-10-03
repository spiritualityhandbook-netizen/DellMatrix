#!/usr/bin/env python3
"""Canonical Idea — GDP-001 Phase 1, Requirement 1.1.

The fundamental DellMatrix object is AN EVOLVING IDEA.

An Idea has:
- Stable UUID identity (independent of title, content, location)
- Versioned properties (no destructive overwrite)
- Lifecycle states (ACTIVE, FADED, SUPERSEDED, PROPOSED, ACCEPTED, REJECTED, ARCHIVED, DELETED, RESTORED)
- Bitemporal history (valid time + transaction time)
- PROV-like provenance (Entity/Activity/Agent)
- Fail-closed persistence (Phase-0 contracts)

Research basis:
- Event sourcing (Fowler): append-only event log, state derived by replay
- W3C PROV: Entity/Activity/Agent for provenance
- Bitemporal (Datomic/SQL:2011): valid time vs transaction time
- Surrogate keys: UUID identity independent of business data
- Soft delete: FADED != DELETED; history preserved
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional


class LifecycleState(str, Enum):
    """Lifecycle states for Idea properties. Distinct semantics."""

    ACTIVE = "active"           # Participates in current Idea state
    FADED = "faded"             # Recoverable/history-visible, not current-active
    SUPERSEDED = "superseded"   # Replaced by a newer version; history preserved
    PROPOSED = "proposed"       # Possibility, not yet established truth
    ACCEPTED = "accepted"       # Proposal accepted into Idea truth
    REJECTED = "rejected"       # Proposal rejected; preserved, not erased
    ARCHIVED = "archived"       # Long-term storage, not active
    DELETED = "deleted"         # Marked deleted (soft); recoverable
    RESTORED = "restored"       # Brought back from faded/archived/deleted


class ProvenanceSource(str, Enum):
    """Who/what provided the information. UNKNOWN is legitimate."""

    HUMAN = "human"
    AI = "ai"
    EXTERNAL = "external"  # Internet/external source
    SYSTEM = "system"
    UNKNOWN = "unknown"


@dataclass
class Provenance:
    """PROV-like provenance: why does this information exist here?

    Entity: the property version (implicit).
    Activity: the operation/process that produced it.
    Agent: who/what is responsible.
    """

    source: ProvenanceSource
    activity: str  # e.g., "human_edit", "proposal_accepted", "supersession", "restoration"
    agent: str  # identifier of the responsible party
    derived_from: List[str] = field(default_factory=list)  # UUIDs of source versions
    detail: str = ""  # human-readable explanation

    def to_dict(self) -> dict:
        return {
            "source": self.source.value,
            "activity": self.activity,
            "agent": self.agent,
            "derived_from": self.derived_from,
            "detail": self.detail,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Provenance":
        return cls(
            source=ProvenanceSource(d["source"]),
            activity=d["activity"],
            agent=d["agent"],
            derived_from=d.get("derived_from", []),
            detail=d.get("detail", ""),
        )


@dataclass(frozen=True)
class PropertyVersion:
    """One version of a property. Immutable once created.

    Transitions (supersede, fade, accept) create NEW version records;
    they never mutate existing ones. This preserves the append-only
    event-sourced semantics and Phase-0 sealed-history compatibility.
    """

    version_id: str  # UUID
    value: Any
    state: LifecycleState
    valid_from: float  # Valid time: when this became true in the domain
    valid_to: Optional[float]  # Valid time: when this stopped being true (None = still valid)
    transaction_time: float  # Transaction time: when recorded in the system
    provenance: Provenance
    supersedes: Optional[str] = None  # version_id of the version this replaces
    superseded_by: Optional[str] = None  # version_id of the version replacing this

    def to_dict(self) -> dict:
        return {
            "version_id": self.version_id,
            "value": self.value,
            "state": self.state.value,
            "valid_from": self.valid_from,
            "valid_to": self.valid_to,
            "transaction_time": self.transaction_time,
            "provenance": self.provenance.to_dict(),
            "supersedes": self.supersedes,
            "superseded_by": self.superseded_by,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "PropertyVersion":
        return cls(
            version_id=d["version_id"],
            value=d["value"],
            state=LifecycleState(d["state"]),
            valid_from=d["valid_from"],
            valid_to=d.get("valid_to"),
            transaction_time=d["transaction_time"],
            provenance=Provenance.from_dict(d["provenance"]),
            supersedes=d.get("supersedes"),
            superseded_by=d.get("superseded_by"),
        )


class Idea:
    """Canonical evolving Idea.

    Identity is a stable UUID, independent of title/content/location.
    Properties are versioned; no destructive overwrite.
    History is append-only; state is derived.
    """

    def __init__(self, idea_id: Optional[str] = None, title: str = ""):
        self.id = idea_id or str(uuid.uuid4())
        self.title = title
        self.created_at = time.time()
        self.modified_at = self.created_at
        # property_name -> list of versions (chronological)
        self._properties: Dict[str, List[PropertyVersion]] = {}
        self._title_history: List[PropertyVersion] = []
        # Lifecycle state of the Idea itself
        self._idea_state = LifecycleState.ACTIVE
        self._idea_state_history: List[tuple] = []  # (state, timestamp, reason)

    # ------------------------------------------------------------------
    # Identity (1.1.1)
    # ------------------------------------------------------------------

    @property
    def identity(self) -> str:
        """Stable identity. Renaming does not change this."""
        return self.id

    def rename(self, new_title: str, provenance: Optional[Provenance] = None) -> None:
        """Rename preserves identity; old title in history."""
        prov = provenance or Provenance(
            source=ProvenanceSource.UNKNOWN,
            activity="rename",
            agent="unknown",
        )
        old_version = PropertyVersion(
            version_id=str(uuid.uuid4()),
            value=self.title,
            state=LifecycleState.SUPERSEDED,
            valid_from=self.created_at,
            valid_to=time.time(),
            transaction_time=time.time(),
            provenance=prov,
        )
        self._title_history.append(old_version)
        self.title = new_title
        self.modified_at = time.time()

    # ------------------------------------------------------------------
    # Properties (1.1.2, 1.2, 1.3)
    # ------------------------------------------------------------------

    def set_property(
        self,
        name: str,
        value: Any,
        provenance: Optional[Provenance] = None,
        state: LifecycleState = LifecycleState.ACTIVE,
    ) -> str:
        """Set a property. Previous ACTIVE version is superseded (not destroyed).

        Event-sourced: creates a NEW immutable version. The previous version
        is linked via `supersedes`; it is not mutated.

        Returns the new version_id.
        """
        prov = provenance or Provenance(
            source=ProvenanceSource.UNKNOWN,
            activity="set_property",
            agent="unknown",
        )
        now = time.time()
        versions = self._properties.setdefault(name, [])

        # Find the current ACTIVE version to supersede (by link, not mutation).
        supersedes_id = None
        for v in reversed(versions):
            if v.state == LifecycleState.ACTIVE:
                supersedes_id = v.version_id
                break

        new_version = PropertyVersion(
            version_id=str(uuid.uuid4()),
            value=value,
            state=state,
            valid_from=now,
            valid_to=None,
            transaction_time=now,
            provenance=prov,
            supersedes=supersedes_id,
        )
        versions.append(new_version)
        self.modified_at = now

        # Live Matrix: information arrival triggers eligible processing.
        self._on_information_change(name, new_version)
        return new_version.version_id

    def _current_version(self, name: str) -> Optional[PropertyVersion]:
        """The current version: latest ACTIVE, or None."""
        versions = self._properties.get(name, [])
        # A version is superseded if another version's `supersedes` points to it.
        superseded_ids = {v.supersedes for v in versions if v.supersedes}
        for v in reversed(versions):
            if v.state == LifecycleState.ACTIVE and v.version_id not in superseded_ids:
                return v
        return None

    def get_property(self, name: str, state: LifecycleState = LifecycleState.ACTIVE) -> Optional[Any]:
        """Get current value of a property in the given state."""
        if state == LifecycleState.ACTIVE:
            v = self._current_version(name)
            return v.value if v else None
        # For other states, return the latest version in that state.
        versions = self._properties.get(name, [])
        for v in reversed(versions):
            if v.state == state:
                return v.value
        return None

    def get_active_properties(self) -> Dict[str, Any]:
        """All ACTIVE properties (current truth). Single truth state."""
        result = {}
        for name in self._properties:
            v = self._current_version(name)
            if v:
                result[name] = v.value
        return result

    def get_property_history(self, name: str) -> List[PropertyVersion]:
        """Full history of a property (all states)."""
        return list(self._properties.get(name, []))

    def fade_property(
        self,
        name: str,
        provenance: Optional[Provenance] = None,
    ) -> bool:
        """Fade a property: create a FADED version (immutable event).

        The previous ACTIVE version is preserved; the FADED version
        links to it via `supersedes`. Recoverable, not deleted.
        """
        prov = provenance or Provenance(
            source=ProvenanceSource.UNKNOWN,
            activity="fade",
            agent="unknown",
        )
        current = self._current_version(name)
        if current is None:
            return False
        now = time.time()
        faded = PropertyVersion(
            version_id=str(uuid.uuid4()),
            value=current.value,
            state=LifecycleState.FADED,
            valid_from=now,
            valid_to=None,
            transaction_time=now,
            provenance=prov,
            supersedes=current.version_id,
        )
        self._properties[name].append(faded)
        self.modified_at = now
        self._on_information_change(name, faded)
        return True

    def get_faded_properties(self) -> Dict[str, Any]:
        """All FADED properties (latest FADED version per property)."""
        result = {}
        for name, versions in self._properties.items():
            for v in reversed(versions):
                if v.state == LifecycleState.FADED:
                    # Only if not superseded by a later ACTIVE.
                    if self._current_version(name) is None:
                        result[name] = v.value
                    break
        return result

    def get_superseded_history(self, name: str) -> List[PropertyVersion]:
        """Superseded versions: ACTIVE versions that have been superseded by link."""
        versions = self._properties.get(name, [])
        superseded_ids = {v.supersedes for v in versions if v.supersedes}
        return [v for v in versions
                if v.version_id in superseded_ids
                and v.state == LifecycleState.ACTIVE]

    def propose_property(
        self,
        name: str,
        value: Any,
        provenance: Optional[Provenance] = None,
    ) -> str:
        """Propose a property value. Does NOT become ACTIVE truth.

        Returns the proposal version_id. The proposal is in PROPOSED state
        until accepted or rejected. Reuses the versioned property model;
        a parallel proposal universe is not created.
        """
        prov = provenance or Provenance(
            source=ProvenanceSource.UNKNOWN,
            activity="propose",
            agent="unknown",
        )
        now = time.time()
        versions = self._properties.setdefault(name, [])
        proposal = PropertyVersion(
            version_id=str(uuid.uuid4()),
            value=value,
            state=LifecycleState.PROPOSED,
            valid_from=now,
            valid_to=None,
            transaction_time=now,
            provenance=prov,
        )
        versions.append(proposal)
        self.modified_at = now
        return proposal.version_id

    def accept_proposal(
        self,
        name: str,
        version_id: str,
        provenance: Optional[Provenance] = None,
    ) -> bool:
        """Accept a proposal: create an ACTIVE version from the proposal.

        The proposal itself is preserved (PROPOSED state, immutable).
        The new ACTIVE version records the acceptance in its provenance.
        This avoids the ACCEPTED/ACTIVE dual-truth: ACTIVE is the single
        current-truth state.

        Returns True if accepted, False if not found or not in PROPOSED state.
        """
        prov = provenance or Provenance(
            source=ProvenanceSource.UNKNOWN,
            activity="proposal_accepted",
            agent="unknown",
        )
        versions = self._properties.get(name, [])
        proposal = None
        for v in versions:
            if v.version_id == version_id and v.state == LifecycleState.PROPOSED:
                proposal = v
                break
        if proposal is None:
            return False
        now = time.time()
        # Find current ACTIVE to supersede (by link).
        supersedes_id = None
        current = self._current_version(name)
        if current:
            supersedes_id = current.version_id
        # Create ACTIVE version with acceptance provenance.
        # The provenance chains: proposal provenance + acceptance activity.
        accept_prov = Provenance(
            source=prov.source,
            activity="proposal_accepted",
            agent=prov.agent,
            derived_from=[proposal.version_id],
            detail=f"Accepted proposal {proposal.version_id[:8]}: {prov.detail}",
        )
        active_version = PropertyVersion(
            version_id=str(uuid.uuid4()),
            value=proposal.value,
            state=LifecycleState.ACTIVE,
            valid_from=now,
            valid_to=None,
            transaction_time=now,
            provenance=accept_prov,
            supersedes=supersedes_id,
        )
        versions.append(active_version)
        self.modified_at = now
        self._on_information_change(name, active_version)
        return True

    def reject_proposal(
        self,
        name: str,
        version_id: str,
        provenance: Optional[Provenance] = None,
    ) -> bool:
        """Reject a proposal: create a REJECTED version (immutable event).

        The original PROPOSED version is preserved. The REJECTED version
        records who rejected and why in its provenance.
        """
        prov = provenance or Provenance(
            source=ProvenanceSource.UNKNOWN,
            activity="proposal_rejected",
            agent="unknown",
        )
        versions = self._properties.get(name, [])
        proposal = None
        for v in versions:
            if v.version_id == version_id and v.state == LifecycleState.PROPOSED:
                proposal = v
                break
        if proposal is None:
            return False
        now = time.time()
        rejected = PropertyVersion(
            version_id=str(uuid.uuid4()),
            value=proposal.value,
            state=LifecycleState.REJECTED,
            valid_from=now,
            valid_to=None,
            transaction_time=now,
            provenance=Provenance(
                source=prov.source,
                activity="proposal_rejected",
                agent=prov.agent,
                derived_from=[proposal.version_id],
                detail=prov.detail,
            ),
            supersedes=proposal.version_id,
        )
        versions.append(rejected)
        self.modified_at = now
        return True

    def get_proposals(self, name: Optional[str] = None) -> Dict[str, List[PropertyVersion]]:
        """Get PROPOSED versions, optionally filtered by property name."""
        result = {}
        names = [name] if name else list(self._properties.keys())
        for n in names:
            props = [v for v in self._properties.get(n, [])
                     if v.state == LifecycleState.PROPOSED]
            if props:
                result[n] = props
        return result

    # ------------------------------------------------------------------
    # Idea lifecycle: archive / delete / restore (1.2.5)
    # ------------------------------------------------------------------

    def archive(self, reason: str = "") -> None:
        """Archive the Idea. Not active, but preserved and restorable."""
        self._idea_state_history.append((self._idea_state, time.time(), f"archive: {reason}"))
        self._idea_state = LifecycleState.ARCHIVED
        self.modified_at = time.time()

    def delete(self, reason: str = "") -> None:
        """Soft-delete the Idea. Marked, not destroyed. Recoverable."""
        self._idea_state_history.append((self._idea_state, time.time(), f"delete: {reason}"))
        self._idea_state = LifecycleState.DELETED
        self.modified_at = time.time()

    def restore(self, reason: str = "") -> None:
        """Restore from archived/deleted/faded. Restoration is history."""
        if self._idea_state not in (LifecycleState.ARCHIVED, LifecycleState.DELETED, LifecycleState.FADED):
            raise ValueError(f"Cannot restore from state {self._idea_state}")
        self._idea_state_history.append((self._idea_state, time.time(), f"restore: {reason}"))
        self._idea_state = LifecycleState.RESTORED
        self.modified_at = time.time()

    @property
    def idea_state(self) -> LifecycleState:
        return self._idea_state

    # ------------------------------------------------------------------
    # Live Matrix processing (1.5)
    # ------------------------------------------------------------------

    def _on_information_change(self, name: str, version: PropertyVersion) -> None:
        """Hook: information arrival/change triggers eligible processing.

        LIVE MATRIX LAW: processing is driven by information arrival,
        not by UI observation. This is the Phase-1 seam; later phases
        deepen the processing.
        """
        # Phase 1: record the change event. Later phases add dependency
        # propagation, semantic recomputation, etc.
        pass

    # ------------------------------------------------------------------
    # Persistence (1.1.5)
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "created_at": self.created_at,
            "modified_at": self.modified_at,
            "idea_state": self._idea_state.value,
            "idea_state_history": [
                {"state": s.value, "at": t, "reason": r}
                for s, t, r in self._idea_state_history
            ],
            "properties": {
                name: [v.to_dict() for v in versions]
                for name, versions in self._properties.items()
            },
            "title_history": [v.to_dict() for v in self._title_history],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Idea":
        idea = cls(idea_id=d["id"], title=d["title"])
        idea.created_at = d["created_at"]
        idea.modified_at = d["modified_at"]
        idea._idea_state = LifecycleState(d.get("idea_state", "active"))
        idea._idea_state_history = [
            (LifecycleState(h["state"]), h["at"], h["reason"])
            for h in d.get("idea_state_history", [])
        ]
        for name, vlist in d.get("properties", {}).items():
            idea._properties[name] = [PropertyVersion.from_dict(v) for v in vlist]
        idea._title_history = [PropertyVersion.from_dict(v)
                               for v in d.get("title_history", [])]
        return idea

    def explain(self, name: str) -> str:
        """Computationally grounded answer to: WHY DOES THIS INFORMATION EXIST HERE?"""
        versions = self._properties.get(name, [])
        if not versions:
            return f"No information recorded for property {name!r}."
        lines = [f"Property {name!r} history:"]
        for v in versions:
            p = v.provenance
            lines.append(
                f"  - {v.value!r} [{v.state.value}] "
                f"via {p.activity} by {p.agent} ({p.source.value}) "
                f"at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(v.transaction_time))}"
            )
            if p.derived_from:
                lines.append(f"    derived from: {', '.join(p.derived_from)}")
            if p.detail:
                lines.append(f"    detail: {p.detail}")
        return "\n".join(lines)
