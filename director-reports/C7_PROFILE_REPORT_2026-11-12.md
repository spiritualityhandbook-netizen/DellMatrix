# C7.PROFILE — DD-39 SPEEDOMETER — CIRCUIT REPORT — 2026-11-12

Circuit: C7.Profile (plan §14 C7 "SELF-REPORT & QUANTITATIVE
CONTRACTS", slice 2 of 4; §14.4 sequence after C7.Schema;
Master Work List item 149 / DD-39). Cycle: 1 of the two-cycle
cap for DD-39. Build PR: this circuit's PR (branch
uni/c7-profile-1112, base main
374c23275dc792c600f4debe0655f1dbf3850767 — the #397 merge plus
the Keeper's watermark record). Grounding:
hidden_files/c7profile/GROUNDING.md (DISCOVER > VERIFY >
CLASSIFY against merged main 2e46272; BEFORE probe and purity
probe preserved in that directory).

## BEFORE → AFTER (capability)

BEFORE: Dell 49 [Profile] — registry "Profile / Benchmark" —
was a status echo: one leaf branch (executor_leaf.py) called
program.status() and printed 6 of its fields (owner, ideas,
history, nursery/lattice/enhance dicts). It timed NOTHING, the
label was ignored (nonsense and real operation names echoed
identically), and it MUTATED on read: its own note_seed history
append plus — proven by probe_purity.py — a transitive write
of persona_matrix.active through status()'s
persona_matrix_status() wrapper. Performance was owned by
nothing; status was duplicated from Schema's territory.

AFTER: 49[Profile] is the speedometer Ace ruled in §12.38a.
It runs a DELIBERATE BENCHMARK on DISPOSABLE state and
receipts it (live run at this head, disposable owner):

  Profile: COMPLETE
    kind: BENCHMARK · workload: 12 ideas · stages: place, pulse, growth, save, load
    env: python 3.12.3 · Linux-7.0.0-44-generic-x86_64-with-glibc2.39
    · place: 0.0059s (1.0%) — 12 ideas placed
    · pulse: 0.0009s (0.2%) — resonance ok, session_pulses=1
    · growth: 0.4995s (89.2%) — nursery update included in growth (sub-stage; proposals pending 0 -> 18)
    · save: 0.0442s (7.9%) — saved program_ProfileBench….json
    · load: 0.0072s (1.3%) — loaded 13 units
    · embedding: ABSENT — OFF-by-design — embedding needs a docked Psalm (Dell 47 binding); the standalone benchmark never contacts a provider
    overhead: 0.0013s (harness, empty-workload calibration)
    unaccounted: 0.0007s
    total: 0.5597s
    largest: growth 89.2%
    dragging: none — dragging is lag that impaired function or capability; no stage's lag did

The largest stage is visible at a glance (growth, 89.2%,
with the Nursery-update sub-stage named inside it) — the
causal picture §12.38a demands, not a single "slow" number:
Ace sees what runs and how fast or slow it runs compared to
its scope and the program as a whole. Largest is NOT
dragging: under Ace's definition (Q-ACE-C7P.1, below)
dragging requires lag that impaired function or capability,
and growth completed cleanly — so the same receipt that
names it largest also reports dragging: none. The structured
report rides the atom result under "profile_report": {kind:
BENCHMARK, workload identity (mode/ideas/stages/setup/run/
owner), environment identity (python/platform),
stages[{name, status, seconds, share, note, error_class?}],
overhead_seconds, unaccounted_seconds, total_seconds,
largest_stage, dragging, verdict}.

## MECHANISM

- New module form/dell_matrix/profile_board.py:
  run_profile_benchmark(only_stage=None) — constructs a
  DISPOSABLE program (unique temp owner, the
  p2_perf_baseline isolation pattern), builds the declared
  workload (12 ideas via Program.place), times the named
  stage sequence place -> pulse -> growth -> save -> load
  with time.perf_counter() (monotonic), and disposes of the
  disposable owner's state files. The board receives NO live
  program and never calls status().
- Per-stage fail-closed isolation: each stage runs in its
  own try/except AND verifies its effect (place: unit-count
  delta == 12 — a fresh plane carries a seed unit, so the
  check is the delta, found by the suite during the build;
  pulse/growth: the operation's own ok flag; save: the file
  exists; load: the loaded unit count equals the count at
  save). A stage that raises or fails its check reports
  FAILED with the error class named; the board completes;
  verdict is COMPLETE only when every attempted stage timed,
  PARTIAL when one failed, FAILED when the harness itself
  could not run.
