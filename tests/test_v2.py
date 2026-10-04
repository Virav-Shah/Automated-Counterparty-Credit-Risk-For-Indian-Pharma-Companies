"""Independent V2 regression checks: dates, missing evidence and priority separation."""
import copy
import csv
import json
import math
import statistics
import tempfile
import unittest
from datetime import date, timedelta, datetime, timezone
from pathlib import Path
from src import crm, market, watchlist, pipeline_v2, download_market

CONFIG=json.loads((crm.ROOT/'config/monitoring.json').read_text())
AS_OF=date(2026,10,4)
COMPANY={'company_id':'Example','ticker':'EXAMPLE.NS','provider_url':'https://example.com/prices'}


def history(n=180,missing_volume=False):
    """Create known alternating returns with a fourfold recent-volatility increase."""
    prices=[100.0]
    for i in range(1,n): prices.append(prices[-1]*(1+(0.004 if i>n-31 else 0.001)*(-1 if i%2 else 1)))
    return [{'date':AS_OF-timedelta(days=n-1-i),'adjusted_close':p,'adjusted_volume':None if missing_volume else (300 if i==n-1 else 100),'volume':100} for i,p in enumerate(prices)]


class MarketTests(unittest.TestCase):
    def test_independent_windows_and_components(self):
        h=history();index=[{**r,'adjusted_close':100} for r in h]
        m=market.indicators(h,index,CONFIG,AS_OF,COMPANY)
        self.assertAlmostEqual(m['return_90'],h[-1]['adjusted_close']/h[-91]['adjusted_close']-1)
        self.assertAlmostEqual(m['relative_return_90'],m['return_90'])
        returns=[h[i]['adjusted_close']/h[i-1]['adjusted_close']-1 for i in range(1,len(h))]
        self.assertAlmostEqual(m['volatility_ratio'],statistics.stdev(returns[-30:])/statistics.stdev(returns[-150:-30]))
        self.assertAlmostEqual(m['volume_ratio'],3)
        self.assertEqual(m['market_stress_score'],35)
        self.assertEqual(m['market_status'],'WATCH')
        self.assertEqual(m['market_data_status'],'CURRENT')

    def test_drawdown_recovery_differs_from_maximum(self):
        self.assertAlmostEqual(market.maximum_drawdown([100,80,110]),-.2)
        h=history();h[-3]['adjusted_close']=100;h[-2]['adjusted_close']=50;h[-1]['adjusted_close']=120
        m=market.indicators(h,h,CONFIG,AS_OF,COMPANY)
        self.assertEqual(m['drawdown_30'],0)
        self.assertLessEqual(m['maximum_drawdown_90'],-.5)

    def test_missing_benchmark_endpoint_is_not_filled(self):
        h=history();b=[r for r in h if r['date']!=h[-91]['date']]
        m=market.indicators(h,b,CONFIG,AS_OF,COMPANY)
        self.assertIsNone(m['relative_return_90']);self.assertIsNone(m['market_stress_score'])
        self.assertEqual(m['market_data_status'],'INCOMPLETE')

    def test_holiday_placeholder_excluded_but_genuine_gap_retained(self):
        h=history();holiday=copy.deepcopy(h[60]);holiday.update(volume=0,adjusted_volume=0,adjusted_close=h[59]['adjusted_close']);h[60]=holiday
        benchmark=[r for i,r in enumerate(h) if i!=60]
        m=market.indicators(h,benchmark,CONFIG,AS_OF,COMPANY)
        self.assertEqual(m['excluded_nontrading_placeholders'],1)
        h[60]['volume']=5
        self.assertEqual(market.indicators(h,benchmark,CONFIG,AS_OF,COMPANY)['excluded_nontrading_placeholders'],0)

    def test_missing_volume_flat_baseline_and_short_history(self):
        h=history(missing_volume=True)
        self.assertIsNone(market.indicators(h,h,CONFIG,AS_OF,COMPANY)['market_stress_score'])
        flat=[{**r,'adjusted_close':100} for r in history()]
        self.assertIsNone(market.indicators(flat,flat,CONFIG,AS_OF,COMPANY)['volatility_ratio'])
        m=market.indicators(history(50),history(50),CONFIG,AS_OF,COMPANY)
        self.assertEqual(m['market_data_status'],'INCOMPLETE')

    def test_stale_and_missing_never_normal(self):
        h=history();m=market.indicators(h,h,CONFIG,AS_OF+timedelta(days=8),COMPANY)
        self.assertEqual(m['market_data_status'],'STALE');self.assertIsNone(m['market_stress_score'])
        self.assertEqual(market.indicators([],h,CONFIG,AS_OF,COMPANY)['market_data_status'],'MISSING')

    def test_band_boundaries(self):
        spec=CONFIG['market']['relative_return_90']
        self.assertEqual(market.upper_band(-.2,spec),25)
        self.assertEqual(market.upper_band(-.1,spec),10)
        self.assertEqual(market.upper_band(-.05,spec),0)
        self.assertEqual(market.lower_band(1.5,CONFIG['market']['volume_ratio']),5)
        self.assertEqual(market.status(75,CONFIG['market']),'SEVERE')

    def test_market_validation_duplicate_negative_and_future(self):
        fields=['date','ticker','company_id','adjusted_close','volume','adjusted_volume','source']
        row=dict(zip(fields,['2026-10-01','EXAMPLE.NS','Example',100,100,100,'https://example.com']))
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'prices.csv'
            def write(rows):
                with p.open('w',newline='') as f:w=csv.DictWriter(f,fields);w.writeheader();w.writerows(rows)
            write([row,row])
            with self.assertRaises(ValueError):market.validate_market(p,{'EXAMPLE.NS':COMPANY},AS_OF)
            write([{**row,'adjusted_close':-1}])
            with self.assertRaises(ValueError):market.validate_market(p,{'EXAMPLE.NS':COMPANY},AS_OF)
            write([row,{**row,'date':'2026-10-05'}])
            h,_=market.validate_market(p,{'EXAMPLE.NS':COMPANY},AS_OF);self.assertEqual(len(h['EXAMPLE.NS']),1)

    def test_download_requires_adjusted_close_and_adjusts_split_volume(self):
        stamps=[int(datetime(2026,10,d,tzinfo=timezone.utc).timestamp()) for d in [1,2]]
        result={'meta':{'symbol':'EXAMPLE.NS'},'timestamp':stamps,'indicators':{'adjclose':[{'adjclose':[50,51]}],'quote':[{'volume':[100,200]}]},'events':{'splits':{'split':{'date':stamps[1],'numerator':2,'denominator':1}}}}
        rows,_=download_market.decode_chart({'chart':{'result':[result]}},COMPANY,AS_OF)
        self.assertEqual(rows[0]['adjusted_volume'],200);self.assertEqual(rows[1]['adjusted_volume'],200)
        del result['indicators']['adjclose']
        with self.assertRaises(ValueError):download_market.decode_chart({'chart':{'result':[result]}},COMPANY,AS_OF)


