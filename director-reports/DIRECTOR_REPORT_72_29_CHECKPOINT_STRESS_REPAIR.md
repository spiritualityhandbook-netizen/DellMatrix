# DIRECTOR REPORT — 72-29 REPAIR: Checkpoint Sealing / Rollback / Directory-Sync Stress

**Circuit:** 72-29 repair, executed under **Ace's FIX-FIRST
ruling (2026-11-05 19:53 CST)** and Sleep Protocol v2 queue
item 4 (first item of the §6.6 persistence batch). This merge
(when gated) is Ace-authorized, **not** Director-certified.
**Base:** main `3677178` (merge of PR #311). **Objective:**
"Stress checkpoint sealing, rollback, directory-sync failure
(P1/E) (= SM-36)". **Gap closed by this circuit:** the
failed-fsync / directory-sync / missing-generation injection
pass named in the register.

## Investigation (probe at main 3677178)

Existing coverage in `form/mandell/dcc_xviii_test.py` (controls
A–W: normal G1/G2, crash at every pre-commit stage, missing /
corrupt / swapped members, manifest/pointer corruption, stale
generations, retention, both-invalid failure, cross-process
matrix) was mapped and NOT duplicated. A probe
(`hidden_files/72-29_probe.py`, unique owners, terminal
output) scored **8/10**: controls hold (file-fsync abort with
the previous generation authoritative; missing-manifest
recovery + explicit fail-closed with no previous; same-id
retry; dir-fsync commit + hash-verified load). Three defect
classes were CONFIRMED:

- **D1 — a pre-Phase-2 (graph-less) generation crashes
  `load_checkpoint` with a RAW `KeyError: 'graph'`.**
  `_read_manifest` explicitly tolerates a manifest with no
  graph member ("generations sealed before the graph member
  existed ... rollback treats it as 'graph cleared'"), but
  `_load_generation` dereferenced `manifest["members"][kind]`
  for every kind including `graph`, and `load_checkpoint`'s
  recovery catches only `CheckpointLoadError` — so the raw
  KeyError escaped with no recovery and no honest fail-closed
  error. Rollback precedent (`core_i_recovery.py`) stages an
  EMPTY graph log for such generations: the intended semantic
  is loadable, not fatal. `_load_generation` only
  fingerprint-validates the graph member, never consumes it.
- **D2 — directory-sync failure is invisible at the
  checkpoint layer.** `atomic_write`'s documented contract is
  best-effort directory fsync with EXPLICIT degradation
  (`atomic_write_json._last_dir_fsynced`), but no caller
  outside `atomic_write.py` read that value (grep over
  `form/`: zero hits) and the commit receipt carried no fsync
  field — degradation could not be verified from any
  checkpoint surface.
- **D3 — a real fsync/write `OSError` inside `atomic_write`
  escapes RAW** (not `AtomicWriteError`), missing
  `checkpoint_generation`'s `CheckpointCommitError` wraps and
  bypassing `commit_checkpoint`'s eager-convergence handler,
  which is keyed on the wrapped type.

**GATE classification:** the repairs are local to
`checkpoint_generation.py` + `atomic_write.py` (error
wrapping / receipt observability / absent-member tolerance).
They do not touch the everyday Program/Nursery pair save
path, Q1 locking, or pair atomicity. => FIX circuit, **T3
evidence tier** (stateful). If the Director rules checkpoint
sealing is save-path, the same suite + grounding convert to
the GATE packet unchanged (Q-29R.2).

## Repair (bounded)

- `checkpoint_generation.py` `_load_generation`: skip an
  absent graph spec exactly as `_read_manifest` tolerates it;
  all other kinds stay fail-closed. Receipt members stay
  as-manifest.
- `atomic_write.py` `_atomic_replace`: a real write/fsync
  `OSError` is wrapped into `AtomicWriteError` (canonical
  target-untouched semantics unchanged; `AtomicWriteError`
  itself, including the injected `temp_write` failure, passes
  through; non-`OSError` exceptions propagate as-is).
- `checkpoint_generation.py` `_seal_members` / manifest /
  `_commit_pointer` wraps broaden to
  `(AtomicWriteError, OSError)` -> `CheckpointCommitError`,
  so any member/manifest/pointer copy failure aborts through
  the eager-convergence handler.
- `commit_checkpoint` receipt gains `"dir_fsynced"`, captured
  from `atomic_write_json._last_dir_fsynced` immediately
  after the pointer write. Additive only.
- New suite `form/checkpoint_generation_stress_test.py`
  registered in `form/regress.py` (LIST 241 -> 242).

Files changed (repair commits): `form/dell_matrix/atomic_write.py`,
`form/mandell/checkpoint_generation.py`,
`form/checkpoint_generation_stress_test.py` (new),
`form/regress.py`. Records in this PR: this report, INDEX
rows, the 72-29 register line, and the verbatim archive of
the Director's 2026-11-06 00:41 CST 72-17 R-B
ALL_AI_CONFIRMATION_PASS ruling (owed a ride since PR #311).

## Evidence

- **Failing-first:** suite run at unrepaired head (branch
  commit `b1bac2d` on main `3677178`): **10/15 PASS, exit 1**
  — all 10 controls PASS, all 5 defect checks FAIL
  (`legacy_no_graph` x2 raw `KeyError`; dir-sync receipt
  carries no fsync field; raw `OSError` x2).
- **Suite after repair:** `form/checkpoint_generation_stress_test.py`
  **15/15 PASS, rc=0** (re-run at branch head `703d7f4`
  before this report commit: 15/15, rc=0). Neighbours:
  dcc_xviii 89/89, dcc_xvi atomicity 101/101, sm35
  pair-atomic 45/45.
- **Mutant:** disabling the D1 graph skip -> suite **13/15**
  (the exact D1 profile: both `legacy_no_graph` checks FAIL).
  Reverted by **inverse edit only**; suite back to 15/15;
  diff clean (repair diff: 3 files, +41/-4 at commit time).
- **Regression:** full regress x3 sequential — **ALL TERMINAL
  GREEN** (logs in the goal workspace,
  `hidden_files/72-29-repair_logs/`): leg 1 (order=fwd)
  242/242 GREEN, `LEG1_RC=0`; leg 2 (order=fwd, twice)
  pass 1 242/242 + pass 2 242/242 GREEN, `LEG2_RC=0`;
  leg 3 (order=rev) 242/242 GREEN, `LEG3_RC=0`; `CHAIN_DONE`.
- **Register:** the 72-29 line records this repair; its
  status prefix stays **PARTIAL** pending the Director's
  confirmation — no status the evidence does not support is
  claimed, and 72-29 is not counted COMPLETED.

## Anticipated probes

- *"Why is a missing graph member loadable rather than
  fail-closed?"* — the manifest validator already accepts it
  by design (pre-Phase-2 generations), rollback's canonical
  semantic is "graph cleared" (empty log), and the loader
  never consumes the graph member — it only fingerprint-
  validates members that exist. Every other member kind
  remains fail-closed, and the suite pins both directions.
- *"Does broadening the wraps mask real bugs?"* — the wraps
  only change the error TYPE surfaced to the documented
  contract (`CheckpointCommitError` / `AtomicWriteError`);
  the commit still aborts, the previous generation still
  loads authoritative, and non-`OSError` exceptions are
  untouched.
- *"Is `dir_fsynced` a durability guarantee?"* — no: it is
  observability of the pointer write's directory fsync, per
  atomic_write's explicit-degradation contract. It makes the
  previously invisible degradation verifiable; it does not
  change the best-effort semantics.
- *"Is this the save path (GATE)?"* — no everyday-save, Q1
  locking, or pair-atomicity semantics change; see the GATE
  classification above and Q-29R.2.

## Questions for the Director

- Q-29R.1: Certification review of this bounded 72-29 repair
  is requested; the merge proceeds under Ace's FIX-FIRST
  authority and is labeled accordingly.
- Q-29R.2: Does the Director concur with the FIX (not GATE)
  classification for checkpoint-generation sealing repairs
  that do not touch the everyday-save pair path or Q1
  locking? If not, this circuit's evidence converts to the
  GATE packet unchanged.
