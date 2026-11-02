# EVIDENCE — DIR-F13: Loop count grammar

Scope: repair circuit DIR-F13. Tested revision: candidate
2a87021, merged 81c976a (tree equality verified). Commands:
suite + regress legs x3 + fresh-clone regress (logs included).
Full narrative: DIRF13_PACKET.md (included). Environment:
local Linux VM, Python 3.12. Gaps: leg-2 first attempt was
killed by a VM replacement at 200/217, zero failures — NO
RESULT; the included leg-2 log is the full re-run.

## Files (SHA-256, bytes)

| File | SHA-256 | Bytes |
|------|---------|-------|
| DIRF13_PACKET.md | 07fcb9d55e74b9ae928791cbb4f6d4af4ca770ddcaa5a6296f86ae1bb144cda4 | 10802 |
| freshclone_regress.log | c045455fb1defd72df0a288b9f8083ae6a0b1a181ed4111dfb950b8fc20a9ba9 | 17180 |
| legs23.done | 5c91bc5fb3c4c9ab3cc8ceee39df4d1ff7bb892e5eb34ed8f809873d8f1dd969 | 8 |
| reg_leg1.log | c045455fb1defd72df0a288b9f8083ae6a0b1a181ed4111dfb950b8fc20a9ba9 | 17180 |
| reg_leg2.log | a038429172db6ecf35679b7cc07f7b649206c7222401956f3b2698e1a10a2a91 | 34346 |
| reg_leg3.log | cbab0ecd1bb0feb60ae1354b09fb02527cf105110d38656ad4c610047c5585cb | 17180 |

Digests computed at publication time from the
files as copied from the originating workspaces;
the originating circuits' packets (included) are
the claim documents for these artifacts.
