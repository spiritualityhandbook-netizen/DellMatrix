#!/usr/bin/env python3
"""72-25 — Define/Alias/Compose failed-run non-publication:
the set-wide proof (evidence circuit; no defect expected).

Acceptance (original inventory): "Failed composition must
not publish a partially built semantic object."

Step 10 (B18) repaired Compose's publication order
(run-before-publish) and its suite proves the in-memory
core; d1_registry_spectrum_test proves Alias failure
non-mutation. This suite proves the SET-WIDE contract at
the public entry path, including the surfaces those
suites do not reach:

- A Compose whose define-run fails MID-BODY (first atom
  ran, second failed) publishes nothing.
- Invoking an attempted-and-failed name behaves exactly
  like invoking a never-defined name
  (malformed_composition) — no ghost object.
- Non-publication is visible ACROSS verbs: an Alias to a
  failed Compose name fails alias_missing and stores
  nothing (the name does not exist to point at), while an
  Alias to a published name binds.
- A failed REDEFINITION retains the prior body, and the
  retained body remains invocable. (A7's failing body is
  an unbound 47[Embed] — deterministic embed_unavailable;
  Q-C3.1 amendment, see the in-code note at A7.)
- Ring 1 (DD-51): a successful Alias arms the Diff
  baseline, so a standalone 89[Diff] after it succeeds
  instead of refusing baseline_missing (A9).
- A Define in an unchosen Branch arm never executes, so
  nothing is published; a normal Define publishes.
- Non-publication SURVIVES persistence: after the
  canonical save + load cycle (persist_rest — the path
  the REPL reloads through), the failed names are absent
  from the restored state and uninvocable, while the
  successful sibling composition is present and runs.

Labels: PUBLIC_ENTRY_PATH throughout (execute_seed;
persist_rest save/load is the program's own canonical
persistence path). Hygiene: uuid-unique owners;
exact-pattern cleanup; cleanup failures reported, never
swallowed.
"""
from __future__ import annotations

import sys
import uuid
from pathlib import Path

REPO = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, REPO)

RESULTS = []
_CLEANUP_ERRORS = []
RUN = uuid.uuid4().hex[:8]


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def _prog(tag):
    from form.open import Program
    from form.mandell.core_ii_exec import attach
    p = Program(owner=f"T7225{tag}{RUN}")
    attach(p)
    return p


def _run(p, chain):
    from form.mandell.executor import execute_seed
    return execute_seed(p, chain)


def _cleanup(tag):
    from form.persist import _STATE_DIR, _safe_owner
    from form.dell_matrix.nursery import owner_nursery_path
    owner = f"T7225{tag}{RUN}"
    state = Path(_STATE_DIR)
    safe = _safe_owner(owner)
    cands = [state / f"program_{safe}.json",
             Path(owner_nursery_path(owner))]
    cands += list(state.glob(f"*{safe}*"))
    for pth in set(cands):
        try:
            if pth.is_dir():
                import shutil
                shutil.rmtree(pth)
            elif pth.exists():
                pth.unlink()
        except OSError as exc:
            _CLEANUP_ERRORS.append(f"{pth}: {exc}")


TAGS = []


