# R5-D SIDE-EFFECT INVENTORY — buildable A/B sites

Prepared 2026-11-19 (susx100000-execution), answering Director
7031447110: explicit side-effect inventories for the proposed
first bounded A/B subset. Source: r5d_path_proofs.jsonl
(aeb862f). Classification is CONSERVATIVE: anything not
provably pure from the call expression + grounded mutator
spot-checks is UNKNOWN and BLOCKS the side-effect-free claim
for its site. Records/evidence only; ZERO product code.

## Site verdicts: {'INVENTORY-CLEAN': 25, 'INVENTORY-ORDER-SENSITIVE': 3, 'INVENTORY-BLOCKED': 32}
## Helper-call classes (all occurrences): {'PURE_KNOWN': 82, 'ORDER_SENSITIVE': 3, 'MUTATING_KNOWN': 41, 'UNKNOWN': 25}

## INVENTORY-ORDER-SENSITIVE — form/dell_matrix/allwhere.py:289 birth_character (note, B-PROVEN-CANDIDATE, in_loop=False)
- PURE_KNOWN: `city.towns.values`
- PURE_KNOWN: `hashlib.sha1`
- PURE_KNOWN: `hashlib.sha1(name.encode()).hexdigest`
- PURE_KNOWN: `interests[0].title`
- PURE_KNOWN: `name.encode`
- ORDER_SENSITIVE: `rng.randint`
- PURE_KNOWN: `town.rooms.values`
- PURE_KNOWN: `world.cities.items`

## INVENTORY-BLOCKED — form/dell_matrix/allwhere.py:327 start_travel (note, B-PROVEN-CANDIDATE, in_loop=False)
- MUTATING_KNOWN: `ch.abilities['traveling'].use`
- PURE_KNOWN: `world.cities.values`

## INVENTORY-CLEAN — form/dell_matrix/allwhere.py:382 enter_room (note, B-PROVEN-CANDIDATE, in_loop=False)
- PURE_KNOWN: `town.rooms.get`

## INVENTORY-BLOCKED — form/dell_matrix/allwhere.py:387 enter_room (note, B-PROVEN-CANDIDATE, in_loop=False)
- UNKNOWN: `room.look`
- PURE_KNOWN: `town.rooms.get`

## INVENTORY-CLEAN — form/dell_matrix/allwhere.py:417 source_post (note, A-PROVEN-DIRECT, in_loop=False)
- helpers: none

## INVENTORY-CLEAN — form/dell_matrix/allwhere.py:475 activate_mission (note, B-PROVEN-CANDIDATE, in_loop=True)
- helpers: none

## INVENTORY-BLOCKED — form/dell_matrix/allwhere.py:491 check_missions (note, B-PROVEN-CANDIDATE, in_loop=True)
- MUTATING_KNOWN: `ch.abilities['navigation'].use`

## INVENTORY-BLOCKED — form/dell_matrix/allwhere.py:496 check_missions (note, B-PROVEN-CANDIDATE, in_loop=True)
- MUTATING_KNOWN: `ch.abilities['navigation'].use`

## INVENTORY-BLOCKED — form/dell_matrix/allwhere.py:503 check_missions (note, B-PROVEN-CANDIDATE, in_loop=True)
- MUTATING_KNOWN: `ch.abilities['navigation'].use`
- PURE_KNOWN: `town.rooms.get`

## INVENTORY-CLEAN — form/dell_matrix/code_evolution.py:76 ensure_root (note_seed, B-PROVEN-CANDIDATE, in_loop=False)
- PURE_KNOWN: `catalog.get`
- PURE_KNOWN: `idea.get`
- PURE_KNOWN: `skin_map.get`

## INVENTORY-BLOCKED — form/dell_matrix/code_evolution.py:201 research_with_internet (note_seed, B-PROVEN-CANDIDATE, in_loop=False)
- PURE_KNOWN: `n.get`
- MUTATING_KNOWN: `net.research_topic`
- PURE_KNOWN: `program.cube.session.plane.units.get`
- PURE_KNOWN: `r.get`
- PURE_KNOWN: `time.strftime`

## INVENTORY-CLEAN — form/dell_matrix/code_evolution.py:254 mark_complete (note_seed, B-PROVEN-CANDIDATE, in_loop=False)
- PURE_KNOWN: `checklist.get`
- PURE_KNOWN: `program.cube.session.plane.units.get`
- PURE_KNOWN: `time.gmtime`
- PURE_KNOWN: `time.strftime`

## INVENTORY-BLOCKED — form/dell_matrix/first_person.py:511 move_fp (note_seed, B-PROVEN-CANDIDATE, in_loop=False)
- PURE_KNOWN: `(direction or 'forward').lower`
- MUTATING_KNOWN: `program._push_user_trail`
- MUTATING_KNOWN: `program.apply_grid_snap`

