# DellMatrix — Full Audit

Repository: spiritualityhandbook-netizen/DellMatrix
Branch: main
Scanned: 2026-08-03

## Summary

- What it is: DellMatrix is an offline-first Python application (Mandell Origin) that provides a structured “bridge language” and an interactive REPL for creating, growing, and managing conceptual “ideas” in a ringed-growth / harmonic-lattice system. It emphasizes an offline acceptance path, multilingual command input (English/Spanish/French/LatinMandell), and saved sessions with a visual HTML output.
- Status: User-ready (offline) per README/docs. Default branch: main. Language: Python. No repository license file detected prior to this audit.
- Primary entry points: `launch.py` (launcher), `form/open.py` (Program core), `form/repl.py` (REPL interface).
- Runtime: Pure-Python core, advertised requirement Python 3.10+. Core loop is offline and claims no external network or API keys required for core features.


## Repository metadata (extracted)

- Full name: spiritualityhandbook-netizen/DellMatrix
- Visibility: public
- Default branch: main
- Language: Python
- Size: ~955 KB (repo metadata)
- Owner: spiritualityhandbook-netizen


## High-level capabilities (features)

- Interactive REPL supporting:
  - Natural-language-like commands: create ideas, grow ideas, proposals, rank, confirm/reject, save/load, visual, lattice transforms (cube/sphere/core/flower), avatar actions (walk/face/express).
  - Multilingual inputs (English primary; Spanish/French mapped into commands; LatinMandell depth for lexical decomposition).
  - Seed-style commands using Dell operators (e.g., `08[Create] > 15[Map] :: name`).
- Core domain model:
  - BlankCube / session plane of units (ideas).
  - Nursery / RingedGrowth for proposed idea evolution and pending proposals.
  - HarmonicLattice for spatial/structural placement in forms (cube, sphere, core, flower).
  - Avatar entity with face controller and expressions.
  - Keys ledger for permanent keying/remembering of important ideas.
- Persistence & visual output:
  - Save/load of sessions (persist module used by Program.save/load).
  - Visual: offline HTML panel written by `form.dell_matrix.visual`, with an "easy" path and html path.
- Sandbox, Enhance, Ambient gates: runtime flags/controls around behaviors (sandbox quarantine, enhance pulse/score system, ambient).
- Offline tutorial and acceptance path: `create → grow → confirm → sphere → save → load → visual`.
- Smoke tests / self-checks: `open_program.smoke` and module-level smoke/invariants referenced.


## Architecture / top-level structure (what each important file/folder does)

- README.md
  - Project overview, quick start commands, brief description of core concepts (Mandell seeds, Dells, Floor, Ringed growth, Harmonic lattice, Avatar, Save/load v7).
  - Points to `docs/INSTALL.md`, `docs/TUTORIAL.md`, `docs/START_HERE.md`, and `form/CORE_SCOPE.md`.
- launch.py
  - Simple entrypoint to change cwd, add project path to `sys.path`, parse optional owner argument, and call `form.repl.run(owner)`.
- docs/INSTALL.md
  - Installation and first-minute walkthrough for average user. States core requires Python 3.10+, is offline, and no network/API keys needed for the acceptance path.
- form/ (live runtime)
  - `form/open.py` (Program): central Program dataclass wiring together the core components and exposing the public API.
  - `form/repl.py` (REPL): interactive command parser and translation layer from natural language to program actions.
  - `form/dell_matrix/*`: core matrix behavior: plane, nursery, ringed growth, lattice, visual output, resonance, etc.
  - `form/mandell/*`: Mandell language utilities, seed parsing/execution, bridges and patterns.
  - `form/avatar`: avatar entity, face controller, locomotion and expressions.
  - `form/duobeta`: duo-beta growth orchestration.
  - `form/persist`: session save/load (persist v7) and state serialization.
- preform/ and src/
  - Marked as legacy/frozen. `preform/` README explicitly states these are historical and must not be treated as current runtime.


## File-by-file walkthrough (key files with behavior detail)

- `launch.py`
  - Entrypoint; constructs Program via `form.repl.run` and prints introductory text. Accepts optional owner argument to name session owner.
- `form/open.py`
  - `Program.__post_init__`: asserts floor intact, gives `BlankCube`, loads nursery, constructs `RingedGrowth` and `HarmonicLattice`, registers `SnapCandidate`s into `DellMatrix`, and seeds `DuoBeta.evolve` with an "Open" action.
  - Core methods: `place`, `grow_ideas`, `confirm_proposal`, `reject_proposal`, `sandbox_on/off`, `enhance_on/off`, `pulse`, `scores`, `save`, `visual`, `set_lattice_size`, `radial_drift`, `avatar_status`, `render`, `status`, `replay_exec`, `macro_seed`, and history note utilities.
  - Includes `smoke()` and CLI-friendly `main()` for quick verification.
