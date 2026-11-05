# README COUNT POINTER — remove the numeric suite count (2026-11-05)

Directed by the Director's hourly review #5 (2026-11-05
02:35 CST, on PR #295): a future separate docs patch
removing the numeric suite count from README, replaced by
a pointer to the canonical harness — discharging the
recurring count-drift class (230 -> 236 -> 237 -> 238 in
four circuits) at its root.

Change (docs only): README's two present-tense numeric
claims ("a regression harness of **238 suites**"; "The
regression harness (238 registered suites)") now point to
`form/regress.py` as the canonical registry — the current
count is the length of its LIST. Historical counts inside
director-reports/ are preserved as history (per the 72-64
precedent). No code changed; no count is asserted anywhere
in this patch, so nothing here can drift.

## Anticipated probes

- "Is any other present-tense count live in README?" The
  two edited lines were the only suite-count claims (grep
  for the count and for "suites" at the patch base).
- "Does the pointer actually resolve?" `form/regress.py`
  LIST is the registry every regress run and the last four
  count circuits recomputed from.

## Questions for the Director

None. This discharges review #5's directive as specified.
