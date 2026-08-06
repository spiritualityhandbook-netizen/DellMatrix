# Live two-way visual

**Status:** Horizon feature implemented as opt-in bridge.  
**Default visual remains the offline snapshot.**

## What it is

A localhost-only HTTP bridge so the panel both **shows** live state and **sends** commands that execute on the running Program.

- Browser → `POST /cmd` with `{ "cmd": "grow ideas 1" }`
- Python executes through the same path the REPL uses
- Response includes fresh state (nodes, nursery, avatar, form)
- `GET /state` returns current snapshot

## Constraints preserved

- 127.0.0.1 only (offline core)
- Growth still only produces Nursery proposals until `confirm`
- Floor lock untouched
- Snapshot `visual` command unchanged

## How to use

```text
you> live
# or
you> visual live
```

Then open the printed URL (default `http://127.0.0.1:8765/`) in a browser.

## Files

- `form/dell_matrix/live_visual.py` — server + minimal live UI
- `Program.live_visual()` — starts the bridge
- REPL: `live` / `visual live`

## Law

DellMatrix enhances itself under the same Nursery + Floor rules.  
No silent live-plane writes. No network beyond localhost.
