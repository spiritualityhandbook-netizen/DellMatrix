"""D1 circuit 21 (registry pass, Core II B) — Dells
70-83 DEEP CONTRACTS.

The second Core II cluster of the full-registry pass:
the quantity arm 70-75 (query_ops), the semantic arm
76-79 (query_ops), and the object/scope arm 80-83
(spectrum_ops + core_ii_exec). Contracts proven here,
per Dell, through the public seed path:

- 70 Count: cardinality of the CURRENT selection
  only — value == count == len(selected), matched
  is True even at 0, and Count is read-only (the
  selection is byte-identical afterwards).
- 71 Measure: parses an optional "unit:kind" label.
  PINNED EXHIBIT: whatever the kind says — even a
  bogus one — the measured value is ALWAYS
  float(len(selected)); Measure is cardinality
  dressed with a unit/kind echo, never a property
  measurement.
- 72 Limit: bare (or "max") is the default bound 8;
  integers 0..64 are accepted (0 included); a float
  label is silently truncated ("8.5" -> 8); anything
  else (65, -3, "abc", "min", "max=10") fails
  invalid_limit and leaves st.limit unchanged.
- 73 Threshold: a typed predicate over the shared
  engine — bare is "gte:count 0" (True), a plain
  number becomes "gte:count N", and store refs work
  ("gte:store:n 3"); a miss is matched=False in the
  cell while the atom itself stays ok=True.
- 74 Weight: "k=v" stores float(v) in st.weights
  (a bare Weight stores target=1.0); non-finite or
  non-numeric values (nan, inf, abc) fail
  nonfinite_weight with no mutation.
- 75 Normalize: rescales st.weights to sum 1.0 in
  place and is idempotent; on an empty (or zero-sum)
  weight set it reports zero_set, matched=False,
  while the atom stays ok=True.
- 76 Resolve: resolves its LABEL against the active
  Dell registry (Director order step 10 / B11,
  superseding the original manifest exhibit, which
  resolved Resolve's own bracket term and ignored
  non-numeric labels): ":: Select" and ":: 51" both
  hit Select at conf 1.00; an unknown label is an
  honest miss (matched=False, conf 0.00,
  error="missing"); bare Resolve is a miss with
  error="target_required". The atom stays ok=True;
  the result cell carries the outcome (Get precedent).
- 77 Infer: NEVER a fact — matched=False,
  projected=True, fact=False on every call; the
  conclusion is the label verbatim; confidence is
  inherited from the previous result cell (1.0
  after a hit Query), 0.6 for fresh explicit
  evidence, 0.0 for a bare first call, whose
  evidence field falls back to the literal label.
- 78 Cause / 79 Depend: "a > b" appends the pair to
  st.causes / st.deps; a duplicate is ok=True with
  matched=False / duplicate_relation and no second
  append; a self-relation fails self_relation; a
  missing ">", an empty side, or a bare call fails
  malformed_relation (the grounding note in the
  execution state).
- 80 Context: sets st.context (bare falls back to
  the current scope name, NOT to ""); publishes NO
  result cell (last_result keeps the previous
  Dell's cell, like Dell 55).
- 81 Reference: refs[name] = target with no copy —
  bare targets selected[0]; on an empty selection
  it records refs["ref"] = ""; publishes NO result
  cell and mutates neither selection nor store.
- 82 Group: groups[name] = a SNAPSHOT COPY of the
  current selection (later Filter narrowing does
  not shrink the group); an empty selection falls
  back to all plane ids; re-grouping the same name
  overwrites; bare name is "group"; publishes NO
  result cell.
- 83 Ungroup: pops the group (bare = the last
  group); members land in the selection ONLY when
  the selection is empty; ungrouping the ACTIVE
  scope group prints the R1 scope warning and
  leaves the scope dangling — Select then refuses
  scope_unknown until the scope is reset. Step 10
  (B12, superseding the original silent-no-op
  exhibit): ungrouping a name that does not exist
  REFUSES ok=False err=ungroup_missing:<name> with
  zero mutation; an existing EMPTY group still
  ungroups ok=True released=0.

Cluster symbiosis: Filter (52) narrows what Count
(70) and Measure (71) report; Set's (55) store is
what Threshold (73) compares against; Group (82)
creates the scope Scope (53) selects within and
Ungroup (83) can dangle; Query's (54) confidence is
what Infer (77) inherits. One literal-REPL leg for
REAL_USER_PATH evidence.

House pattern: RESULTS + _rec; loud cleanup
(owner-wide glob; the test owners are unique to
this suite)."""
import os
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from form.mandell.dell_cards import DEEP_NOTES          # noqa: E402

