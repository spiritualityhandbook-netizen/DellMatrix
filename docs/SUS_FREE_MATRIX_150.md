# SUS Free Matrix 150

## Run

```bash
python -m form.dell_matrix.free_matrix_150_audit
python -m form.dell_matrix.dynamic_view_switch
python -m form.dell_matrix.spatial_audio
python -m form.dell_matrix.free_matrix --smoke
```

Target: **150/150 PASS**.

## Shipped this cycle

| Module | Role |
|--------|------|
| `dynamic_view_switch.py` | Cycle / hotkey / undo view modes |
| `spatial_audio.py` | Pan · gain · ear cues from positions |
| `perspective_views.py` | first · third · parts · whole |
| `free_matrix.py` | One process UI + awake |
| `free_matrix_150_audit.py` | SUS 150 loop |

## Dynamic view switching

```python
from form.dell_matrix.dynamic_view_switch import switch_to, cycle, hotkey, undo
switch_to(p, "whole")
cycle(p)
hotkey(p, "1")  # first
hotkey(p, "c")  # cycle
undo(p)
```

## Spatial audio

```python
from form.dell_matrix.spatial_audio import cues_for_view
cues_for_view(p)  # pan -1..1, gain, ear L/R/C, band near/mid/far
```

Offline dicts for live UI / Web Audio / TTS.

## Law

GitHub first · user/architect any view · SUS 150 green.
