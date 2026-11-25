#!/usr/bin/env python3
"""
Sonification projection — SOUND S0 (Director ruling 7085160720, PR #505).

A pure, deterministic, read-only projection from canonical idea state
to a compact typed SonicDescriptor. Sound is DERIVED PRESENTATION over
the one underlying state: this module holds no store, writes nothing,
confirms nothing, and changes no idea. Changing a view cannot change
an idea; listening cannot change anything at all.

MATH SOURCES (the actual functions, never re-derived):

  * Pitch — the chromatic overlay law of
    form/dell_matrix/harmonic_lattice.py: pitch_class =
    (origin_note + 7*h + 4*v) mod 12 over the idea's quantized lattice
    coordinates (h, v, f). The note name comes from
    HarmonicLattice.note_at itself. Coordinates come from the idea's
    measured "coords" input, or from its measured plane "position"
    quantized exactly as HarmonicLattice.rebuild_from_plane quantizes
    (int(round(x)), int(round(y)), f = 0).
  * Set harmony — form/dell_matrix/harmony.py::harmony_score over a
    real, named, active neighborhood supplied by the caller. The
    scored set is exactly the supplied members that are active,
    well-formed and owned by the idea's owner, counted once per
    (owner, idea_id) identity — a repeated record of one identity is
    one member, never two, and repeated records that disagree on the
    scored data make the harmony explicitly unavailable; exclusions
    are counted in measured_inputs. Fewer than 2 scored members -> the
    relation score is unavailable. A solo idea is NEVER scored:
    harmony_score's solo shortcut (1.0) does not license a harmony
    claim.
  * Space — spatial cue fields reuse form/dell_matrix/spatial_audio.py
    listener/view geometry (relative polar bearing, pan, gain, band,
    ear). spatial_audio's hz_hint is a spatial cue hint only; it is
    never promoted to the per-idea tone and never appears here.

SONIFICATION CONVENTIONS (labelled choices, NOT intrinsic truths):

  * Reference tuning: equal temperament, A4 = 440 Hz (MIDI 69).
    frequency_hz = 440 * 2 ** ((midi - 69) / 12),
    midi = 12 * (octave + 1) + pitch_class. An idea has no intrinsic
    physical frequency; this maps its pitch class into audible Hz.
  * Octave: octave = clamp(BASE_OCTAVE + f, MIN_OCTAVE, MAX_OCTAVE)
    with BASE_OCTAVE = 4, MIN_OCTAVE = 2, MAX_OCTAVE = 6, so every
    frequency stays finite in [65.4, 3951.1] Hz.
  * Brightness: brightness = harmony_score, a linear ENCODING CHOICE
    for a future renderer, not a measured quantity.

DETERMINISM: same measured inputs + same projection version + same
listener context -> the same descriptor. No randomness, no wall
clock, no identifier hashing. Invalid, absent, inactive or foreign
inputs are disclosed as unavailable with reasons; nothing is faked
and no replacement idea is ever constructed.

INPUT SHAPE (plain mappings, as a caller extracts from canonical
state; the projection never mutates them):

  idea: {"idea_id": str, "owner": str, "source_revision": str|int,
         "coords": {"h": int, "v": int, "f": int (optional)},
         "position": {"x": float, "y": float} (alternative to coords),
         "origin_note": int (optional, default 0),
         "active": bool (optional, default True),
         "idea_state": str (canonical lifecycle state, e.g. "active";
         neighborhood members only participate when this reads active
         under canonical_lifecycle — harmony_score's own fail-closed
         gate, applied identically here),
         "title": str, "properties": {name: value}}
  neighborhood: {"name": str, "members": [idea, ...]}
  listener: {"pos": (x, y), "facing": str}
"""
from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from form.dell_matrix.canonical_lifecycle import is_idea_active
from form.dell_matrix.harmonic_lattice import HarmonicLattice, NOTES
from form.dell_matrix.harmony import harmony_score
from form.dell_matrix.spatial_audio import (
    _rel_polar,
    band_from_distance,
    ear_from_pan,
    gain_from_distance,
    pan_from_bearing,
)

PROJECTION_VERSION = "sonification/1"