def main():
    tag = "A"; TAGS.append(tag)
    p = _prog(tag)
    st = p.core_ii

    out = _run(p, "99[Compose] :: part=70,89")
    check("A1.mid_body_failure_not_published",
          out["ok"] is False and "part" not in st.compositions,
          f"{out['error']!r} comps={dict(st.compositions)}")

    out = _run(p, "99[Compose] :: keep=70[Count]")
    check("A2.successful_compose_publishes",
          out["ok"] and st.compositions.get("keep") == "70[Count]")

    out = _run(p, "99[Compose] :: drop=89[Diff]")
    check("A3.failing_body_not_published",
          out["ok"] is False and "drop" not in st.compositions)

    out_f = _run(p, "99[Compose] :: drop")
    out_g = _run(p, "99[Compose] :: ghost")
    check("A4.failed_name_invokes_like_never_defined",
          out_f["ok"] is False and out_f["error"] == "malformed_composition"
          and out_g["ok"] is False
          and out_g["error"] == "malformed_composition",
          f"{out_f['error']!r} vs {out_g['error']!r}")

    out = _run(p, "98[Alias] :: adrop=drop")
    check("A5.alias_to_failed_name_missing",
          out["ok"] is False and out["error"] == "alias_missing"
          and "adrop" not in st.aliases)
    out = _run(p, "98[Alias] :: akeep=keep")
    check("A6.alias_to_published_name_binds",
          out["ok"] and st.aliases.get("akeep") == "keep")

    # Q-C3.1 amendment (Director ruling, mail 1a1cb916b4f20117):
    # A7's original failing body was 89[Diff] — it failed only
    # because no baseline existed. DD-51 Ring 1 made A6's Alias
    # note a baseline, so the Diff body now SUCCEEDS and the
    # redefinition publishes (failing-first probe:
    # c3diff/logs/amend_probe.log). The replacement body, an
    # unbound 47[Embed], fails deterministically with
    # embed_unavailable: the embed binding is runtime-only,
    # never persisted, and nothing in this suite binds one, so
    # the failure cannot depend on baselines, store contents,
    # or ambient state. (An Assert body cannot serve here: the
    # chain grammar rejects a nested :: inside a Compose label,
    # so that body would never run — same probe log.) The B18
    # invariant under test is unchanged: a genuinely failed
    # define-run never publishes and the prior body is retained.
    out = _run(p, "99[Compose] :: keep=47[Embed]")
    check("A7.failed_redefinition_retains_prior",
          out["ok"] is False and out["error"] == "embed_unavailable"
          and st.compositions.get("keep") == "70[Count]")
    out = _run(p, "99[Compose] :: keep")
    check("A8.retained_body_still_invocable", out["ok"])

    # DD-51 Ring 1 success path (the behavior that retired the
    # old A7 trigger): A6's Alias noted a baseline, so a
    # standalone Diff now executes instead of refusing
    # baseline_missing.
    out = _run(p, "89[Diff]")
    check("A9.alias_arms_baseline_diff_succeeds", out["ok"],
          f"{out.get('error')!r}")

    # Persistence: canonical save + load (the REPL's path).
    from form import persist_rest
    persist_rest.save(p)
    p2 = persist_rest.load(p.owner)
    from form.mandell.core_ii_exec import attach
    attach(p2)
    st2 = p2.core_ii
    check("P1.failed_names_absent_after_reload",
          "drop" not in st2.compositions
          and "part" not in st2.compositions,
          str(dict(st2.compositions)))
    check("P2.published_sibling_survives_reload",
          st2.compositions.get("keep") == "70[Count]"
          and st2.aliases.get("akeep") == "keep")
    out = _run(p2, "99[Compose] :: keep")
    check("P3.reloaded_composition_invocable", out["ok"])
    out = _run(p2, "99[Compose] :: drop")
    check("P4.reloaded_failed_name_still_a_ghost",
          out["ok"] is False and out["error"] == "malformed_composition")

    tag = "B"; TAGS.append(tag)
    pb = _prog(tag)
    stb = pb.core_ii
    out = _run(pb, "60[false] > 97[Define] :: hidden=55 "
                   "> 59[Else] > 55[Set] :: vis=1 > 61[Join]")
    check("B1.define_in_unchosen_arm_not_published",
          "hidden" not in stb.defs and stb.store.get("vis") == "1",
          f"defs={dict(stb.defs)} store={dict(stb.store)}")
    out = _run(pb, "97[Define] :: seen=55")
    check("B2.define_publishes", out["ok"]
          and stb.defs.get("seen") == "55")

    for t in TAGS:
        _cleanup(t)
    check("cleanup.no_errors", not _CLEANUP_ERRORS, str(_CLEANUP_ERRORS))

    total = len(RESULTS)
    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"define_compose_nonpublication_test: {passed}/{total} PASS")
    return 0 if passed == total else 1


def smoke():
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
