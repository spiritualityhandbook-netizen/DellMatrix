"""Q1 / J-19 C-B — duplicate-import durable witness + stale-writer
save boundary (Director design ruling 7136749722; Keeper SCOPED
DESIGN CHALLENGE PASS 7202299383; Director FINAL BUILD CLEARANCE
7203152620).

Contract proven here (PROOF_SPEC §1–§3, §6):

- DUPLICATE import: the durable witness verifies the full
  three-leg composition (live proposal + matching seed + receipts)
  from the canonical files, and the import returns the original
  witness {ok, pid=<original>, replay=True, receipts_hash, lint,
  origin, journal_retained=False} with ZERO writes.
- LEGITIMATE NEW import: no verified witness -> the full fence
  runs and the packet lands fresh with replay=False and a fresh
  pid. Identity is the full tuple: a packet differing only in
  manifest.created, or in one receipt field, is a NEW identity.
- DISPOSAL: reject disposes the proposal; the seed + receipt
  records stay durable (M3) but no longer witness — a re-import
  lands NEW, and the next duplicate replays against the NEW
  live witness.
- STALE WRITER (X4): a Program loaded before another writer's
  import completed must not silently drop the import's seed /
  receipt records at its ordinary save — the save preserves the
  unseen durable records (in-process and cross-process shapes).
  When preservation cannot be established (durable read fails —
  including a PRESENT exchange section whose shell is malformed,
  which is unreadable state and never an empty section;
  Director correction 7203516785), the save refuses typed
  (StaleWriterSaveError) before any byte changes.
- CAPACITY (Critic P1, review 4713412892): preservation is
  verified against the serializer's bounded retention — if the
  outgoing section cannot retain EVERY live-bound record (a
  full section of non-live records plus carried live records
  past the cap, adverse timestamp tie), the stale save refuses
  typed pre-byte instead of dropping the live records at
  serialization.
- INDEPENDENT OWNER: the witness is owner-scoped — the same
  packet imported by a second owner lands fresh there, and that
  owner's saves never touch the first owner's state.
- RECOVERY AGREEMENT: an import completed through load-boundary
  recovery (journal retained at landing, resolved at load) is
  the SAME import to the witness — a later duplicate replays.

Labels: INTEGRATION (real Program/Nursery/persist paths, real
canonical files) + one CROSS_PROCESS case (Q6, the X4 shape).
"""
from __future__ import annotations

import glob
import json
import os
import shutil
import subprocess
import sys
import time

RESULTS: list = []


def _rec(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, bool(ok), detail))


def _cleanup(owner: str) -> None:
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "state")
    if not os.path.isdir(base):
        return
    names = []
    for pat in (f"program_{owner}.json", f"nursery_{owner}.json",
                f"checkpoint_{owner}_*", f"confirm_{owner}.journal.json",
                f"checkpoint_{owner}.journal.json", f"gen_{owner}_*",
                f"current_{owner}.json",
                f"exchange_import_{owner}.journal.json"):
        names.extend(glob.glob(os.path.join(base, pat)))
    errors = []
    for name in names:
        try:
            os.remove(name)
        except OSError as e:
            errors.append(f"{name}: {e}")
    for d in glob.glob(os.path.join(base, f"ideas_{owner}*")):
        if os.path.isdir(d):
            try:
                shutil.rmtree(d)
            except OSError as e:
                errors.append(f"{d}: {e}")
    if errors:
        raise RuntimeError(
            f"cleanup failed for owner {owner}: {errors}")


def _packet(label="q1-idea", keep="Q1-KEEP",
            created="2026-11-26T00:00:00Z", receipt_result="r-a"):
    return {
        "version": 1,
        "seed": {"label": label, "chain": "chain-q1", "keep": keep},
        "manifest": {"author_origin": "q1:origin", "created": created,
                     "registry": "core1:00-50,core2:51-99",
                     "requirements": ["req-q1"]},
        "receipts": [
            {"origin": "q1:org-a", "guess": "g-a", "test_method": "m-a",
             "result": receipt_result, "mirror": "mi-a",
             "outcome": "o-a"},
            {"origin": "q1:org-b", "guess": "g-b", "test_method": "m-b",
             "result": "r-b", "mirror": "mi-b", "outcome": "o-b"},
        ],
    }


