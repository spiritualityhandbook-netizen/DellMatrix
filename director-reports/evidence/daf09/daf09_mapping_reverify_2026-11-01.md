# DAF-09 identity mapping — re-verification against current main

Date: 2026-11-01 (sleep-mode Course 1, step a — analysis only, no code
or test changes).
Original mapping: daf09_identity_mapping_2026-10-31.md, written at
base f14df47 against form/regress.py + form/daf09_timeout_tree_test.py.
Re-verified against: origin/main **5f1120e** (fetched this run;
`git show origin/main:form/regress.py`, 800 lines, and
`git show origin/main:form/daf09_timeout_tree_test.py`, 442 lines).
Intervening change: the identity follow-up (identities at witness
time) and the pidfd-hardening follow-up (merge **87be4de** —
tri-state `_signal_identity`, numeric kill() fallback for historical
witnesses deleted, kill report, bounded-wait positive control,
suite 22 checks).

Status reminder (AGENTS.md §31.3): DAF-09 session-escape
certification is WITHHELD; the cross-environment discrepancy is
UNRESOLVED. Nothing below resolves it by local greens. Ruling #7
(register, DAF-09 entry) directs: preserve the exact 22 checks;
instrument identity acquisition at witness time AND signal time,
/proc visibility, namespace identity, reparenting, marker
timestamps, outcome path; separate missing identity from changed
identity from pidfd unavailability; provide a minimal positive
fixture proven visible in the observer's namespace; classify
unsupported environments explicitly.

---

## 1. Mapping claims, one by one

### Probe map

**C1 — Suite `_pid_alive(pid)` reads /proc/<pid>/stat, state parsed
after last ')', returns False for state Z; OSError => False.
ZOMBIE-AWARE.**
**STILL TRUE.** Current suite lines 67–73 implement exactly this
(`stat[stat.rfind(b")") + 2:].split()[0:1] != [b"Z"]`, OSError →
False). Only the line numbers moved (mapping cited test lines
43–50 at the old base).

**C2 — `_kill_process_tree` post-kill wait uses the same /proc stat
parse, state Z skipped as dead, otherwise os.kill(pid,0) existence
probe; bounded 2.0s, 0.05s slices. ZOMBIE-AWARE.**
**CHANGED BY HARDENING (strengthened).** The bound and cadence are
unchanged — deadline `time.monotonic() + 2.0` at regress.py:589,
`time.sleep(0.05)` at regress.py:596 — but the liveness probe is no
longer a bare-PID existence check. The loop (regress.py:589–597)
calls `_identity_alive(ident[0], ident[1])` (regress.py:465–482),
which returns False for state Z **and** False when the current
starttime differs from the witnessed starttime (a recycled PID
reads dead, never as a survivor). No `os.kill(pid, 0)` probe
remains in this path.

**C3 — `_descendant_pids(root)`: /proc ppid walk from root;
snapshot only.**
**CHANGED BY HARDENING (generalized).** The function is now
`_descendant_identities(root_pid)` (regress.py:370–403): one /proc
pass builds ppid links **and** starttimes together, and the walk
returns `(pid, starttime)` identity pairs. Same snapshot semantics
(snapshot before any kill, because reparenting destroys the tree),
stronger payload.

**C4 — `_communicate_tracked`: witness scan = one full /proc ppid
walk per 0.1s communicate slice during the wait; union stashed as
bare ints in proc._witnessed_descendants. NO identity (no
starttime, no pidfd).**
**CHANGED BY HARDENING (this was the H3 fix).** Cadence unchanged —
one `_descendant_identities(proc.pid)` scan per loop iteration,
`proc.communicate(timeout=min(0.1, remaining))` at regress.py:515,
deadline `time.monotonic() + TIMEOUT_S` at regress.py:504. What is
witnessed is now an IDENTITY: the union of `(pid, starttime)` pairs
is stashed as `proc._witnessed_identities` (regress.py:510), and
the function's own docstring states a bare PID is never witnessed
anymore.

**C5 — `_kill_process_tree` signalling: killpg(root pgid) +
os.kill(pid, SIGKILL) for snapshot UNION witnessed bare PIDs +
proc.kill(). Bare-PID risk confirmed in code: a witnessed PID
reused after its owner died would be signalled.**
**CHANGED BY HARDENING (the confirmed hazard is deleted).**
Current `_kill_process_tree` (regress.py:527–597):
- `os.killpg(os.getpgid(root), SIGKILL)` retained (regress.py:567)
  — session-scoped by construction (entry runs with
  `start_new_session=True`, run_entry regress.py:615), not
  history-based.
