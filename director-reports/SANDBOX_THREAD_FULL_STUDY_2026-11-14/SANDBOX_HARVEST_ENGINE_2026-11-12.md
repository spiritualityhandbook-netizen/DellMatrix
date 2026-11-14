# SANDBOX — THE HARVEST ENGINE: A VIBRATION/MAGNETIC-ERA CAR POWERTRAIN

Status: **SANDBOX** (opened by Ace, 2026-11-12, "please keep
it sandboxed"). Exploratory design research using DellMatrix
and Mandellistics as the design method. Nothing here is
pipeline work, product law, or an engineering claim about a
built artifact. It becomes more only if Ace promotes it.

Commission: develop a new car engine that runs off vibration
or some free source of energy — magnetic or something —
treating today's combustion car as primitive: it hurts the
planet to use and to fuel.

## THE HONESTY LOCK (read first, applies to every line below)

1. **Energy is never created.** Every joule the wheels spend
   entered the car from somewhere nameable. Any design whose
   ledger does not balance is not a design; it is a story.
2. **A magnet is a spring, not a meal.** A static magnetic
   field does no net work over a closed cycle; "magnetic
   motors" that run forever on magnets alone are the
   perpetual-motion claim wearing modern clothes, and they
   fail for the same reason all of them fail. Magnets in this
   sandbox are used where they honestly shine: **bearings and
   gearing that delete friction** — loss-killers, not sources.
3. **"Free energy" has exactly one honest meaning here:**
   energy that was *already paid for and is currently thrown
   away* (braking heat, suspension motion, engine waste heat,
   vibration), plus energy that arrives uninvited and unbilled
   (sunlight). The design goal is not a car that runs on
   nothing. It is **a car that wastes nothing** — and the
   distance between those two sentences is the whole sandbox.
4. Vibration in a moving car is mostly energy the motor
   already bought (road bumps are paid for by the wheels'
   work and the road). Harvesting it is RECOVERY, not
   creation — real, valuable, and bounded, which is exactly
   why it belongs in the ledger and not in a legend.

## WHERE A CAR'S ENERGY ACTUALLY GOES (the enemy, measured)

Orders of magnitude from the public engineering record
(approximate, hedged — the sandbox's starting map, not its
conclusions):

- A gasoline car turns only ~25–30% of fuel energy into
  wheel motion. The rest leaves as exhaust heat (~30%),
  coolant heat (~30%), friction, idling, accessories — and
  every stop throws the car's motion away as brake heat.
- An electric car is far thriftier (~3× the tank-to-wheel
  efficiency) but still bleeds: braking beyond what regen
  catches, rolling resistance, air drag, drivetrain and
  bearing friction, cabin loads, battery round-trip losses.
- The primitive part is not the motor. **The primitive part
  is the plumbing: one stream in, a dozen leaks out, no
  ledger anywhere.**

## THE HARVEST CHANNELS (each real, each with its true size)

| channel | mechanism | demonstrated size | verdict |
|---|---|---|---|
| Braking recovery | motor-as-generator (regen) | production EVs; recovers a large share of braking energy in city driving | GIANT — the main artery |
| Suspension recovery | regenerative shock absorbers (Levant Power GenShock; Audi eROT prototype) | ~100 W–1 kW peaks on rough roads; tens–hundreds of W typical | REAL — the vibration channel that matters |
| Road/tire vibration piezo | piezoelectric elements | milliwatts–watts | TRICKLE — powers sensors, never traction |
| Exhaust waste heat | thermoelectric generators (BMW/GM prototypes) | ~500 W–1 kW on combustion/hybrid | REAL where an exhaust exists |
| Solar skin | roof/body photovoltaics (Aptera, Lightyear claims; Hyundai solar roof) | up to ~1–2 kWh/day parked in sun (manufacturer claims, labeled) | REAL — the one truly unbilled input |
| Flywheel buffer | KERS-style mechanical storage | F1-proven; Volvo tests claimed up to ~20–25% city fuel savings (manufacturer claim) | REAL — storage that loses almost nothing at rest |
| Magnetic bearings/gears | contactless support & coupling | near-zero contact friction in service today (turbos, flywheels) | LOSS-KILLER — magnets' honest job |

The sizing verdict the table forces: **vibration alone will
never run a car** — the honest vibration channels pay in
hundreds of watts against a cruise demand of 10–20 kW. But
braking + suspension + solar + heat + lossless storage +
friction deletion, *integrated under one ledger*, is a
powertrain whose total loss profile no production car
currently attempts. The invention is not a new source.
**The invention is the integration and the ledger.**

## THE CONCEPT — HARVEST-CORE

An electric drive core wrapped in five recovery organs and
governed by a per-heartbeat energy ledger:

1. **Drive core:** high-efficiency electric motors on
   magnetic bearings; magnetic gear coupling where gearing
   is needed (no tooth contact, no gear oil drag).
2. **Brake organ:** full-authority regen first, friction
   brakes as the rare fallback — sized so city driving is
   nearly all recovered.
3. **Suspension organ:** every shock absorber is a
   generator; road roughness becomes charge instead of heat.
4. **Skin organ:** photovoltaic body panels feeding the bus
   whenever light exists, driving or parked.
5. **Heat organ (hybrid variant only):** thermoelectrics on
   any hot stream that remains.
6. **Two-store heart:** a flywheel for the fast in/out beats
   (brake, launch — near-lossless at rest, no chemistry) and
   a battery for the long store. Each store's losses are
   separate ledger lines.
7. **The Ledger (the DellMatrix organ):** every beat, the
   powertrain accounts energy in, energy stored, energy
   spent, energy lost — each loss *by name* (16[Decay]'s
   job). A car that cannot show its ledger cannot claim its
   efficiency. Profile (49) is the speedometer of this car:
   not how fast it goes, but how little it wastes per mile —
   drag measured Ace's way, as loss of function, not noise.

## THE ENGINE'S SEED (verified Mandell, 12 atoms, parse-clean)

The operating cycle, one heartbeat of the Harvest-Core:

```
35[Discover]:: scan every waste stream
62[Parallel]:: harvest all channels at once
04[Transform]:: convert each stream to charge
21[Merge]:: one bus, one ledger
10[Keep]:: store the surplus
19[Drive]:: spend on motion
16[Decay]:: account every loss by name
71[Measure]:: net balance for this beat
60[Branch]:: surplus banks deeper, deficit draws the store
06[Cycle]:: next heartbeat
92[Guard]:: never claim more out than came in
90[Trace]:: the full energy ledger, always
```

Bilingual gloss, step by step: Discover finds every stream
currently escaping. Parallel runs all harvest organs at
once — they never take turns. Transform converts each
stream (motion, heat, light) into the one currency, charge.
Merge puts every channel on one bus under one ledger. Keep
banks what the moment doesn't need. Drive spends on the
only job: motion. Decay — the honest step most machines
skip — names every loss as it happens. Measure closes the
beat's books. Branch routes surplus to deeper storage and
deficit to the stores. Cycle beats again. Guard is the
honesty lock as a Dell: the books may never show more out
than in. Trace keeps the whole ledger provable, forever.

Verification: parsed with the production seed parser
against the live registry in this session — 12 atoms, all
canonical (confidence 1.0), seed OK.

## WHAT WOULD KILL IT (falsification, written in advance)

- If an integrated bench build's measured recovery total
  falls below the sum of its parts' standalone recoveries by
  more than integration overhead explains, the integration
  thesis dies (the whole is not greater; it's just heavier).
- If suspension harvesting at realistic road profiles nets
  < 25 W average per corner after its own mass penalty, the
  suspension organ is demoted to sensor-power duty.
- If the flywheel's real standby + cycling losses exceed the
  battery's for the brake/launch duty cycle, the two-store
  heart collapses to one store.
- The concept as a whole dies the day its full ledger —
  including manufacturing energy, which this sandbox has
  NOT yet counted — shows a worse lifetime balance than the
  EV it replaces. The planet judges the whole ledger or
  none of it.

## OPEN DOORS (next sandbox sittings, Ace's choice)

- Count the manufacturing ledger (the "to make" half of
  Ace's commission: it hurts the planet to MAKE, not only
  to fuel).
- Give the ledger a Dell-by-Dell design pass per organ
  (each organ gets its own seed, notebook-style).
- The magnetic-gear deep dive: what contactless gearing
  actually costs at car scale.
- Numbers sitting: model one full city drive cycle through
  the seed, joule by joule, on paper.
