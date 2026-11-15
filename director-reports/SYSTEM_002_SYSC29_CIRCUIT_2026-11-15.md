# SYSTEM-002 / SYS-C29 — Nursery Store Silent-Truncation Repair

Circuit: SYS-C29 (SYSTEM-002, first bounded circuit)
Authorization: Director ruling 1a1dcc6df0394fb0 (Q-S1.1 CONFIRM), relayed
verbatim by Ace 2026-11-14 19:37 CST; Ace "Exe" 2026-11-14 19:49 CST.
Base: e0ad5e240ce0f91a08de0b1c1fefdd605dce52b3
Branch: uni/sysc29-nursery-words

## 1. Contract

`Nursery.add()` must not silently destroy admitted content. The `words`
field is stored in full up to the system's admitted bound of 5,000 chars;
input beyond the bound is refused explicitly, before any mutation or
save, with no partial write. Exact text, identity, metadata, lifecycle,
and recovery behavior are preserved for all admitted input. Repair scope
is the `words` field ONLY: no new persistence authority, no new state
files, no unrelated edits. Sibling truncations in the same method are
classified with evidence (section 3) and are NOT repaired by this
circuit.

## 2. Failing-first receipt (summary; full record in the circuit file)

Reproduction at the actual public path — `Nursery.load(path)` ->
`add()` -> `save()` -> fresh `Nursery.load(path)` -> exact compare —
run before any repair (record: hidden_files/sysc29_repro_2026-11-14.md;
rerunnable script: hidden_files/sysc29_repro.py):

| Case | Input | Stored | Intact |
|---|---|---|---|
| ascii words | 300 chars | 240 chars | NO |
| admitted-max words | 5,000 chars | 240 chars | NO (4,760 chars destroyed) |
| unicode words | 300 chars | 240 chars | NO |

3/3 cases silently lost data; no error was raised in any case. The cut
is `form/dell_matrix/nursery.py` in `Nursery.add()`: `words=words[:240]`.

## 3. Sibling classification (classify-only; NOT repaired here)

All cuts sit in `Nursery.add()` beside the repaired `words` cut. The
classification standard: a cut is a BOUND-CONSISTENT GUARD when it
exactly re-asserts an admitted bound the system's own admission path
already enforces by explicit refusal; it is a SILENT-LOSS DEFECT when it
destroys content the admission path admitted. The admission path of
record is the inference dock's proposal validation
(`form/dell_matrix/inference_dock.py`: MAX_LABEL_CHARS=200,
MAX_WORDS_CHARS=5000, MAX_DETAIL_CHARS=2000, MAX_GOALS=8,
MAX_GOAL_CHARS=200 — each enforced there by an explicit ProviderError
refusal before `nursery.add` is called).

| Field | Cut in add() | Admitted bound elsewhere | Classification | Disposition |
|---|---|---|---|---|
| label | `label[:80]` | dock admits 1..200 chars (MAX_LABEL_CHARS=200), refusing beyond | SILENT-LOSS DEFECT (same class as words, smaller blast radius: a dock-admitted 81..200-char label is silently cut to 80). Mitigating fact: the label is an identifier/display field, and the proposal ID derives from `_slug(label)` which itself uses only `label[:28]`, so identity is unaffected; the loss is display/full-label fidelity only. | Classify-only. Flagged for a future bounded ruling; NOT repaired here (scope is words only). |
| reason | `reason[:160]` | No admitted bound found anywhere in the codebase; the dock composes its own short reason strings (`docked <task> by <subject> via <provider> (model <label>)`) | SILENT BOUND, no admitted contract: nothing admitted is provably destroyed today, but any caller passing a longer rationale loses the tail silently. Guard in effect, defect in kind. | Classify-only. No repair authorized; a future circuit should either admit a bound with explicit refusal or document 160 as the contract. |
| origin | `origin[:120] if isinstance(origin, str) else ""` | No admitted bound; origin is machine-generated provenance of the form `dock:<provider>:<actual model>` (Proposal field comment, Phase E), short by construction | GUARD with large headroom over every value the format can produce; the non-str coercion to "" is explicit shape validation, not truncation of admitted content. No observed loss path. | Classify-only. No action proposed. |
| detail | `detail[:2000] if isinstance(detail, str) else ""` | dock admits detail up to MAX_DETAIL_CHARS=2000, refusing beyond | BOUND-CONSISTENT GUARD for the dock path: the cut exactly equals the admitted bound, so dock-admitted content is never cut. Residual risk: a non-dock caller passing >2000 chars loses the tail silently (no non-dock admission bound exists). | Classify-only. No repair; note the non-dock residual for the record. |
| goals | `[g[:200] for g in (goals or []) if isinstance(g, str) and g.strip()][:8]` | dock admits at most MAX_GOALS=8 goals of at most MAX_GOAL_CHARS=200 each, refusing beyond | BOUND-CONSISTENT GUARD for the dock path (both the per-goal 200 cut and the 8 cap exactly equal the admitted bounds). The isinstance/strip filtering is explicit shape validation. Same non-dock residual as detail. | Classify-only. No repair; note the non-dock residual for the record. |
| **words** | **`words[:240]`** | **dock admits 1..5000 chars (MAX_WORDS_CHARS=5000), refusing beyond** | **SILENT-LOSS DEFECT — the SYS-C29 repair target.** The cut sits 4,760 chars BELOW the admitted bound, so content the system explicitly admitted (including the dock's own maximum) was destroyed with no error. words is authored body content (the proposal's substance), not an identifier. | **REPAIRED by this circuit (section 5).** |

