# Format Super-Router — Voyage / Voyman Pages

## Page 1 — Voyage (path through the system)

Goal: one meaning, many surfaces.

Path:
1. Intent/zone arrives (settings, persona doc, snap-in blocks, snapshot export)
2. Format Router chooses TOML | YAML | JSON | HCL
3. Adapter parses surface → canonical tree
4. Core uses canonical only
5. Optional serialize back to preferred surface
6. Residue records success/fail for (zone → format)

Voyage rule: never make humans edit the frankenstein mix. Route them.

## Page 2 — Voyman (navigation of format choice)

Voyman treats format choice like shell navigation:
- Center = canonical tree
- Shells = surface formats around it
- Walk = convert center → surface or surface → center
- Retrograde = round-trip test (surface → canonical → surface)

If round-trip loses meaning, residue marks failure and router demotes that pair.

## Default policy map

| Zone | Format |
|------|--------|
| foundation settings | TOML |
| nested workshop/persona docs | YAML |
| interchange / snapshots / API | JSON |
| repeated module/snap-in blocks | HCL |
| unknown | JSON |

## Growth

R_{n+1} = R_n strengthened by known wins + unknown experiments
(Δ_known format wins + Δ_unknown trials)

No mystical claim — usage residue only.
