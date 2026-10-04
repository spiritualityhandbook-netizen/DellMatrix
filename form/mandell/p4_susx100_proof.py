#!/usr/bin/env python3
"""SUSX100 — 100-case stress suite for GDP-001 Phase 4 (Living Spatial Matrix).

100 rapid cases (<2s each, <5min total):
  t000-t019: placement determinism (20)
  t020-t039: bounded dynamics (20)
  t040-t054: convergence (15)
  t055-t069: adversarial (15)
  t070-t084: persistence (15)
  t085-t099: semantic isolation (15)

Pattern: rec(name, ok, detail); main() runs all; exit 0 iff all pass.
Unique owner P4SX<i:03d> per case; state cleaned after each.
"""
import math
import os
import shutil
import sys
import time

sys.path.insert(0, os.path.expanduser("~/workspace/dellmatrix-gdp-phase4"))
os.chdir(os.path.expanduser("~/workspace/dellmatrix-gdp-phase4"))

from form.persist import _STATE_DIR, _safe_owner  # noqa: E402
from form.dell_matrix.spatial_authority import (  # noqa: E402
    MAX_DISP_PER_TICK, PLANE_BOUND, MAX_SETTLE_TICKS,
    weather_modulation, SpatialAuthority, SpatialLoadError)

FAILURES = []
CASES = []


def rec(name, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name} | {detail}", flush=True)
    if not ok:
        FAILURES.append(name)


def _clean(owner):
    d = os.path.join(_STATE_DIR, f"ideas_{_safe_owner(owner)}")
    for suffix in ("",):
        shutil.rmtree(d + suffix, ignore_errors=True)
    for fn in (f"nursery_{_safe_owner(owner)}.json",
               f"program_{owner}.json"):
        try:
            os.remove(os.path.join(_STATE_DIR, fn))
        except OSError:
            pass
    try:
        from form.mandell.semantic_graph import (
            graph_path, graph_journal_path)
        for pth in (graph_path(owner), graph_journal_path(owner)):
            try:
                os.remove(pth)
            except OSError:
                pass
    except Exception:
        pass


def _prog(owner):
    from form.open import Program
    return Program(owner=owner)


def _pos(p):
    return {u: (p.cube.session.plane.units[u].x,
                p.cube.session.plane.units[u].y)
            for u in p.cube.session.plane.units}


def case(fn):
    CASES.append(fn)
    return fn


def _run_case(idx, fn):
    owner = f"P4SX{idx:03d}"
    try:
        fn(owner)
    except Exception as e:  # noqa: BLE001
        rec(fn.__name__, False, f"EXC {type(e).__name__}: {e}")
    finally:
        _clean(owner)


# ================================================================ placement
@case
def t000_det_2(owner):
    p1, p2 = _prog(owner + "a"), _prog(owner + "b")
    for p in (p1, p2):
        for j in range(2):
            p.place(f"d{j}", f"delta {j}")
    rec("t000", _pos(p1) == _pos(p2), "2 ideas identical")


@case
def t001_det_4(owner):
    p1, p2 = _prog(owner + "a"), _prog(owner + "b")
    for p in (p1, p2):
        for j in range(4):
            p.place(f"e{j}", f"echo {j} words")
    rec("t001", _pos(p1) == _pos(p2), "4 ideas identical")


@case
def t002_det_6(owner):
    p1, p2 = _prog(owner + "a"), _prog(owner + "b")
    for p in (p1, p2):
        for j in range(6):
            p.place(f"f{j}", f"foxtrot {j} content here")
    rec("t002", _pos(p1) == _pos(p2), "6 ideas identical")


@case
def t003_det_8(owner):
    p1, p2 = _prog(owner + "a"), _prog(owner + "b")
    for p in (p1, p2):
        for j in range(8):
            p.place(f"g{j}", f"golf {j}")
    rec("t003", _pos(p1) == _pos(p2), "8 ideas identical")


@case
def t004_det_12(owner):
    p1, p2 = _prog(owner + "a"), _prog(owner + "b")
    for p in (p1, p2):
        for j in range(12):
            p.place(f"h{j}", f"hotel {j} words words")
    rec("t004", _pos(p1) == _pos(p2), "12 ideas identical")


@case
def t005_exp_pos(owner):
    p = _prog(owner)
    p.place("x1", "explicit one", x=42.5, y=-17.25)
    x, y = _pos(p)["x1"]
    rec("t005", x == 42.5 and y == -17.25, f"got ({x},{y})")


@case
def t006_exp_neg(owner):
    p = _prog(owner)
    p.place("x2", "explicit two", x=-999.0, y=999.0)
    x, y = _pos(p)["x2"]
    rec("t006", x == -999.0 and y == 999.0, f"got ({x},{y})")


@case
def t007_exp_frac(owner):
    p = _prog(owner)
    p.place("x3", "explicit three", x=0.123456789, y=-0.987654321)
    x, y = _pos(p)["x3"]
    rec("t007", x == 0.123456789 and y == -0.987654321, "fractional exact")


@case
def t008_exp_large(owner):
    p = _prog(owner)
    p.place("x4", "explicit four", x=500.0, y=-500.0)
    x, y = _pos(p)["x4"]
    rec("t008", x == 500.0 and y == -500.0, "large exact")


@case
def t009_exp_origin(owner):
    p = _prog(owner)
    p.place("x5", "explicit five", x=0.0, y=0.0)
    x, y = _pos(p)["x5"]
    rec("t009", x == 0.0 and y == 0.0, "explicit origin honored")


