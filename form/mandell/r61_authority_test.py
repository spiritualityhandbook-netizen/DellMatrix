"""R6.1 capability-authority proofs (GDP_PHASE_6_CAPABILITY_AUTHORITY_CIRCUIT).

Proves the complete authority circuit for the nursery.confirm capability:

- human-approved root -> attenuated agent grant -> public Nursery
  confirm -> canonical writer checks -> durable commit -> receipt ->
  reload proves acceptance
- missing/forged/edited credentials deny with no mutation
- operation/target/content/subject/owner/session mismatch denies
- privilege expansion and unrelated derivation are rejected at
  attenuation time
- ancestor revocation, session reset, and process restart invalidate
  grants; committed history survives revocation/restart
- post-dispatch revocation and content changes deny at the writer
  boundaries (pre-place / pre-commit)
- persona changes do not alter permission (PERSONA != PERMISSION)
- denied attempts preserve accepted state and recovery evidence
- incomplete compensation still blocks every exposed persistence path
- sensitivity: disabling the canonical checks makes the negative
  controls fail (proofs are non-vacuous)

Evidence classes: INTEGRATION (real Program, real writer, per-owner
isolation) and CROSS_PROCESS (fixed child scripts via JSON arguments,
separate OS process per case).
"""

import glob
import json
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# NOTE: REPO is the form/ directory; the state dir lives under the
# repository root, one level up.
ROOT = os.path.dirname(REPO)
sys.path.insert(0, ROOT)

CHECKS = []


def check(name, cond, detail=""):
    CHECKS.append(bool(cond))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f" | {detail}" if detail and not cond else ""))


def clean_owner(owner):
    for pat in [f'form/state/nursery_{owner}.json',
                f'form/state/program_{owner}.json']:
        pp = os.path.join(ROOT, pat)
        if os.path.isfile(pp):
            os.remove(pp)
    for pat in glob.glob(os.path.join(ROOT, 'form', 'state',
                                      f'checkpoint_{owner}_*')):
        os.remove(pat)
    from form.mandell.core_i_recovery import _confirm_journal_path
    jp = _confirm_journal_path(owner)
    if not os.path.isabs(jp):
        jp = os.path.join(ROOT, jp)
    if os.path.isfile(jp):
        os.remove(jp)


def fresh_program(owner):
    from form.open import open_program
    clean_owner(owner)
    return open_program(owner)


def mkpair(p, pid, subject="agent-a", target=None, bind_content=True,
           max_depth=1, issuer="human:ace"):
    """Trusted issuance: root grant + attenuated child. Returns (root, child)."""
    from form.dell_matrix import agent_authority as aa
    root = aa.issue_root_grant(p, issuer=issuer, subject=subject,
                               max_depth=max_depth)
    child = aa.attenuate_for(p, root["grant_id"],
                             target=target if target is not None else pid,
                             content_pid=pid if bind_content else None)
    return root, child


def run_child(cmd, args):
    # REPO names the form/ dir (repo convention); the child needs the
    # repository root as its working directory.
    proc = subprocess.run(
        [sys.executable, "-m", "form.mandell.r61_child", cmd,
         json.dumps(args)],
        cwd=os.path.dirname(REPO), capture_output=True, text=True,
        timeout=120)
    try:
        return json.loads(proc.stdout.strip().splitlines()[-1])
    except Exception:
        return {"error": f"child failed rc={proc.returncode} "
                         f"stderr={proc.stderr[:300]}"}


def durable_has_unit(owner, pid, label):
    """Durable bytes: program file records the unit under plane/units."""
    pp = os.path.join(ROOT, 'form', 'state', f'program_{owner}.json')
    if not os.path.isfile(pp):
        return False
    try:
        data = json.load(open(pp))
    except Exception:
        return False
    units = (data.get("plane") or {}).get("units", {})
    rec = units.get(pid)
    return bool(rec) and rec.get("label") == label


# ---------------------------------------------------------------- A. skeleton

def test_root_grant_confirm_reload():
    from form.dell_matrix import agent_authority as aa
    owner = "R61_A1"
    p = fresh_program(owner)
    pr = p.nursery.add("AlphaProp", words="alpha words")
    pid = pr.id
    root, child = mkpair(p, pid)
    r = aa.agent_confirm(p, pid, child["grant_id"], "agent-a")
    check("A1:confirm_ok", r.get("ok") is True, str(r))
    check("A1:receipt_names_pid", r.get("id") == pid, str(r))
    check("A1:status_confirmed", p.nursery.proposals[pid].status == "confirmed")
    check("A1:plane_inventory", pid in p.cube.session.plane.units)
    check("A1:durable_bytes", durable_has_unit(owner, pid, "AlphaProp"))
    # Reload through the production loader proves durable acceptance.
    from form import persist_rest
    p2 = persist_rest.load(owner, activate=False)
    check("A1:reload_status", p2.nursery.proposals[pid].status == "confirmed")
    check("A1:reload_on_plane", pid in p2.cube.session.plane.units)
    check("A1:reload_label",
          p2.cube.session.plane.units[pid].label == "AlphaProp")


def test_human_confirm_still_works():
    owner = "R61_A3"
    p = fresh_program(owner)
    pr = p.nursery.add("HumanProp", words="human words")
    ctx = p.make_review_context(pr.id, reviewer="human:ace")
    r = p.confirm_proposal(pr.id, _producer="repl_user", _review_context=ctx)
    check("A3:human_confirm_ok", r.get("ok") is True, str(r))
    check("A3:human_status", p.nursery.proposals[pr.id].status == "confirmed")


