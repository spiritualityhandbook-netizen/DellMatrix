#!/usr/bin/env python3
"""R6.4 fixed cross-process proof scripts (case data via JSON arguments).

Invoked as:
    python -m form.mandell.r64_child <command> '<json-args>'

Commands:
    issue_pair   {owner, label, words, subject, max_depth?}
                 -> {pid, grant_id, content_hash}
    coord_confirm {owner, subject, pid, grant_id, request_id,
                   content_hash?, correlation?}
                 -> receipt JSON (ok/result/reason)
    agent_observe {owner, subject, label}
                 -> {labels_seen, cells_explored} (IntrinsicAgent, then sync+save)
    agent_restore_check {owner, subject, expect_label?}
                 -> {labels_seen, has_label}
    audit_count  {owner} -> {count}
    rollback_advance {owner} -> {epoch}
    mark_recovery {owner, key, reason} -> {ok}
    clear_recovery {owner, key} -> {ok}

Each invocation runs in its own OS process. Grants are session-scoped:
a handle issued in one process MUST NOT authorize in another (fresh
AcceptancePolicy per process). Coordinator state (queue/receipts) is
per-process; durable state (program payload, audit, agent_local) is
shared via the owner's files.

Evidence class: CROSS_PROCESS (separate OS process per case, real
restart via fresh process + persist_rest.load).
"""

import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(REPO))


def cmd_issue_pair(args):
    from form.open import open_program
    from form.dell_matrix import agent_authority as aa
    p = open_program(args["owner"])
    pr = p.nursery.add(args["label"], words=args.get("words", "w"))
    pid = pr.id
    g = aa.issue_root_grant(p, issuer="human:ace", subject=args["subject"],
                            max_depth=int(args.get("max_depth", 2)))
    child = aa.attenuate_for(p, g["grant_id"], target=pid, content_pid=pid)
    print(json.dumps({
        "pid": pid,
        "grant_id": child["grant_id"],
        "content_hash": p.acceptance_data_hash(pid, "confirm"),
    }))


def cmd_coord_confirm(args):
    from form.open import open_program
    from form.dell_matrix import agent_coordinator as ac
    p = open_program(args["owner"])
    coord = ac.new_coordinator(p)
    coord.register_agent(args["subject"])
    surf = coord.surface_for(args["subject"])
    r = surf.request_confirm(
        args["pid"], args["grant_id"],
        request_id=args.get("request_id") or None,
        expected_content_hash=args.get("content_hash"),
        correlation=args.get("correlation"))
    # Strip non-JSON-safe internals for the wire.
    r.pop("writer_receipt", None)
    print(json.dumps({k: r.get(k) for k in
                      ("ok", "result", "reason", "detail", "request_id",
                       "idempotent_retry", "subject", "operation", "target")},
                     default=str))


def cmd_agent_observe(args):
    from form import persist_rest
    from form.dell_matrix import intrinsic_agent as ia
    # Load (not fresh): preserve existing durable state including audit.
    p = persist_rest.load(args["owner"], activate=False)
    agent = ia.for_agent(p, args["subject"])

    class Body:
        pos = (7, 7)
    class P:
        avatar = type("A", (), {"body": Body()})()
    agent.observe(P(), {"nodes": [{"label": args["label"]}]})
    ia.sync_agent_to_program(p, args["subject"])
    persist_rest.save(p)
    print(json.dumps({
        "labels_seen": sorted(agent.seen_labels),
        "cells_explored": len(agent.seen_cells),
    }))


def cmd_agent_restore_check(args):
    from form import persist_rest
    from form.dell_matrix import intrinsic_agent as ia
    p = persist_rest.load(args["owner"], activate=False)
    agent = ia.for_agent(p, args["subject"])
    expect = args.get("expect_label")
    print(json.dumps({
        "labels_seen": sorted(agent.seen_labels),
        "has_label": (expect in agent.seen_labels) if expect else None,
    }))


def cmd_audit_count(args):
    from form import persist_rest
    from form.dell_matrix import agent_coordinator as ac
    p = persist_rest.load(args["owner"], activate=False)
    print(json.dumps({"count": len(ac.list_agent_audit(p))}))


def cmd_rollback_advance(args):
    from form.mandell import core_i_recovery as rec
    rec._advance_rollback_epoch(args["owner"])
    print(json.dumps({"epoch": rec._rollback_epochs.get(
        rec._epoch_key(args["owner"]), 0)}))


def cmd_mark_recovery(args):
    from form.open import open_program
    from form.mandell import core_i_recovery as rec
    p = open_program(args["owner"])
    rec.mark_recovery_required(p, args["key"], args.get("reason", "test"))
    print(json.dumps({"ok": True}))


def cmd_clear_recovery(args):
    from form.open import open_program
    from form.mandell import core_i_recovery as rec
    p = open_program(args["owner"])
    rec.clear_recovery_required(p, args["key"])
    print(json.dumps({"ok": True}))


COMMANDS = {
    "issue_pair": cmd_issue_pair,
    "coord_confirm": cmd_coord_confirm,
    "agent_observe": cmd_agent_observe,
    "agent_restore_check": cmd_agent_restore_check,
    "audit_count": cmd_audit_count,
    "rollback_advance": cmd_rollback_advance,
    "mark_recovery": cmd_mark_recovery,
    "clear_recovery": cmd_clear_recovery,
}


def main(argv):
    if len(argv) != 3 or argv[1] not in COMMANDS:
        print(json.dumps({"error": "usage: r64_child <command> '<json>'"}))
        return 2
    COMMANDS[argv[1]](json.loads(argv[2]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
