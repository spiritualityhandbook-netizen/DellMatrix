> STATUS: IN USE — describes live code in form/ at commit 11933da. Doc verified against code 2026-10-30.

# Persist patch note — idea detail + goals

detail+goals persist applied in serialize/load of form/persist.py

- **What:** an idea's `detail` text and `goals` list are part of the persisted program state, not display-only data.
- **Where:** `form/persist.py` — serialize writes each idea row with `"detail"` and `"goals"` fields and load restores them. The save/load/checkpoint functions themselves live in `form/persist_rest.py` and are re-exported through `form/persist.py`.
- **Why:** the strong-idea law (`form/IDEA_LAW.md`) treats detail and goals as part of an idea's identity; dropping them on save would silently weaken confirmed ideas.
- **When:** on every program save and load (persist v7).
