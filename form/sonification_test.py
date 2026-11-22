"""SOUND S0 suite — pure read-only sonification projection.

Director ruling 7085160720 on PR #505 (2026-11-22): S0 authorizes a
pure, deterministic SonicDescriptor projection in
form/dell_matrix/sonification.py — pitch from the harmonic_lattice
chromatic law over quantized H/V/F, set harmony ONLY from
form/dell_matrix/harmony.py::harmony_score on a real named active
neighborhood of 2+, spatial cue fields reusing spatial_audio.py
listener/view coordinates (hz_hint never promoted). Fail-first
acceptance named in the ruling: one_state_one_sound,
different_actual_math_changes_sound, unknown_is_silence,
solo_not_pair_harmony, view_audio_parity, no_authority (accessibility
is S1, not S0). Written failing-first: RED while
form/dell_matrix/sonification.py is absent.
"""
import copy
import importlib
import json
import math
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RESULTS = []
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(("PASS " if cond else "FAIL ") + name +
          ((": " + detail) if (detail and not cond) else ""), flush=True)


def load_module():
    return importlib.import_module("form.dell_matrix.sonification")


class RefIdea:
    """Contract-valid harmony_score input (title + active properties
    + a readable canonical lifecycle state, as a real Idea exposes)."""

    def __init__(self, title, props, idea_state="active"):
        self.title = title
        self.idea_state = idea_state
        self._props = dict(props)

    def get_active_properties(self):
        return dict(self._props)


IDEA_A = {
    "idea_id": "idea-alpha",
    "owner": "ace",
    "source_revision": "rev-7",
    "coords": {"h": 1, "v": 0, "f": 0},
    "origin_note": 0,
    "active": True,
    "idea_state": "active",
    "title": "harbor light keeper",
    "properties": {"mood": "calm water"},
}
IDEA_B = {
    "idea_id": "idea-beta",
    "owner": "ace",
    "source_revision": "rev-7",
    "coords": {"h": 0, "v": 1, "f": 0},
    "origin_note": 0,
    "active": True,
    "idea_state": "active",
    "title": "harbor light tender",
    "properties": {"mood": "calm stone"},
}
IDEA_C = {
    "idea_id": "idea-gamma",
    "owner": "ace",
    "source_revision": "rev-7",
    "coords": {"h": 2, "v": 2, "f": 0},
    "origin_note": 0,
    "active": True,
    "idea_state": "active",
    "title": "harbor bell ringer",
    "properties": {"mood": "bright water"},
}
NEIGHBORHOOD = {"name": "north-cluster", "members": [IDEA_A, IDEA_B, IDEA_C]}

LISTENER_E = {"pos": (0.0, 0.0), "facing": "E"}
LISTENER_W = {"pos": (9.0, 3.0), "facing": "W"}


def approx(a, b, tol=1e-9):
    return a is not None and b is not None and abs(a - b) <= tol


