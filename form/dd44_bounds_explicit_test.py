#!/usr/bin/env python3
"""DD-44 — C1.Bounds: loop bounds must be EXPLICIT; no silent 8.

Ace ruling (plan SS12.56, extended SS12.63a): running a loop
requires stating exactly how many iterations are wanted. If
the count is not specified, the loop ASKS (a structured
missing-input refusal carrying the full why); it never
quietly picks 8. DD-44 supersedes the default half of the
72-21 contract (PR #321, "loop bounds exact including
default 8" — bounds being exact stands; the silent default
goes).

Defect at base (probe-verified): bound_of(st) read st.limit
through validate_bound, which maps "" and "max" to 8, and
bound_of returned 8 even for an INVALID stored limit. A
While with a true condition and no Limit ran exactly 8
iterations. The setter shared the silence: a bare Limit
atom stored '8', and Limit "max" also stored '8'.

Contract after repair (loop-bound domain + its setter):
- bound_detail(st) resolves the stored limit as specified /
  unspecified / invalid. bound_of is REMOVED — no accessor
  may hand back a default the user never stated.
- A While/Until that WOULD iterate with an unspecified bound
  refuses: head error bound_unspecified, body occurrences
  receipt honest skips, nothing runs, the message carries
  the why. An invalid stored limit refuses invalid_limit.
- A loop whose condition already settles it (zero
  iterations) needs no bound and proceeds as today.
- A specified bound stays exact (Limit 3 -> 3 iterations,
  bound_reached, frame bound == the stated number).
- Dell 72: a bare Limit refuses limit_unspecified (it may
  not manufacture a value); "max" states the maximum
  (MAX_BOUND = 64); numerics exact; invalid and over-max
  still refuse invalid_limit (hard safety preserved).
- Frame stamps and leaf messages show the stated bound or
  "unspecified" — never a phantom 8.
- Out of scope (pinned unchanged as audit controls): Loop
  13's own receipted count grammar (bare = requested 1) and
  Compose's recursion cap; both are named domains for
  Q-DD44.2 / later circuits, not changed here.

Labels: PUBLIC_ENTRY_PATH (execute_seed) + one INTEGRATION
check (hand-set invalid stored limit). Hygiene: uuid
owners, exact-pattern cleanup, cleanup errors fail.
"""
from __future__ import annotations

import sys
import uuid
from pathlib import Path

REPO = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, REPO)

RESULTS = []
_CLEANUP_ERRORS = []
RUN = uuid.uuid4().hex[:8]
TAGS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def _mk(tag):
    from form.open import Program
    from form.mandell.core_ii_exec import attach
    TAGS.append(tag)
    p = Program(owner=f"DD44{tag}{RUN}")
    attach(p)
    return p


def _run(p, seed):
    from form.mandell.executor import execute_seed
    return execute_seed(p, seed)


def _recs(out, dell=None):
    rs = out.get("atom_results") or []
    if dell is not None:
        rs = [r for r in rs if r.get("dell") == dell]
    return rs


def _body_runs(out, dell=55):
    return [r for r in _recs(out, dell) if not r.get("skipped")]


