# R5-D NAMED MINIMAL CALLER SUBSET — caller-level proofs

Prepared 2026-11-19/20 (susx100000-execution), answering Director
7031879676: narrow to a named minimal caller subset; executable
at-cap/+1 caller-level tests; 10 SKIPs documented; no silent
promotion of all 25 CLEAN from a function-level heuristic.

## The named subset (10)
Intersection of the 25 INVENTORY-CLEAN sites (1d14ebe) with
form/open.py Program methods invocable with NO required arguments:
open.py:1116 radial_drift, 1221 internet_on, 1228 internet_off,
2056 sandbox_on, 2063 sandbox_off, 2068 enhance_on, 2072
enhance_off, 2166 save, 2171 visual, 2191 live_visual.

## Accounting of the 25 CLEAN — nothing promoted silently
- 10 in the subset (above).
- 4 CLEAN but arg-required (SKIP, exact args in the suite):
  806 set_view[room_id], 1011 enter_workshop[workshop_id],
  1110 set_lattice_size[size], 2157 run_script[script].
- 11 CLEAN but non-Program callers needing module fixtures —
  NOT in this subset, NOT claimed proven: allwhere 382/417/475,
  code_evolution 76/254, first_person 537, fourier 199,
  linear_algebra 192, core_ii_exec 134, repl 419/483.
The remaining 6 of the 10 documented SKIPs are non-CLEAN sites:
594/599 zoom_to[ref], 778 bimo_dock[slot,persona],
952 set_weather[condition], 1165 place[id,label],
2052 reject_proposal[pid]. SKIPs are never PASS.

## Suite: form/r5d_caller_subset_test.py
Per caller at cap (10,000) and cap+1 (10,001): typed refusal +
serialize byte-identical (no caller mutation before refusal) +
state-dir file set/sha256 unchanged (external side effects) +
no history-canary leak in refusal output. Cross-cutting: UTF-8
parity (ASCII/accent/CJK/emoji/combining labels refuse
identically), sanitize-before-measure canary, 4-thread TOCTOU
stability, restart round trip, legacy cap+50 loads whole.

## Result (failing-first, current main 7027419)
R5CS 2/27 PASS (control + cleanup), 25 FAIL, exit 1; two runs
identical modulo uuid. Findings beyond the known no-refusal:
- save (2166) and visual (2171) WRITE FILES at cap
  (files_same=False) — external side effects a preflight must
  precede, not follow.
- restart round trip FAIL: an at-cap history does NOT survive
  save->load whole today (load path truncates).
- legacy cap+50 load FAIL: loads truncated, not whole.
- sanitize canary: canary_in_state=False (sanitize works) but
  refused=False — the refusal, not the sanitizer, is missing.
Labels: INTEGRATION, in-process threads; multi-process writers
remain UNKNOWN. ZERO product code.
