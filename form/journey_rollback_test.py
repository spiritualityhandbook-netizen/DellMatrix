#!/usr/bin/env python3
"""Part VII / GP-E27 — journey harness family 5: J-06 Rollback.

Written failing-first at code stage and registered in
form/regress.py LIST in the same commit (omitted-entry law).

Contract — Edition 1 file 06 (06_JOURNEY_ACCEPTANCE.md), J-06,
executed verbatim:

  Action: "Seal named generation, make further edits, invoke
  authorized freeze/grant/confirm rollback, cold reload and
  compare exact restored scope."
  Failure oracle: "Bare rollback refuses; cross-owner and
  stale-grant refusal, injected partial restore, evidence
  remains immutable and current status not faked."

Execution tier: PUBLIC_ENTRY_PATH — every journey action runs in
a literal `python3 -m form.repl` subprocess against a per-run
isolated owner; state comparison uses the persistence loader
(reloaded vs reloaded, never in-memory vs reloaded). Two fixture
mechanics are disclosed where they occur: the sealed-member
tamper injection writes bytes directly to one sealed generation
member file (the fault being injected — the rollback attempt
itself runs at the public path), and the aliasing probe compares
the target's frozen fingerprints through the read-only freeze
door (freeze_rollback_target performs no writes).

Grounded behavior (each expectation verified first-hand in
scratch-owner probes, 2026-11-21, before this suite was written):
  - `27[Checkpoint] :: <name>` seals a NAMED generation and
    prints "Checkpoint written: generation <name>"; the CURRENT
    pointer then names it. commit_checkpoint saves the live pair
    first, then seals byte-exact member copies (program, nursery,
    ideas, graph).
  - Bare `restore` freezes CURRENT and describes only: "Restore
    requires explicit approval. This would: - roll back to
    generation <current> ... To approve, type: restore confirm
    <current>" — it never executes; live state is unchanged.
  - A bare `28[Rollback] :: <gen>` seed routes to the mediated
    door with no approval and is denied: "Rollback denied
    (acceptance_policy_denied): Producer 'dell28' has no issued
    approval or active opt-in ..." — zero mutation.
  - `restore confirm <gen>` is the authorized two-step: the REPL
    freezes the target, issues the human approval bound to the
    frozen target + live fingerprints, and executes through
    Program.confirm_rollback. Success prints "Restored
    generation <gen>." and "Compensating checkpoint: <id>" — the
    safety checkpoint sealing the pre-rollback live state, whose
    own confirm is the undo.
  - After a rollback the live files converge EXACTLY to the
    sealed target scope (loader snapshot identical to the
    seal-time snapshot, history included) — eager convergence by
    independent serialized copies, never by aliasing: mutating
    live state after a rollback leaves the sealed generation's
    frozen member fingerprints untouched, and a second rollback
    to the same target restores the exact sealed scope again
    (the post-rollback mutation is gone, not merged in).
  - The CURRENT pointer after a rollback names the compensating
    generation (the newest committed generation), and a bare
    `restore` afterwards describes that compensating generation
    — the undo point — as its target. Live state (what every
    loader reads) is the rollback target; the pointer records
    the latest seal. Recorded as grounded behavior.
  - Retention keeps CURRENT + previous (+ the frozen target
    during a rollback): after three seals, the oldest generation
    is pruned and `restore confirm <pruned>` refuses at the
    freeze door — "Restore denied: cannot freeze target:
    generation '<gen>' unreadable: ..." — the stale-target
    refusal. An unknown generation id refuses identically.
  - Cross-owner: generations are owner-namespaced; a fresh
    owner's `restore confirm <another owner's gen>` refuses at
    the freeze door, and a bare `restore` with no committed
    generation answers "Restore unavailable: no committed
    generation for owner ...". The foreign attempt creates no
    state files for the foreign owner at all.
  - Injected partial restore (public-path member of the class):
    flipping one byte in the sealed target's program member
    makes the freeze re-hash fail — "Restore denied: cannot
    freeze target: generation '<gen>' member 'program'
    fingerprint mismatch" — with live state and CURRENT
    untouched (evidence is tamper-evident, never absorbed; the
    status quo is not faked into a restore). Restoring the
    member's original bytes makes the same confirm succeed,
    proving the refusal was the corruption, not a broken door.

Uncovered at this tier, named honestly (not silently passed):
  - Grant staleness proper — a grant issued, live state then
    drifting, execution denying at live revalidation — cannot
    be constructed through the REPL text door, where issuance
    and execution are a single command; confirm_rollback's live
    revalidation is exercised by the R6.3 authority circuits at
    API level. The public-path members of the stale/no-grant
    refusal family (no-grant Dell 28 denial, pruned target,
    unknown target, cross-owner) are all exercised here.
  - Mid-flight crash injection into a running rollback (the
    _fail_at points) is likewise API-level, covered by the
    checkpoint crash-matrix circuits; the injected fault this
    suite exercises at the public path is sealed-member
    tampering refused at the freeze door, before any restore
    step runs — a partial/corrupt restore never begins.

Baseline posture (plan section 5.1(iii)): this suite runs
against the pre-Parts main as a labeled BASELINE harness proof.
Its grades are evidence about the harness and the current
program, recorded in
director-reports/GRAND_SYNCHRONIZATION_REHEARSAL_2026-11-20.md;
the GP-E27 rehearsal executions proper run against merged
Parts I + II.

Run: python3 -m form.journey_rollback_test
"""

