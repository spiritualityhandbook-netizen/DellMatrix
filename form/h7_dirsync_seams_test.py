#!/usr/bin/env python3
"""H7 / row #47 (SM-36 / DD-04) — directory-sync failure modes at the
individual seal seams of a checkpoint generation commit.

Existing coverage (NOT duplicated): checkpoint_generation_stress_test
pins directory-sync failure under a GLOBAL injection (every write in
the commit degrades at once) and the pointer seam's receipt surface
(72-29 D2: ``dir_fsynced`` on the commit receipt is the POINTER
write's outcome, captured immediately after the pointer swap).

This suite pins what the landed family does not: the seal writes
BEFORE the commit boundary. A commit performs, in order:

    member copies x4   (atomic_write_bytes)
    manifest write     (atomic_write_json)
    pointer write      (atomic_write_json)  <- commit boundary

Each atomic_write call records its directory-fsync outcome on the
function object (atomic_write's documented explicit-degradation
surface), but the checkpoint layer historically observed ONLY the
pointer's. A member copy whose directory sync degraded left the
generation's payload possibly non-durable while the commit receipt
asserted ``dir_fsynced: True`` with no checkpoint-layer surface for
the member or manifest degradation.

Director correction on PR #547 (source review, 2026-11-26): the
function-object surface is process-wide and last-writer-wins, so a
receipt read from it can carry a SECOND in-process writer's outcome
whenever the writers overlap. The receipt therefore reads each
write's own per-operation capture (``_sync_capture``), never the
shared surface. The final section of this suite pins that with a
deterministic two-writer interleave at the member and pointer
seams, plus the channel property itself.

Contract pinned here (Part I plan 2026-11-20 section 5.1, row #47
retained remainder):
  - the commit receipt carries per-seam directory-sync outcomes:
    ``dir_fsynced_members`` (all four member copies), and
    ``dir_fsynced_manifest``; ``dir_fsynced`` keeps its pinned
    meaning (the pointer write);
  - degradation at any single seam is best-effort and EXPLICIT:
    the commit still succeeds, the sealed generation still loads
    and verifies, and exactly the degraded seam reports False on
    the receipt — seams are reported independently, never conflated
    into one another and never silently upgraded to True.

Injection is seam-targeted: the documented atomic_write
``_fail_at="dir_fsync_fail"`` contract, applied through a wrapper
on the checkpoint module's own references, filtered per seam
(member calls / the manifest path / the pointer path). Wrappers
re-export the real function's ``_last_dir_fsynced`` after every
delegated call, mirroring atomic_write's own surface.

Labels: INTEGRATION (in-process against the real checkpoint
authority on isolated owners). State hygiene: every owner is
uuid-unique; cleanup failures are reported as a failing check,
never swallowed.
"""
from __future__ import annotations

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
    return "H7DS" + tag + uuid.uuid4().hex[:8]


def _wrap_bytes_dirsync_fail(real):
    """Every delegated call degrades its directory sync; the
    wrapper mirrors the real function's outcome surface."""
    def w(path, blob, **kw):
        kw["_fail_at"] = "dir_fsync_fail"
        out = real(path, blob, **kw)
        w._last_dir_fsynced = getattr(real, "_last_dir_fsynced", False)
        return out
    w._last_dir_fsynced = True
    return w


def _wrap_json_dirsync_fail_on(real, target_paths):
    """Only calls whose target is in ``target_paths`` degrade;
    all other calls delegate untouched. Mirrors the outcome
    surface after every delegated call."""
    targets = {os.path.abspath(p) for p in target_paths}

    def w(path, payload, **kw):
        if os.path.abspath(path) in targets:
            kw["_fail_at"] = "dir_fsync_fail"
        out = real(path, payload, **kw)
        w._last_dir_fsynced = getattr(real, "_last_dir_fsynced", False)
        return out
    w._last_dir_fsynced = True
    return w


