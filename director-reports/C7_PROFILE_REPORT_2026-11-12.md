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
    · place: 0.0064s (1.5%) — 12 ideas placed
    · pulse: 0.0010s (0.2%) — resonance ok, session_pulses=1
    · growth: 0.3882s (88.6%) — nursery update included in growth (sub-stage; proposals pending 0 -> 18)
    · save: 0.0371s (8.5%) — saved program_ProfileBench….json
    · load: 0.0045s (1.0%) — loaded 13 units
    · embedding: ABSENT — OFF-by-design — embedding needs a docked Psalm (Dell 47 binding); the standalone benchmark never contacts a provider
    overhead: 0.0011s (harness, empty-workload calibration)
    unaccounted: 0.0000s
    total: 0.4384s
    largest: growth 88.6%

The dragging stage is visible at a glance (growth, 88.6%,
with the Nursery-update sub-stage share named inside it) —
the causal picture §12.38a demands, not a single "slow"
number. The structured report rides the atom result under
"profile_report": {kind: BENCHMARK, workload identity
(mode/ideas/stages/setup/run/owner), environment identity
(python/platform), stages[{name, status, seconds, share,
note}], overhead_seconds, unaccounted_seconds, total_seconds,
largest_stage, verdict}.

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

## DECISIONS TAKEN (defaults, routed for ruling)

The grounding left Q-C7P.1–.7 open; this slice builds the
grounding's recommended conservative defaults and routes
each question below — none is presented as ruled law:

- Q-C7P.1 → BENCHMARK-only v1; kind=BENCHMARK on every
  receipt; OBSERVED mode deferred to its own circuit.
- Q-C7P.2 → receipt-only timings v1 (option (b)); NO new
  timings store built; kept-timings is the named follow-up.
- Q-C7P.5 → the board reports per-stage shares and NAMES the
  largest-share stage as an observation ("largest: <stage>
  <pct>%"); NO normative threshold verdict in v1.
  Q-ACE-C7P.1 (Ace's needle threshold) stays routed.
- Q-C7P.7 → overhead disclosed as its own calibrated line;
  stages + overhead + unaccounted reconcile to total.

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
- Focused neighbours, all green at this head: c7profile
  32/32, c7schema 33/33, lm2_splitter 66/66, lm1_import
  55/55, d1_registry_leaf4 36/36, core_i_maturity 22/22,
  d1_proof_cards 6/6, unified_runtime 37/37.
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
- No threshold/"dragging" verdict; largest-stage naming is
  an observation only (Q-C7P.5 / Q-ACE-C7P.1 open).
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
rule): the observation-only naming taken here vs a ruled
threshold. Q-C7P.6 (operand grammar): confirm bare /
':: <stage>' / honest refusal. Q-C7P.7 (overhead form):
confirm the calibrated-line + remainder reconciliation.
Q-ACE-C7P.1 (for Ace, via the Director): how dominant must
a stage be before Profile calls it out beyond the largest
observation?

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
- "Growth at 88.6% — is that a defect?" — It is a
  measurement on a 12-idea disposable workload: growth does
  the cross-authoring work and pulse/save are near-instant
  at this scale. The board names the largest stage as an
  observation precisely so this question gets asked with
  numbers; whether any share is a BREACH is the unruled
  threshold question (Q-C7P.5), not a verdict v1 invents.

## ACE'S MOVE

Nothing needed from Ace. Next step owner: the main session
(full campaign at the gate, then §32), with the authorities'
dispositions on Q-C7P.1–.7 + Q-ACE-C7P.1 routed through the
Director.
