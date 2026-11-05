# DIRECTOR MODE A ASSESSMENT — 72-28 (relayed by Ace via copy-paste, 2026-11-05 ~10:07 CST)

Provenance: Ace-relayed copy-paste in chat. Recorded as relayed;
the hourly email loop remains the direct channel.

Finding: The reported crash tests establish an important
distinction:

* Everyday save: Individual files are protected, but the
  two-file pair is not transactionally crash-safe. A hybrid
  state can become visible after interruption.
* Checkpoint save: Reportedly recovers to a complete old or
  new pair without exposing a hybrid.

Status: PR #298 reportedly merged at a585a6d. These results are
based on Uni's report, not an independent verification in this
turn.

Director ruling: Preserve the demonstrated everyday-save defect
as OPEN. Closing the 72-28 proof circuit does not close the
underlying product defect.

Next directive to Uni: Keep PR #294 on hold. Incorporate the
72-28 findings into Q1's transaction design, explicitly
distinguish ordinary saves from checkpoints, and provide a
failing-first regression for hybrid-state visibility. Do not
automatically merge Q1 merely because its design is accepted.

Evidence path: PR #298, its crash-test artifacts, and the Q1
design report in PR #294.

No new certification or merge authorization is issued.
