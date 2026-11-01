"""DIR-F12 — journal-deletion receipt (Director Ruling #7, P2).

Defect: _clear_import_journal returns False on unlink failure, but
_fail_import ignored it and reported journal_retained=False after
complete compensation; recovery's completed/removed/already_absent/
no_target exits and the successful-import path also ignored the
deletion outcome.

Contract proven here:
- durable compensation success and journal disposal are SEPARATE
  facts: verified compensation stays "complete" when true, and the
  error reports the ACTUAL retained journal;
- a successful landing whose journal unlink fails returns ok=True
  (the landing is durably complete — disposal must not convert it
  into a failure or trigger compensation) WITH journal_retained
  surfaced in the result and the journal file present on disk;
- load-boundary recovery never claims disposal it did not achieve:
  if the journal cannot be cleared after the recovery outcome is
  established, recovery raises (state is not exposed over
  unresolved evidence); with unlink restored, the next load is a
  safe retry that resolves the journal and exposes coherent state;
- the incomplete-compensation contract (step 5b) is preserved.

Unlink failure is injected with a targeted os.remove wrapper that
fails only for the import-journal path; the journal is a real file
on disk throughout. Labels: INTEGRATION (real Program/Nursery/
persist paths, separate load instances).
"""
from __future__ import annotations

import glob
import json
import os
import shutil
import sys

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


def _packet(tag):
    return {
        "version": 1,
        "seed": {"label": f"f12-label-{tag}", "chain": f"chain-{tag}",
                 "keep": f"F12-KEEP-{tag}"},
        "manifest": {"author_origin": "f12:origin",
                     "created": "2026-11-01T00:00:00Z",
                     "registry": "core1:00-50,core2:51-99",
                     "requirements": [f"req-{tag}"]},
        "receipts": [
            {"origin": "f12:org", "guess": f"g{j}",
             "test_method": "m", "result": "r", "mirror": "mi",
             "outcome": "o"} for j in range(2)],
    }


def _journal_path(owner):
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "state")
    return os.path.join(base, f"exchange_import_{owner}.journal.json")


