#!/usr/bin/env python3
"""R6.1 independent authorization oracle (Director 2026-10-07 AMEND).

A small test-only authorization model written FROM THE DECLARED
CONTRACT (the directive text). It does NOT call production check(),
chain validators, or attenuation logic to compute expected
authorization. Table-driven scenarios are executed against BOTH the
model and the production AcceptancePolicy; every check case must
agree.

Model contract (from the directive):
- issued/session-valid credential; bound subject/owner/operation
- target/content restrictions (None = unconstrained; every Mapping
  including {} is bound)
- attenuation narrows only (subject/owner/operation equal; target/
  content narrow-or-equal; delegation depth strictly decreases)
- ancestor revocation denies unfinished descendants (full chain)
- session reset invalidates grants

Sensitivity: a deliberately weakened production check must DISAGREE
with the oracle on revocation cases (proving the oracle is not a
tautology); production behavior is restored before final verification.

Evidence class: UNIT_SYNTHETIC model vs INTEGRATION production.
"""

import hashlib
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


# ---------------------------------------------------------------- model
# Independent: stdlib only. No production imports.

def _mhash(content):
    return hashlib.sha256(
        json.dumps(content, sort_keys=True,
                   separators=(",", ":")).encode()).hexdigest()


class Oracle:
    """Test-only authorization model from the declared contract."""

    OP = "nursery.confirm"
    MAX_DEPTH = 8

    def __init__(self):
        self.session = "oracle-session-1"
        self.grants = {}
        self.revoked = set()
        self._n = 0

    def _new_id(self):
        self._n += 1
        return f"oracle-grant-{self._n}"

    def issue(self, *, issuer, subject, owner, operation=OP,
              target=None, content=None, depth=1):
        if not isinstance(issuer, str) or not issuer:
            return None, "bad issuer"
        if not isinstance(subject, str) or not subject:
            return None, "bad subject"
        if not isinstance(owner, str) or not owner:
            return None, "bad owner"
        if operation != self.OP:
            return None, "ungrantable operation"
        if target is not None and (not isinstance(target, str) or not target):
            return None, "bad target"
        if content is not None and not isinstance(content, dict):
            return None, "bad content"
        if not isinstance(depth, int) or isinstance(depth, bool):
            return None, "bad depth"
        if not (0 <= depth <= self.MAX_DEPTH):
            return None, "bad depth"
        gid = self._new_id()
        self.grants[gid] = {
            "id": gid, "issuer": issuer, "session": self.session,
            "subject": subject, "owner": owner, "operation": operation,
            "target": target,
            "content_hash": _mhash(content) if content is not None else None,
            "parent": None, "depth": depth,
        }
        return gid, None

    def attenuate(self, *, parent, target=None, content=None, depth=None):
        p = self.grants.get(parent)
        if p is None:
            return None, "unknown parent"
        if parent in self.revoked:
            return None, "parent revoked"
        if p["session"] != self.session:
            return None, "foreign session"
        if not self._chain_valid(p):
            return None, "parent chain invalid"
        if p["depth"] < 1:
            return None, "no delegation"
        if len(self._ancestors(p)) + 1 >= self.MAX_DEPTH:
            return None, "excessive depth"
        if target is not None and (not isinstance(target, str) or not target):
            return None, "bad target"
        if p["target"] is not None:
            if target is not None and target != p["target"]:
                return None, "target widening"
            eff_target = p["target"]
        else:
            eff_target = target
        if content is not None and not isinstance(content, dict):
            return None, "bad content"
        ph = p["content_hash"]
        if ph is not None:
            if content is not None and _mhash(content) != ph:
                return None, "content rebinding"
            eff_hash = ph
        else:
            eff_hash = _mhash(content) if content is not None else None
        if depth is None:
            eff_depth = p["depth"] - 1
        else:
            if (not isinstance(depth, int) or isinstance(depth, bool)
                    or not (0 <= depth < p["depth"])):
                return None, "depth not narrowed"
            eff_depth = depth
        gid = self._new_id()
        self.grants[gid] = {
            "id": gid, "issuer": p["issuer"], "session": self.session,
            "subject": p["subject"], "owner": p["owner"],
            "operation": p["operation"], "target": eff_target,
            "content_hash": eff_hash, "parent": parent, "depth": eff_depth,
        }
        return gid, None

    def revoke(self, gid):
        if gid in self.grants:
            self.revoked.add(gid)
            return True
        return False

    def reset(self):
        self.session = "oracle-session-2"
        self.grants.clear()
        self.revoked.clear()

    def _ancestors(self, rec):
        out, seen, cur = [], {rec["id"]}, rec["parent"]
        while cur:
            if cur in seen:
                break
            seen.add(cur)
            out.append(cur)
            parent = self.grants.get(cur)
            cur = parent["parent"] if parent else None
        return out

    def _chain_valid(self, rec, seen=None):
        seen = seen if seen is not None else set()
        gid = rec["id"]
        if gid in seen:
            return False
        seen.add(gid)
        if gid in self.revoked:
            return False
        if rec["session"] != self.session:
            return False
        parent = rec["parent"]
        if not parent:
            return True
        p = self.grants.get(parent)
        return p is not None and self._chain_valid(p, seen)

    def check(self, *, gid, subject, owner, operation, target,
              content_version):
        """content_version: hash string or None (unversioned call)."""
        r = self.grants.get(gid)
        if r is None:
            return False, "unissued"
        if gid in self.revoked:
            return False, "revoked"
        if r["session"] != self.session:
            return False, "foreign session"
        if not self._chain_valid(r):
            return False, "chain invalid"
        if not isinstance(subject, str) or not subject:
            return False, "unbound subject"
        if subject != r["subject"]:
            return False, "subject mismatch"
        if not isinstance(owner, str) or not owner:
            return False, "unbound owner"
        if owner != r["owner"]:
            return False, "owner mismatch"
        want = "nursery.confirm" if operation == "confirm" else operation
        if want != r["operation"]:
            return False, "operation mismatch"
        if r["target"] is not None and r["target"] != target:
            return False, "target mismatch"
        if (r["content_hash"] is not None
                and r["content_hash"] != content_version):
            return False, "content mismatch"
        return True, "allow"


