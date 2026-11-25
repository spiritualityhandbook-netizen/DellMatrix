#!/usr/bin/env python3
"""Gate 4 / plan §11.2 per-PR tier: symbiosis ledger v1 pins.

Ledger v1 (symbiosis-ledger/1.0, baseline gate0-freeze-11933da,
PRE_AF) is frozen outside the repo; this suite pins its identity
inside the repo's own regress so a silent drift in the recorded
totals, hash, UNIQUE set, or clash catalogue fails the build:

1. Schema-v1 constants + frozen pair/identity totals + the
   ledger hash pin (constants, verified against the frozen
   ledger at freeze time; the §11.2 scheduled-tier full
   re-derivation remains a Gate/milestone event, NOT claimed
   by this per-PR suite).
2. The 8 UNIQUE_CANDIDATE pair pins.
3. The Gate 3 clash-catalogue pins (total, 6 systematic
   families, 8 sporadic pairs).
4. Bounded public-path canaries: world W (the 9 Gate 0 seeds)
   is rebuilt on an isolated owner and a bounded sample of
   frozen pairs is re-executed via execute_seed; a_ok / b_ok
   and the b_error prefix must match the frozen rows. This
   compares outcomes only — it never re-derives classes (no
   second classifier authority). All 26 canary pins were
   probed to hold on post-AF main before this suite landed.
"""
import glob
import os
import shutil

RESULTS = []

SCHEMA_VERSION = "symbiosis-ledger/1.0"
BASELINE_ID = "gate0-freeze-11933da"
CODE_COMMIT_BASELINE = "11933da"
HARNESS_VERSION = "gate2_sweep classifier v3 (R3/R4)"
EVIDENCE_LABEL = "PUBLIC_ENTRY_PATH (execute_seed)"
LEDGER_SHA256 = ("43fe6967ecb980ceccbd27224f6902bfe0"
                 "9aac3282e15885665b943046a0af39")
PAIR_FIELDS = ["pair", "a_seed", "b_seed", "a_ok", "a_error",
               "b_ok", "b_error", "a_writes_net", "b_writes_net",
               "store_b", "secs", "class", "q1", "q2",
               "class_overlay (optional)"]
IDENTITY_FIELDS = ["pair", "class", "first_ok", "second_ok",
                   "second_error", "q1", "q2"]
PAIR_TOTALS = {"FUNCTIONAL": 2047, "FUNCTIONAL_INDEPENDENT": 6682,
               "INTENDED_CLASH": 1163, "UNIQUE_CANDIDATE": 8,
               "DEFECT": 0, "SEAM_FAILURE": 0}
IDENTITY_TOTALS = {"IDENTITY_IDEMPOTENT": 91,
                   "IDENTITY_HONEST_REFUSAL": 9,
                   "IDENTITY_FAILURE": 0}
IDENTITY_TOTALS_RAW = {"IDENTITY_IDEMPOTENT": 91,
                       "IDENTITY_HONEST_REFUSAL": 8,
                       "IDENTITY_FAILURE": 1}
UNIQUE_PAIRS = ["07->51", "22->51", "29->51", "38->51",
                "85->42", "86->42", "87->42", "93->95"]
CLASH_TOTAL = 1163
CLASH_FAMILIES = {"missing_source": 193,
                  "rollback_target_invalid": 192,
                  "bridge_unavailable": 193,
                  "embed_unavailable": 193,
                  "catch_illegal": 192,
                  "commit_without_try": 192}
CLASH_SPORADIC = ["27->28", "85->86", "86->85", "87->57",
                  "87->88", "96->85", "96->86", "96->98"]

