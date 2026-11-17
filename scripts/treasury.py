#!/usr/bin/env python3
"""CME final Treasury futures settlements captured through a browser.
No network calls. Preserve raw dated inputs; never fabricate older history.
"""
import datetime as dt
import json
import math
from pathlib import Path
from statistics import mean
from treasury_quotes import decimal_quote, select_contract

ROOT = Path(__file__).resolve().parent.parent
PRODUCTS = {316: ('ZN', 'zn', '10Y Treasury futures (ZN reference quote)', '10-year-us-treasury-note'),
            307: ('ZB', 'zb', 'Treasury bond futures (ZB reference quote)', '30-year-us-treasury-bond')}
RULE = ('Switch to the next quarterly delivery contract on the first Monday on or after the 20th '
        'of the month before delivery; one contract for the full week. No back-adjustment. '
        'Roll weeks are marked; a level change at a roll is not an investment return.')
NOTE = ('CME final daily settlements, decimal quote per $100 face. Gold equivalent per $100,000 '
        'face = 1,000 x weekly mean decimal quote / same-week World Gold Council gold USD/oz. '
        'Futures reference quote only: not margin, invested capital, delivery invoice price, cash bond '
        'value or total return. Invoice pricing also uses a conversion factor and accrued interest. '
        'At least three dated final daily settlements per completed week. No silver or real-dollar '
        'conversion. Free browser history currently starts November 9, 2026; earlier requests were '
        'empty. The first weekly point is November 13, 2026. ' + RULE)


def apply(doc, log=print, now=None, inputs_dir=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    directory = Path(inputs_dir) if inputs_dir else ROOT / 'inputs' / 'treasury'
    gold = {p[0]: p[2] for r in doc['items'] if r['id'] == 'gold' for p in r['points']}
    daily = {}
    fetched = []
    for path in sorted(directory.glob('*.json')):
        src = json.loads(path.read_text())
        assert src['schema_version'] == 1
        captured = dt.datetime.fromisoformat(src['captured_at'])
        assert captured.utcoffset() is not None and captured <= now
        fetched.append(src['captured_at'])
        for item in src['records']:
            product = item['product']
            assert product in PRODUCTS
            data = item['data']
            if data['empty']:
                continue
            assert data['reportType'] == 'Final'
            date = dt.datetime.strptime(data['tradeDate'], '%m/%d/%Y').date()
            assert date < now.date() and date.weekday() < 5
            symbol = PRODUCTS[product][0]
            contract = select_contract(symbol, date)
            code = {'H': 'MAR', 'M': 'JUN', 'U': 'SEP', 'Z': 'DEC'}[contract[-3]]
            month = code + ' ' + contract[-2:]
            selected = [r for r in data['settlements'] if r['month'] == month]
            assert len(selected) == 1, 'missing or duplicate selected contract'
            row = selected[0]
            assert int(row['volume'].replace(',', '')) > 0, 'inactive settlement'
            assert int(row['openInterest'].replace(',', '')) > 0
            quote = decimal_quote(row['settle'], symbol)
            key = (product, date)
            if key in daily:
                assert daily[key] == (quote, contract), 'conflicting dated input'
            daily[key] = (quote, contract)
    if not daily:
        log('::warning::Treasury futures: no dated input; existing rows retained')
        return []
    added = []
    for product, (symbol, rid, label, slug) in PRODUCTS.items():
        grouped = {}
        for (pid, date), (quote, contract) in sorted(daily.items()):
            if pid != product:
                continue
            friday = date + dt.timedelta(days=4 - date.weekday())
            if friday >= now.date():
                continue
            grouped.setdefault(friday.isoformat(), []).append((date, quote, contract))
        weeks = []
        for friday, observations in sorted(grouped.items()):
            if len(observations) < 3 or friday not in gold:
                continue
            assert len({r[2] for r in observations}) == 1
            q = mean(r[1] for r in observations)
            g = gold[friday]
            assert math.isfinite(g) and g > 0
            contract = observations[0][2]
            prev = select_contract(symbol, dt.date.fromisoformat(friday) - dt.timedelta(days=7))
            weeks.append({'date': friday, 'contract': contract, 'roll': contract != prev,
                          'quote_per_100_face': q, 'reference_usd_per_100k_face': q * 1000,
                          'gold_usd': g, 'oz_per_100k_face': q * 1000 / g,
                          'daily_dates': [r[0].isoformat() for r in observations],
                          'daily_count': len(observations)})
        if not weeks:
            log('::warning::' + rid + ': no complete input and same-week gold match; existing row retained')
            continue
        latest = weeks[-1]
        row = {'id': rid, 'label': label, 'unit': '$100k face (reference)', 'treasury': True,
               'freq': 'completed-week average of final settlements; history from 2026-11-13',
               'asof': latest['date'], 'usd': latest['reference_usd_per_100k_face'],
               'ozau': latest['oz_per_100k_face'], 'ozag': None, 'goldusd': latest['gold_usd'],
               'quote_per_100_face': latest['quote_per_100_face'], 'contract': latest['contract'],
               'points': [[w['date'], w['oz_per_100k_face'], w['reference_usd_per_100k_face'], None] for w in weeks],
               'weeks': weeks, 'roll_rule': RULE, 'note': NOTE,
               'source': 'CME Group final settlements, browser-captured dated inputs',
               'source_url': 'https://www.cmegroup.com/markets/interest-rates/us-treasury/' + slug + '/settlements',
               'source_checked_at': max(fetched), 'source_input_directory': 'inputs/treasury/'}
        assert row['points'] and all(math.isfinite(v) and v > 0 for p in row['points'] for v in p[1:3])
        target = doc.setdefault('more_v3', [])
        old = next((r for r in target if r['id'] == rid), None)
        if old:
            # All retained weekly observations must remain independently recoverable from dated inputs.
            assert set(p[0] for p in old['points']) <= set(p[0] for p in row['points'])
            target[target.index(old)] = row
        else:
            target.append(row)
        added.append(rid)
        log(rid + ': ' + latest['contract'] + ', ' + latest['date'] + ', ' + str(latest['daily_count']) + ' finals')
    if added:
        doc.setdefault('v3_notes', {})['treasury_futures'] = NOTE
    return added
