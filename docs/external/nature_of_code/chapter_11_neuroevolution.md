Chapter 11 — Neuroevolution (notes)

Source: https://natureofcode.com/neuroevolution/

Summary:
Chapter 11 combines neural networks with evolutionary algorithms. Instead of
(or in addition to) gradient-based training, the weights and sometimes topology
of networks are evolved using selection, crossover, and mutation. This is
useful when fitness is easy to evaluate but gradients are hard to compute
(e.g., game agents, robotics).

Key points:
- Genome encodes network weights (and optionally architecture).
- Fitness comes from agent performance in an environment.
- Generations of networks improve via evolutionary operators.
- Can be combined with novelty search or other open-ended evolution techniques.

Integration:
- Seeds for english_brain around evolving controllers.
- Possible future demo of simple neuroevolution for a DellMatrix agent.

End of core Nature of Code chapters.