## 4. FI-009 fitness receipt — storage mechanism for the words repair

Question: how should admitted words (up to 5,000 chars) be stored so the
240 cut can be removed with the least machinery that provably fits?

Candidates:

A. **Native dynamic storage** — store the full Python `str` through the
   existing save path, unchanged. `Nursery.save()` builds
   `{pid: proposal.to_dict()}` and writes it with
   `atomic_write_json` (whole-file JSON, crash-safe atomic replacement,
   DCC-XVII). A JSON string value has no fixed width anywhere in this
   path: not in the dataclass, not in `to_dict()`, not in the writer,
   not in `Nursery.load()` (which validates record shape via
   `Proposal(**record)` and imposes no length check). The 240 cut in
   `add()` is the ONLY fixed-width element in the entire round trip —
   proven by the failing-first receipt: input arrived intact at `add()`
   and left cut; save/load never touched the length.
B. **Nested/chunked storage** — split words into fixed-size chunks
   (e.g. 240-char segments) stored as a list or sidecar records,
   reassembled on load. This adds: a chunking writer, a reassembly
   reader, a second on-disk shape (legacy files carry plain strings, so
   load must accept both shapes forever), chunk-boundary failure modes,
   and a new place for identity/metadata to desynchronize — to store at
   most 5,000 characters, a size a single JSON string holds trivially.
   Chunking earns its cost when individual values are large enough to
   strain whole-value handling (streaming, partial reads, per-chunk
   addressing); none of those needs exists here: the file is already
   rewritten whole on every save, and 5,000 chars is ~0.005 MB.

Verdict: **A — native dynamic storage.** The persistence layer is
already dynamic end to end; the defect is a single slice expression,
and the fittest repair is to remove the slice and enforce the admitted
bound explicitly at the same site. Chunking would be machinery in
search of a problem at this scale and would create a second storage
shape — the opposite of the fitness standard. The admitted bound
itself (5,000) is retained as a runaway stop per the Elastic Limits
Doctrine: FI-004 elasticity applies to capacity, never to the removal
of safety bounds; beyond the bound the refusal is explicit and
mutation-free instead of silent.

## 5. Implementation

`form/dell_matrix/nursery.py` only (native dynamic storage, per the
section 4 fitness verdict):

- New `NurseryWordsError(ValueError)` and module constant
  `MAX_WORDS_CHARS = 5000` — the Nursery's admitted words bound, equal
  to the dock's admitted maximum.
- `Nursery.add()` now checks the bound FIRST, before computing the
  proposal ID and before any mutation or save: a `str` words longer
  than 5,000 chars raises `NurseryWordsError` and nothing is stored
  (the existing pop-and-raise rollback pattern is not even reached —
  no state is touched).
- The `words=words[:240]` slice is removed; admitted words are stored
  exactly as passed. No other field, behavior, or file changes. No new
  persistence authority; no new state files.

Behavior change, stated plainly: a caller passing words in (240, 5000]
previously received a silently truncated proposal and now receives the
full text; a caller passing >5,000 previously received a silently
truncated proposal and now receives an explicit error. The dock can
never trip the refusal (it validates 1..5000 before calling add()).

## 6. Tests

New suite `form/nursery_words_bound_test.py`, registered in
`form/regress.py` LIST (LIST total 286 -> 287; the new entry appears
exactly once; the suite exposes `smoke()`).

Direct run at the build head: **11/11 PASS** —
W1 ascii-300 exact; W2 admitted-5000 exact; W3 unicode-300 exact;
W4 boundary 240/241 exact; W5 5,001 refused explicitly with no
in-memory mutation, byte-identical disk content, and unchanged fresh
load; W6 legacy 240-char record loads intact and round-trips through a
later save; W7 fresh-process reload compares every proposal record
exactly.

Neighbor run: every existing suite that imports the Nursery class
directly (47 suites, each run in its own process via its `smoke()`,
sequentially): **47/47 PASS**, including nursery_confirm_race_test,
foundation_acceptance_test, dcc_xvii_test (load contract),
dd44_bounds_explicit_test, and persist_full_roundtrip_test.

Not run by this build (main-session steps, per circuit order): defect
mutants, the x3 regression campaign, exact-head CI.

## 7. Anticipated probes

- Why is label[:80] not repaired in the same circuit? Scope: the
  Q-S1.1 confirmation authorizes ONE bounded circuit (SYS-C29, the
  words cut, census item R1). The label mismatch is recorded in
  section 3 with its evidence for a separate ruling; repairing it here
  would exceed the authorized scope.
- Does the refusal break any existing caller? The dock validates
  1..5000 before calling add(), so dock traffic can never trip the
  refusal. Non-dock callers passing >5,000 chars previously received a
  silently truncated proposal; they now receive an explicit error —
  that behavior change is the circuit's purpose (never silently cut).
- Are legacy files affected? Load imposes no length validation; a
  legacy record loads and round-trips unchanged (pinned by test).

## 8. Questions for the Director

- Q-S2.1: Section 3 classifies label[:80] as a silent-loss defect
  against the dock's admitted 200-char label bound. Should a bounded
  follow-up circuit align it (store to 200, refuse beyond), or is 80
  the intended Nursery-side label contract, in which case the dock's
  200 bound is the side that should move?
- Q-S2.2: reason[:160] has no admitted bound anywhere. Should one be
  declared (with explicit refusal), or is the field's contract
  "short rationale, tail loss acceptable" by design?
