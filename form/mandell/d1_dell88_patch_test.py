#!/usr/bin/env python3
"""D1 deepening circuit 8 — Dell 88 (Patch) deep contract.

Derived from spectrum_ops.apply_spectrum (n==88) and its
typed signature (roles key + value, both required):

  key, val = lab.partition("=") — FIRST "=" splits; the
  value keeps any further "=" characters
  key is stripped; the value is NOT stripped (raw remainder)
  key not in store -> ok=False "patch_miss:{key}" (the bare
                      form reports "patch_miss:"). Patch is
                      UPDATE-ONLY: unlike Dell 55 (Set) it
                      never creates a key.
  otherwise        -> store[key] = val, publishing a matched
                      result cell (value=key, source="patch")

Pinned consequences:
  - an empty value is legal: "A=" stores "" and the key
    remains present (the signature NOTE said so; now proven)
  - patching replaces the value wholesale, including its
    type: a list-valued cell becomes the raw string
  - patches persist (core_ii store is durable)

English: Patch is in the blocked set (blocked_with_reason,
operand-confirmation policy) at the route and the REPL;
translate does produce the 88 intent with key/value args
preserved (the circuit-3 capture fix), and the route still
refuses it. The REPL user path is the Mandell seed line.

Signature sync in this circuit: derived_from pointed at
155-166 (the arm is 208-227) and the output text now
states the update-only law; the failures text was already
accurate. The suite pins the corrected range.

Labels: seed execution PUBLIC_ENTRY_PATH; translate +
route_intent = the REPL's routing authority; the final
checks are the literal REPL in subprocesses (REAL_USER_PATH).
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


def _repl(owner, lines):
    root = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        "..", ".."))
    _cleanup(owner)
    proc = subprocess.run(
        [sys.executable, "-m", "form.repl", "--owner", owner],
        input=lines, capture_output=True, text=True, cwd=root,
        timeout=180)
    from form.open import Program
    p = Program.load(owner=owner)
    store = dict(_store(p).store)
    _cleanup(owner)
    return proc.returncode, store


def main():
    from form.mandell.executor import execute_seed

    owner = "D188Seed"
    p = _fresh(owner)
    st = _store(p)
    execute_seed(p, "55[Set] :: A=hello")
    r = execute_seed(p, "88[Patch] :: A=world")
    lr = st.last_result or {}
    _rec("patch_updates_and_publishes",
         r.get("ok") and st.store.get("A") == "world"
         and lr.get("value") == "A" and lr.get("source") == "patch"
         and lr.get("matched") is True,
         f"ok={r.get('ok')} A={st.store.get('A')!r} lr={lr.get('value')!r}")
    r = execute_seed(p, "88[Patch] :: Ghost=x")
    lr = st.last_result or {}
    _rec("patch_never_creates_patch_miss",
         not r.get("ok") and r.get("error") == "patch_miss:Ghost"
         and "Ghost" not in st.store
         and lr.get("matched") is False
         and lr.get("error") == "patch_miss:Ghost",
         f"error={r.get('error')}")
    r = execute_seed(p, "88[Patch]")
    _rec("bare_patch_reports_empty_key",
         not r.get("ok") and r.get("error") == "patch_miss:",
         f"error={r.get('error')!r}")
    r = execute_seed(p, "88[Patch] :: A=b=c")
    _rec("value_keeps_further_equals",
         r.get("ok") and st.store.get("A") == "b=c",
         f"A={st.store.get('A')!r}")
    r = execute_seed(p, "88[Patch] :: A=")
    _rec("empty_value_is_legal_and_key_survives",
         r.get("ok") and "A" in st.store and st.store.get("A") == "",
         f"A={st.store.get('A')!r} present={'A' in st.store}")
    r = execute_seed(p, "88[Patch] ::  A = spaced")
    _rec("key_stripped_value_kept_raw",
         r.get("ok") and st.store.get("A") == " spaced",
         f"A={st.store.get('A')!r}")
    st.store["L"] = [1, 2]
    r = execute_seed(p, "88[Patch] :: L=text")
    _rec("patch_replaces_value_type_wholesale",
         r.get("ok") and st.store.get("L") == "text"
         and isinstance(st.store.get("L"), str),
         f"L={st.store.get('L')!r}")
    r = execute_seed(p, '88[Patch](key="A", value="v2")')
    _rec("typed_args_patch",
         r.get("ok") and st.store.get("A") == "v2",
         f"ok={r.get('ok')} A={st.store.get('A')!r}")
    _cleanup(owner)

    # English: blocked set.
    owner = "D188Eng"
    p = _fresh(owner)
    st = _store(p)
    execute_seed(p, "55[Set] :: A=hello")
    r = _english(p, "patch A to v3")
    _rec("english_patch_blocked_with_reason",
         not r.ok and not r.routed
         and "blocked_with_reason" in (r.error or "")
         and st.store.get("A") == "hello",
         f"routed={r.routed} error={(r.error or '')[:44]}")
    _cleanup(owner)

    # Persistence.
    owner = "D188Persist"
    p = _fresh(owner)
    st = _store(p)
    execute_seed(p, "55[Set] :: A=hello")
    execute_seed(p, "88[Patch] :: A=world")
    p.save()
    from form.open import Program
    p2 = Program.load(owner=owner)
    st2 = _store(p2)
    _rec("patch_survives_save_load",
         st2.store.get("A") == "world",
         f"A={st2.store.get('A')!r}")
    _cleanup(owner)

    # REAL_USER_PATH: the literal REPL, both surfaces.
    rc, store = _repl(
        "D188ReplSeed",
        "55[Set] :: A=hello\n88[Patch] :: A=world\n10[Keep]\n")
    _rec("repl_seed_patch_lands_in_saved_state",
         rc == 0 and store.get("A") == "world",
         f"rc={rc} A={store.get('A')!r}")
    rc, store = _repl(
        "D188ReplEng",
        "55[Set] :: A=hello\npatch A to world\n10[Keep]\n")
    _rec("repl_english_patch_refused_in_saved_state",
         rc == 0 and store.get("A") == "hello",
         f"rc={rc} A={store.get('A')!r}")

    # Docs sync.
    from form.mandell.signatures import get_signature
    from form.mandell.dell_cards import DEEP_NOTES
    sig = get_signature(88)
    _rec("signature_derived_from_matches_code",
         sig.derived_from.endswith("208-227")
         and "update-only" in sig.output,
         sig.derived_from)
    _rec("proof_card_carries_the_deep_note",
         88 in DEEP_NOTES and "patch_miss" in DEEP_NOTES[88],
         DEEP_NOTES.get(88, "")[:60])

    ok = all(c for _, c, _ in RESULTS)
    for name, cond, detail in RESULTS:
        print(f"[{'ok' if cond else 'FAIL'}] {name} :: {detail}")
    n = sum(1 for _, c, _ in RESULTS if c)
    print(f"D1_DELL88_PATCH: {n}/{len(RESULTS)}")
    return ok


def smoke():
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