def main():
    # ---------- loop domain: unspecified refuses ----------
    p = _mk("W1")
    out = _run(p, "65[While] :: true > 55[Set] :: tick=1 > 61[Join]")
    head = _recs(out, 65)
    body = _recs(out, 55)
    check("while.unspecified_refused_nothing_runs",
          bool(head) and head[0].get("ok") is False
          and head[0].get("error") == "bound_unspecified"
          and len(_body_runs(out)) == 0
          and all(r.get("skipped") for r in body)
          and "tick" not in p.core_ii.store
          and out.get("error") == "bound_unspecified",
          f"head={head} body={body} err={out.get('error')!r}")
    fr = p.core_ii.last_frame or {}
    check("while.frame_bound_not_phantom_8",
          fr.get("bound") != 8 and fr.get("status") == "fail",
          f"frame={ {k: fr.get(k) for k in ('status', 'bound', 'iterations')} }")

    p = _mk("U1")
    out = _run(p, "64[Until] :: false > 55[Set] :: tick=1 > 61[Join]")
    head = _recs(out, 64)
    check("until.unspecified_refused",
          bool(head) and head[0].get("ok") is False
          and head[0].get("error") == "bound_unspecified"
          and len(_body_runs(out)) == 0,
          f"head={head}")

    # ---------- zero-iteration needs no bound (controls) ----------
    p = _mk("W0")
    out = _run(p, "65[While] :: false > 55[Set] :: tick=1 > 61[Join]")
    fr = p.core_ii.last_frame or {}
    check("while.zero_iteration_no_bound_needed",
          out.get("ok") is True and len(_body_runs(out)) == 0
          and fr.get("status") == "zero",
          f"ok={out.get('ok')} frame={fr.get('status')}")
    p = _mk("U0")
    out = _run(p, "64[Until] :: true > 55[Set] :: tick=1 > 61[Join]")
    fr = p.core_ii.last_frame or {}
    check("until.already_true_no_bound_needed",
          out.get("ok") is True and len(_body_runs(out)) == 0
          and fr.get("status") == "zero",
          f"ok={out.get('ok')} frame={fr.get('status')}")

    # ---------- specified bounds stay exact (controls) ----------
    p = _mk("W3")
    _run(p, "72[Limit] :: 3")
    out = _run(p, "65[While] :: true > 55[Set] :: tick=1 > 61[Join]")
    fr = p.core_ii.last_frame or {}
    check("while.limit_3_exact",
          len(_body_runs(out)) == 3 and out.get("error") == "bound_reached"
          and fr.get("bound") == 3 and fr.get("iterations") == 3,
          f"runs={len(_body_runs(out))} frame={ {k: fr.get(k) for k in ('bound', 'iterations')} }")
    p = _mk("U2")
    _run(p, "72[Limit] :: 2")
    out = _run(p, "64[Until] :: false > 55[Set] :: tick=1 > 61[Join]")
    check("until.limit_2_exact",
          len(_body_runs(out)) == 2 and out.get("error") == "bound_reached",
          f"runs={len(_body_runs(out))} err={out.get('error')!r}")
    p = _mk("WC")
    _run(p, "72[Limit] :: 5")
    _run(p, "55[Set] :: go=1")
    out = _run(p, "65[store_go] > 86[Delete] :: go > 61[Join]")
    check("while.condition_clears_before_bound",
          out.get("ok") is True and not out.get("error"),
          f"ok={out.get('ok')} err={out.get('error')!r}")

    # ---------- invalid stored limit refuses (INTEGRATION) ----------
    p = _mk("WI")
    p.core_ii.limit = "banana"
    out = _run(p, "65[While] :: true > 55[Set] :: tick=1 > 61[Join]")
    head = _recs(out, 65)
    check("while.invalid_stored_limit_refused",
          bool(head) and head[0].get("ok") is False
          and head[0].get("error") == "invalid_limit"
          and len(_body_runs(out)) == 0,
          f"head={head}")

    # ---------- setter domain (Dell 72) ----------
    p = _mk("S1")
    r = _run(p, "72[Limit]")
    check("setter.bare_limit_refused",
          r.get("ok") is False and r.get("error") == "limit_unspecified"
          and p.core_ii.limit == "",
          f"ok={r.get('ok')} err={r.get('error')!r} limit={p.core_ii.limit!r}")
    p = _mk("S2")
    r = _run(p, "72[Limit] :: max")
    lr = p.core_ii.last_result or {}
    check("setter.max_states_maximum_64",
          r.get("ok") is True and p.core_ii.limit == "64"
          and lr.get("value") == 64,
          f"ok={r.get('ok')} limit={p.core_ii.limit!r} lr={lr.get('value')}")
    p = _mk("S3")
    r = _run(p, "72[Limit] :: 5")
    check("setter.numeric_exact",
          r.get("ok") is True and p.core_ii.limit == "5",
          f"limit={p.core_ii.limit!r}")
    p = _mk("S4")
    r = _run(p, "72[Limit] :: banana")
    check("setter.invalid_refused",
          r.get("ok") is False and r.get("error") == "invalid_limit"
          and p.core_ii.limit == "",
          f"err={r.get('error')!r}")
    r = _run(p, "72[Limit] :: 65")
    check("setter.over_max_refused_hard_safety",
          r.get("ok") is False and r.get("error") == "invalid_limit",
          f"err={r.get('error')!r}")

    # ---------- display honesty ----------
    p = _mk("D1")
    r = _run(p, "65[While] :: false")
    msgs = " ".join(r.get("messages") or [])
    check("leaf.while_message_no_phantom_bound",
          "bound=unspecified" in msgs and "bound=8" not in msgs,
          f"msgs={msgs[:120]!r}")

    # ---------- audit controls: named domains unchanged ----------
    p = _mk("A1")
    _run(p, "08[Create] :: Alpha")
    r = _run(p, "13[Loop]")
    msgs = " ".join(r.get("messages") or [])
    check("audit.loop13_grammar_unchanged",
          r.get("ok") is True and "requested 1, executed 1" in msgs,
          f"ok={r.get('ok')} msgs={msgs[:120]!r}")

    for tag in TAGS:
        _cleanup(tag)
    ok_n = sum(1 for _, c in RESULTS if c)
    print(f"DD44_BOUNDS_EXPLICIT: {ok_n}/{len(RESULTS)}")
    if _CLEANUP_ERRORS:
        print("CLEANUP ERRORS:", _CLEANUP_ERRORS)
        return 1
    return 0 if ok_n == len(RESULTS) else 1


def _cleanup(tag):
    from form.persist import _STATE_DIR, _safe_owner
    from form.dell_matrix.nursery import owner_nursery_path
    owner = f"DD44{tag}{RUN}"
    state = Path(_STATE_DIR)
    safe = _safe_owner(owner)
    cands = [state / f"program_{safe}.json",
             Path(owner_nursery_path(owner))]
    cands += list(state.glob(f"*{safe}*"))
    for pth in set(cands):
        try:
            if pth.is_dir():
                import shutil
                shutil.rmtree(pth)
            elif pth.exists():
                pth.unlink()
        except OSError as exc:
            _CLEANUP_ERRORS.append(f"{pth}: {exc}")


def smoke():
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
