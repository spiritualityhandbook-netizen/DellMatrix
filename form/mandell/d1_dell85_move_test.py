#!/usr/bin/env python3
"""D1 deepening circuit 5 — Dell 85 (Move) deep contract.

Derived from spectrum_ops.apply_spectrum (n==85) and its
typed signature (roles source + destination, both required;
failures malformed_move / move_missing):

  src, dest = lab.partition(">"), both stripped
  no src or no dest   -> ok=False "malformed_move" + a
                         failure result cell (matched=False)
  src not in store    -> ok=False "move_missing" + failure cell
  dest != src         -> store[dest] = store.pop(src): the
                         SAME object relocates (identity, not
                         a copy — the contrast with Dell 84);
                         an existing destination is overwritten;
                         partition is on the FIRST ">", so a
                         destination may itself contain ">"
  dest == src         -> named no-op success: message "Move
                         same identity" + a fresh matched cell

Move is NOT in the English blocked set (86/87/88 are): the
English path executes with its named operands, and the moved
state persists (core_ii store is durable). This suite pins
that asymmetry as the observed contract, it does not bless
or change it.

Labels: seed execution PUBLIC_ENTRY_PATH; translate +
route_intent = the REPL's routing authority; the final check
is the literal REPL in a subprocess (REAL_USER_PATH).
"""
from __future__ import annotations

import glob
import os
import shutil
import subprocess
import sys

RESULTS = []

STATE_DIR = os.path.join(os.path.dirname(__file__), "..", "state")


def _rec(name, cond, detail=""):
    RESULTS.append((name, bool(cond), str(detail)))


def _cleanup(owner):
    for pat in (f"program_{owner}.json", f"nursery_{owner}.json",
                f"checkpoint_{owner}_*", f"confirm_{owner}.journal.json",
                f"current_{owner}.json"):
        for f in glob.glob(os.path.join(STATE_DIR, pat)):
            try:
                os.remove(f)
            except FileNotFoundError:
                pass
            except OSError as exc:
                raise RuntimeError(f"cleanup failed for {f}: {exc}")
    d = os.path.join(STATE_DIR, f"ideas_{owner}")
    if os.path.isdir(d):
        shutil.rmtree(d)


def _fresh(owner):
    _cleanup(owner)
    from form.open import Program
    return Program(owner)


def _store(p):
    from form.mandell.core_ii_exec import attach
    return attach(p)


def _english(p, line):
    from form.mandell.translate import translate
    from form.mandell.semantic_router import route_intent
    return route_intent(p, translate(line), line)


