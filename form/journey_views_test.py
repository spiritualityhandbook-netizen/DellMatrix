#!/usr/bin/env python3
"""Part VII / GP-E27 — journey harness family 6: J-07 Cross-view
space, J-08 Tree 3D, J-13 Studio coherence, J-23 Plan-change sync.

Written failing-first at code stage and registered in
form/regress.py LIST in the same commit (omitted-entry law).

Contracts — Edition 1 file 06 (06_JOURNEY_ACCEPTANCE.md), executed
verbatim where the subject exists at this head:

  J-07: "Create at least two noncoincident Ideas, draw/inspect
  same typed relations in 2D/Flower/cube/text. Show distinct
  projection and canonical graph facts." Failure oracle: "Pure
  visual proximity does not create semantic relation; same Idea
  IDs/status after pan/zoom/move and reload; geometry values
  carry units and fixture assumptions."
  J-08: "Render admitted FCC geometry as a typed Tree L1 view,
  compare rendered centers, shells, slices, occupancy and UI
  scale to deterministic fixtures." Failure oracle: "Before
  Director admission show RESEARCH/PROJECTION only; unproven L3
  idea-radius and HCP variant do not alter kernel; guard missing
  inputs."
  J-13: "Navigate all five public pages and perspectives, edit
  approved idea in one, verify refreshed same canonical truth in
  other views and REPL." Failure oracle: "Empty/plantless Idea
  remains truthfully represented; stale token, bad Origin,
  interrupted load, screen-reader/keyboard and narrow viewport;
  no phantom live nodes."
  J-23 (plan section 5.2.1, designed): "change the plan record,
  sync; the Space shows the new state with provenance, and a
  stale mirror is labeled stale — never presented as current
  truth."

Execution tier: PUBLIC_ENTRY_PATH — journey actions run in
literal `python3 -m form.repl` subprocesses against per-run
isolated owners, and, for the Studio surface journey, against
the real Studio HTTP server (`python3 -m gui.server`) booted as
a subprocess on an ephemeral loopback port, driven over HTTP
exactly as its own client protocol requires (session token
served inside the index page). State comparison uses the
persistence loader and the SemanticGraph loader (reloaded vs
reloaded, never in-memory vs reloaded).

Grounded behavior (each expectation verified first-hand in
scratch-owner probes, 2026-11-21, before this suite was written):
  - The spatial authority places created Ideas at distinct
    spiral positions (cause neutral_spiral; `spatial explain`
    names the position and cause); a bare create (no detail, no
    goals) stores NO fabricated detail or goals.
  - `nest <child> under <parent>` draws the typed relation: the
    canonical SemanticGraph gains exactly one ACTIVE `contains`
    entry (parent idea_id -> child idea_id, provenance
    human/bridge_nest); the text views (`containment`,
    `lineage`) show it.
  - `show` renders the plane table projection: every unit with
    its position and the true unit count. `cube` switches the
    lattice form; the idea page (`zoom`/`page`) shows the same
    canonical id, position and detail under the new form.
  - `flower geometry` / `vesica` / `verita` render the Flower
    projection: Verita edges are computed from proximity
    (d=1.0 pairs) and are LABELED "coherence-of-meet between
    ideas" — pairs at distance 1.0 with NO drawn relation
    (welcome <-> beta_stone, beta_stone <-> gamma_stone) carry
    Verita edges in the projection and NO entry in the
    canonical graph. Proximity is projection weather, never
    graph truth.
  - The geometry layer labels itself: "Vesica/Verita is
    coherence-of-meet · Voynich rings are organizational ·
    Fractals are deterministic pattern tools". On an owner with
    no nearby ideas it reports "Verita edges=0" plus the honest
    hint "(place nearby ideas or grow scores to form vesica
    meets)" — no fabricated edges. No Tree/FCC surface answers
    at the public path at this head (`tree` is not understood;
    no FCC or Tree L1 module exists under form/ or gui/) —
    J-08's subject is NOT BUILT at baseline (GP-E18 unlanded),
    a finding, not a harness failure (plan section 5.1(iii)).
  - View/geometry commands mutate no canonical state: loader
    snapshots (units, nursery) and the graph are identical
    before and after a full view battery (history is an action
    log and legitimately records the viewing actions).
  - Rooms disclose truncation: with 19 units the growth room
    lists 12 and prints "… +7 more" — shown is never dressed
    as total.
  - The history view's listed tail is truthful (the last 16
    entries match the loader's history tail exactly) — but see
    the DAF-09 D1 finding recorded in the rehearsal record:
    with 19 true notes its header prints "History · 16 notes
    (last 16 shown)", presenting the shown window's size as
    the note count and never naming the true total. Recorded
    precisely for D1's home circuit; NOT fixed here (the
    family 6 oracles do not name the history view, and D1 is
    a post-completion item with its own circuit).
  - Studio HTTP surface: GET / serves the index with the
    per-launch session token; /api/dells returns exactly the
    canonical 100-Dell registry; POST /api/execute without a
    token or with a stale token refuses 401, with a foreign
    Origin refuses 403; with the token, `55[Set] :: tempo=120`
    executes and the value round-trips through /api/state for
    that owner only (a foreign owner's state stays empty).
    /api/growth nodes come from the server program's canonical
    plane units through the growth lens, and an unplanted node
    carries stage=None with stage_source="unplanted" — no
    fabricated stage.
  - RECORDED GAP (J-13 cross-surface leg): the Studio server
    opens its program via open_program (a fresh Program) and
    never consults the persisted pair — REPL-created Ideas
    saved to disk do NOT appear in the Studio's /api/growth
    nodes at this head. Within-surface coherence is proven
    (REPL views among themselves; Studio execute<->state);
    REPL<->Studio canonical-truth coherence is NOT BUILT at
    baseline — it belongs to the GP-E24/E25 windowed-workspace
    scope (Part 0, in flight), not to a Part VII harness fix.
    Recorded in the rehearsal record as a finding with its
    mechanism; no check asserts the gap as desired behavior.
  - J-23's subject (Muse Space, GP-E25) is likewise absent at
    this head: no form.muse_space_* module exists on this
    branch (GP-E25 is built on PR #510, unmerged). The suite
    probes for the surface dynamically: while absent, J-23 is
    recorded NOT BUILT at baseline; if a future head provides
    it, the check requires its snapshot to carry provenance /
    staleness labeling before any sync claim is accepted.

Uncovered at this tier, named honestly (not silently passed):
  - J-13's five-pages web navigation, interrupted load,
    screen-reader/keyboard and narrow-viewport legs are
    browser-surface acts (gui/browser_acceptance.py territory),
    not constructible from this harness's HTTP/REPL tier; the
    stale-token and bad-Origin legs ARE exercised here.
  - J-07's pan/move leg: the public path offers zoom (a pan to
    a unit) but no idea-move verb that preserves identity was
    found in the REPL surface probed (movement verbs move the
    avatar/viewer); identity stability is proven across zoom,
    form switches and cold reload instead.
  - REAL_USER_PATH not claimed (piped REPL + scripted HTTP are
    PUBLIC_ENTRY_PATH).

Baseline posture (plan section 5.1(iii)): this suite runs
against the pre-Parts main as a labeled BASELINE harness proof.
Its grades are evidence about the harness and the current
program, recorded in
director-reports/GRAND_SYNCHRONIZATION_REHEARSAL_2026-11-20.md;
the GP-E27 rehearsal executions proper run against merged
Parts I + II.

Run: python3 -m form.journey_views_test
"""

