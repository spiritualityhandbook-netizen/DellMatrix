#!/usr/bin/env python3
"""Part VII / GP-E27 — journey harness family 2: J-03 English -> LatinMandell.

Written failing-first as the plan-stage spec
(form/journey_language_test_spec.py); code-stage step zero renames it
to *_test.py and registers it in form/regress.py LIST in the same
commit (omitted-entry law).

Contract: Edition 1 file 06 (06_JOURNEY_ACCEPTANCE.md), executed
verbatim — this suite does not paraphrase the oracle into weaker form:

  J-03 English -> LatinMandell: "Enter a documented supported English
  action. Show recognized intent/typed roles, LM stage/translation
  basis, Mandell seed, exact executed operation and refusal if
  ambiguous."
  Failure oracle: "Long admissible operand remains whole; uncertain
  analysis declines; no fabricated fallback Show; offline
  deterministic and dock-optional paths have truthful source labels."

Execution tier: PUBLIC_ENTRY_PATH — every journey action runs in a
literal `python3 -m form.repl` subprocess against a per-run isolated
owner; state comparison after cold reload uses the persistence loader
(the same like-for-like basis as form/journey_chain_test.py: reloaded
vs reloaded, never in-memory vs reloaded).

Grounded behavior (each expectation verified first-hand in
scratch-owner probes, 2026-11-21, before this spec was written):
  - `mandell create an idea called Seed Probe` prints the Mandell
    seed `08[Create](name="Seed Probe") > 15[Map] :: Seed_Probe` and
    executes nothing (the translation door shows the seed only).
  - `create an idea called Journey Language Oak` (the documented
    action — the REPL banner's own "Try:" line) prints the LM-4
    decomposition trace: the intent morpheme with its translation
    basis ("create -> bring into being - call forth [FUNCTION -
    curated governs: Dell 08]"), operand morphemes labeled
    "OPERAND - operand (user data - traced, not routed)", the spine
    reading labeled "(projection - not the executed chain)", then the
    executed operation `Created idea: "Journey Language Oak"`.
  - `grow ideas 1` routes through route_intent and prints the full
    DCC-III receipt: INPUT / MANDELL (`13[Loop] > 04[Transform] ::
    grow`) / SEMANTIC (grow[Loop]) / ARGUMENTS (cycles=1 - the typed
    role) / ROUTE (grow/13 [Loop]) / DELL 13 executed / RESULT ok=True,
    with the LM trace riding the receipt.
  - Uncertain analysis declines: gibberish ("flibberty gibbet the
    wozzle please") prints `Not understood:` and executes nothing.
    (The unknown intent's seed renders in the echo as
    `09[Show] :: unknown` — a translation artifact labeled "unknown",
    NOT an executed Show: no Show operation runs and no state
    changes. The check below pins exactly that distinction.)
  - Ambiguous analysis declines: bare `restore` is genuinely
    ambiguous between the checkpoint and session readings (REPL
    MPC-008: Dell28's canonical English, "genuinely ambiguous, not
    guessed"); on a fresh owner it prints `Restore unavailable:` and
    executes nothing.
  - DEFECT FOUND BY THIS SPEC (failing-first): a long admissible
    operand did NOT remain whole. `create an idea called
    JourneyLongOperand <160 x's> ZzEndmark` (189 chars) stored the
    label cut at exactly 80 chars, the tail (incl. the end marker)
    silently lost: form/idea_create.py parse_create_line carried
    `"label": label[:80]` with no provenance or refusal. Mechanism
    traced: REPL create door -> dell_matrix/needs.parse_and_place ->
    idea_create.parse_create_line -> Program.place (the cut label is
    the stored unit label). The canonical 40-char slug_id is the
    address slug, a separate disclosed constraint — the operand at
    issue is the label (content), not the address.

Baseline posture (plan section 5.1(iii)): this suite runs against the
pre-Parts main as a labeled BASELINE harness proof. Its grades are
evidence about the harness and the current program, recorded in
director-reports/GRAND_SYNCHRONIZATION_REHEARSAL_2026-11-20.md; the
GP-E27 rehearsal executions proper run against merged Parts I + II.

Run: python3 -m form.journey_language_test
"""

