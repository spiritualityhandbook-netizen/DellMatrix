# R5-D PATH-LEVEL PROOFS — classes A and B (P2 discharge attempt)

Prepared: 2026-11-19 (susx100000-execution), answering Director
7028973030 / 7030045309 / 7030396734: A/B labels were function-level
AST HYPOTHESES; this record replaces them with per-path evidence
from r5d_path_proof.py (checkout-relative, beside this file).
Census at main 702741969c6d2d1d020f85845912f1da84f31418. Sites analyzed: 71 (A=26, B=45).

## Verdict counts

- A-DOWNGRADED-B-LOOP: 2
- A-PROVEN-DIRECT: 24
- B-NOT-PROVEN: 11
- B-PROVEN-CANDIDATE: 34

## Reconciled partition (supersedes the A=26 / B=45 hypothesis counts)

- A-PROVEN-DIRECT: 24 — buildable as class A.
- B-PROVEN-CANDIDATE: 34, plus A-DOWNGRADED-B-LOOP: 2 (per-iteration
  preflight at loop-body start) — buildable as class B: 36.
- B-NOT-PROVEN: 11 — the noted text depends on state mutated before
  the note, so an entry preflight cannot compute the exact eventual
  bytes without simulating the mutation. These MOVE to C-HOLD
  unless a per-site manual proof discharges them.
- Effective partition: A=24 + B=36 + C-HOLD=50 (39 original + 11
  moved) + DOOR=1 = 111. Any bounded R5-D authorization ask must
  use THESE numbers: buildable scope 60 sites, held 50.

## Cross-cutting boundaries (all A/B sites)

- TOCTOU: no threading/lock use exists in form/open.py or
  form/persist.py (grep evidence, this run); the program is
  single-threaded in-process, so a synchronous preflight in the
  same call stack as the append has no interleaving writer.
  Multi-process concurrent writers to one owner file are NOT
  excluded by any lock — that boundary stays UNKNOWN and the
  preflight guarantees refusal atomicity only within one process.
- Restart/fault: preflight is in-memory only; it writes nothing,
  so a crash between preflight and append leaves durable state
  exactly as the underlying mutation path leaves it — the R5
  save path itself keeps the atomic_write_json contract
  (complete generation or previous generation, never torn).
  Power-loss durability remains UNKNOWN per R5-C P6.
- Privacy: preflight must apply sanitize_text (R5 P5) to the
  evaluated argument text BEFORE measuring/admitting, and the
  refusal receipt carries counts/bytes only, never raw text —
  the per-site eventual templates below are formulas, not values.
- Residual limit: helper calls before a note may mutate through
  aliases invisible to direct-mutation AST analysis; each site
  lists its helper_calls_before so the Keeper can spot-challenge.

## B -> B-PROVEN-CANDIDATE — form/dell_matrix/allwhere.py:289 note in birth_character

- args: ["f'Born in {town.name}, city of {city.name}, under interest {interests}.'"]
- mut_before(direct): [[282, 'ch.abilities[ab]'], [284, 'ch.inventory.append'], [285, 'ch.inventory.append'], [286, 'ch.inventory.append'], [288, 'home_room.occupants.append']]
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: ['city.towns.values', 'hashlib.sha1', 'hashlib.sha1(name.encode()).hexdigest', 'interests[0].title', 'name.encode', 'rng.randint', 'town.rooms.values', 'world.cities.items']
- eventual: note: text=(action or "").strip()[:120] (current) ; sanitized under R5 P5 before measure
- why: argument expressions do not depend on any direct mutation between the first mutation and the note call (no interval Name assignment, no attribute overlap, no non-whitelisted arg call); the same expressions evaluated before the first mutation yield the identical eventual text, so a preflight computing sanitize+canonical bytes from them is byte-exact against direct mutations (helper-call side effects UNKNOWN).

## B -> B-PROVEN-CANDIDATE — form/dell_matrix/allwhere.py:327 note in start_travel

- args: ["f'Traveling to {target_town.name} ({minutes} min sim).'"]
- mut_before(direct): [[318, 'ch.traveling'], [324, 'ch.energy']]
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: ["ch.abilities['traveling'].use", 'world.cities.values']
- eventual: note: text=(action or "").strip()[:120] (current) ; sanitized under R5 P5 before measure
- why: argument expressions do not depend on any direct mutation between the first mutation and the note call (no interval Name assignment, no attribute overlap, no non-whitelisted arg call); the same expressions evaluated before the first mutation yield the identical eventual text, so a preflight computing sanitize+canonical bytes from them is byte-exact against direct mutations (helper-call side effects UNKNOWN).

## B -> B-NOT-PROVEN — form/dell_matrix/allwhere.py:351 note in tick_travel

- args: ["f'Arrived in {dest}.'"]
- mut_before(direct): [[334, "ch.traveling['ticks_left']"], [338, 'ch.city_id'], [339, 'ch.town_id'], [340, 'ch.room_id'], [345, 'square.occupants.append'], [346, 'ch.room_id'], [350, 'ch.traveling']]
- in_loop: False; loop_muts: []
- deps: ["arg name(s) ['dest'] assigned after first mutation"]
- helper_calls_before: ['town.rooms.values']
- eventual: note: text=(action or "").strip()[:120] (current) ; sanitized under R5 P5 before measure
- why: noted text may depend on state mutated before the note: ["arg name(s) ['dest'] assigned after first mutation"]

## B -> B-PROVEN-CANDIDATE — form/dell_matrix/allwhere.py:382 note in enter_room

- args: ["f'Looking into {room.name} (full).'"]
- mut_before(direct): [[381, 'ch.room_id']]
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: ['town.rooms.get']
- eventual: note: text=(action or "").strip()[:120] (current) ; sanitized under R5 P5 before measure
- why: argument expressions do not depend on any direct mutation between the first mutation and the note call (no interval Name assignment, no attribute overlap, no non-whitelisted arg call); the same expressions evaluated before the first mutation yield the identical eventual text, so a preflight computing sanitize+canonical bytes from them is byte-exact against direct mutations (helper-call side effects UNKNOWN).

