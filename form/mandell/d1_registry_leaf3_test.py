"""D1 circuit 18 (registry pass, cluster 3) — leaf Dells
21-36 DEEP CONTRACTS.

The third cluster of the full-registry pass: the leaf
executor's next sixteen Dells (executor_leaf arms 21-36,
front-door intercepts for 21/22 via live_identity and
27/28/34/35 via core_i_ops). None of the sixteen is
typed. Contracts proven here, per Dell, through the
public seed path:

- 21 Merge (live_identity authority): sources resolve
  from the label's tokens (id, then exact label, then
  case-insensitive label; joiners and/or/to/from/with/
  into/plus skipped); an ambiguous token fails
  ambiguous_source; exactly one resolved source fails
  missing_source; zero sources on a <2-unit plane fails
  missing_source. The child is merge_<p1>_<p2> (repeat
  merges dedup to _2), label = the raw label or
  "<P1> + <P2>", words "merge <p1> <p2>", parents
  recorded, origin merge, and the parents are NOT
  mutated or destroyed. PINNED EXHIBIT: with zero
  resolved sources and >=2 units, Merge silently falls
  back to the LAST TWO units — a bare Merge merges
  them instead of requiring named sources.
- 22 Split (live_identity authority): the first
  resolved source splits into <src>_a / <src>_b
  ("<label> A/B", words "split <src>", parents
  [source], origin split); the parent is preserved;
  an ambiguous label fails ambiguous_source. PINNED
  EXHIBIT: with no resolved source, Split silently
  falls back to the LAST unit — a bare Split, and
  even a misspelled label, split whatever came last
  instead of failing.
- 23 Lock: the sandbox switch — sandbox_on applies
  the sandbox to every live unit (sandboxed=True),
  "Sandbox ON." (the registry name is Lock; the
  mechanism is the sandbox, not a per-unit freeze).
- 24 Unlock: sandbox_off releases every unit
  (sandboxed=False), "Sandbox OFF."
- 25 Pulse: bare Pulse pulses the enhance engine —
  with enhance OFF the scores are untouched; the
  label "on" / "enhance_on" turns enhance ON instead
  ("Enhance ON.").
- 26 Temp: cold/cool turn enhance OFF (only turning
  it off if it was on), hot/heat turn it ON and pulse
  (a pulse scores every live unit), anything else —
  including bare — is warm (enhance ON); the resolved
  label is noted to history.
- 27 Checkpoint (core_i_ops): writes a committed
  generation via Checkpoint Generation V1 and returns
  its id; last_core_i records {dell 27, generation_id,
  ok}.
- 28 Rollback (core_i_ops, authority-mediated): a
  bare Dell-28 seed is DENIED with zero mutation —
  acceptance_policy_denied once a checkpoint exists,
  rollback_target_invalid on a plane with no committed
  generation. The mediated path (freeze target + grant
  + Program.confirm_rollback) restores the checkpointed
  plane: units created after the checkpoint are gone
  from the restored program.
- 29 Compress: place_idea("compress_" + distilled,
  SEED) where distilled = distill_label(label) —
  tokens >2 chars, lowercased, deduped, max 4, joined
  "_" (empty -> "distill"); "Compressed → <distilled>".
- 30 Expand: the source is the label, or (bare) the
  LAST unit's "<label> <words>"; the expansion is the
  source with "_" -> " " split/rejoined; a unit
  expand_<expansion underscored, truncated to 24
  chars> is minted CUBE; "Expanded → <expansion>".
- 31 Simulate: a dry-run status read (owner, ideas,
  history_len from the pre-run status) — units,
  scores and sandbox are unchanged by the run.
- 32 Pause: bare Pause idles the avatar ("Paused.");
  a label containing "enhance" turns enhance OFF
  instead ("Enhance OFF.", avatar untouched).
- 33 Resume: walks the avatar; if enhance was OFF it
  is turned ON ("Resumed walk + enhance ON."),
  otherwise "Resumed walk."; noted to history.
- 34 Stamp (core_i_ops): last_stamp = {mark, UTC ts}
  with the label as mark (bare = "stamp"); the
  message is "Stamp: <mark> @ <ts>"; last_core_i
  records the stamp.
- 35 Discover (core_i_ops): the default read returns
  the avatar line plus "ideas=<n> nursery=<pending>"
  and records last_discover {ids in plane order,
  count, nursery}; named reads: count_nursery
  (nursery summary), list_pending, compare_nursery,
  trace (history), find_idea <q> (plane substring
  search) — each records a sourced last_discover.
- 36 Inject: place_idea(label, SEED) with the RAW
  label (bare = "inject"); "Injected into scope:
  <name>"; the name is noted to history.

Cluster symbiosis: Merge's (21) child is found by
Discover (35, find_idea) and split by Split (22);
Loop's (13) proposals are counted by Discover's
count_nursery; Inject's (36) unit minted before a
Checkpoint (27) survives the mediated Rollback (28)
while a post-checkpoint unit does not. One
literal-REPL leg (23 + 34) for REAL_USER_PATH
evidence.

House pattern: RESULTS + _rec; loud cleanup (the
checkpoint owner's generation files are removed by
owner-wide glob)."""
import os
import re
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
    # Owner-wide: checkpoint generations scatter files
    # (program_/nursery_/ideas_/graph_/gen_/current_
    # with hash infixes); the test owners are unique to
    # this suite, so the wide glob is exact in effect.
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
            if not m.startswith(("Mandell:", "English:"))]


