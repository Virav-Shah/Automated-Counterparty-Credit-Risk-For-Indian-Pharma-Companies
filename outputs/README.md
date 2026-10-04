# Generated outputs

Do not edit computed CSVs, company reports or dashboard files. Change inputs/templates/configuration, then rerun the pipeline.

## Financial artifacts

`data_validation.csv`, `credit_metrics.csv`, `credit_scores.csv`, `trend_analysis.csv`, `early_warning_alerts.csv`, `peer_analysis.csv` and `portfolio_summary.csv` contain the original seven-stage results. `reports/*.md` contains 20 company reports. `dashboard_data.json` retains full-precision financial records and, after a full V2 run, a `v2` payload. `dashboard.html` embeds this snapshot for offline use.

## Independent monitoring artifacts

| File | Contents |
|---|---|
| `credit_watchlist.csv` | One company row with unchanged financial score/rating, separate market score, priority, reasons, freshness, dates and actions |
| `market_indicators.csv` | Trading-window metrics, stress components, score, data status and missing/excluded-row details |
| `market_validation.csv` | Raw cached observation counts and first/last dates per instrument |
| `monitoring_alerts.csv` | Financial and market alerts with what/why/action fields |

All missing numeric values are blank in CSV, null in JSON and N/A in reports. Fractional returns/growth are decimals, not already multiplied by 100.

## Check status before using outputs

- `RUN_STATUS.json`: financial success/failure, stage, model/source hash and dashboard refresh.
- `V2_RUN_STATUS.json`: V2 success/failure, as-of date, model version, data coverage and input/config hashes.

A failed run can leave prior output files. A V2 failure after V1 succeeds leaves a financial-only dashboard and possibly older V2 CSVs. Partial financial runs do not refresh the dashboard and do not certify existing V2 artifacts. Check both manifests for a successful full workflow at the intended as-of date; see [operations](../docs/OPERATIONS.md).
