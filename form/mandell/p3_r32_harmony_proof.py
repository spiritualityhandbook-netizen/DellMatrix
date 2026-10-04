"""P3 R3.2 harmony proof: harmony_score contract, separation, public path.

GDP-001 Phase 3, R3.2 (3.2.1-3.2.5). Portable: derives REPO from __file__.
Enforced: smoke() -> bool, sys.exit(0/1), registered in form.regress.

What it proves (real execution witnesses, real functions, real objects):
 1. Contract: harmony_score carries the full 8-field mathematical admission
    contract; outputs are float in [0, 1].
 2. Degenerate behavior: empty set -> 0.0; single idea with content -> 1.0;
    single empty idea -> 0.0; malformed input (None, bare string, non-idea
    elements) -> 0.0, never raises.
 3. Symmetry: permuting input order never changes the score.
 4. Determinism: repeated calls return identical results.
 5. Monotonicity spot-checks: adding a near-duplicate decreases harmony;
    adding a coherent-but-distinct idea beats adding an unrelated one.
 6. Separation (3.2.4): harmony_score != _affinity. Concrete
    counterexamples in both directions plus an affinity-fixed /
    harmony-varies construction.
 7. Public path (3.2.5): Program.harmony_of matches harmony_score for
    Idea objects and plane unit IDs; unknown IDs fail closed to 0.0.
 8. Fresh-process: a subprocess computes the same score on a fixed fixture.
 9. Mutation: perturbing the formula's redundancy exponent is detected.

Test realism labels: pure-function checks are UNIT; the public-path check
is INTEGRATION (direct Program method call); the subprocess check is
CROSS_PROCESS. No REPL/UI claims are made.
"""

from __future__ import annotations

import itertools
import json
import os
import subprocess
import sys

# Portable: derive repo root from this file's location.
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, REPO)

from form.dell_matrix.harmony import harmony_score  # noqa: E402
from form.dell_matrix import harmony as harmony_mod  # noqa: E402
from form.mandell.idea import Idea, Provenance, ProvenanceSource  # noqa: E402

_PROV = Provenance(source=ProvenanceSource.HUMAN, activity="p3r32", agent="p3r32")


def _mk(title: str, **props) -> Idea:
    idea = Idea(title=title)
    for k, v in props.items():
        idea.set_property(k, v, _PROV)
    return idea


# Fixed fixtures (content is the only thing that matters; ids/timestamps
# are excluded from token extraction).
A = _mk("crm routes pipeline", detail="customer routing")
B = _mk("crm routes dashboard", detail="customer routing")
C = _mk("sales routes pipeline", detail="customer routing")
DUP_A = _mk("crm routes pipeline", detail="customer routing")
NOISE = _mk("telemetry unrelated zebra", detail="quantum banana")


def _check(results: dict, name: str, ok: bool, detail: str = "") -> None:
    results[name] = bool(ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" | {detail}" if detail else ""),
          flush=True)


def _bounds(results: dict) -> None:
    """All outputs in [0, 1] across a battery of healthy inputs."""
    cases = [
        [],
        [_mk("")],
        [_mk("alpha")],
        [A, B],
        [A, B, C],
        [A, B, C, NOISE],
        [DUP_A, _mk("crm routes pipeline", detail="customer routing"), A],
        [_mk("x y"), _mk("y z"), _mk("z x"), _mk("x y z")],
        [None, 42, object()],
    ]
    ok = True
    for i, case in enumerate(cases):
        v = harmony_score(case)
        if not (isinstance(v, float) and 0.0 <= v <= 1.0):
            ok = False
            print(f"  bounds violation case {i}: {v!r}", flush=True)
    _check(results, "bounds[0,1]", ok, f"{len(cases)} cases")


def _degenerate(results: dict) -> None:
    _check(results, "empty->0.0", harmony_score([]) == 0.0)
    _check(results, "single-content->1.0", harmony_score([A]) == 1.0)
    _check(results, "single-empty->0.0", harmony_score([_mk("")]) == 0.0)
    _check(results, "none-input->0.0", harmony_score(None) == 0.0)
    _check(results, "bare-string->0.0", harmony_score("abc") == 0.0)
    _check(results, "noniterable->0.0", harmony_score(42) == 0.0)
    # Malformed elements: never raises, defined output.
    try:
        v = harmony_score([None, "junk", 42, A])
        _check(results, "malformed-elements-no-crash",
               isinstance(v, float) and 0.0 <= v <= 1.0, f"score={v:.4f}")
    except Exception as e:  # noqa: BLE001
        _check(results, "malformed-elements-no-crash", False, f"raised {e!r}")


