#!/usr/bin/env python3
"""R6.5 verification-only child (no issuance or mutation).

Takes JSON arguments via argv[1]:
{
  "owner": "<unique owner>",
  "confirmed_pid": "<pid>",
  "pending_pid": "<pid>",
  "expected_confirmed_words": "<exact words>",
  "expected_pending_words": "<exact words>",
  "expected_audit": [...]
}

Loads and compares only. No grants issued, no mutations.
Outputs JSON with assertions. Exit 0 iff all pass.
"""

import json
import sys

def main():
    try:
        args = json.loads(sys.argv[1])
        owner = args["owner"]
        confirmed_pid = args["confirmed_pid"]
        pending_pid = args["pending_pid"]
        expected_confirmed_words = args["expected_confirmed_words"]
        expected_pending_words = args["expected_pending_words"]
        expected_audit = args.get("expected_audit", [])

        sys.path.insert(0, ".")
        from form import persist_rest as pr
        from form.dell_matrix import agent_coordinator as ac

        p3 = pr.load(owner, activate=False)
        results = {}

        def get_unit(pid):
            plane = p3.cube.session.plane
            units = getattr(plane, "units", {}) or {}
            return units.get(pid)

        # Verify confirmed proposal.
        prop = p3.nursery.proposals[confirmed_pid]
        results["verify_confirmed_status"] = (str(prop.status) == "confirmed")
        results["verify_confirmed_words"] = (
            str(prop.words) == expected_confirmed_words
        )
        unit = get_unit(confirmed_pid)
        results["verify_confirmed_plane"] = (unit is not None)
        if unit:
            results["verify_confirmed_plane_content"] = (
                str(getattr(unit, "words", "")) == expected_confirmed_words
            )
        else:
            results["verify_confirmed_plane_content"] = False

        # Verify reissued (now confirmed) proposal.
        pend = p3.nursery.proposals[pending_pid]
        results["verify_pending_confirmed"] = (str(pend.status) == "confirmed")
        results["verify_pending_words"] = (
            str(pend.words) == expected_pending_words
        )
        punit = get_unit(pending_pid)
        results["verify_pending_plane"] = (punit is not None)
        if punit:
            results["verify_pending_plane_content"] = (
                str(getattr(punit, "words", "")) == expected_pending_words
            )
        else:
            results["verify_pending_plane_content"] = False

        # Verify audit records.
        try:
            audit_records = ac.list_agent_audit(p3)
        except Exception:
            audit_records = []
        for exp in expected_audit:
            found = any(
                str(r.get("request_id", "")) == exp["request_id"]
                and str(r.get("subject", "")) == exp["subject"]
                for r in audit_records
            )
            results[f"verify_audit_{exp['request_id']}"] = found

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
