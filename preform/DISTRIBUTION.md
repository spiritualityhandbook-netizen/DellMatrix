# DellMatrix — Distribution Guide

Status: TRUE · Living

## What you can give someone

### A) Full Living Matrix (this repo)
Everything under `preform/` — Floor, registry, Code Phase artifacts, Integrator, panels.
Use when they want the complete working system.

### B) Blank Dell Matrix (seed only)
Folder: `preform/seed/`

Minimal kit:
- Floor lock (immutable)
- Core Dell registry 00–26 + Manifest 50
- Dual-output law (Mandel inside · English display)
- Offline stub runner
- Empty personal snap slot

They enhance **their** copy. They do not need your full history.

---

## How others use the Blank

1. Copy `preform/seed/` (or clone repo and work only in seed).
2. Read `seed/00_FLOOR.md` and `seed/README.md`.
3. Run `python seed/blank_runner.py` — confirms Floor + registry live.
4. Add personal pages under `seed/personal/` only.
5. Add personal code under `seed/personal_code/` only.
6. Never edit Floor or True registry numbers in the seed core.

---

## Snap-back to Main (contribution path)

Personal work stays local until they choose to snap.

### Rules
1. **Floor never merges** — Alpha·Delta·Omega·Omni stay locked everywhere.
2. **Registry numbers 00–50 are shared True** — personal may *alias* (Named Dell) but not redefine manors.
3. **Snap packages** are additive modules: pages, packs, panels, helpers.
4. Main accepts a snap only if:
   - Floor untouched
   - No decipherment claims
   - Offline-capable
   - Declares what it adds (manifest)
5. Snap does **not** delete anyone else’s personal matrix.

### Snap package shape
```
snap_pack/
  MANIFEST.md      # name, author, what it adds, Dell hooks
  pages/           # optional living page fragments
  code/            # optional offline modules
  personal/        # optional — stays with author unless dual-licensed
```

### Flow
```
Blank → personal enhance → snap_pack → propose to Main
Main  → review (Architect) → bind into living pages/code
Author keeps their Blank+personal intact either way
```

Main enhancement absorbs useful snaps so **what you’re doing, what they’re doing, what anyone given the kit is doing** can feed the same living matrix without overwriting individual sandboxes.

---

## Identity of matrices

| Matrix | Role |
|--------|------|
| **Main** (`preform/`) | Living shared True — Floor, registry, verified artifacts |
| **Blank** (`preform/seed/`) | Give-away starter — basics only |
| **Personal** (`seed/personal/`) | Their enhancements — local until snapped |

Snap is voluntary Bind, not automatic sync.
