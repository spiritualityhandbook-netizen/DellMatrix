"""GDP-001 Phase 2 — Canonical Semantic Graph authority.

ONE authority answers: WHAT IS THE CURRENT CANONICAL IDEA RELATIONSHIP?

Nodes are canonical Phase-1 Idea IDs (identity lives in the Idea; graph
position never defines identity). Edges are identified objects
(RelationshipEntry): typed, directed, with provenance and lifecycle.

Persisted form is an APPEND-ONLY relationship log per owner. Current graph
state is a deterministic fold over the log (latest entry per rel_id wins;
ACTIVE entries form the current graph). In-memory indexes are derived on
every load — never persisted, never trusted.

Containment (CONTAINS) is a type-level invariant on the single edge store:
at most one ACTIVE containment parent per child, no self-containment, no
cycles. It is NOT a generic association (Phase-2 law 2.3.2).

Relationship history is never destructively overwritten: state transitions
append new entries; REMOVED is a terminal tombstone entry.

Phase-2 laws honored: CONTAINMENT != ASSOCIATION; LINEAGE != CONTAINMENT;
SPATIAL NEARNESS != SEMANTIC RELATIONSHIP; RESONANCE != GRAPH TRUTH;
PERSPECTIVE != GRAPH TRUTH; explicit semantic type per edge; no
relationship from mere coexistence; no duplicate inverse authority;
no orphans; no dangling relationships; no containment cycles;
no silent identity change on reparenting; promotion changes containment,
not identity; navigation triggers no semantic computation; graph change
produces traceable processing evidence; propagation only on declared
dependencies.
"""

from __future__ import annotations

import json
import os
import time
import uuid
from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from form.mandell.idea import Idea, Provenance, ProvenanceSource
from form.mandell.idea_persist import idea_exists, load_idea, save_idea


# ---------------------------------------------------------------------------
# Vocabulary
# ---------------------------------------------------------------------------

class RelationshipType(str, Enum):
    """Closed edge-type vocabulary. Every edge has exactly one type.

    The five types are the smallest vocabulary that covers the required
    distinctions: CONTAINS (structural, with invariants) vs RELATED_TO
    (generic association) vs DEPENDS_ON (drives propagation) vs
    REFERENCES (directional citation, for evidence-based reference
    resolution 2.5.4 — distinct from symmetric association) vs
    DERIVED_FROM (derivation provenance, distinct from runtime
    dependency). Each earns its place by a distinct consumer or invariant.
    """

    CONTAINS = "contains"          # parent -> child containment (type-level invariants)
    RELATED_TO = "related_to"      # generic semantic association
    DEPENDS_ON = "depends_on"     # dependency: source depends on target's unit (drives propagation)
    REFERENCES = "references"     # source cites target (directional; 2.5.4 reference resolution)
    DERIVED_FROM = "derived_from" # source derived from target (derivation provenance)


class RelationshipStatus(str, Enum):
    ACTIVE = "active"
    SUPERSEDED = "superseded"     # replaced by a newer entry (reparent, etc.)
    REMOVED = "removed"           # terminal tombstone; history preserved


class DerivationKind(str, Enum):
    """Closed vocabulary of derived-value computations (1.5.4/2.5.5).

    MIRROR (property-unit sync) and CHILD_COUNT (direct containment
    measure) are the core kinds. DESCENDANT_COUNT is the recursive
    counterpart — "how big is this subtree" — completing the
    containment-measure family; trivial cost, justified by symmetry.
    """

    MIRROR = "mirror"                 # copy of (target, unit) value
    CHILD_COUNT = "child_count"       # active children of subject
    DESCENDANT_COUNT = "descendant_count"  # active descendants of subject


class GraphError(Exception):
    """Base for graph errors."""


class GraphInvariantError(GraphError):
    """A mutation was rejected by the pre-mutation invariant gate."""


class GraphValidationError(GraphError):
    """Persisted graph state failed whole-graph validation (fail closed)."""


class PropagationStatus(str, Enum):
    """Explicit propagation state (R1-1). A dependent is synchronized
    iff no PENDING/FAILED record exists for its derived property.
    FAILED is never confused with success; PENDING is never presented
    as complete."""

    PENDING = "pending"  # operation started, not yet confirmed on disk
    FAILED = "failed"    # operation failed; error recorded; needs reconcile


# ---------------------------------------------------------------------------
# DSC1_J01: canonical journal validator (single authority)
# ---------------------------------------------------------------------------
#
# Every graph-journal reader, writer, appender, remover, recovery path, and
# status query MUST use validate_journal(). There is no second validator.
#
# The validator enforces:
# - Required envelope fields (format_version, owner, operations).
# - Supported format version (exactly _JOURNAL_FORMAT_VERSION; no default).
# - Exact owner match (no foreign journals).
# - Operations is a list (no missing -> default []).
# - Recognized operation types only.
# - Required per-operation fields, types, and identifiers.
# - Operation-specific invariants for safe replay.
#
# Invalid, unreadable, foreign, or unsupported journals are explicit
# non-success. Their bytes are preserved; never overwritten, appended to,
# discarded, or deleted as successful recovery.

_JOURNAL_FORMAT_VERSION = 1

_JOURNAL_OP_TYPES = ("ensure_edge", "sync_dependent")

# Required fields per operation type. Each maps field name -> expected type
# (or tuple of types). Missing fields are errors, not defaults.
_JOURNAL_OP_SCHEMA = {
    "ensure_edge": {
        "op": str,
        "entry": dict,  # full RelationshipEntry dict; validated on replay
    },
    "sync_dependent": {
        "op": str,
        "dependent_id": str,
        "derived_property": str,
        "target_id": str,
        "edge_rel_id": str,
        # Optional: unit, derivation, subject_id (may be None)
    },
}


def validate_journal(data: Any, owner: str) -> dict:
    """Canonical journal validator (DSC1_J01 single authority).

    Returns the validated journal dict (not a copy; the caller's parsed JSON).
    Raises GraphValidationError on any invalid, unreadable, foreign, or
    unsupported journal. Never returns a default or partial result.
    """
    if not isinstance(data, dict):
        raise GraphValidationError(
            f"graph journal for {owner!r}: must be a JSON object, "
            f"got {type(data).__name__}")
    # Envelope: format_version (required, strict int type, exact value).
    # R1-F3: bool is a subclass of int in Python (True == 1), so an
    # explicit type check is required. Float, string, missing, and
    # unsupported versions are all rejected.
    version = data.get("format_version")
    if not isinstance(version, int) or isinstance(version, bool):
        raise GraphValidationError(
            f"graph journal for {owner!r}: format_version must be int, "
            f"got {type(version).__name__} ({version!r})")
    if version != _JOURNAL_FORMAT_VERSION:
        raise GraphValidationError(
            f"graph journal for {owner!r}: unsupported format_version "
            f"{version!r} (supported: {_JOURNAL_FORMAT_VERSION})")
    # Envelope: owner (required, exact match).
    jowner = data.get("owner")
    if jowner != owner:
        raise GraphValidationError(
            f"graph journal owner mismatch: journal owner {jowner!r} != "
            f"expected {owner!r}")
    # Envelope: operations (required, must be a list; missing is an error,
    # not an empty transaction).
    if "operations" not in data:
        raise GraphValidationError(
            f"graph journal for {owner!r}: missing required 'operations' field")
    operations = data["operations"]
    if not isinstance(operations, list):
        raise GraphValidationError(
            f"graph journal for {owner!r}: 'operations' must be a list, "
            f"got {type(operations).__name__}")
    # Per-operation validation.
    for idx, op in enumerate(operations):
        _validate_journal_op(op, owner, idx)
    return data


