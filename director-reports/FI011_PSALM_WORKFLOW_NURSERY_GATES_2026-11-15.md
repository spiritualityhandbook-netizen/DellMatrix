# FI-011 — PSALM WORKFLOW + NURSERY AUTO-CONFIRM GATES

Feature Intake under the FI-002 law (Ace ruling, 2026-11-14): logged the
moment stated, numbered, mirrored against the whole plan, fully developed
to execution-ready standard, placed, done-defined. NOT built — this is
intake, development, and placement only.

## Ace's words (2026-11-15 15:00 CST)

"Also go ahead and add workflow to the Dellmatrix in psalm matrix. Where
you can add automatic workflows that work hand in hand with set automatic
gates in the nursery that allow users to allow certain tasks, tools,
logic, happenings to automatically get confirmation in the nursery. This
is flexible yet strict so that only what is wanted goes through."

"Don't just create it now — put it in its proper place in the grand plan
and perform all the grand plan standards. Mirroring, consideration,
planning, ordering, etc. — and this is the way all new ideas are supposed
to be implemented."

## The feature, in one paragraph

A **WORKFLOW** (Psalm Matrix) is a named automatic sequence the user can
define and watch: a trigger (a happening, a schedule, a condition) runs
steps (tasks, tool uses, Dell chains / logic), and what it produces lands
in the Nursery as proposals. A **GATE** (Nursery) is a standing rule the
USER sets: proposals matching ALL of the gate's conditions confirm
automatically; everything else stays PENDING for the user's own hand.
The two work hand in hand — workflows produce, gates decide what passes —
and neither carries the other's authority: a workflow can never confirm
its own output, and a gate confirms only what the user declared in
advance. Default is deny. Matching is strict. Only what is wanted goes
through.

## Objects

