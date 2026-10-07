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



# ------------------------------------------------------- D. AMEND proofs
# Director 2026-10-07: actual transport, secret values, bounded
# context, real execution (child process, genuine save-guard,
# canary sensitivity), transport-contract via stubbed HTTP.

def test_director_secret_value_reproduction():
    """Director reproduction: context={"note": "grant_" + 32 hex}
    must NOT reach the provider nor the proposal."""
    from form.dell_matrix import inference_dock as idock
    owner = "R62_D1"
    p = fresh_program(owner)
    n0 = len(p.nursery.proposals)
    handle = "grant_" + "ab" * 16
    sess = idock.dock(p, "agent-a", provider="fake", fake_mode="reflect")
    r = sess.propose("draft", context={"note": handle})
    check("D1:protected_input_rejected",
          r.get("ok") is False and r.get("reason") == "protected_input",
          str(r))
    check("D1:zero_provider_calls", sess._provider.calls == 0)
    check("D1:no_proposal", len(p.nursery.proposals) == n0)
    # Nested values are covered too.
    sess2 = idock.dock(p, "agent-a", provider="fake", fake_mode="reflect")
    r2 = sess2.propose("draft",
                       context={"outer": {"inner": [handle]}})
    check("D1:nested_rejected",
          r2.get("ok") is False and r2.get("reason") == "protected_input",
          str(r2))
    # And prompt text itself.
    sess3 = idock.dock(p, "agent-a", provider="fake", fake_mode="valid")
    r3 = sess3.propose("draft about " + handle)
    check("D1:prompt_text_rejected",
          r3.get("ok") is False and r3.get("reason") == "protected_input",
          str(r3))


def test_director_response_bound_reproduction():
    """Director reproduction: max_response_chars=10 must reject the
    66+ char fake response, not silently accept it."""
    from form.dell_matrix import inference_dock as idock
    owner = "R62_D2"
    p = fresh_program(owner)
    n0 = len(p.nursery.proposals)
    sess = idock.dock(p, "agent-a", provider="fake", fake_mode="valid",
                      max_response_chars=10)
    r = sess.propose("draft")
    check("D2:oversized_rejected",
          r.get("ok") is False and r.get("reason") == "response_too_large",
          str(r))
    check("D2:no_proposal", len(p.nursery.proposals) == n0)
    # Boundary: exactly at the limit is accepted.
    import json as _json
    exact = _json.dumps({"label": "L", "words": "W"})
    sess2 = idock.dock(p, "agent-a", provider="fake", fake_mode="valid",
                       max_response_chars=len(
                           _json.dumps({"label": "Docked Idea",
                                        "words": "inference drafted these words"})))
    r2 = sess2.propose("draft")
    check("D2:at_limit_accepted", r2.get("ok") is True, str(r2))


def test_director_context_bound_reproduction():
    """Director reproduction: deeply nested context must be rejected
    with a stable receipt, not RecursionError."""
    from form.dell_matrix import inference_dock as idock
    owner = "R62_D3"
    p = fresh_program(owner)
    n0 = len(p.nursery.proposals)
    deep = cur = {}
    for _ in range(50):
        cur["n"] = {}
        cur = cur["n"]
    sess = idock.dock(p, "agent-a", provider="fake", fake_mode="valid")
    r = sess.propose("draft", context=deep)
    check("D3:deep_rejected",
          r.get("ok") is False and r.get("reason") == "bad_context",
          str(r))
    check("D3:zero_calls", sess._provider.calls == 0)
    # Cyclic context.
    cyc = {"a": {}}
    cyc["a"]["self"] = cyc
    sess2 = idock.dock(p, "agent-a", provider="fake", fake_mode="valid")
    r2 = sess2.propose("draft", context=cyc)
    check("D3:cyclic_rejected",
          r2.get("ok") is False and r2.get("reason") == "bad_context",
          str(r2))
    # Non-dict context.
    sess3 = idock.dock(p, "agent-a", provider="fake", fake_mode="valid")
    r3 = sess3.propose("draft", context=["not", "a", "dict"])
    check("D3:nondict_rejected",
          r3.get("ok") is False and r3.get("reason") == "bad_context",
          str(r3))
    check("D3:no_proposals", len(p.nursery.proposals) == n0)
    # Valid context still works and preserves scalar types.
    sess4 = idock.dock(p, "agent-a", provider="fake", fake_mode="valid")
    ctx = {"count": 3, "ratio": 1.5, "flag": True, "nothing": None,
           "name": "ok"}
    clean = idock.validate_context(ctx)
    check("D3:scalars_preserved",
          clean == ctx, str(clean))


