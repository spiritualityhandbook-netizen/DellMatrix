#!/usr/bin/env python3
"""R6.2 identity/docking circuit proofs (Director 2026-10-07).

Walking skeleton: host identity -> explicit docking -> read-only
context -> deterministic fake inference -> schema-validated PENDING
Nursery proposal -> human review/issued authority -> R6.1 bound
endpoint -> canonical writer -> receipt/save/reload.

Failure controls (directive section 3), each with a declared expected
outcome. Fake-provider modes are the deterministic independent check.

Evidence: INTEGRATION (real Program/Nursery/writer) + CROSS_PROCESS
(reload via production loader).
"""

import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(REPO)
sys.path.insert(0, ROOT)

CHECKS = []


def check(name, cond, detail=""):
    CHECKS.append(bool(cond))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f" | {detail}" if detail and not cond else ""))


def clean_owner(owner):
    import glob
    for pat in (f'form/state/nursery_{owner}.json',
                f'form/state/program_{owner}.json'):
        if os.path.isfile(pat):
            os.remove(pat)
    for pat in glob.glob(f'form/state/checkpoint_{owner}_*'):
        os.remove(pat)


def fresh_program(owner):
    from form.open import open_program
    clean_owner(owner)
    return open_program(owner)


# ------------------------------------------------------- walking skeleton

def test_skeleton_fake_to_confirmed_reload():
    from form.dell_matrix import inference_dock as idock
    from form.dell_matrix import agent_authority as aa
    owner = "R62_S1"
    p = fresh_program(owner)
    sess = idock.dock(p, "agent-a", provider="fake", fake_mode="valid")
    check("S1:docked", sess.is_docked and sess.bound_subject == "agent-a")
    r = sess.propose("draft an idea about rivers",
                     context={"seen": ["r1"]})
    check("S1:propose_ok", r.get("ok") is True, str(r))
    pid = r["pid"]
    check("S1:pending", p.nursery.proposals[pid].status == "pending")
    check("S1:exact_fields",
          p.nursery.proposals[pid].label == "Docked Idea"
          and p.nursery.proposals[pid].words == "inference drafted these words")
    # Human review -> issued authority -> bound endpoint -> writer.
    root = aa.issue_root_grant(p, issuer="human:ace", subject="agent-a",
                               max_depth=1)
    child = aa.attenuate_for(p, root["grant_id"], target=pid,
                             content_pid=pid)
    ep = aa.bind_agent(p, "agent-a")
    c = ep.confirm(pid, child["grant_id"])
    check("S1:confirm_ok", c.get("ok") is True, str(c))
    check("S1:confirmed", p.nursery.proposals[pid].status == "confirmed")
    from form import persist_rest
    p2 = persist_rest.load(owner, activate=False)
    check("S1:reload_on_plane", pid in p2.cube.session.plane.units)


# ------------------------------------------------------- failure controls

def test_undocked_zero_calls():
    from form.dell_matrix import inference_dock as idock
    owner = "R62_C1"
    p = fresh_program(owner)
    n0 = len(p.nursery.proposals)
    sess = idock.dock(p, "agent-a", provider="fake", fake_mode="valid")
    sess.undock()
    check("C1:undocked", not sess.is_docked)
    r = sess.propose("anything")
    check("C1:refuses", r.get("ok") is False and r.get("reason") == "undocked", str(r))
    check("C1:zero_calls", sess._provider.calls == 0)
    check("C1:no_proposal", len(p.nursery.proposals) == n0)


def test_valid_stays_pending_until_authorized():
    from form.dell_matrix import inference_dock as idock
    owner = "R62_C2"
    p = fresh_program(owner)
    sess = idock.dock(p, "agent-a", provider="fake", fake_mode="valid")
    r = sess.propose("draft")
    check("C2:ok", r.get("ok") is True)
    check("C2:pending_not_confirmed",
          p.nursery.proposals[r["pid"]].status == "pending")


def test_malformed_timeout_failure_preserve_state():
    from form.dell_matrix import inference_dock as idock
    owner = "R62_C3"
    p = fresh_program(owner)
    n0 = len(p.nursery.proposals)
    for mode, reason in (("malformed", "invalid_output"),
                         ("timeout", "provider_failure"),
                         ("failure", "provider_failure"),
                         ("empty", "invalid_output")):
        sess = idock.dock(p, "agent-a", provider="fake", fake_mode=mode)
        r = sess.propose("draft")
        check(f"C3:{mode}_rejected",
              r.get("ok") is False and r.get("reason") == reason, str(r))
    check("C3:state_preserved", len(p.nursery.proposals) == n0)


def test_authority_requesting_output_confers_nothing():
    from form.dell_matrix import inference_dock as idock
    owner = "R62_C4"
    p = fresh_program(owner)
    n0 = len(p.nursery.proposals)
    sess = idock.dock(p, "agent-a", provider="fake", fake_mode="authority")
    r = sess.propose("draft")
    check("C4:rejected", r.get("ok") is False
          and r.get("reason") == "invalid_output", str(r))
    check("C4:no_proposal", len(p.nursery.proposals) == n0)
    check("C4:no_grants_minted",
          len(p.acceptance_policy._issued_grants) == 0)


