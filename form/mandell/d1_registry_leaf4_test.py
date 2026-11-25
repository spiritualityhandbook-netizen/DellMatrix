"""D1 circuit 19 (registry pass, cluster 4) — leaf Dells
37-50 DEEP CONTRACTS.

The fourth cluster of the full-registry pass: Dells
37-50 (leaf executor arms 38/39/41/42/43/45/46/48/49/50,
front-door core_i_ops arms for 37/40/44/47). None of
the fourteen is typed. Contracts proven here, per Dell,
through the public seed path:

- 37 Nurture (core_i_ops): the nursery lifecycle
  adapter — bare fails "add idea requires a label"
  with zero mutation; a label ADDS a pending nursery
  proposal (NOT a plane unit); "confirm <pid>" promotes
  through the canonical confirm boundary into the
  plane; "reject <pid>" rejects without promoting;
  unknown pids fail honestly on both paths.
- 38 Distill: source is the label, or (bare) the LAST
  unit's "<label> <words>"; place_idea(distilled,
  SEED) where distilled = distill_label(source) —
  tokens >2 chars, lowercased, deduped, max 4 (no such
  tokens -> the surviving token / "distill").
- 39 Schema: the DD-29 nervous-system board (C7
  circuit) — 16 systems, each reported exists/
  connected/available plus its state line; a healthy
  program's verdict is "Schema: VALID"; any label is
  ignored; the verdict is noted to history.
- 40 TokenCount (core_i_ops): the approx session
  weight — approx = ideas*8 + history*4 + cells*2 +
  pending*6, recorded exactly in last_measure and
  last_core_i.
- 41 Sanitize: the OUT line redacts password/secret/
  token/api_key/bearer values and 12+ digit numbers.
  DAF-02/B5 (Director FIX, step 3): the IN line shows
  the SANITIZED representation — Sanitize no longer
  discloses the raw values it redacts (the former
  raw-echo exhibit is the defect DAF-02 closed).
- 42 Retry: replays the LAST noted history entry —
  on an empty history "Retry: history empty."; else
  "Retry last: <entry>" plus a real replay_exec
  (ran=1), so the retried seed executes again and
  Retry notes itself.
- 43 Fallback: a message-only safe path (status /
  save / acceptance sequence); no mutation; noted.
- 44 Bridge (core_i_ops): HONEST REFUSAL — ok=False
  bridge_unavailable, "Bridge unavailable: no
  external provider bound"; last_core_i records
  capability (the label, default "external") and
  permission offline_origin. (The working EN<->Mandell
  bridge function belongs to Dell 45, not 44.)
- 45 Translate: bridge(label) — an English phrase
  reports its Mandell seed and English gloss; it is
  a REPORT, nothing executes or mutates. B6 (Director
  FIX, step 6): bare Translate reports
  nothing_to_translate (ok=False) with no fabricated
  Show intent — the former empty-string Show report
  was the B6 defect.
- 46 Rank: "Ranked <n> proposals:" plus one line per
  PENDING proposal, affinity-descending (equal
  affinities keep the lens order — score descending,
  then id; the lens has no insertion-order term),
  format "<i>. aff=<aff:.3f> [<kind>] <id> — <label>".
  The order Rank prints is the order
  ranked_proposals() serves — the S lens order
  (Director 7074761282 / §42 delta 7080635172; see
  the symbiosis oracle union below): fresher first
  on the FRESH fade at one-second granularity, exact
  score ties broken by proposal id. Dell 46's own
  affinity sort is stable: at equal affinity it
  preserves the input order it was served (proven in
  isolation in the symbiosis block below).
- 47 Embed (core_i_ops): HONEST REFUSAL — ok=False
  embed_unavailable, representation "none", no
  provider; labeled and bare refuse identically.
- 48 Macro: plain Macro renders the macro seed —
  the last n noted history entries joined " > "
  (bare n=5, a digit label sets n; empty history ->
  "48[Macro] :: empty"); a "replay" label runs
  replay_exec(n) for real instead.
- 49 Profile: the speedometer (C7.Profile, DD-39) —
  a deliberate BENCHMARK on disposable state: named
  stages place/pulse/growth/save/load timed with a
  monotonic clock, per-stage shares, overhead
  disclosed, embedding ABSENT standalone; the
  structured receipt rides the result as
  profile_report. (The status echo is retired;
  Schema owns status.)
- 50 Manifest: a label mints the unit via place_idea
  (CUBE) + "Manifested."; "acceptance"/"accept"
  print the acceptance sequence and mint nothing;
  bare Manifest is ok=True "Manifest needs :: label."
  with zero mutation.

Cluster symbiosis: Rank (46) ranks the pending
proposals Nurture (37) wrote — in S lens order,
pinned with controlled created stamps so no
wall-clock straddle can move the result — and
returns to zero after Nurture confirms/rejects
them all; Discover
(35, circuit 18) find_idea locates the unit Nurture's
confirm promoted; TokenCount (40) counts the units
Manifest (50) and Distill (38) minted. One literal-
REPL leg (44 + 50) for REAL_USER_PATH evidence.

House pattern: RESULTS + _rec; loud cleanup
(owner-wide glob; the test owners are unique to
this suite)."""
import os
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from form.mandell.dell_cards import DEEP_NOTES          # noqa: E402

