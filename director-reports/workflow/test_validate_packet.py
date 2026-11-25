#!/usr/bin/env python3
"""Adversarial structural gate tests; synthetic records never certify a product."""
from copy import deepcopy
import json
import hashlib
from pathlib import Path
import tempfile
import subprocess
import unittest
from validate_packet import validate


def fixture():
    p = json.loads(Path(__file__).with_name("packet-template.json").read_text())
    p.update(id="SYNTHETIC", scope="synthetic contract", authority_ref="https://example.invalid/directive",
             report_ref="https://example.invalid/report", stateful=False, delivery="MERGED")
    p["target"] = {"head": "a" * 40, "tree": "b" * 40}
    e = p["evidence"][0]
    e.update(head="a" * 40, artifact="https://example.invalid/log", sha256="c" * 64,
             command="synthetic command", assertion="synthetic oracle")
    p["merge_authority_ref"] = "https://example.invalid/authority"
    p["ci"]["runs"] = [{"name": name, "head": "a" * 40, "status": "completed",
                            "conclusion": "success", "url": "https://example.invalid/run/" + str(i)}
                           for i, name in enumerate(p["ci"]["required"])]
    p["regression"] = dict.fromkeys(("forward", "twice", "reverse"), "E1")
    p["merge"] = {"sha": "d" * 40, "tree": "b" * 40, "fresh_clone_result": "PASS",
                  "fresh_clone_ref": "https://example.invalid/fresh"}
    return p


class GateTests(unittest.TestCase):
    def test_valid_gates_allow_merged_uncertified(self):
        for gate in ("submit", "merge", "close"):
            self.assertEqual(validate(fixture(), gate), [])

    def test_negative_matrix(self):
        cases = [
            ("short head", lambda p: p["target"].update(head="abc")),
            ("bad tree", lambda p: p["target"].update(tree="x" * 40)),
            ("stale execution", lambda p: p["evidence"][0].update(head="e" * 40)),
            ("failed execution", lambda p: p["evidence"][0].update(exit_code=1)),
            ("local report", lambda p: p.update(report_ref="~/workspace/report.md")),
            ("local log", lambda p: p["evidence"][0].update(artifact="/tmp/log")),
            ("no artifact digest", lambda p: p["evidence"][0].update(sha256="")),
            ("duplicate evidence", lambda p: p["evidence"].append(deepcopy(p["evidence"][0]))),
            ("unknown evidence", lambda p: p["claims"][0].update(evidence_ids=["missing"])),
            ("source masquerades as execution", lambda p: p["evidence"][0].update(kind="SOURCE")),
            ("lint masquerades as execution", lambda p: p["evidence"][0].update(kind="CI")),
            ("missing assertion", lambda p: p["evidence"][0].update(assertion="")),
            ("no evidence", lambda p: p.update(evidence=[])),
            ("no claims", lambda p: p.update(claims=[])),
            ("stateful no failure matrix", lambda p: p.update(stateful=True)),
            ("false cleanup", lambda p: p.update(cleanup={"status":"COMPLETE","evidence_id":"missing"})),
            ("missing owner", lambda p: p.update(owners=[])),
            ("missing environment", lambda p: p["environment"].update(isolation="")),
            ("queued CI", lambda p: p["ci"]["runs"][0].update(status="queued")),
            ("cancelled CI", lambda p: p["ci"]["runs"][0].update(conclusion="cancelled")),
            ("skipped CI", lambda p: p["ci"]["runs"][0].update(conclusion="skipped")),
            ("unavailable CI", lambda p: p["ci"]["runs"][0].update(conclusion="unavailable")),
            ("stale CI", lambda p: p["ci"]["runs"][0].update(head="e" * 40)),
            ("missing CI", lambda p: p["ci"].update(runs=[])),
            ("duplicate CI", lambda p: p["ci"]["runs"].append(deepcopy(p["ci"]["runs"][0]))),
            ("required CI removed", lambda p: p["ci"].update(required=["Python package"])),
            ("missing regression leg", lambda p: p["regression"].pop("twice")),
            ("merge tree differs", lambda p: p["merge"].update(tree="e" * 40)),
            ("fresh clone missing", lambda p: p["merge"].update(fresh_clone_result="")),
            ("not merged", lambda p: p.update(delivery="VERIFIED")),
            ("Uni self certificate", lambda p: p["certification"].update(status="CERTIFIED",actor="Uni")),
            ("boolean schema version", lambda p: p.update(schema_version=True)),
            ("empty authority", lambda p: p.update(authority_ref="")),
            ("duplicate claim", lambda p: p["claims"].append(deepcopy(p["claims"][0]))),
            ("closed finding no evidence", lambda p: p["findings"].append({"id":"F","severity":"P1","status":"CLOSED","closure_ref":""})),
            ("false resolution", lambda p: p["discrepancies"].append({"id":"D","status":"RESOLVED","observations":["red","green"],"experiment_ref":""})),
        ]
        for label, mutate in cases:
            with self.subTest(label=label):
                p = fixture()
                mutate(p)
                self.assertTrue(validate(p, "close"), label)
        self.assertEqual(len(cases), 36)

    def test_certificate_is_bounded_and_not_automatic(self):
        p = fixture()
        p["certification"].update(status="CERTIFIED", actor="Director", head="a" * 40,
                                  ruling_ref="https://example.invalid/ruling")
        self.assertEqual(validate(p), [])
        p["discrepancies"] = [{"id":"D","status":"UNRESOLVED","observations":["red","green"]}]
        self.assertTrue(validate(p))
        p["certification"].update(status="CERTIFIED_WITH_EXCEPTIONS", exceptions=["D excluded from scope"])
        self.assertEqual(validate(p), [])
        p["certification"]["head"] = "e" * 40
        self.assertTrue(validate(p))

    def test_malformed_input_is_rejected(self):
        for p in (None, [], "text", {}, {"schema_version":1}, {"schema_version":1,"id":[]}):
            self.assertTrue(validate(p))
        p = fixture()
        p["evidence"][0]["sha256"] = None
        self.assertTrue(validate(p))

    def test_template_is_not_false_ready(self):
        p = json.loads(Path(__file__).with_name("packet-template.json").read_text())
        self.assertTrue(validate(p))

    def test_refinement_ledger(self):
        rows = json.loads(Path(__file__).with_name("refinements.json").read_text())
        self.assertEqual(len(rows), 100)
        previous = "0" * 64
        changes = set()
        for i, original in enumerate(rows, 1):
            row = dict(original)
            digest = row.pop("revision")
            self.assertEqual(row["pass_id"], i)
            self.assertEqual(row["previous_revision"], previous)
            self.assertEqual(hashlib.sha256(json.dumps(row, sort_keys=True).encode()).hexdigest(), digest)
            self.assertNotIn(row["retained_change"], changes)
            changes.add(row["retained_change"])
            previous = digest

    def test_real_git_tree_check(self):
        with tempfile.TemporaryDirectory() as d:
            subprocess.run(["git","init","-q",d],check=True)
            tree = subprocess.check_output(["git","-C",d,"mktree"], input="",text=True).strip()
            head = subprocess.check_output(["git","-C",d,"-c","user.name=Fixture","-c","user.email=fixture@example.invalid",
                                            "commit-tree",tree,"-m","synthetic"],text=True).strip()
            p = fixture();p["target"] = {"head":head,"tree":tree};p["evidence"][0]["head"] = head
            self.assertEqual(validate(p,repo=d), [])
            p["target"]["tree"] = "b" * 40
            self.assertTrue(validate(p,repo=d))


if __name__ == "__main__":
    unittest.main()
