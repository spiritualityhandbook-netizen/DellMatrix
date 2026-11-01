#!/usr/bin/env python3
"""Canonical regression authority (one list, one runner).

    python -m form.regress              # forward
    python -m form.regress --order rev  # reverse order
    python -m form.regress --twice      # run the list twice on the same state (exposes state coupling)
    python -m form.regress --passk ENTRY K  # run ONE entry K times, fresh copy per run (pass^k reliability)
    python -m form.regress --help       # usage only (exit 0, no entry runs); any bad argument exits 2 unrun

Each entry "module[:function]" (default function: smoke) runs in its own process:
    python -B -c "r = getattr(importlib.import_module(M), F)(); print(<per-run token> if r is True ...); sys.exit(...)"
All entries of one invocation run in ONE private temporary copy of the source tree (fresh form/state, no
writes to the checkout); --twice reuses that copy for the second pass. The copy is removed afterwards.

Entry GREEN only if: rc == 0 AND the function returned True (token printed after return) AND the last "n/m" count printed has m > 0 and
n == m AND no traceback was emitted. Run GREEN only if the list is non-empty, has no duplicate
(normalized) entries, covers every intended entry (LIST + every form/**/*_test.py), and every entry
executed GREEN. Anything else is RED (exit 1).
"""
from __future__ import annotations

