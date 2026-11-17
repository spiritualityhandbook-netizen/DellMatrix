# C5R.4 LENS — Concrete Signal Definitions (Uni, 2026-11-17)

Status: DEFINITIONS v3 — revised per Director source review
6946155095 (PR #468, at v1 head 149c96e1) and Director EXE
6945952130 (PR #444). REVISE PLAN / BUILD NOT YET AUTHORIZED.
No production build, merge, or credit is claimed by this package.

Authority chain: the Director's published LENS directive (via Ace,
verified channel, 2026-11-17, against main 77ea7271) — transparent
scoring, complete paging, preserved human confirmation, PlaneRank
stays separate — as corrected and closed by the two rulings above.
Q-C5R.4 is resolved: C5.PlaneRank (MWL 141, a planned Plane-field
component; no such module exists in form/) does NOT integrate. The
lens is computed entirely inside the existing SEE service
(Nursery.query) from stored Proposal fields and the matched set.

## 1. Contract

- **S is the DEFAULT ordering** of the SEE service (browse and
  search). A query with no sort returns S order and reports
  `sort: "lens-v1"`. Three explicit alternatives ride the same
  contract: `newest` (created desc, ID asc), `oldest` (created asc,
  ID asc — the historical default order, preserved as an explicit
  chronological lens), `alphabetical` (label casefold asc, ID asc).
- Ranking changes ORDER ONLY, never membership, within the same
  owner / status / search / organization-filter scope the query
  already defines. A lens traversal returns exactly the matched ID
  set the `oldest` traversal returns (proven at 1,000 records,
  mixed statuses, and under filters).
- The lens NEVER writes. Confirmation remains Ace's sovereign act;
  no score, at any value, confirms, rejects, deletes, or lands
  anything. Stored payload, status, and organization are
  byte-identical after any lens query.
- Transparent scoring: every returned item carries its score and
  full component breakdown with evidence states; the response names
  the weights version and the effective configuration identity
  (section 5). Anyone can recompute every score by hand from the
  stored record, the disclosed comparison corpus, the evaluation
  instant, and the configuration.

## 2. The score

```
S(p) = 0.40 * LINK(p) + 0.25 * ACE(p) + 0.20 * FRESH(p) + 0.15 * NOVEL(p)
```

Weights version `lens-v1`. Ordering: S descending at FULL
precision; equal full-precision S breaks by stable proposal ID
ascending (no other criterion — age is never a hidden tie-break).
Rounding is for display only and never feeds the ordering. When a
component's evidence is missing or malformed, its contribution is
0, the weights are NOT renormalized, and the score is flagged
`partial` — a partial score is never presented as fully evidenced.

## 3. Signal definitions

### 3.1 LINK(p) — connectedness to the rest of the store

Mean of three stored components:

- `parents_c = min(unique_valid_parents(p), 2) / 2`, where
  unique_valid_parents counts DISTINCT parent IDs that resolve to
  records in the same store. Duplicate parent strings never raise
  connectedness; parent IDs that do not resolve are named in the
  evidence as unresolved and do not count.
- `graph_c = p.graph_coherence`, `harmony_c = p.harmony` — each
  with presence-tracked evidence (section 3.5).

`LINK = (parents_c + graph_c + harmony_c) / 3`

### 3.2 ACE(p) — human-attention component (provenance-limited)

Status alone does NOT prove Ace attention: `Nursery.confirm(pid)`
writes `status='confirmed'` without recording an actor, and
`supersedes_id` records predecessor identity, not an attention
receipt. Therefore, in v1:

- **ACE is explicitly MISSING on every record**: contribution 0,
  weights unchanged, every S flagged partial with
  `evidence.ace = "missing"`. This is the honest state of the
  evidence; no proxy is silently counted as attention.
- The confirmed-lineage signal is still computed and disclosed
  SEPARATELY as `ace_proxy` (1.0 if the supersedes chain reaches a
  confirmed record, else 0.0). It is labeled a proxy in every
  response, is never described as verified personal Ace attention,
  and contributes NOTHING to S in v1.
- Lineage traversal is cycle-safe (visited set; a cycle terminates
  and is reported) and reports broken references (a supersedes_id
  pointing outside the store is named; evidence `partial`).
- Before ACE may count in any later version, a trustworthy
  human-action source must be traced and reviewed (build-phase
  investigation: `Program.confirm_proposal`'s producer parameter
  and the acceptance-data records are the first candidates). No
  unreviewed attention writer may be introduced to solve this.

### 3.3 FRESH(p) — recency, reciprocal fade v1

The fade function is **reciprocal fade v1** (NOT exponential
half-life decay, and never named as such):

```
FRESH = 1 / (1 + age_days / tau(collection(p)))
age_days = max(0, evaluation_instant - created) in days
```

- `collection(p)` is the C5R.3 effective topic. `tau` comes from
  the named table `LENS_FADE_DAYS`. **Ace's ruling (Q-C5R.2,
  ANSWERED 2026-11-17, in-chat):** 14 days is the default AND the
  minimum fade; a collection's tau may be raised only to one of
  24, 48, 96, or 142 days. The lawful tau ladder is therefore
  {14, 24, 48, 96, 142} days; the default table entry for every
  collection is 14.0. A table value outside the ladder is a
  configuration error (below). Until Ace's ruling this ran as the
  Director-accepted provisional uniform 14.0; the ruling keeps the
  same default and adds the ladder. Every lens response names the
  fade policy and the effective tau source.
