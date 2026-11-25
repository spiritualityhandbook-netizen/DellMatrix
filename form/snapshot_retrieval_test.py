"""Snapshot retrieval reachability — Q-SC.3 as amended (Director
ruling, Gmail 1a1bb7d8dde15388, 2026-11-08 08:08 CST).

Defect (measured at base): AgentCoordinator.snapshot_for slices the
FIRST 200 Nursery proposals and FIRST 200 Plane units with no
coverage counts, no truncation marker, no source identity, and no
retrieval path — any authorized entry beyond position 200 is
unreachable to the docked semantic verbs (unknown_target), exactly
as proven live on the Email Matrix field (DistroKid target at
position 219).

Contract pinned by this suite (proposal DIRECTOR_PROPOSAL_
SNAPSHOT_COVERAGE_2026-11-08 + the Director's amendments):
- T1 a caller-named beyond-slice target resolves through ONE
  retrieval round and the verb lands PENDING;
- T2 a relation may span windows (one parent in-slice, one
  retrieved) with parent links preserved exactly;
- T3 every snapshot carries a truthful coverage block (separate
  totals per collection, returned counts, truncated flag);
- T4 retrieved entries pass the same outward sanitization as the
  snapshot (a grant-handle canary never reaches the model);
- T5 retrieval is authority-bound: unknown and cross-owner ids
  return absent; >16 ids is a hard-bound refusal with no partial
  result; duplicate ids dedupe to one entry;
- T6 lifecycle parity: a beyond-slice entry is treated exactly as
  its in-slice twin (status visibility + verb outcome);
- T7 source identity is a trustworthy cross-process identity of
  the source content + lifecycle (stable for identical state,
  changes on mutation, equal across processes/restarts — NOT a
  runtime counter), and incorporation revalidates: a target
  deleted after it became reachable is refused honestly, never
  landed on stale data.

Controls: in-slice comprehend lands PENDING; a small field's
snapshot is complete and untruncated.
"""
from __future__ import annotations

import glob
import json
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from form.open import Program  # noqa: E402
from form.dell_matrix import inference_dock as idock  # noqa: E402
from form.dell_matrix.agent_coordinator import (  # noqa: E402
    new_coordinator, CoordinatorError)

RESULTS = []
CANARY = "grant_" + "a1b2c3d4" * 4  # recognized handle format


def _rec(name, cond, detail=""):
    RESULTS.append((name, bool(cond), str(detail)[:200]))


def _cleanup(owner):
    base = os.path.join(os.path.dirname(__file__), "state")
    for pat in (f"program_{owner}.json", f"nursery_{owner}.json",
                f"checkpoint_{owner}_*", f"confirm_{owner}.journal.json",
                f"checkpoint_{owner}.journal.json"):
        for f in glob.glob(os.path.join(base, pat)):
            os.remove(f)
    for d in glob.glob(os.path.join(base, f"ideas_{owner}*")):
        if os.path.isdir(d):
            shutil.rmtree(d)


class ScriptedJudge:
    """Deterministic judge answering from the [targets] payload."""

    last_actual_model = "judge:snapretrieval"

    def __init__(self):
        self.calls = 0
        self.prompts = []

    def generate(self, prompt, *, timeout_s, max_chars):
        self.calls += 1
        self.prompts.append(prompt)
        targets = []
        if "[targets]\n" in prompt:
            blob = prompt.split("[targets]\n", 1)[1].split("\n\n[", 1)[0]
            targets = json.loads(blob)
        ids = [t.get("uid") or t.get("pid") for t in targets]
        labels = [t.get("label", "") for t in targets]
        if prompt.startswith("[verb:comprehend]") and targets:
            t = targets[0]
            detail = str(t.get("detail", ""))
            return json.dumps({
                "label": f"Meaning: {labels[0]}",
                "words": f"In plain terms, {labels[0]} means: {detail}",
                "detail": (f"Claim: {detail}\n"
                           "Mechanism: the means the entry itself "
                           "describes.\n"
                           "Implications: its stated goals follow.\n"
                           "Assumptions: premises in its own text.\n"
                           "Unknowns: what its text leaves open."),
                "goals": [],
                "reason": "Breakdown drawn only from the entry's own "
                          "text.",
                "parents": ids})
        return json.dumps({
            "label": "Relation: " + " + ".join(labels),
            "words": "synthesized from all shown parents",
            "detail": "Authored from every parent's substance.",
            "goals": [],
            "reason": "All shown parents are genuinely related.",
            "parents": ids})


def _judge_session(p, owner, judge, coord, subject="agent-a"):
    s = idock.DockedSession(
        p, subject, owner, "judge", judge, "judge:snapretrieval",
        30, 8000, 8000, task="propose")
    object.__setattr__(s, "_coordinator", coord)
    return s


