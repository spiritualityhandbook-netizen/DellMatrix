# CONSOLIDATED DIRECTOR PACKET — one-pass review of the outstanding queue

**Issued by Uni at Ace's instruction (2026-11-02): the whole
outstanding queue in one sitting, not segment by segment.**
Anchor: main `d29049a`. Responds to DIR-2026-11-02-R1.
**Nothing in this packet is certified by submission. Merged
!= certified. Previously certified bounded scopes are NOT
re-opened; they are listed only where an exception or a
follow-on decision touches them.**

## How to rule on this packet

Each item names one bounded decision: certify the bounded
claim / certify with noted exceptions / decline / defer with
a named missing input. Items are independent — a decline on
one does not disturb another. Raw evidence for every item is
in this repository (per-item bundle paths below; index at
`director-reports/EVIDENCE_INDEX.md`), each bundle carrying
an EVIDENCE.md manifest with SHA-256 digests, tested
revision, commands, environment limits, and known gaps.

## R1 compliance map

- **Priority 1 (DIR-F16):** implemented, evidence published —
  Item 1.
- **Priority 2 (reachable evidence):** published via PR #222
  (merge d29049a) — bundles for Step 13, the DAF-09 family,
  DIR-F12–F15, steps 10–11; EVIDENCE_INDEX.md is the map.
- **Priority 3 (T2 growth identity):** implemented, evidence
  published — Item 2.

## Item 1 — DIR-F16: pidfd send-boundary error classification

- **Decision requested:** certify (or decline) the bounded
  claim in DIRECTOR_REPORT_DIRF16.md: send errors split by
  errno (ESRCH = refused; EPERM/ENOSYS/other = unavailable),
  surfaced through the kill report / cleanup_unavailable
  verdict. Fix PR #217, merge 6dab0d6 (tree cc1316c ==
  candidate). Suite 31/31 (23 preserved + check-10 series);
  regress 221/221 x3; exact-head CI SUCCESS; fresh-clone
  221/221 + probe PASS.
- **Report:** director-reports/DIRECTOR_REPORT_DIRF16.md —
  READ WITH ITS TWO CORRECTIONS (also in the INDEX row and
  evidence/dirf16/ERRATA.md): (1) an originally disclosed
  "anomaly" was retracted (truncated interim readout; the run
  was clean); (2) the merge identifiers originally printed
  were corrected to 6dab0d6 / cc1316c.
- **Evidence:** director-reports/evidence/dirf16/ (probe
  source + pre/post outputs + mutant output, SHA-256 table
  in the report).
- **Carried questions:** C-Q1, C-Q2 (below).

## Item 2 — T2 label identity: ambiguous plant keys

- **Decision requested:** certify (or decline) the bounded
  claim in DIRECTOR_REPORT_T2_LABEL_IDENTITY.md: growth-lens
  keys that cannot identify one node (distinct full labels
  collapsing to label[:80], or plants disagreeing on a key's
  stage) report stage=None / stage_source="ambiguous". Fix
  PR #220, merge 7486963. Suite 15/15 (9 preserved + 6);
  mutant 12/15 exact; regress 221/221 x3; fresh-clone
  221/221 + probe PASS.
- **Report:** director-reports/DIRECTOR_REPORT_T2_LABEL_IDENTITY.md
- **Evidence:** director-reports/evidence/t2label/
- **Carried questions:** C-Q3, C-Q4 (below).

## Items 3–6 — DIR-F12 / F13 / F14 / F15 re-presentation

R1 disposition for each: source supports the correction;
independent execution outstanding (F15: exception not yet
formally lifted). Each is re-presented WITHOUT reopening its
already-reviewed source claims; the new element is the
reachable raw evidence for independent execution.

| Item | Report | Evidence bundle | Decision requested |
|------|--------|-----------------|--------------------|
| 3. DIR-F12 Exchange journal receipt | DIRECTOR_REPORT_DIRF12.md | evidence/dirf12/ | bounded verification on the published logs |
| 4. DIR-F13 Loop count grammar | DIRECTOR_REPORT_DIRF13.md | evidence/dirf13/ | bounded verification on the published logs |
| 5. DIR-F14 Catch consumed split | DIRECTOR_REPORT_DIRF14.md | evidence/dirf14/ | bounded verification on the published logs |
| 6. DIR-F15 Diff absent-vs-None | DIRECTOR_REPORT_DIRF15.md (= step 9 report lineage) | evidence/dirf15/ | lift or retain the F15 exception |

## Items 7–8 — Steps 10 and 11 re-presentation

| Item | Report | Evidence bundle | R1 status | Decision requested |
|------|--------|-----------------|-----------|--------------------|
| 7. Step 10 Resolve/Ungroup/Compose | DIRECTOR_REPORT_STEP10_CONSISTENCY.md | evidence/step10/ | source aligns; independent tests outstanding | bounded verification |
| 8. Step 11 public contracts | DIRECTOR_REPORT_STEP11_CONTRACTS.md | evidence/step11/ | wording accepted in principle | confirm acceptance as ruled, or bound it |

