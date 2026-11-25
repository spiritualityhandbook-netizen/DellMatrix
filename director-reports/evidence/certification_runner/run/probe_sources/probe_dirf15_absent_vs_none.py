import glob, os, shutil, sys
sys.path.insert(0, os.getcwd())

fails = []

def case(name, cond, detail=""):
    print(("[PASS] " if cond else "[FAIL] ") + name
          + (" -- " + detail if detail else ""))
    if not cond:
        fails.append(name)

def cleanup(owner):
    base = os.path.join(os.getcwd(), "form", "state")
    for pat in ("program_%s.json", "nursery_%s.json",
                "checkpoint_%s.json", "confirm_journal_%s.json",
                "confirm_gen_%s.json", "confirm_current_%s.json"):
        for f in glob.glob(os.path.join(base, pat % owner)):
            os.remove(f)
    d = os.path.join(base, "ideas_%s" % owner)
    if os.path.isdir(d):
        shutil.rmtree(d)

def program(owner):
    cleanup(owner)
    from form.open import Program
    from form.mandell.core_ii_exec import attach
    p = Program(owner=owner)
    attach(p)
    return p

def run(p, seed):
    from form.mandell.executor import execute_seed
    return execute_seed(p, seed)

# Removal: stored None deleted -> membership change (Director's
# reproducer). None is seeded DIRECTLY into state: the store is
# Dict[str, Any] by design and no public string writer emits
# None. This is a state-seeding claim, not a public-writer claim.
owner = "CertRunnerF15Rem"
try:
    p = program(owner)
    st = p.core_ii
    st.store["nullable"] = None
    run(p, "86[Delete] :: nullable")
    r = run(p, "89[Diff]")
    case("stored-None removal is a membership change",
         r.get("ok") is True
         and st.last_diff.get("changed") == ["nullable"]
         and st.last_diff.get("before") == {"nullable": None}
         and st.last_diff.get("after") == {},
         "last_diff=%r" % (st.last_diff,))
finally:
    cleanup(owner)

# Guard: a None retained unchanged on both sides is NOT a change.
owner = "CertRunnerF15Retain"
try:
    p = program(owner)
    st = p.core_ii
    st.store["nullable"] = None
    run(p, "55[Set] :: a=1")
    r = run(p, "89[Diff]")
    case("retained None is absent from changed",
         r.get("ok") is True
         and st.last_diff.get("changed") == ["a"],
         "last_diff=%r" % (st.last_diff,))
finally:
    cleanup(owner)

print("=== probe_dirf15_absent_vs_none: %d/2 ===" % (2 - len(fails)))
sys.exit(1 if fails else 0)
