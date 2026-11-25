#!/usr/bin/env python3
"""R6.2 fixed child process. Args: single JSON argument.

Performs the full circuit in a SEPARATE OS process:
docked propose (fake) -> grant -> bound-endpoint confirm -> v2 save.
Prints a JSON result line. Parent inspects via production reload.
"""
import json
import os
import sys

args = json.loads(sys.argv[1])
repo, owner = args["repo"], args["owner"]
kind = args.get("kind", "full_circuit")
sys.path.insert(0, repo)
os.chdir(repo)

from form.open import open_program
from form.dell_matrix import inference_dock as idock

p = open_program(owner)

if kind == "repr_sweep":
    # Director reproductions in a real OS process.
    handle = "grant_" + "ef" * 16
    words = "see " + handle.replace("a", "\\u0061")
    payload = json.dumps({"label": "Encoded", "words": words})

    class _P(idock.FakeProvider):
        def __init__(self, text):
            super().__init__("valid")
            self._text = text
        def generate(self, prompt, *, timeout_s, max_chars):
            self.calls += 1
            return self._text

    n0 = len(p.nursery.proposals)
    sess = idock.dock(p, "agent-a", provider="fake", fake_mode="valid")
    sess._provider = _P(payload)
    r_enc = sess.propose("draft")

    sess2 = idock.dock(p, "agent-a", provider="fake", fake_mode="valid",
                       max_response_chars=10)
    r_over = sess2.propose("draft")

    deep = cur = {}
    for _ in range(50):
        cur["n"] = {}
        cur = cur["n"]
    sess3 = idock.dock(p, "agent-a", provider="fake", fake_mode="valid")
    r_deep = sess3.propose("draft", context=deep)

    print(json.dumps({
        "ok": True,
        "encoded": r_enc.get("reason"),
        "oversized": r_over.get("reason"),
        "deep": r_deep.get("reason"),
        "proposals": len(p.nursery.proposals) - n0,
    }))
else:
    from form.dell_matrix import agent_authority as aa
    from form import persist_rest
    sess = idock.dock(p, "agent-a", provider="fake", fake_mode="valid")
    r = sess.propose("child process draft")
    assert r.get("ok") is True, r
    pid = r["pid"]
    root = aa.issue_root_grant(p, issuer="human:ace", subject="agent-a",
                               max_depth=1)
    child = aa.attenuate_for(p, root["grant_id"], target=pid,
                             content_pid=pid)
    ep = aa.bind_agent(p, "agent-a")
    c = ep.confirm(pid, child["grant_id"])
    assert c["ok"] is True, c
    persist_rest.save(p)
    print(json.dumps({"ok": True, "pid": pid}))
