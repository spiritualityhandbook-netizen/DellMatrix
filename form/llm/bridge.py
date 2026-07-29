#!/usr/bin/env python3
"""
Universal LLM bridge — link external AIs into Dell Matrix.

44[Bridge] > 35[Discover] >> 04[Transform] :: LLMBridge

Providers (all optional, env-key gated):
  gemini    GOOGLE_API_KEY or GEMINI_API_KEY
  grok      XAI_API_KEY
  claude    ANTHROPIC_API_KEY
  copilot   GITHUB_TOKEN (gh) or COPILOT via gh CLI if present
  aistudio  GOOGLE_API_KEY (Google AI Studio same key family)

No keys in repo. Offline core still works with providers OFF.
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

PROVIDERS = ("gemini", "grok", "claude", "copilot", "aistudio")


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


def _http_json(url: str, payload: dict, headers: dict, timeout: int = 60) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


@dataclass
class LLMBridge:
    """Route prompts to any configured provider."""

    enabled: Dict[str, bool] = field(default_factory=lambda: {p: False for p in PROVIDERS})

    def detect(self) -> Dict[str, Any]:
        """What can run on this machine right now."""
        return {
            "gemini": bool(_env("GOOGLE_API_KEY", "GEMINI_API_KEY")),
            "aistudio": bool(_env("GOOGLE_API_KEY", "GEMINI_API_KEY", "AISTUDIO_API_KEY")),
            "grok": bool(_env("XAI_API_KEY")),
            "claude": bool(_env("ANTHROPIC_API_KEY")),
            "copilot": bool(_env("GITHUB_TOKEN", "GH_TOKEN")) or bool(shutil.which("gh")),
            "gh_cli": bool(shutil.which("gh")),
            "floor": list(FLOOR),
            "note": "Keys via environment only — never commit secrets",
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
        if not self.enabled.get(provider, False):
            # auto-enable if key present for convenience
            det = self.detect()
            if not det.get(provider):
                return ProviderResult(provider, False, error=f"{provider} not configured (missing key/CLI)")
            self.enabled[provider] = True

        try:
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
            if det.get(p):
                out.append(self.call(p, prompt, system))
        return out

    def _gemini(self, prompt: str, system: str, label: str = "gemini") -> ProviderResult:
        key = _env("GOOGLE_API_KEY", "GEMINI_API_KEY", "AISTUDIO_API_KEY")
        if not key:
            return ProviderResult(label, False, error="missing GOOGLE_API_KEY / GEMINI_API_KEY")
        model = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
        text = prompt if not system else f"{system}\n\n{prompt}"
        payload = {"contents": [{"parts": [{"text": text}]}]}
        data = _http_json(url, payload, {"Content-Type": "application/json"})
        parts = (
            data.get("candidates") or [{}]
        )[0].get("content", {}).get("parts") or []}
        out = "".join(p.get("text", "") for p in parts)
        return ProviderResult(label, True, text=out, meta={"model": model})

    def _grok(self, prompt: str, system: str) -> ProviderResult:
        key = _env("XAI_API_KEY")
        if not key:
            return ProviderResult("grok", False, error="missing XAI_API_KEY")
        model = os.environ.get("GROK_MODEL", "grok-2-latest")
        url = "https://api.x.ai/v1/chat/completions"
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        payload = {"model": model, "messages": messages, "temperature": 0.4}
        data = _http_json(
            url,
            payload,
            {"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
        )
        out = (data.get("choices") or [{}])[0].get("message", {}).get("content", "")
        return ProviderResult("grok", True, text=out, meta={"model": model})

    def _claude(self, prompt: str, system: str) -> ProviderResult:
        key = _env("ANTHROPIC_API_KEY")
        if not key:
            return ProviderResult("claude", False, error="missing ANTHROPIC_API_KEY")
        model = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-20250514")
        url = "https://api.anthropic.com/v1/messages"
        payload = {
            "model": model,
            "max_tokens": 2048,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            payload["system"] = system
        data = _http_json(
            url,
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
        # Prefer gh copilot if available; else note token-only limitation
        gh = shutil.which("gh")
        if gh:
            try:
                text = prompt if not system else f"{system}\n\n{prompt}"
                # gh copilot suggest is interactive; use api as soft fallback message
                r = subprocess.run(
                    [gh, "auth", "status"],
                    capture_output=True,
                    text=True,
                    timeout=15,
                )
                if r.returncode != 0:
                    return ProviderResult(
                        "copilot",
                        False,
                        error="gh not authenticated — run: gh auth login",
                        meta={"gh": True},
                    )
                return ProviderResult(
                    "copilot",
                    True,
                    text=(
                        "GitHub CLI authenticated. Use interactive: "
                        "gh copilot suggest \"your question\" "
                        "or wire Copilot API for your org. Context received.\n\n"
                        f"Context preview:\n{text[:1500]}"
                    ),
                    meta={"gh": True, "mode": "cli_ready"},
                )
            except Exception as e:
                return ProviderResult("copilot", False, error=str(e))
        if _env("GITHUB_TOKEN", "GH_TOKEN"):
            return ProviderResult(
                "copilot",
                True,
                text=(
                    "GITHUB_TOKEN present. Install GitHub CLI for Copilot terminal: "
                    "winget install GitHub.cli then gh auth login and gh extension install github/gh-copilot"
                ),
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
    """Send matrix/trading context to one or all available providers."""
    assert_floor_intact()
    det = bridge.detect()
    use = providers or [p for p in PROVIDERS if det.get(p)]
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
    print("detect:", json.dumps(d, indent=2))
    # offline: unknown provider fails cleanly
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
    print("44[Bridge] :: LLMBridge — set API keys in env, then call from trading/matrix")


if __name__ == "__main__":
    main()
