# Contextual Knowledge: Selection → Scope → Relevance V2 → Dependency V1 → Conflict V1 → Lineage V1 → Supersession V1

How DellMatrix answers "grow using knowledge about <context>".

**AUTONOMY = NO.** This is deterministic, bounded knowledge routing — not
autonomy. The system selects, ranks, checks, and consumes knowledge by
fixed, inspectable rules; it does not choose goals, invent intent, or act
without the user's command.

## Chain

lifecycle (DCC-VII/VIII)
→ revision/supersession (DCC-XVI: only active revisions route)
→ lineage (DCC-XIV: persisted ancestry)
→ dependency validity (DCC-XV: current qualification of required ancestry)
→ eligibility (confirmed + on-plane + revision-active + dependency-valid)
→ Relevance V2 ranking (DCC-XII)
→ top-5 selection
→ Conflict V1 detection (DCC-XIII)
→ routable subset
→ enforced consumption scope (DCC-XI)
→ consumer
→ provenance (DCC-X, XIV)

## DCC-VII / VIII: Foundations

Accepted knowledge lifecycle (confirm/promote) and explicit knowledge use
(`use idea <pid> to grow`). The explicit path remains full-plane and
unchanged by later cycles.

## DCC-IX: Contextual Selection

`select_for_context(program, context)` ranks confirmed + promoted cube units
against the context. Pending/rejected units are never eligible.

## DCC-X: Multi-Knowledge Selection + Contribution Evidence

Dell 37's receipt records which selected units produced offspring via
parentage tracking (`contributions`). Provenance, not influence: offspring
are traced to the parents they actually list.

## DCC-XI: Enforced Contextual Consumption Scope

Selection alone did not constrain the consumer. DCC-XI closed that boundary
with a read-only `ScopedPlaneView`: `.units` exposes only the
selector-approved subset; `grow_ideas(cycles, scope_ids=None)` with `None`
preserving historical full-plane behavior. Receipt exposes
`consumer_scope_ids` + `scope_mode`; zero-match yields an empty scope, never
a silent full-plane fallback.

## DCC-XII: Deterministic Explainable Relevance V2

The scope mechanism is trustworthy; DCC-XII targets selector *quality*.

### Scoring contract (`selector_version: 2`)

For each eligible unit, all from existing text fields (label/detail/words)
with the repository's existing tokenization:

| Signal | Definition |
|---|---|
| `score` (Jaccard) | \|ctx ∩ unit\| / \|ctx ∪ unit\| — historical meaning, unchanged |
| `coverage` | \|ctx ∩ unit\| / \|ctx\| — fraction of the context covered |
| `exact_phrase` | 1 if the normalized context is a substring of the normalized unit text, else 0 |
| `ordered` | 1 if context tokens appear as an ordered subsequence of the unit's token sequence, else 0 |

Ranking tuple (total, deterministic): `exact_phrase DESC, ordered DESC,
coverage DESC, jaccard DESC, proposal ID ASC`. Every component is exposed
per selection plus 1-based `rank`; the ranking is reconstructible from the
receipt alone.

Normalization: lowercase, alphanumeric token regex (same as RingedGrowth),
whitespace collapsed. Case, punctuation, and spacing differences do not
affect evidence; repeated words are deduped (no coverage inflation).

Eligibility is unchanged (confirmed AND on-plane). Scoring never weakens
eligibility. Top-5 bound unchanged.

### What Relevance V2 does NOT provide

- No embeddings, no learned semantic model, no world-model understanding.
- No intent invention, no autonomous goals.
- Token order/repetition beyond the documented `exact_phrase`/`ordered`
  signals is invisible (e.g. it cannot judge meaning, only textual evidence).
- Scope enforces the selector's output faithfully; it does not improve it.
  Selector-quality limits and scope-enforcement correctness are separate.

## DCC-XIII: Conflict-Aware Routing (Conflict V1)

Relevance does not prove compatibility. Two highly relevant accepted units
can make textually incompatible claims ("plant growth requires light" vs
"plant growth does not require light"). DCC-XIII detects one bounded,
deterministic pattern — textual polarity conflict — and refuses to silently
combine conflicting units.

### Conflict V1 contract (`conflict_version: 1`)

A conflict is declared for a pair of already-selected units iff ALL hold:

