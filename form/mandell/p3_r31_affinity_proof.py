"""P3 R3.1 affinity proof — _affinity contract, serendipity, seeded IDs.

GDP-001 Phase 3, R3.1 (3.1.1-3.1.5). Portable: derives REPO from __file__.
Enforced: smoke() -> bool, sys.exit(0/1), registered in form.regress.

Evidence classes (labeled honestly):
- UNIT: pure-function checks in this process (serendipity/_harmonic/_slug).
- INTEGRATION: real _affinity on real idea objects via blank_cube.give
  (same process), plus the live RingedGrowth.run witness.
- CROSS_PROCESS: fresh `python3` subprocesses re-derive the same values
  (affinity dict, serendipity, slug under differing PYTHONHASHSEED).

Each case proves:
1. _affinity returns the contract dict on healthy inputs (keys/types).
2. Missing units -> NO exception; fail-closed in effect (affinity ~0.0273,
   below the lowest ring gate, so no proposal; the matrix's literal
   "affinity 0.0" shorthand is falsified and documented as such).
3. Same inputs -> identical outputs, twice (in-process determinism).
4. Cross-process: same rebuilt inputs -> identical affinity dict.
5. serendipity in [0,1): bounds, empty->0.0, symmetry, monotonicity.
6. _harmonic still uses the tension subterm (mutation test detects
   suppression of _tension).
7. affinity bounds: >= 0.0; <= 1.0 when body_boost == 0.0; <= 1.15 general
   (documented invariant, contract docstring in ringed_growth.py).
8. Seeded IDs: _slug deterministic across processes (was NOT before
   Phase 3: hash() salt made it process-random); different seeds differ;
   RingedGrowth.run(seed) yields deterministic proposal IDs end to end.
9. Live-path witness: real RingedGrowth.run on a real plane records what
   it did (gates, proposals, nursery IDs).

3.1.4 finding (documented here and in nursery._slug): proposal IDs are now
deterministic given (seed, label, add-sequence) in every process. Previously
they were deterministic only within one process because _slug used
hash(text), which Python salts per process for str.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile

# Portable: derive repo root from this file's location.
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OWNER = "P3R31"  # Isolated namespace


def _phase(name: str, code: str, env: dict | None = None) -> dict:
    """Run one phase in a fresh process. Returns {check_name: bool}."""
    r = subprocess.run(
        [sys.executable, "-c", code],
        cwd=REPO, capture_output=True, text=True, timeout=120,
        env=env)
    results = {}
    if r.returncode != 0:
        results[f"{name}::crashed"] = False
        results[f"{name}::stderr"] = False
        return results
    for line in r.stdout.splitlines():
        if line.startswith("RESULT "):
            try:
                d = json.loads(line[len("RESULT "):])
                for k, v in d.items():
                    results[f"{name}::{k}"] = bool(v)
            except json.JSONDecodeError:
                results[f"{name}::bad_json"] = False
    if not results:
        results[f"{name}::empty_evidence"] = False
    return results


BUILD = """
import sys
sys.path.insert(0, %(REPO)r)
from form.dell_matrix.blank_cube import give
from form.dell_matrix.plane import Skin
cube = give(%(OWNER)r, clean=True)
cube.place_idea("alpha", "Alpha routes", words="crm routes delivery", skin=Skin.BUILDING, x=1.0)
cube.place_idea("beta", "Beta routes", words="crm routes pickup", skin=Skin.BUILDING, x=-1.0)
cube.place_idea("gamma", "Gamma melody", words="song harmony rhythm", skin=Skin.SEED, x=0.0, y=2.0)
plane = cube.session.plane
r = {}
"""

EMIT = """
print("RESULT " + json.dumps(r))
"""

AFFINITY_JSON = """
import json
from form.dell_matrix import ringed_growth as rg
d = rg._affinity(plane, "alpha", "beta")
r["json"] = json.dumps(d, sort_keys=True)
"""


def _inprocess_cases() -> dict:
    """UNIT + INTEGRATION evidence, same process."""
    sys.path.insert(0, REPO)
    from form.dell_matrix import ringed_growth as rg
    from form.dell_matrix.nursery import Nursery, _slug
    from form.dell_matrix.blank_cube import give
    from form.dell_matrix.plane import Skin

    r = {}

    # --- healthy control on real idea objects (INTEGRATION) ---
    cube = give(OWNER, clean=True)
    cube.place_idea("alpha", "Alpha routes", words="crm routes delivery",
                    skin=Skin.BUILDING, x=1.0)
    cube.place_idea("beta", "Beta routes", words="crm routes pickup",
                    skin=Skin.BUILDING, x=-1.0)
    cube.place_idea("gamma", "Gamma melody", words="song harmony rhythm",
                    skin=Skin.SEED, x=0.0, y=2.0)
    plane = cube.session.plane

    d = rg._affinity(plane, "alpha", "beta")
    expect_keys = {"affinity", "jaccard", "harmonic", "distance",
                   "shared", "goal_boost", "body_boost"}
    r["aff_keys"] = (set(d.keys()) == expect_keys)
    r["aff_types"] = all(isinstance(v, float) for v in d.values())
    r["aff_bounds"] = (0.0 <= d["affinity"]
                       and 0.0 <= d["jaccard"] <= 1.0
                       and 0.0 <= d["harmonic"] <= 1.0
                       and d["distance"] >= 0.0)
    r["aff_healthy_positive"] = (d["affinity"] > 0.0)  # overlapping tokens

    # --- negative controls: missing units -> no exception, fail-closed in effect (INTEGRATION) ---
    # Matrix premise "affinity 0.0" FALSIFIED by repository reality: the
    # spatial/in_scope floors contribute ~0.0273. Documented in the _affinity
    # contract; fail-closed because 0.0273 < STANSTILL_AFFINITY (gate "None").
    try:
        m1 = rg._affinity(plane, "alpha", "missing")
        m2 = rg._affinity(plane, "missing", "also_missing")
        r["aff_missing_noexc"] = True
        r["aff_missing_failclosed"] = (
            m1["distance"] == 99.0 and m2["distance"] == 99.0
            and m1["jaccard"] == 0.0 and m1["harmonic"] == 0.0
            and m1["shared"] == 0.0 and m1["goal_boost"] == 0.0
            and m1["body_boost"] == 0.0
            and set(m1.keys()) == expect_keys
            and rg._ring_phase(m1["affinity"]) == "None"
            and rg._ring_phase(m2["affinity"]) == "None")
    except Exception:
        r["aff_missing_noexc"] = False
        r["aff_missing_failclosed"] = False

    # --- determinism, same inputs twice (INTEGRATION) ---
    d2 = rg._affinity(plane, "alpha", "beta")
    r["aff_deterministic"] = (d == d2)

    # --- upper-bound sweep (UNIT over real pairs) ---
    worst = 0.0
    bound_ok = True
    for a in plane.units:
        for b in plane.units:
            if a == b:
                continue
            dd = rg._affinity(plane, a, b)
            worst = max(worst, dd["affinity"])
            if dd["affinity"] < 0.0:
                bound_ok = False
            # body_boost == 0.0 here (body=None): documented invariant aff <= 1.0
            if dd["body_boost"] == 0.0 and dd["affinity"] > 1.0 + 1e-9:
                bound_ok = False
            if dd["affinity"] > 1.15 + 1e-9:
                bound_ok = False
    r["aff_bound_sweep"] = bound_ok
    r["aff_worst_seen"] = (worst <= 1.15 + 1e-9)

    # --- serendipity: bounds, empty, symmetry, monotonicity (UNIT) ---
    s = rg.serendipity({"a", "b"}, {"b", "c"})
    r["ser_bounds"] = (0.0 <= s < 1.0)
    r["ser_empty"] = (rg.serendipity(set(), set()) == 0.0
                      and rg.serendipity({"a"}, set()) == 0.0)
    r["ser_symmetric"] = (rg.serendipity({"a", "b", "x"}, {"c", "d", "x"})
                          == rg.serendipity({"c", "d", "x"}, {"a", "b", "x"}))
    r["ser_identical_zero"] = (rg.serendipity({"a", "b"}, {"a", "b"}) == 0.0)
    # monotonicity spot-check: more complementary exclusive tokens -> non-decreasing
    s1 = rg.serendipity({"x"}, {"y"})
    s2 = rg.serendipity({"x", "p", "q"}, {"y", "r", "s"})
    r["ser_monotone"] = (0.0 < s1 <= s2 < 1.0)

    # --- _harmonic formula consistency after refactor (UNIT) ---
    a, b = {"a", "b", "x"}, {"b", "c", "y"}
    jac = rg._jaccard(a, b)
    ten = rg._tension(a, b)
    expect = 0.0 if (jac <= 0 and ten <= 0) else (2 * jac * (jac + ten)) / (2 * jac + ten + 1e-9)
    r["harmonic_formula_stable"] = (rg._harmonic(a, b) == expect)
    r["harmonic_empty"] = (rg._harmonic(set(), set()) == 0.0)

    # --- mutation test: suppress _tension -> _harmonic must change (UNIT) ---
    base_sets = ({"a", "b", "x"}, {"b", "c", "y"})
    before = rg._harmonic(*base_sets)
    orig_tension = rg._tension
    try:
        rg._tension = lambda x, y: 0.0  # noqa: E731 -- deliberate suppression
        after = rg._harmonic(*base_sets)
        # 1e-9 epsilon in the denominator: compare with tolerance, not ==.
        r["mutation_detected"] = (before != after
                                  and abs(after - rg._jaccard(*base_sets)) < 1e-6)
    finally:
        rg._tension = orig_tension
    r["mutation_restored"] = (rg._harmonic(*base_sets) == before)
    # honest wiring check: with tension suppressed the harmonic term collapses to jaccard
    try:
        rg._tension = lambda x, y: 0.0  # noqa: E731
        da2 = rg._affinity(plane, "alpha", "gamma")
        r["mutation_wiring"] = abs(da2["harmonic"] - rg._jaccard(
            rg._tokens_uid(plane, "alpha"), rg._tokens_uid(plane, "gamma"))) < 1e-9
    finally:
        rg._tension = orig_tension

    # --- seeded IDs (UNIT + subprocess-comparable) ---
    r["slug_stable"] = (_slug("Restore floor", seed=7) == _slug("Restore floor", seed=7))
    r["slug_seed_matters"] = (_slug("Restore floor", seed=7) != _slug("Restore floor", seed=8))
    r["slug_seed7_value"] = bool(_slug("Restore floor", seed=7))

    # --- Nursery.add end-to-end determinism, isolated temp file ---
    tmp1 = tempfile.mktemp(prefix="p3r31_n1_", suffix=".json")
    tmp2 = tempfile.mktemp(prefix="p3r31_n2_", suffix=".json")
    try:
        n1 = Nursery(path=tmp1)
        n2 = Nursery(path=tmp2)
        p1 = n1.add(label="Restore floor", words="w", kind="evolved", seed=7)
        p2 = n2.add(label="Restore floor", words="w", kind="evolved", seed=7)
        r["nursery_add_deterministic"] = (p1.id == p2.id)
    finally:
        for t in (tmp1, tmp2):
            try:
                os.remove(t)
            except OSError:
                pass

    # --- live-path witness: real RingedGrowth.run (INTEGRATION) ---
    tmpn = tempfile.mktemp(prefix="p3r31_live_", suffix=".json")
    witness = {}
    try:
        from form.dell_matrix.ringed_growth import RingedGrowth
        nurs = Nursery(path=tmpn)
        eng = RingedGrowth(nursery=nurs, seed=7)
        out = eng.run(plane, cycles=1)
        witness = {
            "ok": out.get("ok"),
            "proposed_new": out.get("proposed_new"),
            "proposed_evolved": out.get("proposed_evolved"),
            "gates": out.get("gates"),
            "ids": sorted(nurs.proposals.keys()),
        }
        r["live_run_ok"] = (out.get("ok") is True and isinstance(out.get("steps"), list))
        # second identical run (fresh nursery, same seed) -> same IDs
        tmpn2 = tempfile.mktemp(prefix="p3r31_live2_", suffix=".json")
        try:
            nurs2 = Nursery(path=tmpn2)
            eng2 = RingedGrowth(nursery=nurs2, seed=7)
            eng2.run(plane, cycles=1)
            r["live_ids_deterministic"] = (sorted(nurs2.proposals.keys())
                                           == sorted(nurs.proposals.keys()))
        finally:
            try:
                os.remove(tmpn2)
            except OSError:
                pass
    finally:
        try:
            os.remove(tmpn)
        except OSError:
            pass
    r["live_witness_recorded"] = bool(witness)
    print("LIVE WITNESS: " + json.dumps(witness, default=str))

    return r


def _cross_process_cases() -> dict:
    """CROSS_PROCESS evidence: fresh python3 processes re-derive values."""
    sys.path.insert(0, REPO)
    from form.dell_matrix import ringed_growth as rg

    # baseline affinity json, computed in this process
    from form.dell_matrix.blank_cube import give
    from form.dell_matrix.plane import Skin
    cube = give(OWNER, clean=True)
    cube.place_idea("alpha", "Alpha routes", words="crm routes delivery",
                    skin=Skin.BUILDING, x=1.0)
    cube.place_idea("beta", "Beta routes", words="crm routes pickup",
                    skin=Skin.BUILDING, x=-1.0)
    cube.place_idea("gamma", "Gamma melody", words="song harmony rhythm",
                    skin=Skin.SEED, x=0.0, y=2.0)
    plane = cube.session.plane
    import json as _json
    baseline = _json.dumps(rg._affinity(plane, "alpha", "beta"), sort_keys=True)

    out = {}
    # same rebuilt inputs in a fresh process -> identical affinity dict
    code = (BUILD % {"REPO": REPO, "OWNER": OWNER}
            + AFFINITY_JSON + """