@case
def t010_mix_1(owner):
    p1, p2 = _prog(owner + "a"), _prog(owner + "b")
    seq = [("m0", None), ("m1", (10, 20)), ("m2", None), ("m3", (-5, -5))]
    for p in (p1, p2):
        for uid, xy in seq:
            if xy:
                p.place(uid, f"mix {uid}", x=xy[0], y=xy[1])
            else:
                p.place(uid, f"mix {uid}")
    rec("t010", _pos(p1) == _pos(p2), "mixed deterministic")


@case
def t011_mix_2(owner):
    p1, p2 = _prog(owner + "a"), _prog(owner + "b")
    for p in (p1, p2):
        p.place("n0", "n0", x=1, y=1)
        p.place("n1", "n1")
        p.place("n2", "n2", x=2, y=2)
        p.place("n3", "n3")
    rec("t011", _pos(p1) == _pos(p2), "alternating deterministic")


@case
def t012_mix_3(owner):
    p1, p2 = _prog(owner + "a"), _prog(owner + "b")
    for p in (p1, p2):
        for j in range(5):
            if j % 2:
                p.place(f"p{j}", f"p{j}", x=j * 10.0, y=-j * 10.0)
            else:
                p.place(f"p{j}", f"p{j}")
    rec("t012", _pos(p1) == _pos(p2), "5 mixed deterministic")


@case
def t013_mix_4(owner):
    p1, p2 = _prog(owner + "a"), _prog(owner + "b")
    for p in (p1, p2):
        p.place("q0", "q0")
        p.place("q1", "q1", x=100, y=100)
        p.place("q2", "q2")
    rec("t013", _pos(p1) == _pos(p2), "3 mixed deterministic")


@case
def t014_mix_5(owner):
    p1, p2 = _prog(owner + "a"), _prog(owner + "b")
    for p in (p1, p2):
        p.place("r0", "r0", x=-50, y=25)
        p.place("r1", "r1")
        p.place("r2", "r2")
        p.place("r3", "r3", x=75, y=-75)
    rec("t014", _pos(p1) == _pos(p2), "4 mixed deterministic")


@case
def t015_no_origin(owner):
    p = _prog(owner)
    for j in range(10):
        p.place(f"s{j}", f"sierra {j}")
    at_origin = [u for u, (x, y) in _pos(p).items()
                 if abs(x) < 1e-9 and abs(y) < 1e-9]
    # welcome unit is allowed at origin; placed ideas are not
    bad = [u for u in at_origin if u.startswith("s")]
    rec("t015", not bad, f"implicit at origin: {bad}")


@case
def t016_finite(owner):
    p = _prog(owner)
    for j in range(10):
        p.place(f"t{j}", f"tango {j}")
    ok = all(math.isfinite(x) and math.isfinite(y)
             for x, y in _pos(p).values())
    rec("t016", ok, "all finite")


@case
def t017_bounded(owner):
    p = _prog(owner)
    for j in range(10):
        p.place(f"u{j}", f"uniform {j}")
    ok = all(abs(x) <= PLANE_BOUND and abs(y) <= PLANE_BOUND
             for x, y in _pos(p).values())
    rec("t017", ok, "within bounds")


@case
def t018_explained(owner):
    p = _prog(owner)
    for j in range(5):
        p.place(f"v{j}", f"victor {j}")
    ok = all(p.spatial_explain(f"v{j}")["present"] for j in range(5))
    rec("t018", ok, "all explained")


@case
def t019_unique(owner):
    p = _prog(owner)
    for j in range(8):
        p.place(f"w{j}", f"whiskey {j}")
    pts = list(_pos(p).values())
    uniq = len({(round(x, 9), round(y, 9)) for x, y in pts})
    rec("t019", uniq == len(pts), f"{uniq}/{len(pts)} unique")


# ================================================================ dynamics
def _bound_for(mode, temp=1.0):
    mod = weather_modulation(mode)
    return (MAX_DISP_PER_TICK * mod["disp_mult"] * temp
            + mod["jitter"] * MAX_DISP_PER_TICK + 1e-9)


@case
def t020_clear_1(owner):
    p = _prog(owner)
    for j in range(5):
        p.place(f"c{j}", f"clear {j}")
    p.set_weather("clear")
    r = p.force_tick()["spatial"]
    rec("t020", r["max_displacement"] <= _bound_for("clear"),
        f"max_disp={r['max_displacement']:.4f}")


@case
def t021_rain_1(owner):
    p = _prog(owner)
    for j in range(5):
        p.place(f"c{j}", f"rain {j}")
    p.set_weather("rain")
    r = p.force_tick()["spatial"]
    rec("t021", r["max_displacement"] <= _bound_for("rain"),
        f"max_disp={r['max_displacement']:.4f}")


@case
def t022_fog_1(owner):
    p = _prog(owner)
    for j in range(5):
        p.place(f"c{j}", f"fog {j}")
    p.set_weather("fog")
    r = p.force_tick()["spatial"]
    rec("t022", r["max_displacement"] <= _bound_for("fog"),
        f"max_disp={r['max_displacement']:.4f}")


@case
def t023_storm_1(owner):
    p = _prog(owner)
    for j in range(5):
        p.place(f"c{j}", f"storm {j}")
    p.set_weather("storm")
    r = p.force_tick()["spatial"]
    rec("t023", r["max_displacement"] <= _bound_for("storm"),
        f"max_disp={r['max_displacement']:.4f}")