1. **Polarity**: exactly one unit contains a supported explicit negation
   signal — `not`, `no`, `never`, `none`, `neither`, `nor`, `cannot`, or an
   `n't` contraction (detected on raw text; the tokenizer splits
   "doesn't" into "doesn"+"t", whose residue is dropped from the frame).
2. **Shared frame**: the de-negated token sets share >= 2 tokens AND their
   Jaccard similarity >= 0.5.
3. **Prior eligibility**: analysis runs only on selected units; status
   filtering (confirmed AND on-plane) happens before routing, so an
   ineligible claim can never quarantine valid knowledge.

Pair enumeration is over sorted IDs; conflict entries are ordered by
`(id_a, id_b)` and carry `negation_evidence`, `shared_frame`,
`frame_jaccard`, and a `reason` — every decision reconstructible.

### Routing policy

- Every unit in >= 1 conflict pair is **quarantined**; the system does NOT
  choose which claim is "true" (no ID/time/score truth proxy).
- `routable_selected_ids` = V2 rank order minus quarantined IDs.
- The consumer receives exactly the routable set
  (`consumer_scope_ids == routable_selected_ids`); if nothing remains, the
  scope is empty — never a full-plane fallback.
- Receipt keeps V2 relevance evidence AND conflict evidence separate:
  `selected_ids`, `selected_details`, `conflicts`, `conflict_count`,
  `quarantined_ids`, `routable_selected_ids`, `consumer_scope_ids`,
  `scope_mode`, `contributions` (routable units only), `new_proposals`.
- Conflict routing applies only to the contextual Dell 37 path. Ordinary
  growth, explicit `use idea <pid> to grow`, and direct `scope_ids` calls
  are unchanged.

### Three separate questions

- **RELEVANCE**: which knowledge textually matches the context? (V2)
- **CONFLICT**: which selected knowledge shows bounded deterministic
  incompatibility evidence? (V1)
- **TRUTH**: established by NEITHER mechanism. Confirmation status does not
  adjudicate between two conflicting confirmed claims.

### What Conflict V1 is NOT

- Not general contradiction detection, semantic entailment, truth
  verification, fact checking, learned reasoning, or autonomous judgment.
- Morphological variants ("requires"/"require") are distinct tokens.
- Double negation is read as negation (not resolved).
- Paraphrases with disjoint vocabularies are invisible.
- Asymmetric frame breadth may fall below the 0.5 frame rule (documented
  boundary, not a silent miss — the receipt shows what was checked).

## DCC-XIV: Knowledge Evidence Lineage (Lineage V1)

DellMatrix knows which knowledge matches, which claims conflict, and what
may enter the consumer. DCC-XIV adds the persisted ancestry structure:
where each selected claim came from, whether claims share a root, and
what derivation chain produced them.

Built on the existing lineage authority (`form/dell_matrix/lineage.py`):
`parents`, `origin`, and `lineage_version` are assigned at creation,
validated by `assign_lineage` (self-parent, cycle, and missing-parent
rejected), and survive save/load. No parallel provenance database.

### Lineage V1 contract (`lineage_version: 1`)

Per selected unit, all reconstructible from persisted state:

| Field | Definition |
|---|---|
| `unit_id` | the knowledge unit |
| `origin_kind` | `direct` (no parents) or `derived` (has parents) |
| `origin` | persisted origin tag (e.g. `placed`, `confirmed`) |
| `parent_ids` | normalized parents (deduped, stable first-seen order) |
| `root_ids` | sorted transitive ancestors with no parents; a direct unit is its own root |
| `depth` | derivation generations = `lineage_version` (1 direct; 1 + max(parent depths) derived) |
| `status` | `ok` / `cycle` / `missing_parents` / `unknown_unit` |

Malformed lineage is marked, never fabricated: duplicates normalize,
unknown units and missing parents are reported, cycles flagged. Reads use
a cycle-guarded traversal; creation rejects invalid lineage outright.

### Lineage groups (descriptive only)

Selected units are grouped by shared root: `{root_id: [member_ids]}`.
Two units descending from one root are exposed as one lineage group —
never called "two independent sources." `selected_root_ids` and
`root_count` are exposed on the receipt. Lineage never enters the V2
ranking tuple and never resolves a Conflict V1 quarantine.

### Four separate questions

