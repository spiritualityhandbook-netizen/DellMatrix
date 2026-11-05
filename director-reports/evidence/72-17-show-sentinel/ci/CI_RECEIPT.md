# CI RECEIPT — verify-72-17 at PR #304 frozen head cc8ea8b

- Workflow: verify-72-17 (`.github/workflows/verify-72-17.yml`)
- Run: 42103309741 —
  https://github.com/spiritualityhandbook-netizen/DellMatrix/actions/runs/42103309741
- Head: cc8ea8b53ea7bfc8d22fc58ff9669b008fc06986 (PR #304's
  frozen correction head; this supplement does not amend it)
- Conclusion: **success** (all steps)

Steps of record in that run: manifest `sha256sum -c` at the
exact head; bounded surface probe re-run (q17_probe.py,
exit 0); Chromium located/installed on the runner and
started headless on loopback; the real-browser probe
(q17_browser_probe.py) drove the actual Studio UI.

Browser assertions (browser_assertions.json, this directory;
browser product + pinned SHA recorded inside it):

- B3 session token real (per-launch token served in the
  page; the authenticated user path carried it)
- B1 control seed (55[Set]>>56[Get]): user-visible console
  text contains NO `__RENDER__`
- B2 bare `09[Show]`: user-visible console text DOES contain
  `__RENDER__` — browser PRESENTATION measured in the DOM,
  not inferred from API transport

Raw artifacts preserved alongside: browser_console_log.txt
(full console text), browser_screenshot.png,
verify_q17_browser_probe.log, verify_q17_probe.log,
verify_chrome.log.

Realism label: AUTOMATED BROWSER (CDP) on a GitHub-hosted
runner — genuine Chromium, real DOM, real input events.
Not a human session; not REAL_USER_PATH. PR #304 remains
HELD for the Director's re-review; the Studio defect
remains OPEN; nothing here implements R-A/R-B/R-C.
