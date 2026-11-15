#!/usr/bin/env python3
"""SYS-C29 — Nursery words bound: no silent truncation, explicit refusal.

The defect (failing-first receipt in
director-reports/SYSTEM_002_SYSC29_CIRCUIT_2026-11-15.md): at the
pre-repair head, Nursery.add() stored words=words[:240], silently
destroying content the system admits — the inference dock admits words
up to 5,000 chars (inference_dock.MAX_WORDS_CHARS) and refuses beyond
by explicit error. A 300-char, a 5,000-char, and a 300-char unicode
words all round-tripped at 240 chars with no error raised.

This suite pins the repaired contract at the Nursery public path
(Nursery.load -> add -> save -> fresh load):

  W1  300-char ascii words round-trip exactly.
  W2  5,000-char words (the admitted maximum) round-trip exactly.
  W3  300-char unicode words round-trip exactly (chars, not bytes).
  W4  boundary: 240-char and 241-char words both round-trip exactly
      (241 is the first length the old cut destroyed).
  W5  5,001-char words are refused with NurseryWordsError BEFORE any
      mutation: in-memory proposals unchanged, on-disk bytes
      byte-identical, fresh load unchanged.
  W6  legacy record: a pre-written on-disk record whose words are
      exactly 240 chars (the shape the old cut produced) loads intact
      and round-trips unchanged through a save driven by a later add.
  W7  crash/reload: after save, a FRESH OS PROCESS loads the file and
      every proposal's complete record compares exactly.

State hygiene: every nursery file lives in a per-case temp directory;
the real form/state is never used for proposal data.
Labels: INTEGRATION (W7's fresh-process load is CROSS_PROCESS for the
reload leg).
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, REPO)

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def _words_ascii(n):
    return ("alpha beta gamma delta epsilon " * (n // 32 + 1))[:n]


def _words_unicode(n):
    return ("héllo wörld — ünïcode 🌱 " * (n // 24 + 1))[:n]


def _case_dir():
    tmp = tempfile.mkdtemp(prefix="sysc29_")
    return tmp, os.path.join(tmp, "nursery_sysc29.json")


def _roundtrip(path, label, words):
    """add() on a fresh-loaded nursery, then exact-compare in memory
    and after a fresh load. Returns the proposal id."""
    from form.dell_matrix.nursery import Nursery
    n = Nursery.load(path)
    p = n.add(label, words=words)
    in_mem = n.proposals[p.id].words
    fresh = Nursery.load(path)
    on_disk = fresh.proposals[p.id].words if p.id in fresh.proposals else None
    return p.id, in_mem, on_disk


# ---------------------------------------------------------------- W1-W4
def case_roundtrips():
    tmp, path = _case_dir()
    try:
        w300 = _words_ascii(300)
        assert len(w300) == 300
        pid, in_mem, on_disk = _roundtrip(path, "Ascii Three Hundred", w300)
        check("W1.ascii300_exact", in_mem == w300 and on_disk == w300,
              f"len(in)={len(in_mem or '')} len(disk)={len(on_disk or '')}")

        w5000 = "0123456789" * 500
        assert len(w5000) == 5000
        pid, in_mem, on_disk = _roundtrip(path, "Admitted Maximum", w5000)
        check("W2.admitted5000_exact", in_mem == w5000 and on_disk == w5000,
              f"len(in)={len(in_mem or '')} len(disk)={len(on_disk or '')}")

        wuni = _words_unicode(300)
        assert len(wuni) == 300
        pid, in_mem, on_disk = _roundtrip(path, "Unicode Three Hundred", wuni)
        check("W3.unicode300_exact", in_mem == wuni and on_disk == wuni,
              f"len(in)={len(in_mem or '')} len(disk)={len(on_disk or '')}")

        w240, w241 = "a" * 240, "b" * 241
        _p1, im1, od1 = _roundtrip(path, "Boundary Two Forty", w240)
        _p2, im2, od2 = _roundtrip(path, "Boundary Two Forty One", w241)
        check("W4.boundary240_241_exact",
              im1 == w240 and od1 == w240 and im2 == w241 and od2 == w241,
              f"240:{len(od1 or '')} 241:{len(od2 or '')}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------- W5
def case_refusal_no_mutation():
    from form.dell_matrix.nursery import Nursery, NurseryWordsError
    tmp, path = _case_dir()
    try:
        n = Nursery.load(path)
        seed = n.add("Seed Idea", words="seed words")
        with open(path, "rb") as f:
            bytes_before = f.read()
        count_before = len(n.proposals)
        try:
            n.add("Oversize Idea", words="z" * 5001)
            outcome = "no-raise"
        except NurseryWordsError:
            outcome = "words-error"
        except Exception as e:  # noqa: BLE001
            outcome = f"other:{type(e).__name__}"
        check("W5.refused_explicitly", outcome == "words-error", outcome)
        check("W5.no_inmemory_mutation",
              len(n.proposals) == count_before
              and list(n.proposals) == [seed.id],
              f"count={len(n.proposals)}")
        with open(path, "rb") as f:
            bytes_after = f.read()
        check("W5.no_disk_mutation", bytes_after == bytes_before,
              f"bytes {len(bytes_before)} -> {len(bytes_after)}")
        fresh = Nursery.load(path)
        check("W5.fresh_load_unchanged",
              len(fresh.proposals) == count_before
              and fresh.proposals[seed.id].words == "seed words")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------- W6
def case_legacy_record():
    from form.dell_matrix.nursery import Nursery, DISPOSITION_SECTION_KEY
    tmp, path = _case_dir()
    try:
        legacy_words = "w" * 240
        legacy = {
            "id": "legacy_idea_0001",
            "label": "Legacy Idea",
            "words": legacy_words,
            "kind": "new",
            "parents": [],
            "affinity": 0.0,
            "reason": "pre-repair record",
            "created": "2026-10-01T00:00:00Z",
            "status": "pending",
            "origin": "",
            "detail": "",
            "goals": [],
        }
        payload = {"legacy_idea_0001": legacy, DISPOSITION_SECTION_KEY: {}}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f)
        n = Nursery.load(path)
        check("W6.legacy_loads_intact",
              n.proposals["legacy_idea_0001"].words == legacy_words,
              f"len={len(n.proposals['legacy_idea_0001'].words)}")
        # A later add drives a full save; the legacy record must
        # round-trip through the repaired code byte-exact in content.
        new_words = _words_ascii(1000)
        p = n.add("Post Repair Idea", words=new_words)
        fresh = Nursery.load(path)
        check("W6.legacy_roundtrips_through_save",
              fresh.proposals["legacy_idea_0001"].words == legacy_words
              and fresh.proposals["legacy_idea_0001"].label == "Legacy Idea"
              and fresh.proposals[p.id].words == new_words,
              f"legacy len={len(fresh.proposals['legacy_idea_0001'].words)} "
              f"new len={len(fresh.proposals[p.id].words)}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------- W7
_FRESH_DUMP = r"""
import json, sys
sys.path.insert(0, %(REPO)r)
from form.dell_matrix.nursery import Nursery
n = Nursery.load(sys.argv[1])
print(json.dumps({k: p.to_dict() for k, p in n.proposals.items()},
                 sort_keys=True, ensure_ascii=False))
"""


def case_crash_reload_fresh_process():
    from form.dell_matrix.nursery import Nursery
    tmp, path = _case_dir()
    try:
        n = Nursery.load(path)
        n.add("Reload Alpha", words=_words_ascii(300))
        n.add("Reload Beta", words=_words_unicode(500),
              origin="dock:test:model", detail="d" * 100,
              goals=["goal one"])
        expected = {k: p.to_dict()
                    for k, p in Nursery.load(path).proposals.items()}
        out = subprocess.run(
            [sys.executable, "-c", _FRESH_DUMP % {"REPO": REPO}, path],
            cwd=REPO, capture_output=True, text=True, timeout=120)
        got = json.loads(out.stdout.strip().splitlines()[-1])
        check("W7.fresh_process_exact_compare", got == expected,
              f"proposals={sorted(got)} rc={out.returncode}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    case_roundtrips()
    case_refusal_no_mutation()
    case_legacy_record()
    case_crash_reload_fresh_process()
    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"nursery_words_bound_test: {passed}/{len(RESULTS)} PASS")
    return 0 if passed == len(RESULTS) else 1


def smoke() -> bool:
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
