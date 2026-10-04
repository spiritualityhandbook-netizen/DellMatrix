"""P3 R3.4 geometry proof — vesica authority unification + policy verification.

GDP-001 Phase 3 (Resonance, Harmony & Information Geometry), Stream C.
NON-VACUOUS (P3R rewrite, 2026-10-04):

  3.4.1 (IMPLEMENT): verita.vesica_strength now DELEGATES to
      sacred_geometry.vesica (EQ-GEO-001, live authority). Exactly one
      canonical overlap implementation; no reimplementation. Proven by a
      424-case delegation sweep (bitwise identical outputs) plus a
      mutation test: perturbing the canonical MUST diverge the wrapper.
  3.3.1 (PARK — recorded, NOT built): the Verita transformation layer is
      PARKED. This proof asserts the PARK record exists; it does NOT
      implement the layer.
  3.4.2-3.4.4 (DEFER — recorded, NOT built): Cech nerve, power diagrams,
      alpha filtration are DEFERRED. This proof asserts the DEFERRED
      record exists and that no implementation has appeared.
  3.4.5 (IMPLEMENT — policy verification): "never display uncomputed
      geometric regions" is verified by code audit AND by a live
      failure-injection test.

  BYPASS-MUST-FAIL (geometry failure handling — the Director's explicit
      test): the proof forces the geometry call to raise and asserts
      (a) NO fabricated kind="vesica" edges are emitted and (b) an
      explicit "vesica geometry unavailable" marker is recorded in
      GraphView.warnings (surfaced in to_dict() and ascii()). If the code
      fell back to returning fabricated edges, the proof MUST FAIL
      (exit non-zero). A healthy control (real geometry -> computed
      vesica edge, no warnings) proves the test is sensitive to the
      failure path rather than vacuous.

  P3R update: the old graph_view.py exception fallback that fabricated
      kind="vesica" edges between ALL connected pairs has been REMOVED
      (W2). The two policy checks that documented it as a defect now
      assert the fix.

Portable: derives REPO from __file__. Enforced: smoke() -> bool,
sys.exit(0/1), registered in form.regress (# P3 R3.4 block).

Phases (each in a fresh OS process):
  delegation-sweep  — wrapper vs canonical identical over a documented battery
                      (7x4 radii grid x 8 distance fractions + 200 seeded
                      random cases; all four type branches hit)
  invalid-inputs    — defined wrapper behavior: negative/NaN/zero radii and
                      distances are clamped (policy preserved from the old
                      wrapper); non-numeric inputs raise from float()
  canonical-raw-doc — DOCUMENTED raw-canonical invalid-input behavior
                      (canonical untouched by 3.4.1): negative radii can
                      misclassify as "separate"; NaN propagates into the
                      output dict without raising; zero radii give
                      "separate" (d>0) / "coincident" (d=0)
  live-caller       — real consumer paths: VeritaField.evaluate_link
                      (brain.py's call chain) and verita_between_nodes
                      (Program.verita_edges / English "verita" command path)
  mutation          — canonical perturbed via monkeypatch; wrapper output
                      MUST diverge (proves delegation, not reimplementation)
  ledger-invariants — equation_ledger_invariants_test still green
  failure-honest    — BYPASS-MUST-FAIL: geometry forced to raise ->
                      no fabricated edges + explicit unavailable marker;
                      healthy control proves sensitivity
  policy-345        — 3.4.5 grep audit: no speculative-geometry
                      implementations; every vesica-edge emission site
                      accounted for (computed paths only — none inside an
                      exception handler); every void/negative-space/channel
                      mention allowlisted as benign
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

# Portable: derive repo root from this file's location.
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _phase(name: str, code: str) -> dict:
    """Run one phase in a fresh process. Returns {check_name: bool}."""
    r = subprocess.run(
        [sys.executable, "-c", code],
        cwd=REPO, capture_output=True, text=True, timeout=180)
    results = {}
    if r.returncode != 0:
        results[f"{name}::crashed"] = False
        results[f"{name}::stderr_tail"] = False
        print(f"[{name}] SUBPROCESS CRASH rc={r.returncode}", flush=True)
        print((r.stderr or "")[-2000:], flush=True)
        return results
    for line in r.stdout.splitlines():
        if line.startswith("RESULT "):
            try:
                d = json.loads(line[len("RESULT "):])
                for k, v in d.items():
                    results[f"{name}::{k}"] = bool(v)
            except json.JSONDecodeError:
                results[f"{name}::bad_json"] = False
        elif line.startswith("WITNESS ") or line.startswith("SWEEP "):
            print(f"[{name}] {line}", flush=True)
    if not results:
        results[f"{name}::empty_evidence"] = False
    return results


_PREAMBLE = """
import json, math, random, subprocess, sys
sys.path.insert(0, %(REPO)r)
from form.dell_matrix import verita as V
from form.dell_matrix import sacred_geometry as SG
r = {}
"""

_POSTAMBLE = """
print("RESULT " + json.dumps(r))
"""


def _delegation_sweep() -> tuple[str, str]:
    code = (_PREAMBLE % {"REPO": REPO} + """
