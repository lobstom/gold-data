import json,math,hashlib
def tm(s):
    return int(s[:4])+(int(s[5:7])-1)/12+(int(s[8:10])-1)/365

def stats(it):
    if it['id']=='gold': return {'available':False,'reason':'Gold priced in gold is the constant, not a valuation comparison.'}
    if it.get('kind') or it.get('fixed'): return {'available':False,'reason':'Native rate, ratio or index, not a price in gold ounces.'}
    P=it.get('points',[])
    valid=[p for p in P if len(p)>1 and isinstance(p[1],(float,int)) and math.isfinite(p[1])]
    if len(valid)<24:return {'available':False,'reason':'Fewer than 24 valid observations; no historical comparison.'}
    weights=[]
    for n,p in enumerate(P):
        if p not in valid:continue
        end=tm(P[n+1][0]) if n+1<len(P) else tm(p[0])+1/12
        weights.append((p[1],max(end-tm(p[0]),1e-4)))
    weights.sort(key=lambda a:a[0]);total=sum(w for v,w in weights);cum=0;med=None
    for v,w in weights:
        cum+=w
        if cum>=total/2:med=v;break
    latest=valid[-1][1];pct=math.floor(100*sum(w for v,w in weights if v<latest)/total+0.5)
    return {'available':True,'denomination':'billion troy oz of gold' if it.get('big') else 'troy oz of gold per '+it['unit'],
      'history_start':valid[0][0],'history_end':valid[-1][0], 'observations':len(valid),
      'latest':latest,'median':med,'percentile':pct,'delta_from_median_pct':(latest/med-1)*100 if med else None,
      'basis':'Full available history, with time weights matching the interactive model; not an annual average.'}


def augment(data,summary,data_bytes):
    items=[data.get("overrides_v3",{}).get(i["id"],i) for i in data["items"]]+data.get("more",[])+data.get("more_v3",[])
    byid={i["id"]:i for i in items}
    lines=[]
    for group in summary['groups']:
        for row in group['series']:
            it=byid.get(row['id'])
            if not it:continue
            st=stats(it);row['historical_comparison_gold']=st
            if not st['available']:continue
            delta=st['delta_from_median_pct'];diff=('above' if delta>=0 else 'below')
            amount=f"{st['latest']:.6g}";med=f"{st['median']:.6g}"
            label=row['label']
            if row['id']=='debt': label='Total federal debt'
            elif row['id']=='sp500': label='S&P 500 price-index level'
            elif row['id']=='dow': label='Dow Jones price-index level'
            line=(f"As of {row['as_of']}, {label}: {amount} {st['denomination']}, "
                f"{abs(delta):.1f}% {diff} its {st['history_start']} to {st['history_end']} time-weighted median "
                f"of {med} {st['denomination']} (No Time For Bull model; {row['frequency']}). "
                f"Full-history comparison; histories may include proxies. See this row's source and method notes.")
            historical_notes={
              'silver':'Before 1960, annual or derived history.',
              'usd':'Before 1960, annual history derived from the gold series.',
              'wti':'Before 1982, annual oil history.',
              'brent':'Before 1960, annual oil proxy.',
              'gas':'Before 1960, annual wellhead proxy.',
              'ttf':'Before April 2015, European import-price proxy, not TTF.',
              'elec':'Before 2001, annual history.',
              'housing':'Before 1963, a rescaled home-price index, not observed median new-home prices; full-history comparison is approximate.',
              'ahe':'Before 1964, rescaled manufacturing earnings; full-history comparison is approximate.',
              'debt':'Before 1966, annual fiscal-year history.'}
            if row['id'] in historical_notes:line+=' '+historical_notes[row['id']]
            if it.get('big'): line+=' Dollar-equivalent in gold, not gold owned; overlapping balance rows must not be added.'
            row['citation_sentence_gold']=line;lines.append({'id':row['id'],'text':line,'note':row.get('note'),'stats':st})
    summary['historical_comparison_method']={
     'scope':'Gold-denominated price rows with at least 24 valid observations. Rates, ratios, fixed indexes, gold itself and short histories have explicit unavailable reasons.',
     'percentile':'Rounded percentage of historical time weight strictly below the latest valid value. A percentile is not a forecast, probability or expected return.',
     'weights':'Each valid point receives the fractional-year gap to the next source point; final point receives 1/12 year; minimum weight 0.0001 year. Fractional year = year + (month-1)/12 + (day-1)/365. Same convention as the existing interactive model.',
     'median':'First value in ascending value order whose cumulative time weight reaches half of all time weight.',
     'delta':'100 * (latest / median - 1). Negative means below, positive above. Not a change over time and not a year-average comparison.',
     'caveats':'Available histories differ in start date and frequency and may contain proxies or approximate reconstructions. Preserve every existing series note and source convention alongside these comparisons. Gold-equivalent balance rows are not gold owned. Underlying data remain dated and are not real-time.',
     'source':'https://data.notimeforbull.com/data.json',
     'method_source':'https://www.notimeforbull.com/prices/',
     'dataset_sha256':hashlib.sha256(data_bytes).hexdigest()}
    return summary,lines
