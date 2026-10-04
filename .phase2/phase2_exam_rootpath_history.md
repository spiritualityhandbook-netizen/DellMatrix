# PHASE 2 EXAMINATION — RootPath / RU-PAT Git-History Archaeology

**Archaeologist:** independent subagent (read-only)
**Date:** 2026-10-03
**Scope:** entire git history, all branches (693 commits), deleted files, renames
**Worktree:** `~/workspace/dellmatrix-gdp-phase1` (nothing modified)

---

## EXECUTIVE SUMMARY

**There is no historical "RootPath" module, class, function, or doc.**
The literal string `RootPath` occurs in exactly 3 places, all recent
(2026-10-03), and two of them are the Phase-0 GDP ledgers. The Phase-0
Equation Ledger coined "RootPath" as an English gloss for the older
term **"RuPat" / "RU-PAT"** — a term that genuinely exists in history
but with **two incompatible documented meanings**:

1. **RU→PAT ingest pipeline** (code, JS era, 2026-07-25): a 7-stage
   input-processing pipeline — Tokenize → Embed → Attention → Context
   → Reason → Generate → Refine. Defined in
   `src/core/mandel_ontology.js`, exported via `listRuPat()`, **zero
   callers in all history** (dead from birth), file byte-identical
   since creation.
2. **RuPat = flow / direction of execution** (preform design docs,
   2026-07-25/27): diagonal-flow glyph semantics, "Attach RuPat / flow"
   pipeline step, "may return via RuPat" (fog→active return path).
   Never implemented as code; design vocabulary only.

Neither meaning is a graph path with nodes, edges, prerequisites,
cost, or energy. **No recoverable authoritative RootPath semantic
exists in the route/location/prerequisite/cost sense.** If Phase 2
needs "RootPath" with those semantics, it must be DEFINED by Director,
not recovered — history provides vocabulary fragments, not authority.

**No deleted historical graph code was found.** Deleted source files
are boot shims and audit scripts, not graph implementations. No
renames involving graph/tree/node/edge/path/route/hierarchy terms.

---

## FINDING 1 — "RootPath" (literal): a Phase-0 ledger gloss, not history

### Occurrences (complete inventory)