def test_opt_in_still_works_and_revocable():
    owner = "R61_A4"
    p = fresh_program(owner)
    pr = p.nursery.add("OptProp", words="opt words")
    p.acceptance_policy.grant_opt_in("auto_growth", scope="test")
    r = p.confirm_proposal(pr.id, _producer="auto_growth")
    check("A4:optin_confirm_ok", r.get("ok") is True, str(r))
    pr2 = p.nursery.add("OptProp2", words="opt words 2")
    p.acceptance_policy.revoke_opt_in("auto_growth")
    r2 = p.confirm_proposal(pr2.id, _producer="auto_growth")
    check("A4:optin_revoked_denies", r2.get("ok") is False)


# ---------------------------------------------------------------- B. credential negatives

def test_missing_credential_denies():
    owner = "R61_B1"
    p = fresh_program(owner)
    pr = p.nursery.add("NoCred", words="x")
    r = p.confirm_proposal(pr.id, _producer="agent:x")
    check("B1:deny", r.get("ok") is False and r.get("reason") == "acceptance_policy_denied",
          str(r))
    check("B1:still_pending", p.nursery.proposals[pr.id].status == "pending")
    check("B1:no_unit", pr.id not in p.cube.session.plane.units)


def test_forged_handle_denies():
    from form.dell_matrix import agent_authority as aa
    owner = "R61_B2"
    p = fresh_program(owner)
    pr = p.nursery.add("Forged", words="x")
    r = aa.agent_confirm(p, pr.id, "grant_" + "0" * 32, "agent-a")
    check("B2:deny", r.get("ok") is False, str(r))
    check("B2:still_pending", p.nursery.proposals[pr.id].status == "pending")


def test_edited_handle_denies():
    from form.dell_matrix import agent_authority as aa
    owner = "R61_B3"
    p = fresh_program(owner)
    pr = p.nursery.add("Edited", words="x")
    root, child = mkpair(p, pr.id)
    gid = child["grant_id"]
    edited = gid[:-1] + ("0" if gid[-1] != "0" else "1")
    assert edited != gid
    r = aa.agent_confirm(p, pr.id, edited, "agent-a")
    check("B3:deny", r.get("ok") is False, str(r))
    check("B3:still_pending", p.nursery.proposals[pr.id].status == "pending")
    # The unedited handle still works (edit did not corrupt the record).
    r2 = aa.agent_confirm(p, pr.id, gid, "agent-a")
    check("B3:original_still_valid", r2.get("ok") is True, str(r2))


def test_copied_dict_confers_nothing():
    owner = "R61_B4"
    p = fresh_program(owner)
    pr = p.nursery.add("CopiedDict", words="x")
    _, child = mkpair(p, pr.id)
    gid = child["grant_id"]
    # Attacker copies the handle but claims a different subject inside
    # the dict: the dict's subject is ignored; the trusted binding governs.
    r = p.confirm_proposal(pr.id, _producer="agent:attacker",
                            _review_context={"grant_id": gid,
                                             "subject": "attacker"},
                            _operation="confirm", _subject="attacker")
    check("B4:dict_subject_ignored", r.get("ok") is False, str(r))
    # Attacker replays the real handle but the trusted dispatcher binds
    # a different subject than the grant's: the dict cannot override it.
    r2 = p.confirm_proposal(pr.id, _producer="agent:attacker",
                             _review_context={"grant_id": gid,
                                              "subject": "agent-a"},
                             _operation="confirm", _subject="attacker")
    check("B4:replay_wrong_binding_denies", r2.get("ok") is False, str(r2))
    check("B4:still_pending", p.nursery.proposals[pr.id].status == "pending")


def test_grant_without_trusted_subject_denies():
    owner = "R61_B5"
    p = fresh_program(owner)
    pr = p.nursery.add("NoSubject", words="x")
    _, child = mkpair(p, pr.id)
    r = p.confirm_proposal(pr.id, _producer="agent:a",
                            _review_context={"grant_id": child["grant_id"]},
                            _operation="confirm", _subject=None)
    check("B5:deny", r.get("ok") is False, str(r))
    check("B5:detail_mentions_binding",
          "subject" in str(r.get("detail", "")).lower(), str(r.get("detail")))


def test_no_handle_in_audit_or_receipts():
    from form.dell_matrix import agent_authority as aa
    owner = "R61_B6"
    p = fresh_program(owner)
    pr = p.nursery.add("NoLeak", words="x")
    root, child = mkpair(p, pr.id)
    r_ok = aa.agent_confirm(p, pr.id, child["grant_id"], "agent-a")
    r_bad = aa.agent_confirm(p, pr.id, "grant_" + "f" * 32, "agent-a")
    handles = [root["grant_id"], child["grant_id"]]
    blob = json.dumps(p.acceptance_policy.audit_log()) + json.dumps(r_ok) + json.dumps(r_bad)
    leaked = [h for h in handles if h in blob]
    check("B6:no_handle_leaked", leaked == [], f"leaked={leaked}")
    check("B6:describe_has_no_handles",
          all("grant_id" not in d for d in
              p.acceptance_policy.describe_grants()))


# ---------------------------------------------------------------- C. scope mismatches

def test_operation_mismatch_denies():
    from form.dell_matrix import agent_authority as aa
    owner = "R61_C1"
    p = fresh_program(owner)
    pr = p.nursery.add("OpMis", words="x")
    _, child = mkpair(p, pr.id)
    r = p.confirm_proposal(pr.id, _producer="agent:a",
                            _review_context={"grant_id": child["grant_id"]},
                            _operation="supersede", _subject="agent-a")
    check("C1:deny", r.get("ok") is False, str(r))
    check("C1:still_pending", p.nursery.proposals[pr.id].status == "pending")


