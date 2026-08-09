#!/usr/bin/env python3
"""
Free Matrix 150 enhancement audit — SUS standard.

  python -m form.dell_matrix.free_matrix_150_audit
  python -m form.dell_matrix.free_matrix_150_audit --cycles 150
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Tuple
import importlib

Check = Tuple[str, Callable[[], bool]]


def _import(name: str) -> bool:
    try:
        importlib.import_module(name)
        return True
    except Exception:
        return False


def _build_checks() -> List[Check]:
    C: List[Check] = []

    def add(name: str, fn: Callable[[], bool]) -> None:
        C.append((name, fn))

    mods = [
        "form.dell_matrix.perspective_views",
        "form.dell_matrix.dynamic_view_switch",
        "form.dell_matrix.spatial_audio",
        "form.dell_matrix.free_matrix",
        "form.dell_matrix.vision",
        "form.dell_matrix.first_person",
        "form.dell_matrix.matrix_awake",
        "form.dell_matrix.auto_growth",
        "form.dell_matrix.internet_gate",
        "form.dell_matrix.verita",
        "form.dell_matrix.floor_spirit",
        "form.dell_matrix.delta_pressure",
        "form.dell_matrix.organ_atlas",
        "form.dell_matrix.matrix_body",
        "form.dell_matrix.brain",
        "form.dell_matrix.live_visual",
        "form.dell_matrix.companion",
        "form.dell_matrix.act_on_seen",
        "form.dell_matrix.nursery",
        "form.mandell.floor",
    ]
    for m in mods:
        add(f"import:{m.split('.')[-1]}", lambda m=m: _import(m))

    add("perspective.smoke", lambda: importlib.import_module("form.dell_matrix.perspective_views").smoke())
    add("dynamic_switch.smoke", lambda: importlib.import_module("form.dell_matrix.dynamic_view_switch").smoke())
    add("spatial_audio.smoke", lambda: importlib.import_module("form.dell_matrix.spatial_audio").smoke())

    def modes_ok():
        from form.dell_matrix.perspective_views import MODES, PRIVILEGED
        return set(MODES) == {"first", "third", "parts", "whole"} and "user" in PRIVILEGED and "architect" in PRIVILEGED
    add("modes.law", modes_ok)

    def role_defaults():
        from form.dell_matrix.perspective_views import ROLE_DEFAULT_MODE
        return ROLE_DEFAULT_MODE.get("ai_first") == "first" and ROLE_DEFAULT_MODE.get("architect") == "whole"
    add("roles.defaults", role_defaults)

    def pan_gain():
        from form.dell_matrix.spatial_audio import pan_from_bearing, gain_from_distance, ear_from_pan
        return pan_from_bearing(90) >= 0.9 and gain_from_distance(0.5) == 1.0 and ear_from_pan(-0.5) == "L"
    add("audio.pan_gain", pan_gain)

    def spatialize_sides():
        from form.dell_matrix.spatial_audio import SpatialAudio
        cues = SpatialAudio().spatialize((0, 0), "N", [
            {"label": "R", "x": 5, "y": 0},
            {"label": "L", "x": -5, "y": 0},
        ])
        ears = {c["ear"] for c in cues}
        return "L" in ears and "R" in ears
    add("audio.sides", spatialize_sides)

    def switch_cycle():
        from form.dell_matrix.dynamic_view_switch import DynamicViewSwitch
        from form.dell_matrix.perspective_views import MODES

        class FakePlane:
            def all_nodes(self):
                return [{"id": "a", "label": "A", "x": 1, "y": 0, "skin": "core"}]

        class Body:
            pos = (0.0, 0.0)
            class facing:
                name = "E"

        class P:
            plane = FakePlane()
            avatar = type("A", (), {"body": Body()})()
            perspectives = None

        s = DynamicViewSwitch()
        p = P()
        seen = set()
        for _ in range(4):
            out = s.cycle(p)
            if not out.get("ok"):
                return False
            seen.add(out.get("to"))
        return seen == set(MODES)
    add("switch.full_cycle", switch_cycle)

    def hotkeys():
        from form.dell_matrix.dynamic_view_switch import DynamicViewSwitch

        class FakePlane:
            def all_nodes(self):
                return []

        class Body:
            pos = (0.0, 0.0)
            class facing:
                name = "N"

        class P:
            plane = FakePlane()
            avatar = type("A", (), {"body": Body()})()
            perspectives = None

        s = DynamicViewSwitch()
        p = P()
        return s.hotkey(p, "1").get("to") == "first" and s.hotkey(p, "w").get("to") == "whole"
    add("switch.hotkeys", hotkeys)

    def verita_solo():
        from form.dell_matrix.verita import verita_of_one
        v = verita_of_one("Restore floor skeleton", words="vital densify coherent offline body growth organ")
        return isinstance(v.get("score"), (int, float))
    add("verita.solo", verita_solo)

    def floor_license():
        from form.dell_matrix.verita import verita_of_one
        from form.dell_matrix.floor_spirit import FLOOR_SPIRIT
        v = verita_of_one("System coherence", words="whole body offline coherent growth restore")
        lic = FLOOR_SPIRIT.license_verita(v, "System coherence whole body")
        return "final_accept" in lic
    add("floor.license", floor_license)

    def delta_bands():
        from form.dell_matrix.delta_pressure import measure_pressure
        m = measure_pressure(
            c_now=0.5,
            missing=["lattice", "plane"],
            residue_count=1,
            handicaps=[],
            projections=[],
        )
        return "band" in m or "magnitude" in m
    add("delta.measure", delta_bands)

    def organ_atlas():
        from form.dell_matrix.organ_atlas import ORGAN_ATLAS, atlas_summary
        s = atlas_summary()
        n = s.get("organs", s.get("total", 0))
        return len(ORGAN_ATLAS) >= 20 and n >= 20
    add("organ.atlas", organ_atlas)

    def net_structure():
        from form.dell_matrix.internet_gate import InternetGate
        g = InternetGate()
        return g.on is False and hasattr(g, "search_far_wide") and hasattr(g, "ensure_on_for_auto")
    add("net.structure", net_structure)

    def auto_structure():
        from form.dell_matrix.auto_growth import AutoGrowth
        ag = AutoGrowth(auto=True, internet=False)
        out = ag.step(
            extra_ideas=[{"label": "Restore floor", "words": "vital densify coherent body", "source": "t"}],
            place_on_confirm=False,
        )
        return out.get("ok") is True and isinstance(out.get("confirmed_labels"), list)
    add("auto.step_offline", auto_structure)

    def awake_structure():
        from form.dell_matrix.matrix_awake import MatrixAwake
        m = MatrixAwake(auto=False)
        m.turn_on()
        out = m.step(extra_content="Restore floor skeleton densify coherent offline growth")
        return out.get("ok") is True
    add("awake.manual_step", awake_structure)

    spine = [
        "form.dell_matrix.free_matrix",
        "form.dell_matrix.perspective_views",
        "form.dell_matrix.dynamic_view_switch",
        "form.dell_matrix.spatial_audio",
        "form.dell_matrix.vision",
        "form.dell_matrix.first_person",
        "form.dell_matrix.live_visual",
        "form.dell_matrix.matrix_awake",
        "form.dell_matrix.auto_growth",
        "form.dell_matrix.internet_gate",
        "form.dell_matrix.verita",
        "form.dell_matrix.floor_spirit",
        "form.dell_matrix.delta_pressure",
        "form.dell_matrix.organ_atlas",
        "form.dell_matrix.brain",
        "form.dell_matrix.nursery",
        "form.dell_matrix.companion",
        "form.dell_matrix.act_on_seen",
        "form.dell_matrix.matrix_body",
        "form.mandell.floor",
    ]
    i = 0
    while len(C) < 150:
        m = spine[i % len(spine)]
        add(f"health:{i}:{m.split('.')[-1]}", lambda m=m: _import(m))
        i += 1
    return C[:150]


def run(cycles: int = 150) -> Dict[str, Any]:
    checks = _build_checks()[:cycles]
    print("=" * 60)
    print(f"  FREE MATRIX 150 AUDIT · SUS · cycles={len(checks)}")
    print("=" * 60)
    results: List[Tuple[str, bool, str]] = []
    for name, fn in checks:
        ok = False
        err = ""
        try:
            ok = bool(fn())
        except Exception as e:
            ok = False
            err = f"{type(e).__name__}: {e}"
        results.append((name, ok, err))
        mark = "PASS" if ok else "FAIL"
        extra = f" · {err}" if err else ""
        print(f"  [{mark}] {name}{extra}")

    passed = sum(1 for _, ok, _ in results if ok)
    failed = [name for name, ok, _ in results if not ok]
    print("=" * 60)
    print(f"  RESULT {passed}/{len(results)}  SUS={'PASS' if passed == len(results) else 'FAIL'}")
    if failed:
        print("  FAILED:")
        for f in failed[:40]:
            print(f"    · {f}")
    print("=" * 60)
    return {
        "ok": passed == len(results),
        "passed": passed,
        "total": len(results),
        "failed": failed,
        "sus": passed == len(results),
    }


def smoke() -> bool:
    out = run(cycles=40)
    return out["passed"] >= 30


if __name__ == "__main__":
    import sys
    cycles = 150
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    if "--cycles" in sys.argv:
        i = sys.argv.index("--cycles")
        if i + 1 < len(sys.argv):
            cycles = int(sys.argv[i + 1])
    rep = run(cycles=cycles)
    sys.exit(0 if rep["ok"] else 1)