- Single-stage runs perform their prerequisites as UNTIMED
  setup, disclosed on the receipt (workload.setup): e.g.
  ':: load' places and saves untimed, then times the load.
- Overhead (Q-C7P.7 default): measured by an empty-workload
  calibration (construct + dispose a disposable program, no
  stages) run before the timed run; stages + overhead +
  unaccounted reconcile to the total by construction —
  unaccounted is the remainder, printed, never rounded away.
- Embedding: ABSENT / OFF-by-design standalone (dock-only,
  Dell 47 binding). The row carries seconds=None — never a
  fabricated 0.00 — and a provider tripwire in the suite
  (LLMBridge.embed + embed_bind.embed_text patched to record
  and raise) proves zero provider contact.
- Nursery update: no standalone operation exists, so none
  was invented; it is named as growth's sub-stage in the
  growth note (proposals pending before -> after), and
  ':: nursery' REFUSES with exactly that reason.
- Operand grammar (Q-C7P.6 default): bare = standard
  benchmark; ':: <stage>' = that stage only ('resonance'
  aliases pulse; 'embedding' returns the ABSENT row alone);
  an unknown label returns ok=False skipped=True with the
  reason named and notes NOTHING — retiring ignore-the-label.
- The leaf branch keeps the historical receipt token:
  note_seed(49, "Profile") → history '49[Profile]', the ONE
  sanctioned append on the live program (Schema precedent).
  Everything else about the live program is byte-identical,
  digest-pinned, including a persona_matrix.active sentinel
  that any status() routing would flip.
- Dragging (post-build correction, Ace's Q-ACE-C7P.1
  ruling): FAILED stage entries now also carry a structured
  error_class. The board's `dragging` list is computed by
  ONE rule — a stage is dragging only when its failure is
  time-attributable, i.e. it raised a timeout-class error
  (TimeoutError / TimeoutExpired: a bounded wait or time
  budget exhausted — the failure IS the lag). The stage's
  failure note rides as the entry's reason. Every other
  outcome is excluded by construction: TIMED stages (any
  share), FAILED stages with non-timing errors, ABSENT rows.
  The receipt prints one dragging line per named stage, or
  "dragging: none" with Ace's definition stated on the line
  itself, so share can never be misread as dragging later.

## DECISIONS TAKEN (defaults, routed for ruling)

The grounding left Q-C7P.1–.7 open; this slice builds the
grounding's recommended conservative defaults and routes
each question below — none is presented as ruled law:

- Q-C7P.1 → BENCHMARK-only v1; kind=BENCHMARK on every
  receipt; OBSERVED mode deferred to its own circuit.
- Q-C7P.2 → receipt-only timings v1 (option (b)); NO new
  timings store built; kept-timings is the named follow-up.
- Q-C7P.5 → RESOLVED by Ace's answer to Q-ACE-C7P.1 (see
  below): no share threshold exists; dragging is
  impairment-defined. The board still reports per-stage
  shares and NAMES the largest-share stage as an observation
  ("largest: <stage> <pct>%") — visibility, never a verdict.
- Q-C7P.7 → overhead disclosed as its own calibrated line;
  stages + overhead + unaccounted reconcile to total.

## Q-ACE-C7P.1 — ANSWERED BY ACE (2026-11-12, post-build correction)

Ace ruled, verbatim substance: "Dragging occurs when lag
affects the functionality or the capability of anything,
any process. Otherwise it's not dragging." And on Profile's
purpose: "Profile is so I can see what runs and how fast or
slow it runs compared to its scope and the program as a
whole. Like how it can see that growth eats most of the
tick — now I know that growth takes a lot of power."

Implemented in this same circuit (head after e90a337):
profile_report.dragging lists ONLY stages whose lag
demonstrably impaired function in the run — in the v1
benchmark the one honest impairment evidence is
time-attributable failure: a stage that raised a
timeout-class error (its bounded wait/time budget ran out).
A stage failing for a non-timing reason is FAILED, not
dragging; a clean stage at 89.2% share is largest, not
dragging. The receipt's dragging line states the definition
so the distinction survives the reader. Suite pins both
directions plus the converse (section 12 of the suite).

## NORTH STAR — ACE'S STATED DIRECTION (recorded, NOT built)

