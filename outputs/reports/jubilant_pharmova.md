# Counterparty Credit Monitoring Report

Company: Jubilant Pharmova

Period: FY25

Financial risk score: 22/100 (LOW)

Higher scores indicate higher risk.

## Key risk drivers

- Leverage: 12 risk points
- Servicing: 8 risk points
- Working Capital: 2 risk points

## Five-year monitoring

| Period | Core score /80 | Total score /100 | Rating | Debt/EBITDA | Coverage | FCF/Debt |
|---|---:|---:|---|---:|---:|---:|
| FY21 | 20 | N/A | NOT SCORED | 2.20 | 3.58 | 21.5% |
| FY22 | 25 | 37 | MODERATE | 2.42 | 3.71 | 14.0% |
| FY23 | 65 | 74 | CRITICAL | 4.17 | 1.55 | -2.2% |
| FY24 | 45 | 49 | MODERATE | 3.11 | 2.00 | 7.9% |
| FY25 | 20 | 22 | LOW | 2.07 | 3.57 | 20.4% |

FY21 total score is unavailable because FY20 growth inputs were not supplied. The core score uses four financial components consistently across five years.

## Peer position

Complex / Specialty / Healthcare Platforms (USER_DEFINED_BUSINESS_MODEL assignment). 2 other companies.

ABOVE PEER MEDIAN. Peer median score: 13.50.

Peers exclude the company itself. A small peer group limits comparison strength.

## Early warnings

- [MEDIUM] Receivables grew faster than revenue. Observed 11.6%; threshold 10.5%.

## Recommended monitoring

Watchlist monitoring: investigate alerts and reassess when the next financial results arrive.

## Data and methodology

Source: pharma_financials_5yr.csv. Amounts: Source units (currency and scale not supplied). Model version: 1.0.0.

Earnings bands were not specified in the planner. Proposed points: growth below -10%: 10; -10% to below 0%: 7; 0% to below 5%: 4; 5% to below 10%: 2; at least 10%: 0.

Working capital uses the maximum of receivables-growth minus revenue-growth, inventory-growth minus revenue-growth, and zero. Proposed points: gap <=0: 0; >0 to 5 percentage points: 2; >5 to 10: 5; >10 to 20: 8; >20: 10.

Company-to-peer assignments are provisional analyst assumptions, not assignments supplied by the planner. Review config/peer_groups.csv.

FY21 lacks FY20 growth inputs. Its total financial score and rating are unavailable; its observed four-component core score is shown out of 80. No missing component is imputed as zero.

Financial scores are rule-based monitoring indicators, not calibrated default probabilities. Source financial values and reporting scope have not been independently verified.

# Credit monitoring review

Monitoring as of 2026-10-04. Priority: **WATCH**. Financial rating remains **LOW**.

| Layer | Score | Classification | Data status |
|---|---:|---|---|
| Financial (FY25) | 22.00 /100 | LOW | STALE; assumed period end 2025-03-31 |
| Market (2026-10-01) | 10.00 /100 | NORMAL | CURRENT |

## Why this priority

- Fundamental early-warning rules are triggered.
- Financial inputs end 2025-03-31 and are 552 days old; refresh before drawing current credit conclusions.

Action: Refresh missing market data and financials and investigate flagged developments.

Signal confirmation: NOT CONFIRMED.

## Market observations

30-session return: 15.1%. 90-session return: -0.3%. NIFTY Pharma 90-session return: 6.6%. Relative performance: -6.9%.

Current 30-session drawdown: -6.8%. 90-session maximum drawdown: -15.4%. Daily 30-session volatility: 1.9%. Volatility ratio: 1.11x. Volume ratio: 0.93x.

Source: https://finance.yahoo.com/quote/JUBLPHARMA.NS/.
## Explainable alerts

- **[FINANCIAL/MEDIUM] RECEIVABLES_DETERIORATION**
  - What happened: Receivables grew faster than revenue; observed 0.11570247933884303, threshold 0.1049888309754281.
  - Why it matters: Collections may be lagging reported sales growth.
  - Action: Check receivable ageing and customer payment behaviour.
- **[MARKET/MEDIUM] RELATIVE_UNDERPERFORMANCE**
  - What happened: Company underperformed NIFTY Pharma over 90 trading sessions
  - Why it matters: Sector-relative weakness may precede reported financial deterioration
  - Action: Check recent filings and business developments.
