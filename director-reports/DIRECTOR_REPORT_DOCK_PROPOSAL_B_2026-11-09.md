# DIRECTOR REPORT — DOCK PROPOSAL B (Q-LD.1 / Q-LD.2): failure transparency + fence tolerance + session response view

Circuit: Proposal B, authorized 2026-11-08 (08:08 ruling Q-LD.1/Q-LD.2) as a
separate circuit after the snapshot work; restated as the NEXT authorized
circuit in the Director's 2026-11-09 07:39 ruling. Origin: two gaps proven
live in the 2026-11-08 Gemini demonstration — the dock discarded the bridge
error cause (surfacing only "ProviderError") and its parser accepted bare
JSON only, while the ask path never stated the JSON contract.

Disposition requested: certification of the Proposal B scope (Q-LD.5).

## Defects -> repairs (suite form/dock_proposal_b_test.py)

- **D1 — bridge cause discarded.** Provider failures through the product
  bridge surfaced the literal type name only. REPAIR: ProviderError /
  DockError causes now surface through the existing sanitize_error
  boundary (protected values, grant handles, and secret shapes redacted);
  raw transport exceptions (TimeoutError / ConnectionError / unexpected)
  remain bounded to their type-name category — an arbitrary provider
  object's message is never surfaced raw. Canary test: a secret-shaped
  value planted in the bridge cause never appears in the receipt, while
  the sanitized cause ("503") does.
- **D2 — fence intolerance.** Validators rejected any non-bare reply.
  REPAIR: exactly one complete fenced block is unwrapped and the strict
  schema is enforced after unwrapping; extra prose, extra objects, and
  multiple blocks are still rejected.
- **D3 — schema never stated.** propose() asked without stating the
  output contract. REPAIR: the ask prompt now states the JSON schema up
  front (two neighbour suites updated deliberately for the changed
  prompt: r62 C11 surface list, p4 evidence_prompt_hash).
- **D4 — no response visibility.** REPAIR: DockedSession.last_response_view()
  returns a session-only {kind, text, truncated} view with truncation
  disclosed. Durable storage is unchanged — digest + parsed fields only;
  NO persistent raw-response storage (per the 07:39 restatement).

## Evidence

- Failing-first at base 693fa77 (commit 684c116 lineage): **10/17** —
  7 defect checks fail, 10 controls pass. Post-repair: **17/17**.
- Mutant (fence unwrap disabled): **13/17** — killed, reverted by
  inverse edit.
- Neighbours at candidate head: r62_docking, p4_sd1, pp4_bimo_dock,
  dock_transport, p5_sd2, track_c_dock_verbs, p7_sd4, p8_sd5,
  snapshot_retrieval, snapshot_revalidation — all PASS.
- Regression x3 at candidate head 081add9: **262/262 TERMINAL GREEN x3**
  (fwd / --twice / --order rev). Disclosure: a VM replacement killed the
  first chain mid-leg-2 (leg 1 terminal GREEN preserved; legs 2-3 re-run
  in a recovery chain, both terminal GREEN). Logs:
  evidence/dock-proposal-b/ (chain_fixed.log + chain_legs23.log +
  fixed_leg1-3.log). Chains launched with SIGINT/SIGQUIT reset per the
  Q-SNAP.1 operational law. Suite registered in form/regress.py
  (261 -> 262).
- LIVE acceptance (real Gemini, gemini-3-flash-preview, vault connector;
  script at evidence/dock-proposal-b/acceptance_b.py, owner DOCKB6BC0A7):
  synthesize over two seeded ideas returned ok and landed ONE PENDING
  proposal ("Nocturnal Solar Biosphere", origin
  dock:host:acceptance-b:gemini:gemini-3-flash-preview);
  last_response_view() present ({kind, text, truncated: false}, 926
  chars); the raw model response does NOT appear in any durable state
  file for the owner (leak check negative); a forced provider failure
  (nonexistent model) surfaced {"ok": false, "reason":
  "provider_failure", "detail": "ConnectionError"} — the bounded
  type-name category for the host-adapter seam, as designed. The live
  reply happened to be bare JSON; fence acceptance is proven
  deterministically by the suite (D2), not by this sample.

## Boundaries

Proposal B changes no authority: proposals remain PENDING-only, confirm
stays on the human endpoint, durable records keep digest/parsed fields.
Q-SNAP.3 remains deferred per the 07:39 ruling; nothing here touches it.

## Anticipated probes

- "Why do transport exceptions get only a type name while bridge errors
  get a cause?" — The bridge is product code raising product error types
  whose messages are ours to sanitize; an arbitrary provider object is
  untrusted, and its message is data, not diagnostics. The category is
  the bounded surface for that seam (proven live above).
- "Session view — can it leak into persistence via _persist_state?" —
  The view reads the in-memory _last_response slot only; the durable
  evidence record was checked in the live run (raw absent from state
  files) and the suite asserts the storage contract.

## Questions for the Director

- **Q-LD.5:** certification of the Proposal B scope (D1-D4 as bounded
  above) on this evidence.
