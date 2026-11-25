#!/usr/bin/env python3
"""Offline structural preflight, NOT authentication, execution or certification.

No network, imports of project runtime, mutation, evaluation of submitted code,
or shell interpolation. --repo optionally verifies immutable Git objects.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

SHA = re.compile(r"[0-9a-f]{40}\Z")
DIGEST = re.compile(r"[0-9a-f]{64}\Z")
STATES = {"UNKNOWN", "CERTIFIED", "CERTIFIED_WITH_EXCEPTIONS", "PARTIAL", "DECLINED"}


def reachable_ref(value):
    # Syntax only: the reviewer still verifies permissions, bytes and reachability.
    return isinstance(value, str) and value.startswith("https://") and len(value) > 12


def validate(packet, gate="submit", repo=None):
    errors = []

    def require(condition, message):
        if not condition:
            errors.append(message)

    if not isinstance(packet, dict):
        return ["packet must be an object"]
    try:
        require(packet["schema_version"] == 1 and type(packet["schema_version"]) is int,
                "schema_version must be integer 1")
        for key in ("id", "scope", "authority_ref", "next_action"):
            require(isinstance(packet[key], str) and bool(packet[key].strip()), key + " required")
        require(packet["author"] in ("Uni", "Director", "Ace"), "author invalid")
        require(packet["lane"] in ("runtime", "process", "docs"), "lane invalid")
        require(reachable_ref(packet["report_ref"]), "report_ref must be a reachable HTTPS artifact, not a local path")
        require(packet["delivery"] in ("PLANNED", "IMPLEMENTING", "VERIFIED", "MERGED"), "delivery invalid")
        require(packet["review"] in ("NOT_SUBMITTED", "SUBMITTED", "IN_REVIEW", "RULED", "ACKNOWLEDGED"), "review invalid")
        target = packet["target"]
        for key in ("head", "tree"):
            require(isinstance(target[key], str) and SHA.fullmatch(target[key]) is not None,
                    "target." + key + " must be full SHA")
        env = packet["environment"]
        for key in ("os", "python", "architecture", "isolation", "sensitivity"):
            require(isinstance(env[key], str) and bool(env[key].strip()), "environment." + key + " required")
        require(isinstance(packet["owners"], list) and bool(packet["owners"]), "owners required")
        for owner in packet["owners"]:
            for key in ("name", "state_class", "boundary", "oracle"):
                require(isinstance(owner[key], str) and bool(owner[key].strip()), "owner." + key + " required")
            require(owner["state_class"] in ("executable", "durable", "evidence", "presentation", "process"), "state_class invalid")

        evidence = packet["evidence"]
        claims = packet["claims"]
        require(isinstance(evidence, list) and bool(evidence), "evidence required")
        require(isinstance(claims, list) and bool(claims), "claims required")
        by_id = {}
        for item in evidence:
            require(item["id"] not in by_id, "duplicate evidence id")
            by_id[item["id"]] = item
            require(item["kind"] in ("EXECUTED", "SOURCE", "PROGRAM_RECORD", "CI"), "evidence kind invalid")
            require(item["result"] in ("PASS", "FAIL", "UNAVAILABLE", "OBSERVED"), "evidence result invalid")
            require(item["head"] == target["head"], "evidence head differs from target")
            require(reachable_ref(item["artifact"]), "evidence artifact must be HTTPS")
            require(DIGEST.fullmatch(item["sha256"]) is not None, "evidence digest required")
            for key in ("executor", "command", "assertion"):
                require(isinstance(item[key], str) and bool(item[key].strip()), "evidence." + key + " required")
            if item["kind"] == "EXECUTED":
                require(type(item["exit_code"]) is int, "executed evidence exit code required")
                if item["result"] == "PASS":
                    require(item["exit_code"] == 0, "PASS with nonzero exit")
        claim_ids = set()
        for claim in claims:
            require(claim["id"] not in claim_ids, "duplicate claim id")
            claim_ids.add(claim["id"])
            require(bool(claim["text"].strip()), "claim text required")
            require(claim["level"] in ("EXECUTED", "SOURCE", "REPORTED", "UNKNOWN"), "claim level invalid")
            require(isinstance(claim["evidence_ids"], list), "claim evidence_ids must be list")
            refs = [by_id.get(e) for e in claim["evidence_ids"]]
            require(all(refs), "unknown claim evidence id")
            if claim["level"] != "UNKNOWN":
                require(bool(refs), "supported claim needs evidence")
            if claim["level"] == "EXECUTED":
                require(any(e and e["kind"] == "EXECUTED" and e["result"] == "PASS" for e in refs),
                        "executed claim needs passing execution, not lint/source/reported evidence")

        for field in ("findings", "discrepancies", "anticipated_probes", "questions", "acknowledgments"):
            require(isinstance(packet[field], list), field + " must be list")
        for d in packet["discrepancies"]:
            require(d["status"] in ("UNRESOLVED", "RESOLVED", "EXCLUDED"), "discrepancy status invalid")
            require(bool(d["id"]) and bool(d["observations"]), "discrepancy identity/observations missing")
            if d["status"] == "RESOLVED":
                require(reachable_ref(d["experiment_ref"]), "resolved discrepancy needs discriminating experiment")
        for f in packet["findings"]:
            require(f["status"] in ("OPEN", "CLOSED", "EXCLUDED"), "finding status invalid")
            require(f["severity"] in ("P1", "P2", "P3"), "finding severity invalid")
            if f["status"] == "CLOSED":
                require(reachable_ref(f["closure_ref"]), "closed finding needs closure evidence")
        require(type(packet["stateful"]) is bool, "stateful must be Boolean")
        require(isinstance(packet["failure_matrix"], list), "failure_matrix must be list")
        if packet["stateful"]:
            covered = {f["boundary"] for f in packet["failure_matrix"]}
            require({"forward_write", "compensation_write", "restart", "retry"} <= covered,
                    "stateful matrix lacks forward/compensation/restart/retry")
        for f in packet["failure_matrix"]:
            require(bool(f["oracle"]) and f["evidence_id"] in by_id, "failure row lacks oracle/evidence")
        cleanup = packet["cleanup"]
        require(cleanup["status"] in ("COMPLETE", "INCOMPLETE", "UNAVAILABLE", "NOT_APPLICABLE"), "cleanup status invalid")
        if cleanup["status"] == "COMPLETE":
            require(cleanup["evidence_id"] in by_id and by_id[cleanup["evidence_id"]]["result"] == "PASS",
                    "complete cleanup needs passing evidence")

        cert = packet["certification"]
        require(cert["status"] in STATES, "certification status invalid")
        if cert["status"] != "UNKNOWN":
            require(cert["actor"] == "Director", "certification belongs to Director")
            require(reachable_ref(cert["ruling_ref"]), "ruling reference required")
            require(cert["head"] == target["head"], "ruling target mismatch")
        require(isinstance(cert["exceptions"], list), "exceptions must be list")
        if cert["status"] in ("CERTIFIED_WITH_EXCEPTIONS", "PARTIAL"):
            require(bool(cert["exceptions"]), "bounded certificate must state exceptions")
        if cert["status"] == "CERTIFIED":
            require(not any(f["status"] == "OPEN" for f in packet["findings"]), "full certificate with open findings")
            require(not any(d["status"] == "UNRESOLVED" for d in packet["discrepancies"]), "full certificate with unresolved discrepancy")
            require(cleanup["status"] not in ("INCOMPLETE", "UNAVAILABLE"), "full certificate with incomplete cleanup")

        if gate in ("merge", "close"):
            require(reachable_ref(packet["merge_authority_ref"]), "merge authority reference required")
            ci = packet["ci"]
            require(isinstance(ci["required"], list) and bool(ci["required"]), "required CI names missing")
            runs = ci["runs"]
            require(len({r["name"] for r in runs}) == len(runs), "duplicate CI name")
            indexed = {r["name"]: r for r in runs}
            for name in ci["required"]:
                run = indexed.get(name)
                require(run is not None, "missing required CI " + name)
                if run:
                    require(run["head"] == target["head"], "CI head mismatch")
                    require(run["status"] == "completed" and run["conclusion"] == "success", "required CI not complete SUCCESS")
                    require(reachable_ref(run["url"]), "CI run URL required")
            if packet["lane"] == "runtime":
                require(set(ci["required"]) >= {"Form smoke", "Python package"}, "standing CI omitted")
                require({"forward", "twice", "reverse"} <= set(packet["regression"]), "standing regression legs missing")
                for leg in ("forward", "twice", "reverse"):
                    ev = by_id.get(packet["regression"].get(leg))
                    require(ev is not None and ev["kind"] == "EXECUTED" and ev["result"] == "PASS", "regression leg not proven " + leg)
        if gate == "close":
            merge = packet["merge"]
            require(packet["delivery"] == "MERGED", "close gate requires merged delivery")
            require(SHA.fullmatch(merge["sha"]) is not None, "merge SHA required")
            require(merge["tree"] == target["tree"], "merge tree mismatch")
            require(merge["fresh_clone_result"] == "PASS" and reachable_ref(merge["fresh_clone_ref"]), "fresh clone evidence required")
        if repo:
            require(SHA.fullmatch(target["head"]) is not None, "unsafe Git head")
            if SHA.fullmatch(target["head"]):
                def tree_at(sha):
                    return subprocess.check_output(["git", "-C", str(repo), "rev-parse", sha + "^{tree}"], text=True, stderr=subprocess.PIPE).strip()
                require(tree_at(target["head"]) == target["tree"], "Git candidate tree mismatch")
                if gate == "close" and SHA.fullmatch(packet["merge"]["sha"]):
                    require(tree_at(packet["merge"]["sha"]) == target["tree"], "Git merge tree mismatch")
    except (KeyError, TypeError, AttributeError, ValueError, subprocess.CalledProcessError, OSError) as exc:
        errors.append("invalid/missing packet field or Git object: " + str(exc))
    return errors


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("packet", type=Path)
    ap.add_argument("--gate", choices=("submit", "merge", "close"), default="submit")
    ap.add_argument("--repo", type=Path)
    args = ap.parse_args()
    try:
        with args.packet.open(encoding="utf-8") as f:
            packet = json.load(f)
        errors = validate(packet, args.gate, args.repo)
    except (OSError, ValueError) as exc:
        errors = [str(exc)]
    print(json.dumps({"gate": args.gate, "consistent": not errors, "errors": errors,
                      "authority": "none; structural checks only"}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
