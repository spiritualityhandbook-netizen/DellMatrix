# Contextual Knowledge: Selection → Consumption Scope

How DellMatrix answers "grow using knowledge about <context>".

**AUTONOMY = NO.** This is deterministic, bounded knowledge routing — not
autonomy. The system selects and consumes knowledge by fixed rules; it does
not choose goals, invent intent, or act without the user's command.

## DCC-IX: Contextual Selection

`select_for_context(program, context)` ranks confirmed + promoted cube units
by textual Jaccard overlap with the context. Deterministic ordering:
score DESC, proposal ID ASC. Max 5. Pending/rejected units are never eligible.

## DCC-X: Multi-Knowledge Selection + Contribution Proof

Dell 37's receipt records which selected units produced offspring via
parentage tracking (`contributions`). Provenance, not influence: offspring
are traced to the parents they actually list.

## DCC-XI: Context-Scoped Consumption

Selection alone did not constrain the consumer: `RingedGrowth.run(plane)`
enumerated the entire plane. DCC-XI closes that boundary.

Mechanism: **read-only scoped plane view** (`ScopedPlaneView`).
- `.units` exposes ONLY the selector-approved subset (snapshot dict).
- All other plane API (`enhance_scope`, spatial methods) delegates to the
  real plane; delegated methods only weight affinity between scoped pairs —
  they cannot introduce new units (the sole enumeration point is
  `list(plane.units.keys())` inside `RingedGrowth.run`).
- `grow_ideas(cycles, scope_ids=None)`: `None` preserves historical
  full-plane behavior (baseline growth unchanged). A supplied list strictly
  constrains consumption; unknown IDs raise instead of widening scope.
- The view is constructed per call and never persisted — no scope leakage.

Receipt evidence (`last_nurture`):
- `selected_ids` (selector output) and `consumer_scope_ids` (what the
  consumer actually received) — equality proves selected == consumed.
- `scope_mode`: `"contextual"` or `"full"`.

Rules:
- Zero-match → empty scope → no knowledge-parented offspring. Never a
  silent fallback to the full plane.
- Explicit `use idea <pid> to grow` is unchanged (full-plane, DCC-VIII).
- Baseline `grow` is unchanged unless explicitly scoped.
- Failure: scope validated before construction; consumer exceptions remove
  partial proposals and record an honest failure receipt.

Scope enforces the selector's output faithfully — it does not improve the
selector. Jaccard matches surface tokens, not meaning ("plant growth" and
"growth plant" score identically). That is a selector-quality limitation,
separate from scope-enforcement correctness.
