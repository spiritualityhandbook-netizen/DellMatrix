"""P3 R3.2 harmony proof: harmony_score contract, separation, public path.

GDP-001 Phase 3, R3.2 (3.2.1-3.2.5). NON-VACUOUS (P3R rewrite, 2026-10-04):
  - Content-bearing canonical fixtures: real Idea objects with overlapping
    token content (river/stream/meadow), not empty mocks.
  - Independently expected results: hand-computed harmony for a 2-idea
    case (0.4375, asserted BITWISE) and a 3-idea case (0.2859, asserted
    with tolerance) IN COMMENTS.
  - Bypass-must-fail (the Director's explicit test): exclude_faded
    monkeypatched out of harmony_score -> a faded duplicate MUST leak
    back in and change the score (1.0 -> 0.0). If the score is unchanged,
    the filter is decorative and the proof FAILS.
  - Honest permutation guarantee: bitwise for n <= 2, float-tolerance
    for n >= 3 (the old "permuting never changes the result" is refined —
    pair sums accumulate in input order).

Portable: derives REPO from __file__.
Enforced: smoke() -> bool, sys.exit(0/1), registered in form.regress.

Test realism labels (honest): pure-function checks are UNIT; the
public-path check is INTEGRATION (direct Program method call); the
subprocess check is CROSS_PROCESS. No REPL/UI claims are made.
"""

from __future__ import annotations

import itertools
import os
import subprocess
import sys

# Portable: derive repo root from this file's location.
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, REPO)

from form.dell_matrix.harmony import harmony_score  # noqa: E402
from form.dell_matrix import harmony as harmony_mod  # noqa: E402
from form.mandell.idea import Idea, LifecycleState, Provenance, ProvenanceSource  # noqa: E402

_PROV = Provenance(source=ProvenanceSource.HUMAN, activity="p3r32", agent="p3r32")


def _mk(title: str, **props) -> Idea:
    idea = Idea(title=title)
    for k, v in props.items():
        idea.set_property(k, v, _PROV)
    return idea


def _faded(idea: Idea) -> Idea:
    idea._idea_state = LifecycleState.FADED
    return idea


# Content-bearing fixtures (titles only; no properties, so token sets are
# exactly the title words).
RIVER = _mk("river water flow")
STREAM = _mk("stream water flow")
MEADOW = _mk("meadow grass field")
NOISE = _mk("telemetry unrelated zebra")

_results: dict = {}


def rec(name: str, ok: bool, detail: str = "") -> None:
    _results[name] = bool(ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}"
          + (f" | {detail}" if detail else ""), flush=True)


def t_hand_computed() -> None:
    """3.2.3: harmony values derived BY HAND, then asserted.

    (H2) Two ideas, titles "alpha beta gamma" / "alpha beta delta":
      T1 = {alpha, beta, gamma}, T2 = {alpha, beta, delta}
      jac = 2/4 = 0.5; one pair -> C = 0.5, R = 0.5^3 = 0.125
      harmony = 0.5 * (1 - 0.125) = 0.5 * 0.875 = 0.4375
      (exact in binary: 0.4375 = 7/16, so bitwise equality is required)

    (H3) Three ideas, titles "a b c" / "a b d" / "a e f":
      jac12 = 2/4 = 0.5, jac13 = 1/5 = 0.2, jac23 = 1/5 = 0.2
      C = (0.5 + 0.2 + 0.2)/3 = 0.3
      R = (0.125 + 0.008 + 0.008)/3 = 0.141/3 = 0.047
      harmony = 0.3 * (1 - 0.047) = 0.3 * 0.953 = 0.2859
      (n = 3: pair sums accumulate in input order -> tolerance, NOT
      bitwise, per the honest permutation guarantee)
    """
    h2 = harmony_score([_mk("alpha beta gamma"), _mk("alpha beta delta")])
    rec("hand::two_idea", h2 == 0.4375, f"got {h2!r} (bitwise required)")
    h3 = harmony_score([_mk("a b c"), _mk("a b d"), _mk("a e f")])
    rec("hand::three_idea", abs(h3 - 0.2859) < 1e-9, f"got {h3!r}")
    # Identical set: every jac = 1 -> C = R = 1 -> 0. Disjoint: C = 0 -> 0.
    dup = _mk("river water flow")
    rec("hand::identical_zero",
        harmony_score([dup, _mk("river water flow"), _mk("river water flow")]) == 0.0)
    rec("hand::disjoint_zero",
        harmony_score([_mk("alpha beta"), _mk("gamma delta")]) == 0.0)
    # Solo: 1.0 with content, 0.0 without.
    rec("hand::solo", harmony_score([RIVER]) == 1.0
        and harmony_score([_mk("")]) == 0.0)


