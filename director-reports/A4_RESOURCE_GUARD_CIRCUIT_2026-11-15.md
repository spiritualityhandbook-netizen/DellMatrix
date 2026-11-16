# A4 RESOURCE GUARD CIRCUIT — pre-decomposition guard for the LM-4 toll booth

*Circuit: LM-4 A4 residual (Director fix-first order, mail 1a1d8591a6a1e256,
2026-11-13). Grounding: hidden_files/a4_resource_guard_ground_2026-11-14_1643.md;
design proof: hidden_files/a4_chunking_equivalence_2026-11-14_1743.md.
Base: origin/main 17ae4ce86743d9c5ff848a1b48111119d9bf9a32. Branch:
uni/a4-resource-guard (local commit only at publication of this packet;
push / PR / mutants / ×3 campaign / merge are main-session steps).
Evidence labels: INTEGRATION (module path + scripted FakeProvider through
the public dock()/propose() path). No wall-clock claims anywhere below:
earliness is measured in composed tokens.*

## 1. The problem

In `InferenceDock.propose()` (form/dell_matrix/inference_dock.py) the raw
prompt was checked only against the caller's bound (default
`DEFAULT_MAX_PROMPT_CHARS = 1,000,000`), then `_lm4_text_block()` decomposed
the FULL prompt, and only afterwards did the assembled-length screen refuse.
Decomposition expands ordinary text ~9.1×, linearly. The Gate-2 class —
214,200 raw chars → ~2.2M assembled — paid the full decomposition cost
(~21–23 s, ~98.9 MB in the original measurement) before being refused, with
0 provider calls. Exposure was host CPU/memory only; the guard always
preceded any provider call and any persistence. The Director's constraints:
no arbitrary cap, no silent weakening of the elasticity doctrine, valid
content never refused, explicit smaller caller bounds sovereign (Q-LM4.5).

## 2. The design applied (the proven one, unchanged)

Chunk-pooled decomposition with early abort, exactly as proven feasible in
the 2026-11-14 chunking-equivalence record:

- The token stream is composed in chunks; the per-token records are pooled.
- The sentence aggregates (spine, dell roll-up, ambiguity, the two honesty
  scores, lineage class) are recomputed ONCE from the pooled records and the
  block is rendered ONCE — so an admitted call's block is byte-identical to
  the legacy whole-text path.
- While pooling, the pooled tokens' gloss + diagnostic line lengths
  accumulate (len + 1 separator each) as a running LOWER bound on the final
  block length. The finished block contains exactly those lines plus the
  summary line, the spine line and the remaining tokens' lines — all of
  non-negative length — so the moment `len(prompt) + len(header) + running`
  exceeds the caller's bound, the assembled prompt is GUARANTEED to exceed
  it too, and composition aborts. The remaining tokens are never composed.
- `propose()` converts the abort into the SAME refusal the final
  assembled-length screen returns: `{"ok": False, "reason":
  "prompt_too_large", "detail": "Prompt with its LM-4 decomposition exceeds
  the caller's bound; refused rather than sent undecomposed."}` — same keys,
  same reason, same detail string (suite G5 pins dict equality).
- The final assembled-length screen is untouched and still decides every
  admitted call (pin d).

One structural move keeps a single authority for the aggregate semantics:
the aggregate block of `compose_sentence` (form/mandell/morpheme.py) was
factored VERBATIM into `_sentence_from_token_records(raw, tokens)`;
`compose_sentence` now tokenizes and delegates. The pooled path recomputes
through that same code — no second implementation of the aggregates exists.

