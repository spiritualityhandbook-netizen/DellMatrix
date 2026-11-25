# Connector-to-Bridge Adapter — Design Proposal (2026-11-11)

Routed by the Director (mail 1a1ca4de19ec3aad): "narrow
connector-to-bridge adapter design, no credential copying or
embedding secret in URL/log/receipt. Prefer provider-side
authorized embedding action and bounded vector result over
injecting raw key into runtime environment. Probe actual access,
explicit identity and failure; proposal first."

## Problem

C8 EmbedBind (merged, PR #378) gives DellMatrix an embedding
transport (`LLMBridge.embed`) that reads the Gemini API key from
the process environment. In this host, the key exists ONLY inside
the registered `custom.gemini` connection, which is surrogate-only
by design: callers build URLs with a credential surrogate and the
platform swaps in the real key on approved egress. The key cannot
and must not be copied into the runtime environment.

Proven access (2026-11-11): through the connector's own helper
machinery (`gemini_generate.py` pattern), the registered key
enumerates `gemini-embedding-001` and a live `:embedContent` call
returned a real 3072-dim finite vector. The connector CAN supply
the operation; the gap is purely the bridge's access path.

## Proposal

Two halves, one on each side of the credential boundary:

1. CONNECTOR SIDE (outside the repo, in the connector's bin/,
   beside gemini_generate.py): a `gemini_embed.py` helper with the
   same surrogate discipline — text on stdin, one embedContent
   POST, bounded JSON on stdout: {ok, model (actual, from the
   request), dim, vector} or {ok: false, error}. The surrogate URL
   is never printed or logged; responses are size-bounded; the
   vector is data, not a secret, and is returned whole (3072
   floats is ~25 KB — bounded and acceptable).

2. BRIDGE SIDE (in-repo, form/llm/bridge.py): an opt-in fallback
   for the gemini/aistudio transports. When the API-key env is
   absent AND the host sets DELLMATRIX_GEMINI_CONNECTOR_HELPER to
   the helper's path, `embed()` (and, in a second step,
   `dispatch()`) invoke the helper as a subprocess: JSON request
   on stdin, bounded JSON response on stdout, hard timeout.
   Receipts name the transport explicitly (provider "gemini",
   via "connector-helper", actual model). Failure names are
   distinct and honest: connector_helper_missing,
   connector_helper_failed, connector_helper_timeout,
   connector_helper_bad_response. When neither env key nor helper
   is configured, behavior is exactly today's named refusal.

The binding layer needs no change: bind_embedder's probe exercises
whichever transport answers, so a successful bind through the
helper IS the entitlement proof, end-to-end in-program.

## Alternatives considered and rejected

- Raw key into the runtime env: rejected by the directive and by
  the connector's surrogate-only design.
- form/ importing the platform's dynamic_credentials module:
  couples repository code to host-platform internals and breaks
  on any other host; the repo must stay host-agnostic.
- A standing local proxy service: no such service exists; adds a
  daemon to supervise for a request/response-shaped problem.

## Proof plan (when authorized as a circuit)

- Failing-first suite with a STUB helper (a tiny script emitting
  canned JSON): bind succeeds through the stub, receipt identity
  names the connector-helper transport, helper failure modes each
  refuse by name, and the no-config path stays today's refusal.
- Mutants: helper path silently falling back to a local fake
  (must go red); helper error swallowed into ok (must go red).
- Live end-to-end: with the real helper configured,
  bind_embedder(program, "gemini") probes successfully and
  47[Embed]:: <text> returns a receipt naming gemini /
  gemini-embedding-001 / dim 3072 — converting EmbedBind's
  in-program Gemini path from UNKNOWN to proven, without any key
  entering the DellMatrix process.
- Regression x3 + exact-head CI, standard gates.

## Scope limits

Embedding only in step 1 (the C8 need). Generative dispatch
through the helper is a separable step 2, proposed only if a
circuit needs a docked Gemini on a key-less host. No vector
storage or consumers (C5 scope, unchanged).

Questions for the Director:
1. Helper location: connector bin/ (host-side, outside the repo)
   as proposed, or does he want the helper contract specified
   in-repo with the binary supplied per-host?
2. Env var name and receipt transport label ("connector-helper")
   — confirm or rename before the build circuit opens.
