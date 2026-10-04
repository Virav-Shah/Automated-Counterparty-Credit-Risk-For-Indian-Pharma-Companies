# Counterparty Credit Monitoring Report

Company: Sun Pharma

Period: FY25

Financial risk score: 6/100 (VERY LOW)

Higher scores indicate higher risk.

## Key risk drivers

- Liquidity: 2 risk points
- Earnings: 2 risk points
- Working Capital: 2 risk points

## Five-year monitoring

| Period | Core score /80 | Total score /100 | Rating | Debt/EBITDA | Coverage | FCF/Debt |
|---|---:|---:|---|---:|---:|---:|
| FY21 | 6 | N/A | NOT SCORED | 0.39 | 53.13 | 173.3% |
| FY22 | 0 | 2 | VERY LOW | 0.15 | 63.15 | 490.1% |
| FY23 | 0 | 5 | VERY LOW | 0.54 | 54.37 | 129.3% |
| FY24 | 12 | 14 | VERY LOW | 0.24 | 45.01 | 289.4% |
| FY25 | 2 | 6 | VERY LOW | 0.14 | 59.90 | 483.7% |

FY21 total score is unavailable because FY20 growth inputs were not supplied. The core score uses four financial components consistently across five years.

## Peer position

Global Generics & Diversified (USER_DEFINED_BUSINESS_MODEL assignment). 7 other companies.

ABOVE PEER MEDIAN. Peer median score: 0.00.

Peers exclude the company itself. A small peer group limits comparison strength.

## Early warnings

- [MEDIUM] Receivables grew faster than revenue. Observed 8.2%; threshold 7.3%.

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
| Financial (FY25) | 6.00 /100 | VERY LOW | STALE; assumed period end 2025-03-31 |
| Market (2026-10-01) | 20.00 /100 | NORMAL | CURRENT |

## Why this priority

- Fundamental early-warning rules are triggered.
- Financial inputs end 2025-03-31 and are 552 days old; refresh before drawing current credit conclusions.

Action: Refresh missing market data and financials and investigate flagged developments.

Signal confirmation: NOT CONFIRMED.

## Market observations

30-session return: -5.2%. 90-session return: -1.9%. NIFTY Pharma 90-session return: 6.6%. Relative performance: -8.5%.

Current 30-session drawdown: -9.3%. 90-session maximum drawdown: -10.0%. Daily 30-session volatility: 1.3%. Volatility ratio: 0.95x. Volume ratio: 1.48x.

Source: https://finance.yahoo.com/quote/SUNPHARMA.NS/.
## Explainable alerts

- **[FINANCIAL/MEDIUM] RECEIVABLES_DETERIORATION**
  - What happened: Receivables grew faster than revenue; observed 0.0815850815850816, threshold 0.07307668515578292.
  - Why it matters: Collections may be lagging reported sales growth.
  - Action: Check receivable ageing and customer payment behaviour.
- **[MARKET/MEDIUM] RELATIVE_UNDERPERFORMANCE**
  - What happened: Company underperformed NIFTY Pharma over 90 trading sessions
  - Why it matters: Sector-relative weakness may precede reported financial deterioration
  - Action: Check recent filings and business developments.
- **[MARKET/MEDIUM] MARKET_DRAWDOWN**
  - What happened: Adjusted price is below its 30-session peak
  - Why it matters: A sustained drawdown warrants closer monitoring
  - Action: Investigate recent catalysts and reassess monitoring frequency.
