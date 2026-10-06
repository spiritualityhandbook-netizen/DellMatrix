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
# WO-5.2: FADED is a valid revision state (participation dimension).
# A faded idea remains part of its revision chain; fading affects
# participation, not revision identity.
FADED = "faded"
MALFORMED = "malformed"
UNKNOWN = "unknown"

# Test-only failure injection point. Values: "create" | "confirm" |
# "link_write" | "persist" | "receipt" | None. Never set in production.
_FAIL_AT: Optional[str] = None


class SupersedeError(ValueError):
    """Deterministic supersession failure (validation or injected).

    `reason` is the stable machine-readable code; `str(exc)` appends the
    human detail as "reason:detail". Receipts and tests key on `reason`.
    `details` carries structured failure context (e.g., incomplete
    compensation/rollback details) for observability.
    """

    def __init__(self, reason: str, detail: str = "",
                 details: dict = None):
        self.reason = reason
        self.details = details or {}
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

    Director 2026-10-05: FADED is NOT a revision state. Revision is ACTIVE
    or SUPERSEDED only. Participation (including faded) is a separate
    dimension determined via is_participating(). A stored lifecycle_state
    of FADED is malformed revision data.
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

    # Director 2026-10-05: FADED is NOT a revision state. Revision is
    # ACTIVE or SUPERSEDED only. Fading is a participation dimension,
    # determined separately via is_participating(). A proposal with
    # lifecycle_state=FADED has malformed revision data.
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


def _rollback_unconfirmed(program: Any, succ_id: Optional[str]) -> Dict[str, Any]:
    """Rollback for a failure before/within successor confirmation.

    The predecessor was never touched (still active in memory and on
    disk). The successor never became a confirmed revision, so it is
    removed (proposal + plane unit + spatial entries) and the nursery is
    re-saved.

    Director 2026-10-05 (enclosing rollback): Returns status dict.
    Verifies successor artifacts are absent before saving. Unresolved
    restoration returns ok=False with named failures; the caller must
    retain evidence (journal) and report observably.
    """
    failures = []
    removed = []
    if succ_id is not None:
        # Remove successor proposal
        try:
            program.nursery.proposals.pop(succ_id, None)
            removed.append("proposal")
        except Exception as e:
            failures.append(f"proposal:{type(e).__name__}")
        # Remove plane unit
        try:
            program.cube.session.plane.remove(succ_id)
            removed.append("unit")
        except Exception as e:
            failures.append(f"unit:{type(e).__name__}")
        # Remove spatial entries (velocities, placements)
        try:
            spatial = program.spatial
            if hasattr(spatial, 'velocities'):
                try:
                    spatial.velocities.pop(succ_id, None)
                    removed.append("velocities")
                except Exception as e:
                    failures.append(f"velocities:{type(e).__name__}")
            if hasattr(spatial, 'placements'):
                try:
                    spatial.placements.pop(succ_id, None)
                    removed.append("placements")
                except Exception as e:
                    failures.append(f"placements:{type(e).__name__}")
        except Exception as e:
            failures.append(f"spatial_access:{type(e).__name__}")
        # Verify: successor artifacts must be absent
        # (Director: unverifiable cleanup is incomplete; named failures,
        # not suppressed exceptions)
        try:
            if succ_id in program.nursery.proposals:
                failures.append("verify:proposal_still_present")
        except Exception as e:
            failures.append(f"verify:proposal_check:{type(e).__name__}")
        try:
            if succ_id in program.cube.session.plane.units:
                failures.append("verify:unit_still_present")
        except Exception as e:
            failures.append(f"verify:unit_check:{type(e).__name__}")
        try:
            spatial = program.spatial
            if hasattr(spatial, 'velocities'):
                try:
                    if succ_id in spatial.velocities:
                        failures.append("verify:velocities_still_present")
                except Exception as e:
                    failures.append(f"verify:velocities_check:{type(e).__name__}")
            if hasattr(spatial, 'placements'):
                try:
                    if succ_id in spatial.placements:
                        failures.append("verify:placements_still_present")
                except Exception as e:
                    failures.append(f"verify:placements_check:{type(e).__name__}")
        except Exception as e:
            failures.append(f"verify:spatial_check:{type(e).__name__}")
    # Only save if verification passed; otherwise the saved state would
    # claim restoration that didn't happen.
    if failures:
        return {"ok": False, "failures": failures, "removed": removed}
    # Direct save: the rollback itself must not trip the inject hook.
    try:
        program.nursery.save()
        removed.append("nursery_saved")
    except Exception as e:
        failures.append(f"nursery_save:{type(e).__name__}")
        return {"ok": False, "failures": failures, "removed": removed}
    # Also save Program: the plane.remove above modified in-memory state.
    # Without this, durable Program retains the successor Idea (rollback gap).
    # Propagate failure: incomplete rollback must not be silently accepted.
    try:
        from form import persist_rest
        persist_rest.save(program)
        removed.append("program_saved")
    except Exception as e:
        failures.append(f"program_save:{type(e).__name__}")
        return {"ok": False, "failures": failures, "removed": removed}
    return {"ok": True, "failures": [], "removed": removed}