def test_transport_contract_stubbed_http():
    """Real bridge path with stubbed HTTP (no live calls). Asserts the
    requested model/timeout reach the actual request, the read is
    bounded, no detection runs, and the receipt is truthful."""
    import urllib.request as _urlreq
    from form.dell_matrix import inference_dock as idock
    owner = "R62_D4"
    p = fresh_program(owner)
    seen = {}

    class _Resp:
        def __init__(self, payload):
            self._data = payload
            self._pos = 0
        def __enter__(self):
            return self
        def __exit__(self, *a):
            return False
        def read(self, n=None):
            # Socket-like: advance a cursor; b"" at EOF.
            if "first_read_n" not in seen and n is not None:
                seen["first_read_n"] = n
            seen["read_n"] = n
            if self._pos >= len(self._data):
                return b""
            out = self._data[self._pos:self._pos + n] if n else self._data[self._pos:]
            self._pos += len(out)
            return out

    real_urlopen = _urlreq.urlopen

    def _stub(url_or_req, timeout=None):
        url = (url_or_req.full_url if hasattr(url_or_req, "full_url")
               else url_or_req)
        seen["timeout"] = timeout
        seen["url"] = url
        if url.endswith("/api/tags"):
            return _Resp(b'{"models": []}')
        if url.endswith("/api/chat"):
            import json as _json
            payload = _json.loads(url_or_req.data.decode())
            seen["payload_model"] = payload.get("model")
            seen["payload_prompt_len"] = len(
                str(payload.get("messages")))
            body = _json.dumps(
                {"message": {"content": _json.dumps(
                    {"label": "Stubbed", "words": "via stub"})}}).encode()
            return _Resp(body)
        raise AssertionError("unexpected url " + url)

    _urlreq.urlopen = _stub
    try:
        bridge_mod = idock._load_bridge()
        # No detection may run during configured dispatch.
        real_detect = bridge_mod.LLMBridge.detect
        def _no_detect(self):
            raise AssertionError("detect() called during dispatch")
        bridge_mod.LLMBridge.detect = _no_detect
        try:
            sess = idock.dock(p, "agent-a", provider="ollama",
                              model="HOST_CHOSEN_MODEL", timeout_s=2,
                              max_response_chars=8000)
            r = sess.propose("draft via stub")
        finally:
            bridge_mod.LLMBridge.detect = real_detect
    finally:
        _urlreq.urlopen = real_urlopen
    check("D4:propose_ok", r.get("ok") is True, str(r))
    check("D4:model_reached_transport",
          seen.get("payload_model") == "HOST_CHOSEN_MODEL",
          str(seen.get("payload_model")))
    check("D4:timeout_reached_transport", seen.get("timeout") == 2,
          str(seen.get("timeout")))
    check("D4:read_bounded",
          seen.get("first_read_n") == 8000 * 4 + 1,
          str(seen.get("first_read_n")))
    check("D4:receipt_truthful",
          r.get("model") == "HOST_CHOSEN_MODEL", str(r.get("model")))
    check("D4:fields_exact",
          p.nursery.proposals[r["pid"]].label == "Stubbed")