def test_canary_does_not_leak():
    from form.dell_matrix import inference_dock as idock
    owner = "R62_C5"
    p = fresh_program(owner)
    # (a) reflected provider error is sanitized before surfacing.
    sess = idock.dock(p, "agent-a", provider="fake",
                      fake_mode="canary_error")
    r = sess.propose("draft")
    check("C5:error_sanitized",
          r.get("ok") is False and "sk-canary-REFLECT-1" not in str(r),
          str(r))
    # (b) sensitive context keys never reach the prompt; reflected
    # output therefore cannot carry the canary into proposal metadata.
    sess2 = idock.dock(p, "agent-a", provider="fake", fake_mode="reflect")
    ctx = {"note": "ordinary", "api_key": "sk-canary-CTX-2",
           "nested": {"grant_id": "grant_canary"}}
    r2 = sess2.propose("draft", context=ctx)
    check("C5:reflect_ok", r2.get("ok") is True, str(r2))
    words = p.nursery.proposals[r2["pid"]].words
    check("C5:canary_not_in_metadata",
          "sk-canary-CTX-2" not in words and "grant_canary" not in words,
          words[:120])
    check("C5:prompt_had_no_canary",
          "sk-canary-CTX-2" not in (sess2._provider.last_prompt or ""))
    # (c) negative control: without scrubbing, the canary WOULD appear.
    raw_prompt = "draft\n\n[context]\n" + json.dumps(ctx)
    check("C5:control_nonvacuous", "sk-canary-CTX-2" in raw_prompt)


def test_revocation_before_writer_denies():
    from form.dell_matrix import inference_dock as idock
    from form.dell_matrix import agent_authority as aa
    from form.dell_matrix import confirm_lineage
    owner = "R62_C6"
    p = fresh_program(owner)
    sess = idock.dock(p, "agent-a", provider="fake", fake_mode="valid")
    r = sess.propose("draft")
    pid = r["pid"]
    root = aa.issue_root_grant(p, issuer="human:ace", subject="agent-a",
                               max_depth=1)
    child = aa.attenuate_for(p, root["grant_id"], target=pid,
                             content_pid=pid)
    gid = child["grant_id"]
    # Revoke between staging and pre-commit via the R6.1 hook.
    def _hook(program, _pid, _auth):
        program.acceptance_policy.revoke_grant(gid)
    confirm_lineage._BETWEEN_STAGES = _hook
    try:
        ep = aa.bind_agent(p, "agent-a")
        c = ep.confirm(pid, gid)
    finally:
        confirm_lineage._BETWEEN_STAGES = None
    check("C6:denied", c.get("ok") is False, str(c))
    check("C6:still_pending", p.nursery.proposals[pid].status == "pending")


def test_persona_provider_do_not_change_permission():
    from form.dell_matrix import inference_dock as idock
    from form.dell_matrix.personas import PERSONAS
    owner = "R62_C7"
    p = fresh_program(owner)
    sess = idock.dock(p, "agent-a", provider="fake", fake_mode="valid")
    r1 = sess.propose("draft one")
    for persona in list(PERSONAS.keys())[:4]:
        p.persona_matrix.active = persona
        r = sess.propose(f"draft under {persona}")
        check(f"C7:propose_ok_under_{persona}", r.get("ok") is True)
        check(f"C7:pending_under_{persona}",
              p.nursery.proposals[r["pid"]].status == "pending")
    p.persona_matrix.active = None
    check("C7:subject_stable", sess.bound_subject == "agent-a")
    # A different provider label does not change the permission either:
    # confirmation still requires the grant path.
    from form.dell_matrix import agent_authority as aa
    ep = aa.bind_agent(p, "agent-a")
    c = ep.confirm(r1["pid"], "grant_nonexistent")
    check("C7:confirm_still_denied_without_grant", c.get("ok") is False)


def test_inference_absent_core_still_works():
    import sys
    from form.dell_matrix import inference_dock as idock
    owner = "R62_C8"
    p = fresh_program(owner)
    # Simulate the inference package being absent.
    real_import = idock._load_bridge
    def _boom():
        raise idock.DockError("inference package absent (simulated)")
    idock._load_bridge = _boom
    try:
        try:
            idock.dock(p, "agent-a", provider="ollama")
            check("C8:dock_fails_clean", False, "no error raised")
        except idock.DockError as e:
            check("C8:dock_fails_clean", "absent" in str(e), str(e))
    finally:
        idock._load_bridge = real_import
    # Core acceptance path is unaffected.
    check("C8:no_llm_in_core_modules", "form.llm" not in sys.modules)
    pr = p.nursery.add("CoreStillWorks", words="w")
    ctx = p.make_review_context(pr.id, reviewer="human:ace")
    r = p.confirm_proposal(pr.id, _producer="repl_user",
                           _review_context=ctx)
    check("C8:core_confirm_ok", r.get("ok") is True, str(r))


