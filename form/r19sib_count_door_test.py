"""R19-SIB — English-door count integrity on every count door.

Director ruling 6987078989 (2026-11-18, PR #490), answering the
all-Dells English-door audit (Ace's order): Q-A a shared semantic
contract for explicit count doors (malformed explicit operand =
deterministic typed refusal before mutation; omitted = the door's
established default; no prefix theft, no Unicode digit coercion,
no unbounded int parsing; valid counts travel losslessly; each
door keeps its own execution bounds — Dell 13/19 do NOT inherit
Dell 6's 1..5); Q-B walk + english_expand hardening included,
REPL walk path probed first; Q-C grow/evolve phrase capture
normalized, full-token matching, malformed counts reach refusal
not fallback growth; Q-D separate circuit, cross-ref GP-E03.

Doors covered: grow family (Dell 13: phrases, english_brain
synonym rewrites, translate fallback arm, _seed_grow), walk
(Dell 19: phrases, translate fallback arm, the REPL handler —
proven LIVE pre-repair: 'walk forward banana' walked 1 and
'walk forward ２０' walked 20 at the real user path),
english_expand (Dell 13 phrase door; default 50 for omitted).

Run: python3 -m form.r19sib_count_door_test
"""
import glob
import os
import shutil
import subprocess
import sys

RESULTS = []


def _rec(name, ok, detail=""):
    RESULTS.append((name, bool(ok)))
    if not ok:
        print(f"FAIL {name}: {detail}")


_OWNER_SEQ = [0]


def _owner():
    _OWNER_SEQ[0] += 1
    return f"SibT{_OWNER_SEQ[0]:03d}"


def _cleanup(owner):
    base = os.path.join(os.path.dirname(__file__), "state")
    for pat in (f"program_{owner}.json", f"nursery_{owner}.json",
                f"checkpoint_{owner}.json", f"confirm_journal_{owner}.json",
                f"confirm_gen_{owner}.json", f"confirm_current_{owner}.json"):
        for f in glob.glob(os.path.join(base, pat)):
            try:
                os.remove(f)
            except OSError:
                pass
    d = os.path.join(base, f"ideas_{owner}")
    if os.path.isdir(d):
        shutil.rmtree(d, ignore_errors=True)


