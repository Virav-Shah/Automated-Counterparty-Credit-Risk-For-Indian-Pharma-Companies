# Counterparty Credit Monitoring Report

Company: Alkem Labs

Period: FY25

Financial risk score: 4/100 (VERY LOW)

Higher scores indicate higher risk.

## Key risk drivers

- Earnings: 2 risk points
- Working Capital: 2 risk points

## Five-year monitoring

| Period | Core score /80 | Total score /100 | Rating | Debt/EBITDA | Coverage | FCF/Debt |
|---|---:|---:|---|---:|---:|---:|
| FY21 | 0 | N/A | NOT SCORED | 0.88 | 25.34 | 78.4% |
| FY22 | 0 | 2 | VERY LOW | 0.77 | 33.67 | 67.1% |
| FY23 | 0 | 4 | VERY LOW | 0.75 | 12.13 | 65.6% |
| FY24 | 0 | 4 | VERY LOW | 0.37 | 23.78 | 180.0% |
| FY25 | 0 | 4 | VERY LOW | 0.23 | 35.69 | 296.8% |

FY21 total score is unavailable because FY20 growth inputs were not supplied. The core score uses four financial components consistently across five years.

## Peer position

India-Focused / Branded Formulations (USER_DEFINED_BUSINESS_MODEL assignment). 5 other companies.

ABOVE PEER MEDIAN. Peer median score: 2.00.

Peers exclude the company itself. A small peer group limits comparison strength.

## Early warnings

- [MEDIUM] Receivables grew faster than revenue. Observed 11.5%; threshold 9.1%.

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
| Financial (FY25) | 4.00 /100 | VERY LOW | STALE; assumed period end 2025-03-31 |
| Market (2026-10-01) | 20.00 /100 | NORMAL | CURRENT |

## Why this priority

- Fundamental early-warning rules are triggered.
- Financial inputs end 2025-03-31 and are 552 days old; refresh before drawing current credit conclusions.

Action: Refresh missing market data and financials and investigate flagged developments.

Signal confirmation: NOT CONFIRMED.

## Market observations

30-session return: -3.0%. 90-session return: -3.2%. NIFTY Pharma 90-session return: 6.6%. Relative performance: -9.8%.

Current 30-session drawdown: -4.5%. 90-session maximum drawdown: -12.4%. Daily 30-session volatility: 1.3%. Volatility ratio: 0.88x. Volume ratio: 2.07x.

Source: https://finance.yahoo.com/quote/ALKEM.NS/.
## Explainable alerts

- **[FINANCIAL/MEDIUM] RECEIVABLES_DETERIORATION**
  - What happened: Receivables grew faster than revenue; observed 0.11538461538461542, threshold 0.09093779602147145.
  - Why it matters: Collections may be lagging reported sales growth.
  - Action: Check receivable ageing and customer payment behaviour.
- **[MARKET/MEDIUM] RELATIVE_UNDERPERFORMANCE**
  - What happened: Company underperformed NIFTY Pharma over 90 trading sessions
  - Why it matters: Sector-relative weakness may precede reported financial deterioration
  - Action: Check recent filings and business developments.
- **[MARKET/MEDIUM] VOLUME_SPIKE**
  - What happened: Trading volume increased versus the prior 30-session average
  - Why it matters: Unusual trading activity needs context and is not itself credit deterioration
  - Action: Check announcements and corporate actions before escalating.
