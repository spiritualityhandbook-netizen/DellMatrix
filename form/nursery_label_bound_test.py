#!/usr/bin/env python3
"""Q-S2.1 — Nursery label bound: admitted labels preserved losslessly,
over-bound labels refused before mutation.

The defect (failing-first receipt: hidden_files/label_repro_2026-11-15.md):
the inference dock admits labels of 1..200 chars (inference_dock
MAX_LABEL_CHARS = 200, enforced by explicit refusal in
validate_proposal_output / validate_semantic_output) and hands them
verbatim to Nursery.add() — which stored label[:80], silently
destroying 1..120 chars of admitted content with no error.

The contract pinned here (Director mail 1a1df5bdadd2125e, Q-S2.1):
  - string labels up to MAX_LABEL_CHARS (200) are stored in full,
    exactly — in memory and on disk;
  - a label beyond the bound raises NurseryLabelError BEFORE any
    mutation or save: in-memory proposals unchanged, disk bytes
    byte-identical, and the instance stays usable afterwards;
  - legacy records (labels of at most 80 chars, the old cut's output)
    load and round-trip through later saves unchanged.

Caller check behind the contract (packet
SYSTEM_002_LABEL_CIRCUIT_2026-11-15.md): no production caller of
Nursery.add habitually passes labels over 200 chars — the dock bounds
at 200 by refusal, exchange validates seed labels to <=120 by
refusal, ringed_growth composes labels of at most ~70 chars,
supersession pre-cuts to 80, AutoGrowth's _nursery_auto has no
in-module production caller (test callers pass short literals), and
core_i_ops passes free user text, for which an explicit refusal is
the mandated behavior (today it is silently cut).

State hygiene: isolated temp nursery files only; never form/state.
Labels: INTEGRATION (Nursery + on-disk JSON + fresh-process reload).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")))

from form.dell_matrix.nursery import (  # noqa: E402
    MAX_LABEL_CHARS,
    Nursery,
    NurseryLabelError,
)

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def _label(ch: str, n: int) -> str:
    return ch * n


def main() -> int:
    tmp = tempfile.mkdtemp(prefix="nursery_label_bound_")
    path = os.path.join(tmp, "nursery_labelbound.json")
    n = Nursery.load(path)

    check("L0.bound_is_dock_bound", MAX_LABEL_CHARS == 200,
          f"MAX_LABEL_CHARS={MAX_LABEL_CHARS}")

    # L1: admitted maximum (200) stored exactly, memory + disk.
    lab200 = _label("A", 199) + "Z"
    p1 = n.add(lab200, words="admitted max")
    check("L1.admitted200_exact_memory", p1.label == lab200,
          f"len={len(p1.label)}")
    with open(path, "rb") as f:
        disk = json.loads(f.read().decode("utf-8"))
    check("L1.admitted200_exact_disk", disk[p1.id]["label"] == lab200)

    # L2: the 80/81 boundary — 81 chars was the first length the old
    # cut destroyed; both sides must now survive exactly.
    lab80 = _label("B", 80)
    lab81 = _label("C", 81)
    p80 = n.add(lab80, words="boundary low")
    p81 = n.add(lab81, words="boundary high")
    check("L2.boundary80_exact", p80.label == lab80)
    check("L2.boundary81_exact", p81.label == lab81,
          f"len={len(p81.label)} (old code stored 80)")

    # L4: unicode label (chars, not bytes) stored exactly.
    lab_uni = "λベル" * 40  # 120 chars, multibyte
    assert len(lab_uni) == 120
    pu = n.add(lab_uni, words="unicode")
    check("L4.unicode120_exact", pu.label == lab_uni,
          f"chars={len(pu.label)} utf8={len(pu.label.encode('utf-8'))}")

    # L7: the public-path seam — a label admitted by the dock's own
    # validator lands whole in the Nursery.
    from form.dell_matrix.inference_dock import validate_proposal_output
    lab150 = _label("D", 149) + "E"
    fields = validate_proposal_output(
        json.dumps({"label": lab150, "words": "via dock validator"}))
    p7 = n.add(fields["label"], words=fields["words"])
    check("L7.dock_admitted150_exact", p7.label == lab150,
          f"len={len(p7.label)}")

    # L3: 201 chars refused BEFORE mutation — error raised, in-memory
    # set unchanged, disk bytes byte-identical, instance still usable.
    with open(path, "rb") as f:
        bytes_before = f.read()
    count_before = len(n.proposals)
    lab201 = _label("F", 201)
    try:
        n.add(lab201, words="over bound")
        outcome = "no-raise"
    except NurseryLabelError:
        outcome = "label-error"
    except Exception as e:  # noqa: BLE001
        outcome = f"other:{type(e).__name__}"
    check("L3.refused_explicitly", outcome == "label-error", outcome)
    check("L3.no_inmemory_mutation", len(n.proposals) == count_before,
          f"count={len(n.proposals)}")
    with open(path, "rb") as f:
        bytes_after = f.read()
    check("L3.no_disk_mutation", bytes_after == bytes_before,
          f"bytes {len(bytes_before)} -> {len(bytes_after)}")
    fresh = Nursery.load(path)
    check("L3.fresh_load_unchanged",
          len(fresh.proposals) == count_before
          and all(p.label != lab201 for p in fresh.proposals.values()))
    p_ok = n.add("after refusal", words="still usable")
    check("L3.instance_still_usable", p_ok.label == "after refusal")

    # L5: legacy-shape record (exactly 80 chars — the old cut's output)
    # loads intact and round-trips through a later save unchanged.
    tmp2 = tempfile.mkdtemp(prefix="nursery_label_legacy_")
    path2 = os.path.join(tmp2, "nursery_labellegacy.json")
    legacy = Nursery.load(path2)
    lab_legacy = _label("G", 80)
    lp = legacy.add(lab_legacy, words="legacy record")
    reloaded = Nursery.load(path2)
    check("L5.legacy80_loads_intact",
          reloaded.proposals[lp.id].label == lab_legacy)
    reloaded.add("second idea", words="forces a later save")
    reloaded2 = Nursery.load(path2)
    check("L5.legacy80_roundtrips_through_save",
          reloaded2.proposals[lp.id].label == lab_legacy)

    # L6: fresh-process reload compares every stored label exactly.
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    code = (
        "import json,sys;"
        f"sys.path.insert(0, {root!r});"
        "from form.dell_matrix.nursery import Nursery;"
        f"n = Nursery.load({path!r});"
        "print(json.dumps(sorted(p.label for p in n.proposals.values())))"
    )
    r = subprocess.run([sys.executable, "-c", code],
                       capture_output=True, text=True)
    expected = sorted(p.label for p in n.proposals.values())
    try:
        got = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception:  # noqa: BLE001
        got = None
    check("L6.fresh_process_exact_compare", got == expected,
          f"proposals={len(expected)} rc={r.returncode}")

    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"nursery_label_bound_test: {passed}/{len(RESULTS)} PASS")
    return 0 if passed == len(RESULTS) else 1


def smoke() -> bool:
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
