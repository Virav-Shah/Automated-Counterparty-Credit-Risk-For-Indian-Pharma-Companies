# Qualitative assessment policy

These criteria were defined before researching the companies. The authoritative editable rules and weights are in `config/monitoring.json`. Each factor uses 0–4 severity points. Regulatory weight is 30%; geographic, customer, business and litigation are 15% each; FX is 10%.

The six-factor qualitative index is `sum(factor score / 4 × factor weight)`, from 0–100. This index exists only when all six factors are assessed, sourced and fresh. It does not change the financial score. LOW is below 25, MODERATE is 25–<50, HIGH is 50–<75 and SEVERE is 75–100. A missing factor is not a zero. No completed qualitative rating is claimed for a partial assessment.

| Factor | 0 | 2 | 4 |
|---|---|---|---|
| Geographic concentration | Largest geography <25% revenue | 25–<50% | ≥50% |
| Customer concentration | Largest customer ≤10% revenue | >10–<20% | ≥20% |
| FX exposure | 10% FX-shock profit sensitivity <5% of positive PAT | 5–<15% | ≥15% |
| Business concentration | Largest disclosed business dimension <25% revenue | 25–<50% | ≥50% |
| Litigation | Litigation/tax contingent liabilities <5% of consolidated net worth | 5–<15% | ≥15% |

Regulatory scores: 0 requires a documented review finding no material unresolved issue; 1 requires minor observations and closure evidence; 2 is moderate unresolved observations; 3 is an official warning/significant action; 4 is a material import ban or manufacturing suspension. Search silence is insufficient evidence for 0.

A source’s actual disclosed scope governs an assessment. For geographic revenue, a named country/region is usable; 'international' aggregated across countries does not establish single-country concentration. Business segment concentration does not imply product or facility concentration. FX risk is not inferred from exports. Ordinary guarantees are excluded from litigation numerator.

## Evidence rows

`data/qualitative_risk.csv` has one company/factor row per assessment. Required columns:

- `company_id`, `factor`: stable financial-universe key and one of six configured factor names.
- `score`: blank for unassessed; integer 0–4 otherwise.
- `source`: primary-source URL to annual report, filing, regulator or investor material.
- `source_date`: ISO date for the underlying reporting period/publication, never the retrieval date in its place.
- `source_location`: page, note or section establishing the fact.
- `evidence`: concise factual paraphrase or numerical observation.
- `analyst_note`: interpretation linking evidence to the criteria, including the dimension used.
- `assessment_date`, `analyst`, `review_status`: date of interpretation, authorship and review workflow.

Only `ASSESSED` and `REVIEWED` rows with complete evidence fields can contribute. `UNASSESSED` rows reserve the analyst task and retain a primary-source research link where available. Newer evidence replaces the assessment for that company/factor; keep the source snapshots/research log for an audit trail. Never enter illustrative planner scores as facts.

Stale assessments remain visible but do not receive a current aggregate rating. The configured limit is 550 calendar days from source date. Score 4 for regulatory/litigation supports immediate review even if other factors are missing, when that source is fresh. Other score-4 concentration concerns support watchlist monitoring and remain clearly provisional until analyst review.

## Seed assessment status

The delivered CSV contains 120 factor slots and 46 evidence-backed draft assessments from annual reports and specific regulatory/company filings. Twenty-two are current and 24 are stale as of 2026-10-04. None has independent analyst review; no company has all six current factors. Four regulatory and two FX factors now have sourced draft assessments; remaining research, including litigation, remains incomplete. Initial retrieval failed for Aurobindo, Divi’s and Piramal; the research manifest records those failures. These gaps are explicit follow-up work in the dashboard, not low-risk conclusions.

PDF locations count pages from 1 in the PDF file, which can differ from printed page labels and two-page spreads. Amounts retain the source report’s units and must not be summed across issuers. Source dates identify the underlying fiscal period end; assessment dates identify the later interpretation.

## Evidence update — 2026-10-04

The supplied source directory is retained as `data/qualitative/user_source_directory.txt`. General IR portals, approximate publication dates and typical page ranges do not establish specific factor scores. Actual linked filings/sections were verified separately. The original narrative CSV is preserved, with 120 normalized narratives in `data/qualitative/user_narratives.csv`; these remain explicitly unverified context in analyst notes and do not override the scoring policy.

Seven factor records were updated: Sun/Glenmark/Jubilant/Lupin regulatory factors; Abbott/Ajanta FX factors; Lupin geography refreshed from FY25 to FY26. Regulatory scores describe dated disclosed events, not verified ongoing action status. The Sun shipment restriction supports a priority review; check latest remediation and site materiality before changing credit terms. An old warning letter does not prove it remains open.

FX screening scales reported 1% pre-tax sensitivity linearly to a 10% shock, summing adverse absolute currency impacts, then divides by positive same-scope PAT. Abbott: `(1.65 × 10) / 1552.02 = 1.06%`, score 0. Ajanta: `((10.86 + 0.29 + 0.57 + 0.89) × 10) / 1056.00 = 11.94%`, score 2. This disclosed approximation measures balance-sheet monetary sensitivity, not total operating FX exposure; it mixes pre-tax sensitivity and PAT deliberately under the screening definition.

Prior assessments are archived under `data/qualitative/archive/`; the full changes and references are in `data/qualitative/evidence_update_2026-10-04.json`. None of these research drafts claims independent analyst review. All six current factors are still required for an aggregate.