def test_fresh_process_reload():
    """REAL child OS process: full circuit + save; parent inspects
    via production reload."""
    import subprocess
    owner = "R62_D5"
    fresh_program(owner)  # establishes clean state
    clean_owner(owner)
    args = json.dumps({"repo": ROOT, "owner": owner})
    proc = subprocess.run(
        [sys.executable, "form/mandell/r62_child.py", args],
        cwd=ROOT, capture_output=True, text=True, timeout=120)
    check("D5:child_ok", proc.returncode == 0, proc.stderr[:300])
    out = json.loads(proc.stdout.strip().splitlines()[-1])
    check("D5:child_reported", out.get("ok") is True, str(out))
    from form import persist_rest
    p2 = persist_rest.load(owner, activate=False)
    prop = p2.nursery.proposals.get(out["pid"])
    check("D5:parent_sees_confirmed",
          prop is not None and prop.status == "confirmed",
          str(getattr(prop, "status", None)))
    check("D5:parent_sees_on_plane", out["pid"] in p2.cube.session.plane.units)
    check("D5:words_intact",
          prop.words == "inference drafted these words")
    clean_owner(owner)


def test_save_guard_genuine():
    """Genuinely recovery-required instance via the production marking
    API: exposed save paths reject, bytes unchanged, evidence kept."""
    import hashlib
    from form.mandell.core_i_recovery import (
        mark_recovery_required, RollbackRecoveryError)
    from form import persist_rest
    owner = "R62_D6"
    p = fresh_program(owner)
    path = persist_rest.save(p)
    with open(path, "rb") as f:
        before = hashlib.sha256(f.read()).hexdigest()
    # Genuine mark through the production marking function (the same
    # function production calls on incomplete compensation).
    mark_recovery_required(p, "r62_probe",
                           "incomplete compensation (probe)",
                           {"failures": ["probe"]})
    for fn, name in ((lambda: persist_rest.save(p), "persist_rest.save"),
                     (lambda: p.nursery.save(), "nursery.save")):
        try:
            fn()
            check(f"D6:{name}_rejected", False, "save succeeded")
        except RollbackRecoveryError:
            check(f"D6:{name}_rejected", True)
    with open(path, "rb") as f:
        after = hashlib.sha256(f.read()).hexdigest()
    check("D6:bytes_unchanged", before == after)
    req = getattr(p, "_recovery_required", None)
    check("D6:evidence_retained",
          isinstance(req, dict) and "r62_probe" in req, str(req))
    clean_owner(owner)


def test_canary_sensitivity():
    """Weaken the ACTUAL production protection: the protected-input
    negative control must FAIL; restore -> passes."""
    from form.dell_matrix import inference_dock as idock
    owner = "R62_D7"
    p = fresh_program(owner)
    handle = "grant_" + "cd" * 16
    real = idock.contains_protected
    idock.contains_protected = lambda text, prot: False
    try:
        sess = idock.dock(p, "agent-a", provider="fake",
                          fake_mode="reflect")
        r = sess.propose("draft", context={"note": handle})
        leaked = (r.get("ok") is True
                  and handle in p.nursery.proposals[r["pid"]].words)
        check("D7:weakened_leaks", leaked,
              "protection weakened but no leak observed")
    finally:
        idock.contains_protected = real
    # Restored: the same input is rejected again.
    sess2 = idock.dock(p, "agent-a", provider="fake", fake_mode="reflect")
    r2 = sess2.propose("draft", context={"note": handle})
    check("D7:restored_rejects",
          r2.get("ok") is False and r2.get("reason") == "protected_input",
          str(r2))
    clean_owner(owner)



# ------------------------------------------------------- E. representation boundaries
# Director 2026-10-07 (third review): encoded vs decoded, truncation
# vs rejection, validation vs coercion.

def _scripted_provider(payload_text):
    """Fake-like provider returning an exact canned response."""
    from form.dell_matrix import inference_dock as idock
    class _P(idock.FakeProvider):
        def generate(self, prompt, *, timeout_s, max_chars):
            self.calls += 1
            self.last_prompt = prompt
            return payload_text
    return _P()