class _BrokenJournalUnlink:
    """os.remove wrapper: fails only for the import journal file."""

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
    from form.dell_matrix import exchange
    from form.dell_matrix.exchange import ExchangeError

    def dead_save(*a, **k):
        raise RuntimeError("injected save failure")

    # ---- W1: failure compensation, unlink broken.
    # Final save fails; compensation is verified complete on disk,
    # but the journal unlink fails -> the error must keep
    # compensation=complete AND report journal_retained=True.
    owner = "DirF12FailComp"
    _cleanup(owner)
    p = Program(owner=owner)
    p.save = dead_save
    err = None
    with _BrokenJournalUnlink():
        try:
            exchange.import_packet(p, _packet("one"))
        except ExchangeError as e:
            err = e
    _rec("W1: final-save failure raises", err is not None)
    _rec("W1: compensation still verified complete",
         err is not None
         and err.details.get("compensation") == "complete",
         str(err and err.details))
    _rec("W1: journal_retained reported truthfully (True)",
         err is not None
         and err.details.get("journal_retained") is True,
         str(err and err.details))
    _rec("W1: journal file actually present on disk",
         os.path.isfile(_journal_path(owner)))
    # restored unlink: restart recovery resolves the retained
    # journal (already_absent) and the retry lands cleanly.
    p2 = persist_rest.load(owner, activate=False)
    _rec("W1: restart after restored unlink exposes no partial",
         all(pr.label != "f12-label-one"
             for pr in p2.nursery.proposals.values()))
    _rec("W1: journal cleared by recovery retry",
         not os.path.isfile(_journal_path(owner)))
    imp = exchange.import_packet(p2, _packet("one"))
    _rec("W1: retry import succeeds, no journal retained",
         imp.get("ok") is True
         and imp.get("journal_retained") is False
         and not os.path.isfile(_journal_path(owner)),
         str(imp))
    _cleanup(owner)

    # ---- W2+W3: successful landing, unlink broken; then restart
    # with unlink still broken must fail closed; restored unlink
    # resolves the completed import, changing nothing.
    owner = "DirF12Landing"
    _cleanup(owner)
    p = Program(owner=owner)
    with _BrokenJournalUnlink():
        imp = exchange.import_packet(p, _packet("two"))
    _rec("W2: landing itself succeeds (ok=True, not compensated)",
         imp.get("ok") is True, str(imp))
    _rec("W2: journal_retained surfaced in the result",
         imp.get("journal_retained") is True, str(imp))
    _rec("W2: journal file actually present on disk",
         os.path.isfile(_journal_path(owner)))
    pid = imp["pid"]
    load_err = None
    with _BrokenJournalUnlink():
        try:
            persist_rest.load(owner, activate=False)
        except ExchangeError as e:
            load_err = e
    _rec("W3: load fails closed while journal disposal impossible",
         load_err is not None
         and load_err.details.get("journal_retained") is True,
         str(load_err and load_err.details))
    _rec("W3: journal still present after failed recovery disposal",
         os.path.isfile(_journal_path(owner)))
    p2 = persist_rest.load(owner, activate=False)
    _rec("W3: restored unlink -> load succeeds, journal cleared",
         not os.path.isfile(_journal_path(owner)))
    sp = exchange.seed_payload_for(p2, pid)
    _rec("W3: completed import stands intact after recovery",
         pid in p2.nursery.proposals
         and sp is not None and sp.get("keep") == "F12-KEEP-two"
         and len(exchange.receipts_for(p2, pid)) == 2)
    _cleanup(owner)

    # ---- W4: recovery 'removed' exit, unlink broken.
    # Build a compensation_incomplete journal with a durable
    # partial (step 5b F2 setup), then break the journal unlink
    # at restart: recovery removes the partial but cannot dispose
    # of the journal -> load must raise; restored unlink retries
    # via already_absent and exposes coherent state.
    owner = "DirF12Recovery"
    _cleanup(owner)
    p = Program(owner=owner)
    orig_seed = exchange.record_seed_payload

    def boom_seed(program, pid_, pkt, _defer_save=False):
        raise ExchangeError("injected seed failure")

    real_nsave = p.nursery.save
    calls = {"n": 0}

    def flaky_nsave(*a, **k):
        calls["n"] += 1
        if calls["n"] > 1:
            raise RuntimeError("injected rollback nursery failure")
        return real_nsave(*a, **k)

    p.nursery.save = flaky_nsave
    exchange.record_seed_payload = boom_seed
    err = None
    try:
        exchange.import_packet(p, _packet("four"))
    except ExchangeError as e:
        err = e
    finally:
        exchange.record_seed_payload = orig_seed
    _rec("W4: setup keeps step5b incomplete-compensation contract",
         err is not None
         and err.details.get("compensation") == "incomplete"
         and err.details.get("journal_retained") is True,
         str(err and err.details))
    _rec("W4: setup journal retained as compensation_incomplete",
         os.path.isfile(_journal_path(owner)))
    load_err = None
    with _BrokenJournalUnlink():
        try:
            persist_rest.load(owner, activate=False)
        except ExchangeError as e:
            load_err = e
    _rec("W4: recovery with broken unlink raises (no false disposal)",
         load_err is not None
         and load_err.details.get("journal_retained") is True,
         str(load_err and load_err.details))
    _rec("W4: journal still present after failed recovery disposal",
         os.path.isfile(_journal_path(owner)))
    p2 = persist_rest.load(owner, activate=False)
    _rec("W4: restored unlink -> partial gone, journal cleared",
         all(pr.label != "f12-label-four"
             for pr in p2.nursery.proposals.values())
         and not os.path.isfile(_journal_path(owner)))
    imp = exchange.import_packet(p2, _packet("four"))
    _rec("W4: retry after recovery succeeds",
         imp.get("ok") is True
         and imp.get("journal_retained") is False)
    _cleanup(owner)

    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        print(f"[{'PASS' if ok else 'FAIL'}] {name}"
              + (f" | {detail}" if detail and not ok else ""))
    print(f"DIRF12_JOURNAL_RECEIPT: {passed}/{len(RESULTS)}")
    return passed == len(RESULTS)


def smoke() -> bool:
    return main()


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
