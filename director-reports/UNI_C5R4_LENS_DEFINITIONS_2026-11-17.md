# C5R.4 LENS — Concrete Signal Definitions (Uni, 2026-11-17)

Status: DEFINITIONS DRAFT v2 for two-checker review. No build is
authorized by this document. It answers the Director's published LENS
directive (delivered via Ace, verified channel, 2026-11-17 ~04:52 CST,
against main 77ea7271) as refined by the Director's C5R.4 scope
decisions and next-circuit brief (EXE comment 6945952130 on PR #444,
2026-11-17): transparent scoring, complete paging, preserved human
confirmation; PlaneRank stays separate. It also resolves Q-C5R.4:
C5.PlaneRank does NOT integrate with the lens — the lens is computed
entirely inside the existing SEE service (Nursery.query) from stored
Proposal fields, and never imports, calls, or reads PlaneRank state.

v2 changes against v1 (all from 6945952130): tie-break is the stable
proposal ID after equal full-precision S; a formal signal-contract
table with measured-zero vs missing evidence and partial-coverage
disclosure (no silent renormalization); the FRESH half-life is an
explicit PROVISIONAL policy with Ace's Q-C5R.2 choice kept open and
visible; the lens family is S / newest / oldest / alphabetical; the
paging-hazard rule binds every mutable scoring input; the legacy
Inspire recipe is named, kept, and fenced (section 8); the Keeper
forward-check list is folded into the acceptance suite (L13–L19).

## 1. Contract

- The lens is an OPT-IN ordering of the existing SEE service:
  `query(..., sort="lens")` (family in section 3.6). Lenses reorder
  only within the same owner / status / search / organization
  filter scope the query already defines — a low rank, a missing
  signal, or age NEVER removes a record from a view or changes its
  confirmation state. The default ordering is unchanged:
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

Weights version: `lens-v1`. Ordering: S descending at FULL
precision; equal full-precision S breaks by stable proposal ID
ascending. Scores may be rounded for display only — rounding never
feeds the ordering. Every component is in [0, 1], computed ONLY
from fields stored on the Proposal record and the matched set
itself. Nothing is fabricated: each component carries an evidence
state (section 3.5); a missing component is disclosed as missing
with the score flagged partial — weights are NEVER silently
renormalized and a partial score is never presented as full.

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
not move a ranking. Confirm/reject COUNTS are not attention and are
never used as a proxy. If a `supersedes_id` points outside the store
(dangling link), the traversal is incomplete: ACE reports its value
with evidence state `partial` and the dangling link named — the gap
is disclosed, never silently treated as a complete search.

### FRESH(p) — recency with per-collection fade

`FRESH = 1 / (1 + age_days / half_life_days(collection(p)))`

- `age_days` is computed from `p.created` (ISO-8601) to the query's
  evaluation instant. The evaluation instant is bound into the cursor
  on page 1, so one traversal is one frozen ranking even if the
  wall clock moves between pages.
- `collection(p)` is the record's C5R.3 effective topic (stored topic,
  else `unclassified`). The half-life table is a named mapping
  (`LENS_FADE_DAYS`) so fade rates are per-collection by mechanism.
- PROVISIONAL POLICY (Director 6945952130): the per-collection
  half-life values are Ace's open choice (Q-C5R.2) — Uni does not
  invent them. Until Ace rules, v1 runs on the explicit provisional
  policy "14.0 days for every collection", and every lens response
  names that policy as provisional with Q-C5R.2 still open. When Ace
  rules, only the table changes; the formula and this contract do
  not.
- An unparseable `created` yields `FRESH = 0.0` with evidence state
  `missing` and the breakdown flags `fresh_basis: "unknown"` — no
  fabricated recency.

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

### 3.5 Signal contract table (Director 6945952130, item 5)

| Signal | Source (stored) | Normalization | Range | Provenance in response | Absent / malformed handling |
|---|---|---|---|---|---|
| LINK | `parents`, `graph_coherence`, `harmony` on the Proposal record | mean of `min(len(parents),2)/2`, `graph_coherence`, `harmony` | [0,1] | per-component value + evidence state | a key absent from the stored record (pre-R3.6 legacy) = evidence `missing`, value enters at 0.0, score flagged partial; a stored 0.0 = evidence `measured` (a real zero, never conflated with missing) |
| ACE | `supersedes_id` chain + `status` of reached records | binary | {0,1} | value + evidence state | complete traversal with no confirmed ancestor = `measured` 0.0; dangling `supersedes_id` = evidence `partial`, link named |
| FRESH | `created` (ISO-8601) + bound evaluation instant + `LENS_FADE_DAYS[effective topic]` | `1/(1+age_days/half_life)` | (0,1] | value + `fresh_basis` | unparseable `created` = evidence `missing`, value 0.0, `fresh_basis: "unknown"` |
| NOVEL | `label` + `words` token sets over the matched set | `1 - max Jaccard` | [0,1] | value + matched-set size | empty token set = evidence `missing`, value 0.0; singleton matched set = `measured` 1.0 |

