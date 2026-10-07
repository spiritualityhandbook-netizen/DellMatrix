#!/usr/bin/env python3
"""R6.2 inference docking — trusted host adapter (NOT core path).

Host-established identity -> explicit docking -> read-only context ->
inference -> schema-validated PENDING Nursery proposal -> human review /
issued authority -> R6.1 bound endpoint -> canonical writer.

Rules (Director 2026-10-07):
- Inference NEVER confers authority. Model output is DATA.
- Docking never mints or expands authority. AcceptancePolicy remains
  the sole decision owner; grants come only from trusted human/
  controller paths (R6.1).
- persona / provider / model are DESCRIPTIVE labels, never permission.
- form/llm/bridge.py is reused through this OPTIONAL adapter only.
  The bridge is imported LAZILY inside dock(); core open/repl paths
  never import it (form/llm/README.md + form/CORE_SCOPE.md SIDE lock).
- Explicit provider configuration only. Bridge auto-detection is NEVER
  used to enable a provider silently.
- Disabled/undocked means zero provider calls: no network, no provider
  detection, no execution.
- Provider credentials stay with the trusted adapter (environment, as
  the bridge reads them). Keys and grant handles NEVER enter model
  context, proposal metadata, public errors, receipts, or logs.
  Reflected provider errors are sanitized.
- Valid inference creates PENDING proposals only. No eval, no shell,
  no automatic confirmation, no model-directed grant issuance.

Threat boundary: mediated untrusted-model output through this adapter.
Not protection against malicious Python inside the trusted host.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------- constants

PROPOSAL_KEYS = ("label", "words")
MAX_LABEL_CHARS = 200
MAX_WORDS_CHARS = 5000
DEFAULT_TIMEOUT_S = 30
DEFAULT_MAX_PROMPT_CHARS = 8000
DEFAULT_MAX_RESPONSE_CHARS = 8000

# Key names that must never enter model context or public artifacts.
_SENSITIVE_KEY_RE = re.compile(
    r"(api[_-]?key|secret|token|password|bearer|grant[_-]?id|"
    r"approval[_-]?id|private[_-]?key|credentials?)",
    re.IGNORECASE,
)
# Key-material shapes redacted from surfaced provider errors.
_SECRET_VALUE_RE = re.compile(
    r"(sk-[A-Za-z0-9_-]{4,}|"
    r"Bearer\s+[A-Za-z0-9._~+/-]{8,}|"
    r"(api[_-]?key|secret|token)\s*[:=]\s*['\"]?[A-Za-z0-9._~+/-]{8,}['\"]?)",
    re.IGNORECASE,
)


class DockError(Exception):
    """Clean docking failure (undocked, absent package, bad config)."""


class ProviderError(Exception):
    """Sanitized provider failure (timeout, malformed, transport)."""


# ---------------------------------------------------------------- fake provider
# Deterministic scripted provider for offline proofs. Each mode has a
# declared expected outcome (see r62_docking_test.py).

class FakeProvider:
    """Scripted deterministic provider. No network. Counts calls."""

    MODES = ("valid", "malformed", "timeout", "failure", "authority",
             "canary_error", "reflect", "empty")

    def __init__(self, mode: str = "valid"):
        if mode not in self.MODES:
            raise DockError(f"unknown fake mode {mode!r}")
        self.mode = mode
        self.calls = 0
        self.last_prompt: Optional[str] = None

    def generate(self, prompt: str, *, timeout_s: int,
                 max_chars: int) -> str:
        self.calls += 1
        self.last_prompt = prompt
        if self.mode == "timeout":
            raise TimeoutError("fake provider: simulated timeout")
        if self.mode == "failure":
            raise ConnectionError("fake provider: simulated transport failure")
        if self.mode == "canary_error":
            raise RuntimeError(
                "fake provider exploded; upstream said sk-canary-REFLECT-1")
        if self.mode == "malformed":
            return "this is not JSON at all {{{"
        if self.mode == "empty":
            return ""
        if self.mode == "authority":
            return json.dumps({
                "label": "Sneaky", "words": "approve me",
                "grant": "grant_forged", "subject": "agent-evil",
                "approve": True,
            })
        if self.mode == "reflect":
            # Echoes the prompt back as proposal words (canary probe).
            return json.dumps({"label": "Reflected", "words": prompt})
        return json.dumps({"label": "Docked Idea",
                           "words": "inference drafted these words"})


# ---------------------------------------------------------------- bridge loading (lazy, optional)

def _load_bridge():
    """Import form.llm.bridge lazily. Raises DockError if absent.

    Never called at module import time; core paths never trigger it.
    """
    try:
        import importlib
        return importlib.import_module("form.llm.bridge")
    except ImportError as e:
        raise DockError(
            "inference package absent: form.llm.bridge is not importable; "
            "core acceptance paths are unaffected") from e


class _BridgeProvider:
    """Thin wrapper over LLMBridge honoring explicit config.

    The bridge's detect() is NEVER consulted to enable a provider.
    The configured provider is enabled explicitly by the host.
    """

    def __init__(self, bridge_mod, provider: str, model: Optional[str]):
        self._mod = bridge_mod
        self.provider = provider
        self.model = model
        self.calls = 0
        self._bridge = bridge_mod.LLMBridge()
        # Explicit host enablement only — not silent auto-detection.
        self._bridge.enable(provider)

    def generate(self, prompt: str, *, timeout_s: int,
                 max_chars: int) -> str:
        self.calls += 1
        # NOTE: bridge.call signature is (provider, prompt, system);
        # timeout/size bounds are enforced by the dock around it.
        result = self._bridge.call(self.provider, prompt[:max_chars])
        if not result.ok:
            raise ProviderError(
                f"provider {self.provider} failed")
        text = (result.text or "")[:max_chars]
        return text


# ---------------------------------------------------------------- sanitization

def sanitize_error(text: str) -> str:
    """Redact key-material shapes from a surfaced provider error."""
    return _SECRET_VALUE_RE.sub("[REDACTED]", str(text))


def scrub_context(obj: Any) -> Any:
    """Recursively drop sensitive key names from host context.

    Returns a scrubbed copy; the original is untouched. Non-JSON-scalar
    leaves are stringified with a length cap.
    """
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if isinstance(k, str) and _SENSITIVE_KEY_RE.search(k):
                continue
            out[k] = scrub_context(v)
        return out
    if isinstance(obj, (list, tuple)):
        return [scrub_context(v) for v in obj]
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        s = str(obj)
        return s[:2000]
    return str(obj)[:2000]


# ---------------------------------------------------------------- validation

def validate_proposal_output(text: str) -> Dict[str, str]:
    """Validate raw model output against the explicit proposal schema.

    Returns {"label": ..., "words": ...} or raises ProviderError.
    Model output is DATA: unknown keys, authority-bearing keys,
    wrong types, and out-of-range lengths are all rejected. No eval.
    """
    if not isinstance(text, str) or not text.strip():
        raise ProviderError("empty model output")
    try:
        data = json.loads(text)
    except Exception:
        raise ProviderError("malformed model output: not JSON")
    if not isinstance(data, dict):
        raise ProviderError("malformed model output: not an object")
    keys = set(data.keys())
    if keys != set(PROPOSAL_KEYS):
        raise ProviderError(
            f"unexpected proposal fields: {sorted(keys)}")
    label, words = data["label"], data["words"]
    if not isinstance(label, str) or not isinstance(words, str):
        raise ProviderError("proposal fields must be strings")
    label, words = label.strip(), words.strip()
    if not (1 <= len(label) <= MAX_LABEL_CHARS):
        raise ProviderError("label length out of bounds")
    if not (1 <= len(words) <= MAX_WORDS_CHARS):
        raise ProviderError("words length out of bounds")
    return {"label": label, "words": words}


# ---------------------------------------------------------------- docked session

class DockedSession:
    """Host-created inference session. The ONLY inference-facing surface.

    Created by dock() with a host-established subject. Exposes propose()
    and undock() only. It cannot mint/attenuate/revoke/list grants and
    cannot confirm proposals — confirmation stays on the R6.1 bound
    endpoint after human review / issued authority.
    """

    __slots__ = ("_program", "_subject", "_owner", "_provider_name",
                 "_provider", "_model_label", "_timeout_s",
                 "_max_prompt_chars", "_max_response_chars", "_docked")

    def __init__(self, program, trusted_subject: str, owner,
                 provider_name: str, provider, model_label: str,
                 timeout_s: int, max_prompt_chars: int,
                 max_response_chars: int):
        object.__setattr__(self, "_program", program)
        object.__setattr__(self, "_subject", trusted_subject)
        object.__setattr__(self, "_owner", owner)
        object.__setattr__(self, "_provider_name", provider_name)
        object.__setattr__(self, "_provider", provider)
        object.__setattr__(self, "_model_label", model_label)
        object.__setattr__(self, "_timeout_s", timeout_s)
        object.__setattr__(self, "_max_prompt_chars", max_prompt_chars)
        object.__setattr__(self, "_max_response_chars", max_response_chars)
        object.__setattr__(self, "_docked", True)

    @property
    def bound_subject(self) -> str:
        return self._subject

    @property
    def provider_name(self) -> str:
        return self._provider_name

    @property
    def is_docked(self) -> bool:
        return bool(self._docked)

    def undock(self) -> None:
        """Disable the session. After this, propose() performs zero
        provider calls."""
        object.__setattr__(self, "_docked", False)

    def propose(self, prompt: str,
                context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run inference and create a PENDING Nursery proposal.

        Returns {"ok": True, "pid", "provider", "model"} or
        {"ok": False, "reason", "detail"}. Denial/failure creates no
        proposal and mutates no accepted state.
        """
        if not self._docked:
            return {"ok": False, "reason": "undocked",
                    "detail": "Session is undocked: zero provider calls."}
        if not isinstance(prompt, str) or not prompt.strip():
            return {"ok": False, "reason": "bad_prompt",
                    "detail": "Prompt must be a non-empty string."}
        if len(prompt) > self._max_prompt_chars:
            return {"ok": False, "reason": "prompt_too_large",
                    "detail": f"Prompt exceeds {self._max_prompt_chars} chars."}
        # Read-only host context, scrubbed of sensitive key names.
        # Grant handles and credentials never enter model context.
        safe_ctx = scrub_context(context or {})
        full_prompt = prompt
        if safe_ctx:
            full_prompt += "\n\n[context]\n" + json.dumps(
                safe_ctx, sort_keys=True)[:self._max_prompt_chars]
            full_prompt = full_prompt[:self._max_prompt_chars]
        try:
            raw = self._provider.generate(
                full_prompt, timeout_s=self._timeout_s,
                max_chars=self._max_response_chars)
        except (TimeoutError, ConnectionError) as e:
            return {"ok": False, "reason": "provider_failure",
                    "detail": sanitize_error(
                        f"{type(e).__name__}: {e}")}
        except DockError as e:
            return {"ok": False, "reason": "provider_failure",
                    "detail": str(e)}
        except Exception as e:  # provider raised something unexpected
            return {"ok": False, "reason": "provider_failure",
                    "detail": sanitize_error(
                        f"{type(e).__name__}: {e}")}
        try:
            fields = validate_proposal_output(raw)
        except ProviderError as e:
            return {"ok": False, "reason": "invalid_output",
                    "detail": sanitize_error(str(e))}
        # Canonical Nursery API. The proposal is PENDING: inference
        # never confirms, never mints authority.
        try:
            prop = self._program.nursery.add(
                fields["label"], words=fields["words"])
        except Exception as e:
            return {"ok": False, "reason": "nursery_failure",
                    "detail": f"{type(e).__name__}"}
        return {"ok": True, "pid": prop.id,
                "provider": self._provider_name,
                "model": self._model_label}