RESULTS = []


def _rec(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))


def _cleanup(owner):
    import glob
    import shutil
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


def _program(owner):
    from form.open import Program
    _cleanup(owner)
    prog = Program(owner=owner)
    from form.mandell.core_ii_exec import attach
    attach(prog)
    return prog


def _run(prog, seed):
    from form.mandell.executor import execute_seed
    return execute_seed(prog, seed)


def _msgs(r):
    return [m for m in r.get("messages", [])
            if not m.startswith(("Mandell:", "English:",
                                 "Chain atoms=", "-- "))]


def _st(p):
    return p.core_ii


def main():
    owner = "D1RegCoreIIB"
    p = _program(owner)
    st = _st(p)

    # -- 70 Count / 71 Measure on empty + full selection
    r = _run(p, "70[Count]")
    _rec("70 Count: on an empty selection Count is 0 "
         "with matched=True (zero is a real count, "
         "not a miss)",
         r.get("ok") is True
         and _msgs(r) == ["Count 0"]
         and st.last_result.get("value") == 0
         and st.last_result.get("matched") is True
         and st.last_result.get("source") == "count",
         str(_msgs(r)))
    _run(p, "08[Create] :: Garden Gate")
    _run(p, "08[Create] :: Garden Path")
    _run(p, "08[Create] :: Stone Wall")
    _run(p, "51[Select]")
    before = list(st.selected)
    r = _run(p, "70[Count]")
    _rec("70 Count: counts the CURRENT selection "
         "(4 incl. welcome) and is read-only — the "
         "selection is byte-identical afterwards",
         _msgs(r) == ["Count 4"]
         and st.last_result.get("value") == 4
         and st.last_result.get("count") == 4
         and st.selected == before, str(_msgs(r)))
    r = _run(p, "71[Measure]")
    _rec("71 Measure: bare Measure reports "
         "float(len(selected)) with unit/kind 'count'",
         _msgs(r) == ["Measure count=4.0 unit=count"]
         and st.last_result.get("value") == 4.0
         and isinstance(st.last_result.get("value"), float)
         and st.last_result.get("unit") == "count"
         and st.last_result.get("measure_kind") == "count",
         str(_msgs(r)))
    r = _run(p, "71[Measure] :: items:selected")
    _rec("71 Measure: a 'unit:kind' label is parsed "
         "into unit and measure_kind on the cell",
         _msgs(r) == ["Measure selected=4.0 unit=items"]
         and st.last_result.get("unit") == "items"
         and st.last_result.get("measure_kind") == "selected",
         str(_msgs(r)))
    r = _run(p, "71[Measure] :: bogus")
    _rec("71 Measure EXHIBIT: even a bogus kind "
         "measures float(len(selected)) — Measure is "
         "cardinality with a kind echo, never a "
         "property measurement",
         _msgs(r) == ["Measure bogus=4.0 unit=count"]
         and st.last_result.get("value") == 4.0
         and st.last_result.get("measure_kind") == "bogus",
         str(_msgs(r)))

    # -- symbiosis: Filter narrows Count/Measure
    _run(p, "52[Filter] :: garden")
    r = _run(p, "70[Count]")
    r2 = _run(p, "71[Measure]")
    _rec("symbiosis: Filter (52) narrows the "
         "selection and Count (70) / Measure (71) "
         "both report the filtered cardinality (2)",
         _msgs(r) == ["Count 2"]
         and _msgs(r2) == ["Measure count=2.0 unit=count"],
         str((_msgs(r), _msgs(r2))))

    # -- 72 Limit
    r = _run(p, "72[Limit]")
    _rec("72 Limit: bare Limit installs the default "
         "bound 8",
         _msgs(r) == ["Limit 8"] and st.limit == "8"
         and st.last_result.get("value") == 8,
         str(_msgs(r)))
    _run(p, "72[Limit] :: 5")
    r = _run(p, "72[Limit] :: 8.5")
    _rec("72 Limit EXHIBIT: a float label is "
         "silently truncated — '8.5' installs 8",
         _msgs(r) == ["Limit 8"] and st.limit == "8",
         str(_msgs(r)))
    bad = []
    for lab in ("65", "-3", "abc", "min", "max=10"):
        rr = _run(p, f"72[Limit] :: {lab}")
        bad.append(rr.get("ok") is False
                   and rr.get("error") == "invalid_limit")
    _rec("72 Limit: out-of-range / non-numeric "
         "labels (65, -3, abc, min, max=10) all fail "
         "invalid_limit and leave st.limit unchanged",
         all(bad) and st.limit == "8"
         and st.last_result.get("error") == "invalid_limit",
         str(bad))
    r = _run(p, "72[Limit] :: 0")
    _rec("72 Limit: 0 is an accepted bound (the "
         "range is 0..64 inclusive)",
         r.get("ok") is True and st.limit == "0",
         str(_msgs(r)))

    # -- 73 Threshold
    r = _run(p, "73[Threshold]")
    _rec("73 Threshold: bare Threshold is "
         "'gte:count 0' and matches",
         _msgs(r) == ["Threshold gte:count 0 matched=True"]
         and st.last_result.get("value") is True
         and st.last_result.get("source") == "threshold",
         str(_msgs(r)))
    r = _run(p, "73[Threshold] :: 2")
    _rec("73 Threshold: a plain number becomes "
         "'gte:count N' over the selection size (2)",
         _msgs(r) == ["Threshold gte:count 2 matched=True"]
         and st.last_result.get("matched") is True,
         str(_msgs(r)))
    r = _run(p, "73[Threshold] :: gte:count 99")
    _rec("73 Threshold: a miss is matched=False in "
         "the cell while the atom stays ok=True",
         r.get("ok") is True
         and _msgs(r) == ["Threshold gte:count 99 "
                          "matched=False"]
         and st.last_result.get("value") is False,
         str(_msgs(r)))
    _run(p, "55[Set] :: n=5")
    r = _run(p, "73[Threshold] :: gte:store:n 3")
    r2 = _run(p, "73[Threshold] :: gte:store:n 9")
    _rec("symbiosis: Threshold (73) compares "
         "against Set's (55) store — store:n=5 passes "
         "gte 3 and fails gte 9",
         _msgs(r) == ["Threshold gte:store:n 3 "
                      "matched=True"]
         and _msgs(r2) == ["Threshold gte:store:n 9 "
                           "matched=False"],
         str((_msgs(r), _msgs(r2))))

    # -- 74 Weight / 75 Normalize
    r = _run(p, "75[Normalize]")
    _rec("75 Normalize: on an empty weight set it "
         "reports zero_set / matched=False while the "
         "atom stays ok=True and weights stay empty",
         r.get("ok") is True
         and _msgs(r) == ["Normalize zero_set"]
         and st.last_result.get("error") == "zero_set"
         and st.last_result.get("matched") is False
         and st.weights == {}, str(_msgs(r)))
    _run(p, "74[Weight] :: alpha=2")
    _run(p, "74[Weight] :: beta=6")
    r = _run(p, "74[Weight]")
    _rec("74 Weight: 'k=v' stores float weights; a "
         "bare Weight stores target=1.0",
         _msgs(r) == ["Weight target=1.0"]
         and st.weights == {"alpha": 2.0, "beta": 6.0,
                            "target": 1.0},
         str(_msgs(r)))
    bad = []
    for lab in ("bad=nan", "bad=inf", "bad=abc"):
        rr = _run(p, f"74[Weight] :: {lab}")
        bad.append(rr.get("ok") is False
                   and rr.get("error") == "nonfinite_weight")
    _rec("74 Weight: nan / inf / non-numeric values "
         "fail nonfinite_weight with no mutation",
         all(bad) and "bad" not in st.weights
         and len(st.weights) == 3, str(bad))
    r = _run(p, "75[Normalize]")
    w = dict(st.weights)
    r2 = _run(p, "75[Normalize]")
    _rec("75 Normalize: rescales weights to sum 1.0 "
         "preserving proportions (2/9, 6/9, 1/9) and "
         "is idempotent",
         _msgs(r) == ["Normalize n=3 sum=1.000000"]
         and abs(sum(w.values()) - 1.0) < 1e-9
         and abs(w.get("alpha", 0) - 2 / 9) < 1e-9
         and abs(w.get("beta", 0) - 6 / 9) < 1e-9
         and st.weights == w, str(_msgs(r)))

    # -- 76 Resolve
    r = _run(p, "76[Resolve]")
    _rec("76 Resolve: bare Resolve is an honest "
         "target_required miss (step 10 / B11) — the "
         "atom stays ok, the cell carries the miss",
         r.get("ok") is True
         and _msgs(r) == ["Resolve =MISSING target_required"]
         and st.last_result.get("value") is None
         and st.last_result.get("matched") is False
         and st.last_result.get("confidence") == 0.0
         and st.last_result.get("error") == "target_required",
         str(_msgs(r)))
    r = _run(p, "76[Resolve] :: Select")
    r2 = _run(p, "76[Resolve] :: bogusname")
    _rec("76 Resolve: the label IS the target — "
         "':: Select' hits Select at conf 1.00 while "
         "':: bogusname' is an honest miss (step 10)",
         _msgs(r) == ["Resolve Select=Select dell=51 "
                      "conf=1.00"]
         and _msgs(r2) == ["Resolve bogusname=MISSING"],
         str((_msgs(r), _msgs(r2))))
    r = _run(p, "76[Resolve] :: 51")
    _rec("76 Resolve: a numeric label resolves its "
         "dell at conf 1.00 — ':: 51' is Select, "
         "never the old 0.40 manifest fallback",
         _msgs(r) == ["Resolve 51=Select dell=51 "
                      "conf=1.00"]
         and st.last_result.get("value") == "Select"
         and st.last_result.get("confidence") == 1.0,
         str(_msgs(r)))

    # -- 77 Infer (confidence inheritance in main owner)
    _run(p, "54[Query] :: garden")
    r = _run(p, "77[Infer] :: from query")
    _rec("77 Infer: after a hit Query (conf 1.0) "
         "Infer inherits that confidence, yet stays "
         "matched=False / projected=True / fact=False "
         "— an inference is never a fact",
         _msgs(r) == ["Infer from query "
                      "PROJECTED_NOT_FACT"]
         and st.last_result.get("confidence") == 1.0
         and st.last_result.get("matched") is False
         and st.last_result.get("projected") is True
         and st.last_result.get("fact") is False
         and st.last_result.get("conclusion") == "from query",
         str(_msgs(r)))

    # -- 78 Cause / 79 Depend
    r = _run(p, "78[Cause]")
    _rec("78 Cause: a bare Cause fails "
         "malformed_relation honestly (no '>' pair)",
         r.get("ok") is False
         and r.get("error") == "malformed_relation"
         and st.causes == [], str(_msgs(r)))
    _run(p, "78[Cause] :: rain > flood")
    r = _run(p, "78[Cause] :: rain > flood")
    _rec("78 Cause: 'rain > flood' appends the "
         "pair; a duplicate is ok=True with "
         "duplicate_relation and NO second append",
         _msgs(r) == ["Cause duplicate rain->flood"]
         and st.causes == [("rain", "flood")]
         and st.last_result.get("matched") is False
         and st.last_result.get("error")
         == "duplicate_relation", str(_msgs(r)))
    r = _run(p, "78[Cause] :: rain > rain")
    r2 = _run(p, "78[Cause] :: > flood")
    _rec("78 Cause: a self-relation fails "
         "self_relation and an empty side fails "
         "malformed_relation; neither appends",
         r.get("error") == "self_relation"
         and r2.get("error") == "malformed_relation"
         and st.causes == [("rain", "flood")],
         str((_msgs(r), _msgs(r2))))
    _run(p, "79[Depend] :: gate > key")
    r = _run(p, "79[Depend] :: gate > key")
    r2 = _run(p, "79[Depend]")
    _rec("79 Depend: 'gate > key' records 'gate "
         "requires key' in st.deps; a duplicate does "
         "not re-append; a bare Depend fails "
         "malformed_relation like Cause",
         st.deps == [("gate", "key")]
         and _msgs(r) == ["Depend duplicate gate->key"]
         and r2.get("ok") is False
         and r2.get("error") == "malformed_relation",
         str((_msgs(r), _msgs(r2))))

    # -- 80 Context / 81 Reference (no result cells)
    cell_before = dict(st.last_result)
    r = _run(p, "80[Context] :: nursery")
    _rec("80 Context: sets st.context and "
         "publishes NO result cell (the previous "
         "Dell's cell survives, like Dell 55)",
         _msgs(r) == ["Context -> nursery"]
         and st.context == "nursery"
         and st.last_result == cell_before,
         str(_msgs(r)))
    r = _run(p, "80[Context]")
    _rec("80 Context: a bare Context falls back to "
         "the current SCOPE name ('plane'), not ''",
         _msgs(r) == ["Context -> plane"]
         and st.context == "plane", str(_msgs(r)))
    sel_before, store_before = list(st.selected), dict(st.store)
    cell_before = dict(st.last_result)
    r = _run(p, "81[Reference]")
    _rec("81 Reference: bare Reference points at "
         "selected[0] with no copy — refs gains the "
         "entry, selection/store are unchanged, and "
         "no result cell is published",
         _msgs(r) == ["Reference garden_gate -> "
                      "garden_gate no_copy"]
         and st.refs.get("garden_gate") == "garden_gate"
         and st.selected == sel_before
         and st.store == store_before
         and st.last_result == cell_before,
         str(_msgs(r)))

    # -- 82 Group / 83 Ungroup + scope symbiosis
    cell_before = dict(st.last_result)
    r = _run(p, "82[Group] :: g1")
    _rec("82 Group: groups the current selection "
         "under g1 and publishes NO result cell",
         _msgs(r) == ["Group g1 n=2"]
         and st.groups.get("g1")
         == ["garden_gate", "garden_path"]
         and st.last_result == cell_before,
         str(_msgs(r)))
    _run(p, "52[Filter] :: gate")
    _rec("82 Group: the group is a SNAPSHOT copy — "
         "narrowing the selection afterwards does "
         "not shrink the group",
         st.selected == ["garden_gate"]
         and st.groups.get("g1")
         == ["garden_gate", "garden_path"],
         str(st.groups))
    _run(p, "82[Group] :: g1")
    _rec("82 Group: re-grouping the same name "
         "overwrites it with the current selection",
         st.groups.get("g1") == ["garden_gate"],
         str(st.groups))
    _run(p, "51[Select]")
    _run(p, "82[Group] :: g1")
    _run(p, "53[Scope] :: g1")
    r = _run(p, "51[Select]")
    _rec("symbiosis: Group (82) creates the scope "
         "Scope (53) binds and Select (51) reads — "
         "selecting inside g1 yields exactly its "
         "members",
         _msgs(r) == ["Select scope=g1 n=4"]
         and st.selected
         == ["welcome", "garden_gate", "garden_path",
             "stone_wall"],
         str(_msgs(r)))
    r = _run(p, "83[Ungroup] :: g1")
    r2 = _run(p, "51[Select]")
    _rec("83 Ungroup: ungrouping the ACTIVE scope "
         "group prints the R1 scope warning, leaves "
         "the scope dangling, and Select then "
         "refuses scope_unknown (fail-closed)",
         _msgs(r) == ["Ungroup g1 released=4",
                      "Ungroup warning: scope 'g1' is "
                      "now undefined; Select will "
                      "refuse until the scope is reset"]
         and r2.get("ok") is False
         and r2.get("error") == "scope_unknown:g1",
         str((_msgs(r), _msgs(r2))))
    _run(p, "53[Scope] :: plane")
    r = _run(p, "83[Ungroup] :: nosuch")
    _rec("83 Ungroup: ungrouping a name that does "
         "not exist REFUSES ungroup_missing:nosuch "
         "(step 10 / B12; the original silent-no-op "
         "exhibit is superseded)",
         r.get("ok") is False
         and r.get("error") == "ungroup_missing:nosuch"
         and _msgs(r) == ["Ungroup missing nosuch"],
         str(_msgs(r)))
    _cleanup(owner)

    # -- 77 Infer on a fresh owner (confidence floor)
    owner_i = "D1RegCoreIIBI"
    ip = _program(owner_i)
    ist = _st(ip)
    r = _run(ip, "77[Infer]")
    _rec("77 Infer: a bare first-ever Infer has "
         "conf 0.0 and its evidence field is the "
         "literal fallback label 'evidence'",
         _msgs(r) == ["Infer evidence "
                      "PROJECTED_NOT_FACT"]
         and ist.last_result.get("confidence") == 0.0
         and ist.last_result.get("evidence") == "evidence"
         and ist.last_result.get("projected") is True,
         str(_msgs(r)))
    r = _run(ip, "77[Infer] :: something new")
    _rec("77 Infer: fresh explicit evidence gets "
         "conf 0.6 (no prior cell to inherit from)",
         ist.last_result.get("confidence") == 0.6
         and ist.last_result.get("evidence")
         == "something new", str(_msgs(r)))
    _cleanup(owner_i)

    # -- 81/82/83 on an empty-selection owner
    owner_b = "D1RegCoreIIBB"
    bp = _program(owner_b)
    bst = _st(bp)
    r = _run(bp, "81[Reference]")
    _rec("81 Reference: on an empty selection it "
         "records refs['ref'] = '' (an explicit "
         "none, not a failure)",
         _msgs(r) == ["Reference ref -> (none) no_copy"]
         and bst.refs == {"ref": ""}, str(_msgs(r)))
    r = _run(bp, "82[Group] :: allids")
    _rec("82 Group: on an empty selection Group "
         "falls back to ALL plane ids (welcome)",
         _msgs(r) == ["Group allids n=1"]
         and bst.groups.get("allids") == ["welcome"],
         str(_msgs(r)))
    r = _run(bp, "83[Ungroup] :: allids")
    _rec("83 Ungroup: members land in the "
         "selection ONLY because the selection was "
         "empty — ungroup restores them there",
         _msgs(r) == ["Ungroup allids released=1"]
         and bst.selected == ["welcome"]
         and bst.groups == {}, str(_msgs(r)))
    _run(bp, "82[Group] :: x1")
    _run(bp, "82[Group] :: x2")
    r = _run(bp, "83[Ungroup]")
    _rec("83 Ungroup: a bare Ungroup releases the "
         "LAST group created",
         _msgs(r) == ["Ungroup x2 released=1"]
         and list(bst.groups) == ["x1"],
         str(_msgs(r)))
    _cleanup(owner_b)

    # -- REAL_USER_PATH: literal REPL seed lines
    owner2 = "D1RegCoreIIBRepl"
    _cleanup(owner2)
    proc = subprocess.run(
        [sys.executable, "-m", "form.repl", "--owner", owner2],
        input="08[Create] :: Garden Gate\n51[Select]\n"
              "70[Count]\n74[Weight] :: alpha=2\n"
              "82[Group] :: g1\n",
        capture_output=True, text=True, cwd=_ROOT, timeout=120)
    out = proc.stdout or ""
    _rec("REPL: Count, Weight and Group execute on "
         "the literal user path",
         proc.returncode == 0
         and "Count 2" in out
         and "Weight alpha=2.0" in out
         and "Group g1 n=2" in out, out[-300:])
    _cleanup(owner2)

    # -- docs pins
    _rec("proof cards carry circuit-21 deep notes "
         "(70-83)",
         all(n in DEEP_NOTES and "circuit 21" in DEEP_NOTES[n]
             for n in range(70, 84)),
         str([n for n in range(70, 84)
              if n not in DEEP_NOTES]))

    total = len(RESULTS)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        if not ok:
            print(f"FAIL {name} :: {detail}")
    print(f"D1_REGISTRY_COREII_B: {passed}/{total}")
    return passed == total


def smoke():
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