def _validate_raw_entry(entry: Any, owner: str, idx: int) -> None:
    """R2: strict raw-type schema for journal-embedded relationship entries.

    from_dict() coerces (str([])->"[]", int(True)->1, float("2")->2.0),
    but replay uses RAW fields: rel_id as a dict key (unhashable list
    crashes), seq for ordering. Validation must reject malformed raw
    types before coercion can hide them, before the idempotence skip,
    before reporting success, and before deleting evidence.

    Requires exact types (no bool-as-int, no str-as-int, no list-as-str).
    """
    if not isinstance(entry, dict):
        raise GraphValidationError(
            f"graph journal for {owner!r}: operation {idx} "
            f"(ensure_edge) entry must be a dict, "
            f"got {type(entry).__name__}")

    def _req_str(field: str, non_empty: bool = True) -> None:
        v = entry.get(field)
        # bool is not str, but be explicit; list/dict/int rejected.
        if not isinstance(v, str) or isinstance(v, bool):
            raise GraphValidationError(
                f"graph journal for {owner!r}: operation {idx} "
                f"(ensure_edge) entry field {field!r} must be str, "
                f"got {type(v).__name__}")
        if non_empty and not v:
            raise GraphValidationError(
                f"graph journal for {owner!r}: operation {idx} "
                f"(ensure_edge) entry field {field!r} must be non-empty")

    def _req_int(field: str) -> None:
        v = entry.get(field)
        # Reject bool (True == 1) and str ("2") — no coercion.
        if not isinstance(v, int) or isinstance(v, bool):
            raise GraphValidationError(
                f"graph journal for {owner!r}: operation {idx} "
                f"(ensure_edge) entry field {field!r} must be int, "
                f"got {type(v).__name__}")

    _req_str("rel_id")
    _req_str("type")
    _req_str("source_id")
    _req_str("target_id")
    _req_str("status")
    _req_str("cause", non_empty=False)
    _req_int("seq")

    # props must be a dict (replay may iterate it).
    if not isinstance(entry.get("props"), dict):
        raise GraphValidationError(
            f"graph journal for {owner!r}: operation {idx} "
            f"(ensure_edge) entry field 'props' must be dict, "
            f"got {type(entry.get('props')).__name__}")

    # recorded_at must be numeric (not bool, not str).
    ra = entry.get("recorded_at")
    if not isinstance(ra, (int, float)) or isinstance(ra, bool):
        raise GraphValidationError(
            f"graph journal for {owner!r}: operation {idx} "
            f"(ensure_edge) entry field 'recorded_at' must be numeric, "
            f"got {type(ra).__name__}")

    # provenance must be a dict (from_dict will validate its contents).
    if not isinstance(entry.get("provenance"), dict):
        raise GraphValidationError(
            f"graph journal for {owner!r}: operation {idx} "
            f"(ensure_edge) entry field 'provenance' must be dict, "
            f"got {type(entry.get('provenance')).__name__}")


def _validate_journal_op(op: Any, owner: str, idx: int) -> None:
    """Validate a single journal operation. Raises GraphValidationError."""
    if not isinstance(op, dict):
        raise GraphValidationError(
            f"graph journal for {owner!r}: operation {idx} must be a dict, "
            f"got {type(op).__name__}")
    op_type = op.get("op")
    if op_type not in _JOURNAL_OP_TYPES:
        raise GraphValidationError(
            f"graph journal for {owner!r}: operation {idx} has unknown "
            f"type {op_type!r} (supported: {_JOURNAL_OP_TYPES})")
    schema = _JOURNAL_OP_SCHEMA[op_type]
    for field, ftype in schema.items():
        if field not in op:
            raise GraphValidationError(
                f"graph journal for {owner!r}: operation {idx} ({op_type}) "
                f"missing required field {field!r}")
        if not isinstance(op[field], ftype):
            raise GraphValidationError(
                f"graph journal for {owner!r}: operation {idx} ({op_type}) "
                f"field {field!r} must be {ftype.__name__}, "
                f"got {type(op[field]).__name__}")
    # Operation-specific invariants for safe replay.
    # R2: strict raw-type schema for ensure_edge entries. from_dict()
    # coerces (str([]) -> "[]", int(True) -> 1), but replay uses RAW
    # fields (rel_id as dict key -> unhashable list crashes). Validation
    # and execution must agree: reject malformed raw types BEFORE
    # from_dict coercion can hide them.
    if op_type == "ensure_edge":
        _validate_raw_entry(op["entry"], owner, idx)
        try:
            RelationshipEntry.from_dict(op["entry"])
        except GraphValidationError as exc:
            raise GraphValidationError(
                f"graph journal for {owner!r}: operation {idx} "
                f"(ensure_edge) has malformed entry: {exc}"
            ) from exc
    elif op_type == "sync_dependent":
        # Identifiers must be non-empty (empty IDs cannot be replayed safely).
        for f in ("dependent_id", "derived_property", "target_id", "edge_rel_id"):
            if not op[f]:
                raise GraphValidationError(
                    f"graph journal for {owner!r}: operation {idx} "
                    f"(sync_dependent) field {f!r} must be non-empty")


