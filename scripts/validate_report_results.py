"""Independently verify report figures without calling the scoring pipeline.

Recompute ratios from source CSV, peer medians from other-company records and
market-relative returns from cached price endpoints. This checks arithmetic and
consistency, not issuer source accuracy or predictive credit performance.
"""
import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    """Write an auditable validation summary; fail on any numerical mismatch."""
    payload = json.loads((ROOT / 'outputs/dashboard_data.json').read_text())
    source = {(r['company_id'], r['fiscal_year']): r for r in csv.DictReader((ROOT / 'pharma_financials_5yr.csv').open())}
    counts = defaultdict(int)

    def check(actual, expected, category):
        """Compare defined numbers with tolerance and preserve missing values."""
        valid = actual is None if expected is None else actual is not None and math.isclose(actual, expected, rel_tol=1e-10, abs_tol=1e-10)
        if not valid:
            raise AssertionError((category, actual, expected))
        counts[category] += 1

    for row in payload['rows']:
        s = source[row['company_id'], row['fiscal_year']]
        def value(key):
            return float(s[key])
        fcf = value('operating_cash_flow') - value('capex')
        expectations = {
            'debt_ebitda': value('total_debt') / value('ebitda'),
            'net_debt_ebitda': (value('total_debt') - value('cash')) / value('ebitda'),
            'interest_coverage': value('ebit') / value('interest_expense') if value('interest_expense') else None,
            'current_ratio': value('current_assets') / value('current_liabilities'),
            'free_cash_flow': fcf,
            'fcf_debt': fcf / value('total_debt') if value('total_debt') else None,
        }
        for k, expected in expectations.items():
            check(row[k], expected, 'financial_metric_checks')
        if row['financial_risk_score'] is not None:
            check(row['financial_risk_score'], sum(row[k] for k in ['leverage_points', 'servicing_points', 'cash_flow_points', 'liquidity_points', 'earnings_points', 'working_capital_points']), 'score_reconciliations')
    latest = [r for r in payload['rows'] if r['fiscal_year'] == 'FY25']
    for row in latest:
        other = [r['debt_ebitda'] for r in latest if r['company_id'] != row['company_id'] and r['peer_group'] == row['peer_group'] and r['debt_ebitda'] is not None]
        check(row['debt_ebitda_peer_median'], statistics.median(other), 'peer_median_checks')
    histories = defaultdict(list)
    for r in csv.DictReader((ROOT / 'data/market_data.csv').open()):
        if r['date'] <= payload['v2']['as_of']:
            histories[r['ticker']].append(r)
    index_ticker = next(r['ticker'] for r in csv.DictReader((ROOT / 'config/tickers.csv').open()) if r['instrument'] == 'BENCHMARK')
    index = {r['date']: float(r['adjusted_close']) for r in histories[index_ticker]}
    windows = []
    for row in payload['v2']['market']:
        if row['market_stress_score'] is None:
            continue
        all_days = sorted(histories[row['ticker']], key=lambda r: r['date'])
        days = []
        for i, r in enumerate(all_days):
            placeholder = i > 0 and r['date'] not in index and float(r['volume'] or -1) == 0 and float(r['adjusted_close']) == float(all_days[i-1]['adjusted_close'])
            if not placeholder:
                days.append(r)
        start, end = days[-91], days[-1]
        company_return = float(end['adjusted_close']) / float(start['adjusted_close']) - 1
        benchmark_return = index[end['date']] / index[start['date']] - 1
        for k, val in [('return_90', company_return), ('benchmark_return_90', benchmark_return), ('relative_return_90', company_return-benchmark_return)]:
            check(row[k], val, 'market_endpoint_checks')
        windows.append({'company_id': row['company_id'], 'start_date': start['date'], 'end_date': end['date'], 'return_90': company_return, 'benchmark_return_90': benchmark_return, 'relative_return_90': company_return-benchmark_return})
    report = {'as_of': payload['v2']['as_of'], 'status': 'PASS', 'counts': dict(counts), 'market_windows': windows, 'scope': 'Independent arithmetic verification against project inputs; issuer-data accuracy and default prediction are not certified.'}
    (ROOT / 'reports/result_validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report['counts']))


if __name__ == '__main__':
    main()