@case
def t024_clear_5(owner):
    p = _prog(owner)
    for j in range(5):
        p.place(f"c{j}", f"clear5 {j}")
    p.set_weather("clear")
    ok = True
    for _ in range(5):
        r = p.force_tick()["spatial"]
        if r["max_displacement"] > _bound_for("clear"):
            ok = False
    rec("t024", ok, "5 ticks bounded")


@case
def t025_rain_5(owner):
    p = _prog(owner)
    for j in range(5):
        p.place(f"c{j}", f"rain5 {j}")
    p.set_weather("rain")
    ok = True
    for _ in range(5):
        r = p.force_tick()["spatial"]
        if r["max_displacement"] > _bound_for("rain"):
            ok = False
    rec("t025", ok, "5 ticks bounded")


@case
def t026_fog_5(owner):
    p = _prog(owner)
    for j in range(5):
        p.place(f"c{j}", f"fog5 {j}")
    p.set_weather("fog")
    ok = True
    for _ in range(5):
        r = p.force_tick()["spatial"]
        if r["max_displacement"] > _bound_for("fog"):
            ok = False
    rec("t026", ok, "5 ticks bounded")


@case
def t027_storm_5(owner):
    p = _prog(owner)
    for j in range(5):
        p.place(f"c{j}", f"storm5 {j}")
    p.set_weather("storm")
    ok = True
    for _ in range(5):
        r = p.force_tick()["spatial"]
        if r["max_displacement"] > _bound_for("storm"):
            ok = False
    rec("t027", ok, "5 ticks bounded")


@case
def t028_mod_clear(owner):
    m = weather_modulation("clear")
    rec("t028", m["disp_mult"] == 1.0 and m["friction"] == 0.90
        and m["jitter"] == 0.0, f"{m}")


@case
def t029_mod_rain(owner):
    m = weather_modulation("rain")
    rec("t029", m["disp_mult"] == 1.25 and m["friction"] == 0.95
        and m["jitter"] == 0.0, f"{m}")


@case
def t030_mod_fog(owner):
    m = weather_modulation("fog")
    rec("t030", m["disp_mult"] == 0.8 and m["friction"] == 0.90
        and m["attract_radius_mult"] == 0.6, f"{m}")


@case
def t031_mod_storm(owner):
    m = weather_modulation("storm")
    rec("t031", m["disp_mult"] == 1.0 and m["jitter"] == 0.1, f"{m}")


@case
def t032_10_clear(owner):
    p = _prog(owner)
    for j in range(10):
        p.place(f"c{j}", f"c10 {j}")
    p.set_weather("clear")
    ok = all(p.force_tick()["spatial"]["max_displacement"]
             <= _bound_for("clear") for _ in range(3))
    rec("t032", ok, "10 ideas bounded")


@case
def t033_10_storm(owner):
    p = _prog(owner)
    for j in range(10):
        p.place(f"c{j}", f"s10 {j}")
    p.set_weather("storm")
    ok = all(p.force_tick()["spatial"]["max_displacement"]
             <= _bound_for("storm") for _ in range(3))
    rec("t033", ok, "10 ideas storm bounded")


@case
def t034_10_rain(owner):
    p = _prog(owner)
    for j in range(10):
        p.place(f"c{j}", f"r10 {j}")
    p.set_weather("rain")
    ok = all(p.force_tick()["spatial"]["max_displacement"]
             <= _bound_for("rain") for _ in range(3))
    rec("t034", ok, "10 ideas rain bounded")


@case
def t035_10_fog(owner):
    p = _prog(owner)
    for j in range(10):
        p.place(f"c{j}", f"f10 {j}")
    p.set_weather("fog")
    ok = all(p.force_tick()["spatial"]["max_displacement"]
             <= _bound_for("fog") for _ in range(3))
    rec("t035", ok, "10 ideas fog bounded")


@case
def t036_storm_jitter(owner):
    p = _prog(owner)
    p.place("j0", "jitter zero")
    p.set_weather("storm")
    # single idea at origin-ish: jitter should be <= 0.1*cap
    r = p.force_tick()["spatial"]
    rec("t036", r["max_displacement"] <= 0.1 * MAX_DISP_PER_TICK + 1.0 + 1e-9,
        f"max_disp={r['max_displacement']:.4f}")


@case
def t037_fog_reduced(owner):
    p1, p2 = _prog(owner + "a"), _prog(owner + "b")
    for p in (p1, p2):
        for j in range(4):
            p.place(f"f{j}", f"fogcmp {j}")
    p1.set_weather("fog")
    p2.set_weather("clear")
    d1 = p1.force_tick()["spatial"]["max_displacement"]
    d2 = p2.force_tick()["spatial"]["max_displacement"]
    rec("t037", d1 <= d2 + 1e-9, f"fog={d1:.4f} clear={d2:.4f}")


@case
def t038_rain_amplified(owner):
    m = weather_modulation("rain")
    rec("t038", m["disp_mult"] > weather_modulation("clear")["disp_mult"],
        "rain > clear")


@case
def t039_temp_cools(owner):
    p = _prog(owner)
    for j in range(3):
        p.place(f"t{j}", f"temp {j}")
    t0 = p.spatial.temperature
    p.force_tick()
    rec("t039", p.spatial.temperature < t0, f"{t0:.4f}->{p.spatial.temperature:.4f}")


