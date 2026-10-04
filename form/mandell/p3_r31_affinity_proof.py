"""P3 R3.1 affinity proof — _affinity contract, serendipity, seeded IDs.

GDP-001 Phase 3, R3.1 (3.1.1-3.1.5). NON-VACUOUS (P3R rewrite, 2026-10-04):
  - Content-bearing canonical fixtures: real plane units with overlapping
    token content ("river"/"stream" sharing water/flow), not empty mocks.
  - Independently expected results: hand-computed affinity for a small
    pair IN COMMENTS (every term derived by hand), asserted with
    tolerance; hand-computed missing-unit value (0.0273) asserted by repr.
  - Bypass-must-fail tests:
      * lifecycle: faded_policy.is_faded patched OFF -> a faded pair's
        affinity MUST leak back above 0 (else the filter is decorative).
      * consumption: rg._affinity patched to the zeroed dict -> the
        RingedGrowth.run gate consumer MUST stop proposing (else affinity
        is not what drives proposals).
  - True bounds: <= 1.0 with body_boost == 0.0; <= 1.15 theoretical with
    body_boost (the old "[0,1]" shorthand is withdrawn — see contract).
  - Permutation: the full output dict is BITWISE identical under argument
    permutation (verified over seeded random pairs).

Portable: derives REPO from __file__.
Enforced: smoke() -> bool, sys.exit(0/1), registered in form.regress.

Test realism labels (honest):
  UNIT          — pure-function checks in this process.
  INTEGRATION   — real _affinity on real plane units (blank cube),
                  real RingedGrowth.run (same process).
  CROSS_PROCESS — fresh `python3` subprocesses re-derive the same values
                  under differing PYTHONHASHSEED.

3.1.4 finding (in nursery._slug): proposal IDs are deterministic given
(seed, label, add-sequence) in every process. Pre-Phase-3 they were
deterministic only within one process because _slug used hash(text),
which Python salts per process for str.
"""

from __future__ import annotations

import json
import os
import random
import subprocess
import sys
import tempfile

# Portable: derive repo root from this file's location.
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, REPO)

from form.dell_matrix import ringed_growth as rg  # noqa: E402
from form.dell_matrix import faded_policy  # noqa: E402
from form.dell_matrix.blank_cube import give  # noqa: E402
from form.dell_matrix.plane import Skin  # noqa: E402

OWNER = "P3R31"

_results: dict = {}


def rec(name: str, ok: bool, detail: str = "") -> None:
    _results[name] = bool(ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}"
          + (f" | {detail}" if detail else ""), flush=True)


def _fixture_plane():
    """Content-bearing fixtures: two token-overlapping units + one distant.

    u1 "river": tokens {river, water, flow} at (0,0).
    u2 "stream": tokens {stream, water, flow} at (3,4) -> distance 5.
    u3 "melody": disjoint tokens, far away (negative control).
    """
    cube = give(OWNER, clean=True)
    cube.place_idea("u1", "river", words="river water flow",
                    skin=Skin.SEED, x=0.0, y=0.0)
    cube.place_idea("u2", "stream", words="stream water flow",
                    skin=Skin.SEED, x=3.0, y=4.0)
    cube.place_idea("u3", "melody", words="song rhythm tune",
                    skin=Skin.SEED, x=40.0, y=0.0)
    return cube.session.plane


