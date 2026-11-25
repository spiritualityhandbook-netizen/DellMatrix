#!/usr/bin/env python3
"""72-32 — semantic-graph journal crash windows: graph write vs
derived-effect write, proven to fail closed together (the remaining
gap the register names for SM-25).

Existing coverage (NOT duplicated): form/mandell/p2_dsc1_journal_proof
pins journal INTEGRITY (validation, invalid-journal fail-closed,
bytes preserved, valid-control replay). This suite pins the crash
WINDOWS p2_dsc1 does not:

  Controls (must hold):
  - W1 crash after journal write, before graph save and before the
    derived write: fresh-process load replays ensure_edge +
    sync_dependent; BOTH the edge and the derived value converge.
  - W2 crash after the graph save, before the derived write:
    fresh load converges the derived value from the journal.
  - W3 crash after both commits, before the journal clear: replay
    is idempotent (one edge, value unchanged, journal cleared).
  - W4 mid-batch propagation crash (dependent 1 converged,
    dependent 2 stale, one journal): fresh load converges BOTH.
  - W5b dependent idea corrupt at replay: load succeeds with an
    explicit FAILED ledger record and status "failed" — never
    "synchronized".
  - W7 ensure_edge replay hitting a duplicate seq: load raises
    GraphValidationError and the journal bytes are preserved.

  Defects (fail at the unrepaired head):
  - D1 a journaled sync_dependent whose edge is missing at replay
    is silently skipped: the journal is cleared, the derived value
    is never applied, and the status reports "synchronized".
    A journaled effect must either be applied, recorded FAILED,
    keep its journal, or fail the load closed — never vanish into
    a success report.
  - D2 the same skipped sync must not erase a pre-existing FAILED
    ledger record for that (dependent, property).
  - D3 multi-hop inter-hop window: _recompute_dependent commits a
    hop's derived write before the NEXT hop is journaled, so a
    crash in between leaves the downstream dependent stale with
    no journal and no FAILED record, reported "synchronized".
    The post-crash state must converge on load, or be visibly
    pending/failed — never stale-while-"synchronized".

Labels: CROSS_PROCESS (every phase is a fresh OS process against
the real SemanticGraph authority). State hygiene: each case uses a
uuid-unique owner; cleanup failures are reported, never swallowed.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import uuid
from pathlib import Path

REPO = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, REPO)

RESULTS = []
_CLEANUP_ERRORS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def _run(code, owner):
    p = subprocess.run([sys.executable, "-c", code], cwd=REPO,
                       capture_output=True, text=True, timeout=120)
    res = {}
    for line in p.stdout.splitlines():
        if line.startswith("RESULT "):
            res.update(json.loads(line[len("RESULT "):]))
    if p.returncode != 0 and not res:
        res = {"crashed": True, "stderr": p.stderr[-300:]}
    return res


_COMMON = """
import json, os, shutil, sys
sys.path.insert(0, %(REPO)r)
from form.mandell.idea import Idea, Provenance, ProvenanceSource
from form.mandell.idea_persist import save_idea, load_idea, _idea_path
from form.mandell.semantic_graph import (
    SemanticGraph, DerivationKind, GraphValidationError,
    RelationshipType, RelationshipStatus,
    graph_path, graph_journal_path)
from form.persist import _STATE_DIR
BASE = _STATE_DIR
OWNER = %(OWNER)r
PROV = Provenance(source=ProvenanceSource.HUMAN, activity="t7232", agent="t7232")
def clean():
    d = os.path.join(BASE, f"ideas_{OWNER}")
    if os.path.isdir(d): shutil.rmtree(d)
    for p in [graph_path(OWNER), graph_journal_path(OWNER)]:
        if os.path.isfile(p): os.remove(p)
def pair():
    clean()
    src = Idea(title="S"); src.set_property("v", 42, PROV); save_idea(src, OWNER)
    dep = Idea(title="D"); save_idea(dep, OWNER)
    return src, dep
def mkentry(g, dep, src):
    return g._new_entry(RelationshipType.DEPENDS_ON, dep.id, src.id,
        {"derivation": "mirror", "derived_property": "m", "unit": "v"},
        RelationshipStatus.ACTIVE, PROV, "declare_dependency")