# ================================================================ convergence
@case
def t040_conv_2(owner):
    p = _prog(owner)
    for j in range(2):
        p.place(f"k{j}", f"konv {j}")
    s = p.spatial_settle()
    rec("t040", (s["converged"] or s["honestly_non_convergent"])
        and s["ticks_run"] <= MAX_SETTLE_TICKS, f"ticks={s['ticks_run']}")


@case
def t041_conv_3(owner):
    p = _prog(owner)
    for j in range(3):
        p.place(f"k{j}", f"konv {j}")
    s = p.spatial_settle()
    rec("t041", (s["converged"] or s["honestly_non_convergent"])
        and s["ticks_run"] <= MAX_SETTLE_TICKS, f"ticks={s['ticks_run']}")


@case
def t042_conv_4(owner):
    p = _prog(owner)
    for j in range(4):
        p.place(f"k{j}", f"konv {j}")
    s = p.spatial_settle()
    rec("t042", (s["converged"] or s["honestly_non_convergent"])
        and s["ticks_run"] <= MAX_SETTLE_TICKS, f"ticks={s['ticks_run']}")


@case
def t043_conv_5(owner):
    p = _prog(owner)
    for j in range(5):
        p.place(f"k{j}", f"konv {j}")
    s = p.spatial_settle()
    rec("t043", (s["converged"] or s["honestly_non_convergent"])
        and s["ticks_run"] <= MAX_SETTLE_TICKS, f"ticks={s['ticks_run']}")


@case
def t044_conv_6(owner):
    p = _prog(owner)
    for j in range(6):
        p.place(f"k{j}", f"konv {j}")
    s = p.spatial_settle()
    rec("t044", (s["converged"] or s["honestly_non_convergent"])
        and s["ticks_run"] <= MAX_SETTLE_TICKS, f"ticks={s['ticks_run']}")


@case
def t045_conv_7(owner):
    p = _prog(owner)
    for j in range(7):
        p.place(f"k{j}", f"konv {j}")
    s = p.spatial_settle()
    rec("t045", (s["converged"] or s["honestly_non_convergent"])
        and s["ticks_run"] <= MAX_SETTLE_TICKS, f"ticks={s['ticks_run']}")


@case
def t046_conv_8(owner):
    p = _prog(owner)
    for j in range(8):
        p.place(f"k{j}", f"konv {j}")
    s = p.spatial_settle()
    rec("t046", (s["converged"] or s["honestly_non_convergent"])
        and s["ticks_run"] <= MAX_SETTLE_TICKS, f"ticks={s['ticks_run']}")


@case
def t047_conv_9(owner):
    p = _prog(owner)
    for j in range(9):
        p.place(f"k{j}", f"konv {j}")
    s = p.spatial_settle()
    rec("t047", (s["converged"] or s["honestly_non_convergent"])
        and s["ticks_run"] <= MAX_SETTLE_TICKS, f"ticks={s['ticks_run']}")


@case
def t048_conv_10(owner):
    p = _prog(owner)
    for j in range(10):
        p.place(f"k{j}", f"konv {j}")
    s = p.spatial_settle()
    rec("t048", (s["converged"] or s["honestly_non_convergent"])
        and s["ticks_run"] <= MAX_SETTLE_TICKS, f"ticks={s['ticks_run']}")


@case
def t049_conv_spread(owner):
    p = _prog(owner)
    for j in range(4):
        p.place(f"sp{j}", f"spread {j}", x=j * 20.0, y=-j * 20.0)
    s = p.spatial_settle()
    rec("t049", s["converged"] or s["honestly_non_convergent"],
        f"converged={s['converged']}")


@case
def t050_conv_tight(owner):
    p = _prog(owner)
    for j in range(4):
        p.place(f"ti{j}", f"tight {j}", x=5.0 + j * 0.5, y=5.0)
    s = p.spatial_settle()
    rec("t050", s["converged"] or s["honestly_non_convergent"],
        f"converged={s['converged']}")


@case
def t051_conv_line(owner):
    p = _prog(owner)
    for j in range(5):
        p.place(f"ln{j}", f"line {j}", x=j * 3.0, y=0.0)
    s = p.spatial_settle()
    rec("t051", s["converged"] or s["honestly_non_convergent"],
        f"converged={s['converged']}")


@case
def t052_conv_empty(owner):
    p = _prog(owner)
    # remove welcome to test truly empty
    p.cube.session.plane.units.clear()
    s = p.spatial_settle()
    rec("t052", s["state"] in ("empty", "converged") or s["converged"],
        f"state={s.get('state')}")


@case
def t053_conv_single(owner):
    p = _prog(owner)
    p.cube.session.plane.units.clear()
    p.place("solo", "solo idea")
    s = p.spatial_settle()
    rec("t053", s["converged"] or s["honestly_non_convergent"],
        f"ticks={s['ticks_run']}")


@case
def t054_conv_coincident(owner):
    p = _prog(owner)
    p.place("cc0", "coincident zero", x=7.0, y=7.0)
    p.place("cc1", "coincident one", x=7.0, y=7.0)
    s = p.spatial_settle()
    x0, y0 = _pos(p)["cc0"]
    x1, y1 = _pos(p)["cc1"]
    d = math.hypot(x0 - x1, y0 - y1)
    rec("t054", d > 0.1, f"separated to {d:.3f}")


