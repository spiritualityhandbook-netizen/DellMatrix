#!/usr/bin/env python3
"""GS-4 sandbox containment suite (failing-first origin: Director mail
1a1d05d91f6401dc, 2026-11-12; repair authorized by Director scope
ruling mail 1a1d077edcbc82e2, 2026-11-12).

The wall contract (Ace's Growth Selection Doctrine, 2026-11-12): "a
sandbox that doesn't effect anything outside of it" — growth involving
boxed (sandboxed) units must not use material from outside the wall.

The defect (reproduced independently twice on merged main @074b30f;
PR #403 + PR #402 comment 6827580827): default RingedGrowth pair
enumeration was wall-blind — cross-sandbox pairs were scored like any
pair (the wall entered only as _affinity's soft in_scope 0.2 penalty)
and produced (a) two-parent Solstice proposals spanning the wall and
(b) single-parent Equinox/Standstill drift offspring of boxed units
carrying outside units' tokens under inside-only lineage.

Published failing-first with A1/A2/A3/B2 red on main (6/10). The GS-4
repair filters candidate pair enumeration in RingedGrowth.run by
canonical Plane box membership (wall-key equality), receipts the
exclusion count (pairs_excluded_cross_sandbox, C-7), and leaves
unboxed output byte-for-byte identical — all ten checks green,
including the pre-existing controls that must never regress:
scope_ids containment, unboxed backward-compat, empty scope, and
invalid scope refusal.

Field (5 co-located units; same field as the PR #403 independent
probe so this suite is falsifiable against its published log):
  in_a, in_b   boxed into sandbox 'vault1'
  out_a        outside near-twin of in_a
  out_b        outside, moderate overlap
  out_c        outside, distant tokens (drift source)
Outside-only tokens are computed mechanically from the field texts.
"""
from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from form.open import open_program

OWNER_TAG = "GS4SANDBOX1112"
INSIDE = ["in_a", "in_b"]
OUTSIDE = ["out_a", "out_b", "out_c"]

FIELD = [
    ("in_a", "harbor lantern inkeep",
     "harbor lantern craft timber copper kettle song inkeep cellar vault"),
    ("in_b", "harbor lantern inforge",
     "harbor lantern craft timber copper kettle song inforge cellar vault"),
    ("out_a", "harbor lantern outkeep",
     "harbor lantern craft timber copper kettle song outkeep cellar vault "
     "axolotl azurite"),
    ("out_b", "harbor copper outdrift",
     "harbor lantern craft copper song outdrift axolotl azurite basalt"),
    ("out_c", "glacier tundra outpost",
     "glacier tundra obsidian wolf outpost fjord"),
]


def _cleanup(owner):
    import glob
    import shutil
    state = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state")
    for f in glob.glob(os.path.join(state, f"*{owner}*")):
        try:
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.remove(f)
        except FileNotFoundError:
            pass
        except OSError as e:
            raise RuntimeError(f"cleanup failed for {f}: {e}")


def _raw_words(text):
    return set(re.findall(r"[a-z]+", (text or "").lower()))


def _build(owner, box_inside):
    _cleanup(owner)
    p = open_program(owner)
    plane = p.cube.session.plane
    plane.units.clear()
    plane.sandboxes.clear()
    p.nursery.proposals.clear()
    for uid, label, words in FIELD:
        p.place(uid, label, words=words, x=0.0, y=0.0)
    if box_inside:
        plane.box(list(INSIDE), "vault1", label="gs4 vault")
    return p


def _snapshot(p):
    return [{
        "pid": pid,
        "kind": getattr(prop, "kind", None),
        "label": prop.label,
        "words": prop.words,
        "parents": list(prop.parents or []),
    } for pid, prop in p.nursery.proposals.items()]