def test_target_mismatch_denies():
    from form.dell_matrix import agent_authority as aa
    owner = "R61_C2"
    p = fresh_program(owner)
    pa = p.nursery.add("TargetA", words="a")
    pb = p.nursery.add("TargetB", words="b")
    _, child = mkpair(p, pa.id, target=pa.id)
    r = aa.agent_confirm(p, pb.id, child["grant_id"], "agent-a")
    check("C2:deny", r.get("ok") is False, str(r))
    check("C2:both_pending",
          p.nursery.proposals[pa.id].status == "pending"
          and p.nursery.proposals[pb.id].status == "pending")


def test_content_mismatch_denies():
    from form.dell_matrix import agent_authority as aa
    owner = "R61_C3"
    p = fresh_program(owner)
    pr = p.nursery.add("ContentC", words="original words")
    _, child = mkpair(p, pr.id, bind_content=True)
    pr.words = "tampered words"
    r = aa.agent_confirm(p, pr.id, child["grant_id"], "agent-a")
    check("C3:deny", r.get("ok") is False, str(r))
    check("C3:still_pending", p.nursery.proposals[pr.id].status == "pending")


def test_subject_mismatch_denies():
    from form.dell_matrix import agent_authority as aa
    owner = "R61_C4"
    p = fresh_program(owner)
    pr = p.nursery.add("SubjMis", words="x")
    _, child = mkpair(p, pr.id, subject="agent-a")
    r = aa.agent_confirm(p, pr.id, child["grant_id"], "agent-b")
    check("C4:deny", r.get("ok") is False, str(r))
    check("C4:detail", "subject" in str(r.get("detail", "")).lower(),
          str(r.get("detail")))


def test_owner_mismatch_denies():
    from form.dell_matrix import agent_authority as aa
    owner = "R61_C5"
    p = fresh_program(owner)
    pr = p.nursery.add("OwnerMis", words="x")
    # Trusted path issues for a DIFFERENT owner scope on this program.
    g = p.acceptance_policy.issue_grant(
        issuer="human:ace", subject="agent-a", owner="someone-else",
        operation="nursery.confirm", max_depth=0)
    r = aa.agent_confirm(p, pr.id, g["grant_id"], "agent-a")
    check("C5:deny", r.get("ok") is False, str(r))
    check("C5:detail", "owner" in str(r.get("detail", "")).lower(),
          str(r.get("detail")))


# ---------------------------------------------------------------- D. attenuation negatives

def _raises_approval(p, fn, name):
    from form.dell_matrix.acceptance_policy import ApprovalError
    try:
        fn()
    except ApprovalError:
        check(name, True)
        return
    except Exception as e:
        check(name, False, f"wrong exc {type(e).__name__}: {e}")
        return
    check(name, False, "no exception raised")


def test_expansion_rejected():
    from form.dell_matrix import agent_authority as aa
    owner = "R61_D1"
    p = fresh_program(owner)
    pr = p.nursery.add("ExpA", words="x")
    root = aa.issue_root_grant(p, issuer="human:ace", subject="agent-a",
                               max_depth=2)
    child = aa.attenuate_for(p, root["grant_id"], target=pr.id)
    # Parent bound to pr.id: child for another target is expansion.
    _raises_approval(p, lambda: aa.attenuate_for(p, child["grant_id"],
                                                target="other-pid"),
                     "D1:target_widen_rejected")
    # Parent unbound: child may narrow (not expansion) ...
    ok_child = aa.attenuate_for(p, root["grant_id"], target=pr.id)
    check("D1:narrow_from_unbound_ok", ok_child.get("ok") is True)
    # ... but may not rebind content once bound.
    bound = aa.attenuate_for(p, root["grant_id"], target=pr.id,
                             content_pid=pr.id)
    _raises_approval(
        p, lambda: p.acceptance_policy.attenuate_grant(
            parent_id=bound["grant_id"],
            content={"label": "different", "words": "x"}),
        "D1:content_rebind_rejected")


def test_subject_owner_reassignment_rejected():
    from form.dell_matrix import agent_authority as aa
    owner = "R61_D2"
    p = fresh_program(owner)
    root = aa.issue_root_grant(p, issuer="human:ace", subject="agent-a",
                               max_depth=1)
    _raises_approval(
        p, lambda: p.acceptance_policy.attenuate_grant(
            parent_id=root["grant_id"], subject="agent-b"),
        "D2:subject_reassign_rejected")
    _raises_approval(
        p, lambda: p.acceptance_policy.attenuate_grant(
            parent_id=root["grant_id"], owner="someone-else"),
        "D2:owner_reassign_rejected")


def test_delegation_budget():
    from form.dell_matrix import agent_authority as aa
    owner = "R61_D3"
    p = fresh_program(owner)
    root = aa.issue_root_grant(p, issuer="human:ace", subject="agent-a",
                               max_depth=0)
    _raises_approval(p, lambda: aa.attenuate_for(p, root["grant_id"]),
                     "D3:no_delegation_when_zero")
    root2 = aa.issue_root_grant(p, issuer="human:ace", subject="agent-a",
                                max_depth=1)
    c1 = aa.attenuate_for(p, root2["grant_id"])
    check("D3:one_level_ok", c1.get("ok") is True)
    _raises_approval(p, lambda: aa.attenuate_for(p, c1["grant_id"]),
                     "D3:budget_exhausted")
    _raises_approval(
        p, lambda: p.acceptance_policy.attenuate_grant(
            parent_id=root2["grant_id"], max_depth=5),
        "D3:depth_increase_rejected")