# ================================================================ adversarial
@case
def t055_nan_x(owner):
    p = _prog(owner)
    p.place("a0", "adv zero")
    p.place("a1", "adv one")
    p.cube.session.plane.units["a0"].x = float("nan")
    try:
        for _ in range(3):
            p.force_tick()
        ok = True
    except Exception:
        ok = False
    u1 = p.cube.session.plane.units["a1"]
    rec("t055", ok and math.isfinite(u1.x) and math.isfinite(u1.y),
        "no raise, no propagation")


@case
def t056_inf_y(owner):
    p = _prog(owner)
    p.place("b0", "adv bzero")
    p.place("b1", "adv bone")
    p.cube.session.plane.units["b0"].y = float("inf")
    try:
        for _ in range(3):
            p.force_tick()
        ok = True
    except Exception:
        ok = False
    u1 = p.cube.session.plane.units["b1"]
    rec("t056", ok and math.isfinite(u1.x) and math.isfinite(u1.y),
        "inf contained")


@case
def t057_ninf(owner):
    p = _prog(owner)
    p.place("c0", "adv czero")
    p.cube.session.plane.units["c0"].x = float("-inf")
    try:
        p.force_tick()
        ok = True
    except Exception:
        ok = False
    rec("t057", ok, "-inf contained")


@case
def t058_coinc_2(owner):
    p1, p2 = _prog(owner + "a"), _prog(owner + "b")
    for p in (p1, p2):
        p.place("d0", "coinc dzero", x=5.0, y=5.0)
        p.place("d1", "coinc done", x=5.0, y=5.0)
        p.force_tick()
    rec("t058", _pos(p1) == _pos(p2), "coincidence deterministic")


@case
def t059_coinc_5(owner):
    p = _prog(owner)
    for j in range(5):
        p.place(f"e{j}", f"coinc5 {j}", x=3.0, y=3.0)
    for _ in range(5):
        p.force_tick()
    pts = list(_pos(p).values())
    # exclude welcome
    pts = [pt for uid, pt in _pos(p).items() if uid.startswith("e")]
    uniq = len({(round(x, 6), round(y, 6)) for x, y in pts})
    rec("t059", uniq == 5, f"{uniq}/5 unique")


@case
def t060_coinc_10(owner):
    p = _prog(owner)
    for j in range(10):
        p.place(f"f{j}", f"coinc10 {j}", x=1.0, y=1.0)
    for _ in range(10):
        p.force_tick()
    pts = [pt for uid, pt in _pos(p).items() if uid.startswith("f")]
    ok = all(math.isfinite(x) and math.isfinite(y) for x, y in pts)
    rec("t060", ok, "10 coincident finite")


@case
def t061_crowd_30(owner):
    p = _prog(owner)
    for j in range(30):
        p.place(f"g{j}", f"crowd {j}")
    pts = [pt for uid, pt in _pos(p).items() if uid.startswith("g")]
    ok = all(math.isfinite(x) and math.isfinite(y) for x, y in pts)
    at_o = [1 for x, y in pts if abs(x) < 1e-9 and abs(y) < 1e-9]
    rec("t061", ok and not at_o, f"30 placed, at_origin={len(at_o)}")


@case
def t062_extreme_pos(owner):
    p = _prog(owner)
    p.place("h0", "extreme", x=1e10, y=1e10)
    x, y = _pos(p)["h0"]
    rec("t062", abs(x) <= PLANE_BOUND and abs(y) <= PLANE_BOUND,
        f"clamped to ({x},{y})")


@case
def t063_extreme_neg(owner):
    p = _prog(owner)
    p.place("h1", "extreme neg", x=-1e10, y=-1e10)
    x, y = _pos(p)["h1"]
    rec("t063", abs(x) <= PLANE_BOUND and abs(y) <= PLANE_BOUND,
        f"clamped to ({x},{y})")


@case
def t064_empty_tick(owner):
    p = _prog(owner)
    p.cube.session.plane.units.clear()
    try:
        r = p.force_tick()["spatial"]
        ok = True
    except Exception:
        ok = False
    rec("t064", ok, "empty tick clean")


@case
def t065_bad_weather(owner):
    m = weather_modulation("hurricane")
    c = weather_modulation("clear")
    rec("t065", m == c, "unknown -> clear params")


@case
def t066_exp_origin2(owner):
    p = _prog(owner)
    p.place("i0", "origin explicit", x=0.0, y=0.0)
    e = p.spatial_explain("i0")
    rec("t066", e["present"] and e["placement"]["cause"] == "explicit",
        f"cause={e['placement']['cause']}")


@case
def t067_faded(owner):
    from form.dell_matrix.nursery import Proposal
    from form.dell_matrix import canonical_lifecycle
    p = _prog(owner)
    p.place("j0", "faded adv")
    p.place("j1", "active adv")
    p.nursery.proposals["j0"] = Proposal(
        id="j0", label="j0", words="w", kind="new", lifecycle_state="faded")
    p.nursery.save()
    assert not canonical_lifecycle.is_active(p, "j0")
    b0 = _pos(p)["j0"]
    for _ in range(5):
        p.force_tick()
    a0 = _pos(p)["j0"]
    rec("t067", b0 == a0, "faded frozen")


