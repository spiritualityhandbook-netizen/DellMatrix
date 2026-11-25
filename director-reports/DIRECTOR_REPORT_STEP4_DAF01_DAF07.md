# DIRECTOR REPORT — Step 4: DAF-01 + DAF-07
Director Certification Audit 2026-10-31, §8 step 4.
Submitted by Uni; HELD for the Director. This report is
evidence submitted for re-ruling, never a certificate.

## Findings addressed
- DAF-01 (P1): "valid typed operands can mutate a different
  key" — 88[Patch](key="a",value="b=NEW") on store
  {'a':'TARGET','a=b':'NEIGHBOR'} changed a=b; 85[Move]
  (source="a",destination="b>c") and 87[Replace](old="a",
  new="b>c") on {'a','a>b'} moved the neighbor into c.
  Source: typed roles flattened to a delimiter string;
  partition_existing_key cannot reconstruct lost boundaries.
- DAF-07 (P2): "51[Select] 54[Query]" raised IndexError;
  88[Patch](key="a",key="b",value="N") silently kept "b".

## Frozen candidate
PR #165. Candidate 53e8ad562a4bf41b7d40e465efdf8c61454d84c9,
tree 2bbfe15da202f727fc91b5df17d417603b658a40, base 76a390d.
Merged as a60bb22d9e7af80389267f97c91806de13330e1e (normal
merge commit; parents 76a390d + 53e8ad5; merge tree
2bbfe15 == candidate tree).
Disclosure: the first candidate (6796591) FAILED Form smoke
CI (run 41205806323) on proof-card drift caused by the new
Dell 55 signature; it was amended to 53e8ad5 and every leg
of evidence was refreshed on the amended candidate.
6796591 was never merged and is claimed nowhere.

## Before (executed on unmodified 76a390d, probe)
Typed Patch: store {'a':'TARGET','a=b':'NEW'} — neighbor
mutated, target untouched. Typed Move / Replace: neighbor
'a>b' moved into 'c'. Typed Set: args silently dropped,
junk store entry 'value'='1' created. Legacy Patch label
'a=b=NEW': neighbor mutated (longest-wins guess). Adjacent
atoms: IndexError from both parse_seed and execute_seed.
Duplicate role: parsed ok, key='b' (first value lost).

## Fix (bounded, canonical owners only)
- Validated, reference-resolved typed roles are carried as
  structured data chain_exec -> execute_core_ii ->
  apply_spectrum / apply_query (`roles` parameter); the
  handlers remain the only executors. 85/87/88/55 resolve
  operands from roles; the flattened lab is kept only for
  trace and the AF-1 ARGUMENT_CONFLICT check.
- Dell 55 (Set) gained a signature derived from query_ops
  code (key required, value optional). The typed set is
  therefore 15, not 14: DELL_PROOF_CARDS.md was regenerated
  with its own renderer (diff confined to the count, Dell
  55's card, and the 85/87/88 failure lines) and the
  d1_proof_cards pin was updated 14 -> 15 with the rationale
  recorded in that suite's docstring.
- Legacy labels: predicate.partition_store_operand (the one
  legacy authority; partition_existing_key delegates) now
  returns an ambiguity verdict. A label with TWO OR MORE
  existing split candidates refuses before mutation:
  ambiguous_move / ambiguous_replace / ambiguous_patch /
  ambiguous_set, store byte-unchanged. Exactly-one-existing
  (AF-2 addressing of delimiter keys) and no-existing
  (creation / miss identities) are byte-preserved. This
  supersedes AF-2 suite item 8 (legacy longest-wins when
  both prefixes exist), which the audit's DAF-01 ruling
  declined as a complete repair; that item now pins the
  refusal plus the typed resolution.
- seed.parse_seed: an atom directly following an atom
  refuses "missing flow operator between atoms" (the former
  IndexError); duplicate named roles refuse
  "duplicate role '<name>'" before the args dict is built.
  Trailing/doubled operators and malformed quotes already
  refused and still do; a valid seed executes immediately
  after a refusal (program stays live).

## After (executed)
All Director counterexamples resolve to exactly the named
key with every non-target store entry byte-equal (suite
asserts full store dicts). Occupied-Replace refusal and
Move overwrite (B20) preserved on the typed path. Typed
Patch is lossless inside a chain. All four ambiguous legacy
shapes refuse with the store byte-equal. Delimiter-bearing
quoted values (incl. '::', '>', '=' in one value) execute.

## Suite, mutants, regressions
- New suite form/step4_operand_transport_test.py: 27/27,
  in the regress LIST (206 -> 207 entries).
- Defect-restoring mutants, each killed, code restored and
  re-verified 27/27 after each: M1 roles transport severed
  -> 20/27; M2 ambiguity verdict off (longest-wins) ->
  23/27; M3 duplicate-role refusal off -> 25/27; M4
  alternation refusal off -> the original IndexError.
- Neighborhoods green: af1 13/13, af2 23/23, step3 23/23,
  dells 84/85/86/87/88 (17/14/13/14/14), recon5 10/10,
  spectrum_closure 57/57, registry spectrum/coreii_b/leaf2
  (48/43/33), flow_executor 28/28, cac_i 177/177,
  ssi_i 130/130, p10 12/12, core_ii_smoke PASS,
  symbiosis_ledger 39/39, proof_cards 6/6.
- Regress x3 on the candidate: fwd 207/207 GREEN (leg log
  lost in a service restart; terminal result observed, and
  the --twice leg's first pass is an independent forward
  run, durable log step4_regress_twice.log); --twice
  207+207 GREEN; --order rev 207/207 GREEN
  (step4_regress_rev.log; logs in the goal hidden_files).

## Exact-head CI (verified complete in a separate step,
before merge)
- Python package run 41206440223: SUCCESS, headSha 53e8ad5.
- Form smoke run 41206440227: SUCCESS, completed
  2026-10-31T13:53:52Z, headSha 53e8ad5.

## Fresh clone
Clone at merge a60bb22: regress 207/207 GREEN, step4 suite
27/27 inside (step4_freshclone_regress.log).

## Limitations
- Legacy ambiguity is judged against the current store —
  the same evidence base AF-2 used. A legacy label naming
  two existing keys has no determinate target and refuses;
  the typed grammar is the documented remedy.
- Direct execute_core_ii callers keep the legacy label
  contract (roles default None); the lossless guarantee
  covers the seed/chain public path (including
  semantic_router and operator_bridge, which route through
  execute_chain).
- limitation_knowledge.py still carries the dated
  2026-10-27 probe line "14 Dells have typed signatures" —
  historical evidence, deliberately not rewritten; a dated
  correction belongs to step 11.
- Third-party scanning remains EVALUATION_UNAVAILABLE.

## Ruling requested (bounded)
Re-rule DAF-01 for Dells 85/87/88/55 typed operand
transport plus the ambiguous-legacy refusal contract, and
DAF-07 for parse alternation and duplicate-role refusal,
at candidate 53e8ad5 / merge a60bb22. Note for the step-14
admission packet: the typed set now numbers 15 (Dell 55
added by this circuit).
