#!/usr/bin/env python3
"""Native confirm-proposal lineage body. Called by Program.confirm_proposal."""
from __future__ import annotations

import os
import uuid
from typing import Any, Dict, List

from form.dell_matrix.lineage import assign_lineage
from form.dell_matrix.nursery import NurseryConflictError
from form.dell_matrix.plane import Skin


def _goals(prop, units) -> List[str]:
    g = getattr(prop, "goals", None)
    if isinstance(g, (list, tuple)) and g:
        return [str(x) for x in g if str(x).strip()]
    for pid in list(getattr(prop, "parents", None) or []):
        u = units.get(pid)
        if u and getattr(u, "goals", None):
            return list(u.goals)
    return []


def _detail(prop, units) -> str:
    d = str(getattr(prop, "detail", "") or "").strip()
    if d:
        return d
    for pid in list(getattr(prop, "parents", None) or []):
        u = units.get(pid)
        if u and getattr(u, "detail", ""):
            return str(u.detail)
    return ""


def _validate_writer_auth(program, pid: str, auth: Dict[str, Any], stage: str) -> Dict[str, Any]:
    """Validate carried authorization at a writer stage.

    Director 2026-10-05 (boundary): the writer re-validates live policy
    AND reviewed-data integrity immediately before placement and before
    durable publish. The auth snapshot is immutable; any intervening
    revocation or content mutation denies.

    R6.1: the trusted subject binding rides the auth snapshot (set by
    trusted dispatch in Program.confirm_proposal); the writer never
    re-derives identity from caller input. Owner scope comes from the
    Program object itself.

    Returns {"ok": True} or {"ok": False, "detail": str}. Never raises.
    """
    try:
        if not isinstance(auth, dict):
            return {"ok": False, "detail": f"{stage}: missing authorization (fail closed)"}
        policy = getattr(program, "acceptance_policy", None)
        if policy is None:
            return {"ok": False, "detail": f"{stage}: no acceptance policy (fail closed)"}
        operation = auth.get("operation") or "confirm"
        # Reviewed-data integrity: live hash must match the approved snapshot.
        # Content mutation after approval denies.
        live_hash = program.acceptance_data_hash(pid, operation)
        if live_hash != auth.get("data_hash"):
            return {"ok": False,
                    "detail": f"{stage}: reviewed data changed after approval"}
        decision = policy.check(
            auth.get("producer"), pid, auth.get("review_context"),
            proposal_version=live_hash, operation=operation,
            subject=auth.get("subject"),
            owner=getattr(program, "owner", None))
        if not decision.get("allowed"):
            return {"ok": False,
                    "detail": f"{stage}: {decision.get('detail') or 'policy denied'}"}
        return {"ok": True}
    except Exception as e:
        return {"ok": False,
                "detail": f"{stage}: validation error {type(e).__name__}"}


# R6.1 test-only hook. None (and never set) in production. If set to a
# callable, it is invoked with (program, pid, auth) after staging and
# before the pre-commit authorization check, so proofs can
# deterministically revoke a grant or mutate content mid-write and
# observe the writer deny. A raising hook fails closed through the
# normal compensation path.
_BETWEEN_STAGES = None


class BaselineUnverifiableError(RuntimeError):
    """Baseline capture failed, so failure compensation cannot be
    verified. Raised inside the commit section BEFORE any
    checkpoint call: the confirm is refused explicitly
    (reason='baseline_unverifiable'), the intent journal is left
    for recovery, and no durable write is attempted. Claiming
    success — or proceeding to commit — on an unverifiable
    baseline is the defect the Director's single-worker probe
    reproduced on PR head 616449f (2026-11-06, round 2)."""


def _denied_receipt(pid, producer, detail, stage):
    return {
        "ok": False,
        "reason": "acceptance_policy_denied",
        "detail": detail,
        "pid": pid,
        "producer": producer,
        "stage": stage,
    }


# Confirm-placement circuit (Q-U.3 + Q-U.4 + Q-U.5 + AUTO => SANDBOX
# FIRST; Ace/Director rulings 2026-11-13): the designated per-owner
# auto-staging box. Automatic placements with no wall of their own
# land here first — contained, never directly on the open field.
STAGING_BOX_ID = "auto_staging"
STAGING_BOX_LABEL = "Auto staging — program-placed, awaiting release"


