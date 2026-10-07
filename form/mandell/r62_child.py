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
sys.path.insert(0, repo)
os.chdir(repo)

from form.open import open_program
from form.dell_matrix import inference_dock as idock
from form.dell_matrix import agent_authority as aa
from form import persist_rest

p = open_program(owner)
sess = idock.dock(p, "agent-a", provider="fake", fake_mode="valid")
r = sess.propose("child process draft")
assert r.get("ok") is True, r
pid = r["pid"]
root = aa.issue_root_grant(p, issuer="human:ace", subject="agent-a",
                           max_depth=1)
child = aa.attenuate_for(p, root["grant_id"], target=pid, content_pid=pid)
ep = aa.bind_agent(p, "agent-a")
c = ep.confirm(pid, child["grant_id"])
assert c.get("ok") is True, c
persist_rest.save(p)
print(json.dumps({"ok": True, "pid": pid}))
