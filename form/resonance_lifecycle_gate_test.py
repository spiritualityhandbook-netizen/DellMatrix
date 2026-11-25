#!/usr/bin/env python3
"""72-40 — Lifecycle participation across resonance consumers.

Register: "Enforce active/faded/superseded participation
across all consumers (P1/E) (= SM-29)." Already proven: the
canonical_lifecycle boundary exists, fail-closed on
UNKNOWN/malformed, named consumers covered. Remaining
action: "Consumer census proving EVERY resonance consumer
routes through the boundary."

Census (main b997cc9, 2026-11-07; grounding:
hidden_files/72-40_ground.md):

- form/dell_matrix/resonance.py pulse(): routes through
  canonical_lifecycle.is_active ONLY when program= is passed;
  program=None means no exclusion (documented limitation).
- Production path Program.pulse() (form/open.py) calls
  EnhanceGate.pulse(plane) (form/dell_matrix/
  enhance_gate.py), which calls resonance.pulse(plane,
  state) WITHOUT program= — so the boundary is never
  consulted on the real user path (REPL p.pulse(),
  executor_leaf Pulse Dell, visual_evolve_loop, self_model
  all call program.pulse()).
- harmonize_pair() has no program parameter at all; the
  gate's harmonize() likewise. No live production caller
  today (idea_grow retired in SD-5) — latent surface.
- Consumers that DO route through the boundary when given
  the program: knowledge_selector, knowledge_influence,
  runtime_observe, open.py growth eligibility,
  ringed_growth._affinity (program=None callers skip).

Contract under test (the production path must honor the
same exclusion the module path proves):

- K1 premise: the boundary itself resolves active=True,
  faded=False, superseded=False, pending=False for the
  fixture proposals.
- K2 control: module pulse(program=prog) excludes the
  faded unit (the proven contract the prod path must match).
- K3 control: Program.pulse() scores genuinely active
  units (no over-exclusion after any repair).
- K4 control: enhance OFF still blocks Program.pulse().
- D1 Program.pulse() gives a FADED unit no score/tag entry.
- D2 Program.pulse() gives an active peer exactly the
  score the contract reference (module pulse with
  program=) gives it — the faded unit contributes nothing.
- D3 Program.pulse() excludes a SUPERSEDED unit.
- D4 a unit that fades AFTER an active Program.pulse()
  loses its retained scores on the next Program.pulse().
- D5 Program.pulse() excludes a PENDING (unconfirmed)
  proposal unit.
- D6 D1 in a fresh OS process (CROSS_PROCESS).

Run: python3 -m form.resonance_lifecycle_gate_test
"""

import glob
import json
import os
import subprocess
import sys
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from form.dell_matrix import canonical_lifecycle as cl
from form.dell_matrix.nursery import Proposal
from form.dell_matrix.plane import Skin
from form.dell_matrix.resonance import ResonanceState, pulse as raw_pulse
from form.open import open_program
from form.persist import _STATE_DIR, _safe_owner

RESULTS = []
_CLEANUP_ERRORS = []
RUN = uuid.uuid4().hex[:8]


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))
    print(f"{'PASS' if ok else 'FAIL'} {name} {detail}")


def cleanup(owner):
    safe = _safe_owner(owner)
    for f in glob.glob(os.path.join(_STATE_DIR, f"*{safe}*")):
        try:
            os.unlink(f)
        except OSError as e:
            _CLEANUP_ERRORS.append(f"{f}: {e}")


def build(owner, faded_state="faded"):
    """Real Program with a/b active and f in the given state."""
    prog = open_program(owner)
    cube = prog.cube
    cube.place_idea("a", "river flow", skin=Skin.SEED, x=0.0)
    cube.place_idea("b", "river bank", skin=Skin.SEED, x=1.0)
    cube.place_idea("f", "river faded silt", skin=Skin.SEED, x=2.0)
    prog.nursery.proposals["a"] = Proposal(
        id="a", label="a", words="river flow", kind="new",
        lifecycle_state="active", status="confirmed")
    prog.nursery.proposals["b"] = Proposal(
        id="b", label="b", words="river bank", kind="new",
        lifecycle_state="active", status="confirmed")
    if faded_state == "pending":
        prog.nursery.proposals["f"] = Proposal(
            id="f", label="f", words="river faded silt", kind="new",
            lifecycle_state="active", status="pending")
    else:
        prog.nursery.proposals["f"] = Proposal(
            id="f", label="f", words="river faded silt", kind="new",
            lifecycle_state=faded_state)
    return prog