# ---------------------------------------------------------------- drivers
# Each side exposes: issue/attenuate/revoke/reset/check with the same
# logical signature. Symbolic names ("g1") map to per-side handles.

class _ProdSide:
    def __init__(self):
        from form.dell_matrix.acceptance_policy import AcceptancePolicy
        self.p = AcceptancePolicy()
        self.owner = "oracle-owner"

    def issue(self, **kw):
        from form.dell_matrix.acceptance_policy import ApprovalError
        try:
            r = self.p.issue_grant(issuer=kw.get("issuer", "human:ace"),
                                   subject=kw["subject"], owner=self.owner,
                                   operation=kw.get("operation",
                                                    "nursery.confirm"),
                                   target=kw.get("target"),
                                   content=kw.get("content"),
                                   max_depth=kw.get("depth", 1))
            return r["grant_id"], None
        except ApprovalError as e:
            return None, str(e)

    def attenuate(self, **kw):
        from form.dell_matrix.acceptance_policy import ApprovalError
        try:
            r = self.p.attenuate_grant(
                parent_id=kw["parent"], target=kw.get("target"),
                content=kw.get("content"),
                max_depth=kw.get("depth", "absent")
                if kw.get("depth", "absent") != "absent" else None)
            return r["grant_id"], None
        except ApprovalError as e:
            return None, str(e)

    def revoke(self, gid):
        self.p.revoke_grant(gid)

    def reset(self):
        self.p.reset_session()

    def check(self, *, gid, subject, owner, operation, target,
              content_version):
        d = self.p.check("oracle", target or "p",
                         {"grant_id": gid} if gid else None,
                         proposal_version=content_version,
                         operation=operation, subject=subject, owner=owner)
        return bool(d.get("allowed")), d.get("detail", "")


