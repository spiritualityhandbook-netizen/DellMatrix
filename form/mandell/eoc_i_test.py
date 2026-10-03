#!/usr/bin/env python3
"""EOC-I: Execution Observation Convergence — dedicated control suite.

Closes the observation discontinuity: raw Mandell execution is now
observed through the existing Outcome V1 ledger via the observation
adapter (form/mandell/execution_observer.py), without a new executor,
new router, new ledger, new receipt format, or new truth authority.

LAW: EXECUTION != OUTCOME; OUTCOME != TRUTH;
     OBSERVATION MUST NOT CHANGE EXECUTION SEMANTICS.

Controls:
  A  raw Core-I representative (identity/mutation/checkpoint/rollback/
     knowledge) — one outcome each, honest provenance
  B  all-49 raw Core-II executability — one outcome each
  C  all nine raw flows observed
  D  Dell 99: canonical refusal, raw execution, raw observation
  E  completed / failed / blocked / skipped / partial-failure
  F  parser refusal, unknown Dell, malformed input
  G  control-consumed nodes (no invented events)
  H  double-capture prevention (wrapper/leaf/nested/projection/benchmark)
  I  canonical English vs canonical explicit Dell vs raw Mandell
  J  Outcome V1 identity + ledger singularity
  K  persistence round-trip preserves observed outcomes
  L  literal two-process restore of observed outcomes
  M  checkpoint/generation coherence for raw Dell 27
"""
from __future__ import annotations

import os
import subprocess
import sys
import uuid

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)

from form.open import Program  # noqa: E402
from form.mandell.execution_observer import observe_seed_execution  # noqa: E402
from form.mandell import registry  # noqa: E402

CHECKS = []
STATE_DIR = os.path.join(REPO, "form", "state")


def check(name: str, cond: bool) -> None:
    CHECKS.append((name, bool(cond)))
    if not cond:
        print(f"  FAIL: {name}")


def fresh() -> Program:
    return Program()


def records(p: Program):
    return getattr(p, "outcome_records", {}) or {}


def last_record(p: Program):
    recs = records(p)
    return list(recs.values())[-1] if recs else {}


def wipe_owner(owner: str) -> None:
    import pathlib
    for f in pathlib.Path(STATE_DIR).glob(f"*{owner}*"):
        try:
            if f.is_file():
                f.unlink()
        except OSError:
            pass


# ── A: raw Core-I representative ──────────────────────────────────────
def test_a():
    p = fresh()
    n0 = len(records(p))
    r = observe_seed_execution(p, "02[Grow]")
    recs = records(p)
    check("A1.one_record", len(recs) - n0 == 1)
    last = last_record(p)
    check("A1.identity", r["ok"] is True and last["operation"] == "persona"
          and last["dell"] == 2 and last["result"] == "completed")
    check("A1.observation_flag", last.get("outcome_is_observation") is True
          and last.get("outcome_version") == 1)

    p = fresh(); n0 = len(records(p))
    r = observe_seed_execution(p, "04[Adapt]")
    check("A2.mutation", r["ok"] is True and len(records(p)) - n0 == 1
          and last_record(p)["result"] == "completed")

    owner = f"eoc27_{uuid.uuid4().hex[:8]}"
    p = Program(owner=owner); n0 = len(records(p))
    r = observe_seed_execution(p, "27[Checkpoint]")
    check("A3.checkpoint_ok", r["ok"] is True)
    check("A3.checkpoint_record", len(records(p)) - n0 == 1
          and last_record(p)["dell"] == 27
          and last_record(p)["result"] == "completed")
    r2 = observe_seed_execution(p, "28[Rollback]")
    check("A4.rollback", isinstance(r2, dict) and len(records(p)) - n0 == 2
          and last_record(p)["dell"] == 28)
    wipe_owner(owner)

    p = fresh(); n0 = len(records(p))
    r = observe_seed_execution(p, "37[Nurture] :: raw knowledge probe")
    check("A5.nurture", r["ok"] is True and len(records(p)) - n0 == 1)
    # Honest provenance: the arm supplied no selected_details, so the
    # ledger records [] rather than fabricating knowledge.
    check("A5.honest_empty", last_record(p)["knowledge"] == [])
    observe_seed_execution(p, "70[Count]")
    check("A5.no_contamination", last_record(p)["knowledge"] == []
          and last_record(p)["operation"] == "count")


