"""Deterministic seven-stage financial monitoring engine; Python standard library only."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import re
import shutil
import statistics
import tempfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLUMNS = ['company_id', 'fiscal_year', 'revenue', 'ebitda', 'ebit', 'interest_expense', 'cash', 'total_debt', 'current_assets', 'current_liabilities', 'receivables', 'inventory', 'operating_cash_flow', 'capex']
COMPONENTS = ['leverage_points', 'servicing_points', 'cash_flow_points', 'liquidity_points', 'earnings_points', 'working_capital_points']
PEER_METRICS = {'debt_ebitda': True, 'net_debt_ebitda': True, 'interest_coverage': False, 'current_ratio': False, 'fcf_debt': False, 'financial_risk_score': True}


def write_csv(path, rows, fields=None):
    """Write numeric records with explicit columns; represent unavailable values as blanks."""
    fields = fields or (list(rows[0]) if rows else [])
    with Path(path).open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: ('' if row.get(k) is None else row.get(k)) for k in fields})


def validate(path, config):
    """Return normalized source rows and auditable checks; invalid input yields no usable rows."""
    checks = []
    def check(name, ok, detail):
        """Append a named validation check and its human-readable supporting detail."""
        checks.append({'check': name, 'result': 'PASS' if ok else 'FAIL', 'detail': detail})
    with Path(path).open(newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        raw = list(reader)
    check('Required columns exactly once', len(headers) == len(COLUMNS) and set(headers) == set(COLUMNS), ', '.join(headers))
    if checks[-1]['result'] == 'FAIL':
        return [], checks
    rows, issues = [], []
    for index, raw_row in enumerate(raw, 2):
        row = {}
        if None in raw_row:
            issues.append(f'row {index}: unexpected extra fields')
        for field in COLUMNS:
            value = raw_row.get(field)
            if value is None or not value.strip():
                issues.append(f'row {index}: missing {field}')
                continue
            if field in COLUMNS[:2]:
                row[field] = value.strip()
            else:
                try:
                    row[field] = float(value)
                    if not math.isfinite(row[field]):
                        issues.append(f'row {index}: non-finite {field}')
                except ValueError:
                    issues.append(f'row {index}: nonnumeric {field}')
        rows.append(row)
    check('No missing, nonnumeric or non-finite values', not issues, '; '.join(issues) or 'All inputs populated and finite')
    if issues:
        return [], checks
    keys = [(r['company_id'], r['fiscal_year']) for r in rows]
    check('Unique company/year keys', len(keys) == len(set(keys)), f'{len(keys)} rows / {len(set(keys))} unique keys')
    companies = {r['company_id'] for r in rows}
    years = config['expected_years']
    check('Expected company count', len(companies) == config['expected_companies'], f'{len(companies)} observed; {config["expected_companies"]} expected')
    check('Expected row count', len(rows) == config['expected_companies'] * len(years), f'{len(rows)} observations')
    invalid = [r['fiscal_year'] for r in rows if not re.fullmatch(r'FY\d{2}', r['fiscal_year']) or r['fiscal_year'] not in years]
    check('Valid fiscal years', not invalid, ', '.join(invalid) or ', '.join(years))
    complete = all(sorted(r['fiscal_year'] for r in rows if r['company_id'] == c) == sorted(years) for c in companies)
    check('Complete year coverage per company', complete, f'Each company must have {len(years)} distinct configured years')
    for field in ['revenue', 'ebitda', 'ebit', 'current_assets', 'current_liabilities']:
        bad = [f'{r["company_id"]} {r["fiscal_year"]}' for r in rows if r[field] <= 0]
        check(f'{field} > 0', not bad, ', '.join(bad) or 'All positive')
    for field in ['total_debt', 'cash', 'interest_expense', 'capex', 'receivables', 'inventory']:
        bad = [f'{r["company_id"]} {r["fiscal_year"]}' for r in rows if r[field] < 0]
        check(f'{field} >= 0', not bad, ', '.join(bad) or 'All nonnegative')
    bad = [f'{r["company_id"]} {r["fiscal_year"]}' for r in rows if r['ebitda'] < r['ebit']]
    check('EBITDA >= EBIT', not bad, ', '.join(bad) or 'All consistent')
    return sorted(rows, key=lambda r: (r['company_id'], r['fiscal_year'])), checks


def metrics(rows):
    """Sort each company chronologically and derive full-precision ratios and annual growth."""
    result, previous = [], {}
    for source in sorted(rows, key=lambda r: (r['company_id'], r['fiscal_year'])):
        r = dict(source)
        debt, interest = r['total_debt'], r['interest_expense']
        r.update(debt_ebitda=debt/r['ebitda'], net_debt_ebitda=(debt-r['cash'])/r['ebitda'],
                 interest_coverage=r['ebit']/interest if interest else None,
                 current_ratio=r['current_assets']/r['current_liabilities'],
                 free_cash_flow=r['operating_cash_flow']-r['capex'])
        r['fcf_debt'] = r['free_cash_flow']/debt if debt else None
        r['fcf_debt_status'] = 'DEFINED' if debt else 'NO DEBT'
        r['coverage_status'] = 'DEFINED' if interest else 'NO INTEREST'
        p = previous.get(r['company_id'])
        for field, label in [('revenue','revenue_growth'), ('total_debt','debt_growth'), ('receivables','receivables_growth'), ('inventory','inventory_growth')]:
            r[label] = r[field]/p[field]-1 if p and p[field] else None
        r['debt_from_zero'] = bool(p and p['total_debt'] == 0 and debt > 0)
        previous[r['company_id']] = source
        result.append(r)
    return result


def band(value, spec, inclusive=False):
    """Apply configured ordered scoring bounds with the specified equality convention."""
    for i, (bound, points) in enumerate(zip(spec['upper_bounds'], spec['points'])):
        include = spec.get('upper_inclusive', [inclusive]*len(spec['upper_bounds']))[i]
        if value < bound or (include and value == bound):
            return points
    return spec['points'][-1]


def rate(score, config):
    """Map a complete financial score to its configured primary credit-risk band."""
    if score is None:
        return 'NOT SCORED'
    for bound, label in zip(config['rating_upper_bounds'], config['rating_labels']):
        if score < bound:
            return label
    return config['rating_labels'][-1]


def scores(rows, config):
    """Compute six contributions; retain an 80-point core when growth is unavailable."""
    result = []
    for source in rows:
        r = dict(source)
        r['leverage_points'] = band(r['debt_ebitda'], config['leverage'], inclusive=True)
        r['servicing_points'] = band(r['interest_coverage'], config['coverage']) if r['interest_coverage'] is not None else 0
        # No debt: ratio is N/A; cash deficit still merits the maximum cash-flow penalty.
        r['cash_flow_points'] = band(r['fcf_debt'], config['cash_flow']) if r['total_debt'] else (20 if r['free_cash_flow'] < 0 else 0)
        r['liquidity_points'] = band(r['current_ratio'], config['liquidity'])
        growth = r['revenue_growth']
        r['earnings_points'] = band(growth, config['earnings']) if growth is not None else None
        gap = max(0, r['receivables_growth']-growth, r['inventory_growth']-growth) if all(r[k] is not None for k in ['revenue_growth','receivables_growth','inventory_growth']) else None
        r['working_capital_gap'] = gap
        r['working_capital_points'] = band(gap, config['working_capital'], inclusive=True) if gap is not None else None
        r['core_risk_score'] = sum(r[k] for k in COMPONENTS[:4])
        r['score_available_points'] = 80 if r['earnings_points'] is None or r['working_capital_points'] is None else 100
        r['financial_risk_score'] = sum(r[k] for k in COMPONENTS) if r['score_available_points'] == 100 else None
        r['risk_rating'] = rate(r['financial_risk_score'], config)
        result.append(r)
    return result


def trends(rows):
    """Add period-to-period score changes and financial trend labels without imputing baselines."""
    result, previous = [], {}
    for r in rows:
        p = previous.get(r['company_id'])
        change = r['financial_risk_score']-p['financial_risk_score'] if p and r['financial_risk_score'] is not None and p['financial_risk_score'] is not None else None
        result.append({**r, 'previous_rating': p['risk_rating'] if p else None, 'score_change': change,
                       'core_score_change': r['core_risk_score']-p['core_risk_score'] if p else None,
                       'score_direction': 'UNAVAILABLE' if change is None else 'DETERIORATING' if change > 0 else 'IMPROVING' if change < 0 else 'STABLE'})
        previous[r['company_id']] = r
    return result


def alerts(rows, config):
    """Emit one record per triggered financial rule, preserving metric, value and threshold."""
    result, a = [], config['alerts']
    for r in rows:
        def add(code, severity, metric, threshold, explanation):
            """Append one triggered early-warning rule with its observed value and explanation."""
            result.append({'company_id':r['company_id'], 'fiscal_year':r['fiscal_year'], 'code':code, 'severity':severity,
                           'metric':metric, 'value':r.get(metric), 'threshold':threshold, 'explanation':explanation})
        if r['debt_ebitda'] > a['leverage']:
            add('HIGH_LEVERAGE', 'HIGH', 'debt_ebitda', a['leverage'], 'Debt / EBITDA exceeds the leverage threshold')
        if r['interest_coverage'] is not None and r['interest_coverage'] < a['coverage']:
            add('WEAK_COVERAGE', 'HIGH', 'interest_coverage', a['coverage'], 'EBIT interest coverage is weak')
        if (r['fcf_debt'] is not None and r['fcf_debt'] < a['fcf_debt']) or (r['total_debt'] == 0 and r['free_cash_flow'] < 0):
            add('WEAK_CASH_GENERATION', 'HIGH' if r['free_cash_flow'] < 0 else 'MEDIUM', 'fcf_debt', a['fcf_debt'], 'Negative free cash flow' if r['free_cash_flow'] < 0 else 'Free cash flow supports less than the threshold share of debt')
        if r['current_ratio'] < a['current_ratio']:
            add('LIQUIDITY_PRESSURE', 'HIGH', 'current_ratio', a['current_ratio'], 'Current assets are below current liabilities')
        if r['debt_from_zero'] or (r['debt_growth'] is not None and r['debt_growth'] > a['debt_growth']):
            add('DEBT_ACCELERATION', 'MEDIUM', 'debt_growth', a['debt_growth'], 'New debt from a zero-debt base' if r['debt_from_zero'] else 'Debt growth exceeds the threshold')
        if r['revenue_growth'] is not None and r['revenue_growth'] < a['revenue_growth']:
            add('REVENUE_DETERIORATION', 'MEDIUM', 'revenue_growth', a['revenue_growth'], 'Revenue declined year over year')
        if r['receivables_growth'] is not None and r['revenue_growth'] is not None and r['receivables_growth']-r['revenue_growth'] > a['receivables_gap']:
            add('RECEIVABLES_DETERIORATION', 'MEDIUM', 'receivables_growth', r['revenue_growth']+a['receivables_gap'], 'Receivables grew faster than revenue')
        if r['score_change'] is not None and r['score_change'] >= a['score_increase']:
            add('RISK_MIGRATION', 'HIGH', 'score_change', a['score_increase'], 'Financial risk score increased materially year over year')
    return result


def peers(rows, mapping):
    """Benchmark against other companies in the same group/year with risk-oriented percentiles."""
    groups = defaultdict(list)
    for r in rows:
        groups[(mapping[r['company_id']]['peer_group'],r['fiscal_year'])].append(r)
    result = []
    for r in rows:
        m = mapping[r['company_id']]
        group = groups[(m['peer_group'],r['fiscal_year'])]
        others = [p for p in group if p['company_id'] != r['company_id']]
        p = {**r, **{k:v for k,v in m.items() if k != 'company_id'}, 'peer_count':len(others)}
        for metric, higher_bad in PEER_METRICS.items():
            values = [o[metric] for o in others if o[metric] is not None]
            value = r[metric]
            median = statistics.median(values) if values else None
            percentile = (sum(v < value for v in values) + 0.5*sum(v == value for v in values))/len(values)*100 if values and value is not None else None
            p[metric+'_peer_median'] = median
            p[metric+'_peer_valid_count'] = len(values)
            p[metric+'_risk_percentile'] = percentile if higher_bad or percentile is None else 100-percentile
        med = p['financial_risk_score_peer_median']
        p['peer_risk_position'] = 'UNAVAILABLE' if med is None or r['financial_risk_score'] is None else 'ABOVE PEER MEDIAN' if r['financial_risk_score'] > med else 'BELOW PEER MEDIAN' if r['financial_risk_score'] < med else 'AT PEER MEDIAN'
        result.append(p)
    return result


def monitoring(r, company_alerts):
    """Return the original financial-only monitoring recommendation for historical reports."""
    if r['risk_rating'] in ['HIGH', 'CRITICAL'] or any(a['severity']=='HIGH' for a in company_alerts):
        return 'Enhanced credit monitoring: review leverage, liquidity and cash generation before the next review.'
    if r['risk_rating'] == 'MODERATE' or company_alerts:
        return 'Watchlist monitoring: investigate alerts and reassess when the next financial results arrive.'
    return 'Routine monitoring: refresh at the next financial reporting cycle.'


def display(value, percent=False):
    """Format report values and decimal fractions; render unavailable values as N/A."""
    return 'N/A' if value is None else f'{value*100:.1f}%' if percent else f'{value:,.2f}'


def report(rows, warning_rows, checks, config, out, source):
    """Build financial company reports, portfolio summary and a self-contained HTML snapshot."""
    groups = defaultdict(list)
    for r in rows:
        groups[r['company_id']].append(r)
    latest_year = max(r['fiscal_year'] for r in rows)
    portfolio = []
    reports = out/'reports'
    reports.mkdir(exist_ok=True)
    for company, history in groups.items():
        r = history[-1]
        warnings = [a for a in warning_rows if a['company_id']==company and a['fiscal_year']==r['fiscal_year']]
        action = monitoring(r, warnings)
        portfolio.append({**r,'alert_count':len(warnings),'high_alert_count':sum(a['severity']=='HIGH' for a in warnings),'monitoring':action})
        drivers = sorted([(k,r[k]) for k in COMPONENTS if r[k]], key=lambda x:x[1], reverse=True)
        text = f'# Counterparty Credit Monitoring Report\n\nCompany: {company}\n\nPeriod: {r["fiscal_year"]}\n\nFinancial risk score: {r["financial_risk_score"]}/100 ({r["risk_rating"]})\n\nHigher scores indicate higher risk.\n\n## Key risk drivers\n\n'
        text += '\n'.join(f'- {k.replace("_points", "").replace("_", " ").title()}: {v} risk points' for k,v in drivers) or 'No scored risk drivers.'
        text += '\n\n## Five-year monitoring\n\n| Period | Core score /80 | Total score /100 | Rating | Debt/EBITDA | Coverage | FCF/Debt |\n|---|---:|---:|---|---:|---:|---:|\n'
        text += '\n'.join(f'| {h["fiscal_year"]} | {h["core_risk_score"]} | {h["financial_risk_score"] if h["financial_risk_score"] is not None else "N/A"} | {h["risk_rating"]} | {display(h["debt_ebitda"])} | {display(h["interest_coverage"])} | {display(h["fcf_debt"], True)} |' for h in history)
        text += '\n\nFY21 total score is unavailable because FY20 growth inputs were not supplied. The core score uses four financial components consistently across five years.\n'
        text += f'\n## Peer position\n\n{r["peer_group"]} ({r["assignment_status"]} assignment). {r["peer_count"]} other companies.\n\n{r["peer_risk_position"]}. Peer median score: {display(r["financial_risk_score_peer_median"])}.\n\n'
        text += 'Peers exclude the company itself. A small peer group limits comparison strength.\n\n## Early warnings\n\n'
        text += '\n'.join(f'- [{a["severity"]}] {a["explanation"]}. Observed {display(a["value"], a["metric"] in ['debt_growth','revenue_growth','receivables_growth','fcf_debt'])}; threshold {display(a["threshold"], a["metric"] in ['debt_growth','revenue_growth','receivables_growth','fcf_debt'])}.' for a in warnings) or 'No triggered warnings in this period.'
        text += f'\n\n## Recommended monitoring\n\n{action}\n\n## Data and methodology\n\nSource: {source.name}. Amounts: {config["units"]}. Model version: {config["version"]}.\n\n' + '\n\n'.join(config['assumptions']) + '\n'
        name = re.sub(r'[^a-z0-9]+','_',company.lower()).strip('_')
        (reports/f'{name}.md').write_text(text, encoding='utf-8')
    write_csv(out/'portfolio_summary.csv', sorted(portfolio,key=lambda r: r['financial_risk_score'] or 0,reverse=True))
    payload = {'rows':rows,'alerts':warning_rows,'checks':checks,'config':config,'source':source.name,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'latest_year':latest_year}
    data = json.dumps(payload,allow_nan=False)
    (out/'dashboard_data.json').write_text(data,encoding='utf-8')
    template = (ROOT/'src'/'dashboard.html').read_text(encoding='utf-8')
    (out/'dashboard.html').write_text(template.replace('__CRM_DATA__',data.replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')).replace('__V2_SCRIPT__',''),encoding='utf-8')
    return portfolio


def validate_model(config):
    """Reject incompatible financial weights, component bounds and universe declarations."""
    maxima = {'leverage':25, 'coverage':20, 'cash_flow':20, 'liquidity':15, 'earnings':10, 'working_capital':10}
    for key, maximum in maxima.items():
        spec = config[key]
        bounds, points = spec['upper_bounds'], spec['points']
        if len(points) != len(bounds)+1 or any(not math.isfinite(v) for v in bounds) or sorted(set(bounds)) != bounds:
            raise ValueError(f'Invalid model bands: {key}')
        if any(not isinstance(p, int) or p < 0 or p > maximum for p in points):
            raise ValueError(f'Invalid points for {key} (maximum {maximum})')
        if 'upper_inclusive' in spec and (len(spec['upper_inclusive']) != len(bounds) or any(type(v) is not bool for v in spec['upper_inclusive'])):
            raise ValueError(f'Invalid inclusivity flags: {key}')
    if config['rating_upper_bounds'] != [15,30,50,70] or len(config['rating_labels']) != 5:
        raise ValueError('Rating bounds must match the V1 100-point framework')
    years = config['expected_years']
    if not years or any(not re.fullmatch(r'FY\d{2}', y) for y in years) or len(set(years)) != len(years):
        raise ValueError('Expected fiscal years must be unique FYnn labels')
    if sorted(int(y[2:]) for y in years) != list(range(min(int(y[2:]) for y in years),max(int(y[2:]) for y in years)+1)):
        raise ValueError('Expected years must be consecutive for year-over-year calculations')


def run(source=None, output=None, config_path=None, peers_path=None, stage=7):
    """Validate inputs and run stages through the requested number, publishing prepared outputs."""
    source = Path(source or ROOT/'data'/'pharma_financials_5yr.csv')
    output = Path(output or ROOT/'outputs')
    config = json.loads(Path(config_path or ROOT/'config'/'model.json').read_text())
    output.mkdir(parents=True,exist_ok=True)
    validate_model(config)
    rows, checks = validate(source,config)
    write_csv(output/'data_validation.csv',checks)
    if any(c['result']=='FAIL' for c in checks):
        (output/'RUN_STATUS.json').write_text(json.dumps({'status':'FAILED','reason':'Data validation failed. Earlier output files, if present, are stale.'},indent=2))
        raise ValueError('Data validation failed; inspect data_validation.csv. Earlier outputs are stale.')
    mapping = {}
    if stage >= 6:
        with Path(peers_path or ROOT/'config'/'peer_groups.csv').open(newline='',encoding='utf-8') as f:
            for p in csv.DictReader(f):
                if p['company_id'] in mapping:
                    raise ValueError(f'Duplicate peer assignment: {p["company_id"]}')
                if not p.get('peer_group') or not p.get('assignment_status'):
                    raise ValueError('Peer group and assignment_status are required')
                mapping[p['company_id']] = p
        missing = {r['company_id'] for r in rows}-mapping.keys()
        if missing:
            raise ValueError(f'Missing peer assignments: {sorted(missing)}')
    # Stage output is built in a temporary directory before successful files are published.
    with tempfile.TemporaryDirectory(prefix='crm-',dir=output.parent) as temp:
        out = Path(temp)
        write_csv(out/'data_validation.csv',checks)
        if stage >= 2:
            rows = metrics(rows); write_csv(out/'credit_metrics.csv',rows)
        if stage >= 3:
            rows = scores(rows,config); write_csv(out/'credit_scores.csv',rows)
        if stage >= 4:
            rows = trends(rows); write_csv(out/'trend_analysis.csv',rows)
        warnings = []
        if stage >= 5:
            warnings = alerts(rows,config)
            write_csv(out/'early_warning_alerts.csv',warnings,['company_id','fiscal_year','code','severity','metric','value','threshold','explanation'])
        if stage >= 6:
            rows = peers(rows,mapping); write_csv(out/'peer_analysis.csv',rows)
        if stage >= 7:
            report(rows,warnings,checks,config,out,source)
        for path in out.iterdir():
            if path.is_dir():
                shutil.copytree(path,output/path.name,dirs_exist_ok=True)
            else:
                shutil.copy2(path,output/path.name)
    (output/'RUN_STATUS.json').write_text(json.dumps({'status':'SUCCESS','completed_stage':stage,'model_version':config['version'],'dashboard_refreshed':stage == 7,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'rows':len(rows),'alerts':len(warnings)},indent=2))
    print(f'Completed stages 1–{stage}: {len(rows)} observations, {len(warnings)} historical alerts. Outputs: {output}')
    return rows,warnings


def main(default_stage=7):
    """Parse financial-only CLI arguments for a numbered stage entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--config',type=Path)
    parser.add_argument('--peers',type=Path)
    parser.add_argument('--stage',type=int,choices=range(1,8),default=default_stage)
    args = parser.parse_args()
    try:
        run(args.input,args.output,args.config,args.peers,args.stage)
    except (ValueError,OSError,KeyError,csv.Error) as exc:
        if args.output or (ROOT/'outputs').exists():
            dest = args.output or ROOT/'outputs'
            dest.mkdir(parents=True,exist_ok=True)
            (dest/'RUN_STATUS.json').write_text(json.dumps({'status':'FAILED','reason':str(exc),'note':'Earlier output files, if present, are stale.'},indent=2))
        parser.exit(1,f'CRM error: {exc}\n')

if __name__ == '__main__':
    main()
