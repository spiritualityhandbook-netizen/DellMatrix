# UNI — #307 GATE AUDIT (Director work order, Gmail 1a1b92040d45fc35, items 1–4)

Recorded by Uni, 2026-11-07, in the 72-40 circuit records.
PR #307 (72-16 investigation, evidence only) merged
2026-11-08T03:05:55Z as
cc3219123a3365952fa2796dddb85e6ab596fa6f from head
d395f89848d65a0a31c60488164e7aad3ea4d521, on Ace's
explicit human tap (chat, 2026-11-07 20:51 CST).

## Item 1 — exact-head Form smoke: TIMING BREACH CONFIRMED

Form smoke run 42440371513 at exact head d395f898
completed SUCCESS at 2026-11-08T03:12:41Z — 6m46s
AFTER the merge. Builds (42440371576) and
verify-72-16 (42440371575) were SUCCESS before the
merge. The hard gate's terminal-smoke requirement
was therefore NOT met at merge time. Gate
compliance is NOT claimed retrospectively; the
check itself passed, late.

Root cause (per the executing cycle's own
correction addendum): the merge was executed by
the 21:01 hourly-cycle session on an interim
readout that reported a background poll as
"completed success"; the poll's authoritative
terminal output shows all 10 polls returned
"in_progress", and the same-step `gh pr checks`
showed smoke PENDING. An interim/truncated
readout fabricated a terminal verdict (TOOLS.md
truncated-readout law), and a disagreeing
authoritative source was overridden.

UNIQUE PROCESS DEFECT (logged): merge executed by
a background cycle session on a false interim
terminal readout, against a pending reading from
`gh pr checks`.

CONTAINMENT (Uni-imposed, effective immediately):
(1) merges execute ONLY from the main session —
cycle/heartbeat sessions corroborate and record
but never merge, regardless of recorded
authorizations; (2) DISAGREEMENT-VETO — when two
gate sources disagree, the merge STOPs; a pending
reading from any authoritative source vetoes a
success reading from another until they agree
terminally; (3) interim/truncated readouts are
never gate evidence.

## Item 2 — tree equality: PASS

Approved candidate tree (d395f898) ==
cc321912 merge tree ==
dcbb9275b4ea494e806264430bf643186fe39a35,
git-verified on both commits. The merged content
is exactly the approved candidate. Blast radius:
records/evidence only (72-16 report, INDEX,
register row, evidence bundle, responses) +
.github/workflows/verify-72-16.yml; NO production
code (form/, gui/ untouched).

## Item 3 — merged-main CI: PASS (push route)

At merge SHA cc321912: Python package 42441265016
SUCCESS + Form smoke 42441265004 SUCCESS, both
terminal, both on the push-workflow route (not
merge-ref checks).

## Item 4 — records

#307 is recorded MERGED, investigation-only, in
INDEX + register (this PR). 72-16 is NOT complete;
the semantic-authority divergence (DD-08) stays
OPEN/GATED; R-2 remains mapping only.

## Item 5 — status

Bounded R-1 canonical parser/operand-preservation
proposal + failing-first tests + compatibility
impact: NOT in this PR; it is the separate next
circuit after 72-40 under the completion-first
sequence (Director priority reset, Gmail
1a1b923041cf0720).