WORLD = [
    "08[Create] :: Garden Gate", "08[Create] :: Garden Path",
    "08[Create] :: Stone Arch", "55[Set] :: data=real",
    "55[Set] :: count=3", "51[Select] :: garden",
    "82[Group] :: crew", "74[Weight] :: data=0.5",
    "97[Define] :: note=memo",
]
INV = {
    0: "00[Nova] :: census", 1: "01[Initiate] :: census",
    7: "07[Link] :: garden_gate", 21: "21[Merge] :: garden_gate",
    22: "22[Split] :: garden_gate", 27: "27[Checkpoint] :: census",
    28: "28[Rollback]", 29: "29[Compress] :: garden gate path",
    38: "38[Distill] :: garden", 42: "42[Retry]",
    44: "44[Bridge] :: garden", 47: "47[Embed] :: garden",
    51: "51[Select] :: garden", 54: "54[Query] :: garden",
    55: "55[Set] :: probe=1", 56: "56[Get] :: data",
    57: "57[Compare] :: eq data real",
    85: "85[Move] :: count>moved_count", 86: "86[Delete] :: count",
    87: "87[Replace] :: data>datum", 88: "88[Patch] :: data=real2",
    93: "93[Try]", 94: "94[Catch]", 95: "95[Commit]",
    96: "96[Revert]", 98: "98[Alias] :: al=note",
}
# pair -> (class, a_ok, b_ok, b_error frozen full string)
CANARIES = {
    "07->51": ("UNIQUE_CANDIDATE", True, True, ""),
    "22->51": ("UNIQUE_CANDIDATE", True, True, ""),
    "29->51": ("UNIQUE_CANDIDATE", True, True, ""),
    "38->51": ("UNIQUE_CANDIDATE", True, True, ""),
    "85->42": ("UNIQUE_CANDIDATE", True, True, ""),
    "86->42": ("UNIQUE_CANDIDATE", True, True, ""),
    "87->42": ("UNIQUE_CANDIDATE", True, True, ""),
    "93->95": ("UNIQUE_CANDIDATE", True, True, ""),
    "27->28": ("INTENDED_CLASH", True, False,
               "acceptance_policy_denied"),
    "85->86": ("INTENDED_CLASH", True, False, "delete_missing:count"),
    "86->85": ("INTENDED_CLASH", True, False, "move_missing"),
    "87->57": ("INTENDED_CLASH", True, False, "type_mismatch"),
    "87->88": ("INTENDED_CLASH", True, False, "patch_miss:data"),
    "96->85": ("INTENDED_CLASH", True, False, "move_missing"),
    "96->86": ("INTENDED_CLASH", True, False, "delete_missing:count"),
    "96->98": ("INTENDED_CLASH", True, False, "alias_missing"),
    "00->21": ("INTENDED_CLASH", True, False, "missing_source"),
    "00->28": ("INTENDED_CLASH", True, False,
               "rollback_target_invalid"),
    "00->44": ("INTENDED_CLASH", True, False, "bridge_unavailable"),
    "00->47": ("INTENDED_CLASH", True, False, "embed_unavailable"),
    "00->94": ("INTENDED_CLASH", True, False, "catch_illegal"),
    "00->95": ("INTENDED_CLASH", True, False, "commit_without_try"),
    "55->56": ("FUNCTIONAL", True, True, ""),
    "93->94": ("FUNCTIONAL", True, True, ""),
    "00->01": ("FUNCTIONAL_INDEPENDENT", True, True, ""),
    "51->54": ("FUNCTIONAL_INDEPENDENT", True, True, ""),
}

OWNER = "SymbiosisLedger"


def _rec(name, cond, detail=""):
    RESULTS.append((name, bool(cond), str(detail)[:220]))


def _cleanup(owner):
    failed = []
    for f in glob.glob(os.path.join("form", "state", f"*{owner}*")):
        try:
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.remove(f)
        except OSError as e:
            failed.append(f"{f}: {e}")
    if failed:
        raise RuntimeError("cleanup failed: " + "; ".join(failed))


