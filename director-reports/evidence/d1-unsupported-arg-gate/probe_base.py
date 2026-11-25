"""Base-tree behavior pinning for D1-UNSUPPORTED-ARG-GATE suite
design. Runs on the UNCHANGED base; prints observed behavior for
the shapes whose post-fix assertions must be grounded, plus the
legacy shapes whose outcomes the gate must preserve."""
import glob
import os
import shutil
import sys

ROOT = os.path.expanduser("~/workspace/nbd-omega-arggate")
sys.path.insert(0, ROOT)
STATE = os.path.join(ROOT, "form", "state")


def cleanup(owner):
    for f in glob.glob(os.path.join(STATE, f"*{owner}*")):
        if os.path.isdir(f):
            shutil.rmtree(f)
        else:
            os.remove(f)


def fresh(owner):
    cleanup(owner)
    from form.open import Program
    return Program(owner)


def st(p):
    from form.mandell.core_ii_exec import attach
    return attach(p)


def main():
    from form.mandell.executor import execute_seed

    owner = "GateProbeA"
    p = fresh(owner)
    s = st(p)
    print("baseline units:", sorted(p.cube.session.plane.units))
    p.place("garden_gate", "Garden Gate")
    p.place("garden_fern", "Garden Fern")
    p.place("river_stone", "River Stone")
    execute_seed(p, "51[Select]")

    r = execute_seed(p, '82[Group] :: predicate="garden"')
    print("argshaped-label Group ok:", r.get("ok"),
          "groups:", sorted((s.groups or {}).keys()))

    r = execute_seed(p, "82[Group] :: playlist (draft) mix")
    print("parens-label Group ok:", r.get("ok"),
          "groups:", sorted((s.groups or {}).keys()))

    r = execute_seed(p, "78[Cause] :: rain>flood")
    print("legacy Cause ok:", r.get("ok"), "err:", r.get("error"),
          "causes:", getattr(s, "causes", "NOATTR"))

    r = execute_seed(p, "97[Define] :: tempo=120")
    print("legacy Define ok:", r.get("ok"), "defs:", dict(s.defs or {}))
    cleanup(owner)

    # J3 shape: frame whose body atom is refused (registered law),
    # clean Join — behavior to preserve on both trees.
    owner = "GateProbeB"
    p = fresh(owner)
    s = st(p)
    p.place("garden_gate", "Garden Gate")
    r = execute_seed(p, '63[Sequence] > 55[Set](bogus="x") > 61[Join]')
    print("J3 ok:", r.get("ok"), "err:", r.get("error"))
    print("J3 atom_results:", r.get("atom_results"))
    print("J3 last_frame status/err:",
          (s.last_frame or {}).get("status"),
          (s.last_frame or {}).get("error"))
    cleanup(owner)

    # While witness on base: body must actually run (RED witness).
    owner = "GateProbeC"
    p = fresh(owner)
    s = st(p)
    p.place("garden_gate", "Garden Gate")
    execute_seed(p, "51[Select]")
    r = execute_seed(p, "65[While] :: true > 55[Set] :: k=v > 61[Join]")
    print("While base ok:", r.get("ok"), "store:", dict(s.store or {}),
          "control_steps:", s.control_steps,
          "frame iterations:", (s.last_frame or {}).get("iterations"),
          "frame status:", (s.last_frame or {}).get("status"))
    cleanup(owner)

    # ForEach shape on base.
    owner = "GateProbeD"
    p = fresh(owner)
    s = st(p)
    p.place("garden_gate", "Garden Gate")
    execute_seed(p, "51[Select]")
    r = execute_seed(p, "66[ForEach] > 55[Set] :: k=v > 61[Join]")
    print("ForEach base ok:", r.get("ok"), "store:", dict(s.store or {}),
          "frame iterations:", (s.last_frame or {}).get("iterations"))
    cleanup(owner)

    # Branch with Else on base (arm mechanics for skip receipts).
    owner = "GateProbeE"
    p = fresh(owner)
    s = st(p)
    p.place("garden_gate", "Garden Gate")
    r = execute_seed(p, "60[Branch] :: true > 55[Set] :: a=1 > "
                        "59[Route] > 55[Set] :: b=2 > 61[Join]")
    print("Branch base ok:", r.get("ok"), "store:", dict(s.store or {}))
    print("Branch base receipts:", r.get("atom_results"))
    cleanup(owner)
    print("PROBE_BASE_DONE")


if __name__ == "__main__":
    main()
