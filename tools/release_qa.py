"""Fail-closed validation of the frozen public descriptive release (stdlib only)."""
from pathlib import Path
import csv
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = {
 'fact_observed': 'run_id scenario_id policy_id day_index available_at_day store_id sku_id opening_saleable_qty gross_sales_qty eod_saleable_qty availability_status eod_zero_stock_flag full_exposure_flag censored_flag no_exposure_flag zero_sales_flag provenance'.split(),
 'dim_store': 'store_id city_id city_name region_id region_name assigned_dc_id capacity_liters provenance'.split(),
 'dim_sku': 'sku_id category expirable lot_tracking_required unit_volume_ml provenance'.split(),
 'dim_day': 'day_index pilot_day_number pilot_week_index pilot_week_label pilot_day_in_week_index'.split(),
}
INTS = set('day_index available_at_day opening_saleable_qty gross_sales_qty eod_saleable_qty eod_zero_stock_flag full_exposure_flag censored_flag no_exposure_flag zero_sales_flag capacity_liters expirable lot_tracking_required unit_volume_ml pilot_day_number pilot_week_index pilot_day_in_week_index'.split())

def require(condition, message):
    if not condition:
        raise ValueError(message)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def safe_path(root, relative):
    root = Path(root).resolve()
    path = root / relative
    require(path.resolve().is_relative_to(root), 'Unsafe path: ' + str(relative))
    for part in [path, *path.parents]:
        if part == root:
            break
        require(not part.is_symlink(), 'Symlink input rejected: ' + str(relative))
    return path