- **RELEVANCE**: how strongly does accepted knowledge text match context?
- **CONFLICT**: does bounded textual evidence indicate selected claims
  should not be silently combined?
- **LINEAGE**: what known ancestry/origin structure does the knowledge
  have?
- **TRUTH**: NOT established by any of the above.

Explicitly: multiple roots != truth; same root != falsehood;
direct != verified; derived != unreliable. There is no external source
verification in this architecture, and none is claimed.

### Trace

`trace lineage <unit_id>` answers "where did this knowledge come from?"
from persisted lineage (parents, roots, depth, status) without raw state
inspection. Plain `trace` behavior is unchanged.

## DCC-XV: Dependency Validity + Transitive Invalidation (Dependency V1)

DCC-XIV records where knowledge came from. DCC-XV answers the separate,
current-state question: do a unit's required ancestors still qualify for
contextual use? If ancestor A is later removed from the plane (the
existing legitimate invalidation path: `plane.remove`, exercised via
undo), descendants B and C keep their correct historical lineage, but
their dependency chain is no longer valid.

Historical lineage is never rewritten to represent invalidity. Dependency
inspection is current-state evidence layered on top.

### Discovery (what the lifecycle actually supports)

Post-confirmation state changes possible in-architecture:

- **EXISTING_EXACT**: `plane.remove(uid)` removes a confirmed unit from the
  plane (undo path); the nursery proposal stays `confirmed`. The ancestor
  becomes absent → descendants' required ancestry is "missing".
- **EXISTING_EXACT**: nursery proposals persist to a per-owner JSON file.
  A restore/legacy fixture may record a confirmed unit's proposal as
  rejected/pending → descendants' ancestry is "invalid". (Only through
  restore fixtures; no public transition does this.)
- **EXISTING_EXACT**: confirmed proposals are terminal — `nursery.reject`
  and `nursery.confirm` both return `None` for confirmed proposals. There
  is no public reject/demote/archive for confirmed knowledge.
- **INSUFFICIENT**: no prior dependency contract existed.
- **OUT_OF_SCOPE**: external source verification, source-quality scoring,
  truth scoring, general provenance beyond persisted ancestry.

Revalidation is **NOT_APPLICABLE**: no legitimate operation restores a
removed unit or re-qualifies an ancestor, so invalidation is one-way.
Validity is always recomputed from current state, never cached.

### Dependency V1 contract (`dependency_version: 1`)

For each unit, deterministic and reconstructible:

| Field | Definition |
|---|---|
| `unit_id` | the knowledge unit |
| `direct_parent_ids` | historical persisted parents (unit record, else nursery proposal) |
| `ancestor_ids` | sorted full transitive historical ancestor set |
| `historical_root_ids` | ancestors with no persisted parents; a direct unit roots itself |
| `invalid_dependency_ids` | sorted ancestors present but unqualified |
| `missing_dependency_ids` | sorted ancestors absent from the plane |
| `dependency_status` | `valid` / `missing` / `invalid` / `malformed` |
| `dependency_reason` | machine-readable cause (e.g. `missing_ancestors:<ids>`) |

Ancestor qualification (mirrors the accepted-knowledge model):

- exists on the plane (present where required)
- nursery proposal status == `confirmed`
- lineage constructible (`ok` or `missing_parents`; cycle/unknown
  disqualifies the ancestor itself)

