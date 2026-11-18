# DIRECTOR G2 — UNI CHALLENGE DISPOSITIONS AND REVISED BASELINE

**Date:** 2026-11-18. **Original design:** PR #486 head 169d00a03aea3e7ddb32c873b86912730245e898. **Uni challenge:** #486 comment 6978568514. **G2 verified GitHub main at check:** b73b1d29ce25f33575f7f70d86e278ea0bd0d1ba, which may change; all ongoing CI/merge claims must re-query live. **Purpose:** Director owns and corrects design. Uni independently checks these edits. No production code modified by this PR and no scoreboard status altered.

## 1. Fifteen original challenge findings + two unresolved verification groups

| Uni finding | Director G2 decision | Resolution/evidence |
|---|---|---|
| CH-01 source crosswalk | ACCEPT / no mutation | 185 MWL rows, 3 sandbox, 182 active, statuses 39/54/86/3/3, 49 unadopted Grand Plan candidates. Uni independently matched 185/185. Keep alias proposals only, no denominator change. |
| CH-02 dependency DAG | ACCEPT | 28 nodes, no cycle/dangling ref, eight independent starters. No PR implementation authority implied. |
| CH-03 baseline | ACCEPT | Live published 39/182 21.4% at checked source. Historic 35/224 remains history only. |
| CH-04 R24 translation | ACCEPT | Source slice sites and cases verified. Uni may prepare isolated failing-first repair; implementation test still required before merge. |
| CH-05 R23 outcome | ACCEPT WITH CASE FOLLOW-UP | Caps confirmed, but 12-message count bound needs its public-case reproduction in GP-E02. |
| CH-06 Dell catalog | ACCEPT AS CONTRACT DESIGN ONLY | Registry Core 00–50 + Core II 51–99 = 100 addresses, not "99" items. 100 individual proposed contracts do not certify code. |
| CH-07 Q-R.1 license | ACCEPT | Ace's non-commercial mode and Q-R.1 discharge remain in force; version-specific license and distribution check remains for each dataset. |
| CH-08 R26 DuoBeta | ACCEPT | PR #483 already merged; do not reimplement. |
| CH-09 journeys | ACCEPT AS DESIGN ONLY | J-01..15 historical links and J-16..25 new test designs; no current certification count invented. |
| CH-10 Workflow v2 | ACCEPT WITH TIMESTAMP PROVENANCE CORRECTION | Adopted design, open records PR #461. See CH-13 below. |
| CH-11 R17 / #485 | **SUSTAINED, HIGH SAFETY; CODE MERGE HOLD** | Uni's no-bound implementation removes phantom 8 but returns no bound during nested nonterminal expansion. Finite-name cycle guard catches repeated names; that does NOT guarantee a safe maximum depth if many unique definitions are nested, so no claim of literal infinite recursion is needed. Director HOLD published at #485 comment 6978656808. Require typed bound_unspecified/NEEDS_BOUND before expansion, preserve nonrecursive flat/raw-terminal, exact user cap/max=64, invalid refusal, public paths, test pin reconciliation. |
| CH-12 old #420/#433 facts | SUSTAINED; CORRECTED | #420 MERGED at c7d7fcaf11f8d7da880af50e74a1e488c342da87; Keeper confirmed the refreshed #420 head before merge (review 5956192629). #433 MERGED at c87d808b109b5361a604a0040375c52d6f0e4e6d. Original author base a8786f9c retained as history, now supplemented by exact newer proof. Records merge is not automatic Tree product admission or FI-010 Phase T implementation. |
| CH-13 §32 timestamp | **PARTIALLY SUSTAINED AS AMBIGUOUS PROVENANCE, NOT AS THE PROPOSED EFFECTIVE TIME** | #461 comment 6974842014 was posted at GitHub created_at 09:45:02Z yet its BODY declares effective 09:50Z. #461 comment 6974870306 was posted 09:46:17Z and BODY declares effective 09:46Z. The Director's binding verification comment 6975138216 explicitly selected the **later 09:50Z as a single conservative audit boundary** because receipts disagree. Therefore use 09:45:02Z only as the first COMMENT POSTING TIME; the Director-specified operational/audit boundary remains 09:50Z. This maintains source/event separation and does not silently override a Director ruling. |
| CH-14 FI-010..019 coverage | SUSTAINED; CORRECTED WITH EXPLICIT SOURCE GAP | New file 09_FEATURE_INTAKE_FI010_FI019.md names every one of ten items, minimum behavior/guards, dependencies and disposition. FI-010/011/012/018/019 rely on repo records; FI-013..016 substantively recovered from prior goal-workspace decisions but their exact source documents must be attached and checked; **FI-017 Gemini Docked Operator role was recovered by Uni** (source report 6978844101): Nursery operator, knowledge conductor, resident developer. File 09 now specifies all three, with actual permission gates and failing-first tests. Original goal-workspace bytes are still uninspected and must be verified by Uni/Keeper before any plan adoption; BUILD not authorized. |
| CH-15 R25 test pin | EVIDENCE OWED | GP-E04 design specifies no extra operand drop; locate and reproduce precise existing pinned tests before re-pinning under correction authority. No false claim of already-verified new behavior. |
| CH-16 R5 history sites | EVIDENCE OWED | GP-E05 remains designed; Uni must reproduce current note/save/load cuts and repair all relevant owners if still present. |
| CH-17 house challenge | EVIDENCE OWED, NOT PRETENDED COMPLETE | All 11 H-houses still require caller/writer/source counterexamples on current main. CH-11 is one concrete H1 failure class; one case does not certify all 11. |

