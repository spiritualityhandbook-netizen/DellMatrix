# EVIDENCE — DIR-F12: Exchange journal-deletion receipt

Scope: repair circuit DIR-F12. Tested revision: candidate
ce55d50, merged e9b5d09 (tree equality verified). Commands:
suite + regress legs x3 + fresh-clone regress (logs included).
Full narrative: DIRF12_PACKET.md (included). Environment:
local Linux VM, Python 3.12. Gaps: fresh-clone first attempt
was SIGTERM'd by a VM replacement at 170/216 with no failures
— NO RESULT; the included fresh-clone log is the full re-run.

## Files (SHA-256, bytes)

| File | SHA-256 | Bytes |
|------|---------|-------|
| DIRF12_PACKET.md | c444dbeb205c4db769c3c28fd4ffa0ba1b129d027e17a654890650c1a9b853cd | 3749 |
| freshclone_regress.log | d81b26b43dbaeec3b4c632dacb9fa92b1e385d82ad3c4c5419ab94f13b22c6b1 | 13422 |
| freshclone_regress2.log | 7666c1bcfe7fd47c1699aa2f289f3f72cac8612a1577d6bef36f5434076bc2ca | 17101 |
| reg_leg1.log | 7666c1bcfe7fd47c1699aa2f289f3f72cac8612a1577d6bef36f5434076bc2ca | 17101 |
| reg_leg2.log | 7f0cb005b19a74662a29f42ed0e6a59d9b705203e124a81c76fa5293d261a1a9 | 34188 |
| reg_leg3.log | 6496b1241b40058be21a085092eeab09bd7cb146005fb1fb5b38b73dc9f155b2 | 17101 |

Digests computed at publication time from the
files as copied from the originating workspaces;
the originating circuits' packets (included) are
the claim documents for these artifacts.
