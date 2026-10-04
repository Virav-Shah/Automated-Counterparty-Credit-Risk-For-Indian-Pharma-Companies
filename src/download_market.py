"""Fetch real daily adjusted prices and split-adjusted volumes from Yahoo's chart feed.

Network I/O is isolated here. Cached inputs keep all analysis deterministic and offline.
The provider is an unofficial public chart interface and can rate-limit requests.
No fabricated history or unadjusted-close fallback is used after a download failure.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.parse import quote, urlencode
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
INDIA = ZoneInfo('Asia/Kolkata')
FIELDS = ['date','company_id','ticker','adjusted_close','volume','adjusted_volume','source']


def decode_chart(data, company, as_of):
    """Convert a chart response without imputing missing prices or daily volume."""
    chart=data.get('chart',{})
    if chart.get('error') or not chart.get('result'):
        raise ValueError(f'Provider returned no data: {chart.get("error")}')
    result=chart['result'][0]
    if result['meta'].get('symbol') != company['ticker']:
        raise ValueError('Provider symbol does not match requested ticker')
    adjusted=result['indicators'].get('adjclose',[{}])[0].get('adjclose')
    if not adjusted:
        raise ValueError('Adjusted-close history unavailable; raw close is not substituted')
    volumes=result['indicators']['quote'][0].get('volume',[])
    splits=[]
    for event in result.get('events',{}).get('splits',{}).values():
        factor=float(event['numerator'])/float(event['denominator'])
        splits.append((datetime.fromtimestamp(event['date'],INDIA).date(),factor))
    rows=[];skipped=0
    for i,stamp in enumerate(result.get('timestamp',[])):
        day=datetime.fromtimestamp(stamp,INDIA).date()
        if day>as_of: continue
        price=adjusted[i] if i<len(adjusted) else None
        volume=volumes[i] if i<len(volumes) else None
        if price is None or not math.isfinite(price) or price<=0:
            skipped+=1;continue
        valid_volume=volume if volume is not None and math.isfinite(volume) and volume>=0 else None
        factor=math.prod(f for split_day,f in splits if split_day>day)
        rows.append({'date':day.isoformat(),'company_id':company['company_id'],'ticker':company['ticker'],
                     'adjusted_close':price,'volume':valid_volume,
                     'adjusted_volume':valid_volume*factor if valid_volume is not None else None,
                     'source':company['provider_url']})
    if not rows: raise ValueError('No valid adjusted prices before the requested as-of date')
    return rows,{'long_name':result['meta'].get('longName',result['meta'].get('shortName','')),
                 'currency':result['meta'].get('currency'), 'instrument_type':result['meta'].get('instrumentType'),
                 'split_events':len(splits), 'invalid_prices_skipped':skipped,
                 'last_date':rows[-1]['date'],'observations':len(rows)}


def fetch_one(company,as_of,lookback,cache):
    """Save a verified-HTTPS raw response and derive normalized daily observations."""
    start=datetime.combine(as_of-timedelta(days=lookback),datetime.min.time(),INDIA)
    end=datetime.combine(as_of+timedelta(days=1),datetime.min.time(),INDIA)
    params=urlencode({'period1':int(start.timestamp()),'period2':int(end.timestamp()),'interval':'1d','events':'div,splits','includeAdjustedClose':'true'})
    url=f'https://query2.finance.yahoo.com/v8/finance/chart/{quote(company["ticker"],safe="")}?{params}'
    error=''
    for attempt in range(3):
        result=subprocess.run(['curl','--fail','--silent','--show-error','--user-agent','Mozilla/5.0','--max-time','30',url],capture_output=True,text=True)
        if result.returncode==0:
            try:
                data=json.loads(result.stdout)
                rows,meta=decode_chart(data,company,as_of)
                raw=cache/(company['ticker'].replace('^','INDEX_')+'.json')
                raw.write_text(result.stdout,encoding='utf-8')
                return rows,{'company_id':company['company_id'],'ticker':company['ticker'],'status':'SUCCESS',
                             'endpoint':url,'sha256':hashlib.sha256(result.stdout.encode()).hexdigest(),**meta}
            except (ValueError,KeyError,TypeError) as exc: error=str(exc)
        else: error=result.stderr.strip()
        if attempt<2: time.sleep(1+attempt)
    return [],{'company_id':company['company_id'],'ticker':company['ticker'],'status':'FAILED','error':error,'endpoint':url}


def download(as_of,output=None,tickers=None,lookback=550):
    """Download all instruments; publish the CSV only when every instrument succeeds."""
    output=Path(output or ROOT/'data'/'market_data.csv')
    with Path(tickers or ROOT/'config'/'tickers.csv').open(newline='',encoding='utf-8') as f: companies=list(csv.DictReader(f))
    if len({c['ticker'] for c in companies})!=len(companies): raise ValueError('Duplicate tickers')
    cache=output.parent/'market'/'raw';cache.mkdir(parents=True,exist_ok=True)
    rows=[];statuses=[]
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures={pool.submit(fetch_one,c,as_of,lookback,cache):c for c in companies}
        for future in as_completed(futures):
            values,status=future.result();rows.extend(values);statuses.append(status)
            print(f'{status["ticker"]}: {status["status"]} ({len(values)} sessions)',flush=True)
    manifest={'provider':'Yahoo Finance public chart feed','as_of':as_of.isoformat(),
              'retrieved_at':datetime.now(INDIA).isoformat(),'instruments':sorted(statuses,key=lambda s:s['ticker'])}
    manifest_path=output.parent/'market'/'download_manifest.json'
    manifest_path.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    failed=[s['ticker'] for s in statuses if s['status']=='FAILED']
    if failed: raise ValueError(f'Failed instruments: {failed}. Existing market_data.csv has not been replaced; see {manifest_path}')
    temporary=output.with_suffix('.csv.tmp')
    with temporary.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=FIELDS);writer.writeheader();writer.writerows(sorted(rows,key=lambda r:(r['ticker'],r['date'])))
    temporary.replace(output)
    return manifest


def main():
    """Parse download paths/date and report bounded provider or filesystem failures."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--as-of',type=date.fromisoformat,default=datetime.now(INDIA).date())
    parser.add_argument('--output',type=Path)
    parser.add_argument('--tickers',type=Path)
    args=parser.parse_args()
    try: download(args.as_of,args.output,args.tickers)
    except (ValueError,OSError) as exc: parser.exit(1,f'Market download error: {exc}\n')

if __name__=='__main__': main()