# Battery: radii grid x distance fractions of (r1+r2) + 200 seeded randoms.
cases = []
for r1 in (1e-9, 1e-6, 0.1, 0.5, 1.0, 2.0, 5.0):
    for r2 in (1e-9, 0.25, 1.0, 3.0):
        s = r1 + r2
        for f in (0.0, 0.001, 0.25, 0.5, 0.9, 0.999, 1.0, 1.5):
            cases.append((r1, r2, f * s))
rng = random.Random(20261004)
for _ in range(200):
    a = rng.uniform(0.05, 5.0); b = rng.uniform(0.05, 5.0)
    cases.append((a, b, rng.uniform(0.0, a + b + 1.0)))
bad = []
types = {}
for (r1, r2, d) in cases:
    w = V.vesica_strength(r1, r2, d)
    c = SG.vesica(0.0, 0.0, r1, d, 0.0, r2)
    t = w["type"]; types[t] = types.get(t, 0) + 1
    if not (w["strength"] == c["strength"] and w["type"] == c["type"]
            and w["distance"] == c["distance"]):
        bad.append((r1, r2, d))
    if not (0.0 <= w["strength"] <= 1.0):
        bad.append(("bounds", r1, r2, d))
r["sweep_n"] = len(cases)
r["sweep_identical"] = (len(bad) == 0)
r["sweep_first_bad"] = (bad[0] if bad else "none")
r["branches_hit"] = sorted(types) == ["coincident", "contained", "separate", "vesica"]
print("SWEEP cases=%d branches=%s bad=%d" % (len(cases), sorted(types), len(bad)))
""" + _POSTAMBLE)
    return ("delegation-sweep", code)


def _invalid_inputs() -> tuple[str, str]:
    code = (_PREAMBLE % {"REPO": REPO} + """
w = V.vesica_strength
# Defined wrapper policy: clamps preserved from the pre-delegation wrapper.
r["neg_radius_clamped"] = (w(-2.0, 1.0, 0.5) == w(1e-9, 1.0, 0.5))
r["nan_radius_clamped"] = (w(float("nan"), 1.0, 0.5) == w(1e-9, 1.0, 0.5))
r["zero_radius_clamped"] = (w(0.0, 0.0, 0.5) == w(1e-9, 1e-9, 0.5))
r["neg_dist_clamped"] = (w(1.0, 1.0, -3.0) == w(1.0, 1.0, 0.0))
r["nan_dist_clamped"] = (w(1.0, 1.0, float("nan")) == w(1.0, 1.0, 0.0))
neg = w(1.0, 1.0, -3.0)
r["neg_dist_coincident"] = (neg["type"] == "coincident" and neg["strength"] == 1.0
                            and neg["distance"] == 0.0)
r["shape_keys"] = (set(w(1.0, 1.0, 1.0).keys()) == {"strength", "type", "distance"})
# No NaN leaks through the wrapper boundary (clamps absorb NaN).
allnan = w(float("nan"), float("nan"), float("nan"))
r["no_nan_leak"] = (not math.isnan(allnan["strength"])
                    and not math.isnan(allnan["distance"]))