@case
def t068_interleave(owner):
    p = _prog(owner)
    try:
        for j in range(10):
            p.place(f"k{j}", f"inter {j}")
            p.force_tick()
        ok = True
    except Exception:
        ok = False
    n = len([u for u in p.cube.session.plane.units if u.startswith("k")])
    rec("t068", ok and n == 10, f"10 placed across ticks")


@case
def t069_nan_place(owner):
    p = _prog(owner)
    try:
        p.place("l0", "nan place", x=float("nan"), y=0.0)
        raised = False
    except (ValueError, SpatialLoadError):
        raised = True
    rec("t069", raised, "explicit NaN rejected")


# ================================================================ persistence
@case
def t070_rt_3(owner):
    from form.persist_rest import save, load
    p = _prog(owner)
    for j in range(3):
        p.place(f"m{j}", f"rt {j}")
    p.force_tick()
    before = (_pos(p), p.spatial.tick_count, p.spatial.temperature)
    save(p)
    q = load(owner)
    after = (_pos(q), q.spatial.tick_count, q.spatial.temperature)
    rec("t070", before[0] == after[0] and before[1] == after[1]
        and abs(before[2] - after[2]) < 1e-12, "round-trip identical")


@case
def t071_rt_8(owner):
    from form.persist_rest import save, load
    p = _prog(owner)
    for j in range(8):
        p.place(f"m{j}", f"rt8 {j}")
    for _ in range(3):
        p.force_tick()
    before = _pos(p)
    save(p)
    q = load(owner)
    rec("t071", before == _pos(q), "8 ideas round-trip")


@case
def t072_rt_15(owner):
    from form.persist_rest import save, load
    p = _prog(owner)
    for j in range(15):
        p.place(f"m{j}", f"rt15 {j}")
    p.force_tick()
    before = _pos(p)
    save(p)
    q = load(owner)
    rec("t072", before == _pos(q), "15 ideas round-trip")


@case
def t073_vel_saved(owner):
    from form.persist_rest import save, load
    p = _prog(owner)
    for j in range(3):
        p.place(f"n{j}", f"vel {j}")
    p.force_tick()
    nv = len(p.spatial.velocities)
    save(p)
    q = load(owner)
    rec("t073", len(q.spatial.velocities) == nv and nv > 0,
        f"velocities={nv}")


@case
def t074_expl_saved(owner):
    from form.persist_rest import save, load
    p = _prog(owner)
    p.place("o0", "expl zero")
    save(p)
    q = load(owner)
    rec("t074", q.spatial_explain("o0")["present"], "explanation persisted")


@case
def t075_bad_version(owner):
    try:
        SpatialAuthority.from_dict({"version": 999})
        ok = False
    except SpatialLoadError:
        ok = True
    rec("t075", ok, "bad version raises")


@case
def t076_nan_vel(owner):
    try:
        SpatialAuthority.from_dict({
            "version": 1, "tick_count": 0, "temperature": 1.0,
            "velocities": {"a": [float("nan"), 0.0]},
            "placements": {}, "rng_seed": 42, "rng_state": None})
        ok = False
    except SpatialLoadError:
        ok = True
    rec("t076", ok, "NaN velocity raises")


@case
def t077_nondict(owner):
    try:
        SpatialAuthority.from_dict([1, 2, 3])
        ok = False
    except SpatialLoadError:
        ok = True
    rec("t077", ok, "non-dict raises")


@case
def t078_none_fresh(owner):
    s = SpatialAuthority.from_dict(None)
    rec("t078", s.tick_count == 0 and s.temperature == 1.0, "None -> fresh")


@case
def t079_legacy(owner):
    from form.persist_rest import save, load
    import json
    p = _prog(owner)
    p.place("p0", "legacy zero")
    save(p)
    fp = os.path.join(_STATE_DIR, f"program_{owner}.json")
    d = json.load(open(fp))
    d.pop("spatial", None)
    json.dump(d, open(fp, "w"))
    q = load(owner)
    rec("t079", "p0" in q.cube.session.plane.units
        and q.spatial.tick_count == 0, "legacy loads fresh")


@case
def t080_storm_det_rt(owner):
    from form.persist_rest import save, load
    p = _prog(owner)
    for j in range(4):
        p.place(f"q{j}", f"stormrt {j}")
    p.set_weather("storm")
    for _ in range(3):
        p.force_tick()
    save(p)
    # continue without save in a twin
    p2 = _prog(owner + "twin")
    for j in range(4):
        p2.place(f"q{j}", f"stormrt {j}")
    p2.set_weather("storm")
    for _ in range(3):
        p2.force_tick()
    q = load(owner)
    q.force_tick()
    p2.force_tick()
    rec("t080", _pos(q) == _pos(p2), "post-load storm deterministic")


@case
def t081_rng_exact(owner):
    from form.persist_rest import save, load
    p = _prog(owner)
    for j in range(3):
        p.place(f"r{j}", f"rng {j}")
    p.set_weather("storm")
    p.force_tick()
    save(p)
    q1, q2 = load(owner), load(owner)
    q1.force_tick()
    q2.force_tick()
    rec("t081", _pos(q1) == _pos(q2), "twin loads identical")


@case
def t082_midtick(owner):
    from form.persist_rest import save, load
    p = _prog(owner)
    for j in range(4):
        p.place(f"s{j}", f"midtick {j}")
    p.force_tick()
    save(p)  # save between ticks
    q = load(owner)
    try:
        q.force_tick()
        ok = True
    except Exception:
        ok = False
    rec("t082", ok and q.spatial.tick_count == 2, "mid-tick save coherent")