class _ModelSide:
    def __init__(self):
        self.o = Oracle()
        self.owner = "oracle-owner"

    def issue(self, **kw):
        return self.o.issue(issuer=kw.get("issuer", "human:ace"),
                            subject=kw["subject"], owner=self.owner,
                            operation=kw.get("operation", "nursery.confirm"),
                            target=kw.get("target"),
                            content=kw.get("content"),
                            depth=kw.get("depth", 1))

    def attenuate(self, **kw):
        d = kw.get("depth", "absent")
        return self.o.attenuate(parent=kw["parent"], target=kw.get("target"),
                                content=kw.get("content"),
                                depth=None if d == "absent" else d)

    def revoke(self, gid):
        self.o.revoke(gid)

    def reset(self):
        self.o.reset()

    def check(self, *, gid, subject, owner, operation, target,
              content_version):
        ok, _ = self.o.check(gid=gid, subject=subject, owner=owner,
                             operation=operation, target=target,
                             content_version=content_version)
        return ok, ""


# ---------------------------------------------------------------- table
# Steps: ("issue", {kwargs}, "sym"), ("attenuate", {kwargs+parent sym}, "sym"),
#        ("revoke", "sym"), ("reset",),
#        ("check", {kwargs with gid sym}, expected_bool),
#        ("issue_reject", {kwargs}), ("attenuate_reject", {kwargs}).

C1 = {"label": "a", "words": "w"}
C2 = {"label": "b", "words": "changed"}

SCENARIOS = [
    {"name": "basic_issue_check",
     "steps": [
         ("issue", {"subject": "a", "target": "p1", "content": C1,
                    "depth": 0}, "g"),
         ("check", {"gid": "g", "subject": "a", "owner": "oracle-owner",
                    "operation": "confirm", "target": "p1",
                    "content": C1}, True),
     ]},
    {"name": "empty_content_binds",
     "steps": [
         ("issue", {"subject": "a", "content": {}, "depth": 0}, "g"),
         ("check", {"gid": "g", "subject": "a", "owner": "oracle-owner",
                    "operation": "confirm", "target": "p1",
                    "content": {}}, True),
         ("check", {"gid": "g", "subject": "a", "owner": "oracle-owner",
                    "operation": "confirm", "target": "p1",
                    "content": C1}, False),
     ]},
    {"name": "none_content_unconstrained",
     "steps": [
         ("issue", {"subject": "a", "target": "p1", "depth": 0}, "g"),
         ("check", {"gid": "g", "subject": "a", "owner": "oracle-owner",
                    "operation": "confirm", "target": "p1",
                    "content": C2}, True),
     ]},
    {"name": "multi_ancestor_chain",
     "steps": [
         ("issue", {"subject": "a", "depth": 3}, "g1"),
         ("attenuate", {"parent": "g1", "target": "p1"}, "g2"),
         ("attenuate", {"parent": "g2", "content": C1}, "g3"),
         ("check", {"gid": "g3", "subject": "a", "owner": "oracle-owner",
                    "operation": "confirm", "target": "p1",
                    "content": C1}, True),
         ("check", {"gid": "g3", "subject": "a", "owner": "oracle-owner",
                    "operation": "confirm", "target": "p2",
                    "content": C1}, False),
         ("check", {"gid": "g3", "subject": "a", "owner": "oracle-owner",
                    "operation": "confirm", "target": "p1",
                    "content": C2}, False),
     ]},
    {"name": "revoke_middle_ancestor",
     "steps": [
         ("issue", {"subject": "a", "depth": 3}, "g1"),
         ("attenuate", {"parent": "g1"}, "g2"),
         ("attenuate", {"parent": "g2"}, "g3"),
         ("revoke", "g2"),
         ("check", {"gid": "g3", "subject": "a", "owner": "oracle-owner",
                    "operation": "confirm", "target": "p1",
                    "content": C1}, False),
         ("check", {"gid": "g1", "subject": "a", "owner": "oracle-owner",
                    "operation": "confirm", "target": "p1",
                    "content": C1}, True),
     ]},
    {"name": "sibling_grants",
     "steps": [
         ("issue", {"subject": "a", "depth": 2}, "g1"),
         ("attenuate", {"parent": "g1", "target": "p1"}, "sib1"),
         ("attenuate", {"parent": "g1", "target": "p2"}, "sib2"),
         ("revoke", "sib1"),
         ("check", {"gid": "sib1", "subject": "a", "owner": "oracle-owner",
                    "operation": "confirm", "target": "p1",
                    "content": C1}, False),
         ("check", {"gid": "sib2", "subject": "a", "owner": "oracle-owner",
                    "operation": "confirm", "target": "p2",
                    "content": C1}, True),
     ]},
    {"name": "identity_substitution",
     "steps": [
         ("issue", {"subject": "a", "target": "p1", "depth": 0}, "g"),
         ("check", {"gid": "g", "subject": "b", "owner": "oracle-owner",
                    "operation": "confirm", "target": "p1",
                    "content": C1}, False),
         ("check", {"gid": "g", "subject": None, "owner": "oracle-owner",
                    "operation": "confirm", "target": "p1",
                    "content": C1}, False),
         ("check", {"gid": "g", "subject": "a", "owner": "other-owner",
                    "operation": "confirm", "target": "p1",
                    "content": C1}, False),
     ]},
    {"name": "session_reset",
     "steps": [
         ("issue", {"subject": "a", "depth": 0}, "g"),
         ("reset",),
         ("check", {"gid": "g", "subject": "a", "owner": "oracle-owner",
                    "operation": "confirm", "target": "p1",
                    "content": C1}, False),
     ]},
    {"name": "attenuation_rejections",
     "steps": [
         ("issue", {"subject": "a", "target": "p1", "content": C1,
                    "depth": 1}, "g"),
         ("attenuate_reject", {"parent": "g", "target": "p2"}),
         ("attenuate_reject", {"parent": "g", "content": C2}),
         ("attenuate_reject", {"parent": "g", "depth": 5}),
         ("issue_reject", {"subject": "a", "content": "bad"}),
         ("issue_reject", {"subject": "a", "operation": "confirm"}),
         ("issue_reject", {"subject": "", "depth": 0}),
     ]},
    {"name": "revoke_root_denies_descendants",
     "steps": [
         ("issue", {"subject": "a", "depth": 2}, "g1"),
         ("attenuate", {"parent": "g1"}, "g2"),
         ("attenuate", {"parent": "g2"}, "g3"),
         ("revoke", "g1"),
         ("check", {"gid": "g3", "subject": "a", "owner": "oracle-owner",
                    "operation": "confirm", "target": "p1",
                    "content": C1}, False),
         ("check", {"gid": "g2", "subject": "a", "owner": "oracle-owner",
                    "operation": "confirm", "target": "p1",
                    "content": C1}, False),
     ]},
    {"name": "forged_and_operation",
     "steps": [
         ("check", {"gid": "grant_forged", "subject": "a",
                    "owner": "oracle-owner", "operation": "confirm",
                    "target": "p1", "content": C1}, False),
         ("issue", {"subject": "a", "depth": 0}, "g"),
         ("check", {"gid": "g", "subject": "a", "owner": "oracle-owner",
                    "operation": "supersede", "target": "p1",
                    "content": C1}, False),
     ]},
]