import argparse
import os
import re
import secrets
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from typing import Iterable, List, Optional, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# 4 CI entries (form-smoke.yml history) + 17 *_test suites + core_ii_smoke.
LIST = [
    "form.open",
    "form.mandell.phrase_tests",
    "form.mandell.polyglot_tests",
    "form.accept:run",
    "form.dell_matrix.core_test",
    "form.foundation_acceptance_test",
    "form.lineage_authority_test",
    "form.lineage_semantic_closure_test",
    "form.mandell.control_runtime_test",
    "form.mandell.core_i_maturity_test",
    "form.mandell.core_ii_persist_test",
    "form.mandell.language_efficiency_test",
    "form.mandell.mandell_activation_test",
    "form.mandell.mandell_authority_convergence_test",
    "form.mandell.mandell_canonical_engine_test",
    "form.mandell.mandell_final_runtime_test",
    "form.mandell.mandell_meta_runtime_test",
    "form.mandell.query_reasoning_test",
    "form.mandell.spectrum_closure_test",
    "form.mandell.unified_runtime_test",
    "form.persist_full_roundtrip_test",
    "form.duobeta_live_test",
    "form.mandell.semantic_route_test",
    "form.mandell.flow_executor_test",
    "form.mandell.english_composer_test",
    "form.mandell.dcc_vi_test",
    "form.mandell.dcc_vii_test",
    "form.mandell.dcc_viii_test",
    "form.mandell.dcc_ix_test",
    "form.mandell.dcc_x_test",
    "form.mandell.dcc_xi_test",
    "form.mandell.dcc_xii_test",
    "form.mandell.dcc_xiii_test",
    "form.mandell.dcc_xiv_test",
    "form.mandell.dcc_xv_test",
    "form.mandell.dcc_xv_cross_process_test",
    "form.mandell.dcc_xvi_test",
    "form.mandell.dcc_xvi_atomicity_test",
    "form.mandell.dcc_xvii_test",
    "form.mandell.r3_permanent_regressions:smoke",
    "form.mandell.dcc_xviii_test",
    "form.mandell.dcc_xix_test",
    "form.mandell.dcc_xx_test",
    "form.mandell.p0r1_persist_test",
    "form.mandell.p1_idea_test",
    "form.mandell.p2_graph_test",
    "form.mandell.p2_dsc1_journal_proof",
    "form.mandell.p2_dsc1_r3_listener_proof",
    # P3 R3.1 — affinity/resonance reconciliation proof (GDP-001 Phase 3).
    "form.mandell.p3_r31_affinity_proof",
    # P3 R3.2 (Harmony): GDP-001 Phase 3, stream B.
    "form.mandell.p3_r32_harmony_proof",
    "form.mandell.pac_i_test",
    "form.mandell.cac_i_test",
    "form.mandell.ssi_i_test",
    "form.mandell.eoc_i_test",
    "form.mandell.pac_i_proofs_test",
    "form.mandell.ros_i_test",
    "form.mandell.dbel_i_test",
    "form.mandell.asi_i_test",
    "form.mandell.nbde_i_test",
    "form.mandell.fcnd_i_test",
    "form.mandell.leas_i_test",
    "form.mandell.cdpc_i_test",
    "form.mandell.rccr_i_test",
    "form.mandell.iac_i_test",
    "form.mandell.dell37_nurture_test",
    "form.mandell.set_detail_goals_test",
    "form.mandell.live_response_integrity_test",
    "form.mandell.iac_isolation_test",
    "form.mandell.dell87_refusal_test",
    "form.mandell.cmd_hardening_test",
    "form.mandell.r2_registry_reconciliation_test",
    "form.mandell.r2_semantic_honesty_test",
    "form.mandell.p0r3_execution_integrity_test",
    "form.equation_ledger_invariants_test",
    "form.dell_matrix.perspective_runtime_truth_checks",
    "form.mandell.p0_integrated_proof_test",
    "form.mandell.hic_i_test",
    "form.mandell.ekc_i_test",
    "form.mandell.aec_i_test",
    "form.mandell.odcg_i_test",
    "form.mandell.dla_i_test",
    "form.mandell.kie_i_test",
    "form.cn_ii_nav_test",
    "form.irr_i_find_test",
    "form.iri_i_test",
    "form.saoc_ii_test",
    "form.tpp_i_test",
    "form.greek_test",
    "form.dell_matrix.program_strength",
    "form.mandell.core_ii_smoke",
    # Master plan P3 — Program-surface wiring closures (TD-2/4/5/6/7
    # consolidation identities + wire-or-retire outcomes, REPL-level).
    "form.dell_matrix.p3_wiring_test",
    # Master plan P4 / SD-1 — dock provenance completion (subject in
    # origin, reason + task, dock_sessions evidence, snap registration).
    "form.mandell.p4_sd1_test",
    # Master plan P5 / SD-2 — semantic verbs RELATE/SYNTHESIZE/FLAG
    # (extended schema, coordinator snapshot activation, IdeaLab40
    # calibration against the probe corpus).
    "form.mandell.p5_sd2_test",
    # Master plan P6 / SD-3 — growth demotion (docked SYNTHESIZE
    # routing for pair crosses, labeled token fallback, REPL
    # connect grow).
    "form.mandell.p6_sd3_test",
    # Master plan P7 / SD-4 — scoped Director dock (verb allowlist,
    # recommendation records, scoped snapshot, adversarial scope
    # suite).
    "form.mandell.p7_sd4_test",
    # Master plan P8 / SD-5 — inside-out loop first full turn
    # (kind=design filing, loop ledger chain, REPL recommendation
    # display) + dormant-cluster disposition guards.
    "form.mandell.p8_sd5_test",
    # Master plan P9 — Exchange v1 (seed packets with receipts,
    # chain lint, gated cross-process import, replication counts).
    "form.mandell.p9_exchange_test",
    # Master plan P10 — flow-grammar conformance (parsed set ==
    # contract set == publicly executable set, all nine operators
    # proven at the REPL path).
    "form.mandell.p10_flow_grammar_test",
    # Master plan P11 — satellite disposition guards (sandbox
    # matrices retired per Ace's ruling; useful survivors live).
    "form.mandell.p11_satellites_test",
    # Master plan P12 — final closure guards (registry truth,
    # limitation honesty, README anchor, audit reconciliation).
    "form.mandell.p12_closure_test",
    "form.mandell.repair_r1_test",
    "form.mandell.repair_r2_test",
    "form.mandell.repair_r3_test",
    "form.mandell.pp1_stopwords_test",
    "form.dell_matrix.pp2_autonomy_charter_test",
    "form.dell_matrix.pp3_unknowns_test",
    "form.mandell.repair_r4_test",
    "form.dell_matrix.pp2b_rulings_test",
    "form.dell_matrix.pp4_bimo_dock_test",
    "form.mandell.pp5_flow_visual_test",
    "form.mandell.d1_stale_probes_test",
    "form.mandell.d1_proof_cards_test",
    "form.mandell.d1_dell84_copy_test",
    "form.mandell.d1_dell85_move_test",
    "form.mandell.d1_dell86_delete_test",
    "form.mandell.d1_dell87_replace_test",
    "form.mandell.d1_dell88_patch_test",
    "form.mandell.d1_dell51_select_test",
    "form.mandell.d1_dell54_query_test",
    "form.mandell.d1_dell56_get_test",
    "form.mandell.d1_dell57_compare_test",
    "form.mandell.d1_dell58_match_test",
    "form.mandell.d1_dell67_any_test",
    "form.mandell.d1_dell68_all_test",
    "form.mandell.d1_dell69_none_test",
    "form.mandell.d1_dell8_create_test",
    "form.mandell.d1_recon1_scope_test",
    "form.mandell.d1_recon2_matched_test",
    "form.mandell.d1_recon3_match_engine_test",
    "form.mandell.d1_recon4_create_skin_test",
    "form.mandell.d1_recon5_argument_loss_test",
    "form.mandell.d1_registry_leaf_test",
    "form.mandell.d1_registry_leaf2_test",
    "form.mandell.d1_registry_leaf3_test",
    "form.mandell.d1_registry_leaf4_test",
    "form.mandell.d1_registry_coreii_a_test",
    "form.mandell.d1_registry_coreii_b_test",
    "form.mandell.d1_registry_spectrum_test",
    # P3 R3.4 — geometry authority unification (GDP-001 Phase 3, Stream C):
    # verita.vesica_strength delegates to sacred_geometry.vesica (EQ-GEO-001).
    "form.mandell.p3_r34_geometry_proof",
    # P3 R3.5 — resonance/harmony integration (Stream D)
    "form.mandell.p3_r35_integration_proof",
    # P3 R3.6 — graph/harmony consumer + wiring world proof (GDP-001 Phase 3).
    "form.mandell.p3_r36_graph_harmony_proof",
    # Phase 5 — Nursery, Growth & Learning (GDP-001 Phase 5).
    "form.mandell.wo52_skeleton_test:smoke",
    "form.mandell.wo53_historical_test:smoke",
    "form.mandell.wo54_learning_test:smoke",
    "form.mandell.wo51_adversarial_test:smoke",
    "form.mandell.wo52_coherence_test:smoke",
    "form.mandell.wo54_consumers_test:smoke",
    "form.mandell.d20_reference_test:smoke",
    "form.mandell.absence_matrix_test:smoke",
    "form.mandell.writer_boundary_test:smoke",
    "form.mandell.compensation_test:smoke",
    "form.mandell.supersession_failure_test:smoke",
    "form.mandell.r61_authority_test:smoke",
    "form.mandell.r61_oracle_test:smoke",
    "form.mandell.r62_docking_test:smoke",
    "form.mandell.r63_rollback_test:smoke",
    "form.mandell.r63_amend_proof_test:smoke",
    "form.mandell.r64_multi_intelligence_test:smoke",
    "form.mandell.r65_separation_test:smoke",
    "form.mandell.r71_composition_test:smoke",
    "form.mandell.r72_studio_test:smoke",
    "form.mandell.r73_workshop_test:smoke",
    "form.mandell.r74_onboarding_test:smoke",
    "form.mandell.r75_forge_test:smoke",
    "form.mandell.r76_connected_test:smoke",
    "form.mandell.r77_grand_integration_test:smoke",
    "form.mandell.dock_transport_test:smoke",
    "form.mandell.gate_hardening_test:smoke",
    "form.mandell.lineage_label_test:smoke",
    "form.mandell.resonance_command_test:smoke",
    "form.mandell.duobeta_cross_session_test:smoke",
    "form.mandell.polyglot_user_path_test:smoke",
    "form.mandell.launchers_test:smoke",
    "form.mandell.projects_groups_test:smoke",
    "form.mandell.visual_ux_test:smoke",
    "form.mandell.passk_test:smoke",
    "form.mandell.p1_dedup_test:smoke",
    "form.mandell.p4_lifecycle_gravity_proof:smoke",
    "form.mandell.p4_placement_dynamics_proof:smoke",
    "form.mandell.p4_lattice_collision_proof:smoke",
    "form.mandell.p4_lattice_environment_proof:smoke",
    "form.mandell.p4_susx100_proof:smoke",
    "form.mandell.p4_acceptance_circuit:smoke",
    # P2 (evidence integrity): previously unregistered proof
    # harnesses + invariants, now under the canonical regress.
    "form.invariants:smoke",
    "form.mandell.confirm_crash_matrix:smoke",
    "form.mandell.lifecycle_totality_proof:smoke",
    "form.mandell.p1_idea_circuit:smoke",
    "form.mandell.p1_integrated_proof:smoke",
    "form.mandell.p1_r2_checkpoint_proof:smoke",
    "form.mandell.p1_r3_authoritative_proof:smoke",
    "form.mandell.p1_r4_livematrix_proof:smoke",
    "form.mandell.p2_acceptance_proof:smoke",
    "form.mandell.p2_adversarial_proof:smoke",
    "form.mandell.p2_microgate_proof:smoke",
    "form.mandell.p2_r1_adversarial_proof:smoke",
    "form.mandell.p2_susx100:smoke",
    "form.mandell.english_brain_150_loop:smoke",
    "form.mandell.regress_coverage_test:smoke",
    "form.af1_chain_args_test:smoke",
    "form.af2_delimiter_addressing_test:smoke",
    "form.af34_exchange_counters_test:smoke",
    "form.af5_session_bounds_test:smoke",
    "form.af6_import_batching_test:smoke",
    "form.mandell.symbiosis_ledger_test:smoke",
    "form.daf09_timeout_tree_test:smoke",
    "form.step3_security_test:smoke",
    "form.step3b_sanitize_chain_test:smoke",
    "form.step3c_sanitize_state_test:smoke",
    "form.step4_operand_transport_test:smoke",
    "form.step5_exchange_boundary_test:smoke",
    "form.step5b_exchange_durability_test:smoke",
    "form.step6_leaf_honesty_test:smoke",
    "form.step7_control_verdicts_test:smoke",
    "form.step8_transactions_test:smoke",
    "form.step9_diff_test:smoke",
]

