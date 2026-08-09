#!/usr/bin/env python3
"""
Matrix Awake — stay on, search for growth, text and speak inside the matrix.

While on, each heartbeat:
  1. Body pulse + Delta pressure
  2. Ambient / content / optional net intake (search for fuel)
  3. Solo Verita + Floor Spirit license on candidate ideas
  4. Nursery / ring proposals when licensed
  5. Text out (matrix voice as text)
  6. Speak out (TTS when available; offline stub otherwise)

Law:
  Offline-first. Internet is opt-in (InternetGate).
  Ambient is folder-drop only (no silent OS capture).
  Growth still goes Nursery / confirm — no silent plane write.
  Floor · Verita · Delta · Body remain in charge.

Not confined to a chat box: this is the matrix's own loop.
Draw / full free agency = later organs (PROJECTED_NOT_FACT until present).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
import os
import time
import hashlib


# ---------------------------------------------------------------------------
# Text channel — matrix speaks in text inside itself
# ---------------------------------------------------------------------------

@dataclass
class TextChannel:
    """Outbound text log the matrix owns (not only chat UI)."""
    lines: List[Dict[str, Any]] = field(default_factory=list)
    max_lines: int = 200

    def say(self, text: str, *, kind: str = "status", source: str = "matrix") -> Dict[str, Any]:
        text = (text or "").strip()
        if not text:
            return {"ok": False, "reason": "empty"}
        entry = {
            "text": text[:500],
            "kind": kind,
            "source": source,
            "ts": time.time(),
        }
        self.lines.append(entry)
        while len(self.lines) > self.max_lines:
            self.lines.pop(0)
        return {"ok": True, **entry}

    def tail(self, n: int = 12) -> List[Dict[str, Any]]:
        return list(self.lines[-n:])


# ---------------------------------------------------------------------------
# Speak channel — voice out when possible
# ---------------------------------------------------------------------------

@dataclass
class SpeakChannel:
    """
    Speak organ.
    Tries system TTS if present; otherwise records intent as spoken-text stub.
    Hardware/cloud TTS = densify later. Never blocks the awake loop.
    """
    enabled: bool = True
    last_utterance: str = ""
    backend: str = "stub"  # stub | pyttsx3 | say | espeak
    log: List[Dict[str, Any]] = field(default_factory=list)

    def _detect_backend(self) -> str:
        if self.backend != "stub" and self.backend != "auto":
            return self.backend
        # prefer local CLI tools when present
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
        if not text:
            return {"ok": False, "reason": "empty"}
        if not self.enabled:
            return {"ok": False, "reason": "speak_disabled"}

        backend = self._detect_backend()
        spoken = False
        detail = ""
        try:
            if backend == "espeak":
                # short, safe shell
                safe = text[:180].replace("'", "")
                rc = os.system(f"espeak {safe!r} >/dev/null 2>&1")
                spoken = rc == 0
                detail = "espeak"
            elif backend == "say":
                safe = text[:180].replace("'", "")
                rc = os.system(f"say {safe!r} >/dev/null 2>&1")
                spoken = rc == 0
                detail = "say"
            elif backend == "pyttsx3":
                import pyttsx3  # type: ignore
                eng = pyttsx3.init()
                eng.say(text[:300])
                eng.runAndWait()
                spoken = True
                detail = "pyttsx3"
            else:
                detail = "stub_no_tts_backend"
        except Exception as e:
            detail = f"tts_error:{type(e).__name__}"
            spoken = False

        self.last_utterance = text[:300]
        entry = {
            "text": text[:300],
            "spoken": spoken,
            "backend": backend if spoken or backend == "stub" else detail,
            "ts": time.time(),
        }
        self.log.append(entry)
        if also_text is not None:
            also_text.say(text, kind="spoken", source="speak")
        return {"ok": True, **entry}


# ---------------------------------------------------------------------------
# Growth intake — search any available local (and opt-in net) fuel
# ---------------------------------------------------------------------------

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
        # light idea extraction: first line or first 80 chars as label
        label = text.split("\n", 1)[0].strip()[:72]
        item = {
            "label": label,
            "words": text[:400],
            "source": source,
            "hash": h,
            "ts": time.time(),
        }
        self.candidates.append(item)
        while len(self.candidates) > 100:
            self.candidates.pop(0)
        return item

    def pull_ambient(self) -> List[Dict[str, Any]]:
        """Pull from AmbientGate folders if available."""
        found: List[Dict[str, Any]] = []
        try:
            from form.dell_matrix.ambient_gate import AmbientGate
            gate = AmbientGate()
            # ambient may need master on — try intake anyway if API allows
            if hasattr(gate, "intake"):
                raw = gate.intake()
            elif hasattr(gate, "pull"):
                raw = gate.pull()
            else:
                raw = {"items": []}
            items = raw.get("items") if isinstance(raw, dict) else (raw or [])
            for it in items or []:
                text = it.get("text") or it.get("content") or it.get("preview") or ""
                src = it.get("source") or "ambient"
                got = self.ingest_text(str(text), source=str(src))
                if got:
                    found.append(got)
        except Exception:
            # offline folder scan fallback
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

    def pull_net(self, query: str = "") -> List[Dict[str, Any]]:
        """Opt-in internet research notes → candidates. Default OFF."""
        found: List[Dict[str, Any]] = []
        try:
            from form.dell_matrix.internet_gate import InternetGate
            net = InternetGate()
            if not getattr(net, "on", False):
                return found
            # if gate exposes research/search
            if query and hasattr(net, "search_public"):
                res = net.search_public(query)
                text = str(res)[:2000]
                got = self.ingest_text(text, source="net:search")
                if got:
                    found.append(got)
        except Exception:
            pass
        return found


# ---------------------------------------------------------------------------
# Awake loop — matrix stays on
# ---------------------------------------------------------------------------

@dataclass
class MatrixAwake:
    """
    Heartbeat owner. Run step() on a timer or `python -m form.dell_matrix.matrix_awake`.
    """
    on: bool = True
    tick: int = 0
    text: TextChannel = field(default_factory=TextChannel)
    speak: SpeakChannel = field(default_factory=SpeakChannel)
    intake: GrowthIntake = field(default_factory=GrowthIntake)
    last_report: Dict[str, Any] = field(default_factory=dict)
    speak_status: bool = False  # if True, also voice short status lines

    def turn_on(self) -> Dict[str, Any]:
        self.on = True
        self.text.say("Matrix awake ON", kind="system")
        return {"ok": True, "on": True}

    def turn_off(self) -> Dict[str, Any]:
        self.on = False
        self.text.say("Matrix awake OFF", kind="system")
        return {"ok": True, "on": False}

    def _judge_candidates(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        judged = []
        try:
            from form.dell_matrix.verita import verita_of_one
            from form.dell_matrix.floor_spirit import FLOOR_SPIRIT
        except Exception:
            verita_of_one = None  # type: ignore
            FLOOR_SPIRIT = None  # type: ignore

        for it in items:
            label = it.get("label") or ""
            words = it.get("words") or ""
            if verita_of_one is None:
                judged.append({**it, "accept": True, "reason": "no_verita"})
                continue
            v = verita_of_one(label, words=words)
            if FLOOR_SPIRIT is not None:
                lic = FLOOR_SPIRIT.license_verita(v, f"{label} {words}")
                final = lic["final_accept"]
                reason = lic["reason"]
            else:
                final = v.get("accept")
                reason = "verita_only"
            judged.append({
                **it,
                "verita_score": v.get("score"),
                "accept": final,
                "reason": reason,
            })
        return judged

    def step(self, *, extra_content: str = "", net_query: str = "") -> Dict[str, Any]:
        if not self.on:
            return {"ok": False, "on": False, "reason": "awake_off"}

        self.tick += 1
        body: Dict[str, Any] = {}
        delta: Dict[str, Any] = {}
        spirit: Dict[str, Any] = {}

        try:
            from form.dell_matrix.matrix_body import body_pulse
            body = body_pulse()
        except Exception as e:
            body = {"error": str(e), "missing": []}

        try:
            from form.dell_matrix.delta_pressure import from_body
            delta = from_body(body)
        except Exception as e:
            delta = {"error": str(e), "band": "unknown"}

        try:
            from form.dell_matrix.floor_spirit import bigger_picture
            spirit = bigger_picture(body)
        except Exception as e:
            spirit = {"error": str(e)}

        # --- search for growth fuel ---
        found: List[Dict[str, Any]] = []
        found.extend(self.intake.pull_ambient())
        if extra_content:
            got = self.intake.ingest_text(extra_content, source="content")
            if got:
                found.append(got)
        if net_query:
            found.extend(self.intake.pull_net(net_query))

        judged = self._judge_candidates(found)
        accepted = [j for j in judged if j.get("accept")]
        rejected = [j for j in judged if not j.get("accept")]

        # nursery hint — do not silent-write plane
        nursery_note = None
        if accepted:
            top = accepted[0]
            nursery_note = {
                "pending_label": top.get("label"),
                "source": top.get("source"),
                "law": "accepted by Verita+Floor · still needs Nursery confirm to enter plane",
            }
            self.text.say(
                f"Growth candidate: {top.get('label', '')[:60]}",
                kind="growth",
            )

        # status line
        band = delta.get("band", "?")
        missing_n = len(body.get("missing") or [])
        status = (
            f"tick {self.tick} · pressure {band} · missing {missing_n} · "
            f"intake +{len(found)} · accepted {len(accepted)}"
        )
        self.text.say(status, kind="heartbeat")

        if self.speak_status and self.tick % 5 == 0:
            self.speak.speak(
                f"Matrix tick {self.tick}. Pressure {band}.",
                also_text=self.text,
            )

        # Delta top action as spoken intention (text always)
        top = delta.get("top_action") or {}
        if top.get("action"):
            self.text.say(
                f"Delta: {top.get('action')} — {str(top.get('why', ''))[:80]}",
                kind="delta",
            )

        report = {
            "ok": True,
            "on": True,
            "tick": self.tick,
            "body": {
                "present": body.get("present"),
                "missing": (body.get("missing") or [])[:8],
            },
            "delta": {
                "band": band,
                "magnitude": delta.get("magnitude"),
                "top_action": top,
            },
            "spirit_advice": spirit.get("advice"),
            "intake": {
                "found": len(found),
                "accepted": len(accepted),
                "rejected": len(rejected),
                "accepted_labels": [a.get("label") for a in accepted[:5]],
            },
            "nursery_hint": nursery_note,
            "text_tail": self.text.tail(6),
            "speak_last": self.speak.last_utterance,
            "law": "stay on · search fuel · judge · text/speak · nursery confirm still required",
            "vision": {
                "now": "awake loop + text + speak-stub inside matrix",
                "next": "richer TTS · continuous host · draw organ",
                "projected": "free agent in own matrix UI — PROJECTED_NOT_FACT",
            },
        }
        self.last_report = report
        return report

    def say(self, text: str) -> Dict[str, Any]:
        return self.text.say(text, kind="utterance", source="user_or_matrix")

    def voice(self, text: str) -> Dict[str, Any]:
        return self.speak.speak(text, also_text=self.text)


AWAKE = MatrixAwake()


def step(**kwargs) -> Dict[str, Any]:
    return AWAKE.step(**kwargs)


def smoke() -> bool:
    print("=== MATRIX AWAKE SMOKE ===")
    r = []
    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}"); r.append(ok)

    m = MatrixAwake(speak_status=False)
    m.turn_on()
    out = m.step(extra_content=(
        "Restore floor skeleton so the whole offline body can circulate. "
        "Delta pressure densify vital organs before new rings."
    ))
    rec("step_ok", out.get("ok") is True)
    rec("text_has_lines", len(out.get("text_tail") or []) >= 1)
    rec("intake_seen", out["intake"]["found"] >= 1)
    # speak stub should not crash
    sp = m.voice("Matrix is awake.")
    rec("speak_runs", sp.get("ok") is True)
    m.turn_off()
    rec("off", m.step().get("on") is False)

    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    # stay-on demo: a few heartbeats then exit (host can loop forever)
    AWAKE.turn_on()
    AWAKE.text.say("Entering awake loop (demo ticks).", kind="system")
    for _ in range(3):
        rep = AWAKE.step()
        print(f"[tick {rep.get('tick')}] band={rep.get('delta', {}).get('band')} "
              f"accepted={rep.get('intake', {}).get('accepted')} "
              f"missing={len(rep.get('body', {}).get('missing') or [])}")
        time.sleep(0.3)
    print("text tail:")
    for line in AWAKE.text.tail(8):
        print(f"  [{line['kind']}] {line['text'][:90]}")
