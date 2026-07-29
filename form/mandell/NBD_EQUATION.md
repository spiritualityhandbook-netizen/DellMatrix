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

```bash
python -m form.mandell.nbd_equation
```