TIMEOUT_S = 900
COPY_MARKER = ".dm_regress_copy"  # written into every private copy; run() refuses a copy as its src
_NM = re.compile(r"(\d+)\s*/\s*(\d+)")
_SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv"}


def normalize(entry: str) -> str:
    mod, _, fn = entry.strip().partition(":")
    return f"{mod.strip()}:{(fn.strip() or 'smoke')}"


def discovered_suites(src: str = ROOT) -> List[str]:
    """Every tracked-style form/**/*_test.py (and *_tests.py) suite.

    P2: discovery previously matched only the singular ``_test.py``
    suffix, so plural-named suites (phrase_tests, polyglot_tests) ran
    only because they also appear in LIST — a silent-skip hole if a
    plural suite were ever added without a LIST entry. Both suffixes
    are discovered now; regress_coverage_test asserts the union of
    LIST and discovery covers every test-like file on disk.
    """
    out = []
    base = os.path.join(src, "form")
    for d, dirs, files in os.walk(base):
        dirs[:] = sorted(x for x in dirs if x not in _SKIP_DIRS and not (d == base and x == "state"))
        for f in sorted(files):
            if f.endswith(("_test.py", "_tests.py")):
                rel = os.path.relpath(os.path.join(d, f[:-3]), src)
                out.append(normalize(rel.replace(os.sep, ".")))
    return out


