> STATUS: NOT IN USE — preform/src are earlier generations of DellMatrix, retained as design history and reference. The production runtime is form/ (verified at commit 11933da, 2026-10-30). This file does not describe current behavior.

# DellMatrix — Distribution Guide

Status: TRUE · Living

## Fast handoff (Blank)
```bash
cd preform/seed
python pack_seed.py
```
Send the printed zip. Recipient: unzip → `python blank_runner.py`.

## Full Living Matrix
Whole `preform/` or whole repo — only if they want the complete system.

## Snap-back
Personal → `SNAP_TEMPLATE` pack → Floor-safe review → Bind into Main.  
Floor never merges. Additive only. See seed `SNAP_TEMPLATE/MANIFEST.md`.

## Matrix identity
| Matrix | Role |
|--------|------|
| Main | Living shared True |
| Blank | Give-away starter (`seed/`) |
| Personal | Local enhancements |