## B -> B-PROVEN-CANDIDATE — form/dell_matrix/allwhere.py:387 note in enter_room

- args: ["f'Entered {room.name}.'"]
- mut_before(direct): [[381, 'ch.room_id'], [384, 'room.occupants.append'], [385, 'ch.room_id']]
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: ['room.look', 'town.rooms.get']
- eventual: note: text=(action or "").strip()[:120] (current) ; sanitized under R5 P5 before measure
- why: argument expressions do not depend on any direct mutation between the first mutation and the note call (no interval Name assignment, no attribute overlap, no non-whitelisted arg call); the same expressions evaluated before the first mutation yield the identical eventual text, so a preflight computing sanitize+canonical bytes from them is byte-exact against direct mutations (helper-call side effects UNKNOWN).

## B -> B-NOT-PROVEN — form/dell_matrix/allwhere.py:395 note in rest

- args: ["f'Rested · energy={ch.energy}'"]
- mut_before(direct): [[394, 'ch.energy']]
- in_loop: False; loop_muts: []
- deps: ['arg attr ch.energy overlaps mutated ch.energy']
- helper_calls_before: []
- eventual: note: text=(action or "").strip()[:120] (current) ; sanitized under R5 P5 before measure
- why: noted text may depend on state mutated before the note: ['arg attr ch.energy overlaps mutated ch.energy']

## A -> A-PROVEN-DIRECT — form/dell_matrix/allwhere.py:417 note in source_post

- args: ["f'Source[{kind}]: {text[:60]}'"]
- mut_before(direct): []
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: []
- eventual: note: text=(action or "").strip()[:120] (current) ; sanitized under R5 P5 before measure
- why: no direct mutation before the call in the enclosing function and no loop-carried mutation; door refusal is pre-mutation against direct mutations (helper-call side effects UNKNOWN).

## B -> B-PROVEN-CANDIDATE — form/dell_matrix/allwhere.py:475 note in activate_mission

- args: ["f'Mission active: {m.title}'"]
- mut_before(direct): [[474, 'm.status']]
- in_loop: True; loop_muts: [[474, 'm.status']]
- deps: []
- helper_calls_before: []
- eventual: note: text=(action or "").strip()[:120] (current) ; sanitized under R5 P5 before measure
- why: argument expressions do not depend on any direct mutation between the first mutation and the note call (no interval Name assignment, no attribute overlap, no non-whitelisted arg call); the same expressions evaluated before the first mutation yield the identical eventual text, so a preflight computing sanitize+canonical bytes from them is byte-exact against direct mutations (helper-call side effects UNKNOWN).

## B -> B-PROVEN-CANDIDATE — form/dell_matrix/allwhere.py:491 note in check_missions

- args: ["f'Completed: {m.title} (+{m.reward} coin)'"]
- mut_before(direct): [[486, 'm.status'], [487, 'ch.money'], [490, 'done.append']]
- in_loop: True; loop_muts: [[486, 'm.status'], [487, 'ch.money'], [490, 'done.append'], [493, 'm.status'], [494, 'ch.money'], [495, 'done.append'], [501, 'm.status'], [502, 'done.append']]
- deps: []
- helper_calls_before: ["ch.abilities['navigation'].use"]
- eventual: note: text=(action or "").strip()[:120] (current) ; sanitized under R5 P5 before measure
- why: argument expressions do not depend on any direct mutation between the first mutation and the note call (no interval Name assignment, no attribute overlap, no non-whitelisted arg call); the same expressions evaluated before the first mutation yield the identical eventual text, so a preflight computing sanitize+canonical bytes from them is byte-exact against direct mutations (helper-call side effects UNKNOWN).

## B -> B-PROVEN-CANDIDATE — form/dell_matrix/allwhere.py:496 note in check_missions

- args: ["f'Completed: {m.title} (+{m.reward} coin)'"]
- mut_before(direct): [[486, 'm.status'], [487, 'ch.money'], [490, 'done.append'], [493, 'm.status'], [494, 'ch.money'], [495, 'done.append']]
- in_loop: True; loop_muts: [[486, 'm.status'], [487, 'ch.money'], [490, 'done.append'], [493, 'm.status'], [494, 'ch.money'], [495, 'done.append'], [501, 'm.status'], [502, 'done.append']]
- deps: []
- helper_calls_before: ["ch.abilities['navigation'].use"]
- eventual: note: text=(action or "").strip()[:120] (current) ; sanitized under R5 P5 before measure
- why: argument expressions do not depend on any direct mutation between the first mutation and the note call (no interval Name assignment, no attribute overlap, no non-whitelisted arg call); the same expressions evaluated before the first mutation yield the identical eventual text, so a preflight computing sanitize+canonical bytes from them is byte-exact against direct mutations (helper-call side effects UNKNOWN).

## B -> B-PROVEN-CANDIDATE — form/dell_matrix/allwhere.py:503 note in check_missions

- args: ["f'Completed personal aim: {m.title}'"]
- mut_before(direct): [[486, 'm.status'], [487, 'ch.money'], [490, 'done.append'], [493, 'm.status'], [494, 'ch.money'], [495, 'done.append'], [501, 'm.status'], [502, 'done.append']]
- in_loop: True; loop_muts: [[486, 'm.status'], [487, 'ch.money'], [490, 'done.append'], [493, 'm.status'], [494, 'ch.money'], [495, 'done.append'], [501, 'm.status'], [502, 'done.append']]
- deps: []
- helper_calls_before: ["ch.abilities['navigation'].use", 'town.rooms.get']
- eventual: note: text=(action or "").strip()[:120] (current) ; sanitized under R5 P5 before measure
- why: argument expressions do not depend on any direct mutation between the first mutation and the note call (no interval Name assignment, no attribute overlap, no non-whitelisted arg call); the same expressions evaluated before the first mutation yield the identical eventual text, so a preflight computing sanitize+canonical bytes from them is byte-exact against direct mutations (helper-call side effects UNKNOWN).