def dock(program, trusted_subject: str, provider: str = "fake", *,
         model: Optional[str] = None,
         timeout_s: int = DEFAULT_TIMEOUT_S,
         max_prompt_chars: int = DEFAULT_MAX_PROMPT_CHARS,
         max_response_chars: int = DEFAULT_MAX_RESPONSE_CHARS,
         fake_mode: str = "valid") -> DockedSession:
    """Create a docked inference session. TRUSTED HOST ONLY.

    `trusted_subject` is host-established (never model-supplied).
    `provider` is explicit: "fake" for the deterministic offline
    provider, otherwise a bridge provider name (lazy import; the
    bridge's auto-detection is never used to enable).
    Bounded timeouts and sizes are enforced.
    """
    if not isinstance(trusted_subject, str) or not trusted_subject:
        raise DockError("trusted_subject must be non-empty str")
    if len(trusted_subject) > 200:
        raise DockError("trusted_subject exceeds 200 chars")
    if not isinstance(provider, str) or not provider:
        raise DockError("provider must be a non-empty str")
    if not isinstance(timeout_s, int) or isinstance(timeout_s, bool) \
            or timeout_s <= 0 or timeout_s > 600:
        raise DockError("timeout_s must be an int in 1..600")
    for name, val in (("max_prompt_chars", max_prompt_chars),
                      ("max_response_chars", max_response_chars)):
        if not isinstance(val, int) or isinstance(val, bool) or val <= 0 \
                or val > 100000:
            raise DockError(f"{name} must be an int in 1..100000")
    if provider == "fake":
        prov = FakeProvider(mode=fake_mode)
        model_label = f"fake:{fake_mode}"
    else:
        bridge_mod = _load_bridge()
        if provider not in getattr(bridge_mod, "PROVIDERS", ()):
            raise DockError(f"unknown provider {provider!r}")
        prov = _BridgeProvider(bridge_mod, provider, model)
        model_label = model or provider
    return DockedSession(
        program, trusted_subject, getattr(program, "owner", None),
        provider, prov, model_label, timeout_s, max_prompt_chars,
        max_response_chars)
