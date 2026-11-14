#!/usr/bin/env python3
"""C7.Profile — DD-39 baseline (MWL 149): Dell 49 [Profile] as the
Matrix's speedometer.

Contract (plan §12.38a DD-39 RESOLVED BY ACE + §14 C7 acceptance):
- Profile runs a DELIBERATE BENCHMARK on DISPOSABLE state (never
  the live program): a declared workload of N ideas is built on a
  throwaway owner, then the named stages place -> pulse -> growth
  -> save -> load are timed with a monotonic clock
  (time.perf_counter), each stage isolated so a failure is named,
  never swallowed into a pass.
- The receipt (structured `profile_report` on the result) carries
  kind=BENCHMARK (real observations vs deliberate benchmarks are
  distinct; OBSERVED mode is a separate later circuit),
  environment identity (python version, platform), workload
  identity (idea count, stage sequence), per-stage seconds and
  shares, harness overhead measured by an empty-workload
  calibration and disclosed as its own line, and an unaccounted
  remainder: stages + overhead + unaccounted reconcile to the
  total, printed, never silently rounded away.
- Embedding is ABSENT / OFF-by-design in the standalone benchmark
  (dock-only; §14 forbids silently contacting a provider): the
  stage row exists, carries no fabricated 0.00, and a tripwire
  proves zero provider contact.
- 'Nursery update' is named honestly as a growth SUB-STAGE (no
  standalone operation exists); it is not a peer stage and cannot
  be selected on its own.
- The largest-share stage is NAMED as an observation
  ("largest: <stage> <pct>%"); share alone is never a verdict.
- DRAGGING is defined by Ace (Q-ACE-C7P.1 ANSWERED 2026-11-12):
  "Dragging occurs when lag affects the functionality or the
  capability of anything, any process. Otherwise it's not
  dragging." The report's `dragging` list names only stages
  whose lag DEMONSTRABLY IMPAIRED function — in v1, a stage
  that FAILED by raising a timeout-class error. A clean stage
  with the largest share is NOT dragging (pinned); a stage
  that fails for a non-timing reason is FAILED, not dragging
  (pinned). No share threshold exists (Q-C7P.5 resolved).
- Timings are RECEIPT-ONLY in v1 (Q-C7P.2 default (b)): no new
  timings store is built; the receipt itself carries the full
  per-stage timings. Kept-timings is a named follow-up.
- Purity: the live program is byte-identical before/after except
  the one retained receipt token note_seed(49, 'Profile') ->
  history '49[Profile]'. status() is never called on this path,
  so the transitive persona_matrix write-on-read is unreachable
  from Dell 49 (sentinel-pinned).
- Operand grammar (Q-C7P.6 default): bare = the standard
  benchmark; ':: <stage>' = that stage only ('resonance' aliases
  pulse); an unknown label REFUSES ok=False skipped=True with the
  reason named — retiring the stub's ignore-the-label echo.
"""
from __future__ import annotations

import glob
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from form.open import open_program
from form.mandell.executor import execute_seed

STATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state")
TIMED_STAGES = ["place", "pulse", "growth", "save", "load"]


def _cleanup(owner):
    import shutil
    for f in glob.glob(os.path.join(STATE_DIR, f"*{owner}*")):
        try:
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.remove(f)
        except FileNotFoundError:
            pass
        except OSError as e:
            raise RuntimeError(f"cleanup failed for {f}: {e}")


def _program(owner):
    _cleanup(owner)
    return open_program(owner)


def _msgs(r):
    return [m for m in r.get("messages", [])
            if not m.startswith(("Mandell:", "English:"))]


def _stages(rep):
    return {s["name"]: s for s in rep.get("stages") or []}


def _board_mod():
    from form.dell_matrix import profile_board
    return profile_board