def test_encoded_handle_in_output_rejected():
    """Director reproduction: JSON words containing gr\u0061nt_<hex>
    decodes to a recognized handle; the decoded screen must reject
    before Nursery.add."""
    import json as _json
    from form.dell_matrix import inference_dock as idock
    owner = "R62_E1"
    p = fresh_program(owner)
    n0 = len(p.nursery.proposals)
    handle = "grant_" + "ef" * 16
    # The provider returns the handle with 'a' unicode-escaped, as raw
    # JSON text carrying single-backslash \u0061 sequences.
    payload = ('{"label": "Encoded", "words": "see gr\\u0061nt_'
               + "ef" * 16 + '"}')
    # Sanity: raw text does NOT contain the literal handle...
    check("E1:raw_hides_handle", "grant_" not in payload, payload[:60])
    # ...but JSON decoding restores it.
    check("E1:decoding_restores",
          _json.loads(payload)["words"].count("grant_") == 1)
    sess = idock.dock(p, "agent-a", provider="fake", fake_mode="valid")
    sess._provider = _scripted_provider(payload)
    r = sess.propose("draft")
    check("E1:rejected",
          r.get("ok") is False and r.get("reason") == "protected_output",
          str(r))
    check("E1:no_proposal", len(p.nursery.proposals) == n0)
    check("E1:receipt_non_reflecting", handle not in str(r), str(r)[:120])


def test_literal_handle_and_label_rejected():
    import json as _json
    from form.dell_matrix import inference_dock as idock
    owner = "R62_E2"
    p = fresh_program(owner)
    n0 = len(p.nursery.proposals)
    handle = "grant_" + "12" * 16
    for field in ("words", "label"):
        data = {"label": "L", "words": "W"}
        data[field] = "has " + handle
        sess = idock.dock(p, "agent-a", provider="fake", fake_mode="valid")
        sess._provider = _scripted_provider(_json.dumps(data))
        r = sess.propose("draft")
        check(f"E2:{field}_rejected",
              r.get("ok") is False and r.get("reason") == "protected_output",
              str(r))
    check("E2:no_proposals", len(p.nursery.proposals) == n0)


def test_clean_escaped_unicode_usable():
    """Escaped Unicode that decodes to nothing protected stays usable."""
    import json as _json
    from form.dell_matrix import inference_dock as idock
    owner = "R62_E3"
    p = fresh_program(owner)
    # caf\u00e9 decodes to 'caf\u00e9' (literal backslash-u text);
    # the JSON layer then decodes \u00e9 -> e-acute. No handle.
    payload = _json.dumps({"label": "Caf\u00e9",
                           "words": "plain caf\u00e9 text"})
    sess = idock.dock(p, "agent-a", provider="fake", fake_mode="valid")
    sess._provider = _scripted_provider(payload)
    r = sess.propose("draft")
    check("E3:accepted", r.get("ok") is True, str(r))
    got = p.nursery.proposals[r["pid"]]
    check("E3:decoded_usable", got.label == "Caf\u00e9", got.label)


