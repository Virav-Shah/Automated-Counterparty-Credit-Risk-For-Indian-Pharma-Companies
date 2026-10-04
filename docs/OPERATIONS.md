# Operations

Run the full workflow using `python3 run.py --as-of YYYY-MM-DD`. Read both `RUN_STATUS.json` and `V2_RUN_STATUS.json` before using outputs. A failed/partial run may leave older files; rerun successfully and refresh the dashboard.

Refresh prices with `python3 run.py --refresh-market`. Requests may be rate-limited; a failed refresh preserves the previous CSV. Inspect `data/market/download_manifest.json`. Missing/stale histories never receive a normal score by default. JB’s entity transition requires identity/exposure review rather than substitution of Torrent’s prices.

Update financial CSV/year configuration consistently. Obtain currency, scale, reporting scope and statement provenance. FY25 inputs are stale at the delivered October 2026 date; date alignment prevents them from confirming current market deterioration. Run `python3 -m unittest discover -s tests -v` after model changes.

Edit `config/peer_groups.csv` only when the analytical business-model rationale changes. Current assignments were supplied by the user and have 8/6/3/3 companies. Do not regroup companies to improve a score comparison.

Qualitative research is retained only for the report. Update `data/qualitative/report_evidence.csv` and preserve supporting sources; it is not an input to `run.py`. The application has no qualitative score, qualitative alerts or qualitative-based escalation. Distinguish dated observations from claims about unresolved current issues.

Actual credit-limit monitoring needs exposure/approved-limit data and a defined policy. No exposure or limit has been invented. See the report brief for required fields and a proposed finance workflow.

No scheduled jobs or simultaneous writers are supported. Archive inputs, configurations, raw price responses and outputs when retaining a monitoring history. Historical adjusted prices can be revised by the provider.
