#!/usr/bin/env python3
"""
Universal LLM bridge — cloud + local open-source (Ollama).

44[Bridge] > 35[Discover] >> 04[Transform] :: LLMBridge

Cloud (env keys):
  gemini, aistudio, grok, claude, copilot

Local OSS:
  ollama / local  — http://127.0.0.1:11434  (no cloud key)
  OLLAMA_HOST, OLLAMA_MODEL
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request

try:
    from form.mandell.floor import FLOOR, assert_floor_intact
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    from form.mandell.floor import FLOOR, assert_floor_intact

PROVIDERS = ("ollama", "local", "gemini", "grok", "claude", "copilot", "aistudio")


@dataclass
class ProviderResult:
    provider: str
    ok: bool
    text: str = ""
    error: str = ""
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "ok": self.ok,
            "text": self.text[:8000],
            "error": self.error,
            "meta": self.meta,
        }


def _env(*names: str) -> str:
    for n in names:
        v = os.environ.get(n, "").strip()
        if v:
            return v
    return ""


def _http_json(url: str, payload: dict, headers: Optional[dict] = None, timeout: int = 120) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers=headers or {"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _http_get_json(url: str, timeout: int = 5) -> dict:
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def ollama_host() -> str:
    return _env("OLLAMA_HOST") or "http://127.0.0.1:11434"


def ollama_alive() -> bool:
    try:
        _http_get_json(ollama_host().rstrip("/") + "/api/tags", timeout=2)
        return True
    except Exception:
        return False


def ollama_models() -> List[str]:
    try:
        data = _http_get_json(ollama_host().rstrip("/") + "/api/tags", timeout=5)
        return [m.get("name", "") for m in data.get("models") or [] if m.get("name")]
    except Exception:
        return []


@dataclass
class LLMBridge:
    enabled: Dict[str, bool] = field(default_factory=lambda: {p: False for p in PROVIDERS})

    def detect(self) -> Dict[str, Any]:
        local = ollama_alive()
        models = ollama_models() if local else []
        return {
            "ollama": local,
            "local": local,
            "ollama_host": ollama_host(),
            "ollama_models": models,
            "ollama_model_default": _env("OLLAMA_MODEL") or (models[0] if models else "llama3.2"),
            "gemini": bool(_env("GOOGLE_API_KEY", "GEMINI_API_KEY")),
            "aistudio": bool(_env("GOOGLE_API_KEY", "GEMINI_API_KEY", "AISTUDIO_API_KEY")),
            "grok": bool(_env("XAI_API_KEY")),
            "claude": bool(_env("ANTHROPIC_API_KEY")),
            "copilot": bool(_env("GITHUB_TOKEN", "GH_TOKEN")) or bool(shutil.which("gh")),
            "gh_cli": bool(shutil.which("gh")),
            "floor": list(FLOOR),
            "note": "Prefer ollama/local for offline. Cloud keys optional.",
        }

    def enable(self, name: str) -> bool:
        if name not in self.enabled:
            return False
        self.enabled[name] = True
        return True

    def disable(self, name: str) -> bool:
        if name not in self.enabled:
            return False
        self.enabled[name] = False
        return True

    def call(self, provider: str, prompt: str, system: str = "") -> ProviderResult:
        assert_floor_intact()
        provider = provider.lower().strip()
        if provider not in PROVIDERS:
            return ProviderResult(provider, False, error=f"unknown provider {provider}")
        det = self.detect()
        if not self.enabled.get(provider, False):
            if not det.get(provider):
                return ProviderResult(provider, False, error=f"{provider} not configured")
            self.enabled[provider] = True
        try:
            if provider in ("ollama", "local"):
                return self._ollama(prompt, system)
            if provider in ("gemini", "aistudio"):
                return self._gemini(prompt, system, label=provider)
            if provider == "grok":
                return self._grok(prompt, system)
            if provider == "claude":
                return self._claude(prompt, system)
            if provider == "copilot":
                return self._copilot(prompt, system)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")[:500]
            return ProviderResult(provider, False, error=f"HTTP {e.code}: {body}")
        except Exception as e:
            return ProviderResult(provider, False, error=str(e))
        return ProviderResult(provider, False, error="unhandled")

    def call_all(self, prompt: str, system: str = "") -> List[ProviderResult]:
        det = self.detect()
        out = []
        for p in PROVIDERS:
            if p == "local":
                continue  # alias of ollama
            if det.get(p):
                out.append(self.call(p, prompt, system))
        return out

    def _ollama(self, prompt: str, system: str) -> ProviderResult:
        if not ollama_alive():
            return ProviderResult(
                "ollama",
                False,
                error="Ollama not running — install from ollama.com and run: ollama serve",
            )
        model = _env("OLLAMA_MODEL") or (ollama_models() or ["llama3.2"])[0]
        url = ollama_host().rstrip("/") + "/api/chat"
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        payload = {"model": model, "messages": messages, "stream": False}
        data = _http_json(url, payload, timeout=180)
        out = (data.get("message") or {}).get("content", "")
        return ProviderResult("ollama", True, text=out, meta={"model": model, "host": ollama_host()})

    def _gemini(self, prompt: str, system: str, label: str = "gemini") -> ProviderResult:
        key = _env("GOOGLE_API_KEY", "GEMINI_API_KEY", "AISTUDIO_API_KEY")
        if not key:
            return ProviderResult(label, False, error="missing GOOGLE_API_KEY / GEMINI_API_KEY")
        model = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
        text = prompt if not system else f"{system}\n\n{prompt}"
        data = _http_json(url, {"contents": [{"parts": [{"text": text}]}]}, {"Content-Type": "application/json"})
        parts = (data.get("candidates") or [{}])[0].get("content", {}).get("parts") or []
        out = "".join(p.get("text", "") for p in parts)
        return ProviderResult(label, True, text=out, meta={"model": model})

    def _grok(self, prompt: str, system: str) -> ProviderResult:
        key = _env("XAI_API_KEY")
        if not key:
            return ProviderResult("grok", False, error="missing XAI_API_KEY")
        model = os.environ.get("GROK_MODEL", "grok-2-latest")
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        data = _http_json(
            "https://api.x.ai/v1/chat/completions",
            {"model": model, "messages": messages, "temperature": 0.4},
            {"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
        )
        out = (data.get("choices") or [{}])[0].get("message", {}).get("content", "")
        return ProviderResult("grok", True, text=out, meta={"model": model})

    def _claude(self, prompt: str, system: str) -> ProviderResult:
        key = _env("ANTHROPIC_API_KEY")
        if not key:
            return ProviderResult("claude", False, error="missing ANTHROPIC_API_KEY")
        model = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-20250514")
        payload: Dict[str, Any] = {
            "model": model,
            "max_tokens": 2048,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            payload["system"] = system
        data = _http_json(
            "https://api.anthropic.com/v1/messages",
            payload,
            {
                "Content-Type": "application/json",
                "x-api-key": key,
                "anthropic-version": "2023-06-01",
            },
        )
        blocks = data.get("content") or []
        out = "".join(b.get("text", "") for b in blocks if b.get("type") == "text")
        return ProviderResult("claude", True, text=out, meta={"model": model})

    def _copilot(self, prompt: str, system: str) -> ProviderResult:
        gh = shutil.which("gh")
        if gh:
            try:
                text = prompt if not system else f"{system}\n\n{prompt}"
                r = subprocess.run([gh, "auth", "status"], capture_output=True, text=True, timeout=15)
                if r.returncode != 0:
                    return ProviderResult("copilot", False, error="gh not authenticated — gh auth login")
                return ProviderResult(
                    "copilot",
                    True,
                    text=(
                        "GitHub CLI ready. Interactive: gh copilot suggest \"...\"\n\n"
                        f"Context preview:\n{text[:1500]}"
                    ),
                    meta={"gh": True},
                )
            except Exception as e:
                return ProviderResult("copilot", False, error=str(e))
        if _env("GITHUB_TOKEN", "GH_TOKEN"):
            return ProviderResult(
                "copilot",
                True,
                text="GITHUB_TOKEN set. Install: winget install GitHub.cli && gh auth login",
                meta={"token": True},
            )
        return ProviderResult("copilot", False, error="install GitHub CLI or set GITHUB_TOKEN")


SYSTEM_MATRIX = (
    "You enhance a Dell Matrix trading workspace. "
    "Floor is locked Alpha Delta Omega Omni. "
    "Be practical, risk-aware, not financial advice. "
    "Return concrete observations and ranked next actions. "
    "Mandell-aware: prefer structure over fluff."
)


def enhance_matrix(
    bridge: LLMBridge,
    context: str,
    providers: Optional[List[str]] = None,
) -> Dict[str, Any]:
    assert_floor_intact()
    det = bridge.detect()
    use = providers or [p for p in PROVIDERS if p != "local" and det.get(p)]
    results = []
    for p in use:
        if not det.get(p):
            results.append(ProviderResult(p, False, error="not configured").to_dict())
            continue
        results.append(bridge.call(p, context, SYSTEM_MATRIX).to_dict())
    return {
        "ok": any(r.get("ok") for r in results),
        "results": results,
        "floor": list(FLOOR),
        "disclaimer": "AI output is not financial advice. Verify before trading.",
    }


def smoke() -> bool:
    print("=== LLM BRIDGE SMOKE ===")
    b = LLMBridge()
    d = b.detect()
    print("detect:", json.dumps({k: d[k] for k in d if k != "ollama_models"}, indent=2))
    r = b.call("nope", "test")
    ok = r.ok is False and d["floor"] == list(FLOOR)
    print("PASS" if ok else "FAIL")
    return ok


def main() -> None:
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    if "--detect" in sys.argv:
        print(json.dumps(LLMBridge().detect(), indent=2))
        return
    print("44[Bridge] :: ollama/local + cloud providers")


if __name__ == "__main__":
    main()