def test_attenuate_bad_parents_rejected():
    from form.dell_matrix import agent_authority as aa
    owner = "R61_D4"
    p = fresh_program(owner)
    root = aa.issue_root_grant(p, issuer="human:ace", subject="agent-a",
                               max_depth=1)
    _raises_approval(p, lambda: aa.attenuate_for(p, "grant_" + "9" * 32),
                     "D4:unknown_parent_rejected")
    aa.revoke_grant(p, root["grant_id"])
    _raises_approval(p, lambda: aa.attenuate_for(p, root["grant_id"]),
                     "D4:revoked_parent_rejected")
    # A human approval id is not a grant parent (separate namespaces).
    pr = p.nursery.add("ApprParent", words="x")
    ctx = p.make_review_context(pr.id, reviewer="human:ace")
    _raises_approval(p, lambda: aa.attenuate_for(p, ctx["approval_id"]),
                     "D4:approval_not_grant_parent")
    # Malformed constraints.
    root2 = aa.issue_root_grant(p, issuer="human:ace", subject="agent-a",
                                max_depth=1)
    _raises_approval(
        p, lambda: p.acceptance_policy.attenuate_grant(
            parent_id=root2["grant_id"], target=123),
        "D4:malformed_target_rejected")
    _raises_approval(
        p, lambda: p.acceptance_policy.attenuate_grant(
            parent_id=root2["grant_id"], content="not-a-mapping"),
        "D4:malformed_content_rejected")
    _raises_approval(
        p, lambda: p.acceptance_policy.issue_grant(
            issuer="human:ace", subject="agent-a", owner=owner,
            operation="confirm"),
        "D4:ungrantable_operation_rejected")


def test_grant_cannot_mint_human_consent():
    """A grant never satisfies the human-approval path and vice versa."""
    from form.dell_matrix import agent_authority as aa
    owner = "R61_D5"
    p = fresh_program(owner)
    pr = p.nursery.add("NoConsent", words="x")
    _, child = mkpair(p, pr.id)
    # Grant presented where a human review context is expected: the
    # approval branch requires an issued approval, not a grant.
    rec = p.acceptance_policy._issued_approvals.get(child["grant_id"])
    check("D5:grant_not_an_approval", rec is None)
    # Human approval cannot be attenuated as a grant.
    ctx = p.make_review_context(pr.id, reviewer="human:ace")
    _raises_approval(p, lambda: aa.attenuate_for(p, ctx["approval_id"]),
                     "D5:approval_not_attenuatable")


# ---------------------------------------------------------------- E. revocation

def test_revoke_parent_denies_child():
    from form.dell_matrix import agent_authority as aa
    owner = "R61_E1"
    p = fresh_program(owner)
    pr = p.nursery.add("RevParent", words="x")
    root, child = mkpair(p, pr.id)
    aa.revoke_grant(p, root["grant_id"])
    r = aa.agent_confirm(p, pr.id, child["grant_id"], "agent-a")
    check("E1:deny", r.get("ok") is False, str(r))
    check("E1:detail", "ancestor" in str(r.get("detail", "")).lower(),
          str(r.get("detail")))
    check("E1:still_pending", p.nursery.proposals[pr.id].status == "pending")
    check("E1:no_unit", pr.id not in p.cube.session.plane.units)


def test_revoke_leaf_denies():
    from form.dell_matrix import agent_authority as aa
    owner = "R61_E2"
    p = fresh_program(owner)
    pr = p.nursery.add("RevLeaf", words="x")
    root, child = mkpair(p, pr.id)
    aa.revoke_grant(p, child["grant_id"])
    r = aa.agent_confirm(p, pr.id, child["grant_id"], "agent-a")
    check("E2:deny", r.get("ok") is False, str(r))
    # Sibling derivation from the still-valid root still works.
    sib = aa.attenuate_for(p, root["grant_id"], target=pr.id,
                           content_pid=pr.id)
    r2 = aa.agent_confirm(p, pr.id, sib["grant_id"], "agent-a")
    check("E2:sibling_still_valid", r2.get("ok") is True, str(r2))


def test_revocation_preserves_committed_history():
    from form.dell_matrix import agent_authority as aa
    owner = "R61_E3"
    p = fresh_program(owner)
    pr = p.nursery.add("RevHist", words="x")
    root, child = mkpair(p, pr.id)
    r = aa.agent_confirm(p, pr.id, child["grant_id"], "agent-a")
    check("E3:confirm_ok", r.get("ok") is True, str(r))
    aa.revoke_grant(p, root["grant_id"])
    aa.revoke_grant(p, child["grant_id"])
    # Committed history survives: reload shows the accepted Idea.
    from form import persist_rest
    p2 = persist_rest.load(owner, activate=False)
    check("E3:history_intact_status",
          p2.nursery.proposals[pr.id].status == "confirmed")
    check("E3:history_intact_plane", pr.id in p2.cube.session.plane.units)
    # ... but the revoked grant authorizes nothing further.
    pr2 = p2.nursery.add("RevHist2", words="y")
    r2 = aa.agent_confirm(p2, pr2.id, child["grant_id"], "agent-a")
    check("E3:revoked_grant_denies_new", r2.get("ok") is False, str(r2))


