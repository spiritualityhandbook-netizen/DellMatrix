#!/usr/bin/env python3
"""Part VII / GP-E27 — journey harness family 8: J-10 AI assist,
J-22 Outage/reconnect.

Written failing-first at code stage and registered in
form/regress.py LIST in the same commit (omitted-entry law).

Contracts — Edition 1 file 06 (06_JOURNEY_ACCEPTANCE.md),
executed verbatim where constructible at this head:

  J-10 AI assist: "Dock permitted provider/agent as Psalm,
  submit scoped suggestion, display provider/model + grant +
  reason; Nursery receives PENDING, never auto confirmed."
  Failure oracle: "Provider outage, prompt over-cap, response
  stop_reason, protected-value canaries, revoked grant and
  cross-owner injection refuse; local Matrix continues
  offline."

  J-22 Provider outage / reconnect (plan section 5.2.1):
  "dock a provider, sever it mid-session, reconnect;
  expected: no duplicate confirmation, grant state
  consistent, in-flight suggestion either completed once or
  refused with receipt — never landed twice."

Execution tier: PUBLIC_ENTRY_PATH — every journey action
runs in a literal `python3 -m form.repl` subprocess against
a per-run isolated owner; state comparison after cold
reload uses the persistence loader (reloaded vs reloaded,
never in-memory vs reloaded). The dock's public path is the
Connected World session (`connect`): the provider is
selected BY NAME only (default 'fake': deterministic,
offline; credentials are read from the host environment,
never entered in the REPL), `ask <prompt>` docks lazily and
creates a PENDING Nursery proposal, `leave` saves the
session evidence and undocks (the dock handle is
runtime-only).

Grounded behavior (each expectation verified first-hand in
scratch-owner probes, 2026-11-21, before this suite was
written):
  - `ask draft an idea about harbor weather vanes` answers
    "Proposal docked_idea_4984 created — PENDING in the
    Nursery (provider=fake, model=fake:valid). It is not
    confirmed and carries no authority; review it with
    'proposals'." The review face marks the proposal as
    docked on its face: origin
    "dock:connect:<owner>:fake:fake:valid", reason "docked
    propose by connect:<owner> via fake (model fake:valid)",
    and the SD-1 evidence join "task: propose · session
    <id8>". The loader record agrees (status pending, kind
    "new", the same origin and reason; the pid is NOT a live
    unit), the program's dock_sessions evidence carries the
    pid with task "propose" and model "fake:valid", and no
    grant is issued, displayed, or carried anywhere: the
    proposal record and the evidence entry hold no grant
    field — docking confers no authority by construction.
  - The proposal is still pending after cold reload, with
    the evidence join intact. The human path is the only
    landing path: `confirm <pid>` answers 'Confirmed.
    "Docked Idea" is live.'; a second confirm refuses "not
    found or not pending" (no duplicate confirmation);
    `reject <pid>` on a second docked proposal leaves it
    rejected and non-live. Inside the connect session
    itself, `confirm <pid>` is refused as out of scope
    ("that is not a connect command here") — the docked
    context holds no confirm power of its own.
  - Outage legs, all inside one connect session: `provider
    nosuchthing` then ask refuses "DOCK_FAILED: unknown
    provider 'nosuchthing'"; `provider gemini` (a real
    bridge provider with no host credentials) then ask
    refuses "Ask failed (provider_failure): provider gemini
    failed: missing GOOGLE_API_KEY / GEMINI_API_KEY" (the
    sanitized cause; the suite pins the refusal class, not
    the environment-specific detail); `provider fake` then
    ask succeeds — exactly one proposal exists afterwards.
    Repeated asks mint distinct suffixed pids, each pending,
    each attributed to its own session's evidence; two
    connect sessions leave two dock-session evidence
    records and two connection-session records.
  - Canary leg: an ask line carrying a grant-handle-shaped
    canary (grant_ + 32 hex chars, the recognized protected
    format) is rejected by the connect session's fail-closed
    screen — "Rejected: PROTECTED_MATERIAL." — before any
    routing, and the canary string appears nowhere in the
    transcript. Over-cap leg: an ask whose prompt is
    1,000,005 chars refuses "Ask failed (prompt_too_large):
    Prompt exceeds 1000000 chars." Neither refusal creates
    a proposal; an ordinary ask right after succeeds, and
    after `leave` a local create works — the Matrix
    continues offline.
  - Cross-owner leg: a foreign owner's `confirm <pid>` and
    `reject <pid>` against the dock owner's pid both refuse
    "not found or not pending"; the foreign nursery is
    empty and the foreign loader holds neither the proposal
    nor a unit under that pid (state is owner-namespaced).

  FINDING 1 (recorded at baseline; SUPERSEDED on integrated
  main, verified first-hand during the Part VII staging
  reconciliation, 2026-11-26): at the baseline head the
  auto-confirm sweep was ORIGIN-BLIND — under the human's
  explicit `auto confirm on` opt-in the next `grow ideas`
  swept the DOCKED proposal too (status "confirmed", landed
  in the auto_staging sandbox box). That was Part VI matrix
  row A12 (origin-blind auto-confirm). The landed
  confirmation wave replaced the blanket sweep with the
  grant-based contract (Director's 2026-11-24 auto-confirm
  decisions: grants tied to exact idea and contents,
  single-use receipts; the FI-011 door landed in #520):
  with no grant covering a proposal, the opt-in grow now
  accepts NOTHING — verified 2026-11-26 in scratch-owner
  probes for both the docked proposal and the owner's own
  growth proposals, in-session and across reload: all stay
  PENDING, unplaced, unconfirmed. J-10's "never auto
  confirmed" therefore now holds unconditionally. The suite
  pins the current fence: default OFF never sweeps, and the
  opt-in sweep without a grant never sweeps either.
  RESIDUAL WART, recorded not fixed in this lane: the
  opt-in banner still reads "every grow accepts all nursery
  proposals", wording the grant gate no longer performs —
  a display-truth item surfaced in the staging package for
  the Director.
  FINDING 2 (recorded, not fixed): growth from inside the
  connect session prints "Growth (docked): 1 new + 2
  evolved proposal(s) — all PENDING review", but every
  proposal it produced carries origin "growth:token" on
  the review face and in the loader record: the fake
  provider's SYNTHESIZE response does not pass the
  semantic schema, so SD-3's per-pair token fallback
  authored the crosses. The proposal-level provenance is
  truthful; the one-line connect receipt does not disclose
  the fallback. A receipt-precision wart of the same class
  as A.7's stale-count finding; the suite pins the
  proposal-level truth (all pending, all token-labeled,
  the cross parented by exactly the Harbor pair).

  UNCOVERED at baseline, recorded not smoothed: the
  failure oracle's "response stop_reason" case — a bridge
  transport outcome not constructible offline at the
  public path (the credential-less bridge provider refuses
  before any response exists; that refusal IS exercised).
  The "revoked grant" case as a presented object: no grant
  is ever issued to a docked session, so there is no grant
  object to revoke or present — refusal is by construction,
  evidenced by the no-grant checks, not by a revocation
  event. The hostile FakeProvider modes ("authority",
  "canary_error", "reflect", "timeout", "failure",
  "malformed", "empty") are NOT selectable at the public
  path: the connect `provider` command takes a name only
  and the host dock() call never exposes fake_mode there —
  by design. (No suite at this head was found exercising
  the non-valid modes; the module comment's r62 pointer
  does not resolve to a file at this head — reported as
  unproven, never as "not there".)

Baseline posture (plan section 5.1(iii)): this suite runs
against the pre-Parts main as a labeled BASELINE harness
proof. Its grades are evidence about the harness and the
current program, recorded in
director-reports/GRAND_SYNCHRONIZATION_REHEARSAL_2026-11-20.md;
the GP-E27 rehearsal executions proper run against merged
Parts I + II.

Run: python3 -m form.journey_dock_test
"""

