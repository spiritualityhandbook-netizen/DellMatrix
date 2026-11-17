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
import uuid
from form.utc_time import utc_now_str

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


class NurseryReasonError(ValueError):
    """Proposal reason exceeds the Nursery's admitted bound (Q-S2.2).

    Raised by Nursery.add BEFORE any mutation or save: oversize input is
    refused explicitly and nothing is stored, replacing the historical
    silent truncation at 160 chars, which destroyed admitted content
    (the inference dock admits reasons up to 1,000 chars) with no error."""


# Q-S2.2: the Nursery's admitted bound for Proposal.reason — the same
# 1,000-char bound the inference dock enforces by explicit refusal
# (form/dell_matrix/inference_dock.py: host reason in propose() and at
# the semantic-verb entry, model reason in validate_semantic_output)
# and director_session.py's MAX_REASON_CHARS = 1000, before callers
# reach Nursery.add. Admitted reasons are stored in full, exactly;
# reasons beyond the bound raise NurseryReasonError with no mutation.
# The dock-session evidence validator (dock_session.py) shares this
# bound, since its entries carry the stored reason verbatim.
MAX_REASON_CHARS = 1000


class NurseryOriginError(ValueError):
    """Proposal origin exceeds the Nursery's admitted bound (C5R.1).

    Raised by Nursery.add BEFORE any mutation or save: oversize input
    is refused explicitly and nothing is stored, replacing the
    historical silent truncation at 120 chars (the inference dock
    keeps the whole origin inside this bound by construction — its
    _origin_for segments are limited so the assembled origin fits)."""


# C5R.1: the Nursery's admitted bound for Proposal.origin — the same
# 120-char bound the inference dock's _origin_for is built to fit.
# Admitted origins are stored in full, exactly; origins beyond the
# bound raise NurseryOriginError with no mutation.
MAX_ORIGIN_CHARS = 120


class NurseryDetailError(ValueError):
    """Proposal detail exceeds the Nursery's admitted bound (C5R.1).

    Raised by Nursery.add BEFORE any mutation or save: oversize input
    is refused explicitly and nothing is stored, replacing the
    historical silent truncation at 2,000 chars (the inference dock
    admits detail up to 2,000 chars by explicit refusal)."""


# C5R.1: the Nursery's admitted bound for Proposal.detail — the same
# 2,000-char bound the inference dock enforces by explicit refusal
# (form/dell_matrix/inference_dock.py MAX_DETAIL_CHARS = 2000) before
# it calls Nursery.add. Admitted detail is stored in full, exactly;
# detail beyond the bound raises NurseryDetailError with no mutation.
MAX_DETAIL_CHARS = 2000


class NurseryGoalsError(ValueError):
    """Proposal goals exceed the Nursery's admitted bounds (C5R.1).

    Raised by Nursery.add BEFORE any mutation or save: an over-bound
    goals list (more than MAX_GOALS entries, a goal longer than
    MAX_GOAL_CHARS, or a non-string entry) is refused explicitly and
    nothing is stored, replacing the historical silent per-goal
    truncation at 200 chars, silent list truncation at 8, and silent
    dropping of non-string/empty entries."""


# C5R.1: the Nursery's admitted bounds for Proposal.goals — the same
# bounds the inference dock enforces by explicit refusal
# (form/dell_matrix/inference_dock.py MAX_GOALS = 8,
# MAX_GOAL_CHARS = 200) before it calls Nursery.add. Admitted goals
# are stored in full, exactly, in order; goals beyond the bounds
# raise NurseryGoalsError with no mutation.
MAX_GOALS = 8
MAX_GOAL_CHARS = 200


class NurseryLabelError(ValueError):
    """Proposal label exceeds the Nursery's admitted bound (Q-S2.1).

    Raised by Nursery.add BEFORE any mutation or save: an over-bound
    label is refused explicitly and nothing is stored, replacing the
    historical silent truncation at 80 chars, which destroyed admitted
    content (the inference dock admits labels up to 200 chars) with no
    error."""


# Q-S2.1: the Nursery's admitted bound for Proposal.label — the same
# 200-char bound the inference dock enforces by explicit refusal
# (form/dell_matrix/inference_dock.py MAX_LABEL_CHARS = 200) before it
# calls Nursery.add. Admitted labels are stored in full, exactly;
# labels beyond the bound raise NurseryLabelError with no mutation.
MAX_LABEL_CHARS = 200


class NurseryWordsError(ValueError):
    """Proposal words exceed the Nursery's admitted bound (SYS-C29).

    Raised by Nursery.add BEFORE any mutation or save: oversize input is
    refused explicitly and nothing is stored, replacing the historical
    silent truncation at 240 chars, which destroyed admitted content
    (the inference dock admits words up to 5,000 chars) with no error."""


# SYS-C29: the Nursery's admitted bound for Proposal.words — the same
# 5,000-char bound the inference dock enforces by explicit refusal
# (form/dell_matrix/inference_dock.py MAX_WORDS_CHARS = 5000) before it
# calls Nursery.add. Admitted words are stored in full, exactly; words
# beyond the bound raise NurseryWordsError with no mutation. Per the
# Elastic Limits Doctrine the bound is a runaway stop, not a hindrance:
# it sits at the system's own admitted maximum.
MAX_WORDS_CHARS = 5000


class NurseryTopicError(ValueError):
    """Proposal topic exceeds the Nursery's admitted bound (C5R.3).

    Raised BEFORE any mutation or save: an over-bound topic is refused
    explicitly and nothing is stored, in the same typed-refusal style
    as NurseryLabelError / NurseryWordsError. Admitted topics are
    stored in full, exactly — never silently sliced."""


# C5R.3: the Nursery's admitted bound for Proposal.topic. Justified
# against the AC-3.1 1,000-proposal acceptance fixture: at 200 chars
# the topic contributes at most ~200 bytes per record (~200 KB over
# the whole fixture), small next to the already-admitted 5,000-char
# words field, so the bound is a runaway stop in the Elastic Limits
# sense, not a hindrance.
MAX_TOPIC_CHARS = 200


class NurseryTagsError(ValueError):
    """Proposal tags exceed the Nursery's admitted bounds, or repeat a
    tag exactly (C5R.3).

    Raised BEFORE any mutation or save: an over-bound tag list (more
    than MAX_TAGS entries, a tag longer than MAX_TAG_CHARS, or a
    non-string entry) is refused explicitly and nothing is stored.
    An EXACT duplicate tag within the list is likewise refused with
    this named error — duplicates are never silently deduplicated or
    normalized away. Tags differing only in case or spelling are
    distinct tags: the exact accepted spelling is what is stored."""