# ---------------------------------------------------------------------------
# Records
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RelationshipEntry:
    """One immutable append-only log entry. A relationship's history is the
    chain of entries sharing its rel_id; the max-seq entry is current."""

    rel_id: str
    type: RelationshipType
    source_id: str
    target_id: str
    props: Tuple[Tuple[str, Any], ...]  # sorted tuple pairs (JSON-safe)
    status: RelationshipStatus
    seq: int
    recorded_at: float
    provenance: Provenance
    cause: str  # e.g. "nest", "reparent", "promote", "remove"

    def props_dict(self) -> Dict[str, Any]:
        return dict(self.props)

    def to_dict(self) -> dict:
        return {
            "rel_id": self.rel_id,
            "type": self.type.value,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "props": dict(self.props),
            "status": self.status.value,
            "seq": self.seq,
            "recorded_at": self.recorded_at,
            "provenance": self.provenance.to_dict(),
            "cause": self.cause,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "RelationshipEntry":
        try:
            props = d.get("props", {})
            if not isinstance(props, dict):
                raise GraphValidationError("relationship props must be an object")
            return cls(
                rel_id=str(d["rel_id"]),
                type=RelationshipType(d["type"]),
                source_id=str(d["source_id"]),
                target_id=str(d["target_id"]),
                props=tuple(sorted(props.items())),
                status=RelationshipStatus(d["status"]),
                seq=int(d["seq"]),
                recorded_at=float(d["recorded_at"]),
                provenance=Provenance.from_dict(d["provenance"]),
                cause=str(d.get("cause", "")),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise GraphValidationError(f"malformed relationship entry: {exc}") from exc


@dataclass(frozen=True)
class RootPath:
    """A recorded directed traversal over the canonical graph.

    Historical note: "RootPath" has no recoverable historical authority in
    the route/location/prerequisite/cost sense (see phase-2 archaeology).
    Implemented per the historically-supported RuPat notion (flow/direction
    of execution over structure): a RootPath is a directed walk — root
    (starting marker), ordered edge sequence, hop count as the
    computationally-meaningful cost. It is NOT the graph, NOT plane
    position, NOT execution flow. No invented prerequisites; no game
    statistics.
    """

    path_id: str
    root_id: str
    node_ids: Tuple[str, ...]   # ordered node walk, root first
    edge_ids: Tuple[str, ...]   # ordered edge traversal, len = len(node_ids) - 1
    hop_count: int              # = len(edge_ids); the only cost metric
    provenance: Provenance
    recorded_at: float

    def to_dict(self) -> dict:
        return {
            "path_id": self.path_id,
            "root_id": self.root_id,
            "node_ids": list(self.node_ids),
            "edge_ids": list(self.edge_ids),
            "hop_count": self.hop_count,
            "provenance": self.provenance.to_dict(),
            "recorded_at": self.recorded_at,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "RootPath":
        try:
            node_ids = tuple(str(x) for x in d["node_ids"])
            edge_ids = tuple(str(x) for x in d["edge_ids"])
            hop_count = int(d["hop_count"])
            if hop_count != len(edge_ids) or len(node_ids) != len(edge_ids) + 1:
                raise GraphValidationError("root path node/edge/hop count inconsistent")
            if not node_ids or node_ids[0] != str(d["root_id"]):
                raise GraphValidationError("root path must start at its root")
            return cls(
                path_id=str(d["path_id"]),
                root_id=str(d["root_id"]),
                node_ids=node_ids,
                edge_ids=edge_ids,
                hop_count=hop_count,
                provenance=Provenance.from_dict(d["provenance"]),
                recorded_at=float(d["recorded_at"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise GraphValidationError(f"malformed root path: {exc}") from exc


# ---------------------------------------------------------------------------
# Persistence helpers
# ---------------------------------------------------------------------------

_GRAPH_FORMAT_VERSION = 1


def _state_dir() -> str:
    from form.persist import _STATE_DIR
    return _STATE_DIR


# MICRO-GATE: no local sanitizer. Reuse the canonical form.persist._safe_owner
# (single authority for owner namespace mapping).
from form.persist import _safe_owner as _safe_owner


def graph_path(owner: str) -> str:
    return os.path.join(_state_dir(), f"graph_{_safe_owner(owner)}.json")


def graph_journal_path(owner: str) -> str:
    """Fail-closed recovery transaction journal (R1-2). Written before any
    multi-step graph+idea mutation; replayed on load if present (crash);
    deleted on clean completion. The journal's presence means 'transaction
    was interrupted' — never a success state."""
    return os.path.join(_state_dir(), f"graph_{_safe_owner(owner)}.journal.json")


# ---------------------------------------------------------------------------
# SemanticGraph
# ---------------------------------------------------------------------------

class SemanticGraph:
    """The ONE canonical semantic graph authority for an owner's Ideas.

    Usage: graph = SemanticGraph.load(owner) — reads the persisted log,
    validates it whole (fail closed), folds to current state, builds
    derived indexes. Mutations append to the log and save. No global
    registry; instances are session-scoped.
    """

    def __init__(self, owner: str):
        self.owner = owner
        self._entries: List[RelationshipEntry] = []  # the log (persisted)
        self._paths: List[RootPath] = []             # persisted paths
        # R1-1: propagation ledger (persisted). Maps (dependent_id,
        # derived_property) -> {status, error, timestamp, target_id}.
        # Absence of a record means synchronized (or never attempted).
        # PENDING/FAILED are never confused with success.
        self._propagation_ledger: Dict[Tuple[str, str], Dict[str, Any]] = {}
        self._next_seq = 0
        # Derived (rebuilt on load, never persisted):
        self._current: Dict[str, RelationshipEntry] = {}  # rel_id -> latest entry
        self._by_source: Dict[str, List[str]] = {}        # idea_id -> [rel_id] (active)
        self._by_target: Dict[str, List[str]] = {}        # idea_id -> [rel_id] (active)
        self._by_type: Dict[RelationshipType, List[str]] = {}
        self._active_parent: Dict[str, str] = {}           # child_id -> rel_id (CONTAINS)
        self._title_index: Dict[str, str] = {}            # title -> idea_id
        self._idea_titles: Dict[str, str] = {}            # idea_id -> title
        self._propagating: Set[Tuple[str, str]] = set()   # recursion guard
        self._journal_depth = 0  # nesting depth for journaled propagation
        self._replaying = False  # True during _replay_journal (suppress clear)

    # -- load / save ------------------------------------------------------

    @classmethod
    def load(cls, owner: str) -> "SemanticGraph":
        g = cls(owner)
        path = graph_path(owner)
        if os.path.isfile(path):
            try:
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
            except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
                raise GraphValidationError(
                    f"graph file unreadable for {owner!r}: {exc}"
                ) from exc
            g._load_data(data)
        g._fold()
        # R1-2: fail-closed recovery. If a journal exists, a multi-step
        # transaction was interrupted. Replay it deterministically BEFORE
        # validation exposes state. This converges to either completed
        # (edge + derived value both present) or explicitly FAILED.
        g._replay_journal()
        g._validate_whole()  # fail closed on any invalid persisted state
        SemanticGraph._rebuild_title_index(g)
        return g

    def _load_data(self, data: dict) -> None:
        if not isinstance(data, dict):
            raise GraphValidationError("graph file must be a JSON object")
        if data.get("format_version") != _GRAPH_FORMAT_VERSION:
            raise GraphValidationError(
                f"unsupported graph format version {data.get('format_version')!r}"
            )
        if data.get("owner") != self.owner:
            raise GraphValidationError("graph file owner mismatch")
        entries = data.get("relationships", [])
        if not isinstance(entries, list):
            raise GraphValidationError("graph relationships must be a list")
        seen_seq: Set[int] = set()
        for e in entries:
            entry = RelationshipEntry.from_dict(e)  # raises GraphValidationError
            if entry.seq in seen_seq:
                raise GraphValidationError(f"duplicate relationship seq {entry.seq}")
            seen_seq.add(entry.seq)
            self._entries.append(entry)
        paths = data.get("paths", [])
        if not isinstance(paths, list):
            raise GraphValidationError("graph paths must be a list")
        for p in paths:
            self._paths.append(RootPath.from_dict(p))
        # R1-1: propagation ledger (persisted explicit failure state).
        ledger = data.get("propagation_ledger", {})
        if not isinstance(ledger, dict):
            raise GraphValidationError("propagation_ledger must be a dict")
        for k, v in ledger.items():
            # A6: only "failed" is a valid persisted ledger status.
            # "pending" is derived from journal presence, never stored.
            if not isinstance(v, dict) or v.get("status") != "failed":
                raise GraphValidationError(f"malformed propagation ledger entry {k!r}")
            dep_id, _, prop = k.partition("|")
            self._propagation_ledger[(dep_id, prop)] = v
        if self._entries:
            self._next_seq = max(e.seq for e in self._entries) + 1

    @classmethod
    def _rebuild_title_index(cls, g: "SemanticGraph") -> None:
        # 2.5.1: title-level information is immediately available to
        # Phase-2 processing after load. Rebuild the title index from
        # the owner's ideas (in-memory only; the observer keeps it
        # fresh for attached ideas during the session).
        from form.mandell.idea_persist import list_idea_ids
        for iid in list_idea_ids(g.owner):
            try:
                idea = load_idea(iid, g.owner)
            except Exception:
                continue  # corrupt ideas fail on their own load path
            g._track_title(idea)

    def save(self) -> str:
        """Persist the log. Called after every mutation (no deferred writes)."""
        ledger = {}
        for (dep_id, prop), rec in self._propagation_ledger.items():
            ledger[f"{dep_id}|{prop}"] = rec
        data = {
            "format_version": _GRAPH_FORMAT_VERSION,
            "owner": self.owner,
            "relationships": [e.to_dict() for e in self._entries],
            "paths": [p.to_dict() for p in self._paths],
            "propagation_ledger": ledger,
        }
        from form.dell_matrix.atomic_write import atomic_write_json
        atomic_write_json(graph_path(self.owner), data)
        return graph_path(self.owner)

    # -- R1-2: fail-closed recovery journal ---------------------------------
    #
    # The journal is an explicitly persisted transaction record. It is
    # written BEFORE any multi-step graph+idea mutation begins, replayed
    # deterministically on load if present (crash/interruption), and deleted
    # on clean completion. Invariant: after every interrupted/failed
    # operation, either (a) both graph and derived effects are committed
    # (via replay), or (b) neither is (failure before any disk write), or
    # (c) the failure is explicitly recorded as FAILED in the ledger.

    def _write_journal(self, operations: List[Dict[str, Any]]) -> str:
        """Persist the transaction journal. Operations are idempotent:
        ensure_edge (append if rel_id absent) and sync_dependent (recompute).

        Nested calls APPEND to the existing journal (for multi-hop chains:
        the outer journal covers a→b, the inner covers b→c; both must
        survive for complete recovery).

        DSC1_J01: uses the canonical validate_journal(). If an existing
        journal cannot be parsed/validated, DO NOT overwrite it. Raise
        GraphValidationError (fail closed)."""
        from form.dell_matrix.atomic_write import atomic_write_json
        path = graph_journal_path(self.owner)
        existing_ops: List[Dict[str, Any]] = []
        if os.path.isfile(path):
            try:
                with open(path, encoding="utf-8") as f:
                    existing = json.load(f)
            except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
                raise GraphValidationError(
                    f"graph journal unreadable for {self.owner!r}: {exc}; "
                    f"refusing to overwrite unknown recovery state"
                ) from exc
            # DSC1_J01: canonical validation (single authority).
            validate_journal(existing, self.owner)
            existing_ops = existing["operations"]
        journal = {
            "format_version": _JOURNAL_FORMAT_VERSION,
            "owner": self.owner,
            "txn_id": str(uuid.uuid4()),
            "started_at": time.time(),
            "operations": existing_ops + operations,
        }
        # R1-F2: validate the ENTIRE assembled journal (existing + new)
        # before the atomic write. Invalid new operations must not be
        # persisted. On failure the existing journal is preserved (or no
        # new journal is created).
        validate_journal(journal, self.owner)
        atomic_write_json(path, journal)
        return path

    def _clear_journal(self) -> None:
        path = graph_journal_path(self.owner)
        if os.path.isfile(path):
            os.remove(path)

    def _replay_journal(self) -> None:
        """Deterministic forward recovery. Called on load before validation.
        Re-applies journaled operations idempotently, then clears the journal.
        Converges to committed state; never exposes a half-transaction.
        Operations that cannot be completed (e.g., dependent idea file
        permanently gone) are recorded as FAILED in the ledger — the load
        itself does not crash; the failure is explicit and queryable.

        DSC1_J01: uses the canonical validate_journal() (single authority).
        Invalid journals raise GraphValidationError; their bytes are preserved
        (never deleted as successful recovery)."""
        path = graph_journal_path(self.owner)
        if not os.path.isfile(path):
            return
        try:
            with open(path, encoding="utf-8") as f:
                journal = json.load(f)
        except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise GraphValidationError(
                f"graph journal unreadable for {self.owner!r}: {exc}"
            ) from exc
        # DSC1_J01: canonical validation. Rejects: non-dict, wrong version,
        # foreign owner, missing/non-list operations, unknown op types,
        # missing/invalid op fields. Bytes preserved on failure.
        validate_journal(journal, self.owner)
        operations = journal["operations"]
        self._replaying = True
        try:
            for op in operations:
                try:
                    if op["op"] == "ensure_edge":
                        rel_id = op["entry"]["rel_id"]
                        if rel_id not in self._current:
                            entry = RelationshipEntry.from_dict(op["entry"])
                            # A14: enforce seq uniqueness on the replay path.
                            if any(e.seq == entry.seq for e in self._entries):
                                raise GraphValidationError(
                                    f"journal replay: duplicate seq {entry.seq}")
                            self._entries.append(entry)
                            self._next_seq = max(self._next_seq, entry.seq + 1)
                            # A11: fold immediately so the following
                            # sync_dependent sees the edge in _current.
                            self._fold()
                    elif op["op"] == "sync_dependent":
                        self._sync_dependent_by_ids(
                            op["dependent_id"], op["derived_property"],
                            op["target_id"], op.get("unit"), op.get("derivation"),
                            op.get("subject_id"), op.get("edge_rel_id"))
                        # NULL-1: successful replay clears any stale FAILED.
                        ledger_key = (op["dependent_id"], op["derived_property"])
                        if ledger_key in self._propagation_ledger:
                            del self._propagation_ledger[ledger_key]
                except GraphValidationError:
                    raise
                except Exception as exc:
                    dep_id = op.get("dependent_id", "?")
                    prop = op.get("derived_property", "?")
                    self._propagation_ledger[(dep_id, prop)] = {
                        "status": PropagationStatus.FAILED.value,
                        "error": f"journal_replay: {type(exc).__name__}: {exc}",
                        "timestamp": time.time(),
                        "target_id": op.get("target_id"),
                    }
        finally:
            self._replaying = False
        self._fold()
        self.save()
        self._clear_journal()

    def _sync_dependent_by_ids(self, dependent_id: str, derived_property: str,
                                target_id: str, unit: Optional[str],
                                derivation: Optional[str],
                                subject_id: Optional[str],
                                edge_rel_id: Optional[str]) -> None:
        """Idempotent dependent sync for journal replay. Finds the edge by
        rel_id and recomputes; skips gracefully if the edge is gone."""
        edge = self._current.get(edge_rel_id) if edge_rel_id else None
        if edge is None or edge.status != RelationshipStatus.ACTIVE:
            return
        self._recompute_dependent(edge)

    # -- fold + derived indexes --------------------------------------------

    def _fold(self) -> None:
        """Deterministic fold: latest entry per rel_id wins; ACTIVE entries
        form the current graph. Rebuilds all derived indexes."""
        self._current = {}
        for e in self._entries:
            prev = self._current.get(e.rel_id)
            if prev is None or e.seq > prev.seq:
                self._current[e.rel_id] = e
        self._by_source = {}
        self._by_target = {}
        self._by_type = {}
        self._active_parent = {}
        for rel_id, e in self._current.items():
            if e.status != RelationshipStatus.ACTIVE:
                continue
            self._by_source.setdefault(e.source_id, []).append(rel_id)
            self._by_target.setdefault(e.target_id, []).append(rel_id)
            self._by_type.setdefault(e.type, []).append(rel_id)
            if e.type == RelationshipType.CONTAINS:
                # Invariant enforced at mutation; fold keeps first (deterministic).
                self._active_parent.setdefault(e.target_id, rel_id)

    # -- whole-graph validation (load path; never skips) --------------------

    def _validate_whole(self) -> None:
        """Fail closed on any malformed persisted state. No restore-mode skip."""
        # MF-P2-1: endpoint + duplicate-parent checks run over _current
        # (the fold: latest entry per rel_id), NOT over derived dicts —
        # _active_parent is a dict, so a check that iterates it can never
        # observe duplicate keys (dead code). Counting over _entries would
        # false-positive on superseded history; the fold is the truth.
        #
        # Historical (superseded/removed) entries are records of the past;
        # their endpoints may legitimately be gone (out-of-band idea
        # deletion). Only ACTIVE edges must be dangle-free.
        active_contains_per_child: Dict[str, int] = {}
        for e in self._current.values():
            if e.status != RelationshipStatus.ACTIVE:
                continue
            if not idea_exists(e.source_id, self.owner):
                raise GraphValidationError(
                    f"dangling relationship {e.rel_id}: source {e.source_id} has no idea"
                )
            if not idea_exists(e.target_id, self.owner):
                raise GraphValidationError(
                    f"dangling relationship {e.rel_id}: target {e.target_id} has no idea"
                )
            if e.type == RelationshipType.CONTAINS:
                active_contains_per_child[e.target_id] = \
                    active_contains_per_child.get(e.target_id, 0) + 1
        for child_id, n in active_contains_per_child.items():
            if n > 1:
                raise GraphValidationError(
                    f"two active containment parents for {child_id}"
                )
        # Containment invariants on the CURRENT fold:
        for child_id, rel_id in self._active_parent.items():
            e = self._current[rel_id]
            if e.source_id == child_id:
                raise GraphValidationError(f"self-containment for {child_id}")
        # Cycle check over active CONTAINS edges: O(V * depth), small scale.
        for child_id in self._active_parent:
            seen: Set[str] = set()
            node = child_id
            while node in self._active_parent:
                if node in seen:
                    raise GraphValidationError(
                        f"containment cycle involving {child_id}"
                    )
                seen.add(node)
                node = self._current[self._active_parent[node]].source_id

    # -- internal append -----------------------------------------------------

    def _append(self, entry: RelationshipEntry,
                after: Optional[Callable[[], None]] = None) -> RelationshipEntry:
        """Append + fold. If `after` (propagation) is given, it runs BEFORE
        the save; on failure the in-memory append is rolled back and the
        exception re-raised — disk never sees the edge (SF-P2-4)."""
        return self._append_many([entry], after)[0]

    def _append_many(self, entries: List[RelationshipEntry],
                     after: Optional[Callable[[], None]] = None
                     ) -> List[RelationshipEntry]:
        """Atomic multi-append: stage all entries, fold, run after()
        (propagation), then save ONCE. On failure, roll back all staged
        entries and re-raise — the graph is unchanged on disk and memory."""
        n = len(entries)
        self._entries.extend(entries)
        for e in entries:
            self._next_seq = max(self._next_seq, e.seq + 1)
        self._fold()
        try:
            if after is not None:
                after()
        except Exception:
            # Propagation never appends graph entries, so ours are last.
            del self._entries[-n:]
            self._fold()
            raise
        self.save()
        # Success: clear any journal written by after() (e.g.,
        # _propagate_structure). The journal is for crash recovery;
        # on clean success it must not remain.
        if self._journal_depth == 0:
            self._clear_journal()
        return entries

    def _new_entry(self, type: RelationshipType, source_id: str, target_id: str,
                   props: Dict[str, Any], status: RelationshipStatus,
                   provenance: Provenance, cause: str,
                   rel_id: Optional[str] = None) -> RelationshipEntry:
        # A-P2-4: fail fast on non-JSON-serializable props, BEFORE the
        # entry is staged — a save-time serialization failure would leave
        # memory and disk diverged.
        try:
            json.dumps(props)
        except (TypeError, ValueError) as exc:
            raise GraphInvariantError(
                f"relationship props must be JSON-serializable: {exc}") from exc
        # Allocate-and-increment: every entry gets a unique monotonic seq,
        # even when several are staged together via _append_many (reparent).
        seq = self._next_seq
        self._next_seq += 1
        return RelationshipEntry(
            rel_id=rel_id or str(uuid.uuid4()),
            type=type,
            source_id=source_id,
            target_id=target_id,
            props=tuple(sorted(props.items())),
            status=status,
            seq=seq,
            recorded_at=time.time(),
            provenance=provenance,
            cause=cause,
        )

    # -- pre-mutation invariant gate -----------------------------------------

    def _gate_endpoints(self, source_id: str, target_id: str) -> None:
        if not idea_exists(source_id, self.owner):
            raise GraphInvariantError(
                f"relationship source {source_id} is not an existing idea"
            )
        if not idea_exists(target_id, self.owner):
            raise GraphInvariantError(
                f"relationship target {target_id} is not an existing idea"
            )

    def _gate_containment(self, parent_id: str, child_id: str) -> None:
        """Pure containment gate: raises on self-containment and on genuine
        cycles. Idempotency is handled by the caller (nest/reparent).

        Cycle logic: adding parent_id -> child_id creates a cycle iff
        child_id is reachable from parent_id by following parent pointers
        (i.e. child_id is parent_id itself or one of its ancestors) —
        because the new edge would close the loop back down to child_id.
        """
        if parent_id == child_id:
            raise GraphInvariantError("an idea cannot contain itself")
        # O(depth) walk from the prospective parent upward: if we reach
        # the child, the new edge would close a cycle.
        node = parent_id
        while node in self._active_parent:
            node = self._current[self._active_parent[node]].source_id
            if node == child_id:
                raise GraphInvariantError(
                    f"containment cycle: {child_id} is an ancestor of {parent_id}"
                )

    # -- relationship mutations ----------------------------------------------

    def add_relationship(self, type: RelationshipType, source_id: str,
                         target_id: str, provenance: Provenance,
                         props: Optional[Dict[str, Any]] = None,
                         cause: str = "relate",
                         after: Optional[Callable[[RelationshipEntry], None]] = None
                         ) -> RelationshipEntry:
        """Add a typed association. Containment goes through nest().

        `after`, if given, runs atomically after the fold but before the
        save (a failure rolls the entry back); it receives the new entry.
        """
        if type == RelationshipType.CONTAINS:
            raise GraphInvariantError("use nest()/reparent()/unnest() for containment")
        if not isinstance(type, RelationshipType):
            raise GraphInvariantError(f"illegal relationship type {type!r}")
        self._gate_endpoints(source_id, target_id)
        props = props or {}
        if type == RelationshipType.DEPENDS_ON:
            self._gate_dependency_props(source_id, target_id, props)
        entry = self._new_entry(type, source_id, target_id, props,
                                RelationshipStatus.ACTIVE, provenance, cause)
        def _run() -> None:
            if after is not None:
                after(entry)
        return self._append(entry, after=_run)

    def _gate_dependency_props(self, source_id: str, target_id: str,
                               props: Dict[str, Any]) -> None:
        try:
            derivation = DerivationKind(props["derivation"])
        except (KeyError, ValueError) as exc:
            raise GraphInvariantError(
                f"DEPENDS_ON requires a legal derivation kind: {exc}"
            ) from exc
        if "derived_property" not in props or not props["derived_property"]:
            raise GraphInvariantError("DEPENDS_ON requires derived_property")
        if derivation == DerivationKind.MIRROR and "unit" not in props:
            raise GraphInvariantError("mirror derivation requires unit")
        # A-P2-2: subject_id must reference a real idea.
        if props.get("subject_id") and not idea_exists(props["subject_id"], self.owner):
            raise GraphInvariantError(
                f"DEPENDS_ON subject_id {props['subject_id']} has no idea")
        # Duplicate DEPENDS_ON on the same (source, target, unit/derivation)
        # is semantically invalid (would double-propagate): reject.
        for rel_id in self._by_source.get(source_id, []):
            e = self._current[rel_id]
            if (e.type == RelationshipType.DEPENDS_ON
                    and e.status == RelationshipStatus.ACTIVE
                    and e.target_id == target_id
                    and e.props_dict().get("derivation") == derivation.value
                    and e.props_dict().get("unit") == props.get("unit")):
                raise GraphInvariantError(
                    f"duplicate active DEPENDS_ON {source_id}->{target_id} "
                    f"({derivation.value}/{props.get('unit')})"
                )

    def remove_relationship(self, rel_id: str, provenance: Provenance,
                            cause: str = "remove") -> RelationshipEntry:
        """Terminal removal: appends a REMOVED tombstone. History preserved."""
        current = self._current.get(rel_id)
        if current is None:
            raise GraphInvariantError(f"unknown relationship {rel_id}")
        if current.status != RelationshipStatus.ACTIVE:
            raise GraphInvariantError(
                f"relationship {rel_id} is not active (status={current.status.value})"
            )
        tombstone = self._new_entry(
            current.type, current.source_id, current.target_id,
            current.props_dict(), RelationshipStatus.REMOVED,
            provenance, cause, rel_id=rel_id,
        )
        entry = self._append(
            tombstone,
            after=lambda: (self._propagate_structure(current.source_id),
                           self._propagate_structure(current.target_id)),
        )
        # PRISM-2: a removed DEPENDS_ON edge must not leave an orphan FAILED
        # ledger record (unrecoverable, confusing). Clear it.
        if current.type == RelationshipType.DEPENDS_ON:
            derived = current.props_dict().get("derived_property")
            self._propagation_ledger.pop((current.source_id, derived), None)
            self.save()
        return entry

    # -- containment ----------------------------------------------------------

    def nest(self, child_id: str, parent_id: str,
             provenance: Provenance) -> RelationshipEntry:
        """Make child_id contained by parent_id. Idempotent for duplicates
        (same parent). Rejects when the child already has a DIFFERENT
        active parent — use reparent() to move it (explicit, not silent)."""
        self._gate_endpoints(parent_id, child_id)
        existing_rel_id = self._active_parent.get(child_id)
        if existing_rel_id is not None:
            existing = self._current[existing_rel_id]
            if existing.source_id == parent_id:
                return existing  # idempotent no-op
            raise GraphInvariantError(
                f"{child_id} already has an active parent; "
                f"use reparent() to move it")
        self._gate_containment(parent_id, child_id)
        entry = self._new_entry(
            RelationshipType.CONTAINS, parent_id, child_id, {},
            RelationshipStatus.ACTIVE, provenance, "nest",
        )
        result = self._append(
            entry,
            after=lambda: (self._propagate_structure(parent_id),
                           self._propagate_structure(child_id)),
        )
        return result

    def unnest(self, child_id: str, provenance: Provenance) -> RelationshipEntry:
        """Promote to top-level: supersede the active CONTAINS edge, no new
        edge. Former-parent history preserved in the log. Identity untouched."""
        rel_id = self._active_parent.get(child_id)
        if rel_id is None:
            raise GraphInvariantError(f"{child_id} has no active parent to unnest from")
        current = self._current[rel_id]
        superseded = self._new_entry(
            RelationshipType.CONTAINS, current.source_id, child_id, {},
            RelationshipStatus.SUPERSEDED, provenance, "promote", rel_id=rel_id,
        )
        result = self._append(
            superseded,
            after=lambda: (self._propagate_structure(current.source_id),
                           self._propagate_structure(child_id)),
        )
        return result

    def reparent(self, child_id: str, new_parent_id: str,
                 provenance: Provenance) -> RelationshipEntry:
        """Atomic reparent: supersede old CONTAINS and activate new CONTAINS
        in a single atomic append (one save). Never yields two active
        containment parents; a propagation failure rolls back both entries."""
        self._gate_endpoints(new_parent_id, child_id)
        self._gate_containment(new_parent_id, child_id)  # raises on cycle/self
        old_rel_id = self._active_parent.get(child_id)
        old_parent_id: Optional[str] = None
        staged: List[RelationshipEntry] = []
        if old_rel_id is not None:
            old = self._current[old_rel_id]
            old_parent_id = old.source_id
            if old_parent_id == new_parent_id:
                return old  # idempotent: already parented here
            staged.append(self._new_entry(
                RelationshipType.CONTAINS, old_parent_id, child_id, {},
                RelationshipStatus.SUPERSEDED, provenance, "reparent",
                rel_id=old_rel_id,
            ))
        new_entry = self._new_entry(
            RelationshipType.CONTAINS, new_parent_id, child_id, {},
            RelationshipStatus.ACTIVE, provenance, "reparent",
        )
        staged.append(new_entry)

        def _prop() -> None:
            if old_parent_id is not None:
                self._propagate_structure(old_parent_id)
            self._propagate_structure(new_parent_id)
            self._propagate_structure(child_id)

        # Atomic: both entries staged, propagation runs, then ONE save.
        result = self._append_many(staged, after=_prop)[-1]
        return result

    # -- navigation (derived; triggers no semantic computation) ----------------
    #
    # LIFECYCLE/GRAPH COMPOSITION RULE (explicit, per directive):
    # Graph edges are historical relationship facts. Idea lifecycle
    # transitions (archive/delete/fade/restore) do NOT create, modify, or
    # remove graph edges — history is never silently erased, and a
    # deleted idea's former containment remains queryable as history.
    # Structural navigation below answers the graph question purely.
    # Consumers needing "live" views compose with Idea lifecycle state
    # themselves; live_children() is the provided convenience.

    def parent(self, child_id: str) -> Optional[str]:
        rel_id = self._active_parent.get(child_id)
        return self._current[rel_id].source_id if rel_id else None

    def children(self, parent_id: str) -> List[str]:
        return [self._current[r].target_id
                for r in self._by_source.get(parent_id, [])
                if self._current[r].type == RelationshipType.CONTAINS]

    def live_children(self, parent_id: str) -> List[str]:
        """Children whose Idea lifecycle state is ACTIVE. Structural
        children() plus lifecycle composition, explicitly."""
        from form.mandell.idea import LifecycleState
        out = []
        for cid in self.children(parent_id):
            try:
                idea = load_idea(cid, self.owner)
            except Exception:
                continue
            if idea.idea_state == LifecycleState.ACTIVE:
                out.append(cid)
        return out

    def ancestors(self, child_id: str) -> List[str]:
        out, node = [], child_id
        seen: Set[str] = {child_id}
        while node in self._active_parent:
            node = self._current[self._active_parent[node]].source_id
            if node in seen:
                # Unreachable if mutation gates + load validation hold;
                # fail closed rather than loop forever.
                raise GraphValidationError(
                    f"containment cycle detected during ancestors({child_id})")
            seen.add(node)
            out.append(node)
        return out

    def descendants(self, parent_id: str) -> List[str]:
        out: List[str] = []
        seen: Set[str] = {parent_id}
        stack = self.children(parent_id)
        while stack:
            node = stack.pop()
            if node in seen:
                raise GraphValidationError(
                    f"containment cycle detected during descendants({parent_id})")
            seen.add(node)
            out.append(node)
            stack.extend(self.children(node))
        return out

    def breadcrumb(self, child_id: str) -> List[str]:
        """Root-first path of idea IDs from the top-level ancestor to child."""
        return list(reversed(self.ancestors(child_id))) + [child_id]

    def is_top_level(self, idea_id: str) -> bool:
        return idea_id not in self._active_parent

    def roots(self) -> List[str]:
        """All top-level ideas: every known idea with no active containment
        parent. Consistent with is_top_level()."""
        from form.mandell.idea_persist import list_idea_ids
        contained = set(self._active_parent)
        return sorted(iid for iid in list_idea_ids(self.owner)
                      if iid not in contained)

    # -- queries -----------------------------------------------------------------

    def outgoing(self, idea_id: str,
                 type: Optional[RelationshipType] = None) -> List[RelationshipEntry]:
        return [self._current[r] for r in self._by_source.get(idea_id, [])
                if type is None or self._current[r].type == type]

    def incoming(self, idea_id: str,
                 type: Optional[RelationshipType] = None) -> List[RelationshipEntry]:
        return [self._current[r] for r in self._by_target.get(idea_id, [])
                if type is None or self._current[r].type == type]

    def by_type(self, type: RelationshipType) -> List[RelationshipEntry]:
        return [self._current[r] for r in self._by_type.get(type, [])]

    def association_neighbors(self, idea_id: str) -> List[Tuple[str, RelationshipType]]:
        """Semantic neighbors via association edges (excludes containment)."""
        out = []
        for r in self._by_source.get(idea_id, []):
            e = self._current[r]
            if e.type != RelationshipType.CONTAINS:
                out.append((e.target_id, e.type))
        for r in self._by_target.get(idea_id, []):
            e = self._current[r]
            if e.type != RelationshipType.CONTAINS:
                out.append((e.source_id, e.type))
        return out

    def edge_history(self, rel_id: str) -> List[RelationshipEntry]:
        return sorted((e for e in self._entries if e.rel_id == rel_id),
                      key=lambda e: e.seq)

    # -- RootPath ------------------------------------------------------------------

    def find_path(self, source_id: str, target_id: str,
                  types: Optional[Set[RelationshipType]] = None) -> RootPath:
        """Breadth-first directed traversal over ACTIVE edges. Hop count is
        the computationally-meaningful cost. Raises GraphError if unreachable."""
        self._gate_endpoints(source_id, target_id)
        allowed = types or set(RelationshipType)
        # BFS over active edges.
        prev: Dict[str, Tuple[str, str]] = {}  # node -> (prev_node, rel_id)
        queue = [source_id]
        prev[source_id] = ("", "")
        found = source_id == target_id
        while queue and not found:
            node = queue.pop(0)
            for r in self._by_source.get(node, []):
                e = self._current[r]
                if e.type not in allowed or e.target_id in prev:
                    continue
                prev[e.target_id] = (node, r)
                if e.target_id == target_id:
                    found = True
                    break
                queue.append(e.target_id)
        if target_id not in prev or not found and source_id != target_id:
            raise GraphError(f"no path from {source_id} to {target_id}")
        # Reconstruct.
        node_ids = [target_id]
        edge_ids = []
        node = target_id
        while node != source_id:
            p, r = prev[node]
            edge_ids.append(r)
            node_ids.append(p)
            node = p
        node_ids.reverse()
        edge_ids.reverse()
        return RootPath(
            path_id=str(uuid.uuid4()),
            root_id=source_id,
            node_ids=tuple(node_ids),
            edge_ids=tuple(edge_ids),
            hop_count=len(edge_ids),
            provenance=Provenance(
                source=ProvenanceSource.SYSTEM,
                activity="path_computed",
                agent="semantic_graph",
                detail=f"BFS over {[t.value for t in allowed]}",
            ),
            recorded_at=time.time(),
        )

    def save_path(self, path: RootPath) -> RootPath:
        """Persist a named, provenance-bearing route record.

        Justification (vs computed-only): 2.4.2 requires representing
        "route requirements" — a requirement is a persistent artifact,
        not a transient computation. Persisted paths are named, carry
        provenance, and participate coherently in checkpoint/rollback
        (they're in the graph file). The STALE mechanism (validate_path)
        honestly handles graph change instead of hiding it.
        """
        self._paths.append(path)
        self.save()
        return path

    def get_path(self, path_id: str) -> RootPath:
        for p in self._paths:
            if p.path_id == path_id:
                return p
        raise GraphError(f"unknown path {path_id}")

    def validate_path(self, path_id: str) -> str:
        """Re-validate a persisted path against current graph truth.
        Returns "ACTIVE" or "STALE:<reason>". Never silently follows a
        path whose edges changed."""
        path = self.get_path(path_id)
        if list(path.node_ids) and path.node_ids[0] != path.root_id:
            return "STALE:root_mismatch"
        for i, rel_id in enumerate(path.edge_ids):
            current = self._current.get(rel_id)
            if current is None or current.status != RelationshipStatus.ACTIVE:
                return f"STALE:edge_{i}_{rel_id[:8]}_not_active"
            if not (current.source_id == path.node_ids[i]
                    and current.target_id == path.node_ids[i + 1]):
                return f"STALE:edge_{i}_endpoints_changed"
        return "ACTIVE"

    # -- 2.5 semantic processing -----------------------------------------------------

    def attach(self, idea: Idea) -> None:
        """Subscribe this graph to an Idea's change events (session-scoped,
        in-memory only). Title index updates and dependency propagation
        then happen immediately on mutation (2.5.1/2.5.2)."""
        idea.add_change_listener(self._on_idea_event)
        self._track_title(idea)

    def _track_title(self, idea: Idea) -> None:
        old = self._idea_titles.get(idea.id)
        if old is not None and self._title_index.get(old) == idea.id:
            del self._title_index[old]
        self._idea_titles[idea.id] = idea.title
        self._title_index[idea.title] = idea.id

    def _on_idea_event(self, idea: Idea, event) -> None:  # event: IdeaChangeEvent
        # Title index stays current.
        self._track_title(idea)
        # Dependency propagation on property-affecting operations.
        # The live idea is threaded through: the observer fires BEFORE
        # the caller necessarily saved, so propagation must read the
        # in-memory value, not the possibly-stale file.
        #
        # SF-P2-3: ANY operation that can change the ACTIVE value of a
        # property must trigger propagation — not just set_property.
        # fade_property removes it from active; accept_proposal promotes
        # a proposal to active; reject_proposal can restore a previous
        # active. The equality cutoff in _recompute_dependent makes
        # no-op triggers cheap (no write, no event).
        if event.property_name and event.operation in (
                "set_property", "fade_property",
                "propose_property", "accept_proposal", "reject_proposal"):
            # R1-1: propagation failure must NEVER be silent. The Phase-1
            # listener dispatch catches all exceptions (a listener must not
            # break the mutation), so this handler converts failures into
            # explicit persisted FAILED ledger records — queryable via
            # get_propagation_failures(), recoverable via reconcile().
            # No swallowed exception, no fake success receipt.
            #
            # MICRO-GATE: GraphValidationError (integrity failure: corrupt
            # journal, unknown recovery state) is NOT converted to FAILED.
            # It propagates — the graph is in an unknown state and the
            # operation must fail closed, not pretend a routine propagation
            # failure occurred.
            try:
                self._propagate_property(idea.id, event.property_name,
                                         live_idea=idea)
            except GraphValidationError:
                raise
            except Exception as exc:
                self._record_propagation_failure(
                    idea.id, event.property_name,
                    f"{type(exc).__name__}: {exc}")

    @staticmethod
    def categorize_value(value: Any) -> str:
        """Structural categorization only (2.5.3). No NLP is claimed or used."""
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "boolean"
        if isinstance(value, (int, float)):
            return "number"
        if isinstance(value, str):
            return "text"
        if isinstance(value, list):
            return "list"
        if isinstance(value, dict):
            return "object"
        return "unknown"

    def unit_categories(self, idea_id: str) -> Dict[str, str]:
        idea = load_idea(idea_id, self.owner)
        return {name: self.categorize_value(value)
                for name, value in idea.get_active_properties().items()}

    def resolve_references(self, idea_id: str) -> List[Tuple[RelationshipEntry, Any]]:
        """Follow REFERENCES edges. Returns (edge, Idea) or (edge, "UNKNOWN")
        where resolution is unsupported (2.5.4). UNKNOWN stays UNKNOWN."""
        out = []
        for e in self.outgoing(idea_id, RelationshipType.REFERENCES):
            try:
                target = load_idea(e.target_id, self.owner)
            except Exception:
                target = "UNKNOWN"
            out.append((e, target))
        return out

    def lookup_by_title(self, title: str) -> Optional[str]:
        return self._title_index.get(title)

    # -- dependency declaration + propagation (1.5.4 / 2.5.5) -------------------------

    def declare_dependency(self, dependent_id: str, target_id: str,
                           derivation: DerivationKind, derived_property: str,
                           unit: Optional[str] = None,
                           subject_id: Optional[str] = None,
                           provenance: Optional[Provenance] = None,
                           force: bool = False) -> RelationshipEntry:
        """Declare that dependent's `derived_property` is computed from
        target (mirror: target's `unit`; counts: subject's containment).

        R1-2 disk atomicity: uses a fail-closed journal with graph-first
        ordering.
        - Journal written before any mutation.
        - Graph edge saved FIRST. If this fails: NEITHER committed
          (idea untouched; journal deleted; in-memory rolled back).
        - Dependent idea saved SECOND. If this fails: edge is committed;
          FAILED is recorded explicitly in the propagation ledger (never
          silent); the exception propagates to the caller.
        - On clean success: journal deleted; edge + derived value both
          committed.
        - On crash/interruption: journal replay on next load completes
          deterministically (idempotent ensure_edge + sync_dependent).

        SF-P2-2: refuses to silently overwrite existing user data unless
        force=True.

        Session contract: propagation fires for mutations through attached
        Idea instances; call reconcile() for out-of-session mutations.
        """
        from form.mandell.idea import LifecycleState
        if not force:
            dep_idea = load_idea(dependent_id, self.owner)
            hist = dep_idea.get_property_history(derived_property)
            if hist:
                latest = hist[-1]
                if (latest.state == LifecycleState.ACTIVE
                        and latest.provenance.activity != "dependency_propagation"):
                    raise GraphInvariantError(
                        f"declare_dependency refuses to overwrite existing "
                        f"property '{derived_property}' on {dependent_id} "
                        f"(activity={latest.provenance.activity}); "
                        f"use force=True to take it over as derived")

        props: Dict[str, Any] = {
            "derivation": derivation.value,
            "derived_property": derived_property,
        }
        if unit is not None:
            props["unit"] = unit
        if subject_id is not None:
            if not idea_exists(subject_id, self.owner):
                raise GraphInvariantError(
                    f"DEPENDS_ON subject_id {subject_id} has no idea")
            props["subject_id"] = subject_id
        provenance = provenance or Provenance(
            source=ProvenanceSource.SYSTEM, activity="dependency_declared",
            agent="semantic_graph")

        # Gate endpoints and duplicate before journaling.
        self._gate_endpoints(dependent_id, target_id)
        self._gate_dependency_props(dependent_id, target_id, props)

        # Create the entry (validates JSON-serializability; allocates seq).
        entry = self._new_entry(
            RelationshipType.DEPENDS_ON, dependent_id, target_id, props,
            RelationshipStatus.ACTIVE, provenance, "declare_dependency")

        # R1-2: journal BEFORE any disk mutation.
        journal_ops = [
            {"op": "ensure_edge", "entry": entry.to_dict()},
            {"op": "sync_dependent",
             "dependent_id": dependent_id,
             "derived_property": derived_property,
             "target_id": target_id,
             "unit": unit,
             "derivation": derivation.value,
             "subject_id": subject_id,
             "edge_rel_id": entry.rel_id},
        ]
        self._write_journal(journal_ops)

        # Graph FIRST. If save fails: neither committed (idea untouched).
        self._entries.append(entry)
        self._fold()
        try:
            self.save()
        except Exception:
            self._entries.pop()
            self._fold()
            self._clear_journal()
            raise

        # Idea SECOND. If this fails: edge committed, FAILED recorded
        # explicitly (never silent); caller sees the exception.
        # (No PENDING marker: the journal is the in-flight record; the
        # ledger holds only explicit FAILED states.)
        ledger_key = (dependent_id, derived_property)
        try:
            self._recompute_dependent(entry)
        except Exception as exc:
            self._propagation_ledger[ledger_key] = {
                "status": PropagationStatus.FAILED.value,
                "error": f"{type(exc).__name__}: {exc}",
                "timestamp": time.time(),
                "target_id": target_id,
            }
            # A8: persist the FAILED state. If this save SUCCEEDS, the
            # failure is explicitly recorded → clear journal. If it FAILS,
            # the journal MUST remain for forward recovery on next load.
            # (The old `finally` cleared it unconditionally — wrong.)
            try:
                self.save()
            except Exception:
                # Journal remains; FAILED is in-memory only for this session.
                # Next load will replay the journal and re-attempt the sync.
                raise
            self._clear_journal()
            raise
        # Success: both committed; clear journal.
        self._clear_journal()
        return entry

    def reconcile(self, idea_id: str) -> int:
        """Recompute every derived value depending on idea_id's current
        persisted state. For mutations made outside this graph session
        (unattached instances), and for retrying FAILED propagations.
        Returns the number of dependents updated."""
        updated = 0
        for rel_id in list(self._by_target.get(idea_id, [])):
            e = self._current[rel_id]
            if e.type != RelationshipType.DEPENDS_ON:
                continue
            props = e.props_dict()
            derived_prop = props.get("derived_property")
            ledger_key = (e.source_id, derived_prop)
            # PRISM-4: the `before` snapshot load is inside the try so a
            # missing/corrupt dependent records FAILED instead of crashing
            # the recovery function.
            try:
                before = load_idea(e.source_id, self.owner).get_active_properties().get(
                    derived_prop)
                self._recompute_dependent(e)
            except Exception as exc:
                # Record FAILED; do not pretend success.
                self._propagation_ledger[ledger_key] = {
                    "status": PropagationStatus.FAILED.value,
                    "error": f"{type(exc).__name__}: {exc}",
                    "timestamp": time.time(),
                    "target_id": idea_id,
                }
                self.save()
                continue
            # Success: clear any FAILED record and remove journaled ops
            # for this dependent (they're now complete).
            if ledger_key in self._propagation_ledger:
                del self._propagation_ledger[ledger_key]
            self._remove_journal_ops(e.source_id, derived_prop)
            self.save()
            try:
                after = load_idea(e.source_id, self.owner).get_active_properties().get(
                    derived_prop)
            except Exception:
                after = None
            if before != after:
                updated += 1
        return updated

    def _remove_journal_ops(self, dependent_id: str, derived_property: str) -> None:
        """Remove completed sync_dependent ops from the journal.

        DSC1_J01: uses the canonical validate_journal(). Do NOT silently
        ignore corrupt/unreadable journal. If the journal cannot be
        parsed/validated, raise GraphValidationError (fail closed)."""
        jpath = graph_journal_path(self.owner)
        if not os.path.isfile(jpath):
            return
        try:
            with open(jpath, encoding="utf-8") as f:
                journal = json.load(f)
        except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise GraphValidationError(
                f"graph journal unreadable for {self.owner!r}: {exc}; "
                f"cannot remove completed ops from unknown state"
            ) from exc
        # DSC1_J01: canonical validation (single authority).
        validate_journal(journal, self.owner)
        ops = journal["operations"]
        filtered = [op for op in ops
                    if not (isinstance(op, dict)
                            and op.get("op") == "sync_dependent"
                            and op.get("dependent_id") == dependent_id
                            and op.get("derived_property") == derived_property)]
        if len(filtered) != len(ops):
            journal["operations"] = filtered
            from form.dell_matrix.atomic_write import atomic_write_json
            atomic_write_json(jpath, journal)
            if not filtered:
                self._clear_journal()

    def _record_propagation_failure(self, target_id: str, property_name: str,
                                    error: str) -> None:
        """R1-1: record an explicit FAILED propagation state. Called when
        the listener-path propagation throws.

        MICRO-GATE: a failure to persist FAILED state must not disappear.
        If self.save() throws, the journal (written by _propagate_property
        before the failure) REMAINS as the authoritative pending-recovery
        record — it is not cleared. If no journal exists (e.g., failure
        outside a journaled batch), raise GraphValidationError (fail closed)
        so the caller knows the FAILED state is in-memory only."""
        # Find affected dependents to record them individually.
        recorded = False
        for rel_id in list(self._by_target.get(target_id, [])):
            e = self._current.get(rel_id)
            if e is None or e.type != RelationshipType.DEPENDS_ON:
                continue
            props = e.props_dict()
            if props.get("derivation") != DerivationKind.MIRROR.value:
                continue
            if props.get("unit") != property_name:
                continue
            ledger_key = (e.source_id, props.get("derived_property"))
            self._propagation_ledger[ledger_key] = {
                "status": PropagationStatus.FAILED.value,
                "error": error,
                "timestamp": time.time(),
                "target_id": target_id,
            }
            recorded = True
        if not recorded:
            self._propagation_ledger[(target_id, property_name)] = {
                "status": PropagationStatus.FAILED.value,
                "error": error,
                "timestamp": time.time(),
                "target_id": target_id,
            }
        try:
            self.save()
        except Exception as exc:
            # FAILED is in-memory only. If a journal exists, it remains as
            # the authoritative pending-recovery record (not cleared).
            # If no journal exists, fail closed with a typed error — do not
            # let the FAILED state silently disappear.
            jpath = graph_journal_path(self.owner)
            if not os.path.isfile(jpath):
                raise GraphValidationError(
                    f"failed to persist propagation FAILED state for "
                    f"{self.owner!r}: {exc}; no journal exists for recovery"
                ) from exc
            # Journal exists: it covers recovery. FAILED remains in-memory
            # for this session; the journal ensures deterministic replay.

    def get_propagation_failures(self) -> List[Dict[str, Any]]:
        """All FAILED propagation records. Empty means no known failures
        (not proof of success — use propagation_status for a specific check)."""
        out = []
        for (dep_id, prop), rec in self._propagation_ledger.items():
            if rec.get("status") == PropagationStatus.FAILED.value:
                out.append({"dependent_id": dep_id, "derived_property": prop, **rec})
        return out

    def propagation_status(self, dependent_id: str,
                           derived_property: str) -> str:
        """Queryable propagation state. Returns 'synchronized', 'pending',
        'failed', or 'unknown'. NEVER returns 'synchronized' when a FAILED
        record exists, a journaled operation is in-flight, or the journal
        cannot be validated.

        DSC1_J01: uses the canonical validate_journal(). Invalid journals
        yield 'unknown' (explicit non-success), never 'synchronized'."""
        rec = self._propagation_ledger.get((dependent_id, derived_property))
        if rec is not None and rec.get("status") == PropagationStatus.FAILED.value:
            return "failed"
        # PENDING = a journaled operation exists for this dependent
        # (in-flight transaction, not yet confirmed).
        jpath = graph_journal_path(self.owner)
        if os.path.isfile(jpath):
            try:
                with open(jpath, encoding="utf-8") as f:
                    journal = json.load(f)
            except (OSError, json.JSONDecodeError, UnicodeDecodeError):
                return "unknown"
            # DSC1_J01: canonical validation. Any invalid journal -> "unknown".
            try:
                validate_journal(journal, self.owner)
            except GraphValidationError:
                return "unknown"
            for op in journal["operations"]:
                if (op.get("op") == "sync_dependent"
                        and op.get("dependent_id") == dependent_id
                        and op.get("derived_property") == derived_property):
                    return "pending"
        return "synchronized"

    def _propagate_property(self, idea_id: str, property_name: str,
                            live_idea: Optional[Idea] = None) -> None:
        """INFORMATION CHANGE → find declared affected dependencies →
        recompute only legitimately affected derived state → record →
        leave unrelated untouched.

        R1-2 (E): multi-dependent propagation uses a journal. If the 2nd
        of 3 dependents fails, the journal ensures deterministic recovery:
        on next load, the journal replays the remaining syncs. Partial
        progress is never presented as complete — FAILED ledger entries
        mark exactly which dependents did not converge.
        """
        # Collect affected edges first (deterministic order).
        affected = []
        for rel_id in list(self._by_target.get(idea_id, [])):
            e = self._current[rel_id]
            if e.type != RelationshipType.DEPENDS_ON:
                continue
            props = e.props_dict()
            if props.get("derivation") != DerivationKind.MIRROR.value:
                continue
            if props.get("unit") != property_name:
                continue
            affected.append(e)
        if not affected:
            return
        # Journal the multi-dependent sync for crash recovery.
        # Nested calls (multi-hop) append to the same journal; only the
        # outermost call clears it on success.
        journal_ops = [
            {"op": "sync_dependent",
             "dependent_id": e.source_id,
             "derived_property": e.props_dict().get("derived_property"),
             "target_id": idea_id,
             "unit": property_name,
             "derivation": DerivationKind.MIRROR.value,
             "subject_id": None,
             "edge_rel_id": e.rel_id}
            for e in affected
        ]
        # A9: increment AFTER successful journal write. If _write_journal
        # throws, depth is never incremented (no leak).
        self._write_journal(journal_ops)
        self._journal_depth += 1
        try:
            for e in affected:
                props = e.props_dict()
                ledger_key = (e.source_id, props.get("derived_property"))
                try:
                    self._recompute_dependent(e, live_idea=live_idea)
                except Exception as exc:
                    # R1-1: explicit FAILED, never silent.
                    self._propagation_ledger[ledger_key] = {
                        "status": PropagationStatus.FAILED.value,
                        "error": f"{type(exc).__name__}: {exc}",
                        "timestamp": time.time(),
                        "target_id": idea_id,
                    }
                    # Re-raise to signal the batch did not fully converge;
                    # the caller (_on_idea_event) records it. The journal
                    # remains for the unprocessed dependents.
                    raise
        finally:
            # Persist ledger state, then clear journal on full success.
            # If we raised, the journal remains for recovery replay.
            # Only the outermost call clears (nested multi-hop appends).
            # Never clear during replay (A12).
            self._journal_depth -= 1
            try:
                self.save()
            except Exception:
                pass
            if self._journal_depth == 0 and not self._replaying:
                import sys
                if sys.exc_info()[0] is None:
                    self._clear_journal()

    def _propagate_structure(self, subject_id: str) -> None:
        """Count-derivation propagation (CHILD_COUNT/DESCENDANT_COUNT).
        R1 (A10): journaled like the MIRROR path. A partial failure (e.g.,
        dependent #2's save throws after #1 committed) records FAILED
        explicitly — never a stale derived value presented as synchronized."""
        affected = []
        for rel_id in list(self._by_target.get(subject_id, [])):
            e = self._current[rel_id]
            if e.type != RelationshipType.DEPENDS_ON:
                continue
            props = e.props_dict()
            if props.get("derivation") not in (
                    DerivationKind.CHILD_COUNT.value,
                    DerivationKind.DESCENDANT_COUNT.value):
                continue
            dep_subject = props.get("subject_id") or e.source_id
            if dep_subject != subject_id:
                continue
            affected.append(e)
        for rel_id in list(self._by_source.get(subject_id, [])):
            e = self._current[rel_id]
            if e.type != RelationshipType.DEPENDS_ON:
                continue
            props = e.props_dict()
            if props.get("derivation") not in (
                    DerivationKind.CHILD_COUNT.value,
                    DerivationKind.DESCENDANT_COUNT.value):
                continue
            if props.get("subject_id", e.source_id) != subject_id:
                continue
            affected.append(e)
        if not affected:
            return
        journal_ops = [
            {"op": "sync_dependent",
             "dependent_id": e.source_id,
             "derived_property": e.props_dict().get("derived_property"),
             "target_id": e.target_id,
             "unit": None,
             "derivation": e.props_dict().get("derivation"),
             "subject_id": e.props_dict().get("subject_id"),
             "edge_rel_id": e.rel_id}
            for e in affected
        ]
        self._journal_depth += 1
        try:
            self._write_journal(journal_ops)
        except Exception:
            self._journal_depth -= 1
            raise
        try:
            for e in affected:
                props = e.props_dict()
                ledger_key = (e.source_id, props.get("derived_property"))
                try:
                    self._recompute_dependent(e)
                except Exception as exc:
                    self._propagation_ledger[ledger_key] = {
                        "status": PropagationStatus.FAILED.value,
                        "error": f"{type(exc).__name__}: {exc}",
                        "timestamp": time.time(),
                        "target_id": e.target_id,
                    }
                    raise
        finally:
            # Do NOT save here: _propagate_structure is always called from
            # _append's after() callback, and _append owns persistence.
            # Saving here would persist uncommitted entries on the failure
            # path (before _append rolls back). The FAILED ledger is
            # persisted by _append's save on success; on rollback the
            # operation failed and the caller sees the exception.
            # The journal is left for the outer _append to clear on success,
            # or for replay on crash.
            self._journal_depth -= 1

    def _recompute_dependent(self, edge: RelationshipEntry,
                              live_idea: Optional[Idea] = None) -> None:
        props = edge.props_dict()
        key = (edge.source_id, props.get("derived_property"))
        if key in self._propagating:
            return  # recursion guard: dependency cycle terminates
        self._propagating.add(key)
        try:
            derivation = DerivationKind(props["derivation"])
            if derivation == DerivationKind.MIRROR:
                # Prefer the live in-memory target: the observer fires
                # before the mutator necessarily saved to disk.
                if live_idea is not None and live_idea.id == edge.target_id:
                    target_props = live_idea.get_active_properties()
                else:
                    target = load_idea(edge.target_id, self.owner)
                    target_props = target.get_active_properties()
                new_value = deepcopy(target_props.get(props["unit"]))
            elif derivation == DerivationKind.CHILD_COUNT:
                subject = props.get("subject_id") or edge.source_id
                new_value = len(self.children(subject))
            elif derivation == DerivationKind.DESCENDANT_COUNT:
                subject = props.get("subject_id") or edge.source_id
                new_value = len(self.descendants(subject))
            else:
                return
            if live_idea is not None and live_idea.id == edge.source_id:
                dependent = live_idea
                save_after = False  # caller owns the save
            else:
                dependent = load_idea(edge.source_id, self.owner)
                save_after = True
            current = dependent.get_active_properties().get(
                props["derived_property"], _MISSING)
            if current is not _MISSING and current == new_value:
                return  # EQUALITY CUTOFF: unchanged → no write, no event
            prov = Provenance(
                source=ProvenanceSource.SYSTEM,
                activity="dependency_propagation",
                agent="semantic_graph",
                derived_from=[edge.rel_id],
                detail=(f"recomputed {props['derived_property']} via "
                        f"{derivation.value} of {edge.target_id[:8]}"),
            )
            dependent.set_property(props["derived_property"], new_value, prov)
            if save_after:
                save_idea(dependent, self.owner)
            # SF-P2-1 multi-hop: this dependent's newly derived value may
            # feed further dependents (chains a→b→c). Re-enter propagation
            # for the derived property; the _propagating guard terminates
            # cycles. Pass the live dependent when the caller hasn't saved
            # yet so the next hop reads the fresh in-memory value.
            self._propagate_property(
                edge.source_id, props["derived_property"],
                live_idea=None if save_after else dependent,
            )
        finally:
            self._propagating.discard(key)


_MISSING = object()
