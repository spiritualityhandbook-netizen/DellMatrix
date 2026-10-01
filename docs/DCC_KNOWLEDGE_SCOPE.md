# Contextual Knowledge: Selection → Scope → Relevance V2 → Conflict V1 → Lineage V1

How DellMatrix answers "grow using knowledge about <context>".

**AUTONOMY = NO.** This is deterministic, bounded knowledge routing — not
autonomy. The system selects, ranks, checks, and consumes knowledge by
fixed, inspectable rules; it does not choose goals, invent intent, or act
without the user's command.

## Chain

lifecycle (DCC-VII/VIII)
→ contextual selection (DCC-IX)
→ multi-selection + contribution evidence (DCC-X)
→ enforced consumption scope (DCC-XI)
→ Relevance V2 ranking (DCC-XII)
→ Conflict V1 detection (DCC-XIII)
→ Lineage V1 evidence (DCC-XIV)
→ routable subset
→ consumer
→ provenance

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
