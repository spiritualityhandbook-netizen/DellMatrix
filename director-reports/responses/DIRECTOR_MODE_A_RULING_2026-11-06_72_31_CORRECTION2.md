# DIRECTOR RULING (Mode A relay) — Q-31R.1 CORRECTION_REQUIRED (round 2) + Q-31R.2 FIX bounded

Received via Ace copy-paste relay, 2026-11-06 ~09:40 CST
(Ace is the relay under wake mode; email watermark frozen
at 2026-11-06 06:26 CST; timers paused). Provenance:
Ace-relayed Director text, scoped exactly as written.
Folded into SLEEP_V2_STATE.md on receipt.

---

Q-31R.1 — CORRECTION_REQUIRED. Do not merge PR #314 at 616449f. The final commit changes seven report files. Its parent is 756916c, the code head covered by my second correction order. Uni's packet demonstrates the first correction. I reran the two outstanding probes on the exact PR head.

Probe	Result on 616449f
One worker, unreadable baseline, otherwise healthy checkpoint	commit_checkpoint ran once. Confirm returned success. Reload showed confirmed, one unit. The required result is refusal with zero commit calls.
CURRENT is a directory or a dangling symlink	Both returned ('absent', None). Both must return unreadable.

The existing baseline test starts with a winner that already committed, so the stale loser can be refused for a separate reason. That explains how 42/42 passes while a lone worker still commits after the baseline read fails.

Q-31R.2 — FIX, bounded to 72-31. Uni is authorized to repair baseline refusal and pointer classification in this PR. Broader save-path changes retain their separate gate.

DIRECTOR → UNI Ω | #314 | CORRECTION_REQUIRED

Update the existing PR. First add the single-worker test and the real directory and dangling-link cases. Prove they fail at 616449f. Then repair the two paths. On baseline uncertainty, require explicit refusal, zero checkpoint calls, proposal still pending after fresh-process reload, recovery evidence preserved, and owner lock released. Keep genuine first-confirm success as the missing-pointer control.

Push the new code head and relay its SHA with the focused results as soon as they pass. Start T3 on that same head immediately. I can check the probes while regression runs. Keep 72-36 next.
