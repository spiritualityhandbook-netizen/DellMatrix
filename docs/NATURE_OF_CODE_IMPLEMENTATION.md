# Nature of Code → DellMatrix Implementation Map

**Source:** Daniel Shiffman, *The Nature of Code* (https://natureofcode.com/)  
**Repo notes:** `docs/external/nature_of_code/`  
**Runnable cores:** `form/dell_matrix/nature_code.py`  
**Visual canvas:** `form/dell_matrix/assets/pages/nature_code.html`  
**Law:** Usable concepts implemented. Boolean host intact.

---

## Visual status — COMPLETE for Ch0–5 + CA

| Chapter | Python core | Canvas visual |
|---------|-------------|---------------|
| Ch0 Randomness | Walker, gaussian, accept_reject | Live biased walker + trail |
| Ch1 Vectors | Vec2 full ops | Inside Forces movers |
| Ch2 Forces | apply_force, gravity, wind, friction | Live multi-mass movers |
| Ch3 Oscillation | oscillate() | Live harmonic orbits |
| Ch4 Particles | Particle + Emitter | Live emitter follow pointer |
| Ch5 Agents | seek / flee | Live seek-mouse agents |
| Ch7 CA | ca1d_step | Live Rule 90 scroll |
| Ch6 / 8–11 | Documented seeds | Next growth / PROJECTED |

---

## How to open the canvas

With live host running:

```text
/nature_code
```

or open the page file under assets/pages when serving static assets.

Keys on the page: `1`–`6` switch mode · `R` reset · pointer = agent/particle target.

---

## Runnable Python

```bash
python -m form.dell_matrix.nature_code
```

## Relation to Code Evolution

- Randomness → ProbabilisticShell
- Direction + magnitude → FlowShell / look / move
- Forces on grade → continuous fuel
- Particles / agents → multiple open surfaces + aggregate_looks
- Canvas = eyes; nature_code.py = brain; decision_shells = judgment

**True · Dense · Placed · Runnable · Labeled · Finishable**
