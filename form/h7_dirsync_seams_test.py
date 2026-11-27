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

Each atomic_write call records its own directory-fsync outcome on
the function object (atomic_write's documented explicit-degradation
surface), but the checkpoint layer historically observed ONLY the
pointer's. A member copy whose directory sync degraded left the
generation's payload possibly non-durable while the commit receipt
asserted ``dir_fsynced: True`` with no checkpoint-layer surface for
the member or manifest degradation.

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

    for o in owners:
        wipe(o)
    check("cleanup.ok", not _CLEANUP_ERRORS,
          "; ".join(_CLEANUP_ERRORS[:3]))

    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"\n{passed}/{len(RESULTS)} PASS")
    return passed == len(RESULTS)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
