#!/usr/bin/env python3
"""Report stored observation vintages without implying a fresh source retrieval.
No network calls, price changes, or frozen-snapshot rewrites. Age thresholds are
review heuristics, not assertions that a publisher missed a release.
"""
import argparse, datetime as dt, json
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parent.parent
TZ=ZoneInfo('America/Los_Angeles')

def effective_rows(doc):
    rows={r['id']:r for key in ('items','more','more_v3') for r in doc.get(key,[])}
    rows.update(doc.get('overrides_v3',{}))
    return rows

def date_value(s):
    if len(s)==7:return dt.date.fromisoformat(s+'-01')
    return dt.date.fromisoformat(s)

def describe_period(r):
    a=r['asof'];f=r.get('freq','').lower()
    if f.startswith('quarterly') or (f.startswith('quarter-end') and 'weekly since' not in f):
        d=date_value(a);return f'{d.year}-Q{(d.month-1)//3+1}', 'quarter-start label, not a daily observation'
    if len(a)==7 or ('monthly' in f and 'weekly since' not in f):return a[:7], 'monthly period, not a daily quote'
    return a,'source observation date or completed-week label'

def build(doc,snapshot,now):
    generated=now.isoformat();oldrows=effective_rows(snapshot.get('data',{}));oldmeta=snapshot.get('series',{});weekly=snapshot.get('weekly_prices',{})
    out=[]
    for rid,r in effective_rows(doc).items():
        last=r['points'][-1][0];period,semantics=describe_period(r)
        f=r.get('freq','');low=f.lower();anchor=date_value(r['asof']);days=(now.date()-anchor).days
        threshold=14 if ('weekly' in low or 'week' in low) else 200 if (low.startswith('quarterly') or low.startswith('quarter-end')) else 550 if low.startswith('annual') else 75
        review='future_date_error' if days<0 else 'review_old_vintage' if days>threshold else 'within_age_review_threshold'
        # Trust source attribution from frozen evidence only when it matches
        # the actual effective row and latest observation, including overrides.
        w=weekly.get(rid,{});m=oldmeta.get(rid,{});same=oldrows.get(rid)==r
        exact_weekly=(w.get('observation_date')==last and w.get('status') in ('available','overdue') and w.get('value') is not None and (round(w['value'],4) if r.get('kind') else float(f"{w['value']:.5g}"))==r.get('usd'))
        if exact_weekly:
            source=w.get('source');url=w.get('source_url');checked=w.get('checked_at') if rid!='uranium' else None;basis='matching frozen weekly source record' if rid!='uranium' else 'matching stored input file; checked_at is file inspection, not authenticated upstream retrieval'
        elif same and ('weekly' not in low):
            source=m.get('source');url=m.get('source_url');checked=None;basis='frozen attribution only; legacy check timestamp does not prove source retrieval'
        else:source=url=checked=None;basis='no matching source-check evidence for this effective row'
        gold=None
        if not r.get('kind'):
            gold={'usd_per_oz':r.get('goldusd'),'timing':'synchronized completed-week conversion only if matching source dates are evidenced; otherwise inspect original row convention','same_period_verified':False}
            g=weekly.get('gold',{})
            gold_week=(date_value(last)+dt.timedelta(days=4-date_value(last).weekday())).isoformat()
            if exact_weekly and g.get('observation_date')==gold_week and g.get('value') is not None and r.get('goldusd')==float(f"{g['value']:.5g}"):
                gold.update(timing='same-week gold denominator evidenced; stock observations remain point-in-time, not weekly averages',same_period_verified=True)
            if rid=='uranium':gold['timing']='latest uranium may use monthly gold; do not label a synchronized weekly ratio'
        out.append({'id':rid,'label':r.get('label',rid),'observation_period':period,'asof_label':r['asof'],'latest_point_date':last,'date_semantics':semantics,'frequency':f,'age_from_label_days':days,'age_review_threshold_days':threshold,'age_review_status':review,'source':source,'source_url':url,'last_evidenced_source_check_at':checked,'source_evidence':basis,'source_rechecked_now':False,'next_release_at':None,'release_expectation':'not verified by this report; age threshold is not a publisher release calendar','gold_conversion':gold})
    return {'schema_version':1,'generated_at':generated,'data_updated_label':doc.get('updated'),'frozen_snapshot_captured_at':snapshot.get('captured_at'),'checks_performed':'local observation metadata inspection only; no live upstream source checks','summary':{'rows':len(out),'old_vintage_review':sum(r['age_review_status']=='review_old_vintage' for r in out),'future_date_errors':sum(r['age_review_status']=='future_date_error' for r in out)},'rows':out}

