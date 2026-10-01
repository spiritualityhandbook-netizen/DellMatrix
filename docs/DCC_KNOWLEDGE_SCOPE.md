# Contextual Knowledge: Selection → Consumption Scope → Relevance V2

How DellMatrix answers "grow using knowledge about <context>".

**AUTONOMY = NO.** This is deterministic, bounded knowledge routing — not
autonomy. The system selects, ranks, and consumes knowledge by fixed,
inspectable rules; it does not choose goals, invent intent, or act without
the user's command.

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
