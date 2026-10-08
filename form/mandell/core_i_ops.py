#!/usr/bin/env python3
"""Locally closable Core I arms that wrap the leaf without rewriting it."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

HANDLED = {27, 28, 34, 35, 37, 40, 44, 47}


def _rev_state(program: Any, pid: str) -> str:
    """Lifecycle state for receipts (DCC-XVI explicit-override evidence)."""
    from form.mandell.supersession import inspect_revision
    try:
        return inspect_revision(program, pid)["lifecycle_state"]
    except Exception:
        return "unknown"


def apply_core_i(program: Any, seed_text: str, seed: Any) -> Optional[Dict[str, Any]]:
    n = seed.primary_dell()
    if n not in HANDLED:
        return None
    label = seed.label or ""
    messages = [f"Mandell: {seed.as_mandel()}", f"English: {seed.as_english()}"]
    base = {
        "seed": seed.as_mandel(),
        "english": seed.as_english(),
        "primary": n,
        "messages": messages,
        "new_program": None,
    }
    if n == 27:
        from .core_i_recovery import checkpoint
        try:
            # PAC-I: checkpoint() delegates to Checkpoint Generation V1 and
            # returns the committed generation id (observable generation identity).
            gen_id = checkpoint(program, stamp=label or None)
            program.last_core_i = {"dell": 27, "generation_id": gen_id, "ok": True}
            messages.append(f"Checkpoint written: generation {gen_id}")
            return {**base, "ok": True, "error": "", "generation_id": gen_id}
        except Exception as exc:
            program.last_core_i = {"dell": 27, "ok": False, "error": str(exc)}
            messages.append(f"Checkpoint fail: {exc}")
            return {**base, "ok": False, "error": str(exc)}
    if n == 28:
        # R6.3: Dell 28 is authority-mediated. It routes through
        # Program.confirm_rollback — the single enforcement point.
        # Without an explicit bound approval/grant (human two-step
        # "restore confirm <generation>" or an agent RollbackEndpoint),
        # this denies with zero mutation. Typing "restore" alone is
        # never approval.
        from form.dell_matrix import rollback_authority as _ra
        label_gen = label if (label and not label.endswith(".json")) else None
        try:
            res = program.confirm_rollback(
                label_gen, _review_context=None,
                _subject="dell28-system", _producer="dell28")
        except Exception as exc:
            program.last_core_i = {"dell": 28, "ok": False,
                                   "error": f"{type(exc).__name__}: {exc}"}
            messages.append(f"Rollback fail: {exc}")
            return {**base, "ok": False, "error": str(exc)}
        if res.get("ok"):
            program.last_core_i = {"dell": 28, "ok": True,
                                   "generation_id": res["generation_id"]}
            messages.append(
                f"Checkpoint restored: generation {res['generation_id']} "
                f"(compensating {res['compensating_generation_id']}).")
            from form import persist_rest as _pr
            return {**base, "ok": True, "error": "",
                    "new_program": _pr.load(program.owner, activate=False)}
        program.last_core_i = {"dell": 28, "ok": False,
                               "error": res.get("reason")}
        messages.append(
            f"Rollback denied ({res.get('reason')}): "
            f"{res.get('detail', '')[:160]}")
        return {**base, "ok": False, "error": res.get("reason") or ""}
    if n == 34:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        mark = label or "stamp"
        program.last_stamp = {"mark": mark, "ts": ts}
        program.last_core_i = {"dell": 34, "value": program.last_stamp, "ok": True}
        messages.append(f"Stamp: {mark} @ {ts}")
        return {**base, "ok": True, "error": ""}
    if n == 35:
        lab = label.lower()
        # DCC-VI: extended read labels for operational capabilities.
        if lab == "count_nursery":
            ns = program.nursery.summary()
            program.last_discover = {
                "pending": ns.get("pending", 0),
                "total": ns.get("total", 0),
                "confirmed": ns.get("confirmed", 0),
                "rejected": ns.get("rejected", 0),
                "source": "nursery_summary",
            }
            messages.append(f"Nursery: pending={ns.get('pending',0)} total={ns.get('total',0)} "
                          f"confirmed={ns.get('confirmed',0)} rejected={ns.get('rejected',0)}")
        elif lab == "list_pending":
            pending = program.nursery.pending()
            program.last_discover = {
                "ids": [p.id for p in pending],
                "labels": [p.label for p in pending],
                "count": len(pending),
                "source": "nursery_pending",
            }
            messages.append(f"Pending proposals: {len(pending)}")
            for p in pending[:10]:
                messages.append(f"  {p.id}: {p.label}")
        elif lab == "compare_nursery":
            ns = program.nursery.summary()
            pending = ns.get("pending", 0)
            confirmed = ns.get("confirmed", 0)
            program.last_discover = {
                "pending": pending,
                "confirmed": confirmed,
                "comparison": "pending>confirmed" if pending > confirmed else (
                    "confirmed>pending" if confirmed > pending else "equal"),
                "source": "nursery_compare",
            }
            messages.append(f"Nursery compare: pending={pending} confirmed={confirmed}")
        elif lab == "trace":
            hist = list(getattr(program, "history", []))
            program.last_discover = {
                "history": hist,
                "count": len(hist),
                "source": "trace",
            }
            messages.append(f"Trace: {len(hist)} operations")
            for h in hist[-10:]:
                messages.append(f"  {h}")
        elif lab.startswith("trace_lineage "):
            # DCC-XIV: answer "where did this knowledge come from?" from
            # persisted lineage, without raw state inspection.
            from form.mandell.knowledge_lineage import lineage_record
            target = lab[len("trace_lineage "):].strip()
            rec = lineage_record(program, target)
            program.last_discover = {**rec, "source": "trace_lineage"}
            if rec["status"] == "unknown_unit":
                messages.append(f"Lineage: unknown unit '{target}'")
            else:
                messages.append(
                    f"Lineage {target}: {rec['origin_kind']} "
                    f"(origin={rec['origin']}, depth={rec['depth']}, "
                    f"status={rec['status']})"
                )
                messages.append(f"  parents: {rec['parent_ids'] or '—'}")
                messages.append(f"  roots: {rec['root_ids'] or '—'}")
        elif lab.startswith("trace_dependency "):
            # DCC-XV: answer "is this knowledge dependency-valid right now,
            # and if not, why?" — historical lineage alongside current
            # dependency status. Dependency is not truth, relevance, or
            # conflict; it is current qualification of required ancestry.
            from form.mandell.dependency_validity import (
                DEPENDENCY_VERSION, inspect_dependency,
            )
            from form.mandell.knowledge_lineage import lineage_record
            target = lab[len("trace_dependency "):].strip()
            lin = lineage_record(program, target)
            dep = inspect_dependency(program, target)
            program.last_discover = {
                "source": "trace_dependency",
                "unit_id": target,
                "dependency_version": DEPENDENCY_VERSION,
                "dependency_status": dep["dependency_status"],
                "dependency_reason": dep["dependency_reason"],
                "direct_parent_ids": dep["direct_parent_ids"],
                "ancestor_ids": dep["ancestor_ids"],
                "invalid_dependency_ids": dep["invalid_dependency_ids"],
                "missing_dependency_ids": dep["missing_dependency_ids"],
                "origin_kind": lin["origin_kind"],
                "origin": lin["origin"],
                "parent_ids": dep["direct_parent_ids"],
                "root_ids": dep["historical_root_ids"],
                "depth": lin["depth"],
                "lineage_status": lin["status"],
            }
            if dep["dependency_status"] == "valid":
                messages.append(f"Dependency {target}: valid "
                                f"(origin={lin['origin_kind']}, depth={lin['depth']})")
            else:
                messages.append(f"Dependency {target}: {dep['dependency_status']} "
                                f"({dep['dependency_reason']})")
                messages.append(f"  historical parents: {dep['direct_parent_ids'] or '—'}")
                messages.append(f"  historical roots: {dep['historical_root_ids'] or '—'}")
        elif lab.startswith("trace_revision "):
            # DCC-XVI: answer "which accepted version replaces which?" —
            # revision identity and chain, without touching derivation
            # lineage. Revision ancestry != derivation ancestry.
            from form.mandell.supersession import inspect_revision
            target = lab[len("trace_revision "):].strip()
            rec = inspect_revision(program, target)
            program.last_discover = {**rec, "source": "trace_revision"}
            if rec["lifecycle_state"] == "unknown":
                messages.append(f"Revision: unknown unit '{target}'")
            elif rec["lifecycle_state"] == "malformed":
                messages.append(
                    f"Revision {target}: malformed "
                    f"({rec['malformed_reason']})")
                messages.append(
                    f"  declared predecessor: {rec['supersedes_id'] or '—'}")
                messages.append(
                    f"  declared successor: {rec['superseded_by_id'] or '—'}")
            else:
                messages.append(
                    f"Revision {target}: {rec['lifecycle_state']} "
                    f"(root={rec['revision_root_id']}, "
                    f"number={rec['revision_number']})")
                messages.append(
                    f"  predecessor: {rec['supersedes_id'] or '—'}")
                messages.append(
                    f"  successor: {rec['superseded_by_id'] or '—'}")
                if rec["chain"]:
                    messages.append(
                        f"  chain: {' -> '.join(rec['chain'])}")
        elif lab.startswith("trace_conflict "):
            # DCC-XIX: answer "what is the current detection evidence and
            # operator disposition for this stable conflict?" -- routing
            # governance inspection, never a truth claim.
            from form.mandell.conflict_disposition import trace_conflict
            target = lab[len("trace_conflict "):].strip()
            rec = trace_conflict(program, target)
            program.last_discover = {**rec, "source": "trace_conflict"}
            if not rec.get("ok"):
                messages.append(f"Conflict trace failed: {rec.get('error')}")
            else:
                messages.append(
                    f"Conflict {target}: disposition={rec['disposition']} "
                    f"({rec['applicability']})")
                if rec["detection_evidence"]:
                    ev = rec["detection_evidence"]
                    messages.append(
                        f"  participants: {ev['id_a']} <-> {ev['id_b']} "
                        f"(frame_jaccard={ev['frame_jaccard']})")
                for p in rec["participants"]:
                    messages.append(
                        f"  {p['unit_id']}: revision={p['lifecycle_state']}, "
                        f"dependency={p['dependency_status']} "
                        f"({'qualifies' if p['currently_qualifies'] else p['qualification_note']})")
        elif lab.startswith("trace_outcome "):
            # DCC-XX: answer "what exactly happened in this execution?" --
            # durable structured observation, never a truth claim.
            from form.mandell.outcome_ledger import get_outcome
            target = lab[len("trace_outcome "):].strip()
            rec = get_outcome(program, target)
            if rec is None:
                program.last_discover = {"ok": False, "error": "outcome not found",
                                         "source": "trace_outcome", "outcome_id": target}
                messages.append(f"Outcome {target}: not found")
            else:
                program.last_discover = {**rec, "source": "trace_outcome"}
                messages.append(
                    f"Outcome {rec['outcome_id']}: {rec['operation']} -> {rec['result']} "
                    f"(seq={rec['outcome_seq']})")
                if rec["knowledge"]:
                    messages.append(
                        "  knowledge: " + ", ".join(
                            f"{k['id']}#rev{k['revision_number']}" for k in rec["knowledge"]))
                for c in rec["conflicts"]:
                    messages.append(
                        f"  conflict {c['conflict_id']}: {c['disposition']}")
                if rec["error"]:
                    messages.append(f"  error: {rec['error'][:120]}")
        elif lab == "list_outcomes":
            # DCC-XX: most recent outcomes, newest first.
            from form.mandell.outcome_ledger import list_outcomes
            recs = list_outcomes(program, limit=10)
            program.last_discover = {"outcomes": recs, "count": len(recs),
                                     "source": "list_outcomes"}
            if not recs:
                messages.append("Outcomes: none recorded")
            else:
                messages.append(f"Outcomes: {len(recs)} recent")
                for r in recs:
                    messages.append(
                        f"  {r['outcome_id']}: {r['operation']} -> {r['result']} "
                        f"(seq={r['outcome_seq']})")
        elif lab.startswith("outcomes_for_idea "):
            # DCC-XX: outcomes whose knowledge provenance includes an ID.
            from form.mandell.outcome_ledger import outcomes_for_knowledge
            target = lab[len("outcomes_for_idea "):].strip()
            recs = outcomes_for_knowledge(program, target)
            program.last_discover = {"outcomes": recs, "count": len(recs),
                                     "source": "outcomes_for_idea",
                                     "knowledge_id": target}
            if not recs:
                messages.append(f"Outcomes for idea {target}: none recorded")
            else:
                messages.append(f"Outcomes for idea {target}: {len(recs)}")
                for r in recs:
                    messages.append(
                        f"  {r['outcome_id']}: {r['operation']} -> {r['result']} "
                        f"(seq={r['outcome_seq']})")
        elif "nursery" in lab:
            pending = program.list_proposals()
            program.last_discover = {"ids": [p.get("id") for p in pending], "count": len(pending), "source": "nursery"}
            messages.append(f"Nursery pending: {len(pending)}")
        # DCC-VII: query accepted/promoted knowledge (confirmed proposals in cube).
        elif lab == "list_confirmed":
            confirmed = [p for p in program.nursery.proposals.values()
                        if p.status == "confirmed"]
            program.last_discover = {
                "ids": [p.id for p in confirmed],
                "labels": [p.label for p in confirmed],
                "count": len(confirmed),
                "source": "nursery_confirmed",
            }
            messages.append(f"Confirmed proposals: {len(confirmed)}")
            for p in confirmed[:10]:
                messages.append(f"  {p.id}: {p.label}")
        elif lab == "count_confirmed":
            confirmed = [p for p in program.nursery.proposals.values()
                        if p.status == "confirmed"]
            promoted = sum(1 for p in confirmed
                          if p.id in program.cube.session.plane.units)
            program.last_discover = {
                "confirmed": len(confirmed),
                "promoted": promoted,
                "source": "nursery_confirmed_count",
            }
            messages.append(f"Confirmed: {len(confirmed)} (promoted to cube: {promoted})")
        elif lab.startswith("find_idea"):
            # Query promoted knowledge in cube by deterministic text match.
            query = lab[10:].strip()
            units = program.cube.session.plane.units
            matches = []
            if query:
                q = query.lower()
                for uid, unit in units.items():
                    text = f"{uid} {getattr(unit, 'label', '')} {getattr(unit, 'detail', '')}".lower()
                    if q in text:
                        matches.append({"id": uid, "label": getattr(unit, "label", uid)})
            program.last_discover = {
                "query": query,
                "matches": matches,
                "count": len(matches),
                "source": "cube_idea_search",
            }
            if not query:
                messages.append("find_idea requires a query term")
            else:
                messages.append(f"Found {len(matches)} ideas matching '{query}'")
                for m in matches[:10]:
                    messages.append(f"  {m['id']}: {m['label']}")
        else:
            ids = list(program.cube.session.plane.units.keys())
            ns = program.nursery.summary()
            program.last_discover = {"ids": ids, "count": len(ids), "nursery": ns.get("pending", 0)}
            st = program.avatar_status()
            messages.append(f"{st['look']}  {st['describe']}")
            messages.append(f"ideas={len(ids)} nursery={ns.get('pending', 0)}")
        program.last_core_i = {"dell": 35, "value": program.last_discover, "ok": True}
        return {**base, "ok": True, "error": ""}
    # DCC-VI: Dell 37 Nurture — nursery mutations via existing Nursery authority.
    # SAFE_ADAPTER: Nursery.add/confirm/reject are real, tested methods.
    # DCC-VII: confirm uses program.confirm_proposal (real promotion to cube).
    if n == 37:
        lab = label.strip()
        low = lab.lower()
        if low.startswith("confirm "):
            pid = lab[8:].strip()
            # Use canonical promotion authority: places in cube + confirms.
            # WO-5.1: User typed "confirm <id>" — carry explicit review context.
            # The direct nursery.confirm fallback is removed; coupled
            # acceptance must go through the canonical boundary.
            result = program.confirm_proposal(
                pid,
                _producer="repl_user",
                _review_context=program.make_review_context(pid, "repl_user"),
            )
            if result.get("ok"):
                program.last_nurture = {"action": "confirm", "pid": pid, "ok": True,
                                       "promoted": True}
                messages.append(f"Confirmed and promoted proposal: {pid}")
            else:
                program.last_nurture = {"action": "confirm", "pid": pid, "ok": False,
                                       "error": result.get("reason", "not found or not pending")}
                messages.append(f"Confirm failed: {pid} ({result.get('reason', 'not found')})")
                return {**base, "ok": False, "error": f"confirm failed: {pid}"}
        elif low.startswith("reject "):
            pid = lab[7:].strip()
            result = program.nursery.reject(pid)
            if result:
                program.last_nurture = {"action": "reject", "pid": pid, "ok": True}
                messages.append(f"Rejected proposal: {pid}")
            else:
                program.last_nurture = {"action": "reject", "pid": pid, "ok": False,
                                       "error": "not found or not pending"}
                messages.append(f"Reject failed: {pid} not found or not pending")
                return {**base, "ok": False, "error": f"reject failed: {pid}"}
        elif low.startswith("use_idea "):
            # DCC-VIII: Explicit knowledge consumption.
            # Format: "use_idea <pid>" or "use_idea <pid> to grow"
            rest = lab[9:].strip()
            # Extract PID (handle "to grow" suffix)
            if " to " in rest.lower():
                pid = rest[:rest.lower().index(" to ")].strip()
            else:
                pid = rest.split()[0] if rest.split() else ""

            # Validate: must be confirmed knowledge in cube
            prop = program.nursery.proposals.get(pid)
            if not prop:
                program.last_nurture = {"action": "use", "pid": pid, "ok": False,
                                       "error": "unknown knowledge ID"}
                messages.append(f"Use failed: unknown ID {pid}")
                return {**base, "ok": False, "error": f"unknown knowledge ID: {pid}"}
            if prop.status != "confirmed":
                program.last_nurture = {"action": "use", "pid": pid, "ok": False,
                                       "error": f"not confirmed (status={prop.status})"}
                messages.append(f"Use failed: {pid} is {prop.status}, not confirmed")
                return {**base, "ok": False, "error": f"knowledge not confirmed: {pid}"}
            if pid not in program.cube.session.plane.units:
                program.last_nurture = {"action": "use", "pid": pid, "ok": False,
                                       "error": "not promoted to cube"}
                messages.append(f"Use failed: {pid} not in cube")
                return {**base, "ok": False, "error": f"knowledge not in cube: {pid}"}

            # Record nursery state before growth
            before_ids = set(program.nursery.proposals.keys())

            # Run existing consumer: grow_ideas
            # WO-5.3: Explicit historical use — include superseded.
            # The user explicitly requested "use idea {pid} to grow".
            growth_result = program.grow_ideas(1, include_superseded=True)

            # Find offspring parented by this knowledge
            after_props = program.nursery.proposals
            offspring = []
            for new_id in set(after_props.keys()) - before_ids:
                new_prop = after_props[new_id]
                parents = getattr(new_prop, "parents", []) or []
                if pid in parents:
                    offspring.append({"id": new_id, "label": new_prop.label})

            program.last_nurture = {
                "action": "use",
                "pid": pid,
                "label": prop.label,
                "ok": True,
                "consumer": "grow_ideas",
                "offspring": offspring,
                "offspring_count": len(offspring),
                # DCC-XVI (CONTROL T): explicit use of a superseded unit
                # remains possible because the operator named the historical
                # ID explicitly — but the receipt identifies its lifecycle
                # state so the override is never silent.
                "lifecycle_state": _rev_state(program, pid),
            }
            messages.append(f"Used knowledge {pid} in growth")
            if program.last_nurture["lifecycle_state"] == "superseded":
                messages.append(f"  Note: {pid} is a superseded revision "
                                f"(explicit historical use)")
            messages.append(f"  Offspring parented by {pid}: {len(offspring)}")
            for o in offspring[:5]:
                messages.append(f"    {o['id']}: {o['label']}")
        elif low.startswith("supersede "):
            # DCC-XVI: versioned knowledge supersession through the normal
            # language/runtime path. Format: "supersede <old_id> with <words>".
            # Atomic: validate -> create successor -> confirm/promote
            # successor (predecessor stays active) -> prepare complete
            # revision links -> single durable commit -> auditable receipt.
            # Any failure before the commit restores the pre-supersession
            # state; a crash can never expose a half-superseded chain.
            from form.mandell.supersession import (
                SUPERSESSION_VERSION, SupersedeError, supersede_proposal,
            )
            rest = lab[len("supersede "):].strip()
            cut = rest.lower().find(" with ")
            if cut >= 0:
                old_id = rest[:cut].strip()
                words = rest[cut + len(" with "):].strip()
            else:
                old_id, words = rest, ""
            try:
                # WO-5.1 / Director 2026-10-05 (whole-circuit): REPL supersede
                # is an explicit user command — issue a bound approval
                # (predecessor version + proposed successor data) so the
                # operation authorizes before creating successor state.
                result = supersede_proposal(
                    program, old_id, words,
                    _producer="repl_user",
                    _review_context=program.make_supersede_context(
                        old_id, "repl_user", words, label=None),
                )
            except SupersedeError as e:
                program.last_nurture = {
                    "action": "supersede", "ok": False, "old_id": old_id,
                    "error": str(e), "consumer": "supersede_idea",
                    "dell": 37, "supersession_version": SUPERSESSION_VERSION,
                }
                messages.append(f"Supersede failed: {e}")
                return {**base, "ok": False, "error": f"supersede failed: {e}"}
            # supersede_proposal sets program.last_nurture for both success
            # and the deterministic already-superseded refusal.
            if result.get("ok"):
                messages.append(
                    f"Superseded {result['old_id']} with {result['new_id']}")
                messages.append(
                    f"  revision {result['revision_number']} "
                    f"of root {result['revision_root_id']}")
                return {**base, "ok": True}
            messages.append(
                f"Supersede refused ({result.get('reason')}): {old_id} "
                f"already superseded by {result.get('superseded_by_id')}")
            return {**base, "ok": False,
                    "error": result.get("reason") or "supersede refused"}
        elif low.startswith("resolve_conflict "):
            # DCC-XIX: operator-governed conflict disposition. Explicit
            # routing policy for one stable conflict -- never a truth
            # claim. Format: "resolve_conflict <conflict_id> prefer <unit_id>"
            # or "resolve_conflict <conflict_id> coexist".
            from form.mandell.conflict_disposition import (
                CONFLICT_DISPOSITION_VERSION, set_disposition,
            )
            rest = lab[len("resolve_conflict "):].strip()
            parts = rest.split()
            result = None
            if len(parts) >= 2 and parts[1].lower() == "prefer" and len(parts) >= 3:
                result = set_disposition(
                    program, parts[0], "prefer", [parts[2]])
            elif len(parts) >= 2 and parts[1].lower() == "coexist":
                result = set_disposition(program, parts[0], "coexist", [])
            if result is None:
                program.last_nurture = {
                    "action": "resolve_conflict", "ok": False,
                    "error": ("usage: resolve conflict <conflict_id> prefer <unit_id> "
                              "or resolve conflict <conflict_id> coexist"),
                    "consumer": "resolve_conflict", "dell": 37,
                    "conflict_disposition_version": CONFLICT_DISPOSITION_VERSION,
                }
                messages.append("Resolve conflict failed: unrecognized form")
                return {**base, "ok": False,
                        "error": "usage: resolve conflict <conflict_id> prefer <unit_id> "
                                 "or resolve conflict <conflict_id> coexist"}
            program.last_nurture = {
                "action": "resolve_conflict", "consumer": "resolve_conflict",
                "dell": 37, **result,
            }
            if result.get("ok"):
                if result.get("noop"):
                    messages.append(
                        f"Conflict {result['conflict_id']}: disposition unchanged "
                        f"({result['disposition']})")
                else:
                    messages.append(
                        f"Conflict {result['conflict_id']}: operator disposition "
                        f"'{result['disposition']}' recorded (routing only, not truth)")
                return {**base, "ok": True}
            messages.append(f"Resolve conflict failed: {result.get('error')}")
            return {**base, "ok": False,
                    "error": f"resolve conflict failed: {result.get('error')}"}
        elif low.startswith("clear_conflict_resolution "):
            # DCC-XIX: return one conflict to the default unresolved state.
            # Format: "clear_conflict_resolution <conflict_id>".
            from form.mandell.conflict_disposition import (
                CONFLICT_DISPOSITION_VERSION, clear_disposition,
            )
            cid = lab[len("clear_conflict_resolution "):].strip().split()
            cid = cid[0] if cid else ""
            result = clear_disposition(program, cid)
            program.last_nurture = {
                "action": "clear_conflict_resolution",
                "consumer": "clear_conflict_resolution",
                "dell": 37, **result,
            }
            if result.get("ok"):
                if result.get("noop"):
                    messages.append(
                        f"Conflict {cid}: already unresolved; nothing to clear")
                else:
                    messages.append(
                        f"Conflict {cid}: disposition cleared; default "
                        f"unresolved quarantine restored")
                return {**base, "ok": True}
            messages.append(f"Clear conflict resolution failed: {result.get('error')}")
            return {**base, "ok": False,
                    "error": f"clear conflict resolution failed: {result.get('error')}"}
        elif low.startswith("grow_using_knowledge_about "):
            # DCC-IX: Contextual knowledge selection.
            # Format: "grow_using_knowledge_about <context>"
            # EKC-I: "grow_using_knowledge_about <context> using <id1>,<id2>"
            from form.mandell.knowledge_selector import select_for_context
            rest = lab[27:].strip()
            if not rest:
                return {**base, "ok": False, "error": "context required"}
            # Parse explicit IDs (if " using " present)
            explicit_ids = None
            if " using " in rest.lower():
                # Split on last " using " (context may contain the word)
                idx = rest.lower().rfind(" using ")
                context = rest[:idx].strip()
                ids_part = rest[idx+7:].strip()
                explicit_ids = [i.strip() for i in ids_part.split(",") if i.strip()]
            else:
                context = rest
            if not context:
                return {**base, "ok": False, "error": "context required"}
            
            # Select relevant knowledge (with explicit choice if provided)
            selection = select_for_context(
                program, context, operation="grow", explicit_ids=explicit_ids
            )
            selected_ids = [s["id"] for s in selection["selected"]]
            
            # DCC-XI: validate scope at the consumer boundary (defense in
            # depth). The selector guarantees confirmed+promoted, but the
            # scope is re-verified here: unknown/pending/rejected can never
            # enter the consumer scope even if the selector were bypassed.
            plane = program.cube.session.plane
            for sid in selected_ids:
                prop = program.nursery.proposals.get(sid)
                if not prop or prop.status != "confirmed" or sid not in plane.units:
                    program.last_nurture = {
                        "action": "grow_contextual", "context": context,
                        "ok": False, "error": f"scope validation failed for {sid}",
                        "consumer": "grow_ideas", "dell": 37,
                        "dependency_version": selection.get("dependency_version"),
                        "dependency_valid_count": selection.get("dependency_valid_count"),
                        "dependency_exclusions": selection.get("dependency_exclusions", []),
                    "supersession_version": selection.get("supersession_version"),
                    "active_revision_count": selection.get("active_revision_count"),
                    "supersession_exclusions": selection.get("supersession_exclusions", []),
                    }
                    messages.append(f"Contextual grow refused: scope invalid for {sid}")
                    return {**base, "ok": False, "error": f"scope validation failed: {sid}"}
            
            # DCC-XIII: conflict-aware routing. Relevance (V2) answers which
            # knowledge matches the context; conflict routing answers which
            # selected knowledge can safely be combined. Every unit in >=1
            # detected polarity-conflict pair is quarantined; the consumer
            # receives exactly the routable subset (never a silent merge of
            # conflicting claims, never a full-plane fallback).
            # DCC-XIX: the conflict-routing gate is disposition-aware. An
            # explicit operator disposition (prefer/coexist) governs a
            # detected conflict for routing purposes only; absent a
            # disposition the DCC-XIII unresolved quarantine is preserved.
            # Disposition never alters relevance scores or widens the set.
            from form.mandell.conflict_router import (
                CONFLICT_VERSION, detect_conflicts,
            )
            from form.mandell.conflict_disposition import apply_dispositions
            from form.mandell.knowledge_selector import unit_text
            conflict_items = [
                {"id": s["id"], "text": unit_text(program, s["id"])}
                for s in selection["selected"]
            ]
            conflicts = detect_conflicts(conflict_items)
            routable_ids, quarantined_ids, disp_evidence = apply_dispositions(
                selected_ids, conflicts, program)

            # DCC-XIV: lineage/evidence structure (Lineage V1). Descriptive
            # metadata only: provenance is NOT truth. Built on the existing
            # lineage authority (parents/origin/lineage_version persisted on
            # every unit). A lineage failure must fail honestly before any
            # consumer runs — never widen scope or write stale metadata.
            from form.mandell.knowledge_lineage import (
                LINEAGE_VERSION, lineage_groups, selected_lineage,
                selected_root_ids,
            )
            try:
                sel_lineage = selected_lineage(program, selected_ids)
                sel_root_ids = selected_root_ids(program, selected_ids)
                lin_groups = lineage_groups(program, selected_ids)
            except Exception as e:
                program.last_nurture = {
                    "action": "grow_contextual", "context": context,
                    "eligible_count": selection["eligible_count"],
                    "selected_ids": selected_ids,
                    "conflict_version": CONFLICT_VERSION,
                    "conflicts": conflicts,
                    "conflict_count": len(conflicts),
                    "quarantined_ids": quarantined_ids,
                    "routable_selected_ids": routable_ids,
                    "conflict_disposition_version": disp_evidence["conflict_disposition_version"],
                    "conflict_dispositions": disp_evidence["conflict_dispositions"],
                    "conflict_policy_exclusions": disp_evidence["conflict_policy_exclusions"],
                    "stale_disposition_ids": disp_evidence["stale_disposition_ids"],
                    "invalid_disposition_ids": disp_evidence["invalid_disposition_ids"],
                    "lineage_version": LINEAGE_VERSION,
                    "dependency_version": selection.get("dependency_version"),
                    "dependency_valid_count": selection.get("dependency_valid_count"),
                    "dependency_exclusions": selection.get("dependency_exclusions", []),
                    "supersession_version": selection.get("supersession_version"),
                    "active_revision_count": selection.get("active_revision_count"),
                    "supersession_exclusions": selection.get("supersession_exclusions", []),
                    "ok": False,
                    "error": f"lineage construction failed: {type(e).__name__}: {e}",
                    "consumer": "grow_ideas", "dell": 37,
                    "scope_mode": "contextual",
                }
                messages.append(f"Contextual grow refused: lineage failed: {e}")
                return {**base, "ok": False, "error": f"lineage failed: {e}"}

            # Record state before
            before_ids = set(program.nursery.proposals.keys())
            
            # DCC-XI: scoped consumption with failure atomicity.
            # The consumer receives EXACTLY the routable IDs via a read-only
            # view; zero-match or all-quarantined yields an empty scope
            # (never silent fallback). On consumer failure, partial proposals
            # are removed and the receipt reports failure honestly.
            # P3 R3.5.1 — SELECTION → GROWTH HANDOFF CONTRACT (honest).
            #
            # What flows across this boundary: routable_ids — a list of ID
            # strings ONLY. The consumer (Program.grow_ideas →
            # RingedGrowth.run over a read-only ScopedPlaneView restricted
            # to exactly these IDs) enumerates pairs from those IDs and
            # recomputes affinity independently: _affinity derives its
            # harmonic/jaccard/spatial/goal/body terms from unit text,
            # goals, and plane coordinates. Selection never passes scores.
            #
            # What does NOT flow: selection scores. The Relevance V2
            # score (jaccard), coverage, exact_phrase, ordered, and
            # learned_scores are echoed in receipts/last_nurture for
            # audit only. Verified: no consumer in ringed_growth.py or
            # nursery.py reads a selection score (neither module
            # references one); the nursery Proposal records only the
            # consumer-computed affinity and reason (e.g. "Solstice
            # harm=0.43 goals=0.00").
            #
            # Why wiring scores is NOT justified: there is no consumer of
            # such scores in growth, and _affinity already owns the
            # jaccard term, computed deterministically from the same unit
            # text. Injecting selection scores would create a second
            # authority for that term. IDs-only stands unless a real
            # consumer appears.
            try:
                growth_result = program.grow_ideas(1, scope_ids=routable_ids)
            except Exception as e:
                for nid in set(program.nursery.proposals.keys()) - before_ids:
                    try:
                        del program.nursery.proposals[nid]
                    except KeyError:
                        pass
                program.last_nurture = {
                    "action": "grow_contextual", "context": context,
                    "eligible_count": selection["eligible_count"],
                    "selected_ids": selected_ids,
                    "conflict_version": CONFLICT_VERSION,
                    "conflicts": conflicts,
                    "conflict_count": len(conflicts),
                    "quarantined_ids": quarantined_ids,
                    "routable_selected_ids": routable_ids,
                    "conflict_disposition_version": disp_evidence["conflict_disposition_version"],
                    "conflict_dispositions": disp_evidence["conflict_dispositions"],
                    "conflict_policy_exclusions": disp_evidence["conflict_policy_exclusions"],
                    "stale_disposition_ids": disp_evidence["stale_disposition_ids"],
                    "invalid_disposition_ids": disp_evidence["invalid_disposition_ids"],
                    "lineage_version": LINEAGE_VERSION,
                    "selected_lineage": sel_lineage,
                    "selected_root_ids": sel_root_ids,
                    "root_count": len(sel_root_ids),
                    "lineage_groups": lin_groups,
                    "dependency_version": selection.get("dependency_version"),
                    "dependency_valid_count": selection.get("dependency_valid_count"),
                    "dependency_exclusions": selection.get("dependency_exclusions", []),
                    "supersession_version": selection.get("supersession_version"),
                    "active_revision_count": selection.get("active_revision_count"),
                    "supersession_exclusions": selection.get("supersession_exclusions", []),
                    "ok": False,
                    "error": f"consumer failed: {type(e).__name__}: {e}",
                    "consumer": "grow_ideas", "dell": 37,
                    "scope_mode": "contextual",
                }
                messages.append(f"Contextual grow failed: {e}")
                return {**base, "ok": False, "error": f"contextual growth failed: {e}"}
            
            # Consumer-echoed scope (direct evidence of what was consumed)
            consumer_scope_ids = growth_result.get("scope_ids")
            scope_mode = growth_result.get("scope_mode", "contextual")
            
            # Find new proposals
            after_ids = set(program.nursery.proposals.keys())
            new_ids = after_ids - before_ids
            new_count = len(new_ids)
            
            # DCC-X: per-item contribution via offspring parentage, over the
            # ROUTABLE set (DCC-XIII): quarantined conflict members never
            # enter the consumer, so no offspring may be attributed to them.
            # Technically provable: new proposals list parents; we count
            # how many new proposals each routable unit parented.
            routable_details = [s for s in selection["selected"]
                                if s["id"] in set(routable_ids)]
            contributions = []
            for s in routable_details:
                sid = s["id"]
                parented = []
                for nid in new_ids:
                    new_prop = program.nursery.proposals[nid]
                    parents = getattr(new_prop, "parents", []) or []
                    if sid in parents:
                        parented.append({"id": nid, "label": new_prop.label})
                contributions.append({
                    "id": sid,
                    "label": s["label"],
                    "score": s["score"],
                    "shared": s["shared"],
                    "offspring_count": len(parented),
                    "offspring_ids": [o["id"] for o in parented],
                })
            
            program.last_nurture = {
                "action": "grow_contextual",
                "context": context,
                "eligible_count": selection["eligible_count"],
                "selected_ids": selected_ids,
                "selection_reason": selection["reason"],
                "selected_details": selection["selected"],
                "ordering_rule": "relevance v2: exact_phrase DESC, ordered DESC, coverage DESC, jaccard DESC, proposal ID ASC",
                "selector_version": 2,
                "conflict_version": CONFLICT_VERSION,
                "conflicts": conflicts,
                "conflict_count": len(conflicts),
                "quarantined_ids": quarantined_ids,
                "routable_selected_ids": routable_ids,
                "conflict_disposition_version": disp_evidence["conflict_disposition_version"],
                "conflict_dispositions": disp_evidence["conflict_dispositions"],
                "conflict_policy_exclusions": disp_evidence["conflict_policy_exclusions"],
                "stale_disposition_ids": disp_evidence["stale_disposition_ids"],
                "invalid_disposition_ids": disp_evidence["invalid_disposition_ids"],
                "lineage_version": LINEAGE_VERSION,
                "selected_lineage": sel_lineage,
                "selected_root_ids": sel_root_ids,
                "root_count": len(sel_root_ids),
                "lineage_groups": lin_groups,
                "dependency_version": selection.get("dependency_version"),
                "dependency_valid_count": selection.get("dependency_valid_count"),
                "dependency_exclusions": selection.get("dependency_exclusions", []),
                    "supersession_version": selection.get("supersession_version"),
                    "active_revision_count": selection.get("active_revision_count"),
                    "supersession_exclusions": selection.get("supersession_exclusions", []),
                "contributions": contributions,
                "consumer_scope_ids": consumer_scope_ids,
                "scope_mode": scope_mode,
                # EKC-I: explicit choice provenance
                "explicit_choice": selection.get("explicit_choice", {
                    "requested": [], "resolutions": {}, "selected_explicit": [],
                }),
                "ok": True,
                "consumer": "grow_ideas",
                "dell": 37,
                "new_proposals": new_count,
            }
            messages.append(f"Contextual grow: '{context}'")
            messages.append(f"  Eligible: {selection['eligible_count']}, Selected: {len(selected_ids)}")
            messages.append(f"  Reason: {selection['reason']}")
            messages.append(f"  Conflicts: {len(conflicts)}, Quarantined: {quarantined_ids}, Routable: {len(routable_ids)}")
            disp_applied = [d for d in disp_evidence["conflict_dispositions"]
                            if d["disposition_applicable"]]
            if disp_applied:
                messages.append(
                    "  Dispositions: " + ", ".join(
                        f"{d['conflict_id'][:12]}...={d['disposition']}"
                        for d in disp_applied))
            messages.append(f"  Lineage roots: {len(sel_root_ids)} independent roots over {len(selected_ids)} selected")
            if selection.get("dependency_exclusions"):
                messages.append(f"  Dependency exclusions: {len(selection['dependency_exclusions'])}")
            if selection.get("supersession_exclusions"):
                messages.append(f"  Supersession exclusions: {len(selection['supersession_exclusions'])}")
            messages.append(f"  Scope mode: {scope_mode}, Consumer scope IDs: {consumer_scope_ids}")
            for s in selection["selected"][:3]:
                messages.append(f"    {s['id']}: {s['label']} (score={s['score']})")
            messages.append(f"  New proposals: {new_count}")
        else:
            # Default: add idea with label
            if not lab:
                return {**base, "ok": False, "error": "add idea requires a label"}
            proposal = program.nursery.add(lab)
            program.last_nurture = {"action": "add", "pid": proposal.id,
                                   "label": proposal.label, "ok": True}
            messages.append(f"Added idea: {proposal.id} ({proposal.label})")
        program.last_core_i = {"dell": 37, "value": program.last_nurture, "ok": True}
        return {**base, "ok": True, "error": ""}
    if n == 40:
        ideas = len(program.cube.session.plane.units)
        hist = len(getattr(program, "history", []))
        cells = len(program.lattice.cells)
        pending = program.nursery.summary().get("pending", 0)
        approx = ideas * 8 + hist * 4 + cells * 2 + pending * 6
        program.last_measure = {"value": approx, "ideas": ideas, "history": hist, "cells": cells, "pending": pending, "unit": "approx_units"}
        program.last_core_i = {"dell": 40, "value": program.last_measure, "ok": True}
        messages.append("TokenCount (approx session weight):")
        messages.append(f"  ideas={ideas} history={hist} cells={cells} pending={pending}")
        messages.append(f"  approx_units={approx}")
        return {**base, "ok": True, "error": ""}
    if n == 44:
        program.last_core_i = {"dell": 44, "ok": False, "error": "bridge_unavailable", "capability": label or "external", "permission": "offline_origin"}
        messages.append("Bridge unavailable: no external provider bound")
        return {**base, "ok": False, "error": "bridge_unavailable"}
    if n == 47:
        program.last_core_i = {"dell": 47, "ok": False, "error": "embed_unavailable", "representation": "none", "provider": ""}
        messages.append("Embed unavailable: no vector provider bound")
        return {**base, "ok": False, "error": "embed_unavailable"}
    return None