def _rollback_full(program: Any, old: Any, old_snap: Dict[str, Any],
                   succ_id: Optional[str]) -> Dict[str, Any]:
    """Rollback for a failure at the final link-commit.

    The successor was created and confirmed solely by this operation but
    the revision links were never durably committed, so the operation is
    all-or-nothing: the predecessor's link fields are restored, the
    successor proposal/plane unit/spatial entries are removed, and the
    nursery is re-saved. Durable state returns to entirely-old; no half
    revision chain can survive.

    Director 2026-10-05 (enclosing rollback): Returns status dict.
    Verifies predecessor restoration and successor removal before saving.
    Unresolved restoration returns ok=False; caller must retain evidence.
    """
    failures = []
    removed = []
    # Restore predecessor link fields
    try:
        for k, v in old_snap.items():
            setattr(old, k, v)
        removed.append("predecessor_restored")
    except Exception as e:
        failures.append(f"predecessor_restore:{type(e).__name__}")
    # Verify predecessor restoration
    try:
        for k, v in old_snap.items():
            if getattr(old, k, None) != v:
                failures.append(f"verify:predecessor_{k}_not_restored")
    except Exception as e:
        failures.append(f"verify:predecessor_check:{type(e).__name__}")
    # Remove successor artifacts
    if succ_id is not None:
        try:
            program.nursery.proposals.pop(succ_id, None)
            removed.append("proposal")
        except Exception as e:
            failures.append(f"proposal:{type(e).__name__}")
        try:
            program.cube.session.plane.remove(succ_id)
            removed.append("unit")
        except Exception as e:
            failures.append(f"unit:{type(e).__name__}")
        try:
            spatial = program.spatial
            if hasattr(spatial, 'velocities'):
                try:
                    spatial.velocities.pop(succ_id, None)
                    removed.append("velocities")
                except Exception as e:
                    failures.append(f"velocities:{type(e).__name__}")
            if hasattr(spatial, 'placements'):
                try:
                    spatial.placements.pop(succ_id, None)
                    removed.append("placements")
                except Exception as e:
                    failures.append(f"placements:{type(e).__name__}")
        except Exception as e:
            failures.append(f"spatial_access:{type(e).__name__}")
        # Verify successor absent
        try:
            if succ_id in program.nursery.proposals:
                failures.append("verify:proposal_still_present")
        except Exception as e:
            failures.append(f"verify:proposal_check:{type(e).__name__}")
        try:
            if succ_id in program.cube.session.plane.units:
                failures.append("verify:unit_still_present")
        except Exception as e:
            failures.append(f"verify:unit_check:{type(e).__name__}")
    # Only save if verification passed
    if failures:
        return {"ok": False, "failures": failures, "removed": removed}
    try:
        program.nursery.save()
        removed.append("nursery_saved")
    except Exception as e:
        failures.append(f"nursery_save:{type(e).__name__}")
        return {"ok": False, "failures": failures, "removed": removed}
    try:
        from form import persist_rest
        persist_rest.save(program)
        removed.append("program_saved")
    except Exception as e:
        failures.append(f"program_save:{type(e).__name__}")
        return {"ok": False, "failures": failures, "removed": removed}
    return {"ok": True, "failures": [], "removed": removed}


