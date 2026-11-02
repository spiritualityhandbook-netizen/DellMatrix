# STEP 13 — CHECKSUM AND BOUNDARY RECONCILIATION (2026-11-02)

**Status: SUBMITTED for the Director's re-ruling. The step-13
provisional exception is NOT self-lifted by this record.**

This record closes execution order #3 of
DIR-2026-11-02-CONSOLIDATED-R1, which kept step 13
PROVISIONAL for two stated reasons: (a) ledger v2's canonical
checksum "remains unreproduced under the documented v1
method," and (b) the tested public boundary required precise
documentation. Both are addressed below with exact method
specifications.

## Part 1 — The checksum reproduces; the two builders differ by one argument

Canonical-hash method, stated completely for each ledger
(JSON of the ledger object with its own `ledger_sha256`
field removed, UTF-8 encoded, SHA-256):

- **Ledger v1:** `json.dumps(obj, sort_keys=True,
  separators=(",", ":"))` → reproduces the embedded
  `43fe6967ecb980ce…` exactly. (This is the method in the
  preserved builder, `gate4_ledger_freeze.py`.)
- **Ledger v2:** `json.dumps(obj, sort_keys=True)` — Python
  DEFAULT separators `(", ", ": ")` → reproduces the
  embedded `de5354f0254cf87b1f3e0d1df30006d70eb846ffdc77
  4b989e0bb4a0cfc2bafd` exactly.

Neither hash reproduces under the other ledger's separators
(v1 under default separators: 5a738c27…; v2 under compact:
ef65bc7e…). The v2 checksum was therefore never incorrect;
it was computed with default separators, and every prior
reproduction attempt applied v1's compact separators.

**Verification, runnable:** `step13_checksum_reconcile.py`
is included in this bundle at
`director-reports/evidence/step13/step13_checksum_reconcile.py`.
Executed against the published artifact
(`evidence/step13/gate4_ledger_v2.json`, file SHA-256
`061472c9232bd29be3c6ab8ca25136288dd4507ec9f5f5cc741140
8e34388c90`, byte-identical to the working ledger; 9,900
rows + 100 identity rows; class totals FI 6375 / IC 1528 /
F 1989 / UNIQUE 8): exit 0, output RECONCILED. A 105-variant
search (separator sets × sort × indent × dropped-header
subsets × rows-only × file-bytes-minus-hash-line) found the
default-separator sorted form to be the ONLY match for v2.

**Corrections owned:** (1) `STEP13_PACKET.md`'s "(same
canonical-hash method as v1; verified after write)" was
inaccurate in the separator detail. (2) The Priority 2
`evidence/step13/EVIDENCE.md` limit ("v2's canonical hash
does NOT reproduce under v1's minus-field method and the v2
freeze builder was not preserved as a file") was literally
true but materially incomplete; this record supersedes that
limit statement. The original files are preserved
unrewritten; this dated record is the correction layer.

## Part 2 — The tested public boundary, precisely

Verified by first-hand reads of the harness at the exact
freeze head named in ledger v2's header (baseline_id
`step13-freeze-c94e223`, commit c94e223). Per pair row, the
sweep:

1. cleared the sweep owner's state;
2. built a `Program` pre-loaded by executing the frozen
   9-seed WORLD recipe through the same executor;
3. called `form.mandell.executor.execute_seed` with the
   battery-v0.1 invocation for Dell A, snapshotted, then
   for Dell B, snapshotted (battery = exactly ONE
   invocation seed per Dell; recorded errata INV[86],
   INV[41]); identity rows ran the same invocation twice;
4. classified harness-side over the snapshot diffs.

**One-sentence form:** Step 13's 9,900 pairs were executed
through the public Python seed executor
(`form.mandell.executor.execute_seed`) on a harness-built
Program, one battery invocation per Dell in A-then-B
sequence; the interactive REPL and its observation,
English, and flow layers were not exercised.

**Honest label:** PUBLIC_ENTRY_PATH (executor) — the
executor's front door, not a private leaf or direct Dell
call. Explicitly NOT REAL_USER_PATH: at the same freeze
head, the REPL (`form.repl`) reaches `execute_seed` only
through `execution_observer.observe_seed_execution`, and
the sweep bypassed that wrapper plus `_execute_intent` /
translate, `flow_executor`, and `english_composer`. Also
outside the boundary: multi-atom seeds as a user would type
them, English input, persistence across sessions (owner
state was cleaned before every pair), and any GUI/launch
path.

## Requested ruling

That the Director re-rule on step 13 with (a) the checksum
exception's ground removed under C-Q2's conditions — the
internal checksum now verifies against its stated method —
and (b) the boundary documented as PUBLIC_ENTRY_PATH
(executor), not REAL_USER_PATH. Ledger v2's other verified
properties stand as published (row counts, class totals,
the exact 369-change v1→v2 diff). Nothing in this record
argues whole-program certification (order #5 remains gated
on its own conditions), and DAF-09 (order #4) is untouched.
