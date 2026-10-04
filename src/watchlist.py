"""Rule-based monitoring decisions from financial and market observations.

All escalations have an explanation; numeric financial scores are never overwritten.
Confirmed deterioration requires comparable dates and fresh fundamental/market data.
"""
from __future__ import annotations
from datetime import date

PRIORITIES=['NORMAL','WATCH','ENHANCED MONITORING','CREDIT REVIEW']
ACTIONS={
    'NORMAL':'Refresh financial and market data at the next monitoring cycle.',
    'WATCH':'Refresh missing market data and financials and investigate flagged developments.',
    'ENHANCED MONITORING':'Review the risk drivers, current exposure and credit terms; increase monitoring frequency.',
    'CREDIT REVIEW':'Perform a priority counterparty review, verify the legal entity and current exposure, and reassess approved terms.'
}
FINANCIAL_EXPLANATIONS={
 'HIGH_LEVERAGE':('Debt is high relative to operating earnings.','Review debt maturities and reassess credit terms.'),
 'WEAK_COVERAGE':('Operating earnings provide limited interest cover.','Review debt servicing capacity and refinancing needs.'),
 'WEAK_CASH_GENERATION':('Cash generation provides weak support for the debt burden.','Review cash forecasts, capex commitments and current exposure.'),
 'LIQUIDITY_PRESSURE':('Short-term liabilities exceed current assets.','Review near-term liquidity and payment obligations.'),
 'DEBT_ACCELERATION':('Borrowing increased faster than the monitoring threshold.','Check acquisition funding and debt drawdowns.'),
 'REVENUE_DETERIORATION':('Falling revenue can weaken future debt servicing.','Review demand, margins and recent operating disclosures.'),
 'RECEIVABLES_DETERIORATION':('Collections may be lagging reported sales growth.','Check receivable ageing and customer payment behaviour.'),
 'RISK_MIGRATION':('More financial scoring thresholds were breached.','Review the drivers of score migration and current credit terms.')
}


def financial_period_end(year,config):
    """Use the explicit, configurable March fiscal-year-end assumption for freshness."""
    c=config['integration']
    return date(2000+int(year[2:]),c['financial_fiscal_year_end_month'],c['financial_fiscal_year_end_day'])


def fundamental_deterioration(current,previous,config):
    """Capture adverse financial changes without inferring causality from market moves."""
    if previous is None:return []
    c=config['integration'];signals=[]
    for metric,threshold,comparison,label in [
        ('debt_ebitda',c['fundamental_leverage_increase'],'rise','Debt/EBITDA increased'),
        ('fcf_debt',c['fundamental_fcf_debt_drop'],'fall','FCF/debt declined')]:
        old,new=previous.get(metric),current.get(metric)
        if old is not None and new is not None and ((new-old>=threshold) if comparison=='rise' else (old-new>=threshold)):
            signals.append(f'{label} from {old:.3f} to {new:.3f}')
    old,new=previous.get('interest_coverage'),current.get('interest_coverage')
    if old is not None and new is not None and old>0 and 1-new/old>=c['fundamental_coverage_drop_fraction']:
        signals.append(f'Interest coverage declined from {old:.2f}x to {new:.2f}x')
    old,new=previous.get('financial_risk_score'),current.get('financial_risk_score')
    if old is not None and new is not None and new-old>=c['fundamental_score_increase']:
        signals.append(f'Financial risk score increased from {old} to {new}')
    return signals