@case
def t083_corrupt(owner):
    from form.persist_rest import save, load
    p = _prog(owner)
    p.place("t0", "corrupt zero")
    save(p)
    fp = os.path.join(_STATE_DIR, f"program_{owner}.json")
    open(fp, "w").write("{not valid json")
    try:
        load(owner)
        ok = False
    except Exception:
        ok = True
    rec("t083", ok, "corrupt file raises")


@case
def t084_tick_preserved(owner):
    from form.persist_rest import save, load
    p = _prog(owner)
    p.place("u0", "tickpres zero")
    for _ in range(4):
        p.force_tick()
    save(p)
    q = load(owner)
    rec("t084", q.spatial.tick_count == 4, f"tick={q.spatial.tick_count}")


# ================================================================ semantic isolation
def _sem_snap(p, ids):
    from form.dell_matrix import canonical_lifecycle
    from form.mandell.semantic_graph import SemanticGraph
    from form.dell_matrix.graph_harmony import graph_neighbor_ids
    g = SemanticGraph.load(p.owner)
    try:
        nbrs = {i: sorted(graph_neighbor_ids(g, i)) for i in ids}
    except Exception:
        nbrs = {}
    return {
        "lc": {i: canonical_lifecycle.resolve_lifecycle(p, i) for i in ids},
        "nbrs": nbrs,
    }


@case
def t085_iso_clear(owner):
    p = _prog(owner)
    ids = [f"v{j}" for j in range(4)]
    for uid in ids:
        p.place(uid, f"iso {uid}")
    s0 = _sem_snap(p, ids)
    p.set_weather("clear")
    for _ in range(10):
        p.force_tick()
    rec("t085", _sem_snap(p, ids) == s0, "clear: semantic unchanged")


@case
def t086_iso_rain(owner):
    p = _prog(owner)
    ids = [f"v{j}" for j in range(4)]
    for uid in ids:
        p.place(uid, f"iso {uid}")
    s0 = _sem_snap(p, ids)
    p.set_weather("rain")
    for _ in range(10):
        p.force_tick()
    rec("t086", _sem_snap(p, ids) == s0, "rain: semantic unchanged")


@case
def t087_iso_fog(owner):
    p = _prog(owner)
    ids = [f"v{j}" for j in range(4)]
    for uid in ids:
        p.place(uid, f"iso {uid}")
    s0 = _sem_snap(p, ids)
    p.set_weather("fog")
    for _ in range(10):
        p.force_tick()
    rec("t087", _sem_snap(p, ids) == s0, "fog: semantic unchanged")


@case
def t088_iso_storm(owner):
    p = _prog(owner)
    ids = [f"v{j}" for j in range(4)]
    for uid in ids:
        p.place(uid, f"iso {uid}")
    s0 = _sem_snap(p, ids)
    p.set_weather("storm")
    for _ in range(10):
        p.force_tick()
    rec("t088", _sem_snap(p, ids) == s0, "storm: semantic unchanged")


@case
def t089_edge_clear(owner):
    from form.mandell.semantic_graph import SemanticGraph, RelationshipType
    from form.mandell.idea import Idea, Provenance, ProvenanceSource
    from form.mandell.idea_persist import save_idea
    p = _prog(owner)
    ids = ["w0", "w1"]
    for uid in ids:
        p.place(uid, f"edge {uid}")
        save_idea(Idea(idea_id=uid, title=uid), owner)
    g = SemanticGraph.load(owner)
    g.add_relationship(RelationshipType.RELATED_TO, "w0", "w1",
                       Provenance(source=ProvenanceSource.SYSTEM,
                                  activity="sx", agent="sx"), cause="sx")
    s0 = _sem_snap(p, ids)
    p.set_weather("clear")
    for _ in range(10):
        p.force_tick()
    rec("t089", _sem_snap(p, ids) == s0, "edges survive clear")


@case
def t090_edge_storm(owner):
    from form.mandell.semantic_graph import SemanticGraph, RelationshipType
    from form.mandell.idea import Idea, Provenance, ProvenanceSource
    from form.mandell.idea_persist import save_idea
    p = _prog(owner)
    ids = ["w0", "w1"]
    for uid in ids:
        p.place(uid, f"edge {uid}")
        save_idea(Idea(idea_id=uid, title=uid), owner)
    g = SemanticGraph.load(owner)
    g.add_relationship(RelationshipType.RELATED_TO, "w0", "w1",
                       Provenance(source=ProvenanceSource.SYSTEM,
                                  activity="sx", agent="sx"), cause="sx")
    s0 = _sem_snap(p, ids)
    p.set_weather("storm")
    for _ in range(10):
        p.force_tick()
    rec("t090", _sem_snap(p, ids) == s0, "edges survive storm")


@case
def t091_no_new_edges(owner):
    from form.mandell.semantic_graph import SemanticGraph
    from form.dell_matrix.graph_harmony import graph_neighbor_ids
    p = _prog(owner)
    ids = [f"x{j}" for j in range(5)]
    for uid in ids:
        p.place(uid, f"noedge {uid}")
    for _ in range(15):
        p.force_tick()
    g = SemanticGraph.load(owner)
    total = sum(len(graph_neighbor_ids(g, i)) for i in ids)
    rec("t091", total == 0, f"movement created {total} edges")


