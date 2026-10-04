# Tests and verification

## Standard-library regression suite

```bash
python3 -m unittest discover -s tests -v
```

28 tests cover financial formulas/boundaries and full V2 integration. No internet access is required. Temporary-directory outputs prevent tests from overwriting the delivered snapshot.

- `test_crm.py`: source coverage, chronology, independently calculated ratios, score reconciliation and boundaries, unavailable first-year growth, zero denominators, new debt from zero, alert thresholds/migration, peers and failed input/model runs.
- `test_v2.py`: independent trading windows and sample volatility, drawdown recovery versus maximum drawdown, exact benchmark endpoints, holiday placeholders, missing/flat/stale histories, market validation, adjusted-close/split-volume decoding,  unchanged financial ratings, priority rules, aligned confirmation, entity transitions and end-to-end output generation.

The integration test uses the shipped cached snapshot and its explicit 2026-10-04 date. If you intentionally replace the fixture data, update its expected coverage assertions alongside the documented snapshot counts.

## Optional browser smoke test

Requires Node.js, Playwright and a compatible Chrome/Chromium executable. This is an optional development dependency; it is not needed to run the project. Set `NODE_PATH` if Playwright is installed outside this repository; set `CHROME_PATH` to use a system browser.

```bash
CHROME_PATH='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' node tests/browser_smoke.cjs
```

The script opens the generated local HTML, checks watchlist/drilldown, priority/group/search filters, sort, watchlist downloads, view switching, financial baseline, mobile overflow and JavaScript errors. Screenshots are written to an OS temporary folder; it changes no project inputs.

After template/UI changes, regenerate the dashboard before this check. Do not broaden test runs unnecessarily after all required checks pass; add targeted cases when a new behavior or failure needs coverage.