def decide(financial,market,alerts,config,as_of,previous=None,event=None):
    """Return priority, confirmation status, dates, coverage and explicit rule reasons."""
    end=financial_period_end(financial['fiscal_year'],config)
    age=(as_of-end).days
    fresh=0<=age<=config['integration']['financial_stale_after_calendar_days']
    financial_status='CURRENT' if fresh else 'STALE'
    reasons=[];priority=0
    def escalate(level,reason):
        """Keep the highest triggered priority while retaining every explanatory reason."""
        nonlocal priority
        priority=max(priority,PRIORITIES.index(level));reasons.append(reason)
    rating=financial['risk_rating'];m=market['market_status']
    financial_high=rating in ['HIGH','CRITICAL']
    market_high=m in ['ELEVATED','SEVERE'] and market['market_data_status']=='CURRENT'
    signals=fundamental_deterioration(financial,previous,config)
    market_day=date.fromisoformat(market['market_date']) if market['market_date'] else None
    gap=abs((market_day-end).days) if market_day else None
    relative=market.get('relative_return_90')
    confirmed=bool(signals and market_high and relative is not None and relative<config['integration']['relative_market_confirmation'] and fresh and gap is not None and gap<=config['integration']['confirmation_max_period_gap_days'])
    if rating=='CRITICAL':escalate('CREDIT REVIEW','Critical financial rating requires priority credit review.')
    elif rating=='HIGH':escalate('ENHANCED MONITORING','High financial rating warrants enhanced monitoring.')
    elif rating=='MODERATE':escalate('WATCH','Moderate financial rating warrants a watchlist review.')
    if any(a['severity']=='HIGH' for a in alerts):escalate('ENHANCED MONITORING','A HIGH fundamental early-warning rule is triggered.')
    elif alerts:escalate('WATCH','Fundamental early-warning rules are triggered.')
    if market_high:escalate('ENHANCED MONITORING',f'Market-led monitoring: market stress is {m}; financial rating remains {rating}.')
    elif m=='WATCH':escalate('WATCH','Independent market stress indicates WATCH.')
    if financial_high and market_high and fresh:escalate('CREDIT REVIEW','High financial risk and elevated current market stress jointly require credit review.')
    if confirmed:escalate('CREDIT REVIEW' if financial_high else 'ENHANCED MONITORING','Confirmed deterioration: adverse fundamental changes and sector-relative market stress have sufficiently aligned, fresh dates.')
    if not fresh:escalate('WATCH',f'Financial inputs end {end.isoformat()} and are {age} days old; refresh before drawing current credit conclusions.')
    if market['market_data_status']!='CURRENT':escalate('WATCH',f'Market layer is {market["market_data_status"]}; do not treat missing or stale signals as normal.')
    if event and date.fromisoformat(event['effective_date'])<=as_of:
        escalate('CREDIT REVIEW',f'Entity transition: {event["event"]} into {event["successor"]} effective {event["effective_date"]}. Verify counterparty identity and exposure continuity.')
    if not reasons:reasons=['Fresh, complete layers have no monitoring escalation triggers.']
    return {'company_id':financial['company_id'],'monitoring_as_of':as_of.isoformat(),
            'financial_year':financial['fiscal_year'],'financial_period_end':end.isoformat(),
            'financial_score':financial['financial_risk_score'],'financial_rating':rating,
            'financial_data_status':financial_status,'financial_age_days':age,
            'market_score':market['market_stress_score'],'market_status':m,'market_date':market['market_date'],
            'market_data_status':market['market_data_status'],
            'monitoring_priority':PRIORITIES[priority],'priority_rank':priority,
            'confirmed_deterioration':confirmed,'financial_market_gap_days':gap,
            'fundamental_deterioration':'; '.join(signals),
            'confirmation_status':'CONFIRMED' if confirmed else 'NOT CONFIRMED: financial period and market signal dates are too far apart or stale' if signals and market_high and (not fresh or gap is None or gap>config['integration']['confirmation_max_period_gap_days']) else 'NOT CONFIRMED',
            'reasons':' | '.join(reasons),'recommended_action':ACTIONS[PRIORITIES[priority]],
            'entity_event':event['event'] if event and date.fromisoformat(event['effective_date'])<=as_of else None,
            'entity_event_source':event['source'] if event and date.fromisoformat(event['effective_date'])<=as_of else None}


def explain_financial(alerts,config):
    """Add what/why/action fields to existing alerts while retaining V1 rule values."""
    result=[]
    for a in alerts:
        why,action=FINANCIAL_EXPLANATIONS[a['code']]
        result.append({**a,'layer':'FINANCIAL','date':financial_period_end(a['fiscal_year'],config).isoformat(),
                       'what_happened':f'{a["explanation"]}; observed {a["value"]}, threshold {a["threshold"]}.',
                       'why_it_matters':why,'recommended_action':action})
    return result
