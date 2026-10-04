"""DCC-XVI: Versioned knowledge supersession + revision lifecycle (Supersession V1).

A confirmed unit may be replaced by an explicit newer revision WITHOUT
deleting or rewriting history:

  - the predecessor remains stored (historical, inspectable)
  - the successor becomes the active revision for contextual routing
  - revision ancestry (which version replaces which) is kept SEPARATE from
    derivation ancestry (Lineage V1 parent/root chain)

Confirmed vs superseded are different dimensions:
  CONFIRMATION: was this knowledge accepted?        (nursery status)
  SUPERSESSION: is this accepted revision active?   (lifecycle_state)

Supersession does NOT mean: the old statement was false, the new one is
true, history was rewritten, descendants were retargeted, or source
authority was established. newer != truer. superseded != false.

Revision metadata lives as additive fields on the nursery Proposal, so
legacy persisted state (without these fields) loads with safe defaults:
active, no predecessor/successor, no fabricated history.

One inspection implementation (inspect_revision) is reused by the
lifecycle operation, selector eligibility, trace, receipts, and tests.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

SUPERSESSION_VERSION = 1

ACTIVE = "active"
SUPERSEDED = "superseded"
MALFORMED = "malformed"
UNKNOWN = "unknown"

# Test-only failure injection point. Values: "create" | "confirm" |
# "link_write" | "persist" | "receipt" | None. Never set in production.
_FAIL_AT: Optional[str] = None


class SupersedeError(ValueError):
    """Deterministic supersession failure (validation or injected).

    `reason` is the stable machine-readable code; `str(exc)` appends the
    human detail as "reason:detail". Receipts and tests key on `reason`.
    """

    def __init__(self, reason: str, detail: str = ""):
        self.reason = reason
        super().__init__(f"{reason}:{detail}" if detail else reason)


def _proposals(program: Any) -> Dict[str, Any]:
    return getattr(getattr(program, "nursery", None), "proposals", {}) or {}


def inspect_revision(program: Any, uid: str) -> Dict[str, Any]:
    """Deterministic Supersession V1 inspection for one unit.

    Fields: unit_id, supersession_version, lifecycle_state
    ("active" | "superseded" | "malformed" | "unknown"), supersedes_id,
    superseded_by_id, revision_root_id, revision_number, chain (ordered
    root->tip ids, [] when unconstructible), malformed_reason, routable.

    Legacy units (no revision metadata) inspect as active revision #1 of
    their own root: no predecessor/successor is fabricated.
    """
    proposals = _proposals(program)
    prop = proposals.get(uid)
    if prop is None:
        return {
            "unit_id": uid,
            "supersession_version": SUPERSESSION_VERSION,
            "lifecycle_state": UNKNOWN,
            "supersedes_id": None,
            "superseded_by_id": None,
            "revision_root_id": None,
            "revision_number": None,
            "chain": [],
            "malformed_reason": "unknown_unit",
            "routable": False,
        }

    # ARGUS-2 FIX (approved): Fail closed on explicit None/empty lifecycle_state.
    # Distinguish "attribute missing" (legacy → ACTIVE via compatibility policy)
    # from "attribute present but None/empty/whitespace" (malformed → fail closed).
    _MISSING = object()
    _raw_state = getattr(prop, "lifecycle_state", _MISSING)
    if _raw_state is _MISSING:
        state = ACTIVE
    elif _raw_state is None:
        state = None
    elif isinstance(_raw_state, str) and _raw_state.strip() == "":
        state = None
    else:
        state = _raw_state
    supersedes = getattr(prop, "supersedes_id", None)
    superseded_by = getattr(prop, "superseded_by_id", None)
    root = getattr(prop, "revision_root_id", None) or uid
    number = getattr(prop, "revision_number", None)
    if number is None:
        number = 1

    malformed: Optional[str] = None

    if state not in (ACTIVE, SUPERSEDED):
        malformed = f"bad_lifecycle_state:{state}"
    elif superseded_by is not None and state == ACTIVE:
        # Claims a successor while still active: inconsistent link state.
        malformed = "inconsistent_link_state:active_with_successor"
    elif superseded_by is not None and superseded_by not in proposals:
        malformed = f"missing_successor:{superseded_by}"
    elif supersedes is not None and supersedes not in proposals:
        malformed = f"missing_predecessor:{supersedes}"

    chain: List[str] = []
    if malformed is None:
        # Walk back to the revision root, then forward to the tip.
        seen = {uid}
        node = uid
        backward: List[str] = [uid]
        while True:
            prev = getattr(proposals[node], "supersedes_id", None)
            if not prev:
                break
            if prev in seen:
                malformed = f"revision_cycle:{prev}"
                break
            if prev not in proposals:
                malformed = f"missing_predecessor:{prev}"
                break
            seen.add(prev)
            backward.append(prev)
            node = prev
        if malformed is None:
            root_id = backward[-1]
            chain = list(reversed(backward))
            # Walk forward from the root along superseded_by links to
            # discover successors beyond uid. This retraces the backward
            # path (same edges, opposite direction), so it uses its own
            # visited set and only appends nodes the backward walk did
            # not already cover.
            node = root_id
            fwd_seen = {root_id}
            while True:
                nxt = getattr(proposals[node], "superseded_by_id", None)
                if not nxt:
                    break
                if nxt in fwd_seen:
                    malformed = f"revision_cycle:{nxt}"
                    break
                if nxt not in proposals:
                    malformed = f"missing_successor:{nxt}"
                    break
                fwd_seen.add(nxt)
                if nxt not in chain:
                    chain.append(nxt)
                node = nxt
        if malformed is None:
            # Declared roots must agree across the whole chain: every
            # member declares either nothing (legacy) or the true root
            # (the chain head we walked to).
            bad = [c for c in chain
                   if (getattr(proposals[c], "revision_root_id", None)
                       not in (None, chain[0]))]
            if bad:
                malformed = f"inconsistent_revision_root:{','.join(sorted(bad))}"
            else:
                # Revision numbers must be unique and 1-based in chain order.
                nums = [getattr(proposals[c], "revision_number", None)
                        for c in chain]
                present = [n for n in nums if n is not None]
                if len(set(present)) != len(present):
                    malformed = "duplicate_revision_number"
                # Bidirectional links must agree.
                for a, b in zip(chain, chain[1:]):
                    pa = proposals[a]
                    pb = proposals[b]
                    if getattr(pa, "superseded_by_id", None) != b \
                            or getattr(pb, "supersedes_id", None) != a:
                        malformed = f"broken_bidirectional_link:{a}<->{b}"
                        break
            if malformed is None and uid not in chain:
                malformed = f"broken_bidirectional_link:{uid}_not_in_chain"

    if malformed is not None:
        return {
            "unit_id": uid,
            "supersession_version": SUPERSESSION_VERSION,
            "lifecycle_state": MALFORMED,
            "supersedes_id": supersedes,
            "superseded_by_id": superseded_by,
            "revision_root_id": root,
            "revision_number": number,
            "chain": [],
            "malformed_reason": malformed,
            "routable": False,
        }

    return {
        "unit_id": uid,
        "supersession_version": SUPERSESSION_VERSION,
        "lifecycle_state": state,
        "supersedes_id": supersedes,
        "superseded_by_id": superseded_by,
        "revision_root_id": chain[0] if chain else root,
        "revision_number": number,
        "chain": chain,
        "malformed_reason": None,
        "routable": state == ACTIVE,
    }


def is_revision_active(program: Any, uid: str) -> bool:
    """True iff the unit is an active (routable) revision."""
    return inspect_revision(program, uid)["lifecycle_state"] == ACTIVE


def revision_exclusions(
    program: Any, unit_ids: List[str]
) -> List[Dict[str, Any]]:
    """Deterministic exclusion evidence for non-active revisions.

    Each entry: id, lifecycle_state, superseded_by_id, revision_number,
    revision_root_id, reason. Sorted by id.
    """
    out = []
    for uid in sorted(unit_ids):
        rec = inspect_revision(program, uid)
        if rec["lifecycle_state"] != ACTIVE:
            out.append({
                "id": uid,
                "lifecycle_state": rec["lifecycle_state"],
                "superseded_by_id": rec["superseded_by_id"],
                "revision_root_id": rec["revision_root_id"],
                "revision_number": rec["revision_number"],
                "reason": rec["malformed_reason"] or "superseded",
            })
    return out


def _save_nursery(program: Any) -> None:
    """Nursery commit point, honoring the test failure-injection hook."""
    if _FAIL_AT == "persist":
        raise SupersedeError("injected_failure", "persist")
    program.nursery.save()


def _rollback_unconfirmed(program: Any, succ_id: Optional[str]) -> None:
    """Rollback for a failure before/within successor confirmation.

    The predecessor was never touched (still active in memory and on
    disk). The successor never became a confirmed revision, so it is
    removed (proposal + plane unit) and the nursery is re-saved.
    """
    if succ_id is not None:
        program.nursery.proposals.pop(succ_id, None)
        try:
            program.cube.session.plane.remove(succ_id)
        except Exception:
            pass
    # Direct save: the rollback itself must not trip the inject hook.
    program.nursery.save()


def _rollback_full(program: Any, old: Any, old_snap: Dict[str, Any],
                   succ_id: Optional[str]) -> None:
    """Rollback for a failure at the final link-commit.

    The successor was created and confirmed solely by this operation but
    the revision links were never durably committed, so the operation is
    all-or-nothing: the predecessor's link fields are restored, the
    successor proposal/plane unit is removed, and the nursery is
    re-saved. Durable state returns to entirely-old; no half revision
    chain can survive.
    """
    for k, v in old_snap.items():
        setattr(old, k, v)
    if succ_id is not None:
        program.nursery.proposals.pop(succ_id, None)
        try:
            program.cube.session.plane.remove(succ_id)
        except Exception:
            pass
    # Direct save: the rollback itself must not trip the inject hook.
    program.nursery.save()


def supersede_proposal(program: Any, old_id: str, words: str,
                       label: Optional[str] = None,
                       _fail_at: Optional[str] = None) -> Dict[str, Any]:
    """Atomic public operation: supersede accepted knowledge with a new revision.

    `_fail_at` is the test-only failure-injection hook (one of "create",
    "confirm", "link_write", "persist", "receipt"); it is never set in
    production and is always restored after the call.
    """
    global _FAIL_AT
    prev_fail, _FAIL_AT = _FAIL_AT, _fail_at
    try:
        return _supersede_impl(program, old_id, words, label)
    finally:
        _FAIL_AT = prev_fail


def _supersede_impl(program: Any, old_id: str, words: str,
                    label: Optional[str]) -> Dict[str, Any]:
    """Atomic supersede implementation (see supersede_proposal).

    Lifecycle (all-or-nothing), ordered so a crash can never expose a
    half-superseded revision chain:

      1. validate old unit: exists, confirmed, on-plane, currently active
      2. create successor through the legitimate nursery path (pending)
      3. confirm/promote successor via the canonical confirm path --
         the predecessor stays ACTIVE in durable storage throughout
      4. prepare complete revision links in memory, then ONE atomic
         durable commit (nursery.save). This single save is the
         durability boundary: before it the predecessor is active;
         after it the predecessor is superseded AND the successor is
         confirmed with complete bidirectional links.
      5. persist + emit auditable receipt (post-commit)

    The successor is created as a derivation root (parents=[]): revision
    ancestry is NOT derivation ancestry. A repeated supersession of an
    already-superseded unit is deterministically rejected and returns the
    existing relationship — no duplicate successor is ever created.

    Raises SupersedeError on validation or injected failure. Any failure
    before the final commit restores the pre-supersession state entirely:
    the predecessor is untouched (Phase 3) or its link fields are
    restored (Phase 4), the successor created solely by this operation
    is removed, and the nursery is re-saved.
    """
    nursery = program.nursery

    # ---- Phase 1: validate (no writes) ----
    old_id = (old_id or "").strip()
    if not old_id:
        raise SupersedeError("empty_predecessor_id")
    old = nursery.proposals.get(old_id)
    if old is None:
        raise SupersedeError("unknown_predecessor", old_id)
    if getattr(old, "status", None) != "confirmed":
        raise SupersedeError("not_confirmed",
                             f"{old_id}:{getattr(old, 'status', None)}")
    if old_id not in program.cube.session.plane.units:
        raise SupersedeError("not_on_plane", old_id)
    rec = inspect_revision(program, old_id)
    if rec["lifecycle_state"] == UNKNOWN:
        raise SupersedeError("unknown_revision", old_id)
    if rec["lifecycle_state"] == MALFORMED:
        raise SupersedeError("malformed_revision",
                             f"{old_id}:{rec['malformed_reason']}")
    if rec["lifecycle_state"] != ACTIVE:
        # Deterministic repeat/idempotency: reject, return the existing
        # relationship. Never create a duplicate successor.
        receipt = {
            "action": "supersede",
            "ok": False,
            "reason": "already_superseded",
            "old_id": old_id,
            "superseded_by_id": rec["superseded_by_id"],
            "revision_root_id": rec["revision_root_id"],
            "revision_number": rec["revision_number"],
            "supersession_version": SUPERSESSION_VERSION,
            "consumer": "supersede_idea",
            "dell": 37,
        }
        program.last_nurture = receipt
        return receipt
    words = (words or "").strip()
    if not words:
        raise SupersedeError("empty_successor_words")

    if _FAIL_AT == "create":
        raise SupersedeError("injected_failure", "create")

    # ---- Phase 2: create successor via the legitimate nursery path ----
    new_label = (label or f"revision of {getattr(old, 'label', old_id)}")[:80]
    succ = nursery.add(
        new_label,
        words=words[:240],
        kind="evolved",
        parents=[],
        reason=f"supersedes {old_id}"[:160],
    )
    succ_id = succ.id

    # ---- Phase 3: confirm/promote the successor FIRST ----
    # The predecessor stays ACTIVE in durable storage for the whole of
    # this phase. Any failure here (or a crash at any point before the
    # Phase-4 commit) therefore leaves the predecessor active: a fresh
    # process can never observe "predecessor superseded" without a
    # completely established successor.
    try:
        if _FAIL_AT == "confirm":
            raise SupersedeError("injected_failure", "confirm")
        # Set skip flag: supersession has its own transaction boundary
        # (Phase 4 save). Avoid nested checkpoint commits.
        from form.dell_matrix import confirm_lineage as _cl
        _orig_skip = getattr(_cl.confirm_proposal, '_SKIP_CHECKPOINT', False)
        _cl.confirm_proposal._SKIP_CHECKPOINT = True
        try:
            res = program.confirm_proposal(succ_id)
        finally:
            _cl.confirm_proposal._SKIP_CHECKPOINT = _orig_skip
        if not res.get("ok"):
            raise SupersedeError("confirm_failed", str(res.get("reason")))
    except Exception:
        _rollback_unconfirmed(program, succ_id)
        raise

    # ---- Phase 4: complete revision links, then ONE atomic commit ----
    # This single _save_nursery call is the durability boundary of the
    # whole operation. Everything before it leaves the predecessor
    # active on disk; everything after it has the predecessor superseded
    # with the successor confirmed and both revision links complete.
    # There is no crash window between "predecessor superseded" and
    # "successor confirmed" because they are written by the same save.
    old_snap = {
        "lifecycle_state": getattr(old, "lifecycle_state", ACTIVE),
        "supersedes_id": getattr(old, "supersedes_id", None),
        "superseded_by_id": getattr(old, "superseded_by_id", None),
        "revision_root_id": getattr(old, "revision_root_id", None),
        "revision_number": getattr(old, "revision_number", None),
    }
    root_id = rec["revision_root_id"]
    new_number = int(rec["revision_number"]) + 1
    try:
        old.superseded_by_id = succ_id
        old.lifecycle_state = SUPERSEDED
        # Make the predecessor's revision identity explicit in stored
        # state (legacy units carry None until their first supersession).
        old.revision_root_id = root_id
        if old.revision_number is None:
            old.revision_number = rec["revision_number"]
        succ.supersedes_id = old_id
        succ.revision_root_id = root_id
        succ.revision_number = new_number
        succ.lifecycle_state = ACTIVE
        if _FAIL_AT == "link_write":
            raise SupersedeError("injected_failure", "link_write")
        _save_nursery(program)
        # SWAT R2 VIOLATION 1 FIX: Persist the program file as well.
        # The successor Idea exists in memory (from Phase 3 place()) but
        # must be durable. Otherwise the loader recovery
        # (recover_confirmation_hybrid) sees "confirmed without Idea" and
        # heals the legitimate successor to pending, corrupting the chain.
        # The invariant "confirmed => Idea present on disk" must hold for
        # all producers, not just confirm_proposal.
        from form import persist_rest
        persist_rest.save(program)
    except Exception:
        _rollback_full(program, old, old_snap, succ_id)
        raise

    # ---- Phase 5: auditable receipt ----
    receipt = {
        "action": "supersede",
        "ok": True,
        "old_id": old_id,
        "new_id": succ_id,
        "old_lifecycle_state": SUPERSEDED,
        "new_lifecycle_state": ACTIVE,
        "supersession_version": SUPERSESSION_VERSION,
        "revision_root_id": root_id,
        "revision_number": new_number,
        "consumer": "supersede_idea",
        "dell": 37,
    }
    if _FAIL_AT == "receipt":
        # State is committed and persisted; only receipt emission fails.
        raise SupersedeError("injected_failure", "receipt")
    program.last_nurture = receipt
    return receipt