def intended_entries(src: str = ROOT) -> List[str]:
    seen, out = set(), []
    for e in [normalize(x) for x in LIST] + discovered_suites(src):
        if e not in seen:
            seen.add(e)
            out.append(e)
    return out


def _copy_tree(src: str) -> str:
    dst = tempfile.mkdtemp(prefix="dm_regress_")
    state = os.path.join(src, "form", "state")

    def ignore(d, names):
        skip = {n for n in names if n in _SKIP_DIRS or n.endswith((".pyc", ".pyo"))}
        if os.path.abspath(d) == os.path.abspath(os.path.dirname(state)) and "state" in names:
            skip.add("state")
        return skip

    work = os.path.join(dst, "src")
    shutil.copytree(src, work, ignore=ignore, symlinks=True)
    open(os.path.join(work, COPY_MARKER), "w").close()  # every regression copy is identifiable
    return dst


def _proc_starttime(pid: int) -> Optional[int]:
    """The /proc start-time fingerprint of ONE process instance.

    Field 22 of /proc/<pid>/stat (clock ticks since boot). A PID is
    recycled by the kernel; (pid, starttime) identifies the instance
    that was actually witnessed. None when unreadable (process gone
    or /proc unavailable).
    """
    try:
        with open(f"/proc/{pid}/stat", "rb") as fh:
            stat = fh.read()
        # comm is parenthesised and may contain spaces/parens; fields
        # after the last ')' start at field 3 (state), so field 22
        # (starttime) is tail index 19.
        return int(stat[stat.rfind(b")") + 2:].split()[19])
    except (OSError, ValueError, IndexError):
        return None