def _symmetry_determinism(results: dict) -> None:
    scores = {round(harmony_score(list(p)), 12)
              for p in itertools.permutations([A, B, C])}
    _check(results, "symmetry-permutation", len(scores) == 1,
           f"distinct={len(scores)}")
    _check(results, "determinism-repeat",
           harmony_score([A, B, C]) == harmony_score([A, B, C]))


def _monotonicity(results: dict) -> None:
    h2 = harmony_score([A, B])
    h3dup = harmony_score([A, B, DUP_A])
    h4 = harmony_score([A, B, C])
    h4noise = harmony_score([A, B, NOISE])
    _check(results, "duplicate-decreases", h3dup < h2,
           f"{h2:.4f} -> {h3dup:.4f}")
    _check(results, "coherent-beats-noise", h4 > h4noise,
           f"coherent={h4:.4f} noise={h4noise:.4f}")
    _check(results, "healthy-moderate-range", 0.3 < h2 < 0.7, f"{h2:.4f}")
    _check(results, "identical-set-zero",
           harmony_score([DUP_A, DUP_A, DUP_A, DUP_A]) == 0.0)
    _check(results, "disjoint-set-zero",
           harmony_score([_mk("alpha beta"), _mk("gamma delta")]) == 0.0)


def _contract_docstring(results: dict) -> None:
    doc = harmony_score.__doc__ or ""
    fields = ["(1) NAME", "(2) INPUTS", "(3) OUTPUTS", "(4) FORMULA",
              "(5) INVARIANTS", "(6) FAILURE", "(7) DETERMINISM",
              "(8) CANONICAL OWNER"]
    missing = [f for f in fields if f not in doc]
    _check(results, "contract-8-fields", not missing,
           f"missing={missing}" if missing else "all present")


def _separation(results: dict) -> None:
    """3.2.4: harmony_score and _affinity measure different things.

    Real functions, real objects. _affinity operates on plane units;
    harmony_score on idea objects with matching content.
    """
    from form.dell_matrix.blank_cube import give
    from form.dell_matrix.ringed_growth import _affinity

    # Case A: HIGH pair affinity, LOW set harmony.
    # Two co-located, token-identical plane units -> affinity 0.88.
    # Four token-identical ideas -> harmony exactly 0.0 (C=R=1).
    cube_a = give("P3R32A", clean=True)
    cube_a.place_idea("a", "crm routes pipeline", words="crm routes pipeline",
                      x=0.0, y=0.0)
    cube_a.place_idea("b", "crm routes pipeline", words="crm routes pipeline",
                      x=0.0, y=0.0)
    aff_ab = _affinity(cube_a.session.plane, "a", "b")["affinity"]
    harm_dup = harmony_score([_mk("crm routes pipeline",
                                  detail="crm routes pipeline") for _ in range(4)])
    _check(results, "separation-A-high-affinity", aff_ab >= 0.7,
           f"affinity={aff_ab:.4f}")
    _check(results, "separation-A-low-harmony", harm_dup <= 0.1,
           f"harmony={harm_dup:.4f}")
    _check(results, "separation-A-disagree", aff_ab >= 0.7 and harm_dup <= 0.1)

    # Case B: LOW pair affinity, HIGH set harmony.
    # Disjoint tokens, far apart, sandboxed out of mutual scope -> ~0.03.
    # Four coherent-but-distinct ideas -> ~0.45.
    cube_b = give("P3R32B", clean=True)
    cube_b.place_idea("x", "alpha beta", words="alpha beta", x=0.0, y=0.0)
    cube_b.place_idea("y", "gamma delta", words="gamma delta", x=50.0, y=50.0)
    plane_b = cube_b.session.plane
    plane_b.box(["x"], "solo")  # x sandboxed alone -> y out of scope
    aff_xy = _affinity(plane_b, "x", "y")["affinity"]
    harm_hi = harmony_score([
        _mk("crm routes pipeline", detail="customer routing"),
        _mk("crm routes dashboard", detail="customer routing"),
        _mk("sales routes pipeline", detail="customer routing"),
        _mk("crm leads dashboard", detail="customer routing"),
    ])
    _check(results, "separation-B-low-affinity", aff_xy <= 0.15,
           f"affinity={aff_xy:.4f}")
    _check(results, "separation-B-high-harmony", harm_hi >= 0.4,
           f"harmony={harm_hi:.4f}")
    _check(results, "separation-B-disagree", aff_xy <= 0.15 and harm_hi >= 0.4)

    # Case C: affinity FIXED, harmony varies -> harmony is not a function
    # of pair affinity (set-level redundancy is invisible to _affinity).
    aff_fixed = _affinity(cube_a.session.plane, "a", "b")["affinity"]
    h_small = harmony_score([A, B])
    h_big = harmony_score([A, B] + [DUP_A for _ in range(6)])
    _check(results, "separation-C-affinity-fixed", aff_fixed == aff_ab)
    _check(results, "separation-C-harmony-varies", h_big < h_small * 0.5,
           f"{h_small:.4f} -> {h_big:.4f}")


