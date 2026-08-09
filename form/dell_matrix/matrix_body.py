#!/usr/bin/env python3
"""
Matrix Body — one living body for DellMatrix.

Law:
  Every process is an organ. Problems = missing or injured organ.
  Growth senses the gap, decides what to do next and why, moves toward goal.
  Sensory organs (ear, eye, screen, content) feed high-quality context into growth.

Ties: gate_discipline handicap→grow · RingedGrowth · forces · nature ·
      fourier · eigen · logistic · vision · nursery · floor · one-body.

Offline-first. Hardware senses are gated stubs until present.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
import time

# ---------------------------------------------------------------------------
# Organs — body map (no part excluded)
# ---------------------------------------------------------------------------

ORGANS: Dict[str, Dict[str, Any]] = {
    # structural
    "floor": {"role": "skeleton", "module": "form.mandell.floor", "dell": 65, "vital": True},
    "nursery": {"role": "immune", "module": "form.dell_matrix.nursery", "dell": 64, "vital": True},
    "lattice": {"role": "nervous", "module": "form.dell_matrix.harmonic_lattice", "dell": 61, "vital": True},
    "plane": {"role": "tissue", "module": "form.dell_matrix.plane", "dell": 15, "vital": True},
    # circulation / force
    "forces": {"role": "circulation", "module": "form.dell_matrix.forces", "dell": 83, "vital": True},
    "nature": {"role": "muscle", "module": "form.dell_matrix.nature_code", "dell": 60, "vital": True},
    "ringed_growth": {"role": "growth_plate", "module": "form.dell_matrix.ringed_growth", "dell": 87, "vital": True},
    # mind / signal
    "english_brain": {"role": "language_cortex", "module": "form.mandell.english_brain", "dell": 66, "vital": True},
    "gate": {"role": "brainstem", "module": "form.mandell.gate_discipline", "dell": 72, "vital": True},
    "fourier": {"role": "auditory_cortex", "module": "form.dell_matrix.fourier", "dell": 59, "vital": False},
    "eigen": {"role": "balance", "module": "form.dell_matrix.eigen_stability", "dell": 57, "vital": False},
    "logistic": {"role": "metabolism", "module": "form.dell_matrix.logistic_map", "dell": 58, "vital": False},
    "linear_algebra": {"role": "spatial_reasoning", "module": "form.dell_matrix.linear_algebra", "dell": 15, "vital": False},
    # perception / action
    "vision": {"role": "eye", "module": "form.dell_matrix.vision", "dell": 82, "vital": False},
    "perception": {"role": "proprioception", "module": "form.dell_matrix.perception", "dell": 82, "vital": False},
    "live_visual": {"role": "face", "module": "form.dell_matrix.live_visual", "dell": 9, "vital": False},
    "act_on_seen": {"role": "hand", "module": "form.dell_matrix.act_on_seen", "dell": 82, "vital": False},
    # higher / social
    "personas": {"role": "identity", "module": "form.dell_matrix.personas", "dell": 2, "vital": False},
    "neuroevo": {"role": "adaptation", "module": "form.dell_matrix.neuroevo", "dell": 88, "vital": False},
    "trading": {"role": "livelihood", "module": "form.trading", "dell": 89, "vital": False},
    "audit": {"role": "conscience", "module": "form.dell_matrix.incorporation_audit", "dell": 70, "vital": False},
    # sensory intake (hardware-gated)
    "ear": {"role": "microphone", "module": "form.dell_matrix.sense_intake", "dell": 75, "vital": False, "hardware": "mic"},
    "eye_cam": {"role": "camera", "module": "form.dell_matrix.sense_intake", "dell": 75, "vital": False, "hardware": "camera"},
    "screen": {"role": "screen_share", "module": "form.dell_matrix.sense_intake", "dell": 75, "vital": False, "hardware": "screen"},
    "content": {"role": "high_quality_intake", "module": "form.dell_matrix.sense_intake", "dell": 75, "vital": False, "hardware": None},
}


@dataclass
class OrganStatus:
    name: str
    present: bool
    healthy: bool
    role: str
    detail: str = ""
    dell: int = 0


@dataclass
class Decision:
    action: str
    why: str
    target_organ: str
    dell: int
    priority: int  # 1 = urgent vital
    goal_alignment: str


@dataclass
class BodyReport:
    organs: List[OrganStatus]
    missing: List[str]
    injured: List[str]
    decisions: List[Decision]
    goal: str
    ts: float = field(default_factory=time.time)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "goal": self.goal,
            "missing": self.missing,
            "injured": self.injured,
            "decisions": [
                {
                    "action": d.action,
                    "why": d.why,
                    "target_organ": d.target_organ,
                    "dell": d.dell,
                    "priority": d.priority,
                    "goal_alignment": d.goal_alignment,
                }
                for d in self.decisions
            ],
            "organ_count": len(self.organs),
            "present": sum(1 for o in self.organs if o.present),
            "healthy": sum(1 for o in self.organs if o.healthy),
            "ts": self.ts,
        }


class MatrixBody:
    """
    Living body wrapper around DellMatrix subsystems.
    Sense gaps → decide next + why → grow toward goal.
    """

    def __init__(self, goal: str = "grow DellMatrix as one body toward coherent offline-capable intelligence"):
        self.goal = goal
        self.history: List[Dict[str, Any]] = []
        self._import_cache: Dict[str, bool] = {}

    def _probe_module(self, dotted: str) -> Tuple[bool, str]:
        if dotted in self._import_cache:
            return self._import_cache[dotted], "cached"
        try:
            parts = dotted.split(".")
            mod = __import__(dotted, fromlist=[parts[-1]])
            self._import_cache[dotted] = True
            return True, "import_ok"
        except Exception as e:
            self._import_cache[dotted] = False
            return False, f"{type(e).__name__}: {e}"

    def sense_organs(self) -> List[OrganStatus]:
        out: List[OrganStatus] = []
        for name, meta in ORGANS.items():
            present, detail = self._probe_module(meta["module"])
            # hardware organs: present module does not mean hardware ready
            healthy = present
            if meta.get("hardware") and present:
                detail = f"{detail}; hardware={meta['hardware']} gated_until_device"
                # still healthy as software organ; device is separate densify
            out.append(OrganStatus(
                name=name,
                present=present,
                healthy=healthy,
                role=meta["role"],
                detail=detail,
                dell=int(meta.get("dell", 0)),
            ))
        return out

    def diagnose(self, organs: Optional[List[OrganStatus]] = None) -> BodyReport:
        organs = organs or self.sense_organs()
        missing = [o.name for o in organs if not o.present]
        injured = [o.name for o in organs if o.present and not o.healthy]
        decisions = self.decide(missing, injured)
        report = BodyReport(
            organs=organs,
            missing=missing,
            injured=injured,
            decisions=decisions,
            goal=self.goal,
        )
        return report

    def decide(self, missing: List[str], injured: List[str]) -> List[Decision]:
        """What to do next and why — vital gaps first, then goal-aligned densify."""
        decisions: List[Decision] = []
        for name in missing:
            meta = ORGANS.get(name, {})
            vital = bool(meta.get("vital"))
            decisions.append(Decision(
                action=f"densify_or_restore:{name}",
                why=(
                    f"Organ '{name}' ({meta.get('role')}) is missing. "
                    + ("Vital — body cannot fully circulate without it. " if vital else "Non-vital but needed for full capability. ")
                    + f"Grow toward goal: {self.goal[:80]}"
                ),
                target_organ=name,
                dell=int(meta.get("dell", 71)),
                priority=1 if vital else 2,
                goal_alignment="restore_missing_organ",
            ))
        for name in injured:
            meta = ORGANS.get(name, {})
            decisions.append(Decision(
                action=f"heal:{name}",
                why=f"Organ '{name}' present but unhealthy — heal before extending.",
                target_organ=name,
                dell=int(meta.get("dell", 42)),  # Retry
                priority=1,
                goal_alignment="heal_injured",
            ))
        if not missing and not injured:
            decisions.append(Decision(
                action="advance_goal",
                why="All known organs present. Move growth, sense intake, and audit toward goal.",
                target_organ="ringed_growth",
                dell=87,
                priority=3,
                goal_alignment="forward",
            ))
        decisions.sort(key=lambda d: d.priority)
        return decisions

    def on_problem(self, kind: str, detail: str) -> Dict[str, Any]:
        """
        Any unsolved challenge is treated as a missing/injured organ signal.
        Routes through gate handicap growth when available.
        """
        # map problem keywords → organ
        low = f"{kind} {detail}".lower()
        suspected = []
        mapping = [
            (("fourier", "spectrum", "frequency"), "fourier"),
            (("eigen", "stability"), "eigen"),
            (("logistic", "chaos", "regime"), "logistic"),
            (("force", "tick", "nature"), "nature"),
            (("vision", "seen", "look"), "vision"),
            (("import", "module", "open.py"), "gate"),
            (("audio", "mic", "listen"), "ear"),
            (("camera", "see", "video"), "eye_cam"),
            (("screen", "share", "display"), "screen"),
            (("content", "context", "ingest"), "content"),
            (("growth", "ring", "nursery"), "ringed_growth"),
            (("audit", "test"), "audit"),
        ]
        for keys, organ in mapping:
            if any(k in low for k in keys):
                suspected.append(organ)
        if not suspected:
            suspected = ["gate"]  # brainstem default

        growth_events = []
        try:
            from form.mandell.gate_discipline import on_handicap
            for organ in suspected:
                growth_events.append(on_handicap(
                    f"missing_or_injured_organ:{organ}",
                    f"{kind}: {detail[:160]}",
                ))
        except Exception as e:
            growth_events.append({"fallback": str(e), "organ": suspected})

        report = self.diagnose()
        entry = {
            "problem": kind,
            "detail": detail[:200],
            "suspected_organs": suspected,
            "growth": growth_events,
            "body": report.as_dict(),
            "next": report.decisions[0].__dict__ if report.decisions else None,
            "law": "problem = missing organ · sense · decide · grow",
        }
        self.history.append(entry)
        return entry

    def pulse(self) -> Dict[str, Any]:
        """One body heartbeat: sense → diagnose → decide → optional growth stamp."""
        report = self.diagnose()
        # notify gate of vital missing
        for name in report.missing:
            if ORGANS.get(name, {}).get("vital"):
                try:
                    from form.mandell.gate_discipline import on_handicap
                    on_handicap(f"vital_missing:{name}", f"role={ORGANS[name]['role']}")
                except Exception:
                    pass
        out = report.as_dict()
        out["history_len"] = len(self.history)
        return out

    def set_goal(self, goal: str) -> None:
        self.goal = goal


# ---------------------------------------------------------------------------
# Sensory intake — offline stubs; densify when device/content available
# ---------------------------------------------------------------------------

class SenseIntake:
    """
    Ear / eye_cam / screen / content organs.
    Hardware paths stay gated. Content path accepts text/context offline.
    High-quality intake grows the matrix via gate + body on_problem if weak.
    """

    def __init__(self, body: Optional[MatrixBody] = None):
        self.body = body or MatrixBody()
        self.buffer: List[Dict[str, Any]] = []

    def listen_stub(self, transcript: Optional[str] = None) -> Dict[str, Any]:
        if transcript is None:
            return {
                "organ": "ear",
                "status": "gated",
                "why": "No microphone stream in this host. Provide transcript text to densify offline.",
                "dell": 75,
            }
        return self.ingest_content(transcript, source="mic_transcript", quality="speech")

    def see_stub(self, description: Optional[str] = None) -> Dict[str, Any]:
        if description is None:
            return {
                "organ": "eye_cam",
                "status": "gated",
                "why": "No camera frame in this host. Provide visual description to densify offline.",
                "dell": 75,
            }
        return self.ingest_content(description, source="camera_desc", quality="vision")

    def screen_stub(self, capture_text: Optional[str] = None) -> Dict[str, Any]:
        if capture_text is None:
            return {
                "organ": "screen",
                "status": "gated",
                "why": "No screen-share frame. Provide OCR/text capture to densify offline.",
                "dell": 75,
            }
        return self.ingest_content(capture_text, source="screen", quality="ui_context")

    def ingest_content(
        self,
        text: str,
        source: str = "content",
        quality: str = "text",
    ) -> Dict[str, Any]:
        """High-quality context intake — always available offline as text."""
        text = (text or "").strip()
        if len(text) < 8:
            return self.body.on_problem(
                "weak_content",
                f"source={source} too short for growth",
            )
        item = {
            "source": source,
            "quality": quality,
            "n_chars": len(text),
            "preview": text[:160],
            "ts": time.time(),
        }
        self.buffer.append(item)
        # light gate turn so language sees the intake
        try:
            from form.mandell.gate_discipline import gate_turn
            plan = gate_turn(f"INTAKE[{source}/{quality}]: {text[:200]}")
        except Exception as e:
            plan = {"error": str(e)}
        return {
            "organ": "content",
            "status": "ingested",
            "item": item,
            "gate": plan,
            "buffer_len": len(self.buffer),
            "why": "High-quality context expands DellMatrix language and lattice pressure.",
        }


# module helpers
BODY = MatrixBody()
SENSES = SenseIntake(BODY)


def body_pulse() -> Dict[str, Any]:
    return BODY.pulse()


def problem(kind: str, detail: str) -> Dict[str, Any]:
    return BODY.on_problem(kind, detail)


def smoke() -> bool:
    print("=== MATRIX_BODY SMOKE ===")
    r = []
    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}"); r.append(ok)

    b = MatrixBody(goal="one body coherent growth")
    report = b.diagnose()
    rec("diagnose_runs", isinstance(report.missing, list))
    rec("decisions_exist", len(report.decisions) >= 1)
    rec("organs_mapped", len(report.organs) >= 10)

    p = b.on_problem("import_error", "No module named form.open")
    rec("problem_maps_organ", "suspected_organs" in p and len(p["suspected_organs"]) >= 1)

    s = SenseIntake(b)
    gated = s.listen_stub(None)
    rec("ear_gated", gated.get("status") == "gated")
    got = s.ingest_content("Fourier spectrum of square wave shows odd harmonics.", source="doc")
    rec("content_ingest", got.get("status") == "ingested")

    pulse = b.pulse()
    rec("pulse_ok", "missing" in pulse and "decisions" in pulse)

    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
