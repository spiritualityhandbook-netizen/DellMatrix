#!/usr/bin/env python3
"""Gate 4 — build + verify the FROZEN corrected ledger v1.

Inputs (all pre-existing evidence, none re-executed here):
  sweep/block_00..99.json  (9,900 raw pair rows, Gate 2)
  sweep/identity.json      (100 identity rows, R1 lens)
  gate2_rederived.json     (92 class_changes overlay, Gate 2 Addendum R3/R4)

Output: gate4_ledger_v1.json — one object:
  {schema_version, baseline, totals, identity_totals, rows, identity_rows,
   source_hashes}
Verification (asserts, fail-loud):
  - exactly 9,900 unique ordered pairs A!=B, each Dell 00-99 as A x99
  - overlay 'before' matches raw class for all 92 changes; applying it
    reproduces corrected totals EXACTLY 2047/6682/1163/8, DEFECT 0
  - identity: 100 rows, totals 91 IDEMPOTENT / 9 HONEST_REFUSAL / 0 FAILURE
    (87->87 reclassified by overlay identity note: raw identity file is
     checked separately; see gate2_rederived identity_87 field)
  - every row carries the v1 schema fields; q1/q2 present on all rows
  - row content hash + whole-ledger hash computed (sha256, canonical json)
"""
import hashlib
import json
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
SWEEP = os.path.join(HERE, "sweep")
OUT = os.path.join(HERE, "gate4_ledger_v1.json")

PAIR_FIELDS = ["pair", "a_seed", "b_seed", "a_ok", "a_error", "b_ok",
               "b_error", "a_writes_net", "b_writes_net", "store_b",
               "secs", "class", "q1", "q2"]
IDENTITY_FIELDS = ["pair", "class", "first_ok", "second_ok",
                   "second_error", "q1", "q2"]


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def file_sha(path):
    with open(path, "rb") as f:
        return sha_bytes(f.read())


def main():
    rows = []
    source_hashes = {}
    for i in range(100):
        p = os.path.join(SWEEP, f"block_{i:02d}.json")
        source_hashes[f"block_{i:02d}"] = file_sha(p)
        with open(p) as f:
            rows.extend(json.load(f)["rows"])
    assert len(rows) == 9900, len(rows)
    pairs = [r["pair"] for r in rows]
    assert len(set(pairs)) == 9900
    for a in range(100):
        mine = [p for p in pairs if p.startswith(f"{a:02d}->")]
        assert len(mine) == 99, (a, len(mine))
        assert f"{a:02d}->{a:02d}" not in mine
    for r in rows:
        for k in PAIR_FIELDS:
            assert k in r, (r["pair"], k)

    # overlay
    with open(os.path.join(HERE, "gate2_rederived.json")) as f:
        overlay = json.load(f)
    changes = overlay["class_changes"]
    assert len(changes) == 92, len(changes)
    by_pair = {r["pair"]: r for r in rows}
    for ch in changes:
        r = by_pair[ch["pair"]]
        assert r["class"] == ch["before"], (ch["pair"], r["class"], ch["before"])
        r["class"] = ch["after"]
        r["class_overlay"] = "gate2_rederive_R3R4"
    totals = Counter(r["class"] for r in rows)
    expected = {"FUNCTIONAL": 2047, "FUNCTIONAL_INDEPENDENT": 6682,
                "INTENDED_CLASH": 1163, "UNIQUE_CANDIDATE": 8}
    assert dict(totals) == expected, dict(totals)

    # identity rows
    ipath = os.path.join(SWEEP, "identity.json")
    source_hashes["identity"] = file_sha(ipath)
    with open(ipath) as f:
        irows = json.load(f)["rows"]
    assert len(irows) == 100
    for r in irows:
        for k in IDENTITY_FIELDS:
            assert k in r, (r.get("pair"), k)
    itot_raw = Counter(r["class"] for r in irows)
    # Gate 2 Addendum: 87->87 reclassified HONEST_REFUSAL by R4
    # (replace_missing designed prefix). Record both raw + corrected.
    id87 = overlay.get("identity_87")
    print("identity raw totals:", dict(itot_raw))
    print("overlay identity_87:", id87)
    assert id87 == {"before": "IDENTITY_FAILURE",
                    "after": "IDENTITY_HONEST_REFUSAL"}, id87
    for r in irows:
        if r["pair"] == "87->87":
            assert r["class"] == "IDENTITY_FAILURE"
            r["class"] = "IDENTITY_HONEST_REFUSAL"
            r["class_overlay"] = "gate2_rederive_R4"
    itot = Counter(r["class"] for r in irows)
    assert dict(itot) == {"IDENTITY_IDEMPOTENT": 91,
                          "IDENTITY_HONEST_REFUSAL": 9}, dict(itot)

    ledger = {
        "schema_version": "symbiosis-ledger/1.0",
        "baseline_id": "gate0-freeze-11933da",
        "code_commit_baseline": "11933da",
        "harness_version": "gate2_sweep classifier v3 (R3/R4)",
        "battery_version": "v0.1 S1 (+ identity R1 lens)",
        "evidence_label": "PUBLIC_ENTRY_PATH (execute_seed)",
        "pair_row_fields": PAIR_FIELDS + ["class_overlay (optional)"],
        "identity_row_fields": IDENTITY_FIELDS,
        "totals": dict(totals),
        "identity_totals_raw": dict(itot_raw),
        "identity_totals": dict(itot),
        "rows": rows,
        "identity_rows": irows,
        "source_hashes": source_hashes,
        "overlay": "gate2_rederived.json class_changes x92 (R3/R4)",
    }
    canon = json.dumps(ledger, sort_keys=True, separators=(",", ":")).encode()
    ledger["ledger_sha256"] = sha_bytes(canon)
    with open(OUT, "w") as f:
        json.dump(ledger, f, indent=1)
    print("pair totals:", dict(totals))
    print("ledger_sha256:", ledger["ledger_sha256"])
    print("wrote", OUT, os.path.getsize(OUT), "bytes")
    return True


if __name__ == "__main__":
    main()
