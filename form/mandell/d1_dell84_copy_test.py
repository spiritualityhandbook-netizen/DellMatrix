#!/usr/bin/env python3
"""D1 deepening circuit 4 — Dell 84 (Copy) deep contract.

D1 rule: derive the Dell's ACTUAL arguments / outputs /
failures from its executor, enforce and test them on public
paths, cover state/persistence, sync the docs. Never invent
semantics from the name.

Dell 84's contract, derived from spectrum_ops.apply_spectrum
(n==84) and its typed signature (signatures.py, derived_from
spectrum_ops.py:103-109):

  src  = lab, else selected[0], else "object"
  dest = "copy_" + src          (DERIVED, never caller-controlled)
  store[dest] = deepcopy(store.get(src, src))
       — a missing source copies the source NAME string itself;
         the signature documents this ("always succeeds")
  publishes last_result (value=dest, source="copy", matched)
  message: "Copy {src}->{dest} original_intact"

The circuit also found and fixed an operational defect in
the generalized English route (semantic_router
._route_generalized): rebuilding the seed from the resolved
Dell discarded the Intent's typed arguments, so "copy A"
executed a bare 84[Copy] and silently copied the fallback
"object" while the receipt reported ok=True. The fix carries
the original atom's args (else the Intent's) onto the rebuilt
atom; chain_exec validates and lowers them. The destructive
guard is untouched: English delete still refuses
blocked_with_reason.

Labels: seed execution PUBLIC_ENTRY_PATH; translate +
route_intent = the REPL's routing authority (INTEGRATION /
PUBLIC_ENTRY); the final check is the literal REPL in a
subprocess (REAL_USER_PATH).
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

    # --- the seed-path contract -------------------------------------
    owner = "D184Seed"
    p = _fresh(owner)
    st = _store(p)
    execute_seed(p, "55[Set] :: A=hello")
    r = execute_seed(p, "84[Copy] :: A")
    _rec("set_then_copy_value_and_original_intact",
         r.get("ok") and st.store.get("copy_A") == "hello"
         and st.store.get("A") == "hello",
         f"ok={r.get('ok')} copy_A={st.store.get('copy_A')!r}")
    _rec("copy_message_receipt",
         any("Copy A->copy_A original_intact" in m
             for m in (r.get("messages") or [])),
         str(r.get("messages"))[:80])
    lr = st.last_result or {}
    _rec("copy_publishes_last_result",
         lr.get("value") == "copy_A" and lr.get("source") == "copy"
         and lr.get("matched") is True,
         str({k: lr.get(k) for k in ("value", "source", "matched")}))

    r = execute_seed(p, "84[Copy] :: Ghost")
    _rec("missing_source_copies_the_name_itself",
         r.get("ok") and st.store.get("copy_Ghost") == "Ghost",
         f"ok={r.get('ok')} copy_Ghost={st.store.get('copy_Ghost')!r}")

    execute_seed(p, "84[Copy] :: copy_A")
    execute_seed(p, "55[Set] :: A=changed")
    execute_seed(p, "84[Copy] :: A")
    _rec("copy_of_copy_and_overwrite_on_recopy",
         st.store.get("copy_copy_A") == "hello"
         and st.store.get("copy_A") == "changed",
         f"copy_copy_A={st.store.get('copy_copy_A')!r} "
         f"copy_A={st.store.get('copy_A')!r}")
    _cleanup(owner)

    owner = "D184Bare"
    p = _fresh(owner)
    st = _store(p)
    r = execute_seed(p, "84[Copy]")
    _rec("bare_copy_falls_back_to_object",
         r.get("ok") and st.store.get("copy_object") == "object",
         f"copy_object={st.store.get('copy_object')!r}")
    _cleanup(owner)

    # --- signature conformance ---------------------------------------
    from form.mandell.signatures import get_signature
    sig = get_signature(84)
    role_names = [role.name for role in (sig.roles or [])]
    _rec("destination_is_derived_never_a_role",
         role_names == ["source"]
         and bool(sig.validate({"destination": "B"}))
         and not sig.validate({"source": "A"}),
         f"roles={role_names} "
         f"validate_dest={sig.validate({'destination': 'B'})}")

    # --- integration: fallback order + deepcopy ----------------------
    owner = "D184Int"
    p = _fresh(owner)
    st = _store(p)
    execute_seed(p, "55[Set] :: A=hello")
    st.selected = ["A"]
    r = execute_seed(p, "84[Copy]")
    _rec("selected_fallback_beats_object",
         r.get("ok") and st.store.get("copy_A") == "hello"
         and "copy_object" not in st.store,
         f"copy_A={st.store.get('copy_A')!r}")
    st.selected = []
    st.store["L"] = [1, [2, 3]]
    execute_seed(p, "84[Copy] :: L")
    st.store["L"][1].append(99)
    _rec("deepcopy_is_independent",
         st.store.get("copy_L") == [1, [2, 3]],
         f"copy_L={st.store.get('copy_L')!r}")
    _cleanup(owner)

    # --- persistence ---------------------------------------------------
    owner = "D184Persist"
    p = _fresh(owner)
    st = _store(p)
    execute_seed(p, "55[Set] :: A=hello")
    st.store["L"] = [1, [2, 3]]
    execute_seed(p, "84[Copy] :: A")
    execute_seed(p, "84[Copy] :: L")
    p.save()
    from form.open import Program
    p2 = Program.load(owner=owner)
    st2 = _store(p2)
    _rec("copy_survives_save_load",
         st2.store.get("copy_A") == "hello"
         and st2.store.get("copy_L") == [1, [2, 3]],
         f"copy_A={st2.store.get('copy_A')!r} "
         f"copy_L={st2.store.get('copy_L')!r}")
    _cleanup(owner)

    # --- the generalized-route fix (English path) ---------------------
    owner = "D184Eng"
    p = _fresh(owner)
    st = _store(p)
    execute_seed(p, "55[Set] :: A=hello")
    execute_seed(p, "55[Set] :: My Field=notes")
    r = _english(p, "copy A")
    _rec("english_copy_uses_the_named_source",
         r.ok and st.store.get("copy_A") == "hello"
         and "copy_object" not in st.store,
         f"ok={r.ok} copy_A={st.store.get('copy_A')!r} seed={r.seed}")
    r = _english(p, "copy My Field")
    _rec("english_copy_preserves_case",
         r.ok and st.store.get("copy_My Field") == "notes",
         f"ok={r.ok} value={st.store.get('copy_My Field')!r}")
    execute_seed(p, "55[Set] :: a=low")
    # A later key makes Get's no-arg fallback (last store key)
    # observably wrong, so this check can tell arg survival from
    # fallback luck.
    execute_seed(p, "55[Set] :: zz=last")
    r = _english(p, "get a")
    lr = st.last_result or {}
    _rec("english_get_args_survive_the_route",
         r.ok and lr.get("value") == "low" and lr.get("matched") is True,
         f"ok={r.ok} last_result={lr.get('value')!r}")
    r = _english(p, "delete A")
    _rec("english_delete_still_blocked",
         not r.ok and "blocked" in (r.error or "")
         and st.store.get("A") == "hello",
         f"ok={r.ok} error={(r.error or '')[:40]}")
    _cleanup(owner)

    # --- chain regression: conflict law unchanged ---------------------
    from form.mandell.seed import parse_seed
    from form.mandell.chain_exec import execute_chain
    owner = "D184Chain"
    p = _fresh(owner)
    st = _store(p)
    execute_seed(p, "55[Set] :: A=hello")
    seed = parse_seed('84[Copy](source="A") :: B')
    out = execute_chain(p, seed, '84[Copy](source="A") :: B')
    _rec("argument_conflict_still_fails_closed",
         not out.get("ok")
         and "ARGUMENT_CONFLICT" in str(out.get("error") or "")
         and "copy_A" not in st.store and "copy_B" not in st.store,
         f"ok={out.get('ok')} error={out.get('error')}")
    _cleanup(owner)

    # --- REAL_USER_PATH: the literal REPL ------------------------------
    owner = "D184Repl"
    _cleanup(owner)
    root = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", ".."))
    proc = subprocess.run(
        [sys.executable, "-m", "form.repl", "--owner", owner],
        input="55[Set] :: A=hello\ncopy A\n10[Keep]\n",
        capture_output=True, text=True, cwd=root, timeout=180)
    from form.open import Program
    p = Program.load(owner=owner)
    st = _store(p)
    _rec("repl_english_copy_lands_in_saved_state",
         proc.returncode == 0 and st.store.get("copy_A") == "hello"
         and "copy_object" not in st.store,
         f"rc={proc.returncode} copy_A={st.store.get('copy_A')!r}")
    _cleanup(owner)

    # --- docs sync: the proof card carries the deep note ---------------
    from form.mandell.dell_cards import DEEP_NOTES
    _rec("proof_card_carries_the_deep_note",
         84 in DEEP_NOTES and "copy_" in DEEP_NOTES[84],
         DEEP_NOTES.get(84, "")[:60])

    ok = all(c for _, c, _ in RESULTS)
    for name, cond, detail in RESULTS:
        print(f"[{'ok' if cond else 'FAIL'}] {name} :: {detail}")
    n = sum(1 for _, c, _ in RESULTS if c)
    print(f"D1_DELL84_COPY: {n}/{len(RESULTS)}")
    return ok


def smoke():
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