@case
def t092_faded_lc(owner):
    from form.dell_matrix.nursery import Proposal
    from form.dell_matrix import canonical_lifecycle
    p = _prog(owner)
    p.place("y0", "faded iso")
    p.nursery.proposals["y0"] = Proposal(
        id="y0", label="y0", words="w", kind="new", lifecycle_state="faded")
    p.nursery.save()
    lc0 = canonical_lifecycle.resolve_lifecycle(p, "y0")
    for _ in range(10):
        p.force_tick()
    rec("t092", canonical_lifecycle.resolve_lifecycle(p, "y0") == lc0,
        f"lifecycle={lc0}")


@case
def t093_props_stable(owner):
    p = _prog(owner)
    p.place("z0", "props zero", words="alpha beta")
    u = p.cube.session.plane.units["z0"]
    label0, words0 = u.label, getattr(u, "words", "")
    for _ in range(10):
        p.force_tick()
    u = p.cube.session.plane.units["z0"]
    rec("t093", u.label == label0 and getattr(u, "words", "") == words0,
        "label/words unchanged")


@case
def t094_scores_stable(owner):
    p = _prog(owner)
    for j in range(3):
        p.place(f"aa{j}", f"scores {j}")
    s0 = dict(p.scores())
    for _ in range(10):
        p.force_tick()
    rec("t094", dict(p.scores()) == s0, "scores unchanged by movement")


@case
def t095_multi_weather(owner):
    p = _prog(owner)
    ids = [f"ab{j}" for j in range(4)]
    for uid in ids:
        p.place(uid, f"multi {uid}")
    s0 = _sem_snap(p, ids)
    for mode in ("clear", "rain", "fog", "storm"):
        p.set_weather(mode)
        for _ in range(5):
            p.force_tick()
    rec("t095", _sem_snap(p, ids) == s0, "all modes: semantic unchanged")


@case
def t096_settle_iso(owner):
    p = _prog(owner)
    ids = [f"ac{j}" for j in range(5)]
    for uid in ids:
        p.place(uid, f"settleiso {uid}")
    s0 = _sem_snap(p, ids)
    p.spatial_settle()
    rec("t096", _sem_snap(p, ids) == s0, "settle: semantic unchanged")


@case
def t097_faded_no_attract(owner):
    from form.dell_matrix.nursery import Proposal
    p1 = _prog(owner + "a")
    p2 = _prog(owner + "b")
    for p in (p1, p2):
        p.place("ad0", "anchor", x=0.0, y=20.0)
        p.place("ad1", "mover", x=0.0, y=0.0)
    # p1: ad0 faded; p2: ad0 active. Compare ad1 displacement.
    p1.nursery.proposals["ad0"] = Proposal(
        id="ad0", label="ad0", words="w", kind="new", lifecycle_state="faded")
    p1.nursery.save()
    d1 = []
    d2 = []
    for _ in range(5):
        b1 = _pos(p1)["ad1"]
        p1.force_tick()
        a1 = _pos(p1)["ad1"]
        d1.append(math.hypot(a1[0] - b1[0], a1[1] - b1[1]))
        b2 = _pos(p2)["ad1"]
        p2.force_tick()
        a2 = _pos(p2)["ad1"]
        d2.append(math.hypot(a2[0] - b2[0], a2[1] - b2[1]))
    # faded well should not pull: p1's mover moves <= p2's (no well attraction)
    rec("t097", sum(d1) <= sum(d2) + 1e-9,
        f"faded={sum(d1):.4f} active={sum(d2):.4f}")


@case
def t098_lattice_not_truth(owner):
    p = _prog(owner)
    for j in range(4):
        p.place(f"ae{j}", f"lat {j}")
    # lattice cells are derived; moving via authority then rebuilding
    # must keep every unit represented
    for _ in range(3):
        p.force_tick()
    p.lattice.rebuild_from_plane(p.cube.session.plane)
    contents = {c.content for c in p.lattice.cells.values()}
    units = set(p.cube.session.plane.units)
    rec("t098", units <= contents, "lattice covers all units")


@case
def t099_full_iso(owner):
    from form.mandell.semantic_graph import SemanticGraph, RelationshipType
    from form.mandell.idea import Idea, Provenance, ProvenanceSource
    from form.mandell.idea_persist import save_idea
    p = _prog(owner)
    ids = [f"af{j}" for j in range(6)]
    for uid in ids:
        p.place(uid, f"full {uid}")
        save_idea(Idea(idea_id=uid, title=uid), owner)
    g = SemanticGraph.load(owner)
    g.add_relationship(RelationshipType.RELATED_TO, "af0", "af1",
                       Provenance(source=ProvenanceSource.SYSTEM,
                                  activity="sx", agent="sx"), cause="sx")
    s0 = _sem_snap(p, ids)
    p.set_weather("storm")
    p.spatial_settle(50)
    p.set_weather("clear")
    for _ in range(5):
        p.force_tick()
    rec("t099", _sem_snap(p, ids) == s0, "full circuit: semantic unchanged")


def main():
    t0 = time.time()
    assert len(CASES) == 100, f"expected 100 cases, got {len(CASES)}"
    for i, fn in enumerate(CASES):
        _run_case(i, fn)
    dt = time.time() - t0
    n = len(CASES)
    print(f"SUSX100: {n - len(FAILURES)}/{n} pass in {dt:.1f}s", flush=True)
    if FAILURES:
        print(f"FAILURES: {FAILURES}", flush=True)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
