# Perspectives & one-process Free Matrix

## One process

```bash
python -m form.dell_matrix.free_matrix
python -m form.dell_matrix.free_matrix --awake-every 30
```

- **Background thread:** live UI (`http://127.0.0.1:8765/`)
- **Main thread:** awake growth loop until Ctrl+C

No second terminal required.

## Who sees what

| Mode | Meaning |
|------|--------|
| **first** | First person — only what’s in the forward vision cone |
| **third** | Third person — nodes in a ring around the body |
| **parts** | Partial — filtered slice (skins / radius) |
| **whole** | Omniscient — full plane inventory |

| Role | Default mode | Can switch to any? |
|------|--------------|--------------------|
| **user** | first | **Yes** |
| **architect** | whole | **Yes** |
| ai_first (companion) | first | Only if user/architect sets it |
| ai_third (witness) | third | Only if user/architect sets it |
| ai_parts (scout) | parts | Only if user/architect sets it |
| ai_whole (overseer) | whole | Only if user/architect sets it |

**Law:** User or architect always can see any mode by choice.

```python
from form.dell_matrix import free_matrix as fm
p = fm.open_world()

fm.see(p, "user", "first")
fm.see(p, "user", "third")
fm.see(p, "architect", "whole")

fm.set_view(p, "companion", "whole")   # user grants full sight
fm.set_view(p, "scout", "parts")
fm.list_views(p)
```

## Modules

- `form/dell_matrix/perspective_views.py` — modes + registry
- `form/dell_matrix/free_matrix.py` — one process + see/set_view
- `form/dell_matrix/vision.py` — cone math used by **first**

## Track notes

- B primary (this)
- A support (awake loop in same process)
- D seed (`draw_frame` includes mode)
- C trading skipped
