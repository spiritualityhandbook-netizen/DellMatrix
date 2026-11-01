"""D1 circuit 20 (registry pass, Core II A) — Dells
52, 55, 59-66 DEEP CONTRACTS.

The first Core II cluster of the full-registry pass:
52 Filter and 55 Set (query/state arms in query_ops),
59 Route (query_ops), and the flow/control Dells
60-66 (core_ii_exec single-atom arms plus the
chain_exec control runtime). Contracts proven here,
per Dell, through the public seed path:

- 52 Filter: narrows the CURRENT selection only
  (never the plane) by the shared _pred engine
  (substring OR underscore-prefix, so a spaced phrase
  matches the underscored id); bare Filter is the
  identity; a no-match Filter is a SUCCESS that
  empties the selection (matched=False, count=0);
  publishes a filter result cell.
- 55 Set: the store writer — "k=v" stores v, a bare
  key stores "1", "k=" stores "", a bare Set stores
  value="1"; a snapshot of the PRE-write state is
  appended before the mutation. PINNED: Set
  publishes NO result cell — last_result still
  carries the previous Dell's cell after a Set.
- 59 Route: sets st.route (bare resets "primary")
  and publishes a route cell (matched=True). In a
  Branch chain the 59 atom is consumed as the Else
  marker and never executes as Route (designed
  clash, catalogued). The flow operator :>
  (FlowTowards) writes the same route channel.
- 60 Branch: single-atom arm records st.branch
  {cond, taken, path}; in a chain it runs only the
  taken arm to Join (the unchosen arm is skipped,
  listed in chain_skipped, and does not mutate).
- 61 Join: reads the results of the frame in
  st.last_frame — policy "all" (default) fails with
  join_fail if any incoming result failed, "any"
  passes if at least one did (or none came in).
  STEP 7 (B7/DAF-08): the Join that CLOSES a control
  block evaluates the completed block's ACTUAL results
  (the chain layer publishes them to last_frame before
  the Join runs) — no vacuous incoming=0 verdict when
  children ran; a Join invoked again afterwards sees
  the finished block's results the same way.
- 62 Parallel: single-atom arm parses the label as
  a comma list (bare defaults ["a", "b"]) and is
  "offline_deterministic"; in a chain the body runs
  sequentially, a sibling failure is captured (the
  remaining body still runs) and the chain reports
  the failure. STEP 7 (B7): the parallel last_control
  status is "fail" when a captured sibling failed —
  the closing Join's verdict is represented in the
  frame, with the chain error keeping the root cause.
- 63 Sequence: in a chain the body runs in written
  order to Join; the last writer wins shared state.
- 64 Until: loops the body until the condition
  holds; a body that makes the condition true exits
  after 1 iteration; a condition that never holds
  fails bound_reached at the Limit bound (default
  8). STEP 7 (B8): bare Until's two layers AGREE —
  the empty condition is true in both surfaces, so
  the core arm reports cond=true / already=True and
  the chain reports "already true — zero
  iterations" (status zero, ok=True); the frame
  exposes bound + iterations.
- 65 While: loops while the condition holds; bare
  While (condition defaults true) with an empty
  body fails bound_reached honestly; a false
  condition is zero iterations; a body that clears
  the condition (Delete of the store key) exits
  after 1 iteration.
- 66 ForEach: in a chain it iterates the CURRENT
  selection in order, binding each member (results
  carry the member), and restores route afterwards.
  STEP 7 (B9): on an empty selection BOTH surfaces
  report zero iterations — the core arm reports
  n=0 / empty_ok=True (no plane-id fallback) and
  the chain layer reports "empty selection valid"
  with status empty and 0 iterations — the body
  never runs.

Cluster symbiosis: Filter narrows Select's (51)
selection and Count (70) counts the filtered set;
Set's (55) writes are Get's (56) reads; While's
(65) condition is cleared by Delete (86) inside
its own body; Until's (64) condition is set by
Set (55) inside its own body; ForEach (66) walks
the selection Select (51) published. One literal-
REPL leg for REAL_USER_PATH evidence.

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
    owner = "D1RegCoreIIA"
    p = _program(owner)
    st = _st(p)

    # -- 52 Filter: empty selection
    r = _run(p, "52[Filter] :: x")
    _rec("52 Filter: on an empty selection Filter is "
         "0->0, ok=True, and publishes a non-matched "
         "filter cell",
         r.get("ok") is True
         and _msgs(r) == ["Filter 0->0 cond=x"]
         and st.last_result.get("source") == "filter"
         and st.last_result.get("matched") is False
         and st.last_result.get("count") == 0,
         str(_msgs(r)))

    # -- setup + Select all
    _run(p, "08[Create] :: Garden Gate")
    _run(p, "08[Create] :: Garden Path")
    _run(p, "08[Create] :: Stone Wall")
    _run(p, "51[Select]")
    r = _run(p, "52[Filter] :: garden")
    _rec("52 Filter: 'garden' narrows Select's 4-id "
         "selection to the two garden ids and "
         "publishes the filter cell (count=2)",
         _msgs(r) == ["Filter 4->2 cond=garden"]
         and st.selected == ["garden_gate", "garden_path"]
         and st.last_result.get("value") == ["garden_gate",
                                             "garden_path"]
         and st.last_result.get("matched") is True
         and st.last_result.get("count") == 2,
         str(_msgs(r)))
    r = _run(p, "52[Filter]")
    ok_bare = (_msgs(r) == ["Filter 2->2 cond=*"]
               and st.selected == ["garden_gate", "garden_path"])
    r = _run(p, "52[Filter] :: garden gate")
    _rec("52 Filter: bare Filter is the identity; a "
         "spaced phrase matches the underscored id "
         "by prefix ('garden gate' -> garden_gate)",
         ok_bare and _msgs(r) == ["Filter 2->1 cond=garden gate"]
         and st.selected == ["garden_gate"], str(_msgs(r)))
    r = _run(p, "52[Filter] :: zzz")
    _rec("52 Filter: a no-match Filter is a SUCCESS "
         "that empties the selection (matched=False) "
         "— Filter never widens back to the plane",
         r.get("ok") is True
         and _msgs(r) == ["Filter 1->0 cond=zzz"]
         and st.selected == []
         and st.last_result.get("matched") is False,
         str(_msgs(r)))

    # -- symbiosis: Select -> Filter -> Count
    _run(p, "51[Select] :: garden")
    _run(p, "52[Filter] :: gate")
    r = _run(p, "70[Count]")
    _rec("symbiosis: Count (70) counts the set Filter "
         "(52) narrowed from Select's (51) selection "
         "— exactly garden_gate",
         _msgs(r) == ["Count 1"]
         and st.last_result.get("value") == 1
         and st.selected == ["garden_gate"], str(_msgs(r)))

    # -- 55 Set: forms + pre-write snapshot + no cell
    prev_cell = dict(st.last_result)
    snap_before = len(st.snapshots)
    r = _run(p, "55[Set] :: mode=fast")
    _rec("55 Set: 'mode=fast' writes store[mode]; the "
         "appended snapshot holds the PRE-write store "
         "(no mode yet); Set publishes NO result cell "
         "(PINNED: last_result is still Count's cell)",
         _msgs(r) == ["Set mode=fast"]
         and st.store.get("mode") == "fast"
         and len(st.snapshots) == snap_before + 1
         and "mode" not in st.snapshots[-1].get("store", {})
         and st.last_result == prev_cell, str(_msgs(r)))
    _run(p, "55[Set] :: flag")
    _run(p, "55[Set] :: empty=")
    r = _run(p, "55[Set]")
    _rec("55 Set: a bare key stores '1', 'k=' stores "
         "the empty string, and a bare Set stores "
         "value='1'",
         _msgs(r) == ["Set value=1"]
         and st.store.get("flag") == "1"
         and st.store.get("empty") == ""
         and st.store.get("value") == "1", str(_msgs(r)))

    # -- symbiosis: Set -> Get
    r = _run(p, "56[Get] :: mode")
    _rec("symbiosis: Get (56) reads back the value "
         "Set (55) wrote (status ok, matched=True)",
         _msgs(r) == ["Get mode='fast' status=ok"]
         and st.last_result.get("value") == "fast"
         and st.last_result.get("source") == "get",
         str(_msgs(r)))

    # -- 59 Route: set + bare reset + cell
    r = _run(p, "59[Route] :: alt")
    ok_alt = (_msgs(r) == ["Route -> alt"]
              and st.route == "alt"
              and st.last_result.get("source") == "route"
              and st.last_result.get("value") == "alt"
              and st.last_result.get("matched") is True)
    r = _run(p, "59[Route]")
    _rec("59 Route: a label sets st.route and "
         "publishes the route cell; bare Route resets "
         "the route to 'primary'",
         ok_alt and _msgs(r) == ["Route -> primary"]
         and st.route == "primary", str(_msgs(r)))

    # -- symbiosis: FlowTowards overwrites route
    _run(p, "59[Route] :: backup")
    r = _run(p, "80[Context] :> 53[Scope]")
    _rec("symbiosis: the :> flow (FlowTowards) writes "
         "the SAME route channel Route (59) owns — "
         "after it, route is the next atom's term "
         "('Scope'), not Route's 'backup'",
         st.route == "Scope"
         and "FlowTowards Scope" in _msgs(r), str(_msgs(r)))
    _cleanup(owner)

    # ---- control singles (fresh owner) ----
    owner_b = "D1RegCoreIIAB"
    q = _program(owner_b)
    qs = _st(q)

    r = _run(q, "60[Branch]")
    ok_bare = (_msgs(r)[0] == "Branch cond=true taken=True "
               "unchosen_not_run"
               and qs.branch == {"cond": "true", "taken": True,
                                 "path": "true"})
    r = _run(q, "60[Branch] :: false")
    _rec("60 Branch: bare Branch defaults cond=true "
         "(taken, path 'true' recorded in st.branch); "
         "cond=false records taken=False / path false "
         "and the chain frame status is 'skipped'",
         ok_bare
         and _msgs(r)[0] == "Branch cond=false taken=False "
                            "unchosen_not_run"
         and qs.branch == {"cond": "false", "taken": False,
                           "path": "false"}
         and qs.last_control.get("status") == "skipped",
         str(_msgs(r)))

    r = _run(q, "62[Parallel]")
    ok_par = (_msgs(r) == ["Parallel n=2 offline_deterministic"]
              and qs.parallel == ["a", "b"])
    r = _run(q, "62[Parallel] :: x, y ,z")
    _rec("62 Parallel: bare Parallel defaults to "
         "['a', 'b']; a label is a comma list, "
         "stripped — and the mode is "
         "offline_deterministic (no threads)",
         ok_par and _msgs(r) == ["Parallel n=3 "
                                  "offline_deterministic"]
         and qs.parallel == ["x", "y", "z"], str(_msgs(r)))

    r = _run(q, "63[Sequence]")
    ok_seq = _msgs(r) == ["Sequence ordered"]
    r = _run(q, "63[Sequence] :: myorder")
    _rec("63 Sequence: bare announces 'Sequence "
         "ordered'; a label replaces the word",
         ok_seq and _msgs(r) == ["Sequence myorder"],
         str(_msgs(r)))

    r = _run(q, "65[While]")
    _rec("65 While: bare While (condition defaults "
         "true) with an empty body fails HONESTLY — "
         "ok=False bound_reached at the default "
         "bound 8",
         r.get("ok") is False
         and r.get("error") == "bound_reached"
         and qs.last_control.get("kind") == "while"
         and qs.last_control.get("status") == "bounded"
         and qs.last_control.get("iterations") == 8,
         str(_msgs(r)))
    r = _run(q, "65[While] :: false")
    ok_wf = (r.get("ok") is True
             and "While already false — zero iterations"
             in _msgs(r)
             and qs.last_control.get("status") == "zero")
    r = _run(q, "64[Until] :: true")
    _rec("65 While false / 64 Until true: an already-"
         "settled condition is zero iterations, ok=True, "
         "frame status 'zero'",
         ok_wf and r.get("ok") is True
         and "Until already true — zero iterations" in _msgs(r)
         and qs.last_control.get("status") == "zero",
         str(_msgs(r)))
    r = _run(q, "64[Until]")
    _rec("64 Until STEP 7 (B8): bare Until's two layers "
         "AGREE — the core arm prints 'Until "
         "cond=true already=True bound=8' and the "
         "chain layer prints 'Until already true — "
         "zero iterations', closing ok=True / "
         "status zero with an EMPTY condition",
         r.get("ok") is True
         and "Until cond=true already=True bound=8"
         in _msgs(r)
         and "Until already true — zero iterations"
         in _msgs(r)
         and qs.last_control.get("condition") == ""
         and qs.last_control.get("status") == "zero",
         str(_msgs(r)))
    _run(q, "72[Limit] :: 3")
    r = _run(q, "64[Until] :: false")
    _rec("64 Until: a condition that never holds "
         "fails bound_reached at the Limit (72) bound "
         "— 3 iterations under Limit 3, not the "
         "default 8",
         r.get("ok") is False
         and r.get("error") == "bound_reached"
         and qs.last_control.get("iterations") == 3
         and qs.last_control.get("status") == "bounded",
         str(_msgs(r)))
    _cleanup(owner_b)

    # -- 66 ForEach: empty-selection exhibit (fresh)
    owner_f = "D1RegCoreIIAF"
    f = _program(owner_f)
    fs = _st(f)
    r = _run(f, "66[ForEach]")
    _rec("66 ForEach STEP 7 (B9): on an empty selection "
         "BOTH surfaces agree — the core arm reports "
         "'ForEach n=0 op=identity empty_ok=True' "
         "(no plane-id fallback) and the chain layer "
         "reports 'ForEach empty selection valid', "
         "status empty, 0 iterations — the body "
         "never runs",
         r.get("ok") is True
         and "ForEach n=0 op=identity empty_ok=True"
         in _msgs(r)
         and "ForEach empty selection valid" in _msgs(r)
         and fs.last_control.get("status") == "empty"
         and fs.last_control.get("iterations") == 0,
         str(_msgs(r)))
    _cleanup(owner_f)

    # ---- chains (fresh owner) ----
    owner_c = "D1RegCoreIIAC"
    c = _program(owner_c)
    cs = _st(c)
    _run(c, "82[Group] :: FalseArm")
    r = _run(c, "60[true] > 80[TrueArm] > 59[Else] > "
                "53[FalseArm] > 61[Join]")
    _rec("60 Branch chain (true): only the taken arm "
         "runs (ran=[60, 80, 61]); the else arm and "
         "the 59 Else marker are skipped; context is "
         "the taken arm's and scope is untouched",
         r.get("chain_ran") == [60, 80, 61]
         and r.get("chain_skipped") == [53, 59]
         and cs.context == "TrueArm"
         and cs.scope == "plane", str(_msgs(r)))
    _rec("59 Route EXHIBIT (designed clash): in a "
         "Branch chain the 59 atom is the Else "
         "marker — it is skipped and never executes "
         "as Route (route stays 'primary')",
         59 in (r.get("chain_skipped") or [])
         and cs.route == "primary", str(_msgs(r)))
    _cleanup(owner_c)

    owner_c2 = "D1RegCoreIIAC2"
    c2 = _program(owner_c2)
    cs2 = _st(c2)
    _run(c2, "82[Group] :: FalseArm")
    r = _run(c2, "60[false] > 80[TrueArm] > 59[Else] > "
                 "53[FalseArm] > 61[Join]")
    _rec("60 Branch chain (false): the else arm runs "
         "(ran=[60, 53, 61]), the true arm is skipped "
         "and does NOT mutate (context stays empty) "
         "while scope becomes the else arm's group",
         r.get("chain_ran") == [60, 53, 61]
         and r.get("chain_skipped") == [80, 59]
         and cs2.context == ""
         and cs2.scope == "FalseArm", str(_msgs(r)))
    _cleanup(owner_c2)

    # -- Join exhibit via a Parallel chain with a failing sibling
    owner_j = "D1RegCoreIIAJ"
    j = _program(owner_j)
    js = _st(j)
    r = _run(j, "62[Parallel] > 91[false] > 80[TrueArm] > "
                "61[Join]")
    join_msg = [m for m in _msgs(r) if m.startswith("Join ")]
    _rec("61 Join STEP 7 (B7): the Join closing a Parallel "
         "block evaluates the block's ACTUAL results "
         "(incoming=2, fails=1, ok=False) — and the "
         "parallel frame status is 'fail', representing "
         "the captured sibling failure; the chain "
         "aggregate still reports assert_fail (the root "
         "cause, not join_fail) and the surviving "
         "sibling still ran",
         join_msg == ["Join policy=all ok=False incoming=2 "
                      "fails=1"]
         and r.get("ok") is False
         and r.get("error") == "assert_fail"
         and js.context == "TrueArm"
         and js.last_control.get("kind") == "parallel"
         and js.last_control.get("status") == "fail"
         and any(not x.get("ok", True)
                 for x in js.last_control.get("results", [])),
         str(_msgs(r)))
    r = _run(j, "61[Join]")
    ok_all = (r.get("ok") is False
              and r.get("error") == "join_fail"
              and _msgs(r) == ["Join policy=all ok=False "
                               "incoming=3 fails=1"])
    r = _run(j, "61[Join] :: any")
    _rec("61 Join: invoked AFTER the block, Join sees "
         "the real incoming results — policy all "
         "fails join_fail (incoming=3, fails=1) while "
         "policy any passes on the same results",
         ok_all and r.get("ok") is True
         and _msgs(r) == ["Join policy=any ok=True "
                          "incoming=3 fails=1"],
         str(_msgs(r)))
    _cleanup(owner_j)

    # -- Until / While mutation chains
    owner_l = "D1RegCoreIIAL"
    lp = _program(owner_l)
    ls = _st(lp)
    r = _run(lp, "64[store_done] > 55[done] > 61[Join]")
    _rec("symbiosis: Until's body is Set (55) — the "
         "body writes store[done], the Until "
         "condition (store_done) turns true, and the "
         "loop exits after exactly 1 iteration",
         r.get("ok") is True
         and r.get("chain_ran") == [64, 55, 61]
         and ls.store.get("done") == "1"
         and ls.last_control.get("iterations") == 1
         and ls.last_control.get("status") == "ok",
         str(_msgs(r)))
    _run(lp, "55[Set] :: go=1")
    _run(lp, "72[Limit] :: 8")
    r = _run(lp, "65[store_go] > 86[go] > 61[Join]")
    _rec("symbiosis: While's body is Delete (86) — "
         "deleting store[go] clears the While "
         "condition (store_go) and the loop exits "
         "after exactly 1 iteration with the key gone",
         r.get("ok") is True
         and r.get("chain_ran") == [65, 86, 61]
         and "go" not in ls.store
         and ls.last_control.get("iterations") == 1,
         str(_msgs(r)))
    _run(lp, "72[Limit] :: 3")
    r = _run(lp, "64[false] > 80[TrueArm] > 61[Join]")
    _rec("64 Until chain: a never-true condition runs "
         "the body exactly Limit times (3) and then "
         "fails bound_reached (status bounded)",
         r.get("ok") is False
         and r.get("error") == "bound_reached"
         and (r.get("chain_ran") or []).count(80) == 3
         and ls.last_control.get("iterations") == 3
         and ls.last_control.get("status") == "bounded",
         str(_msgs(r)))
    _cleanup(owner_l)

    # -- Sequence + ForEach chains
    owner_s = "D1RegCoreIIAS"
    s = _program(owner_s)
    ss = _st(s)
    r = _run(s, "63[Sequence] > 80[Alpha] > 80[Beta] > "
                "61[Join]")
    _rec("63 Sequence chain: the body runs in written "
         "order (results dells [80, 80, 61]) and the "
         "last writer wins the shared context (Beta)",
         r.get("chain_ran") == [63, 80, 80, 61]
         and [x.get("dell") for x in
              ss.last_control.get("results", [])] == [80, 80, 61]
         and ss.context == "Beta", str(_msgs(r)))
    _run(s, "08[Create] :: Garden Gate")
    _run(s, "08[Create] :: Stone Wall")
    _run(s, "51[Select]")
    r = _run(s, "66[ForEach] > 80[TrueArm] > 61[Join]")
    members = [x.get("member") for x in
               ss.last_control.get("results", [])
               if x.get("member")]
    _rec("symbiosis: ForEach (66) walks the selection "
         "Select (51) published, in order — one body "
         "run per member, each result carrying its "
         "member, and st.route is restored to "
         "'primary' afterwards",
         r.get("ok") is True
         and ss.last_control.get("iterations") == 3
         and members == ["welcome", "garden_gate",
                         "stone_wall"]
         and ss.route == "primary", str(_msgs(r)))
    _cleanup(owner_s)

    # -- REAL_USER_PATH: literal REPL seed lines
    owner2 = "D1RegCoreIIARepl"
    _cleanup(owner2)
    proc = subprocess.run(
        [sys.executable, "-m", "form.repl", "--owner", owner2],
        input="08[Create] :: Garden Gate\n51[Select]\n"
              "52[Filter] :: garden\n55[Set] :: mode=fast\n"
              "59[Route] :: alt\n",
        capture_output=True, text=True, cwd=_ROOT, timeout=120)
    out = proc.stdout or ""
    _rec("REPL: Filter, Set and Route execute on the "
         "literal user path",
         proc.returncode == 0
         and "Filter 2->1 cond=garden" in out
         and "Set mode=fast" in out
         and "Route -> alt" in out, out[-300:])
    _cleanup(owner2)

    # -- docs pins
    _rec("proof cards carry circuit-20 deep notes "
         "(52, 55, 59-66)",
         all(n in DEEP_NOTES and "circuit 20" in DEEP_NOTES[n]
             for n in (52, 55, 59, 60, 61, 62, 63, 64, 65, 66)),
         str([n for n in (52, 55, 59, 60, 61, 62, 63, 64, 65, 66)
              if n not in DEEP_NOTES]))

    total = len(RESULTS)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        if not ok:
            print(f"FAIL {name} :: {detail}")
    print(f"D1_REGISTRY_COREII_A: {passed}/{total}")
    return passed == total


def smoke():
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