import os
import re
import shutil
import subprocess
import sys
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from form.persist import _STATE_DIR, _safe_owner, load as persist_load
from form.dell_matrix.rollback_authority import freeze_rollback_target
from form.mandell.checkpoint_generation import (
    _member_path, current_generation_id)

RESULTS = []
_CLEANUP_ERRORS = []
RUN = uuid.uuid4().hex[:8]
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

CA = ("create an idea called Alpha Stone detail: alpha stone "
      "granite quarry marker goals: hold the alpha line")
CB = ("create an idea called Beta Stone detail: beta stone "
      "granite quarry marker goals: hold the beta line")
CC = ("create an idea called Gamma Stone detail: gamma stone "
      "granite quarry marker goals: hold the gamma line")
CD = ("create an idea called Delta Stone detail: delta stone "
      "granite quarry marker goals: hold the delta line")


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


def run_repl(owner, lines, load=False, timeout=300):
    args = [sys.executable, "-m", "form.repl", "--owner", owner]
    if load:
        args.append("--load")
    proc = subprocess.run(args, input="\n".join(lines) + "\n",
                          capture_output=True, text=True, cwd=ROOT,
                          timeout=timeout)
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def snap(owner):
    """Loader-basis snapshot: the full persisted scope — units
    with content fields, nursery statuses, boxes, history."""
    prog = persist_load(owner)
    plane = prog.cube.session.plane
    units = {}
    for uid, u in plane.units.items():
        units[uid] = {
            "label": u.label,
            "detail": getattr(u, "detail", "") or "",
            "goals": list(getattr(u, "goals", []) or []),
            "words": getattr(u, "words", "") or "",
            "parents": list(getattr(u, "parents", None) or []),
            "origin": getattr(u, "origin", None),
            "sandboxed": bool(getattr(u, "sandboxed", False)),
            "sandbox_id": getattr(u, "sandbox_id", None),
        }
    boxes = {sid: sorted(sb.member_ids)
             for sid, sb in plane.sandboxes.items()}
    props = {pid: p.status
             for pid, p in prog.nursery.proposals.items()}
    return {"units": units, "boxes": boxes, "props": props,
            "summary": prog.nursery.summary(),
            "history": list(getattr(prog, "history", []) or [])}


