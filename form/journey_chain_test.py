#!/usr/bin/env python3
"""Part VII / GP-E27 — journey harness family 1: J-01 Chain, J-02 Refusal.

Written failing-first as the plan-stage spec
(form/journey_chain_test_spec.py); code-stage step zero renamed it to
*_test.py and registered it in form/regress.py LIST in the same commit
(omitted-entry law).

Contract: Edition 1 file 06 (06_JOURNEY_ACCEPTANCE.md), executed
verbatim — this suite does not paraphrase the oracles into weaker form:

  J-01 Chain: "In REPL submit supported typed and legacy Mandell
  chain. Receipt lists every atom and its actual executed/skipped
  result; canonical Idea/Program state matches declared effects."
  Failure oracle: "One malformed middle atom refuses in precedence
  order; no unreported trailing side effect; first-failure provenance
  persists where authorized; reload and compare."

  J-02 Refusal: "Issue unsupported Dell address, malformed role,
  ambiguous identifier and unauthorized mutation. See specific refusal
  before execution." Failure oracle: "State/file generation and count
  unchanged; no stealth PP3 or GUI substitute; exception must not hide
  source/identity details needed for diagnosis."

Execution tier: PUBLIC_ENTRY_PATH — every journey action runs in a
literal `python3 -m form.repl` subprocess against a per-run isolated
owner; state comparison after cold reload uses the persistence loader
(the same like-for-like basis as form/four_way_equivalence_test.py:
reloaded vs reloaded, never in-memory vs reloaded).

J-02's four refusal classes, mapped to grounded seed-grammar shapes
(each refusal text verified first-hand in scratch-owner probes,
2026-11-21, before this spec was written):
  - unsupported Dell address: `500[Nope] :: x`
    -> "Seed error: unknown Dell 500"
  - malformed role: `08[Create](name="a", name="b")`
    -> "Seed error: duplicate role 'name'"
  - ambiguous identifier: `08[A[B]] :: x` (identifier ambiguous between
    aggregate and atom form) -> "Seed error: aggregate Dell conflict —
    use explicit atom form"
  - unauthorized mutation: `151[Harmonic] :: x` (reserved address;
    execution attempt on a Dell the caller may not execute — Ace's
    DC-8 ruling: documented, non-executing, explicit refusal)
    -> "Dell 151[reserved/not-active] refused: no executor on this path."
  Limitation, stated: a literal cross-owner mutation attempt is
  J-18's family (journey_exchange_test.py), not J-02's; J-02's
  unauthorized case here is the reserved-address execution attempt.

Baseline posture (plan section 5.1(iii)): this suite runs against the
pre-Parts main as a labeled BASELINE harness proof. Its grades are
evidence about the harness and the current program, recorded in
director-reports/GRAND_SYNCHRONIZATION_REHEARSAL_2026-11-20.md; the
GP-E27 rehearsal executions proper run against merged Parts I + II.

Run: python3 -m form.journey_chain_test
"""

import os
import shutil
import subprocess
import sys
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from form.persist import _STATE_DIR, _safe_owner, load as persist_load

RESULTS = []
_CLEANUP_ERRORS = []
RUN = uuid.uuid4().hex[:8]
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))
    print(f"{'PASS' if ok else 'FAIL'} {name} {detail}")


def cleanup(owner):
    safe = _safe_owner(owner)
    if not os.path.isdir(_STATE_DIR):
        return
    for name in os.listdir(_STATE_DIR):
        if safe in name:
            p = os.path.join(_STATE_DIR, name)
            try:
                shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
            except OSError as e:
                _CLEANUP_ERRORS.append(f"{p}: {e}")


def state_files(owner):
    safe = _safe_owner(owner)
    if not os.path.isdir(_STATE_DIR):
        return []
    return sorted(n for n in os.listdir(_STATE_DIR) if safe in n)


def run_repl(owner, lines, load=False):
    args = [sys.executable, "-m", "form.repl", "--owner", owner]
    if load:
        args.append("--load")
    proc = subprocess.run(args, input="\n".join(lines) + "\n",
                          capture_output=True, text=True, cwd=ROOT,
                          timeout=300)
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def snap(owner):
    prog = persist_load(owner)
    core_ii = getattr(prog, "core_ii", None)
    store = getattr(core_ii, "store", {}) if core_ii is not None else {}
    return {
        "store": store or {},
        "labels": sorted(n.get("label") for n in prog.nodes_payload()),
    }


