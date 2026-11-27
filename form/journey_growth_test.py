#!/usr/bin/env python3
"""Part VII / GP-E27 — journey harness family 7: J-09 Resonance to
Nursery, J-14 Scoped growth.

Written failing-first at code stage and registered in
form/regress.py LIST in the same commit (omitted-entry law).

Contracts — Edition 1 file 06 (06_JOURNEY_ACCEPTANCE.md), executed
verbatim:

  J-09 Resonance to Nursery: "Two active eligible Ideas yield
  explainable pair score and a distinct pending candidate; human
  accepts with source-bound record." Failure oracle: "Faded/
  superseded/sandboxed excluded per policy; no fake 'vesica'
  geometry, no automatic graph edge from score; reload accepted
  relationship and provenance."

  J-14 Scoped growth: "Select named eligible idea scope and
  grow; only that scope receives the new candidate and logged
  effect. Bare grow must disclose mode." Failure oracle:
  "Cross-wall, faded, superseded, stopped and partial evidence
  cases; accepted candidate does not silently mutate unrelated
  live Ideas."

Execution tier: PUBLIC_ENTRY_PATH — every journey action runs in
a literal `python3 -m form.repl` subprocess against a per-run
isolated owner; state comparison after cold reload uses the
persistence loader and the SemanticGraph loader (reloaded vs
reloaded, never in-memory vs reloaded). No fixture seeding: the
J-14 destination owner's eligible knowledge is manufactured
through the public path itself (exchange export from a source
owner, exchange import, human confirm) — the only public route
by which a confirmed, parentless (dependency-valid) knowledge
record arises, as the probes below establish.

Grounded behavior (each expectation verified first-hand in
scratch-owner probes, 2026-11-21, before this suite was written):
  - `grow ideas` over the two word-sharing Harbor ideas yields
    the [new] cross candidate with the pair score explained on
    the review face: "aff=0.674" and "reason: Solstice
    harm=0.76 goals=0.02 hs=0.42 gcoh=0.00"; `lineage <pid>`
    repeats "affinity: 0.674" with both parents and "status:
    pending". The candidate is a distinct new ID, pending, not a
    live unit.
  - The canonical SemanticGraph holds ZERO entries before the
    grow, after the grow, and after the confirm: the pair score
    writes no graph edge (and no 'vesica' geometry record — the
    graph is the only canonical relationship store), and the
    accepted relationship lives in the unit's lineage + the
    proposal record. After confirm, the proposal record keeps
    origin "growth:token", the full Solstice reason string and
    affinity 0.674 — the source-bound record — durable across
    cold reload.
  - `fade harbor_forge` prints "Faded: harbor_forge (use
    'unfade harbor_forge' to restore)"; the next grow reports
    "+0 new" and no proposal anywhere is parented by the faded
    unit (faded units contribute 0.0 affinity by policy).
  - Supersession at the public path acts on nursery-born
    records: `supersede idea <unconfirmed-unit-id>` refuses
    "unknown_predecessor". Confirming the cross candidate first
    makes it supersedeable: "Superseded <pid> with <succ-id>",
    the predecessor proposal's lifecycle_state reads
    "superseded" with superseded_by_id set; the next grow
    parents NO pending proposal by the superseded unit, while
    the successor unit itself grows crosses — the exclusion is
    the state, not a broken grow.
  - Both parents boxed in DIFFERENT boxes before the grow:
    "+0 new +0 evolved", nursery empty (GS-4: cross-wall pairs
    are never scored). The same fixtures unboxed score 0.674.
  - `grow using knowledge about <context>` (the contextual /
    scoped grow, Dell 37) selects CONFIRMED knowledge by the
    selection law (STORED > ELIGIBLE > SELECTED > ROUTABLE):
    with nothing confirmed it prints "Eligible: 0, Selected: 0",
    "Reason: no eligible knowledge", "Scope mode: contextual,
    Consumer scope IDs: []", "New proposals: 0" — and grows
    NOTHING; it never silently broadens to the full plane (the
    same state then grows the cross under bare `grow ideas`).
    A confirmed candidate whose parents are unconfirmed direct
    units is dependency-INVALID (DCC-XV) and likewise
    ineligible, disclosed as "Dependency exclusions: 1".
  - Eligible knowledge via the public path: `exchange export
    <proposal-id> <file>` in a source owner, `exchange import
    <file>` in a destination owner lands the record as a
    PENDING proposal with parents [] ("Exchange: imported as
    PENDING proposal <pid> from exchange:growth:token"); human
    confirm lands it as a parentless unit — dependency-valid,
    hence eligible. In the destination: context "harbor"
    selects exactly 1 of 2 eligible ("Eligible: 2, Selected:
    1", scope IDs = the harbor unit alone, "New proposals: 0"
    — a one-unit scope cannot pair, and nothing outside the
    scope grows); a context covering both selects 2 and the
    scoped grow yields exactly one new pending candidate whose
    parents are exactly the two scope units — the built-in
    Welcome unit never appears as a parent, and no live unit's
    record changes.
  - Bare-grow mode disclosure: `grow mode` prints "Grow mode ·
    auto_confirm_grow=OFF"; the bare `grow ideas` receipt
    discloses its full-plane effect ("Ringed growth: +1 new +2
    evolved", "Nursery pending: 3") and every proposal it
    leaves is PENDING (mode OFF — nothing auto-confirmed).

  UNCOVERED at baseline, recorded not smoothed: J-14's
  "stopped" case — no stopped state exists in the growth /
  selection machinery at this head (searches of
  ringed_growth, knowledge_selector, canonical_lifecycle and
  open.py return no stopped state; the claim is "unproven",
  never "not there" — the case is named here so a future
  stopped-state build lands its check in this family). J-14's
  cross-wall / faded / superseded negatives are the same
  mechanisms J-09 exercises; they are proven once, under
  J-09, and not duplicated under J-14.

Baseline posture (plan section 5.1(iii)): this suite runs
against the pre-Parts main as a labeled BASELINE harness proof.
Its grades are evidence about the harness and the current
program, recorded in
director-reports/GRAND_SYNCHRONIZATION_REHEARSAL_2026-11-20.md;
the GP-E27 rehearsal executions proper run against merged
Parts I + II.

Run: python3 -m form.journey_growth_test
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from form.persist import _STATE_DIR, _safe_owner, load as persist_load
from form.mandell.semantic_graph import SemanticGraph

RESULTS = []
_CLEANUP_ERRORS = []
RUN = uuid.uuid4().hex[:8]
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

CA = ("create an idea called Harbor Lantern detail: harbor lantern "
      "craft timber copper kettle song cellar vault goals: keep "
      "the harbor lit")
CB = ("create an idea called Harbor Forge detail: harbor lantern "
      "craft timber copper kettle song forge cellar vault goals: "
      "work the harbor forge")
CC = ("create an idea called Orchard Press detail: orchard apple "
      "cider press barrel autumn harvest goals: press the orchard")
CD = ("create an idea called Orchard Ladder detail: orchard apple "
      "cider ladder barrel autumn harvest goals: climb the orchard")
CROSS_LABEL = "Harbor Lantern × Harbor Forge"
REASON = "Solstice harm=0.76 goals=0.02 hs=0.42 gcoh=0.00"


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))
    print(f"{'PASS' if ok else 'FAIL'} {name} {detail}")


def cleanup(owner):
    safe = _safe_owner(owner)
    if not os.path.isdir(_STATE_DIR):
        return
    for name in os.listdir(_STATE_DIR):
        if safe in name:
            p = os.path.join(_STATE_DIR, name)
            try:
                shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
            except OSError as e:
                _CLEANUP_ERRORS.append(f"{p}: {e}")


def state_files(owner):
    safe = _safe_owner(owner)
    if not os.path.isdir(_STATE_DIR):
        return []
    return sorted(n for n in os.listdir(_STATE_DIR) if safe in n)


def run_repl(owner, lines, load=False, timeout=300):
    args = [sys.executable, "-m", "form.repl", "--owner", owner]
    if load:
        args.append("--load")
    proc = subprocess.run(args, input="\n".join(lines) + "\n",
                          capture_output=True, text=True, cwd=ROOT,
                          timeout=timeout)
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def _unit_fp(u):
    return {
        "label": u.label,
        "words": getattr(u, "words", None),
        "detail": getattr(u, "detail", None),
        "goals": list(getattr(u, "goals", None) or []),
        "parents": list(getattr(u, "parents", None) or []),
        "origin": getattr(u, "origin", None),
        "sandboxed": bool(getattr(u, "sandboxed", False)),
        "sandbox_id": getattr(u, "sandbox_id", None),
    }


def snap(owner):
    """Loader-basis snapshot: unit fingerprints, full proposal
    records, nursery summary."""
    prog = persist_load(owner)
    plane = prog.cube.session.plane
    units = {uid: _unit_fp(u) for uid, u in plane.units.items()}
    props = {}
    for pid, p in prog.nursery.proposals.items():
        props[pid] = {
            "status": p.status,
            "kind": p.kind,
            "parents": list(p.parents or []),
            "origin": p.origin,
            "reason": p.reason,
            "affinity": round(float(p.affinity or 0.0), 3),
            "lifecycle_state": p.lifecycle_state,
            "superseded_by_id": p.superseded_by_id,
        }
    return {"units": units, "props": props,
            "summary": prog.nursery.summary()}


def graph_entries(owner):
    g = SemanticGraph.load(owner)
    return [e.to_dict() for e in g._entries]


def grow_harbor(owner):
    """Create the Harbor pair, grow, list. Returns (rc, out,
    cross_pid)."""
    rc, out = run_repl(owner, [CA, CB, "grow ideas", "proposals",
                               "save", "quit"])
    m = re.search(r"\[new\] (\S+)\n\s+Harbor Lantern", out)
    return rc, out, (m.group(1) if m else None)


def main():
    res_owner = f"JRes{RUN}"
    fade_owner = f"JFade{RUN}"
    sup_owner = f"JSup{RUN}"
    wall_owner = f"JWall{RUN}"
    bare_owner = f"JBare{RUN}"
    src_owner = f"JScopeSrc{RUN}"
    dst_owner = f"JScopeDst{RUN}"
    owners = (res_owner, fade_owner, sup_owner, wall_owner,
              bare_owner, src_owner, dst_owner)
    for o in owners:
        cleanup(o)
    pkt_dir = tempfile.mkdtemp(prefix=f"jgrowth_{RUN}_")
    pkt_h = os.path.join(pkt_dir, "harbor_packet.json")
    pkt_o = os.path.join(pkt_dir, "orchard_packet.json")
    try:
        # Isolation boundary, proven — not assumed (a fresh
        # Program() in this codebase loads persisted state by
        # default; the boundary is the per-run unique owner +
        # verified-empty start).
        check("growth_isolation_boundary_clean_start",
              all(state_files(o) == [] for o in owners),
              "no state files exist for any of the seven per-run "
              "owners before the sessions start")

        # ---------------- J-09: score -> inspect -> accept ------
        check("j09_graph_empty_before_grow",
              graph_entries(res_owner) == [],
              "the canonical graph holds no entries before any "
              "scoring — the baseline the score must not move")
        rc, out, cross = grow_harbor(res_owner)
        check("j09_repl_exit_clean",
              rc == 0 and "Traceback" not in out,
              f"rc={rc} traceback={'Traceback' in out}")
        s = snap(res_owner)
        cp = s["props"].get(cross) or {}
        check("j09_candidate_distinct_pending",
              cross is not None
              and cp.get("status") == "pending"
              and cp.get("kind") == "new"
              and cp.get("parents") == ["harbor_lantern",
                                        "harbor_forge"]
              and cross not in s["units"],
              f"the pair yields a distinct pending candidate "
              f"({cross}) parented by both ideas, not yet a "
              f"live unit")
        check("j09_pair_score_explainable",
              f"aff=0.674 [new] {cross}" in out
              and f"reason: {REASON}" in out,
              "the review face explains the score before any "
              "decision: affinity 0.674 with its components "
              f"({REASON})")
        rc, out = run_repl(res_owner, [f"lineage {cross}", "quit"],
                           load=True)
        check("j09_lineage_repeats_score_and_parents",
              "parents: ['harbor_lantern', 'harbor_forge']" in out
              and "affinity: 0.674" in out
              and "status: pending" in out
              and cp.get("affinity") == 0.674
              and cp.get("reason") == REASON,
              "inspection repeats the same affinity the view "
              "showed, and the stored record carries the same "
              "reason string — one score, three faces, no drift")
        check("j09_score_writes_no_graph_edge",
              graph_entries(res_owner) == [],
              "after scoring, the canonical graph still holds "
              "zero entries: no automatic graph edge from a "
              "score, no 'vesica' geometry record — resonance "
              "is weather, not graph truth")
        rc, out = run_repl(res_owner, [f"confirm {cross}", "save",
                                       "quit"], load=True)
        s = snap(res_owner)
        cu = s["units"].get(cross) or {}
        cp = s["props"].get(cross) or {}
        check("j09_accept_source_bound_record",
              f'Confirmed. "{CROSS_LABEL}" is live.' in out
              and cu.get("label") == CROSS_LABEL
              and cu.get("parents") == ["harbor_lantern",
                                        "harbor_forge"]
              and cu.get("origin") == "confirmed"
              and cp.get("status") == "confirmed"
              and cp.get("origin") == "growth:token"
              and cp.get("reason") == REASON
              and cp.get("affinity") == 0.674,
              "human acceptance lands the unit with both "
              "parents as lineage, and the proposal record "
              "keeps its source binding: origin growth:token, "
              "the full Solstice reason, affinity 0.674")
        rc, out = run_repl(res_owner, ["status", "quit"], load=True)
        s2 = snap(res_owner)
        check("j09_reload_relationship_and_provenance",
              rc == 0 and s2["units"] == s["units"]
              and s2["props"] == s["props"]
              and graph_entries(res_owner) == [],
              "after cold reload the accepted relationship "
              "(lineage) and provenance (origin/reason/affinity) "
              "are identical, and the graph still holds no "
              "score-born edge")

        # ---------------- J-09: faded exclusion -----------------
        rc, out = run_repl(fade_owner, [
            CA, CB, "fade harbor_forge", "grow ideas", "proposals",
            "save", "quit"])
        s = snap(fade_owner)
        check("j09_fade_receipt",
              "Faded: harbor_forge (use 'unfade harbor_forge' "
              "to restore)" in out,
              "the fade is a public, reversible act with its "
              "receipt on the transcript")
        check("j09_faded_pair_never_scores",
              "Ringed growth: +0 new" in out
              and CROSS_LABEL not in out.split("Faded:")[-1]
              and not any("harbor_forge" in (p["parents"])
                          for p in s["props"].values()),
              "with one parent faded the pair never scores: "
              "zero new candidates and no proposal anywhere is "
              "parented by the faded unit (faded contributes "
              "0.0 affinity by policy)")

        # ---------------- J-09: superseded exclusion ------------
        rc, out, scross = grow_harbor(sup_owner)
        rc, out = run_repl(sup_owner, [
            f"confirm {scross}",
            f"supersede idea {scross} with harbor beacon craft "
            f"timber copper signal",
            "save", "quit"], load=True)
        m = re.search(r"Superseded (\S+) with (\S+)", out)
        succ = m.group(2) if m else None
        s = snap(sup_owner)
        sp = s["props"].get(scross) or {}
        check("j09_supersede_receipt_and_state",
              m is not None and m.group(1) == scross
              and succ in s["units"]
              and sp.get("lifecycle_state") == "superseded"
              and sp.get("superseded_by_id") == succ,
              f"the confirmed candidate is superseded by "
              f"{succ}: the predecessor record reads "
              f"lifecycle_state=superseded with the successor "
              f"named, and the successor unit is live")
        rc, out = run_repl(sup_owner, ["grow ideas", "save",
                                       "quit"], load=True)
        s = snap(sup_owner)
        pending = {pid: p for pid, p in s["props"].items()
                   if p["status"] == "pending"}
        check("j09_superseded_never_parent_successor_grows",
              not any(scross in p["parents"]
                      for p in pending.values())
              and any(succ in p["parents"]
                      for p in pending.values()),
              "the next grow parents no pending proposal by "
              "the superseded unit, while the successor unit "
              "itself grows crosses — the exclusion is the "
              "superseded state, not a broken grow")

        # ---------------- J-09: cross-wall exclusion ------------
        rc, out = run_repl(wall_owner, [
            CA, CB,
            "group create Box One", "group create Box Two",
            "group add harbor_lantern to Box One",
            "group add harbor_forge to Box Two",
            "grow ideas", "proposals", "save", "quit"])
        s = snap(wall_owner)
        check("j09_crosswall_pair_never_scored",
              "Ringed growth: +0 new +0 evolved" in out
              and "Nursery is empty." in out
              and s["summary"].get("total") == 0,
              "the same fixtures that score 0.674 unboxed yield "
              "nothing across a wall: GS-4 pair enumeration "
              "never scores a cross-wall pair")

        # ---------------- J-14: scoped door, nothing eligible ---
        rc, out = run_repl(bare_owner, [
            CA, CB, "grow using knowledge about harbor",
            "proposals", "save", "quit"])
        s = snap(bare_owner)
        check("j14_scoped_without_eligible_grows_nothing",
              "Eligible: 0, Selected: 0" in out
              and "Reason: no eligible knowledge" in out
              and "Scope mode: contextual, Consumer scope "
              "IDs: []" in out
              and "New proposals: 0" in out
              and "Nursery is empty." in out
              and s["summary"].get("total") == 0,
              "the scoped grow discloses its empty selection "
              "and grows nothing — it never silently broadens "
              "to the full plane its caller did not name")
        rc, out = run_repl(bare_owner, [
            "grow mode", "grow ideas", "proposals", "save",
            "quit"], load=True)
        s = snap(bare_owner)
        check("j14_bare_grow_discloses_mode",
              "Grow mode · auto_confirm_grow=OFF" in out
              and "Ringed growth: +1 new +2 evolved" in out
              and "Nursery pending: 3" in out
              and s["summary"].get("pending") == 3
              and s["summary"].get("confirmed") == 0,
              "bare grow discloses its mode on its face: the "
              "mode query answers OFF, the receipt states the "
              "full-plane effect, and every proposal it leaves "
              "is PENDING — nothing auto-confirmed")

        # ---------------- J-14: scoped growth, eligible scope ---
        rc, out = run_repl(src_owner, [
            CA, CB, CC, CD, "grow ideas", "proposals", "save",
            "quit"])
        mh = re.search(r"\[new\] (\S+)\n\s+Harbor Lantern", out)
        mo = re.search(r"\[new\] (\S+)\n\s+Orchard Press", out)
        hpid = mh.group(1) if mh else None
        opid = mo.group(1) if mo else None
        rc, out = run_repl(src_owner, [
            f"exchange export {hpid} {pkt_h}",
            f"exchange export {opid} {pkt_o}",
            "quit"], load=True)
        check("j14_export_receipts",
              f"Exchange: exported {hpid} → {pkt_h}" in out
              and f"Exchange: exported {opid} → {pkt_o}" in out,
              "both source candidates export as packets at "
              "the public path")
        rc, out = run_repl(dst_owner, [
            f"exchange import {pkt_h}",
            f"exchange import {pkt_o}",
            "save", "quit"])
        s = snap(dst_owner)
        hp = s["props"].get(hpid) or {}
        op = s["props"].get(opid) or {}
        check("j14_import_lands_pending_parentless",
              f"Exchange: imported as PENDING proposal {hpid}" in out
              and f"Exchange: imported as PENDING proposal {opid}" in out
              and hp.get("status") == "pending"
              and op.get("status") == "pending"
              and hp.get("parents") == []
              and op.get("parents") == []
              and set(s["units"]) == {"welcome"},
              "import lands both records PENDING and "
              "parentless in the destination — placement "
              "awaits the human gate; no unit is live yet")
        rc, out = run_repl(dst_owner, [
            f"confirm {hpid}", f"confirm {opid}", "save",
            "quit"], load=True)
        s = snap(dst_owner)
        before = s["units"]
        check("j14_imported_confirms_land",
              out.count("is live.") == 2
              and hpid in s["units"] and opid in s["units"]
              and s["units"][hpid]["parents"] == []
              and s["units"][opid]["parents"] == [],
              "both imported records confirm into live "
              "parentless units — dependency-valid knowledge, "
              "eligible for selection")
        rc, out = run_repl(dst_owner, [
            "grow using knowledge about harbor", "save",
            "quit"], load=True)
        s = snap(dst_owner)
        check("j14_partial_scope_selects_only_matching",
              "Eligible: 2, Selected: 1" in out
              and f"Consumer scope IDs: ['{hpid}']" in out
              and "New proposals: 0" in out
              and set(s["props"]) == {hpid, opid}
              and s["units"] == before,
              "a context naming only harbor selects exactly "
              "the harbor unit (partial evidence disclosed: "
              "1 of 2 eligible); the one-unit scope cannot "
              "pair, and the orchard unit and Welcome do not "
              "grow — the scope binds")
        rc, out = run_repl(dst_owner, [
            "grow using knowledge about harbor orchard cellar "
            "vault apple barrel", "proposals", "save", "quit"],
            load=True)
        s = snap(dst_owner)
        newp = {pid: p for pid, p in s["props"].items()
                if pid not in (hpid, opid)}
        child = next(iter(newp), None)
        cp = newp.get(child) or {}
        check("j14_scoped_grow_effect_inside_scope_only",
              "Eligible: 2, Selected: 2" in out
              and "New proposals: 1" in out
              and len(newp) == 1
              and cp.get("status") == "pending"
              and sorted(cp.get("parents") or []) == sorted(
                  [hpid, opid])
              and not any("welcome" in p["parents"]
                          for p in s["props"].values()),
              f"the two-unit scope grows exactly one new "
              f"pending candidate ({child}) whose parents are "
              f"exactly the scope units — the logged effect "
              f"lands inside the named scope and nowhere else")
        check("j14_unrelated_units_unmutated_by_scoped_grow",
              s["units"] == before,
              "after both scoped grows every pre-existing "
              "live unit's record (the two scope units and "
              "the unrelated Welcome) is byte-identical in "
              "the loader snapshot — scoped growth mutates "
              "no live idea")
        rc, out = run_repl(dst_owner, [
            f"confirm {child}", "save", "quit"], load=True)
        s = snap(dst_owner)
        rest = {uid: fp for uid, fp in s["units"].items()
                if uid != child}
        check("j14_scoped_candidate_confirm_mutates_nothing_else",
              f"is live." in out
              and (s["units"].get(child) or {}).get(
                  "parents") is not None
              and sorted(s["units"][child]["parents"]) == sorted(
                  [hpid, opid])
              and rest == before,
              "accepting the scoped candidate lands it with "
              "the scope pair as lineage and changes no other "
              "live unit's record")
        rc, out = run_repl(dst_owner, ["status", "quit"], load=True)
        s2 = snap(dst_owner)
        check("j14_dst_reload_reconciles",
              rc == 0 and s2["units"] == s["units"]
              and s2["props"] == s["props"],
              "after cold reload the destination's units and "
              "proposal records are identical — the scoped "
              "growth and its acceptance are durable")
    finally:
        for o in owners:
            cleanup(o)
        shutil.rmtree(pkt_dir, ignore_errors=True)

    check("Z.cleanup", not _CLEANUP_ERRORS, "; ".join(_CLEANUP_ERRORS))
    failed = [n for n, ok, _ in RESULTS if not ok]
    print(f"JOURNEY_GROWTH: {len(RESULTS) - len(failed)}/{len(RESULTS)} PASS")
    if failed:
        print("FAILURES:", ", ".join(failed))
    return 1 if failed else 0


def smoke():
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
