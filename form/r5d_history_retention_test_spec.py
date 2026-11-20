#!/usr/bin/env python3
"""R5-D failing-first — lossless safe history retention (GP-E05).

Authority: Director R5-C FINAL BINDING POLICY CHOICE 7026062701
(PR #498) adopting P1-P6; Director 7027509092 directing Uni to
"prepare reproducible failing-first tests and classify any
non-preflightable callers before asking for bounded implementation
authorization." Preparation package: Uni 7026727439 / R5D_PREP.

STATUS: FAILING-FIRST. Every contract check below FAILS on current
main (7027419) for the stated reason; the R5-D build turns them
green. Control checks (marked CONTROL) pass today and guard
against vacuous greens. NO product code is changed by this file.

Contract encoded (P1-P6):
- Cap: 10,000 entries AND 2,097,152 canonical bytes (atomic_write_json
  serialization: json.dumps indent=2 ensure_ascii=True, UTF-8),
  first-reached binds; exact-fit admitted; no eviction ever.
- Over-cap capture is a TYPED PRE-MUTATION refusal: it either raises
  an exception whose type name names the refusal, or returns a
  refusal receipt dict (ok=False). Silent eviction / silent no-op
  is a failure of this contract.
- Save writes full history; restore loads full history (no 24-entry
  cut, no 120-char entry cut, at save, restore, OR capture).
- Legacy over-budget files load whole, are marked LEGACY_OVER_BUDGET,
  unchanged-history saves write through byte-preserving history,
  new growth refuses LEGACY_OVER_BUDGET_NEW_ENTRY_REFUSED.
- sanitize_text (form.mandell.redaction) applies at capture for ALL
  note()/note_seed() strings; redaction-changed entries are marked
  NON-REPLAYABLE. Disclosed limits stand (keyword-free secrets can
  miss); this suite only asserts the keyword-shaped canaries.
- history_report states shown AND total truthfully.

Labels: INTEGRATION (Program + persist save/load path in-process).
Hygiene: uuid owners, tempfile save paths, exact-pattern cleanup;
cleanup errors fail the suite.
"""
from __future__ import annotations

import json
import sys
import tempfile
import uuid
from pathlib import Path

REPO = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, REPO)

RESULTS = []
_CLEANUP_ERRORS = []
RUN = uuid.uuid4().hex[:8]
OWNERS = []

CAP_ENTRIES = 10_000
CAP_BYTES = 2_097_152


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def _prog(tag):
    from form.open import open_program
    owner = f"R5D{tag}{RUN}"
    OWNERS.append(owner)
    return open_program(owner)


def _canonical_bytes(entries):
    return len(json.dumps(list(entries), indent=2,
                          ensure_ascii=True).encode("utf-8"))


def _refusal_seen(fn):
    """Run fn(); return (refused, exc_or_ret). A refusal is an
    exception naming the refusal, or a receipt dict ok=False."""
    try:
        ret = fn()
    except Exception as exc:  # noqa: BLE001 - refusal form under test
        name = type(exc).__name__
        msg = str(exc)
        if any(k in name for k in ("Refus", "History", "Cap", "Budget")) \
                or "LEGACY_OVER_BUDGET" in msg or "refus" in msg.lower():
            return True, exc
        return False, exc
    if isinstance(ret, dict) and ret.get("ok") is False:
        return True, ret
    return False, ret


def _tmpfile():
    fd, path = tempfile.mkstemp(suffix=".json")
    import os
    os.close(fd)
    return path