def main():
    _rec("schema version pin", SCHEMA_VERSION == "symbiosis-ledger/1.0")
    _rec("baseline pin", BASELINE_ID == "gate0-freeze-11933da"
         and CODE_COMMIT_BASELINE == "11933da")
    _rec("harness + evidence pins",
         HARNESS_VERSION.endswith("(R3/R4)")
         and EVIDENCE_LABEL.startswith("PUBLIC_ENTRY_PATH"))
    _rec("pair field list pin (15, overlay optional last)",
         len(PAIR_FIELDS) == 15
         and PAIR_FIELDS[-1] == "class_overlay (optional)")
    _rec("identity field list pin (7)", len(IDENTITY_FIELDS) == 7)
    _rec("ledger hash pin shape", len(LEDGER_SHA256) == 64
         and LEDGER_SHA256.startswith("43fe6967ecb980ce"))
    _rec("pair totals sum to 9,900",
         sum(PAIR_TOTALS.values()) == 9900, str(PAIR_TOTALS))
    _rec("pair totals pins (2047/6682/1163/8, zero defect)",
         PAIR_TOTALS["FUNCTIONAL"] == 2047
         and PAIR_TOTALS["FUNCTIONAL_INDEPENDENT"] == 6682
         and PAIR_TOTALS["INTENDED_CLASH"] == 1163
         and PAIR_TOTALS["UNIQUE_CANDIDATE"] == 8
         and PAIR_TOTALS["DEFECT"] == 0
         and PAIR_TOTALS["SEAM_FAILURE"] == 0)
    _rec("identity totals pins (91/9 corrected, raw 91/8/1)",
         IDENTITY_TOTALS["IDENTITY_IDEMPOTENT"] == 91
         and IDENTITY_TOTALS["IDENTITY_HONEST_REFUSAL"] == 9
         and IDENTITY_TOTALS_RAW["IDENTITY_FAILURE"] == 1
         and sum(IDENTITY_TOTALS.values()) == 100)
    _rec("UNIQUE pins are exactly the frozen 8",
         sorted(UNIQUE_PAIRS) == ["07->51", "22->51", "29->51",
                                  "38->51", "85->42", "86->42",
                                  "87->42", "93->95"])
    _rec("clash catalogue: total + family sum + sporadic",
         CLASH_TOTAL == 1163
         and sum(CLASH_FAMILIES.values()) == 1155
         and len(CLASH_SPORADIC) == 8
         and sum(CLASH_FAMILIES.values()) + len(CLASH_SPORADIC)
         == CLASH_TOTAL)
    _rec("canary sample covers uniques + sporadic + families",
         all(p in CANARIES for p in UNIQUE_PAIRS)
         and all(p in CANARIES for p in CLASH_SPORADIC)
         and len(CANARIES) == 26)

    from form.open import Program
    from form.mandell.core_ii_exec import attach
    from form.mandell.executor import execute_seed
    for pair, (cls, a_ok, b_ok, b_err) in sorted(CANARIES.items()):
        a, b = (int(x) for x in pair.split("->"))
        _cleanup(OWNER)
        p = Program(owner=OWNER)
        attach(p)
        for seed in WORLD:
            execute_seed(p, seed)
        ra = execute_seed(p, INV[a])
        rb = execute_seed(p, INV[b])
        got_err = str(rb.get("error") or "")
        _rec(f"canary {pair} ({cls})",
             ra.get("ok") == a_ok and rb.get("ok") == b_ok
             and got_err == b_err,
             f"a_ok={ra.get('ok')} b_ok={rb.get('ok')} "
             f"b_error={got_err!r} want {b_err!r}")
    _cleanup(OWNER)
    leftover = [x for x in os.listdir(os.path.join("form", "state"))
                if OWNER in x] \
        if os.path.isdir(os.path.join("form", "state")) else []
    _rec("cleanup leaves no residue", leftover == [], str(leftover))

    passed = sum(1 for _, ok_, _ in RESULTS if ok_)
    for name, ok_, detail in RESULTS:
        if not ok_:
            print(f"FAIL {name}: {detail}")
    print(f"SYMBIOSIS_LEDGER: {passed}/{len(RESULTS)}")
    return passed == len(RESULTS)


def smoke():
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
