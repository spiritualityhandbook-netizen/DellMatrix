# Director Report — B-2 Reachability Validation (G-02)

Status: SUBMITTED (Uni evidence; certification is the Director's)
Base: main 843a44c5d63f8b0c6359c4f57764a3851eb16d68 (TD-2 merge)
Date: 2026-11-04 (SUSX100,000 sleep run, Cycle 6)
SWAT calibration: proportionate falsification — B-2 is a
read-only investigation over `translate()`; no stateful or
cross-cutting mechanism is built. Choice recorded per Ace's
2026-11-04 calibration.

## Question

The SM-14 census (PR #280 evidence, P4 investigations) found
37/100 Dells reachable in English and 63 NO_ROUTE_FOUND, a
bounded claim: translate() carries hardcoded families keyed to
domain vocabulary the census battery may have missed, and
per-Dell verb aliases were unexplored. B-2 was held PROVISIONAL
pending per-Dell evidence. This circuit supplies it.

## Method (uniform, disclosed, no per-Dell hand-tuning)

For each of the 63 NO_ROUTE_FOUND Dells, probe v2
(`b2_deep_probe.py`, preserved in the goal working papers with
its full JSON output) ran three tiers through the real
`translate()` at the base above:

- **Tier S (static):** translate.py + phrases.py source scanned
  for the Dell's seed token `N[` and its registry name as a word.
- **Tier M (manor verbs):** verbs extracted mechanically from
  the Dell's own registry "manor" string, plus the Dell name;
  frames "{v} testitem", "{v} the testitem", "please {v}
  testitem", "{v}".
- **Tier N (name forms):** "{name} the testitem", "use {name}",
  "use {name} on testitem", "do {name}", "{name} on testitem",
  "{name}s testitem", "{name}ing testitem".

Routing rule identical to SM-14 (Intent.dell, or the produced
seed's primary / any chain segment head equals the target).
1,694 phrases tried across the 63 Dells; 0 translate() errors;
misroutes recorded per phrase in the JSON.

## Positive control (the probe is not vacuous)

The identical probe run against known-reachable Dells finds
routes: 8 Create ("create testitem"), 12 Test ("test
testitem"), 51 Select ("select testitem"), and 28 Rollback via
its manor verb "restore" ("restore testitem") — a catch the
SM-14 name battery alone would not have made. A probe that can
find routes where they exist is evidence when it finds none.

## Result

**Route found deep: 0 of 63.** All 63 remain STILL_NO_ROUTE
after the deep tiers: 0 Nova, 1 Initiate, 2 Persona, 3 Logic,
16 Decay, 17 Shadow, 18 Mirror, 20 Alpha, 22 Split, 26 Temp,
30 Expand, 33 Resume, 36 Inject, 39 Schema, 41 Sanitize,
43 Fallback, 44 Bridge, 45 Translate, 49 Profile, 52 Filter,
53 Scope, 54 Query, 55 Set, 57 Compare, 59 Route, 60 Branch,
61 Join, 62 Parallel, 63 Sequence, 64 Until, 65 While,
66 ForEach, 67 Any, 68 All, 69 None, 70 Count, 71 Measure,
72 Limit, 73 Threshold, 74 Weight, 75 Normalize, 76 Resolve,
77 Infer, 78 Cause, 79 Depend, 80 Context, 81 Reference,
82 Group, 83 Ungroup, 85 Move, 87 Replace, 88 Patch, 89 Diff,
90 Trace, 91 Assert, 92 Guard, 93 Try, 94 Catch, 95 Commit,
96 Revert, 97 Define, 98 Alias, 99 Compose.

Static nuance, stated plainly: 28 of the 63 have a name-word
mention in translate.py/phrases.py source, but a mention is not
a route (comments, other Dells' templates, self-reference —
Dell 45 is translate()'s own module). Only Dell 45 carries a
seed-token hit among the 63, in its own translator module, and
no live phrase routes to it. The live tiers are the evidence;
the static tier bounds what code even names.

## Bounded claim

The 63 are true English-reachability gaps **relative to the
combined evidence**: SM-14 tiers (PHRASES table + name battery
+ 74 generic frames) plus B-2 tiers M/N (1,694 phrases) plus
Tier S static scan. This is not a proof that no conceivable
English sentence routes to them; it is per-Dell evidence that
no route exists through the vocabulary these Dells' own names,
manors, and the program's generic command frames supply. Any
future claim of a route for one of these Dells should name its
phrase — the probe reruns deterministically.

## Disposition requested

B-2's queue is validated: the 63 above, and only these, are
the English-reachability gap set. No Dell is promoted to an
implementation queue by this report — adding English routes is
implementation, a separate authorization. Uni's recommendation:
route-adding, if authorized, should be smallest-scope first
(Core I spine 0, 1, 2, 3, 16–20, 22, 26, 30, 33, 36, 39, 41,
43–45, 49 before Core II 52–99), one bounded circuit per batch,
each route proven through translate() with failing-first tests.

## Anticipated probes

- *Why not probe arbitrary synonyms (a thesaurus)?* The manor
  string is the program's own canonical semantic vocabulary
  for each Dell; a thesaurus would import vocabulary the
  program never claimed. If the Director wants a thesaurus
  tier, it is a disclosed extension, not a silent widening.
- *Does STILL_NO_ROUTE mean the Dell is unreachable at all?*
  No. Every Dell remains reachable by direct Mandell seed
  (e.g. `52[Filter …]`) and through the REPL paths TD-1/TD-2
  exercised. The gap is English-only, exactly as censused.

## Questions for the Director

- Q1: Is B-2's validation accepted as closing G-02's
  investigation, with route-adding as a separate circuit
  requiring its own authorization?
- Q2: If route-adding is authorized later, does the Director
  concur with Core-I-first batching, or should priority follow
  the Master Objective Register order instead?