- Every non-group signal goes through `_signal_identity(pid,
  starttime, SIGKILL)` (regress.py:572). `_signal_identity`
  (regress.py:420–462): returns "refused" if starttime is None or
  the current `_proc_starttime(pid)` differs; opens a pidfd
  (`os.pidfd_open`), re-verifies starttime after the open, then
  signals via `_pidfd_send_signal` (ctypes syscall 424,
  regress.py:406–417). pidfd_open failure / no `os.pidfd_open` →
  "unavailable", nothing signalled. **There is no kill(2) fallback
  for witnessed identities** (docstring regress.py:438–445 cites
  the ruling and AGENTS.md §31.2).
- Legacy `proc._witnessed_descendants` bare-PID entries are
  explicitly NEVER signalled (comment, regress.py:~561–563).
- Per-identity outcomes are collected into a kill report stashed
  as `proc._kill_report` and module-level `_LAST_KILL_REPORT`
  (regress.py:571–575); `run_entry` surfaces a non-empty
  unavailable set in the timeout verdict as
  `cleanup_unavailable=<n>:<pids>` (regress.py:~622–631) and on
  the KeyboardInterrupt path as a printed line.
- `proc.kill()` retained for the root process itself (its own
  Popen handle, not a historical PID).

**C6 — The suite's own cleanup (old test lines ~166-169, ~224-227)
also os.kill()s a bare recorded PID if _pid_alive() is true — a
reused PID would read "alive" AND be SIGKILLed by the test
itself.**
**CHANGED BY HARDENING.** The surviving-escapee cleanup guard in
the current suite (test lines ~229–235) is identity-checked: it
signals only when `_pid_alive(esc_pid)` **and**
`R._proc_starttime(esc_pid) == esc_start`, where `esc_start` is
the starttime the grandchild captured from its own /proc/self/stat
and wrote into its pidfile (test lines ~155–160).

### Hypotheses

**H1 (zombie misread): NOT supported — both dead-checks are
explicitly zombie-aware; a zombie in the Director's environment
would read dead here.**
**STILL TRUE at current main.** Suite `_pid_alive` (test:67–73)
and regress `_identity_alive` (regress.py:465–482) both treat
state Z as dead; `_identity_alive` additionally requires the
starttime to match. H1 remains unsupported for every probe in
these two files. Do not spend the investigation on H1.

**H3 (identity race): CONFIRMED in code at f14df47 (bare int sets
everywhere); directed pidfd/starttime fix stands.**
**CHANGED BY HARDENING — the confirmed mechanism is closed in
code; the open residue points the other direction.** The chain
witness → store → signal now carries `(pid, starttime)` end to
end (C3/C4/C5), signalling is pidfd-pinned with starttime
re-verified before AND after the open (regress.py:447–458), and
the unsafe direction (signalling a reuser) has no remaining code
path. What hardening introduced instead is a *classification
seam*, visible in the Director's Ruling #7 failures:
- An identity whose starttime is **None** is "refused" at
  regress.py:~447 (`if starttime is None: return "refused"`)
  BEFORE pidfd is ever attempted — it can never land in
  "unavailable". None starttimes can enter the sets:
  `_descendant_identities` uses `starttimes.get(pid)` (may be
  None if that entry's stat read failed mid-scan), and the suite's
  controls capture `R._proc_starttime(pid)` directly, which
  returns None on any OSError/parse failure.
- The Director's failure (3) — pidfd-failure control showing
  `refused: [(22, None)]`, unavailable empty — is exactly this
  shape: in his environment the control's identity was captured
  with starttime None, so the pidfd branch was never reached.
  Failure (2) — positive control `kill_report=refused` — likewise
  means a starttime re-read at signal time returned None or a
  mismatching value.
So the live question is no longer identity *use* but identity
*acquisition reliability* in the Director's environment (why
`/proc/<pid>/stat` reads/parses fail or differ there). That is
precisely what Ruling #7's instrumentation must separate:
missing identity vs changed identity vs pidfd unavailability.
The current code collapses "missing" and "changed" into the same
"refused" bucket and records neither the expected nor the
observed starttime — the instrumented run must log the values.

---

## 2. H2 (marker-window timing) against the current code

### The bounds NOW

Suite-level (form/daf09_timeout_tree_test.py at 5f1120e):
- `R.TIMEOUT_S = 2` for the hang/escape/cancel sections
  (test:121). (Regress default is 900, regress.py:294.)
- Hang fixture descendant: writes pidfile, `time.sleep(3)`, writes
  marker, sleeps 30 (test:~99–101). Assertion after
  `time.sleep(4)` post-return (test:137).