## INVENTORY-BLOCKED — form/dell_matrix/first_person.py:523 turn_fp (note_seed, A-PROVEN-DIRECT, in_loop=False)
- MUTATING_KNOWN: `program.avatar.face`

## INVENTORY-CLEAN — form/dell_matrix/first_person.py:537 look_fp (note_seed, B-PROVEN-CANDIDATE, in_loop=False)
- PURE_KNOWN: `(pitch or 'level').lower`

## INVENTORY-CLEAN — form/dell_matrix/fourier.py:199 program_fourier_demo (note_seed, A-PROVEN-DIRECT, in_loop=False)
- helpers: none

## INVENTORY-CLEAN — form/dell_matrix/linear_algebra.py:192 program_transform (note_seed, A-PROVEN-DIRECT, in_loop=False)
- PURE_KNOWN: `(kind or 'rotate').lower`
- PURE_KNOWN: `Mat2.identity`
- PURE_KNOWN: `Mat2.rotate`
- PURE_KNOWN: `Mat2.scale`
- PURE_KNOWN: `Mat2.shear_x`

## INVENTORY-BLOCKED — form/dell_matrix/matrices_hub.py:115 evolve_program (note_seed, B-PROVEN-CANDIDATE, in_loop=False)
- MUTATING_KNOWN: `program.forces.tick`
- UNKNOWN: `program.nodes_payload`

## INVENTORY-ORDER-SENSITIVE — form/dell_matrix/needs.py:132 set_detail (note_seed, B-PROVEN-CANDIDATE, in_loop=False)
- PURE_KNOWN: `(detail or '').strip`
- PURE_KNOWN: `(u.words or '').strip`
- ORDER_SENSITIVE: `time.time`

## INVENTORY-ORDER-SENSITIVE — form/dell_matrix/needs.py:144 set_goals (note_seed, B-PROVEN-CANDIDATE, in_loop=False)
- PURE_KNOWN: `g.strip`
- PURE_KNOWN: `re.split`
- ORDER_SENSITIVE: `time.time`

## INVENTORY-BLOCKED — form/dell_matrix/needs.py:533 redo_last (note_seed, B-PROVEN-CANDIDATE, in_loop=False)
- PURE_KNOWN: `act.get`
- PURE_KNOWN: `plane.sandboxes.values`
- MUTATING_KNOWN: `plane.unbox`
- PURE_KNOWN: `record.get`

## INVENTORY-BLOCKED — form/dell_matrix/spatial_authority.py:473 tick (note_seed, A-DOWNGRADED-B-LOOP, in_loop=True)
- UNKNOWN: `canonical_lifecycle.is_active`
- PURE_KNOWN: `math.isfinite`
- MUTATING_KNOWN: `self._build_grid`
- UNKNOWN: `self._env_mode`
- UNKNOWN: `self._graph_neighbors`
- UNKNOWN: `self._report`
- UNKNOWN: `self._scores`
- UNKNOWN: `self._wells`

## INVENTORY-BLOCKED — form/dell_matrix/spatial_authority.py:530 tick (note_seed, A-DOWNGRADED-B-LOOP, in_loop=True)
- UNKNOWN: `canonical_lifecycle.is_active`
- PURE_KNOWN: `graph_nbrs.get`
- PURE_KNOWN: `math.cos`
- PURE_KNOWN: `math.hypot`
- PURE_KNOWN: `math.isfinite`
- PURE_KNOWN: `math.sin`
- PURE_KNOWN: `scores.get`
- MUTATING_KNOWN: `self._build_grid`
- UNKNOWN: `self._env_mode`
- UNKNOWN: `self._graph_neighbors`
- UNKNOWN: `self._grid_neighbors`
- UNKNOWN: `self._report`

## INVENTORY-BLOCKED — form/dell_matrix/spatial_authority.py:573 settle (note_seed, B-PROVEN-CANDIDATE, in_loop=False)
- MUTATING_KNOWN: `self.tick`

## INVENTORY-CLEAN — form/mandell/core_ii_exec.py:134 mark (note_seed, B-PROVEN-CANDIDATE, in_loop=False)
- helpers: none

## INVENTORY-BLOCKED — form/open.py:487 look_around (note_seed, B-PROVEN-CANDIDATE, in_loop=False)
- PURE_KNOWN: `(mv.get('layers') or {}).items`
- PURE_KNOWN: `layer.get`
- PURE_KNOWN: `mv.get`
- UNKNOWN: `self.companion.to_dict`
- MUTATING_KNOWN: `self.inspire.vision_mem.observe`
- UNKNOWN: `self.nodes_payload`