## B -> B-NOT-PROVEN — form/dell_matrix/allwhere.py:665 note in step_story

- args: ['self.ending']
- mut_before(direct): [[543, 'self.tick'], [549, 'events.append'], [556, 'self.lore_heard'], [557, 'events.append'], [565, 'events.append'], [575, 'self.lore_heard'], [576, 'events.append'], [590, 'self.lore_heard'], [591, 'events.append'], [598, 'events.append'], [601, 'events.append'], [606, 'events.append'], [608, 'events.append'], [618, 'self.lore_heard'], [619, 'events.append'], [623, 'events.append'], [631, 'ch.money'], [634, 'events.append'], [642, 'ch.money'], [650, 'events.append'], [657, 'self.completed'], [658, 'self.ending']]
- in_loop: False; loop_muts: []
- deps: ['arg attr self.ending overlaps mutated self.ending']
- helper_calls_before: ['ch.abilities.get', "ch.abilities['bargaining'].use", 'p.get', "p.get('text', '').lower", 'r.get', 'self.status_card', 'self.world.cities[ch.city_id].towns.values', 'town.rooms.values']
- eventual: note: text=(action or "").strip()[:120] (current) ; sanitized under R5 P5 before measure
- why: noted text may depend on state mutated before the note: ['arg attr self.ending overlaps mutated self.ending']

## B -> B-PROVEN-CANDIDATE — form/dell_matrix/code_evolution.py:76 note_seed in ensure_root

- args: ['8', "'Create'", "'code_evolution_root'"]
- mut_before(direct): [[63, 'program.place']]
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: ['catalog.get', 'idea.get', 'skin_map.get']
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: argument expressions do not depend on any direct mutation between the first mutation and the note call (no interval Name assignment, no attribute overlap, no non-whitelisted arg call); the same expressions evaluated before the first mutation yield the identical eventual text, so a preflight computing sanitize+canonical bytes from them is byte-exact against direct mutations (helper-call side effects UNKNOWN).

## B -> B-PROVEN-CANDIDATE — form/dell_matrix/code_evolution.py:201 note_seed in research_with_internet

- args: ['45', "'Translate'", "'ce_research'"]
- mut_before(direct): [[187, 'notes.append'], [200, 'u.detail']]
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: ['n.get', 'net.research_topic', 'program.cube.session.plane.units.get', 'r.get', 'time.strftime']
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: argument expressions do not depend on any direct mutation between the first mutation and the note call (no interval Name assignment, no attribute overlap, no non-whitelisted arg call); the same expressions evaluated before the first mutation yield the identical eventual text, so a preflight computing sanitize+canonical bytes from them is byte-exact against direct mutations (helper-call side effects UNKNOWN).

## B -> B-PROVEN-CANDIDATE — form/dell_matrix/code_evolution.py:254 note_seed in mark_complete

- args: ['50', "'Manifest'", "'code_evolution_complete'"]
- mut_before(direct): [[245, 'goals.append'], [246, 'u.goals'], [253, 'u.detail']]
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: ['checklist.get', 'program.cube.session.plane.units.get', 'time.gmtime', 'time.strftime']
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: argument expressions do not depend on any direct mutation between the first mutation and the note call (no interval Name assignment, no attribute overlap, no non-whitelisted arg call); the same expressions evaluated before the first mutation yield the identical eventual text, so a preflight computing sanitize+canonical bytes from them is byte-exact against direct mutations (helper-call side effects UNKNOWN).

## B -> B-PROVEN-CANDIDATE — form/dell_matrix/first_person.py:511 note_seed in move_fp

- args: ['19', "'Drive'", "f'fp_{d}'"]
- mut_before(direct): [[503, 'program.avatar.body.pos'], [504, 'program.center_f'], [505, 'program.grid_snap']]
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: ["(direction or 'forward').lower", 'program._push_user_trail', 'program.apply_grid_snap']
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: argument expressions do not depend on any direct mutation between the first mutation and the note call (no interval Name assignment, no attribute overlap, no non-whitelisted arg call); the same expressions evaluated before the first mutation yield the identical eventual text, so a preflight computing sanitize+canonical bytes from them is byte-exact against direct mutations (helper-call side effects UNKNOWN).

## A -> A-PROVEN-DIRECT — form/dell_matrix/first_person.py:523 note_seed in turn_fp

- args: ['4', "'Transform'", "f'fp_turn_{direction}'"]
- mut_before(direct): []
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: ['program.avatar.face']
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: no direct mutation before the call in the enclosing function and no loop-carried mutation; door refusal is pre-mutation against direct mutations (helper-call side effects UNKNOWN).

## B -> B-PROVEN-CANDIDATE — form/dell_matrix/first_person.py:537 note_seed in look_fp

- args: ['9', "'Show'", "f'fp_look_{p}'"]
- mut_before(direct): [[535, 'program.look_pitch']]
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: ["(pitch or 'level').lower"]
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: argument expressions do not depend on any direct mutation between the first mutation and the note call (no interval Name assignment, no attribute overlap, no non-whitelisted arg call); the same expressions evaluated before the first mutation yield the identical eventual text, so a preflight computing sanitize+canonical bytes from them is byte-exact against direct mutations (helper-call side effects UNKNOWN).

## A -> A-PROVEN-DIRECT — form/dell_matrix/fourier.py:199 note_seed in program_fourier_demo

- args: ['17', "'Wave'", "'fourier_demo'"]
- mut_before(direct): []
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: []
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: no direct mutation before the call in the enclosing function and no loop-carried mutation; door refusal is pre-mutation against direct mutations (helper-call side effects UNKNOWN).

## A -> A-PROVEN-DIRECT — form/dell_matrix/linear_algebra.py:192 note_seed in program_transform

- args: ['15', "'Map'", "f'la_{kind}'"]
- mut_before(direct): []
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: ["(kind or 'rotate').lower", 'Mat2.identity', 'Mat2.rotate', 'Mat2.scale', 'Mat2.shear_x']
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: no direct mutation before the call in the enclosing function and no loop-carried mutation; door refusal is pre-mutation against direct mutations (helper-call side effects UNKNOWN).

