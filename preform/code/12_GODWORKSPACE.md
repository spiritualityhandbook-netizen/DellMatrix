> STATUS: NOT IN USE — preform/src are earlier generations of DellMatrix, retained as design history and reference. The production runtime is form/ (verified at commit 11933da, 2026-10-30). This file does not describe current behavior.

# 12 — GodWorkSpace Terminal Shell (Code Phase 3 Artifact 12)

Status: TRUE (minimal offline shell)

## Purpose
Text-first GodWorkSpace that satisfies page 08 keep-blend requirements offline.

## Keep-blend coverage
| Requirement | Implementation |
|-------------|----------------|
| Header + status | HeaderPanel + StatusPanel |
| Sections / panels | Status · Seed · Log · Drafts |
| Temp C/W/H | set_temp() |
| Read-only seed strip | SeedStripPanel (do not disturb) |
| local drafts | DraftPanel (in-memory until True confirm) |
| Pipeline / Dell search | deferred to later expansion |

## Growth
- Hosts Avatar status, anim frame, inventory from prior artifacts
- Full graphical UI remains future work
- This shell is the living True core for Code Phase 3