class PriorityTests(unittest.TestCase):
    def setUp(self):
        self.f={'company_id':'Example','fiscal_year':'FY26','financial_risk_score':10,'risk_rating':'VERY LOW','debt_ebitda':1,'interest_coverage':6,'fcf_debt':.2}
        self.m={'market_date':'2026-05-01','market_stress_score':60,'market_status':'ELEVATED','market_data_status':'CURRENT','relative_return_90':-.15}
        self.now=date(2026,5,2)
    def decide(self,**kw):return watchlist.decide(kw.get('f',self.f),kw.get('m',self.m),[],CONFIG,kw.get('as_of',self.now),kw.get('previous'),kw.get('event'))
    def test_market_alone_preserves_financial_rating(self):
        r=self.decide();self.assertEqual(r['monitoring_priority'],'ENHANCED MONITORING');self.assertEqual(r['financial_rating'],'VERY LOW');self.assertEqual(r['financial_score'],10)
    def test_joint_high_requires_review(self):
        self.assertEqual(self.decide(f={**self.f,'risk_rating':'HIGH'})['monitoring_priority'],'CREDIT REVIEW')
    def test_confirmation_requires_aligned_fresh_dates(self):
        previous={**self.f,'debt_ebitda':.4}
        self.assertTrue(self.decide(previous=previous)['confirmed_deterioration'])
        stale={**self.f,'fiscal_year':'FY25'}
        self.assertFalse(self.decide(f=stale,previous=previous,as_of=AS_OF)['confirmed_deterioration'])
        self.assertFalse(self.decide(previous=previous,m={**self.m,'market_date':'2026-10-01'})['confirmed_deterioration'])
        self.assertFalse(self.decide(previous=previous,m={**self.m,'market_data_status':'STALE'})['confirmed_deterioration'])
    def test_missing_market_requires_watch_and_entity_requires_review(self):
        m={**self.m,'market_status':'NORMAL','market_stress_score':0}
        self.assertEqual(self.decide(m={**m,'market_data_status':'MISSING'})['monitoring_priority'],'WATCH')
        self.assertEqual(self.decide(m=m)['monitoring_priority'],'NORMAL')
        event={'event':'AMALGAMATED','successor':'Successor','effective_date':'2026-04-01','source':'https://example.com/filing'}
        self.assertEqual(self.decide(m=m,event=event)['monitoring_priority'],'CREDIT REVIEW')
        self.assertEqual(self.decide(m=m,event={**event,'effective_date':'2026-06-01'})['monitoring_priority'],'NORMAL')