def t_hand_computed_affinity() -> None:
    """3.1.1: every term of _affinity derived BY HAND, then asserted.

    HAND COMPUTATION for (u1, u2):
      T1 = {river, water, flow}, T2 = {stream, water, flow}
      jaccard = |{water,flow}| / |{river,stream,water,flow}| = 2/4 = 0.5
      tension: only sets {river} / {stream} -> bridge = min(1,1) = 1;
               t = 1 / (1 + |union|) = 1/5 = 0.2
      harmonic = (2*j*(j+t)) / (2*j + t + 1e-9)
               = (2*0.5*0.7) / (1.0 + 0.2 + 1e-9)
               = 0.7 / 1.200000001
      distance = hypot(3,4) = 5.0 -> spatial = 1/(1+5) = 1/6
      in_scope = 1.0 (both non-sandboxed; u2 in enhance_scope(u1))
      goal_boost = 0.0 (no goals); body_boost = 0.0 (body=None)
      affinity = 0.40*h + 0.22*0.5 + 0.13*(1/6) + 0.13*1.0
    """
    plane = _fixture_plane()
    d = rg._affinity(plane, "u1", "u2")

    h_hand = (2 * 0.5 * (0.5 + 0.2)) / (2 * 0.5 + 0.2 + 1e-9)
    aff_hand = 0.40 * h_hand + 0.22 * 0.5 + 0.13 * (1.0 / 6.0) + 0.13 * 1.0

    rec("hand::keys", set(d) == {"affinity", "jaccard", "harmonic",
                                 "distance", "shared", "goal_boost",
                                 "body_boost"})
    rec("hand::types", all(isinstance(v, float) for v in d.values()))
    rec("hand::jaccard", d["jaccard"] == 0.5, f"got {d['jaccard']!r}")
    rec("hand::harmonic", abs(d["harmonic"] - h_hand) < 1e-12,
        f"got {d['harmonic']!r} hand={h_hand!r}")
    rec("hand::distance", d["distance"] == 5.0)
    rec("hand::shared", d["shared"] == 2.0)
    rec("hand::boosts_zero", d["goal_boost"] == 0.0 and d["body_boost"] == 0.0)
    rec("hand::affinity", abs(d["affinity"] - aff_hand) < 1e-9,
        f"got {d['affinity']!r} hand={aff_hand!r}")
    # The distant disjoint pair scores strictly lower (ordering, not just range).
    d_far = rg._affinity(plane, "u1", "u3")
    rec("hand::ordering", d_far["affinity"] < d["affinity"],
        f"near={d['affinity']:.4f} far={d_far['affinity']:.4f}")


def t_missing_unit() -> None:
    """3.1.1 failure behavior: HAND-COMPUTED missing-unit value.

    HAND COMPUTATION for a missing unit: tokens empty -> jaccard 0,
    harmonic 0; distance sentinel 99.0 -> spatial = 1/(1+99) = 0.01;
    enhance_scope -> [] so in_scope floor 0.2; boosts 0.0.
      affinity = 0.40*0 + 0.22*0 + 0.13*0.01 + 0.13*0.2 + 0 + 0
               = 0.0013 + 0.026 = 0.0273   (NOT 0.0)
    Fail-closed IN EFFECT: 0.0273 < STANSTILL_AFFINITY (0.10), so the
    gate is "None" and no ring proposal results. No exception raised.
    """
    plane = _fixture_plane()
    try:
        m1 = rg._affinity(plane, "u1", "missing")
        m2 = rg._affinity(plane, "missing", "also_missing")
        noexc = True
    except Exception as e:  # noqa: BLE001
        noexc = False
        m1 = m2 = {}
        print(f"    raised {e!r}", flush=True)
    rec("missing::no_exception", noexc)
    if not noexc:
        return
    expect = 0.13 * (1.0 / 100.0) + 0.13 * 0.2
    rec("missing::hand_value", abs(m1["affinity"] - expect) < 1e-15,
        f"got {m1['affinity']!r} hand={expect!r}")
    rec("missing::repr", repr(m1["affinity"]) == "0.0273",
        f"repr={m1['affinity']!r}")
    rec("missing::not_zero", m1["affinity"] != 0.0,
        "the old 'affinity 0.0' shorthand is falsified")
    rec("missing::fail_closed",
        m1["distance"] == 99.0 and m1["jaccard"] == 0.0
        and m1["harmonic"] == 0.0 and m1["shared"] == 0.0
        and m1["goal_boost"] == 0.0 and m1["body_boost"] == 0.0
        and rg._ring_phase(m1["affinity"]) == "None"
        and rg._ring_phase(m2["affinity"]) == "None",
        f"gate={rg._ring_phase(m1['affinity'])!r}")