## B -> B-NOT-PROVEN — form/dell_matrix/logistic_map.py:100 note_seed in apply_to_forces

- args: ['13', "'Loop'", "f'logistic_{regime}'"]
- mut_before(direct): [[76, 'self.step'], [85, 'ff.growth.intensity'], [96, "report['forces']"], [98, "report['error']"]]
- in_loop: False; loop_muts: []
- deps: ["arg name(s) ['regime'] assigned after first mutation"]
- helper_calls_before: ['ff.status', 'ff.weather.set_condition', 'regime.startswith', 'self.intensity_hint', 'self.regime']
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: noted text may depend on state mutated before the note: ["arg name(s) ['regime'] assigned after first mutation"]

## B -> B-PROVEN-CANDIDATE — form/dell_matrix/matrices_hub.py:115 note_seed in evolve_program

- args: ['13', "'Loop'", "'evolve'"]
- mut_before(direct): [[110, "out['duo']"], [110, 'program.duo.evolve'], [113, "out['forces']"]]
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: ['program.forces.tick', 'program.nodes_payload']
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: argument expressions do not depend on any direct mutation between the first mutation and the note call (no interval Name assignment, no attribute overlap, no non-whitelisted arg call); the same expressions evaluated before the first mutation yield the identical eventual text, so a preflight computing sanitize+canonical bytes from them is byte-exact against direct mutations (helper-call side effects UNKNOWN).

## B -> B-PROVEN-CANDIDATE — form/dell_matrix/needs.py:132 note_seed in set_detail

- args: ['4', "'Transform'", "f'detail_{uid}'"]
- mut_before(direct): [[128, 'u.detail'], [130, 'u.words']]
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: ["(detail or '').strip", "(u.words or '').strip", 'time.time']
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: argument expressions do not depend on any direct mutation between the first mutation and the note call (no interval Name assignment, no attribute overlap, no non-whitelisted arg call); the same expressions evaluated before the first mutation yield the identical eventual text, so a preflight computing sanitize+canonical bytes from them is byte-exact against direct mutations (helper-call side effects UNKNOWN).

## B -> B-PROVEN-CANDIDATE — form/dell_matrix/needs.py:144 note_seed in set_goals

- args: ['4', "'Transform'", "f'goals_{uid}'"]
- mut_before(direct): [[142, 'u.goals']]
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: ['g.strip', 're.split', 'time.time']
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: argument expressions do not depend on any direct mutation between the first mutation and the note call (no interval Name assignment, no attribute overlap, no non-whitelisted arg call); the same expressions evaluated before the first mutation yield the identical eventual text, so a preflight computing sanitize+canonical bytes from them is byte-exact against direct mutations (helper-call side effects UNKNOWN).

## B -> B-NOT-PROVEN — form/dell_matrix/needs.py:396 note_seed in undo_last

- args: ['24', "'Unlock'", "f'undo_place_{uid}'"]
- mut_before(direct): [[351, 'st.pop'], [361, 'st.append'], [392, 'plane.remove']]
- in_loop: False; loop_muts: []
- deps: ["arg name(s) ['uid'] assigned after first mutation"]
- helper_calls_before: ['act.get']
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: noted text may depend on state mutated before the note: ["arg name(s) ['uid'] assigned after first mutation"]

## B -> B-NOT-PROVEN — form/dell_matrix/needs.py:412 note_seed in undo_last

- args: ['24', "'Unlock'", "f'undo_edit_detail_{uid}'"]
- mut_before(direct): [[351, 'st.pop'], [361, 'st.append'], [392, 'plane.remove'], [411, 'u.detail']]
- in_loop: False; loop_muts: []
- deps: ["arg name(s) ['uid'] assigned after first mutation"]
- helper_calls_before: ['act.get', 'program.cube.session.plane.units.get']
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: noted text may depend on state mutated before the note: ["arg name(s) ['uid'] assigned after first mutation"]

## B -> B-NOT-PROVEN — form/dell_matrix/needs.py:421 note_seed in undo_last

- args: ['24', "'Unlock'", "f'undo_edit_goals_{uid}'"]
- mut_before(direct): [[351, 'st.pop'], [361, 'st.append'], [392, 'plane.remove'], [411, 'u.detail'], [420, 'u.goals']]
- in_loop: False; loop_muts: []
- deps: ["arg name(s) ['uid'] assigned after first mutation"]
- helper_calls_before: ['act.get', 'program.cube.session.plane.units.get']
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: noted text may depend on state mutated before the note: ["arg name(s) ['uid'] assigned after first mutation"]

## B -> B-PROVEN-CANDIDATE — form/dell_matrix/needs.py:533 note_seed in redo_last

- args: ['24', "'Unlock'", "f'redo_place_{uid}'"]
- mut_before(direct): [[475, 'program.place'], [502, 'plane.box'], [503, 'u.sandboxed'], [504, 'u.sandbox_id'], [518, 'plane.remove'], [522, 'sb.member_ids'], [523, 'plane.units.pop'], [532, 'redo.pop']]
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: ['act.get', 'plane.sandboxes.values', 'plane.unbox', 'record.get']
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: argument expressions do not depend on any direct mutation between the first mutation and the note call (no interval Name assignment, no attribute overlap, no non-whitelisted arg call); the same expressions evaluated before the first mutation yield the identical eventual text, so a preflight computing sanitize+canonical bytes from them is byte-exact against direct mutations (helper-call side effects UNKNOWN).

## B -> B-NOT-PROVEN — form/dell_matrix/needs.py:552 note_seed in redo_last

