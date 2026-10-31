#!/usr/bin/env python3
"""Director order step 3b — DAF-02 chain follow-up (Director Mode D).

Step 3 repaired Sanitize standalone, but the Director's independently
executed counterexample at a60bb22 still leaked in a CHAIN:
41[Sanitize] > 54[Query](predicate="password=<canary>") returned
ok=True with the marker in the TOAM typed-args line, the Query scope
line, the returned result, and the saved program JSON history[1].

Contract: a chain containing Dell 41 carries its redaction
requirement through atom traces, returned evidence, and history
BEFORE persistence — the marker appears in NO surface (result dict,
messages, traces, last_result, frames, history, outcome records,
saved JSON, last_flow). Execution semantics are preserved: the
Query still runs with the real predicate (its count/value equal a
non-Sanitize control chain's), and non-Sanitize chains and ordinary
(non-secret) text are byte-unchanged — no over-redaction, and the
redaction flag does not stick to later executions.

Synthetic canary only, presence booleans only; isolated synthetic
program owners with loud cleanup.
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
MARKER = "SYNTHETIC_STEP3B_CANARY_4242"
SEED = f'41[Sanitize] > 54[Query](predicate="password={MARKER}")'


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


def _surfaces(p, r):
    st = getattr(p, "core_ii", None)
    return {
        "result": json.dumps(r, default=str),
        "messages": "\n".join(str(m) for m in r.get("messages", [])),
        "traces": "\n".join(str(t) for t in (st.traces if st else [])),
        "last_result": json.dumps(st.last_result if st else {}, default=str),
        "frames": json.dumps((st.frames if st else []) + [st.last_frame if st else {}], default=str),
        "history": json.dumps(list(p.history), default=str),
        "outcome": json.dumps(p.outcome_records, default=str),
        "last_flow": json.dumps(getattr(p, "last_flow", {}), default=str),
    }


def main():
    from form.open import Program
    from form.mandell.execution_observer import observe_seed_execution

    # ---------- Director counterexample ----------
    owner = "step3bmainZZ"
    _cleanup(owner)
    p = Program(owner=owner)
    r = observe_seed_execution(p, SEED)
    _rec("counterexample chain returns ok=True", r.get("ok") is True,
         str(r.get("error")))
    surf = _surfaces(p, r)
    for name, blob in surf.items():
        _rec(f"marker absent from {name}", MARKER not in blob)
    _rec("TOAM line survives in redacted form",
         any("TOAM: typed args lowered" in m and "[REDACTED]" in m
             for m in r.get("messages", [])))
    _rec("Query line survives in redacted form",
         any("Query scope=" in m and "[REDACTED]" in m
             for m in r.get("messages", [])))
    st = getattr(p, "core_ii", None)
    _rec("last_result predicate is the redacted form",
         st is not None and st.last_result.get("predicate") == "password=[REDACTED]",
         str(st.last_result if st else None))
    path = p.save()
    with open(path, encoding="utf-8", errors="replace") as fh:
        saved = fh.read()
    _rec("marker absent from saved program JSON", MARKER not in saved)
    _cleanup(owner)

    # ---------- Execution semantics preserved ----------
    o1, o2 = "step3bsemAA", "step3bsemBB"
    _cleanup(o1); _cleanup(o2)
    pa, pb = Program(owner=o1), Program(owner=o2)
    ra = observe_seed_execution(pa, SEED)
    rb = observe_seed_execution(pb, f'54[Query](predicate="password={MARKER}")')
    la = getattr(pa, "core_ii", None).last_result
    lb = getattr(pb, "core_ii", None).last_result
    _rec("Query count/value identical to non-Sanitize control",
         la.get("count") == lb.get("count") and la.get("value") == lb.get("value")
         and la.get("matched") == lb.get("matched"),
         f"{la.get('count')}/{lb.get('count')}")
    _rec("control chain (no Sanitize) is NOT redacted",
         any(MARKER in str(m) for m in rb.get("messages", [])))
    _cleanup(o1); _cleanup(o2)

    # ---------- Ordinary text is not damaged ----------
    o3 = "step3bordCC"
    _cleanup(o3)
    p3 = Program(owner=o3)
    r3 = observe_seed_execution(
        p3, '41[Sanitize] > 54[Query](predicate="hello world")')
    _rec("ordinary predicate text survives byte-identical",
         any("q=hello world" in str(m) for m in r3.get("messages", [])))
    _cleanup(o3)

    # ---------- Sibling sweep: Match (58) in a Sanitize chain ----------
    o4 = "step3bsibDD"
    _cleanup(o4)
    p4 = Program(owner=o4)
    r4 = observe_seed_execution(
        p4, f'41[Sanitize] > 58[Match](pattern="password={MARKER}")')
    surf4 = _surfaces(p4, r4)
    _rec("sibling Match chain: marker absent from all surfaces",
         all(MARKER not in blob for blob in surf4.values()))
    _cleanup(o4)

    # ---------- Sibling sweep: leaf note_seed label (Dell 3 Logic) ----------
    # Logic records its label via Program.note_seed — a history
    # writer that only the program-level redaction flag protects
    # (the CoreII mark() sanitization cannot reach it).
    o4b = "step3bleafDD"
    _cleanup(o4b)
    p4b = Program(owner=o4b)
    r4b = observe_seed_execution(
        p4b, f"41[Sanitize] > 03[Logic] :: password={MARKER}")
    surf4b = _surfaces(p4b, r4b)
    _rec("leaf-note_seed chain: marker absent from all surfaces",
         all(MARKER not in blob for blob in surf4b.values()))
    _cleanup(o4b)

    # ---------- Legacy label form ----------
    o5 = "step3blegEE"
    _cleanup(o5)
    p5 = Program(owner=o5)
    r5 = observe_seed_execution(p5, f"41[Sanitize] > 54[Query] :: password={MARKER}")
    surf5 = _surfaces(p5, r5)
    _rec("legacy-label chain: marker absent from all surfaces",
         all(MARKER not in blob for blob in surf5.values()))
    path5 = p5.save()
    with open(path5, encoding="utf-8", errors="replace") as fh:
        _rec("legacy-label chain: marker absent from saved JSON",
             MARKER not in fh.read())
    _cleanup(o5)

    # ---------- Sanitize second: chain-level requirement ----------
    o6 = "step3brevFF"
    _cleanup(o6)
    p6 = Program(owner=o6)
    r6 = observe_seed_execution(
        p6, f'54[Query](predicate="password={MARKER}") > 41[Sanitize]')
    surf6 = _surfaces(p6, r6)
    _rec("reversed chain: marker absent from all surfaces",
         all(MARKER not in blob for blob in surf6.values()))

    # ---------- Flag does not stick to later executions ----------
    r7 = observe_seed_execution(
        p6, f'54[Query](predicate="password={MARKER}")')
    _rec("redaction flag clears after the Sanitize chain",
         any(MARKER in str(m) for m in r7.get("messages", [])))
    _cleanup(o6)

    leftovers = []
    base = os.path.join(_ROOT, "form", "state")
    if os.path.isdir(base):
        leftovers = [f for f in os.listdir(base) if "step3b" in f.lower()]
    _rec("cleanup leaves no residue", leftovers == [], str(leftovers))

    passed = sum(1 for _, ok_, _ in RESULTS if ok_)
    for name, ok_, detail in RESULTS:
        if not ok_:
            print(f"FAIL {name}: {detail}")
    print(f"STEP3B_SANITIZE_CHAIN: {passed}/{len(RESULTS)}")
    return passed == len(RESULTS) and len(RESULTS) > 0


def smoke():
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