def _hash_for(side, content):
    if content is None:
        return None
    if isinstance(side, _ModelSide):
        return _mhash(content)
    from form.dell_matrix.acceptance_policy import canonical_hash
    return canonical_hash(content)


def _run_side(sc, side):
    """Execute a scenario's steps on one side. Returns ordered outcomes."""
    syms = {}
    outcomes = []  # ("check", bool) | ("reject", bool)
    for step in sc["steps"]:
        kind = step[0]
        if kind == "issue":
            gid, err = side.issue(**step[1])
            assert err is None, f"{sc['name']} issue: {err}"
            syms[step[2]] = gid
        elif kind == "attenuate":
            kw = dict(step[1])
            kw["parent"] = syms[kw["parent"]]
            gid, err = side.attenuate(**kw)
            assert err is None, f"{sc['name']} attenuate: {err}"
            syms[step[2]] = gid
        elif kind == "revoke":
            side.revoke(syms[step[1]])
        elif kind == "reset":
            side.reset()
        elif kind == "issue_reject":
            gid, _ = side.issue(**step[1])
            outcomes.append(("reject", gid is None))
        elif kind == "attenuate_reject":
            kw = dict(step[1])
            kw["parent"] = syms[kw["parent"]]
            gid, _ = side.attenuate(**kw)
            outcomes.append(("reject", gid is None))
        elif kind == "check":
            kw = dict(step[1])
            expected = kw.pop("_expected", None)
            gid_sym = kw.pop("gid")
            kw["gid"] = syms.get(gid_sym, gid_sym)
            content = kw.pop("content", None)
            kw["content_version"] = _hash_for(side, content)
            ok, _ = side.check(**kw)
            outcomes.append(("check", ok, expected))
    return outcomes