import os
import shutil
import subprocess
import sys
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from form.persist import _STATE_DIR, _safe_owner, load as persist_load

RESULTS = []
_CLEANUP_ERRORS = []
RUN = uuid.uuid4().hex[:8]
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

LONG_NAME = "JourneyLongOperand " + "x" * 160 + " ZzEndmark"


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))
    print(f"{'PASS' if ok else 'FAIL'} {name} {detail}")


def cleanup(owner):
    safe = _safe_owner(owner)
    if not os.path.isdir(_STATE_DIR):
        return
    for name in os.listdir(_STATE_DIR):
        if safe in name:
            p = os.path.join(_STATE_DIR, name)
            try:
                shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
            except OSError as e:
                _CLEANUP_ERRORS.append(f"{p}: {e}")


def state_files(owner):
    safe = _safe_owner(owner)
    if not os.path.isdir(_STATE_DIR):
        return []
    return sorted(n for n in os.listdir(_STATE_DIR) if safe in n)


def run_repl(owner, lines, load=False):
    args = [sys.executable, "-m", "form.repl", "--owner", owner]
    if load:
        args.append("--load")
    proc = subprocess.run(args, input="\n".join(lines) + "\n",
                          capture_output=True, text=True, cwd=ROOT,
                          timeout=300)
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def snap(owner):
    prog = persist_load(owner)
    return {
        "labels": sorted(n.get("label") for n in prog.nodes_payload()),
    }


