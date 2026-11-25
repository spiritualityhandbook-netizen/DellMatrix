# RUN RECORD — Studio Browser Acceptance (GitHub Actions)

- Workflow: `.github/workflows/studio-browser-acceptance.yml`
  ("Studio Browser Acceptance")
- Run: 41750912673 —
  https://github.com/spiritualityhandbook-netizen/DellMatrix/actions/runs/41750912673
- Trigger: pull_request (PR #258), paths gui/** + the workflow file
- Code head executed: 5d889e3be058c395b3928095488cc0aed46b91c3
  (branch uni/studio-browser-acceptance; base db61de0a1a1391c83237a0fab016d814f0c10af0)
- Runner: ubuntu-latest (GitHub-hosted); job `browser-acceptance`
  (ID 126315503183), conclusion SUCCESS
- Engine: Chrome/156.0.8078.47 (HeadlessChrome; see chrome_version.json)
- Server: `python3 -m gui.server --owner BrowserCI --port 8765`
  on the same runner, loopback bind, no --allow-remote
- Driver: `python3 gui/browser_acceptance.py`
  (PAGE_URL=http://127.0.0.1:8765/, CDP_PORT=9333)
- Attempt 1 verdict: **BROWSER-ACCEPT: 16/16** (driver.log,
  assertions.json in this bundle; artifact downloaded with
  `gh run download 41750912673` and copied byte-identical)
- Console: exactly one raw error candidate in the whole session —
  the favicon.ico 404 network log entry — excluded by the driver's
  disclosed favicon-only rule; app errors: ZERO (console_events.json)
- Screenshot: studio_browser.png, 159,387 bytes, 1440x857 PNG,
  captured in-session after the assertions passed. It shows the
  Studio after the driven run: transport "done · ok", owner
  BrowserCI, Dell Rack (Core I list), Flow Canvas with the 55[Set]
  and 56[Get] cards painted atom-ok ("✓ ran") under a
  "✓ CHAIN OK — 2 atoms" verdict, the seed in the editor,
  Inspector "Last result — OK" with the run's result JSON,
  Store "1 keys", and the Receipts row for the run marked OK.
  (Contents verified by direct inspection of the downloaded PNG.)
- Attempt 2 (rerun of the same run ID, repeatability check):
  see packet §3 for its verdict; its driver log is preserved in
  the workspace evidence dir and, if green, is cited there rather
  than bundled, to keep this bundle the single canonical attempt.

Realism label: AUTOMATED BROWSER (CDP) on CI runner — genuine
Chromium, real DOM, real input-pipeline events; NOT a human
session; NOT REAL_USER_PATH.
