#!/usr/bin/env python3
"""Director order step 3c — DAF-02 semantic-preservation follow-up.

Step 3b (PR #168) repaired the Query disclosure, but the Director's
Mode D probes at 1ab1afe showed it sanitizes EXECUTABLE state in
place, both returning success with clean controls:

  (1) Sanitize -> Get, then a Set using last_result copies
      "password=[REDACTED]" instead of the original value;
  (2) Sanitize -> Set, then Revert restores a redacted value,
      corrupting the rollback.

Cause: last_result and rollback snapshots are executable state, not
display evidence. Contract for 3c: canonical last_result values,
control frames, and rollback checkpoints (shot() snapshots and Try
checkpoints) stay EXACTLY as a non-Sanitize control leaves them;
redaction applies only to DETACHED outward-facing evidence copies
(returned result / messages / traces / history / saved JSON), and
the step 3b marker-free disclosure checks on those surfaces stay
green.

Synthetic canary only, presence booleans only in records; isolated
synthetic program owners with loud cleanup.
"""
import glob
import json
import os
import shutil
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

RESULTS = []
MARKER = "SYNTHETIC_STEP3C_CANARY_7373"
ORIGINAL = f"password={MARKER}"
QUERY_SEED = f'41[Sanitize] > 54[Query](predicate="password={MARKER}")'
QUERY_CTRL = f'54[Query](predicate="password={MARKER}")'


def _rec(name, cond, detail=""):
    RESULTS.append((name, bool(cond), str(detail)[:220]))


def _cleanup(owner):
    state = os.path.join(_ROOT, "form", "state")
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


def _detached(p, r):
    """Outward-facing evidence surfaces only — live canonical
    state (last_result / frames / snapshots) is NOT here; it is
    checked separately for exact equality with the control."""
    st = getattr(p, "core_ii", None)
    return {
        "result": json.dumps(r, default=str),
        "messages": "\n".join(str(m) for m in r.get("messages", [])),
        "traces": "\n".join(str(t) for t in (st.traces if st else [])),
        "history": json.dumps(list(p.history), default=str),
        "outcome": json.dumps(p.outcome_records, default=str),
        "last_flow": json.dumps(getattr(p, "last_flow", {}), default=str),
    }


