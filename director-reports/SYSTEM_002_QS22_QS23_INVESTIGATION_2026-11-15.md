# SYSTEM-002 — Q-S2.2 + Q-S2.3 INVESTIGATION (2026-11-15)

*Director-authorized bounded investigations (mail 1a1df5bdadd2125e, 2026-11-15). READ-ONLY: no code was changed. All findings verified first-hand against main @ 17ae4ce (clone: g31proof_clone). Every claim carries a file:line citation.*

**Verdicts up front:**

- **Q-S2.2 — `reason[:160]` is a SILENT-LOSS DEFECT**, the same class as the SYS-C29 words defect: the inference dock admits a reason of up to **1,000 chars** at three separate admission points, and `Nursery.add()` silently cuts it to 160 with no error. (This sharpens the SYS-C29 packet's preliminary "silent bound, no admitted contract" classification — first-hand checking found the admitted contract; it lives at the dock, not in the Nursery.)
- **Q-S2.3 — exchange.py:768 `[:240]`: DEFECT** (accidental mirror of the old store cut; fix shape proposed, not implemented).
- **Q-S2.3 — supersession.py:651 `[:240]`: DEFECT** (accidental mirror of the store bounds; additionally diverges from the operation's own authorization hash, which binds the FULL text; fix shape proposed, not implemented).
- Per the Director's instruction: **no end-to-end content-preservation claim is made.** Even with SYS-C29 merged, the exchange-import and supersession paths still cut at their call sites until their own bounded fixes land.

---

## PART 1 — Q-S2.2: CLASSIFY `reason[:160]`

The cut: `form/dell_matrix/nursery.py:216` — `reason=reason[:160]` inside `Nursery.add()` (signature `reason: str = ""` at nursery.py:186; Proposal field at nursery.py:97). No bound is declared, named, or documented at the store; there is no `MAX_*` constant for reason in nursery.py.

### (a) Producers of the `reason` argument (production call sites of `Nursery.add`)

1. **Inference dock, propose path** — `form/dell_matrix/inference_dock.py:1272-1274` passes `reason=chosen_reason`, where `chosen_reason` (inference_dock.py:1265-1268) is the host-supplied reason when given, else a derived provenance string (`f"docked {task} by {subject} via {provider} (model {model})"` — short by construction). The host-supplied reason is the exposure (see (c)).
2. **Inference dock, semantic-verb path** (relate / synthesize / relate_field / comprehend etc.) — `inference_dock.py:1948-1952` passes `reason=chosen_reason`, where `chosen_reason` (inference_dock.py:1921) is the host-supplied reason when given, else `fields["reason"]` — the model-supplied reason from `validate_semantic_output` (called at inference_dock.py:1892).
3. **AutoGrowth** — `form/dell_matrix/auto_growth.py:133-138`: `reason=f"auto:{source}:{judge.get('reason', '')}"[:160]` — the caller pre-cuts to 160 itself. The embedded judge reason is LLM free text (unbounded upstream); this caller already conforms to the store's bound.
4. **Exchange import** — `form/dell_matrix/exchange.py:767-769` passes `reason=reason`, composed at exchange.py:712-716 as a fixed-format f-string (author origin, replication counts, lint labels) and pre-cut `[:160]` by the caller itself.
5. **RingedGrowth** — `form/dell_matrix/ringed_growth.py:548-554`, `:684-690`, `:715-721`: fixed-format numeric f-strings only (e.g. `f"Solstice harm={...:.2f} goals={...:.2f} hs={...:.2f} gcoh={...:.2f}"`, `f"body_pulse vital_missing={organ}"`) — bounded by construction, well under 160.
6. **Supersession** — `form/mandell/supersession.py:649-654`: `reason=f"supersedes {old_id}"[:160]` — `old_id` is a proposal slug; short by construction, caller also pre-cuts.
7. **Core I ops** — `form/mandell/core_i_ops.py:872`: `program.nursery.add(lab)` — no reason passed; default `""`.

(Test-only callers pass short literals and are not producers of record.)

So of the seven production producers, three compose short-by-construction reasons, two pre-cut to 160 themselves — and the two dock paths pass through reasons admitted at up to 1,000 chars.

### (b) Consumers of `Proposal.reason`

- **The human gate at review** — `validate_semantic_output`'s docstring states the contract: the reason is REQUIRED because "the human gate reads the reason at review" (inference_dock.py:565-568). A silently truncated reason is degraded review evidence: the reviewer cannot tell the text was cut.
- **Design loop record** — `form/dell_matrix/design_loop.py:184` surfaces `prop.reason` verbatim in the proposal record.
- **Dock session evidence** — `form/dell_matrix/inference_dock.py:1344` copies `prop.reason` into the session evidence entry.
- **Dock session evidence validator (a consumer that DEPENDS on the 160 bound)** — `form/dell_matrix/dock_session.py:143`: `_is_valid_entry` requires `_bounded_str(e.get("reason"), 160)` for a persisted evidence entry to be valid. This bound mirrors the store cut: any future store repair that admits longer reasons must reconcile this validator in the same circuit, or evidence entries copied from `prop.reason` become invalid.
- No other consumer reads `Proposal.reason`; ranking does not use it (no reference in nursery.py beyond the field definition at :97 and the cut at :216).

### (c) Admitted bounds for reason elsewhere in the codebase

There IS an admitted contract — at the dock, three times over, all at **1,000 chars**:

1. `DockedSession.propose()` rejects a host-supplied reason over 1000: `if len(reason) > 1000: return {"ok": False, "reason": "bad_reason", ...}` (inference_dock.py:1120-1122). The docstring (inference_dock.py:1082-1085) describes the reason as "bounded, protected-screened like the prompt."
2. The semantic-verb entry point does the same for its host reason: "Reason exceeds 1000 chars" → `bad_reason` (inference_dock.py:1637-1642).
3. `validate_semantic_output` REQUIRES a non-empty model reason and admits it up to 1000: `if not isinstance(reason, str) or not reason.strip() or len(reason) > 1000: raise ProviderError(...)` (inference_dock.py:605-608).

Neighboring corroboration: `form/dell_matrix/director_session.py:43` declares `MAX_REASON_CHARS = 1000` — the only named reason constant in the codebase (it governs DirectorSession record entries, and `DirectorSession.directive()` at director_session.py:221 forwards its reason into the dock's `propose()`, where the dock's own 1000 bound applies). The codebase's consistent admitted reason bound is 1000; the Nursery's 160 appears nowhere as an admitted contract.

### (d) Verdict — SILENT-LOSS DEFECT

An admitted value is actually cut today, by construction, on both dock paths:

- A host files a proposal (or a Director directive via director_session.py:221) with a reason of 161–1,000 chars: admitted by `propose()` (inference_dock.py:1120-1122), stored at 160 chars, no error anywhere.
- A docked model returns a semantic judgment whose reason is 161–1,000 chars: admitted by `validate_semantic_output` (inference_dock.py:605-608), flows through inference_dock.py:1921 → :1948, stored at 160 chars. Model judgment reasons are exactly the free-text class that routinely exceeds 160 chars, and the reason is the evidence the human gate reads (inference_dock.py:565-568).

This is the SYS-C29 words pattern one field over: admitted bound 1000 at the admitting layer, silent cut at 160 in the store, no refusal, no marker. Per the Director's terms nothing was removed or changed; classification only. A repair, if authorized, would follow the SYS-C29 shape (store admits to the admitted bound, explicit refusal before mutation beyond it) and must additionally reconcile the dock-session evidence validator's 160 expectation (dock_session.py:143).

---

## PART 2 — Q-S2.3: CALLER-SIDE PRE-CUT INVESTIGATION

### Site 1 — `form/dell_matrix/exchange.py:768`: `words=seed["keep"][:240]`

**(a) What the value is.** `seed["keep"]` is the exported idea's kept text. On export, `build_packet` sets it from the source proposal: for a native proposal, `keep = prop.detail or prop.words` (exchange.py:302); for a re-exported import, the stored original keep verbatim (exchange.py:285). Packet validation admits keep up to **2,000 chars** (`"keep": _str(seed["keep"], 2000, "seed.keep")`, exchange.py:175), and the in-code rationale records that the bound was deliberately raised to 2000, "aligned with the Nursery detail bound, so a 1000 bound made re-export of legitimately-kept ideas fail" (exchange.py:167-171). Lengths over 240 are therefore plainly reachable: any idea whose detail/words exceed 240 chars, a class the 2000 bound was explicitly raised to accommodate.

**(b) Original input contract.** `validate_packet` (exchange.py:155-208) is the strict input contract (exact keys, per-field `_str` bounds, raises `ExchangeError`); `import_packet`'s docstring states the landing contract: "Land a foreign packet as a PENDING proposal in the receiver's nursery" (exchange.py:688-692). No contract anywhere states that the landed proposal's words should be a 240-char prefix of keep.

**(c) Intentional or accidental?** Accidental mirror of the old store cut. Git history: `words=seed["keep"][:240]` is present verbatim in the file's creation commit (e910dc2, "P9: Exchange v1 — seed packets with receipts, chain lint, gated import") — written when `Nursery.add()` itself cut words at 240, so the pre-cut exactly duplicated (and was redundant with) the store's bound. No comment, docstring, or test presents 240 as a summary/preview bound for keep. The file's recorded design intent runs the other way: the full keep is preserved verbatim in the durable seed-payload store at import (`record_seed_payload`, exchange.py:813; rationale comment exchange.py:807-812: "the seed survives re-export byte-exact") and rendered in full as the first detail line (`detail_lines = [f"KEEP: {seed['keep']}"]`, exchange.py:717 — subject to detail's own 2000-char rendering cap at exchange.py:730, which is bound-consistent with the store detail bound).

**(d) Consumers and harm.** The landed proposal's `words` become the confirmed unit's body: the confirm path creates the unit with `words=prop.words` (form/dell_matrix/confirm_lineage.py:423). So an imported idea whose keep is 241–2,000 chars confirms with only its first 240 chars as its live text. Re-export is NOT harmed — `build_packet` reads the verbatim payload store, never the rendered words/detail (exchange.py:285, docstring exchange.py:238-243). No consumer wants exactly 240; full text would help the confirmed unit and harm nothing identified.

**(e) Verdict: DEFECT.** Proposed bounded fix shape (NOT implemented): delete the `[:240]` at exchange.py:768 so `seed["keep"]` passes to `Nursery.add` whole — post-SYS-C29 the store admits words to 5,000 with explicit refusal beyond, and keep is contractually ≤2,000, inside that bound. Failing-first test shape: import a valid packet with a 1,000-char keep; assert the landed proposal's `words` equal the keep exactly, and the confirmed unit carries it in full.

### Site 2 — `form/mandell/supersession.py:651`: `words=words[:240]`

**(a) What the value is.** `words` is the successor revision text — the replacement knowledge itself — supplied by the caller of `supersede_proposal(program, old_id, words, ...)` (supersession.py:502). The production caller is the REPL/Nurture path: `form/mandell/core_i_ops.py:467-486` parses the user's command `supersede <old_id> with <words>` and passes the remainder as free text. No length bound exists anywhere on this path; the only validation is non-emptiness after strip (supersession.py:641-643). Lengths over 240 are trivially reachable — any revision text longer than 240 chars.

**(b) Original input contract.** `supersede_proposal`'s docstring: "Atomic public operation: supersede accepted knowledge with a new revision" (supersession.py:507) — no length contract stated. The module docstring (supersession.py:1-22) defines the semantics (successor becomes the active revision; history preserved) with no summary/preview notion. Critically, the operation's authorization binds the FULL text: the acceptance-policy binding hash is computed as `_succ_data_hash = canonical_hash({"label": _eff_label, "words": words or ""})` over the untruncated words (supersession.py:581).

**(c) Intentional or accidental?** Accidental mirror of the store bounds. Git history: `words=words[:240]` is present in the file's creation commit (5139ac4, "DCC-XVI: Versioned Knowledge Supersession + Revision Lifecycle"). It sits in a cluster of three call-site mirrors of the Nursery's then-current store bounds — label `[:80]` (supersession.py:648), words `[:240]` (:651), reason `[:160]` (:654) — the signature of copying the store's storage cuts at the call site, not of an independent summary contract. No consumer wants exactly 240: the successor is confirmed and becomes the active revision, whose words ARE the revised knowledge. Worse, the cut contradicts the operation's own authorization: the approval hash covers the full words (supersession.py:581) while the stored successor carries only `words[:240]` — for any input over 240 chars (or a label over 80), the approved content and the stored content silently diverge. Unlike exchange, there is no second copy: receipts and the intent journal carry ids, not text, so the cut tail is lost entirely.

**(d) Consumers and harm.** The confirm/promote phase mints the successor unit from `prop.words` (form/dell_matrix/confirm_lineage.py:423); the truncated text becomes the active revision's body, superseding the predecessor in contextual routing (supersession.py:5-7). The consumer is harmed directly by the cut and helped by full text; nothing identified wants a 240-char prefix.

**(e) Verdict: DEFECT.** Proposed bounded fix shape (NOT implemented): remove the `[:240]` pre-cut at supersession.py:651 and pass the validated words whole, relying on the repaired Nursery store bound (post-SYS-C29: admit to 5,000, explicit refusal beyond, before mutation). The sibling mirrors at :648 (label — the Q-S2.1 circuit's field) and :654 (reason — Part 1 of this report) should be treated by their own classifications, not swept into this fix. Failing-first test shape: supersede under a bound approval with a 300-char successor text; assert the successor's stored words equal the approved text exactly (this also pins the authorization-hash/stored-content divergence).

---

## SCOPE NOTE

Both Part 2 verdicts rest on the repaired store bound from SYS-C29 (PR #429: words admitted in full to 5,000, explicit refusal beyond, before any mutation). Until the two bounded fixes above are authorized and landed, the correct end-to-end statement is: **the Nursery store no longer truncates (SYS-C29), but the exchange-import path and the supersession path still pre-cut words at 240 at their call sites.** No stronger preservation claim is made.

*Investigation by Uni (subagent lane), 2026-11-15. Read-only; no commit, no push.*
