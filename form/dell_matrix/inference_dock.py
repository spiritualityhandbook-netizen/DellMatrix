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

    Uses dispatch() — NEVER call() — so no provider auto-detection
    runs during configured dispatch. Explicit model/timeout/read-bound
    reach the actual provider request. The ACTUAL model identity comes
    back in result.meta and is reported truthfully by the dock.
    """

    def __init__(self, bridge_mod, provider: str, model: Optional[str]):
        self._mod = bridge_mod
        self.provider = provider
        self.model = model
        self.calls = 0
        self.last_actual_model: Optional[str] = None
        self._bridge = bridge_mod.LLMBridge()
        # Explicit host enablement only — not silent auto-detection.
        self._bridge.enable(provider)

    def generate(self, prompt: str, *, timeout_s: int,
                 max_chars: int) -> str:
        self.calls += 1
        # max_chars is chars; the transport read bound is bytes.
        max_bytes = max_chars * 4
        result = self._bridge.dispatch(
            self.provider, prompt, "",
            model=self.model, timeout=timeout_s, max_bytes=max_bytes)
        if not result.ok:
            raise ProviderError(
                f"provider {self.provider} failed")
        self.last_actual_model = (result.meta or {}).get("model")
        # NOTE: no silent truncation here. The dock enforces the
        # response bound by REJECTING oversized responses before
        # parsing (directive: slicing after an unlimited read, or
        # silent truncation, is insufficient).
        return result.text or ""


# ---------------------------------------------------------------- sanitization

def sanitize_error(text: str, protected: frozenset = frozenset()) -> str:
    """Redact key-material shapes AND known protected values from a
    surfaced provider error."""
    s = str(text)
    for val in protected:
        if val and val in s:
            s = s.replace(val, "[REDACTED]")
    return _SECRET_VALUE_RE.sub("[REDACTED]", s)


# Recognized handle format (canonical issued handles look like this).
_HANDLE_RE = re.compile(r"grant_[0-9a-f]{32}")

# Environment names whose values are provider credentials. The trusted
# host reads these values for redaction; they are never logged,
# exposed to agents, or placed in model context.
_CREDENTIAL_ENV_NAMES = (
    "GOOGLE_API_KEY", "GEMINI_API_KEY", "AISTUDIO_API_KEY",
    "XAI_API_KEY", "ANTHROPIC_API_KEY", "GITHUB_TOKEN", "GH_TOKEN",
    "OLLAMA_API_KEY",
)


def protected_values(program) -> frozenset:
    """Trusted-host knowledge of protected material (AMEND 2026-10-07).

    Covers EXACTLY:
    - canonical issued grant handles (this session's policy)
    - active approval IDs (this session's policy)
    - configured provider credential values (environment)
    - recognized handle formats are matched by _HANDLE_RE separately.

    This is a value list for redaction, computed by trusted host code.
    It is never exposed to agents, never logged, and never placed in
    model context. It does NOT claim detection of arbitrary unknown
    secrets.
    """
    vals = set()
    try:
        policy = getattr(program, "acceptance_policy", None)
        if policy is not None:
            for gid in getattr(policy, "_issued_grants", {}):
                if isinstance(gid, str) and gid:
                    vals.add(gid)
            for aid in getattr(policy, "_issued_approvals", {}):
                if isinstance(aid, str) and aid:
                    vals.add(aid)
    except Exception:
        pass
    import os as _os
    for name in _CREDENTIAL_ENV_NAMES:
        v = _os.environ.get(name, "").strip()
        if v:
            vals.add(v)
    return frozenset(vals)


def contains_protected(text: str, protected: frozenset) -> bool:
    """True if text carries protected material: a known protected
    value or a recognized handle format."""
    s = str(text)
    for val in protected:
        if val and val in s:
            return True
    return bool(_HANDLE_RE.search(s))


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


# ---------------------------------------------------------------- context validation (AMEND 2026-10-07)
# Bounded processing: depth, node count, and combined size are
# validated BEFORE generation. Malformed/cyclic/excessive context is
# rejected with a stable receipt: no provider call, no proposal.

_MAX_CONTEXT_DEPTH = 10
_MAX_CONTEXT_NODES = 1000
_MAX_CONTEXT_CHARS = 100000


def validate_context(context: Any) -> Dict[str, Any]:
    """Validate host context. Returns a scrubbed plain-dict copy.

    Raises DockError on: non-dict input (None is explicitly mapped to
    {}), cycles, depth > 10, nodes > 1000, serialized size > 100000
    chars, or scrub/serialize failure. Valid JSON scalar types are
    preserved.
    """
    if context is None:
        return {}
    if not isinstance(context, dict):
        raise DockError(
            f"bad_context: context must be a dict or None, "
            f"got {type(context).__name__}")
    seen: set = set()
    count = [0]

    def _walk(node: Any, depth: int) -> Any:
        # Cycle detection BEFORE recursion (no RecursionError).
        if isinstance(node, (dict, list, tuple)):
            nid = id(node)
            if nid in seen:
                raise DockError("bad_context: cyclic context")
            seen.add(nid)
            try:
                if depth > _MAX_CONTEXT_DEPTH:
                    raise DockError(
                        f"bad_context: depth exceeds {_MAX_CONTEXT_DEPTH}")
                count[0] += 1
                if count[0] > _MAX_CONTEXT_NODES:
                    raise DockError(
                        f"bad_context: nodes exceed {_MAX_CONTEXT_NODES}")
                if isinstance(node, dict):
                    out = {}
                    for k, v in node.items():
                        if not isinstance(k, str):
                            raise DockError(
                                "bad_context: non-string dict key")
                        if _SENSITIVE_KEY_RE.search(k):
                            continue
                        out[k] = _walk(v, depth + 1)
                    return out
                return [_walk(v, depth + 1) for v in node]
            finally:
                seen.discard(nid)
        if isinstance(node, (str, int, float, bool)) or node is None:
            return node
        s = str(node)
        return s[:2000]

    try:
        clean = _walk(context, 0)
    except DockError:
        raise
    except Exception as e:
        raise DockError(
            f"bad_context: processing failed ({type(e).__name__})")
    try:
        serial = json.dumps(clean, sort_keys=True)
    except Exception as e:
        raise DockError(
            f"bad_context: not JSON-serializable ({type(e).__name__})")
    if len(serial) > _MAX_CONTEXT_CHARS:
        raise DockError(
            f"bad_context: serialized size exceeds {_MAX_CONTEXT_CHARS}")
    return clean


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

        Enforcement order (AMEND 2026-10-07):
        docked? -> prompt bound -> context validated/bounded ->
        protected-input rejected -> provider call ->
        response bound enforced -> protected-output rejected ->
        schema validated -> Nursery.add (pending only).

        Returns {"ok": True, "pid", "provider", "model"} (model is the
        ACTUAL model identity reported by the transport) or
        {"ok": False, "reason", "detail"} with bounded public
        error messages. Denial/failure creates no proposal and mutates
        no accepted state.
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
        # Bounded context validation BEFORE generation. Malformed /
        # cyclic / excessive context -> stable receipt, no provider
        # call, no proposal. Failures stay inside the failure boundary.
        try:
            safe_ctx = validate_context(context)
        except DockError as e:
            return {"ok": False, "reason": "bad_context",
                    "detail": str(e)}
        full_prompt = prompt
        if safe_ctx:
            full_prompt += "\n\n[context]\n" + json.dumps(
                safe_ctx, sort_keys=True)
            if len(full_prompt) > self._max_prompt_chars:
                return {"ok": False, "reason": "prompt_too_large",
                        "detail": "Prompt+context exceeds bound."}
        # Protected-material screen on the exact outbound text.
        # Key-name filtering alone is insufficient: values (issued
        # handles, credential values, recognized formats) are checked.
        prot = protected_values(self._program)
        if contains_protected(full_prompt, prot):
            return {"ok": False, "reason": "protected_input",
                    "detail": "Prompt/context carries protected material; "
                             "rejected before provider call."}
        try:
            raw = self._provider.generate(
                full_prompt, timeout_s=self._timeout_s,
                max_chars=self._max_response_chars)
        except (TimeoutError, ConnectionError) as e:
            return {"ok": False, "reason": "provider_failure",
                    "detail": sanitize_error(
                        f"{type(e).__name__}", prot)}
        except DockError as e:
            return {"ok": False, "reason": "provider_failure",
                    "detail": sanitize_error(str(e), prot)}
        except Exception as e:  # provider raised something unexpected
            return {"ok": False, "reason": "provider_failure",
                    "detail": sanitize_error(
                        f"{type(e).__name__}", prot)}
        # Response bound enforced by REJECTION before parsing. Silent
        # truncation is not accepted.
        if not isinstance(raw, str):
            return {"ok": False, "reason": "invalid_output",
                    "detail": "Provider returned non-text."}
        if len(raw) > self._max_response_chars:
            return {"ok": False, "reason": "response_too_large",
                    "detail": f"Response exceeds {self._max_response_chars} "
                             "chars; rejected before parsing."}
        # Protected-material screen on provider output BEFORE parsing
        # and before Nursery.add.
        if contains_protected(raw, prot):
            return {"ok": False, "reason": "protected_output",
                    "detail": "Provider output carries protected material; "
                             "rejected before proposal creation."}
        try:
            fields = validate_proposal_output(raw)
        except ProviderError as e:
            return {"ok": False, "reason": "invalid_output",
                    "detail": sanitize_error(str(e), prot)}
        # Canonical Nursery API. The proposal is PENDING: inference
        # never confirms, never mints authority.
        try:
            prop = self._program.nursery.add(
                fields["label"], words=fields["words"])
        except Exception as e:
            return {"ok": False, "reason": "nursery_failure",
                    "detail": f"{type(e).__name__}"}
        # Truthful model identity: the ACTUAL model reported by the
        # transport, not merely the requested label.
        actual_model = getattr(self._provider, "last_actual_model", None)
        return {"ok": True, "pid": prop.id,
                "provider": self._provider_name,
                "model": actual_model or self._model_label}


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
