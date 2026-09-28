#!/usr/bin/env python3
"""Mandell Core II — Dells 51-99 instruction architecture. DVS=F*C*X*H*M*T-O"""
from __future__ import annotations
from typing import Any, Dict, List, Optional

_ROWS = [
    (51, "Select", "Select target(s) from current scope", "selection", "query", "select", "Select Pick Choose Target"),
    (52, "Filter", "Reduce a set by conditions", "reduction", "query", "select", "Filter Exclude Include Narrow Screen Qualify Sift"),
    (53, "Scope", "Establish execution/context boundary", "boundary", "scope", "select", "Scope Bound Within Frame"),
    (54, "Query", "Retrieve information without mutation", "read", "query", "select", "Query Ask Inspect Read Lookup Question"),
    (55, "Set", "Assign an explicit value/state", "assign", "mutate", "state", "Set Assign Put Write"),
    (56, "Get", "Retrieve explicit value/state", "fetch", "query", "state", "Get Fetch ReadValue"),
    (57, "Compare", "Structured comparison between >=2 targets", "compare", "query", "logic", "Compare Contrast Eq Neq Gt Lt"),
    (58, "Match", "Pattern/semantic matching", "match", "query", "logic", "Match Fit Pattern"),
    (59, "Route", "Choose/direct execution path", "route", "control", "flow", "Route Direct Send"),
    (60, "Branch", "Conditional divergence", "branch", "control", "flow", "Branch If Else Switch"),
    (61, "Join", "Rejoin divergent execution paths", "join", "control", "flow", "Join Rejoin Converge"),
    (62, "Parallel", "Execute independent operations concurrently", "concurrent", "control", "flow", "Parallel Concurrent Simultaneous Together"),
    (63, "Sequence", "Explicit ordered execution", "order", "control", "flow", "Sequence Then Order"),
    (64, "Until", "Continue until condition becomes true", "until", "control", "flow", "Until Await WaitUntil"),
    (65, "While", "Continue while condition remains true", "while", "control", "flow", "While During"),
    (66, "ForEach", "Apply operation across collection", "map-each", "control", "flow", "ForEach Each MapEach"),
    (67, "Any", "Existential/set-any condition", "exists", "query", "quantifier", "Any Exists Some"),
    (68, "All", "Universal/set-all condition", "forall", "query", "quantifier", "All Every ForAll"),
    (69, "None", "Explicit absence/zero-match condition", "absent", "query", "quantifier", "None Empty Absent"),
    (70, "Count", "Cardinality - not token count", "cardinality", "query", "quantity", "Count Card Size"),
    (71, "Measure", "Quantify a property", "measure", "query", "quantity", "Measure Quantify Gauge"),
    (72, "Limit", "Establish maximum/minimum/range", "bound", "scope", "quantity", "Limit Cap Min Max Range"),
    (73, "Threshold", "Trigger/qualify at boundary", "threshold", "control", "quantity", "Threshold Trigger Cross"),
    (74, "Weight", "Assign relative influence", "weight", "mutate", "quantity", "Weight Influence Bias"),
    (75, "Normalize", "Convert differing scales/forms to common basis", "normalize", "transform", "quantity", "Normalize Scale Standardize"),
    (76, "Resolve", "Resolve ambiguity/conflict/reference", "resolve", "control", "semantic", "Resolve Disambiguate Clarify"),
    (77, "Infer", "Derive unstated result from evidence/rules", "infer", "query", "semantic", "Infer Derive Deduce"),
    (78, "Cause", "Encode causal relationship", "cause", "mutate", "semantic", "Cause Because Effect"),
    (79, "Depend", "Encode dependency/prerequisite", "depend", "mutate", "semantic", "Depend Require Need"),
    (80, "Context", "Establish semantic contextual frame", "context", "scope", "semantic", "Context Frame Setting"),
    (81, "Reference", "Address existing object/state without copying", "ref", "query", "object", "Reference Ref Point"),
    (82, "Group", "Treat multiple targets as one collection", "group", "mutate", "object", "Group Collect Bundle"),
    (83, "Ungroup", "Release collection while preserving members", "ungroup", "mutate", "object", "Ungroup Release Unpack"),
    (84, "Copy", "Duplicate without consuming original", "copy", "create", "object", "Copy Duplicate Clone"),
    (85, "Move", "Relocate ownership/location/state", "move", "mutate", "object", "Move Relocate Transfer"),
    (86, "Delete", "Explicit controlled removal", "delete", "destroy", "object", "Delete Remove Drop"),
    (87, "Replace", "Atomic substitution old to new", "replace", "mutate", "object", "Replace Swap Substitute"),
    (88, "Patch", "Partial targeted modification", "patch", "mutate", "object", "Patch Update Amend"),
    (89, "Diff", "Produce exact change-set", "diff", "query", "object", "Diff Delta Changeset"),
    (90, "Trace", "Follow provenance/execution/data path", "trace", "query", "audit", "Trace Follow Provenance"),
    (91, "Assert", "Require invariant; fail if false", "assert", "control", "audit", "Assert Require Must"),
    (92, "Guard", "Prevent execution unless conditions hold", "guard", "control", "audit", "Guard Unless OnlyIf"),
    (93, "Try", "Begin recoverable/failable operation", "try", "control", "transaction", "Try Attempt"),
    (94, "Catch", "Handle failure/error class", "catch", "control", "transaction", "Catch Handle OnError"),
    (95, "Commit", "Atomically accept staged mutation", "commit", "mutate", "transaction", "Commit Accept Apply"),
    (96, "Revert", "Undo a mutation/change-set", "revert", "mutate", "transaction", "Revert Undo Unapply"),
    (97, "Define", "Create reusable semantic definition", "define", "create", "abstract", "Define Name Specify"),
    (98, "Alias", "Bind alternate expression to existing semantic identity", "alias", "create", "abstract", "Alias Aka Rename"),
    (99, "Compose", "Create reusable higher-order operation from Dells", "compose", "create", "abstract", "Compose Complete Pipeline"),
]
CORE_II: Dict[int, Dict[str, Any]] = {}
for n, name, manor, root, effect, family, manifests in _ROWS:
    CORE_II[n] = {"name": name, "manor": manor, "root": root, "effect": effect, "family": family, "manifests": manifests.split()}

def dvs_floor() -> Dict[str, Any]:
    return {"formula": "DVS = F*C*X*H*M*T - O", "gate": "low DVS becomes Manifest or Macro", "core_ii_status": "FORMALIZED", "full_operator_status": "PROJECTED_NOT_FACT until 15-layer audit + tests pass", "count": len(CORE_II), "range": "51-99"}

def contract(n: int) -> Optional[Dict[str, Any]]:
    row = CORE_II.get(n)
    return None if not row else {"dell": n, **row, "namespace": "CORE_II", "maturity": "FORMALIZED"}

def all_contracts() -> List[Dict[str, Any]]:
    return [contract(n) for n in range(51, 100)]

def family_index() -> Dict[str, List[int]]:
    out: Dict[str, List[int]] = {}
    for n, row in CORE_II.items():
        out.setdefault(row["family"], []).append(n)
    return out