Evidence states are part of the score breakdown on every item:
`lens: {score, link, ace, fresh, novel, partial, evidence}` where
the four components are their numeric values, `partial` is true
when any component's evidence is not `measured`, and `evidence`
maps each component (for LINK, each sub-component) to `measured` /
`missing` / `partial`. Revisions to any signal definition
increment the weights version (`lens-v2`, ...) and are recorded
here; a cursor bound to an older version refuses rather than
mixing versions mid-traversal.

## 3.6 The lens family

`sort` accepts exactly: `lens` (the S ranking above), `newest`
(created desc, ID asc), `oldest` (created asc, ID asc — the same
order as today's default, named), `alphabetical` (label casefold
asc, ID asc). Every lens obeys the identical contract: membership
never changes, paging is complete, cursors bind the lens, nothing
writes. The default (no sort passed) remains `oldest`'s order,
reported as today (`created,id`).

## 4. Cursor and refusal semantics (inherited from SEE, extended)

- The cursor binds: owner, mode, filters, page size, sort (`lens-v1`
  + weights version), and the evaluation instant. Continuing with an
  explicitly different sort refuses `CURSOR_FILTER_MISMATCH`; an
  unpassed sort defers to the bound lens (SEE convention).
- PAGING HAZARD RULE (Director 6945952130): a continuation is valid
  only when EVERY mutable scoring input is unchanged. In the S
  recipe every input is either (a) inside the nursery file — LINK,
  ACE, and NOVEL read stored records only, and the file's disk
  signature covers them — or (b) the evaluation instant, bound into
  the cursor. There is no third input: the S recipe reads no
  preference model, no Plane evidence, no external state (that
  external dependence is precisely what keeps the legacy recipe,
  section 8, from being this lens). A store change between pages
  refuses `STALE_CURSOR`; there is no mid-traversal recomputation
  against changed inputs, and no repeats or skips across pages.
- A stale in-memory instance refuses `STALE_OWNER_STATE` before
  page 1, exactly as SEE does today.
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
L1 default-order pin (passes today), L2–L19 the lens contract above
(all failing today for the stated reason: no lens exists). L13–L19
carry the Keeper forward-check list from 6945952130: per-lens
1,000-record membership, equal-score ID tie-break, missing-vs-zero
evidence, FRESH timestamp boundaries under the provisional policy,
a weight-permutation control (the implementation's order must match
the STATED weights' hand computation and differ from a permuted
weights computation where the two disagree), changed-lens cursor
refusal, and public-path confirmation of the last-ranked pending
proposal. The build is complete only when the whole suite passes at
an exact head plus the standard campaign/CI/checker gates.

## 8. The legacy lens — named, kept, fenced (Director 6945952130, item 3)

`Program.ranked_proposals` (form/open.py) already ranks: the Inspire
preference blend (0.65 affinity + 0.35 tanh(preference)) with
harmony / graph_coherence tie-breaks and an affinity fallback. That
recipe is hereby named the LEGACY LENS. It must never become an
undocumented secondary formula beside the S lens:

- The legacy lens KEEPS its current behavior for its current
  callers in this circuit. C5R.4 does not replace it, retune it, or
  silently reroute any caller.
- Callers inventoried at main 77ea7271: form/dell_matrix/
  code_evolution.py, live_visual.py (5 sites), sacred_geometry.py,
  visual.py, form/mandell/executor_leaf.py, and the REPL `rank`
  door (form/repl.py). The Dell 46 and snapshot surfaces ride these
  same callers.
- Pinned ordering assertions Uni has enumerated (Uni side; the
  Keeper's independent enumeration rides her forward check, and
  BOTH enumerations must agree before any expected result is
  replaced): form/mandell/p3_r35_integration_proof.py
  (bypass-must-fail on ranked consumption),
  form/mandell/p3_r36_graph_harmony_proof.py (B4 + ranked
  sections), form/nursery_c5r1_readpath_test.py,
  form/nursery_c5r2_see_test.py.
- Any future migration of a caller from the legacy lens to a SEE
  lens is its own circuit with its own failing-first evidence; the
  legacy lens is tested separately under its own name until then.
