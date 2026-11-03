# SWAT PRE-MORTEM — D1-TYPED-52-53 (Director's-eye, before implementation)

## Mechanism (verified in tree at base b6dd46b)

- chain_exec._run_atom: typed args are validated/lowered ONLY if
  signatures.has_signature(n). No signature -> atom.args silently
  ignored; the atom executes on the legacy payload with ok=True.
- Registry form/mandell/signatures.py holds 15 Dells:
  [8,51,54,55,56,57,58,67,68,69,84,85,86,87,88]. 52/53 absent.
- Filter (query_ops n==52): consumes the WHOLE lab via pred_fn;
  empty lab = identity. Whole-lab role => lowering is lossless.
- Scope (core_ii_exec n==53): name = lab or "plane"; "plane" or an
  existing group switches st.scope; anything else refuses
  scope_unknown:{name} (fail-closed, R1). Whole-lab role => lossless.
- Dell 55 precedent (DAF-01): delimiter consumer needed roles_arg
  because its legacy path re-splits the lab. 52/53 never re-split;
  transport = signature registration + lower_args_to_lab branch,
  zero handler changes. (If a probe shows any re-split, this
  assumption is falsified and roles transport becomes required.)
- Conflict law (existing gate, all typed Dells): typed args lower
  to a lab; a non-empty legacy label that differs refuses with
  ARGUMENT_CONFLICT BEFORE mutation; equal label proceeds.
  Duplicate roles refuse at parse (DAF-07). Unknown roles refuse
  via sig.validate -> UNKNOWN_ROLE, zero mutation.
- Role types are "string"; the seed parser produces only strings,
  so no non-string value can arrive via seed text. Refusal classes
  for this circuit: UNKNOWN_ROLE, ARGUMENT_CONFLICT, parse-level
  duplicate-role refusal, and the handler's own scope_unknown.

## How the Director will try to break it (anticipated probes)

1. Typed Filter matching nothing -> selection must empty honestly
   (result cell matched=False), not silently keep the selection.
2. Typed Scope to a missing group -> scope_unknown refusal AND
   st.scope unchanged; in a chain the atom receipt must read
   ok=False honestly (no invented chain-stop semantics).
3. Typed+legacy conflict in both Dells, both directions; equal
   typed/legacy values must proceed (no false conflict).
4. Bogus role (52[Filter](bogus="x")) -> refusal, ZERO mutation:
   selection and scope byte-identical before/after.
5. Empty typed values: predicate="" = legacy identity filter;
   name="" = legacy default "plane". No new semantics.
6. Delimiters inside typed values: spaces, "=", ":" ride whole
   through lowering exactly as the legacy label does (same lab,
   same handler -> sameness is the proof).
7. Legacy seeds byte-identical behavior (messages, state, cells)
   for Filter/Scope with and without labels, incl. Scope's
   fail-closed refusal on the legacy path.
8. Count integrity: EVERY live pin found (step11 test incl. its
   limitation-correction coupling, d1_proof_cards pin); historical
   fields (evidence line, limitation field, 2026-11-01 correction
   text, Step 11 report text) byte-identical in git diff — the
   2026-11-03 correction is an APPEND only.
9. Why DIRECTOR_REPORT_STEP14_ADMISSION.md still says 15: it is a
   frozen dated admission record (historical evidence), not live
   documentation; the Director ordered Step 11 versioning only.
10. Reference resolution (last_result / store:) now applies to
    52/53 typed values via the shared gate — inherited sibling
    behavior, not new machinery; packet states it, suite does not
    need to re-prove the C2 authority.
11. Direct execute_core_ii callers (roles=None) and the GUI server
    path: unchanged code, inherited behavior only.

## Failure-class search (bounded)

The gate drops typed args for EVERY untyped Dell identically.
That is the class; this circuit's authorized scope is 52/53 only.
The packet records the class and does not expand scope.

## Mutant plan (after real work committed)

- M1: remove the 52 registration -> suite typed-Filter checks RED,
  legacy checks GREEN.
- M2: remove the 53 registration -> suite typed-Scope checks RED.
- M3: remove the 52 lowering branch (registration present) ->
  typed Filter raises/never lowers -> RED (proves lowering is
  load-bearing, not decorative).
Revert by inverse edit; verify diff clean after each.