- args: ['24', "'Unlock'", "f'redo_edit_detail_{uid}'"]
- mut_before(direct): [[475, 'program.place'], [502, 'plane.box'], [503, 'u.sandboxed'], [504, 'u.sandbox_id'], [518, 'plane.remove'], [522, 'sb.member_ids'], [523, 'plane.units.pop'], [532, 'redo.pop'], [549, 'u.detail'], [551, 'redo.pop']]
- in_loop: False; loop_muts: []
- deps: ["arg name(s) ['uid'] assigned after first mutation"]
- helper_calls_before: ['act.get', 'act.items', 'plane.sandboxes.values', 'plane.unbox', 'program.cube.session.plane.units.get', 'record.get']
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: noted text may depend on state mutated before the note: ["arg name(s) ['uid'] assigned after first mutation"]

## B -> B-NOT-PROVEN — form/dell_matrix/needs.py:565 note_seed in redo_last

- args: ['24', "'Unlock'", "f'redo_edit_goals_{uid}'"]
- mut_before(direct): [[475, 'program.place'], [502, 'plane.box'], [503, 'u.sandboxed'], [504, 'u.sandbox_id'], [518, 'plane.remove'], [522, 'sb.member_ids'], [523, 'plane.units.pop'], [532, 'redo.pop'], [549, 'u.detail'], [551, 'redo.pop'], [562, 'u.goals'], [564, 'redo.pop']]
- in_loop: False; loop_muts: []
- deps: ["arg name(s) ['uid'] assigned after first mutation"]
- helper_calls_before: ['act.get', 'act.items', 'plane.sandboxes.values', 'plane.unbox', 'program.cube.session.plane.units.get', 'record.get']
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: noted text may depend on state mutated before the note: ["arg name(s) ['uid'] assigned after first mutation"]

## A -> A-DOWNGRADED-B-LOOP — form/dell_matrix/spatial_authority.py:473 note_seed in tick

- args: ['5', "'Spatial'", "f'freeze {uid}: non-finite position'"]
- mut_before(direct): []
- in_loop: True; loop_muts: [[540, 'self.velocities[uid]']]
- deps: []
- helper_calls_before: ['canonical_lifecycle.is_active', 'math.isfinite', 'self._build_grid', 'self._env_mode', 'self._graph_neighbors', 'self._report', 'self._scores', 'self._wells']
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: inside loop; loop body mutates [(540, 'self.velocities[uid]')]; on iteration >=2 those mutations precede the note, so the function-level n_before=0 does NOT prove pre-mutation per path. Args do not depend on mutations before the call in the same iteration, so a per-iteration preflight at loop-body start remains possible (class B-LOOP).

## A -> A-DOWNGRADED-B-LOOP — form/dell_matrix/spatial_authority.py:530 note_seed in tick

- args: ['5', "'Spatial'", "f'freeze {uid}: non-finite update'"]
- mut_before(direct): []
- in_loop: True; loop_muts: [[540, 'self.velocities[uid]']]
- deps: []
- helper_calls_before: ['canonical_lifecycle.is_active', 'graph_nbrs.get', 'math.cos', 'math.hypot', 'math.isfinite', 'math.sin', 'scores.get', 'self._build_grid', 'self._env_mode', 'self._graph_neighbors', 'self._grid_neighbors', 'self._report']
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: inside loop; loop body mutates [(540, 'self.velocities[uid]')]; on iteration >=2 those mutations precede the note, so the function-level n_before=0 does NOT prove pre-mutation per path. Args do not depend on mutations before the call in the same iteration, so a per-iteration preflight at loop-body start remains possible (class B-LOOP).

## B -> B-PROVEN-CANDIDATE — form/dell_matrix/spatial_authority.py:573 note_seed in settle

- args: ['5', "'Spatial'", "'settle budget exhausted: honestly non-convergent'"]
- mut_before(direct): [[568, "last['ticks_run']"], [569, "last['honestly_non_convergent']"], [571, "last['ticks_run']"], [572, "last['honestly_non_convergent']"]]
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: ['self.tick']
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: argument expressions do not depend on any direct mutation between the first mutation and the note call (no interval Name assignment, no attribute overlap, no non-whitelisted arg call); the same expressions evaluated before the first mutation yield the identical eventual text, so a preflight computing sanitize+canonical bytes from them is byte-exact against direct mutations (helper-call side effects UNKNOWN).

## B -> B-PROVEN-CANDIDATE — form/mandell/core_ii_exec.py:134 note_seed in mark

- args: ['n', 'term', '_lab_shown or term']
- mut_before(direct): [[131, 'st.traces.append'], [132, 'st.traces_dropped_total']]
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: []
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: argument expressions do not depend on any direct mutation between the first mutation and the note call (no interval Name assignment, no attribute overlap, no non-whitelisted arg call); the same expressions evaluated before the first mutation yield the identical eventual text, so a preflight computing sanitize+canonical bytes from them is byte-exact against direct mutations (helper-call side effects UNKNOWN).

## B -> B-PROVEN-CANDIDATE — form/open.py:487 note_seed in look_around

- args: ['9', "'Show'", "'look'"]
- mut_before(direct): [[479, 'self.inspire.last_multivision'], [480, "vision['multiscale']"], [484, "vision['vision_memory']"]]
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: ["(mv.get('layers') or {}).items", 'layer.get', 'mv.get', 'self.companion.to_dict', 'self.inspire.vision_mem.observe', 'self.nodes_payload']
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: argument expressions do not depend on any direct mutation between the first mutation and the note call (no interval Name assignment, no attribute overlap, no non-whitelisted arg call); the same expressions evaluated before the first mutation yield the identical eventual text, so a preflight computing sanitize+canonical bytes from them is byte-exact against direct mutations (helper-call side effects UNKNOWN).

## A -> A-PROVEN-DIRECT — form/open.py:594 note_seed in zoom_to

- args: ['15', "'Map'", "f'zoom_{ref}'"]
- mut_before(direct): []
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: ["(ref or '').strip", 'plane.zoom_in']
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: no direct mutation before the call in the enclosing function and no loop-carried mutation; door refusal is pre-mutation against direct mutations (helper-call side effects UNKNOWN).

## A -> A-PROVEN-DIRECT — form/open.py:599 note_seed in zoom_to