def main():
    chain_owner = f"JChain{RUN}"
    refuse_owner = f"JRefuse{RUN}"
    for o in (chain_owner, refuse_owner):
        cleanup(o)
    try:
        # ---------------- J-01: Chain ----------------
        rc, out = run_repl(chain_owner, [
            '08[Create](name="Journey Typed Oak", skin="SPHERE") > 70[Count]',
            "55[Set] :: jtempo=120 >> 56[Get] :: jtempo",
            '55[Set] :: jfirst=1 >> 08[Create](name="ConflictA") :: ConflictB'
            " >> 55[Set] :: jlast=1",
            "56[Get] :: jlast",
            "08[Create] :: JParseOak >> 999[Nope] :: x >> 55[Set] :: jparse=1",
            "56[Get] :: jparse",
            "save",
            "quit",
        ])
        check("j01_repl_exit_clean",
              rc == 0 and "Traceback" not in out,
              f"rc={rc} traceback={'Traceback' in out}")
        check("j01_typed_chain_receipt_lists_atoms",
              "Chain atoms=2" in out
              and '-- 08[Create]' in out and "-- 70[Count]" in out
              and 'Created idea: "Journey Typed Oak"' in out,
              "typed chain: per-atom receipt + declared Create effect")
        check("j01_legacy_chain_receipt_lists_atoms",
              "Set jtempo=120" in out
              and "Get jtempo='120' status=ok" in out,
              "legacy lab chain: Set executed, Get reads the value back")
        check("j01_midchain_refusal_in_precedence_order",
              "Set jfirst=1" in out
              and "ARGUMENT_CONFLICT for 08[Create]" in out
              and "FlowThru blocked after fail" in out,
              "atom before the malformed atom executed and is reported; "
              "the malformed atom refuses by name; flow blocks there")
        check("j01_no_unreported_trailing_side_effect",
              "Get jlast=MISSING" in out,
              "the atom after the refusal never executed (key absent)")
        check("j01_reserved_atom_blocks_chain",
              "Created idea: \"JParseOak\"" in out
              and "Dell 999[Omega] reserved/not-active" in out
              and "Get jparse=MISSING" in out,
              "reserved middle atom blocks; prior effect reported; "
              "trailing Set never landed")
        check("j01_save_receipt", "Session saved." in out, "")

        # Cold reload: a second, separate process on the saved state.
        rc2, out2 = run_repl(chain_owner, [
            "56[Get] :: jtempo",
            "56[Get] :: jfirst",
            "56[Get] :: jlast",
            "quit",
        ], load=True)
        check("j01_reload_compare",
              rc2 == 0
              and "Get jtempo='120' status=ok" in out2
              and "Get jfirst='1' status=ok" in out2
              and "Get jlast=MISSING" in out2,
              f"rc={rc2}; first-failure provenance (jfirst) persists; "
              "the blocked trailing effect stays absent after reload")
        s = snap(chain_owner)
        store = {k: str(v) for k, v in (s["store"] or {}).items()}
        check("j01_canonical_state_matches_declared_effects",
              store.get("jtempo") == "120" and store.get("jfirst") == "1"
              and "jlast" not in store and "jparse" not in store
              and "Journey Typed Oak" in s["labels"]
              and "JParseOak" in s["labels"]
              and "ConflictA" not in s["labels"]
              and "ConflictB" not in s["labels"],
              f"store={store} labels={s['labels']}")

        # ---------------- J-02: Refusal ----------------
        rc3, out3 = run_repl(refuse_owner, [
            "500[Nope] :: x",
            '08[Create](name="a", name="b")',
            "08[A[B]] :: x",
            "151[Harmonic] :: x",
            "status",
            "quit",
        ])
        check("j02_unsupported_address_refused_before_execution",
              "Seed error: unknown Dell 500" in out3,
              "refusal names the unsupported address (500)")
        check("j02_malformed_role_refused_before_execution",
              "Seed error: duplicate role 'name'" in out3,
              "refusal names the malformed role ('name')")
        check("j02_ambiguous_identifier_refused_before_execution",
              "Seed error: aggregate Dell conflict" in out3,
              "identifier ambiguous between aggregate and atom form "
              "refuses, directing to the explicit atom form")
        check("j02_unauthorized_mutation_refused_before_execution",
              "Dell 151[reserved/not-active] refused" in out3,
              "reserved-address execution attempt refused explicitly "
              "(DC-8 documented refusal)")
        idx = out3.find("Dell 151[reserved/not-active] refused")
        tail = out3[idx:] if idx >= 0 else ""
        check("j02_state_and_count_unchanged",
              "ideas=1" in tail and "nursery=0" in tail
              and state_files(refuse_owner) == [],
              "after all four refusals: only the start-of-session idea, "
              "empty nursery, and no state file / generation was ever "
              "created for the owner")
        check("j02_session_survives_refusals",
              rc3 == 0 and "Traceback" not in out3 and "Goodbye." in out3,
              f"rc={rc3}; the session answered status and quit cleanly "
              "after the refusal battery")
    finally:
        for o in (chain_owner, refuse_owner):
            cleanup(o)

    check("Z.cleanup", not _CLEANUP_ERRORS, "; ".join(_CLEANUP_ERRORS))
    failed = [n for n, ok, _ in RESULTS if not ok]
    print(f"JOURNEY_CHAIN: {len(RESULTS) - len(failed)}/{len(RESULTS)} PASS")
    if failed:
        print("FAILURES:", ", ".join(failed))
    return 1 if failed else 0


def smoke():
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