def _retrieve(coord, subject, ids):
    """Call retrieve_for if it exists; return (result, error)."""
    fn = getattr(coord, "retrieve_for", None)
    if fn is None:
        return None, "no retrieve_for"
    try:
        return fn(subject, ids), None
    except Exception as exc:  # CoordinatorError expected on bounds
        return None, f"{type(exc).__name__}: {exc}"


def _child_snapshot(owner, subject="agent-a"):
    code = (
        "import json,sys;"
        "sys.path.insert(0, '.');"
        "from form.open import Program;"
        "from form.dell_matrix.agent_coordinator import new_coordinator;"
        f"p=Program(owner={owner!r});"
        "c=new_coordinator(p);"
        f"c.register_agent({subject!r});"
        "s=c.snapshot_for(" + repr(subject) + ");"
        "print(json.dumps({'identity': s.get('source_identity'),"
        " 'coverage': s.get('coverage')}))")
    r = subprocess.run([sys.executable, "-c", code],
                       capture_output=True, text=True, timeout=300,
                       cwd=os.path.join(os.path.dirname(__file__), ".."))
    if r.returncode != 0:
        return None, r.stderr[-300:]
    return json.loads(r.stdout.strip().splitlines()[-1]), ""


def smoke() -> bool:
    owners = ["SnapRetrieval", "SnapRetrievalOther"]
    for o in owners:
        _cleanup(o)
    try:
        return _run(owners)
    finally:
        for o in owners:
            _cleanup(o)


