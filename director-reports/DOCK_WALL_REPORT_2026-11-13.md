# Q-U.2 DOCK-LANDING WALL ADMISSIBILITY — repair report

**Status: BUILT — awaiting Keeper review + Director disposition BEFORE merge (per Director mail 1a1d44118259b159). NO MWL credit claimed.**

## 0. Provenance and authorization

- Defect record: `director-reports/SANDBOX_DOCK_CONFIRM_DEFECT_2026-11-13.md`
  (PR #410, merged at `d220196`), Finding 1 (U2): the inference dock's
  DIRECT verbs — `synthesize` / `relate` / `relate_field` — landed
  PENDING proposals whose parents span a sandbox wall.
- Repair scope CONFIRMED by Director mail `1a1d44118259b159`
  (2026-11-13), Q-U.2: enforce canonical parent-wall admissibility on
  dock landing for the direct verbs, BEFORE pending proposal
  persistence, with an explicit refusal receipt; never rely on AI
  judgment for wall enforcement; snapshot wall fields are a separate
  scoped step and are NOT in this circuit.
- Base: `d2201968e0a1f81039904ae0fad97ae9cea01432` (merged main).
  Branch: `uni/dock-wall-1113`. Build commit: `bf5d3d4`.
- This circuit changes NO manual-confirm semantics (Q-U.4 HOLD
  untouched), does not touch `confirm_lineage.py` or the auto-confirm
  sweep (Q-U.3 / Q-U.5 are separate queued circuits).

## 1. BEFORE — the leaks (U2 evidence, INTEGRATION)

At main `6d5f821`, with the repository's scripted-FakeProvider dock
harness (the `form/dock_proposal_b_test.py` pattern; probe script and
log preserved outside the repo in the goal workspace,
`hidden_files/u_probes/u2_probe.py` / `u2_probe.log`):

- `synthesize([in_a, out_a])` → LANDED `docked_cross_7748`,
  status=pending, parents `['in_a', 'out_a']` (vault1 × unboxed).
- `relate(in_a, out_c)` → LANDED `docked_cross_7748_1`, parents
  `['in_a', 'out_c']`.
- `relate_field(in_a)` → candidates shown to the judge (target
  first): `['in_a', 'in_b', 'out_a', 'out_b']` — the host token
  pre-filter was wall-blind → LANDED `docked_cross_7748_2`, parents
  `['in_a', 'in_b', 'out_a', 'out_b']`.
- Mechanism: `sandbox` occurred 0 times in
  `form/dell_matrix/inference_dock.py`; the field snapshot
  (`_unit_entry`) carried no wall fields; landing validation checked
  only that the judge's parents are a subset of the shown targets.
- CONTROL that already held: the growth path — RingedGrowth hands
  only wall-mate pairs to `session.synthesize` (GS-4 filter), and
  the U2 probe's growth leg showed `docked_pairs` exactly
  `(in_a, in_b)` / `(out_a, out_b)` with
  `pairs_excluded_cross_sandbox=6`.

## 2. Mechanism (AFTER)

All changes are in `form/dell_matrix/inference_dock.py` (+110 lines,
pure insertions; no existing line modified).

Canonical semantics are REUSED, not reinvented: wall keys and the
malformed verdict come from the GS-4 authority itself —
`form/dell_matrix/ringed_growth.py`'s `_wall_key(plane, uid)` and
`_malformed_boxed(plane, uid)` (the latter built on the
`form/mandell/unit_containment.py` F1 malformed definition) —
imported at call time. `_wall_key` returns `None` for an unboxed
unit, else its `sandbox_id`; `_malformed_boxed` is True when a unit
claims sandbox isolation its records cannot verify (id
missing/empty, names no Sandbox record, or membership
inconsistency). Import direction checked: `ringed_growth` never
imports `inference_dock` (the coordinator imports the dock lazily),
so no cycle is introduced (verified: clean import + all dock suites
green).

1. **The landing check** — `_parent_wall_refusal(program, verb,
   parents)` (module level, inference_dock.py:633). It resolves the
   program's Plane exactly as the coordinator's `_plane_units` does
   (`program.cube.session.plane`, via `_session_plane`), computes
   each parent's canonical wall key FROM THE PLANE RECORDS — never
   from snapshot data (snapshots carry no wall fields) and never
   from judge output — and:
   - any parent malformed → refusal `malformed_wall_claim`
     (fail-closed; a malformed claim is NEVER collapsed to unboxed —
     the GS-4 `None == None` fail-open);
   - more than one distinct wall key → refusal
     `cross_wall_parents`;
   - otherwise → admissible (None). A parent absent from the Plane
     (a PENDING Nursery idea) carries the unboxed key, exactly as
     `_wall_key` rules it. A program with no Plane has no wall
     records; every parent is unboxed by definition.
2. **The enforcement point** — ONE point in the single shared
   landing funnel `DockedSession._verb`, invoked for the three
   in-scope verbs (`_WALL_VERBS = ("relate", "synthesize",
   "relate_field")`) immediately before `nursery.add`, after the
   existing schema / parents-subset / protected-output /
   stale-target checks (all existing refusal precedences preserved).
   The checked set is the ACTUAL lineage about to persist:
   `fields["parents"] or list(targets)`. A refusal returns before
   `nursery.add` — nothing is persisted. All three direct verbs
   land exclusively through `_verb` (verified by call-graph read:
   `relate` / `synthesize` / `relate_field` → `_verb` → one
   `nursery.add`); `propose()` lands parentless proposals and is
   outside the contract; `flag` / `comprehend` ride the same funnel
   but land single-parent lineage and are gated OUT of this circuit
   by `_WALL_VERBS`, per the authorized scope.
3. **The relate_field pre-filter** — in `relate_field`, after the
   token-overlap scoring, the candidate list is additionally
   constrained to the target's canonical wall BEFORE anything is
   shown to the judge: candidates across the wall (or malformed)
   are removed from `scored`, so the judge cannot be handed a
   cross-wall lineage to author. Exact behavior:
   - target malformed → the `malformed_wall_claim` refusal
     (fail-closed; the target is caller-named);
   - token-overlapping candidates exist but ALL are walled off →
     `no_wall_mates` refusal, provider never called;
   - no token-overlapping candidates at all → the pre-existing
     `no_candidates` receipt (unchanged);
   - candidates that share the target's wall pass through in the
     original token-rank order (the wall filter only removes).
   The `_verb` landing check still applies to whatever the judge
   returns (e.g. a target retrieved after the filter ran), so the
   pre-filter is defense in depth, not the enforcement of record.

## 3. Refusal receipt shape

The dock's existing refusal style (`{"ok": False, "reason",
"detail"}`, bounded public text) plus naming fields:

- Cross-wall: `{"ok": False, "reason": "cross_wall_parents",
  "detail": "Parents span more than one sandbox wall (unboxed,
  vault1); refused before proposal creation — a docked proposal's
  parents must share one wall (Q-U.2).", "verb": <verb>, "task":
  <verb>, "parents": [...], "walls": ["unboxed", "vault1"]}`.
- Malformed: `{"ok": False, "reason": "malformed_wall_claim",
  "detail": "Parent <pid> claims sandbox isolation that the
  Plane's box records cannot verify; refused fail-closed before
  proposal creation (Q-U.2).", "verb": <verb>, "task": <verb>,
  "parents": [...], "malformed": [<pid>]}`.
- relate_field pre-filter: `{"ok": False, "reason":
  "no_wall_mates", "detail": "Every field entry sharing content
  tokens with the target sits across a sandbox wall or carries an
  unverifiable box claim; the provider was not called.", "verb":
  "relate_field", "task": "relate_field"}`.

## 4. AFTER behavior per verb (suite form/dock_wall_test.py)

- **synthesize cross-wall** → `cross_wall_parents` refusal; nursery
  pending count unchanged; nothing persists. Same-wall and
  both-unboxed synthesize land PENDING exactly as before.
- **relate cross-wall** → `cross_wall_parents` refusal, likewise;
  same-wall relate lands.
- **relate_field** → the judge is shown only same-wall candidates:
  on the GS-4 field, `relate_field(in_a)` shows exactly
  `[in_a, in_b]` (BEFORE: `[in_a, in_b, out_a, out_b]`) and lands
  parents `{in_a, in_b}`; `relate_field(out_b)` shows
  `[out_b, out_a]` (BEFORE it also showed both boxed units) and
  lands `{out_a, out_b}`.
- **Malformed parent** (sandboxed=True with `sandbox_id=None`, and
  the ghost variant naming no Sandbox record — both constructed by
  direct field assignment, the same states a verbatim save restore
  produces; GS-4 suite run F pattern) → `malformed_wall_claim`
  refusal on synthesize and relate; nothing persists.
- **Growth-path control** → `grow_ideas(1, session=...)` still
  authors both docked pairs `(in_a, in_b)` / `(out_a, out_b)`,
  landed PENDING (`docked_new=2`), `growth_mode="docked"`, and the
  GS-4 receipts are intact (`pairs_excluded_cross_sandbox=6`). The
  new landing check passes these pairs because RingedGrowth already
  filters them to wall-mates.

## 5. Failing-first evidence

New suite `form/dock_wall_test.py` (15 checks; INTEGRATION — real
Program/Nursery via production loaders, scripted MaximalJudge whose
parents are exactly the targets shown, the maximal acceptance a
real model's output could receive), registered in
`form/regress.py` LIST directly after `form.gs4_sandbox_test:smoke`.

Red run against BEFORE code (base `d220196`, suite + registration
only): **6/15 — FAILING: A1, A2, A3, A4, A5, A6, F1, F2, F3** (every
refusal check red; the cross-wall proposals landed with the exact
U2 pids `docked_cross_7748` / `_1` / `_2`); all positive controls
green (A0 wall sanity, A7/A8/A9 lawful landings, G1/G2 growth
control). Red log pointer:
`hidden_files/dockwall/red_run_before.log` (goal workspace).
After the build: **15/15**.

## 6. Mutants (committed work first; inverse-edit reverts only)

- **M-A — landing check removed** (the `_verb` call neutralized):
  suite 8/15, FAILING A1, A2, A3, A5, F1, F2, F3 — KILLED. (A4/A6
  stayed green under M-A because the relate_field pre-filter
  independently constrains what the judge can author; the landing
  checks proper all went red.)
- **M-B — malformed treated as unboxed** (the `_malformed_boxed`
  branch in `_parent_wall_refusal` disabled): suite 12/15, FAILING
  F1, F2, F3 exactly — KILLED. Notable: under M-B the id-absent
  cases landed (the precise GS-4 fail-open), and the ghost case
  degraded to a `cross_wall_parents` refusal instead of the
  fail-closed malformed verdict — the suite pins the distinction.
- Both reverted by inverse edit; post-restore `git diff` empty and
  suite back to 15/15. Mutant logs:
  `hidden_files/dockwall/mutant_ma.log`, `mutant_mb.log`.

## 7. Focused suite results (at head bf5d3d4, regress-style smoke)

| Suite | Result |
|---|---|
| form.dock_wall_test (new) | 15/15 |
| form.dock_proposal_b_test | 17/17 |
| form.mandell.p4_sd1_test | 19/19 |
| form.mandell.p5_sd2_test | 24/24 |
| form.mandell.track_c_dock_verbs_test | 29/29 |
| form.mandell.p6_sd3_test | 10/10 |
| form.mandell.p7_sd4_test | 17/17 |
| form.snapshot_retrieval_test | 16/16 |
| form.snapshot_revalidation_test | 15/15 |
| form.gs4_sandbox_test | 19/19 |
| form.nursery_confirm_race_test | 57/57 |
| form.mandell.r62_docking_test | 177/177 |
| form.mandell.dock_transport_test | 29/29 |
| form.lm3_composer_test (sanity) | 43/43 (returns True) |

The ×3 regression campaign (fwd/twice/rev) is run by the main
session after this lane returns, per the circuit protocol.

## 8. Files changed

- `form/dell_matrix/inference_dock.py` (+110, pure insertions):
  `_WALL_VERBS`, `_session_plane`, `_parent_wall_refusal`; the
  `_verb` landing call; the `relate_field` pre-filter constraint.
- `form/dock_wall_test.py` (new, 15 checks).
- `form/regress.py` (+3 lines): `form.dock_wall_test:smoke`
  registered after the GS-4 entry.
- `director-reports/DOCK_WALL_REPORT_2026-11-13.md` (this report),
  `director-reports/INDEX.md` (+1 row),
  `director-reports/DIRECTOR_REVIEW_QUEUE.md` (+1 row).

## 9. Questions for the Director

- **Q-DW.1** — Disposition on this circuit at the PR head (build
  `bf5d3d4`): does the landing-check placement (single funnel point,
  checked set = the lineage about to persist, after the existing
  refusal precedences) match the Q-U.2 confirmation?
- **Q-DW.2** — The relate_field pre-filter constraint (wall filter
  at candidate selection + `no_wall_mates` receipt) is defense in
  depth beyond the landing refusal the ruling named. Confirm it is
  in-scope, or direct its removal.
- **Q-DW.3** — Parents that are PENDING Nursery ideas carry the
  unboxed wall key (inherited from `_wall_key`: absent from the
  Plane = unboxed), so a boxed unit + a pending idea is refused as
  cross-wall, and two pending ideas (or a pending idea + an
  unboxed unit) are admissible. Confirm this reading of the
  canonical semantics for dock landing.

## 10. Residuals (NOT addressed here, by scope)

- Snapshot wall fields (truthful read-only wall metadata for the
  docked AI) — separate scoped step per the Q-U.2 ruling; not
  implemented.
- Confirm placement inheritance (Q-U.3) and the auto-confirm
  sweep's cross-wall behavior (Q-U.5) — separate queued circuits;
  `confirm_lineage.py` and the sweep untouched.
- Q-U.4 (mixed-parentage MANUAL confirm semantics) remains on
  Director HOLD pending Ace's sovereignty ruling; this circuit
  changes no manual-confirm behavior.
- A docked proposal whose parents are a boxed unit and a PENDING
  idea is now refused at landing (the idea carries the unboxed
  key). If the authorities later give Nursery ideas a wall of
  their own, this reading changes with the canonical helpers —
  the dock follows `_wall_key`, it does not fork it.
- NO MWL credit claimed for this circuit.

---

# SECOND PASS — transitive pending-lineage repair (2026-11-13)

Added under Director mail **1a1d4790779b6edc** (2026-11-13 04:34
CST), the same bounded circuit. The sections above stand as the
first-pass record at head 822636d except where this section
states a supersession: **Q-DW.3 as answered in mail 1a1d45ae
is SUPERSEDED for pending parents** (the interim reading —
pending = unboxed by absence — is withdrawn), and the
terminal-green campaign at 822636d (fwd/twice/rev 280/280,
receipt comment 6850422382) is **superseded for
certification**; the main session campaigns the new head.

## SP.1 The escalation (probe P6(ii), adversarial battery)

The first pass resolved each parent ONLY through the Plane:
`_wall_key` returns None (unboxed) for an id absent from the
Plane, and a PENDING proposal is absent from the Plane by
definition. The probe composed two legal hops — hop 1 lands an
in-wall pending (parents in_a + in_b, wall vault1); hop 2
relates that pending pid with out_a — and the second hop LANDED
with persisted parents [pending_pid, out_a]: transitive lineage
spanned the wall while every immediate check passed.
Symmetrically, pending + in_b was falsely REFUSED as
cross-wall. Both directions are the same defect: an id's wall
was inferred from its ABSENCE, violating the positive-evidence
law.

## SP.2 Resolution design and its authority

`_wall_verdict(program, plane, pid, stack, anchor)` in
`form/dell_matrix/inference_dock.py` is now the single resolver
for both the landing gate and the relate_field pre-filter:

- **Plane unit** → the GS-4 helpers `_malformed_boxed` /
  `_wall_key` (ringed_growth.py, UNCHANGED). A malformed claim
  refuses `malformed_wall_claim`, naming the ancestor that
  carries it.
- **PENDING Nursery record** → resolves through its OWN
  recorded parents, recursively (the Nursery is the canonical
  store the session already holds; placement is never inferred
  from provider fields). Mixed resolved keys inside one lineage
  are themselves a cross-wall verdict.
- **No canonical authority** → verdict `unknown`, refusing with
  the NEW receipt reason **`unknown_parent`** (receipt carries
  `"unknown": [culprit]`): a ghost id in neither store, a
  Nursery record that is NOT pending (only pending records are
  lineage authorities — a confirmed idea resolves through the
  Plane unit its confirmation placed; a rejected record was
  never placed), a lineage cycle, a missing link mid-chain, or
  depth beyond the bound. Fail-closed: absence never resolves
  to unboxed.
- **Depth bound:** 32 lineage links (`_WALL_LINEAGE_MAX_DEPTH`).
  Each landing adds at most one link and MAX_PARENTS bounds the
  width; a longer chain is treated as unestablished, not as
  unboxed.
- **Anchor vs ancestor (the one place the contract left a
  choice):** a parentless PENDING proposal is itself a legal
  field entry whose wall is unboxed — the Nursery creates
  parentless entries BY DESIGN (organic growth proposals,
  manual adds, ingest) — so as the ANCHOR of a checked parent
  set it resolves unboxed. As an ANCESTOR of another proposal
  it establishes nothing about that descendant's lineage, and
  the strict rule stands in recursion: parentless resolves
  unknown. Evidence for the anchor side: the shipped suites
  (track_c_dock_verbs 29, snapshot_retrieval,
  snapshot_revalidation) exercise parentless pendings as
  relatable field entries — first the strict-everywhere reading
  broke exactly those three suites and no others; the
  anchor/ancestor refinement restored them with the T-checks
  (which pin the ancestor side) unmodified.
- **Ghost naming at the schema boundary:** the semantic
  validator rejects a provider-named parent outside the field
  (`invalid_output`) BEFORE the gate runs — correct, and
  untouched. `_unknown_parent_refusal` re-checks ONLY that
  failure shape: when the payload's parents are otherwise
  well-formed and at least one resolves `unknown`, the refusal
  is returned as `unknown_parent` instead. The validator is
  never weakened — the refusal is stricter than the generic
  verdict, never an admission — and a legitimate PENDING parent
  still distinguishes itself: it validates inside the field and
  resolves through its lineage at the gate (T5).

`confirm_lineage.py`, the auto-confirm sweep, ringed_growth's
plane-unit semantics, and snapshot wall fields are untouched.
Q-U.4 (manual cross-wall confirm policy) remains on Director
HOLD pending Ace — untouched.

## SP.3 Failing-first evidence (Build T, form/dock_wall_test.py)

New checks T0–T8 (suite total 15 → **24**; the original 15
expectations unmodified). RED run against unmodified 822636d
product code: **17/24** — T0 fixture and T3 pass; FAILING:
**T1** (multi-hop relate AND synthesize both LANDED — the leak
itself), **T2** (same-wall continuation falsely refused),
**T4** (ghost refused only as schema `invalid_output`, no wall
verdict), **T5** (legitimate pending falsely refused),
**T6** (crafted two-record cycle LANDED), **T7** (orphan
pending with a ghost mid-chain parent LANDED), **T8**
(malformed-ancestor child LANDED). After the repair: **24/24**.
Logs: `hidden_files/dockwall_repair/red_run_second_pass.log`,
`green_run_second_pass.log`, `restore_verify.log`.

## SP.4 Mutants (real work committed first at 3a3666b;
inverse-edit reverts only; post-restore diff empty, 24/24)

- **M-C — pending parent treated as unboxed** (the old absence
  rule, restored inside `_wall_verdict`): suite 18/24, FAILING
  T1 (the leak lands again), T2, T5, T6, T7, T8 — KILLED.
  (One earlier M-C probe placement landed in a code path the
  suite never reaches and passed 24/24; it was reverted and the
  mutant re-applied at the resolver's real decision point —
  recorded here because a mutant that changes nothing proves
  nothing.)
- **M-D — ghost treated as unboxed** (an id in neither store
  resolves unboxed): suite 22/24, FAILING T4 (ghost degrades to
  the schema verdict) and T7 (orphan lands) — KILLED.

Logs: `hidden_files/dockwall_repair/mutant_mc.log`,
`mutant_md.log`.

## SP.5 Focused suites (at 3a3666b, regress-style smoke)

dock_wall **24/24**; dock_proposal_b PASS; track_c_dock_verbs
**29/29**; snapshot_retrieval PASS; snapshot_revalidation PASS;
gs4_sandbox **19/19**; nursery_confirm_race PASS; r62_docking
PASS; dock_transport PASS; p4_sd1 PASS; p5_sd2 PASS; p6_sd3
PASS; p7_sd4 PASS; lm3_composer PASS — 14/14 suites green. The
×3 campaign is the main session's, at the new head (this lane
does not campaign, per the §37 serial law).

## SP.6 Questions for the Director (second pass)

- **Q-DW.4** — Confirm the anchor/ancestor rule: a parentless
  PENDING proposal is unboxed as an anchor but establishes
  nothing as an ancestor. The anchor side is load-bearing for
  shipped behavior (parentless field entries are relatable);
  the ancestor side is the conservative reading of your
  contract item 2.
- **Q-DW.5** — Confirm the depth bound of 32 lineage links and
  the `unknown_parent` receipt name/shape as the canonical
  ghost verdict, including its use at the schema boundary
  (`_unknown_parent_refusal` — stricter naming only; the
  validator itself is untouched).

## SP.7 Residuals (second pass)

None beyond the first-pass residuals: Q-U.4 HOLD (Ace's open
question), Q-U.3 confirm-placement and Q-U.5 sweep circuits
queued separately, snapshot wall fields a separate scoped
step. NO MWL credit claimed (register row 185 stays OPEN).
