"""72-49 (= SM-32) — AcceptancePolicy revocation-chain invalidation
across restart + retry, as ONE contract.

Register gap (NBD Master Objective Register, 72-49): the pieces were
proven separately — in-session ancestor revocation (r61), a single
grant handle denied after a cross-process restart (r61 F2), revoked
plain approvals and derive-time blocking (wo51), the opt-in-sourced
derived child denied at execution (wo51) — but no suite bound the
full sequence for all three chain types at once:

  1. Build full chains in session A and verify EVERY link allows:
     grant root -> child -> grandchild; a plain approval; a second
     plain approval; a supersede approval -> derived child; an
     opt-in -> derived child; the opt-in itself.
  2. Revoke MID-CHAIN in A (the grant child, the supersede source,
     the opt-in, the second plain approval) and RETRY every link
     twice: descendants and unfinished children deny on both
     retries; the unrevoked root grant and the unrevoked plain
     approval still allow (revocation is surgical).
  3. RESTART: a fresh policy (new session) presented with ALL
     session-A artifacts — revoked and unrevoked alike — denies
     everything, on retry x2. Repeated both with an in-process
     fresh policy and in a genuine child OS process.
  4. RE-ISSUANCE in the new session: a new grant and a new approval
     allow, while the session-A artifacts STILL deny there.

The policy is in-memory by design (form/dell_matrix/
acceptance_policy.py): restart clears opt-ins, approvals and
grants. Committed history surviving restart is NOT re-proven here;
r61 F3 (cross-process reload) already proves it.

Evidence class: INTEGRATION (policy API, the canonical check()
boundary) + CROSS_PROCESS (phase 3 child). No canonical state is
written: the only file is a JSON artifacts hand-off in a temp dir.

Run: python3 -m form.sm32_revocation_chain_test
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}"
          + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        raise AssertionError(name)


OWNER = "OwnerSM32"
ALL_LINKS = ("grant_root", "grant_child", "grant_grandchild", "plain",
             "plain2", "derived_appr", "derived_optin", "optin_direct")


def _check_all(p, art):
    """Present every session-A artifact to policy p; return verdicts."""
    from form.dell_matrix.acceptance_policy import canonical_hash  # noqa: F401
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


def _issue_all(p):
    from form.dell_matrix.acceptance_policy import canonical_hash
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
    return {
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


def _expect_matrix(tag, verdicts, wants):
    for link, want in wants.items():
        check(f"{tag}:{link}", verdicts[link] is want,
              f"allowed={verdicts[link]} want={want}")


def _present_mode(path):
    from form.dell_matrix.acceptance_policy import AcceptancePolicy
    with open(path, encoding="utf-8") as f:
        art = json.load(f)
    print(json.dumps(_check_all(AcceptancePolicy(), art)))
    return 0


def run_all():
    from form.dell_matrix.acceptance_policy import (
        AcceptancePolicy, canonical_hash)

    a = AcceptancePolicy()
    art = _issue_all(a)

    # Phase 1: positive controls — every link allows in session A.
    _expect_matrix("A-pre", _check_all(a, art),
                   {k: True for k in ALL_LINKS})

    # Phase 2: mid-chain revocation, retry x2. Root grant and the
    # unrevoked plain approval must survive (surgical revocation).
    a.revoke_grant(art["grants"]["child"])
    a.revoke_approval(art["src_approval_id"])
    a.revoke_opt_in("prod-x")
    a.revoke_approval(art["plain2_approval_id"])
    wants2 = {"grant_root": True, "grant_child": False,
              "grant_grandchild": False, "plain": True, "plain2": False,
              "derived_appr": False, "derived_optin": False,
              "optin_direct": False}
    for i in (1, 2):
        _expect_matrix(f"A-retry{i}", _check_all(a, art), wants2)

    # Phase 3a: restart as a fresh in-process policy, retry x2.
    b = AcceptancePolicy()
    check("restart mints a new session", b.session_id != a.session_id)
    for i in (1, 2):
        _expect_matrix(f"B-retry{i}", _check_all(b, art),
                       {k: False for k in ALL_LINKS})

    # Phase 3b: restart as a genuine child OS process.
    tmp = tempfile.mkdtemp(prefix="sm32_")
    art_path = os.path.join(tmp, "artifacts.json")
    with open(art_path, "w", encoding="utf-8") as f:
        json.dump(art, f)
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    proc = subprocess.run(
        [sys.executable, "-m", "form.sm32_revocation_chain_test",
         "present", art_path],
        capture_output=True, text=True, cwd=root)
    check("child process ran", proc.returncode == 0, proc.stderr[-400:])
    verdicts = json.loads(proc.stdout.strip().splitlines()[-1])
    _expect_matrix("C-child", verdicts, {k: False for k in ALL_LINKS})

    # Phase 4: re-issuance in session B allows; session-A artifacts
    # still deny in B (no cross-session contamination either way).
    new_root = b.issue_grant(issuer="human", subject="agent-a",
                             owner=OWNER, operation="nursery.confirm",
                             max_depth=1)
    r = b.check("probe", "pid-target",
                review_context={"grant_id": new_root["grant_id"]},
                proposal_version=None, operation="confirm",
                subject="agent-a", owner=OWNER)
    check("B-new-grant allows", r.get("allowed") is True, str(r))
    new_plain_data = {"k": "new"}
    new_plain = b.issue_approval(operation="confirm", target="pid-plain",
                                 reviewer="test", data=new_plain_data)
    r = b.check("probe", "pid-plain", review_context=new_plain["context"],
                proposal_version=canonical_hash(new_plain_data),
                operation="confirm")
    check("B-new-approval allows", r.get("allowed") is True, str(r))
    _expect_matrix("B-old-still-denied", _check_all(b, art),
                   {k: False for k in ALL_LINKS})

    print(f"SM32: {sum(1 for _, c in RESULTS if c)}/{len(RESULTS)} GREEN")


def smoke() -> bool:
    try:
        run_all()
        return True
    except Exception as e:
        print(f"SM32 SMOKE FAILED: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "present":
        sys.exit(_present_mode(sys.argv[2]))
    run_all()
    sys.exit(0)
