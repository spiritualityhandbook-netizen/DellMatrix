# C7.SCHEMA — DD-29 READ-ONLY BASELINE — CIRCUIT REPORT — 2026-11-12

Circuit: C7.Schema (plan §14.3 C7 card, §14.4 sequence; Master
Work List item 148 / DD-29). Build PR: this circuit's PR (branch
uni/c7-schema-1112, base main 42c4987ab24987c8d422af33acb8a2925937dd1a).
Grounding: hidden_files/c7schema/GROUNDING.md (cycle-1
preparation; DISCOVER > VERIFY > CLASSIFY > ARCHITECT, probe
P1–P6 at 42c4987).

## BEFORE → AFTER (capability)

BEFORE: Dell 39 [Schema] was a 3-hasattr stub
(executor_leaf.py): lattice present-and-not-None, nursery
present, growth present → "Schema: VALID". Verified by probe at
42c4987: VALID with a nonsense operand ("validate my
mixtape"), VALID with the enhance gate off and unmentioned,
VALID with `forces` deleted outright, VALID with `growth`
replaced by an inert object(). Presence was treated as health;
CONNECTED and AVAILABLE did not exist; no organ lines printed.

AFTER: 39[Schema] returns the nervous-system board. Each of
DD-29's 16 named systems is probed in isolation through its
own status provider and reported EXISTS / CONNECTED /
AVAILABLE plus its state line:

  Schema: VALID
    board: 16 systems examined · 16/16 pass
    · floor: exists=YES connected=YES available=YES — floor=Alpha/Delta/Omega/Omni locked=True
    · truths: exists=YES connected=YES available=YES — truths=3 locked=True
    · … (one line per organ)

The verdict is VALID only when every organ passes; otherwise
INVALID and the board line NAMES the failing organs and checks
(e.g. `failing: forces(exists=NO)`). The enhance gate off
reports available=OFF-by-design — healthy, never "down". A
probe that raises reports the organ UNKNOWN with the error
class named; the board itself never raises. The structured
board also rides the atom result under "schema_board" for
machine consumers. The operand remains ignored by design —
Schema interrogates the program, not the label; bare and
labeled runs return the identical board.

## MECHANISM

- New reader module form/dell_matrix/schema_board.py:
  build_schema_board(program) — per-organ isolated probes,
  one declared inventory (the 16, in Program.status()'s
  aggregation order), every organ's state from that organ's
  existing status provider using the same expressions
  status() calls. No second status authority, registry, or
  inventory. Program.status() is untouched.
- CONNECTED = the provider returns a well-formed report
  (per-organ anchor keys) without raising. Presence alone is
  never connection (the P5 husk defect class).
- AVAILABLE = read from the organ's own report: designed-off
  → OFF-by-design; explicit error marker → DEGRADED with the
  organ's reason; probe failure → UNKNOWN.
- The leaf branch (executor_leaf.py, Dell 39) now renders the
  board, carries it in the result dict, and notes the verdict
  with the historical tokens — the history receipt
  '39[Schema] :: valid' is preserved for a healthy program.

PROBE PURITY (finding the Director should note):
Program.persona_matrix_status() WRITES persona_matrix.active
on read, and personas_status() nests that call — so
Program.status()'s own aggregation mutates on that one organ
(pre-existing behavior, not introduced here). The board does
NOT call either wrapper: it reads persona_matrix.to_dict()
directly and assembles personas from the same registry reads
personas_status() uses. All 16 providers the board calls were
audited as pure reads (names in the module docstring); the
test-7 digest pins the purity, including a persona_lens set
with persona_matrix.active unset, which any wrapper-routing
probe would flip.

## EVIDENCE (Uni-run, this head)

- Failing-first: form/c7schema_test.py (28 checks, the
  brief's 9 tests) ran RED 14/28 against the stub
  (logs: hidden_files/c7schema/logs/red_stub2.log) — every
  failure a missing-board check; the purity/neighbour pins
  held pre-implementation as designed. Post-build: 28/28.
- One implementation defect found by the suite and repaired:
  the personas presence check required a callable registry
  attribute (PERSONAS is a mapping) → personas reported
  absent; fixed to presence semantics, suite green.
- Mutants (commit-first, inverse-edit reverts): M-A
  hasattr-only connected → test 4 RED; M-B OFF-by-design
  counted as failure → tests 1/5 RED; M-C raising organ
  swallowed to PASS → test 6 RED; M-D verdict = any-organ-
  healthy → test 3 RED; M-E one organ dropped from the
  inventory → test 8 RED (expectation hardcoded in the
  suite, independent of the module constant); M-F probe
  routed through the writing persona_matrix_status()
  wrapper → test 7 digest RED.
- Focused neighbours: d1_registry_leaf4 36/36 (with the 39
  expectation amended — see CONTRACT CHANGE), unified_runtime
  37/37, step6_leaf_honesty 34/34, schema_board smoke 1/1.
- Full regression campaign + exact-head CI: main session's
  step, not claimed here.

## CONTRACT CHANGE (disclosed)

The pinned D1 expectation (d1_registry_leaf4_test) asserted
39[Schema] messages == ["Schema: VALID"] exactly. The board
necessarily changes Dell 39's message shape. Amended in this
PR: the D1 39 check now asserts the board contract (verdict
line, 16 examined, 16 organ lines with three checks each,
enhance OFF-by-design, history receipt preserved); the
file's header contract line and the dell_cards.py Dell-39
deep note were updated to the measured behavior in the same
PR. No other Dell's contract changed; the history receipt
form '39[Schema] :: valid' / ':: invalid' is unchanged.

## SCOPE BOUNDARIES

- Baseline only (§14.4 cut): existing numeric facts via state
  lines; no Measure/Threshold/Limit read-in (§12.65's owed
  integration belongs to C7.MeasureFamily), no new semantic
  weights, no C7.Profile/Tokens content.
- Connectedness is provider-report well-formedness, not a
  proof the organ can WORK (growth-style action proofs are
  mutating and excluded by the purity rule) — the UNKNOWN-
  where-unprovable discipline is the mitigation.
- Registry name/manor for Dell 39 ("Validate shape")
  untouched; no typed signature added; Dell 12 untouched;
  invariants.py untouched (patterns only).
- NO MWL credit claimed; scoring is the authorities' call.

## QUESTIONS FOR THE DIRECTOR

Q-C7.1–Q-C7.7 as filed in the grounding (§4.5) — inventory
(this build takes DD-29's 16 as the contract seed; pillars/
audit() and matrices treated as meta-reports, UI/session keys
excluded, organ_atlas cross-check only), CONNECTED semantics
(provider well-formedness as the baseline definition),
AVAILABLE taxonomy (enhance the only designed-off organ among
the 16 today), output contract (VALID/INVALID vocabulary and
the preserved history receipt taken as the reasonable
version; structured "schema_board" dict rides the result —
is that the required machine-readable form?), numeric scope
(state lines only), operand (none in the baseline), probe
purity (mutating wrapper excluded in favor of the organ's
pure read — persona_matrix case — rather than isolated-
program probing).

## ANTICIPATED PROBES

- "Your CONNECTED is just 'status() didn't crash' dressed
  up." — Partly fair, and bounded honestly: it is the
  strongest read-only signal every one of the 16 organs
  actually offers today; the alternative proofs in
  invariants.py mutate. The board says UNKNOWN wherever no
  read-only signal exists rather than inflating presence
  into connection — the husk and bomb tests pin exactly
  that seam.
- "Why is the inventory yours to declare?" — DD-29 names the
  list "the circuit's contract question, seeded from
  Program.status()'s own aggregation"; the 16 are §12.28's
  named systems in status()'s order, filed as Q-C7.1 for
  ruling before any certification.
- "Test 7's digest has a hole: the history append." — The
  append is the atom's own verdict receipt, byte-compared
  to exactly ['39[Schema] :: valid'] — the historical note
  the stub also wrote. Everything else in the digest is
  direct attribute reads (no provider calls), so the digest
  cannot mask a probe mutation with its own reads.

## ACE'S MOVE

Nothing needed from Ace. Next step owner: the authorities
(Keeper stamp + Director disposition on Q-C7.1–.7 and the
build), then the main session's §32 merge transaction.
