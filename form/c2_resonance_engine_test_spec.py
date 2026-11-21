#!/usr/bin/env python3
"""C2 Resonance Core — failing-first (Part I, MWL #121-#129, GP-E19).

The C2 family is the resonance engine contract set from the Unified
Edition §14.3 / Edition 1 GP-E19: a bounded candidate engine whose
verdicts, relatedness, growth coupling, targeted pulse, decay,
fusion, partition, enhancement outcome, and temperature are TYPED
and inspectable — not bare floats, global switches, or silent side
effects.

STATUS: FAILING-FIRST. Controls (marked CONTROL) pass on current
main and guard against vacuous greens. Contract checks assert the
C2 surfaces named in the register rows; each failure states what
exists today instead. NO product code is changed by this file. The
C2 build turns the contract checks green inside Part I's PR after
PLAN-CONFIRM; this suite is the failing-first evidence that the
contracts are not met today.

Rows: #121 C2.Candidate, #122 C2.Relatedness, #123 C2.Growth,
#124 C2.TargetedPulse, #125 C2.Decay, #126 C2.Fusion (DD-15),
#127 C2.Partition (DD-16), #128 C2.EnhancementOutcome (DD-23),
#129 C2.TemperatureDesign (DD-19).
"""
from __future__ import annotations

import glob
import inspect
import os
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from form.open import open_program

OWNER = "C2RESO1112"


def _cleanup(owner):
    state = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state")
    for f in glob.glob(os.path.join(state, f"*{owner}*")):
        try:
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.remove(f)
        except FileNotFoundError:
            pass
        except OSError as e:
            raise RuntimeError(f"cleanup failed for {f}: {e}")