## INVENTORY-BLOCKED — form/open.py:594 zoom_to (note_seed, A-PROVEN-DIRECT, in_loop=False)
- PURE_KNOWN: `(ref or '').strip`
- MUTATING_KNOWN: `plane.zoom_in`

## INVENTORY-BLOCKED — form/open.py:599 zoom_to (note_seed, A-PROVEN-DIRECT, in_loop=True)
- PURE_KNOWN: `(ref or '').strip`
- PURE_KNOWN: `plane.units.items`
- MUTATING_KNOWN: `plane.zoom_in`
- PURE_KNOWN: `ref.lower`
- UNKNOWN: `self.page_card`
- PURE_KNOWN: `u.label.lower`

## INVENTORY-BLOCKED — form/open.py:605 unzoom (note_seed, A-PROVEN-DIRECT, in_loop=False)
- MUTATING_KNOWN: `self.cube.session.plane.zoom_out`

## INVENTORY-BLOCKED — form/open.py:778 bimo_dock (note_seed, A-PROVEN-DIRECT, in_loop=False)
- PURE_KNOWN: `out.get`
- MUTATING_KNOWN: `self.bimo.dock`

## INVENTORY-BLOCKED — form/open.py:786 bimo_defaults (note_seed, A-PROVEN-DIRECT, in_loop=False)
- MUTATING_KNOWN: `self.bimo.dock_defaults`

## INVENTORY-BLOCKED — form/open.py:795 bimo_fuse (note_seed, B-PROVEN-CANDIDATE, in_loop=False)
- PURE_KNOWN: `out.get`
- MUTATING_KNOWN: `self.bimo.fuse`

## INVENTORY-CLEAN — form/open.py:806 set_view (note_seed, B-PROVEN-CANDIDATE, in_loop=False)
- helpers: none

## INVENTORY-BLOCKED — form/open.py:887 force_tick (note_seed, B-PROVEN-CANDIDATE, in_loop=False)
- MUTATING_KNOWN: `self.forces.tick`
- UNKNOWN: `self.nodes_payload`
- MUTATING_KNOWN: `self.spatial.tick`

## INVENTORY-BLOCKED — form/open.py:914 force_growth (note_seed, A-PROVEN-DIRECT, in_loop=False)
- PURE_KNOWN: `pl.get`
- PURE_KNOWN: `self.cube.session.plane.units.values`
- MUTATING_KNOWN: `self.forces.activate`
- MUTATING_KNOWN: `self.forces.growth.grow_all`
- MUTATING_KNOWN: `self.forces.growth.map`
- MUTATING_KNOWN: `self.forces.growth.plant`

## INVENTORY-BLOCKED — form/open.py:927 force_water (note_seed, A-PROVEN-DIRECT, in_loop=False)
- PURE_KNOWN: `self.cube.session.plane.units.values`
- MUTATING_KNOWN: `self.forces.activate`
- MUTATING_KNOWN: `self.forces.water.flow`
- MUTATING_KNOWN: `self.forces.water.merge_last_two`

## INVENTORY-BLOCKED — form/open.py:939 force_breath (note_seed, A-PROVEN-DIRECT, in_loop=False)
- MUTATING_KNOWN: `self.forces.activate`
- MUTATING_KNOWN: `self.forces.breath.heartbeat`

## INVENTORY-BLOCKED — form/open.py:947 force_gravity (note_seed, A-PROVEN-DIRECT, in_loop=False)
- PURE_KNOWN: `', '.join`
- MUTATING_KNOWN: `self.forces.activate`
- MUTATING_KNOWN: `self.forces.gravity.set_wells_from_scores`
- UNKNOWN: `self.nodes_payload`

## INVENTORY-BLOCKED — form/open.py:952 set_weather (note_seed, A-PROVEN-DIRECT, in_loop=False)
- MUTATING_KNOWN: `self.forces.weather.set_condition`

## INVENTORY-CLEAN — form/open.py:1011 enter_workshop (note_seed, B-PROVEN-CANDIDATE, in_loop=False)
- helpers: none

## INVENTORY-CLEAN — form/open.py:1110 set_lattice_size (note_seed, B-PROVEN-CANDIDATE, in_loop=False)
- helpers: none

## INVENTORY-CLEAN — form/open.py:1116 radial_drift (note_seed, A-PROVEN-DIRECT, in_loop=False)
- helpers: none