Status precedence: `malformed` (unknown unit / cycle — evidence cannot be
constructed) > `missing` > `invalid` > `valid`. Direct units with no
parents are vacuously `valid`; no self-dependency is manufactured (their
own standing remains base eligibility's job).

A lineage `missing_parents` status is a dependency-state signal, not an
ancestor disqualifier: the absent ancestors are named in
`missing_dependency_ids`, and the historical parent lists, historical
roots, depth, and origin never change.

### Traversal contract

Historical ancestry walks persisted parent lists (plane unit, falling
back to the nursery proposal which survives plane removal), cycle-guarded
with a seen-set, FIFO order, sorted output. All IDs in
`missing/invalid_dependency_ids`, exclusions, and traces are sorted —
equivalent states produce identical evidence.

### Routing order (actual)

1. lifecycle: confirmed proposals
2. revision/supersession: only `active` revisions are eligible (DCC-XVI) —
   before lineage, dependency, and Relevance V2 ever see the candidate
3. lineage: persisted ancestry (DCC-XIV)
4. dependency validity: eligibility additionally requires
   dependency-`valid` (DCC-XV) — before Relevance V2 ever scores
5. Relevance V2 ranking over revision-active, dependency-valid candidates only
6. top-5 selection (excluded candidates never consume slots)
7. Conflict V1 over selected valid candidates only (an excluded unit can
   neither create a conflict nor quarantine a valid unit)
8. routable subset → enforced consumption scope (DCC-XI)
9. consumer → provenance

Lineage metadata stays descriptive: groups are built from actual selected
knowledge only. `trace dependency <unit_id>` answers "is this knowledge
dependency-valid right now, and if not, why?" exposing historical lineage
(parents, historical roots, origin, depth) alongside current dependency
status.

### Receipt evidence (additive)

- `dependency_version: 1`
- `dependency_valid_count`: dependency-valid eligible candidates
- `dependency_exclusions`: `[{id, dependency_status, dependency_reason,
  invalid_dependency_ids, missing_dependency_ids}]` — which candidate,
  why excluded, which dependency caused it

Relevance fields are not overloaded.

### Boundaries

- Baseline `grow_ideas` (full-plane) is unchanged; no dependency fields
  appear on its receipts.
- Explicit `use idea <pid> to grow` bypasses the selector as before —
  the operator's explicit choice. Dependency filtering applies to
  contextual routing only. If explicit use of dependency-invalid
  knowledge is requested, the command runs; the boundary is documented,
  not silently changed.
- A rejected ancestor can only exist via restore/legacy fixture; normal
  lifecycle never produces one.

### Five separate questions

- **LINEAGE**: what known ancestry/origin structure does the knowledge
  have? (historical, immutable)
- **DEPENDENCY**: do its required ancestors currently qualify?
  (current-state, recomputed)
- **RELEVANCE**: how strongly does accepted knowledge text match context?
- **CONFLICT**: does bounded textual evidence indicate selected claims
  should not be silently combined?
- **TRUTH**: NOT established by any of the above.

Dependency validity is not truth, not relevance, not conflict. Invalid
ancestry propagates deterministically to descendants; dependency-invalid
knowledge cannot silently enter contextual selection or consumption; and
every exclusion is explained on the receipt.

## DCC-XVI: Versioned Knowledge Supersession + Revision Lifecycle (Supersession V1)

Confirmed knowledge can be replaced by an explicit newer revision WITHOUT
deleting or rewriting history. `supersede idea <old_id> with <words>`
(English) / `37[Nurture] :: supersede <old_id> with <words>` (Mandell label),
dispatched through Dell 37 like any other nurture operation.

### What supersession is and is not

- The predecessor REMAINS stored: confirmed proposal, plane unit,
  derivation lineage, all intact and inspectable. Historical != deleted.
- The successor is created as a derivation ROOT (`parents=[]`): revision
  ancestry (which version replaces which) is kept SEPARATE from derivation
  ancestry (Lineage V1). Revision parent != derivation parent.
- Only the active revision routes contextually. Superseded revisions are
  excluded with evidence — never silently used, never silently deleted.
- Confirmation and supersession are separate dimensions: a unit can be
  confirmed AND superseded (accepted history, inactive revision).
- **newer != truer.** Recency grants no truth, rank, or authority advantage.
  Relevance V2 scores text only; the receipt never claims the new revision
  is true or the old one false. superseded != false.
- Linear V1 chains only: each revision has at most one predecessor and one
  successor. No branches, no DAG, no merge.
- Deterministic repeat: superseding an already-superseded unit is refused
  with `already_superseded` and returns the existing successor — a duplicate
  successor is never created.

### Discovery (what the lifecycle actually supports)

- **EXISTING_EXACT**: canonical confirmation (`confirm_proposal` in
  `form/dell_matrix/confirm_lineage.py`) assigns derivation lineage, places
  the unit, confirms the nursery proposal — reused unchanged for the
  successor.
- **EXISTING_EXACT**: nursery proposals persist per-owner JSON; additive
  dataclass fields (`lifecycle_state`, `supersedes_id`, `superseded_by_id`,
  `revision_root_id`, `revision_number`) round-trip through `asdict` /
  `Nursery.load`, and legacy units (fields absent) default to
  active / revision 1 / self-rooted. No fabricated history.
- **EXISTING_EXACT**: `trace lineage` / `trace dependency` extension pattern
  reused for `trace revision <unit_id>`.
- **EXISTING_EXACT**: explicit `use idea <pid> to grow` checks only
  confirmed + on-plane, so explicit naming of a historical (superseded)
  unit keeps working — the receipt now discloses
  `lifecycle_state=superseded`.
- **EXISTING_SAFE**: `Nursery.add` persists-then-rolls-back;
  `Nursery.confirm` pending→confirmed with save-failure restore.
- **INSUFFICIENT**: no prior supersession/revision lifecycle existed;
  removal/deletion cannot represent replacement; the dependency gate did
  not consider revision state.
- **OUT_OF_SCOPE**: truth/authority scoring, revision branches/DAG,
  history rewriting, silent descendant retargeting, new composition
  system.

### Supersession V1 contract (`supersession_version: 1`)

One inspector, `inspect_revision(program, uid)`, is the single authority
reused by the operation, selector, trace, receipts, and tests:

| Field | Definition |
|---|---|
| `lifecycle_state` | `active` / `superseded` / `malformed` / `unknown` |
| `supersedes_id` | predecessor revision, if any |
| `superseded_by_id` | successor revision, if any |
| `revision_root_id` | first revision of the chain |
| `revision_number` | 1-based position in the chain |
| `chain` | ordered revision ids, root → tip |
| `malformed_reason` | machine-readable cause when `malformed` |
| `routable` | true only for `active` |

Malformed conditions (deterministic): bad lifecycle value, active unit
claiming a successor, dangling predecessor/successor links, revision
cycle, inconsistent declared roots, duplicate revision numbers, broken
bidirectional links. Malformed units are inspectable and traceable but
never routable.

`supersede_proposal(program, old_id, words)` is atomic, all-or-nothing:

1. validate (no writes): old exists, confirmed, on-plane, currently active
2. create successor through the legitimate nursery path (pending)
3. establish revision links in memory, then commit (`nursery.save`)
4. confirm/promote the successor via the canonical confirm path
5. persist + emit the auditable receipt

Any failure before the final commit rolls back predecessor metadata, the
pending successor proposal, and plane placement, then re-saves. A failure
at receipt emission (after commit) raises honestly without rolling back
committed state; a retry then hits the deterministic
`already_superseded` refusal.

### Routing and dependency interplay

- The revision gate runs FIRST in eligibility: confirmed + on-plane +
  revision-active, then Dependency V1, then Relevance V2.
- Dependency V1 ancestors must additionally be revision-active: a
  superseded ancestor makes descendants `invalid` with reason
  `superseded_dependency:<ids>`. Historical parents are KEPT — descendants
  are never silently retargeted to the successor revision.
- Receipt evidence (additive): `supersession_version`,
  `active_revision_count`, `supersession_exclusions`
  (`[{id, lifecycle_state, superseded_by_id, revision_number,
  revision_root_id, reason}]`); each selection carries
  `lifecycle_state`, `revision_number`, `revision_root_id`.
- `trace revision <unit_id>` answers "which accepted version replaces
  which?" — revision chain, predecessor, successor, number, root — without
  touching derivation lineage.

### Boundaries

- Baseline `grow_ideas` (full-plane) is unchanged; no supersession fields
  appear on its receipts.
- Explicit `use idea <pid> to grow` bypasses the selector as before — the
  operator's explicit choice, including for superseded units. The receipt
  discloses the lifecycle state; the boundary is documented, not silently
  changed.
- Malformed revision metadata can only exist via direct state
  manipulation or corrupt restore; normal lifecycle never produces it.
  Malformed units are excluded from routing with evidence.

### Six separate questions

- **REVISION**: which accepted version replaces which? (DCC-XVI;
  current-state lifecycle, history preserved)
- **LINEAGE**: what known ancestry/origin structure does the knowledge
  have? (historical, immutable)
- **DEPENDENCY**: do its required ancestors currently qualify?
  (current-state, recomputed)
- **RELEVANCE**: how strongly does accepted knowledge text match context?
- **CONFLICT**: does bounded textual evidence indicate selected claims
  should not be silently combined?
- **TRUTH**: NOT established by any of the above.

Supersession is not truth, not relevance, not conflict, not dependency.
Active != verified.

## DCC-XVII: Crash-Safe Persistence (Persistence V2)

Three different atomicities guard the knowledge lifecycle. They must not be
confused.

### Three separate atomicities

- **DCC-XVI logical transaction atomicity** — the supersession operation
  is all-or-nothing at the object level: a failure before the final
  nursery commit rolls back predecessor metadata, the pending successor,
  and plane placement; a fresh process can never observe a predecessor as
  superseded unless the corresponding successor revision is completely
  established (certified by `dcc_xvi_atomicity_test`, 101/101).
- **DCC-XVII file replacement atomicity** — the physical save of a
  generation is all-or-nothing at the byte level: a failed or interrupted
  save leaves a fresh process seeing a complete OLD generation or a
  complete NEW generation, never a partially serialized generation
  (certified by `dcc_xvii_test`, 81/81, including literal cross-process
  SIGKILL and os._exit probes).
- **DCC-XVIII checkpoint generation coherence** — the logical state is a
  JOIN of nursery owner JSON and program JSON; the generation protocol
  seals them as one certified generation and the loader never mixes
  files from different generations (certified by `dcc_xviii_test`, 89/89,
  including a literal OS-process crash/recovery matrix).

DCC-XVI orders the logical operation; DCC-XVII makes the physical commit
indivisible; DCC-XVIII makes the multi-file logical checkpoint coherent.
Each can fail independently; together they guarantee the required success
statement: every file participating in one committed logical checkpoint
belongs to the same certified generation; a crash before generation
commit leaves the previous committed generation authoritative; a crash
after commit exposes the new complete generation; loading never
constructs a hybrid from independently valid but generation-mismatched
files; and a failed load never partially mutates live state.

### Persistence V2 contract (`PERSISTENCE_PROTOCOL_VERSION = 2`)

Every canonical write (`Nursery.save`, program save, checkpoint save)
goes through `form/dell_matrix/atomic_write.py`:

1. Serialize the complete payload to bytes BEFORE touching the target.
   A serialization failure leaves the target untouched.
2. Write to a collision-safe sibling temp
   (`<canonical>.dmtmp.<pid>.<random8>`, created `O_CREAT | O_EXCL`,
   mode `0644`), then flush + `os.fsync` the temp.
3. `os.replace(temp, target)` — one atomic same-filesystem rename. There
   is no delete-then-rename, no in-place truncation, no partial JSON.
4. Best-effort parent-directory fsync (`O_DIRECTORY`) so the rename
   itself is durable; the result is observable, not assumed.

Load is read → decode → validate → privately prepare → bind/swap. Every
proposal record is built into a private staged dict and applied ONLY
after all records validate. A truncated, malformed, or schema-invalid
canonical file raises an explicit error (`NurseryLoadError`) — it never
silently becomes an empty nursery, and a failed load never partially
mutates live in-memory state.

Loader precedence: a valid canonical file is the ONLY source of truth.
There is no backup generation, no backup promotion, no fabricated
recovery. Valid canonical → load; otherwise explicit failure.

### Documented durability (what fsync does and does not promise)

- `os.fsync` on the temp orders the file's data to the storage device
  before the rename, and the directory fsync orders the rename itself —
  on filesystems and platforms where those calls are honored.
- This is crash-consistency against process death (SIGKILL), OS crash,
  and power loss **within the documented fsync assumptions**: the
  storage stack must actually persist what fsync reports as persisted.
  No claim is made about hardware or firmware that acknowledges writes
  it has not stored.
- No database transactions, no distributed consensus, no multi-host
  coordination, and no lock-based concurrent-writer framework are
  introduced. Concurrent writers still use the pre-existing nursery
  optimistic SHA conflict detection; last-writer-wins across processes
  is unchanged and out of scope.

### Temp files and cleanup

- Temps are process-unique by PID + randomness; two writers never share
  a temp path.
- A hard crash (SIGKILL, os._exit) between temp write and replace leaves
  a stale temp beside the canonical file. Loaders ignore it; it never
  shadows or merges into canonical state.
- `sweep_stale_tmps(directory)` removes helper temps whose PID is dead
  and leaves temps of live writers alone. It is ordinary hygiene, not
  recovery: sweeping a stale temp changes nothing about the canonical
  generation.
- Injected (non-crash) failures clean up their own temp before raising;
  only literal process death leaves stale temps.

### Boundaries

- Only canonical persisted runtime owner state moved to Persistence V2:
  nursery owner JSON, program canonical JSON, checkpoint JSON
  (private clone files inherit the mechanics through the shared save
  path). Standalone pack export/import and unrelated ledgers/assets are
  untouched — different persistence semantics, not blindly refactored.
- Payload JSON shape is unchanged; Persistence V1 files load as-is.
- ATOMICITY != DURABILITY != RECOVERY. DCC-XVII provides file
  replacement atomicity with documented fsync durability. It provides no
  backup, no restore, no repair, and no recovery narrative.

## DCC-XVIII: Coherent Checkpoint Generations (Checkpoint Generation V1)

DCC-XVII guarantees each canonical file is old-complete or new-complete.
It does NOT guarantee that the files constituting one logical DellMatrix
state belong to the same committed generation: nursery G2 + program G1
are two perfect files describing contradictory logical state. The
authoritative live state is the JOIN of `nursery_<owner>.json` (proposal
decisions, revision lifecycle, lineage source) and `program_<owner>.json`
(plane membership, session state); neither is reconstructible from the
other (the program file's `nursery` field is back-compat only and is
never restored).

### Checkpoint Generation V1 contract (`CHECKPOINT_PROTOCOL_VERSION = 1`)

The smallest justified commit model (`form/mandell/checkpoint_generation.py`):

1. Save the live nursery + live program (Persistence V2 each).
2. Seal byte-exact, immutable, generation-specific member copies
   (`nursery_<ns>.g_<gid>.json`, `program_<ns>.g_<gid>.json`).
3. Validate member SHA-256 fingerprints over the exact sealed bytes
   (detection of mismatch/corruption only — not authentication).
4. Write the generation manifest (V2 atomic) naming the exact member
   filenames, fingerprints, owner, and previous generation link.
5. Atomically replace the CURRENT pointer (`current_<ns>.json`) —
   **the commit boundary**.

A crash before the pointer swap leaves the previous committed generation
authoritative; a crash after it exposes the new complete generation.
Member files are never overwritten after sealing. Generation IDs are
uuid4-derived (stable, unique); wall-clock time is never used for
uniqueness or recovery order. The owner namespace is collision-safe
(`safe_owner` + sha256 prefix of the exact owner bytes), so raw owners
that normalize to the same safe name cannot overwrite each other's
generations.

### Loader contract

1. Locate the committed generation via the CURRENT pointer.
   Absent pointer → `CheckpointNotEstablished`: legacy behavior applies
   (existing legacy loader); the next successful commit establishes
   Generation V1. Nothing is migrated on read.
2. Validate the manifest (protocol version, generation identity,
   `committed: true`, exact owner).
3. Validate every required member's filename identity + sha256
   fingerprint.
4. Parse all members through the existing staged loaders (private
   staging only).
5. Build the private staged Program against the exact staged nursery;
   bind/activate only after the full generation stages successfully.
   A failed load leaves live in-memory state unchanged.

### Recovery (deterministic, no guessing)

If the committed generation is invalid but the manifest's
`previous_generation_id` names a previous committed generation, that
previous generation is fully verified (manifest + every member) and
loaded instead; the receipt records `recovered_from`. If no usable
previous generation exists, `CheckpointLoadError` names both generations
explicitly. Recovery follows the manifest link — never timestamps,
directory order, or heuristics. Corrupt pointer → explicit failure.

### Retention and receipt

Retention keeps the current + previous committed generations and removes
older committed and stale uncommitted artifacts only after a successful
new pointer commit; if the pointer is unreadable, nothing is deleted.
The receipt carries protocol version, generation id, previous
generation id, owner, member identities/fingerprints,
`committed: true`, the retention result, and (on load) `recovered_from`
and `legacy: false`.

### Boundaries

- Program checkpoint files (`program_<owner>_cp_<stamp>.json`,
  `_cp_latest.json`) and `core_i_recovery.py` snapshots are explicit
  checkpoint/rollback artifacts, not normal-load members — out of scope.
- No new semantic knowledge layer is introduced; fingerprints are
  mismatch detectors, not truth signals.
- COHERENCE != ATOMICITY != DURABILITY != RECOVERY. DCC-XVIII adds
  cross-file generation coherence on top of DCC-XVI logical atomicity
  and DCC-XVII file atomicity.