# C5R.3: the Nursery's admitted bounds for Proposal.tags. Justified
# against the AC-3.1 1,000-proposal fixture: at most 16 tags of at
# most 100 chars is ~1.6 KB of tag data per record worst case, the
# same order as the already-admitted reason (1,000) and detail
# (2,000) bounds; organization metadata stays a small fraction of a
# record next to the 5,000-char words field.
MAX_TAGS = 16
MAX_TAG_CHARS = 100


class NurseryClusterError(ValueError):
    """Proposal cluster exceeds the Nursery's admitted bound (C5R.3).

    Raised BEFORE any mutation or save: an over-bound cluster is
    refused explicitly and nothing is stored. Cluster is an
    organization reference only — never a containment/Plane
    authority."""


# C5R.3: the Nursery's admitted bound for Proposal.cluster — the same
# 200-char class as label/topic, justified the same way against the
# 1,000-proposal fixture.
MAX_CLUSTER_CHARS = 200


def validate_topic(topic: Any) -> str:
    """Admit a topic value or refuse typed (C5R.3). Returns the value
    unchanged (exact spelling preserved) when admitted."""
    if not isinstance(topic, str) or len(topic) > MAX_TOPIC_CHARS:
        raise NurseryTopicError(
            f"topic must be a string of at most {MAX_TOPIC_CHARS} "
            f"chars; refused, nothing stored")
    return topic


def validate_tags(tags: Any) -> List[str]:
    """Admit a tag list or refuse typed (C5R.3). Returns the list
    unchanged (exact spellings, order preserved) when admitted. An
    exact duplicate tag is a refusal, never a silent dedup."""
    if not isinstance(tags, list) or len(tags) > MAX_TAGS:
        raise NurseryTagsError(
            f"tags must be a list of at most {MAX_TAGS} entries; "
            f"refused, nothing stored")
    seen: set = set()
    for t in tags:
        if not isinstance(t, str) or len(t) > MAX_TAG_CHARS:
            raise NurseryTagsError(
                f"each tag must be a string of at most "
                f"{MAX_TAG_CHARS} chars; refused, nothing stored")
        if t in seen:
            raise NurseryTagsError(
                f"duplicate tag {t!r} refused; tags are never "
                f"silently deduplicated, nothing stored")
        seen.add(t)
    return tags


def validate_cluster(cluster: Any) -> str:
    """Admit a cluster value or refuse typed (C5R.3). Returns the
    value unchanged when admitted."""
    if not isinstance(cluster, str) or len(cluster) > MAX_CLUSTER_CHARS:
        raise NurseryClusterError(
            f"cluster must be a string of at most "
            f"{MAX_CLUSTER_CHARS} chars; refused, nothing stored")
    return cluster


# Reserved nursery-file key for DCC-XIX conflict dispositions. Can never
# collide with a proposal ID: _slug() output is lowercase alnum plus
# underscores, stripped of leading/trailing underscores, with a numeric
# hash suffix -- it can never equal this dunder constant.
DISPOSITION_SECTION_KEY = "__conflict_dispositions__"

# C5R.3: reserved nursery-file key for human organization EDIT
# receipts (same-file section precedent: DCC-XIX dispositions above).
# Can never collide with a proposal ID for the same _slug() reason.
# Phase 1 ships the load/save plumbing only — the section starts
# empty and round-trips; the edit door that appends receipts is
# Phase 2. Stored receipts carry NO file digest (Resolution 3): the
# canonical post-save digest is returned to the caller, never
# embedded in the file that digest describes.
EDIT_RECEIPT_SECTION_KEY = "__organization_edit_receipts__"

# C5R.3 creation-seed rule (seed-rule v1). Deterministic, applied
# ONLY at Nursery.add() construction of a genuinely NEW proposal:
#   primary  = validated kind — the canonical validated-kind set for
#              v1 is exactly the Proposal docstring's producer kinds
#              (Acting-Keeper ruling on Q-C5R.3-UNI.1, PR #460);
#   fallback = validated origin family (the origin's leading segment
#              before the first ":", when it is a well-formed family
#              token);
#   else     = the explicit topic "unclassified".
# Any expansion of the validated-kind set requires a seed-rule
# version increment. Legacy records are never seeded: load/browse
# assign nothing.
SEED_RULE_VERSION = "c5r3-seed-v1"
SEED_VALIDATED_KINDS = frozenset({"new", "evolved", "design", "auto"})
UNCLASSIFIED_TOPIC = "unclassified"

_ORIGIN_FAMILY_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


def _origin_family(origin: Any) -> Optional[str]:
    """The validated origin family for the seed fallback: the
    origin's leading segment (e.g. "growth" for "growth:token",
    "dock" for "dock:<provider>:<model>"), or None when the origin
    is absent or its family segment is not a well-formed token."""
    if not isinstance(origin, str) or not origin:
        return None
    family = origin.split(":", 1)[0]
    return family if _ORIGIN_FAMILY_RE.match(family) else None


def _derive_seed_topic(kind: Any, origin: Any) -> tuple:
    """Seed-rule v1: returns (topic, seed_topic_source) where the
    source is "kind", "origin_family", or "unclassified"."""
    if isinstance(kind, str) and kind in SEED_VALIDATED_KINDS:
        return kind, "kind"
    family = _origin_family(origin)
    if family is not None:
        return family, "origin_family"
    return UNCLASSIFIED_TOPIC, "unclassified"


def build_organization_receipt(
    *,
    operation_id: str,
    actor: str,
    proposal_id: str,
    before: Dict[str, Any],
    after: Dict[str, Any],
    rule_version: str,
    predecessor_generation: Optional[str],
) -> Dict[str, Any]:
    """The STORABLE organization receipt (C5R.3, Resolution 3).

    Carries operation ID, trusted actor (or "system_seed" for the
    automatic creation seed), proposal ID, before/after organization
    state, rule version, and the predecessor-generation identity
    (the pre-save _seen). It deliberately carries NO file digest:
    the canonical digest of the generation this receipt lands in
    cannot be known before that generation is written, and a file
    must never embed a claim to be its own digest. Use
    receipt_with_file_digest() for the RETURNED form handed to the
    caller after a successful save; that form is never stored.
    """
    return {
        "operation_id": operation_id,
        "actor": actor,
        "proposal_id": proposal_id,
        "before": before,
        "after": after,
        "rule_version": rule_version,
        "predecessor_generation": predecessor_generation,
    }


