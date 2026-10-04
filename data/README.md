# Data and research provenance

`pharma_financials_5yr.csv` is an unchanged copy of the user’s original root CSV, with 20 companies over FY21–FY25. Currency, scale and standalone/consolidated scope were not supplied. `market_data.csv` stores real adjusted prices and volume; `market/raw/` and its download manifest preserve responses, metadata and hashes.

## Qualitative research — report use only

The application does not read or score this material:

- Original root `pharma_qualitative_data.csv`: user narratives for all 20 companies and six categories; unchanged.
- `qualitative/user_narratives.csv`: the 120 narratives normalized by company/factor, explicitly unverified.
- `qualitative/report_evidence.csv`: score-free source observations, dates, locations and analyst notes. Historical scoring language in notes is a retired draft interpretation, not an active rating.
- `qualitative/research_sources.json` and `research_manifest.json`: initial annual-report sources, extraction outcomes and hashes.
- `qualitative/user_source_directory.txt`: supplied repository/IR directory; typical publication dates and page ranges are not company evidence.
- `qualitative/evidence_update_2026-10-04.json`: historical record of source-based research updates.
- `qualitative/archive/`: retired scored inputs, earlier inputs and former assessment policy retained for provenance. No archived scores influence the application.

Use primary reports/filings to verify report statements. Source dates identify underlying reporting periods or publication dates, not retrieval dates. Qualitative data may be stale or incomplete; no independent analyst review is claimed. Keep narrative context separate from the financial score and verify later remediation before describing a regulatory matter as current.

See [data dictionary](../docs/DATA_DICTIONARY.md) for financial/market schemas and [report brief](../docs/PROJECT_REPORT_BRIEF.md) for the planned narrative treatment.