def main():
    lang_owner = f"JLang{RUN}"
    decline_owner = f"JDecline{RUN}"
    for o in (lang_owner, decline_owner):
        cleanup(o)
    try:
        # Isolation boundary, proven — not assumed: this run's owners
        # have no pre-existing state files (a fresh Program() in this
        # codebase loads persisted state by default; the boundary
        # here is the per-run unique owner + verified-empty start).
        check("j03_isolation_boundary_clean_start",
              state_files(lang_owner) == []
              and state_files(decline_owner) == [],
              "no state files exist for either per-run owner before "
              "the sessions start")

        # ---------------- J-03: supported English action ----------------
        rc, out = run_repl(lang_owner, [
            "mandell create an idea called Seed Probe",
            "create an idea called Journey Language Oak",
            "grow ideas 1",
            f"create an idea called {LONG_NAME}",
            "save",
            "quit",
        ])
        check("j03_repl_exit_clean",
              rc == 0 and "Traceback" not in out,
              f"rc={rc} traceback={'Traceback' in out}")
        check("j03_mandell_door_shows_seed_without_executing",
              '08[Create](name="Seed Probe") > 15[Map] :: Seed_Probe' in out
              and 'Created idea: "Seed Probe"' not in out,
              "the mandell door displays the exact Mandell seed for "
              "the English action and executes nothing")
        check("j03_recognized_intent_with_translation_basis",
              "create → bring into being · call forth "
              "[FUNCTION · curated governs: Dell 08]" in out,
              "LM stage: the intent morpheme is recognized and its "
              "translation basis is named (curated LM governs Dell 08)")
        check("j03_operands_labeled_user_data_traced_not_routed",
              "OPERAND · operand (user data — traced, not routed)" in out,
              "the name's morphemes are typed as OPERAND roles - user "
              "data traced through the LM stage, never routed as "
              "instructions")
        check("j03_spine_labeled_projection_not_executed_chain",
              "LM: spine reading: 08[Create] > 08[Create] "
              "(projection — not the executed chain)" in out,
              "truthful source label: the LM spine reading declares "
              "itself a projection; the executed operation is "
              "reported separately")
        check("j03_exact_executed_operation",
              'Created idea: "Journey Language Oak"' in out,
              "the executed operation and its declared effect are "
              "printed for the English action")
        check("j03_routed_receipt_full",
              "INPUT: grow ideas 1" in out
              and "MANDELL: 13[Loop] > 04[Transform] :: grow" in out
              and "SEMANTIC: grow[Loop]" in out
              and "ARGUMENTS: cycles=1" in out
              and "ROUTE: grow/13 [Loop]" in out
              and "DELL: 13 (executed via Dell authority)" in out
              and "RESULT: ok=True" in out,
              "routed English action shows intent, typed roles "
              "(cycles=1), Mandell seed, route and the exact Dell "
              "executed, with ok result")
        check("j03_routed_lm_basis_named",
              "grow → increase by living process "
              "[FUNCTION · curated governs: Dell 13]" in out,
              "the routed action's LM trace rides its receipt with "
              "the same truthful basis label (offline deterministic "
              "curated LM; no dock connected on this path)")
        check("j03_long_operand_remains_whole_in_session",
              f'Created idea: "{LONG_NAME}"' in out
              and "ZzEndmark" in out,
              "189-char admissible operand: the created idea's label "
              "is the whole operand, end marker included, in-session")
        check("j03_save_receipt", "Session saved." in out, "")

        # Cold reload: a second, separate process on the saved state.
        rc2, out2 = run_repl(lang_owner, ["status", "quit"], load=True)
        s = snap(lang_owner)
        check("j03_reload_compare",
              rc2 == 0 and "ideas=3" in out2,
              f"rc={rc2}; Welcome + the two created ideas after cold "
              "reload")
        check("j03_long_operand_remains_whole_after_reload",
              LONG_NAME in s["labels"]
              and "Journey Language Oak" in s["labels"],
              f"persisted labels carry the whole long operand "
              f"(labels={s['labels']})")

        # ---------------- J-03: uncertain / ambiguous decline ----------------
        rc3, out3 = run_repl(decline_owner, [
            "flibberty gibbet the wozzle please",
            "restore",
            "status",
            "quit",
        ])
        check("j03_uncertain_analysis_declines",
              'Not understood: "flibberty gibbet the wozzle' in out3,
              "gibberish English declines with an explicit Not "
              "understood - no intent is fabricated")
        check("j03_no_fabricated_fallback_show",
              "Created idea" not in out3
              and "executed via Dell authority" not in out3,
              "the decline executes nothing: the unknown intent's "
              "seed echo (09[Show] :: unknown) is a labeled "
              "translation artifact, not an executed Show operation")
        check("j03_ambiguous_analysis_declines",
              "Restore unavailable:" in out3,
              "bare 'restore' (genuinely ambiguous between the "
              "checkpoint and session readings) declines and "
              "executes nothing")
        idx = out3.find("(·_·)")
        tail = out3[idx:] if idx >= 0 else ""
        check("j03_declines_leave_state_untouched",
              "ideas=1" in tail and "nursery=0" in tail
              and state_files(decline_owner) == [],
              "after both declines: only the start-of-session idea, "
              "empty nursery, no state file was ever created")
        check("j03_session_survives_declines",
              rc3 == 0 and "Traceback" not in out3 and "Goodbye." in out3,
              f"rc={rc3}; the session answered status and quit "
              "cleanly after the decline battery")
    finally:
        for o in (lang_owner, decline_owner):
            cleanup(o)

    check("Z.cleanup", not _CLEANUP_ERRORS, "; ".join(_CLEANUP_ERRORS))
    failed = [n for n, ok, _ in RESULTS if not ok]
    print(f"JOURNEY_LANGUAGE: {len(RESULTS) - len(failed)}/{len(RESULTS)} PASS")
    if failed:
        print("FAILURES:", ", ".join(failed))
    return 1 if failed else 0


def smoke():
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
