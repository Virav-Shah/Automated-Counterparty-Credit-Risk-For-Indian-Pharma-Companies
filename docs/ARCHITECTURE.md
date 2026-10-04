# Architecture

```text
Financial CSV + financial rules + business-model peers
  → validation → ratios/growth → financial score → trends/alerts/peers → reports/JSON
Market CSV + ticker mapping + monitoring rules
  → validation → adjusted-price indicators → independent market stress/alerts
Financial records + market signals + dated entity events
  → monitoring priorities and explanations → watchlist/reports/dashboard
```

The financial engine owns the primary internal credit-risk score. The market engine supplies independent monitoring signals. Watchlist rules combine observations into a review priority without blending scores. Qualitative evidence is retained separately as project-report research and is not read by the pipeline.

Only the downloader accesses the network. The normal workflow is offline and deterministic from cached inputs/configs. Missing values are CSV blanks, JSON null and report N/A. Full-precision financial JSON feeds monitoring; rounded exports do not.

V1 and V2 prepare outputs separately in temporary directories, then copy individual files. Publication is not an atomic transaction across the whole folder; simultaneous writers are unsupported. A V2 failure after V1 success can leave a financial-only dashboard and older monitoring CSVs. Check both manifests and rerun successfully. Retired qualitative output files are removed after a successful V2 publication.

Extending the financial universe requires consistent company/year coverage, peer assignments and one-to-one ticker mapping. Entity changes require explicit sources and dates. Tests cover missing values, boundaries, freshness and peer membership. Browser code renders generated data rather than duplicating financial formulas.