Ace, same ruling: if every part of a car were entered into
DellMatrix as information, Profile should be able to see
how they all run together — how they tick together. That
is: Profile's receipts generalize from the program's own
stages to ANY modeled system whose parts and operations are
represented in the Matrix — per-part timing against the
whole system's tick, with dragging judged by impaired
function of the modeled system. Recorded here as Ace's
direction for later Profile slices. V1 claims NONE of it:
v1 times DellMatrix's own named stages only, on disposable
state, in BENCHMARK mode.

## EVIDENCE (Uni-run, this head)

- Failing-first: form/c7profile_test.py (32 checks, the
  grounding's ten cases; case 10 adapted to receipt-only per
  Q-C7P.2(b)) ran RED 7/32 against the stub
  (logs: hidden_files/c7profile/logs/red_prefix.log) — the
  failures ARE DD-39 reproduced: status echo, ok=True label
  ignored, persona sentinel flipped SENTINEL→None. Post-build:
  32/32 (logs/green_postfix.log).
- One implementation defect found by the suite and repaired
  in-cycle: the place effect check assumed an empty plane;
  a fresh program carries a seed unit (13 != 12) → the check
  is now the unit-count DELTA. Disclosed, not silently
  adapted.
- Mutants (real work committed first; inverse-edit reverts;
  tree verified clean after each): M1 wall-clock substitution
  perf_counter→time.time → t7 RED; M2 overhead line dropped
  → t1_lines RED; M3 provider contact for embedding
  (embed_bind.embed_text call added) → t4 tripwire RED
  (calls=['embed_bind.embed_text']); M4 live-program contact
  reintroduced (program.status() in the leaf branch) → t3
  digest + sentinel RED (pm_active SENTINEL→None).
