"""Pure calculations for the independent market-stress layer.

Windows count trading observations. Relative returns use exactly matching company
and index endpoints. Freshness gates prevent old snapshots being labelled NORMAL.
"""
from __future__ import annotations
import csv
import math
import statistics
from collections import defaultdict
from datetime import date
from pathlib import Path


def validate_market(path, tickers, as_of):
    """Read cached CSV, reject malformed/duplicate observations and future leakage."""
    by_ticker=defaultdict(list);checks=[];seen=set()
    with Path(path).open(newline='',encoding='utf-8-sig') as f:
        reader=csv.DictReader(f)
        required={'date','ticker','company_id','adjusted_close','volume','adjusted_volume','source'}
        if not required.issubset(reader.fieldnames or []): raise ValueError('Market CSV is missing required columns')
        for line,r in enumerate(reader,2):
            try:
                day=date.fromisoformat(r['date']); price=float(r['adjusted_close'])
                volume=float(r['adjusted_volume']) if r['adjusted_volume'].strip() else None
                raw_volume=float(r['volume']) if r['volume'].strip() else None
            except (ValueError,TypeError): raise ValueError(f'Malformed market observation on row {line}') from None
            if r['ticker'] not in tickers: raise ValueError(f'Unknown market ticker: {r["ticker"]}')
            if r['company_id']!=tickers[r['ticker']]['company_id']: raise ValueError('Market ticker/company mapping mismatch')
            if not math.isfinite(price) or price<=0 or any(v is not None and (not math.isfinite(v) or v<0) for v in [volume,raw_volume]):
                raise ValueError(f'Invalid market price or volume on row {line}')
            if day>as_of: continue  # Exact as-of runs never consume later observations.
            key=(r['ticker'],day)
            if key in seen: raise ValueError(f'Duplicate market observation: {key}')
            seen.add(key)
            by_ticker[r['ticker']].append({**r,'date':day,'adjusted_close':price,'adjusted_volume':volume,'volume':raw_volume})
    for ticker in tickers:
        values=sorted(by_ticker[ticker],key=lambda r:r['date']);by_ticker[ticker]=values
        checks.append({'ticker':ticker,'company_id':tickers[ticker]['company_id'],'observations':len(values),
                       'first_date':values[0]['date'].isoformat() if values else None,
                       'last_date':values[-1]['date'].isoformat() if values else None,
                       'age_calendar_days':(as_of-values[-1]['date']).days if values else None})
    return by_ticker,checks


def upper_band(value, spec):
    """Lower metric values receive greater stress; exact bounds enter the next band."""
    if value is None:return None
    for bound,points in zip(spec['upper_bounds'],spec['points']):
        if value<bound:return points
    return spec['points'][-1]


def lower_band(value, spec):
    """Spikes score upward; equality enters the band beginning at that threshold."""
    if value is None:return None
    result=spec['points'][0]
    for bound,points in zip(spec['lower_bounds'],spec['points'][1:]):
        if value>=bound:result=points
    return result


def status(score, config):
    """Classify one layer without combining it with a financial credit score."""
    if score is None:return 'UNAVAILABLE'
    for bound,label in zip(config['status_upper_bounds'],config['status_labels']):
        if score<bound:return label
    return config['status_labels'][-1]


def maximum_drawdown(prices):
    """Maximum historical peak-to-trough loss in a window, as a negative fraction."""
    peak=prices[0];worst=0
    for price in prices:
        peak=max(peak,price);worst=min(worst,price/peak-1)
    return worst


