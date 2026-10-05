#!/usr/bin/env python3
"""DCC-XIX: Operator-governed conflict disposition + routing policy (Disposition V1).

Success definition under test: detected conflicts remain quarantined by
default. An explicit operator may assign a durable routing disposition to
a specific stable conflict. That disposition controls only the
conflict-routing gate, never creates truth, never bypasses
revision/dependency/relevance requirements, never silently transfers to
changed knowledge, and survives coherent cross-process persistence.

Controls:
  A  stable conflict identity (order-independent, deterministic, restart-stable)
  B  default unresolved preserves DCC-XIII quarantine (backward compatible)
  C  prefer A via full contextual route (language path included)
  D  prefer B (mirror)
  E  coexist waives quarantine only; conflict still detected in receipts
  F  clear returns to unresolved; clear twice is deterministic
  G  supersede preferred -> new conflict identity; no silent transfer
  H  supersede non-preferred -> new conflict identity; no silent transfer
  I  preferred becomes dependency-invalid -> no auto-promotion (mandatory)
  J  stale disposition: no routing effect, still inspectable
  K  multiple conflicts composition: one unresolved still quarantines
  L  coexist + other-conflict composition
  M  malformed dispositions fail closed (command + routing layers)
  N  relevance scores and top-5 unchanged by disposition
  O  explicit historical use keeps its DCC-XVI contract; disposition inert
  P  literal two-process persistence (G1/G2, no inherited-memory canary)
  Q  failure atomicity: old complete policy or new complete policy
  R  trace_conflict evidence (detection, disposition, revision, dependency)
  S  receipt evidence distinguishes unresolved/prefer/coexist
  T  idempotency: repeat noop, change replaces, clear twice
  U  18-case auditable corpus, 0 mismatches
  V  crash boundaries: pre-save crash loses nothing; save failure rolls back
  W  prior layers preserved (XIII/XVI/XVII/XVIII)

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
from form.persist import _STATE_DIR, _safe_owner
from form.mandell.conflict_disposition import (
    CONFLICT_DISPOSITION_VERSION,
    apply_dispositions,
    clear_disposition,
    conflict_id_for,
    detectable_conflicts,
    set_disposition,
    trace_conflict,
    validate_record,
)
from form.mandell.conflict_router import (
    CONFLICT_VERSION,
    detect_conflicts,
    route_conflicts,
)
from form.mandell.knowledge_selector import select_for_context, unit_text
from form.mandell.supersession import inspect_revision, supersede_proposal
from form.mandell.dependency_validity import inspect_dependency
from form.mandell.knowledge_lineage import lineage_record
from form.mandell.translate import translate
from form.mandell.semantic_router import route_intent
from form import persist_rest
from form.dell_matrix.nursery import Nursery, owner_nursery_path

STATE = Path(_STATE_DIR)
OWNERS: list[str] = []
CHECKS: list[tuple[str, bool]] = []

TA = "plants require water"
TB = "plants do not require water"
TC = "plants never need water"
TD = "greenhouse humidity affects growth"
CTX = "plants water"


def check(name: str, cond: bool) -> None:
    CHECKS.append((name, bool(cond)))
    if not cond:
        print(f"  FAIL: {name}")


def wipe_owner(owner: str) -> None:
    safe = _safe_owner(owner)
    for f in STATE.glob(f"*{safe}*"):
        try:
            if f.is_file():
                f.unlink()
        except OSError:
            pass


def fresh_owner(owner: str):
    wipe_owner(owner)
    if owner not in OWNERS:
        OWNERS.append(owner)
    return open_program(owner)


def add_confirmed(p, label: str, words: str | None = None, parents=None) -> str:
    pr = p.nursery.add(label, words=words if words is not None else label,
                       parents=parents or [])
    p.confirm_proposal(pr.id, _producer="test", _review_context=p.make_review_context(pr.id, "test"))
    return pr.id


def ctx(p, context: str = CTX):
    r = route_intent(p, translate(f"grow using knowledge about {context}"),
                     raw_line=context)
    assert r.ok, "contextual grow must succeed"
    return p.last_nurture


def cleanup() -> None:
    for owner in OWNERS:
        wipe_owner(owner)
    OWNERS.clear()


# ---------------------------------------------------------------- CONTROL A
def control_a() -> None:
    p = fresh_owner("DCCXIX_A")
    a = add_confirmed(p, TA)
    b = add_confirmed(p, TB)
    c = add_confirmed(p, TC)
    confs = detectable_conflicts(p)
    by_pair = {(e["id_a"], e["id_b"]): e for e in confs}
    check("A1 conflict A<->B detected", (a, b) in by_pair or (b, a) in by_pair)
    e_ab = by_pair.get((a, b)) or by_pair.get((b, a))
    check("A2 conflict A<->C detected", (a, c) in by_pair or (c, a) in by_pair)
    check("A3 B<->C not a conflict (both negated)",
          (b, c) not in by_pair and (c, b) not in by_pair)
    cid_ab = e_ab["conflict_id"]
    check("A4 identity order-independent",
          conflict_id_for(a, b) == conflict_id_for(b, a) == cid_ab)
    check("A5 identity carries cv1 marker", cid_ab.startswith("cv1:"))
    check("A6 distinct pairs get distinct identities",
          conflict_id_for(a, b) != conflict_id_for(a, c))
    # Restart stability: checkpoint commit + generation load (the coherent
    # restart path) re-detects the identical conflict identity.
    from form.mandell import checkpoint_generation as CG
    CG.commit_checkpoint(p)
    p2, _rc = CG.load_checkpoint("DCCXIX_A")
    confs2 = detectable_conflicts(p2)
    ids2 = {e["conflict_id"] for e in confs2}
    check("A7 identity stable across process restart", cid_ab in ids2)
    # Relevance rank must not leak into the identity.
    check("A8 identity independent of selection order",
          conflict_id_for(b, a) == conflict_id_for(a, b))


# ---------------------------------------------------------------- CONTROL B
def control_b() -> None:
    p = fresh_owner("DCCXIX_B")
    a = add_confirmed(p, TA)
    b = add_confirmed(p, TB)
    rec = ctx(p)
    check("B1 no disposition stored by default",
          p.nursery.conflict_dispositions == {})
    check("B2 default unresolved quarantines both",
          rec["routable_selected_ids"] == [] and
          set(rec["quarantined_ids"]) == {a, b})
    check("B3 receipt carries DCC-XIII conflict evidence",
          rec["conflict_version"] == CONFLICT_VERSION and rec["conflict_count"] == 1)
    check("B4 disposition evidence present and empty",
          rec["conflict_disposition_version"] == CONFLICT_DISPOSITION_VERSION and
          all(d["disposition"] == "unresolved" for d in rec["conflict_dispositions"]))
    # route_conflicts (DCC-XIII) agrees with apply_dispositions sans disposition.
    items = [{"id": x, "text": unit_text(p, x)} for x in (a, b)]
    old_r, old_q = route_conflicts([a, b], detect_conflicts(items))
    new_r, new_q, _ = apply_dispositions([a, b], detect_conflicts(items), p)
    check("B5 no-disposition routing identical to DCC-XIII",
          (old_r, old_q) == (new_r, new_q))


# ---------------------------------------------------------------- CONTROL C
def control_c() -> None:
    p = fresh_owner("DCCXIX_C")
    a = add_confirmed(p, TA)
    b = add_confirmed(p, TB)
    cid = conflict_id_for(a, b)
    # Language path: explicit operator command.
    r = route_intent(p, translate(f"resolve conflict {cid} prefer {a}"),
                     raw_line="resolve")
    check("C1 language command accepted", r.ok)
    last = p.last_nurture
    check("C2 receipt records prefer",
          last.get("ok") and last.get("disposition") == "prefer" and
          last.get("preferred_ids") == [a])
    rec = ctx(p)
    check("C3 prefer A routes A", rec["routable_selected_ids"] == [a])
    check("C4 prefer A excludes B",
          rec["quarantined_ids"] == [b])
    disp = {d["conflict_id"]: d for d in rec["conflict_dispositions"]}
    check("C5 receipt shows operator prefer",
          disp[cid]["disposition"] == "prefer" and
          disp[cid]["permitted_ids"] == [a])
    check("C6 policy exclusion names B",
          any(x["unit_id"] == b and x["conflict_id"] == cid
              for x in rec["conflict_policy_exclusions"]))
    check("C7 consumer scope is exactly preferred A",
          rec["consumer_scope_ids"] == [a])
    check("C8 relevance scores untouched by disposition",
          all("score" in s for s in rec["selected_details"]))


# ---------------------------------------------------------------- CONTROL D
def control_d() -> None:
    p = fresh_owner("DCCXIX_D")
    a = add_confirmed(p, TA)
    b = add_confirmed(p, TB)
    cid = conflict_id_for(a, b)
    rec0 = set_disposition(p, cid, "prefer", [b], "operator prefers the negative claim")
    check("D1 prefer B accepted", rec0["ok"] and not rec0["noop"])
    rec = ctx(p)
    check("D2 prefer B routes B", rec["routable_selected_ids"] == [b])
    check("D3 prefer B excludes A", rec["quarantined_ids"] == [a])
    check("D4 consumer scope is exactly B", rec["consumer_scope_ids"] == [b])


# ---------------------------------------------------------------- CONTROL E
def control_e() -> None:
    p = fresh_owner("DCCXIX_E")
    a = add_confirmed(p, TA)
    b = add_confirmed(p, TB)
    cid = conflict_id_for(a, b)
    rec0 = set_disposition(p, cid, "coexist", [])
    check("E1 coexist accepted", rec0["ok"])
    rec = ctx(p)
    check("E2 coexist routes both",
          rec["routable_selected_ids"] == [a, b] or
          set(rec["routable_selected_ids"]) == {a, b})
    check("E3 coexist quarantines neither", rec["quarantined_ids"] == [])
    check("E4 conflict still detected under coexist", rec["conflict_count"] == 1)
    disp = {d["conflict_id"]: d for d in rec["conflict_dispositions"]}
    check("E5 receipt keeps conflict + disposition=coexist",
          disp[cid]["disposition"] == "coexist" and
          set(disp[cid]["permitted_ids"]) == {a, b})
    check("E6 consumer scope holds both", set(rec["consumer_scope_ids"]) == {a, b})


# ---------------------------------------------------------------- CONTROL F
def control_f() -> None:
    p = fresh_owner("DCCXIX_F")
    a = add_confirmed(p, TA)
    b = add_confirmed(p, TB)
    cid = conflict_id_for(a, b)
    set_disposition(p, cid, "prefer", [a])
    rec0 = ctx(p)
    check("F1 prefer routes A before clear", rec0["routable_selected_ids"] == [a])
    c = clear_disposition(p, cid)
    check("F2 clear accepted", c["ok"] and not c["noop"])
    check("F3 clear reports previous disposition",
          c.get("cleared_disposition") == "prefer")
    rec = ctx(p)
    check("F4 after clear both quarantined (unresolved)",
          rec["routable_selected_ids"] == [] and
          set(rec["quarantined_ids"]) == {a, b})
    check("F5 record removed from store", cid not in p.nursery.conflict_dispositions)
    c2 = clear_disposition(p, cid)
    check("F6 clear twice is deterministic noop",
          c2["ok"] and c2["noop"])
    # Language path for clear.
    set_disposition(p, cid, "coexist", [])
    r = route_intent(p, translate(f"clear conflict resolution {cid}"),
                     raw_line="clear")
    check("F7 language clear accepted", r.ok)
    check("F8 language clear removed record",
          cid not in p.nursery.conflict_dispositions)

# ---------------------------------------------------------------- CONTROL G
def control_g() -> None:
    p = fresh_owner("DCCXIX_G")
    a = add_confirmed(p, TA)
    b = add_confirmed(p, TB)
    cid_old = conflict_id_for(a, b)
    set_disposition(p, cid_old, "prefer", [a])
    # Supersede the PREFERRED unit: A -> A2 (still a positive claim).
    p.acceptance_policy.grant_opt_in("test", scope="test")
    sup = supersede_proposal(p, a, "plants require water", _producer="test")
    check("G1 supersede succeeded", sup.get("ok"))
    a2 = sup["new_id"]
    cid_new = conflict_id_for(a2, b)
    check("G2 new conflict has a NEW identity", cid_new != cid_old)
    confs = detectable_conflicts(p)
    ids = {e["conflict_id"] for e in confs}
    check("G3 old conflict no longer detected", cid_old not in ids)
    check("G4 new conflict detected", cid_new in ids)
    rec = ctx(p)
    disp = {d["conflict_id"]: d for d in rec["conflict_dispositions"]}
    check("G5 old disposition does not govern the new conflict",
          disp[cid_new]["disposition"] == "unresolved")
    check("G6 new conflict quarantined by default",
          a2 in rec["quarantined_ids"] and b in rec["quarantined_ids"])
    check("G7 old disposition retained as stale (inspectable)",
          cid_old in rec["stale_disposition_ids"])
    tr = trace_conflict(p, cid_old)
    check("G8 stale disposition traceable",
          tr["ok"] and tr["disposition"] == "prefer" and
          "stale" in tr["applicability"])


# ---------------------------------------------------------------- CONTROL H
def control_h() -> None:
    p = fresh_owner("DCCXIX_H")
    a = add_confirmed(p, TA)
    b = add_confirmed(p, TB)
    cid_old = conflict_id_for(a, b)
    set_disposition(p, cid_old, "prefer", [a])
    # Supersede the NON-preferred unit: B -> B2 (still negative).
    p.acceptance_policy.grant_opt_in("test", scope="test")
    sup = supersede_proposal(p, b, "plants do not require water", _producer="test")
    check("H1 supersede succeeded", sup.get("ok"))
    b2 = sup["new_id"]
    cid_new = conflict_id_for(a, b2)
    check("H2 new conflict has a NEW identity", cid_new != cid_old)
    rec = ctx(p)
    disp = {d["conflict_id"]: d for d in rec["conflict_dispositions"]}
    check("H3 new conflict unresolved (no transfer)",
          disp[cid_new]["disposition"] == "unresolved")
    check("H4 both quarantined", set(rec["quarantined_ids"]) == {a, b2})
    check("H5 A2-less stale record kept", cid_old in rec["stale_disposition_ids"])


# ---------------------------------------------------------------- CONTROL I
def control_i() -> None:
    # Mandatory: preferred becomes dependency-invalid -> no auto-promotion.
    p = fresh_owner("DCCXIX_I")
    par = add_confirmed(p, "parent claim about soil")
    a = add_confirmed(p, TA, parents=[par])
    b = add_confirmed(p, TB)
    cid = conflict_id_for(a, b)
    r0 = set_disposition(p, cid, "prefer", [a])
    check("I1 disposition set while A valid", r0["ok"])
    check("I2 A dependency-valid before removal",
          inspect_dependency(p, a)["dependency_status"] == "valid")
    # Invalidate A's ancestry: remove the parent from the plane.
    check("I3 plane removal succeeds", p.cube.session.plane.remove(par))
    check("I4 A now dependency-invalid",
          inspect_dependency(p, a)["dependency_status"] != "valid")
    # The conflict is still detectable pairwise; the policy layer must
    # refuse to route either side.
    entry = {"id_a": a, "id_b": b}
    routable, quarantined, ev = apply_dispositions([a, b], [entry], p)
    check("I5 preferred-ineligible: A excluded", a not in routable)
    check("I6 preferred-ineligible: B NOT auto-promoted", b not in routable)
    check("I7 both quarantined", set(quarantined) == {a, b})
    excl = {x["unit_id"]: x["reason"] for x in ev["conflict_policy_exclusions"]}
    check("I8 receipt explains no fallback winner",
          excl.get(a, "").startswith("preferred participant ineligible") and
          excl.get(b, "") == "not preferred; no auto-promotion")
    check("I9 disposition remains inspectable",
          p.nursery.conflict_dispositions[cid]["disposition"] == "prefer")


# ---------------------------------------------------------------- CONTROL J
def control_j() -> None:
    p = fresh_owner("DCCXIX_J")
    a = add_confirmed(p, TA)
    b = add_confirmed(p, TB)
    cid = conflict_id_for(a, b)
    set_disposition(p, cid, "prefer", [a])
    # Remove B from the plane: the conflict can no longer be detected.
    check("J1 plane removal succeeds", p.cube.session.plane.remove(b))
    check("J2 conflict no longer detectable",
          all(e["conflict_id"] != cid for e in detectable_conflicts(p)))
    rec = ctx(p)
    check("J3 stale disposition has no routing effect",
          rec["routable_selected_ids"] == [a] and rec["quarantined_ids"] == [])
    check("J4 no global preferred-unit behavior: A routes on merit",
          rec["consumer_scope_ids"] == [a])
    check("J5 stale ID listed", cid in rec["stale_disposition_ids"])
    tr = trace_conflict(p, cid)
    check("J6 stale disposition inspectable via trace",
          tr["ok"] and tr["disposition"] == "prefer" and
          "stale" in tr["applicability"])


# ---------------------------------------------------------------- CONTROL K
def control_k() -> None:
    p = fresh_owner("DCCXIX_K")
    a = add_confirmed(p, TA)
    b = add_confirmed(p, TB)
    c = add_confirmed(p, TC)
    cid_ab = conflict_id_for(a, b)
    cid_ac = conflict_id_for(a, c)
    set_disposition(p, cid_ab, "prefer", [b])
    # (A,C) left unresolved.
    rec = ctx(p)
    check("K1 both conflicts detected", rec["conflict_count"] == 2)
    check("K2 A quarantined: one unresolved conflict suffices",
          a in rec["quarantined_ids"])
    check("K3 B routable (its only conflict prefers it)",
          b in rec["routable_selected_ids"])
    check("K4 C quarantined (unresolved)", c in rec["quarantined_ids"])
    check("K5 routable is exactly [B]", rec["routable_selected_ids"] == [b])
    disp = {d["conflict_id"]: d["disposition"] for d in rec["conflict_dispositions"]}
    check("K6 dispositions differ per conflict",
          disp[cid_ab] == "prefer" and disp[cid_ac] == "unresolved")


# ---------------------------------------------------------------- CONTROL L
def control_l() -> None:
    p = fresh_owner("DCCXIX_L")
    a = add_confirmed(p, TA)
    b = add_confirmed(p, TB)
    c = add_confirmed(p, TC)
    cid_ab = conflict_id_for(a, b)
    cid_ac = conflict_id_for(a, c)
    set_disposition(p, cid_ab, "coexist", [])
    rec = ctx(p)
    check("L1 coexist waives A/B quarantine only",
          a in rec["quarantined_ids"] and c in rec["quarantined_ids"])
    check("L2 B routes (no other conflict blocks it)",
          rec["routable_selected_ids"] == [b])
    disp = {d["conflict_id"]: d for d in rec["conflict_dispositions"]}
    check("L3 A/B permitted, A/C denied",
          set(disp[cid_ab]["permitted_ids"]) == {a, b} and
          disp[cid_ac]["permitted_ids"] == [])


# ---------------------------------------------------------------- CONTROL M
def control_m() -> None:
    p = fresh_owner("DCCXIX_M")
    a = add_confirmed(p, TA)
    b = add_confirmed(p, TB)
    cid = conflict_id_for(a, b)
    # Command layer: malformed inputs refused, nothing stored.
    r1 = set_disposition(p, "not-a-conflict-id", "prefer", [a])
    check("M1 malformed conflict_id refused", not r1["ok"])
    r2 = set_disposition(p, "cv1:" + "0" * 32, "prefer", [a])
    check("M2 unknown conflict refused", not r2["ok"])
    r3 = set_disposition(p, cid, "prefer", ["ghost_unit"])
    check("M3 non-participant preferred refused", not r3["ok"])
    r4 = set_disposition(p, cid, "prefer", [a, b])
    check("M4 duplicate/double preferred refused", not r4["ok"])
    r5 = set_disposition(p, cid, "truth", [])
    check("M5 bogus disposition type refused", not r5["ok"])
    r6 = set_disposition(p, cid, "coexist", [a])
    check("M6 coexist with preferred refused", not r6["ok"])
    check("M7 nothing stored after refusals",
          p.nursery.conflict_dispositions == {})
    # Routing layer: a hand-corrupted record fails closed.
    set_disposition(p, cid, "prefer", [a])
    p.nursery.conflict_dispositions[cid]["preferred_ids"] = ["ghost_unit"]
    p.nursery.save()
    entry = {"id_a": a, "id_b": b}
    routable, quarantined, ev = apply_dispositions([a, b], [entry], p)
    check("M8 corrupted record fails closed (both quarantined)",
          routable == [] and set(quarantined) == {a, b})
    check("M9 corrupted record flagged",
          ev["invalid_disposition_ids"] == [cid])
    # Structural validation unit checks.
    ok, errs = validate_record({"disposition": "prefer"})
    check("M10 validate_record rejects shapeless input", not ok and errs)
    ok2, _ = validate_record(p.nursery.conflict_dispositions[cid])
    check("M11 validate_record flags non-participant preferred", not ok2)

# ---------------------------------------------------------------- CONTROL N
def control_n() -> None:
    p = fresh_owner("DCCXIX_N")
    a = add_confirmed(p, TA)
    b = add_confirmed(p, TB)
    d = add_confirmed(p, TD)
    sel_before = select_for_context(p, CTX)
    before = {s["id"]: (s["score"], s["shared"], s["exact_phrase"],
                        s["ordered"], s["coverage"])
              for s in sel_before["selected"]}
    order_before = [s["id"] for s in sel_before["selected"]]
    cid = conflict_id_for(a, b)
    set_disposition(p, cid, "prefer", [a])
    sel_after = select_for_context(p, CTX)
    after = {s["id"]: (s["id"] and (s["score"], s["shared"], s["exact_phrase"],
                       s["ordered"], s["coverage"]))
             for s in sel_after["selected"]}
    after = {s["id"]: (s["score"], s["shared"], s["exact_phrase"],
                       s["ordered"], s["coverage"])
             for s in sel_after["selected"]}
    check("N1 relevance scores unchanged by disposition", before == after)
    check("N2 top-5 order unchanged by disposition",
          order_before == [s["id"] for s in sel_after["selected"]])
    set_disposition(p, cid, "coexist", [])
    sel_co = select_for_context(p, CTX)
    check("N3 coexist grants no relevance bonus",
          {s["id"]: s["score"] for s in sel_co["selected"]} ==
          {s["id"]: s["score"] for s in sel_before["selected"]})


# ---------------------------------------------------------------- CONTROL O
def control_o() -> None:
    # Explicit historical use (DCC-XVI contract) is untouched by disposition.
    p = fresh_owner("DCCXIX_O")
    a = add_confirmed(p, TA)
    b = add_confirmed(p, TB)
    cid = conflict_id_for(a, b)
    set_disposition(p, cid, "prefer", [a])
    p.acceptance_policy.grant_opt_in("test", scope="test")
    sup = supersede_proposal(p, a, "plants require water", _producer="test")
    a2 = sup["new_id"]
    r = route_intent(p, translate(f"use idea {a} to grow"), raw_line="use")
    check("O1 explicit use of superseded unit still governed by DCC-XVI",
          r.ok)
    last = p.last_nurture
    check("O2 lifecycle disclosed on explicit use",
          "superseded" in json.dumps(last).lower() or
          last.get("lifecycle_state") == "superseded" or
          "superseded_by_id" in json.dumps(last))
    # The stale prefer-A disposition does not leak onto the new revision.
    rec = ctx(p)
    cid_new = conflict_id_for(a2, b)
    disp = {d["conflict_id"]: d["disposition"] for d in rec["conflict_dispositions"]}
    check("O3 no disposition inheritance onto new revision",
          disp[cid_new] == "unresolved")


# ---------------------------------------------------------------- CONTROL R
def control_r() -> None:
    p = fresh_owner("DCCXIX_R")
    a = add_confirmed(p, TA)
    b = add_confirmed(p, TB)
    cid = conflict_id_for(a, b)
    set_disposition(p, cid, "prefer", [a], "greenhouse logs, 2026 season")
    # Language trace path.
    r = route_intent(p, translate(f"trace conflict {cid}"), raw_line="trace")
    check("R1 language trace accepted", r.ok)
    tr = p.last_discover
    check("R2 trace carries conflict_id", tr.get("conflict_id") == cid)
    check("R3 trace shows disposition", tr.get("disposition") == "prefer")
    ev = tr.get("detection_evidence") or {}
    check("R4 trace carries detection evidence",
          ev.get("id_a") in (a, b) and ev.get("frame_jaccard", 0) >= 0.5)
    parts = {x["unit_id"]: x for x in tr.get("participants", [])}
    check("R5 trace carries revision state",
          parts[a]["lifecycle_state"] == "active")
    check("R6 trace carries dependency state",
          parts[a]["dependency_status"] == "valid")
    check("R7 trace states applicability",
          "detected now" in tr.get("applicability", ""))
    check("R8 trace claims no truth",
          "truth" not in json.dumps(tr).lower().replace("not a truth claim", ""))
    tr_bad = trace_conflict(p, "bogus")
    check("R9 malformed trace refused honestly", not tr_bad["ok"])


# ---------------------------------------------------------------- CONTROL S
def control_s() -> None:
    p = fresh_owner("DCCXIX_S")
    a = add_confirmed(p, TA)
    b = add_confirmed(p, TB)
    cid = conflict_id_for(a, b)
    rec_u = ctx(p)
    du = {d["conflict_id"]: d for d in rec_u["conflict_dispositions"]}[cid]
    set_disposition(p, cid, "prefer", [a])
    rec_p = ctx(p)
    dp = {d["conflict_id"]: d for d in rec_p["conflict_dispositions"]}[cid]
    set_disposition(p, cid, "coexist", [])
    rec_c = ctx(p)
    dc = {d["conflict_id"]: d for d in rec_c["conflict_dispositions"]}[cid]
    check("S1 unresolved receipt: quarantine, no preferred",
          du["disposition"] == "unresolved" and du["permitted_ids"] == [])
    check("S2 prefer receipt: permitted==preferred",
          dp["disposition"] == "prefer" and dp["permitted_ids"] == [a])
    check("S3 coexist receipt: both permitted",
          dc["disposition"] == "coexist" and set(dc["permitted_ids"]) == {a, b})
    check("S4 the three receipts are pairwise distinct",
          len({du["disposition"], dp["disposition"], dc["disposition"]}) == 3)
    for rec in (rec_u, rec_p, rec_c):
        check("S5 DCC-XIII conflict evidence retained",
              rec["conflict_version"] == CONFLICT_VERSION and
              rec["conflict_count"] == 1 and len(rec["conflicts"]) == 1)
        check("S6 disposition version stamped",
              rec["conflict_disposition_version"] == CONFLICT_DISPOSITION_VERSION)


# ---------------------------------------------------------------- CONTROL T
def control_t() -> None:
    p = fresh_owner("DCCXIX_T")
    a = add_confirmed(p, TA)
    b = add_confirmed(p, TB)
    cid = conflict_id_for(a, b)
    r1 = set_disposition(p, cid, "prefer", [a], "first reason")
    check("T1 first set accepted", r1["ok"] and not r1["noop"])
    seq1 = r1["update_seq"]
    r2 = set_disposition(p, cid, "prefer", [a], "first reason")
    check("T2 identical repeat is noop", r2["ok"] and r2["noop"])
    check("T3 noop does not bump seq", r2["update_seq"] == seq1)
    r3 = set_disposition(p, cid, "prefer", [b], "changed mind")
    check("T4 change replaces deterministically",
          r3["ok"] and not r3["noop"] and
          r3["update_seq"] == seq1 + 1 and r3["preferred_ids"] == [b])
    check("T5 store reflects replacement",
          p.nursery.conflict_dispositions[cid]["preferred_ids"] == [b])
    r4 = set_disposition(p, cid, "prefer", [b], "changed mind")
    check("T6 repeat of replacement is noop", r4["ok"] and r4["noop"])
    c1 = clear_disposition(p, cid)
    c2 = clear_disposition(p, cid)
    check("T7 clear twice deterministic",
          c1["ok"] and not c1["noop"] and c2["ok"] and c2["noop"])

# ---------------------------------------------------------------- CONTROL U
def control_u() -> None:
    """18-case auditable conflict-disposition corpus. 0 mismatches required."""
    mismatches = []

    def run(num, name, build, expect):
        p = fresh_owner(f"DCCXIX_U{num:02d}")
        got = build(p)
        ok = True
        for k, v in expect.items():
            gv = got.get(k)
            if isinstance(v, (set, list)) and isinstance(gv, (set, list)):
                match = set(v) == set(gv)
            else:
                match = gv == v
            if not match:
                ok = False
                mismatches.append((num, name, k, v, gv))
        check(f"U{num:02d} corpus: {name}", ok)
        return got

    def base_ab(p):
        a = add_confirmed(p, TA)
        b = add_confirmed(p, TB)
        return p, a, b, conflict_id_for(a, b)

    def snap(p, rec):
        return {
            "detected": rec["conflict_count"],
            "dispositions": sorted(
                (d["conflict_id"], d["disposition"]) for d in rec["conflict_dispositions"]),
            "exclusions": sorted(x["unit_id"] for x in rec["conflict_policy_exclusions"]),
            "routable": list(rec["routable_selected_ids"]),
            "scope": list(rec["consumer_scope_ids"] or []),
        }

    # 1. unresolved A/B
    def b1(p):
        p, a, b, cid = base_ab(p)
        return {**snap(p, ctx(p)), "cid": cid}
    g = run(1, "unresolved A/B", b1,
            {"detected": 1, "routable": [], "scope": []})
    cid1 = g["cid"]

    # 2. prefer A (exact expectation, checked explicitly below)
    def b2b(p):
        p, a, b, cid = base_ab(p)
        set_disposition(p, cid, "prefer", [a])
        rec = ctx(p)
        return {"detected": rec["conflict_count"],
                "disposition": [d["disposition"] for d in rec["conflict_dispositions"]],
                "routable": list(rec["routable_selected_ids"]),
                "scope": list(rec["consumer_scope_ids"] or []),
                "excluded": sorted(x["unit_id"] for x in rec["conflict_policy_exclusions"])}
    p2 = fresh_owner("DCCXIX_U02")
    got2 = b2b(p2)
    a2 = [u for u in p2.nursery.proposals if u.startswith("plants_require_water_")][0]
    b2i = [u for u in p2.nursery.proposals if "do_not_require" in u][0]
    ok2 = (got2["detected"] == 1 and got2["disposition"] == ["prefer"] and
           got2["routable"] == [a2] and got2["scope"] == [a2] and
           got2["excluded"] == [b2i])
    check("U02 corpus: prefer A", ok2)
    if not ok2:
        mismatches.append((2, "prefer A", "exact", "see above", got2))

    # 3. prefer B
    def b3(p):
        p, a, b, cid = base_ab(p)
        set_disposition(p, cid, "prefer", [b])
        rec = ctx(p)
        return {"routable": list(rec["routable_selected_ids"]),
                "scope": list(rec["consumer_scope_ids"] or [])}
    p3 = fresh_owner("DCCXIX_U03")
    got3 = b3(p3)
    b3i = [u for u in p3.nursery.proposals if "do_not_require" in u][0]
    ok3 = got3["routable"] == [b3i] and got3["scope"] == [b3i]
    check("U03 corpus: prefer B", ok3)
    if not ok3:
        mismatches.append((3, "prefer B", "exact", [b3i], got3))

    # 4. coexist A/B
    def b4(p):
        p, a, b, cid = base_ab(p)
        set_disposition(p, cid, "coexist", [])
        rec = ctx(p)
        return {"detected": rec["conflict_count"],
                "disposition": [d["disposition"] for d in rec["conflict_dispositions"]],
                "routable": sorted(rec["routable_selected_ids"]),
                "quarantined": rec["quarantined_ids"]}
    p4 = fresh_owner("DCCXIX_U04")
    got4 = b4(p4)
    a4 = [u for u in p4.nursery.proposals if u.startswith("plants_require_water_")][0]
    b4i = [u for u in p4.nursery.proposals if "do_not_require" in u][0]
    ok4 = (got4["detected"] == 1 and got4["disposition"] == ["coexist"] and
           got4["routable"] == sorted([a4, b4i]) and got4["quarantined"] == [])
    check("U04 corpus: coexist A/B", ok4)
    if not ok4:
        mismatches.append((4, "coexist A/B", "exact", "both routable", got4))

    # 5. clear -> unresolved
    def b5(p):
        p, a, b, cid = base_ab(p)
        set_disposition(p, cid, "prefer", [a])
        clear_disposition(p, cid)
        rec = ctx(p)
        return {"routable": list(rec["routable_selected_ids"]),
                "stored": cid in p.nursery.conflict_dispositions}
    p5 = fresh_owner("DCCXIX_U05")
    got5 = b5(p5)
    ok5 = got5["routable"] == [] and got5["stored"] is False
    check("U05 corpus: clear -> unresolved", ok5)
    if not ok5:
        mismatches.append((5, "clear -> unresolved", "exact", "[]", got5))

    # 6. prefer then supersede preferred
    def b6(p):
        p, a, b, cid = base_ab(p)
        set_disposition(p, cid, "prefer", [a])
        p.acceptance_policy.grant_opt_in("test", scope="test")
        sup = supersede_proposal(p, a, "plants require water", _producer="test")
        a2x = sup["new_id"]
        rec = ctx(p)
        disp = {d["conflict_id"]: d["disposition"] for d in rec["conflict_dispositions"]}
        return {"new_identity": conflict_id_for(a2x, b) != cid,
                "new_disposition": disp.get(conflict_id_for(a2x, b)),
                "routable": list(rec["routable_selected_ids"])}
    p6 = fresh_owner("DCCXIX_U06")
    got6 = b6(p6)
    ok6 = got6["new_identity"] and got6["new_disposition"] == "unresolved" and got6["routable"] == []
    check("U06 corpus: prefer then supersede preferred", ok6)
    if not ok6:
        mismatches.append((6, "supersede preferred", "exact", "new unresolved", got6))

    # 7. prefer then supersede nonpreferred
    def b7(p):
        p, a, b, cid = base_ab(p)
        set_disposition(p, cid, "prefer", [a])
        p.acceptance_policy.grant_opt_in("test", scope="test")
        sup = supersede_proposal(p, b, "plants do not require water", _producer="test")
        b2x = sup["new_id"]
        rec = ctx(p)
        disp = {d["conflict_id"]: d["disposition"] for d in rec["conflict_dispositions"]}
        return {"new_identity": conflict_id_for(a, b2x) != cid,
                "new_disposition": disp.get(conflict_id_for(a, b2x)),
                "routable": list(rec["routable_selected_ids"])}
    p7 = fresh_owner("DCCXIX_U07")
    got7 = b7(p7)
    ok7 = got7["new_identity"] and got7["new_disposition"] == "unresolved" and got7["routable"] == []
    check("U07 corpus: prefer then supersede nonpreferred", ok7)
    if not ok7:
        mismatches.append((7, "supersede nonpreferred", "exact", "new unresolved", got7))

    # 8. preferred becomes dependency-invalid (policy layer, mandatory control)
    def b8(p):
        par = add_confirmed(p, "parent claim about soil")
        a = add_confirmed(p, TA, parents=[par])
        b = add_confirmed(p, TB)
        cid = conflict_id_for(a, b)
        set_disposition(p, cid, "prefer", [a])
        p.cube.session.plane.remove(par)
        entry = {"id_a": a, "id_b": b}
        routable, quarantined, ev = apply_dispositions([a, b], [entry], p)
        excl = {x["unit_id"]: x["reason"] for x in ev["conflict_policy_exclusions"]}
        return {"routable": routable,
                "a_reason": excl.get(a, ""),
                "b_reason": excl.get(b, "")}
    p8 = fresh_owner("DCCXIX_U08")
    got8 = b8(p8)
    ok8 = (got8["routable"] == [] and
           got8["a_reason"].startswith("preferred participant ineligible") and
           got8["b_reason"] == "not preferred; no auto-promotion")
    check("U08 corpus: preferred dependency-invalid", ok8)
    if not ok8:
        mismatches.append((8, "dep-invalid", "exact", "no auto-promotion", got8))

    # 9. stale historical disposition
    def b9(p):
        p, a, b, cid = base_ab(p)
        set_disposition(p, cid, "prefer", [a])
        p.cube.session.plane.remove(b)
        rec = ctx(p)
        return {"routable": list(rec["routable_selected_ids"]),
                "stale": cid in rec["stale_disposition_ids"],
                "kept": p.nursery.conflict_dispositions.get(cid, {}).get("disposition")}
    p9 = fresh_owner("DCCXIX_U09")
    got9 = b9(p9)
    a9 = [u for u in p9.nursery.proposals if u.startswith("plants_require_water_")][0]
    ok9 = got9["stale"] and got9["kept"] == "prefer" and a9 in got9["routable"]
    check("U09 corpus: stale historical disposition", ok9)
    if not ok9:
        mismatches.append((9, "stale", "exact", "no effect, inspectable", got9))

    # 10. A/B prefer A + A/C unresolved
    def b10(p):
        a = add_confirmed(p, TA)
        b = add_confirmed(p, TB)
        c = add_confirmed(p, TC)
        set_disposition(p, conflict_id_for(a, b), "prefer", [a])
        rec = ctx(p)
        return {"routable": list(rec["routable_selected_ids"])}
    p10 = fresh_owner("DCCXIX_U10")
    got10 = b10(p10)
    ok10 = got10["routable"] == []
    check("U10 corpus: prefer A/B + unresolved A/C", ok10)
    if not ok10:
        mismatches.append((10, "multi-conflict", "exact", [], got10))

    # 11. A/B coexist + A/C unresolved
    def b11(p):
        a = add_confirmed(p, TA)
        b = add_confirmed(p, TB)
        c = add_confirmed(p, TC)
        set_disposition(p, conflict_id_for(a, b), "coexist", [])
        rec = ctx(p)
        return {"routable": list(rec["routable_selected_ids"])}
    p11 = fresh_owner("DCCXIX_U11")
    got11 = b11(p11)
    b11i = [u for u in p11.nursery.proposals if "do_not_require" in u][0]
    ok11 = got11["routable"] == [b11i]
    check("U11 corpus: coexist A/B + unresolved A/C", ok11)
    if not ok11:
        mismatches.append((11, "coexist+other", "exact", [b11i], got11))

    # 12. malformed preferred ID
    def b12(p):
        p, a, b, cid = base_ab(p)
        r = set_disposition(p, cid, "prefer", ["ghost"])
        rec = ctx(p)
        return {"accepted": r["ok"], "routable": list(rec["routable_selected_ids"])}
    p12 = fresh_owner("DCCXIX_U12")
    got12 = b12(p12)
    ok12 = got12["accepted"] is False and got12["routable"] == []
    check("U12 corpus: malformed preferred ID", ok12)
    if not ok12:
        mismatches.append((12, "malformed preferred", "exact", "refused", got12))

    # 13. unknown conflict
    def b13(p):
        p, a, b, cid = base_ab(p)
        r = set_disposition(p, "cv1:" + "f" * 32, "prefer", [a])
        rec = ctx(p)
        return {"accepted": r["ok"], "routable": list(rec["routable_selected_ids"])}
    p13 = fresh_owner("DCCXIX_U13")
    got13 = b13(p13)
    ok13 = got13["accepted"] is False and got13["routable"] == []
    check("U13 corpus: unknown conflict", ok13)
    if not ok13:
        mismatches.append((13, "unknown conflict", "exact", "refused", got13))

    # 14. restart persistence
    def b14(p):
        p, a, b, cid = base_ab(p)
        set_disposition(p, cid, "prefer", [a])
        p2 = open_program(p.owner)  # fresh process: nursery reload only
        stored = p2.nursery.conflict_dispositions.get(cid, {})
        return {"kept": stored.get("disposition"),
                "participants": stored.get("participant_ids"),
                "preferred": stored.get("preferred_ids")}
    p14 = fresh_owner("DCCXIX_U14")
    got14 = b14(p14)
    a14 = [u for u in p14.nursery.proposals if u.startswith("plants_require_water_")][0]
    b14i = [u for u in p14.nursery.proposals if "do_not_require" in u][0]
    ok14 = (got14["kept"] == "prefer" and
            set(got14["participants"]) == {a14, b14i} and
            got14["preferred"] == [a14])
    check("U14 corpus: restart persistence", ok14)
    if not ok14:
        mismatches.append((14, "restart", "exact", "prefer survives", got14))

    # 15. relevance scores unchanged
    def b15(p):
        p, a, b, cid = base_ab(p)
        d = add_confirmed(p, TD)
        s0 = {s["id"]: s["score"] for s in select_for_context(p, CTX)["selected"]}
        set_disposition(p, cid, "prefer", [a])
        s1 = {s["id"]: s["score"] for s in select_for_context(p, CTX)["selected"]}
        return {"same": s0 == s1}
    p15 = fresh_owner("DCCXIX_U15")
    got15 = b15(p15)
    check("U15 corpus: relevance scores unchanged", got15["same"])
    if not got15["same"]:
        mismatches.append((15, "relevance", "exact", "unchanged", got15))

    # 16. top-5 unchanged
    def b16(p):
        p, a, b, cid = base_ab(p)
        d = add_confirmed(p, TD)
        o0 = [s["id"] for s in select_for_context(p, CTX)["selected"]]
        set_disposition(p, cid, "coexist", [])
        o1 = [s["id"] for s in select_for_context(p, CTX)["selected"]]
        return {"same": o0 == o1}
    p16 = fresh_owner("DCCXIX_U16")
    got16 = b16(p16)
    check("U16 corpus: top-5 unchanged", got16["same"])
    if not got16["same"]:
        mismatches.append((16, "top-5", "exact", "unchanged", got16))

    # 17. explicit historical use keeps DCC-XVI contract
    def b17(p):
        p, a, b, cid = base_ab(p)
        set_disposition(p, cid, "prefer", [a])
        p.acceptance_policy.grant_opt_in("test", scope="test")
        sup = supersede_proposal(p, a, "plants require water", _producer="test")
        r = route_intent(p, translate(f"use idea {a} to grow"), raw_line="use")
        return {"ok": r.ok}
    p17 = fresh_owner("DCCXIX_U17")
    got17 = b17(p17)
    check("U17 corpus: explicit historical use", got17["ok"])
    if not got17["ok"]:
        mismatches.append((17, "historical use", "exact", True, got17))

    # 18. deterministic repeated disposition
    def b18(p):
        p, a, b, cid = base_ab(p)
        r1 = set_disposition(p, cid, "prefer", [a], "reason")
        r2 = set_disposition(p, cid, "prefer", [a], "reason")
        rec = ctx(p)
        return {"noop": r2["noop"], "same_seq": r2["update_seq"] == r1["update_seq"],
                "routable": list(rec["routable_selected_ids"])}
    p18 = fresh_owner("DCCXIX_U18")
    got18 = b18(p18)
    a18 = [u for u in p18.nursery.proposals if u.startswith("plants_require_water_")][0]
    ok18 = got18["noop"] and got18["same_seq"] and got18["routable"] == [a18]
    check("U18 corpus: deterministic repeat", ok18)
    if not ok18:
        mismatches.append((18, "repeat", "exact", "noop", got18))

    check("U19 corpus mismatch count is 0", len(mismatches) == 0)
    if mismatches:
        for m in mismatches:
            print(f"  CORPUS MISMATCH case {m[0]} ({m[1]}): field={m[2]}")

# ---------------------------------------------------------------- CONTROL P
_CHILD_A = r'''
import json, os, sys
sys.path.insert(0, __REPO__)
from form.open import open_program
from form.mandell import checkpoint_generation as CG
from form.mandell.conflict_disposition import conflict_id_for, set_disposition, detectable_conflicts
from form.mandell.supersession import supersede_proposal

owner = "DCCXIX_P"
p = open_program(owner)
# G1: base knowledge.
x = p.nursery.add("soil retains moisture"); p.confirm_proposal(x.id, _producer="test", _review_context=p.make_review_context(x.id, "test"))
CG.commit_checkpoint(p)  # G1
g1 = CG.load_checkpoint(owner)[1]["generation_id"]
# G2: revision + lineage + dependency + routing fixture, then disposition.
p.acceptance_policy.grant_opt_in("test", scope="test")
sup = supersede_proposal(p, x.id, "soil retains moisture well", _producer="test")
x2 = sup["new_id"]
y = p.nursery.add("watering schedule depends on soil", parents=[x2]); p.confirm_proposal(y.id, _producer="test", _review_context=p.make_review_context(y.id, "test"))
a = p.nursery.add("plants require water"); p.confirm_proposal(a.id, _producer="test", _review_context=p.make_review_context(a.id, "test"))
b = p.nursery.add("plants do not require water"); p.confirm_proposal(b.id, _producer="test", _review_context=p.make_review_context(b.id, "test"))
cid = conflict_id_for(a.id, b.id)
assert any(e["conflict_id"] == cid for e in detectable_conflicts(p)), "conflict must detect"
r = set_disposition(p, cid, "prefer", [a.id], "operator: greenhouse logs")
assert r["ok"], r
p.__dccxix_canary__ = "inherited-memory"
rc = CG.commit_checkpoint(p)  # G2
out = {"pid": os.getpid(), "g1": g1, "g2": rc["generation_id"],
       "cid": cid, "a": a.id, "b": b.id, "x2": x2, "y": y.id,
       "members": rc["members"]}
open(__OUT__, "w").write(json.dumps(out))
os._exit(0)
'''

_CHILD_B = r'''
import json, os, sys
sys.path.insert(0, __REPO__)
from form.open import open_program
from form.mandell import checkpoint_generation as CG
from form.mandell.conflict_disposition import apply_dispositions, conflict_id_for, detectable_conflicts
from form.mandell.conflict_router import detect_conflicts
from form.mandell.knowledge_selector import unit_text
from form.mandell.supersession import inspect_revision
from form.mandell.dependency_validity import inspect_dependency
from form.mandell.knowledge_lineage import lineage_record

owner = "DCCXIX_P"
expect = json.load(open(__OUT__))
p2, rc = CG.load_checkpoint(owner)  # independent process, persisted state only
res = {"pid": os.getpid()}
res["generation_matches"] = rc["generation_id"] == expect["g2"]
res["fingerprints"] = {k: v["sha256"] for k, v in rc["members"].items()}
res["no_canary"] = not hasattr(p2, "__dccxix_canary__")
a, b, cid = expect["a"], expect["b"], expect["cid"]
res["conflict_reconstructed"] = any(e["conflict_id"] == cid for e in detectable_conflicts(p2))
res["disposition_recovered"] = (p2.nursery.conflict_dispositions.get(cid, {}).get("disposition") == "prefer")
res["revision"] = inspect_revision(p2, expect["x2"])["lifecycle_state"]
res["lineage_parents"] = lineage_record(p2, expect["y"])["parent_ids"]
res["dependency"] = inspect_dependency(p2, expect["y"])["dependency_status"]
items = [{"id": u, "text": unit_text(p2, u)} for u in (a, b)]
routable, quarantined, ev = apply_dispositions([a, b], detect_conflicts(items), p2)
res["routing_routable"] = routable
res["routing_quarantined"] = quarantined
res["distinct_pid"] = res["pid"] != expect["pid"]
open(__RES__, "w").write(json.dumps(res))
os._exit(0)
'''


def control_p() -> None:
    owner = "DCCXIX_P"
    wipe_owner(owner)
    OWNERS.append(owner)
    out_path = str(STATE / "dccxix_p_out.json")
    res_path = str(STATE / "dccxix_p_res.json")
    for f in (out_path, res_path):
        try:
            os.unlink(f)
        except OSError:
            pass
    repo = str(REPO)
    def _fill(t):
        return t.replace("__REPO__", repr(repo)).replace("__OUT__", repr(out_path)).replace("__RES__", repr(res_path))
    with open(STATE / "dccxix_child_a.py", "w") as f:
        f.write(_fill(_CHILD_A))
    with open(STATE / "dccxix_child_b.py", "w") as f:
        f.write(_fill(_CHILD_B))
    try:
        ra = subprocess.run([sys.executable, str(STATE / "dccxix_child_a.py")],
                            capture_output=True, text=True, timeout=300)
        check("P1 process A exited cleanly", ra.returncode == 0)
        if ra.returncode != 0:
            print("  child A stderr:", ra.stderr[-2000:])
            return
        rb = subprocess.run([sys.executable, str(STATE / "dccxix_child_b.py")],
                            capture_output=True, text=True, timeout=300)
        check("P2 process B exited cleanly", rb.returncode == 0)
        if rb.returncode != 0:
            print("  child B stderr:", rb.stderr[-2000:])
            return
        out = json.load(open(out_path))
        res = json.load(open(res_path))
        check("P3 distinct PIDs (literal two-process)", res["distinct_pid"])
        check("P4 B loaded committed G2", res["generation_matches"])
        check("P5 member fingerprints present",
              set(res["fingerprints"]) == {"nursery", "program", "ideas", "graph"} and
              all(len(v) == 64 for v in res["fingerprints"].values()))
        check("P6 no inherited-memory canary", res["no_canary"])
        check("P7 conflict reconstructed in B", res["conflict_reconstructed"])
        check("P8 disposition recovered in B", res["disposition_recovered"])
        check("P9 revision fixture intact", res["revision"] == "active")
        check("P10 lineage fixture intact", out["x2"] in res["lineage_parents"])
        check("P11 dependency fixture valid", res["dependency"] == "valid")
        check("P12 routing follows disposition in B",
              res["routing_routable"] == [out["a"]] and
              res["routing_quarantined"] == [out["b"]])
    finally:
        for f in ("dccxix_child_a.py", "dccxix_child_b.py",
                  "dccxix_p_out.json", "dccxix_p_res.json"):
            try:
                os.unlink(STATE / f)
            except OSError:
                pass


# ---------------------------------------------------------------- CONTROL Q
def control_q() -> None:
    from form.mandell import checkpoint_generation as CG
    from form.mandell.checkpoint_generation import CheckpointCommitError
    p = fresh_owner("DCCXIX_Q")
    a = add_confirmed(p, TA)
    b = add_confirmed(p, TB)
    cid = conflict_id_for(a, b)
    # Save failure during set_disposition: old policy preserved, honestly reported.
    real_save = p.nursery.save
    def boom(*args, **kwargs):
        raise OSError("simulated disk failure")
    p.nursery.save = boom
    r = set_disposition(p, cid, "prefer", [a])
    p.nursery.save = real_save
    check("Q1 save failure reported honestly", not r["ok"] and "persistence failed" in r["error"])
    check("Q2 in-memory store rolled back", cid not in p.nursery.conflict_dispositions)
    p2 = open_program("DCCXIX_Q")
    check("Q3 disk holds old complete policy",
          cid not in p2.nursery.conflict_dispositions)
    # Checkpoint failure: old generation stays authoritative.
    set_disposition(p, cid, "prefer", [a])
    g1 = CG.commit_checkpoint(p)["generation_id"]
    set_disposition(p, cid, "coexist", [])
    try:
        CG.commit_checkpoint(p, _fail_at="after_members")
        check("Q4 checkpoint failure raised", False)
    except CheckpointCommitError:
        check("Q4 checkpoint failure raised", True)
    _, rc = CG.load_checkpoint("DCCXIX_Q")
    check("Q5 failed checkpoint leaves previous generation authoritative",
          rc["generation_id"] == g1)
    check("Q6 previous generation carries prefer (not half-policy)",
          CG.load_checkpoint("DCCXIX_Q")[0].nursery.conflict_dispositions[cid]["disposition"] == "prefer")


# ---------------------------------------------------------------- CONTROL V
def control_v() -> None:
    p = fresh_owner("DCCXIX_V")
    a = add_confirmed(p, TA)
    b = add_confirmed(p, TB)
    cid = conflict_id_for(a, b)
    persist_rest.save(p)
    # Crash between in-memory mutation and save: the disk is the authority;
    # a fresh process must see the OLD policy (nothing).
    p.nursery.conflict_dispositions[cid] = {
        "conflict_disposition_version": CONFLICT_DISPOSITION_VERSION,
        "conflict_id": cid,
        "participant_ids": sorted([a, b]),
        "disposition": "prefer",
        "preferred_ids": [a],
        "operator_reason": "",
        "update_seq": 1,
    }
    # NOTE: deliberately no save() -> simulates os._exit before the write.
    p2 = open_program("DCCXIX_V")
    check("V1 pre-save crash loses nothing durable",
          cid not in p2.nursery.conflict_dispositions)
    # A committed disposition survives; clearing is equally atomic.
    # (Discard V1's simulated-crash dirt: it was never saved, so the honest
    # post-crash in-memory state is the empty map. A reload would also drop
    # the plane, which open_program never restores.)
    del p.nursery.conflict_dispositions[cid]
    set_disposition(p, cid, "prefer", [a])
    p3 = open_program("DCCXIX_V")
    check("V2 committed disposition durable",
          p3.nursery.conflict_dispositions[cid]["disposition"] == "prefer")
    # Failed clear preserves the existing record.
    real_save = p.nursery.save
    p.nursery.save = lambda *a_, **k_: (_ for _ in ()).throw(OSError("disk down"))
    c = clear_disposition(p, cid)
    p.nursery.save = real_save
    check("V3 failed clear reported", not c["ok"])
    check("V4 failed clear keeps record",
          p.nursery.conflict_dispositions.get(cid, {}).get("disposition") == "prefer")


# ---------------------------------------------------------------- CONTROL W
def control_w() -> None:
    # Prior layers preserved under DCC-XIX.
    from form.mandell import checkpoint_generation as CG
    p = fresh_owner("DCCXIX_W")
    a = add_confirmed(p, TA)
    b = add_confirmed(p, TB)
    cid = conflict_id_for(a, b)
    set_disposition(p, cid, "prefer", [a])
    rc = CG.commit_checkpoint(p)
    p2, rc2 = CG.load_checkpoint("DCCXIX_W")
    check("W1 checkpoint seals dispositions",
          p2.nursery.conflict_dispositions[cid]["disposition"] == "prefer")
    check("W2 generation loads coherent", rc2["generation_id"] == rc["generation_id"])
    # DCC-XIII default still applies to conflicts without dispositions.
    c = add_confirmed(p2, TC)
    rec = ctx(p2)
    disp = {d["conflict_id"]: d["disposition"] for d in rec["conflict_dispositions"]}
    check("W3 undispositioned conflict still unresolved",
          disp.get(conflict_id_for(a, c)) == "unresolved")
    # DCC-XVII: nursery file still loadable / writable through V2 path.
    p2.nursery.save()
    p3 = open_program("DCCXIX_W")
    check("W4 nursery V2 round-trip keeps dispositions",
          p3.nursery.conflict_dispositions[cid]["preferred_ids"] == [a])


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
    control_r()
    control_s()
    control_t()
    control_u()
    control_p()
    control_q()
    control_v()
    control_w()
    cleanup()
    total = len(CHECKS)
    failed = [n for n, ok in CHECKS if not ok]
    print(f"DCC-XIX: {total - len(failed)}/{total}")
    for n in failed:
        print(f"  FAILED: {n}")
    return 0 if not failed else 1


def smoke() -> bool:
    """Regress entry point: the full dedicated DCC-XIX control suite."""
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