r["same"] = (r["json"] == %(BASELINE)r)
r["keys_ok"] = (sorted(json.loads(r["json"]).keys())
                == ["affinity", "body_boost", "distance", "goal_boost",
                    "harmonic", "jaccard", "shared"])
""" + EMIT) % {"BASELINE": baseline}
    out.update(_phase("xproc-affinity", code,
                      env=dict(os.environ, PYTHONHASHSEED="random")))

    # slug stability across differing hash seeds
    slug7 = __import__("form.dell_matrix.nursery", fromlist=["_slug"])._slug(
        "Restore floor", seed=7)
    for seed_env, tag in (("1", "seed1"), ("987654", "seed987654")):
        out.update(_phase(f"xproc-slug-{tag}",
                          """
import sys
sys.path.insert(0, %(REPO)r)
from form.dell_matrix.nursery import _slug
r = {}
r["slug"] = _slug("Restore floor", seed=7)
r["same"] = (r["slug"] == %(SLUG)r)
print("RESULT " + __import__("json").dumps(r))
""" % {"REPO": REPO, "SLUG": slug7},
                          env=dict(os.environ, PYTHONHASHSEED=seed_env)))

    # serendipity / harmonic in a fresh process
    s_base = rg.serendipity({"a", "b", "x"}, {"b", "c", "y"})
    h_base = rg._harmonic({"a", "b", "x"}, {"b", "c", "y"})
    out.update(_phase("xproc-serendipity",
                      """
