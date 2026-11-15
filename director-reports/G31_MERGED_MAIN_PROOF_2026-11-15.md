# G31-CONTRACT-02 — IMMUTABLE MERGED-MAIN PROOF (Director closure item 2 for PR #417)

*Produced 2026-11-15 by Uni (main session) in a fresh clone. Every value below is copied from terminal output of the commands shown. This document claims NO MWL credit — credit remains the authorities' ruling (Director closure items 3–4 are handled in the companion reconciliation).*

## 1. MERGE IDENTITY

- PR: #417 (G31-CONTRACT-02: execution profiles on FLOW_CONTRACT + D-6 refusal visibility)
- Candidate head: a20997d5
- Merge commit: b39c6a062b8dabd7d34c69d8c50c0e8735b089c2 (Merge: cc1e2ad a20997d)
- Merged at: 2026-11-14T20:38:06Z
- Changed paths (3): form/mandell/control_runtime.py (+33), form/mandell/flow_executor.py (+14/−), form/mandell/g31_contract_test.py (+238, new)

## 2. AUTHORITY TRAIL

- Keeper terminal CONFIRM at head a20997d5: PR comment 6883825576.
- Director FINAL DISPOSITION (merge authorization): relayed by Ace in the main chat 2026-11-14 14:37 CST (sanctioned channel; the ruling mail itself was folded under §35 after repeated safety flags on raw reads).
- §32 transaction at merge: mail triage in the same step; no HOLD outstanding on #417.
- Trailing second certification: DISCHARGED — the Keeper's watermark of 2026-11-14 23:19 CST lists the trailing ledger as DD-18 + Q-DD42.1 only (G31 no longer carried). Certification of the full THL circuit remains the Director's call.

## 3. PRE-MERGE EVIDENCE (at candidate head a20997d5)

- ×3 regression campaign, terminal green (logs: goal hidden_files/g31_campaign/): forward 286/286, twice 572/572, reverse-order 286/286, all exit 0. Receipts posted as PR comment 6884872026 (Director closure item 1 — discharged 2026-11-14).
- Exact-head CI at a20997d5: terminal green before merge (hard gate).

## 4. MERGED-MAIN VERIFICATION — RE-RUN 2026-11-15 (this document's own evidence)

Fresh clone of the real GitHub remote; main tip at verification time: **17ae4ce86743d9c5ff848a1b48111119d9bf9a32** (2026-11-15 06:24:49 -0600).

1. Ancestry: `git merge-base --is-ancestor b39c6a06 HEAD` → TRUE. The #417 merge is in current main's history.
2. Suite: `form.mandell.g31_contract_test` smoke() → **RESULT: 20/20 PASS; smoke = True**.
3. REAL_USER_PATH (public REPL entry, `python3 -m form.repl --owner G31PROOF1115B`), input `150[Future] >>> 70[Count]` → verbatim output:
   > Flow refused (Correspondence composition profile): flow '>>>' is REQUIRES_RUNTIME_SUPPORT, not executable
   > This line was not executed. Raw Mandell seeds run under the canonical chain profile (all nine operators).
   The refusal is visible by name and nothing executed — the D-6 contract, live on merged main.

## 5. SCOPE AND LIMITS OF THIS PROOF

- Proves: the merged code is present in current main, its registered suite passes there, and the refusal contract behaves identically through the public REPL path.
- Does not prove: MWL 167–170 credit (authorities' ruling; see companion reconciliation), whole-program certification (WITHHELD — DAF-09), or any claim beyond the G31 contract's stated scope.