def t_degenerate() -> None:
    """3.2.3 failure behavior: degenerate inputs -> defined outputs."""
    rec("degen::empty", harmony_score([]) == 0.0)
    rec("degen::none", harmony_score(None) == 0.0)
    rec("degen::bare_string", harmony_score("abc") == 0.0)
    rec("degen::noniterable", harmony_score(42) == 0.0)
    try:
        v = harmony_score([None, "junk", 42, RIVER])
        rec("degen::malformed_no_crash",
            isinstance(v, float) and 0.0 <= v <= 1.0, f"score={v:.4f}")
    except Exception as e:  # noqa: BLE001
        rec("degen::malformed_no_crash", False, f"raised {e!r}")
    # Bounds battery.
    cases = [[], [_mk("")], [_mk("alpha")], [RIVER, STREAM],
             [RIVER, STREAM, MEADOW], [RIVER, STREAM, MEADOW, NOISE],
             [None, 42, object()]]
    ok = all(isinstance(harmony_score(c), float)
             and 0.0 <= harmony_score(c) <= 1.0 for c in cases)
    rec("degen::bounds_battery", ok, f"{len(cases)} cases")


def t_permutation_honest() -> None:
    """3.2.3 permutation guarantee, stated honestly.

    n <= 2: BITWISE identical (single deterministic computation).
    n >= 3: equal within float tolerance (pair sums accumulate in input
    order; last-ulp differences are possible and do NOT violate the
    contract). The old blanket "permuting never changes the result" is
    refined, not contradicted.
    """
    pair = [RIVER, STREAM]
    base2 = harmony_score(pair)
    rec("perm::pair_bitwise",
        all(harmony_score(list(p)) == base2
            for p in itertools.permutations(pair)))
    trio = [RIVER, STREAM, MEADOW]
    base3 = harmony_score(trio)
    diffs = [abs(harmony_score(list(p)) - base3)
             for p in itertools.permutations(trio)]
    rec("perm::trio_tolerance", max(diffs) < 1e-9, f"max_diff={max(diffs)!r}")
    rec("perm::determinism_repeat",
        harmony_score(trio) == harmony_score(trio))


def t_bypass_faded_filter() -> None:
    """BYPASS-MUST-FAIL (the Director's explicit test).

    Removing harmony's faded filter must NOT leave the proof green.
    With the filter active, a faded exact duplicate is excluded, so
    [active, faded-dup] scores like the solo idea (1.0). With
    exclude_faded monkeypatched to the identity, the duplicate leaks
    back in: every pair is identical -> C = R = 1 -> score 0.0.
    If the bypassed score still equals the filtered score, the filter
    is decorative and the proof FAILS.
    """
    dup_faded = _faded(_mk("river water flow"))
    solo = harmony_score([RIVER])
    filtered = harmony_score([RIVER, dup_faded])
    rec("faded::excluded", filtered == solo == 1.0,
        f"filtered={filtered!r} solo={solo!r}")

    orig = harmony_mod.exclude_inactive_ideas
    harmony_mod.exclude_inactive_ideas = lambda ideas: list(ideas)  # BYPASS
    try:
        bypassed = harmony_score([RIVER, dup_faded])
    finally:
        harmony_mod.exclude_inactive_ideas = orig
    rec("faded::bypass_leaks", bypassed != filtered,
        f"filter disabled -> score={bypassed!r} (was {filtered!r})")
    rec("faded::bypass_value", bypassed == 0.0,
        "leaked duplicate is identical -> C=R=1 -> 0.0")
    rec("faded::restored", harmony_score([RIVER, dup_faded]) == filtered)

    # All-faded input: filtered -> 0.0 (defined); bypassed -> leaks > 0.
    all_faded = [_faded(_mk("river water flow")), _faded(_mk("stream water flow"))]
    rec("faded::all_faded_zero", harmony_score(all_faded) == 0.0)
    harmony_mod.exclude_inactive_ideas = lambda ideas: list(ideas)  # BYPASS
    try:
        leaked_all = harmony_score(all_faded)
    finally:
        harmony_mod.exclude_inactive_ideas = orig
    rec("faded::all_faded_bypass_leaks", leaked_all > 0.0,
        f"filter disabled -> score={leaked_all:.4f} (must be > 0)")