def syncop(dep_id, src_id, rel_id, prop="m", unit="v"):
    return {"op": "sync_dependent", "dependent_id": dep_id,
            "derived_property": prop, "target_id": src_id, "unit": unit,
            "derivation": "mirror", "subject_id": None, "edge_rel_id": rel_id}
r = {}
"""

_LOAD = """
import json, os, sys
sys.path.insert(0, %(REPO)r)
from form.mandell.semantic_graph import SemanticGraph, GraphValidationError, graph_journal_path
from form.mandell.idea_persist import load_idea
r = {}
try:
    g = SemanticGraph.load(%(OWNER)r)
    r["loaded"] = True
    r["status"] = g.propagation_status(%(DEP)r, %(PROP)r)
    r["failures"] = g.get_propagation_failures()
    r["n_entries"] = len(g._entries)
    r["edge_active"] = (%(EDGE)r in g._current)
except GraphValidationError as exc:
    r["loaded"] = False; r["error_type"] = "GraphValidationError"
except Exception as exc:
    r["loaded"] = False; r["error_type"] = type(exc).__name__
try:
    r["derived"] = load_idea(%(DEP)r, %(OWNER)r).get_property(%(PROP)r)
except Exception as exc:
    r["derived"] = "<" + type(exc).__name__ + ">"
r["journal_exists"] = os.path.isfile(graph_journal_path(%(OWNER)r))
if r["journal_exists"]:
    with open(graph_journal_path(%(OWNER)r), "rb") as f:
        r["journal_len"] = len(f.read())
print("RESULT " + json.dumps(r, default=str))
"""


def _load(owner, dep, edge, prop="m"):
    code = _LOAD % {"REPO": REPO, "OWNER": owner, "DEP": dep,
                    "EDGE": edge, "PROP": prop}
    return _run(code, owner)


def _cleanup(owner):
    code = (_COMMON % {"REPO": REPO, "OWNER": owner}
            + "\nclean()\nprint('RESULT {}')")
    res = _run(code, owner)
    if res.get("crashed"):
        _CLEANUP_ERRORS.append(owner)


def case_w1():
    owner = "T7232W1" + uuid.uuid4().hex[:8]
    s = _run((_COMMON % {"REPO": REPO, "OWNER": owner}) + """
src, dep = pair()
g = SemanticGraph.load(OWNER)
e = mkentry(g, dep, src)
g._write_journal([{"op": "ensure_edge", "entry": e.to_dict()},
                  syncop(dep.id, src.id, e.rel_id)])
r = {"dep": dep.id, "edge": e.rel_id}  # CRASH: no graph save, no derived write
print("RESULT " + json.dumps(r))
""", owner)
    lc = _load(owner, s.get("dep", "?"), s.get("edge", "?"))
    check("W1.edge_converges", lc.get("loaded") and lc.get("edge_active"),
          str(lc))
    check("W1.derived_converges", lc.get("derived") == 42
          and not lc.get("journal_exists"), str(lc))
    _cleanup(owner)


def case_w2():
    owner = "T7232W2" + uuid.uuid4().hex[:8]
    s = _run((_COMMON % {"REPO": REPO, "OWNER": owner}) + """
src, dep = pair()
g = SemanticGraph.load(OWNER)
e = mkentry(g, dep, src)
g._write_journal([{"op": "ensure_edge", "entry": e.to_dict()},
                  syncop(dep.id, src.id, e.rel_id)])
g._entries.append(e); g._fold(); g.save()  # CRASH: derived never written
r = {"dep": dep.id, "edge": e.rel_id}
print("RESULT " + json.dumps(r))
""", owner)
    lc = _load(owner, s.get("dep", "?"), s.get("edge", "?"))
    check("W2.derived_converges", lc.get("loaded") and lc.get("derived") == 42
          and lc.get("status") == "synchronized"
          and not lc.get("journal_exists"), str(lc))
    _cleanup(owner)


def case_w3():
    owner = "T7232W3" + uuid.uuid4().hex[:8]
    s = _run((_COMMON % {"REPO": REPO, "OWNER": owner}) + """
src, dep = pair()
g = SemanticGraph.load(OWNER)
e = g.declare_dependency(dep.id, src.id, DerivationKind.MIRROR, "m",
                         unit="v", provenance=PROV)
g._write_journal([{"op": "ensure_edge", "entry": e.to_dict()},
                  syncop(dep.id, src.id, e.rel_id)])  # CRASH before clear