## INVENTORY-BLOCKED — form/open.py:1165 place (note_seed, B-PROVEN-CANDIDATE, in_loop=False)
- PURE_KNOWN: `kwargs.get`
- MUTATING_KNOWN: `self.cube.place_idea`
- MUTATING_KNOWN: `self.keys.remember`
- MUTATING_KNOWN: `self.lattice.rebuild_from_plane`
- MUTATING_KNOWN: `self.sandbox.maybe_auto_box`

## INVENTORY-CLEAN — form/open.py:1221 internet_on (note_seed, B-PROVEN-CANDIDATE, in_loop=False)
- helpers: none

## INVENTORY-CLEAN — form/open.py:1228 internet_off (note_seed, B-PROVEN-CANDIDATE, in_loop=False)
- helpers: none

## INVENTORY-BLOCKED — form/open.py:2052 reject_proposal (note_seed, A-PROVEN-DIRECT, in_loop=False)
- PURE_KNOWN: `' '.join`
- MUTATING_KNOWN: `self.inspire.prefs.observe_reject`
- MUTATING_KNOWN: `self.nursery.reject`

## INVENTORY-CLEAN — form/open.py:2056 sandbox_on (note_seed, A-PROVEN-DIRECT, in_loop=False)
- helpers: none

## INVENTORY-CLEAN — form/open.py:2063 sandbox_off (note_seed, A-PROVEN-DIRECT, in_loop=False)
- helpers: none

## INVENTORY-CLEAN — form/open.py:2068 enhance_on (note_seed, B-PROVEN-CANDIDATE, in_loop=False)
- helpers: none

## INVENTORY-CLEAN — form/open.py:2072 enhance_off (note_seed, B-PROVEN-CANDIDATE, in_loop=False)
- helpers: none

## INVENTORY-BLOCKED — form/open.py:2083 pulse (note_seed, B-PROVEN-CANDIDATE, in_loop=False)
- UNKNOWN: `self.enhance.pulse`
- UNKNOWN: `self.inspire.scores.slopes`
- UNKNOWN: `self.scores`

## INVENTORY-BLOCKED — form/open.py:2098 multilook (note_seed, B-PROVEN-CANDIDATE, in_loop=False)
- MUTATING_KNOWN: `self.inspire.vision_mem.observe`
- UNKNOWN: `self.nodes_payload`

## INVENTORY-BLOCKED — form/open.py:2131 attend (note_seed, B-PROVEN-CANDIDATE, in_loop=False)
- PURE_KNOWN: `' '.join`
- PURE_KNOWN: `(query or '').strip`
- PURE_KNOWN: `n.get`
- PURE_KNOWN: `p.get`
- UNKNOWN: `self.list_proposals`
- UNKNOWN: `self.nodes_payload`

## INVENTORY-BLOCKED — form/open.py:2152 glyph (note_seed, A-PROVEN-DIRECT, in_loop=False)
- PURE_KNOWN: `(seed or self.owner or 'matrix').strip`
- PURE_KNOWN: `label.lower`
- PURE_KNOWN: `n.get`
- UNKNOWN: `self.nodes_payload`
- PURE_KNOWN: `str(n.get('label') or '').lower`

## INVENTORY-CLEAN — form/open.py:2157 run_script (note_seed, A-PROVEN-DIRECT, in_loop=False)
- helpers: none

## INVENTORY-CLEAN — form/open.py:2166 save (note_seed, A-PROVEN-DIRECT, in_loop=False)
- helpers: none

## INVENTORY-CLEAN — form/open.py:2171 visual (note_seed, A-PROVEN-DIRECT, in_loop=False)
- helpers: none

## INVENTORY-CLEAN — form/open.py:2191 live_visual (note_seed, A-PROVEN-DIRECT, in_loop=False)
- helpers: none

## INVENTORY-CLEAN — form/repl.py:419 _handle_latinmandell (note_seed, A-PROVEN-DIRECT, in_loop=False)
- PURE_KNOWN: `lower.startswith`
- PURE_KNOWN: `raw.split`
- PURE_KNOWN: `rep.get`

## INVENTORY-CLEAN — form/repl.py:483 _handle_latinmandell (note_seed, B-PROVEN-CANDIDATE, in_loop=False)
- PURE_KNOWN: `' '.join`
- PURE_KNOWN: `' '.join(sense_parts).strip`
- PURE_KNOWN: `c.get`
- PURE_KNOWN: `lower.startswith`
- PURE_KNOWN: `out.get`
- PURE_KNOWN: `part.get`
- PURE_KNOWN: `payload.get`
- PURE_KNOWN: `r.get`
- PURE_KNOWN: `raw.split`
- PURE_KNOWN: `raw.split(maxsplit=1)[1].strip`
- PURE_KNOWN: `rep.get`
- PURE_KNOWN: `rest.split`
