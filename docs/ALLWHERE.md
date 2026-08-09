# Allwhere inside DellMatrix

Social media open-world RPG from the Allwhere design PDF, grown as a matrix module.

## Run

```bash
git pull origin main
python -m form.dell_matrix.allwhere
python -m form.dell_matrix.allwhere --name Ace --seed 42 --interests art,travel,lore
python -m form.dell_matrix.allwhere --smoke
```

## First arc (run to completion)

1. Birth by interests → matching city hometown  
2. Source posts in Square + Inn (Dimenia lore)  
3. Real-time travel to second town  
4. Retrieve map scrap + bounty (3 lore echoes)  
5. Stand in Square with ≥100 coin (personal dream of a store)  
6. **ARC_COMPLETE** — middle world holds; immortal child only died, never slain

## Systems implemented

| Design | Code |
|--------|------|
| World → City → Town → Room | `World` / `City` / `Town` / `Room` |
| Source feeds per place | `feed` lists + `source_post` |
| World feed = top posts only | `world.world_feed` |
| Birth by interests | `birth_character` |
| Travel energy + ticks | `start_travel` / `tick_travel` |
| Room capacity / looking-in | `enter_room` |
| Missions | retrieve, bounty, personal |
| Abilities XP → mastery | `Ability.use` |
| Inventory / money / intentions | on `Character` |
| Procedural still-art glyphs | `_glyph` (zero assets) |
| Main lore | Dimenia / Above / Below / reincarnating child |

## Not yet (next growth)

- Full party / family / group Source channels as live multiplayer
- Land ownership upkeep economy
- NPC agendas with schedules
- Stealth perception gates
- Live visual page in `free_matrix` / `live_visual`

## Law

GitHub first · offline procedural · first arc completes deterministically by seed.