def test_transport_size_boundaries():
    """Below/at/over limit, short reads, valid-JSON-prefix + excess."""
    import json as _json
    import urllib.request as _urlreq
    from form.dell_matrix import inference_dock as idock
    owner = "R62_E4"

    def _run(body: bytes, max_bytes: int, chunk_sizes):
        """Drive _read_bounded + parse through a chunked stub."""
        chunks = []
        pos = [0]

        class _R:
            def __enter__(self):
                return self
            def __exit__(self, *a):
                return False
            def read(self, n=None):
                if pos[0] >= len(body):
                    return b""
                # Simulate short reads via the chunk plan.
                want = chunk_sizes[min(len(chunks), len(chunk_sizes) - 1)]
                n = min(n, want) if n else want
                out = body[pos[0]:pos[0] + n]
                pos[0] += len(out)
                chunks.append(out)
                return out

        real = _urlreq.urlopen
        _urlreq.urlopen = lambda *a, **k: _R()
        try:
            from form.llm import bridge as _b
            try:
                return ("parsed", _b._http_json("http://x/", {},
                                                max_bytes=max_bytes))
            except _b._ResponseTooLarge:
                return ("too_large", None)
            except Exception as e:
                return ("error", f"{type(e).__name__}")
        finally:
            _urlreq.urlopen = real

    small = _json.dumps({"a": 1}).encode()
    # Below limit: parses.
    st, _ = _run(small, 100, [7])
    check("E4:below_limit", st == "parsed", st)
    # Exactly at limit: parses.
    st, _ = _run(small, len(small), [3])
    check("E4:at_limit", st == "parsed", st)
    # Over limit: rejected, even with short reads.
    st, _ = _run(small, len(small) - 1, [2])
    check("E4:over_limit", st == "too_large", st)
    # Valid JSON prefix + excessive whitespace/data: the truncated
    # prefix must NOT be accepted because it parses.
    prefix = _json.dumps({"label": "L", "words": "W"}).encode()
    body = prefix + b" " * 5000
    st, val = _run(body, len(prefix) + 10, [64])
    check("E4:prefix_not_accepted", st == "too_large", f"{st} {val}")
    # Director's shape: 1011-byte body, 11-byte limit.
    big = b'{"k": "' + b"x" * 1002 + b'"}'
    check("E4:body_size", len(big) == 1011, str(len(big)))
    st, _ = _run(big, 11, [5])
    check("E4:director_shape", st == "too_large", st)


def test_context_boundary_matrix():
    from form.dell_matrix import inference_dock as idock
    owner = "R62_E5"
    p = fresh_program(owner)
    n0 = len(p.nursery.proposals)

    def _try(ctx):
        sess = idock.dock(p, "agent-a", provider="fake", fake_mode="valid")
        r = sess.propose("draft", context=ctx)
        return r, sess._provider.calls

    # 1,001 scalar entries: every value counts -> rejected.
    r, calls = _try({"items": list(range(1001))})
    check("E5:scalar_budget",
          r.get("ok") is False and r.get("reason") == "bad_context"
          and calls == 0, str(r))
    # 999 scalars: accepted (positive control).
    r, _ = _try({"items": list(range(990))})
    check("E5:under_budget_ok", r.get("ok") is True, str(r))
    # Arbitrary object: rejected, not str()-normalized.
    class _Weird:
        def __str__(self):
            return "innocent"
    r, calls = _try({"obj": _Weird()})
    check("E5:object_rejected",
          r.get("ok") is False and r.get("reason") == "bad_context"
          and calls == 0, str(r))
    # NaN / infinities rejected.
    for v, name in ((float("nan"), "nan"), (float("inf"), "inf"),
                    (float("-inf"), "ninf")):
        r, calls = _try({"v": v})
        check(f"E5:{name}_rejected",
              r.get("ok") is False and r.get("reason") == "bad_context"
              and calls == 0, str(r))
    # Oversized individual string rejected during traversal.
    r, calls = _try({"big": "x" * 200000})
    check("E5:oversize_string",
          r.get("ok") is False and r.get("reason") == "bad_context"
          and calls == 0, str(r))
    # Legitimate nested finite scalars accepted.
    r, _ = _try({"a": {"b": [1, 2.5, "x", True, None]}})
    check("E5:legit_nested_ok", r.get("ok") is True, str(r))
    # Only the accepted proposes created proposals.
    check("E5:only_accepted_proposed",
          len(p.nursery.proposals) == n0 + 2,
          str(len(p.nursery.proposals) - n0))
    clean_owner(owner)


