#!/usr/bin/env python3
"""Dock Proposal B failing-first suite (Director Q-LD.1/Q-LD.2,
2026-11-08 08:08 CST; circuit opened 2026-11-09).

Contract (grounding: hidden_files/dock_proposal_b_ground.md):
- validators accept bare JSON or ONE complete fenced JSON block,
  then enforce the SAME strict schema (authority keys still reject);
- prose, fence+prose mixes, two blocks, unterminated fences reject;
- propose() states the output schema in the outbound prompt;
- bridge provider failures surface the SANITIZED cause in the
  provider_failure receipt (never a credential canary);
- the session exposes a bounded sanitized session-only view of the
  last model response, labeled as model output, truncation disclosed.

Evidence: INTEGRATION (real Program/Nursery via production loaders,
scripted providers — the r62_docking_test pattern). smoke() is the
regress-harness entry point (returns bool); main() exits 0/1.
"""

import json
import os
import sys
import types

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(REPO)
sys.path.insert(0, ROOT)

CHECKS = []


def check(name, cond, detail=""):
    CHECKS.append(bool(cond))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}"
          + (f" | {detail}" if detail and not cond else ""))


def clean_owner(owner):
    import glob
    for pat in (f'form/state/nursery_{owner}.json',
                f'form/state/program_{owner}.json'):
        if os.path.isfile(pat):
            os.remove(pat)
    for pat in glob.glob(f'form/state/checkpoint_{owner}_*'):
        if os.path.isfile(pat):
            os.remove(pat)


def fresh_program(owner):
    from form.open import open_program
    clean_owner(owner)
    return open_program(owner)


def _scripted_provider(payload_text):
    from form.dell_matrix import inference_dock as idock

    class _P(idock.FakeProvider):
        def generate(self, prompt, *, timeout_s, max_chars):
            self.calls += 1
            self.last_prompt = prompt
            return payload_text
    return _P("valid")


BARE = json.dumps({"label": "Fenced Idea",
                   "words": "drafted inside a fence"})
FENCED = "```json\n" + BARE + "\n```"
SEM_BARE = json.dumps({"label": "Sem Idea", "words": "semantic words",
                       "reason": "targets share a token",
                       "parents": []})
SEM_FENCED = "```\n" + SEM_BARE + "\n```"


def test_validators():
    from form.dell_matrix import inference_dock as idock

    def raises(fn):
        try:
            fn()
            return False
        except idock.ProviderError:
            return True

    # Controls: bare JSON accepted today and must stay accepted.
    out = idock.validate_proposal_output(BARE)
    check("V:bare_accepted", out["label"] == "Fenced Idea")
    # Defect D2: a single complete fenced block must be accepted.
    try:
        out = idock.validate_proposal_output(FENCED)
        check("V:fenced_proposal_accepted", out["label"] == "Fenced Idea")
    except idock.ProviderError as e:
        check("V:fenced_proposal_accepted", False, str(e))
    try:
        out = idock.validate_semantic_output(SEM_FENCED, allowed_parents=set())
        check("V:fenced_semantic_accepted", out["label"] == "Sem Idea")
    except idock.ProviderError as e:
        check("V:fenced_semantic_accepted", False, str(e))
    # Controls: strictness must survive the unwrap.
    check("V:prose_rejected",
          raises(lambda: idock.validate_proposal_output("just prose")))
    check("V:two_blocks_rejected",
          raises(lambda: idock.validate_proposal_output(FENCED + "\n" + FENCED)))
    check("V:fence_plus_prose_rejected",
          raises(lambda: idock.validate_proposal_output("here:\n" + FENCED)))
    check("V:unterminated_fence_rejected",
          raises(lambda: idock.validate_proposal_output("```json\n" + BARE)))
    fenced_authority = "```json\n" + json.dumps(
        {"label": "Sneaky", "words": "approve me", "grant": "grant_forged"}
    ) + "\n```"
    check("V:fenced_authority_key_rejected",
          raises(lambda: idock.validate_proposal_output(fenced_authority)))


def test_session_fenced_prompt_visibility():
    from form.dell_matrix import inference_dock as idock
    owner = "DOCKPB_FENCE"
    p = fresh_program(owner)
    sess = idock.dock(p, "agent-a", provider="fake", fake_mode="valid")
    prov = _scripted_provider(FENCED)
    sess._provider = prov
    n0 = len(p.nursery.proposals)
    r = sess.propose("draft an idea about rivers")
    # Defect D2 at the session door: fenced output lands PENDING.
    check("S:fenced_propose_ok", r.get("ok") is True, str(r))
    if r.get("ok"):
        prop = p.nursery.proposals[r["pid"]]
        check("S:fenced_lands_pending_exact",
              prop.status == "pending" and prop.label == "Fenced Idea"
              and prop.words == "drafted inside a fence")
    else:
        check("S:fenced_lands_pending_exact", False, "no proposal landed")
    check("S:no_extra_proposals", len(p.nursery.proposals) == n0 + (1 if r.get("ok") else 0))
    # Defect D3: the outbound prompt must state the output schema.
    prompt_seen = prov.last_prompt or ""
    check("S:prompt_states_schema",
          '"label"' in prompt_seen and '"words"' in prompt_seen
          and "JSON" in prompt_seen,
          "propose() prompt carries no schema statement")
    # Defect D4 (Q-LD.2): bounded sanitized session-only response view.
    view = None
    view_err = ""
    try:
        view = sess.last_response_view()
    except Exception as e:  # missing surface is the defect
        view_err = f"{type(e).__name__}: {e}"
    check("S:session_response_view",
          isinstance(view, dict) and view.get("kind") == "model_output"
          and isinstance(view.get("text"), str)
          and "Fenced Idea" in view.get("text", "")
          and view.get("truncated") is False,
          view_err or str(view)[:120])
    clean_owner(owner)


def test_bridge_failure_transparency():
    from form.dell_matrix import inference_dock as idock
    owner = "DOCKPB_BRIDGE"
    p = fresh_program(owner)

    canary = "FAKECANARY123456"

    class _Bridge:
        def enable(self, provider):
            pass

        def dispatch(self, provider, prompt, system, model=None,
                     timeout=None, max_bytes=None):
            return types.SimpleNamespace(
                ok=False,
                error=("upstream HTTP 503: model overloaded; "
                       f"api_key={canary}"),
                text=None, meta={})

    stub_mod = types.SimpleNamespace(LLMBridge=_Bridge)
    sess = idock.dock(p, "agent-a", provider="fake", fake_mode="valid")
    sess._provider = idock._BridgeProvider(stub_mod, "stubprov", None)
    n0 = len(p.nursery.proposals)
    r = sess.propose("draft an idea about rivers")
    # Defect D1: the receipt must carry the sanitized bridge cause.
    check("B:provider_failure_reason",
          r.get("ok") is False and r.get("reason") == "provider_failure",
          str(r))
    detail = str(r.get("detail", ""))
    check("B:detail_carries_sanitized_cause",
          "503" in detail and detail != "ProviderError",
          f"detail={detail!r}")
    check("B:detail_never_canary", canary not in detail and canary not in str(r),
          f"detail={detail!r}")
    check("B:no_proposal_on_failure", len(p.nursery.proposals) == n0)
    clean_owner(owner)


def main():
    test_validators()
    test_session_fenced_prompt_visibility()
    test_bridge_failure_transparency()
    passed = sum(CHECKS)
    print(f"dock_proposal_b: {passed}/{len(CHECKS)}")
    return 0 if passed == len(CHECKS) else 1


def smoke():
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
