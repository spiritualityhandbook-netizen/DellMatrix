Chapter 9 — Evolutionary Computing (notes)

Source: https://natureofcode.com/genetic-algorithms/

Summary:
Chapter 9 introduces evolutionary computing as a process that uses natural
selection to evolve solutions to problems. Key ideas:
- Evolutionary systems work with a population of candidate solutions, each
  represented by a genome or set of parameters.
- Fitness functions evaluate how well each candidate performs with respect to a
  goal.
- Selection chooses the best candidates to reproduce, while crossover and
  mutation generate new offspring.
- Genetic algorithms are a common evolutionary technique; they can optimize
  variables, shapes, or behaviors by simulating generations of adaptation.
- Evolution is not a smart designer; it is a process of variation, selection,
  and inheritance where good traits survive and bad ones are discarded.

Implementation notes:
- Represent individuals as arrays, objects, or bit strings; make fitness easy to
  compute and compare.
- Use a population array, compute fitness for each individual, then create the
  next generation by selecting parents, crossing their genomes, and mutating the
  results.
- Keep copies of the current population and build the next generation separately
  to avoid in-place corruption.
- Mutation introduces small random changes; crossover recombines parent traits.

Integration ideas:
- Add a simple genetic algorithm demo under `form/dell_matrix/assets/examples`.
- Create paraphrase seeds for `form/mandell/english_brain.py` on evolutionary
  computing concepts, such as how selection, crossover, and mutation shape
  populations.

Next: Chapter 10 (Neural Networks) — https://natureofcode.com/neural-networks/
