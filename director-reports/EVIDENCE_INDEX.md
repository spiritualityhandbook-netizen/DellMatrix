# EVIDENCE INDEX — reachable raw evidence (DIR-2026-11-02-R1 Priority 2)

Published 2026-11-02 in response to the Director's evidence-
accessibility finding: reported results whose raw artifacts
lived only in Uni's workspace are not independently checkable.
The bundles below place the artifacts themselves in this
repository, each with an EVIDENCE.md manifest (scope, tested
revision, commands, environment limits, known gaps, and a
SHA-256 digest for every file). Historical submissions
(reports, packets) are preserved unrewritten; these bundles
are additive.

| Scope | Bundle | Manifest |
|-------|--------|----------|
| Step 13 (9,900-pair re-derivation, ledger v2) | evidence/step13/ | evidence/step13/EVIDENCE.md |
| DAF-09 investigations (timeout tree, identity, pidfd, ESRCH, instrumented, post-check) | evidence/daf09/ | evidence/daf09/EVIDENCE.md |
| DIR-F12 (Exchange journal receipt) | evidence/dirf12/ | evidence/dirf12/EVIDENCE.md |
| DIR-F13 (Loop count grammar) | evidence/dirf13/ | evidence/dirf13/EVIDENCE.md |
| DIR-F14 (Catch consumed split) | evidence/dirf14/ | evidence/dirf14/EVIDENCE.md |
| DIR-F15 (Diff absent-vs-None) | evidence/dirf15/ | evidence/dirf15/EVIDENCE.md |
| Step 10 (Resolve/Ungroup/Compose) | evidence/step10/ | evidence/step10/EVIDENCE.md |
| Step 11 (public contracts) | evidence/step11/ | evidence/step11/EVIDENCE.md |
| DIR-F16 (send-boundary classes) | evidence/dirf16/ | in DIRECTOR_REPORT_DIRF16.md |
| T2 label identity | evidence/t2label/ | in DIRECTOR_REPORT_T2_LABEL_IDENTITY.md |
| DIR-CERT-2026-11-02 certification execution (PR #233 CI-only mechanism, unmerged; frozen revision e0769adf, run 41555532846, 12/12 items exit 0) | evidence/certification_ci/ | evidence/certification_ci/EVIDENCE.md |
| Certification runner | evidence/certification_runner/ | evidence/certification_runner/EVIDENCE.md |
| Core I arg gate | evidence/core-i-arg-gate/ | evidence/core-i-arg-gate/MANIFEST.sha256 |
| Core I contract review | evidence/core-i-contract-review/ | evidence/core-i-contract-review/MANIFEST.sha256 |
| D1 unsupported-arg gate | evidence/d1-unsupported-arg-gate/ | evidence/d1-unsupported-arg-gate/MANIFEST.md |
| D1 unsupported-arg honesty (investigation probes; bundle carries no EVIDENCE/MANIFEST file) | evidence/d1-unsupported-arg-honesty/ | probe logs in the bundle (probe_q1.log et al.) |
| D1 typed 52/53 | evidence/d1_typed_52_53/ | evidence/d1_typed_52_53/EVIDENCE.md |
| DCC-XVII | evidence/dccxvii/ | evidence/dccxvii/EVIDENCE.md |
| DIR-T2-R2 | evidence/dirt2r2/ | evidence/dirt2r2/EVIDENCE.md |
| Studio browser acceptance | evidence/studio-browser-acceptance/ | evidence/studio-browser-acceptance/MANIFEST.sha256 |
| Studio security | evidence/studio-security/ | evidence/studio-security/MANIFEST.md |

Per-circuit bundles from DIR-F16 onward ship with their
reports in the same pattern.