# ── B: all-49 raw Core-II ─────────────────────────────────────────────
def test_b():
    for n in range(51, 100):
        rec = registry.get_dell(n) or {}
        name = rec.get("name") or f"Dell{n}"
        p = fresh()
        n0 = len(records(p))
        try:
            observe_seed_execution(p, f"{n}[{name}]")
        except Exception:
            pass
        recs = records(p)
        check(f"B.dell{n}.one_record", len(recs) - n0 == 1)
        last = list(recs.values())[-1] if len(recs) > n0 else {}
        check(f"B.dell{n}.identity", last.get("dell") == n
              and last.get("outcome_is_observation") is True)


# ── C: all nine raw flows ─────────────────────────────────────────────
def test_c():
    flows = [">", ">>", ">>>", "::", ":", ":>", "<:", "<:>", "<<[Delta]"]
    for op in flows:
        p = fresh(); n0 = len(records(p))
        seed = "70[Count] :: lbl" if op == "::" else f"51[Select] {op} 70[Count]"
        try:
            observe_seed_execution(p, seed)
        except Exception:
            pass
        check(f"C.flow_{op}.observed", len(records(p)) - n0 == 1)


# ── D: Dell 99 ────────────────────────────────────────────────────────
def test_d():
    from form.mandell.translate import translate
    from form.mandell.semantic_router import route_intent

    p = fresh(); n0 = len(records(p))
    intent = translate("dell 99")
    res = route_intent(p, intent)
    check("D1.canonical_refusal",
          res.routed is False
          and "intentionally_raw_only" in str(res.error or "")
          and len(records(p)) - n0 == 1)  # the refusal itself is observed (existing contract)

    p = fresh(); n0 = len(records(p))
    r = observe_seed_execution(p, "99[Compose] :: Path=51")
    recs = records(p)
    check("D2.raw_executes", r["ok"] is True)
    check("D3.raw_observed_once", len(recs) - n0 == 1
          and last_record(p)["dell"] == 99
          and last_record(p)["operation"] == "compose"
          and last_record(p)["result"] == "completed")

    # Canonical English still cannot reach 99 (observation grants nothing).
    p = fresh()
    res = route_intent(p, translate("compose"))
    check("D4.english_still_refused", res.routed is False)


# ── E: completed / failed / blocked / skipped / partial ───────────────
def test_e():
    p = fresh(); n0 = len(records(p))
    observe_seed_execution(p, "70[Count]")
    check("E1.completed", last_record(p)["result"] == "completed"
          and len(records(p)) - n0 == 1)

    p = fresh(); n0 = len(records(p))
    r = observe_seed_execution(p, "86[Delete]")
    check("E2.failed", r["ok"] is False
          and last_record(p)["result"] == "failed"
          and len(records(p)) - n0 == 1)

    p = fresh(); n0 = len(records(p))
    r = observe_seed_execution(p, "not a seed at all")
    check("E3.blocked_parse", r["ok"] is False
          and last_record(p)["result"] == "blocked"
          and last_record(p)["operation"] == "parse"
          and len(records(p)) - n0 == 1)

    p = fresh(); n0 = len(records(p))
    r = observe_seed_execution(p, "999[Omega] > 70[Count]")
    # DIRECTOR DECISION 1 (gate R1): a skipped atom is ok=False; the chain
    # continues per policy but the aggregate is honest (ok=False, partial).
    check("E4.skipped", r["ok"] is False and 999 in (r.get("chain_skipped") or [])
          and last_record(p)["result"] == "failed"
          and last_record(p)["partial_completion"] is True
          and len(records(p)) - n0 == 1)

    p = fresh(); n0 = len(records(p))
    r = observe_seed_execution(p, "51[Select] > 86[Delete]")
    atoms = [(a.get("dell"), a.get("ok")) for a in (r.get("atom_results") or [])]
    check("E5.partial", r["ok"] is False and atoms == [(51, True), (86, False)]
          and last_record(p)["result"] == "failed"
          and len(records(p)) - n0 == 1)