def t_bounds() -> None:
    """3.1.1 true bounds: <= 1.0 without body boost; <= 1.15 with it."""
    plane = _fixture_plane()
    ok = True
    worst = 0.0
    for a in plane.units:
        for b in plane.units:
            if a == b:
                continue
            d = rg._affinity(plane, a, b)
            worst = max(worst, d["affinity"])
            if d["affinity"] < 0.0 or d["affinity"] > 1.0 + 1e-9:
                ok = False
    rec("bounds::no_body_le_1", ok, f"worst={worst:.4f}")

    # Theoretical corner: identical co-located in-scope units, identical
    # goals, body naming 3 missing organs in the labels:
    #   0.40*~1 + 0.22*1 + 0.13*1 + 0.13*1 + 0.12 + 0.15 ~= 1.15
    # (harmonic is 1 - 5e-10 from the 1e-9 epsilon). This CONSTRUCTS a
    # value above 1.0, falsifying the old "[0,1]" bound.
    cube = give(OWNER, clean=True)
    lab, w = "Floor nursery lattice core", "floor nursery lattice core"
    cube.place_idea("ca", lab, words=w, goals=["floor nursery lattice"],
                    skin=Skin.BUILDING, x=1.0, y=2.0)
    cube.place_idea("cb", lab, words=w, goals=["floor nursery lattice"],
                    skin=Skin.BUILDING, x=1.0, y=2.0)
    p2 = cube.session.plane
    body = {"missing": ["floor", "nursery", "lattice"], "present": []}
    dc = rg._affinity(p2, "ca", "cb", body=body)
    rec("bounds::corner_above_1", dc["affinity"] > 1.0,
        f"got {dc['affinity']!r} (old [0,1] bound falsified)")
    rec("bounds::corner_le_1_15", dc["affinity"] <= 1.15 + 1e-9,
        f"got {dc['affinity']!r}")
    rec("bounds::body_boost_capped", dc["body_boost"] == 0.15)


def t_permutation() -> None:
    """3.1.1: full output dict BITWISE identical under argument permutation."""
    plane = _fixture_plane()
    pairs = [("u1", "u2"), ("u1", "u3"), ("u2", "u3")]
    ok = all(rg._affinity(plane, a, b) == rg._affinity(plane, b, a)
             for a, b in pairs)
    rec("perm::fixture_bitwise", ok)
    # Seeded sweep over random label/word/coordinate content.
    rng = random.Random(20261004)
    vocab = ["river", "stream", "water", "flow", "bank", "stone",
             "bridge", "forest", "meadow", "path", "light", "delta"]
    pl = give(OWNER, clean=True).session.plane
    from form.dell_matrix.plane import Unit
    ids = [f"w{i}" for i in range(6)]
    for i in ids:
        pl.units[i] = Unit(
            id=i, label=" ".join(rng.choice(vocab) for _ in range(3)),
            words=" ".join(rng.choice(vocab) for _ in range(rng.randint(0, 6))),
            x=rng.uniform(-5, 5), y=rng.uniform(-5, 5))
    mism = sum(1 for _ in range(500)
               for x, y in [rng.sample(ids, 2)]
               if rg._affinity(pl, x, y) != rg._affinity(pl, y, x))
    rec("perm::sweep_bitwise", mism == 0, f"mismatches={mism}/500")


