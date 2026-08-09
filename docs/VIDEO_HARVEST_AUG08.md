# Video harvest — 2026-08-08

Analyzed six links → high-value ideas → modules on GitHub.

| Video | Theme | Idea taken | Module |
|-------|--------|------------|--------|
| [Qr3VsZYQy4s](https://youtu.be/Qr3VsZYQy4s) Game with **no assets** (Zanzlanz) | Procedural-only world | Zero external art; glyphs from rules/seeds | `procedural_assets.py` |
| [vO6SWG-jxvE](https://youtu.be/vO6SWG-jxvE) DeepMind **sees the world** (Two Minute Papers) | World models / predict beyond sensors | Predict unseen nodes + delta gaps; honesty tag | `world_predict.py` |
| [ebqKYLKjL6U](https://youtu.be/ebqKYLKjL6U) **Verse** language (Logan Smith) | Transactional memory, effects, rollback | Commit-or-abort staging for nursery/view | `transactional_ops.py` |
| [8B05cy3UuSE](https://youtu.be/8B05cy3UuSE) NVIDIA **copying humans isn’t enough** | Intrinsic RL / anti-shortcut | Curiosity reward + exploration actions | `intrinsic_agent.py` |
| [bm1BjOjS7sQ](https://youtu.be/bm1BjOjS7sQ) **DeepSeek** Flash moment | Efficiency under constraints | Sparse flash judge path | `flash_path.py` |
| [IoM5zUI8oFc](https://youtu.be/IoM5zUI8oFc) | Title unresolved in harvest | Held for next pass | — |

## How to run

```bash
python -m form.dell_matrix.procedural_assets
python -m form.dell_matrix.world_predict
python -m form.dell_matrix.transactional_ops
python -m form.dell_matrix.intrinsic_agent
python -m form.dell_matrix.flash_path
```

## Wiring next

- `free_matrix.draw_frame` can call `plane_sheet`
- `see` + `predict_unseen` for HUD “beyond view”
- auto_growth optional flash_batch under time pressure
- companion step → `IntrinsicAgent.step`

Law: PROJECTED_NOT_FACT on predictions · GitHub first · offline core.