def receipt_with_file_digest(receipt: Dict[str, Any],
                             file_digest: Optional[str]) -> Dict[str, Any]:
    """The RETURNED receipt form: a copy of the storable receipt plus
    the canonical post-save file digest (Nursery._seen after save).
    Return-only — this dict is never serialized into the owner file.
    """
    out = dict(receipt)
    out["file_digest"] = file_digest
    return out


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
    return utc_now_str()


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
    kind: str  # producer kinds in production use: "new" |
    # "evolved" (growth + docked verbs) | "design" (SD-5: a
    # proposal whose confirmation accepts a design for host
    # implementation) | "auto" (AutoGrowth's auto-propose path)
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
    # Post-GDP Phase E: action provenance (additive). origin records
    # who/what drafted this proposal when the creator knows: the dock
    # sets "dock:<provider>:<actual model>" for inference-drafted
    # proposals, so a reviewer can tell model-drafted proposals from
    # human-typed ones at the review gate. "" = not recorded (legacy
    # records and creators that do not assert provenance); never
    # fabricated after the fact. Proposal(**record) fills the default
    # for pre-Phase-E nursery files.
    origin: str = ""
    # SD-2 (master plan P5): authored content carried by semantic
    # proposals (the dock's RELATE / SYNTHESIZE / FLAG verbs). The
    # confirmation writer (confirm_lineage) already prefers
    # prop.detail / prop.goals over its first-parent fallback, so a
    # synthesized proposal's AUTHORED text — not a parent's — is
    # what confirmation places. Defaults keep legacy nursery files
    # loading unchanged (same additive pattern as origin).
    detail: str = ""
    goals: List[str] = field(default_factory=list)
    # C5R.3 ORGANIZE (Phase 1): organization metadata + creation-seed
    # provenance (additive; the defaults keep pre-C5R.3 nursery files
    # loading unchanged — Proposal(**record) fills these for legacy
    # records). topic/tags/cluster are organization metadata only:
    # never a retention bucket, never a containment/Plane authority.
    # Legacy records are NEVER seeded on load or browse: the seed
    # below is assigned only at Nursery.add() construction of a
    # genuinely NEW proposal (a GROW-DUP-suppressed add returns its
    # survivor before construction and is never seeded).
    topic: str = ""
    tags: List[str] = field(default_factory=list)
    cluster: str = ""
    # Creation-seed provenance: which source produced `topic` at
    # creation ("kind" | "origin_family" | "unclassified"; "" =
    # unseeded legacy record), the EXACT source field values the
    # seed rule consulted, the seed-rule version, and the creation
    # receipt's operation ID (actor "system_seed"; see
    # build_organization_receipt). The canonical post-save file
    # digest is NEVER stored on the record — it is returned to the
    # caller after save (Nursery.save / last_organization_receipt).
    seed_topic_source: str = ""
    seed_source_kind: str = ""
    seed_source_origin: str = ""
    seed_rule_version: str = ""
    seed_operation_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# Sentinel for "argument not passed" in the SEE query API. A
# continuation call must distinguish an absent filter argument
# (the cursor's bound value governs) from an explicitly passed
# one (which must equal the bound value or refuse loudly) —
# Director source review on PR #465, 2026-11-16.
SEE_UNSET = object()