def smoke() -> bool:
    from form.open import open_program
    from form.persist import _STATE_DIR, _safe_owner
    from form.mandell import checkpoint_generation as CG

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

    def loads(o, gen_id):
        try:
            _q, lr = CG.load_checkpoint(o, activate=False)
            return lr["generation_id"] == gen_id
        except Exception:
            return False

    # -- control: healthy commit reports every seal seam synced --
    o, p = fresh("CTRL")
    add(p, "ctrl base", "control base words here")
    r = CG.commit_checkpoint(p, generation_id="gc47000000000001")
    check("control.all_seams_synced",
          r.get("committed") is True
          and r.get("dir_fsynced") is True
          and r.get("dir_fsynced_members") is True
          and r.get("dir_fsynced_manifest") is True,
          f"receipt={ {k: r.get(k) for k in ('committed', 'dir_fsynced', 'dir_fsynced_members', 'dir_fsynced_manifest')} }")
    check("control.load_coherent", loads(o, "gc47000000000001"))

    # -- member seam only: degradation surfaced, pointer intact ---
    o, p = fresh("MEMB")
    add(p, "memb base", "member seam base words")
    real_bytes = CG.atomic_write_bytes
    CG.atomic_write_bytes = _wrap_bytes_dirsync_fail(real_bytes)
    try:
        r = CG.commit_checkpoint(p, generation_id="gm47000000000001")
    finally:
        CG.atomic_write_bytes = real_bytes
    check("member_seam.degradation_surfaced",
          r.get("committed") is True
          and r.get("dir_fsynced_members") is False
          and r.get("dir_fsynced_manifest") is True
          and r.get("dir_fsynced") is True,
          f"receipt={ {k: r.get(k) for k in ('dir_fsynced', 'dir_fsynced_members', 'dir_fsynced_manifest')} }")
    check("member_seam.load_coherent", loads(o, "gm47000000000001"))

    # -- manifest seam only ---------------------------------------
    o, p = fresh("MANI")
    add(p, "mani base", "manifest seam base words")
    gen = "gx47000000000001"
    real_json = CG.atomic_write_json
    CG.atomic_write_json = _wrap_json_dirsync_fail_on(
        real_json, [CG._manifest_path(o, gen)])
    try:
        r = CG.commit_checkpoint(p, generation_id=gen)
    finally:
        CG.atomic_write_json = real_json
    check("manifest_seam.degradation_surfaced",
          r.get("committed") is True
          and r.get("dir_fsynced_manifest") is False
          and r.get("dir_fsynced_members") is True
          and r.get("dir_fsynced") is True,
          f"receipt={ {k: r.get(k) for k in ('dir_fsynced', 'dir_fsynced_members', 'dir_fsynced_manifest')} }")
    check("manifest_seam.load_coherent", loads(o, gen))

    # -- pointer seam only: pinned meaning stays independent ------
    o, p = fresh("PNTR")
    add(p, "pntr base", "pointer seam base words")
    gen = "gp47000000000001"
    real_json = CG.atomic_write_json
    CG.atomic_write_json = _wrap_json_dirsync_fail_on(
        real_json, [CG._pointer_path(o)])
    try:
        r = CG.commit_checkpoint(p, generation_id=gen)
    finally:
        CG.atomic_write_json = real_json
    check("pointer_seam.independent",
          r.get("committed") is True
          and r.get("dir_fsynced") is False
          and r.get("dir_fsynced_members") is True
          and r.get("dir_fsynced_manifest") is True,
          f"receipt={ {k: r.get(k) for k in ('dir_fsynced', 'dir_fsynced_members', 'dir_fsynced_manifest')} }")
    check("pointer_seam.load_coherent", loads(o, gen))

    # -- channel property: the function-object surface is process-
    # wide and holds only the LAST writer's outcome (Director
    # source review on PR #547, 2026-11-26). Two writers sharing
    # one process can therefore replace each other's published
    # outcome between a write returning and a reader observing
    # the surface. A per-operation capture is the only honest
    # receipt source under concurrency.
    from form.dell_matrix import atomic_write as AW
    scratch = STATE / f"h7ds_channel_{uuid.uuid4().hex[:8]}.bin"
    cap_a, cap_b = {}, {}
    try:
        AW.atomic_write_bytes(str(scratch), b"a", _sync_capture=cap_a)
        AW.atomic_write_bytes(str(scratch), b"b",
                              _fail_at="dir_fsync_fail",
                              _sync_capture=cap_b)
        channel_ok = (
            getattr(AW.atomic_write_bytes, "_last_dir_fsynced", None)
            is False
            and cap_a.get("dir_fsynced") is True
            and cap_b.get("dir_fsynced") is False)
        channel_detail = (
            f"attr={getattr(AW.atomic_write_bytes, '_last_dir_fsynced', None)} "
            f"cap_a={cap_a} cap_b={cap_b}")
    except TypeError as exc:
        channel_ok = False
        channel_detail = f"per-operation capture unsupported: {exc}"
    finally:
        try:
            scratch.unlink()
        except OSError:
            pass
    check("channel.shared_surface_last_writer_wins", channel_ok,
          channel_detail)

    # -- two writers, one process (deterministic interleave):
    # writer B's degraded write lands after writer A's seam write
    # returns but before A's receipt observation, at BOTH the
    # member seam and the pointer seam. A's receipt must report
    # A's OWN outcomes: every A write in this run genuinely
    # synced, so every seam must read True.
    import threading
    o, p = fresh("RACE")
    add(p, "race base", "two writer race base words")
    gen = "gr47000000000001"
    real_bytes = CG.atomic_write_bytes
    real_json = CG.atomic_write_json
    b_bin = STATE / f"h7ds_b_{uuid.uuid4().hex[:8]}.bin"
    b_json = STATE / f"h7ds_b_{uuid.uuid4().hex[:8]}.json"
    at1, done1 = threading.Event(), threading.Event()
    at2, done2 = threading.Event(), threading.Event()
    b_ran = {"bytes": False, "json": False}

    def w_bytes(path, blob, **kw):
        out = real_bytes(path, blob, **kw)
        if not at1.is_set() and not b_ran["bytes"]:
            at1.set()
            done1.wait(120)
        w_bytes._last_dir_fsynced = getattr(
            real_bytes, "_last_dir_fsynced", False)
        return out
    w_bytes._last_dir_fsynced = True

    pointer_abspath = os.path.abspath(CG._pointer_path(o))

    def w_json(path, payload, **kw):
        out = real_json(path, payload, **kw)
        if (os.path.abspath(path) == pointer_abspath
                and not b_ran["json"]):
            at2.set()
            done2.wait(120)
        w_json._last_dir_fsynced = getattr(
            real_json, "_last_dir_fsynced", False)
        return out
    w_json._last_dir_fsynced = True

    result_box = {}

    def run_a():
        try:
            result_box["r"] = CG.commit_checkpoint(
                p, generation_id=gen)
        except Exception as exc:  # surfaced by the checks below
            result_box["exc"] = exc

    CG.atomic_write_bytes = w_bytes
    CG.atomic_write_json = w_json
    t = threading.Thread(target=run_a)
    try:
        t.start()
        if at1.wait(180):
            real_bytes(str(b_bin), b"b", _fail_at="dir_fsync_fail")
            b_ran["bytes"] = True
            done1.set()
            if at2.wait(180):
                real_json(str(b_json), {"b": 1},
                          _fail_at="dir_fsync_fail")
                b_ran["json"] = True
                done2.set()
        t.join(300)
    finally:
        CG.atomic_write_bytes = real_bytes
        CG.atomic_write_json = real_json
        for f in (b_bin, b_json):
            try:
                f.unlink()
            except OSError:
                pass
    check("two_writer.interleave_executed",
          b_ran["bytes"] and b_ran["json"] and "r" in result_box,
          f"b_ran={b_ran} exc={result_box.get('exc')}")
    r = result_box.get("r") or {}
    check("two_writer.members_manifest_honest",
          r.get("dir_fsynced_members") is True
          and r.get("dir_fsynced_manifest") is True,
          f"receipt={ {k: r.get(k) for k in ('dir_fsynced', 'dir_fsynced_members', 'dir_fsynced_manifest')} }")
    check("two_writer.pointer_honest",
          r.get("dir_fsynced") is True,
          f"receipt={ {k: r.get(k) for k in ('dir_fsynced', 'dir_fsynced_members', 'dir_fsynced_manifest')} }")
    check("two_writer.load_coherent",
          bool(r) and loads(o, gen))

    for o in owners:
        wipe(o)
    check("cleanup.ok", not _CLEANUP_ERRORS,
          "; ".join(_CLEANUP_ERRORS[:3]))

    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"\n{passed}/{len(RESULTS)} PASS")
    return passed == len(RESULTS)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