# Reference tuning (sonification convention; see module docstring).
REFERENCE_A4_HZ = 440.0
REFERENCE_A4_MIDI = 69
BASE_OCTAVE = 4
MIN_OCTAVE = 2
MAX_OCTAVE = 6

MAPPING_LABELS = {
    "pitch": "chromatic law (origin_note + 7h + 4v) mod 12 via "
             "harmonic_lattice.note_at; sonification convention over "
             "actual coordinates, not an intrinsic frequency",
    "frequency": "equal temperament, A4 = 440 Hz reference; "
                 "octave = clamp(4 + f, 2, 6)",
    "harmony": "form.dell_matrix.harmony.harmony_score over the named "
               "active neighborhood (2+ scored members); a solo idea is "
               "never scored",
    "brightness": "linear encoding choice: brightness = harmony_score; "
                  "not a measured quantity",
    "spatial": "spatial_audio listener/view cue geometry; hz_hint is a "
               "cue hint, never the per-idea tone",
}


@dataclass(frozen=True)
class SonicDescriptor:
    """One idea's (or one pair's) derived sound, with provenance."""

    kind: str  # "idea" | "relation"
    idea_id: Optional[str]
    owner: Optional[str]
    source_revision: Any
    projection_version: str
    status: str  # "supported" | "unavailable"
    reasons: Tuple[str, ...] = ()
    pitch_class: Optional[int] = None
    note_name: Optional[str] = None
    octave: Optional[int] = None
    frequency_hz: Optional[float] = None
    harmony_score: Optional[float] = None
    harmony_status: str = "unavailable"
    neighborhood: Optional[str] = None
    brightness: Optional[float] = None
    interval_semitones: Optional[int] = None
    member_ids: Tuple[str, ...] = ()
    pitch_classes: Tuple[int, ...] = ()
    spatial: Optional[Dict[str, Any]] = None
    measured_inputs: Dict[str, Any] = field(default_factory=dict)
    mapping: Dict[str, str] = field(default_factory=lambda: dict(MAPPING_LABELS))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "kind": self.kind,
            "idea_id": self.idea_id,
            "owner": self.owner,
            "source_revision": self.source_revision,
            "projection_version": self.projection_version,
            "status": self.status,
            "reasons": list(self.reasons),
            "pitch_class": self.pitch_class,
            "note_name": self.note_name,
            "octave": self.octave,
            "frequency_hz": self.frequency_hz,
            "harmony_score": self.harmony_score,
            "harmony_status": self.harmony_status,
            "neighborhood": self.neighborhood,
            "brightness": self.brightness,
            "interval_semitones": self.interval_semitones,
            "member_ids": list(self.member_ids),
            "pitch_classes": list(self.pitch_classes),
            "spatial": dict(self.spatial) if self.spatial is not None else None,
            "measured_inputs": dict(self.measured_inputs),
            "mapping": dict(self.mapping),
        }


class _TokenSource:
    """Duck-typed harmony_score input built from measured fields.

    harmony_score reads .title and .get_active_properties() for its
    tokens, and canonical_lifecycle.is_idea_active reads .idea_state:
    harmony_score fail-closes on members whose canonical lifecycle is
    unreadable, so this adapter exposes exactly the member's measured
    lifecycle state (never an assumed one) alongside its tokens.
    """

    __slots__ = ("title", "idea_state", "_props")

    def __init__(self, title: str, props: Dict[str, Any], idea_state: Any):
        self.title = title
        self.idea_state = idea_state
        self._props = dict(props)

    def get_active_properties(self) -> Dict[str, Any]:
        return dict(self._props)


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_finite_number(value: Any) -> bool:
    if not (isinstance(value, (int, float)) and not isinstance(value, bool)):
        return False
    try:
        return math.isfinite(float(value))
    except (OverflowError, TypeError, ValueError):
        # Huge ints (float(10**1000)) overflow float conversion; they are
        # not finite measured numbers, never an exception (Director
        # 7088588966: the projection never raises on bad input).
        return False


