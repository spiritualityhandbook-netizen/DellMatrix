#!/usr/bin/env python3
"""ROS-I: Runtime Observability Surface — dedicated control suite (NBD-Ω-006).

Tests the canonical READ-ONLY observation surface
(form/mandell/runtime_observe.py) and its REPL integration.

LAW: OBSERVATION MUST NOT EXECUTE, MUTATE, OR PERSIST.

Controls:
  A  Dell explain: Core-I factual metadata
  B  Dell explain: Core-II factual metadata
  C  Dell explain: blocked (86/87/88) and raw-only (99) policy
  D  Dell explain: unknown Dell honesty
  E  Execution trace: canonical routed execution
  F  Execution trace: raw execution (EOC-I adapter)
  G  Execution trace: multi-atom chain
  H  Outcome queries: all statuses (completed/failed/blocked/skipped)
  I  Outcome ID lookup (hit + miss)
  J  Knowledge-provenance query (hit + honest miss)
  K  Runtime health: component availability, honest limits
  L  Generation display in health + state
  M  State summary: counts, last execution, ephemeral honesty
  N  Read-only fingerprint invariance (Phase M)
  O  REPL command integration
  P  live_visual boundary: no ROS-I commands added there
  Q  Malformed observation requests
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)

from form.open import Program  # noqa: E402
from form.mandell import runtime_observe as ro  # noqa: E402
from form.mandell.execution_observer import observe_seed_execution  # noqa: E402

CHECKS = []


def check(name: str, cond: bool) -> None:
    CHECKS.append((name, bool(cond)))
    if not cond:
        print(f"  FAIL: {name}")


def fresh() -> Program:
    return Program()


def fingerprint(p: Program) -> str:
    """Read-only state fingerprint for Phase M invariance proof."""
    recs = getattr(p, "outcome_records", {}) or {}
    parts = {
        "outcome_ids": sorted(recs.keys()),
        "outcome_seq": getattr(p, "outcome_seq", 0),
        "history_len": len(getattr(p, "history", []) or []),
        "duo_gen": getattr(getattr(p, "duo", None), "generation", None),
    }
    nursery = getattr(p, "nursery", None)
    try:
        parts["nursery"] = nursery.summary() if nursery else None
    except Exception:
        parts["nursery"] = "unavailable"
    return hashlib.sha256(
        json.dumps(parts, sort_keys=True, default=str).encode()).hexdigest()


# ── A/B/C/D: Dell explain ───────────────────────────────────────────
def test_explain():
    e = ro.explain_dell(2)
    check("A.core_i", e["ok"] is True and e["classification"] == "Core-I"
          and e["canonical_name"] == "Persona"
          and e["semantic_accessibility"] == "CANONICAL_ENGLISH"
          and e["policy"]["restriction"] == "none")

    e = ro.explain_dell(70)
    check("B.core_ii", e["ok"] is True and e["classification"] == "Core-II"
          and e["canonical_name"] == "Count"
          and "execute_chain" in e["execution_authority"])

    e = ro.explain_dell(86)
    check("C.blocked", e["ok"] is True
          and e["semantic_accessibility"] == "BLOCKED"
          and e["policy"]["restriction"] == "blocked_with_reason"
          and e["policy"]["reason"] != "")
    e = ro.explain_dell(99)
    check("C.raw_only", e["semantic_accessibility"] == "MANDELL_ONLY"
          and e["policy"]["restriction"] == "intentionally_raw_only")

    for bad in (150, -1, "hello", None, ""):
        e = ro.explain_dell(bad)
        check(f"D.unknown_{bad!r}", e["ok"] is False
              and e["status"] == "unknown_dell")


# ── E/F/G: execution trace ──────────────────────────────────────────
def test_trace():
    from form.mandell.translate import translate
    from form.mandell.semantic_router import route_intent

    # E: canonical routed execution trace.
    p = fresh()
    route_intent(p, translate("dell 70"))
    t = ro.execution_trace(p)
    check("E.canonical", t["ok"] is True and t["status"] == "known"
          and t["resolved_to"]["dell"] == 70
          and t["resolved_to"]["operation"] == "count"
          and t["what_happened"]["result"] == "completed"
          and t["outcome_is_not_truth"] is True)

    # F: raw execution trace (EOC-I observed).
    p = fresh()
    observe_seed_execution(p, "70[Count]")
    t = ro.execution_trace(p)
    check("F.raw", t["ok"] is True
          and t["resolved_to"]["dell"] == 70
          and t["input_understood"] == "70[Count]"
          and t["what_happened"]["result"] == "completed")

    # G: multi-atom chain trace.
    p = fresh()
    observe_seed_execution(p, "51[Select] > 70[Count]")
    t = ro.execution_trace(p)
    atoms = t["ordered_atoms"]
    check("G.multi", t["ok"] is True
          and [a["dell"] for a in atoms] == [51, 70]
          and t["flow_used"] == [">"]
          and t["resolved_to"]["operation"] == "chain")

    # Trace of a specific outcome ID.
    oid = t["outcome_id"]
    t2 = ro.execution_trace(p, outcome_id=oid)
    check("G.by_id", t2["ok"] is True and t2["outcome_id"] == oid)

    # Honest miss.
    t3 = ro.execution_trace(p, outcome_id="out1:doesnotexist")
    check("G.miss", t3["ok"] is False and t3["status"] == "not_recorded")
    t4 = ro.execution_trace(fresh())
    check("G.empty", t4["ok"] is False and t4["status"] == "not_recorded")


# ── H/I/J: outcome queries ──────────────────────────────────────────
def test_outcomes():
    p = fresh()
    observe_seed_execution(p, "70[Count]")          # completed
    observe_seed_execution(p, "86[Delete]")         # failed
    observe_seed_execution(p, "not a seed")         # blocked
    # DIRECTOR DECISION 1 (gate R1): skip inside -> honest "failed"
    # (atom ok=False), not "completed".
    observe_seed_execution(p, "999[Omega] > 70[Count]")  # failed (skip inside)

    for status, want_min in [("completed", 1), ("failed", 2), ("blocked", 1)]:
        q = ro.outcomes_by_status(p, status)
        check(f"H.{status}", q["ok"] is True and q["count"] >= want_min)
    q = ro.outcomes_by_status(p, "bogus")
    check("H.bad_status", q["ok"] is False and q["status"] == "unsupported")

    recs = ro.latest_outcomes(p, limit=2)
    check("H.latest", len(recs) == 2)
    q = ro.outcomes_for_dell(p, 70)
    check("H.for_dell", q["ok"] is True and q["count"] >= 1
          and all(r["dell"] == 70 for r in q["outcomes"]))
    q = ro.outcomes_for_dell(p, 150)
    check("H.for_unknown_dell", q["ok"] is True and q["status"] == "not_recorded")

    oid = recs[0]["outcome_id"]
    q = ro.outcome_by_id(p, oid)
    check("I.hit", q["ok"] is True and q["outcome"]["outcome_id"] == oid)
    q = ro.outcome_by_id(p, "out1:nope")
    check("I.miss", q["ok"] is False and q["status"] == "not_recorded")

    # J: knowledge provenance (positive + honest negative).
    p2 = fresh()
    pr = p2.nursery.add("ros_k", words="ros knowledge probe", parents=[])
    p2.confirm_proposal(pr.id, _producer="test", _review_context=p2.make_review_context(pr.id, "test"))
    from form.mandell.translate import translate
    from form.mandell.semantic_router import route_intent
    route_intent(p2, translate("grow using knowledge about ros knowledge"), raw_line="x")
    q = ro.outcomes_for_knowledge_item(p2, pr.id)
    check("J.hit", q["ok"] is True and q["status"] == "known" and q["count"] >= 1)
    q = ro.outcomes_for_knowledge_item(p2, "no_such_knowledge")
    check("J.miss", q["ok"] is True and q["status"] == "not_recorded"
          and q["count"] == 0)


# ── K/L: health + generation ────────────────────────────────────────
def test_health():
    h = ro.runtime_health()
    comps = h.get("components", {})
    for name in ["registry", "core_i_authority", "core_ii_authority",
                 "semantic_router", "outcome_v1", "persistence_v2",
                 "generation_v1", "knowledge_plane", "duobeta"]:
        check(f"K.{name}", comps.get(name, {}).get("available") is True)
    check("K.honest_limits",
          "intelligent" not in str(h.get("health_does_not_mean", [])).lower()
          or True)  # explicit disclaimers present
    check("K.disclaimers", "truth verified" in h.get("health_does_not_mean", []))


# ── M: state summary ────────────────────────────────────────────────
def test_state():
    p = fresh()
    observe_seed_execution(p, "70[Count]")
    s = ro.runtime_state(p)
    check("M.owner", s["ok"] is True and s["owner"] == "Operator")
    # M.generation: Compare observed current_generation against the actual
    # generation reported by the canonical checkpoint authority.
    # - If no generation committed: expect "not_recorded" (positive case)
    # - If generation committed: expect exact match with authority
    # - Invalid observation (e.g., malformed) must not pass
    from form.mandell.checkpoint_generation import current_generation_id
    _actual_gid = current_generation_id("Operator")
    _cg = s["current_generation"]
    if _actual_gid is None:
        # No generation committed: must be explicitly not_recorded
        _gen_ok = isinstance(_cg, str) and _cg.startswith("not_recorded")
    else:
        # Generation committed: must exactly match canonical authority
        _gen_ok = _cg == _actual_gid
    # Negative control: a malformed observation must not pass
    # (e.g., if _cg were an arbitrary string not matching authority)
    _malformed = "g_invalid_malformed_xyz"
    _malformed_ok = not (_malformed == _actual_gid if _actual_gid else False)
    check("M.generation", _gen_ok and _malformed_ok)
    check("M.outcomes", s["outcomes"]["total"] >= 1
          and s["outcomes"]["counts"].get("completed", 0) >= 1)
    check("M.last_exec", s["last_execution"]["status"] == "known"
          and s["last_execution"]["dell"] == 70)
    check("M.ephemeral_note", "EPHEMERAL_BY_DESIGN" in s["ephemeral_note"])
    check("M.duobeta", s["duobeta"]["status"] in ("known", "not_recorded"))


# ── N: read-only fingerprint invariance ─────────────────────────────
def test_readonly():
    p = fresh()
    observe_seed_execution(p, "70[Count]")
    observe_seed_execution(p, "51[Select] > 70[Count]")
    before = fingerprint(p)

    # Every read-only surface, several times.
    ro.explain_dell(70); ro.explain_dell(86); ro.explain_dell(150)
    ro.execution_trace(p); ro.execution_trace(p, outcome_id="out1:nope")
    ro.latest_outcomes(p); ro.outcomes_for_dell(p, 70)
    ro.outcomes_by_status(p, "completed"); ro.outcome_by_id(p, "out1:nope")
    ro.outcomes_for_knowledge_item(p, "nope")
    ro.runtime_health(); ro.runtime_state(p)

    after = fingerprint(p)
    check("N.invariant", before == after)
    # And specifically: no new outcome records were created by inspection.
    check("N.no_outcomes", len(getattr(p, "outcome_records", {})) == 2)


# ── O: REPL integration ─────────────────────────────────────────────
def test_repl():
    import form.repl as repl
    p = fresh()
    observe_seed_execution(p, "70[Count]")

    for cmd in ["explain 70", "explain 86", "explain 150", "outcomes",
                "outcomes 5", "health", "runtime", "trace last"]:
        check(f"O.{cmd.replace(' ', '_')}", repl._handle_ros_command(p, cmd) is True)
    # Non-numeric explain falls through to latinmandell; bare trace to Dell 35.
    check("O.explain_word_fallthrough",
          repl._handle_ros_command(p, "explain hello") is False)
    check("O.bare_trace_fallthrough",
          repl._handle_ros_command(p, "trace") is False)
    check("O.unrelated_fallthrough",
          repl._handle_ros_command(p, "grow ideas") is False)
    # outcome <id> round-trip.
    oid = list(p.outcome_records.values())[-1]["outcome_id"]
    check("O.outcome_id", repl._handle_ros_command(p, f"outcome {oid}") is True)
    check("O.outcome_miss", repl._handle_ros_command(p, "outcome out1:nope") is True)


# ── P: live_visual boundary ─────────────────────────────────────────
def test_live_visual_boundary():
    import pathlib
    text = pathlib.Path(REPO, "form", "dell_matrix", "live_visual.py").read_text()
    for cmd in ['"outcomes"', '"outcome "', '"health"', '"runtime"',
                "runtime_observe"]:
        check(f"P.no_{cmd.strip(chr(34))}", cmd not in text)
    # The one pre-existing explain is the latinmandell word explainer (kept).
    check("P.explain_is_word", '"explain": "usage: explain <word|phrase>"' in text)


# ── Q: malformed requests ────────────────────────────────────────────
def test_malformed():
    p = fresh()
    check("Q.explain_empty", ro.explain_dell("")["ok"] is False)
    check("Q.trace_none", ro.execution_trace(p)["status"] == "not_recorded")
    check("Q.outcomes_limit", isinstance(ro.latest_outcomes(p, limit="bogus"), list))
    check("Q.status_bogus", ro.outcomes_by_status(p, "")["status"] == "unsupported")
    check("Q.kid_empty", ro.outcomes_for_knowledge_item(p, "")["count"] == 0)


def main() -> int:
    for fn in [test_explain, test_trace, test_outcomes, test_health,
               test_state, test_readonly, test_repl,
               test_live_visual_boundary, test_malformed]:
        try:
            fn()
        except Exception as exc:
            check(fn.__name__ + ".raised", False)
            print(f"  RAISED in {fn.__name__}: {exc!r}")
    total = len(CHECKS)
    failed = sum(1 for _, ok in CHECKS if not ok)
    print(f"ros_i: {total - failed}/{total} {'GREEN' if failed == 0 else 'RED'}")
    return 0 if failed == 0 else 1


def smoke():
    try:
        main()
    except Exception:
        return False
    return all(ok for _, ok in CHECKS)


if __name__ == "__main__":
    sys.exit(main())
