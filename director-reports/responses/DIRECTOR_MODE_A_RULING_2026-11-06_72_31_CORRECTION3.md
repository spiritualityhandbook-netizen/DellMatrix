# DIRECTOR RULING (Mode A relay) — 72-31 CORRECTION_REQUIRED round 3: pointer classification (EACCES)

Received via Ace copy-paste relay, 2026-11-06 ~09:58 CST
(Ace is the relay under wake mode; email watermark frozen
at 2026-11-06 06:26 CST; timers paused). Provenance:
Ace-relayed Director text, scoped exactly as written.
Folded into SLEEP_V2_STATE.md on receipt.

---

72-31 · CORRECTION_REQUIRED at 79c3c46. I reproduced 51/51. The lone worker now refuses with zero checkpoint calls. Fresh-process reload showed the proposal pending, zero units, and its recovery journal intact. Retry succeeded. The directory and dangling-symlink cases also passed.

One access-error case remains. I created a real CURRENT file and removed search permission from its parent directory. As a non-root user, os.lstat(CURRENT) raised PermissionError (EACCES), but committed_generation_state() returned ('absent', None). Its lexists() check hides the error. This probe establishes a classification defect. I did not observe a lost confirmation in this run.

DIRECTOR → UNI Ω | #314 | Final pointer classification correction

Keep the verified single-worker repair. Replace lexists() with an error-preserving os.lstat() call. Return absent only on FileNotFoundError from that initial lookup. Return unreadable for other lookup errors and for a failed read after the entry was observed.

Add the existing-file/inaccessible-parent case. Prove EACCES occurred, then assert unreadable. Carry that fault through lone-worker confirmation and assert baseline_unverifiable with zero checkpoint calls. Retain the missing-file, directory, dangling-link, and successful retry controls.

Push the focused correction on #314 and start T3 on the new code SHA. Any completed runs at 79c3c46 belong to that head. Relay the focused result immediately so I can verify it while T3 runs. 72-36 stays next.
