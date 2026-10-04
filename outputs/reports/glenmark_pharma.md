# Counterparty Credit Monitoring Report

Company: Glenmark Pharma

Period: FY25

Financial risk score: 0/100 (VERY LOW)

Higher scores indicate higher risk.

## Key risk drivers

No scored risk drivers.

## Five-year monitoring

| Period | Core score /80 | Total score /100 | Rating | Debt/EBITDA | Coverage | FCF/Debt |
|---|---:|---:|---|---:|---:|---:|
| FY21 | 20 | N/A | NOT SCORED | 2.20 | 4.65 | 21.2% |
| FY22 | 9 | 9 | VERY LOW | 1.86 | 5.51 | 25.2% |
| FY23 | 20 | 27 | LOW | 2.02 | 5.18 | 17.4% |
| FY24 | 26 | 35 | MODERATE | 1.82 | 1.43 | 24.7% |
| FY25 | 0 | 0 | VERY LOW | 0.51 | 8.79 | 116.4% |

FY21 total score is unavailable because FY20 growth inputs were not supplied. The core score uses four financial components consistently across five years.

## Peer position

Global Generics & Diversified (USER_DEFINED_BUSINESS_MODEL assignment). 7 other companies.

BELOW PEER MEDIAN. Peer median score: 2.00.

Peers exclude the company itself. A small peer group limits comparison strength.

## Early warnings

No triggered warnings in this period.

## Recommended monitoring

Routine monitoring: refresh at the next financial reporting cycle.

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
| Market (2026-10-01) | 15.00 /100 | NORMAL | CURRENT |

## Why this priority

- Financial inputs end 2025-03-31 and are 552 days old; refresh before drawing current credit conclusions.

Action: Refresh missing market data and financials and investigate flagged developments.

Signal confirmation: NOT CONFIRMED.

## Market observations

30-session return: 3.9%. 90-session return: -0.2%. NIFTY Pharma 90-session return: 6.6%. Relative performance: -6.8%.

Current 30-session drawdown: -7.2%. 90-session maximum drawdown: -10.4%. Daily 30-session volatility: 1.9%. Volatility ratio: 1.01x. Volume ratio: 1.68x.

Source: https://finance.yahoo.com/quote/GLENMARK.NS/.
## Explainable alerts

- **[MARKET/MEDIUM] RELATIVE_UNDERPERFORMANCE**
  - What happened: Company underperformed NIFTY Pharma over 90 trading sessions
  - Why it matters: Sector-relative weakness may precede reported financial deterioration
  - Action: Check recent filings and business developments.
- **[MARKET/MEDIUM] VOLUME_SPIKE**
  - What happened: Trading volume increased versus the prior 30-session average
  - Why it matters: Unusual trading activity needs context and is not itself credit deterioration
  - Action: Check announcements and corporate actions before escalating.
