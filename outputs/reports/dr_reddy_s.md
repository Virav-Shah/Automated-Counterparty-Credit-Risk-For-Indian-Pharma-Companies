# Counterparty Credit Monitoring Report

Company: Dr. Reddy's

Period: FY25

Financial risk score: 0/100 (VERY LOW)

Higher scores indicate higher risk.

## Key risk drivers

No scored risk drivers.

## Five-year monitoring

| Period | Core score /80 | Total score /100 | Rating | Debt/EBITDA | Coverage | FCF/Debt |
|---|---:|---:|---|---:|---:|---:|
| FY21 | 0 | N/A | NOT SCORED | 0.68 | 32.97 | 84.2% |
| FY22 | 0 | 10 | VERY LOW | 0.69 | 37.42 | 65.1% |
| FY23 | 0 | 0 | VERY LOW | 0.19 | 42.67 | 357.2% |
| FY24 | 0 | 8 | VERY LOW | 0.22 | 38.13 | 272.5% |
| FY25 | 0 | 0 | VERY LOW | 0.55 | 24.46 | 79.4% |

FY21 total score is unavailable because FY20 growth inputs were not supplied. The core score uses four financial components consistently across five years.

## Peer position

Global Generics & Diversified (USER_DEFINED_BUSINESS_MODEL assignment). 7 other companies.

BELOW PEER MEDIAN. Peer median score: 2.00.

Peers exclude the company itself. A small peer group limits comparison strength.

## Early warnings

- [MEDIUM] Debt growth exceeds the threshold. Observed 156.6%; threshold 20.0%.

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
| Financial (FY25) | 0.00 /100 | VERY LOW | STALE; assumed period end 2025-03-31 |
| Market (2026-10-01) | 30.00 /100 | WATCH | CURRENT |

## Why this priority

- Fundamental early-warning rules are triggered.
- Independent market stress indicates WATCH.
- Financial inputs end 2025-03-31 and are 552 days old; refresh before drawing current credit conclusions.

Action: Refresh missing market data and financials and investigate flagged developments.

Signal confirmation: NOT CONFIRMED.

## Market observations

30-session return: 3.1%. 90-session return: -8.8%. NIFTY Pharma 90-session return: 6.6%. Relative performance: -15.5%.

Current 30-session drawdown: -3.7%. 90-session maximum drawdown: -16.9%. Daily 30-session volatility: 1.3%. Volatility ratio: 0.76x. Volume ratio: 1.56x.

Source: https://finance.yahoo.com/quote/DRREDDY.NS/.
## Explainable alerts

- **[FINANCIAL/MEDIUM] DEBT_ACCELERATION**
  - What happened: Debt growth exceeds the threshold; observed 1.5659340659340661, threshold 0.2.
  - Why it matters: Borrowing increased faster than the monitoring threshold.
  - Action: Check acquisition funding and debt drawdowns.
- **[MARKET/MEDIUM] RELATIVE_UNDERPERFORMANCE**
  - What happened: Company underperformed NIFTY Pharma over 90 trading sessions
  - Why it matters: Sector-relative weakness may precede reported financial deterioration
  - Action: Check recent filings and business developments.
- **[MARKET/MEDIUM] VOLUME_SPIKE**
  - What happened: Trading volume increased versus the prior 30-session average
  - Why it matters: Unusual trading activity needs context and is not itself credit deterioration
  - Action: Check announcements and corporate actions before escalating.
