Grok AI / External AI Directive — Continue Nature of Code ingestion and integration

Context
- Repo: DellMatrix (you have read/write access to repository content).
- Current work: Introduction and Chapters 0–3 of The Nature of Code have been
  fetched and saved under `docs/external/nature_of_code/`.

Goal
- Continue ingesting remaining chapters from https://natureofcode.com/ into
  `docs/external/nature_of_code/`, extract concise chapter summaries and
  paraphrase seeds, and integrate those seeds into `form/mandell/english_brain.py`.

High-level steps for an AI with repo access
1. Sync repo locally (if not already):

   git pull origin main

2. Read current chapter notes:

   - `docs/external/nature_of_code/introduction.md`
   - `docs/external/nature_of_code/chapter_00_randomness.md`
   - `docs/external/nature_of_code/chapter_01_vectors.md`
   - `docs/external/nature_of_code/chapter_02_forces.md`
   - `docs/external/nature_of_code/chapter_03_oscillation.md`

3. For each remaining chapter (4..11):
   a. Fetch the chapter page (e.g., `https://natureofcode.com/particles/` for
      Chapter 4). Use `curl` or Playwright to extract the article body.
   b. Clean text: remove navigation, links, captions; preserve code blocks.
   c. Write `docs/external/nature_of_code/chapter_0N_<slug>.md` with summary,
      key concepts, and 3–5 paraphrase seeds suitable for English Brain.

4. After all chapters present, follow `english_brain_integration_plan.md`.

Law: Keep offline core intact. All new material under docs/external/ only.