def test_mid_write_revocation_denies():
    from form.dell_matrix import agent_authority as aa
    from form.dell_matrix import confirm_lineage
    owner = "R61_E4"
    p = fresh_program(owner)
    pr = p.nursery.add("MidRevoke", words="x")
    root, child = mkpair(p, pr.id)
    gid = child["grant_id"]

    def hook(program, pid, auth):
        program.acceptance_policy.revoke_grant(gid)

    confirm_lineage._BETWEEN_STAGES = hook
    try:
        r = aa.agent_confirm(p, pr.id, gid, "agent-a")
    finally:
        confirm_lineage._BETWEEN_STAGES = None
    check("E4:deny", r.get("ok") is False, str(r))
    check("E4:stage", r.get("stage") == "pre_commit", str(r.get("stage")))
    check("E4:still_pending", p.nursery.proposals[pr.id].status == "pending")
    check("E4:no_durable_unit", not durable_has_unit(owner, pr.id, "MidRevoke"))
    check("E4:no_live_unit", pr.id not in p.cube.session.plane.units)


def test_mid_write_content_change_denies():
    from form.dell_matrix import agent_authority as aa
    from form.dell_matrix import confirm_lineage
    owner = "R61_E5"
    p = fresh_program(owner)
    pr = p.nursery.add("MidContent", words="before")
    _, child = mkpair(p, pr.id, bind_content=True)

    def hook(program, pid, auth):
        program.nursery.proposals[pid].words = "mutated mid-write"

    confirm_lineage._BETWEEN_STAGES = hook
    try:
        r = aa.agent_confirm(p, pr.id, child["grant_id"], "agent-a")
    finally:
        confirm_lineage._BETWEEN_STAGES = None
    check("E5:deny", r.get("ok") is False, str(r))
    check("E5:still_pending", p.nursery.proposals[pr.id].status == "pending")


# ---------------------------------------------------------------- F. session lifecycle

def test_session_reset_invalidates():
    from form.dell_matrix import agent_authority as aa
    owner = "R61_F1"
    p = fresh_program(owner)
    pr = p.nursery.add("SessReset", words="x")
    _, child = mkpair(p, pr.id)
    p.acceptance_policy.reset_session()
    r = aa.agent_confirm(p, pr.id, child["grant_id"], "agent-a")
    check("F1:deny", r.get("ok") is False, str(r))
    check("F1:still_pending", p.nursery.proposals[pr.id].status == "pending")
    # Ideas are untouched by session reset.
    check("F1:no_ideas_deleted", pr.id in p.nursery.proposals)


def test_restart_invalidates_grant_cross_process():
    owner = "R61_F2"
    clean_owner(owner)
    # Handle issued inside child process A (its session).
    issued = run_child("issue", {"owner": owner, "label": "RestartGrant",
                                 "subject": "agent-a"})
    check("F2:issued", "grant_id" in issued, str(issued))
    # Fresh child process B (fresh session): the handle authorizes nothing.
    r = run_child("confirm", {"owner": owner, "pid": issued["pid"],
                              "grant_id": issued["grant_id"],
                              "subject": "agent-a"})
    check("F2:deny", r.get("ok") is False, str(r))


def test_restart_preserves_ideas_cross_process():
    from form.dell_matrix import agent_authority as aa
    owner = "R61_F3"
    p = fresh_program(owner)
    pr = p.nursery.add("RestartIdea", words="keep me")
    pid = pr.id
    _, child = mkpair(p, pid)
    r = aa.agent_confirm(p, pid, child["grant_id"], "agent-a")
    check("F3:confirm_ok", r.get("ok") is True, str(r))
    del p
    got = run_child("reload_check", {"owner": owner, "pid": pid,
                                     "label": "RestartIdea"})
    check("F3:reload_on_plane", got.get("on_plane") is True, str(got))
    check("F3:reload_status", got.get("status") == "confirmed", str(got))
    check("F3:reload_label", got.get("label_ok") is True, str(got))


# ---------------------------------------------------------------- G. separation: PERSONA != PERMISSION

def test_persona_change_does_not_alter_permission():
    from form.dell_matrix import agent_authority as aa
    from form.dell_matrix.personas import PERSONAS
    owner = "R61_G1"
    p = fresh_program(owner)
    pr = p.nursery.add("PersonaPerm", words="x")
    _, child = mkpair(p, pr.id)
    persona_ids = list(PERSONAS.keys())[:4]
    assert len(persona_ids) >= 2
    decisions = []
    for pid_persona in persona_ids:
        p.persona_matrix.active = pid_persona
        d = p.acceptance_policy.check(
            "agent:a", pr.id, {"grant_id": child["grant_id"]},
            proposal_version=p.acceptance_data_hash(pr.id, "confirm"),
            operation="confirm", subject="agent-a", owner=owner)
        decisions.append(bool(d.get("allowed")))
    check("G1:allow_invariant_across_personas",
          all(decisions) and len(set(decisions)) == 1,
          str(list(zip(persona_ids, decisions))))
    # ... and denial is likewise persona-invariant.
    denials = []
    for pid_persona in persona_ids:
        p.persona_matrix.active = pid_persona
        d = p.acceptance_policy.check(
            "agent:a", pr.id, {"grant_id": "grant_" + "1" * 32},
            proposal_version=p.acceptance_data_hash(pr.id, "confirm"),
            operation="confirm", subject="agent-a", owner=owner)
        denials.append(bool(d.get("allowed")))
    check("G1:deny_invariant_across_personas",
          not any(denials), str(list(zip(persona_ids, denials))))
    p.persona_matrix.active = None