def indicators(history, benchmark, config, as_of, company):
    """Return metrics plus completeness/freshness; never manufacture a complete score."""
    c=config['market']
    # Yahoo occasionally repeats a prior close with zero volume on exchange holidays.
    # Exclude only this exact pattern when the benchmark also lacks that date.
    # Preserve real zero-volume or nonmatching-price observations and benchmark gaps.
    benchmark_dates={r['date'] for r in benchmark}
    original_count=len(history)
    history=[r for i,r in enumerate(history) if not (i>0 and r['date'] not in benchmark_dates and r['volume']==0 and r['adjusted_close']==history[i-1]['adjusted_close'])]
    prices=[r['adjusted_close'] for r in history]
    last=history[-1]['date'] if history else None
    result={'company_id':company['company_id'],'ticker':company['ticker'],
            'market_date':last.isoformat() if last else None,'observations':len(history),'excluded_nontrading_placeholders':original_count-len(history),
            'market_age_days':(as_of-last).days if last else None,
            'return_30':None,'return_90':None,'benchmark_return_90':None,'relative_return_90':None,
            'volatility_30_daily':None,'volatility_30_annualized':None,'volatility_baseline_daily':None,
            'volatility_ratio':None,'drawdown_30':None,'maximum_drawdown_90':None,'volume_ratio':None,
            'relative_points':None,'drawdown_points':None,'volatility_points':None,'volume_points':None,
            'market_stress_score':None,'market_status':'UNAVAILABLE','market_data_status':'MISSING',
            'market_source':company['provider_url'],'missing_reason':''}
    if not history:result['missing_reason']='No observations';return result
    result['market_data_status']='CURRENT'
    if result['market_age_days']>c['stale_after_calendar_days']:result['market_data_status']='STALE'
    if len(prices)>=31:result['return_30']=prices[-1]/prices[-31]-1
    if len(prices)>=91:
        start=history[-91]['date'];end=history[-1]['date']
        result['return_90']=prices[-1]/prices[-91]-1
        index={r['date']:r['adjusted_close'] for r in benchmark}
        if start in index and end in index:
            result['benchmark_return_90']=index[end]/index[start]-1
            result['relative_return_90']=result['return_90']-result['benchmark_return_90']
    if len(prices)>=c['drawdown_window']:result['drawdown_30']=prices[-1]/max(prices[-c['drawdown_window']:])-1
    if len(prices)>=90:result['maximum_drawdown_90']=maximum_drawdown(prices[-90:])
    returns=[prices[i]/prices[i-1]-1 for i in range(1,len(prices))]
    if len(returns)>=30:
        recent=statistics.stdev(returns[-30:]);result['volatility_30_daily']=recent
        result['volatility_30_annualized']=recent*math.sqrt(c['trading_days_per_year'])
        n=c['volatility_baseline_days']
        if len(returns)>=30+n:
            baseline=statistics.stdev(returns[-(30+n):-30]);result['volatility_baseline_daily']=baseline
            # A completely flat baseline is undefined, not an arbitrary infinite spike.
            if baseline>0:result['volatility_ratio']=recent/baseline
    if len(history)>=31:
        previous=[r['adjusted_volume'] for r in history[-31:-1]];latest=history[-1]['adjusted_volume']
        if latest is not None and all(v is not None for v in previous) and statistics.mean(previous)>0:
            result['volume_ratio']=latest/statistics.mean(previous)
    result['relative_points']=upper_band(result['relative_return_90'],c['relative_return_90'])
    result['drawdown_points']=upper_band(result['drawdown_30'],c['drawdown_30'])
    result['volatility_points']=lower_band(result['volatility_ratio'],c['volatility_ratio'])
    result['volume_points']=lower_band(result['volume_ratio'],c['volume_ratio'])
    missing=[k for k in ['relative_points','drawdown_points','volatility_points','volume_points'] if result[k] is None]
    if len(history)<c['minimum_history']:missing.append(f'minimum {c["minimum_history"]} sessions')
    result['missing_reason']='; '.join(missing)
    if missing:
        if result['market_data_status']=='CURRENT':result['market_data_status']='INCOMPLETE'
    elif result['market_data_status']=='CURRENT':
        result['market_stress_score']=sum(result[k] for k in ['relative_points','drawdown_points','volatility_points','volume_points'])
        result['market_status']=status(result['market_stress_score'],c)
    return result


def market_alerts(rows):
    """Explain each stress component with observed event, implication and next action."""
    alerts=[]
    rules=[('relative_points','relative_return_90','RELATIVE_UNDERPERFORMANCE','Company underperformed NIFTY Pharma over 90 trading sessions','Sector-relative weakness may precede reported financial deterioration','Check recent filings and business developments.'),
           ('drawdown_points','drawdown_30','MARKET_DRAWDOWN','Adjusted price is below its 30-session peak','A sustained drawdown warrants closer monitoring','Investigate recent catalysts and reassess monitoring frequency.'),
           ('volatility_points','volatility_ratio','VOLATILITY_SPIKE','Recent volatility increased versus the preceding baseline','Higher uncertainty can signal company-specific stress','Review market disclosures and the cause of volatility.'),
           ('volume_points','volume_ratio','VOLUME_SPIKE','Trading volume increased versus the prior 30-session average','Unusual trading activity needs context and is not itself credit deterioration','Check announcements and corporate actions before escalating.')]
    for r in rows:
        if r['market_data_status']!='CURRENT':continue
        for points,metric,code,what,why,action in rules:
            if r[points]:alerts.append({'company_id':r['company_id'],'date':r['market_date'],'layer':'MARKET','code':code,
                                      'severity':'HIGH' if r['market_status'] in ['ELEVATED','SEVERE'] else 'MEDIUM',
                                      'metric':metric,'value':r[metric],'what_happened':what,'why_it_matters':why,'recommended_action':action})
    return alerts
