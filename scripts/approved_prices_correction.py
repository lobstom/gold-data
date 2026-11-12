#!/usr/bin/env python3
"""One-time, owner-approved Nov 12 debt/CPI/provenance correction. No full refresh."""
import copy,datetime as dt,hashlib,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'scripts'))
import weekly_snapshot as ws
from zoneinfo import ZoneInfo
now=dt.datetime.now(ZoneInfo('America/Los_Angeles'));stamp=now.strftime('%Y%m%dT%H%M%S');dest=ROOT/'snapshots/corrections/2026-11-12';dest.mkdir(parents=True,exist_ok=True)
assert not (dest/'latest.json').exists(),'Correction already published; refusing a second application'
frozen=ROOT/'snapshots/2026-11-09.json';frozen_hash=hashlib.sha256(frozen.read_bytes()).hexdigest();monday_manifest=(ROOT/'snapshots/latest.json').read_bytes()
doc=json.loads((ROOT/'data.json').read_text());original=copy.deepcopy(doc);before=ws.digest(doc)
assert doc['updated']=='2026-11-09','Unexpected live base; review before applying'
notes=[]
def save(num):ws.validate(doc);ws.atomic(dest/f'option{num}-after.json',doc)
# 5. Preserve original vintage, replace only Nov 6 weekly total and gold conversion.
ws.atomic(dest/'option5-before.json',doc)
de=doc['overrides_v3']['debt'];assert de['points'][-1][0]=='2026-11-06' and de['usd']==40.556
v=40552751019092.61/1e12;g=4018.43
p=de['points'][-1];p[1]=float(f'{v/g*1000:.5g}');p[2]=float(f'{v:.5g}');de['usd']=p[2];de['ozau']=p[1]
notes.append({'option':5,'series':'debt','period':'2026-11-06','old_trillion':40.556,'new_trillion_unrounded':v,'new_trillion':de['usd'],'gold_weekly_mean':g,'source_url':'https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/debt_to_penny?filter=record_date:eq:2026-11-06&fields=record_date,tot_pub_debt_out_amt','checked_at':'2026-11-12T17:09:36+00:00','note':'Current upstream mismatch corrected. Frozen Nov 9 observation vintage retained; no claim about cause of mismatch.'});save(5)
# 6. Add October CPI and move the real-dollar rebasing endpoint through existing runtime logic.
ws.atomic(dest/'option6-before.json',doc)
c=next(i for i in doc['more'] if i['id']=='cpi');assert c['points'][-1]==['2026-09-01',336.94]
c['prev']=c['usd'];c['points'].append(['2026-10-01',337.511]);c['usd']=337.511;c['asof']='2026-10'
notes.append({'option':6,'series':'cpi','period':'2026-10','old_period':'2026-09','old_value':336.94,'new_value':337.511,'source_url':'https://fred.stlouisfed.org/series/CPIAUCNS','checked_at':'2026-11-12T17:08:53+00:00','note':'New release after Monday cut. Runtime CPI map and latest-CPI rebasing value derive from this row; rates/indexes remain unadjusted.'});save(6)
# 7. Describe the actual endpoint source; do not alter uranium values.
ws.atomic(dest/'option7-before.json',doc)
u=next(i for i in doc['items'] if i['id']=='uranium');assert u['asof']=='2026-10-30' and u['usd']==91.55
u['freq']='month-end spot average (UxC/TradeTech via Cameco)';u['source']='Cameco month-end industry-average UxC/TradeTech spot price';u['source_url']='https://www.cameco.com/invest/markets/uranium-price';u['source_checked_at']='2026-11-12T17:08:53+00:00';u['source_note']='Current Oct 30, 2026 endpoint is Cameco month-end industry average of UxC and TradeTech. This is not independently verified as a latest weekly UxC quote. Historical dated manual UxC observations, where present, retain their original provenance.'
notes.append({'option':7,'series':'uranium','period':'2026-10-30','value_unchanged':91.55,'source_url':u['source_url'],'checked_at':u['source_checked_at'],'note':u['source_note']});save(7)
# Persist accurate provenance in future normal builds, conditional on which source supplies endpoint.
p=ROOT/'scripts/build_data.py';s=p.read_text();old='    add("uranium", "Uranium U3O8 (spot)", "lb", "month-end history, latest UxC weekly", pts)';assert old in s
new='''    endpoint_uxc = latest is not None and latest[0] > max(cam)
    add("uranium", "Uranium U3O8 (spot)", "lb", "month-end history; latest dated UxC input" if endpoint_uxc else "month-end spot average (UxC/TradeTech via Cameco)", pts)
    items[-1]["source"] = "Dated manual UxC input" if endpoint_uxc else "Cameco month-end industry-average UxC/TradeTech spot price"
    items[-1]["source_url"] = "https://www.uxc.com/p/price" if endpoint_uxc else "https://www.cameco.com/invest/markets/uranium-price"
    items[-1]["source_note"] = "Current endpoint comes from the named source. Historical dated UxC input and Cameco month-end history retain their original conventions."'''
p.write_text(s.replace(old,new))
# Correction is a separately labeled build, not a new Monday issue cut.
doc['updated']='2026-11-12';doc['correction']={'id':'2026-11-12-approved-1-7','base_snapshot':'snapshots/2026-11-09.json','base_sha256':frozen_hash,'captured_at':now.isoformat(),'notes':notes}
ws.validate(doc)
# Assert no other observations/settings changed.
assert [i for i in doc['items'] if i['id']!='uranium']==[i for i in original['items'] if i['id']!='uranium']
assert [i for i in doc['more'] if i['id']!='cpi']==[i for i in original['more'] if i['id']!='cpi']
assert {k:v for k,v in doc['overrides_v3'].items() if k!='debt'}=={k:v for k,v in original['overrides_v3'].items() if k!='debt'}
assert doc['more_v3']==original['more_v3'] and u['points']==next(i for i in original['items'] if i['id']=='uranium')['points']
ws.atomic(dest/'data.json',doc);ws.atomic(dest/'latest.json',{'schema_version':1,'kind':'approved_correction','complete':True,'base_snapshot':'snapshots/2026-11-09.json','base_snapshot_sha256':frozen_hash,'before_data_sha256':before,'data_sha256':ws.digest(doc),'path':str((dest/'data.json').relative_to(ROOT)),'captured_at':now.isoformat(),'changes':notes})
ws.atomic(ROOT/'data.json',doc)
assert hashlib.sha256(frozen.read_bytes()).hexdigest()==frozen_hash
assert (ROOT/'snapshots/latest.json').read_bytes()==monday_manifest
print('PASS options5,6,7; schema and constrained diff; frozen Monday and manifest unchanged; correction',ws.digest(doc))