- args: ['15', "'Map'", "f'zoom_{uid}'"]
- mut_before(direct): []
- in_loop: True; loop_muts: []
- deps: []
- helper_calls_before: ["(ref or '').strip", 'plane.units.items', 'plane.zoom_in', 'ref.lower', 'self.page_card', 'u.label.lower']
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: no direct mutation before the call in the enclosing function and no loop-carried mutation; door refusal is pre-mutation against direct mutations (helper-call side effects UNKNOWN).

## A -> A-PROVEN-DIRECT — form/open.py:605 note_seed in unzoom

- args: ['15', "'Map'", "'unzoom'"]
- mut_before(direct): []
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: ['self.cube.session.plane.zoom_out']
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: no direct mutation before the call in the enclosing function and no loop-carried mutation; door refusal is pre-mutation against direct mutations (helper-call side effects UNKNOWN).

## B -> B-NOT-PROVEN — form/open.py:729 note_seed in set_ux_mode

- args: ['4', "'Transform'", "f'mode_{self.ux_mode}'"]
- mut_before(direct): [[728, 'self.ux_mode']]
- in_loop: False; loop_muts: []
- deps: ['arg attr self.ux_mode overlaps mutated self.ux_mode']
- helper_calls_before: []
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: noted text may depend on state mutated before the note: ['arg attr self.ux_mode overlaps mutated self.ux_mode']

## A -> A-PROVEN-DIRECT — form/open.py:778 note_seed in bimo_dock

- args: ['21', "'Merge'", "f'bimo_{slot}'"]
- mut_before(direct): []
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: ['out.get', 'self.bimo.dock']
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: no direct mutation before the call in the enclosing function and no loop-carried mutation; door refusal is pre-mutation against direct mutations (helper-call side effects UNKNOWN).

## A -> A-PROVEN-DIRECT — form/open.py:786 note_seed in bimo_defaults

- args: ['21', "'Merge'", "'bimo_defaults'"]
- mut_before(direct): []
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: ['self.bimo.dock_defaults']
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: no direct mutation before the call in the enclosing function and no loop-carried mutation; door refusal is pre-mutation against direct mutations (helper-call side effects UNKNOWN).

## B -> B-PROVEN-CANDIDATE — form/open.py:795 note_seed in bimo_fuse

- args: ['21', "'Merge'", "'bimo_fuse'"]
- mut_before(direct): [[793, 'self.persona_lens'], [794, 'self.persona_matrix.active']]
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: ['out.get', 'self.bimo.fuse']
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: argument expressions do not depend on any direct mutation between the first mutation and the note call (no interval Name assignment, no attribute overlap, no non-whitelisted arg call); the same expressions evaluated before the first mutation yield the identical eventual text, so a preflight computing sanitize+canonical bytes from them is byte-exact against direct mutations (helper-call side effects UNKNOWN).

## B -> B-PROVEN-CANDIDATE — form/open.py:806 note_seed in set_view

- args: ['9', "'Show'", "f'view_{room['id']}'"]
- mut_before(direct): [[805, 'self.active_view']]
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: []
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: argument expressions do not depend on any direct mutation between the first mutation and the note call (no interval Name assignment, no attribute overlap, no non-whitelisted arg call); the same expressions evaluated before the first mutation yield the identical eventual text, so a preflight computing sanitize+canonical bytes from them is byte-exact against direct mutations (helper-call side effects UNKNOWN).

## B -> B-PROVEN-CANDIDATE — form/open.py:887 note_seed in force_tick

- args: ['25', "'Pulse'", "'force_tick'"]
- mut_before(direct): [[878, "report['spatial']"], [880, "report['spatial']"], [884, "report['nature']"]]
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: ['self.forces.tick', 'self.nodes_payload', 'self.spatial.tick']
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: argument expressions do not depend on any direct mutation between the first mutation and the note call (no interval Name assignment, no attribute overlap, no non-whitelisted arg call); the same expressions evaluated before the first mutation yield the identical eventual text, so a preflight computing sanitize+canonical bytes from them is byte-exact against direct mutations (helper-call side effects UNKNOWN).

## A -> A-PROVEN-DIRECT — form/open.py:914 note_seed in force_growth

- args: ['25', "'Pulse'", "'force_growth'"]
- mut_before(direct): []
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: ['pl.get', 'self.cube.session.plane.units.values', 'self.forces.activate', 'self.forces.growth.grow_all', 'self.forces.growth.map', 'self.forces.growth.plant']
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: no direct mutation before the call in the enclosing function and no loop-carried mutation; door refusal is pre-mutation against direct mutations (helper-call side effects UNKNOWN).

## A -> A-PROVEN-DIRECT — form/open.py:927 note_seed in force_water

- args: ['25', "'Pulse'", "'force_water'"]
- mut_before(direct): []
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: ['self.cube.session.plane.units.values', 'self.forces.activate', 'self.forces.water.flow', 'self.forces.water.merge_last_two']
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: no direct mutation before the call in the enclosing function and no loop-carried mutation; door refusal is pre-mutation against direct mutations (helper-call side effects UNKNOWN).

## A -> A-PROVEN-DIRECT — form/open.py:939 note_seed in force_breath

- args: ['25', "'Pulse'", "'force_breath'"]
- mut_before(direct): []
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: ['self.forces.activate', 'self.forces.breath.heartbeat']
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: no direct mutation before the call in the enclosing function and no loop-carried mutation; door refusal is pre-mutation against direct mutations (helper-call side effects UNKNOWN).

## A -> A-PROVEN-DIRECT — form/open.py:947 note_seed in force_gravity

- args: ['25', "'Pulse'", "'force_gravity'"]
- mut_before(direct): []
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: ["', '.join", 'self.forces.activate', 'self.forces.gravity.set_wells_from_scores', 'self.nodes_payload']
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: no direct mutation before the call in the enclosing function and no loop-carried mutation; door refusal is pre-mutation against direct mutations (helper-call side effects UNKNOWN).

## A -> A-PROVEN-DIRECT — form/open.py:952 note_seed in set_weather