class PipelineTests(unittest.TestCase):
    def test_full_v2_retains_every_financial_score_and_source(self):
        with tempfile.TemporaryDirectory() as t:
            out=Path(t)/'outputs';crm.run(output=out)
            before=json.loads((out/'dashboard_data.json').read_text())['rows']
            p=pipeline_v2.run(out,AS_OF)
            after=json.loads((out/'dashboard_data.json').read_text())
            self.assertEqual(before,after['rows']);self.assertEqual(len(p['watchlist']),19)
            self.assertEqual(sum(r['market_data_status']=='CURRENT' for r in p['market']),19)
            self.assertNotIn('JB Chemicals',{r['company_id'] for r in after['rows']})
            self.assertNotIn('JB Chemicals',{r['company_id'] for r in p['watchlist']})
            self.assertNotIn('qualitative',p)
            self.assertNotIn('factors',p)
            self.assertTrue(all(not any('qualitative' in key for key in r) for r in p['watchlist']))
            self.assertTrue(all(a['layer'] in ['FINANCIAL','MARKET'] for a in p['alerts']))
            self.assertFalse((out/'qualitative_summary.csv').exists())
            self.assertTrue((crm.ROOT/'data/qualitative/report_evidence.csv').exists())
            sun=next(r for r in p['watchlist'] if r['company_id']=='Sun Pharma')
            self.assertEqual(sun['monitoring_priority'],'WATCH')
            self.assertEqual(sun['financial_score'],6)
            self.assertEqual(sun['financial_rating'],'VERY LOW')
            latest=[r for r in after['rows'] if r['fiscal_year']=='FY25']
            from collections import Counter
            self.assertEqual(sorted(Counter(r['peer_group'] for r in latest).values()),[3,3,5,8])
            self.assertEqual(next(r for r in latest if r['company_id']=='Torrent Pharma')['peer_group'],'Global Generics & Diversified')
            self.assertEqual(next(r for r in latest if r['company_id']=='Gland Pharma')['peer_group'],'Complex / Specialty / Healthcare Platforms')
            self.assertFalse(any(r['confirmed_deterioration'] for r in p['watchlist']))
            self.assertNotIn('__V2_SCRIPT__',(out/'dashboard.html').read_text())
            self.assertEqual(len(list((out/'reports').glob('*.md'))),19)
            self.assertTrue(all(a['what_happened'] and a['why_it_matters'] and a['recommended_action'] for a in p['alerts']))
            manifest=json.loads((out/'V2_RUN_STATUS.json').read_text());self.assertEqual(manifest['status'],'SUCCESS')
    def test_bad_monitoring_config_rejected(self):
        for change in [('minimum_history',30),('volatility_baseline_days',1),('stale_after_calendar_days',-1)]:
            bad=copy.deepcopy(CONFIG);bad['market'][change[0]]=change[1]
            with self.assertRaises(ValueError):pipeline_v2.validate_config(bad)
        bad=copy.deepcopy(CONFIG);bad['market']['volume_ratio']['points']=[0,5]
        with self.assertRaises(ValueError):pipeline_v2.validate_config(bad)

if __name__=='__main__':unittest.main()
