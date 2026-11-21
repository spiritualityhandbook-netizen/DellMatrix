#!/usr/bin/env python3
"""Part VII — Edition 1 DAG edge ledger checker + negative bypass tests.

Contract (Director D1-D4 binding, PR #502 comment 7044797269; full
pass 7056445974): the Edition 1 DAG (file 08) is the prerequisite /
code-order truth; the Unified section 5 sequence is demonstration
only. This suite proves, mechanically:

  1. The checked-in ledger
     director-reports/PART_VII_DAG_EDGE_LEDGER_2026-11-20.json
     is a faithful transcription of the source DAG
     director-reports/GRAND_PLAN_DIRECTOR_EDITION1_2026-11-18/
     08_DEPENDENCY_DAG.json (same nodes, phases, edges, topological
     order; source pinned by sha256). Authority gates recorded in
     the DAG are NOT dependency edges and never become edges here.
  2. The ledger graph is acyclic and its recorded topological order
     is a valid linearization of its edges.
  3. The plan's cross-document claims hold in the DAG itself:
     GP-E27's dependency set is exactly the 13 circuits named in
     PART_VII_PLAN section 1.2; GP-E22's is exactly
     {GP-E07, GP-E13, GP-E14, GP-E15} (plan section 7, D1).
  4. NEGATIVE BYPASS TESTS: for every divergent edge (an Edition 1
     dependency the Unified section 5 sequence does not express --
     D1: GP-E13/E14/E15 -> GP-E22; D2: GP-E13 -> GP-E14; D3:
     GP-E20 -> GP-E23), a readiness evaluation over the ledger
     REFUSES the downstream node when that prerequisite is the only
     one missing, and a simulated section-5-only evaluator is shown
     to wave the same state through -- the bypass exists under
     section 5 alone and is closed by the ledger. D4 (phases with
     no Unified step) is covered structurally: the exact set of
     section-5-unmapped nodes is pinned.

Readiness rule under test: a node is build-ready iff every one of
its depends_on prerequisites is complete. The Unified order alone
never suffices.

Evidence tier: UNIT (records/graph contract; no product state is
touched -- this suite reads two JSON files and evaluates a pure
function). smoke() is the regress-harness entry point.
"""

import hashlib
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DAG_PATH = os.path.join(
    REPO, "director-reports", "GRAND_PLAN_DIRECTOR_EDITION1_2026-11-18",
    "08_DEPENDENCY_DAG.json")
LEDGER_PATH = os.path.join(
    REPO, "director-reports", "PART_VII_DAG_EDGE_LEDGER_2026-11-20.json")

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))


# The divergent edges, from PART_VII_PLAN section 7 (D1-D4). An edge
# is divergent when the Unified section 5 sequence does not express
# the constraint it carries.
DIVERGENT = {
    ("GP-E13", "GP-E22"): "D1",   # HCN needs Language/state beneath it
    ("GP-E14", "GP-E22"): "D1",   # HCN needs Simulate's contract
    ("GP-E15", "GP-E22"): "D1",   # HCN needs pair-save integrity
    ("GP-E13", "GP-E14"): "D2",   # Simulate: no Unified step at all
    ("GP-E20", "GP-E23"): "D3",   # Dock/Psalm needs Nursery, not just HCN
}

# Nodes no Unified section 5 step sequences (D4 structural set):
# phases 0/2/3/4 entire, plus GP-E14 (D2) and GP-E25 (phase 1, but
# no section 5 step sequences the Muse evidence view).
UNMAPPED = {
    "GP-E01", "GP-E02", "GP-E03", "GP-E05", "GP-E06",          # phase 0
    "GP-E08", "GP-E10", "GP-E11", "GP-E12", "GP-E15",          # phase 2
    "GP-E16", "GP-E17", "GP-E18",                              # phase 3
    "GP-E19", "GP-E20", "GP-E21",                              # phase 4
    "GP-E14", "GP-E25",                                        # D2 / view
}

GP_E27_DEPS = {"GP-E08", "GP-E10", "GP-E11", "GP-E12", "GP-E16",
               "GP-E17", "GP-E18", "GP-E19", "GP-E21", "GP-E22",
               "GP-E23", "GP-E24", "GP-E26"}
GP_E22_DEPS = {"GP-E07", "GP-E13", "GP-E14", "GP-E15"}


