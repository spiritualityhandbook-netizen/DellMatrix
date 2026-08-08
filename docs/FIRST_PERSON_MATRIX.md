# First-person matrix walk

You are **inside** the lattice — always at the **centerpoint of a cell** (block or sphere dual).  
This is not a top-down map with a vision cone.

## Model

```
        up (F+)
          │
   W ──── ● ──── E     ● = you (center of cell)
          │
        down (F-)
          N/S on V axis
```

- **Cube dual:** orthogonal 6-neighbors (Minecraft-style faces).  
- **Sphere dual:** same centers; radial in/out + ring steps (toggle form).  
- **Move:** centerpoint → centerpoint only (integer H,V,F).  
- **Look:** pages of data ranked by **harmony + resonance + forces** that reach this cell.  
- **Pages:** detail/goals/words; presentation follows **perspective** + form.

## Keys (live)

| Key | Action |
|-----|--------|
| W / S | forward / back one cell |
| A / D | turn left / right (90°) |
| Shift+A / Shift+D | strafe left / right |
| R / F | up / down (F axis) |
| Q / E | look up / look down |
| Space | look level |
| Click a face | step that direction |

## Commands

```text
you> live
you> fp
you> fp forward
you> fp turn left
you> fp look up
you> goto 1 0 0
you> cube | sphere     # dual cell grammar
```

## Law

Floor locked · Nursery still required for growth · offline 127.0.0.1 only.
