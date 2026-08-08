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
      key concepts, and `Next:` link.
   d. Produce 8–15 paraphrase seeds per chapter: one-line, high-quality
      paraphrases suitable for seeding `form/mandell/english_brain.py`.

4. Integrate paraphrase seeds into `form/mandell/english_brain.py` safely:
   - Append a new dict entry under the existing data structure labeled
     `nature_of_code_chapter_<n>` containing the seeds.
   - Ensure no syntax errors; run `python -m pyflakes` or `python -m compileall`.

5. Commit and push changes in a feature branch, open a PR:

   git checkout -b feature/natureofcode-ingest
   git add docs/external/nature_of_code/*.md form/mandell/english_brain.py
   git commit -m "ingest natureofcode chapters 0-11: summaries + seeds"
   git push --set-upstream origin feature/natureofcode-ingest

6. Run local test (optional):
   - Run the 150-loop for `form.mandell.english_brain_150_loop.py` if available.
   - Or run unit checks where applicable.

Notes
- Prefer offline-capable seeds; keep Mandell Floor / Nursery laws.
- Do not commit .venv, __pycache__, or large media.
- After ingest, update form/NBD_LOG.md with a short entry.