def _descendant_identities(root_pid: int) -> List[Tuple[int, Optional[int]]]:
    """All live descendants of root_pid as (pid, starttime) identities,
    from /proc parent links.

    Snapshot BEFORE any kill: once the parent dies its children are
    reparented and the tree can no longer be reconstructed. Returns []
    where /proc is unavailable (the process-group kill still applies).
    """
    children = {}
    starttimes = {}
    try:
        entries = os.listdir("/proc")
    except OSError:
        return []
    for name in entries:
        if not name.isdigit():
            continue
        try:
            with open(os.path.join("/proc", name, "stat"), "rb") as fh:
                stat = fh.read()
            tail = stat[stat.rfind(b")") + 2:].split()
            ppid = int(tail[1])
            starttime = int(tail[19])
        except (OSError, ValueError, IndexError):
            continue
        pid = int(name)
        children.setdefault(ppid, []).append(pid)
        starttimes[pid] = starttime
    out, stack = [], list(children.get(root_pid, []))
    while stack:
        pid = stack.pop()
        out.append((pid, starttimes.get(pid)))
        stack.extend(children.get(pid, []))
    return out


def _pidfd_send_signal(fd: int, sig: int) -> None:
    """pidfd_send_signal(2) via ctypes (os has pidfd_open but, on
    Python 3.12, no send wrapper). Raises OSError on failure — notably
    ESRCH when the pinned instance is already dead, in which case the
    signal is delivered to NOBODY, never to a PID reuser."""
    import ctypes

    libc = ctypes.CDLL(None, use_errno=True)
    res = libc.syscall(424, fd, sig, None, 0)  # SYS_pidfd_send_signal
    if res != 0:
        err = ctypes.get_errno()
        raise OSError(err, os.strerror(err))


def _signal_identity(pid: int, starttime: Optional[int], sig: int) -> str:
    """Signal ONLY the witnessed process instance (pid, starttime).

    Identity-safe signalling (DAF-09 follow-up): a bare PID from a
    historical witness set proves nothing — the PID may have been
    recycled by an unrelated process. Returns a tri-state outcome:

    - "signalled": the signal was delivered through a pidfd, which
      pins the witnessed instance, after re-verifying the starttime
      following the open (closing the capture->open race).
    - "refused": the identity is missing or the process now at that
      PID is a different instance (or the pinned instance is already
      dead — pidfd_send_signal delivered the signal to NOBODY, never
      to a PID reuser). Nothing was signalled.
    - "unavailable": pidfd signalling could not be attempted at all
      (no os.pidfd_open, or pidfd_open failed). Nothing was signalled.

    There is NO kill(2) fallback for witnessed identities (DAF-09
    pidfd-hardening follow-up, Director Mode D ruling at 3234966;
    AGENTS.md law: no silent downgrade from a verified primitive).
    The earlier starttime check cannot close the check->kill PID-reuse
    window, so when the pidfd path is unavailable the cleanup is
    reported unavailable instead of degrading to a bare-PID signal.
    """
    if starttime is None:
        return "refused"
    if _proc_starttime(pid) != starttime:
        return "refused"  # different instance (or gone): never signal
    if not hasattr(os, "pidfd_open"):
        return "unavailable"
    try:
        fd = os.pidfd_open(pid)
    except OSError:
        return "unavailable"
    try:
        if _proc_starttime(pid) != starttime:
            return "refused"
        _pidfd_send_signal(fd, sig)
        return "signalled"
    except OSError:
        return "refused"  # pinned instance already dead: nobody signalled
    finally:
        os.close(fd)


def _identity_alive(pid: int, starttime: Optional[int]) -> bool:
    """True only while THE WITNESSED INSTANCE is alive and non-zombie.

    A recycled PID (different starttime) is not our process: it reads
    dead for our purposes, never as a survivor.
    """
    if starttime is None:
        return False
    try:
        with open(f"/proc/{pid}/stat", "rb") as fh:
            stat = fh.read()
        tail = stat[stat.rfind(b")") + 2:].split()
        if tail[0:1] == [b"Z"]:
            return False
        return int(tail[19]) == starttime
    except (OSError, ValueError, IndexError):
        return False