def t_serendipity() -> None:
    """3.1.3: serendipity = t/(1+t) in [0,1); the exposed tension subterm."""
    s = rg.serendipity
    rec("ser::range", all(0.0 <= v < 1.0 for v in
                           (s({"a", "b"}, {"b", "c"}),
                            s({"x"}, {"y", "z", "w"}),
                            s({"p", "q", "r"}, {"s", "t"}))))
    rec("ser::empty", s(set(), set()) == 0.0 and s({"a"}, set()) == 0.0)
    rec("ser::identical_zero", s({"a", "b"}, {"a", "b"}) == 0.0)
    rec("ser::symmetric",
        s({"a", "b", "x"}, {"c", "d", "x"}) == s({"c", "d", "x"}, {"a", "b", "x"}))
    # More complementary exclusive tokens -> non-decreasing.
    rec("ser::monotone",
        0.0 < s({"x"}, {"y"}) <= s({"x", "p", "q"}, {"y", "r", "s"}) < 1.0)
    # serendipity() is the NORMALIZED twin of the raw _tension term that
    # _harmonic consumes directly (code-verified: _harmonic calls
    # _tension, not serendipity). Fixture needs BOTH overlap and
    # exclusive tokens: jac = 1/5, tension = 2/6.
    a, b = {"a", "b", "x"}, {"b", "c", "y"}
    t = rg._tension(a, b)
    rec("ser::normalizes_tension", abs(s(a, b) - t / (1.0 + t)) < 1e-15)
    # _harmonic still consumes the tension subterm (mutation detects
    # suppression): with tension zeroed, harmonic collapses to jaccard.
    before = rg._harmonic(a, b)
    assert before > rg._jaccard(a, b) > 0, "fixture must carry tension"
    orig = rg._tension
    try:
        rg._tension = lambda x, y: 0.0  # noqa: E731 -- deliberate
        after = rg._harmonic(a, b)
        rec("ser::tension_load_bearing",
            before != after
            and abs(after - rg._jaccard(a, b)) < 1e-6,
            f"{before:.4f} -> {after:.4f} (collapses to jaccard)")
    finally:
        rg._tension = orig
    rec("ser::restored", rg._harmonic(a, b) == before)


def t_bypass_lifecycle() -> None:
    """BYPASS-MUST-FAIL (lifecycle): with the faded filter disabled, a
    faded pair's affinity MUST leak back above 0. If it stays 0.0, the
    filter is decorative and the proof fails."""
    plane = _fixture_plane()
    plane.units["u2"].lifecycle_state = "faded"
    try:
        z = rg._affinity(plane, "u1", "u2")["affinity"]
        rec("lifecycle::faded_zero", z == 0.0, "filter active -> 0.0")
        orig = faded_policy.is_faded
        faded_policy.is_faded = lambda obj: False  # BYPASS the filter
        try:
            leaked = rg._affinity(plane, "u1", "u2")["affinity"]
        finally:
            faded_policy.is_faded = orig
        rec("lifecycle::bypass_leaks", leaked > 0.0,
            f"filter disabled -> affinity={leaked:.4f} (must be > 0)")
        rec("lifecycle::restored",
            rg._affinity(plane, "u1", "u2")["affinity"] == 0.0)
    finally:
        del plane.units["u2"].lifecycle_state


def t_bypass_consumption() -> None:
    """BYPASS-MUST-FAIL (consumption): RingedGrowth.run's gates consume
    _affinity. With _affinity patched to the zeroed dict, the run MUST
    stop proposing. If proposals still appear, affinity is not what
    drives growth and the proof fails."""
    plane = _fixture_plane()
    tmp = tempfile.mktemp(prefix="p3r31_b_", suffix=".json")
    try:
        from form.dell_matrix.nursery import Nursery
        n1 = Nursery(path=tmp)
        real_out = rg.RingedGrowth(nursery=n1, seed=7).run(plane, cycles=1)
        n_real = real_out["proposed_new"] + real_out["proposed_evolved"]
        rec("consume::real_proposes", n_real > 0, f"n={n_real}")
        if n_real == 0:
            rec("consume::bypass_stops", False,
                "fixture yields no proposals; causality untestable")
            return
        zeroed = {"affinity": 0.0, "jaccard": 0.0, "harmonic": 0.0,
                  "distance": 0.0, "shared": 0.0, "goal_boost": 0.0,
                  "body_boost": 0.0}
        orig = rg._affinity
        rg._affinity = lambda plane, a, b, body=None: dict(zeroed)  # BYPASS
        try:
            n2 = Nursery(path=tmp + "2")
            out = rg.RingedGrowth(nursery=n2, seed=7).run(plane, cycles=1)
            n_byp = out["proposed_new"] + out["proposed_evolved"]
        finally:
            rg._affinity = orig
            try:
                os.remove(tmp + "2")
            except OSError:
                pass
        rec("consume::bypass_stops", n_byp == 0,
            f"affinity zeroed -> proposals={n_byp} (must be 0)")
        rec("consume::causal", n_byp != n_real,
            "output changed when affinity was bypassed")
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass


