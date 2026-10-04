# Artifact-generation scripts

`build_project_report.py` generates the Word and Markdown finance reports from the project's financial results and authored analysis. It uses `python-docx`; the main CRM pipeline remains dependency-free.

Run `python3 scripts/build_project_report.py` after generating `outputs/dashboard_data.json`. Paths resolve relative to the repository rather than the shell's working directory. The builder creates `reports/` if needed and overwrites only its two named report artifacts.

First run `python3 scripts/validate_report_results.py` to create the independent validation evidence consumed by the report builder. This standard-library checker recomputes six financial metrics for all 100 records, reconciles 80 complete scores, verifies 20 FY25 issuer-excluding leverage medians and checks company/index/relative returns for 19 complete market series from their exact cached endpoints. It does not call production scoring or market functions. Numeric mismatches fail the run; issuer-source accuracy and predictive validity remain separate questions.

Public helpers have docstrings describing heading, table, paragraph, company-summary and case-study generation. Tables use explicit widths, repeating header rows, visible borders and non-splitting rows. Financial ratios preserve unavailable values instead of rendering them as zero or infinity.

See `reports/README.md` for content revision, data reconciliation and visual verification requirements. Narrative prose must be reconsidered when changing the financial period; dynamic tables alone do not update the analyst's conclusions.
