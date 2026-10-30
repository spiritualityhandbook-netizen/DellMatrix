#!/usr/bin/env python3
"""D1 deepening circuit 11 — Dell 56 (Get) deep contract.

Derived from query_ops.apply_query (n==56) and its typed
signature (role key, required for typed invocation):

  key = lab, or — when lab is empty — the LAST INSERTED
        store key, or "" when the store is empty
  key absent -> cell(value=None, matched=False,
                error="missing"), message "Get {key}=MISSING"
  value == "" -> cell(value="", matched=False,
                error="empty") — a stored empty string is
                a distinct third state, not a hit
  otherwise  -> cell(value=stored value, matched=True,
                error=""), the value itself (identity for
                non-string values)

Pinned consequences:
  - THREE-STATE READ: ok / empty / missing, told apart
    only by the result cell.
  - The atom returns ok=True in ALL THREE states —
    including missing. The miss lives in the cell, not
    the atom result. (Contrast Dell 86 Delete, whose
    missing key fails the atom with delete_missing:{key}.)
  - Get is read-only: store keys, values, and order are
    byte-identical after any Get.
  - The bare-Get fallback reads the last inserted key —
    insertion order, not alphabetical, not most-recently
    read.

English: Get IS reachable ("get A" / "find A" -> 56).
The old ARGUMENT_LOSS residual (limitation_knowledge,
circuit 3: MITIGATED) lowercased the operand on the
English path — "get A" looked up 'a'. D1 reconciliation
R5 repaired that end to end: the English operand is
preserved, so "get A" reads 'A' and returns its value,
at the route and in the literal REPL; the record now
reads RESOLVED. (Historical residual evidence stays in
the circuit-11 commit.)

Signature sync in this circuit: derived_from 29-38 ->
35-44; failures text gains the empty state; output text
states the three-state read and the ok=True law.

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
    return proc.returncode, proc.stdout, store


def main():
    from form.mandell.executor import execute_seed

    owner = "D156Seed"
    p = _fresh(owner)
    st = _store(p)
    r = execute_seed(p, "56[Get]")
    lr = st.last_result or {}
    _rec("bare_get_on_empty_store_is_missing_with_empty_key",
         r.get("ok") and lr.get("matched") is False
         and lr.get("error") == "missing" and lr.get("predicate") == "",
         f"error={lr.get('error')} pred={lr.get('predicate')!r}")
    execute_seed(p, "55[Set] :: A=hello")
    r = execute_seed(p, "56[Get] :: A")
    lr = st.last_result or {}
    _rec("get_hit_publishes_value",
         r.get("ok") and lr.get("value") == "hello"
         and lr.get("matched") is True and lr.get("error") == ""
         and lr.get("source") == "get",
         f"value={lr.get('value')!r}")
    r = execute_seed(p, "56[Get] :: Ghost")
    lr = st.last_result or {}
    _rec("missing_key_atom_ok_cell_reports_the_miss",
         r.get("ok") and lr.get("value") is None
         and lr.get("matched") is False
         and lr.get("error") == "missing"
         and any("Get Ghost=MISSING" in m
                 for m in r.get("messages") or []),
         f"ok={r.get('ok')} error={lr.get('error')}")
    execute_seed(p, "55[Set] :: E=")
    r = execute_seed(p, "56[Get] :: E")
    lr = st.last_result or {}
    _rec("stored_empty_string_is_a_third_state",
         r.get("ok") and lr.get("value") == ""
         and lr.get("matched") is False and lr.get("error") == "empty",
         f"value={lr.get('value')!r} error={lr.get('error')}")
    execute_seed(p, "55[Set] :: B=second")
    r = execute_seed(p, "56[Get]")
    lr = st.last_result or {}
    _rec("bare_get_falls_back_to_last_inserted_key",
         r.get("ok") and lr.get("predicate") == "B"
         and lr.get("value") == "second",
         f"pred={lr.get('predicate')} value={lr.get('value')!r}")
    st.store["L"] = [1, 2]
    ref = st.store["L"]
    r = execute_seed(p, "56[Get] :: L")
    lr = st.last_result or {}
    _rec("nonstring_value_returned_by_identity",
         r.get("ok") and lr.get("value") is ref
         and lr.get("matched") is True,
         f"identity={lr.get('value') is ref}")
    snap = dict(st.store)
    keys_before = list(st.store)
    execute_seed(p, "56[Get] :: A")
    execute_seed(p, "56[Get] :: Ghost")
    _rec("get_is_read_only",
         st.store == snap and list(st.store) == keys_before,
         f"keys={list(st.store)}")
    r = execute_seed(p, '56[Get](key="A")')
    lr = st.last_result or {}
    _rec("typed_args_get",
         r.get("ok") and lr.get("value") == "hello",
         f"value={lr.get('value')!r}")
    _cleanup(owner)

    # English: reachable, operand case preserved (R5).
    owner = "D156Eng"
    p = _fresh(owner)
    st = _store(p)
    execute_seed(p, "55[Set] :: low=down")
    r = _english(p, "get low")
    lr = st.last_result or {}
    _rec("english_get_lowercase_key_returns_value",
         r.ok and r.routed and lr.get("value") == "down",
         f"routed={r.routed} value={lr.get('value')!r}")
    execute_seed(p, "55[Set] :: A=hello")
    r = _english(p, "get A")
    lr = st.last_result or {}
    _rec("english_get_uppercase_preserves_the_key_R5",
         r.ok and lr.get("value") == "hello"
         and lr.get("predicate") == "A"
         and st.store.get("A") == "hello",
         f"pred={lr.get('predicate')!r} value={lr.get('value')!r}")
    _cleanup(owner)

    # REAL_USER_PATH: the literal REPL, both surfaces.
    rc, out, store = _repl(
        "D156ReplSeed",
        "55[Set] :: A=hello\n56[Get] :: A\n10[Keep]\n")
    _rec("repl_seed_get_reports_ok_in_output",
         rc == 0 and "Get A='hello' status=ok" in out
         and store.get("A") == "hello",
         f"rc={rc}")
    rc, out, store = _repl(
        "D156ReplEng",
        "55[Set] :: A=hello\nget A\n10[Keep]\n")
    _rec("repl_english_get_preserves_the_key_R5",
         rc == 0 and "Get A='hello'" in out
         and store.get("A") == "hello",
         f"rc={rc}")

    # Docs sync.
    from form.mandell.signatures import get_signature
    from form.mandell.dell_cards import DEEP_NOTES
    sig = get_signature(56)
    _rec("signature_matches_code",
         sig.derived_from.endswith("35-44")
         and "empty" in sig.failures,
         sig.derived_from)
    _rec("proof_card_carries_the_deep_note",
         56 in DEEP_NOTES and "three-state" in DEEP_NOTES[56].lower(),
         DEEP_NOTES.get(56, "")[:60])

    ok = all(c for _, c, _ in RESULTS)
    for name, cond, detail in RESULTS:
        print(f"[{'ok' if cond else 'FAIL'}] {name} :: {detail}")
    n = sum(1 for _, c, _ in RESULTS if c)
    print(f"D1_DELL56_GET: {n}/{len(RESULTS)}")
    return ok


def smoke():
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
