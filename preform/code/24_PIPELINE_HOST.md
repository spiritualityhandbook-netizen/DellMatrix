> STATUS: NOT IN USE — preform/src are earlier generations of DellMatrix, retained as design history and reference. The production runtime is form/ (verified at commit 11933da, 2026-10-30). This file does not describe current behavior.

# 24_PIPELINE_HOST — UnifiedEntry owns PipelineQueue

Status: TRUE

Pattern for living core:
1. `pipeline = PipelineQueue()` on boot
2. successful command → `pipeline.add(label)`
3. `confirm(n)` from UI/status
4. render PIPELINE section via `pipeline.render_lines()`

```bash
python preform/code/24_PIPELINE_HOST.py
python preform/code/28_PIPELINE_QUEUE.py
```
