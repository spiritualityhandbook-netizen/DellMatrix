#!/usr/bin/env python3
"""C8 EmbedBind (MWL 153): Dell 47 Embed lights up only behind a
host-established embedding-provider binding.

Contract (plan SS14.3 C8 + SS12.36 + Ace ruling 2026-11-10):
- Unbound: 47[Embed] refuses embed_unavailable, representation
  "none" - byte-identical to the pre-EmbedBind behavior.
- Binding is HOST-side (bind_embedder, the dock() precedent): atoms
  use bindings, hosts make them. The binding is runtime-only state
  on the Program; it is never persisted.
- Bind PROBES the transport (entitlement test, SS12.36): a provider
  whose embedding endpoint cannot answer does not bind.
- Bound: 47[Embed]:: <text> embeds the segment-label text and the
  receipt (program.last_core_i) reports the ACTUAL provider, model,
  vector space ("<provider>:<model>:<dim>") and the vector itself.
- No silent downgrade: the pedagogy bag (inspire_pack.embed_bag)
  is never served as a provider embedding (SS31.2).
"""
from __future__ import annotations

import os

from form.open import open_program
from form.mandell.executor import execute_seed
from form.dell_matrix.embed_bind import bind_embedder, unbind_embedder


def smoke() -> bool:
    print("=== C8 EMBEDBIND ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" | {detail}" if detail and not ok else ""))
        r.append(bool(ok))

    # 1-2. Unbound behavior is exactly the historical refusal.
    p = open_program("EbUnbound")
    rec("starts_unbound", getattr(p, "embed_binding", None) is None)
    em = execute_seed(p, "47[Embed]")
    rec("unbound_bare_refuses", em.get("ok") is False and em.get("error") == "embed_unavailable")
    em = execute_seed(p, "47[Embed]:: hello world")
    rec("unbound_labeled_refuses", em.get("ok") is False and em.get("error") == "embed_unavailable")
    rec("unbound_receipt_shape", p.last_core_i.get("representation") == "none" and p.last_core_i.get("provider") == "")

    # 3. Host binds the deterministic fake embedder (probe passes).
    b = bind_embedder(p, "fake")
    rec("bind_fake_ok", b.get("ok") is True and getattr(p, "embed_binding", None) is not None, str(b))

    # 4. Bound embed: receipt carries actual identity + vector.
    em = execute_seed(p, "47[Embed]:: the quick brown fox")
    ci = p.last_core_i
    rec("bound_embed_ok", em.get("ok") is True and ci.get("ok") is True, str(em))
    rec("receipt_identity", ci.get("provider") == "fake" and bool(ci.get("model")) and ci.get("representation") == "vector", str(ci))
    vec = ci.get("vector") or []
    rec("receipt_vector_space", ci.get("vector_space") == f"fake:{ci.get('model')}:{len(vec)}" and ci.get("dim") == len(vec) and len(vec) > 0, str(ci.get("vector_space")))

    # 5-6. Deterministic per text; distinct across texts.
    execute_seed(p, "47[Embed]:: the quick brown fox")
    rec("deterministic", p.last_core_i.get("vector") == vec)
    execute_seed(p, "47[Embed]:: a completely different sentence")
    rec("distinct_text_distinct_vector", p.last_core_i.get("vector") != vec)

    # 7. Bound but no text: named refusal, not an empty embedding.
    em = execute_seed(p, "47[Embed]")
    rec("bound_no_text_refuses", em.get("ok") is False and em.get("error") == "embed_no_text", str(em))

    # 8. Unbind restores the historical refusal.
    unbind_embedder(p)
    em = execute_seed(p, "47[Embed]:: hello again")
    rec("unbind_restores_refusal", em.get("ok") is False and em.get("error") == "embed_unavailable")

    # 9. Entitlement failure: gemini with no API key in the
    # environment must NOT bind (probe fails honestly), and the
    # program stays unbound. Env is restored whatever happens.
    saved = {k: os.environ.pop(k, None) for k in ("GOOGLE_API_KEY", "GEMINI_API_KEY", "AISTUDIO_API_KEY")}
    try:
        q = open_program("EbNoKey")
        b = bind_embedder(q, "gemini")
        rec("bind_without_entitlement_refused", b.get("ok") is False and getattr(q, "embed_binding", None) is None, str(b))
        em = execute_seed(q, "47[Embed]:: hello")
        rec("failed_bind_stays_unbound", em.get("ok") is False and em.get("error") == "embed_unavailable")
    finally:
        for k, v in saved.items():
            if v is not None:
                os.environ[k] = v

    # 10. No pedagogy-bag downgrade: the bound receipt's vector is
    # the provider transport's, not inspire_pack's bag vector.
    from form.dell_matrix.inspire_pack import embed_bag, build_vocab
    toks = "the quick brown fox".split()
    bag = embed_bag(toks, build_vocab(["the quick brown fox"]))
    z = open_program("EbNoBag")
    bind_embedder(z, "fake")
    execute_seed(z, "47[Embed]:: the quick brown fox")
    rec("no_bag_fallback", list(bag) != list(z.last_core_i.get("vector") or []))

    # 11. Isolation: binding is per-program, never global.
    w = open_program("EbOther")
    em = execute_seed(w, "47[Embed]:: hello")
    rec("binding_not_global", em.get("ok") is False and em.get("error") == "embed_unavailable")

    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)