- Post-build correction (Ace's Q-ACE-C7P.1 ruling): suite
  32 → 36 checks. New section 12 pins: t12_clean_largest_
  not_dragging (standard run: dragging == [] while largest
  == growth), t12_dragging_line_none_wording (the "dragging:
  none" line states the impaired-function definition),
  t12_timeout_stage_is_dragging (synthetic pulse double
  raising TimeoutError appears in dragging with its reason;
  verdict PARTIAL; receipt line "dragging: pulse (...)"),
  t12_nontiming_failure_not_dragging (RuntimeError bomb at
  save: FAILED, dragging == []). One legacy pin amended,
  disclosed: t8_no_threshold_verdict previously also required
  the word "dragging" to be ABSENT from receipts — that
  pinned the pre-ruling default; Ace's ruling makes the
  dragging line mandatory, so the pin now asserts only the
  surviving contract (no share-threshold verdict). Post-
  correction suite: 36/36 (logs/green_dragging.log). M5
  (correction mutant): dragging computed by share (>50% →
  dragging) → ALL FOUR t12 pins RED, growth flagged at 92.7%
  share despite clean completion (logs/mutant_share_flag.
  log); reverted by inverse edit, tree clean, 36/36 restored.
- Focused neighbours: re-run at the correction head —
  c7profile 36/36, c7schema 33/33, d1_registry_leaf4 PASS,
  core_i_maturity 22/22. Green at the build head a24089a
  (the correction touches no surface they read):
  lm2_splitter 66/66, lm1_import 55/55, d1_proof_cards 6/6,
  unified_runtime 37/37.
- regress LIST: 278 entries by import (277 + c7profile),
  no duplicates.
- Full regression campaign + exact-head CI: NOT run by this
  lane — campaigns serialize on this box and LM-3's (#398)
  is running; the campaign follows at the gate from the main
  session. Not claimed here.

## CONTRACT CHANGES (disclosed, deliberate)

The stub was pinned by two legacy checks; both pins are
updated IN THIS PR with the change named, per the brief:

- d1_registry_leaf4_test: the exact status-echo expectation
  for 49[Profile] now asserts the benchmark contract
  (receipt kind/verdict, no "owner=" echo); the file's
  header contract line for Dell 49 rewritten to match.
- core_i_maturity_test: the "ideas=" pin now asserts the
  benchmark receipt fields (BENCHMARK kind line + total
  line).
- dell_cards.py: Dell 49's deep note rewritten to the
  measured behavior (circuit-19 provenance marker kept, per
  the leaf4 docs pin — the same disposition #397 used for
  Dell 39); DELL_PROOF_CARDS.md re-rendered via the
  canonical renderer (build_all_cards/render_cards_md);
  diff is the single Dell-49 note line.

## SCOPE BOUNDARIES (non-claims)

- No OBSERVED mode; no live-tick numbers; every number is
  labeled BENCHMARK and is a this-machine/this-workload fact.
- No timings store; change-over-time visibility awaits the
  kept-timings follow-up (Q-C7P.2).
- Dragging is impairment-defined ONLY (Ace's ruling): v1
  attributes it solely on timeout-class stage failure.
  OBSERVED-mode dragging — lag measurably degrading a live
  operation without a timeout — is not evidenced by a
  disposable benchmark and is NOT claimed; it belongs to
  the deferred OBSERVED circuit. No share threshold exists
  at any size. The north-star generalization (Profile over
  arbitrary modeled systems) is recorded, not built.
- No save-path repair: Profile TIMES the everyday save; the
  DD-06 pair defect stays gated on the Q1 line.
- No persona write-on-read fix: routed around on this path,
  not repaired; it remains the C7.Schema audit's separate
  hygiene item.
- Timings are evidence, never influence: nothing here
  gates, ranks, authorizes, or feeds DuoBeta learning.
  Becoming weighable quantities is C7.MeasureFamily's later
  step.
- NO MWL credit claimed; scoring is the authorities' call.

## QUESTIONS FOR THE DIRECTOR

Q-C7P.1 (mode fork): confirm BENCHMARK-only v1, OBSERVED
deferred. Q-C7P.2 (timings kept): confirm receipt-only v1
with the bounded store as a follow-up circuit — or rule the
store into a correction. Q-C7P.3 (receipt token + echo):
confirm retiring the status echo entirely and retaining
only note_seed(49, "Profile"). Q-C7P.4 (stage inventory):
confirm place/pulse/growth/save/load with nursery-update as
growth's sub-stage and embedding ABSENT standalone, and the
benchmark's named sequence as what "the tick" means for
Profile v1 (no Program.tick exists). Q-C7P.5 (dragging
rule): RESOLVED — Ace answered it through Q-ACE-C7P.1
(dragging = lag that impaired function/capability; no
share threshold); implemented impairment-evidenced-only
in the post-build correction. No Director action needed
unless he disputes the v1 attribution (timeout-class
failure as the sole benchmark-honest impairment evidence).
Q-C7P.6 (operand grammar): confirm bare /
':: <stage>' / honest refusal. Q-C7P.7 (overhead form):
confirm the calibrated-line + remainder reconciliation.
Q-ACE-C7P.1: ANSWERED BY ACE 2026-11-12 (see the dedicated
section above); nothing outstanding.

## ANTICIPATED PROBES

- "Your 'benchmark' times a program you built yourself —
  what does it say about MY program?" — Exactly what the
  receipt claims and no more: kind=BENCHMARK, workload and
  environment identified. §14 mandates disposable state for
  repeat benchmarks and forbids the probe mutating user
  work; OBSERVED numbers are the separate circuit Q-C7P.1
  names. The alternative shipped for years — timing
  nothing while echoing status — said less and implied
  more.
- "Overhead is measured on a DIFFERENT (empty) run — the
  reconciliation is rigged." — The overhead line is labeled
  a calibration estimate, and the identity holds because
  unaccounted is DEFINED as the remainder and printed —
  the reader sees all three terms and can judge the
  estimate's size (observed: overhead ~0.001s against a
  ~0.44s total, unaccounted ~0.0000s). Nothing is hidden
  inside a rounded total.
- "Growth at ~89% — is that a defect?" — It is a
  measurement on a 12-idea disposable workload: growth does
  the cross-authoring work and pulse/save are near-instant
  at this scale. The board names the largest stage as an
  observation precisely so this question gets asked with
  numbers. And under Ace's own definition it is NOT
  dragging: growth completed its function cleanly, so the
  receipt says dragging: none on the same lines that name
  it largest. Dragging would require lag that impaired
  function — in v1, a stage dying on a timeout — and no
  share, however large, substitutes for that evidence.

## ACE'S MOVE

Nothing needed from Ace — Q-ACE-C7P.1 is answered and its
ruling is implemented in this same circuit. Next step
owner: the main session (full campaign at the gate, then
§32), with the authorities' dispositions on Q-C7P.1–.4
and Q-C7P.6–.7 routed through the Director.