def _units(prog):
    return prog.cube.session.plane.units


def main():
    owner = "D1RegLeaf3"
    p = _program(owner)

    # -- 21 Merge: bare on a 1-unit plane fails
    r = _run(p, "21[Merge]")
    _rec("21 Merge: bare Merge on a one-unit plane fails "
         "missing_source, zero mutation",
         r.get("ok") is False and r.get("error") == "missing_source"
         and _msgs(r) == ["Merge failed: missing_source"]
         and list(_units(p)) == ["welcome"], str(_msgs(r)))

    _run(p, "08[Create] :: Garden Gate")
    _run(p, "08[Create] :: Stone")

    # -- 21 Merge: one named source is not enough
    before = list(_units(p))
    r = _run(p, "21[Merge] :: garden_gate")
    _rec("21 Merge: a single resolved source fails "
         "missing_source (no fallback when one source "
         "WAS named), zero mutation",
         r.get("ok") is False and r.get("error") == "missing_source"
         and list(_units(p)) == before, str(_msgs(r)))

    # -- 21 Merge: two named sources (ids, '+' joiner)
    gg = _units(p)["garden_gate"]
    snap = (gg.label, gg.words, list(gg.parents))
    r = _run(p, "21[Merge] :: garden_gate + stone")
    child = _units(p).get("merge_garden_gate_stone")
    _rec("21 Merge: two sources mint merge_<p1>_<p2> with "
         "the raw label, words 'merge <p1> <p2>', parents "
         "and origin recorded; parents unmutated, surviving",
         _msgs(r) == ["Merged → merge_garden_gate_stone "
                      "parents=['garden_gate', 'stone']"]
         and child is not None
         and child.label == "garden_gate + stone"
         and child.words == "merge garden_gate stone"
         and list(child.parents) == ["garden_gate", "stone"]
         and getattr(child, "origin", "") == "merge"
         and (gg.label, gg.words, list(gg.parents)) == snap
         and "garden_gate" in _units(p) and "stone" in _units(p),
         str(_msgs(r)))
    r = _run(p, "21[Merge] :: garden_gate + stone")
    _rec("21 Merge: repeating the same merge dedups the "
         "child id to _2 (suffix_start=2 convention)",
         _msgs(r) == ["Merged → merge_garden_gate_stone_2 "
                      "parents=['garden_gate', 'stone']"]
         and "merge_garden_gate_stone_2" in _units(p),
         str(_msgs(r)))

    # -- 22 Split: named source
    r = _run(p, "22[Split] :: garden_gate")
    a = _units(p).get("garden_gate_a")
    b = _units(p).get("garden_gate_b")
    _rec("22 Split: a named source splits into <src>_a/_b "
         "('<label> A/B', words 'split <src>', parents "
         "[source], origin split); the parent survives",
         _msgs(r) == ["Split → garden_gate_a + garden_gate_b"]
         and a is not None and b is not None
         and a.label == "Garden Gate A"
         and b.label == "Garden Gate B"
         and a.words == "split garden_gate"
         and list(a.parents) == ["garden_gate"]
         and getattr(a, "origin", "") == "split"
         and "garden_gate" in _units(p), str(_msgs(r)))

    # -- 23 Lock / 24 Unlock: the sandbox switch
    r = _run(p, "23[Lock]")
    _rec("23 Lock: sandbox ON and every live unit is "
         "sandboxed (Lock's mechanism is the sandbox)",
         _msgs(r) == ["Sandbox ON."] and p.sandbox.on is True
         and all(getattr(u, "sandboxed", False)
                 for u in _units(p).values()), str(_msgs(r)))
    r = _run(p, "24[Unlock]")
    _rec("24 Unlock: sandbox OFF and every live unit is "
         "released",
         _msgs(r) == ["Sandbox OFF."] and p.sandbox.on is False
         and not any(getattr(u, "sandboxed", False)
                     for u in _units(p).values()), str(_msgs(r)))

    # -- 25 Pulse: gated bare pulse; 'on' arms enhance
    p.enhance.state.scores.clear()
    p.enhance.state.scores["garden_gate"] = 1.0
    r = _run(p, "25[Pulse]")
    _rec("25 Pulse: bare Pulse with enhance OFF leaves "
         "the scores exactly unchanged",
         _msgs(r) == ["Pulse sent."]
         and p.enhance.on is False
         and p.scores() == {"garden_gate": 1.0}, str(_msgs(r)))
    r = _run(p, "25[Pulse] :: on")
    r2 = _run(p, "25[Pulse] :: enhance_on")
    _rec("25 Pulse: the labels 'on' and 'enhance_on' turn "
         "enhance ON instead of pulsing",
         _msgs(r) == ["Enhance ON."] and _msgs(r2) == ["Enhance ON."]
         and p.enhance.on is True, str(_msgs(r)))

    # -- 26 Temp: cold/cool, hot/heat, warm default
    r = _run(p, "26[Temp] :: cold")
    _rec("26 Temp cold: enhance ON -> OFF",
         _msgs(r) == ["Temp → cold (enhance OFF)"]
         and p.enhance.on is False, str(_msgs(r)))
    _run(p, "26[Temp] :: warm")
    r = _run(p, "26[Temp] :: cool")
    _rec("26 Temp cool: the cold alias also turns "
         "enhance OFF",
         _msgs(r) == ["Temp → cold (enhance OFF)"]
         and p.enhance.on is False, str(_msgs(r)))
    p.enhance.state.scores.clear()
    r = _run(p, "26[Temp] :: hot")
    sc = p.scores()
    _rec("26 Temp hot: enhance ON + pulse — every live "
         "unit carries a positive score afterwards",
         _msgs(r) == ["Temp → hot (enhance ON + pulse)"]
         and p.enhance.on is True
         and set(sc) == set(_units(p))
         and all(v > 0 for v in sc.values()), str(sc))
    _run(p, "26[Temp] :: cold")
    r = _run(p, "26[Temp] :: heat")
    ok_heat = _msgs(r) == ["Temp → hot (enhance ON + pulse)"] \
        and p.enhance.on is True
    _run(p, "26[Temp] :: cold")
    r = _run(p, "26[Temp]")
    _rec("26 Temp: 'heat' is the hot alias; bare Temp is "
         "warm (enhance ON) and the resolved label is "
         "noted to history",
         ok_heat and _msgs(r) == ["Temp → warm (enhance ON)"]
         and p.enhance.on is True
         and "26[Temp] :: warm" in list(p.history),
         str(_msgs(r)))

    # -- 29 Compress: distill rules
    r = _run(p, "29[Compress] :: Garden Gate")
    cu = _units(p).get("compress_garden_gate")
    _rec("29 Compress: mints compress_<distilled> as "
         "SEED ('compress garden gate'); the source "
         "unit is untouched",
         _msgs(r) == ['Created idea: "compress_garden_gate"',
                      "Compressed → garden_gate"]
         and cu is not None and cu.label == "compress garden gate"
         and str(cu.skin) == "Skin.SEED"
         and "garden_gate" in _units(p), str(_msgs(r)))
    r = _run(p, "29[Compress] :: alpha alpha beta gamma delta epsilon")
    _rec("29 Compress: distill lowercases, dedups and "
         "caps at 4 tokens (>2 chars) — alpha_beta_gamma_delta",
         _msgs(r)[-1] == "Compressed → alpha_beta_gamma_delta"
         and "compress_alpha_beta_gamma_delta" in _units(p),
         str(_msgs(r)))
    r = _run(p, "29[Compress]")
    _rec("29 Compress: bare Compress distills the empty "
         "label to 'distill'",
         _msgs(r)[-1] == "Compressed → distill"
         and "compress_distill" in _units(p), str(_msgs(r)))

    # -- 30 Expand: labeled + 24-char slug truncation
    r = _run(p, "30[Expand] :: hello wide world")
    eu = _units(p).get("expand_hello_wide_world")
    _rec("30 Expand: mints expand_<expansion> as CUBE "
         "from the label",
         _msgs(r) == ['Created idea: "expand_hello_wide_world"',
                      "Expanded → hello wide world"]
         and eu is not None and str(eu.skin) == "Skin.CUBE",
         str(_msgs(r)))
    r = _run(p, "30[Expand] :: one two three four five six seven eight nine ten")
    _rec("30 Expand: the minted id truncates the "
         "underscored expansion to 24 chars while the "
         "message keeps the full expansion",
         _msgs(r)[-1] == "Expanded → one two three four five "
                         "six seven eight nine ten"
         and "expand_one_two_three_four_five" in _units(p),
         str(_msgs(r)))

    # -- 31 Simulate: dry-run read, no state change
    st = p.status()
    snap_units = list(_units(p))
    snap_scores = p.scores()
    r = _run(p, "31[Simulate]")
    _rec("31 Simulate: reports the pre-run status "
         "(owner/ideas/history_len) and mutates nothing "
         "— units, scores, sandbox unchanged",
         _msgs(r) == ["Simulate (dry-run — no mutation):",
                      f"  owner={st.get('owner')} "
                      f"ideas={st.get('ideas')}",
                      f"  history_len={st.get('history_len')}"]
         and list(_units(p)) == snap_units
         and p.scores() == snap_scores
         and p.sandbox.on is False, str(_msgs(r)))

    # -- 32 Pause / 33 Resume
    _run(p, "33[Resume]")  # walking, enhance ON
    r = _run(p, "32[Pause]")
    _rec("32 Pause: bare Pause idles the avatar",
         _msgs(r) == ["Paused."]
         and p.avatar_status()["locomotion"] == "idle",
         str(_msgs(r)))
    _run(p, "33[Resume]")
    r = _run(p, "32[Pause] :: enhance")
    _rec("32 Pause: a label containing 'enhance' turns "
         "enhance OFF instead — the avatar keeps walking",
         _msgs(r) == ["Enhance OFF."] and p.enhance.on is False
         and p.avatar_status()["locomotion"] == "walk",
         str(_msgs(r)))
    r = _run(p, "33[Resume]")
    _rec("33 Resume: with enhance OFF, Resume walks AND "
         "turns enhance ON; the seed is noted",
         _msgs(r) == ["Resumed walk + enhance ON."]
         and p.avatar_status()["locomotion"] == "walk"
         and p.enhance.on is True
         and "33[Resume]" in list(p.history), str(_msgs(r)))
    r = _run(p, "33[Resume]")
    _rec("33 Resume: with enhance already ON, Resume "
         "only walks",
         _msgs(r) == ["Resumed walk."]
         and p.avatar_status()["locomotion"] == "walk",
         str(_msgs(r)))

    # -- 34 Stamp: machine-readable mark + UTC ts
    r = _run(p, "34[Stamp] :: gate")
    ts = getattr(p, "last_stamp", {}).get("ts", "")
    _rec("34 Stamp: last_stamp records the label as the "
         "mark with a UTC ISO timestamp; the message "
         "echoes both; last_core_i records dell 34",
         _msgs(r) == [f"Stamp: gate @ {ts}"]
         and p.last_stamp.get("mark") == "gate"
         and re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z",
                          ts or "") is not None
         and p.last_core_i.get("dell") == 34
         and p.last_core_i.get("ok") is True, str(_msgs(r)))
    r = _run(p, "34[Stamp]")
    _rec("34 Stamp: bare Stamp defaults the mark to "
         "'stamp'",
         p.last_stamp.get("mark") == "stamp"
         and _msgs(r)[0].startswith("Stamp: stamp @ "),
         str(_msgs(r)))

    # -- 36 Inject: raw label, SEED skin
    r = _run(p, "36[Inject] :: Secret Sauce")
    iu = _units(p).get("secret_sauce")
    _rec("36 Inject: mints the raw label as SEED and "
         "announces the scope injection; the name is noted",
         _msgs(r) == ['Created idea: "Secret Sauce"',
                      "Injected into scope: Secret Sauce"]
         and iu is not None and iu.label == "Secret Sauce"
         and str(iu.skin) == "Skin.SEED"
         and "36[Inject] :: Secret Sauce" in list(p.history),
         str(_msgs(r)))
    r = _run(p, "36[Inject]")
    _rec("36 Inject: bare Inject mints 'inject'",
         _msgs(r)[-1] == "Injected into scope: inject"
         and "inject" in _units(p), str(_msgs(r)))

    # -- 35 Discover: default + nursery reads (Loop-fed)
    _run(p, "13[Loop]")
    ns = p.nursery.summary()
    r = _run(p, "35[Discover]")
    ld = getattr(p, "last_discover", {})
    av = p.avatar_status()
    _rec("35 Discover: the default read returns the "
         "avatar line + ideas/nursery counts and records "
         "last_discover with the plane ids in order",
         _msgs(r) == [f"{av['look']}  {av['describe']}",
                      f"ideas={len(_units(p))} "
                      f"nursery={ns.get('pending', 0)}"]
         and ld.get("ids") == list(_units(p))
         and ld.get("count") == len(_units(p))
         and ld.get("nursery") == ns.get("pending", 0),
         str(_msgs(r)))
    r = _run(p, "35[Discover] :: count_nursery")
    ld = getattr(p, "last_discover", {})
    _rec("35 Discover count_nursery: the nursery summary "
         "is read back exactly (Loop's proposals included)",
         _msgs(r) == [f"Nursery: pending={ns.get('pending',0)} "
                      f"total={ns.get('total',0)} "
                      f"confirmed={ns.get('confirmed',0)} "
                      f"rejected={ns.get('rejected',0)}"]
         and ld.get("source") == "nursery_summary"
         and ld.get("pending") == ns.get("pending", 0)
         and ld.get("pending", 0) > 0, str(_msgs(r)))
    r = _run(p, "35[Discover] :: list_pending")
    ld = getattr(p, "last_discover", {})
    _rec("35 Discover list_pending: one line per pending "
         "proposal; count agrees with the summary",
         _msgs(r)[0] == f"Pending proposals: {ns.get('pending',0)}"
         and ld.get("source") == "nursery_pending"
         and ld.get("count") == ns.get("pending", 0)
         and len(ld.get("ids", [])) == ns.get("pending", 0),
         str(_msgs(r)))
    r = _run(p, "35[Discover] :: find_idea merge")
    ld = getattr(p, "last_discover", {})
    match_ids = [m["id"] for m in ld.get("matches", [])]
    _rec("symbiosis: Discover find_idea locates Merge's "
         "(21) children by substring over the plane",
         ld.get("source") == "cube_idea_search"
         and "merge_garden_gate_stone" in match_ids
         and "merge_garden_gate_stone_2" in match_ids
         and ld.get("count") == len(match_ids), str(match_ids))
    hist_n = len(list(p.history))
    r = _run(p, "35[Discover] :: trace")
    ld = getattr(p, "last_discover", {})
    _rec("35 Discover trace: the history read-back "
         "counts every noted operation",
         _msgs(r)[0] == f"Trace: {hist_n} operations"
         and ld.get("source") == "trace"
         and ld.get("count") == hist_n, str(_msgs(r)))

    # -- symbiosis: Split divides Merge's child
    r = _run(p, "22[Split] :: merge_garden_gate_stone")
    _rec("symbiosis: Split (22) splits Merge's (21) child; "
         "the grandchildren carry the merge child as parent",
         _msgs(r) == ["Split → merge_garden_gate_stone_a + "
                      "merge_garden_gate_stone_b"]
         and list(_units(p)["merge_garden_gate_stone_a"].parents)
         == ["merge_garden_gate_stone"], str(_msgs(r)))
    _cleanup(owner)

    # -- 21 Merge EXHIBIT: bare Merge falls back to the
    #    last two units (dedicated owner)
    owner_m = "D1RegLeaf3Merge"
    q = _program(owner_m)
    _run(q, "08[Create] :: A One")
    _run(q, "08[Create] :: B Two")
    r = _run(q, "21[Merge]")
    mc = _units(q).get("merge_a_one_b_two")
    _rec("21 Merge EXHIBIT: bare Merge with >=2 units "
         "silently merges the LAST TWO units (fallback "
         "sources) instead of requiring named sources — "
         "the child label is '<P1> + <P2>'",
         _msgs(r) == ["Merged → merge_a_one_b_two "
                      "parents=['a_one', 'b_two']"]
         and mc is not None and mc.label == "A One + B Two",
         str(_msgs(r)))
    _run(q, "08[Create] :: Twin")
    _run(q, "08[Create] :: Twin")
    before = list(_units(q))
    r = _run(q, "21[Merge] :: Twin + a_one")
    r2 = _run(q, "22[Split] :: Twin")
    _rec("21/22: a label matching two units (duplicate "
         "labels) fails ambiguous_source for BOTH Merge "
         "and Split, zero mutation",
         r.get("ok") is False
         and r.get("error") == "ambiguous_source"
         and r2.get("ok") is False
         and r2.get("error") == "ambiguous_source"
         and list(_units(q)) == before,
         f"{r.get('error')} / {r2.get('error')}")
    _cleanup(owner_m)

    # -- 22 Split EXHIBIT: unknown/bare labels fall back
    #    to the last unit (dedicated owner)
    owner_s = "D1RegLeaf3Split"
    q = _program(owner_s)
    _run(q, "08[Create] :: Solo")
    r = _run(q, "22[Split] :: nosuchthing")
    _rec("22 Split EXHIBIT: an unknown label silently "
         "splits the LAST unit instead of failing",
         _msgs(r) == ["Split → solo_a + solo_b"]
         and "solo_a" in _units(q) and "solo_b" in _units(q),
         str(_msgs(r)))
    r = _run(q, "22[Split]")
    _rec("22 Split EXHIBIT: bare Split splits the last "
         "unit too (now solo_b, the newest unit)",
         _msgs(r) == ["Split → solo_b_a + solo_b_b"]
         and "solo_b_a" in _units(q), str(_msgs(r)))
    _cleanup(owner_s)

    # -- 30 Expand: bare Expand reads the last unit
    owner_e = "D1RegLeaf3Expand"
    q = _program(owner_e)
    _run(q, "08[Create] :: Garden Gate")
    r = _run(q, "30[Expand]")
    _rec("30 Expand: bare Expand's source is the last "
         "unit's '<label> <words>' — a Create unit (label "
         "== words) expands to the doubled phrase",
         _msgs(r)[-1] == "Expanded → Garden Gate Garden Gate"
         and "expand_garden_gate_garden_gate" in _units(q),
         str(_msgs(r)))
    _cleanup(owner_e)

    # -- 27 Checkpoint / 28 Rollback (dedicated owner)
    owner_c = "D1RegLeaf3Cp"
    q = _program(owner_c)
    _run(q, "08[Create] :: Keep Me")
    _run(q, "36[Inject] :: Checkpoint Seed")
    r = _run(q, "27[Checkpoint]")
    gen = r.get("generation_id") or ""
    _rec("27 Checkpoint: writes a committed generation "
         "and returns its id; last_core_i records it",
         r.get("ok") is True and bool(gen)
         and _msgs(r) == [f"Checkpoint written: generation {gen}"]
         and q.last_core_i.get("generation_id") == gen
         and q.last_core_i.get("ok") is True, str(_msgs(r)))
    _run(q, "08[Create] :: Later One")
    before = list(_units(q))
    r = _run(q, "28[Rollback]")
    _rec("28 Rollback: a bare Dell-28 seed is DENIED "
         "(acceptance_policy_denied — no bound approval) "
         "with zero mutation; last_core_i records the denial",
         r.get("ok") is False
         and r.get("error") == "acceptance_policy_denied"
         and _msgs(r)[0].startswith(
             "Rollback denied (acceptance_policy_denied):")
         and list(_units(q)) == before
         and q.last_core_i.get("ok") is False, str(_msgs(r)))
    from form.dell_matrix import rollback_authority as _ra
    frozen = _ra.freeze_rollback_target(q.owner, None)
    grant = _ra.issue_rollback_grant(
        q, issuer="root", subject="test", frozen_target=frozen)
    res = q.confirm_rollback(
        None, _review_context={"grant_id": grant["grant_id"]},
        _subject="test")
    restored = None
    if res.get("ok"):
        from form import persist_rest as _pr
        restored = _pr.load(q.owner, activate=False)
    _rec("symbiosis: the mediated rollback (freeze + "
         "grant + confirm_rollback) restores the "
         "checkpointed plane — Inject's (36) pre-checkpoint "
         "unit survives, the post-checkpoint unit is gone",
         res.get("ok") is True and restored is not None
         and "keep_me" in restored.cube.session.plane.units
         and "checkpoint_seed" in restored.cube.session.plane.units
         and "later_one" not in restored.cube.session.plane.units,
         str(res)[:200])
    _cleanup(owner_c)

    # -- 28 Rollback: no checkpoint at all
    owner_f = "D1RegLeaf3Fresh"
    q = _program(owner_f)
    r = _run(q, "28[Rollback]")
    _rec("28 Rollback: with no committed generation the "
         "denial reason is rollback_target_invalid",
         r.get("ok") is False
         and r.get("error") == "rollback_target_invalid"
         and _msgs(r)[0].startswith(
             "Rollback denied (rollback_target_invalid):"),
         str(_msgs(r)))
    _cleanup(owner_f)

    # -- REAL_USER_PATH: literal REPL seed lines
    owner2 = "D1RegLeaf3Repl"
    _cleanup(owner2)
    proc = subprocess.run(
        [sys.executable, "-m", "form.repl", "--owner", owner2],
        input="23[Lock]\n34[Stamp] :: gate\n",
        capture_output=True, text=True, cwd=_ROOT, timeout=120)
    out = proc.stdout or ""
    _rec("REPL: Lock and Stamp execute on the literal "
         "user path",
         proc.returncode == 0 and "Sandbox ON." in out
         and "Stamp: gate @ " in out, out[-300:])
    _cleanup(owner2)

    # -- docs pins
    _rec("proof cards carry circuit-18 deep notes (21-36)",
         all(n in DEEP_NOTES and "circuit 18" in DEEP_NOTES[n]
             for n in range(21, 37)),
         str([n for n in range(21, 37) if n not in DEEP_NOTES]))

    total = len(RESULTS)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        if not ok:
            print(f"FAIL {name} :: {detail}")
    print(f"D1_REGISTRY_LEAF3: {passed}/{total}")
    return passed == total


def smoke():
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