def t_monotonicity() -> None:
    """3.2.3: redundancy penalized, coherence rewarded."""
    h2 = harmony_score([RIVER, STREAM])
    h3dup = harmony_score([RIVER, STREAM, _mk("river water flow")])
    h3coh = harmony_score([RIVER, STREAM, _mk("river bank shore")])
    h3noise = harmony_score([RIVER, STREAM, NOISE])
    rec("mono::duplicate_decreases", h3dup < h2, f"{h2:.4f} -> {h3dup:.4f}")
    rec("mono::coherent_beats_noise", h3coh > h3noise,
        f"coherent={h3coh:.4f} noise={h3noise:.4f}")
    rec("mono::healthy_range", 0.3 < h2 < 0.7, f"{h2:.4f}")


def t_separation() -> None:
    """3.2.4: harmony_score and _affinity measure different things.

    Real functions, real objects. Counterexamples in both directions,
    plus an affinity-fixed / harmony-varies construction.
    """
    from form.dell_matrix.blank_cube import give
    from form.dell_matrix.ringed_growth import _affinity

    # A: HIGH pair affinity, LOW set harmony. Two co-located,
    # token-identical plane units -> affinity ~0.88+; four token-identical
    # ideas -> harmony exactly 0.0 (C = R = 1).
    cube_a = give("P3R32A", clean=True)
    cube_a.place_idea("a", "crm routes pipeline", words="crm routes pipeline",
                      x=0.0, y=0.0)
    cube_a.place_idea("b", "crm routes pipeline", words="crm routes pipeline",
                      x=0.0, y=0.0)
    aff_ab = _affinity(cube_a.session.plane, "a", "b")["affinity"]
    harm_dup = harmony_score([_mk("crm routes pipeline",
                                  detail="crm routes pipeline")
                              for _ in range(4)])
    rec("sep::A_high_affinity", aff_ab >= 0.7, f"affinity={aff_ab:.4f}")
    rec("sep::A_low_harmony", harm_dup <= 0.1, f"harmony={harm_dup:.4f}")

    # B: LOW pair affinity, HIGH set harmony. Disjoint tokens, far apart,
    # sandboxed out of mutual scope -> ~0.03; four coherent-but-distinct
    # ideas -> ~0.45.
    cube_b = give("P3R32B", clean=True)
    cube_b.place_idea("x", "alpha beta", words="alpha beta", x=0.0, y=0.0)
    cube_b.place_idea("y", "gamma delta", words="gamma delta", x=50.0, y=50.0)
    plane_b = cube_b.session.plane
    plane_b.box(["x"], "solo")
    aff_xy = _affinity(plane_b, "x", "y")["affinity"]
    harm_hi = harmony_score([
        _mk("crm routes pipeline", detail="customer routing"),
        _mk("crm routes dashboard", detail="customer routing"),
        _mk("sales routes pipeline", detail="customer routing"),
        _mk("crm leads dashboard", detail="customer routing"),
    ])
    rec("sep::B_low_affinity", aff_xy <= 0.15, f"affinity={aff_xy:.4f}")
    rec("sep::B_high_harmony", harm_hi >= 0.4, f"harmony={harm_hi:.4f}")

    # C: affinity FIXED, harmony varies -> harmony is not a function of
    # pair affinity (set-level redundancy is invisible to _affinity).
    h_small = harmony_score([RIVER, STREAM])
    h_big = harmony_score([RIVER, STREAM]
                          + [_mk("river water flow") for _ in range(6)])
    rec("sep::C_harmony_varies", h_big < h_small * 0.5,
        f"{h_small:.4f} -> {h_big:.4f}")


