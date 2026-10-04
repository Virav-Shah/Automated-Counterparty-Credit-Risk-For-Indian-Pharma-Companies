# Counterparty Credit Monitoring & Early-Warning System

A finance-focused monitoring project covering 19 Indian pharmaceutical and biopharmaceutical businesses over FY21–FY25. The supplied company financial and narrative records are simulated; cached market prices are public historical observations. Financial analysis produces an internal credit-risk score; independent market signals guide review intensity. Peer comparisons use business models and operating characteristics.

## Run and verify

Requires Python 3.10+; calculations and tests use the standard library.

```bash
cd '/Users/viravshah/Documents/CRM Project'
python3 run.py --as-of 2026-10-04
python3 -m unittest discover -s tests -v
python3 -m http.server 8765 --bind 127.0.0.1 --directory outputs
```

Open [the local dashboard](http://127.0.0.1:8765/dashboard.html) or `outputs/dashboard.html` directly. Regenerate outputs and refresh the browser after edits. Use `python3 run.py --refresh-market` for a public-price refresh; requires internet and system curl. Use `--financial-only` for the original seven financial stages.

Run the Streamlit app locally with `python3 -m pip install -r requirements.txt` and `streamlit run app.py`. See [Streamlit deployment instructions](docs/STREAMLIT_DEPLOYMENT.md) to publish it with Community Cloud.

Alternate financial/market inputs and model settings are supported through `--input`, `--market-input`, `--config`, `--monitoring-config`, `--peers`, `--output`, `--as-of` and `--stage`. See `python3 run.py --help`. A partial stage run does not update the dashboard.

## Current scope

- P&L-derived analysis: revenue and earnings growth, EBITDA/EBIT trends and margins, interest servicing.
- Balance-sheet analysis: debt, cash, net leverage, current liquidity, receivables and inventory growth.
- Cash-flow analysis: operating cash flow, capex, free cash flow and debt support.
- Six financial scoring categories; historical migration, eight early-warning rules and other-company peer comparisons.
- Independent market stress from sector-relative returns, drawdown, volatility and volume; explainable watchlist priorities and entity-transition reviews.
- Company drilldowns, financial history, filters, CSV downloads and printable reports.

**Qualitative scoring has been removed entirely from active code, configuration, dashboard, alerts, priorities and generated company reports.** Research remains in `data/qualitative/` for narrative use in the project report. Historical scored input/policy files are preserved under its `archive/` folder; they are not read by the application. `report_evidence.csv` is a score-free reference.

Actual credit-limit utilization is not implemented because approved limits, outstanding exposures, commitments, collateral and overdue balances have not been supplied. The analyst report distinguishes completed counterparty analysis from a proposed limit-monitoring workflow. Internal financial risk bands are not external agency ratings or default probabilities.

## User-defined peer groups

| Group | Companies | Count |
|---|---|---:|
| Global Generics & Diversified | Sun, Dr. Reddy’s, Cipla, Zydus, Lupin, Aurobindo, Glenmark, Torrent | 8 |
| India-Focused / Branded Formulations | Mankind, Alkem, Abbott India, Ipca, Ajanta | 5 |
| API / CDMO / Contract Manufacturing | Divi’s, Laurus, Piramal Pharma | 3 |
| Complex / Specialty / Healthcare Platforms | Biocon, Gland, Jubilant Pharmova | 3 |

Groups follow revenue sources, geography, regulation, working capital and operating risk; market capitalization and credit scores are not grouping inputs. Assignments are marked `USER_DEFINED_BUSINESS_MODEL`. Benchmarks exclude the company being assessed. See [the complete rationale](docs/PEER_GROUPS.md).

## Delivered snapshot — 2026-10-04

95 financial observations; 19 financial validation checks pass; 76 full financial scores and 19 FY21 core-only records; 103 historical financial alerts. All 19 active companies have complete market stress inputs dated 2026-10-01. The active universe excludes the archived source records of one entity.

Current priority: 18 WATCH and 1 ENHANCED MONITORING (Mankind). Removing the qualitative overlay removes Sun’s former qualitative-driven escalation. Its financial score remains 6/100, VERY LOW. All FY25 financial inputs are stale under the 540-day policy at this snapshot date; no current combined deterioration is confirmed.

FY21 full scores are unavailable because FY20 growth inputs were not supplied. Currency, units and standalone/consolidated scope for the original financial CSV are unconfirmed. Amounts remain in source units. Group labels are project analytical classifications, not identical business mixes.

## Documentation

- [Professional analyst report](reports/Indian_Pharma_Counterparty_Credit_Report.docx): the original report format, now focused on Cipla for detailed company analysis, with sector and peer-group context, statement-analysis methods, seven-peer benchmarking, moderate/severe stress testing, an audited FY25-FY26 retrospective check, counterparty review and proposed credit-limit monitoring. [Readable Markdown copy](reports/Indian_Pharma_Counterparty_Credit_Report.md) and [report build instructions](reports/README.md).
- Reproduce Cipla stress calculations with `python3 scripts/cipla_stress_test.py`, then rebuild the original report using `python3 scripts/build_cipla_report.py`.
- [Streamlit Community Cloud deployment guide](docs/STREAMLIT_DEPLOYMENT.md): local setup and public-hosting instructions for `app.py`.
- [Independent calculation validation](reports/result_validation.json): 757 numerical comparisons pass against project inputs. [External reconciliation](reports/external_benchmarks.json) identifies differences from Biocon/Laurus FY25 disclosures; results remain provisional. The report distinguishes peer/index benchmarking, a dated CARE rating comparison, calculation testing and source validation.
- [Finance report working brief](docs/PROJECT_REPORT_BRIEF.md): background research and initial all-company analysis plan; the delivered report's issuer-level scope is Cipla only.
- [Methodology](docs/METHODOLOGY.md): financial/market formulas, score thresholds and priority rules.
- [Peer groups](docs/PEER_GROUPS.md): user assignments and comparability limits.
- [Source code](src/README.md), [architecture](docs/ARCHITECTURE.md), [configuration](config/README.md).
- [Data](data/README.md), [dictionary](docs/DATA_DICTIONARY.md), [operations](docs/OPERATIONS.md), [tests](tests/README.md), [outputs](outputs/README.md).

28 regression tests pass, covering original financial rules, independent market windows, date alignment, priority decisions, revised peer membership and removal of qualitative influence. Optional Chrome smoke tests verify desktop/mobile behavior and watchlist downloads.
