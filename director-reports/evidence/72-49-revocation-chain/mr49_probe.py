"""72-49 failing-first probe: revocation-chain invalidation across
restart + retry as one contract, against AcceptancePolicy at the
checked-out code. Sequential processes only; session-A artifacts
cross the process boundary as a JSON file (handles/contexts are
plain data). No production code is modified.

Modes:
  parent            run the full contract sequence
  present <file>    fresh policy; present artifacts; print verdicts
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.getcwd())

from form.dell_matrix.acceptance_policy import AcceptancePolicy, canonical_hash

OWNER = "Owner49"
FAILURES = []


def expect(name, got, want):
    ok = got == want
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: allowed={got} want={want}")
    if not ok:
        FAILURES.append(name)


def check_all(p, art):
    """Present every session-A artifact to policy p. Returns verdicts."""
    v = {}
    for link in ("root", "child", "grandchild"):
        r = p.check("probe", "pid-target",
                    review_context={"grant_id": art["grants"][link]},
                    proposal_version=None, operation="confirm",
                    subject="agent-a", owner=OWNER)
        v[f"grant_{link}"] = bool(r.get("allowed"))
    r = p.check("probe", "pid-plain", review_context=art["plain_ctx"],
                proposal_version=art["plain_pv"], operation="confirm")
    v["plain"] = bool(r.get("allowed"))
    r = p.check("probe", "pid-plain2", review_context=art["plain2_ctx"],
                proposal_version=art["plain2_pv"], operation="confirm")
    v["plain2"] = bool(r.get("allowed"))
    r = p.check("probe", "succ-target", review_context=art["derived_ctx"],
                proposal_version=art["derived_pv"], operation="confirm")
    v["derived_appr"] = bool(r.get("allowed"))
    r = p.check("probe", "succ-target-2",
                review_context=art["derived_optin_ctx"],
                proposal_version=art["derived_pv"], operation="confirm")
    v["derived_optin"] = bool(r.get("allowed"))
    r = p.check("prod-x", "pid-any", review_context=None)
    v["optin_direct"] = bool(r.get("allowed"))
    return v


def issue_all(p):
    root = p.issue_grant(issuer="human", subject="agent-a", owner=OWNER,
                         operation="nursery.confirm", max_depth=3)
    child = p.attenuate_grant(parent_id=root["grant_id"])
    grandchild = p.attenuate_grant(parent_id=child["grant_id"])
    succ_hash = canonical_hash({"label": "V2", "words": "v2 words"})
    src = p.issue_approval(operation="supersede", target="pred-1",
                           reviewer="test", data={"successor": succ_hash})
    derived_data = {"content": {"label": "V2", "words": "v2 words"}}
    rel = {"type": "supersede_successor", "predecessor_id": "pred-1"}
    derived = p.derive_approval(source_approval_id=src["approval_id"],
                                source_opt_in=None, operation="confirm",
                                target="succ-target", reviewer="test",
                                data=derived_data, relationship=rel)
    p.grant_opt_in("prod-x", scope="test")
    derived_o = p.derive_approval(source_approval_id=None,
                                  source_opt_in="prod-x",
                                  operation="confirm",
                                  target="succ-target-2", reviewer="test",
                                  data=derived_data, relationship=rel)
    plain_data = {"k": "v"}
    plain = p.issue_approval(operation="confirm", target="pid-plain",
                             reviewer="test", data=plain_data)
    plain2_data = {"k": "v2"}
    plain2 = p.issue_approval(operation="confirm", target="pid-plain2",
                              reviewer="test", data=plain2_data)
    art = {
        "grants": {"root": root["grant_id"], "child": child["grant_id"],
                   "grandchild": grandchild["grant_id"]},
        "src_approval_id": src["approval_id"],
        "plain_ctx": plain["context"],
        "plain_pv": canonical_hash(plain_data),
        "plain2_ctx": plain2["context"],
        "plain2_pv": canonical_hash(plain2_data),
        "plain2_approval_id": plain2["approval_id"],
        "derived_ctx": derived["context"],
        "derived_optin_ctx": derived_o["context"],
        "derived_pv": canonical_hash(derived_data),
    }
    return art


ALL_LINKS = ("grant_root", "grant_child", "grant_grandchild", "plain",
             "plain2", "derived_appr", "derived_optin", "optin_direct")


def expect_matrix(tag, verdicts, wants):
    for link, want in wants.items():
        expect(f"{tag}:{link}", verdicts[link], want)


def parent():
    art_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "mr49_artifacts.json")
    a = AcceptancePolicy()
    art = issue_all(a)
    with open(art_path, "w", encoding="utf-8") as f:
        json.dump(art, f)

    print("== Phase 1: session A, pre-revocation positive controls ==")
    expect_matrix("A-pre", check_all(a, art), {k: True for k in ALL_LINKS})

    print("== Phase 2: mid-chain revocation in A, retry x2 ==")
    a.revoke_grant(art["grants"]["child"])
    a.revoke_approval(art["src_approval_id"])
    a.revoke_opt_in("prod-x")
    a.revoke_approval(art["plain2_approval_id"])
    wants2 = {"grant_root": True, "grant_child": False,
              "grant_grandchild": False, "plain": True, "plain2": False,
              "derived_appr": False, "derived_optin": False,
              "optin_direct": False}
    for i in (1, 2):
        expect_matrix(f"A-retry{i}", check_all(a, art), wants2)

    print("== Phase 3: restart = fresh policy in-process, retry x2 ==")
    b = AcceptancePolicy()
    for i in (1, 2):
        expect_matrix(f"B-retry{i}", check_all(b, art),
                      {k: False for k in ALL_LINKS})

    print("== Phase 4: restart = genuine child OS process ==")
    proc = subprocess.run(
        [sys.executable, os.path.abspath(__file__), "present", art_path],
        capture_output=True, text=True, cwd=os.getcwd())
    print(proc.stdout.strip())
    if proc.returncode != 0:
        expect("child_process_ran", False, True)
        print(proc.stderr[-2000:])
    else:
        verdicts = json.loads(proc.stdout.strip().splitlines()[-1])
        expect_matrix("C-child", verdicts, {k: False for k in ALL_LINKS})

    print("== Phase 5: re-issuance in new session B ==")
    new_root = b.issue_grant(issuer="human", subject="agent-a",
                             owner=OWNER, operation="nursery.confirm",
                             max_depth=1)
    r = b.check("probe", "pid-target",
                review_context={"grant_id": new_root["grant_id"]},
                proposal_version=None, operation="confirm",
                subject="agent-a", owner=OWNER)
    expect("B-new-grant", bool(r.get("allowed")), True)
    new_plain_data = {"k": "new"}
    new_plain = b.issue_approval(operation="confirm", target="pid-plain",
                                 reviewer="test", data=new_plain_data)
    r = b.check("probe", "pid-plain", review_context=new_plain["context"],
                proposal_version=canonical_hash(new_plain_data),
                operation="confirm")
    expect("B-new-approval", bool(r.get("allowed")), True)
    expect_matrix("B-old-still-denied", check_all(b, art),
                  {k: False for k in ALL_LINKS})

    print(f"PROBE VERDICT: {'CONTRACT HOLDS' if not FAILURES else 'FAILED: ' + ','.join(FAILURES)}")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "present":
        with open(sys.argv[2], encoding="utf-8") as f:
            artifacts = json.load(f)
        print(json.dumps(check_all(AcceptancePolicy(), artifacts)))
        sys.exit(0)
    sys.exit(parent())
