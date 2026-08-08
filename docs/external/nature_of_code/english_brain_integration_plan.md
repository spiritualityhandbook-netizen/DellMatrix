English Brain integration plan — Nature of Code

Goal
----
Integrate Nature of Code chapter summaries into `form/mandell/english_brain.py` as paraphrase seeds, enabling page-by-page chapter queries to be learned and grounded by the English Brain enhance loop.

Page-by-page implementation plan
--------------------------------
1. Confirm all chapter summary notes are available under `docs/external/nature_of_code/`.
2. Add a new chapter knowledge paraphrase pattern in `form/mandell/english_brain.py`:
   - map questions like "what is X", "tell me about X", "explain X", "describe X" to canonical chapter forms.
3. Add chapter seed families to `EXPAND_FAMILIES` for each page:
   - `chapter introduction`
   - `chapter randomness`
   - `chapter vectors`
   - `chapter forces`
   - `chapter oscillation`
   - `chapter particle systems`
   - `chapter autonomous agents`
   - `chapter physics libraries`
   - `chapter cellular automata`
   - `chapter fractals`
   - `chapter evolutionary computing`
   - `chapter neural networks`
   - `chapter neuroevolution`
4. Seed each family with 3–5 short paraphrase sentences drawn from the chapter notes.
5. Run English Brain enhance / smoke after integration.
6. Document any new Dell or lattice hooks in NBD_LOG.

Keep all seeds offline-capable and Floor-locked.
