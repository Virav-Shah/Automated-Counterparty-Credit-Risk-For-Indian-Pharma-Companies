# Counterparty Credit Monitoring Report

Company: Cipla

Period: FY25

Financial risk score: 7/100 (VERY LOW)

Higher scores indicate higher risk.

## Key risk drivers

- Working Capital: 5 risk points
- Earnings: 2 risk points

## Five-year monitoring

| Period | Core score /80 | Total score /100 | Rating | Debt/EBITDA | Coverage | FCF/Debt |
|---|---:|---:|---|---:|---:|---:|
| FY21 | 0 | N/A | NOT SCORED | 0.66 | 19.78 | 109.4% |
| FY22 | 0 | 0 | VERY LOW | 0.34 | 33.03 | 196.5% |
| FY23 | 0 | 12 | VERY LOW | 0.16 | 35.05 | 407.8% |
| FY24 | 0 | 5 | VERY LOW | 0.08 | 60.12 | 865.4% |
| FY25 | 0 | 7 | VERY LOW | 0.07 | 76.27 | 1020.8% |

FY21 total score is unavailable because FY20 growth inputs were not supplied. The core score uses four financial components consistently across five years.

## Peer position

Global Generics & Diversified (USER_DEFINED_BUSINESS_MODEL assignment). 7 other companies.

ABOVE PEER MEDIAN. Peer median score: 0.00.

Peers exclude the company itself. A small peer group limits comparison strength.

## Early warnings

- [MEDIUM] Receivables grew faster than revenue. Observed 17.6%; threshold 9.1%.

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
| Financial (FY25) | 7.00 /100 | VERY LOW | STALE; assumed period end 2025-03-31 |
| Market (2026-10-01) | 25.00 /100 | WATCH | CURRENT |

## Why this priority

- Fundamental early-warning rules are triggered.
- Independent market stress indicates WATCH.
- Financial inputs end 2025-03-31 and are 552 days old; refresh before drawing current credit conclusions.

Action: Refresh missing market data and financials and investigate flagged developments.

Signal confirmation: NOT CONFIRMED.

## Market observations

30-session return: -5.5%. 90-session return: -4.1%. NIFTY Pharma 90-session return: 6.6%. Relative performance: -10.7%.

Current 30-session drawdown: -6.5%. 90-session maximum drawdown: -9.0%. Daily 30-session volatility: 1.0%. Volatility ratio: 0.66x. Volume ratio: 1.03x.

Source: https://finance.yahoo.com/quote/CIPLA.NS/.
## Explainable alerts

- **[FINANCIAL/MEDIUM] RECEIVABLES_DETERIORATION**
  - What happened: Receivables grew faster than revenue; observed 0.1759921123983239, threshold 0.09102196011484431.
  - Why it matters: Collections may be lagging reported sales growth.
  - Action: Check receivable ageing and customer payment behaviour.
- **[MARKET/MEDIUM] RELATIVE_UNDERPERFORMANCE**
  - What happened: Company underperformed NIFTY Pharma over 90 trading sessions
  - Why it matters: Sector-relative weakness may precede reported financial deterioration
  - Action: Check recent filings and business developments.
