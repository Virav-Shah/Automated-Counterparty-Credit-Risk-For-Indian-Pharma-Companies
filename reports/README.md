# Finance analyst report

`Indian_Pharma_Counterparty_Credit_Report.docx` is the original 11-page report, revised to retain its title, cover treatment, reading guide, section flow, typography, page setup and navy table styling. Its detailed company analysis is now limited to Cipla. It retains the Indian pharma sector context, four operating-model peer groups, financial-statement analysis method, internal score framework, Cipla's five-year simulated case, peer benchmarks, downside stress tests, an audited FY25–FY26 retrospective challenge, counterparty review and credit-limit monitoring.

The report is authored by Virav Shah for a finance or credit-risk interview. All project financial and qualitative CSV data are simulated; official Cipla figures are identified separately. The audited FY26 comparison is an ex-post challenge to the model's assumptions, not validation of the simulated data or a claim of predictive accuracy.

`Indian_Pharma_Counterparty_Credit_Report.md` is a text-and-table companion for review in an editor. The original supplied Word document remains unchanged. The earlier working brief in `docs/PROJECT_REPORT_BRIEF.md` is a research foundation, not the current report scope.

## Reproduce

Regenerate the scenario calculations and then rebuild the report:

```bash
python3 scripts/cipla_stress_test.py
python3 scripts/build_cipla_report.py
```

The calculation outputs are `cipla_stress_results.json` and `cipla_stress_scenarios.csv`. The document builder starts from the original reference file and transplants only the authored main-document body, preserving the reference package's styles, page setup, page-number footer, relationships and remaining components. The generated project copy uses the original report filename shown above.

The report is 11 pages, including an index. Rerender and inspect all pages after changing report content because pagination can shift the index. Source-unit, scope, model calibration and counterparty-exposure limitations are stated in the report.