`_lm4_text_block` itself is preserved with identical behavior (it is the
legacy whole-text reference, and two suites call it directly:
pp4_bimo_dock_test's timing checks and p4_sd1_test). `propose()` is its
only production caller and now calls `_lm4_text_block_bounded`.

## 3. Chunking parameters

- **Chunk size: 512 tokens** (`_LM4_CHUNK_TOKENS` in inference_dock.py).
  Why: the chunk bounds the abort overshoot. At the measured ~9.1×
  expansion, one 512-token chunk adds at most ~30K gloss chars past the
  bound before the abort can fire — ~3% of the default bound — while the
  per-chunk `compose_sentence` overhead stays at ~1 call per 512 tokens
  (84 calls at the largest admissible prompt) instead of a call per token.
  The feasibility simulation used 32-token chunks; 512 keeps the same
  soundness with materially less call overhead, and the suite's Gate-2
  check still aborts below 60% of the token stream (observed ≈40%).
- **Accounting:** per pooled token, its gloss line length + 1; per
  disagreeing pooled token, its diagnostic line length + 1. The summary
  line is excluded (it is the partial render's last line and belongs to
  the un-counted tail). The spine line is likewise un-counted: the gap
  between the running bound and the true assembled length is exactly
  summary + spine + separators (measured on a 5,100-token ordinary text:
  gap 5,773 = summary 63 + spine 5,698 + 1 separator). A caller bound
  falling inside that gap cannot trigger the abort — the input pays full
  decomposition and the FINAL screen refuses it (suite G4 pins this).
  That is the designed trade: the abort never refuses valid content;
  maximal earliness yields to soundness at the gap.
- **Abort condition:** `len(text) + len("\n\n[decomposition]\n") + running
  > bound`, checked after each chunk, where `bound` is the session's own
  `_max_prompt_chars` — the caller's actual bound, never a hard-coded
  default (suite G6 pins a smaller explicit bound).

## 4. Changed paths

- `form/dell_matrix/inference_dock.py` — `_lm4_block_from_sentence` (the
  single render, factored out of `_lm4_text_block`); `_LM4_DECOMP_HEADER`;
  `_LM4_CHUNK_TOKENS = 512`; `_LM4AssembledTooLarge`; `_lm4_text_block_bounded`;
  `propose()` calls the bounded path and maps the abort to the
  prompt_too_large refusal.
- `form/mandell/morpheme.py` — aggregate block of `compose_sentence`
  factored verbatim into `_sentence_from_token_records` (no behavior
  change; morpheme smoke 6/6).
- `form/lm4_resource_guard_test.py` — NEW suite (8 checks).
- `form/regress.py` — LIST + 1 entry (`form.lm4_resource_guard_test:smoke`,
  verified exactly once; LIST total 287).

## 5. Test results

New suite `form.lm4_resource_guard_test` — **8/8 PASS** (~32 s on this VM):

- A1: bounded == legacy block, byte-identical, across 11 text classes
  (ordinary, caps, unicode, punctuation, numbers, whitespace-heavy, short
  words, empty, single token, and 600-/1500-token streams crossing the
  512- and 1024-token chunk boundaries).
- G1 (pin a + c): Gate-2 class — raw 214,200 chars at the default bound:
  refused `prompt_too_large` with the final screen's detail, provider
  calls == 0, tokens composed < 60% of the stream (compose-work counter,
  not timing), at least one full chunk composed.
- G2 (pin a + c): raw 20,000 vs caller bound 100,000 (legacy assembled
  ~202K): early-abort refusal, 0 calls, tokens composed < total; the legacy
  assembled length proves the final screen would refuse the same input.
- G3 (pin b + d): valid content at exactly the bound (assembled == bound):
  admitted, 1 provider call, outbound decomposition segment byte-identical
  to the legacy whole-text block.
- G4 (pin d): bound = assembled − 1 (inside the summary/spine gap): the
  abort cannot fire, the FULL token stream is composed (counter == total),
  and the FINAL screen refuses — 0 provider calls.
- G5: early-abort refusal dict == final-screen refusal dict (exact
  equality of ok/reason/detail).
- G6: explicit smaller caller bound (10,000) is sovereign — refusal after
  the first chunk against the caller's bound, 0 calls.
- G7: tollbooth baseline behavior — an ordinary docked propose is admitted
  and the outbound prompt carries the [decomposition] block with gloss
  lines and the honesty summary line.

Pre-suite differential probe (main-session build lane, same head):
byte-identity held for all classes and chunk crossings; the abort/admit
sweep over bounds {A−1, A, A+1, A/2, 100,000, 50,000} was sound in every
case (abort ⇒ assembled > bound; admit ⇒ byte-identical block).

Neighbors — each in its own process via `smoke()`, sequential:
- `form.lm4_tollbooth_test`: **26/26 PASS** (baseline held).
- All 17 further suites importing inference_dock (plus lm1_import as a
  compose_sentence consumer): **smoke() True, 17/17** — pp3_unknowns,
  pp4_bimo_dock, dock_proposal_b, dock_wall, p4_sd1, p5_sd2, p6_sd3,
  p7_sd4, p8_sd5, r62_docking, r64_multi_intelligence, r72_studio,
  repair_r1, track_c_dock_verbs, snapshot_retrieval, snapshot_revalidation,
  lm1_import.

## 6. Where the proven design met the code

No part of the proven design failed on contact. Two notes:

- The feasibility record's probe recomputed aggregates in probe code; the
  production shape factors the aggregates out of `compose_sentence`
  instead, so the pooled path and the whole-text path share one
  implementation (§2). Same semantics, no drift surface.
- The running bound deliberately excludes the spine line. For
  spine-heavy text the gap is large (5,773 chars on the measured sample),
  so a bound inside the gap pays full decomposition before the final
  screen refuses (G4). Cost remains bounded by the bound for the
  token-line mass, which is the dominant term; soundness is unaffected.

## 7. Anticipated probes

- *"Show an input the abort refuses but the final screen would admit."*
  None can exist: the running total is a proven lower bound on the final
  block length (§3), so abort ⇒ assembled > bound. G2/G4 bracket the
  boundary from both sides.
- *"A bound inside the gap makes the guard useless."* No: the guard's
  cost bound applies to the token-line mass (~9.1× expansion); the gap is
  only the summary + spine tail. Gate-2 still aborts at ≈40% of tokens.
- *"Chunk boundaries split a token's context."* Token records are
  context-free (compose is per-token; the only cross-token products are
  the aggregates, recomputed once). A1's battery includes punctuation,
  whitespace-heavy and unicode classes and two chunk crossings.
- *"The abort changes the refusal."* G5: the dicts are exactly equal.
- *"What about the _verb paths / `_lm4_field_block`?"* Untouched: those
  decompose snapshot fields (label/words of field entries), which are
  field-sized, not caller-prompt-sized; no exposure was grounded there.
- *"A caller bound above the default?"* `dock()` validates
  `max_prompt_chars` ≤ the 1,000,000 ceiling; the guard keys off the
  session's actual bound in all cases.

## 8. Questions for the Director

- Q-A4.1: Chunk size 512 tokens — accept this overshoot/overhead trade,
  or direct a different one?
- Q-A4.2: Credit shape: A4 closes the LM-4 pre-decomposition guard
  residual disclosed at #416 — which register row carries it, and is the
  scope "propose() path only" (the _verb field blocks were never exposed)?
- Q-A4.3: Should a later circuit give the snapshot-field decomposition
  (`_lm4_field_block`) the same bounded treatment as defense in depth, or
  is the field-size bound sufficient by construction?

## 9. Limitations

- Earliness is proven in composed tokens on this VM; absolute times from
  the grounding record are the Gate-2 machine's, not re-measured here.
- The guard covers the `propose()` free-text path — the only caller of
  `_lm4_text_block` and the only path where caller-sized text is
  decomposed. No claim is made for any other path.
- Mutants, the ×3 campaign, exact-head CI and the merge are main-session
  steps and have NOT been run by this lane.