- args: ['25', "'Pulse'", "f'weather_{c}'"]
- mut_before(direct): []
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: ['self.forces.weather.set_condition']
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: no direct mutation before the call in the enclosing function and no loop-carried mutation; door refusal is pre-mutation against direct mutations (helper-call side effects UNKNOWN).

## B -> B-PROVEN-CANDIDATE — form/open.py:1011 note_seed in enter_workshop

- args: ['9', "'Show'", "f'workshop_{w['id']}'"]
- mut_before(direct): [[1010, 'self.active_workshop']]
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: []
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: argument expressions do not depend on any direct mutation between the first mutation and the note call (no interval Name assignment, no attribute overlap, no non-whitelisted arg call); the same expressions evaluated before the first mutation yield the identical eventual text, so a preflight computing sanitize+canonical bytes from them is byte-exact against direct mutations (helper-call side effects UNKNOWN).

## B -> B-PROVEN-CANDIDATE — form/open.py:1110 note_seed in set_lattice_size

- args: ['15', "'Map'", "f'size_{s}'"]
- mut_before(direct): [[1109, 'self.lattice.size']]
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: []
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: argument expressions do not depend on any direct mutation between the first mutation and the note call (no interval Name assignment, no attribute overlap, no non-whitelisted arg call); the same expressions evaluated before the first mutation yield the identical eventual text, so a preflight computing sanitize+canonical bytes from them is byte-exact against direct mutations (helper-call side effects UNKNOWN).

## A -> A-PROVEN-DIRECT — form/open.py:1116 note_seed in radial_drift

- args: ['16', "'Decay'", "f'drift_{outer_shell}'"]
- mut_before(direct): []
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: []
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: no direct mutation before the call in the enclosing function and no loop-carried mutation; door refusal is pre-mutation against direct mutations (helper-call side effects UNKNOWN).

## B -> B-PROVEN-CANDIDATE — form/open.py:1165 note_seed in place

- args: ['8', "'Create'", 'label']
- mut_before(direct): [[1136, 'self.spatial.place'], [1142, 'self.spatial.place'], [1148, 'u.detail'], [1151, 'u.goals']]
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: ['kwargs.get', 'self.cube.place_idea', 'self.keys.remember', 'self.lattice.rebuild_from_plane', 'self.sandbox.maybe_auto_box']
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: argument expressions do not depend on any direct mutation between the first mutation and the note call (no interval Name assignment, no attribute overlap, no non-whitelisted arg call); the same expressions evaluated before the first mutation yield the identical eventual text, so a preflight computing sanitize+canonical bytes from them is byte-exact against direct mutations (helper-call side effects UNKNOWN).

## B -> B-PROVEN-CANDIDATE — form/open.py:1221 note_seed in internet_on

- args: ['25', "'Pulse'", "'internet_on'"]
- mut_before(direct): [[1219, 'self.internet'], [1220, 'self.internet.turn_on']]
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: []
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: argument expressions do not depend on any direct mutation between the first mutation and the note call (no interval Name assignment, no attribute overlap, no non-whitelisted arg call); the same expressions evaluated before the first mutation yield the identical eventual text, so a preflight computing sanitize+canonical bytes from them is byte-exact against direct mutations (helper-call side effects UNKNOWN).

## B -> B-PROVEN-CANDIDATE — form/open.py:1228 note_seed in internet_off

- args: ['32', "'Pause'", "'internet_off'"]
- mut_before(direct): [[1227, 'self.internet.turn_off']]
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: []
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: argument expressions do not depend on any direct mutation between the first mutation and the note call (no interval Name assignment, no attribute overlap, no non-whitelisted arg call); the same expressions evaluated before the first mutation yield the identical eventual text, so a preflight computing sanitize+canonical bytes from them is byte-exact against direct mutations (helper-call side effects UNKNOWN).

## B -> B-NOT-PROVEN — form/open.py:1290 note_seed in set_auto_confirm_grow

- args: ['13', "'Loop'", "f'auto_confirm_grow_{('on' if self.auto_confirm_grow else 'off')}'"]
- mut_before(direct): [[1279, 'self.auto_confirm_grow']]
- in_loop: False; loop_muts: []
- deps: ['arg attr self.auto_confirm_grow overlaps mutated self.auto_confirm_grow']
- helper_calls_before: ['policy.grant_opt_in', 'policy.revoke_opt_in']
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: noted text may depend on state mutated before the note: ['arg attr self.auto_confirm_grow overlaps mutated self.auto_confirm_grow']

## A -> A-PROVEN-DIRECT — form/open.py:2052 note_seed in reject_proposal

- args: ['24', "'Unlock'", "'reject'"]
- mut_before(direct): []
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: ["' '.join", 'self.inspire.prefs.observe_reject', 'self.nursery.reject']
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: no direct mutation before the call in the enclosing function and no loop-carried mutation; door refusal is pre-mutation against direct mutations (helper-call side effects UNKNOWN).

## A -> A-PROVEN-DIRECT — form/open.py:2056 note_seed in sandbox_on

- args: ['23', "'Lock'", "'sandbox_on'"]
- mut_before(direct): []
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: []
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: no direct mutation before the call in the enclosing function and no loop-carried mutation; door refusal is pre-mutation against direct mutations (helper-call side effects UNKNOWN).

## A -> A-PROVEN-DIRECT — form/open.py:2063 note_seed in sandbox_off

- args: ['24', "'Unlock'", "'sandbox_off'"]
- mut_before(direct): []
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: []
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: no direct mutation before the call in the enclosing function and no loop-carried mutation; door refusal is pre-mutation against direct mutations (helper-call side effects UNKNOWN).

## B -> B-PROVEN-CANDIDATE — form/open.py:2068 note_seed in enhance_on

- args: ['25', "'Pulse'", "'enhance_on'"]
- mut_before(direct): [[2067, 'self.enhance.turn_on']]
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: []
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: argument expressions do not depend on any direct mutation between the first mutation and the note call (no interval Name assignment, no attribute overlap, no non-whitelisted arg call); the same expressions evaluated before the first mutation yield the identical eventual text, so a preflight computing sanitize+canonical bytes from them is byte-exact against direct mutations (helper-call side effects UNKNOWN).

