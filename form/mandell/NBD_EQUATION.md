> STATUS: IN USE — describes live code in form/ at commit 11933da. Doc verified against code 2026-10-30.

# NBD Equation (Mandell)

## Seed
```
15[Map] : 18[Mirror] >> 46[Rank] > 50[Manifest] :: NBD
```

## Formula

$$
\mathrm{NBD}_t = \arg\max_{c \in \Delta_t} \, \varphi(c)\,\rho(c)\,\lambda(c)\,\sigma(c)
$$

|
Symbol | Meaning |
|-------|--------|
| $G^*$ | Goal (FOUNDATION end-state) |
| $G_t$ | State now |
| $\Delta_t = G^* \setminus G_t$ | Still missing or under-level |
| $\varphi$ | 1 if Floor-safe and Manifest-complete, else 0 |
| $\rho$ | Resonance with spine Mandell→Dell→DuoBeta→… |
| $\lambda = L^* - L_t$ | Level deficit ($L^*=3$ working, $1$=label, $2$=stub) |
| $\sigma$ | Sequence priority (language-first) |

Dynamic: as $L_t$ rises, $\lambda$ falls, ranking shifts — equation stays fixed.

> Module note (2026-10-30): there is no `form/mandell/nbd_equation.py` in this tree at commit 11933da — the equation above is the design formula, not a runnable module. The live NBD decision-support code is `form/mandell/nbd_engine.py` (NBDE-I: read-only DISCOVER / CLASSIFY / SCORE / COMPARE / RANK / EXPLAIN / PROPOSE) with `form/mandell/nbd_candidates.py`.
