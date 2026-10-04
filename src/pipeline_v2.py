"""Offline V2 orchestration and publication with a separate run-status manifest.

Inputs are validated before publishing the V2 watchlist, reports and dashboard.
The financial engine remains the authoritative owner of the 100-point credit score.
"""
from __future__ import annotations
import csv
import hashlib
import json
import math
import re
import shutil
import tempfile
from datetime import date
from pathlib import Path
from . import crm, market, watchlist


def read_tickers(path,companies,benchmark):
    """Require exact financial-universe mapping plus one benchmark and unique tickers."""
    with Path(path).open(newline='',encoding='utf-8') as f:rows=list(csv.DictReader(f))
    equities=[r for r in rows if r['instrument']=='EQUITY']
    if {r['company_id'] for r in equities}!=set(companies) or len(equities)!=len(companies):raise ValueError('Equity tickers must map exactly once to the financial universe')
    if len({r['ticker'] for r in rows})!=len(rows):raise ValueError('Duplicate ticker mapping')
    indexes=[r for r in rows if r['instrument']=='BENCHMARK']
    if len(indexes)!=1 or indexes[0]['ticker']!=benchmark:raise ValueError('Exactly one configured benchmark is required')
    return {r['ticker']:r for r in rows}


def validate_config(c):
    """Reject incompatible weights, nonfinite bands, windows and status vocabularies."""
    def finite(value):
        return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value)
    maxima={'relative_return_90':35,'drawdown_30':30,'volatility_ratio':20,'volume_ratio':15}
    for key,maximum in maxima.items():
        spec=c['market'][key];bounds=spec.get('upper_bounds',spec.get('lower_bounds'));points=spec['points']
        if not bounds or any(not finite(v) for v in bounds+points) or len(points)!=len(bounds)+1 or sorted(set(bounds))!=bounds:
            raise ValueError(f'Invalid market bands: {key}')
        if max(points)!=maximum or min(points)<0:raise ValueError(f'Invalid market weight: {key}')
        if points!=sorted(points,reverse=key in ['relative_return_90','drawdown_30']):raise ValueError(f'Nonmonotonic market points: {key}')
    vocab={'market':['NORMAL','WATCH','ELEVATED','SEVERE']}
    for layer in vocab:
        bounds=c[layer]['status_upper_bounds']
        if c[layer]['status_labels']!=vocab[layer] or len(bounds)!=3 or any(not finite(v) or not 0<v<100 for v in bounds) or sorted(set(bounds))!=bounds:
            raise ValueError(f'Invalid {layer} status bands')
    for layer,keys in {'market':['minimum_history','volatility_baseline_days','drawdown_window','trading_days_per_year','stale_after_calendar_days'],
                       'integration':['financial_stale_after_calendar_days','confirmation_max_period_gap_days']}.items():
        for key in keys:
            if type(c[layer][key]) is not int or c[layer][key]<=0:raise ValueError(f'{layer}.{key} must be a positive integer')
    m=c['market']
    if m['volatility_baseline_days']<2 or m['drawdown_window']<2 or m['minimum_history']<max(91,31+m['volatility_baseline_days'],m['drawdown_window']):
        raise ValueError('Market minimum history must cover all return and independent volatility windows')
    i=c['integration']
    date(2026,i['financial_fiscal_year_end_month'],i['financial_fiscal_year_end_day'])
    for key in ['fundamental_score_increase','fundamental_leverage_increase','fundamental_coverage_drop_fraction','fundamental_fcf_debt_drop']:
        if not finite(i[key]) or i[key]<=0:raise ValueError(f'{key} must be a finite positive threshold')
    if i['fundamental_coverage_drop_fraction']>1 or not finite(i['relative_market_confirmation']) or i['relative_market_confirmation']>=0:
        raise ValueError('Invalid confirmation decline thresholds')