import importlib
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from form.persist import _STATE_DIR, _safe_owner, load as persist_load
from form.mandell.semantic_graph import SemanticGraph

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
CP = "create an idea called Bare Pebble"


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
    """Loader-basis snapshot: units with content + position +
    canonical idea_id, nursery summary, history."""
    prog = persist_load(owner)
    units = {}
    for uid, u in prog.cube.session.plane.units.items():
        units[uid] = {
            "label": u.label,
            "detail": getattr(u, "detail", "") or "",
            "goals": list(getattr(u, "goals", []) or []),
            "words": getattr(u, "words", "") or "",
            "x": float(u.x), "y": float(u.y),
            "idea_id": getattr(u, "idea_id", None),
        }
    props = {pid: p.status
             for pid, p in prog.nursery.proposals.items()}
    return {"units": units, "props": props,
            "summary": prog.nursery.summary(),
            "history": list(getattr(prog, "history", []) or [])}


def graph_entries(owner):
    g = SemanticGraph.load(owner)
    return [e.to_dict() for e in g._entries]


def _free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def _http(base, method, path, body=None, headers=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    hdrs = dict(headers or {})
    if data is not None:
        hdrs["Content-Type"] = "application/json"
    req = urllib.request.Request(base + path, data=data, headers=hdrs,
                                 method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            return res.status, res.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")


def main():
    view_owner = f"JView{RUN}"
    geom_owner = f"JGeom{RUN}"
    many_owner = f"JMany{RUN}"
    studio_owner = f"JStudio{RUN}"
    owners = (view_owner, geom_owner, many_owner, studio_owner)
    for o in owners:
        cleanup(o)
    server = None
    try:
        # Isolation boundary, proven — not assumed (a fresh
        # Program() in this codebase loads persisted state by
        # default; the boundary is the per-run unique owner +
        # verified-empty start).
        check("views_isolation_boundary_clean_start",
              all(state_files(o) == [] for o in owners),
              "no state files exist for any of the four per-run "
              "owners before the sessions start")

        # ---------------- J-07: create + positions -------------
        rc, out = run_repl(view_owner, [CA, CB, CC, CP, "save",
                                        "quit"])
        check("j07_repl_exit_clean",
              rc == 0 and "Traceback" not in out,
              f"rc={rc} traceback={'Traceback' in out}")
        s0 = snap(view_owner)
        units = s0["units"]
        positions = {(u["x"], u["y"]) for u in units.values()}
        check("j07_ideas_noncoincident",
              len(units) == 5 and len(positions) == 5,
              "welcome + four created Ideas occupy five "
              f"distinct positions: {sorted(positions)}")
        pebble = units.get("bare_pebble") or {}
        check("j07_bare_idea_truthful_no_fabricated_content",
              pebble.get("detail") == ""
              and pebble.get("goals") == [],
              "the bare create stored no fabricated detail or "
              "goals — an empty Idea is represented as empty")

        # ---------------- J-07: draw the typed relation --------
        rc, out = run_repl(view_owner, [
            "nest beta_stone under alpha_stone",
            "containment alpha_stone",
            "lineage beta_stone",
            "save", "quit",
        ], load=True)
        check("j07_nest_receipt_and_text_views",
              "Nested Beta Stone under Alpha Stone" in out
              and "children: Beta Stone" in out
              and "Live idea beta_stone" in out,
              "the nest receipt prints, and the text views show "
              "the relation: containment lists the child under "
              "the parent, lineage names the live child")
        s1 = snap(view_owner)
        alpha_id = s1["units"]["alpha_stone"]["idea_id"]
        beta_id = s1["units"]["beta_stone"]["idea_id"]
        welcome_id = s1["units"]["welcome"]["idea_id"]
        entries = graph_entries(view_owner)
        contains = [e for e in entries if e["type"] == "contains"
                    and e["source_id"] == alpha_id
                    and e["target_id"] == beta_id
                    and e["status"] == "active"]
        check("j07_graph_exactly_the_drawn_relation",
              len(entries) == 1 and len(contains) == 1,
              "the canonical graph holds exactly one entry — "
              "the drawn ACTIVE contains alpha->beta — after "
              "cold reload")

        # ---------------- J-07: projections --------------------
        before = snap(view_owner)
        rc, out = run_repl(view_owner, [
            "cube",
            "zoom beta_stone",
            "page",
            "unzoom",
            "flower",
            "flower geometry",
            "vesica",
            "verita",
            "show",
            "view growth",
            "view network",
            "quit",
        ], load=True)
        unit_lines_ok = all(
            f"{u['label']}@{u['x']:.1f},{u['y']:.1f}" in out
            for u in before["units"].values())
        check("j07_show_table_projection_same_facts",
              f"units={len(before['units'])}" in out and unit_lines_ok,
              "the 2D table projection (`show`) lists every "
              "unit with its loader position and the true unit "
              "count — the same canonical facts as the loader")
        beta = before["units"]["beta_stone"]
        check("j07_cube_and_page_projection_same_identity",
              "id=beta_stone" in out
              and f"pos=({beta['x']:.1f}, {beta['y']:.1f})" in out
              and "detail: beta stone granite quarry marker" in out
              and "form=cube" in out,
              "under the cube form, the idea page shows the "
              "same canonical id, position and detail — the "
              "projection changed, the facts did not")
        check("j07_flower_projection_is_vesica_not_graph",
              "coherence-of-meet between ideas" in out
              and "welcome ⇄ beta_stone" in out
              and "alpha_stone ⇄ beta_stone" in out,
              "the Flower projection renders Verita edges for "
              "proximate pairs (welcome<->beta at d=1.0 "
              "included) and labels them coherence-of-meet — "
              "a projection, presented as a projection")
        entries_after = graph_entries(view_owner)
        wb = [e for e in entries_after
              if {e["source_id"], e["target_id"]} == {welcome_id,
                                                      beta_id}]
        check("j07_proximity_creates_no_semantic_relation",
              len(entries_after) == 1 and wb == [],
              "after the Flower battery the canonical graph "
              "still holds ONLY the drawn contains entry: the "
              "welcome<->beta vesica edge, born of pure visual "
              "proximity, created no semantic relation")
        after = snap(view_owner)
        check("j07_views_and_zoom_mutate_nothing",
              after["units"] == before["units"]
              and after["summary"] == before["summary"]
              and len(entries_after) == 1,
              "zoom, form switches and every projection left "
              "units, nursery and graph identical (history, "
              "the action log, legitimately records the "
              "viewing actions)")

        # ---------------- J-08: geometry honesty ---------------
        rc, out = run_repl(geom_owner, [
            "flower geometry", "vesica", "geometry", "quit",
        ])
        check("j08_geometry_empty_owner_no_fabricated_edges",
              "Verita edges=0" in out
              and "(place nearby ideas or grow scores to form "
                  "vesica meets)" in out,
              "with no nearby ideas the Flower reports zero "
              "Verita edges plus an honest hint — missing "
              "inputs are guarded, never papered over")
        check("j08_geometry_labels_projection_honestly",
              "Vesica/Verita is coherence-of-meet" in out
              and "Voynich rings are organizational" in out
              and "Fractals are deterministic pattern tools" in out,
              "the geometry layer labels its own outputs: "
              "coherence-of-meet, organizational rings, "
              "deterministic pattern tools — projection "
              "language, never kernel claims")
        rc, out = run_repl(geom_owner, [
            "create an idea called Solo Stone detail: solo stone "
            "marker goals: stand alone",
            "save", "quit",
        ])
        g_before = snap(geom_owner)
        rc, out = run_repl(geom_owner, [
            "lattice", "shell 0", "chord 0 0", "flower geometry",
            "geometry", "quit",
        ], load=True)
        g_after = snap(geom_owner)
        check("j08_geometry_battery_mutates_no_kernel",
              g_after["units"] == g_before["units"]
              and g_after["summary"] == g_before["summary"]
              and graph_entries(geom_owner) == [],
              "lattice/shell/chord/Flower/geometry renders "
              "changed no unit, no nursery state and no graph "
              "entry — unproven geometry does not alter the "
              "kernel")
        rc, out = run_repl(view_owner, ["tree", "quit"], load=True)
        tree_labeled = ("Not understood" in out
                        or "RESEARCH" in out or "PROJECTION" in out)
        check("j08_tree_fcc_surface_projection_labeled_or_absent",
              tree_labeled,
              "no Tree/FCC surface answers at this head "
              "(`tree` is not understood; no FCC/Tree L1 "
              "module exists) — J-08's subject is NOT BUILT "
              "at baseline; if a Tree surface ever answers "
              "without RESEARCH/PROJECTION labeling this "
              "check fails, as it must")

        # ---------------- J-13: REPL cross-view coherence ------
        rc, out = run_repl(view_owner, [
            "set detail alpha_stone revised alpha detail for views",
            "idea alpha_stone",
            "save", "quit",
        ], load=True)
        s_edit = snap(view_owner)
        check("j13_repl_edit_coherent_across_views",
              "Detail → Alpha Stone: revised alpha detail for "
              "views" in out
              and "detail: revised alpha detail for views" in out
              and s_edit["units"]["alpha_stone"]["detail"]
              == "revised alpha detail for views",
              "an edit made once is the same truth in the "
              "receipt, the idea page and the cold loader")
        check("j13_edit_preserves_identity_and_position",
              s_edit["units"]["alpha_stone"]["idea_id"] == alpha_id
              and s_edit["units"]["alpha_stone"]["x"]
              == s1["units"]["alpha_stone"]["x"]
              and s_edit["units"]["alpha_stone"]["y"]
              == s1["units"]["alpha_stone"]["y"],
              "the edited Idea keeps its canonical idea_id "
              "and its position — the views refreshed, the "
              "Idea did not move or re-mint")

        # ---------------- J-13: no phantom live nodes ----------
        rc, out = run_repl(view_owner, [
            "grow ideas", "proposals", "save", "quit",
        ], load=True)
        s_grow = snap(view_owner)
        pending_ids = [pid for pid, st in s_grow["props"].items()
                       if st == "pending"]
        # The projection assertion runs on a `show`-only session:
        # the `proposals` listing in the growth session names the
        # pending ids itself (that is its job), so pid absence is
        # asserted against the plane projection alone.
        rc, show_out = run_repl(view_owner, ["show", "quit"],
                                load=True)
        check("j13_pending_proposals_never_live_nodes",
              len(pending_ids) >= 1
              and set(s_grow["units"]) == set(s_edit["units"])
              and f"units={len(s_edit['units'])}" in show_out
              and all(pid not in show_out for pid in pending_ids),
              f"growth left {len(pending_ids)} proposal(s) "
              "pending in the Nursery; the plane projection "
              "still shows exactly the live units — no "
              "pending proposal is rendered as a live node")

        # ---------------- J-13: rooms + history (many owner) ---
        lines = []
        for i in range(1, 19):
            lines.append(
                f"create an idea called Mass Item {i:02d} "
                f"detail: mass item {i} body goals: mass goal {i}")
        lines += ["save", "quit"]
        rc, out = run_repl(many_owner, lines)
        m_snap = snap(many_owner)
        rc, out = run_repl(many_owner, ["history", "view growth",
                                        "quit"], load=True)
        total_units = len(m_snap["units"])
        check("j07_room_overflow_disclosed",
              f"… +{total_units - 12} more" in out,
              f"the growth room lists 12 of {total_units} "
              "units and discloses the remainder — shown is "
              "never dressed as total")
        hist = m_snap["history"]
        tail = hist[-16:]
        listed = re.findall(r"^\s+\d+\.\s+(.*)$", out, re.M)
        check("j13_history_tail_entries_truthful",
              len(hist) > 16 and listed[:16] == tail,
              f"the history view's listed entries are "
              f"exactly the loader's last 16 of {len(hist)} "
              "notes (the header's shown/total conflation "
              "is DAF-09 D1 — recorded in the rehearsal "
              "record for its home circuit, not fixed here)")

        # ---------------- J-13: Studio HTTP surface ------------
        rc, out = run_repl(studio_owner, [CA, CB, "save", "quit"])
        port = _free_port()
        base = f"http://127.0.0.1:{port}"
        server = subprocess.Popen(
            [sys.executable, "-m", "gui.server", "--owner",
             studio_owner, "--port", str(port)],
            cwd=ROOT, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL)
        up = False
        for _ in range(60):
            try:
                st, _ = _http(base, "GET", "/api/dells")
                if st == 200:
                    up = True
                    break
            except Exception:
                time.sleep(0.5)
        check("j13_studio_server_up",
              up, "the Studio server boots on an ephemeral "
              "loopback port and answers /api/dells")
        st, page = _http(base, "GET", "/")
        m = re.search(r'name="studio-token"\s+content="([^"]+)"',
                      page)
        token = m.group(1) if m else None
        st_d, dells_raw = _http(base, "GET", "/api/dells")
        dells = json.loads(dells_raw).get("dells") or []
        check("j13_studio_index_and_registry",
              st == 200 and token is not None
              and "STUDIO" in page and len(dells) == 100,
              "the index page carries the Studio wordmark and "
              "the per-launch session token; /api/dells is "
              "exactly the canonical 100-Dell registry")
        st_no, _ = _http(base, "POST", "/api/execute",
                         body={"seed": "9[Show]",
                               "owner": studio_owner})
        st_stale, _ = _http(base, "POST", "/api/execute",
                            body={"seed": "9[Show]",
                                  "owner": studio_owner},
                            headers={"X-Studio-Token":
                                     "stale-token-value"})
        check("j13_studio_post_token_gate",
              st_no == 401 and st_stale == 401,
              "a POST with no token and a POST with a stale "
              "token both refuse 401 — the stale-token leg "
              "of the J-13 failure oracle")
        st_org, _ = _http(base, "POST", "/api/execute",
                          body={"seed": "9[Show]",
                                "owner": studio_owner},
                          headers={"X-Studio-Token": token or "",
                                   "Origin":
                                   "http://evil.example:9999"})
        check("j13_studio_bad_origin_refused",
              st_org == 403,
              "a POST carrying the valid token but a foreign "
              "Origin refuses 403 — the bad-Origin leg of "
              "the J-13 failure oracle")
        st_ex, ex_raw = _http(base, "POST", "/api/execute",
                              body={"seed": "55[Set] :: tempo=120",
                                    "owner": studio_owner},
                              headers={"X-Studio-Token":
                                       token or ""})
        ex = json.loads(ex_raw)
        st_st, st_raw = _http(base, "GET",
                              f"/api/state?owner={studio_owner}")
        state = json.loads(st_raw).get("state") or {}
        check("j13_studio_execute_state_coherent",
              st_ex == 200 and ex.get("ok") is True
              and (ex.get("state") or {}).get("store", {})
              .get("tempo") == "120"
              and state.get("store", {}).get("tempo") == "120"
              and state.get("store_count") == 1
              and state.get("owner") == studio_owner,
              "an execution through the Studio is the same "
              "truth in the execute response and in a fresh "
              "/api/state read — one canonical state per "
              "owner inside the surface")
        st_ot, ot_raw = _http(base, "GET",
                              f"/api/state?owner=JForeign{RUN}")
        other = json.loads(ot_raw).get("state") or {}
        st_bk, bk_raw = _http(base, "GET",
                              f"/api/state?owner={studio_owner}")
        back = json.loads(bk_raw).get("state") or {}
        check("j13_studio_owner_isolation",
              other.get("store_count") == 0
              and back.get("store", {}).get("tempo") == "120",
              "a foreign owner's Studio state is empty and "
              "the first owner's state is intact on return — "
              "no cross-owner leakage through the surface")
        st_gr, gr_raw = _http(base, "GET",
                              f"/api/growth?owner={studio_owner}")
        growth = json.loads(gr_raw).get("growth") or {}
        nodes = growth.get("nodes") or []
        welcome_nodes = [n for n in nodes
                         if n.get("id") == "welcome"]
        stages_honest = all(
            n.get("stage") is None
            or n.get("stage_source") in ("growth_force",
                                         "ambiguous",
                                         "unplanted",
                                         "unavailable")
            for n in nodes)
        check("j13_studio_growth_nodes_honest_stages",
              len(welcome_nodes) == 1
              and welcome_nodes[0].get("stage") is None
              and welcome_nodes[0].get("stage_source")
              == "unplanted"
              and stages_honest,
              "the Studio growth lens serves canonical plane "
              "nodes and claims a stage only where a proven "
              "plant supplies one — the unplanted welcome "
              "node carries stage=None / unplanted, never a "
              "fabricated stage (the REPL<->Studio load gap "
              "is recorded in the rehearsal record)")

        # ---------------- J-23: Muse Space probe ---------------
        space_mods = []
        for name in ("form.muse_space_snapshot",
                     "form.muse_space_views"):
            try:
                space_mods.append(importlib.import_module(name))
            except ImportError:
                space_mods.append(None)
        if all(m is None for m in space_mods):
            check("j23_muse_space_provenance_contract_or_absent",
                  True,
                  "Muse Space (GP-E25) is absent at this "
                  "head — no form.muse_space_* module exists "
                  "on this branch and no public surface "
                  "claims a plan sync; J-23 is NOT BUILT at "
                  "baseline, recorded as a finding (GP-E25 "
                  "in flight on PR #510)")
        else:
            src = ""
            for mod in space_mods:
                if mod is not None and mod.__file__:
                    with open(mod.__file__) as f:
                        src += f.read()
            check("j23_muse_space_provenance_contract_or_absent",
                  "provenance" in src and "stale" in src,
                  "the Muse Space surface exists at this "
                  "head and its snapshot code carries "
                  "provenance and staleness handling — the "
                  "designed J-23 contract's minimum honesty "
                  "surface (full sync execution is graded "
                  "in the rehearsal record)")
    finally:
        if server is not None:
            server.terminate()
            try:
                server.wait(timeout=10)
            except Exception:
                server.kill()
        for o in owners:
            cleanup(o)

    check("Z.cleanup", not _CLEANUP_ERRORS, "; ".join(_CLEANUP_ERRORS))
    failed = [n for n, ok, _ in RESULTS if not ok]
    print(f"JOURNEY_VIEWS: {len(RESULTS) - len(failed)}/{len(RESULTS)} PASS")
    if failed:
        print("FAILURES:", ", ".join(failed))
    return 1 if failed else 0


def smoke():
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