def _identity(idea: Any) -> Tuple[Optional[str], Optional[str], List[str]]:
    """Validate identity-level fields. Returns (idea_id, owner, reasons)."""
    reasons: List[str] = []
    if not isinstance(idea, Mapping):
        return None, None, ["idea_not_a_mapping"]
    idea_id = idea.get("idea_id")
    if not (isinstance(idea_id, str) and idea_id.strip()):
        idea_id = None
        reasons.append("idea_id_missing")
    owner = idea.get("owner")
    if not (isinstance(owner, str) and owner.strip()):
        owner = None
        reasons.append("owner_missing")
    return idea_id, owner, reasons


def _active_state(idea: Mapping) -> Tuple[bool, Optional[str]]:
    """(is_active, reason_if_not). Absent flag defaults to active."""
    if "active" not in idea:
        return True, None
    flag = idea.get("active")
    if not isinstance(flag, bool):
        return False, "invalid_active_flag"
    if not flag:
        return False, "inactive"
    return True, None


def _coords_of(idea: Mapping) -> Tuple[Optional[Tuple[int, int, int]],
                                       Optional[str], Optional[str],
                                       Optional[Tuple[float, float]]]:
    """Resolve quantized (h, v, f) from measured coords or position.

    Returns (coords, coords_source, reason_if_unavailable, raw_position).
    Position quantization mirrors rebuild_from_plane exactly.
    """
    raw_position: Optional[Tuple[float, float]] = None
    pos = idea.get("position")
    if isinstance(pos, Mapping):
        x, y = pos.get("x"), pos.get("y")
        if _is_finite_number(x) and _is_finite_number(y):
            raw_position = (float(x), float(y))
    coords_raw = idea.get("coords")
    if coords_raw is not None:
        if not isinstance(coords_raw, Mapping):
            return None, None, "invalid_coordinate", raw_position
        h, v = coords_raw.get("h"), coords_raw.get("v")
        f = coords_raw.get("f", 0)
        if not (_is_int(h) and _is_int(v) and _is_int(f)):
            return None, None, "invalid_coordinate", raw_position
        if not (_is_finite_number(h) and _is_finite_number(v)
                and _is_finite_number(f)):
            # An integer too large to represent as a finite float is
            # outside safe spatial geometry: refuse it typed here
            # rather than let a downstream float() conversion raise
            # OverflowError (Director 7095214624).
            return None, None, "invalid_coordinate", raw_position
        return (int(h), int(v), int(f)), "coords", None, raw_position
    if pos is not None:
        if raw_position is None:
            return None, None, "invalid_position", None
        x, y = raw_position
        return (int(round(x)), int(round(y)), 0), "position", None, raw_position
    return None, None, "coordinate_missing", None


def _pitch(coords: Tuple[int, int, int], origin_note: int) -> Tuple[int, str, int, float]:
    """(pitch_class, note_name, octave, frequency_hz) for a coordinate.

    The note name is harmonic_lattice's own note_at output; the pitch
    class is that name's index in NOTES, so the two cannot disagree.
    """
    h, v, f = coords
    note_label = HarmonicLattice(origin_note=origin_note).note_at(h, v, f)
    note_name = note_label.rsplit("_o", 1)[0]
    pitch_class = NOTES.index(note_name)
    octave = min(MAX_OCTAVE, max(MIN_OCTAVE, BASE_OCTAVE + f))
    midi = 12 * (octave + 1) + pitch_class
    frequency = round(REFERENCE_A4_HZ * 2.0 ** ((midi - REFERENCE_A4_MIDI) / 12.0), 3)
    return pitch_class, note_name, octave, frequency


def _member_adapter(member: Any, owner: Optional[str]) -> Optional[_TokenSource]:
    """A scored-set member, or None when it must be excluded."""
    if not isinstance(member, Mapping):
        return None
    mid = member.get("idea_id")
    if not (isinstance(mid, str) and mid.strip()):
        return None
    if member.get("owner") != owner:
        return None  # foreign-owned: not ours to assert over
    active, _ = _active_state(member)
    if not active:
        return None
    title = member.get("title", "")
    if not isinstance(title, str):
        return None
    props = member.get("properties", {})
    if not isinstance(props, Mapping):
        return None
    state = member.get("idea_state", member.get("lifecycle_state"))
    adapter = _TokenSource(title, dict(props), state)
    if not is_idea_active(adapter):
        # harmony_score's own gate: a member whose measured canonical
        # lifecycle does not read active does not participate. The
        # projection applies the same gate up front so the disclosed
        # scored count is exactly the set the score was computed over.
        return None
    return adapter