def main():
    roll_owner = f"JRoll{RUN}"
    alias_owner = f"JAlias{RUN}"
    stale_owner = f"JStale{RUN}"
    cross_owner = f"JCross{RUN}"
    tamper_owner = f"JTamper{RUN}"
    owners = (roll_owner, alias_owner, stale_owner, cross_owner,
              tamper_owner)
    for o in owners:
        cleanup(o)
    try:
        # Isolation boundary, proven — not assumed (a fresh
        # Program() in this codebase loads persisted state by
        # default; the boundary is the per-run unique owner +
        # verified-empty start).
        check("rollback_isolation_boundary_clean_start",
              all(state_files(o) == [] for o in owners),
              "no state files exist for any of the five per-run "
              "owners before the sessions start")

        # ---------------- J-06: seal named, edit, seal again ----
        rc, out = run_repl(roll_owner, [
            CA, CB,
            "27[Checkpoint] :: alpha_base",
            "quit",
        ])
        check("j06_repl_exit_clean",
              rc == 0 and "Traceback" not in out,
              f"rc={rc} traceback={'Traceback' in out}")
        check("j06_seal_named_generation",
              "Checkpoint written: generation alpha_base" in out
              and current_generation_id(roll_owner) == "alpha_base",
              "Dell 27 seals the NAMED generation alpha_base and "
              "the CURRENT pointer names it")
        s1 = snap(roll_owner)
        check("j06_scope_at_first_seal",
              set(s1["units"]) == {"welcome", "alpha_stone",
                                   "beta_stone"},
              f"sealed scope: {sorted(s1['units'])}")
        rc, out = run_repl(roll_owner, [
            CC,
            "27[Checkpoint] :: beta_base",
            "quit",
        ], load=True)
        s2 = snap(roll_owner)
        check("j06_second_seal_after_further_edits",
              "Checkpoint written: generation beta_base" in out
              and current_generation_id(roll_owner) == "beta_base"
              and "gamma_stone" in s2["units"]
              and s2["units"].keys() != s1["units"].keys(),
              "further edits land, the second named generation "
              "seals, and CURRENT advances to it")

        # ---------------- J-06: bare rollback refuses ----------
        rc, out = run_repl(roll_owner, ["restore", "quit"],
                           load=True)
        check("j06_bare_restore_describes_and_refuses",
              "Restore requires explicit approval." in out
              and "- roll back to generation beta_base" in out
              and "To approve, type: restore confirm beta_base"
              in out,
              "bare restore freezes CURRENT and describes the "
              "rollback — it never executes it")
        check("j06_bare_restore_mutates_nothing",
              snap(roll_owner) == s2,
              "live state after the bare restore is byte-scope "
              "identical to before it")
        rc, out = run_repl(roll_owner, [
            "28[Rollback] :: alpha_base",
            "quit",
        ], load=True)
        check("j06_dell28_bare_seed_denied_no_grant",
              "Rollback denied (acceptance_policy_denied)" in out
              and "has no issued approval or active opt-in" in out
              and snap(roll_owner) == s2,
              "a bare Dell 28 seed hits the mediated door with no "
              "approval and is denied with zero mutation")

        # ---------------- J-06: authorized rollback ------------
        rc, out = run_repl(roll_owner, [
            "restore confirm alpha_base",
            "quit",
        ], load=True)
        m = re.search(r"Compensating checkpoint: (\S+)", out)
        comp = m.group(1) if m else None
        check("j06_authorized_rollback_receipt",
              "Restored generation alpha_base." in out
              and comp is not None,
              f"the two-step confirm restores; compensating "
              f"checkpoint={comp}")
        check("j06_restored_scope_exact",
              snap(roll_owner) == s1,
              "after cold reload the live scope equals the "
              "alpha_base seal-time scope EXACTLY (units with "
              "content, nursery, boxes, history) — Gamma is "
              "gone, nothing of the later state leaks in")
        check("j06_current_names_compensating_not_faked",
              comp is not None
              and current_generation_id(roll_owner) == comp,
              "CURRENT names the newest committed generation — "
              "the safety checkpoint — while live state is the "
              "target; neither is dressed as the other")
        rc, out = run_repl(roll_owner, ["restore", "quit"],
                           load=True)
        check("j06_bare_restore_now_describes_undo_point",
              comp is not None
              and f"- roll back to generation {comp}" in out
              and snap(roll_owner) == s1,
              "a bare restore after the rollback describes the "
              "compensating generation (the undo point) and "
              "still executes nothing")
        rc, out = run_repl(roll_owner, [
            f"restore confirm {comp}",
            "quit",
        ], load=True)
        check("j06_undo_via_compensating_restores_scope",
              comp is not None
              and f"Restored generation {comp}." in out
              and snap(roll_owner) == s2,
              "confirming the compensating generation undoes "
              "the rollback: the pre-rollback scope (Gamma "
              "included) is restored exactly")
        rc, out = run_repl(roll_owner, ["status", "quit"],
                           load=True)
        check("j06_cold_reload_scope_stable",
              rc == 0 and "Traceback" not in out
              and snap(roll_owner) == s2,
              "a fresh cold session loads the same scope — the "
              "restored state is durable, not session luck")

        # ---------------- J-06: aliasing probe -----------------
        rc, out = run_repl(alias_owner, [
            CA,
            "27[Checkpoint] :: seal_one",
            "quit",
        ])
        sb1 = snap(alias_owner)
        rc, out = run_repl(alias_owner, [
            CC,
            "27[Checkpoint] :: seal_two",
            "quit",
        ], load=True)
        frozen1 = freeze_rollback_target(alias_owner, "seal_one")
        rc, out = run_repl(alias_owner, [
            "restore confirm seal_one",
            "quit",
        ], load=True)
        check("j06_alias_rollback_receipt",
              "Restored generation seal_one." in out
              and snap(alias_owner) == sb1,
              "rollback to seal_one restores its exact scope")
        rc, out = run_repl(alias_owner, [
            CD,
            "save",
            "quit",
        ], load=True)
        mutated = snap(alias_owner)
        check("j06_alias_live_mutation_lands_live",
              "delta_stone" in mutated["units"],
              "after the rollback, a new idea is created and "
              "saved into LIVE state (the mutation under test)")
        frozen2 = freeze_rollback_target(alias_owner, "seal_one")
        check("j06_alias_sealed_generation_unchanged",
              frozen2["members"] == frozen1["members"]
              and frozen2["manifest_sha256"]
              == frozen1["manifest_sha256"],
              "the sealed generation's frozen fingerprints (all "
              "four members + manifest) are identical before and "
              "after the live mutation — rollback copied the "
              "sealed target into independent live state; live "
              "state is NOT aliased to the sealed member, or "
              "the mutation would have rewritten the seal")
        rc, out = run_repl(alias_owner, [
            "restore confirm seal_one",
            "quit",
        ], load=True)
        check("j06_alias_second_rollback_restores_exact",
              "Restored generation seal_one." in out
              and snap(alias_owner) == sb1,
              "a second rollback to seal_one restores the exact "
              "sealed scope again — Delta is gone, not merged "
              "into the generation")

        # ---------------- J-06: stale / unknown targets --------
        rc, out = run_repl(stale_owner, [
            CA, "27[Checkpoint] :: gen_a",
            CB, "27[Checkpoint] :: gen_b",
            CC, "27[Checkpoint] :: gen_c",
            "quit",
        ])
        ss = snap(stale_owner)
        check("j06_stale_setup_three_seals",
              rc == 0
              and current_generation_id(stale_owner) == "gen_c"
              and set(ss["units"]) == {"welcome", "alpha_stone",
                                       "beta_stone", "gamma_stone"},
              "three named generations sealed in sequence; "
              "CURRENT names gen_c")
        rc, out = run_repl(stale_owner, [
            "restore confirm gen_a",
            "quit",
        ], load=True)
        check("j06_pruned_generation_refused",
              "Restore denied: cannot freeze target:" in out
              and "generation 'gen_a' unreadable" in out
              and snap(stale_owner) == ss,
              "retention (CURRENT + previous) pruned gen_a; "
              "confirming the stale target refuses at the "
              "freeze door and mutates nothing")
        rc, out = run_repl(stale_owner, [
            "restore confirm gen_bogus_999",
            "quit",
        ], load=True)
        check("j06_unknown_generation_refused",
              "Restore denied: cannot freeze target:" in out
              and "generation 'gen_bogus_999' unreadable" in out
              and snap(stale_owner) == ss,
              "an unknown generation id refuses identically — "
              "the door never guesses a target")

        # ---------------- J-06: cross-owner --------------------
        rc, out = run_repl(cross_owner, [
            "restore",
            "restore confirm gen_c",
            "quit",
        ])
        check("j06_cross_owner_no_generation_unavailable",
              "Restore unavailable: no committed generation for "
              "owner" in out,
              "a bare restore for an owner with no committed "
              "generation answers unavailable, not a guess")
        check("j06_cross_owner_confirm_refused",
              "Restore denied: cannot freeze target:" in out
              and "generation 'gen_c' unreadable" in out,
              "owner-namespaced generations: the foreign owner "
              "cannot freeze (hence cannot roll back to) the "
              "other owner's generation")
        check("j06_cross_owner_attempt_creates_no_state",
              state_files(cross_owner) == [],
              "the refused foreign attempts created no state "
              "files for the foreign owner at all")

        # ---------------- J-06: tamper injection ---------------
        rc, out = run_repl(tamper_owner, [
            CA, "27[Checkpoint] :: vault_one",
            "quit",
        ])
        st1 = snap(tamper_owner)
        rc, out = run_repl(tamper_owner, [
            CB, "27[Checkpoint] :: vault_two",
            "quit",
        ], load=True)
        st2 = snap(tamper_owner)
        member = _member_path(tamper_owner, "program", "vault_one")
        with open(member, "rb") as f:
            original = f.read()
        flipped = bytearray(original)
        flipped[len(flipped) // 2] ^= 0xFF
        with open(member, "wb") as f:
            f.write(bytes(flipped))
        try:
            rc, out = run_repl(tamper_owner, [
                "restore confirm vault_one",
                "quit",
            ], load=True)
        finally:
            with open(member, "wb") as f:
                f.write(original)
        check("j06_tampered_member_refused_at_freeze",
              "Restore denied: cannot freeze target:" in out
              and "member 'program' fingerprint mismatch" in out,
              "one flipped byte in the sealed program member: "
              "the freeze re-hash refuses the target before "
              "any restore step runs — a partial/corrupt "
              "restore never begins")
        check("j06_tamper_refusal_preserves_status_quo",
              snap(tamper_owner) == st2
              and current_generation_id(tamper_owner)
              == "vault_two",
              "after the refusal, live state and CURRENT are "
              "exactly the pre-attempt state — the evidence "
              "detected the tamper instead of absorbing it, "
              "and no restored status was faked")
        rc, out = run_repl(tamper_owner, [
            "restore confirm vault_one",
            "quit",
        ], load=True)
        check("j06_repaired_member_rolls_back",
              "Restored generation vault_one." in out
              and snap(tamper_owner) == st1,
              "with the member's original bytes restored, the "
              "same confirm succeeds — the refusal was the "
              "corruption, not a broken door")
    finally:
        for o in owners:
            cleanup(o)

    check("Z.cleanup", not _CLEANUP_ERRORS, "; ".join(_CLEANUP_ERRORS))
    failed = [n for n, ok, _ in RESULTS if not ok]
    print(f"JOURNEY_ROLLBACK: {len(RESULTS) - len(failed)}/{len(RESULTS)} PASS")
    if failed:
        print("FAILURES:", ", ".join(failed))
    return 1 if failed else 0


def smoke():
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