- **Gate** — {id, name, owner, conditions, placement, state
  (active / suspended), created-by, created-at, history}. Conditions are
  deterministic predicates over: kind / task type; tool; logic (Dell ids
  and chain shapes); happening / event class; origin (which Psalm,
  persona, workflow, or system source produced the item); size and scope
  bounds. Every gate restates itself in one plain-language sentence the
  user reads before setting it ("Items from Workflow X, kind Y, under N
  chars, confirm into the sandbox").
- **Workflow** — {id, name, trigger, steps (task / tool / logic
  references), outputs → Nursery, state}. A workflow definition is data
  the user owns; executing it produces PENDING proposals, never
  confirmations.
- **AutoConfirmReceipt** — {item id, gate id, the exact conditions
  matched, workflow id (when applicable), timestamp, reversal pointer}.
  One receipt per auto-confirmation, visible in the Nursery and in the
  Psalm Matrix live feed.

## MIRRORING — the feature against the whole plan

1. **Freedom Clause / sovereignty at the gate** (Afterplan; Grand Plan
   Psalm Matrix stage): the Nursery confirm gate is where human
   sovereignty lives — "the human companion lets AI happenings through
   VIA THE NURSERY." FI-011 does NOT move or dissolve that gate. A gate
   is a human decision made in advance: what changes is WHEN the human
   decides (at rule-setting time instead of item time), never WHO
   decides. Sovereignty at the gate is preserved by construction.
2. **C5 replan + C5.Door (MWL 143) + the AI hard line**: the docked AI
   never confirms, rejects, deletes, or lands anything. PRESERVED: gates
   can be created, edited, suspended, or revoked ONLY by the user's own
   hand at a user surface. A Psalm may PROPOSE a gate — as a PENDING
   suggestion object riding C5R.6's AI-organizer suggestion machinery —
   and a proposed gate has no force until the user sets it. An
   auto-confirmation executes the USER's standing rule, never the AI's
   judgment.
3. **Gemini Command Doctrine** (Psalm output is PENDING only): FI-011
   refines it under Ace's authority — PENDING remains the default for
   everything a Psalm produces; gate-matched items confirm under a user
   gate, with the receipt naming the gate. This touches doctrine, so it
   is asked, not assumed: **Q-FI011.1** to the Director before any build.
4. **Placement law (Q-U.4)**: a user confirming a mixed-wall proposal by
   hand is asked placement each time; AUTO placement goes to the SANDBOX
   FIRST. A gate declares its placement; an automatic placement defaults
   to the sandbox staging box unless the gate itself names the wall the
   user chose while setting it. No gate may silently place onto a wall
   the user did not name in the gate. (**Q-FI011.3**, Ace, non-blocking:
   confirm this default.)
5. **Hard-law precedence** (information/influence integrity; AGENTS
   §7/§19): explicit user choice cannot bypass hard eligibility or
   safety laws. Categories barred by hard law are UNGATEABLE — the gate
   editor refuses them by name. Gates operate only inside the space hard
   law leaves open. (**Q-FI011.2** to the Director: the ungateable list.)
6. **Witness Law** (Psalm Matrix): every layer witnessable; witnessing
   is a read, never a mutation path. Every auto-confirmation appears in
   the live feed and on its receipt — auto-confirm is never silent.
7. **C5 dependency and storage**: gates act on Nursery proposals, so the
   gate half requires C5R.5 MANAGE (confirm mechanics, tombstones,
   reversibility) and follows C5R.6 AI ORGANIZER (whose suggestion
   objects are the proposal path for gates). Gate objects live in the
   Nursery's OWN store as user configuration — the C5R.3 in-store
   metadata ruling applied to configuration. An auto-confirmation can be
   un-done by the user; the reversal is a tombstone event on the
   receipt, never a silent rewrite of history.
8. **Elastic limits (FI-004)**: no arbitrary cap on the number of gates
   or workflows; the stores grow on demand.
9. **FI-006 / FI-008**: FI-011 enters the interaction-exploration
   register (pairs and triples with Nursery, Dock, Psalm Matrix,
   confirm_lineage, persona matrix), each combination carrying an
   exploration state; the compare / clash / differ /
   hidden-in-combinations inquiry was re-asked at this intake (this
   section is its record) and is re-asked at every synchronization.
10. **FI-009 fitness**: the matching semantics are chosen for DellMatrix
    fitness and receipted here — STRICT CONJUNCTION (every declared
    condition must match), default-deny, deterministic predicates only.
    An AI may propose a gate; an AI never EVALUATES whether an item
    matches one. A gate that "sort of matches" is a hole, and strictness
    is the feature Ace named: "only what is wanted goes through."
11. **Name discipline**: this product feature is PSALM WORKFLOW. It is
    not THE GRAND WORKFLOW (the engineering pipeline) and not WORKFLOW
    v1 (the authority workflow). Records always use the full name.
12. **Kill switch**: the user can suspend ALL gates in one action,
    receipted; suspension deletes nothing — gates and their history
    remain readable while suspended.

## Placement and ordering

- **Gate half**: a Nursery capability in the C5 lineage — sequenced
  AFTER C5R.5 MANAGE and C5R.6 AI ORGANIZER (Grand Plan §14.4 C5 line).
  Buildable and provable at the Nursery/REPL door before the Psalm
  Matrix surface exists.
- **Workflow half**: Grand Plan sequence step 4, THE PSALM MATRIX stage
  (Dell Plan gate → Census → HCN → Dock → **Psalm Matrix** → windowed
  workspace → Grand Synchronization → §7), where the workflow surface,
  live feed, and witness views live.
- **Ordering constraints**: Q-FI011.1 + Q-FI011.2 rulings precede any
  build; C5R.5 precedes the gate half; C5R.6 precedes AI-proposed gates;
  the Dock precedes the workflow half.

## Slices (each failing-first, each independently closable)

- **W1 GATES** (Nursery): gate store + editor semantics + strict matcher
  + receipts + ungateable categories + kill switch. Failing-first:
  an unmatched item stays PENDING; a gate set by any non-user caller is
  impossible (caller-trace proof + adversarial suite); a hard-law
  category is refused at the editor by name.
- **W2 WORKFLOWS** (Psalm Matrix stage): workflow definitions, triggers,
  step execution producing PENDING proposals only.
- **W3 HAND-IN-HAND**: workflow output evaluated against gates at
  landing; placement law binding; live-feed witness surface.
- **W4 HARDENING**: adversarial pass — gate-widening attempts, origin
  spoofing, placement escapes, receipt completeness; held-out probes.
  (**Q-FI011.4**, Keeper: adversarial scope.)

## Done-definition

FI-011 is DONE when a user can: (a) define a workflow in the Psalm
Matrix; (b) set a gate in the Nursery, reading it back as one plain
sentence; (c) watch gate-matched output confirm automatically, each with
a receipt, while everything unmatched stays PENDING; (d) suspend or
revoke any gate — or all gates — instantly; and (e) no path exists,
proven adversarially, for a Psalm or a workflow to create, widen, or
satisfy a gate by itself, nor for any gate to pass a hard-law-barred
category.

## Questions

- **Q-FI011.1** (Director): is a user-set standing gate a human
  confirmation within C5.Door's meaning, and does the PENDING-only
  doctrine admit the gate-matched refinement on these terms?
- **Q-FI011.2** (Director): the ungateable category list under hard law.
- **Q-FI011.3** (Ace, non-blocking): gate placement default —
  sandbox-first unless the gate names a wall?
- **Q-FI011.4** (Keeper): W4 adversarial scope.

## Status

INTAKE → DEVELOPED + PLACED (2026-11-15). NOT authorized to build.
Waits: its sequence turn (Psalm Matrix stage; gate half after C5R.5/.6)
and the Q-FI011.1/.2 rulings.