def _placement_options(keys):
    opts = [{"sandbox_id": k} for k in sorted(k for k in keys if k)]
    opts.append({"outside": True})
    return opts


def _resolve_confirm_placement(program, prop, auth) -> Dict[str, Any]:
    """Resolve where a confirmation lands, per Q-U.3/.4/.5 +
    AUTO => SANDBOX FIRST. READ-ONLY.

    Returns {"ok": True, "sandbox_id": Optional[str], "mode": str,
             "parent_wall_keys": List[Optional[str]],
             "choice": Optional[str]}
    or a refusal receipt {"ok": False, "reason": ..., "pid": ...,
    "producer": ..., ...} in the writer's existing receipt shape.

    Wall verdicts come from the PR #412 resolver,
    inference_dock._wall_verdict, imported at function level (the
    established deferred-import pattern for this module): ONE wall
    semantics, no second authority. Eligibility precedes choice —
    a malformed or unestablished claim refuses BEFORE any choice
    is offered or honored, and a caller-supplied choice is only
    ever validated against the parents' ACTUAL walls; the writer
    never lets a caller name an arbitrary box.
    """
    from form.dell_matrix.inference_dock import _wall_verdict
    pid = prop.id
    producer = auth.get("producer") if isinstance(auth, dict) else None
    auto = producer == "grow_auto"
    choice = auth.get("placement") if isinstance(auth, dict) else None

    def _refuse(reason, **extra):
        r = {"ok": False, "reason": reason, "pid": pid,
             "producer": producer}
        r.update(extra)
        return r

    parents = getattr(prop, "parents", None)
    if not isinstance(parents, list) or any(
            not isinstance(x, str) or not x for x in parents):
        return _refuse("malformed_parentage")
    if not parents:
        if auto:
            return {"ok": True, "sandbox_id": STAGING_BOX_ID,
                    "mode": "auto_staging", "parent_wall_keys": [],
                    "choice": None}
        return {"ok": True, "sandbox_id": None, "mode": "parentless",
                "parent_wall_keys": [], "choice": None}
    plane = program.cube.session.plane
    keys = set()
    for parent in parents:
        verdict, vkeys, culprit = _wall_verdict(program, plane, parent)
        if verdict == "malformed":
            return _refuse("malformed_wall_claim", culprit=culprit)
        if verdict == "unknown":
            return _refuse("unknown_parent", culprit=culprit)
        keys |= vkeys
    key_list = sorted(keys, key=lambda k: (k is not None, k or ""))
    if len(keys) > 1:
        if auto:
            return _refuse("auto_mixed_wall_noneligible")
        if choice is None:
            return _refuse("placement_choice_required",
                           options=_placement_options(keys))
        if choice == "outside":
            return {"ok": True, "sandbox_id": None,
                    "mode": "manual_choice",
                    "parent_wall_keys": key_list, "choice": "outside"}
        if isinstance(choice, str) and choice in keys:
            return {"ok": True, "sandbox_id": choice,
                    "mode": "manual_choice",
                    "parent_wall_keys": key_list, "choice": choice}
        return _refuse("invalid_placement_choice",
                       options=_placement_options(keys))
    if choice is not None:
        # A choice exists only where a choice exists (D13).
        return _refuse("invalid_placement_choice")
    only = next(iter(keys))
    if only is None:
        if auto:
            return {"ok": True, "sandbox_id": STAGING_BOX_ID,
                    "mode": "auto_staging",
                    "parent_wall_keys": [None], "choice": None}
        return {"ok": True, "sandbox_id": None,
                "mode": "unboxed_parents",
                "parent_wall_keys": [None], "choice": None}
    return {"ok": True, "sandbox_id": only,
            "mode": "auto_parents_wall" if auto else "inherited_wall",
            "parent_wall_keys": [only], "choice": None}


