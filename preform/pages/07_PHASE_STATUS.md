# Page 07 — Phase Status & Build Order

Status: Living

## Code Phase 4 — TRUE
Pipeline owned on Unified-shaped host (`24_PIPELINE_HOST.py` + `28_PIPELINE_QUEUE.py`)

```bash
python preform/code/24_PIPELINE_HOST.py
python preform/code/24_UNIFIED_ENTRY.py --smoke
cd preform/seed && python pack_seed.py
```
