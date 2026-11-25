> STATUS: IN USE — describes live code in form/ at commit 11933da. Doc verified against code 2026-10-30.

# Matrix profiles

Same runtime (`form/`). Different **owners / state**.

| Profile | Launch | State |
|---------|--------|-------|
| DEV / Operator | `python launch.py` | `form/state/program_Operator.json` |
| Ace (personal) | `python launch.py Ace` | `program_Ace.json` |
| Worldwide | `python launch.py Worldwide` | `program_Worldwide.json` |
| Blank handoff | `python launch.py Friend` or blank_cube pack | no Ace lore |

### Worldwide → DEV (development)

The automatic planter is **gone**: `form/worldwide/plant_to_dev.py` was removed in master-plan P11. What remains is the catalog, `form/worldwide/WORLDWIDE_IDEAS.py`. To develop a catalog idea today, create and confirm it manually in a session (Worldwide or DEV) through the normal create → grow → confirm path; there is no one-command plant/import step in this tree.

See `form/MATRIX_ARCHITECTURE.md`.