def _score_neighborhood(idea: Mapping, owner: Optional[str],
                        neighborhood: Any,
                        measured: Dict[str, Any]) -> Tuple[Optional[float], Optional[str], List[str]]:
    """harmony_score over the named active set, or (None, name, reasons).

    The scored set is a set of IDENTITIES, not of supplied rows: each
    eligible (owner, idea_id) identity is counted and scored exactly
    once, however many times its record is repeated in the member
    list. Repeating one identity can therefore never manufacture the
    second member a harmony claim requires (Director 7166216146: a
    repeated solo idea published a harmony score + brightness for one
    identity). When the repeated records for one identity disagree on
    the scored data (title, properties, lifecycle state) the conflict
    cannot be resolved from canonical input, so the harmony is
    explicitly unavailable rather than computed over an arbitrary one
    of the conflicting records.
    """
    if neighborhood is None:
        return None, None, []
    if not isinstance(neighborhood, Mapping):
        return None, None, ["neighborhood_malformed"]
    name = neighborhood.get("name")
    members = neighborhood.get("members")
    if not (isinstance(name, str) and name.strip()) or not isinstance(members, list):
        return None, None, ["neighborhood_malformed"]
    adapters: List[_TokenSource] = []
    by_identity: Dict[Tuple[Optional[str], str], _TokenSource] = {}
    conflict = False
    for member in members:
        adapter = _member_adapter(member, owner)
        if adapter is None:
            continue
        identity = (owner, member.get("idea_id"))
        prior = by_identity.get(identity)  # type: ignore[arg-type]
        if prior is None:
            by_identity[identity] = adapter  # type: ignore[index]
            adapters.append(adapter)
        elif (prior.title != adapter.title
              or prior._props != adapter._props
              or prior.idea_state != adapter.idea_state):
            conflict = True
    measured["neighborhood_members_supplied"] = len(members)
    measured["neighborhood_members_scored"] = len(adapters)
    if conflict:
        return None, name, ["neighborhood_conflicting_duplicate"]
    if len(adapters) < 2:
        return None, name, ["neighborhood_below_two_scored"]
    return float(harmony_score(adapters)), name, []


def _spatial_cue(idea: Mapping, coords: Optional[Tuple[int, int, int]],
                 raw_position: Optional[Tuple[float, float]],
                 listener: Any) -> Tuple[Optional[Dict[str, Any]], Optional[str],
                                         Optional[Dict[str, Any]]]:
    """spatial_audio cue geometry for this idea from a listener context.

    Returns (cue, reason, parsed_listener). parsed_listener is the ONE
    validated representation of the listener — the same values the cue
    geometry consumed — so measured provenance never re-reads raw
    caller values (Director 7088588966: never invoke list() on
    unvalidated input; an invalid listener discloses pos/facing None).
    """
    if listener is None:
        return None, None, None
    parsed: Dict[str, Any] = {"pos": None, "facing": None}
    if not isinstance(listener, Mapping):
        return None, "invalid_listener", parsed
    pos = listener.get("pos")
    src: Optional[Tuple[float, float]] = None
    if isinstance(pos, Mapping):
        if _is_finite_number(pos.get("x")) and _is_finite_number(pos.get("y")):
            src = (float(pos.get("x")), float(pos.get("y")))
    elif isinstance(pos, (list, tuple)) and len(pos) == 2:
        if _is_finite_number(pos[0]) and _is_finite_number(pos[1]):
            src = (float(pos[0]), float(pos[1]))
    if src is None:
        return None, "invalid_listener", parsed
    parsed["pos"] = [src[0], src[1]]
    facing = listener.get("facing", "N")
    if not isinstance(facing, str):
        return None, "invalid_listener", parsed
    parsed["facing"] = facing
    if raw_position is not None:
        source = raw_position
    elif coords is not None:
        source = (float(coords[0]), float(coords[1]))
    else:
        return None, "coordinate_missing", parsed
    dist, bearing = _rel_polar(src, facing, source)
    if not math.isfinite(dist):
        # Both endpoints passed the finite checks individually, but
        # their separation can still lie outside the float range:
        # _rel_polar's subtraction overflows to inf, which a strict
        # JSON consumer cannot serialize. Suppress ONLY the spatial
        # cue with a typed reason; pitch and measured provenance are
        # unaffected (Director 7136695481).
        return None, "spatial_distance_unrepresentable", parsed
    pan = pan_from_bearing(bearing)
    cue = {
        "dist": round(dist, 2),
        "bearing": round(bearing, 1),
        "pan": round(pan, 3),
        "gain": round(gain_from_distance(dist), 3),
        "band": band_from_distance(dist),
        "ear": ear_from_pan(pan),
    }
    return cue, None, parsed


