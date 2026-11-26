# PART IV — CODE STAGE, SECTION 2: PERSONAMATRIX (ROW #155, C8.MultiPsalm)

Date: 2026-11-21 · Lane: PR #505 (`uni/part-4-far-stratum`) · Actor: Uni

## Authority

- Ace ruling 2026-11-20, item 11: "Row #155 PERSONAMATRIX:
  incorporate them all, analyze abilities, place each properly as
  the general setting; users can create new personas; personamatrix
  is a user experimentation layer." (Recorded on PR #505 and in
  MEMORY.md; design home ACE_FUTURE_DEVELOPMENT_PLAN §12.)
- Register row #155 verbatim: "Multi-Psalm / BIMO execution design —
  persona execution needs actual instance semantics and Ace-approved
  roles; BIMO metadata alone is not execution (design sit-down owed,
  §12.36e)", ids C8.MultiPsalm, block "Plan §14.3 — C8 Dock & Psalms".
- Fences (Ace, never moving): docking confers NO authority; Nursery
  confirmation stays the owner's sovereign act; a persona is a
  setting, never a gate bypass.

## Grounding (repository reality before the build)

- The canonical roster already lived in `form/dell_matrix/personas.py`
  (11 personas: Manny, Melody, Aetheris, Mathelody, The_Ancient,
  Translator, Della, Mansplainer, Dell, Oracle, BIMO) — each with
  category, BIMO slot, matrix position, directives/abilities/limits,
  prefer_skins. The repo AGENTS.md names personas.py the runtime
  authority; `form/mandell/PERSONAS.md` carries the same roster.