# ---------------------------------------------------------------- H. denial consequences

def test_denied_attempt_preserves_state_and_evidence():
    from form.dell_matrix import agent_authority as aa
    from form.mandell.core_i_recovery import _confirm_journal_path
    owner = "R61_H1"
    p = fresh_program(owner)
    pr = p.nursery.add("DeniedKeep", words="x")
    before_units = set(p.cube.session.plane.units.keys())
    r = aa.agent_confirm(p, pr.id, "grant_" + "2" * 32, "agent-a")
    check("H1:deny", r.get("ok") is False, str(r))
    check("H1:still_pending", p.nursery.proposals[pr.id].status == "pending")
    check("H1:no_new_units",
          set(p.cube.session.plane.units.keys()) == before_units)
    check("H1:no_durable_unit", not durable_has_unit(owner, pr.id, "DeniedKeep"))
    jp = _confirm_journal_path(owner)
    if not os.path.isabs(jp):
        jp = os.path.join(ROOT, jp)
    check("H1:no_stray_journal", not os.path.isfile(jp))
    # The denial is observable in the audit trail (observable consequence).
    vias = [e.get("via") for e in p.acceptance_policy.audit_log()
            if e.get("action") == "deny"]
    check("H1:denial_audited", "unissued_grant" in vias, str(vias))


class _BrokenDict(dict):
    def pop(self, *a, **kw):
        raise RuntimeError("injected_cleanup_failure")


def test_incomplete_compensation_blocks_grant_path():
    """Grant-authorized confirm, revoked mid-write, cleanup fails:
    incomplete compensation is reported (not ordinary denial), the
    journal is retained, and no durable unit exists."""
    from form.dell_matrix import agent_authority as aa
    from form.mandell.core_i_recovery import _confirm_journal_path
    owner = "R61_H2"
    p = fresh_program(owner)
    pr = p.nursery.add("GrantIncomplete", words="x")
    _, child = mkpair(p, pr.id)
    gid = child["grant_id"]

    orig_place = p.place

    def injecting_place(*a, **kw):
        result = orig_place(*a, **kw)
        p.acceptance_policy.revoke_grant(gid)
        p.spatial.velocities = _BrokenDict(p.spatial.velocities)
        return result

    p.place = injecting_place
    try:
        r = aa.agent_confirm(p, pr.id, gid, "agent-a")
    finally:
        p.place = orig_place
    check("H2:denied", r.get("ok") is False, str(r.get("reason")))
    check("H2:reported_incomplete", r.get("compensation") == "incomplete",
          str(r.get("compensation")))
    check("H2:failures_listed", bool(r.get("compensation_failures")),
          str(r.get("compensation_failures")))
    check("H2:evidence_retained", r.get("evidence_retained") is True)
    jp = _confirm_journal_path(owner)
    if not os.path.isabs(jp):
        jp = os.path.join(ROOT, jp)
    check("H2:journal_kept", os.path.isfile(jp),
          "journal must be retained on incomplete compensation")
    check("H2:no_durable_unit",
          not durable_has_unit(owner, pr.id, "GrantIncomplete"))


# ---------------------------------------------------------------- I. sensitivity: checks disabled -> negatives fail

def test_checks_disabled_negatives_fail():
    """Non-vacuous proof: with the canonical check disabled, the forged
    credential is no longer denied -- the denial comes from the check."""
    from form.dell_matrix import agent_authority as aa
    from form.dell_matrix.acceptance_policy import AcceptancePolicy
    owner = "R61_I1"
    p = fresh_program(owner)
    pr = p.nursery.add("Sensitivity", words="x")
    forged = "grant_" + "3" * 32

    r = aa.agent_confirm(p, pr.id, forged, "agent-a")
    check("I1:baseline_denies", r.get("ok") is False, str(r))

    real_check = AcceptancePolicy.check

    def always_allow(self, *a, **kw):
        return {"allowed": True, "via": "disabled_check"}

    AcceptancePolicy.check = always_allow
    try:
        r2 = aa.agent_confirm(p, pr.id, forged, "agent-a")
    finally:
        AcceptancePolicy.check = real_check
    check("I1:disabled_check_allows_forgery", r2.get("ok") is True,
          "negative control must FAIL when the check is disabled; "
          f"got ok={r2.get('ok')}")
    # And the check is really restored.
    r3 = aa.agent_confirm(p, pr.id, forged, "agent-a")
    check("I1:check_restored_denies", r3.get("ok") is False, str(r3))


# ---------------------------------------------------------------- smoke


# ---------------------------------------------------------------- J. content semantics (Director 2026-10-07 AMEND)
# Absence vs empty: None = unconstrained (documented positive);
# every valid Mapping, including {}, is hashed and bound.

def test_none_content_is_unconstrained_positive():
    from form.dell_matrix import agent_authority as aa
    owner = "R61_J1"
    p = fresh_program(owner)
    pr = p.nursery.add("NoneContent", words="v1")
    # No content_pid -> content=None -> unconstrained by content.
    root = aa.issue_root_grant(p, issuer="human:ace", subject="agent-a",
                               max_depth=1)
    child = aa.attenuate_for(p, root["grant_id"], target=pr.id)
    check("J1:record_unbound",
          p.acceptance_policy._issued_grants[child["grant_id"]]
          .get("content_hash") is None)
    pr.words = "changed words entirely"
    r = aa.agent_confirm(p, pr.id, child["grant_id"], "agent-a")
    check("J1:unconstrained_allows", r.get("ok") is True, str(r))