def _run(owners):
    o, o2 = owners
    p = Program(owner=o)
    coord = new_coordinator(p)
    coord.register_agent("agent-a")

    # --- build a 250-proposal field ------------------------------
    ids = []
    for i in range(250):
        pr = p.nursery.add(
            f"Field Entry {i:03d}", words=f"entry{i}",
            detail=f"detail for entry {i} about shared topic alpha",
            goals=["g"])
        ids.append(pr.id)
    in_slice = ids[10]
    beyond = ids[239]

    # Planted beyond-slice fixtures: sanitization canary (idx 245)
    # and a rejected lifecycle twin (idx 246); in-slice rejected
    # twin at idx 5.
    canary = p.nursery.add(
        "Canary Entry", words="canary",
        detail=f"the credential handle is {CANARY} keep it safe",
        goals=[])
    twin_out = p.nursery.add("Twin Entry", words="twin",
                             detail="twin detail", goals=[])
    p.nursery.reject(ids[5])
    p.nursery.reject(twin_out.id)

    total_ideas = len(p.nursery.proposals)

    # --- controls -------------------------------------------------
    judge = ScriptedJudge()
    s = _judge_session(p, o, judge, coord)
    n0 = len(p.nursery.proposals)
    r = s.comprehend(in_slice)
    prop = p.nursery.proposals.get(r.get("pid", ""))
    _rec("control.in_slice_comprehend_lands_pending",
         r.get("ok") and prop is not None
         and prop.status == "pending"
         and len(p.nursery.proposals) == n0 + 1, str(r)[:140])

    snap = coord.snapshot_for("agent-a")

    # --- T3 coverage truth ----------------------------------------
    cov = snap.get("coverage") or {}
    _rec("T3.coverage_block_exact",
         cov.get("ideas_total") == total_ideas + 1
         and cov.get("ideas_returned") == 200
         and cov.get("units_total") == len(p.cube.session.plane.units)
         and cov.get("units_returned")
         == len(snap.get("units", []))
         and cov.get("truncated") is True,
         f"cov={cov} total_ideas={total_ideas + 1}")

    # --- T7 source identity: stable + cross-process ---------------
    identity = snap.get("source_identity")
    snap2 = coord.snapshot_for("agent-a")
    _rec("T7.identity_present_and_stable",
         isinstance(identity, str) and len(identity) >= 16
         and snap2.get("source_identity") == identity,
         f"identity={identity!r}")
    child, err = _child_snapshot(o)
    _rec("T7.identity_equal_across_processes",
         child is not None and child.get("identity") == identity
         and (child.get("coverage") or {}).get("ideas_total")
         == total_ideas + 1,
         f"child={child} err={err[:120]}")

    # --- T1 reachability ------------------------------------------
    n0 = len(p.nursery.proposals)
    r = s.comprehend(beyond)
    prop = p.nursery.proposals.get(r.get("pid", ""))
    _rec("T1.beyond_slice_target_reachable",
         r.get("ok") and prop is not None
         and prop.status == "pending"
         and list(prop.parents) == [beyond]
         and len(p.nursery.proposals) == n0 + 1, str(r)[:140])

    # --- T2 cross-window relation ----------------------------------
    n0 = len(p.nursery.proposals)
    r = s.synthesize([in_slice, beyond])
    prop = p.nursery.proposals.get(r.get("pid", ""))
    _rec("T2.cross_window_synthesize_parents_exact",
         r.get("ok") and prop is not None
         and prop.status == "pending"
         and set(prop.parents) == {in_slice, beyond}
         and len(p.nursery.proposals) == n0 + 1, str(r)[:140])

    # --- T4 sanitization parity on retrieval -----------------------
    res, err = _retrieve(coord, "agent-a", [canary.id])
    entries = (res or {}).get("entries", []) if isinstance(res, dict) \
        else []
    blob = json.dumps(entries)
    _rec("T4.retrieved_entry_sanitized",
         err is None and len(entries) == 1
         and entries[0].get("source") == "retrieved"
         and CANARY not in blob,
         f"err={err} entries={len(entries)} canary_leaked={CANARY in blob}")

    # --- T5 authority + hard bounds --------------------------------
    res, err = _retrieve(coord, "agent-a", ["no_such_id_xyz"])
    _rec("T5.unknown_id_absent",
         err is None and isinstance(res, dict)
         and res.get("entries") == []
         and "no_such_id_xyz" in (res.get("absent") or []),
         f"err={err} res={res}")
    p2 = Program(owner=o2)
    foreign = p2.nursery.add("Foreign Entry", words="f",
                             detail="foreign", goals=[])
    res, err = _retrieve(coord, "agent-a", [foreign.id])
    _rec("T5.cross_owner_id_absent",
         err is None and isinstance(res, dict)
         and res.get("entries") == []
         and foreign.id in (res.get("absent") or []),
         f"err={err} res={res}")
    many = [f"fake_{i}" for i in range(17)]
    res, err = _retrieve(coord, "agent-a", many)
    _rec("T5.over_bound_refused_no_partial",
         err is not None and "no retrieve_for" not in str(err)
         and res is None, f"err={err} res={res}")
    res, err = _retrieve(coord, "agent-a", [beyond, beyond])
    entries = (res or {}).get("entries", []) if isinstance(res, dict) \
        else []
    _rec("T5.duplicate_ids_deduped",
         err is None and len(entries) == 1
         and entries[0].get("pid") == beyond,
         f"err={err} n={len(entries)}")

    # --- T6 lifecycle parity (rejected twins) -----------------------
    snap_now = coord.snapshot_for("agent-a")
    in_twin = [e for e in snap_now.get("ideas", [])
               if e.get("pid") == ids[5]]
    res, err = _retrieve(coord, "agent-a", [twin_out.id])
    entries = (res or {}).get("entries", []) if isinstance(res, dict) \
        else []
    _rec("T6.retrieved_status_matches_in_slice_twin",
         len(in_twin) == 1 and in_twin[0].get("status") == "rejected"
         and err is None and len(entries) == 1
         and entries[0].get("status") == in_twin[0].get("status"),
         f"in={in_twin} err={err} entries={entries}")
    r_in = s.comprehend(ids[5])
    r_out = s.comprehend(twin_out.id)
    _rec("T6.verb_outcome_parity_for_twins",
         bool(r_in.get("ok")) == bool(r_out.get("ok")),
         f"in_ok={r_in.get('ok')} out_ok={r_out.get('ok')}")

    # --- T7 mutation sensitivity + deletion revalidation ------------
    before = coord.snapshot_for("agent-a").get("source_identity")
    extra = p.nursery.add("Mutation Entry", words="m",
                          detail="mutation", goals=[])
    after = coord.snapshot_for("agent-a").get("source_identity")
    _rec("T7.identity_changes_on_mutation",
         isinstance(before, str) and isinstance(after, str)
         and before != after, f"before={before!r} after={after!r}")

    victim = ids[238]
    r = s.comprehend(victim)
    reachable_first = bool(r.get("ok"))
    p.nursery.reject(victim)
    p.nursery.clear_rejected()
    n0 = len(p.nursery.proposals)
    r2 = s.comprehend(victim)
    res, err = _retrieve(coord, "agent-a", [victim])
    _rec("T7.deleted_target_refused_not_stale",
         reachable_first and not r2.get("ok")
         and len(p.nursery.proposals) == n0
         and err is None and isinstance(res, dict)
         and res.get("entries") == []
         and victim in (res.get("absent") or []),
         f"reachable_first={reachable_first} r2={str(r2)[:100]}")

    # --- T3 small field: complete + untruncated ---------------------
    snap_small = None
    coord2 = new_coordinator(p2)
    coord2.register_agent("agent-a")
    snap_small = coord2.snapshot_for("agent-a")
    cov2 = snap_small.get("coverage") or {}
    _rec("T3.small_field_untruncated",
         cov2.get("ideas_total") == len(p2.nursery.proposals)
         and cov2.get("ideas_returned") == len(p2.nursery.proposals)
         and cov2.get("truncated") is False,
         f"cov2={cov2}")

    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'} {name} :: {detail}")
    print(f"SNAPSHOT_RETRIEVAL: {passed}/{len(RESULTS)}")
    return passed == len(RESULTS)


def main() -> int:
    return 0 if smoke() else 1


if __name__ == "__main__":
    raise SystemExit(main())
