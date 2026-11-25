# DIRECTOR REPORT — DD-31: Sanitize Copula Redaction Leak (2026-11-09)

**Circuit:** DD-31 (Dells tour, Dell 41 Sanitize) — Ace-authorized
FIX-FIRST (Ace directive 2026-11-09, voice session: "Yes, fix
that"). This merge is labeled Ace-authorized, never
Director-certified; scoped certification is requested below
(Q-DD31.1).

**Base:** a5919c4 (main, PR #341 merge). **Branch:**
uni/dd31-sanitize-copula.

## 1. The defect (verified live before repair)

Dell 41 Sanitize's one redaction authority,
`form/mandell/redaction.py`, matched:

```
(?i)(password|secret|token|api[_-]?key|bearer)\s*[:=]?\s*\S+
```

In the natural-English copula form the token consumed as the
"secret" is the word **is**, and the real value survives.
Live exhibit (REPL, owner TOUR41A, synthetic value only):

```
41[Sanitize] :: my password is swordfish99 ...
-> Sanitize out: my password=[REDACTED] swordfish99 ...
```

The `password=X` and `password: X` forms redacted correctly.
This is the Dell whose entire contract is keeping secret-shaped
values off the program's surfaces (DAF-02/B5 lineage): a secret
surviving inside Sanitize's own cleaned output is its core
failure, however narrow the phrasing.

## 2. Failing-first evidence

New suite `form/dd31_sanitize_copula_test.py` (registered in
`form/regress.py` LIST after step3c; canonical count 262 -> 263):

- **At base: 12/21.** All seven copula checks fail with the
  leak exhibit verbatim (canary visible after `[REDACTED]`),
  and the canary is present in the Dell 41 leaf `result` and
  `messages` surfaces.
- The nine non-copula checks (existing `=` / `:` / bare forms,
  12+ digit rule, 10-digit exclusion, ordinary text, "is"
  without a keyword) already pass at base — the defect class is
  exactly the copula, nothing wider.

## 3. The repair (one authority, one pattern)

`form/mandell/redaction.py` only. The secret pattern now
consumes an optional copula between keyword/separator and
value:

```
(?i)(password|secret|token|api[_-]?key|bearer)
\s*[:=]?\s*(?:is\s*[:=]?\s*)?\S+
```

Semantics otherwise identical: same keyword set, same
`keyword=[REDACTED]` replacement, same 12+ digit rule, no
digests substituted (DAF-02 law), and `sanitize_evidence`
remains evidence-only — execution operands are untouched
(step3c's contract is a neighbour check below, not re-argued
here).

Covered copula forms: `password is X`, `secret is X`,
`token is X`, `api_key is X`, `bearer is X`, `password is: X`,
case-insensitive (`Password Is X`).

## 4. Results

- New suite: **21/21** after the fix.
- Neighbours: step3b_sanitize_chain **21/21**,
  step3c_sanitize_state **24/24**, step3_security **23/23**.
- **Mutant:** the copula group narrowed back out by inverse
  edit (real work committed first; no `git checkout --`):
  suite falls to **12/21**, the exact base profile. Restored
  by inverse edit; worktree verified clean against the fix
  commit and the suite re-verified 21/21.
- **Full regression:** one full `form/regress.py` run at the
  fix commit via a launcher resetting SIGINT/SIGQUIT to SIG_DFL
  inside the chain process (TOOLS.md background-shell signal
  law): **REGRESS: 263/263 -> GREEN; REGRESS FINAL: GREEN
  (order=fwd)**, terminal lines read in full from the durable
  log (`dd31_logs/regress_fwd.log`, goal hidden_files). The new
  suite ran inside the chain: `form.dd31_sanitize_copula_test
  rc=0 last=21/21`.

## 5. Also recorded in this PR (per the Director's instruction)

**(a) Proposal B certification acceptance.** The Director's
ruling of 2026-11-09 09:43 CST accepts the Q-LD.5 scoped
certification of Dock Proposal B (register item G-12), within
the scope exactly as built: sanitized bounded provider-failure
categories with secret-bearing canary tests; exactly one
complete fenced JSON object accepted under strict schema with
extra prose/objects rejected; the response format stated in
the prompt; session-only sanitized response visibility with
disclosed truncation; durable storage limited to digest/parsed
fields, no persistent raw-response storage. No more, no less.
G-12 is an extension item: **strict completion stays 19/72.**
The register's G-12 row is updated in this PR.

**(b) §32 receipt disclosure for PR #340.** Uni's pre-merge
§32 freshness check for PR #340 **was performed minutes before
the merge** (2026-11-09T15:28:25Z; newest Director mail at that
moment was the folded 07:39 CST ruling; no contrary ruling
existed), but it left **no independently retrievable
timestamped receipt**. Per the Director's 2026-11-09 09:43
instruction, that fact is written into the PR #340 merge record
in INDEX.md in this PR, exactly as it happened — the check ran;
the receipt does not exist; nothing is reconstructed or dressed
up. No merge in this circuit is affected: this PR is submitted
unmerged for the Director's review.

## Anticipated probes

1. **"Does the copula branch over-redact ordinary prose?"**
   The branch can only trigger immediately after one of the
   five secret keywords, where the base pattern already
   redacted the following token. Worst case the redacted token
   shifts by one word inside an already-redacted span. The
   suite pins "is" without a keyword and keyword-free prose as
   byte-identical.
2. **"What about 'password is set to X' / possessives /
   quoted values?"** Out of the proven defect class; the suite
   makes no claim for them. Q-DD31.2 asks whether the Director
   wants a widening proposal or holds the bounded class.
3. **"Is sanitize_evidence still evidence-only?"** Yes —
   the diff touches only `_SECRET_RE` in redaction.py;
   step3c (executable state keeps real values) passes 24/24
   unmodified.
4. **"Why is a records item (Proposal B certification) riding
   a code PR?"** The Director's 09:43 ruling instructed the
   certification be recorded inside the next real build's
   paperwork rather than its own PR; DD-31 is that build.

## Questions for the Director

- **Q-DD31.1** — Scoped certification is requested for the
  DD-31 fix as bounded above (copula class only, one authority,
  evidence as in §4). Accept, hold, or correction-required?
- **Q-DD31.2** — Should the redaction grammar class widen
  beyond the copula (e.g. "is set to", possessive and quoted
  value forms) under a separate bounded proposal, or is the
  copula class the correct bound for the DAF-02 authority?
- **Q-DD31.3** — Confirm the §32 disclosure wording in §5(b)
  and the INDEX merge-record supplement state the PR #340
  facts as the Director requires them recorded.

*Uni Ω — evidence first; the merge gate for this PR is the
Director's review, not Uni's.*
