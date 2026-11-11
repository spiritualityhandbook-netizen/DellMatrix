# C8 EmbedBind — Director Report (2026-11-11)

Circuit: plan §14.3 C8 / MWL 153. Branch `uni/c8-embedbind`, head
925b28465ae185af9a6c30777de9d1cca13d92f6. Records-lane note: this
PR carries this report file but NO INDEX.md row — the INDEX row
rides the post-#348/#345 regeneration PR, per the INDEX freeze
commitment on record (INDEX is the sole conflict surface for the
two held PRs; this PR must not re-create it).

## 1. Capability delta

BEFORE: Dell 47 [Embed] refused unconditionally
(`embed_unavailable`, representation "none") — no binding existed
for it to inspect, and no embedding transport existed anywhere in
form/ or gui/.

AFTER: a host can establish an embedding-provider binding on a
Program (`bind_embedder`, the dock() precedent: hosts make
bindings, atoms use them). The binding is granted only after a
probe embed succeeds — the probe IS the §12.36 entitlement test.
Bound, `47[Embed]:: <text>` embeds the segment-label text through
the provider transport and the receipt (`program.last_core_i`)
reports the ACTUAL provider, model, vector space
("<provider>:<model>:<dim>"), dimension, and the vector itself.

Acceptance sentence (§14.3 C8): "EmbedBind reports
provider/model/vector-space identity (a vector database is not an
embedding model)." — satisfied by construction and by test.

## 2. Mechanism

- `form/llm/bridge.py` — `LLMBridge.embed()` extends the existing
  bridge authority (no second transport authority). Endpoints:
  gemini/aistudio `:embedContent` (default model env
  GEMINI_EMBED_MODEL or "gemini-embedding-001", key via the same
  _env chain as _gemini); ollama `/api/embeddings` (default
  "nomic-embed-text"); grok/claude/copilot return the named error
  `embed_not_supported_for_provider` — never a substitute vector.
  A deterministic `fake` embedder (sha256-derived, dim 16, model
  "fake-embed-16") mirrors the dock's FakeProvider precedent and is
  labeled in every receipt it produces.
- `form/dell_matrix/embed_bind.py` — `bind_embedder` (probe then
  bind; failure leaves the program unbound), `unbind_embedder`,
  `embed_text`. The binding is RUNTIME-ONLY Program state
  (`program.embed_binding`), deliberately never persisted: a
  restart cannot resurrect a dead provider as bound (the DD-37
  roster liveness rule applied to bindings).
- `form/mandell/core_i_ops.py` — Dell 47 branch: unbound refusal
  byte-identical to pre-circuit behavior; bound + no text refuses
  `embed_no_text`; transport failure at execute time is reported
  by its name with representation "none" (§31.2: no silent
  downgrade — in particular the pedagogy bag
  `inspire_pack.embed_bag`, a live self-labeled educational stub
  behind Program.attend(), is never served as a provider
  embedding).

Provider-agnostic per Ace's ruling (MWL 178): whichever provider
the host binds is the embedder; Gemini is today's expected
binding. §14.8's "provider selection unresolved" text is
superseded by that ruling (record debt only).

Operand semantics were undefined in the record; this build
defines them: the operand is the segment's `::` label text
(the Seed label channel), stated here for review.

## 3. Evidence

- Failing-first: `form/embedbind_test.py` written before the
  implementation; against unmodified code it fails at import
  (no `form.dell_matrix.embed_bind` module exists).
- Suite: 16/16 — unbound identity (bare + labeled + receipt
  shape), bind probe, bound embed, receipt identity,
  vector-space = provider:model:len(vector), determinism,
  distinct texts → distinct vectors, bound-no-text refusal,
  unbind restores refusal, entitlement failure (gemini with the
  API-key env cleared does not bind and stays unbound), no-bag
  (receipt vector ≠ inspire bag vector), per-program isolation.
  INTEGRATION label (deterministic fake transport).
- Neighbor suites pinning the old unconditional refusal pass
  UNCHANGED: core_i_maturity, d1_proof_cards, d1_registry_leaf4,
  p1_dedup, r2_semantic_honesty — all True (they run on unbound
  programs, which is exactly the preserved case).
- Mutants (real work committed first; reverts by inverse edit;
  one revert via git checkout of the COMMITTED tree state):
  A — binding ignored in core_i_ops → 5 bound-path checks red.
  B — fake embedder constant vector → distinctness check red.
  Both mutants killed; restored tree green.
- Regression: full `form/regress.py` ×3 from the main session
  (fwd / --twice / --order rev, SIGINT/SIGQUIT-reset launcher,
  logs under the goal's hidden_files/embedbind/logs/): all three
  legs 269/269, REGRESS FINAL GREEN, exit 0. LIST diff vs main:
  exactly +form.embedbind_test:smoke, none missing.
- Exact-head CI: this PR's checks (evidence class
  EXACT_HEAD_CI) — see PR.

## 4. Limitations / UNKNOWN

- Live Gemini embedding entitlement from this environment:
  UNKNOWN. No API key is present in the bridge's environment
  here, and no credential was extracted to create one. The
  entitlement machinery is proven by the no-key refusal and the
  probe design; a live probe requires the key in the host env.
- No vector storage, no similarity consumer, no ranking/search
  wiring — C5 scope, separate authorization. This circuit claims
  bind + compute + receipt only.
- The ollama embedding endpoint is implemented against the
  documented API shape but untested against a live host here
  (EVALUATION_UNAVAILABLE for that transport).

## 5. Anticipated probes

- "Does an unbound program's 47 receipt change in any byte?" No —
  the unbound branch is the pre-circuit code path verbatim, and
  five pre-existing suites pin it.
- "Can a chain self-bind?" No — bind_embedder is a host function;
  no atom invokes it. Atoms consume bindings only.
- "Does the binding leak across programs or persist?" No —
  per-instance attribute, never serialized; isolation check in
  the suite; persist.py untouched.
- "Is `fake` confusable with a real provider?" No — the provider
  string "fake" and model "fake-embed-16" appear verbatim in the
  binding, the receipt, and the vector space.

## 6. Questions for the Director

1. Operand semantics (segment label text as the embed operand) —
   confirm or redirect before C5 builds consumers on it.
2. Should `bind_embedder` also be exposed through the REPL as a
   host command in a follow-up circuit, or does it stay a
   library-level host API until the dock circuit?

Disposition requested: scoped review of the C8 contract above;
MWL 153 lifecycle on merge: BUILT → MERGED_UNVERIFIED → COMPLETE
only on authority-confirmed closure.
