# Matrix profiles

Same runtime (`form/`). Different **owners / state**.

| Profile | Launch | State |
|---------|--------|-------|
| DEV / Operator | `python launch.py` | `form/state/program_Operator.json` |
| Ace (personal) | `python launch.py Ace` | `program_Ace.json` |
| Worldwide | `python launch.py Worldwide` | `program_Worldwide.json` |
| Blank handoff | `python launch.py Friend` or blank_cube pack | no Ace lore |

### Worldwide → DEV (development)

Plant world ideas into Worldwide **and** import them into the DEV Operator matrix:

```bash
python -m form.worldwide.plant_to_dev
python -m form.worldwide.plant_to_dev --dev-only
```

Catalog: `form/worldwide/WORLDWIDE_IDEAS.py`  
DEV session then holds those ideas with detail + goals for active development.

See `form/MATRIX_ARCHITECTURE.md`.
