# C5R.4 LENS — Concrete Signal Definitions (Uni, 2026-11-17)

Status: DEFINITIONS DRAFT for two-checker review. No build is authorized
by this document. It answers the Director's published LENS directive
(delivered via Ace, verified channel, 2026-11-17 ~04:52 CST, against
main 77ea7271): transparent scoring, complete paging, preserved human
confirmation; PlaneRank stays separate. It also resolves Q-C5R.4:
C5.PlaneRank does NOT integrate with the lens — the lens is computed
entirely inside the existing SEE service (Nursery.query) from stored
Proposal fields, and never imports, calls, or reads PlaneRank state.

## 1. Contract

- The lens is an OPT-IN ordering of the existing SEE service:
  `query(..., sort="lens")`. The default ordering is unchanged:
  `(created, id)` ascending, reported as `sort: "created,id"`.
- Ranking changes ORDER ONLY, never membership. A lens traversal
  returns exactly the matched ID set a default traversal returns
  (proven at 1,000 records by the failing-first suite).
- The lens NEVER writes. Confirmation remains Ace's sovereign act;
  no score, at any value, confirms, rejects, deletes, or lands
  anything. The store file is byte-identical after any lens query.
- Transparent scoring: every returned item carries its full score
  breakdown, and the response names the weights version. Anyone can
  recompute every score by hand from the stored record.

## 2. The score

```
S(p) = 0.40 * LINK(p) + 0.25 * ACE(p) + 0.20 * FRESH(p) + 0.15 * NOVEL(p)
```

Weights version: `lens-v1`. Ordering: S descending; ties break by
`(created, id)` ascending (the preserved default order). Every
component is in [0, 1], computed ONLY from fields stored on the
Proposal record and the matched set itself. Nothing is fabricated:
absent evidence scores as the disclosed neutral for that component,
and the breakdown shows it.

## 3. Signal definitions

### LINK(p) — connectedness to the rest of the store

Mean of three stored components:

- `parents_c = min(len(p.parents), 2) / 2`  → one of {0, 0.5, 1}
- `graph_c   = p.graph_coherence`          → stored [0,1]; 0.0 is the
  recorded value when no graph evidence exists (never invented)
- `harmony_c = p.harmony`                  → stored [0,1]; 0.0 is the
  recorded neutral for non-pair proposals

`LINK = (parents_c + graph_c + harmony_c) / 3`

### ACE(p) — Ace-attention lineage

`ACE = 1.0` if following `supersedes_id` links from p within the store
reaches a record whose status is `confirmed` (Ace acted on this
lineage); otherwise `ACE = 0.0`. Binary in v1 by design: the stored
record either proves an Ace confirmation in the chain or it does not.
No softer inference is permitted — an unproven attention claim must
not move a ranking.

### FRESH(p) — recency with per-collection fade

`FRESH = 1 / (1 + age_days / half_life_days(collection(p)))`

- `age_days` is computed from `p.created` (ISO-8601) to the query's
  evaluation instant. The evaluation instant is bound into the cursor
  on page 1, so one traversal is one frozen ranking even if the
  wall clock moves between pages.
- `collection(p)` is the record's C5R.3 effective topic (stored topic,
  else `unclassified`). The half-life table is a named mapping
  (`LENS_FADE_DAYS`) so fade rates are per-collection by mechanism
  (Ace's Q-C5R.2 answer). In v1 every collection ships the default
  14.0 days; setting a collection's rate is a data change to that
  table, never a code change to the formula.
- An unparseable `created` yields `FRESH = 0.0` and the breakdown
  flags `fresh_basis: "unknown"` — no fabricated recency.

### NOVEL(p) — dissimilarity inside the matched set

`NOVEL = 1 - max over q in matched, q != p of J(tokens(p), tokens(q))`

- `tokens(x)` = the casefolded whitespace token set of
  `label + " " + words`.
- `J` is Jaccard similarity. NOVEL is computed over the matched set
  (after filters, before paging) and the response discloses the
  matched-set size it was computed against.
- A single-record matched set gives `NOVEL = 1.0`. An empty token
  set gives `NOVEL = 0.0` (no content to be novel with). An exact
  duplicate of another matched record gives `NOVEL = 0.0`.

## 4. Cursor and refusal semantics (inherited from SEE, extended)

- The cursor binds: owner, mode, filters, page size, sort (`lens-v1`
  + weights version), and the evaluation instant. Continuing with an
  explicitly different sort refuses `CURSOR_FILTER_MISMATCH`; an
  unpassed sort defers to the bound lens (SEE convention).
- A store change between pages refuses `STALE_CURSOR` (the existing
  disk-signature mechanism). A stale in-memory instance refuses
  `STALE_OWNER_STATE` before page 1, exactly as SEE does today.
- An unknown sort value refuses `SORT_UNSUPPORTED` (typed, never a
  silent fall back to the default order).

## 5. REPL surface (build phase)

`proposals browse sort:lens` / `proposals search sort:lens <term...>`
render the ranked order with each item's score shown; continuations
ride the same cursor grammar. The legacy `proposals` and `rank`
doors are untouched.

## 6. What this is not

- Not PlaneRank: no shared code, no shared state, no cross-reads.
- Not a filter: membership is the matched set, whole and unchanged.
- Not an actor: it cannot confirm, reject, delete, organize, or
  persist anything. It is a lens in the literal sense — it changes
  what you look at first, nothing else.

## 7. Proof contract

`form/nursery_c5r4_lens_test.py` (failing-first, this package):
L1 default-order pin (passes today), L2–L12 the lens contract above
(all failing today for the stated reason: no lens exists). The build
is complete only when the whole suite passes at an exact head plus
the standard campaign/CI/checker gates.
