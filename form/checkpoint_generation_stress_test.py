#!/usr/bin/env python3
"""72-29 — checkpoint sealing stress: fsync / directory-sync /
missing generations / retry (the injection pass the register
names as the remaining gap for SM-36).

Existing coverage (NOT duplicated): form/mandell/dcc_xviii_test.py
controls A–W pin normal commits, crash-at-stage injection,
missing/corrupt/swapped members, manifest/pointer corruption,
retention and the cross-process matrix.

This suite pins what DCC-XVIII does not:
  - a pre-Phase-2 generation whose manifest has NO graph member
    (checkpoint_generation._read_manifest explicitly tolerates
    it — "rollback treats it as graph cleared", and
    core_i_recovery stages an empty graph for such generations):
    load_checkpoint must LOAD it, never escape a raw KeyError;
  - directory-sync failure (atomic_write _fail_at="dir_fsync_fail"):
    the commit is best-effort and the sealed hashes still verify
    on load (control), AND the degradation is observable in the
    commit receipt (atomic_write's contract: "Degradation is
    explicit: the caller can observe dir_fsynced=False");
  - a real fsync/write OSError inside atomic_write: it must
    surface as AtomicWriteError with the target untouched (the
    helper's documented error type), not as a raw OSError;
  - a member-copy OSError at the checkpoint boundary: it must
    abort the commit as CheckpointCommitError (the wrap
    _seal_members states) so commit_checkpoint's eager
    convergence handler runs, and the previous generation stays
    authoritative;
  - missing MANIFEST (a missing generation, distinct from a
    missing member): recover the previous generation, or fail
    explicitly with CheckpointLoadError when there is none;
  - retry of the same generation_id after a failed seal.

Labels: INTEGRATION (in-process against the real checkpoint
authority on isolated owners). State hygiene: every owner is
uuid-unique; cleanup failures are reported as a failing check,
never swallowed.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

RESULTS = []
_CLEANUP_ERRORS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def _owner(tag):
    return "S7229" + tag + uuid.uuid4().hex[:8]


def smoke() -> bool:
    from form.open import open_program
    from form.persist import _STATE_DIR, _safe_owner
    from form.dell_matrix import atomic_write as AW
    from form.dell_matrix.atomic_write import AtomicWriteError
    from form.mandell import checkpoint_generation as CG
    from form.mandell.checkpoint_generation import (
        CheckpointCommitError, CheckpointLoadError)

    STATE = Path(_STATE_DIR)
    owners = []

    def wipe(owner):
        ns = CG._owner_ns(owner)
        safe = _safe_owner(owner)
        pats = [f"*{ns}*", f"program_{safe}.json", f"nursery_{safe}.json",
                f"ideas_{safe}.json", f"*{safe}*graph*"]
        seen = set()
        for pat in pats:
            for f in STATE.glob(pat):
                if f in seen or not f.is_file():
                    continue
                seen.add(f)
                try:
                    f.unlink()
                except OSError as exc:
                    _CLEANUP_ERRORS.append(f"{f}: {exc}")

    def fresh(tag):
        o = _owner(tag)
        owners.append(o)
        wipe(o)
        return o, open_program(o)

    def add(p, label, words):
        from form.dell_matrix import confirm_lineage
        pr = p.nursery.add(label, words=words)
        orig = getattr(confirm_lineage.confirm_proposal,
                       "_SKIP_CHECKPOINT", False)
        confirm_lineage.confirm_proposal._SKIP_CHECKPOINT = True
        try:
            p.confirm_proposal(
                pr.id, _producer="test",
                _review_context=p.make_review_context(pr.id, "test"))
        finally:
            confirm_lineage.confirm_proposal._SKIP_CHECKPOINT = orig
        return pr.id

    def sha(path):
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    # -- control: normal commit, hash agreement, coherent load --
    o, p = fresh("NORM")
    a = add(p, "norm base", "normal base words here")
    r1 = CG.commit_checkpoint(p, generation_id="gn29000000000001")
    man = json.loads(Path(CG._manifest_path(o, "gn29000000000001")).read_text())
    agree = all(sha(STATE / spec["file"]) == spec["sha256"]
                for spec in man["members"].values())
    check("normal.hashes_agree", agree and r1["committed"] is True)
    q, lr = CG.load_checkpoint(o, activate=False)
    check("normal.load_coherent",
          lr["generation_id"] == "gn29000000000001"
          and a in q.nursery.proposals)

    # -- control: missing member recovers previous --------------
    o, p = fresh("MMBR")
    add(p, "mmbr base", "member base words here")
    CG.commit_checkpoint(p, generation_id="gm2900000000000a")
    add(p, "mmbr next", "member next words here")
    CG.commit_checkpoint(p, generation_id="gm2900000000000b")
    Path(CG._member_path(o, "program", "gm2900000000000b")).unlink()
    q, lr = CG.load_checkpoint(o, activate=False)
    check("missing_member.recovers_previous",
          lr["generation_id"] == "gm2900000000000a"
          and lr["recovered_from"] == "gm2900000000000b")

    # -- control: tampered member fingerprint recovers previous -
    o, p = fresh("TAMP")
    add(p, "tamp base", "tamper base words here")
    CG.commit_checkpoint(p, generation_id="gt2900000000000a")
    add(p, "tamp next", "tamper next words here")
    CG.commit_checkpoint(p, generation_id="gt2900000000000b")
    mp = Path(CG._member_path(o, "nursery", "gt2900000000000b"))
    blob = mp.read_bytes()
    mp.write_bytes(blob[: len(blob) // 3])
    q, lr = CG.load_checkpoint(o, activate=False)
    check("tamper.recovers_previous",
          lr["generation_id"] == "gt2900000000000a"
          and lr["recovered_from"] == "gt2900000000000b")

    # -- missing generation (manifest absent) -------------------
    o, p = fresh("MMAN")
    add(p, "mman base", "manifest base words here")
    CG.commit_checkpoint(p, generation_id="gx2900000000000a")
    add(p, "mman next", "manifest next words here")
    CG.commit_checkpoint(p, generation_id="gx2900000000000b")
    Path(CG._manifest_path(o, "gx2900000000000b")).unlink()
    try:
        q, lr = CG.load_checkpoint(o, activate=False)
        check("missing_manifest.recovers_previous",
              lr["generation_id"] == "gx2900000000000a"
              and lr["recovered_from"] == "gx2900000000000b")
    except Exception as exc:
        check("missing_manifest.recovers_previous", False,
              f"{type(exc).__name__}: {exc}")

    o, p = fresh("MMN2")
    add(p, "mmn2 base", "manifest two base words")
    CG.commit_checkpoint(p, generation_id="gy2900000000000a")
    Path(CG._manifest_path(o, "gy2900000000000a")).unlink()
    try:
        CG.load_checkpoint(o, activate=False)
        check("missing_manifest_no_prev.explicit_fail", False,
              "loaded unexpectedly")
    except CheckpointLoadError:
        check("missing_manifest_no_prev.explicit_fail", True)
    except Exception as exc:
        check("missing_manifest_no_prev.explicit_fail", False,
              f"raw {type(exc).__name__}: {exc}")

    # -- control: retry same generation_id after failed seal ----
    o, p = fresh("RTRY")
    add(p, "rtry base", "retry base words here")
    try:
        CG.commit_checkpoint(p, generation_id="gr29000000000001",
                             _fail_at="after_members")
        aborted = False
    except Exception:
        aborted = True
    try:
        CG.commit_checkpoint(p, generation_id="gr29000000000001")
        q, lr = CG.load_checkpoint(o, activate=False)
        retried = lr["generation_id"] == "gr29000000000001"
    except Exception as exc:
        retried = False
        print(f"  retry exc: {type(exc).__name__}: {exc}")
    check("retry.same_id_after_failure", aborted and retried)

    # -- DEFECT D1: pre-Phase-2 generation (no graph member) ----
    o, p = fresh("LEG1")
    a = add(p, "leg1 base", "legacy one base words")
    CG.commit_checkpoint(p, generation_id="gl29000000000001")
    mpath = Path(CG._manifest_path(o, "gl29000000000001"))
    man = json.loads(mpath.read_text())
    del man["members"]["graph"]
    mpath.write_text(json.dumps(man, indent=2))
    try:
        q, lr = CG.load_checkpoint(o, activate=False)
        check("legacy_no_graph.loads",
              lr["generation_id"] == "gl29000000000001"
              and a in q.nursery.proposals)
    except Exception as exc:
        check("legacy_no_graph.loads", False,
              f"{type(exc).__name__}: {exc}")

    o, p = fresh("LEG2")
    add(p, "leg2 base", "legacy two base words")
    CG.commit_checkpoint(p, generation_id="gl2900000000000a")
    add(p, "leg2 next", "legacy two next words")
    CG.commit_checkpoint(p, generation_id="gl2900000000000b")
    mpath = Path(CG._manifest_path(o, "gl2900000000000b"))
    man = json.loads(mpath.read_text())
    del man["members"]["graph"]
    mpath.write_text(json.dumps(man, indent=2))
    try:
        q, lr = CG.load_checkpoint(o, activate=False)
        check("legacy_no_graph.with_previous_no_raw",
              lr["generation_id"] in ("gl2900000000000a",
                                      "gl2900000000000b"))
    except CheckpointLoadError:
        check("legacy_no_graph.with_previous_no_raw", False,
              "fail-closed instead of the tolerated load")
    except Exception as exc:
        check("legacy_no_graph.with_previous_no_raw", False,
              f"raw {type(exc).__name__}: {exc}")

    # -- directory-sync failure ---------------------------------
    o, p = fresh("DSYN")
    add(p, "dsyn base", "dirsync base words here")
    AW._FAIL_AT = "dir_fsync_fail"
    try:
        r = CG.commit_checkpoint(p, generation_id="gd29000000000001")
        committed = True
    except Exception as exc:
        committed = False
        r = {}
        print(f"  dirsync exc: {type(exc).__name__}: {exc}")
    finally:
        AW._FAIL_AT = None
    try:
        q, lr = CG.load_checkpoint(o, activate=False)
        loads = lr["generation_id"] == "gd29000000000001"
    except Exception:
        loads = False
    check("dirsync.commit_and_load", committed and loads)
    flat = json.dumps(r).lower()
    check("dirsync.receipt_surfaces_degradation",
          committed and "fsync" in flat,
          f"receipt keys={sorted(r.keys())}")

    # -- DEFECT D3a: fsync OSError inside atomic_write ----------
    target = STATE / f"stress_fsync_{uuid.uuid4().hex[:8]}.json"
    target.write_text('{"v": 1}')
    orig_fsync = os.fsync

    def bad_fsync(fd):
        raise OSError("injected fsync failure")

    os.fsync = bad_fsync
    try:
        AW.atomic_write_json(str(target), {"v": 2})
        kind = "none"
    except AtomicWriteError:
        kind = "atomic"
    except OSError:
        kind = "raw-oserror"
    except Exception as exc:
        kind = f"other-{type(exc).__name__}"
    finally:
        os.fsync = orig_fsync
    untouched = target.read_text() == '{"v": 1}'
    check("atomic.fsync_raises_atomic_write_error",
          kind == "atomic" and untouched,
          f"kind={kind} untouched={untouched}")
    try:
        target.unlink()
    except OSError as exc:
        _CLEANUP_ERRORS.append(f"{target}: {exc}")

    # -- control: global fsync failure, previous authoritative --
    o, p = fresh("FSYN")
    add(p, "fsyn base", "fsync base words here")
    CG.commit_checkpoint(p, generation_id="gf2900000000000a")
    add(p, "fsyn next", "fsync next words here")
    os.fsync = bad_fsync
    try:
        CG.commit_checkpoint(p, generation_id="gf2900000000000b")
        aborted = False
    except Exception:
        aborted = True
    finally:
        os.fsync = orig_fsync
    try:
        q, lr = CG.load_checkpoint(o, activate=False)
        prev = (lr["generation_id"] == "gf2900000000000a"
                and lr["recovered_from"] is None)
    except Exception:
        prev = False
    check("fsync_global.previous_authoritative", aborted and prev)

    # -- DEFECT D3b: member-copy OSError at checkpoint boundary -
    o, p = fresh("MEMB")
    add(p, "memb base", "memberr base words here")
    CG.commit_checkpoint(p, generation_id="gk2900000000000a")
    add(p, "memb next", "memberr next words here")
    orig_awb = CG.atomic_write_bytes

    def bad_awb(path, blob, **kw):
        raise OSError("injected member write failure (EIO)")

    CG.atomic_write_bytes = bad_awb
    try:
        CG.commit_checkpoint(p, generation_id="gk2900000000000b")
        kind = "none"
    except CheckpointCommitError:
        kind = "commit-error"
    except OSError:
        kind = "raw-oserror"
    except Exception as exc:
        kind = f"other-{type(exc).__name__}"
    finally:
        CG.atomic_write_bytes = orig_awb
    try:
        q, lr = CG.load_checkpoint(o, activate=False)
        prev = lr["generation_id"] == "gk2900000000000a"
    except Exception:
        prev = False
    check("member_oserror.checkpoint_commit_error",
          kind == "commit-error" and prev, f"kind={kind} prev={prev}")

    for o in owners:
        wipe(o)
    check("cleanup.ok", not _CLEANUP_ERRORS,
          "; ".join(_CLEANUP_ERRORS[:3]))

    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"\n{passed}/{len(RESULTS)} PASS")
    return passed == len(RESULTS)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
