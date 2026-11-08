# UNI ACK — SLEEP PROTOCOL v2 WORKFLOW CONFIRMATION (2026-11-05)

Published on GitHub per the channel law (Director -> Uni by
email; Uni -> Director by GitHub). ACK to the Director's
confirmation email of 2026-11-05 20:09 CST (Gmail
1a1ae9df1f63cdf2; archived beside this file).

ACK: Received and adopted, with the single divergence below
named and resolved to the Director's stricter reading.

GOVERNING DIRECTIVE: goals workspace
`hidden_files/SLEEP_V2_DIRECTIVE.md` (state:
`SLEEP_V2_STATE.md`; analysis of record:
`goals/dellmatrix-capability-circuits/files/WORKFLOW_EVOLUTION_2026-11-05.md`).
Workspace-governing files; this ACK + the confirmation archive
ride the first v2 circuit PR (72-06 Class E repair) for their
repository record.

CURRENT ACTIVE CIRCUIT: 72-06 Class E repair (spelled-out
counts), branch uni/72-06-class-e-repair @
97c976bd44083d56c794d8c06284f39bd2f64b0f. Suite
form/translate_word_counts_test.py 21/21 (incl. bare-REPL
real-user-path checks); digit-only mutant killed (6/21);
regress x3 in flight at ACK time (leg 1 fwd terminal GREEN
rc=0). Any merge is labeled Ace-authorized under FIX-FIRST,
never Director-certified.

MERGE-GATE IMPLEMENTATION (exact): (1) section-32 freshness —
Gmail checked for Director mail newer than
DIRECTOR_MAIL_LAST_PROCESSED (2026-11-05 20:09 CST after this
fold) immediately before any merge; an unprocessed HOLD /
INSUFFICIENT_EVIDENCE / CORRECTION_REQUIRED for that PR stops
the merge. (2) Hard gate — same-step `gh pr checks`, every
check terminal PASS at the exact head, head re-verified at
merge time; SHAs only from terminal output verified against
gh/git. (3) Tier rules per the confirmation, including no
merge against a pending mandatory smoke. (4) Carve-outs:
PR #307 merges only on Ace's human tap; PR #294 (gated) and
PR #233 (fenced) never merge under this protocol.

DIVERGENCE: one. Uni's v2 draft Tier 1 allowed a docs/records
PR to merge before smoke completed; the confirmation requires
all repository-required checks terminal and forbids bypassing
a pending mandatory smoke. ADOPTED — directive text updated
before this ACK. No other divergence.

72-06 NOTE: PR #308 @ ee9e1fd is all-terminal (smoke run
42147038695 PASS 13m5s after the 20:08 review); head/evidence
unchanged; no re-presentation, per the review's terms.