- `form/repl.py`
  - Command parsing: translates natural language into intents and maps to Program methods. Supports LatinMandell depth (explain/deepen/morph/customize) and polyglot input (es/fr).
  - Tutorial runner `_run_tutorial` exercises the acceptance path and returns a saved session and visual path.
- `form/persist.py`
  - Session serialization and deserialization (save/load). Writes session JSON under `form/state/` by default (path: `form/state/program_<owner>.json`).
  - Serialized state includes plane units, sandboxes, nursery proposals, lattice cells, avatar state, enhance/resonance state, history, and LatinMandell customs.


## Security, secrets, and sensitive-data findings

- Scanned files: README.md, launch.py, docs/*, form/*.py (open.py, repl.py, persist.py, and other referenced modules when present), package.json, AGENTS.md, and workspace_manifest.json.
- No plaintext API keys, `.env` file, or PEM private-key blocks were found in the files inspected for this audit (notably: no occurrences of `BEGIN PRIVATE KEY`, `BEGIN RSA PRIVATE KEY`, `AWS_SECRET_ACCESS_KEY`, `AWS_ACCESS_KEY_ID`, or obvious `API_KEY` tokens in the files opened).
- `form/persist.save` writes session JSON files into `form/state/` (created by persist). These session files may contain user-provided content (labels, words, goals, custom LatinMandell bindings) and therefore can contain PII or sensitive content if users saved such content. Review existing saved JSON files before making the repository public.
- `form/llm/` and `form/trading/` are marked as SIDE (not core). These side folders may contain optional integrations that could reference external services; they should be reviewed separately if present and if you plan to enable those features publicly.
- I could not run a full git-history-sensitive scan within this action. If secrets were committed and later removed, they may still exist in the commit history. Recommended next steps (automation): run `gitleaks`, `truffleHog`, or `git-secrets` against the repository and use `git filter-repo` or BFG to purge any secrets found, then rotate affected credentials.


## Dependency, packaging, and runtime considerations

- The repository does not include `requirements.txt` or `pyproject.toml` at the repository root prior to this commit. A `package.json` exists for legacy JS pieces and is marked `license: "UNLICENSED"`.
- Based on imported modules in the inspected Python files, the core runtime appears to rely only on the Python standard library (json, os, sys, dataclasses, typing, datetime, etc.). No external pip packages were detected in the main runtime files opened.
- If optional side modules (e.g., `form/llm/` or `form/trading/`) are enabled, they may require extra packages (LLM clients, requests/httpx, numpy, etc.). Those must be enumerated and pinned in `requirements.txt` when you decide to enable those features.


## License & compliance

- No LICENSE file was present in the repo before this audit. Without a license file, reuse by others is legally restricted. I am adding an MIT license file in this commit as requested.


## Code quality and maintainability notes

- The code is modular and uses a dataclass-based `Program` entrypoint. Responsibilities are separated into modules for matrix, nursery, lattice, avatar, persistence, and Mandell language utilities.
- Documentation exists for installation and a short tutorial; additional API docs or contributor docs would help external contributors.
- Tests: smoke/invariant hooks exist (smoke() in modules) but no CI workflows were detected in top-level files reviewed. Consider adding GitHub Actions to run smoke tests on push.


## Risks, issues, and suggested remediation

1. Add LICENSE (done in this commit) to clarify reuse rights.
2. Add `requirements.txt` or `pyproject.toml` to document dependencies and Python version. (Added in this commit with detected findings.)
3. Review persisted session files in `form/state/` for PII or secrets before public sharing; consider clearing sample sessions or adding `.gitignore` to avoid committing user session files.
4. Run a comprehensive git-history secrets scan (gitleaks/truffleHog/git-secrets). If secrets are found, use `git filter-repo` or BFG to remove them, then rotate the credentials immediately.
5. Add CONTRIBUTING.md and CI workflows (Action to run smoke tests and linting).


## Runtime / usage summary (how the program runs)

- Prerequisite: Python 3.10+.
- Start options:
  - Any: `python launch.py`
  - Windows: double-click `Launch DellMatrix.bat`
  - Mac: double-click `Launch DellMatrix.command`
  - Optionally pass an owner: `python launch.py YourName`
- REPL usage: type `help` for examples; acceptance path demonstrated by `tutorial` command: `create an idea`, `grow ideas 2`, `proposals`, `confirm all`, `sphere`, `save`, `visual`.
- Output: `visual()` writes an offline HTML visual (path returned) that can be opened locally.


## Conclusion

- DellMatrix is a self-contained, offline-first Python application providing a rich REPL-driven environment for structured idea creation and evolution. The main runtime is in `form/` with `launch.py` and docs supporting easy local start.
- Before broad public sharing, address missing license (added), declare dependencies (added `requirements.txt`), and verify persistence content and git history for sensitive data.


---

(End of audit)