def confirm_proposal(program, pid: str, _auth: Dict[str, Any] = None) -> Dict[str, Any]:
    """Canonical confirmation authority (transactional).

    Uses the checkpoint generation transaction (DCC-XVIII) to atomically
    commit Program + Nursery state. The logical transition is:

    OLD: proposal=PENDING, Idea absent from accepted Plane
    NEW: proposal=CONFIRMED, Idea present in accepted Program state

    Externally observable durable state is either OLD complete or NEW
    complete, never a hybrid. Any failure before the commit boundary
    leaves the proposal pending (memory and disk), so it stays retryable
    and rejectable.

    Internal: Set confirm_lineage._SKIP_CHECKPOINT = True to bypass the
    checkpoint (caller manages durability). Used by supersede_proposal
    which has its own transaction boundary.

    Authorization: _auth carries the immutable approved operation from
    Program.confirm_proposal. The writer validates live policy and
    reviewed-data integrity before placement and before durable publish.
    Missing _auth fails closed.
    """
    # Check for skip flag (set by supersede_proposal)
    _skip = getattr(confirm_proposal, '_SKIP_CHECKPOINT', False)
    nursery = program.nursery
    prop = nursery.proposals.get(pid)
    if not prop or prop.status != "pending":
        return {"ok": False, "reason": "not found or not pending"}
    units = program.cube.session.plane.units
    rec = assign_lineage(units, getattr(prop, "parents", None), origin="confirmed", child_id=prop.id)
    if not rec.get("ok"):
        return {"ok": False, "reason": rec.get("error") or "invalid_lineage", "missing": rec.get("missing")}
    # Director 2026-10-05 (boundary): validate carried authorization
    # immediately before the placement mutation. No placement without
    # live approval of the exact reviewed data.
    _v = _validate_writer_auth(program, pid, _auth, "pre_place")
    if not _v["ok"]:
        _producer = _auth.get("producer") if isinstance(_auth, dict) else None
        return _denied_receipt(pid, _producer, _v["detail"], "pre_place")
    # Confirm-placement (Q-U.3/.4/.5 + AUTO => SANDBOX FIRST):
    # resolve placement READ-ONLY after authorization, before any
    # mutation. A refusal here means zero mutation: the proposal
    # stays pending and no checkpoint transaction begins.
    _placement = _resolve_confirm_placement(program, prop, _auth)
    if not _placement.get("ok"):
        return _placement
    existed = prop.id in units
    def _remove_newly_placed():
        """Remove a newly placed Idea from all in-memory structures.

        Director 2026-10-05 (compensation): cleanup failures are OBSERVABLE,
        not suppressed. Returns {"ok", "failures", "removed"}.

        Critical (accepted-state artifacts that must not persist after
        denial): plane unit, spatial velocities, spatial placements.
        Best-effort (derived/append-only): lattice rebuild, history.

        F2: Program.place() calls self.spatial.place() (SpatialAuthority),
        which writes placements and velocities. Cleanup must use the SAME
        authority: program.spatial.
        """
        failures = []
        removed = []
        # Critical (confirm-placement): box membership — a boxed
        # confirm that is later denied must not leave the child id
        # dangling in the box's member_ids.
        try:
            _placed = units.get(prop.id)
            _sid = getattr(_placed, "sandbox_id", None) if _placed else None
            if _sid:
                _sb = program.cube.session.plane.sandboxes.get(_sid)
                if _sb is not None and prop.id in _sb.member_ids:
                    _sb.member_ids = [m for m in _sb.member_ids
                                      if m != prop.id]
                    removed.append("sandbox_membership")
        except Exception as e:
            failures.append(f"sandbox_membership:{type(e).__name__}")
        # Critical: plane unit
        try:
            units.pop(prop.id, None)
            removed.append("unit")
        except Exception as e:
            failures.append(f"unit:{type(e).__name__}")
        # Critical: spatial entries
        try:
            spatial = program.spatial
            if hasattr(spatial, 'velocities'):
                try:
                    spatial.velocities.pop(prop.id, None)
                    removed.append("velocities")
                except Exception as e:
                    failures.append(f"velocities:{type(e).__name__}")
            if hasattr(spatial, 'placements'):
                try:
                    spatial.placements.pop(prop.id, None)
                    removed.append("placements")
                except Exception as e:
                    failures.append(f"placements:{type(e).__name__}")
        except Exception as e:
            failures.append(f"spatial_access:{type(e).__name__}")
        # Best-effort: lattice rebuild (derived state; rebuildable later)
        try:
            if hasattr(program.lattice, 'rebuild_from_plane'):
                program.lattice.rebuild_from_plane(program.cube.session.plane)
                removed.append("lattice_rebuilt")
        except Exception as e:
            failures.append(f"lattice:{type(e).__name__}")
        # Note: history is append-only and honestly records the attempt;
        # keys index staleness is harmless.
        #
        # Director 2026-10-05 (enclosing rollback): Preserve evidence until
        # complete restoration is VERIFIED. A pop() that silently does
        # nothing (key already absent) is not proof of removal. Verify the
        # critical artifacts are actually absent; if verification fails,
        # report incomplete compensation so the journal is retained.
        _verify_failures = []
        try:
            if prop.id in units:
                _verify_failures.append("verify:unit_still_present")
        except Exception as e:
            _verify_failures.append(f"verify:unit_check:{type(e).__name__}")
        try:
            spatial = program.spatial
            if hasattr(spatial, 'velocities'):
                try:
                    if prop.id in spatial.velocities:
                        _verify_failures.append("verify:velocities_still_present")
                except Exception as e:
                    # Director 2026-10-05: Unverifiable cleanup is incomplete.
                    # Named failure, not suppressed.
                    _verify_failures.append(
                        f"verify:velocities_check_failed:{type(e).__name__}")
            if hasattr(spatial, 'placements'):
                try:
                    if prop.id in spatial.placements:
                        _verify_failures.append("verify:placements_still_present")
                except Exception as e:
                    _verify_failures.append(
                        f"verify:placements_check_failed:{type(e).__name__}")
        except Exception as e:
            _verify_failures.append(f"verify:spatial_check:{type(e).__name__}")
        failures.extend(_verify_failures)
        return {"ok": not failures, "failures": failures, "removed": removed}
    try:
        program.place(
            prop.id, prop.label, words=prop.words, detail=_detail(prop, units), goals=_goals(prop, units),
            skin=Skin.SEED, parents=list(rec["parents"]), origin=rec["origin"], lineage_version=int(rec["lineage_version"]),
        )
        # Confirm-placement: apply box membership via the ONLY
        # writer that maintains both sides (Plane.box), inside
        # this same try — i.e. inside the checkpoint transaction
        # below. place_idea accepts no sandbox kwargs, so
        # membership is applied immediately after placement.
        if _placement.get("sandbox_id"):
            _sid = _placement["sandbox_id"]
            _label = (STAGING_BOX_LABEL
                      if _sid == STAGING_BOX_ID else None)
            program.cube.session.plane.box([prop.id], _sid,
                                           label=_label)
    except Exception as e:
        # Director 2026-10-05 (compensation): cleanup failures are
        # observable. The original exception propagates (honest failure),
        # but incomplete compensation is attached for the caller.
        # Director 2026-10-06 (close unsafe save): incomplete compensation
        # marks the instance; normal saves are rejected until verified
        # restoration or reconstruction.
        if not existed:
            _pc = _remove_newly_placed()
            if not _pc["ok"]:
                e._compensation_incomplete = _pc
                from form.mandell.core_i_recovery import mark_recovery_required
                mark_recovery_required(
                    program, prop.id, "compensation_incomplete",
                    {"failures": _pc["failures"],
                     "removed": _pc.get("removed", [])})
        raise
    # R3: Record intent BEFORE any durable writes. The journal enables
    # recovery to distinguish "crashed confirmation" from "legitimate
    # historical record". Recovery uses recorded intent, not visibility.
    # R3-COMPLETION-GATE: Skip journal if supersession is managing the
    # transaction (it uses its own enclosing journal). Do not publish
    # independent successor acceptance and clear recovery evidence before
    # the supersession outcome is recoverable.
    from form.mandell.core_i_recovery import write_confirm_intent, clear_confirm_intent
    _skip_journal = getattr(confirm_proposal, '_SKIP_JOURNAL', False)
    if not _skip_journal:
        try:
            write_confirm_intent(program.owner, prop.id)
        except Exception as e:
            # F1: Intent-write failure must restore newly placed memory.
            # The Idea was placed in-memory but no journal exists to enable
            # recovery. Remove it to prevent exposing unrecoverable hybrid.
            # Director 2026-10-05 (compensation): incomplete cleanup is
            # attached to the propagating exception (observable).
            # Director 2026-10-06 (close unsafe save): incomplete
            # compensation marks the instance; normal saves rejected until
            # verified restoration or reconstruction.
            if not existed:
                _ic = _remove_newly_placed()
                if not _ic["ok"]:
                    e._compensation_incomplete = _ic
                    from form.mandell.core_i_recovery import mark_recovery_required
                    mark_recovery_required(
                        program, prop.id, "compensation_incomplete",
                        {"failures": _ic["failures"],
                         "removed": _ic.get("removed", [])})
            raise
    # Stage the nursery confirmation in memory (do NOT save yet).
    # The checkpoint transaction will persist both Program and Nursery atomically.
    # ARGUS-3: All persistence failures must preserve/restore pre-operation state.
    prop.status = "confirmed"
    # Director 2026-10-05 (boundary): validate carried authorization
    # immediately before durable publish. Revocation or content mutation
    # after staging denies; staged in-memory state is reverted via the
    # existing compensation path.
    #
    # Director 2026-10-05 (compensation): incomplete compensation must NOT
    # be reported as ordinary denial. If critical cleanup fails, the intent
    # journal is RETAINED (evidence outlives unresolved restoration) and
    # the receipt reports incomplete compensation alongside the original
    # authorization denial.
    # R6.1: deterministic mid-write hook for revocation/content-change
    # proofs (test-only; _BETWEEN_STAGES is None in production).
    _hook = _BETWEEN_STAGES
    _hook_err = None
    if callable(_hook):
        try:
            _hook(program, pid, _auth)
        except Exception as e:
            _hook_err = f"between-stages hook failed: {type(e).__name__}"
    _v2 = _validate_writer_auth(program, pid, _auth, "pre_commit")
    if _hook_err is not None and _v2["ok"]:
        _v2 = {"ok": False, "detail": _hook_err}
    if not _v2["ok"]:
        prop.status = "pending"
        _comp = {"ok": True, "failures": [], "removed": []}
        if not existed:
            _comp = _remove_newly_placed()
        _producer2 = _auth.get("producer") if isinstance(_auth, dict) else None
        if not _comp["ok"]:
            # Incomplete compensation: retain journal, report honestly.
            # The original auth denial remains identifiable; the receipt
            # is NOT an ordinary completed denial.
            # Director 2026-10-06 (close unsafe save): mark the instance;
            # normal saves are rejected until verified restoration or
            # reconstruction.
            from form.mandell.core_i_recovery import mark_recovery_required
            mark_recovery_required(
                program, pid, "compensation_incomplete",
                {"failures": _comp["failures"],
                 "removed": _comp.get("removed", [])})
            return {
                "ok": False,
                "reason": "acceptance_policy_denied",
                "detail": _v2["detail"],
                "pid": pid,
                "producer": _producer2,
                "stage": "pre_commit",
                "compensation": "incomplete",
                "compensation_failures": _comp["failures"],
                "compensation_removed": _comp["removed"],
                "evidence_retained": True,
            }
        # Complete compensation: clear journal (deliberate denial, not crash).
        try:
            from form.mandell.core_i_recovery import clear_confirm_intent
            if not _skip_journal:
                clear_confirm_intent(program.owner)
        except Exception:
            pass
        return _denied_receipt(pid, _producer2, _v2["detail"], "pre_commit")
    if not _skip:
        # 72-31: serialize the durable commit section per owner under
        # the canonical owner-state lock (TD-1-R2 authority — the same
        # lock persist_rest.save takes; re-entrant for this thread, so
        # the seal's own saves join rather than deadlock). Two live
        # instances racing a confirm otherwise interleave baseline
        # capture, checkpoint seal and failure compensation: both can
        # pass the nursery optimistic guard inside its check/write
        # window (double-ok), and a refused loser's baseline restore
        # can overwrite the winner's committed generation (lost
        # winner). Holding the lock from baseline capture through
        # compensation makes the commit section one owner-scoped
        # transaction; the nursery guard then refuses a stale loser
        # deterministically, after the winner's commit is durable.
        # Acquisition failure fails closed (OwnerLockBusy /
        # OwnerLockUnavailable propagate): in-memory staging is
        # reverted first; the transaction never proceeds unlocked.
        from form.owner_state_lock import owner_state_lock
        _commit_lock = owner_state_lock(program.owner)
        try:
            _commit_lock.__enter__()
        except Exception:
            prop.status = "pending"
            if not existed:
                _lk = _remove_newly_placed()
                if not _lk["ok"]:
                    from form.mandell.core_i_recovery import mark_recovery_required
                    mark_recovery_required(
                        program, prop.id, "compensation_incomplete",
                        {"failures": _lk["failures"],
                         "removed": _lk.get("removed", [])})
            raise

        def _release_commit_lock():
            try:
                _commit_lock.__exit__(None, None, None)
            except Exception:
                pass

        # F2: Capture baseline file bytes before commit. If commit fails
        # after partial saves, restore these bytes directly. This is more
        # robust than trying to surgically revert all in-memory side
        # effects of program.place() (units, velocities, placements,
        # lattice, history, keys).
        _baseline_program_bytes = None
        _baseline_nursery_bytes = None
        _baseline_gen = None
        _baseline_gen_state = None
        _baseline_ok = False
        try:
            from form.persist import _path as _ppath
            from form.dell_matrix.nursery import owner_nursery_path
            _p_path = _ppath(program.owner)
            _n_path = owner_nursery_path(program.owner)
            # F2: Do not suppress baseline read failures. If we cannot
            # capture baseline, compensation cannot be verified; leave
            # journal for recovery instead of claiming success.
            if os.path.isfile(_p_path):
                with open(_p_path, 'rb') as f:
                    _baseline_program_bytes = f.read()
            # Legitimate absence: file doesn't exist, None is correct
            if os.path.isfile(_n_path):
                with open(_n_path, 'rb') as f:
                    _baseline_nursery_bytes = f.read()
            # 72-31 (D-B): record the committed generation at baseline
            # time. Compensation re-validates against it before
            # restoring any baseline bytes. Tri-state read (Director
            # correction 2026-11-06): an UNREADABLE pointer at
            # baseline makes compensation unverifiable — fail the
            # capture (the except below leaves the journal for
            # recovery) instead of recording a None that is
            # indistinguishable from proven absence.
            from form.mandell.checkpoint_generation import committed_generation_state as _cgs
            _baseline_gen_state, _baseline_gen = _cgs(program.owner)
            if _baseline_gen_state == "unreadable":
                raise OSError(
                    "committed generation unreadable at baseline "
                    "capture; compensation cannot be verified")
            _baseline_ok = True
        except Exception as e:
            # Baseline capture failed; compensation cannot be verified.
            # Leave journal for recovery (do not clear).
            _baseline_ok = False
        # 72-31: name our own generation up front (same id format as
        # checkpoint_generation._new_generation_id) so compensation
        # can distinguish "our commit boundary was crossed" from
        # "another transaction's generation is now committed".
        _our_gen = "g" + uuid.uuid4().hex[:16]
        try:
            from form.mandell.checkpoint_generation import commit_checkpoint
            if not _baseline_ok:
                # Baseline capture failed (bytes or committed
                # generation unreadable): compensation could never
                # be verified, so the confirm is refused HERE —
                # before any checkpoint call — rather than
                # committing and claiming success on an
                # unverifiable baseline. The except handler below
                # reverts in-memory staging, leaves the intent
                # journal as recovery evidence, releases the lock,
                # and returns the explicit refusal.
                raise BaselineUnverifiableError(
                    "baseline capture failed; failure compensation "
                    "cannot be verified — confirm refused before "
                    "any durable write")
            commit_checkpoint(program, generation_id=_our_gen)
            # Success: clear the intent journal (unless supersession manages it).
            if not _skip_journal:
                clear_confirm_intent(program.owner)
            _release_commit_lock()
        except Exception as exc:
            # Transaction failed: revert in-memory state to OLD.
            # Proposal stays pending (retryable), Idea removed if newly placed.
            # Never claim success, never silently discard, never expose hybrid.
            #
            # PRISM FINDING (2026-10-04): The checkpoint saves the LIVE nursery
            # file before the program file. If program save fails, the live
            # nursery file is left dirty with status="confirmed". The production
            # loader reads live files directly (bypasses checkpoint pointer),
            # so we MUST rewrite the live nursery file with reverted status.
            # Otherwise a crash here exposes confirmed+Idea-absent hybrid.
            #
            # R3: The intent journal remains for crash recovery. If this
            # handler completes the revert, clear the journal. If the process
            # dies before clearing, recovery will use the journal.
            prop.status = "pending"
            _ckpt_comp = {"ok": True, "failures": []}
            if not existed:
                _ckpt_comp = _remove_newly_placed()
            # Director 2026-10-06 (close unsafe save): incomplete
            # compensation marks the instance; normal saves are rejected
            # until verified restoration or reconstruction.
            if not _ckpt_comp["ok"]:
                from form.mandell.core_i_recovery import mark_recovery_required
                mark_recovery_required(
                    program, prop.id, "compensation_incomplete",
                    {"failures": _ckpt_comp["failures"],
                     "removed": _ckpt_comp.get("removed", [])})
            # Revert the live files that checkpoint may have dirtied.
            # F2: Restore baseline bytes directly for complete compensation.
            # A Nursery-only revert leaves durable Program with Idea but no
            # journal for recovery. Use atomic_write_bytes (not raw open)
            # to prevent partial writes.
            reverted = False
            # 72-31 (D-B): re-validate the committed generation before
            # restoring baseline bytes. If the CURRENT pointer advanced
            # past the baseline generation, it names either a NEWER
            # generation committed by another transaction after our
            # baseline was captured (the race winner — its live files
            # are authoritative and must not be overwritten with our
            # stale baseline) or OUR OWN generation (our commit
            # boundary was crossed before a later stage failed;
            # restoring baseline would diverge the live pair from the
            # committed members). Either way durable state is a
            # complete committed generation that is not ours to
            # revert: skip the restore and treat compensation as
            # converged on it.
            _gen_advanced = False
            _gen_uncertain = False
            _now_state = "error"
            try:
                from form.mandell.checkpoint_generation import committed_generation_state as _cgs_now
                _now_state, _now_gen = _cgs_now(program.owner)
                if _now_state == "verified" and _baseline_gen_state == "verified":
                    _gen_advanced = (_now_gen != _baseline_gen)
                elif _now_state == "verified" and _baseline_gen_state == "absent":
                    # A generation appeared after an absent baseline:
                    # another transaction committed (the race winner).
                    _gen_advanced = True
                elif _now_state == "absent" and _baseline_gen_state == "absent":
                    _gen_advanced = False  # proven unchanged
                else:
                    # verified->absent (pointer vanished) or the
                    # pointer is UNREADABLE: committed identity
                    # cannot be positively established. Uncertainty
                    # is never evidence that a baseline restore is
                    # safe (Director correction 2026-11-06: the
                    # best-effort helper's None collapsed exactly
                    # this case and let a stale restore erase the
                    # winner).
                    _gen_uncertain = True
            except Exception:
                _gen_uncertain = True
            if _gen_advanced:
                reverted = True
            elif _gen_uncertain:
                # Preserve recovery evidence on uncertainty: do NOT
                # restore baseline bytes, do NOT clear the intent
                # journal (reverted stays False), and fence this
                # instance from saving until verified restoration.
                _already = getattr(program, "_recovery_required", None)
                if not (isinstance(_already, dict) and prop.id in _already):
                    from form.mandell.core_i_recovery import mark_recovery_required
                    mark_recovery_required(
                        program, prop.id,
                        "compensation_unverified_generation_unreadable",
                        {"baseline_state": str(_baseline_gen_state),
                         "now_state": str(_now_state)})
                reverted = False
            # F2: Only attempt compensation if baseline was captured.
            # Otherwise leave journal for recovery (fail closed).
            # Director 2026-10-05 (compensation): incomplete in-memory
            # cleanup also blocks journal clearing (evidence retained).
            elif _baseline_ok and _ckpt_comp["ok"]:
                try:
                    from form.dell_matrix.atomic_write import atomic_write_bytes
                    # Restore Program file from baseline bytes (complete revert)
                    if _baseline_program_bytes is not None:
                        atomic_write_bytes(_p_path, _baseline_program_bytes)
                    elif not existed:
                        # No baseline (new file): save reverted in-memory state
                        from form import persist_rest
                        persist_rest.save(program)
                    # Restore Nursery file from baseline (has pending status)
                    if _baseline_nursery_bytes is not None:
                        atomic_write_bytes(_n_path, _baseline_nursery_bytes)
                    else:
                        nursery.save()
                    reverted = True
                except Exception:
                    # If we can't revert both files, leave journal for recovery.
                    pass
            # If baseline capture failed (_baseline_ok=False) or cleanup
            # incomplete, reverted stays False, journal is preserved.
            if reverted:
                if not _skip_journal:
                    clear_confirm_intent(program.owner)
            _release_commit_lock()
            # Check if it's a nursery conflict (optimistic concurrency).
            # The checkpoint wraps the original error, so check the chain.
            from form.dell_matrix.nursery import NurseryConflictError
            def _is_conflict(e):
                if isinstance(e, NurseryConflictError):
                    return True
                if "conflict" in str(e).lower():
                    return True
                # Check wrapped cause (checkpoint wraps nursery errors)
                cause = getattr(e, '__cause__', None)
                if cause is not None and cause is not e:
                    return _is_conflict(cause)
                return False
            if isinstance(exc, BaselineUnverifiableError):
                return {"ok": False, "reason": "baseline_unverifiable",
                        "error": str(exc)}
            if _is_conflict(exc):
                return {"ok": False, "reason": "nursery_conflict", "error": str(exc)}
            raise
    else:
        # Skipping checkpoint (caller manages durability, e.g., supersession).
        # R3: Save BOTH nursery and program. The caller (supersession Phase 4)
        # will update predecessor links, but the successor's Idea must be
        # durable before Phase 4 begins. Otherwise a crash in Phase 4 leaves
        # the successor confirmed in nursery but absent from program.
        # Write intent journal for this confirmation as well, so crash
        # recovery can distinguish it from historical records.
        try:
            nursery.save()
            from form import persist_rest
            persist_rest.save(program)
            if not _skip_journal:
                clear_confirm_intent(program.owner)
        except Exception:
            prop.status = "pending"
            if not existed:
                _sk = _remove_newly_placed()
                # Director 2026-10-06 (close unsafe save): incomplete
                # compensation marks the instance even here; the enclosing
                # supersession rollback will clear it on verified success.
                if not _sk["ok"]:
                    from form.mandell.core_i_recovery import mark_recovery_required
                    mark_recovery_required(
                        program, prop.id, "compensation_incomplete",
                        {"failures": _sk["failures"],
                         "removed": _sk.get("removed", [])})
            # Leave journal for recovery (do not clear).
            raise
    try:
        text = " ".join([str(prop.label or ""), str(getattr(prop, "words", "") or ""), str(getattr(prop, "detail", "") or "")])
        aff = float(getattr(prop, "affinity", 1.0) or 1.0)
        program.inspire.prefs.observe_confirm(text, aff)
    except Exception:
        pass
    program.note_seed(50, "Manifest", prop.label)
    return {"ok": True, "id": prop.id, "label": prop.label, "kind": prop.kind,
            "placement": {
                "mode": _placement.get("mode"),
                "sandbox_id": _placement.get("sandbox_id"),
                "parent_wall_keys": _placement.get("parent_wall_keys"),
                "choice": _placement.get("choice"),
            }}
