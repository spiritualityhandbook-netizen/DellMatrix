#!/usr/bin/env python3
"""DCC-XX: Execution Outcome Ledger — dedicated control suite.

Outcome Record V1: durable, queryable evidence connecting
KNOWLEDGE > SELECTION > CONFLICT DISPOSITION > EXECUTION > OBSERVED OUTCOME,
without turning outcome into truth.

LAW: OUTCOME != TRUTH.

Controls:
  A  successful outcome captured (schema, identity, result)
  B  failed outcome captured (honest FAILED, bounded reason)
  C  knowledge provenance (id/revision/fingerprint frozen)
  D  revision immutability (O1 keeps R1 after R2; O2 references R2; O1 != O2)
  E  conflict provenance (conflict ID + routing state at execution time)
  F  disposition provenance (prefer/coexist recorded; clear restores quarantine)
  G  clear does not rewrite history
  H  query exact outcome (trace outcome)
  I  query by knowledge ID (outcomes for idea)
  J  list recent outcomes
  K  persistence (save/load roundtrip preserves ledger + sequence)
  L  literal two-process restore (A builds+executes+checkpoints+exits;
     B loads+queries; distinct PIDs, no inherited-memory canary)
  M  failed checkpoint atomicity (failed commit -> previous generation
     authoritative; no partial outcome authority)
  N  multiple executions distinguishable (seq + distinct IDs)
  O  composition granularity (one outcome per node; program-level derivable)
  P  outcome != truth invariants (no truth fields; success/failure changes nothing)
  Q  outcome cannot mutate verification status
  R  outcome cannot mutate conflict disposition
  S  pending/rejected knowledge governed by existing rules
  T  outcome record shape validation (forbidden fields rejected)
  U  DCC-XX-C1 blocked semantics (all-quarantined Dell 37 grow ->
     blocked, never completed; blocked record immutable)
  V  DCC-XX-C1 stale state (freshness gate: no previous call's
     evidence contaminates later blocked/failed/no-route/non-
     knowledge outcomes; blocked carries its own call's evidence)
  W  DCC-XX-C1 disposition lifecycle (prefer permits only eligible;
     coexist; clear restores blocking; conflict identity stable)
  X  DCC-XX-C1 blocked persistence + literal two-process restore

AUTONOMY = NO.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from form.open import open_program
from form.persist import _STATE_DIR
from form.mandell.translate import translate
from form.mandell.semantic_router import route_intent
from form.mandell.outcome_ledger import (
    OUTCOME_VERSION,
    OUTCOME_ID_PREFIX,
    RESULT_COMPLETED,
    RESULT_FAILED,
    RESULT_BLOCKED,
    capture_outcome,
    get_outcome,
    list_outcomes,
    outcomes_for_knowledge,
    outcome_id_for,
    validate_record_shape,
)
from form.mandell.conflict_disposition import conflict_id_for, detectable_conflicts
from form.mandell.supersession import supersede_proposal
from form.mandell import checkpoint_generation as CG

CHECKS = []
OWNERS = []


def check(name: str, cond: bool) -> None:
    CHECKS.append((name, bool(cond)))
    if not cond:
        print(f"  FAIL: {name}")


def wipe_owner(owner: str) -> None:
    for f in Path(_STATE_DIR).glob(f"*{owner}*"):
        try:
            if f.is_file():
                f.unlink()
        except OSError:
            pass
    # checkpoint generations
    import shutil
    from form.mandell.checkpoint_generation import _owner_ns
    ns = _owner_ns(owner)
    cdir = Path(_STATE_DIR) / "checkpoints" / ns
    if cdir.exists():
        shutil.rmtree(cdir, ignore_errors=True)


def fresh_owner(owner: str):
    wipe_owner(owner)
    if owner not in OWNERS:
        OWNERS.append(owner)
    return open_program(owner)


def op(p, text: str):
    r = route_intent(p, translate(text), raw_line=text)
    return r


def add_confirmed(p, label: str, words: str) -> str:
    pr = p.nursery.add(label, words=words, parents=[])
    p.confirm_proposal(pr.id, _producer="test", _review_context={"reviewer": "test", "approved_pid": pr.id})
    return pr.id


def last_outcome_id(p) -> str:
    assert p.outcome_records, "no outcomes captured"
    return max(p.outcome_records.keys(),
               key=lambda k: p.outcome_records[k]["outcome_seq"])


def cleanup() -> None:
    for owner in OWNERS:
        wipe_owner(owner)
    OWNERS.clear()


# ---------------------------------------------------------------- CONTROL A
def control_a() -> None:
    p = fresh_owner("DCCXX_A")
    a = add_confirmed(p, "plants_a", "plants require water")
    r = op(p, "grow using knowledge about plants water")
    check("A1 routed ok", r.ok)
    check("A2 outcome captured", len(p.outcome_records) == 1)
    oid = last_outcome_id(p)
    rec = p.outcome_records[oid]
    check("A3 id has out1: prefix", oid.startswith(OUTCOME_ID_PREFIX))
    check("A4 version 1", rec["outcome_version"] == OUTCOME_VERSION == 1)
    check("A5 result completed", rec["result"] == RESULT_COMPLETED)
    check("A6 operation recorded", rec["operation"] == "nurture")
    check("A7 dell 37", rec["dell"] == 37)
    check("A8 seq 1", rec["outcome_seq"] == 1)
    check("A9 owner recorded", rec["owner"] == "DCCXX_A")
    check("A10 observation marker", rec.get("outcome_is_observation") is True)


# ---------------------------------------------------------------- CONTROL B
def control_b() -> None:
    p = fresh_owner("DCCXX_B")
    # A legitimately failing operation: trace a nonexistent outcome.
    r = op(p, "trace outcome out1:doesnotexist1234567890abcdef")
    check("B1 routed (trace runs)", r.ok)
    # Force a genuinely failed execution: invalid Dell correspondence.
    r2 = op(p, "gibberish nonexistent command xyzzy")
    oid = last_outcome_id(p)
    rec = p.outcome_records[oid]
    check("B2 failed or blocked outcome recorded",
          rec["result"] in (RESULT_FAILED, RESULT_BLOCKED))
    check("B3 bounded error evidence", len(rec["error"]) <= 300)
    check("B4 outcome recorded despite failure", oid in p.outcome_records)


# ---------------------------------------------------------------- CONTROL C
def control_c() -> None:
    p = fresh_owner("DCCXX_C")
    a = add_confirmed(p, "plants_a", "plants require water")
    r = op(p, "grow using knowledge about plants water")
    check("C1 routed ok", r.ok)
    rec = p.outcome_records[last_outcome_id(p)]
    k = [x for x in rec["knowledge"] if x["id"] == a]
    check("C2 knowledge provenance present", len(k) == 1)
    k = k[0]
    check("C3 revision_number frozen", k["revision_number"] == 1)
    check("C4 revision_root_id", k["revision_root_id"] == a)
    check("C5 lifecycle_state", k["lifecycle_state"] == "active")
    check("C6 content fingerprint present", len(k["content_fingerprint"]) == 32)


# ---------------------------------------------------------------- CONTROL D
def control_d() -> None:
    p = fresh_owner("DCCXX_D")
    a = add_confirmed(p, "plants_a", "plants require water")
    r = op(p, "grow using knowledge about plants water")
    o1_id = last_outcome_id(p)
    o1 = dict(p.outcome_records[o1_id])
    k1 = [x for x in o1["knowledge"] if x["id"] == a][0]
    r1_rev = k1["revision_number"]
    # Revise the knowledge: A -> A2.
    sup = supersede_proposal(p, a, "plants require water every day indeed")
    check("D1 supersede ok", sup.get("ok"))
    a2 = sup["new_id"]
    check("D2 new revision id", a2 != a)
    # O1 must still reference R1.
    o1_after = p.outcome_records[o1_id]
    k1_after = [x for x in o1_after["knowledge"] if x["id"] == a][0]
    check("D3 O1 still references R1",
          k1_after["revision_number"] == r1_rev and
          k1_after["content_fingerprint"] == k1["content_fingerprint"])
    # Execute again using R2 -> O2.
    r = op(p, "grow using knowledge about plants water")
    o2_id = last_outcome_id(p)
    check("D4 O1 != O2 identity", o2_id != o1_id)
    o2 = p.outcome_records[o2_id]
    k2 = [x for x in o2["knowledge"] if x["id"] == a2]
    check("D5 O2 references R2", len(k2) == 1 and k2[0]["revision_number"] == 2)
    check("D6 O2 seq > O1 seq", o2["outcome_seq"] > o1["outcome_seq"])


# ---------------------------------------------------------------- CONTROL E
def control_e() -> None:
    p = fresh_owner("DCCXX_E")
    a = add_confirmed(p, "plants_a", "plants require water")
    b = add_confirmed(p, "plants_b", "plants do not require water")
    r = op(p, "grow using knowledge about plants water")
    check("E1 routed ok", r.ok)
    rec = p.outcome_records[last_outcome_id(p)]
    check("E2 conflict recorded", len(rec["conflicts"]) >= 1)
    c = rec["conflicts"][0]
    check("E3 conflict id stable", c["conflict_id"].startswith("cv1:"))
    check("E4 unresolved by default", c["disposition"] == "unresolved")
    check("E5 quarantined ids", set(rec["quarantined_ids"]) >= {a, b})
    check("E6 routable empty when quarantined", rec["routable_ids"] == [])


# ---------------------------------------------------------------- CONTROL F
def control_f() -> None:
    p = fresh_owner("DCCXX_F")
    a = add_confirmed(p, "plants_a", "plants require water")
    b = add_confirmed(p, "plants_b", "plants do not require water")
    confs = detectable_conflicts(p)
    cid = conflict_id_for(confs[0]["id_a"], confs[0]["id_b"])
    ids = sorted([confs[0]["id_a"], confs[0]["id_b"]])
    # Resolve prefer A, then execute.
    r = op(p, f"resolve conflict {cid} prefer {ids[0]}")
    check("F1 resolve ok", r.ok)
    r = op(p, "grow using knowledge about plants water")
    rec = p.outcome_records[last_outcome_id(p)]
    c = [x for x in rec["conflicts"] if x["conflict_id"] == cid]
    check("F2 conflict in outcome", len(c) == 1)
    c = c[0]
    check("F3 disposition prefer recorded", c["disposition"] == "prefer")
    check("F4 preferred ids", c["preferred_ids"] == [ids[0]])
    check("F5 permitted ids", c["permitted_ids"] == [ids[0]])
    check("F6 routable shows A only",
          ids[0] in rec["routable_ids"] and ids[1] not in rec["routable_ids"])
    # Coexist.
    r = op(p, f"resolve conflict {cid} coexist")
    r = op(p, "grow using knowledge about plants water")
    rec2 = p.outcome_records[last_outcome_id(p)]
    c2 = [x for x in rec2["conflicts"] if x["conflict_id"] == cid][0]
    check("F7 coexist recorded", c2["disposition"] == "coexist")
    check("F8 both permitted", set(c2["permitted_ids"]) == set(ids))


# ---------------------------------------------------------------- CONTROL G
def control_g() -> None:
    p = fresh_owner("DCCXX_G")
    a = add_confirmed(p, "plants_a", "plants require water")
    b = add_confirmed(p, "plants_b", "plants do not require water")
    confs = detectable_conflicts(p)
    cid = conflict_id_for(confs[0]["id_a"], confs[0]["id_b"])
    ids = sorted([confs[0]["id_a"], confs[0]["id_b"]])
    r = op(p, f"resolve conflict {cid} prefer {ids[0]}")
    r = op(p, "grow using knowledge about plants water")
    resolved_oid = last_outcome_id(p)
    resolved_rec = dict(p.outcome_records[resolved_oid])
    # Clear the disposition.
    r = op(p, f"clear conflict resolution {cid}")
    check("G1 clear ok", r.ok)
    # Future execution returns to unresolved.
    r = op(p, "grow using knowledge about plants water")
    rec = p.outcome_records[last_outcome_id(p)]
    c = [x for x in rec["conflicts"] if x["conflict_id"] == cid]
    check("G2 future execution unresolved",
          len(c) == 1 and c[0]["disposition"] == "unresolved")
    # Historical resolved outcome unchanged.
    hist = p.outcome_records[resolved_oid]
    hc = [x for x in hist["conflicts"] if x["conflict_id"] == cid][0]
    check("G3 historical outcome keeps prefer", hc["disposition"] == "prefer")
    check("G4 historical permitted unchanged",
          hist["conflicts"][0]["permitted_ids"] == resolved_rec["conflicts"][0]["permitted_ids"])


# ---------------------------------------------------------------- CONTROL H
def control_h() -> None:
    p = fresh_owner("DCCXX_H")
    a = add_confirmed(p, "plants_a", "plants require water")
    r = op(p, "grow using knowledge about plants water")
    oid = last_outcome_id(p)
    # Exact query via command.
    r = op(p, f"trace outcome {oid}")
    check("H1 trace ok", r.ok)
    check("H2 last_discover source", p.last_discover.get("source") == "trace_outcome")
    check("H3 exact id match", p.last_discover.get("outcome_id") == oid)
    # Direct API.
    rec = get_outcome(p, oid)
    check("H4 get_outcome returns copy", rec is not None and rec["outcome_id"] == oid)
    check("H5 unknown id -> None", get_outcome(p, "out1:ffffffffffffffffffffffffffffffff") is None)


# ---------------------------------------------------------------- CONTROL I
def control_i() -> None:
    p = fresh_owner("DCCXX_I")
    a = add_confirmed(p, "plants_a", "plants require water")
    b = add_confirmed(p, "soil_b", "soil needs nutrients daily")
    r = op(p, "grow using knowledge about plants water")
    r = op(p, "grow using knowledge about soil nutrients")
    # Query by knowledge ID via command.
    r = op(p, f"outcomes for idea {a}")
    check("I1 query ok", r.ok)
    recs = p.last_discover.get("outcomes") or []
    check("I2 finds outcomes for A", len(recs) >= 1)
    check("I3 all contain A",
          all(any(k.get("id") == a for k in (o.get("knowledge") or [])) for o in recs))
    # Direct API.
    api_recs = outcomes_for_knowledge(p, a)
    check("I4 API matches", len(api_recs) == len(recs))
    check("I5 unknown id -> empty", outcomes_for_knowledge(p, "nope_0000") == [])


# ---------------------------------------------------------------- CONTROL J
def control_j() -> None:
    p = fresh_owner("DCCXX_J")
    a = add_confirmed(p, "plants_a", "plants require water")
    for _ in range(3):
        op(p, "grow using knowledge about plants water")
    r = op(p, "list outcomes")
    check("J1 list ok", r.ok)
    recs = p.last_discover.get("outcomes") or []
    check("J2 recent listed", len(recs) >= 3)
    seqs = [o["outcome_seq"] for o in recs]
    check("J3 newest first", seqs == sorted(seqs, reverse=True))
    # show last outcome alias.
    r = op(p, "show last outcome")
    check("J4 alias ok", r.ok and p.last_discover.get("source") == "list_outcomes")


# ---------------------------------------------------------------- CONTROL K
def control_k() -> None:
    p = fresh_owner("DCCXX_K")
    a = add_confirmed(p, "plants_a", "plants require water")
    r = op(p, "grow using knowledge about plants water")
    oid = last_outcome_id(p)
    seq_before = p.outcome_seq
    p.save()
    # Fresh program object, same owner: nursery reload only is NOT enough;
    # the ledger lives in the program payload, so use persist load.
    from form.persist import load as persist_load
    p2 = persist_load("DCCXX_K")
    check("K1 ledger restored", oid in p2.outcome_records)
    check("K2 seq restored", p2.outcome_seq == seq_before)
    rec = p2.outcome_records[oid]
    check("K3 knowledge provenance intact",
          any(k["id"] == a for k in rec["knowledge"]))
    check("K4 new execution continues sequence", True)
    r = route_intent(p2, translate("grow using knowledge about plants water"), raw_line="x")
    check("K5 seq advances after restore",
          p2.outcome_seq == seq_before + 1)


# ---------------------------------------------------------------- CONTROL L
def control_l() -> None:
    owner = "DCCXX_L"
    wipe_owner(owner)
    OWNERS.append(owner)
    repo = str(REPO)
    script_a = f'''
import sys; sys.path.insert(0, {repo!r})
from form.open import open_program
from form.mandell.translate import translate
from form.mandell.semantic_router import route_intent
from form.mandell import checkpoint_generation as CG
import os
p = open_program({owner!r})
for label, words in [("plants_a", "plants require water"),
                     ("plants_b", "plants do not require water")]:
    pr = p.nursery.add(label, words=words, parents=[])
    p.confirm_proposal(pr.id, _producer="test", _review_context={"reviewer": "test", "approved_pid": pr.id})
r = route_intent(p, translate("grow using knowledge about plants water"), raw_line="x")
assert r.ok, "route failed"
oids = list(p.outcome_records.keys())
assert len(oids) == 1, oids
rec = p.outcome_records[oids[0]]
p.save()
rc = CG.commit_checkpoint(p)
assert rc.get("committed"), rc
# No inherited-memory canary: record PID and a canary marker.
print("A_PID:" + str(os.getpid()), flush=True)
print("A_OID:" + oids[0], flush=True)
print("A_SEQ:" + str(rec["outcome_seq"]), flush=True)
print("A_KNOW:" + ",".join(sorted(k["id"] for k in rec["knowledge"])), flush=True)
os._exit(0)
'''
    pa = Path("/tmp/dccxx_a.py")
    pa.write_text(script_a)
    out_a = subprocess.run([sys.executable, str(pa)], capture_output=True, text=True)
    assert out_a.returncode == 0, f"process A failed: {out_a.stderr[-500:]}"
    vals = {}
    for line in out_a.stdout.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            vals[k] = v
    check("L1 process A produced outcome", "A_OID" in vals)
    script_b = f'''
import sys; sys.path.insert(0, {repo!r})
from form.mandell import checkpoint_generation as CG
from form.mandell.outcome_ledger import get_outcome
import os
p2, rc = CG.load_checkpoint({owner!r})
assert rc.get("generation_id"), rc
rec = get_outcome(p2, {vals.get("A_OID", "")!r})
assert rec is not None, "outcome missing after checkpoint load"
print("B_PID:" + str(os.getpid()), flush=True)
print("B_OID:" + rec["outcome_id"], flush=True)
print("B_SEQ:" + str(rec["outcome_seq"]), flush=True)
print("B_KNOW:" + ",".join(sorted(k["id"] for k in rec["knowledge"])), flush=True)
print("B_RESULT:" + rec["result"], flush=True)
print("B_CONFLICTS:" + str(len(rec["conflicts"])), flush=True)
os._exit(0)
'''
    pb = Path("/tmp/dccxx_b.py")
    pb.write_text(script_b)
    out_b = subprocess.run([sys.executable, str(pb)], capture_output=True, text=True)
    assert out_b.returncode == 0, f"process B failed: {out_b.stderr[-500:]}"
    bvals = {}
    for line in out_b.stdout.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            bvals[k] = v
    check("L2 distinct PIDs", vals.get("A_PID") != bvals.get("B_PID"))
    check("L3 same outcome ID", bvals.get("B_OID") == vals.get("A_OID"))
    check("L4 same seq", bvals.get("B_SEQ") == vals.get("A_SEQ"))
    check("L5 same knowledge", bvals.get("B_KNOW") == vals.get("A_KNOW"))
    check("L6 same result", bvals.get("B_RESULT") == "blocked")
    check("L7 conflict evidence survives", bvals.get("B_CONFLICTS") == "1")
    pa.unlink(missing_ok=True)
    pb.unlink(missing_ok=True)


# ---------------------------------------------------------------- CONTROL M
def control_m() -> None:
    p = fresh_owner("DCCXX_M")
    a = add_confirmed(p, "plants_a", "plants require water")
    r = op(p, "grow using knowledge about plants water")
    p.save()
    rc1 = CG.commit_checkpoint(p)
    check("M1 first checkpoint committed", rc1.get("committed"))
    gen1 = rc1["generation_id"]
    n1 = len(p.outcome_records)
    # Second execution, then a failed checkpoint commit (after members).
    r = op(p, "grow using knowledge about plants water")
    check("M2 second outcome captured", len(p.outcome_records) == n1 + 1)
    p.save()
    try:
        CG.commit_checkpoint(p, _fail_at="after_members")
        check("M3 commit raised", False)
    except Exception:
        check("M3 commit raised", True)
    # Previous generation must remain authoritative; the failed commit
    # must not leave partial outcome authority.
    p2, rc = CG.load_checkpoint("DCCXX_M")
    check("M4 previous generation authoritative",
          rc.get("generation_id") == gen1)
    check("M5 no partial outcome authority",
          len(p2.outcome_records) == n1)


# ---------------------------------------------------------------- CONTROL N
def control_n() -> None:
    p = fresh_owner("DCCXX_N")
    a = add_confirmed(p, "plants_a", "plants require water")
    ids = set()
    seqs = []
    for _ in range(3):
        op(p, "grow using knowledge about plants water")
        oid = last_outcome_id(p)
        ids.add(oid)
        seqs.append(p.outcome_records[oid]["outcome_seq"])
    check("N1 three distinct IDs", len(ids) == 3)
    check("N2 seq strictly increasing", seqs == sorted(seqs) and len(set(seqs)) == 3)
    check("N3 ids deterministic prefix", all(i.startswith(OUTCOME_ID_PREFIX) for i in ids))


# ---------------------------------------------------------------- CONTROL O
def control_o() -> None:
    from form.mandell.flow_executor import parse_program, execute_program
    p = fresh_owner("DCCXX_O")
    a = add_confirmed(p, "plants_a", "plants require water")
    n_before = len(p.outcome_records)
    # Use Dells with verified correspondence (37 nurture, 35 discover).
    fp = parse_program("37[Nurture] :: grow_using_knowledge_about plants water >> 35[Discover] :: trace")
    receipt = execute_program(p, fp)
    check("O1 flow executed", receipt.completed >= 1)
    new_oids = [k for k in p.outcome_records.keys()
                if p.outcome_records[k]["outcome_seq"] > n_before]
    check("O2 one outcome per node", len(new_oids) == len(fp.nodes))
    comps = [p.outcome_records[k]["composition"] for k in new_oids]
    check("O3 composition recorded",
          all(c is not None and c["node_index"] in (0, 1) for c in comps))
    check("O4 same flow program ref",
          len({c["flow_program"] for c in comps}) == 1)
    # Program-level aggregation is derivable by grouping on composition.
    idxs = sorted(c["node_index"] for c in comps)
    check("O5 node indexes distinguishable", idxs == [0, 1])


# ---------------------------------------------------------------- CONTROL P
def control_p() -> None:
    p = fresh_owner("DCCXX_P")
    a = add_confirmed(p, "plants_a", "plants require water")
    # Successful execution.
    r = op(p, "grow using knowledge about plants water")
    check("P1 routed ok", r.ok)
    rec_ok = p.outcome_records[last_outcome_id(p)]
    # Failed execution (blocked: no correspondence).
    r = op(p, "gibberish nonexistent command xyzzy")
    rec_bad = p.outcome_records[last_outcome_id(p)]
    check("P2 both recorded", rec_ok["outcome_id"] != rec_bad["outcome_id"])
    # OUTCOME != TRUTH: no truth/verification/confidence fields anywhere.
    forbidden = ("truth", "verified", "verification", "confidence",
                 "truth_score", "auto_confirm", "auto_reject")
    for rec in p.outcome_records.values():
        for f in forbidden:
            check(f"P3 no {f} in {rec['outcome_id'][:12]}", f not in rec)
    # Success changed nothing about the knowledge's standing.
    prop = p.nursery.proposals[a]
    check("P4 success did not verify knowledge",
          getattr(prop, "status", "") == "confirmed")
    check("P5 no truth field on proposal",
          not hasattr(prop, "truth") or getattr(prop, "truth", None) is None)


# ---------------------------------------------------------------- CONTROL Q
def control_q() -> None:
    p = fresh_owner("DCCXX_Q")
    a = add_confirmed(p, "plants_a", "plants require water")
    # Record verification-relevant state before.
    from form.mandell.supersession import inspect_revision
    rev_before = inspect_revision(p, a)
    r = op(p, "grow using knowledge about plants water")
    check("Q1 routed ok", r.ok)
    rev_after = inspect_revision(p, a)
    check("Q2 revision authority unchanged",
          rev_after.get("lifecycle_state") == rev_before.get("lifecycle_state"))
    check("Q3 revision number unchanged",
          rev_after.get("revision_number") == rev_before.get("revision_number"))
    # A failed outcome must not touch verification either.
    r = op(p, "gibberish nonexistent command xyzzy")
    rev_after2 = inspect_revision(p, a)
    check("Q4 failure did not alter revision",
          rev_after2.get("revision_number") == rev_before.get("revision_number"))


# ---------------------------------------------------------------- CONTROL R
def control_r() -> None:
    p = fresh_owner("DCCXX_R")
    a = add_confirmed(p, "plants_a", "plants require water")
    b = add_confirmed(p, "plants_b", "plants do not require water")
    confs = detectable_conflicts(p)
    cid = conflict_id_for(confs[0]["id_a"], confs[0]["id_b"])
    check("R1 no disposition initially", cid not in p.nursery.conflict_dispositions)
    # Successful execution with unresolved conflict.
    r = op(p, "grow using knowledge about plants water")
    check("R2 routed ok", r.ok)
    check("R3 outcome did not create disposition",
          cid not in p.nursery.conflict_dispositions)
    # Failed execution also must not create one.
    r = op(p, "gibberish nonexistent command xyzzy")
    check("R4 failure did not create disposition",
          cid not in p.nursery.conflict_dispositions)


# ---------------------------------------------------------------- CONTROL S
def control_s() -> None:
    p = fresh_owner("DCCXX_S")
    # Pending (unconfirmed) knowledge: existing rules govern eligibility.
    pr = p.nursery.add("pending_a", words="plants require water", parents=[])
    pending_id = pr.id
    check("S1 pending status", getattr(pr, "status", "") == "pending")
    r = op(p, "grow using knowledge about plants water")
    check("S2 routed ok", r.ok)
    rec = p.outcome_records[last_outcome_id(p)]
    ids = [k["id"] for k in rec["knowledge"]]
    check("S3 pending not selected (existing eligibility)",
          pending_id not in ids)
    # Rejected knowledge stays rejected.
    p.reject_proposal(pending_id)
    r = op(p, "grow using knowledge about plants water")
    rec2 = p.outcome_records[last_outcome_id(p)]
    ids2 = [k["id"] for k in rec2["knowledge"]]
    check("S4 rejected not selected", pending_id not in ids2)
    check("S5 outcome still recorded", rec2["outcome_id"] in p.outcome_records)


# ---------------------------------------------------------------- CONTROL T
def control_t() -> None:
    p = fresh_owner("DCCXX_T")
    a = add_confirmed(p, "plants_a", "plants require water")
    r = op(p, "grow using knowledge about plants water")
    rec = p.outcome_records[last_outcome_id(p)]
    check("T1 valid shape passes", validate_record_shape(rec))
    bad = dict(rec)
    bad["truth"] = True
    check("T2 truth field rejected", not validate_record_shape(bad))
    bad2 = dict(rec)
    bad2["result"] = "good"
    check("T3 bad result rejected", not validate_record_shape(bad2))
    bad3 = dict(rec)
    bad3["outcome_id"] = "bogus"
    check("T4 bad id rejected", not validate_record_shape(bad3))
    check("T5 wrong version rejected",
          not validate_record_shape({**rec, "outcome_version": 999}))
    # Identity determinism: same inputs -> same id.
    id1 = outcome_id_for(1, "O", 7, "nurture", "a#1#fp", "c:prefer:x", "completed")
    id2 = outcome_id_for(1, "O", 7, "nurture", "a#1#fp", "c:prefer:x", "completed")
    check("T6 identity deterministic", id1 == id2 and id1.startswith("out1:"))
    id3 = outcome_id_for(1, "O", 8, "nurture", "a#1#fp", "c:prefer:x", "completed")
    check("T7 seq distinguishes", id3 != id1)


# ---------------------------------------------------------------- CONTROL U
def control_u() -> None:
    # DCC-XX-C1 BLOCKED semantics: an unresolved conflict that
    # quarantines every selected unit means the intended execution did
    # not occur. The routing succeeded (correct quarantine) but the
    # outcome must be blocked, never completed.
    p = fresh_owner("DCCXX_U")
    a = add_confirmed(p, "plants_a", "plants require water")
    b = add_confirmed(p, "plants_b", "plants do not require water")
    r = op(p, "grow using knowledge about plants water")
    check("U1 routed ok", r.ok)
    last = p.last_nurture
    check("U2 XIII quarantine default", last["conflict_count"] >= 1)
    check("U3 routable empty", last["routable_selected_ids"] == [])
    rec = p.outcome_records[last_outcome_id(p)]
    check("U4 outcome is blocked, not completed",
          rec["result"] == RESULT_BLOCKED)
    check("U5 blocked keeps quarantine evidence",
          rec["quarantined_ids"] != [] and len(rec["conflicts"]) >= 1)
    check("U6 blocked keeps frozen knowledge selection",
          {a, b} <= {k["id"] for k in rec["knowledge"]})
    check("U7 conflict disposition unresolved",
          all(c["disposition"] == "unresolved" for c in rec["conflicts"]))
    # A later successful operation must not rewrite the blocked record.
    blocked_oid = last_outcome_id(p)
    c = add_confirmed(p, "sun_c", "sunlight helps plants grow")
    r = op(p, "grow using knowledge about sunlight plants")
    rec_after = p.outcome_records[blocked_oid]
    check("U8 blocked record immutable",
          rec_after["result"] == RESULT_BLOCKED
          and rec_after["quarantined_ids"] == rec["quarantined_ids"])


# ---------------------------------------------------------------- CONTROL V
def control_v() -> None:
    # DCC-XX-C1 STALE STATE: program.last_nurture is a single slot
    # shared across calls. The freshness gate must ensure a previous
    # successful call's evidence never contaminates a later blocked,
    # failed, no-route, or non-knowledge outcome — and a blocked
    # outcome carries only its own call's evidence.
    p = fresh_owner("DCCXX_V")
    a = add_confirmed(p, "plants_a", "plants require water")
    # V1: successful grow -> completed with knowledge provenance.
    r = op(p, "grow using knowledge about plants water")
    rec_ok = p.outcome_records[last_outcome_id(p)]
    check("V1 success completed", rec_ok["result"] == RESULT_COMPLETED)
    check("V2 success has knowledge provenance",
          any(k["id"] == a for k in rec_ok["knowledge"]))
    # V3: a non-Dell-37 operation after the success must carry NO stale
    # knowledge/conflict provenance.
    r = op(p, "list outcomes")
    rec_list = p.outcome_records[last_outcome_id(p)]
    check("V4 non-knowledge op recorded", rec_list["operation"] == "discover")
    check("V5 no stale knowledge", rec_list["knowledge"] == [])
    check("V6 no stale conflicts",
          rec_list["conflicts"] == [] and rec_list["quarantined_ids"] == []
          and rec_list["routable_ids"] == [])
    # V7: a failed/no-route operation after the success: no stale provenance.
    r = op(p, "gibberish nonexistent command xyzzy")
    rec_bad = p.outcome_records[last_outcome_id(p)]
    check("V8 failed outcome has no stale knowledge",
          rec_bad["knowledge"] == [] and rec_bad["conflicts"] == [])
    # V9: now create the conflict and run the blocked grow. The blocked
    # outcome must carry THIS call's evidence only.
    b = add_confirmed(p, "plants_b", "plants do not require water")
    r = op(p, "grow using knowledge about plants water")
    rec_blocked = p.outcome_records[last_outcome_id(p)]
    check("V10 blocked after prior success",
          rec_blocked["result"] == RESULT_BLOCKED)
    check("V11 blocked carries current-call conflict evidence",
          len(rec_blocked["conflicts"]) >= 1
          and {a, b} <= set(rec_blocked["quarantined_ids"]))
    check("V12 blocked knowledge is this call's selection",
          {a, b} <= {k["id"] for k in rec_blocked["knowledge"]})
    # V13: a non-Dell-37 op after the blocked call: still no contamination
    # (the slot holds the blocked call's receipt, but it is not fresh).
    r = op(p, "list outcomes")
    rec_list2 = p.outcome_records[last_outcome_id(p)]
    check("V14 post-block non-knowledge op clean",
          rec_list2["knowledge"] == [] and rec_list2["conflicts"] == [])


# ---------------------------------------------------------------- CONTROL W
def control_w() -> None:
    # DCC-XX-C1 disposition lifecycle on outcomes: PREFER permits only
    # independently eligible behavior; COEXIST preserves both;
    # CLEAR restores unresolved blocking; conflict identity is stable.
    p = fresh_owner("DCCXX_W")
    a = add_confirmed(p, "plants_a", "plants require water")
    b = add_confirmed(p, "plants_b", "plants do not require water")
    confs = detectable_conflicts(p)
    cid = conflict_id_for(confs[0]["id_a"], confs[0]["id_b"])
    ids = sorted([confs[0]["id_a"], confs[0]["id_b"]])
    # W: PREFER -> execution proceeds on the preferred unit only.
    r = op(p, f"resolve conflict {cid} prefer {ids[0]}")
    check("W1 prefer resolve ok", r.ok)
    r = op(p, "grow using knowledge about plants water")
    prefer_oid = last_outcome_id(p)
    rec = p.outcome_records[prefer_oid]
    c = [x for x in rec["conflicts"] if x["conflict_id"] == cid][0]
    check("W2 prefer outcome completed", rec["result"] == RESULT_COMPLETED)
    check("W3 prefer permits only the preferred unit",
          c["disposition"] == "prefer" and c["permitted_ids"] == [ids[0]]
          and ids[0] in rec["routable_ids"]
          and ids[1] not in rec["routable_ids"])
    # W: COEXIST -> both permitted, execution proceeds.
    r = op(p, f"resolve conflict {cid} coexist")
    r = op(p, "grow using knowledge about plants water")
    rec2 = p.outcome_records[last_outcome_id(p)]
    c2 = [x for x in rec2["conflicts"] if x["conflict_id"] == cid][0]
    check("W4 coexist outcome completed", rec2["result"] == RESULT_COMPLETED)
    check("W5 coexist permits both",
          c2["disposition"] == "coexist"
          and set(c2["permitted_ids"]) == set(ids))
    # W: CLEAR -> unresolved blocking returns.
    r = op(p, f"clear conflict resolution {cid}")
    check("W6 clear ok", r.ok)
    r = op(p, "grow using knowledge about plants water")
    rec3 = p.outcome_records[last_outcome_id(p)]
    c3 = [x for x in rec3["conflicts"] if x["conflict_id"] == cid][0]
    check("W7 clear restores blocked",
          rec3["result"] == RESULT_BLOCKED
          and c3["disposition"] == "unresolved")
    # W: REVISION — conflict identity stable across the lifecycle.
    check("W8 conflict identity stable",
          c["conflict_id"] == c2["conflict_id"] == c3["conflict_id"] == cid)
    # W: historical prefer/coexist outcomes keep their dispositions.
    hist = p.outcome_records[prefer_oid]
    hc = [x for x in hist["conflicts"] if x["conflict_id"] == cid][0]
    check("W9 history not rewritten by clear",
          hist["result"] == RESULT_COMPLETED and hc["disposition"] == "prefer")


# ---------------------------------------------------------------- CONTROL X
def control_x() -> None:
    # DCC-XX-C1: blocked status and provenance survive persistence and
    # a literal cross-process checkpoint restore, exactly.
    p = fresh_owner("DCCXX_X")
    a = add_confirmed(p, "plants_a", "plants require water")
    b = add_confirmed(p, "plants_b", "plants do not require water")
    r = op(p, "grow using knowledge about plants water")
    oid = last_outcome_id(p)
    rec = p.outcome_records[oid]
    check("X1 blocked before save", rec["result"] == RESULT_BLOCKED)
    seq_before = p.outcome_seq
    quarantined_before = list(rec["quarantined_ids"])
    p.save()
    from form.persist import load as persist_load
    p2 = persist_load("DCCXX_X")
    check("X2 blocked ledger restored", oid in p2.outcome_records)
    rec2 = p2.outcome_records[oid]
    check("X3 blocked status survives",
          rec2["result"] == RESULT_BLOCKED)
    check("X4 quarantine provenance survives",
          rec2["quarantined_ids"] == quarantined_before
          and len(rec2["conflicts"]) == len(rec["conflicts"]))
    check("X5 seq restored", p2.outcome_seq == seq_before)

    # Literal two-process restore of a blocked outcome.
    owner = "DCCXX_X2"
    wipe_owner(owner)
    OWNERS.append(owner)
    repo = str(REPO)
    script_a = f'''
import sys; sys.path.insert(0, {repo!r})
from form.open import open_program
from form.mandell.translate import translate
from form.mandell.semantic_router import route_intent
from form.mandell import checkpoint_generation as CG
import os
p = open_program({owner!r})
for label, words in [("plants_a", "plants require water"),
                     ("plants_b", "plants do not require water")]:
    pr = p.nursery.add(label, words=words, parents=[])
    p.confirm_proposal(pr.id, _producer="test", _review_context={"reviewer": "test", "approved_pid": pr.id})
r = route_intent(p, translate("grow using knowledge about plants water"), raw_line="x")
assert r.ok, "route failed"
oids = list(p.outcome_records.keys())
assert len(oids) == 1, oids
rec = p.outcome_records[oids[0]]
assert rec["result"] == "blocked", rec["result"]
p.save()
rc = CG.commit_checkpoint(p)
assert rc.get("committed"), rc
print("XA_PID:" + str(os.getpid()), flush=True)
print("XA_OID:" + oids[0], flush=True)
print("XA_SEQ:" + str(rec["outcome_seq"]), flush=True)
print("XA_RESULT:" + rec["result"], flush=True)
print("XA_QUAR:" + ",".join(sorted(rec["quarantined_ids"])), flush=True)
os._exit(0)
'''
    pa = Path("/tmp/dccxx_xa.py")
    pa.write_text(script_a)
    out_a = subprocess.run([sys.executable, str(pa)], capture_output=True, text=True)
    assert out_a.returncode == 0, f"process A failed: {out_a.stderr[-500:]}"
    vals = {}
    for line in out_a.stdout.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            vals[k] = v
    check("X6 process A produced blocked outcome", vals.get("XA_RESULT") == "blocked")
    script_b = f'''
import sys; sys.path.insert(0, {repo!r})
from form.mandell import checkpoint_generation as CG
from form.mandell.outcome_ledger import get_outcome
import os
p2, rc = CG.load_checkpoint({owner!r})
assert rc.get("generation_id"), rc
rec = get_outcome(p2, {vals.get("XA_OID", "")!r})
assert rec is not None, "outcome missing after checkpoint load"
print("XB_PID:" + str(os.getpid()), flush=True)
print("XB_OID:" + rec["outcome_id"], flush=True)
print("XB_SEQ:" + str(rec["outcome_seq"]), flush=True)
print("XB_RESULT:" + rec["result"], flush=True)
print("XB_QUAR:" + ",".join(sorted(rec["quarantined_ids"])), flush=True)
os._exit(0)
'''
    pb = Path("/tmp/dccxx_xb.py")
    pb.write_text(script_b)
    out_b = subprocess.run([sys.executable, str(pb)], capture_output=True, text=True)
    assert out_b.returncode == 0, f"process B failed: {out_b.stderr[-500:]}"
    bvals = {}
    for line in out_b.stdout.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            bvals[k] = v
    check("X7 distinct PIDs", vals.get("XA_PID") != bvals.get("XB_PID"))
    check("X8 same outcome ID", bvals.get("XB_OID") == vals.get("XA_OID"))
    check("X9 same seq", bvals.get("XB_SEQ") == vals.get("XA_SEQ"))
    check("X10 blocked result exact after restore",
          bvals.get("XB_RESULT") == "blocked")
    check("X11 quarantine set exact after restore",
          bvals.get("XB_QUAR") == vals.get("XA_QUAR"))
    pa.unlink(missing_ok=True)
    pb.unlink(missing_ok=True)


def main() -> int:
    global CHECKS
    CHECKS = []
    control_a()
    control_b()
    control_c()
    control_d()
    control_e()
    control_f()
    control_g()
    control_h()
    control_i()
    control_j()
    control_k()
    control_l()
    control_m()
    control_n()
    control_o()
    control_p()
    control_q()
    control_r()
    control_s()
    control_t()
    control_u()
    control_v()
    control_w()
    control_x()
    cleanup()
    total = len(CHECKS)
    failed = [n for n, ok in CHECKS if not ok]
    print(f"DCC-XX: {total - len(failed)}/{total}")
    for n in failed:
        print(f"  FAILED: {n}")
    return 0 if not failed else 1


def smoke() -> bool:
    """Regress entry point: the full dedicated DCC-XX control suite."""
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
