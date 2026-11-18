"""R26 — DuoBeta ledger detail must survive whole (no silent 120 cut).

Director ruling 6974763716 on PR #427 (2026-11-18): a 200-character
DuoBeta evolution detail landed as 120. Preserve the whole string at
both producers and at save/load. Prove 119/120/121, Unicode, both
public ingestion paths, restart, and readability of old records.

Cut sites on main 44191a89 (all verified first-hand):
  * form/duobeta/growth.py        DuoBeta.evolve()      detail[:120]
  * form/mandell/duobeta_learn.py _append_learn_entry() detail[:120]
  * form/persist.py               duo_ledger save       detail[:120]
  * form/persist_rest.py          duo_ledger load       detail[:120]
    (the matrix named the first three; the load site is the fourth
    cut covered by the ruling's "at save/load" wording — lifting only
    the producers + save would be silently re-imposed at load.)
  * form/repl.py                  REPL `evolve <detail>` door pre-cut
    detail[:120] before calling Program.evolve() — a producer pre-cut
    on the real user path, the same shape Q-S2.2 removed for R16.
    Found during this repair; lifted with the others and named in
    the PR for the check pass.

Public ingestion paths exercised:
  A. Program.duo.evolve(detail)            (growth producer)
  B. duobeta_learn.propose(kind=<long>)    (learn producer; its ledger
     detail is constructed from the caller's kind string)

Restart = persist_rest.save -> persist_rest.load into a fresh Program
with an isolated state file (INTEGRATION evidence, same process).

Old-record readability: an envelope whose duo_ledger carries a legacy
120-char detail (the old truncated form) loads byte-for-byte — the
repair never fabricates or extends what an old record actually holds.

Run: python3 -m form.duobeta_detail_whole_test
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}"
          + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        raise AssertionError(name)


def _details(prog):
    return [e.detail for e in prog.duo.ledger]


def run_all():
    from form.open import open_program
    from form import persist_rest
    from form.mandell import duobeta_learn

    tmpdir = tempfile.mkdtemp(prefix="r26-detail-")
    owner = "R26DetailProbe"
    try:
        path = os.path.join(tmpdir, "state.json")
        prog = open_program(owner)
        base = len(prog.duo.ledger)

        # ── Path A: evolve() at the boundary lengths ──────────────────
        d119 = "a" * 119
        d120 = "b" * 120
        d121 = "c" * 121
        d200 = "d" * 200
        for d in (d119, d120, d121, d200):
            r = prog.duo.evolve(d)
            check(f"evolve({len(d)}) reports ok", r.get("ok") is True)
            check(f"evolve({len(d)}) returns the whole detail",
                  r.get("entry") == d,
                  f"got len {len(r.get('entry') or '')}")
        got = _details(prog)
        for d in (d119, d120, d121, d200):
            check(f"ledger holds evolve detail whole ({len(d)})", d in got)

        # Unicode: length is in characters; multi-byte text survives.
        uni = "é" * 100 + "—" * 50 + "🎵" * 60  # 210 chars
        r = prog.duo.evolve(uni)
        check("evolve(unicode 210) returns the whole detail",
              r.get("entry") == uni)
        check("ledger holds unicode detail whole", uni in _details(prog))

        # ── Path B: learn producer via the public propose() door ──────
        long_kind = "k" * 180
        res = duobeta_learn.propose(prog, long_kind, 7)
        check("propose(long kind) reports ok", res.get("ok") is True)
        expected = (f"LEARN PROPOSED {long_kind} dell=7 knowledge=None")
        check("learn ledger detail is whole (>120, uncut)",
              expected in _details(prog),
              f"expected len {len(expected)}; lens present: "
              f"{sorted({len(x) for x in _details(prog)})}")

        # ── Save / restart / load round-trip ──────────────────────────
        persist_rest.save(prog, path)
        with open(path, encoding="utf-8") as fh:
            envelope = json.load(fh)
        saved = [e.get("detail") for e in envelope.get("duo_ledger") or []]
        for d in (d121, d200, uni, expected):
            check(f"saved envelope holds detail whole ({len(d)})",
                  d in saved)

        prog2 = persist_rest.load(owner, path, activate=False)
        got2 = _details(prog2)
        for d in (d119, d120, d121, d200, uni, expected):
            check(f"reloaded ledger holds detail whole ({len(d)})",
                  d in got2)

        # ── Old-record readability ────────────────────────────────────
        # A legacy envelope: one entry already cut to exactly 120 by the
        # old code. It must load byte-for-byte (nothing fabricated), and
        # the loader must not re-cut a whole entry written by new code.
        legacy = "L" * 120
        whole = "W" * 200
        old_env = {
            "duo_generation": 2,
            "duo_ledger": [
                {"gen": 1, "detail": legacy, "ts": "2026-01-01T00:00:00Z",
                 "meta": {}},
                {"gen": 2, "detail": whole, "ts": "2026-01-01T00:01:00Z",
                 "meta": {}},
            ],
        }
        old_path = os.path.join(tmpdir, "legacy.json")
        # Load through the same restore helper the public load() uses,
        # on a fresh program, so the envelope stays minimal.
        prog3 = open_program(owner)
        persist_rest._restore_duo_ledger(prog3, old_env, 2)
        got3 = _details(prog3)
        check("legacy 120-char record loads byte-for-byte",
              legacy in got3)
        check("whole 200-char record is not re-cut at load",
              whole in got3)
        check("no fabricated entries on legacy load",
              len([d for d in got3 if d in (legacy, whole)]) == 2)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    print(f"R26-DETAIL-WHOLE: {sum(1 for _, c in RESULTS if c)}"
          f"/{len(RESULTS)} GREEN")


def smoke() -> bool:
    try:
        run_all()
        return True
    except Exception as e:
        print(f"R26-DETAIL-WHOLE SMOKE FAILED: {e}")
        return False


if __name__ == "__main__":
    run_all()
    sys.exit(0)