def test_save_guards_hold_for_docked_proposals():
    from form.dell_matrix import inference_dock as idock
    owner = "R62_C9"
    p = fresh_program(owner)
    sess = idock.dock(p, "agent-a", provider="fake", fake_mode="valid")
    r = sess.propose("draft")
    check("C9:proposed", r.get("ok") is True)
    # Incomplete-restoration guards: a save must not silently drop the
    # pending proposal; reload must show it pending. Uses the
    # production v2 save path (form/state/, gitignored).
    from form import persist_rest
    persist_rest.save(p)
    p2 = persist_rest.load(owner, activate=False)
    st = p2.nursery.proposals.get(r["pid"])
    check("C9:pending_survives_save_load",
          st is not None and st.status == "pending",
          str(getattr(st, "status", None)))
    clean_owner(owner)


def test_schema_strictness_and_bounds():
    from form.dell_matrix import inference_dock as idock
    owner = "R62_C10"
    p = fresh_program(owner)
    n0 = len(p.nursery.proposals)
    # Direct validator probes (no nursery involved).
    bad_texts = [
        json.dumps({"label": "x"}),                       # missing words
        json.dumps({"label": "x", "words": "y", "extra": 1}),  # extra key
        json.dumps({"label": "x", "words": 5}),            # wrong type
        json.dumps({"label": "", "words": "y"}),          # empty label
        json.dumps({"label": "x" * 201, "words": "y"}),   # label too long
        json.dumps(["label", "words"]),                   # not an object
    ]
    for i, t in enumerate(bad_texts):
        try:
            idock.validate_proposal_output(t)
            check(f"C10:reject_{i}", False, "accepted")
        except idock.ProviderError:
            check(f"C10:reject_{i}", True)
    good = idock.validate_proposal_output(
        json.dumps({"label": "L", "words": "W"}))
    check("C10:accept_exact", good == {"label": "L", "words": "W"})
    # Oversized prompt refused before any provider call.
    sess = idock.dock(p, "agent-a", provider="fake", fake_mode="valid",
                      max_prompt_chars=10)
    r = sess.propose("this prompt is far too long for the bound")
    check("C10:prompt_bound", r.get("ok") is False
          and r.get("reason") == "prompt_too_large", str(r))
    check("C10:zero_calls_on_bound", sess._provider.calls == 0)
    check("C10:no_proposals", len(p.nursery.proposals) == n0)
    # Bad dock configuration rejected at the trusted entry.
    for kwargs in ({"timeout_s": 0}, {"timeout_s": -5},
                   {"max_prompt_chars": 0}, {"provider": ""}):
        try:
            idock.dock(p, "agent-a", **kwargs)
            check(f"C10:bad_config_{sorted(kwargs)}", False, "accepted")
        except idock.DockError:
            check(f"C10:bad_config_{sorted(kwargs)}", True)


def test_dock_surface_has_no_authority_methods():
    from form.dell_matrix import inference_dock as idock
    owner = "R62_C11"
    p = fresh_program(owner)
    sess = idock.dock(p, "agent-a", provider="fake")
    for name in ("issue_grant", "issue_root_grant", "attenuate_grant",
                 "attenuate_for", "revoke_grant", "confirm",
                 "confirm_proposal", "describe_grants"):
        check(f"C11:no_{name}", not hasattr(sess, name), name)
    import inspect as _inspect
    methods = [m for m in dir(sess)
               if not m.startswith("_") and callable(getattr(sess, m))]
    check("C11:surface", sorted(methods) == ["propose", "undock"],
          str(methods))


def test_no_eval_or_shell_on_output():
    from form.dell_matrix import inference_dock as idock
    owner = "R62_C12"
    p = fresh_program(owner)
    # Hostile text that would execute under eval/exec: must be inert data.
    hostile = ('{"label": "__import__(\'os\').system(\'x\')", '
               '"words": "y"}')
    try:
        out = idock.validate_proposal_output(hostile)
        # It parses as inert strings; nothing executed.
        check("C12:inert_strings",
              out["label"].startswith("__import__"))
    except idock.ProviderError:
        check("C12:inert_strings", True, "rejected as malformed")
    src = open(idock.__file__).read()
    # Strip the module docstring, then scan the code body.
    body = src.split('"""', 2)[-1]
    for token in ("subprocess", "os.system", "eval(", "exec(",
                  "__import__"):
        check(f"C12:no_{token}_in_dock", token not in body, token)


def smoke():
    for fn in [test_skeleton_fake_to_confirmed_reload,
               test_undocked_zero_calls,
               test_valid_stays_pending_until_authorized,
               test_malformed_timeout_failure_preserve_state,
               test_authority_requesting_output_confers_nothing,
               test_canary_does_not_leak,
               test_revocation_before_writer_denies,
               test_persona_provider_do_not_change_permission,
               test_inference_absent_core_still_works,
               test_save_guards_hold_for_docked_proposals,
               test_schema_strictness_and_bounds,
               test_dock_surface_has_no_authority_methods,
               test_no_eval_or_shell_on_output]:
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