def _communicate_tracked(proc: "subprocess.Popen") -> Tuple[str, str]:
    """communicate() with a deadline, witnessing the tree while waiting.

    DAF-09 addendum: a descendant that leaves BOTH the ppid tree
    (reparented when its parent exits early) and the process group
    (setsid) is invisible to a kill-time snapshot. Snapshot the
    descendant set periodically DURING the wait and stash the union
    on the proc object, so _kill_process_tree can still reach every
    process that was witnessed as a tree member while attached.
    Only witnessed descendants are ever added — never a process
    matched by name or cmdline. Bounded: one /proc scan per poll
    slice (0.1s), only while this entry runs.

    DAF-09 follow-up: what is witnessed is an IDENTITY — (pid,
    starttime) — never a bare PID. A bare PID proves nothing at kill
    time (it may have been recycled); the identity is what the kill
    path is allowed to signal.
    """
    seen: List[Tuple[int, Optional[int]]] = []
    seen_set = set()
    deadline = time.monotonic() + TIMEOUT_S
    while True:
        for ident in _descendant_identities(proc.pid):
            if ident not in seen_set:
                seen_set.add(ident)
                seen.append(ident)
        proc._witnessed_identities = list(seen)
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise subprocess.TimeoutExpired(proc.args, TIMEOUT_S)
        try:
            return proc.communicate(timeout=min(0.1, remaining))
        except subprocess.TimeoutExpired:
            continue


# Diagnostics from the most recent _kill_process_tree call:
# {"signalled": [(pid, starttime), ...], "refused": [...],
#  "unavailable": [...]}. Read by run_entry (which holds no proc
# handle at its return site) and by the DAF-09 suite.
_LAST_KILL_REPORT = None


def _kill_process_tree(proc: "subprocess.Popen") -> None:
    """DAF-09: kill the WHOLE tree rooted at proc, then reap proc.

    The entry runs in its own session/process group (start_new_session),
    so killpg reaches ordinary descendants; the /proc descendant snapshot
    additionally reaches descendants that left the group without leaving
    the tree; the witnessed set from _communicate_tracked additionally
    reaches descendants that escaped BOTH (setsid + reparented before
    the snapshot) but were seen while still attached. Only PIDs in
    those sets / group are signalled — never unrelated processes.
    Bounded: one SIGKILL pass plus a bounded reap.

    DAF-09 follow-up: the snapshot and witnessed sets carry
    IDENTITIES (pid + starttime), and every non-group signal goes
    through _signal_identity — a process is signalled only when it
    is provably the witnessed instance. The process-group kill is
    session-scoped by construction (the entry runs in its own
    session), not history-based, and is unchanged.

    DAF-09 pidfd-hardening follow-up: the per-identity outcomes are
    collected into a kill report, stashed as proc._kill_report and
    as the module-level _LAST_KILL_REPORT (diagnostics for callers
    like run_entry, which has no proc handle at its return site, and
    for the suite). An identity whose pidfd could not be opened is
    reported "unavailable" — explicitly, never silently downgraded
    to a bare-PID signal.
    """
    global _LAST_KILL_REPORT
    root = proc.pid
    identities = _descendant_identities(root)
    known = set(identities)
    for ident in getattr(proc, "_witnessed_identities", []):
        if ident not in known:
            known.add(ident)
            identities.append(ident)
    # Legacy bare-PID entries (proc._witnessed_descendants) carry no
    # identity and are NEVER signalled: historical PID membership is
    # not proof of identity (DAF-09 follow-up, Director directive).
    if os.name == "posix":
        try:
            os.killpg(os.getpgid(root), signal.SIGKILL)
        except (ProcessLookupError, PermissionError, OSError):
            pass
    report = {"signalled": [], "refused": [], "unavailable": []}
    for pid, starttime in identities:
        outcome = _signal_identity(pid, starttime, signal.SIGKILL)
        report[outcome].append((pid, starttime))
    proc._kill_report = report
    _LAST_KILL_REPORT = report
    try:
        proc.kill()
    except (ProcessLookupError, OSError):
        pass
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        pass
    # Reap any descendant that was our direct child is impossible (they
    # are not); SIGKILL is final, so no further waiting is required for
    # the verdict. Give the kernel a brief bounded moment so a following
    # liveness check in the same process observes the kills. Liveness
    # is identity-aware: a recycled PID is not our survivor.
    deadline = time.monotonic() + 2.0
    while identities and time.monotonic() < deadline:
        alive = [ident for ident in identities
                 if _identity_alive(ident[0], ident[1])]
        if not alive:
            break
        identities = alive
        time.sleep(0.05)


class _Completed:
    def __init__(self, returncode, stdout, stderr):
        self.returncode, self.stdout, self.stderr = returncode, stdout, stderr


