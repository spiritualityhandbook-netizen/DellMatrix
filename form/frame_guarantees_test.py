#!/usr/bin/env python3
"""72-20 — Branch/Parallel/Sequence/Join reported guarantees:
set-wide recheck + the explicit no-true-concurrency contract.

Acceptance (original inventory): "Confirm execution order,
failure propagation, and Join verdicts. Do not claim true
concurrency if execution is sequential." Register remaining
action: "Set-wide guarantee recheck + explicit
no-true-concurrency contract statement."

Grounded guarantees (chain_exec.py + core_ii_exec.py, probed
at the public entry path before pinning):

- Sequence: the body executes in written order; the last
  writer wins shared state; a member failure does NOT stop
  the body (later members still run); the closing Join
  verdict reflects the body.
- Parallel: THE SAME sequential walk in listed order —
  deterministic across repeated runs (last listed writer
  wins). Its distinction from Sequence is failure CAPTURE:
  a sibling failure is recorded, the remaining siblings
  still run, the frame status becomes 'fail', and the chain
  error keeps the sibling's root cause. There is NO true
  concurrency: the execution modules contain no threading,
  asyncio, multiprocessing, or executor-pool primitives
  (source census pinned below), and the observable order is
  exactly the listed order every run.
- Branch: only the taken arm executes and mutates; the
  unchosen arm's occurrences are skipped receipts and never
  mutate, in both directions.
- Join: policy is the Join atom's label (default 'all'):
  'all' fails (join_fail) when any EXECUTED incoming result
  failed; 'any' passes when at least one executed result
  passed. Skipped receipts and prior Join verdicts never
  count as failures. An EMPTY executed child set is a
  successful Join under both policies (Step 11 settlement),
  including an orphan Join with no frame at all.

Contract defect found and repaired in this circuit: the
canonical registry row for Dell 62 (form/mandell/core_ii.py)
claimed manor "Execute independent operations concurrently"
with root "concurrent", and the generated proof card's
headline repeated the claim — while the card's own DEEP NOTE
and the proven behavior are sequential. The row now states
the true contract. (Manifest keywords are routing synonyms,
not contract claims, and are unchanged; see the Director
report's Q-72-20.2.)

Existing coverage (NOT duplicated): control_runtime_test
(frame mechanics and syntax), first_failure_provenance_test
(72-19, provenance compositions), step7/step11 suites (frame
receipt and Join settlement internals).

Labels: PUBLIC_ENTRY_PATH throughout (execute_seed).
Hygiene: uuid-unique owners; exact-pattern cleanup;
cleanup failures reported, never swallowed.
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


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def _fresh(tag):
    from form.open import open_program
    return open_program(f"T7220{tag}{RUN}")


def _run(tag, chain):
    from form.mandell.executor import execute_seed
    p = _fresh(tag)
    out = execute_seed(p, chain)
    return p, out


def _recs(out):
    return [(r.get("dell"), bool(r.get("ok", True)),
             r.get("error") or "", bool(r.get("skipped")))
            for r in (out.get("atom_results") or [])]


def _join_receipt(out):
    js = [r for r in (out.get("atom_results") or []) if r.get("dell") == 61]
    return js[-1] if js else None


def _cleanup(tag):
    from form.persist import _STATE_DIR, _safe_owner
    from form.dell_matrix.nursery import owner_nursery_path
    owner = f"T7220{tag}{RUN}"
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


TAGS = []


def main():
    # --- Sequence guarantees -------------------------------------
    tag = "S1"; TAGS.append(tag)
    p, out = _run(tag, "63[Sequence] > 55[Set] :: k=first "
                       "> 55[Set] :: k=second > 55[Set] :: other=x > 61[Join]")
    check("S1.written_order", [d for d, *_ in _recs(out)] == [63, 55, 55, 55, 61])
    check("S1.last_writer_wins", p.core_ii.store.get("k") == "second")
    check("S1.join_ok", (_join_receipt(out) or {}).get("ok") is True)
    check("S1.clean", out["ok"] and not out["partial"])

    tag = "S2"; TAGS.append(tag)
    p, out = _run(tag, "63[Sequence] > 55[Set] :: a=1 "
                       "> 86[Delete] :: seqmiss > 55[Set] :: b=2 > 61[Join]")
    check("S2.failure_does_not_stop_body",
          p.core_ii.store.get("b") == "2" and len(_recs(out)) == 5)
    jr = _join_receipt(out) or {}
    check("S2.join_verdict_fail", jr.get("ok") is False
          and jr.get("error") == "join_fail")
    check("S2.chain_error_is_leaf", out["error"] == "delete_missing:seqmiss")

    # --- Parallel guarantees: sequential, deterministic ---------
    for i in range(5):
        tag = f"P1{i}"; TAGS.append(tag)
        p, out = _run(tag, "62[Parallel] > 55[Set] :: k=A "
                           "> 55[Set] :: k=B > 55[Set] :: k=C > 61[Join]")
        check(f"P1.run{i}.listed_order_last_wins",
              p.core_ii.store.get("k") == "C"
              and [d for d, *_ in _recs(out)] == [62, 55, 55, 55, 61])

    tag = "P2"; TAGS.append(tag)
    p, out = _run(tag, "62[Parallel] > 55[Set] :: a=1 "
                       "> 86[Delete] :: parmiss > 55[Set] :: b=2 > 61[Join]")
    check("P2.capture_and_continue", p.core_ii.store.get("b") == "2")
    frames = [(f.get("kind"), f.get("status")) for f in (p.core_ii.frames or [])]
    check("P2.frame_status_fail", ("parallel", "fail") in frames, str(frames))
    jr = _join_receipt(out) or {}
    check("P2.join_verdict_fail", jr.get("ok") is False
          and jr.get("error") == "join_fail")
    check("P2.chain_error_keeps_root_cause",
          out["error"] == "delete_missing:parmiss")

    # --- Branch guarantees ---------------------------------------
    tag = "B1T"; TAGS.append(tag)
    p, out = _run(tag, "60[true] > 55[Set] :: taken=yes "
                       "> 59[Else] > 55[Set] :: untaken=no > 61[Join]")
    check("B1T.taken_mutates_unchosen_does_not",
          p.core_ii.store.get("taken") == "yes"
          and "untaken" not in p.core_ii.store)
    tag = "B1F"; TAGS.append(tag)
    p, out = _run(tag, "60[false] > 55[Set] :: taken=yes "
                       "> 59[Else] > 55[Set] :: untaken=no > 61[Join]")
    check("B1F.taken_mutates_unchosen_does_not",
          p.core_ii.store.get("untaken") == "no"
          and "taken" not in p.core_ii.store)

    # --- Join verdicts --------------------------------------------
    tag = "J1A"; TAGS.append(tag)
    p, out = _run(tag, "63[Sequence] > 55[Set] :: a=1 "
                       "> 86[Delete] :: jmiss > 61[Join]")
    jr = _join_receipt(out) or {}
    check("J1.policy_all_fails_on_mixed", jr.get("ok") is False
          and jr.get("error") == "join_fail")
    tag = "J1Y"; TAGS.append(tag)
    p, out = _run(tag, "63[Sequence] > 55[Set] :: a=1 "
                       "> 86[Delete] :: jmiss > 61[any]")
    jr = _join_receipt(out) or {}
    check("J1.policy_any_passes_on_mixed", jr.get("ok") is True,
          str(jr))
    check("J1.any_chain_still_reports_leaf",
          out["ok"] is False and out["error"] == "delete_missing:jmiss")

    for tag, chain in (("J2S", "63[Sequence] > 61[Join]"),
                       ("J2P", "62[Parallel] > 61[Join]"),
                       ("J2Y", "63[Sequence] > 61[any]")):
        TAGS.append(tag)
        p, out = _run(tag, chain)
        jr = _join_receipt(out) or {}
        check(f"{tag}.empty_child_set_join_ok",
              jr.get("ok") is True and out["ok"])

    tag = "J3"; TAGS.append(tag)
    p, out = _run(tag, "61[Join]")
    jr = _join_receipt(out) or {}
    check("J3.orphan_join_ok", jr.get("ok") is True and out["ok"])

    tag = "J4"; TAGS.append(tag)
    p, out = _run(tag, "60[true] > 55[Set] :: a=1 "
                       "> 59[Else] > 86[Delete] :: never > 61[Join]")
    jr = _join_receipt(out) or {}
    check("J4.skipped_receipts_never_fail_join",
          jr.get("ok") is True and out["ok"])

    # --- No-true-concurrency contract ------------------------------
    from form.mandell.core_ii import CORE_II
    row = CORE_II.get(62) or {}
    manor = (row.get("manor") or "")
    check("NC.registry_manor_states_sequential",
          "sequential" in manor.lower()
          and "operations concurrently" not in manor.lower(), manor)
    check("NC.registry_root_not_concurrent",
          (row.get("root") or "") != "concurrent", str(row.get("root")))
    cards = (Path(REPO) / "form" / "mandell" / "DELL_PROOF_CARDS.md"
             ).read_text(encoding="utf-8")
    check("NC.cards_carry_no_concurrency_claim",
          "concurrently" not in cards.lower())
    sec62 = ""
    lines = cards.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("### 62[Parallel]"):
            sec62 = "\n".join(lines[i:i + 4])
            break
    check("NC.card_note_states_sequential",
          "runs sequentially" in sec62, sec62[:80])
    banned = ("import threading", "import asyncio", "multiprocessing",
              "concurrent.futures", "ThreadPool", "ProcessPool")
    for mod in ("chain_exec.py", "core_ii_exec.py",
                "control_runtime.py", "executor.py"):
        src = (Path(REPO) / "form" / "mandell" / mod).read_text(
            encoding="utf-8")
        hits = [b for b in banned if b in src]
        check(f"NC.no_concurrency_primitives.{mod}", not hits, str(hits))

    for t in TAGS:
        _cleanup(t)
    check("cleanup.no_errors", not _CLEANUP_ERRORS, str(_CLEANUP_ERRORS))

    total = len(RESULTS)
    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"frame_guarantees_test: {passed}/{total} PASS")
    return 0 if passed == total else 1


def smoke():
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