def _revision_of(idea: Mapping, reasons: List[str]) -> Any:
    rev = idea.get("source_revision")
    if isinstance(rev, str) or _is_int(rev):
        return rev
    reasons.append("source_revision_missing")
    return None


def sonify_idea(idea: Any, *, neighborhood: Any = None,
                listener: Any = None) -> SonicDescriptor:
    """Project one idea to its SonicDescriptor. Never raises on bad
    input, never mutates its inputs, never invents a value: anything
    unmeasured is disclosed as unavailable with a reason."""
    reasons: List[str] = []
    idea_id, owner, id_reasons = _identity(idea)
    reasons.extend(id_reasons)
    measured: Dict[str, Any] = {"coords": None, "coords_source": None,
                                "position": None, "origin_note": None}
    if not isinstance(idea, Mapping):
        return SonicDescriptor(
            kind="idea", idea_id=None, owner=None, source_revision=None,
            projection_version=PROJECTION_VERSION, status="unavailable",
            reasons=tuple(reasons), measured_inputs=measured)
    revision = _revision_of(idea, reasons)
    active, active_reason = _active_state(idea)
    if active_reason:
        reasons.append(active_reason)
    coords, coords_source, coords_reason, raw_position = _coords_of(idea)
    origin = idea.get("origin_note", 0)
    if not _is_int(origin):
        origin = None
        reasons.append("invalid_origin_note")
    if coords_reason:
        reasons.append(coords_reason)
    if raw_position is not None:
        measured["position"] = [raw_position[0], raw_position[1]]
    measured["origin_note"] = origin
    if coords is not None:
        measured["coords"] = [coords[0], coords[1], coords[2]]
        measured["coords_source"] = coords_source

    harmony, hood_name, hood_reasons = _score_neighborhood(
        idea, owner, neighborhood, measured)
    reasons.extend(hood_reasons)
    measured["neighborhood"] = hood_name

    if idea_id is None or owner is None or not active or coords is None or origin is None:
        # Silence is total: an unavailable idea asserts no pitch AND
        # no harmony, whatever was computable along the way.
        return SonicDescriptor(
            kind="idea", idea_id=idea_id, owner=owner,
            source_revision=revision, projection_version=PROJECTION_VERSION,
            status="unavailable", reasons=tuple(reasons),
            measured_inputs=measured)

    pitch_class, note_name, octave, frequency = _pitch(coords, int(origin))
    cue, cue_reason, parsed_listener = _spatial_cue(
        idea, coords, raw_position, listener)
    if cue_reason:
        reasons.append(cue_reason)
    if listener is not None:
        measured["listener"] = parsed_listener
    return SonicDescriptor(
        kind="idea", idea_id=idea_id, owner=owner, source_revision=revision,
        projection_version=PROJECTION_VERSION, status="supported",
        reasons=tuple(reasons), pitch_class=pitch_class,
        note_name=note_name, octave=octave, frequency_hz=frequency,
        harmony_score=harmony,
        harmony_status="available" if harmony is not None else "unavailable",
        neighborhood=hood_name,
        brightness=harmony,  # linear encoding choice, labelled in mapping
        member_ids=(idea_id,), pitch_classes=(pitch_class,),
        spatial=cue, measured_inputs=measured)