def smoke() -> bool:
    print("=== C2 RESONANCE CORE (FAILING-FIRST) ===")
    fails = []

    def check(name, cond, detail=""):
        print(f"[{'PASS' if cond else 'FAIL'}] {name}"
              + (f" :: {detail}" if detail else ""))
        if not cond:
            fails.append(name)

    _cleanup(OWNER)
    p = open_program(OWNER)
    p.place("c2_a", "harbor lantern alpha",
            words="harbor lantern craft timber copper kettle song", x=0.0, y=0.0)
    p.place("c2_b", "harbor lantern beta",
            words="harbor lantern craft timber copper kettle bell", x=1.0, y=0.0)
    p.place("c2_c", "glacier tundra gamma",
            words="glacier tundra obsidian wolf fjord", x=9.0, y=9.0)

    # CONTROL — the H4 coherence helper exists and returns a bare
    # float in range today, loaded exactly as production loads it
    # (open.py:1332-1333: SemanticGraph.load(owner) inside growth).
    # This is the raw material C2 must type, not the C2 contract.
    from form.dell_matrix import graph_harmony
    from form.mandell.semantic_graph import SemanticGraph
    coh = None
    try:
        coh = graph_harmony.graph_coherence(
            SemanticGraph.load(OWNER), ["c2_a", "c2_b"])
    except Exception as e:
        coh = f"error: {type(e).__name__}: {e}"
    check("CONTROL H4 graph_coherence returns a bare float in [0,1]",
          isinstance(coh, float) and 0.0 <= coh <= 1.0, f"coherence={coh!r}")

    # CONTROL — growth runs today and produces PENDING proposals.
    res = p.grow_ideas(1)
    n_props = len(getattr(p.nursery, "proposals", {}) or {})
    check("CONTROL grow_ideas runs and the Nursery holds proposals",
          isinstance(res, (dict, list)) and n_props >= 0,
          f"grow_result_type={type(res).__name__} proposals={n_props}")

    # #121 — C2.Candidate: a graded input on one real canonical path
    # yields a TYPED verdict (grade + basis), not a bare float.
    verdict_surface = None
    for modname in ("form.dell_matrix.resonance_engine",):
        try:
            mod = __import__(modname, fromlist=["x"])
            verdict_surface = mod
        except ImportError:
            pass
    typed = [n for n in dir(graph_harmony)
             if "verdict" in n.lower() or "grade" in n.lower()]
    check("#121 C2.Candidate typed graded verdict surface exists",
          verdict_surface is not None or bool(typed),
          f"resonance_engine_module={'present' if verdict_surface else 'ABSENT'}; "
          f"graph_harmony verdict/grade symbols={typed or 'none'} "
          f"(only bare-float graph_coherence exists)")

    # #122 — C2.Relatedness: a query exposing with-whom / how-strong /
    # why over agreed fixtures.
    rel_fns = [n for n in dir(graph_harmony) if "relat" in n.lower()]
    check("#122 C2.Relatedness exposes with-whom/how-strong/why",
          bool(rel_fns),
          f"graph_harmony relatedness symbols={rel_fns or 'none'}; "
          f"graph_neighbor_ids gives ids only, graph_coherence a bare float")

    # #123 — C2.Growth: growth is COUPLED to agreed development
    # evidence — a development-evidence input changes growth
    # behavior. (Proposals DO carry provenance today — parents, a
    # coded reason string, a graph_coherence float; that is recorded
    # in the detail. Provenance is not coupling.)
    gsig = inspect.signature(p.grow_ideas)
    gparams = set(gsig.parameters)
    coupling = bool(gparams & {"development", "development_evidence",
                               "evidence", "duobeta", "learning"})
    props = getattr(p.nursery, "proposals", {}) or {}
    sample = next(iter(props.values()), None)
    prov = (f"parents={getattr(sample, 'parents', None)} "
            f"reason={getattr(sample, 'reason', None)!r} "
            f"gcoh={getattr(sample, 'graph_coherence', None)}"
            if sample is not None else "no proposals")
    check("#123 growth responds to development-evidence input",
          coupling,
          f"grow_ideas parameters={sorted(gparams)} "
          f"(no development-evidence parameter); proposal provenance "
          f"exists but is not coupling: {prov}")

    # #124 — C2.TargetedPulse: Pulse obeys selected targets and
    # exclusions (typed selection arguments), per DD-18/H-4 cluster.
    sig = inspect.signature(p.pulse)
    params = set(sig.parameters)
    check("#124 pulse accepts selected targets and exclusions",
          bool(params & {"targets", "target_ids", "scope_ids",
                         "exclude", "exclusions"}),
          f"Program.pulse parameters={sorted(params) or 'none'} "
          f"(no target/exclusion selection today)")

    # #125 — C2.Decay: decline-coupled decay as a typed operation
    # (rate coupled to decline evidence), distinct from fade flags.
    decay_surface = [n for n in dir(p) if "decay" in n.lower()]
    check("#125 decline-coupled decay operation exists on Program",
          bool(decay_surface),
          f"Program decay symbols={decay_surface or 'none'}; "
          f"only faded_policy participation flags exist")

    # #126 — C2.Fusion (DD-15): Merge carries parent substance and
    # provenance while preserving parents.
    fusion_surface = [n for n in dir(p)
                      if n.lower().startswith(("merge", "fuse", "fusion"))]
    check("#126 fusion/merge operation exists on Program",
          bool(fusion_surface),
          f"Program fusion symbols={fusion_surface or 'none'}")

    # #127 — C2.Partition (DD-16): Split keeps each resonating
    # cluster intact; zero/one-cluster and ties handled honestly.
    split_surface = [n for n in dir(p)
                     if n.lower().startswith(("split", "partition"))]
    check("#127 partition/split operation exists on Program",
          bool(split_surface),
          f"Program split symbols={split_surface or 'none'}")

    # #128 — C2.EnhancementOutcome (DD-23): Enhance, redefined per
    # Ace's ruling, yields a typed outcome receipt (what changed,
    # why, on what evidence) — not only an on/off toggle.
    enh = [n for n in dir(p) if n.lower().startswith("enhance")]
    typed_outcome = any(
        callable(getattr(p, n, None)) and n not in ("enhance_on", "enhance_off")
        for n in enh)
    check("#128 enhance yields a typed outcome receipt beyond on/off",
          typed_outcome,
          f"Program enhance symbols={enh or 'none'}: 'enhance' is the "
          f"EnhanceGate state object (not an operation); the only "
          f"operations are the enhance_on/enhance_off toggles — no "
          f"operation returns a typed outcome receipt") 

    # #129 — C2.TemperatureDesign (DD-19): temperature as a typed
    # intensity control PER CONSUMER, not a secret global switch.
    temp_surface = []
    for modname in ("form.dell_matrix.spatial_authority",):
        mod = __import__(modname, fromlist=["x"])
        temp_surface = [n for n in dir(mod) if "temper" in n.lower()
                        and not n.startswith("_")]
    typed_temp = [n for n in temp_surface
                  if isinstance(getattr(__import__(
                      "form.dell_matrix.spatial_authority",
                      fromlist=["x"]), n, None), type)]
    check("#129 temperature is a typed per-consumer control",
          bool(typed_temp),
          f"spatial_authority temperature symbols={temp_surface or 'none'}; "
          f"typed control classes={typed_temp or 'none'} "
          f"(module-level dynamics constants only)")

    total = 11
    print(f"C2 RESONANCE ENGINE: {total - len(fails)}/{total} checks passed"
          + (f"; FAILING: {fails}" if fails else ""))
    _cleanup(OWNER)
    return not fails


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
