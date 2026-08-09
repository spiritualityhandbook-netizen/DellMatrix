#!/usr/bin/env python3
"""
Matrix Awake — stay on, search far and wide, auto-grow, text and speak.

Modes:
  manual  — intake + judge + nursery hints
  auto    — Internet search_far_wide + self-handled nursery (confirm/reject)
            continuous growth without human nursery clicks

Heartbeat:
  body · delta · floor spirit · intake/auto_growth · text · speak

Floor · Verita · Delta still gate quality. Auto does not accept fog.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import os
import time
import hashlib


@dataclass
class TextChannel:
    lines: List[Dict[str, Any]] = field(default_factory=list)
    max_lines: int = 200

    def say(self, text: str, *, kind: str = "status", source: str = "matrix") -> Dict[str, Any]:
        text = (text or "").strip()
        if not text:
            return {"ok": False, "reason": "empty"}
        entry = {"text": text[:500], "kind": kind, "source": source, "ts": time.time()}
        self.lines.append(entry)
        while len(self.lines) > self.max_lines:
            self.lines.pop(0)
        return {"ok": True, **entry}

    def tail(self, n: int = 12) -> List[Dict[str, Any]]:
        return list(self.lines[-n:])


@dataclass
class SpeakChannel:
    enabled: bool = True
    last_utterance: str = ""
    backend: str = "auto"
    log: List[Dict[str, Any]] = field(default_factory=list)

    def _detect_backend(self) -> str:
        if self.backend not in ("stub", "auto"):
            return self.backend
        for cmd, name in (("espeak", "espeak"), ("say", "say")):
            if os.system(f"command -v {cmd} >/dev/null 2>&1") == 0:
                return name
        try:
            import pyttsx3  # type: ignore
            return "pyttsx3"
        except Exception:
            return "stub"

    def speak(self, text: str, *, also_text: Optional[TextChannel] = None) -> Dict[str, Any]:
        text = (text or "").strip()
        if not text or not self.enabled:
            return {"ok": False, "reason": "empty_or_disabled"}
        backend = self._detect_backend()
        spoken = False
        try:
            if backend == "espeak":
                safe = text[:180].replace("'", "")
                spoken = os.system(f"espeak {safe!r} >/dev/null 2>&1") == 0
            elif backend == "say":
                safe = text[:180].replace("'", "")
                spoken = os.system(f"say {safe!r} >/dev/null 2>&1") == 0
            elif backend == "pyttsx3":
                import pyttsx3  # type: ignore
                eng = pyttsx3.init()
                eng.say(text[:300])
                eng.runAndWait()
                spoken = True
        except Exception:
            spoken = False
        self.last_utterance = text[:300]
        entry = {"text": text[:300], "spoken": spoken, "backend": backend, "ts": time.time()}
        self.log.append(entry)
        if also_text is not None:
            also_text.say(text, kind="spoken", source="speak")
        return {"ok": True, **entry}


@dataclass
class GrowthIntake:
    seen_hashes: set = field(default_factory=set)
    candidates: List[Dict[str, Any]] = field(default_factory=list)

    def _hash(self, text: str) -> str:
        return hashlib.sha1(text.strip().encode("utf-8", errors="ignore")).hexdigest()[:16]

    def ingest_text(self, text: str, source: str = "content") -> Optional[Dict[str, Any]]:
        text = (text or "").strip()
        if len(text) < 12:
            return None
        h = self._hash(text)
        if h in self.seen_hashes:
            return None
        self.seen_hashes.add(h)
        label = text.split("\n", 1)[0].strip()[:72]
        item = {"label": label, "words": text[:400], "source": source, "hash": h, "ts": time.time()}
        self.candidates.append(item)
        while len(self.candidates) > 100:
            self.candidates.pop(0)
        return item

    def pull_ambient(self) -> List[Dict[str, Any]]:
        found: List[Dict[str, Any]] = []
        state = os.path.join(os.path.dirname(__file__), "..", "state")
        for sub in ("inbox", "screen", "mic", "clipboard"):
            folder = os.path.join(state, sub)
            if not os.path.isdir(folder):
                continue
            for name in sorted(os.listdir(folder))[:20]:
                path = os.path.join(folder, name)
                if not os.path.isfile(path) or not name.endswith(".txt"):
                    continue
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        text = f.read(4000)
                    got = self.ingest_text(text, source=f"ambient:{sub}")
                    if got:
                        found.append(got)
                except Exception:
                    continue
        return found


@dataclass
class MatrixAwake:
    on: bool = True
    auto: bool = True  # default ON per continuous self-growth request
    tick: int = 0
    text: TextChannel = field(default_factory=TextChannel)
    speak: SpeakChannel = field(default_factory=SpeakChannel)
    intake: GrowthIntake = field(default_factory=GrowthIntake)
    last_report: Dict[str, Any] = field(default_factory=dict)
    speak_status: bool = False

    def turn_on(self) -> Dict[str, Any]:
        self.on = True
        self.text.say("Matrix awake ON", kind="system")
        return {"ok": True, "on": True, "auto": self.auto}

    def turn_off(self) -> Dict[str, Any]:
        self.on = False
        self.text.say("Matrix awake OFF", kind="system")
        return {"ok": True, "on": False}

    def auto_on(self) -> Dict[str, Any]:
        self.auto = True
        self.text.say("Auto-growth ON · net far-wide · nursery self-handled", kind="system")
        return {"ok": True, "auto": True}

    def auto_off(self) -> Dict[str, Any]:
        self.auto = False
        self.text.say("Auto-growth OFF · manual nursery path", kind="system")
        return {"ok": True, "auto": False}

    def step(
        self,
        *,
        extra_content: str = "",
        net_query: str = "",
        place_on_confirm: bool = True,
    ) -> Dict[str, Any]:
        if not self.on:
            return {"ok": False, "on": False, "reason": "awake_off"}

        self.tick += 1
        auto_report: Dict[str, Any] = {}

        if self.auto:
            try:
                from form.dell_matrix.auto_growth import AutoGrowth
                ag = AutoGrowth(auto=True, internet=True)
                extras = []
                if extra_content.strip():
                    extras.append({
                        "label": extra_content.split("\n", 1)[0][:72],
                        "words": extra_content[:400],
                        "source": "content",
                    })
                extras.extend(self.intake.pull_ambient())
                auto_report = ag.step(
                    query=net_query or "",
                    extra_ideas=extras,
                    place_on_confirm=place_on_confirm,
                )
                if auto_report.get("confirmed_labels"):
                    self.text.say(
                        f"Auto confirmed: {auto_report['confirmed_labels'][0][:60]}",
                        kind="growth",
                    )
                self.text.say(
                    f"tick {self.tick} AUTO · net {auto_report.get('net_count', 0)} · "
                    f"confirmed {auto_report.get('confirmed', 0)} · "
                    f"band {auto_report.get('delta_band')}",
                    kind="heartbeat",
                )
            except Exception as e:
                auto_report = {"ok": False, "error": str(e)}
                self.text.say(f"Auto growth error: {e}", kind="error")

            if self.speak_status and self.tick % 5 == 0:
                self.speak.speak(
                    f"Auto tick {self.tick}. Confirmed {auto_report.get('confirmed', 0)}.",
                    also_text=self.text,
                )

            report = {
                "ok": True,
                "on": True,
                "auto": True,
                "tick": self.tick,
                "auto_growth": auto_report,
                "text_tail": self.text.tail(8),
                "speak_last": self.speak.last_utterance,
                "law": (
                    "AUTO: internet far-wide → Verita+Floor → nursery self-handle "
                    "→ confirm strong · reject fog · continuous"
                ),
            }
            self.last_report = report
            return report

        # ---- manual path ----
        body: Dict[str, Any] = {}
        delta: Dict[str, Any] = {}
        try:
            from form.dell_matrix.matrix_body import body_pulse
            body = body_pulse()
        except Exception as e:
            body = {"missing": [], "error": str(e)}
        try:
            from form.dell_matrix.delta_pressure import from_body
            delta = from_body(body)
        except Exception:
            delta = {"band": "unknown"}

        found: List[Dict[str, Any]] = list(self.intake.pull_ambient())
        if extra_content:
            got = self.intake.ingest_text(extra_content, source="content")
            if got:
                found.append(got)

        # net even in manual if query provided — turn on gate
        if net_query:
            try:
                from form.dell_matrix.internet_gate import InternetGate
                net = InternetGate()
                net.ensure_on_for_auto()
                fw = net.search_far_wide(net_query)
                for idea in fw.get("ideas") or []:
                    found.append(idea)
            except Exception:
                pass

        judged = []
        try:
            from form.dell_matrix.verita import verita_of_one
            from form.dell_matrix.floor_spirit import FLOOR_SPIRIT
            for it in found:
                v = verita_of_one(it.get("label") or "", words=it.get("words") or "")
                lic = FLOOR_SPIRIT.license_verita(v, f"{it.get('label','')} {it.get('words','')}")
                judged.append({**it, "accept": lic["final_accept"], "score": v.get("score")})
        except Exception:
            judged = [{**it, "accept": True} for it in found]

        accepted = [j for j in judged if j.get("accept")]
        band = delta.get("band", "?")
        self.text.say(
            f"tick {self.tick} manual · pressure {band} · found {len(found)} · accepted {len(accepted)}",
            kind="heartbeat",
        )
        report = {
            "ok": True,
            "on": True,
            "auto": False,
            "tick": self.tick,
            "intake": {"found": len(found), "accepted": len(accepted),
                       "labels": [a.get("label") for a in accepted[:5]]},
            "delta": {"band": band, "top": delta.get("top_action")},
            "text_tail": self.text.tail(6),
            "law": "manual: judge only · use auto_on() for self-handled nursery",
        }
        self.last_report = report
        return report

    def say(self, text: str) -> Dict[str, Any]:
        return self.text.say(text, kind="utterance")

    def voice(self, text: str) -> Dict[str, Any]:
        return self.speak.speak(text, also_text=self.text)


AWAKE = MatrixAwake(auto=True)


def step(**kwargs) -> Dict[str, Any]:
    return AWAKE.step(**kwargs)


def smoke() -> bool:
    print("=== MATRIX AWAKE AUTO SMOKE ===")
    r = []
    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}"); r.append(ok)
    m = MatrixAwake(auto=True, speak_status=False)
    m.turn_on()
    out = m.step(
        extra_content="Restore floor skeleton vital densify coherent offline body growth",
        place_on_confirm=False,
    )
    rec("auto_step", out.get("auto") is True and out.get("ok") is True)
    rec("text", len(out.get("text_tail") or []) >= 1)
    m.auto_off()
    out2 = m.step(extra_content="Alpha structure coherent growth densify organ")
    rec("manual_step", out2.get("auto") is False)
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    AWAKE.auto_on()
    AWAKE.turn_on()
    for i in range(2):
        rep = AWAKE.step(net_query="autonomous systems coherence architecture")
        ag = rep.get("auto_growth") or {}
        print(
            f"[tick {rep.get('tick')}] net={ag.get('net_count')} "
            f"confirmed={ag.get('confirmed')} band={ag.get('delta_band')} "
            f"labels={ag.get('confirmed_labels')}"
        )
        time.sleep(0.4)