def _file_bytes(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()


class _BrokenJournalUnlink:
    """os.remove wrapper: fails only for the import journal file
    (the DIR-F12 injection, reused for the recovery case)."""

    def __enter__(self):
        self._real = os.remove

        def guarded(path, *a, **k):
            if "exchange_import_" in str(path) \
                    and str(path).endswith(".journal.json"):
                raise OSError("injected journal unlink failure")
            return self._real(path, *a, **k)

        os.remove = guarded
        return self

    def __exit__(self, *exc):
        os.remove = self._real
        return False


def main() -> bool:
    from form.open import Program
    from form import persist_rest
    from form.persist import _path as _program_path
    from form.dell_matrix import exchange
    from form.dell_matrix.nursery import owner_nursery_path
    try:
        from form.persist_rest import StaleWriterSaveError
    except ImportError:
        StaleWriterSaveError = None

    def label_count(p, label):
        return sum(1 for pr in p.nursery.proposals.values()
                   if pr.label == label)

    # ---- Q1/Q2/Q3: duplicate replay, fresh landing, tuple pins.
    owner = "Q1Dup"
    _cleanup(owner)
    p = Program(owner=owner)
    imp1 = exchange.import_packet(p, _packet())
    pid1 = imp1.get("pid")
    _rec("Q1: first import lands fresh (replay=False)",
         imp1.get("ok") is True and imp1.get("replay") is False
         and bool(pid1), str(imp1))
    prog_bytes = _file_bytes(_program_path(owner))
    nurs_bytes = _file_bytes(owner_nursery_path(owner))
    imp2 = exchange.import_packet(p, _packet())
    _rec("Q1: duplicate import returns the original witness",
         imp2.get("ok") is True and imp2.get("replay") is True
         and imp2.get("pid") == pid1
         and imp2.get("journal_retained") is False
         and bool(imp2.get("receipts_hash"))
         and imp2.get("lint") is not None, str(imp2))
    _rec("Q1: duplicate lands NO second copy",
         label_count(p, "q1-idea") == 1
         and len([e for e in p.exchange_seeds.values()
                  if e.get("pid") == pid1]) == 1
         and len(exchange.receipts_for(p, pid1)) == 2)
    _rec("Q1: replay performed ZERO writes",
         _file_bytes(_program_path(owner)) == prog_bytes
         and _file_bytes(owner_nursery_path(owner)) == nurs_bytes)
    imp3 = exchange.import_packet(
        p, _packet(label="q1-idea-two", keep="Q1-KEEP-2"))
    _rec("Q2: a different packet lands fresh with a new pid",
         imp3.get("ok") is True and imp3.get("replay") is False
         and imp3.get("pid") not in (None, pid1)
         and label_count(p, "q1-idea-two") == 1, str(imp3))
    imp4 = exchange.import_packet(
        p, _packet(created="2026-11-27T00:00:00Z"))
    _rec("Q3: created-only difference is a NEW identity (E5)",
         imp4.get("ok") is True and imp4.get("replay") is False
         and imp4.get("pid") != pid1, str(imp4))
    imp5 = exchange.import_packet(p, _packet(receipt_result="r-a2"))
    _rec("Q3: one receipt field difference is NEW (E4)",
         imp5.get("ok") is True and imp5.get("replay") is False
         and imp5.get("pid") != pid1, str(imp5))
    _cleanup(owner)

    # ---- Q4: disposal breaks the witness; re-import lands new;
    # the disposed import's records stay durable (M3).
    owner = "Q1Dispose"
    _cleanup(owner)
    p = Program(owner=owner)
    imp1 = exchange.import_packet(p, _packet())
    pid1 = imp1["pid"]
    p.nursery.reject(pid1)
    imp2 = exchange.import_packet(p, _packet())
    pid2 = imp2.get("pid")
    _rec("Q4: re-import after reject lands NEW (no witness)",
         imp2.get("ok") is True and imp2.get("replay") is False
         and pid2 not in (None, pid1), str(imp2))
    imp3 = exchange.import_packet(p, _packet())
    _rec("Q4: next duplicate replays against the NEW witness",
         imp3.get("ok") is True and imp3.get("replay") is True
         and imp3.get("pid") == pid2, str(imp3))
    p.nursery.clear_rejected()
    st = exchange._durable_import_state(owner, pid1)
    _rec("Q4: disposed import's seed + receipts stay durable (M3)",
         st["proposal_present"] is False and st["seed_present"]
         and st["receipts_count"] == 2, str(st))
    _cleanup(owner)

    # ---- Q5: stale writer, in-process (X4 shape).
    owner = "Q1Stale"
    _cleanup(owner)
    stale = Program(owner=owner)
    importer = Program(owner=owner)
    imp = exchange.import_packet(importer, _packet())
    pid = imp["pid"]
    stale.save()
    st = exchange._durable_import_state(owner, pid)
    _rec("Q5: stale save preserves the completed import (no hybrid)",
         st["proposal_present"] and st["seed_present"]
         and st["receipts_count"] == 2, str(st))
    fresh = persist_rest.load(owner, activate=False)
    _rec("Q5: fresh load sees payload + receipts intact",
         exchange.seed_payload_for(fresh, pid) is not None
         and len(exchange.receipts_for(fresh, pid)) == 2)
    _cleanup(owner)

    # ---- Q6: stale writer, cross-process (the X4 case itself).
    owner = "Q1StaleX"
    _cleanup(owner)
    clone = os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))
    state = os.path.join(clone, "form", "state")
    ready = os.path.join(state, "q1x.ready")
    go = os.path.join(state, "q1x.go")
    for f in (ready, go):
        if os.path.exists(f):
            os.remove(f)
    child_code = (
        "import json, os, sys, time\n"
        "from form.open import Program\n"
        f"p = Program(owner={owner!r})\n"
        f"open({ready!r}, 'w').write('ready')\n"
        "t0 = time.time()\n"
        f"while not os.path.exists({go!r}):\n"
        "    if time.time() - t0 > 120: sys.exit(3)\n"
        "    time.sleep(0.05)\n"
        "p.save()\n"
        "print(json.dumps({'saved': True}))\n")
    env = dict(os.environ, PYTHONPATH=clone,
               PYTHONDONTWRITEBYTECODE="1")
    proc = subprocess.Popen(
        [sys.executable, "-c", child_code], cwd=clone, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        t0 = time.time()
        while not os.path.exists(ready):
            if time.time() - t0 > 120:
                raise TimeoutError("stale child never ready")
            time.sleep(0.05)
        importer = Program(owner=owner)
        imp = exchange.import_packet(importer, _packet())
        pid = imp["pid"]
        open(go, "w").write("go")
        out, err = proc.communicate(timeout=300)
    finally:
        if proc.poll() is None:
            proc.kill()
        for f in (ready, go):
            if os.path.exists(f):
                os.remove(f)
    sj = json.loads(out.strip().splitlines()[-1]) if out.strip() \
        else {}
    _rec("Q6: cross-process stale child saved without error",
         sj.get("saved") is True, f"{sj} stderr={err[-200:]}")
    st = exchange._durable_import_state(owner, pid)
    _rec("Q6: X4 hybrid does NOT recur (import fully preserved)",
         st["proposal_present"] and st["seed_present"]
         and st["receipts_count"] == 2, str(st))
    _cleanup(owner)

    # ---- Q7: independent-owner control.
    owner_a, owner_b = "Q1IndepA", "Q1IndepB"
    _cleanup(owner_a)
    _cleanup(owner_b)
    pa = Program(owner=owner_a)
    impa = exchange.import_packet(pa, _packet())
    bytes_a = _file_bytes(_program_path(owner_a))
    pb = Program(owner=owner_b)
    impb = exchange.import_packet(pb, _packet())
    _rec("Q7: same packet lands FRESH for an independent owner",
         impb.get("ok") is True and impb.get("replay") is False
         and label_count(pb, "q1-idea") == 1, str(impb))
    pb.save()
    _rec("Q7: owner B's save never touches owner A's state",
         _file_bytes(_program_path(owner_a)) == bytes_a)
    _cleanup(owner_a)
    _cleanup(owner_b)

    # ---- Q8: recovery agreement — an import completed through
    # load-boundary recovery is the same import to the witness.
    owner = "Q1Recover"
    _cleanup(owner)
    p = Program(owner=owner)
    with _BrokenJournalUnlink():
        imp1 = exchange.import_packet(p, _packet())
    pid1 = imp1["pid"]
    p2 = persist_rest.load(owner, activate=False)
    imp2 = exchange.import_packet(p2, _packet())
    _rec("Q8: post-recovery duplicate replays the original pid",
         imp2.get("ok") is True and imp2.get("replay") is True
         and imp2.get("pid") == pid1, str(imp2))
    _rec("Q8: still exactly one copy after recovery + replay",
         label_count(p2, "q1-idea") == 1)
    _cleanup(owner)

    # ---- Q9: preservation impossible -> typed refusal, no bytes.
    owner = "Q1FailClosed"
    _cleanup(owner)
    stale = Program(owner=owner)
    importer = Program(owner=owner)
    exchange.import_packet(importer, _packet())
    before = _file_bytes(_program_path(owner))
    real_raw = exchange._raw_state_files

    def _boom(_owner):
        raise RuntimeError("injected durable read failure")

    exchange._raw_state_files = _boom
    err = None
    try:
        stale.save()
    except Exception as e:  # noqa: BLE001 - verdict recorded below
        err = e
    finally:
        exchange._raw_state_files = real_raw
    _rec("Q9: unpreservable stale save refuses TYPED pre-byte",
         StaleWriterSaveError is not None
         and isinstance(err, StaleWriterSaveError), repr(err))
    _rec("Q9: refused save changed no durable bytes",
         _file_bytes(_program_path(owner)) == before)
    _cleanup(owner)

    # ---- Q10: Director correction 7203516785 — a PRESENT but
    # malformed exchange section (here: the entries container is
    # a list, not an object) is unreadable durable state, not
    # zero records. With a live proposal, the stale save refuses
    # typed pre-byte; the source bytes stay untouched. Control:
    # with no live proposal, the same shape is outside this
    # boundary's scope and the stale save proceeds.
    owner = "Q1Shell"
    _cleanup(owner)
    stale = Program(owner=owner)
    importer = Program(owner=owner)
    imp = exchange.import_packet(importer, _packet())
    pid = imp["pid"]
    path = _program_path(owner)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    data["exchange_seeds"]["entries"] = ["not", "an", "object"]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    before = _file_bytes(path)
    err = None
    try:
        stale.save()
    except Exception as e:  # noqa: BLE001 - verdict recorded below
        err = e
    _rec("Q10: present malformed exchange section + live proposal "
         "-> stale save refuses TYPED pre-byte",
         StaleWriterSaveError is not None
         and isinstance(err, StaleWriterSaveError), repr(err))
    _rec("Q10: refused save left the source bytes untouched",
         _file_bytes(path) == before)
    fresh = Program(owner=owner)
    fresh.nursery.reject(pid)
    fresh.nursery.clear_rejected()
    err2 = None
    try:
        stale.save()
    except Exception as e:  # noqa: BLE001 - verdict recorded below
        err2 = e
    _rec("Q10: same malformed shape with NO live proposal is out "
         "of scope — stale save proceeds",
         err2 is None, repr(err2))
    _cleanup(owner)

    # ---- Q11: Critic P1 (review 4713412892, verified real) —
    # preservation must survive BOUNDED SERIALIZATION. The stale
    # instance carries a full receipts section (200) bound to
    # cleared rejected proposals; a second instance's live import
    # carries 2 receipts. With the live entries' timestamps
    # pinned oldest (the deterministic form of the review's
    # equal-timestamp tie), serializer retention would drop the
    # just-preserved live receipts at the save — so the stale
    # save refuses typed pre-byte and the import's durable
    # receipts survive intact.
    owner = "Q1Cap"
    _cleanup(owner)

    def _big_packet(label, n):
        pkt = _packet(label=label)
        pkt["receipts"] = [
            {"origin": f"cap:{label}-{j}", "guess": f"g{j}",
             "test_method": "m", "result": "r", "mirror": "mi",
             "outcome": "o"} for j in range(n)]
        return pkt

    stale = Program(owner=owner)
    for i in range(4):
        impf = exchange.import_packet(
            stale, _big_packet(f"cap-fill-{i}", 50))
        stale.nursery.reject(impf["pid"])
        stale.nursery.clear_rejected()
    importer = Program(owner=owner)
    imp = exchange.import_packet(importer, _packet(label="cap-live"))
    pid = imp["pid"]
    path = _program_path(owner)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    for e in data["exchange_receipts"]["entries"].values():
        if e.get("pid") == pid:
            e["ts"] = "2000-01-01T00:00:00Z"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    before = _file_bytes(path)
    err = None
    try:
        stale.save()
    except Exception as e:  # noqa: BLE001 - verdict recorded below
        err = e
    _rec("Q11: full-section stale save that would drop live "
         "receipts at serialization refuses TYPED pre-byte",
         StaleWriterSaveError is not None
         and isinstance(err, StaleWriterSaveError), repr(err))
    _rec("Q11: refused save changed no durable bytes",
         _file_bytes(path) == before)
    st = exchange._durable_import_state(owner, pid)
    _rec("Q11: live import's durable receipts survive intact (2)",
         st["proposal_present"] and st["seed_present"]
         and st["receipts_count"] == 2, str(st))
    _cleanup(owner)

    # ---- Q12: corrupt-bytes repair posture (the DCC-XVII / TD-1
    # contract, following _persisted_bindings' precedent beside
    # the check): whole-file unparseable durable state carries
    # no READABLE exchange record to preserve, and a live
    # instance's save over it is the established repair — not a
    # stale-writer refusal. (Q9's refusal class is a read failure
    # with no corrupt file.)
    owner = "Q1Repair"
    _cleanup(owner)
    p = Program(owner=owner)
    exchange.import_packet(p, _packet())
    path = _program_path(owner)
    with open(path, "wb") as f:
        f.write(b"\xff\xfe not json")
    err = None
    try:
        p.save()
    except Exception as e:  # noqa: BLE001 - verdict recorded below
        err = e
    _rec("Q12: save over whole-file-corrupt durable state "
         "proceeds (repair posture, no stale-writer refusal)",
         err is None, repr(err))
    _cleanup(owner)

    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        print(f"[{'PASS' if ok else 'FAIL'}] {name}"
              + (f" | {detail}" if detail and not ok else ""))
    print(f"Q1_DUPLICATE_IMPORT: {passed}/{len(RESULTS)}")
    return passed == len(RESULTS)


def smoke() -> bool:
    return main()


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