# ── F: parser refusal / unknown Dell / malformed ──────────────────────
def test_f():
    for name, seed in [("F1.unknown_dell", "150[X]"),
                       ("F2.unbalanced", "70[Count"),
                       ("F3.empty", "")]:
        p = fresh(); n0 = len(records(p))
        r = observe_seed_execution(p, seed)
        check(f"{name}.observed_blocked", r["ok"] is False
              and len(records(p)) - n0 == 1
              and last_record(p)["result"] == "blocked")


# ── G: control-consumed nodes ─────────────────────────────────────────
def test_g():
    p = fresh(); n0 = len(records(p))
    r = observe_seed_execution(p, "40[TokenCount] >>> 70[Count]")
    msgs = " ".join(r.get("messages") or [])
    check("G.consumed", r["ok"] is True
          and 70 in (r.get("chain_skipped") or [])
          and len(records(p)) - n0 == 1
          and last_record(p)["result"] == "completed")
    check("G.no_invention", "TokenCount" in msgs)  # existing evidence only


# ── H: double-capture prevention ──────────────────────────────────────
def test_h():
    from form.mandell.translate import translate
    from form.mandell.semantic_router import route_intent

    # H1: routed path captures exactly once (wrapper; adapter not involved).
    p = fresh(); n0 = len(records(p))
    route_intent(p, translate("dell 70"))
    check("H1.routed_once", len(records(p)) - n0 == 1)

    # H2: raw chain with Core-I leaf inside captures exactly once.
    p = fresh(); n0 = len(records(p))
    observe_seed_execution(p, "02[Grow] > 70[Count]")
    check("H2.chain_once", len(records(p)) - n0 == 1)

    # H3: nested Dell 99 composition captures exactly once.
    p = fresh(); n0 = len(records(p))
    observe_seed_execution(p, "99[Compose] :: Path=51")
    check("H3.nested_once", len(records(p)) - n0 == 1)

    # H4: projection (cheat_project) is never observed.
    from form.mandell.canonical import cheat_project
    p = fresh(); n0 = len(records(p))
    try:
        cheat_project(p, "70[Count]")
    except Exception:
        pass
    check("H4.projection_silent", len(records(p)) - n0 == 0)

    # H5: benchmark probes are never observed.
    from form.mandell import language
    p = fresh(); n0 = len(records(p))
    try:
        language.metrics(p)
    except Exception:
        pass
    check("H5.benchmark_silent", len(records(p)) - n0 == 0)


# ── I: canonical explicit Dell vs raw Mandell ────────────────────────────
# NOTE: NATURAL_ENGLISH is intentionally empty by SSI-I design — there
# are no loose prose aliases. The canonical English form IS "dell 70".
def test_i():
    from form.mandell.translate import translate
    from form.mandell.semantic_router import route_intent

    p2 = fresh()
    route_intent(p2, translate("dell 70"))
    r_dell = last_record(p2)

    p3 = fresh()
    observe_seed_execution(p3, "70[Count]")
    r_raw = last_record(p3)

    check("I.semantic_consistency",
          r_dell["operation"] == r_raw["operation"] == "count"
          and r_dell["dell"] == r_raw["dell"] == 70
          and r_dell["result"] == r_raw["result"] == "completed")
    check("I.all_observed",
          r_dell.get("outcome_is_observation") is True
          and r_raw.get("outcome_is_observation") is True)
    # Natural English has no alias for 70 (design invariant, not a gap).
    p4 = fresh()
    res = route_intent(p4, translate("count"))
    check("I.natural_empty_by_design", res.routed is False)


# ── J: Outcome V1 identity + ledger singularity ───────────────────────
def test_j():
    p = fresh()
    observe_seed_execution(p, "70[Count]")
    observe_seed_execution(p, "51[Select]")
    recs = list(records(p).values())
    check("J1.identity", all(r.get("outcome_version") == 1 for r in recs)
          and all(str(r.get("outcome_id", "")).startswith("out1:") for r in recs))
    ids = [r["outcome_id"] for r in recs]
    seqs = [r["outcome_seq"] for r in recs]
    check("J2.singularity", len(set(ids)) == len(ids) == 2
          and sorted(seqs) == seqs and len(set(seqs)) == 2)

