# DIRECTOR REPORT — DD-45: Chain Authority Swallowed Failed Seeds (2026-11-09)

**Circuit:** DD-45 (Dells tour §12.57/§12.57a, Dells 51/52/66) —
Ace-authorized FIX-FIRST (Ace directive 2026-11-09, voice
session: "Absolutely unacceptable. Go ahead and get that
fixed."). This merge is labeled Ace-authorized, never
Director-certified; scoped certification is requested below
(Q-DD45.1).

**Base:** 7399ee504cfc215f74a67f537be9717ec03a8353 (main, PR #343
merge). **Branch:** uni/dd45-select-chain-erasure. **Fix commit:**
531601e (code + suite + registration).

## 1. The defect (verified live before repair)

The Dells tour (2026-11-09) reported: any chain containing
Dell 51 (Select) or 52 (Filter) loses all Core I Create (08)
work made in that same chain, in any atom position, while the
chain reports ok=True (§12.57a). The circuit's mechanism trace
**corrects that framing** — no atom ever ran, and no state was
ever rolled back:

1. `parse_seed` REFUSES the tour's probe seeds outright
   (ok=False, atoms=[]). The tour's canonical per-atom grammar
   ends segments with `:: <label>`; a trailing `::` with an
   EMPTY label — `08[Create] :: Alpha > 51[Select] :: ` — fails
   the whole parse with error `too many flow operators`
   (seed.py: the empty-segment-label arm). The refusal is NOT
   Select/Filter-specific: it fires for ANY Dell whose segment
   carries a trailing empty label (Query 54 fails identically),
   and the tour's Dell-by-Dell map (51/52 "erase"; 54/56/58
   "preserve") was an artifact of which probe strings happened
   to carry trailing empty labels. Other parse refusals share
   the shape: unknown Dell, duplicate typed role, atoms with no
   flow operator between them.
2. The FRONT DOOR (`executor.execute_seed`, executor.py:36-41)
   checks `seed.ok` first and refuses honestly:
   `{"ok": False, "error": <parse error>}`.
3. The CHAIN AUTHORITY (`chain_exec.execute_chain`) never
   checked `seed.ok`. Handed a refused seed directly (the tour
   probes called it directly; so do other non-front-door
   surfaces), it executed the empty atom list and returned
   **ok=True, atom_results=[], zero executed atoms** — a
   success receipt covering nothing. The caller's fresh program
   still held only its starter 'welcome' unit, which read as
   "creates erased / plane rolled back." The work was never
   created; the receipt lied about it. That is the defect:
   **a success receipt over a refused parse**, in the one
   execution authority the front door itself delegates to.

With VALID grammar, same-chain composition was always sound
(verified at base and pinned in the suite): Select sees
same-chain creates in both select-all and predicate forms,
ForEach runs its body once per selected member, and creates
survive every one of the 21 QUERY_DELLS atoms placed after
them.

## 2. Failing-first evidence

New suite `form/dd45_chain_parse_refusal_test.py` (registered
in `form/regress.py` LIST after dd31; canonical count
263 -> 264):

- **At base: 99/113.** Exactly 14 failures — for each of 7
  parse-refusal shapes, the two chain-authority checks:
  `chain_refuses` (execute_chain returned ok=True) and
  `error_names_parse_failure` (chain error '' vs the named
  parse error). Every other check already passed at base:
  parse-refusal preconditions, zero atoms executed, state
  untouched, the front-door control refusing identically, the
  full 21-Dell blast radius, Select/ForEach composition, and
  receipt honesty for genuinely-failing and all-good chains.
  The defect class is exactly the missing refusal, nothing
  wider.
- Checks: A-group (7 refusal shapes × chain refusal, named
  error, zero execution, untouched state, front-door control);
  B-group (every QUERY_DELLS atom 51-59/67-79 after two
  same-chain creates: creates survive, every atom receipted;
  Select select-all/predicate visibility; Select->ForEach
  per-member body runs); C-group (a chain with a genuinely
  failing atom reports ok=False AND keeps its executed work;
  an all-good chain's ok=True is backed by all-ok receipts and
  the created units present).

## 3. The repair (one authority, fail-closed)