**G2 FOLLOW-UP GP-E03A NEW-HEAD FINDING (CODE HOLD EXTENDED):** PR #485 advanced from held head 4a2939f8 to 17c03df4 with refusal for omitted nested nonterminal bound, explicit max/invalid handling, and new tests. Director direct source inspection identified `_compose_seed` calling recursively implemented `_compose_cycle_ahead` **before** `_compose_bound`: an arbitrarily deep acyclic unique-name chain can exhaust the recursion stack before the bound acts. This is a PRE-SCAN budget bypass, not proof of an infinite execution cycle. New finding / continued HOLD: #485 comment **6978856860**. Uni must bound both preflight and executor and demonstrate no uncaught exception or partial mutation at 65/66/1100-depth and broad branching with stated cap 3, max=64, no limit and short cycles; Keeper then reviews a NEW head. No merge or credit for 17c03df4 on this evidence.

**G2 cross-cutting Director-identified issue FI-012:** previously broad "hard limits refuse or page" wording was insufficiently distinguished from Ace's final any-size elastic intake doctrine. 00 and 02 now specify demand-grown/chunked resumable intake as the target, keep existing honest guards explicitly temporary, and forbid silent cuts or infinite-device claims. **FI-011:** advanced human-set strict approval gates are future allowed *only* after independent authority; AI/workflows cannot create their own approval rules. 00, 03, 09 now preserve that distinction.

## 2. Role/action allocation

**Director (done this G2):** Designed and published architecture, 28 implementation circuits, individual 100-Dell minimum contracts, 25 journeys, Muse Space, decision register, all 19 FI entries (with FI-017 three-depth Gemini design based on Uni report and original-file provenance check), edited G2 status corrections, R17 merge HOLD and source-time provenance. Not a CODE or product completion claim.

**Uni (next G2 check; not redrafting):** verify every changed file, original source identity FI-013..017 and FI-017 source-reported Gemini operator's three separate depth contracts, 185/49 mapping vs latest main, §32 time interpretation above, existing #485 safe no-bound patch tests, and whether the high-risk first-three repairs remain current. For FI-017 bring original goal-workspace bytes/ID and compare against Uni's reported 6978844101 and Director's file 09 three-depth contract; return exact mismatch, or a signed source-equivalence receipt. For CH-15..17 return exact code counterexamples and missing evidence. Report PASS/CORRECTION_REQUIRED, avoid renaming missing evidence as verified.

**Keeper:** independent exact-new-head records and evidence review after Uni's delta. Prior stamp of original #486 head (if any) cannot transfer automatically to a new head.

**Ace:** remains sole arbiter of substantive Dell meaning/sandbox promotion/uncapped automation options; routine Director corrections are within delegated planning authority. No new sovereign question need be forced on Ace merely to progress the independently safe first code circuits.

## 3. Next isolated code packages

1. GP-E01 R24 — translator operand preservation; failing-first 100→80, 300→240, 80→60, all sibling source slices and caller compatibility. Exact accepted source rather than blindly huge strings.
2. GP-E02 R23 — outcome evidence full fidelity and find/search transparent coverage; revalidate 12-message cap and direct consumers first.
3. GP-E03A R17 — fix existing #485 at a **new exact head**; omitted bound on nested nonterminal expansion refuses before execution; preserve raw/flat behavior; B18 old pinned fixture either proves genuinely nonrecursive or is re-pinned with explicit authorization. Do not merge #485 original unsafe head. Its green tests are not proof the new contract passes.
4. GP-E03B R19 and GP-E04 R25 remain independent follow-ups; no premature aggregation.

Each code package follows normal failing-first, neighboring callers, exact-head CI, Keeper, Director, Uni §32 GitHub-first freshness with outage fallback, current-main zero-loss and post-merge proof. Full-system work continues independently of any one blocked PR.

## 4. Adoption versus design completeness

The **authoring pass** is complete with an explicit unknown register. This does **not** mean zero remaining source gaps, an adopted Grand Plan, or implemented DellMatrix. PR #486 remains DRAFT; prior #421 remains CORRECTION_REQUIRED; code/scoreboard/authority gates remain. The required independent next step is Uni review of this G2 head, then Keeper review, then Director final scoped adoption ruling. Any missing FI-017 original file must be verified against the complete now-authored three-depth contract or explicitly reserved from adopted implementation scope, never silently imported.