def run_entry(entry: str, cwd: str) -> Tuple[bool, str]:
    mod, _, fn = normalize(entry).partition(":")
    token = secrets.token_hex(8)  # proves the function RETURNED True (an early sys.exit(0) cannot print it)
    code = ("import importlib,sys; "
            f"r = getattr(importlib.import_module({mod!r}), {fn!r})(); "
            f"print('REGRESS_RETURNED_TRUE:{token}' if r is True else 'REGRESS_RETURNED_NOT_TRUE', flush=True); "
            "sys.exit(0 if r is True else 1)")
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    env.pop("PYTHONPATH", None)
    proc = subprocess.Popen([sys.executable, "-B", "-c", code], cwd=cwd, env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, start_new_session=True)
    try:
        stdout, stderr = _communicate_tracked(proc)
    except subprocess.TimeoutExpired:
        _kill_process_tree(proc)
        why = "TIMEOUT"
        # Pidfd-hardening: unavailable cleanup is explicit in the
        # verdict, never silent. In an environment where pidfd works
        # the unavailable set is empty and why stays exactly "TIMEOUT".
        unavail = getattr(proc, "_kill_report", {}).get("unavailable", [])
        if unavail:
            pids = ",".join(str(pid) for pid, _ in unavail)
            why += f" cleanup_unavailable={len(unavail)}:{pids}"
        return False, why
    except KeyboardInterrupt:
        _kill_process_tree(proc)
        unavail = getattr(proc, "_kill_report", {}).get("unavailable", [])
        if unavail:
            pids = ",".join(str(pid) for pid, _ in unavail)
            print(f"REGRESS cleanup_unavailable={len(unavail)}:{pids}",
                  flush=True)
        raise
    r = _Completed(proc.returncode, stdout, stderr)
    hits = _NM.findall(r.stdout)
    n, m = (int(hits[-1][0]), int(hits[-1][1])) if hits else (0, 0)
    tb = "Traceback (most recent call last)" in (r.stdout + r.stderr)
    returned = f"REGRESS_RETURNED_TRUE:{token}" in r.stdout
    ok = r.returncode == 0 and returned and bool(hits) and m > 0 and n == m and not tb
    why = f"rc={r.returncode} last={n}/{m}"
    if not returned:
        why += " NOT_RETURNED_TRUE"
    if not hits:
        why += " NO_COUNT"
    if tb:
        why += " TRACEBACK"
    if not ok and r.stderr.strip():
        why += " err=" + r.stderr.strip().splitlines()[-1][:90]
    return ok, why


def run_pass(entries: List[str], intended: Iterable[str], cwd: str, label: str = "") -> bool:
    norm = [normalize(e) for e in entries]
    if not norm:
        print(f"REGRESS{label}: EMPTY LIST -> RED")
        return False
    dups = sorted({e for e in norm if norm.count(e) > 1})
    if dups:
        print(f"REGRESS{label}: DUPLICATE ENTRY {dups} -> RED")
        return False
    omitted = [e for e in (normalize(x) for x in intended) if e not in set(norm)]
    if omitted:
        print(f"REGRESS{label}: OMITTED INTENDED ENTRY {omitted} -> RED")
        return False
    bad, executed = [], 0
    for e in norm:
        ok, why = run_entry(e, cwd)
        executed += 1
        print(f"{'OK ' if ok else 'RED'} {e:58s} {why}", flush=True)
        if not ok:
            bad.append(e)
    green = not bad and executed == len(norm)
    print(f"REGRESS{label}: {executed - len(bad)}/{len(norm)} -> {'GREEN' if green else 'RED'}"
          + (f" red={bad}" if bad else ""), flush=True)
    return green


def run(entries: Optional[List[str]] = None, intended: Optional[Iterable[str]] = None,
        src: str = ROOT, order: str = "fwd", twice: bool = False) -> bool:
    """Run entries (default LIST) against a private copy of ``src``. intended defaults to LIST + discovered.

    Recursion guard: a src that is itself a regression copy (COPY_MARKER present) is refused RED before anything
    is copied or run, whatever the entries, env or caller (self-entry, stubbed/re-spawned CLI, nested run())."""
    if os.path.exists(os.path.join(src, COPY_MARKER)):
        print(f"REGRESS: src {src} is a regression copy ({COPY_MARKER}); nested run refused -> RED", flush=True)
        return False
    entries = list(LIST if entries is None else entries)
    intended = list(intended_entries(src) if intended is None else intended)
    if order == "rev":
        entries.reverse()
    tmp = _copy_tree(src)
    try:
        cwd = os.path.join(tmp, "src")
        ok = run_pass(entries, intended, cwd, " pass1" if twice else "")
        if twice:
            ok = run_pass(entries, intended, cwd, " pass2") and ok
        return ok
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