def main():
    from form.open import Program
    from form.mandell.execution_observer import observe_seed_execution

    # ---------- Query disclosure retained (3b checks, detached) --
    owner = "step3cmainZZ"
    _cleanup(owner)
    p = Program(owner=owner)
    r = observe_seed_execution(p, QUERY_SEED)
    _rec("counterexample chain returns ok=True", r.get("ok") is True,
         str(r.get("error")))
    for name, blob in _detached(p, r).items():
        _rec(f"marker absent from detached {name}", MARKER not in blob)
    path = p.save()
    with open(path, encoding="utf-8", errors="replace") as fh:
        _rec("marker absent from saved program JSON", MARKER not in fh.read())
    _cleanup(owner)

    # ---------- Canonical state equality vs control ----------
    o1, o2 = "step3ccanonAA", "step3ccanonBB"
    _cleanup(o1); _cleanup(o2)
    pa, pb = Program(owner=o1), Program(owner=o2)
    observe_seed_execution(pa, QUERY_SEED)
    observe_seed_execution(pb, QUERY_CTRL)
    sa, sb = getattr(pa, "core_ii", None), getattr(pb, "core_ii", None)
    _rec("live last_result EXACTLY equals control",
         sa.last_result == sb.last_result,
         f"{sa.last_result} vs {sb.last_result}")
    _rec("live last_result carries the real predicate",
         sa.last_result.get("predicate") == ORIGINAL)
    _rec("live frames/last_frame/last_control equal control",
         sa.frames == sb.frames and sa.last_frame == sb.last_frame
         and sa.last_control == sb.last_control)
    _rec("live snapshots equal control",
         sa.snapshots == sb.snapshots)
    _cleanup(o1); _cleanup(o2)

    # ---------- Director probe 1: Get -> Set using last_result --
    for tag, sanitize in (("sanitize", True), ("control", False)):
        o = f"step3cget{tag}AA"
        _cleanup(o)
        pp = Program(owner=o)
        observe_seed_execution(
            pp, f'55[Set](key="cred", value="{ORIGINAL}")')
        get_seed = ('41[Sanitize] > 56[Get](key="cred")' if sanitize
                    else '56[Get](key="cred")')
        observe_seed_execution(pp, get_seed)
        st = getattr(pp, "core_ii", None)
        if sanitize:
            _rec("probe1: live last_result value is the ORIGINAL",
                 st.last_result.get("value") == ORIGINAL,
                 str(st.last_result.get("value")))
        observe_seed_execution(
            pp, '55[Set](key="copy", value="last_result")')
        _rec(f"probe1 ({tag}): Set using last_result copies ORIGINAL",
             st.store.get("copy") == ORIGINAL,
             str(st.store.get("copy")))
        _cleanup(o)

    # ---------- Director probe 2: Set -> Revert ----------
    for tag, sanitize in (("sanitize", True), ("control", False)):
        o = f"step3crev{tag}AA"
        _cleanup(o)
        pp = Program(owner=o)
        observe_seed_execution(
            pp, f'55[Set](key="cred", value="{ORIGINAL}")')
        set_seed = (f'41[Sanitize] > 55[Set](key="cred", '
                    f'value="password=CHANGED_{tag}")' if sanitize
                    else f'55[Set](key="cred", value="password=CHANGED_{tag}")')
        observe_seed_execution(pp, set_seed)
        st = getattr(pp, "core_ii", None)
        _rec(f"probe2 ({tag}): Set applied its real value",
             st.store.get("cred") == f"password=CHANGED_{tag}",
             str(st.store.get("cred")))
        observe_seed_execution(pp, '96[Revert]')
        _rec(f"probe2 ({tag}): Revert restores ORIGINAL exactly",
             st.store.get("cred") == ORIGINAL,
             str(st.store.get("cred")))
        _cleanup(o)

    # ---------- Nested execution: Query inside Sequence ----------
    o3, o4 = "step3cnestAA", "step3cnestBB"
    _cleanup(o3); _cleanup(o4)
    pn, pc = Program(owner=o3), Program(owner=o4)
    rn = observe_seed_execution(
        pn, f'41[Sanitize] > 63[Sequence] > 54[Query](predicate="password={MARKER}") > 61[Join]')
    rc = observe_seed_execution(
        pc, f'63[Sequence] > 54[Query](predicate="password={MARKER}") > 61[Join]')
    sn, sc = getattr(pn, "core_ii", None), getattr(pc, "core_ii", None)
    _rec("nested: last_result EXACTLY equals control",
         sn.last_result == sc.last_result,
         f"{sn.last_result} vs {sc.last_result}")
    _rec("nested: frames EXACTLY equal control",
         sn.frames == sc.frames and sn.last_frame == sc.last_frame,
         f"{sn.frames} vs {sc.frames}")
    _rec("nested: detached surfaces marker-free",
         all(MARKER not in blob for blob in _detached(pn, rn).values()))
    _cleanup(o3); _cleanup(o4)

    # ---------- Try checkpoint: Sanitize > Try > Set > Revert ----
    o5 = "step3ctryAA"
    _cleanup(o5)
    pt = Program(owner=o5)
    observe_seed_execution(pt, f'55[Set](key="cred", value="{ORIGINAL}")')
    observe_seed_execution(
        pt, '41[Sanitize] > 93[Try] > 55[Set](key="cred", '
            'value="password=CHANGED_try") > 96[Revert]')
    stt = getattr(pt, "core_ii", None)
    _rec("try/revert: checkpoint restores ORIGINAL exactly",
         stt.store.get("cred") == ORIGINAL, str(stt.store.get("cred")))
    _cleanup(o5)

    leftovers = []
    base = os.path.join(_ROOT, "form", "state")
    if os.path.isdir(base):
        leftovers = [f for f in os.listdir(base) if "step3c" in f.lower()]
    _rec("cleanup leaves no residue", leftovers == [], str(leftovers))

    passed = sum(1 for _, ok_, _ in RESULTS if ok_)
    for name, ok_, detail in RESULTS:
        if not ok_:
            print(f"FAIL {name}: {detail}")
    print(f"STEP3C_SANITIZE_STATE: {passed}/{len(RESULTS)}")
    return passed == len(RESULTS) and len(RESULTS) > 0


def smoke():
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