r = {"dep": dep.id, "edge": e.rel_id}
print("RESULT " + json.dumps(r))
""", owner)
    lc = _load(owner, s.get("dep", "?"), s.get("edge", "?"))
    check("W3.replay_idempotent", lc.get("loaded") and lc.get("n_entries") == 1
          and lc.get("derived") == 42 and not lc.get("journal_exists"),
          str(lc))
    _cleanup(owner)


def case_w4():
    owner = "T7232W4" + uuid.uuid4().hex[:8]
    s = _run((_COMMON % {"REPO": REPO, "OWNER": owner}) + """
src, dep = pair()
dep2 = Idea(title="D2"); save_idea(dep2, OWNER)
g = SemanticGraph.load(OWNER)
e1 = g.declare_dependency(dep.id, src.id, DerivationKind.MIRROR, "m",
                          unit="v", provenance=PROV)
e2 = g.declare_dependency(dep2.id, src.id, DerivationKind.MIRROR, "m",
                          unit="v", provenance=PROV)
src.set_property("v", 100, PROV); save_idea(src, OWNER)
g._write_journal([syncop(dep.id, src.id, e1.rel_id),
                  syncop(dep2.id, src.id, e2.rel_id)])
g._recompute_dependent(e1)  # dep1 -> 100; CRASH before dep2
r = {"dep": dep.id, "dep2": dep2.id, "edge": e1.rel_id}
print("RESULT " + json.dumps(r))
""", owner)
    lc = _load(owner, s.get("dep", "?"), s.get("edge", "?"))
    lc2 = _load(owner, s.get("dep2", "?"), s.get("edge", "?"))
    check("W4.both_converge", lc.get("derived") == 100
          and lc2.get("derived") == 100 and not lc.get("journal_exists"),
          f"{lc} / {lc2}")
    _cleanup(owner)


def case_w5b():
    owner = "T7232W5" + uuid.uuid4().hex[:8]
    s = _run((_COMMON % {"REPO": REPO, "OWNER": owner}) + """
src, dep = pair()
g = SemanticGraph.load(OWNER)
e = g.declare_dependency(dep.id, src.id, DerivationKind.MIRROR, "m",
                         unit="v", provenance=PROV)
src.set_property("v", 100, PROV); save_idea(src, OWNER)
g._write_journal([syncop(dep.id, src.id, e.rel_id)])
with open(_idea_path(dep.id, OWNER), "w") as f: f.write("{corrupt")
r = {"dep": dep.id, "edge": e.rel_id}
print("RESULT " + json.dumps(r))
""", owner)
    lc = _load(owner, s.get("dep", "?"), s.get("edge", "?"))
    check("W5b.corrupt_dependent_failed_explicit",
          lc.get("loaded") and lc.get("status") == "failed"
          and len(lc.get("failures") or []) >= 1, str(lc))
    _cleanup(owner)


def case_w7():
    owner = "T7232W7" + uuid.uuid4().hex[:8]
    s = _run((_COMMON % {"REPO": REPO, "OWNER": owner}) + """
src, dep = pair()
g = SemanticGraph.load(OWNER)
e = g.declare_dependency(dep.id, src.id, DerivationKind.MIRROR, "m",
                         unit="v", provenance=PROV)
bad = dict(e.to_dict()); bad["rel_id"] = "rel-dup-seq-999"
g._write_journal([{"op": "ensure_edge", "entry": bad}])
with open(graph_journal_path(OWNER), "rb") as f: before = len(f.read())
r = {"dep": dep.id, "edge": e.rel_id, "journal_len": before}
print("RESULT " + json.dumps(r))
""", owner)
    lc = _load(owner, s.get("dep", "?"), s.get("edge", "?"))
    check("W7.dup_seq_failclosed_journal_preserved",
          lc.get("loaded") is False
          and lc.get("error_type") == "GraphValidationError"
          and lc.get("journal_exists")
          and lc.get("journal_len") == s.get("journal_len"), str(lc))
    _cleanup(owner)


def case_d1():
    owner = "T7232D1" + uuid.uuid4().hex[:8]
    s = _run((_COMMON % {"REPO": REPO, "OWNER": owner}) + """
