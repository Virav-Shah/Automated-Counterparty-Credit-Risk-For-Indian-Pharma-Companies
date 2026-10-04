# Finance analyst report

`Indian_Pharma_Counterparty_Credit_Report.docx` is the editable, professional analyst report intended for a finance or credit-risk interview. The report covers the 20 studied companies, sector economics, four business-model peer groups, P&L/balance-sheet/cash-flow methods, internal credit-risk classification, credit reviews, counterparty assessment and a proposed limit-monitoring framework. Biocon and Laurus have detailed five-year case studies; the other 18 companies receive concise assessments.

`Indian_Pharma_Counterparty_Credit_Report.md` mirrors the report's text and tables for review in a text editor. The earlier working brief in `docs/PROJECT_REPORT_BRIEF.md` remains a research foundation, not the final report.

## Reproduce or revise

The report builder is `scripts/build_project_report.py`. It requires Python with `python-docx`, an optional artifact-generation dependency; normal project calculations need only the standard library.

```bash
python3 run.py --as-of 2026-10-04
python3 scripts/validate_report_results.py
python3 scripts/build_project_report.py
```

The builder reads `outputs/dashboard_data.json`, formats company tables and calculated ratios, and writes both report files. Analytical prose, source URLs and the review date are explicitly authored in the builder. When changing the data period, update those statements and reconcile all historical interpretations before publishing. Editing the DOCX directly is supported, but a subsequent builder run replaces both generated files; transfer lasting edits to the builder.

The revised report has explicit benchmark and validation sections. `result_validation.json` records 757 independent numerical comparisons (600 financial metrics, 80 score sums, 20 peer medians, 57 market endpoint comparisons); all pass against project inputs. The separate regression suite has 28 passing tests. These checks verify computation, not issuer-data accuracy or default prediction.

`external_benchmarks.json` preserves dated Biocon/Laurus FY25 disclosure values and Laurus's 1 July 2025 CARE rating. The external comparison identifies unresolved source differences, including Laurus OCF minus capex of -57 in disclosures versus +240 in the extract. Internal results remain provisional. Original financial inputs are preserved; no partial replacements or hybrid scores are made. The report also shows actual NIFTY Pharma relative returns from cached prices and acknowledges the adjusted-equity/price-index convention mismatch.

The delivered DOCX was rendered and every page visually checked. After content/layout changes, repeat a DOCX-to-PDF/page-image rendering check; changing text length can alter pagination and invalidate the reading guide. Rendering tools are development utilities and are not required to read the report.

## Evidence boundaries

Company monetary figures retain source units pending confirmation of currency, scale and statement scope. Ratings are internal historical screening categories. No qualitative score is used; dated regulatory evidence is narrative context and is not proof of current unresolved status. The report contains references to primary sector and regulatory sources. Approved limits and actual exposures are absent: the credit-limit section is a proposed workflow with a clearly hypothetical illustration.

Report files are stored separately from `outputs/` so regenerating the dashboard does not replace the report. Retained narrative research is documented in `data/README.md`.
