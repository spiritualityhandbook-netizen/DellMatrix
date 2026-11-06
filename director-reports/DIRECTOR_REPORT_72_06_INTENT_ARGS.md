# DIRECTOR REPORT — 72-06: English Intent.args End-to-End Census

**Circuit:** NBD Master Objective Register 72-06 (= SM-11 full-contract
review, ordered in ruling Q-C3). **Mode:** INVESTIGATION ONLY, per the
Director's Mode A authorizations (2026-11-05 18:41 and 19:26 CST).
**Base:** main `f92e5b1`. **No product code changed.**
**Evidence:** `evidence/72-06-intent-args/` — `q06_probe.py`
(21 checks), two identical run logs, `MANIFEST.sha256` (verified).
**SWAT:** proportionate (investigation of one data channel; no build).

## Question

SM-11 certified the *digit-count* dropped-args class. The full
contract was never reviewed: for every argument `translate()` puts
into `Intent.args`, does it reach execution, get transformed, get
refused loudly, or get silently dropped — at each layer (canonical
router, REPL handlers, programmatic route)?

## Method

Static census of every `Intent(...)` production site in
`form/mandell/translate.py` (714 lines) and every `intent.args`
consumer in `form/` + `gui/`; dynamic end-to-end probe (21 cases,
two identical runs): translate → record args/mandel → `route_intent`
on isolated per-case Programs → record executed seed / refusal.
REPL-layer spot checks cross-process (REAL_USER_PATH).

## Census result — six classes, complete over the args-bearing surface

**Class A — consumed by the canonical router (4 keys).** The
correspondence `build_seed` functions in `semantic_router.py` are
the ONLY router readers of `intent.args` (lines 110/143/151/159):
`grow.cycles`, `stamp.mark`, `cycle.count`, `form.form` — each is
transformed into the executed seed label (A1–A4 pass).

**Class B — mirrored in the mandel text (9+ keys).** For move, copy,
get/find, select, match, nurture, place, turn, express, strafe, the
operand rides the mandel string (typed-arg or label syntax); the
router executes the mandel and never reads the args dict. Operand
verified present in the executed seed (B6/B7/B11–B14). The args
dict is a faithful mirror, not a channel.

**Class B-gated — mirrored, but execution refused BY DESIGN (3).**
`delete`/`replace`/`patch` (Dells 86/87/88): `route_intent` refuses
with `blocked_with_reason: destructive store mutation via English
composition is deferred pending operand-confirmation flow`. The
operand is intact in args and mandel up to the gate; the refusal is
explicit, not silent (BG8–BG10).

**Class C — REPL-only (router honestly refuses).** `walk.steps`,
`backstep.steps`, `strafe.*`, `turn.direction`, `express.expression`,
`place.id/label/words`: `route_intent` returns routed=False
(C15/C16 pin the walk/turn cases). The REPL's direct handlers in
`_execute_intent` are the consumers (`form/repl.py`: place 2940,
walk 3022, backstep 3059, strafe 3070, turn 3089, express 3123).
Verified at REAL_USER_PATH: `walk forward 3` moves the avatar to
(0, 3) — steps consumed. No layer drops these silently; the router
layer simply does not serve these actions.

**Class D — dead args (2 keys).** `zoom.ref` and
`weather.condition` are produced by translate, absent from the
mandel (`15[Map] :: zoom`, `25[Pulse] :: weather`), and read by NO
code in `form/` or `gui/` (exhaustive grep). The operand survives
at the REPL only because separate raw-line handlers re-parse the
user's text (`repl.py` 2445 `zoom <ref>`, 2081 `weather <cond>`);
verified live: `weather rain` → "Weather → rain". A programmatic
consumer of `Intent.args` would find plausible-looking values that
do nothing. The channel lies; the user path does not.

**Class E — producer-side silent default (THE live defect class).**
Spelled-out counts are silently replaced by 1 and executed with
ok=True: `cycle three times` → args count=1 → executed
`06[Cycle] :: 1` (E19); `grow three` → cycles=1 → `13[Loop] :: 1`
(E20). Digit forms are honored (control CTL: `cycle 3 times` →
:: 3). This is the SM-11 family — operand present in the English,
a default substituted, success reported — in the word-form the
SM-11 certification never covered. The composite path is NOT
affected: `english_composer` normalizes number words before
translate (verified in 72-16: "cycle 3 times and then measure"
executes count=3). The gap is bare `translate()` only: its count
extractions are digit-only (phrase branch `isdigit()` checks at
translate.py:387/404; fallback cycle regex `(\d+)?` at :656).

**Transformations catalogued (stated, not silent):** cycle counts
are clamped at the producer (translate clamps 9→5 in args itself,
A5; the router clamps again); stamp marks are truncated to 48
chars and sanitized at the router (`_seed_stamp`); form names are
enum-validated with a `cube` default at the router (`_seed_form`) —
unreachable from English, whose producer regex admits only the
four valid forms. **No-arg majority:** 36+ Intent returns carry
`args={}`; their operands (discover variants, etc.) ride the
mandel label — nothing exists to drop. One inverse gap:
`repl.py`:3215 reads `args["query"]`, produced only by unknown
intents, for the error message — benign.

## Verdict

The Intent.args contract is **mostly honest**: one true channel
(Class A), one faithful mirror (B), one designed gate (B-gated),
one honestly-refusing split (C). Two residual defects, both
bounded: **Class E is a real silent-operand-loss defect** (same
family as the certified SM-11 repair, in its uncovered word-form),
and **Class D is a vestigial channel** that misrepresents itself
to programmatic consumers while the user path routes around it.
No repair is proposed or made under this investigation;
remedies are the Director's to authorize.

## Anticipated probes

- *"Is Class E reachable by a real user?"* Yes — bare REPL English
  (`cycle three times`) is the primary English entry; the probe
  executed it through translate + route_intent, and the REPL
  consumes that same Intent.
- *"Why isn't Class D a user-facing loss?"* Because the REPL
  never routes "weather rain" through translate's args — its
  raw-line handler fires first; verified cross-process.
- *"Did you census synthetic/API intents too?"* The census covers
  every producer in translate.py; hand-built intents from other
  callers enter at route_intent, where only the four Class A keys
  are read — stated as the router's contract, probed via B/C/D.

## Questions for the Director

- Q-06.1: Class E remedy — a bounded repair circuit normalizing
  number words in translate()'s count extractions (mirroring the
  composer's existing normalization), failing-first on E19/E20?
- Q-06.2: Class D — should zoom/weather consume their args (make
  the channel real), stop producing them (make the type honest),
  or remain as documented vestige?
- Q-06.3: The B-gated trio cites a "pending operand-confirmation
  flow" — is that flow a registered objective anywhere, or should
  it be entered into the register as its own item?
