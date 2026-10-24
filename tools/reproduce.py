"""Rebuild analytical SQLite and independently reconcile grouped public results."""
import csv
import json
from pathlib import Path
import sqlite3
import sys
from collections import defaultdict
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.release_qa import ROOT, validate_data, require, INTS

METRICS={'sales_units':'gross_sales_qty','full_exposure_cells':'full_exposure_flag','censored_cells':'censored_flag','no_exposure_cells':'no_exposure_flag','eod_zero_cells':'eod_zero_stock_flag','zero_sales_cells':'zero_sales_flag'}
GROUPS={'daily':['day_index'],'weekly':['pilot_week_index'],'store':['store_id'],'sku':['sku_id'],'exposure':['availability_status'],'sku_week':['sku_id','pilot_week_index']}

def reproduce(root=ROOT, destination=None):
    root=Path(root); tables=validate_data(root)
    db=sqlite3.connect(':memory:');db.row_factory=sqlite3.Row
    for name,rows in tables.items():
        columns=list(rows[0]); db.execute('CREATE TABLE '+name+' ('+','.join('"'+k+'" '+('INTEGER' if k in INTS else 'TEXT') for k in columns)+')')
        db.executemany('INSERT INTO '+name+' VALUES ('+','.join('?' for _ in columns)+')',[tuple(x[k] for k in columns) for x in rows])
    db.executescript((root/'sql/business_queries.sql').read_text())
    results={};checked=0
    for group,keys in GROUPS.items():
        python=defaultdict(lambda:defaultdict(int))
        for original in tables['fact_observed']:
            row=dict(original,pilot_week_index=(original['day_index']-2)//7+1)
            agg=python[tuple(row[k] for k in keys)];agg['cells']+=1
            for metric,column in METRICS.items():agg[metric]+=row[column]
            if group=='daily':agg['closing_store_units']+=row['eod_saleable_qty']
        sql=[dict(x) for x in db.execute('SELECT * FROM v_'+group+' ORDER BY '+','.join(keys))]
        require(len(sql)==len(python),'Group size mismatch')
        for row in sql:
            expected=python[tuple(row[k] for k in keys)]
            require(all(row[k]==v for k,v in expected.items()),'SQL/Python parity failure: '+group);checked+=1
        results[group]=sql
    totals=dict(db.execute('SELECT * FROM v_totals').fetchone())
    require(totals['sales_units']==5272 and totals['cells']==2688 and totals['closing_store_units_last_day']==119,'SQL total mismatch')
    require([x['sales_units'] for x in results['weekly']]==[942,835,753,584,558,659,503,438],'Weekly context mismatch')
    require(results['weekly'][-1]['full_exposure_cells']==77,'Week 8 exposure mismatch')
    require(next(x['sales_units'] for x in results['store'] if x['store_id']=='STORE-018')==904,'Store context mismatch')
    require(next(x['sales_units'] for x in results['sku'] if x['sku_id']=='SKU-0245')==47,'SKU context mismatch')
    results['totals']=[totals]
    if destination is not None:
        destination=Path(destination);destination.mkdir(parents=True,exist_ok=False)
        for name,rows in results.items():
            with (destination/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
        with sqlite3.connect(destination/'analytics.sqlite') as target: db.backup(target)
        (destination/'QA.json').write_text(json.dumps({'group_rows_reconciled':checked,'totals':totals},indent=2))
    db.close()
    return {'group_rows_reconciled':checked,'totals':totals}

if __name__=='__main__':
    import datetime
    destination=ROOT/'outputs'/datetime.datetime.now().strftime('analysis_%Y%m%d_%H%M%S_%f')
    print(json.dumps(reproduce(destination=destination),indent=2));print('RESULTS',destination)
