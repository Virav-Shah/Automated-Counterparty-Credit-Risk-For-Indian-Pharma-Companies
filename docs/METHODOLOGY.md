# Monitoring methodology

## Primary financial score

The supplied notes specify four scoring categories and their weights. The other two categories use explicit proposed rules:

| Category | Maximum | Rule |
|---|---:|---|
| Leverage | 25 | Debt/EBITDA: <1 gives 0; 1–<2 gives 6; 2–<3 gives 12; 3–4 gives 20; >4 gives 25 |
| Debt servicing | 20 | EBIT/interest: <2 gives 20; 2–<3 gives 15; 3–<5 gives 8; 5–8 gives 3; >8 gives 0 |
| Cash flow | 20 | FCF/debt: <0% gives 20; 0–<5% gives 15; 5–<10% gives 10; 10–20% gives 5; >20% gives 0 |
| Liquidity | 15 | Current ratio: <0.8 gives 15; 0.8–<1 gives 12; 1–<1.2 gives 6; 1.2–1.5 gives 2; >1.5 gives 0 |
| Earnings resilience (proposed) | 10 | Revenue growth: <-10% gives 10; -10–<0% gives 7; 0–<5% gives 4; 5–<10% gives 2; ≥10% gives 0 |
| Working capital (proposed) | 10 | Maximum excess of receivables/inventory growth over revenue growth, floored at zero: 0 gives 0; >0–5pp gives 2; >5–10pp gives 5; >10–20pp gives 8; >20pp gives 10 |

Higher scores mean higher risk. Ratings: 0–14 VERY LOW, 15–29 LOW, 30–49 MODERATE, 50–69 HIGH, 70–100 CRITICAL. These are monitoring rules, not calibrated default probabilities.

FY21 lacks FY20 growth inputs. Its earnings and working-capital contributions, full score and rating are unavailable. Its observed four-component core score remains available out of 80 for five-year comparison. The dashboard never imputes absent growth components as zero. Full score migration starts with FY22 → FY23.

Zero debt: FCF/debt is unavailable and excluded from peer ratio benchmarks. Cash-flow points are 0 when FCF is nonnegative and 20 for a cash deficit. Zero interest: coverage is unavailable, excluded from benchmarks, and servicing points are 0. New debt from a zero base triggers a debt acceleration alert even though percentage growth is undefined. Negative net debt is preserved.

## Alert rules

1. Debt/EBITDA >3: HIGH.
2. Interest coverage <3: HIGH.
3. FCF/debt <10%: MEDIUM; negative FCF: HIGH.
4. Current ratio <1: HIGH.
5. Debt growth >20%, or new debt from zero: MEDIUM.
6. Revenue growth <0%: MEDIUM.
7. Receivables growth exceeds revenue growth: MEDIUM.
8. Full score increase ≥10 points (proposed migration threshold): HIGH.

Alert counts represent triggered rules, not company counts. Historical alerts include all five fiscal years. Latest portfolio outputs use FY25. Enhanced monitoring applies to HIGH/CRITICAL ratings or any HIGH alert; watchlist monitoring applies to MODERATE ratings or other alerts. Routine monitoring applies otherwise.

## Peer benchmarking

For each company/year, benchmarks use **other companies** in the same configured group and year. Missing ratios are excluded. Output includes valid peer counts, median and risk-oriented percentile for leverage, net leverage, coverage, liquidity, FCF/debt and financial score.

For higher-is-worse metrics, percentile is `(number of peers below + 0.5 × ties) / valid peers × 100`. Lower-is-worse metrics invert that result. Thus higher percentile always means higher relative risk. A lone company has unavailable peer metrics. Each of the two three-company groups supplies only two other-company comparators per issuer; results require individual judgment.


## Independent market stress

Let P be chronological adjusted prices after removing documented holiday placeholders. A 30-session return is `P[-1]/P[-31] - 1`; a 90-session return is `P[-1]/P[-91] - 1`. Relative performance is company return minus the NIFTY Pharma return using exactly the same two dates. Missing index endpoints are not substituted. Equity adjusted closes include dividends/splits; the price index is not total return, so this is a disclosed benchmark mismatch.

Current 30-session drawdown is `P[-1]/max(P[-30:]) - 1`. Maximum 90-session drawdown is the lowest running price/preceding peak −1 across the last 90 observations; recovered prices can have zero current drawdown and a large historical maximum loss.

Daily simple returns are `P[t]/P[t-1] - 1`. Volatility uses sample standard deviation of the latest 30 daily returns. The baseline uses the 120 preceding **nonoverlapping** returns. Ratio = recent volatility/baseline; a zero baseline is undefined. Annualized volatility = daily volatility × sqrt(252). Volume ratio = latest split-adjusted volume / mean of preceding 30 sessions. Any missing volume or zero baseline prevents a complete component.

| Component | Bands and points | Maximum |
|---|---|---:|
| Relative 90-session return | <−20%:35; −20–<−10%:25; −10–<−5%:10; ≥−5%:0 | 35 |
| Current 30-session drawdown | <−25%:30; −25–<−15%:20; −15–<−8%:10; ≥−8%:0 | 30 |
| Volatility ratio | <1.5:0; 1.5–<2:5; 2–<3:12; ≥3:20 | 20 |
| Volume ratio | <1.5:0; 1.5–<2:5; 2–<3:10; ≥3:15 | 15 |

The score is the sum of **market components only**, when all components exist, history has at least 151 observations and latest data is at most 7 calendar days old. Status: <25 NORMAL; 25–<50 WATCH; 50–<75 ELEVATED; ≥75 SEVERE. Thresholds are proposed monitoring policy. Stale/missing/incomplete histories have no current aggregate score.

## Priority matrix

The final priority is the highest applicable rule; reasons are cumulative, not a numeric mixture.

| Trigger | Priority floor |
|---|---|
| Critical financial rating | CREDIT REVIEW |
| High financial rating or any HIGH financial alert | ENHANCED MONITORING |
| Moderate financial rating or other financial alert | WATCH |
| Current ELEVATED/SEVERE market stress alone | ENHANCED MONITORING |
| Current WATCH market stress | WATCH |
| Fresh HIGH/CRITICAL financial rating plus current ELEVATED/SEVERE market | CREDIT REVIEW |
| Confirmed deterioration (below) | ENHANCED MONITORING; CREDIT REVIEW if financial HIGH/CRITICAL |
| Missing or stale financial/market data | WATCH |
| Effective sourced entity amalgamation | CREDIT REVIEW |
| Fresh complete layers, no triggers | NORMAL |

Stale financial ratings/alerts remain historical concerns and may still set a review floor, but are not current market corroboration. Market-led escalation explicitly leaves the financial rating intact.

## Confirmation and dates

Fundamental deterioration means at least one year-over-year event: debt/EBITDA rises ≥0.5x; FCF/debt falls ≥5pp; interest coverage falls ≥20%; financial score rises ≥10. Confirmation additionally requires current ELEVATED/SEVERE market stress, relative 90-session return <−10pp, financial age ≤540 days and financial-period/market-date gap ≤180 days. These gates avoid calling an old financial period and a much later price signal jointly confirmed.