def supersede_proposal(program: Any, old_id: str, words: str,
                       label: Optional[str] = None,
                       _fail_at: Optional[str] = None,
                       _producer: str = "unknown",
                       _review_context: dict = None) -> Dict[str, Any]:
    """Atomic public operation: supersede accepted knowledge with a new revision.

    `_fail_at` is the test-only failure-injection hook (one of "create",
    "replace", "confirm", "link", "cleanup").

    Director 2026-10-05: The supersession must be authorized via the
    acceptance policy BEFORE creating successor state or writing intent.
    The internal confirm uses the verified authorization (not a bypass).
    """
    global _FAIL_AT
    prev_fail, _FAIL_AT = _FAIL_AT, _fail_at
    try:
        return _supersede_impl(program, old_id, words, label,
                                _producer=_producer,
                                _review_context=_review_context)
    finally:
        _FAIL_AT = prev_fail


def _supersede_impl(program: Any, old_id: str, words: str,
                    label: Optional[str],
                    _producer: str = "unknown",
                    _review_context: dict = None) -> Dict[str, Any]:
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

    # Director 2026-10-05 (whole-circuit): Authorize BEFORE creating
    # successor state or writing intent.
    #
    # Binding: predecessor version + proposed successor data. The approval
    # must be an ISSUED approval (operation="supersede", target=old_id)
    # whose data hash covers the predecessor's canonical version and the
    # proposed successor's label/words; or a session opt-in for the
    # producer. No direct policy._opt_ins inspection (use is_opted_in).
    #
    # The successor's confirmation authority is DERIVED from this approved
    # enclosing operation via policy.derive_approval — recorded, bound,
    # revocable, session-scoped. Not a general bypass.
    from form.dell_matrix.acceptance_policy import canonical_hash
    policy = getattr(program, "acceptance_policy", None)
    if policy is None:
        raise SupersedeError("acceptance_policy_missing")
    # Expected binding hash: predecessor canonical version + successor data.
    # Effective label matches successor creation (line ~456) and
    # Program.make_supersede_context: explicit label, else "revision of...".
    _old_prop = program.nursery.proposals.get(old_id)
    _eff_label = label or f"revision of {getattr(_old_prop, 'label', old_id)}"
    _pred_hash = program.acceptance_data_hash(old_id, "supersede")
    _succ_data_hash = canonical_hash({"label": _eff_label, "words": words or ""})
    _binding_hash = canonical_hash(
        {"predecessor": _pred_hash, "successor": _succ_data_hash})
    _source_approval_id = None
    _source_opt_in = None
    _reviewer = _producer
    if isinstance(_review_context, dict) and _review_context.get("approval_id"):
        _decision = policy.check(_producer, old_id, _review_context,
                                 proposal_version=_binding_hash,
                                 operation="supersede")
        if _decision.get("allowed"):
            _source_approval_id = _decision.get("approval_id")
            _reviewer = _review_context.get("reviewer") or _producer
    if _source_approval_id is None and policy.is_opted_in(_producer):
        _source_opt_in = _producer
    if _source_approval_id is None and _source_opt_in is None:
        raise SupersedeError(
            "acceptance_policy_denied: supersede operation not authorized "
            f"(producer={_producer!r}, old_id={old_id!r})"
        )
    # Carry the authorization source for the derived successor confirm.
    _auth_source = {"approval_id": _source_approval_id,
                    "opt_in": _source_opt_in, "reviewer": _reviewer}

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
    #
    # R3-COMPLETION-GATE: Write supersession intent journal BEFORE any
    # writes. This is the ENCLOSING transaction. Do not publish independent
    # successor acceptance and clear its recovery evidence before the
    # supersession outcome is recoverable.
    from form.mandell.core_i_recovery import (
        write_supersede_intent, clear_supersede_intent
    )
    write_supersede_intent(program.owner, old_id, succ_id)
    try:
        if _FAIL_AT == "confirm":
            raise SupersedeError("injected_failure", "confirm")
        # Set skip flags: supersession has its own transaction boundary.
        # _SKIP_CHECKPOINT avoids nested checkpoint commits.
        # _SKIP_JOURNAL prevents confirm_proposal from writing/clearing
        # its own journal; the supersession journal is the authority.
        from form.dell_matrix import confirm_lineage as _cl
        _orig_skip = getattr(_cl.confirm_proposal, '_SKIP_CHECKPOINT', False)
        _orig_skip_j = getattr(_cl.confirm_proposal, '_SKIP_JOURNAL', False)
        _cl.confirm_proposal._SKIP_CHECKPOINT = True
        _cl.confirm_proposal._SKIP_JOURNAL = True
        try:
            # Director 2026-10-05 (whole-circuit): derive the successor's
            # confirmation authority from the approved enclosing operation.
            # Recorded, bound to the successor's actual data, revocable,
            # session-scoped — not a general bypass.
            _policy = getattr(program, "acceptance_policy", None)
            _derived = _policy.derive_approval(
                source_approval_id=_auth_source["approval_id"],
                source_opt_in=_auth_source["opt_in"],
                operation="confirm",
                target=succ_id,
                reviewer=_auth_source["reviewer"],
                data=program._acceptance_data_for(succ_id, "confirm"),
                relationship={"type": "supersede_successor",
                              "predecessor_id": old_id},
                note="supersede successor confirm",
            )
            res = program.confirm_proposal(
                succ_id,
                _producer=_producer,
                _review_context=_derived["context"],
                _operation="confirm",
            )
        finally:
            _cl.confirm_proposal._SKIP_CHECKPOINT = _orig_skip
            _cl.confirm_proposal._SKIP_JOURNAL = _orig_skip_j
        if not res.get("ok"):
            # Director 2026-10-05: Carry incomplete-compensation details
            # through confirm_failed. If the successor confirmation itself
            # reported incomplete compensation, preserve those details.
            _comp_detail = res.get("compensation")
            _comp_failures = res.get("compensation_failures", [])
            raise SupersedeError(
                "confirm_failed", str(res.get("reason")),
                {"compensation": _comp_detail,
                 "compensation_failures": _comp_failures})
    except Exception as e:
        # Director 2026-10-05 (enclosing rollback): Verify restoration
        # before clearing intent. Unresolved restoration retains evidence.
        _rb = _rollback_unconfirmed(program, succ_id)
        if not _rb.get("ok"):
            # Incomplete rollback: retain journal, attach details to
            # the exception so the failure remains observable.
            if isinstance(e, SupersedeError):
                e.details = getattr(e, 'details', {}) or {}
                e.details["rollback"] = "incomplete"
                e.details["rollback_failures"] = _rb.get("failures", [])
                e.details["rollback_removed"] = _rb.get("removed", [])
            # Do NOT clear intent; evidence retained for recovery.
        else:
            # Complete rollback: clear supersession journal (operation aborted)
            try:
                clear_supersede_intent(program.owner)
            except Exception:
                pass
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
        # R3: Phase 3 (confirm_proposal with skip) already saved both nursery
        # and program files with the successor Idea durable. Phase 4 only
        # updates predecessor links in the nursery. No program save needed.
        # R3-COMPLETION-GATE: Clear supersession journal ONLY after the
        # complete transition is durable. The successor's acceptance is
        # now recoverable as part of the supersession outcome.
        clear_supersede_intent(program.owner)
    except Exception as e:
        # Director 2026-10-05 (enclosing rollback): Verify restoration.
        # Unresolved restoration must retain evidence and remain observable.
        _rb = _rollback_full(program, old, old_snap, succ_id)
        if not _rb.get("ok"):
            # Incomplete rollback: attach details to exception.
            # Journal is already preserved (not cleared on failure).
            if isinstance(e, SupersedeError):
                e.details = getattr(e, 'details', {}) or {}
                e.details["rollback"] = "incomplete"
                e.details["rollback_failures"] = _rb.get("failures", [])
                e.details["rollback_removed"] = _rb.get("removed", [])
            # Do NOT clear intent; evidence retained.
        # Else: complete rollback, journal preserved for crash recovery
        # (do not clear on failure). If process survives, caller can retry.
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