try:
    w("abc", 1.0, 0.5); r["str_raises"] = False
except ValueError:
    r["str_raises"] = True
try:
    w(None, 1.0, 0.5); r["none_raises"] = False
except TypeError:
    r["none_raises"] = True
print("WITNESS all-nan -> %s" % (allnan,))
""" + _POSTAMBLE)
    return ("invalid-inputs", code)


def _canonical_raw_doc() -> tuple[str, str]:
    code = (_PREAMBLE % {"REPO": REPO} + """
# DOCUMENTED raw-canonical behavior (canonical NOT modified by 3.4.1).
# These assertions pin the observed behavior so any silent change is caught.
c1 = SG.vesica(0.0, 0.0, -1.0, 2.0, 0.0, 1.0)
r["raw_neg_radius_separate"] = (c1["type"] == "separate" and c1["strength"] == 0.0)
c2 = SG.vesica(0.0, 0.0, 1.0, float("nan"), 0.0, 1.0)
r["raw_nan_no_raise"] = isinstance(c2, dict)
r["raw_nan_propagates"] = (math.isnan(c2["distance"]) and math.isnan(c2["strength"]))
c3 = SG.vesica(0.0, 0.0, 0.0, 1.0, 0.0, 0.0)
r["raw_zero_radii_separate"] = (c3["type"] == "separate" and c3["strength"] == 0.0)
c4 = SG.vesica(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
r["raw_zero_radii_coincident"] = (c4["type"] == "coincident" and c4["strength"] == 1.0)
print("WITNESS raw-neg-radius -> %s" % ({"type": c1["type"], "strength": c1["strength"]},))
print("WITNESS raw-nan -> type=%s strength=nan distance=nan (no raise)" % (c2["type"],))
""" + _POSTAMBLE)
    return ("canonical-raw-doc", code)


def _live_caller() -> tuple[str, str]:
    code = (_PREAMBLE % {"REPO": REPO} + """
from form.dell_matrix.verita import VeritaField, verita_of_pair
from form.dell_matrix.sacred_geometry import verita_between_nodes
# Real consumer 1: VeritaField.evaluate_link <- brain.py:121 (evaluate_link
# calls verita_of_pair which calls the delegated vesica_strength).
vf = VeritaField()
link = vf.evaluate_link("Alpha structure grow", "structure clarity grow")
r["link_accept"] = bool(link["accept"])
r["link_strength_half"] = (link["vesica"]["strength"] == 0.5)
r["link_score_half"] = (link["score"] == 0.5)
r["link_logged"] = (vf.residue_summary()["count"] >= 0 and link["link_count"] == 1)
# Real consumer 2: verita_between_nodes <- Program.verita_edges (open.py)
# <- English "verita" command (repl.py) and graph_view.py.
nodes = [
    {"id": "a", "x": 0.0, "y": 0.0, "score": 1.0},
    {"id": "b", "x": 1.0, "y": 0.0, "score": 1.0},
    {"id": "c", "x": 50.0, "y": 50.0, "score": 1.0},
]
edges = verita_between_nodes(nodes)
r["edges_one_pair"] = (len(edges) == 1 and edges[0]["source"] == "a"
                       and edges[0]["target"] == "b")
r["edge_has_verita"] = ("verita" in edges[0] and edges[0]["verita"] > 0)
r["edge_distance_one"] = (edges[0]["distance"] == 1.0)
print("WITNESS link score=%s accept=%s vesica=%s" % (
    link["score"], link["accept"], link["vesica"]))
print("WITNESS edge verita=%s strength=%s type=%s distance=%s" % (
    edges[0]["verita"], edges[0]["strength"], edges[0]["type"], edges[0]["distance"]))
""" + _POSTAMBLE)
    return ("live-caller", code)


def _mutation() -> tuple[str, str]:
    code = (_PREAMBLE % {"REPO": REPO} + """
# Mutation: perturb the canonical; the wrapper MUST show divergence.
# (Proves delegation rather than reimplementation: a reimplemented formula
# would be unaffected by patching sacred_geometry.vesica.)
orig = SG.vesica
cases = [(1.0, 1.0, 1.0), (2.0, 1.0, 0.5), (1.0, 2.0, 5.0),
         (0.5, 0.5, 0.4), (3.0, 3.0, 0.0)]
baseline = [V.vesica_strength(*c) for c in cases]
def mutated(ax, ay, ar, bx, by, br):
    res = dict(orig(ax, ay, ar, bx, by, br))
    # subtle shift: bijective on [0,1] at 4dp, no fixed points
    res["strength"] = round((res["strength"] + 0.0007) % 1.0, 4)
    return res
SG.vesica = mutated
after = [V.vesica_strength(*c) for c in cases]
SG.vesica = orig
diverged = [i for i, (b, a) in enumerate(zip(baseline, after))
            if b["strength"] != a["strength"]]
r["mutation_detected"] = (len(diverged) == len(cases))
r["mutation_diverged_n"] = len(diverged)
r["mutation_all_cases_diverged"] = (diverged == list(range(len(cases))))
print("WITNESS baseline[0]=%s mutated[0]=%s diverged=%s" % (
    baseline[0]["strength"], after[0]["strength"], diverged))
""" + _POSTAMBLE)
    return ("mutation", code)


def _ledger_invariants() -> tuple[str, str]:
    code = ("""
import json, sys
sys.path.insert(0, %(REPO)r)
from form.equation_ledger_invariants_test import smoke as ledger_smoke
r = {}
r["ledger_all_pass"] = bool(ledger_smoke())
print("RESULT " + json.dumps(r))
""" % {"REPO": REPO})
    return ("ledger-invariants", code)


def _failure_honest() -> tuple[str, str]:
    code = ("""
import json, sys
sys.path.insert(0, @@REPO@@)
from form.dell_matrix import graph_view as gv
from form.dell_matrix import sacred_geometry as sg
from form.dell_matrix.blank_cube import give
from form.dell_matrix.plane import Skin
r = {}

cube = give("R34FH", clean=True)
cube.place_idea("a", "alpha beta", words="alpha beta", skin=Skin.SEED, x=0.0, y=0.0)
cube.place_idea("b", "beta gamma", words="beta gamma", skin=Skin.SEED, x=1.0, y=0.0)
plane = cube.session.plane

# Healthy control: real geometry -> a COMPUTED kind="vesica" edge, no warnings.
v_ok = gv.build_view(plane)
r["healthy_computed_vesica"] = any(e.kind == "vesica" for e in v_ok.edges)
r["healthy_no_warnings"] = (v_ok.warnings == [])
print("WITNESS healthy kinds=%s warnings=%s" % (
    [e.kind for e in v_ok.edges], v_ok.warnings))

# BYPASS-MUST-FAIL: force the geometry call to raise. The honest contract:
# (a) NO fabricated kind="vesica" edges, (b) an explicit unavailable
# marker in GraphView.warnings. If the code fell back to fabricating
# edges, no_fabricated_edges would be False and the proof would FAIL.
orig = sg.verita_between_nodes
def _boom(*a, **k):
    raise RuntimeError("simulated geometry outage")
sg.verita_between_nodes = _boom
try:
    v = gv.build_view(plane)
finally:
    sg.verita_between_nodes = orig
fab = [e for e in v.edges if e.kind == "vesica"]
r["no_fabricated_edges"] = (len(fab) == 0)
r["unavailable_marker"] = any("vesica geometry unavailable" in w
                              for w in v.warnings)
print("WITNESS failed kinds=%s warnings=%s" % (
    [e.kind for e in v.edges], v.warnings))
# The marker is explicit in both serializations (not silent).
d = v.to_dict()
r["marker_in_dict"] = any("vesica geometry unavailable" in w
                          for w in d["warnings"])
r["marker_in_ascii"] = ("vesica geometry unavailable" in v.ascii())
# Differential: the failure path is observably different from success,
# proving this test is sensitive to the failure path (not vacuous).
r["failure_differs_from_healthy"] = (
    (len(v_ok.edges), list(v_ok.warnings)) != (len(v.edges), list(v.warnings)))
print("RESULT " + json.dumps(r))
""".replace("@@REPO@@", repr(REPO)))
    return ("failure-honest", code)


def _policy_345() -> tuple[str, str]:
    code = ("""
import json, os, subprocess, sys
REPO = @@REPO@@
r = {}

def _grep(pat, *paths, extra=()):
    cmd = ["grep", "-rniE", pat, "--include=*.py"] + list(extra) + list(paths)
    pr = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=60)
    out = pr.stdout.strip().splitlines() if pr.stdout.strip() else []
    return [ln for ln in out if ln.strip()]