src, dep = pair()
g = SemanticGraph.load(OWNER)
# Journaled sync whose edge is NOT in the graph at replay time.
g._write_journal([syncop(dep.id, src.id, "rel-nonexistent-000")])
r = {"dep": dep.id, "edge": "rel-nonexistent-000"}
print("RESULT " + json.dumps(r))
""", owner)
    lc = _load(owner, s.get("dep", "?"), s.get("edge", "?"))
    not_silent_success = (
        (lc.get("loaded") is False)
        or (lc.get("derived") == 42)
        or (lc.get("status") in ("failed", "pending", "unknown")
            and (lc.get("failures") or lc.get("journal_exists"))))
    check("D1.missing_edge_sync_not_silent_success", not_silent_success,
          str(lc))
    check("D1.missing_edge_failure_visible",
          (lc.get("loaded") is False) or lc.get("derived") == 42
          or bool(lc.get("failures")) or bool(lc.get("journal_exists")),
          str(lc))
    _cleanup(owner)


def case_d2():
    owner = "T7232D2" + uuid.uuid4().hex[:8]
    s = _run((_COMMON % {"REPO": REPO, "OWNER": owner}) + """
src, dep = pair()
g = SemanticGraph.load(OWNER)
e = g.declare_dependency(dep.id, src.id, DerivationKind.MIRROR, "m",
                         unit="v", provenance=PROV)
# Persist an explicit FAILED record for (dep, m)...
g._propagation_ledger[(dep.id, "m")] = {
    "status": "failed", "error": "probe: prior failure",
    "timestamp": 1.0, "target_id": src.id}
g.save()
# ...then a journal arrives whose sync names a MISSING edge.
g2 = SemanticGraph.load(OWNER)
g2._write_journal([syncop(dep.id, src.id, "rel-nonexistent-000")])
r = {"dep": dep.id, "edge": e.rel_id,
     "status_before": g2.propagation_status(dep.id, "m")}
print("RESULT " + json.dumps(r))
""", owner)
    lc = _load(owner, s.get("dep", "?"), s.get("edge", "?"))
    check("D2.stale_failed_not_erased_by_skipped_sync",
          lc.get("loaded") and lc.get("status") == "failed"
          and len(lc.get("failures") or []) >= 1,
          f"setup={s} load={lc}")
    _cleanup(owner)


def case_d3():
    owner = "T7232D3" + uuid.uuid4().hex[:8]
    s = _run((_COMMON % {"REPO": REPO, "OWNER": owner}) + """
clean()
a = Idea(title="A"); a.set_property("v", 42, PROV); save_idea(a, OWNER)
b = Idea(title="B"); save_idea(b, OWNER)
c = Idea(title="C"); save_idea(c, OWNER)
g = SemanticGraph.load(OWNER)
g.declare_dependency(b.id, a.id, DerivationKind.MIRROR, "m",
                     unit="v", provenance=PROV)
ec = g.declare_dependency(c.id, b.id, DerivationKind.MIRROR, "n",
                          unit="m", provenance=PROV)
# Post-crash state of the inter-hop window: source + first hop
# committed at 100; the downstream hop was never journaled/applied.
a.set_property("v", 100, PROV); save_idea(a, OWNER)
bb = load_idea(b.id, OWNER); bb.set_property("m", 100, PROV)
save_idea(bb, OWNER)
r = {"dep": c.id, "edge": ec.rel_id,
     "c_before": load_idea(c.id, OWNER).get_property("n")}
print("RESULT " + json.dumps(r))
""", owner)
    lc = _load(owner, s.get("dep", "?"), s.get("edge", "?"), prop="n")
    check("D3.downstream_not_stale_while_synchronized",
          lc.get("loaded") and (lc.get("derived") == 100
                                or lc.get("status") != "synchronized"
                                or bool(lc.get("failures"))
                                or bool(lc.get("journal_exists"))),
          f"setup={s} load={lc}")
    _cleanup(owner)


def main():
    case_w1(); case_w2(); case_w3(); case_w4(); case_w5b(); case_w7()
    case_d1(); case_d2(); case_d3()
    check("cleanup.no_errors", not _CLEANUP_ERRORS, str(_CLEANUP_ERRORS))
    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"graph_journal_crash_test: {passed}/{len(RESULTS)} PASS")
    return 0 if passed == len(RESULTS) else 1


def smoke() -> bool:
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