def apply_release_evidence(report, evidence):
    """Attach dated manual publisher checks, without upgrading model-value provenance."""
    for row in report['rows']:
        matches=[e for e in evidence.get('checks',[]) if e.get('row_id')==row['id'] and e.get('matched_model_period')==row['observation_period'] and dt.datetime.fromisoformat(e['checked_at'])<=dt.datetime.fromisoformat(report['generated_at'])]
        if not matches:continue
        check=max(matches,key=lambda e:dt.datetime.fromisoformat(e['checked_at']))
        row['publisher_release_evidence']=dict(check)
        row['release_expectation']=check['note']
        # A date-only publisher notice is not an exact dispatch/release time.
        row['next_release_date']=check.get('next_release_date')
    return report

def markdown(report):
    lines=['# Observation freshness report','',f"Generated {report['generated_at']}.",f"Model update label {report['data_updated_label']}. This is not the observation date of every row.",'This generator performs no live upstream retrieval. Dated manual publisher checks, where available, are listed separately below. Other release expectations remain unverified; age flags are review prompts, not missed-release claims.','','| Row | Observation period | Cadence | Age review | Last evidenced source check |','| --- | --- | --- | --- | --- |']
    for r in report['rows']:lines.append('| '+' | '.join(str(v).replace('|','/') for v in (r['label'],r['observation_period'],r['frequency'],r['age_review_status'],r['last_evidenced_source_check_at'] or 'Unverified'))+' |')
    checks=[r for r in report['rows'] if r.get('publisher_release_evidence')]
    if checks:
        lines+=['','## Dated publisher release checks','','These are dated manual release-period checks, not a new fetch on each report build. They do not verify stored values or gold conversions. No model data was changed.','']
        for row in checks:
            e=row['publisher_release_evidence']
            lines += [f"### {row['label']}",f"Checked {e['checked_at']}. Source [{e['source']}]({e['source_url']}).",f"Publisher release {e['release_date']}; latest published period {e['latest_published_period']}; stored model period {row['observation_period']}.",e['note']]
            if e.get('next_release_date'):lines.append(f"Next announced release date {e['next_release_date']}; no release time is inferred.")
            lines.append('')
    return '\n'.join(lines)+'\n' 

def main():
    p=argparse.ArgumentParser();p.add_argument('--as-of');p.add_argument('--output-dir',default=str(ROOT/'reports'));a=p.parse_args()
    now=dt.datetime.fromisoformat(a.as_of) if a.as_of else dt.datetime.now(TZ)
    if now.tzinfo is None:raise SystemExit('--as-of must have a timezone offset')
    manifest=json.loads((ROOT/'snapshots/latest.json').read_text());snap=json.loads((ROOT/manifest['path']).read_text());doc=json.loads((ROOT/'data.json').read_text());report=build(doc,snap,now);evidence_path=ROOT/'reports/source-release-evidence.json';report=apply_release_evidence(report,json.loads(evidence_path.read_text())) if evidence_path.exists() else report;dest=Path(a.output_dir);dest.mkdir(parents=True,exist_ok=True)
    (dest/'freshness.json').write_text(json.dumps(report,indent=2)+'\n');(dest/'freshness.md').write_text(markdown(report));print(json.dumps(report['summary']))
if __name__=='__main__':main()