def main():
    owner = f"C40-{RUN}"
    cleanup(owner)
    try:
        prog = build(owner)

        # K1 premise: boundary resolution for the fixtures
        check("K1.boundary_premise",
              cl.is_active(prog, "a") and cl.is_active(prog, "b")
              and not cl.is_active(prog, "f"),
              f"a={cl.is_active(prog, 'a')} f={cl.is_active(prog, 'f')}")

        # K2 control: module path with program= excludes faded
        st = raw_pulse(prog.cube.session.plane, ResonanceState(), program=prog)
        check("K2.module_pulse_excludes_faded",
              "f" not in st.scores and "f" not in st.tags
              and st.scores.get("a", 0.0) > 0,
              f"a={st.scores.get('a')} f={st.scores.get('f')}")
        ref_a = st.scores.get("a", 0.0)

        # K4 control: enhance OFF blocks the production pulse
        off = prog.pulse()
        check("K4.enhance_off_blocks", off.get("ok") is False,
              f"ok={off.get('ok')}")

        # Production path
        prog.enhance_on()
        out = prog.pulse()
        scores = out.get("scores", {})
        tags = prog.enhance.state.tags
        check("K3.prod_pulse_scores_active",
              out.get("ok") is True and scores.get("a", 0.0) > 0
              and scores.get("b", 0.0) > 0,
              f"a={scores.get('a')} b={scores.get('b')}")
        check("D1.prod_pulse_faded_no_entry",
              "f" not in scores and "f" not in tags,
              f"f_score={scores.get('f')}")
        check("D2.prod_pulse_faded_contributes_nothing",
              scores.get("a", 0.0) == ref_a,
              f"prod_a={scores.get('a')} ref_a={ref_a}")

        # D4 retained scores dropped after fading (same program)
        prog.nursery.proposals["b"].lifecycle_state = "faded"
        out2 = prog.pulse()
        check("D4.prod_pulse_retained_dropped",
              "b" not in out2.get("scores", {}),
              f"b_score={out2.get('scores', {}).get('b')}")
    finally:
        cleanup(owner)

    # D3 superseded, D5 pending: fresh programs
    for tag, state, name in (("S", "superseded", "D3.prod_pulse_superseded_excluded"),
                             ("P", "pending", "D5.prod_pulse_pending_excluded")):
        o2 = f"C40{tag}-{RUN}"
        cleanup(o2)
        try:
            p2 = build(o2, faded_state=state)
            premise = not cl.is_active(p2, "f")
            p2.enhance_on()
            o = p2.pulse()
            check(name, premise and "f" not in o.get("scores", {}),
                  f"premise={premise} f_score={o.get('scores', {}).get('f')}")
        finally:
            cleanup(o2)

    # D6 cross-process: production pulse in a fresh process
    child = (
        "import json, sys\n"
        "sys.path.insert(0, sys.argv[1])\n"
        "from form.resonance_lifecycle_gate_test import build\n"
        "p = build(sys.argv[2])\n"
        "p.enhance_on()\n"
        "o = p.pulse()\n"
        "print(json.dumps({'f_in': 'f' in o.get('scores', {}),"
        " 'a': o.get('scores', {}).get('a')}))\n"
    )
    o3 = f"C40X-{RUN}"
    cleanup(o3)
    try:
        r = subprocess.run(
            [sys.executable, "-c", child, os.getcwd(), o3],
            capture_output=True, text=True, timeout=300)
        got = json.loads(r.stdout.strip().splitlines()[-1]) if r.stdout.strip() else {}
        check("D6.prod_pulse_faded_excluded_cross_process",
              got.get("f_in") is False and (got.get("a") or 0) > 0,
              f"child={got} rc={r.returncode}")
    except Exception as e:
        check("D6.prod_pulse_faded_excluded_cross_process", False,
              f"{type(e).__name__}: {e}")
    finally:
        cleanup(o3)

    check("Z.cleanup", not _CLEANUP_ERRORS, "; ".join(_CLEANUP_ERRORS))
    failed = [n for n, ok, _ in RESULTS if not ok]
    print(f"resonance_lifecycle_gate: "
          f"{len(RESULTS) - len(failed)}/{len(RESULTS)} PASS")
    if failed:
        print("FAILURES:", ", ".join(failed))
    return 1 if failed else 0


def smoke():
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