## B -> B-PROVEN-CANDIDATE — form/open.py:2072 note_seed in enhance_off

- args: ['32', "'Pause'", "'enhance_off'"]
- mut_before(direct): [[2071, 'self.enhance.turn_off']]
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: []
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: argument expressions do not depend on any direct mutation between the first mutation and the note call (no interval Name assignment, no attribute overlap, no non-whitelisted arg call); the same expressions evaluated before the first mutation yield the identical eventual text, so a preflight computing sanitize+canonical bytes from them is byte-exact against direct mutations (helper-call side effects UNKNOWN).

## B -> B-PROVEN-CANDIDATE — form/open.py:2083 note_seed in pulse

- args: ['25', "'Pulse'"]
- mut_before(direct): [[2078, 'self.inspire.scores.push'], [2080, "out['slopes']"]]
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: ['self.enhance.pulse', 'self.inspire.scores.slopes', 'self.scores']
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: argument expressions do not depend on any direct mutation between the first mutation and the note call (no interval Name assignment, no attribute overlap, no non-whitelisted arg call); the same expressions evaluated before the first mutation yield the identical eventual text, so a preflight computing sanitize+canonical bytes from them is byte-exact against direct mutations (helper-call side effects UNKNOWN).

## B -> B-PROVEN-CANDIDATE — form/open.py:2098 note_seed in multilook

- args: ['9', "'Show'", "'multilook'"]
- mut_before(direct): [[2097, 'self.inspire.last_multivision']]
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: ['self.inspire.vision_mem.observe', 'self.nodes_payload']
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: argument expressions do not depend on any direct mutation between the first mutation and the note call (no interval Name assignment, no attribute overlap, no non-whitelisted arg call); the same expressions evaluated before the first mutation yield the identical eventual text, so a preflight computing sanitize+canonical bytes from them is byte-exact against direct mutations (helper-call side effects UNKNOWN).

## B -> B-PROVEN-CANDIDATE — form/open.py:2131 note_seed in attend

- args: ['9', "'Show'", "'attend'"]
- mut_before(direct): [[2109, 'docs.append'], [2120, 'docs.append'], [2130, 'self.inspire.last_attention']]
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: ["' '.join", "(query or '').strip", 'n.get', 'p.get', 'self.list_proposals', 'self.nodes_payload']
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: argument expressions do not depend on any direct mutation between the first mutation and the note call (no interval Name assignment, no attribute overlap, no non-whitelisted arg call); the same expressions evaluated before the first mutation yield the identical eventual text, so a preflight computing sanitize+canonical bytes from them is byte-exact against direct mutations (helper-call side effects UNKNOWN).

## A -> A-PROVEN-DIRECT — form/open.py:2152 note_seed in glyph

- args: ['9', "'Show'", "'glyph'"]
- mut_before(direct): []
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: ["(seed or self.owner or 'matrix').strip", 'label.lower', 'n.get', 'self.nodes_payload', "str(n.get('label') or '').lower"]
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: no direct mutation before the call in the enclosing function and no loop-carried mutation; door refusal is pre-mutation against direct mutations (helper-call side effects UNKNOWN).

## A -> A-PROVEN-DIRECT — form/open.py:2157 note_seed in run_script

- args: ['13', "'Loop'", "'script'"]
- mut_before(direct): []
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: []
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: no direct mutation before the call in the enclosing function and no loop-carried mutation; door refusal is pre-mutation against direct mutations (helper-call side effects UNKNOWN).

## A -> A-PROVEN-DIRECT — form/open.py:2166 note_seed in save

- args: ['10', "'Keep'"]
- mut_before(direct): []
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: []
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: no direct mutation before the call in the enclosing function and no loop-carried mutation; door refusal is pre-mutation against direct mutations (helper-call side effects UNKNOWN).

## A -> A-PROVEN-DIRECT — form/open.py:2171 note_seed in visual

- args: ['9', "'Show'", "'visual'"]
- mut_before(direct): []
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: []
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: no direct mutation before the call in the enclosing function and no loop-carried mutation; door refusal is pre-mutation against direct mutations (helper-call side effects UNKNOWN).

## A -> A-PROVEN-DIRECT — form/open.py:2191 note_seed in live_visual

- args: ['9', "'Show'", "'live_visual'"]
- mut_before(direct): []
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: []
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: no direct mutation before the call in the enclosing function and no loop-carried mutation; door refusal is pre-mutation against direct mutations (helper-call side effects UNKNOWN).

## A -> A-PROVEN-DIRECT — form/repl.py:419 note_seed in _handle_latinmandell

- args: ['45', "'Translate'", "'explain'"]
- mut_before(direct): []
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: ['lower.startswith', 'raw.split', 'rep.get']
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: no direct mutation before the call in the enclosing function and no loop-carried mutation; door refusal is pre-mutation against direct mutations (helper-call side effects UNKNOWN).

## B -> B-PROVEN-CANDIDATE — form/repl.py:483 note_seed in _handle_latinmandell

- args: ['14', "'Bind'", 'label[:24]']
- mut_before(direct): [[474, 'sense_parts.append']]
- in_loop: False; loop_muts: []
- deps: []
- helper_calls_before: ["' '.join", "' '.join(sense_parts).strip", 'c.get', 'lower.startswith', 'out.get', 'part.get', 'payload.get', 'r.get', 'raw.split', 'raw.split(maxsplit=1)[1].strip', 'rep.get', 'rest.split']
- eventual: note_seed: body=f"{dell:02d}[{term}]" + (" :: "+label[:40] if label) ; label sanitized first iff _chain_sanitize_redact (current) / always under R5 P5
- why: argument expressions do not depend on any direct mutation between the first mutation and the note call (no interval Name assignment, no attribute overlap, no non-whitelisted arg call); the same expressions evaluated before the first mutation yield the identical eventual text, so a preflight computing sanitize+canonical bytes from them is byte-exact against direct mutations (helper-call side effects UNKNOWN).