PASSK_MAX = 20


def run_passk(entry: str, k: int, src: str = ROOT) -> bool:
    """Run ONE entry k times, each in a FRESH private copy of ``src`` (pass^k reliability).

    A single GREEN can be luck or state coupling; pass^k reports p/k honestly and is
    GREEN only at p == k. Every run gets its own _copy_tree, so no run can inherit
    another run's state. Usage errors (a regression copy as src, k outside
    1..PASSK_MAX, an entry not intended for src) print a PASSK error line and return
    False WITHOUT running anything."""
    e = normalize(entry)
    if os.path.exists(os.path.join(src, COPY_MARKER)):
        print(f"PASSK: src {src} is a regression copy ({COPY_MARKER}); refused, nothing run", flush=True)
        return False
    if not isinstance(k, int) or isinstance(k, bool) or k < 1 or k > PASSK_MAX:
        print(f"PASSK: k must be an integer in 1..{PASSK_MAX} (got {k!r}); nothing run", flush=True)
        return False
    if e not in intended_entries(src):
        print(f"PASSK: unknown entry {e}; nothing run", flush=True)
        return False
    passed = 0
    for i in range(1, k + 1):
        tmp = _copy_tree(src)
        try:
            ok, why = run_entry(e, os.path.join(tmp, "src"))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        passed += 1 if ok else 0
        print(f"PASSK run {i}/{k}: {'OK ' if ok else 'RED'} {e} {why}", flush=True)
    print(f"PASSK: {e} {passed}/{k} -> {'GREEN' if passed == k else 'RED'}", flush=True)
    return passed == k


class _Once(argparse.Action):
    """Store an option at most once: a repeated or conflicting --order/--twice is a usage error."""

    def __call__(self, parser, namespace, values, option_string=None):
        seen = namespace.__dict__.setdefault("_given", set())
        if self.dest in seen:
            parser.error(f"{option_string} given more than once (repeated or conflicting)")
        seen.add(self.dest)
        setattr(namespace, self.dest, True if self.nargs == 0 else values)


def _parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="python -m form.regress", allow_abbrev=False,
                                 description="Canonical regression runner (one list, one process per entry).")
    ap.add_argument("--order", choices=("fwd", "rev"), default="fwd", action=_Once,
                    help="entry order (fwd|rev); --order rev and --order=rev are equivalent")
    ap.add_argument("--twice", nargs=0, default=False, action=_Once,
                    help="run the list twice on the same state (exposes state coupling)")
    ap.add_argument("--passk", nargs=2, default=None, action=_Once, metavar=("ENTRY", "K"),
                    help="run ONE entry K times (1..20), fresh copy per run; conflicts with --order/--twice")
    return ap


def main(argv: Optional[List[str]] = None) -> int:
    """Strict CLI: every argument is validated BEFORE any entry runs. --help/-h prints usage and exits 0 with
    zero entries run and no verdict; any unknown, malformed, abbreviated, repeated or extra token exits 2."""
    a = list(sys.argv[1:] if argv is None else argv)
    ap = _parser()
    if "--" in a:
        print(ap.format_usage().rstrip() + "\nerror: '--' is not accepted", file=sys.stderr)
        return 2
    try:
        ns = ap.parse_args(a)
    except SystemExit as e:
        return 0 if e.code in (0, None) else 2
    if ns.passk is not None:
        given = ns.__dict__.get("_given", set())
        if "order" in given or "twice" in given:
            print("error: --passk conflicts with --order/--twice", file=sys.stderr)
            return 2
        entry_raw, k_raw = ns.passk
        try:
            k = int(k_raw)
        except (TypeError, ValueError):
            print(f"error: --passk K must be an integer in 1..{PASSK_MAX} (got {k_raw!r})", file=sys.stderr)
            return 2
        if k < 1 or k > PASSK_MAX:
            print(f"error: --passk K must be in 1..{PASSK_MAX} (got {k})", file=sys.stderr)
            return 2
        if normalize(entry_raw) not in intended_entries(ROOT):
            print(f"error: --passk unknown entry {normalize(entry_raw)}", file=sys.stderr)
            return 2
        ok = run_passk(entry_raw, k)
        print(f"PASSK FINAL: {'GREEN' if ok else 'RED'}")
        return 0 if ok else 1
    ok = run(order=ns.order, twice=ns.twice)
    print(f"REGRESS FINAL: {'GREEN' if ok else 'RED'} (order={ns.order}{', twice' if ns.twice else ''})")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
