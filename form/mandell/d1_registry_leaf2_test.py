"""D1 circuit 17 (registry pass, cluster 2) — leaf Dells
09-20 DEEP CONTRACTS.

The second cluster of the full-registry pass: the leaf
executor's next twelve Dells (executor_leaf.py arms
9-20). None of the twelve is typed (08 Create, the one
typed Dell in 00-20, was circuit 15). Contracts proven
here, per Dell, through the public seed path:

- 09 Show: dispatch on the label — bare Show is the
  literal render token "__RENDER__"; "avatar" returns
  exactly Persona's read ("<look>  <describe>");
  "lattice" returns the lattice's ASCII render;
  "visual" reports "Visual ready." plus the UI path.
- 10 Keep: saves the session — "Session saved.",
  "ideas=<plane census> nursery=<pending>", and
  "file=<program_<owner>.json>" (the file exists);
  Program.load restores the saved plane.
- 11 Architect: a schema read — owner, idea census,
  lattice size/form, cell count — plus a history note.
- 12 Test: five live checks (floor, lattice, growth,
  nursery, ideas) all PASS on a healthy program:
  "Test: 5/5", noted to history as "5/5".
- 13 Loop: ringed growth with cycles = the digit
  label else 1, and NO upper clamp (label 7 runs 7
  cycles — the deliberate contrast with Dell 06 Cycle,
  which clamps to 1..5); growth PROPOSES only (live
  census unchanged, nursery pending grows).
- 14 Bind: mints a plane unit through place_idea with
  the RAW label (no prefix, unlike 07 Link): bare Bind
  mints "bind"; repeats dedup.
- 15 Map: a label in {cube, sphere, core, flower}
  sets the lattice form; any other label mints a unit
  via place_idea (form unchanged); bare Map reports
  "Mapped units=<census>".
- 16 Decay: factor = the numeric label clamped to
  0.1..1.0 (default 0.9 for bare/non-numeric); with
  enhance ON the resonance scores are multiplied by
  the factor; note_seed records the resolved factor.
  PINNED EXHIBIT: with enhance OFF the gate refuses
  the decay (scores unchanged) but the leaf message
  still claims "Scores decayed" — the message
  overclaims the effect (see packet).
- 17 Shadow: message-only parallel track — the id is
  "shadow_" + the label (spaces -> '_', case kept,
  truncated to 20 chars; bare = "shadow_bg"); the
  live census is unchanged; the id is noted.
- 18 Mirror: a read of the live plane — header
  "Mirror: <N> live ideas" and one bullet per unit
  ("<uid>: <label> [<skin>]"), CAPPED at 16 bullets
  while the header keeps the true total.
- 19 Drive: locomotion + step — bare/walk steps 1
  ("Walked to <pos>."), "run" steps 2 ("Ran to
  <pos>."), "stop" sets idle in place ("Stopped.").
- 20 Alpha: the close read — idea census, the CURRENT
  lattice form, and the save tip; the label (or
  "close") is noted to history.

Cluster symbiosis: Bind's (14) unit is listed by
Mirror (18) and survives Keep (10) + load; Map's (15)
form change is read back by Architect (11) and Alpha
(20); Drive's (19) new position is read by Show (09,
avatar branch); Loop's (13) proposals are counted by
Keep's (10) nursery line. One literal-REPL leg
(19 + 20) for REAL_USER_PATH evidence.

House pattern: RESULTS + _rec; loud cleanup."""
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
    pats = [f"program_{owner}.json", f"nursery_{owner}.json",
            f"checkpoint_{owner}.json",
            f"confirm_journal_{owner}.json",
            f"confirm_gen_{owner}.json",
            f"confirm_current_{owner}.json"]
    for pat in pats:
        for f in glob.glob(os.path.join(state, pat)):
            try:
                os.remove(f)
            except FileNotFoundError:
                pass
            except OSError as e:
                raise RuntimeError(f"cleanup failed for {f}: {e}")
    d = os.path.join(state, f"ideas_{owner}")
    if os.path.isdir(d):
        shutil.rmtree(d)


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
    owner = "D1RegLeaf2"
    p = _program(owner)
    _run(p, "08[Create] :: Garden Gate")
    _run(p, "08[Create] :: Stone")

    # -- 09 Show: four-way dispatch
    r = _run(p, "09[Show]")
    _rec("09 Show: bare Show returns the literal render token",
         _msgs(r) == ["__RENDER__"], str(_msgs(r)))
    st = p.avatar_status()
    r = _run(p, "09[Show] :: avatar")
    _rec("09 Show avatar: exactly '<look>  <describe>' of "
         "live status",
         _msgs(r) == [f"{st['look']}  {st['describe']}"],
         str(_msgs(r)))
    r = _run(p, "09[Show] :: lattice")
    m = _msgs(r)
    _rec("09 Show lattice: the ASCII render, headed by the "
         "lattice summary (size + form)",
         len(m) == 1 and m[0].startswith("HarmonicLattice size=")
         and "form=cube" in m[0], str(m)[:120])
    r = _run(p, "09[Show] :: visual")
    m = _msgs(r)
    _rec("09 Show visual: 'Visual ready.' + the UI html path",
         m[0] == "Visual ready."
         and m[1].endswith("DellMatrix_UI.html"), str(m))

    # -- 14 Bind: raw-label place_idea, no prefix
    r = _run(p, "14[Bind] :: River Song")
    u = _units(p).get("river_song")
    _rec("14 Bind: unit river_song minted with the raw label "
         "(no prefix; label/words raw, CUBE)",
         u is not None and u.label == "River Song"
         and u.words == "River Song"
         and str(u.skin) == "Skin.CUBE"
         and 'Created idea: "River Song"' in str(r.get("messages")),
         f"{u.label}|{u.words}" if u else "missing")
    _run(p, "14[Bind] :: River Song")
    _run(p, "14[Bind]")
    _rec("14 Bind: repeat dedups to _1; bare Bind mints 'bind'",
         "river_song_1" in _units(p) and "bind" in _units(p),
         str(sorted(_units(p))))

    # -- 18 Mirror: header + bullets over the live plane
    n_units = len(_units(p))
    r = _run(p, "18[Mirror]")
    m = _msgs(r)
    _rec("18 Mirror: header counts the live plane; one bullet "
         "per unit '<uid>: <label> [<skin>]'",
         m[0] == f"Mirror: {n_units} live ideas"
         and "  · river_song: River Song [cube]" in m
         and "  · welcome: Welcome [words]" in m
         and len(m) == 1 + n_units, str(m))

    # -- 11 Architect: schema read of live state
    r = _run(p, "11[Architect]")
    _rec("11 Architect: owner / census / lattice size+form / "
         "cells lines agree with live state",
         _msgs(r) == ["Architect schema:",
                      f"  owner={owner}",
                      f"  ideas={len(_units(p))}",
                      f"  lattice size={p.lattice.size} "
                      f"form={p.lattice.perception.form.value}",
                      f"  cells={len(p.lattice.cells)}"]
         and "11[Architect]" in list(p.history),
         str(_msgs(r)))

    # -- 15 Map: form names set the form; other labels mint
    r = _run(p, "15[Map]")
    _rec("15 Map: bare Map reports the unit census",
         _msgs(r) == [f"Mapped units={len(_units(p))}"],
         str(_msgs(r)))
    r = _run(p, "15[Map] :: sphere")
    _rec("15 Map sphere: lattice form becomes sphere",
         _msgs(r) == ["Form → sphere"]
         and p.lattice.perception.form.value == "sphere",
         str(_msgs(r)))
    # symbiosis: Alpha (20) and Architect (11) read Map's form
    r = _run(p, "20[Alpha]")
    _rec("symbiosis: Alpha (20) reports the form Map (15) set",
         "  form=sphere" in _msgs(r), str(_msgs(r)))
    _run(p, "15[Map] :: flower")
    _run(p, "15[Map] :: core")
    r = _run(p, "15[Map] :: cube")
    _rec("15 Map: flower and core are form names too; cube "
         "restores",
         _msgs(r) == ["Form → cube"]
         and p.lattice.perception.form.value == "cube",
         str(_msgs(r)))
    before_form = p.lattice.perception.form.value
    r = _run(p, "15[Map] :: New Place")
    _rec("15 Map: a non-form label mints a unit, form unchanged",
         "new_place" in _units(p)
         and p.lattice.perception.form.value == before_form
         and 'Created idea: "New Place"' in str(r.get("messages")),
         str(_msgs(r)))

    # -- 12 Test: the five live checks
    r = _run(p, "12[Test]")
    m = _msgs(r)
    _rec("12 Test: floor/lattice/growth/nursery/ideas all PASS, "
         "summary 'Test: 5/5', noted to history",
         m == ["  PASS  floor", "  PASS  lattice",
               "  PASS  growth", "  PASS  nursery",
               "  PASS  ideas", "Test: 5/5"]
         and "12[Test] :: 5/5" in list(p.history), str(m))

    # -- 19 Drive: walk / run / stop, then Show reads it back
    r = _run(p, "19[Drive]")
    _rec("19 Drive: bare Drive walks one step (0,0) -> (0,1)",
         _msgs(r) == ["Walked to (0, 1)."]
         and p.avatar_status()["pos"] == [0, 1]
         and p.avatar_status()["locomotion"] == "walk",
         str(_msgs(r)))
    r = _run(p, "19[Drive] :: run")
    _rec("19 Drive run: two steps to (0,3), locomotion run",
         _msgs(r) == ["Ran to (0, 3)."]
         and p.avatar_status()["pos"] == [0, 3]
         and p.avatar_status()["locomotion"] == "run",
         str(_msgs(r)))
    r = _run(p, "19[Drive] :: stop")
    _rec("19 Drive stop: idle, position unchanged",
         _msgs(r) == ["Stopped."]
         and p.avatar_status()["pos"] == [0, 3]
         and p.avatar_status()["locomotion"] == "idle",
         str(_msgs(r)))
    st = p.avatar_status()
    r = _run(p, "09[Show] :: avatar")
    _rec("symbiosis: Show (09 avatar) reports the position "
         "Drive (19) reached",
         _msgs(r) == [f"{st['look']}  {st['describe']}"]
         and "(0, 3)" in st["describe"], str(_msgs(r)))

    # -- 17 Shadow: message-only, census untouched
    before_units = set(_units(p))
    r = _run(p, "17[Shadow]")
    r2 = _run(p, "17[Shadow] :: My Track")
    r3 = _run(p, "17[Shadow] :: averyverylonglabelnamethatexceeds")
    _rec("17 Shadow: ids are shadow_<label> (spaces->'_', case "
         "kept, 20-char cap; bare = shadow_bg); census unchanged",
         _msgs(r) == ["Shadow track: shadow_bg "
                      "(parallel — not live)"]
         and _msgs(r2) == ["Shadow track: shadow_My_Track "
                           "(parallel — not live)"]
         and _msgs(r3) == ["Shadow track: "
                           "shadow_averyverylonglabelna "
                           "(parallel — not live)"]
         and set(_units(p)) == before_units
         and "17[Shadow] :: shadow_My_Track" in list(p.history),
         f"{_msgs(r)} / {_msgs(r2)} / {_msgs(r3)}")

    # -- 16 Decay: factor clamp; real effect only when ON
    p.enhance.state.scores["garden_gate"] = 1.0
    p.enhance.state.scores["stone"] = 2.0
    r = _run(p, "16[Decay] :: 0.5")
    _rec("16 Decay EXHIBIT: enhance OFF — the gate refuses, "
         "scores are UNCHANGED, yet the message claims decay",
         _msgs(r) == ["Scores decayed ×0.5."]
         and p.enhance.state.scores["garden_gate"] == 1.0
         and p.enhance.state.scores["stone"] == 2.0,
         str(_msgs(r)))
    p.enhance_on()
    r = _run(p, "16[Decay]")
    sc = p.enhance.state.scores
    _rec("16 Decay: bare Decay defaults to x0.9 and (enhance "
         "ON) multiplies every score; the factor is noted",
         _msgs(r) == ["Scores decayed ×0.9."]
         and abs(sc["garden_gate"] - 0.9) < 1e-9
         and abs(sc["stone"] - 1.8) < 1e-9
         and "16[Decay] :: 0.9" in list(p.history),
         str(sc))
    r = _run(p, "16[Decay] :: 99")
    r2 = _run(p, "16[Decay] :: 0")
    sc = p.enhance.state.scores
    _rec("16 Decay: factor clamps to 1.0 above and 0.1 below "
         "(x1.0 leaves scores, then x0.1 scales them)",
         _msgs(r) == ["Scores decayed ×1.0."]
         and _msgs(r2) == ["Scores decayed ×0.1."]
         and abs(sc["garden_gate"] - 0.09) < 1e-9
         and "16[Decay] :: 1.0" in list(p.history)
         and "16[Decay] :: 0.1" in list(p.history),
         f"{_msgs(r)} / {_msgs(r2)} / {sc}")

    # -- 20 Alpha: close read (form already legged via Map)
    r = _run(p, "20[Alpha]")
    _rec("20 Alpha: census + current form + the Keep tip; "
         "bare Alpha notes 'close'",
         _msgs(r) == ["Alpha close:",
                      f"  ideas={len(_units(p))}",
                      f"  form={p.lattice.perception.form.value}",
                      "  Tip: save before exit — 10[Keep]"]
         and "20[Alpha] :: close" in list(p.history),
         str(_msgs(r)))
    _run(p, "20[Alpha] :: finale")
    _rec("20 Alpha: a label is noted verbatim to history",
         "20[Alpha] :: finale" in list(p.history))

    # -- 10 Keep: save + load round-trip (Bind unit survives)
    r = _run(p, "10[Keep]")
    m = _msgs(r)
    saved_path = os.path.join(
        _ROOT, "form", "state", f"program_{owner}.json")
    _rec("10 Keep: 'Session saved.' with census + nursery "
         "counts and the state file, which exists on disk",
         m[0] == "Session saved."
         and m[1] == f"ideas={len(_units(p))} "
                     f"nursery={p.nursery.summary()['pending']}"
         and m[2] == f"file={saved_path}"
         and os.path.isfile(saved_path), str(m))
    from form.open import Program
    p2 = Program.load(owner=owner)
    _rec("symbiosis: load restores the saved plane — Bind's "
         "and Map's units included",
         "river_song" in p2.cube.session.plane.units
         and "new_place" in p2.cube.session.plane.units
         and len(p2.cube.session.plane.units) == len(_units(p)),
         str(sorted(p2.cube.session.plane.units)))

    # -- 18 Mirror cap: 21 units, header true, 16 bullets
    for i in range(14):
        _run(p, f"08[Create] :: Item {i}")
    total = len(_units(p))
    r = _run(p, "18[Mirror]")
    m = _msgs(r)
    bullets = [x for x in m if x.startswith("  ·")]
    _rec("18 Mirror: with >16 units the header keeps the "
         "true total while bullets cap at 16",
         total > 16 and m[0] == f"Mirror: {total} live ideas"
         and len(bullets) == 16, f"{m[0]} bullets={len(bullets)}")

    # -- 13 Loop (isolated owner): unclamped ringed growth
    owner3 = "D1RegLeaf2Loop"
    q = _program(owner3)
    _run(q, "08[Create] :: Garden Gate")
    _run(q, "08[Create] :: Stone")
    before_units = set(_units(q))
    r = _run(q, "13[Loop]")
    _rec("13 Loop: bare Loop runs 1 cycle — growth proposes "
         "(nursery +3 for 3 units), live census unchanged",
         _msgs(r) == ["Ringed growth: +0 new +3 evolved",
                      "Nursery pending: 3"]
         and set(_units(q)) == before_units, str(_msgs(r)))
    r = _run(q, "13[Loop] :: 7")
    _rec("13 Loop: label 7 runs 7 cycles UNCLAMPED (+21 "
         "evolved) — the contrast with 06 Cycle's 1..5 clamp",
         _msgs(r) == ["Ringed growth: +0 new +21 evolved",
                      "Nursery pending: 24"]
         and set(_units(q)) == before_units, str(_msgs(r)))
    r = _run(q, "13[Loop] :: bogus")
    _rec("13 Loop: a non-digit label falls back to 1 cycle",
         _msgs(r)[0] == "Ringed growth: +0 new +3 evolved",
         str(_msgs(r)))
    # symbiosis: Keep's nursery line counts Loop's proposals
    r = _run(q, "10[Keep]")
    _rec("symbiosis: Keep (10) counts Loop's (13) proposals "
         "in its nursery line (27 pending)",
         _msgs(r)[1].endswith("nursery=27"), str(_msgs(r)))
    _cleanup(owner3)

    # -- REAL_USER_PATH: literal REPL seed lines
    owner2 = "D1RegLeaf2Repl"
    _cleanup(owner2)
    proc = subprocess.run(
        [sys.executable, "-m", "form.repl", "--owner", owner2],
        input="19[Drive] :: run\n20[Alpha]\n",
        capture_output=True, text=True, cwd=_ROOT, timeout=120)
    out = proc.stdout or ""
    _rec("REPL: Drive and Alpha execute on the literal "
         "user path",
         proc.returncode == 0 and "Ran to" in out
         and "Alpha close:" in out, out[-300:])
    _cleanup(owner2)

    # -- docs pins
    _rec("proof cards carry circuit-17 deep notes (09-20)",
         all(n in DEEP_NOTES and "circuit 17" in DEEP_NOTES[n]
             for n in range(9, 21)),
         str([n for n in range(9, 21) if n not in DEEP_NOTES]))

    _cleanup(owner)
    total = len(RESULTS)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        if not ok:
            print(f"FAIL {name} :: {detail}")
    print(f"D1_REGISTRY_LEAF2: {passed}/{total}")
    return passed == total


def smoke():
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