def _load(path):
    with open(path, "rb") as fh:
        raw = fh.read()
    return raw, json.loads(raw.decode("utf-8"))


def main():
    if not os.path.isfile(LEDGER_PATH):
        check("ledger_exists", False, f"missing: {LEDGER_PATH}")
        return _tally()
    dag_raw, dag = _load(DAG_PATH)
    _, ledger = _load(LEDGER_PATH)
    check("ledger_exists", True)

    # -- 1. source pin -------------------------------------------------
    digest = hashlib.sha256(dag_raw).hexdigest()
    check("source_pin_sha256",
          ledger.get("generated_from", {}).get("source_sha256") == digest,
          f"ledger={ledger.get('generated_from', {}).get('source_sha256')}"
          f" actual={digest}")
    check("source_pin_dag_version",
          ledger.get("generated_from", {}).get("dag_version")
          == dag.get("version"),
          str(dag.get("version")))

    # -- 2. node fidelity ----------------------------------------------
    dag_nodes = {n["id"]: n for n in dag["nodes"]}
    led_nodes = {n["id"]: n for n in ledger.get("nodes", [])}
    check("node_count_28", len(dag_nodes) == 28 and len(led_nodes) == 28,
          f"dag={len(dag_nodes)} ledger={len(led_nodes)}")
    check("node_ids_equal", set(dag_nodes) == set(led_nodes))
    bad = [i for i in dag_nodes
           if i in led_nodes
           and (led_nodes[i].get("phase") != dag_nodes[i]["phase"]
                or led_nodes[i].get("title") != dag_nodes[i]["title"]
                or set(led_nodes[i].get("depends_on", []))
                != set(dag_nodes[i]["depends_on"]))]
    check("node_fields_faithful", not bad, f"mismatched: {bad}")

    # -- 3. edge fidelity ----------------------------------------------
    dag_edges = {(d, n["id"]) for n in dag["nodes"]
                 for d in n["depends_on"]}
    led_edges = {(e["from"], e["to"]) for e in ledger.get("edges", [])}
    check("edge_count_53", len(dag_edges) == 53 and len(led_edges) == 53,
          f"dag={len(dag_edges)} ledger={len(led_edges)}")
    check("edge_sets_equal", dag_edges == led_edges,
          f"missing={sorted(dag_edges - led_edges)}"
          f" extra={sorted(led_edges - dag_edges)}")

    # -- 4. authority gates are not edges -------------------------------
    check("authority_gates_carried_not_edges",
          ledger.get("authority_gates") == dag.get("authority_gates")
          and ledger.get("authority_gates_are_edges") is False,
          "gates must be recorded verbatim and marked non-edges")

    # -- 5. topological order -------------------------------------------
    topo = ledger.get("topological_order", [])
    check("topo_matches_dag", topo == dag.get("topological_order"))
    pos = {node: i for i, node in enumerate(topo)}
    check("topo_is_linearization",
          len(pos) == 28
          and all(pos[a] < pos[b] for a, b in led_edges),
          "every edge must point forward in the recorded order")

    # -- 6. acyclicity (Kahn) --------------------------------------------
    indeg = {i: 0 for i in led_nodes}
    adj = {i: [] for i in led_nodes}
    for a, b in led_edges:
        if a in adj and b in indeg:
            adj[a].append(b)
            indeg[b] += 1
    queue = sorted([i for i, d in indeg.items() if d == 0])
    seen = 0
    while queue:
        node = queue.pop(0)
        seen += 1
        for nxt in adj[node]:
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                queue.append(nxt)
    check("graph_acyclic", seen == 28, f"kahn visited {seen}/28")

    # -- 7. plan cross-document claims -----------------------------------
    check("gp_e27_deps_match_plan_s1_2",
          set(dag_nodes["GP-E27"]["depends_on"]) == GP_E27_DEPS
          and set(led_nodes["GP-E27"]["depends_on"]) == GP_E27_DEPS,
          f"dag={sorted(dag_nodes['GP-E27']['depends_on'])}")
    check("gp_e22_deps_match_plan_s7_d1",
          set(dag_nodes["GP-E22"]["depends_on"]) == GP_E22_DEPS,
          f"dag={sorted(dag_nodes['GP-E22']['depends_on'])}")

    # -- 8. divergence annotations ---------------------------------------
    annotated = {(e["from"], e["to"]): e.get("divergent")
                 for e in ledger.get("edges", [])}
    bad = [k for k, v in DIVERGENT.items() if annotated.get(k) != v]
    extra = [k for k, v in annotated.items() if v and k not in DIVERGENT]
    check("divergent_edges_annotated_exactly", not bad and not extra,
          f"wrong={bad} extra={extra}")
    unmapped = {n["id"] for n in ledger.get("nodes", [])
                if n.get("unified_step") is None}
    check("d4_unmapped_node_set", unmapped == UNMAPPED,
          f"diff={sorted(unmapped ^ UNMAPPED)}")
    divs = ledger.get("divergences", {})
    check("d4_recorded_structural",
          divs.get("D4", {}).get("edges") == []
          and set(divs.get("D4", {}).get("unmapped_nodes", [])) == UNMAPPED,
          "D4 carries no single edge; it is the unmapped-node set")

    # -- 9. readiness + negative bypass tests -----------------------------
    deps = {i: set(n["depends_on"]) for i, n in led_nodes.items()}
    all_nodes = set(led_nodes)

    def ready(node, completed):
        return deps[node] <= set(completed)

    def unified_visible(node):
        return led_nodes[node].get("unified_step") is not None

    # A section-5-only evaluator, modeled on section 5's own gate
    # definitions (plan section 6): a step closes on its NAMED
    # closure circuits, not on every node its phase happens to
    # contain. SEQ1 (Dell Plan gate) closes on the GP-E07 Dell
    # audit; SEQ3/SEQ4 presuppose SEQ2's HCN circuit GP-E22. So a
    # section-5 evaluator readies GP-E22 once GP-E07 is complete,
    # and GP-E23 once GP-E22 is -- it has no gate that names
    # GP-E13/E14/E15 or GP-E20. (The ledger's unified_step field is
    # the coarser phase-level association used for the D4 mapping;
    # gate conditions are the sharper instrument, and they are the
    # ones a bypass would actually slip through.)
    UNIFIED_GATE_PREREQS = {"GP-E22": {"GP-E07"},
                            "GP-E23": {"GP-E22"}}

    def unified_ready(node, completed):
        if node in UNIFIED_GATE_PREREQS:
            return UNIFIED_GATE_PREREQS[node] <= set(completed)
        visible = {d for d in deps[node] if unified_visible(d)}
        return visible <= set(completed)

    for (a, b), tag in sorted(DIVERGENT.items()):
        without = all_nodes - {a, b}
        check(f"bypass_{tag}_{a}_to_{b}_refused",
              not ready(b, without),
              f"{b} must refuse readiness with {a} incomplete")
        check(f"bypass_{tag}_{a}_to_{b}_control",
              ready(b, without | {a}),
              f"{b} must be ready once {a} completes")

    # The bypass, demonstrated: states section 5 waves through.
    check("bypass_d1_unified_waves_hcn_through",
          unified_ready("GP-E22", {"GP-E07"})
          and not ready("GP-E22", {"GP-E07"}),
          "section 5 readies HCN on the Dell Plan gate alone; "
          "the ledger refuses without GP-E13/E14/E15")
    check("bypass_d2_simulate_invisible_to_unified",
          not unified_visible("GP-E14")
          and not ready("GP-E10", all_nodes - {"GP-E14", "GP-E10"})
          and ready("GP-E10", all_nodes - {"GP-E10"}),
          "GP-E14 has no Unified step, yet GP-E10 readiness "
          "mechanically requires it in the ledger")
    check("bypass_d3_unified_waves_dock_through",
          unified_ready("GP-E23", {"GP-E22"})
          and not ready("GP-E23", {"GP-E22"}),
          "section 5 readies Dock/Psalm on HCN alone; the ledger "
          "refuses without GP-E20 (Nursery)")

    # Positive control on the certification node itself.
    e27_done = GP_E27_DEPS
    check("gp_e27_ready_only_when_all_13_complete",
          ready("GP-E27", e27_done)
          and not ready("GP-E27", e27_done - {"GP-E08"})
          and not ready("GP-E27", e27_done - {"GP-E22"})
          and not ready("GP-E27", e27_done - {"GP-E26"}),
          "any single missing prerequisite refuses GP-E27")

    return _tally()


def _tally():
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        if not ok:
            print(f"FAIL {name}: {detail}")
    print(f"DAG_EDGE_LEDGER: {passed}/{len(RESULTS)}")
    return passed == len(RESULTS) and len(RESULTS) > 0


def smoke():
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
