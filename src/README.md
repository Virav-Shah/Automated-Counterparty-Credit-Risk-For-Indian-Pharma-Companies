# Source code

The project uses Python’s standard library. All public calculation functions have docstrings.

| Module | Responsibility |
|---|---|
| `crm.py` | Financial validation, ratios/growth, six-component score, migration, eight alert rules, other-company peers and reports |
| `01_*.py` through `07_*.py` | Financial stage wrappers, including earlier prerequisites |
| `download_market.py` | Network-only public chart fetching, adjusted prices, split-adjusted volume, raw cache and provenance |
| `market.py` | Cached-price validation, trading-window indicators, independent market stress and explanatory alerts |
| `watchlist.py` | Financial/market priority, date-aligned confirmation and effective entity transitions |
| `pipeline_v2.py` | Validate/compose financial and market records; publish watchlist, alerts, JSON, HTML and reports |
| `dashboard.html` | Historical financial UI and base browser helpers |
| `dashboard_v2.js` | Current financial/market watchlist, drilldown, filters, export and view switching |

`run.py` is the supported root CLI. The downloader is also available as `python3 -m src.download_market`. `pipeline_v2.run` requires a complete financial output folder first. It reads full-precision JSON, not rounded exported ratios. Priority never changes the financial score.

The former qualitative scoring module has been removed. Report research is outside runtime imports and outputs. Adding a narrative score or priority dependence would conflict with current project scope.

The HTML placeholders are `__CRM_DATA__` and `__V2_SCRIPT__`. Generated snapshots work offline. Edit source templates, regenerate, then test; generated HTML edits are overwritten. All displayed source text is escaped and links are restricted to HTTP(S).