- PersonaMatrix (placement), BIMOBody (dock slots / pilot / fuse),
  Program wiring (`persona_lens`, `set_persona_lens`, bimo persisted
  in the program save), and the BIMO Forge (named configurations)
  all existed. Confirmation is AcceptancePolicy-gated at
  `Program.confirm_proposal` (default DENY; producers authorized
  only through the policy's own paths).
- The gap: NO user persona creation existed anywhere in `form/`
  (grep for create_persona / custom_persona / register_persona =
  empty). Ace's "users can create new personas" was unbuilt.

## What was built

- `form/dell_matrix/personas.py` (+250/−31): a user
  persona layer INSIDE the canonical module — no second authority,
  no parallel system.
  - `CUSTOM_PERSONAS` active layer + `create_custom_persona()` /
    `remove_custom_persona()` / `activate_custom_personas()` /
    `custom_personas()` / `all_personas()` / `validate_custom_persona()`.
  - Creation validation: id derived by the canonical normalization;
    refuses canonical-id and canonical-ALIAS collisions, unknown
    category (must be one of the 7 CATEGORIES), unknown BIMO slot
    (must be one of BIMO_SLOTS or None), missing role/focus, empty
    directives/abilities/limits (every persona declares its fences),
    malformed matrix (h/v ∈ [−1,1], shell ∈ [0,2]; defaults from the
    category axis), and duplicate custom ids (remove-first, no
    silent overwrite).
  - Lookups (`normalize_persona_id`, `get_persona`, `list_personas`,
    `vision_lenses`, `PersonaMatrix.cells`, `render_roster`) now
    resolve canonical first, then the user layer. The canonical
    PERSONAS dict is never mutated by the layer; removal of a
    canonical id is refused ("canonical roster is read-only").
  - `PersonaMatrix.to_dict()` count now counts all cells and adds
    `canonical_count`; the module smoke's cell-count check accounts
    for the user layer.
- `form/open.py` (+51/−0): Program field `user_personas` (persisted
  records); `__post_init__` activates the layer from those records;
  `Program.create_persona()` / `Program.remove_persona()` delegate
  to the personas layer and maintain the persisted record list.
- `form/persist.py` (+4/−0): new save section `custom_personas`
  beside `bimo` (absent = legacy).
- `form/persist_rest.py` (+11/−0): restore re-validates the section
  through `activate_custom_personas` (invalid records skipped and
  reported there, never half-applied).
- `form/personamatrix_test.py` (new, +290/−0): the suite below,
  registered in `form/regress.py` (+6/−0) in the same commit
  (omitted-entry law).

## Evidence

- Failing-first: suite written first — RED = ImportError
  (`create_custom_persona` absent). Mid-build (personas layer only):
  17 checks green, stopping at the unwired Program surface. GREEN
  after full wiring: **personamatrix 28/28**.
  - S1 roster/placement (6): full canonical roster incorporated;
    every persona placed (known category + slot + matrix position);
    abilities analyzed (directives/abilities/limits non-empty);
    matrix cells cover the roster exactly once; DEFAULT_DOCK
    consistent with each persona's own slot; Psalm family present.
  - S2 creation (11): create/resolve/list/place a user persona;
    refusals for canonical collision, alias collision, unknown
    category, empty limits, unknown slot, duplicate custom id;
    canonical removal refused; custom removal works.
  - S3 Program + persistence (4): Program.create_persona; dock +
    lens sync; save → `persist_rest.load` round-trip (persona
    resolvable, dockable, in the matrix, in `user_personas`);
    canonical roster byte-identical afterwards.
  - S4 guidance/fusion (5): switching the docked set changes fused
    directives; fused limits are the UNION of all docked personas'
    limits including the user persona's; the user persona appears in
    fusion threads/directives/prefer_skins; pilot switch honored.
  - S5 authority fence (2): with defaults docked and the user
    persona piloting, `confirm_proposal` under producers
    `persona:manny`, `harbor_light`, `bimo`, `persona` is denied
    (`acceptance_policy_denied`) and the proposal stays pending;
    a plain `repl_user` attempt without an approval is denied
    identically, and neither BIMOBody nor the personas module
    exposes any confirm surface.
- Mutants (both reverted by inverse edit only):
  1. Authority fence: canonical-collision refusal in
     `validate_custom_persona` disabled → suite FAILS at
     `pm_create_collision_canonical`. Revert → 28/28.
  2. Roster drop: oracle's id corrupted → suite FAILS at
     `pm_roster_complete`. Revert → 28/28.
- Neighbor suites (all exit 0): personas module smoke PASS ·
  persona_purity PASS · pp4_bimo_dock PASS · r75_forge PASS ·
  persist_full_roundtrip PASS · open smoke 7/7 · c9_dualmode 26/26 ·
  translate_intent_args 18/18 · translate_dead_args PASS ·
  translate_word_counts PASS · english_composer PASS ·
  phrase_tests PASS · polyglot_tests PASS.
- No campaign run (focused suites only, per lane discipline); no
  merge performed or requested.

## Limitations

- The active user layer is process-level module state (the same
  pattern as other module registries in this codebase): the loaded
  Program's records own it; constructing/loading a Program replaces
  it wholesale from that program's records. Per-owner durability is
  through the program save, as built.
- REPL/Studio commands for persona creation are not added here;
  creation is a Program/personas API. The existing REPL persona
  commands (activate/dock/fuse/roster) resolve user personas through
  the same lookups with no further change.
- Row #155 is not flipped; credit settles via the normal post-merge
  path. Part IV lands as a whole Part under §32 at its final head.

## Exact ask

Keeper + Director: **scoped CODE review of this section** (row #155
PERSONAMATRIX user layer) at the section head named in the PR #505
package comment. No merge is requested.

---

## Correction addendum — Director CORRECTION REQUIRED 7069171691 (2026-11-21)

**Defect (as ruled):** at S2 head c572a215 the user layer lived in
`CUSTOM_PERSONAS`, a mutable module-global dict: `create_custom_persona`
wrote it, the lookups read it, and `activate_custom_personas()` cleared
and replaced it on every Program construction/load — process-wide, not
owner-scoped. Two live Programs in one process could expose or
overwrite each other's custom personas; loading owner B cleared owner
A's active registry. The S2 "Limitations" note above described that
wholesale-replacement behavior; it is SUPERSEDED by this addendum.

**Reproduction (failing-first, pre-fix):** two-owner A→B→A in one
process — A creates `iso_alpha` (resolves); B merely constructs →
A's persona is GONE from the active registry; A can no longer dock
its own persona (`unknown persona: iso_alpha`); B's later creation is
visible through the unscoped global lookup. Defect reproduced exactly
as ruled.

**Repair — smallest canonical owner-scoped seam, no parallel
registry:** `form/dell_matrix/personas.py` gains `UserPersonaLayer`,
the one layer object inside the canonical module. Each Program owns
exactly one layer (`Program.persona_layer`, created at construction,
activated from its own `user_personas` records); every Program
surface addresses only that layer — create/remove (`open.py`),
lens/status/guide/roster reads, `BIMOBody` and `PersonaMatrix`
(bound via `Program._bind_persona_layer()`, re-bound after persist
restore replaces them), and the persist load path
(`persist_rest.py` activates into the loaded program's own layer).
All personas.py lookups gained an optional `layer=` parameter;
canonical-first resolution is unchanged. Calls without a layer
address the process DEFAULT layer (`CUSTOM_PERSONAS` is now that
default layer's records dict) — the surface for single-program tools
(REPL, vision, standalone BIMOBody). A Program never writes the
default layer.

**Evidence:**
- New failing-first isolation section S6 in
  `form/personamatrix_test.py` (10 checks): cross-owner read,
  creation (incl. same id in both owners with different records),
  construction-preservation A→B→A, load non-clobber, scoped removal,
  save/reload per owner, construction-with-records activation, and
  default-layer untouched. RED pre-fix (behavioral repro above +
  suite failure at the first scoped surface); GREEN post-fix.
- Suite: **38/38** (all 28 S2 checks preserved and passing + 10 new).
  S3/S4 reads re-pointed at the owner scope they always meant.
- Mutants (inverse-edit reverts only): (1) canonical-collision
  refusal disabled → FAIL at `pm_create_collision_canonical`;
  (2) oracle id corrupted → FAIL at `pm_roster_complete`;
  (3) Program construction activation misdirected to the default
  layer → FAIL at `pm_iso_construct_with_records` (a check added
  after the mutant first slipped the suite — the construction-with-
  records path is now pinned).
- Neighbors (all PASS): personas smoke · persona_purity 6/6 ·
  pp4_bimo_dock 35/35 · r75_forge 69/69 · persist_full_roundtrip
  114/114 · open smoke 7/7 · c9_dualmode 26/26.
- Post-fix A→B→A verification: A's persona intact after B
  constructs, A docks it, B cannot read it, default layer clean.

**Limitations (current, honest):** module-level calls without a
layer still address the shared default layer by design (single-
program tools); multi-Program processes must use Program surfaces or
pass a layer — that is the seam the correction ordered. No merge
requested; CODE-CONFIRM remains withheld pending the Director's
re-review and the independent Keeper delta challenge at the new head.
