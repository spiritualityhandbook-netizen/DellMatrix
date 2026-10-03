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


@dataclass(frozen=True)
class IdeaChangeEvent:
    """Deterministic record that Live Matrix information-change processing
    occurred (Requirement 1.5).

    This is a DERIVED PROJECTION of a mutation operation, not a second
    authority: it references canonical PropertyVersion IDs and carries the
    operation's semantic consequence. The version lists remain the truth;
    the event is the processing receipt. Immutable and append-only.

    LIVE MATRIX LAW: the event exists because information arrived/changed,
    never because a Perspective was opened, zoomed, or rendered.
    """
    event_id: str  # UUID
    idea_id: str
    operation: str  # set_property | fade_property | propose_property |
                    # accept_proposal | reject_proposal | rename |
                    # archive | delete | restore
    property_name: Optional[str]  # None for idea-level lifecycle operations
    version_id: Optional[str]  # canonical PropertyVersion affected (None for lifecycle)
    superseded_version_id: Optional[str]  # the version this replaced, if any
    consequence: str  # semantic/lifecycle consequence, e.g. "ACTIVE established",
                      # "prior version superseded", "value faded",
                      # "proposal accepted", "lifecycle ACTIVE->ARCHIVED"
    timestamp: float
    provenance: Provenance

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "idea_id": self.idea_id,
            "operation": self.operation,
            "property_name": self.property_name,
            "version_id": self.version_id,
            "superseded_version_id": self.superseded_version_id,
            "consequence": self.consequence,
            "timestamp": self.timestamp,
            "provenance": self.provenance.to_dict(),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "IdeaChangeEvent":
        return cls(
            event_id=d["event_id"],
            idea_id=d["idea_id"],
            operation=d["operation"],
            property_name=d.get("property_name"),
            version_id=d.get("version_id"),
            superseded_version_id=d.get("superseded_version_id"),
            consequence=d["consequence"],
            timestamp=d["timestamp"],
            provenance=Provenance.from_dict(d["provenance"]),
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
        # Live Matrix processing record (1.5): append-only, immutable events.
        # Derived projection of mutations; PropertyVersion lists remain truth.
        self._change_events: List[IdeaChangeEvent] = []

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
        now = time.time()
        # A-5 fix: valid_from should be when this title became current,
        # not creation time. Use last title change or creation.
        valid_from = self.created_at
        if self._title_history:
            # The current title became valid when the last rename happened.
            # We track this via modified_at of the last title event.
            valid_from = self._title_history[-1].transaction_time
        old_version = PropertyVersion(
            version_id=str(uuid.uuid4()),
            value=self.title,
            state=LifecycleState.SUPERSEDED,
            valid_from=valid_from,
            valid_to=now,
            transaction_time=now,
            provenance=prov,
        )
        self._title_history.append(old_version)
        self.title = new_title
        self._on_information_change(
            "rename", "title", old_version,
            "title changed; prior title superseded", prov,
        )

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

        INGESTION BOUNDARY (1.5.2): accepts a SEGMENTED IDEA UNIT —
        (name, value) where name is a unit identifier and value is a
        JSON-serializable payload. Raw/compound information must be
        segmented upstream; this boundary validates the unit contract
        and rejects non-units.

        Event-sourced: creates a NEW immutable version. The previous version
        is linked via `supersedes`; it is not mutated.

        Returns the new version_id.
        """
        self._validate_unit(name, value)
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
        consequence = (
            "ACTIVE established; prior version superseded"
            if supersedes_id
            else "ACTIVE established"
        )
        self._on_information_change(
            "set_property", name, new_version, consequence, prov,
            superseded_version_id=supersedes_id,
        )
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
        self._on_information_change(
            "fade_property", name, faded, "value faded; prior ACTIVE superseded",
            prov, superseded_version_id=current.version_id,
        )
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

        Note on Nursery relationship: Nursery.Proposal governs *idea-level*
        proposals (new ideas, idea evolution). This method governs
        *property-level* proposals (suggested values for existing properties).
        Different granularities; not a competing authority. If a property
        proposal is accepted, it becomes an ACTIVE version via accept_proposal.

        Returns the proposal version_id. The proposal is in PROPOSED state
        until accepted or rejected.

        INGESTION BOUNDARY (1.5.2): same segmented-unit contract as
        set_property — proposals are units awaiting acceptance.

        Returns the proposal version_id. The proposal is in PROPOSED state
        until accepted or rejected.
        """
        self._validate_unit(name, value)
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
        self._on_information_change(
            "propose_property", name, proposal, "proposal recorded", prov,
        )
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
        self._on_information_change(
            "accept_proposal", name, active_version,
            "proposal accepted; new ACTIVE established",
            accept_prov, superseded_version_id=supersedes_id,
        )
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
        self._on_information_change(
            "reject_proposal", name, rejected, "proposal rejected",
            rejected.provenance, superseded_version_id=proposal.version_id,
        )
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
        prev = self._idea_state
        self._idea_state_history.append((self._idea_state, time.time(), f"archive: {reason}"))
        self._idea_state = LifecycleState.ARCHIVED
        self._on_information_change(
            "archive", None, None,
            f"lifecycle {prev.value}->{LifecycleState.ARCHIVED.value}",
            Provenance(source=ProvenanceSource.HUMAN, activity="archive",
                       agent="idea", detail=reason),
        )

    def delete(self, reason: str = "") -> None:
        """Soft-delete the Idea. Marked, not destroyed. Recoverable."""
        prev = self._idea_state
        self._idea_state_history.append((self._idea_state, time.time(), f"delete: {reason}"))
        self._idea_state = LifecycleState.DELETED
        self._on_information_change(
            "delete", None, None,
            f"lifecycle {prev.value}->{LifecycleState.DELETED.value}",
            Provenance(source=ProvenanceSource.HUMAN, activity="delete",
                       agent="idea", detail=reason),
        )

    def restore(self, reason: str = "") -> None:
        """Restore from archived/deleted/faded. Restoration is history."""
        if self._idea_state not in (LifecycleState.ARCHIVED, LifecycleState.DELETED, LifecycleState.FADED):
            raise ValueError(f"Cannot restore from state {self._idea_state}")
        prev = self._idea_state
        self._idea_state_history.append((self._idea_state, time.time(), f"restore: {reason}"))
        self._idea_state = LifecycleState.RESTORED
        self._on_information_change(
            "restore", None, None,
            f"lifecycle {prev.value}->{LifecycleState.RESTORED.value}",
            Provenance(source=ProvenanceSource.HUMAN, activity="restore",
                       agent="idea", detail=reason),
        )

    @property
    def idea_state(self) -> LifecycleState:
        return self._idea_state

    # ------------------------------------------------------------------
    # Ingestion boundary (1.5.2 segmentation contract)
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_unit(name: str, value: Any) -> None:
        """Enforce the segmented-unit ingestion contract.

        The canonical Idea boundary consumes SEGMENTED IDEA UNITS, not raw
        information. A unit is (name, value) where:
          - name: non-empty string unit identifier (the segmentation key);
          - value: JSON-serializable payload (persistable as a version).

        Raw/compound information (unstructured text, unparsed payloads) must
        be segmented upstream before reaching this boundary. This validation
        proves the boundary exists: it accepts units and rejects non-units
        with an explicit contract error, rather than silently versioning
        whatever the caller supplied.
        """
        if not isinstance(name, str) or not name.strip():
            raise ValueError(
                "ingestion: property name must be a non-empty string unit "
                f"identifier; got {name!r}"
            )
        try:
            json.dumps(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"ingestion: property value for unit {name!r} must be "
                f"JSON-serializable; got {type(value).__name__}: {exc}"
            ) from exc

    # ------------------------------------------------------------------
    # Live Matrix processing (1.5)
    # ------------------------------------------------------------------

    def _on_information_change(
        self,
        operation: str,
        property_name: Optional[str],
        version: Optional[PropertyVersion],
        consequence: str,
        provenance: Provenance,
        superseded_version_id: Optional[str] = None,
    ) -> IdeaChangeEvent:
        """Live Matrix processing boundary (1.5.3).

        Every legitimate information/state mutation passes through here.
        Processing is driven by information arrival, never by Perspective,
        zoom, fractal navigation, rendering, or UI inspection.

        The boundary performs the SMALLEST REAL Phase-1 computation: it
        deterministically constructs an immutable IdeaChangeEvent that
        records the operation, the canonical version it affected, the
        semantic consequence, and provenance — and appends it to the
        Idea's processing record. The event references canonical version
        IDs; it does not duplicate PropertyVersion authority.

        This is the extension point Phase 2 (Fractal Semantic Graph) and
        Phase 3 (Resonance) will deepen. The Phase-1 core does real work:
        INFORMATION CHANGE → PROCESSING OCCURS → COMPUTATIONAL RESULT
        (the event) EXISTS → RESULT IS OBSERVABLE (change_events()).
        """
        event = IdeaChangeEvent(
            event_id=str(uuid.uuid4()),
            idea_id=self.id,
            operation=operation,
            property_name=property_name,
            version_id=version.version_id if version else None,
            superseded_version_id=superseded_version_id,
            consequence=consequence,
            timestamp=time.time(),
            provenance=provenance,
        )
        self._change_events.append(event)
        self.modified_at = event.timestamp
        return event

    # ------------------------------------------------------------------
    # Live Matrix observability (1.5.5)
    # ------------------------------------------------------------------

    def change_events(self) -> List[IdeaChangeEvent]:
        """All recorded information-change processing events (chronological).

        Each event is a real computation product of the processing boundary:
        it exists because information arrived/changed, never because a
        Perspective was opened or rendered. Events persist with the Idea
        (see to_dict/from_dict) and survive fresh-process load.
        """
        return list(self._change_events)

    def last_change(self) -> Optional[IdeaChangeEvent]:
        """The most recent processing event, or None if no mutation occurred."""
        return self._change_events[-1] if self._change_events else None

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
            # Live Matrix processing record (1.5): derived events, persisted
            # with the Idea. References canonical version IDs; the version
            # lists above remain the truth.
            "change_events": [e.to_dict() for e in self._change_events],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Idea":
        # MF-4 fix: structural validation. Unknown/corrupt state must not
        # become valid state (Phase-0 contract).
        if not isinstance(d, dict):
            raise ValueError("Idea data must be an object")
        if "id" not in d or "properties" not in d:
            raise ValueError("Idea data missing required fields")
        idea = cls(idea_id=d["id"], title=d.get("title", ""))
        idea.created_at = d.get("created_at", 0)
        idea.modified_at = d.get("modified_at", idea.created_at)
        idea._idea_state = LifecycleState(d.get("idea_state", "active"))
        idea._idea_state_history = [
            (LifecycleState(h["state"]), h["at"], h["reason"])
            for h in d.get("idea_state_history", [])
        ]
        seen_version_ids = set()
        for name, vlist in d.get("properties", {}).items():
            if not isinstance(vlist, list):
                raise ValueError(f"Property {name!r}: versions must be a list")
            versions = []
            for v in vlist:
                pv = PropertyVersion.from_dict(v)
                if pv.version_id in seen_version_ids:
                    raise ValueError(f"Duplicate version_id {pv.version_id}")
                seen_version_ids.add(pv.version_id)
                versions.append(pv)
            idea._properties[name] = versions
        idea._title_history = [PropertyVersion.from_dict(v)
                               for v in d.get("title_history", [])]
        # R4: restore the derived processing record. Events are validated
        # structurally; each must reference this idea.
        for e in d.get("change_events", []):
            ev = IdeaChangeEvent.from_dict(e)
            if ev.idea_id != idea.id:
                raise ValueError(
                    f"Change event {ev.event_id} references idea "
                    f"{ev.idea_id!r}, not {idea.id!r}"
                )
            idea._change_events.append(ev)
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