| # | Location | Commit | Date | Context |
|---|---|---|---|---|
| 1 | `docs/DELLMATRIX_EQUATION_LEDGER.md:380` | `8922a19` | 2026-10-03 | Lineage row "**RootPath / RuPat**" |
| 2 | `docs/GDP_001_PHASE_0_GDP_LEDGER.md` | `e194da2` | 2026-10-03 | Req 0.4.3: "Preserve mathematical lineage: RootPath, …" |
| 3 | `.phase2/PHASE2_AUTHORITY_MAP.md` | (parent's Phase-2 working doc) | 2026-10-03 | "RootPath → TBD (see history report)" |

### The ledger's own words (commit 8922a19, §8 Lineage Register)

> | **RootPath / RuPat** | preform design docs only | NONE — mentions in
> `preform/MANUAL_EXTRACT.md:12,18`,
> `preform/VISUAL_GLYPH_LAYER.md:18,44,58,65,110` (flow diagonals,
> fog-return path) | No runtime equations found | `UNKNOWN` as
> mathematics; preserved as design vocabulary. No-loss law applies:
> do not erase, do not invent. |

### Critical verification

The cited preform files contain the string **"RuPat"**, NOT "RootPath"
(verified by case-insensitive grep of the files at HEAD). The ledger
author equated the two. The name "RootPath" never existed in the
preform era.

### Negative searches (all returned zero)

- `git log --all --oneline -S "rootpath"` → 0 (case-sensitive lower)
- `git log --all --oneline -S "ROOTPATH"` → 0
- `git log --all --oneline -S "root path"` → 0 (two words)
- `git log --all --oneline -S "root_path"` → 0
- `git log --all --oneline -S "root-path"` → 0
- `git log --all --oneline -S "RootPath"` → 2 (only the two ledger commits above)

---

## FINDING 2 — RU-PAT as a 7-stage ingest pipeline (the code definition)

### Source

`src/core/mandel_ontology.js`, created in commit
`8af1639` (2026-07-25, "Establish Mandel Compendium V2 coherent core:
ontology registry, 7 laws, morpheme layer, RU-PAT pipeline —
Nova/Focus placement per floor lock").

Quoted verbatim from `git show 8af1639:src/core/mandel_ontology.js`:

```js
/** RU→PAT pipeline (ingest) — structural stages, not a claim of raw transformer access */
export const RU_PAT = [
  { id: 'S1', name: 'Tokenize', job: 'Cut input into pieces' },
  { id: 'S2', name: 'Embed', job: 'Map pieces into working form' },
  { id: 'S3', name: 'Attention', job: 'Relate pieces (pin / focus set)' },
  { id: 'S4', name: 'Context', job: 'Tier memory stack' },
  { id: 'S5', name: 'Reason', job: 'Lattice + Dell + Verita logic' },
  { id: 'S6', name: 'Generate', job: 'Build result block-by-block' },
  { id: 'S7', name: 'Refine', job: 'Pre-output chain + SUS gates' }
];
...
export function listRuPat() {
  return RU_PAT;
}
```

### What it MEANT here

**RU→PAT = an ingest pipeline**: raw unit → pattern, seven structural
stages from tokenization through SUS-gated refinement. It is about
input processing, NOT about routes, locations, prerequisites, or
cost/energy. The docstring explicitly disclaims "a claim of raw
transformer access."

### Companion evidence

- `src/core/control_primitives.js:3` (same era, still live):
  `* + Compendium V2 alignment hooks (RU-PAT refine stage = preOutputChain)`
  — i.e., stage S7 (Refine) maps to the pre-output chain.
- `docs/MANDEL_COMPENDIUM_V2_ESTABLISHED.md` (commit 8af1639):
  > - Any claim that RU-PAT literally rewrites transformer weights
  — listed under "Rejected / not established as floor truth."
  Someone had claimed RU-PAT could rewrite transformer weights
  (a learning/adaptation claim); this was explicitly REJECTED.

### What happened to it

- File `src/core/mandel_ontology.js` still exists on main and in the
  worktree, **byte-identical since 2026-07-25** (verified by diff
  against `8af1639:`).
- `listRuPat()` / `RU_PAT`: **zero callers** in all 693 commits
  (`git log --all -S "listRuPat"` and `-S "RU_PAT"` return only the
  defining commit). Dead from birth.
- The only other mentions are doc-inventory lines ("Runtime already
  established … mandel_ontology") in commits 7db574c/ccbc420 — not
  imports.

**Fate: defined once, never used, never deleted. Abandoned in place.**

---

## FINDING 3 — RuPat as flow / direction of execution (preform design vocabulary)

### Sources (all preform era, July 2026)

**`preform/MANUAL_EXTRACT.md`** (commit `d62a175`, 2026-07-25,
"Preform: Manual practical extract only"):

> Line 12: `3. Attach RuPat / flow`
> (step 3 of the "Entropy solidify pipeline": 1. Origin stillness →
> 2. Define/write/structure → **3. Attach RuPat / flow** →
> 4. Follow + correct → 5. Emergency stop / Void / Fade →
> 6. Show / realize output)
>
> Line 18: `- Fog = drop from active workspace; may return via RuPat`
> (fog = archive tier; RuPat is the **fog-return path** back to the
> active workspace)

**`preform/VISUAL_GLYPH_LAYER.md`** (commits `fff7fc2` 2026-07-25,
`508446e` 2026-07-27):

> - `| **Diagonal flow** | `╱ ╲ ╳` + arrows | RuPat diagonals ↘↙↗↖ |`
> - `| **Arrows** (U+2190) | Flow · RuPat · direction of execution |`
> - `### FLOW (direction / RuPat)` — glyph taxonomy section
> - `Use: sequence, diagonal RuPat, major jump`
> - `| **Dual Lattice** | Structure = edges; Flow = RuPat; Markers = nodes/centers |`

**`preform/pages/05_VISUAL_GLYPH.md`** — duplicates the glyph taxonomy.

### What it MEANT here

**RuPat = flow pattern / direction of execution**: the diagonal-flow
glyph family in the terminal visual language, and the abstract
"execution direction" concept in the design pipeline. The one
functional-ish usage is the **fog-return path** (archived content may
return to the active workspace "via RuPat") — a state-transition
notion, not a graph route.

### What happened to it

Never implemented as code. Remains design vocabulary in preform docs
(still present at HEAD). The Phase-0 Equation Ledger preserved it
under the no-loss law as `UNKNOWN` mathematics / design vocabulary.

---

## FINDING 4 — Deleted historical graph code: NONE FOUND

### All deleted source files (complete list, excluding state/visual artifacts)

| File | Deleted in | Date | What it was |
|---|---|---|---|
| `form/boot.py` | `da6e154` (FCND-I) | 2026-10-02 | Boot shim delegating to `form.open`; dead duplication |
| `form/mandell/gate_core_ii_bind.py` | `da6e154` | 2026-10-02 | (gate binding shim) |
| `form/smoke_all.py` | `da6e154` | 2026-10-02 | (smoke runner) |
| `run_full_audit_and_enhance.py` | `ea179e7` (RTPH-I) | 2026-10-01 | Audit script |
| `.github/workflows/npm-publish*.yml` | `ea179e7` | 2026-10-01 | CI workflows |
| `form/docs_tmp_placeholder` | `ea179e7` | 2026-10-01 | placeholder |

None implements graphs, trees, nodes, edges, or hierarchies.

### Renames

`git log --all --diff-filter=R --name-status`, filtered for
graph/tree/node/edge/path/route/hierarchy terms → **zero results**.

### Existing (live) graph-ish files — neither is RootPath

- `form/dell_matrix/graph_view.py` — UI view contract: `ViewNode`
  (id/label/x/y/words/sandboxed/score) + edges for plane
  visualization. A perspective-bound view model, not a semantic graph.
- `form/mandell/correction_graph.py` — ODCG-I: read-only
  outcome-derived correction-candidate projection; explicitly
  non-causal, no new ledger, no second Outcome authority.

---

## FINDING 5 — Route/location/prerequisite/cost semantics: none connected to RootPath

- `form/mandell/semantic_router.py` — "Typed Mandell → Dell semantic
  routing boundary (DCC-II)". Dispatch routing, not RootPath.
- `form/dell_matrix/flash_path.py` — `flash_judge()` with a
  `budget_ms` param. "Path" is a name only.
- `form/dell_matrix/button_path_enhance_loop.py` — "Canonical app
  routes (must load assets)". UI routes.
- `git log --all -i -S "prerequisite"` → only Core-II catalog and
  license commits (unrelated).
- No cost/energy semantics attached to any route/path concept anywhere.

---

## JUDGMENT — recoverable authoritative semantic?

**No.** The evidence supports three distinct, non-unifiable items:

| # | Term as written | Era | Meaning (quoted/primary) | Status |
|---|---|---|---|---|
| A | `RootPath` | 2026-10-03 (GDP ledgers) | Ledger gloss for "RuPat"; no independent definition | **Neologism — not historical** |
| B | `RU_PAT` / `RU-PAT` | 2026-07-25 (JS code) | 7-stage ingest pipeline (Tokenize→…→Refine); explicitly not transformer access | Code-defined but **dead** (0 callers, unchanged since birth) |
| C | `RuPat` | 2026-07-25/27 (preform docs) | Flow / direction of execution / diagonal glyphs / fog-return path | Design vocabulary, **never implemented** |

- (A) cannot be "recovered" — it was invented 10 days ago as a label.
- (B) is the only code-level definition, but it is an **ingest
  pipeline**, not a graph route; adopting it for Phase-2 RootPath
  would be a semantic transplant, not a recovery.
- (C) is the meaning the Equation Ledger actually documented ("flow
  diagonals, fog-return path") — closest to a "path" notion, but it is
  visual/execution-direction vocabulary with no nodes, edges,
  prerequisites, or cost.

**Recommendation to the parent agent:** if the Phase-2 directive's
RootPath objectives (2.4.1–2.4.5: route/location, prerequisites,
cost/energy) require those semantics, they must be **authored as new
Phase-2 semantics by Director decision**, informed by — but not
claiming descent from — this history. Claiming historical authority
for a route/prerequisite/cost RootPath would be fabrication; the
history does not contain one.

---

## SEARCH METHODS (for absence-proof)

Worktree `~/workspace/dellmatrix-gdp-phase1`, 693 commits, all branches:

1. `git log --all --oneline -S "RootPath"` → 2 commits (8922a19, e194da2)
2. `git log --all --oneline -S "RU-PAT"` → 1 commit (8af1639)
3. `git log --all --oneline -S "ru-pat"` → 0
4. `git log --all --oneline -S "rootpath"` → 0
5. `git log --all --oneline -S "ROOTPATH"` → 0
6. `git log --all --oneline -S "root path"` → 0
7. `git log --all --oneline -S "root_path"` → 0
8. `git log --all --oneline -S "root-path"` → 0
9. `git log --all --oneline -i -S "rupat"` → 5 commits (8922a19, 508446e, fff7fc2, d62a175, 8af1639)
10. `git log --all --oneline -S "RU_PAT"` → 1 commit (8af1639)
11. `git log --all --oneline -S "listRuPat"` → 1 commit (8af1639)
12. `git log --all --diff-filter=D --name-only --pretty=format:"%h"` → enumerated; source deletions listed in Finding 4; no graph code
13. `git log --all --diff-filter=R --name-status` filtered for graph/tree/node/edge/path/route/hierarchy → 0
14. `git log --all --name-only --pretty=format:` unique filenames matching `*graph*` → 2 live files (graph_view.py, correction_graph.py); matching `*route*|*_path*` (non-state) → 6 files, none RootPath-related
15. `grep -rin "rupat\|ru_pat\|ru-pat"` over worktree (py/md/js) → 15 lines, all inventoried above
16. `grep -ri "rootpath"` over worktree → 4 lines (2 ledger rows + ledger req + `.phase2/PHASE2_AUTHORITY_MAP.md` TBD note)
17. `git show <sha>:<path>` used to read deleted/old file contents (boot.py, mandel_ontology.js at 8af1639, preform docs at introducing commits)
18. `diff <(git show 8af1639:src/core/mandel_ontology.js) src/core/mandel_ontology.js` → identical