def run(output,as_of,market_path=None,config_path=None):
    """Build independently dated layers and append them to freshly generated V1 reports."""
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    c=json.loads(Path(config_path or crm.ROOT/'config/monitoring.json').read_text());validate_config(c)
    # Use in-memory full-precision financial records, never rounded exported metrics.
    financial_bytes=(output/'dashboard_data.json').read_bytes()
    financial=json.loads(financial_bytes)
    rows=financial['rows'];companies={r['company_id'] for r in rows}
    mapping=read_tickers(crm.ROOT/'config/tickers.csv',companies,c['benchmark_ticker'])
    market_path=Path(market_path or crm.ROOT/'data/market_data.csv')
    histories,market_checks=market.validate_market(market_path,mapping,as_of)
    benchmark=histories[c['benchmark_ticker']]
    metrics=[market.indicators(histories[t],benchmark,c,as_of,mapping[t]) for t in mapping if mapping[t]['instrument']=='EQUITY']
    market_by_company={r['company_id']:r for r in metrics}
    with (crm.ROOT/'config/entity_events.csv').open(newline='',encoding='utf-8') as f:
        events={r['company_id']:r for r in csv.DictReader(f)}
    result=[];latest=[]
    for company in sorted(companies):
        history=sorted([r for r in rows if r['company_id']==company and watchlist.financial_period_end(r['fiscal_year'],c)<=as_of],key=lambda r:r['fiscal_year'])
        if not history:raise ValueError(f'No financial period available before as-of date for {company}')
        r=history[-1];previous=history[-2] if len(history)>1 else None;latest.append(r)
        alerts=[a for a in financial['alerts'] if a['company_id']==company and a['fiscal_year']==r['fiscal_year']]
        result.append(watchlist.decide(r,market_by_company[company],alerts,c,as_of,previous,events.get(company)))
    f_alerts=watchlist.explain_financial([a for a in financial['alerts'] if any(r['company_id']==a['company_id'] and r['fiscal_year']==a['fiscal_year'] for r in latest)],c)
    all_alerts=f_alerts+market.market_alerts(metrics)
    for r in result:
        r['current_alert_count']=sum(a['company_id']==r['company_id'] for a in all_alerts)
        r['relative_return_90']=market_by_company[r['company_id']]['relative_return_90']
    result.sort(key=lambda r:(-r['priority_rank'],-(r['financial_score'] or 0),r['company_id']))
    payload={'config':c,'as_of':as_of.isoformat(),'watchlist':result,'market':metrics,'alerts':all_alerts,'market_checks':market_checks,'entity_events':list(events.values())}
    financial['v2']=payload
    data=json.dumps(financial,allow_nan=False)
    with tempfile.TemporaryDirectory(prefix='crm-v2-',dir=output.parent) as temp:
        out=Path(temp)
        crm.write_csv(out/'credit_watchlist.csv',result)
        crm.write_csv(out/'market_indicators.csv',metrics)
        crm.write_csv(out/'market_validation.csv',market_checks)
        fields=['company_id','date','layer','code','severity','metric','value','threshold','what_happened','why_it_matters','recommended_action','source','source_location','review_status']
        crm.write_csv(out/'monitoring_alerts.csv',all_alerts,fields)
        (out/'dashboard_data.json').write_text(data,encoding='utf-8')
        script=(crm.ROOT/'src/dashboard_v2.js').read_text(encoding='utf-8')
        template=(crm.ROOT/'src/dashboard.html').read_text(encoding='utf-8')
        (out/'dashboard.html').write_text(template.replace('__CRM_DATA__',data.replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')).replace('__V2_SCRIPT__',script),encoding='utf-8')
        report_dir=out/'reports';report_dir.mkdir()
        for r in result:
            company=r['company_id'];name=re.sub(r'[^a-z0-9]+','_',company.lower()).strip('_')+'.md'
            base=(output/'reports'/name).read_text().split('\n# Credit monitoring review')[0]
            m=market_by_company[company]
            content=f'\n# Credit monitoring review\n\nMonitoring as of {as_of.isoformat()}. Priority: **{r["monitoring_priority"]}**. Financial rating remains **{r["financial_rating"]}**.\n\n'
            content+=f'| Layer | Score | Classification | Data status |\n|---|---:|---|---|\n| Financial ({r["financial_year"]}) | {crm.display(r["financial_score"])} /100 | {r["financial_rating"]} | {r["financial_data_status"]}; assumed period end {r["financial_period_end"]} |\n| Market ({m["market_date"]}) | {crm.display(m["market_stress_score"])} /100 | {m["market_status"]} | {m["market_data_status"]} |\n'
            content+='\n## Why this priority\n\n'+'\n'.join('- '+reason for reason in r['reasons'].split(' | '))
            content+=f'\n\nAction: {r["recommended_action"]}\n\nSignal confirmation: {r["confirmation_status"]}.\n\n## Market observations\n\n'
            content+=f'30-session return: {crm.display(m["return_30"],True)}. 90-session return: {crm.display(m["return_90"],True)}. NIFTY Pharma 90-session return: {crm.display(m["benchmark_return_90"],True)}. Relative performance: {crm.display(m["relative_return_90"],True)}.\n\nCurrent 30-session drawdown: {crm.display(m["drawdown_30"],True)}. 90-session maximum drawdown: {crm.display(m["maximum_drawdown_90"],True)}. Daily 30-session volatility: {crm.display(m["volatility_30_daily"],True)}. Volatility ratio: {crm.display(m["volatility_ratio"])}x. Volume ratio: {crm.display(m["volume_ratio"])}x.\n\nSource: {m["market_source"]}.\n'
            content+='## Explainable alerts\n\n'
            for a in [a for a in all_alerts if a['company_id']==company]:
                content+=f'- **[{a["layer"]}/{a["severity"]}] {a["code"]}**\n  - What happened: {a["what_happened"]}\n  - Why it matters: {a["why_it_matters"]}\n  - Action: {a["recommended_action"]}\n'
            (report_dir/name).write_text(base+content,encoding='utf-8')
        for path in out.iterdir():
            if path.is_dir():shutil.copytree(path,output/path.name,dirs_exist_ok=True)
            else:shutil.copy2(path,output/path.name)
    manifest={'status':'SUCCESS','version':c['version'],'as_of':as_of.isoformat(),'companies':len(result),
              'market_complete_companies':sum(r['market_data_status']=='CURRENT' for r in metrics),
              'financial_payload_sha256':hashlib.sha256(financial_bytes).hexdigest(),
              'source_hashes':{str(p.relative_to(crm.ROOT)) if p.is_relative_to(crm.ROOT) else str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [market_path,Path(config_path or crm.ROOT/'config/monitoring.json'),crm.ROOT/'config/tickers.csv',crm.ROOT/'config/entity_events.csv']}}
    # Remove retired computed overlays after a successful publication; source research is retained.
    for name in ['qualitative_summary.csv','qualitative_evidence.csv']:
        (output/name).unlink(missing_ok=True)
    (output/'V2_RUN_STATUS.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(f'V2: {len(result)} counterparties; {manifest["market_complete_companies"]} complete market layers.')
    return payload
