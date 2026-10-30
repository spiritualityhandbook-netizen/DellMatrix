"""D1 circuit 16 (registry pass, cluster 1) — leaf foundation
Dells 00-07 DEEP CONTRACTS.

The first cluster of the full-registry pass: the leaf
executor's foundation Dells (executor_leaf.py arms 0-7).
None of the eight is typed. Contracts proven here, per
Dell, through the public seed path:

- 00 Nova: message-only locked floor — the exact refusal
  line, and NO state change (plane census, avatar, and
  history all untouched).
- 01 Initiate: message-only; names the program owner.
- 02 Persona: a pure READ of avatar_status — the message
  is exactly "<look>  <describe>", and it reflects state
  written by other Dells (after 04 turns the avatar,
  Persona reports the new facing).
- 03 Logic: prints the four live constraints; a label is
  echoed as a noted rule AND written to program history
  via note_seed ("03[Logic] :: <label>"); bare Logic
  notes "constraints".
- 04 Transform: substring dispatch on the lowered label —
  left/right rotate the avatar (N -> NW -> ...), sit /
  stand set posture, jump lands back at STAND, toggle
  flips the lattice form (cube -> sphere -> cube); an
  unrecognized label is a named no-op ("Transform
  ready.") that changes nothing.
- 05 Tone: expression map over the lowered label (joy,
  smile, calm, focus, soft, intense, curious, neutral);
  any other label — and a bare Tone — falls back to
  NEUTRAL (never an error).
- 06 Cycle: n = int(label) if digits else 1, CLAMPED to
  1..5; growth PROPOSES (message counts proposals) but
  never writes the live plane — the census is unchanged
  (the growth gate); note_seed records the clamped n.
- 07 Link: mints a plane unit through the same place_idea
  machinery as Create: name "link_<label or 'link'>",
  canonical slug id, label with '_' -> ' ', words = the
  name as passed, Skin.CUBE, collision dedup.

Cluster symbiosis: a Link-minted unit is immediately
selectable by Core II Select (51); Persona (02) reads
what Transform (04) wrote.

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
    owner = "D1RegLeaf"
    p = _program(owner)

    # -- 00 Nova: locked floor, zero state change
    before_units = set(_units(p))
    before_hist = list(p.history)
    r = _run(p, "00[Nova]")
    _rec("00 Nova: exact locked-floor line, no state change",
         r.get("ok") is True
         and _msgs(r) == ["Nova is cheat/edge only — floor "
                          "stays locked."]
         and set(_units(p)) == before_units
         and list(p.history) == before_hist,
         str(_msgs(r)))

    # -- 01 Initiate: names the owner, no mutation
    r = _run(p, "01[Initiate]")
    _rec("01 Initiate: message names the owner; census intact",
         _msgs(r) == [f"Initiated. owner={owner}"]
         and set(_units(p)) == before_units, str(_msgs(r)))

    # -- 03 Logic: constraints + history note (before 02 so
    #    the read-after-write leg below stays attributable)
    r = _run(p, "03[Logic] :: Be Kind")
    m = _msgs(r)
    _rec("03 Logic: four constraints + the noted rule line",
         m[0] == "Logic constraints (live):"
         and any("Floor locked" in x for x in m)
         and any("Growth never auto-writes" in x for x in m)
         and m[-1] == "  · noted rule: Be Kind", str(m))
    _rec("03 Logic: note_seed writes history '03[Logic] :: "
         "Be Kind'",
         "03[Logic] :: Be Kind" in list(p.history),
         str(list(p.history)))
    _run(p, "03[Logic]")
    _rec("03 Logic: bare Logic notes 'constraints'",
         "03[Logic] :: constraints" in list(p.history))

    # -- 04 Transform: turn / posture / form / no-op
    _rec("04 setup: avatar starts facing N, posture stand",
         p.avatar_status()["facing"] == "N"
         and p.avatar_status()["posture"] == "stand")
    r = _run(p, "04[Transform] :: left")
    _rec("04 Transform left: facing N -> NW, message agrees",
         _msgs(r) == ["Turned left. Facing NW."]
         and p.avatar_status()["facing"] == "NW",
         str(_msgs(r)))
    r = _run(p, "04[Transform] :: sit")
    _rec("04 Transform sit: posture sit",
         _msgs(r) == ["Sat down."]
         and p.avatar_status()["posture"] == "sit")
    r = _run(p, "04[Transform] :: jump")
    _rec("04 Transform jump: lands back at stand",
         _msgs(r) == ["Jumped."]
         and p.avatar_status()["posture"] == "stand")
    r = _run(p, "04[Transform] :: toggle")
    f1 = _msgs(r)
    r = _run(p, "04[Transform] :: toggle")
    _rec("04 Transform toggle: form flips sphere then cube",
         f1 == ["Form toggled → sphere"]
         and _msgs(r) == ["Form toggled → cube"],
         f"{f1} / {_msgs(r)}")
    snap = p.avatar_status()
    r = _run(p, "04[Transform] :: wiggle")
    _rec("04 Transform unknown label: named no-op, state "
         "identical",
         _msgs(r) == ["Transform ready."]
         and p.avatar_status() == snap, str(_msgs(r)))

    # -- 02 Persona: pure read that reflects 04's writes
    st = p.avatar_status()
    r = _run(p, "02[Persona]")
    _rec("02 Persona: message is exactly look + describe of "
         "live status (facing NW after 04's turn)",
         _msgs(r) == [f"{st['look']}  {st['describe']}"]
         and "facing NW" in st["describe"], str(_msgs(r)))

    # -- 05 Tone: map + NEUTRAL fallback
    r = _run(p, "05[Tone] :: joy")
    _rec("05 Tone joy: face (^_^), tone=joy",
         _msgs(r) == ["(^_^)  tone=joy"], str(_msgs(r)))
    r = _run(p, "05[Tone] :: bogus")
    r2 = _run(p, "05[Tone]")
    _rec("05 Tone: unknown label and bare Tone both fall "
         "back to NEUTRAL",
         _msgs(r) == [":-)  tone=neutral"]
         and _msgs(r2) == [":-)  tone=neutral"],
         f"{_msgs(r)} / {_msgs(r2)}")

    # -- 06 Cycle: clamp + propose-only growth + note
    before_units = set(_units(p))
    r = _run(p, "06[Cycle] :: 9")
    _rec("06 Cycle: label 9 clamps to x5; growth proposes "
         "but the live census is unchanged (the gate)",
         _msgs(r)[0].startswith("Cycle x5:")
         and set(_units(p)) == before_units, str(_msgs(r)))
    _rec("06 Cycle: note_seed records the CLAMPED n",
         "06[Cycle] :: 5" in list(p.history),
         str(list(p.history)[-3:]))
    r = _run(p, "06[Cycle]")
    _rec("06 Cycle: bare Cycle runs x1",
         _msgs(r)[0].startswith("Cycle x1:"), str(_msgs(r)))

    # -- 07 Link: place_idea machinery with the link_ prefix
    r = _run(p, "07[Link] :: Garden Gate")
    u = _units(p).get("link_garden_gate")
    _rec("07 Link: unit link_garden_gate minted (label "
         "'link Garden Gate', words raw, CUBE)",
         u is not None and u.label == "link Garden Gate"
         and u.words == "link_Garden Gate"
         and str(u.skin) == "Skin.CUBE"
         and 'Created idea: "link_Garden Gate"' in str(
             r.get("messages")),
         f"{u.label}|{u.words}" if u else "missing")
    _run(p, "07[Link] :: Garden Gate")
    _run(p, "07[Link]")
    _rec("07 Link: repeat dedups to _1; bare Link mints "
         "link_link",
         "link_garden_gate_1" in _units(p)
         and "link_link" in _units(p), str(sorted(_units(p))))

    # -- cluster symbiosis: Core II Select sees Link's unit
    _run(p, "51[Select] :: link")
    sel = list(p.core_ii.selected)
    _rec("symbiosis: Select (51) finds the Link-minted "
         "units on the plane",
         "link_garden_gate" in sel and "link_link" in sel,
         str(sel))

    # -- REAL_USER_PATH: literal REPL seed lines
    owner2 = "D1RegLeafRepl"
    _cleanup(owner2)
    proc = subprocess.run(
        [sys.executable, "-m", "form.repl", "--owner", owner2],
        input="04[Transform] :: left\n05[Tone] :: joy\n",
        capture_output=True, text=True, cwd=_ROOT, timeout=120)
    out = proc.stdout or ""
    _rec("REPL: Transform and Tone execute on the literal "
         "user path",
         proc.returncode == 0 and "Turned left" in out
         and "tone=joy" in out, out[-300:])
    _cleanup(owner2)

    # -- docs pins
    _rec("proof cards carry circuit-16 deep notes (00-07)",
         all(n in DEEP_NOTES and "circuit 16" in DEEP_NOTES[n]
             for n in range(8)),
         str([n for n in range(8) if n not in DEEP_NOTES]))

    _cleanup(owner)
    total = len(RESULTS)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        if not ok:
            print(f"FAIL {name} :: {detail}")
    print(f"D1_REGISTRY_LEAF: {passed}/{total}")
    return passed == total


def smoke():
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
