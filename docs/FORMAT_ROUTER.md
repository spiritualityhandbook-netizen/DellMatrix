# Format Super-Router

## Idea
Combine TOML + YAML + JSON + HCL by routing, not by inventing one mixed syntax.

## Canonical core
Always a JSON-compatible tree in memory.

## Surfaces
- TOML — settings
- YAML — nested docs / personas / workshops
- JSON — interchange / snapshots
- HCL — repeated blocks / snap-ins / modules

## Learning
Residue counts wins/fails per (zone, format).
Router prefers higher score over bare default when enough signal exists.

## Files
- `src/core/format_router.js`
- `docs/FORMAT_VOYAGE.md`
- `docs/FORMAT_ROUTER.md`

## Note on parsers
JSON parse/serialize is live.
TOML/YAML/HCL full parse can attach offline libs later; router policy and residue work now.
