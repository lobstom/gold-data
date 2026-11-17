"""Local candidate only. No production/network effects.

Reference unit: decimal USD quote per $100 face; ounce equivalent per $100k
face = quote * 1000 / same-week gold USD/oz. Not invoice price or investment
value. Contract selection is fixed for a full observation week, without
back-adjustment. Switch to the next quarterly expiry at the first Monday on
or after the 20th of the month before the delivery month. Roll markers must
be emitted when the selected symbol changes. Require final dated inputs;
missing points are omitted, not forward-filled.
"""
import datetime as dt
import re
from statistics import mean


def decimal_quote(raw, symbol):
    if symbol not in ('ZN', 'ZB'):
        raise ValueError('unsupported symbol')
    pattern = r"(\d+)'(\d{2})([05])" if symbol == 'ZN' else r"(\d+)'(\d{2})"
    m = re.fullmatch(pattern, raw)
    if not m:
        raise ValueError('not an unqualified final Treasury quote')
    whole, thirtyseconds = int(m[1]), int(m[2])
    if thirtyseconds >= 32:
        raise ValueError('invalid thirtyseconds')
    return whole + thirtyseconds / 32 + (int(m[3]) / 320 if symbol == 'ZN' else 0)


def select_contract(symbol, date):
    if symbol not in ('ZN', 'ZB'):
        raise ValueError('unsupported symbol')
    monday = date - dt.timedelta(days=date.weekday())
    for year in (date.year, date.year + 1):
        for month, code in ((3, 'H'), (6, 'M'), (9, 'U'), (12, 'Z')):
            start = dt.date(year, month - 1, 20)
            roll = start + dt.timedelta(days=(-start.weekday()) % 7)
            if monday < roll:
                return f'{symbol}{code}{year % 100:02d}'
    raise AssertionError('no contract')


def completed_week(symbol, friday, observations, gold_usd, today):
    if friday.weekday() != 4 or friday >= today or gold_usd <= 0:
        raise ValueError('not a completed week or missing same-week gold')
    monday = friday - dt.timedelta(days=4)
    rows = [(date, quote) for date, quote in observations if monday <= date <= friday and date.weekday() < 5]
    if len({date for date, _ in rows}) != len(rows):
        raise ValueError('duplicate observations')
    if len(rows) < 3:
        raise ValueError('need at least three final observations')
    price = mean(decimal_quote(quote, symbol) for _, quote in rows)
    current = select_contract(symbol, monday)
    previous = select_contract(symbol, monday - dt.timedelta(days=7))
    return {'date': friday.isoformat(), 'contract': current, 'roll': current != previous,
            'decimal_per_100_face': price, 'gold_usd': gold_usd,
            'oz_per_100k_face': price * 1000 / gold_usd, 'observation_count': len(rows),
            'basis': 'completed-week mean of final settlements; no back-adjustment'}
