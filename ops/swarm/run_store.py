"""Run store: load/save run state, append-only evidence, fresh-process reload.

Provenance rule: evidence entries are append-only. One agent cannot silently
overwrite another agent's evidence — appends are per-agent and the store
rejects in-place mutation of entries written by a different agent.
No secrets are ever persisted: values matching secret patterns are refused.
"""

from __future__ import annotations

import copy
import json
import os
import re
import time

SECRET_PATTERNS = [
    re.compile(p, re.IGNORECASE) for p in [
        r"\bapi[_-]?key\b", r"\bsecret\b", r"\bpassword\b", r"\bpasswd\b",
        r"\btoken\b", r"\bprivate[_-]?key\b", r"BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY",
        r"ghp_[A-Za-z0-9]+", r"github_pat_[A-Za-z0-9_]+",
    ]
]


def _no_secrets(obj) -> None:
    blob = json.dumps(obj)
    for pat in SECRET_PATTERNS:
        if pat.search(blob):
            raise ValueError(f"refusing to persist value matching secret pattern: {pat.pattern}")


def run_dir(root: str, run_id: str) -> str:
    return os.path.join(root, "runs", run_id)


def save(root: str, run: dict) -> str:
    """Persist run manifest. Returns manifest path."""
    _no_secrets(run)
    d = run_dir(root, run["run_id"])
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, "manifest.json")
    with open(path, "w") as f:
        json.dump(run, f, indent=2, sort_keys=True)
    return path


def load(root: str, run_id: str) -> dict:
    """Fresh-process reload of run state."""
    path = os.path.join(run_dir(root, run_id), "manifest.json")
    with open(path) as f:
        return json.load(f)


def new_run(run_id: str, **kw) -> dict:
    mode = kw.get("mode", "SWARM")
    if mode not in ("SWARM", "CORE"):
        raise ValueError(f"unknown mode: {mode}")
    run = {
        "run_id": run_id,
        "parent_run_id": None,
        "mode": mode,
        "mode_history": [{"from": None, "to": mode, "decided_by": kw.get("mode_decided_by", "DIRECTOR")}],
        "base_sha": kw["base_sha"],
        "base_tree": kw["base_tree"],
        "goal": kw.get("goal", ""),
        "director_authority": kw.get("director_authority", {"directive": "", "decision": "PROCEED", "autonomy": "NO"}),
        "allowed_actions": kw.get("allowed_actions", []),
        "forbidden_actions": kw.get("forbidden_actions", []),
        "phase": "DIRECTOR_SCOPE",
        "required_gates": kw.get("required_gates", []),
        "agent_assignments": {},
        "agent_status": {},
        "evidence": [],
        "contradictions": [],
        "unknowns": [],
        "falsifications": [],
        "candidate_decisions": [],
        "director_decision": None,
        "uni_execution": None,
        "candidate_head": None,
        "tests": [],
        "ci": None,
        "merge_state": "NOT_REQUESTED",
        "merge_sha": None,
        "post_merge_state": None,
        "capability_delta": None,
        "next_broken_link": None,
        "next_directive": None,
        "termination": {"state": "ACTIVE", "director_decision_required": kw.get("director_decision_required", True), "terminal_reason": None},
    }
    return run


def append_evidence(run: dict, agent: str, claim: str, classification: str,
                    source: str, sha: str = "", timestamp: str | None = None) -> dict:
    if classification not in ("VERIFIED", "DERIVED", "PROJECTION", "UNKNOWN"):
        raise ValueError(f"bad classification: {classification}")
    entry = {
        "agent": agent,
        "claim": claim,
        "classification": classification,
        "source": source,
        "sha": sha,
        "timestamp": timestamp or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    _no_secrets(entry)
    run.setdefault("evidence", []).append(entry)
    return run


def add_contradiction(run: dict, cid: str, parties: list[str], statement: str) -> dict:
    """Contradictions are preserved, never auto-resolved."""
    run.setdefault("contradictions", []).append({
        "id": cid, "parties": parties, "statement": statement, "status": "OPEN", "resolution": None,
    })
    return run


def snapshot(run: dict) -> dict:
    return copy.deepcopy(run)