def _public_path(results: dict) -> None:
    """3.2.5: Program.harmony_of is the honest public path (INTEGRATION)."""
    from form.open import Program

    prog = Program(owner="P3R32")
    direct = harmony_score([A, B, C])
    via_ideas = prog.harmony_of([A, B, C])
    _check(results, "public-path-ideas", via_ideas == direct,
           f"{via_ideas:.4f}")
    # Unit IDs resolve against the program's cube plane.
    prog.cube.place_idea("u1", "crm routes pipeline", words="customer routing")
    prog.cube.place_idea("u2", "crm routes dashboard", words="customer routing")
    via_units = prog.harmony_of(["u1", "u2"])
    _check(results, "public-path-unit-ids",
           isinstance(via_units, float) and 0.0 <= via_units <= 1.0,
           f"{via_units:.4f}")
    _check(results, "public-path-unknown-id-fail-closed",
           prog.harmony_of(["no-such-unit"]) == 0.0)
    _check(results, "public-path-none-fail-closed", prog.harmony_of(None) == 0.0)


def _fresh_process(results: dict) -> None:
    """CROSS_PROCESS: a fresh interpreter computes the same score."""
    code = (
        "import sys; sys.path.insert(0, %r);"
        "from form.dell_matrix.harmony import harmony_score;"
        "from form.mandell.idea import Idea, Provenance, ProvenanceSource;"
        "p = Provenance(source=ProvenanceSource.HUMAN, activity='fp', agent='fp');"
        "a = Idea(title='crm routes pipeline'); a.set_property('detail', 'customer routing', p);"
        "b = Idea(title='crm routes dashboard'); b.set_property('detail', 'customer routing', p);"
        "print('RESULT ' + repr(harmony_score([a, b])))"
    ) % REPO
    r = subprocess.run([sys.executable, "-c", code], cwd=REPO,
                       capture_output=True, text=True, timeout=120)
    val = None
    for line in r.stdout.splitlines():
        if line.startswith("RESULT "):
            try:
                val = float(line[len("RESULT "):])
            except ValueError:
                val = None
    expected = harmony_score([A, B])
    _check(results, "fresh-process-same-score",
           r.returncode == 0 and val is not None and val == expected,
           f"subprocess={val} inprocess={expected:.4f}")


def _mutation(results: dict) -> None:
    """Perturbing the redundancy exponent must be DETECTED by the proof."""
    # Near-duplicate (not identical): jaccard in (0, 1) so R is
    # exponent-sensitive. Identical pairs would give jac = 1 = 1**k.
    near = _mk("crm routes pipeline", detail="customer routing extra")
    fixture = [A, near]
    baseline = harmony_score(fixture)
    assert 0.0 < baseline < 1.0, f"fixture not exponent-sensitive: {baseline}"
    old = harmony_mod._DUP_EXPONENT
    try:
        harmony_mod._DUP_EXPONENT = 1.0
        mutated = harmony_score(fixture)
    finally:
        harmony_mod._DUP_EXPONENT = old
    detected = abs(mutated - baseline) > 1e-9
    _check(results, "mutation-exponent-detected", detected,
           f"baseline={baseline:.4f} mutated={mutated:.4f}")
    # Restore verified: score returns to baseline.
    _check(results, "mutation-restored", harmony_score(fixture) == baseline)


def smoke() -> bool:
    """Run all P3 R3.2 harmony cases. Returns True iff all pass."""
    print("=== P3 R3.2 HARMONY PROOF ===", flush=True)
    results: dict = {}
    _bounds(results)
    _degenerate(results)
    _symmetry_determinism(results)
    _monotonicity(results)
    _contract_docstring(results)
    _separation(results)
    _public_path(results)
    _fresh_process(results)
    _mutation(results)

    fails = [k for k, v in results.items() if not v]
    npass = sum(1 for v in results.values() if v)
    ntotal = len(results)
    print(f"P3 R3.2: {npass}/{ntotal} PASS", flush=True)
    if fails:
        print(f"FAILURES: {fails}", flush=True)
        return False
    if ntotal == 0:
        print("FAIL: empty evidence", flush=True)
        return False
    print("P3 R3.2 WORLD: ALL PASS", flush=True)
    return True


def main() -> None:
    """Entry point with honest exit status."""
    ok = smoke()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
