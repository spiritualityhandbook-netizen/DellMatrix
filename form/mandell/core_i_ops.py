#!/usr/bin/env python3
"""Locally closable Core I arms that wrap the leaf without rewriting it."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

HANDLED = {27, 28, 34, 35, 37, 40, 44, 47}


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
            cp = checkpoint(program, stamp=label or None)
            program.last_core_i = {"dell": 27, "path": cp, "ok": True}
            messages.append(f"Checkpoint written: {cp}")
            return {**base, "ok": True, "error": ""}
        except Exception as exc:
            program.last_core_i = {"dell": 27, "ok": False, "error": str(exc)}
            messages.append(f"Checkpoint fail: {exc}")
            return {**base, "ok": False, "error": str(exc)}
    if n == 28:
        from .core_i_recovery import rollback
        target = label if label.endswith(".json") else getattr(program, "last_checkpoint", None)
        try:
            restored = rollback(program.owner, target)
            program.last_core_i = {"dell": 28, "ok": True}
            messages.append("Checkpoint restored.")
            return {**base, "ok": True, "error": "", "new_program": restored}
        except FileNotFoundError:
            program.last_core_i = {"dell": 28, "ok": False, "error": "rollback_missing"}
            messages.append("Rollback missing checkpoint")
            return {**base, "ok": False, "error": "rollback_missing"}
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
            if hasattr(program, "confirm_proposal"):
                result = program.confirm_proposal(pid)
            else:
                result = program.nursery.confirm(pid)
                result = {"ok": bool(result), "id": pid} if result else {"ok": False}
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
