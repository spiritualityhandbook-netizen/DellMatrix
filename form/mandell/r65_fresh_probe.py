#!/usr/bin/env python3
"""R6.5 fresh-process restart probe (fixed child script).

Takes JSON arguments via argv[1]:
{
  "owner": "<unique owner>",
  "confirmed_pid": "<pid>",
  "pending_pid": "<pid>",
  "old_grant_id": "<grant ID from before restart>",
  "expected_confirmed_words": "<exact words>",
  "expected_pending_words": "<exact words>",
  "expected_audit": [
    {"request_id": "...", "subject": "...", "target": "...", "result": "..."}
  ]
}

Uses plane.units[pid] for exact Idea identity (not label search).
Outputs JSON with assertions. Exit 0 iff all pass. Exit 2 on exception.
"""

import json
import sys

def main():
    try:
        args = json.loads(sys.argv[1])
        owner = args["owner"]
        confirmed_pid = args["confirmed_pid"]
        pending_pid = args["pending_pid"]
        old_grant_id = args["old_grant_id"]
        expected_confirmed_words = args["expected_confirmed_words"]
        expected_pending_words = args["expected_pending_words"]
        expected_audit = args.get("expected_audit", [])

        sys.path.insert(0, ".")
        from form import persist_rest as pr
        from form.dell_matrix import agent_coordinator as ac
        from form.dell_matrix import agent_authority as aa
        from form.dell_matrix.agent_coordinator import make_envelope

        p2 = pr.load(owner, activate=False)
        results = {}

        def get_unit(pid):
            plane = p2.cube.session.plane
            units = getattr(plane, "units", {}) or {}
            return units.get(pid)

        # (a) Confirmed proposal: exact status and words.
        prop = p2.nursery.proposals[confirmed_pid]
        results["confirmed_status_exact"] = (str(prop.status) == "confirmed")
        results["confirmed_words_exact"] = (
            str(prop.words) == expected_confirmed_words
        )

        # (b) Confirmed Idea in Plane by EXACT pid key.
        unit = get_unit(confirmed_pid)
        results["confirmed_idea_in_plane"] = (unit is not None)
        if unit is not None:
            results["plane_content_exact"] = (
                str(getattr(unit, "words", "")) == expected_confirmed_words
            )
        else:
            results["plane_content_exact"] = False

        # (c) Audit records survive: compare captured expectations.
        # Use list_agent_audit to get actual records.
        audit_records = ac.list_agent_audit(p2)  # Do not swallow errors.
        # Require nonempty expectations.
        results["audit_expectations_nonempty"] = len(expected_audit) > 0
        # Check each expected record is present with matching result.
        for exp in expected_audit:
            found = any(
                str(r.get("request_id", "")) == exp["request_id"]
                and str(r.get("subject", "")) == exp["subject"]
                and str(r.get("target", "")) == exp["target"]
                and str(r.get("result", "")) == exp["result"]
                for r in audit_records
            )
            results[f"audit_{exp['request_id']}"] = found
        results["audit_nonempty"] = len(audit_records) > 0
        # Negative control: empty expectations must fail (not vacuously pass).
        # (This is verified by the parent requiring nonempty above.)
        # Negative control: changed result must not match.
        fake_exp = {"request_id": "r65-restart-confirm",
                    "subject": "agent-a", "target": confirmed_pid,
                    "result": "CHANGED_RESULT"}
        fake_found = any(
            str(r.get("request_id", "")) == fake_exp["request_id"]
            and str(r.get("result", "")) == fake_exp["result"]
            for r in audit_records
        )
        results["audit_changed_result_fails"] = (fake_found is False)

        # (d) Pending proposal: status==pending and pid NOT in plane.units.
        pend_prop = p2.nursery.proposals[pending_pid]
        results["pending_status_exact"] = (
            str(pend_prop.status) == "pending"
        )
        results["pending_absent_from_plane"] = (
            get_unit(pending_pid) is None
        )

        # (e) Old grant against SAME pending target must deny.
        coord = ac.new_coordinator(p2)
        coord.register_agent("agent-a")
        h = p2.acceptance_data_hash(pending_pid, "confirm")
        env = make_envelope(
            request_id="r65-fresh-old",
            operation="confirm", target=pending_pid,
            expected={"content_hash": h}, _program=p2)
        qid = coord.enqueue("agent-a", env)
        r = coord.dispatch(qid, old_grant_id)
        results["old_grant_denied_same_target"] = (r["ok"] is False)

        # (f) Denial preserves pending state AND Idea absence.
        post_prop = p2.nursery.proposals[pending_pid]
        results["denial_preserves_pending"] = (
            str(post_prop.status) == "pending"
        )
        results["denial_preserves_absence"] = (
            get_unit(pending_pid) is None
        )

        # (g) Reissue for same target: confirmed + exact Plane content.
        grant2 = aa.issue_root_grant(
            p2, issuer="test-host", subject="agent-a",
            target=pending_pid, content_pid=pending_pid)
        h2 = p2.acceptance_data_hash(pending_pid, "confirm")
        env2 = make_envelope(
            request_id="r65-fresh-new",
            operation="confirm", target=pending_pid,
            expected={"content_hash": h2}, _program=p2)
        qid2 = coord.enqueue("agent-a", env2)
        r2 = coord.dispatch(qid2, grant2["grant_id"])
        results["reissued_succeeds"] = (r2["ok"] is True)
        final_prop = p2.nursery.proposals[pending_pid]
        results["reissued_confirmed_status"] = (
            str(final_prop.status) == "confirmed"
        )
        final_unit = get_unit(pending_pid)
        results["reissued_idea_in_plane"] = (final_unit is not None)
        if final_unit is not None:
            results["reissued_plane_content_exact"] = (
                str(getattr(final_unit, "words", "")) == expected_pending_words
            )
        else:
            results["reissued_plane_content_exact"] = False

        # Save for the verification-only child.
        pr.save(p2)

        output = {"returncode": 0, "assertions": results}
        print(json.dumps(output))
        sys.exit(0 if all(results.values()) else 1)

    except Exception as e:
        import traceback
        print(json.dumps({"returncode": 2, "error": str(e),
                          "trace": traceback.format_exc()[:500]}))
        sys.exit(2)

if __name__ == "__main__":
    main()
