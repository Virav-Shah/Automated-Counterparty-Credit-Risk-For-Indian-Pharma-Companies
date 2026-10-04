"""Project entry point: seven financial stages plus optional independent V2 layers.

The default is an offline full run using cached market data.
Use --financial-only for the original seven-stage workflow. Network refresh is an
explicit --refresh-market step and preserves existing market CSV on fetch failure.
"""
from __future__ import annotations
import argparse
import json
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from src import crm


def main():
    """Parse paths/as-of date, run validated layers, and record V2 publication failures."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,help='Financial CSV; default data/pharma_financials_5yr.csv')
    parser.add_argument('--output',type=Path,default=crm.ROOT/'outputs')
    parser.add_argument('--config',type=Path,help='Financial model config')
    parser.add_argument('--peers',type=Path,help='Peer assignments CSV')
    parser.add_argument('--stage',type=int,choices=range(1,8),default=7)
    parser.add_argument('--financial-only',action='store_true',help='Run V1 without independent market overlay')
    parser.add_argument('--as-of',type=date.fromisoformat,default=datetime.now(ZoneInfo('Asia/Kolkata')).date())
    parser.add_argument('--refresh-market',action='store_true',help='Download public prices before the offline run; requires curl and network')
    parser.add_argument('--market-input',type=Path,help='Alternate cached market CSV')
    parser.add_argument('--monitoring-config',type=Path,help='Independent V2 monitoring rules JSON')
    args=parser.parse_args()
    try:
        if args.refresh_market:
            from src.download_market import download
            download(args.as_of,args.market_input)
        crm.run(args.input,args.output,args.config,args.peers,args.stage)
        if args.stage==7 and not args.financial_only:
            from src.pipeline_v2 import run
            run(args.output,args.as_of,args.market_input,args.monitoring_config)
    except (ValueError,OSError,KeyError,TypeError) as exc:
        args.output.mkdir(parents=True,exist_ok=True)
        (args.output/'V2_RUN_STATUS.json').write_text(json.dumps({'status':'FAILED','reason':str(exc),'note':'V2 outputs are not current. Inspect inputs, correct the error and rerun.'},indent=2))
        parser.exit(1,f'CRM error: {exc}\n')

if __name__=='__main__':main()
