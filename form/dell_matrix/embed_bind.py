"""C8 EmbedBind — host-side embedding-provider binding (MWL 153).

Dell 47 [Embed] needs an embedding provider/model (plan SS12.36):
a vector database is not an embedding model, and a docked Psalm's
generative access does not by itself prove embedding entitlement.

The binding follows the dock() precedent: HOSTS make bindings,
atoms use them. `bind_embedder` establishes the binding on a
Program after PROBING the provider's embedding transport - the
probe is the entitlement test, and a provider whose endpoint
cannot answer does not bind. The binding is runtime-only state
(`program.embed_binding`); it is deliberately NOT persisted, so a
restart can never resurrect a dead provider as "bound" (the
C8.Roster liveness rule applied to bindings).

Ace's provider ruling (2026-11-10): the embedder is whichever
provider the host binds - provider-agnostic; Gemini is today's
expected binding. Nothing here auto-detects or guesses a provider.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from form.llm.bridge import LLMBridge, PROVIDERS, EmbedResult

_PROBE_TEXT = "embedbind entitlement probe"


def bind_embedder(program: Any, provider: str, model: Optional[str] = None,
                  *, bridge: Optional[LLMBridge] = None) -> Dict[str, Any]:
    """Probe the provider's embedding endpoint; bind only on proof.

    Returns {"ok": True, provider, model, dim, vector_space} on
    success (model/dim are the ACTUAL values the probe reported),
    or {"ok": False, error, provider} leaving the program unbound.
    """
    provider = (provider or "").lower().strip()
    if provider != "fake" and provider not in PROVIDERS:
        return {"ok": False, "error": f"unknown provider {provider}",
                "provider": provider}
    br = bridge or LLMBridge()
    probe = br.embed(provider, _PROBE_TEXT, model=model)
    if not probe.ok:
        return {"ok": False, "error": probe.error or "embed_probe_failed",
                "provider": provider}
    binding = {"provider": provider, "model": probe.model or model or ""}
    program.embed_binding = binding
    return {"ok": True, **binding, "dim": len(probe.vector),
            "vector_space": f"{provider}:{binding['model']}:{len(probe.vector)}"}


def unbind_embedder(program: Any) -> None:
    program.embed_binding = None


def embed_text(program: Any, text: str, *,
               bridge: Optional[LLMBridge] = None) -> Optional[EmbedResult]:
    """Embed `text` through the program's binding; None if unbound."""
    binding = getattr(program, "embed_binding", None)
    if not binding:
        return None
    br = bridge or LLMBridge()
    return br.embed(binding["provider"], text,
                    model=binding.get("model") or None)