def test_empty_dict_content_binds():
    from form.dell_matrix.acceptance_policy import canonical_hash
    owner = "R61_J2"
    p = fresh_program(owner)
    g = p.acceptance_policy.issue_grant(
        issuer="human:ace", subject="agent-a", owner=owner,
        operation="nursery.confirm", content={}, max_depth=0)
    rec = p.acceptance_policy._issued_grants[g["grant_id"]]
    check("J2:empty_hashed_not_none",
          rec.get("content_hash") == canonical_hash({}),
          str(rec.get("content_hash")))
    # Exact hash match allows (policy level).
    d = p.acceptance_policy.check(
        "agent:a", "any-pid", {"grant_id": g["grant_id"]},
        proposal_version=canonical_hash({}), operation="confirm",
        subject="agent-a", owner=owner)
    check("J2:exact_match_allows", d.get("allowed") is True, str(d))
    # Different content denies (policy level).
    d2 = p.acceptance_policy.check(
        "agent:a", "any-pid", {"grant_id": g["grant_id"]},
        proposal_version=canonical_hash({"x": 1}), operation="confirm",
        subject="agent-a", owner=owner)
    check("J2:different_denies", d2.get("allowed") is False, str(d2))


def test_nonempty_content_binding():
    from form.dell_matrix import agent_authority as aa
    owner = "R61_J3"
    p = fresh_program(owner)
    pr = p.nursery.add("NonEmpty", words="stable words")
    _, child = mkpair(p, pr.id, bind_content=True)
    rec = p.acceptance_policy._issued_grants[child["grant_id"]]
    check("J3:bound", rec.get("content_hash") is not None)
    r = aa.agent_confirm(p, pr.id, child["grant_id"], "agent-a")
    check("J3:matching_allows", r.get("ok") is True, str(r))
    # Fresh proposal for the deny case (pr is now confirmed).
    pr2 = p.nursery.add("NonEmpty2", words="stable words")
    _, child2 = mkpair(p, pr2.id, bind_content=True)
    pr2.words = "mutated"
    r2 = aa.agent_confirm(p, pr2.id, child2["grant_id"], "agent-a")
    check("J3:changed_denies", r2.get("ok") is False, str(r2))


def test_malformed_content_rejected():
    owner = "R61_J4"
    p = fresh_program(owner)
    _raises_approval(p, lambda: p.acceptance_policy.issue_grant(
        issuer="human:ace", subject="agent-a", owner=owner,
        operation="nursery.confirm", content="not-a-mapping"),
        "J4:malformed_issue_rejected")
    _raises_approval(p, lambda: p.acceptance_policy.issue_grant(
        issuer="human:ace", subject="agent-a", owner=owner,
        operation="nursery.confirm", content=123),
        "J4:malformed_type_rejected")


def test_attenuation_never_drops_restriction():
    from form.dell_matrix import agent_authority as aa
    from form.dell_matrix.acceptance_policy import canonical_hash
    owner = "R61_J5"
    p = fresh_program(owner)
    pr = p.nursery.add("NoDrop", words="w")
    root = aa.issue_root_grant(p, issuer="human:ace", subject="agent-a",
                               max_depth=2)
    bound = aa.attenuate_for(p, root["grant_id"], target=pr.id,
                             content_pid=pr.id)
    bh = p.acceptance_policy._issued_grants[bound["grant_id"]]["content_hash"]
    check("J5:child_bound", bh is not None)
    # Omitting content inherits the parent's binding (never drops it).
    child2 = p.acceptance_policy.attenuate_grant(parent_id=bound["grant_id"])
    check("J5:inherited_not_dropped",
          p.acceptance_policy._issued_grants[child2["grant_id"]]
          ["content_hash"] == bh)
    # Empty-dict parent binding is preserved exactly.
    g = p.acceptance_policy.issue_grant(
        issuer="human:ace", subject="agent-a", owner=owner,
        operation="nursery.confirm", content={}, max_depth=1)
    gc = p.acceptance_policy.attenuate_grant(parent_id=g["grant_id"])
    check("J5:empty_binding_preserved",
          p.acceptance_policy._issued_grants[gc["grant_id"]]
          ["content_hash"] == canonical_hash({}))

# ---------------------------------------------------------------- K. subject-bound endpoint (Director 2026-10-07 AMEND)

def test_endpoint_legitimate_succeeds_and_reloads():
    from form.dell_matrix import agent_authority as aa
    owner = "R61_K1"
    p = fresh_program(owner)
    pr = p.nursery.add("EpLegit", words="w")
    ep = aa.bind_agent(p, "agent-a")
    root = aa.issue_root_grant(p, issuer="human:ace", subject="agent-a",
                               max_depth=1)
    child = aa.attenuate_for(p, root["grant_id"], target=pr.id,
                             content_pid=pr.id)
    r = ep.confirm(pr.id, child["grant_id"])
    check("K1:confirm_ok", r.get("ok") is True, str(r))
    check("K1:status", p.nursery.proposals[pr.id].status == "confirmed")
    from form import persist_rest
    p2 = persist_rest.load(owner, activate=False)
    check("K1:reload_on_plane", pr.id in p2.cube.session.plane.units)


def test_endpoint_other_subject_handle_denies():
    from form.dell_matrix import agent_authority as aa
    owner = "R61_K2"
    p = fresh_program(owner)
    pr = p.nursery.add("EpOther", words="w")
    root = aa.issue_root_grant(p, issuer="human:ace", subject="agent-a",
                               max_depth=1)
    child = aa.attenuate_for(p, root["grant_id"], target=pr.id)
    ep_b = aa.bind_agent(p, "agent-b")
    r = ep_b.confirm(pr.id, child["grant_id"])
    check("K2:deny", r.get("ok") is False, str(r))
    check("K2:still_pending", p.nursery.proposals[pr.id].status == "pending")


