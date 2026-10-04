# Configuration

- `model.json`: financial universe/years, six category weights, scoring/rating bands and eight financial alert rules.
- `monitoring.json`: independent market weights/bands, history/freshness policy and fundamental/market confirmation thresholds. No qualitative weights or criteria remain.
- `peer_groups.csv`: user-defined business-model membership (8/6/3/3), marked `USER_DEFINED_BUSINESS_MODEL`; see `docs/PEER_GROUPS.md`.
- `tickers.csv`: one equity ticker per company and one benchmark; unique keys.
- `entity_events.csv`: effective dated transition, successor and primary source.

Run the full pipeline after edits. Bounds use the equality convention documented in methodology; market upper bounds use `<`, lower bounds use `>=`. Status vocabularies are module contracts. These are internal monitoring-policy assumptions, not calibrated probabilities.

Changes to scoring/monitoring policy require a version increment, preserved prior configuration and focused tests. Peer membership reflects operations; never derive it from market capitalization or the resulting risk score.