import os
import re
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

CA = ("create an idea called Harbor Lantern detail: harbor lantern "
      "craft timber copper kettle song cellar vault goals: keep "
      "the harbor lit")
CB = ("create an idea called Harbor Forge detail: harbor lantern "
      "craft timber copper kettle song forge cellar vault goals: "
      "work the harbor forge")
CANARY = "grant_" + "0123456789abcdef" * 2
BIG_PROMPT = "word " * 200001  # 1,000,005 chars > the 1,000,000 cap


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
    """Loader-basis snapshot: units, proposal records, boxes,
    dock evidence, connection-session count."""
    prog = persist_load(owner)
    plane = prog.cube.session.plane
    units = {uid: {"label": u.label,
                   "parents": list(getattr(u, "parents", None) or []),
                   "origin": getattr(u, "origin", None)}
             for uid, u in plane.units.items()}
    props = {}
    for pid, p in prog.nursery.proposals.items():
        props[pid] = {
            "status": p.status,
            "kind": p.kind,
            "origin": p.origin,
            "reason": p.reason,
            "parents": list(p.parents or []),
            "lifecycle_state": p.lifecycle_state,
        }
    boxes = {sid: sorted(sb.member_ids)
             for sid, sb in plane.sandboxes.items()}
    evidence = {}
    for rec in (getattr(prog, "dock_sessions", None) or {}).values():
        if isinstance(rec, dict):
            for entry in rec.get("proposals") or []:
                if isinstance(entry, dict) and entry.get("pid"):
                    evidence[entry["pid"]] = {
                        "task": entry.get("task"),
                        "model": entry.get("model"),
                        "origin": entry.get("origin"),
                        "keys": sorted(entry.keys()),
                    }
    return {"units": units, "props": props, "boxes": boxes,
            "evidence": evidence,
            "connections": len(
                getattr(prog, "connection_sessions", None) or {}),
            "summary": prog.nursery.summary()}