- Escape grandchild: writes pidfile carrying **(pid, starttime)**
  captured from its own /proc/self/stat, `time.sleep(3)`, writes
  marker, sleeps 30 (test:153–164). Assertion after
  `time.sleep(4)` post-return (test:206).
- Escape mid parent: spawns the grandchild with
  `start_new_session=True`, then **waits until the pidfile exists
  (10s deadline, 0.05s polls) plus a 0.5s margin** before exiting
  (test:~169–181).
- Identity positive control: bounded wait, 5s deadline, 0.05s
  poll (test:~321–326). Pidfd-failure survival confirmation:
  0.5s bounded poll (test:~396–400).

Regress-level (form/regress.py at 5f1120e):
- Witness cadence: one full `_descendant_identities` /proc
  enumeration per `_communicate_tracked` loop iteration; slice
  `min(0.1, remaining)` (regress.py:515); deadline at
  regress.py:504.
- Kill path, in order: kill-time `_descendant_identities`
  snapshot → union with witnessed identities → killpg →
  per-identity `_signal_identity` (one `_proc_starttime` read +
  pidfd_open + second `_proc_starttime` read + pidfd_send_signal
  **per identity**) → root kill/wait(10) → identity-aware
  post-kill wait bounded 2.0s / 0.05s slices (regress.py:589–596).
  All of this runs inside run_entry's timeout handling, i.e.
  after the 2s deadline and before run_entry returns.

### Verdict on the mapping's two sub-claims

**(a) "Witness window is only the grandchild's first ~1s of
attachment (before mid exits)" — STALE-INAPPLICABLE as written.**
The ~1s fixed-sleep mid parent no longer exists. Mid's exit is
now gated on the grandchild's pidfile (proof the grandchild is
running) + 0.5s, so the attachment window is at least ~0.5s after
confirmed grandchild start, unbounded above (up to mid's 10s
pidfile deadline) — and witness scans run every ≤0.1s of
communicate wait throughout it. Slow fixture startup no longer
shrinks the window, because the window is keyed to the pidfile,
not the clock. Two residual narrowings remain, both worth
instrumenting rather than assuming away:
- Scans stop at the 2s timeout. If grandchild start + mid exit
  both land after the deadline (heavily loaded environment), the
  escapee is reachable only via the kill-time snapshot — which
  sees it only if mid is still alive at that instant. A mid exit
  between deadline expiry and the snapshot reopens a (much
  narrower) miss window.
- Each witness scan is a full /proc enumeration; in an
  environment with many processes or slow /proc, one scan +
  communicate cycle can exceed the nominal 0.1s slice, coarsening
  the effective cadence. The 0.5s post-pidfile margin absorbs
  ~5 nominal slices but perhaps only 1 slow one.

**(b) "Marker slack is only 3s − 2s = 1s after the timeout kill
begins" — STILL TRUE, structurally unchanged by hardening.** The
marker write is scheduled at grandchild_start + 3s; the kill
begins at entry_start + 2s. Slack = 1s + (grandchild_start −
entry_start) − (kill-path latency before the escapee's identity
is signalled). Hardening changed both correction terms in
opposite directions: the pidfile gate tends to make
grandchild_start earlier relative to the deadline (it is
confirmed running well before 2s in a healthy environment), but
the identity kill path is *slower per target* than the old bare
killpg+kill — a full /proc snapshot walk, then per identity two
stat reads and a pidfd open before the signal. The escapee is
reached only when its turn in the identities loop arrives. In a
slow environment a ~1s slack remains genuinely tight.

**H2 overall: SURVIVES, narrowed and reshaped.** The
witness-window half is largely mitigated (mapping figure stale);
the marker-slack half is intact. H2 remains a live explanation
for the Director's failure (1) (escaping grandchild post-timeout
marker) only. It does NOT explain failures (2) and (3), which are
identity-acquisition-shaped (§1, H3 residue). The instrumented
run must therefore not be a timing-only probe.

---

## 3. Per-hypothesis verdicts at current main (5f1120e)

- **H1 zombie-misread: NOT SUPPORTED — unchanged.** Both
  dead-checks zombie-aware; `_identity_alive` additionally
  starttime-matched. Closed as an explanation for these probes.
- **H2 marker-window timing: PLAUSIBLE, narrowed.** Witness
  sub-claim stale (pidfile-gated mid parent); marker-slack
  sub-claim (~1s) still true and per-identity kill latency grew.
  Live for failure (1) only.
- **H3 identity race: CONFIRMED at f14df47, CLOSED IN CODE by
  the identity + pidfd-hardening follow-ups.** No bare-PID
  signalling path remains for witnessed/snapshot identities;
  legacy bare entries are never signalled. Residual open seam:
  starttime-None identities collapse into "refused", confounding
  missing vs changed identity — matching the shape of the
  Director's failures (2) and (3). Reframed open question:
  identity *acquisition* reliability in the observing
  environment.