def validate_data(root=ROOT):
    manifest = json.loads(safe_path(root, 'data/manifest.json').read_text(encoding='utf-8'))
    require(set(manifest['files']) == {x+'.csv' for x in SCHEMAS}, 'Unexpected public manifest file set')
    tables = {}
    for name, schema in SCHEMAS.items():
        path = safe_path(root, 'data/powerbi/'+name+'.csv')
        require(path.is_file(), 'Missing required CSV: '+name)
        spec = manifest['files'][path.name]
        with path.open(encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            require(reader.fieldnames == schema == spec['columns'], 'Unexpected CSV schema: '+name)
            rows = list(reader)
        require(digest(path) == spec['sha256'], 'CSV checksum mismatch: '+name)
        require(len(rows) == spec['rows'] == {'fact_observed':2688,'dim_day':56,'dim_store':6,'dim_sku':8}[name], 'Unexpected rows: '+name)
        for row in rows:
            require(set(row)==set(schema) and all(v not in ('', None) for v in row.values()), 'Null or malformed row: '+name)
            for key in INTS & row.keys():
                require(re.fullmatch(r'\d+',row[key]) is not None, 'Invalid integer: '+key)
                row[key] = int(row[key])
        tables[name] = rows
    keys = {}
    for name,key in [('dim_day','day_index'),('dim_store','store_id'),('dim_sku','sku_id')]:
        keys[key] = {x[key] for x in tables[name]}
        require(len(keys[key])==len(tables[name]), 'Duplicate dimension key: '+name)
    require(keys['day_index']==set(range(2,58)), 'Unexpected day coverage')
    for d in tables['dim_day']:
        day=d['day_index']; require((d['pilot_day_number'],d['pilot_week_index'],d['pilot_day_in_week_index'],d['pilot_week_label'])==(day-1,(day-2)//7+1,(day-2)%7+1,'Week '+str((day-2)//7+1)), 'Invalid relative-day attributes')
    seen=set()
    for row in tables['fact_observed']:
        key=tuple(row[k] for k in ('day_index','store_id','sku_id'))
        require(key not in seen, 'Duplicate fact grain'); seen.add(key)
        require(all(row[k] in v for k,v in keys.items()), 'Orphan foreign key')
        require(row['available_at_day']==row['day_index'], 'Invalid as-of day')
        require(row['provenance']=='SYN_OBSERVED', 'Invalid observed provenance')
        require(row['opening_saleable_qty']==row['gross_sales_qty']+row['eod_saleable_qty'], 'Service observation conservation mismatch')
        status=row['availability_status']
        require(status in ('FULL_EXPOSURE','DEPLETED_UNCONFIRMED','NO_EXPOSURE'), 'Invalid exposure status')
        expected={'full_exposure_flag':int(status=='FULL_EXPOSURE'),'censored_flag':int(status!='FULL_EXPOSURE'),'no_exposure_flag':int(status=='NO_EXPOSURE'),'eod_zero_stock_flag':int(row['eod_saleable_qty']==0),'zero_sales_flag':int(row['gross_sales_qty']==0)}
        require(all(row[k]==v for k,v in expected.items()), 'Invalid observation flags')
        require((status=='NO_EXPOSURE')==(row['opening_saleable_qty']==0), 'Invalid no-exposure quantity')
    lineage=manifest['lineage']
    require(all(len({x[k] for x in tables['fact_observed']})==1 and tables['fact_observed'][0][k]==lineage[k] for k in ('run_id','policy_id','scenario_id')), 'Mixed/mismatched run lineage')
    require(not lineage['model_training_eligible'], 'Release cannot be training approved')
    for name in ('dim_store','dim_sku'):
        require(all(x['provenance']=='SYN_MASTER' for x in tables[name]), 'Invalid master provenance')
    require(all(x['expirable']==0 for x in tables['dim_sku']), 'Unexpected perishable SKU')
    f=tables['fact_observed']
    totals=[len(f)]+[sum(x[k] for x in f) for k in ['gross_sales_qty','full_exposure_flag','censored_flag','no_exposure_flag','zero_sales_flag']]+[sum(x['eod_saleable_qty'] for x in f if x['day_index']==57),sum(x['zero_sales_flag']*x['full_exposure_flag'] for x in f)]
    require(totals==[2688,5272,1259,1429,1080,1541,119,461], 'Approved KPI totals mismatch: '+str(totals))
    return tables

def walk(obj):
    if isinstance(obj,dict):
        yield obj
        for v in obj.values(): yield from walk(v)
    elif isinstance(obj,list):
        for v in obj: yield from walk(v)

def validate_native(root=ROOT):
    root=Path(root); native=safe_path(root,'powerbi')
    pins=json.loads(safe_path(root,'data/native_manifest.json').read_text())
    actual={p.relative_to(native).as_posix():digest(p) for p in native.rglob('*') if p.is_file()}
    require(actual==pins, 'Canonical native file inventory/checksum mismatch')
    for p in native.rglob('*'):
        if p.is_file():
            safe_path(root,p.relative_to(root))
            if p.suffix in ('.json','.pbip','.pbir','.pbism'):json.loads(p.read_text(encoding='utf-8-sig'))
    model=native/'DemandFlow 360.SemanticModel/definition'
    tables={p.stem:p.read_text(encoding='utf-8-sig') for p in (model/'tables').glob('*.tmdl')}
    require(set(tables)==set(SCHEMAS)|{'_Measures'}, 'Unexpected native table set')
    measures=re.findall(r"^\tmeasure '([^']+)'",tables['_Measures'],re.M)
    require(len(measures)==len(set(measures))==18,'Invalid measure host')
    require(len(re.findall(r'^relationship ',(model/'relationships.tmdl').read_text(),re.M))==3,'Invalid relationships')
    columns={name:set(re.findall(r'^\tcolumn (.+)$',text,re.M)) for name,text in tables.items()}
    pages=native/'DemandFlow 360.Report/definition/pages'
    definitions={p.parent.name:json.loads(p.read_text()) for p in pages.glob('*/page.json')}
    expected=['00 INDEX','01 Executive Overview','02 Sales & Availability','03 Store & SKU Performance','04 Stockout Diagnostics','05 Data Quality']
    order=json.loads((pages/'pages.json').read_text())['pageOrder']
    require([definitions[x]['displayName'] for x in order]==expected,'Invalid pages/order')
    nav=0; bindings=0; visuals=0
    for p in pages.glob('*/visuals/*/visual.json'):
        visuals+=1
        obj=json.loads(p.read_text())
        for node in walk(obj):
            if 'navigationSection' in node:
                target=node['navigationSection']['expr']['Literal']['Value'].strip("'")
                require(target in definitions,'Broken navigation target'); nav+=1
            for kind in ('Column','Measure'):
                if kind in node and isinstance(node[kind],dict):
                    field=node[kind]; source=field.get('Expression',{}).get('SourceRef',{})
                    if 'Entity' in source:
                        entity=source['Entity']; prop=field['Property']
                        require(entity in tables,'Unknown binding entity')
                        require(prop in (set(measures) if kind=='Measure' and entity=='_Measures' else columns[entity]),'Unknown field binding: '+str(field)); bindings+=1
    require(nav>=10 and bindings>0 and visuals==72,'Incomplete navigation/bindings/visuals')
    return {'pages':6,'visuals':visuals,'measures':18,'relationships':3,'navigation_targets':nav,'field_bindings':bindings}

def publication_scan(root=ROOT,index=False):
    root=Path(root)
    if index:
        names=subprocess.check_output(['git','ls-files','--cached','-z'],cwd=root).decode().split('\0')
        files=[n for n in names if n]
    else:
        files=[p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and not any(x in ('.git','.runtime','outputs','__pycache__') for x in p.relative_to(root).parts)]
    for name in files:
        low=name.lower()
        require(not any(x in low for x in ('_backup_','_before_','oracle_restricted','evaluator','.pbi/','.venv/','__pycache__','output.txt','codex_report')), 'Publication denylist: '+name)
        require(Path(name).suffix.lower() not in ('.zip','.gz','.abf','.sqlite','.db','.pyc'), 'Unapproved binary/container: '+name)
        raw=subprocess.check_output(['git','show',':'+name],cwd=root) if index else (root/name).read_bytes()
        if Path(name).suffix.lower()=='.png':continue
        text=raw.decode('utf-8-sig')
        require(not any(word in text for word in ('true_'+'demand_qty','lost_'+'sales_qty')), 'Restricted evaluator field: '+name)
        require(not re.search(r'(?<![A-Za-z])[A-Za-z]:[\\/]',text),'Absolute workstation path: '+name)
        require(not re.search(r'gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,}|^-----BEGIN [A-Z ]*PRIVATE KEY-----',text,re.M),'Potential secret: '+name)
    return len(files)

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--index',action='store_true');args=parser.parse_args()
    validate_data(); print(json.dumps(validate_native(),indent=2))
    print('PUBLICATION_SCAN_FILES',publication_scan(index=args.index))
    print('RELEASE_STATIC_QA PASS')
