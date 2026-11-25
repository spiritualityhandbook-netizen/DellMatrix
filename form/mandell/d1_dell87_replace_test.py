#!/usr/bin/env python3
"""D1 deepening circuit 7 — Dell 87 (Replace) deep contract.

Derived from spectrum_ops.apply_spectrum (n==87) and its
typed signature (roles old required, new optional):

  old, new = lab.partition(">"), both stripped
  old not in store       -> ok=False "replace_missing:{old}"
                            (the bare form reports
                            "replace_missing:" with empty old)
  new occupied (and != old)
                         -> ok=False "replace_occupied:{new}",
                            ZERO mutation — the MPC-012 §0 /
                            MPC-011 J-decision recorded in the
                            executor's own comment. This is the
                            deliberate contrast with Dell 85
                            (Move), which overwrites silently.
  otherwise              -> store[new or old] =
                            store.pop(old): identity rename,
                            publishing a matched result cell
                            (value=result_key, source="replace")
  new empty, or new == old -> no-op success under the
                            original key (legacy fallback)

The occupied-refusal core is also covered by
dell87_refusal_test (including its zero-snapshot check);
this suite proves the rest of the contract around it and
syncs the signature, whose failures text previously named
only replace_missing and whose derived_from pointed at a
stale line range. dell87's refusal lineage matters: an
MPC-era decision with a live computational referent.

English: Replace is in the blocked set (blocked_with_reason,
operand-confirmation policy) at the route and the REPL;
the REPL user path is the Mandell seed line. Renames
persist.

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

    owner = "D187Seed"
    p = _fresh(owner)
    st = _store(p)
    execute_seed(p, "55[Set] :: A=hello")
    r = execute_seed(p, "87[Replace] :: A>B")
    lr = st.last_result or {}
    _rec("replace_renames_and_publishes",
         r.get("ok") and st.store.get("B") == "hello"
         and "A" not in st.store
         and lr.get("value") == "B" and lr.get("source") == "replace"
         and lr.get("matched") is True,
         f"ok={r.get('ok')} B={st.store.get('B')!r} lr={lr.get('value')!r}")
    execute_seed(p, "55[Set] :: C=see")
    r = execute_seed(p, "87[Replace] :: B>C")
    lr = st.last_result or {}
    _rec("occupied_destination_refuses_with_zero_mutation",
         not r.get("ok") and r.get("error") == "replace_occupied:C"
         and st.store.get("B") == "hello" and st.store.get("C") == "see"
         and lr.get("matched") is False
         and lr.get("error") == "replace_occupied:C",
         f"error={r.get('error')} B={st.store.get('B')!r} "
         f"C={st.store.get('C')!r}")
    # The deliberate sibling contrast: Move overwrites the
    # same occupied destination without refusing.
    r = execute_seed(p, "85[Move] :: B>C")
    _rec("move_contrast_overwrites_where_replace_refuses",
         r.get("ok") and st.store.get("C") == "hello"
         and "B" not in st.store,
         f"ok={r.get('ok')} C={st.store.get('C')!r}")
    r = execute_seed(p, "87[Replace] :: Ghost>X")
    _rec("replace_missing_fails",
         not r.get("ok") and r.get("error") == "replace_missing:Ghost",
         f"error={r.get('error')}")
    r = execute_seed(p, "87[Replace]")
    _rec("bare_replace_reports_empty_old",
         not r.get("ok") and r.get("error") == "replace_missing:",
         f"error={r.get('error')!r}")
    execute_seed(p, "55[Set] :: D=dee")
    r1 = execute_seed(p, "87[Replace] :: D>")
    lr = st.last_result or {}
    r2 = execute_seed(p, "87[Replace] :: D>D")
    _rec("empty_new_and_same_name_are_noop_successes",
         r1.get("ok") and r2.get("ok") and st.store.get("D") == "dee"
         and lr.get("value") == "D",
         f"r1={r1.get('ok')} r2={r2.get('ok')} lr={lr.get('value')!r}")
    r = execute_seed(p, '87[Replace](old="D", new="Final")')
    _rec("typed_args_replace",
         r.get("ok") and st.store.get("Final") == "dee"
         and "D" not in st.store,
         f"ok={r.get('ok')} Final={st.store.get('Final')!r}")
    _cleanup(owner)

    owner = "D187Int"
    p = _fresh(owner)
    st = _store(p)
    st.store["L"] = [1, 2]
    ref = st.store["L"]
    execute_seed(p, "87[Replace] :: L>M")
    _rec("identity_not_copy",
         st.store.get("M") is ref and "L" not in st.store,
         f"same_object={st.store.get('M') is ref}")
    _cleanup(owner)

    # English: blocked set.
    owner = "D187Eng"
    p = _fresh(owner)
    st = _store(p)
    execute_seed(p, "55[Set] :: M=mval")
    r = _english(p, "replace M with Done")
    _rec("english_replace_blocked_with_reason",
         not r.ok and not r.routed
         and "blocked_with_reason" in (r.error or "")
         and st.store.get("M") == "mval" and "Done" not in st.store,
         f"routed={r.routed} error={(r.error or '')[:44]}")
    _cleanup(owner)

    # Persistence.
    owner = "D187Persist"
    p = _fresh(owner)
    st = _store(p)
    execute_seed(p, "55[Set] :: A=hello")
    execute_seed(p, "87[Replace] :: A>B")
    p.save()
    from form.open import Program
    p2 = Program.load(owner=owner)
    st2 = _store(p2)
    _rec("rename_survives_save_load",
         st2.store.get("B") == "hello" and "A" not in st2.store,
         f"B={st2.store.get('B')!r}")
    _cleanup(owner)

    # REAL_USER_PATH: the literal REPL, both surfaces.
    rc, store = _repl(
        "D187ReplSeed",
        "55[Set] :: A=hello\n87[Replace] :: A>B\n10[Keep]\n")
    _rec("repl_seed_replace_lands_in_saved_state",
         rc == 0 and store.get("B") == "hello" and "A" not in store,
         f"rc={rc} B={store.get('B')!r}")
    rc, store = _repl(
        "D187ReplEng",
        "55[Set] :: A=hello\nreplace A with B\n10[Keep]\n")
    _rec("repl_english_replace_refused_in_saved_state",
         rc == 0 and store.get("A") == "hello" and "B" not in store,
         f"rc={rc} A={store.get('A')!r}")

    # Docs sync.
    from form.mandell.signatures import get_signature
    from form.mandell.dell_cards import DEEP_NOTES
    sig = get_signature(87)
    _rec("signature_failures_match_code",
         "replace_occupied" in sig.failures
         and "replace_missing" in sig.failures,
         sig.failures[:60])
    _rec("proof_card_carries_the_deep_note",
         87 in DEEP_NOTES and "replace_occupied" in DEEP_NOTES[87],
         DEEP_NOTES.get(87, "")[:60])

    ok = all(c for _, c, _ in RESULTS)
    for name, cond, detail in RESULTS:
        print(f"[{'ok' if cond else 'FAIL'}] {name} :: {detail}")
    n = sum(1 for _, c, _ in RESULTS if c)
    print(f"D1_DELL87_REPLACE: {n}/{len(RESULTS)}")
    return ok


def smoke():
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
