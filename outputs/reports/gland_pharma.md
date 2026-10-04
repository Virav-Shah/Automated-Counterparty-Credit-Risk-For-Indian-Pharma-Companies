# Counterparty Credit Monitoring Report

Company: Gland Pharma

Period: FY25

Financial risk score: 2/100 (VERY LOW)

Higher scores indicate higher risk.

## Key risk drivers

- Working Capital: 2 risk points

## Five-year monitoring

| Period | Core score /80 | Total score /100 | Rating | Debt/EBITDA | Coverage | FCF/Debt |
|---|---:|---:|---|---:|---:|---:|
| FY21 | 0 | N/A | NOT SCORED | 0.00 | 240.40 | 20000.0% |
| FY22 | 0 | 0 | VERY LOW | 0.00 | 277.60 | 29000.0% |
| FY23 | 0 | 20 | LOW | 0.00 | 125.71 | 23500.0% |
| FY24 | 0 | 10 | VERY LOW | 0.62 | 50.91 | 73.2% |
| FY25 | 0 | 2 | VERY LOW | 0.37 | 74.44 | 150.0% |

FY21 total score is unavailable because FY20 growth inputs were not supplied. The core score uses four financial components consistently across five years.

## Peer position

Complex / Specialty / Healthcare Platforms (USER_DEFINED_BUSINESS_MODEL assignment). 2 other companies.

BELOW PEER MEDIAN. Peer median score: 23.50.

Peers exclude the company itself. A small peer group limits comparison strength.

## Early warnings

- [MEDIUM] Receivables grew faster than revenue. Observed 12.7%; threshold 10.3%.

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

Monitoring as of 2026-10-04. Priority: **WATCH**. Financial rating remains **VERY LOW**.

| Layer | Score | Classification | Data status |
|---|---:|---|---|
| Financial (FY25) | 2.00 /100 | VERY LOW | STALE; assumed period end 2025-03-31 |
| Market (2026-10-01) | 0.00 /100 | NORMAL | CURRENT |

## Why this priority

- Fundamental early-warning rules are triggered.
- Financial inputs end 2025-03-31 and are 552 days old; refresh before drawing current credit conclusions.

Action: Refresh missing market data and financials and investigate flagged developments.

Signal confirmation: NOT CONFIRMED.

## Market observations

30-session return: 1.2%. 90-session return: 24.1%. NIFTY Pharma 90-session return: 6.6%. Relative performance: 17.5%.

Current 30-session drawdown: -5.0%. 90-session maximum drawdown: -6.8%. Daily 30-session volatility: 1.5%. Volatility ratio: 0.59x. Volume ratio: 0.62x.

Source: https://finance.yahoo.com/quote/GLAND.NS/.
## Explainable alerts

- **[FINANCIAL/MEDIUM] RECEIVABLES_DETERIORATION**
  - What happened: Receivables grew faster than revenue; observed 0.12658227848101267, threshold 0.10326566637246248.
  - Why it matters: Collections may be lagging reported sales growth.
  - Action: Check receivable ageing and customer payment behaviour.