import sys
sys.path.insert(0, %(REPO)r)
from form.dell_matrix import ringed_growth as rg
import json
r = {}
r["same_ser"] = (rg.serendipity({"a", "b", "x"}, {"b", "c", "y"}) == %(S)r)
r["same_harm"] = (rg._harmonic({"a", "b", "x"}, {"b", "c", "y"}) == %(H)r)
r["empty_zero"] = (rg.serendipity(set(), set()) == 0.0)
print("RESULT " + json.dumps(r))
""" % {"REPO": REPO, "S": s_base, "H": h_base}))
    return out


def smoke() -> bool:
    """Run all P3 R3.1 cases. Returns True iff all pass."""
    all_results = {}
    all_results.update({f"unit::{k}": v for k, v in _inprocess_cases().items()})
    all_results.update(_cross_process_cases())

    fails = [k for k, v in all_results.items() if not v]
    npass = sum(1 for v in all_results.values() if v)
    ntotal = len(all_results)
    print(f"P3 R3.1 affinity: {npass}/{ntotal} PASS", flush=True)
    if fails:
        print(f"FAILURES: {fails}", flush=True)
        return False
    if ntotal == 0:
        print("FAIL: empty evidence", flush=True)
        return False
    print("P3 R3.1 WORLD: ALL PASS", flush=True)
    return True


def main() -> None:
    """Entry point with honest exit status."""
    ok = smoke()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