- Timestamp conventions: the canonical record format
  (`%Y-%m-%dT%H:%M:%SZ`, UTC) and offset-bearing ISO-8601 parse
  (offsets convert to UTC). A naive timestamp (no Z, no offset) is
  ambiguous and contributes disclosed missing/0 — no zone is
  invented. An invalid timestamp likewise contributes missing/0.
- A future-dated `created` clamps age to 0 (FRESH = 1.0) and is
  disclosed with `future_dated: true` — never a negative age,
  never a score above the function's range.
- tau validation: a table value that is not finite, not strictly
  positive, or not on Ace's ladder {14, 24, 48, 96, 142} is a
  configuration error; the lens refuses `LENS_CONFIG_INVALID`
  rather than dividing by it.

### 3.4 NOVEL(p) — lexical dissimilarity proxy

NOVEL is a precisely labeled **lexical** dissimilarity proxy over
the matched set. It does not establish semantic novelty across the
Matrix, and no response may describe it as doing so.

```
NOVEL = 1 - max over q in matched, q != p of J(tokens(p), tokens(q))
tokens(x) = casefolded whitespace token set of label + " " + words
J = Jaccard similarity
```

- The comparison corpus is the matched set (after owner/status/
  search/organization filters, before paging); the response
  discloses the corpus size. **Filter changes can change scores** —
  stated here and in the response metadata.
- Singleton corpus: NOVEL = 1.0 (measured, no comparator exists).
  Empty token set: NOVEL evidence `missing`, value 0.0.
- Tokenization happens once per query snapshot; the 1,000-record
  path is measured in the build packet. No retention cap may be
  introduced to avoid comparison cost.

### 3.5 Component validity, missingness, provenance

Every component on every item reports `{value, evidence}` where
evidence is `measured`, `missing`, `malformed`, or `partial`:

- A stored numeric value inside its range = `measured` (a stored
  0.0 is a real measured zero, never conflated with absence).
- A key ABSENT from the stored record (pre-R3.6 legacy records load
  with dataclass defaults) = `missing`. Presence is tracked at
  load; the dataclass default alone never masquerades as a
  measurement.
- A stored value that is non-numeric, non-finite, or outside its
  declared range = `malformed`: it contributes as missing (0), is
  named in the evidence, and the ORIGINAL stored value is
  preserved untouched — never silently clamped, never rewritten.
- Any missing/malformed component (and in v1, ACE always) flags
  the item's score `partial`.

| Signal | Source | Range | Malformed rule |
|---|---|---|---|
| LINK.parents | `parents` list | {0, 0.5, 1} after unique-valid count | non-list / non-string entries: `malformed`, excluded + named |
| LINK.graph | `graph_coherence` | [0,1] | outside range / non-finite / non-numeric: `malformed` |
| LINK.harmony | `harmony` | [0,1] | same |
| ACE | (no trustworthy source in v1) | {0} contribution | always `missing` in v1; `ace_proxy` disclosed separately |
| FRESH | `created` + bound instant + tau table | (0,1] | naive/invalid timestamp: `missing`; future: clamped + disclosed |
| NOVEL | `label`+`words` over matched corpus | [0,1] | empty tokens: `missing` |

Definition revisions increment the weights version (`lens-v2`,
...) and are recorded here; a cursor bound to an older version or
configuration refuses rather than mixing (section 5).

## 4. Evaluation instant

A query may pass `lens_now` (an offset-aware ISO-8601 instant) to
fix the evaluation instant — for reproducible scoring and tests.
When passed, it governs every FRESH computation in the traversal
and is bound into the cursor. When absent, the service clock at
page 1 governs and is bound the same way. An invalid `lens_now`
refuses `ARGUMENT_INVALID`. A frozen traversal's scores and order
are identical even if the wall clock advances between pages.

## 5. Continuation identity (cursor contract)