def t_seeded_ids() -> None:
    """3.1.4: _slug deterministic across processes; seed matters."""
    from form.dell_matrix.nursery import Nursery, _slug
    rec("slug::stable", _slug("Restore floor", seed=7) == _slug("Restore floor", seed=7))
    rec("slug::seed_matters",
        _slug("Restore floor", seed=7) != _slug("Restore floor", seed=8))
    t1 = tempfile.mktemp(prefix="p3r31_n1_", suffix=".json")
    t2 = tempfile.mktemp(prefix="p3r31_n2_", suffix=".json")
    try:
        p1 = Nursery(path=t1).add(label="Restore floor", words="w",
                                   kind="evolved", seed=7)
        p2 = Nursery(path=t2).add(label="Restore floor", words="w",
                                   kind="evolved", seed=7)
        rec("slug::nursery_deterministic", p1.id == p2.id, f"id={p1.id[:32]}")
    finally:
        for t in (t1, t2):
            try:
                os.remove(t)
            except OSError:
                pass


def t_cross_process() -> None:
    """CROSS_PROCESS: fresh interpreters re-derive identical values."""
    sys.path.insert(0, REPO)
    plane = _fixture_plane()
    baseline = json.dumps(rg._affinity(plane, "u1", "u2"), sort_keys=True)
    code = (
        "import sys, json; sys.path.insert(0, %r);"
        "from form.dell_matrix.blank_cube import give;"
        "from form.dell_matrix.plane import Skin;"
        "from form.dell_matrix import ringed_growth as rg;"
        "cube = give(%r, clean=True);"
        "cube.place_idea('u1', 'river', words='river water flow', skin=Skin.SEED, x=0.0, y=0.0);"
        "cube.place_idea('u2', 'stream', words='stream water flow', skin=Skin.SEED, x=3.0, y=4.0);"
        "d = rg._affinity(cube.session.plane, 'u1', 'u2');"
        "print('RESULT ' + json.dumps({"
        "'same': json.dumps(d, sort_keys=True) == %r,"
        "'perm': d == rg._affinity(cube.session.plane, 'u2', 'u1')}))"
    ) % (REPO, OWNER, baseline)
    r = subprocess.run([sys.executable, "-c", code], cwd=REPO,
                       capture_output=True, text=True, timeout=120,
                       env=dict(os.environ, PYTHONHASHSEED="random"))
    found = {}
    for line in r.stdout.splitlines():
        if line.startswith("RESULT "):
            found = json.loads(line[len("RESULT "):])
    rec("xproc::affinity_identical", r.returncode == 0 and found.get("same") is True,
        f"rc={r.returncode}")
    rec("xproc::perm_bitwise", found.get("perm") is True)
    # _slug stable across hash seeds.
    from form.dell_matrix.nursery import _slug
    slug7 = _slug("Restore floor", seed=7)
    ok = True
    for hs in ("1", "987654"):
        rr = subprocess.run(
            [sys.executable, "-c",
             "import sys; sys.path.insert(0, %r);"
             "from form.dell_matrix.nursery import _slug;"
             "print('RESULT ' + __import__('json').dumps("
             "{'same': _slug('Restore floor', seed=7) == %r}))" % (REPO, slug7)],
            cwd=REPO, capture_output=True, text=True, timeout=120,
            env=dict(os.environ, PYTHONHASHSEED=hs))
        good = False
        for line in rr.stdout.splitlines():
            if line.startswith("RESULT "):
                good = json.loads(line[len("RESULT "):]).get("same") is True
        ok = ok and rr.returncode == 0 and good
    rec("xproc::slug_hashseed_stable", ok)


def smoke() -> bool:
    """Run all P3 R3.1 cases. Returns True iff all pass."""
    print("=== P3 R3.1 AFFINITY PROOF (non-vacuous) ===", flush=True)
    _results.clear()
    t_hand_computed_affinity()
    t_missing_unit()
    t_bounds()
    t_permutation()
    t_serendipity()
    t_bypass_lifecycle()
    t_bypass_consumption()
    t_seeded_ids()
    t_cross_process()
    fails = [k for k, v in _results.items() if not v]
    npass = sum(1 for v in _results.values() if v)
    ntotal = len(_results)
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
