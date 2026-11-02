#!/usr/bin/env python3
"""Step 13 ledger checksum reconciliation verifier (2026-11-02).

Finding: ledger v1 and ledger v2 were hashed with the SAME
minus-field, sort_keys canonical-JSON method but DIFFERENT
separators:

- v1 (builder preserved, gate4_ledger_freeze.py):
  sha256(json.dumps(obj_minus_hash, sort_keys=True,
                    separators=(",", ":")).encode())
- v2 (builder not preserved; method recovered by variant search
  2026-11-02 and verified here):
  sha256(json.dumps(obj_minus_hash, sort_keys=True).encode())
  i.e. Python's DEFAULT separators (", ", ": ").

Both embedded checksums reproduce exactly under their own
method and fail under the other's; the bundle's v2 file must
also hash to its published file digest. Run: python3
step13_checksum_reconcile.py ; exit 0 iff every check holds —
no check is optional or skippable (RDI-2026-11-02).
Read-only: loads JSON files, constructs no Program().
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
V1 = os.path.join(HERE, "gate4_ledger_v1.json")
V2 = os.path.join(HERE, "gate4_ledger_v2.json")
# Published file digest of the in-bundle v2 ledger, as stated in
# STEP13_CHECKSUM_AND_BOUNDARY_RECONCILIATION_2026-11-02.md.
# Repository-relative and verifiable in any clone.
V2_FILE_SHA256 = ("061472c9232bd29be3c6ab8ca25136288dd4507ec9"
                  "f5f5cc7411408e34388c90")
# RDI-2026-11-02 correction: an earlier version compared the
# bundle copy against a machine-specific ~/workspace/... path
# and silently skipped that comparison when the path was
# absent. The Director caught it. There are no optional or
# skipped comparisons in this verifier: every check below is
# required, participates in the verdict, and a missing input
# is reported UNVERIFIED and fails the run — never skipped.


def file_sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def methods(obj):
    base = {k: v for k, v in obj.items() if k != "ledger_sha256"}
    return {
        "compact (v1 builder)": hashlib.sha256(json.dumps(
            base, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "default-sep (v2 builder)": hashlib.sha256(json.dumps(
            base, sort_keys=True).encode()).hexdigest(),
    }


def main():
    ok = True
    for label, path, own in (
            ("v1", V1, "compact (v1 builder)"),
            ("v2", V2, "default-sep (v2 builder)")):
        if not os.path.exists(path):
            print(f"{label}: UNVERIFIED — required file missing: {path}")
            ok = False
            continue
        obj = json.load(open(path))
        target = obj["ledger_sha256"]
        got = methods(obj)
        for name, val in got.items():
            match = val == target
            if (name == own) != match:
                ok = False
            print(f"{label} {name}: {val} "
                  f"match={match} (expected {'match' if name == own else 'no match'})")
        print(f"{label} embedded: {target}")
    if os.path.exists(V2):
        digest = file_sha(V2)
        same = digest == V2_FILE_SHA256
        print(f"v2 bundle file sha256 == published digest: {same} "
              f"({digest})")
        ok = ok and same
    else:
        print("v2 bundle file digest: UNVERIFIED — file missing")
        ok = False
    print("RECONCILED" if ok else "NOT RECONCILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
