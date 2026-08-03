# Idea law — strong ideas only

An idea in DellMatrix is not a label.

| Field | Required for **strong** | Role |
|-------|-------------------------|------|
| label | yes | Name |
| detail | yes | What it is |
| goals | yes (≥1) | What evolution aims at |
| words | optional | Notes / tags |

**Weak idea** = label only → growth is nearly random.  
**Strong idea** = detail + goals → RingedGrowth biases toward goals.

Create form:

```text
create an idea called NAME detail: … goals: a; b; c
```

Strength helper: `python -m form.idea_create --check "…"`  
Seed strong templates: `python -m form.seed_strong_ideas`

Nursery still quarantines all growth until confirm (DEV / Blank / Ace / Worldwide).