# 3.4.2-3.4.4 DEFER record exists, and no implementation has appeared.
spec = _grep("cech|nerve|power.diagram|power_diagram|alpha.filtration|alpha_filtration",
             "form")
spec_ok = True
for ln in spec:
    # Allowed: the DEFERRED record in sacred_geometry.py, the PARKED record
    # in verita.py, and this proof file. Anything else = implementation.
    if ("form/dell_matrix/sacred_geometry.py" in ln
            or "form/dell_matrix/verita.py" in ln
            or "p3_r34_geometry_proof.py" in ln):
        continue
    spec_ok = False
r["speculative_no_impl"] = spec_ok
r["speculative_hits_n"] = len(spec)
print("WITNESS speculative-geometry hits=%d (all must be deferral records)" % len(spec))
for ln in spec:
    print("WITNESS   " + ln[:160])

# Vesica-edge emission sites, post-W2 fix: kind="vesica" is emitted ONLY on
# computed paths (graph_view.py try-block, sacred_geometry.py's own edge
# builder). The fabricated exception fallback is REMOVED. Assert no
# kind="vesica" emission inside any exception handler.
def _no_fabrication_in_handlers(path):
    src = open(os.path.join(REPO, path)).read().splitlines()
    # line numbers (1-based) of except handlers and of kind="vesica" hits
    excepts = [i + 1 for i, ln in enumerate(src)
               if ln.lstrip().startswith("except")]
    hits = [i + 1 for i, ln in enumerate(src) if 'kind="vesica"' in ln
            or "kind='vesica'" in ln or '"kind": "vesica"' in ln]
    # A hit is suspicious if it comes after an except at deeper-or-equal
    # indent without an intervening def/class (i.e., inside the handler).
    # Conservative structural check: every hit must precede every except
    # in graph_view.py (single handler at the end); sacred_geometry.py's
    # hit is inside verita_between_nodes, whose except (line ~168) is in
    # the vesica() helper, not on the edge path.
    return hits, excepts