def t_public_path() -> None:
    """3.2.5: Program.harmony_of is the honest public path (INTEGRATION)."""
    from form.open import Program

    prog = Program(owner="P3R32")
    direct = harmony_score([RIVER, STREAM, MEADOW])
    via_ideas = prog.harmony_of([RIVER, STREAM, MEADOW])
    rec("pub::ideas", via_ideas == direct, f"{via_ideas:.4f}")
    prog.cube.place_idea("u1", "river water flow", words="current rapid")
    prog.cube.place_idea("u2", "stream water flow", words="current brook")
    via_units = prog.harmony_of(["u1", "u2"])
    # Tokens: u1 {river,water,flow,words,current,rapid},
    #         u2 {stream,water,flow,words,current,brook} -> jac = 4/8 = 0.5
    # -> 0.4375, the same hand-computed value as H2.
    rec("pub::unit_ids", via_units == 0.4375, f"{via_units!r}")
    rec("pub::unknown_id_fail_closed", prog.harmony_of(["no-such-unit"]) == 0.0)
    rec("pub::none_fail_closed", prog.harmony_of(None) == 0.0)
    # Canonical lifecycle: two faded units -> 0.0 via owner-aware boundary.
    # Uses nursery proposals (canonical records), NOT dynamic Unit attributes.
    prog.cube.place_idea("f1", "river water flow", words="current")
    prog.cube.place_idea("f2", "river water flow", words="current")
    # Create canonical faded records via nursery proposals
    from form.dell_matrix.nursery import Proposal
    prog.nursery.proposals["f1"] = Proposal(
        id="f1", label="river water flow", words="current",
        kind="new", lifecycle_state="faded")
    prog.nursery.proposals["f2"] = Proposal(
        id="f2", label="river water flow", words="current",
        kind="new", lifecycle_state="faded")
    rec("pub::faded_units_zero", prog.harmony_of(["f1", "f2"]) == 0.0)


def t_fresh_process() -> None:
    """CROSS_PROCESS: a fresh interpreter computes the same score."""
    code = (
        "import sys; sys.path.insert(0, %r);"
        "from form.dell_matrix.harmony import harmony_score;"
        "from form.mandell.idea import Idea;"
        "a = Idea(title='alpha beta gamma');"
        "b = Idea(title='alpha beta delta');"
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
    rec("xproc::same_score", r.returncode == 0 and val == 0.4375,
        f"subprocess={val!r} (hand-computed 0.4375)")


def t_mutation() -> None:
    """Perturbing the redundancy exponent must be DETECTED."""
    near = _mk("crm routes pipeline", detail="customer routing extra")
    fixture = [_mk("crm routes pipeline", detail="customer routing"), near]
    baseline = harmony_score(fixture)
    assert 0.0 < baseline < 1.0, f"fixture not exponent-sensitive: {baseline}"
    old = harmony_mod._DUP_EXPONENT
    try:
        harmony_mod._DUP_EXPONENT = 1.0
        mutated = harmony_score(fixture)
    finally:
        harmony_mod._DUP_EXPONENT = old
    rec("mutation::exponent_detected", abs(mutated - baseline) > 1e-9,
        f"baseline={baseline:.4f} mutated={mutated:.4f}")
    rec("mutation::restored", harmony_score(fixture) == baseline)


def t_contract_docstring() -> None:
    """The 8-field mathematical admission contract is present."""
    doc = harmony_score.__doc__ or ""
    fields = ["(1) NAME", "(2) INPUTS", "(3) OUTPUTS", "(4) FORMULA",
              "(5) INVARIANTS", "(6) FAILURE", "(7) DETERMINISM",
              "(8) CANONICAL OWNER"]
    missing = [f for f in fields if f not in doc]
    rec("contract::8_fields", not missing, f"missing={missing}")


def smoke() -> bool:
    """Run all P3 R3.2 harmony cases. Returns True iff all pass."""
    print("=== P3 R3.2 HARMONY PROOF (non-vacuous) ===", flush=True)
    _results.clear()
    t_hand_computed()
    t_degenerate()
    t_permutation_honest()
    t_bypass_faded_filter()
    t_monotonicity()
    t_separation()
    t_public_path()
    t_fresh_process()
    t_mutation()
    t_contract_docstring()
    fails = [k for k, v in _results.items() if not v]
    npass = sum(1 for v in _results.values() if v)
    ntotal = len(_results)
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
