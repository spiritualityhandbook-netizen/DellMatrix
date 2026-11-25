# DIRECTOR REPORT — Step 3c: DAF-02 (third presentation)

Status: IMPLEMENTED-VERIFIED, awaiting Director re-ruling.
NOT certified. Evidence submitted, never a certificate.

## Finding re-presented
DAF-02 (OPEN after Mode D ruling on step 3b at 1ab1afe):
step 3b repaired the Query disclosure but sanitized executable
state in place. Director's two probes, both returning success
with clean controls:
(1) Sanitize -> Get, then a Set using last_result copies
    "password=[REDACTED]" instead of the original value;
(2) Sanitize -> Set, then Revert restores a redacted value,
    corrupting the rollback.
Cause: last_result and rollback snapshots are executable
state, not display evidence; PR #168 sanitized them in place.

## Bounded ruling requested
Certify DAF-02 as repaired within this bounded scope:
canonical last_result values, control frames, and rollback
checkpoints (shot() snapshots, Try checkpoints) are unchanged
by a Sanitize chain; redaction applies only to detached
outward-facing evidence copies; the step 3b Query-disclosure
repair is retained on all detached surfaces.

## Frozen candidate
PR #173, candidate bc61a7b, tree 18e508b
(fix commit 32a9b3d; base lineage 40e504d + merge of main
beb9f3a, docs-only delta).

## Closure addendum (2026-10-31)
Exact-head CI on bc61a7b verified COMPLETE in a separate
step before merge: Python package run 41241300749 SUCCESS
(completed 20:58:07Z); Form smoke run 41241300784 SUCCESS
(completed 21:07:51Z). PR #173 merged as bd71c1e (merge
tree 18e508b == candidate tree; parents beb9f3a + bc61a7b).
Fresh-clone regress at merge bd71c1e: 210/210 GREEN
(log step3c_freshclone_regress.log). IMPLEMENTED-VERIFIED;
DAF-02 re-presented (third presentation) for Director
re-ruling. NOT certified.

## Fix (subtractive; one redaction authority retained)
- form/mandell/chain_exec.py execute_range: per-atom in-place
  sanitization of last_result predicate/error removed.
- form/mandell/chain_exec.py execute_chain: end-of-chain
  in-place sanitization of st.last_result / last_frame /
  last_control / frames removed. Detached copies
  (atom_results, returned core_ii snapshot) remain sanitized;
  messages/traces/history/saved JSON remain redacted at their
  own writers.
- form/mandell/core_ii_exec.py shot(): snapshot sanitization
  removed — snapshots are rollback checkpoints Revert
  restores from.
- Audit: every other sanitize_* call site operates on a
  detached copy or an evidence writer (grep-verified);
  Try checkpoints (_ckpt in spectrum_ops) were never
  sanitized — suite-covered.

## Before / after counterexamples
New suite form/step3c_sanitize_state_test.py (24 checks):
- Failing-first on the pre-fix tree: 18/24. Failures were
  exactly: live last_result != control; probe 1 live value
  redacted and downstream Set copied "password=[REDACTED]";
  probe 2 Revert restored "password=[REDACTED]"; nested
  (Sequence) last_result != control.
- After the fix: 24/24 — both counterexamples require exact
  downstream-value equality AND exact Revert restoration;
  live last_result/frames/snapshots exactly equal the
  non-Sanitize control; detached result/messages/traces/
  history/outcome/last_flow/saved JSON marker-free.
- Step 3b suite amended to the 3c contract (its two live-state
  "surfaces" removed; the redacted-predicate assertion flipped
  to the real predicate): 21/21, Query-disclosure checks
  retained.

## Mutants (defect-restoring; all killed)
M1 end-block in-place sanitization restored: 19/24.
M2 shot() sanitization restored: 23/24 — exactly probe 2.
M3 per-atom descriptor sanitization restored: 21/24.
Each reverted and re-verified 24/24.

## Neighborhoods + regress
step3 security 23/23; step4 operand transport 27/27;
step5 exchange 20/20; daf09 timeout tree 16/16.
Regress x3 on bc61a7b: fwd 210/210 GREEN; --twice 210/210 +
210/210 GREEN; --order rev 210/210 GREEN (regress count
209 -> 210 with the new suite).

## Limitations
- Synthetic canary only; no real user state probed.
- Frames equality is exercised on Query and Sequence-nested
  chains; control-frame conditions carrying secret-shaped
  values through Branch/While condition evaluation were not
  separately probed (frames follow the same untouched-state
  path; no in-place writer remains).
- Code scanning: EVALUATION_UNAVAILABLE (unchanged standing
  state; never a PASS).