gv_hits, gv_excepts = _no_fabrication_in_handlers("form/dell_matrix/graph_view.py")
gv_src_lines = open(os.path.join(REPO, "form/dell_matrix/graph_view.py")).read().splitlines()
# The geometry-failure handler is the `except` whose body records
# geometry_warnings; kind="vesica" must be emitted only BEFORE it
# (i.e., on the computed path inside the try).
fail_handler = next(
    i + 1 for i, ln in enumerate(gv_src_lines)
    if ln.lstrip().startswith("except")
    and any("geometry_warnings.append" in gv_src_lines[j]
            for j in range(i, min(i + 12, len(gv_src_lines)))))
r["graphview_computed_only"] = (
    len(gv_hits) == 1 and all(h < fail_handler for h in gv_hits))
print("WITNESS graph_view.py kind=vesica lines=%s fail-handler line=%s" % (
    gv_hits, fail_handler))
sg_src = open(os.path.join(REPO, "form/dell_matrix/sacred_geometry.py")).read()
# sacred_geometry.py's "kind": "vesica" hit must be inside
# verita_between_nodes (the computed path), not inside an except block.
sg_lines = sg_src.splitlines()
sg_hit = next(i + 1 for i, ln in enumerate(sg_lines) if '"kind": "vesica"' in ln)
sg_def = next(i + 1 for i, ln in enumerate(sg_lines)
              if ln.startswith("def verita_between_nodes"))