def sonify_relation(idea_a: Any, idea_b: Any) -> SonicDescriptor:
    """Project one pair of ideas: their measured set harmony and, when
    both coordinates are known, their chromatic interval. A relation
    has no single tone in S0; frequency_hz stays None. Cross-owner,
    inactive, same-idea or malformed pairs are silent."""
    reasons: List[str] = []
    id_a, owner_a, ra = _identity(idea_a)
    id_b, owner_b, rb = _identity(idea_b)
    reasons.extend(ra)
    reasons.extend(rb)
    member_ids = tuple(x for x in (id_a, id_b) if x is not None)
    pair_id = f"{id_a}~{id_b}" if id_a is not None and id_b is not None else None
    measured: Dict[str, Any] = {"set": "pair", "member_pitch_classes": None}

    def unavailable() -> SonicDescriptor:
        return SonicDescriptor(
            kind="relation", idea_id=pair_id, owner=owner_a,
            source_revision=None, projection_version=PROJECTION_VERSION,
            status="unavailable", reasons=tuple(reasons),
            member_ids=member_ids, measured_inputs=measured)

    if id_a is None or id_b is None or owner_a is None or owner_b is None:
        return unavailable()
    if id_a == id_b:
        reasons.append("same_idea_pair")
        return unavailable()
    if owner_a != owner_b:
        reasons.append("cross_owner_pair")
        return unavailable()
    for member in (idea_a, idea_b):
        active, active_reason = _active_state(member)  # type: ignore[arg-type]
        if not active:
            reasons.append(active_reason or "inactive")
            return unavailable()
    adapters: List[_TokenSource] = []
    for member in (idea_a, idea_b):
        adapter = _member_adapter(member, owner_a)
        if adapter is None:
            reasons.append("member_malformed")
            return unavailable()
        adapters.append(adapter)
    harmony = float(harmony_score(adapters))

    pitch_classes: List[int] = []
    interval: Optional[int] = None
    coords_pair: List[Optional[Tuple[int, int, int]]] = []
    for member in (idea_a, idea_b):
        coords, _, coords_reason, _ = _coords_of(member)  # type: ignore[arg-type]
        origin = member.get("origin_note", 0)  # type: ignore[union-attr]
        if coords is None or not _is_int(origin):
            coords_pair.append(None)
            if coords_reason:
                reasons.append(coords_reason)
        else:
            coords_pair.append(coords)
            pitch_classes.append(_pitch(coords, int(origin))[0])
    if coords_pair[0] is not None and coords_pair[1] is not None \
            and len(pitch_classes) == 2:
        interval = (pitch_classes[1] - pitch_classes[0]) % 12
        measured["member_pitch_classes"] = list(pitch_classes)
    rev_a = idea_a.get("source_revision")  # type: ignore[union-attr]
    rev_b = idea_b.get("source_revision")  # type: ignore[union-attr]
    revision = rev_a if rev_a == rev_b and (isinstance(rev_a, str) or _is_int(rev_a)) else None
    if revision is None:
        reasons.append("source_revision_mismatch_or_missing")
    return SonicDescriptor(
        kind="relation", idea_id=pair_id, owner=owner_a,
        source_revision=revision, projection_version=PROJECTION_VERSION,
        status="supported", reasons=tuple(reasons),
        harmony_score=harmony, harmony_status="available",
        brightness=harmony,  # linear encoding choice, labelled in mapping
        interval_semitones=interval, member_ids=(id_a, id_b),
        pitch_classes=tuple(pitch_classes), measured_inputs=measured)


def smoke() -> bool:
    """Tiny self-check (full acceptance lives in form/sonification_test.py)."""
    d = sonify_idea({"idea_id": "s", "owner": "o", "source_revision": "r",
                     "coords": {"h": 1, "v": 0, "f": 0}, "title": "x"})
    silent = sonify_idea({"idea_id": "s", "owner": "o"})
    return (d.status == "supported" and d.pitch_class == 7
            and d.note_name == "G" and silent.status == "unavailable")