`form/mandell/chain_exec.py` only — a guard at the head of
`execute_chain`, mirroring the front door's existing refusal:
when `seed.ok` is False, the chain executes ZERO atoms, mutates
ZERO state, records the refusal as an encountered unknown
(PP3 parity with the executor's parse note), and returns the
standard chain result shape with `ok=False` and
`error = <the parse error, named>`. Semantics of every valid
seed are untouched — the guard is unreachable for ok seeds
(parse failures always carry atoms=[], so no execution path
changes for any seed that parses).

Sibling search (same failure class — an execution surface
swallowing a failed parse): `executor.execute_seed` checks
ok (line 36); `bridge.py` checks ok at both parse sites;
`canonical.seed_graph` checks ok; `activation.semantic_hash`
does not execute (ok is hashed as data). `execute_chain` was
the sole swallowing execution surface; the class is closed in
the neighborhood searched.

NOT changed, deliberately:
- `parse_seed` grammar: the trailing-empty-label refusal
  stands (it is a refusal with a named error, now surfaced by
  every execution surface). Whether that shape should instead
  be LEGAL grammar is Q-DD45.2 — a grammar decision, not
  smuggled into a defect fix.
- The refusal's error text (`too many flow operators`,
  seed.py's empty-segment-label arm) misdescribes the cause;
  it is pinned by seed_grammar_stress_test P1 through the
  front door and is now surfaced verbatim by the chain too.
  Renaming it is a separate bounded change (Q-DD45.2).
- The save/persistence path is untouched (in-memory chain
  execution visibility only; no Q1-bucket semantics).

## 4. Results

- New suite: **113/113** after the fix.
- **Mutants** (real work committed first at 531601e; reverted
  by inverse edit, `git diff` verified empty after each):
  M1 guard disabled (`if False and not ...`): suite falls to
  **99/113** — the exact base profile; killed. M2 guard
  returning ok=True instead of False: suite falls to
  **106/113** (the 7 `chain_refuses` checks); killed.
- **Full regression ×3** at 531601e via the signal-reset
  launcher (SIGINT/SIGQUIT reset to SIG_DFL inside the chain
  process; TOOLS.md background-shell signal law), legs
  sequential, durable logs in `director-reports/evidence/
  dd45-chain-parse-refusal/` (force-added; also goal
  hidden_files/dd45_logs/):
  - leg 1 (fwd): REGRESS: 264/264 -> GREEN; REGRESS FINAL:
    GREEN (order=fwd) — chain RC=0, 2026-11-09T18:25:48Z; the
    new suite ran inside the chain at 113/113.
  - leg 2 (--twice): REGRESS pass1: 264/264 -> GREEN;
    REGRESS pass2: 264/264 -> GREEN; REGRESS FINAL: GREEN
    (order=fwd, twice) — chain RC=0, 2026-11-09T18:44:01Z;
    the new suite ran at 113/113 in both passes.
  - leg 3 (--order rev): REGRESS: 264/264 -> GREEN; REGRESS
    FINAL: GREEN (order=rev) — chain RC=0; CHAIN_END
    2026-11-09T18:52:56Z; the new suite ran at 113/113.
- Neighbourhood suites inside the chain include
  seed_grammar_stress (P1's front-door parse-precedence pin)
  and step6_leaf_honesty, both GREEN in every leg above.

## Anticipated probes

1. **"Is the tour's original claim — Select destroys creates —
   now disproven or merely renamed?"** Disproven as a
   mechanism, with the receipts in §1: atom-level tracing
   (plane keys before/after each `_run_atom`) shows NO atom
   executes for the refused seeds, and with valid grammar
   Select reads the live plane (`scope_universe -> _ids`) and
   sees same-chain creates. What survives of the tour claim is
   its worst half: a chain-issued ok=True over work that never
   happened. §12.57a's text stands as the tour record; this
   report is the correction of record for its mechanism.
2. **"Could the guard mask a REAL empty chain?"** A seed that
   parses ok with zero atoms cannot arise from parse_seed
   (`no Dell atoms found` is itself a refusal). Programmatic
   Seed objects default ok=True; the guard keys on the
   parser's own verdict field, not on atom count.
3. **"Does any production caller depend on the old vacuous
   ok=True?"** Callers of execute_chain: the front door (only
   ever passes ok seeds — its own check fires first),
   core_ii_smoke (parses valid seeds), and direct test/probe
   surfaces. The full regression (§4) is the evidence that no
   in-repo consumer regressed.
4. **"Why not fix the grammar instead — make `51[Select] :: `
   legal?"** Because the front door has always refused it and
   the parser's refusal is coherent (an explicitly opened
   label with no content). Making it legal changes user-facing
   grammar for every surface at once; that is a design ruling
   (Q-DD45.2), not a defect repair. The defect was the
   SILENT SUCCESS, and it is closed for every parse refusal,
   not only this shape.
5. **"Test realism?"** INTEGRATION: the suite drives the
   chain authority directly (the defective surface) with the
   front door as the public-entry control; no REAL_USER_PATH
   claim is made. The front door's behavior is unchanged by
   the fix, so no new user-path evidence is claimed either.

## Questions for the Director

- **Q-DD45.1** — Scoped certification is requested for the
  DD-45 fix as bounded above (execute_chain fails closed on a
  parser-refused seed; parse error named; zero execution;
  valid-seed semantics unchanged). Accept, hold, or
  correction-required?
- **Q-DD45.2** — Grammar disposition for the trailing empty
  label (`NN[Dell] :: ` with nothing after): keep it a named
  parse refusal (current, now honestly surfaced everywhere),
  make it legal as a bare atom, or keep the refusal and rename
  its error (today `too many flow operators`, which
  misdescribes an empty label)? Uni's recommendation: keep the
  refusal, rename the error under a separate bounded change.
- **Q-DD45.3** — DD-45 is recorded in the register's G table
  as an extension-register defect (FIXED, Ace-authorized
  fix-first; strict stays 19/72), beside DD-31. Confirm the
  slotting, or direct a different register home.

*Uni Ω — evidence first; the merge gate for this PR is the
main session's §32 freshness check plus the hard gate, and
certification remains the Director's alone.*