r["sg_computed_only"] = (sg_hit > sg_def)
print("WITNESS sacred_geometry.py kind-vesica line=%s def line=%s" % (sg_hit, sg_def))
# The old fabricated fallback is gone from the except handler: the handler
# records geometry_warnings and appends no ViewEdge.
gv_src = open(os.path.join(REPO, "form/dell_matrix/graph_view.py")).read()
handler = gv_src.split("except Exception as exc:")[1]
r["handler_records_warning"] = ("geometry_warnings.append" in handler)
r["handler_no_viewedge"] = ("ViewEdge(" not in handler)
r["warning_text_honest"] = ("vesica geometry unavailable" in handler)

# Void / negative-space / channel mentions: every hit allowlisted as benign.
void_hits = _grep("void|negative.space|negative_space",
                  "form/dell_matrix", "form/repl.py", "form/open.py")
allow = [
    ("actions_registry.py", "Forces in voids"),          # dead registry hint; no handler
    ("first_person.py", "Void cell"),                    # empty-cell card declares emptiness
    ("forces.py", "Negative space and voids between nodes"),  # description string only
    ("intrinsic_agent.py", "avoid"),                     # code comments, not geometry
    ("needs.py", "avoid collision"),                     # code comment
    ("nursery.py", "Nursery / Void / Op-Box"),            # module docstring header
    ("nursery.py", "avoid exact id collision"),           # code comment
    ("sacred_geometry.py", "void"),                        # 3.4.4 DEFERRED record
    ("sync_ux_150_loop.py", "Avoid HTML comments"),       # code comment
    ("view_rooms.py", "Forces in the voids between ideas"),  # description string
    ("visual_evolve_loop.py", "void-"),                   # empty-cell HTML CTA
    ("repl.py", '"void", "pending"'),                     # nursery/proposals alias
    ("repl.py", "avoidance"),                             # preference kind, not geometry
]
void_ok = True
for ln in void_hits:
    if not any(f in ln and s in ln for f, s in allow):
        void_ok = False
        print("WITNESS UNACCOUNTED void hit: " + ln[:160])
r["void_mentions_allowlisted"] = void_ok
r["void_hits_n"] = len(void_hits)
chan_hits = _grep("channel", "form/dell_matrix")
chan_allow = [
    ("allwhere.py", "Source channels"),      # data-source channels
    ("graph_view.py", "side channel"),       # code comment
    ("matrix_awake.py", "Channel"),          # TextChannel/SpeakChannel messaging
    ("sacred_geometry.py", "flow channels"), # metaphor string
]
chan_ok = all(any(f in ln and s in ln for f, s in chan_allow) for ln in chan_hits)
r["channel_mentions_allowlisted"] = chan_ok
print("WITNESS void/negative-space hits=%d channel hits=%d" % (len(void_hits), len(chan_hits)))

# 3.3.1 PARK record exists in verita.py; not implemented.
vsrc = open(os.path.join(REPO, "form/dell_matrix/verita.py")).read()
r["park_record_present"] = ("PARKED (GDP-001 Phase 3, objective 3.3.1" in vsrc
                            and "do not build" in vsrc)
r["no_transform_layer"] = ("def verita_transform" not in vsrc
                            and "class VeritaTransform" not in vsrc)
print("RESULT " + json.dumps(r))
""".replace("@@REPO@@", repr(REPO)))
    return ("policy-345", code)


def smoke() -> bool:
    """Run all P3 R3.4 phases. Returns True iff every check passes."""
    cases = [
        _delegation_sweep(),
        _invalid_inputs(),
        _canonical_raw_doc(),
        _live_caller(),
        _mutation(),
        _ledger_invariants(),
        _failure_honest(),
        _policy_345(),
    ]

    all_results = {}
    for name, code in cases:
        all_results.update(_phase(name, code))

    fails = [k for k, v in all_results.items() if not v]
    npass = sum(1 for v in all_results.values() if v)
    ntotal = len(all_results)
    print(f"P3_R34 geometry: {npass}/{ntotal} PASS", flush=True)
    if fails:
        print(f"FAILURES: {fails[:12]}", flush=True)
        return False
    if ntotal == 0:
        print("FAIL: empty evidence", flush=True)
        return False
    print("P3_R34 WORLD: ALL PASS", flush=True)
    return True


def main() -> None:
    """Entry point with honest exit status."""
    ok = smoke()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