# ── K: persistence round-trip ─────────────────────────────────────────
def test_k():
    from form.persist import load as persist_load
    owner = f"eoct_{uuid.uuid4().hex[:8]}"
    p = Program(owner=owner)
    observe_seed_execution(p, "70[Count]")
    oid = last_record(p)["outcome_id"]
    p.save()
    # The ledger lives in the program payload; restore via persist load
    # (same as DCC-XX control K), not nursery-only Program.load().
    p2 = persist_load(owner)
    recs = records(p2)
    check("K.roundtrip", oid in recs
          and recs[oid]["operation"] == "count"
          and recs[oid].get("outcome_is_observation") is True)
    wipe_owner(owner)


# ── L: literal two-process restore ────────────────────────────────────
def test_l():
    owner = f"eocx_{uuid.uuid4().hex[:8]}"
    build = (
        "import sys; sys.path.insert(0, %r)\n"
        "from form.open import Program\n"
        "from form.mandell.execution_observer import observe_seed_execution\n"
        "p = Program(owner=%r)\n"
        "observe_seed_execution(p, '70[Count]')\n"
        "p.save()\n"
        "print('PID:' + str(__import__('os').getpid()))\n"
        "print('OID:' + list(p.outcome_records.values())[-1]['outcome_id'])\n" % (REPO, owner)
    )
    r1 = subprocess.run([sys.executable, "-c", build], capture_output=True,
                        text=True, timeout=120, cwd=REPO)
    pid_a = [l for l in r1.stdout.splitlines() if l.startswith("PID:")]
    oid_a = [l for l in r1.stdout.splitlines() if l.startswith("OID:")]
    check("L1.build_ok", r1.returncode == 0 and pid_a and oid_a)

    verify = (
        "import sys; sys.path.insert(0, %r)\n"
        "from form.persist import load as persist_load\n"
        "p = persist_load(%r)\n"
        "recs = p.outcome_records or {}\n"
        "print('PID:' + str(__import__('os').getpid()))\n"
        "print('FOUND:' + str(%r in recs))\n"
        "print('OBS:' + str(recs.get(%r, {}).get('outcome_is_observation')))\n"
        % (REPO, owner, oid_a[0][4:], oid_a[0][4:])
    )
    r2 = subprocess.run([sys.executable, "-c", verify], capture_output=True,
                        text=True, timeout=120, cwd=REPO)
    pid_b = [l for l in r2.stdout.splitlines() if l.startswith("PID:")]
    check("L2.restore_ok", r2.returncode == 0 and "FOUND:True" in r2.stdout
          and "OBS:True" in r2.stdout)
    check("L3.distinct_processes", pid_a and pid_b
          and pid_a[0] != pid_b[0])
    wipe_owner(owner)


# ── M: checkpoint/generation coherence ───────────────────────────────
def test_m():
    from form.mandell.checkpoint_generation import current_generation_id
    owner = f"eocm_{uuid.uuid4().hex[:8]}"
    p = Program(owner=owner)
    observe_seed_execution(p, "27[Checkpoint]")
    last = last_record(p)
    committed = current_generation_id(owner)
    check("M.coherence", last["dell"] == 27
          and last["result"] == "completed"
          and last.get("generation_id") == committed
          and committed is not None)
    wipe_owner(owner)


def main() -> int:
    for fn in [test_a, test_b, test_c, test_d, test_e, test_f, test_g,
               test_h, test_i, test_j, test_k, test_l, test_m]:
        try:
            fn()
        except Exception as exc:  # never let one control abort the suite
            check(fn.__name__ + ".raised", False)
            print(f"  RAISED in {fn.__name__}: {exc!r}")
    total = len(CHECKS)
    failed = sum(1 for _, ok in CHECKS if not ok)
    print(f"eoc_i: {total - failed}/{total} {'GREEN' if failed == 0 else 'RED'}")
    return 0 if failed == 0 else 1


def smoke():
    try:
        main()
    except Exception:
        return False
    return all(ok for _, ok in CHECKS)


if __name__ == "__main__":
    sys.exit(main())
