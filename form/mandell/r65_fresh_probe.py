#!/usr/bin/env python3
"""R6.5 fresh-process restart probe (fixed child script).

Takes JSON arguments via argv[1]:
{
  "owner": "r65s1",
  "confirmed_pid": "<pid of already-confirmed proposal>",
  "pending_pid": "<pid of pending proposal>",
  "old_grant_id": "<grant ID from before restart>",
  "expected_words": "<words of pending proposal>"
}

Outputs JSON to stdout:
{
  "returncode": 0,
  "assertions": {
    "confirmed_status_exact": bool,
    "confirmed_words_match": bool,
    "old_grant_denied_same_target": bool,
    "no_mutation": bool,
    "reissued_succeeds": bool
  }
}

Exit code 0 on success, 1 on any assertion failure.
Exit code 2 on unexpected exception.
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
        expected_words = args["expected_words"]

        sys.path.insert(0, ".")
        from form import persist_rest as pr
        from form.dell_matrix import agent_coordinator as ac
        from form.dell_matrix import agent_authority as aa
        from form.dell_matrix.agent_coordinator import make_envelope

        p2 = pr.load(owner, activate=False)
        results = {}

        # (a) Exact status of confirmed proposal.
        prop = p2.nursery.proposals[confirmed_pid]
        results["confirmed_status_exact"] = (str(prop.status) == "confirmed")
        results["confirmed_words_match"] = (
            str(prop.words) == "separation test idea words"
        )

        # (b) Old grant against SAME pending target must deny.
        coord = ac.new_coordinator(p2)
        coord.register_agent("agent-a")
        # Capture pre-state.
        pre_status = str(p2.nursery.proposals[pending_pid].status)
        pre_words = str(p2.nursery.proposals[pending_pid].words)

        h = p2.acceptance_data_hash(pending_pid, "confirm")
        env = make_envelope(
            request_id="r65-fresh-old",
            operation="confirm", target=pending_pid,
            expected={"content_hash": h}, _program=p2)
        qid = coord.enqueue("agent-a", env)
        r = coord.dispatch(qid, old_grant_id)
        results["old_grant_denied_same_target"] = (r["ok"] is False)

        # (c) No mutation from denied attempt.
        post_status = str(p2.nursery.proposals[pending_pid].status)
        post_words = str(p2.nursery.proposals[pending_pid].words)
        results["no_mutation"] = (
            pre_status == post_status and pre_words == post_words
            and pre_words == expected_words
        )

        # (d) Reissue for same target succeeds.
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

        # Output structured results.
        output = {"returncode": 0, "assertions": results}
        print(json.dumps(output))
        # Exit 0 only if all assertions pass.
        sys.exit(0 if all(results.values()) else 1)

    except Exception as e:
        print(json.dumps({"returncode": 2, "error": str(e)}))
        sys.exit(2)

if __name__ == "__main__":
    main()