def ask_pid(out):
    m = re.search(r"Proposal (\S+) created", out)
    return m.group(1) if m else None


def main():
    dock_owner = f"JDock{RUN}"
    human_owner = f"JHuman{RUN}"
    out_owner = f"JOut{RUN}"
    canary_owner = f"JCanary{RUN}"
    sweep_owner = f"JSweep{RUN}"
    foreign_owner = f"JForeign{RUN}"
    grow_owner = f"JGrow{RUN}"
    owners = (dock_owner, human_owner, out_owner, canary_owner,
              sweep_owner, foreign_owner, grow_owner)
    for o in owners:
        cleanup(o)
    try:
        # Isolation boundary, proven — not assumed (a fresh
        # Program() in this codebase loads persisted state by
        # default; the boundary is the per-run unique owner +
        # verified-empty start).
        check("dock_isolation_boundary_clean_start",
              all(state_files(o) == [] for o in owners),
              "no state files exist for any of the seven per-run "
              "owners before the sessions start")

        # ---------------- J-10: dock -> ask -> PENDING ---------
        rc, out = run_repl(dock_owner, [
            "connect", "status",
            "ask draft an idea about harbor weather vanes",
            "leave", "proposals", "save", "quit"])
        pid = ask_pid(out)
        check("j10_repl_exit_clean",
              rc == 0 and "Traceback" not in out,
              f"rc={rc} traceback={'Traceback' in out}")
        check("j10_status_shows_provider_fake_undocked",
              "Provider: fake (offline deterministic) · docked: no"
              in out,
              "the connect status face names the selected provider "
              "and its offline-deterministic nature before any dock")
        check("j10_ask_receipt_displays_provider_model_pending",
              pid is not None
              and f"Proposal {pid} created — PENDING in the Nursery "
                  f"(provider=fake, model=fake:valid)" in out
              and "It is not confirmed and carries no authority"
              in out,
              "the ask receipt displays provider + model and states "
              "on its face that the proposal is PENDING and "
              "authority-free")
        check("j10_review_face_marks_docked_provenance",
              f"origin: dock:connect:{dock_owner}:fake:fake:valid"
              in out
              and f"reason: docked propose by connect:{dock_owner} "
                  f"via fake (model fake:valid)" in out
              and "task: propose · session " in out,
              "the Nursery review face marks the proposal as docked: "
              "origin carries subject/provider/model, the derived "
              "reason names all three, and the SD-1 evidence join "
              "shows the task kind and session")
        s = snap(dock_owner)
        cp = s["props"].get(pid) or {}
        ev = s["evidence"].get(pid) or {}
        check("j10_loader_record_pending_not_a_unit",
              cp.get("status") == "pending"
              and cp.get("kind") == "new"
              and cp.get("origin") == (f"dock:connect:{dock_owner}"
                                       f":fake:fake:valid")
              and cp.get("reason") == (
                  f"docked propose by connect:{dock_owner} via fake "
                  f"(model fake:valid)")
              and pid not in s["units"],
              "the loader record agrees with the review face: the "
              "docked suggestion is a pending proposal, not a live "
              "unit — docking landed nothing by itself")
        check("j10_session_evidence_links_proposal_no_grant",
              ev.get("task") == "propose"
              and ev.get("model") == "fake:valid"
              and ev.get("origin") == cp.get("origin")
              and "grant" not in (ev.get("keys") or [])
              and "grant" not in (cp.get("origin") or "")
              and "grant" not in (cp.get("reason") or "")
              and s["connections"] >= 1,
              "the durable dock-session evidence links the pid to "
              "its task and the ACTUAL model, the connection session "
              "itself is on the record, and no grant is issued, "
              "displayed, or carried by either record")
        rc, out = run_repl(dock_owner, [
            "proposals", f"lineage {pid}", "quit"], load=True)
        check("j10_cold_reload_still_pending_marked",
              "task: propose · session " in out
              and f"Proposal {pid} [new] Docked Idea" in out
              and "status: pending" in out,
              "after cold reload the proposal is still pending and "
              "still visibly marked as docked — time and restart do "
              "not launder a suggestion into a landing")

        # ---------------- J-10: the human gate is the only door --
        rc, out = run_repl(human_owner, [
            "connect", "ask draft the first docked candidate",
            "leave", "save", "quit"])
        hpid1 = ask_pid(out)
        rc, out = run_repl(human_owner, [
            "connect", f"confirm {hpid1}", "leave",
            f"confirm {hpid1}", "save", "quit"], load=True)
        check("j10_docked_context_cannot_confirm_own_proposal",
              "that is not a connect command here" in out,
              "inside the docked session a confirm command is "
              "refused as out of scope — the docked context holds "
              "no confirm power, not even over its own proposal")
        check("j10_human_confirm_is_the_landing",
              '"Docked Idea" is live' in out,
              "the human's confirm outside the docked session is "
              "what lands the suggestion, and nothing else did")
        rc, out = run_repl(human_owner, [
            "connect", "ask draft the second docked candidate",
            "leave", "save", "quit"], load=True)
        hpid2 = ask_pid(out)
        rc, out = run_repl(human_owner, [
            f"reject {hpid2}", "save", "quit"], load=True)
        rc, out = run_repl(human_owner, [
            f"confirm {hpid1}", "quit"], load=True)
        check("j10_reconfirm_refuses_no_duplicate",
              "Could not confirm: not found or not pending" in out,
              "a second confirm of the landed proposal refuses — "
              "a docked suggestion can land exactly once")
        s = snap(human_owner)
        check("j10_confirm_and_reject_reconcile_after_reload",
              hpid1 in s["units"]
              and (s["props"].get(hpid1) or {}).get("status")
              == "confirmed"
              and hpid2 is not None
              and (s["props"].get(hpid2) or {}).get("status")
              == "rejected"
              and hpid2 not in s["units"],
              "after cold reload: the confirmed docked proposal is "
              "a live unit with a confirmed record; the rejected "
              "one is a rejected record and never became a unit")

        # ---------------- J-22: outage -> reconnect ------------
        rc, out = run_repl(out_owner, [
            "grow mode", "connect",
            "provider nosuchthing", "ask draft during outage one",
            "provider gemini", "ask draft during outage two",
            "provider fake", "ask draft after reconnect",
            "leave", "proposals", "save", "quit"])
        opid = ask_pid(out)
        check("j22_unknown_provider_dock_refused",
              "DOCK_FAILED: unknown provider 'nosuchthing'" in out,
              "severing to an unknown provider refuses at the dock "
              "with a named receipt — no proposal, no session")
        check("j22_credentialless_provider_refused",
              "Ask failed (provider_failure)" in out,
              "a real bridge provider with no host credentials "
              "refuses the ask as a provider failure with its "
              "sanitized cause — the outage lands nothing")
        check("j22_reconnect_lands_exactly_once",
              opid is not None
              and len(re.findall(r"Proposal \S+ created", out)) == 1
              and out.count("Nursery has 1 proposal(s)") == 1,
              "after reconnect the retried suggestion completes "
              "exactly once: one creation receipt, one pending "
              "proposal — the refused in-flight asks landed zero "
              "times and the retry did not double-land")
        rc, out = run_repl(out_owner, [
            f"confirm {opid}", f"confirm {opid}", "grow mode",
            "save", "quit"], load=True)
        s = snap(out_owner)
        check("j22_no_duplicate_confirmation_after_reconnect",
              '"Docked Idea" is live' in out
              and "Could not confirm: not found or not pending"
              in out
              and opid in s["units"]
              and (s["props"].get(opid) or {}).get("status")
              == "confirmed"
              and not any(v.get("status") == "pending"
                          for v in s["props"].values()),
              "the reconnected proposal confirms once and only "
              "once; the reload shows one live unit, a confirmed "
              "record, and nothing left pending")
        check("j22_policy_state_consistent_across_outage",
              out.count("auto_confirm_grow=OFF") >= 1
              and (s["props"].get(opid) or {}).get("origin")
              == f"dock:connect:{out_owner}:fake:fake:valid",
              "grant/policy state is untouched by the outage: the "
              "auto-confirm mode still reads OFF after reconnect, "
              "and the landed record's provenance still names the "
              "reconnected provider truthfully")

        # ---------------- J-10 negatives: canary / cap / local --
        rc, out = run_repl(canary_owner, [
            "connect",
            f"ask leak this {CANARY} please",
            "ask " + BIG_PROMPT,
            "ask a perfectly ordinary request",
            "leave",
            "create an idea called Local Lantern detail: local "
            "work continues offline",
            "proposals", "save", "quit"])
        cpid = ask_pid(out)
        check("j10_protected_canary_refused_and_never_echoed",
              "Rejected: PROTECTED_MATERIAL." in out
              and CANARY not in out,
              "an ask carrying a grant-handle-shaped canary is "
              "rejected by the fail-closed screen before routing, "
              "and the canary value appears nowhere in the "
              "transcript")
        check("j10_prompt_over_cap_refused",
              "Ask failed (prompt_too_large): Prompt exceeds "
              "1000000 chars." in out,
              "a prompt past the disclosed cap refuses by name "
              "(prompt_too_large) instead of being silently "
              "trimmed or sent")
        s = snap(canary_owner)
        check("j10_refusals_create_nothing_local_continues",
              cpid is not None
              and len(s["props"]) == 1
              and (s["props"].get(cpid) or {}).get("status")
              == "pending"
              and "local_lantern" in s["units"],
              "the two refusals created no proposals; the ordinary "
              "ask after them landed as the owner's only pending "
              "proposal, and a local create after leaving the dock "
              "works — the Matrix continues offline")

        # ---------------- J-10 fence: the auto-confirm sweep ----
        rc, out = run_repl(sweep_owner, [
            "connect", "ask draft the sweep candidate",
            "leave", "save", "quit"])
        spid = ask_pid(out)
        rc, out = run_repl(sweep_owner, [
            "grow mode", "grow ideas", "save", "quit"], load=True)
        s = snap(sweep_owner)
        check("j10_default_mode_never_sweeps_docked_proposal",
              "auto_confirm_grow=OFF" in out
              and (s["props"].get(spid) or {}).get("status")
              == "pending"
              and spid not in s["units"]
              and not any(spid in members
                          for members in s["boxes"].values()),
              "with the mode at its default OFF, a grow leaves the "
              "docked proposal pending, unplaced, and unconfirmed "
              "— the dock path itself never auto-confirms")
        rc, out = run_repl(sweep_owner, [
            "auto confirm on", "grow ideas", "save", "quit"],
            load=True)
        s = snap(sweep_owner)
        check("j10_optin_docked_proposal_never_swept",
              "every grow accepts all nursery proposals" in out
              and (s["props"].get(spid) or {}).get("status")
              == "pending"
              and spid not in s["units"]
              and not any(spid in members
                          for members in s["boxes"].values()),
              "FINDING 1 SUPERSEDED (see header): the opt-in is "
              "still disclosed on the banner's face, but under "
              "the landed grant-based confirmation contract the "
              "sweep without an exact-idea grant accepts "
              "nothing — the docked proposal stays pending, "
              "unplaced, and unconfirmed")

        # ---------------- J-10 negative: cross-owner -----------
        rc, out = run_repl(foreign_owner, [
            f"confirm {pid}", f"reject {pid}", "proposals", "quit"])
        s = snap(foreign_owner)
        check("j10_cross_owner_injection_refuses",
              "Could not confirm: not found or not pending" in out
              and "Could not reject: not found or not pending"
              in out
              and "Nursery is empty." in out
              and pid not in s["props"] and pid not in s["units"],
              "a foreign owner can neither confirm nor reject the "
              "dock owner's proposal: both refuse, the foreign "
              "nursery is empty, and the foreign state holds "
              "neither the proposal nor a unit under its pid")

        # ---------------- J-10 adjacency: docked growth --------
        rc, out = run_repl(grow_owner, [
            CA, CB, "save", "connect", "grow", "leave",
            "proposals", "save", "quit"])
        s = snap(grow_owner)
        crosses = [v for v in s["props"].values()
                   if v.get("parents") == ["harbor_lantern",
                                           "harbor_forge"]]
        check("j10_docked_growth_proposals_pending_token_truth",
              "Growth (docked):" in out
              and "all PENDING review" in out
              and len(s["props"]) == 3
              and all(v.get("status") == "pending"
                      for v in s["props"].values())
              and all((v.get("origin") or "") == "growth:token"
                      for v in s["props"].values())
              and len(crosses) == 1
              and sorted(s["units"]) == ["harbor_forge",
                                         "harbor_lantern",
                                         "welcome"],
              "FINDING 2 pinned at baseline: growth inside the "
              "docked session leaves every proposal PENDING and "
              "the cross parented by exactly the Harbor pair, but "
              "the proposal-level provenance truthfully reads "
              "growth:token for all three — the docked mind "
              "authored none of them (SD-3 fallback), whatever "
              "the one-line receipt's '(docked)' label says; no "
              "live unit changed")
    finally:
        for o in owners:
            cleanup(o)

    check("Z.cleanup", not _CLEANUP_ERRORS, "; ".join(_CLEANUP_ERRORS))
    failed = [n for n, ok, _ in RESULTS if not ok]
    print(f"JOURNEY_DOCK: {len(RESULTS) - len(failed)}/{len(RESULTS)} PASS")
    if failed:
        print("FAILURES:", ", ".join(failed))
    return 1 if failed else 0


def smoke():
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