Session-escape status: WITHHELD. Discrepancy: UNRESOLVED.

---

## 4. Instrumented-run spec (step b) — ready to execute

Principle: the suite file is **not edited**. The suite imports
regress inside main() (`from form import regress as R`,
test:88), so a driver script pre-injects an instrumented regress
module as `sys.modules["form.regress"]` before invoking the
suite's `main()`. Instrumentation wraps/copies regress functions
in a scratch tree; the 22 checks, their names, fixtures, and
bounds are byte-identical. Verify preservation by diffing the
check-name list and the final `DAF09_TIMEOUT_TREE: n/22` line
shape against an uninstrumented local run.

### What to log (JSONL, monotonic + wall timestamps on every event)

Environment header (once per run):
- uname/kernel, Python version, CPU count, load average;
- `hasattr(os, "pidfd_open")`;
- PID namespace identity: inode of /proc/self/ns/pid and
  /proc/1/ns/pid; /proc mount options (hidepid) from
  /proc/self/mountinfo;
- observer pid.

Minimal positive fixture (BEFORE the 22 checks, per Ruling #7):
spawn a plain sleeper as a direct child of a throwaway root in
the observer's own namespace; prove (i) `_descendant_identities`
sees it, (ii) `_proc_starttime` returns a non-None value equal
to the starttime in its scan record, (iii) `_signal_identity`
on it returns "signalled" and the bounded wait observes death.
If any of (i)–(iii) fails, the environment is classified
UNSUPPORTED-FOR-CLEANUP-JUDGEMENT and the 22-check outcome is
reported as environment evidence, not a cleanup verdict.

Per-function hooks (line numbers at 5f1120e):
1. `_descendant_identities` (regress.py:370) — per call: t,
   root pid, scan duration, /proc entry count, returned
   identities incl. any `(pid, None)`, entries skipped on
   OSError/parse failure (pid + exception class).
2. `_communicate_tracked` (regress.py:484) — per slice: t,
   slice index, TIMEOUT_S in force, witnessed-union size,
   whether the escapee identity (from the pidfile, once known)
   is present, scan duration.
3. `_proc_starttime` (regress.py:351) — when called from
   `_signal_identity`: pid, returned value (value / None),
   exception class+errno when None.
4. `_signal_identity` (regress.py:420) — entry (pid, expected
   starttime); each re-read value (pre-open check ~:447,
   post-open check ~:456) labelled MISSING (None) vs CHANGED
   (different int) vs MATCH; pidfd_open result/errno; outcome;
   t. This is the hook that separates the three Ruling #7
   classes.
5. `_kill_process_tree` (regress.py:527) — t_kill_start;
   snapshot identities; witnessed identities; union; killpg
   result; per-identity outcomes with timestamps (extends the
   existing kill report, does not replace it); escapee ppid
   at kill time (reparenting evidence: ppid read from
   /proc/<esc_pid>/stat at witness time, kill time, assertion
   time); post-kill wait exit reason (all-dead vs 2.0s
   deadline) and final alive set.
6. `run_entry` (regress.py:604) — outcome path taken
   (normal / TimeoutExpired / KeyboardInterrupt), why string
   incl. any cleanup_unavailable suffix.
7. Marker timing (harness observer around the escape section,
   not in the suite): poll esc_marker existence at 0.05s
   cadence with monotonic timestamps from escape-section start;
   record pidfile mtime (≈ grandchild start), marker mtime if
   written, t of kill start (from hook 5) — yielding the actual
   slack consumed vs the §2 budget.
8. Suite-side events observable without editing the suite:
   capture the escape section's `_diag` detail string (kill
   report membership, identity_now, marker state) and the three
   Ruling #7 failure checks' details verbatim from RESULTS
   output.

### Runs and reporting
- ≥3 instrumented runs locally (idle) + ≥1 under CPU saturation;
  the local runs calibrate the instrumentation (they do NOT
  resolve the discrepancy, §31.3).
- The same driver + spec is packaged so the Director's
  environment can run it unchanged; his instrumented output is
  the discriminating evidence.
- Deliverable: evidence packet keyed to the three failures
  separately — (1) escape marker: timing/witness class;
  (2) positive control refused: MISSING vs CHANGED identity;
  (3) pidfd control: whether the captured identity was None at
  capture time (suite-side `_proc_starttime`) or became refused
  later. No claim change without that evidence; no blind
  sleeps; no numeric fallback reintroduced, in instrumentation
  or anywhere else.

**Spec status: READY TO EXECUTE.**
