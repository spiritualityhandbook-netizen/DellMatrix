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

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# Sentinel for "argument not passed" in the SEE query API. A
# continuation call must distinguish an absent filter argument
# (the cursor's bound value governs) from an explicitly passed
# one (which must equal the bound value or refuse loudly) —
# Director source review on PR #465, 2026-11-16.
SEE_UNSET = object()


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
        pid = _slug(label, seed)
        # avoid exact id collision
        if pid in self.proposals:
            pid = pid + "_" + str(len(self.proposals))
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
              cursor: Optional[str] = None) -> Dict[str, Any]:
        """One page of a browse (term="") or search over this store.

        With a cursor, the cursor's bound owner/mode/filter/sort/
        page-size govern. An argument the caller did not pass
        (SEE_UNSET) defers to the bound value; an argument passed
        explicitly must EQUAL the bound value — a changed filter,
        term, or page size refuses CURSOR_FILTER_MISMATCH, never a
        silent ignore (Director source review, PR #465). All
        refusals are typed dicts; nothing here writes.
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
                    (page_size, data["size"], "page size")):
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
            sig_bound = data["sig"]
            last = data["last"]
        else:
            if status is SEE_UNSET:
                status = None
            if term is SEE_UNSET:
                term = ""
            if page_size is SEE_UNSET:
                page_size = self.SEE_DEFAULT_PAGE
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
        total_searched = len(scope)
        needle = (term or "").casefold()
        if needle:
            matched = [p for p in scope
                       if any(needle in str(v).casefold()
                              for v in self._see_searchable(p))]
        else:
            matched = list(scope)
        total_matches = len(matched)
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
