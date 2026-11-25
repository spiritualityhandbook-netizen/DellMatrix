#!/usr/bin/env python3
"""D1 deepening circuit 6 — Dell 86 (Delete) deep contract.

Derived from spectrum_ops.apply_spectrum (n==86) and its
typed signature (role key, required):

  key = the whole lab (no partition)
  key in store  -> pop from STORE (store wins over groups
                   when a name exists in both), message
                   "Delete store[key]"
  key in groups -> pop from groups, "Delete group[key]"
  else          -> ok=False "delete_missing:{key}", with
                   the empty key reported as
                   "delete_missing:empty" (this circuit synced
                   the signature's failures text to that truth)

  NO_AUTHORITATIVE_RESULT (the C2 law, in the executor's own
  comment): deletion produces nothing, so even a SUCCESSFUL
  delete publishes an explicit non-matched result cell
  (value=None, matched=False, source="delete", error empty)
  — never a stale success from an earlier operation, and
  distinguishable from the failure cell, which carries the
  error.

English: Delete is in the blocked set — the route refuses
blocked_with_reason (destructive store mutation via English
is deferred pending operand-confirmation policy; raw
Mandell only), at route_intent and at the REPL surface
alike. Negated English ("don't delete ...") does not even
produce a delete intent. The REPL user path for 86 is the
Mandell seed line. Deletions persist.

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
    intent = translate(line)
    return intent, route_intent(p, intent, line)


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
    st = _store(p)
    store = dict(st.store)
    _cleanup(owner)
    return proc.returncode, store


def main():
    from form.mandell.executor import execute_seed

    owner = "D186Seed"
    p = _fresh(owner)
    st = _store(p)
    execute_seed(p, "55[Set] :: A=hello")
    execute_seed(p, "84[Copy] :: A")  # a matched result to go stale
    r = execute_seed(p, "86[Delete] :: A")
    lr = st.last_result or {}
    _rec("delete_store_key_and_no_authoritative_result",
         r.get("ok") and "A" not in st.store
         and lr.get("value") is None and lr.get("matched") is False
         and lr.get("source") == "delete" and not lr.get("error"),
         f"ok={r.get('ok')} lr={ {k: lr.get(k) for k in ('value', 'matched', 'source', 'error')} }")
    st.groups["G"] = ["x", "y"]
    r = execute_seed(p, "86[Delete] :: G")
    _rec("delete_group_key",
         r.get("ok") and "G" not in st.groups
         and any("Delete group[G]" in m for m in (r.get("messages") or [])),
         f"ok={r.get('ok')}")
    execute_seed(p, "55[Set] :: Dual=storeval")
    st.groups["Dual"] = ["m"]
    r1 = execute_seed(p, "86[Delete] :: Dual")
    kept_after_first = "Dual" in st.groups and "Dual" not in st.store
    r2 = execute_seed(p, "86[Delete] :: Dual")
    _rec("store_precedence_over_groups",
         r1.get("ok") and kept_after_first and r2.get("ok")
         and "Dual" not in st.groups,
         f"after_first_group_kept={kept_after_first}")
    r = execute_seed(p, "86[Delete] :: Nope")
    lr = st.last_result or {}
    _rec("delete_missing_fails_with_error_cell",
         not r.get("ok") and r.get("error") == "delete_missing:Nope"
         and lr.get("matched") is False
         and lr.get("error") == "delete_missing:Nope",
         f"error={r.get('error')}")
    r = execute_seed(p, "86[Delete]")
    _rec("bare_delete_reports_empty",
         not r.get("ok") and r.get("error") == "delete_missing:empty",
         f"error={r.get('error')}")
    execute_seed(p, "55[Set] :: T=tval")
    r = execute_seed(p, '86[Delete](key="T")')
    _rec("typed_args_delete",
         r.get("ok") and "T" not in st.store,
         f"ok={r.get('ok')}")
    _cleanup(owner)

    # English: blocked, and negation never becomes an intent.
    owner = "D186Eng"
    p = _fresh(owner)
    st = _store(p)
    execute_seed(p, "55[Set] :: K=keep")
    _, r = _english(p, "delete K")
    _rec("english_delete_blocked_with_reason",
         not r.ok and not r.routed
         and "blocked_with_reason" in (r.error or "")
         and st.store.get("K") == "keep",
         f"routed={r.routed} error={(r.error or '')[:44]}")
    intent, r = _english(p, "don't delete K")
    _rec("negated_delete_never_executes",
         intent.action != "delete" and not r.ok
         and st.store.get("K") == "keep",
         f"action={intent.action}")
    _cleanup(owner)

    # Persistence: the deletion stays deleted.
    owner = "D186Persist"
    p = _fresh(owner)
    st = _store(p)
    execute_seed(p, "55[Set] :: A=hello")
    execute_seed(p, "55[Set] :: K=keep")
    execute_seed(p, "86[Delete] :: A")
    p.save()
    from form.open import Program
    p2 = Program.load(owner=owner)
    st2 = _store(p2)
    _rec("deletion_survives_save_load",
         "A" not in st2.store and st2.store.get("K") == "keep",
         f"keys={sorted(st2.store)}")
    _cleanup(owner)

    # REAL_USER_PATH: the literal REPL, both surfaces.
    rc, store = _repl("D186ReplSeed",
                      "55[Set] :: A=hello\n86[Delete] :: A\n10[Keep]\n")
    _rec("repl_seed_delete_lands_in_saved_state",
         rc == 0 and "A" not in store,
         f"rc={rc} keys={sorted(store)}")
    rc, store = _repl("D186ReplEng",
                      "55[Set] :: A=hello\ndelete A\n10[Keep]\n")
    _rec("repl_english_delete_refused_in_saved_state",
         rc == 0 and store.get("A") == "hello",
         f"rc={rc} A={store.get('A')!r}")

    # Docs sync.
    from form.mandell.signatures import get_signature
    from form.mandell.dell_cards import DEEP_NOTES
    sig = get_signature(86)
    _rec("signature_failures_match_code",
         "delete_missing:empty" in sig.failures,
         sig.failures[:60])
    _rec("proof_card_carries_the_deep_note",
         86 in DEEP_NOTES and "NO_AUTHORITATIVE_RESULT" in DEEP_NOTES[86],
         DEEP_NOTES.get(86, "")[:60])

    ok = all(c for _, c, _ in RESULTS)
    for name, cond, detail in RESULTS:
        print(f"[{'ok' if cond else 'FAIL'}] {name} :: {detail}")
    n = sum(1 for _, c, _ in RESULTS if c)
    print(f"D1_DELL86_DELETE: {n}/{len(RESULTS)}")
    return ok


def smoke():
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