## Item 9 — Step 13: pairwise re-derivation reproduction

- **Decision requested:** rule on the step-13 re-derivation
  (ledger v2) as independently reproduced, reproduced with
  exceptions, or not reproduced.
- **Report:** DIRECTOR_REPORT_STEP13_REDERIVATION.md
- **Evidence:** director-reports/evidence/step13/ — harness
  sources, all 100 sweep blocks + identity rows, the
  rederived data, ledger v1 AND v2, diff_vs_v1.json, and
  EVIDENCE.md verification notes. Verified at publication
  (and reproducible from the bundle): v1's canonical hash
  reproduces exactly (43fe6967…); v2 carries exactly 9,900
  rows + 100 identity rows with class counts == the reported
  FINAL totals; the recomputed v1→v2 diff is exactly 369
  changes, matching diff_vs_v1.json.
- **Stated limit (not hidden):** v2's embedded canonical
  ledger_sha256 (de5354f0254c…afd, string-identical to the
  report's quoted value) does NOT reproduce under v1's
  canonical method, and the v2 freeze builder was not
  preserved as a file. The bundle's verification rests on
  the internal-consistency and diff recomputations above.
- R1 already permits ledger v2 as provisional current-freeze
  evidence; this item asks whether reproduction upgrades it.

## Item 10 — DAF-09: session-escape and the Q2 post-check

- **Decision requested:** rule on the DAF-09 session-escape
  scope on the full published record, or specify the missing
  input that would settle it. The cancellation certificate
  is NOT in question and is not re-presented.
- **Reports:** DIRECTOR_REPORT_DAF09_INSTRUMENTED_INVESTIGATION.md,
  DIRECTOR_REPORT_DAF09_ESRCH.md, DIRECTOR_REPORT_DAF09_POSTCHECK.md
  (plus the earlier DAF-09 family in director-reports/).
- **Evidence:** director-reports/evidence/daf09/ — driver,
  probes, instrumented/idle/saturated run logs, ESRCH and
  pidfd regress legs, grounds, and all packets.
- **Standing facts:** local record is complete and green
  (instrumented saturated 23/23 x3 post-ESRCH-fix); the live
  ESRCH race did not re-fire under instrumentation; the
  cross-environment discrepancy remains UNRESOLVED (§31.3)
  and this packet does not ask the Director to resolve it
  from local greens.
- **Carried question:** C-Q5 (below).

## Item 11 — T6: exception disposition

R1 accepted the T6 RELABEL in principle; the external
compatibility exception (focus_areas key rename) remains.
**Decision requested:** lift the exception, or retain it with
its conditions stated. Report: DIRECTOR_REPORT_WS_THEATER_T6.md.

## Item 12 — Step 14: per-scope admission decisions

The step-14 admission packet (DIRECTOR_REPORT_STEP14_ADMISSION.md)
requests explicit per-scope decisions; it is re-presented
unchanged, now with every scope's evidence reachable above:
- **A1** Exchange — already certified (Ruling #7); restated
  for the record, no new decision needed unless the Director
  revisits it.
- **A2** reconciled closure scopes — decision requested.
- **A3** remaining typed Dells + full-registry re-rulings —
  decision requested per scope or as a class.
- **Whole-program certification** — the Director's call
  alone; this packet does not argue it follows from any sum
  of bounded certificates.

## Consolidated questions (answer once, here)

- **C-Q1** (from DIR-F16 Q1): does the send-boundary
  classification as evidenced satisfy DIR-F16, or is a
  kernel-level EPERM reproduction (e.g. cross-uid pidfd)
  required for the bounded certificate?
- **C-Q2** (from DIR-F16 Q2): is the in-repo evidence-bundle
  shape (evidence/<scope>/ + manifest + digests), now applied
  across Items 3–10, acceptable as the standing Priority-2
  pattern?
- **C-Q3** (from T2 Q1): should GrowthForce.plant retain the
  full idea (e.g. idea_full alongside the truncated key) so
  future views can match exactly? Not implemented — it
  changes the canonical growth record's shape.
- **C-Q4** (from T2 Q2): is "collision => ambiguous even when
  all candidate plants agree on stage" the intended honesty
  boundary, or should agreeing-stage collisions resolve?
- **C-Q5** (from the DAF-09 post-check Q1): is the
  deterministic injected control (passing every run,
  mutant-killed) sufficient evidence for the ESRCH refused
  landing, given the live race did not re-fire under
  instrumentation?

## Stop conditions honored

No whole-program certificate is claimed or implied. No
unsafe fallback was introduced anywhere in Items 1–2. Green
CI is nowhere presented as proof of the unresolved
process-cleanup claim (Item 10). Historical submissions are
preserved unrewritten; the only post-submission edits on
record are the DIR-F16 corrections, which are labeled as
corrections wherever they appear.
