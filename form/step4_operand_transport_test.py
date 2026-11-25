#!/usr/bin/env python3
"""Director order step 4 — DAF-01 + DAF-07.

DAF-01: typed operands were flattened into a delimiter string
and recovered by longest-existing-key guessing, so a value or
destination containing '=' or '>' retargeted Patch/Move/
Replace onto a colliding neighbor key. Contract: validated
typed roles are carried LOSSLESSLY into the canonical handlers
(85/87/88/55); legacy labels with two or more existing split
candidates are ambiguous and refuse BEFORE mutation with the
store byte-unchanged; AF-2's determinate cases (exactly one
existing candidate, or none) are byte-preserved.

DAF-07: adjacent atoms escaped parse_seed as an IndexError and
duplicate named roles silently overwrote. Contract: atom/
operator alternation and duplicate roles are structured parse
refusals (no exception, no mutation, the program stays live);
trailing operators and malformed quotes remain refusals;
valid delimiter-containing quoted values still work.

Public entry path (execute_seed / parse_seed); isolated
synthetic owner with loud cleanup.
"""
import glob
import os
import shutil
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

RESULTS = []
OWNER = "step4opZZ"


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


def main():
    from form.open import Program
    from form.mandell.core_ii_exec import attach
    from form.mandell.executor import execute_seed
    from form.mandell.seed import parse_seed

    def fresh(store=None):
        _cleanup(OWNER)
        p = Program(owner=OWNER)
        st = attach(p)
        if store:
            st.store.update(store)
        return p, st

    # ---- DAF-01 typed: the Director's exact counterexamples ----
    p, st = fresh({"a": "TARGET", "a=b": "NEIGHBOR", "z": "KEEP"})
    r = execute_seed(p, '88[Patch](key="a", value="b=NEW")')
    _rec("DAF-01 typed Patch patches the named key only",
         r.get("ok") and dict(st.store) == {"a": "b=NEW", "a=b": "NEIGHBOR", "z": "KEEP"},
         f"ok={r.get('ok')} store={dict(st.store)}")

    p, st = fresh({"a": "TARGET", "a>b": "NEIGHBOR", "z": "KEEP"})
    r = execute_seed(p, '85[Move](source="a", destination="b>c")')
    _rec("DAF-01 typed Move moves the named source only",
         r.get("ok") and dict(st.store) == {"a>b": "NEIGHBOR", "z": "KEEP", "b>c": "TARGET"},
         f"ok={r.get('ok')} store={dict(st.store)}")

    p, st = fresh({"a": "TARGET", "a>b": "NEIGHBOR", "z": "KEEP"})
    r = execute_seed(p, '87[Replace](old="a", new="b>c")')
    _rec("DAF-01 typed Replace renames the named key only",
         r.get("ok") and dict(st.store) == {"a>b": "NEIGHBOR", "z": "KEEP", "b>c": "TARGET"},
         f"ok={r.get('ok')} store={dict(st.store)}")

    p, st = fresh({"a": "TARGET", "a=b": "NEIGHBOR"})
    r = execute_seed(p, '55[Set](key="a", value="b=NEW")')
    _rec("DAF-01 typed Set sets the named key only",
         r.get("ok") and dict(st.store) == {"a": "b=NEW", "a=b": "NEIGHBOR"},
         f"ok={r.get('ok')} store={dict(st.store)}")

    p, st = fresh()
    r = execute_seed(p, '55[Set](key="x=y", value="v=1")')
    _rec("DAF-01 typed Set creates a delimiter key losslessly",
         r.get("ok") and dict(st.store) == {"x=y": "v=1"},
         f"ok={r.get('ok')} store={dict(st.store)}")

    p, st = fresh({"x": "SHORT", "x=y": "LONG"})
    r = execute_seed(p, '88[Patch](key="x=y", value="2")')
    _rec("DAF-01 typed Patch addresses a delimiter key directly",
         r.get("ok") and dict(st.store) == {"x": "SHORT", "x=y": "2"},
         f"ok={r.get('ok')} store={dict(st.store)}")

    p, st = fresh({"a": "TARGET", "a=b": "NEIGHBOR"})
    r = execute_seed(p, '88[Patch](key="a", value="b=NEW") > 70[Count]')
    _rec("DAF-01 typed Patch lossless inside a chain (AF-1 parity)",
         r.get("ok") and st.store.get("a") == "b=NEW"
         and st.store.get("a=b") == "NEIGHBOR",
         f"ok={r.get('ok')} err={r.get('error')} store={dict(st.store)}")

    p, st = fresh({"a": "TARGET", "a>b": "NEIGHBOR"})
    r = execute_seed(p, '87[Replace](old="a", new="a>b")')
    _rec("DAF-01 typed Replace occupied destination still refuses, zero mutation",
         not r.get("ok") and "replace_occupied" in str(r.get("error"))
         and dict(st.store) == {"a": "TARGET", "a>b": "NEIGHBOR"},
         f"ok={r.get('ok')} err={r.get('error')} store={dict(st.store)}")

    p, st = fresh({"a": "TARGET", "c": "OLD"})
    r = execute_seed(p, '85[Move](source="a", destination="c")')
    _rec("B20 typed Move overwrite semantics preserved",
         r.get("ok") and dict(st.store) == {"c": "TARGET"},
         f"ok={r.get('ok')} store={dict(st.store)}")

    # ---- DAF-01 legacy: ambiguous labels refuse before mutation ----
    for seed_txt, err_id in (
            ("88[Patch] :: a=b=NEW", "ambiguous_patch"),
            ("85[Move] :: a>b>c", "ambiguous_move"),
            ("87[Replace] :: a>b>c", "ambiguous_replace"),
            ("55[Set] :: a=b=NEW", "ambiguous_set")):
        base = {"a": "TARGET", "a=b": "NEIGHBOR", "a>b": "NEIGHBOR2", "z": "KEEP"}
        p, st = fresh(base)
        r = execute_seed(p, seed_txt)
        _rec(f"DAF-01 legacy ambiguous refuses ({err_id}), store byte-equal",
             not r.get("ok") and err_id in str(r.get("error"))
             and dict(st.store) == base,
             f"ok={r.get('ok')} err={r.get('error')} store={dict(st.store)}")

    # ---- DAF-01 legacy: AF-2 determinate cases preserved ----
    p, st = fresh({"x=y": "OLD"})
    r = execute_seed(p, "88[Patch] :: x=y=2")
    _rec("AF-2 exactly-one-existing still addresses the long key",
         r.get("ok") and dict(st.store) == {"x=y": "2"},
         f"ok={r.get('ok')} store={dict(st.store)}")
    p, st = fresh({"x": "1"})
    r = execute_seed(p, "88[Patch] :: x=y=2")
    _rec("AF-2 no-longer-key fallback still patches the short key",
         r.get("ok") and dict(st.store) == {"x": "y=2"},
         f"ok={r.get('ok')} store={dict(st.store)}")
    p, st = fresh()
    r = execute_seed(p, "55[Set] :: fresh=a=b")
    _rec("AF-2 fresh Set creation still splits at the first '='",
         r.get("ok") and dict(st.store) == {"fresh": "a=b"},
         f"ok={r.get('ok')} store={dict(st.store)}")

    # ---- DAF-07: malformed grammar is a structured refusal ----
    sd = parse_seed("51[Select] 54[Query]")
    _rec("DAF-07 adjacent atoms refuse at parse (no IndexError)",
         not sd.ok and "missing flow operator" in sd.error,
         f"ok={sd.ok} err={sd.error}")
    p, st = fresh({"a": "TARGET"})
    r = execute_seed(p, "51[Select] 54[Query]")
    _rec("DAF-07 adjacent atoms execute as refusal, zero mutation",
         not r.get("ok") and "missing flow operator" in str(r.get("error"))
         and dict(st.store) == {"a": "TARGET"},
         f"ok={r.get('ok')} err={r.get('error')}")
    r = execute_seed(p, "55[Set] :: after=alive")
    _rec("DAF-07 program stays live after a parse refusal",
         r.get("ok") and st.store.get("after") == "alive",
         f"ok={r.get('ok')} err={r.get('error')}")
    sd = parse_seed('88[Patch](key="a", value="1") 70[Count]')
    _rec("DAF-07 adjacent atoms after typed args refuse",
         not sd.ok and "missing flow operator" in sd.error,
         f"ok={sd.ok} err={sd.error}")
    sd = parse_seed("51[Select] >")
    _rec("DAF-07 trailing operator refuses at parse",
         not sd.ok and bool(sd.error), f"ok={sd.ok} err={sd.error}")
    sd = parse_seed("51[Select] > > 54[Query]")
    _rec("DAF-07 doubled operator refuses at parse",
         not sd.ok and bool(sd.error), f"ok={sd.ok} err={sd.error}")
    sd = parse_seed('88[Patch](key="a, value="b")')
    _rec("DAF-07 malformed quote refuses at parse (no exception)",
         not sd.ok and bool(sd.error), f"ok={sd.ok} err={sd.error}")

    sd = parse_seed('88[Patch](key="a", key="b", value="N")')
    _rec("DAF-07 duplicate named role refuses at parse",
         not sd.ok and "duplicate role 'key'" in sd.error,
         f"ok={sd.ok} err={sd.error}")
    p, st = fresh({"a": "TARGET", "b": "OTHER"})
    r = execute_seed(p, '88[Patch](key="a", key="b", value="N")')
    _rec("DAF-07 duplicate role executes as refusal, zero mutation",
         not r.get("ok") and dict(st.store) == {"a": "TARGET", "b": "OTHER"},
         f"ok={r.get('ok')} err={r.get('error')} store={dict(st.store)}")

    p, st = fresh({"a": "TARGET"})
    r = execute_seed(p, '88[Patch](key="a", value="x::y > z=w")')
    _rec("DAF-07 valid delimiter-containing quoted value works",
         r.get("ok") and st.store.get("a") == "x::y > z=w",
         f"ok={r.get('ok')} err={r.get('error')} store={dict(st.store)}")
    sd = parse_seed("51[Select] > 54[Query]")
    _rec("DAF-07 valid chain still parses",
         sd.ok and [a.dell for a in sd.atoms] == [51, 54],
         f"ok={sd.ok} err={sd.error}")

    _cleanup(OWNER)
    passed = sum(1 for _, ok_, _ in RESULTS if ok_)
    for name, ok_, detail in RESULTS:
        if not ok_:
            print(f"FAIL {name}: {detail}")
    print(f"STEP4_OPERAND_TRANSPORT: {passed}/{len(RESULTS)}")
    return passed == len(RESULTS) and len(RESULTS) > 0


def smoke():
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