def smoke() -> bool:
    print("=== GS-4 SANDBOX CONTAINMENT ===")
    fails = []

    def check(name, ok, detail):
        print(f"  [{'PASS' if ok else 'FAIL'}] {name} :: {detail}")
        if not ok:
            fails.append(name)

    in_set, out_set = set(INSIDE), set(OUTSIDE)
    inside_words, outside_words = set(), set()
    for uid, label, words in FIELD:
        (inside_words if uid in in_set else outside_words).update(
            _raw_words(label) | _raw_words(words))
    out_only_tokens = outside_words - inside_words

    # --- RUN A: boxed field, default growth — THE WALL CONTRACT ------
    p = _build(f"{OWNER_TAG}A", box_inside=True)
    res = p.grow_ideas(1)
    steps = res.get("steps") or [{}]
    pairs_scanned = steps[0].get("pairs_scanned")
    props = _snapshot(p)

    # A0 setup truth: the wall exists in the plane's own authority.
    check("A0 wall is real in plane authority",
          list(p.cube.session.plane.enhance_scope("in_a")) == ["in_b"],
          f"enhance_scope(in_a)={p.cube.session.plane.enhance_scope('in_a')}")

    # A1 enumeration: 5 units = 10 pairs; wall-respecting scans 4
    # (1 inside-inside + 3 outside-outside), never the 6 cross-wall.
    check("A1 enumeration excludes cross-wall pairs",
          pairs_scanned == 4,
          f"pairs_scanned={pairs_scanned} (10 = all pairs incl. 6 cross-wall; "
          f"4 = wall-respecting)")

    # A1b receipt (C-7): the exclusion count is receipted, never
    # silent — 6 cross-wall pairs excluded on this run's step.
    check("A1b receipt counts excluded cross-sandbox pairs (C-7)",
          steps[0].get("pairs_excluded_cross_sandbox") == 6
          and res.get("pairs_excluded_cross_sandbox") == 6,
          f"step={steps[0].get('pairs_excluded_cross_sandbox')} "
          f"total={res.get('pairs_excluded_cross_sandbox')} (6 expected)")

    # A2 manifestation 1: no proposal's parents span the wall.
    cross = [pr for pr in props
             if set(pr["parents"]) & in_set and set(pr["parents"]) & out_set]
    check("A2 no proposal parents span the wall",
          len(cross) == 0,
          f"cross-parented proposals={len(cross)} "
          f"{[(pr['pid'], pr['parents']) for pr in cross]}")

    # A3 manifestation 2: no single-parent (drift) offspring of a boxed
    # unit carries any outside-only token.
    drift = []
    for pr in props:
        if pr["parents"] and set(pr["parents"]) <= in_set:
            hits = sorted(out_only_tokens
                          & _raw_words(pr["label"] + " " + pr["words"]))
            if hits:
                drift.append((pr["pid"], pr["parents"], hits))
    check("A3 no boxed drift offspring carries outside-only tokens",
          len(drift) == 0,
          f"drift offspring carrying outside-only tokens={drift}")

    # --- RUN B (control): same field, NO sandbox — backward compat ---
    p2 = _build(f"{OWNER_TAG}B", box_inside=False)
    res2 = p2.grow_ideas(1)
    props2 = _snapshot(p2)
    steps2 = res2.get("steps") or [{}]
    check("B1 unboxed control still scans all pairs",
          steps2[0].get("pairs_scanned") == 10,
          f"pairs_scanned={steps2[0].get('pairs_scanned')} (10 expected)")
    sig_a = sorted((pr["kind"], tuple(pr["parents"]), pr["label"])
                   for pr in props)
    sig_b = sorted((pr["kind"], tuple(pr["parents"]), pr["label"])
                   for pr in props2)
    check("B2 boxed default output differs from unboxed (the wall acts)",
          sig_a != sig_b,
          f"boxed proposals={len(props)} unboxed proposals={len(props2)}; "
          f"identical={(sig_a == sig_b)}")

    # B3 receipt (C-7): the unboxed run receipts ZERO exclusions.
    check("B3 unboxed receipt shows zero exclusions (C-7)",
          steps2[0].get("pairs_excluded_cross_sandbox") == 0,
          f"step={steps2[0].get('pairs_excluded_cross_sandbox')} (0 expected)")

    # --- RUN E: mixed boxes + unboxed are strangers (C-3) ------------
    # Same field, but in_a/in_b are boxed into DIFFERENT sandboxes:
    # every pair involving a boxed unit must be a within-box pair, and
    # only the 3 unboxed-unboxed pairs may scan (pairs_scanned == 3,
    # 7 excluded).
    pe = _build(f"{OWNER_TAG}E", box_inside=False)
    plane_e = pe.cube.session.plane
    plane_e.box(["in_a"], "vaultA", label="gs4 vault A")
    plane_e.box(["in_b"], "vaultB", label="gs4 vault B")
    rese = pe.grow_ideas(1)
    stepse = rese.get("steps") or [{}]
    propse = _snapshot(pe)
    cross_e = [pr for pr in propse
               if (set(pr["parents"]) & in_set
                   and set(pr["parents"]) != {"in_a"}
                   and set(pr["parents"]) != {"in_b"})
               or (set(pr["parents"]) == {"in_a", "in_b"})]
    check("E1 mixed boxes: only unboxed-unboxed pairs scan",
          stepse[0].get("pairs_scanned") == 3
          and stepse[0].get("pairs_excluded_cross_sandbox") == 7,
          f"pairs_scanned={stepse[0].get('pairs_scanned')} "
          f"excluded={stepse[0].get('pairs_excluded_cross_sandbox')} "
          f"(3 scanned / 7 excluded expected)")
    check("E2 mixed boxes: no proposal crosses any wall",
          len(cross_e) == 0,
          f"crossing proposals={[(pr['pid'], pr['parents']) for pr in cross_e]}")

    # --- RUN C (control): scope_ids door contains — pre-existing -----
    p3 = _build(f"{OWNER_TAG}C", box_inside=True)
    res3 = p3.grow_ideas(1, scope_ids=list(INSIDE))
    props3 = _snapshot(p3)
    steps3 = res3.get("steps") or [{}]
    leaks3 = [pr for pr in props3
              if set(pr["parents"]) & out_set
              or (out_only_tokens
                  & _raw_words(pr["label"] + " " + pr["words"]))]
    check("C1 scope_ids growth scans only the selected pair",
          steps3[0].get("pairs_scanned") == 1,
          f"pairs_scanned={steps3[0].get('pairs_scanned')} (1 expected)")
    check("C2 scope_ids growth has zero leaks",
          len(leaks3) == 0,
          f"leaks={len(leaks3)}")

    # --- RUN D (controls): empty + invalid scope — pre-existing ------
    p4 = _build(f"{OWNER_TAG}D", box_inside=True)
    raised = None
    try:
        p4.grow_ideas(1, scope_ids=["missing_unit_xyz"])
    except ValueError as e:
        raised = str(e)
    check("D1 invalid scope ID refuses with ValueError",
          raised is not None and "not on plane" in raised,
          f"ValueError={raised!r}")
    res4 = p4.grow_ideas(1, scope_ids=[])
    props4 = _snapshot(p4)
    check("D2 empty scope grows nothing (no silent fallback to full)",
          len(props4) == 0,
          f"proposals={len(props4)} scope_mode={res4.get('scope_mode')}")

    # --- RUN F: malformed / unknown / stale-member boxed state ------
    # Director code-review finding (mail 1a1d0990c34b0d99): _wall_key
    # returns None for BOTH a genuinely unboxed unit and a unit with
    # sandboxed=True but sandbox_id=None — None==None equality would
    # admit the malformed unit as a wall-mate of unboxed peers
    # (fail-open under malformed/restored state: persist_rest restores
    # unit.sandboxed/unit.sandbox_id verbatim, and Plane.box() never
    # validates box membership). Canonical verdict on malformed
    # endpoints already exists: form/mandell/unit_containment.py F1
    # (Director review 2026-11-04) refuses them outright. These runs
    # construct each malformed state by direct field assignment (the
    # same state a verbatim restore can produce) and pin the repair:
    # such units are refused — excluded from pair enumeration with
    # the refusal receipted (malformed_box_units_refused) — never
    # collapsed to unboxed. Construction probes for every box/unbox
    # permutation reachable through the public box API are in the
    # run-F taxonomy comment in the repair report §11.
    F_UNITS = ["malf", "stale_a", "stale_b", "ghost", "ok_a", "ok_b"]

    def _f_base(tag, boxed):
        p = _build(f"{OWNER_TAG}F{tag}", box_inside=False)
        plane = p.cube.session.plane
        plane.units.clear()
        plane.sandboxes.clear()
        p.nursery.proposals.clear()
        for uid in F_UNITS:
            p.place(uid, f"flabel {uid}", words=f"fwords {uid}",
                    x=0.0, y=0.0)
        for uid in boxed:
            plane.box([uid], "realbox", label="gs4 real box")
        return p, plane

    # F-run driver: each malformed field is driven through the public
    # grow path; refusal evidence is read from the result receipt.
    def _f_run(tag, boxed, mutate):
        p, plane = _f_base(tag, boxed)
        mutate(plane)
        before = list(plane.units)
        res = p.grow_ideas(1)
        steps = res.get("steps") or [{}]
        props = _snapshot(p)
        return p, plane, res, steps, props, before

    def _pairs_touching(props, uid):
        return [pr for pr in props if uid in (pr["parents"] or [])]

    def _tokens_of(p, uid):
        return _raw_words(p.cube.session.plane.units[uid].label + " "
                          + p.cube.session.plane.units[uid].words)

    # F1/F2 — malformed boxed (sandbox_id None) beside unboxed peers.
    def _mk_malformed(plane):
        u = plane.units["malf"]
        u.sandboxed = True
        u.sandbox_id = None
        u.label = "harbor lantern malformed"
        u.words = ("harbor lantern craft timber copper kettle song "
                   "malformed cellar vault")

    pf, planf, resf, stepsf, propsf, _ = _f_run("1", [], _mk_malformed)
    f_refused = list(resf.get("malformed_box_units_refused") or [])
    check("F1 malformed boxed unit is refused, never wall-mate of unboxed",
          "malf" in f_refused
          and len(_pairs_touching(propsf, "malf")) == 0,
          f"refused={f_refused} "
          f"proposals_touching_malf={len(_pairs_touching(propsf, 'malf'))} "
          f"pairs_scanned={stepsf[0].get('pairs_scanned')} "
          f"excluded_cross={stepsf[0].get('pairs_excluded_cross_sandbox')}")
    drift_f = [pr for pr in propsf
               if pr["parents"] == ["malf"]
               and (out_only_tokens
                    & _raw_words(pr["label"] + " " + pr["words"]))]
    check("F2 malformed unit: no outside-token drift to or from it",
          len(drift_f) == 0
          and all(set(pr["parents"] or []) != {"malf"} for pr in propsf),
          f"drift_from_malf={[(pr['pid'], pr['parents']) for pr in drift_f]}")

    # F3 — unknown sandbox_id (names no sandbox in Plane.sandboxes).
    def _mk_ghost(plane):
        u = plane.units["ghost"]
        u.sandboxed = True
        u.sandbox_id = "no_such_box"
        u.label = "harbor lantern ghostbox"
        u.words = ("harbor lantern craft timber copper kettle song "
                   "ghostbox cellar vault")

    pg, plang, resg, stepsg, propsg, _ = _f_run("3", [], _mk_ghost)
    g_refused = list(resg.get("malformed_box_units_refused") or [])
    check("F3 unknown sandbox_id is refused (fail-closed)",
          "ghost" in g_refused
          and len(_pairs_touching(propsg, "ghost")) == 0,
          f"refused={g_refused} "
          f"proposals_touching_ghost={len(_pairs_touching(propsg, 'ghost'))}")

    # F4 — membership inconsistency, direction (i): two units claim
    # realbox; the Sandbox record lists only stale_a. Plane.box()
    # keeps both sides in sync through the API, so this state is
    # reachable only by field/record divergence (restore of a
    # hand-edited or partially-written save; see report §11) — but a
    # restore CAN produce it verbatim, so growth must fail closed.
    def _mk_stale(plane):
        sb = plane.sandboxes["realbox"]
        sb.member_ids = [m for m in sb.member_ids if m != "stale_b"]

    ps, plans, ress, stepss, propss, _ = _f_run(
        "4", ["stale_a", "stale_b"], _mk_stale)
    s_refused = list(ress.get("malformed_box_units_refused") or [])
    pair_stale = [pr for pr in propss
                  if set(pr["parents"] or []) == {"stale_a", "stale_b"}]
    check("F4 membership-inconsistent unit is refused; its claimed-mate pair never scores",
          "stale_b" in s_refused
          and "stale_a" not in s_refused
          and len(pair_stale) == 0,
          f"refused={s_refused} stale_pair_proposals={len(pair_stale)} "
          f"pairs_scanned={stepss[0].get('pairs_scanned')}")

    # F5 — well-formed boxed pair among the refused: still grows.
    check("F5 well-formed unboxed peers still grow beside refused units",
          stepss[0].get("pairs_scanned") == 6,
          f"pairs_scanned={stepss[0].get('pairs_scanned')} "
          f"(6 = the pairs among the 4 unboxed units; stale_a's 4 "
          f"cross-wall pairs excluded, stale_b refused outright)")

    total = 19
    print(f"GS-4 SANDBOX: {total - len(fails)}/{total} checks passed"
          + (f"; FAILING: {fails}" if fails else ""))
    for owner in ("A", "B", "C", "D", "E", "F1", "F3", "F4"):
        _cleanup(f"{OWNER_TAG}{owner}")
    return not fails


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