def test_oracle_agreement():
    n_cases = 0
    for sc in SCENARIOS:
        # annotate expected outcomes
        steps = []
        for step in sc["steps"]:
            if step[0] == "check":
                kw = dict(step[1])
                kw["_expected"] = step[2]
                steps.append(("check", kw))
            else:
                steps.append(step)
        sc2 = {"name": sc["name"], "steps": steps}
        m_out = _run_side(sc2, _ModelSide())
        p_out = _run_side(sc2, _ProdSide())
        # 1. the table's expectations match the independent model
        #    (the table encodes the contract correctly)
        exp_ok = all(len(t) < 3 or t[2] is None or t[1] == t[2]
                     for t in m_out)
        check(f"oracle:{sc['name']}:table_matches_model", exp_ok,
              str(m_out))
        # 2. production agrees with the model on every outcome
        m_simple = [t[:2] for t in m_out]
        p_simple = [t[:2] for t in p_out]
        check(f"oracle:{sc['name']}:prod_agrees_model",
              m_simple == p_simple,
              f"model={m_simple} prod={p_simple}")
        n_cases += len(m_out)
    # exact coverage: every check/reject outcome in the table
    expect = sum(1 for sc in SCENARIOS for s in sc["steps"]
                 if s[0] in ("check", "issue_reject", "attenuate_reject"))
    check("oracle:total_cases", n_cases == expect,
          f"n={n_cases} expect={expect}")


def test_oracle_sensitivity():
    """Weaken production chain validation: oracle must DISAGREE."""
    from form.dell_matrix import acceptance_policy as ap_mod
    real = ap_mod.AcceptancePolicy._grant_chain_valid
    ap_mod.AcceptancePolicy._grant_chain_valid = lambda self, rec, _s=None: True
    try:
        scenarios = []
        for sc in SCENARIOS:
            if sc["name"] in ("revoke_middle_ancestor",
                              "revoke_root_denies_descendants"):
                scenarios.append({"name": sc["name"], "steps": sc["steps"]})
        diverged = 0
        for sc in scenarios:
            for side_name, side in (("model", _ModelSide()),
                                    ("prod", _ProdSide())):
                syms, results = {}, []
                for step in sc["steps"]:
                    kind = step[0]
                    if kind == "issue":
                        gid, _ = side.issue(**step[1])
                        syms[step[2]] = gid
                    elif kind == "attenuate":
                        kw = dict(step[1])
                        kw["parent"] = syms[kw["parent"]]
                        gid, _ = side.attenuate(**kw)
                        syms[step[2]] = gid
                    elif kind == "revoke":
                        side.revoke(syms[step[1]])
                    elif kind == "check":
                        kw = dict(step[1])
                        gid_sym = kw.pop("gid")
                        kw["gid"] = syms.get(gid_sym, gid_sym)
                        content = kw.pop("content", None)
                        kw["content_version"] = _hash_for(side, content)
                        ok, _ = side.check(**kw)
                        results.append(ok)
                sc.setdefault("_w", {})[side_name] = results
            mr, pr = sc["_w"]["model"], sc["_w"]["prod"]
            if mr != pr:
                diverged += 1
        check("oracle:sensitivity_diverges_when_weakened", diverged == 2,
              f"diverged={diverged}/2 scenarios")
    finally:
        ap_mod.AcceptancePolicy._grant_chain_valid = real
    # restored: agreement returns
    prod = _ProdSide()
    gid, _ = prod.issue(subject="a", depth=1)
    c2, _ = prod.attenuate(parent=gid)
    prod.revoke(gid)
    ok, _ = prod.check(gid=c2, subject="a", owner=prod.owner,
                       operation="confirm", target="p1",
                       content_version=None)
    check("oracle:restored_denies_revoked_chain", ok is False)


def smoke():
    test_oracle_agreement()
    test_oracle_sensitivity()
    n = sum(CHECKS)
    print(f"=== {n}/{len(CHECKS)} ===")
    return n == len(CHECKS)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