def _validate_loaded_organization(key: str, rec: "Proposal",
                                  path: str) -> None:
    """Fail-closed shape check for a staged record's C5R.3
    organization fields (AC-3.1): malformed persisted metadata
    raises NurseryLoadError during load staging — it is never
    converted into a seemingly valid empty value, and no partially
    loaded Nursery escapes. Type and bound checks mirror the
    admission validators (validate_topic / validate_tags /
    validate_cluster) plus the exact-duplicate tag refusal."""
    base = os.path.basename(path)

    def bad(why: str) -> NurseryLoadError:
        return NurseryLoadError(
            f"nursery file {base} has a malformed organization "
            f"field for {key!r}: {why}")

    if not isinstance(rec.topic, str) or len(rec.topic) > MAX_TOPIC_CHARS:
        raise bad(f"topic must be a string of at most "
                  f"{MAX_TOPIC_CHARS} chars")
    if not isinstance(rec.cluster, str) \
            or len(rec.cluster) > MAX_CLUSTER_CHARS:
        raise bad(f"cluster must be a string of at most "
                  f"{MAX_CLUSTER_CHARS} chars")
    if not isinstance(rec.tags, list) or len(rec.tags) > MAX_TAGS:
        raise bad(f"tags must be a list of at most {MAX_TAGS} entries")
    seen: set = set()
    for t in rec.tags:
        if not isinstance(t, str) or len(t) > MAX_TAG_CHARS:
            raise bad(f"each tag must be a string of at most "
                      f"{MAX_TAG_CHARS} chars")
        if t in seen:
            raise bad(f"duplicate tag {t!r}")
        seen.add(t)
    for fname in ("seed_topic_source", "seed_source_kind",
                  "seed_source_origin", "seed_rule_version",
                  "seed_operation_id"):
        if not isinstance(getattr(rec, fname), str):
            raise bad(f"{fname} must be a string")


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
    # GROW-DUP (Director ruling 6931279746): receipts for token-growth
    # adds suppressed as demonstrably identical to a still-pending
    # growth:token proposal. In-memory only — a receipt is evidence
    # about THIS instance's add stream, never stored proposal state,
    # so it is never serialized into the owner file.
    suppression_receipts: List[Dict[str, Any]] = field(
        default_factory=list, repr=False, compare=False)
    # C5R.3: human organization EDIT receipts (operation_id ->
    # receipt record, the storable form from
    # build_organization_receipt — no file digest inside). Serialized
    # under EDIT_RECEIPT_SECTION_KEY in the same atomic write as the
    # proposals and dispositions. Phase 1 ships the plumbing only:
    # the section starts empty and round-trips; the Phase 2 edit
    # door appends receipts.
    organization_edit_receipts: Dict[str, Dict[str, Any]] = field(
        default_factory=dict, repr=False, compare=False)
    # C5R.3: the most recent organization operation's RETURNED
    # receipt (receipt_with_file_digest form, including the
    # canonical post-save digest). In-memory only, like the
    # suppression receipts: the digest describes the file, so it is
    # handed to the caller and never serialized into it.
    last_organization_receipt: Optional[Dict[str, Any]] = field(
        default=None, repr=False, compare=False)

    def _suppression_fresh(self) -> bool:
        """True when this instance provably sees the current owner
        file — the same signature comparison save() enforces
        (``_disk_sig(self.path) == self._seen``). An ownerless
        in-memory nursery has no external writer, so its view is
        current by construction."""
        if not self.path:
            return True
        return _disk_sig(self.path) == self._seen

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
        origin: str = "",
        detail: str = "",
        goals: Optional[List[str]] = None,
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

        Q-S2.1: labels are stored in full up to MAX_LABEL_CHARS; longer
        labels raise NurseryLabelError BEFORE any mutation or save (the
        historical label[:80] silently destroyed admitted content).

        SYS-C29: words are stored in full up to MAX_WORDS_CHARS; longer
        words raise NurseryWordsError BEFORE any mutation or save (the
        historical words[:240] silently destroyed admitted content).

        Q-S2.2: reason is stored in full up to MAX_REASON_CHARS; a longer
        reason raises NurseryReasonError BEFORE any mutation or save (the
        historical reason[:160] silently destroyed admitted content).

        C5R.1: origin, detail and goals follow the same contract at the
        bounds the inference dock already enforces by explicit refusal
        (origin 120, detail 2,000, goals 8 x 200): admitted values are
        stored byte-exact; over-bound values raise NurseryOriginError /
        NurseryDetailError / NurseryGoalsError BEFORE any mutation or
        save (the historical origin[:120] / detail[:2000] /
        goals[:200]-and-[:8] silently destroyed admitted content, and
        non-string or empty goals were silently dropped).

        C5R.3: a genuinely NEW proposal is automatically seeded at
        construction (seed-rule v1: validated kind, else validated
        origin family, else explicit "unclassified") with its
        provenance persisted on the record in this same save; the
        creation receipt's returned form (including the canonical
        post-save digest) is exposed as last_organization_receipt.
        """
        if isinstance(label, str) and len(label) > MAX_LABEL_CHARS:
            raise NurseryLabelError(
                f"label length {len(label)} exceeds the admitted bound "
                f"of {MAX_LABEL_CHARS} chars; refused, nothing stored")
        if isinstance(words, str) and len(words) > MAX_WORDS_CHARS:
            raise NurseryWordsError(
                f"words length {len(words)} exceeds the admitted bound "
                f"of {MAX_WORDS_CHARS} chars; refused, nothing stored")
        if isinstance(reason, str) and len(reason) > MAX_REASON_CHARS:
            raise NurseryReasonError(
                f"reason length {len(reason)} exceeds the admitted bound "
                f"of {MAX_REASON_CHARS} chars; refused, nothing stored")
        if isinstance(origin, str) and len(origin) > MAX_ORIGIN_CHARS:
            raise NurseryOriginError(
                f"origin length {len(origin)} exceeds the admitted bound "
                f"of {MAX_ORIGIN_CHARS} chars; refused, nothing stored")
        if isinstance(detail, str) and len(detail) > MAX_DETAIL_CHARS:
            raise NurseryDetailError(
                f"detail length {len(detail)} exceeds the admitted bound "
                f"of {MAX_DETAIL_CHARS} chars; refused, nothing stored")
        if goals is not None:
            if not isinstance(goals, list) or len(goals) > MAX_GOALS:
                raise NurseryGoalsError(
                    f"goals must be a list of at most {MAX_GOALS} "
                    f"entries; refused, nothing stored")
            for g in goals:
                if not isinstance(g, str) or len(g) > MAX_GOAL_CHARS:
                    raise NurseryGoalsError(
                        f"each goal must be a string of at most "
                        f"{MAX_GOAL_CHARS} chars; refused, nothing stored")
        # GROW-DUP (Director ruling 6931279746, scoped): token growth
        # re-derives the same pair cross every cycle, and the historical
        # add stored each re-derivation as a new pending proposal (the
        # _slug collision suffix minted a fresh ID per copy). Suppress
        # ONLY a demonstrably identical still-PENDING growth:token add:
        # both records carry origin="growth:token" (token provenance on
        # both sides), and kind, full label, full words, detail, goals,
        # parents, reason and the score fields (affinity, harmony,
        # graph_coherence) are all exactly equal. Generated ID and
        # creation time are excluded from equality. Parents compare as
        # ordered lists: the growth enumeration emits a pair in one
        # canonical order, and the lineage is spelled out in words, so
        # a different parent order is a different authored proposal.
        # Anything else — changed content, different provenance (human,
        # dock, growth:body), different scores, a non-pending survivor —
        # is stored as its own proposal, exactly as before. A skip
        # mutates nothing, saves nothing, and returns the survivor with
        # a receipt recorded on this instance.
        #
        # G-DUP.1 (Director 6933752017): suppression returns a record
        # WITHOUT passing the save-time lost-update check, so it is
        # lawful only when this instance provably sees the current
        # owner file (freshness-before-suppression). A stale instance
        # — whose in-memory "pending" survivor may already be
        # confirmed, rejected, or removed on disk — falls through to
        # the normal add path, whose save raises the canonical
        # NurseryConflictError. A genuine skip (fresh instance) still
        # performs no save and writes nothing.
        if origin == "growth:token" and self._suppression_fresh():
            for existing in self.proposals.values():
                if (
                    existing.status == "pending"
                    and existing.origin == "growth:token"
                    and existing.kind == kind
                    and existing.label == label
                    and existing.words == words
                    and existing.detail == (detail if isinstance(detail, str) else "")
                    and existing.goals == (list(goals) if goals else [])
                    and existing.parents == (parents or [])
                    and existing.reason == reason
                    and existing.affinity == float(affinity)
                    and existing.harmony == float(harmony)
                    and existing.graph_coherence == float(graph_coherence)
                ):
                    self.suppression_receipts.append({
                        "surviving_id": existing.id,
                        "reason": "identical_pending_growth_token",
                        "kind": kind,
                        "label": label,
                    })
                    return existing
        pid = _slug(label, seed)
        # avoid exact id collision
        if pid in self.proposals:
            pid = pid + "_" + str(len(self.proposals))
        # C5R.3 (AC-3.2): the creation seed is derived HERE, at
        # construction of a genuinely NEW proposal — the GROW-DUP
        # suppression path above returns its survivor BEFORE this
        # point, so a suppressed add is never seeded, mutated, or
        # saved. The seed rides the Proposal record itself, so the
        # pop-on-failure path below keeps seed + proposal atomic:
        # both persist or neither does.
        seed_topic, seed_source = _derive_seed_topic(kind, origin)
        validate_topic(seed_topic)
        predecessor = self._seen
        p = Proposal(
            id=pid,
            label=label,
            words=words,
            kind=kind,
            parents=parents or [],
            affinity=float(affinity),
            reason=reason,
            harmony=float(harmony),
            graph_coherence=float(graph_coherence),
            origin=origin if isinstance(origin, str) else "",
            detail=detail if isinstance(detail, str) else "",
            goals=list(goals) if goals else [],
            topic=seed_topic,
            seed_topic_source=seed_source,
            seed_source_kind=kind if isinstance(kind, str) else "",
            seed_source_origin=origin if isinstance(origin, str) else "",
            seed_rule_version=SEED_RULE_VERSION,
            seed_operation_id=f"seed:{pid}",
        )
        self.proposals[pid] = p
        try:
            self.save()
        except Exception:
            self.proposals.pop(pid, None)
            raise
        # The creation receipt's RETURNED form (Resolution 3): the
        # canonical post-save digest is attached only now that the
        # save has succeeded, and only to this in-memory copy — the
        # storable provenance on the record carries no digest.
        self.last_organization_receipt = receipt_with_file_digest(
            build_organization_receipt(
                operation_id=p.seed_operation_id,
                actor="system_seed",
                proposal_id=pid,
                before={"topic": "", "tags": [], "cluster": ""},
                after={"topic": p.topic, "tags": list(p.tags),
                       "cluster": p.cluster},
                rule_version=SEED_RULE_VERSION,
                predecessor_generation=predecessor),
            self._seen)
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

    # ── C5R.3 ORGANIZE Phase 2: trusted human organization edits ──
    # The ONE organization mutation operation (Director 6936275880,
    # Resolutions 1/3/4/5/7). It changes ONLY topic/tags/cluster,
    # persists through this instance's canonical save() (the
    # check_save_allowed recovery guard and the lost-update check
    # ride along — never bypassed), and appends the edit's storable
    # receipt to organization_edit_receipts in the SAME transaction.
    # There is no undo stack here: Q-LC.1 generation rollback is
    # the only undo authority, and per-edit organization undo is
    # explicitly UNAVAILABLE (ORG_UNDO_NOTE is surfaced to callers).
    ORG_UNDO_NOTE = (
        "organization undo is unavailable at edit granularity: "
        "Q-LC.1 generation rollback is the only undo authority; "
        "no shadow undo stack exists")

    def organize_proposal(
        self,
        pid: str,
        *,
        actor: str,
        topic: Any = SEE_UNSET,
        tags: Any = SEE_UNSET,
        cluster: Any = SEE_UNSET,
        expected_generation: Any = SEE_UNSET,
        _fail_at: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Edit one proposal's organization metadata (topic/tags/
        cluster), receipted, through the canonical save.

        Boundary (Resolution 5): ``actor`` is the TRUSTED subject
        established by the host caller (the REPL door passes
        "repl:<owner>"; a Program caller passes its own traced
        subject). It is never parsed from proposal content or from
        the edited line — a model-supplied actor string is not
        authentication, and this method is unreachable from the
        connect-session dispatcher by construction. A missing/empty
        actor is a caller bug and raises ValueError.

        Binding: the edit resolves by stable ID in THIS owner-bound
        store. When ``expected_generation`` is passed, it must equal
        the owner file's current on-disk signature (_disk_sig) or
        the edit refuses STALE_GENERATION before staging anything —
        the STALE_CURSOR pattern applied to mutation. Independently,
        save()'s own lost-update check still applies to a stale
        instance (NurseryConflictError propagates, in-memory values
        restored).

        Values: fields left SEE_UNSET keep their current values;
        passed fields are validated as one complete proposed state
        by the Phase 1 admission validators (typed NurseryTopicError
        / NurseryTagsError / NurseryClusterError, raised BEFORE any
        mutation or staging). Only topic/tags/cluster change — id,
        label, words, reason, detail, goals, parents, status,
        lineage and the creation-seed provenance are byte-identical
        after an edit; the seed history is retained under a human
        override (the receipt records topic_source "human" when the
        edit sets the topic).

        Outcomes: success returns {"ok": True, "receipt": <returned
        receipt form incl. the canonical post-save file_digest>,
        "generation": <post-save digest>, "undo": ORG_UNDO_NOTE}.
        Refusals that are caller-state facts (unknown ID, no fields,
        stale expected generation) return {"ok": False, "error":
        code, "detail": ..., "receipt": <truthful refusal receipt>,
        "undo": ORG_UNDO_NOTE} and persist NOTHING — a refusal
        receipt is returned to the caller, never written, because
        writing it would itself mutate the generation it reports on.
        A persistence failure restores the staged in-memory values
        (Persistence V2: the old canonical generation stays intact)
        and re-raises.
        """
        if not isinstance(actor, str) or not actor:
            raise ValueError(
                "organize_proposal requires a non-empty trusted "
                "actor subject established by the host caller; a "
                "model-supplied actor string is not authentication")
        op_id = (f"edit:{pid}:"
                 f"{len(self.organization_edit_receipts) + 1}")
        refusal_base = {
            "operation_id": op_id,
            "actor": actor,
            "proposal_id": pid,
            "rule_version": SEED_RULE_VERSION,
            "predecessor_generation": self._seen,
            "outcome": "refused",
        }

        def refuse(code: str, detail: str) -> Dict[str, Any]:
            receipt = dict(refusal_base, reason=code)
            return {"ok": False, "error": code, "detail": detail,
                    "receipt": receipt, "undo": self.ORG_UNDO_NOTE}

        p = self.proposals.get(pid)
        if p is None:
            return refuse(
                "PROPOSAL_NOT_FOUND",
                f"no proposal {pid!r} in this owner's nursery")
        if topic is SEE_UNSET and tags is SEE_UNSET \
                and cluster is SEE_UNSET:
            return refuse(
                "NO_CHANGES",
                "name at least one of topic, tags, or cluster")
        if expected_generation is not SEE_UNSET:
            current = _disk_sig(self.path) if self.path else self._seen
            if expected_generation != current:
                return refuse(
                    "STALE_GENERATION",
                    "the nursery generation the edit was prepared "
                    "against is not the current on-disk generation; "
                    "re-read the proposal and retry — nothing was "
                    "staged or written")
        # Compose and validate the ENTIRE proposed organization
        # state before changing any value (typed refusals raise).
        new_topic = validate_topic(
            p.topic if topic is SEE_UNSET else topic)
        new_tags = validate_tags(
            list(p.tags) if tags is SEE_UNSET else tags)
        new_cluster = validate_cluster(
            p.cluster if cluster is SEE_UNSET else cluster)
        before = {"topic": p.topic, "tags": list(p.tags),
                  "cluster": p.cluster}
        after = {"topic": new_topic, "tags": list(new_tags),
                 "cluster": new_cluster}
        predecessor = self._seen
        receipt = build_organization_receipt(
            operation_id=op_id,
            actor=actor,
            proposal_id=pid,
            before=before,
            after=after,
            rule_version=SEED_RULE_VERSION,
            predecessor_generation=predecessor)
        receipt["kind"] = "human_organization_edit"
        receipt["created"] = _ts()
        if topic is not SEE_UNSET:
            # The plan's override marker: the current topic is now
            # human-set; the creation seed history stays on the
            # record untouched (seed_* fields are never rewritten).
            receipt["topic_source"] = "human"
        old_tags = p.tags
        prior_receipt = self.last_organization_receipt
        p.topic = new_topic
        p.tags = list(new_tags)
        p.cluster = new_cluster
        self.organization_edit_receipts[op_id] = receipt
        try:
            self.save(_fail_at=_fail_at)
        except Exception:
            p.topic = before["topic"]
            p.tags = old_tags
            p.cluster = before["cluster"]
            self.organization_edit_receipts.pop(op_id, None)
            self.last_organization_receipt = prior_receipt
            raise
        self.last_organization_receipt = receipt_with_file_digest(
            receipt, self._seen)
        return {"ok": True, "receipt": self.last_organization_receipt,
                "generation": self._seen, "undo": self.ORG_UNDO_NOTE}

    # ── C5R.2 SEE: read-only query service (AC-2.1-AC-2.4) ──────
    # Complete Nursery visibility over THIS owner-bound store. The
    # query path never calls save/confirm/reject or any placement
    # operation; it reads the in-memory records and returns copies
    # (Proposal.to_dict). Design answers (Director plan
    # DIRECTOR_PLAN_C5R2_SEE_2026-11-16.md section 4, Q-SEE.1-5):
    # (1) cursor version = the owner file's on-disk SHA-256
    #     (_disk_sig), re-read at every page; this instance's _seen
    #     must equal it or the query refuses STALE_OWNER_STATE
    #     before page 1, and a generation change between pages
    #     refuses STALE_CURSOR — an old in-memory instance never
    #     pretends to represent a newer on-disk version.
    # (2) sort is (created, id) ascending, id the final tie-break.
    # (3) search = Unicode casefold substring over every persisted
    #     text field plus canonical scalars (str() of revision
    #     number and the three scores); conflict dispositions are
    #     not proposal fields and are never searched.
    # (4) page size default 50, max 200; invalid sizes refuse with
    #     PAGE_SIZE_INVALID — never silently clamped. Page size is
    #     a work parameter, never a retention control.

    SEE_STATUSES = ("pending", "confirmed", "rejected")
    SEE_DEFAULT_PAGE = 50
    SEE_MAX_PAGE = 200

    @staticmethod
    def _see_refusal(code: str, detail: str) -> Dict[str, Any]:
        return {"ok": False, "error": code, "detail": detail}

    @staticmethod
    def _see_searchable(p: "Proposal") -> List[str]:
        vals = [p.id, p.label, p.words, p.kind, p.reason, p.created,
                p.status, p.lifecycle_state, p.origin, p.detail]
        vals.extend(p.parents or [])
        vals.extend(p.goals or [])
        # C5R.3 (Resolution 6): organization fields are searchable
        # ONLY because they are enumerated here deliberately —
        # adding the dataclass fields alone changed nothing. The
        # stored topic ("" for legacy records), every stored tag,
        # and the stored cluster ("" = unset) are the search text;
        # the derived effective topic used for grouping is a view
        # projection and is not a stored field, so it is not added.
        vals.append(p.topic)
        vals.extend(p.tags or [])
        vals.append(p.cluster)
        for extra in (p.supersedes_id, p.superseded_by_id,
                      p.revision_root_id):
            if extra:
                vals.append(extra)
        for scalar in (p.revision_number, p.affinity, p.harmony,
                       p.graph_coherence):
            if scalar is not None:
                vals.append(str(scalar))
        return vals

    @staticmethod
    def _see_cursor_encode(payload: Dict[str, Any]) -> str:
        # Hex, not base64: the REPL lowercases every line before
        # dispatch, and a cursor must survive that transport intact.
        # Hex is lowercase-safe by construction.
        raw = json.dumps(payload, separators=(",", ":"),
                         sort_keys=True).encode("utf-8")
        return raw.hex()

    @staticmethod
    def _see_cursor_decode(cursor: Any) -> Optional[Dict[str, Any]]:
        if not isinstance(cursor, str) or not cursor:
            return None
        try:
            raw = bytes.fromhex(cursor).decode("utf-8")
            data = json.loads(raw)
        except Exception:
            return None
        if not isinstance(data, dict) or data.get("v") != 1:
            return None
        for key in ("owner", "mode", "sig", "status", "term",
                    "size", "last"):
            if key not in data:
                return None
        # Field types are validated, not assumed: a hand-crafted
        # cursor must refuse CURSOR_MALFORMED, never crash the
        # query (Codex P2 on PR #465, accepted).
        if not isinstance(data["owner"], str):
            return None
        if data["mode"] not in ("browse", "search"):
            return None
        if data["sig"] is not None and not isinstance(data["sig"], str):
            return None
        if (data["status"] is not None
                and not isinstance(data["status"], str)):
            return None
        if not isinstance(data["term"], str):
            return None
        if (isinstance(data["size"], bool)
                or not isinstance(data["size"], int)):
            return None
        last = data["last"]
        if last is not None:
            if (not isinstance(last, list) or len(last) != 2
                    or not all(isinstance(x, str) for x in last)):
                return None
        # C5R.3: the organization filter/group keys are OPTIONAL in
        # the payload — cursors issued before C5R.3 lack them and
        # bind None (no organization filter, no grouping). When
        # present they are type-validated like every other field.
        for key in ("topic", "tag", "cluster"):
            if key in data and data[key] is not None \
                    and not isinstance(data[key], str):
                return None
        if "group" in data and data["group"] not in (
                None, "topic", "tag", "cluster"):
            return None
        return data

    def _see_freshness(self) -> Optional[Dict[str, Any]]:
        """None when this instance represents the on-disk file."""
        disk = _disk_sig(self.path) if self.path else None
        if disk != self._seen:
            return self._see_refusal(
                "STALE_OWNER_STATE",
                "this instance's nursery state is behind the owner "
                "file on disk; reload before querying so results "
                "represent the current generation")
        return None

    def query(self, *, owner: str, mode: str = "browse",
              status: Any = SEE_UNSET, term: Any = SEE_UNSET,
              page_size: Any = SEE_UNSET,
              topic: Any = SEE_UNSET, tag: Any = SEE_UNSET,
              cluster: Any = SEE_UNSET, group_by: Any = SEE_UNSET,
              cursor: Optional[str] = None) -> Dict[str, Any]:
        """One page of a browse (term="") or search over this store.

        With a cursor, the cursor's bound owner/mode/filter/sort/
        page-size govern. An argument the caller did not pass
        (SEE_UNSET) defers to the bound value; an argument passed
        explicitly must EQUAL the bound value — a changed filter,
        term, or page size refuses CURSOR_FILTER_MISMATCH, never a
        silent ignore (Director source review, PR #465). All
        refusals are typed dicts; nothing here writes.

        C5R.3 (Resolution 6): topic/tag/cluster filters and a
        group_by summary ride THIS service — never a separate
        organization database. Filters narrow the searched scope
        (total_searched reflects them, exactly as the status filter
        does). The topic filter and topic grouping use the
        EFFECTIVE topic: the stored topic when non-empty, else the
        explicit "unclassified" group — a read-only projection for
        legacy records; stored bytes are never rewritten by a view.
        Tag and cluster filters match stored values exactly under
        Unicode casefold. Grouping summarizes the matched set:
        topic and cluster groups partition it (every record in
        exactly one group, the unclassified / unset group always
        present); tag groups may overlap, so the response carries
        BOTH group_membership_total and group_distinct_total —
        overlap is disclosed, never forced into a partition.
        """
        last = None
        sig_bound = None
        if cursor is not None:
            data = self._see_cursor_decode(cursor)
            if data is None:
                return self._see_refusal(
                    "CURSOR_MALFORMED",
                    "cursor is not a well-formed SEE cursor; "
                    "restart the query from page 1")
            if data["owner"] != owner:
                return self._see_refusal(
                    "CURSOR_OWNER_MISMATCH",
                    "cursor was issued for a different owner; "
                    "cursors never cross owner boundaries")
            if data["mode"] != mode:
                return self._see_refusal(
                    "CURSOR_MALFORMED",
                    f"cursor was issued for {data['mode']}; continue "
                    f"with proposals {data['mode']} cursor:<token>")
            for passed, bound, field in (
                    (status, data["status"], "status filter"),
                    (term, data["term"], "search term"),
                    (page_size, data["size"], "page size"),
                    (topic, data.get("topic"), "topic filter"),
                    (tag, data.get("tag"), "tag filter"),
                    (cluster, data.get("cluster"), "cluster filter"),
                    (group_by, data.get("group"), "grouping")):
                if passed is not SEE_UNSET and passed != bound:
                    return self._see_refusal(
                        "CURSOR_FILTER_MISMATCH",
                        f"cursor was issued with {field} "
                        f"{bound!r}; continuing with {passed!r} "
                        "would silently change the query — restart "
                        "from page 1 with the new filter")
            status = data["status"]
            term = data["term"]
            page_size = data["size"]
            topic = data.get("topic")
            tag = data.get("tag")
            cluster = data.get("cluster")
            group_by = data.get("group")
            sig_bound = data["sig"]
            last = data["last"]
        else:
            if status is SEE_UNSET:
                status = None
            if term is SEE_UNSET:
                term = ""
            if page_size is SEE_UNSET:
                page_size = self.SEE_DEFAULT_PAGE
            if topic is SEE_UNSET:
                topic = None
            if tag is SEE_UNSET:
                tag = None
            if cluster is SEE_UNSET:
                cluster = None
            if group_by is SEE_UNSET:
                group_by = None
        if group_by is not None and group_by not in (
                "topic", "tag", "cluster"):
            return self._see_refusal(
                "GROUP_INVALID",
                f"group_by {group_by!r} is not an organization "
                "grouping (topic | tag | cluster)")
        if status is not None and status not in self.SEE_STATUSES:
            return self._see_refusal(
                "STATUS_UNSUPPORTED",
                f"status {status!r} is not an implemented nursery "
                "status (pending | confirmed | rejected); archived "
                "arrives with C5R.5")
        if (isinstance(page_size, bool)
                or not isinstance(page_size, int)
                or page_size < 1 or page_size > self.SEE_MAX_PAGE):
            return self._see_refusal(
                "PAGE_SIZE_INVALID",
                f"page size must be an integer 1..{self.SEE_MAX_PAGE} "
                f"(got {page_size!r}); sizes are never silently "
                "clamped")
        disk = _disk_sig(self.path) if self.path else None
        if cursor is not None and sig_bound != disk:
            # The between-pages generation change is the cursor's
            # own diagnosis and outranks the instance-level one.
            return self._see_refusal(
                "STALE_CURSOR",
                "the nursery changed since the previous page; "
                "restart the query from page 1")
        stale = self._see_freshness()
        if stale is not None:
            return stale
        scope = [p for p in self.proposals.values()
                 if status is None or p.status == status]
        # C5R.3 organization filters narrow the searched scope, so
        # total_searched reflects them exactly as it reflects the
        # status filter. Matching is exact-value under Unicode
        # casefold (the stored spelling is never rewritten).
        if topic is not None:
            want = str(topic).casefold()
            scope = [p for p in scope
                     if (p.topic or UNCLASSIFIED_TOPIC).casefold()
                     == want]
        if tag is not None:
            want = str(tag).casefold()
            scope = [p for p in scope
                     if any(t.casefold() == want
                            for t in (p.tags or []))]
        if cluster is not None:
            want = str(cluster).casefold()
            scope = [p for p in scope
                     if (p.cluster or "").casefold() == want]
        total_searched = len(scope)
        needle = (term or "").casefold()
        if needle:
            matched = [p for p in scope
                       if any(needle in str(v).casefold()
                              for v in self._see_searchable(p))]
        else:
            matched = list(scope)
        total_matches = len(matched)
        # C5R.3 grouping over the full matched set (before paging):
        # topic/cluster groups partition the set; tag groups may
        # overlap. Both membership and distinct totals are always
        # reported together so overlap can never masquerade as
        # inventory. The untagged pseudo-group (key None) keeps
        # tag coverage complete: every matched record is either in
        # at least one tag group or counted there.
        groups = None
        group_membership_total = None
        if group_by == "topic":
            counts: Dict[Any, int] = {UNCLASSIFIED_TOPIC: 0}
            for p in matched:
                key = p.topic or UNCLASSIFIED_TOPIC
                counts[key] = counts.get(key, 0) + 1
            groups = [{"key": k, "count": counts[k]}
                      for k in sorted(counts)]
            group_membership_total = sum(counts.values())
        elif group_by == "cluster":
            counts = {"": 0}
            for p in matched:
                counts[p.cluster] = counts.get(p.cluster, 0) + 1
            groups = [{"key": k, "count": counts[k]}
                      for k in sorted(counts)]
            group_membership_total = sum(counts.values())
        elif group_by == "tag":
            counts = {}
            untagged = 0
            for p in matched:
                if p.tags:
                    for t in p.tags:
                        counts[t] = counts.get(t, 0) + 1
                else:
                    untagged += 1
            # Membership counts EVERY group membership, including
            # the untagged pseudo-group below: memberships (5 in a
            # 2+2+1 overlap fixture) vs distinct records (4) is
            # exactly the overlap disclosure.
            group_membership_total = sum(counts.values()) + untagged
            groups = [{"key": k, "count": counts[k]}
                      for k in sorted(counts)]
            groups.append({"key": None, "count": untagged})
        matched.sort(key=lambda p: (p.created, p.id))
        if last is not None:
            bound = (last[0], last[1])
            matched = [p for p in matched
                       if (p.created, p.id) > bound]
        page = matched[:page_size]
        exhausted = len(matched) <= page_size
        next_cursor = None
        if not exhausted and page:
            tail = page[-1]
            next_cursor = self._see_cursor_encode({
                "v": 1, "owner": owner, "mode": mode, "sig": disk,
                "status": status, "term": term or "",
                "size": page_size,
                "topic": topic, "tag": tag, "cluster": cluster,
                "group": group_by,
                "last": [tail.created, tail.id],
            })
        return {
            "ok": True,
            "owner": owner,
            "mode": mode,
            "status_filter": status,
            "term": term or "",
            "sort": "created,id",
            "snapshot": disk,
            "total_inventory": len(self.proposals),
            "total_searched": total_searched,
            "total_matches": total_matches,
            "shown": len(page),
            "page_size": page_size,
            "items": [p.to_dict() for p in page],
            "next_cursor": next_cursor,
            "exhausted": exhausted,
            # C5R.3: organization view state rides every response —
            # the bound filters, the grouping (when requested) with
            # its dual totals, and how many matched records are
            # unseeded legacy records (seed_rule_version "") riding
            # the view projection rather than stored seeds.
            "topic_filter": topic,
            "tag_filter": tag,
            "cluster_filter": cluster,
            "group_by": group_by,
            "groups": groups,
            "group_membership_total": group_membership_total,
            "group_distinct_total": (
                total_matches if group_by is not None else None),
            "unseeded_in_scope": sum(
                1 for p in matched if not p.seed_rule_version),
        }

    def fetch_many(self, ids: List[str]) -> Dict[str, Any]:
        """Direct ID-set retrieval from this owner store (AC-2.4).

        Found records return in input order; duplicate input IDs
        collapse to their first occurrence (stated in `policy`);
        missing IDs are named individually. No G-11 path, no cap.
        """
        stale = self._see_freshness()
        if stale is not None:
            return stale
        seen: set = set()
        found: List[Dict[str, Any]] = []
        missing: List[str] = []
        collapsed = 0
        for pid in ids:
            if pid in seen:
                collapsed += 1
                continue
            seen.add(pid)
            rec = self.proposals.get(pid)
            if rec is None:
                missing.append(pid)
            else:
                found.append(rec.to_dict())
        return {
            "ok": True,
            "requested": len(ids),
            "found": found,
            "missing": missing,
            "duplicates_collapsed": collapsed,
            "policy": "input order; duplicate IDs collapse to "
                      "first occurrence",
        }

    def save(self, *, _fail_at: Optional[str] = None) -> str:
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
        # C5R.3: the organization edit-receipt section rides the same
        # atomic write under the same arrangement (empty until the
        # Phase 2 edit door appends receipts).
        payload[EDIT_RECEIPT_SECTION_KEY] = {
            op_id: dict(rec)
            for op_id, rec in self.organization_edit_receipts.items()
        }
        blob = atomic_write_json(self.path, payload, _fail_at=_fail_at)
        self._seen = hashlib.sha256(blob).hexdigest()
        # C5R.3 (Resolution 3): the canonical post-save digest is
        # RETURNED to the caller — it is never embedded in the file
        # it describes.
        return self._seen

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
        staged_edit_receipts: Dict[str, Dict[str, Any]] = {}
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
                # C5R.3: the reserved organization edit-receipt
                # section is staged separately under the same
                # arrangement; it is never mistaken for a proposal.
                if k == EDIT_RECEIPT_SECTION_KEY:
                    if not isinstance(v, dict):
                        raise NurseryLoadError(
                            f"nursery file {os.path.basename(path)} has a malformed "
                            f"{EDIT_RECEIPT_SECTION_KEY} section (not an object)"
                        )
                    for op_id, rec in v.items():
                        if not isinstance(op_id, str) or not isinstance(rec, dict):
                            raise NurseryLoadError(
                                f"nursery file {os.path.basename(path)} has a malformed "
                                f"organization edit receipt for {op_id!r}"
                            )
                    staged_edit_receipts = {
                        op_id: dict(rec) for op_id, rec in v.items()}
                    continue
                if not isinstance(v, dict):
                    raise NurseryLoadError(
                        f"nursery file {os.path.basename(path)} has an invalid proposal record for {k!r}"
                    )
                rec = Proposal(**v)
                _validate_loaded_organization(k, rec, path)
                staged[k] = rec
        except NurseryLoadError:
            raise
        except Exception as exc:
            raise NurseryLoadError(
                f"nursery file {os.path.basename(path)} has an invalid proposal record: {exc}"
            ) from exc
        # Only now apply: nothing partial can escape.
        n.proposals = staged
        n.conflict_dispositions = staged_dispositions
        n.organization_edit_receipts = staged_edit_receipts
        n._seen = hashlib.sha256(blob).hexdigest()
        return n
