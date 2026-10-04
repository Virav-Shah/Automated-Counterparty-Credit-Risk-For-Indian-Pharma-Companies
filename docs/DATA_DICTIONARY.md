# Data dictionary

## Financial input

Exact columns: `company_id`, `fiscal_year`, `revenue`, `ebitda`, `ebit`, `interest_expense`, `cash`, `total_debt`, `current_assets`, `current_liabilities`, `receivables`, `inventory`, `operating_cash_flow`, `capex`.

One unique company/year row; years use `FY21` … `FY25`. Monetary values retain the same user-supplied source units; ratios/growth assume consistent units within each issuer. Revenue, EBITDA, EBIT and current assets/liabilities must be positive. Debt/cash/interest/capex/receivables/inventory must be nonnegative; OCF can be negative. Required universe/year coverage is in `model.json`. Loss-making companies are outside the current positive-earnings validation policy.

## Market input

| Field | Meaning |
|---|---|
| `date` | ISO exchange-local observation date |
| `company_id`, `ticker` | Stable company identifier and provider ticker; benchmark has its own mapping row |
| `adjusted_close` | Positive finite adjusted daily price; not raw-close fallback |
| `volume` | Raw reported daily traded shares; can be blank |
| `adjusted_volume` | Volume multiplied by future split ratios in the fetched window; blank remains missing |
| `source` | Provider history URL |

Validation rejects unknown ticker/company mapping, duplicate observations and invalid numeric values. Rows after `--as-of` are excluded. Raw columns are retained as supplied; exclusions used by market windows are reported separately.



## Derived financial fields

| Fields | Units / meaning |
|---|---|
| `free_cash_flow`, `net_debt` | OCF − capex; total debt − cash, in source units |
| `debt_ebitda`, `net_debt_ebitda`, `interest_coverage`, `current_ratio`, `fcf_debt` | Ratios; zero-debt FCF ratio and zero-interest coverage are unavailable |
| `*_growth`, `*_growth_gap` | Annual fractional change / growth excess; 0.05 means 5% or 5 percentage points |
| `*_points` | Six financial category contributions |
| `financial_risk_score`, `risk_rating` | Complete 0–100 primary financial score and rating; FY21 full score unavailable |
| `core_risk_score`, `score_available_points` | Observed four-category score /80 for first year; available-point count |
| `score_change` | Change in complete score from preceding available fiscal year |
| `peer_*` | Other-company group/year benchmark statistics; valid-peer count and risk-oriented percentile |

## Derived V2 fields

| Fields | Units / meaning |
|---|---|
| `return_30`, `return_90`, `benchmark_return_90`, `relative_return_90` | Fractional trading-session returns; relative return is difference, not ratio |
| `drawdown_30`, `maximum_drawdown_90` | Negative fractional current drawdown / historical worst drawdown |
| `volatility_30_daily`, `volatility_baseline_daily` | Sample standard deviation of daily simple fractional returns |
| `volatility_30_annualized` | Daily volatility × sqrt(252) |
| `volatility_ratio`, `volume_ratio` | Multiples of independent prior baseline / prior 30-session mean |
| `relative_points`, `drawdown_points`, `volatility_points`, `volume_points` | Independent market contribution points, maxima 35/30/20/15 |
| `market_stress_score`, `market_status` | Complete fresh market score /100 and NORMAL/WATCH/ELEVATED/SEVERE; missing/stale = unavailable |
| `market_data_status`, `missing_reason` | CURRENT/INCOMPLETE/STALE/MISSING and unresolved components |
| `observations`, `excluded_nontrading_placeholders` | Usable session count and strict holiday-placeholder exclusions |
| `financial_data_status`, `financial_age_days` | CURRENT/STALE relative to configured assumed fiscal period end |
| `monitoring_priority`, `priority_rank` | NORMAL=0, WATCH=1, ENHANCED MONITORING=2, CREDIT REVIEW=3 |
| `confirmed_deterioration`, `confirmation_status` | Fundamental deterioration and sector-relative stress jointly meet freshness/alignment rules |
| `financial_market_gap_days` | Absolute calendar-day gap between financial period end and market observation |
| `reasons`, `recommended_action` | All triggered explanations joined with ` | `; next monitoring action |
| `entity_event`, `entity_event_source` | Effective documented transition and primary-source URL |

`monitoring_alerts.csv` contains one rule alert per company/date/layer: `code`, `severity`, `metric`, `value`, optional `threshold`, `what_happened`, `why_it_matters`, `recommended_action`, optional evidence source/location/review status. Counts are rule counts, not company counts. Financial alerts retain historical financial-period dates; they are not presented as newly reported October events.