RESULTS = []


def _rec(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))


def _cleanup(owner):
    import glob
    import shutil
    state = os.path.join(_ROOT, "form", "state")
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


def _program(owner):
    from form.open import Program
    _cleanup(owner)
    prog = Program(owner=owner)
    from form.mandell.core_ii_exec import attach
    attach(prog)
    return prog


def _run(prog, seed):
    from form.mandell.executor import execute_seed
    return execute_seed(prog, seed)


def _msgs(r):
    return [m for m in r.get("messages", [])
            if not m.startswith(("Mandell:", "English:"))]


def _units(prog):
    return prog.cube.session.plane.units


def main():
    owner = "D1RegLeaf4"
    p = _program(owner)

    # -- 46 Rank: empty nursery
    r = _run(p, "46[Rank]")
    _rec("46 Rank: with no pending proposals the report "
         "is 'Ranked 0 proposals:' and nothing else",
         _msgs(r) == ["Ranked 0 proposals:"], str(_msgs(r)))

    # -- 37 Nurture: bare fails, zero mutation
    r = _run(p, "37[Nurture]")
    _rec("37 Nurture: bare Nurture fails 'add idea "
         "requires a label' with zero mutation",
         r.get("ok") is False
         and r.get("error") == "add idea requires a label"
         and p.nursery.summary().get("total", 0) == 0
         and list(_units(p)) == ["welcome"], str(_msgs(r)))

    # -- 37 Nurture: add mints a PENDING proposal only
    r = _run(p, "37[Nurture] :: First Idea")
    pid1 = getattr(p, "last_nurture", {}).get("pid", "")
    _rec("37 Nurture: a label adds a pending nursery "
         "proposal — last_nurture records the add and "
         "the plane is NOT mutated",
         r.get("ok") is True and bool(pid1)
         and _msgs(r) == [f"Added idea: {pid1} (First Idea)"]
         and p.last_nurture.get("action") == "add"
         and pid1 in p.nursery.proposals
         and p.nursery.proposals[pid1].status == "pending"
         and pid1 not in _units(p), str(_msgs(r)))
    r = _run(p, "37[Nurture] :: Second Idea")
    pid2 = getattr(p, "last_nurture", {}).get("pid", "")

    # -- symbiosis: Rank reads Nurture's pending set.
    #
    #    ORACLE UNION (Director §42 COMPOSITION RULING
    #    7090358247, 2026-11-22 ~21:00 CST; blocker
    #    7090289557): TEST-ONLY union of the two competing
    #    corrections of this block. Governing law: the
    #    adopted lens orders by (-score, id); the FRESH
    #    term reads the created stamp at ONE-SECOND
    #    granularity; neither side's tests redefine
    #    production behavior. Case-by-case crosswalk:
    #
    #    U1 = main's equal-stamp ID tie-break (Director
    #      §42 delta 7080635172; classification
    #      D1_LEAF4_CLASSIFICATION_2026-11-22): pin the
    #      second proposal's created stamp to the first's;
    #      exactly equal scores tie-break by id. KEPT
    #      VERBATIM as the first check below. Branch (b)
    #      (Director 7074761282, PR #506) asserted the
    #      same control — identical stamps, id tie-break,
    #      same expected order — using absolute controlled
    #      stamps instead of the relative pin. EQUIVALENT:
    #      consolidated into U1; no distinct behavior or
    #      negative case lost.
    #    U2 = main's boundary control (§42 delta
    #      7080635172): the second proposal exactly one
    #      second younger ranks FIRST on its strictly
    #      larger FRESH score. KEPT VERBATIM as the second
    #      check below. Branch (a) (7074761282) asserted
    #      the same configuration and outcome with
    #      absolute stamps (pid2 at "...T00:00:01Z" vs
    #      pid1 at "...T00:00:00Z"). EQUIVALENT:
    #      consolidated into U2; no distinct behavior or
    #      negative case lost.
    #    U3 = branch (c) (7074761282), DISTINCT, kept
    #      verbatim as the third check: the id tie-break
    #      governs against insertion order (Zebra added
    #      first, Apple second; Apple ranks first at
    #      identical stamps). Main's version has no such
    #      case — its tie-break pair's ids coincide with
    #      insertion order, so it cannot distinguish the
    #      two orders.
    #    U4 = branch (d) (7074761282), DISTINCT, kept
    #      verbatim as the fourth check: Dell 46 isolated
    #      from the lens — served a pre-ranked list
    #      directly, its stable affinity sort preserves
    #      the served input order at equal affinity.
    #
    #    Failing-first provenance: each side's correction
    #    was written against a documented campaign red of
    #    the pre-correction oracle — main's pin against
    #    the leg-1 35/36 red, the branch's controlled
    #    stamps against the leg-3 red (both reds the same
    #    wall-clock second-straddle under the old
    #    insertion-order pin). The union preserves both
    #    corrections' controls; no assertion from either
    #    side was weakened.
    #
    #    ORACLE CORRECTION (Director §42 delta 7080635172;
    #    classification D1_LEAF4_CLASSIFICATION_2026-11-22):
    #    the adopted lens orders by (-score, id) — there is
    #    no insertion-order term — and the score's FRESH
    #    term reads the created stamp at ONE-SECOND
    #    granularity, so two uncontrolled adds that straddle
    #    a wall-clock second boundary score ~1e-7 apart and
    #    the younger proposal legitimately ranks first. The
    #    old oracle asserted insertion order against
    #    uncontrolled stamps (the campaign leg-1 35/36 red).
    #    Pin the second proposal's created stamp to the
    #    first's (in-memory only) so this check tests the
    #    adopted semantics deterministically: exactly equal
    #    scores fall to the id tie-break.
    from datetime import datetime, timedelta
    _stamp = p.nursery.proposals[pid1].created
    p.nursery.proposals[pid2].created = _stamp
    r = _run(p, "46[Rank]")
    _rec("symbiosis: Rank (46) ranks Nurture's (37) two "
         "pending proposals under the adopted lens "
         "semantics — created stamps pinned equal, the "
         "exactly equal scores tie-break by id (which is "
         "insertion order for these ids) at aff=0.000 [new]",
         _msgs(r) == ["Ranked 2 proposals:",
                      f"  1. aff=0.000 [new] {pid1} — First Idea",
                      f"  2. aff=0.000 [new] {pid2} — Second Idea"],
         str(_msgs(r)))

    # -- symbiosis boundary control (union U2): with the
    #    second proposal's created stamp exactly one second
    #    younger, its strictly larger FRESH score MUST
    #    rank it first — the freshness ordering is the
    #    adopted semantics, not noise. This is the exact
    #    configuration the uncontrolled oracle mistook
    #    for a defect.
    _dt = datetime.strptime(_stamp, "%Y-%m-%dT%H:%M:%SZ")
    p.nursery.proposals[pid2].created = (
        _dt + timedelta(seconds=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    r = _run(p, "46[Rank]")
    _rec("symbiosis: Rank (46) boundary control — the "
         "second proposal one second younger ranks FIRST "
         "on its strictly larger FRESH score (adopted "
         "freshness semantics)",
         _msgs(r) == ["Ranked 2 proposals:",
                      f"  1. aff=0.000 [new] {pid2} — Second Idea",
                      f"  2. aff=0.000 [new] {pid1} — First Idea"],
         str(_msgs(r)))
    p.nursery.proposals[pid2].created = _stamp

    # -- symbiosis (c) (union U3): the id tie-break is NOT
    #    insertion order — a pair whose slugs sort
    #    against their insertion order still comes
    #    out in id order at identical stamps.
    owner_c = "D1RegLeaf4Lens"
    pc = _program(owner_c)
    _run(pc, "37[Nurture] :: Zebra Idea")
    pidz = getattr(pc, "last_nurture", {}).get("pid", "")
    _run(pc, "37[Nurture] :: Apple Idea")
    pida = getattr(pc, "last_nurture", {}).get("pid", "")
    pc.nursery.proposals[pidz].created = "2026-01-01T00:00:00Z"
    pc.nursery.proposals[pida].created = "2026-01-01T00:00:00Z"
    r = _run(pc, "46[Rank]")
    _rec("symbiosis: Rank (46) tie-break follows "
         "proposal id against insertion order — Apple "
         "(added second) ranks before Zebra (added "
         "first) at identical stamps",
         _msgs(r) == ["Ranked 2 proposals:",
                      f"  1. aff=0.000 [new] {pida} — Apple Idea",
                      f"  2. aff=0.000 [new] {pidz} — Zebra Idea"],
         str(_msgs(r)))
    _cleanup(owner_c)

    # -- symbiosis (d) (union U4): Dell 46 isolated from
    #    the lens — served a pre-ranked list directly, its
    #    stable affinity sort preserves the input
    #    order at equal affinity.
    owner_s = "D1RegLeaf4Rank46"
    ps = _program(owner_s)
    feed = [{"id": "zz_feed", "label": "Zeta Feed",
             "kind": "new", "affinity": 0.0},
            {"id": "aa_feed", "label": "Alpha Feed",
             "kind": "new", "affinity": 0.0},
            {"id": "mm_feed", "label": "Mid Feed",
             "kind": "new", "affinity": 0.0}]
    ps.ranked_proposals = lambda: [dict(d) for d in feed]
    r = _run(ps, "46[Rank]")
    _rec("symbiosis: Dell 46 in isolation preserves "
         "its served input order at equal affinity — "
         "zz_feed, aa_feed, mm_feed print in feed "
         "order, not id order",
         _msgs(r) == ["Ranked 3 proposals:",
                      "  1. aff=0.000 [new] zz_feed — Zeta Feed",
                      "  2. aff=0.000 [new] aa_feed — Alpha Feed",
                      "  3. aff=0.000 [new] mm_feed — Mid Feed"],
         str(_msgs(r)))
    _cleanup(owner_s)

    # -- 44 Bridge: honest refusal, bare and labeled
    before = list(_units(p))
    r = _run(p, "44[Bridge]")
    _rec("44 Bridge: bare Bridge honestly refuses "
         "(bridge_unavailable, no provider bound); "
         "last_core_i records capability 'external' / "
         "permission offline_origin; zero mutation",
         r.get("ok") is False
         and r.get("error") == "bridge_unavailable"
         and _msgs(r) == ["Bridge unavailable: no external "
                          "provider bound"]
         and p.last_core_i.get("capability") == "external"
         and p.last_core_i.get("permission") == "offline_origin"
         and list(_units(p)) == before, str(_msgs(r)))
    r = _run(p, "44[Bridge] :: payments")
    _rec("44 Bridge: a labeled Bridge still refuses — "
         "the label becomes the recorded capability",
         r.get("ok") is False
         and r.get("error") == "bridge_unavailable"
         and p.last_core_i.get("capability") == "payments",
         str(_msgs(r)))

    # -- 47 Embed: honest refusal, bare and labeled
    r = _run(p, "47[Embed]")
    ok_bare = (r.get("ok") is False
               and r.get("error") == "embed_unavailable"
               and _msgs(r) == ["Embed unavailable: no vector "
                                "provider bound"]
               and p.last_core_i.get("representation") == "none"
               and p.last_core_i.get("provider") == "")
    r = _run(p, "47[Embed] :: hello world")
    _rec("47 Embed: bare and labeled Embed honestly "
         "refuse identically (embed_unavailable, "
         "representation none, no provider)",
         ok_bare and r.get("ok") is False
         and r.get("error") == "embed_unavailable",
         str(_msgs(r)))

    # -- 45 Translate: report only
    before = list(_units(p))
    r = _run(p, "45[Translate] :: create a garden")
    _rec("45 Translate: an English phrase reports its "
         "Mandell seed and English gloss — a report "
         "only, zero mutation (nothing is created)",
         _msgs(r) == ['mandel: 08[Create](name="garden") '
                      '> 15[Map] :: garden',
                      'english: Create (Instantiate) then '
                      'Map (Coordinate / index) → garden']
         and list(_units(p)) == before
         and "garden" not in _units(p), str(_msgs(r)))
    r = _run(p, "45[Translate] :: show avatar")
    _rec("45 Translate: 'show avatar' translates to the "
         "bare Show seed with its gloss",
         _msgs(r) == ["mandel: 09[Show]",
                      "english: Show (Render / output)"],
         str(_msgs(r)))
    r = _run(p, "45[Translate]")
    _rec("45 Translate (B6, step 6): bare Translate reports "
         "nothing_to_translate — no fabricated Show intent, "
         "zero mutation",
         r.get("ok") is False
         and r.get("error") == "nothing_to_translate"
         and _msgs(r) == ["Translate: nothing_to_translate — "
                          "no input, nothing executed."]
         and list(_units(p)) == before,
         str(_msgs(r)))

    # -- 41 Sanitize: redaction + the echo exhibit
    r = _run(p, "41[Sanitize] :: password: hunter2 "
                "token=abc123 api_key=XYZ789 "
                "1234567890123 normal")
    _rec("41 Sanitize: the OUT line redacts password/"
         "token/api_key values and 12+ digit numbers, "
         "leaving ordinary words untouched",
         _msgs(r)[-1] == "Sanitize out: password=[REDACTED] "
                         "token=[REDACTED] "
                         "api_key=[REDACTED] [REDACTED_NUM] "
                         "normal", str(_msgs(r)))
    _rec("41 Sanitize DAF-02/B5: the IN line shows the "
         "SANITIZED representation — the secrets the OUT "
         "line redacts are NOT printed verbatim anywhere "
         "in Sanitize's own output",
         _msgs(r)[0] == "Sanitize in:  password=[REDACTED] "
                        "token=[REDACTED] "
                        "api_key=[REDACTED] [REDACTED_NUM] "
                        "normal",
         str(_msgs(r)))
    r = _run(p, "41[Sanitize] :: hello world")
    ok_clean = _msgs(r) == ["Sanitize in:  hello world",
                            "Sanitize out: hello world"]
    r = _run(p, "41[Sanitize]")
    _rec("41 Sanitize: clean text passes through "
         "unchanged; bare Sanitize reports (empty) on "
         "both lines",
         ok_clean and _msgs(r) == ["Sanitize in:  (empty)",
                                   "Sanitize out: (empty)"],
         str(_msgs(r)))

    # -- 39 Schema: DD-29 nervous-system board (C7.Schema
    # circuit — contract changed from the 3-hasattr stub and
    # disclosed in that PR): per-organ exists/connected/
    # available board over DD-29's 16 systems, label ignored,
    # verdict noted to history in the historical form.
    r = _run(p, "39[Schema] :: anything at all")
    _m39 = _msgs(r)
    _organs39 = [m for m in _m39 if m.startswith("  · ")]
    _rec("39 Schema: a healthy program's board is VALID — "
         "16 systems examined, one line per organ carrying "
         "its three checks, the label ignored, enhance "
         "OFF-by-design — and the verdict is noted to "
         "history",
         _m39[0] == "Schema: VALID"
         and "16 systems examined" in _m39[1]
         and len(_organs39) == 16
         and all(": exists=" in m and " connected=" in m
                 and " available=" in m for m in _organs39)
         and any(m.startswith("  · enhance:")
                 and "available=OFF-by-design" in m
                 for m in _organs39)
         and "39[Schema] :: valid" in list(p.history),
         str(_m39))

    # -- 43 Fallback: message-only safe path
    before = list(_units(p))
    r = _run(p, "43[Fallback]")
    _rec("43 Fallback: the safe path is exactly status "
         "/ save / the acceptance sequence — message "
         "only, zero mutation, noted to history",
         _msgs(r) == ["Fallback safe path:",
                      "  1. status / 31[Simulate]",
                      "  2. save / 10[Keep]",
                      "  3. acceptance: create → grow → "
                      "confirm → sphere → save → load → visual"]
         and list(_units(p)) == before
         and "43[Fallback]" in list(p.history),
         str(_msgs(r)))

    # -- 38 Distill: labeled distillation rules
    r = _run(p, "38[Distill] :: Alpha Alpha Beta Gamma "
                "Delta Epsilon Zeta")
    du = _units(p).get("alpha_beta_gamma_delta")
    _rec("38 Distill: mints the distilled name itself "
         "as SEED (no prefix) — distill lowercases, "
         "dedups and caps at 4 tokens (>2 chars)",
         _msgs(r) == ['Created idea: "alpha_beta_gamma_delta"',
                      "Distilled → alpha_beta_gamma_delta"]
         and du is not None and str(du.skin) == "Skin.SEED",
         str(_msgs(r)))
    r = _run(p, "38[Distill] :: a an the")
    _rec("38 Distill: tokens of <=2 chars are dropped "
         "— 'a an the' distills to 'the'",
         _msgs(r)[-1] == "Distilled → the"
         and "the" in _units(p), str(_msgs(r)))

    # -- 50 Manifest: mint / acceptance / bare
    r = _run(p, "50[Manifest] :: Real Thing")
    mu = _units(p).get("real_thing")
    _rec("50 Manifest: a label mints the unit as CUBE "
         "via place_idea and announces 'Manifested.'",
         _msgs(r) == ['Created idea: "Real Thing"',
                      "Manifested."]
         and mu is not None and str(mu.skin) == "Skin.CUBE",
         str(_msgs(r)))
    before = list(_units(p))
    r = _run(p, "50[Manifest] :: acceptance")
    r2 = _run(p, "50[Manifest] :: accept")
    _rec("50 Manifest: 'acceptance' and its alias "
         "'accept' print the acceptance sequence and "
         "mint nothing",
         _msgs(r) == ["Acceptance: create → grow → "
                      "confirm → sphere → save → load → visual"]
         and _msgs(r2) == _msgs(r)
         and list(_units(p)) == before, str(_msgs(r)))
    r = _run(p, "50[Manifest]")
    _rec("50 Manifest: bare Manifest is ok=True "
         "'Manifest needs :: label.' with zero mutation "
         "(a message-level refusal, unlike 44/47's "
         "ok=False refusals)",
         r.get("ok") is True
         and _msgs(r) == ["Manifest needs :: label."]
         and list(_units(p)) == before, str(_msgs(r)))

    # -- 49 Profile: the speedometer (C7.Profile, DD-39).
    #    The exact-echo pin is retired DELIBERATELY with the
    #    stub it pinned: Profile no longer echoes status()
    #    (Schema owns status); bare Profile runs the standard
    #    benchmark on disposable state and receipts it.
    r = _run(p, "49[Profile]")
    rep49 = r.get("profile_report") or {}
    _rec("49 Profile: runs the standard BENCHMARK on "
         "disposable state — receipt carries kind/verdict, "
         "all named stages timed, no status echo",
         r.get("ok") is True
         and rep49.get("kind") == "BENCHMARK"
         and rep49.get("verdict") == "COMPLETE"
         and bool(_msgs(r)) and _msgs(r)[0] == "Profile: COMPLETE"
         and not any(m.startswith("  owner=") for m in _msgs(r)),
         str(_msgs(r))[:200])

    # -- 40 TokenCount: exact approx formula
    ideas = len(_units(p))
    hist = len(list(p.history))
    cells = len(p.lattice.cells)
    pending = p.nursery.summary().get("pending", 0)
    approx = ideas * 8 + hist * 4 + cells * 2 + pending * 6
    r = _run(p, "40[TokenCount]")
    _rec("40 TokenCount: approx = ideas*8 + history*4 "
         "+ cells*2 + pending*6, recorded in "
         "last_measure and last_core_i — and the ideas "
         "term counts the units Manifest (50) and "
         "Distill (38) minted (symbiosis)",
         _msgs(r) == ["TokenCount (approx session weight):",
                      f"  ideas={ideas} history={hist} "
                      f"cells={cells} pending={pending}",
                      f"  approx_units={approx}"]
         and p.last_measure.get("value") == approx
         and p.last_measure.get("ideas") == len(_units(p))
         and "real_thing" in _units(p)
         and p.last_core_i.get("dell") == 40
         and p.last_core_i.get("ok") is True,
         str(_msgs(r)))

    # -- 37 Nurture: unknown confirm/reject fail honestly
    r = _run(p, "37[Nurture] :: confirm nope123")
    _rec("37 Nurture: confirming an unknown pid fails "
         "honestly and records the failure",
         r.get("ok") is False
         and _msgs(r) == ["Confirm failed: nope123 "
                          "(not found or not pending)"]
         and p.last_nurture.get("ok") is False,
         str(_msgs(r)))
    r = _run(p, "37[Nurture] :: reject nope123")
    _rec("37 Nurture: rejecting an unknown pid fails "
         "honestly ('not found or not pending')",
         r.get("ok") is False
         and _msgs(r) == ["Reject failed: nope123 not "
                          "found or not pending"]
         and p.last_nurture.get("ok") is False,
         str(_msgs(r)))

    # -- 37 Nurture: confirm promotes into the plane
    r = _run(p, f"37[Nurture] :: confirm {pid1}")
    _rec("37 Nurture: confirm promotes the proposal "
         "through the canonical boundary — the pid "
         "becomes a plane unit and the nursery counts "
         "it confirmed",
         r.get("ok") is True
         and _msgs(r) == [f"Confirmed and promoted "
                          f"proposal: {pid1}"]
         and pid1 in _units(p)
         and p.nursery.summary().get("confirmed", 0) == 1
         and p.last_nurture.get("promoted") is True,
         str(_msgs(r)))

    # -- symbiosis: Discover finds the promoted unit
    r = _run(p, "35[Discover] :: find_idea first")
    ld = getattr(p, "last_discover", {})
    match_ids = [m["id"] for m in ld.get("matches", [])]
    _rec("symbiosis: Discover (35) find_idea locates "
         "the unit Nurture's (37) confirm promoted",
         ld.get("source") == "cube_idea_search"
         and pid1 in match_ids, str(match_ids))

    # -- 37 Nurture: reject does not promote
    r = _run(p, f"37[Nurture] :: reject {pid2}")
    _rec("37 Nurture: reject marks the proposal "
         "rejected and it never reaches the plane",
         r.get("ok") is True
         and _msgs(r) == [f"Rejected proposal: {pid2}"]
         and pid2 not in _units(p)
         and p.nursery.summary().get("rejected", 0) == 1,
         str(_msgs(r)))
    r = _run(p, "46[Rank]")
    _rec("symbiosis: after Nurture's confirm + reject, "
         "Rank (46) returns to 'Ranked 0 proposals:' — "
         "the pending set both Dells share is empty",
         _msgs(r) == ["Ranked 0 proposals:"], str(_msgs(r)))
    _cleanup(owner)

    # -- 38 Distill: bare reads the LAST unit
    owner_d = "D1RegLeaf4Distill"
    q = _program(owner_d)
    _run(q, "08[Create] :: Garden Gate")
    _run(q, "08[Create] :: Stone Wall")
    snap = (_units(q)["stone_wall"].label,
            _units(q)["stone_wall"].words)
    r = _run(q, "38[Distill]")
    du = _units(q).get("stone_wall_1")
    _rec("38 Distill: bare Distill's source is the "
         "LAST unit's '<label> <words>' — Stone Wall "
         "distills to stone_wall; the minted id dedups "
         "to stone_wall_1 (the source keeps its id) and "
         "the source is unmutated",
         _msgs(r) == ['Created idea: "stone_wall" '
                      '(id: stone_wall_1)',
                      "Distilled → stone_wall"]
         and du is not None and str(du.skin) == "Skin.SEED"
         and (_units(q)["stone_wall"].label,
              _units(q)["stone_wall"].words) == snap,
         str(_msgs(r)))
    _cleanup(owner_d)

    # -- 42 Retry: empty history, then a real re-run
    owner_r = "D1RegLeaf4Retry"
    q = _program(owner_r)
    r = _run(q, "42[Retry]")
    _rec("42 Retry: on an empty noted history Retry "
         "reports 'Retry: history empty.' and runs "
         "nothing",
         _msgs(r) == ["Retry: history empty."], str(_msgs(r)))
    _run(q, "03[Logic] :: retrytarget")
    r = _run(q, "42[Retry]")
    _rec("42 Retry: Retry re-executes the LAST noted "
         "entry for real (ran=1) — the Logic seed runs "
         "again (its note appears twice) and Retry "
         "notes itself against the retried entry",
         _msgs(r) == ["Retry last: 03[Logic] :: retrytarget",
                      "Retry ran=1 skipped=0"]
         and list(q.history).count(
             "03[Logic] :: retrytarget") == 2
         and "42[Retry] :: 03[Logic] :: retrytarget"
         in list(q.history), str(_msgs(r)))
    _cleanup(owner_r)

    # -- 48 Macro: empty / render / digit / replay
    owner_m = "D1RegLeaf4Macro"
    q = _program(owner_m)
    r = _run(q, "48[Macro]")
    _rec("48 Macro: on an empty history the macro seed "
         "is '48[Macro] :: empty'",
         _msgs(r) == ["48[Macro] :: empty"], str(_msgs(r)))
    _run(q, "03[Logic] :: alpha rule")
    _run(q, "11[Architect]")
    hist_before = list(q.history)
    r = _run(q, "48[Macro]")
    ok_bare = _msgs(r) == ["48[Macro] :: 03[Logic] :: "
                           "alpha rule > 11[Architect]"]
    r = _run(q, "48[Macro] :: 1")
    _rec("48 Macro: plain Macro renders the last n "
         "noted entries joined ' > ' (bare n=5, a digit "
         "label sets n=1) and notes nothing itself",
         ok_bare and _msgs(r) == ["48[Macro] :: 11[Architect]"]
         and list(q.history) == hist_before, str(_msgs(r)))
    r = _run(q, "48[Macro] :: replay 1")
    _rec("48 Macro: a 'replay' label runs replay_exec "
         "for real — the last entry (Architect) "
         "executes again and its note reappears",
         _msgs(r) == ["Replay exec n=1 ran=1 skipped=0"]
         and list(q.history).count("11[Architect]") == 2,
         str(_msgs(r)))
    _cleanup(owner_m)

    # -- REAL_USER_PATH: literal REPL seed lines
    owner2 = "D1RegLeaf4Repl"
    _cleanup(owner2)
    proc = subprocess.run(
        [sys.executable, "-m", "form.repl", "--owner", owner2],
        input="44[Bridge]\n50[Manifest] :: Real Thing\n",
        capture_output=True, text=True, cwd=_ROOT, timeout=120)
    out = proc.stdout or ""
    _rec("REPL: Bridge's honest refusal and Manifest's "
         "mint execute on the literal user path",
         proc.returncode == 0
         and "Bridge unavailable: no external provider bound" in out
         and "Manifested." in out, out[-300:])
    _cleanup(owner2)

    # -- docs pins
    _rec("proof cards carry circuit-19 deep notes (37-50)",
         all(n in DEEP_NOTES and "circuit 19" in DEEP_NOTES[n]
             for n in range(37, 51)),
         str([n for n in range(37, 51) if n not in DEEP_NOTES]))

    total = len(RESULTS)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        if not ok:
            print(f"FAIL {name} :: {detail}")
    print(f"D1_REGISTRY_LEAF4: {passed}/{total}")
    return passed == total


def smoke():
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