def run_checks() -> bool:
    from form.open import Program
    from form.mandell.core_ii_exec import attach
    from form.mandell.translate import translate
    from form.mandell.semantic_router import route_intent
    from form.mandell.english_brain import normalize_english

    def prog(owner):
        _cleanup(owner)
        p = Program(owner=owner)
        attach(p)
        return p

    # ---------- Brain layer: no theft, no deletion, no conversion
    for text, want_tail in (
        ("evolve ideas -3", "-3"),
        ("evolve ideas 20x", "20x"),
        ("cultivate ideas banana", "banana"),
        ("expand banana", "banana"),
        ("evolve ideas 3", "3"),
        ("evolve ideas three", "three"),
    ):
        norm, _path = normalize_english(text)
        _rec(f"brain[{text}]: operand preserved whole",
             norm.endswith(want_tail), f"normalized={norm!r}")
    norm, _ = normalize_english("grow ２０")
    _rec("brain[grow ２０]: not converted to 20",
         "20" not in norm.replace("２０", ""), f"normalized={norm!r}")

    # ---------- Translate layer: args judgment per door
    def args_of(text):
        return (translate(text).args or {})

    for text, want in (
        ("grow 3", 3), ("grow three", 3), ("grow", 1),
        ("grow ideas 20", 20), ("grow ideas", 1),
    ):
        _rec(f"translate[{text}]: cycles == {want}",
             args_of(text).get("cycles") == want, str(args_of(text)))
    for text, raw in (
        ("grow banana", "banana"), ("grow -3", "-3"),
        ("grow 20x", "20x"), ("grow ²", "²"), ("grow ２０", "２０"),
        ("evolve ideas banana", "banana"),
        ("evolve ideas -3", "-3"), ("evolve ideas 20x", "20x"),
    ):
        got = args_of(text).get("cycles")
        _rec(f"translate[{text}]: malformed travels RAW",
             got == raw, f"cycles={got!r}")
    try:
        got = args_of("grow " + "9" * 5000).get("cycles")
        _rec("translate[grow oversized]: raw travel, no crash",
             got == "9" * 5000, f"cycles type={type(got)}")
    except Exception as e:  # noqa: BLE001
        _rec("translate[grow oversized]: raw travel, no crash",
             False, f"CRASH {type(e).__name__}: {e}")

    for text, want in (("walk forward 3", 3), ("walk 3", 3),
                       ("walk", 1), ("walk forward", 1)):
        _rec(f"translate[{text}]: steps == {want}",
             args_of(text).get("steps") == want, str(args_of(text)))
    for text, raw in (("walk forward banana", "banana"),
                      ("walk forward -3", "-3"),
                      ("walk forward ２０", "２０")):
        got = args_of(text).get("steps")
        _rec(f"translate[{text}]: malformed steps travel RAW",
             got == raw, f"steps={got!r}")
    try:
        args_of("walk forward " + "9" * 5000)
        _rec("translate[walk oversized]: no crash", True, "")
    except Exception as e:  # noqa: BLE001
        _rec("translate[walk oversized]: no crash", False,
             f"CRASH {type(e).__name__}: {e}")

    # english_expand: default 50 only when omitted; valid travels;
    # malformed never becomes a silent number and never crashes.
    _rec("translate[english expand]: omitted defaults to 50",
         args_of("english expand").get("cycles") == 50,
         str(args_of("english expand")))
    _rec("translate[english expand 3]: cycles == 3",
         args_of("english expand 3").get("cycles") == 3,
         str(args_of("english expand 3")))
    for text in ("english expand ２０", "english expand banana"):
        i = translate(text)
        cyc = (i.args or {}).get("cycles")
        _rec(f"translate[{text}]: no silent numeric default",
             i.action == "unknown" or cyc in ("２０", "banana"),
             f"action={i.action} cycles={cyc!r}")
    try:
        translate("english expand " + "9" * 5000)
        _rec("translate[expand oversized]: no crash", True, "")
    except Exception as e:  # noqa: BLE001
        _rec("translate[expand oversized]: no crash", False,
             f"CRASH {type(e).__name__}: {e}")

    # ---------- Router layer: grow end-to-end
    for text in ("grow banana", "grow -3", "grow 20x", "grow ２０",
                 "grow " + "9" * 5000):
        owner = _owner()
        p = prog(owner)
        h0 = len(list(getattr(p, "history", []) or []))
        try:
            r = route_intent(p, translate(text), text)
        except Exception as e:  # noqa: BLE001
            _rec(f"routed[{text[:16]}]: typed refusal, no growth",
                 False, f"CRASH {type(e).__name__}: {e}")
            continue
        h1 = len(list(getattr(p, "history", []) or []))
        _rec(f"routed[{text[:16]}]: typed refusal, no growth",
             (not r.ok)
             and getattr(r, "error", "") == "invalid_loop_count"
             and h1 == h0,
             f"ok={r.ok} err={getattr(r, 'error', '')} hist {h0}->{h1}")
    owner = _owner()
    p = prog(owner)
    r = route_intent(p, translate("grow 20"), "grow 20")
    _rec("routed[grow 20]: valid travels, Loop bounds apply",
         r.ok and r.seed == "13[Loop] :: 20",
         f"ok={r.ok} seed={r.seed!r}")
    owner = _owner()
    p = prog(owner)
    r = route_intent(p, translate("grow"), "grow")
    _rec("routed[grow]: omitted defaults to 1",
         r.ok and r.seed == "13[Loop] :: 1",
         f"ok={r.ok} seed={r.seed!r}")

    # ---------- REPL layer: the real user path for walk + grow
    def repl(owner, lines):
        _cleanup(owner)
        cp = subprocess.run(
            [sys.executable, "-m", "form.repl", "--owner", owner],
            input="\n".join(lines) + "\n", capture_output=True,
            text=True, timeout=180)
        return cp.stdout + cp.stderr

    out = repl(_owner(), ["walk forward 3"])
    _rec("repl[walk forward 3]: walks 3",
         "walked forward 3" in out, out[-200:])
    out = repl(_owner(), ["walk forward banana"])
    _rec("repl[walk forward banana]: refusal, no silent step",
         "walked forward 1" not in out and "invalid" in out.lower(),
         out[-200:])
    out = repl(_owner(), ["walk forward ２０"])
    _rec("repl[walk forward ２０]: refusal, no conversion",
         "walked forward 20" not in out and "invalid" in out.lower(),
         out[-200:])
    out = repl(_owner(), ["grow banana"])
    _rec("repl[grow banana]: RESULT ok=False",
         "RESULT: ok=False" in out, out[-200:])

    failed = [n for n, ok in RESULTS if not ok]
    print(f"R19SIB_COUNT_DOOR: {len(RESULTS) - len(failed)}/{len(RESULTS)}")
    return not failed


def smoke() -> bool:
    return run_checks()


if __name__ == "__main__":
    sys.exit(0 if run_checks() else 1)