def test_representation_sensitivity():
    """Weaken each new protection: the corresponding control fails;
    restore -> passes."""
    import json as _json
    from form.dell_matrix import inference_dock as idock
    owner = "R62_E6"
    p = fresh_program(owner)
    handle = "grant_" + "ab" * 16
    # Single-backslash \u0061 in the raw JSON text, as in E1.
    payload = ('{"label": "L", "words": "x gr\\u0061nt_' + "ab" * 16 + '"}')

    # Weaken the whole output protection (contains_protected_decoded
    # feeds both the raw and the parsed screens).
    real_cpd = idock.contains_protected_decoded
    idock.contains_protected_decoded = lambda text, prot: False
    try:
        sess = idock.dock(p, "agent-a", provider="fake", fake_mode="valid")
        sess._provider = _scripted_provider(payload)
        r = sess.propose("draft")
        leaked = (r.get("ok") is True
                  and handle in p.nursery.proposals[r["pid"]].words)
        check("E6:weakened_screen_leaks", leaked, str(r))
    finally:
        idock.contains_protected_decoded = real_cpd
    # Restored.
    sess2 = idock.dock(p, "agent-a", provider="fake", fake_mode="valid")
    sess2._provider = _scripted_provider(payload)
    r2 = sess2.propose("draft")
    check("E6:restored_rejects",
          r2.get("ok") is False and r2.get("reason") == "protected_output",
          str(r2))

    # Weaken the transport bound: truncated prefix must not parse-accept.
    from form.llm import bridge as _b
    real_read = _b._read_bounded
    _b._read_bounded = lambda resp, max_bytes: resp.read(max_bytes)
    try:
        import urllib.request as _urlreq
        body = b'{"a": 1}' + b" " * 500

        class _R:
            def __init__(self):
                self._done = False
            def __enter__(self):
                return self
            def __exit__(self, *a):
                return False
            def read(self, n=None):
                if self._done:
                    return b""
                self._done = True
                return body[:n] if n else body

        real_u = _urlreq.urlopen
        _urlreq.urlopen = lambda *a, **k: _R()
        try:
            val = _b._http_json("http://x/", {}, max_bytes=10)
            parsed = True
        except Exception:
            parsed = False
        finally:
            _urlreq.urlopen = real_u
        check("E6:weakened_transport_parses_prefix", parsed,
              "truncated prefix was rejected even when weakened")
    finally:
        _b._read_bounded = real_read
    clean_owner(owner)


def test_child_process_representation_sweep():
    """Fixed child script replays the Director reproductions in a real
    OS process; parent asserts receipts and zero state change."""
    import subprocess
    owner = "R62_E7"
    fresh_program(owner)
    clean_owner(owner)
    args = json.dumps({"repo": ROOT, "owner": owner,
                       "kind": "repr_sweep"})
    proc = subprocess.run(
        [sys.executable, "form/mandell/r62_child.py", args],
        cwd=ROOT, capture_output=True, text=True, timeout=120)
    check("E7:child_ok", proc.returncode == 0, proc.stderr[:300])
    out = json.loads(proc.stdout.strip().splitlines()[-1])
    check("E7:encoded_rejected", out.get("encoded") == "protected_output",
          str(out))
    check("E7:oversized_rejected", out.get("oversized") == "response_too_large",
          str(out))
    check("E7:deep_rejected", out.get("deep") == "bad_context", str(out))
    check("E7:zero_proposals", out.get("proposals") == 0, str(out))
    clean_owner(owner)


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
               test_no_eval_or_shell_on_output,
               test_director_secret_value_reproduction,
               test_director_response_bound_reproduction,
               test_director_context_bound_reproduction,
               test_transport_contract_stubbed_http,
               test_fresh_process_reload,
               test_save_guard_genuine,
               test_canary_sensitivity,
               test_encoded_handle_in_output_rejected,
               test_literal_handle_and_label_rejected,
               test_clean_escaped_unicode_usable,
               test_transport_size_boundaries,
               test_context_boundary_matrix,
               test_representation_sensitivity,
               test_child_process_representation_sweep]:
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
