#!/usr/bin/env python3
"""Core I locally closable clusters: recovery, inverse, measure, external contracts."""
from __future__ import annotations

import os
import shutil
import tempfile

from form.open import open_program
from form.mandell.executor import execute_seed
from form.persist import load, save
from form.mandell.core_i_recovery import latest_checkpoint


def smoke() -> bool:
    print("=== CORE I MATURITY ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" | {detail}" if detail and not ok else ""))
        r.append(bool(ok))

    p = open_program("CpA")
    execute_seed(p, "08[Create] :: keep_unit")
    execute_seed(p, "55[Set] :: k=1")
    out = execute_seed(p, "27[Checkpoint]")
    rec("checkpoint_unified_state", out.get("ok") is not False and bool(latest_checkpoint("CpA")))
    execute_seed(p, "08[Create] :: extra_unit")
    execute_seed(p, "55[Set] :: k=9")
    out = execute_seed(p, "28[Rollback]")
    restored = out.get("new_program")
    rec("rollback_unified_state", restored is not None and "keep_unit" in restored.cube.session.plane.units and "extra_unit" not in restored.cube.session.plane.units and restored.core_ii.store.get("k") == "1")

    p = open_program("TxIso")
    execute_seed(p, "08[Create] :: base")
    execute_seed(p, "27[Checkpoint]")
    execute_seed(p, "55[Set] :: k=1")
    execute_seed(p, "93[Try]")
    execute_seed(p, "88[Patch] :: k=2")
    execute_seed(p, "96[Revert]")
    rec("tx_independent_from_checkpoint", latest_checkpoint("TxIso") and p.core_ii.store.get("k") == "1")
    execute_seed(p, "55[Set] :: k=3")
    execute_seed(p, "93[Try]")
    execute_seed(p, "88[Patch] :: k=4")
    execute_seed(p, "27[Checkpoint]")
    execute_seed(p, "96[Revert]")
    rec("checkpoint_independent_from_tx", p.core_ii.store.get("k") == "3" and bool(latest_checkpoint("TxIso")))

    p = open_program("SavR")
    execute_seed(p, "08[Create] :: saved")
    execute_seed(p, "27[Checkpoint]")
    execute_seed(p, "08[Create] :: later")
    out = execute_seed(p, "28[Rollback]")
    q = out.get("new_program")
    tmpd = tempfile.mkdtemp(prefix="dm_corei_rb_")
    try:
        path = os.path.join(tmpd, "corei_rb.json")
        save(q, path)
        loaded = load("SavR", path)
    finally:
        shutil.rmtree(tmpd, ignore_errors=True)
    rec("save_after_rollback", "saved" in loaded.cube.session.plane.units and "later" not in loaded.cube.session.plane.units)
    p = open_program("LdCp")
    execute_seed(p, "08[Create] :: parked")
    execute_seed(p, "55[Set] :: z=2")
    execute_seed(p, "27[Checkpoint]")
    blob_path = latest_checkpoint("LdCp")
    loaded = load("LdCp", blob_path)
    rec("load_after_checkpointed_state", "parked" in loaded.cube.session.plane.units and loaded.core_ii.store.get("z") == "2")

    p = open_program("Inv")
    execute_seed(p, "23[Lock]")
    rec("lock_sandbox_on", p.sandbox.on is True)
    execute_seed(p, "24[Unlock]")
    rec("unlock_sandbox_off", p.sandbox.on is False)
    execute_seed(p, "32[Pause]")
    rec("pause_idle", p.avatar.body.locomotion.name == "IDLE")
    execute_seed(p, "33[Resume]")
    rec("resume_walk", p.avatar.body.locomotion.name == "WALK")
    miss = execute_seed(open_program("Miss"), "28[Rollback]")
    rec("invalid_rollback_explicit", miss.get("error") == "rollback_missing")

    p = open_program("Mirr")
    before = list(p.cube.session.plane.units)
    execute_seed(p, "18[Mirror]")
    rec("mirror_read_only", list(p.cube.session.plane.units) == before)
    execute_seed(p, "35[Discover]")
    rec("discover_machine_readable", isinstance(getattr(p, "last_discover", {}).get("ids"), list) and p.last_discover.get("count") == len(before))
    execute_seed(p, "40[TokenCount]")
    rec("tokencount_numeric", isinstance(getattr(p, "last_measure", {}).get("value"), int))
    execute_seed(p, "34[Stamp] :: gate")
    rec("stamp_machine_readable", p.last_stamp.get("mark") == "gate" and "T" in p.last_stamp.get("ts", ""))
    rec("profile_has_runtime_fields", any("ideas=" in m for m in execute_seed(open_program("Pr"), "49[Profile]").get("messages") or []))

    br = execute_seed(open_program("Br"), "44[Bridge] :: llm")
    rec("bridge_unavailable_explicit", br.get("error") == "bridge_unavailable" and br.get("ok") is False)
    em = execute_seed(open_program("Em"), "47[Embed]")
    rec("embed_unavailable_explicit", em.get("error") == "embed_unavailable" and em.get("ok") is False)

    p = open_program("Str")
    execute_seed(p, "08[Create] :: a")
    execute_seed(p, "08[Create] :: b")
    execute_seed(p, "21[Merge] :: ab")
    rec("merge_does_not_destroy_parents", "a" in p.cube.session.plane.units and "b" in p.cube.session.plane.units and any(uid.startswith("ab") or "merge" in uid or uid == "ab" for uid in p.cube.session.plane.units))
    before = set(p.cube.session.plane.units)
    execute_seed(p, "22[Split] :: a")
    rec("split_preserves_parent", "a" in p.cube.session.plane.units and set(p.cube.session.plane.units) - before)

    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
