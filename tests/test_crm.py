import csv
import json
import tempfile
import unittest
from pathlib import Path
from src import crm

class MonitoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config=json.loads((crm.ROOT/'config/model.json').read_text())
        cls.rows,cls.checks=crm.validate(crm.ROOT/'data/pharma_financials_5yr.csv',cls.config)
        cls.metrics=crm.metrics(cls.rows)
        cls.scores=crm.scores(cls.metrics,cls.config)
        cls.trends=crm.trends(cls.scores)

    def test_source_coverage(self):
        self.assertEqual(len(self.rows),100)
        self.assertTrue(all(c['result']=='PASS' for c in self.checks))

    def test_independent_metric_calculation(self):
        r=next(r for r in self.metrics if r['company_id']=='Sun Pharma' and r['fiscal_year']=='FY25')
        self.assertAlmostEqual(r['debt_ebitda'],2150/15272)
        self.assertEqual(r['free_cash_flow'],10400)
        self.assertAlmostEqual(r['revenue_growth'],52041/48497-1)
        self.assertAlmostEqual(r['net_debt_ebitda'],-8100/15272)

    def test_sort_before_growth(self):
        self.assertEqual(crm.metrics(list(reversed(self.rows))),self.metrics)

    def test_first_year_not_fabricated(self):
        first=[r for r in self.scores if r['fiscal_year']=='FY21']
        self.assertEqual(len(first),20)
        self.assertTrue(all(r['financial_risk_score'] is None and r['risk_rating']=='NOT SCORED' and r['score_available_points']==80 for r in first))
        self.assertTrue(all(r['score_change'] is None for r in self.trends if r['fiscal_year']=='FY22'))

    def test_score_reconciles(self):
        for r in self.scores:
            self.assertGreaterEqual(r['core_risk_score'],0)
            self.assertLessEqual(r['core_risk_score'],80)
            if r['financial_risk_score'] is not None:
                self.assertEqual(sum(r[k] for k in crm.COMPONENTS),r['financial_risk_score'])
                self.assertLessEqual(r['financial_risk_score'],100)

    def test_score_boundaries(self):
        for metric, cases in {
            'leverage':[(0.999,0),(1,6),(2,12),(3,20),(4,20),(4.001,25)],
            'coverage':[(1.99,20),(2,15),(3,8),(5,3),(8,3),(8.01,0)],
            'cash_flow':[(-0.01,20),(0,15),(0.05,10),(0.10,5),(0.20,5),(0.201,0)],
            'liquidity':[(0.79,15),(0.8,12),(1,6),(1.2,2),(1.5,2),(1.51,0)],
            'earnings':[(-0.11,10),(-0.1,7),(0,4),(0.05,2),(0.1,0)]
        }.items():
            for value,expected in cases:
                with self.subTest(metric=metric,value=value):
                    self.assertEqual(crm.band(value,self.config[metric]),expected)
        for value,expected in [(0,0),(.05,2),(.1,5),(.2,8),(.201,10)]:
            self.assertEqual(crm.band(value,self.config['working_capital'],inclusive=True),expected)
        for score,expected in [(14,'VERY LOW'),(15,'LOW'),(29,'LOW'),(30,'MODERATE'),(50,'HIGH'),(70,'CRITICAL'),(100,'CRITICAL')]:
            self.assertEqual(crm.rate(score,self.config),expected)

    def test_zero_debt_and_interest(self):
        r=dict(self.rows[0],total_debt=0,interest_expense=0,operating_cash_flow=100,capex=50)
        scored=crm.scores(crm.metrics([r]),self.config)[0]
        self.assertIsNone(scored['fcf_debt'])
        self.assertIsNone(scored['interest_coverage'])
        self.assertEqual(scored['servicing_points'],0)
        self.assertEqual(scored['cash_flow_points'],0)
        r['capex']=200
        scored=crm.scores(crm.metrics([r]),self.config)[0]
        self.assertEqual(scored['cash_flow_points'],20)
        self.assertIn('WEAK_CASH_GENERATION',[a['code'] for a in crm.alerts(crm.trends([scored]),self.config)])

    def test_debt_from_zero_alert(self):
        a=dict(self.rows[0],fiscal_year='FY21',total_debt=0)
        b=dict(a,fiscal_year='FY22',total_debt=10)
        series=crm.trends(crm.scores(crm.metrics([b,a]),self.config))
        self.assertIsNone(series[1]['debt_growth'])
        self.assertIn('DEBT_ACCELERATION',[a['code'] for a in crm.alerts(series,self.config)])

    def test_alert_strict_thresholds_and_migration(self):
        r=dict(self.trends[-1],debt_ebitda=3,interest_coverage=3,fcf_debt=.10,current_ratio=1,debt_growth=.20,revenue_growth=0,receivables_growth=0,score_change=9,debt_from_zero=False)
        self.assertEqual(crm.alerts([r],self.config),[])
        r.update(debt_ebitda=3.01,score_change=10)
        self.assertEqual({a['code'] for a in crm.alerts([r],self.config)},{'HIGH_LEVERAGE','RISK_MIGRATION'})

    def test_peers_exclude_self_ties_and_direction(self):
        a=dict(self.trends[-1],company_id='A',debt_ebitda=9,interest_coverage=2,financial_risk_score=40)
        b=dict(a,company_id='B',debt_ebitda=1,interest_coverage=10,financial_risk_score=10)
        c=dict(b,company_id='C')
        mapping={name:{'peer_group':'test','assignment_status':'PROVISIONAL'} for name in ['A','B','C']}
        rows=crm.peers([a,b,c],mapping)
        self.assertEqual(rows[0]['debt_ebitda_peer_median'],1)
        self.assertEqual(rows[0]['financial_risk_score_peer_median'],10)
        self.assertEqual(rows[0]['debt_ebitda_risk_percentile'],100)
        self.assertEqual(rows[0]['interest_coverage_risk_percentile'],100)
        self.assertEqual(rows[1]['debt_ebitda_risk_percentile'],25)
        singleton=crm.peers([a],mapping)[0]
        self.assertIsNone(singleton['debt_ebitda_peer_median'])
        self.assertIsNone(singleton['financial_risk_score_risk_percentile'])

    def test_validation_rejects_bad_inputs(self):
        for change in ['duplicate','nan','missing','negative','extra','year']:
            with self.subTest(change=change),tempfile.TemporaryDirectory() as tmp:
                rows=[dict(r) for r in self.rows]
                if change=='duplicate': rows[1]=dict(rows[0])
                if change=='nan': rows[0]['ebitda']='NaN'
                if change=='missing': rows[0]['cash']=''
                if change=='negative': rows[0]['revenue']=-1
                if change=='extra': rows[0]['unrequested']=1
                if change=='year': rows[0]['fiscal_year']='FY20'
                fields=crm.COLUMNS+(['unrequested'] if change=='extra' else [])
                path=Path(tmp)/'bad.csv';crm.write_csv(path,rows,fields)
                _,checks=crm.validate(path,self.config)
                self.assertTrue(any(c['result']=='FAIL' for c in checks))

    def test_bad_model_rejected(self):
        config=json.loads(json.dumps(self.config));config['coverage']['points'][0]=99
        with self.assertRaises(ValueError): crm.validate_model(config)

    def test_full_pipeline_and_invalid_rerun(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'outputs'
            rows,alerts=crm.run(output=out)
            self.assertEqual(len(rows),100)
            self.assertEqual(len(list((out/'reports').glob('*.md'))),20)
            payload=json.loads((out/'dashboard_data.json').read_text())
            self.assertEqual(len(payload['rows']),100)
            self.assertNotIn('__CRM_DATA__',(out/'dashboard.html').read_text())
            self.assertTrue(json.loads((out/'RUN_STATUS.json').read_text())['dashboard_refreshed'])
            before=(out/'credit_scores.csv').read_bytes()
            bad=Path(tmp)/'bad.csv';bad.write_text('company_id,fiscal_year\nA,FY25\n')
            with self.assertRaises(ValueError): crm.run(source=bad,output=out)
            self.assertEqual((out/'credit_scores.csv').read_bytes(),before)
            self.assertEqual(json.loads((out/'RUN_STATUS.json').read_text())['status'],'FAILED')

if __name__=='__main__': unittest.main()
