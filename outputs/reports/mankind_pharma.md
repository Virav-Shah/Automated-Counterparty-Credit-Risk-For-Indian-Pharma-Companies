# Counterparty Credit Monitoring Report

Company: Mankind Pharma

Period: FY25

Financial risk score: 20/100 (LOW)

Higher scores indicate higher risk.

## Key risk drivers

- Leverage: 12 risk points
- Working Capital: 8 risk points

## Five-year monitoring

| Period | Core score /80 | Total score /100 | Rating | Debt/EBITDA | Coverage | FCF/Debt |
|---|---:|---:|---|---:|---:|---:|
| FY21 | 0 | N/A | NOT SCORED | 0.14 | 35.95 | 383.0% |
| FY22 | 0 | 10 | VERY LOW | 0.44 | 31.21 | 72.6% |
| FY23 | 0 | 10 | VERY LOW | 0.13 | 35.21 | 379.6% |
| FY24 | 0 | 8 | VERY LOW | 0.07 | 58.46 | 838.9% |
| FY25 | 12 | 20 | LOW | 2.32 | 15.61 | 25.1% |

FY21 total score is unavailable because FY20 growth inputs were not supplied. The core score uses four financial components consistently across five years.

## Peer position

India-Focused / Branded Formulations (USER_DEFINED_BUSINESS_MODEL assignment). 4 other companies.

ABOVE PEER MEDIAN. Peer median score: 3.00.

Peers exclude the company itself. A small peer group limits comparison strength.

## Early warnings

- [MEDIUM] Debt growth exceeds the threshold. Observed 3927.8%; threshold 20.0%.
- [MEDIUM] Receivables grew faster than revenue. Observed 30.9%; threshold 17.9%.
- [HIGH] Financial risk score increased materially year over year. Observed 12.00; threshold 10.00.

## Recommended monitoring

Enhanced credit monitoring: review leverage, liquidity and cash generation before the next review.

## Data and methodology

Source: pharma_financials_5yr.csv. Amounts: Source units (currency and scale not supplied). Model version: 1.0.0.

Earnings bands were not specified in the planner. Proposed points: growth below -10%: 10; -10% to below 0%: 7; 0% to below 5%: 4; 5% to below 10%: 2; at least 10%: 0.

Working capital uses the maximum of receivables-growth minus revenue-growth, inventory-growth minus revenue-growth, and zero. Proposed points: gap <=0: 0; >0 to 5 percentage points: 2; >5 to 10: 5; >10 to 20: 8; >20: 10.

Company-to-peer assignments are provisional analyst assumptions, not assignments supplied by the planner. Review config/peer_groups.csv.

FY21 lacks FY20 growth inputs. Its total financial score and rating are unavailable; its observed four-component core score is shown out of 80. No missing component is imputed as zero.

Financial scores are rule-based monitoring indicators, not calibrated default probabilities. Source financial values and reporting scope have not been independently verified.

# Credit monitoring review

Monitoring as of 2026-10-04. Priority: **ENHANCED MONITORING**. Financial rating remains **LOW**.

| Layer | Score | Classification | Data status |
|---|---:|---|---|
| Financial (FY25) | 20.00 /100 | LOW | STALE; assumed period end 2025-03-31 |
| Market (2026-10-01) | 0.00 /100 | NORMAL | CURRENT |

## Why this priority

- A HIGH fundamental early-warning rule is triggered.
- Financial inputs end 2025-03-31 and are 552 days old; refresh before drawing current credit conclusions.

Action: Review the risk drivers, current exposure and credit terms; increase monitoring frequency.

Signal confirmation: NOT CONFIRMED.

## Market observations

30-session return: 5.9%. 90-session return: 3.2%. NIFTY Pharma 90-session return: 6.6%. Relative performance: -3.5%.

Current 30-session drawdown: -0.4%. 90-session maximum drawdown: -14.5%. Daily 30-session volatility: 1.9%. Volatility ratio: 1.05x. Volume ratio: 0.92x.

Source: https://finance.yahoo.com/quote/MANKIND.NS/.
## Explainable alerts

- **[FINANCIAL/MEDIUM] DEBT_ACCELERATION**
  - What happened: Debt growth exceeds the threshold; observed 39.27777777777778, threshold 0.2.
  - Why it matters: Borrowing increased faster than the monitoring threshold.
  - Action: Check acquisition funding and debt drawdowns.
- **[FINANCIAL/MEDIUM] RECEIVABLES_DETERIORATION**
  - What happened: Receivables grew faster than revenue; observed 0.3088235294117647, threshold 0.17851959361393321.
  - Why it matters: Collections may be lagging reported sales growth.
  - Action: Check receivable ageing and customer payment behaviour.
- **[FINANCIAL/HIGH] RISK_MIGRATION**
  - What happened: Financial risk score increased materially year over year; observed 12, threshold 10.
  - Why it matters: More financial scoring thresholds were breached.
  - Action: Review the drivers of score migration and current credit terms.