def main():
    try:
        son = load_module()
    except Exception as exc:  # module absent at RED time
        check("module_importable", False, repr(exc))
        return finish()
    check("module_importable", True)

    from form.dell_matrix.harmonic_lattice import HarmonicLattice
    from form.dell_matrix.harmony import harmony_score
    from form.dell_matrix import spatial_audio as sa

    # ---- schema / provenance -------------------------------------
    d = son.sonify_idea(copy.deepcopy(IDEA_A))
    dd = d.to_dict()
    for field_name in ("kind", "idea_id", "owner", "source_revision",
                       "projection_version", "status", "reasons",
                       "pitch_class", "note_name", "octave", "frequency_hz",
                       "harmony_score", "harmony_status", "neighborhood",
                       "brightness", "interval_semitones", "member_ids",
                       "pitch_classes", "spatial", "measured_inputs",
                       "mapping"):
        if field_name not in dd:
            check("descriptor_schema_fields", False, "missing " + field_name)
            break
    else:
        check("descriptor_schema_fields", True)
    check("projection_version_declared",
          dd["projection_version"] == son.PROJECTION_VERSION == "sonification/1")
    check("provenance_echoed",
          dd["idea_id"] == "idea-alpha" and dd["owner"] == "ace"
          and dd["source_revision"] == "rev-7" and dd["kind"] == "idea"
          and dd["status"] == "supported")

    # ---- golden pitch (hand-computed from the chromatic law) -----
    # A: (0 + 7*1 + 4*0) % 12 = 7 -> G, octave 4, midi 67.
    check("golden_pitch_fifth",
          d.pitch_class == 7 and d.note_name == "G" and d.octave == 4
          and approx(d.frequency_hz, 391.995, 0.01),
          f"pc={d.pitch_class} note={d.note_name} hz={d.frequency_hz}")
    # B: (0 + 0 + 4*1) % 12 = 4 -> E, midi 64.
    db = son.sonify_idea(copy.deepcopy(IDEA_B))
    check("golden_pitch_third",
          db.pitch_class == 4 and db.note_name == "E"
          and approx(db.frequency_hz, 329.628, 0.01),
          f"pc={db.pitch_class} note={db.note_name} hz={db.frequency_hz}")
    # Origin cell: pc 0 -> C, midi 60.
    origin = dict(IDEA_A, coords={"h": 0, "v": 0, "f": 0})
    do = son.sonify_idea(origin)
    check("golden_pitch_origin",
          do.pitch_class == 0 and do.note_name == "C"
          and approx(do.frequency_hz, 261.626, 0.01))
    # note_at parity over a grid: descriptor note name is the lattice's own.
    lat = HarmonicLattice(origin_note=0)
    parity = True
    for h in range(-2, 4):
        for v in range(-2, 4):
            for f in (0, 1):
                got = son.sonify_idea(dict(IDEA_A, coords={"h": h, "v": v, "f": f}))
                want_name = lat.note_at(h, v, f).rsplit("_o", 1)[0]
                if got.note_name != want_name:
                    parity = False
    check("golden_note_matches_note_at", parity)
    # f raises the octave: f=1 -> octave 5, midi 72 for pc 0.
    up = son.sonify_idea(dict(IDEA_A, coords={"h": 0, "v": 0, "f": 1}))
    check("golden_octave_from_floor",
          up.octave == 5 and approx(up.frequency_hz, 523.251, 0.01))
    # Octave bounded: extreme floors clamp into [MIN_OCTAVE, MAX_OCTAVE].
    hi = son.sonify_idea(dict(IDEA_A, coords={"h": 0, "v": 0, "f": 99}))
    lo = son.sonify_idea(dict(IDEA_A, coords={"h": 0, "v": 0, "f": -99}))
    check("octave_bounded",
          hi.octave == son.MAX_OCTAVE and lo.octave == son.MIN_OCTAVE
          and math.isfinite(hi.frequency_hz) and math.isfinite(lo.frequency_hz)
          and 50.0 < lo.frequency_hz < hi.frequency_hz < 5000.0)
    # Non-default origin note shifts by the law: origin 3, cell (0,0) -> pc 3.
    shifted = son.sonify_idea(dict(IDEA_A, origin_note=3,
                                   coords={"h": 0, "v": 0, "f": 0}))
    check("origin_note_respected",
          shifted.pitch_class == 3 and shifted.note_name == "D#")
    # Plane position quantizes exactly as rebuild_from_plane does.
    class _Unit:
        def __init__(self, x, y):
            self.x, self.y, self.label = x, y, "u"
    class _Plane:
        units = {"idea-alpha": _Unit(1.4, 2.6)}
    lat2 = HarmonicLattice()
    lat2.rebuild_from_plane(_Plane())
    cell_key = next(k for k, c in lat2.cells.items()
                    if "idea-alpha" in c.members)
    dp = son.sonify_idea(dict(IDEA_A, coords=None,
                              position={"x": 1.4, "y": 2.6}))
    dp2 = {k: v for k, v in IDEA_A.items() if k != "coords"}
    dp2["position"] = {"x": 1.4, "y": 2.6}
    dp = son.sonify_idea(dp2)
    check("position_quantization_matches_rebuild",
          tuple(dp.measured_inputs["coords"]) == cell_key
          and dp.pitch_class == (0 + 7 * cell_key[0] + 4 * cell_key[1]) % 12,
          f"cell={cell_key} measured={dp.measured_inputs.get('coords')}")

    # ---- one_state_one_sound --------------------------------------
    again = son.sonify_idea(copy.deepcopy(IDEA_A),
                            neighborhood=copy.deepcopy(NEIGHBORHOOD))
    first = son.sonify_idea(copy.deepcopy(IDEA_A),
                            neighborhood=copy.deepcopy(NEIGHBORHOOD))
    check("one_state_one_sound_inprocess", first.to_dict() == again.to_dict())
    # Save/reload across processes: snapshot JSON on disk, two separate
    # processes must produce byte-identical descriptor JSON.
    snap = {"idea": IDEA_A, "neighborhood": NEIGHBORHOOD}
    code = (
        "import json,sys;"
        "from form.dell_matrix.sonification import sonify_idea;"
        "snap=json.load(open(sys.argv[1]));"
        "d=sonify_idea(snap['idea'], neighborhood=snap['neighborhood']);"
        "print(json.dumps(d.to_dict(), sort_keys=True))"
    )
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "snap.json")
        with open(path, "w") as fh:
            json.dump(snap, fh)
        outs = []
        for _ in range(2):
            proc = subprocess.run([sys.executable, "-B", "-c", code, path],
                                  cwd=ROOT, capture_output=True, text=True,
                                  timeout=120)
            outs.append(proc.stdout.strip())
        local = json.dumps(first.to_dict(), sort_keys=True)
        check("one_state_one_sound_save_reload_processes",
              proc.returncode == 0 and outs[0] == outs[1] == local,
              f"rc={proc.returncode} err={proc.stderr[-200:]}")
    check("deterministic_two_process_reruns", outs[0] == outs[1] and outs[0] != "")

    # ---- different_actual_math_changes_sound ----------------------
    moved = son.sonify_idea(dict(IDEA_A, coords={"h": 2, "v": 0, "f": 0}))
    check("different_math_changes_pitch",
          moved.pitch_class == 2 and moved.note_name == "D"
          and not approx(moved.frequency_hz, d.frequency_hz, 0.01)
          and moved.owner == d.owner
          and moved.source_revision == d.source_revision
          and moved.idea_id == d.idea_id)
    duo = {"name": "duo", "members": [IDEA_A, IDEA_B]}
    h_trio = son.sonify_idea(copy.deepcopy(IDEA_A),
                             neighborhood=copy.deepcopy(NEIGHBORHOOD))
    h_duo = son.sonify_idea(copy.deepcopy(IDEA_A),
                            neighborhood=copy.deepcopy(duo))
    check("different_math_changes_harmony_only",
          h_trio.harmony_score is not None and h_duo.harmony_score is not None
          and not approx(h_trio.harmony_score, h_duo.harmony_score, 1e-9)
          and h_trio.pitch_class == h_duo.pitch_class
          and approx(h_trio.frequency_hz, h_duo.frequency_hz, 1e-9))

    # ---- harmony: real source function, named set of 2+ -----------
    refs = [RefIdea(m["title"], m["properties"]) for m in NEIGHBORHOOD["members"]]
    want = harmony_score(refs)
    check("harmony_matches_source_function",
          approx(h_trio.harmony_score, want, 1e-9)
          and h_trio.harmony_status == "available"
          and h_trio.neighborhood == "north-cluster"
          and approx(h_trio.brightness, want, 1e-9),
          f"got={h_trio.harmony_score} want={want}")
    twins = {"name": "twins", "members": [IDEA_A, dict(IDEA_A, idea_id="idea-alpha2")]}
    h_twins = son.sonify_idea(copy.deepcopy(IDEA_A),
                              neighborhood=copy.deepcopy(twins))
    check("harmony_identical_set_zero",
          h_twins.harmony_score is not None
          and approx(h_twins.harmony_score, 0.0, 1e-12))
    solo = son.sonify_idea(copy.deepcopy(IDEA_A))
    check("solo_not_pair_harmony_no_neighborhood",
          solo.harmony_score is None and solo.harmony_status == "unavailable")
    one_member = {"name": "solo-set", "members": [IDEA_A]}
    h_solo = son.sonify_idea(copy.deepcopy(IDEA_A),
                             neighborhood=copy.deepcopy(one_member))
    check("solo_not_pair_harmony_one_member_set",
          h_solo.harmony_score is None
          and h_solo.harmony_status == "unavailable")
    # Inactive and cross-owner members are excluded and disclosed.
    mixed = {"name": "mixed", "members": [
        IDEA_A, IDEA_B,
        dict(IDEA_C, active=False),
        dict(IDEA_C, idea_id="idea-foreign", owner="mallory"),
    ]}
    h_mixed = son.sonify_idea(copy.deepcopy(IDEA_A),
                              neighborhood=copy.deepcopy(mixed))
    check("neighborhood_exclusions_disclosed",
          h_mixed.harmony_score is not None
          and approx(h_mixed.harmony_score,
                     harmony_score([RefIdea(IDEA_A["title"], IDEA_A["properties"]),
                                    RefIdea(IDEA_B["title"], IDEA_B["properties"])]),
                     1e-9)
          and h_mixed.measured_inputs["neighborhood_members_supplied"] == 4
          and h_mixed.measured_inputs["neighborhood_members_scored"] == 2)
    thin = {"name": "thin", "members": [IDEA_A, dict(IDEA_B, active=False)]}
    h_thin = son.sonify_idea(copy.deepcopy(IDEA_A),
                             neighborhood=copy.deepcopy(thin))
    check("neighborhood_below_two_after_exclusions",
          h_thin.harmony_score is None
          and h_thin.harmony_status == "unavailable")
    # harmony_score's own canonical gate: a member whose measured
    # lifecycle reads faded does not participate, even with active=True.
    faded = {"name": "faded-set", "members": [
        IDEA_A, IDEA_B, dict(IDEA_C, idea_state="faded")]}
    h_faded = son.sonify_idea(copy.deepcopy(IDEA_A),
                              neighborhood=copy.deepcopy(faded))
    check("neighborhood_faded_member_excluded_by_source_gate",
          h_faded.harmony_score is not None
          and approx(h_faded.harmony_score,
                     harmony_score([RefIdea(IDEA_A["title"], IDEA_A["properties"]),
                                    RefIdea(IDEA_B["title"], IDEA_B["properties"])]),
                     1e-9)
          and h_faded.measured_inputs["neighborhood_members_supplied"] == 3
          and h_faded.measured_inputs["neighborhood_members_scored"] == 2)
    # A member carrying no readable lifecycle state at all is likewise
    # excluded by the source gate (fail-closed, never assumed active).
    stateless = {"name": "stateless-set", "members": [
        IDEA_A, {k: v for k, v in IDEA_B.items() if k != "idea_state"}]}
    h_stateless = son.sonify_idea(copy.deepcopy(IDEA_A),
                                  neighborhood=copy.deepcopy(stateless))
    check("neighborhood_stateless_member_excluded_by_source_gate",
          h_stateless.harmony_score is None
          and h_stateless.harmony_status == "unavailable"
          and h_stateless.measured_inputs["neighborhood_members_scored"] == 1)

    # Golden cross-check on REAL Idea objects: mappings extracted the
    # way a real caller extracts them (id, title, active properties,
    # idea_state.value) must score exactly what harmony_score computes
    # over the Idea objects themselves.
    from form.mandell.idea import Idea as RealIdea
    real = []
    extracted = []
    for src in (IDEA_A, IDEA_B, IDEA_C):
        ri = RealIdea(idea_id=src["idea_id"], title=src["title"])
        for k, v in src["properties"].items():
            ri.set_property(k, v)
        real.append(ri)
        extracted.append({
            "idea_id": ri.id, "owner": "ace", "title": ri.title,
            "properties": ri.get_active_properties(),
            "idea_state": ri.idea_state.value, "active": True,
        })
    real_hood = {"name": "real-hood", "members": extracted}
    h_real = son.sonify_idea(dict(IDEA_A, idea_id="idea-alpha"),
                             neighborhood=real_hood)
    check("harmony_real_idea_objects",
          h_real.harmony_score is not None
          and h_real.harmony_score > 0.0
          and approx(h_real.harmony_score, harmony_score(real), 1e-9)
          and h_real.measured_inputs["neighborhood_members_scored"] == 3,
          f"got={h_real.harmony_score} want={harmony_score(real)}")

    # ---- unknown_is_silence ---------------------------------------
    def silent(desc):
        return (desc.status == "unavailable" and desc.pitch_class is None
                and desc.frequency_hz is None and desc.note_name is None)
    no_coords = {k: v for k, v in IDEA_A.items() if k != "coords"}
    check("unknown_missing_coords", silent(son.sonify_idea(no_coords)))
    check("unknown_float_coordinate",
          silent(son.sonify_idea(dict(IDEA_A, coords={"h": 1.5, "v": 0, "f": 0}))))
    check("unknown_string_coordinate",
          silent(son.sonify_idea(dict(IDEA_A, coords={"h": "x", "v": 0, "f": 0}))))
    nan_pos = dict(no_coords, position={"x": float("nan"), "y": 0.0})
    check("unknown_nan_position", silent(son.sonify_idea(nan_pos)))
    inf_pos = dict(no_coords, position={"x": 0.0, "y": float("inf")})
    check("unknown_inf_position", silent(son.sonify_idea(inf_pos)))
    check("unknown_inactive_idea",
          silent(son.sonify_idea(dict(IDEA_A, active=False))))
    no_owner = {k: v for k, v in IDEA_A.items() if k != "owner"}
    check("unknown_missing_owner", silent(son.sonify_idea(no_owner)))
    check("unknown_empty_owner",
          silent(son.sonify_idea(dict(IDEA_A, owner="  "))))
    no_id = {k: v for k, v in IDEA_A.items() if k != "idea_id"}
    d_noid = son.sonify_idea(no_id)
    check("unknown_missing_id", silent(d_noid) and d_noid.idea_id is None)
    for bad in (None, "a string", 42, [1, 2]):
        try:
            d_bad = son.sonify_idea(bad)
            ok = d_bad.status == "unavailable" and d_bad.pitch_class is None
        except Exception:
            ok = False
        if not ok:
            check("malformed_top_level_inputs", False, repr(bad))
            break
    else:
        check("malformed_top_level_inputs", True)
    # An unavailable descriptor never invents a replacement identity.
    ghost = son.sonify_idea(dict(IDEA_A, coords=None))
    check("orphan_no_replacement",
          ghost.idea_id == "idea-alpha" and ghost.status == "unavailable"
          and ghost.harmony_score is None)

    # ---- relations --------------------------------------------------
    rel = son.sonify_relation(copy.deepcopy(IDEA_A), copy.deepcopy(IDEA_B))
    want_pair = harmony_score([RefIdea(IDEA_A["title"], IDEA_A["properties"]),
                               RefIdea(IDEA_B["title"], IDEA_B["properties"])])
    check("relation_pair_harmony_and_interval",
          rel.kind == "relation" and rel.status == "supported"
          and approx(rel.harmony_score, want_pair, 1e-9)
          and rel.interval_semitones == (4 - 7) % 12
          and rel.member_ids == ("idea-alpha", "idea-beta")
          and rel.pitch_classes == (7, 4),
          f"h={rel.harmony_score} want={want_pair} iv={rel.interval_semitones}")
    foreign = son.sonify_relation(copy.deepcopy(IDEA_A),
                                  dict(IDEA_B, owner="mallory"))
    check("relation_cross_owner_silence",
          foreign.status == "unavailable" and foreign.harmony_score is None
          and foreign.interval_semitones is None)
    self_rel = son.sonify_relation(copy.deepcopy(IDEA_A), copy.deepcopy(IDEA_A))
    check("relation_same_idea_refused",
          self_rel.status == "unavailable" and self_rel.harmony_score is None)
    inactive_rel = son.sonify_relation(copy.deepcopy(IDEA_A),
                                        dict(IDEA_B, active=False))
    check("relation_inactive_member_silence",
          inactive_rel.status == "unavailable"
          and inactive_rel.harmony_score is None)
    nocoord_rel = son.sonify_relation(no_coords, copy.deepcopy(IDEA_B))
    check("relation_missing_coords_keeps_measured_harmony",
          nocoord_rel.status == "supported"
          and nocoord_rel.interval_semitones is None
          and approx(nocoord_rel.harmony_score, want_pair, 1e-9))

    # ---- view_audio_parity + spatial cues ---------------------------
    pos_a = dict(IDEA_A, position={"x": 4.0, "y": 0.0})
    view1 = son.sonify_idea(copy.deepcopy(pos_a),
                            neighborhood=copy.deepcopy(NEIGHBORHOOD),
                            listener=copy.deepcopy(LISTENER_E))
    view2 = son.sonify_idea(copy.deepcopy(pos_a),
                            neighborhood=copy.deepcopy(NEIGHBORHOOD),
                            listener=copy.deepcopy(LISTENER_W))
    semantic = ("pitch_class", "note_name", "octave", "frequency_hz",
                "harmony_score", "brightness", "status")
    check("view_audio_parity",
          all(getattr(view1, f) == getattr(view2, f) for f in semantic)
          and view1.spatial is not None and view2.spatial is not None
          and view1.spatial["pan"] != view2.spatial["pan"],
          f"pan1={view1.spatial and view1.spatial.get('pan')} "
          f"pan2={view2.spatial and view2.spatial.get('pan')}")
    dist, rel_bearing = sa._rel_polar((0.0, 0.0), "E", (4.0, 0.0))
    want_cue = {
        "dist": round(dist, 2), "bearing": round(rel_bearing, 1),
        "pan": round(sa.pan_from_bearing(rel_bearing), 3),
        "gain": round(sa.gain_from_distance(dist), 3),
        "band": sa.band_from_distance(dist),
        "ear": sa.ear_from_pan(sa.pan_from_bearing(rel_bearing)),
    }
    check("spatial_cue_fields_match_source", view1.spatial == want_cue,
          f"got={view1.spatial} want={want_cue}")
    check("spatial_hz_hint_not_promoted",
          "hz_hint" not in (view1.spatial or {})
          and approx(view1.frequency_hz, 391.995, 0.01))
    no_listener = son.sonify_idea(copy.deepcopy(IDEA_A))
    check("no_listener_no_spatial",
          no_listener.spatial is None and no_listener.pitch_class == 7)

    # ---- immutability / reserialization -----------------------------
    snap_in = {"idea": copy.deepcopy(IDEA_A),
               "neighborhood": copy.deepcopy(NEIGHBORHOOD),
               "listener": copy.deepcopy(LISTENER_E)}
    before = json.dumps(snap_in, sort_keys=True)
    son.sonify_idea(snap_in["idea"], neighborhood=snap_in["neighborhood"],
                    listener=snap_in["listener"])
    son.sonify_relation(snap_in["idea"], copy.deepcopy(IDEA_B))
    after = json.dumps(snap_in, sort_keys=True)
    check("snapshot_immutability", before == after)
    s1 = json.dumps(view1.to_dict(), sort_keys=True)
    s2 = json.dumps(json.loads(s1), sort_keys=True)
    check("reserialization_unchanged", s1 == s2)

    # ---- no_authority -------------------------------------------------
    with tempfile.TemporaryDirectory() as td:
        code2 = (
            "from form.dell_matrix.sonification import sonify_idea;"
            "idea=" + repr(IDEA_A) + ";"
            "d=sonify_idea(idea);"
            "print(d.status)"
        )
        proc = subprocess.run([sys.executable, "-B", "-c", code2],
                              cwd=td, capture_output=True, text=True,
                              timeout=120,
                              env=dict(os.environ, PYTHONPATH=ROOT))
        leftover = os.listdir(td)
        check("no_authority_no_writes",
              proc.returncode == 0 and proc.stdout.strip() == "supported"
              and leftover == [],
              f"rc={proc.returncode} files={leftover} err={proc.stderr[-200:]}")
    import form.dell_matrix.sonification as _mod
    src = open(_mod.__file__, encoding="utf-8").read()
    banned = ("socket", "urllib", "requests", "subprocess", "shutil",
              "os.remove", "os.unlink", ".confirm(", "network")
    found = [b for b in banned if b in src]
    check("no_authority_source_fences", found == [], f"found={found}")

    return finish()


def finish():
    n = sum(1 for _, ok in RESULTS if ok)
    print(f"SONIFICATION: {n}/{len(RESULTS)}", flush=True)
    return 0 if n == len(RESULTS) else 1


def smoke():
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