def main():
    from form.open import open_program  # noqa: F401
    from form.persist import serialize, save, load
    from form.mandell.redaction import sanitize_text
    from form.dell_matrix.needs import history_report

    # ── CONTROL: the sanitize authority itself redacts the canary ──
    check("control_sanitize_authority_redacts",
          "CANARYVAL" not in sanitize_text("password: CANARYVAL"),
          sanitize_text("password: CANARYVAL"))

    # ── T1 capture: 30 notes via note() are all retained, in order ──
    p = _prog("T1")
    for i in range(30):
        p.note(f"entry-{i:02d}")
    check("t1_capture_retains_30", list(p.history) ==
          [f"entry-{i:02d}" for i in range(30)],
          f"len={len(p.history)} (today: history_max=24 evicts)")

    # ── T1 save: serialize/save carries all 30; roundtrip keeps 30 ──
    p.history = [f"saved-{i:02d}" for i in range(30)]
    ser = serialize(p)
    check("t1_serialize_full_30", len(ser.get("history") or []) == 30,
          f"len={len(ser.get('history') or [])} (today: persist.py [-24:])")
    path = _tmpfile()
    save(p, path)
    q = load(p.owner, path)
    check("t1_roundtrip_full_30", list(q.history) ==
          [f"saved-{i:02d}" for i in range(30)],
          f"len={len(q.history)}")

    # ── T2 restore: 30 entries incl. a 200-char entry, byte-identical ──
    entries = [f"r-{i:02d}" for i in range(29)] + ["L" * 200]
    data = serialize(p)
    data["history"] = entries
    path2 = _tmpfile()
    Path(path2).write_text(json.dumps(data, indent=2, ensure_ascii=True),
                            encoding="utf-8")
    q2 = load(p.owner, path2)
    check("t2_restore_full_long_entry", list(q2.history) == entries,
          f"len={len(q2.history)} lastlen="
          f"{len(q2.history[-1]) if q2.history else 0} "
          f"(today: persist_rest.py [:120] + [-24:])")

    # ── T2b note_seed label: >40-char label retained in full ──
    p2b = _prog("T2B")
    long_label = "label-" + "x" * 60
    p2b.note_seed(9, "Show", long_label)
    check("t2b_note_seed_label_full", any(long_label in h
          for h in p2b.history),
          f"history={list(p2b.history)} (today: note_seed label [:40] cut)")

    # ── T3a exact-fit: exactly 10,000 entries admitted ──
    p3 = _prog("T3")
    for i in range(CAP_ENTRIES):
        p3.note(f"e{i}")
    check("t3_exact_fit_10000_admitted", len(p3.history) == CAP_ENTRIES,
          f"len={len(p3.history)}")

    # ── T3b/T4 over-cap: typed refusal, state byte-identical ──
    before_hist = list(p3.history)
    before_ser = serialize(p3)
    refused, how = _refusal_seen(lambda: p3.note("one-too-many"))
    check("t3_over_cap_typed_refusal", refused, f"how={how!r}")
    check("t4_refusal_atomicity", list(p3.history) == before_hist
          and serialize(p3) == before_ser,
          "history/serialized state must be unchanged after refusal")

    # ── T3c canonical bytes bind before raw count does ──
    p3c = _prog("T3C")
    refused_c = False
    for _ in range(2000):
        refused_c, _ = _refusal_seen(lambda: p3c.note("漢" * 400))
        if refused_c:
            break
    check("t3c_canonical_byte_cap_refuses", refused_c,
          "CJK entries: canonical bytes exceed cap far below 10k entries")
    check("t3c_history_within_canonical_cap",
          _canonical_bytes(p3c.history) <= CAP_BYTES,
          f"bytes={_canonical_bytes(p3c.history)}")

    # ── T7 legacy: >cap file loads whole, marked, write-through, ──
    # ── growth refused ──
    legacy = [f"leg-{i:05d}" for i in range(CAP_ENTRIES + 50)]
    data7 = serialize(p)
    data7["history"] = legacy
    path7 = _tmpfile()
    Path(path7).write_text(json.dumps(data7, indent=2, ensure_ascii=True),
                           encoding="utf-8")
    try:
        q7 = load(p.owner, path7)
        loaded_legacy = list(q7.history)
        load_err = None
    except Exception as exc:  # noqa: BLE001
        q7, loaded_legacy, load_err = None, [], exc
    check("t7_legacy_loads_whole", loaded_legacy == legacy,
          f"len={len(loaded_legacy)} err={load_err!r}")
    if q7 is not None:
        marker = getattr(q7, "history_legacy_over_budget", False) \
            or "LEGACY_OVER_BUDGET" in json.dumps(serialize(q7),
                                                  ensure_ascii=True)
        check("t7_legacy_marked", bool(marker),
              "LEGACY_OVER_BUDGET marker absent")
        path7b = _tmpfile()
        save(q7, path7b)
        written = json.loads(Path(path7b).read_text(encoding="utf-8"))
        check("t7_legacy_write_through", written.get("history") == legacy,
              f"written len={len(written.get('history') or [])}")
        refused7, _ = _refusal_seen(lambda: q7.note("new-growth"))
        check("t7_legacy_growth_refused", refused7
              and list(q7.history) == legacy,
              "new entry on legacy-over-budget must refuse pre-mutation")

    # ── T8 sanitize-at-capture on ordinary note / note_seed ──
    p8 = _prog("T8")
    p8.note("password: CANARYVAL note")
    p8.note_seed(9, "Show", "token: CANARYVAL seed")
    surfaces = {
        "history": "\n".join(p8.history),
        "serialized": json.dumps(serialize(p8), ensure_ascii=True),
        "macro_seed": p8.macro_seed(5),
        "replay": "\n".join(p8.replay(5)),
    }
    for sname, text in surfaces.items():
        check(f"t8_canary_absent_{sname}", "CANARYVAL" not in text,
              "keyword-shaped secret must be redacted at capture (P5)")
    marked = any("NON-REPLAYABLE" in str(h) for h in p8.history) \
        or bool(getattr(p8, "history_non_replayable", None))
    check("t8_redacted_entries_marked_non_replayable", marked,
          "redaction-changed entries must carry NON-REPLAYABLE marking")

    # ── T10 history_report: shown AND total ──
    p10 = _prog("T10")
    p10.history = [f"h{i}" for i in range(30)]
    first = history_report(p10, 16)[0]
    check("t10_report_shows_total_and_shown",
          "30" in first and "16" in first, f"first line: {first!r}")

    _cleanup_all()
    check("cleanup_clean", not _CLEANUP_ERRORS,
          "; ".join(_CLEANUP_ERRORS))
    ok_n = sum(1 for _, ok in RESULTS if ok)
    print(f"R5D {ok_n}/{len(RESULTS)} PASS")
    return 0 if ok_n == len(RESULTS) else 1


def _cleanup_all():
    from form.persist import _STATE_DIR, _safe_owner
    from form.dell_matrix.nursery import owner_nursery_path
    state = Path(_STATE_DIR)
    for owner in OWNERS:
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