def test_endpoint_payload_substitution_impossible():
    from form.dell_matrix import agent_authority as aa
    owner = "R61_K3"
    p = fresh_program(owner)
    pr = p.nursery.add("EpSubst", words="w")
    ep = aa.bind_agent(p, "agent-a")
    # The request surface has no subject/issuer/producer/review-context
    # parameters: substitution attempts are TypeErrors, not silent accepts.
    import inspect
    sig = inspect.signature(ep.confirm)
    check("K3:surface_is_pid_and_handle_only",
          list(sig.parameters.keys()) == ["pid", "grant_handle"],
          str(list(sig.parameters.keys())))
    for kwargs in ({"subject": "agent-b"}, {"issuer": "human:ace"},
                   {"producer": "agent-b"}, {"_auth": {}}):
        try:
            ep.confirm(pr.id, "grant_x", **kwargs)
            check(f"K3:substitution_rejected_{sorted(kwargs)}", False,
                  "no TypeError raised")
        except TypeError:
            check(f"K3:substitution_rejected_{sorted(kwargs)}", True)
    check("K3:still_pending", p.nursery.proposals[pr.id].status == "pending")


def test_endpoint_persona_cannot_change_binding():
    from form.dell_matrix import agent_authority as aa
    from form.dell_matrix.personas import PERSONAS
    owner = "R61_K4"
    p = fresh_program(owner)
    ep = aa.bind_agent(p, "agent-a")
    for pid_persona in list(PERSONAS.keys())[:4]:
        p.persona_matrix.active = pid_persona
        check(f"K4:binding_stable_under_{pid_persona}",
              ep.bound_subject == "agent-a", ep.bound_subject)
    p.persona_matrix.active = None


def test_endpoint_surface_has_no_controller_methods():
    from form.dell_matrix import agent_authority as aa
    owner = "R61_K5"
    p = fresh_program(owner)
    ep = aa.bind_agent(p, "agent-a")
    for name in ("issue_grant", "issue_root_grant", "attenuate_grant",
                 "attenuate_for", "revoke_grant", "describe_grants",
                 "list_approvals", "audit_log", "reset_session"):
        check(f"K5:no_{name}", not hasattr(ep, name), name)
    # The only callable request method is confirm(); bound_subject is a
    # read-only host-audit property, not a request parameter.
    import inspect as _inspect
    methods = [m for m in dir(ep)
               if not m.startswith("_") and callable(getattr(ep, m))]
    check("K5:only_confirm_callable", methods == ["confirm"], str(methods))
    prop = getattr(type(ep), "bound_subject", None)
    check("K5:bound_subject_readonly",
          isinstance(prop, property) and prop.fset is None)


def test_bind_agent_rejects_bad_subject():
    from form.dell_matrix import agent_authority as aa
    owner = "R61_K6"
    p = fresh_program(owner)
    for bad in ("", None, 123, "x" * 201):
        try:
            aa.bind_agent(p, bad)
            check(f"K6:rejects_{type(bad).__name__}", False, "no error")
        except (ValueError, TypeError):
            check(f"K6:rejects_{type(bad).__name__}", True)


def smoke():
    for fn in [test_root_grant_confirm_reload,
               test_human_confirm_still_works,
               test_opt_in_still_works_and_revocable,
               test_missing_credential_denies,
               test_forged_handle_denies,
               test_edited_handle_denies,
               test_copied_dict_confers_nothing,
               test_grant_without_trusted_subject_denies,
               test_no_handle_in_audit_or_receipts,
               test_operation_mismatch_denies,
               test_target_mismatch_denies,
               test_content_mismatch_denies,
               test_subject_mismatch_denies,
               test_owner_mismatch_denies,
               test_expansion_rejected,
               test_subject_owner_reassignment_rejected,
               test_delegation_budget,
               test_attenuate_bad_parents_rejected,
               test_grant_cannot_mint_human_consent,
               test_revoke_parent_denies_child,
               test_revoke_leaf_denies,
               test_revocation_preserves_committed_history,
               test_mid_write_revocation_denies,
               test_mid_write_content_change_denies,
               test_session_reset_invalidates,
               test_restart_invalidates_grant_cross_process,
               test_restart_preserves_ideas_cross_process,
               test_persona_change_does_not_alter_permission,
               test_denied_attempt_preserves_state_and_evidence,
               test_incomplete_compensation_blocks_grant_path,
               test_checks_disabled_negatives_fail,
               test_none_content_is_unconstrained_positive,
               test_empty_dict_content_binds,
               test_nonempty_content_binding,
               test_malformed_content_rejected,
               test_attenuation_never_drops_restriction,
               test_endpoint_legitimate_succeeds_and_reloads,
               test_endpoint_other_subject_handle_denies,
               test_endpoint_payload_substitution_impossible,
               test_endpoint_persona_cannot_change_binding,
               test_endpoint_surface_has_no_controller_methods,
               test_bind_agent_rejects_bad_subject]:
        try:
            fn()
        except Exception as e:
            import traceback
            check(fn.__name__, False,
                  f"EXC {type(e).__name__}: {e}\n{traceback.format_exc()[:600]}")
    n = sum(CHECKS)
    print(f"=== {n}/{len(CHECKS)} ===")
    return n == len(CHECKS)




if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