def main():
    from form.mandell.executor import execute_seed

    owner = "D185Seed"
    p = _fresh(owner)
    st = _store(p)
    execute_seed(p, "55[Set] :: A=hello")
    r = execute_seed(p, "85[Move] :: A>B")
    lr = st.last_result or {}
    _rec("move_relocates_and_publishes",
         r.get("ok") and "A" not in st.store
         and st.store.get("B") == "hello"
         and lr.get("value") == "B" and lr.get("source") == "move"
         and lr.get("matched") is True
         and any("Move A->B identity_preserved" in m
                 for m in (r.get("messages") or [])),
         f"ok={r.get('ok')} B={st.store.get('B')!r} lr={lr.get('value')!r}")
    r = execute_seed(p, "85[Move] :: B>B")
    lr = st.last_result or {}
    _rec("move_to_self_is_a_named_noop_success",
         r.get("ok") and st.store.get("B") == "hello"
         and any("Move same identity" in m
                 for m in (r.get("messages") or []))
         and lr.get("value") == "B" and lr.get("matched") is True,
         f"ok={r.get('ok')} lr={lr.get('value')!r}")
    r = execute_seed(p, "85[Move] :: Ghost>X")
    lr = st.last_result or {}
    _rec("move_missing_fails_honestly",
         not r.get("ok") and r.get("error") == "move_missing"
         and lr.get("matched") is False
         and lr.get("error") == "move_missing"
         and "X" not in st.store,
         f"ok={r.get('ok')} error={r.get('error')}")
    r1 = execute_seed(p, "85[Move] :: OnlySrc")
    r2 = execute_seed(p, "85[Move]")
    _rec("move_malformed_without_destination",
         not r1.get("ok") and r1.get("error") == "malformed_move"
         and not r2.get("ok") and r2.get("error") == "malformed_move",
         f"r1={r1.get('error')} r2={r2.get('error')}")
    execute_seed(p, "55[Set] :: C=see")
    r = execute_seed(p, "85[Move] :: B>C")
    _rec("move_overwrites_destination",
         r.get("ok") and st.store.get("C") == "hello"
         and "B" not in st.store,
         f"C={st.store.get('C')!r}")
    execute_seed(p, "55[Set] :: X=ex")
    r = execute_seed(p, "85[Move] :: X>Y>Z")
    _rec("move_destination_may_contain_gt",
         r.get("ok") and st.store.get("Y>Z") == "ex"
         and "X" not in st.store,
         f"keys={[k for k in st.store if 'Y' in k]}")
    r = execute_seed(p, '85[Move](source="C", destination="D")')
    _rec("typed_args_move",
         r.get("ok") and st.store.get("D") == "hello"
         and "C" not in st.store,
         f"ok={r.get('ok')} D={st.store.get('D')!r}")
    _cleanup(owner)

    # Identity, not copy (the Dell 84 contrast).
    owner = "D185Int"
    p = _fresh(owner)
    st = _store(p)
    st.store["L"] = [1, 2]
    ref = st.store["L"]
    execute_seed(p, "85[Move] :: L>M")
    _rec("identity_not_copy",
         st.store.get("M") is ref and "L" not in st.store,
         f"same_object={st.store.get('M') is ref}")
    _cleanup(owner)

    # English path: Move executes (not in the blocked set).
    owner = "D185Eng"
    p = _fresh(owner)
    st = _store(p)
    execute_seed(p, "55[Set] :: N=nval")
    r = _english(p, "move N to Final")
    _rec("english_move_executes_with_named_operands",
         r.ok and st.store.get("Final") == "nval"
         and "N" not in st.store,
         f"ok={r.ok} Final={st.store.get('Final')!r} seed={r.seed}")
    r = _english(p, "move Ghost to X")
    _rec("english_move_missing_source_fails",
         not r.ok and "move_missing" in (r.error or "")
         and "X" not in st.store,
         f"ok={r.ok} error={(r.error or '')[:40]}")
    _cleanup(owner)

    # Persistence.
    owner = "D185Persist"
    p = _fresh(owner)
    st = _store(p)
    execute_seed(p, "55[Set] :: A=hello")
    execute_seed(p, "85[Move] :: A>B")
    p.save()
    from form.open import Program
    p2 = Program.load(owner=owner)
    st2 = _store(p2)
    _rec("move_survives_save_load",
         st2.store.get("B") == "hello" and "A" not in st2.store,
         f"B={st2.store.get('B')!r}")
    _cleanup(owner)

    # REAL_USER_PATH: the literal REPL. The Mandell seed line
    # is the REPL user path for this Dell (see the next check
    # for why the English line is not).
    owner = "D185Repl"
    _cleanup(owner)
    root = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", ".."))
    proc = subprocess.run(
        [sys.executable, "-m", "form.repl", "--owner", owner],
        input="55[Set] :: A=hello\n85[Move] :: A>B\n10[Keep]\n",
        capture_output=True, text=True, cwd=root, timeout=180)
    from form.open import Program
    p = Program.load(owner=owner)
    st = _store(p)
    _rec("repl_seed_move_lands_in_saved_state",
         proc.returncode == 0 and st.store.get("B") == "hello"
         and "A" not in st.store,
         f"rc={proc.returncode} B={st.store.get('B')!r}")
    _cleanup(owner)

    # Surface fact, pinned not fixed: at the REPL, an English
    # "move A to B" line is captured by the avatar-navigation
    # layer ("You walked forward 1") before intent routing —
    # translate() itself yields the Dell 85 intent, but the
    # REPL surface owns the word "move" for walking. The store
    # move does NOT execute from that line at this surface.
    owner = "D185ReplNav"
    _cleanup(owner)
    proc = subprocess.run(
        [sys.executable, "-m", "form.repl", "--owner", owner],
        input="55[Set] :: A=hello\nmove A to B\n10[Keep]\n",
        capture_output=True, text=True, cwd=root, timeout=180)
    p = Program.load(owner=owner)
    st = _store(p)
    _rec("repl_english_move_is_captured_by_navigation",
         proc.returncode == 0 and st.store.get("A") == "hello"
         and "B" not in st.store,
         f"rc={proc.returncode} A={st.store.get('A')!r} "
         f"B={st.store.get('B')!r}")
    _cleanup(owner)

    from form.mandell.dell_cards import DEEP_NOTES
    _rec("proof_card_carries_the_deep_note",
         85 in DEEP_NOTES and "pop" in DEEP_NOTES[85],
         DEEP_NOTES.get(85, "")[:60])

    ok = all(c for _, c, _ in RESULTS)
    for name, cond, detail in RESULTS:
        print(f"[{'ok' if cond else 'FAIL'}] {name} :: {detail}")
    n = sum(1 for _, c, _ in RESULTS if c)
    print(f"D1_DELL85_MOVE: {n}/{len(RESULTS)}")
    return ok


def smoke():
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