def smoke() -> bool:
    print("=== C7.PROFILE (DD-39) ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}"
              + (f" | {detail}" if detail and not ok else ""))
        r.append(bool(ok))

    # -- 1. Bare run: the standard benchmark, fully receipted.
    p = _program("C7ProfileT1")
    res = execute_seed(p, "49[Profile]")
    rep = res.get("profile_report") or {}
    st = _stages(rep)
    rec("t1_executed_ok", res.get("ok") is True, str(res.get("error")))
    rec("t1_report_present",
        rep.get("kind") == "BENCHMARK" and rep.get("dell") == 49,
        str(rep)[:160])
    rec("t1_verdict_complete", rep.get("verdict") == "COMPLETE",
        str(rep.get("verdict")))
    rec("t1_all_stages_timed",
        all((st.get(n) or {}).get("status") == "TIMED"
            and isinstance((st.get(n) or {}).get("seconds"), float)
            and (st.get(n) or {}).get("seconds") >= 0
            for n in TIMED_STAGES),
        str({n: st.get(n) for n in TIMED_STAGES})[:240])
    emb = st.get("embedding") or {}
    rec("t1_embedding_absent",
        emb.get("status") == "ABSENT" and emb.get("seconds") is None
        and "dock" in (emb.get("note") or "").lower(),
        str(emb))
    timed_sum = sum((st.get(n) or {}).get("seconds") or 0
                    for n in TIMED_STAGES)
    total = rep.get("total_seconds") or 0
    rec("t1_reconciles",
        all(isinstance((st.get(n) or {}).get("seconds"), float)
            for n in TIMED_STAGES)
        and total > 0 and rep.get("overhead_seconds") is not None
        and rep.get("overhead_seconds") >= 0
        and rep.get("unaccounted_seconds") is not None
        and abs(timed_sum + rep["overhead_seconds"]
                + rep["unaccounted_seconds"] - total) < 1e-6,
        f"stages={timed_sum} overhead={rep.get('overhead_seconds')} "
        f"unaccounted={rep.get('unaccounted_seconds')} total={total}")
    largest = rep.get("largest_stage") or {}
    rec("t1_largest_named",
        largest.get("name") in TIMED_STAGES
        and abs(largest.get("share", -1)
                - max(st[n]["share"] for n in TIMED_STAGES)) < 1e-9
        and any(m.startswith("  largest:") for m in _msgs(res)),
        str(largest))
    lines = _msgs(res)
    rec("t1_lines_present",
        lines and lines[0] == "Profile: COMPLETE"
        and any(m.startswith("  overhead:") for m in lines)
        and any(m.startswith("  total:") for m in lines)
        and any("embedding" in m and "ABSENT" in m for m in lines),
        str(lines)[:240])

    # -- 2. Operand grammar: single stage, honest refusals.
    p = _program("C7ProfileT2")
    res = execute_seed(p, "49[Profile]:: pulse")
    rep2 = res.get("profile_report") or {}
    timed2 = [s["name"] for s in rep2.get("stages") or []
              if s.get("status") == "TIMED"]
    rec("t2_single_stage_pulse",
        res.get("ok") is True and timed2 == ["pulse"]
        and rep2.get("verdict") == "COMPLETE",
        f"timed={timed2} verdict={rep2.get('verdict')}")
    hist_before = list(p.history)
    bad = execute_seed(p, "49[Profile]:: nonsense")
    rec("t2_unknown_refuses",
        bad.get("ok") is False and bad.get("skipped") is True
        and "nonsense" in str(bad.get("error") or "")
        and any("refused" in m for m in _msgs(bad)),
        str(bad)[:200])
    nur = execute_seed(p, "49[Profile]:: nursery")
    rec("t2_nursery_refuses_named",
        nur.get("ok") is False and nur.get("skipped") is True
        and "sub-stage of growth" in str(nur.get("error") or ""),
        str(nur.get("error"))[:160])
    rec("t2_refusal_notes_nothing", list(p.history) == hist_before,
        f"{hist_before} -> {list(p.history)}")

    # -- 3. Live-program purity: the instrument never perturbs
    #       the measured system (it measures a disposable one).
    p = _program("C7ProfileT3")
    execute_seed(p, "50[Manifest] :: c7p_keepsake")
    execute_seed(p, "37[Nurture] :: C7 Profile Rose")
    p.persona_lens = None
    p.persona_matrix.active = "SENTINEL_UNTOUCHED"  # any status()
    # routing flips this to persona_lens (None) on read.

    def digest(prog):
        return {
            "units": sorted((u, getattr(x, "label", ""))
                            for u, x in prog.cube.session.plane.units.items()),
            "nursery": prog.nursery.summary(),
            "history": list(prog.history),
            "enhance": (prog.enhance.on, prog.enhance.level,
                        prog.enhance.session_pulses,
                        dict(prog.enhance.state.scores)),
            "pm_active": prog.persona_matrix.active,
            "lens": prog.persona_lens,
            "keys": len(prog.keys.keys),
            "lattice": (len(prog.lattice.cells), prog.lattice.size),
            "generation": prog.duo.generation,
        }

    before = digest(p)
    res = execute_seed(p, "49[Profile]")
    after = digest(p)
    hist_ok = after.pop("history") == before.pop("history") + ["49[Profile]"]
    rec("t3_digest_identical", after == before,
        str({k: (before[k], after[k]) for k in before
             if before[k] != after[k]})[:300])
    rec("t3_history_exactly_one_receipt", hist_ok,
        f"history tail {list(p.history)[-2:]}")
    rec("t3_persona_sentinel_untouched",
        p.persona_matrix.active == "SENTINEL_UNTOUCHED",
        str(p.persona_matrix.active))

    # -- 4. Embedding: ABSENT with ZERO provider contact.
    calls = []
    try:
        from form.llm import bridge as _bridge
        from form.dell_matrix import embed_bind as _eb
        orig_embed = _bridge.LLMBridge.embed
        orig_embed_text = _eb.embed_text

        def _trip_embed(self, *a, **k):
            calls.append("LLMBridge.embed")
            raise AssertionError("provider contacted by benchmark")

        def _trip_text(*a, **k):
            calls.append("embed_bind.embed_text")
            raise AssertionError("provider contacted by benchmark")

        _bridge.LLMBridge.embed = _trip_embed
        _eb.embed_text = _trip_text
        try:
            p = _program("C7ProfileT4")
            res = execute_seed(p, "49[Profile]")
        finally:
            _bridge.LLMBridge.embed = orig_embed
            _eb.embed_text = orig_embed_text
        trip_ok = True
    except Exception as e:
        res, trip_ok = {}, False
        rec("t4_tripwire_installed", False, f"{type(e).__name__}: {e}")
    if trip_ok:
        rep4 = res.get("profile_report") or {}
        st4 = _stages(rep4)
        rec("t4_zero_provider_calls", calls == [] and res.get("ok") is True,
            f"calls={calls}")
        rec("t4_absent_not_zero",
            (st4.get("embedding") or {}).get("seconds") is None
            and isinstance((st4.get("place") or {}).get("seconds"), float),
            str(st4.get("embedding")))

    # -- 5. A stage that raises is FAILED and named; the board
    #       completes; the failed stage is never a timed pass.
    try:
        pb = _board_mod()
        orig_save = pb.STAGE_FUNCS["save"]

        def _bomb(prog, ctx):
            raise RuntimeError("c7profile bomb")

        pb.STAGE_FUNCS["save"] = _bomb
        try:
            p = _program("C7ProfileT5")
            res = execute_seed(p, "49[Profile]")
            raised = ""
        except Exception as e:  # Profile itself must not raise
            res, raised = {}, f"{type(e).__name__}: {e}"
        finally:
            pb.STAGE_FUNCS["save"] = orig_save
        rep5 = res.get("profile_report") or {}
        st5 = _stages(rep5)
        rec("t5_board_returns", not raised and res.get("ok") is True,
            raised)
        rec("t5_failed_stage_named",
            (st5.get("save") or {}).get("status") == "FAILED"
            and "RuntimeError" in ((st5.get("save") or {}).get("note") or "")
            and rep5.get("verdict") == "PARTIAL"
            and all((st5.get(n) or {}).get("status") == "TIMED"
                    for n in ("place", "pulse", "growth", "load")),
            f"{rep5.get('verdict')} | {st5.get('save')}")
    except Exception as e:
        rec("t5_board_returns", False, f"setup: {type(e).__name__}: {e}")
        rec("t5_failed_stage_named", False, "setup failed")

    # -- 6. Receipt identity: kind, environment, workload.
    import platform as _platform
    p = _program("C7ProfileT6")
    res = execute_seed(p, "49[Profile]")
    rep6 = res.get("profile_report") or {}
    wl = rep6.get("workload") or {}
    env = rep6.get("environment") or {}
    try:
        std_ideas = _board_mod().STANDARD_IDEAS
    except Exception:
        std_ideas = None
    rec("t6_kind_benchmark_no_observed",
        rep6.get("kind") == "BENCHMARK"
        and "OBSERVED" not in json.dumps(rep6)
        and not any("OBSERVED" in m for m in _msgs(res)),
        str(rep6.get("kind")))
    rec("t6_environment_identity",
        env.get("python") == _platform.python_version()
        and env.get("platform") == _platform.platform(),
        str(env))
    rec("t6_workload_identity",
        wl.get("ideas") == std_ideas and wl.get("stages") == TIMED_STAGES
        and wl.get("mode") == "standard",
        str(wl))

    # -- 7. Monotonic discipline (mutant pin): durations derive
    #       from perf_counter; a wall-clock substitution fails.
    try:
        import inspect
        src = inspect.getsource(_board_mod())
        rec("t7_monotonic_source",
            "perf_counter" in src and "time.time(" not in src
            and "utcnow" not in src, "")
    except Exception as e:
        rec("t7_monotonic_source", False, f"{type(e).__name__}: {e}")

    # -- 8. Largest-stage naming is an observation, not a verdict.
    try:
        pb = _board_mod()
        orig_place = pb.STAGE_FUNCS["place"]

        def _slow_place(prog, ctx):
            import time as _t
            # Decisive dominance: growth — the heaviest real
            # stage — runs ~0.3s here; 1.5s cannot lose to it.
            _t.sleep(1.5)
            return orig_place(prog, ctx)

        pb.STAGE_FUNCS["place"] = _slow_place
        try:
            p = _program("C7ProfileT8")
            res = execute_seed(p, "49[Profile]")
        finally:
            pb.STAGE_FUNCS["place"] = orig_place
        rep8 = res.get("profile_report") or {}
        lg8 = rep8.get("largest_stage") or {}
        rec("t8_dominant_stage_named",
            lg8.get("name") == "place" and lg8.get("share", 0) > 0.5,
            str(lg8))
    except Exception as e:
        rec("t8_dominant_stage_named", False,
            f"setup: {type(e).__name__}: {e}")
    p = _program("C7ProfileT8B")
    res = execute_seed(p, "49[Profile]")
    # Amended in the Q-ACE-C7P.1 correction: the original pin also
    # required the WORD "dragging" to be absent, pinning the
    # pre-ruling default. Ace's ruling makes the dragging line
    # mandatory; the surviving pin is that no share THRESHOLD
    # verdict exists. Dragging semantics are pinned in section 12.
    rec("t8_no_threshold_verdict",
        not any("threshold" in m.lower() for m in _msgs(res))
        and (res.get("profile_report") or {}).get("verdict") == "COMPLETE",
        str(_msgs(res))[:200])

    # -- 9. Repeatability + disposable hygiene: same stage SET,
    #       and no benchmark state is left behind.
    p = _program("C7ProfileT9")
    ra = execute_seed(p, "49[Profile]")
    rb = execute_seed(p, "49[Profile]")
    set_a = sorted(s["name"] for s in (ra.get("profile_report") or {})
                   .get("stages") or [] if s.get("status") == "TIMED")
    set_b = sorted(s["name"] for s in (rb.get("profile_report") or {})
                   .get("stages") or [] if s.get("status") == "TIMED")
    rec("t9_repeat_same_stage_set",
        ra.get("ok") is True and rb.get("ok") is True
        and set_a == set_b == sorted(TIMED_STAGES)
        and (ra.get("profile_report") or {}).get("verdict") == "COMPLETE"
        and (rb.get("profile_report") or {}).get("verdict") == "COMPLETE",
        f"{set_a} vs {set_b}")
    leftovers = glob.glob(os.path.join(STATE_DIR, "*ProfileBench*"))
    rec("t9_disposable_cleaned", leftovers == [], str(leftovers))

    # -- 10. Receipt-only timings (Q-C7P.2 default (b), adapted
    #        from grounding case 10): the receipt itself carries
    #        the full per-stage timings; NO timings store exists;
    #        consecutive receipts are independent.
    p = _program("C7ProfileT10")
    r1 = execute_seed(p, "49[Profile]").get("profile_report") or {}
    r2 = execute_seed(p, "49[Profile]").get("profile_report") or {}
    st10 = _stages(r1)
    rec("t10_receipt_carries_full_timings",
        all(isinstance((st10.get(n) or {}).get("seconds"), float)
            for n in TIMED_STAGES)
        and "previous" not in r1 and "history" not in r1,
        str([ (n, (st10.get(n) or {}).get("seconds")) for n in TIMED_STAGES]))
    store_leftovers = [f for f in glob.glob(os.path.join(STATE_DIR, "*"))
                       if "profilebench" in os.path.basename(f).lower()
                       or "profile_timing" in os.path.basename(f).lower()]
    rec("t10_no_timings_store", store_leftovers == [],
        str(store_leftovers))
    rec("t10_runs_independent",
        (r1.get("workload") or {}).get("run")
        != (r2.get("workload") or {}).get("run")
        and (r1.get("workload") or {}).get("run") is not None,
        f"{(r1.get('workload') or {}).get('run')} vs "
        f"{(r2.get('workload') or {}).get('run')}")

    # -- 11. Neighbours hold: Schema still owns status; status()
    #        itself is untouched.
    p = _program("C7ProfileT11")
    rs = execute_seed(p, "39[Schema]")
    rec("t11_schema_neighbour_ok",
        rs.get("ok") is True
        and (rs.get("schema_board") or {}).get("verdict") == "VALID",
        str((rs.get("schema_board") or {}).get("verdict")))
    rec("t11_status_unchanged", len(p.status()) == 32,
        f"{len(p.status())} keys")

    # -- 12. Dragging (Ace's definition, Q-ACE-C7P.1 answered):
    #        lag that impaired function/capability — never share.
    p = _program("C7ProfileT12")
    res = execute_seed(p, "49[Profile]")
    rep12 = res.get("profile_report") or {}
    rec("t12_clean_largest_not_dragging",
        rep12.get("dragging") == []
        and (rep12.get("largest_stage") or {}).get("name") == "growth",
        f"dragging={rep12.get('dragging')} "
        f"largest={rep12.get('largest_stage')}")
    rec("t12_dragging_line_none_wording",
        any(m.startswith("  dragging: none") and "impaired function" in m
            for m in _msgs(res)),
        str([m for m in _msgs(res) if "dragging" in m])[:200])
    try:
        pb = _board_mod()
        orig_pulse = pb.STAGE_FUNCS["pulse"]

        def _timeout_pulse(prog, ctx):
            raise TimeoutError(
                "bounded wait exhausted after 5.00s (synthetic double)")

        pb.STAGE_FUNCS["pulse"] = _timeout_pulse
        try:
            p = _program("C7ProfileT12B")
            res = execute_seed(p, "49[Profile]")
        finally:
            pb.STAGE_FUNCS["pulse"] = orig_pulse
        rep12b = res.get("profile_report") or {}
        st12b = _stages(rep12b)
        drag12b = rep12b.get("dragging") or []
        rec("t12_timeout_stage_is_dragging",
            [d.get("name") for d in drag12b] == ["pulse"]
            and "TimeoutError" in (drag12b[0].get("reason") or "")
            and (st12b.get("pulse") or {}).get("status") == "FAILED"
            and rep12b.get("verdict") == "PARTIAL"
            and any(m.startswith("  dragging: pulse (")
                    for m in _msgs(res)),
            f"dragging={drag12b} verdict={rep12b.get('verdict')}")
    except Exception as e:
        rec("t12_timeout_stage_is_dragging", False,
            f"setup: {type(e).__name__}: {e}")
    try:
        pb = _board_mod()
        orig_save12 = pb.STAGE_FUNCS["save"]

        def _bomb12(prog, ctx):
            raise RuntimeError("c7profile bomb (non-timing)")

        pb.STAGE_FUNCS["save"] = _bomb12
        try:
            p = _program("C7ProfileT12C")
            res = execute_seed(p, "49[Profile]")
        finally:
            pb.STAGE_FUNCS["save"] = orig_save12
        rep12c = res.get("profile_report") or {}
        st12c = _stages(rep12c)
        rec("t12_nontiming_failure_not_dragging",
            rep12c.get("dragging") == []
            and (st12c.get("save") or {}).get("status") == "FAILED",
            f"dragging={rep12c.get('dragging')} "
            f"save={st12c.get('save')}")
    except Exception as e:
        rec("t12_nontiming_failure_not_dragging", False,
            f"setup: {type(e).__name__}: {e}")

    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