The cursor binds: owner, mode, filters, page size, sort + weights
version, the evaluation instant, AND the **effective configuration
identity** — a digest of the weights, the fade-function version,
and the full effective `LENS_FADE_DAYS` table. The nursery file
digest alone is NOT sufficient, because the fade table is mutable
configuration outside the file. Continuation rules:

- Explicitly different sort/filter/size: `CURSOR_FILTER_MISMATCH`.
- Store change between pages: `STALE_CURSOR`.
- Configuration change between pages: `CURSOR_CONFIG_CHANGED`.
- Stale in-memory instance: `STALE_OWNER_STATE` before page 1.
- Unknown sort: `SORT_UNSUPPORTED`. Invalid tau at query time:
  `LENS_CONFIG_INVALID`.
- No mid-traversal recomputation against changed inputs; no
  repeats or skips across pages.

## 6. Migration contract (ranked_proposals and its consumers)

`Program.ranked_proposals` (form/open.py) currently orders the
pending scope by the LEGACY recipe: the Inspire preference blend
with harmony/graph_coherence tie-breaks and an affinity fallback.
Under C5R.4 the build migrates the consumers to the SEE lens:

- `ranked_proposals` keeps its signature and its pending scope and
  membership, but its ORDER becomes the S lens order over that
  scope (via Nursery.query), with the score breakdown available on
  each returned record. The Inspire preference model itself is not
  modified; only its use as ranked_proposals' ordering authority
  retires.
- Consumers inventoried at main 77ea7271 — form/dell_matrix/
  code_evolution.py, live_visual.py (5 sites), sacred_geometry.py,
  visual.py, form/mandell/executor_leaf.py, the REPL `rank` door
  (form/repl.py), and the Dell 46 / snapshot surfaces riding these
  callers — keep working against the same signature; what changes
  is the order and the disclosed scores.
- REPL doors: `proposals browse` / `proposals search` show the
  default S order with each item's score; `sort:<lens>` tokens
  select the alternatives; `rank` renders the migrated order. The
  legacy `proposals` door is untouched.

**Assertion mapping** (each old ordering assertion, Uni side;
the Keeper's independent enumeration agreed at v2 and is re-run
against this v3 mapping in her recheck):

| Assertion | Disposition |
|---|---|
| p3_r35_integration_proof bypass-must-fail (ranked consumption of harmony/graph signals) | SUPERSEDED as written — the consumer changes. The underlying contract (stored harmony/graph evidence affects ranking) is PRESERVED through LINK and re-proved by the lens suite's consumption checks (suite L20). |
| p3_r36_graph_harmony_proof B4 + ranked sections | SUPERSEDED as written; same replacement as above. |
| nursery_c5r1_readpath_test R2 (ranked count + ID set == list set) | PRESERVED — pending scope and membership do not change; only order does. |
| nursery_c5r2_see_test S1 (default traversal in (created,id) order) | SUPERSEDED for the default (now S); PRESERVED as the `oldest` lens pin. The SEE suite is updated in the build PR to pin default = S and oldest = historical order. |
| nursery_c5r2_see_test docstring note (ranked_proposals pending-only) | PRESERVED (informational; still true). |

Until the build lands, the legacy recipe remains the live
behavior, named the LEGACY LENS and tested under its own name;
nothing in this plan changes any expected result before the build
PR does so deliberately, assertion by assertion, per this map.

## 7. What this is not

- Not PlaneRank: no shared code, state, or cross-reads (suite
  tripwire enforces it).
- Not a filter: membership is the matched set, whole and unchanged.
- Not an actor: it cannot confirm, reject, delete, organize, or
  persist anything. A low rank, a missing signal, or age never
  removes a record or changes its confirmation state — the
  lowest-ranked pending proposal confirms through the public path
  exactly like the highest (suite-proved).

## 8. Proof contract

`form/nursery_c5r4_lens_test.py` (failing-first, this package;
v3: 21 checks, L1–L20 with L10 split in two). At this stage the suite is explicitly STANDALONE
(Director registration clarification, 6946155095): it is not in
form/regress.py, so plan-stage failure cannot break main
regression. Mandatory registration rides the implementation
candidate and is verified before admission. The build is complete
only when the whole suite passes at an exact head, the SEE suite
updates land with it, and the standard campaign/CI/checker gates
close.

## 9. Open items at contract close (Director's decision)

- ACE: whether the traced human-action source (if any qualifies)
  admits ACE into S in v1, or ACE remains missing until a reviewed
  provenance mechanism exists. Uni's position: missing until
  proven — no attention claim without a receipt.
- Q-C5R.2: ANSWERED by Ace 2026-11-17 — 14 days default and
  minimum; raisable per collection to 24, 48, 96, or 142 days
  (section 3.3). No longer open.
